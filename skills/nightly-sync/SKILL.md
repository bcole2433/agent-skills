---
name: nightly-sync
description: Nightly pull of changes from external work tools (docs, databases, chat) into a git-tracked knowledge repo as immutable raw files, then targeted ingest into a wiki and a review report
---

Work knowledge lives in tools like a docs workspace and a chat app. This skill pulls only what changed since the last run into a git repo, files it as immutable raw snapshots, folds the signal into a wiki, and leaves a short report for a human to review. It is source-agnostic. Which sources to read is listed in `CONFIG.md`, not here.

Notion and Slack appear below as worked examples because they are common. Swap in any docs, tracker, or chat tool that can be read by CLI or MCP.

Local Claude memory and sessions are a different pipeline (`claude-daily-sync`). Do not add them here, two pipelines writing the same files will race.

## Target repo layout

```
SYNC-STATE.md                   last-sync timestamp per source, one table per tool
index.md                        catalog of wiki pages
log.md                          one line per run, newest first
raw/<tool>/<category>/DATE.md   immutable snapshots
wiki/                           curated pages
lessons/                        optional, lesson files plus an index
decisions/OPEN-QUESTIONS.md     optional decision ledger
pending/DATE-nightly.md         the run report
sync-notes.md                   gotchas earlier runs hit (see Run notes)
```

Static method lives in this file. Run-specific history (timestamps, gotchas, counts) lives in repo files.

### CONFIG.md

Every constant lives in `CONFIG.md` beside this file: repo path, docs sources with ids, chat channels and DMs, wiki folders, style rules. Read it first. If a required value is still a `<placeholder>`, log it and skip that source instead of guessing. `Kind` in the docs table matters because change detection differs (see Phase 1).

## Phase 1: Scan (minimize reads)

1. Read `CONFIG.md`, `SYNC-STATE.md`, `index.md`, and `sync-notes.md`.
2. **Check each source's readiness with a real call, not an environment variable.** Many CLIs authenticate from their own credential store, so a missing `*_TOKEN` variable proves nothing. Use the tool's own health check if it has one (for example `ntn doctor`) or just make the first read and inspect the exit code and payload. Only a missing binary, a non-zero exit, an auth-error payload, or a 401/403 means unavailable. Then log it, skip that tool's sources, and continue with the rest. Never fail the whole run for one tool.
3. **Detect change cheaply, per source kind.**
   - **Page or document:** compare its `last_edited_time` to the last sync.
   - **Database or collection: never trust the container's own timestamp.** It tracks edits to the schema and name, not to rows. One run reported "unchanged" five nights straight while 13 rows changed underneath. Query the rows sorted by last edited descending and compare the newest row to the last sync.
   - **Chat channel:** read history with `oldest` set to the last sync time.
4. **Compute timestamps with a script, never by hand.** A hand-converted epoch was a full year off and silently returned a year of history. Run `date -j -u -f "%Y-%m-%d" "YYYY-MM-DD" +%s` on macOS or `date -u -d YYYY-MM-DD +%s` on Linux, and sanity-check that the result is in the current year's range.
5. **In shell loops, never name a variable `path`.** In zsh `path` is tied to `PATH`. Assigning to it mid-loop breaks command lookup for the rest of the loop with `command not found` and empty output. Use `api_path`, `src_path`, or similar.
6. **Chat DMs and group chats:** resolve a person to a user id first and pass it as the channel id. Prefer channels known to carry work content and skip bot-only channels on the first pass.
7. **The recorded last-sync date understates the prior run's real coverage.** A run dated the 21st that executed in the evening covered that evening, but the next `oldest` is anchored to midnight. Before drafting the raw file, grep the immediately prior raw file for a short distinctive substring of each fetched message (name plus a few words) and drop what is already there. State the overlap in the new raw file, for example "4 of 5 channels duplicated the prior sync, only the following is new".
8. If nothing changed anywhere, write a minimal `pending/DATE-nightly.md` ("No changes detected"), update the `SYNC-STATE.md` timestamps, commit, and stop.

## Phase 2: Fetch changed sources only

Skip unchanged sources entirely. Do not fetch, export, or read them.

For each changed source, export a snapshot to the destination in `CONFIG.md`. A `404 object_not_found` from a docs tool usually means the integration was never shared into that page or database, which is a permissions fix and not an auth failure.

**Raw file frontmatter** (tags are set at creation because the file is immutable afterward):

```markdown
---
type: raw
source: <tool>
date: YYYY-MM-DD
fetched: YYYY-MM-DD
tags: [source, <tool>, <domain>, <initiative>]
---
```

**Chat export format:** one file per day covering all channels and DMs, with a `## #channel` heading per channel and `**[HH:MM] Person:** text` lines, thread replies quoted beneath.

**Capture from chat and docs:** decisions (including informal ones like "let's go with X"), action items and owners, status of active projects, links to specs and designs, open questions and whether they were answered.

**Skip:** pure social messages, bot output with no decision thread, reaction-only replies, scheduling logistics.

Docs tool examples with the Notion CLI, where databases are queried by data source:

```bash
ntn api v1/databases/<db_id> | jq -r '.data_sources[0].id'
ntn api v1/data_sources/<ds_id>/query -d '{"sorts":[{"timestamp":"last_edited_time","direction":"descending"}],"page_size":25}'
ntn pages get <page_id>   # page as Markdown
```

## Phase 3: Targeted ingest

