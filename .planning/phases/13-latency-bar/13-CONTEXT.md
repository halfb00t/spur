# Phase 13: Latency Bar - Context

**Gathered:** 2026-10-01
**Status:** Ready for planning

<domain>
## Phase Boundary

The v0.1 latency bar, settled: the two observations the 2026-09-23 waiver left unexplained
each get a cause ruled in or out by measurement, then the ten-concurrent bar is either
demonstrated on both runs of one decisive session on the harness as it stands, or the
harness/bar is changed by a logged `L32` with the measured reason and re-measured — never
a third outcome, never tuned toward a pass. The composed worst row (Phase 12, 29.42 s) is
measured once under ten concurrent builds. The `must` debt file retires in the commit that
demonstrates or supersedes the bar.

1. **The investigation** (REQ-latency-observations-explained, SC1). A bounded, scripted
   experiment in `02-LATENCY-INVESTIGATION.md`'s shape: three pair legs, each run twice,
   with a split-process poller beside every run, raw samples kept, predictions
   pre-registered (D-01…D-04). No `src/` or `bench/` change. Write-up at
   `.planning/phases/13-latency-bar/13-LATENCY-INVESTIGATION.md`; scripts and raw results
   under `.planning/phases/13-latency-bar/investigation/`.
2. **The bar** (REQ-latency-bar-demonstrated-or-superseded, SC2). One decisive session
   (D-05…D-08) on the unmodified `make bench.latency`. Both runs ≤ 2.00× → outcome (a).
   Either run over → outcome (b): a checkpoint with the numbers whose first offer is fixed
   by the surviving cause (D-09…D-11), the change logged as L32, re-measured on both runs
   of one session on the changed harness. A double miss halts; the debt stays active
   (D-11).
3. **SC3** — the composed worst row under ten concurrent builds (D-13…D-16): a third
   `bench/latency.py` scenario in its own commit after the bar's session, run once on a
   fresh server, recorded whatever it reads.
4. **The record** (SC4): one L32 amending L18 (append-only), the Dockerfile `HEALTHCHECK`
   comment sentence, `bench/RESULTS.md` sections, the debt file retired with its sha
   (D-12).

**Out of this phase:** any `src/` change (the fixture is trivially byte-unchanged); a fix
for whatever the investigation finds (a finding is written up, a defect is filed as debt
with a trigger — never fixed here); the ten-identical-requests queue-wait scenario (not
run — see `<deferred>`); L17's `mem_limit` re-sweep; the `make verify` profile (Phase 15).

</domain>

<decisions>
## Implementation Decisions

### Investigation design
- **D-01:** **Three pair legs separate the three candidates for observation 1** (the
  second run of a pair always reads worse). Each leg is two back-to-back runs of
  `make bench.latency` in Runs 1–8's exact shape (`single` then `concurrent`, D-08):
  **Pair A** same server, same teeth 190–199 — the baseline reproduction, observation 1
  expected; **Pair B** same server, run 2 on teeth 180–189 — cold export cache, warm
  workers, separates worker-side state from cache-hit sends with no `src/` change;
  **Pair C** a server restart between the runs — everything cold. A split-process poller
  (02's `poller.py` shape: own OS process, own `httpx.Client`, `time.monotonic()`
  timestamps, stop-file) rides beside every run to re-check H1 post-fix. Rejected: only
  the two legs the debt file names (if the restart makes run 2 match run 1, carryover and
  worker state die together and the write-up can only say "server state"); adding Pair B
  conditionally (a third session when it is needed, for two runs saved when it is not).
- **D-02:** **Observation 2 (the ~0.1 ms floor) is measured from raw samples, not
  asserted.** Every run's `(timestamp, latency)` samples are saved as JSONL; p95 is
  recomputed at full float precision and reported to 3 dp (µs). `bench/latency.py` prints
  p95 at `:.1f` ms but computes the ratio on raw floats (`load_p95 / idle_p95`,
  `_report_markdown`), so the "0.1 ms apart" reading in the record is the print format's
  resolution until the raw samples say otherwise. The write-up reports p94/p95/p96 and the
  count of samples at the timer's quantum, and states whether the pass/miss flips inside
  one percentile. Rejected: a longer idle window (more data per run for a question the
  raw samples answer); reading the floor off the spread of printed p95s (cannot tell
  timer resolution from print rounding from variance).
