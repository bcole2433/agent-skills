---
name: meeting-prep
description: Build a one-screen pre-meeting briefing from a knowledge repo. Given a meeting name, topic, or attendees, pull current status, open questions, recent decisions, and suggested talking points from what the wiki already knows
---

On-demand command. You give it a meeting name, a topic, or a list of attendees. It returns a briefing you can read in under a minute, built only from the repo. It never invents context.

## Config

Read `CONFIG.md` beside this file first. It holds the repo layout, the status tracker pages to check, the look-back window, and the length cap. If a required value is still a `<placeholder>`, say which one and stop.

## Governance

Before writing any file, load the governance files named in `CONFIG.md` (`CONSTITUTION_PATH`, `WIKI_SCHEMA_PATH`, `CONNECTIVITY_PATH`). Follow `CONSTITUTION_PATH` for operating rules and priorities, `WIKI_SCHEMA_PATH` for page types and conventions, and `CONNECTIVITY_PATH` for the tag and WikiLink contract on every file you create or edit. If a file is missing, say so and continue with the skill's own rules.

## Process

1. Read the index to find pages relevant to the meeting topic.
2. Read the people registry to resolve attendees and their roles.
3. Read the relevant entity and concept pages.
4. Read recent raw meeting notes that involve the same topic or people, inside `LOOKBACK_DAYS`.
5. Read each status tracker page listed in `CONFIG.md` (epics, projects, roadmap) for the items the topic touches.

Read cheap first. Use the index and page summaries, and open full pages only for the ones the topic actually touches.

## Output: the briefing

```markdown
### <Meeting name>, <date>

**Attendees:** names and roles from the registry

**Current status**
- status of each relevant item (epics, features, initiatives)
- recent changes or decisions from the wiki

**Open questions**
- unresolved questions from related pages
- anything flagged `[NEEDS REVIEW]`

**Recent context**
- decisions from the last meetings on this topic
- action items from previous meetings, marked resolved or pending

**Suggested talking points**
- drawn from open questions, stale items, and recent changes
```

## Rules

- Pull from the repo, not from imagination. Every status line should trace to a page you read.
- If the wiki has no coverage of the topic, say so at the top and keep the briefing short rather than padding it.
- Flag stale items (not updated within `STALE_AFTER_DAYS`) so the user does not walk in quoting old status.
- One screenful. Cut anything that does not change what the user will say in the room.
- Meeting notes can be sensitive. Carry decisions and status only, never quote private conversation, and mark executive-only material.
- Resolve names against the people registry. If an attendee is not in it, list the name as given and flag it.
- Apply `STYLE_RULES` to the text you write.
