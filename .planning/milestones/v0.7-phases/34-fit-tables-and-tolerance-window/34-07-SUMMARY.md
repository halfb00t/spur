---
phase: 34-fit-tables-and-tolerance-window
plan: 07
subsystem: shaft
tags: [din5480, solid, max-material, build-pool, browser-parity, d-13]

requires:
  - phase: 34-fit-tables-and-tolerance-window
    provides: "34-04: ShaftDimensions.max_effective_thickness and SOLID_AT_NOMINAL_THICKNESS; 34-05: BuildPool(tables=...); 34-02: with_tables and the synthetic fixture"
provides:
  - "build_shaft writes the printed max_effective_thickness as the flank's shift when the tables give one, the nominal shift otherwise"
  - "tests/test_shaft_model.py: _flank_shift, _thickness_at_reference_circle (a per-flank read-back off the z-section), four thickness/name tests"
  - "tests/test_pool.py: _built_volume and the worker-builds-the-same-part test"
  - "tests/browser_session.py serve(env=...) and the browser step 'parity with tables'"
affects: [34-16, 34-17]

actuals:
  tokens: 5500   # chars/4 over the src and tests diff (21,884 chars); red logs and this file excluded
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "The solid takes its thickness from the printed row, never re-derived: the row is written as the flank's shift s = pi*m/2 + 2*xm*tan(ALPHA)"
    - "A thickness is proved off the solid by bisecting each flank edge of the z-section to the circle m*z/2, one value per flank"
    - "A browser step that needs a table file starts its own server through serve(env=...)"

key-files:
  created:
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-07-red-thickness.log
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-07-red-browser.log
  modified:
    - src/spur/shaft_model.py
    - src/spur/shaft_params.py
    - tests/test_shaft_model.py
    - tests/test_shaft_interfaces.py
    - tests/test_pool.py
    - tests/browser_session.py
    - tests/test_browser.py

key-decisions:
  - "D-13 (raised by 34-04, the human chose KEEP): there is no separate, always-present thickness row. max_effective_thickness is the row the solid carries: printed means the solid is cut at it, null means the solid is cut at the nominal thickness and SOLID_AT_NOMINAL_THICKNESS says so. No sixth thickness key was added."
  - "The solid carries the printed value rounded to 0.001 mm, not the unrounded s_vmax, so the number and the part name one shaft (L08)."
  - "The download name does not follow the tables (L49): the row and the warning tell the two solids apart."

requirements-completed: [REQ-solid-max-material, REQ-fit-tolerance-window, REQ-mre-limits]

coverage:
  - id: D1
    description: "With the tables loaded and the fit listed, the default shaft's solid carries s_vmax 2.592 on every one of its 36 flanks (worst 3.8e-8 mm against a bar of 6.25e-4), its flank agrees with the oracle at that thickness (2.6e-7 mm) and its volume within 4.0e-9 relative"
    requirement: REQ-solid-max-material
    verification:
      - kind: unit
        ref: "tests/test_shaft_model.py#test_with_the_tables_the_solid_carries_the_maximum_effective_thickness"
        status: pass
    human_judgment: false
  - id: D2
    description: "The solid switches exactly where the row does: a fit outside Table 7, an off-table size and no file all carry the nominal thickness on every flank with SOLID_AT_NOMINAL_THICKNESS"
    requirement: REQ-solid-max-material
    verification:
      - kind: unit
        ref: "tests/test_shaft_model.py#test_a_fit_outside_table_7_and_an_off_table_size_build_the_nominal_solid, #test_without_the_tables_the_solid_carries_the_nominal_thickness"
        status: pass
    human_judgment: false
  - id: D3
    description: "A build worker given the parent's tables builds the same maximum-material solid (volume equal to 1e-9 relative, 6.4e-4 away from the nominal solid) and exports STL bytes"
    requirement: REQ-solid-max-material
    verification:
      - kind: integration
        ref: "tests/test_pool.py#test_a_worker_builds_the_maximum_material_shaft_from_the_parents_tables"
        status: pass
    human_judgment: false
  - id: D4
    description: "The download name is spur_shaft_w25x1.25x18 with the tables loaded as without them, in ShaftParams.slug(), the API's Content-Disposition and the browser's saved file"
    requirement: REQ-solid-max-material
    verification:
      - kind: unit
        ref: "tests/test_shaft_model.py#test_the_download_name_does_not_follow_the_tables, tests/test_shaft_interfaces.py#test_the_download_name_does_not_follow_the_tables"
        status: pass
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step parity with tables)"
        status: pass
    human_judgment: false
  - id: D5
    description: "With a table file loaded a real browser prints the five rows from the schema with no page code: the page's rows equal the API's for all four parity shafts (63 rows, against 42 with no tables) and the default shows the five new labels"
    requirement: REQ-fit-tolerance-window
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (steps parity: web and API, parity with tables)"
        status: pass
    human_judgment: false
  - id: D6
    description: "The thickness and the rows are computed from the synthetic Table 6/7 values: they prove the plumbing and the arithmetic, not the standard's own numbers"
    requirement: REQ-mre-limits
    verification: []
    human_judgment: true
    rationale: "The fixture's Table 7 is invented. That the solid carries the standard's s_vmax for a real size is proved by 34-16's worked-example anchor and the human at 34-14/34-15."

