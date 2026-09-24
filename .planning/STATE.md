---
gsd_state_version: "1.0"
milestone: v0.1
current_phase: 04
current_phase_name: Typed Derived-Dimensions Contract
status: verifying
stopped_at: Completed 04-03-PLAN.md
last_updated: "2026-09-24T14:52:22.159Z"
last_activity: 2026-09-24
last_activity_desc: Phase 04 execution started
state_head: cfe5f8d9610ce18404a6dc33ada8beaf0623f802
progress:
  total_phases: 5
  completed_phases: 3
  total_plans: 11
  completed_plans: 11
milestone_name: Hardening
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-24)

**Core value:** A number this tool prints is a number someone will cut metal to — every
dimension is computed honestly or reported as a warning, never guessed (L08).
**Current focus:** Phase 04 — Typed Derived-Dimensions Contract

## Current Position

Phase: 04 (Typed Derived-Dimensions Contract) — EXECUTING
Plan: 3 of 3
Status: Phase complete — ready for verification
Last activity: 2026-09-24 — Phase 04 execution started

## Performance Metrics

**Velocity:**

- Total plans completed via GSD: 8 (Phase 2: 5, Phase 3: 3; v0 was built and verified
  directly against `make verify`, before this planning structure existed)
- Average duration: N/A
- Total execution time: N/A

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. v0 Baseline | N/A | N/A | N/A |
| 2. CAD Off the Event Loop | 5 | ~3h50m | ~46min |
| 3. Structured Logging | 3 | ~1h12m | ~24min |
| 4. Typed Derived-Dimensions Contract | TBD | - | - |
| 5. CI Observed Green | TBD | - | - |

**Recent Trend:** Phase 2's five plans took ~3h50m of executor time; 02-04 (~2h)
dominated because it waited on real benchmark runs, not on code. Phase 3's three plans
took ~1h12m; the post-review fix pass (CR-01/WR-01/WR-02, three commits) added ~10 min.
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 02 P01 | 30min | 3 tasks | 8 files |
| Phase 02 P02 | 19min | 3 tasks | 6 files |
| Phase 02 P03 | ~25min | 4 tasks | 4 files |
| Phase 02 P04 | ~2h | 3 tasks | 9 files |
| Phase 02 P05 | 35min | 3 tasks | 5 files |
| Phase 03 P01 | 25min | 3 tasks | 8 files |
| Phase 03 P02 | 27min | 3 tasks | 5 files |
| Phase 03 P03 | 20min | 3 tasks | 9 files |
| Phase 04 P01 | ~45min | 3 tasks | 11 files |
| Phase 04 P02 | 16min | 3 tasks | 9 files |
| Phase 04 P03 | 9min | 3 tasks | 7 files |

## Accumulated Context

### Decisions

Full decision log: PROJECT.md "Key Decisions" table (L01–L20, from
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
- [Phase 03]: build.failed carries no hash slot and worker.replaced carries no request id -- both deliberate boundary/type-signature limitations (03-02-PLAN.md flagged assumptions 1-2), correlated instead by stream adjacency and the cause field.
- [Phase 03]: gsd_run check tdd-red-evidence does not support pytest output (its TAP parser expects node --test format) -- RED phases in this Python project are verified by direct inspection of pytest failure output instead; documented in 03-02-SUMMARY.md's Issues Encountered for future TDD plans in this phase.
- [Phase 03]: L20 appended recording D-01 through D-04, D-06 and D-14, including why there are two idempotent configure() call sites (03-RESEARCH.md falsified the single-call-site assumption).
- [Phase 03]: docs/tech_debt/active/2026-09-21-no-structured-logging.md retired: Status: resolved, Resolved in: 21b8fe4 (Plan 03-02's commit, not this plan's own), git mv'd into resolved/, INDEX.md row moved -- same commit as the four corrected Logging sections.
- [Phase 03, post-review fixes 2a1900d/a2a2371/482c936]: `_JsonFormatter` renders `exc_info`/`stack_info` into `traceback`/`stack_info` fields only for records that carry them (uvicorn's "Exception in ASGI application" record) -- spur's own helpers never set `exc_info`, so D-06/T-03-05 hold; `model()` gained a catch-all that logs `build.failed` and re-raises, with `HTTPException` passed through untouched so a 503 refusal does not double-log; import-linter contract "The gear maths stays free of the logger" forbids `spur.calc` -> `spur.records`/`logging`.
- [Phase 04]: DerivedDimensions: 19-field frozen pydantic model, no defaults on any field, derive() as the single construction site; with_mate() deleted (D-01, D-02, D-09). — A default would make a key optional in OpenAPI, contradicting the always-present/null-where-it-doesn't-apply contract (Pitfall 2); a single construction site means a shape bug fails loudly instead of quietly matching dict[str, Any].
- [Phase 04]: pool._run_with_timeout forwards through functools.partial(func, *args, **kwargs), not a bare *args/**kwargs pass-through to run_in_executor -- run_in_executor takes positional arguments only, and PEP 612 requires *args: P.args and **kwargs: P.kwargs declared together, so a signature that only forwarded *args would type-check while silently dropping any keyword argument.
- [Phase 04]: app.py's lifespan now dels app.state.pool in its finally block, in addition to shutting it down -- app is one module-level FastAPI singleton shared across every test file in a pytest session, and a shut-down pool object was lingering for a later, lifespan-free test client to see (04-02 Rule 1 deviation).
- [Phase 04]: Plan 04-03: L21 appended superseding L14 -- disallow_any_explicit on globally, satisfiable via the pydantic mypy plugin's init_typed/init_forbid_extra settings (R-1, human decision) rather than per-class suppression comments.
- [Phase 04]: Plan 04-03: spur info --mate-teeth range-checked to InfoQuery's ge=6/le=1000 bounds (R-2, human decision); --mate-teeth 0 now exits 2 instead of meaning 'no mate'.

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
- ⚠️ [Phase 3] A cached `cq.Solid`'s `.BoundingBox()` reads wrong after `exportStl()` has
  attached a coarser mesh to the same object — `model.py`'s process-global `_build_cached`
  LRU shares the mutable solid across calls. No production caller today and STL bytes are
  unaffected; the suite is protected by an autouse cache-clearing fixture.
  `docs/tech_debt/active/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md`
  (must). Triggers: a feature needs a measured dimension from a `Solid` after export, or a
  test outside the fixture's protection hits the symptom.
- *(Resolved in Phase 3: "No structured logging anywhere" — `21b8fe4`/`013997a`, moved to
  `docs/tech_debt/resolved/`; L20. Resolved in Phase 2: "CAD builds block the event loop" — `daeb284`, moved to
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

Last session: 2026-09-24T14:52:22.129Z
Stopped at: Completed 04-03-PLAN.md
Resume file: None
