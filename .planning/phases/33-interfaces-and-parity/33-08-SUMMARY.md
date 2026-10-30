---
phase: 33-interfaces-and-parity
plan: 08
subsystem: testing
tags: [playwright, parity, shaft, vanilla-js, number-box, viewer, readme]

requires:
  - phase: 33-interfaces-and-parity
    provides: "33-05 tests/shaft_parity.py (SHAFTS, displayed, web_rows); 33-06/33-07 the shaft page, PARTS descriptor, shaft links; 33-03 the as-written rule and the token table; 33-01 decision B1 and C1"
provides:
  - "Browser steps `parity: web and API`, `shaft as-written sweep`, `viewer framing`; helpers `_download_name` and `_assert_refused_as_written` (shared with the gear sweep)"
  - "test_the_page_formats_numbers_with_the_expression_the_parity_test_ports and test_only_the_shaft_sizes_the_floor_grid_from_its_height"
  - "PARTS.gridAlong: a long shaft's floor grid is sized from its height too; the gear's grid is unchanged"
  - "README, web-ui.md, L49 'The page agrees', bench/RESULTS.md section and two seen-red rows, three screenshots with -after copies"
affects: [33-09]

actuals:
  tokens: 6663   # chars/4 over the added lines of src/, tests/, README, docs/ and bench/ (logs and pictures excluded)
  tasks: 3
  commits: 5
plan_head_before: a863945f1cf5f0ef25d67f3e48773c7c20020271
plan_head_after: 15d775f7634ca2cc9bc39d86e7b02ab6f9df374e

tech-stack:
  added: []
  patterns:
    - "The page's table is compared with the API's at the displayed text through a Python port of fmt, and the port is itself checked against the browser's own expression, which a source pin holds equal to app.js"
    - "A browser step that makes pictures writes them under pytest's tmp_path and a run keeps them with --basetemp, so a gate run leaves nothing in the tree and no environment read is added (D-02 pin)"
    - "A part-specific view rule lives in the PARTS descriptor, never as a branch beside gear code"

key-files:
  created:
    - .planning/phases/33-interfaces-and-parity/investigation/33-08-red-fmt.log
    - .planning/phases/33-interfaces-and-parity/investigation/33-08-browser.log
    - .planning/phases/33-interfaces-and-parity/investigation/33-08-shaft-default.png
    - .planning/phases/33-interfaces-and-parity/investigation/33-08-shaft-longest.png
    - .planning/phases/33-interfaces-and-parity/investigation/33-08-shaft-widest.png
    - .planning/phases/33-interfaces-and-parity/investigation/33-08-shaft-default-after.png
    - .planning/phases/33-interfaces-and-parity/investigation/33-08-shaft-longest-after.png
    - .planning/phases/33-interfaces-and-parity/investigation/33-08-shaft-widest-after.png
  modified:
    - tests/test_browser.py
    - tests/test_api.py
    - src/spur/static/app.js
    - README.md
    - docs/architecture/web-ui.md
    - docs/architecture/decision_log.md
    - bench/RESULTS.md

key-decisions:
  - "The shaft's floor grid counts the part's height through a descriptor field (gridAlong), because the longest shaft's 40 mm grid could not be seen under a 1000 mm part; the gear's descriptor says false so every gear's grid is as it was"
  - "Framing pictures go to pytest's tmp_path (kept with --basetemp) and not to the investigation directory on every run, and not through an environment variable: test_browser_pins refuses an environ read that is not SPUR_ or PLAYWRIGHT_BROWSERS_PATH"
  - "B2 in the browser is the 91-token re-read on the seven shaft inputs plus one API request per blanked token naming all seven fields, not 455 more page links; the page-link proof is B1's seven links, as 33-03 did for the gear"

patterns-established:
  - "A red that the plan's perturbation cannot reach because an earlier step stops the walk is paired with a second perturbation only the new step can see, both kept in the one log"

requirements-completed: [REQ-shaft-web, REQ-shaft-parity, REQ-wr02-fixed]

