# Routine: weekly-retro

The scheduled prompt that invokes the `weekly-retro` skill once a week. The skill also works on demand as a slash command.

| Field | Value |
|---|---|
| Skill | [`weekly-retro`](../skills/weekly-retro/SKILL.md) |
| Runs | Local or cloud. Needs only the knowledge repo |
| Schedule | Weekly, end of the work week, after the syncs (example cron `0 16 * * 5`) |
| Mode | Unattended. Writes one page, back-links it, commits |

## Design notes

- **Reads reports, not raw data.** The week's sync reports are already summaries, so the retro stays cheap and fast.
- **The back-link pass is part of the job.** A synthesis nobody links to disappears from the graph. The routine is not done until the inbound count is verified.
- **Run it after `tend-vault`** if you want the retro to see that week's health findings.

## Interactive command

To run on demand, save this as `.claude/commands/weekly-retro.md` in the knowledge repo:

```markdown
# /weekly-retro

Run the weekly-retro skill interactively for the current week, or the week given below. Show the draft for my review and write the page only after I approve it.

$ARGUMENTS
```

## Install

Desktop agent scheduled tasks live at `~/.claude/scheduled-tasks/<name>/SKILL.md`. Copy the prompt below there and set the schedule in the scheduled tasks UI.

## Prompt

Replace the `<...>` placeholders.

```markdown
---
name: weekly-retro
description: Weekly executive synthesis of the knowledge repo, with back-links
---

This is an automated, unattended weekly run. Make reasonable choices without asking clarifying questions.

1. Use the working checkout at `<path to repo>` (remote: `<git remote url>`).
2. Fetch the latest and work from current `origin/main`, then invoke the `weekly-retro` skill from `.claude/skills/weekly-retro/SKILL.md`. Read it in full and execute it as written.
3. Run the back-link pass and verify the inbound count before committing.
```
