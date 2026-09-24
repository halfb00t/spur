---
gsd_state_version: "1.0"
milestone: v0.1
current_phase: 02
current_phase_name: CAD Off the Event Loop
status: executing
stopped_at: "Phase 2 executed 5/5; 02-REVIEW.md findings all resolved (quick task 260924-bv5, commits 17048c9 d334049 08697f0 15fa5cd); verification stale after the fixes -- next: /gsd-verify-work 2 (re-verify, then the 2 UAT items in 02-UAT.md)"
last_updated: "2026-09-24T03:10:31.445Z"
last_activity: 2026-09-23
last_activity_desc: Phase 02 execution complete (5/5 plans); awaiting /gsd-verify-work 2
state_head: 15fa5cde154148a10ecdd7dcb38401ca1dc8acdd
progress:
  total_phases: 5
  completed_phases: 1
  total_plans: 5
  completed_plans: 5
milestone_name: Hardening
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-21)

**Core value:** A number this tool prints is a number someone will cut metal to — every
dimension is computed honestly or reported as a warning, never guessed (L08).
**Current focus:** Phase 02 — CAD Off the Event Loop
gear features ship in v0.1.

## Current Position

Phase: 02 (CAD Off the Event Loop) — COMPLETE
Plan: 5 of 5
Status: Phase 02 complete, ready for /gsd-plan-phase 3 and /gsd-verify-work 2
Last activity: 2026-09-23 — Plan 02-05 closed the loop (L17/L18/L19, HEALTHCHECK timeout,
tech-debt resolution, redrawn system map)

## Performance Metrics

**Velocity:**

- Total plans completed via GSD: 0 (v0 was built and verified directly against
  `make verify`, before this planning structure existed)
- Average duration: N/A
- Total execution time: N/A

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. v0 Baseline | N/A | N/A | N/A |
| 2. CAD Off the Event Loop | TBD | - | - |
| 3. Structured Logging | TBD | - | - |
| 4. Typed Derived-Dimensions Contract | TBD | - | - |
| 5. CI Observed Green | TBD | - | - |

**Recent Trend:** N/A — no GSD-tracked plan history yet.
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 02 P01 | 30min | 3 tasks | 8 files |
| Phase 02 P02 | 19min | 3 tasks | 6 files |
| Phase 02 P03 | ~25min | 4 tasks | 4 files |
| Phase 02 P04 | ~2h | 3 tasks | 9 files |
| Phase 02 P05 | 35min | 3 tasks | 5 files |

## Accumulated Context

### Decisions

Full decision log: PROJECT.md "Key Decisions" table (L01–L16, from
`docs/architecture/decision_log.md`). Two flagged for revisit there: L10 (radial root
fillet — trochoidal is a tracked idea) and L14 (`disallow_any_explicit` off — retired by
Phase 4, not just revisited).

Roadmap-time decisions for v0.1:

- Phase 2 bundles REQ-cad-off-event-loop and REQ-measured-memory-ceiling into one phase
  rather than two consecutive ones — they share the same process-pool change and the same
  two superseding decision-log entries (L06, L07); splitting them would put a single
  requirement in each with no independent deliverable.
- Phases 3, 4, and 5 are ordered as independent, sequential phases (not merged into Phase
  2 or each other) — nothing in the debt files ties structured logging's fields, the typed
  contract, or CI verification to the process-pool work; each is small enough on its own
  that CLAUDE.md's "one concern per commit" and the milestone's own "REQ-ci-verified does
  not belong bundled inside a large phase" instruction argued against merging.