coverage:
  - id: D1
    description: "The page's shaft table equals the API's numbers over the four shafts of the fixed set, at the displayed text and with no tolerance: same labels, order, fmt(v) plus unit, designation as printed, no row for a null (42 rows)"
    requirement: REQ-shaft-parity
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step parity: web and API)"
        status: pass
    human_judgment: false
  - id: D2
    description: "displayed() equals the browser's own toFixed(3) rule on the tie and sign cases and every number of every document (47 numbers); app.js fmt is pinned to exactly that expression"
    requirement: REQ-shaft-parity
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step parity: web and API)"
        status: pass
      - kind: unit
        ref: "tests/test_api.py#test_the_page_formats_numbers_with_the_expression_the_parity_test_ports"
        status: pass
    human_judgment: false
  - id: D3
    description: "The download name is one name on the page and the API for each shaft of the set (spur_shaft_w25x1.25x18, w30x2x14, w26x1.25x19, w25x1.25x18) and the default's STEP, compared as strings"
    requirement: REQ-shaft-parity
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step parity: web and API)"
        status: pass
    human_judgment: false
  - id: D4
    description: "WR-02 on the shaft: the token table re-read on the seven shaft number inputs, fit holds +8f, seven #part=shaft&<field>=%2B<default> links refused as written with the box blank and no shaft STL, every blanked token refused on all seven fields"
    requirement: REQ-wr02-fixed
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step shaft as-written sweep)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The viewer frames every shaft whole after Fit (default, longest, widest), and the longest shaft's grid is visible after the gridAlong change; the gear's grid is unchanged by construction"
    requirement: REQ-shaft-web
    verification:
      - kind: unit
        ref: "tests/test_api.py#test_only_the_shaft_sizes_the_floor_grid_from_its_height"
        status: pass
    human_judgment: true
    rationale: "Whether a part is in view and a grid reads well is a judgment on a picture; the step saves the pictures and the pin holds only the descriptor and the expression. Read on 33-08-shaft-*.png and -after.png by the executor"
  - id: D6
    description: "README says spur makes a gear and a DIN 5480 shaft, documents the switch and #part=shaft links and advertises no fit window or tolerance value; web-ui.md and L49 'The page agrees' match what shipped"
    requirement: REQ-shaft-web
    verification: []
    human_judgment: true
    rationale: "Whether the prose says what the page does is a reading judgment; the grep criteria (0 fit-window words, DIN 5480 present, one bold lead) only prove its shape"

duration: 22min
completed: 2026-10-27
status: complete
---

# Phase 33 Plan 08: The page agrees with the API, and the shaft's refusal and framing Summary

