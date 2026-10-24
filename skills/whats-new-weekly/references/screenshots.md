# Screenshot method

For the Phase 3 and Phase 3b subagents. Phase 3 captures production, Phase 3b captures unreleased work from a local run. Web only, no simulators. Write only PNG files under `STATE_DIR/runs/<date>/screenshots/`. The browser CLI, viewport, and QA account come from `CONFIG.md`.

## Setup

Use `BROWSER_CLI` or any tool that can navigate, take an accessibility snapshot, and save a PNG to disk. Set the viewport to `DEFAULT_VIEWPORT` (mobile) unless the handoff names desktop. If the tool is missing or cannot start, report and stop. Do not fall back to screen capture.

## Navigate and capture

Locate with text, capture to disk, and never screenshot just to look around.

- Navigate to the exact production URL in the handoff, take a compact snapshot to find elements, and re-run it before each click or fill because references go stale after every state change.
- Capture the feature element or a cropped region, not the whole page. The feature should fill at least half the image, or redo it tighter. One capture per planned image, one redo at most.
- Decline cookie and promo banners. No real user's name or details on screen.
- Name files `01-<slug>.png`, `02-<slug>.png`. At most `MAX_IMAGES` per page and `MAX_IMAGES_PER_FEATURE` per feature. Phase 3b images are a separate cap of `MAX_BUILDING_IMAGES`, at most 1 per feature.

## Running unreleased work (Phase 3b only)

For "Coming up" images. Web repos only. The handoff names the repo, the branch or PR the work lives on, the route to open, and the element to frame.

```bash
REPO=<local_path from CONFIG.md>
WT="$TMPDIR/wn-<repo>-<date>"
git -C "$REPO" fetch origin <branch>
git -C "$REPO" worktree add --detach "$WT" origin/<branch>
cd "$WT"
```

- Find the work with `git log --first-parent --oneline origin/<production branch>..origin/<integration branch>`. Do not add `--no-merges`, repos that merge with merge commits would show nothing.
- Install and start with the repo's own scripts (its package manifest and README). Copy env files from the main checkout into the worktree instead of creating or pulling secrets. Pick a free port, for example with a `PORT` env var, because many start scripts do not forward `--port` and the main checkout's dev server usually holds the default. Wait for the server to answer before capturing.
- Give up and report if install plus start has not worked within about 5 minutes, or if the app only runs against production data it would write to. Never run migrations, seed scripts or anything that writes to a shared database.
- Capture the same way as above against `http://localhost:<port>`. For a tall section, scroll it into view and use a clip region instead of an element capture, which can stitch a sticky header and the framework's dev badge into the image. Hide any dev overlay still visible.
- Launch gates. Unreleased features are often hidden behind a gate that is off locally, so the old UI renders. Before capturing, check the route and its layout for environment-variable and feature-flag checks. If a gate is only an env var missing from every env file, you may set it for this local run only. If the screen is still the old UI, report INCOMPLETE.
- Data. If the screen's data exists only for a future event or date (so it shows an empty or "available later" state), it is INCOMPLETE. Do not fake data.
- The work must be on a branch that contains the whole feature. If the change is one piece of a larger feature and the screen depends on pieces missing from the branch, report INCOMPLETE.
- Cleanup, always, even on failure: stop the dev server, remove the worktree with `git -C "$REPO" worktree remove --force "$WT"`, and confirm `git -C "$REPO" status --short` is unchanged. Never commit, push, stash or edit anything in a repo.

### Completeness check

Before reporting, Read each final PNG once and judge it against this list. Report COMPLETE only if every line is true:
- The feature is working end to end in the frame with realistic data on screen.
- None of these appear: empty state, loading skeleton, spinner, error banner, broken image, placeholder text, "coming soon", debug or dev overlay, a feature flag falling back to the old UI, error toasts.
- The frame shows what the bullet in the handoff promises.
- The feature fills at least half the image and no real person's name or details show.

Otherwise report INCOMPLETE with one line saying what is missing, delete the file, and do not retry more than once. A redo is allowed only to fix framing, never to coax a half-built screen into looking done.

## Sign-in

Prefer signed-out surfaces when the feature allows. When sign-in is required, use only the QA account from `CONFIG.md`, a fake account created for QA. Fetch its code or password from the source named in `QA_ACCOUNT_SECRET_SOURCE`, never from this file. If two fresh attempts are rejected, stop, capture signed-out surfaces only, and report it.

## Never

Solve a CAPTCHA or bot check (stop and report instead), submit any form other than sign-in, change account settings, make a purchase, or use any credentials other than the QA account.

## Report

At most 12 lines: each file and what it shows (for Phase 3b, COMPLETE or INCOMPLETE and the evidence), anything not captured and why, and whether each URL showed the feature live. Read each final PNG once and nothing else.
