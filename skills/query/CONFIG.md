# query config

Fill in the values below before the first run.

## Layout

| Key | Value | Notes |
|---|---|---|
| `KNOWLEDGE_REPO_PATH` | `<absolute path to your knowledge repo>` | Local checkout |
| `INDEX_PATH` | `index.md` | Page catalog. Every query starts here |
| `LOG_PATH` | `log.md` | Used when a new synthesis page is created |
| `PEOPLE_REGISTRY_PATH` | `people/_registry.md` | Blank to disable |
| `RAW_DIR` | `raw` | Raw sources, read only when a page points to one |
| `SYNTHESIS_TEMPLATE_PATH` | `wiki/_templates/synthesis.md` | Template for new synthesis pages |
| `SYNTHESES_DIR` | `wiki/syntheses` | Where approved synthesis pages go |

## Limits

| Key | Value | Notes |
|---|---|---|
| `STALE_AFTER_DAYS` | `30` | Sources older than this get a stale flag when an answer depends on them |

## Style

| Key | Value | Notes |
|---|---|---|
| `STYLE_RULES` | | Optional punctuation or tone rules. Example: `no em dashes, no semicolons` |