**The browser now proves the page's shaft table and download names equal the API's over the four-shaft set (42 rows, no tolerance, the `fmt` port checked against the browser's own rule), the as-written refusal holds on all seven shaft number fields, and a long shaft's invisible floor grid is fixed through a descriptor field that leaves every gear's grid as it was.**

## Performance

- **Duration:** about 22 min (Started about 2026-10-27T17:44Z, estimated: the start stamp was not recorded; first commit 17:48:56Z; Completed 2026-10-27T18:06Z)
- **Tasks:** 3 (1 tracer, 2 auto)
- **Files modified:** 7 tracked files modified (plus 8 created: 2 logs and 6 pictures)

## Accomplishments

- **Parity step** (`parity: web and API`, 1.19 s): for each member of `tests/shaft_parity.py` `SHAFTS` the page is sent to `part=shaft` plus the values, its `#dims` rows are read as `(dt, dd)` pairs and asserted equal (not near) to `web_rows(info, dims)`: `parity: 4 shafts, 42 rows equal the API's, 47 numbers rounded as the browser does`. The null rows (`odd-z` has no `Measurement over pins M_Re`, `no-shank-no-chamfer` no `End chamfer used`) are absent on both sides. Each `#dl-stl` click's `suggested_filename` equals the API's `Content-Disposition` name (`_download_name`, header only) and the literal; the default's STEP is `spur_shaft_w25x1.25x18.step`.
- **Precision:** `displayed()` equals `Number(v).toFixed(3).replace(/\.?0+$/, '')` evaluated in the page on nine tie and sign cases (`0.0625`, `0.0005`, `1.0005`, `2.675`, `-0.0001`, `-0.0`, `27.9994`, `123456.7895`, `1e-7`) and on every number of every document. `test_the_page_formats_numbers_with_the_expression_the_parity_test_ports` holds `app.js`'s `fmt` to exactly that expression.
- **Seen red twice, both reverted** (`investigation/33-08-red-fmt.log`, two rows in `bench/RESULTS.md`): a sign-dropping `fmt` (`Math.abs`) failed the parity step first line `E AssertionError: w30x2x14: the page's rows differ from the API's.` (`Profile shift x` reads `0.05` for `-0.05`), and the pin; the plan's `toFixed(2)` failed the pin and the earlier step `part switch` (`'Profile shift x·m', '0.56 mm' != '0.562 mm'`). `git diff --quiet HEAD -- src/spur/static/app.js` was clean after each.
- **Shaft as-written sweep** (`shaft as-written sweep`, 1.12 s): `shaft sweep: 7 inputs probed x 91 tokens, 7 links, 65 blanked tokens refused on 7 fields`. The probe agrees with the table on the seven shaft inputs; `fit` is `type=text` and holds `+8f`; one `#part=shaft&<field>=%2B<default>` link per number field is sent as given, answered `number_as_written` at `["query", name]`, with the box blank, the field `.invalid`, the message equal to `_expected_422`, no href and no shaft STL asked for; each of the 65 blanked non-empty tokens is refused by `/api/shaft/info` with all seven fields named. The per-link check is a helper (`_assert_refused_as_written`) that the gear's `as-written sweep` now calls too (still `30 links, 1.17 s`).
- **Framing judgement:** read on `33-08-shaft-default.png`, `-longest.png`, `-widest.png` after a click on Fit: the whole part is in view in all three. The longest shaft's grid was 40 mm (step 2) under a 1000 mm part and could not be seen, so `placeGrid()` now takes `Math.max(across, height)` when the part's descriptor says `gridAlong`. After: default shaft 40 to 80 mm (step 2 to 5), longest 40 to 1600 mm (step 100), widest 1400 mm (step 100) unchanged. **The gear default's grid, before and after: size 60, step 5** (its STL box is 36.56 x 36.68 x 7.5 mm; the gear's descriptor says `gridAlong: false`, so the extent is the same expression as before for every gear). The `-after` pictures were read: the longest now stands on a visible grid.
- **Docs:** README intro and a bullet name both parts, a new `## Web` section describes the Gear | Shaft switch, `#part=shaft` links and the refusal of any other `part`, with no fit window or tolerance value; web-ui.md `Tests` and the grid note; L49 gained **The page agrees**; `bench/RESULTS.md` gained `### The page's half of parity (33-08)` and the two seen-red rows.

## Task Commits

1. **Task 1: Tracer: the page's shaft table and download names equal the API's over the fixed set, seen red on a perturbed `fmt`** - `293d5dd` (test)
2. **Task 2: The as-written refusal proved on the shaft's own number inputs** - `84b1b6b` (test)
3. **Task 3: The viewer frames every shaft; README and web-ui.md say what the page serves; the browser cost recorded**
   - `6df1ab6` (test) the `viewer framing` step and the before pictures
   - `f13f4cc` (fix) `fix(web): frame a long shaft's grid along its axis`, its pin and the after pictures
   - `15d775f` (docs) README, web-ui.md, L49, `bench/RESULTS.md`, the browser log

**Plan metadata:** the `docs(33-08): complete ...` commit that adds this file.

## Verification

