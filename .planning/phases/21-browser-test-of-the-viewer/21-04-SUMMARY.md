---
phase: 21-browser-test-of-the-viewer
plan: 04
subsystem: testing
tags: [playwright, shareable-link, hashchange, reset, chrome-headless-shell, pytest, tech-debt]

requires:
  - phase: 21-03
    provides: serve_stl_from, _follow_link, the three form/422/warning steps
provides:
  - eval_pairs(page) in tests/browser_session.py
  - step `link round trip` (fresh load, hashchange, default dropped, Reset) in the one scenario test
  - step `root_shape=bogus as today`, pinning the silent drop of an invalid enum value
  - docs/tech_debt/active/2026-10-10-root-shape-bogus-loads-a-blank-select.md (must) and its INDEX row
  - four 21-04 rows in bench/RESULTS.md `### Seen red once (Phase 21)` plus the 21-04 readings
affects: [21-05, 21-06, 21-07, 23, 24]

actuals:
  tokens: 6000
  tasks: 2
  commits: 2

plan_head_before: 068358ca43dfee65f6ccafd509515565ee3fc7d8
plan_head_after: 3db272caf8d9c36db4ebcc611eec1096e47e71f0
commits: 2

tech-stack:
  added: []
  patterns:
    - a wait is on the /api/info request the page sent, captured with expect_request around the action, never on an empty #status or on an href's mere presence
    - a link is compared with the form, the sent query and the rewritten fragment as sorted (name, value) pairs, because gearQuery() emits schema order
    - a pin of a known-bad behaviour names its debt file in every assertion message

key-files:
  created:
    - docs/tech_debt/active/2026-10-10-root-shape-bogus-loads-a-blank-select.md
  modified:
    - tests/browser_scenarios.py
    - tests/browser_session.py
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "Links are compared as sorted lists of pairs, not sets, so a duplicated pair would also fail"
  - "The form check is total: fields the link names read its string, every other field reads what the fresh default load read, so readHash resetting absent fields is covered too"
  - "In the bogus step the info query is asserted inside the STL wait, because a blank root_shape makes the API refuse and no STL is ever requested"

patterns-established:
  - "Seen red once may need a narrower break than the plan names when an earlier step shares the code path (hashchange)"

requirements-completed: [REQ-browser-link-round-trip]

coverage:
  - id: D1
    description: "Every field a link sets reaches the form, and the query the page sends and the fragment it writes equal the link as pairs, on fresh load and on hashchange; a field at its default shows in the form and is not sent"
    requirement: REQ-browser-link-round-trip
    verification:
      - kind: integration
        ref: "tests/browser_scenarios.py#test_the_shipped_viewer_in_a_real_browser (step link round trip)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Reset sends an empty query, leaves an empty fragment and an empty #mate-teeth, and restores the form to the fresh default load's pairs"
    requirement: REQ-browser-link-round-trip
    verification:
      - kind: integration
        ref: "tests/browser_scenarios.py#test_the_shipped_viewer_in_a_real_browser (step link round trip, Reset)"
        status: pass
    human_judgment: false
  - id: D3
    description: "#root_shape=bogus&teeth=22 is pinned as it behaves today (blank select, query without root_shape, no message, API alone 422) and filed as must debt"
    requirement: REQ-browser-link-round-trip
    verification:
      - kind: integration
        ref: "tests/browser_scenarios.py#test_the_shipped_viewer_in_a_real_browser (step root_shape=bogus as today)"
        status: pass
    human_judgment: false

duration: 10min
completed: 2026-10-10
status: complete
---

# Phase 21 Plan 04: Link Round Trip and the Bogus-Enum Pin Summary

**The browser test now proves a shared link's fields reach the form and come back unchanged on fresh load, `hashchange` and Reset, judged against the requests the page actually sent, and pins `#root_shape=bogus` as today's silent drop with the debt filed in the same commit**

## Performance

- **Duration:** about 10 min (12:57Z to 13:07Z, after reading the plan and the earlier summaries)
- **Tasks:** 2
- **Files modified:** 5 (four modified, one created)
- Quick run `make test PYTEST_ARGS="tests/browser_scenarios.py -n0 --no-cov -q"`: `1 passed in 4.04s` to `4.20s` wall. Steps: `link round trip` 0.35 to 0.38 s, `root_shape=bogus as today` 0.07 s.

## Accomplishments

- `link round trip`, fresh load: a second page opened on hash A (STL fulfilled from the first build); each field A names reads A's string, every other field reads its fresh default, `#mate-teeth` reads 30, and the sent `/api/info` query and the fragment `update()` wrote equal A as pairs.
- `link round trip`, `hashchange`: the same on the main page for hash B (fragment asserted different first), then link C naming `teeth` at its schema default (19, read at test time) beside `face_width=8`: the form shows 19, the page sends `face_width=8` only.
- `link round trip`, Reset: empty sent query, empty fragment, empty `#mate-teeth`, and the form equal to the pairs read on the fresh default load.
- `root_shape=bogus as today`: select `''` at `selectedIndex` -1; requests `api/info?teeth=22` and `api/model.stl?teeth=22&quality=preview`; fragment `#teeth=22`; no `.error`; `.warning` texts equal the API's for `teeth=22`; the API alone answers 422 "Input should be 'radial' or 'trochoid'". Each message begins "today's behaviour, filed as debt:" and the debt path.

## Links as chosen

- **A** (out of schema order on purpose): `mate_teeth=30&recess_sides=top&root_shape=trochoid&face_width=9&teeth=24&module=2&bore_d=10` (Teeth, Body, Bore, Recess; two selects at non-default options).
- **B**: `mate_teeth=45&recess_sides=bottom&pressure_angle=20&face_width=6&teeth=31&module=1.5` (Teeth, Body, Recess; one select).
- **C**: `teeth=19&face_width=8`, `19` being `properties["teeth"]["default"]` read from `/api/schema` and asserted an int.
- The API answered 200 for A (one warning), B (none) and C; the test asserts 200 for A and B at run time. They are constants in `tests/browser_scenarios.py` with a comment on how they were chosen.

