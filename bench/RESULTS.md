# bench results

The committed, re-runnable measurement record for Phase 2 (`docs/tech_debt/active/
2026-09-21-cad-builds-block-the-event-loop.md`, `REQ-cad-off-event-loop`,
`REQ-measured-memory-ceiling`). Produced by `make bench.latency` and `make bench.memory`
(`bench/README.md`); re-run these commands to check any number below.

## Machine

- CPU: 12 cores, Apple M2 Max, arm64
- RAM: 32.0 GiB
- OS: macOS 27.0 (Darwin 27.0.0)
- Python: 3.12.13 (`.venv`)
- Docker: 29.4.0, Compose v5.1.2
- Date: 2026-09-23, ~09:37-10:30 UTC

**This is not the debt file's 12-core machine that produced the recorded baseline** — only
the *ratio* (under-load p95 / idle p95) is comparable across the two machines; the
absolute millisecond figures are not (D-17).

**Environment caveat.** Task 1's checkpoint (this plan's blocking-human environment gate)
was answered `quiet` at 09:21 UTC. Re-checking immediately before the latency runs
(09:37-09:41 UTC) found the host was *not* fully idle: load average 1-minute figures of
2.35 and 2.33 (above the >1.5-on-a-12-core-host threshold this plan itself names), with
`claude` (this session), iTerm2, VS Code's plugin helper and a restart-looping unrelated
Docker container (`fleet-user`, `Restarting (2)`, pre-existing and unrelated to this
project) all present in the process/container list. Per this plan's Task 1 instructions
("Numbers recorded with that caveat ... are still useful; a clean-looking number from a
busy machine is exactly the plausible-but-unmeasured number L08 forbids"), the latency
numbers below carry this caveat rather than being presented as clean. Docker itself
(`docker info`, exit 0) and the memory sweep's own host state are re-checked separately
in the `## Memory` section below, at the later time that sweep actually ran.

## Latency

`make bench.latency` against a host `spur serve` on an alternate port (`SPUR_PORT=8001`
— the default `:8000` was occupied by a long-running `spur-spur-1` container from an
earlier, unrelated `docker compose up`; using a different port keeps this a like-for-like
host run per D-17, just not on the default port).

Run twice in immediate succession (same host state, same caveat above) to check whether a
single sample was representative — not to search for a passing run; both are reported.

### `single` scenario (one 200-tooth fine build in flight)

| Run | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|
| 1 | 0.6 ms (n=3810) | 0.7 ms (n=6622) | 1.12x | 3.91 s | 0 of 1 |
| 2 | 0.6 ms (n=3787) | 0.7 ms (n=1817) | 1.18x | 1.08 s | 0 of 1 |

Pass bar: under-load p95 <= 2.00x idle p95. **Met** on both runs.

### `concurrent` scenario (ten concurrent fine builds)

| Run | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|
| 1 | 0.6 ms (n=3694) | 1.2 ms (n=9051) | 2.02x | 7.39 s | 2 of 10 |
| 2 | 0.6 ms (n=3718) | 1.5 ms (n=8160) | 2.45x | 6.96 s | 0 of 10 |

Pass bar: under-load p95 <= 2.00x idle p95. **Not met** on either run (2.02x, then
2.45x — got worse, not better, on the second attempt).

`Refused` = requests admission control turned away with `503` rather than building
(`MAX_QUEUED_BUILDS`, D-09) — 4 requests fit the queue by default
(`2 x SPUR_BUILD_WORKERS`, `SPUR_BUILD_WORKERS=2`), so up to 6 of the 10 concurrent
requests are expected to be refused; the harness (`bench/latency.py`) previously crashed
on this instead of reporting it (see "Deviations" in `02-04-SUMMARY.md`).

**Finding.** The `concurrent` scenario does not clear the 2x bar
(`REQ-cad-off-event-loop`'s acceptance clause) on this machine, in this environment. Both
absolute figures are sub-millisecond (0.6 ms -> 1.2-1.5 ms) — small enough that the noise
budget from a host running other work (the caveat above) plausibly explains a chunk of
the gap between 2.00x and the observed 2.02x/2.45x, and the second run's load average was
no better than the first's. Per this plan's own instruction ("do not adjust the bar and
do not adjust the corpus... record the numbers as measured, state that the criterion was
not met"), this is recorded as a finding rather than tuned into a pass: **the
`concurrent` scenario's ratio bar is not demonstrated to be met on this measurement
session**, and a re-run on a genuinely idle host is needed before `REQ-cad-off-event-loop`
can be marked fully satisfied by this evidence. The `single` scenario — one build in
flight, the scenario the debt file's own headline numbers (0.22s -> 0.76s -> 2.00s) come
from — clears the bar comfortably on both runs. Recorded baseline, quoted verbatim,
different (12-core) machine, ratio-only comparison per D-17: single: 0.22s -> 0.76s ->
2.00s under one 200-tooth fine build; concurrent: repeatedly over 5s under ten concurrent
builds.

### Idle-host re-run (Runs 3-4)

Dispatched by the human's choice to re-run on a quieted host rather than accept-with-caveat
or investigate (broken-windows ledger item 1). Same machine, `make serve` on
`SPUR_PORT=8001` (port 8000 still held by the pre-existing `spur-spur-1` container, D-17),
same harness (`bench/latency.py`), unmodified.

**Environment snapshot (2026-09-23, ~12:11-12:12 UTC, immediately before the runs):**

- `docker info`: exit 0.
- `sysctl -n vm.loadavg`, three samples 30 s apart: `{ 3.33 2.86 2.23 }` (12:11:13 UTC),
  `{ 3.79 3.02 2.31 }` (12:11:48 UTC), `{ 3.96 3.13 2.37 }` (12:12:18 UTC).
- Top CPU (`ps -Ao %cpu,comm -r | head -5`), latest sample: `node` 160.9%, iTerm2 97.1%,
  WindowServer 67.9%, MenuBarAgent 25.2%.
- `docker ps --format '{{.Names}} {{.Status}}'`: `spur-spur-1 Up 2 hours (healthy)`,
  `fleet-user Restarting (2)` (pre-existing, unrelated, not touched).

**Environment caveat.** The human's `quiet` request at ~12:09 UTC did not produce an idle
host: the 1-minute load figure climbed across the three samples (3.33 -> 3.79 -> 3.96),
higher than either of Runs 1-2's pre-run figures (2.35, 2.33), with `node` (an unrelated
process, not this session) at 160.9% CPU driving most of it. This re-run does not clear
the ">1.5-on-a-12-core-host idle" bar the plan itself names any better than the original
session did; per the same L08 reasoning Runs 1-2 recorded this caveat under, the numbers
below are reported as measured, not presented as clean.

#### `single` scenario (Runs 3-4)

| Run | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|
| 3 | 0.7 ms (n=3302) | 1.2 ms (n=5529) | 1.68x | 4.17 s | 0 of 1 |
| 4 | 0.9 ms (n=3139) | 1.0 ms (n=1526) | 1.17x | 1.08 s | 0 of 1 |

Pass bar: under-load p95 <= 2.00x idle p95. **Met** on both runs (3, 4).

#### `concurrent` scenario (Runs 3-4)

| Run | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|
| 3 | 1.0 ms (n=2787) | 2.3 ms (n=9785) | 2.32x | 11.04 s | 6 of 10 |
| 4 | 0.9 ms (n=2903) | 2.1 ms (n=7588) | 2.35x | 7.72 s | 2 of 10 |

Pass bar: under-load p95 <= 2.00x idle p95. **Not met** on either run (3, 4) -- worse than
both of Runs 1-2 (2.02x, 2.45x), consistent with the host being less idle at this re-run
than the original session, not more. Four measurements across two sessions now agree: the
`concurrent` scenario's ratio bar is not demonstrated met on this machine under any
environment condition observed so far.

### Post-fix re-run (Runs 5-6)

Commit under test: `7a61fad` (`perf(app): bound and cache model-body compression`, quick
task 260923-qwr, HEAD at measurement time -- includes `2d47994`,
`perf(app): set the gzip level from measured compression cost`). What changed since Runs
3-4: `_GZIP_LEVEL` is now a measured constant (`1`, `src/spur/app.py`) instead of
Starlette's unmeasured `compresslevel=9` default; and model-body gzip encoding moved out
of `GZipMiddleware` and into `model()`, performed inside `_build_slot()`'s admission
bound and cached in `_EXPORTS` under an encoding-tagged key, so a repeat download of an
already-compressed gear performs zero compressions and takes zero slots. Both runs were
made against the same server in immediate succession, so Run 6 inherits Run 5's
`_EXPORTS` contents (as Run 2 inherited Run 1's, and Run 4 inherited Run 3's): Run 6's
popular gears from Run 5 hit the cached, already-compressed bytes and skip compression
entirely -- close to the E2c repeat-download scenario this fix targets.

**Environment snapshot (2026-09-23, ~13:49-13:50 UTC, immediately before the runs):**

- `docker info`: exit 0.
- `sysctl -n vm.loadavg`, three samples 30 s apart: `{ 4.64 4.37 3.53 }` (13:49:36 UTC),
  `{ 3.58 4.13 3.47 }` (13:50:06 UTC), `{ 2.73 3.88 3.40 }` (13:50:36 UTC).
- Top CPU (`ps -Ao %cpu,comm -r | head -5`), latest sample: OrbStack Helper 19.5%,
  WindowServer 14.0%, airportd 13.4%, iTerm2 6.8%.
- `docker ps --format '{{.Names}} {{.Status}}'`: `spur-spur-1 Up 3 hours (healthy)`,
  `fleet-user Restarting (2)` (pre-existing, unrelated, not touched).

**Environment caveat.** The 1-minute load figure fell across the three samples (4.64 ->
3.58 -> 2.73), ending below both Runs 1-2's pre-run figures (2.35, 2.33) and below Runs
3-4's climbing figures (3.33 -> 3.79 -> 3.96) -- the quietest close of the four sessions
by this measure, though still above the ">1.5-on-a-12-core-host idle" bar this file
itself names. As before (L08), the numbers below are reported as measured, not presented
as clean.

#### `single` scenario (Runs 5-6)

| Run | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|
| 5 | 0.6 ms (n=3666) | 0.7 ms (n=5139) | 1.10x | 3.08 s | 0 of 1 |
| 6 | insufficient (n<20) | insufficient (n=19) | -- | -- | -- |

Pass bar: under-load p95 <= 2.00x idle p95. **Met** on Run 5. Run 6's `single` scenario
printed `warning: single/under-load has only 19 /api/health samples (need >= 20);
refusing to report a p95` -- `bench/latency.py`'s own `MIN_SAMPLES` gate refused to
report a p95 for that series, so no ratio is reported for Run 6's `single` scenario, per
L08 (a wrong number is worse than no number), not filled with a guessed one.

#### `concurrent` scenario (Runs 5-6)

| Run | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|
| 5 | 0.6 ms (n=3601) | 0.8 ms (n=15432) | 1.31x | 10.88 s | 6 of 10 |
| 6 | 0.6 ms (n=3640) | 1.3 ms (n=7769) | 2.10x | 6.52 s | 2 of 10 |

Pass bar: under-load p95 <= 2.00x idle p95. **Met** on Run 5 (1.31x), **Not met** on
Run 6 (2.10x). Run 6 was not restarted or repeated in search of a passing number; both
runs are reported as measured.

The fix moves the `concurrent` ratio from four consecutive failures over two prior
sessions (2.02x, 2.45x, 2.32x, 2.35x) to one clear pass and one narrow miss (1.31x,
2.10x) -- a real improvement, driven by the cache-hit compression this fix bounds and
caches, not by a quieter host alone (the host was not meaningfully quieter than Runs
1-2's start). The `concurrent` scenario's acceptance clause (under-load p95 <= 2.00x idle
p95) is **not** demonstrated met on both runs measured this session: Run 5 clears it,
Run 6 does not.

### Idle-host re-run (Runs 7-8)

Dispatched by the human's choice, after Runs 5-6, to re-measure on a genuinely idle host
rather than waive the ledger item or fix further. Commit under test: `aaf5852` -- the
served code is the Runs 5-6 fix (`7a61fad`; `5a6e7d7` since then changed one comment in
`src/spur/app.py`, nothing executable). Same harness, same server convention
(`SPUR_PORT=8001 make serve`, port 8000 still held by `spur-spur-1`), two runs in
immediate succession against the same server, so Run 8 inherits Run 7's `_EXPORTS`
contents as every even-numbered run before it did.

The host was waited for, not asserted. A manual sample at 14:05:16 UTC read a 1-minute
load of 4.16 with Spotlight (`mds`, 61.6%) and a Time Machine pass (`backupd-helper`,
53.8%) on top; a watcher then sampled `sysctl -n vm.loadavg` every 30 s and released the
runs only after three consecutive samples under the 1.5 bar this file names (1.35, 1.02,
1.05 at 14:09:05-14:10:05 UTC). Nothing was killed; the daemons finished on their own.

**Environment snapshot (2026-09-23, ~14:10-14:11 UTC, immediately before the runs):**

- `docker info`: exit 0.
- `sysctl -n vm.loadavg`, three samples 30 s apart: `{ 1.11 1.85 2.38 }` (14:10:17 UTC),
  `{ 1.20 1.80 2.34 }` (14:10:47 UTC), `{ 1.63 1.85 2.34 }` (14:11:17 UTC).
- Top CPU (`ps -Ao %cpu,comm -r | head -5`), latest sample: WindowServer 44.1%, iTerm2
  21.1%, AlDente 6.4%, claude 6.1%.
- `docker ps --format '{{.Names}} {{.Status}}'`: `spur-spur-1 Up 4 hours (healthy)`,
  `fleet-user Restarting (2)` (pre-existing, unrelated, not touched).
- After both runs: `{ 2.29 1.99 2.37 }`.

**Environment caveat.** The quietest of the four sessions by every sample: the 1-minute
figure was under the 1.5 bar for the two samples before the runs and 1.63 at the third
(cause not identified; `fleet-user` restart-loops every ~40 s throughout). This is the
closest this machine has come to its own idle bar; it is not a lab. Numbers reported as
measured (L08).

#### `single` scenario (Runs 7-8)

| Run | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|
| 7 | 0.6 ms (n=3540) | 0.7 ms (n=5132) | 1.11x | 3.18 s | 0 of 1 |
| 8 | insufficient (n<20) | insufficient (n=18) | -- | -- | -- |

Pass bar: under-load p95 <= 2.00x idle p95. **Met** on Run 7. Run 8 printed `warning:
single/under-load has only 18 /api/health samples (need >= 20); refusing to report a
p95` -- the 200-tooth gear was cached from Run 7, so there was no load window to sample;
no ratio, per L08, exactly as in Run 6.

#### `concurrent` scenario (Runs 7-8)

| Run | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|
| 7 | 0.6 ms (n=3543) | 1.2 ms (n=10527) | 1.86x | 8.77 s | 6 of 10 |
| 8 | 0.6 ms (n=3553) | 1.3 ms (n=7719) | 2.02x | 6.63 s | 2 of 10 |

Pass bar: under-load p95 <= 2.00x idle p95. **Met** on Run 7 (1.86x), **Not met** on
Run 8 (2.02x). Neither run was repeated or restarted in search of a passing number.

**Finding.** The `concurrent` acceptance clause is still not demonstrated on both runs
of one session: post-fix, four runs over two sessions read 1.31x, 2.10x, 1.86x, 2.02x.
Two things are visible in the eight runs now recorded -- stated as observations, not as
causes, because neither was investigated:

1. Every second run of a pair -- the one that inherits the first run's `_EXPORTS` -- is
   worse than its first run, before the fix (2.02x -> 2.45x, 2.32x -> 2.35x) and after it
   (1.31x -> 2.10x, 1.86x -> 2.02x). Post-fix, the inherited cache hits perform no
   compression and take no slot (`tests/test_api.py`,
   `test_an_already_compressed_download_needs_no_slot_at_all`), so whatever makes the
   second run worse is not the mechanism the fix removed.
2. The verdict is being read at the harness's floor: idle p95 is 0.6 ms in six of the
   eight runs (0.9-1.0 ms in Runs 3-4), so the 2.00x bar sits at about 1.2 ms of
   under-load p95, and Run 7 (1.2 ms, 1.86x) and Run 8 (1.3 ms, 2.02x) are separated by
   roughly a tenth of a millisecond of p95.

Both bear on how the bar should be read; neither changes what it says. Not met on both
runs.

### `SPUR_BUILD_TIMEOUT`

Worst single build observed across both runs and both scenarios: **7.39 s** (`concurrent`
run 1). `SPUR_BUILD_TIMEOUT`'s shipped default is set to **30 s** — roughly 4x that
observation — to leave margin for hardware slower than this M2 Max under host contention
(the debt file's own concern: "on slower hardware... the stall is proportionally worse").
See `src/spur/app.py`'s `int_env("SPUR_BUILD_TIMEOUT", 30)` for the comment naming this
observation.

## Memory

`make bench.memory` (`.venv/bin/python -m bench.memory sweep`, then `confirm 4g`) against
`docker compose`, the same 40-gear corpus L07's `2g` was earned against (`bench/corpus.py`,
D-18). Docker: `docker info` exit 0, Docker Compose v5.1.2, Docker 29.4.0. Run in the same
session as the Latency numbers above, same machine, ~09:50-10:35 UTC.

### Two blocking issues found and fixed before this data could be trusted

1. **The pre-existing `mem_limit: 2g` was silently capping the sweep it was supposed to be
   replaced by.** `compose.yaml` was already at `SPUR_WORKERS: "1"` / `SPUR_BUILD_WORKERS:
   "2"` (this task's own first edit, done before the first sweep) but still carried the
   old, superseded `mem_limit: 2g`. That first sweep attempt gave N=2 and N=4 identical
   peaks of exactly `2048.0 MiB` — the `2g` limit itself, not a real footprint — with N=4
   additionally failing 2 of 40 requests to OOM pressure at that cap. `mem_limit` was
   temporarily raised to `8g` for the sweep so the measurement could not be capped by the
   value it exists to determine, then set back to the real, measured value below. Only the
   runs at the relaxed limit are reported here.
2. **`docker/smoke.py` and `docker compose build` both failed** against the pool topology:
   `docker/smoke.py` calls the ASGI app directly (`await app(scope, receive, send)`),
   which never runs `app.py`'s `lifespan` -- so `app.state.pool` was never set, and
   `build_backend()` hard-fails by design (02-01-SUMMARY.md). Fixed by driving the
   lifespan explicitly via `app.router.lifespan_context(app)`. That surfaced a second bug:
   the script's unguarded module-level `anyio.run(main)` recursed under `spawn`
   multiprocessing (which re-imports `__main__` in the child) once a build actually tried
   to spawn a worker; fixed with the standard `if __name__ == "__main__":` guard. The image
   in place before this task predated all of Phase 2's code (45 hours old); a rebuild was
   required regardless, and would have hit this the first time anyone rebuilt the image
   locally or in CI.

### Sweep (SPUR_WORKERS=1, mem_limit temporarily relaxed to 8g)

| N (SPUR_BUILD_WORKERS) | Peak | Early peak | Late peak | Requests | Failures | Elapsed |
|---|---|---|---|---|---|---|
| 1 | 2052.1 MiB | 2052.1 MiB | 1833.0 MiB | 40 | 0 | 276.8s |
| 2 | 2878.5 MiB | 2566.1 MiB | 2878.5 MiB | 40 | 0 | 284.3s |
| 4 | 4731.9 MiB | 4155.4 MiB | 4731.9 MiB | 40 | 0 | 292.8s |

Peak read from `docker stats --no-stream` MEM USAGE, polled every 0.5s (a sampled peak,
not the cgroup's exact accounting). Early/late peak: max of the first half vs second half
of that N's samples, in run order (D-11 drift check). A second, otherwise-identical sweep
run immediately before this one (also uncapped) gave peaks of 2015.2 / 2821.1 / 4502.5 MiB
for N=1/2/4 -- run-to-run variance of roughly 2-5%, the noise floor for this measurement.

**Formula in words (D-06): parent byte budget + N x solid cache.** The naive version of
that formula -- `SPUR_EXPORT_CACHE_MB` (64 MiB) + N x `SPUR_SOLID_CACHE` (4) x one solid
(~280 MiB) -- predicts roughly 1184 / 2304 / 4544 MiB for N=1/2/4. The measured peaks
(2052 / 2879 / 4732 MiB) are all higher, by an amount that grows with N: each additional
build worker costs roughly 810-870 MiB here (N=1->2: +826 MiB; N=2->4: +927 MiB average
per added worker), not the ~1120 MiB the naive cache-only term would predict alone, nor
small enough to be cache-only. The gap is each worker's own baseline footprint --
`cadquery`/OCP/VTK loaded once per worker process (D-04's warm-up) -- which is resident
memory but not a "cache" in D-06's sense; the naive formula omits it because L07's original
version only ever had to account for one process. The observed numbers, not the naive
formula, are what set `mem_limit` below.

**Drift (D-11):** N=1's late-half peak is *lower* than its early-half peak (1833.0 vs
2052.1 MiB) -- no growth. N=2 and N=4 both show late > early (2879 vs 2566 MiB; 4732 vs
4155 MiB). This is not treated as evidence of a leak `malloc_trim(0)` fails to flatten:
`bench/corpus.py`'s corpus is strictly ascending tooth count (160 -> 199), so the "late"
half of any run is inherently the biggest gears in the corpus, and each worker's bounded,
4-entry solid cache (`SPUR_SOLID_CACHE`) holding increasingly large solids as the corpus
advances grows resident memory for that reason alone -- no leak required to explain it. No
run showed unbounded growth, a growing failure rate, or an elapsed time trending up across
repeated sweeps (276-293s across three runs). `max_tasks_per_child` stays off; see
`src/spur/pool.py`'s comment on `BuildPool.__init__` for the same reasoning, so the two
never drift apart.

### `mem_limit`: earned, not asserted

Shipping default is N=2 (`SPUR_BUILD_WORKERS=2`, D-19). Measured peak: **2878.5 MiB**.
Headroom factor: **x1.3** (a named 30%, chosen for margin over run-to-run noise and gears
outside the 40-gear corpus, without being arbitrarily large) = 3742.05 MiB, rounded up to
a clean value: **4g**.

Confirm run, `.venv/bin/python -m bench.memory confirm 4g` (`SPUR_BUILD_WORKERS=2`, the
full 40-gear corpus): **0 of 40 requests failed** -- the same bar `2g` cleared and `1g`
did not, before this phase (`docs/plan-2026-09-21.md`). No lower value was attempted or
needed; `4g` cleared on the first try.

`compose.yaml` now ships `SPUR_WORKERS: "1"`, `SPUR_BUILD_WORKERS: "2"` and
`mem_limit: 4g`, with the comment above `mem_limit` naming this peak, this headroom
factor and this confirm result.

## Regression fixture cost (Phase 7, D-06)

The committed measurement record for `tests/regression/` (`docs/tech_debt/active/
2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md`, `REQ-defaults-off-regression`,
D-06). D-06 requires the fixture's cost to `make verify` measured — two runs each way,
same session — and a delta above 15.0 s to halt for a human trim decision instead of a
silent subset.

### Host state

- CPU: Apple M2 Max, 12 cores
- RAM: 32.0 GiB
- Python: 3.12.13 (`.venv`)
- Date: 2026-09-26, ~12:20-12:26 UTC
- HEAD: `7cb4eb6` (`test(07-01): pin every pre-v0.2 parameter set in the regression fixture`)
- `uptime` load averages at the start of this session: 2.34, 2.49, 2.19 — above this
  project's usual "quiet" bar (`bench/RESULTS.md`'s Latency section names >1.5 on a
  12-core host); the numbers below carry that caveat rather than being presented as
  clean (L08).

### Same-session, alternating runs

Same HEAD, same session, alternating `--ignore=tests/regression` (A) against the full
suite (B), twice each, to average out one noisy sample:

| Run | Command | Result |
|---|---|---|
| A1 | `make test PYTEST_ARGS="--ignore=tests/regression -q"` | 191 passed in 32.05s |
| B1 | `make test PYTEST_ARGS="-q"` | 276 passed in 48.41s |
| A2 | `make test PYTEST_ARGS="--ignore=tests/regression -q"` | 191 passed in 32.15s |
| B2 | `make test PYTEST_ARGS="-q"` | 276 passed in 48.33s |

mean(A) = 32.10s, mean(B) = 48.37s -> **delta = 16.27s**, above the D-06 15.0s line.

### D-06 gate: human decision

The delta (16.27s) exceeded the 15.0s line, so this halted for a `checkpoint:decision`
per D-06 and prohibition 2 (no silent subset). Planning-time evidence going into that
decision: two standalone probes of the 39 builds alone, on this machine, on 2026-09-25,
took 15.66s and 15.83s (load average 1.4-2.4) — the gate was expected to sit near the
line before this session ever ran.

**Decision: Option A — accept the measured cost, keep every one of the 44 records
built.** Reason: 16.27s sits under the planner's own ~20s ceiling for accepting the cost
as-is; the cost is spread across all 39 builds (see durations below — no single outlier
build dominates), not concentrated in a few sets that could be dropped cheaply; and
Success Metric 3 ("old links unchanged") is kept literal — every pre-v0.2 hand-written
parameter set, not a curated subset. No record was narrowed, dropped, marked slow, or
given a loosened tolerance (prohibition 2).

### Ten slowest regression fixture cases

`make test PYTEST_ARGS="tests/regression -q --durations=10"`: 85 passed in 18.24s.

| Duration | Case |
|---|---|
| 0.81s | `test_calc.py::test_root_fillet_is_capped_with_a_warning` (build) |
| 0.78s | `test_calc.py::test_oversized_recess_is_narrowed_to_fit_and_says_so` (build) |
| 0.77s | `test_calc.py::test_recess_fillet_is_capped_to_the_narrowed_groove` (build) |
| 0.76s | `test_api.py::test_an_unclassified_exception_still_emits_build_failed_and_is_not_swallowed` (build) |
| 0.75s | `test_api.py::test_a_failed_build_emits_build_failed_naming_the_class_and_the_level` (build) |
| 0.74s | `test_api.py::test_a_saturated_service_emits_queue_refused_naming_the_gear_and_the_ceiling` (build) |
| 0.67s | `README:export-teeth-24` (build) |
| 0.67s | `test_api.py::test_two_requests_for_one_gear_get_two_different_request_ids` (build) |
| 0.65s | `test_api.py::test_a_repeat_download_is_served_from_cache_with_zero_duration_and_no_build_started` (build) |
| 0.65s | `test_api.py::test_a_gzip_request_after_an_identity_download_emits_source_compressed` (build) |

No outlier: the slowest and tenth-slowest builds differ by 0.16s, and the cost is spread
evenly across the 39 `build()` calls the fixture makes, matching the Decision A rationale
above.

### `make verify` wall time

`time make verify`: **49.51s** total, against the recorded pre-fixture baseline of
**32.47s** / 191 tests at `b3ca789` (this phase's own CONTEXT.md).

### Tripwire proof

`.venv/bin/python -c "import sys, pytest, spur.model as m; m._bore_rim_edges = lambda
*a, **k: []; sys.exit(pytest.main(['tests/regression', '-q', '-p',
'no:cacheprovider']))"` — the Phase 8 hex-selector defect in miniature: a bore-rim
selector that silently selects no edges, handed to `.chamfer()`.

Result: **32 failed, 53 passed in 13.46s** — exactly the 32 base records whose params
have `bore_d > 0` and `bore_chamfer > 0` went red on their solid case; every derive case,
the 7 bore-less or chamfer-less solid cases, the corpus-coverage test and the
kernel-version test stayed green. `git status --porcelain -- src tests` printed nothing
afterwards — the monkeypatch was in-process only, no file was touched. The fixture
catches a silently vanished chamfer.

### After the selector change (07-02)

`calc.bore_rim_limit(p)`, `model.BORE_RIM_SLACK`, the two `BuildError` guards and their
tests (D-15/D-16/D-17/D-18) added 13 tests (1 `calc.py` unit test, 10 selector-matrix
rows, 2 zero-edge refusals) on top of 07-01's 276. `tests/regression/pre_v0_2.json` was
never touched by this plan (`git diff --exit-code`, run after every task) — the
selector change is behaviour-neutral for every pre-v0.2 set.

#### Host state

- CPU: Apple M2 Max, 12 cores
- RAM: 32.0 GiB
- Python: 3.12.13 (`.venv`)
- Date: 2026-09-26, ~12:48 local (06:48 UTC)
- HEAD: `bd4e477` (`feat(07-02): refuse an empty recess-floor selection and count both
  selectors per bore shape`)
- `uptime` load averages at measurement: 2.58, 2.47, 2.47 — same "not quiet" host as
  07-01's session (>1.5 on this 12-core machine); carried as a caveat, not cleaned up
  (L08).

#### `make verify`, two runs

| Run | Result | Wall time |
|---|---|---|
| 1 | `289 passed in 51.39s` | 52.30s (`time`, includes lint/typecheck/import-lint/no-fake-done) |
| 2 | `289 passed in 51.28s` | 52.19s |

mean(`make verify`) = **52.25s**, against 07-01's recorded **49.51s** (276 tests) and this
phase's own pre-fixture baseline of **32.47s** / 191 tests at `b3ca789` — a **+2.74s**
delta over 07-01 for these 13 new tests, and **+19.78s** over the pre-Phase-7 baseline
(07-01's fixture plus 07-02's selector tests combined). No D-06-style gate applies here:
D-06 named a ~15.0s line for the *fixture's* build cost specifically; the selector tests
build far fewer solids (13 new tests vs. 39 fixture builds) and this delta was not the
subject of that decision.

#### Selector test durations

`make test PYTEST_ARGS="tests/test_model.py tests/test_calc.py -q --durations=15"`:
**50 passed in 10.61s**.

| Duration | Case |
|---|---|
| 1.24s | `test_model.py::test_an_stl_export_matches_a_first_export_whatever_came_before` |
| 0.65s | `test_model.py::test_a_gear_too_small_for_the_stock_recess_still_builds` |
| 0.51s | `test_model.py::test_recess_removes_expected_volume` |
| 0.46s | `test_model.py::test_builds_one_valid_solid[kw1]` |
| 0.44s | `test_model.py::test_builds_one_valid_solid[kw8]` |
| 0.43s | `test_model.py::test_builds_one_valid_solid[kw0]` |
| 0.43s | `test_model.py::test_exports` |
| 0.42s | `test_model.py::test_builds_one_valid_solid[kw6]` |
| 0.41s | `test_model.py::test_builds_one_valid_solid[kw2]` |
| 0.38s | `test_model.py::test_each_edge_selector_picks_exactly_its_own_edges[d-flat-both]` |
| 0.37s | `test_model.py::test_each_edge_selector_picks_exactly_its_own_edges[round-both]` |
| 0.35s | `test_model.py::test_a_bore_chamfer_that_selects_no_rim_edges_is_a_build_error_not_a_bare_bore` |
| 0.29s | `test_model.py::test_builds_one_valid_solid[kw5]` |
| 0.26s | `test_model.py::test_each_edge_selector_picks_exactly_its_own_edges[d-flat-top]` |
| 0.25s | `test_model.py::test_each_edge_selector_picks_exactly_its_own_edges[d-flat-bottom]` |

No outlier: the ten selector-matrix rows and two refusal tests each build one gear
(≤0.4s), the same shape as the fixture's own cost.

## Hex bore build and export time (Phase 8, D-11)

The committed measurement record for the hex bore's heaviest allowed configuration
(ROADMAP Phase 8 SC4, D-11). `REQ-measured-build-time` asks for build time plus fine-STL
and STEP export time per feature, at 200 teeth, re-measured combined in Phase 12; this is
the hex bore's own entry. The runner is `make bench.build` (D-12,
`bench/build_time.py`), over the committed sweep `bench/sweeps/hex_bore.json`. The sweep
has 16 rows, not 8, because the planning probe found module drives fine-STL export time
(0.64s to 1.14s and 10.2 MB to 15.7 MB at `bore_hex` 200, recess both, chamfer 3), so
module {1.75, 10} joins `bore_hex` {200, 12.7} x `recess_sides` {both, none} x
`bore_chamfer` {0.4, 3} — D-11's own condition. 3 mm is the chamfer maximum because the
field's `le` is 3 mm, and at 200 teeth neither hex rule binds: measured this session, the
chamfered mouth reaches 119.02 mm against the root-circle limit of 172.41 mm
(`rf - MIN_WALL`).

### Host state

- Machine: 12 CPUs, arm64, 32.0 GiB RAM
- Python: 3.12.13
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `a3a651b`
- Sweep: `bench/sweeps/hex_bore.json`
- Load averages at start (script's own `os.getloadavg()`): 3.47, 3.12, 2.67
- `uptime` at the same time: load averages 4.78, 3.23, 2.68
- SPUR_BUILD_TIMEOUT: 30 s, a cold request is one build plus one export
- Both readings sit above this project's usual "quiet" bar (>1.5 on this 12-core host,
  Phase 7's own convention) — the numbers below carry that caveat rather than being
  presented as clean (L08).

### Sweep

| Parameter set | Build (s) | Fine STL (s) | STEP (s) | Build + slower export (s) | Inside 30 s |
|---|---|---|---|---|---|
| teeth=200 module=1.75 bore_hex=200 recess_sides=both bore_chamfer=0.4 | 4.44 | 0.64 | 0.40 | 5.08 | yes |
| teeth=200 module=1.75 bore_hex=200 recess_sides=both bore_chamfer=3 | 4.32 | 0.61 | 0.39 | 4.93 | yes |
| teeth=200 module=1.75 bore_hex=200 recess_sides=none bore_chamfer=0.4 | 1.57 | 0.49 | 0.40 | 2.06 | yes |
| teeth=200 module=1.75 bore_hex=200 recess_sides=none bore_chamfer=3 | 1.58 | 0.50 | 0.40 | 2.07 | yes |
| teeth=200 module=1.75 bore_hex=12.7 recess_sides=both bore_chamfer=0.4 | 2.13 | 0.72 | 0.39 | 2.85 | yes |
| teeth=200 module=1.75 bore_hex=12.7 recess_sides=both bore_chamfer=3 | 2.14 | 0.72 | 0.39 | 2.85 | yes |
| teeth=200 module=1.75 bore_hex=12.7 recess_sides=none bore_chamfer=0.4 | 1.58 | 0.52 | 0.39 | 2.10 | yes |
| teeth=200 module=1.75 bore_hex=12.7 recess_sides=none bore_chamfer=3 | 1.58 | 0.52 | 0.40 | 2.10 | yes |
| teeth=200 module=10 bore_hex=200 recess_sides=both bore_chamfer=0.4 | 2.13 | 1.11 | 0.40 | 3.24 | yes |
| teeth=200 module=10 bore_hex=200 recess_sides=both bore_chamfer=3 | 2.15 | 1.10 | 0.40 | 3.25 | yes |
| teeth=200 module=10 bore_hex=200 recess_sides=none bore_chamfer=0.4 | 1.58 | 0.58 | 0.40 | 2.15 | yes |
| teeth=200 module=10 bore_hex=200 recess_sides=none bore_chamfer=3 | 1.58 | 0.57 | 0.40 | 2.15 | yes |
| teeth=200 module=10 bore_hex=12.7 recess_sides=both bore_chamfer=0.4 | 2.16 | 1.14 | 0.40 | 3.30 | yes |
| teeth=200 module=10 bore_hex=12.7 recess_sides=both bore_chamfer=3 | 2.13 | 1.13 | 0.41 | 3.26 | yes |
| teeth=200 module=10 bore_hex=12.7 recess_sides=none bore_chamfer=0.4 | 1.58 | 0.58 | 0.40 | 2.16 | yes |
| teeth=200 module=10 bore_hex=12.7 recess_sides=none bore_chamfer=3 | 1.58 | 0.58 | 0.41 | 2.16 | yes |

**Heaviest:** teeth=200 module=1.75 bore_hex=200 recess_sides=both bore_chamfer=0.4 --
5.08 s of 30 s.

The heaviest row (5.08 s) sits at about a sixth of the 30 s timeout, and below the worst
single build already on record ("### `SPUR_BUILD_TIMEOUT`" above, 7.39 s at 200 teeth
under ten concurrent requests) — the hex bore's heaviest configuration costs less than
the plain round bore already did under load.

### make verify wall time

`time make verify`: **330 passed in 60.79s** — **61.74s** wall time (`time`, includes
lint/typecheck/import-lint/no-fake-done), against Phase 7's recorded **52.25s** / 289
tests. The phase's hex tests (41 new: the D-01/D-02/D-03/D-04/D-05 unit and matrix tests,
the two new test_bench.py cases) add **+9.49s** to the gate, measured rather than
assumed.

## Keyway bore build and export time (Phase 9)

The committed measurement record for the keyway bore's heaviest allowed configuration
(ROADMAP Phase 9 SC5, D-11/D-12's shape). `REQ-measured-build-time` asks for build time
plus fine-quality STL and STEP export time per feature, at 200 teeth, re-measured
combined in Phase 12; this is the keyway's own entry. The runner is `make bench.build`
(08 D-12), over the committed sweep `bench/sweeps/keyway_bore.json`, reused unchanged
from Phase 8. The sweep has 32 rows: 200 teeth on the largest bore the rules allow
(`bore_d` 200, the field's `le`), module {1.75, 10} because module drives fine-STL export
time (Phase 8's probe), round and D-flat {`bore_flat` 0, 150} because the D-flat is the
composition D-02 guards, `bore_chamfer` {0.4, 3} (3 is the field's `le`; D-12's rule does
not bind here -- the chamfered mouth reaches 103.075 mm from the axis at module 1.75,
69.74 mm inside the 172.8125 mm root radius), and, for each (module, `bore_flat`) pair,
both the largest keyway the rules allow (199.95 x 40.3 round / 99.3 x 65 D-flat at module
1.75; 199.95 x 200 round / 99.3 x 200 D-flat at module 10, where `keyway_depth`'s own
`le` binds before the root ever would) and a 3 x 1.4 mm keyway. The 3 x 1.4 rows are in
the sweep, not just the largest keyway, because the planning probe found the largest
keyway at module 1.75 pushes the face recess out entirely, making those rows lighter
than a keyed gear that keeps its recess (09-CONTEXT.md Claude's Discretion: sweep rows)
-- the heaviest configuration is found by measuring both, not by assuming the biggest
keyway is the heaviest.

### Host state

- Machine: 12 CPUs, arm64, 32.0 GiB RAM
- Python: 3.12.13
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `575b3a9`
- Sweep: `bench/sweeps/keyway_bore.json`
- Load averages at start (script's own `os.getloadavg()`): 6.10, 5.08, 4.98
- `uptime` moments before the run: load averages 4.87, 4.33, 4.74
- SPUR_BUILD_TIMEOUT: 30 s, a cold request is one build plus one export
- Both readings sit above this project's usual "quiet" bar (>1.5 on this 12-core host,
  Phase 7's own convention) -- the numbers below carry that caveat rather than being
  presented as clean (L08).

### Sweep

| Parameter set | Build (s) | Fine STL (s) | STEP (s) | Build + slower export (s) | Inside 30 s |
|---|---|---|---|---|---|
| teeth=200 module=1.75 bore_d=200 bore_flat=0 keyway_width=199.95 keyway_depth=40.3 recess_sides=both bore_chamfer=0.4 | 1.93 | 0.61 | 0.41 | 2.54 | yes |
| teeth=200 module=1.75 bore_d=200 bore_flat=0 keyway_width=199.95 keyway_depth=40.3 recess_sides=both bore_chamfer=3 | 1.86 | 0.59 | 0.41 | 2.46 | yes |
| teeth=200 module=1.75 bore_d=200 bore_flat=0 keyway_width=199.95 keyway_depth=40.3 recess_sides=none bore_chamfer=0.4 | 1.88 | 0.58 | 0.41 | 2.46 | yes |
| teeth=200 module=1.75 bore_d=200 bore_flat=0 keyway_width=199.95 keyway_depth=40.3 recess_sides=none bore_chamfer=3 | 1.88 | 0.58 | 0.42 | 2.46 | yes |
| teeth=200 module=1.75 bore_d=200 bore_flat=0 keyway_width=3 keyway_depth=1.4 recess_sides=both bore_chamfer=0.4 | 4.17 | 0.66 | 0.43 | 4.83 | yes |
| teeth=200 module=1.75 bore_d=200 bore_flat=0 keyway_width=3 keyway_depth=1.4 recess_sides=both bore_chamfer=3 | 4.11 | 0.66 | 0.41 | 4.78 | yes |
| teeth=200 module=1.75 bore_d=200 bore_flat=0 keyway_width=3 keyway_depth=1.4 recess_sides=none bore_chamfer=0.4 | 1.88 | 0.73 | 0.41 | 2.62 | yes |
| teeth=200 module=1.75 bore_d=200 bore_flat=0 keyway_width=3 keyway_depth=1.4 recess_sides=none bore_chamfer=3 | 1.81 | 0.70 | 0.41 | 2.52 | yes |
| teeth=200 module=1.75 bore_d=200 bore_flat=150 keyway_width=99.3 keyway_depth=65 recess_sides=both bore_chamfer=0.4 | 1.97 | 0.58 | 0.41 | 2.55 | yes |
| teeth=200 module=1.75 bore_d=200 bore_flat=150 keyway_width=99.3 keyway_depth=65 recess_sides=both bore_chamfer=3 | 1.95 | 0.58 | 0.42 | 2.53 | yes |
| teeth=200 module=1.75 bore_d=200 bore_flat=150 keyway_width=99.3 keyway_depth=65 recess_sides=none bore_chamfer=0.4 | 1.96 | 0.57 | 0.41 | 2.53 | yes |
| teeth=200 module=1.75 bore_d=200 bore_flat=150 keyway_width=99.3 keyway_depth=65 recess_sides=none bore_chamfer=3 | 1.96 | 0.57 | 0.42 | 2.53 | yes |
| teeth=200 module=1.75 bore_d=200 bore_flat=150 keyway_width=3 keyway_depth=1.4 recess_sides=both bore_chamfer=0.4 | 4.20 | 0.66 | 0.41 | 4.85 | yes |
| teeth=200 module=1.75 bore_d=200 bore_flat=150 keyway_width=3 keyway_depth=1.4 recess_sides=both bore_chamfer=3 | 4.16 | 0.68 | 0.41 | 4.84 | yes |
| teeth=200 module=1.75 bore_d=200 bore_flat=150 keyway_width=3 keyway_depth=1.4 recess_sides=none bore_chamfer=0.4 | 1.96 | 0.62 | 0.41 | 2.58 | yes |
| teeth=200 module=1.75 bore_d=200 bore_flat=150 keyway_width=3 keyway_depth=1.4 recess_sides=none bore_chamfer=3 | 1.91 | 0.61 | 0.41 | 2.52 | yes |
| teeth=200 module=10 bore_d=200 bore_flat=0 keyway_width=199.95 keyway_depth=200 recess_sides=both bore_chamfer=0.4 | 2.64 | 1.17 | 0.41 | 3.81 | yes |
| teeth=200 module=10 bore_d=200 bore_flat=0 keyway_width=199.95 keyway_depth=200 recess_sides=both bore_chamfer=3 | 2.65 | 1.15 | 0.41 | 3.80 | yes |
| teeth=200 module=10 bore_d=200 bore_flat=0 keyway_width=199.95 keyway_depth=200 recess_sides=none bore_chamfer=0.4 | 1.87 | 0.72 | 0.41 | 2.59 | yes |
| teeth=200 module=10 bore_d=200 bore_flat=0 keyway_width=199.95 keyway_depth=200 recess_sides=none bore_chamfer=3 | 1.88 | 0.75 | 0.42 | 2.63 | yes |
| teeth=200 module=10 bore_d=200 bore_flat=0 keyway_width=3 keyway_depth=1.4 recess_sides=both bore_chamfer=0.4 | 2.67 | 1.14 | 0.42 | 3.81 | yes |
| teeth=200 module=10 bore_d=200 bore_flat=0 keyway_width=3 keyway_depth=1.4 recess_sides=both bore_chamfer=3 | 2.63 | 1.15 | 0.41 | 3.78 | yes |
| teeth=200 module=10 bore_d=200 bore_flat=0 keyway_width=3 keyway_depth=1.4 recess_sides=none bore_chamfer=0.4 | 1.87 | 1.11 | 0.42 | 2.97 | yes |
| teeth=200 module=10 bore_d=200 bore_flat=0 keyway_width=3 keyway_depth=1.4 recess_sides=none bore_chamfer=3 | 1.81 | 1.13 | 0.41 | 2.94 | yes |
| teeth=200 module=10 bore_d=200 bore_flat=150 keyway_width=99.3 keyway_depth=200 recess_sides=both bore_chamfer=0.4 | 2.67 | 1.13 | 0.41 | 3.80 | yes |
| teeth=200 module=10 bore_d=200 bore_flat=150 keyway_width=99.3 keyway_depth=200 recess_sides=both bore_chamfer=3 | 2.66 | 1.15 | 0.41 | 3.81 | yes |
| teeth=200 module=10 bore_d=200 bore_flat=150 keyway_width=99.3 keyway_depth=200 recess_sides=none bore_chamfer=0.4 | 2.00 | 0.67 | 0.41 | 2.67 | yes |
| teeth=200 module=10 bore_d=200 bore_flat=150 keyway_width=99.3 keyway_depth=200 recess_sides=none bore_chamfer=3 | 2.00 | 0.68 | 0.42 | 2.68 | yes |
| teeth=200 module=10 bore_d=200 bore_flat=150 keyway_width=3 keyway_depth=1.4 recess_sides=both bore_chamfer=0.4 | 2.67 | 1.16 | 0.42 | 3.83 | yes |
| teeth=200 module=10 bore_d=200 bore_flat=150 keyway_width=3 keyway_depth=1.4 recess_sides=both bore_chamfer=3 | 2.65 | 1.14 | 0.42 | 3.79 | yes |
| teeth=200 module=10 bore_d=200 bore_flat=150 keyway_width=3 keyway_depth=1.4 recess_sides=none bore_chamfer=0.4 | 1.98 | 0.79 | 0.41 | 2.77 | yes |
| teeth=200 module=10 bore_d=200 bore_flat=150 keyway_width=3 keyway_depth=1.4 recess_sides=none bore_chamfer=3 | 1.90 | 0.81 | 0.41 | 2.71 | yes |

**Heaviest:** teeth=200 module=1.75 bore_d=200 bore_flat=150 keyway_width=3 keyway_depth=1.4 recess_sides=both bore_chamfer=0.4 -- 4.85 s of 30 s.

The heaviest row (4.85 s) sits at about a sixth of the 30 s timeout, close to but lighter
than Phase 8's heaviest hex row (5.08 s), and well below the worst single build already
on record ("### `SPUR_BUILD_TIMEOUT`" above, 7.39 s at 200 teeth under ten concurrent
requests) -- as the planning probe predicted, the heaviest keyway row is a 3 x 1.4 mm
keyway that keeps its face recess, not the largest keyway the rules allow, which pushes
the recess out entirely and builds in about half the time (2.46-2.55 s at module 1.75).

### make verify wall time

`time make verify`: **396 passed in 77.20s** — **78.21s** wall time (`time`, includes
lint/typecheck/import-lint/no-fake-done), against Phase 8's recorded **61.74s** / 330
tests. The phase's keyway tests (66 new, across 09-01 through 09-04) add **+16.47s** to
the gate, measured rather than assumed.

## Tooth-tip chamfer spike (Phase 10, D-05)

The committed measurement record for the ROADMAP Phase 10 research flag:
`Mixin3D.chamfer()` on up to 400 edges is the one v0.2 operator in L09's cost family,
and this phase measures it before the cap is designed (D-05). The probe chamfers the
`2 x teeth` end-face tip-arc edges (`bench/tip_chamfer_spike.py`'s `tip_arcs`) through
`spur.model._build_checked` plus one `chamfer()` call, with no `tip_chamfer` field in
`GearParams` yet -- the field, the cap and the selector are 10-02 through 10-05, planned
on these numbers. Command: `.venv/bin/python -m bench.tip_chamfer_spike`.

### Host state

- Machine: 12 CPUs, arm64, 32.0 GiB RAM
- Python: 3.12.13
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `56daf85`
- Load averages at start (script's own `os.getloadavg()`): 7.18, 5.62, 4.11
- `uptime` moments before the run: load averages 7.72, 5.70, 4.12
- SPUR_BUILD_TIMEOUT: 30 s
- Both readings sit well above this project's usual "quiet" bar (>1.5 on this 12-core
  host, Phase 7's own convention) -- the numbers below carry that caveat rather than
  being presented as clean (L08).

### Cost

| Set | Arcs | Per face | Bare (s) | Chamfer (s) | STL (s) | STEP (s) | Request (s) | dFaces | dCone | dEdges | dVolume | BBox moved | Why |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| teeth=19 c=0.4 | 38 | 19/19 | 0.38 | 0.32 | 0.07 | 0.04 | 0.77 | 38 | 38 | 114 | -2.88 | 7.11e-15 | ok |
| teeth=19 c=1.75 | 38 | 19/19 | 0.39 | 0.51 | 0.07 | 0.04 | 0.96 | 38 | 38 | 114 | -86.22 | 7.11e-15 | ok |
| teeth=40 c=0.4 | 80 | 40/40 | 0.36 | 0.88 | 0.14 | 0.08 | 1.38 | 80 | 80 | 240 | -6.67 | 0.00e+00 | ok |
| teeth=40 c=1.75 | 80 | 40/40 | 0.37 | 1.07 | 0.14 | 0.09 | 1.58 | 80 | 80 | 240 | -186.12 | 8.88e-16 | ok |
| teeth=200 c=0.4 | 400 | 200/200 | 2.24 | 12.50 | 0.87 | 0.50 | 15.61 | 400 | 400 | 1200 | -35.84 | 8.88e-16 | ok |
| teeth=200 c=1.75 | 400 | 200/200 | 2.22 | 12.81 | 0.72 | 0.50 | 15.76 | 400 | 400 | 1200 | -950.48 | 8.88e-16 | ok |
| teeth=19 module=10 c=0.4 | 38 | 19/19 | 0.19 | 0.34 | 0.20 | 0.04 | 0.73 | 38 | 38 | 114 | -15.56 | 0.00e+00 | ok |
| teeth=19 module=10 c=3.375 | 38 | 19/19 | 0.19 | 0.42 | 0.19 | 0.04 | 0.80 | 38 | 38 | 114 | -1384.38 | 8.88e-16 | ok |
| teeth=40 module=10 c=0.4 | 80 | 40/40 | 0.36 | 0.81 | 0.31 | 0.08 | 1.48 | 80 | 80 | 240 | -36.75 | 0.00e+00 | ok |
| teeth=40 module=10 c=3.375 | 80 | 40/40 | 0.36 | 0.90 | 0.31 | 0.08 | 1.57 | 80 | 80 | 240 | -3121.42 | 8.88e-16 | ok |
| teeth=200 module=10 c=0.4 | 400 | 200/200 | 2.22 | 11.85 | 1.28 | 0.54 | 15.35 | 400 | 400 | 1200 | -200.53 | 9.06e-14 | ok |
| teeth=200 module=10 c=3.375 | 400 | 200/200 | 2.22 | 12.38 | 1.24 | 0.52 | 15.84 | 400 | 400 | 1200 | -16465.09 | 8.88e-16 | ok |
| teeth=19 module=0.2 backlash=0 bore_d=0 c=0.05 | 38 | 19/19 | 0.04 | 0.29 | 0.05 | 0.04 | 0.39 | 38 | 38 | 114 | -0.01 | 8.88e-16 | ok |
| teeth=19 module=0.2 backlash=0 bore_d=0 c=0.2 | 38 | 19/19 | 0.04 | 0.32 | 0.05 | 0.04 | 0.41 | 38 | 38 | 114 | -0.14 | 8.88e-16 | ok |
| teeth=40 module=0.2 backlash=0 bore_d=0 c=0.05 | 80 | 40/40 | 0.80 | 0.79 | 0.08 | 0.07 | 1.67 | 80 | 80 | 240 | -0.01 | 0.00e+00 | ok |
| teeth=40 module=0.2 backlash=0 bore_d=0 c=0.2 | 80 | 40/40 | 0.78 | 0.83 | 0.08 | 0.07 | 1.69 | 80 | 80 | 240 | -0.30 | 8.88e-16 | ok |
| teeth=200 module=0.2 backlash=0.07 c=0.05 | 400 | 200/200 | 3.08 | 12.27 | 0.55 | 0.52 | 15.90 | 400 | 400 | 1200 | -0.04 | 1.78e-15 | ok |
| teeth=200 module=0.2 backlash=0.07 c=0.2 | 400 | 200/200 | 3.03 | 12.27 | 0.53 | 0.50 | 15.83 | 400 | 400 | 1200 | -0.95 | 8.88e-16 | ok |

All 18 rows read `ok`: exactly `2 x teeth` tip arcs split evenly across both end faces,
`+2 x teeth` CONE faces, `+6 x teeth` edges, volume strictly smaller, bounding box
unchanged within `TOL` (D-12). The chamfer call is the dominant cost at 200 teeth: it is
77-82% of every 200-tooth row's request time (12.50-12.81s of a 15.35-15.90s request
across the six 200-tooth rows). Cost scales with edge count, not chamfer size or module:
38 edges cost 0.29-0.51s to chamfer, 80 edges 0.79-1.07s, 400 edges 11.85-12.81s --
worse than linear (roughly 30x from 38 to 400 edges, not the ~10.5x edge-count ratio),
matching L09's family (OCCT's fillet/chamfer machinery scales with simultaneous edge
count). Whether the time moves with `c`: at 200 teeth, chamfering from the small `c` to
the analytic-cap `c` changes the chamfer time by only 0.3-0.5s (2-4%) at module 1.75 and
10, and by 0.00s at module 0.2 -- inside this session's run-to-run noise (host load 7.18
at start, well above the 1.5 "quiet" bar). At 19/40 teeth the same comparison shows a
larger *proportional* swing (e.g. teeth=19: 0.32s -> 0.51s), but the absolute difference
(0.19-0.20s) is the same order as the 200-tooth swing -- consistent with the cost being
driven by edge count, with `c` and module contributing at most session noise, not a real
per-mm cost. **A smaller chamfer is not meaningfully cheaper**: D-07's first offer (a
lower `tip_chamfer` `le`) would not have reduced the 200-tooth chamfer cost, because that
cost is set by how many edges are chamfered in one call, not by how deep the chamfer is.
The heaviest 200-tooth request (module=0.2, backlash=0.07, `c`=0.05) reads **15.90s of
30s** -- about half the budget, comfortably inside it, but roughly 3x Phase 8's heaviest
row (5.08s, `<=12` edges) and Phase 9's (4.85s, `<=2` edges), and about 2x the 7.39s
worst single build already on record (10-concurrent, Phase 2) -- the 400-edge chamfer is
the most expensive single operation this project has measured, even though it stays well
inside `SPUR_BUILD_TIMEOUT`.

### Kernel boundary

| Set | pred | last_ok | first_fail | last_ok - pred | Why |
|---|---|---|---|---|---|
| profile_shift=1.0 pressure_angle=14.5 | 2.9375000 | 2.9374981 | 2.9375010 | -1.91e-06 | invalid |
| profile_shift=1.0 pressure_angle=14.5 teeth=40 | 2.9375000 | 2.9374981 | 2.9375010 | -1.91e-06 | invalid |
| profile_shift=0.8 pressure_angle=20 | 2.9375000 | 2.9374981 | 2.9375010 | -1.91e-06 | invalid |
| profile_shift=1.0 pressure_angle=14.5 root_fillet=1.0 | 2.3835000 | 2.3834982 | 2.3835011 | -1.81e-06 | invalid |
| root_fillet=1.0 | 2.4895000 | 2.4894991 | 2.4895020 | -9.08e-07 | invalid |
| profile_shift=1.0 pressure_angle=14.5 module=1 bore_d=5 bore_flat=0 | 1.3240000 | 1.3639641 | 1.3639669 | 4.00e-02 | invalid |

200-tooth pair (`teeth=200 profile_shift=1.0 pressure_angle=14.5`): pred - 0.001 ->
builds, pred + 0.05 -> invalid.

The kernel stops within about 2 microns of `pred = ra - spline_start` on five of the six
sets (last_ok reads 0.9-1.9e-6 mm *inside* pred, first_fail 0.9-1.0e-6 mm *past* it,
20-step bisection resolution) -- teeth-independent where compared (19 and 40 teeth agree
to the same gap), the way `ROOT_CONTACT` is and the hex corner (L27) is not. The sixth
set (module 1, x 1.0) builds 0.0400 mm *past* `pred`, confirming the one flagged
exception (the rule is conservative, never optimistic, where it differs): `pred` under-
predicts by 0.04 mm there, which only means the rule trims a hair more than the kernel
strictly needs, never that it lets an unbuildable chamfer through. The 200-tooth pair
confirms `pred` at the size that actually matters for the budget: it builds 0.001 mm
inside `pred` and fails 0.05 mm past it. D-01 (`0.45 x face_width` = 3.375 mm at the
default 7.5 mm face) and D-02 (`ra - r` = 3.5 mm at `profile_shift=1.0`) would both pass
`c = 3.0` here -- inside both analytic caps -- yet the kernel turns that into an invalid
solid (confirmed again at `pred + 0.05` = 2.9875 mm, also inside both caps). So the
analytic caps alone are not sufficient: 10-02's cap needs a third term, `pred` less a
margin (D-04 -- "the cap becomes the measured boundary").

### Flank rule over the grid

405 sets validated, 163 conservative (pred < the analytic cap), 0 failed, 17 also built
at the analytic cap.

Every one of the 163 sets where `pred` sits inside the analytic cap built cleanly both at
`pred` and 0.05 mm inside it (0 failures) -- confirming `pred`'s bisected boundary holds
across the grid, not just the six hand-picked boundary sets. 17 of those 163 sets *also*
built when chamfered all the way out to the (larger) analytic cap: the `pred`-based rule
trims some chamfers the kernel would in fact have accepted on those 17 -- a capped
dimension, reported in `warnings`, never a refused one (L03); the rule is conservative by
construction, not a source of a new 422.

### Verdict

**Verdict:** held -- 18 cost rows ok, 6 boundary sets held, grid 163/405 conservative
with 0 failures, heaviest 200-tooth request teeth=200 module=0.2 backlash=0.07 c=0.05 --
15.90 s of 30 s.

## Tooth-tip chamfer build and export time (Phase 10)

The committed measurement record for the tooth-tip chamfer at its heaviest allowed
configuration (ROADMAP Phase 10 SC4; `REQ-measured-build-time`'s per-feature entry,
re-measured combined in Phase 12). The runner is `make bench.build` over the committed
sweep `bench/sweeps/tip_chamfer.json`, reused unchanged from Phase 8 (08 D-12). The
sweep has 9 rows, per D-06: `module` {1.75, 10} (module drives fine-STL export time,
Phase 8's probe) x `tip_chamfer` {0.4, the largest each module allows -- 1.75 mm at the
pitch circle for module 1.75, 3 mm at the field's own `le` for module 10} x
`recess_sides` {both, none} (a recess is the heaviest factor Phase 8 and 9 both found),
on the default bore -- 8 rows -- plus one row at module 0.2, backlash 0.07 (the finest
tips this model allows, at the backlash that keeps the tooth tip above `check()`'s
0.05 mm floor), with its recess. 10-01's spike found the chamfer's cost does not depend
on `c` (edge count dominates, not chamfer depth or module), so the 0.4 mm rows here are
a check on that finding, not expected to be the heaviest.

### Host state

- Machine: 12 CPUs, arm64, 32.0 GiB RAM
- Python: 3.12.13
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `e63ae4c`
- Sweep: `bench/sweeps/tip_chamfer.json`
- Load averages at start (script's own `os.getloadavg()`): 3.29, 4.08, 4.36
- `uptime` moments before the run: load averages 3.88, 4.42, 4.51
- SPUR_BUILD_TIMEOUT: 30 s, a cold request is one build plus one export
- Both readings sit above this project's usual "quiet" bar (>1.5 on this 12-core host,
  Phase 7's own convention) -- the numbers below carry that caveat rather than being
  presented as clean (L08).

### Sweep

| Parameter set | Build (s) | Fine STL (s) | STEP (s) | Build + slower export (s) | Inside 30 s |
|---|---|---|---|---|---|
| teeth=200 module=1.75 tip_chamfer=0.4 recess_sides=both | 13.95 | 0.81 | 0.50 | 14.77 | yes |
| teeth=200 module=1.75 tip_chamfer=0.4 recess_sides=none | 13.21 | 0.76 | 0.48 | 13.97 | yes |
| teeth=200 module=1.75 tip_chamfer=1.75 recess_sides=both | 14.17 | 0.70 | 0.48 | 14.87 | yes |
| teeth=200 module=1.75 tip_chamfer=1.75 recess_sides=none | 13.38 | 0.62 | 0.50 | 14.01 | yes |
| teeth=200 module=10 tip_chamfer=0.4 recess_sides=both | 13.40 | 1.22 | 0.48 | 14.63 | yes |
| teeth=200 module=10 tip_chamfer=0.4 recess_sides=none | 12.63 | 0.77 | 0.48 | 13.40 | yes |
| teeth=200 module=10 tip_chamfer=3 recess_sides=both | 13.51 | 1.20 | 0.49 | 14.71 | yes |
| teeth=200 module=10 tip_chamfer=3 recess_sides=none | 12.75 | 0.76 | 0.48 | 13.51 | yes |
| teeth=200 module=0.2 backlash=0.07 tip_chamfer=0.2 recess_sides=both | 14.32 | 0.52 | 0.46 | 14.84 | yes |

**Heaviest:** teeth=200 module=1.75 tip_chamfer=1.75 recess_sides=both -- 14.87 s of 30 s.

The heaviest row (14.87 s) sits at about half the 30 s timeout -- roughly 3x Phase 8's
heaviest hex row (5.08 s) and Phase 9's heaviest keyway row (4.85 s), and about 2x the
7.39 s worst single build already on record ("### `SPUR_BUILD_TIMEOUT`" above, 200 teeth
under ten concurrent requests). The chamfer operator is the dominant cost, exactly as
10-01's spike found: at ~13-14 s of bare build against the spike's own 12.50-12.81 s
chamfer-only measurement on the same 400-edge case, the chamfer step accounts for the
large majority of every row's build time here too.

### SPUR_BUILD_TIMEOUT margin

`SPUR_BUILD_TIMEOUT`'s 30 s default was set at about 4x the 7.39 s worst build on record
("### `SPUR_BUILD_TIMEOUT`" above). The heaviest tip-chamfer row (14.87 s) leaves only
30 / 14.87 ~= **2.0x** of that margin -- half of what the default was sized against. This
sweep builds one gear at a time, so behaviour under ten concurrent builds is not measured
here, and nothing is extrapolated from it.

### make verify wall time

`time make verify`: **453 passed in 97.18s** -- **98.17s** wall time (`time`, includes
lint/typecheck/import-lint/no-fake-done), against Phase 9's recorded **78.21s** / 396
tests. The phase's tip-chamfer tests (57 new, across 10-01 through 10-04) add **+19.96s**
to the gate, measured rather than assumed.

## Honeycomb cell-count spike (Phase 11, D-24)

The committed measurement record for the ROADMAP Phase 11 SC3 research flag: a
build-time-vs-cell-count sweep before any cap formula is written, L17's methodology.
D-11 sets the honeycomb's share at 7.5 s -- a quarter of `SPUR_BUILD_TIMEOUT` -- beside
the 14.87 s tip-chamfer row Phase 12 will stack it on. The probe raises `hex_cell` in
0.05 mm steps until the exact whole-cell count on the axis-centred lattice fits each
target, then cuts the whole cells as hexagonal prisms through `spur.model._build_checked`
plus one `solid.cut(*prisms)` call, with no `hex_cell`/`hex_wall` field in `GearParams`
yet -- the field, the cap and the cutter are 11-05 through 11-09, planned on these
numbers. Command: `.venv/bin/python -m bench.honeycomb_spike`.

### Host state

- Machine: 12 CPUs, arm64, 32.0 GiB RAM
- Python: 3.12.13
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `35f0137`
- Load averages at start (script's own `os.getloadavg()`): 8.28, 6.26, 5.41
- `uptime` moments before the run: load averages 9.35, 6.39, 5.44
- SPUR_BUILD_TIMEOUT: 30 s
- BUDGET_S: 7.5 s (a quarter of `SPUR_BUILD_TIMEOUT`, D-11)
- Both readings sit well above this project's usual "quiet" bar (>1.5 on this 12-core
  host, Phase 7's own convention) -- the numbers below carry that caveat rather than
  being presented as clean (L08). A cap measured under this load is conservative, never
  optimistic: a quiet host would read every row faster, if anything raising the cap the
  sweep would find, never lowering it.

### Cost by cell count

| Set | Cell (mm) | Cells | Bare (s) | Cut (s) | STL (s) | STEP (s) | Request (s) | dFaces | Why | Run 1 / Run 2 request (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| teeth=200 module=10 target=0 | 3 | 0 | 2.20 | 0.00 | 0.00 | 0.00 | 2.20 | 0 | ok | 2.20 / 2.15 |
| teeth=200 module=10 target=25 | 305.3 | 18 | 2.26 | 1.45 | 0.66 | 0.52 | 4.37 | 218 | ok | 4.30 / 4.37 |
| teeth=200 module=10 target=50 | 235 | 42 | 2.25 | 3.13 | 0.78 | 0.69 | 6.16 | 482 | ok | 6.16 / 6.16 |
| teeth=200 module=10 target=75 | 190.3 | 72 | 2.26 | 3.86 | 0.83 | 0.81 | 6.95 | 602 | ok | 6.95 / 6.75 |
| teeth=200 module=10 target=100 | 167.2 | 96 | 2.21 | 3.99 | 0.88 | 0.86 | 7.09 | 806 | ok | 7.09 / 7.03 |
| teeth=200 module=10 target=125 | 149.1 | 120 | 2.34 | 3.88 | 0.91 | 0.92 | 7.15 | 950 | ok | 7.15 / 6.96 |
| teeth=200 module=10 target=150 | 137.35 | 150 | 2.22 | 4.67 | 0.93 | 1.06 | 7.95 | 1130 | ok | 7.56 / 7.95 |
| teeth=200 module=10 target=175 | 129.3 | 168 | 2.23 | 5.93 | 1.08 | 1.23 | 9.38 | 1286 | ok | 9.29 / 9.38 |
| teeth=200 module=10 target=200 | 120.5 | 198 | 2.65 | 8.84 | 1.07 | 1.41 | 12.90 | 1598 | ok | 12.90 / 12.80 |
| teeth=200 module=10 target=250 | 111.65 | 240 | 2.21 | 7.68 | 1.14 | 1.61 | 11.50 | 1730 | ok | 11.31 / 11.50 |
| teeth=200 module=10 target=300 | 100.35 | 300 | 2.31 | 10.10 | 1.15 | 1.93 | 14.34 | 2270 | ok | 14.34 / 14.13 |

The `target=0` row is the first measurement of this gear (200 teeth, module 10, both
recesses) on the pinned kernel: a bare build of **2.20-2.65 s**, steady across every row
regardless of cell count -- the cut and its exports are the variable cost, not the build.
Cut time grows with cell count but not linearly or monotonically: 18 cells cost 1.45 s to
cut (0.081 s/cell), 300 cells cost 10.10 s (0.034 s/cell) -- a large fixed part from
walking the ~1620-face body dominates at low counts (L09's cost family), and the
198-cell row (8.84 s) reads slower than the 240-cell row (7.68 s) immediately after it,
which the 8-9 load average at the time of the run is the more likely explanation for than
any real reversal in cost. Fine-STL and STEP both grow with the cut's own face count
(`dFaces`, 218 at 18 cells to 2270 at 300): STL 0.66-1.15 s, STEP 0.52-1.93 s, together a
minority of most rows' request time next to the cut itself. The heaviest rows here (200,
250 and 300 cells, all above the cap this spike measures below) read 11.50-14.34 s,
roughly the same order as Phase 10's heaviest tip-chamfer row (14.87 s) -- confirming
D-11's premise that an uncapped honeycomb on this gear is not a cheap cut.

### Cut spelling

| Set | Cell (mm) | Cells | Bare (s) | Cut (s) | STL (s) | STEP (s) | Request (s) | dFaces | Why | Spelling |
|---|---|---|---|---|---|---|---|---|---|---|
| teeth=200 module=10 target=125 | 149.1 | 120 | 2.16 | 3.75 | 0.88 | 0.89 | 6.81 | 950 | ok | star |
| teeth=200 module=10 target=125 | 149.1 | 120 | 2.16 | 3.74 | 0.90 | 0.94 | 6.84 | 950 | ok | compound |
| teeth=200 module=10 target=125 | 149.1 | 120 | 2.17 | 3.75 | 0.87 | 0.91 | 6.83 | 950 | ok | fuse |
**Spelling:** star

The three spellings read within 0.03 s of each other on 120 cells -- inside this run's
own noise, not a real margin -- so `cut(*prisms)` stays the default per D-24's >10% rule:
none of the alternatives cleared it.

### Cap

**Cap:** HEX_CELL_CAP = 120 -- teeth=200 module=10 target=125 reads 7.15 s of 7.5 s; the next row (150 cells) reads 7.95 s.

The constant is the cell count the row actually cut (120), not its target (125): no
honeycomb link cuts more cells than were measured inside 7.5 s at D-11's configuration.

### Confirmation at module 1.75

| Set | Cell (mm) | Cells | Bare (s) | Cut (s) | STL (s) | STEP (s) | Request (s) | dFaces | Why |
|---|---|---|---|---|---|---|---|---|---|
| teeth=200 module=1.75 target=125 | 25.25 | 120 | 2.16 | 4.21 | 0.80 | 0.89 | 7.25 | 930 | ok |

The module-1.75 gear at the cap's 120 cells reads 7.25 s against the cap row's 7.15 s at
module 10 -- confirming the planning probe's flagged finding (Flagged Assumption A2) that
the smaller-module gear is the heavier one, though by a much narrower margin here (0.10 s)
than the planning probe read at 150 cells (8.4 s vs 7.6 s, under load). Both readings sit
inside the 7.5 s budget, so D-11's module-10 configuration still sets the cap, but the
confirmation row leaves only 0.25 s of headroom -- tighter than the cap row's own 0.35 s.

### Enumeration cost

`cells_within(120, 3.0, 0.4, inner, outer)` at teeth=200 module=10: 7.371 ms (best of 5).

### Verdict

**Verdict:** held -- HEX_CELL_CAP = 120 cells (7.15 s of 7.5 s), spelling star, confirmation 7.25 s of 7.5 s.

## Body cutout build and export time (Phase 11)

The committed measurement record for every body cutout pattern at its heaviest allowed
configuration (ROADMAP SC5; `REQ-measured-build-time`'s per-feature entry, re-measured
combined in Phase 12). The runner is `make bench.build` over three committed sweeps,
`bench/sweeps/hole_cutout.json`, `bench/sweeps/spoke_cutout.json` and
`bench/sweeps/honeycomb.json`, unchanged from `bench/build_time.py` (08 D-12). Each sweep
is 200 teeth (D-18's `le` on `hole_count`/`spoke_count`, one instance per tooth) x module
{1.75, 10} (module drives fine-STL export time, Phase 8's probe) x a small and a large
size for holes and spokes (09-04's lesson: the heaviest row is not the largest feature,
so both are measured) x `recess_sides` {both, none} (a recess is the heaviest factor
every prior phase's sweep has found) -- 8 rows each, 24 rows total. The honeycomb sweep
holds `hex_cell` at its field default (3 mm, the smallest legal request) and varies
`hex_wall` {0.4, 5} instead, so every one of its four gears (module x recess) is raised
past 3 mm to `HEX_CELL_CAP` (11-05's raise-to-fit) rather than measuring a cell size that
was never going to be requested. The planning probe (11-06-PLAN.md's `<interfaces>`)
predicted the module-1.75 small-hole-with-recess row at 41.06 s and the recess-bearing
spoke rows at 68-70 s; both predictions are confirmed measured, not estimated, below.

### Host state

- Machine: 12 CPUs, arm64, 32.0 GiB RAM
- Python: 3.12.13
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `e908b29`
- Sweeps: `bench/sweeps/hole_cutout.json`, `bench/sweeps/spoke_cutout.json`,
  `bench/sweeps/honeycomb.json`
- `uptime` moments before each run: hole 4.51, 5.17, 5.97; spoke 6.48, 6.19, 6.31;
  honeycomb 9.71, 10.35, 8.39
- Load averages at start (each script's own `os.getloadavg()`): hole 6.79, 6.24, 6.33;
  spoke 10.38, 10.49, 8.43; honeycomb 8.31, 9.65, 8.25
- SPUR_BUILD_TIMEOUT: 30 s, a cold request is one build plus one export
- Every reading across all three runs sits well above this project's usual "quiet" bar
  (>1.5 on this 12-core host, Phase 7's own convention) -- the numbers below carry that
  caveat rather than being presented as clean (L08). A row measured this loaded is
  conservative, never optimistic: a quieter host would read every row faster, if
  anything shrinking the gate's list, never growing it.

### Holes

| Parameter set | Build (s) | Fine STL (s) | STEP (s) | Build + slower export (s) | Inside 30 s |
|---|---|---|---|---|---|
| teeth=200 module=1.75 hole_count=200 hole_d=1 hole_circle_d=183.4 recess_sides=both | 22.48 | 19.38 | 0.93 | 41.85 | **NO** |
| teeth=200 module=1.75 hole_count=200 hole_d=1 hole_circle_d=183.4 recess_sides=none | 3.51 | 3.72 | 0.61 | 7.23 | yes |
| teeth=200 module=1.75 hole_count=200 hole_d=4.9 hole_circle_d=339.9 recess_sides=both | 4.46 | 2.19 | 0.61 | 6.65 | yes |
| teeth=200 module=1.75 hole_count=200 hole_d=4.9 hole_circle_d=339.9 recess_sides=none | 3.71 | 1.94 | 0.61 | 5.65 | yes |
| teeth=200 module=10 hole_count=200 hole_d=1 hole_circle_d=400 recess_sides=both | 4.16 | 1.79 | 0.47 | 5.95 | yes |
| teeth=200 module=10 hole_count=200 hole_d=1 hole_circle_d=400 recess_sides=none | 3.51 | 4.65 | 0.62 | 8.16 | yes |
| teeth=200 module=10 hole_count=200 hole_d=5.85 hole_circle_d=400 recess_sides=both | 4.50 | 1.76 | 0.45 | 6.26 | yes |
| teeth=200 module=10 hole_count=200 hole_d=5.85 hole_circle_d=400 recess_sides=none | 3.73 | 4.14 | 0.62 | 7.87 | yes |

**Heaviest:** teeth=200 module=1.75 hole_count=200 hole_d=1 hole_circle_d=183.4 recess_sides=both -- 41.85 s of 30 s.

The heaviest row is the *small* hole (1 mm) on module 1.75, with a recess -- not the
large hole. At `hole_circle_d` 183.4 the hole centres sit exactly where the plan's
`<interfaces>` block placed them: straddling the recess groove's outer wall (the
`recess_inner_d`/`recess_width`-derived band at 85.69-91.69 mm radius on this gear).
Every one of the 200 holes crossing that boundary splits the recess floor fillet into
many small faces (Pitfall 8) rather than leaving it whole, and fine-STL tessellation
pays for it directly: 19.38 s of the row's 41.85 s, more than STL's cost on every other
row in this table combined. The cut itself is also the row's own heaviest (22.48 s vs.
3.51-4.50 s elsewhere). The large-hole rows (4.9/5.85 mm) sit on a bolt circle far
outside the recess band at both moduli, so their fillet never splits and every one reads
5.65-7.87 s regardless of recess -- confirming the plan's own framing that the heaviest
row is a geometry interaction, not the largest feature. This single row (41.85 s) is
the only hole row over budget; it is close to the planning probe's 41.06 s prediction
(+0.79 s, inside this run's load noise).

### Spokes

| Parameter set | Build (s) | Fine STL (s) | STEP (s) | Build + slower export (s) | Inside 30 s |
|---|---|---|---|---|---|
| teeth=200 module=1.75 spoke_count=200 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=both | 63.09 | 2.60 | 2.55 | 65.70 | **NO** |
| teeth=200 module=1.75 spoke_count=200 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=none | 12.86 | 3.40 | 1.90 | 16.26 | yes |
| teeth=200 module=1.75 spoke_count=200 spoke_width=4.3 hub_d=300 rim_wall=10 spoke_fillet=5 recess_sides=both | 11.12 | 3.86 | 2.01 | 14.98 | yes |
| teeth=200 module=1.75 spoke_count=200 spoke_width=4.3 hub_d=300 rim_wall=10 spoke_fillet=5 recess_sides=none | 10.45 | 3.71 | 1.91 | 14.16 | yes |
| teeth=200 module=10 spoke_count=200 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=both | 65.65 | 3.05 | 2.58 | 68.70 | **NO** |
| teeth=200 module=10 spoke_count=200 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=none | 14.16 | 6.09 | 1.90 | 20.25 | yes |
| teeth=200 module=10 spoke_count=200 spoke_width=5.85 hub_d=400 rim_wall=100 spoke_fillet=5 recess_sides=both | 63.45 | 3.22 | 2.63 | 66.67 | **NO** |
| teeth=200 module=10 spoke_count=200 spoke_width=5.85 hub_d=400 rim_wall=100 spoke_fillet=5 recess_sides=none | 10.89 | 4.14 | 1.91 | 15.04 | yes |

**Heaviest:** teeth=200 module=10 spoke_count=200 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=both -- 68.70 s of 30 s.

Three of the four `recess_sides=both` rows are over budget (63-69 s); the fourth --
module 1.75, `spoke_width` 4.3, `hub_d` 300, `rim_wall` 10 -- reads 14.98 s, a sixth of
the others despite also carrying a recess. The difference is geometric, not a cost of
"recess" in general: at module 1.75 the recess band sits at 85.69-91.69 mm radius, and
this row's sectors span 150-162.81 mm (`hub_d/2` to `rf`) -- entirely above the recess
band, so the cut never crosses it. Every over-budget row's sectors do cross the recess
band on their own gear (module 1.75's small-hub row spans 26-172.61 mm; both module-10
rows span well past 493.04-499.04 mm at either 26-987.3 mm or 200-887.5 mm) -- each
sector crossing the groove's walls and its floor fillet the same way the heaviest hole
row's cutters did. The measured cost is close to the planning probe's own estimate
(~0.3 s per sector crossing the groove, 200 sectors ~= 60 s): the three over-budget rows
read 63.09-65.65 s of *build* alone, plus 2.55-2.63 s more for export -- the heaviest
individual operation this project has measured for any single sweep row to date, well
past Phase 10's 14.87 s tip-chamfer row. Every `recess_sides=none` row, regardless of
sector shape or module, reads 14.16-20.25 s -- inside budget, confirming the recess
crossing (not the sector width) is what drives the cost here.

### Honeycomb at the cap

| Parameter set | Build (s) | Fine STL (s) | STEP (s) | Build + slower export (s) | Inside 30 s |
|---|---|---|---|---|---|
| teeth=200 module=1.75 hex_cell=3 hex_wall=0.4 recess_sides=both | 7.76 | 0.78 | 0.89 | 8.65 | yes |
| teeth=200 module=1.75 hex_cell=3 hex_wall=0.4 recess_sides=none | 4.54 | 0.86 | 0.98 | 5.52 | yes |
| teeth=200 module=1.75 hex_cell=3 hex_wall=5 recess_sides=both | 6.56 | 0.79 | 0.85 | 7.42 | yes |
| teeth=200 module=1.75 hex_cell=3 hex_wall=5 recess_sides=none | 4.56 | 0.87 | 0.97 | 5.54 | yes |
| teeth=200 module=10 hex_cell=3 hex_wall=0.4 recess_sides=both | 6.45 | 0.89 | 0.89 | 7.34 | yes |
| teeth=200 module=10 hex_cell=3 hex_wall=0.4 recess_sides=none | 4.61 | 0.97 | 0.98 | 5.59 | yes |
| teeth=200 module=10 hex_cell=3 hex_wall=5 recess_sides=both | 6.46 | 0.91 | 0.88 | 7.37 | yes |
| teeth=200 module=10 hex_cell=3 hex_wall=5 recess_sides=none | 4.55 | 0.99 | 0.98 | 5.54 | yes |

**Heaviest:** teeth=200 module=1.75 hex_cell=3 hex_wall=0.4 recess_sides=both -- 8.65 s of 30 s.

Every row is comfortably inside the 30 s absolute timeout (worst margin 3.47x, the
heaviest row against 30 s). But D-11 set the honeycomb's own share at 7.5 s -- a quarter
of `SPUR_BUILD_TIMEOUT`, beside the 14.87 s tip-chamfer row Phase 12 stacks it on -- and
the heaviest row here (8.65 s, module 1.75, `hex_wall` 0.4, both recesses) reads 1.153x
that share, 1.15 s over it. This is Flagged Assumption A2 firing: 11-02's spike measured
the cap row at 7.15-7.25 s with a different `hex_wall`, and this sweep's thinner-wall,
both-recess combination (raised to `HEX_CELL_CAP` at a larger 25.85 mm cell, per
`calc.hex_cells`) is measurably heavier than either of 11-02's readings. The other seven
rows all stay inside 7.5 s (5.52-7.42 s); only this one combination -- the thinnest legal
wall with both recesses on, the module the smaller-module confirmation already flagged
as heavier -- crosses it.

### SPUR_BUILD_TIMEOUT margin

`SPUR_BUILD_TIMEOUT`'s 30 s default was set at about 4x the 7.39 s worst build on record
(the "### `SPUR_BUILD_TIMEOUT`" section above). Four rows across two patterns are over
that 30 s timeout on their own, before this section's gate is decided: one hole row
(41.85 s, 1.4x the timeout) and three spoke rows (65.70-68.70 s, 2.19-2.29x the timeout)
-- for these, there is no margin to report; D-18's `le` of 200 does not fit at these
sizes on this measured kernel. Among the rows that already build inside 30 s, the
heaviest is a spoke row (20.25 s, module 10, `spoke_width` 0.4, no recess), leaving
1.48x margin; the heaviest in-budget hole row is 8.16 s, leaving 3.68x. Naively placed
beside Phase 10's 14.87 s tip-chamfer row (Phase 12's own combined re-measurement, not
predicted here), the in-budget totals already read 35.12 s for the heaviest spoke row
(over 30 s on its own) and 23.03 s for the heaviest hole row (6.97 s of headroom) --
arithmetic only, not a real combined build; Phase 12 re-measures the actual composition.
This sweep builds one gear at a time, so behaviour under concurrent builds is not
measured here either.

### Gate

Four rows read over `SPUR_BUILD_TIMEOUT` (30 s):

- `teeth=200 module=1.75 hole_count=200 hole_d=1 hole_circle_d=183.4 recess_sides=both` --
  41.85 s (build 22.48 s, fine STL 19.38 s -- the split recess fillet, Pitfall 8)
- `teeth=200 module=1.75 spoke_count=200 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=both` --
  65.70 s (build 63.09 s -- cut-heavy, 200 sectors crossing the recess groove)
- `teeth=200 module=10 spoke_count=200 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=both` --
  68.70 s (build 65.65 s -- cut-heavy, same crossing)
- `teeth=200 module=10 spoke_count=200 spoke_width=5.85 hub_d=400 rim_wall=100 spoke_fillet=5 recess_sides=both` --
  66.67 s (build 63.45 s -- cut-heavy, same crossing)

One row reads over the honeycomb's own D-11 share (7.5 s, a quarter of
`SPUR_BUILD_TIMEOUT`), while staying inside the 30 s absolute timeout:

- `teeth=200 module=1.75 hex_cell=3 hex_wall=0.4 recess_sides=both` -- 8.65 s of 7.5 s
  (7.76 s build, 0.89 s STEP export)

Per this plan's must-have and prohibition, none of these five rows is dropped, re-picked
or re-run to green -- they are recorded above exactly as measured, and Task 2's
checkpoint decision is pending as of this writing.