- **D-03:** **Scripts and raw results live in the phase directory and ride the PR:**
  `.planning/phases/13-latency-bar/investigation/` holds `poller.py`,
  `run_experiment.py` (names the planner's), every run's JSONL and a per-run JSON summary;
  the write-up cites them by file name. Not under `bench/` (SC1 forbids a `bench/` change
  under this requirement), not part of `make verify`. Reason: 02's scratch scripts are
  gone — only an empty `results/` directory survives in that session's scratchpad —
  so the 02 precedent (scratchpad + tables in the write-up) is not re-runnable. —
  **Reversibility:** reversible — files under `.planning/`, no code path depends on them.
- **D-04:** **Each pair runs twice; both repetitions must point the same way before a
  candidate is ruled in or out.** Twelve runs plus pollers, on the order of 20 min of
  load. A split reads as "not separable on this host" and is written up as such, never
  as a cause. Predictions per candidate are pre-registered in the write-up before the
  first run (02's H1/H2/H3 shape; the prediction table is Claude's discretion, see
  `<specifics>`). Rejected: once per pair (one pair cannot exclude a ±0.3× swing —
  02's E0 read 1.53× against Runs 1–4's 2.02–2.45×); up to three with stop-at-two
  (bias toward whichever direction appears first).

### Session rules
- **D-05:** **A session is decisive only when it met the quiet bar:** release the pair
  only after three consecutive 30 s samples of 1-minute `sysctl -n vm.loadavg` under 1.5,
  with a 15-minute cap. On cap expiry the pair runs anyway, is recorded as measured, and
  is marked **non-decisive** — it counts for the record and for the investigation, never
  for outcome (a). The same rule gates every session in the phase (investigation pairs,
  the bar session, SC3). Runs 7–8's watcher shape; bounded the way 12-03's 5-minute cap
  was, with the non-decisive marking 12 D-02 lacked. Rejected: "< 1.5 at start, no wait"
  (today's reading is 3.38; sessions may never qualify); any load (a loaded-host pass
  would count, so would a miss caused by an unrelated test runner).
- **D-06:** **`spur-spur-1` stays up on `:8000`; `fleet-user` is stopped for the
  sessions.** The service under test serves on `SPUR_PORT=8001` as in every recorded run.
  Stopping the restart-looping `fleet-user` (every ~40 s, present beside all eight
  recorded runs) is a change of environment relative to Runs 1–8: it is named in every
  host-state header and in the write-up, and a pass is not read as explaining the
  recorded misses. Rejected: keep both (the human's call: the loop is a known periodic
  CPU hit nobody measured); stop both (a second environment change for a container that
  is this project's own and healthy). — **Reversibility:** reversible — `docker start`.
- **D-07:** **Outcome (a) gets one decisive session.** One pair on the unmodified
  `make bench.latency`, no extra poller, on a session that met D-05. Both `concurrent`
  runs ≤ 2.00× → (a), recorded. Either run over → (b) is taken, with the investigation's
  surviving cause as its reason. Rejected: two decisive sessions (the host reached the
  quiet bar once in four sessions); the investigation's Pair A doubling as (a) (the split
  poller riding alongside is not "the harness as it stands").
- **D-08:** **Both scenarios, in Runs 1–8's order.** Every pair runs `single` then
  `concurrent` exactly as `make bench.latency` does, so the second run inherits the same
  cache state the record's second runs inherited (teeth 200 fine from `single` plus the
  admitted 190–199 builds) and observation 1 is asked under the conditions it was
  observed. The second run's `single` "insufficient (n<20)" rows are recorded as before.
  Rejected: `concurrent` only (a different inherited cache than every recorded pair).

