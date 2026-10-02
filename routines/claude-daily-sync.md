# Routine: claude-daily-sync

A routine is the scheduled prompt that invokes a skill. The skill holds the method. The routine holds only the "where, when, and under what conditions" so it stays short.

| Field | Value |
|---|---|
| Skill | [`claude-daily-sync`](../skills/claude-daily-sync/SKILL.md) |
| Runs | Local machine only (reads `~/.claude/projects`) |
| Schedule | Daily, late afternoon, while the machine is awake (example cron `0 17 * * *`) |
| Mode | Unattended, all permissions pre-accepted |

## Why local, and why late afternoon

The data lives in `~/.claude/projects`, which no cloud environment can reach. A local scheduled task is the only way to read it, and it only fires while the machine is on. Schedule it for a time you are reliably at your desk, ahead of any cloud routine that consumes its output.

## Install

Claude desktop scheduled tasks live at `~/.claude/scheduled-tasks/<name>/SKILL.md`. Copy the prompt below into `~/.claude/scheduled-tasks/claude-daily-sync/SKILL.md` and set the schedule in the scheduled tasks UI. Put the skill itself in your knowledge repo at `.claude/skills/claude-daily-sync/` (or in `~/.claude/skills/`).

## Prompt

Replace the `<...>` placeholders.

```markdown
---
name: claude-daily-sync
description: Daily local-only sync of Claude memory and sessions into the knowledge repo
---

This is an automated, unattended local-only run. All permissions are pre-accepted. Make reasonable choices without asking clarifying questions and note them in the run report.

This task must run on my local machine while it is on. It reads `~/.claude/projects/`, which does not exist in any cloud environment.

1. Work in my knowledge repo checkout at `<path to repo>` (remote: `<git remote url>`).
2. Fetch the latest and work from current `origin/main` (`git pull --rebase origin main`).
3. Invoke the `claude-daily-sync` skill from `.claude/skills/claude-daily-sync/SKILL.md`. Read it in full and execute it as written. Do not summarize it from memory.
4. This routine covers Claude memory and sessions only. Other sources are handled by their own routines.
5. If `~/.claude/projects` does not exist, the skill's own guard logs it and stops without writing or committing.
```

## Pairing with a cloud routine

The point of the push is that a cloud routine can then read `raw/claude/` from the repo. A typical downstream consumer is a nightly or weekly job that pulls the repo, reads the newest session digests, and synthesizes a summary or backlog from them. Run the local sync first so the cloud job sees fresh data.
