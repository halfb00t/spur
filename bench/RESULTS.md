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

### Phase 13 investigation sessions

`.planning/phases/13-latency-bar/13-LATENCY-INVESTIGATION.md` ran six pair sessions
(twelve runs) to explain the two observations above. Every run carried a split-process
poller beside the harness's own in-process sampling and, for Pairs B and C, a mirrored
teeth range or a server restart the unmodified harness never does — so none of these
twelve runs is "the harness as it stands" and none counts for the bar (D-07); they are
recorded here as the investigation's own record.

`fleet-user` (unrelated, restart-looping every ~40 s beside Runs 1–8) was stopped for this
session; `spur-spur-1` left running.

| Session | Released (UTC) | 1-min load at release | Decisive | Run 1 ratio | Run 2 ratio | Run 2 vs run 1 |
|---|---|---|---|---|---|---|
| A1 | 2026-10-02T02:37:53.913Z | 1.49, 1.34, 1.15 | yes | 1.327x | 1.940x | worse |
| B1 | 2026-10-02T02:41:40.765Z | 1.31, 1.14, 1.02 | yes | 1.476x | 2.309x | worse |
| C1 | 2026-10-02T02:48:51.582Z | 1.38, 1.34, 1.41 | yes | 1.792x | 1.396x | not worse |
| A2 | 2026-10-02T02:53:10.129Z | 1.46, 1.35, 1.29 | yes | 1.896x | 1.517x | not worse |
| B2 | 2026-10-02T03:06:22.211Z | 1.19, 1.18, 1.34 | yes | 1.426x | 1.528x | worse |
| C2 | 2026-10-02T03:11:05.906Z | 1.40, 1.39, 1.23 | yes | 1.369x | 1.534x | worse |