### Outcome (b) and the record
- **D-09:** **(b)'s change is chosen at a checkpoint with the numbers, with the first
  offer fixed now by the surviving cause** (12 D-03's shape): observation 1's cause
  (cache carryover or worker state) → **a server restart between runs** becomes the
  harness's protocol; observation 2's cause (the verdict flips inside one percentile) →
  **an absolute threshold the harness can resolve** (D-10); a **higher `MIN_SAMPLES`**
  only if the floor analysis shows the sample count is the problem. The human confirms
  with the measurement in front of them; the change is logged as L32 with the measured
  reason and re-measured on both runs of one decisive session. Rejected: a fixed ranking
  applied without a halt (a change for a cause the investigation did not find); a
  checkpoint with all three open (a second discussion of the same evidence).
- **D-10:** **If the floor survives, the threshold keeps the ratio and adds a floor:**
  pass = under-load p95 ≤ max(2.00 × idle p95, idle p95 + M ms), where M is set from the
  floor analysis (on the order of 10× the measured per-sample resolution) and recorded
  in L32 together with the samples that set it. The ratio stays the claim (D-17's reason:
  the bar travels between hosts); a tenth of a millisecond stops deciding a verdict.
  Rejected: report precision only (does nothing if the floor is real variance at the
  quantum); an absolute ms bar per host class (the bar no longer travels). —
  **Reversibility:** costly — the bar's published definition changes; L32 and
  `bench/latency.py`'s report text both state it, and every later run is read against it.
- **D-11:** **A double miss halts; the debt stays active.** If (b)'s re-measurement on
  the changed harness also misses on both runs, the phase halts at a checkpoint with the
  numbers. A second harness change happens only by a second `Lxx` with its own measured
  reason; otherwise the phase closes with the measurement recorded, the debt file **not**
  retired (new trigger, new numbers), and SC4 recorded as not met. Rejected: recording
  the measured ratio as the bar (tuning toward a pass by definition — forbidden by the
  debt file and L08); accepting with caveat again (L18's shape repeated — the milestone's
  stated point is to stop doing this).
- **D-12:** **One L32 in L27–L31's shape, amending L18 (append-only):** the two
  observations with the candidate that survived and the measurement that ruled the others
  out, outcome (a) or (b) with the decisive session's numbers, the SC3 reading, the
  environment change (D-06) — each cited to the write-up or a `bench/RESULTS.md` section,
  none re-estimated. L18's own text is untouched (L25-amends-L22 precedent; Phase 12
  D-18); PROJECT.md's L18 row gets its Outcome column updated at the phase transition.
  The Dockerfile `HEALTHCHECK` comment (lines 41–50) does **not** cite the ≤ 2× bar; its
  "measured under-load p95 is 0.7–2.3 ms across the eight bench/RESULTS.md latency runs
  (worst: 2.3 ms …)" sentence is updated to the new run count and worst reading. Rejected:
  L32 for the bar only (the causes and SC3 would live only in the write-up); two entries
  (no precedent in L26–L31).

