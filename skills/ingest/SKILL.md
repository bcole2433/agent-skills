---
name: ingest
description: Manually ingest a source into a knowledge repo. Takes a raw file path, a docs-tool URL, or "all", writes an immutable raw snapshot, then extracts entities, decisions and status changes into wiki pages
---

On-demand command, the manual counterpart to `nightly-sync`. Use it when you do not want to wait for the nightly run, or when a single source needs ingesting now.

## Config

Read `CONFIG.md` beside this file first. It holds the repo layout, the raw category map, and where the docs sources are defined. If a required value is still a `<placeholder>`, say which one and stop.

## Governance

Before writing any file, load the governance files named in `CONFIG.md` (`CONSTITUTION_PATH`, `WIKI_SCHEMA_PATH`, `CONNECTIVITY_PATH`, `SYNC_STATE_PATH`). Follow `CONSTITUTION_PATH` for operating rules and priorities, `WIKI_SCHEMA_PATH` for page types and conventions, and `CONNECTIVITY_PATH` for the tag and WikiLink contract on every file you create or edit. Read `SYNC_STATE_PATH` for per-source sync state and update it when this skill changes that state. If a file is missing, say so and continue with the skill's own rules.

## Process

1. Read the operating principles and schema documents named in `CONFIG.md`, then the index for current wiki state.
2. Branch on the argument.

### A file path under `RAW_DIR`

1. Read the file.
2. Run the ingest operation: extract entities, concepts, decisions, status changes, action items, contradictions and lessons.
3. Update or create wiki pages (see "Ingest operation").
4. Update the index and add a log entry.
5. Show which pages were created or updated.

### A docs-tool URL

1. Fetch the page with your docs tool or CLI.
2. Export the full content to `RAW_DIR/<tool>/<category>/YYYY-MM-DD-slug.md` using the category map in `CONFIG.md`. The raw file gets tags in its frontmatter at creation and is immutable afterward.
3. Run the ingest operation on the new raw file.
4. Update the index, add a log entry, and update the sync state file.
5. Show which pages were created or updated.

### "all" or "sync"

1. Read the sync state for last-sync timestamps.
2. Check each source in the sources config for changes since then. For databases, query the rows sorted by last edited and compare the newest row. Never trust the container's own timestamp, it tracks schema edits and not row edits.
3. For each changed source, fetch it and export it as above.
4. Run the ingest operation on each new raw file.
5. Update all metadata files and write the run report to `REPORTS_DIR`.
6. Commit. This path is the same work `nightly-sync` does, so follow that skill's phases if you need more detail.

## Ingest operation

- Use the index to find only the pages the extracted content might touch, and read only those. Verify every path with `find` before editing.
- Existing page: update it, bump `updated`, and append a dated line to its Log.
- Genuinely new entity or concept: create a page from the template in `TEMPLATES_DIR`.
- Contradiction: flag it in the page's Questions section as `[NEEDS REVIEW]`. Newer source wins for facts, ambiguous cases stay flagged.
- Resolve person references against the people registry.
- If a wiki update would remove significant content, show it and ask instead of applying it.

## Rules

- Raw files are immutable after creation.
- Always show a summary of changes before committing, and wait for approval in interactive use.
- Commit only the paths this ingest touched. Never `git add -A`.
- Meeting notes and DMs can be sensitive. Extract work-relevant content only and never quote private conversation.
- Apply `STYLE_RULES` to text you write, checking only the lines you added.
