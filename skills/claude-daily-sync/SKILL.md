---
name: claude-daily-sync
description: Daily local-only sync of agent memory files and session transcripts into a git-tracked knowledge repo, so cloud routines and teammates can read data that only exists on your machine
---

The agent keeps memory files and session transcripts under `~/.claude/projects/`. That directory exists only on your local machine, so cloud routines cannot see it. This skill snapshots what changed into a git repo and pushes it, which makes that history available anywhere the repo is.

It is a capture pipeline first. Anything beyond capture (ingesting into a wiki, extracting lessons) is optional and driven by what the target repo already has.

## Config

Read `CONFIG.md` beside this file first. It holds the repo path, remote and branch, the session filters, and the optional-output switches. Use its values wherever this file says "the knowledge repo", `--exclude-session`, or `--include-project`. If a required value is still a `<placeholder>`, log it and stop.

## Governance

Before writing any file, load the governance files named in `CONFIG.md` (`CONSTITUTION_PATH`, `WIKI_SCHEMA_PATH`, `CONNECTIVITY_PATH`, `SYNC_STATE_PATH`). Follow `CONSTITUTION_PATH` for operating rules and priorities, `WIKI_SCHEMA_PATH` for page types and conventions, and `CONNECTIVITY_PATH` for the tag and WikiLink contract on every file you create or edit. Read `SYNC_STATE_PATH` for per-source sync state and update it when this skill changes that state. If a file is missing, say so and continue with the skill's own rules.

## Lessons

This skill improves itself. Before running, read `LESSONS_DIR/index.md` from `CONFIG.md`, then `LESSONS_DIR/claude-daily-sync.md` and follow it. After any correction from the user or a failure you worked around, append a dated entry to `LESSONS_DIR/claude-daily-sync.md` using the format in the index, and keep the index current. If `LESSONS_DIR` is blank, skip.

## Target repo layout

The skill writes into a repo you own (the "knowledge repo"). Only the first three entries are required. Everything else is optional and used only if present.

```
raw/claude/memory/YYYY-MM-DD.md      memory snapshots (immutable once written)
raw/claude/sessions/YYYY-MM-DD.md    session digests (immutable once written)
SYNC-STATE.md                        last-sync timestamps, one table per source
sync-notes.md                        gotchas this pipeline hit (see Run notes)
log.md                               optional, newest entry first
pending/YYYY-MM-DD-claude-sync.md    optional run report for human review
```

Static method lives here in SKILL.md. Anything that changes run to run (timestamps, gotchas, counts) lives in those repo files, never in this file.

## Phase 0: Guard

1. If `~/.claude/projects` does not exist, log "not a local environment, skipping" and stop. Write nothing and commit nothing.
2. `git pull --rebase origin main` in the knowledge repo. If a foreign file you did not touch blocks the pull, stash that path by name (never the whole tree), pull, pop, and confirm the pop restored it with `git diff --quiet HEAD -- <file>` reporting dirty.
3. Read `sync-notes.md` if it exists. It records problems earlier runs hit and how they were solved.

## Phase 1: Scan

1. Read `SYNC-STATE.md` for the last sync time of each source. Cross-check it against `ls -t raw/claude/sessions | head -3` and `ls -t raw/claude/memory | head -3` and use whichever is newer. State tables drift, the files on disk do not.
2. **Memory change detection.** Enumerate memory files with `find ~/.claude/projects -maxdepth 3 -name "*.md" -path "*/memory/*"` (depth 3 is correct, depth 2 returns nothing). Use mtime as the primary change signal.
   - macOS (BSD find) has no `-printf`. Use `-newermt "<date>"` for the filter and `-exec stat -f "%Sm %N" -t "%Y-%m-%d %H:%M:%S" {} +` to print times.
   - On a same-day second run anchor on the prior snapshot file instead of a date: `find ... -newer raw/claude/memory/<prior>.md`. A date means midnight and re-flags everything the earlier run captured.
   - Compare the total file count to the prior snapshot to catch deletions and brand-new projects.
   - Project directory names start with a hyphen. Always use absolute paths or `--` when passing them to `cat`.
3. **Session extraction.** Run the bundled extractor with a long timeout (300000 ms or more). A short timeout can truncate output silently with exit 0.

   ```bash
   python3 skills/claude-daily-sync/extract_sessions.py --since <last sync date> \
     --exclude-session "daily[- ]sync|<your other automation titles>" \
     [--include-project <cwd-substring> ...]
   ```

   Cross-check `grep -c '^### '` against the qualifying count in the digest header before trusting it.
4. **Dedupe by session id, in one pass.** `--since` filters by calendar date, but the previous run extended past midnight, so same-day candidates can already be captured.
   - Build the candidate list from the `session_id:` lines only, never from every UUID in the digest (prompts quote other ids).
   - Concatenate every prior digest back to and including the last-sync date. Do not use a fixed file count, a gap run will outrun it.
   - Match with one `grep -o -F -f ids.txt prior.txt | sort -u`. A per-id shell loop has silently reported zero duplicates before.
   - Record the window and counts in the new file header, for example "18 qualifying, 3 already captured, 15 net-new".
5. If there are no memory changes and no net-new sessions, write nothing except the `SYNC-STATE.md` timestamps and a minimal pending note, commit, and stop.