duration: 23min
completed: 2026-10-30
status: complete
plan_head_before: 70bca9e46e40d0bc94646447726b2133ed65814f
plan_head_after: 656cf02c8fafe47e5ccf1ef9a96d476ad264d763
commits: 3
---

# Phase 34 Plan 07: The solid carries the printed thickness Summary

**With the tables loaded and the fit listed, build_shaft cuts the flank at the printed s_vmax (2.592 on the default, read back off the solid on all 36 flanks to 3.8e-8 mm), a build worker given the parent's tables builds the same part, and a real browser shows the five tolerance rows from the schema with no page code.**

## Performance

- **Duration:** about 23 min (start about 16:14Z, end 16:37Z)
- **Tasks:** 3 of 3 (Task 1 a tracer)
- **Files:** 7 modified, 2 red logs created
- **Host load:** 4.4 to 7.4 at the runs below

## Accomplishments

- **The change in `build_shaft`:** `xm_flank` is `(s_vmax - pi*m/2) / (2*tan(ALPHA))` when `dims.max_effective_thickness` is printed and today's `xm` otherwise, passed to `_outline`. Tip and root stay the printed diameters. The module docstring now says which thickness the solid carries and why.
- **The read-back, default shaft, tables loaded:** 36 flanks (2 per tooth), worst distance from 2.592 is 3.79e-8 mm against a bar of `FLANK_BAR_PER_MODULE * m` = 6.25e-4 mm (16000x under). Flank against the oracle at that thickness written as the shift: 2.56e-7 mm. Volume against `shaft_oracle.shaft_volume` at that shift: 3.96e-9 relative (bar `VOLUME_REL` 1e-4). `model.export(ShaftParams(), "stl", "preview")` returns 209484 bytes.
- **Worker against parent:** default shaft volume 22841.013 mm^3 with the tables, 22855.626 mm^3 without (14.6 mm^3, 6.4e-4 relative; the preview mesh's own error bar, 6e-3, is 9x that, which is why the test compares volumes as numbers). The worker built from `BuildPool(1, 30, tables=build())` equals the in-process build to 1e-9 relative, and `pool.export` returns STL bytes (`len == 84 + 50*n`).
- **Browser step:** `parity with tables: 4 shafts, 63 rows equal the API's, 3.10 s` (green run, 3.11 s in the second); `parity: 4 shafts, 42 rows` still reads 42 on the shared no-table server. The 21 extra rows are the five labels on each of the four shafts, plus the odd-count shaft's M_Re at the tabulated pin. The default's rows hold all five new labels.
- **Browser test call time (the gate cost 34-17 reads):** `test_the_shipped_viewer_in_a_real_browser` call 60.43 s in both green runs (host load 4.44 and 4.25 at their start).
- **Gate:** `make verify` rc 0, `2924 passed in 364.29s (0:06:04)` (host load 7.35 at the start).

## Task Commits

1. **Task 1 (tracer): the solid carries the maximum effective tooth thickness from the tables** - `b3461d7`
2. **Task 2: a worker builds the maximum-material shaft from the parent's tables** - `9f5b4df`
3. **Task 3: the five tolerance rows reach the page from the schema** - `656cf02`

**Tracer gate:** the tracer's `<verify>` carries only `<automated>` commands; after the commit all were green (49 tests in `tests/test_shaft_model.py`, the export one-liner, ruff, mypy, 10 contracts kept, `make no-fake-done`, `make gear.unchanged`, the hook's `make verify.fast`), so the plan expanded: Tracer verified end-to-end.

## Files Created/Modified

- `src/spur/shaft_model.py` - the printed thickness written as the flank's shift; docstring
- `src/spur/shaft_params.py` - the `slug()` docstring no longer says the solid does not depend on the fit
- `tests/test_shaft_model.py` - `_flank_shift`, `_thickness_at_reference_circle`, `_assert_every_flank_carries`, four tests; `_closed_form` and `_flank_error` read the shift through `_flank_shift` (no change without tables)
- `tests/test_shaft_interfaces.py` - the Content-Disposition half of the name test (light, stub backend)
- `tests/test_pool.py` - `_built_volume` and the worker test
- `tests/browser_session.py` - `serve(floor_applies, env=None)`
- `tests/test_browser.py` - the step `parity with tables`

## Decisions Made

- **D-13 (raised by 34-04, the human chose KEEP), for 34-17 to log:** there is no separate, always-present thickness row. `max_effective_thickness` is the row the solid carries: printed means the solid is cut at it; null means the solid is cut at the nominal thickness and `SOLID_AT_NOMINAL_THICKNESS` says so. No sixth thickness key was added.
- The solid carries the printed value, rounded to 0.001 mm, so the row and the part name one shaft.
- The tests read the thickness per flank (an `all` over 36 values by loop, one assert each), not an average.

