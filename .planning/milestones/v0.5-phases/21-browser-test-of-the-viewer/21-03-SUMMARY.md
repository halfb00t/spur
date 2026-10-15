---
phase: 21-browser-test-of-the-viewer
plan: 03
subsystem: testing
tags: [playwright, schema, 422, warnings, chrome-headless-shell, pytest]

requires:
  - phase: 21-01
    provides: the tracer, tests/browser_session.py, the staging scenario
  - phase: 21-02
    provides: PNG_RATIO_BAR 4.9 and BUILD_WAIT_MS 45000 confirmed on two hosts
provides:
  - serve_stl_from(page, stl) and STL_ROUTE in tests/browser_session.py
  - steps `form from schema`, `invalid field marked`, `warning rendered` in the one scenario test
  - five 21-03 rows in bench/RESULTS.md `### Seen red once (Phase 21)` plus the 21-03 readings
affects: [21-04, 21-05, 21-06, 21-07, 21-08, 23, 24]

actuals:
  tokens: 4600
  tasks: 2
  commits: 2

plan_head_before: efe833f26a91885263ad357f63a01726b0b8ade7
plan_head_after: 528a8dd7afc8ac80952fa4427a5a152078574095
commits: 2

tech-stack:
  added: []
  patterns:
    - every expectation is read from the server at test time (/api/schema, the API's own 422 body, /api/info warnings for the query the page sent)
    - a wait is on the expected text or href for the query the page sent, never on an element count
    - after the first real build the STL is fulfilled from its bytes, so later steps build nothing

key-files:
  created: []
  modified:
    - tests/browser_scenarios.py
    - tests/browser_session.py
    - bench/RESULTS.md

key-decisions:
  - "STL_ROUTE moved to tests/browser_session.py so serve_stl_from and the scenario share one pattern"
  - "_follow_link uses expect_request for both the 422 and warning links, and refuses a fragment equal to the current one (no hashchange would fire)"
  - "zero-count assertions use locator.count() == 0, so no integer literal reaches to_have_count"

patterns-established:
  - "Marked titles are compared as a set against the 422 body's loc[1] and ctx.fields, and the text against msg after app.js's two documented transforms"

requirements-completed: [REQ-browser-form-from-schema, REQ-browser-invalid-field-marked, REQ-browser-warning-rendered]

coverage:
  - id: D1
    description: "The rendered form equals /api/schema: field names in order, legends by group, titles, and the four theme custom properties non-empty"
    requirement: REQ-browser-form-from-schema
    verification:
      - kind: integration
        ref: "tests/browser_scenarios.py#test_the_shipped_viewer_in_a_real_browser (step form from schema)"
        status: pass
    human_judgment: false
  - id: D2
    description: "bore_flat=3 (ctx.fields path) and teeth=2 (loc[1] path) mark the right field and show the API's message; a valid link clears the marks"
    requirement: REQ-browser-invalid-field-marked
    verification:
      - kind: integration
        ref: "tests/browser_scenarios.py#test_the_shipped_viewer_in_a_real_browser (step invalid field marked)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Warnings render as exactly /api/info's list for two links (two, one) and nothing for a link with none"
    requirement: REQ-browser-warning-rendered
    verification:
      - kind: integration
        ref: "tests/browser_scenarios.py#test_the_shipped_viewer_in_a_real_browser (step warning rendered)"
        status: pass
    human_judgment: false

duration: 38min
completed: 2026-10-10
status: complete
---

# Phase 21 Plan 03: Form, 422 Marking and Warnings Summary

**The browser test now proves the rendered form equals `/api/schema`, that both of `problems()`'s marking paths follow the API's own 422 body, and that warnings render as exactly `/api/info`'s list, each assertion seen red once**

## Performance

- **Duration:** 38 min (10:40:33Z to 11:18:48Z)
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- `form from schema` runs inside the parked window: 31 fields in 7 groups, names in DOM order, legends, titles and `--view-bg`, `--grid`, `--mesh`, `--edge` all compared with values read at test time.
- `invalid field marked`: `#bore_flat=3` marks `D-flat` and shows `D-flat must be between 4.5 and 9 mm (flat to opposite side).` (no prefix); `#teeth=2` marks `Teeth` and shows `Teeth: Input should be greater than or equal to 6`. `data-triangles` unchanged, and a valid link leaves no `.invalid`.
- `warning rendered`: API warning counts for `module=1&pressure_angle=14.5`, `bore_hex=6`, `teeth=23` are 2, 1, 0, and the rendered `.warning` texts equal each list exactly, with no `.error`.
- The scenario still issues one real STL request per run (`continue_()` count 1); every later STL comes from `serve_stl_from`.

## Task Commits

1. **Task 1: form from schema and the two 422 paths** - `fd30026` (test)
2. **Task 2: warnings rendered** - `528a8dd` (test)

## Red lines (five, all in `bench/RESULTS.md` `### Seen red once (Phase 21)`)

| Step | Break | First failure line |
|---|---|---|
| `form from schema` | `Object.entries(...)` reversed | `form fields ['hex_wall', 'hex_cell', ...] differ from the schema's, grouped: ['teeth', 'module', ...]` |
| `form from schema` | `--grid` renamed `--grid-x` | `the custom property --grid is empty on :root` |
| `invalid field marked` | `...(d.ctx?.fields ?? [])` removed | `#bore_flat=3: marked [], the 422 names ['D-flat']` |
| `invalid field marked` | `d.loc?.[1],` removed | `#teeth=2: marked [], the 422 names ['Teeth']` |
| `warning rendered` | rendered warnings `.slice(0, 1)` | `#module=1&pressure_angle=14.5: rendered warnings [one] differ from the API's [two]` |

Each break was reverted with `git checkout -- <file>` and checked with `git diff --exit-code` before the next.

## Verification

- Quick run `make test PYTEST_ARGS="tests/browser_scenarios.py -n0 --no-cov -q"`: `1 passed in 3.06s`.
- `make lint typecheck`: ruff clean, mypy `Success: no issues found in 45 source files`.
- `make verify`: `1220 passed in 152.97s (0:02:32)`, coverage 97.92 % against the 96 % floor (the staging module is still uncollected).
- `git diff --exit-code` on `app.js` against HEAD and on `tests/regression/pre_v0_2.json`, `tests/test_api.py` and the product modules against `592506f`: clean.
- Step seconds on this host (Apple M5 Max, macOS): `form from schema` 0.01 s, `invalid field marked` 0.08 s, `warning rendered` 0.21 s.

## Deviations from Plan

None - plan executed exactly as written. Small choices inside the plan's latitude: `STL_ROUTE` moved to `browser_session.py`; the 422 and warning links share one `_follow_link` helper (the plan named `expect_response` for the 422 step and `expect_request` for the warning step; `expect_request` serves both); zero-count checks use `.count() == 0` because the acceptance criterion forbids a numeric literal after `to_have_count`.

## Issues Encountered

- `make verify` ran in the background after the shell's 10 minute limit; the log was read from disk. No gate or test failure occurred, so nothing was filed under `investigation/`.
- The "Seen red once" table now has a readings paragraph under it; later plans insert their rows above that paragraph.

## Known Stubs

None.

## Threat Flags

None. No new network surface: the test reads the same server it already starts on 127.0.0.1.

## Next Phase Readiness

21-04 can add the link round trip and the `root_shape=bogus` pin on top of `_follow_link` and `serve_stl_from`. No blockers.

## Self-Check: PASSED

- Files found: `tests/browser_scenarios.py`, `tests/browser_session.py`, `bench/RESULTS.md`
- Commits found on HEAD: `fd30026`, `528a8dd`
- Plan checks re-run: quick run `1 passed`; `make verify` `1220 passed`; `grep -c '| 21-03' bench/RESULTS.md` prints 5; `grep -c 'continue_()' tests/browser_scenarios.py` prints 1; `to_have_count([0-9]` finds nothing.

---
*Phase: 21-browser-test-of-the-viewer*
*Completed: 2026-10-10*
