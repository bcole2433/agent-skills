# How the collector decides what shipped

Repos are listed in the JSON block of `CONFIG.md`. This file explains the method so you can tune it.

## Release trains

A feature shipped when it reached the production branch, not when its PR merged to the integration branch, which can be days earlier. A **release train** is a merge commit that lands on `origin/<production_branch>` inside the window (`git rev-list --first-parent`). Everything that commit introduced, `git log <parent>..<merge-sha>`, or the commit itself when it has no second parent, is scanned for PR references:

- `Merge pull request #(\d+)` (merge-commit style)
- a trailing `(#\d+)` on the subject line (squash-merge style)

Some teams run a two-hop train, `develop` into `staging`, then `staging` into `production`. The intermediate sync PR appears inside the introduced range. It is mechanical, not a feature. The collector flags any PR whose base and head match a leg in `release_train_legs`, or whose title is in `release_train_titles`, as a release train and keeps it out of the candidates. The real feature PRs underneath are what show up as shipped.

## Repos that ship by GitHub Release

Set `releases_only: true` on a repo whose production branch does not move (typical for mobile apps). The collector then reads `gh api repos/<repo>/releases --paginate` and filters by `published_at`. PRs merged to the integration branch in the window appear as "merged, not yet released" context.

## Commands the script runs

```bash
# Per repo, before reading history (skip with --skip-fetch)
git fetch origin <production_branch>
git fetch origin <integration_branch>

# Release trains in the window
git rev-list --first-parent --since=<since> --until=<until> origin/<production_branch>

# What a given train introduced
git log <first-parent-sha>..<train-sha>

# Per shipped PR number
gh pr view <number> -R <org>/<repo> --json number,title,body,mergedAt,baseRefName,headRefName,author,url,labels

# PRs merged to the integration branch that have not shipped
gh pr list -R <org>/<repo> --state merged --base <integration_branch> --search "merged:>=<since_date>" --json number,title,url,mergedAt
```

The script never checks out or modifies a working tree. Every read is `git log` or `git rev-list` against `origin/<branch>` refs, plus `gh` API calls.

## What agents read

The script writes two files. **Read the `.md` digest, not the JSON.** A busy week's JSON runs well past 100 KB. The digest is a compact per-repo summary with obviously internal PRs collapsed to a title-only line. The JSON stays on disk as the audit trail. Grep it when a digest line needs a citation, a changelog excerpt needs full text, or a PR's labels or author need checking.

## Internal-PR classification

Every shipped PR gets `likely_internal` and `internal_reason`. A PR is internal when any of these hold:

- The title starts with `chore`, `ci`, `build`, `deps`, `test(s)`, `docs`, `refactor`, `style` or `perf`, with an optional `(scope)` before the `:`, `/` or space.
- The author is in `internal_authors`.
- A label is in `internal_labels`.
- The PR's `## Changelog` section is a placeholder (empty, only headings, or "No changelog").
- The title contains a phrase from `internal_title_keywords`.

This is a recall-oriented heuristic, not a judgment about newsworthiness. A real feature PR with a `fix` or `feat` title still appears as a candidate even when small.

## Running it

```bash
python3 skills/whats-new-weekly/scripts/collect_shipped.py \
  --config skills/whats-new-weekly/CONFIG.md --out /tmp/shipped.json
```

Flags: `--since` and `--until` (default: trailing 7 days, `YYYY-MM-DD` or ISO 8601), `--out` (JSON path, a summary prints either way), `--md` (digest path, default is the `--out` path with a `.md` extension), `--repos name,name` (subset), `--skip-fetch` (use refs already local).

## Digest shape

```
## web-app (The website, https://www.example.com)
Release trains: 3. Candidate PRs: 5. Filtered as internal: 4. Not yet in production: 2.

### Candidates
- #101 (shipped Sep 9) feat(profile): rebuild the profile page
  Changelog: Profile page - new header, tabs for Rewards and History ...

### Filtered as internal (titles only)
#98 chore(deps): bump next · #99 docs(changelog): pending entries

### Not yet in production (titles only)
#102 fix(search): handle empty query
```

A repo with zero trains and zero candidates gets one line: "Nothing reached production this week."