- Browser test: `3 passed in 47.64s` (`make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"`, log `33-08-browser.log`). The plan's fails_when says `1 passed`; the file holds three tests (33-06 and 33-07 recorded the same), so the line reads `3 passed` and nothing failed. Step timers: `parity: web and API` 1.19 s, `shaft as-written sweep` 1.12 s, `viewer framing` 4.39 s. 1-minute load 5.79 before and 4.91 after. Recorded in `bench/RESULTS.md` against 33-07's call time (40.41 s vs 47.12 s, a 6.71 s difference equal to the three steps' total, on different load; no speed claim).
- `make verify` (the gate): `2775 passed in 257.67s (0:04:17)`, `real 258.58`, rc 0, `Contracts: 10 kept, 0 broken.`; 1-minute load 4.55 before and 5.29 after. The tree was clean afterwards (no picture written).
- `make verify.fast`: `2308 passed in 11.31s`, `real 12.18` (under the 30 s bar), load 4.18. `make gear.unchanged`: byte-equal to v0.6 (`/api/schema` 8723 bytes). `make no-fake-done`: rc 0. ruff clean, mypy `--strict` on `tests/test_browser.py`, `tests/test_browser_pins.py` 15 passed.
- Acceptance criteria re-run: `grep -c 'from shaft_parity import' tests/test_browser.py` 1; `grep -cE 'approx|isclose' tests/test_browser.py` 0 (0 before); `^| 33-08 | parity: web and API` 1 in RESULTS; `parity: web and API` 3 in the red log; app.js clean after the reds; `shaft as-written sweep` 1 in test_browser.py; the step printed 7 links and 7 probed inputs; `### The page's half of parity (33-08)` 1; `**The page agrees**` 1; README `fit window|tolerance window|deviation` 0 and `DIN 5480` 5.

## Decisions Made

- `gridAlong` in the `PARTS` descriptor (shaft true, gear false) instead of a branch in `placeGrid()`: the plan's way (through the descriptor so every gear's grid is unchanged), after the longest shaft's grid read as invisible.
- The framing pictures use `tmp_path` and `--basetemp`, not a committed path rewritten on every gate run and not an environment variable (see Deviations 3).
- B2 is the probe plus one all-fields API request per blanked token (see Deviations 4).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The plan's `toFixed(2)` perturbation cannot turn the parity step red first**
- **Found during:** Task 1 (the seen-red run)
- **Issue:** step `part switch`, which runs before `parity: web and API`, compares the default shaft's rows with a Python `_js_fmt` and fails on `0.56 mm` vs `0.562 mm`, so the walk stops there and the parity step never runs. The plan's acceptance wants `parity: web and API` in the log.
- **Fix:** kept the plan's run as run 1 in `33-08-red-fmt.log` (the pin and `part switch` red), and added run 2 with a perturbation only the new step can see (`fmt` dropping the sign: no number an earlier step compares is negative, `w30x2x14`'s profile shift is). Both are rows in `### Seen red once (Phase 33)`; the parity row is the `Math.abs` one.
- **Files modified:** `bench/RESULTS.md`, `investigation/33-08-red-fmt.log` (app.js reverted after each)
- **Verification:** the log holds `parity: web and API` three times; `git diff --quiet HEAD -- src/spur/static/app.js` clean.
- **Commit:** `293d5dd`

**2. [Rule 1 - Bug] The page does not send a value that equals its default**
- **Found during:** Task 1 (first green run)
- **Issue:** the plan's step asserts the sent query for `odd-z` is the set's values; the page's `gearQuery` drops `module=1.25` (its default), so the first run failed on `sent 'reference_d=26&teeth=19'`.
- **Fix:** the step compares the page's sent pairs with the set's values less the fields at their schema default, while the API is asked for all of them.
- **Files modified:** `tests/test_browser.py`
- **Commit:** `293d5dd`

**3. [Rule 3 - Blocking] The framing pictures are not written to the investigation directory by the step**
- **Found during:** Task 3 (the commit hook)
- **Issue:** the plan has the step screenshot straight into the three PNGs under `investigation/`, which makes every gate run rewrite tracked files. My first answer, an `SPUR_FRAMING_DIR` read, failed `tests/test_browser_pins.py` (an `environ` read that is not `SPUR_` or `PLAYWRIGHT_BROWSERS_PATH` is a D-02 path that can change which part is tested), and that pin is not mine to loosen.
- **Fix:** the test function takes pytest's `tmp_path`, the step saves there and asserts each file is non-empty; the committed pictures were taken from a run with `--basetemp=<dir>` and copied in (`33-08-shaft-*.png`, then the `-after` copies).
- **Files modified:** `tests/test_browser.py`
- **Verification:** `tests/test_browser_pins.py` 15 passed; `git status` clean after `make verify`.
- **Commit:** `6df1ab6`

