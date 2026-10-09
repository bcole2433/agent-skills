---
name: tend-vault
description: Weekly health check for a markdown knowledge repo. Lints for contradictions, orphans and broken links, checks staleness, tag coverage and page quality, detects recurring patterns, audits lessons, and writes a prioritized report
---

A knowledge repo decays quietly. Pages go stale, links break, tags go missing, and the same topic recurs in reports without anyone naming it. This skill is the weekly maintenance pass. It reads, measures, and reports. It does not rewrite your content.

It runs in two modes:

- **Scheduled (unattended):** write the report, commit, push. Make no content edits unless `SCHEDULED_AUTO_FIX` is `yes` in `CONFIG.md`.
- **Interactive (`/tend`):** show findings inline grouped by severity, propose fixes, and ask before changing anything.

## Config

Read `CONFIG.md` beside this file first. It holds the paths, thresholds, required page structure, and mode. If a required value is still a `<placeholder>`, log it and stop.

## Governance

Before writing any file, load the governance files named in `CONFIG.md` (`CONSTITUTION_PATH`, `WIKI_SCHEMA_PATH`, `CONNECTIVITY_PATH`, `SYNC_STATE_PATH`). Follow `CONSTITUTION_PATH` for operating rules and priorities, `WIKI_SCHEMA_PATH` for page types and conventions, and `CONNECTIVITY_PATH` for the tag and WikiLink contract on every file you create or edit. Read `SYNC_STATE_PATH` for per-source sync state and update it when this skill changes that state. If a file is missing, say so and continue with the skill's own rules.

## Lessons

This skill improves itself. Before running, read `LESSONS_DIR/index.md` from `CONFIG.md`, then `LESSONS_DIR/tend-vault.md` and follow it. After any correction from the user or a failure you worked around, append a dated entry to `LESSONS_DIR/tend-vault.md` using the format in the index, and keep the index current. If `LESSONS_DIR` is blank, skip.

## Phase 1: Load state (minimal reads)

Read the index (page catalog and stats), the sync state file, and the last `LOG_WINDOW_DAYS` of the log. Use an offset to skip older log entries. If `LINK_CONTRACT_PATH` is set, read it, the connectivity checks below audit against it.

Large files: read them with the Read tool and an offset or limit, not `cat`. Bash output over its inline cap is persisted to a file and re-reading that file loops.

## Phase 2: Lint

Read each wiki page listed in the index, then check:

- **Contradictions:** compare claims across pages (dates, statuses, owners, descriptions). Quote both sides.
- **Orphans:** pages with zero inbound links.
- **Missing pages:** `[[WikiLinks]]` that point at nonexistent pages.
- **Gaps:** entities mentioned in three or more pages that lack their own page.
- **Unlinked mentions:** known entities from the index that are mentioned but not linked.

For a large repo, build the link graph with a script instead of reading every page into context. Read in full only the pages the script flags.

## Phase 2b: Tag and frontmatter coverage

Use the bundled scanner, not a read of every file. `raw/` and report folders are large.

```bash
python3 skills/tend-vault/lint_tags.py --dirs wiki lessons pending raw --min-tags 3 --report-dir pending
```

It reports per directory the files with no `tags:`, files under the minimum, and reports whose first line is not `---`. Templates are skipped because their empty tag list is intentional. Keep the per-directory counts in the report so coverage trend is visible week to week, and list named offenders so a backfill can target them.

## Phase 3: Staleness and quality

For each wiki page already loaded:

**Staleness**
- `updated` older than `STALE_AFTER_DAYS` in an active domain that has had recent ingests means potentially stale.
- Any source in the sync state not synced within `SYNC_STALE_AFTER_DAYS`.

**Quality**
- Has every heading in `REQUIRED_SECTIONS`?
- Has every field in `REQUIRED_FRONTMATTER`?
- Longer than `MAX_PAGE_LINES`? Flag for splitting.

## Phase 4: Pattern detection

Read only the last `PATTERN_WINDOW_DAYS` of daily notes and run reports. **Do not re-read raw files.** Reports are the summaries.

Look for:
- Topics mentioned `PATTERN_MIN_MENTIONS` or more times in the window.
- Recurring blockers.
- Emerging themes with no wiki page.
- Action items that appear across several reports and never close.

## Phase 4b: Lessons maintenance

Skip if `LESSONS_DIR` is blank. Read the lessons index and each category file, then check:

- **Overlap:** two categories covering similar ground, suggest consolidation.
- **Oversized:** a category above `MAX_LESSON_FILE_LINES`, suggest splitting.
- **Unreferenced:** lessons no longer reflected in any page or process doc.
- **Missing categories:** recurring patterns from this week's reports with no category yet.
- **Stale routing:** index entries pointing at missing files, or category files absent from the index.
- **Orphaned lessons:** each category file should have a `## Relations` section linking the entities it references, and those targets should link back. Flag any lesson file with no outbound links and any link that is not reciprocated.

Never modify lesson files in this skill. Flag them for the owner's review.

## Phase 5: Report

Write `REPORTS_DIR/YYYY-MM-DD-tend.md`. It must open with frontmatter, never a bare heading:

```yaml
---
type: pending-review
created: YYYY-MM-DD
pipeline: tend-vault
status: needs-review
tags: [pending-review, tend-vault, <domains with issues this week>]
---
```

Sections, in order:

1. **Health score:** percent of pages passing every quality check.
2. **Contradictions**
3. **Orphans and missing pages**
4. **Stale content**
5. **Tag and connectivity coverage:** counts and named offenders per directory
6. **Emerging patterns**
7. **Proposed new pages**
8. **Missing cross-references**
9. **Lessons review**
10. **Recommendations:** prioritized, highest impact first

Write every page you name as a `[[WikiLink]]` so the report is a hub in the graph.

### Interactive mode severity

When run interactively, present the same findings grouped by severity and ask before any change:

- **Red:** contradictions, broken links, missing required sections.
- **Yellow:** stale content, orphan pages, quality issues, missing tags.
- **Blue:** patterns, recommended new pages, missing cross-references.

## Phase 6: Commit and push

Commit only the report: `[tend-vault] YYYY-MM-DD: vault health check, X issues, Y recommendations`. Never `git add -A`.

Then `git pull --rebase origin main` and `git push origin main`. Try once, do not retry, and never fail the run or undo the commit over a push problem. Note any push failure in the report. In a git worktree whose branch is not `main`, push `HEAD:main` instead, because a stale local `main` ref can make a plain push print "Everything up-to-date" while publishing nothing.

## Rules

- Read-only on content. The only file this skill creates is the report (plus the optional auto-fix mode).
- Quote specifics. "Page A says launch is March 3, page B says March 10" beats "dates may conflict".
- Do not report an issue you did not verify against the file.
- Apply `STYLE_RULES` to the report text you write, checking added lines only.
- If a run finds nothing, say so in a short report instead of padding it.
