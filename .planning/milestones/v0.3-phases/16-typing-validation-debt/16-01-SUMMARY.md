---
phase: 16-typing-validation-debt
plan: 01
subsystem: typing
tags: [mypy, cadquery, isinstance, BuildError, no-fake-done, tech-debt]

requires:
  - phase: 10-tooth-tip-chamfer
    provides: the fifth suppression (_chamfer_tips) and the warn_return_any assignment shape
provides:
  - "_NOT_A_BODY, _body and _shape_of in src/spur/model.py; zero mypy suppressions under src/spur"
  - "make no-fake-done refuses a new mypy suppression under src/spur/"
  - "mypy override scoped to OCP.* alone"
  - "2026-09-21-cadquery-shape-typing.md retired with its sha"
affects: [16-02, 16-03]

actuals:
  tokens: 5886
  tasks: 3
  commits: 2
plan_head_before: fcbad1c8e2244d7bd1cd412d2ea34399d18d81dd
plan_head_after: c11213eb00f133f385728812bfdda5f35cdff751

tech-stack:
  added: []
  patterns:
    - "Narrow a vendor type with an isinstance helper that raises BuildError, never a cast"

key-files:
  created: []
  modified:
    - Makefile
    - src/spur/model.py
    - tests/test_model.py
    - pyproject.toml
    - docs/architecture/solid-model/implementation.md
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/resolved/2026-09-21-cadquery-shape-typing.md
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md

key-decisions:
  - "Two isinstance helpers raising BuildError, never a cast: _body at the three fillet/chamfer sites, _shape_of at the two .val() sites; _gear_blank stays -> cq.Shape"
  - "D-04 gate passed: mypy output byte-identical with and without cadquery.* in the override, so it was dropped"
  - "make no-fake-done pins zero suppressions under src/spur/ only; tests/ keeps its two deliberate ones"

requirements-completed: [REQ-model-py-no-type-ignore]

coverage:
  - id: D1
    description: "src/spur/model.py carries no mypy suppression: five sites narrowed through _body and _shape_of, each raising BuildError with the full D-03 message"
    requirement: "REQ-model-py-no-type-ignore"
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_a_non_body_shape_in_the_build_pipeline_is_named_as_a_modelling_defect"
        status: pass
      - kind: unit
        ref: "tests/test_model.py#test_a_workplane_value_that_is_not_a_shape_is_named_as_a_modelling_defect"
        status: pass
      - kind: other
        ref: "rm -rf .mypy_cache && make typecheck"
        status: pass
    human_judgment: false
  - id: D2
    description: "make no-fake-done refuses a mypy suppression under src/spur/, seen red against the five lines at 085e5a6 and green after"
    requirement: "REQ-model-py-no-type-ignore"
    verification:
      - kind: other
        ref: "make no-fake-done"
        status: pass
    human_judgment: false
  - id: D3
    description: "No geometry change: five-site gear tuple and the 44-record replay unchanged, 18 untouched functions AST-identical to 085e5a6"
    requirement: "REQ-model-py-no-type-ignore"
    verification:
      - kind: integration
        ref: "make test PYTEST_ARGS='tests/test_model.py tests/regression -q --no-cov'"
        status: pass
    human_judgment: false
  - id: D4
    description: "Debt retired with its sha; REQ, SC1 and SC2 sentences corrected to say what was built"
    requirement: "REQ-model-py-no-type-ignore"
    verification: []
    human_judgment: true
    rationale: "Prose accuracy of the corrected requirement and roadmap sentences needs a human read; the plan's checks only assert key phrases"

duration: 7min
completed: 2026-10-04
status: complete
---

# Phase 16 Plan 01: Shape-typing narrowing Summary

**Five mypy suppressions in `model.py` replaced by two `isinstance` helpers that raise `BuildError`, a `no-fake-done` pin that refuses a sixth, and the mypy override scoped to OCP, with no geometry change.**

## Performance

