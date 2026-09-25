---
gsd_state_version: "1.0"
milestone: v0.1
current_phase: 06
current_phase_name: "Address tech debt: merge gate + solid cache"
status: executing
stopped_at: Completed 06-03-PLAN.md
last_updated: "2026-09-25T12:53:50.439Z"
last_activity: 2026-09-25
last_activity_desc: Phase 06 execution started
state_head: ff7441a0a8bcc6d6903c9cdf90cdc9d22fece76e
progress:
  total_phases: 6
  completed_phases: 5
  total_plans: 21
  completed_plans: 20
milestone_name: Hardening
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-25)

**Core value:** A number this tool prints is a number someone will cut metal to — every
dimension is computed honestly or reported as a warning, never guessed (L08).
**Current focus:** Phase 06 — Address tech debt: merge gate + solid cache

## Current Position

Phase: 06 (Address tech debt: merge gate + solid cache) — EXECUTING
Plan: 4 of 4
Status: Ready to execute
Last activity: 2026-09-25 — Phase 06 execution started

## Performance Metrics

**Velocity:**

- Total plans completed via GSD: 17 (Phase 2: 5, Phase 3: 3, Phase 4: 3, Phase 5: 6; v0 was built and verified
  directly against `make verify`, before this planning structure existed)
- Average duration: N/A
- Total execution time: N/A

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. v0 Baseline | N/A | N/A | N/A |
| 2. CAD Off the Event Loop | 5 | ~3h50m | ~46min |
| 3. Structured Logging | 3 | ~1h12m | ~24min |
| 4. Typed Derived-Dimensions Contract | 3 | ~1h10m | ~23min |
| 5. CI Observed Green | 6 | ~1h38m | ~16min |

