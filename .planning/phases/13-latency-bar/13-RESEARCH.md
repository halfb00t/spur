# Phase 13: Latency Bar - Research

**Researched:** 2026-10-01
**Domain:** Internal measurement/investigation (no new library, no `src/` change) — verifying
CONTEXT.md's code citations against the live tree, settling one code-level ASSUMPTION, and
mapping the 02-era investigation harness shape so the planner can name scripts/fields without
inventing.
**Confidence:** HIGH — every claim below was checked by opening the cited file this session
(`Read`/`grep -n`/`sed -n`) and quoting the actual lines, not by memory or web search. This
phase is internal-only (ROADMAP "Research flag: No"); no external provider/doc lookup applies.

## Summary

CONTEXT.md's code citations are **almost entirely accurate**: every function name, every line
number in `bench/latency.py`, and the ten SC3 row indices against `bench/sweeps/composed.json`
check out exactly. Three citations in `src/spur/app.py` and `bench/RESULTS.md` are off by enough
to matter for a planner who trusts the line range literally rather than the function name: the
`_max_queued_builds`/`MAX_QUEUED_BUILDS`/`BUILD_QUEUE` range should read 91–102 (not 91–96 —
`MAX_QUEUED_BUILDS` and `BUILD_QUEUE` themselves sit at 101–102, outside the cited range), the
`BuildTimeout` mapping range should read 435–446 (not 435–463 — 463 falls inside the next
`except BrokenProcessPool` block), and `bench/RESULTS.md`'s Latency section runs lines 34–279,
not 34–247 — the cited 247 cuts off **before** the two named observations, which actually live
at lines 252–268, and before the `SPUR_BUILD_TIMEOUT` subsection (271–279) entirely.

The more substantive finding is in `src/spur/pool.py`: CONTEXT.md's `<specifics>` ASSUMPTION says
"`recreate_for` terminates every process of the slot's executor." Reading the code shows this
attributes the termination to the wrong function. `recreate_for` (lines 99–155) never calls
`proc.terminate()` — it only does a non-blocking `shutdown()` on the stale executor object and
swaps in a fresh `ProcessPoolExecutor`. The actual `proc.terminate()` loop lives in the
**caller**, `_run_with_timeout`'s timeout branch (lines 204–206), which runs *before*
`recreate_for` is invoked. The aggregate behaviour CONTEXT.md describes (a timeout kills the
worker and replaces the whole slot) is correct; the function attribution is not. The other half
of the ASSUMPTION — that queue wait inside a slot counts toward the 30 s timeout — is directly
confirmed: `asyncio.wait_for(future, timeout=self.timeout)` (line 183) wraps a future created at
line 181 by `loop.run_in_executor(executor, ...)`, and that submission happens immediately,
before the single-worker executor's queue has necessarily started the task. The wait clock runs
from submission, not from execution start.

A separate, concrete trap for session mechanics: `make bench.latency` runs `python -m
bench.latency` with **no arguments** (`Makefile` line 117) against `bench/latency.py`'s
`DEFAULT_BASE_URL = "http://127.0.0.1:8000"` (line 28). Every recorded session in
`bench/RESULTS.md` ran the server on `SPUR_PORT=8001` because port 8000 is held by the
`spur-spur-1` container — which means the literal `make bench.latency` target was **never**
what produced any of the eight recorded runs. The planner must have every session invoke
`.venv/bin/python -m bench.latency --base-url http://127.0.0.1:8001 [scenario]` directly; running
the bare `make` target against a server on 8001 would silently measure the unrelated
`spur-spur-1` container's `/api/health` instead — a plausible-looking but wrong number, exactly
what L08 forbids.

