# Routine: nightly-sync

The scheduled prompt that invokes the `nightly-sync` skill. The skill holds the method. This file holds only where, when, and under what conditions.

| Field | Value |
|---|---|
| Skill | [`nightly-sync`](../skills/nightly-sync/SKILL.md) |
| Runs | Local or cloud. Needs only the knowledge repo and read access to your tools |
| Schedule | Nightly, after `claude-daily-sync` so the two never write the same files at once (example cron `0 19 * * *`) |
| Mode | Unattended, all permissions pre-accepted |

## Design notes

- **The real instructions live in the repo, not in the prompt.** The routine tells the agent to read `SKILL.md` from the checked-out repo, so improving the skill is a normal commit and the scheduled prompt never needs editing.
- **Scope is stated explicitly.** The routine names what it does not cover so an agent that notices adjacent data does not wander into another pipeline's job.
- **Sources are data, not prompt text.** Ids and channel names live in the skill's `CONFIG.md`.

## Install

Claude desktop scheduled tasks live at `~/.claude/scheduled-tasks/<name>/SKILL.md`. Copy the prompt below there and set the schedule in the scheduled tasks UI. For a cloud run, create a routine with the same prompt and attach the repo and the connectors it needs (docs workspace, chat).

## Prompt

Replace the `<...>` placeholders.

```markdown
---
name: nightly-sync
description: Nightly pull of docs and chat changes into the knowledge repo, ingest to wiki, generate a review report
---

This is an automated, unattended nightly run. All permissions are pre-accepted. Make reasonable choices without asking clarifying questions and note them in the pending report.

The pipeline's real instructions live in the knowledge repo, not in this prompt.

1. Use the working checkout at `<path to repo>` (remote: `<git remote url>`).
2. Fetch the latest and work from current `origin/main`, then invoke the `nightly-sync` skill from `.claude/skills/nightly-sync/SKILL.md`. Read it in full and execute it as written. Do not summarize it from memory.
3. This pipeline covers docs and chat only. Claude memory and sessions belong to the separate `claude-daily-sync` task. Do not attempt those steps even if you notice `raw/claude/` files.
```

## Ordering with other routines

Run the local `claude-daily-sync` first, then this one. Each owns its own raw folders and its own `SYNC-STATE.md` section, so they can share one repo without colliding. Rebase conflicts on `log.md` and `index.md` are resolved by keeping both entries.
