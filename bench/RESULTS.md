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
