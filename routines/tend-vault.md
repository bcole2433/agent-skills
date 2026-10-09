# Routine: tend-vault

The scheduled prompt that invokes the `tend-vault` skill once a week. The skill also works on demand as a slash command.

| Field | Value |
|---|---|
| Skill | [`tend-vault`](../skills/tend-vault/SKILL.md) |
| Runs | Local or cloud. Needs only the knowledge repo |
| Schedule | Weekly, after the week's syncs have landed (example cron `0 9 * * 5`) |
| Mode | Unattended and read-only on content. Writes one report and commits it |

## Design notes

- **Report only.** An unattended run that rewrites your notes is a risk. The routine produces a prioritized list and a human decides.
- **Reads summaries, not raw.** Pattern detection uses the run reports from the week, so a large raw folder never enters context.
- **Run it after the syncs.** Health checks on stale data waste the pass.

## Interactive command

To run on demand, save this as `.claude/commands/tend.md` in the knowledge repo:

```markdown
# /tend

Run the tend-vault skill interactively. Show findings inline grouped by severity (red, yellow, blue) and ask before making any change. Show proposed fixes and let me approve each.

$ARGUMENTS
```

## Install

Desktop agent scheduled tasks live at `~/.claude/scheduled-tasks/<name>/SKILL.md`. Copy the prompt below there and set the schedule in the scheduled tasks UI.

## Prompt

Replace the `<...>` placeholders.

```markdown
---
name: tend-vault
description: Weekly knowledge repo maintenance, lint, staleness, tag coverage, patterns, report
---

This is an automated, unattended weekly run. Make reasonable choices without asking clarifying questions and note them in the report.

1. Use the working checkout at `<path to repo>` (remote: `<git remote url>`).
2. Fetch the latest and work from current `origin/main`, then invoke the `tend-vault` skill from `.claude/skills/tend-vault/SKILL.md`. Read it in full and execute it as written.
3. Report only. Do not edit wiki or lesson content unless `SCHEDULED_AUTO_FIX` is `yes` in the skill's `CONFIG.md`.
```
