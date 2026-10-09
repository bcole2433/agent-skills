# claude-daily-sync config

Fill in the values below before the first run. The skill reads this file at the start of every run. Leave a value blank to use the default.

## Repo

| Key | Value | Notes |
|---|---|---|
| `KNOWLEDGE_REPO_PATH` | `<absolute path to your knowledge repo>` | Local checkout the skill writes into |
| `GIT_REMOTE` | `origin` | Remote to push to |
| `GIT_BRANCH` | `main` | Branch to pull and push |
| `CLAUDE_PROJECTS_DIR` | `~/.claude/projects` | Where the agent stores transcripts and memory |

## Session filters

| Key | Value | Notes |
|---|---|---|
| `EXCLUDE_SESSION_REGEX` | `daily[- ]sync` | Case-insensitive regex tested against session titles and opening prompts. Add the names of your own automation sessions, separated by `\|` |
| `INCLUDE_PROJECTS` | | Optional list of substrings matched against each session's working directory. Blank means every project. Example: `my-app, api-server` |

## Memory sources

| Key | Value | Notes |
|---|---|---|
| `PRIORITY_MEMORY_PROJECTS` | | Optional. Project directory names whose memory should be listed first in the snapshot, for example your global user memory and your knowledge repo's own memory |

## Optional outputs

| Key | Value | Notes |
|---|---|---|
| `WRITE_PENDING_REPORT` | `yes` | Write `pending/DATE-claude-sync.md` |
| `WRITE_LOG_ENTRY` | `yes` | Add an entry to `log.md` |
| `RUN_INGEST_PHASE` | `no` | Set `yes` if the repo has a wiki and lessons folder to update |
| `STYLE_RULES` | | Optional punctuation or tone rules to apply to text the skill writes. Example: `no em dashes, no semicolons` |

## Schedule

| Key | Value | Notes |
|---|---|---|
| `RUN_TIME_LOCAL` | `17:00` | Machine must be awake. Pick a time you are reliably at your desk |

## Governance files

Paths relative to the knowledge repo root. See [docs/governance.md](../../docs/governance.md).

| Key | Value | Notes |
|---|---|---|
| `CONSTITUTION_PATH` | `CONSTITUTION.md` | How the agent operates in this repo, plus current priorities |
| `WIKI_SCHEMA_PATH` | `WIKI-SCHEMA.md` | Conventions, page types, operations |
| `CONNECTIVITY_PATH` | `CONNECTIVITY.md` | Tag and WikiLink contract. Applies to every file the skill creates or edits |
| `SYNC_STATE_PATH` | `SYNC-STATE.md` | Pipeline sync state per source |

## Lessons

| Key | Value | Notes |
|---|---|---|
| `LESSONS_DIR` | `lessons` | Relative to the knowledge repo root. Holds `index.md` and one file per skill |
