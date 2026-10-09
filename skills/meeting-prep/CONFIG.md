# meeting-prep config

Fill in the values below before the first run.

## Layout

| Key | Value | Notes |
|---|---|---|
| `KNOWLEDGE_REPO_PATH` | `<absolute path to your knowledge repo>` | Local checkout |
| `INDEX_PATH` | `index.md` | Page catalog |
| `PEOPLE_REGISTRY_PATH` | `people/_registry.md` | Names and roles. Blank to skip attendee lookup |
| `MEETING_NOTES_DIR` | `raw/notion/meeting-notes` | Where raw meeting notes live |

## Status trackers

Pages that hold current status. The skill reads these for items the meeting topic touches.

| Name | Path | What it tracks |
|---|---|---|
| `<Engineering Epics>` | `<wiki/engineering/Engineering-Epics.md>` | Epic status |
| `<Roadmap>` | `<wiki/product/Roadmap.md>` | Roadmap items |

## Limits

| Key | Value | Notes |
|---|---|---|
| `LOOKBACK_DAYS` | `14` | How far back to read raw meeting notes |
| `STALE_AFTER_DAYS` | `14` | Pages not updated within this window get a stale flag |
| `MAX_BRIEFING_LINES` | `40` | Keep it to one screenful |

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
