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

## Core Principles
- Do not preserve backward compatibility. Remove obsolete paths instead of
  adding compatibility layers, fallbacks, or migrations.
- Choose the simplest implementation that fully meets the current
  requirements. Avoid speculative abstractions, configuration, and
  indirection.
- Grow the system in layers. Start from the smallest version that works end
  to end, and add each new capability on top of a product that already
  works. Never trade a working product for unfinished complexity.
- Keep components modular and concerns clearly separated.
- Lean on the dependencies already in the project before writing your own
  implementation or adding packages. Do not assume a library lacks a
  capability without checking its documentation and types.
- Make architectural decisions for the long term. Do not accept a stopgap
  that only works for now and is meant to be replaced later.


## Agent Behavior

Write plainly, with no mannered prose, in responses, docs, PR descriptions, and commit messages.
Never add `Co-Authored-By:`, `Generated with [Claude Code]` line (or any "Generated with" footer), `Claude-Session:` lines, or Claude session links (`https://claude.ai/code/session_...`) to commit messages or PR descriptions.

**Self-improve:** after corrections, update `lessons.md`. Review at session start.
**Verify before done:** run tests, check logs, test in browser
**Lint budget gate:** `yarn lint:budget` enforces warning count. Re-baseline with `node scripts/lint-budget.mjs --update`.

## Git workflow

- Never commit directly to `main` or `develop`. Branch off `develop` and open a PR into `develop`. `develop` is merged into `main` by PR.
- This repo is public. Commit with the GitHub noreply email (already set in local git config). Never commit real ids, channel ids, credentials, QA logins or run output. Fill real values only in a private copy of the config.
- `__pycache__/` and `.pyc` files are gitignored. Keep them out.
