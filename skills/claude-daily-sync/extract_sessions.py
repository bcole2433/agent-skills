#!/usr/bin/env python3
"""
extract_sessions.py - Digest on-disk agent session transcripts.

The agent stores terminal and IDE sessions as JSONL transcripts at
~/.claude/projects/<escaped-cwd>/<session-uuid>.jsonl. This script reads them directly and emits
a compact Markdown digest (user prompts plus the final assistant note) so an agent can triage
decisions without loading images or tool output into context.

Usage:
    python3 extract_sessions.py --since 2026-05-29
    python3 extract_sessions.py --since 2026-05-29 --include-project myapp --include-project api
    python3 extract_sessions.py --since 2026-05-29 --exclude-session "daily[- ]sync|weekly retro"

Output: Markdown to stdout, grouped by project directory name.
"""
import argparse
import datetime as dt
import glob
import json
import os
import re

# System and IDE wrappers injected into user turns. Strip the wrapper, keep any real prompt around it.
WRAPPER = re.compile(r"<(ide_[^>]*|command-[^>]*|system-reminder|local-command-[^>]*)>.*?</\1>", re.S)
NOISE_PREFIX = ("<command-", "<local-command", "<system-reminder", "Caveat:")
# Prompts that are pure tooling noise (skill preambles, interrupt markers, continuation stubs).
TOOLING_NOISE = re.compile(
    r"Base directory for this skill|^\[Request interrupted|^\[The user|"
    r"This session is being continued from a previous",
    re.I,
)
USER_CAP = 600          # chars per user prompt
ASSISTANT_CAP = 900     # chars for the final assistant note
MAX_PROMPTS = 25        # prompts listed per session
PIPELINE_PROMPTS = 3    # how many opening prompts to test against --exclude-session


def parse_since(s):
    return dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc)


def to_dt(ts):
    try:
        return dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def text_of(message):
    """Concatenate the text blocks of a message, skipping images, tool use, tool results and thinking."""
    if not isinstance(message, dict):
        return ""
    c = message.get("content")
    if isinstance(c, str):
        return c.strip()
    if isinstance(c, list):
        parts = []
        for b in c:
            if isinstance(b, dict) and b.get("type") == "text":
                t = (b.get("text") or "").strip()
                if t:
                    parts.append(t)
        return "\n".join(parts).strip()
    return ""


def clean_prompt(text):
    """Strip wrappers. Return an empty string if what remains is tooling noise."""
    if not text:
        return ""
    text = WRAPPER.sub("", text).strip()
    if not text:
        return ""
    if text.startswith(NOISE_PREFIX) or TOOLING_NOISE.search(text):
        return ""
    return text


def load(path):
    rows = []
    try:
        with open(path, "r", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        return None
    return rows


def digest_file(path, since_dt, exclude_session):
    rows = load(path)
    if not rows:
        return None

    title = next((r.get("aiTitle") for r in rows if r.get("type") == "ai-title" and r.get("aiTitle")), None)
    cwd = next((r.get("cwd") for r in rows if r.get("cwd")), None)
    branch = next((r.get("gitBranch") for r in rows if r.get("gitBranch")), None)
    session_id = next((r.get("sessionId") for r in rows if r.get("sessionId")), os.path.basename(path)[:-6])

    stamps = [s for s in (to_dt(r["timestamp"]) for r in rows if r.get("timestamp")) if s]
    if not stamps:
        return None
    first_ts, last_ts = min(stamps), max(stamps)
    if last_ts <= since_dt:
        return None

    prompts, final_note, n_user, n_assistant = [], "", 0, 0
    for r in rows:
        if r.get("type") == "user":
            t = clean_prompt(text_of(r.get("message", {})))
            if t:
                n_user += 1
                prompts.append(t[:USER_CAP])
        elif r.get("type") == "assistant":
            t = text_of(r.get("message", {}))
            if t:
                n_assistant += 1
                final_note = t  # keep the last non-empty assistant text

    opening = "\n".join(prompts[:PIPELINE_PROMPTS])
    is_excluded = bool(
        exclude_session
        and (
            (title and exclude_session.search(title))
            or exclude_session.search(opening)
        )
    )

    return {
        "path": path,
        "session_id": session_id,
        "title": title or "(untitled)",
        "project": (os.path.basename(cwd) if cwd else os.path.basename(os.path.dirname(path))) or "(unknown)",
        "cwd": cwd or "",
        "branch": branch or "",
        "first": first_ts,
        "last": last_ts,
        "n_user": n_user,
        "n_assistant": n_assistant,
        "prompts": prompts[:MAX_PROMPTS],
        "final_note": (final_note or "")[:ASSISTANT_CAP],
        "is_excluded": is_excluded,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True, help="YYYY-MM-DD. Include sessions active after this date.")
    ap.add_argument("--root", default="~/.claude/projects")
    ap.add_argument(
        "--include-project",
        action="append",
        default=[],
        help="Case-insensitive substring of the session cwd. Repeatable. Default: include every project.",
    )
    ap.add_argument(
        "--exclude-session",
        default="",
        help="Regex tested against the session title and its first prompts. Matches are skipped. "
             "Use it to drop your own automation sessions.",
    )
    args = ap.parse_args()

    since_dt = parse_since(args.since)
    root = os.path.expanduser(args.root)
    exclude = re.compile(args.exclude_session, re.I) if args.exclude_session else None
    includes = [s.lower() for s in args.include_project]
    paths = sorted(glob.glob(os.path.join(root, "*", "*.jsonl")))

    sessions, skipped_excluded, skipped_project = [], 0, 0
    for p in paths:
        d = digest_file(p, since_dt, exclude)
        if not d:
            continue
        if d["is_excluded"]:
            skipped_excluded += 1
            continue
        if includes and not any(tok in (d["cwd"] or p).lower() for tok in includes):
            skipped_project += 1
            continue
        sessions.append(d)

    sessions.sort(key=lambda d: (d["project"], d["last"]))

    print(f"# Claude Sessions Digest - on-disk transcripts since {args.since}\n")
    print(f"_Scanned {len(paths)} transcripts under {args.root}. "
          f"Qualifying: {len(sessions)}. Skipped: {skipped_excluded} excluded by pattern, "
          f"{skipped_project} outside --include-project._\n")
    if not sessions:
        print("No qualifying sessions.")
        return

    by_project = {}
    for d in sessions:
        by_project.setdefault(d["project"], []).append(d)

    print("## Projects with sessions\n")
    for proj, items in by_project.items():
        print(f"- **{proj}**: {len(items)} session(s)")
    print()

    for proj, items in by_project.items():
        print(f"\n## Project: {proj}\n")
        for d in items:
            print(f"### {d['title']}")
            print(f"- session_id: `{d['session_id']}`")
            print(f"- cwd: `{d['cwd']}`  branch: `{d['branch']}`")
            print(f"- window: {d['first'].strftime('%Y-%m-%d %H:%M')} -> "
                  f"{d['last'].strftime('%Y-%m-%d %H:%M')} UTC  "
                  f"({d['n_user']} user / {d['n_assistant']} assistant msgs)")
            print(f"- file: `{d['path']}`")
            if d["prompts"]:
                print("\n**User prompts:**")
                for i, pr in enumerate(d["prompts"], 1):
                    print(f"{i}. {' '.join(pr.split())}")
            if d["final_note"]:
                print(f"\n**Final assistant note:** {' '.join(d['final_note'].split())}")
            print("\n---")


if __name__ == "__main__":
    main()
