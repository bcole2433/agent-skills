---
name: whats-new-weekly
description: Weekly "What's New" post for a non-technical audience. Collects what reached production in the last 7 days across your repos, adds context from meeting notes and chat, checks analytics for the impact of recent launches, captures optional web screenshots, and publishes a release-announcement page to Notion
---

## Purpose and audience

This skill produces a weekly page for people who do not write code. It reads like a product release announcement: a headline, an optional header image, and a short description per item, written so a teammate on the business side understands what changed and why they should care. No technical language, no repo names, no PR numbers, and no framework words ever reach the published page. See `references/voice.md`.

## Config

Read `CONFIG.md` beside this file first. It holds the repo list, the Notion ids, the voice rules, the analytics settings, the model roles, and the caps. If a required value is still a `<placeholder>`, log it and skip the part that needs it. A missing Notion id stops the run before publishing.

## Governance

Before writing any file, load the governance files named in `CONFIG.md` (`CONSTITUTION_PATH`, `WIKI_SCHEMA_PATH`, `CONNECTIVITY_PATH`). Follow `CONSTITUTION_PATH` for operating rules and priorities, `WIKI_SCHEMA_PATH` for page types and conventions, and `CONNECTIVITY_PATH` for the tag and WikiLink contract on every file you create or edit. If a file is missing, say so and continue with the skill's own rules.

## Model and concurrency rule

Run the orchestrator on `ORCHESTRATOR_MODEL`. Dispatch research, collection, screenshot and drafting-support work to subagents on `WORKER_MODEL`, never more than `MAX_PARALLEL_AGENTS` at once. The orchestrator keeps feature selection, the final copy, the causation judgment in the impact section, the screenshot decision, and publishing.

Handoffs must be self-contained, because subagents cannot see the conversation: paths, window dates, the exact output file, and the line "write only the one output file named here, do not edit this skill, its references, or its scripts". Before the commit, read the staged diff and revert anything outside `STATE_DIR`, `REPORTS_DIR` and the log that the run did not deliberately make. Another session may be editing the skill at the same time.

## Token budget

This runs unattended every week, so it reads excerpts and never raw sources.

- The orchestrator reads only this file, `references/voice.md`, the "Draft file format" section of `references/notion-publishing.md`, the three Phase 1 output files, and the collector's summary lines. It never opens `shipped.json`, raw files, or full analytics reports. To check a fact, grep the JSON for the PR number.
- Subagents read the digest files named in their handoff and open a raw source only when a specific bullet needs verifying (context agent at most 3 raw files, shipped-changes agent at most 8 `gh pr view` calls, impact agent at most `MAX_ANALYTICS_QUERIES` queries).
- Output caps in the handoff: candidates at most 40 entries of 4 lines each, context and impact at most 60 lines each, each subagent's final message at most 15 lines. The file is the deliverable.
- No screenshots return to the model. The screenshot agent saves PNGs to disk and Reads each final PNG once.
- Publish verification pipes through `head -c 3000`.

## Local-only check and window

This skill needs local repo checkouts, `gh`, `ntn`, and optionally your analytics CLI and browser CLI. Before anything else, confirm the first repo's `local_path` exists and `ntn doctor < /dev/null` passes. If not, log "not a local environment, skipping" and stop without writing. Then `git pull --rebase origin main`.

**Window:** rolling `WINDOW_DAYS` ending at run time. Compute both timestamps with a script, never by hand, and record them in the run directory. The page title uses the most recent Monday on or before the run date.

## Run state (lives in the repo, never in this file)

- `STATE_DIR/published.md`: append-only log of every published page (date, window, Notion URL, features named and their PR sources). The source for "previous 3 weeks".
- `STATE_DIR/impact-tracking.md`: one row per published feature with the metrics that should move, the baseline, and a status (`watching`, `signal`, `no signal`, `retired`).
- `STATE_DIR/lessons.md`: dated run quirks, data gotchas, and copy feedback. Permanent method fixes go in this file or a reference.
- `STATE_DIR/runs/YYYY-MM-DD/`: `shipped.json`, `shipped.md`, `candidates.md`, `context.md`, `impact.md`, `draft.md`, `screenshots/`, `publish.log`. Committed.

## Phase 1: Collect (three worker agents in parallel)

First the orchestrator runs the collector with `--since` set `COLLECTOR_LOOKBACK_DAYS` back:

```bash
python3 skills/whats-new-weekly/scripts/collect_shipped.py \
  --config skills/whats-new-weekly/CONFIG.md \
  --since <ISO> --until <ISO> --out STATE_DIR/runs/<date>/shipped.json
```

It writes `shipped.md` beside the JSON: candidate PRs, internal PRs as titles only, and not-yet-shipped titles. Agents read the `.md`, the JSON is the audit trail. See `references/repos.md` for how it decides what shipped. Then dispatch these three agents in one message:

- **Agent A, shipped-changes reader.** Reads `shipped.md` only. Drops any PR number already in `published.md`. Uses `gh pr view <n> -R <repo> --json title,body` at most 8 times, only for an ambiguous title with no changelog text, and never reads diffs. Writes `candidates.md`: one entry per user-visible or staff-relevant change with a plain-language name, what a person can now do, the surface, repo and PR numbers (orchestrator only), a confidence that it is live in production, and a category of `feature`, `staff-benefit`, `significant-fix` or `internal`. Backend changes count only when they power something visible or staff should know about them. Speed work, refactors, tooling, dependency bumps, CI, and small fixes are `internal`. A fix is `significant-fix` only when other teams were affected or asked about it.
- **Agent B, context reader.** Reads the recent files in the context directories from `CONFIG.md` (meeting notes, chat, session digests), at most `CONTEXT_FILES_MAX` in full. Writes `context.md`: what people said shipped or was celebrated, requests from other teams that a shipped change answers (name the team and the ask, never quote customer or user PII), launch names or marketing terms staff already use (use their words), anything shipped but embargoed, and upcoming items people are waiting on. Cite the source file per bullet.
- **Agent C, impact analyst.** Skip if `ANALYTICS_ENABLED` is `no` or there are no tracked features. Reads the last 3 entries of `published.md`, `impact-tracking.md`, the analytics baselines, and the analytics digest if configured. Greps the lessons file for confounder names instead of reading it. Uses the analytics CLI per `references/impact-method.md` only where those do not answer the question. Writes `impact.md`: per tracked feature the metric, before and after with the windows, confounders, and a verdict of `attributable`, `moved but not attributable`, or `no movement` with a one-line reason. Also proposes watch metrics for this week's candidates.

