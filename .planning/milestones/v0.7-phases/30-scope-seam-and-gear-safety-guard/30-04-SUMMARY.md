---
phase: 30-scope-seam-and-gear-safety-guard
plan: 04
subsystem: api
tags: [seam, part-type, serve-model, pure-move, 503-wording, fastapi]

requires:
  - phase: 30-scope-seam-and-gear-safety-guard
    provides: "30-01: make gear.unchanged; 30-03: parts.py (Part), the ten import contracts and tests/test_seam.py, which guard every edit here"
provides:
  - "Part at the shared entry points: pool.py (5), records.py (5), app.py (BuildBackend, _build_slot), model.py (build, export)"
  - "src/spur/app.py::_serve_model, the one serving path; model() delegates to it"
  - "part-neutral 503 queue-full text, pinned by test_a_saturated_service_names_its_queue_in_parts"
affects: [30-05, 31, 32, 33]

plan_head_before: d6e97b495c0511f97f9456124c571274e16098f5
plan_head_after: 92fc0d4a74d722f3bb950f050b37564e5dd02fc4

actuals:
  tokens: 7200    # chars/4 over `git diff d6e97b4 HEAD` (28735 chars, the four kept logs included), before this SUMMARY
  tasks: 3
  commits: 3      # MEASURED: git rev-list --count d6e97b495c0511f97f9456124c571274e16098f5..HEAD, before this SUMMARY's own commit

tech-stack:
  added: []
  patterns:
    - "a pure move is proved mechanically against the commit (anchor-to-anchor body compare modulo two named substitutions), not by reading the diff"
    - "the logs of a pure commit ride in the next commit so the pure commit stays one concern"

key-files:
  created: []
  modified:
    - src/spur/pool.py
    - src/spur/records.py
    - src/spur/app.py
    - src/spur/model.py
    - tests/test_api.py
    - bench/RESULTS.md

key-decisions:
  - "Phase 31 widens the shared entry points by editing the alias in parts.py alone; the gear's internal helpers, InfoQuery, ModelQuery, _gear and schema() keep GearParams (D-08)"
  - "_serve_model sits above the model route and takes the validated params as an argument; Phase 33's shaft routes become its second caller (D-07, ARCHITECTURE F3)"
  - "No dispatch stub in model.py: its diff since v0.6 adds no isinstance and names no shaft module (D-10)"

patterns-established:
  - "Move first, reword second: the response string changed in its own commit, after the pin was seen red against the old text"

requirements-completed: [REQ-gear-unchanged-proof, REQ-shaft-routes-separate]

coverage:
  - id: D1
    description: "pool.py (5), records.py (5), app.py (BuildBackend, _build_slot) and model.py (build, export) name Part, imported from spur.parts; the gear internals keep GearParams"
    requirement: REQ-shaft-routes-separate
    verification:
      - kind: other
        ref: "make lint typecheck lint-imports gear.unchanged (30-04-annotations.log): exit 0, 'Contracts: 10 kept, 0 broken.'; model.py numstat 3/2; stat lists the four files only"
        status: pass
      - kind: unit
        ref: "tests/test_api.py tests/test_pool.py tests/test_records.py tests/test_cli.py: 154 passed (30-04-annotations.log)"
        status: pass
    human_judgment: false
  - id: D2
    description: "model()'s serving body moved into _serve_model unchanged, in a commit holding app.py alone, no test edited"
    requirement: REQ-gear-unchanged-proof
    verification:
      - kind: other
        ref: "30-04-pure-move.log: 'pure move: 115 lines identical'; git show --stat of ca60285 lists src/spur/app.py only"
        status: pass
      - kind: unit
        ref: "tests/test_api.py tests/test_pool.py tests/test_records.py tests/regression tests/test_browser.py: 185 passed, unedited (30-04-move-tests.log)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The 503 queue-full message counts parts; status, Retry-After and type are unchanged; the pin was seen red against the old wording"
    requirement: REQ-shaft-routes-separate
    verification:
      - kind: unit
        ref: "tests/test_api.py#test_a_saturated_service_names_its_queue_in_parts; -k saturated: 3 passed"
        status: pass
      - kind: other
        ref: "30-04-red-503.log: 1 failed on the message assertion only; bench/RESULTS.md '| 30-04 |' row"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every one of the three commits leaves make gear.unchanged green and no gear request, part, /api/schema byte or status code moves"
    requirement: REQ-gear-unchanged-proof
    verification:
      - kind: other
        ref: "make gear.unchanged green after each commit (8723 bytes, byte-equal to v0.6); git diff --exit-code v0.6 over calc.py, params.py, tests/regression/, ci.yml, requirements.txt empty; make verify exit 0"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-10-23
