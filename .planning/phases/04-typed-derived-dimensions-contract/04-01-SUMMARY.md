---
phase: 04-typed-derived-dimensions-contract
plan: 01
subsystem: api-contract
tags: [pydantic, fastapi, openapi, cli, calc]

# Dependency graph
requires:
  - phase: 03-structured-logging-at-the-composition-boundary
    provides: the build_started/build_failed/export_served/queue_refused/worker_replaced
      logging vocabulary that app.py already calls; this plan touches app.py's info()
      only, never its logging
provides:
  - "`spur.calc.DerivedDimensions`, a frozen pydantic response model with 19 always-present fields"
  - "`spur.calc.derive(p, mate_teeth=None, mate_shift=0.0) -> DerivedDimensions`, the single construction site"
  - "`/api/info`'s FastAPI-inferred OpenAPI component, `#/components/schemas/DerivedDimensions`"
  - "a D-13 CLI-equals-API equivalence test, a D-11 OpenAPI contract test, and a D-12 UI-key belt test"
affects: [04-02-typed-health-and-pool-contract, 04-03-any-explicit-ratchet-retired]

# Actuals (#2632)
actuals:
  tokens: 7741
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "One frozen pydantic model as the single construction site for a multi-front-end
      response document, with every field required (no `default=`) so OpenAPI's
      `required` list stays the always-present contract's own proof"
    - "r3() narrowed to `(float) -> float`, called once per value at model-construction
      time, rather than a dict comprehension over an already-built mapping"

key-files:
  created: []
  modified:
    - src/spur/calc.py
    - src/spur/app.py
    - src/spur/cli.py
    - tests/test_calc.py
    - tests/test_cli.py
    - tests/test_api.py
    - docs/architecture/gear-maths/tactics.md
    - docs/architecture/gear-maths/implementation.md
    - docs/architecture/gear-maths/strategy.md
    - docs/architecture/gear-maths/errors_and_logging.md
    - docs/architecture/http-api.md

key-decisions:
  - "DerivedDimensions declares every field with no default of any kind (Field(description=...) only) so a default can never make a key optional in OpenAPI, which would contradict D-01's always-present contract (RESEARCH.md Pitfall 2)."
  - "with_mate() is deleted outright rather than kept as a thin wrapper: derive() absorbs the mate computation so there is exactly one construction site (D-02, D-09)."
  - "r3() renamed rfil/rec_fil rounding: root_fillet() and recess_fillet() already round(..., 3) internally, so wrapping them in r3() again changes no value on the wire today, but keeps D-10's 'every length rounded once, at construction' rule true if either helper's internal rounding ever changes."
  - "cmd_info's `ns.mate_teeth or None` keeps --mate-teeth 0 meaning 'no mate', byte-identical to pre-phase behaviour, until Plan 04-03 range-checks the CLI flag like InfoQuery.mate_teeth already does (flagged assumption 2, human decision R-2)."

patterns-established:
  - "A shared response model with a docstring naming which three front ends print it (D-13's living rationale in one place, not re-derived at each call site)."

requirements-completed: [REQ-typed-derived-dimensions]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "DerivedDimensions is a frozen pydantic BaseModel with 19 fields, no field carrying a default; derive() is its single construction site and with_mate() no longer exists anywhere in src/ or tests/."
    requirement: REQ-typed-derived-dimensions
    verification:
      - kind: unit
        ref: "tests/test_calc.py::test_default_dimensions"
        status: pass
      - kind: unit
        ref: "tests/test_calc.py::test_a_derived_dimensions_result_cannot_be_changed"
        status: pass
      - kind: unit
        ref: "tests/test_calc.py::test_impossible_pairs_have_no_centre_distance"
        status: pass
      - kind: other
        ref: "git grep -n 'with_mate' -- src tests docs/architecture (expected: no output)"
        status: pass
    human_judgment: false
  - id: D2
    description: "/api/info and spur info print byte-identical documents for the no-mate, meshing-mate, and impossible-pair cases (D-13)."
    requirement: REQ-typed-derived-dimensions
    verification:
      - kind: integration
        ref: "tests/test_cli.py::test_cli_and_api_print_the_same_document"
        status: pass
    human_judgment: false
  - id: D3
    description: "/openapi.json's /api/info response points at #/components/schemas/DerivedDimensions, whose properties and required both equal the 19 field names, with unit: mm on lengths and no unit on span_teeth (D-11, info half)."
    requirement: REQ-typed-derived-dimensions
    verification:
      - kind: integration
        ref: "tests/test_api.py::test_openapi_documents_the_typed_contracts"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every key src/spur/static/app.js reads from the info document is a DerivedDimensions field, proven by a regex belt over the shipped file (D-12)."
    requirement: REQ-typed-derived-dimensions
    verification:
      - kind: integration
        ref: "tests/test_api.py::test_every_key_the_ui_reads_is_a_derived_dimensions_field"
        status: pass
    human_judgment: false
  - id: D5
    description: "No published number changed: spur info output is byte-identical before/after this plan for the with-mate and impossible-pair cases; the default case gains only the two new null keys."
    requirement: REQ-typed-derived-dimensions
    verification:
      - kind: manual_procedural
        ref: "diff of `spur info`, `spur info --teeth 21 --mate-teeth 40`, and the impossible-pair command, captured before Task 1's edits and re-captured after Task 1 (see 'Before/After Diffs' below)"
        status: pass
    human_judgment: false
  - id: D6
    description: "derive()'s per-call cost is measured before and after, and both figures are written into its docstring next to the module's 'fast enough for every keystroke' claim (CONTEXT.md discretion, CLAUDE.md's measure-don't-assume rule)."
    verification:
      - kind: manual_procedural
        ref: ".venv/bin/python -m timeit -s \"from spur.calc import derive; from spur.params import GearParams; p = GearParams()\" \"derive(p)\" (see 'Performance' below)"
        status: pass
    human_judgment: false
  - id: D7
    description: "The four gear-maths documents and the http-api.md /api/info row describe DerivedDimensions and derive()'s new signature; no document under docs/architecture/ names with_mate() or dict[str, Any] as the reports contract (D-15)."
    requirement: REQ-typed-derived-dimensions
    verification:
      - kind: other
        ref: "git grep -n 'with_mate' -- docs/architecture; grep -n 'dict\\[str, Any\\]' docs/architecture/gear-maths/tactics.md (both expected: no output); grep -n DerivedDimensions across the three edited docs (expected: all three present)"
        status: pass
    human_judgment: false