**Recent Trend:** Phase 2's five plans took ~3h50m of executor time; 02-04 (~2h)
dominated because it waited on real benchmark runs, not on code. Phase 3's three plans
took ~1h12m; the post-review fix pass (CR-01/WR-01/WR-02, three commits) added ~10 min.
Phase 4's three plans took ~1h10m: 04-01 (~45 min — reconstructed, not measured) carried
the model and the three contract tests; 04-02 and 04-03 were 16 and 9 measured minutes.
Code review came back clean (1 info) and verification passed 4/4 with no fix pass.
Phase 5's six plans took ~1h38m: 05-02 (~35 min, the live `make pr.land` tracer) dominated;
the rest were 11–14 min each. Code review found CR-01 (pr.land's cut-line bypass) and
verification scored 4/5; gap-closure plan 05-06 (13 min) closed it, the re-review was clean
and re-verification passed 5/5.
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
| Phase 05 P01 | 12 min | 2 tasks | 8 files |
| Phase 05 P02 | ~35min | 2 tasks | 5 files |
| Phase 05 P03 | ~13min | 3 tasks | 3 files |
| Phase 05 P04 | 14 min | 3 tasks | 10 files |
| Phase 05 P05 | ~11min | 3 tasks | 13 files |
| Phase 05 P06 | 13min | 2 tasks | 5 files |
| Phase 06 P01 | ~20min | 2 tasks | 6 files |
| Phase 06 P02 | 9min | 2 tasks | 6 files |
| Phase 06 P03 | 10min | 3 tasks | 6 files |

## Accumulated Context

### Decisions

Full decision log: PROJECT.md "Key Decisions" table (L01–L21, from
`docs/architecture/decision_log.md`). Flagged for revisit there: L10 (radial root
fillet — trochoidal is a tracked idea) and L18 (ten-concurrent latency bar accepted with
caveat). L14 was superseded by L21 in Phase 4 — the ratchet is on, not deferred again.

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
- [Phase 05]: Python, not bash, for the skip-token hook -- Plan 05-02's make pr.land must import the same find_skip_tokens() to check the squash commit's subject and body; one importable module is the only way the two checks cannot drift apart. — 05-01-SUMMARY.md key-decisions
- [Phase 05]: The verify pre-commit hook needed stages: [pre-commit] -- an unpinned hook inherits every installed stage and ran make verify twice per commit once commit-msg joined default_install_hook_types (planning-probe finding, re-confirmed live). — 05-01-SUMMARY.md key-decisions
- [Phase 05]: Git's commit -v scissors cut line is exactly '# ' + 24 dashes + ' >8 ' + 24 dashes -- verified byte-for-byte in a scratch repo this session, not taken from the plan's prose alone. — 05-01-SUMMARY.md key-decisions
- [Phase 05]: 05-02: head_refusals gains a required compare:tuple[int,int] param (no default) in Task 2 -- check_head always fetches it, so a default would be dead code — Task 1's own tests updated in the same commit to pass a neutral NOT_BEHIND=(1,0)
- [Phase 05]: 05-02: JSON-field narrowing uses isinstance-based _as_object/_as_array/_as_int/_as_str helpers raising TypeError, not # type: ignore comments — mypy --strict flagged the ignore comment as unused/wrong-code; ruff TRY004/TRY301/TRY300 flagged the inline isinstance-raise pattern; matches L21's object-narrowed-at-use convention
- [Phase 05]: 05-03: Retargeted the repository's existing `default` ruleset (id 23977515) onto `main` rather than creating a second ruleset -- planning's flagged assumption 1 confirmed live before the change (empty `include`, exactly deletion/non_fast_forward/pull_request); required checks are the post-D-09 set (test (3.12), vendor-bundle, image) applied now, before Plan 05-04 collapses the CI matrix
- [Phase 05]: 05-03: docs/HOW_TO_DEVELOP.md Section 8's old manual `git switch main && git pull --ff-only ... && git branch -D ...` block was removed entirely rather than merged with the new pr.land description -- make pr.land performs every one of those steps itself (confirmed against scripts/pr_land.py's land() control flow); L22 is one decision-log entry covering D-02 through D-05 and D-12, not five entries
- [Phase 05]: Plan 05-04: kept the one-entry CI matrix (test (3.12)) rather than a bare test job -- required-jobs.txt and the live ruleset both name that string; widening later is one line, a rename would need a ruleset update too — Plan's flagged assumption 3, confirmed against the live ruleset read-back in Task 3
- [Phase 05]: Plan 05-04: the ruleset on main needed no write -- Plan 05-03 already applied the post-D-09 required-check set, so Task 3's live read-back confirmed agreement rather than changing anything — gh api repos/halfb00t/spur/rules/branches/main read back exactly image;test (3.12);vendor-bundle, matching the collapsed required-jobs.txt byte-for-byte
- [Phase 05]: [Phase 05]: Plan 05-05: STATE.md's CI-unverified blocker was removed with one scoped edit inside Blockers/Concerns rather than state.resolve-blocker, which filters single '- ' lines and would orphan the bullet's three continuation lines — Plan's flagged assumption 3
- [Phase 05]: 05-06: the cut moves into the hook's main() (editor-only), not find_skip_tokens -- pr_land.py's code is unchanged; message_refusals now searches the whole PR title/body with no cut, closing CR-01's reproduced bypass. The one residual (a hand-typed cut line inside an editor session without -v) is filed as must debt, backstopped by the ruleset on main, make pr.land's run check, and D-03.
- [Phase 06]: shape.copy() before exportStl(), not BRepTools.Clean_s() — Clean_s measured 4-13% faster but strips the mesh after export, so the cached object would carry a mesh through the whole export window while build() releases _LOCK before callers read the solid; a copy keeps the cached solid mesh-free for its whole life instead. -- 06-01-SUMMARY.md key-decisions
- [Phase 06]: Content equivalence (triangle count + decoded volume, rel=1e-6), never raw STL bytes, is D-08's proof — OCCT export matched byte-for-byte in only 8 of 20 reruns across independently built solids at planning/research time. -- 06-01-SUMMARY.md key-decisions
- [Phase 06]: No replacement autouse fixture for the deleted solid-cache reset (D-09) — make verify's 185-test pass with the fixture gone is the only cross-test proof needed; no test relied on a cold cache for an unrelated reason. -- 06-01-SUMMARY.md key-decisions
- [Phase 06]: 06-02: two test fixtures dropped the blank line before a hand-typed cut line so the second matched token lands on the plan's own stated line 4, not line 5 -- verified with a throwaway regex walk against the literal message text before writing the assertion. — The plan's <behavior> block and the D-02 case both specify line 4; keeping the blank line (a literal reuse of the prior test's spacing) would have put the token on line 5 instead, per re.finditer computed against the exact fixture string.
- [Phase 06]: Task 2's RED phase used a temporary stub-then-restore of _effective_job_names (ids-only, no name: lookup) rather than a separate intermediate commit -- the plan's own action text offered this as an alternative to a stub helper, and it was the more direct way to prove RED once the block-scoped implementation was already drafted. — Proves a genuine RED assertion failure before GREEN without committing a throwaway helper; the plan text explicitly sanctioned this path.
- [Phase 06]: The plan's own Task 2 <verify> command (-k 'job_name', expecting '2 passed') collides with a pre-existing test name (test_head_refusals_one_red_job_names_it_and_its_conclusion) and prints '3 passed' instead -- verified via the task's acceptance_criteria and a narrower -k selector, not treated as a failure. — The plan text is a historical record of what was specified and is not edited by execution; the task's own acceptance_criteria and make verify are the authoritative pass signal.

### Pending Todos

None yet.

### Blockers/Concerns

- ⚠️ [Phase 2] The ten-concurrent `/api/health` latency bar (≤2.00x idle p95) was waived,
  not demonstrated: eight runs across four sessions read 1.31x–2.45x and never ≤2.00x on
  both runs of one session. The caveat and two uninvestigated observations (every second
  run of a pair is worse than its first; the verdict sits at the harness floor, ~0.1 ms of
  p95) live in `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`
  (must). Triggers: the harness or the machine changes, or any run reads above 2.45x.
  History: `bench/RESULTS.md`, `02-LATENCY-INVESTIGATION.md`, `02-04-SUMMARY.md`.
- ⚠️ [Phase 5] The `commit-msg` hook cannot see a skip token hidden below a git cut line
  typed by hand inside an editor session without `-v` — by content it is identical to git's
  own `commit -v` diff, which the hook must skip. Backstopped: the ruleset on `main` refuses
  a head without green required checks, `make pr.land` refuses a run-less head, and after
  D-03 a branch commit's message never becomes `main`'s.
  `docs/tech_debt/active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md` (must).
- *(Resolved in Phase 6: "A cached solid's `.BoundingBox()` reads wrong after
  `exportStl()`" — `655ec52` (`_write_export` meshes `shape.copy()`, autouse cache reset
  deleted) and `f17bda0` (L24, debt file moved), 06-01-SUMMARY.md. Resolved in Phase 5:
  "CI workflow unverified" — the premise was false: main push run
  <https://github.com/halfb00t/spur/actions/runs/35963114939> (`59f02c3`, all four jobs
  green) and PR #3 head run <https://github.com/halfb00t/spur/actions/runs/36088409707>
  (`2c4b544`, tree-identical to `bfc9110`); L22's merge gate keeps it true, and this
  phase's own squash-commit run is recorded after `make pr.land` prints it. Resolved in
  Phase 4: "Untyped info contract" — `013900d` (the model) / `cfe5f8d` (the
  rule turned on and the debt file retired, same commit), moved to
  `docs/tech_debt/resolved/`; L14 superseded by L21. Resolved in Phase 3: "No structured logging anywhere" — `21b8fe4`/`013997a`, moved to
  `docs/tech_debt/resolved/`; L20. Resolved in Phase 2: "CAD builds block the event loop" — `daeb284`, moved to
  `docs/tech_debt/resolved/`; L06/L07 superseded by L18/L17. Resolved at v0.1 start:
  "Forward scope undefined" and "Success metric not derivable" — both set by the human,
  see PROJECT.md "Current Milestone" and "Success Metric".)*

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260923-qwr | Fix /api/health under-load latency: gzip level 1 from measurement, model-body compression inside _build_slot() and cached; Runs 5-6 concurrent 1.31x / 2.10x -- bar not met on both, WINDOWS item 1 stays open | 2026-09-23 | 2d47994..5a6e7d7 | [260923-qwr-fix-the-api-health-under-load-latency-co](./quick/260923-qwr-fix-the-api-health-under-load-latency-co/) |
| 260924-bv5 | Fix 02-REVIEW.md CR-01/CR-02/WR-01: recreate_for identity-guarded and no longer cancels pending futures (fourth same-slot request observed CancelledError pre-fix, BrokenProcessPool after); memory sweep runs under its own 8 GiB ceiling and refuses capped rows; 5 new tests, 76 passing | 2026-09-24 | 15fa5cd | [260924-bv5-fix-02-review-md-findings-cr-01-cr-02-an](./quick/260924-bv5-fix-02-review-md-findings-cr-01-cr-02-an/) |

### Roadmap Evolution

- Phase 5 edited: edited fields: goal, success_criteria (reframed per 05-CONTEXT.md D-10), Phases-list one-liner
- Phase 6 added: Address tech debt: merge gate + solid cache

## Deferred Items

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| *(none)* | | | | |

## Session Continuity

Last session: 2026-09-25T12:53:50.399Z
Stopped at: Completed 06-03-PLAN.md
Resume file: None