status: complete
---

# Phase 30 Plan 04: The seam on the gear side Summary

**`Part` at the shared entry points, `model()`'s serving body moved byte for byte into `_serve_model` (115 lines, proved mechanically), and a 503 queue-full text that counts parts, each in its own commit and each leaving `make gear.unchanged` green**

## Performance

- **Duration:** about 12 min (start 2026-10-23T16:24Z, end 2026-10-23T16:37Z); the two full `make verify` runs were 3 min 49 s each
- **Tasks:** 3
- **Files modified:** 6 source, test and doc files plus 4 logs

## Accomplishments

- Task 1: the params import in `pool.py` and `records.py` became `from .parts import Part` and their ten parameters read `p: Part`; `app.py` gained the import and `BuildBackend` and `_build_slot` take `Part`; `model.py` gained the import and `build` and `export` take `Part`. `model.py`'s numstat is `3	2` as the plan fixes. `_build`, `_build_checked`, `_write_export`, every `_cut_*`, `InfoQuery`, `ModelQuery`, `_gear` and `schema()` keep `GearParams`.
- Task 2: `_serve_model(params, fmt, quality, request, backend)` holds the body from the D-13 request-id comment through the final `Response`; `model()` keeps its decorator, `responses=`, signature and annotations and returns `await _serve_model(_gear(q), fmt, q.quality, request, backend)`. The move was checked against the commit: `pure move: 115 lines identical`.
- Task 3: the pin `test_a_saturated_service_names_its_queue_in_parts` was written first and read `AssertionError: assert 'Busy: 4 gear... in a moment.' == 'Busy: 4 part... in a moment.'` at the message assertion only (status, `retry-after` and `type` passed before it). The one-word change in `_build_slot` turned it green; `-k saturated` reads `3 passed`. No other file in `src`, `tests` or `docs` held the old text.

## Task Commits

1. **Task 1: the entry points name `Part`** - `e0e9225911f93e25a72e3d9db10c4ad7fe8ffaed` (refactor). The stat lists `pool.py`, `records.py`, `app.py` and `model.py` only.
2. **Task 2: `_serve_model`, a pure move** - `ca6028563ee926dec5de1b078d4091420b6eecbb` (refactor). `app.py` alone, no test edited. **This is the move's sha.**
3. **Task 3: the busy refusal counts parts** - `92fc0d4a74d722f3bb950f050b37564e5dd02fc4` (fix). `app.py`, `tests/test_api.py`, `bench/RESULTS.md` and the four `30-04-*.log` files.

**Plan metadata:** the `docs(30-04)` commit that adds this file, STATE.md, ROADMAP.md and REQUIREMENTS.md.

## Files Created/Modified

- `src/spur/pool.py`, `src/spur/records.py` - `Part` on five parameters each
- `src/spur/app.py` - `Part` on `BuildBackend` and `_build_slot`; `_serve_model`; the part-neutral 503 text
- `src/spur/model.py` - `Part` on `build` and `export`
- `tests/test_api.py` - the 503 text pin (21 lines)
- `bench/RESULTS.md` - one row appended to `### Seen red once (Phase 30)` (1 added, 0 deleted)
- `.planning/phases/30-scope-seam-and-gear-safety-guard/investigation/30-04-annotations.log`, `30-04-pure-move.log`, `30-04-move-tests.log`, `30-04-red-503.log`

## Decisions Made

