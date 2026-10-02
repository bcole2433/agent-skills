#!/usr/bin/env python3
"""
lint_tags.py - Fast tag and frontmatter coverage scan for a markdown knowledge repo.

Reports, per directory:
  - files with no `tags:` line
  - files with fewer than --min-tags tags
  - files in --report-dir (default: pending) whose first line is not `---`

Usage:
    python3 lint_tags.py --dirs wiki lessons pending raw
    python3 lint_tags.py --dirs wiki lessons --min-tags 3 --report-dir pending

Templates (any path containing `_templates`) are skipped because their empty `tags: []` is intentional.
Run from the repo root. Prints Markdown so the output can be pasted into a report.
"""
import argparse
import os
import re

TAGS_LINE = re.compile(r"^tags:\s*(.*)$", re.M)


def count_tags(raw):
    """Count tags in an inline list. Return None when the value is a block list."""
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        return len([t for t in inner.split(",") if t.strip()])
    if raw == "":
        return None
    return len([t for t in raw.split(",") if t.strip()])


def block_list_count(lines, start):
    n = 0
    for line in lines[start + 1:]:
        if line.lstrip().startswith("- "):
            n += 1
        else:
            break
    return n


def scan(root, dirs, min_tags, report_dir):
    result = {d: {"no_tags": [], "few_tags": [], "bad_frontmatter": [], "total": 0} for d in dirs}
    for d in dirs:
        base = os.path.join(root, d)
        for dirpath, _, files in os.walk(base):
            if "_templates" in dirpath:
                continue
            for name in files:
                if not name.endswith(".md"):
                    continue
                path = os.path.join(dirpath, name)
                result[d]["total"] += 1
                with open(path, "r", errors="replace") as fh:
                    text = fh.read()
                lines = text.splitlines()
                if d == report_dir and (not lines or lines[0].strip() != "---"):
                    result[d]["bad_frontmatter"].append(path)
                m = TAGS_LINE.search(text)
                if not m:
                    result[d]["no_tags"].append(path)
                    continue
                n = count_tags(m.group(1))
                if n is None:
                    idx = next(i for i, line in enumerate(lines) if line.startswith("tags:"))
                    n = block_list_count(lines, idx)
                if n < min_tags:
                    result[d]["few_tags"].append((path, n))
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", nargs="+", required=True)
    ap.add_argument("--min-tags", type=int, default=3)
    ap.add_argument("--report-dir", default="pending")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()

    result = scan(args.root, args.dirs, args.min_tags, args.report_dir)

    print("# Tag coverage\n")
    print("| Directory | Files | No tags | Under minimum | Bad frontmatter |")
    print("|---|---|---|---|---|")
    for d, r in result.items():
        print(f"| {d} | {r['total']} | {len(r['no_tags'])} | {len(r['few_tags'])} | {len(r['bad_frontmatter'])} |")

    for d, r in result.items():
        if r["no_tags"]:
            print(f"\n## {d}: no tags\n")
            for p in sorted(r["no_tags"]):
                print(f"- {p}")
        if r["few_tags"]:
            print(f"\n## {d}: fewer than {args.min_tags} tags\n")
            for p, n in sorted(r["few_tags"]):
                print(f"- {p} ({n})")
        if r["bad_frontmatter"]:
            print(f"\n## {d}: first line is not `---`\n")
            for p in sorted(r["bad_frontmatter"]):
                print(f"- {p}")


if __name__ == "__main__":
    main()
