---
phase: 21-browser-test-of-the-viewer
plan: 05
subsystem: testing
tags: [playwright, golden-pin, shareable-link, make-target, chrome-headless-shell, pytest]

requires:
  - phase: 21-04
    provides: eval_pairs, step link round trip, the fragment/hashchange wait on the /api/info request
  - phase: 21-01
    provides: serve(floor_applies=...), launch, STL_ROUTE, BUILD_WAIT_MS
provides:
  - fixture_hash, fixture_hashes, sweep, FIXTURE_PATH, GOLDEN_PATH in tests/browser_session.py
  - tests/capture_requests.py and `make golden.regen`
  - tests/regression/golden_requests.json, the query each of the 44 fixture links sends
  - step `golden sweep` in the one scenario test, between `link round trip` and `root_shape=bogus as today`
  - two 21-05 rows in bench/RESULTS.md `### Seen red once (Phase 21)` and `### Golden request pin (21-05)`
affects: [21-06, 21-07, 21-08, 23, 24]

actuals:
  tokens: 5900
  tasks: 2
  commits: 2

plan_head_before: 0b5e15839adb15c25d6fe050227a31b8b4f20250
plan_head_after: 9c7f5b3f3007d71214cdbcb46b1096193a2c1db3
commits: 2

tech-stack:
  added: []
  patterns:
    - one sweep shared by the test and the regen script, so the pin is captured by the page and never by a Python copy of gearQuery()
    - a pin file is written only by its make target and only read by the test; a regen is a commit of its own
    - the sweep guards on the live fragment (not the previous raw link) because update() rewrites the fragment with replaceState

key-files:
  created:
    - tests/capture_requests.py
    - tests/regression/golden_requests.json
  modified:
    - tests/browser_session.py
    - tests/browser_scenarios.py
    - Makefile
    - bench/RESULTS.md

key-decisions:
  - "The sweep is called with serve(floor_applies=lambda: False): it aborts the STL route and builds nothing, so the pool never starts a worker and the teardown group floor would otherwise fail"
  - "The pin and the fixture are compared by name before the queries are, so a record added to one and not the other fails with a message that says to run make golden.regen"
  - "The scenario's golden variable is named `swept`, because `sent` already holds a str earlier in the same test function (mypy)"

patterns-established:
  - "Seen red once may need a narrower break than the plan names when an earlier step reads the same code path: gearQuery() sending every field is caught first at `link round trip, fresh load`; narrowed with `|| location.hash.includes('mate_teeth=40')` it reaches `golden sweep`"

requirements-completed: [REQ-browser-golden-request-sets]

coverage:
  - id: D1
    description: "The exact api/info query string the real page sends for each of the 44 fixture records' links is pinned in tests/regression/golden_requests.json and asserted by the browser test, which names every record that moved with its expected and sent query"
    requirement: REQ-browser-golden-request-sets
    verification:
      - kind: integration
        ref: "tests/browser_scenarios.py#test_the_shipped_viewer_in_a_real_browser (step golden sweep)"
        status: pass
    human_judgment: false
  - id: D2
    description: "make golden.regen rewrites the pin through the same serve/launch/sweep as the test, and a regen on unchanged code is a byte-identical rewrite"
    requirement: REQ-browser-golden-request-sets
    verification:
      - kind: other
        ref: "make golden.regen && git diff --exit-code tests/regression/golden_requests.json"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-10-10
status: complete
---

# Phase 21 Plan 05: Golden request pin Summary

**The query each of the 44 fixture links sends is pinned in `tests/regression/golden_requests.json`, captured by the real page through `make golden.regen` and asserted by step `golden sweep`, so Phases 23-24 show an empty diff instead of asserting "the same fields are sent".**

## Performance

- **Duration:** about 25 min
- **Completed:** 2026-10-10
- **Tasks:** 2
- **Files modified:** 6 (2 created, 4 modified)

## Accomplishments

