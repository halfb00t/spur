---
phase: quick/260923-qwr
plan: 01
subsystem: api
tags: [gzip, fastapi, starlette, latency, admission-control]

requires:
  - phase: 02-cad-off-the-event-loop
    provides: "_build_slot() admission control, _EXPORTS byte cache, the E2c-diagnosing
      02-LATENCY-INVESTIGATION.md"
provides:
  - "_GZIP_LEVEL=1, measured against the real 9,062,784-byte STL, replacing Starlette's
    unmeasured compresslevel=9 default"
  - "model-body gzip compression moved inside _build_slot(), cached in _EXPORTS under an
    encoding-tagged key so a repeat download of a cached gear compresses zero times"
  - "bench/RESULTS.md Runs 5-6, the post-fix concurrent/single latency re-measurement"
affects: [02-cad-off-the-event-loop]

actuals:
  tokens: 4585
  tasks: 3
  commits: 3
  plan_head_before: "41715af8a0d19742a49f30970fc40e8366109533"

tech-stack:
  added: []
  patterns:
    - "Encoding-tagged cache key ((params, fmt, quality, encoding)): every content
       encoding of an exported blob is a first-class variant of the one byte-budgeted
       cache, not a bolted-on sidecar."
    - "Compression performed inside the same admission slot as the build it compresses,
       via run_in_threadpool, so cache-hit compression is bounded the same way a fresh
       build is."

key-files:
  created: []
  modified:
    - src/spur/app.py
    - tests/test_api.py
    - bench/RESULTS.md

key-decisions:
  - "_GZIP_LEVEL=1 (not 6 or 9): level 6 is only 8.7% smaller than level 1's output and
     level 9 only 8.66% smaller -- both miss the plan's 10% size-reduction bar decisively
     (not a near-tie), while costing 2.7x-12.4x the 10-concurrent wall time. STL triangle
     data is mostly non-repeating floats, so a slower zlib search buys almost nothing."
  - "Compress inside _build_slot(), cache the compressed bytes (chosen_design in the
     plan): the only way to make an admission bound apply to cache-hit compression,
     since GZipMiddleware compresses after the slot is already released."
  - "Runs 5-6 not retried after Run 6 came in at 2.10x (just over the 2.00x bar): the
     plan's own instruction is to report both runs as measured, not search for a pass."

requirements-completed: [REQ-cad-off-event-loop]

coverage:
  - id: D1
    description: "_GZIP_LEVEL set from a measured 1/6/9 table against the real 9 MB STL"
    verification:
      - kind: unit
        ref: "tests/test_api.py -- make verify's own \
              `.venv/bin/python -c \"from spur.app import _GZIP_LEVEL; ...\"` check"
        status: pass
    human_judgment: false
  - id: D2
    description: "gzip client gets Content-Encoding: gzip, identity client gets raw
      bytes, decoded gzip body equals identity body byte for byte"
    verification:
      - kind: unit
        ref: "tests/test_api.py::test_a_gzip_client_gets_compressed_bytes_an_identity_client_gets_the_raw_file"
        status: pass
    human_judgment: false
  - id: D3
    description: "a gear is compressed once per cache fill, not once per download"
    verification:
      - kind: unit
        ref: "tests/test_api.py::test_a_gear_is_compressed_once_per_cache_fill_not_once_per_download"
        status: pass
    human_judgment: false
  - id: D4
    description: "a cache hit that still needs compressing goes through admission
      control (503 busy when all slots are held)"
    verification:
      - kind: unit
        ref: "tests/test_api.py::test_a_cache_hit_that_still_needs_compressing_goes_through_admission_control"
        status: pass
    human_judgment: false
  - id: D5
    description: "an already-compressed download needs no slot at all"
    verification:
      - kind: unit
        ref: "tests/test_api.py::test_an_already_compressed_download_needs_no_slot_at_all"
        status: pass
    human_judgment: false
  - id: D6
    description: "concurrent scenario's under-load p95 <= 2.00x idle p95 on both post-fix
      runs"
    verification:
      - kind: other
        ref: "bench/RESULTS.md 'Post-fix re-run (Runs 5-6)' -- Run 5 1.31x, Run 6 2.10x"
        status: fail
    human_judgment: true
    rationale: "Real, measured ratios (Run 5 1.31x met, Run 6 2.10x not met) -- the human
      decides how to route the broken-windows ledger on this evidence, per the plan's own
      instruction not to flip it here."

duration: ~15min
completed: 2026-09-23
status: complete
---

# Quick Task 260923-qwr: Fix `/api/health` under-load latency (gzip cost) Summary

**Moved model-body gzip compression off Starlette's unbounded 9-default and inside the
build's own admission slot, cached the compressed bytes, and re-measured: the concurrent
scenario now passes on one of two runs (1.31x, 2.10x) instead of failing on all four
prior runs (2.02x, 2.45x, 2.32x, 2.35x).**

## Gzip level measurement (Task 1)

Measured `gzip.compress` (the function the shipped code now calls) against the real
9,062,784-byte STL for `teeth=199&quality=fine`, host loadavg 2.68/3.07/2.78 just before
measuring:

| level | single-threaded median | output bytes (% of input) | 10-concurrent wall (median of 3) |
|---|---|---|---|
| 1 | 51.5 ms | 2,632,467 (29.0%) | 74.4 ms |
| 6 | 147.9 ms | 2,403,312 (26.5%) | 198.9 ms |
| 9 | 788.0 ms | 2,404,371 (26.5%) | 925.5 ms |

Selection rule: adopt a higher level only if it shrinks output by >=10% **and** costs
<=1.5x the lower level's 10-concurrent wall time. Level 6 over level 1 is only 8.7%
smaller; level 9 over level 1 is only 8.66% smaller (and 12.4x the wall time) -- both
miss the 10% bar decisively, so level 1 was chosen with no ambiguity requiring a
stop-and-ask.

