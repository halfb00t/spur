# gsd's 30 s commit timeout kills the pre-commit `make verify` hook, warm or cold

Severity: must
Status: resolved
Date: 2026-09-25
Resolved in: build(gate): run make verify.fast at commit and make verify at push (L36)
Source: `/gsd-new-milestone` session starting v0.2 (the first `gsd_run query commit` of the session)
Related files:
- `.pre-commit-config.yaml` (the `verify` hook: ~64 s warm, "a couple of minutes" cold; now at pre-push, the commit stage runs `verify-fast`)
- `Makefile` (`verify.static`, `verify.fast`, `test.fast`, `$(HOOKS)`)
- `~/.claude/gsd-core/bin/lib/commands.cjs` — `COMMIT_TIMEOUT_MS = 30_000` (gsd-core 1.16.0; cite the symbol, lines drift), hard-coded, outside this repo
- `~/.claude/gsd-core/agents/gsd-executor.md` — the `commit_timeout` bullet, the executor's retry rule

File name kept (`bench/RESULTS.md` and `.planning/` link it) though the title no longer says
"cold": retitled and raised to `must` on 2026-10-06, 15-REVIEW WR-03.

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
`new-milestone` — hits this on every SDK commit, not only the first cold one of a session: a
warm hook runs ~64 s, twice the 30 s limit. The executor's documented recovery (verify no git
process, remove the lock the error names, retry once) assumed the retry runs warm and passes;
it cannot now, so the recovery is a second kill. In practice every close-out commit of v0.3
and one UAT commit were made by hand with a plain `git commit` (`.planning/RETROSPECTIVE.md`,
v0.3 "What Was Inefficient"), outside the SDK's state tracking, and a kill that lands
mid-write can leave a stale `index.lock`. Unverified: whether the killed hook's `pytest`
keeps running orphaned and overlaps the retry. The trigger this file named — a warm retry
also timing out — fired the day L34 measured the warm hook at 63-64 s; a deferred item whose
trigger has fired is `must`.

## Next step
Decide, and log the choice as an `Lxx`, between: (a) raising upstream that `COMMIT_TIMEOUT_MS`
be configurable (the SDK already special-cases the failure as #3886) and committing by hand
until then; (b) moving `make verify` from the pre-commit hook to a pre-push hook, keeping CI
and `make pr.land` as the wall — a change to L13's "one definition of passing in three
places" that needs its own entry; (c) a sub-30 s pre-commit subset (lint, types, boundaries,
scan; pytest left to pre-push and CI), priced from the Phase 15 profile. Revisit no later
than the next milestone's first executor commit, or when gsd exposes a commit-timeout
setting.

## Resolution (2026-10-06)
Option (b)+(c) taken, logged as L36: the commit stage runs `make verify.fast`, the whole
`make verify` runs at pre-push, and CI, the `main` ruleset and `make pr.land` stay the wall.
`verify` and `verify.fast` share one `verify.static` prefix, and `test.fast` is the gate's
own pytest recipe over every test file but tests/test_model.py, tests/test_pool.py,
tests/test_api.py and tests/test_cli.py at `-n 8 --no-cov`, so the commit stage is a named
prefix of the gate and not a second list (tests/test_hooks.py pins it). The Makefile's
`$(HOOKS)` stamp installs the three hook types from the main checkout. Re-priced on
2026-10-06, `make verify.fast` read 11.28, 11.30 and 11.28 s warm and 19.94 s with an empty
mypy cache, every one under the 30.0 s kill.

"Unverified: whether the killed hook's `pytest` keeps running orphaned" is answered: it does
(PITFALLS 15, git 2.54.0, Node `spawnSync`): the killed `git commit` leaves nothing committed
and no `index.lock`, and the hook runs to completion with parent PID 1. The recovery that
replaces the executor's retry is D-07: wait until `pgrep` finds no hook process, then make
exactly one plain `git commit` (docs/HOW_TO_DEVELOP.md §4, L36). The live SDK-commit proof is
17-02's; the upstream request for a configurable `COMMIT_TIMEOUT_MS` is D-08, also 17-02.
