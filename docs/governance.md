# Governance files

Every skill reads a small set of governance files from the knowledge repo before it writes anything. They keep all skills on one set of rules. Skills never copy their content. They read the files live.

| File | Purpose | Loaded by |
|---|---|---|
| `CONSTITUTION.md` | How the agent operates in the repo, plus current priorities | all skills |
| `WIKI-SCHEMA.md` | Conventions, page types, operations | all skills |
| `CONNECTIVITY.md` | Tag and WikiLink contract loaded before writing | all skills |
| `SYNC-STATE.md` | Pipeline sync state per source | `nightly-sync`, `claude-daily-sync`, `ingest`, `tend-vault` |
| `index.md` | Master catalog of all wiki pages | already wired through each `CONFIG.md` |
| `log.md` | Append-only timeline of all operations | already wired through each `CONFIG.md` |

Each skill's `CONFIG.md` has a `Governance files` table with the path of each file relative to the knowledge repo root. Change a value there if your repo names or places a file differently. Each `SKILL.md` has a `Governance` section telling the agent to load them first.
