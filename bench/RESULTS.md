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