**Primary recommendation:** Trust CONTEXT.md's design and function names; correct the three line
ranges above when citing code in the plan; attribute process termination to
`_run_with_timeout`'s timeout branch, not to `recreate_for`, in any plan text or debt file that
describes the mechanism; and make every bar/investigation session script call
`bench.latency`'s functions with an explicit `--base-url http://127.0.0.1:8001`, never the bare
`make bench.latency` target, while the server runs off the default port.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Investigation design**
- **D-01:** Three pair legs separate the three candidates for observation 1 (the second run of
  a pair always reads worse). Each leg is two back-to-back runs of `make bench.latency` in Runs
  1–8's exact shape (`single` then `concurrent`, D-08): **Pair A** same server, same teeth
  190–199 — the baseline reproduction; **Pair B** same server, run 2 on teeth 180–189 — cold
  export cache, warm workers; **Pair C** a server restart between the runs — everything cold. A
  split-process poller (02's `poller.py` shape) rides beside every run.
- **D-02:** Observation 2 (the ~0.1 ms floor) is measured from raw samples, not asserted. Every
  run's `(timestamp, latency)` samples are saved as JSONL; p95 is recomputed at full float
  precision and reported to 3 dp (µs). The write-up reports p94/p95/p96 and the count of samples
  at the timer's quantum, and states whether the pass/miss flips inside one percentile.
- **D-03:** Scripts and raw results live in the phase directory and ride the PR:
  `.planning/phases/13-latency-bar/investigation/` holds `poller.py`, `run_experiment.py`, every
  run's JSONL and a per-run JSON summary; the write-up cites them by file name. Not under
  `bench/` (SC1 forbids a `bench/` change under this requirement), not part of `make verify`.
  Reversible — files under `.planning/`, no code path depends on them.
- **D-04:** Each pair runs twice; both repetitions must point the same way before a candidate is
  ruled in or out. Twelve runs plus pollers. A split reads as "not separable on this host."
  Predictions per candidate are pre-registered in the write-up before the first run.

**Session rules**
- **D-05:** A session is decisive only when it met the quiet bar: release the pair only after
  three consecutive 30 s samples of 1-minute `sysctl -n vm.loadavg` under 1.5, with a 15-minute
  cap. On cap expiry the pair runs anyway, is recorded as measured, and is marked
  **non-decisive**. The same rule gates every session in the phase.
- **D-06:** `spur-spur-1` stays up on `:8000`; `fleet-user` is stopped for the sessions. The
  service under test serves on `SPUR_PORT=8001`. Reversible — `docker start`.
- **D-07:** Outcome (a) gets one decisive session. One pair on the unmodified `make
  bench.latency`, no extra poller, on a session that met D-05. Both `concurrent` runs ≤ 2.00× →
  (a), recorded. Either run over → (b) is taken, with the investigation's surviving cause as its
  reason.
- **D-08:** Both scenarios, in Runs 1–8's order. Every pair runs `single` then `concurrent`
  exactly as `make bench.latency` does.

**Outcome (b) and the record**
- **D-09:** (b)'s change is chosen at a checkpoint with the numbers, with the first offer fixed
  now by the surviving cause: observation 1's cause (cache carryover or worker state) → a server
  restart between runs becomes the harness's protocol; observation 2's cause (the verdict flips
  inside one percentile) → an absolute threshold the harness can resolve (D-10); a higher
  `MIN_SAMPLES` only if the floor analysis shows the sample count is the problem. The change is
  logged as L32 with the measured reason and re-measured on both runs of one decisive session.
- **D-10:** If the floor survives, the threshold keeps the ratio and adds a floor: pass =
  under-load p95 ≤ max(2.00 × idle p95, idle p95 + M ms), where M is set from the floor analysis
  (on the order of 10× the measured per-sample resolution) and recorded in L32 together with the
  samples that set it. Reversibility: costly — the bar's published definition changes.
- **D-11:** A double miss halts; the debt stays active. If (b)'s re-measurement on the changed
  harness also misses on both runs, the phase halts at a checkpoint with the numbers. The debt
  file is **not** retired; SC4 recorded as not met.
- **D-12:** One L32 in L27–L31's shape, amending L18 (append-only): the two observations with the
  candidate that survived and the measurement that ruled the others out, outcome (a) or (b) with
  the decisive session's numbers, the SC3 reading, the environment change (D-06) — each cited to
  the write-up or a `bench/RESULTS.md` section, none re-estimated. L18's own text is untouched.
  The Dockerfile `HEALTHCHECK` comment (lines 41–50) does **not** cite the ≤ 2× bar; its
  "measured under-load p95 is 0.7–2.3 ms across the eight bench/RESULTS.md latency runs" sentence
  is updated to the new run count and worst reading.

**SC3 — the composed worst row under ten concurrent builds**
- **D-13:** The worst row plus the composed sweep's next nine heaviest rows (ten distinct keys,
  so admission control takes 4 and hash affinity spreads the admitted builds over both workers).
  Rejected: ten identical worst-row requests (measures the timeout's queue-wait semantics, not
  kernel contention — see `<deferred>`); both scenarios as two rows.
- **D-14:** `bench/RESULTS.md` records a per-request table plus the health ratio: one row per
  request — parameters, outcome (admitted / `503` refused / timeout), wall time — the worst
  row's own time named against 30 s, `/api/health`'s `workers_replaced` before and after, and the
  idle/under-load p95 ratio from the same poller the investigation uses.
- **D-15:** The SC3 scenario is a third scenario in `bench/latency.py`, landed in its own commit
  after the bar's decisive session. It reads its rows from `bench/sweeps/composed.json`,
  registers in `_SCENARIOS`, runs as `python -m bench.latency <name>`, and gets a
  `tests/test_bench.py` row; `scenario_single` and `scenario_concurrent` are untouched.
  Reversible — an added scenario; deleting it changes no bar.
- **D-16:** SC3 runs on its own fresh server, after the decisive session and before the close,
  under D-05's quiet rule. A timed-out worker is replaced (`pool.recreate_for`) and must not
  pollute a bar session; the quiet wait applies with the same 15-minute cap, and the run is
  recorded as measured either way.

**Contract and process**
- **D-17:** No `src/` change in this phase. The investigation forbids it (SC1); the bar's (b)
  touches only `bench/latency.py` under L32; SC3 adds to `bench/latency.py` and
  `tests/test_bench.py`; the Dockerfile comment is prose. `tests/regression/pre_v0_2.json` is
  byte-unchanged by construction; `GearParams` gains no field. Anything found in the server is
  filed as debt with a trigger and severity, never fixed here.
- **D-18:** Process. The phase runs on `gsd/phase-13-latency-bar`, cut from `origin/main`
  (`9f26052`), and lands via `make pr.land PR=N`. Commits are plain `git commit` with explicitly
  staged files (the `make verify` hook runs ~3.5 min at 907 tests). The debt file retires in the
  commit that demonstrates or supersedes the bar.