## Red lines (four rows in `bench/RESULTS.md`, plus two notes under them)

| Step | Break | First failure line |
|---|---|---|
| `link round trip`, fresh load | `readHash();` removed from the load function | `link round trip, fresh load: the form differs from the link on [(('teeth', ''), ('teeth', '24')), ...]` |
| `link round trip`, hashchange | narrowed break `if (!location.hash.includes('mate_teeth')) readHash();` | `link round trip, hashchange: the form differs from the link on [(('teeth', '23'), ('teeth', '31')), ...]` |
| `link round trip`, Reset | the default-restoring loop removed from `#reset` | `link round trip, Reset: the page sent 'face_width=8'` |
| `root_shape=bogus as today` | `input.value !== '' && ` removed from `gearQuery()` | `...: /api/info was sent 'teeth=22&root_shape='` |

Each break was reverted with `git checkout -- src/spur/static/app.js` and checked with `git diff --exit-code` before the next.

## Task Commits

1. **Task 1: link round trip on fresh load, Reset and hashchange** - `91150ae` (test)
2. **Task 2: pin `#root_shape=bogus` and file it as debt** - `3db272c` (test)

## Files Created/Modified

- `tests/browser_session.py` - `eval_pairs`, the form's (name, value) pairs, typed without `Any`
- `tests/browser_scenarios.py` - link constants, `_pairs`, `_differing`, `_assert_link_applied`, the two new steps
- `bench/RESULTS.md` - four 21-04 red rows and the 21-04 readings
- `docs/tech_debt/active/2026-10-10-root-shape-bogus-loads-a-blank-select.md` - the debt, `Severity: must`
- `docs/tech_debt/INDEX.md` - its Active row, trigger "Phase 23 or 24 touches buildForm's enum rendering, or a user reports a link that loaded a blank select"

## Decisions Made

See `key-decisions`. No product code, fixture byte or `tests/test_api.py` pin moved: `git diff --exit-code` on `src/spur/static/app.js` against HEAD, and on `tests/regression/pre_v0_2.json`, `tests/test_api.py` and the product modules against `592506f`, is clean; `tests/test_api.py -k round_trips` still passes.

## Deviations from Plan

None - plan executed exactly as written, apart from two small choices and one observation:

- The `hashchange` break the plan names (remove `readHash();` from the listener) does go red, but first at the earlier step `invalid field marked` (`/api/info? answered 200, not 422`), since 21-03's steps also depend on that listener. It never reaches the new step, so the row records both that and a narrower break that does (the listener skips `readHash()` for hashes naming `mate_teeth`).
- The first draft of the bogus step read the plan's break as a 45 s `TimeoutError`, because a blank `root_shape` makes the API refuse and no STL is requested. The info query is now asserted inside the STL wait, so the red line is the assertion naming `root_shape=`.
- Links are compared as sorted lists of pairs rather than sets (strictly stronger).

## Issues Encountered

- Acceptance check `grep -nE 'wait_for_timeout\(|time\.sleep\(' ... | grep -vE '^[^:]+:[0-9]+:[[:space:]]*#'` prints one line, `tests/browser_session.py:117`, the `time.sleep(0.05)` poll interval in 21-01's `stop_group` (its condition is the process group, with a comment saying so). Not introduced by this plan and not a wait in a browser step; nothing in `tests/browser_scenarios.py` matches.
- Extra breaks, recorded as a note and not as rows: dropping `gearQuery()`'s default check altogether goes red at the fresh-load sub-path; to reach the default-dropped sub-path itself the check was removed for `teeth` only, giving `link round trip, default dropped: the page sent the default 'teeth=19&face_width=8'`.

## Verification

- `make test PYTEST_ARGS="tests/browser_scenarios.py -n0 --no-cov -q"`: `1 passed in 4.20s`.
- `make lint typecheck`: ruff `All checks passed!`, mypy `Success: no issues found in 45 source files`.
- `make verify` (foreground, exit 0): `1220 passed in 198.58s (0:03:18)`, coverage 97.75 % against the 96 % floor.
- Debt checks: file has `Severity: must`, `Status: active`; INDEX and the scenario module name it; both in one commit with `tests/browser_scenarios.py`.

## Known Stubs

None.

## Threat Flags

None. No new network surface; the test reads the same 127.0.0.1 server it already starts. T-21-12 is transferred as planned (pinned and filed, validation unchanged); T-21-13 is mitigated (the fragment is asserted different before every assignment, and the captured request is the signal).

## Debt Filed

`docs/tech_debt/active/2026-10-10-root-shape-bogus-loads-a-blank-select.md` (must), INDEX row added in commit `3db272c`.

## Next Phase Readiness

21-05 (golden request sweep) can reuse `eval_pairs` and `_pairs`. No blockers.

## Self-Check: PASSED

- Files found: `tests/browser_scenarios.py`, `tests/browser_session.py`, `bench/RESULTS.md`, `docs/tech_debt/INDEX.md`, `docs/tech_debt/active/2026-10-10-root-shape-bogus-loads-a-blank-select.md`
- Commits found on HEAD: `91150ae`, `3db272c`; `git rev-list --count 068358c..HEAD` printed 2 before this summary
- `grep -c '^| 21-04' bench/RESULTS.md` prints 4; `eval_pairs` defined once; both step names present in order

---
*Phase: 21-browser-test-of-the-viewer*
*Completed: 2026-10-10*
