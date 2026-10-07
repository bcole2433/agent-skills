# Notion publishing

How to publish the weekly page into a Notion database with `scripts/publish_page.py` and the `ntn` CLI. Ids come from `CONFIG.md`.

## IDs

- `NOTION_DATABASE_ID`: the database that holds one page per week.
- `NOTION_DATA_SOURCE_ID`: create pages under this, not the database id. Resolve it with `ntn api v1/databases/<database-id> | jq -r '.data_sources[0].id'`.
- Properties: a title property (`NOTION_TITLE_PROPERTY`) and a multi-select tags property (`NOTION_TAGS_PROPERTY`). New tag options are created on demand from unknown names.

## Draft file format

The orchestrator writes a draft markdown file, then hands it to the script.

```markdown
---
title: "What's New: Week of Sep 8"
tags: [Web, App]
---
## This Week

Body markdown goes here. Headings, paragraphs, bullet lists and links pass
straight through to `ntn pages create`.

### Feature title

{{IMAGE: screenshot.png | Optional caption text}}

The description goes after the image, so the screenshot sits between the
title and the text.
```

- `title` is required. `tags` is optional.
- `{{IMAGE: filename.png | caption}}` must be alone on its own line. The filename resolves relative to `--images-dir`. The caption is optional.

## Running the script

```bash
python3 skills/whats-new-weekly/scripts/publish_page.py \
  --draft draft.md --images-dir ./images --data-source <id>

# preview without touching Notion
python3 skills/whats-new-weekly/scripts/publish_page.py \
  --draft draft.md --images-dir ./images --data-source <id> --dry-run

# also set a page cover (the image must live in --images-dir)
python3 skills/whats-new-weekly/scripts/publish_page.py \
  --draft draft.md --images-dir ./images --data-source <id> --cover hero.png
```

Step status goes to stderr. On success stdout ends with exactly `PAGE_URL=<url>` and `PAGE_ID=<id>`. On `--dry-run` it prints the parsed title, tags, images, cover and body length and exits 0 without calling Notion. On any failure it prints an `ERROR:` line to stderr and exits non-zero. A failed cover upload is a warning only.

## Verifying a published page

```bash
ntn pages get <page-id> < /dev/null        # markdown body and frontmatter properties
ntn api v1/pages/<page-id> < /dev/null     # raw properties (tags, cover)
```

Check that headings, paragraphs, bullets and links round-trip, that each image placeholder became an inline image at the same position, and that tags match the draft.

## Undoing a publish

Trash the page (recoverable from Notion's trash):

```bash
ntn api -X PATCH v1/pages/<page-id> -d '{"in_trash":true}' < /dev/null
```

If `in_trash` is rejected by the API version in use, try `"archived":true`.

## `ntn` gotchas

- `ntn pages create --content '...'` hangs when run non-interactively. Always feed markdown through stdin: `ntn pages create --parent data-source:<id> --json < page.md`. For read-only commands redirect stdin from `/dev/null` so nothing inherits the terminal.
- `ntn pages create` strips a leading frontmatter block and uses its `title`. Every other frontmatter key is ignored, so tags are set separately with a PATCH on the page properties.
- Give API paths without a leading slash (`v1/...`). `ntn api ls` lists endpoints and `ntn api <path> -X <METHOD> --docs` prints request and response shapes. Check it before assuming a parameter name.
- The `after` parameter on `PATCH v1/blocks/{id}/children` is rejected. Use `position`: `{"children": [...], "position": {"type": "after_block", "after_block": {"id": "<block_id>"}}}`. `{"type": "start"}` and `{"type": "end"}` are the other position types.
- File uploads: `ntn files create --filename shot.png --content-type image/png --json < shot.png` returns an object whose `id` can be attached exactly once, to one block or one page cover. A cover needs its own separate upload.
- Archiving with `in_trash: true` worked directly in testing.
