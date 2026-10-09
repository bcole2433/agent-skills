---
name: decision
description: Log a decision in a knowledge repo with context, rationale, alternatives and consequences, then cross-reference it from every affected page so it can be found later
---

On-demand command. A decision that lives only in a meeting or a chat thread gets relitigated. This skill writes it down once, in a fixed shape, and links it into the pages it affects.

## Config

Read `CONFIG.md` beside this file first. It holds the paths, the allowed statuses and domains, and the ledger location. If a required value is still a `<placeholder>`, say which one and stop.

## Governance

Before writing any file, load the governance files named in `CONFIG.md` (`CONSTITUTION_PATH`, `WIKI_SCHEMA_PATH`, `CONNECTIVITY_PATH`). Follow `CONSTITUTION_PATH` for operating rules and priorities, `WIKI_SCHEMA_PATH` for page types and conventions, and `CONNECTIVITY_PATH` for the tag and WikiLink contract on every file you create or edit. If a file is missing, say so and continue with the skill's own rules.

## Process

1. Read the index to find pages related to the decision.
2. Collect the five facts below. Extract them from the conversation or source when they are there, and ask only for what is missing:
   - What was decided?
   - Why? (rationale)
   - What alternatives were considered, and why was each rejected?
   - Who decided?
   - What does it affect?
3. Resolve every name against the people registry.
4. Write `DECISIONS_DIR/YYYY-MM-DD-slug.md`:

```markdown
---
type: decision
created: YYYY-MM-DD
domain: <domain of the most affected page>
status: decided
decided_by: [names]
tags: [decision, <domain>, <topic>]
---

# Decision: <title>

## Context
Why was this decision needed?

## Decision
What was decided, in one or two sentences.

## Rationale
Why this option over the alternatives.

## Alternatives Considered
- <Alternative 1>: why it was rejected
- <Alternative 2>: why it was rejected

## Consequences
What this decision changes, constrains, or commits the team to.

## Relations
- [[Affected Page 1]]
- [[Affected Page 2]]
```

`status` is one of the values in `ALLOWED_STATUSES`. Use `revisit` when the decision has a review date and `reversed` only when a later decision replaces it. Name the replacing decision.

5. For each affected page, add a line to its Relations section linking the decision, and a dated line to its Log section.
6. If a decision ledger exists and the decision resolves an open entry, link the decision file from that entry and move the entry to Resolved. Do not delete it.
7. Add an entry to the log (newest first, above the existing newest entry).

## Rules

- Always cross-reference the decision from the affected pages. A decision nothing links to is lost.
- Use the domain of the most affected page.
- Record what was decided, not who argued what. Keep the rationale to the reasoning, not the conversation.
- If the decision contradicts an existing page, flag it with `[NEEDS REVIEW]` on that page instead of silently rewriting it.
- If two sources disagree on what was decided, write the decision as the later or more authoritative source states it, and note the disagreement under Context.
- Apply `STYLE_RULES` to text you write.