## Deviations from Plan

**1. [Rule 1 - Bug] A stale comment in `ShaftParams.slug()`**
- **Found during:** Task 1
- **Issue:** the docstring said the fit is left out of the name because "the solid does not depend on it". With the tables the solid depends on the fit, so the sentence had become false.
- **Fix:** the sentence now says the solid depends on the fit only when a table file gives it a maximum-material thickness, and that the printed row and the warning, not the name, say which solid it is. Comment only; the name is unchanged (L49).
- **Files modified:** src/spur/shaft_params.py
- **Committed in:** `b3461d7`

**2. [Rule 3 - Blocking] The API half of the name test lives in `tests/test_shaft_interfaces.py`**
- **Found during:** Task 1
- **Issue:** the plan lists `test_the_download_name_does_not_follow_the_tables` under `tests/test_shaft_model.py`, which builds real solids; the `Content-Disposition` assertion needs a `TestClient` and the stub backend that file does not have, and `tests/test_shaft_interfaces.py` already holds both and the frozen-name test.
- **Fix:** the slug half is in `test_shaft_model.py` as planned; the header half is a light test beside the existing download-name test.
- **Files modified:** tests/test_shaft_interfaces.py
- **Committed in:** `b3461d7`

**3. [Rule 1 - Bug] The first tabled read-back test failed on the volume before it reached the thickness**
- **Found during:** Task 1 (red run)
- **Issue:** `_check` asserts volume first, so the red run showed a volume miss (6.4e-4) and not the 0.021 mm thickness miss the plan names.
- **Fix:** the test builds the solid, reads every flank back first, then checks the flank and the volume. Test only.
- **Committed in:** `b3461d7`

**Total deviations:** 3 auto-fixed (2 bug, 1 blocking). **Impact:** none on scope or on the artifacts the plan lists.

## Seen red

| Plan | Test id | Deliberate break | First failure line | Restored |
|---|---|---|---|---|
| 34-07 | `test_with_the_tables_the_solid_carries_the_maximum_effective_thickness` | none: ran against the unchanged `build_shaft` | `assert 0.02101449881648243 <= (0.0005 * 1.25)` (read 2.6130145 against 2.592; 34x the bar), `investigation/34-07-red-thickness.log` | n/a, then implemented |
| 34-07 | `test_a_worker_builds_the_maximum_material_shaft_from_the_parents_tables` | `BuildPool(1, 30)` with no `tables=` | `assert 0.0006397595291864899 <= 1e-09` (worker 22855.626 against the in-process 22841.013) | `tables=with_tables` put back, green |
| 34-07 | `test_the_shipped_viewer_in_a_real_browser`, step `parity with tables` | `serve()` with the `env` argument left out | `AssertionError: the default shows no ['Max actual tooth thickness s_max', 'Max effective tooth thickness s_vmax', 'Measurement over pins M_Re max', 'Measurement over pins M_Re min', 'Min actual tooth thickness s_min'] with the tables loaded`, `investigation/34-07-red-browser.log` | `env=` put back, green |

Not seen red: the tier-3 and off-table cases, the no-file case and the two name tests passed on the first run, because they pin behaviour the code already had (34-04's tiers, L49's slug); they exist so a later edit to `build_shaft` cannot move those solids.

## Issues Encountered

- `tests/test_browser.py` did not flake in either run or in `make verify`.
- The commit hook stashes unstaged files while it runs; the user's uncommitted `.planning/state.json` change and the untracked `.planning/milestone.lock` and `.planning/ui-reviews/` were restored each time and never staged.

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None beyond the plan's threat model. T-34-24 (a solid and its printed thickness naming different shafts) is mitigated and seen red; T-34-25 (a cache serving the other table state) by `with_tables` clearing both caches; T-34-26 by the step writing the synthetic fixture to `tmp_path` and `serve()` still stripping inherited `SPUR_*` variables.

## Debt and ideas

Filed none.

## User Setup Required

None.

## Next Phase Readiness

34-16 can anchor the worked example against a solid that carries the printed thickness. 34-17 reads the browser test's call time (60.43 s) from here and logs D-13 as above. No blocker.

## Self-Check: PASSED

- FOUND: `src/spur/shaft_model.py` (`grep -c 'dims.max_effective_thickness'` prints 1), both red logs (`grep -cE 'failed|FAILED'` prints 2 and 8), the five modified test and harness files
- FOUND: commits `b3461d7`, `9f5b4df`, `656cf02`; `git rev-list --count 70bca9e..HEAD` prints 3
- `git diff ddfb3ea -- src/spur/static/` and `git diff ddfb3ea -- src/spur/model.py src/spur/calc.py src/spur/params.py tests/regression/` are empty; `make gear.unchanged` passes
- `grep -c 'parity with tables' tests/test_browser.py` prints 2; the green run holds `parity: 4 shafts, 42 rows` and `parity with tables: 4 shafts,`
- `make verify`: 2924 passed

---
*Phase: 34-fit-tables-and-tolerance-window*
*Completed: 2026-10-30*