# Metrics
duration: ~45min
completed: 2026-09-24
status: complete
---

# Phase 4 Plan 1: Typed Derived-Dimensions Contract Summary

`derive()` now returns a frozen `DerivedDimensions` pydantic model — 19 always-present
fields, `null` where a value does not apply or cannot be computed honestly — built once
inside `derive()` itself; the old `dict[str, Any]` plus the post-hoc `with_mate()` patch
function are gone, and four tests (a frozen-result test, a CLI/API equivalence test, an
OpenAPI contract test, and a UI-key belt) hold the shape in place.

## Performance

- **Duration:** ~45min (approximate — session start wasn't captured at dispatch time;
  reconstructed from the scope of work, not measured to the minute)
- **Task commits:** `013900d` (20:01:46+06:00), `80506db` (20:04:41+06:00), `2f8b2da`
  (20:07:01+06:00)
- **Tasks:** 3 completed
- **Files modified:** 11 (0 created)

**`derive()`'s per-call cost** (`.venv/bin/python -m timeit -s "from spur.calc import
derive; from spur.params import GearParams; p = GearParams()" "derive(p)"`, best of 5,
default `GearParams`, arm64, Python 3.12.13, three consecutive runs after the change:
11.6 / 11.5 / 11.5 usec):

| | usec/call |
|---|---|
| Before (dict literal) | 9.19 |
| After (`DerivedDimensions(...)`, validated on construction) | 11.5 |

About +2.3 usec (~1.25x), well under the plan's 2x stop-and-surface bar and negligible
next to an HTTP round trip. Recorded verbatim in `derive()`'s own docstring next to the
module docstring's "fast enough to run on every keystroke" claim.

## Accomplishments
- `DerivedDimensions`, a frozen pydantic model with 19 fields and no defaults on any of
  them, declared immediately above `derive()` in `calc.py` (D-01, D-03, D-09).
- `derive(p, mate_teeth=None, mate_shift=0.0) -> DerivedDimensions` is now the single
  construction site for the mate fields and the cannot-mesh warning; `with_mate()` no
  longer exists in `src/` or `tests/` (D-02).
- `/api/info`'s `info()` is annotated `-> DerivedDimensions` and FastAPI infers
  `#/components/schemas/DerivedDimensions` from that alone; `spur info` prints the same
  model's `model_dump_json(indent=2)` — one serialiser for both front ends (D-11, D-13).
- Four new tests hold the contract: `test_a_derived_dimensions_result_cannot_be_changed`
  (frozen), `test_cli_and_api_print_the_same_document` (D-13),
  `test_openapi_documents_the_typed_contracts` (D-11, info half),
  `test_every_key_the_ui_reads_is_a_derived_dimensions_field` (D-12) — the latter two
  each proven to fail against a deliberate break, then reverted.
- Five `docs/architecture/` documents rewritten to describe `DerivedDimensions` instead
  of the old `dict[str, Any]` contract and the deleted `with_mate()` (D-15).

## Task Commits

Each task was committed atomically:

1. **Task 1: End to end — one typed document built by `derive()`, printed identically by
   `/api/info` and `spur info`** — `013900d` (feat)
2. **Task 2: Prove the contract on the wire and against the UI — `/openapi.json` (D-11)
   and the `app.js` belt (D-12)** — `80506db` (test)
3. **Task 3: Make the contract docs true — the gear-maths documents and the
   `/api/info` row (D-15)** — `2f8b2da` (docs)

**Plan metadata:** committed alongside this file (see below).

## Files Created/Modified
- `src/spur/calc.py` — `DerivedDimensions` model + rewritten `derive()`; `with_mate()`
  deleted
