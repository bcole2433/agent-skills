---
name: query
description: Answer a question from a knowledge repo's accumulated wiki, citing specific pages, rating confidence, and naming gaps. Offers to save novel answers as a synthesis page
---

On-demand command. It answers from what the repo knows, says how well sourced the answer is, and says what is missing. It does not fill gaps with general knowledge unless it labels that clearly.

## Config

Read `CONFIG.md` beside this file first. It holds the repo layout and the synthesis template location. If a required value is still a `<placeholder>`, say which one and stop.

## Process

1. **Start from the index.** Never guess which pages exist.
2. Read the relevant wiki pages and follow cross-references as needed.
3. Read raw sources only if a page points to one and the question needs more detail than the page holds.
4. Check the people registry if the question involves team members.
5. Synthesize the answer with `[[PageName]]` citations.

## Output

Answer the question directly first. Then:

- **Sources:** the wiki pages used.
- **Confidence:** High, Medium, or Low, based on how well sourced the answer is. High means stated in a recent page. Low means inferred or from a stale page.
- **Gaps:** what the wiki lacks that a complete answer would need.

## When to create a page

If the answer reveals something worth keeping (a comparison, an analysis, a pattern across pages):

1. Propose a new synthesis page.
2. Show the draft and ask for approval.
3. Write it from the template at `SYNTHESIS_TEMPLATE_PATH` only after approval, then add it to the index and log.

## Rules

- Cite specific pages, never "the wiki says".
- If the answer needs information that is not in the repo, say so plainly. Do not guess.
- Prefer the newer source when two pages disagree, and name both.
- Flag a stale source (not updated within `STALE_AFTER_DAYS`) when the answer depends on it.
- Meeting notes and DMs can be sensitive. Answer with decisions and status, never quote private conversation, and respect executive-only markings.
- Apply `STYLE_RULES` to the text you write.
