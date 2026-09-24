---
gsd_state_version: "1.0"
milestone: v0.1
current_phase: 03
current_phase_name: Structured Logging at the Composition Boundary
status: executing
stopped_at: Completed 03-01-PLAN.md
last_updated: "2026-09-24T09:28:53.899Z"
last_activity: 2026-09-24
last_activity_desc: Phase 03 execution started
state_head: 047c1231a78a3cfed1a16f714d9e588c6f39f434
progress:
  total_phases: 5
  completed_phases: 2
  total_plans: 8
  completed_plans: 6
milestone_name: Hardening
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-24)

**Core value:** A number this tool prints is a number someone will cut metal to — every
dimension is computed honestly or reported as a warning, never guessed (L08).
**Current focus:** Phase 03 — Structured Logging at the Composition Boundary

## Current Position

Phase: 03 (Structured Logging at the Composition Boundary) — EXECUTING
Plan: 2 of 3
Status: Ready to execute
Last activity: 2026-09-24 — Phase 03 execution started

## Performance Metrics

**Velocity:**

- Total plans completed via GSD: 5 (Phase 2; v0 was built and verified directly against
  `make verify`, before this planning structure existed)
- Average duration: N/A
- Total execution time: N/A

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. v0 Baseline | N/A | N/A | N/A |
| 2. CAD Off the Event Loop | 5 | ~3h50m | ~46min |
| 3. Structured Logging | TBD | - | - |
| 4. Typed Derived-Dimensions Contract | TBD | - | - |
| 5. CI Observed Green | TBD | - | - |

**Recent Trend:** Phase 2's five plans took ~3h50m of executor time; 02-04 (~2h)
dominated because it waited on real benchmark runs, not on code.
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 02 P01 | 30min | 3 tasks | 8 files |
| Phase 02 P02 | 19min | 3 tasks | 6 files |
| Phase 02 P03 | ~25min | 4 tasks | 4 files |
| Phase 02 P04 | ~2h | 3 tasks | 9 files |
| Phase 02 P05 | 35min | 3 tasks | 5 files |
| Phase 03 P01 | 25min | 3 tasks | 8 files |

## Accumulated Context

### Decisions

Full decision log: PROJECT.md "Key Decisions" table (L01–L19, from
`docs/architecture/decision_log.md`). Flagged for revisit there: L10 (radial root
fillet — trochoidal is a tracked idea), L14 (`disallow_any_explicit` off — retired by
Phase 4, not just revisited) and L18 (ten-concurrent latency bar accepted with caveat).

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

Phase 2 (full detail: the `02-0x-SUMMARY.md` files, `bench/RESULTS.md`, decision log
L17–L19):

- L17/L18/L19 appended with every number transcribed from `bench/RESULTS.md`; L18 records
  the ten-concurrent scenario as accepted with caveat, not demonstrated (human waiver
  after Runs 1–8: 2.02x, 2.45x, 2.32x, 2.35x, 1.31x, 2.10x, 1.86x, 2.02x vs a ≤2.00x bar).
- Every knob from measurement, none from L07's superseded formula: `SPUR_BUILD_TIMEOUT=30s`
  (~4× the worst build, 7.39 s), `mem_limit=4g` (N=2 peak 2878.5 MiB × 1.3),
  `max_tasks_per_child` off (drift tracked the ascending corpus, not a leak), Dockerfile
  HEALTHCHECK `--timeout=2s` from the 0.7–2.3 ms under-load p95.
- `/api/health`'s pool fields nest under one `pool` object (D-13) so later fields never
  touch the published top-level `status`/`version` the UI and healthcheck read.
- Model-body gzip at `compresslevel=1` runs inside `_build_slot()` and is cached per
  encoding (quick 260923-qwr, L19); `BuildPool.recreate_for` replaces one slot per
  incident and no longer cancels pending futures (quick 260924-bv5, CR-01/WR-01).
- TDD RED tests were committed together with GREEN, not as a separate failing commit: the
  pre-commit hook runs the full `make verify` with no bypass.
- [Phase 03]: records.py falls back to record.getMessage() for the event field when a record carries no event extra (uvicorn's own records), so the shared formatter never raises on a record it did not originate.
- [Phase 03]: Filed docs/tech_debt/active/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md (must): model.py's process-global solid cache lets exportStl()'s mesh side effect skew a later .BoundingBox() call on the same cached object; no production code calls BoundingBox() today, fixed test-side via an autouse cache-clearing fixture.

### Pending Todos

None yet.

### Blockers/Concerns

- **CI workflow unverified.** `.github/workflows/ci.yml` was hand-verified step-by-step but
  has never executed inside GitHub Actions (per `docs/plan-2026-09-21.md`). Now Phase 5's
  entire scope: a real push, a run URL, three jobs (`test` matrix, `vendor-bundle`,
  `image`) observed green.
- ⚠️ [Phase 2] The ten-concurrent `/api/health` latency bar (≤2.00x idle p95) was waived,
  not demonstrated: eight runs across four sessions read 1.31x–2.45x and never ≤2.00x on
  both runs of one session. The caveat and two uninvestigated observations (every second
  run of a pair is worse than its first; the verdict sits at the harness floor, ~0.1 ms of
  p95) live in `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`
  (must). Triggers: the harness or the machine changes, or any run reads above 2.45x.
  History: `bench/RESULTS.md`, `02-LATENCY-INVESTIGATION.md`, `02-04-SUMMARY.md`.
- *(Resolved in Phase 2: "CAD builds block the event loop" — `daeb284`, moved to
  `docs/tech_debt/resolved/`; L06/L07 superseded by L18/L17. Resolved at v0.1 start:
  "Forward scope undefined" and "Success metric not derivable" — both set by the human,
  see PROJECT.md "Current Milestone" and "Success Metric".)*

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

Last session: 2026-09-24T09:28:53.874Z
Stopped at: Completed 03-01-PLAN.md
Resume file: None