**Finish every read and every raw write before editing any wiki page.** If the run is interrupted, the raw files let a resumed run re-derive everything. Never interleave reads and edits.

1. Read the people registry only if meeting notes or chat were fetched, and resolve names against it.
2. From each new raw file extract entities, decisions, status changes, action items, contradictions, and lessons.
3. Use `index.md` to pick only the pages that might be affected, and read only those. **Verify every path with `find` before editing.** Never infer a path from a page title.
4. For each item: update the existing page (new info, bump `updated`, append to its Log), or create a page from a template if it is a genuinely new entity or concept, or flag a contradiction in a Questions section as `[NEEDS REVIEW]`.
5. **Linking contract (if the repo is a linked wiki, such as an Obsidian vault):** every file you touch keeps at least 3 tags, every entity mentioned gets a `[[WikiLink]]`, and pages keep a `## Relations` section above `## Log`. Raw files get tags but no wikilinks, because bare date basenames collide across folders. When you add a lesson, link the entities it references and back-link the lesson from each of those entity pages.

**Chat ingest rules:**
- Attribute by person, not channel. "Dana said in #engineering the SDK is blocked" updates the SDK page's Questions section.
- Informal channel agreements are real decisions. Treat them like meeting decisions.
- DMs often hold 1:1 context that never reaches meeting notes. Extract project-relevant decisions and status only.
- Do not create a page for a single chat mention unless it is substantial and not captured elsewhere.
- If docs and chat cover the same topic on the same day, merge into one update.

**Lessons:** look for postmortems, "we learned that", "next time we should", root causes, and process breakdowns. Read the lessons index, append a 2 to 4 sentence dated entry to the best-fitting category (or create one and route it from the index), and cite the source (`from meeting YYYY-MM-DD, [[Entity]]` or `from Slack #channel, YYYY-MM-DD`).

## Phase 4: Metadata and report

1. Update `index.md` and `SYNC-STATE.md`. In `SYNC-STATE.md` find the section header for the tool first, then the table separator after it, and insert there. Keep the prior row as history.
2. Add a `log.md` entry above the existing newest entry: `## [YYYY-MM-DD] nightly-sync | X doc sources, Y chat channels, W pages created, V updated`. Anchor on the first heading's exact text and assert it occurs once.
3. **Decision ledger (if the repo has one).** Run `git status` on it before touching it. A human may have hand-edited it, for example flipping an entry to `closed` with or without a note. Treat that as real in-progress work. Finish the reconciliation by moving the entry to Resolved, keep any rationale they wrote, flag entries with no rationale instead of inventing one, and note it in the report so it does not look like it came from tonight's sources. Then append new decision-worthy items with the next id, move settled questions to Resolved with the resolving source cited, and bump `updated`. Leave the file alone if nothing changed. Explicit decisions ("we decided", "going with") also get their own `decisions/DATE-slug.md` linked from the ledger entry they resolve.
4. Write `pending/DATE-nightly.md`. **It must open with frontmatter, never a bare heading:**

   ```yaml
   ---
   type: pending-review
   created: YYYY-MM-DD
   pipeline: nightly-sync
   status: needs-review
   tags: [pending-review, <domains>, <initiatives>]
   ---
   ```

   Sections: Summary (2 to 3 sentences), Decisions Needed (top 3 open ledger entries by stakes, each with age in days), Changes (path, what, why, source), New Pages, Lessons Added or Updated, Contradictions, Status Changes, Action Items, Stale Content, Recommendations. Write every page named as a `[[WikiLink]]`.
5. Commit only this pipeline's paths, never `git add -A`. Message: `[nightly-sync] YYYY-MM-DD: X doc sources, Y chat sources, W pages created, V updated`.

## Phase 5: Push

`git pull --rebase origin main`, then push. Try once and never fail the run or undo the commit over a push problem. Note any failure in the log entry or report.

**In a git worktree, push `HEAD`, not `main`.** If the worktree's branch is not `main`, a stale local `main` ref may exist because another worktree has it checked out. `git push origin main` then pushes that stale ref and prints "Everything up-to-date" while your commit is never published. Check `git branch --list main` (a `+` prefix means it is checked out elsewhere), push with `git push origin HEAD:main`, and confirm with `git fetch origin --quiet && git log --oneline -1 origin/main` that the hash matches your `HEAD`.

## Run notes

When a run hits a problem and finds a fix, append date, symptom, and fix to `sync-notes.md` in the target repo and commit it with the run. Do not edit this SKILL.md.

## Rules

- Raw files are immutable after creation, and each goes in its tool and category folder, never the `raw/` root.
- Newer source wins for facts. Ambiguous contradictions are flagged `[NEEDS REVIEW]`.
- If a wiki update would remove significant content, flag it in the report instead of applying it.
- If one source is unreachable, log it, skip it, and continue. Complete the pipeline regardless.
- Chat DMs and meeting transcripts are sensitive. Extract work-relevant content only, never quote personal conversation verbatim, and mark executive-only material accordingly.
- Do not ingest sessions from your own automation.
- **Style rules are applied to new lines only.** If your repo bans certain punctuation, write new content clean from the start. Never fix it with a whole-file find-and-replace, which silently rewrites hundreds of historical lines. Check only what you added: `git diff | grep '^+' | grep -v '^+++'` piped to your character check. Sanity-check `git diff --stat` before committing. A file where you added a few lines but the diff shows hundreds of changes means a blanket replace leaked.