- `_serve_model` is placed above the model route, as the plan says, and takes the already-validated params; it keeps `Literal` types on `fmt` and `quality` so the OpenAPI document and the query model do not move.
- The new test's message is written as an f-string on `app_module.MAX_QUEUED_BUILDS`, as the plan states, so the pin follows the configured queue size.

## Deviations from Plan

**1. [Acceptance criterion] The `-(async def model|@app.get("/api/model)` grep prints 2, not 0**
- **Found during:** Task 2 acceptance
- **Issue:** the criterion reads the diff of the move commit for deleted route-header lines. Git (myers, minimal, patience and histogram alike) aligns the long moved body with the old body and shows the four-line header as deleted at the old spot and added after `_serve_model`. The lines themselves are unchanged and the route stays in the same place relative to the rest of the file.
- **Fix:** none to the code. The substantive claim was checked instead: the five header lines (decorator, `responses=`, signature, two continuation lines) read identically at the old commit and at `ca60285` (`True`, printed from a `git show` compare of both blobs), and the whole suite, including the OpenAPI-reading route pin in `tests/test_seam.py` and `gear.unchanged`'s `/api/schema` compare, passed. Putting `_serve_model` below `model()` would have satisfied the grep but contradicts "above the model route" in the same task.
- **Files modified:** none
- **Commit:** ca60285

**2. [Instruction conflict] Commit trailer**
- The session's attribution reminder names `Claude Sonnet 5.5`; all three commits carry it, as the earlier plans' do.

**Total deviations:** 0 auto-fixed, 1 acceptance-criterion note, 1 instruction conflict. **Impact:** none on the seam or its proofs.

## Issues Encountered

- BSD `sed -i` on macOS reads `-e` after `-i` as the backup suffix; the first attempt at the Task 1 edit failed before touching any file and was rerun with `-i ''`.
- The pre-commit hook ran `make verify.fast` (which includes `gear.unchanged`) on all three commits and passed.
- No item was filed under `docs/tech_debt/` or `docs/ideas/`.

## Known Stubs

None.

## Threat Flags

None. No endpoint, auth path or schema change; the 503 text carries only the configured queue size, which `/api/health` already reports.

## User Setup Required

None - no external service configuration required.

## Verification

- `make verify`: exit 0, `1369 passed in 229.05s (0:03:49)`, `Contracts: 10 kept, 0 broken.`, `Required test coverage of 96.0% reached. Total coverage: 98.00%`, run after the third commit.
- `make gear.unchanged`: green after each commit, `tests/regression/, .github/workflows/ci.yml and /api/schema (8723 bytes) are byte-equal to v0.6`.
- `git diff --exit-code v0.6 -- src/spur/calc.py src/spur/params.py tests/regression/ .github/workflows/ci.yml requirements.txt`: empty.
- `git diff v0.6 -- src/spur/model.py`, added lines matching `isinstance|shaft`: 0 (D-10).
- Plan acceptance re-run: `p: Part` 5 and 5; `^from .parts import Part$` once in each of the four files; `BuildBackend` and `_build_slot` lines once each; `^def (build|export)\(p: Part` 2; `return await _serve_model(...)` once; `^async def _serve_model(` once; `request_id = uuid.uuid4().hex[:8]` once; `parts are already being built or` once; the new test once; `| 30-04 |` once; Task 3's stat lists the seven expected files; `git status --porcelain` showed only the orchestrator's `.planning/milestone.lock`. The one exception is deviation 1.

## Next Phase Readiness

30-05 can record the gate delta and check the order of the L46, wall and seam commits. Phase 31 widens `Part` in one line of `parts.py`; Phase 33's shaft routes call `_serve_model` as its second caller. When Phase 32 first imports `shaft_model` in `model.py`, C3 needs its `ignore_imports` line in the same commit (30-03 handoff).

## Self-Check: PASSED

Files found: `src/spur/pool.py`, `records.py`, `app.py`, `model.py`, `tests/test_api.py`, `bench/RESULTS.md`, four `30-04-*.log` files. Commits found in HEAD: `e0e9225`, `ca60285`, `92fc0d4`.

---
*Phase: 30-scope-seam-and-gear-safety-guard*
*Completed: 2026-10-23*
