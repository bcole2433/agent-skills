#!/usr/bin/env python3
"""
publish_page.py - Publish a weekly "What's New" draft to a Notion database via the `ntn` CLI.

Draft format (frontmatter + markdown body):

    ---
    title: "What's New: Week of Sep 8"
    tags: [Web, App]
    ---
    <markdown body>

Anywhere in the body, a line of the form:

    {{IMAGE: filename.png | optional caption}}

marks where an image block goes. `filename.png` is resolved relative to
--images-dir.

Usage:
    python3 publish_page.py --draft draft.md --images-dir ./images --data-source <id>
    python3 publish_page.py --draft draft.md --dry-run --data-source <id>
    python3 publish_page.py --draft draft.md --images-dir ./images --cover hero.png --data-source <id>

Prints step status to stderr, and on success prints two final lines to
stdout: `PAGE_URL=<url>` and `PAGE_ID=<id>`.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

NTN_TIMEOUT = 60
IMAGE_PLACEHOLDER_RE = re.compile(r"^\{\{IMAGE:\s*(?P<filename>[^|]+?)\s*(\|\s*(?P<caption>.*))?\}\}\s*$")


def log(msg):
    print(msg, file=sys.stderr)


def die(msg):
    log(f"ERROR: {msg}")
    sys.exit(1)


def run_ntn(args, stdin_path=None, input_bytes=None):
    """Run an `ntn` subcommand with stdin always redirected, never inherited."""
    cmd = ["ntn"] + args
    stdin_source = subprocess.DEVNULL
    stdin_file = None
    try:
        if stdin_path is not None:
            stdin_file = open(stdin_path, "rb")
            stdin_source = stdin_file
        result = subprocess.run(
            cmd,
            stdin=stdin_source,
            input=input_bytes if stdin_path is None and input_bytes is not None else None,
            capture_output=True,
            timeout=NTN_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        die(f"command timed out after {NTN_TIMEOUT}s: {' '.join(cmd)}")
    finally:
        if stdin_file is not None:
            stdin_file.close()
    if result.returncode != 0:
        die(
            f"command failed ({result.returncode}): {' '.join(cmd)}\n"
            f"stderr: {result.stderr.decode(errors='replace')}"
        )
    return result.stdout.decode(errors="replace")


def parse_frontmatter(text):
    if not text.startswith("---"):
        die("draft is missing a leading '---' frontmatter block")
    parts = text.split("---", 2)
    if len(parts) < 3:
        die("draft frontmatter block is not terminated with '---'")
    _, fm_text, body = parts
    title = None
    tags = []
    for line in fm_text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("title:"):
            title = line.split(":", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("tags:"):
            raw = line.split(":", 1)[1].strip()
            raw = raw.strip("[]")
            tags = [t.strip().strip('"').strip("'") for t in raw.split(",") if t.strip()]
    if not title:
        die("draft frontmatter is missing required 'title'")
    return title, tags, body.lstrip("\n")


def find_image_placeholders(body):
    """Return (rewritten_body, [(token, filename, caption), ...])."""
    tokens = []
    out_lines = []
    for line in body.splitlines():
        m = IMAGE_PLACEHOLDER_RE.match(line.strip())
        if m:
            token = f"IMG-PLACEHOLDER-{len(tokens) + 1}"
            filename = m.group("filename").strip()
            caption = (m.group("caption") or "").strip()
            tokens.append((token, filename, caption))
            out_lines.append(token)
        else:
            out_lines.append(line)
    return "\n".join(out_lines), tokens


def validate_images(images, images_dir):
    if not images:
        return
    if images_dir is None:
        die("draft references images but --images-dir was not given")
    for _token, filename, _caption in images:
        path = images_dir / filename
        if not path.is_file():
            die(f"image not found: {path}")


def create_page(data_source, title, body):
    tmp_md = f"---\ntitle: {json.dumps(title)}\n---\n{body}\n"
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(tmp_md)
        tmp_path = f.name
    log(f"creating page under data-source:{data_source} ...")
    out = run_ntn(["pages", "create", "--parent", f"data-source:{data_source}", "--json"], stdin_path=tmp_path)
    data = json.loads(out)
    page_id = data.get("id")
    url = data.get("url")
    if not page_id or not url:
        die(f"unexpected `ntn pages create --json` shape, missing id/url: {out}")
    log(f"page created: {page_id} ({url})")
    return page_id, url


def set_tags(page_id, tags):
    if not tags:
        return
    log(f"setting Tags: {tags}")
    body = {"properties": {"Tags": {"multi_select": [{"name": t} for t in tags]}}}
    run_ntn(["api", "-X", "PATCH", f"v1/pages/{page_id}", "-d", json.dumps(body)])


def upload_file(path):
    log(f"uploading {path.name} ...")
    out = run_ntn(
        ["files", "create", "--filename", path.name, "--content-type", content_type_for(path), "--json"],
        stdin_path=path,
    )
    data = json.loads(out)
    upload_id = data.get("id")
    if not upload_id:
        die(f"unexpected `ntn files create --json` shape, missing id: {out}")
    return upload_id


def content_type_for(path):
    ext = path.suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }.get(ext, "application/octet-stream")


def list_block_children(page_id):
    blocks = []
    cursor = None
    while True:
        path = f"v1/blocks/{page_id}/children"
        args = ["api", path]
        if cursor:
            args.append(f"start_cursor=={cursor}")
        out = run_ntn(args, stdin_path="/dev/null")
        data = json.loads(out)
        blocks.extend(data.get("results", []))
        if data.get("has_more") and data.get("next_cursor"):
            cursor = data["next_cursor"]
        else:
            break
    return blocks


def block_plain_text(block):
    if block.get("type") != "paragraph":
        return None
    rich_text = block.get("paragraph", {}).get("rich_text", [])
    return "".join(rt.get("plain_text", "") for rt in rich_text)


def insert_images(page_id, images, upload_ids):
    blocks = list_block_children(page_id)
    text_to_block_id = {}
    for block in blocks:
        text = block_plain_text(block)
        if text:
            text_to_block_id[text.strip()] = block["id"]

    for token, filename, caption in images:
        placeholder_id = text_to_block_id.get(token)
        if not placeholder_id:
            die(f"placeholder block for {token} ({filename}) not found among page children")
        upload_id = upload_ids[token]
        image_block = {
            "object": "block",
            "type": "image",
            "image": {"type": "file_upload", "file_upload": {"id": upload_id}},
        }
        if caption:
            image_block["image"]["caption"] = [{"type": "text", "text": {"content": caption}}]
        log(f"inserting image block for {token} after {placeholder_id} ...")
        position = {"type": "after_block", "after_block": {"id": placeholder_id}}
        run_ntn(
            [
                "api",
                "-X",
                "PATCH",
                f"v1/blocks/{page_id}/children",
                "-d",
                json.dumps({"children": [image_block], "position": position}),
            ]
        )
        log(f"deleting placeholder block {placeholder_id} ...")
        run_ntn(["api", "-X", "DELETE", f"v1/blocks/{placeholder_id}"], stdin_path="/dev/null")


def set_cover(page_id, images_dir, cover_filename):
    path = images_dir / cover_filename
    if not path.is_file():
        die(f"--cover image not found: {path}")
    upload_id = upload_file(path)
    log("setting page cover ...")
    body = {"cover": {"type": "file_upload", "file_upload": {"id": upload_id}}}
    cmd = ["ntn"] + ["api", "-X", "PATCH", f"v1/pages/{page_id}", "-d", json.dumps(body)]
    result = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, timeout=NTN_TIMEOUT)
    if result.returncode != 0:
        log(
            "WARNING: setting cover failed, continuing without it. "
            f"stderr: {result.stderr.decode(errors='replace')}"
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--draft", required=True, type=Path, help="path to the draft markdown file")
    parser.add_argument("--images-dir", type=Path, default=None, help="directory image placeholders resolve against")
    parser.add_argument("--data-source", required=True, help="Notion data source id to create the page under (NOTION_DATA_SOURCE_ID in CONFIG.md)")
    parser.add_argument("--dry-run", action="store_true", help="print the plan and exit without calling Notion")
    parser.add_argument("--cover", default=None, help="image filename (in --images-dir) to set as the page cover")
    args = parser.parse_args()

    if not args.draft.is_file():
        die(f"draft not found: {args.draft}")
    raw = args.draft.read_text()
    title, tags, body = parse_frontmatter(raw)
    body, images = find_image_placeholders(body)
    validate_images(images, args.images_dir)
    if args.cover and args.images_dir is None:
        die("--cover was given but --images-dir was not")

    if args.dry_run:
        print(f"title: {title}")
        print(f"tags: {tags}")
        print(f"images: {[(f, c) for _t, f, c in images]}")
        print(f"cover: {args.cover}")
        print(f"body length: {len(body)} chars")
        return

    page_id, url = create_page(args.data_source, title, body)
    set_tags(page_id, tags)

    if images:
        upload_ids = {token: upload_file(args.images_dir / filename) for token, filename, _caption in images}
        insert_images(page_id, images, upload_ids)

    if args.cover:
        set_cover(page_id, args.images_dir, args.cover)

    print(f"PAGE_URL={url}")
    print(f"PAGE_ID={page_id}")


if __name__ == "__main__":
    main()
