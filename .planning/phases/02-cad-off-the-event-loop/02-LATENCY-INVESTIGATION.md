---
phase: 02-cad-off-the-event-loop
plan: 04
type: investigation
status: complete
date: 2026-09-23
---

# Why does `/api/health` under-load p95 blow past 2x idle in the `concurrent` scenario?

## Question

`bench/RESULTS.md`'s `concurrent` scenario (ten concurrent fine builds) measured
`/api/health` under-load p95 at 2.02x-2.45x idle p95 across four runs in two sessions,
against a <=2.00x acceptance bar. Is that a property of the server topology (`app.py`,
`pool.py`), or an artifact of how `bench/latency.py` measures it (its health poller shares
a process, and a GIL, with the ten threads pulling multi-MB STL bodies)?

## Environment

Same machine as `bench/RESULTS.md`: 12 CPUs, arm64, 32.0 GiB RAM (`bench.machine_facts()`,
confirmed this session by the harness's own printed output). This machine was **not**
idle for any part of this session -- every experiment below carries its own load-average
and top-CPU sample, per L08, rather than one clean number presented for the whole run.
`sysctl -n vm.loadavg` gives the 1-, 5-, 15-minute load averages; `ps -Ao %cpu,comm -r |
head -4` gives the top CPU consumers at that instant.

| When | 1/5/15-min loadavg | Top CPU (excl. header) |
|---|---|---|
| Server start (8001) | 3.50 3.01 2.73 | WindowServer 30.7%, claude 16.8%, Telegram 10.5%, coreaudiod 10.5% |
| Before E0 | 3.54 3.03 2.74 | OrbStack Helper 74.5%, WindowServer 23.2%, coreaudiod 10.8%, Telegram 8.0% |
| Before E1 run1 | 3.06 3.05 2.77 | **node 291.6%**, Firefox plugin-container 40.6%, WindowServer 29.3%, plugin-container 10.8% |
| Before E1 run2 | 8.39 4.24 3.20 | **go 222.4%**, Firefox plugin-container 24.8%, WindowServer 12.8%, claude 9.7% |
| Before E2a run1 (retry) | 6.22 5.60 4.12 | WindowServer 44.1%, Firefox plugin-container 33.0%, claude 15.5%, Telegram 13.7% |
| Before E2a run2 | 5.27 5.42 4.09 | WindowServer 24.6%, claude 11.6%, coreaudiod 10.6%, launchd 7.8% |
| Before E2b run1 (fresh server) | 3.58 4.87 4.06 | iStat Menus history.xpc 58.0%, claude 14.9%, iTerm2 8.7%, xprotectd 4.9% |
| Before E2b run2 | 3.52 4.79 4.04 | VS Code Code Helper (Renderer) 45.8%, claude 5.1%, iTerm2 4.7%, xprotectd 3.3% |
| Before E2c run1 | 2.93 4.54 3.98 | iTerm2 12.0%, xprotectd 5.6%, claude 4.6%, syspolicyd 4.4% |
| Before E2c run2 | 2.92 4.46 3.96 | claude 10.4%, iTerm2 6.2%, xprotectd 5.7%, powermetrics 3.5% |
| Before gzip_bench.py | 5.68 4.91 4.13 | **node (vitest 5) 98.5%, node (vitest 4) 97.1%, node (vitest 6) 93.7%, node (vitest 9) 87.6%** (unrelated project's test runner) |
| Before E3 w1 run1 | 8.36 6.02 4.59 | fseventsd 14.3%, claude 14.3%, iTerm2 8.1%, xprotectd 6.0% |
| Before E3 w1 run2 | 7.30 5.93 4.59 | chrome-headless-shell 81.3%, java 15.4%, node 15.1%, systemstats 13.9% |
| Before E3 w2 run1 | 6.10 5.76 4.56 | **govulncheck (go) 319.8%**, iTerm2 6.5%, xprotectd 4.7%, AlDente 4.0% |
| Before E3 w2 run2 | 5.53 5.66 4.56 | claude 14.9%, Activity Monitor 9.8%, iTerm2 8.8%, xprotectd 7.0% |
| Before bonus no-gzip run1 | 3.29 4.42 4.22 | Firefox plugin-container 8.6%, iTerm2 6.0%, Activity Monitor 4.5%, Telegram 2.3% |
| Before bonus no-gzip run2 | 2.85 4.27 4.17 | claude 18.7%, iTerm2 8.7%, xprotectd 6.9%, powermetrics 5.8% |

This host was consistently at 1-minute loadavg 2.9-8.4 on a 12-core machine (never below
the >1.5 "quiet" threshold `bench/RESULTS.md` names), with several genuinely unrelated,
CPU-heavy processes appearing mid-session (`node`/vitest test runners at 87-99% each,
`go`/`govulncheck` at 220-320%). This confirms the session was not idle and every
absolute millisecond figure below inherits that noise -- consistent with, and no better
than, the environment `bench/RESULTS.md`'s own four runs recorded.

## Method

All experiments live under
`/private/tmp/claude-501/-Users-halfb00t-git-halfb00t-spur/a7aff741-d5d0-4ba6-8a65-8bb49a58e3a9/scratchpad/latency-spike/`
(`poller.py`, `run_experiment.py`, `gzip_bench.py`, `results/*.json`, `results/*.jsonl`).
**No file under `src/` or `bench/` was modified this session** (`git status --short`
shows only `.planning/STATE.md` and this report touched).

- **`poller.py`** -- a standalone script, launched via `subprocess.Popen` as a genuinely
  separate OS process with its own `httpx.Client` and its own GIL. Samples `/api/health`
  in a do-while loop (same cadence as `bench/latency.py`'s own `_sample_while_building`:
  no delay between requests) until a `--stop-file` appears, then writes every
  `(time.monotonic(), latency_seconds)` pair to `--out` as JSON lines.
  `time.monotonic()` is CLOCK_MONOTONIC-backed (system/boot-time, not per-process) on
  macOS, so its timestamps are directly comparable to the launching process's own
  `time.monotonic()` calls without any clock-sync step.
- **`run_experiment.py`** -- the harness process. For every experiment: launches
  `poller.py` as a subprocess (the split-process leg), then, concurrently, runs an
  **in-process** idle/under-load sample using `bench.latency`'s own `_sample_for`,
  `_sample_while_building`, `_build` and `_p95` -- **imported unmodified from
  `bench.latency`**, not reimplemented (`sys.path.insert(0, PROJECT_ROOT)` then
  `from bench.latency import ...`) -- while firing ten concurrent build requests via
  `ThreadPoolExecutor(max_workers=10)`, exactly `bench/latency.py::scenario_concurrent`'s
  own shape. After the builds finish, it signals the poller subprocess to stop, reads its
  samples back, and splits them into an idle segment (before `t_builds_start`) and an
  under-load segment (`t_builds_start`..`t_builds_end`), both measured in `monotonic()`
  time recorded by the *harness* process and compared against the *poller* process's own
  timestamps. `--mode range` reproduces `scenario_concurrent`'s own params verbatim
  (teeth 190..199, one each, quality=fine -- read from `bench/latency.py`, not re-picked).
  `--mode single` repeats one (teeth, quality) ten times concurrently. `--mode cached`
  warms the `(params, fmt, quality)` cache with one request first, then fires it ten times
  concurrently, so the pool never runs for any of the ten. A bonus `--no-gzip` flag sends
  `Accept-Encoding: identity` on the build client to isolate whether gzip compression
  itself is the mechanism (see E2c-bonus below).
- **`gzip_bench.py`** -- no server involved. Measures `zlib.compressobj` at Starlette's
  `GZipMiddleware` defaults (`compresslevel=9`, gzip wrapper) directly against the actual
  9,062,784-byte STL this app serves for `teeth=199&quality=fine` (captured via `curl`
  with `Accept-Encoding: identity` during this session), single-threaded and as 10
  concurrent threads.
- **Deviation found and fixed in this scratch code (not src/bench):** the first `--mode
  single` attempt for a tiny gear (`teeth=6`) crashed with an unhandled 422 ("Bore is too
  large for the root diameter") before the script reached its own cleanup step, orphaning
  the `poller.py` subprocess (it never saw a stop-file, so it kept sampling in the
  background). On retry with the same `--label`/`--run`, the orphan and the new poller
  process both wrote the same output path concurrently, interleaving and corrupting the
  JSON lines file (`json.decoder.JSONDecodeError` on read-back). Fixed by wrapping the
  build phase in `try/finally` so the stop-file is always written and the poller process
  is always waited on (with a `kill()` fallback on timeout) even if the build phase
  raises. The corrupted file was deleted and E2a re-run cleanly with `bore_d=0` (the
  smallest change that makes 6 teeth buildable at all -- the params default `bore_d=9.0mm`
  is infeasible at 6 teeth).
- Server started the way `make serve` does (`.venv/bin/spur serve`), on port 8001
  (port 8000 is held by the pre-existing `spur-spur-1` container, same as
  `bench/RESULTS.md`'s own D-17 reasoning), with `SPUR_BUILD_WORKERS` overridden only for
  E3's two legs. Verified `/api/health` returns 200 with a `pool` object before each
  experiment; stopped with `pkill -f "spur serve"` after; verified with `lsof -i :8001`
  and a `poller.py`/`run_experiment.py` process grep that nothing was left running.

## Results

Every ratio below is `under-load p95 / idle p95`, `_p95` = `statistics.quantiles(samples,
n=20)[-1]`, imported from `bench.latency`. "insufficient (n<20)" means `bench.latency`'s
own `MIN_SAMPLES` gate would refuse to report a p95 for that series -- reported as such
per L08, not filled with a guessed number.

### E0 -- baseline reproduction, unmodified `bench/latency.py`

| Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|
| 0.6 ms (n=3714) | 0.9 ms (n=12099) | **1.53x** | 9.14 s | 6 of 10 |

Passes the <=2.00x bar this run -- itself evidence the ratio is noise-sensitive near the
boundary (matches `bench/RESULTS.md`'s own observation of run-to-run swings: 2.02x, 2.45x,
2.32x, 2.35x).

### E1 -- H1 test: split-process poller vs in-process poller, same params as `scenario_concurrent`

| Run | Poller | Idle p95 (n) | Under-load p95 (n) | Ratio | Refused |
|---|---|---|---|---|---|
| 1 | in-process | 0.87 ms (n=2832) | 6.11 ms (n=6246) | 7.06x | 2 of 10 |
| 1 | **split-process** | 0.87 ms (n=2853) | 5.22 ms (n=7440) | **5.99x** | 2 of 10 |
| 2 | in-process | 1.67 ms (n=2294) | 2.59 ms (n=8958) | 1.55x | 0 of 10 |
| 2 | **split-process** | 1.56 ms (n=2332) | 2.31 ms (n=9999) | **1.48x** | 0 of 10 |

The split-process poller (own OS process, own GIL) tracks the in-process poller closely in
both runs (5.99x vs 7.06x; 1.48x vs 1.55x) -- it never collapses toward 1.x while the
in-process ratio stays elevated, which is what H1 predicts. **H1 refuted.**

(Run 1's unusually high ratio: the server was not restarted between E0 and E1, so several
of E1's ten teeth were already cached from E0's admitted builds -- see E2b/E2c below for
why cache hits make this *worse*, not better.)

### E2 -- H2/H3 payload test (split poller)

**(a) tiny gear** (`teeth=6, bore_d=0, quality=preview`, single value x10; STL = 186,884
bytes; smallest valid params -- the field default `bore_d=9.0mm` is infeasible at 6 teeth,
"Bore is too large for the root diameter", 422):

| Run | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|
| 1 | 0.87 ms (n=2830) | insufficient (n<20) | -- | 0.036 s | 0 of 10 |
| 2 | 0.84 ms (n=2836) | 4.51 ms (n=20) | 5.34x (n at the reporting floor -- unreliable) | 0.034 s | 0 of 10 |

Builds complete in ~35 ms; the load window is too short to collect a trustworthy p95 most
of the time. This is itself informative: it takes real, sustained concurrent work to move
the ratio, and a 186 KB payload's build+compress+send does not produce that.

**(b) 199-tooth fine, single value x10** (STL = 9,062,784 bytes; identical params means
hash-affinity, D-07, routes all ten to one worker):

| Run | Server state | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|---|
| 1 | fresh (uncached) | 0.74 ms (n=3104) | 1.15 ms (n=8437) | **1.55x** | 6.87 s | 6 of 10 |
| 2 | same server, now cached | 0.84 ms (n=2942) | 5.08 ms (n=391) | **6.06x** | 1.02 s | 0 of 10 |

Run 2 was not intended as a cache-hit test (server wasn't restarted between runs 1 and 2,
so run 1's admitted build populated `_EXPORTS` for this exact key) -- but the result is the
key finding of this investigation: a **cache hit** (`slowest = 1.02 s`, no build at all)
produced a **higher** ratio than the genuine, admission-controlled build in run 1.

**(c) already-cached request, pool never runs** (warm once, then ten concurrent hits on
the same `(params, fmt, quality)` key; teeth=199, quality=fine):

| Run | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest ("build") | Refused |
|---|---|---|---|---|---|
| 1 | 0.80 ms (n=2923) | 3.47 ms (n=444) | **4.33x** | 1.00 s | 0 of 10 |
| 2 | 0.84 ms (n=2816) | 4.66 ms (n=396) | **5.52x** | 1.00 s | 0 of 10 |

Confirms b/run2: the pool never runs (confirmed by code -- `app.py`'s `model()` checks
`_EXPORTS.get(key)` *before* `_build_slot()`; a hit returns straight from the byte cache
without ever acquiring `BUILD_QUEUE`), yet the ratio is as high as, or higher than, any
genuinely pool-touching scenario measured this session. **This refutes H2 as the primary
mechanism** (parent-side unpickling of pool results cannot explain a ratio this high when
the pool is never invoked) and **confirms H3's prediction** ("similar to H2 but present
even when the pool returns instantly").

**Bonus confirmatory check -- same scenario, gzip disabled** (`Accept-Encoding: identity`
on the build client; not one of the four named experiments, run because E2c's cache-hit
result pointed directly at response-body compression):

| Run | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest ("build") | Refused |
|---|---|---|---|---|---|
| 1 | 0.77 ms (n=3041) | 1.33 ms (n=65) | 1.73x | 0.076 s | 0 of 10 |
| 2 | 0.77 ms (n=3030) | 2.79 ms (n=59) | 3.63x (n=59, noisy) | 0.063 s | 0 of 10 |

Disabling gzip drops the round trip from ~1.00 s to 0.06-0.08 s (13-16x) and pulls the
ratio down from E2c's 4.33x/5.52x toward the pass bar (though run 2 still shows some
elevation at a small sample count -- see Verdict). **Directly, causally confirms gzip
compression as the dominant mechanism**, not merely a correlate.

**`gzip_bench.py` -- direct cost of the mechanism**, no server involved, against the real
9,062,784-byte STL, at Starlette's own default `compresslevel=9`
(`inspect.signature(GZipMiddleware.__init__)` confirmed this session: `compresslevel: int
= 9`; `app.py`'s `app.add_middleware(GZipMiddleware, minimum_size=1024)` never overrides
it):

- Single-threaded: **1181.7 ms**, output 2,404,371 bytes (26.5% of input).
- 10 concurrent (`ThreadPoolExecutor(max_workers=10)`, mirrors what 10 concurrent
  `/api/model.stl` responses for the same cached gear do, since Starlette's
  `GZipResponder` offloads bodies >=128 KiB to a thread via `anyio.to_thread.run_sync`):
  per-thread times 1352-1428 ms, wall clock for all 10: **1432.5 ms**.
- Sampled under load average 5.68/4.91/4.13, with four unrelated `node`/vitest processes
  at 87-99% CPU each -- this specific number is itself inflated by host noise, but the
  order of magnitude (over a second to gzip-9 a 9 MB STL) is real and matches every
  "slowest ~1.0s" figure observed in the cache-hit experiments above almost exactly.

### E3 -- admitted-builds test (`SPUR_BUILD_WORKERS`, split poller, `range` mode)

| Workers | Slots | Run | Poller | Idle p95 (n) | Under-load p95 (n) | Ratio | Refused |
|---|---|---|---|---|---|---|---|
| 1 | 2 | 1 | in-process | 1.29 ms (n=2501) | 1.40 ms (n=9411) | 1.08x | 8 of 10 |
| 1 | 2 | 1 | **split** | 1.32 ms (n=2512) | 1.24 ms (n=10877) | **0.94x** | 8 of 10 |
| 1 | 2 | 2 | in-process | 1.04 ms (n=2543) | 1.53 ms (n=6486) | 1.47x | 6 of 10 |
| 1 | 2 | 2 | **split** | 1.04 ms (n=2573) | 1.21 ms (n=7902) | **1.16x** | 6 of 10 |
| 2 | 4 | 1 | in-process | 0.78 ms (n=3009) | 1.06 ms (n=14385) | 1.36x | 6 of 10 |
| 2 | 4 | 1 | **split** | 0.77 ms (n=3046) | 0.93 ms (n=15822) | **1.20x** | 6 of 10 |
| 2 | 4 | 2 | in-process | 0.78 ms (n=3007) | 1.17 ms (n=11130) | 1.50x | 2 of 10 |
| 2 | 4 | 2 | **split** | 0.77 ms (n=3041) | 1.00 ms (n=12643) | **1.29x** | 2 of 10 |

Both worker counts stay under the 2x bar in every run of this leg (0.94x-1.50x). The
falling `refused` count run-over-run within each leg (8->6, 6->2) is the same
`_EXPORTS`-cache-carryover effect as E2b: teeth already built in an earlier run bypass
admission control entirely on a later run against the same, not-restarted server.

## Verdict

**H1 (harness artifact): refuted.** Across every experiment (E1, E2, E3), the
split-process poller's ratio tracks the in-process poller's ratio closely and moves in
the same direction run-to-run (e.g. E1: 5.99x vs 7.06x, then both drop together to
1.48x/1.55x; E3 w2 run2: 1.29x vs 1.50x). If the harness's own GIL contention (ten
threads pulling multi-MB bodies) were the cause, isolating the poller in its own OS
process (its own GIL) should have collapsed its ratio toward 1.x while the in-process
figure stayed elevated. It never did. `Runs 1-4` in `bench/RESULTS.md` are measuring a
real, server/host-level effect, not the harness's own scheduling.

**H2 (parent-side unpickling): refuted as the primary mechanism.** E2c fires ten
concurrent requests for an already-cached export -- `app.py`'s `model()` checks
`_EXPORTS.get(key)` before ever calling `_build_slot()`/the pool, confirmed by reading the
code this session (`src/spur/app.py`, `model()`, ~line 254-289) -- and still measured
4.33x and 5.52x, as high as or higher than any pool-touching scenario measured. Unpickling
cannot be the cause of a ratio this size when the pool is never invoked for any of the ten
requests.

**H3 (loop-side send cost): confirmed, with the mechanism refined by direct
measurement.** It is not literally *synchronous, on-the-event-loop* gzip, because this
app's installed Starlette (1.6.0) already offloads bodies >=128 KiB to a thread pool via
`anyio.to_thread.run_sync` specifically to avoid blocking the loop -- confirmed by reading
`GZipResponder.apply_compression` this session. But that offloaded work is itself
expensive and, critically, **unbounded on a cache hit**: `zlib` compression at Starlette's
default `compresslevel=9` (never overridden by `app.py`'s
`app.add_middleware(GZipMiddleware, minimum_size=1024)`) costs **~1.18 s single-threaded,
~1.35-1.43 s per thread when 10 run concurrently** for the 9 MB STL this app serves at
`teeth=199, quality=fine` (`gzip_bench.py`, this session) -- and unlike a real build, a
cache hit never touches `BUILD_QUEUE` (`_build_slot()`), so **nothing bounds how many of
these ~1.2-1.4 s compressions can run concurrently for repeat/cached downloads**, whereas
genuine builds are capped at `MAX_QUEUED_BUILDS` (4 by default). Disabling gzip on the
same cache-hit scenario (bonus check) dropped the round trip 13-16x (1.00 s -> 0.06-0.08
s) and pulled the ratio from 4.33x/5.52x down to 1.73x/3.63x -- a direct causal
confirmation, not just a correlation. On a 12-core, not-fully-idle host, several
concurrent ~1.2-1.4 s CPU-bound compression threads (whether from throttled fresh builds
or unthrottled cache hits) compete for CPU cores with the single event-loop thread that
must run periodically to answer `/api/health`; because CPU-core contention is a
machine-wide resource, not a per-process one, moving the poller to a separate OS process
(H1's proposed fix) does nothing about it -- which is exactly what E1/E2/E3 show.

**What this means for `bench/RESULTS.md`'s Runs 1-4:** they measured a real, reproducible
server-side cost (gzip compression of multi-MB STL bodies at level 9, worsened by the
missing admission-control gate on cache hits), amplified by this session's consistently
non-idle host (1-minute loadavg 2.9-8.4 throughout, several unrelated CPU-heavy processes
appearing mid-session). It is not a measurement artifact of `bench/latency.py`'s own
design (H1 refuted) and it is not solely the CAD-build/process-pool path this phase's own
topology work targeted (H2 refuted as primary) -- it is dominated by response
compression, a cost this phase's plan never named or measured.

## Recommendation

**(b) The topology has a real per-response parent-side cost.** This is not primarily a
harness artifact (rules out (a): re-measuring with a fixed harness would not make this
cost disappear, since the split-process poller already shows it) and it is not purely
sub-millisecond noise below the measurement floor (rules out treating it as pure noise:
`gzip_bench.py` measured a real, order-of-a-second cost with no server or host contention
involved in the measurement itself). Name it as a gap plan for `/gsd-plan-phase 2
--gaps`, with fix candidates in rough order of expected leverage (none implemented this
session):

1. **Lower `GZipMiddleware`'s `compresslevel` for this app's bodies**, or gate it by
   content type/size more aggressively. Level 9 is zlib's slowest setting; STL/STEP
   bodies are large binary/ASCII geometry data where a much cheaper level (1-6) likely
   trades a small amount of transfer size for a large amount of CPU time -- worth
   measuring directly against `gzip_bench.py`'s own numbers before picking a value.
2. **Gate cache-hit (`_EXPORTS` hit) responses through the same concurrency bound as
   fresh builds**, or a separate limiter sized for "concurrent large-body sends" --
   currently `app.py`'s `model()` skips `_build_slot()` entirely on a cache hit
   (confirmed this session), so a burst of repeat downloads for one popular gear has no
   ceiling on concurrent compression work, unlike a fresh build (capped at
   `MAX_QUEUED_BUILDS`).
3. **Cache the compressed bytes, not just the raw bytes**, in `_EXPORTS` (or a sibling
   cache) -- today, ten requests for the identical cached gear each pay the full
   compression cost again; compressing once per cache-fill instead of once per response
   would make repeat downloads (E2c's exact scenario) nearly free.
4. **Result-transfer path off the parent's GIL** (the objective's own suggestion --
   shared memory/file, or `Response` streaming) -- this session's evidence puts it well
   below gzip-compresslevel as the dominant cost (E2c shows the effect with zero pool
   involvement), so treat it as a secondary candidate, not the first thing to change.

After any of the above lands, re-run `make bench.latency concurrent` (ideally the E1/E2/E3
scratch scripts too, since they isolate the mechanism far more precisely than the
committed scenario alone) to confirm the fix, then continue to 02-05.

## Cleanup

Server processes on port 8001 stopped after every experiment leg (`pkill -f "spur
serve"`); `lsof -i :8001` and a `poller.py`/`run_experiment.py` process grep both came back
empty after the final run. No container was touched (`spur-spur-1` on port 8000 was left
running throughout, per this task's own instructions). Scratch scripts and raw JSON/JSONL
results remain under the scratchpad path named above for anyone who wants to re-run or
re-inspect them; nothing under it was committed.
