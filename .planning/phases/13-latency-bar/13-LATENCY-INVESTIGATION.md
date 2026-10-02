---
phase: 13-latency-bar
plan: 03
type: investigation
status: pre-registered
date: 2026-10-02
---

# Why does the second run of a pair read worse, and is the 2.00x verdict read at the harness's floor?

## Question

`docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` left two observations
unexplained across eight runs over four sessions (pre-fix 2.02x/2.45x and 2.32x/2.35x;
post-fix 1.31x/2.10x and 1.86x/2.02x):

1. Every second run of a pair -- the one inheriting the first run's `_EXPORTS` -- is worse
   than its first, before and after the fix (2.02 -> 2.45, 2.32 -> 2.35, 1.31 -> 2.10,
   1.86 -> 2.02). Post-fix those cache hits do no compression and take no slot
   (`tests/test_api.py::test_an_already_compressed_download_needs_no_slot_at_all`), so it
   is not the mechanism the fix removed. Candidates neither ruled in nor out: four instant
   ~2.6 MB sends from the loop thread at t=0; worker-side state after the first batch; a
   shorter load window (n=7719 vs n=10527) read at the floor.
2. The verdict sits at the harness's resolution floor: idle p95 is 0.6 ms in six of the
   eight runs, so the bar is about 1.2 ms of under-load p95, and passes and misses are
   separated by roughly 0.1 ms.

The three candidates for observation 1, verbatim from the debt file: "four instant
~2.6 MB sends from the loop thread at t=0; worker-side state after the first batch; a
shorter load window (n=7719 vs n=10527) read at the floor."

H1 re-check: does the split-process poller still track the in-process one post-fix, as
02's E1 found pre-fix (H1 refuted pre-fix: split 5.99x/1.48x vs in-process 7.06x/1.55x)?

## Environment

Machine: 12 CPUs, arm64, 32.0 GiB RAM (`.venv/bin/python -c "from bench import
machine_facts; print(machine_facts())"`). The commit under test is each run's own `head`
field in its `summary.json` -- `run_experiment.py` reads `git rev-parse HEAD` itself at
run time, not a value fixed here.

The server is started by `session.py::_start_server`: every inherited `SPUR_*` environment
variable is removed first, then only `SPUR_PORT=8001` is set, so every other `SPUR_*`
value is the shipping default (`SPUR_BUILD_WORKERS=2`, `MAX_QUEUED_BUILDS=4`,
`SPUR_BUILD_TIMEOUT=30`).

`fleet-user` (unrelated, restart-looping every ~40 s beside Runs 1–8) was stopped for this
session; `spur-spur-1` left running.

This is an environment change relative to Runs 1-8 (`fleet-user` was up and
restart-looping throughout every recorded run); a pass in this investigation is not read
as explaining the recorded misses on the original, noisier environment (D-06).

| Session | Released (UTC) | 1-min load at release (three samples) | Decisive | Top CPU | Load after |
|---|---|---|---|---|---|

## Method

- **`poller.py`** -- its own OS process, its own `httpx.Client`, `time.monotonic()`
  timestamps (cross-process comparable with no clock-sync step), a `--stop-file` it polls
  after every sample, and a line-flushed JSONL (`{"t", "latency_s"}` keys per line) so an
  orphaned poller still leaves honest partial data.
