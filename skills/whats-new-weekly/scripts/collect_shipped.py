#!/usr/bin/env python3
"""Collect what shipped to production across a set of repos in a date window.

For each configured repo, walks the merge commits landed on `origin/production`
(the "release trains") in the window, extracts the PR numbers introduced by
each train, and pulls each PR's title/body/changelog section via `gh`. Also
scans CHANGELOG.md where present and lists PRs merged to develop that have not
shipped yet, for "coming soon" context.

Also emits a compact markdown digest (see `--md`) that classifies obviously
internal PRs (chores, bumps, docs, CI) so a subagent can read the digest
instead of the much larger JSON, which stays as the full audit trail.

Repos and tuning come from the fenced ```json block in the skill's CONFIG.md (see --config).
Stdlib only. Read-only: never checks out or modifies a repo's working tree.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

DEFAULTS = {
    "production_branch": "production",
    "integration_branch": "develop",
    "release_train_titles": ["staging", "develop", "production"],
    "release_train_legs": [["staging", "develop"], ["production", "staging"], ["production", "develop"]],
    "internal_title_keywords": ["changelog sync", "bump", "lint", "prettier", "eslint"],
    "internal_labels": ["dependencies", "chore", "internal", "ci"],
    "internal_authors": ["dependabot[bot]", "dependabot"],
}
SETTINGS = dict(DEFAULTS)

CONFIG_BLOCK_RE = re.compile(r"```json\s*\n(.*?)\n```", re.S)


def load_config(path):
    """Read the first fenced json block of CONFIG.md. Fill repo defaults and expand ~ in paths."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    match = CONFIG_BLOCK_RE.search(text)
    if not match:
        sys.exit(f"ERROR: no fenced json block found in {path}")
    cfg = json.loads(match.group(1))
    for key in DEFAULTS:
        if key in cfg:
            SETTINGS[key] = cfg[key]
    repos = cfg.get("repos", [])
    if not repos:
        sys.exit(f"ERROR: no repos listed in {path}")
    for repo in repos:
        repo["local_path"] = os.path.expanduser(repo["local_path"])
        repo.setdefault("production_branch", SETTINGS["production_branch"])
        repo.setdefault("integration_branch", SETTINGS["integration_branch"])
        repo.setdefault("production_url", None)
        repo.setdefault("display_name", None)
        repo.setdefault("surface", "web")
        repo.setdefault("has_changelog_file", False)
    return repos


MERGE_PR_RE = re.compile(r"Merge pull request #(\d+)")
SQUASH_PR_RE = re.compile(r"\(#(\d+)\)\s*$")
CHANGELOG_DATE_RE = re.compile(r"\(\[#(\d+)\]\([^)]*\),\s*(\d{4}-\d{2}-\d{2})\)")

GH_TIMEOUT = 30
GIT_TIMEOUT = 30

# Classification of "obviously internal" PRs, so the digest can list them as
# titles only instead of spending space/attention on chores and bumps.
INTERNAL_TITLE_PREFIX_RE = re.compile(
    r"^(?:\([^)]*\)\s*)?(chore|ci|build|deps|test|tests|docs|doc|refactor|style|perf)(?:\([^)]*\))?(:|/|\s)",
    re.IGNORECASE,
)


def parse_date_arg(value, end_of_day=False):
    """Parse YYYY-MM-DD or full ISO 8601 into an aware local datetime."""
    if len(value) == 10:
        dt = datetime.strptime(value, "%Y-%m-%d")
        if end_of_day:
            dt = dt + timedelta(days=1) - timedelta(seconds=1)
        return dt.astimezone() if dt.tzinfo else dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.astimezone()
    return dt


