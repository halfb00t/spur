---
phase: 32-the-shaft-solid
plan: 04
subsystem: shaft-solid
tags: [din5480, model, doorway, part-union, import-linter, stl, step, pool, l06, l17, l18, l24]

requires:
  - phase: 32-the-shaft-solid
    provides: "32-03 shaft_model.build_shaft, tests/shaft_oracle.py closed form, heavy test_shaft_model; 32-02 ShaftParams.slug()"
provides:
  - "model._build dispatches a ShaftParams to shaft_model.build_shaft as its first statement, under the one _LOCK, the one _build_cached and the one _write_export"
  - "Part = GearParams | ShaftParams; _build_checked and _write_export take Part"
  - "the doorway contract's one ignored edge, spur.model -> spur.shaft_model (Contracts: 10 kept, 0 broken.)"
  - "STL (preview, fine) and STEP of a shaft through model and through a real BuildPool worker, pool.py untouched"
  - "MESH_PREVIEW_REL 6e-3, MESH_FINE_REL 1e-3, MESH_VERTEX_TOL 1e-4, each with its measured worst"
  - "three seen-red rows in bench/RESULTS.md and the commit slice re-priced at 14.94 s"
affects: [32-05, 32-06, 33]

tech-stack:
  added: []
  patterns:
    - "one dispatch inside _build keeps one lock, one solid cache and one export path for both parts"
    - "a mesh bar is set from the measured worst on the rows the test uses, with both quality rows recorded beside the constant"

key-files:
  created:
    - .planning/phases/32-the-shaft-solid/investigation/32-04-mesh.py
    - .planning/phases/32-the-shaft-solid/investigation/32-04-mesh.log
    - .planning/phases/32-the-shaft-solid/investigation/32-04-verify-fast.log
    - .planning/phases/32-the-shaft-solid/investigation/32-04-red-no-ignore.log
    - .planning/phases/32-the-shaft-solid/investigation/32-04-red-no-dispatch.log
    - .planning/phases/32-the-shaft-solid/investigation/32-04-red-cycle.log
    - docs/tech_debt/resolved/2026-10-23-parts-one-line-widening-claim-is-false.md
  modified:
    - src/spur/model.py
    - src/spur/parts.py
    - src/spur/records.py
    - pyproject.toml
    - tests/test_shaft_model.py
    - tests/test_pool.py
    - tests/test_records.py
    - tests/test_seam.py
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "MESH_PREVIEW_REL = 6e-3 (human decision, 2026-10-27, Option A): the measured preview worst on W 14x2x6 is -3.691e-3, which is 0.615 of 6e-3 and meets the plan's two-thirds rule; the plan's 5e-3 would have put it at 0.74"
  - "MESH_FINE_REL 1e-3 and MESH_VERTEX_TOL 1e-4 kept: fine worst -4.920e-4 (0.49 of the bar), end-face radius gap worst 4.726e-7 mm (212x under the bar)"
  - "No further file named heavy: the re-priced slice reads 14.94 s at worst against the 20.0 s rule; test_shaft_model stays heavy as 32-03 decided"
  - "Quality-typed test parameters instead of a type: ignore, so make typecheck stays clean with no new suppression"

requirements-completed: []  # REQ-shaft-solid is not fully delivered by this plan alone: the plan delivers the STL and STEP path through model and a pool worker, but 32-05 (cache and memory measurement) and 32-06 remain in the phase, and no route exists until Phase 33.

duration: about 45 min
completed: 2026-10-27
status: complete
actuals:
  tokens: 10500   # chars/4 over the added lines of the four task commits (42,209 chars: src, tests, pyproject, docs, bench and the investigation logs and script)
  tasks: 3
  commits: 4
plan_head_before: b3aebc3fa4b2531899c183379a078b65e8d32b21
plan_head_after: c7253455a9caabbdb5ea8327ed87069b8c63ffeb
---

# Phase 32 Plan 04: The shaft through the one kernel doorway Summary

`model.build` and `model.export` take a `ShaftParams` through `shaft_model.build_shaft` under the one lock, the one solid cache and the one export path the gear uses, so a shaft now exports a closed STL carrying its end chamfer and a STEP solid, through `model` and through a real BuildPool worker with `pool.py` untouched, `Part` widened, the doorway contract holding with its one ignored edge, and the Phase 30 widening debt item closed.

## What shipped

Commits (single repo, hooks on, no `--no-verify`):

