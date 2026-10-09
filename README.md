# agent-skills

Skills and routines for agents that turn a git repo of markdown into a self-maintaining team knowledge base. They are codebase-agnostic and service-agnostic. Use the whole set, or copy one skill.

- **Skills** are reusable instructions an agent loads when a task matches. Each lives in `skills/<name>/SKILL.md` with a `CONFIG.md` and any helper scripts beside it.
- **Routines** are scheduled prompts that run a skill on a cadence. Each lives in `routines/<name>.md`.
- **Services** (Notion, Slack, PostHog and so on) are replaceable. See [docs/services.md](docs/services.md).

## What is in here

| Skill | Routine | What it does |
|---|---|---|
| [claude-daily-sync](skills/claude-daily-sync/SKILL.md) | [claude-daily-sync](routines/claude-daily-sync.md) | Snapshots agent memory files and session transcripts into a git repo so cloud agents can read data that only exists on your machine |
| [nightly-sync](skills/nightly-sync/SKILL.md) | [nightly-sync](routines/nightly-sync.md) | Pulls changed pages, databases and chat from your work tools into a repo as immutable snapshots, folds the signal into a wiki, and writes a review report |
| [tend-vault](skills/tend-vault/SKILL.md) | [tend-vault](routines/tend-vault.md) | Weekly health check: contradictions, orphans, staleness, tag coverage, patterns, and a prioritized report |
| [weekly-retro](skills/weekly-retro/SKILL.md) | [weekly-retro](routines/weekly-retro.md) | Weekly executive brief from the week's run reports, with a mandatory back-link pass |
| [whats-new-weekly](skills/whats-new-weekly/SKILL.md) | [whats-new-weekly](routines/whats-new-weekly.md) | Weekly release announcement for non-technical readers, from what reached production plus analytics impact |
| [meeting-prep](skills/meeting-prep/SKILL.md) | on demand | One-screen pre-meeting briefing built from what the wiki already knows |
| [decision](skills/decision/SKILL.md) | on demand | Logs a decision with rationale and alternatives, then cross-links it from affected pages |
| [query](skills/query/SKILL.md) | on demand | Answers a question from the wiki with citations, a confidence rating, and named gaps |
| [ingest](skills/ingest/SKILL.md) | on demand | Manually ingests a file, URL or all sources into the wiki |

## How the pieces fit

```
your machine                      knowledge repo (git)                 readers
------------                      --------------------                 -------
claude-daily-sync  ─────────────▶ raw/claude/...   ┐
nightly-sync (docs, chat) ──────▶ raw/<tool>/...   ├─▶ wiki/ lessons/ decisions/
                                  pending/ reports ┘        │
tend-vault   ──▶ health report                              ├─▶ weekly-retro (brief)
whats-new-weekly (repos + analytics) ──▶ published page     └─▶ query, meeting-prep
decision, ingest ──▶ write into the repo
```

1. **Capture** into raw, immutable snapshots: `claude-daily-sync`, `nightly-sync`, `ingest`.
2. **Curate** into wiki pages, lessons and decisions: the ingest phase of the same skills, plus `decision`.
3. **Maintain**: `tend-vault` audits the repo weekly.
4. **Synthesize**: `weekly-retro` and `whats-new-weekly` turn a week of material into a short page.
5. **Use**: `query` and `meeting-prep` answer questions from what the repo knows.

The skills share one convention: **the skill file is method only.** Anything that changes run to run (timestamps, counts, gotchas) lives in files in your knowledge repo, never in the skill.

All skills also load the repo's governance files (constitution, schema, connectivity contract) before writing. See [docs/governance.md](docs/governance.md).

## What you need

| Need | Why | Required for |
|---|---|---|
| An agent that supports skills | Runs the skills | Everything |
| A git repo for your knowledge base, with a remote | Where all output lands | Everything |
| `git`, `python3` | Helper scripts and commits | Everything |
| Access to your docs tool and chat (CLI or MCP) | Source material | `nightly-sync`, `ingest` |
| `gh` (GitHub CLI) and local clones of your product repos | Detect what shipped | `whats-new-weekly` |
| An analytics tool with a CLI or MCP | Impact section | `whats-new-weekly` (optional) |
| A browser CLI that saves PNGs | Screenshots | `whats-new-weekly` (optional) |
| A machine that is awake at the scheduled time | Local routines | `claude-daily-sync`, `whats-new-weekly` |

You do not need all of it. Pick the skills you want and skip the rest.

## Quick start

1. **Create the knowledge repo.** Any git repo works. The skills expect these folders and create them when missing:

   ```
   raw/            immutable snapshots (raw/claude/, raw/<tool>/)
   wiki/           curated pages
   lessons/        durable lessons learned (router pattern): index.md plus one file per skill
   decisions/      optional, decision files and an open-questions ledger
   people/         optional, a _registry.md of names and roles
   pending/        run reports
   index.md        page catalog
   log.md          newest entry first
   SYNC-STATE.md   last-sync timestamps per source
   ```

2. **Copy the skills you want** into the knowledge repo:

   ```bash
   mkdir -p .claude/skills
   cp -R path/to/agent-skills/skills/nightly-sync .claude/skills/
   ```

   Use `~/.claude/skills/` instead to make a skill available in every project. The agent finds each one by the `name` and `description` in its frontmatter.