## Phase 2: Capture

Finish every read and every raw write before editing anything else. If the run is interrupted, the raw files let a resumed run re-derive the rest.

### Memory

Read every changed memory file in full and write one snapshot to `raw/claude/memory/YYYY-MM-DD.md` (suffix `-b`, `-c` for later runs the same day). Group by project. Do not assume a file is unchanged because it existed before, formatting-only edits count.

```markdown
---
type: raw
source: claude-memory
date: YYYY-MM-DD
files_changed: [paths]
tags: [source, claude-memory, <topics>]
---

# Claude Memory Snapshot (YYYY-MM-DD)

## <project name>

### <file name>
<full file content in a fenced block>
```

Fenced blocks reproduce the source verbatim, including its own punctuation. Never edit a snapshot to satisfy a style rule.

### Sessions

Triage from the digest. The prompts show intent and the final assistant note usually carries the outcome. Keep sessions that contain a decision, a direction change, a lesson, or a durable output. Drop pure mechanical implementation and your own automation sessions. Reach for a transcript file only when a session looks important but ambiguous.

- **Group by each block's own `cwd`, never by the `## Project:` heading above it.** Filtering removes headings, and worktree checkouts can be filed under an unrelated project. Name a worktree explicitly.
- **Split the digest with Python, not `awk -v RS`.** macOS awk only supports a single-character record separator and fails silently with an empty file. Split on `'\n### '` and `wc -c` the result.
- **Read large files with the Read tool, not `cat`.** Bash output over its inline cap is persisted to a file and `cat` on that file persists again. Filter to net-new blocks first, then Read.
- Bounded range reads on macOS: `sed -n 'START,ENDp'`. The GNU `START,+Np` form fails on BSD sed.

Write the result to `raw/claude/sessions/YYYY-MM-DD.md`:

```markdown
---
type: raw
source: claude-sessions
date: YYYY-MM-DD
session_ids: [every id included]
tags: [source, claude-sessions, <topics>]
---

# Claude Sessions Digest (YYYY-MM-DD)

## Project: <cwd basename>

### Session: <title> (YYYY-MM-DD HH:MM)
**Session ID:** <uuid>
**Key outputs:**
- <decision or direction, paraphrased>
```

Then diff the ids written against the net-new list in both directions with `comm -23` and `comm -13`. A stray duplicate block in the body gets re-ingested downstream even when the frontmatter is right.

**Sessions are candid.** Record decisions and outputs. Never quote prompts verbatim, and never copy secrets, tokens, or personal data that appear in a transcript.

## Phase 3: Ingest (optional)

Skip this phase if the repo is a plain archive. If it has a wiki, index, or lessons folder, read its index first, verify every path with `find` before editing, update only the pages a new fact touches, and flag contradictions instead of silently overwriting. Append lesson-shaped content (postmortems, root causes, "next time we should") to the matching lessons file with a source reference.

## Phase 4: Record

1. Update `SYNC-STATE.md`. Locate the section header for each source first, then the table separator that follows it, and insert there. A prepend anchored on "first table row" can land in the wrong table. Prepend a new row and keep the prior one as history.
2. If the repo keeps `log.md`, add an entry above the first existing entry (newest first), anchoring on that heading's exact text and asserting it occurs once.
3. Write `pending/YYYY-MM-DD-claude-sync.md` if the repo uses one. Open with frontmatter, never a bare heading. Include a summary, files changed, anything flagged for review, and the exact counts.
4. Commit only this pipeline's own paths. Never `git add -A`, other automation may have files mid-write in the same repo. Name the paths explicitly.

   Commit message: `[claude-daily-sync] YYYY-MM-DD: X memory changes, Y sessions net-new`

## Phase 5: Push

`git pull --rebase origin main` then `git push origin main`. Try once, do not retry, and never fail the run or undo the local commit over a push problem. Note any failure in the run record.

- A closing pull can fail on the same foreign dirty file as the opening one. Run the push anyway. It usually fast-forwards. Look for the `a1b2c3..d4e5f6 main -> main` line, a failed pull does not mean the run did not publish.
- If origin moved and the rebase conflicts, resolve by keeping both sides: chronological files take the incoming entry first and yours after, stats lines demote the incoming one to a "prior" entry.
- If `git rebase --continue` refuses after real conflicts are resolved, `git commit -C <pre-rebase-sha>`, verify with `git show --stat`, `git rebase --quit`, `git checkout -B main <new-sha>`, then push.
- A `git diff -- $VAR` pathspec built from a shell variable silently returns nothing. Write paths literally and cross-check against `git diff --stat`.

## Run notes

When a run hits a problem and finds a working fix, append it to `sync-notes.md` in the knowledge repo (date, symptom, fix) and commit it with the run. Do not edit this SKILL.md. Keeping method static and run-specific history in repo files means the skill stays portable and the notes stay greppable.

## Rules

- Raw files are immutable after creation.
- Newer source wins for facts. Ambiguous contradictions get flagged, not resolved.
- If a change would remove significant content, flag it in the report instead of applying it.
- If the extractor fails (no python, unreadable transcripts), log the error and stop.
- Check style on the lines you added, not the whole file: `git diff -- <file> | grep '^+'`.
