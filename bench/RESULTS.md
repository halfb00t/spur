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
