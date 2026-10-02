---
phase: 13-latency-bar
plan: 03
type: investigation
status: complete
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
| A1 | 2026-10-02T02:37:53.913Z | 1.49, 1.34, 1.15 | yes | Telegram 5.3% | 2.23 |
| B1 | 2026-10-02T02:41:40.765Z | 1.31, 1.14, 1.02 | yes | Telegram 4.2% | 2.17 |
| C1 | 2026-10-02T02:48:51.582Z | 1.38, 1.34, 1.41 | yes | iTerm2 7.5% | 2.33 |
| A2 | 2026-10-02T02:53:10.129Z | 1.46, 1.35, 1.29 | yes | iStat Menus Menubar 11.6% | 3.06 |
| B2 | 2026-10-02T03:06:22.211Z | 1.19, 1.18, 1.34 | yes | iTerm2 5.7% | 2.36 |
| C2 | 2026-10-02T03:11:05.906Z | 1.40, 1.39, 1.23 | yes | OrbStack Helper 10.8% | 4.83 |

All six sessions released decisively (three consecutive 30 s samples under 1.5 within the
900 s cap); none hit the cap. No session aborted; no retry was needed. Every session's
`host.docker_ps` read `spur-spur-1 Up ... (healthy)` and `fleet-user Exited (2) ...` --
unchanged from the pre-phase state recorded in 13-02. Commit under test throughout:
`aff8f68` (`git rev-parse --short HEAD`, recorded in each session's own `status.json`).

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

Every table below is `tabulate.py --tables`/`--sessions` output over the six committed
sessions' raw files (`git log -1 --format=%h` at write-up time: `a24cb93`), pasted, never
retyped (L08). `tabulate.py --check` recomputed all twelve runs clean before this section
was written (Task 1's verify).

### Pair A -- same server, teeth 190-199

## A1-run1 (head aff8f688aba95319cf073341f2a290590380106e, 12 CPUs, arm64, 32.0 GiB RAM)

| Scenario | Source | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|---|
| concurrent | inproc | 0.760 ms (n=2945) | 1.008 ms (n=17543) | 1.327x (pass) | 14.29 s | 6 |
| concurrent | poller | 0.758 ms (n=2942) | 0.889 ms (n=18919) | 1.174x (pass) | 14.29 s | 6 |
| single | inproc | 0.734 ms (n=3012) | 0.811 ms (n=4327) | 1.105x (pass) | 3.07 s | 0 |
| single | poller | 0.739 ms (n=3007) | 0.803 ms (n=4303) | 1.086x (pass) | 3.07 s | 0 |

### Floor analysis

| Scenario | Source | Series | p94 (ms) | p95 (ms) | p96 (ms) | min gap (us) | ties |
|---|---|---|---|---|---|---|---|
| concurrent | inproc | idle | 0.753 | 0.760 ms | 0.773 | 0.00 | 494 |
| concurrent | inproc | under_load | 0.989 | 1.008 ms | 1.042 | 0.00 | 5430 |
| concurrent | poller | idle | 0.751 | 0.758 ms | 0.767 | 0.00 | 430 |
| concurrent | poller | under_load | 0.861 | 0.889 ms | 0.927 | 0.00 | 7904 |
| single | inproc | idle | 0.729 | 0.734 ms | 0.746 | 0.00 | 517 |
| single | inproc | under_load | 0.797 | 0.811 ms | 0.833 | 0.00 | 777 |
| single | poller | idle | 0.731 | 0.739 ms | 0.749 | 0.00 | 485 |
| single | poller | under_load | 0.787 | 0.803 ms | 0.830 | 0.00 | 762 |

Clock resolution: 41.7 ns

## A1-run2 (head aff8f688aba95319cf073341f2a290590380106e, 12 CPUs, arm64, 32.0 GiB RAM)

| Scenario | Source | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|---|
| concurrent | inproc | 0.767 ms (n=2921) | 1.488 ms (n=8901) | 1.940x (pass) | 8.51 s | 2 |
| concurrent | poller | 0.763 ms (n=2919) | 1.179 ms (n=10229) | 1.546x (pass) | 8.51 s | 2 |
| single | inproc | 0.770 ms (n=2954) | insufficient (n=14) | -- | 0.01 s | 0 |
| single | poller | 0.767 ms (n=2938) | insufficient (n=16) | -- | 0.01 s | 0 |

### Floor analysis

| Scenario | Source | Series | p94 (ms) | p95 (ms) | p96 (ms) | min gap (us) | ties |
|---|---|---|---|---|---|---|---|
| concurrent | inproc | idle | 0.762 | 0.767 ms | 0.777 | 0.00 | 411 |
| concurrent | inproc | under_load | 1.383 | 1.488 ms | 1.577 | 0.00 | 1361 |
| concurrent | poller | idle | 0.755 | 0.763 ms | 0.770 | 0.00 | 391 |
| concurrent | poller | under_load | 1.130 | 1.179 ms | 1.250 | 0.00 | 2422 |
| single | inproc | idle | 0.758 | 0.770 ms | 0.781 | 0.00 | 529 |
| single | inproc | under_load | -- | insufficient | -- | 0.92 | 0 |
| single | poller | idle | 0.758 | 0.767 ms | 0.779 | 0.00 | 454 |
| single | poller | under_load | -- | insufficient | -- | 1.71 | 0 |

Clock resolution: 41.7 ns

## A2-run1 (head aff8f688aba95319cf073341f2a290590380106e, 12 CPUs, arm64, 32.0 GiB RAM)

| Scenario | Source | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|---|
| concurrent | inproc | 0.751 ms (n=2950) | 1.424 ms (n=8657) | 1.896x (pass) | 8.44 s | 6 |
| concurrent | poller | 0.757 ms (n=2949) | 1.231 ms (n=9989) | 1.627x (pass) | 8.44 s | 6 |
| single | inproc | 0.744 ms (n=2962) | 0.822 ms (n=4335) | 1.104x (pass) | 3.10 s | 0 |
| single | poller | 0.754 ms (n=2955) | 0.828 ms (n=4285) | 1.097x (pass) | 3.10 s | 0 |

### Floor analysis

| Scenario | Source | Series | p94 (ms) | p95 (ms) | p96 (ms) | min gap (us) | ties |
|---|---|---|---|---|---|---|---|
| concurrent | inproc | idle | 0.745 | 0.751 ms | 0.759 | 0.00 | 518 |
| concurrent | inproc | under_load | 1.243 | 1.424 ms | 1.668 | 0.00 | 1406 |
| concurrent | poller | idle | 0.749 | 0.757 ms | 0.765 | 0.00 | 513 |
| concurrent | poller | under_load | 1.057 | 1.231 ms | 1.452 | 0.00 | 2428 |
| single | inproc | idle | 0.734 | 0.744 ms | 0.756 | 0.00 | 529 |
| single | inproc | under_load | 0.799 | 0.822 ms | 0.856 | 0.00 | 755 |
| single | poller | idle | 0.746 | 0.754 ms | 0.762 | 0.00 | 483 |
| single | poller | under_load | 0.807 | 0.828 ms | 0.870 | 0.00 | 721 |

Clock resolution: 41.7 ns

## A2-run2 (head aff8f688aba95319cf073341f2a290590380106e, 12 CPUs, arm64, 32.0 GiB RAM)

| Scenario | Source | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|---|
| concurrent | inproc | 0.757 ms (n=2963) | 1.148 ms (n=10346) | 1.517x (pass) | 9.32 s | 2 |
| concurrent | poller | 0.753 ms (n=2961) | 0.977 ms (n=11733) | 1.297x (pass) | 9.32 s | 2 |
| single | inproc | 0.750 ms (n=2965) | insufficient (n=17) | -- | 0.01 s | 0 |
| single | poller | 0.750 ms (n=2964) | insufficient (n=17) | -- | 0.01 s | 0 |

### Floor analysis

| Scenario | Source | Series | p94 (ms) | p95 (ms) | p96 (ms) | min gap (us) | ties |
|---|---|---|---|---|---|---|---|
| concurrent | inproc | idle | 0.746 | 0.757 ms | 0.767 | 0.00 | 527 |
| concurrent | inproc | under_load | 1.099 | 1.148 ms | 1.228 | 0.00 | 1898 |
| concurrent | poller | idle | 0.745 | 0.753 ms | 0.762 | 0.00 | 449 |
| concurrent | poller | under_load | 0.927 | 0.977 ms | 1.076 | 0.00 | 3319 |
| single | inproc | idle | 0.742 | 0.750 ms | 0.762 | 0.00 | 501 |
| single | inproc | under_load | -- | insufficient | -- | 2.83 | 0 |
| single | poller | idle | 0.743 | 0.750 ms | 0.762 | 0.00 | 488 |
| single | poller | under_load | -- | insufficient | -- | 0.92 | 0 |

Clock resolution: 41.7 ns

Pair A, repetition 1 (A1): run 2 reads worse than run 1 (1.327x -> 1.940x) -- the recorded
pattern from `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`. Pair A,
repetition 2 (A2): run 2 reads **not** worse (1.896x -> 1.517x). Both A2 runs' slowest
build (8.44 s, 9.32 s) is already in the same range as A1-run2's cache-influenced 8.51 s,
not A1-run1's cold 14.29 s -- something beyond this session's own in-memory `_EXPORTS`
cache (which resets on `session.py`'s fresh server start for A2) made A2-run1 behave like
a warm run from its first request. This investigation did not look past the server
boundary for that cause (D-17: no `src/` change); it is noted here, not explained.

### Pair B -- run 2 on teeth 180-189

## B1-run1 (head aff8f688aba95319cf073341f2a290590380106e, 12 CPUs, arm64, 32.0 GiB RAM)

| Scenario | Source | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|---|
| concurrent | inproc | 0.743 ms (n=3011) | 1.096 ms (n=12965) | 1.476x (pass) | 11.36 s | 6 |
| concurrent | poller | 0.735 ms (n=3014) | 0.949 ms (n=14360) | 1.292x (pass) | 11.36 s | 6 |
| single | inproc | 0.773 ms (n=2946) | 0.940 ms (n=4329) | 1.216x (pass) | 3.15 s | 0 |
| single | poller | 0.767 ms (n=2939) | 0.931 ms (n=4297) | 1.213x (pass) | 3.15 s | 0 |

### Floor analysis

| Scenario | Source | Series | p94 (ms) | p95 (ms) | p96 (ms) | min gap (us) | ties |
|---|---|---|---|---|---|---|---|
| concurrent | inproc | idle | 0.732 | 0.743 ms | 0.754 | 0.00 | 555 |
| concurrent | inproc | under_load | 1.059 | 1.096 ms | 1.160 | 0.00 | 3077 |
| concurrent | poller | idle | 0.726 | 0.735 ms | 0.744 | 0.00 | 474 |
| concurrent | poller | under_load | 0.912 | 0.949 ms | 1.030 | 0.00 | 4912 |
| single | inproc | idle | 0.765 | 0.773 ms | 0.786 | 0.00 | 476 |
| single | inproc | under_load | 0.881 | 0.940 ms | 1.041 | 0.00 | 733 |
| single | poller | idle | 0.754 | 0.767 ms | 0.781 | 0.00 | 425 |
| single | poller | under_load | 0.872 | 0.931 ms | 1.020 | 0.00 | 666 |

Clock resolution: 41.7 ns

## B1-run2 (head aff8f688aba95319cf073341f2a290590380106e, 12 CPUs, arm64, 32.0 GiB RAM)

| Scenario | Source | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|---|
| concurrent | inproc | 0.790 ms (n=2864) | 1.825 ms (n=5389) | 2.309x (miss) | 5.81 s | 6 |
| concurrent | poller | 0.789 ms (n=2857) | 1.472 ms (n=6661) | 1.865x (pass) | 5.81 s | 6 |
| single | inproc | 0.782 ms (n=2934) | insufficient (n=19) | -- | 0.02 s | 0 |
| single | poller | 0.772 ms (n=2928) | 1.396 ms (n=21) | 1.809x (pass) | 0.02 s | 0 |

### Floor analysis

| Scenario | Source | Series | p94 (ms) | p95 (ms) | p96 (ms) | min gap (us) | ties |
|---|---|---|---|---|---|---|---|
| concurrent | inproc | idle | 0.783 | 0.790 ms | 0.800 | 0.00 | 404 |
| concurrent | inproc | under_load | 1.650 | 1.825 ms | 1.979 | 0.00 | 664 |
| concurrent | poller | idle | 0.781 | 0.789 ms | 0.804 | 0.00 | 362 |
| concurrent | poller | under_load | 1.331 | 1.472 ms | 1.587 | 0.00 | 1133 |
| single | inproc | idle | 0.771 | 0.782 ms | 0.797 | 0.00 | 435 |
| single | inproc | under_load | -- | insufficient | -- | 0.54 | 0 |
| single | poller | idle | 0.766 | 0.772 ms | 0.786 | 0.00 | 416 |
| single | poller | under_load | -- | 1.396 ms | -- | 0.25 | 0 |

Clock resolution: 41.7 ns

## B2-run1 (head aff8f688aba95319cf073341f2a290590380106e, 12 CPUs, arm64, 32.0 GiB RAM)

| Scenario | Source | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|---|
| concurrent | inproc | 0.771 ms (n=2942) | 1.100 ms (n=12965) | 1.426x (pass) | 11.35 s | 6 |
| concurrent | poller | 0.765 ms (n=2932) | 0.941 ms (n=14340) | 1.229x (pass) | 11.35 s | 6 |
| single | inproc | 0.746 ms (n=2998) | 0.811 ms (n=4420) | 1.086x (pass) | 3.11 s | 0 |
| single | poller | 0.745 ms (n=2996) | 0.816 ms (n=4397) | 1.096x (pass) | 3.11 s | 0 |

### Floor analysis

| Scenario | Source | Series | p94 (ms) | p95 (ms) | p96 (ms) | min gap (us) | ties |
|---|---|---|---|---|---|---|---|
| concurrent | inproc | idle | 0.760 | 0.771 ms | 0.786 | 0.00 | 442 |
| concurrent | inproc | under_load | 1.055 | 1.100 ms | 1.171 | 0.00 | 3190 |
| concurrent | poller | idle | 0.756 | 0.765 ms | 0.777 | 0.00 | 427 |
| concurrent | poller | under_load | 0.902 | 0.941 ms | 1.022 | 0.00 | 4822 |
| single | inproc | idle | 0.739 | 0.746 ms | 0.757 | 0.00 | 523 |
| single | inproc | under_load | 0.797 | 0.811 ms | 0.846 | 0.00 | 743 |
| single | poller | idle | 0.739 | 0.745 ms | 0.752 | 0.00 | 486 |
| single | poller | under_load | 0.789 | 0.816 ms | 0.849 | 0.00 | 744 |

Clock resolution: 41.7 ns

## B2-run2 (head aff8f688aba95319cf073341f2a290590380106e, 12 CPUs, arm64, 32.0 GiB RAM)

| Scenario | Source | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|---|
| concurrent | inproc | 0.752 ms (n=2988) | 1.149 ms (n=8964) | 1.528x (pass) | 8.35 s | 6 |
| concurrent | poller | 0.746 ms (n=2986) | 0.967 ms (n=10453) | 1.296x (pass) | 8.35 s | 6 |
| single | inproc | 0.751 ms (n=3002) | insufficient (n=18) | -- | 0.01 s | 0 |
| single | poller | 0.744 ms (n=2997) | insufficient (n=19) | -- | 0.01 s | 0 |

### Floor analysis

| Scenario | Source | Series | p94 (ms) | p95 (ms) | p96 (ms) | min gap (us) | ties |
|---|---|---|---|---|---|---|---|
| concurrent | inproc | idle | 0.744 | 0.752 ms | 0.760 | 0.00 | 500 |
| concurrent | inproc | under_load | 1.095 | 1.149 ms | 1.275 | 0.00 | 1509 |
| concurrent | poller | idle | 0.741 | 0.746 ms | 0.753 | 0.00 | 456 |
| concurrent | poller | under_load | 0.912 | 0.967 ms | 1.058 | 0.00 | 2726 |
| single | inproc | idle | 0.742 | 0.751 ms | 0.762 | 0.00 | 502 |
| single | inproc | under_load | -- | insufficient | -- | 0.33 | 0 |
| single | poller | idle | 0.735 | 0.744 ms | 0.750 | 0.00 | 466 |
| single | poller | under_load | -- | insufficient | -- | 0.58 | 0 |

Clock resolution: 41.7 ns

Pair B, both repetitions: run 2 reads worse than run 1 in both B1 (1.476x -> 2.309x, a
miss) and B2 (1.426x -> 1.528x). Pair B points worse in both repetitions, cleanly, despite
run 2 moving to a cold export-cache range (teeth 180-189) on a warm-worker server --
exactly D-02's prediction for candidate (2), worker state.

### Pair C -- server restart between the runs

## C1-run1 (head aff8f688aba95319cf073341f2a290590380106e, 12 CPUs, arm64, 32.0 GiB RAM)

| Scenario | Source | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|---|
| concurrent | inproc | 0.740 ms (n=2998) | 1.327 ms (n=8834) | 1.792x (pass) | 8.51 s | 6 |
| concurrent | poller | 0.743 ms (n=2998) | 1.155 ms (n=10059) | 1.553x (pass) | 8.51 s | 6 |
| single | inproc | 0.745 ms (n=3016) | 0.826 ms (n=4379) | 1.109x (pass) | 3.10 s | 0 |
| single | poller | 0.741 ms (n=3015) | 0.820 ms (n=4353) | 1.107x (pass) | 3.10 s | 0 |

### Floor analysis

| Scenario | Source | Series | p94 (ms) | p95 (ms) | p96 (ms) | min gap (us) | ties |
|---|---|---|---|---|---|---|---|
| concurrent | inproc | idle | 0.735 | 0.740 ms | 0.752 | 0.00 | 564 |
| concurrent | inproc | under_load | 1.169 | 1.327 ms | 1.623 | 0.00 | 1524 |
| concurrent | poller | idle | 0.736 | 0.743 ms | 0.753 | 0.00 | 480 |
| concurrent | poller | under_load | 1.017 | 1.155 ms | 1.329 | 0.00 | 2304 |
| single | inproc | idle | 0.735 | 0.745 ms | 0.754 | 0.00 | 534 |
| single | inproc | under_load | 0.800 | 0.826 ms | 0.851 | 0.00 | 794 |
| single | poller | idle | 0.735 | 0.741 ms | 0.751 | 0.00 | 457 |
| single | poller | under_load | 0.800 | 0.820 ms | 0.850 | 0.00 | 711 |

Clock resolution: 41.7 ns

## C1-run2 (head aff8f688aba95319cf073341f2a290590380106e, 12 CPUs, arm64, 32.0 GiB RAM)

| Scenario | Source | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|---|
| concurrent | inproc | 0.752 ms (n=2984) | 1.050 ms (n=13046) | 1.396x (pass) | 11.34 s | 6 |
| concurrent | poller | 0.747 ms (n=2983) | 0.908 ms (n=14329) | 1.215x (pass) | 11.34 s | 6 |
| single | inproc | 0.748 ms (n=2957) | 0.851 ms (n=4413) | 1.137x (pass) | 3.16 s | 0 |
| single | poller | 0.752 ms (n=2952) | 0.837 ms (n=4377) | 1.113x (pass) | 3.16 s | 0 |

### Floor analysis

| Scenario | Source | Series | p94 (ms) | p95 (ms) | p96 (ms) | min gap (us) | ties |
|---|---|---|---|---|---|---|---|
| concurrent | inproc | idle | 0.744 | 0.752 ms | 0.760 | 0.00 | 513 |
| concurrent | inproc | under_load | 1.028 | 1.050 ms | 1.085 | 0.00 | 3193 |
| concurrent | poller | idle | 0.740 | 0.747 ms | 0.754 | 0.00 | 447 |
| concurrent | poller | under_load | 0.882 | 0.908 ms | 0.949 | 0.00 | 5002 |
| single | inproc | idle | 0.740 | 0.748 ms | 0.758 | 0.00 | 533 |
| single | inproc | under_load | 0.822 | 0.851 ms | 0.892 | 0.00 | 765 |
| single | poller | idle | 0.744 | 0.752 ms | 0.761 | 0.00 | 449 |
| single | poller | under_load | 0.819 | 0.837 ms | 0.877 | 0.00 | 699 |

Clock resolution: 41.7 ns

## C2-run1 (head aff8f688aba95319cf073341f2a290590380106e, 12 CPUs, arm64, 32.0 GiB RAM)

| Scenario | Source | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|---|
| concurrent | inproc | 0.773 ms (n=2979) | 1.058 ms (n=12989) | 1.369x (pass) | 11.27 s | 6 |
| concurrent | poller | 0.760 ms (n=2975) | 0.932 ms (n=14203) | 1.226x (pass) | 11.27 s | 6 |
| single | inproc | 0.737 ms (n=3029) | 0.824 ms (n=4409) | 1.118x (pass) | 3.12 s | 0 |
| single | poller | 0.729 ms (n=3022) | 0.823 ms (n=4372) | 1.129x (pass) | 3.12 s | 0 |

### Floor analysis

| Scenario | Source | Series | p94 (ms) | p95 (ms) | p96 (ms) | min gap (us) | ties |
|---|---|---|---|---|---|---|---|
| concurrent | inproc | idle | 0.763 | 0.773 ms | 0.790 | 0.00 | 491 |
| concurrent | inproc | under_load | 1.030 | 1.058 ms | 1.097 | 0.00 | 3234 |
| concurrent | poller | idle | 0.751 | 0.760 ms | 0.779 | 0.00 | 482 |
| concurrent | poller | under_load | 0.902 | 0.932 ms | 0.985 | 0.00 | 4714 |
| single | inproc | idle | 0.728 | 0.737 ms | 0.746 | 0.00 | 530 |
| single | inproc | under_load | 0.798 | 0.824 ms | 0.856 | 0.00 | 769 |
| single | poller | idle | 0.722 | 0.729 ms | 0.737 | 0.00 | 529 |
| single | poller | under_load | 0.798 | 0.823 ms | 0.866 | 0.00 | 725 |

Clock resolution: 41.7 ns

## C2-run2 (head aff8f688aba95319cf073341f2a290590380106e, 12 CPUs, arm64, 32.0 GiB RAM)

| Scenario | Source | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|---|
| concurrent | inproc | 0.754 ms (n=2992) | 1.156 ms (n=8719) | 1.534x (pass) | 8.42 s | 6 |
| concurrent | poller | 0.747 ms (n=2986) | 0.976 ms (n=9966) | 1.308x (pass) | 8.42 s | 6 |
| single | inproc | 0.752 ms (n=2987) | 0.802 ms (n=4426) | 1.066x (pass) | 3.11 s | 0 |
| single | poller | 0.754 ms (n=2981) | 0.810 ms (n=4399) | 1.074x (pass) | 3.11 s | 0 |

### Floor analysis

| Scenario | Source | Series | p94 (ms) | p95 (ms) | p96 (ms) | min gap (us) | ties |
|---|---|---|---|---|---|---|---|
| concurrent | inproc | idle | 0.746 | 0.754 ms | 0.763 | 0.00 | 481 |
| concurrent | inproc | under_load | 1.100 | 1.156 ms | 1.278 | 0.00 | 1441 |
| concurrent | poller | idle | 0.740 | 0.747 ms | 0.753 | 0.00 | 461 |
| concurrent | poller | under_load | 0.931 | 0.976 ms | 1.117 | 0.00 | 2515 |
| single | inproc | idle | 0.742 | 0.752 ms | 0.761 | 0.00 | 521 |
| single | inproc | under_load | 0.790 | 0.802 ms | 0.825 | 0.00 | 769 |
| single | poller | idle | 0.748 | 0.754 ms | 0.760 | 0.00 | 478 |
| single | poller | under_load | 0.794 | 0.810 ms | 0.835 | 0.00 | 740 |

Clock resolution: 41.7 ns

Pair C, repetition 1 (C1): run 2 reads **not** worse (1.792x -> 1.396x). Pair C,
repetition 2 (C2): run 2 reads worse (1.369x -> 1.534x). Pair C is split, the restart
between runs did not produce a consistent direction either way.

### Observation 1 -- run 2 against run 1

| Session | Run1 ratio (inproc) | Run1 under-load n | Run1 refused | Run2 ratio (inproc) | Run2 under-load n | Run2 refused | Direction |
|---|---|---|---|---|---|---|---|
| A1 | 1.327 | 17543 | 6 | 1.940 | 8901 | 2 | worse |
| A2 | 1.896 | 8657 | 6 | 1.517 | 10346 | 2 | not worse |
| B1 | 1.476 | 12965 | 6 | 2.309 | 5389 | 6 | worse |
| B2 | 1.426 | 12965 | 6 | 1.528 | 8964 | 6 | worse |
| C1 | 1.792 | 8834 | 6 | 1.396 | 13046 | 6 | not worse |
| C2 | 1.369 | 12989 | 6 | 1.534 | 8719 | 6 | worse |

Pair-level reading (both repetitions must agree to call a pair "points worse" or "points
not worse" -- D-04): **Pair A is split** (A1 worse, A2 not worse). **Pair B points worse**
(both B1 and B2 worse). **Pair C is split** (C1 not worse, C2 worse).

### H1 re-check -- split poller against in-process

| Session | Run1 ratio (poller) | Run2 ratio (poller) | Poller direction | In-process direction | Agree? |
|---|---|---|---|---|---|
| A1 | 1.174 | 1.546 | worse | worse | agree |
| A2 | 1.627 | 1.297 | not worse | not worse | agree |
| B1 | 1.292 | 1.865 | worse | worse | agree |
| B2 | 1.229 | 1.296 | worse | worse | agree |
| C1 | 1.553 | 1.215 | not worse | not worse | agree |
| C2 | 1.226 | 1.308 | worse | worse | agree |

Every one of the six sessions agrees. No disagreement occurred in either repetition of
any pair.

### Observation 2 -- the floor

Clock resolution on this host (`time.get_clock_info("perf_counter").resolution`): 41.7 ns
(4.1667e-08 s), identical across every one of the twelve runs (reported once per run in
the floor-analysis tables above). Every idle and under-load series' smallest positive gap
between distinct samples (`min_gap_s`) reads 2.328e-10 s (~0.233 ns) across all 48
concurrent idle/under-load series (inproc and poller, twelve runs) -- below the declared
41.7 ns clock resolution, so this minimum reflects float64 subtraction precision at this
host's `monotonic()` timestamp magnitude (~1.08e6 s), not a genuine minimum sampling
interval; the printed "min gap (us)" column rounds this to 0.00 in every row above. Tie
counts (362-7904 identical values per series, out of 2857-18919 samples) are the real
floor signature of the 41.7 ns clock tick quantizing nearby latencies into identical
buckets.

Per-run flip summary (whether the reported verdict would land on the other side of 2.0
under a one-percentile-shifted estimate, D-02):

| Run | Inproc ratio (verdict) | Inproc flips? | Poller ratio (verdict) | Poller flips? |
|---|---|---|---|---|
| A1-run1 | 1.327 (pass) | no | 1.174 (pass) | no |
| A1-run2 | 1.940 (pass) | **yes** | 1.546 (pass) | no |
| B1-run1 | 1.476 (pass) | no | 1.292 (pass) | no |
| B1-run2 | 2.309 (miss) | no | 1.865 (pass) | **yes** |
| C1-run1 | 1.792 (pass) | **yes** | 1.553 (pass) | no |
| C1-run2 | 1.396 (pass) | no | 1.215 (pass) | no |
| A2-run1 | 1.896 (pass) | **yes** | 1.627 (pass) | no |
| A2-run2 | 1.517 (pass) | no | 1.297 (pass) | no |
| B2-run1 | 1.426 (pass) | no | 1.229 (pass) | no |
| B2-run2 | 1.528 (pass) | no | 1.296 (pass) | no |
| C2-run1 | 1.369 (pass) | no | 1.226 (pass) | no |
| C2-run2 | 1.534 (pass) | no | 1.308 (pass) | no |

Four of the twenty-four (run, source) cells flip: `A1-run2.summary.json` (inproc, ratio
1.940, `u96_i95`=2.057, implied under-load p96 1.577 ms vs. p95 1.488 ms -- a 0.090 ms
spread), `C1-run1.summary.json` (inproc, ratio 1.792, `u96_i95`=2.192, implied under-load
p96 1.623 ms vs. p95 1.327 ms -- a 0.296 ms spread), `A2-run1.summary.json` (inproc, ratio
1.896, `u96_i95`=2.220, implied under-load p96 1.668 ms vs. p95 1.424 ms -- a 0.244 ms
spread), and `B1-run2.summary.json` (poller, ratio 1.865, `u96_i95`=2.011, a smaller
spread). `B1-run2.summary.json`'s in-process verdict (2.309, miss) does not flip -- it is
already a clear miss at every alternative (2.088-2.504), not a boundary case.

Sample-count check for candidate (iii): sorting all twelve runs' in-process under-load `n`
(5389, 8657, 8719, 8834, 8901, 8964, 10346, 12965, 12965, 12989, 13046, 17543), the median
is 9655. The three flipping in-process runs (8657, 8834, 8901) are all below the median,
but so are three non-flipping runs (5389 `B1-run2`, 8719 `C2-run2`, 8964 `B2-run2`) --
below-median sample count does not predict a flip on its own; (iii)'s *exact* claim does
not hold.

## Verdict

### Observation 1

Not reproduced in this environment. Pair A does not point worse (it is split: A1 worse,
A2 not worse -- see `A1-run1.summary.json`/`A1-run2.summary.json` vs.
`A2-run1.summary.json`/`A2-run2.summary.json`), and the pre-registered rule states that
when Pair A does not point worse, observation 1 is not reproduced and Pairs B and C cannot
rule anything in or out -- even though Pair B alone points worse in both repetitions
(`B1-run2.summary.json`, `B2-run2.summary.json`) and Pair C is itself split
(`C1-run2.summary.json` not worse, `C2-run2.summary.json` worse). This is an environment
change relative to the original eight runs: `fleet-user` was stopped for this campaign
(D-06), where it was up and restart-looping throughout Runs 1-8. No candidate (cache-hit
sends, worker state, window at the floor) is ruled in or ruled out by this campaign; none
survives as "the" cause of observation 1 on this host, in this environment.

### Observation 2

Candidate (ii) -- the floor is real -- is ruled in. At least one concurrent run's in-process verdict flips
inside one percentile -- three do (`A1-run2.summary.json`, `C1-run1.summary.json`,
`A2-run1.summary.json`), plus one on the split poller (`B1-run2.summary.json`) -- which
directly refutes (i) ("no concurrent run's verdict flips inside one percentile"). (iii)'s
exact claim (the flipping runs are *exactly* the below-median-n runs) does not hold: three
below-median-n runs do not flip (`B1-run2.summary.json`, `C2-run2.summary.json`,
`B2-run2.summary.json`). (ii) is therefore the surviving candidate -- the pass/miss line
sits close enough to real sample-to-sample variation at the achieved sample counts that a
one-percentile shift changes the verdict in four of twenty-four (run, source) cells. D-09's
first offer for observation 2 is D-10's absolute floor.

### H1 verdict

H1 stays refuted. In every one of the six sessions, the split-process poller's run-2-vs-
run-1 direction agrees with the in-process direction (H1 re-check table above); H1 is
revived only if they disagree in both repetitions of a pair, and there is no disagreement
in any repetition of any pair.

## Recommendation

Observation 1 is not reproduced in this environment (no cause ruled in; D-09 names no
first offer for an unreproduced observation). Observation 2 is ruled to (ii) -- the floor
is real. D-09's first offer therefore is D-10's absolute floor: pass iff under-load p95
<= max(2.00 x idle p95, idle p95 + M ms), with M on the order of 10x the measured
per-sample resolution.

The floor analysis's numbers that would set M (D-10): the declared clock resolution is
41.7 ns (`time.get_clock_info("perf_counter").resolution`), uniform across all twelve
runs -- 10x that is 417 ns (0.000417 ms), far smaller than any observed pass/miss spread.
The measured smallest gap between distinct samples, 2.328e-10 s, is a float64-precision
artifact below the clock's own declared resolution (see Observation 2) and must not be
used to set M directly -- using it would set a threshold below the noise floor it is meant
to absorb. The one-percentile spreads that actually flipped a verdict this session ran
0.090-0.296 ms in absolute under-load p95 terms (`A1-run2`, `C1-run1`, `A2-run1` above) --
on the order of 100-700x the clock resolution, not 10x it. 13-04/13-05 (D-10's own plan)
should set M from this campaign's spreads, not from the clock resolution alone; the 10x
clock-resolution heuristic in D-10's text does not match what this campaign actually
measured, and that mismatch itself is worth naming to the human before M is fixed in L32.

No server-side cost is named by this investigation. Observation 1 was not reproduced, so
neither "four instant ~2.6 MB sends from the loop thread at t=0" (candidate 1) nor
"worker-side state after the first batch" (candidate 2) is ruled in -- there is nothing to
file as a `docs/tech_debt/active/` item under D-17 from this plan. Observation 2's cause
(the floor) is a harness/measurement-floor property, not a server defect, so it is not
filed as debt either -- D-17 reserves that filing for a server-side cause ruled in, and
none was. Both findings carry forward to D-09/D-10's own machinery in the plans that
follow (13-04 for the decisive session; 13-05 only if D-10's floor threshold is adopted).

## Cleanup

- `lsof -nP -iTCP:8001 -sTCP:LISTEN -t` empty after the sixth session (confirmed in Task
  1's verify, re-confirmed before this write-up).
- `pgrep -f run_experiment.py` and `pgrep -f poller.py`: no processes from this campaign
  left running (every session's own `finally` block stopped its server and waited for the
  port to clear before the session returned `done`).
- No `investigation/.session.lock` exists (confirmed before each of the six launches and
  after the sixth).
- `spur-spur-1` still `Up ... (healthy)` throughout (last confirmed in C2's own
  `docker_ps` snapshot: `spur-spur-1 Up 36 hours (healthy)`).
- `fleet-user` still `Exited` throughout every session (last confirmed in C2's snapshot:
  `fleet-user Exited (2) 14 hours ago`) -- stopped for the campaign window (D-06), left
  stopped for 13-04's decisive bar session; 13-07 restores it once the whole phase closes.
  13-03 does not restore it.
- Raw files for all six sessions (A1, B1, C1, A2, B2, C2) committed in `a24cb93`
  (`docs(13-03): record the latency investigation's six pair sessions, raw samples and
  summaries (D-01, D-02, D-03)`).
- `git diff --quiet 9f26052 -- src bench` exits 0 -- no `src/` or `bench/` file was
  touched by this plan.