### SC3 — the composed worst row under ten concurrent builds
- **D-13:** **The worst row plus the composed sweep's next nine heaviest rows.** The
  worst row (`teeth=200 module=10 bore_d=9 keyway_width=3 keyway_depth=1.4 spoke_count=32
  spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both`,
  29.42 s alone) is fired first, then the nine rows listed in `<specifics>` at t=0 — ten
  distinct keys, so admission control takes 4 (`MAX_QUEUED_BUILDS` = 2 ×
  `SPUR_BUILD_WORKERS`) and hash affinity spreads the admitted builds over both workers:
  kernel work actually stacks on the host, which is the tip-chamfer debt's original
  question. Rejected: ten identical worst-row requests (one hash slot, serial — measures
  the timeout's queue-wait semantics, not kernel contention; see `<deferred>`); both
  scenarios as two rows (a second protocol for a question the milestone scoped once).
- **D-14:** **`bench/RESULTS.md` records a per-request table plus the health ratio:** one
  row per request — parameters, outcome (admitted / `503` refused / timeout), wall time —
  the worst row's own time named against 30 s, `/api/health`'s `workers_replaced` before
  and after, and the idle/under-load p95 ratio from the same poller the investigation
  uses. Host-state header as every section has. Rejected: the worst-row time and counts
  only (no view of what the other worker did).
- **D-15:** **The SC3 scenario is a third scenario in `bench/latency.py`, landed in its
  own commit after the bar's decisive session.** It reads its rows from
  `bench/sweeps/composed.json`, registers in `_SCENARIOS` (name the planner's), runs as
  `python -m bench.latency <name>`, and gets a `tests/test_bench.py` row; `scenario_single`
  and `scenario_concurrent` are untouched, so the bar is measured on the harness as it
  stands. Rerunnable — the project's rule for every number (12 D-17). Rejected: a script
  in the phase dir (no make target, no test); a one-off with the command pasted (12 D-17
  rejected exactly this). — **Reversibility:** reversible — an added scenario; deleting
  it changes no bar.
- **D-16:** **SC3 runs on its own fresh server, after the decisive session and before
  the close, under D-05's quiet rule.** A timed-out worker is replaced
  (`pool.recreate_for`) and must not pollute a bar session; the quiet wait applies with the
  same 15-minute cap, and the run is recorded as measured either way — "whatever it
  reads". Rejected: any time with the load noted (a timeout under a test runner reads the
  same as one under a quiet host).

### Contract and process
- **D-17:** **No `src/` change in this phase.** The investigation forbids it (SC1); the
  bar's (b) touches only `bench/latency.py` under L32; SC3 adds to `bench/latency.py` and
  `tests/test_bench.py`; the Dockerfile comment is prose. `tests/regression/pre_v0_2.json`
  is byte-unchanged by construction; `GearParams` gains no field. Anything the
  investigation or SC3 finds in the server (for example, the queue-wait-counts-toward-
  timeout behaviour in `<specifics>`) is filed as debt with a trigger and severity, never
  fixed here.
- **D-18:** **Process.** PR #15 (`gsd/milestone-v0.3-start`, planning-only, PR #14's
  precedent) was landed this session via `make pr.land PR=15` → `origin/main` `9f26052`;
  the phase runs on **`gsd/phase-13-latency-bar`**, cut from that commit, and lands via
  `make pr.land PR=N` (L22/L25); `.planning/` rides the same PR. Commits are plain
  `git commit` with explicitly staged files (the `make verify` hook runs ~3.5 min at 907
  tests; `gsd_run query commit`'s 30 s timeout cannot survive it — after any wrapper
  timeout, wait for the orphaned `pre_commit hook-impl` to exit and restore its stash).
  The debt file retires in the commit that demonstrates or supersedes the bar: `Status:
  resolved`, the sha, `git mv` to `docs/tech_debt/resolved/`, INDEX row 19 moved.

### Claude's Discretion
- **The pre-registered prediction table** (D-04): one row per candidate × pair leg,
  stating what each candidate predicts for run 2 vs run 1 and for n (the shape in
  `<specifics>` is a starting point, not a pinned answer).
- **Script names, JSONL field names, the per-run summary's fields**, and whether
  `run_experiment.py` drives `make bench.latency` as a subprocess or imports
  `bench.latency`'s functions unmodified (02 imported `_sample_for`,
  `_sample_while_building`, `_build`, `_p95` — the same rule: never reimplement the
  harness's own sampling).
- **The write-up's section order** within 02's shape (Question, Environment, Method,
  Results, Verdict, Recommendation, Cleanup) and its file name
  (`13-LATENCY-INVESTIGATION.md`).
- **What the host-state header records** beyond Runs 7–8's set (three loadavg samples 30 s
  apart, top CPU, `docker ps`, HEAD, machine facts) — at least: `fleet-user` stopped (D-06),
  the commit under test, `SPUR_*` values (shipping defaults).
