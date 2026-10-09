# decision config

Fill in the values below before the first run.

## Layout

| Key | Value | Notes |
|---|---|---|
| `KNOWLEDGE_REPO_PATH` | `<absolute path to your knowledge repo>` | Local checkout |
| `INDEX_PATH` | `index.md` | Page catalog |
| `LOG_PATH` | `log.md` | Newest entries first |
| `DECISIONS_DIR` | `decisions` | Where decision files are written |
| `DECISION_LEDGER_PATH` | `decisions/OPEN-QUESTIONS.md` | Open questions ledger. Blank if you keep none |
| `PEOPLE_REGISTRY_PATH` | `people/_registry.md` | Used to resolve `decided_by`. Blank to disable |

## Vocabulary

| Key | Value | Notes |
|---|---|---|
| `ALLOWED_STATUSES` | `decided, revisit, reversed` | Values for the `status` field |
| `DOMAINS` | `<engineering, product, business, marketing>` | Allowed values for `domain` |
| `DEFAULT_TAGS` | `decision` | Tags added to every decision file |

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

## Lessons

| Key | Value | Notes |
|---|---|---|
| `LESSONS_DIR` | `lessons` | Relative to the knowledge repo root. Holds `index.md` and one file per skill |