- [Phase 02]: Task 2's TDD RED tests were committed together with GREEN, not as a separate failing commit, because the repo's pre-commit hook always runs full make verify with no bypass
- [Phase 02]: Container memory peak for bench.memory is sampled via docker stats --no-stream polling (0.5s interval) rather than reading a cgroup peak file, since the image's non-root/nologin user makes exec-based cgroup reads unreliable and the cgroup version was never verified. — Resolved 02-02-PLAN.md's flagged assumption 1 rather than deferring it; documented as a sampled (not exact) peak in code and bench/README.md.
- [Phase 02]: /api/health's pool fields (D-13) nest under one `pool` object rather than flat top-level keys or a separate endpoint (Task 3 checkpoint, 02-03-PLAN.md) — Every later pool field lands inside `pool` without touching the published top-level status/version the UI and container healthcheck already read -- converts a one-way decision (the response is a published contract Phase 4's OpenAPI work inherits) into a reversible one.
- [Phase 02]: SPUR_BUILD_TIMEOUT=30s (~4x the worst observed build, 7.39s); mem_limit=4g (N=2 measured peak 2878.5 MiB x1.3 headroom, confirmed at zero failures); max_tasks_per_child stays off (drift explained by ascending corpus tooth size, not a leak). — Every knob is set from bench/RESULTS.md's measured numbers, not guessed or derived from L07's superseded per-process formula.
- [Phase 02]: The concurrent latency scenario's pass bar (under-load p95 <= 2x idle p95) was NOT demonstrated met on this measurement session (2.02x, then 2.45x on a repeat run); recorded as a finding per the plan's own instruction rather than tuned into a pass. — Host was not fully idle at measurement time (load average 2.3-2.7 on a 12-core machine); absolute latencies are sub-millisecond and noise-sensitive. Needs a decision before REQ-cad-off-event-loop is marked complete -- see 02-04-SUMMARY.md Next Phase Readiness.
- [Phase 02]: Phase 2 halted before 02-05 to fix the concurrent /api/health latency cost first (route chosen by the human 2026-09-23), then re-measure, then resume 02-05. — Four latency runs measured 2.02-2.45x against the <=2x bar; 02-LATENCY-INVESTIGATION.md traced it to GZipMiddleware compresslevel=9 on 9 MB STL bodies in the serving process, with _EXPORTS cache hits bypassing admission control. Writing L17/L18 and the HEALTHCHECK timeout from those numbers would need a second edit after the fix, and retiring the debt file with the acceptance clause unmet would be a plausible-looking record L08 forbids. Fix via /gsd-quick (compresslevel from measurement, cache hits through an admission bound, cached compressed bytes if simple), re-run make bench.latency, resolve WINDOWS item 1 on evidence, then /gsd-execute-phase 2 for 02-05.
- [Quick 260923-qwr]: `_GZIP_LEVEL = 1`, measured on the real 9,062,784-byte teeth=199 fine STL (level 1: 51.5 ms median / 29.0% of input / 74.4 ms 10-concurrent wall; level 6: 147.9 ms / 26.5% / 198.9 ms; level 9: 788.0 ms / 26.5% / 925.5 ms; host loadavg 2.68/3.07/2.78). Levels 6 and 9 are only 8.7% / 8.66% smaller than level 1 -- under the plan's 10% bar -- so level 1 by the rule, not by taste. The comment beside the constant carries the table (2d47994).
- [Quick 260923-qwr]: model-body gzip moved out of GZipMiddleware into `model()`, performed inside `_build_slot()` in a worker thread and cached in `_EXPORTS` under an encoding-tagged key `(params, fmt, quality, encoding)` -- the middleware compresses only after the endpoint has returned and released its slot, so any bound placed inside the endpoint without moving the compression would have capped nothing. Concurrent compressions are now <= MAX_QUEUED_BUILDS and a repeat download of a compressed gear takes no slot and no compression; a first compression of an already-built gear can now be refused 503 busy (7a61fad, four behaviour tests). Not sized: Starlette's private `_gzip_capacity_limiter` RunVar (same private-internals objection as D-13).
- [Quick 260924-bv5]: `BuildPool.recreate_for` takes the failing request's own executor and replaces a slot only if it still holds it (one incident, one replacement, D-13's `workers_replaced` counted once), and shuts the old executor down WITHOUT `cancel_futures=True`: CPython keeps `max_workers + EXTRA_QUEUED_CALLS = 2` items RUNNING in the call queue, so only the fourth-and-later same-slot request was ever cancellable -- observed as an escaped `asyncio.CancelledError` (a 500) pre-fix, `BrokenProcessPool` -> 503 `pool_broken` after. `bench.memory sweep` now measures under its own 8 GiB ceiling via the existing override helper and refuses a row within 1% of it (L08). 02-REVIEW.md status: resolved.
- [Phase 02]: L17 (supersedes L07) and L18 (supersedes L06) appended to docs/architecture/decision_log.md with every number transcribed from bench/RESULTS.md; L18 records the concurrent latency scenario as accepted with caveat, not demonstrated, per the human's waiver -- no throughput number invented. — D-20's decision checkpoint (Option A, plus L19) resolved by the human before this continuation began.
- [Phase 02]: L19 (new) records the gzip-level/admission-bound decision from quick task 260923-qwr (compresslevel=1, compression moved inside _build_slot(), cached in _EXPORTS). — Human approved adding L19 alongside L17/L18 at the Task 1 checkpoint.
- [Phase 02]: Dockerfile HEALTHCHECK --timeout dropped from 10s to 2s (inner urlopen timeout 8s -> 1s), set from the measured under-load p95 (0.7-2.3 (worst 2.3 ms, Run 3 concurrent, pre-L19)ms across all eight bench/RESULTS.md latency runs). — CONTEXT.md: if the timeout cannot come down, that is evidence the phase did not land -- it came down.

