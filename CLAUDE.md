# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A public library of Claude Code skills and scheduled routines. It is markdown plus a few stdlib-only Python helpers. There is no build, lint or test tooling. The skills operate on a separate knowledge repo (wiki, raw snapshots, reports), never on this one.

- `skills/<name>/SKILL.md` is the method. `CONFIG.md` beside it holds every constant the skill needs.
- `routines/<name>.md` is the thin scheduled prompt that invokes a skill.
- `docs/` holds the service capability map (`services.md`) and the governance file contract (`governance.md`).

## Design rules to preserve

- **SKILL.md is method only.** Run-mutable data (timestamps, counts, gotchas) lives in the knowledge repo, never in a skill.
- **No product, company or person names.** Every specific is a `<placeholder>` in `CONFIG.md`. Services (Notion, Slack, PostHog) appear only as swappable examples.
- **Skills read `CONFIG.md` first.** A required value still a `<placeholder>` means log it and skip, never guess.
- **Every skill has a `## Governance` section** and a `## Governance files` table in its `CONFIG.md`. They load `CONSTITUTION.md`, `WIKI-SCHEMA.md` and `CONNECTIVITY.md` from the knowledge repo before writing. Sync skills (`nightly-sync`, `claude-daily-sync`, `ingest`, `tend-vault`) also load `SYNC-STATE.md`. Keep new skills consistent with this. `DESIGN.md` is deliberately not wired in.
- Routines stay thin, raw files are immutable, and skills commit only their own paths (never `git add -A`).
- New skills need a `SKILL.md`, a `CONFIG.md`, an entry in the README tables, and usually a routine.

## Helper scripts

Python 3 stdlib only. Each prints usage with `--help`.

```bash
python3 skills/tend-vault/lint_tags.py --dirs wiki lessons --root <knowledge-repo>
python3 skills/claude-daily-sync/extract_sessions.py --since YYYY-MM-DD
python3 skills/whats-new-weekly/scripts/collect_shipped.py --config skills/whats-new-weekly/CONFIG.md --since YYYY-MM-DD
python3 skills/whats-new-weekly/scripts/publish_page.py --draft draft.md --data-source <id> --dry-run
```

`collect_shipped.py` reads the first fenced `json` block of the `CONFIG.md` it is given. `publish_page.py` must keep rejecting image paths outside `--images-dir`.

## Git workflow

- Never commit directly to `main` or `develop`. Branch off `develop` and open a PR into `develop`. `develop` is merged into `main` by PR.
- This repo is public. Commit with the GitHub noreply email (already set in local git config). Never commit real ids, channel ids, credentials, QA logins or run output. Fill real values only in a private copy of the config.
- `__pycache__/` and `.pyc` files are gitignored. Keep them out.
