# whats-new-weekly config

Fill in the values below before the first run. The skill reads this file at the start of every run. Anything left as a `<placeholder>` makes the skill log it and skip that part.

## Product and audience

| Key | Value | Notes |
|---|---|---|
| `PRODUCT_NAME` | `<Acme>` | Used in the page title and Slack message |
| `AUDIENCE` | `<non-technical staff in sales, marketing and support>` | Who reads the page. Shapes every sentence |
| `PAGE_TITLE_TEMPLATE` | `What's New in <Product>: Week of {Mon DD}` | `{Mon DD}` is the most recent Monday on or before the run date |
| `WINDOW_DAYS` | `7` | Rolling window ending at run time |
| `COLLECTOR_LOOKBACK_DAYS` | `9` | Collector runs wider than the window so a release between two runs is never missed. Items already in `published.md` are dropped |
| `MIN_ITEMS` | `3` | Items per page |
| `MAX_ITEMS` | `6` | Items per page |
| `MAX_IMAGES` | `3` | Hard cap per page |
| `MAX_IMAGES_PER_FEATURE` | `2` | |

## Repos

Edit the JSON block below. The collector script reads it directly, so keep it valid JSON. Every key except `name`, `github` and `local_path` is optional.

```json
{
  "production_branch": "production",
  "integration_branch": "develop",
  "release_train_titles": ["staging", "develop", "production"],
  "release_train_legs": [["staging", "develop"], ["production", "staging"], ["production", "develop"]],
  "internal_title_keywords": ["changelog sync", "bump", "lint", "prettier", "eslint"],
  "internal_labels": ["dependencies", "chore", "internal", "ci"],
  "internal_authors": ["dependabot[bot]", "dependabot"],
  "repos": [
    {
      "name": "web-app",
      "github": "<org>/<web-app>",
      "local_path": "~/code/web-app",
      "production_url": "https://www.example.com",
      "display_name": "The website",
      "surface": "web",
      "has_changelog_file": true
    },
    {
      "name": "ios-app",
      "github": "<org>/<ios-app>",
      "local_path": "~/code/ios-app",
      "surface": "ios",
      "display_name": "The app",
      "releases_only": true
    },
    {
      "name": "api",
      "github": "<org>/<api>",
      "local_path": "~/code/api",
      "surface": "backend"
    }
  ]
}
```

How each field is used:

| Field | Meaning |
|---|---|
| `production_branch` | Branch whose merge commits are the release trains. A feature shipped when it lands here, not when its PR merged to the integration branch |
| `integration_branch` | Where feature PRs merge first. Used to list "merged, not yet shipped" items |
| `release_train_titles` and `release_train_legs` | How to recognize mechanical sync PRs so they are not mistaken for features |
| `internal_*` | Heuristics that collapse chores, bumps and bot PRs to a title-only line |
| `releases_only` (per repo) | The repo ships by GitHub Release instead of a production branch. Releases are read with `gh api` |
| `has_changelog_file` (per repo) | The repo keeps a `CHANGELOG.md` the collector can cross-check |
| `surface` | `web`, `ios`, `android` or `backend`. Backend changes only count when they power something visible |

## Where context lives

Sources the context agent reads, with caps. Leave a row blank to skip it.

| Key | Value | Notes |
|---|---|---|
| `MEETING_NOTES_DIR` | `raw/notion/meeting-notes` | Recent meeting notes |
| `CHAT_DIR` | `raw/slack` | Recent chat digests |
| `SESSIONS_DIR` | `raw/claude/sessions` | Recent AI session digests |
| `CONTEXT_FILES_MAX` | `10` | Most files the context agent may open in full |

## Impact tracking

