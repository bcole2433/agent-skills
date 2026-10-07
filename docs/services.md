# Swapping services

The skills are written against capabilities, not products. "Docs tool" means wherever your team writes pages. "Chat" means wherever it talks. The examples in the skills use Notion, Slack and PostHog because those are common. Nothing in the method depends on them.

## How a swap works

1. Open the skill's `CONFIG.md`.
2. Change the `Tool` column or key for that source to your service's name.
3. Give the agent a way to read it: a CLI on your `PATH`, or an MCP server connected to your Claude session.
4. Replace the example commands in the skill's SKILL.md with your service's equivalents, or add a line to `CONFIG.md` telling the agent which commands to use.

The skills never hardcode ids. They read them from `CONFIG.md`, so changing a service rarely means changing the method.

## Capability map

| Capability | Used by | Examples in the skills | Other options |
|---|---|---|---|
| Docs and databases | `nightly-sync`, `ingest`, `whats-new-weekly` | Notion (`ntn` CLI) | Confluence, Google Docs, Coda, Obsidian or any folder of markdown, GitHub wiki |
| Chat | `nightly-sync`, `whats-new-weekly` (announce) | Slack | Microsoft Teams, Discord, Mattermost, email digests |
| Analytics | `whats-new-weekly` (impact) | PostHog | Amplitude, Mixpanel, GA4, any SQL warehouse |
| Code host | `whats-new-weekly` | GitHub (`gh` CLI) | GitLab (`glab`), Bitbucket, plain `git` only |
| Publish target | `whats-new-weekly` | Notion | Confluence, Google Docs, a static site, a Slack canvas, a markdown file in a repo |
| Scheduler | all routines | Claude desktop scheduled tasks | cron, launchd, GitHub Actions, any cloud routine |
| Browser capture | `whats-new-weekly` (screenshots) | A browser CLI | Playwright, Puppeteer, any tool that saves a PNG |
| Knowledge repo | all | A git repo of markdown | Any git host |

If you do not use a capability, skip it. Leave its `CONFIG.md` rows as `<placeholder>` and the skill logs it and moves on. Examples: set `ANALYTICS_ENABLED` to `no` and the impact section disappears, set `SCREENSHOTS_ENABLED` to `no` and the screenshot phase is skipped, leave the announce channel blank and nothing is posted.

## Reading from a different docs or chat service

`nightly-sync` and `ingest` need one thing from a source: **what changed since a timestamp, and the content of it.** Any service that can answer those two questions works.

Add your source to the `nightly-sync` `CONFIG.md` table with a `Kind` of `page`, `database` or `channel`, then tell the agent how to read it. A short note in `CONFIG.md` is enough:

```markdown
## Reading my sources

| Tool | Check for changes | Fetch content |
|---|---|---|
| confluence | `GET /rest/api/content?orderby=lastmodified` | `GET /rest/api/content/<id>?expand=body.storage` |
| teams | Graph API `messages?$filter=lastModifiedDateTime gt <ts>` | same call |
```

Rules that apply to every service:

- A container's own "last edited" timestamp is not proof its children are unchanged. Check the newest child.
- Compute timestamps with a script, never by hand.
- A missing CLI or an auth error means "unavailable". Log it, skip that source, and finish the run.
- Raw snapshots are written once and never edited.

## Publisher contract (`whats-new-weekly`)

The bundled `scripts/publish_page.py` publishes to Notion. To publish somewhere else, write your own script and set `PUBLISHER` in the skill's `CONFIG.md`. It must:

| Requirement | Detail |
|---|---|
| Inputs | `--draft <file>` (markdown with `title` and optional `tags` frontmatter) and `--images-dir <dir>` |
| Image placeholders | A line `{{IMAGE: file.png \| optional caption}}` marks where an image goes. Resolve filenames inside `--images-dir` only and reject anything that escapes it |
| Success output | The last two stdout lines are `PAGE_URL=<url>` and `PAGE_ID=<id>` |
| Failure | Print `ERROR: <reason>` to stderr and exit non-zero |
| Dry run | Optional `--dry-run` that prints the plan and calls nothing |

A minimal publisher can be a dozen lines that copy the draft into a repo folder and print its path as `PAGE_URL`.

## Analytics contract (`whats-new-weekly`)

Impact analysis needs only a way to run a query and a list of known-healthy events. Set `ANALYTICS_TOOL` to your tool, point `ANALYTICS_BASELINES_PATH` at a file of events and their normal values, and tell the agent how to query in `CONFIG.md`. The method in `references/impact-method.md` is tool-neutral: the four-part causation bar, the comparison window, and the confounder checklist.

## Checklist before your first run

- The CLI or MCP server for each service you kept is installed and authenticated. Test with one real read.
- Every `<placeholder>` you care about is filled in.
- Every service you do not use is turned off or left blank.
- Secrets are in your secret store or CLI credential store, never in `CONFIG.md`.