- **Duration:** 7 min (wall clock, 17:26:30Z to 17:33:36Z; includes three full-suite runs)
- **Started:** 2026-10-04T17:26:30Z
- **Completed:** 2026-10-04T17:33:36Z
- **Tasks:** 3
- **Files modified:** 14 (eight in the code commit, two in the sha follow-up, REQUIREMENTS.md, ROADMAP.md, STATE.md, state.json in the closing commit)

## Accomplishments

- `_NOT_A_BODY`, `_body(shape: cq.Shape) -> cq.Solid | cq.Compound` and `_shape_of(wp: cq.Workplane) -> cq.Shape` stand where the five suppressions stood (lines 213, 237, 239, 411, 420 at 085e5a6). `_body` is called three times, `_shape_of` twice. `git grep -nE 'type: ignore' -- 'src/spur/*.py'` prints nothing.
- `make no-fake-done` gained a second `git grep` block scoped to `src/spur/*.py`; `tests/test_calc.py` and `tests/test_cli.py` keep their deliberate suppressions.
- `[[tool.mypy.overrides]]` is `module = ["OCP.*"]`; mypy's output is byte-identical before and after.
- Two refusal tests (927 -> 929 collected) assert the whole D-03 message with `==`, naming `Face` and `Vector`.
- The debt retired to `resolved/` with a `## Resolution`, the INDEX row moved, and the implementation note's bullet rewritten.
- REQ-model-py-no-type-ignore and ROADMAP Phase 16 SC1 and SC2 now say what was built and why a cast at `.val()` reaches two of five.

## Task Commits

1. **Task 1: Tracer** - not committed on its own: the plan's D-07 puts the gate, helpers, five sites and tests in the Task 2 code commit.
2. **Task 2: The record in the same commit** - `4f7e8fe` (refactor) carrying Makefile, model.py, test_model.py, pyproject.toml, implementation.md, INDEX.md and both sides of the debt `git mv`
3. **Task 3: The sha recorded** - `c11213e` (docs); the REQ/ROADMAP edits ride the closing commit below

**Plan metadata:** the closing `docs(16-01)` commit, which carries this SUMMARY, REQUIREMENTS.md, ROADMAP.md, STATE.md and state.json.

## Evidence