- `fixture_hash`, `fixture_hashes` and `sweep` in `tests/browser_session.py`: the fixture is parsed straight from `pre_v0_2.json` (no kernel import), each record becomes its shareable link, and one page with the STL route aborted puts each link in `location.hash` and keeps the `api/info` query exactly as `URLSearchParams` wrote it. A link equal to the live fragment raises naming the record (Pitfall P5); the empty link takes the fresh-load query.
- `tests/capture_requests.py` and the `golden.regen` target (prerequisites `$(STAMP) $(BROWSER)`, in `.PHONY` and `make help`) write the pin with `sort_keys`, indent 2, a trailing newline and a `regenerate` sentence. No date, no sha.
- The first capture: 44 records, 44 distinct queries, 16 of the 43 non-empty links differ from their raw link, `README:export-defaults` pins `""`.
- Step `golden sweep` (0.19-0.23 s on this host over 5 runs) compares the sweep with the pin, read-only, and names every moved record with its expected and sent query. The pin and fixture names are compared first.

## Task Commits

1. **Task 1: one sweep, a regen script behind make golden.regen, the first capture** - `d40a09a` (test)
2. **Task 2: step golden sweep, seen red twice** - `9c7f5b3` (test)

**Plan metadata:** the docs commit that carries this file.

## TDD record

- **Task 1 RED:** a scratch script (kept in the scratchpad, not committed) asserting the `<behavior>` lines -- `fixture_hash({}, None) == ''`, `fixture_hash({'teeth': 19}, 40) == 'teeth=19&mate_teeth=40'`, `1.0` kept as `1.0`, `fixture_hashes()` names equal the fixture's in file order, the defaults record is `''` -- failed with `ImportError: cannot import name 'fixture_hash'` before any code existed. This is a load failure, so it is a record that the function was absent, not a behavioural RED. GREEN: the same script printed `behavior ok 44`. The pin itself is proved by Task 2's step, which is the committed test.
- **Task 2 RED, two breaks, both reverted** (rows in `bench/RESULTS.md` `### Seen red once (Phase 21)`):
  - an edited pin entry (`README:export-teeth-24` `teeth=24` to `teeth=25`): `AssertionError: golden sweep: the form sends other queries: README:export-teeth-24: expected 'teeth=25&module=1&pressure_angle=20&bore_flat=0', sent 'teeth=24&module=1&pressure_angle=20&bore_flat=0'`, note `step: golden sweep`.
  - `gearQuery()` sending every non-empty field (`String(input.value) !== String(defaults[name])` becomes `true`): red, but first at `link round trip, fresh load`, because that step also reads what a default load sends. Narrowed to `... || location.hash.includes('mate_teeth=40')` it reaches the new step: `AssertionError: golden sweep: the form sends other queries: README:info-mate-40+mate=40: expected 'mate_teeth=40', sent 'teeth=19&module=1.75&...&mate_teeth=40'; ...`, naming all four records that carry `mate_teeth=40`.
  - Both reverted with `git checkout` of the file; `git diff --exit-code` on `app.js` and the pin exits 0.
- No separate GREEN or REFACTOR commit exists for the step: the plan names two commits, one per task, and the breaks are reverted before each commit.

## Readings (Apple M5 Max, macOS, 2026-10-10, load 4.4)

| Reading | Value |
|---|---|
| Records, distinct queries | 44, 44 |
| Links whose sent query differs from their raw link | 16 of 43 |
| `golden sweep` step | 0.23, 0.19, 0.21, 0.23, 0.19 s |
| `make golden.regen` on unchanged code | byte-identical on 4 regens after the first capture; `git diff --exit-code tests/regression/golden_requests.json` exits 0 |

Three queries that differ from their raw link:

- `README:export-teeth-24`: `bore_flat=0&module=1&pressure_angle=20&teeth=24` became `teeth=24&module=1&pressure_angle=20&bore_flat=0` (schema order)
- `README:info-mate-40+mate=40`: `teeth=19&mate_teeth=40` became `mate_teeth=40` (19 is the default)
- `test_api.py::test_impossible_mate_is_a_warning_not_a_number`: `bore_chamfer=0&bore_d=0&bore_flat=0&pressure_angle=14.5&profile_shift=-0.6&recess_sides=none&teeth=6` became `teeth=6&pressure_angle=14.5&profile_shift=-0.6&bore_d=0&bore_flat=0&bore_chamfer=0&recess_sides=none`

## Gate

- `make verify`: `1220 passed in 144.65s (0:02:24)`, coverage 97.92 % against the required 96.0 %, exit 0. Run in the foreground after Task 2's last edit and before its commit. The commit-time hook (`make verify.fast`) passed on both commits.
- `make lint typecheck`: `All checks passed!` and `Success: no issues found in 46 source files`.
- Quick run: `make test PYTEST_ARGS="tests/browser_scenarios.py -n0 --no-cov -q"` gave `1 passed` (3.5-3.7 s) on every green run.
- Untouched: `git diff --exit-code 592506f -- tests/regression/pre_v0_2.json tests/test_api.py src/spur/params.py src/spur/calc.py src/spur/model.py src/spur/pool.py src/spur/app.py src/spur/cli.py` exits 0, and `src/spur/static/app.js` is byte-identical to the phase base.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Lint line length and a mypy name clash**
- **Found during:** Task 1 (a 101-column print) and Task 2 (the scenario's `sent` is already a `str` in the same function, so the sweep result could not take that name)
- **Fix:** split the print into two lines; named the sweep result `swept` in the step
- **Files modified:** tests/capture_requests.py, tests/browser_scenarios.py
- **Committed in:** `d40a09a`, `9c7f5b3`

**2. [Plan break narrowed] The `gearQuery()` break reached an earlier step first**
- **Found during:** Task 2, seen-red
- **Issue:** with `String(input.value) !== String(defaults[name])` replaced by `true`, `link round trip, fresh load` fails before `golden sweep` is reached, so the plan's break does not show the new step red
- **Fix:** kept that reading in the row, and added the narrowed break (`|| location.hash.includes('mate_teeth=40')`) that reaches the new step. Same approach as 21-04's `hashchange` row. Both in one table row, so the table keeps its two 21-05 rows.
- **Files modified:** bench/RESULTS.md (the row only; `app.js` reverted)

---

**Total deviations:** 2 (1 blocking, 1 narrowed break). **Impact:** none on the product or on the pin.

## Issues Encountered

None that remain. A first `sed` for the `app.js` break failed on macOS `sed`'s newline handling before touching the file; the edit was redone in Python.

## Known Stubs

None.

## Threat Flags

None. The plan's register (T-21-14, T-21-15) is mitigated: the test only reads the pin, only `make golden.regen` writes it, and the fixture is byte-identical to `592506f`.

## Debt filed

None filed in this plan.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for 21-06 (admission: the rename to `tests/test_browser.py` and the gate exclusions). `tests/capture_requests.py` and `tests/browser_session.py` are not collected, so the rename does not touch them. Phases 23-24 owe an empty diff on `tests/regression/golden_requests.json`, or a `make golden.regen` commit of its own saying what moved and why.

## Self-Check: PASSED

- FOUND: tests/capture_requests.py, tests/regression/golden_requests.json, tests/browser_session.py (`def sweep(`, `def fixture_hash(`, `def fixture_hashes(`), Makefile (`golden.regen: $(STAMP) $(BROWSER)`), tests/browser_scenarios.py (`step("golden sweep")` between `link round trip` and `root_shape=bogus as today`), bench/RESULTS.md (`### Golden request pin (21-05)` and two `| 21-05` rows)
- FOUND: commits `d40a09a`, `9c7f5b3` on `gsd/phase-21-browser-test-of-the-viewer`

---
*Phase: 21-browser-test-of-the-viewer*
*Completed: 2026-10-10*
