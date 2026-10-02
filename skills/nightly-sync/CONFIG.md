# nightly-sync config

Fill in the values below before the first run. The skill reads this file at the start of every run and never hardcodes ids or names.

## Repo

| Key | Value | Notes |
|---|---|---|
| `KNOWLEDGE_REPO_PATH` | `<absolute path to your knowledge repo>` | Local checkout the skill writes into |
| `GIT_REMOTE` | `origin` | Remote to push to |
| `GIT_BRANCH` | `main` | Branch to pull and push |

## Docs sources

One row per page or database. `Kind` decides how change is detected, so set it correctly.

| Name | Tool | Kind (`page` or `database`) | Id | Raw destination | Tags |
|---|---|---|---|---|---|
| `<Meeting Notes>` | notion | database | `<32 char id>` | `raw/notion/meetings/` | `meeting-notes, product` |
| `<Roadmap>` | notion | page | `<32 char id>` | `raw/notion/strategy/` | `roadmap, product` |
| | | | | | |

## Chat sources

Channel names are resolved to ids at run time. List ids only if name search is unreliable in your workspace.

| Name | Tool | Channel name | Channel id (optional) | Notes |
|---|---|---|---|---|
| `<engineering>` | slack | `engineering` | `<C0123456789>` | |
| `<product>` | slack | `product` | | |

### Direct messages

| Person | User id (optional) | Notes |
|---|---|---|
| `<Name>` | `<U0123456789>` | Work-relevant content only |

### Channels to skip

List bot-only or low-signal channels so the scan ignores them: `<alerts>, <deploys>`

## People registry

| Key | Value | Notes |
|---|---|---|
| `PEOPLE_REGISTRY_PATH` | `people/_registry.md` | Used to resolve names found in meetings and chat. Blank to disable |

## Wiki layout

| Key | Value | Notes |
|---|---|---|
| `WIKI_DOMAIN_FOLDERS` | `wiki/product, wiki/engineering, wiki/business` | Folders pages may live in. Used to verify paths before edits |
| `LESSONS_DIR` | `lessons` | Blank if you do not keep lessons |
| `DECISION_LEDGER_PATH` | `decisions/OPEN-QUESTIONS.md` | Blank if you do not keep one |
| `LINKING_CONTRACT` | `no` | Set `yes` if the repo is a linked wiki (Obsidian or similar) requiring tags and wikilinks |
| `MIN_TAGS` | `3` | Only used when `LINKING_CONTRACT` is `yes` |

## Style

| Key | Value | Notes |
|---|---|---|
| `STYLE_RULES` | | Optional punctuation or tone rules for text the skill writes. Example: `no em dashes, no semicolons` |

## Schedule

| Key | Value | Notes |
|---|---|---|
| `RUN_TIME_LOCAL` | `19:00` | Run after `claude-daily-sync` so they never write the same files at once |
