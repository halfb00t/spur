---
gsd_state_version: "1.0"
milestone: v0.1
current_phase: 02
current_phase_name: CAD Off the Event Loop
status: executing
stopped_at: "Phase 2 at 4/5: fix-first route chosen; next is /gsd-quick for the gzip/admission fix + re-measure, then /gsd-execute-phase 2 for 02-05"
last_updated: "2026-09-23T13:07:53.192Z"
last_activity: 2026-09-23
last_activity_desc: Phase 02 execution started
state_head: "0b5ffe2ef7573f657beb7e9f09fa1d9187958fd6"
progress:
  total_phases: 5
  completed_phases: 1
  total_plans: 5
  completed_plans: 4
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

Phase: 02 (CAD Off the Event Loop) — EXECUTING
Plan: 5 of 5
Status: Ready to execute
Last activity: 2026-09-23 — Phase 02 execution started
the five v0.1 requirements, 100% coverage validated.

Progress: [██░░░░░░░░] 20%

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

### Pending Todos

None yet.

### Blockers/Concerns

- **L07 needs superseding, not rewriting.** L07 fixes the memory story on *per-process*
  bounded caches plus `malloc_trim(0)`, with a measured 1.87 GiB → 358 MiB result backing
  `compose.yaml`'s `mem_limit: 2g`. Moving CAD builds to a process pool makes those caches
  per-worker and invalidates that formula. Phase 2 carries this: a new superseding `Lxx`
  in `docs/architecture/decision_log.md` with a **re-measured** ceiling — an estimated
  `mem_limit` would be exactly the guessed number L08 forbids. Largest risk in v0.1.
- **L06 also needs superseding, not rewriting.** Same phase, second entry: "concurrency
  buys latency, not throughput" no longer holds once a process pool exists; the `RLock`'s
  scope becomes per-worker rather than global.
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

## Deferred Items

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| *(none)* | | | | |

## Session Continuity

Last session: 2026-09-23T13:07:18.961Z
Stopped at: Phase 2 at 4/5: fix-first route chosen; next is /gsd-quick for the gzip/admission fix + re-measure, then /gsd-execute-phase 2 for 02-05
complete; Phases 2–5 derived from the five v0.1 requirements with 100% coverage; awaiting
human approval before `/gsd-plan-phase 2`.
Resume file: .planning/phases/02-cad-off-the-event-loop/02-LATENCY-INVESTIGATION.md