1. `4018de8` feat(model): build and export a shaft through the one kernel doorway (Part widens) (Task 1, tracer)
2. `ee8a543` docs(debt): record the commit that widened Part (Task 1, the sha follow-up)
3. `7a657cd` test(shaft): a real worker, the shared cache, the record and the no-cycle belt (Task 2)
4. `c725345` docs(bench): the shaft doorway's guards seen red once (32-04) (Task 3)

**The commit that widened `Part` is `4018de8`**; `ee8a543` wrote that sha into the debt item's `Resolved in:` line and its INDEX row. That one commit holds the dispatch, the union, the contract edge, the debt move and the mesh tests, as the CONTEXT lock requires.

The path is `ShaftParams -> model.export -> _build_cached -> _build -> shaft_model.build_shaft -> _write_export`. The gear's `_build` lines and its `_build_checked` wording are unchanged; `model.py` gained one import line, one `isinstance` dispatch, a docstring sentence and `Part` on two signatures. `app.py`, `cli.py`, `pool.py`, `calc.py` and `params.py` are byte-identical to `b4cfd71` (`git diff --exit-code` exits 0).

### The mesh bars with their measured worsts

From `investigation/32-04-mesh.py` (log `32-04-mesh.log`), run through `model.export`, the path the shipped tests use.

| Row | Quality | Triangles | Volume rel | End-face radius gap (mm) |
|---|---|---|---|---|
| default | preview | 4188 | -1.930e-03 | 4.726e-07 |
| default | fine | 5662 | -3.092e-04 | 4.715e-07 |
| W 14x2x6 | preview | 1728 | -3.691e-03 | 1.907e-07 |
| W 14x2x6 | fine | 7598 | -4.920e-04 | 1.907e-07 |

| Constant | Value | Worst measured | Ratio of worst to bar |
|---|---|---|---|
| `MESH_PREVIEW_REL` | 6e-3 | -3.691e-3 (W 14x2x6 preview) | 0.615 |
| `MESH_FINE_REL` | 1e-3 | -4.920e-4 (W 14x2x6 fine) | 0.49 |
| `MESH_VERTEX_TOL` | 1e-4 mm | 4.726e-7 mm (default preview) | 0.0047 |

### Re-pricing outcome

Three warm `make verify.fast` after Task 2 (`investigation/32-04-verify-fast.log`): 14.94, 14.86 and 14.62 s (1-minute load 16.4, 23.2, 23.9; 2194 passed). The slowest is at or under the 20.0 s rule, so no further file was named heavy and neither the Makefile nor `tests/test_hooks.py` changed. `tests/test_shaft_model.py` was already ignored by the slice after 32-03; its nine new collected cases only add to a file that is out of the slice. The slice gained two tests (2192 to 2194: one in `test_records.py`, one in `test_seam.py`).

## Verification

- `make verify`: `======================= 2638 passed in 358.81s (0:05:58) =======================`, exit 0 (2626 at the 32-03 close). `Contracts: 10 kept, 0 broken.`, `gear.unchanged: ... byte-equal to v0.6`, coverage 98.22 % (floor 96.0).
- Task 1: `pytest -n 8 tests/test_shaft_model.py tests/test_seam.py tests/test_records.py` 57 passed; `make lint typecheck no-fake-done gear.unchanged` green; the STEP probe prints `b'ISO-10303-21;' True`; `git diff --exit-code b4cfd71 -- pool.py app.py cli.py calc.py params.py` exits 0.
- Task 2: `pytest -n0 tests/test_pool.py -k builds_and_exports_a_shaft` 1 passed; `-n 8` over test_shaft_model, test_records and test_seam 62 passed; `tests/test_seam.py` 7 passed; mypy and `ruff check tests` clean.
- Task 3: each red log holds its failure (below); `grep -c '^| 32-04 |' bench/RESULTS.md` is 3; `make lint-imports` reads `10 kept` after the last revert; the last `bench/RESULTS.md` commit changes 13 lines and deletes 0; `git status --porcelain -- src tests pyproject.toml` is empty.
- Tracer gate: the Task 1 verify was re-run end to end after its commit before Task 2 began.

## Seen red once

Three breaks, each with `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared before and after, reverted with `git checkout -- <file>`, `git status --porcelain -- src tests pyproject.toml` empty after each. Rows are in `bench/RESULTS.md` under `### Seen red once (Phase 32)`.