- **The SC3 scenario's name, its firing order mechanics** (the worst row's request leaves
  the client before the other nine), how per-request outcomes are read (the client's
  status codes; `records.py`'s `build.started` / `queue.refused` / `worker.replaced` lines
  if the server's stderr is captured), and whether the health poller's samples from SC3
  feed the same floor analysis.
- **The order of plans:** the investigation scripts and runs first; the write-up; the
  decisive session; (b)'s checkpoint if reached; the SC3 scenario and run; L32, the
  Dockerfile sentence, `RESULTS.md` sections and the debt retirement last, citing shas.
- **The restart-between-runs rule's enforcement if D-09 adopts it:** a documented protocol
  (`bench/README.md`, the `RESULTS.md` header) at minimum; whether the harness also warns
  when `single`'s slowest build reads as a cache hit is the planner's call under L32.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements, roadmap, project
- `.planning/REQUIREMENTS.md` — "### Latency bar": REQ-latency-observations-explained,
  REQ-latency-bar-demonstrated-or-superseded (the two contracts, their acceptance text,
  the "never a third outcome" clause); "Rules every requirement lives by" (measured, never
  tuned; retired in the fixing commit); "Out of Scope" (tuning the harness or server
  until the bar passes).
- `.planning/ROADMAP.md` "### Phase 13: Latency Bar" — goal, SC1–SC4, "Research flag:
  No"; "Process Notes (carried forward)".
- `.planning/PROJECT.md` — "Current Milestone: v0.3 Clean Ledger" (the latency-bar
  target feature text, the three rules), "Success Metric (Milestone v0.3)" 1–2, Key
  Decisions L18 (the row whose Outcome column changes at transition), L19, L24.

### The debt and its history
- `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` — the file this
  phase retires: the two observations verbatim, the three candidates, the prescribed
  investigation shape, the re-homed SC3 trigger (12 D-04). Its "Next step" is D-01's
  brief.
- `docs/tech_debt/INDEX.md` row 19 — moves to the resolved table in the retiring commit.
- `docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md` —
  the original concurrent-load question SC3 answers ("nothing here measures the chamfer
  under concurrent load"; worst plain 200-tooth build 7.39 s under ten concurrent).
- `.planning/milestones/v0.1-phases/02-cad-off-the-event-loop/02-LATENCY-INVESTIGATION.md`
  — **the shape the write-up must follow** (Question / Environment table / Method /
  Results per experiment / Verdict / Recommendation / Cleanup) and the harness design
  reused by D-01: `poller.py` as a subprocess with its own GIL, `run_experiment.py`
  importing `bench.latency`'s functions unmodified, the `try/finally` stop-file lesson,
  H1 refuted pre-fix (E1: split 5.99×/1.48× vs in-process 7.06×/1.55×), E2c's cache-hit
  finding, the host-state table per experiment.
- `bench/RESULTS.md` "## Latency" through "### `SPUR_BUILD_TIMEOUT`" (lines 34–247) —
  Runs 1–8 with their host-state headers and the two observations as first written
  ("Idle-host re-run (Runs 7-8)" → "**Finding.**"); the port-8001 convention; the
  `Refused` column's meaning. "### Re-run after the gate (lower-le: spoke_count 32)"
  (Phase 12) — the composed table D-13's ten rows come from, the heaviest row named.
  "## Composition pass test cost (Phase 12, D-10)" — the host-state header shape.

### Decisions
- `docs/architecture/decision_log.md` — **L18** (the entry L32 amends; its caveat
  paragraph), L06 (the lock L18 kept), L08 (no plausible numbers), L13 (the gate), L17
  (`mem_limit`, its own trigger), **L19** (gzip level 1 — the fix the second-run
  observation survived; `_build_slot` covers build + first encode), L22/L25 (merge gate;
  L25-amends-L22 is D-12's precedent), L24, L26 (fixture byte-unchanged), L31 (the
  composed sweep and its numbers). Append-only; L32 is this phase's.
- `.planning/milestones/v0.2-phases/12-composition-pass/12-CONTEXT.md` — D-02 (the
  quiet-host bar D-05 bounds), D-03 (the checkpoint-with-the-number shape D-09 copies),
  D-04 (the re-homed SC3 question), D-17 (committed script behind a make target — D-15),
  D-18 (append-only precedent — D-12), D-21 (process).

### The harness and the server
- `bench/latency.py` — `MIN_SAMPLES` (20, `statistics.quantiles` bucket count),
  `SETTLE_SECONDS` (2.0), `_p95` (48), `_sample_for` (59), `_sample_while_building` (70),
  `_build` (86: `503` → `None`, other non-2xx raises), `scenario_concurrent` (135: teeth
  190–199, `ThreadPoolExecutor(max_workers=10)`), `_SCENARIOS` (149 — D-15 registers
  here), `_p95_or_warn` (155), `_report_markdown` (168 — `:.1f` ms print, ratio on raw
  floats), `main` (200 — the scenario argument).
- `bench/__init__.py` — `machine_facts()`; `bench/README.md` — "Where each half must
  run, and why" (host, port, D-17 comparability).
- `bench/sweeps/composed.json` — the 18 rows; `bench/build_time.py` `load_sweep` — the
  sweep-file reader D-15 may reuse; `tests/test_bench.py` — the per-sweep row-test shape.
- `src/spur/app.py` — `_BlobCache`/`_EXPORTS` (47–88: the cache the second run inherits;
  both encodings under one budget), `_max_queued_builds`/`MAX_QUEUED_BUILDS`/`BUILD_QUEUE`
  (91–96), `_GZIP_LEVEL` and L19's table comment (168–207), `_build_slot` (258–283),
  `health()` (325–370: plain `def`, O(1) reads), `model()` (381–499: `_EXPORTS.get(key)`
  before `_build_slot`; `run_in_threadpool(_gzip, raw)` inside the slot; `BuildTimeout`
  mapping 435–463).
- `src/spur/pool.py` — `executor_for` (97: `hash(p) % self.workers`), `recreate_for`
  (123–155: terminates every process of the slot's executor), `_run_with_timeout`
  (157–220: `asyncio.wait_for(future, timeout=self.timeout)` at submit — queue wait
  inside a slot counts toward the 30 s; `proc.terminate()` on timeout).
- `src/spur/records.py` — `build.started`, `queue.refused`, `worker.replaced` records
  (the SC3 table's server-side source if stderr is captured).
- `Dockerfile` 41–50 — the `HEALTHCHECK` comment sentence D-12 updates; the check itself
  cites no bar.

### Process
- `docs/HOW_TO_DEVELOP.md` §2/§4 — the phase branch is cut from `origin/main` before
  discuss-phase and reused by execute-phase; `main` only via `make pr.land`.
- `docs/CODING_VALUES.md`, `CLAUDE.md` — comments carry the measurement; debt lifecycle;
  `make verify` is the gate; caveman for user-facing text, Conventional Commits.
- `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md` — why
  commits are plain `git commit`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `bench/latency.py`'s sampling and p95 functions (`_sample_for`,
  `_sample_while_building`, `_build`, `_p95`, `_p95_or_warn`) — imported unmodified by
  the investigation's `run_experiment.py` (02's rule); `scenario_concurrent`'s shape is
  the template for D-15's scenario; `_SCENARIOS` is the registration point; `main`'s
  positional `scenario` argument already selects one scenario.
- `bench/__init__.py::machine_facts()` — every printed number carries the machine.
- `bench/build_time.py::load_sweep` and `bench/sweeps/composed.json` — the row source for
  D-13 (the ten rows are the re-run table's ten heaviest by "Build + slower export").
- `tests/test_bench.py` — one test per sweep/scenario asserting the rows are what the
  plan names (Phase 8–12 precedent) — D-15's `test_bench` row.
- `src/spur/app.py::health()` — a plain `def` (FastAPI runs it on the threadpool), every
  read O(1); `HealthReport.pool.workers_replaced` is D-14's before/after counter.
- `02-LATENCY-INVESTIGATION.md` "## Method" — the scratch harness design to rebuild
  (scripts lost; the description survives).
- `bench/RESULTS.md` host-state headers (Runs 7–8's three-sample wait; Phase 12's
  at-start reading) — the section shape every new run copies.

### Established Patterns
- A number is measured via a committed script and a `make` target, recorded with host
  state and load, cited in the `Lxx` — never re-estimated (08 D-12, 12 D-17, L27–L31).
- Rows over a bar are recorded as measured, never dropped or re-run to green (11-06;
  Runs 5–8 "not restarted or repeated in search of a passing number").
- A decision that needs a number halts at a checkpoint with the number and a pre-agreed
  first offer (07 D-06, 12 D-03).
- The decision log is append-only; an amendment is a new entry (L25 → L22; 12 D-18).
- Debt is resolved in the fixing commit: status, sha, `git mv`, INDEX row (CLAUDE.md).
- The harness refuses to print a p95 it cannot compute (`MIN_SAMPLES`, L08) — the
  investigation keeps that rule for every series it reports.

### Integration Points
- `bench/latency.py` — D-15's scenario (and D-09's change if (b) is taken, under L32);
  `tests/test_bench.py` — the scenario's row test.
- `bench/RESULTS.md` — a Phase 13 latency section (investigation pairs by session, the
  decisive session, any (b) re-measurement) and the SC3 section; `bench/README.md` if a
  protocol rule (restart between runs) is adopted.
- `.planning/phases/13-latency-bar/13-LATENCY-INVESTIGATION.md` and `investigation/`
  (scripts, JSONL, summaries).
- `docs/architecture/decision_log.md` (L32); `Dockerfile` (comment sentence);
  `docs/tech_debt/active/` → `resolved/` and `INDEX.md` row 19; PROJECT.md L18 row at
  transition.

</code_context>

<specifics>
## Specific Ideas

**Numbers on record (`bench/RESULTS.md`, `concurrent` scenario, ratio = under-load p95 /
idle p95):** Runs 1–2: 2.02× → 2.45×; Runs 3–4: 2.32× → 2.35×; post-fix (`7a61fad`, L19)
Runs 5–6: 1.31× → 2.10×; Runs 7–8: 1.86× → 2.02×. Idle p95 0.6 ms in six of eight runs
(0.9–1.0 ms in Runs 3–4); under-load n: Run 7 10527, Run 8 7719. Refused: 6 of 10 on first
runs with a cold cache, 2 of 10 on second runs (cached teeth bypass admission). 02's E0 on
the same harness read 1.53× — the run-to-run band D-04's "twice, agreeing" rule exists
for.

**The three candidates for observation 1 (debt file):** (1) four instant ~2.6 MB sends at
t=0 — on run 2 the admitted gears from run 1 are cache hits (`model()` returns the cached
gzip bytes with no slot: `tests/test_api.py::test_an_already_compressed_download_needs_no_slot_at_all`),
so four `Response(data)` bodies leave the loop thread at once; (2) worker-side state after
the first batch (the per-worker solid cache, arenas, whatever `BuildPool` carries); (3) a
shorter load window (n=7719 vs 10527) read at the floor. A starting prediction table for
D-04 (Claude's discretion to refine):

| Candidate | Pair A (same/same) | Pair B (cold cache, warm workers) | Pair C (restart) |
|---|---|---|---|
| (1) cache-hit sends | run 2 worse | run 2 ≈ run 1 | run 2 ≈ run 1 |
| (2) worker state | run 2 worse | run 2 worse | run 2 ≈ run 1 |
| (3) window at the floor | run 2's n smaller, verdict flips inside one percentile | n restored | n restored |

**The harness's own resolution:** samples are `time.perf_counter()` differences (ns
resolution); `_p95` is `statistics.quantiles(samples, n=20)[-1]`; the report formats p95
at one decimal of a millisecond while the ratio divides the raw floats — so D-02's raw
samples are the only honest source for the floor claim.

**Server and host conventions:** `SPUR_PORT=8001 .venv/bin/spur serve` (port 8000 is
`spur-spur-1`'s, up 22 h at discuss time); shipping defaults `SPUR_BUILD_WORKERS=2`,
`MAX_QUEUED_BUILDS=4`, `SPUR_BUILD_TIMEOUT=30`; this host: 12 CPUs, arm64, 32.0 GiB
(`machine_facts()`), 1-minute load 3.38 at discuss time; `fleet-user` restart-looping
(to be stopped, D-06).

**SC3's ten rows** (the composed re-run table's heaviest by "Build + slower export", all
`teeth=200 recess_sides=both`): the worst row (29.42 s — `module=10 bore_d=9 bore_flat=0
keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4
spoke_fillet=5 tip_chamfer=3`), then `module=1.75` keyed spokes (28.92), `module=10
bore_hex=43.35` spokes (28.87), `module=1.75 bore_hex=43.35` spokes (28.61), `module=1.75
bore_hex=200 hex_cell=3 hex_wall=0.4 tip_chamfer=1.75` (27.27), `module=1.75` keyed holes
`hole_count=60 hole_d=1 hole_circle_d=183.4 tip_chamfer=1.75` (24.91), `module=1.75` keyed
honeycomb (24.06), `module=10` keyed honeycomb `hex_cell=3 hex_wall=5 tip_chamfer=3`
(22.26), `module=10 bore_hex=200` honeycomb (22.09), `module=1.75 bore_hex=156.3` holes
(16.80). Exact field values in `bench/sweeps/composed.json` rows 4, 2, 3, 1, 9, 6, 10,
12, 11, 5 (1-based).

**ASSUMPTION (from code, unmeasured — the planner verifies, SC3 measures):**
`pool._run_with_timeout` wraps `loop.run_in_executor(...)` in
`asyncio.wait_for(timeout=30)` at submit, so a request queued behind another build on the
same worker counts its queue wait toward the 30 s; on timeout `recreate_for` terminates
every process of that executor, which would kill the in-flight build on that worker too.
With four admitted ~16–29 s builds over two workers, the second on each worker is expected
to time out and take the first down with it unless the first finishes inside 30 s. Slot
assignment is `hash(p) % workers` on a pydantic model — not controllable from the client;
the per-request table records what happened, not what was intended. If observed, this is
a finding → a debt file with severity and trigger (D-17), not a fix.

**Environment change recorded verbatim (D-06):** "`fleet-user` (unrelated, restart-looping
every ~40 s beside Runs 1–8) was stopped for this session; `spur-spur-1` left running."

</specifics>

<deferred>
## Deferred Ideas

- **Ten identical worst-row requests** (the queue-wait scenario) — not run (D-13); if
  SC3's per-request table shows a queued request's timeout terminating an in-flight
  build, the behaviour is filed as a debt item with the measurement (D-17), and the
  identical-key scenario becomes that file's "next step".
- **Server-side admission for cache-hit sends** — if candidate (1) survives, bounding
  the concurrent large-body sends is a `src/` change outside this phase (02's
  recommendation 2 revisited); the write-up names it, the debt file (if any) carries it.
- **L17's `mem_limit: 4g` re-swept on v0.2 topology** — stands from 12-CONTEXT
  `<deferred>`; not this phase's.
- **Refreshing `.planning/codebase/*.md`** — the maps are dated 2026-09-21 and predate
  `bench/`, `pool.py` and Phases 7–12; this discussion read the code directly. Process,
  not product.
- **A `make bench.latency SCENARIO=` argument** — the Makefile target runs both scenarios
  with no selector; D-15's scenario is run through `python -m bench.latency <name>`.
  Adding a make variable is a convenience, not a requirement.

</deferred>

---

*Phase: 13-latency-bar*
*Context gathered: 2026-10-01*
