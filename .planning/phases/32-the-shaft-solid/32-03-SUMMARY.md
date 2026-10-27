---
phase: 32-the-shaft-solid
plan: 03
subsystem: shaft-solid
tags: [din5480, cadquery, solid, closed-form, oracle, guards, kernel-hang, l08, l26]

requires:
  - phase: 32-the-shaft-solid
    provides: "32-02 derive_shaft().end_chamfer_effective (the applied chamfer), ShaftParams.slug()"
provides:
  - "din5480.flank_half_angle(m, z, xm, r), the one flank angle the solid and its oracle compare"
  - "shaft_model.build_shaft(p) -> cq.Solid: one outline extruded, the shank fused, the chamfer cone intersected, no cleaning step"
  - "tests/shaft_oracle.py: tooth_half_angle, profile_area_within, shaft_volume (stdlib only)"
  - "_guard_cone_start (the 1e-9..1e-4 mm band around the root circle) and _guard_volume (the volume bracket and z extent), both BuildErrors naming a modelling defect"
  - "tests/test_shaft_model.py: 32 kernel tests against the closed form; test_shaft_model is a heavy file"
  - "four measured bars and seven seen-red rows in bench/RESULTS.md"
affects: [32-04, 32-05, 32-06, 33]

tech-stack:
  added: []
  patterns:
    - "every test that builds compares solid.Volume() with a kernel-free closed form, never isValid() alone"
    - "a guard goes red once against a deliberate break, and the first failure line is logged and tabled"
    - "a measurement bar is the smallest step at least 10x the worst reading on the file's own rows, recorded beside the constant and in bench/RESULTS.md"

key-files:
  created:
    - tests/test_shaft_model.py
    - .planning/phases/32-the-shaft-solid/investigation/32-03-tolerances.py
    - .planning/phases/32-the-shaft-solid/investigation/32-03-tolerances.log
    - .planning/phases/32-the-shaft-solid/investigation/32-03-verify-fast.log
    - .planning/phases/32-the-shaft-solid/investigation/32-03-red-clean.log
    - .planning/phases/32-the-shaft-solid/investigation/32-03-red-no-band.log
    - .planning/phases/32-the-shaft-solid/investigation/32-03-red-no-bracket.log
    - .planning/phases/32-the-shaft-solid/investigation/32-03-red-no-wrap.log
    - .planning/phases/32-the-shaft-solid/investigation/32-03-red-no-tooth-cap.log
    - .planning/phases/32-the-shaft-solid/investigation/32-03-red-round.log
    - .planning/phases/32-the-shaft-solid/investigation/32-03-red-oracle.log
    - docs/tech_debt/active/2026-10-27-pre-commit-hook-name-and-l36-still-say-five-heavy-files.md
  modified:
    - src/spur/din5480.py
    - src/spur/shaft_model.py
    - tests/shaft_oracle.py
    - tests/test_din5480.py
    - tests/test_hooks.py
    - Makefile
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "Fuse before intersect, no cleaning step, no glue, no Solid.chamfer, kept as 32-RESEARCH Pattern 2 locks them; each reason is in the build_shaft docstring with its log"
  - "Bars set from this file's own worst rows: FLANK_ANGLE_ABS 1e-14 rad, VOLUME_REL 1e-4, READBACK_TOL 1e-6 mm, FLANK_BAR_PER_MODULE 5e-4, VOLUME_BRACKET_SLACK 1e-4"
  - "tests/test_shaft_model.py is named heavy: the slowest of three warm make verify.fast readings was 20.97 s, above the 20.0 s rule"
  - "Flank deviation is sampled at 201 positions per spline edge, not 21: the sparse sample read 5x low"

requirements-completed: []  # REQ-shaft-solid is not fully delivered here: the solid is built and proved, but the STL and STEP download path (model dispatch, export) arrives in 32-04 onward

duration: about 30 min
completed: 2026-10-27
status: complete
actuals:
  tokens: 22700   # chars/4 over the added lines of src, tests, Makefile, bench and docs (40,194 chars) plus the 7 red logs, 3 measurement logs and the measurement script
  tasks: 3
  commits: 5
plan_head_before: be554100edae6d69f55544f3c268f6d4776da405
plan_head_after: 0fe931290e90d0f1e09da5b4f5b1c6c22f1754a9
---

# Phase 32 Plan 03: The shaft solid, proved against a stdlib closed form Summary

`shaft_model.build_shaft` builds the default shaft as one valid solid whose volume agrees with a kernel-free Simpson closed form to 4e-9, and every shank regime, chamfer cap and tooth count from 6 to 82 builds within bars set from this file's own measurements; the kernel's two silent failures (a cone start on the root circle, a cone that eats the core) are `BuildError`s, each seen red once.

## What shipped

Commits (single repo, hooks on, no `--no-verify`):

1. `47c4782` feat(32-03): the shaft solid, proved against a stdlib closed form (Task 1, tracer)
2. `a87e225` test(32-03): every shank regime, every chamfer cap and the flank against the closed form (Task 2)
3. `2345939` chore(32-03): name the shaft kernel test file heavy, priced at 20.97 s in the commit slice (Task 2, pricing)
4. `09c0009` feat(32-03): refuse a cone start on the root circle and a solid outside its volume bracket (Task 3)
5. `0fe9312` docs(bench): the shaft solid's guards seen red once (32-03) (Task 3)