def run(cmd, cwd=None, timeout=GIT_TIMEOUT):
    """Run a subprocess, returning (ok, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired as exc:
        return False, "", f"timed out after {timeout}s: {exc}"
    except OSError as exc:
        return False, "", str(exc)


def fetch_branches(local_path, branches):
    for branch in branches:
        ok, _, err = run(["git", "fetch", "origin", branch], cwd=local_path, timeout=GIT_TIMEOUT)
        if not ok:
            # A missing branch is not fatal.
            print(f"  warn: fetch origin/{branch} failed: {err.strip()}", file=sys.stderr)


def git_log(local_path, args):
    ok, out, err = run(["git", "log"] + args, cwd=local_path, timeout=GIT_TIMEOUT)
    if not ok:
        raise RuntimeError(f"git log {' '.join(args)} failed: {err.strip()}")
    return out


def find_release_trains(local_path, since, until, branch):
    """Return production merge commits in the window as [{sha, date, subject}]."""
    since_iso = since.isoformat()
    until_iso = until.isoformat()
    ok, out, err = run(
        [
            "git", "rev-list", "--first-parent",
            f"--since={since_iso}", f"--until={until_iso}",
            f"origin/{branch}",
        ],
        cwd=local_path,
        timeout=GIT_TIMEOUT,
    )
    if not ok:
        raise RuntimeError(f"git rev-list failed: {err.strip()}")
    shas = [s for s in out.splitlines() if s.strip()]
    trains = []
    for sha in shas:
        subject = git_log(local_path, ["-1", "--format=%s", sha]).strip()
        date = git_log(local_path, ["-1", "--format=%aI", sha]).strip()
        trains.append({"sha": sha, "date": date, "subject": subject})
    return trains


def introduced_commits(local_path, sha):
    """Commits introduced by `sha`: M^1..M for a merge, or just M otherwise."""
    ok, parents, _ = run(["git", "log", "-1", "--format=%P", sha], cwd=local_path, timeout=GIT_TIMEOUT)
    parent_list = parents.split()
    if len(parent_list) < 2:
        range_spec = f"{sha}^..{sha}" if parent_list else sha
    else:
        first_parent = parent_list[0]
        range_spec = f"{first_parent}..{sha}"
    out = git_log(local_path, ["--format=%H%x01%s%x01%b%x02", range_spec])
    commits = []
    for chunk in out.split("\x02"):
        chunk = chunk.strip("\n")
        if not chunk.strip():
            continue
        parts = chunk.split("\x01", 2)
        if len(parts) != 3:
            continue
        commit_hash, subject, body = parts
        commits.append({"hash": commit_hash, "subject": subject, "body": body})
    return commits


def extract_pr_numbers(commits):
    numbers = []
    seen = set()
    for commit in commits:
        text = commit["subject"] + "\n" + commit["body"]
        for match in MERGE_PR_RE.finditer(text):
            n = int(match.group(1))
            if n not in seen:
                seen.add(n)
                numbers.append(n)
        match = SQUASH_PR_RE.search(commit["subject"].strip())
        if match:
            n = int(match.group(1))
            if n not in seen:
                seen.add(n)
                numbers.append(n)
    return numbers


def gh_pr_view(github_repo, number):
    fields = "number,title,body,mergedAt,baseRefName,headRefName,author,url,labels"
    ok, out, err = run(
        ["gh", "pr", "view", str(number), "-R", github_repo, "--json", fields],
        timeout=GH_TIMEOUT,
    )
    if not ok:
        print(f"  warn: gh pr view {number} failed: {err.strip()}", file=sys.stderr)
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        print(f"  warn: gh pr view {number} returned invalid JSON", file=sys.stderr)
        return None


def extract_changelog_section(body):
    if not body:
        return None, body or ""
    match = re.search(r"^##\s*Changelog\s*$", body, re.IGNORECASE | re.MULTILINE)
    if not match:
        return None, body
    start = match.end()
    rest = body[start:]
    next_heading = re.search(r"^##\s+", rest, re.MULTILINE)
    end = next_heading.start() if next_heading else len(rest)
    section = rest[:end].strip()
    remainder = body[:match.start()] + rest[end:]
    return section, remainder


def is_release_train_pr(pr):
    title = (pr.get("title") or "").strip().lower()
    if title in SETTINGS["release_train_titles"]:
        return True
    base = (pr.get("baseRefName") or "").lower()
    head = (pr.get("headRefName") or "").lower()
    # Covers both single-hop (develop/staging -> production) and two-hop
    # (develop -> staging -> production) release-train topologies: a PR whose
    # base/head pair is itself a leg of the train, regardless of its
    # auto-generated title, is a mechanical sync, not a feature.
    train_legs = {tuple(leg) for leg in SETTINGS["release_train_legs"]}
    if (base, head) in train_legs:
        return True
    return False


def is_changelog_placeholder(section):
    """True when a `## Changelog` section is present but carries no real content."""
    if section is None:
        return False
    if not section.strip():
        return True
    if re.search(r"no changelog", section, re.IGNORECASE):
        return True
    lines = [line for line in section.splitlines() if line.strip()]
    if lines and all(line.strip().startswith("#") for line in lines):
        return True
    return False


def classify_internal(title, author_login, labels, changelog_section):
    """Return (likely_internal, reason) for an obviously-internal PR."""
    title = title or ""
    match = INTERNAL_TITLE_PREFIX_RE.match(title.strip())
    if match:
        return True, f"title prefix: {match.group(1).lower()}"
    if author_login in SETTINGS["internal_authors"]:
        return True, f"author: {author_login}"
    label_hits = {(label or "").lower() for label in labels} & set(SETTINGS["internal_labels"])
    if label_hits:
        return True, f"label: {sorted(label_hits)[0]}"
    if is_changelog_placeholder(changelog_section):
        return True, "changelog placeholder"
    lowered = title.lower()
    for keyword in SETTINGS["internal_title_keywords"]:
        if keyword in lowered:
            return True, f"title keyword: {keyword}"
    return False, None


def build_pr_entry(pr, shipped_in):
    body = pr.get("body") or ""
    changelog_section, remainder = extract_changelog_section(body)
    if changelog_section:
        changelog_section = changelog_section[:1500]
    author = pr.get("author") or {}
    author_login = author.get("login")
    labels = [label.get("name") for label in pr.get("labels", [])]
    title = pr.get("title")
    likely_internal, internal_reason = classify_internal(
        title, author_login, labels, changelog_section
    )
    # A real changelog section is the canonical summary, so the raw body
    # excerpt is only kept around for PRs that don't have one.
    body_excerpt = None if changelog_section else (remainder.strip()[:400] or None)
    return {
        "number": pr["number"],
        "title": title,
        "url": pr.get("url"),
        "merged_at": pr.get("mergedAt"),
        "author": author_login,
        "labels": labels,
        "is_release_train": is_release_train_pr(pr),
        "changelog_section": changelog_section,
        "body_excerpt": body_excerpt,
        "likely_internal": likely_internal,
        "internal_reason": internal_reason,
        "shipped_in": shipped_in,
    }


def scan_changelog_file(local_path, since, until):
    changelog_path = os.path.join(local_path, "CHANGELOG.md")
    if not os.path.isfile(changelog_path):
        return []
    entries = []
    with open(changelog_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            match = CHANGELOG_DATE_RE.search(line)
            if not match:
                continue
            pr_number, date_str = match.group(1), match.group(2)
            entry_date = datetime.strptime(date_str, "%Y-%m-%d").replace(
                tzinfo=since.tzinfo
            )
            if since <= entry_date <= until:
                entries.append({
                    "raw": line.strip().lstrip("-").strip(),
                    "pr_number": int(pr_number),
                    "date": date_str,
                })
    return entries


def gh_pr_list_merged(github_repo, base, since):
    since_date = since.strftime("%Y-%m-%d")
    ok, out, err = run(
        [
            "gh", "pr", "list", "-R", github_repo,
            "--state", "merged", "--base", base,
            "--search", f"merged:>={since_date}",
            "--json", "number,title,url,mergedAt",
            "--limit", "200",
        ],
        timeout=GH_TIMEOUT,
    )
    if not ok:
        print(f"  warn: gh pr list --base {base} failed: {err.strip()}", file=sys.stderr)
        return []
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return []


def gh_releases(github_repo, since, until):
    ok, out, err = run(
        ["gh", "api", f"repos/{github_repo}/releases", "--paginate"],
        timeout=GH_TIMEOUT,
    )
    if not ok:
        print(f"  warn: gh api releases failed: {err.strip()}", file=sys.stderr)
        return []
    try:
        releases = json.loads(out)
    except json.JSONDecodeError:
        return []
    result = []
    for rel in releases:
        published_at = rel.get("published_at")
        if not published_at:
            continue
        published_dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        if since <= published_dt <= until:
            result.append({
                "name": rel.get("name"),
                "tag": rel.get("tag_name"),
                "body": (rel.get("body") or "")[:2000],
                "url": rel.get("html_url"),
                "published_at": published_at,
            })
    return result


def process_repo(repo, since, until, skip_fetch):
    name = repo["name"]
    local_path = repo["local_path"]
    print(f"== {name} ==", file=sys.stderr)

    if not os.path.isdir(local_path):
        return {**base_repo_output(repo), "error": f"local path not found: {local_path}"}

    branches = [repo["production_branch"], repo["integration_branch"]]
    if os.path.isdir(os.path.join(local_path, ".git")):
        ok, out, _ = run(["git", "branch", "-a"], cwd=local_path)
        branch_names = {line.strip().lstrip("* ").rsplit("/", 1)[-1] for line in out.splitlines()}
        if ok and "main" in branch_names:
            branches.append("main")

    if not skip_fetch:
        fetch_branches(local_path, branches)

    try:
        release_trains_raw = find_release_trains(local_path, since, until, repo["production_branch"])
    except RuntimeError as exc:
        return {**base_repo_output(repo), "error": str(exc)}

    all_introduced = []
    train_by_pr = {}
    release_trains = []
    for train in release_trains_raw:
        commits = introduced_commits(local_path, train["sha"])
        all_introduced.extend(commits)
        pr_numbers = extract_pr_numbers(commits)
        # The train's own PR number, if the merge commit itself was a PR merge.
        own_pr = None
        m = MERGE_PR_RE.search(train["subject"])
        if m:
            own_pr = int(m.group(1))
        release_trains.append({
            "sha": train["sha"],
            "date": train["date"],
            "subject": train["subject"],
            "pr_number": own_pr,
        })
        for pr_number in pr_numbers:
            train_by_pr.setdefault(pr_number, train)

    shipped_prs = []
    for pr_number, train in train_by_pr.items():
        pr = gh_pr_view(repo["github"], pr_number)
        if pr is None:
            continue
        shipped_in = {"sha": train["sha"], "date": train["date"]}
        shipped_prs.append(build_pr_entry(pr, shipped_in))
    shipped_prs.sort(key=lambda p: p["number"])

    changelog_file_entries = []
    if repo.get("has_changelog_file"):
        for entry in scan_changelog_file(local_path, since, until):
            entry["in_production"] = entry["pr_number"] in train_by_pr
            changelog_file_entries.append(entry)

    releases = []
    merged_unreleased = []
    if repo.get("releases_only"):
        releases = gh_releases(repo["github"], since, until)
        merged_unreleased = gh_pr_list_merged(repo["github"], repo["integration_branch"], since)

    shipped_numbers = set(train_by_pr.keys())
    develop_merged = gh_pr_list_merged(repo["github"], repo["integration_branch"], since)
    merged_not_yet_in_production = [
        {"number": pr["number"], "title": pr["title"], "url": pr["url"], "mergedAt": pr["mergedAt"]}
        for pr in develop_merged
        if pr["number"] not in shipped_numbers
    ]

    output = base_repo_output(repo)
    output.update({
        "release_trains": release_trains,
        "shipped_prs": shipped_prs,
        "changelog_file_entries": changelog_file_entries,
        "releases": releases,
        "merged_not_yet_in_production": merged_not_yet_in_production,
        "error": None,
    })
    if repo.get("releases_only"):
        output["merged_unreleased"] = merged_unreleased
    return output


def base_repo_output(repo):
    return {
        "name": repo["name"],
        "github": repo["github"],
        "local_path": repo["local_path"],
        "production_url": repo["production_url"],
        "display_name": repo.get("display_name"),
        "surface": repo["surface"],
        "releases_only": repo.get("releases_only", False),
    }


def human_summary(data):
    lines = []
    for repo in data["repos"]:
        lines.append(f"\n{repo['name']}:")
        if repo.get("error"):
            lines.append(f"  ERROR: {repo['error']}")
            continue
        trains = repo.get("release_trains", [])
        shipped = [pr for pr in repo.get("shipped_prs", []) if not pr["is_release_train"]]
        internal = [pr for pr in shipped if pr["likely_internal"]]
        candidates = [pr for pr in shipped if not pr["likely_internal"]]
        lines.append(f"  release trains: {len(trains)}")
        lines.append(f"  shipped feature PRs: {len(shipped)} ({len(candidates)} candidates, {len(internal)} internal)")
        for pr in shipped:
            flag = " [internal]" if pr["likely_internal"] else ""
            lines.append(f"    #{pr['number']}: {pr['title']}{flag}")
        if repo.get("releases"):
            lines.append(f"  releases: {len(repo['releases'])}")
            for rel in repo["releases"]:
                lines.append(f"    {rel['tag']}: {rel['name']}")
        if repo.get("merged_not_yet_in_production"):
            lines.append(f"  merged to develop, not yet shipped: {len(repo['merged_not_yet_in_production'])}")
    return "\n".join(lines)


def flatten_markdown(text):
    """Flatten markdown emphasis/links to plain text for a compact one-liner."""
    if not text:
        return ""
    text = re.sub(r"\[(#\d+)\]\([^)]*\)", r"\1", text)
    text = text.replace("**", "").replace("__", "")
    text = text.replace("_", "")
    return re.sub(r"\s+", " ", text).strip()


def format_short_date(iso_str):
    if not iso_str:
        return "unknown"
    try:
        dt = datetime.fromisoformat(iso_str)
    except ValueError:
        return iso_str[:10]
    return dt.strftime("%b %-d")


def format_changelog_for_digest(section):
    """Flatten a `## Changelog` section into a single line for the digest, capped at 600 chars."""
    if not section:
        return None
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    bullets, plain = [], []
    for line in lines:
        match = re.match(r"^[-*]\s+(.*)", line)
        if match:
            bullets.append(match.group(1))
        else:
            plain.append(line)
    if bullets:
        joined = " / ".join(flatten_markdown(b) for b in bullets)
    else:
        joined = flatten_markdown(" ".join(plain))
    return joined[:600] or None


def build_repo_digest_section(repo):
    name = repo["name"]
    display = repo.get("display_name")
    url = repo.get("production_url")
    if display and url:
        header = f"## {name} ({display}, {url})"
    elif url:
        header = f"## {name} ({url})"
    else:
        header = f"## {name}"
    lines = [header]

    if repo.get("error"):
        lines.append(f"Error: {repo['error']}")
        return "\n".join(lines)

    not_yet = repo.get("merged_not_yet_in_production", [])
    not_yet_line = " · ".join(f"#{pr['number']} {pr['title']}" for pr in not_yet)

    if repo.get("releases_only"):
        releases = repo.get("releases", [])
        lines.append(
            f"Releases: {len(releases)}. Merged to the integration branch, not yet released: {len(not_yet)}."
        )
        lines.append("")
        lines.append("### Releases")
        if releases:
            for rel in releases:
                body = flatten_markdown(rel.get("body") or "")[:200]
                date = format_short_date(rel.get("published_at"))
                lines.append(f"- {rel.get('name')} ({rel.get('tag')}, {date}): {body}")
        else:
            lines.append("none in window")
        if not_yet:
            lines.append("")
            lines.append("### Not yet in production (titles only)")
            lines.append(not_yet_line)
        return "\n".join(lines)

    trains = repo.get("release_trains", [])
    shipped = [pr for pr in repo.get("shipped_prs", []) if not pr["is_release_train"]]
    candidates = [pr for pr in shipped if not pr["likely_internal"]]
    internal = [pr for pr in shipped if pr["likely_internal"]]

    lines.append(
        f"Release trains: {len(trains)}. Candidate PRs: {len(candidates)}. "
        f"Filtered as internal: {len(internal)}. Not yet in production: {len(not_yet)}."
    )

    if not trains and not candidates:
        lines.append("")
        lines.append("Nothing reached production this week.")
        if not_yet:
            lines.append("")
            lines.append("### Not yet in production (titles only)")
            lines.append(not_yet_line)
        return "\n".join(lines)

    if candidates:
        lines.append("")
        lines.append("### Candidates")
        for pr in candidates:
            date = format_short_date(pr["shipped_in"]["date"])
            lines.append(f"- #{pr['number']} (shipped {date}) {pr['title']}")
            changelog = format_changelog_for_digest(pr.get("changelog_section"))
            if changelog:
                lines.append(f"  Changelog: {changelog}")
            elif pr.get("body_excerpt"):
                body = re.sub(r"\s+", " ", pr["body_excerpt"]).strip()[:250]
                lines.append(f"  Body: {body}")

    if internal:
        lines.append("")
        lines.append("### Filtered as internal (titles only)")
        lines.append(" · ".join(f"#{pr['number']} {pr['title']}" for pr in internal))

    if not_yet:
        lines.append("")
        lines.append("### Not yet in production (titles only)")
        lines.append(not_yet_line)

    return "\n".join(lines)


def build_markdown_digest(data):
    since = data["window"]["since"][:10]
    until = data["window"]["until"][:10]
    lines = [f"# Shipped digest, {since} to {until}", ""]
    for repo in data["repos"]:
        lines.append(build_repo_digest_section(repo))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--since", help="Window start (YYYY-MM-DD or ISO 8601)")
    parser.add_argument("--until", help="Window end (YYYY-MM-DD or ISO 8601)")
    parser.add_argument("--out", help="Write JSON here instead of stdout. A summary prints either way")
    parser.add_argument(
        "--md",
        help="Write the compact markdown digest here (default: --out path with .md extension, "
        "skipped if --out is not given)",
    )
    parser.add_argument("--config", required=True, help="Path to the skill's CONFIG.md (first fenced json block is read)")
    parser.add_argument("--repos", help="Comma-separated subset of repo names to run")
    parser.add_argument("--skip-fetch", action="store_true", help="Skip git fetch before reading history")
    args = parser.parse_args()

    until = parse_date_arg(args.until, end_of_day=True) if args.until else datetime.now().astimezone()
    since = parse_date_arg(args.since) if args.since else until - timedelta(days=7)

    repos = load_config(args.config)
    if args.repos:
        wanted = set(args.repos.split(","))
        repos = [r for r in repos if r["name"] in wanted]

    results = []
    for repo in repos:
        try:
            results.append(process_repo(repo, since, until, args.skip_fetch))
        except Exception as exc:  # noqa: BLE001 - one bad repo must not kill the run
            results.append({**base_repo_output(repo), "error": f"unhandled: {exc}"})

    data = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "window": {"since": since.isoformat(), "until": until.isoformat()},
        "repos": results,
    }

    md_path = args.md
    if md_path is None and args.out:
        md_path = os.path.splitext(args.out)[0] + ".md"

    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Wrote JSON to {args.out}")
        if md_path:
            os.makedirs(os.path.dirname(md_path) or ".", exist_ok=True)
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(build_markdown_digest(data))
            size_kb = os.path.getsize(md_path) / 1024
            print(f"digest: {md_path} ({size_kb:.1f} KB)")
        print(human_summary(data))
    else:
        print(json.dumps(data, indent=2))

    if all(r.get("error") for r in results):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