| Key | Value | Notes |
|---|---|---|
| `ANALYTICS_ENABLED` | `yes` | `no` skips the impact section entirely |
| `ANALYTICS_TOOL` | `posthog` | Any tool the agent can query by CLI or MCP |
| `ANALYTICS_PROJECT_ID` | `<project id>` | |
| `ANALYTICS_BASELINES_PATH` | `analytics/baselines.md` | Known-healthy metrics and their baselines. Blank if none |
| `ANALYTICS_LESSONS_PATH` | `analytics/lessons.md` | Known confounders and data gotchas. Blank if none |
| `ANALYTICS_DIGEST_PATH` | | Latest analytics digest, read as text. Blank if none |
| `MAX_ANALYTICS_QUERIES` | `3` | Hard cap per run |
| `COMPARE_WINDOW_DAYS` | `7` | Days after launch versus the same number before |
| `RETIRE_AFTER_WEEKS` | `6` | A row with no signal after this long is retired |
| `CONFOUNDERS` | `<peak-traffic days, seasonal changes, marketing sends, outages, app release lag>` | Named events that can fake or hide a lift. The impact agent checks each against the launch dates |

## Publishing

The Notion rows below apply only to the bundled publisher. Skip them if you use your own.

| Key | Value | Notes |
|---|---|---|
| `PUBLISHER` | `scripts/publish_page.py` | Script that publishes the draft. The bundled one targets Notion. To use another service, point this at your own script that follows the publisher contract in `docs/services.md` |
| `NOTION_DATABASE_ID` | `<database id>` | The database that holds one page per week |
| `NOTION_DATA_SOURCE_ID` | `<data source id>` | Pages are created under this, not the database id. Resolve it with `ntn api v1/databases/<id>` |
| `NOTION_TITLE_PROPERTY` | `Name` | |
| `NOTION_TAGS_PROPERTY` | `Tags` | A multi-select property |
| `TAG_VOCABULARY` | `Web, iOS, Android, Backend` | Tags used on pages. New names are created on demand |

## Announce (optional)

| Key | Value | Notes |
|---|---|---|
| `SLACK_ANNOUNCE_CHANNEL_ID` | `<C0123456789>` | Blank to skip the announcement |

## Voice

| Key | Value | Notes |
|---|---|---|
| `BANNED_WORDS` | `API, endpoint, refactor, PR, merge, deploy, backend, frontend, component, cache, latency, schema, migration, repo, commit, sprint, ticket` | Never appear on the page. Add your framework and library names |
| `STYLE_RULES` | | Optional punctuation rules. Example: `no em dashes, no semicolons` |

### Substitution table

Map internal names to the words your audience uses.

| Internal name | Say instead |
|---|---|
| `web-app` | `<the website>` |
| `ios-app` | `<the app>` |
| `caching work` | `faster loading` |
| `auth` | `sign-in` |
| `deploy, ship, merge` | `went live, is now live` |

### "Try it" links

| Surface | Link |
|---|---|
| `web-app` | `https://www.example.com` |
| mobile apps | No link. Say "Open the app to see it" |

## Screenshots (optional, web only)

| Key | Value | Notes |
|---|---|---|
| `SCREENSHOTS_ENABLED` | `yes` | `no` skips Phase 3 |
| `BROWSER_CLI` | `<path to your headless or headed browser CLI>` | Anything that can navigate, snapshot and save a PNG to disk |
| `DEFAULT_VIEWPORT` | `375x812` | Mobile by default. Name desktop only for a feature with no mobile view |
| `QA_ACCOUNT_LOGIN` | `<test account login>` | A fake account for QA only. Never a real user. Keep real credentials out of this file and use your secret store |
| `QA_ACCOUNT_SECRET_SOURCE` | `<where the agent gets the code or password>` | Name the source, not the value |

## Models

| Key | Value | Notes |
|---|---|---|
| `ORCHESTRATOR_MODEL` | `<your strongest model>` | Feature selection, final copy, causation judgment, screenshot decision, publishing |
| `WORKER_MODEL` | `<a cheaper model>` | Research, collection and drafting support |
| `MAX_PARALLEL_AGENTS` | `3` | |

## Run state files

| Key | Value | Notes |
|---|---|---|
| `STATE_DIR` | `whats-new` | Holds `published.md`, `impact-tracking.md`, `lessons.md` and `runs/` |
| `LOG_PATH` | `log.md` | |
| `REPORTS_DIR` | `pending` | |
| `GIT_REMOTE` | `origin` | |
| `GIT_BRANCH` | `main` | |
| `RUN_DAY_AND_TIME` | `Mon 18:00` | Local machine, awake |

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