- **Five-site gear, before and after:** `build(GearParams(tip_chamfer=0.5))` reads `('Solid', True, 4446.54642, 210, 604)` for (type, isValid, volume at 6 dp, faces, edges), both before any edit and after all five sites changed.
- **RED `make no-fake-done`** (before model.py was touched; make exit 2 from the recipe's `exit 1`):

```
src/spur/model.py:213:        solid = solid.fillet(fillet, _groove_floor_edges(solid, (r_in, r_out), floor_z))  # type: ignore[attr-defined]
src/spur/model.py:237:    solid = solid.cut(hole.val())  # type: ignore[arg-type]  # .val() is typed as a 4-way union
src/spur/model.py:239:        solid = solid.chamfer(  # type: ignore[attr-defined]  # see _cut_face_recesses
src/spur/model.py:411:    solid = solid.chamfer(  # type: ignore[attr-defined]  # see _cut_face_recesses
src/spur/model.py:420:            .circle(r_out).circle(r_in).extrude(height).val())  # type: ignore[return-value]
make: a mypy suppression in src/spur above. Narrow the type, or file it in docs/tech_debt/.
```

  GREEN after the edit: `make no-fake-done` exits 0.
- **D-04 gate:** `rm -rf .mypy_cache && .venv/bin/python -m mypy src tests docker bench scripts` exited 0 before and after the override edit; both captures end `Success: no issues found in 37 source files`; `cmp` reported them identical. `make typecheck` afterwards refreshed the venv stamp (pip reinstalled spur, then the Success line).
- **Hook pytest line, code commit `4f7e8fe`:** the hook's `make verify` printed `Passed`; its pytest output is not shown by pre-commit on success, so the line comes from a `make verify` run on that tree immediately after: `929 passed in 60.66s (0:01:00)`, total coverage 97.24 % against the 96 floor. The same hook passed on `c11213e`.
- **AST check:** 18 named untouched functions are AST-identical to 085e5a6; helper signatures as specified; no `cast`, `Any` or `TypeIs` in `model.py`.
- **Fixture and neighbours:** `tests/regression/pre_v0_2.json`, `tests/test_calc.py`, `tests/test_cli.py` and `requirements.txt` are byte-identical to 085e5a6; `tests/test_model.py tests/regression` read `289 passed`.
- **Commit contents:** `4f7e8fe` carries exactly the eight plan paths; `c11213e` carries the debt file and INDEX only. `Resolved in:` reads `4f7e8fe`, equal to the INDEX cell.

### REQUIREMENTS and ROADMAP diffs

REQUIREMENTS.md, REQ-model-py-no-type-ignore: the line list `212, 236, 238, 410, 419` became `213, 237, 239, 411, 420` ("five at the phase's start"); "narrowing the pipeline's annotations ... and casting **once** at the `.val()` boundary" became two `isinstance` helpers raising `BuildError`, `_body` at the three `fillet`/`chamfer` sites and `_shape_of` at the two `.val()` sites, with the reason a cast reaches two of five; the acceptance now says mypy's `warn_unused_ignores` refuses a stale suppression, `RUF100` stays on and governs `noqa`, `make no-fake-done` refuses a new one under `src/spur/`, and "annotations only" became "no geometry change -- two checks that cannot fire on a valid build".

ROADMAP.md, Phase 16: SC1 carries the same line list, the two helpers, the `Shape.cut` reason and "pinned by `make no-fake-done`"; SC2 carries the `warn_unused_ignores`/`RUF100` sentence and "no geometry change". The `**Plans:**` list is untouched, edited only by a scoped Edit inside `### Phase 16:`; `roadmap milestone-scope` read 4 phases before and after, and one Roadmap Evolution line was added (`state.add-roadmap-evolution`).

## Files Created/Modified

- `src/spur/model.py` - `_NOT_A_BODY`, `_body`, `_shape_of`; five call sites; the two old comments and five suppressions removed
- `tests/test_model.py` - the two refusal tests and two imports
- `Makefile` - second `no-fake-done` block and its comment
- `pyproject.toml` - override scoped to `OCP.*` with a corrected comment
- `docs/architecture/solid-model/implementation.md` - the "load-bearing" bullet rewritten
- `docs/tech_debt/resolved/2026-09-21-cadquery-shape-typing.md`, `docs/tech_debt/INDEX.md` - debt retired, sha recorded
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` - sentences corrected

## Decisions Made

- `isinstance` helpers that raise `BuildError`, never a cast (D-01); `_gear_blank` keeps `-> cq.Shape` (D-02, 16-RESEARCH Pitfall 1).
- `cadquery.*` leaves the mypy override after D-04's byte-identical gate passed.
- The pin is scoped to `src/spur/` (D-05).

## Deviations from Plan

None - plan executed exactly as written.

One procedural note, not a deviation: the first `git add` for the code commit listed the old `active/` path, which no longer exists after `git mv`; git rejected the whole command with nothing staged by it, and it was re-run without that path. The rename was already staged by `git mv`.

## Tangent for the human: `_cell_cutters`

`_cell_cutters` raises `TypeError` on a non-Solid prototype and was left alone (D-16: no cut changes). `_build_checked` would relabel that `TypeError` with the catch-all's "try smaller fillets or chamfers" remedy, which is the D-03 problem in a second place. Not filed as debt: the plan asked only for a note. The human decides whether it deserves a file under `docs/tech_debt/active/`.

## Issues Encountered

None.

## Known Stubs

None.

## Threat Flags

None. The new `BuildError` text carries only a vendor class name (T-16-04) and crosses the existing 422 / exit-1 mapping unchanged.

## Next Phase Readiness

Ready for 16-02 (Phase 7/8 Nyquist pass). The tree is clean apart from the session-scoped `.planning/milestone.lock`.

Filed no ideas or debt items in this plan; the one debt item it touched (`2026-09-21-cadquery-shape-typing.md`) was retired.

## Self-Check: PASSED

Created and modified files exist; commits 4f7e8fe and c11213e are in the log.