**4. [Rule 2 - interpretation] B2 as written in the plan is the probe and an API check, not 455 more page links**
- **Found during:** Task 2
- **Issue:** the plan's "B2, every refused-blank TOKENS entry on every shaft field" repeated 33-03's wording, but 33-03's executed step and the plan's own acceptance ("7 links under B1 and 7 probed inputs") hold B1's links and the table re-read only; 33-01's recorded pick says the full table is re-probed in Chromium on every number input.
- **Fix:** B2 is the Chromium re-read on the seven shaft inputs (all 91 tokens) and, for the shaft route, one request per blanked non-empty token naming all seven fields, asserting a 422 that names each (65 requests, about 1 s).
- **Files modified:** `tests/test_browser.py`
- **Commit:** `84b1b6b`

**5. [Rule 2 - Missing critical functionality] A pin for the new descriptor field**
- **Found during:** Task 3 (after the fix)
- **Issue:** New behaviour ships with its test: nothing held the gear's grid at `gridAlong: false`.
- **Fix:** `test_only_the_shaft_sizes_the_floor_grid_from_its_height` holds the gear false, the shaft true once, and the `placeGrid()` expression; seen red once by flipping the gear's field (`the gear's grid must not follow its height`), then restored.
- **Files modified:** `tests/test_api.py`
- **Commit:** `f13f4cc`

---

**Total deviations:** 5 (2 bugs in the plan's steps, 1 blocking, 2 additions). **Impact on plan:** the plan's assertions all hold; the pictures come from `--basetemp` and not from the gate.

## Issues Encountered

- While checking the new pin red I ran `git checkout -- src/spur/static/app.js` to undo a one-line flip, which also discarded the uncommitted `gridAlong` fix. The `sed -i.bak` backup of the fixed file was still on disk, so I copied it back, re-ran the three affected pins and diffed (`9 insertions, 4 deletions`) before committing. Nothing was lost or committed wrong.
- The host load stayed between 4 and 8 for this plan (it was 10 to 32 in earlier plans), so the timings above carry a smaller spread than 33-07's.

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None. The shaft table is still written with `textContent` only and the `writes_a_field_shut` guard (`.innerHTML`, `insertAdjacentHTML`) is green (T-33-19 mitigated). T-33-18 is mitigated by the parity step, the `fmt` pin and two recorded reds; T-33-20 by the shaft sweep.

## Debt and ideas filed

None filed in this plan.

## Next Phase Readiness

- 33-09 can diff `refuse()` and `gearQuery()` against `6800769` (untouched here; only `PARTS` and `placeGrid()` changed in `app.js`), read the gate delta against 33-01's baseline (229.17 s; this plan's gate read 257.67 s at a load of 4.5 to 5.3, with the browser test now holding the three new steps' 6.71 s), and write the C1 reading beside SC4 and REQ-wr02-fixed.
- Shared requirement IDs (REQ-shaft-web, REQ-shaft-parity, REQ-wr02-fixed are also declared by other plans) stay open until the last declaring plan finishes.

## Self-Check: PASSED

- Created and modified files exist (the two test files, `app.js`, README, web-ui.md, `decision_log.md`, `bench/RESULTS.md`, the two logs and the six pictures).
- Commits `293d5dd`, `84b1b6b`, `6df1ab6`, `f13f4cc` and `15d775f` are ancestors of HEAD; `git rev-list --count a863945..HEAD` is 5 (the measured `commits:`).
- Acceptance criteria and the plan-level verification re-run (see Verification).

---
*Phase: 33-interfaces-and-parity*
*Completed: 2026-10-27*