| Break | Result | Log |
|---|---|---|
| `ignore_imports` line removed from pyproject.toml | `Contracts: 9 kept, 1 broken.`, chain `spur.cli -> spur.model (l.102)`, `spur.model -> spur.shaft_model (l.33)` | `32-04-red-no-ignore.log` |
| `isinstance(p, ShaftParams)` dispatch removed from `_build` | 2 failed (both doorway rows): `BuildError: Geometry kernel failed (AttributeError); try smaller fillets or chamfers.`, the shaft reaching the gear's pipeline and reading `p.pressure_angle` | `32-04-red-no-dispatch.log` |
| function-local `from . import model` in `shaft_model._polar` | 1 failed, 6 passed: `test_the_shaft_solid_never_imports_the_gear_doorway` only | `32-04-red-cycle.log` |

`32-04-red-no-ignore.log` opens with the venv's `pip install -e` output: touching `pyproject.toml` invalidates the Makefile's venv stamp, so `make lint-imports` reinstalled before it linted. The contract result follows it and is the first failure.

## Deviations from Plan

### Human decision

**1. [Decision, checkpoint] `MESH_PREVIEW_REL` is 6e-3, not the plan's 5e-3**
- **Found during:** Task 1, measuring before setting the bars (the plan's "each bar stays if the measured worst is at most two thirds of it, otherwise stop and ask").
- **Issue:** W 14x2x6 preview reads -3.691e-3, which is 0.74 of 5e-3 and fails the two-thirds rule. The plan took its preview bar from 32-RESEARCH's -3.3e-3 "z6 m2" row, but that row used `reference_d` 14.2, not the plan's 14.0, so the measured worst moved.
- **Resolution:** The human picked Option A on 2026-10-27: `MESH_PREVIEW_REL = 6e-3` (0.615 of the bar, meeting the rule). `MESH_FINE_REL` (1e-3) and `MESH_VERTEX_TOL` (1e-4) stay, since their worsts are 0.49 and 0.0047 of the bar. The constant's comment records both W 14x2x6 rows and the `reference_d` 14.2 versus 14.0 difference.
- **Files modified:** `tests/test_shaft_model.py`
- **Commit:** 4018de8

### Auto-fixed Issues

**2. [Rule 3 - Blocking] A `Quality` annotation instead of a `type: ignore`**
- **Found during:** Task 1, `make typecheck`.
- **Issue:** the parametrized quality came from a plain `dict[str, float]`, which `model.export` (`Literal["preview", "fine"]`) rejects under `mypy --strict`.
- **Fix:** `MESH_BARS` is `dict[Quality, float]` and the parametrized test takes `quality: Quality`, so no suppression was added (the plan says none).
- **Files modified:** `tests/test_shaft_model.py`
- **Commit:** 4018de8

**3. [Rule 3 - Blocking] mypy rejected `GearParams() != ShaftParams()` as a non-overlapping comparison**
- **Found during:** Task 2, `mypy tests/test_shaft_model.py`.
- **Fix:** the two models are held as `tuple[object, object]` for the inequality assertion; the cache identity checks use `is` on the built solids, which is also what the plan's "each rebuilt call returning the cached object" asks.
- **Files modified:** `tests/test_shaft_model.py`
- **Commit:** 7a657cd

**4. [Rule 1 - Wording] The mesh constant's comment first said "a chamfer's width (1.0 mm)"**
- **Issue:** the applied chamfer is 1.0 mm on both mesh rows (read from `derive_shaft`), so the comment now says so for those rows instead of generalising.
- **Commit:** 4018de8

None of the plan's Task 3 conditionals fired: the heavy-file change was not needed, so `Makefile` and `tests/test_hooks.py` are untouched.

## Debt and ideas

One debt item closed: `docs/tech_debt/resolved/2026-10-23-parts-one-line-widening-claim-is-false.md` (moved from `active/`, `Status: resolved`, `Resolved in: 4018de8 ...`, its INDEX row moved to the Resolved table). Nothing new was filed under `docs/tech_debt/active/` or `docs/ideas/`. The existing nice item `2026-10-27-shaft-contention-row.md` (32-03) and 32-05's cache measurement remain open as planned.

## Flagged assumption carried forward

The edge probe for REQ-shaft-solid (unclassified, unresolved) is not resolved here: the mesh rows and the cache-sharing row are added; whether a shaft entry in the 4-entry solid cache retains more memory than a 199-tooth gear's is 32-05's measurement (the test docstring says so).

## Known Stubs

None.

## Threat Flags

None. No new endpoint, auth path or file access: the export still writes inside the existing `TemporaryDirectory`, and `ShaftParams.slug()` (the temp stem) is covered by the 32-02 test. The serving process still never reaches the kernel: only `spur.model -> spur.shaft_model` is ignored, and R1 shows every other path breaks the contract.

## Self-Check: PASSED