The solid runs `ShaftParams -> derive_shaft -> din5480.flank_half_angle -> outline -> extrude -> fuse -> cone intersect`. It reads tip, root and the applied chamfer from `derive_shaft` and the flank from `din5480.flank_half_angle` with the unrounded shift, and re-derives none of them. `model.py`, `parts.py`, `records.py`, `pool.py` and `pyproject.toml` are untouched (`git diff --exit-code b4cfd71` exits 0), so nothing in `src/spur` imports `shaft_model` yet and `make lint-imports` still reads `Contracts: 10 kept, 0 broken.`

### Each bar with its measured worst

All from `investigation/32-03-tolerances.py` (log `32-03-tolerances.log`), tabled in `bench/RESULTS.md` under `### Kernel tolerances, measured (32-03)`.

| Constant | Value | Worst measured | Its row | Ratio |
|---|---|---|---|---|
| `FLANK_ANGLE_ABS` | 1e-14 rad | 3.886e-16 rad | `m0.8-z6-x0.45`, r 3.02 (192 cases) | 25.7x |
| `VOLUME_REL` | 1e-4 | 1.471e-06 | W 14x2x6 | 68x |
| `READBACK_TOL` | 1e-6 mm | 1.0e-07 mm (cone bounding box; radii read 2.8e-14) | every chamfer row | 10x |
| `FLANK_BAR_PER_MODULE` | 5e-4 | 4.353e-05 per module | W 9x1x8 | 11.5x |
| `VOLUME_BRACKET_SLACK` | 1e-4 | 4.539e-09 relative excursion outside the bracket | `below-resolution`, `none-asked` | 22000x |

Neither stop-and-ask threshold fired: the flank angle gap is far under 1e-9, the file's worst volume error is under 1e-5, and the bracket's worst excursion is under 1e-6.

### The kernel file, priced (heavy-file outcome)

`make verify.fast` after `a87e225`, warm, load read before each (`32-03-verify-fast.log`): with the file 20.12, 20.50 and 20.97 s (1-minute load 29.8, 29.0, 29.3), without it 12.76 and 12.98 s (load 26.3, 23.4). The slowest is above the 20.0 s rule, so in one commit `--ignore=tests/test_shaft_model.py` joined `test.fast`, `"test_shaft_model"` joined `HEAVY_TEST_FILES`, and the Makefile comment records the readings. The host was loaded far above the 3.0-5.5 earlier pricing was read at, so the readings overstate an idle host; the rule was applied as measured because the cost of being wrong is a commit killed at 30 s. The whole gate and the pre-push hook still run the file. The next commit's hook ran 12.6 s.

## Verification

- `make verify`: `======================= 2626 passed in 286.96s (0:04:46) =======================` (2402 at the 32-02 close, plus 192 flank-angle cases and 32 kernel tests). Static steps green, `Contracts: 10 kept, 0 broken.`, `gear.unchanged: ... byte-equal to v0.6`, coverage 98.21 % (floor 96).
- `git diff --exit-code v0.6 -- src/spur/calc.py src/spur/params.py tests/regression/ .github/workflows/ci.yml` exits 0.
- Task acceptance criteria all held: `1 True`; 11 shank and 6 chamfer-cap tests pass; no pinned face count (`grep` prints 0); each of the seven red logs has a `N failed` summary and `32-03-red-clean.log` names `shank-eq-tip` and `shank-eq-root`; `_guard_cone_start(` and `_guard_volume(` each appear twice; `-k "root_band or volume_bracket or lattice"` reports 3 passed; the last `bench/RESULTS.md` commit changes no `src`, `tests` or `pyproject.toml` and deletes 0 lines; `git status --porcelain -- src tests` is empty.
- Tracer gate: the Task 1 verify was re-run after its commit (1145 passed, `10 kept`) before Task 2 began.

## Seen red once

Seven breaks, each with `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared before and after, reverted with `git checkout`, `git status --porcelain -- src tests` empty after each. Rows are in `bench/RESULTS.md` under `### Seen red once (Phase 32)`; logs are `investigation/32-03-red-*.log`.

