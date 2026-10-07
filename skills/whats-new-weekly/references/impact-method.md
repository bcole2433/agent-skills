# Impact method

Static method for the impact agent (Phase 1) and the orchestrator (Phase 2, impact section). Read it in full before querying anything.

## The causation bar

A metric counts as **attributable** only when all four hold:

1. It moved beyond normal week-to-week noise, not a single-day blip.
2. The movement starts at or after the launch date, not before.
3. The affected surface or event is the one the feature actually touches, not an adjacent or aggregate metric.
4. The known confounders in the lessons file and the baselines file do not explain it.

If any of the four fails, the metric is **moved but not attributable** (it moved, but a confounder is plausible or the timing does not line up) or **no movement**. Never round "moved but not attributable" up to attributable because the direction is convenient.

## Order of sources

1. The latest analytics digest (if `ANALYTICS_DIGEST_PATH` is set) read as text, plus the baselines file. Never open an HTML report itself. Most questions are already answered here.
2. `impact-tracking.md` for the specific metrics tied to each tracked feature.
3. The analytics CLI directly, only for gaps the first two do not cover, at most `MAX_ANALYTICS_QUERIES` per run. On a run where `impact-tracking.md` has no rows, skip querying entirely and only propose watch metrics from event names already in the baselines file.

For confounders, grep the lessons file for the specific term (the confounder name, the event name) and read only the matching paragraphs. The file is large and mostly irrelevant to any one question.

## Analytics CLI bootstrap

Before the first query in a run:

1. Load your analytics tool's agent or help guide as instructions, only once you know a query is needed. Its output is long, so do not run it speculatively.
2. Check whether the tool has an installable skill for this task and read it.
3. Verify an event exists in the schema before querying it. Never assume an event name.
4. Always put an explicit `LIMIT` on every query.

If your analytics tool has quirks (several SDK sources in one project, per-platform event naming drift), record them in the lessons file and check it before assuming two similarly named events are the same, or different.

## Comparison window rule

Default is `COMPARE_WINDOW_DAYS` after the launch date versus the same number immediately before. When a high-activity day falls inside one window and not the other, compare against the same weekday mix too, and treat any lift as suspect until that effect is accounted for.

## Confounder checklist

Check each item in `CONFOUNDERS` against the launch and comparison dates before calling anything attributable. Common ones:

- Peak-traffic events (a game day, a sale, a product launch).
- Seasonal changes in the business calendar.
- Deadlines that cluster activity just before them.
- Outages and catch-up bursts (a recovery day can inflate its own window and distort the next comparison).
- Mobile release timing (adoption lags the code landing until enough users update).
- Marketing sends (an email or push blast can produce a spike unrelated to the feature).

## Row format for impact-tracking.md

```
| Feature | Launched | Surface | Metric or event | Baseline | Latest | Verdict | Notes |
```

- **Feature:** plain-language name, matching what was published.
- **Launched:** the date it went live.
- **Surface:** web, iOS, Android, or whichever the feature touches.
- **Metric or event:** the actual event or insight name, never invented, or "no instrumentation" if none exists.
- **Baseline:** the trailing value before launch.
- **Latest:** the current value.
- **Verdict:** `watching` (too soon), `signal` (moved, not yet confirmed attributable), `no signal` (no movement or not attributable), `retired` (`RETIRE_AFTER_WEEKS` or more with no signal).
- **Notes:** one line, the confounder check or the reason for the verdict.

## Proposing watch metrics for new launches

For each new candidate, propose 1 to 2 existing events or insights to watch:

- Pick events that already exist and are known healthy. Never invent an event name that has not been verified against the schema.
- Name the surface whose event to trust if the feature touches a platform with a known naming split.
- If nothing in the taxonomy captures the feature's effect, write "no instrumentation" so the run report can flag it for an instrumentation request.
