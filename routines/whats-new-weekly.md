# Routine: whats-new-weekly

The scheduled prompt that invokes the `whats-new-weekly` skill once a week.

| Field | Value |
|---|---|
| Skill | [`whats-new-weekly`](../skills/whats-new-weekly/SKILL.md) |
| Runs | Local machine only (needs repo checkouts, `gh`, `ntn`, and optionally an analytics CLI and a browser CLI) |
| Schedule | Weekly, early in the week so it covers the prior week's releases (example cron `0 18 * * 1`) |
| Mode | Unattended, all permissions pre-accepted |

## Design notes

- **Local only.** The skill reads local repo checkouts and CLIs that do not exist in a cloud environment. Its own guard logs and stops when they are missing.
- **Orchestrator plus workers.** One strong model keeps judgment (what to feature, the final copy, whether a metric moved because of a launch). Cheaper models do the reading and collecting. The prompt states this so the run does not collapse into one expensive agent.
- **Cadence is the product.** If nothing shipped, the run still publishes a short page so readers keep expecting it.
- **Shared repo.** If other pipelines write to the same repo, the prompt limits this one to its own folders and one commit at the end.

## Install

Desktop agent scheduled tasks live at `~/.claude/scheduled-tasks/<name>/SKILL.md`. Copy the prompt below there and set the schedule in the scheduled tasks UI.

## Prompt

Replace the `<...>` placeholders.

```markdown
---
name: whats-new-weekly
description: Weekly local-only run that publishes the What's New page to Notion from the last 7 days of production releases, context and analytics impact
---

This is an automated, unattended local-only run. All permissions are pre-accepted. Make reasonable choices without asking clarifying questions and record them in the run report.

Model rule: you are the orchestrator and run on `<strongest model>`. Dispatch research, collection, screenshot and drafting-support work to `<cheaper model>` subagents, never more than 3 at once. You keep feature selection, the final copy, the impact causation judgment, the screenshot decision, and publishing.

This task must run on my local machine. It needs the repo checkouts, the `gh` CLI, the `ntn` CLI, and optionally the analytics and browser CLIs. None exist in a cloud environment.

1. Work in the knowledge repo checkout at `<path to repo>` (remote: `<git remote url>`).
2. Run `git pull --rebase origin main`.
3. Invoke the `whats-new-weekly` skill from `.claude/skills/whats-new-weekly/SKILL.md`. Read it in full and execute it as written. Read every file under its `references/` folder that a phase points to before running that phase.
4. The window is the rolling 7 days ending now. Publish directly to the Notion database named in the skill's `CONFIG.md`. If nothing shipped, still publish the short cadence page.
5. If the local-only check fails, log it and stop without writing or committing anything.
6. Other pipelines may write to this repo. Keep all writes under the skill's state folder, the reports folder and the log, commit once at the end, and `git pull --rebase` before pushing, retrying once on conflict.
```
