# agent-skills

Skills and routines I use with Claude Code, written to be codebase-agnostic. Copy what is useful.

- **Skills** are reusable instructions an agent loads when a task matches. They live in `skills/<name>/SKILL.md`, with any helper scripts beside them.
- **Routines** are scheduled prompts that invoke a skill on a cadence. They live in `routines/<name>.md`.

## Contents

| Skill | Routine | What it does |
|---|---|---|
| [claude-daily-sync](skills/claude-daily-sync/SKILL.md) | [claude-daily-sync](routines/claude-daily-sync.md) | Snapshots Claude Code memory files and session transcripts into a git repo so cloud agents can read data that only exists on your machine |
| [nightly-sync](skills/nightly-sync/SKILL.md) | [nightly-sync](routines/nightly-sync.md) | Pulls changed pages, databases and chat from your work tools into a repo as immutable snapshots, folds the signal into a wiki, and writes a review report |
| [tend-vault](skills/tend-vault/SKILL.md) | [tend-vault](routines/tend-vault.md) | Weekly health check for a markdown knowledge repo: contradictions, orphans, staleness, tag coverage, patterns, and a prioritized report |
| [weekly-retro](skills/weekly-retro/SKILL.md) | [weekly-retro](routines/weekly-retro.md) | Weekly executive brief from the week's run reports: decisions, shipped work, risks, next-week outlook, with a mandatory back-link pass |

They pair well: `claude-daily-sync` runs first on your machine, `nightly-sync` runs after, `tend-vault` audits the result weekly, and `weekly-retro` synthesizes the week. All four feed one knowledge repo.

## Configuring a skill

Each skill folder has a `CONFIG.md` with the constants you fill in: repo path, Notion page and database ids, Slack channels, thresholds, style rules. Skills read it at the start of every run and never hardcode these values. Anything left as a `<placeholder>` makes the skill log it and skip that part instead of guessing.

## Using a skill

Copy the skill folder into `.claude/skills/` in a project, or `~/.claude/skills/` for every project. Claude Code discovers it by the `name` and `description` in the frontmatter.

## Design conventions

- **The skill file is method only.** Anything that changes run to run (timestamps, counts, gotchas) lives in files in the target repo, not in the skill.
- **Skills assume nothing about your stack.** Project-specific paths and names are arguments or placeholders.
- **Routines stay thin.** A routine says where, when, and under what conditions. The skill says how.

## License

MIT