- `src/spur/app.py` — `info()` annotated `-> DerivedDimensions`, returns `derive()`
  directly
- `src/spur/cli.py` — `cmd_info` prints `model_dump_json(indent=2)`; `cmd_export` reads
  `.warnings`; unused `json` import dropped
- `tests/test_calc.py` — dict-key reads moved to attributes; two new empty-mate asserts;
  `test_a_derived_dimensions_result_cannot_be_changed` added;
  `test_impossible_pairs_have_no_centre_distance` calls `derive(p, mate_teeth=mate)`
  directly
- `tests/test_cli.py` — `test_cli_and_api_print_the_same_document` added (D-13)
- `tests/test_api.py` — `test_openapi_documents_the_typed_contracts` (D-11) and
  `test_every_key_the_ui_reads_is_a_derived_dimensions_field` (D-12) added; pre-existing
  `test_info_with_mate` renamed to `test_info_reports_the_mate` (deviation, see below)
- `docs/architecture/gear-maths/tactics.md`, `implementation.md`, `strategy.md`,
  `errors_and_logging.md`, `docs/architecture/http-api.md` — the old dict/`with_mate()`
  contract descriptions replaced with `DerivedDimensions`'s

## Decisions Made

See `key-decisions` in the frontmatter. The most consequential: no `DerivedDimensions`
field carries a default, which is what makes the OpenAPI `required` list a live proof of
the always-present contract rather than a claim nobody checks (D-01, Pitfall 2).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking issue] Renamed a pre-existing test whose name collided with the
plan's own literal `with_mate` grep**
- **Found during:** Task 1's mandatory `<verify>` gate
  (`! git grep -n 'with_mate' -- src tests`)
- **Issue:** `tests/test_api.py` already contained `test_info_with_mate()`, a test
  unrelated to the deleted `with_mate()` function — its name is just the English phrase
  "info with mate" — but it contains the literal substring `with_mate`, so the plan's
  own verification command (checking that the deleted function's name is gone) matched
  it and failed with exit 1.
- **Fix:** Renamed `test_info_with_mate` to `test_info_reports_the_mate`. No behaviour
  change; the test body is untouched.
- **Files modified:** `tests/test_api.py`
- **Verification:** `(! git grep -n 'with_mate' -- src tests)` now exits 0; the renamed
  test still passes.
- **Committed in:** `013900d` (part of Task 1's commit, since Task 1's own `<verify>`
  step required it before proceeding)

---

**Total deviations:** 1 auto-fixed (Rule 3).
**Impact on plan:** None on behaviour or scope — a one-line test rename to satisfy a
verification command the plan wrote before this coincidental substring collision
existed. Not filed as tech debt: it is fully resolved, not deferred.

**Also consciously not touched (noted, not fixed):** `docs/architecture/gear-maths/
implementation.md`'s header line ("`src/spur/calc.py` — 270 lines, no classes but
`Profile`") is now stale — the file is 343 lines and has two classes
(`Profile` and `DerivedDimensions`). The plan's Task 3 action list does not mention this
line, and it is not part of the reports-contract description D-15 targets (it describes
file structure, not the dict-vs-model contract), so it was left byte-identical per the
plan's own instruction ("every other sentence stays byte-identical"). Flagging here
rather than silently drifting further out of date.

## Issues Encountered

None beyond the deviation above.

## User Setup Required

None — no external service configuration required.

## Before/After Diffs (Task 1, Step 8)

Captured with `.venv/bin/spur info`, `.venv/bin/spur info --teeth 21 --mate-teeth 40`,
and `.venv/bin/spur info --teeth 6 --pressure-angle 14.5 --profile-shift -0.6 --bore-d 0
--bore-flat 0 --bore-chamfer 0 --recess-sides none --mate-teeth 40`, before Task 1's
edits and again after:

- **With-mate case:** byte-identical (`diff` empty).
- **Impossible-pair case:** byte-identical (`diff` empty) — including the "cannot mesh"
  warning's wording and position (after the undercut warning, matching the pre-phase
  append order `with_mate()` used).
- **Default case:** the only difference is the trailing comma added to the `warnings`
  line plus two new lines, `"mate_teeth": null` and `"centre_distance": null`:

  ```diff
  18c18,20
  <   "warnings": []
  ---
  >   "warnings": [],
  >   "mate_teeth": null,
  >   "centre_distance": null
  ```

## Next Phase Readiness

Plan 04-02 (typed health/pool contract) and Plan 04-03 (`disallow_any_explicit` on,
`spur info --mate-teeth` range-checked) both depend on `DerivedDimensions` existing
exactly as declared here — confirmed present with all 19 fields, no defaults, frozen.
`REQ-typed-derived-dimensions` is not yet complete: it also requires
`disallow_any_explicit` on and L14's ratchet retired, both Plan 04-03's scope. No
blockers.

---
*Phase: 04-typed-derived-dimensions-contract*
*Completed: 2026-09-24*

## Self-Check: PASSED

All 11 created/modified files found on disk; all 3 task commits (`013900d`, `80506db`,
`2f8b2da`) found in `git log --oneline --all`.