Cross-check: this run's level-9 output byte count (2,404,371) matches
`02-LATENCY-INVESTIGATION.md`'s figure exactly (same input); this run's level-9 timings
are ~34% faster than the investigation's, consistent with a quieter host this session.

**`_GZIP_LEVEL = 1`**

## Runs 5-6 latency re-measurement (Task 3)

`concurrent` scenario ratios, verbatim from the harness (`under-load p95 / idle p95`):

- **Run 5: 1.31x** (idle 0.6 ms n=3601, under-load 0.8 ms n=15432) -- loadavg samples
  `{4.64 4.37 3.53}` -> `{3.58 4.13 3.47}` -> `{2.73 3.88 3.40}`, 30 s apart, immediately
  before the two runs.
- **Run 6: 2.10x** (idle 0.6 ms n=3640, under-load 1.3 ms n=7769) -- same environment
  snapshot as Run 5 (both runs made against the same server in immediate succession, no
  restart, no re-run to search for a pass).

`single` scenario ratios:

- **Run 5: 1.10x** (idle 0.6 ms n=3666, under-load 0.7 ms n=5139).
- **Run 6: insufficient samples** -- `bench/latency.py`'s `MIN_SAMPLES` gate refused to
  report a p95 (`single/under-load has only 19 /api/health samples, need >= 20`); no
  ratio reported for Run 6's `single` scenario, per L08 (no guessed number).

**Was the <=2.00x bar met on both concurrent runs? NO.** Run 5 met it (1.31x); Run 6 did
not (2.10x). This is a real, measured improvement over the four prior failing runs
(2.02x, 2.45x, 2.32x, 2.35x), but not a demonstrated pass on both runs in this session.
Per `<hard_fact_10>`, `.planning/WINDOWS.md` item 1 was not touched -- the orchestrator
decides the ledger on this evidence.

## Task Commits

1. **Task 1: Measure gzip levels 1/6/9, set `_GZIP_LEVEL`** - `2d47994` (perf)
2. **Task 2: Compress inside `_build_slot()`, cache compressed bytes (4 tests)** - `7a61fad` (perf)
3. **Task 3: Re-measure with `make serve` + `bench.latency` twice, record Runs 5-6** - `013926e` (docs)

## Files Modified

- `src/spur/app.py` -- `_GZIP_LEVEL` constant + comment; `_gzip()` helper; `model()`
  endpoint reads `Accept-Encoding` itself, compresses inside `_build_slot()`, caches
  under an encoding-tagged `_EXPORTS` key; `_build_slot`'s and `health()`'s docstrings
  re-documented to say a slot now covers build plus first encode.
- `tests/test_api.py` -- 4 new behaviour tests (gzip-vs-identity byte equality,
  compress-once-per-cache-fill, cache-hit-goes-through-admission-control,
  already-compressed-needs-no-slot).
- `bench/RESULTS.md` -- `### Post-fix re-run (Runs 5-6)` subsection.

## Decisions Made

- `_GZIP_LEVEL = 1` -- see measurement table above; not a near-tie, no stop-and-ask
  needed.
- Compress inside `_build_slot()`, cache the result under `(params, fmt, quality,
  encoding)` -- the plan's chosen design (design A); the only way to make an admission
  bound apply to cache-hit compression, since `GZipMiddleware` compresses after the
  endpoint (and its slot) has already returned.
- Runs 5-6 reported as measured, Run 6's 2.10x not retried -- the plan's own instruction.

## Deviations from Plan

None - plan executed exactly as written. All three tasks' `<done>` criteria were met;
`make verify` was green at every commit.

## Issues Encountered

None beyond what the plan anticipated -- Run 6's `single` scenario hitting
`bench/latency.py`'s own `MIN_SAMPLES` gate is the harness behaving as designed (L08),
not a bug.

## Tech debt / ideas filed

None. Nothing discovered during this task warranted a new `docs/tech_debt/active/` or
`docs/ideas/` entry -- the open item (the `concurrent` scenario's <=2.00x bar not yet met
on both runs) is the pre-existing tracked item (`.planning/WINDOWS.md` item 1,
`STATE.md`'s "Blockers/Concerns"), which this task's evidence updates but does not
newly create.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

`REQ-cad-off-event-loop`'s `concurrent` acceptance clause is closer to demonstrated
(1.31x/2.10x vs the prior 2.02x-2.45x range) but not met on both runs this session. The
orchestrator decides, on this evidence, whether to flip `.planning/WINDOWS.md` item 1 and
resume `/gsd-execute-phase 2` for `02-05`, or call for a further re-run/decision first.

---
*Quick task: 260923-qwr*
*Completed: 2026-09-23*

## Self-Check: PASSED

- FOUND: src/spur/app.py (modified, contains `_GZIP_LEVEL`, `_gzip`, updated `model()`)
- FOUND: tests/test_api.py (modified, contains the 4 new test functions)
- FOUND: bench/RESULTS.md (modified, contains `### Post-fix re-run (Runs 5-6)`)
- FOUND commit 2d47994 (`git log --oneline --all | grep 2d47994`)
- FOUND commit 7a61fad (`git log --oneline --all | grep 7a61fad`)
- FOUND commit 013926e (`git log --oneline --all | grep 013926e`)
- CONFIRMED: `make verify` green at final state (ruff, mypy --strict, lint-imports, no-fake-done, 71 passed)
- CONFIRMED: `lsof -i :8001` empty (server stopped); `spur-spur-1` untouched
- CONFIRMED: `.planning/WINDOWS.md` unmodified (`git status --short .planning/WINDOWS.md` empty)