| Break | Result |
|---|---|
| clean after the fuse | 4 failed: `shank-eq-tip`, `shank-eq-root`, and the rows within 1e-9 and one ulp of the tip; first `BuildError: ... not one valid solid` |
| no `_guard_cone_start` | 1 failed, `DID NOT RAISE BuildError` (the offset 1e-5 builds in 0.65 s, so it fails instead of hanging) |
| no `_guard_volume` | 1 failed, `DID NOT RAISE BuildError` |
| no wrap | 1 failed, `RuntimeError: kernel exploded` |
| no tooth cap (shaft_calc) | 1 failed, bracket `volume 11897.3 outside 11898.6 to 11906` |
| `floor_mm` rounds | 2 failed: no-shank on one-solid, shank row on bounding box xmax 34.6996 against 34.7 |
| oracle sign flipped | 1 failed, `0.04114862456829815 <= 0.0001` |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The plan's 21-position flank sample reads the deviation 5x low**
- **Found during:** Task 2, measuring before setting `FLANK_BAR_PER_MODULE`.
- **Issue:** At 21 positions per BSPLINE edge W 14x2x6 read 7.4e-06 per module and W 9x1x8 7.7e-06, which would have set the bar at 1e-4. The spline's error peaks between its 16 interpolation points, and a sparse sample steps over the peak. At 201 positions W 14x2x6 reads 3.985e-05 and W 9x1x8 4.353e-05, the latter matching the research's own 4.35e-05 (`32-flank-dev.log`, m 1, z 8).
- **Fix:** The flank test samples 201 positions; W 9x1x8, the row the bar is set from, joined the flank rows (five rows, not the plan's four); the bar is 5e-4 (11.5x), the smallest step at least 10x the dense worst.
- **Files modified:** `tests/test_shaft_model.py`, `bench/RESULTS.md`
- **Commit:** a87e225

**2. [Rule 3 - Blocking, plan rule applied] The heavy-file rule fired**
- **Found during:** Task 2 pricing: slowest `real` 20.97 s against the 20.0 s rule.
- **Fix:** Applied exactly as the plan states (Makefile `--ignore`, `HEAVY_TEST_FILES`, Makefile comment with the readings, `bench/RESULTS.md` section, the log) in one commit. The Makefile's help line, recipe comment and `test.fast` description were changed from "five" to "six".
- **Commit:** 2345939

**3. `_guard_volume` has no `ra` parameter.** The plan's signature lists `ra`, but the bracket formula never reads it; an unused argument is dropped. Signature is `_guard_volume(solid, area, rf, c, length, shank_length, shank_d)`.

**4. The measurement script and log are in the plan's file list only as a log.** `32-03-tolerances.log` is now produced by `32-03-tolerances.py` (modes `angle`, `rows`, `bracket`, ruff-clean because the hook lints `investigation/*.py`), and both were committed with Task 1 because the `FLANK_ANGLE_ABS` comment cites the log.

**5. The tip and root read-back skips a row whose section height is the junction.** For `both-caps-tie` the section height `(c + Ls)/2` is `Ls` itself, where the spline meets the shank; the script reads it as 0 there. The test reads tip and root on the default only (D-02), so no test depends on it.

**Total deviations:** 1 bug, 1 plan rule applied, 3 notes. **Impact:** none on printed numbers; the flank bar is set from the honest dense reading instead of the sparse one.

## Findings that matter later

- **Overshoot of 4.4e-16 mm builds.** Scratch check, not a committed test: `splined_length` `nextafter(3.0, 0)` with W 70x3x22 and `end_chamfer` 5 gives `end_chamfer_effective` 3.0, which is 4.44e-16 mm above the length; it builds one valid solid with and without a 20 mm shank, volume 2.2e-9 and 1.1e-9 off the closed form. 32-02 measured the overshoot at most 1.03e-12 mm up to 500 mm; no row here reaches a splined length that large with a chamfer capped by it, and no claim of "under 1e-12" is made.
- The pre-commit hook lints `investigation/*.py` with ruff, so evidence scripts must be ruff-clean (already noted in 32-02).
- `tests/test_shaft_model.py` is 29 kernel builds and about 8 s of the commit slice on a loaded host; 32-04 adds more kernel-touching shaft rows and should price them the same way.

## Debt and ideas filed

Filed: `docs/tech_debt/active/2026-10-27-pre-commit-hook-name-and-l36-still-say-five-heavy-files.md` (severity nice, INDEX row added in `2345939`). The `.pre-commit-config.yaml` hook name and L36's amendment still count five heavy files; the config was left alone because the Makefile's hooks stamp depends on it and touching it mid-commit would re-run `pre-commit install` inside a running hook. No idea item filed.

## Auth gates

None.

## Known Stubs

None.

## Threat Flags

None. T-32-04 (kernel hang) is mitigated by the band guard, the grid test and R2; T-32-05 (empty shape or remnant returned as the part) by the one-solid check, the bracket, every test against the closed form and R3, R5, R6; T-32-06 (tangent shank invalid) by `Shape.fuse` only, the 11 shank rows and R1.

## Open item for review

- **Edge probe, REQ-shaft-solid (unresolved, from the plan):** the row set is the planner's reading (shank equal to tip and root and the tiny offsets around tip, caps at tooth height and splined length and their tie, a sub-resolution and a zero chamfer, no shank, small and large tooth counts). A reviewer should confirm no edge is missing. 32-RESEARCH A3 also stands: hang points off the lattice other than the one found may exist; the band guard bounds it and the grid test shows it is never reached.

## Self-Check: PASSED

Commits 47c4782, a87e225, 2345939, 09c0009 and 0fe9312 are ancestors of HEAD; `src/spur/shaft_model.py`, `tests/test_shaft_model.py`, the seven `32-03-red-*.log` files, `32-03-tolerances.log`, `32-03-verify-fast.log` and the debt item exist; `git status --porcelain -- src tests` is empty.