Observation 1 verdict (13-LATENCY-INVESTIGATION.md ## Verdict): not reproduced in this
environment — Pair A does not point worse (it is split: A1 worse, A2 not worse), and the
pre-registered rule states that when Pair A does not point worse, observation 1 is not
reproduced and Pairs B and C cannot rule anything in or out.

Observation 2 verdict (13-LATENCY-INVESTIGATION.md ## Verdict): candidate (ii) — the
floor is real — is ruled in. At least one concurrent run's in-process verdict flips
inside one percentile — three do, plus one on the split poller — which directly refutes
(i); (iii)'s exact claim does not hold (three below-median-n runs do not flip). (ii) is
therefore the surviving candidate.

### Bar session bar-1 (Runs 9-10)

Commit under test: `34d9ef4`. Command: `.venv/bin/python -m bench.latency --base-url
http://127.0.0.1:8001` (not the bare `make bench.latency` target, which targets port
8000 — RESEARCH.md Pitfall 1), two runs in immediate succession against one fresh
server (Run 10 inherits Run 9's `_EXPORTS`, as every even-numbered run did), shipping
defaults (`server_env`: `{"SPUR_PORT": "8001"}`).

`fleet-user` (unrelated, restart-looping every ~40 s beside Runs 1–8) was stopped for this
session; `spur-spur-1` left running.

**Environment snapshot** (`bar-1.status.json`, every D-05 quiet-gate sample, 30 s apart,
2026-10-02T03:41:00Z through 2026-10-02T03:56:00Z UTC):

1.61, 1.31, 1.63, 1.67, 2.40, 1.77, 1.75, 1.65, 1.39, 1.57, 1.87, 1.54, 2.59, 2.23, 2.03,
1.76, 1.77, 1.81, 1.81, 1.48, 1.89, 1.65, 1.89, 1.60, **8.02**, 5.46, 3.55, 2.66, 2.08,
1.96, 1.88 (30 samples, never three consecutive under 1.5 — a spike to 8.02 at
2026-10-02T03:53:00Z broke the streak closest to release, at sample 24/25/26).

- `docker info`: exit 0.
- Top CPU (`ps -Ao %cpu,comm -r`, latest sample): loginwindow 12.4%, Notion Calendar
  Helper (Renderer) 6.2%, iTerm2 5.9%, WindowServer 4.9%, Code Helper (Plugin) 3.0%.
- `docker ps --format '{{.Names}} {{.Status}}'`: `spur-spur-1 Up 36 hours (healthy)`,
  `fleet-user Exited (2) 14 hours ago`.
- Load after: 3.67.

Decisive (D-05): no — the 900 s cap expired; recorded, not counted for the bar.

#### `single` scenario (Runs 9-10)

| Run | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|
| 9 | 0.6 ms (n=3605) | 0.7 ms (n=5062) | 1.18x | 3.12 s | 0 of 1 |
| 10 | insufficient (n<20) | insufficient (n=18) | -- | -- | -- |

Run 10 printed `warning: single/under-load has only 18 /api/health samples (need >= 20);
refusing to report a p95` — the 200-tooth gear was cached from Run 9, so there was no load
window to sample; no ratio, per L08, exactly as in Runs 6 and 8.

Pass bar: under-load p95 <= 2.00x idle p95. **Met** on Run 9 (1.18x). Run 10: no ratio
printed (insufficient samples).

#### `concurrent` scenario (Runs 9-10)

| Run | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|
| 9 | 0.6 ms (n=3636) | 0.9 ms (n=15236) | 1.42x | 11.09 s | 6 of 10 |
| 10 | 0.7 ms (n=3528) | 0.9 ms (n=12426) | 1.37x | 9.37 s | 2 of 10 |

Pass bar: under-load p95 <= 2.00x idle p95. **Met** on Run 9 (1.42x) and Run 10 (1.37x).
Neither run was repeated or restarted in search of a passing number. This session is
**non-decisive** (D-05): the quiet gate never released, so neither reading counts for
outcome (a) or (b) — the decisive session (D-07) is a separate attempt.

### Bar session bar-2 (Runs 11-12)

Commit under test: `83bb448`. Command: `.venv/bin/python -m bench.latency --base-url
http://127.0.0.1:8001` (not the bare `make bench.latency` target, which targets port
8000 — RESEARCH.md Pitfall 1), two runs in immediate succession against one fresh
server (Run 12 inherits Run 11's `_EXPORTS`, as every even-numbered run did), shipping
defaults (`server_env`: `{"SPUR_PORT": "8001"}`).

`fleet-user` (unrelated, restart-looping every ~40 s beside Runs 1–8) was stopped for this
session; `spur-spur-1` left running.

**Environment snapshot** (`bar-2.status.json`, every D-05 quiet-gate sample, 30 s apart,
2026-10-02T06:33:35Z through 2026-10-02T06:48:36Z UTC):

5.51, 4.29, 3.69, 3.54, 2.59, 2.64, 2.51, 2.13, 2.30, 1.63, 1.84, 1.62, **1.31**, 1.97,
1.47, 1.99, 2.37, 2.10, 1.97, 1.65, 2.13, 2.00, 2.13, 2.05, 2.08, 2.01, 1.55, 2.03, 2.15,
1.88, 1.63 (31 samples; the load never fell far enough to approach the three-consecutive-
under-1.5 streak the gate needs — sample 13 at 1.31 is the single lowest point, with no
adjacent sample under 1.5 to build a streak around it).

- `docker info`: exit 0.
- Top CPU (`ps -Ao %cpu,comm -r`, latest sample): WindowServer 26.5%, Telegram 12.0%,
  iTerm2 9.5%, claude 6.0%, go 5.9%.
- `docker ps --format '{{.Names}} {{.Status}}'`: `spur-spur-1 Up 39 hours (healthy)`,
  `fleet-user Exited (2) 17 hours ago`.
- Load after: 2.11.

Decisive (D-05): no — the 900 s cap expired; recorded, not counted for the bar.

#### `single` scenario (Runs 11-12)

| Run | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|
| 11 | 0.6 ms (n=3682) | 0.7 ms (n=5098) | 1.11x | 3.08 s | 0 of 1 |
| 12 | insufficient (n<20) | insufficient (n=18) | -- | -- | -- |

Run 12 printed `warning: single/under-load has only 18 /api/health samples (need >= 20);
refusing to report a p95` — the 200-tooth gear was cached from Run 11, so there was no
load window to sample; no ratio, per L08, exactly as in Runs 6, 8 and 10.

Pass bar: under-load p95 <= 2.00x idle p95. **Met** on Run 11 (1.11x). Run 12: no ratio
printed (insufficient samples).

#### `concurrent` scenario (Runs 11-12)

| Run | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|
| 11 | 0.6 ms (n=3640) | 0.8 ms (n=15653) | 1.38x | 11.24 s | 6 of 10 |
| 12 | 0.6 ms (n=3578) | 0.9 ms (n=12634) | 1.42x | 9.44 s | 2 of 10 |

Pass bar: under-load p95 <= 2.00x idle p95. **Met** on Run 11 (1.38x) and Run 12 (1.42x).
Neither run was repeated or restarted in search of a passing number. This session is
**non-decisive** (D-05): the quiet gate never released, so neither reading counts for
outcome (a) or (b) — the decisive session (D-07) is a separate attempt.

### Bar session bar-3 (Runs 13-14)

Commit under test: `fe17199`. Command: `.venv/bin/python -m bench.latency --base-url
http://127.0.0.1:8001` (not the bare `make bench.latency` target, which targets port
8000 — RESEARCH.md Pitfall 1), two runs in immediate succession against one fresh
server (Run 14 inherits Run 13's `_EXPORTS`, as every even-numbered run did), shipping
defaults (`server_env`: `{"SPUR_PORT": "8001"}`).

`fleet-user` (unrelated, restart-looping every ~40 s beside Runs 1–8) was stopped for this
session; `spur-spur-1` left running.

**Environment snapshot** (`bar-3.status.json`, every D-05 quiet-gate sample, 30 s apart,
2026-10-02T07:10:04Z through 2026-10-02T07:15:05Z UTC):

2.95, 2.58, 2.83, 2.56, 2.21, 1.87, 1.97, 1.98, **1.39, 1.12, 0.96** (11 samples; released
by the first three-consecutive-under-1.5 streak, samples 9-11 at 2026-10-02T07:14:05Z,
07:14:35Z and 07:15:05Z UTC).

- `docker info`: exit 0.
- Top CPU (`ps -Ao %cpu,comm -r`, latest sample): WindowServer 21.0%, AlDente 6.5%,
  iTerm2 5.8%, claude 4.3%, Code Helper (Plugin) 3.9%.
- `docker ps --format '{{.Names}} {{.Status}}'`: `spur-spur-1 Up 40 hours (healthy)`,
  `fleet-user Exited (2) 18 hours ago`.
- Load after: 5.34.

Decisive (D-05): yes — released by three consecutive samples under 1.5.

#### `single` scenario (Runs 13-14)

| Run | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|
| 13 | 0.6 ms (n=3614) | 0.7 ms (n=5220) | 1.12x | 3.14 s | 0 of 1 |
| 14 | insufficient (n<20) | insufficient (n=18) | -- | -- | -- |

Run 14 printed `warning: single/under-load has only 18 /api/health samples (need >= 20);
refusing to report a p95` — the 200-tooth gear was cached from Run 13, so there was no
load window to sample; no ratio, per L08, exactly as in Runs 6, 8, 10 and 12.

Pass bar: under-load p95 <= 2.00x idle p95. **Met** on Run 13 (1.12x). Run 14: no ratio
printed (insufficient samples).

#### `concurrent` scenario (Runs 13-14)

| Run | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|
| 13 | 0.6 ms (n=3586) | 0.8 ms (n=15813) | 1.31x | 11.38 s | 6 of 10 |
| 14 | 0.6 ms (n=3640) | 0.9 ms (n=12781) | 1.42x | 9.40 s | 2 of 10 |

Pass bar: under-load p95 <= 2.00x idle p95. **Met** on Run 13 (1.31x) and Run 14 (1.42x).
Neither run was repeated or restarted in search of a passing number.

**Outcome (a): demonstrated.** Both runs of the decisive session read under the bar on
the `concurrent` scenario — Run 13 printed `Ratio (under-load / idle): 1.31x` and Run 14
printed `1.42x`, both <= 1.99x (E8). The `single` scenario's Run 13 also passes (1.12x);
Run 14's single/under-load series was refused (n=18 < 20) and is not read against the
bar per E9 — the `concurrent` scenario decides it (D-08). Neither run was repeated or
restarted in search of a passing number. This closes SC2's first half: the bar is
demonstrated on both runs of one decisive session on the harness as it stands (D-07).
13-04 Task 2's D-09 checkpoint is not reached.

### Composed worst row under ten concurrent builds (Phase 13)

**The question.** `docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md`
measured the heaviest 200-tooth tip-chamfer configuration one gear at a time (14.87 s of
30 s), then Phase 12's composed sweep re-measured it alongside every other stacked feature,
still one gear at a time (29.42 s of 30 s after the `spoke_count` gate, 0.58 s of margin).
Neither run ever measured it under concurrent load; that question was re-homed into
`docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`'s "Revisit when" trigger
(12-CONTEXT.md D-04) as SC3 of this phase.

**The ten rows** (D-13, `bench/sweeps/composed.json` 1-based rows 4, 2, 3, 1, 9, 6, 10, 12,
11, 5 — each a distinct key, so admission control takes four and hash affinity spreads them
over both workers): the worst row first (29.42 s alone — `teeth=200 module=10 bore_d=9
bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52
rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both`), then the next nine heaviest
from "### Re-run after the gate (lower-le: spoke_count 32)": row 2 (28.92 s), row 3
(28.87 s), row 1 (28.61 s), row 9 (27.27 s), row 6 (24.91 s), row 10 (24.06 s), row 12
(22.26 s), row 11 (22.09 s), row 5 (16.80 s). Firing rule: the worst row's request leaves
the client alone first; the other nine fire only once `/api/health` shows the worst row
holding a build slot.

**How it was run.** `.planning/phases/13-latency-bar/investigation/session.py --mode
composed --label sc3`, one fresh server, one run (`sc3-run1`), calling
`bench.latency.run_composed` unmodified with the split-process poller riding beside it
(D-15, D-16). Re-run without the poller: `.venv/bin/python -m bench.latency --base-url
http://127.0.0.1:8001 composed`. Commit under test: `bfa54b7`. Fresh server, shipping
defaults (`server_env`: `{"SPUR_PORT": "8001"}` — `SPUR_BUILD_WORKERS`, `MAX_QUEUED_BUILDS`
and `SPUR_BUILD_TIMEOUT` all unset: 2 workers, 4 queued builds, 30 s per-build timeout).

`fleet-user` (unrelated, restart-looping every ~40 s beside Runs 1–8) was stopped for this
session; `spur-spur-1` left running.

**Environment snapshot** (`sc3.status.json`, every D-05 quiet-gate sample, 30 s apart,
2026-10-02T08:08:01Z through 2026-10-02T08:23:01Z UTC):

5.64, 4.0, 2.94, 2.33, 2.12, 1.62, 2.43, 3.85, 3.01, 2.71, 2.39, 3.79, 3.16, 9.92, 6.97,
5.44, 4.17, 3.41, 2.75, 3.01, 2.86, 2.62, 3.03, 3.31, 8.64, 6.23, 4.34, 3.51, 2.86, 2.2,
1.53 (31 samples, never three consecutive under 1.5 — the two lowest points, 1.62 and 1.53,
have no adjacent sample under 1.5 to build a streak around either one).

- `docker info`: exit 0.
- `docker ps --format '{{.Names}} {{.Status}}'`: `spur-spur-1 Up 41 hours (healthy)`,
  `fleet-user Exited (2) 19 hours ago`.
- Load after: 4.74.

Decisive (D-05): no — the 900 s cap expired; recorded regardless, per D-16 ("whatever it
reads").

**The run aborted (exit 1) after every request had been sent** — `sc3.status.json` records
`state: aborted`, `reason: "sc3-run1 exited 1"`. `run_composed`'s own `ThreadPoolExecutor`
`with` block waits for all ten requests to finish before `bench/latency.py` tries to read
`future.result()` for each in firing order; the second future it reads (the worst row's own
future resolved cleanly first) raised `httpx.HTTPStatusError: 500 Internal Server Error`,
which propagated out of `run_composed`, out of `scenario_composed`, and out of
`run_experiment.py`'s `main()` before any markdown, summary or per-request table was ever
printed or written (`sc3-run1.stdout.txt` is 0 bytes; no `sc3-run1.summary.json` exists).
**No client-side per-request latency table exists for this run** — the harness never
produced one. Everything below is read from the server's own records
(`sc3.server1.records.jsonl`), not from the client.

**Per-request outcomes, as the server recorded them** (firing order = `COMPOSED_ROWS`;
"Alone" is the single-build time from the re-run table, for reference only — SC3 is not
that measurement):

| Composed row | Alone (s) | Request | Server outcome | Duration |
|---|---|---|---|---|
| 4 (worst) | 29.42 | `51e80f35` | admitted, slot 0 — `BuildTimeout` | 30.004 s |
| 2 | 28.92 | `912cd2d4` | admitted, slot 0 — crashed, undocumented `500` (see Finding) | 30.000 s |
| 3 | 28.87 | `33260796` | `queue.refused` (503 busy) | instant |
| 1 | 28.61 | `0fc30d53` | admitted, slot 1 — crashed, undocumented `500` (see Finding) | 30.000 s |
| 9 | 27.27 | `4b777b09` | admitted, slot 1 — `BuildTimeout` | 30.002 s |
| 6 | 24.91 | `e4f8e9a6` | `queue.refused` (503 busy) | instant |
| 10 | 24.06 | `a76fb01b` | `queue.refused` (503 busy) | instant |
| 12 | 22.26 | `5d0b7449` | `queue.refused` (503 busy) | instant |
| 11 | 22.09 | `22767e72` | `queue.refused` (503 busy) | instant |
| 5 | 16.80 | `ef3c2387` | `queue.refused` (503 busy) | instant |

Outcome counts: 0 of 10 served (`200`); 6 of 10 refused by admission control (`503 busy`,
`queue.refused`, all within 08:23:05.3549–08:23:05.3959 UTC, `in_flight: 4, max_queued: 4`
on every one); 4 of 10 admitted, and **all four** exceeded `SPUR_BUILD_TIMEOUT` and were
recorded `build.failed` — two (`51e80f35`, `4b777b09`) with the documented `BuildTimeout`
exception the client would have read as `503 timeout`; two (`912cd2d4`, `0fc30d53`) with an
`AttributeError` inside the server that produced an undocumented raw `500` instead (the
client's `_fetch` raises on that, which is what aborted the run).

**The worst row's own outcome:** `51e80f35` (row 4, 29.42 s alone) did **not** complete
inside `SPUR_BUILD_TIMEOUT`'s 30 s shipping default under this composition — it was
terminated at 30.004 s, 0.58 s past where it finishes alone and squarely past the margin
Phase 12's re-run measured ("0.58 s of margin (~1.02x)") assuming no concurrent contention.

**`/api/health` `workers_replaced`:** 0 → 2 (a fresh server starts with
`BuildPool.replaced == 0`, `src/spur/pool.py` line 77; both hash slots recorded exactly one
`worker.replaced` event each, `cause: "timeout"` — slot 0 after `51e80f35`'s timeout, slot 1
after `4b777b09`'s).

**In-process and split-poller idle/under-load p95: do not exist for this run.** Both are
computed from `run.requests[].sent`/`.done` (`run_experiment.py`'s `composed_run`) or from
`ComposedRun` itself — neither was ever built, because `run_composed` raised before
returning. `sc3-run1.poller.jsonl` (32,037 raw `/api/health` latency samples) is committed
in full, but the idle/under-load boundary the harness computes from the crashed run's own
timestamps does not exist; reporting a ratio from a differently-chosen boundary would be a
plausible-looking number this project does not print (L08). No ratio is reported here.

**Server record counts** (`sc3.server1.records.jsonl`, excluding uvicorn lifecycle lines):

| Event | Count |
|---|---|
| `build.started` | 4 |
| `queue.refused` | 6 |
| `build.failed` | 4 |
| `worker.replaced` | 2 (slot 0, cause `timeout`; slot 1, cause `timeout`) |
| `export.served` | 0 |

**Finding.** The composed worst row did not complete under ten concurrent builds in the
shipped configuration. Six of ten requests were refused by admission control exactly as
designed (`503 busy`, 4 in flight already). Of the four admitted, both pairs shared a hash
slot (D-07's affinity, uncontrollable from the client) and both pairs hit
`SPUR_BUILD_TIMEOUT` together: the first request on each slot (`51e80f35`, `4b777b09`)
timed out cleanly and had its worker replaced; the second request on the *same* slot
(`912cd2d4`, `0fc30d53`) — timing out moments later on the same incident — ran
`_run_with_timeout`'s own `except TimeoutError` branch against an executor its slot-mate's
`recreate_for` call had already shut down, and crashed with an `AttributeError` that reached
the client as an undocumented `500` instead of one of the three contracted `503` types. The
worst row itself, which has only 0.58 s of margin alone, also failed to finish inside 30 s
once paired with contention from the other requests. Measured once, not repeated (D-16);
not re-run in search of a cleaner reading.

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
holds `hex_cell` at 3 mm (the sweep's own chosen input, the value 11-02's spike
measured; the field's default is 0 = off) and varies `hex_wall` {0.4, 5} instead, so
every one of its four gears (module x recess) is raised past 3 mm to `HEX_CELL_CAP`
(11-05's raise-to-fit) rather than measuring a cell size that was never going to be
requested. The planning probe (11-06-PLAN.md's `<interfaces>`)
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
or re-run to green -- they are recorded above exactly as measured. Task 2's checkpoint
decision: lower `hole_count`'s and `spoke_count`'s `le` from 200 to 60 and 40 (D-18's
first offer, the orchestrator's recommendation, accepted verbatim); the honeycomb's one
over-share row is accepted as measured, `HEX_CELL_CAP` unchanged at 120. The re-run below
proves the new `le`.

### Re-run after the gate (lower-le)

`hole_count`'s and `spoke_count`'s `le` lowered to 60 and 40 (`feat` commit `2224697`);
`bench/sweeps/hole_cutout.json` and `bench/sweeps/spoke_cutout.json` re-generated at the
new count on every row, same sizes and moduli as the first run, and re-run through
`make bench.build`. The honeycomb sweep is unchanged and was not re-run -- its one
over-share row was accepted, not gated on a new limit.

#### Host state (re-run)

- Machine, Python and kernel versions: unchanged from the first run's host state
- HEAD: `9d523b5` (the commit the sweep files were re-read from; the `feat` commit that
  changed `le` and the sweep files landed after this run started)
- `uptime` moments before each run: hole 3.72; spoke 3.72 (same reading, back-to-back runs)
- Load averages at start (`os.getloadavg()`): hole 9.27, 5.84, 4.92; spoke 32.17, 14.18,
  8.21 -- both readings are again well above this project's "quiet" bar (>1.5), the spoke
  run markedly more loaded than either the first run (5-10) or the hole re-run; the same
  L08 caveat applies -- a quieter host reads every row faster, never slower.

#### Holes at `le` 60

| Parameter set | Build (s) | Fine STL (s) | STEP (s) | Build + slower export (s) | Inside 30 s |
|---|---|---|---|---|---|
| teeth=200 module=1.75 hole_count=60 hole_d=1 hole_circle_d=183.4 recess_sides=both | 8.62 | 3.17 | 0.57 | 11.79 | yes |
| teeth=200 module=1.75 hole_count=60 hole_d=1 hole_circle_d=183.4 recess_sides=none | 2.41 | 1.70 | 0.52 | 4.11 | yes |
| teeth=200 module=1.75 hole_count=60 hole_d=4.9 hole_circle_d=339.9 recess_sides=both | 3.19 | 1.08 | 0.46 | 4.27 | yes |
| teeth=200 module=1.75 hole_count=60 hole_d=4.9 hole_circle_d=339.9 recess_sides=none | 2.47 | 0.95 | 0.46 | 3.42 | yes |
| teeth=200 module=10 hole_count=60 hole_d=1 hole_circle_d=400 recess_sides=both | 3.07 | 1.19 | 0.41 | 4.26 | yes |
| teeth=200 module=10 hole_count=60 hole_d=1 hole_circle_d=400 recess_sides=none | 2.41 | 1.74 | 0.50 | 4.15 | yes |
| teeth=200 module=10 hole_count=60 hole_d=5.85 hole_circle_d=400 recess_sides=both | 3.24 | 1.19 | 0.41 | 4.43 | yes |
| teeth=200 module=10 hole_count=60 hole_d=5.85 hole_circle_d=400 recess_sides=none | 2.41 | 1.68 | 0.47 | 4.10 | yes |

**Heaviest:** teeth=200 module=1.75 hole_count=60 hole_d=1 hole_circle_d=183.4 recess_sides=both -- 11.79 s of 30 s.

Every hole row is now inside budget -- the same row that overran at `le` 200 (41.85 s) is
still the heaviest at `le` 60 (11.79 s, 2.54x margin), confirming the cost scales with
count on this row (the recess-crossing fillet split, Pitfall 8) rather than being fixed.

#### Spokes at `le` 40

| Parameter set | Build (s) | Fine STL (s) | STEP (s) | Build + slower export (s) | Inside 30 s |
|---|---|---|---|---|---|
| teeth=200 module=1.75 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=both | 16.89 | 0.79 | 0.80 | 17.69 | yes |
| teeth=200 module=1.75 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=none | 6.73 | 0.86 | 0.63 | 7.59 | yes |
| teeth=200 module=1.75 spoke_count=40 spoke_width=4.3 hub_d=300 rim_wall=10 spoke_fillet=5 recess_sides=both | 4.16 | 1.02 | 0.69 | 5.18 | yes |
| teeth=200 module=1.75 spoke_count=40 spoke_width=4.3 hub_d=300 rim_wall=10 spoke_fillet=5 recess_sides=none | 3.41 | 0.91 | 0.65 | 4.33 | yes |
| teeth=200 module=10 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=both | 17.55 | 0.97 | 0.83 | 18.52 | yes |
| teeth=200 module=10 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=none | 7.58 | 1.04 | 0.63 | 8.63 | yes |
| teeth=200 module=10 spoke_count=40 spoke_width=5.85 hub_d=400 rim_wall=100 spoke_fillet=5 recess_sides=both | 13.83 | 1.03 | 0.82 | 14.86 | yes |
| teeth=200 module=10 spoke_count=40 spoke_width=5.85 hub_d=400 rim_wall=100 spoke_fillet=5 recess_sides=none | 3.49 | 1.12 | 0.64 | 4.61 | yes |

**Heaviest:** teeth=200 module=10 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=both -- 18.52 s of 30 s.

Every spoke row is now inside budget -- the row that overran at `le` 200 on this same
module (68.70 s) is the heaviest at `le` 40 (18.52 s, 1.62x margin). This run's load
(32.17 at start) is the highest recorded anywhere in this section, well above the first
run's own 5-10 and above the hole re-run's 9.27 -- the 18.52 s figure is likely
conservative, not a quiet-host number.

#### Room beside Phase 10's tip-chamfer row

Naive addition only (this sweep builds one gear at a time; Phase 12 re-measures the real
composition, as the first run's own margin section already noted): heaviest hole re-run
(11.79 s) plus Phase 10's 14.87 s tip-chamfer row totals 26.66 s, 3.34 s inside 30 s.
Heaviest spoke re-run (18.52 s) plus the same 14.87 s totals 33.39 s -- 3.39 s **over**
30 s, not the ~2 s margin the gate's decision anticipated from the planning estimate. This
arithmetic total was measured under this run's exceptional load (32.17); the accepted
decision's rationale (~0.3 s/sector, projecting margin at typical load) is not
contradicted by a single reading taken under 20x the "quiet" load, but the gap is real
enough at this reading to record rather than round away (L08) -- filed as
`docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md`
(must), not fixed here: Task 3's own scope is the `le`, not a new build-time guarantee on
an arithmetic sum Phase 12 measures for real.

### make verify wall time

`time make verify` (host: 12 CPUs, arm64, 32.0 GiB RAM, Python 3.12.13, load averages
3.07/4.04/4.65 at start, HEAD `67e0e3b`): **621 passed in 177.62s** -- **178.55s** wall
time (`time`, includes lint/typecheck/import-lint/no-fake-done), against Phase 10's
recorded **453 passed** / **98.17s** wall. The phase's body-cutout tests (168 new, across
11-01 through 11-08) add **+80.38s** to the gate, measured rather than assumed. The wall
time is now past 150 s, so every commit's pre-commit hook -- which runs this same `make
verify` -- takes about that long too (D-23;
`docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`).

## Composed build and export time (Phase 12)

ROADMAP SC3 as amended (12-01-SUMMARY.md, per 12-CONTEXT.md D-06): this section measures
"the heaviest combined configuration the composed sweep measures -- each cutout pattern
stacked with the tip chamfer and a recess on the heaviest bore its rules allow -- and each
individual feature", replacing the literal "recess + hex pattern" the original roadmap
text named before this number existed. The runner is `bench/build_time.py`, unchanged
except for D-16's two new columns (Fine STL bytes, Triangles) and the `**Largest fine
STL:**` line -- the same script every sweep since Phase 8 has used (08-CONTEXT.md D-12).

`bench/sweeps/composed.json`'s 18-row design (D-01, this plan's Task 2): each of the three
cutout patterns' own recorded heaviest row (spokes at `le` 40, holes at `le` 60, honeycomb
at the cap) is stacked with the tip chamfer at that gear's own cap and both recesses, on
the largest `bore_hex` its hub rule allows (computed from `bore_mouth_limit` against the
cutout's hub datum -- 43.35 mm for the spokes' `hub_d` 52, 156.3 mm for the module-1.75
holes' `hole_circle_d` 183.4, 200 mm -- the field's own `le` -- everywhere else, since
`bore_hex` 200 reaches 115.47 mm at the corners and would conflict with the spoke row's
26 mm hub and the module-1.75 hole row's 91.2 mm inner edge) and separately on a keyed
round bore (`bore_d` 9, `bore_flat` 0, `keyway_width` 3, `keyway_depth` 1.4 -- the default
bore's own keyway, whose floor corner at ~6.18 mm never approaches any cutout's hub
datum), at module 1.75 and module 10 (12 rows) -- plus the six single-feature heaviest
rows re-run unchanged as same-host baselines (6 rows), all pinned exactly by
`tests/test_bench.py`'s `test_the_composed_sweep_stacks_each_cutout_on_its_heaviest_bore_beside_six_baselines`.
09-04's lesson stands: the heaviest row was not always the largest feature, so both
moduli are measured for every pattern rather than assumed from one.

One planning-only computation worth recording, not a prediction of time (no kernel probe
backs it): the module-1.75 hex-bore holes row moves the face recess to 257.1-269.1 mm
diameter, clear of the holes on the 183.4 mm bolt circle, while the keyed row at the same
holes keeps the recess at 171.4-183.4 mm, where the holes straddle its outer wall -- the
same crossing that made the single-feature hole row the heaviest reading in Phase 11
("Body cutout build and export time (Phase 11)", "Holes").

This sweep builds one gear at a time through `make bench.build` (D-04); no
`bench.latency` run and no concurrent-load scenario is attempted for any row here -- the
ten-concurrent scenario for a composed worst row stays out of this phase (12-CONTEXT.md
`<deferred>`; the trigger re-homes into
`docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` when the tip-chamfer
debt file below is resolved).

Two runs were taken. Both started with the host quiet (`uptime`/`sysctl -n vm.loadavg`
read below 1.5 immediately before `make bench.build` was launched each time -- Run 1 at
1.13, Run 2 at 1.33), but `bench/build_time.py`'s own `report()` reads
`os.getloadavg()` only once, after every row in the sweep has already built -- so the
"Load averages at start" figure it prints is actually a reading taken at the end of a
~6-7 minute run, not literally at its start. Both runs read well above D-02's 1.5 bar at
that point (12.66 and 7.04) despite the genuinely quiet host each run began on; this
matches every earlier sweep in this file ("Re-run after the gate (lower-le)", "Host state
(re-run)": "both readings are again well above this project's 'quiet' bar"). Per D-02
neither run is decisive, and per this plan's prohibitions no run is dropped, re-picked or
re-run to green -- both are recorded below exactly as measured, and the `le`/timeout
decision this raises is left to 12-03's checkpoint. Every `uptime`/`sysctl` reading taken
while waiting for the host to quiet down before each run is in the session record; the
notable ones are reproduced under each run below.

### Run 1 (load 12.66 at start; not decisive)

Readings taken while waiting for the host to quiet before this run (`sysctl -n
vm.loadavg`, polled about every 30-60 s from 02:48:52Z, D-02's 30-minute budget): load1
fell from 5.48 to 1.13 over eighteen minutes, crossing below the 1.5 bar three times
(1.49 at 03:05:53Z, 1.38 at 03:06:30Z) before the final pre-run check read **1.13** at
03:07:00Z UTC, when `make bench.build SWEEP=bench/sweeps/composed.json` was launched.

- Machine: 12 CPUs, arm64, 32.0 GiB RAM
- Python: 3.12.13
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `682dca6`
- Sweep: `bench/sweeps/composed.json`
- Load averages at start: 12.66, 7.79, 6.25
- SPUR_BUILD_TIMEOUT: 30 s, a cold request is one build plus one export

| Parameter set | Build (s) | Fine STL (s) | STEP (s) | Build + slower export (s) | Inside 30 s | Fine STL (bytes) | Triangles |
|---|---|---|---|---|---|---|---|
| teeth=200 module=1.75 bore_hex=43.35 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both | 30.38 | 0.76 | 0.92 | 31.30 | **NO** | 7830684 | 156612 |
| teeth=200 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both | 30.69 | 0.78 | 0.87 | 31.56 | **NO** | 7921984 | 158438 |
| teeth=200 module=10 bore_hex=43.35 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 30.41 | 0.95 | 0.88 | 31.36 | **NO** | 8517584 | 170350 |
| teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 31.01 | 0.97 | 0.87 | 31.98 | **NO** | 8573384 | 171466 |
| teeth=200 module=1.75 bore_hex=156.3 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both | 16.06 | 0.67 | 0.48 | 16.73 | yes | 11279684 | 225592 |
| teeth=200 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both | 21.97 | 3.17 | 0.63 | 25.15 | yes | 14207884 | 284156 |
| teeth=200 module=10 bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both | 14.44 | 1.20 | 0.48 | 15.64 | yes | 17306084 | 346120 |
| teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both | 14.93 | 1.25 | 0.49 | 16.18 | yes | 16015284 | 320304 |
| teeth=200 module=1.75 bore_hex=200 hex_cell=3 hex_wall=0.4 tip_chamfer=1.75 recess_sides=both | 26.54 | 0.69 | 0.93 | 27.47 | yes | 10723884 | 214476 |
| teeth=200 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hex_cell=3 hex_wall=0.4 tip_chamfer=1.75 recess_sides=both | 23.18 | 0.73 | 0.97 | 24.15 | yes | 6966084 | 139320 |
| teeth=200 module=10 bore_hex=200 hex_cell=3 hex_wall=5 tip_chamfer=3 recess_sides=both | 20.94 | 0.89 | 0.95 | 21.89 | yes | 7859984 | 157198 |
| teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hex_cell=3 hex_wall=5 tip_chamfer=3 recess_sides=both | 21.34 | 0.95 | 0.97 | 22.31 | yes | 8210984 | 164218 |
| teeth=200 module=1.75 bore_hex=200 recess_sides=both bore_chamfer=0.4 | 4.39 | 0.61 | 0.40 | 5.00 | yes | 10224284 | 204484 |
| teeth=200 module=1.75 bore_d=200 bore_flat=150 keyway_width=3 keyway_depth=1.4 recess_sides=both bore_chamfer=0.4 | 4.15 | 0.66 | 0.40 | 4.81 | yes | 10144684 | 202892 |
| teeth=200 module=1.75 tip_chamfer=1.75 recess_sides=both | 14.09 | 0.71 | 0.47 | 14.80 | yes | 8866484 | 177328 |
| teeth=200 module=1.75 hole_count=60 hole_d=1 hole_circle_d=183.4 recess_sides=both | 8.54 | 3.14 | 0.55 | 11.67 | yes | 14447884 | 288956 |
| teeth=200 module=10 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=both | 17.92 | 0.95 | 0.80 | 18.86 | yes | 8478184 | 169562 |
| teeth=200 module=1.75 hex_cell=3 hex_wall=0.4 recess_sides=both | 7.76 | 0.78 | 0.90 | 8.66 | yes | 7206084 | 144120 |

**Heaviest:** teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both -- 31.98 s of 30 s.
**Largest fine STL:** teeth=200 module=10 bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both -- 17306084 bytes, 346120 triangles.

Run exit code: 1 (`make`'s own wrapper exit: 2) -- an over-budget row, not a build failure;
`bench/build_time.py main()` returns 1 whenever any row reads over the timeout, exactly as
documented, and `make` reports its sub-command's nonzero status as its own `Error 1`.

### Run 2 (load 7.04 at start; not decisive)

Readings taken while re-quieting the host before this run: load1 fell from 8.50 (checked
immediately after Run 1's report printed) to 1.33 over about seven minutes (7.35 at
03:13:55Z falling to 1.36 at 03:19:55Z), with the final pre-run check reading **1.33** at
03:20:09Z UTC, when this run was launched immediately after.

- Machine: 12 CPUs, arm64, 32.0 GiB RAM
- Python: 3.12.13
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `682dca6`
- Sweep: `bench/sweeps/composed.json`
- Load averages at start: 7.04, 5.47, 5.19
- SPUR_BUILD_TIMEOUT: 30 s, a cold request is one build plus one export

| Parameter set | Build (s) | Fine STL (s) | STEP (s) | Build + slower export (s) | Inside 30 s | Fine STL (bytes) | Triangles |
|---|---|---|---|---|---|---|---|
| teeth=200 module=1.75 bore_hex=43.35 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both | 30.31 | 0.76 | 0.85 | 31.16 | **NO** | 7830684 | 156612 |
| teeth=200 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both | 30.75 | 0.77 | 0.86 | 31.61 | **NO** | 7921984 | 158438 |
| teeth=200 module=10 bore_hex=43.35 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 30.66 | 0.94 | 0.87 | 31.59 | **NO** | 8517584 | 170350 |
| teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 30.95 | 0.95 | 0.87 | 31.90 | **NO** | 8573384 | 171466 |
| teeth=200 module=1.75 bore_hex=156.3 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both | 16.07 | 0.66 | 0.48 | 16.73 | yes | 11279684 | 225592 |
| teeth=200 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both | 21.87 | 3.18 | 0.63 | 25.05 | yes | 14207884 | 284156 |
| teeth=200 module=10 bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both | 14.36 | 1.23 | 0.49 | 15.59 | yes | 17306084 | 346120 |
| teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both | 14.81 | 1.23 | 0.48 | 16.04 | yes | 16015284 | 320304 |
| teeth=200 module=1.75 bore_hex=200 hex_cell=3 hex_wall=0.4 tip_chamfer=1.75 recess_sides=both | 26.54 | 0.71 | 0.94 | 27.48 | yes | 10723884 | 214476 |
| teeth=200 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hex_cell=3 hex_wall=0.4 tip_chamfer=1.75 recess_sides=both | 23.12 | 0.72 | 0.97 | 24.09 | yes | 6966084 | 139320 |
| teeth=200 module=10 bore_hex=200 hex_cell=3 hex_wall=5 tip_chamfer=3 recess_sides=both | 20.95 | 0.89 | 0.95 | 21.90 | yes | 7859984 | 157198 |
| teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hex_cell=3 hex_wall=5 tip_chamfer=3 recess_sides=both | 21.17 | 0.94 | 0.96 | 22.13 | yes | 8210984 | 164218 |
| teeth=200 module=1.75 bore_hex=200 recess_sides=both bore_chamfer=0.4 | 4.36 | 0.61 | 0.40 | 4.97 | yes | 10224284 | 204484 |
| teeth=200 module=1.75 bore_d=200 bore_flat=150 keyway_width=3 keyway_depth=1.4 recess_sides=both bore_chamfer=0.4 | 4.15 | 0.65 | 0.40 | 4.80 | yes | 10144684 | 202892 |
| teeth=200 module=1.75 tip_chamfer=1.75 recess_sides=both | 14.16 | 0.70 | 0.47 | 14.85 | yes | 8866484 | 177328 |
| teeth=200 module=1.75 hole_count=60 hole_d=1 hole_circle_d=183.4 recess_sides=both | 8.59 | 3.15 | 0.57 | 11.74 | yes | 14447884 | 288956 |
| teeth=200 module=10 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=both | 17.80 | 0.94 | 0.80 | 18.74 | yes | 8478184 | 169562 |
| teeth=200 module=1.75 hex_cell=3 hex_wall=0.4 recess_sides=both | 7.74 | 0.78 | 0.89 | 8.64 | yes | 7206084 | 144120 |

**Heaviest:** teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both -- 31.90 s of 30 s.
**Largest fine STL:** teeth=200 module=10 bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both -- 17306084 bytes, 346120 triangles.

Run exit code: 1 (`make`'s own wrapper exit: 2), same reading as Run 1.

Every fine-STL byte count and triangle count is identical between the two runs on every
row (the geometry is deterministic on the pinned kernel), and every build/export time is
within 0.6 s of its Run 1 counterpart -- the four over-budget spoke rows read 31.16-31.90 s
here against 31.30-31.98 s in Run 1. Neither the 12.66-vs-7.04 gap in the script's own
load reading nor the roughly two-fold difference in load1 between the runs' pre-launch
checks (1.13 vs 1.33) shows up as a corresponding difference in build cost -- consistent
with the report's load figure reflecting load at the end of a long run rather than the
quiet host each run actually started on, per the note above. This is recorded as a fact
about these two readings, not a basis for any `le` or timeout decision (D-02).

### Run 3 (load 2.74 at start; not decisive)

12-03's Task 2 checkpoint asked for a quiet re-run (D-02, option `quiet-rerun`) before any
gate decision. Readings taken while waiting for the host to quiet before this run
(`sysctl -n vm.loadavg`, polled about every 45 s from 07:03:04Z, D-02's 30-minute budget):
load1 fluctuated between **1.98** (the single dip below 2, at 07:30:06Z) and 9.82 (a brief
spike at 07:13:35Z) and never once read below the 1.5 bar across the full 30-minute
window; the last reading before the budget expired was 2.65 at 07:33:06Z. Per D-02's own
cap on the wait ("for at most 30 minutes") the sweep was launched once that budget
expired rather than waited on further, with a final pre-launch check reading 2.72 at
07:34:07Z UTC -- decisiveness is judged from the runner's own at-start figure below, the
same rule 12-02 Task 3 applied (the wait is capped, not a precondition for launching).
`bench/build_time.py`'s `report()` now reads `os.getloadavg()` before the first row
builds (`9b9af43`, this plan's pre-Task-1 deviation), so the load figure below is a
genuine at-start reading, not the end-of-run figure Runs 1 and 2 carried.

- Machine: 12 CPUs, arm64, 32.0 GiB RAM
- Python: 3.12.13
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `238b6cc`
- Sweep: `bench/sweeps/composed.json`
- Load averages at start: 2.74, 2.73, 3.11
- SPUR_BUILD_TIMEOUT: 30 s, a cold request is one build plus one export

| Parameter set | Build (s) | Fine STL (s) | STEP (s) | Build + slower export (s) | Inside 30 s | Fine STL (bytes) | Triangles |
|---|---|---|---|---|---|---|---|
| teeth=200 module=1.75 bore_hex=43.35 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both | 31.74 | 0.80 | 0.94 | 32.68 | **NO** | 7830684 | 156612 |
| teeth=200 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both | 31.21 | 0.81 | 0.94 | 32.14 | **NO** | 7921984 | 158438 |
| teeth=200 module=10 bore_hex=43.35 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 32.32 | 1.00 | 0.89 | 33.32 | **NO** | 8517584 | 170350 |
| teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 31.63 | 0.99 | 0.88 | 32.62 | **NO** | 8573384 | 171466 |
| teeth=200 module=1.75 bore_hex=156.3 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both | 16.22 | 0.68 | 0.49 | 16.89 | yes | 11279684 | 225592 |
| teeth=200 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both | 22.08 | 3.20 | 0.63 | 25.28 | yes | 14207884 | 284156 |
| teeth=200 module=10 bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both | 14.55 | 1.27 | 0.49 | 15.82 | yes | 17306084 | 346120 |
| teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both | 14.91 | 1.27 | 0.49 | 16.18 | yes | 16015284 | 320304 |
| teeth=200 module=1.75 bore_hex=200 hex_cell=3 hex_wall=0.4 tip_chamfer=1.75 recess_sides=both | 26.67 | 0.71 | 0.94 | 27.61 | yes | 10723884 | 214476 |
| teeth=200 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hex_cell=3 hex_wall=0.4 tip_chamfer=1.75 recess_sides=both | 23.20 | 0.75 | 0.98 | 24.18 | yes | 6966084 | 139320 |
| teeth=200 module=10 bore_hex=200 hex_cell=3 hex_wall=5 tip_chamfer=3 recess_sides=both | 21.09 | 0.92 | 0.97 | 22.06 | yes | 7859984 | 157198 |
| teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hex_cell=3 hex_wall=5 tip_chamfer=3 recess_sides=both | 21.31 | 0.96 | 0.97 | 22.28 | yes | 8210984 | 164218 |
| teeth=200 module=1.75 bore_hex=200 recess_sides=both bore_chamfer=0.4 | 4.40 | 0.65 | 0.41 | 5.05 | yes | 10224284 | 204484 |
| teeth=200 module=1.75 bore_d=200 bore_flat=150 keyway_width=3 keyway_depth=1.4 recess_sides=both bore_chamfer=0.4 | 4.16 | 0.64 | 0.39 | 4.80 | yes | 10144684 | 202892 |
| teeth=200 module=1.75 tip_chamfer=1.75 recess_sides=both | 14.21 | 0.75 | 0.51 | 14.95 | yes | 8866484 | 177328 |
| teeth=200 module=1.75 hole_count=60 hole_d=1 hole_circle_d=183.4 recess_sides=both | 8.63 | 3.15 | 0.57 | 11.79 | yes | 14447884 | 288956 |
| teeth=200 module=10 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=both | 17.95 | 0.95 | 0.85 | 18.90 | yes | 8478184 | 169562 |
| teeth=200 module=1.75 hex_cell=3 hex_wall=0.4 recess_sides=both | 7.82 | 0.83 | 0.91 | 8.73 | yes | 7206084 | 144120 |

**Heaviest:** teeth=200 module=10 bore_hex=43.35 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both -- 33.32 s of 30 s.
**Largest fine STL:** teeth=200 module=10 bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both -- 17306084 bytes, 346120 triangles.

Run exit code: 1 (`make`'s own wrapper exit: 2), same reading as Runs 1 and 2.

Not decisive: the script's own 1-minute figure at start (2.74) sits well above D-02's 1.5
bar -- higher, in fact, than either Run 1's or Run 2's pre-launch check (1.13, 1.33), even
though this run's figure is now a genuine at-start reading and theirs were end-of-run
readings under the pre-fix `report()`. No `le`, `HEX_CELL_CAP` or `SPUR_BUILD_TIMEOUT`
decision may rest on this run either (D-02). The same four spoke rows read over budget
again, each 0.5-1.3 s worse than its Run 1/Run 2 counterpart (32.14-33.32 s here against
31.16-31.98 s in Runs 1-2) -- consistent with, not contradicted by, the heavier host load
this run measured at its genuine start.

### Run 4 (load 1.54 at start; not decisive)

12-03's Task 2 checkpoint asked for a second quiet re-run (D-02, option `quiet-rerun`
again) after Run 3 also came in non-decisive; the human stepped away from the machine so
the host could actually go quiet. Readings taken while waiting for the host to quiet
before this run (`sysctl -n vm.loadavg`, polled about every 45 s from 07:48:41Z, D-02's
30-minute budget): load1 fell from 4.31 to **1.46** over about eighteen minutes, dipping
as low as 1.64 at 08:05:57Z before crossing the 1.5 bar for good at 08:06:42Z UTC, when
the wait script reported QUIET and the sweep was launched immediately, no second
pre-check added. By the time the launch pre-check ran nine seconds later (08:06:51Z),
load1 had already climbed back to 1.50, and by the time `bench/build_time.py`'s own
`report()` took its genuine at-start reading a few seconds further into Python/CadQuery
startup, it read **1.54** -- just above D-02's 1.5 bar, illustrating how quickly this
host's load can drift in the seconds between a shell-level quiet check and the runner's
own measurement.

- Machine: 12 CPUs, arm64, 32.0 GiB RAM
- Python: 3.12.13
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `ea31799`
- Sweep: `bench/sweeps/composed.json`
- Load averages at start: 1.54, 2.54, 3.44
- SPUR_BUILD_TIMEOUT: 30 s, a cold request is one build plus one export

| Parameter set | Build (s) | Fine STL (s) | STEP (s) | Build + slower export (s) | Inside 30 s | Fine STL (bytes) | Triangles |
|---|---|---|---|---|---|---|---|
| teeth=200 module=1.75 bore_hex=43.35 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both | 30.59 | 0.77 | 0.87 | 31.46 | **NO** | 7830684 | 156612 |
| teeth=200 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both | 30.66 | 0.78 | 0.88 | 31.53 | **NO** | 7921984 | 158438 |
| teeth=200 module=10 bore_hex=43.35 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 30.58 | 0.94 | 0.88 | 31.52 | **NO** | 8517584 | 170350 |
| teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 31.06 | 0.96 | 0.88 | 32.03 | **NO** | 8573384 | 171466 |
| teeth=200 module=1.75 bore_hex=156.3 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both | 16.10 | 0.71 | 0.48 | 16.80 | yes | 11279684 | 225592 |
| teeth=200 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both | 21.87 | 3.18 | 0.63 | 25.05 | yes | 14207884 | 284156 |
| teeth=200 module=10 bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both | 14.44 | 1.21 | 0.49 | 15.65 | yes | 17306084 | 346120 |
| teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both | 14.86 | 1.30 | 0.52 | 16.16 | yes | 16015284 | 320304 |
| teeth=200 module=1.75 bore_hex=200 hex_cell=3 hex_wall=0.4 tip_chamfer=1.75 recess_sides=both | 26.53 | 0.69 | 0.95 | 27.49 | yes | 10723884 | 214476 |
| teeth=200 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hex_cell=3 hex_wall=0.4 tip_chamfer=1.75 recess_sides=both | 23.11 | 0.74 | 0.98 | 24.09 | yes | 6966084 | 139320 |
| teeth=200 module=10 bore_hex=200 hex_cell=3 hex_wall=5 tip_chamfer=3 recess_sides=both | 21.01 | 0.91 | 0.96 | 21.97 | yes | 7859984 | 157198 |
| teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hex_cell=3 hex_wall=5 tip_chamfer=3 recess_sides=both | 21.27 | 0.94 | 0.97 | 22.23 | yes | 8210984 | 164218 |
| teeth=200 module=1.75 bore_hex=200 recess_sides=both bore_chamfer=0.4 | 4.46 | 0.63 | 0.42 | 5.09 | yes | 10224284 | 204484 |
| teeth=200 module=1.75 bore_d=200 bore_flat=150 keyway_width=3 keyway_depth=1.4 recess_sides=both bore_chamfer=0.4 | 4.16 | 0.64 | 0.40 | 4.80 | yes | 10144684 | 202892 |
| teeth=200 module=1.75 tip_chamfer=1.75 recess_sides=both | 14.20 | 0.72 | 0.48 | 14.92 | yes | 8866484 | 177328 |
| teeth=200 module=1.75 hole_count=60 hole_d=1 hole_circle_d=183.4 recess_sides=both | 8.57 | 3.17 | 0.57 | 11.73 | yes | 14447884 | 288956 |
| teeth=200 module=10 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=both | 17.43 | 0.94 | 0.81 | 18.36 | yes | 8478184 | 169562 |
| teeth=200 module=1.75 hex_cell=3 hex_wall=0.4 recess_sides=both | 7.77 | 0.81 | 0.89 | 8.66 | yes | 7206084 | 144120 |

**Heaviest:** teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both -- 32.03 s of 30 s.
**Largest fine STL:** teeth=200 module=10 bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both -- 17306084 bytes, 346120 triangles.

Run exit code: 1 (`make`'s own wrapper exit: 2), same reading as Runs 1-3.

Not decisive: the script's own 1-minute figure at start (1.54) sits just above D-02's 1.5
bar -- the closest of the four runs to date, and the only one where a shell-level check
bracketed the bar on either side of the runner's own reading (1.46 at the QUIET verdict,
1.50 nine seconds later at the launch pre-check). No `le`, `HEX_CELL_CAP` or
`SPUR_BUILD_TIMEOUT` decision may rest on this run either (D-02). The same four spoke rows
read over budget again, this time 31.46-32.03 s -- inside the band of all three earlier
runs (31.16-33.32 s across Runs 1-3) -- consistent with a genuinely quieter host than
Run 3's 2.74 but still not a decisive reading.

### Against the single-feature baselines

No decisive run: no comparison against the single-feature baselines or the Phase 10/11
arithmetic totals is drawn from these readings (D-02). For the record, the six baseline
rows (Run 2, columns 13-18 above) read within the same 0.6 s band as their own recorded
same-host figures cited in `<interfaces>` (hex 4.97 s vs. 5.08 s on record, keyway 4.80 s
vs. 4.85 s, tip chamfer 14.85 s vs. 14.87 s, holes 11.74 s vs. 11.79 s, spokes 18.74 s vs.
18.52 s, honeycomb 8.64 s vs. 8.65 s) -- offered only as a same-host sanity check on the
runner, not as a decisive composed-vs-baseline comparison.

Decisive as of Run 4 (D-02 superseded for this gate; see `### Gate` below). Each
pattern's worst composed row (module 10, the heaviest bore its rules allow) beside
the arithmetic total it replaces -- 12-02-PLAN Task 3's own same-host figures, spokes
18.52 s + tip chamfer 14.87 s = 33.39 s, holes 11.79 s + 14.87 s = 26.66 s, honeycomb
8.65 s + 14.87 s = 23.52 s; measured numbers only, the difference stated, not
explained away:

| Pattern | Run 4's worst composed row | Measured (s) | Arithmetic total replaced (s) | Difference |
|---|---|---|---|---|
| Spokes | module=10, keyed bore, tip_chamfer=3, recess_sides=both | 32.03 | 33.39 | -1.36 |
| Holes | module=1.75, keyed bore, tip_chamfer=1.75, recess_sides=both | 25.05 | 26.66 | -1.61 |
| Honeycomb | module=1.75, hex bore, tip_chamfer=1.75, recess_sides=both | 27.49 | 23.52 | +3.97 |

Every composed row of Run 4 beside the same-host baselines it stacks (Run 4's own
columns 13-18: hex bore chamfer only 5.09 s, keyway bore chamfer only 4.80 s, tip
chamfer module=1.75/tip_chamfer=1.75 14.92 s, holes module=1.75 11.73 s, spokes
module=10 18.36 s, honeycomb module=1.75/hex_wall=0.4 8.66 s -- no same-host baseline
was measured for `tip_chamfer=3` or `hex_wall=5` alone, so a module=10 composed row is
compared against the nearest available baseline rather than a matched one, noted per
row; sums are naive arithmetic, not a prediction -- stacking features is not linearly
additive, and every composed row measures well under its naive sum):

| Composed row (Run 4) | Measured (s) | Baselines summed (s) | Difference (s) |
|---|---|---|---|
| module=1.75 hex spokes tip=1.75 | 31.46 | 5.09 + 14.92 + 18.36 (spokes baseline is module=10) = 38.37 | -6.91 |
| module=1.75 keyed spokes tip=1.75 | 31.53 | 4.80 + 14.92 + 18.36 (spokes baseline is module=10) = 38.08 | -6.55 |
| module=10 hex spokes tip=3 | 31.52 | 5.09 + 14.92 (chamfer baseline is tip_chamfer=1.75) + 18.36 = 38.37 | -6.85 |
| module=10 keyed spokes tip=3 | 32.03 | 4.80 + 14.92 (chamfer baseline is tip_chamfer=1.75) + 18.36 = 38.08 | -6.05 |
| module=1.75 hex holes tip=1.75 | 16.80 | 5.09 + 14.92 + 11.73 = 31.74 | -14.94 |
| module=1.75 keyed holes tip=1.75 | 25.05 | 4.80 + 14.92 + 11.73 = 31.45 | -6.40 |
| module=10 hex holes tip=3 | 15.65 | 5.09 + 14.92 (chamfer baseline is tip_chamfer=1.75) + 11.73 = 31.74 | -16.09 |
| module=10 keyed holes tip=3 | 16.16 | 4.80 + 14.92 (chamfer baseline is tip_chamfer=1.75) + 11.73 = 31.45 | -15.29 |
| module=1.75 hex honeycomb tip=1.75 | 27.49 | 5.09 + 14.92 + 8.66 = 28.67 | -1.18 |
| module=1.75 keyed honeycomb tip=1.75 | 24.09 | 4.80 + 14.92 + 8.66 = 28.38 | -4.29 |
| module=10 hex honeycomb tip=3 | 21.97 | 5.09 + 14.92 (chamfer baseline is tip_chamfer=1.75) + 8.66 (honeycomb baseline is hex_wall=0.4) = 28.67 | -6.70 |
| module=10 keyed honeycomb tip=3 | 22.23 | 4.80 + 14.92 (chamfer baseline is tip_chamfer=1.75) + 8.66 (honeycomb baseline is hex_wall=0.4) = 28.38 | -6.15 |

### SPUR_BUILD_TIMEOUT margin

No decisive run: no margin figure against `SPUR_BUILD_TIMEOUT`'s 30 s default, and no
factor against the ~4x the default was sized for, is computed from these readings (D-02).

Decisive as of Run 4 (D-02 superseded for this gate; see `### Gate` below).
`SPUR_BUILD_TIMEOUT`'s 30 s default was set at about 4x the 7.39 s worst build on
record (the "### `SPUR_BUILD_TIMEOUT`" section above). Four rows read over that 30 s
timeout on their own in Run 4 -- the same four spoke rows named in `### Gate` below,
31.46-32.03 s, 1.05-1.07x the timeout, leaving no margin. Among the rows that build
inside 30 s, the heaviest is the module=1.75 hex-bore honeycomb row at 27.49 s, leaving
1.09x -- the lightest margin of any in-budget row. This sweep builds one gear at a
time, so behaviour under concurrent builds is not measured here either (D-04; the
ten-concurrent question for a composed worst row re-homes to
docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md when the tip-chamfer
debt is resolved).

### Gate

No decisive row is recorded as over `SPUR_BUILD_TIMEOUT`: none. No decisive run: no `le`
or timeout decision may rest on these readings (D-02). For the record -- not a gate
verdict -- the same four rows (both module-1.75 and module-10 spokes, hex and keyed bore
alike, each stacked with the tip chamfer at its cap and both recesses) read over 30 s in
both non-decisive runs, within 0.7 s of each other run to run: `bore_hex=43.35
spoke_count=40 ... tip_chamfer=1.75` (31.30/31.16 s), the same row keyed (31.56/31.61 s),
`module=10` with the same spokes and `tip_chamfer=3` (31.36/31.59 s), and the same row
keyed (31.98/31.90 s). Whether that consistency, or a genuinely quiet run, changes the
verdict is 12-03's checkpoint to decide.

Superseded (D-02, this gate only): the human reviewed all four runs on record --
loads 12.66 and 7.04 (both read at the end of the run, the tool-bug reading; see above)
and 2.74 and 1.54 (read at a genuine start, after the fix) -- an eightfold spread across
the two measurement methods -- and found the same four spoke rows over budget in every
one, at times within a roughly 2 s band across all
four (31.16-33.32 s) that did not track the load figure (Run 3, load 2.74, read
*higher* than Run 1, load 12.66, on three of the four rows; Run 4, load 1.54 -- the
closest of the four to the 1.5 bar -- read 31.46-32.03 s, inside that same band).
D-02's purpose -- that no bound moves on a load-inflated reading -- is met by that
four-run agreement on this sweep, so the human recorded (12-03-SUMMARY.md, Task 2) that
this gate rests on Run 4 as its reference run rather than waiting for a fifth.

Decisive (Run 4): four rows read over `SPUR_BUILD_TIMEOUT` (30 s), all
`spoke_count=40` composed rows, both moduli, hex and keyed bore alike, each stacked
with the tip chamfer at its cap and both recesses:

- `teeth=200 module=1.75 bore_hex=43.35 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both` -- 31.46 s (build 30.59 s, fine STL 0.77 s, STEP 0.87 s)
- `teeth=200 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both` -- 31.53 s (build 30.66 s, fine STL 0.78 s, STEP 0.88 s)
- `teeth=200 module=10 bore_hex=43.35 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both` -- 31.52 s (build 30.58 s, fine STL 0.94 s, STEP 0.88 s)
- `teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both` -- 32.03 s (build 31.06 s, fine STL 0.96 s, STEP 0.88 s) -- the heaviest, D-03's probe target

### Gate probe

No decisive run: no probe (D-02).

Superseding D-02 for this gate (see `### Gate` above), Run 4 is the reference run and
its heaviest row -- `module=10` keyed-bore spokes, `tip_chamfer=3`, 32.03 s -- is
probed for D-03's first offer. A count that fits the heaviest row fits the pattern's
other three over-budget rows (all lighter in Run 4: 31.46-31.53 s at module=1.75,
31.52 s at module=10 hex, against the keyed module=10 row's 32.03 s), so only that one
row is probed, per Task 1's text ("that pattern's worst over-budget composed row").
Holes and honeycomb rows are inside 30 s in every run and are not probed.

Probed per Task 1's step sizes (down by 5, then up by 1) in a one-row scratch sweep
(session scratchpad, not committed), one gear at a time, on the same host. The
1-minute figure was polled every 30 s for the plan's five-minute cap starting at
08:46:12Z, ranged 2.84-6.31 without settling under 2.5, and the probe was launched
once the cap expired, at a 1-minute reading of 2.48 (08:51:15Z) -- the closest the
wait got. Each row's own load reading (`sysctl -n vm.loadavg` immediately before
launch, then the runner's own "Load averages at start" line, taken a few seconds
later) is recorded below; the host's load climbed steadily across the probe (2.40 to
29.51) for reasons outside this session -- other local processes were already running
concurrently on this shared machine (`ps aux` during the probe showed two other AI
agent sessions and a system indexing process at high CPU) -- consistent with this
gate's own load-independence finding: build time did not track the load figure here
either (28.06-30.60 s across a load spread from 2.40 to 29.51, over 12x).

- Machine: 12 CPUs, arm64, 32.0 GiB RAM
- Python: 3.12.13
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `083b312`
- Sweep: one-row scratch sweep (session scratchpad), the composed.json module=10 keyed-bore
  spokes row (`teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4
  spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both`)
  with `spoke_count` varied
- SPUR_BUILD_TIMEOUT: 30 s, a cold request is one build plus one export

| spoke_count | sysctl reading before launch | Load averages at start (runner) | Build (s) | Fine STL (s) | STEP (s) | Build + slower export (s) | Inside 30 s | Fine STL (bytes) | Triangles |
|---|---|---|---|---|---|---|---|---|---|
| 35 | 2.40, 3.73, 4.25 (08:51:24Z) | 2.40, 3.73, 4.25 | 29.66 | 0.95 | 0.87 | 30.60 | **NO** | 8135384 | 162706 |
| 30 | 14.74, 6.83, 5.37 (08:52:02Z) | 14.28, 6.86, 5.39 | 28.06 | 0.88 | 0.81 | 28.95 | yes | 7719384 | 154386 |
| 31 | 29.24, 12.09, 7.40 (08:52:42Z) | 27.22, 11.96, 7.38 | 28.44 | 0.87 | 0.81 | 29.32 | yes | 7803384 | 156066 |
| 32 | 32.00, 16.01, 9.13 (08:53:27Z) | 29.51, 15.76, 9.08 | 28.51 | 0.90 | 0.82 | 29.41 | yes | 7886984 | 157738 |
| 33 | 21.15, 15.14, 9.09 (08:54:04Z) | 19.62, 14.92, 9.05 | 29.21 | 0.90 | 0.83 | 30.11 | **NO** | 7970184 | 159402 |

Offer (D-03 first offer): the largest `spoke_count` measured inside 30 s is **32**
(29.41 s of 30 s) -- the row at 33 reads over budget again (30.11 s). `lower-le:
spoke_count 32`.

### Re-run after the gate (lower-le: spoke_count 32)

12-03's Task 2 checkpoint (4th ask) recorded the human's decision on the probe's offer:
"lower-le: spoke_count 32 (Recommended)". `spoke_count`'s `le` was lowered 40 -> 32 in
`src/spur/params.py` (commit `547214e`), every `spoke_count=40` row in
`bench/sweeps/composed.json` and `bench/sweeps/spoke_cutout.json` moved to 32 (40 is no
longer a valid value), and the whole composed sweep was re-run on this host per Task 3's
own instruction ("re-run the whole composed sweep on a quiet host ... append `### Re-run
after the gate (lower-le)`").

Per the human's D-02 supersession for this gate (`### Gate` above) this re-run does not
chase the 1.5 bar for 30 minutes: the 1-minute figure was polled every 30 s for a 5-minute
cap starting at 09:44:20Z, falling from 4.41 to 1.53 across the window without settling
under 1.5 -- the closest reading, 1.53, came at the cap's own expiry (09:49:27Z) -- and the
sweep was launched immediately once the cap expired, with no further wait. `sysctl -n
vm.loadavg` read 1.65 nine seconds before launch (09:49:31Z); `bench/build_time.py`'s own
`report()` (post-`9b9af43`, a genuine at-start reading) read 1.68 a few seconds further
into Python/CadQuery startup.

- Machine: 12 CPUs, arm64, 32.0 GiB RAM
- Python: 3.12.13
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `547214e`
- Sweep: `bench/sweeps/composed.json`
- Load averages at start: 1.68, 4.07, 4.95
- SPUR_BUILD_TIMEOUT: 30 s, a cold request is one build plus one export

| Parameter set | Build (s) | Fine STL (s) | STEP (s) | Build + slower export (s) | Inside 30 s | Fine STL (bytes) | Triangles |
|---|---|---|---|---|---|---|---|
| teeth=200 module=1.75 bore_hex=43.35 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both | 27.80 | 0.71 | 0.81 | 28.61 | yes | 7125584 | 142510 |
| teeth=200 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both | 28.13 | 0.73 | 0.78 | 28.92 | yes | 7219484 | 144388 |
| teeth=200 module=10 bore_hex=43.35 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 27.96 | 0.91 | 0.79 | 28.87 | yes | 7831184 | 156622 |
| teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 28.51 | 0.91 | 0.80 | 29.42 | yes | 7886984 | 157738 |
| teeth=200 module=1.75 bore_hex=156.3 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both | 16.12 | 0.68 | 0.49 | 16.80 | yes | 11279684 | 225592 |
| teeth=200 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both | 21.72 | 3.20 | 0.64 | 24.91 | yes | 14207884 | 284156 |
| teeth=200 module=10 bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both | 14.48 | 1.25 | 0.52 | 15.72 | yes | 17306084 | 346120 |
| teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both | 14.90 | 1.25 | 0.49 | 16.15 | yes | 16015284 | 320304 |
| teeth=200 module=1.75 bore_hex=200 hex_cell=3 hex_wall=0.4 tip_chamfer=1.75 recess_sides=both | 26.31 | 0.69 | 0.96 | 27.27 | yes | 10723884 | 214476 |
| teeth=200 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hex_cell=3 hex_wall=0.4 tip_chamfer=1.75 recess_sides=both | 23.09 | 0.75 | 0.98 | 24.06 | yes | 6966084 | 139320 |
| teeth=200 module=10 bore_hex=200 hex_cell=3 hex_wall=5 tip_chamfer=3 recess_sides=both | 21.13 | 0.92 | 0.96 | 22.09 | yes | 7859984 | 157198 |
| teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hex_cell=3 hex_wall=5 tip_chamfer=3 recess_sides=both | 21.30 | 0.94 | 0.96 | 22.26 | yes | 8210984 | 164218 |
| teeth=200 module=1.75 bore_hex=200 recess_sides=both bore_chamfer=0.4 | 4.37 | 0.61 | 0.40 | 4.98 | yes | 10224284 | 204484 |
| teeth=200 module=1.75 bore_d=200 bore_flat=150 keyway_width=3 keyway_depth=1.4 recess_sides=both bore_chamfer=0.4 | 4.13 | 0.63 | 0.40 | 4.75 | yes | 10144684 | 202892 |
| teeth=200 module=1.75 tip_chamfer=1.75 recess_sides=both | 14.14 | 0.72 | 0.47 | 14.86 | yes | 8866484 | 177328 |
| teeth=200 module=1.75 hole_count=60 hole_d=1 hole_circle_d=183.4 recess_sides=both | 8.50 | 3.15 | 0.56 | 11.65 | yes | 14447884 | 288956 |
| teeth=200 module=10 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=both | 15.46 | 0.86 | 0.71 | 16.32 | yes | 7791784 | 155834 |
| teeth=200 module=1.75 hex_cell=3 hex_wall=0.4 recess_sides=both | 7.72 | 0.81 | 0.90 | 8.62 | yes | 7206084 | 144120 |

**Heaviest:** teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both -- 29.42 s of 30 s.
**Largest fine STL:** teeth=200 module=10 bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both -- 17306084 bytes, 346120 triangles.

Every row of this re-run reads inside `SPUR_BUILD_TIMEOUT` (30 s). The heaviest row is the
same pattern (module=10, keyed bore, `tip_chamfer=3`) that was over budget at
`spoke_count=40`: 29.42 s of 30 s, 0.58 s of margin -- consistent with the probe's own
reading for `spoke_count=32` on the same row (29.41 s), one build/export apart. No row is
over budget; per Task 3's own instruction this re-run does not trigger a further
checkpoint.

**Note (2026-10-06, L37).** The 0.58 s margin is a single-build reading. Under ten concurrent
builds the same row ended `BuildTimeout` at `duration_ms` 30004 (SC3, Phase 13, "### Composed
worst row under ten concurrent builds (Phase 13)"), and with one worker busy and three requests
queued behind it the slot-holding request for it read `503 timeout` at 30.01 s client wall and
30003 ms server `duration_ms`, at 1-minute load 5.48 to 5.88 on 2026-10-06 and again at 18.94 to
15.30 later that day ("## Same-slot timeout race (Phase 17)", "### Attempt 1" and "### After the
fix"). The limit is documented behaviour (L37); the text above is as it was written.

### Gate decision

The human's verbatim answer to Task 2's checkpoint (4th ask, D-03's first offer): "lower-le:
spoke_count 32 (Recommended)".

Applied: `src/spur/params.py`'s `spoke_count` field lowered from `le` 40 to `le` 32,
committed as `feat(12-03): lower spoke_count le from 40 to 32 (D-03)` (`547214e`), together
with the RED tests (bound test, schema maximum, both sweeps' pinned `want` values -- see
that commit's own message for why RED and GREEN land together: `workflow.tdd_mode` is not
enabled) and the two sweep files' `spoke_count` rows moved from 40 to 32.

Rests on: Run 4 (`### Gate` above, the reference run under D-02's supersession for this
gate) measured the module=10 keyed-bore spokes row at 32.03 s of 30 s at `spoke_count=40`;
this task's probe (`### Gate probe` above) found 32 the largest count still inside budget
(29.41 s), 33 over again (30.11 s); the re-run above confirms the whole composed sweep,
including this same row, now reads inside 30 s at `spoke_count=32` (heaviest 29.42 s).

## Export cost on the heaviest v0.2 topology (Phase 12)

ROADMAP SC4: L19's gzip-level table and L24's mesh-copy cost, re-measured on "the heaviest
v0.2 face topology" -- the composed-sweep row with the largest measured fine STL (D-16),
chosen by that number, not by inspection. Every recorded run of the composed sweep
above (Runs 1-4 and the re-run after the gate) names the same row as its
`**Largest fine STL:**` line: `teeth=200 module=10 bore_hex=200 hole_count=60 hole_d=5.85
hole_circle_d=400 tip_chamfer=3 recess_sides=both` -- 17,306,084 bytes, 346,120 triangles,
about 1.9x the byte size of L19's own v0.1 measurement STL (`teeth=199&quality=fine`,
9,062,784 bytes). The re-measurement runs through `bench/export_cost.py`, committed
behind `make bench.export SWEEP=<json> SET="<label>"` (D-17), and applies L19's selection
rule exactly as written (D-18).

### Quiet-host wait

Per D-02's protocol (12-02/12-03's own gate discipline): `sysctl -n vm.loadavg` polled
about once a minute, waiting for the 1-minute figure to fall below 1.5, for at most 30
minutes. Every reading:

| Time (UTC) | Elapsed | load1 | load5 | load15 |
|---|---|---|---|---|
| 10:30:18Z | 0s | 4.40 | 4.34 | 4.52 |
| 10:31:18Z | 60s | 2.93 | 3.95 | 4.36 |
| 10:32:18Z | 120s | 2.06 | 3.49 | 4.16 |
| 10:33:18Z | 180s | 2.37 | 3.27 | 4.03 |
| 10:34:18Z | 240s | 1.57 | 2.89 | 3.83 |
| 10:35:18Z | 300s | 1.66 | 2.66 | 3.68 |
| 10:36:18Z | 360s | 1.30 | 2.39 | 3.51 |

Quiet reached at 10:36:18Z UTC (load1 1.30, well within the 30-minute budget). The run was
launched immediately after, with one final pre-launch check reading 1.35 at 10:36:24Z UTC
and `make bench.export` itself starting at 10:36:31Z UTC (pre-launch `sysctl` read 1.33 at
that instant). `bench/export_cost.py`'s own `main()` reads `os.getloadavg()` before any
building starts, the same discipline `bench/build_time.py`'s `report()` adopted after
12-03 -- its reading below (1.38) is the genuine at-start figure and the one D-02's <1.5
bar is judged against: **decisive**.

### `make bench.export` output, verbatim

```
- Machine: 12 CPUs, arm64, 32.0 GiB RAM
- Python: 3.12.13
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `64528fb`
- Set: teeth=200 module=10 bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both
- Load averages at start: 1.38, 2.35, 3.47

- Fine STL: 17306084 bytes, 346120 triangles

### gzip level (L19)
| Level | Single-threaded median (ms) | Output bytes (% of input) | 10-concurrent wall, median of 3 (ms) |
|---|---|---|---|
| 1 | 95.3 | 5170722 (29.9%) | 118.2 |
| 6 | 274.2 | 4785216 (27.7%) | 324.3 |
| 9 | 1352.1 | 4786073 (27.7%) | 1587.3 |

**L19 selects:** level 1 -- level 6: 7.46% smaller (bar 10%), 2.74x wall (bar 1.5x) -- not adopted; level 9: 7.44% smaller (bar 10%), 13.43x wall (bar 1.5x) -- not adopted

### Mesh copy (L24)
3 child processes per mode, alternating copy and in-place, one fresh process per run so peak RSS is that run's own reading, never a cumulative maximum carried over from an earlier one.
| Run | Mode | Export (ms) | Peak RSS (MiB) | Triangles |
|---|---|---|---|---|
| 1 | copy | 1244.3 | 1856.5 | 346120 |
| 1 | in-place | 1181.0 | 1890.8 | 346120 |
| 2 | copy | 1239.0 | 1770.2 | 346120 |
| 2 | in-place | 1160.8 | 1896.7 | 346120 |
| 3 | copy | 1178.2 | 1897.8 | 346120 |
| 3 | in-place | 1161.0 | 1905.2 | 346120 |

**Copy cost:** +52.9 ms mean export, -56.0 MiB mean peak RSS over in place (mean of 3 each).
```

Exit code: 0 (every run's triangle count agrees -- copy and in-place produced the same
triangle *count*; this does not by itself prove identical mesh content down to vertex
positions or winding, which this script does not check).

### Against the v0.1 numbers

**Gzip (L19):** the rule reads the same verdict on this 1.9x-larger input as it did on
L19's own STL -- level 1 wins both comparisons. Level 6 over level 1 is 7.46% smaller here
against 8.7% on L19's STL; level 9 over level 1 is 7.44% smaller here against 8.66% there
-- both still short of the 10% bar, and both wall ratios (2.74x and 13.43x here, against
2.67x and 12.4x there) stay in the same range. `_GZIP_LEVEL` is unchanged; `src/spur/app.py`
carries the new table as a dated addition above the existing one (D-18: "if not, L19 is
annotated with the new row"; 12-01-SUMMARY.md's binding answer: "comment + L31" -- the
comment is this addition, L31 is 12-09's).

**Mesh copy (L24):** L24's own reading, a 200-tooth fine export (9,086,484-byte STL, a
busy host, mean of 3): +1.4 to +17.6 ms per export, +3.2 to +7.7 MiB peak RSS. This
run's reading, on the 346,120-triangle heaviest-topology STL, a quiet host: +52.9 ms mean
export (outside L24's range -- consistent with a larger mesh costing proportionally more
to copy) and -56.0 MiB mean peak RSS (outside L24's range on the other side -- each
process here peaks around 1.8-1.9 GiB, so a few-MiB copy/in-place difference is well
inside ordinary allocator noise at that scale, and this run's noise happened to land
negative). Recorded exactly as measured (L08), not adjusted toward L24's range. Per D-18,
L24's cost is recorded only -- the copy in `model._write_export` is a correctness decision
(a cached solid never carries a mesh, L24), not a cost trade, and stays regardless of this
reading.

## Composition pass test cost (Phase 12, D-10)

D-10: the phase's added `make verify` cost measured as 07 D-06 measured it -- the
phase-start code (`c9a169d`, the commit the branch was cut from) and the phase-end code,
same host, same session, alternating A1 B1 A2 B2 full `make verify` runs with the load
read before each; the delta is `mean(B) - mean(A)` wall seconds, against the pre-agreed
30.0 s line.

### Host state

- CPU: Apple M2 Max, 12 cores
- RAM: 32.0 GiB
- Python: 3.12.13 (`.venv`)
- Date: 2026-09-30
- Phase-start HEAD (worktree A, detached): `c9a169d`
- Phase-end HEAD (main checkout, B): `480da30`
- The A runs borrow the main `.venv` via `PYTHONPATH="$WT/src"` and `make -o
  "$MAIN/.venv/.installed"`, proven before timing: `PYTHONPATH="$WT/src"
  "$MAIN/.venv/bin/python" -c "import spur, pathlib; print(pathlib.Path(spur.__file__).resolve())"`
  printed a path under the worktree; `_editable_impl_spur.pth`'s content
  (`/Users/halfb00t/git/halfb00t/spur/src`) was identical before and after all four runs --
  the main venv's editable install was never repointed at the worktree.
- Load averages (1-minute, `sysctl -n vm.loadavg`), read immediately before each run
  started building: A1 2.87, B1 8.07, A2 8.51, B2 9.07 -- the host carried background load
  from this same session's earlier `make verify` runs throughout; no quiet bar is required
  for this measurement (the alternation is what makes the delta fair, not an absolute
  quiet reading, per D-10's own instruction).

### Same-session, alternating runs

| Run | Code | Load | pytest | Wall (s) |
|---|---|---|---|---|
| A1 | `c9a169d` | 2.87 | 621 passed in 183.67s | 193.30 |
| B1 | `480da30` | 8.07 | 907 passed in 216.90s | 217.90 |
| A2 | `c9a169d` | 8.51 | 621 passed in 184.89s | 185.88 |
| B2 | `480da30` | 9.07 | 907 passed in 216.73s | 217.83 |

mean(A) = 189.59s, mean(B) = 217.87s -> **delta = 28.28s**, against D-10's 30.0s line (1.72s
of margin).

For context, not the gate's own number: 12-06-SUMMARY.md's 15 new tier-2 kernel rows
(the tip chamfer with each cutout on each bore, and the single-sided-recess pairing) were
measured on their own at **30.66-30.73s** of pytest time across two runs, before 12-07/12-08's
own new tests were added on top -- close to D-10's phase-wide 30 s advisory share by
themselves, and the largest single contributor to the phase's +28.28s wall delta above.

### make verify wall time

B2 (this session, load 9.07/8.82/7.30 at start, HEAD `480da30`): **907 passed in 216.73s**
-- **217.83s** wall time (`/usr/bin/time -p`, includes lint/typecheck/import-lint/
no-fake-done), against Phase 11's recorded **621 passed** / **178.55s** wall
(`bench/RESULTS.md`'s "Body cutout" section, load 3.07/4.04/4.65 at start). The phase's own
composition tests (286 new items across 12-02 through 12-08) add the measured **28.28s**
delta above to the gate.

### Regression fixture share

Final pass (D-20), this session, before either A/B run: `git diff --exit-code c9a169d --
tests/regression/pre_v0_2.json` -- clean (byte-unchanged since `c9a169d`, unmodified
through the whole phase). `make test PYTEST_ARGS="tests/regression -q"`: **86 passed in
19.24s** -- the fixture's own share of the phase-end gate, essentially unchanged from
07-01's original 85-case / 16.27s reading (one case added since Phase 7's own count; the
fixture itself was never regenerated).

### Gate decision

The human's verbatim answer to Task 2's checkpoint: "accept (Recommended)". The measured
**28.28s** delta against D-10's 30.0s line stands as recorded above; no tier-2 row is
trimmed; `tests/test_model.py` is untouched.

## The gate, measured and pinned (Phase 15)

What this section measures: `make verify`'s wall time per stage and per test file, the
`pytest-xdist` sweep, then (later subsections, added by 15-02 to 15-05) the coverage floor,
the bar and the CI kernel pin. The method is D-04's, which is Phase 12's D-10 method
without a quiet bar: full `make verify` runs in one session, the 1-minute load read
immediately before each, no waiting for a quiet host, and every delta is
`mean(B) - mean(A)` of alternating runs; a single-sided profile is two runs with their
loads recorded and per-file seconds read as shares. The bar itself is not set here: the
human sets it at 15-03's checkpoint from these rows (D-01).

### Host state

- CPU: Apple M2 Max (`sysctl -n machdep.cpu.brand_string`); `bench.machine_facts()`:
  12 CPUs, arm64, 32.0 GiB RAM
- Python: 3.12.13 (`.venv`); pytest: 9.1.1
- Date: 2026-10-03
- Phase-start HEAD: `20cd484`. HEAD measured by P1 and P2: `862a807` (three `docs(15)`
  commits on top of `20cd484`; `git diff --quiet 20cd484 -- src tests Makefile
  pyproject.toml requirements.txt bench .github` exits 0, so the code and the gate under
  test are the phase-start ones)
- SPUR_* environment: none set (`env | grep '^SPUR_'` empty) -- defaults apply
- Load (1-minute, `sysctl -n vm.loadavg`), read immediately before each run: P1 6.53,
  P2 9.09. The host carried background load throughout (this session's own Claude Code
  process, OrbStack, a browser and other desktop apps were open; a reading of 8.46 was
  taken half a minute before P1). Per D-04 no quiet bar was waited for; each row carries its load.
- Peak RSS: the sum of per-process RSS over the `make` process tree (the `/usr/bin/time`
  process, `make`, `pytest` and every child), sampled once a second. It is an upper bound
  of real memory: file-backed pages of the shared OpenCascade/VTK libraries count once per
  process (RESEARCH A2). `/usr/bin/time -l` would report only the waited-for child's
  `ru_maxrss`, not the tree.

### Method

Every Phase 15 row uses this run recipe and nothing else. The raw `.out`, `.time` and
`.rss` files of each run are session scratch, not committed; the numbers below are read
from them.

- R1: before each run, `pgrep -fl '[p]ytest|[p]re_commit|[m]ake verify'` prints nothing --
  no other gate, test run or commit hook of this session is alive. (The bracketed first
  letters are `pytest|pre_commit|make verify` spelt so the pattern does not match the shell
  command line that holds it.)
- R2: read `sysctl -n vm.loadavg` and keep the 1-minute figure.
- R3: in ONE Bash call with timeout 600000 ms, start
  `/usr/bin/time -p make verify PYTEST_ARGS="<args>"` in the background with stdout to
  `<scratch>/<label>.out` and stderr to `<scratch>/<label>.time`, keep its PID, and while
  `kill -0` on that PID succeeds append one sampler line (root = that PID) to
  `<scratch>/<label>.rss` and sleep 1; then `wait` on the PID and keep its exit status:

  ```bash
  /usr/bin/time -p make verify PYTEST_ARGS="$ARGS" > "$S/$L.out" 2> "$S/$L.time" &
  PID=$!
  : > "$S/$L.rss"
  while kill -0 $PID 2>/dev/null; do
    ps -axo pid=,ppid=,rss= | awk -v root=$PID '{p[$1]=$2; r[$1]=$3; ids[NR]=$1}
      END{keep[root]=1; c=1; while(c){c=0; for(i in ids){id=ids[i]; if(!(id in keep)&&(p[id] in keep)){keep[id]=1;c=1}}}
          t=0;n=0; for(id in keep){t+=r[id];n++} print t, n}' >> "$S/$L.rss"
    sleep 1
  done
  wait $PID
  ```

  The awk prints the summed RSS in KiB and the process count over the root PID and all its
  descendants.
- R4: read the exit status, `real` from the `.time` file (wall seconds), pytest's final
  summary line from the `.out` file (count and seconds), and the largest summed RSS in the
  `.rss` file divided by 1024 (MiB, no decimals) with that sample's process count
  (`sort -n -k1 "$S/$L.rss" | tail -1`); on `--cov` runs also the TOTAL row.
- R5: one table row per run, in the order run. A red run (non-zero exit, a summary other
  than `927 passed`, any failed, error or rerun) is recorded red with its failing node ids
  and is never re-run to replace it.

Per-stage method. Make reports no per-recipe time, so after each full run the four quick
stages are timed as separate warm invocations, `/usr/bin/time -p make lint`,
`make typecheck`, `make lint-imports` and `make no-fake-done`, keeping each `real`; pytest's
stage is the run's wall minus those four, with pytest's own reported seconds beside it.

Per-file method. A run with `--durations=0 --durations-min=0` prints one line per
setup, call and teardown phase, `<seconds>s <phase> <nodeid>`; the per-file seconds are
those lines grouped by the node id's path before its first `::` (the regression ids
contain further `test_x.py::` text and stay with their own file):

```bash
grep -E '^[0-9.]+s (call|setup|teardown) ' "$S/$L.out" \
  | awk '{split($3,a,"::"); t[a[1]]+=$1; n[a[1]]++} END{for(f in t) printf "%8.2fs %5d %s\n", t[f], n[f], f}' \
  | sort -rn
```

The item counts come from `.venv/bin/python -m pytest --collect-only -q` (one line per
item, grouped the same way); the awk's own count is three phases per item.

Precision. Wall seconds are `/usr/bin/time -p`'s two-decimal `real`; loads are sysctl's
two-decimal figures; pytest prints each phase to two decimals, so a per-file figure is a
sum of rounded values (a phase under 0.005 s reads 0.00). Means and shares are computed
from the recorded values and rounded only when written.

Where the numbers stand (RESEARCH Open Question 3, decided here): the per-file and RSS
readings stand on these committed commands plus the `make verify` target, and no
`bench/` script is added -- a script would need its own tests under `mypy --strict` for
two lines of awk (12 D-17 asks that every number be reproducible from committed material,
which committed prose plus a make target is).

### Per-stage wall time

Two serial profile runs, each `make verify PYTEST_ARGS="--durations=0 --durations-min=0"`,
P1 then P2, in the order run:

| Run | HEAD | Load | pytest | Wall (s) | Peak RSS (MiB, procs) | Exit |
|---|---|---|---|---|---|---|
| P1 | `862a807` | 6.53 | 927 passed in 229.15s | 230.20 | 1396 (6) | 0 |
| P2 | `862a807` | 9.09 | 927 passed in 217.59s | 218.36 | 1390 (5) | 0 |

| Stage | P1 (s) | P2 (s) |
|---|---|---|
| ruff (`make lint`) | 0.07 | 0.03 |
| mypy (`make typecheck`) | 0.37 | 0.20 |
| import-linter (`make lint-imports`) | 0.11 | 0.09 |
| unfinished-work scan (`make no-fake-done`) | 0.02 | 0.01 |
| pytest (wall minus the four; pytest's own seconds in brackets) | 229.63 (229.15) | 218.03 (217.59) |
| whole gate (`/usr/bin/time -p make verify`) | 230.20 | 218.36 |

The four quick stages were timed as separate warm invocations right after each full run,
which is what they cost inside the gate. Pytest is 99.75 % of the gate in P1 and 99.85 % in
P2: nothing outside the test suite is worth cutting on this host. The two runs differ by
11.84 s (mean wall 224.28 s) with the heavier load on P2, so a single-sided pair says only
that the gate is about 3.6-3.8 minutes serial here. The serial run is already multi-core:
`/usr/bin/time -p` read user 350.77 s + sys 616.20 s over 230.20 s real in P1 (4.2 cores
on average) and 343.14 s + 629.40 s over 218.36 s in P2 (4.5), which is why the xdist gain
below is expected to be sublinear (RESEARCH Pitfall 9).

### Per-file share

Item counts from `--collect-only`; seconds are the per-file sums of the duration lines
(P1 sums to 226.41 s, P2 to 214.79 s of the 229.15 s and 217.59 s pytest reported -- the
difference is collection and session start, which sit outside the duration lines, plus
rounding); the share is each file's seconds over the sum of that run's per-file seconds
(P1 % / P2 %). Sorted by P1 seconds descending, ties by path ascending.

| File | Items | P1 (s) | P2 (s) | Share of pytest (%) |
|---|---|---|---|---|
| tests/test_model.py | 201 | 167.76 | 157.53 | 74.1 / 73.3 |
| tests/test_pool.py | 16 | 19.29 | 17.92 | 8.5 / 8.3 |
| tests/regression/test_pre_v0_2.py | 85 | 17.58 | 17.01 | 7.8 / 7.9 |
| tests/test_api.py | 54 | 10.92 | 11.23 | 4.8 / 5.2 |
| tests/test_cli.py | 44 | 9.75 | 10.04 | 4.3 / 4.7 |
| tests/test_records.py | 13 | 0.46 | 0.44 | 0.2 / 0.2 |
| tests/test_bench.py | 24 | 0.42 | 0.43 | 0.2 / 0.2 |
| tests/test_skip_tokens.py | 27 | 0.17 | 0.13 | 0.1 / 0.1 |
| tests/test_calc.py | 404 | 0.06 | 0.06 | 0.0 / 0.0 |
| tests/regression/test_corpus.py | 1 | 0.00 | 0.00 | 0.0 / 0.0 |
| tests/test_pr_land.py | 58 | 0.00 | 0.00 | 0.0 / 0.0 |
| total | 927 | 226.41 | 214.79 | 100.0 / 100.0 |

`tests/test_model.py` is three quarters of pytest's time in both runs; the next three
files (pool, regression fixture, api) together are about a fifth. The 1212 phases of
`tests/test_calc.py` print 0.06 s in total (its slowest is 0.03 s), and every printed phase
of `tests/test_pr_land.py` and `tests/regression/test_corpus.py` reads 0.00 s, so those
shares are below what two-decimal printing can resolve; they are rows of the table, not of
the cost.

### Slowest 25

P1's own `--durations` output, the first 25 duration lines, verbatim in pytest's order:

```
7.03s call     tests/test_cli.py::test_readme_export_examples_run
5.22s call     tests/test_pool.py::test_four_same_slot_requests_all_refuse_without_cancellation
4.62s call     tests/test_pool.py::test_a_wedged_build_is_terminated_and_its_worker_replaced
4.43s call     tests/test_pool.py::test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced
3.25s call     tests/test_model.py::test_each_edge_selector_picks_exactly_its_own_edges[module-0.2]
2.96s call     tests/test_model.py::test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore[keyed-holes]
2.85s call     tests/test_model.py::test_the_same_cutout_link_builds_the_same_solid_twice[spokes-filleted]
2.77s call     tests/test_model.py::test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore[round-holes]
2.76s call     tests/test_model.py::test_every_selector_takes_only_its_own_edges_with_a_body_cutout[teeth-200-holes]
2.67s call     tests/test_model.py::test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore[hex-holes]
2.57s call     tests/test_model.py::test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore[keyed-spokes]
2.50s call     tests/test_model.py::test_the_same_cutout_link_builds_the_same_solid_twice[cells]
2.50s call     tests/test_model.py::test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore[d-flat-holes]
2.49s call     tests/test_pool.py::test_two_same_slot_deaths_from_one_incident_replace_the_worker_once
2.48s call     tests/test_model.py::test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore[round-spokes]
2.38s call     tests/test_model.py::test_each_edge_selector_picks_exactly_its_own_edges[teeth-200]
2.23s call     tests/test_model.py::test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore[hex-spokes]
2.23s call     tests/test_pool.py::test_a_real_worker_builds_and_downloads
2.18s call     tests/test_model.py::test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore[hex-cells]
2.18s call     tests/test_model.py::test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore[d-flat-spokes]
2.16s call     tests/test_model.py::test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore[d-flat-cells]
2.15s call     tests/test_cli.py::test_an_unknown_output_extension_exits_1_from_the_real_process
2.14s call     tests/test_model.py::test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore[round-cells]
2.08s call     tests/test_model.py::test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore[keyed-cells]
1.93s call     tests/test_model.py::test_the_recess_floor_fillet_survives_every_cutout_on_every_bore[hex-cells]
```

`tests/test_model.py` holds 18 of the 25 (the twelve tip-chamfer-with-each-cutout-on-each-bore
rows alone take 28.9 s of P1's call time), `tests/test_pool.py` 5 and `tests/test_cli.py` 2.

### xdist sweep

`pytest-xdist` 3.8.0 and `pytest-cov` 7.1.0 were added to the `[dev]` extras and installed
into `.venv` only after the human confirmed both are the pytest-dev packages (`approved`);
neither is in `requirements.txt` or `[project] dependencies`, and `addopts` is unchanged.
No `--cov` is on in this sweep (the floor is 15-02's).

Knee rule, fixed before any sweep number was read (D-06): the apparent knee is the
smallest N among the green sweep rows whose wall is at most 1.10 times the fastest green
sweep wall (a row at exactly 1.10 times qualifies); two green rows with equal wall go to
the smaller N. A red row is recorded red with its failing node ids, never re-run, and is
left out of the rule.

Each row is `make verify PYTEST_ARGS="-n N"` per the run recipe above, in the order run
(P1 and P2 repeat as the serial reference). HEAD is `39eb062` for S2-S12: the Task 1
commit, with only the `pyproject.toml` dev-extras edit uncommitted on top. Each load is
the 1-minute figure read immediately before that run, so for S4-S12 it still carries the
previous sweep row's own work; no quiet bar was waited for (D-04), and nothing else of
this session ran on the host between rows.

| Run | N | HEAD | Load | pytest | Wall (s) | Peak RSS (MiB, procs) | Exit |
|---|---|---|---|---|---|---|---|
| P1 | serial | `862a807` | 6.53 | 927 passed in 229.15s | 230.20 | 1396 (6) | 0 |
| P2 | serial | `862a807` | 9.09 | 927 passed in 217.59s | 218.36 | 1390 (5) | 0 |
| S2 | 2 | `39eb062` | 2.29 | 927 passed in 128.45s | 130.72 | 2226 (8) | 0 |
| S4 | 4 | `39eb062` | 9.33 | 927 passed in 84.02s | 84.76 | 3969 (11) | 0 |
| S8 | 8 | `39eb062` | 17.07 | 927 passed in 67.95s | 68.93 | 5649 (17) | 0 |
| S12 | 12 | `39eb062` | 28.01 | 927 passed in 74.21s | 75.47 | 7880 (22) | 0 |

All four sweep rows are green: exit 0, `927 passed`, no failed, error or rerun in any
`.out`. No shared-state site (`tests/test_pool.py`, `tests/test_api.py`,
`tests/test_records.py`) failed at any N, so there is nothing for 15-02's `xdist_group`
response to inherit from this sweep.

Apparent knee: N = 8 (68.93 s against the fastest 68.93 s at N = 8)

The rule's ceiling is 1.10 x 68.93 = 75.82 s: S4 (84.76 s) is above it, S8 qualifies, S12
(75.47 s, 1.095 x) is also under it but is the larger N. S12 is slower than S8 by 6.54 s on
a 12-CPU host; a likely cause is oversubscription (12 workers plus the controller on 12
CPUs), but this sweep did not test that.

Peak RSS grows with N and is an upper bound (shared-library pages count once per process):
1396 and 1390 MiB serial, then 2226, 3969, 5649 and 7880 MiB at N = 2, 4, 8, 12, so the
sweep at N = 12 holds about 5.7 times the serial peak for 3.0 times the speed.

Pitfall 9 shows in the speed-ups against the serial mean of 224.28 s: 1.72 x at N = 2, 2.65 x
at N = 4, 3.25 x at N = 8 and 2.97 x at N = 12, far from linear because the serial gate
already spends 4.2-4.5 cores on average (user + sys / real). By the same reading user time
stays near 340 s at every N (S2 344.23, S4 334.38, S8 338.57, S12 337.21) while sys time
falls from 507.65 s at N = 2 to 106.30 s at N = 12 (serial: 616.20 s in P1, 629.40 s in P2).

No N is chosen here: the human picks it at 15-03 from these rows (D-06).

### Coverage baseline

One serial run with coverage on, per the run recipe above (REQ-coverage-floor's "one
baseline `pytest --cov` run"). HEAD is `f771c5e`, the commit that added the coverage config
(`concurrency = ["multiprocessing", "thread"]`, `parallel`, `sigterm`, `precision = 2`) and
the `.gitignore` entries; the Makefile `test` recipe has no `--cov` yet, so `--cov` rides in
`PYTEST_ARGS` for every row here. Args: `--cov --cov-report=term-missing`, no `-n`.

| Run | Args | Load | pytest | Wall (s) | Peak RSS (MiB, procs) | Exit | Coverage |
|---|---|---|---|---|---|---|---|
| C0 | `--cov --cov-report=term-missing` | 8.37 | 927 passed in 243.54s (0:04:03) | 244.59 | 1407 (5) | 0 | 96.99% |

The rows of C0's report that matter, verbatim:

```
Name                       Stmts   Miss Branch BrPart   Cover   Missing
src/spur/pool.py              54      3      6      0  95.00%   63-67, 222
TOTAL                       1069     26    294     15  96.99%
```

Worker lines are counted. `BuildPool`'s workers are spawned processes (`pool.py:35`) and
`pytest-cov` 7 has no subprocess hook of its own, so coverage's own multiprocessing support
does the counting: `concurrency = ["multiprocessing", "thread"]` (the thread entry keeps the
lifespan thread that builds and shuts down the pool traced, which the key's replacement of
coverage's default would otherwise drop), `parallel = true` writes one data file per
process for `pytest-cov` to combine, and `sigterm = true` saves the data of a worker
`pool.py` terminates. The proof is `tests/test_pool.py` alone, run with `--cov`, which reads
`src/spur/pool.py 54 0 6 0 100.00%` both serially and at `-n 2` (16 passed each): the
statements of `_warm` and `build_export`, which run only inside a spawned worker, read
covered. Today's config without those keys reads 95 % there with `build_export`'s body
missing (15-RESEARCH Pitfall 1).

C0's own pool.py row is not 100 %. Lines 63-67 (the body of `build_export`, the worker's
side) and 222 (`return await self._run_with_timeout(...)` in `export()`) read missing on
this full serial run: three statements, 0.22 points, which is exactly the difference
between C0's 96.99 % (26 missed) and the 97.21 % (23 missed) every `--cov` run at `-n 8`
below reads. This is 15-RESEARCH Pitfall 13 (a lost worker flush, cause unproven) occurring
once in four full `--cov` runs here and, unlike the sightings in that note, on a serial run
(the first of the four, the only serial one), so it is not specific to xdist. It is a
reading, not a retry: C0 stays as measured (R5), is the lowest green total of the set, and
sets L in the floor below.

One point of this total is (statements + branches) / 100 units: 1,069 statements and 294
branches are 1,363 units, so one point is 13.63 units and one missed statement is 0.073
points (C0 missed 26 statements and had 15 partially covered branches).

### Tolerance and coverage cost

D-05's three tolerance runs at the apparent knee K = 8 (the sweep above) and D-12's cost
runs are the same six runs: A is `-n 8` without coverage and B is `-n 8 --cov`, alternating
A1 B1 A2 B2 A3 B3. The order was fixed before the first of them ran, after C0, with no
`--dist` option (D-08's `loadgroup` only if a shared-state module failed). HEAD `f771c5e`
for every row; each load is the 1-minute figure read immediately before the run and, the
rows running back to back, still carries the previous row's own work (D-04: recorded as
read, no quiet bar). Nothing else of this session ran on the host between rows.

| Run | Args | Load | pytest | Wall (s) | Peak RSS (MiB, procs) | Exit | Coverage |
|---|---|---|---|---|---|---|---|
| A1 | `-n 8` | 7.94 | 927 passed in 60.86s (0:01:00) | 61.60 | 6829 (17) | 0 | none |
| B1 | `-n 8 --cov` | 22.37 | 927 passed in 63.23s (0:01:03) | 64.03 | 6596 (16) | 0 | 97.21% |
| A2 | `-n 8` | 23.15 | 927 passed in 59.14s | 59.88 | 6968 (18) | 0 | none |
| B2 | `-n 8 --cov` | 28.31 | 927 passed in 65.03s (0:01:05) | 65.83 | 6614 (15) | 0 | 97.21% |
| A3 | `-n 8` | 28.25 | 927 passed in 59.61s | 60.35 | 6911 (17) | 0 | none |
| B3 | `-n 8 --cov` | 30.02 | 927 passed in 61.94s (0:01:01) | 62.50 | 6673 (16) | 0 | 97.21% |

All six rows read `927 passed`, exit 0, no failed, error or rerun in any output, so no
shared-state module (`tests/test_pool.py`, `tests/test_api.py`, `tests/test_records.py`)
failed and D-08's `xdist_group` response did not fire.

mean(A) = 60.61 s, mean(B) = 64.12 s -> coverage cost = 3.51 s at -n 8 (5.8 % of mean(A))

D-05 tolerance at N = 8: adopted -- 6 of 6 green, 927 passed each

Largest peak RSS of the set: 6968 MiB (A2, 18 processes), an upper bound by the same rule
as the sweep (shared-library pages count once per process); the B rows peak at 6596-6673
MiB, no higher than the A rows.

The three B totals are 97.21 %, 97.21 % and 97.21 %, the same 23 missed statements and 15
partial branches each, so their spread is 0.00 points: the combined total did not depend on
the order in which the eight workers' and the pool workers' data files were written, at
this resolution (D-10's determinism reading). The one thing this set does not show is
Pitfall 13's lost flush, which cost C0 0.22 points: three xdist runs of three did not lose
it, one serial run did, so the B spread understates the real one and L below takes C0.

### Coverage floor

D-10's rule: a whole percent under the baseline, one more point when that leaves under
0.25 points of slack, wider when the spread of the totals needs it. Written against the
lowest observed total: L is the lowest of C0 and every green tolerance total (96.99, 97.21,
97.21, 97.21), S is the spread of the green tolerance totals (max - min over all of them),
and the floor is the whole percent under L - max(0.25, S).

Floor: L = 96.99, S = 0.00, slack = max(0.25, S) = 0.25 -> fail_under = 96

L - slack = 96.74, whose whole percent below is 96. With `precision = 2` the total is
compared as printed: a total of exactly 96.00 passes and 95.99 fails
(`coverage.results.should_fail_under(96, 96, 2)` is False, `(95.99, 96, 2)` is True), so
the gate trips 0.99 points (about 13.5 units) under C0 and 1.21 points under the xdist
totals; a lost worker flush (0.22 points) cannot trip it by itself. The literal lives in
`pyproject.toml` `[tool.coverage.report]` alone: `make test` passes no `--cov-fail-under`,
and `pytest-cov` copies the config value when the flag is absent.

### Red on the floor

D-12's proof that the floor gates: with `fail_under = 96` in `pyproject.toml` and `--cov` in
`make test` applied to the working tree but not yet committed, one test file is left out of
a full run by `--ignore`. Attempt 1 of at most two went red on the floor, so no second file
was tried.

- File left out: `tests/test_cli.py` (44 of the 927 tests)
- Command: `make verify PYTEST_ARGS="-n 8 --ignore=tests/test_cli.py"` per the run recipe,
  so pytest ran `pytest --cov --cov-report=term -n 8 --ignore=tests/test_cli.py`; HEAD
  `6599677` plus the uncommitted `pyproject.toml` and `Makefile` edits; load 5.57
- pytest line: `883 passed in 59.03s`; wall 59.59 s; peak RSS 7021 MiB (17 processes)
- Total read: 90.24 % (`TOTAL 1069 105 294 14 90.24%`); floor: 96
- Exit: pytest 1, `make` 2 (`make: *** [Makefile:78: test] Error 1`)
- Failure lines, verbatim:

  ```
  ERROR: Coverage failure: total of 90.24 is less than fail-under=96.00
  FAIL Required test coverage of 96.0% not reached. Total coverage: 90.24%
  ```

The total sits 5.76 points under the floor, so losing one test file is far outside the
slack the floor was given (0.99 points under C0). `--ignore` left every file in the tree
as it was (`git diff --quiet HEAD -- tests` exits 0); scratch run, not committed (D-12).

Checking the partial-run edge found that the first Makefile recipe, `pytest --cov
$(PYTEST_ARGS)`, ran the whole suite when `PYTEST_ARGS` began with a path:
`--cov` takes an optional value, so `--cov tests/test_calc.py` read the path as the coverage
source and ran 927 tests, the documented `--no-cov` hatch included. The recipe is
`pytest --cov --cov-report=term $(PYTEST_ARGS)`: the option after `--cov` stops it from
taking the path, `make test PYTEST_ARGS="tests/test_calc.py -q"` then runs 404 tests, reads
45.93 % and fails the floor, and the same with `--no-cov` exits 0 (404 passed in 0.25 s).

### Heaviest contributors

Selection rule, fixed before any per-test second was read: every file whose mean share of
pytest's seconds over P1 and P2 (### Per-file share) is at least 5 %. Four files qualify,
together 95.0 % of pytest's seconds. `tests/test_api.py` is just over the line (4.8 % in P1,
5.2 % in P2, 5.03 % unrounded). `tests/test_cli.py` is under it (4.3 % / 4.7 %, mean
4.5 %), so the rule leaves out its two slow tests (`test_readme_export_examples_run`,
7.03 s, the slowest single test in P1, and
`test_an_unknown_output_extension_exits_1_from_the_real_process`, 2.15 s) and no cut is
proposed for them.

| File | Items | Serial s (P1, P2) | Share (%) | What it proves |
|---|---|---|---|---|
| tests/test_model.py | 201 | 167.76, 157.53 | 73.7 (74.1 / 73.3) | The kernel-level geometry proofs, on real solids: every feature builds one valid solid and its edge selector takes exactly its own edges and never none (L26: rim chamfer, recess-floor fillet, tip arcs; L27 hex bore; L28 keyway; L29 tip chamfer; L30 body cutouts), the features compose on one gear (L31, tier 2: tip chamfer with each cutout on each bore), the spoke fillet against its closed form (L33), and a cached solid never carries a mesh (L24) |
| tests/test_pool.py | 16 | 19.29, 17.92 | 8.4 (8.5 / 8.3) | The one place a build really crosses a process boundary: a real worker builds and downloads, a wedged build is killed and its worker replaced, a dying worker surfaces as `BrokenProcessPool` and is replaced, same-slot requests queued behind a timeout refuse without cancellation and replace the worker once (L17, L18) |
| tests/regression/test_pre_v0_2.py | 85 | 17.58, 17.01 | 7.8 (7.8 / 7.9) | The pre-v0.2 part is unchanged: every pre-v0.2 parameter set derives the same dimensions (44 records, exact) and builds the same solid (39 records: faces, edges, volume at rel 1e-6, six bounding-box corners at abs 1e-6), and the fixture was captured on the kernel pair this run uses (L05, L26; Success Metric 3 of v0.2, "old links unchanged") |
| tests/test_api.py | 54 | 10.92, 11.23 | 5.0 (4.8 / 5.2) | The HTTP layer end to end on an in-process build: schema, info and download for each feature's link with the numbers it prints, the refusal and cap-and-warn contracts, the byte cache and its log events (L02, L03, L07, L19, L20, L24, L29, L30) |

### Proposed cuts

Pricing source: the per-test duration lines of P1 and P2 themselves, that is
`make verify PYTEST_ARGS="--durations=0 --durations-min=0"` serial and without coverage (the
profile's own kind), loads 6.53 and 9.09 (`sysctl -n vm.loadavg`, ### Host state), HEAD
`862a807`; `src/`, `tests/` and `requirements.txt` there are byte-identical to the current
HEAD `4b798ac` (`git diff --quiet 862a807 4b798ac -- src tests requirements.txt` exits 0).
Those two runs already printed every test phase, so no separate pricing run was made. The raw
`.out` files are session scratch (as ### Method says); a reader reproduces the figures by
re-running P1 and P2 and aggregating per test function, parametrize id stripped, setup, call
and teardown summed:

```bash
grep -E '^[0-9.]+s (call|setup|teardown) ' "$S/$L.out" \
  | awk '{n=$3; sub(/\[.*$/,"",n); t[n]+=$1} END{for(k in t) printf "%8.2f %s\n", t[k], k}' \
  | sort -rn
```

The Serial s column is the mean of P1 and P2 with the pair in brackets. These are serial
seconds of the named tests. They say nothing about what removing them saves at `-n 8`: that
is not measured here (L08), and a saving at N depends on how the workers are balanced.
Candidate selection, fixed before the numbers were read: for each file in the Heaviest
contributors table, the test functions that together make up at least half of that file's
seconds, taken heaviest first (five in `tests/test_model.py`, two in
`tests/test_pool.py`, the one build function in the regression file, seven in
`tests/test_api.py`), plus every dedup pair found among them. For a matrix group the cut
named is a sample of rows (the rows left out are named; the rest keep running). No row
proposes a tier the hook skips and CI runs (D-03, L13), and no row is a `mark`: the only
marker that would save hook seconds the gate then does not spend is that rejected tier.

| Candidate | Kind | Tests | Serial s | What it proves | Proof-value cost of losing it | Needs acceptance |
|---|---|---|---|---|---|---|
| `tier2-round-bore` | sample | tests/test_model.py::test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore, rows `round-holes`, `round-spokes`, `round-cells` (3 of 12; group 27.61 s) | 6.96 (7.39 / 6.53) | The tip chamfer (1.75 mm) composed with each cutout on a round bore, the tip-arc and cutout-delta proofs on one built solid (L31 tier 2, L29, L30) | The round-bore composition is no longer built. The test's own comment says d-flat and round read identical cutout deltas and the d-flat rows stay, so what goes unseen is a fault of the chamfer-plus-cutout boolean that only a round bore shows (L31) | by name |
| `selector-cutout-no-recess` | sample | tests/test_model.py::test_every_selector_takes_only_its_own_edges_with_a_body_cutout, rows `no-recess-holes`, `no-recess-spokes`, `no-recess-cells` (3 of 19; group 17.31 s) | 0.83 (0.82 / 0.84) | With a cutout and the recesses off, the floor selector is never called and the rim and tip counts still match (L26, L30) | "No floor call without a recess" is no longer observed on a part with a cutout; its no-cutout twin (`d-flat-no-recess` in `test_each_edge_selector_picks_exactly_its_own_edges`) stays | by name |
| `selector-bottom-recess` | sample | tests/test_model.py::test_each_edge_selector_picks_exactly_its_own_edges, rows `d-flat-bottom`, `round-bottom`, `hex-bottom`, `keyway-d-flat-bottom`, `keyway-round-bottom` (5 of 30; group 14.07 s) | 1.33 (1.35 / 1.32) | A bottom-only recess: the floor selector takes the two floor edges at z = recess_depth, on the d-flat, round, hex and keyed bores (L26, L27, L28) | Bottom-only floor selection is no longer observed on those five bores; the top-only and both-sides rows stay | by name |
| `pre-v0.2-solids` | skip | tests/regression/test_pre_v0_2.py::test_a_pre_v0_2_parameter_set_builds_the_same_solid (39 rows, 39 distinct GearParams; the whole group) | 17.30 (17.58 / 17.01) | Every pre-v0.2 parameter set that builds still builds the same solid: faces, edges, volume at rel 1e-6, six corners at abs 1e-6 (L05, L26) | The milestone's "old links unchanged" proof for the geometry is gone. Only the dimension replay (44 rows) and the kernel-pair tripwire remain, and the fixture's own rule is that a red row here is the code's bug, never the fixture's | by name |
| `pool-same-slot-refusal` | skip | tests/test_pool.py::test_four_same_slot_requests_all_refuse_without_cancellation | 5.10 (5.22 / 4.98) | CR-01, WR-01: four requests queued on one hash slot behind a timeout all surface as `BrokenProcessPool`, never `CancelledError` nor their own `BuildTimeout`; the worker is replaced exactly once and the slot works again (L17, L18) | The only test of the queued same-slot path with real processes: a cancellation escaping every handler, or a double replacement, would no longer be seen | by name |
| `pool-wedged-build` | skip | tests/test_pool.py::test_a_wedged_build_is_terminated_and_its_worker_replaced | 4.43 (4.62 / 4.24) | A build over its timeout is killed, not abandoned, its slot's worker is replaced and the next request succeeds (L17, L18) | The kill-on-timeout and replace path is no longer exercised; `test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced` stays and covers a hard death, not a timeout | by name |
| `api-honeycomb-link` | remove | tests/test_api.py::test_a_honeycomb_link_is_served_with_its_cells | 1.24 (1.21 / 1.27) | `?hex_cell=3&hex_wall=1` end to end: schema group, info's 18 cells and walls, the null default, the large-gear raise-to-fit warning, STL and STEP (L30, L02) | The honeycomb's HTTP contract goes unobserved; the kernel-level honeycomb proofs stay | by name |
| `api-spoke-link` | remove | tests/test_api.py::test_a_spoke_link_is_served_with_the_fillet_it_cut | 1.12 (1.12 / 1.13) | The spoke link end to end: schema group, info's cap and walls, the null default, both exports (L30, L33) | The spokes' HTTP contract goes unobserved; the kernel-level spoke proofs stay | by name |
| `api-tip-chamfer-link` | remove | tests/test_api.py::test_a_tip_chamfer_link_is_served_with_the_chamfer_it_cut | 0.76 (0.76 / 0.76) | `?tip_chamfer=0.4` end to end: schema, applied value and `tip_d`, the cap to 1.75 mm with its warning, the field's refusal above 3, both exports (L29, L03) | The tip chamfer's HTTP contract, including the cap warning a user reads, goes unobserved | by name |
| `api-gzip-after-identity` | remove | tests/test_api.py::test_a_gzip_request_after_an_identity_download_emits_source_compressed | 0.69 (0.69 / 0.69) | After an identity download, the gzip request logs `export.served` with `source=compressed` and a duration above zero (L19, L20) | The compress-from-cached-raw path of the byte cache is no longer observed | by name |
| `api-two-request-ids` | remove | tests/test_api.py::test_two_requests_for_one_gear_get_two_different_request_ids | 0.68 (0.66 / 0.69) | Two requests for one gear log two different request ids, the case params and time cannot tell apart (L20) | A log line could no longer be tied to its request when two identical requests arrive | by name |
| `api-small-gear-recess` | remove | tests/test_api.py::test_a_gear_too_small_for_the_stock_recess_is_still_served | 0.66 (0.64 / 0.68) | A 24-tooth, module-1 gear too small for the stock recess is still served and `/api/info` still reports a recess id (L03, L05) | The cap-and-warn path for the stock recess on a small gear is no longer observed over HTTP | by name |
| `api-repeat-download` | remove | tests/test_api.py::test_a_repeat_download_is_served_from_cache_with_zero_duration_and_no_build_started | 0.65 (0.63 / 0.66) | A repeat download logs `source=cache` with `duration_ms` 0 and no `build.started` (L07, L20) | A byte-cache hit that silently rebuilds would no longer be seen | by name |
| `dedup-g4-regression` | dedup | tests/test_model.py::test_builds_one_valid_solid, rows `kw0` to `kw8` (9 of 23; group 13.78 s), against the nine records of test_a_pre_v0_2_parameter_set_builds_the_same_solid with the same GearParams (six of the records are named after these very rows, `test_model.py::test_builds_one_valid_solid[2]` and so on); both build through `build()` | at most 2.90 (2.84 / 2.95), the nine rows; the saving is one build of each pair, not measured | kw0 to kw8: the built solid is valid, its z length is the face width and its extent is inside the module bound; the replay compares faces, edges, volume and corners of the same solids (L05, L26) | None if the replay's `solid()` gains `isValid()`, the z-length and the extent assertions, so every assertion stays on one build. Deleting the nine rows alone would drop those three assertions | free (D-03) with the assertions moved; by name if the rows are only deleted |
| `dedup-g4-g5` | dedup | tests/test_model.py::test_builds_one_valid_solid rows `kw18`, `kw19`, `kw22` (holes, filleted spokes, cells) and test_the_recess_floor_fillet_survives_every_cutout_on_every_bore rows `d-flat-holes`, `d-flat-spokes`, `d-flat-cells`: the same GearParams built twice (`build()` and `_build_checked()`) | at most 2.81 (2.92 / 2.71), the three fillet rows; the other three rows are 3.08 (3.13 / 3.03); the saving is one build of each pair, not measured | kw18, kw19, kw22: a valid solid of the right height and extent (L30). The fillet rows: the recess floor fillet survives the cutout and the TORUS count is the kernel's (4, 20, 14) (L30, L31) | None: every assertion of both stays on one built solid. The cache cannot do it today (`build()`'s lru_cache holds 4 solids, `SPUR_SOLID_CACHE`, and the rows are about 1,500 lines apart), so it needs one session-level cache of the `_build_reference` kind for these three, and those three `build()` rows would then run `_build_checked` | free (D-03) |

Pairs found and not proposed, so the list is complete. Counted over the five test_model
groups and the 39 regression records by canonical GearParams, nineteen parameter sets are
built by more than one test: nine are the `dedup-g4-regression` pair, three are
`dedup-g4-g5` (two of them, holes and cells, are also built by the d-flat rows of
`test_every_selector_takes_only_its_own_edges_with_a_body_cutout`), and seven more pair the
selector-with-cutout rows `round-holes`, `round-cells`, `hex-holes`, `hex-cells`,
`keyway-holes`, `keyway-spokes` and `keyway-cells` with the matching rows of the
recess-fillet group (nine of the selector test's rows share GearParams with that group in
all). Those are not candidates: the selector test
patches `_bore_rim_edges` and `_groove_floor_edges` with spies and builds through
`_build_checked`, never `build()`, with a comment that says why (15-RESEARCH Pitfall 10), so
its builds cannot be shared. `test_each_edge_selector_picks_exactly_its_own_edges` builds a
bare variant (chamfer and fillet off, `_cut_keyway` patched out) that no other test builds,
the tier-2 rows build a tip-chamfered composition no other test builds, and the 39
regression records are 39 distinct GearParams. The `test_api.py` link tests build the same
links over HTTP, whose build is incidental to the route they prove, and a cross-file
share would be a new design, so none is listed.

Coverage check of every row that removes a test (REQ-coverage-floor's trip point, 96.00).
One scratch run removed all 71 items of the rows above at once, the two dedup rows
included as the worst case: `make test PYTEST_ARGS="-n 8 -q --deselect=<the 71 node ids>"`,
the recipe's `--cov --cov-report=term` first, per R1 and R2 of the recipe (nothing else
alive, load 1.01 read before), HEAD `4b798ac`. Result: `856 passed in 53.67s` (927 - 71),
exit 0, wall 53.91 s, peak tree RSS 6690 MiB (18 processes), and

```
src/spur/app.py              157      3     20      3  96.61%
src/spur/pool.py              54      0      6      0 100.00%
TOTAL                       1069     28    294     17  96.40%
Required test coverage of 96.0% reached. Total coverage: 96.40%
```

With every candidate gone the total is 96.40 %, 0.40 points over the trip point and 0.81
under the 97.21 % the three `-n 8 --cov` runs read (23 missed statements, 15 partial
branches there, 28 and 17 here). A smaller set of removed tests cannot cover less than a
larger one, so every row alone reads at least 96.40 %; the single-row totals were not run.
If the lost worker flush of C0 (0.22 points, debt
`2026-10-04-worker-coverage-flush-is-sometimes-lost.md`) struck on top of the union it would
read 96.18 %, still over. This run is a coverage reading, scratch and not committed: its
53.91 s is one run at load 1.01 and not an alternating A/B pair, so it is no reading of
what the cuts save. The 71 items' seconds in the table add up to 47.46 s serial (the two
dedup rows, 5.71 s of it, are upper bounds), of the 224.28 s serial mean.

None of these rows is recommended here. The gate at `-n 8` with coverage reads a mean of
64.12 s (### Tolerance and coverage cost), so no cut is needed to reach a bar set from
that; the rows are for the record (D-03).

### Gate decision

The human's verbatim answer to 15-03's D-01 checkpoint: "knee-headroom N=8 bar=66 cuts=none before=244.59".

The option taken is `knee-headroom`. Its four consequences, recorded here as the CONTEXT
addendum records them:

- **Bar.** 66 s of `make verify` wall time on this host: the largest of B1-B3 (65.83 s, B2)
  rounded up to the next whole second, to be read in 15-04 as mean(B) of the `-n 8 --cov`
  gate by this section's recipe, alternating with A, and at or under 66 s (D-04, D-05: a
  miss is recorded and goes to the human, never re-run). For scale, the six runs read
  mean(B) 64.12 s, spread 3.33 s (62.50 to 65.83), loads 22.37 to 30.02.
- **N.** 8, the apparent knee K, so ### Tolerance and coverage cost (6 of 6 green at
  N = 8) stands and 15-04 runs no further tolerance runs. CI runs `-n 4` on its 4-vCPU
  runner (Open Question 4).
- **Cuts.** None accepted. Every row of ### Proposed cuts is refused by name:
  `tier2-round-bore`, `selector-cutout-no-recess`, `selector-bottom-recess`,
  `pre-v0.2-solids`, `pool-same-slot-refusal`, `pool-wedged-build`, `api-honeycomb-link`,
  `api-spoke-link`, `api-tip-chamfer-link`, `api-gzip-after-identity`,
  `api-two-request-ids`, `api-small-gear-recess`, `api-repeat-download`,
  `dedup-g4-regression`, `dedup-g4-g5`. Nothing in `tests/` changes in 15-04.
- **Before.** 15-04's Before row is C0, the serial `--cov` run: 244.59 s (### Coverage
  baseline), not the no-`--cov` serial profile's 224.28 s (P1/P2).

### Before and after

Order, fixed before A1: A1 B1 A2 B2.

What A and B are. B is the gate as committed: `make verify` with no extra arguments, which
now runs `pytest -n 8 --cov --cov-report=term` (Makefile `PYTEST_WORKERS`, HEAD `5797199`).
A is the Before the human chose at the profile checkpoint (### Gate decision): the serial
gate with coverage, the gate as 15-02 left it. With `-n 8` in the recipe that is
`make verify PYTEST_ARGS="-n0"`: `PYTEST_ARGS` comes last, so `-n0` overrides `-n 8`, runs
the tests in-process and leaves `--cov --cov-report=term` in place, so the only variable
between A and B is `-n`. (The plan's own A, serial without coverage, is not used: the
human's answer replaces it, and 15-02's C0 at 244.59 s is the same configuration measured
before the Makefile change.) Each run follows ### Method's recipe R1-R5; the read-out below
is from its `.out`, `.time` and `.rss` files. No rerun, no quiet bar (D-04).

Date 2026-10-04, HEAD `5797199` for every row (the `-n 8` commit; `src/`, `tests/` and
`requirements.txt` are byte-identical to `20cd484`, `git diff --quiet 20cd484 -- src tests
requirements.txt` exits 0). Each load is the 1-minute figure read immediately before the
run; it carries the previous row's own work, and nothing else of this session ran on the
host between rows.

| Run | Code | Args | Load | pytest | Wall (s) | Peak RSS (MiB, procs) | Exit |
|---|---|---|---|---|---|---|---|
| A1 | `5797199` | `PYTEST_ARGS="-n0"` (serial, `--cov`) | 14.15 | 927 passed in 227.22s (0:03:47) | 228.23 | 1415 (5) | 0 |
| B1 | `5797199` | none (`-n 8 --cov`) | 5.91 | 927 passed in 63.63s (0:01:03) | 64.19 | 6638 (17) | 0 |
| A2 | `5797199` | `PYTEST_ARGS="-n0"` (serial, `--cov`) | 19.17 | 927 passed in 228.73s (0:03:48) | 229.75 | 1418 (5) | 0 |
| B2 | `5797199` | none (`-n 8 --cov`) | 5.31 | 927 passed in 62.35s (0:01:02) | 62.92 | 6634 (15) | 0 |

mean(A) = 228.99 s, mean(B) = 63.555 s -> delta = -165.435 s (B is 3.60 times faster)

Bar: 66 s (15-CONTEXT.md D-01 addendum) -> met, mean(B) = 63.555 s

mean(B) is 2.445 s under the bar. The two B walls are 64.19 s and 62.92 s (spread 1.27 s);
15-02's three `-n 8 --cov` runs read 64.03, 65.83 and 62.50 s at loads 22.37 to 30.02, so
these two, at loads 5.31 and 5.91, sit inside that range. The bar is the largest of those
three rounded up (65.83 s -> 66 s) and neither B row here is over it.

Test count: 927 passed in every row, exit 0, no failed, error or rerun in any `.out` (the
only "error" text is the file name `src/spur/build_errors.py` in the coverage table); no cut
was applied, so there is no difference to name.

Coverage on the four rows (`--cov`, floor `fail_under = 96`, "Required test coverage of
96.0% reached" in every `.out`): A1 and A2 read `TOTAL 1069 26 294 15 96.99%` with
`src/spur/pool.py` at 95.00% (lines 63-67 and 222 missing, the lost worker flush of C0),
B1 and B2 read `TOTAL 1069 23 294 15 97.21%` with `pool.py` at 100.00%. Counting C0, all
three serial full `--cov` runs of this phase lost those three statements, and none of the
six `-n 8 --cov` runs that printed `pool.py` did (15-02's B1-B3, B1 and B2 here, and the
71-item deselect run under "Proposed cuts" above), nor did the CI run at `-n 4` below.
15-RESEARCH Pitfall 13 saw the same loss once at `-n 4`, so it is not specific to serial;
the tally is a count of ten runs, not a cause.

Largest peak RSS of the four rows: 6638 MiB (B1, 17 processes), an upper bound by the same
rule as the sweep (shared-library pages count once per process); the serial A rows peak at
1415 and 1418 MiB. CPU time (`/usr/bin/time -p`): A1 user 354.94 s + sys 619.62 s, A2 357.00
s + 627.82 s; B1 366.42 s + 283.93 s, B2 365.48 s + 274.63 s.

A is the Before the human chose (serial, coverage on): 15-02's C0 read 244.59 s at load
8.37 before `-n 8` went in; A1 and A2 read 228.23 s and 229.75 s here, 16.36 s and 14.84 s
less, at loads 14.15 and 19.17 (the cause of the difference was not tested). Context, not a
bar reading: the pre-commit hook of the Makefile commit itself (`make verify` with the new
recipe plus the commit-msg hook), taken from `date` before and after `git commit`, was
64 s. CI's `test (3.12)` job duration is context on a
different, 4-vCPU host, recorded in 15-05's CI-run subsection, below, and never the bar (D-02).

### CI run

Run: https://github.com/halfb00t/spur/actions/runs/37181871926 (id 37181871926), the
`pull_request` run of ci.yml on the draft phase PR #18, head `839dfeaa33d60c1c996c9d7c111190a1dcca4cbc`
(the `ci(15-05)` commit that carries the pin). Conclusion `success`; `test (3.12)`, `image` and
`vendor-bundle` all `success` (the three jobs `required-jobs.txt` lists).

What the log printed, copied from `gh run view 37181871926 --log`:

- The step `kernel pair this run resolved` printed `cadquery 2.8.0 cadquery-ocp 7.9.3.1.1`,
  the strings in `tests/regression/pre_v0_2.json`'s provenance header.
- The install line of the `make verify PYTHON=python` step (pip's own output, under
  `PIP_CONSTRAINT: requirements.txt`) lists `cadquery-2.8.0 cadquery-ocp-7.9.3.1.1
  cadquery-ocp-proxy-7.9.3.1.1`, and `pytest-cov-7.1.0` and `pytest-xdist-3.8.0` from the
  dev extras. setup-python reported `Cache hit` for its pip cache and pip's install output
  still named the pair (RESEARCH Pitfall 14 again: the cache restores downloads, not the
  venv).
- Workers: `created: 4/4 workers`, then `4 workers [927 items]`. `PYTEST_WORKERS` is 8
  clamped to the online CPUs (15-04), and `ubuntu-latest` has 4, so `-n 4`.
- pytest: `927 passed in 203.16s (0:03:23)`, no failed, error or rerun. Coverage
  `TOTAL 1069 22 294 15 97.29%` against the floor `fail_under = 96`.
- `test (3.12)` job: started 2026-10-04T06:07:19Z, completed 2026-10-04T06:11:46Z, 267 s
  (4 min 27 s) including checkout, setup-python and the venv install.

Beside it, so a reader does not assume CI got no worse: the last CI run before the phase
changed the gate, 37116412012 (2026-10-03, serial, no coverage), printed `927 passed in
193.21s`; its `test (3.12)` job ran 240 s and its `make verify` step 231 s. This run reads
203.16 s, 267 s and 259 s. Two single runs on different commits, no verdict drawn — but on
the 4-vCPU runner `-n 4` with coverage and two more dev packages made pytest about 10 s
slower and the job 27 s slower; the 3.6x gain is the dev host's, eight workers on twelve
CPUs. The runner has not been A/B'd. (Both logs re-read with `gh run view --json jobs` and
`--log` on 2026-10-06; 15-REVIEW WR-01.)

The pair came out right on the first run, so the tripwire
`test_the_fixture_was_captured_on_the_kernel_this_run_uses` passed in this run's 927. Whether the
constraint, rather than cadquery 2.8.0's own `cadquery-ocp<8.0` cap, held the pair here cannot be
read from one run: both give 7.9.3.1.1 today. The local dry run in 15-05 Task 1 is what shows the
constraint fails closed (a `cadquery-ocp==8.0.1.0.0` constraint file gives `ResolutionImpossible`).

This is context on GitHub's 4-vCPU `ubuntu-latest` runner with a different CPU and `-n 4`, never
the bar: the 66 s bar is the dev host's gate (15-CONTEXT.md D-01 addendum, D-02), and 203.16 s here
is not read against it.

## Same-slot timeout race (Phase 17)

**The question.** SC3 (Phase 13, "### Composed worst row under ten concurrent builds (Phase 13)")
saw two undocumented raw `500`s, request ids `912cd2d4` and `0fc30d53`, each the second
request on a hash slot whose first request had just timed out. The race the active debt
describes (`docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md`)
was never reproduced on purpose: SC3 hit it by affinity luck among ten distinct keys. Does it
reproduce when the affinity is made certain, before any fix is written?

**The scenario.** `identical` in `bench/latency.py` (registered in `_SCENARIOS`, not in
`DEFAULT_SCENARIOS`, so `make bench.latency` is unchanged): `bench/sweeps/composed.json` row 4,
the composed worst row (29.42 s alone), ten times -- `teeth=200 module=10 bore_d=9 bore_flat=0
keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4
spoke_fillet=5 tip_chamfer=3 recess_sides=both`. Ten copies are one cache key, so every
admitted copy shares one hash slot. Firing rule (`run_composed`, unchanged from SC3): request #1
leaves the client alone, the other nine fire once `/api/health` shows #1 holding a build slot.
Fresh server on :8001 started by this plan for each attempt, shipping defaults
(`SPUR_BUILD_WORKERS`, `SPUR_MAX_QUEUED_BUILDS` and `SPUR_BUILD_TIMEOUT` unset: 2 workers, 4
queued builds, 30 s per-build timeout), stopped after it. Client command:
`.venv/bin/python -m bench.latency --base-url http://127.0.0.1:8001 identical`; it records a
`500` instead of raising on it (`_fetch(..., record_500=True)`). Commit under test: `814f4f3`
(the scenario's own commit, 17-03 Task 1). There is no quiet-host gate (Phase 17 D-14): the
1-minute load is recorded beside each attempt and every number below belongs to it. This scenario
is not part of the gate and not a bar reading; the idle/under-load p95 section the harness prints
after the table is kept in each `attempt-N.client.txt` and is not read against the bar.

Raw records, uncut: `.planning/phases/17-debt-first-commit-gate-and-pool-race/investigation/attempt-N.server.log`
(the server's stderr, one JSON object per line, including uvicorn's own access lines) and
`attempt-N.client.txt` (the client's whole output).

### Attempt 1 (before the fix)

#### Host state

- Machine: Apple M2 Max (`sysctl -n machdep.cpu.brand_string`); `bench.machine_facts()`:
  12 CPUs, arm64, 32.0 GiB RAM
- Python 3.12.13 (`.venv`), cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `814f4f3`
- Started 2026-10-06T09:17:41Z, server stopped 2026-10-06T09:18:23Z (requests fired about
  09:17:47Z; the server's last `build.failed` is at 09:18:17Z)
- Load (1-minute, `sysctl -n vm.loadavg`): 5.48 before (5.94 at the preflight a few seconds
  earlier), 5.88 after. The host carried background load throughout; no quiet bar was waited for.
- `docker ps` before and after: no containers running (header line only, both times).
  `spur-spur-1` is not up on this host today, so there was no service on :8000 to disturb;
  nothing was started or stopped on it. `lsof -nP -iTCP:8001 -sTCP:LISTEN` printed nothing before
  the start and nothing after the stop.
- SPUR_* environment: none set; the server's first `/api/health` read
  `{"workers":2,"queue_available":4,"workers_replaced":0}`.
- Client exit status: 0.

#### Client table

| # | Parameters | Outcome | Wall time (s) |
|---|---|---|---|
| 1 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 503 timeout | 30.01 |
| 2 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 500 | 30.00 |
| 3 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 500 | 30.01 |
| 4 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 503 busy | 0.01 |
| 5 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 500 | 30.01 |
| 6 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 503 busy | 0.01 |
| 7 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 503 busy | 0.01 |
| 8 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 503 busy | 0.01 |
| 9 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 503 busy | 0.01 |
| 10 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 503 busy | 0.01 |

503 timeout: 1, 500: 3, 503 busy: 6
- /api/health workers_replaced: 0 -> 1

#### Server readout

Read from `attempt-1.server.log` (4 `build.started`, 6 `queue.refused`, 4 `build.failed`, 1
`worker.replaced`, 3 "Exception in ASGI application" lines). The client does not read request
ids, so rows are matched to ids by outcome and start order: the one `503 timeout` row is the one
`BuildTimeout` record, and the three `500` rows are the three `AttributeError` records.

| Request | Started (UTC) | Server outcome | duration_ms |
|---|---|---|---|
| `cf3e6608` | 09:17:47.5956 | `build.failed`, `BuildTimeout` (client: `503 timeout`) | 30003 |
| `44be5292` | 09:17:47.6008 | `build.failed`, `AttributeError` (client: `500`) | 30000 |
| `2bdbff52` | 09:17:47.6094 | `build.failed`, `AttributeError` (client: `500`) | 30000 |
| `b9183811` | 09:17:47.6100 | `build.failed`, `AttributeError` (client: `500`) | 30001 |

`queue.refused`: 6, all between 09:17:47.6103 and 09:17:47.6123 (the six `503 busy` rows). No
`export.served`; no `503 pool_broken`; nothing in the table is called the race except a `500`
backed by an `AttributeError` record. The three tracebacks all end
`AttributeError: 'NoneType' object has no attribute 'values'`.

`/api/health` `workers_replaced`: 0 -> 1. `worker.replaced`: one, slot 0, `cause: "timeout"`, at
09:18:17.5984 -- just before `cf3e6608`'s `build.failed` at 09:18:17.5985. The three
`AttributeError` records follow at 09:18:17.6012, .6097 and .6109: 2.7, 11.3 and 12.5 ms after the
first request's `build.failed`, on the slot whose worker had just been replaced. So the server
replaced one worker and failed three same-slot siblings with an `AttributeError` that reached the
client as a raw `500`.

**Verdict:** hit. A `500` row is backed by the server's own `build.failed` record with
`exception: AttributeError`, three times over, and the count of ASGI exceptions (3) matches.

**The slot-holding request (D-11):** #1 (`cf3e6608`) was not served: `503 timeout`, client wall
30.01 s, server `duration_ms` 30003, at this load (5.48 -> 5.88). A request that is 29.42 s alone
did not finish inside the 30 s `SPUR_BUILD_TIMEOUT` here, with three same-key siblings queued
behind it. One reading at one load, taken as measured; it is the identical-row figure
L37 (Phase 17-05) reads, not a margin claim of its own.

### Before the fix: verdict

Reproduced in attempt 1.

The first attempt saw the undocumented `500`: three of them, each a same-slot sibling of the
request whose timeout replaced the slot's worker, each backed by an `AttributeError`
`build.failed` record in the server's own log. Attempts 2 and 3 were not run (stop at the first
hit, D-15). 17-04's D-17 checkpoint is not reached: the fix is written against a failure someone
saw.


### After the fix

Commit under test: `0628182` (`fix(17-04): a second same-slot timeout raises BuildTimeout, never
AttributeError`), the last commit to touch `src/spur/pool.py`; HEAD at the run was `d30f32f`, whose
only later commits are docs. Same scenario, same client command and same fresh-server protocol as
"### Attempt 1 (before the fix)" (`identical`, composed.json row 4 ten times, shipping defaults,
:8001); the only change under test is the fix. Raw records, uncut:
`.planning/phases/17-debt-first-commit-gate-and-pool-race/investigation/after-1.server.log` (the server's stderr, 44,329
lines, 7.6 MB, sha1 `55903d84c961b2f8d63bb9d30fbaf70efbf2542a`) and `after-1.client.txt`. One run was
enough: it was decisive and held, so none of the three allowed runs was repeated.

#### Run 1

##### Host state

- Machine: Apple M2 Max (`sysctl -n machdep.cpu.brand_string`); 12 CPUs, arm64, 32.0 GiB RAM
  (the harness's own `machine_facts` line in `after-1.client.txt`)
- Python 3.12.13 (`.venv`), HEAD `d30f32f`, branch `gsd/phase-17-debt-first-commit-gate-and-pool-race`
- Server started 2026-10-06T09:57:57Z (PID 61223), client fired the ten requests about 09:58:03Z
  (the server's first `build.started` is at 09:58:05.9496Z, after the client's settle sampling), the
  server's last `build.failed` is at 09:58:35.9648Z, server stopped by PID, `lsof -nP
  -iTCP:8001 -sTCP:LISTEN` printed nothing before the start and nothing after the stop
- Load (1-minute, `sysctl -n vm.loadavg`): 20.33 at the preflight (09:57:51Z), 18.94 at the server
  start, 15.30 right after the client finished (09:58:35Z), 13.49 after the stop (09:58:42Z). The
  host was busier than at attempt 1 (5.48 to 5.88); no quiet bar was waited for (D-14), and every
  reading below belongs to this load.
- `docker ps` before and after: no containers running (header line only). `spur-spur-1` is not up
  on this host today; nothing was started or stopped on it and :8000 was never touched.
- SPUR_* environment: none set; the server's first `/api/health` read
  `{"workers":2,"queue_available":4,"workers_replaced":0}`.
- Client exit status: 0.

##### Client table

| # | Parameters | Outcome | Wall time (s) |
|---|---|---|---|
| 1 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 503 timeout | 30.01 |
| 2 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 503 timeout | 30.00 |
| 3 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 503 timeout | 30.01 |
| 4 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 503 timeout | 30.01 |
| 5 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 503 busy | 0.01 |
| 6 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 503 busy | 0.01 |
| 7 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 503 busy | 0.01 |
| 8 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 503 busy | 0.01 |
| 9 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 503 busy | 0.01 |
| 10 | teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both | 503 busy | 0.01 |

503 timeout: 4, 503 busy: 6
- /api/health workers_replaced: 0 -> 1

##### Server readout

Read from `after-1.server.log` (4 `build.started`, 6 `queue.refused`, 4 `build.failed`, 1
`worker.replaced`; no "Exception in ASGI application" line and no `Traceback`). Rows are matched
to request ids by outcome and start order, as in attempt 1.

| Request | Server outcome | duration_ms |
|---|---|---|
| `d6cd9587` | `build.failed`, `BuildTimeout` (client: `503 timeout`) | 30003 |
| `fd31a765` | `build.failed`, `BuildTimeout` (client: `503 timeout`) | 30000 |
| `49f774bd` | `build.failed`, `BuildTimeout` (client: `503 timeout`) | 30000 |
| `a45e9734` | `build.failed`, `BuildTimeout` (client: `503 timeout`) | 30000 |

`worker.replaced`: one, slot 0, `cause: "timeout"`, at 09:58:35.9532Z, 0.06 ms before the first
`build.failed` at 09:58:35.9533Z; the other three `build.failed` records land 2.6, 11.0 and 11.5 ms
after it, in the same window in which attempt 1 logged its three `AttributeError` records. No
`build.failed` carries `exception: AttributeError`, no `500` row exists in the client table, no
`503 pool_broken` appears. `/api/health` `workers_replaced`: 0 -> 1.

**Decisive:** yes. Four admitted requests ended in `build.failed` with `BuildTimeout` and
`workers_replaced` rose from 0 to 1, so the same-slot double timeout actually happened: one
timeout replaced the slot's worker and three same-slot siblings timed out within 11.5 ms of it
(the order is read from the records' timestamps, not from a causal log). Each of them got the
documented `503 timeout`.

**The slot-holding request (D-11):** #1 (`d6cd9587`, 29.42 s alone) was not served: `503 timeout`,
client wall 30.01 s, server `duration_ms` 30003, at this load (18.94 at the server start, 15.30
after the client), with three same-key siblings queued behind it. One reading at one load, taken as
measured; it is the second identical-row reading L37 cites beside attempt 1's (30.01 s,
`duration_ms` 30003 at load 5.48 to 5.88).

Zero 500s after the fix: run 1 of 1 (one decisive, none non-decisive) on `0628182` shows no `500`
row and no `AttributeError` record, where the same scenario on `814f4f3` showed three and three.
The bench is not the proof: the deterministic stale-executor test, red before and green after
(17-04), is.

## Trochoid maths (Phase 18)

What the hob's trochoid root costs to trust, in the order the phase builds it: the cutter's tip
radius cap and the junction bar it is held to (18-01, this subsection), the join epsilon (18-03),
the generator sweep over the allowed box (18-03), the oracle bars and their tripwires (18-04),
the per-call costs and the root-shape step (18-05). Each subsection carries its own host state,
because every number below belongs to the load it was read at. Nothing here is a kernel
measurement: the maths is pure stdlib `math` in `calc.py`, so the kernel pair is recorded only
because every section of this file records it.

### Cutter cap and junction (18-01)

#### Host state

- Machine: Apple M2 Max (`sysctl -n machdep.cpu.brand_string`); `bench.machine_facts()`:
  12 CPUs, arm64, 32.0 GiB RAM
- Python 3.12.13 (`.venv`), cadquery 2.8.0, cadquery-ocp 7.9.3.1.1 (the pinned pair; this
  measurement does not use the kernel)
- HEAD: `8e75273` (the commit that carries the tests quoted below)
- Read 2026-10-08T01:29:17Z to 01:29:19Z (the test run and the scratch table, two seconds)
- Load (1-minute, `sysctl -n vm.loadavg`): 3.39 before, 3.39 after. The host carried
  background load; no quiet bar was waited for. These are float-arithmetic residues, not
  timings, so load does not move them; it is recorded because every section records it.

#### The cap, reconciled

`tests/test_trochoid.py::test_the_cap_formula_reconciles_0_318_m_and_0_363_m_as_one_cap_at_two_backlashes`
is the phase's first test. PITFALLS gave the largest cutter tip radius at module 1.75, 25 degrees
as 0.635 mm = 0.363 m; STACK and FEATURES gave 0.318 m. They are one formula,
`(pi*m/4 + backlash/2 - 1.25*m*tan(alpha)) / (1/cos(alpha) - tan(alpha))`: the first is the
default gear's 0.10 mm backlash entering the tip land as backlash/2, the second is the same gear
at backlash 0 (SUMMARY's inference, now measured). It does not depend on the profile shift:
x = -0.4, 0 and 0.6 agree to 2.2e-16 mm.

| module | pressure angle | backlash | `rho_max` (mm) | `rho_max / m` | the figure it reconciles |
|---|---|---|---|---|---|
| 1.75 | 25 | 0.10 | 0.63478 | 0.36273 | PITFALLS' 0.635 mm = 0.363 m |
| 1.75 | 25 | 0 | 0.55629 | 0.31788 | STACK / FEATURES' 0.318 m |
| 1 | 20 | 0 | 0.47191 | 0.47191 | the tracer gear's cap |

#### The cap, floored

Module 0.5, 15 degrees, 12 teeth, backlash 0: the unrounded cap is 0.29353 mm (0.2935265).

| request (mm) | used (mm) | tip land `a` (mm) | cap sentence |
|---|---|---|---|
| 0.293 | 0.293 | 4.04e-4 | none (under the cap) |
| 0.294 | 0.293 | 4.04e-4 | "Cutter tip radius reduced to 0.293 mm, ..." |
| 0.2935265 (the cap itself) | 0.2935265 | 0 | none (not trimmed) |
| 0.294 if rounded to nearest | 0.294 | -3.63e-4 | would refuse a legal gear as having no tip land |

The used radius and the printed one are the same float.

#### The tip-land limit, one field step either side

The sign of the sharp-corner land `a0` decides it, so it moves with backlash and module (the limit
is tan(alpha) = (pi/4 + backlash/(2 m)) / 1.25: 32.14 degrees at backlash 0, 33.07 at the default
gear).

| gear | pressure angle | `a0` (mm) | tip land |
|---|---|---|---|
| 12 teeth, m 1, x 0, backlash 0 | 32.0 | +0.00431 | yes, a curve |
| 12 teeth, m 1, x 0, backlash 0 | 32.5 | -0.01094 | none, `tip land gone` |
| 19 teeth, m 1.75, x -0.4, backlash 0.10 | 33.0 | +0.00387 | yes, a curve |
| 19 teeth, m 1.75, x -0.4, backlash 0.10 | 33.5 | -0.02343 | none, `tip land gone` |

#### The junction bar

The tangent junction needs no root-find: the curve ends at the cutter flank's foot and its last
point is the involute's. Gaps of the last point against `Profile.half_angle` at its radius and
against `sqrt(rb^2 + xi^2)`, and the angle between the two curves' directions there (unit
chords over the last 1e-7 rad of contact-normal angle):

| row | backlash | abs delta half-angle (rad) | abs delta R (mm) | direction angle (rad) |
|---|---|---|---|---|
| 19 teeth, m 1.75, 25 deg, rho 0.5 | 0 | 1.39e-17 | 1.78e-15 | 1.38e-7 |
| 19 teeth, m 1.75, 25 deg, rho 0.5 | 0.10 | 1.39e-17 | 1.78e-15 | 1.38e-7 |
| 30 teeth, m 1, 20 deg, rho 0.38 | 0 | 4.16e-17 | 0 | 1.10e-7 |
| 30 teeth, m 1, 20 deg, rho 0.38 | 0.10 | 1.39e-17 | 0 | 1.11e-7 |

Bars, each from the two recorded numbers (the model's gap and float64's own resolution at that
magnitude: one ulp is 2.8e-17 rad near 0.2 rad and 1.78e-15 mm at R 15.3 mm):

| bar | value | largest measured | headroom |
|---|---|---|---|
| `JUNCTION_BAR_RAD` | 1e-12 rad | 4.16e-17 rad | 2.4e4 (1e-12 is the cross-platform libm floor; 10x the gap would be 1e-15) |
| `JUNCTION_BAR_MM` | 1e-12 mm | 1.78e-15 mm | 562 (same floor) |
| `DIRECTION_BAR_RAD` | 1e-5 rad | 1.38e-7 rad | 72 (smallest power of ten above 10x the reading) |

The direction angle is the chord's own error, not noise: it reads 1.39 * step and 1.16 * step at
steps 1e-4, 1e-5 and 1e-6 (1.39e-4, 1.39e-5, 1.39e-6 rad on the first row), so the tangents
agree and only the secant differs. At a step of 1e-8 float noise starts to show (1.1e-8 and
3.6e-8 rad), which is why the test uses 1e-7.

Tripwires (both seen red):

- A cutter built with backlash 0 for the backlash-0.10 default gear ends 3.008e-3 rad from
  that gear's involute, 0.0460 mm at its radius (PITFALLS 3's 0.046 mm step): 3.0e9 times
  `JUNCTION_BAR_RAD`. Mutation check, 2026-10-08: with the cutter ignoring backlash the
  junction test fails on both backlash-0.10 rows and passes on both backlash-0 rows.
- Tangency holds only for z >= z_min. The 17-tooth, 20 degree, rho 0.38 gear (z_min 17.10, so
  just undercut, join `crossing`) reads a direction angle of 3.08e-3 rad at its crossing:
  308 times `DIRECTION_BAR_RAD`, 2.2e4 times the tangent rows' reading. (Read 4.13e-3 rad
  until 2026-10-08, when the secant was taken at the cutter's flank foot, which is not where
  that curve ends -- cross-review XR-02.)

No headroom here is under 10x. 18-04 Task 3 (the phase's L33 D-06 checkpoint) collects every
18-01 bar again.

### Join epsilon (18-03)

The question (D-09): how close to the z_min double root may `xi` (the roll of the cutter's flank
foot, mm) get before the closed-form bracket for the junction with the involute is lost, so that
inside that band the flank join is taken as the form point without a bracket? The band has to be
relative to `rb`: STACK and 18-RESEARCH saw it scale with the base radius (1e-5 mm at module 0.2,
1e-4 at module 1, 1e-3 at module 10). `calc.TROCHOID_JOIN_EPS` was the research value, 1e-4, from a
prototype; this is the measurement made in the repo, with the repo's `_junction`.

Command, from the repo root: `.venv/bin/python -m bench.trochoid epsilon` (about 0.7 s).

#### Host state

- Machine: Apple M2 Max (`sysctl -n machdep.cpu.brand_string`); `bench.machine_facts()`:
  12 CPUs, arm64, 32.0 GiB RAM
- Python 3.12.13 (`.venv`); stdlib maths only, no kernel in this measurement
- HEAD: `39c00dd` (the commit that carries `bench/trochoid.py` and the constant's comment)
- Read 2026-10-08T01:59:30Z (the table below); the run that wrote the constant's comment, a minute
  earlier, printed the same figures
- Load (1-minute, `os.getloadavg()`): 2.21 before, 2.21 after. These are float residues, not
  timings, so load does not move them; it is recorded because every section records it.

#### The scan

`random.Random(18)`, 400 usable draws (1,163 attempts, 763 skipped): teeth 6 to 40, module from
{0.2, 0.5, 1, 1.75, 4, 10}, pressure angle on the 0.5 degree grid 14.5 to 30, backlash from
{0, 0.1, 0.25, 0.5}, tip radius a uniform fraction 0 to 0.5 of the module. For each draw the
profile shift is tuned (xi is linear in it: `xi(x) = xi(x0) + (x - x0) * m / sin(alpha)`, and `rb`
does not depend on it) so that `xi = -t * rb` for t from 1e-2 down to 1e-12 at 4 steps per decade
(41 values), and `_junction(c, 0.0)` is called at each. A draw is skipped when its cutter has no tip
land, its own z_min double root is outside the field's shift range -0.6 to 1.0, or the gear does not
validate (763 of 1,163 attempts).

| | value |
|---|---|
| draws used | 400 |
| draws that lost the bracket at some t | 400 (never lost: 0) |
| largest lost t | 5.62e-6 |
| median of the draws' largest lost t | 3.16e-6 |
| 18-RESEARCH F6 (361 prototype draws) | largest 1.0e-5, median 3.2e-6 |

| decade of the largest lost t | draws |
|---|---|
| 1e-6 to 1e-5 | 399 |
| 1e-7 to 1e-6 | 1 |

STACK's two points, re-created on the 10-tooth, 20 degree, module 1, backlash 0, tip radius 0.38 mm
gear (rb 4.6985 mm) with the epsilon at 0: the bracket is found at xi -2.9e-3 mm, as STACK
measured, and also at -2.9e-5 mm, where the prototype lost it. That gear's own edge in this scan is
t = 5.62e-6, xi = -2.64e-5 mm: the same place as STACK's loss point to within one scan step (a
quarter decade is a factor 1.8, and 2.9e-5 / 2.64e-5 is 1.1). So the two points bracket the edge
and the repo's solver does not move it.

#### Decision

Recommended constant: the smallest power of ten at least 10x the largest loss: 10 * 5.62e-6 =
5.62e-5, so 1e-4. `TROCHOID_JOIN_EPS` stays 1e-4; its comment now quotes this run (date, load,
draws, largest and median loss, STACK's two points as the bracket, the error bound). The scan's
ceiling for a constant worth writing is 1e-3; 1e-4 is a decade under it.

The flank-join error where the bracket would have worked is bounded by `(eps*rb)^2 / (2*rb)` =
`eps^2/2 * rb` = 5e-9 * rb: 2.4e-8 mm at the 10-tooth gear's rb, and 4.8e-6 mm at the largest base
radius the box allows (200 teeth, module 10, 14.5 degrees, rb 968 mm). That is the maths bound, not
a kernel measurement; no kernel was run here.

Pinned in `tests/test_trochoid.py`: 9 / 10 / 11 teeth (30 degrees, module 1, no shift) read crossing
/ tangent / tangent, the 10-tooth `xi` is -8.9e-16; x -0.05 / 0.05 at the same gear read crossing /
tangent; at xi = -10 * eps * rb the bracket is found and the last point is on `Profile.half_angle`
to 1e-12 rad, at -eps * rb / 10 it is the flank join; STACK's -2.9e-3 mm is a crossing and -2.9e-5
mm is a tangent join; with the constant patched to 0 at xi = -1e-9 * rb the bracket is lost and
`root_mode` names `bracket degenerate`.

### Generator sweep (18-03)

The question (SC2, D-12, D-13): for every gear the project allows, does the generator give a curve
or a named refusal, never a numerical failure and never a curve that loops, rises above the tip
circle or fails to meet the involute? The grid is written out as literals in `bench/trochoid.py`
(`GRID_A`, `GRID_B`) and pinned in `tests/test_bench.py`; every case is checked against closed
forms typed in that module (rb, rf, ra, the tooth-thickness angle, xi and the involute half-angle
written from the textbook rack, not read from calc's expressions).

- **Grid A**, STACK's whole product at module 1: teeth 6 to 40, 60, 100, 200 (38); profile shift
  -0.6 (the field's limit; STACK's -1 is rejected by `GearParams`), -0.5, -0.2, 0, 0.2, 0.5, 1.0;
  14.5 / 20 / 25 degrees; backlash 0 and 0.10; tip radius 0, 0.1, 0.25, 0.38, 0.5 times the module
  and the cap request (3.0 mm, the `root_fillet` maximum, which each cutter trims to its own cap):
  1,596 gears, 9,576 cases, 1,489 gears accepted. The x = 1.0 rows with a tip radius at or over
  the tip depth stay in (18-RESEARCH F5: STACK's 7,296 dropped them).
- **Grid B**, the box corners: module 0.2 / 1.75 / 10; teeth 6, 7, 8, 9, 10, 12, 14, 17, 18, 20,
  25, 30, 40, 60, 100, 116, 117, 200; 14.5 / 20 / 25 / 30 / 32.0 / 32.5 / 33.0 / 33.5 / 35
  degrees; shift -0.6 / 0 / 1.0; backlash 0 / 0.10 / 1.0; tip radius 0, 0.25 m, 0.5 m, 0.5 mm
  (each case's own `root_fillet` default) and the cap request: 4,374 gears, 21,870 cases, 1,924
  gears accepted.

Command, from the repo root:
`.venv/bin/python -m bench.trochoid sweep --list .planning/phases/18-trochoid-maths-proved/investigation/18-03-refusals.tsv`

#### Host state

- Machine: Apple M2 Max (`sysctl -n machdep.cpu.brand_string`); `bench.machine_facts()`:
  12 CPUs, arm64, 32.0 GiB RAM
- Python 3.12.13 (`.venv`); stdlib maths only, no kernel in this measurement
- HEAD: `32d7697` (the commit that carries the sweep, its gate test and its pins)
- Bench run read 2026-10-08T02:03:37Z; load (1-minute, `os.getloadavg()`) 4.01 before and after
- The host carried background load throughout (1-minute load 2 to 7); no quiet bar was waited for,
  so every timing below is an upper bound for a quiet host and a fair one for the commit gate,
  which runs on the same machine under the same kind of load.

#### The bench run (the whole product)

31,446 cases in 1.75 s wall (1.77 s on the first run, load 2.0). Zero problems, zero
`bracket degenerate`, zero `curve invalid`.

| outcome | cases |
|---|---|
| not a gear (`GearParams` refuses the fields) | 12,892 |
| nothing radial to replace (`rb <= rf`) | 7,175 |
| tip land gone (`a0 < 0`) | 980 |
| tooth severed | 73 |
| trochoid / crossing | 4,466 |
| trochoid / crossing / capped | 1,557 |
| trochoid / tangent | 2,657 |
| trochoid / tangent / capped | 1,646 |

18,554 cases are gears (1,489 x 6 + 1,924 x 5); 10,326 of them have a curve, 8,228 are a named
refusal. By module:

| module | not a gear | nothing radial to replace | tip land gone | tooth severed | trochoid |
|---|---|---|---|---|---|
| 0.2 | 6,185 | 420 | 65 | 4 | 616 |
| 1 | 642 | 2,520 | 0 | 15 | 6,399 |
| 1.75 | 3,710 | 1,730 | 345 | 36 | 1,469 |
| 10 | 2,355 | 2,505 | 570 | 18 | 1,842 |

Every refusal is one of the three the predicate names; the list is
`.planning/phases/18-trochoid-maths-proved/investigation/18-03-refusals.tsv`, 8,228 rows and a
header (7,175 nothing radial, 980 tip land gone, 73 tooth severed). The tip-land refusals are at
32.5, 33, 33.5 and 35 degrees (260, 230, 240, 250); the severed teeth are 47 at 6 teeth, 13 at 7,
8 at 8, 4 at 9 and 1 at 10, 53 at 14.5 degrees and 20 at 20 degrees, with a waist half-angle from
-0.1426 to -0.00055 rad (the tsv's last column). F9's nesting holds over the product: no crossing
has `rb <= rf`. D-11's accounting stands: nothing outside the three named reasons exists in the
box, so the checkpoint was not reached.

#### The worst junction gaps against `SWEEP_BAR`

`SWEEP_BAR = 1e-12` (the junction radius relative, the half-angle in rad).

| join | worst gap | headroom to the bar |
|---|---|---|
| crossing, half-angle against the involute | 6.9e-16 rad | 1.4e3 |
| tangent, half-angle against the involute | 1.7e-16 rad | 6.0e3 |
| tangent, radius against sqrt(rb^2 + xi^2), relative | 4.0e-16 | 2.5e3 |
| tangent inside the join band (xi in [-eps*rb, 0)) | 2.44e-13 rad | see below |

The band row is geometry, not noise. Inside the band the flank join is the form point, and the
cutter's flank foot sits at negative roll, on the involute's continuation through the base circle,
so its half-angle differs from the involute's by 2 (tan(phi) - phi) with tan(phi) = |xi| / rb: 6.7e-13
rad at the band's edge for eps = 1e-4. `check_curve` allows that term on top of the bar. Two cases of
the product are inside the band besides the five exactly on z_min (10 teeth, 30 degrees, no shift,
sharp cutter; xi / rb about -2e-16): grid A, 26 teeth, module 1, 20 degrees, shift -0.6, backlash
0.10, tip radius 0.5 mm, xi / rb = -7.16e-5, and grid A, 32 teeth, 14.5 degrees, shift -0.2, tip
radius 3.0 mm (trimmed), xi / rb = -4.75e-5. The first reads 2.44e-13 rad against the closed form
2 (tan(phi) - phi) = 2.44e-13: the model of the band's error is right to the last digit.

Checker mutations, 2026-10-08, each run as a stride-7 sweep and each exiting 1: the join band in
calc patched to 1e-2 (the bench's own rack disagrees on the join), every half-angle shifted by
1e-6 sin(beta) (the last point leaves the involute), and the first radius moved 1e-9 off the root
circle. The sweep can fail.

#### The gate (D-13)

`tests/test_calc.py::test_the_trochoid_sweep_over_the_allowed_box` runs the whole product with
`check_case` and asserts the tally above as a literal dict.

- Isolated, `make test PYTEST_ARGS="tests/test_calc.py -q -n 8 --no-cov --durations=5 -k
  trochoid_sweep"`: call time 1.72, 1.71 and 1.68 s (1-minute load 2.2 after).
- Inside the commit slice, `make verify.fast PYTEST_ARGS="--durations=3"`: 1.92 s call (load 2 to
  3), the slowest test of the slice, running beside the other workers.

**Decision: the whole product stays in the gate, no stride.** The plan's line is a call time over
2.0 s at `-n 8`; the isolated reading is 1.7 s, which is 15 percent under it. The in-slice reading
is 4 percent under it. The planning-time prototype costs (87 usec per crossing solve, 8.5 usec per tangent solve, plus
the waist's 60 golden steps; load 1.5) suggested a price above the line; the measured whole is
1.75 s over 18,554 gears, 94 usec per gear with the validation of the 12,892 refused field sets
included. Not isolated further. Had it read over 2.0 s the gate would keep
`itertools.islice(sweep_cases(), 0, None, k)` for the smallest k that fits and `bench/trochoid.py
sweep --stride k` reproduces that sample's tally.

`make verify.fast` wall (the pre-commit hook's own target, L36's 30 s): 14.37, 14.62 and 14.78 s,
675 passed, at 1-minute loads of 6.9, 6.9 and 6.5 before each run; 14.2 s on the first reading at
load 2.0 to 2.9 (673 passed, before the two bench pins). The slice was 11.3 s warm when L36 set
the budget; the sweep is the slowest test but runs beside the rest: the same target with
the test deselected read 14.35 and 14.63 s and with it 14.52 and 14.17 s (alternating runs at
1-minute loads of 7.6 to 9.7), so its wall cost is inside the run-to-run noise. `make verify`: 996 passed in 78.25 s, coverage 97.48 percent (calc.py 99.20).

### Oracle bars (18-04)

The question (SC3, T2): does something that shares no code with the generator, a cutter built from
the textbook rack definitions with its neighbouring teeth, read every curve the generator produces
as the boundary the hob cuts, at a bar a millionth of a millimetre of tip radius breaks? The oracle
is `tests/trochoid_oracle.py` (stdlib `math`, imports nothing from `spur`); a point reads about 0
on the cut boundary, negative where the curve gouges, positive where it leaves material uncut.

Commands, from the repo root: `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov
--durations=0 -k t2_"` for the gate rows; `.venv/bin/python -m bench.trochoid oracle` for the whole
sweep product (about 4.3 minutes on 12 workers); `.venv/bin/python -m bench.trochoid oracle
--serial-slice 200` for the worker-count check.

#### Host state

- Machine: Apple M2 Max (`sysctl -n machdep.cpu.brand_string`); `bench.machine_facts()`:
  12 CPUs, arm64, 32.0 GiB RAM
- Python 3.12.13 (`.venv`); stdlib maths only, no kernel in this measurement
- HEAD: `16d82a4` (the commit that carries the tests and the `oracle` subcommand)
- Read 2026-10-08T02:31:13Z to 02:36:28Z (the pooled run, then the serial slice); the gate rows
  at about 02:37Z
- Load (1-minute): 42.89 before and 32.78 after the pooled run, 25.72 before and 14.18 after the
  serial slice, 8.61 before the gate rows. The host was loaded throughout (this session, other
  users); these are float residues, not timings, so load does not move them. The wall times
  below do move with it and are recorded as read.

#### The roll window: the first whole-product run failed, and why

The first pooled run, with the oracle as 18-01 committed it (roll searched over +-1 span of
2 pi / z), judged 10,399 cases in 274.9 s and **failed**: 3,244 of 10,326 trochoid curves read
beyond the 1e-9 mm bar, worst +0.6075 mm (14 teeth, module 10, 14.5 degrees, x -0.6, sharp
cutter; points at radii 63.8, 65.7 and 67.7 mm read +0.198, +0.470 and +0.608 mm, uncut). The
twelve gate rows were all clean at that window (worst 1.07e-14 mm), which is why the gate did not
show it.

The cause is the oracle's window, not the generator. The roll at which the cutter touches a
trochoid point is (a + w_c tan(beta)) / r; for the first failing point of that gear it is -0.473
rad against a window of +-0.449. Over the product the largest roll is **2.13 spans** (60 teeth,
module 10, 14.5 degrees, x -0.6, sharp cutter); 3,729 of the 10,399 cases need more than one
span; closed form (d cot(alpha) / (r * span), x -0.6, 14.5 degrees) bounds the box at about 2.3
spans. With the window at +-2 spans (diagnostic) the same 16 points read 1e-15 mm.

The window is now +-3 spans (1.3 times the box's bound). Grid check, 259 trochoid cases (every
40th of the product), window +-3 spans: a grid of 2001 / 3001 / 4001 / 6001 rolls reads worst
1.0e-13 / 1.1e-13 / 8.9e-14 / 9.2e-14 mm with none beyond the bar, so the grid stays 2001.

The same window had hidden the severed-tooth separation. 18-02 recorded that the neighbouring
teeth made no difference on a severed tooth; at +-3 spans the 6-tooth, 14.5 degree sharp-cutter
gear at x -0.6 reads **-0.138979 mm** on its one flank with the neighbours on and -2.1e-15 mm with
them off (x -0.5: -0.020103 against -8e-16; the 7-tooth, x -0.6 gear: -4.6e-16 either way), which
is what 18-RESEARCH described (0.141 and 0.0201 on its 21-point sets). 18-02's test was updated to
pin it.

#### The twelve gate rows

`tests/test_trochoid.py::test_t2_the_oracle_reads_every_gate_row_as_the_cut_boundary`, each row
asserting 16 points before reading them and the same readings, reversed, with the points reversed.

| row | join | tip radius used (mm) | worst reading (mm) | per module |
|---|---|---|---|---|
| tracer, 10 teeth | crossing | 0.38 | 9.99e-16 | 9.99e-16 |
| default gear, 19 teeth, module 1.75 | tangent | 0.5 | 2.72e-15 | 1.55e-15 |
| 17 teeth, just undercut | crossing | 0.38 | 1.50e-15 | 1.50e-15 |
| 18 teeth, just not | tangent | 0.38 | 1.22e-15 | 1.22e-15 |
| 7 teeth, x -0.6, sharp (thin positive waist) | crossing | 0 | 6.50e-16 | 6.50e-16 |
| 6 teeth, x -0.6, cap request 3.0 | crossing | 0.596 | 9.99e-16 | 9.99e-16 |
| 16 teeth, x 1.0, w_c = 0 | tangent | 0.25 | 7.22e-16 | 7.22e-16 |
| 16 teeth, x 1.0, w_c > 0 | tangent | 0.5 | 1.22e-15 | 1.22e-15 |
| 12 teeth, 32 degrees, cap request 3.0 (tip land nearly gone) | tangent | 0.007 | 1.18e-15 | 1.18e-15 |
| tracer at module 0.2 | crossing | 0.05 | 1.94e-16 | 9.71e-16 |
| 12 teeth, module 10, x 0.2, backlash 1.0 | tangent | 0.5 | 9.83e-15 | 9.83e-16 |
| 30 teeth, backlash 0.10 | tangent | 0.38 | 2.61e-15 | 2.61e-15 |

Worst over the twelve: **9.83e-15 mm** (module 10). Wall time at `-n0` (load 8.6): the twelve rows
0.42 to 0.45 s each, 5.2 s together; the controls 0.61 s; the tripwire 0.21 s; the T2 tests 6.0 s.
The commit that carried them, with the hook, took 15.0 s.

#### The whole sweep product (D-13: the full grid only in bench)

`bench.trochoid oracle`, 12 spawn workers, 257.4 s wall (load 42.9 before, 32.8 after):

- 10,399 cases judged: 10,326 trochoid curves of 16 points each, 73 severed teeth. Beyond the bar:
  **0**. Verdict ok, exit 0.
- Worst reading **2.985e-12 mm** (26 teeth, module 1, 20 degrees, x -0.6, backlash 0.10, tip
  radius 0.5 mm), 335 times under the bar. It is one of the two cases of the product inside the
  join band (18-03): the curve ends at the cutter's flank foot, 2 (tan(phi) - phi) = 2.44e-13 rad
  off the involute, times R = 12 mm: geometry, not noise. The other band case reads 1.106e-12 mm.
  Every other curve reads **1.594e-13 mm or less** (116 teeth, module 10, 14.5 degrees, x -0.6,
  tip radius 3 mm, trimmed), 6.3e3 times under the bar; 15 of 10,326 read above 1e-13 mm.
- The 73 severed teeth: the oracle reads a gouge (one flank, neighbours on) on **73 of 73**,
  shallowest -1.653e-03 mm, deepest -1.899 mm. The predicate and the oracle agree on every case.
- Serial slice (the backstop for "the reading does not depend on the worker count"): the first
  200 trochoid cases judged in-process, 42.7 s on one worker: worst 2.63897000341122582e-15 mm. The
  pooled run's worst over the same first 200 trochoid cases: 2.63897000341122582e-15 mm. Equal to
  every printed digit.

#### The negative controls (tracer gear unless stated)

| control | readings (mm) |
|---|---|
| involute between rb (4.6985) and the crossing radius (4.7256), at 0.25 / 0.5 / 0.75 of the way | -5.321e-03 / -3.695e-03 / -1.913e-03 |
| the trochoid carried past the crossing, 0.25 / 0.5 / 1.0 of the way to the flank foot | -9.649e-03 / -2.152e-02 / -5.192e-02 (18-RESEARCH: 5.19e-2 at the foot) |
| severed tooth (6 teeth, 14.5 degrees, x -0.6, sharp), one flank, neighbours on / off | -0.138979 / -2.07e-15 |
| the same tooth's other flank (mirror), neighbours on | -0.138979 |

Each is below -1e-4 mm (the severed ones below -1e-3), so an oracle that read 0 everywhere would
fail all three.

#### The tripwire and the T2 bar

The tracer gear's curve generated at tip radius 0.38 mm + 1e-6 mm and judged against the cutter at
0.38 mm reads **2.205e-07 mm**, 220 times the bar (unmoved: 1.0e-15 mm). The reading moves 0.2205
per mm of tip radius (2.2e-10 at 1e-9, 2.2e-8 at 1e-7, 2.2e-7 at 1e-6, 2.2e-5 at 1e-4 mm), as
18-RESEARCH predicted.

| bar | value | the two numbers | headroom |
|---|---|---|---|
| `ORACLE_BAR_MM` | 1e-9 mm | the generator's worst gap over the product (2.99e-12 mm at the band case; 1.6e-13 mm elsewhere; 9.8e-15 mm on the gate rows) and the oracle's resolution after golden-section refinement (about 1e-15 mm) | 335 over the product's worst, 6.3e3 outside the band, 1.0e5 on the gate rows; tripwire 220 over the bar |

No headroom is under 10x.

#### T3 and T4

**T3, freecad.gears at a sharp cutter (rho 0).** One-off run on 2026-10-08, never inside the
repository:

- Source: `https://github.com/looooo/freecad.gears`, `pygears/involute_tooth.py`
  (`InvoluteTooth.undercut_points`) with `pygears/__init__.py` and `pygears/_functions.py`, at commit
  `4cc4b1a233c232e15c3fdfb8a35909aa0d828796` (2026-09-15, "ruff refactoring", the last commit touching
  the file); repository HEAD `83ec154b1925347622b61812f75d2ed51e956b9f`; package 1.4.0; licence
  **GPL-3.0** (GitHub's licence API, `spdx_id`). The files were fetched with `gh api` into a scratch
  directory under the session's scratchpad (`spur-18-04-freecad/pygears/`), the script
  (`spur-18-04-t3/run.py`) kept in another, and run as `python -I run.py <dir>` with the repository's
  `.venv` (numpy, never declared by the repository). The code is plain numpy geometry; it was read
  before it was run.
- Cases: teeth 8, 10, 14; shift 0 and 0.3; backlash 0 and 0.10; module 1, 20 degrees; clearance 0.25
  (their root circle is this project's `r - (1.25 - x) m`, asserted to 1e-12 in the script). 200 samples
  each; 119 to 200 of them lie on the cutter flank (contact-normal angle at most pi/2 - alpha); five,
  evenly spread from the root circle to the flank foot, are recorded: **60 literals**, with their
  source, commit, licence and date, in `FREECAD_T3_POINTS`.
- Mapping, compared point for point through each row's own psi: `beta = atan((rf/d) tan(psi))`, the
  point `_trochoid_point(cutter(p, 0.0), beta)`. The half-angle is minus the polar angle of the
  library's returned point (at psi = 0 it equals this project's `pi/z - a/r`, checked by hand).
  The sample parameter psi is the library's own (`linspace(0, undercut_end, 200)`); recovering it as
  `acos((df/2)/R)` was tried first and turns a rounding error of 1e-16 in R into 1.5e-8 rad at the
  first point, so it was not used.
- Worst gaps: **1.776e-15 mm** in radius, **1.943e-16 rad** in half-angle (the prototype read
  2.66e-15 and 3.05e-16 over 1,972 points). Float level, as 18-RESEARCH expected: the frame
  conversion is right.
- Bars `T3_BAR_MM` and `T3_BAR_RAD` = 1e-12 each: ten times the larger gap is 1.8e-14, under the
  1e-12 cross-platform libm floor, so the floor is the bar. Headroom **563** (mm) and **5.1e3**
  (rad). The reference prints no resolution (float64 closed-form arithmetic on both sides).
- Tripwire: the same rows against a cutter of tip radius 1e-6 mm read **7.353e-07 mm** (7.4e5 times
  the radius bar) and **1.751e-07 rad** (1.8e5 times the angle bar).
- What it checks and does not: the rolling convention, the depth, the tip land and the backlash
  entry for a sharp corner; not the crossing (the library trims polylines), not rho above 0.
- No freecad.gears file entered the repository: no tracked path names `pygears` or `freecad`, and no
  tracked Python file imports `pygears` (checked by the plan's verify command).

**T4, KISSsoft's form diameter (D-15).** Zhang, "Methods to Determine Form Diameter on Hobbed
External Involute Gears", AGMA 18FTM02 (September 2018), Table 7 example 7, via Gear Solutions: 35
teeth, 22.5 degrees, dedendum factor 1.3 (x -0.05 on this project's 1.25 m rack), no protuberance, hob
tip radius 0.04, form diameter **4.1530 in** (four printed decimals). Diametral pitch 8 (module
3.175 mm, tip radius 1.016 mm) is **inferred**, not printed, and is recorded as inferred.

| | value |
|---|---|
| printed (KISSsoft) | 4.1530 in |
| the cutter-envelope junction here (`trochoid_root(cutter(p, 1.016))`, tangent join, xi 12.1 mm; `rb - rf` is -0.102 mm so `root_mode` would hand this gear back, hence the direct call) | 4.153036 in |
| gap | 3.593e-05 in |
| `T4_BAR_IN` (half the last printed digit) | 5e-05 in |
| headroom | **1.39** (the gap is 0.72 of the bar) |

The 1.39 is under the 10x line by construction, because the reference is rounded to four decimals,
and the human accepted exactly that at planning (D-15); it is recorded here as a known sub-10x bar
and was not escalated again. Tripwires: a tip radius 1e-3 in larger gives 4.153778 in, a gap of
**7.782e-04 in, 15.6 times the bar**; the two pitches either side of the inferred 8 miss 4.1530 by
5.514e-04 in (7.999, 11.0 times the bar) and 4.794e-04 in (8.001, 9.6 times), so the pitch that
reproduces the number is 8 to within 1e-4. The number is the cutter-envelope junction, never an
ISO 21771 form diameter: one tool-generated point is not parity (D-08, D-15, L08).

The four T3 and T4 tests run in 0.13 s at `-n0`. `make verify` after the tests' commit: 1016 passed
in 74.77 s, coverage 97.68 percent.

### Root-shape step (18-05, D-05)

The rule, written and committed before any table below existed (commit `8badc55`, `test(18-05): fix
the D-05 comparison line before measuring the root-shape step`): D-01's premise, about 0.14 m of root
shape between 17 and 18 teeth at 20 degrees, **holds when every 17- and 18-tooth row of the threshold
table has a gap within 25 percent either side of 0.14 m**, nominally 0.105 to 0.175 mm at module 1.
The figure is FEATURES' simulation as carried by 18-RESEARCH Pattern 8, which measured 0.145 m
(3 percent off). `bench.trochoid.premise_holds` carries the line and
`test_the_d05_premise_line_sits_25_percent_either_side_of_0_14_m` pins it at points 1e-4 m inside and
outside the band, never at its float64 edges. A figure outside it reopens the root-mode choice before
Phase 19 is planned.

The step is the largest-magnitude same-radius arc gap `R * (h_trochoid(R) - h_shipped(R))`, h the
half-angle from the tooth centre, between the trochoid outline (`trochoid_root(cutter(p, rho))`, the
involute above its junction) and the shipped analytic root zone rebuilt the way `model._outline`
builds it (the fillet arc `_fillet_corner` returns, the lead-in line, the involute from
`calc.spline_start`), read at 2,001 radii from the root circle to the higher of the two junctions,
sign kept (positive: the trochoid lies deeper into the tooth space). The maximum sits at the root
circle in every row, so each row states the tip radius asked for (which is also the `root_fillet`
requested), the shipped fillet actually used (rounded and capped to 0.45 of the root gap, so it is
below the request in the last four rows), what `root_mode(p, pr, requested="trochoid", rho=rho)`
answers and the join.

#### Host state

- Machine: Apple M2 Max (`bench.machine_facts()`: 12 CPUs, arm64, 32.0 GiB RAM)
- Python 3.12.13, cadquery 2.8.0, cadquery-ocp 7.9.3.1.1 (the pinned pair; the kernel is used only
  for the `Vector` arithmetic of `_fillet_corner`, not for a solid)
- HEAD `1db6fc6` (the commit that carries `bench.trochoid step`)
- Read 2026-10-08T02:50:48Z; 1-minute load 17.01 before, 17.81 after (a first run a minute earlier,
  2026-10-08T02:49:38Z, load 3.36 before, 4.85 after, printed the same figures to four decimals).
  These are geometry, not timings, so load does not move them; it is recorded because every
  section records it.

Command: `.venv/bin/python -m bench.trochoid step` from the repo root (exit 0).

Module 1, 20 degrees, no shift, no backlash, bore and recesses off.

**Table 1, the undercut threshold (teeth 16-19).** The O1 counterfactual: under D-02 the trochoid applies on both sides of 17/18 and the join only changes kind.

| teeth | tip radius rho | shipped fillet | root_mode | join | rb - rf | step (mm) | step / m | at R (mm) | trochoid junction R | spline start R |
|---|---|---|---|---|---|---|---|---|---|---|
| 16 | 0.38 | 0.38 | trochoid | crossing | +0.7675 | +0.1479 | +0.1479 | 6.7500 | 7.5181 | 7.5175 |
| 17 | 0.38 | 0.38 | trochoid | crossing | +0.7374 | +0.1463 | +0.1463 | 7.2500 | 7.9874 | 8.0100 |
| 18 | 0.38 | 0.38 | trochoid | tangent | +0.7072 | +0.1449 | +0.1449 | 7.7500 | 8.4586 | 8.5100 |
| 19 | 0.38 | 0.38 | trochoid | tangent | +0.6771 | +0.1433 | +0.1433 | 8.2500 | 8.9330 | 9.0100 |
| 16 | 0.471 | 0.471 | trochoid | crossing | +0.7675 | +0.1323 | +0.1323 | 6.7500 | 7.5175 | 7.6920 |
| 17 | 0.471 | 0.471 | trochoid | tangent | +0.7374 | +0.1328 | +0.1328 | 7.2500 | 7.9890 | 8.1920 |
| 18 | 0.471 | 0.471 | trochoid | tangent | +0.7072 | +0.1329 | +0.1329 | 7.7500 | 8.4637 | 8.6920 |
| 19 | 0.471 | 0.471 | trochoid | tangent | +0.6771 | +0.1325 | +0.1325 | 8.2500 | 8.9411 | 9.1920 |

**Table 2, the `rb = rf` crossover (teeth 40-43).** What a user stepping `teeth` meets under D-02.

| teeth | tip radius rho | shipped fillet | root_mode | join | rb - rf | step (mm) | step / m | at R (mm) | trochoid junction R | spline start R |
|---|---|---|---|---|---|---|---|---|---|---|
| 40 | 0 | 0 | trochoid | tangent | +0.0439 | +0.1471 | +0.1471 | 18.7500 | 19.0619 | 18.7939 |
| 41 | 0 | 0 | trochoid | tangent | +0.0137 | +0.1403 | +0.1403 | 19.2500 | 19.5540 | 19.2637 |
| 42 | 0 | 0 | radial (nothing radial to replace) | tangent | -0.0165 | +0.1340 | +0.1340 | 19.7500 | 20.0464 | 19.7500 |
| 43 | 0 | 0 | radial (nothing radial to replace) | tangent | -0.0466 | +0.1288 | +0.1288 | 20.2500 | 20.5392 | 20.2500 |
| 40 | 0.38 | 0.38 | trochoid | tangent | +0.0439 | +0.0838 | +0.0838 | 18.7500 | 19.1976 | 19.5100 |
| 41 | 0.38 | 0.38 | trochoid | tangent | +0.0137 | +0.0800 | +0.0800 | 19.2500 | 19.6926 | 20.0100 |
| 42 | 0.38 | 0.38 | radial (nothing radial to replace) | tangent | -0.0165 | +0.0765 | +0.0765 | 19.7500 | 20.1879 | 20.5100 |
| 43 | 0.38 | 0.38 | radial (nothing radial to replace) | tangent | -0.0466 | +0.0736 | +0.0736 | 20.2500 | 20.6833 | 21.0100 |
| 40 | 0.471 | 0.411 | trochoid | tangent | +0.0439 | +0.1214 | +0.1214 | 18.7500 | 19.2341 | 19.5720 |
| 41 | 0.471 | 0.406 | trochoid | tangent | +0.0137 | +0.1213 | +0.1213 | 19.2500 | 19.7297 | 20.0620 |
| 42 | 0.471 | 0.4 | radial (nothing radial to replace) | tangent | -0.0165 | +0.1221 | +0.1221 | 19.7500 | 20.2255 | 20.5500 |
| 43 | 0.471 | 0.396 | radial (nothing radial to replace) | tangent | -0.0466 | +0.1222 | +0.1222 | 20.2500 | 20.7215 | 21.0420 |

Rule applied: D-01's premise holds when every 17- and 18-tooth row of the threshold table has a gap
within 25 percent either side of 0.14 m (0.1050 to 0.1750 mm at module 1). The four rows are 0.1463
and 0.1449 mm at tip radius 0.38 and 0.1328 and 0.1329 mm at 0.471.

**D-01 premise holds**

What the figures say beyond the verdict: the step barely moves across the threshold itself (16 to 19
teeth: 0.1479 to 0.1433 mm at 0.38), so it is not a feature of the 17/18 edge. The crossover rows are
the step a user meets under D-02: the request is ignored and warned at 42 teeth and above (`nothing
radial to replace`), so stepping `teeth` from 41 to 42 turns the trochoid off and the part moves by
the 41-tooth gap, **0.1403 mm at a sharp cutter and no fillet, 0.0800 mm at 0.38, 0.1213 mm at
0.471** (0.1471, 0.0838 and 0.1214 at 40 teeth). The 42- and 43-tooth rows print the generator's
curve anyway (`trochoid_root` has no `rb` test of its own) to show that the gap does not vanish at
the edge; no user sees those curves.

Human's reading (2026-10-08): **d05-hold**. The human was shown both tables and the verdict and
answered "d05-hold": the premises hold, and Phase 19 is planned on D-01 (the root-mode option,
default off) and D-02 (the trochoid only where `rb > rf`) as decided. The crossover step stays a
visible discontinuity in the opt-in mode, on record above for Phase 19's Lxx: 0.1403 mm at a sharp
cutter and no fillet, 0.0800 mm at 0.38, 0.1213 mm at 0.471, all at 41 teeth.

Open note, not resolved here: one figure does not reconcile with 18-RESEARCH. Pattern 8's prototype
quoted the sharp-cutter crossover as "rho 0 -> -0.1885"; this run reads **+0.1403 mm** at rho 0, 41
teeth (and +0.1471 mm at 40 teeth), with the opposite sign. Its other crossover figures match to
four decimals (0.0800 and 0.1213 at 41 teeth), so the difference is confined to the rho 0 row.
ASSUMPTION: the prototype paired rho 0 with a non-zero shipped fillet (the trochoid of a sharp
cutter against a filleted shipped root), where this table's rho 0 row sets the shipped fillet to 0
too. Not checked, because the prototype's script is not in the repository and the verdict does not
turn on it: the premise rule reads only the 17- and 18-tooth rows of the threshold table, and none
of them uses rho 0. If Phase 19 prices the sharp-cutter crossover, it should re-derive this row
rather than quote either figure.

### Per-call cost (18-05, D-14)

How long the maths takes per call, read the way `derive()`'s docstring reads it, so Phase 19 can
price what enters the keystroke path. **No budget is set**; Phase 19 decides what enters the keystroke
path from these numbers.

#### Host state

- Machine: Apple M2 Max (12 CPUs, arm64, 32.0 GiB RAM), Python 3.12.13
- HEAD `1db6fc6`; five measurements one after another on 2026-10-08, UTC times below
- The host was busy: macOS Spotlight indexing (`mdworker_shared`) held several cores, and the
  1-minute load read 14.4 to 16.0 across the five measurements (3.4 a few minutes earlier, before the
  commit hook's eight test workers ran). No quiet host was waited for (D-14 asks for the load beside
  the figure, not for a quiet bar), so each figure is an upper bound for the same code on an idle
  machine.

Each: `.venv/bin/python -m timeit -r 5 -s "<setup>" "<statement>"`, best of 5 (the per-loop time of
the fastest repeat). Default `GearParams()` (19 teeth, module 1.75, 25 degrees, backlash 0.1, bore as
shipped) except the last row; `cutter` is built in the setup, so the `trochoid_root` rows are the
solve alone. The tracer gear is 10 teeth, module 1, 20 degrees, no shift, no backlash, bore off, the
crossing join.

| call | read (UTC) | 1-minute load before -> after | best of 5 |
|---|---|---|---|
| `derive(p)` | 2026-10-08T02:50:24Z | 14.38 -> 14.75 | 14.7 usec |
| `root_mode(p, pr)` (nothing requested: what every present caller pays) | 2026-10-08T02:50:27Z | 14.75 -> 14.75 | 362 nsec |
| `root_mode(p, pr, requested="trochoid", rho=0.5)` (default gear, tangent) | 2026-10-08T02:50:29Z | 14.75 -> 15.49 | 33.7 usec |
| `trochoid_root(c)`, default gear, tip radius 0.38 (tangent) | 2026-10-08T02:50:32Z | 15.49 -> 15.49 | 30.7 usec |
| `trochoid_root(c)`, tracer gear, tip radius 0.38 (crossing) | 2026-10-08T02:50:34Z | 15.49 -> 16.01 | 88.9 usec |

The crossing costs about three times the tangent solve (two 60-step bisections against none: 88.9
against 30.7 usec here). Asking `root_mode` for a trochoid on the default gear costs 33.7 usec, and
asking for nothing costs 0.362 usec. `derive(p)` read 14.7 usec against the 11.5 usec its docstring
carried: 18-RESEARCH read 14.5 usec at load 14.33 (2026-10-07) and PITFALLS 20.4 at about 6.8, so the
old figure moves with the host and nothing measured here separates a regression from load; the
docstring now carries the number, the load and the date together.

## Trochoid in the part (Phase 19)

What the hob's trochoid root costs once it is in the part, in the order the phase builds it: the
gate's before-figure at the phase base (19-01, this subsection first), the tip chamfer's kernel
limit across the spline-to-spline junction (19-01), and the heaviest low-tooth rows against
`SPUR_BUILD_TIMEOUT` (19-01); the later plans (19-02, 19-09) append their own subsections below.
Each subsection carries its own host state, because every number belongs to the load it was read
at. The kernel subsections are measured on a trochoid outline `bench/trochoid_part.py` builds
itself from the Phase 18 `RootCurve` and runs through the shipped pipeline steps (recesses, bore,
keyway, body cutout), before any schema change: ROADMAP "Order inside the phase", PITFALLS 18, the
`bench/tip_chamfer_spike.py` precedent (L29).

### Gate baseline (19-01)

The gate's before-figure for Phase 19, taken at the phase base before any edit: `make verify`
four times in a row (three green readings were wanted, and one run failed), nothing else
CPU-heavy started by this session. Each run was `/usr/bin/time -p make verify`, `uptime` read
immediately before and after. The phase base is `df4749e`; HEAD for these runs was `29c742c`,
which differs from it by planning documents only (no file under `src/`, `tests/` or `bench/`).

#### Host state

- Machine: Apple M5 Max (`sysctl -n machdep.cpu.brand_string`); `bench.machine_facts()`:
  18 CPUs, arm64, 64.0 GiB RAM
- Python 3.12.15 (`.venv`), cadquery 2.8.0, cadquery-ocp 7.9.3.1.1 (the pinned pair)
- Read 2026-10-08, 22:10 to 22:14 local time (16:10 to 16:14 UTC), ten users logged in
- The 1-minute load is dominated by the run itself (eight xdist workers plus the gate's
  other steps): the "after" of one run is mostly the "before" of the next, so the loads below
  are not independent readings. Before the first run, with nothing of this session running, the
  1-minute load read 3.16.

| Run | Result line | `real` (s) | 1-minute load before -> after |
|---|---|---|---|
| 1 | `1023 passed in 53.89s` | 54.60 | 3.16 -> 16.71 |
| 2 | `1 failed, 1022 passed in 53.61s` (a flake, below) | 54.04 | 16.71 -> 22.09 |
| 3 | `1023 passed in 52.10s` | 52.53 | 22.09 -> 24.94 |
| 4 | `1023 passed in 51.09s` | 51.53 | 11.75 -> 24.80 (a 20 s pause preceded it) |

Mean of the three green runs: `real` 52.89 s (54.60, 52.53, 51.53), pytest 52.36 s (53.89, 52.10,
51.09).

Run 2 failed `tests/test_pool.py::test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced`
on worker `gw0`, with `multiprocessing.resource_tracker.ReentrantCallError` and the
`UserWarning: ResourceTracker called reentrantly` it raises under `filterwarnings = ["error"]`,
the known flake. The whole log is kept at
`.planning/phases/19-the-trochoid-in-the-part/investigation/19-01-gate-flake.log` as evidence for
19-03. Nothing was changed between runs 1, 2, 3 and 4.

For the record, not for a conclusion: L34 read 63.555 s on an Apple M2 Max with 12 CPUs and set
the bar at 66 s on that host; 19-RESEARCH F10 read 46.21 s wall (1023 passed in 45.59s) on this
host at a 1-minute load of 6.12 before and 15.73 after. 19-09 measures the phase's delta against
the readings above, on this host, in one session.

### Chamfer across the junction (19-01)

L29's kernel law on the hob root: the tip chamfer's footprint on the end face reaches inward
from the tip circle, and the kernel cannot carry it from one spline onto another. On the radial
outline that boundary was the spline start; on the trochoid outline it is the junction between
the root spline and the involute spline, `R_join = RootCurve.points[-1][0]`. `python -m
bench.trochoid_part chamfer` builds each of 14 rows (seven gears at tip radius 0 and 0.5 mm,
typed out in `CHAMFER_ROWS`, every one a trochoid gear), bisects the chamfer size on the unchamfered
part's tip arcs for 20 halvings between 0 and 0.45 x face_width (3.375 mm), and compares the
largest size that built with `pred = ra - R_join`. The verdict is never optimistic: only a last
building size more than `TIP_CHAMFER_MARGIN` (0.001 mm) inside `pred` fails. Every part is one
valid solid, its tooth-0 root edges are selected by position with the count asserted equal to
2 x teeth, and the Phase 18 oracle reads them with the tip radius the cutter used (no bar is
applied here: 19-02 sets it). The script's output follows verbatim.

#### Host state

- Machine: 18 CPUs, arm64, 64.0 GiB RAM
- Python: 3.12.15
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `29c742c`
- Read 2026-10-08T16:18:28Z to 2026-10-08T16:23:12Z
- Load averages at start: 8.92, 10.72, 9.15; at end: 9.61, 8.53, 8.48

#### Bisection (20 halvings between 0 and 0.45 x face_width)

| Gear | Tip radius (mm) | Join | R_join (mm) | pred = ra - R_join | last ok | first fail | last ok - pred | Verdict | Binding cap | Worst oracle (mm) |
|---|---|---|---|---|---|---|---|---|---|---|
| default 19 teeth, m 1.75, 25 deg, x 0 | 0 | tangent | 15.1805 | 3.1944892 | 3.1944884 | 3.1944916 | -7.71e-07 | on the law | ra - r | 1.35e-05 |
| default 19 teeth, m 1.75, 25 deg, x 0 | 0.5 | tangent | 15.2788 | 3.0961925 | 3.0961908 | 3.0961940 | -1.73e-06 | on the law | ra - r | 2.20e-05 |
| 100 teeth, m 1, 14.5 deg, x -0.6 | 0 | tangent | 48.6785 | 1.7215252 | 1.7215244 | 1.7215276 | -8.65e-07 | on the law | ra - r | 5.91e-06 |
| 100 teeth, m 1, 14.5 deg, x -0.6 | 0.5 | tangent | 48.8589 | 1.5410770 | 1.5410739 | 1.5410771 | -3.06e-06 | on the law | ra - r | 9.50e-05 |
| 30 teeth, m 1, 14.5 deg, x -0.6 | 0 | crossing | 14.5916 | 0.8084213 | 0.8233534 | 0.8233566 | +1.49e-02 | conservative | ra - r | 2.44e-05 |
| 30 teeth, m 1, 14.5 deg, x -0.6 | 0.5 | crossing | 14.5508 | 0.8492071 | 2.2499979 | 2.2500011 | +1.40e+00 | conservative | ra - r | 1.23e-04 |
| 12 teeth, m 1, 20 deg, x 0 | 0 | crossing | 5.6756 | 1.3243676 | 1.3243654 | 1.3243686 | -2.23e-06 | on the law | ra - r | 1.97e-05 |
| 12 teeth, m 1, 20 deg, x 0 | 0.5 | crossing | 5.6457 | 1.3542630 | 1.3542602 | 1.3542634 | -2.80e-06 | on the law | ra - r | 3.99e-05 |
| 10 teeth, m 1, 20 deg, x 0 | 0 | crossing | 4.7567 | 1.2433329 | 2.2499979 | 2.2500011 | +1.01e+00 | conservative | ra - r | 2.15e-05 |
| 10 teeth, m 1, 20 deg, x 0 | 0.5 | crossing | 4.7174 | 1.2825685 | 1.2825680 | 1.2825712 | -5.13e-07 | on the law | ra - r | 3.94e-05 |
| 8 teeth, m 1, 20 deg, x 0 | 0 | crossing | 3.8448 | 1.1552447 | 1.2656250 | 1.2656282 | +1.10e-01 | conservative | ra - r | 2.29e-05 |
| 8 teeth, m 1, 20 deg, x 0 | 0.5 | crossing | 3.7960 | 1.2039992 | 2.2499979 | 2.2500011 | +1.05e+00 | conservative | ra - r | 3.66e-05 |
| 6 teeth, m 1, 14.5 deg, x 0 | 0 | crossing | 3.0994 | 0.9006385 | 0.9006364 | 0.9006397 | -2.04e-06 | on the law | ra - R_join | 2.99e-05 |
| 6 teeth, m 1, 14.5 deg, x 0 | 0.5 | crossing | 3.0183 | 0.9816865 | 1.3320547 | 1.3320580 | +3.50e-01 | conservative | ra - R_join | 4.47e-05 |

First-failure reasons: default 19 teeth, m 1.75, 25 deg, x 0 @ 0: Standard_Failure; default 19 teeth, m 1.75, 25 deg, x 0 @ 0.5: Standard_Failure; 100 teeth, m 1, 14.5 deg, x -0.6 @ 0: Standard_Failure; 100 teeth, m 1, 14.5 deg, x -0.6 @ 0.5: Standard_Failure; 30 teeth, m 1, 14.5 deg, x -0.6 @ 0: invalid; 30 teeth, m 1, 14.5 deg, x -0.6 @ 0.5: Standard_Failure; 12 teeth, m 1, 20 deg, x 0 @ 0: invalid; 12 teeth, m 1, 20 deg, x 0 @ 0.5: invalid; 10 teeth, m 1, 20 deg, x 0 @ 0: invalid; 10 teeth, m 1, 20 deg, x 0 @ 0.5: invalid; 8 teeth, m 1, 20 deg, x 0 @ 0: invalid; 8 teeth, m 1, 20 deg, x 0 @ 0.5: invalid; 6 teeth, m 1, 14.5 deg, x 0 @ 0: invalid; 6 teeth, m 1, 14.5 deg, x 0 @ 0.5: invalid

Binding cap is ra - R_join on: 6 teeth, m 1, 14.5 deg, x 0 @ 0; 6 teeth, m 1, 14.5 deg, x 0 @ 0.5.
Verdict: law holds -- 8 rows on the law, 6 conservative (30 teeth, m 1, 14.5 deg, x -0.6 @ 0; 30 teeth, m 1, 14.5 deg, x -0.6 @ 0.5; 10 teeth, m 1, 20 deg, x 0 @ 0; 8 teeth, m 1, 20 deg, x 0 @ 0; 8 teeth, m 1, 20 deg, x 0 @ 0.5; 6 teeth, m 1, 14.5 deg, x 0 @ 0.5).

The law holds across the junction, to the bisection's resolution. On the 8 rows on the law, the
largest chamfer that built sits 0.5 to 3.1 microns inside `pred` and the first that failed
sits 0.1 to 2.7 microns past it, a bracket 3.2e-6 mm wide on every row (3.375 mm / 2^20), so
the kernel's boundary is `ra - R_join` to the last bisection step, the same "within about 2
microns" L29 read at the spline start on five of six configurations (there the bracket was
2.9e-6 mm). RESEARCH F5's 14 to 16 step scratch readings (3.19434 against 3.1945 on the default
gear, 1.7215 on 100 teeth) resolved about 2e-4 mm; these are 20 steps on the same rows and agree.
Six rows are conservative, as L29's sixth was: the same six F5 named (10 teeth at tip radius 0,
8 teeth at both, 6 teeth at 0.5, 30 teeth at both) built past `pred`, by 0.015 mm (30 teeth, tip
radius 0) up to 1.40 mm (30 teeth, tip radius 0.5). Three of them (30 teeth at 0.5, 10 teeth at
0, 8 teeth at 0.5) stopped at 2.25 mm, which is the whole tooth depth `ra - rf` of a module-1 gear;
ASSUMPTION: that is the footprint reaching the root circle, not isolated here. A conservative row
costs a user nothing unless `ra - R_join - TIP_CHAMFER_MARGIN` is the cap in force: of the 14 rows
that is only the two 6-tooth rows (`ra - R_join` against `ra - r` = 1.0 mm there, the junction
above the pitch circle at R_join 3.0994 and 3.0183 mm against r 3.0), and the one of the two that
is conservative (tip radius 0.5) is conservative by 0.35 mm. Everywhere else `ra - r` or
0.45 x face_width binds first, so those rows prove the law is not optimistic, not that it
binds. The worst oracle reading on an unchamfered root is 1.23e-04 mm (30 teeth, module 1,
tip radius 0.5), against the 1.79e-4 mm per module RESEARCH F3 read as the worst of the 5,159
swept gears; no bar is applied in this plan.


### Heaviest low-tooth rows (19-01)

ROADMAP success criterion 4: what the hob root costs at the heaviest gear a `root_shape="trochoid"`
request can still change, before the field exists. The trochoid applies only where `rb > rf`
(`root_mode` ignores the request otherwise, 18 D-02), and with `rb = r cos(alpha)` and
`rf = r - m (1.25 - x)` that reads `z < 2 (1.25 - x) / (1 - cos(alpha))`, which is 116.1 at
14.5 degrees and profile shift -0.6, the field's extremes. So `CORNER` is 116 teeth, 14.5 degrees,
profile shift -0.6, and every row of `bench/sweeps/composed.json` (18 rows: 200 teeth, modules 1.75
and 10, every cutout family, hex and keyed bores, the tip chamfer at each module's largest, both
recesses) is moved to it, keeping its other keys. Two lighter module-10 rows are added: the bare
corner gear and the corner gear with `tip_chamfer=3` and both recesses. Each row is built and
exported twice, as a worker pays it (a cold build with no cache, then the fine STL and the STEP
export, each timed with `time.perf_counter()`): radial through `model._build_checked`, trochoid
through `trochoid_part` with the cutter's tip radius at `root_fillet` (the cap applied by the cutter,
as 19-04 will pass it). A cold request is the build plus the slower of the two exports, the rule of
`bench.build_time.Timing.worst_request`, against `SPUR_BUILD_TIMEOUT` = 30 s. The last column is the
Phase 18 oracle's worst reading over the built trochoid part's tooth-0 root edges, so the timed part
is shown to be the oracle's root. 20 rows were tried: 17 validated and are timed as a pair, three are
refused by `GearParams` at the corner and are printed with their sentences below the table. The
RESEARCH A12 plan to replace refused hole rows did not arise: all five 60-hole rows validate at the
corner and are timed. The script's output follows verbatim.

#### Host state

- Machine: 18 CPUs, arm64, 64.0 GiB RAM
- Python: 3.12.15
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `7a0268f`
- Read 2026-10-08T16:28:04Z to 2026-10-08T16:33:04Z
- Load averages at start: 4.86, 7.00, 7.87; at end: 9.48, 10.47, 9.41

SPUR_BUILD_TIMEOUT: 30 s; a cold request is one build plus the slower of the fine STL and the STEP export.

#### Timings

| Parameter set | Mode | Build (s) | Fine STL (s) | STEP (s) | Build + slower export (s) | Trochoid / radial | Inside 30 s | Oracle, tooth 0 (mm) |
|---|---|---|---|---|---|---|---|---|
| teeth=116 module=1.75 bore_hex=43.35 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | radial | 10.03 | 0.36 | 0.33 | 10.40 | -- | yes | -- |
| teeth=116 module=1.75 bore_hex=43.35 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | trochoid | 11.04 | 0.41 | 0.30 | 11.45 | 1.10 | yes | 1.12e-04 |
| teeth=116 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | radial | 9.14 | 0.42 | 0.38 | 9.56 | -- | yes | -- |
| teeth=116 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | trochoid | 10.71 | 0.69 | 0.66 | 11.41 | 1.19 | yes | 1.12e-04 |
| teeth=116 module=10 bore_hex=43.35 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | radial | 12.21 | 0.63 | 0.43 | 12.85 | -- | yes | -- |
| teeth=116 module=10 bore_hex=43.35 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | trochoid | 13.97 | 0.69 | 0.43 | 14.66 | 1.14 | yes | 2.79e-04 |
| teeth=116 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | radial | 13.16 | 0.66 | 0.46 | 13.82 | -- | yes | -- |
| teeth=116 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | trochoid | 14.28 | 0.70 | 0.43 | 14.98 | 1.08 | yes | 2.79e-04 |
| teeth=116 module=1.75 bore_hex=156.3 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | radial | 11.10 | 0.38 | 0.30 | 11.48 | -- | yes | -- |
| teeth=116 module=1.75 bore_hex=156.3 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | trochoid | 16.20 | 0.41 | 0.27 | 16.61 | 1.45 | yes | 1.12e-04 |
| teeth=116 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | radial | 4.95 | 1.04 | 0.30 | 5.99 | -- | yes | -- |
| teeth=116 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | trochoid | 6.07 | 1.06 | 0.20 | 7.13 | 1.19 | yes | 1.12e-04 |
| teeth=116 module=10 bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | radial | 4.21 | 0.70 | 0.23 | 4.91 | -- | yes | -- |
| teeth=116 module=10 bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | trochoid | 5.53 | 0.75 | 0.19 | 6.28 | 1.28 | yes | 2.79e-04 |
| teeth=116 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | radial | 4.33 | 0.72 | 0.21 | 5.05 | -- | yes | -- |
| teeth=116 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | trochoid | 5.94 | 0.80 | 0.18 | 6.74 | 1.34 | yes | 2.79e-04 |
| teeth=116 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hex_cell=3 hex_wall=0.4 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | radial | 7.37 | 0.54 | 0.42 | 7.91 | -- | yes | -- |
| teeth=116 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hex_cell=3 hex_wall=0.4 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | trochoid | 9.23 | 0.61 | 0.39 | 9.85 | 1.24 | yes | 1.12e-04 |
| teeth=116 module=10 bore_hex=200 hex_cell=3 hex_wall=5 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | radial | 9.33 | 0.71 | 0.47 | 10.03 | -- | yes | -- |
| teeth=116 module=10 bore_hex=200 hex_cell=3 hex_wall=5 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | trochoid | 9.88 | 0.76 | 0.48 | 10.64 | 1.06 | yes | 2.79e-04 |
| teeth=116 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hex_cell=3 hex_wall=5 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | radial | 8.02 | 0.76 | 0.79 | 8.81 | -- | yes | -- |
| teeth=116 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hex_cell=3 hex_wall=5 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | trochoid | 9.51 | 0.79 | 0.44 | 10.30 | 1.17 | yes | 2.79e-04 |
| teeth=116 module=1.75 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | radial | 4.50 | 0.64 | 0.29 | 5.13 | -- | yes | -- |
| teeth=116 module=1.75 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | trochoid | 4.04 | 0.51 | 0.19 | 4.54 | 0.88 | yes | 1.12e-04 |
| teeth=116 module=1.75 hole_count=60 hole_d=1 hole_circle_d=183.4 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | radial | 1.33 | 1.34 | 0.25 | 2.67 | -- | yes | -- |
| teeth=116 module=1.75 hole_count=60 hole_d=1 hole_circle_d=183.4 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | trochoid | 1.39 | 1.08 | 0.16 | 2.47 | 0.93 | yes | 1.12e-04 |
| teeth=116 module=10 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | radial | 8.12 | 0.60 | 0.39 | 8.72 | -- | yes | -- |
| teeth=116 module=10 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | trochoid | 9.41 | 0.63 | 0.37 | 10.04 | 1.15 | yes | 2.79e-04 |
| teeth=116 module=1.75 hex_cell=3 hex_wall=0.4 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | radial | 2.85 | 0.53 | 0.37 | 3.37 | -- | yes | -- |
| teeth=116 module=1.75 hex_cell=3 hex_wall=0.4 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | trochoid | 4.06 | 0.64 | 0.37 | 4.69 | 1.39 | yes | 1.12e-04 |
| teeth=116 pressure_angle=14.5 profile_shift=-0.6 module=10 | radial | 0.76 | 0.68 | 0.16 | 1.44 | -- | yes | -- |
| teeth=116 pressure_angle=14.5 profile_shift=-0.6 module=10 | trochoid | 0.82 | 0.79 | 0.14 | 1.60 | 1.11 | yes | 2.79e-04 |
| teeth=116 pressure_angle=14.5 profile_shift=-0.6 module=10 tip_chamfer=3 recess_sides=both | radial | 4.66 | 0.69 | 0.21 | 5.36 | -- | yes | -- |
| teeth=116 pressure_angle=14.5 profile_shift=-0.6 module=10 tip_chamfer=3 recess_sides=both | trochoid | 3.68 | 0.75 | 0.18 | 4.43 | 0.83 | yes | 2.79e-04 |

Refused by `GearParams` at the corner, not timed:

- `teeth=116 module=1.75 bore_hex=200 hex_cell=3 hex_wall=0.4 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6`: Hex bore is too large for the root diameter: its corners (231.11 mm across) must stay 0.4 mm inside the root circle (196.53 mm); reduce bore_hex. No whole honeycomb cell fits between 116.42 and 97.86 mm from the axis (hex_wall outside the bore mouth and inside the root circle): a 3 mm cell reaches 1.73 mm from its centre; reduce hex_cell or hex_wall.
- `teeth=116 module=1.75 bore_hex=200 recess_sides=both bore_chamfer=0.4 pressure_angle=14.5 profile_shift=-0.6`: Hex bore is too large for the root diameter: its corners (231.11 mm across) must stay 0.4 mm inside the root circle (196.53 mm); reduce bore_hex.
- `teeth=116 module=1.75 bore_d=200 bore_flat=150 keyway_width=3 keyway_depth=1.4 recess_sides=both bore_chamfer=0.4 pressure_angle=14.5 profile_shift=-0.6`: Bore is too large for the root diameter. Keyway is too deep for the root diameter: its floor corners reach 202.97 mm across, which must stay 0.4 mm inside the root circle (196.53 mm); reduce keyway_depth or keyway_width.

**Heaviest:** teeth=116 module=1.75 bore_hex=156.3 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 (trochoid) -- 16.61 s of 30 s.
**Heaviest trochoid:** teeth=116 module=1.75 bore_hex=156.3 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 (trochoid) -- 16.61 s of 30 s.


`uptime` read 4.86 7.00 7.87 at 22:28 local time and 9.48 10.47 9.41 at 22:33, the same figures the
script printed. The 1-minute load was above 1.5 for the whole run (the host carried other work, and
the run itself adds its own build and export threads), so each figure is an upper bound for this host.

Every one of the 17 pairs is inside 30 s, on both paths. The heaviest trochoid row is the 116-tooth,
module-1.75 gear with a 156.3 mm hex bore, 60 holes of 1 mm on a 183.4 mm circle, the tip chamfer at
1.75 mm and both recesses: 16.20 s to build plus 0.41 s (STL) and 0.27 s (STEP), 16.61 s for the
request, 13.39 s of margin to 30 s, and 1.45 times its own radial row (11.48 s); it is also the heaviest
row overall, radial rows included, which the keyed 32-spoke module-10 row (13.82 s radial, 14.98 s
trochoid, 1.08 times) and the hex-bore 32-spoke module-10 row (12.85 s, 14.66 s, 1.14 times) follow.
RESEARCH F7's scratch run read the keyed 32-spoke module-10 row at 11.12 s radial and 12.24 s
trochoid (host load 6.5 to 11); this run reads 13.82 s and 14.98 s, 24 % and 22 % higher at a
1-minute load of 4.9 to 9.5, with no cause isolated, and the same ratio to two digits (1.10 there,
1.08 here). The trochoid path costs more than the radial on 14 of the 17 pairs and less on three (0.83, 0.88 and
0.93 times: the module-10 and module-1.75 chamfer-and-recess rows and the module-1.75 60-hole row
without a bore, each a 2.5 to 5.4 s request); the ratio ranges from 0.83 to 1.45, and the five largest
(1.45, 1.39, 1.34, 1.28, 1.24) are all hole or honeycomb rows. This names the trochoid's share of each
row and does not extrapolate to concurrent load: L37 owns that contract. L37's 29.42 s row (the
200-tooth, module-10 keyed 32-spoke composition, read on the 12-CPU M2 Max) is untouched by
construction: at 200 teeth `rb <= rf`, so a trochoid request is ignored and warned (18 D-02) and its
cold request stays as L37 records it. The three refusals are the rows whose 200 mm hex bore or 200 mm
round bore reaches the 196.53 mm root circle of a 116-tooth module-1.75 gear; they are `GearParams`
refusals, not trochoid ones, and honeycomb, hex bore and keyed bore are all timed on the other rows.
The oracle reads every trochoid row's root at 1.12e-04 mm (module 1.75, 6.4e-5 per module) or
2.79e-04 mm (module 10, 2.79e-5 per module), inside the 1.3e-5 to 1.8e-4 per module RESEARCH F3 read
over the swept gears; no bar is applied in this plan.


### Spline deviation and the kernel bar (19-02)

Two research files measured the shipped involute flank's spline deviation a factor of hundreds
apart (SUMMARY correction 16: STACK 6.0e-5 and 1.0e-4 mm, PITFALLS 0.13 and 0.004 micrometres), so
neither number could be a bar. `python -m bench.trochoid_part spline` reconciles them. **Method A**
is the distance from a sample of the kernel spline to the nearest *vertex* of a 20,001-point
reference; **method B** is the distance to the reference *polyline*, segment-wise. The reference
for the hob root is `_trochoid_point` at 20,001 contact-normal angles, uniform in tan(beta) like
the 16 points of `RootCurve`, from the root circle to the junction. The kernel tier is the Phase
18 oracle (`tests/trochoid_oracle.clearance`) on `Edge.positionAt` positions of the built solid's
tooth-0 root edges, read beside method B on the very same positions. Exit 0 means method B
reproduced STACK's three trochoid figures to within one in the third digit and the oracle agreed
with method B on all seven rows to the same standard.

#### Host state

- Machine: 18 CPUs, arm64, 64.0 GiB RAM
- Python: 3.12.15
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `88c5ec5`
- Read 2026-10-08T16:56:53Z to 2026-10-08T16:58:05Z
- Load averages at start: 6.89, 6.37, 7.89; at end: 3.96, 5.57, 7.46

Positions per spline: 2001 for the deviation figures (method B converges there, see the table below), 401 per root edge for the oracle against method B on the same positions, 41 for the 19-01 oracle reading. Reference: 20,001 points.

#### Reconciliation: STACK's trochoid figures (module 1, mm)

| Gear | Join | STACK | Method B | B off by (units of the 3rd digit) | Method A | Half the reference's largest vertex gap |
|---|---|---|---|---|---|---|
| 8 teeth, m 1, 20 deg, x 0, tip radius 0.38 | crossing | 3.58e-05 | 3.5807e-05 | 0.07 | 5.1845e-05 | 3.78e-05 |
| 10 teeth, m 1, 20 deg, x 0, tip radius 0.38 | crossing | 3.89e-05 | 3.8933e-05 | 0.33 | 5.2097e-05 | 3.74e-05 |
| 14 teeth, m 1, 20 deg, x 0, tip radius 0.38 | crossing | 3.99e-05 | 3.9847e-05 | 0.53 | 5.2250e-05 | 3.62e-05 |

#### Reconciliation: STACK's shipped-flank figures (mm)

| Gear | STACK | Reference spacing | Method A | Half the largest vertex gap | Method B |
|---|---|---|---|---|---|
| z=12, m=1, 20 deg | 6.0e-05 | i^1.5 (the shipped spline's) | 5.722e-05 | 5.820e-05 | 1.701e-06 |
| z=12, m=1, 20 deg | 6.0e-05 | uniform in radius | 3.824e-05 | 3.880e-05 | 1.701e-06 |
| z=12, m=1, 25 deg | 6.0e-05 | i^1.5 (the shipped spline's) | 6.221e-05 | 6.353e-05 | 1.536e-06 |
| z=12, m=1, 25 deg | 6.0e-05 | uniform in radius | 4.192e-05 | 4.235e-05 | 1.536e-06 |
| z=8, m=1, 25 deg | -- | i^1.5 (the shipped spline's) | 6.903e-05 | 7.055e-05 | 2.373e-05 |
| z=8, m=1, 25 deg | -- | uniform in radius | 4.639e-05 | 4.703e-05 | 2.373e-05 |
| z=19, m=1.75, 25 deg (default gear) | 1.0e-04 | i^1.5 (the shipped spline's) | 1.310e-04 | 1.343e-04 | 3.343e-06 |
| z=19, m=1.75, 25 deg (default gear) | 1.0e-04 | uniform in radius | 8.854e-05 | 8.956e-05 | 3.343e-06 |

#### Method B against the number of positions (14 teeth, m 1, 20 deg, x 0)

| Positions per root edge | Method B (mm) |
|---|---|
| 201 | 3.9675e-05 |
| 2001 | 3.9847e-05 |
| 20001 | 3.9847e-05 |

#### Kernel tier on seven rows (mm unless stated)

| Row | Tip radius used | Join | Oracle, 41 positions | Oracle | Method B, same positions | Oracle vs B (units of the 3rd digit) | Method B, converged | Converged per module | 41-position reading / converged |
|---|---|---|---|---|---|---|---|---|---|
| default 19 teeth, m 1.75, 25 deg, x 0 | 0.5 | tangent | 2.1967e-05 | 2.2595e-05 | 2.2596e-05 | 0.01 | 2.2610e-05 | 1.2920e-05 | 0.97 |
| 8 teeth, m 1, 20 deg, x 0 | 0.38 | crossing | 3.5473e-05 | 3.5794e-05 | 3.5795e-05 | 0.01 | 3.5807e-05 | 3.5807e-05 | 0.99 |
| 10 teeth, m 1, 20 deg, x 0 | 0.38 | crossing | 3.8193e-05 | 3.8929e-05 | 3.8929e-05 | 0.01 | 3.8933e-05 | 3.8933e-05 | 0.98 |
| 14 teeth, m 1, 20 deg, x 0 | 0.38 | crossing | 3.8167e-05 | 3.9846e-05 | 3.9847e-05 | 0.01 | 3.9847e-05 | 3.9847e-05 | 0.96 |
| 6 teeth, m 1, 14.5 deg, x 0 | 0 | crossing | 2.9877e-05 | 3.4905e-05 | 3.4906e-05 | 0.01 | 3.4941e-05 | 3.4941e-05 | 0.86 |
| 30 teeth, m 0.2, 14.5 deg, x -0.6 | 0.183 | crossing | 3.5795e-05 | 3.5795e-05 | 3.5796e-05 | 0.01 | 3.5796e-05 | 1.7898e-04 | 1.00 |
| 30 teeth, m 10, 14.5 deg, x -0.6 | 0.5 | crossing | 4.4785e-04 | 6.2097e-04 | 6.2097e-04 | 0.00 | 6.2097e-04 | 6.2097e-05 | 0.72 |

#### Tripwire: the tip radius read 0.05 mm above the one used

| Row | Reading (mm) | Reading per module | vs 0.001 x module | vs 0.002 x module | vs 0.005 x module | vs 0.01 x module |
|---|---|---|---|---|---|---|
| 10 teeth, m 1, 20 deg, x 0 | 1.1039e-02 | 1.1039e-02 | 11.04x, over | 5.52x, over | 2.21x, over | 1.10x, over |
| 30 teeth, m 10, 14.5 deg, x -0.6 | 1.3233e-02 | 1.3233e-03 | 1.32x, over | 0.66x, UNDER | 0.26x, UNDER | 0.13x, UNDER |

tripwire, 10 teeth, m 1, 20 deg, x 0: 1.1039e-02 mm, 1.1039e-02 per module
tripwire, 30 teeth, m 10, 14.5 deg, x -0.6: 1.3233e-02 mm, 1.3233e-03 per module

Verdict: reconciled -- method B reproduces STACK's three trochoid figures to one in the third digit, and the oracle agrees with method B on all seven rows.

**Reading the tables.** STACK's trochoid figures are method B: 3.5807, 3.8933 and 3.9847e-5 mm
against the quoted 3.58, 3.89 and 3.99e-5, off by 0.07, 0.33 and 0.53 of a unit of the third digit
(the 14-tooth row reads 3.98e-5 where STACK printed 3.99e-5). Method A reads 5.18 to 5.23e-5 on the
same splines, because it adds the reference's own vertex spacing to the deviation. STACK's
shipped-flank figures are method A: every A reading sits within 2.5 % of half the largest vertex
gap of its own reference (5.72 against 5.82e-5, 6.22 against 6.35e-5, 1.310 against 1.343e-4, and
so on), so they are a measurement floor of the 20,001-point curve and not a deviation; method B on
the same splines reads 1.5 to 3.3e-6 mm on z=12 and the default gear, 30 to 40 times below what
STACK quoted. STACK does not record its flank's pressure angle or reference spacing, so its 6.0e-5
and 1.0e-4 are bracketed (5.7 to 6.2e-5 with the shipped i^1.5 spacing at 20 and 25 degrees; 8.9e-5
uniform to 1.31e-4 i^1.5 on the default gear) and not reproduced to three digits. PITFALLS' 0.13
micrometre (1.3e-4 mm, z=8, 25 degrees) is not reproduced by either method (B reads 2.37e-5 mm, A
6.9e-5 mm); its 0.004 micrometre on the default gear is within 20 % of B's 3.34e-6 mm (0.0033
micrometre) and is not claimed as a reproduction, since the other of the pair is not. SUMMARY
correction 16 is closed: **method B is the deviation, and the one a bar rests on.**

**Sampling.** The plan read the kernel spline at 201 positions; the 14-tooth row shows that is too
few (3.9675e-5 at 201, 3.9847e-5 at 2,001 and at 20,001: 2.2 units off STACK's third digit at
201, 0.5 at 2,001), so the deviation figures here and in `product` use 2,001 positions. The oracle
reads 401 positions per root edge (the whole run takes about 70 s for the seven rows, most of it
the oracle) and agrees with method B on the same positions to 0.01 of a unit on all seven rows; the
19-01 reading at 41 positions reads 0.72 to 1.00 of the converged figure (the module-10 row 28 %
low, 4.4785e-4 against 6.2097e-4 mm). A correct root read at 41 positions can therefore sit 28 %
below its true spline error, so the bar rests on the converged method-B maximum and not on a
41-position reading, and 19-04 chooses its position count knowing that.

**Bar arithmetic on the seven rows** (the whole product is `product`'s): the worst per module is
the 30-tooth module-0.2 row at 1.7898e-4 (3.5796e-5 mm, matching 19-RESEARCH F3's 1.79e-4); 2e-3
times the module is 11.2 times that. **Tripwire** (the tip radius read 0.05 mm above the one the
cutter used): the module-1 10-tooth row reads 1.1039e-2 mm, over every listed bar (11.0x over
1e-3, 5.5x over 2e-3, 2.2x over 5e-3, 1.10x over 1e-2). The shift does not scale with the module, so
the module-10 row reads 1.3233e-2 mm = 1.32e-3 per module: over 1e-3 times the module, **under**
2e-3 times it (0.66x). The tripwire therefore sits on a module-1 row.


### Root arc dead band (19-02)

The hob root leaves the root circle at half-angle pi / z - a / rf, where `a` is the cutter's flat
tip land, so the root arc between neighbouring teeth spans about 2a, and
`cq.Edge.makeThreePointArc` fails or silently drops it when that chord is tiny (19-RESEARCH F4).
`python -m bench.trochoid_part arc` moves the first point of one gear's root curve along the root
circle by each `a` below, builds the blank through the spike's outline and reads what the kernel
did; then it tunes `backlash` by bisection until the real cutter's `a` lands near 1e-8 mm, to show
the band is reachable from user input.

#### Host state

- Machine: 18 CPUs, arm64, 64.0 GiB RAM
- Python: 3.12.15
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `88c5ec5`
- Read 2026-10-08T16:58:06Z to 2026-10-08T16:58:06Z
- Load averages at start: 3.96, 5.57, 7.46; at end: 3.96, 5.57, 7.46

Gear: 12 teeth, module 1, 20 degrees, shift 0, tip radius 0.38 mm; the first point of the root curve moved along the root circle to half-angle pi / z - a / rf, so the root arc between neighbours spans about 2a. A build counts only if it is valid and has 6 z + 2 = 74 faces.

#### Dead band

| a (mm) | chord, root_r[-1] to the next root_l[0] (mm) | result |
|---|---|---|
| 0 | 0.000e+00 | Standard_Failure: GC_MakeArcOfCircle::Value() - no result |
| 1e-12 | 2.000e-12 | builds, 62 faces (expected 74), valid, the arc was silently dropped |
| 1e-10 | 2.000e-10 | builds, 62 faces (expected 74), valid, the arc was silently dropped |
| 1e-09 | 2.000e-09 | Standard_Failure: GC_MakeArcOfCircle::Value() - no result |
| 1e-08 | 2.000e-08 | Standard_Failure: GC_MakeArcOfCircle::Value() - no result |
| 1e-07 | 2.000e-07 | Standard_Failure: GC_MakeArcOfCircle::Value() - no result |
| 2e-07 | 4.000e-07 | builds, 74 faces (expected 74), valid |
| 3e-07 | 6.000e-07 | builds, 74 faces (expected 74), valid |
| 6e-07 | 1.200e-06 | builds, 74 faces (expected 74), valid |
| 1e-06 | 2.000e-06 | builds, 74 faces (expected 74), valid |
| 2e-06 | 4.000e-06 | builds, 74 faces (expected 74), valid |

Last failing chord: 2.000e-07 mm (a = 1e-07); first building chord above it: 4.000e-07 mm (a = 2e-07); monotone (no building row at or below the last failing chord): yes.

#### Reachable from user input: the tuned-backlash gear

`GearParams` as above with root_fillet 3.0 (the cap applies) and backlash bisected over [0, 0.4] in 40 halvings: backlash 0.19898413579248878, tip radius used 0.614 mm of rho_max 0.614000014 mm, tip-land half-width a = 1.000e-08 mm (target 1e-08), root-arc chord 2.000e-08 mm. The bench outline raises Standard_Failure: GC_MakeArcOfCircle::Value() - no result.

ROOT_ARC_MIN proposal: 2e-06 mm (10.0x the last failing chord); against the smallest real chord the product shows: pending (`product` reads it)

**Reading the table.** The dead band has two edges. At chords of 2e-12 and 2e-10 mm (a = 1e-12 and
1e-10) the arc is silently dropped: the blank builds, is valid, and has 62 faces where 74 are
expected, which is the worse failure for being quiet. From 2e-9 mm up to **2.0e-7 mm (the last
failing chord, a = 1e-7)**, and at a chord of exactly 0, the kernel raises `Standard_Failure:
GC_MakeArcOfCircle::Value() - no result`. **4.0e-7 mm (a = 2e-7)
is the first chord that builds** with all 74 faces, valid; every larger row builds, and no row at
or below the last failing chord builds (monotone). 19-RESEARCH had 3e-7 as the first building row
because it did not try 2e-7. The band is reachable: at backlash 0.19898413579248878 the cutter's
`a` is 1.0e-8 mm with the tip radius capped to 0.614 mm of a rho_max of 0.614000014, and the bench
outline raises the same exception. `model._build_checked` catches any non-`BuildError` and
re-labels it "Geometry kernel failed (Standard_Failure); try smaller fillets or chamfers." which is
the wrong remedy: the user set neither a fillet nor a chamfer, and the cause is a backlash and tip
radius that happen to leave 1e-8 mm of tip land. 19-05's `ROOT_ARC_MIN` branch drops the arc below
the constant and shares the junction vector instead. The proposal printed above is the smallest of
1e-6, 2e-6, 5e-6 and 1e-5 mm that is at least 10 times the last failing chord, 2e-6 mm; whether
it is below the smallest real chord in the product is read by `product`: the smallest real chord
is 3.1644e-5 mm, so 2e-6 mm is 15.8 times below it (the guard subsection below).


### Guard numbers over the product (19-02)

19-RESEARCH measured the four structural guards on a 5,159-gear stride-2 sample of the Phase 18
sweep product (A7). `python -m bench.trochoid_part product` runs **every** trochoid case of the
31,446-case product, no stride: it builds each gear's blank through the spike's outline, reads the
tooth-0 root splines against a 20,001-point reference (method B, 2,001 positions per edge), and
measures the spacing ratio (max over min chord of the 16 root points), the annulus (81 positions
per root edge against [rf, ra]), the closed-form area (the extruded face's area, volume over face
width, against the shoelace area of the outline's own points), the junction gap
(|half-angle of the last point - Profile.half_angle at its radius|, split by join) and the root
arc's chord. It then resamples one gear's own curve with a growing chord ratio to find where the
kernel fails, and proposes each bar from the maximum, with the headroom beside it. A second area
measure, with the polygon taken through each arc's midpoint as well as its ends, is printed beside
the plan's arcs-as-chords measure (see the area guard below).

#### Host state

- Machine: 18 CPUs, arm64, 64.0 GiB RAM
- Python: 3.12.15
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `01cd617`
- Read 2026-10-08T17:12:56Z to 2026-10-08T17:15:28Z
- Load averages at start: 19.93, 23.88, 15.18; at end: 68.90, 44.50, 25.06

- Sweep cases: 31,446; trochoid gears (what `bench.trochoid._oracle_cases()` lists as `trochoid`): 10,326; built without a kernel exception: 10,326; kernel exceptions: 0.
- 150 s wall on 18 spawn workers, one pass, no stride.

#### Maxima over the whole product

| Measure | Worst over the product | Gear |
|---|---|---|
| Spline error per module (method B, mm per mm of module) | 1.8431e-04 | grid B: 30 teeth, m 1.75, 14.5 deg, x -0.6, backlash 1.0, tip radius asked 3 mm |
| Spacing ratio, max / min chord of the 16 root points | 13.325 (median 1.692) | grid A: 40 teeth, m 1.0, 14.5 deg, x 0.5, backlash 0.1, tip radius asked 3 mm |
| Annulus, min(R - rf) over 162 positions | -1.137e-13 mm | grid B: 116 teeth, m 10.0, 14.5 deg, x -0.6, backlash 0.0, tip radius asked 3 mm |
| Annulus, max(R - ra) | -4.405e-02 mm | grid B: 8 teeth, m 0.2, 14.5 deg, x -0.6, backlash 0.0, tip radius asked 0 mm |
| Closed-form area, |face area / shoelace area - 1|, arcs as chords | 1.2162e-02 | grid A: 6 teeth, m 1.0, 14.5 deg, x -0.6, backlash 0.0, tip radius asked 0.38 mm |
| Closed-form area, the polygon through each arc's midpoint too | 3.6791e-03 | grid B: 7 teeth, m 1.75, 14.5 deg, x -0.6, backlash 1.0, tip radius asked 3 mm |
| Junction gap, tangent joins (4,303 gears), rad | 2.442e-13 | grid A: 26 teeth, m 1.0, 20.0 deg, x -0.6, backlash 0.1, tip radius asked 0.5 mm |
| Junction gap, crossing joins (6,023 gears), rad | 6.939e-16 | grid A: 7 teeth, m 1.0, 14.5 deg, x -0.5, backlash 0.1, tip radius asked 0 mm |
| Smallest root-arc chord | 3.1644e-05 mm | grid B: 6 teeth, m 1.75, 14.5 deg, x -0.6, backlash 0.1, tip radius asked 3 mm |
| Thinnest waist per module (2 R h) | 2.5577e-03 mm | grid B: 7 teeth, m 10.0, 14.5 deg, x -0.6, backlash 0.1, tip radius asked 0 mm |

#### Bunching: one gear resampled with a growing chord ratio (12 teeth, module 1, 20 degrees, tip radius 0.38 mm)

| Nominal ratio | Chord ratio as built | Spline error, method B (mm) | Kernel |
|---|---|---|---|
| 10 | 7.849 | 6.0802e-05 | builds, 74 faces, valid |
| 100 | 76.5 | 2.2007e-04 | builds, 74 faces, valid |
| 1000 | 749.7 | 5.1756e-04 | builds, 74 faces, valid |
| 10000 | 7393 | 3.6088e-03 | builds, 74 faces, valid |
| 100000 | 7.327e+04 | 9.1444e-03 | builds, 74 faces, valid |
| 1e+06 | 7.289e+05 | nan | Standard_Failure:  |
| 1e+07 | 7.269e+06 | nan | Standard_Failure:  |

#### Proposals (each from the maximum above)

kernel bar proposal: 0.002 x module -- the worst spline error per module is 1.8431e-04 and the oracle's own resolution about 1e-15 per module; headroom 10.9x over the worst, 2e+12x over the resolution (at or over 10x: the planner's call)
ROOT_SPACING_RATIO_MAX proposal: 1000 -- the maximum spacing ratio is 13.325, headroom 75.0x (at or over 10x: the planner's call); the first chord ratio the kernel failed at is 728888, 729x over the bar
annulus proposal: [rf - TOL, ra + TOL] with TOL = 1e-06 mm -- the worst excursion outside [rf, ra] is 1.137e-13 mm, headroom 8.8e+06x (at or over 10x: the planner's call)
ROOT_AREA_REL_MAX proposal (arcs as chords): NONE of (0.01, 0.02, 0.05, 0.1) has 10x headroom over 1.2162e-02; the largest listed value, 0.1, is 8.2x; goes to the human
ROOT_AREA_REL_MAX proposal (arc midpoints in the polygon): 0.05 -- the maximum is 3.6791e-03, headroom 13.6x (at or over 10x: the planner's call)
ROOT_JUNCTION_BAR_RAD proposal: 1e-11 rad -- the larger join maximum is 2.442e-13 rad (tangent 2.442e-13, crossing 6.939e-16), the libm floor 1e-12; headroom 40.9x (at or over 10x: the planner's call)
ROOT_ARC_MIN check: proposal 2e-06 mm (from `arc`) against the smallest real root-arc chord 3.1644e-05 mm: the proposal is below it, which is 15.8x the proposal

**Guard by guard.** 10,326 trochoid gears, the count `bench.trochoid._oracle_cases()` lists (and
18-04's 10,326 curves), all built, **0 kernel exceptions**.

- *Kernel bar.* The worst spline error is 1.8431e-4 per module (30 teeth, module 1.75, 14.5 degrees,
  x -0.6, backlash 1.0, tip radius capped from 3.0), 3 % above the 1.79e-4 the stride-2 sample
  read; the oracle's own resolution is about 1e-15 per module (18-04). The proposed bar is
  2e-3 x module, **10.9x the worst**: at the 10x line, so it goes to the human with the tripwire
  (11.0x over 1e-3 and 5.5x over 2e-3 on the module-1 10-tooth row; 0.66x of it on module 10).
- *Spacing ratio.* Maximum 13.325 (40 teeth, module 1, 14.5 degrees, x 0.5, backlash 0.1, tip radius
  capped from 3.0; the sample's 11.34 was another gear). Proposed `ROOT_SPACING_RATIO_MAX` 1000,
  **75x**; the kernel first fails at a chord ratio of 7.29e5 (an empty `Standard_Failure`), 729x
  above it, and the spline error on the bunching gear is 5.2e-4 mm at a ratio of 750 and 3.6e-3 mm at
  7,393 (over a 2e-3 bar): at 1000 the guard stops a bunched curve before the proof would see it.
- *Annulus.* The worst excursion outside [rf, ra] is 1.137e-13 mm (116 teeth, module 10, backlash 0:
  a float residue below the root circle); the nearest approach to the tip circle is 0.044 mm.
  Proposed [rf - TOL, ra + TOL] with `model.TOL` = 1e-6 mm, **8.8e6x**.
- *Closed-form area.* With both arcs taken as chords, as the plan specifies, the maximum is
  1.2162e-2 (6 teeth, module 1, 14.5 degrees, x -0.6, backlash 0, tip radius 0.38): none of 1e-2,
  2e-2, 5e-2, 1e-1 is 10x over it (0.1 is **8.2x**), so this guard **joins the checkpoint**. With the
  polygon through each arc's midpoint (which `model` has for nothing: `_polar(ra, c)` and
  `_polar(rf, c + pi / z)` are the arcs' own middle points) the maximum is 3.6791e-3 (7 teeth,
  module 1.75, x -0.6, backlash 1.0, tip radius capped from 3.0) and 5e-2 reads **13.6x**. 19-05
  builds the polygon either way; the measure is the human's choice, with the bar following it.
- *Junction gap.* Tangent joins (4,303 gears) 2.442e-13 rad (26 teeth, 20 degrees, x -0.6, backlash
  0.1, tip radius 0.5), crossing joins (6,023 gears) 6.939e-16 rad. Proposed
  `ROOT_JUNCTION_BAR_RAD` 1e-11 rad, **40.9x**. The 1e-12 rad of 18-01's `JUNCTION_BAR_RAD` was set on
  rows reading 4e-17 and is only 4.1x over this product's tangent maximum, so 19-05 does not reuse
  it.
- *Root arc.* The smallest real chord in the product is 3.1644e-5 mm (6 teeth, module 1.75, 14.5
  degrees, x -0.6, backlash 0.1, tip radius capped from 3.0); the `arc` proposal of 2e-6 mm is
  **15.8x below it**, which closes the comparison the root-arc subsection left pending: the
  guard cannot drop a real arc.


### Waist walk (19-02, D-07)

D-07 asked the bench to walk the low-tooth corner and find where the built waist stops being a
tooth: the kernel refuses, or the spline-to-oracle gap leaves its bar. `python -m bench.trochoid_part
waist --bar-per-module 2e-3` walks 6, 7 and 8 teeth, module 1, 14.5 degrees, profile shift -0.6 to 0
in 0.01 steps, tip radius 0, 0.38 and 3.0 (capped), at the default backlash (0.10) and at 0 (the
backlash 19-RESEARCH F8's scratch walk used), builds every trochoid gear's blank, reads its tooth-0
root with the independent oracle at 401 positions per edge and takes the waist as `2 R h` of
`RootCurve.waist`. The bar in use is 2e-3 x module, the proposal `product` made. Floor candidates
are printed with the number of gears each would warn on, in the walk and in the whole product (the
product's waists come from the curve alone, no kernel).

#### Host state

- Machine: 18 CPUs, arm64, 64.0 GiB RAM
- Python: 3.12.15
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `2dbf6f3`
- Read 2026-10-08T17:50:55Z to 2026-10-08T18:02:50Z
- Load averages at start: 8.47, 23.43, 36.47; at end: 49.56, 54.38, 49.19

D-07's walk: teeth (6, 7, 8), module 1, 14.5 degrees, backlash (0.1, 0.0) mm, profile shift -0.6 to 0 in 0.01 steps, tip radius (0.0, 0.38, 3.0) mm (3.0 is the field's maximum, capped by the cutter). 1098 gears in 713 s on 18 spawn workers; oracle at 401 positions per root edge; bar read as 0.002 x module.

#### What `root_mode` answered

| Answer | Gears |
|---|---|
| radial (tooth severed) | 37 |
| trochoid | 1061 |

#### The walk by series

| Teeth | Backlash | Tip radius asked (used) | Severed at x up to | First trochoid x | Thinnest built waist (mm) | at x | Worst oracle reading (mm) |
|---|---|---|---|---|---|---|---|
| 6 | 0.1 | 0 (0) | -0.44 | -0.43 | 1.4861e-02 | -0.43 | 4.227e-05 |
| 6 | 0.1 | 0.38 (0.38) | -0.58 | -0.57 | 3.2325e-03 | -0.57 | 4.447e-05 |
| 6 | 0.1 | 3 (0.661) | -- | -0.6 | 1.0652e-01 | -0.6 | 5.017e-05 |
| 6 | 0 | 0 (0) | -0.49 | -0.48 | 4.9794e-03 | -0.48 | 4.300e-05 |
| 6 | 0 | 0.38 (0.38) | -- | -0.6 | 2.1992e-02 | -0.6 | 4.463e-05 |
| 6 | 0 | 3 (0.596) | -- | -0.6 | 1.3753e-01 | -0.6 | 4.814e-05 |
| 7 | 0.1 | 0 (0) | -0.56 | -0.55 | 1.2622e-02 | -0.55 | 4.685e-05 |
| 7 | 0.1 | 0.38 (0.38) | -- | -0.6 | 1.3704e-01 | -0.6 | 5.023e-05 |
| 7 | 0.1 | 3 (0.661) | -- | -0.6 | 2.8410e-01 | -0.6 | 5.983e-05 |
| 7 | 0 | 0 (0) | -- | -0.6 | 9.4238e-03 | -0.6 | 4.764e-05 |
| 7 | 0 | 0.38 (0.38) | -- | -0.6 | 2.0800e-01 | -0.6 | 5.023e-05 |
| 7 | 0 | 3 (0.596) | -- | -0.6 | 3.2235e-01 | -0.6 | 5.681e-05 |
| 8 | 0.1 | 0 (0) | -- | -0.6 | 9.0302e-02 | -0.6 | 5.001e-05 |
| 8 | 0.1 | 0.38 (0.38) | -- | -0.6 | 2.8143e-01 | -0.6 | 5.541e-05 |
| 8 | 0.1 | 3 (0.661) | -- | -0.6 | 4.2284e-01 | -0.6 | 6.900e-05 |
| 8 | 0 | 0 (0) | -- | -0.6 | 1.6362e-01 | -0.6 | 5.001e-05 |
| 8 | 0 | 0.38 (0.38) | -- | -0.6 | 3.5694e-01 | -0.6 | 5.541e-05 |
| 8 | 0 | 3 (0.596) | -- | -0.6 | 4.6704e-01 | -0.6 | 6.502e-05 |

The thinnest built waist, then the next four:

- 3.2325e-03 mm: 6 teeth, x -0.57, backlash 0.1, tip radius asked 0.38 mm (used 0.38), crossing join
- 4.9794e-03 mm: 6 teeth, x -0.48, backlash 0, tip radius asked 0 mm (used 0), crossing join
- 9.4238e-03 mm: 7 teeth, x -0.6, backlash 0, tip radius asked 0 mm (used 0), crossing join
- 1.2622e-02 mm: 7 teeth, x -0.55, backlash 0.1, tip radius asked 0 mm (used 0), crossing join
- 1.4861e-02 mm: 6 teeth, x -0.43, backlash 0.1, tip radius asked 0 mm (used 0), crossing join

**Thinnest built waist: 3.2325e-03 mm** (6 teeth, x -0.57, backlash 0.1, tip radius asked 0.38 mm (used 0.38)); 1061 trochoid gears built of 1098 walked.

Kernel refusals: none (every trochoid gear built one valid solid).

Worst oracle reading in the walk: 6.8995e-05 mm (8 teeth, x 0, backlash 0.1, tip radius asked 3 mm (used 0.661)).
- readings over 0.001 x module (module 1): 0 of 1061
- readings over 0.002 x module (module 1): 0 of 1061
- readings over 0.005 x module (module 1): 0 of 1061
- readings over 0.01 x module (module 1): 0 of 1061
Oracle readings over the bar in use (0.002 mm): 0.

#### Floor candidates

| Candidate | Floor | Walk gears warned (of 1061 built) | Product gears warned (of 10,326) |
|---|---|---|---|
| measured: 10x the thickest waist where the kernel refused or the oracle left the bar | none: no failure signature in the walk | -- | -- |
| spline scale: 10x the worst oracle reading in the walk | 6.8995e-04 mm per mm of module | 0 | 0 |
| printability: MIN_TIP_FDM, the tip warning's own number | 4.0000e-01 mm, absolute | 294 | 771 |

Product gears warned, by module:

- spline scale: module 0.2: 0 of 616 (0 on a tangent join); module 1: 0 of 6,399 (0 on a tangent join); module 1.75: 0 of 1,469 (0 on a tangent join); module 10: 0 of 1,842 (0 on a tangent join)
- printability: module 0.2: 595 of 616 (195 on a tangent join); module 1: 125 of 6,399 (0 on a tangent join); module 1.75: 43 of 1,469 (0 on a tangent join); module 10: 8 of 1,842 (0 on a tangent join)

Thinnest waist per module over the whole product: 2.5577e-03 mm (grid B: 7 teeth, m 10.0, 14.5 deg, x -0.6, backlash 0.1, tip radius asked 0 mm).

**What the walk found.** Nothing refuses. Of 1,098 gears, 37 are `tooth severed` (waist at or below
zero, refused by `root_mode` before the kernel sees them) and 1,061 are trochoid gears, **all
1,061 built one valid solid**; the worst oracle reading is 6.9e-5 mm (8 teeth, x 0, tip radius
capped from 3.0), and **0 readings are over even the smallest listed bar**, 1e-3 mm. So there is no
failure signature above the spline-error scale, as 19-RESEARCH F8 expected: the kernel builds a
valid tooth at a waist of 3.2e-3 mm and the oracle accepts it, and the floor is a choice the human
makes on these numbers. The walk reproduces F8 (4.9794e-3 mm at 6 teeth, x -0.48, backlash 0, sharp
cutter; next 9.4238e-3 mm, F8's 4.98e-3 and 9.4e-3) and finds a thinner waist F8 did not: **3.2325e-3
mm** at 6 teeth, x -0.57, backlash 0.1, tip radius 0.38. The waist grows by about 0.015 mm per 0.01
of profile shift, so any positive thickness is reachable from user input. The three candidates:
**(measured)** none, because no gear failed; **(spline scale)** 10x the worst oracle reading,
6.8995e-4 mm per mm of module, warns on 0 of 1,061 walk gears and 0 of the 10,326 product gears
(the product's thinnest waist per module is 2.5577e-3 mm, 3.7x above it); **(printability)**
`MIN_TIP_FDM`, 0.4 mm, the number the tip warning already uses, warns on 294 of the 1,061 walk gears
and 771 of the 10,326 product gears. By module the 771 are mostly a small-module warning: 595 of
the 616 module-0.2 gears (195 of them on tangent joins, with no undercut at all) against 176 of the
9,710 gears of module 1 and above (125 at module 1, 43 at 1.75, 8 at 10), because an absolute
0.4 mm floor sits above the whole tooth base of a module-0.2 gear.


### Bars adopted (19-02)

Recorded 2026-10-09 from the human's answer at 19-02's blocking checkpoint (Task 3). 19-04, 19-05
and 19-06 write these values into code from this subsection, each beside the measurement it rests
on, and nowhere else. Nothing was re-measured to write it: every number below is copied from the
four subsections above (HEAD `01cd617`, `2dbf6f3`, `af53e4f`).

**The human's words, verbatim: `take the recommendations`.** The mapping to option ids is the
orchestrator's, from the recommendations the first 19-02 executor stated in its checkpoint report;
the human named no id. The five decisions as adopted:

| Decision | Adopted id | Value |
|---|---|---|
| Kernel bar | `bar-proposed` | 2e-3 x module |
| Waist floor | `floor-print` | 0.4 mm, absolute (`MIN_TIP_FDM`) |
| Waist field name | `name-root_waist` | `root_waist` |
| D-02's one-way door | `d02-confirm` | `root_shape` and the `root_fillet` reinterpretation stand |
| Area guard bar | `area-midpoints` | 5e-2 on the polygon through the arcs' midpoints |

#### Kernel bar: `bar-proposed`, 2e-3 x module (L33 D-06)

- Worst spline error per module over all 10,326 trochoid gears of the Phase 18 product, no stride:
  **1.8431e-4** (30 teeth, module 1.75, 14.5 degrees, x -0.6, backlash 1.0, tip radius capped from
  3.0). The oracle's own resolution: about 1e-15 per module (18-04).
- Bar 2e-3 x module: **10.9x** the worst (10.85), 2e12x the resolution. At the 10x line and not
  far over it, which is why it went to the human; the next listed value, 5e-3, was offered as
  `bar-wider` (27x) and not taken.
- Tripwire (the tip radius read 0.05 mm above the one the cutter used), on the module-1 10-tooth
  row: **1.1039e-2 mm, 5.5x over the bar**. The tripwire must stay on a module-1 row: the shift does
  not scale with the module, and on module 10 the same shift reads 1.3233e-2 mm, 0.66x of the bar
  (2e-2 mm), under it.
- Position count: the 19-01 reading at 41 positions can sit 28 % below the converged spline error
  (module-10 row, 4.4785e-4 against 6.2097e-4 mm), so the bar is applied to a reading taken at 401 or
  more positions per root edge, where the oracle agrees with method B to 0.01 of a unit of the third
  digit on all seven rows.

#### Waist floor: `floor-print`, 0.4 mm absolute (D-07, L08)

- Measured: thinnest built waist **3.2325e-3 mm** (6 teeth, module 1, x -0.57, backlash 0.1, tip
  radius 0.38, crossing join). Every one of the 1,061 trochoid gears in the walk built one valid
  solid; the worst oracle reading was 6.8995e-5 mm and no reading was over even 1e-3 x module. There
  is no failure signature above the spline-error scale, so the floor is a printability choice made
  on the numbers, after the walk, and not a kernel limit. The floor is 124x the thinnest built waist
  and 5.8e3x the worst oracle reading; "headroom over a failure" does not apply because nothing failed.
- The floor warns and never refuses (D-06): the waist is printed for every trochoid gear.
- It warns on **294 of the 1,061** walk gears and **771 of the 10,326** product gears.
- **Small-module caveat, recorded with the adoption.** 595 of the 616 module-0.2 gears warn (195 of
  them on tangent joins, which have no undercut at all) against 176 of the 9,710 gears of module 1
  and above (125 of 6,399 at module 1, 43 of 1,469 at 1.75, 8 of 1,842 at 10). The 0.4 mm floor sits
  above the whole tooth base of a module-0.2 gear, so on a small module the warning is mostly a
  printability remark about the part and not about the undercut. The human adopted the floor with
  these counts in front of them. The warning 19-06 plans for it is the `waist thin` sentence, which
  does not use the word undercut, so a tangent-join module-0.2 gear is not told it is undercut.
- The two candidates not taken: `floor-measured` does not exist (no failure signature) and
  `floor-spline` (6.8995e-4 mm per mm of module) warns on 0 of 1,061 and 0 of 10,326.

#### Waist field name: `name-root_waist`

`root_waist`: the tooth's narrowest thickness in the hob-cut root, printed for every trochoid gear,
true on tangent and crossing joins alike, beside `root_d`, `root_fillet` and `root_form_d`. "Undercut
waist" would misname it on a tangent gear, which has a waist and no undercut. It is a published key
on `/api/info` and `spur info` from its first release, so a rename later must keep the old key.

#### D-02's one-way door: `d02-confirm`

`root_shape: Literal["radial", "trochoid"]`, default `radial` (so no shared link moves, L05), group
Teeth after `tip_chamfer`, the generated `--root-shape` flag, and `root_fillet` read as the hob's
tip radius under it (D-01). Resting on: 10,326 of 10,326 trochoid gears built, 0 kernel exceptions.
**19-04 is not blocked.**

#### Area guard: `area-midpoints`, bar 5e-2 on the polygon through the arcs' midpoints

- Measure: |face area / shoelace area - 1| with the polygon taken through the midpoint of each arc
  (the tip arc's and the root arc's own middle points, which `model` already has) as well as its
  ends. Worst over the product: **3.6791e-3** (7 teeth, module 1.75, x -0.6, backlash 1.0, tip radius
  capped from 3.0). Bar 5e-2: **13.6x** (13.59).
- Rejected: the plan's measure with both arcs taken as chords. Worst 1.2162e-2 (6 teeth, module 1,
  14.5 degrees, x -0.6, backlash 0, tip radius 0.38); the largest listed bar, 0.1, is **8.2x**, and
  none of 1e-2, 2e-2, 5e-2, 1e-1 reaches 10x. A bar under 10x is the human's, and a larger listed
  value was not invented to fit it. 19-05 builds the midpoint polygon.

#### The other guard bars: the planner's call, recorded as measured

None of these is under 10x, so none needed a human answer (19-CONTEXT "Claude's Discretion").

| Bar | Value | Worst over the product | Headroom | Beside it |
|---|---|---|---|---|
| `ROOT_SPACING_RATIO_MAX` | 1000 | 13.325 (40 teeth, module 1, 14.5 degrees, x 0.5, backlash 0.1, tip radius capped from 3.0) | 75.0x | the kernel first fails at a chord ratio of 728,888, 729x above the bar |
| annulus | [rf - TOL, ra + TOL], TOL = `model.TOL` = 1e-6 mm | 1.137e-13 mm outside [rf, ra] (116 teeth, module 10, backlash 0); nearest approach to the tip circle 0.044 mm | 8.8e6x | |
| `ROOT_JUNCTION_BAR_RAD` | 1e-11 rad | 2.442e-13 rad on tangent joins (26 teeth, 20 degrees, x -0.6, backlash 0.1, tip radius 0.5); crossing joins 6.939e-16 rad | 40.9x | the 18-01 bar of 1e-12 rad is only 4.1x over this product's tangent maximum, so **19-05 must not reuse it** |
| `ROOT_ARC_MIN` | 2e-6 mm | last failing chord 2.0e-7 mm (a = 1e-7 mm) | 10.0x over the last failing chord | 15.8x below the smallest real chord in the product, 3.1644e-5 mm (6 teeth, module 1.75, x -0.6, backlash 0.1, tip radius capped from 3.0) |

The root-arc dead band has a second, quieter edge: chords of 2e-12 and 2e-10 mm build a valid
solid with the arc silently dropped (62 faces where 74 are expected), and the band is reachable
from user input (backlash 0.19898413579248878 with the tip radius capped leaves a = 1.0e-8 mm).
`ROOT_ARC_MIN` is why 19-05 drops the arc below it and shares the junction vector.


### Chamfer law on the real build (19-09)

19-01 bisected L29's tip-chamfer law on a trochoid outline `bench/trochoid_part.py` assembled itself
(`trochoid_outline`, a copy of RESEARCH Pattern 2), and 19-02 read the root arc's dead band on the
same copy. 19-04 moved the builder into `spur.model` and 19-09 removed the copy: since this plan the
bench builds blanks through `model._gear_blank` / `model._outline` and parts through
`model._build_checked` with `root_shape="trochoid"` and the row's tip radius as `root_fillet`; for a
bisection the part is built with `tip_chamfer=0` and chamfered at `c` by `chamfered`, as before. One
definition of the hob-root outline by the phase's end (the 11-05 precedent). The same 14 rows were
re-run with `python -m bench.trochoid_part chamfer` and `... arc`; both outputs follow verbatim
(`chamfer` first), the `arc` host-state heading renamed so this subsection has one per run. HEAD in the
host state is the commit before this plan's: the tree carried this plan's bench edits, uncommitted,
while the runs were taken.

#### Host state

- Machine: 18 CPUs, arm64, 64.0 GiB RAM
- Python: 3.12.15
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `5f3df84`
- Read 2026-10-09T05:47:04Z to 2026-10-09T05:51:31Z
- Load averages at start: 2.92, 5.27, 5.90; at end: 3.86, 4.27, 5.26

#### Bisection (20 halvings between 0 and 0.45 x face_width)

| Gear | Tip radius (mm) | Join | R_join (mm) | pred = ra - R_join | last ok | first fail | last ok - pred | Verdict | Binding cap | Worst oracle (mm) |
|---|---|---|---|---|---|---|---|---|---|---|
| default 19 teeth, m 1.75, 25 deg, x 0 | 0 | tangent | 15.1805 | 3.1944892 | 3.1944884 | 3.1944916 | -7.71e-07 | on the law | ra - r | 1.35e-05 |
| default 19 teeth, m 1.75, 25 deg, x 0 | 0.5 | tangent | 15.2788 | 3.0961925 | 3.0961908 | 3.0961940 | -1.73e-06 | on the law | ra - r | 2.20e-05 |
| 100 teeth, m 1, 14.5 deg, x -0.6 | 0 | tangent | 48.6785 | 1.7215252 | 1.7215244 | 1.7215276 | -8.65e-07 | on the law | ra - r | 5.91e-06 |
| 100 teeth, m 1, 14.5 deg, x -0.6 | 0.5 | tangent | 48.8589 | 1.5410770 | 1.5410739 | 1.5410771 | -3.06e-06 | on the law | ra - r | 9.50e-05 |
| 30 teeth, m 1, 14.5 deg, x -0.6 | 0 | crossing | 14.5916 | 0.8084213 | 0.8233534 | 0.8233566 | +1.49e-02 | conservative | ra - r | 2.44e-05 |
| 30 teeth, m 1, 14.5 deg, x -0.6 | 0.5 | crossing | 14.5508 | 0.8492071 | 2.2499979 | 2.2500011 | +1.40e+00 | conservative | ra - r | 1.23e-04 |
| 12 teeth, m 1, 20 deg, x 0 | 0 | crossing | 5.6756 | 1.3243676 | 1.3243654 | 1.3243686 | -2.23e-06 | on the law | ra - r | 1.97e-05 |
| 12 teeth, m 1, 20 deg, x 0 | 0.5 | crossing | 5.6457 | 1.3542630 | 1.3542602 | 1.3542634 | -2.80e-06 | on the law | ra - r | 3.99e-05 |
| 10 teeth, m 1, 20 deg, x 0 | 0 | crossing | 4.7567 | 1.2433329 | 2.2499979 | 2.2500011 | +1.01e+00 | conservative | ra - r | 2.15e-05 |
| 10 teeth, m 1, 20 deg, x 0 | 0.5 | crossing | 4.7174 | 1.2825685 | 1.2825680 | 1.2825712 | -5.13e-07 | on the law | ra - r | 3.94e-05 |
| 8 teeth, m 1, 20 deg, x 0 | 0 | crossing | 3.8448 | 1.1552447 | 1.2656250 | 1.2656282 | +1.10e-01 | conservative | ra - r | 2.29e-05 |
| 8 teeth, m 1, 20 deg, x 0 | 0.5 | crossing | 3.7960 | 1.2039992 | 2.2499979 | 2.2500011 | +1.05e+00 | conservative | ra - r | 3.66e-05 |
| 6 teeth, m 1, 14.5 deg, x 0 | 0 | crossing | 3.0994 | 0.9006385 | 0.9006364 | 0.9006397 | -2.04e-06 | on the law | ra - R_join | 2.99e-05 |
| 6 teeth, m 1, 14.5 deg, x 0 | 0.5 | crossing | 3.0183 | 0.9816865 | 1.3320547 | 1.3320580 | +3.50e-01 | conservative | ra - R_join | 4.47e-05 |

First-failure reasons: default 19 teeth, m 1.75, 25 deg, x 0 @ 0: Standard_Failure; default 19 teeth, m 1.75, 25 deg, x 0 @ 0.5: Standard_Failure; 100 teeth, m 1, 14.5 deg, x -0.6 @ 0: Standard_Failure; 100 teeth, m 1, 14.5 deg, x -0.6 @ 0.5: Standard_Failure; 30 teeth, m 1, 14.5 deg, x -0.6 @ 0: invalid; 30 teeth, m 1, 14.5 deg, x -0.6 @ 0.5: Standard_Failure; 12 teeth, m 1, 20 deg, x 0 @ 0: invalid; 12 teeth, m 1, 20 deg, x 0 @ 0.5: invalid; 10 teeth, m 1, 20 deg, x 0 @ 0: invalid; 10 teeth, m 1, 20 deg, x 0 @ 0.5: invalid; 8 teeth, m 1, 20 deg, x 0 @ 0: invalid; 8 teeth, m 1, 20 deg, x 0 @ 0.5: invalid; 6 teeth, m 1, 14.5 deg, x 0 @ 0: invalid; 6 teeth, m 1, 14.5 deg, x 0 @ 0.5: invalid

Binding cap is ra - R_join on: 6 teeth, m 1, 14.5 deg, x 0 @ 0; 6 teeth, m 1, 14.5 deg, x 0 @ 0.5.
Verdict: law holds -- 8 rows on the law, 6 conservative (30 teeth, m 1, 14.5 deg, x -0.6 @ 0; 30 teeth, m 1, 14.5 deg, x -0.6 @ 0.5; 10 teeth, m 1, 20 deg, x 0 @ 0; 8 teeth, m 1, 20 deg, x 0 @ 0; 8 teeth, m 1, 20 deg, x 0 @ 0.5; 6 teeth, m 1, 14.5 deg, x 0 @ 0.5).

**Against 19-01.** The 14 table rows above are identical to the 14 rows of `### Chamfer across the
junction (19-01)`: every R_join, `pred`, last ok, first fail, `last ok - pred`, verdict, binding cap and
worst oracle reading (a string equality of the two row lists, run when this was written). So the last
building `c` on every row equals 19-01's to all seven printed decimals, inside the bisection's
resolution (3.2e-6 mm), as expected: the assembly moved unchanged from the bench into `model.py`. The
verdict is the same, `law holds`, 8 rows on the law and the same 6 conservative, no row optimistic, so
the cap `ra - R_join - TIP_CHAMFER_MARGIN` that 19-04 shipped rests on the shipped build and not only on
the copy. The worst oracle reading on an unchamfered root is 1.23e-04 mm (30 teeth, module 1, tip radius
0.5), unchanged; the bar is 2e-3 x module (`### Bars adopted (19-02)`), so that reading is 0.06 of it.

#### Root arc dead band on the shipped outline

#### Host state (the `arc` run)

- Machine: 18 CPUs, arm64, 64.0 GiB RAM
- Python: 3.12.15
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `5f3df84`
- Read 2026-10-09T05:52:24Z to 2026-10-09T05:52:24Z
- Load averages at start: 3.40, 4.09, 5.13; at end: 3.40, 4.09, 5.13

Gear: 12 teeth, module 1, 20 degrees, shift 0, tip radius 0.38 mm; the first point of the root curve moved along the root circle to half-angle pi / z - a / rf, so the root arc between neighbours spans about 2a. The outline is the shipped one (`model._outline`, ROOT_ARC_MIN 2e-06 mm), read twice: with every guard on, and with the annulus guard lifted (a moved first point is not a curve any cutter draws, and its spline swings under the root circle). A build counts only if it is one valid solid with 5 z + (root arcs made) + 2 faces; 6 z + 2 = 74 when every arc is made.

#### Dead band

| a (mm) | chord, root_r[-1] to the next root_l[0] (mm) | all guards on | annulus guard lifted |
|---|---|---|---|
| 0 | 0.000e+00 | BuildError: A hob-root spline leaves the root-to-tip annulus (radius 4.748526 mm outside 4.750000 to 7.000000): a modelling defect in spur, not a conflict in these parameters. Set root_shape to radial to build this gear with the analytic root. | builds, 62 faces (expected 62: 0 of 12 root arcs made), valid |
| 1e-12 | 2.000e-12 | BuildError: A hob-root spline leaves the root-to-tip annulus (radius 4.748526 mm outside 4.750000 to 7.000000): a modelling defect in spur, not a conflict in these parameters. Set root_shape to radial to build this gear with the analytic root. | builds, 62 faces (expected 62: 0 of 12 root arcs made), valid |
| 1e-10 | 2.000e-10 | BuildError: A hob-root spline leaves the root-to-tip annulus (radius 4.748526 mm outside 4.750000 to 7.000000): a modelling defect in spur, not a conflict in these parameters. Set root_shape to radial to build this gear with the analytic root. | builds, 62 faces (expected 62: 0 of 12 root arcs made), valid |
| 1e-09 | 2.000e-09 | BuildError: A hob-root spline leaves the root-to-tip annulus (radius 4.748526 mm outside 4.750000 to 7.000000): a modelling defect in spur, not a conflict in these parameters. Set root_shape to radial to build this gear with the analytic root. | builds, 62 faces (expected 62: 0 of 12 root arcs made), valid |
| 1e-08 | 2.000e-08 | BuildError: A hob-root spline leaves the root-to-tip annulus (radius 4.748526 mm outside 4.750000 to 7.000000): a modelling defect in spur, not a conflict in these parameters. Set root_shape to radial to build this gear with the analytic root. | builds, 62 faces (expected 62: 0 of 12 root arcs made), valid |
| 1e-07 | 2.000e-07 | BuildError: A hob-root spline leaves the root-to-tip annulus (radius 4.748526 mm outside 4.750000 to 7.000000): a modelling defect in spur, not a conflict in these parameters. Set root_shape to radial to build this gear with the analytic root. | builds, 62 faces (expected 62: 0 of 12 root arcs made), valid |
| 2e-07 | 4.000e-07 | BuildError: A hob-root spline leaves the root-to-tip annulus (radius 4.748526 mm outside 4.750000 to 7.000000): a modelling defect in spur, not a conflict in these parameters. Set root_shape to radial to build this gear with the analytic root. | builds, 62 faces (expected 62: 0 of 12 root arcs made), valid |
| 3e-07 | 6.000e-07 | BuildError: A hob-root spline leaves the root-to-tip annulus (radius 4.748526 mm outside 4.750000 to 7.000000): a modelling defect in spur, not a conflict in these parameters. Set root_shape to radial to build this gear with the analytic root. | builds, 62 faces (expected 62: 0 of 12 root arcs made), valid |
| 6e-07 | 1.200e-06 | BuildError: A hob-root spline leaves the root-to-tip annulus (radius 4.748526 mm outside 4.750000 to 7.000000): a modelling defect in spur, not a conflict in these parameters. Set root_shape to radial to build this gear with the analytic root. | builds, 62 faces (expected 62: 0 of 12 root arcs made), valid |
| 1e-06 | 2.000e-06 | BuildError: A hob-root spline leaves the root-to-tip annulus (radius 4.748526 mm outside 4.750000 to 7.000000): a modelling defect in spur, not a conflict in these parameters. Set root_shape to radial to build this gear with the analytic root. | builds, 67 faces (expected 67: 5 of 12 root arcs made), valid |
| 2e-06 | 4.000e-06 | BuildError: A hob-root spline leaves the root-to-tip annulus (radius 4.748526 mm outside 4.750000 to 7.000000): a modelling defect in spur, not a conflict in these parameters. Set root_shape to radial to build this gear with the analytic root. | builds, 74 faces (expected 74: 12 of 12 root arcs made), valid |

11 rows. All guards on: 0 build, 11 are refused before the kernel. Annulus guard lifted: 10 rows are under ROOT_ARC_MIN (chord at most 2.000e-06 mm, the neighbours share a vertex); the dead band is CLOSED: every row builds one valid solid.

#### Reachable from user input: the tuned-backlash gear

`GearParams` as above with root_fillet 3.0 (the cap applies) and backlash bisected over [0, 0.4] in 40 halvings: backlash 0.19898413579248878, tip radius used 0.614 mm of rho_max 0.614000014 mm, tip-land half-width a = 1.000e-08 mm (target 1e-08), root-arc chord 2.000e-08 mm: builds, 62 faces (expected 62: 0 of 12 root arcs made), valid. The shipped blank builds.

**Is the dead band closed?** On what the kernel and `ROOT_ARC_MIN` do, yes. With the annulus guard lifted,
all 11 rows build one valid solid: the 9 rows with a chord of 1.2e-6 mm or less leave the arc out and read
62 faces (5 z + 2: the neighbours share a vertex), the row at a = 1e-6 mm (chord 2.000e-06 mm, which is
`ROOT_ARC_MIN` to float noise) makes 5 of its 12 arcs and reads 67 faces, and the row at 2e-6 mm makes all
12 and reads 74. 19-02 read this gear raising `GC_MakeArcOfCircle::Value() - no result` at every chord from
2e-9 to 2.0e-7 mm and at exactly 0, silently dropping the arc (62 faces where 74 were expected) at 2e-12
and 2e-10 mm, and building from 4.0e-7 mm; no row of this table raises, and the 62-face rows are the
shipped rule's own answer and not a silent drop. The user-reachable gear (backlash 0.19898413579248878,
tip land 1.0e-8 mm) builds through the shipped blank with every guard on: 62 faces, 0 of 12 arcs made.

**With every guard on, the 11 hand-made rows are all refused, and the refusal is not the dead band.** The
shipped annulus guard raises `BuildError` on each, at the same radius (4.748526 mm against a root circle
of 4.750000 mm, 1.474e-3 mm under it). A moved first point is not a curve any cutter draws: the root spline
through it and the other points of the real curve runs under the root circle. 19-02's table built these
rows because its outline had no such guard; this outline is the shipped one and does what 19-04 and 19-05
made it do. The plan expected every row of the dead-band table to build one valid solid with the guards on,
and that is not met for these hand-made rows; the table shows both readings instead of smoothing it. The
closure is read on the annulus-lifted column (kernel plus `ROOT_ARC_MIN`) and on the tuned gear, which is a
real cutter's curve and builds with all guards on.

**What else moved in the bench.** `arc`'s ROOT_ARC_MIN proposal and `arc_min_proposal` are gone (the
constant is adopted: 2e-6 mm, 10.0x the last failing chord 19-02 read); `product` prints the shipped
constant against the smallest real root-arc chord instead of a proposal; `product`'s bunching table lifts
the shipped spacing guard for its builds (it would answer first at every ratio over 1000), so it still
reads the kernel's own first failure and not the guard. Neither `product` nor `waist` was re-run: their
bars are adopted and no number in this plan depends on them. `outline_teeth` stays as a measuring helper:
it makes no edge and keeps the points before `ROOT_ARC_MIN`, which `arc` and `product` read their chords
and areas from.

### Composed build time on the real build (19-09)

ROADMAP success criterion 4, on the code that ships: the heaviest gear a `root_shape="trochoid"` request
can still change (116 teeth at 14.5 degrees and profile shift -0.6, where `rb > rf` still holds), every
row 19-01 timed, each in both root shapes, through the standard runner. `bench/sweeps/trochoid.json` holds
the 17 corner rows `GearParams` accepts (the 18 rows of `composed.json` moved to the corner, minus 3
refused there, plus the 2 lighter module-10 rows of `LIGHTER_ROWS`), each followed by the same row with
`"root_shape": "trochoid"`; `tests/test_bench.py` pins the file to `corner_rows()` and the refusal rule and
checks that every twin is a trochoid build (a row the predicate ignores would be timed as a radial one).
`make bench.build SWEEP=bench/sweeps/trochoid.json` times each set as a worker pays it: a cold build, then
the fine STL and the STEP export, against `SPUR_BUILD_TIMEOUT` = 30 s. This is also the reading L37 asks
for ("Revisit when ... Phase 19's composed re-measure"). The script's output follows verbatim.

#### Host state

- Machine: Apple M5 Max (`sysctl -n machdep.cpu.brand_string`); `bench.machine_facts()`: 18 CPUs, arm64, 64.0 GiB RAM
- Python: 3.12.15
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `5f3df84`
- Sweep: `bench/sweeps/trochoid.json`
- Load averages at start: 3.40, 4.05, 5.10
- SPUR_BUILD_TIMEOUT: 30 s, a cold request is one build plus one export
- `uptime` before the first row: 11:52 local, load averages 3.26 4.04 5.10 (2026-10-09T05:52:35Z); after the last: 11:56 local, 7.70 6.45 5.96 (05:56:45Z)

#### Timings

| Parameter set | Build (s) | Fine STL (s) | STEP (s) | Build + slower export (s) | Inside 30 s | Fine STL (bytes) | Triangles |
|---|---|---|---|---|---|---|---|
| teeth=116 module=1.75 bore_hex=43.35 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | 9.94 | 0.43 | 0.38 | 10.37 | yes | 5898384 | 117966 |
| teeth=116 module=1.75 bore_hex=43.35 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 root_shape=trochoid | 10.81 | 0.48 | 0.35 | 11.28 | yes | 9656784 | 193134 |
| teeth=116 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | 9.26 | 0.43 | 0.35 | 9.69 | yes | 5935584 | 118710 |
| teeth=116 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 root_shape=trochoid | 10.24 | 0.49 | 0.36 | 10.73 | yes | 9693984 | 193878 |
| teeth=116 module=10 bore_hex=43.35 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | 10.79 | 0.54 | 0.39 | 11.33 | yes | 7298484 | 145968 |
| teeth=116 module=10 bore_hex=43.35 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 root_shape=trochoid | 11.73 | 0.59 | 0.39 | 12.32 | yes | 10708884 | 214176 |
| teeth=116 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | 10.78 | 0.55 | 0.38 | 11.33 | yes | 7354284 | 147084 |
| teeth=116 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 root_shape=trochoid | 11.86 | 0.59 | 0.37 | 12.45 | yes | 10764684 | 215292 |
| teeth=116 module=1.75 bore_hex=156.3 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | 9.17 | 0.32 | 0.27 | 9.50 | yes | 10223484 | 204468 |
| teeth=116 module=1.75 bore_hex=156.3 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 root_shape=trochoid | 14.28 | 0.36 | 0.25 | 14.64 | yes | 13981884 | 279636 |
| teeth=116 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | 4.67 | 0.91 | 0.22 | 5.58 | yes | 8951684 | 179032 |
| teeth=116 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 root_shape=trochoid | 4.87 | 0.95 | 0.19 | 5.83 | yes | 12710084 | 254200 |
| teeth=116 module=10 bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | 3.99 | 0.62 | 0.19 | 4.61 | yes | 13825284 | 276504 |
| teeth=116 module=10 bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 root_shape=trochoid | 3.89 | 0.69 | 0.17 | 4.58 | yes | 17235684 | 344712 |
| teeth=116 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | 4.11 | 0.67 | 0.20 | 4.77 | yes | 14545884 | 290916 |
| teeth=116 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 root_shape=trochoid | 4.10 | 0.73 | 0.17 | 4.84 | yes | 17956284 | 359124 |
| teeth=116 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hex_cell=3 hex_wall=0.4 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | 6.99 | 0.52 | 0.41 | 7.51 | yes | 5546684 | 110932 |
| teeth=116 module=1.75 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hex_cell=3 hex_wall=0.4 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 root_shape=trochoid | 7.08 | 0.55 | 0.37 | 7.63 | yes | 9305084 | 186100 |
| teeth=116 module=10 bore_hex=200 hex_cell=3 hex_wall=5 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | 7.82 | 0.64 | 0.44 | 8.46 | yes | 10425284 | 208504 |
| teeth=116 module=10 bore_hex=200 hex_cell=3 hex_wall=5 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 root_shape=trochoid | 8.00 | 0.68 | 0.41 | 8.68 | yes | 13835684 | 276712 |
| teeth=116 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hex_cell=3 hex_wall=5 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | 6.68 | 0.65 | 0.41 | 7.33 | yes | 7757084 | 155140 |
| teeth=116 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hex_cell=3 hex_wall=5 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 root_shape=trochoid | 6.93 | 0.70 | 0.41 | 7.63 | yes | 11167484 | 223348 |
| teeth=116 module=1.75 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | 3.73 | 0.41 | 0.19 | 4.14 | yes | 7420684 | 148412 |
| teeth=116 module=1.75 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 root_shape=trochoid | 3.62 | 0.44 | 0.16 | 4.06 | yes | 11179084 | 223580 |
| teeth=116 module=1.75 hole_count=60 hole_d=1 hole_circle_d=183.4 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | 1.09 | 0.91 | 0.17 | 2.01 | yes | 8921484 | 178428 |
| teeth=116 module=1.75 hole_count=60 hole_d=1 hole_circle_d=183.4 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 root_shape=trochoid | 1.25 | 1.03 | 0.16 | 2.28 | yes | 12679884 | 253596 |
| teeth=116 module=10 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | 7.21 | 0.54 | 0.35 | 7.75 | yes | 7324084 | 146480 |
| teeth=116 module=10 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 root_shape=trochoid | 8.49 | 0.56 | 0.33 | 9.06 | yes | 10757684 | 215152 |
| teeth=116 module=1.75 hex_cell=3 hex_wall=0.4 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 | 2.74 | 0.50 | 0.37 | 3.24 | yes | 5504484 | 110088 |
| teeth=116 module=1.75 hex_cell=3 hex_wall=0.4 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 root_shape=trochoid | 2.89 | 0.56 | 0.33 | 3.45 | yes | 9262884 | 185256 |
| teeth=116 pressure_angle=14.5 profile_shift=-0.6 module=10 | 0.70 | 0.66 | 0.15 | 1.35 | yes | 12991684 | 259832 |
| teeth=116 pressure_angle=14.5 profile_shift=-0.6 module=10 root_shape=trochoid | 0.86 | 0.75 | 0.14 | 1.61 | yes | 16425284 | 328504 |
| teeth=116 pressure_angle=14.5 profile_shift=-0.6 module=10 tip_chamfer=3 recess_sides=both | 3.54 | 0.64 | 0.19 | 4.18 | yes | 13014884 | 260296 |
| teeth=116 pressure_angle=14.5 profile_shift=-0.6 module=10 tip_chamfer=3 recess_sides=both root_shape=trochoid | 3.44 | 0.71 | 0.17 | 4.14 | yes | 16425284 | 328504 |

**Heaviest:** teeth=116 module=1.75 bore_hex=156.3 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 root_shape=trochoid -- 14.64 s of 30 s.
**Largest fine STL:** teeth=116 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both pressure_angle=14.5 profile_shift=-0.6 root_shape=trochoid -- 17956284 bytes, 359124 triangles.

The 1-minute load was above 1.5 for the whole run (3.3 to 7.7; the run's own build and export threads are
part of it), so every figure is an upper bound for this host and none is a bar.

**The heaviest row, against 30 s.** The runner exits 0: all 34 requests are inside 30 s. The heaviest is the
trochoid twin of the 116-tooth, module-1.75 gear with a 156.3 mm hex bore, 60 holes of 1 mm on a 183.4 mm
circle, the tip chamfer at 1.75 mm and both recesses: 14.28 s to build plus 0.36 s (STL) and 0.25 s (STEP),
**14.64 s of 30 s, 15.36 s of margin** (49 % of the timeout). It is the heaviest row of the whole sweep,
radial rows included (the heaviest radial request is 11.33 s). **Against its radial twin:** 9.50 s (9.17
build, 0.32 STL, 0.27 STEP), so the hob root costs 1.54 times the radial request on this row, the largest
of the 17 pairs. The other 16 pairs read 0.98 to 1.19 times (median over the 17, 1.06; 14 above 1, 3 below,
at 0.98, 0.99 and 0.99); the next heaviest are the module-10 keyed 32-spoke row at 12.45 s trochoid against
11.33 s radial (1.10) and the module-10 hex-bore 32-spoke row at 12.32 against 11.33 (1.09). **Against
19-01's spike reading of the same row:** 16.61 s trochoid (16.20 build) and 11.48 s radial, 1.45 times, at a
load of 4.86 rising to 9.48 on the same host. This run reads 1.97 s lower on the trochoid request
(14.64 against 16.61, 12 %) and 1.98 s lower on the radial one (9.50 against 11.48, 17 %) at a load of 3.3
rising to 7.7. Both are single readings under different loads, so this is not a delta and no cause is
isolated; what it supports is that the shipped build did not cost more than the bench copy it replaced on
this row, and that the margin to 30 s was 13.39 s in the spike and is 15.36 s here. The ratio rose from 1.45
to 1.54 because both requests fell by about the same 2 s.

**Against L37's 29.42 s row.** L37's heaviest allowed composed row is the 200-tooth, module-10 keyed
32-spoke composition (29.42 s alone on the 12-CPU M2 Max, 2026-09-30). It is not in this sweep and was not
re-run: at 200 teeth `rb <= rf` for every pressure angle and shift the field allows (the trochoid applies
only below 116.1 teeth, `CORNER`'s comment), so a trochoid request is ignored and warned (18 D-02,
`root_mode` answers "nothing radial to replace") and that request builds the radial part it built before.
The heaviest row a trochoid request can change reads 14.64 s on this host, half of L37's figure from
another host, so Phase 19's composed re-measure does not reach L37's row: its 503-under-load contract,
`SPUR_BUILD_TIMEOUT` = 30 s and `spoke_count`'s `le` of 32 stand. Nothing here is extrapolated to
concurrent load, and no figure is compared across hosts as a delta.

### The gate, priced (19-09)

What the phase cost the gate (L34, 66 s) and the commit slice (L36, 30 s), and what `derive()` costs per call
now that it asks `root_mode`. Everything is read on the host 19-01 read its before-figure on, so the delta
below is between two readings on one machine; the bars were set on another and are quoted, not compared with a
delta. HEAD for every run below is `4b08aa8` (19-09 Task 1, which added one test and touched only `bench/` and
`tests/test_bench.py` beyond the plans before it). The runs are consecutive, `uptime` before and after each, nothing else CPU-heavy
started by the executor.

#### Host state

- Machine: Apple M5 Max (`sysctl -n machdep.cpu.brand_string`), 18 CPUs, arm64, 64.0 GiB RAM: the host of
  `### Gate baseline (19-01)`, so a delta against its 52.89 s mean is valid
- The bars' host: L34 set 66 s on an Apple M2 Max with 12 CPUs (63.555 s read there); L36 read
  `make verify.fast` at 11.28 s warm on the same host. `PYTEST_WORKERS` is 8 on both machines. The bars are
  quoted as written, not rescaled, and no figure here is extrapolated to another host
- Python 3.12.15 (`.venv`), cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- Read 2026-10-09, 05:59 to 06:13 UTC for the runs, 07:32 UTC for the `derive()` re-read
- The 1-minute load rose with each run's own eight workers (4.03 before the first `make verify`, 9.06
  after the second), so every wall figure is an upper bound for an idle host and none is a bar

#### `make verify`, three runs

| Run | Result line | `real` (s) | 1-minute load before -> after | UTC |
|---|---|---|---|---|
| 1 | `1210 passed in 208.01s` | 208.52 | 4.03 -> 6.30 | 05:59:24 -> 06:02:52 |
| 2 | `1210 passed in 160.95s` | 161.71 | 6.30 -> 9.06 | 06:02:52 -> 06:05:34 |
| 3 | `1210 passed in 207.90s` | 208.60 | 9.06 -> 7.98 | 06:05:34 -> 06:09:02 |

Mean `real` **192.94 s** (pytest 192.29 s), range 161.71 to 208.60 s; coverage 97.90 % against the floor of 96;
all three green, no `ReentrantCallError`. **Against L34's 66 s bar: 2.92 times it, 126.94 s over.** **Delta
against `### Gate baseline (19-01)` on this host: +140.05 s (52.89 s mean to 192.94 s), 3.65 times, with 187
more tests (1023 to 1210).** The plan's gate stops here, because the mean is over 66.0 s; the human was asked
and answered `accept-A` on 2026-10-09 (below).

The cost accumulated wave by wave. These are the orchestrator's `make test` walls after each wave, same host,
the same caveat on load:

| After | Tests | `make test` wall |
|---|---|---|
| 19-01 baseline | 1026 | 52.89 s |
| wave 3 (19-04) | 1054 | 112.79 s |
| wave 4 (19-06) | 1081 | 137.76 s |
| wave 5 (19-07) | 1209 | 206.05 s |

Wave by wave the wall grew by 59.90 s (wave 3, 28 tests), 24.97 s (wave 4, 27 tests) and 68.29 s (wave 5, 128
tests); 19-09 added one test (1209 to 1210). The walls are single readings under different loads, so the steps
say where the cost entered, not what each test costs.

#### `make verify.fast`, three runs against L36's 30 s kill

| Run | Result line | `real` (s) | 1-minute load before -> after |
|---|---|---|---|
| 1 | `824 passed in 11.01s` | 11.46 | 6.34 -> 6.12 |
| 2 | `824 passed in 10.96s` | 11.39 | 6.12 -> 6.49 |
| 3 | `824 passed in 11.11s` | 11.54 | 6.49 -> 8.06 |

All three are inside the 30 s kill, at 824 tests, 11.39 to 11.54 s; L36's own reading was 11.28 s on the M2
Max. A commit does not pay the gate's extra time: the pre-push hook, CI and `make worktree.land` do.

#### Where the cost is: the 25 slowest calls

One `.venv/bin/python -m pytest -n 8 --cov --cov-report=term --durations=25 -q`: `1210 passed in 208.03s`,
`real` 208.23 s, load 8.06 -> 6.43. The 25 slowest call times sum to 340.5 s. **21 of them are this phase's
tests in `tests/test_model.py`, summing to 305.5 s**, which is 18.4 % of the 1,664 worker-seconds the run had
(208.03 s x 8 workers):

| Kernel-tier test | Rows in the 25 | Each (s) | Sum (s) |
|---|---|---|---|
| `test_the_built_root_is_the_oracle_s_root_on_every_kernel_row` | 7 | 11.1 to 21.6 | 92.0 |
| `test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore[trochoid-*]` | 12 | 12.5 to 21.4 | 169.5 |
| `test_the_kernel_tier_proof_fails_when_the_printed_tip_radius_is_off_by_0_05_mm` | 1 | 25.78 | 25.78 |
| `test_the_default_gear_asked_for_the_hob_root_builds_the_oracle_s_root` | 1 | 18.22 | 18.22 |

The listing stops at 25, so 305.5 s is a lower bound for the phase's share, not the whole of the 140.05 s
delta. The other four of the 25 are not this phase's: `tests/test_cli.py::test_readme_export_examples_run`
12.06 s, `tests/test_calc.py::test_the_trochoid_sweep_over_the_allowed_box` 8.80 s and two pool tests. The
oracle's 401 positions per row (19-02) set the kernel rows' cost; 19-02's `Method B against the number of
positions` table is the place that count was chosen.

#### `derive()` per call

`.venv/bin/python -m timeit -r 5 -s "from spur.calc import derive; from spur.params import GearParams;
p=GearParams()" "derive(p)"`, and the same with `p=GearParams(root_shape='trochoid')`, best of 5:

| Call | Best of 5 | UTC | 1-minute load before -> after |
|---|---|---|---|
| default `GearParams()` | 10.2 usec | 06:13:50 | 5.22 -> 4.96 |
| `GearParams(root_shape='trochoid')` | 29.8 usec | 06:13:51 | 4.96 -> 4.96 |
| default `GearParams()` | 10.3 usec | 07:32:45 | 2.55 -> 2.67 |
| `GearParams(root_shape='trochoid')` | 30 usec (timeit's own rounding) | 07:32:47 | 2.67 -> 2.67 |

19-04 read 10.3 and 29.6 usec at a load of 2.75 on this host. The hob root costs `derive()` about three times
the radial call, 20 usec, because it solves the curve once; against an HTTP round trip and the module
docstring's every-keystroke claim that stays negligible. The `derive()` docstring carries the second pair and
names the first.

#### Decision: `accept-A` (2026-10-09)

The mean is 2.92 times L34's 66 s bar, so the plan stopped and the human was offered three options: (A) accept
the measured cost and record it in L38 (Phase 12 D-10's precedent); (B) move named kernel rows out of the gate
into `bench/`, each named with its cost; (C) raise the bar with a new decision. The human's reply, verbatim:
`accept-A`. No test moves out of the gate, L34's 66 s is not changed and the oracle's 401-position count stays.
That leaves L34's 66 s on paper while the gate reads about 193 s on this host; re-setting the bar from an
idle-host reading, or a measured revisit of the per-row position count, is a separate decision and is not part
of this plan. L38 (19-10) records the cost.

### Waist at the smallest arc thickness (19-REVIEW CR-01)

The 19-02 walk above takes `RootCurve.waist` at the smallest half-angle `h` and prints `2 R h` there.
19-REVIEW CR-01 found that on a crossing join `d(R h)/dR = R' h` is positive at that point, so the arc
thickness is still falling below that radius and the printed `root_waist` was too thick. `_waist` now
minimises `R h` (the same 60-step golden section, the same neighbours of the smallest sample), so
`root_waist` is the narrowest arc. The walk table above is dated history and is not rewritten.

Read 2026-10-09 on the host of the walk above (18 CPUs, arm64, Python 3.12.15), from the curve alone, no
kernel and no oracle. Dense = the smallest of 40,000 samples of `2 R h` from the root circle to the
junction.

| Gear (module, pressure angle, shift, tip radius) | Printed before | Printed after | Dense minimum |
|---|---|---|---|
| 10 teeth, 1, 20, 0, 0.38 (backlash 0) | 1.473 | 1.442 | 1.442 |
| 7 teeth, 2, 25, 0.27, 0 | 3.269 | 3.149 | 3.149 |
| 8 teeth, 2, 25, 0.24, 1 | 3.536 | 3.428 | 3.428 |
| 8 teeth, 1, 14.5, -0.5132, 0.38 | 0.401 | 0.395 | 0.395 |
| 6 teeth, 1, 14.5, -0.3103, 0.38 | 0.401 | 0.391 | 0.391 |
| default gear (tangent join) | 3.303 | 3.303 | 3.303 |

The last two gears sit just under the 0.4 mm floor: the old reading printed 0.401 and warned on neither.

The walk and the product re-counted with the same code (`bench.trochoid_part`'s `WALK_*` grid and
`product_waists()`), old definition reproducing L38's figures first:

| | Before | After |
|---|---|---|
| Walk trochoid gears under 0.4 mm | 294 of 1,061 | 303 of 1,061 |
| Product gears under 0.4 mm (unrounded) | 771 of 10,326 | 775 of 10,326 |
| Thinnest walk waist, mm | 3.2325e-3 | 3.2317e-3 |
| Thinnest product waist per module, mm | 2.5577e-3 | 2.5574e-3 |

The floor is unchanged at 0.4 mm and stays 124x the thinnest walk waist. The kernel and oracle columns of
the walk were not re-read: no curve moved, only which point of it is called the waist.

## Browser test of the viewer (Phase 21)

What Phase 21 priced and proved about the shipped page in a real browser, in plan order: the spike on macOS
(21-01), the Linux runner spike (21-02), the golden request pin (21-05), the gate's admission (21-06), the
browser test priced (21-07) and the Linux path on the real runner (21-08). Each subsection carries its own host
state, because the figures below are read on different machines on different days and are never compared
across them. Nothing here is a bar unless it says so beside the reading that set it (L08).

### Spike readings, macOS (21-01)

The tracer: `playwright==1.63.0` pinned in the `[dev]` extra, its headless shell installed under `.venv` by the
`$(BROWSER)` stamp, a real `uvicorn` on a pre-bound socket, the shipped page opened in Chrome Headless Shell.
HEAD for the readings is `593de97` (the 21-01 test commits on the phase branch); the PNG sizes were first read
on the uncommitted tree over `a310cd3` and read the same again at `593de97`. `tests/browser_scenarios.py`
is a staging module that nothing in `make verify` collects yet (PD-01).

#### Host state

- Machine: Apple M5 Max (`sysctl -n machdep.cpu.brand_string`), 18 CPUs, arm64, 64 GiB RAM
- macOS 27.0.1, Darwin 27.0.0 kernel (`xnu-13432.1.9~1/RELEASE_ARM64_T6050`)
- Python 3.12.15 (`.venv`), `playwright` 1.63.0, `uvicorn` 0.54.0
- Shell: Chrome Headless Shell 153.0.8010.12 (`browser.version`; Playwright `chromium-headless-shell` v1243)
- Read 2026-10-10, about 09:26 to 09:45 UTC
- 1-minute load: 4.15 before the install, 3.31 before the first reading, 4.67 to 4.80 around the three isolated
  runs, 3.22 before and 9.37 after the first `make verify` (its own eight workers). The host has ten logged-in
  users and was never idle, so every wall figure is an upper bound and none is a bar

#### Readings

| Reading | Value |
|---|---|
| `make .venv/.browser` from a venv without the pin | 20.46 s `real`: the `$(STAMP)` re-resolve (playwright 1.63.0, pyee 13.0.1, greenlet 3.5.6) plus the 94.3 MiB shell and a 1 MiB ffmpeg. The research's 16.4 s was the shell alone |
| Size of `.venv/ms-playwright` | 198 MB (`chromium_headless_shell-1243`, `ffmpeg-1011`) |
| Host cache `~/Library/Caches/ms-playwright`, before the install | `chromium_headless_shell-1228`, `chromium-1228`, `ffmpeg-1011` |
| Host cache, after the install | the same three entries (D-06: another project's browser untouched) |
| `/api/health` reports a non-null `pool` | 0.20, 0.20, 0.21 s after spawn |
| Group members seen before the kill | 3 (uvicorn and two pool workers) in all three timing runs and every test run. Before the first build the group read 2: pool workers start on first use |
| Teardown, SIGTERM to group empty and leader reaped | 0.25, 0.24, 0.25 s |
| Renderer string | `ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (LLVM 10.0.0) (0x0000C0DE)), SwiftShader driver)` |
| Canvas PNG, blank control (same `#canvas`, STL request parked) | 3,917 B |
| Canvas PNG, first part drawn | 38,908 B |
| Ratio drawn / blank | 9.93 |
| Canvas PNG with `scene.add(mesh, edges);` deleted (grid and background only) | 16,627 B, ratio 4.24 |
| `data-triangles` against the STL header (uint32 at byte 80) | 9066 against 9066 |
| `expect`'s default timeout | 5000 ms (Playwright's own line: `Expect "to_have_count" locator("form#params [name]") with timeout 5000ms`) |
| Form fields | 31, equal to the `/api/schema` property count read at test time |
| Slowest build-bound step | 2.53 s (`first build drawn`), under PD-04's 15 s, so `BUILD_WAIT_MS` stays 45,000 ms |
| `git status --porcelain --ignored` after a green run | nothing outside `.venv/` and the ignores already in place (`.coverage`, caches, `__pycache__`, `web/node_modules`); the test writes no file (PD-10) |

`PNG_RATIO_BAR` by PD-03, written in the plan before this reading: the lower of the hosts' drawn/blank ratios
divided by 2, rounded down to one decimal place. Only macOS is read here: 9.93 / 2 = 4.96, rounded down to
**4.9**, which is not under 2.0, so it is asserted. 21-02 re-sets it from the lower of the macOS and
ubuntu-latest readings. The bar separates a gear from a scene without one by a narrow margin (4.24 against
4.9 with the mesh deleted, 9.93 with it), which is why the deliberate break below went red on the ratio alone.

Per step, three isolated runs (`make test PYTEST_ARGS="tests/browser_scenarios.py -n0 --no-cov -q -s"`), load
before the run in brackets:

| Run | `webgl2` | `form built` | `first build drawn` | `href after showModel` | pytest | `make` `real` |
|---|---|---|---|---|---|---|
| 1 (4.67) | 0.01 s | 0.06 s | 2.49 s | 0.02 s | 3.43 s | 3.64 s |
| 2 (4.67) | 0.01 s | 0.06 s | 2.52 s | 0.04 s | 3.40 s | 3.59 s |
| 3 (4.70) | 0.01 s | 0.05 s | 2.53 s | 0.04 s | 3.40 s | 3.59 s |

The research read 3.21 s for the serial scenario on this host; the isolated runs read 3.40 to 3.43 s of pytest
(3.59 to 3.64 s with `make`), at load 4.7 against the research's 7 to 8. The difference is inside what a loaded
host moves, so the 3.2 to 3.8 s order of magnitude that D-01 rests on holds. The first reading of the day
(cold shell) read `webgl2` at 0.35 s and `first build drawn` at 2.15 s.

The whole gate with the staging module present and uncollected: `make verify` read `1220 passed in 155.30s
(0:02:35)`, TOTAL coverage 97.92 % against the 96 % floor, and `1220 passed in 198.00s (0:03:17)` on the second
run at a higher load. Neither is a bar; Phase 25 owns that.

### Seen red once (Phase 21)

Every assertion the tracer makes, shown red once against a deliberate break, reverted before any commit. Later
plans append rows to this table.

| Plan | Step or pin | Deliberate break | First failure line | Reverted |
|---|---|---|---|---|
| 21-01 | `webgl2` | `launch()` passes `args=["--disable-3d-apis"]` | `1 failed`: `AssertionError: this browser gives no WebGL2 context: the viewer builds no form without WebGL (app.js:229)`, note `step: webgl2` | yes, `git diff --exit-code` clean |
| 21-01 | `first build drawn`, canvas | `scene.add(mesh, edges);` deleted in `app.js` | `AssertionError: the canvas looks undrawn: PNG 16627 B against a blank 3917 B is 4.24x, bar 4.9`, note `step: first build drawn`; `data-triangles` still read 9066 against the header's 9066, so the triangle check alone would have passed | yes |
| 21-01 | `first build drawn`, triangles | `/ 3` changed to `/ 9` in the new `app.js` line | `AssertionError: the scene holds 3022 triangles, the STL header declares 9066`, note `step: first build drawn` | yes |
| 21-01 | `href after showModel` | `setDownloads(q);` moved above `showModel(buf);` in `update()` | `AssertionError: the STL link has an href although showModel failed on the body` (`assert 'api/model.stl?teeth=23' is None`), note `step: href after showModel` | yes |
| 21-01 | fail closed | `PLAYWRIGHT_BROWSERS_PATH` set to an empty temporary directory, pytest run directly | `1 failed in 0.69s`: ``Failed: the headless shell is not installed: run `playwright install --only-shell chromium` (PLAYWRIGHT_BROWSERS_PATH=/var/folders/g1/qxn3_5tx48xg4srplqpp46140000gn/T/tmp.TKWFihxa3O); `make test` runs the install stamp for you.``, then Playwright's own error | yes (nothing to revert: the variable was set for one command) |
| 21-01 | no orphan after the kill | `stop_group` sends SIGKILL to the leader only (`os.kill(pgid, SIGKILL)` for `os.killpg`) | `Failed: server process group 66058 still has live pids [66059, 66066] after SIGTERM, SIGKILL and 5 s`, then the server log tail (reported as a teardown error after `1 passed`); the two pool workers were killed by group id afterwards | yes |
| 21-01 | strict typing | `eval_int` returns `page.evaluate(expression, arg)` directly | `tests/browser_session.py:213: error: Returning Any from function declared to return "int"  [no-any-return]` from `make typecheck` | yes |
| 21-03 | `form from schema`, order | `Object.entries(schema.properties)` becomes `Object.entries(schema.properties).reverse()` in `buildForm()` (`app.js`) | `AssertionError: form fields ['hex_wall', 'hex_cell', ...] differ from the schema's, grouped: ['teeth', 'module', ...]`, `At index 0 diff: 'hex_wall' != 'teeth'`, note `step: form from schema` (the form-built count wait still passed: 31 fields either way) | yes, `git diff --exit-code` clean |
| 21-03 | `form from schema`, theme variable | `--grid:` renamed `--grid-x:` in both blocks of `style.css` | `AssertionError: the custom property --grid is empty on :root`, note `step: form from schema` (the page still loaded and built its form) | yes |
| 21-03 | `invalid field marked`, `bore_flat=3` | `...(d.ctx?.fields ?? [])` removed from the array in `problems()` | `AssertionError: #bore_flat=3: marked [], the 422 names ['D-flat']` | yes |
| 21-03 | `invalid field marked`, `teeth=2` | `d.loc?.[1],` removed from the same array | `AssertionError: #teeth=2: marked [], the 422 names ['Teeth']` | yes |

### Linux runner spike (21-02)

The tracer run inside the whole gate on a real `ubuntu-latest` runner, with the headless shell installed through
`playwright install --with-deps --only-shell chromium` (sudo, apt). Branch `spike/21-linux-runner`, one commit
`a6a4fc5` on top of the phase branch's `e5deff8` (the admission wiring 21-06 will land for real: the module
renamed `tests/test_browser.py`, `test: $(STAMP) $(BROWSER)`, the `--ignore` in `test.fast` and `test-image`,
`BROWSER_INSTALL_ARGS: --with-deps` and `PYTEST_ARGS: -rP` in `ci.yml`, a `runner hardware (spike only)` step).
Draft PR #32, `spike(21): browser tracer on ubuntu-latest -- DO NOT MERGE`, never merged; the spike branch is not
an ancestor of the phase branch. The whole log is kept at
`.planning/phases/21-browser-test-of-the-viewer/investigation/21-02-run-38044109910.log`.

| Run | Conclusion | Classification |
|---|---|---|
| 38044109910 (`ci`, head `a6a4fc5`, 2026-10-10 10:12:40Z) | success (`test (3.12)`, `vendor-bundle`, `image` all green) | none to classify: first push, no red run; one run of the three allowed |

#### Host state (the runner)

- Image `ubuntu-24.04`, version `20261004.327.1`, provisioner `20261002.596`, runner 2.337.0
  (the `Set up job` group); kernel `6.17.0-1022-azure #22-Ubuntu SMP Mon Jul 27 17:24:03 UTC 2026 x86_64`
- `nproc` 4; `free -m` read after the run: total 15,989 MB, used 1,028, free 9,107, buff/cache 6,247, available
  14,961, swap 3,071 (unused)
- Python 3.12.15 (`actions/setup-python@v5`, cache hit); `playwright` 1.63.0 (`manylinux1_x86_64` wheel, 48.2 MB);
  shell Chrome Headless Shell 153.0.8010.12 (`chromium_headless_shell-1243`, plus `ffmpeg-1011`, the whole
  `ls .venv/ms-playwright`)
- `make verify` ran `pytest -n 4` (`PYTEST_WORKERS` is capped by the CPU count); the tracer ran on worker `gw2`
  beside three other workers
- Read 2026-10-10 10:12 to 10:29 UTC. A shared runner: load is not observable from the log, so every wall figure
  is one sample

#### Readings

| Reading | Value |
|---|---|
| `test (3.12)` job wall time | 16 min 25 s (`startedAt` 10:12:43Z, `completedAt` 10:29:08Z); `1221 passed in 906.71s (0:15:06)`, TOTAL coverage 97.98 % against the 96 % floor |
| Install, `playwright install --with-deps --only-shell chromium` | 14.7 s from the command line (10:13:43.916) to the next command's line (10:13:58.578): `Switching to root user to install dependencies...`, `apt-get update`, 79.5 MB of apt packages (fonts, `libfreetype6` upgraded), then the 3.3 s shell download and the ffmpeg download |
| Size of `.venv/ms-playwright` on the runner | not measured: the diagnostic step ran `ls`, not `du`. macOS read 198 MB for the same two entries |
| Renderer string | `ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (Subzero) (0x0000C0DE)), SwiftShader driver)` (macOS: `(LLVM 10.0.0)`) |
| `webgl2` step | 0.04 s |
| `form built` step | 0.16 s |
| Canvas PNG, blank control | 3,654 B |
| Canvas PNG, first part drawn | 38,168 B |
| Ratio drawn / blank | 10.45 (macOS 9.93) |
| `data-triangles` against the STL header | 9066 against 9066 |
| `first build drawn` step | 4.75 s (macOS 2.53 s) |
| `href after showModel` step | 0.25 s |
| Server process group members before the kill | 3 (uvicorn and two pool workers), read by `ps -A -o pgid=,stat=,pid=` on the runner's procps. The post-kill zero was read by the same reader: the teardown that asserts it ran and the test is in the passed set. The runner's log does not print the group-gone time |
| Same job on `main`, for scale (same workflow, `pytest -n 4`, no browser) | 8 min 54 s job, `1220 passed in 487.39s` (run 38040124903, 2026-10-10); 16 min 04 s, `894.96s` (37951628866, 2026-10-09); 16 min 35 s, `924.02s` (37930095920, 2026-10-09) |

The three `main` runs differ from each other by up to 437 s of pytest wall with no change to the suite, which is
more than the spike run differs from the two slower of them. The spike run's own 906.71 s therefore sits inside
the runner-to-runner band, and these samples cannot show what the browser test adds: its own steps total about
5.2 s. Phase 25 owns pricing the gate.

#### The two rules applied

- **PD-03** (canvas bar = the lower of the hosts' ratios / 2, rounded down to one decimal place): the lower ratio
  is macOS's 9.933 (38,908 / 3,917); 9.933 / 2 = 4.966, rounded down to **4.9**. Linux's 10.446 (38,168 / 3,654)
  is higher, so `PNG_RATIO_BAR` stays 4.9 and is not under 2.0. The macOS scene with the mesh deleted read 4.24,
  so the bar still separates a gear from an empty scene on the lower host.
- **PD-04** (build wait): the slowest build-bound step on either host is `first build drawn`, 2.53 s on macOS and
  4.75 s on Linux. Neither is over 15 s, so `BUILD_WAIT_MS` stays **45,000 ms**.

Both constants in `tests/browser_session.py` carry both readings in their comments; neither value changed.

#### Answers to the research's assumptions

- **A1, sudo through `--with-deps`:** works on `ubuntu-latest` as is, with no `sudo` in the workflow: Playwright
  prints `Switching to root user to install dependencies...` and runs apt itself. It costs about 10 s of the
  14.7 s (the rest is the shell download).
- **A2, the Linux PNG against macOS:** the same shell draws a larger ratio on Linux (10.45 against 9.93), on
  SwiftShader Subzero rather than LLVM 10.0.0. Blank and drawn byte counts differ by about 7 % and 2 % from
  macOS, so the ratio, not an absolute size, is the right assertion, and the bar holds on both.
- **A4, procps columns:** the `ps -A -o pgid=,stat=,pid=` reader works on the runner's procps: the pre-kill floor
  of 3 members held and the teardown, which fails on any survivor, passed.
- **A7, memory:** no out-of-memory kill and no failure in a 15 GiB, 4 CPU runner with the tracer beside three
  other workers; `free -m` read after the run (1,028 MB used) is not a peak, and no peak was measured.
- **A8, runner image:** `ubuntu-24.04`, version `20261004.327.1`.

SC5's own real run is 21-08's, on the phase's head. This one is the spike's.
