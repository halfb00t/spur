---
gsd_state_version: "1.0"
milestone: v0.1
current_phase: 02
current_phase_name: CAD Off the Event Loop
status: executing
stopped_at: Completed 02-02-PLAN.md
last_updated: "2026-09-23T03:10:52.411Z"
last_activity: 2026-09-23
last_activity_desc: Phase 02 execution started
state_head: 8920c197ea560fb029d1a3a3b7b0b5bfbda372d8
progress:
  total_phases: 5
  completed_phases: 1
  total_plans: 5
  completed_plans: 2
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
Plan: 3 of 5
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

## Deferred Items

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| *(none)* | | | | |

## Session Continuity

Last session: 2026-09-23T03:10:52.393Z
Stopped at: Completed 02-02-PLAN.md
complete; Phases 2–5 derived from the five v0.1 requirements with 100% coverage; awaiting
human approval before `/gsd-plan-phase 2`.
Resume file: None
