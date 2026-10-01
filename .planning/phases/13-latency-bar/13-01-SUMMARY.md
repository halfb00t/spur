---
phase: 13-latency-bar
plan: 01
subsystem: testing
tags: [latency, bench, httpx, investigation-harness, bisection-free-measurement]

requires:
  - phase: 02-cad-off-the-event-loop
    provides: "bench/latency.py's own sampling functions and scenarios (_sample_for, _sample_while_building, _build, _collect, _p95, _report_markdown, scenario_single, scenario_concurrent) -- imported unmodified, never reimplemented"
provides:
  - "poller.py: a split-process /api/health poller (own OS process, own GIL, own httpx.Client, time.monotonic() timestamps, --stop-file, line-flushed JSONL)"
  - "run_experiment.py: one run -- poller.py beside an in-process mirror of bench.latency's own scenarios, imported unmodified; series_stats and ratio_block, the one definition of every number this phase prints"
  - "session.py: one quiet-gated session -- preflight (lock, port, src/bench clean, fleet-user state), D-05's quiet wait, server lifecycle (start/stop, PID-verified, access-log collapse), pair and bar modes"
  - "tabulate.py: --self-check (9 boundary/adjacency/empty/precision cases), --check (recompute-from-raw-JSONL verification), --tables, --sessions"
  - "two proven tracer runs (tracer-run1, tracer-C) with their raw JSONL, summaries, and session status committed as the instrument's own proof -- their numbers are not evidence and are never cited"
affects: [13-02, 13-03, 13-04, 13-05, 13-06]

actuals:
  tokens: 11810
  tasks: 2
  commits: 2
  plan_head_before: b524ed274fe553c42e823554302acf1bf3430f3c
  plan_head_after: b55d3edf7463b2c65a3da291b1b24e2922c45d88

tech-stack:
  added: []
  patterns:
    - "Split-process poller + imported-unmodified in-process mirror (02's own investigation shape, rebuilt from 02-LATENCY-INVESTIGATION.md's Method section since 02's scripts are gone)"
    - "Atomic status.json rewrite (temp file + rename) at every session state change"
    - "Never overwrite an existing output path -- refuse and exit non-zero instead (poller.py, run_experiment.py, and, after a same-session fix, session.py)"

key-files:
  created:
    - .planning/phases/13-latency-bar/investigation/poller.py
    - .planning/phases/13-latency-bar/investigation/run_experiment.py
    - .planning/phases/13-latency-bar/investigation/session.py
    - .planning/phases/13-latency-bar/investigation/tabulate.py
  modified: []

key-decisions:
  - "Order default kept as concurrent,single (bench.latency.main()'s own sorted() order with no scenario argument) rather than D-08's literal 'single then concurrent' -- both scripts take --order so 13-02 Task 1's checkpoint can settle A1 without a code change either way."
  - "poller.py and run_experiment.py use `with` context managers for their output file and httpx.Client instead of a literal try/finally -- same always-closed guarantee the plan's try/finally wording asks for, and satisfies ruff's SIM115 (use a context manager for an opened file) without weakening the 02 try/finally lesson."
  - "session.py's own-label existing-files preflight check was found, during Task 2's own proof, to overwrite the very status.json it was refusing to disturb (abort() always rewrites status_path). Fixed in the same commit: that one preflight branch now prints to stderr and exits non-zero without touching any file for the label, matching run_experiment.py/poller.py's own refuse-not-overwrite behavior and E7."

patterns-established:
  - "series_stats/ratio_block in run_experiment.py are the one definition of every percentile, ratio, verdict and alternative this phase computes -- tabulate.py imports them rather than recomputing differently, and later plans (13-02 onward) are expected to do the same."

requirements-completed: [REQ-latency-observations-explained]

duration: ~22min
completed: 2026-10-01
status: complete
---

# Phase 13 Plan 01: Investigation Harness Summary

Built and proved end to end the four-script instrument the rest of Phase 13's investigation runs on: a split-process `/api/health` poller, a per-run harness that reuses `bench.latency` unmodified, a quiet-gated session driver that starts and owns its own port-8001 server, and a tabulator that recomputes every number from raw samples -- nothing under `src/` or `bench/` changed.

## Performance

