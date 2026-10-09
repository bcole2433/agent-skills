# weekly-retro config

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
| `INDEX_PATH` | `index.md` | Page catalog |
| `LOG_PATH` | `log.md` | Newest entries first |
| `REPORTS_DIR` | `pending` | Where sync run reports live. These are the primary source |
| `DAILY_NOTES_DIR` | `daily` | Blank if you keep none |
| `PEOPLE_REGISTRY_PATH` | `people/_registry.md` | Blank to disable |
| `SYNTHESES_DIR` | `wiki/syntheses` | Where retros are written |
| `LINK_CONTRACT_PATH` | | Optional file describing your tag and link rules |
| `DOMAIN` | `<product>` | The `domain` frontmatter value for retros |

## Week definition

| Key | Value | Notes |
|---|---|---|
| `WEEK_START` | `Monday` | First day of the retro week |
| `WEEK_END` | `Friday` | Last day included |
| `WEEK_NUMBERING` | `ISO` | Page names use `YYYY-WXX` |

## Reader

| Key | Value | Notes |
|---|---|---|
| `READER_ROLE` | `<executive>` | Who reads this. Shapes how aggressively sections are cut |
| `TARGET_READ_MINUTES` | `2` | The brief should fit this |
| `INITIATIVE_TAGS` | `<launch-2026, onboarding>` | Initiative names to tag retros with when they appear that week |

## Back-link pass

| Key | Value | Notes |
|---|---|---|
| `MIN_INBOUND_LINKS` | `8` | Sanity floor for inbound links to the new retro |
| `BACKLINK_SKIP_DIRS` | `wiki/_templates, wiki/archive` | Folders that never take inbound retro links |

## Mode and style

| Key | Value | Notes |
|---|---|---|
| `SCHEDULED_REQUIRES_REVIEW` | `no` | `yes` makes even scheduled runs stop at a draft |
| `STYLE_RULES` | | Optional punctuation or tone rules. Example: `no em dashes, no semicolons` |
| `RUN_DAY_AND_TIME` | `Fri 16:00` | Weekly, after the week's syncs have landed |

## Governance files

Paths relative to the knowledge repo root. See [docs/governance.md](../../docs/governance.md).

| Key | Value | Notes |
|---|---|---|
| `CONSTITUTION_PATH` | `CONSTITUTION.md` | How the agent operates in this repo, plus current priorities |
| `WIKI_SCHEMA_PATH` | `WIKI-SCHEMA.md` | Conventions, page types, operations |
| `CONNECTIVITY_PATH` | `CONNECTIVITY.md` | Tag and WikiLink contract. Applies to every file the skill creates or edits |