- **`run_experiment.py`** -- imports `bench.latency`'s own sampling functions
  (`_sample_for`, `_sample_while_building`, `_build`, `_collect`, `_p95`, `MIN_SAMPLES`,
  `SETTLE_SECONDS`, `ScenarioResult`, `_report_markdown`) unmodified, and copies
  `scenario_single`/`scenario_concurrent`'s bodies line for line (`bench/latency.py:
  123-132, 135-146`), adding only the teeth range's first tooth (`--teeth-start`, so
  Pair B's `range(180, 190)` can run without a `bench/` change) and three
  `time.monotonic()` stamps (`t_start`, `t_builds_start`, `t_builds_done`) per scenario
  for the poller/in-process segmentation.
- **Segmentation rule** (`run_experiment.py::_segment_poller_samples`): idle is
  `t_start <= t < t_builds_start`; under-load is `t_builds_start <= t <= t_builds_done`.
- **Statistics** (`run_experiment.py::series_stats`, `ratio_block`): p95 by
  `bench.latency._p95` (`statistics.quantiles(samples, n=20)[-1]`); p94/p96 by
  `statistics.quantiles(samples, n=100)`, refused below 100 samples; any series under
  `MIN_SAMPLES` (20) is refused, never guessed (L08). The verdict is decided on raw
  floats, pass iff ratio `<= 2.0`, ratios printed to 3 dp. The four one-percentile
  alternatives (`u94_i95`, `u96_i95`, `u95_i94`, `u95_i96`) and the `flips` flag record
  whether any alternative lands on the other side of 2.0 from the reported ratio (D-02).
- **Floor analysis**: each series' `min_gap_s` (smallest positive gap between distinct
  sorted values) and `ties` (sample count minus distinct-value count) are read against
  the declared clock resolution (`time.get_clock_info("perf_counter").resolution`,
  4.1667e-08 s on this host -- 13-01 Flagged Assumption A3) to tell "samples at the
  timer's quantum" from ordinary variance.
- **Run order**: Task 1's answer (harness order, see below) and its `--order` value,
  `concurrent,single` -- `run_experiment.py`'s own default, matching
  `bench.latency.main()`'s own `sorted()` order with no scenario argument.
- **The pairs**: Pair A -- same server, both runs teeth 190-199; Pair B -- same server,
  run 2 teeth 180-189 (cold export cache, warm workers); Pair C -- server restart between
  the runs. Each pair runs twice. Session order: A1, B1, C1, A2, B2, C2, one session at a
  time, nothing else CPU-heavy started during a session (no commit, no `make verify`
  while a session runs).
- **The D-05 quiet gate** (`session.py`): release only after three consecutive 30 s
  samples of 1-minute `sysctl -n vm.loadavg` under 1.5, capped at 900 s. A session that
  never reaches three quiet samples still runs, is recorded as measured, and is marked
  non-decisive -- it counts for the investigation and for the record, never for outcome
  (a) (D-05).
- **Port and records**: port 8001 with the listener-PID check (`session.py::_start_server`
  confirms the 8001 listener really is the child it started, never trusting that
  *something* answered); server access lines (`logger == "uvicorn.access"`) are dropped
  when the server stops, every other record line is kept (`session.py::_stop_server`).
- **The tracer runs** (`tracer-run1`, `tracer-C`, committed in 13-01) proved the harness
  end to end before this pre-registration and are not evidence -- their own numbers are
  never cited in Results or Verdict.

## Predictions

Definitions: a run's ratio is its in-process concurrent under-load p95 / idle p95, on raw
floats. In one session, run 2 "reads worse" iff its ratio is strictly greater than run
1's. A pair "points worse" when both repetitions read worse, "points not worse" when
neither does, and is "split" otherwise -- a split pair is "not separable on this host"
and rules nothing in or out (D-04).

| Candidate | Pair A | Pair B | Pair C | Also predicts |
|---|---|---|---|---|
| (1) cache-hit sends | worse | not worse | not worse | run 2 refuses fewer than run 1 in Pair A (cached teeth bypass admission); the Pair A worsening is larger than a one-percentile move (flips false on run 2) |
| (2) worker state | worse | worse | not worse | Pair B worse although no run-2 request is a cache hit |
| (3) window at the floor | worse | not worse | not worse | run 2's under-load n below run 1's in Pair A, and run 2's verdict flips inside one percentile; Pairs B and C restore n |

Ruling rule: a candidate is ruled out when any pair it predicts worse points not worse, or
any pair it predicts not worse points worse; a candidate is ruled in when every one of its
pair predictions and its "also predicts" column holds in both repetitions and every other
candidate is ruled out; when two candidates survive, the write-up states which measurement
would separate them and names both. If Pair A does not point worse, observation 1 is not
reproduced in this environment (D-06's change named), and Pairs B and C cannot rule
anything in or out.

H1 re-check: in every session the split poller's run-2-vs-run-1 direction equals the
in-process direction; H1 is revived only if they disagree in both repetitions of a pair.

Observation 2: (i) print resolution -- no concurrent run's verdict flips inside one
percentile, so "0.1 ms apart" in the record is the `:.1f` print, not the samples; (ii) the
floor is real -- at least one concurrent run's verdict flips inside one percentile; (iii)
sample count -- the runs that flip are exactly runs whose under-load n is below the
median n of the twelve. D-09's first offers follow: (i) no threshold change for
observation 2; (ii) D-10's absolute floor; (iii) a higher `MIN_SAMPLES`. Observation 1
ruled to (1) or (2), or split between them: D-09's first offer is a server restart between
runs; ruled to (3): it joins observation 2's offer.

## Results

## Verdict

## Recommendation

## Cleanup