## Phase 2: Select and write (orchestrator)

Read the three outputs. Pick `MIN_ITEMS` to `MAX_ITEMS`. Anything the collector lists as merged but not yet in production is not shipped and never appears as a launch. At most it feeds a "Coming up" line. Order: biggest user-facing launch first, then staff-benefit items, then significant fixes. Merge one feature landing across web, iOS and Android into one item. Drop anything marked embargoed. Write `draft.md` in the publisher's format (`references/notion-publishing.md`), following `references/voice.md` exactly.

Page sections:
- Headline paragraph, 2 sentences, the week's theme.
- One block per item: plain-language title, then the image placeholder directly under the title if the item earned a screenshot, then 2 to 3 sentences on what changed and why staff should care, then a "Try it" link for web features. The image sits between title and description, never after the text.
- "For the team", internal-benefit items, 1 to 2 sentences each.
- "Impact from recent launches", from `impact.md`. Only `attributable` items are stated as results. `moved but not attributable` is phrased as early signal with the caveat named. `no movement` is left out unless the launch was major and staff will ask.
- A one-line "Coming up" only if the context agent found something safe to preview.

No page exceeds `MAX_IMAGES`. No PR numbers, repo names, commit language, or engineering terms in the body.

## Phase 3: Screenshots (one worker agent, web only)

Skip if `SCREENSHOTS_ENABLED` is `no`. Decide which items earn a screenshot (at most `MAX_IMAGES` total and `MAX_IMAGES_PER_FEATURE` per feature, preferring the headline launch). Mobile app screenshots are out of scope. Hand off per `references/screenshots.md`: exact production URL, the feature element to frame (not the page), file name, output dir. A missing screenshot never blocks publishing. Remove the placeholder and continue.

## Phase 4: Publish (orchestrator)

```bash
python3 <PUBLISHER> \
  --draft STATE_DIR/runs/<date>/draft.md \
  --images-dir STATE_DIR/runs/<date>/screenshots \
  --data-source <NOTION_DATA_SOURCE_ID> \
  --cover <first image if any> | tee STATE_DIR/runs/<date>/publish.log
```

Verify with `ntn pages get <id> < /dev/null | head -c 3000` that the title, first heading and an image block landed. Publish directly, no draft status.

`<PUBLISHER>` is the script named in `CONFIG.md`. Any publisher must accept `--draft` and `--images-dir` and print `PAGE_URL=<url>` and `PAGE_ID=<id>` as its last two stdout lines. The bundled one also takes `--data-source` and `--cover` (Notion). Verify the page with your service's own read command. The `ntn` command shown is the Notion one.

### Announce (optional)

If `SLACK_ANNOUNCE_CHANNEL_ID` is set, post one message after verification using your chat connector, written for the same audience and following the voice guide. Use standard markdown, the tool converts it.

```
**<page title>**
<the headline paragraph, 2 sentences>
- <item 1 title>
- <item 2 title>

Full post with screenshots: [<page title>](<Notion URL>)
```

List only launch titles. Never paste the whole page and never include PR numbers, repo names or PII. If the send fails, log "announce failed" in `publish.log`, note it in the report, and do not retry. The Notion page is the deliverable.

## Phase 5: Record (orchestrator)

1. Append to `published.md`, including the announce result.
2. Update `impact-tracking.md`. New features get `watching` with the proposed metrics, older rows get verdicts, and rows older than `RETIRE_AFTER_WEEKS` with no signal get `retired`.
3. Write the run report in `REPORTS_DIR` with frontmatter, the Notion URL, what was included, what was deliberately left out and why, and decisions needed.
4. Add a log entry above the newest one.
5. Add a `lessons.md` entry only if something was learned.
6. Commit everything as one commit and push (`git pull --rebase` first, retry once on conflict). In a git worktree whose branch is not `main`, push `HEAD:main`.

## Rules

- Never include PII from chat or user feedback.
- Never announce something not confirmed in production. Low-confidence candidates are held to next week and noted in the report.
- If nothing shipped, still publish a short page saying so with the impact section. Staff expect the cadence.
- The first run has empty `published.md` and `impact-tracking.md`. Skip the impact section and only propose watch metrics.
- If `ntn` or `gh` fail, stop before publishing and write the report with the failure.
- If the announce fails, record it and finish Phase 5.
- Other pipelines may share the repo. Keep writes under `STATE_DIR`, `REPORTS_DIR` and the log, commit once at the end, and rebase before pushing.
- Never solve a CAPTCHA, submit a form other than sign-in, or use credentials other than the QA account.

## References

- `references/repos.md`: how the collector decides what shipped and the digest format.
- `references/notion-publishing.md`: draft file format, how the publisher maps it to Notion, and `ntn` gotchas.
- `references/voice.md`: the style guide every page follows.
- `references/impact-method.md`: the causation bar the impact agent uses.
- `references/screenshots.md`: the screenshot agent's method.