- **Duration:** ~22 min (reconstructed from file/commit timestamps; `PLAN_START_TIME` was not captured with a literal `date` call at session start)
- **Completed:** 2026-10-01T23:09:46+06:00 (`b55d3ed`'s commit time)
- **Tasks:** 2/2
- **Files modified:** 4 scripts + 20 raw-output files (poller/inproc JSONL, summaries, session status/log, server records, stdout/stderr captures)

## Accomplishments

- `poller.py` and `run_experiment.py` built, proven by one real tracer run (`tracer-run1`) against a server this task started and stopped on port 8001 -- poller + in-process harness → JSONL → summary, with `run_experiment.py --self-check`-style recompute confirmed via `tabulate.py --check`.
- `session.py` (D-05 quiet gate, D-06 host preflight, server lifecycle) and `tabulate.py` (self-check, check, tables, sessions) built, proven by a detached Pair-C-shaped tracer session (`tracer-C`) that exercised the server-restart path: two server starts, two runs, two `.records.jsonl` files, no full server log left behind, and the session lock released.
- A real bug found during Task 2's own proof -- `session.py`'s existing-files preflight check overwrote the very `status.json` it was supposed to protect -- was fixed in the same commit (Rule 1), re-verified, and did not require re-running the tracer session.

## Task Commits

1. **Task 1: Tracer -- one run end to end: own-process poller beside the in-process harness, JSONL and summary** - `ea4c039` (chore)
2. **Task 2: Session driver (D-05 quiet gate, D-06 preflight, server lifecycle) and the tabulator, proven by a Pair-C-shaped tracer session** - `b55d3ed` (chore)

**Plan metadata:** (this commit, immediately following)

## Files Created/Modified

- `.planning/phases/13-latency-bar/investigation/poller.py` - split-process `/api/health` poller; `--base-url`/`--out`/`--stop-file`, refuses an existing `--out` path, writes `{"t", "latency_s"}` JSON lines, line-flushed
- `.planning/phases/13-latency-bar/investigation/run_experiment.py` - one run: launches `poller.py`, runs `concurrent_run`/`single_run` (line-for-line copies of `bench.latency`'s own scenario bodies with three `monotonic()` stamps added), `series_stats`/`ratio_block` (the one definition of every number), writes `<label>.poller.jsonl`/`.inproc.jsonl`/`.summary.json`
- `.planning/phases/13-latency-bar/investigation/session.py` - one quiet-gated session: preflight (existing files, lock, `src`/`bench` clean, port 8001 free, `fleet-user` state), D-05's quiet wait (three consecutive under-1.5 samples or a bounded cap), server lifecycle (start/verify-PID/stop/collapse-access-log), `pair` and `bar` modes, `status.json` rewritten atomically
- `.planning/phases/13-latency-bar/investigation/tabulate.py` - `--self-check` (9 cases: E1/E2/E3/E6), `--check` (recompute from raw JSONL vs. committed summary), `--tables`, `--sessions`
- 20 raw-output files (`tracer-run1.*`, `tracer-C*`) -- the instrument's own proof, not evidence for the investigation itself

## Decisions Made

- **Order default:** kept `concurrent,single` (matching `bench.latency.main()`'s own `sorted()` order with no scenario argument), not D-08's literal "single then concurrent" -- both scripts expose `--order` so 13-02 Task 1's checkpoint resolves A1 without a code change either way.
- **`with` over literal `try/finally`:** `poller.py`'s output file and `httpx.Client`, and `run_experiment.py`'s per-scenario `httpx.Client`, use context managers rather than an explicit `try/finally` block. The guarantee (always closed, even on an exception) is identical to what the plan's prose asked for, and this form is what satisfies ruff's `SIM115` without reintroducing 02's own corrupted-JSONL failure mode.
- **Session preflight bug, fixed in-commit:** `session.py`'s "does a file for this label already exist" check originally called the same `abort()` helper every other preflight failure uses, which unconditionally rewrites `status.json` -- including a prior, already-`done` run's own status file, the exact overwrite the project's "never appended to or overwritten" rule (E7, T-13-02) forbids. Fixed by making that one branch print to stderr and exit non-zero without touching any file for the label. Verified by directory-listing checksum before/after a repeat `tracer-C` launch: identical.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `session.py`'s existing-files preflight overwrote its own prior status.json**
- **Found during:** Task 2, while proving the "re-launching the same label aborts and creates no new files" acceptance criterion
- **Issue:** The preflight check for "files already exist under this label" called `abort()`, which unconditionally calls `_atomic_write_json(status_path, status)` -- clobbering `tracer-C.status.json`'s `state: "done"` with `state: "aborted"` the moment the check ran a second time, destroying the record of the completed tracer session.
- **Fix:** That one preflight branch now prints an error to stderr and returns `2` directly, without constructing or writing a status dict at all -- mirroring `run_experiment.py`/`poller.py`'s own refuse-before-writing-anything behavior.
- **Files modified:** `.planning/phases/13-latency-bar/investigation/session.py`
- **Verification:** Restored `tracer-C.status.json`/`tracer-C.session.log` to their correct post-run content (captured in full before the bug manifested), re-ran the fixed script against the same label: exit code 2, error message naming all 15 existing files, directory-listing checksum unchanged before/after, `tracer-C.status.json` still reads `state: "done"`.
- **Committed in:** `b55d3ed` (part of Task 2's commit)

---

**Total deviations:** 1 auto-fixed (1 Rule 1 bug).
**Impact on plan:** The fix is scoped to one preflight branch in a script this plan itself introduces; no `src/` or `bench/` file was touched, and the fix was verified before committing rather than deferred. No scope creep.

## Issues Encountered

None beyond the deviation above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

The four scripts are proven end to end (one tracer run, one detached tracer session exercising the server-restart path) and committed. 13-02 can now write predictions and run the twelve-run campaign through `session.py --mode pair` without building anything new; its Task 1 checkpoint should resolve A1 (the `--order` default) before the first real pair runs. The measured tracer footprint (`tracer-run1.poller.jsonl`: 21,954 samples / 1,329,832 bytes, ~60.6 bytes/sample) is close to planning's ~1.4 MB/22,000-sample estimate (A4) -- 13-03's campaign of twelve such runs should budget on the order of 25-40 MB raw, consistent with A4's working-tree estimate.

No blockers. `tracer-run1`'s and `tracer-C`'s own numbers are not evidence and must not be cited in `13-LATENCY-INVESTIGATION.md`.

---
*Phase: 13-latency-bar*
*Completed: 2026-10-01*

## Self-Check: PASSED

All four created scripts found on disk; both task commits (`ea4c039`, `b55d3ed`) found in `git log --oneline --all`.
