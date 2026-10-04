# gsd's 30 s commit timeout kills the pre-commit `make verify` hook on a cold cache

Severity: nice
Status: active
Date: 2026-09-25
Source: `/gsd-new-milestone` session starting v0.2 (the first `gsd_run query commit` of the session)
Related files:
- `.pre-commit-config.yaml` (the `verify` hook: ~64 s warm, "a couple of minutes" cold)
- `~/.claude/gsd-core/bin/lib/commands.cjs:3655` — `COMMIT_TIMEOUT_MS = 30_000`, hard-coded, outside this repo
- `~/.claude/gsd-core/agents/gsd-executor.md:837` — the executor's `commit_timeout` retry rule

## Context
gsd's SDK commit (`gsd_run query commit …`) runs `git commit` under a hard-coded 30 s
timeout with no config knob (`.planning/config.json` has none; `references/planning-config.md`
lists none). This repo's pre-commit hook runs `make verify`, which is ~64 s warm (`-n 8` with
coverage, bench/RESULTS.md, Phase 15) and takes minutes on the first run after the
OpenCascade pages have been evicted. Observed today: the
session's first SDK commit returned `{committed: false, reason: 'commit_timeout'}` — killed
mid-hook, nothing committed, no stale `index.lock` in that instance. A direct `git commit`
with the hook allowed to finish passed; every later commit in the session (research,
requirements, roadmap) was made the same way and each passed the hook. Phase 15 timed a
whole commit (the `make verify` hook plus commit-msg) at 63-64 s by `date`
(`.planning/phases/15-the-gate-measured-and-pinned/15-04-SUMMARY.md`), so a warm run is
itself over the 30 s limit now, not only a cold one.

## Why it matters
Every gsd workflow that commits — `execute-phase` executors, `complete-milestone`,
`new-milestone` — hits this on the first cold commit of a session. The executor's documented
recovery (verify no git process, remove the lock the error names, retry once) works because
the retry runs warm, so the cost is one wasted `make verify` per session and a window for a
stale `index.lock` if the kill lands mid-write. Unverified: whether the killed hook's `pytest`
keeps running orphaned and overlaps the retry.

## Next step
Warm the cache before the first commit of a session (`make verify` once, e.g. at the start of
`/gsd-execute-phase`), and raise upstream that `COMMIT_TIMEOUT_MS` should be configurable
(the SDK already special-cases the failure as #3886). Revisit when gsd exposes a
commit-timeout setting, or when an executor's warm retry also times out.