### Claude's Discretion
- The pre-registered prediction table (D-04): one row per candidate × pair leg.
- Script names, JSONL field names, the per-run summary's fields, and whether
  `run_experiment.py` drives `make bench.latency` as a subprocess or imports `bench.latency`'s
  functions unmodified (02 imported `_sample_for`, `_sample_while_building`, `_build`, `_p95` —
  never reimplement the harness's own sampling).
- The write-up's section order within 02's shape (Question, Environment, Method, Results,
  Verdict, Recommendation, Cleanup) and its file name (`13-LATENCY-INVESTIGATION.md`).
- What the host-state header records beyond Runs 7–8's set — at least: `fleet-user` stopped
  (D-06), the commit under test, `SPUR_*` values (shipping defaults).
- The SC3 scenario's name, its firing order mechanics, how per-request outcomes are read, and
  whether the health poller's samples from SC3 feed the same floor analysis.
- The order of plans: investigation scripts/runs first; the write-up; the decisive session;
  (b)'s checkpoint if reached; the SC3 scenario and run; L32/Dockerfile/`RESULTS.md`/debt
  retirement last, citing shas.
- The restart-between-runs rule's enforcement if D-09 adopts it: a documented protocol
  (`bench/README.md`, the `RESULTS.md` header) at minimum.

### Deferred Ideas (OUT OF SCOPE)
- Ten identical worst-row requests (the queue-wait scenario) — not run (D-13); if SC3's
  per-request table shows a queued request's timeout terminating an in-flight build, the
  behaviour is filed as a debt item with the measurement (D-17), and the identical-key scenario
  becomes that file's "next step."
- Server-side admission for cache-hit sends — if candidate (1) survives, bounding the concurrent
  large-body sends is a `src/` change outside this phase.
- L17's `mem_limit: 4g` re-sweep on v0.2 topology — not this phase's.
- Refreshing `.planning/codebase/*.md` — process, not product.
- A `make bench.latency SCENARIO=` argument — a convenience, not a requirement.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-latency-observations-explained | The two observations get a cause ruled in or out by the bounded investigation, written up in 02's shape; no `src/` or `bench/` change | "Investigation Harness Shape" section below maps exactly which `bench.latency` functions `run_experiment.py` imports unmodified, how `poller.py` runs as a split process, and what per-run fields the 02 write-up's tables carried — so the planner names scripts/JSONL fields without inventing. "Verified Code Citations" confirms the exact `bench/latency.py` line numbers the investigation scripts must import from. |
| REQ-latency-bar-demonstrated-or-superseded | One of two outcomes, never a third; SC3's composed worst row measured once; debt file retires | "Session Mechanics" section documents the port-8001 `--base-url` trap, the `sysctl -n vm.loadavg` quiet-wait shape, and the `fleet-user` stop/start reversibility a decisive session depends on. "Settled ASSUMPTION" section gives the planner the corrected mechanism (timeout → `_run_with_timeout` terminates processes → `recreate_for` swaps the executor) so SC3's per-request table and any debt file it produces describe the real code path. |
</phase_requirements>

## Architectural Responsibility Map

This phase has no new user-facing capability and no browser/frontend tier at all — it is a
measurement phase over an existing API/Backend topology. The standard tier table is a poor fit;
mapped here for completeness against what the phase actually touches:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `/api/health` latency measurement | Measurement harness (`bench/latency.py`, a host CLI process) | API / Backend (`src/spur/app.py::health()`) | The harness is a separate OS process polling the API from outside; it is not part of the service's own deployment tier, but it measures the API tier's responsiveness under the Backend's own admission control. |
| Per-build timeout & worker replacement | API / Backend (`src/spur/pool.py`) | — | `BuildPool._run_with_timeout`/`recreate_for` are server-internal process-pool management; no client or browser involvement. |
| Build admission control | API / Backend (`src/spur/app.py::_build_slot`) | — | In-process semaphore gating `/api/model.*`; purely server-side. |
| Decision/record-keeping (L32, debt retirement, RESULTS.md) | Documentation / Process | — | Not a runtime tier; a `.planning`/`docs/` artifact concern, included for completeness since SC4 is a phase success criterion. |

No Browser/Client, Frontend-SSR, CDN/Static, or Database tier is implicated by this phase.

## Verified Code Citations

Every row below was checked by opening the file this session. "Match" means CONTEXT.md's
function name, line number, and described behavior are all accurate as cited. "Correction" means
at least one of those three is off.

### `bench/latency.py` — all citations VERIFIED exact

| Symbol | CONTEXT.md cite | Actual | Status |
|---|---|---|---|
| `MIN_SAMPLES` | 20, `statistics.quantiles` bucket count | Line 43: `MIN_SAMPLES = 20` | [VERIFIED: bench/latency.py:43] |
| `_p95` | line 48 | Line 48: `def _p95(samples: list[float]) -> float:` | [VERIFIED: bench/latency.py:48] |
| `_sample_for` | line 59 | Line 59: `def _sample_for(base_url: str, client: httpx.Client, duration: float) -> list[float]:` | [VERIFIED: bench/latency.py:59] |
| `_sample_while_building` | line 70 | Line 70: `def _sample_while_building(...)` | [VERIFIED: bench/latency.py:70] |
| `_build` | line 86; `503` → `None`, other non-2xx raises | Line 86: `def _build(...)`; line 99 `if response.status_code == 503: return None`; line 101 `response.raise_for_status()` | [VERIFIED: bench/latency.py:86,99,101] |
| `scenario_concurrent` | line 135; teeth 190–199, `ThreadPoolExecutor(max_workers=10)` | Line 135: `def scenario_concurrent(...)`; line 141 `ThreadPoolExecutor(max_workers=10)`; line 143 `for teeth in range(190, 200)` (= 190..199 inclusive) | [VERIFIED: bench/latency.py:135,141,143] |
| `_SCENARIOS` | line 149 | Line 149: `_SCENARIOS: dict[str, Callable[[str], ScenarioResult]] = {` | [VERIFIED: bench/latency.py:149] |
| `_p95_or_warn` | line 155 | Line 155: `def _p95_or_warn(...)` | [VERIFIED: bench/latency.py:155] |
| `_report_markdown` | line 168; `:.1f` ms print, ratio on raw floats | Line 168: `def _report_markdown(...)`; line 171 `ratio = load_p95 / idle_p95 ...` (raw float division); lines 175–176 `f"- Idle p95: {idle_p95 * 1000:.1f} ms ..."` | [VERIFIED: bench/latency.py:168,171,175-176] |
| `main` | line 200; scenario argument | Line 200: `def main(argv: list[str] \| None = None) -> int:`; line 206 `parser.add_argument("scenario", ...)` | [VERIFIED: bench/latency.py:200,206] |

**D-02's own claim re-confirmed from code:** the report prints p95 at one decimal of a
millisecond (`:.1f`) while the ratio is computed on the raw, unrounded float division
(`load_p95 / idle_p95`) — so a "0.1 ms apart" reading in `bench/RESULTS.md`'s prose genuinely is
the *print format's* resolution, not necessarily the samples' real separation. The investigation
write-up's JSONL-based p95 recomputation (D-02) is the only way to tell the two apart.

### `src/spur/pool.py` — one substantive correction, one claim confirmed

| Symbol | CONTEXT.md cite | Actual | Status |
|---|---|---|---|
| `executor_for` | line 97: `hash(p) % self.workers` | Line 97: `return self._executors[hash(p) % self.workers]  # D-07: affinity, not load-balance` | [VERIFIED: src/spur/pool.py:97] |
| `recreate_for` | lines 123–155: "terminates every process of the slot's executor" | Lines 123–155 are the function's **executable body** (def is at line 99, docstring 100–122); but the body itself (line 151) does `self._executors[i].shutdown(wait=False)` — a non-blocking, non-forceful shutdown — then (152–153) constructs a fresh `ProcessPoolExecutor`. **It never calls `proc.terminate()`.** | **[CORRECTED — see below]** |
| `_run_with_timeout` | lines 157–220: `asyncio.wait_for(future, timeout=self.timeout)` at submit — queue wait counts toward the 30 s; `proc.terminate()` on timeout | Line 181: `future = loop.run_in_executor(executor, functools.partial(func, *args, **kwargs))`; line 183: `return await asyncio.wait_for(future, timeout=self.timeout)`; lines 204–206: `for proc in executor._processes.values(): proc.terminate()` then `self.recreate_for(p, executor, "timeout")` | [VERIFIED: src/spur/pool.py:181,183,204-206] — accurate, **and this is where the `proc.terminate()` loop actually lives**, not in `recreate_for` |

**Correction detail:** `recreate_for`'s own job (lines 99–155) is to discard a dead-or-stale
executor **object** and replace it; it assumes the worker process is already gone or already
terminated by its caller. The *only* call site that forcibly kills OS processes is
`_run_with_timeout`'s `TimeoutError` branch (lines 203–206), which runs the `proc.terminate()`
loop over `executor._processes.values()` *before* calling `recreate_for(p, executor, "timeout")`.
For the `BrokenProcessPool` branch (line 211 onward), no termination call is made at all — the
worker already died on its own, so there is nothing to terminate. If SC3's write-up or a debt
file describes this mechanism, attribute the termination to `_run_with_timeout`'s timeout
handler, not to `recreate_for` itself — `recreate_for`'s own docstring (lines 100–122) is
explicit that `cancel_futures=True` is deliberately *not* used, and walks through why a
same-slot queued request can reach `BrokenProcessPool` without ever calling
`proc.terminate()` anywhere in this class.

**ASSUMPTION settled (from code, read-only, no server run — per the research brief's Step 2):**
Yes, queue wait inside a slot counts toward the 30 s timeout. `loop.run_in_executor(executor,
...)` at line 181 submits the callable to the executor's own internal work queue and returns
immediately with a `Future`; `asyncio.wait_for(future, timeout=self.timeout)` at line 183 starts
its clock on that `Future` object at the moment it is wrapped — i.e., at submission, not at the
moment a worker actually picks the item off the queue. Under D-07's hash-affinity routing, a
single-worker `ProcessPoolExecutor` can have more than one pending item ahead of a given request
(pool.py's own comment at lines 126–150 states the call queue holds `max_workers +
EXTRA_QUEUED_CALLS == 2` items before PENDING begins, confirmed `[VERIFIED this session ...]` in
that comment by the Phase-2-era author against the installed `process.py`). A request queued
behind a long-running build on the same hash slot therefore has its 30 s clock already running
while it waits, exactly as CONTEXT.md's `<specifics>` ASSUMPTION states — this part of the
ASSUMPTION is directly confirmed, not merely plausible.

### `src/spur/app.py` — two line-range corrections, rest VERIFIED

| Symbol | CONTEXT.md cite | Actual | Status |
|---|---|---|---|
| `_BlobCache`/`_EXPORTS` | 47–88 | `class _BlobCache:` at line 46 (class body starts 47); `_EXPORTS = _BlobCache(...)` at line 88 | [VERIFIED: src/spur/app.py:46-88] (off by one on the start line, immaterial) |
| `_max_queued_builds`/`MAX_QUEUED_BUILDS`/`BUILD_QUEUE` | 91–96 | `def _max_queued_builds() -> int:` at 91; `return int_env(...)` at 98; `MAX_QUEUED_BUILDS = _max_queued_builds()` at **101**; `BUILD_QUEUE = threading.BoundedSemaphore(MAX_QUEUED_BUILDS)` at **102** | **[CORRECTED: actual range is 91–102, not 91–96]** — the cited range excludes the two module-level names it's citing them *for*. |
| `_GZIP_LEVEL` and L19's table comment | 168–207 | `_GZIP_LEVEL = 1` at line 205, inside the comment block that runs from ~168–204 | [VERIFIED: src/spur/app.py:168-207] |
| `_build_slot` | 258–283 | `def _build_slot(...)` at 258; admission-control raise block ends at 283; function's `finally` block (284–289) is outside the cited range | [VERIFIED: src/spur/app.py:258-283] (cited range covers the admission-refusal path exactly; the release-on-exit `finally` at 284–289 is just outside it, immaterial) |
| `health()` | 325–370: plain `def`, O(1) reads | `def health() -> HealthReport:` at 325; next endpoint (`schema()`) begins at 368–369 | [VERIFIED: src/spur/app.py:325-370] (health() itself ends ~366, next decorator at 368 — range is a few lines generous, immaterial) |
| `model()` | 381–499: `_EXPORTS.get(key)` before `_build_slot`; `run_in_threadpool(_gzip, raw)` inside the slot; `BuildTimeout` mapping 435–463 | `async def model(...)` at 381, file ends at line 499 (exact match); `data = _EXPORTS.get(key)` at line ~403 runs before the `with _build_slot(...)` at ~412; `run_in_threadpool(_gzip, raw)` at ~421 is inside that `with` block; `except BuildTimeout as exc:` at **435**, next `except BrokenProcessPool as exc:` at **447** | [VERIFIED: src/spur/app.py:381-499] for the function bounds and cache-before-slot ordering; **[CORRECTED: `BuildTimeout` mapping is lines 435–446, not 435–463 — 463 falls inside the following `except BrokenProcessPool` block (447–466)]** |

### `bench/sweeps/composed.json` — ten SC3 row indices VERIFIED exact

CONTEXT.md's `<specifics>` states: "Exact field values in `bench/sweeps/composed.json` rows 4,
2, 3, 1, 9, 6, 10, 12, 11, 5 (1-based)." Reading the file (18 rows total) and matching each
1-based index against the field values CONTEXT.md quotes for the worst row and the nine others:

| 1-based row | Fields (as read from the file) | CONTEXT.md's description | Match |
|---|---|---|---|
| 4 | `module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both` | the worst row, 29.42 s | exact |
| 2 | `module=1.75` + same keyway/spoke fields, `tip_chamfer=1.75` | "module=1.75 keyed spokes (28.92)" | exact |
| 3 | `module=10 bore_hex=43.35` + spoke fields, `tip_chamfer=3` | "module=10 bore_hex=43.35 spokes (28.87)" | exact |
| 1 | `module=1.75 bore_hex=43.35` + spoke fields, `tip_chamfer=1.75` | "module=1.75 bore_hex=43.35 spokes (28.61)" | exact |
| 9 | `module=1.75 bore_hex=200 hex_cell=3 hex_wall=0.4 tip_chamfer=1.75` | matches verbatim | exact |
| 6 | `module=1.75` keyway + `hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75` | "module=1.75 keyed holes" | exact |
| 10 | `module=1.75` keyway + `hex_cell=3 hex_wall=0.4 tip_chamfer=1.75` | "module=1.75 keyed honeycomb" | exact |
| 12 | `module=10` keyway + `hex_cell=3 hex_wall=5 tip_chamfer=3` | "module=10 keyed honeycomb" | exact |
| 11 | `module=10 bore_hex=200 hex_cell=3 hex_wall=5 tip_chamfer=3` | "module=10 bore_hex=200 honeycomb" | exact |
| 5 | `module=1.75 bore_hex=156.3 hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75` | "module=1.75 bore_hex=156.3 holes" | exact |

[VERIFIED: bench/sweeps/composed.json — all 18 rows read this session, all 10 cited indices and
field sets match CONTEXT.md's `<specifics>` exactly]. The worst row's 29.42 s figure is also
independently confirmed in `bench/RESULTS.md`'s "Re-run after the gate (lower-le: spoke_count
32)" table ([VERIFIED: bench/RESULTS.md, that section's row for this exact parameter set —
"Build + slower export (s)" column reads 29.42]).

### `bench/RESULTS.md` — citation range correction

CONTEXT.md cites: `"## Latency" through "### SPUR_BUILD_TIMEOUT"` at **lines 34–247**. Actual
section boundaries, confirmed via `grep -n '^## \|^### '`:

- `## Latency` at line 34
- `### SPUR_BUILD_TIMEOUT` at line 271
- `## Memory` (the next top-level section) at line 280

**[CORRECTED: the Latency section through SPUR_BUILD_TIMEOUT actually spans lines 34–279, not
34–247.]** This matters because the two numbered observations themselves — "every second run
of a pair reads worse" and "the verdict sits at the harness's ~0.1 ms resolution floor" — live
at **lines 252–268** (`grep -n` confirmed: "Every second run of a pair" at line 257, "The
verdict is being read at the harness's floor" at line 263), which is *outside* the cited
34–247 range. A planner who trusts the cited range literally and stops reading at line 247
would miss the exact text of both observations this phase exists to explain.

**Cross-checked numeric claims from `<specifics>`, all [VERIFIED: bench/RESULTS.md Latency
section, read in full this session]:**
- Idle p95 reads 0.6 ms in Runs 1, 2, 5, 6, 7, 8 (six of eight) and 1.0 ms / 0.9 ms in Runs 3, 4
  — matches CONTEXT.md's "Idle p95 0.6 ms in six of eight runs (0.9–1.0 ms in Runs 3–4)" exactly.
- Run 7 under-load n=10527, Run 8 under-load n=7719 — matches exactly.
- Ratios: Runs 1–2 2.02×/2.45×; Runs 3–4 2.32×/2.35×; Runs 5–6 1.31×/2.10×; Runs 7–8 1.86×/2.02×
  — matches exactly.
- Refused counts: of the four pairs, the *first* run of three of four pairs (Runs 3, 5, 7) shows
  6 of 10 refused and the *second* run of all four pairs (2, 4, 6, 8) shows 0, 2, 2, 2 of 10
  refused respectively. CONTEXT.md's generalization ("6 of 10 on first runs with a cold cache, 2
  of 10 on second runs") holds for three of the four pairs; Run 1 (first of the pre-fix pair)
  actually reads 2 of 10 refused, not 6 — a minor exception to the stated generalization, worth
  the planner knowing but not altering the investigation's design.

## Investigation Harness Shape (from `02-LATENCY-INVESTIGATION.md`)

Read in full this session. The Method section the write-up must follow names these reusable
pieces exactly:

- **`poller.py`** — a standalone script launched via `subprocess.Popen` as a genuinely separate
  OS process with its own `httpx.Client` and its own GIL. Samples `/api/health` in the same
  do-while cadence as `bench.latency._sample_while_building` (no delay between requests) until a
  `--stop-file` appears, then writes every `(time.monotonic(), latency_seconds)` pair to `--out`
  as JSON lines. `time.monotonic()` is CLOCK_MONOTONIC-backed (system/boot-time, not
  per-process), so its timestamps compare directly against the launching process's own
  `time.monotonic()` calls with no clock-sync step.
- **`run_experiment.py`** — the harness process. Launches `poller.py` as a subprocess, then
  concurrently runs an **in-process** idle/under-load sample using `bench.latency`'s own
  `_sample_for`, `_sample_while_building`, `_build` and `_p95` — **imported unmodified**
  (`sys.path.insert(0, PROJECT_ROOT)` then `from bench.latency import ...`), never
  reimplemented — while firing concurrent build requests via `ThreadPoolExecutor`, mirroring
  `scenario_concurrent`'s own shape. After builds finish it signals the poller to stop, reads its
  samples back, and splits into idle/under-load segments by `t_builds_start`/`t_builds_end`
  recorded in the *harness* process's own `monotonic()` clock, compared against the *poller*
  process's independent timestamps.
- **The `try/finally` lesson**: 02's first attempt crashed on an unhandled 422 before reaching
  its own cleanup, orphaning the poller subprocess (it never saw the stop-file and kept sampling
  in the background); a retry with the same label/run then had two processes writing the same
  JSONL path concurrently, corrupting it. Fixed by wrapping the build phase in `try/finally` so
  the stop-file write and the poller wait (with a `kill()` fallback on timeout) happen even if
  the build phase raises. D-01's twelve-run, multi-pair design makes this exact failure mode more
  likely here than in 02's four-experiment session — the planner should budget for it explicitly
  (a fixed `--label`/`--run` naming scheme per pair×run, and the try/finally from day one, not
  discovered after a corrupted file).
- **Per-run fields the write-up's tables carried**: idle p95 (n), under-load p95 (n), ratio,
  slowest build, refused count — the same five fields `_report_markdown` already prints, plus
  (02-specific) the poller/in-process comparison as two rows per run where H1 was being tested.
  D-02's raw-sample floor analysis needs JSONL carrying at minimum `(monotonic_timestamp,
  latency_seconds)` per sample, tagged by series (`idle` vs `under_load`) and by pair/run/poller
  — a shape `run_experiment.py` can satisfy directly from what it already collects from
  `poller.py`'s own JSONL output and the in-process `_sample_for`/`_sample_while_building`
  results.
- **02's scratch scripts are genuinely gone** (confirmed by CONTEXT.md's own D-03 reasoning and
  consistent with the write-up's own "Cleanup" section stating results remain only under a
  session-scoped scratchpad path, never committed) — `run_experiment.py` must be rebuilt from
  this Method section's description, not copied.
- **Host-state table shape** (the table the investigation write-up's "Environment" section uses,
  confirmed in the file): `sysctl -n vm.loadavg` (1/5/15-min) and `ps -Ao %cpu,comm -r | head -N`
  sampled before each experiment/leg, in a markdown table with one row per sampling point — the
  same shape D-05's quiet-wait and Runs 7–8's host-state header both already use in
  `bench/RESULTS.md`.

## Session Mechanics

- **The port-8001 `--base-url` trap (confirmed this session, not previously documented
  anywhere):** `make bench.latency` (Makefile line 117: `$(PY) -m bench.latency`) passes **no
  arguments**, so it always targets `bench/latency.py`'s hardcoded `DEFAULT_BASE_URL =
  "http://127.0.0.1:8000"` (line 28). `make serve` (Makefile line 74: `$(VENV)/bin/spur serve`)
  also has no port override baked in — it serves on `spur`'s own default (`src/spur/cli.py` line
  127: `s.add_argument("--port", type=int, default=int(env("SPUR_PORT", "8000")))`). Every
  session in `bench/RESULTS.md` instead ran `SPUR_PORT=8001 .venv/bin/spur serve` directly
  (bypassing `make serve`) because port 8000 is held by the `spur-spur-1` container
  (`compose.yaml`'s `spur` service, confirmed no `fleet-user`/`spur-spur-1` definitions exist in
  this repo's `compose.yaml` — `spur-spur-1` is this repo's own container from a prior `docker
  compose up`; `fleet-user` is an unrelated external container). **The literal `make
  bench.latency` target was never what produced any of the eight recorded runs** — it would have
  measured port 8000's `spur-spur-1` instead, silently. The planner must have every investigation
  and bar-session script invoke `.venv/bin/python -m bench.latency --base-url
  http://127.0.0.1:8001 <scenario>` directly, not the bare `make bench.latency` target, while the
  test server runs off-default on 8001.
- **Quiet-wait shape (D-05), confirmed from `bench/RESULTS.md`'s Runs 7–8 section:** a watcher
  samples `sysctl -n vm.loadavg` every 30 s and releases the pair only after **three consecutive
  samples** under 1.5 (Runs 7–8's actual samples: 1.35, 1.02, 1.05 at 14:09:05–14:10:05 UTC,
  after an initial reading of 4.16 at 14:05:16 with identified transient load —
  Spotlight/`mds` and a Time Machine pass — that was waited out, not killed). D-05's 15-minute
  cap and non-decisive marking is new relative to Runs 7–8 (which had no cap and no
  non-decisive concept); the Phase 12 D-02/12-03 precedent for a bounded cap (5 minutes there)
  is the shape to follow, scaled to 15 minutes per D-05's own text.
- **`docker stop fleet-user` / `docker start fleet-user` reversibility (D-06):** `fleet-user` is
  confirmed external to this repo (no reference in `compose.yaml`); stopping and restarting it
  via plain `docker stop`/`docker start` is reversible by construction — no compose file or
  volume state in this repo is touched. `spur-spur-1` (this repo's own container, serving on
  :8000) is left running throughout every session per every recorded run's host-state header.
- **Checkpoints needing a human at the keyboard** (from CONTEXT.md's own decisions, confirmed
  consistent with the live code/tooling — no correction needed): D-09's outcome-(b) checkpoint
  (choosing the harness/bar change from the surviving cause, with the numbers in front of the
  human); D-11's double-miss halt checkpoint; any D-05 quiet-bar cap expiry is *not* a checkpoint
  (the pair runs anyway, marked non-decisive) — only the outcome decisions themselves gate on a
  human.
- **`make verify`'s pre-commit cost** (confirmed current, `Makefile` lines 50–71): `verify: lint
  typecheck lint-imports no-fake-done test`, where `test: $(PY) -m pytest $(PYTEST_ARGS)` — the
  project's own STATE.md records this now runs ~3.5 min at 907 tests, consistent with D-18's
  text; `gsd_run query commit`'s 30 s timeout cannot survive it, so every commit in this phase
  should be a plain `git commit` with the hook running, per D-18 and the existing debt file
  `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`.

## Package Legitimacy Audit

Not applicable. D-17 forbids any `src/` change and no new dependency is introduced anywhere in
this phase (investigation scripts under `.planning/phases/13-latency-bar/investigation/` use
only `httpx`, `argparse`, `statistics`, `subprocess` — all already project dependencies per
`bench/latency.py`'s own imports, confirmed [VERIFIED: bench/latency.py:16-26]). No package
install, no registry check needed.

## Common Pitfalls

### Pitfall 1: Running `make bench.latency` against a server on a non-default port
**What goes wrong:** The harness silently measures the wrong service (`spur-spur-1` on :8000)
instead of the test server (:8001), producing a plausible-looking but meaningless p95/ratio.
**Why it happens:** `make bench.latency` hardcodes no `--base-url`; `bench/latency.py`'s own
default is `:8000`, and `:8000` is *also* a real, healthy spur deployment that will answer
`/api/health` with a valid-looking response.
**How to avoid:** Every script in this phase invokes `.venv/bin/python -m bench.latency
--base-url http://127.0.0.1:8001 <scenario>` explicitly, never the bare make target, whenever
the server under test is not on the default port.
**Warning signs:** A ratio or p95 that looks suspiciously stable/good across a session where the
test server was supposedly restarted — a sign the harness never actually hit the restarted
server.

### Pitfall 2: Attributing process termination to `recreate_for`
**What goes wrong:** A debt file or SC3 write-up that says "`recreate_for` kills the in-flight
build" is citing the wrong function and the wrong line range, which will mislead anyone later
trying to verify or modify the timeout/replacement mechanism.
**Why it happens:** The two steps (terminate the OS processes, then swap the executor object)
are adjacent in `_run_with_timeout`'s timeout branch and easy to read as one operation performed
by `recreate_for`.
**How to avoid:** Cite `_run_with_timeout`'s `except TimeoutError` branch (lines 203–210,
`src/spur/pool.py`) for the `proc.terminate()` loop, and `recreate_for` (lines 99–155) only for
the executor-object swap and the `replaced` counter / `worker_replaced()` log record.
**Warning signs:** Any future test or comment asserting `recreate_for` itself calls
`proc.terminate()` — it does not, and never has in the version read this session.

### Pitfall 3: Trusting a cited line range without checking the symbol it's supposed to bound
**What goes wrong:** Three of the citations in CONTEXT.md's `<canonical_refs>` have correct
function names but a line range that excludes part of what's being cited (see "Verified Code
Citations" above) — a planner who jumps straight to the cited range in an editor and stops
reading there will miss `MAX_QUEUED_BUILDS`/`BUILD_QUEUE`, the `BuildTimeout`-vs-`BrokenProcessPool`
boundary, and the two named observations in `bench/RESULTS.md`.
**How to avoid:** Use `grep -n` for the symbol name when writing the plan or any later debt/decision
text, not the cited range alone.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (`pyproject.toml` pins `pytest>=8`) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (line 115) |
| Quick run command | `make test PYTEST_ARGS="-k <pattern>"` |
| Full suite command | `make verify` (lint, mypy --strict, import-linter, unfinished-work scan, then `make test`) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-latency-observations-explained | Investigation write-up names a surviving candidate per observation, cites the ruling measurement | **Human-verified artifact** — the write-up's own prose and tables, checked against raw JSONL this phase produces under `.planning/phases/13-latency-bar/investigation/` | None — not test-suite-visible; SC1 explicitly forbids a `bench/`/`src/` change, so there is nothing for `make verify` to assert here | N/A |
| REQ-latency-bar-demonstrated-or-superseded (outcome a or b) | `scenario_concurrent` ≤2.00× on both runs of one session, OR a logged L32 change re-measured | **Human-verified artifact** — `bench/RESULTS.md`'s new session tables, read against the pass bar by eye, same as every prior Run 1–8 entry | None directly — if outcome (b) changes `bench/latency.py`'s pass-bar logic (D-10's `max(2.00×, idle+M)` formula), that *new logic itself* should get a unit test (new, Wave-0 gap — see below) even though the *measurement* stays human-verified | ❌ Wave 0 (only if outcome (b) is taken) |
| REQ-latency-bar-demonstrated-or-superseded (SC3 composed worst row) | A third `bench/latency.py` scenario reads `bench/sweeps/composed.json`'s 10 heaviest rows under 10 concurrent builds | Unit test pinning the scenario's row selection (D-15) | `make test PYTEST_ARGS="-k composed"` (new test, analogous to `test_the_composed_sweep_stacks_each_cutout_on_its_heaviest_bore_beside_six_baselines` in `tests/test_bench.py`) | ❌ Wave 0 |
| REQ-latency-bar-demonstrated-or-superseded (SC3 measurement itself) | The composed worst row's wall time under 10 concurrent builds, recorded whatever it reads | **Human-verified artifact** — `bench/RESULTS.md`'s per-request table (D-14), not asserted by `make verify` | N/A — a live measurement, not a repeatable unit-test assertion (the number legitimately varies run to run per L08's own reasoning) | N/A |
| REQ-latency-bar-demonstrated-or-superseded (debt retirement, SC4) | `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` → `resolved/`, INDEX row 19 moved, L18 text amended by L32 | **Human-verified artifact** — file move + git log inspection | None | N/A |

### Sampling Rate
- **Per task commit:** `make test PYTEST_ARGS="-k <relevant pattern>"` for the one new
  `tests/test_bench.py` row (D-15's scenario) and, if outcome (b) is taken, for any new pass-bar
  unit test.
- **Per wave merge / before any commit that will actually run the pre-commit hook:**
  `make verify` (the hook runs it anyway per D-18 — this is not optional).
- **Phase gate:** `make verify` green before `/gsd-verify-work`. Note per D-18: the hook itself
  already runs the full suite on every `git commit`; there is no cheaper "per-commit" tier
  available in this repo today (no `pytest-xdist`, no `-k`-scoped pre-commit config) — the
  "quick run" above is for the developer's own fast-feedback loop between commits, not a
  replacement for the hook.

### Wave 0 Gaps
- [ ] `tests/test_bench.py` — a new test for D-15's SC3 scenario, pinning its row selection
  against `bench/sweeps/composed.json` (indices 4, 2, 3, 1, 9, 6, 10, 12, 11, 5, 1-based — see
  "Verified Code Citations" above for the exact field sets each index carries), following the
  existing `test_the_composed_sweep_stacks_each_cutout_on_its_heaviest_bore_beside_six_baselines`
  shape (`load_sweep` + an exact `want` list comparison).
- [ ] If outcome (b) is taken and D-10's floor formula (`max(2.00 × idle_p95, idle_p95 + M)`) is
  adopted, a new unit test over `_p95_or_warn`/`_report_markdown`'s pass/fail logic pinning the
  formula at at least one case where the ratio alone would pass but the floor correctly keeps it
  failing (or vice versa) — this is new logic in `bench/latency.py` that today has no unit test
  at all (the module's only test coverage today is `tests/test_bench.py`'s sweep/report tests,
  which do not touch `_p95_or_warn`/`_report_markdown`'s pass-bar decision).
- [ ] No fixture or conftest gap identified for the investigation itself — it is explicitly out
  of `make verify`'s scope (D-03) and produces no automated assertion.

## Security Domain

No ASVS category applies: this phase makes no change to authentication, session management,
access control, input validation, or cryptography. It is a measurement/record-keeping phase over
an already-shipped topology, with the one code change (D-15's new `bench/latency.py` scenario)
reading from a committed, non-user-controlled JSON file (`bench/sweeps/composed.json`) and
calling the already-existing `/api/model.stl`/`/api/health` endpoints exactly as
`scenario_concurrent` already does. No new input surface, no new trust boundary.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | CONTEXT.md's generalization "6 of 10 refused on first runs, 2 of 10 on second runs" holds for 3 of 4 recorded pairs, not all 4 (Run 1 reads 2 of 10, not 6) | Verified Code Citations — bench/RESULTS.md cross-check | Negligible — the investigation's design (D-01) does not depend on this generalization being exact; it is background color in `<specifics>`, not a locked decision. |

No claim in this document rests on unread code, training memory, or an external source — every
`[VERIFIED]` tag above cites a file and line range opened this session, with the exact text
quoted beside it. This phase being internal-only (no new library, no external API), there is no
package-legitimacy or third-party-documentation risk to log.

**If this table is empty:** N/A — one low-risk item logged above; no user confirmation is needed
before planning, since it does not affect any locked decision's correctness.

## Open Questions

1. **Does `run_experiment.py` need its own `conftest.py`-style fixture, or is it a pure script?**
   - What we know: 02's `run_experiment.py` was a standalone script (not a pytest test), driven
     by CLI flags (`--mode`, `--label`, `--run`, `--no-gzip`), per the Method section read this
     session.
   - What's unclear: whether D-01's twelve-run, three-pair design benefits from a thin
     orchestration wrapper (e.g., a shell script or a `--pair`/`--leg` argument) versus 02's
     flatter per-experiment invocation style — this is explicitly Claude's Discretion in
     CONTEXT.md, not something research should pre-decide.
   - Recommendation: leave to the planner/executor; 02's precedent (plain CLI flags, no pytest
     involvement) is sufficient and matches D-03's "not part of `make verify`" requirement.

## Sources

### Primary (HIGH confidence — all code/docs read directly this session)
- `bench/latency.py` (full file) — function names, line numbers, `_p95`/`_report_markdown`
  behavior
- `src/spur/pool.py` (full file) — `executor_for`, `recreate_for`, `_run_with_timeout`,
  including the author's own `[VERIFIED this session ...]` comments on `cancel_futures`/queue
  depth behavior
- `src/spur/app.py` (lines 1-100, 160-290, 320-500) — `_BlobCache`/`_EXPORTS`,
  `_max_queued_builds`, `_GZIP_LEVEL`, `_build_slot`, `health()`, `model()`
- `src/spur/records.py` (full file) — `build.started`/`queue.refused`/`worker.replaced` records
- `Dockerfile` (full file) — `HEALTHCHECK` comment, lines 41-50
- `bench/build_time.py::load_sweep` (lines 62-80)
- `bench/sweeps/composed.json` (all 18 rows, parsed with `python3 -m json.tool`/`json.load`)
- `tests/test_bench.py` (function names + `test_the_composed_sweep_...` body in full)
- `Makefile` (full) — `bench.latency`, `serve`, `verify`, `test`, `pr.land` targets
- `bench/README.md` (full file)
- `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` (full file — the debt
  being retired)
- `.planning/milestones/v0.1-phases/02-cad-off-the-event-loop/02-LATENCY-INVESTIGATION.md`
  (full file)
- `bench/RESULTS.md` (lines 1-350, plus 1628-1705 for the SC3 composed table, plus section-header
  grep for the full document)
- `docs/architecture/decision_log.md` L18 (full entry, lines 214-256) and L19's header
- `docs/tech_debt/INDEX.md` (full "Active" table)
- `src/spur/cli.py` (lines 100-145) — `--port`/`SPUR_PORT` default
- `compose.yaml` (service names) — confirms no `fleet-user` in this repo
- `docs/HOW_TO_DEVELOP.md` §2 — phase branch cut convention
- `.planning/phases/13-latency-bar/13-CONTEXT.md`, `.planning/REQUIREMENTS.md`,
  `.planning/STATE.md`, `.planning/ROADMAP.md` — required reading per the research brief

No secondary or tertiary sources were used — this phase is entirely internal-code verification
with no external library, API, or documentation dependency (ROADMAP.md: "Research flag: No").

## Metadata

**Confidence breakdown:**
- Code citation verification: HIGH — every file read this session, every line-number claim
  checked against the live tree with `grep -n`/`sed -n`/`cat -n`.
- ASSUMPTION settlement (pool.py mechanism): HIGH — confirmed by reading the exact lines, no
  server run needed or performed, matching the research brief's "read-only verification" scope.
- Investigation harness shape: HIGH — 02-LATENCY-INVESTIGATION.md read in full; its Method
  section is explicit and complete about reusable functions and the split-process design.
- Session mechanics (port trap, quiet-wait, fleet-user): HIGH for the port-8001 trap (directly
  derived from reading `Makefile` + `bench/latency.py` + `bench/RESULTS.md`'s own prose
  contradiction); HIGH for quiet-wait shape (directly read from Runs 7-8's recorded samples);
  MEDIUM for `fleet-user` reversibility (confirmed external to this repo's `compose.yaml`, but
  its actual `docker start` behavior was not executed this session, per the research brief's
  read-only scope).

**Research date:** 2026-10-01
**Valid until:** This phase's own completion — once Phase 13 lands, these citations (especially
the `bench/latency.py` line numbers) will shift if D-15's new scenario or D-09's outcome-(b)
change touches that file.

## RESEARCH COMPLETE
