# Screenshot method

For the Phase 3 subagent. Web only, no simulators. Write only PNG files under `STATE_DIR/runs/<date>/screenshots/`. The browser CLI, viewport, and QA account come from `CONFIG.md`.

## Setup

Use `BROWSER_CLI` or any tool that can navigate, take an accessibility snapshot, and save a PNG to disk. Set the viewport to `DEFAULT_VIEWPORT` (mobile) unless the handoff names desktop. If the tool is missing or cannot start, report and stop. Do not fall back to screen capture.

## Navigate and capture

Locate with text, capture to disk, and never screenshot just to look around.

- Navigate to the exact production URL in the handoff, take a compact snapshot to find elements, and re-run it before each click or fill because references go stale after every state change.
- Capture the feature element or a cropped region, not the whole page. The feature should fill at least half the image, or redo it tighter. One capture per planned image, one redo at most.
- Decline cookie and promo banners. No real user's name or details on screen.
- Name files `01-<slug>.png`, `02-<slug>.png`. At most `MAX_IMAGES` per page and `MAX_IMAGES_PER_FEATURE` per feature.

## Sign-in

Prefer signed-out surfaces when the feature allows. When sign-in is required, use only the QA account from `CONFIG.md`, a fake account created for QA. Fetch its code or password from the source named in `QA_ACCOUNT_SECRET_SOURCE`, never from this file. If two fresh attempts are rejected, stop, capture signed-out surfaces only, and report it.

## Never

Solve a CAPTCHA or bot check (stop and report instead), submit any form other than sign-in, change account settings, make a purchase, or use any credentials other than the QA account.

## Report

At most 12 lines: each file and what it shows, anything not captured and why, and whether each URL showed the feature live. Read each final PNG once and nothing else.