### Pending Todos

None yet.

### Blockers/Concerns

- **Resolved (02-05):** L07 and L06 are superseded by L17 and L18
  (`docs/architecture/decision_log.md`) — the re-measured memory ceiling and the
  retired "concurrency buys latency, not throughput" consequence. No longer a blocker.
- **CI workflow unverified.** `.github/workflows/ci.yml` was hand-verified step-by-step but
  has never executed inside GitHub Actions (per `docs/plan-2026-09-21.md`). Now Phase 5's
  entire scope: a real push, a run URL, three jobs (`test` matrix, `vendor-bundle`,
  `image`) observed green.
- *(Resolved at v0.1 start: "Forward scope undefined" and "Success metric not derivable" —
  both set by the human, see PROJECT.md "Current Milestone" and "Success Metric". Resolved
  at roadmap creation: "Forward scope" now points to REQUIREMENTS.md "Future Requirements"
  as candidates for the next milestone, not phases in this one.)*
- REQ-cad-off-event-loop's concurrent-scenario latency ratio (bench/RESULTS.md) was not demonstrated within the 2x pass bar on Plan 02-04's measurement session (2.02x, 2.45x); a genuinely-idle-host re-run or an explicit accept-with-caveat decision is needed before this requirement is marked Complete. **Re-run (2026-09-23, ~12:11-12:12 UTC, dispatched by the human's `quiet` re-run choice):** two more runs against the same harness gave 2.32x and 2.35x -- still not met, and worse than the original session, because the host's load average climbed higher during the re-run (1-minute figures 3.33->3.96) than during the original measurement (2.35, 2.33), driven by an unrelated `node` process at 160.9% CPU. Four measurements across two sessions now agree the bar is not met on this machine under any environment condition observed so far; broken-windows ledger item 1 stays open. See `bench/RESULTS.md`'s "Idle-host re-run (Runs 3-4)" subsection and `02-04-SUMMARY.md`'s follow-up section.
- **Root cause investigated (2026-09-23):** a bounded investigation (no `src/`/`bench/` changes) found the ratio is a real server-side cost, not a harness artifact -- `GZipMiddleware`'s default `compresslevel=9` costs ~1.2-1.4s per concurrent compression of a 9MB fine STL, and a cache hit in `app.py`'s `model()` bypasses `_build_slot()`'s admission control entirely, so nothing bounds concurrent compression work for repeat downloads. See `.planning/phases/02-cad-off-the-event-loop/02-LATENCY-INVESTIGATION.md` for the full evidence and gap-plan recommendation.
- **Fix landed and re-measured (2026-09-23, quick task 260923-qwr):** `bench/RESULTS.md` "Post-fix re-run (Runs 5-6)", commit under test 7a61fad, loadavg 4.64 -> 3.58 -> 2.73 before the runs (still above the >1.5 idle bar). `concurrent`: **Run 5 1.31x (met), Run 6 2.10x (not met)**; `single`: Run 5 1.10x (met), Run 6 no p95 (n=19 < MIN_SAMPLES, refused per L08). Down from four straight failures (2.02x-2.45x) to one pass and one narrow miss, but the task's own rule was "mark WINDOWS item 1 fixed only if <=2x on both runs" -- so **item 1 stays open**. Needs a human decision before 02-05: (a) another two-run measurement on a genuinely idle host, (b) accept-with-caveat and waive the ledger item with a reason, or (c) a further fix (candidate 4 in the investigation, the result-transfer path, is the next lever named there).
- **Idle-host re-run, Runs 7-8 (2026-09-23, ~14:10-14:12 UTC, human chose option (a)):** host waited for, not asserted -- a watcher released the runs after three consecutive 1-minute load samples under 1.5 (1.35, 1.02, 1.05; a Time Machine pass and Spotlight indexing had finished on their own). Pre-run samples 1.11 / 1.20 / 1.63, the quietest session of the four. `concurrent`: **Run 7 1.86x (met), Run 8 2.02x (not met)**; `single`: Run 7 1.11x, Run 8 no p95 (n=18). `bench/RESULTS.md` "Idle-host re-run (Runs 7-8)". **Item 1 stays open.** Two observations recorded there, uninvestigated: every second run of a pair (the one inheriting the first run's cache) is worse than its first, before and after the fix (2.02->2.45, 2.32->2.35, 1.31->2.10, 1.86->2.02); and the verdict sits at the harness floor (idle p95 0.6 ms, so the bar is ~1.2 ms and Runs 7/8 differ by ~0.1 ms of p95). Options now: waive with this evidence; a bounded investigation of the second-run effect; or decide whether a like-for-like second run against a warm cache is the right thing to measure at all.
- **Waived (2026-09-23, human decision after Runs 7-8):** `.planning/WINDOWS.md` item 1 waived, reason carrying the Runs 1-8 evidence. Not demonstrated, accepted with caveat. The caveat and the two uninvestigated observations live in `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` (Severity: must; triggers: 02-05 writes L17/L18, harness/machine change, any run above 2.45x). 02-05 must carry it into L17/L18 verbatim rather than citing the bar as met.

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260923-qwr | Fix /api/health under-load latency: gzip level 1 from measurement, model-body compression inside _build_slot() and cached; Runs 5-6 concurrent 1.31x / 2.10x -- bar not met on both, WINDOWS item 1 stays open | 2026-09-23 | 2d47994..5a6e7d7 | [260923-qwr-fix-the-api-health-under-load-latency-co](./quick/260923-qwr-fix-the-api-health-under-load-latency-co/) |
| 260924-bv5 | Fix 02-REVIEW.md CR-01/CR-02/WR-01: recreate_for identity-guarded and no longer cancels pending futures (fourth same-slot request observed CancelledError pre-fix, BrokenProcessPool after); memory sweep runs under its own 8 GiB ceiling and refuses capped rows; 5 new tests, 76 passing | 2026-09-24 | 15fa5cd | [260924-bv5-fix-02-review-md-findings-cr-01-cr-02-an](./quick/260924-bv5-fix-02-review-md-findings-cr-01-cr-02-an/) |

## Deferred Items

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| *(none)* | | | | |

## Session Continuity

Last session: 2026-09-24T03:10:31.421Z
Stopped at: Phase 2 executed 5/5; 02-REVIEW.md findings all resolved (quick task 260924-bv5, commits 17048c9 d334049 08697f0 15fa5cd); verification stale after the fixes -- next: /gsd-verify-work 2 (re-verify, then the 2 UAT items in 02-UAT.md)
complete; Phases 2–5 derived from the five v0.1 requirements with 100% coverage; awaiting
human approval before `/gsd-plan-phase 2`.
Resume file: .planning/phases/02-cad-off-the-event-loop/02-UAT.md
