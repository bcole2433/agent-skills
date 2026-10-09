# tend-vault config

Fill in the values below before the first run. The skill reads this file at the start of every run.

## Repo

| Key | Value | Notes |
|---|---|---|
| `KNOWLEDGE_REPO_PATH` | `<absolute path to your knowledge repo>` | Local checkout |
| `GIT_REMOTE` | `origin` | Remote to push to |
| `GIT_BRANCH` | `main` | Branch to pull and push |

## Layout

| Key | Value | Notes |
|---|---|---|
| `INDEX_PATH` | `index.md` | Page catalog the lint walks |
| `LOG_PATH` | `log.md` | Newest entries first |
| `SYNC_STATE_PATH` | `SYNC-STATE.md` | Last-sync dates per source |
| `WIKI_DIR` | `wiki` | Curated pages |
| `LESSONS_DIR` | `lessons` | Blank to skip lessons maintenance |
| `REPORTS_DIR` | `pending` | Where run reports are written and where recent reports are read for patterns |
| `DAILY_NOTES_DIR` | `daily` | Blank if you keep none |
| `TEMPLATES_DIR_NAME` | `_templates` | Skipped by the tag scan |
| `LINK_CONTRACT_PATH` | | Optional file describing your tag and link rules. Blank to use the defaults below |

## Thresholds

| Key | Value | Notes |
|---|---|---|
| `STALE_AFTER_DAYS` | `14` | A page older than this in an active domain is potentially stale |
| `SYNC_STALE_AFTER_DAYS` | `7` | A source not synced within this many days is flagged |
| `MAX_PAGE_LINES` | `500` | Pages above this are flagged for splitting |
| `MAX_LESSON_FILE_LINES` | `300` | Lesson files above this are flagged for splitting |
| `MIN_TAGS` | `3` | Minimum tags per file |
| `PATTERN_WINDOW_DAYS` | `7` | Window for recurring-topic detection |
| `PATTERN_MIN_MENTIONS` | `3` | Mentions inside the window that make a topic recurring |
| `LOG_WINDOW_DAYS` | `14` | How far back to read `log.md` |

## Active domains

Domains where staleness matters most: `<engineering, product>`

## Required page structure

| Key | Value | Notes |
|---|---|---|
| `REQUIRED_SECTIONS` | `Summary, Relations, Log` | Headings every wiki page must have |
| `REQUIRED_FRONTMATTER` | `type, domain, created, updated, sources, tags` | Fields every wiki page must have |

## Mode

| Key | Value | Notes |
|---|---|---|
| `SCHEDULED_AUTO_FIX` | `no` | Scheduled runs only report. Leave `no` unless you want unattended edits |
| `STYLE_RULES` | | Optional punctuation or tone rules for the report. Example: `no em dashes, no semicolons` |
| `RUN_DAY_AND_TIME` | `Fri 09:00` | Weekly, after the week's nightly syncs have landed |

## Governance files

Paths relative to the knowledge repo root. See [docs/governance.md](../../docs/governance.md).

| Key | Value | Notes |
|---|---|---|
| `CONSTITUTION_PATH` | `CONSTITUTION.md` | How the agent operates in this repo, plus current priorities |
| `WIKI_SCHEMA_PATH` | `WIKI-SCHEMA.md` | Conventions, page types, operations |
| `CONNECTIVITY_PATH` | `CONNECTIVITY.md` | Tag and WikiLink contract. Applies to every file the skill creates or edits |
| `SYNC_STATE_PATH` | `SYNC-STATE.md` | Pipeline sync state per source |
