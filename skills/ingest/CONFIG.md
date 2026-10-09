# ingest config

Fill in the values below before the first run.

## Layout

| Key | Value | Notes |
|---|---|---|
| `KNOWLEDGE_REPO_PATH` | `<absolute path to your knowledge repo>` | Local checkout |
| `CONSTITUTION_PATH` | `CONSTITUTION.md` | Operating principles. Blank if you have none |
| `SCHEMA_PATH` | `WIKI-SCHEMA.md` | Page conventions. Blank if you have none |
| `INDEX_PATH` | `index.md` | Page catalog |
| `LOG_PATH` | `log.md` | Newest entries first |
| `SYNC_STATE_PATH` | `SYNC-STATE.md` | Last-sync timestamps |
| `RAW_DIR` | `raw` | Raw snapshots |
| `REPORTS_DIR` | `pending` | Run reports |
| `TEMPLATES_DIR` | `wiki/_templates` | Page templates |
| `PEOPLE_REGISTRY_PATH` | `people/_registry.md` | Blank to disable |

## Sources

| Key | Value | Notes |
|---|---|---|
| `SOURCES_CONFIG_PATH` | `skills/nightly-sync/CONFIG.md` | Where the docs sources, ids and kinds are defined. Reuse the nightly-sync file so ids live in one place |

## Raw category map

Where a fetched source is filed under `RAW_DIR`.

| Source type | Folder | Default tags |
|---|---|---|
| `<meeting notes>` | `raw/<tool>/meeting-notes/` | `source, meeting-notes` |
| `<strategy page>` | `raw/<tool>/strategy/` | `source, strategy` |
| `<epics or project database>` | `raw/<tool>/epics/` | `source, epics` |

## Style

| Key | Value | Notes |
|---|---|---|
| `STYLE_RULES` | | Optional punctuation or tone rules. Example: `no em dashes, no semicolons` |

## Governance files

Paths relative to the knowledge repo root. See [docs/governance.md](../../docs/governance.md).

| Key | Value | Notes |
|---|---|---|
| `CONSTITUTION_PATH` | `CONSTITUTION.md` | How the agent operates in this repo, plus current priorities |
| `WIKI_SCHEMA_PATH` | `WIKI-SCHEMA.md` | Conventions, page types, operations |
| `CONNECTIVITY_PATH` | `CONNECTIVITY.md` | Tag and WikiLink contract. Applies to every file the skill creates or edits |
| `SYNC_STATE_PATH` | `SYNC-STATE.md` | Pipeline sync state per source |