3. **Fill in `CONFIG.md`** in each skill folder. This is the one file you edit. See [Configuring a skill](#configuring-a-skill).

4. **Run it once by hand** from the knowledge repo, in your agent, before scheduling it. For example: "run the nightly-sync skill". Fix whatever the first run surfaces.

5. **Schedule it.** Copy the prompt from the skill's file in `routines/` into a scheduled task. See [Scheduling](#scheduling).

## Configuring a skill

Every skill folder has a `CONFIG.md`. It holds the constants a skill needs: repo paths, ids, channel names, thresholds, style rules, and which services to use. Skills read it at the start of every run and never hardcode these values.

- Replace every `<placeholder>` you want to use.
- Anything left as a placeholder makes the skill log it and skip that part. It never guesses.
- Leave optional rows blank to turn a feature off.
- Keep secrets out of it. Use your CLI's credential store or a secret manager and name the source, not the value.

| Skill | The main things to fill in |
|---|---|
| `claude-daily-sync` | Repo path, session exclude regex, project filters |
| `nightly-sync` | Docs sources (id, kind, destination), chat channels, DMs, wiki folders, linking rules |
| `tend-vault` | Layout paths, staleness and size thresholds, required page sections |
| `weekly-retro` | Layout paths, week definition, reader role, back-link minimum |
| `whats-new-weekly` | Repo list (JSON block), publish target, voice rules and banned words, analytics settings, models |
| `meeting-prep` | Layout paths, status tracker pages, look-back window |
| `decision` | Decisions folder, allowed statuses and domains |
| `query` | Index, templates, staleness window |
| `ingest` | Layout paths, raw category map, pointer to the nightly-sync sources |

## Using different services

Nothing here requires Notion, Slack or PostHog. They are examples. To use something else:

1. Set the tool name in the skill's `CONFIG.md`.
2. Make sure the agent can reach it through a CLI on your `PATH` or a connected MCP server.
3. Tell the agent how to read from it, in a short table in `CONFIG.md`.

Not using a capability at all? Turn it off. Examples: `ANALYTICS_ENABLED=no`, `SCREENSHOTS_ENABLED=no`, a blank announce channel, or no chat sources in `nightly-sync`.

The full capability map, the publisher contract for `whats-new-weekly`, and a first-run checklist are in [docs/services.md](docs/services.md).

| If you use | Do this |
|---|---|
| Confluence or Google Docs instead of Notion | Add your sources to the `nightly-sync` config with your tool name and describe how to list changes and fetch content |
| Teams or Discord instead of Slack | Same, with `Kind` set to `channel` |
| GitLab instead of GitHub | Swap `gh` for `glab` in the `whats-new-weekly` collector commands |
| Amplitude or a warehouse instead of PostHog | Set `ANALYTICS_TOOL` and describe how to query |
| Publishing to Confluence or a static site | Write a publisher script that follows the contract and set `PUBLISHER` |
| Plain markdown with no docs tool | Use `ingest` on files under `raw/` and skip the docs sources |

## Scheduling

A routine is a short prompt that points at a skill. The skill holds the method, the routine holds where, when and under what conditions.

- **Desktop agent scheduled tasks.** Copy the routine prompt to `~/.claude/scheduled-tasks/<name>/SKILL.md` and set the schedule in the UI. The machine must be awake. This is the only option for routines that read `~/.claude/projects` or local repo clones.
- **Cloud routines.** Create a routine with the same prompt and attach the repo and connectors. Good for `nightly-sync`, `tend-vault` and `weekly-retro`, which need only the repo and read access to your tools.
- **cron, launchd or CI.** Run `claude -p "<routine prompt>"` from the knowledge repo on a schedule.

Suggested order so routines never write the same files at once:

| Time | Routine | Where |
|---|---|---|
| Late afternoon, daily | `claude-daily-sync` | Local |
| Evening, daily | `nightly-sync` | Local or cloud |
| Early week | `whats-new-weekly` | Local |
| End of the week, after syncs | `tend-vault`, then `weekly-retro` | Local or cloud |

On-demand skills (`meeting-prep`, `decision`, `query`, `ingest`) need no schedule. Ask for them in your agent, or save the slash command file shown in the routine docs.

## Design conventions

- **The skill file is method only.** Run-specific data lives in the knowledge repo.
- **No codebase or product names in skills.** Specifics are placeholders in `CONFIG.md`.
- **Raw files are immutable.** Snapshots are written once and linked from reports.
- **Routines stay thin.** A routine says where, when and under what conditions. The skill says how.
- **Degrade, do not fail.** A missing tool is logged and skipped. The rest of the run finishes.
- **Commit only your own paths.** Never `git add -A`, other automation may share the repo.
- **Unattended runs report, they do not rewrite.** `tend-vault` produces a list and a human decides.

## Safety notes

- Skills read transcripts, chat and meeting notes. They are told to extract decisions only and never quote private conversation, but review the first few runs before you trust them with sensitive channels.
- Never put credentials in `CONFIG.md`.
- `claude-daily-sync` and `whats-new-weekly` run with permissions pre-accepted when unattended. Run them by hand first and read what they do.
- The publisher rejects image paths outside its images folder. Keep any publisher you write to the same standard.

## License

MIT
