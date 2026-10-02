---
name: weekly-retro
description: Weekly executive synthesis of a knowledge repo. Reads the week's run reports and logs, writes a one-scroll brief of decisions, shipped work, risks and next-week outlook, then back-links it into every page it references
---

Turns a week of sync reports into a brief a busy reader finishes in under two minutes. It synthesizes. It does not copy meeting notes, and it does not re-read raw data.

It works two ways:

- **Scheduled (unattended):** write the page, run the back-link pass, update the index and log, commit, push.
- **Interactive (`/weekly-retro`):** show the draft first and write only after approval. Accepts an optional week argument.

## Config

Read `CONFIG.md` beside this file first. It holds the paths, the week definition, the reader profile, the table shapes, and the style rules. If a required value is still a `<placeholder>`, log it and stop.

## Phase 1: Read (minimal)

1. The link contract file if `LINK_CONTRACT_PATH` is set. It is one page and the page you write must satisfy it.
2. The index, for the current wiki state.
3. The log, this week's entries only.
4. **Run reports from this week. These are the primary source.** They already summarize the raw data, so do not re-read raw files or wiki pages unless a specific claim needs verifying.
5. Daily notes for the week, if any.
6. The people registry, for team context.
7. Last week's retro, for comparison.

**Do not read** raw files, schema or constitution documents, or wiki pages beyond verifying a claim. Cheap reads first, expensive reads only on doubt.

## Phase 2: Write the synthesis

Create `SYNTHESES_DIR/YYYY-WXX-weekly-retro.md` (ISO week). Frontmatter:

```yaml
---
type: synthesis
domain: <config>
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [this week's run reports and daily notes]
tags: [weekly-retro, synthesis, weekly, YYYY-WXX, <initiatives this week>]
confidence: high
status: active
---
```

### Format: an executive brief, not a narrative

Every section obeys these constraints with no exceptions. A retro full of multi-sentence bullets is a failed retro even when the content is right.

- **Lead with impact.** The first line of the retro and of every section is the bottom line: what changed, what is at risk, what needs a decision.
- **No paragraphs.** No bullet spans more than 2 lines. If a point needs more, split it or cut it.
- **Tables over lists** for three or more items sharing a shape (status, owner, risk, date).
- **Bold the number, date, or verdict.** Not the connective tissue.
- **Cut hedging, scene-setting, and commentary about the repo's own coverage** unless a coverage gap is the finding. One line stating a source gap is fine.
- **One scroll.** If a section has nothing material, write "Nothing material" and move on. Never pad to match prior weeks.

### Sections

| Section | Shape |
|---|---|
| Week Summary | 3 to 5 one-line bullets, each led by the outcome (shipped, blocked, decided) with the headline fact bold |
| Key Decisions Made | Table: `Decision \| Rationale \| Links`, one line per cell |
| Shipped This Week | Table: `Item \| Status \| Notes` |
| Blocked / At Risk | Table: `Item \| Risk \| Owner \| Deadline`. Usually the most-read section, keep every row scannable at a glance |
| People & Context | Table: `Person \| This Week`, one line each |
| Patterns & Trends | Max 5 bullets of 1 to 2 lines, pattern first and evidence second |
| Next Week Outlook | Table: `Priority (P0/P1/Watch) \| What to Watch`, P0 first |
| Open Questions | One line each, phrased as an actual question |
| Relations | `[[WikiLink]]` plus one line of context for every page the retro references, including prior retros |

The Relations list is the source of truth for the back-link pass. Make it complete before moving on. Flag strategic shifts and direction changes, and compare against last week's retro.

## Phase 3: Back-link pass (mandatory)

An unlinked retro is an orphan at birth. For each `[[WikiLink]]` in the retro's Relations section:

1. Open the target page.
2. Find its `## Relations` section, or create one above `## Log` if absent.
3. Append `- [[YYYY-WXX-weekly-retro]]` plus the one-line context from the retro's own entry.
4. If a line for this retro is already there, skip. The pass is idempotent.
5. Skip prior retros, the log, template files, anything outside the wiki, and any folder listed in `BACKLINK_SKIP_DIRS`.

Sanity check: the new retro should have at least `MIN_INBOUND_LINKS` inbound links when the pass finishes. If it has fewer, the Relations list was incomplete. Go back and fix it before committing.

## Phase 4: Record

1. Add the retro to the index (by type, entries table, stats counter).
2. Add a `log.md` entry above the newest one: `## [YYYY-MM-DD] weekly-retro | Week XX synthesis`, including a "Pages back-linked: N" line so the audit trail is visible.
3. Commit only the retro, the pages the back-link pass touched, the index, and the log. Never `git add -A`. Message: `[weekly-retro] YYYY-WXX: weekly synthesis (N pages back-linked)`.

## Phase 5: Push

`git pull --rebase origin main`, then push. Try once, never retry, and never fail the run or undo the commit over a push problem. Note any failure in the log entry. In a git worktree whose branch is not `main`, push `HEAD:main`, because a stale local `main` ref can make a plain push print "Everything up-to-date" while publishing nothing.

## Rules

- Synthesis only. Find patterns, do not copy source notes.
- The format constraints are hard rules, not style preferences. If a draft section reads like a paragraph, rewrite it as a table or a short bullet before moving on.
- Do not call the retro done until the back-link pass has run and the inbound count is verified.
- Apply `STYLE_RULES` to text you write, checking added lines only (`git diff | grep '^+'`), never with a whole-file find-and-replace.
- If the week had no material change, write a short retro that says so instead of padding it.
