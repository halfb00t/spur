---
phase: 27-ledger-tests-and-harness
plan: 05
subsystem: testing
tags: [playwright, browser-harness, ast-pins, tech-debt, js-number, fixture-hash]

requires:
  - phase: 27-ledger-tests-and-harness
    provides: 27-03 moved the server group teardown out of tests/browser_session.py's way; 27-04 left docs/tech_debt/INDEX.md free (one writer per wave)
provides:
  - launch() prints Playwright's error first, then a reinstall that works with the stamp present, the literal install command and the Linux --with-deps hint
  - test_browser_pins pins the reinstall command beside the install literal, and reads an environ allowance from the read's own statement
  - _js_number checks its range and writes -0 as 0; fixture_hash refuses a non-scalar param; the documented copy _page_string mirrors _js_number
  - the launch-message debt item retired
affects: [27-06 (MIN_GROUP_MEMBERS comment touches tests/browser_session.py after this plan)]

actuals:
  tokens: 2500   # chars/4 over the +/- lines of tests/ and docs/ (investigation logs excluded)
  tasks: 3
  commits: 3     # MEASURED: git rev-list --count e487d36..HEAD at write time (before the SUMMARY commit)

plan_head_before: e487d360700da08be982bc074e82c4cbc3959fb1
plan_head_after: 4d43b64262939c3d4d6465fadab522e48740ed62

tech-stack:
  added: []
  patterns:
    - "An AST pin allows a vendor-state read by a whole string constant in the read's own statement, not by a substring of its line"
    - "A documented commit-slice copy of a harness helper mirrors every check of the original, so its docstring stays true"

key-files:
  created:
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-05-red-launch-pin.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-05-launch-fail-closed.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-05-stamp-dry-run.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-05-red-environ-rule.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-05-red-harness-info.log
  modified:
    - tests/browser_session.py
    - tests/test_browser_pins.py
    - tests/test_browser.py
    - tests/test_selector.py
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/resolved/2026-10-10-launch-failure-message-names-a-stamp-that-skips-the-install.md

key-decisions:
  - "launch() stays text-only: the same pw.chromium.launch() call, the same except Error, the same single pytest.fail; no install, retry or skip path (L39, 21 D-02)"
  - "The environ allowance is equality with a string constant anywhere in the read's nearest enclosing ast.stmt, so a compound statement (if, with) holding a marker in its body also allows a read in its header; the pins stay a tripwire, which the docstring now says"
  - "fixture_hash is the place that refuses a non-scalar param (the encoder, not fixture_hashes), so the unit test drives it without a fixture file and every fixture record still goes through it"

patterns-established:
  - "Shown, not assumed: fail-closed with an empty PLAYWRIGHT_BROWSERS_PATH and the stamp read with make -n, so no 198 MB browser cache or stamp is deleted to demonstrate advice"

requirements-completed: [REQ-launch-message-true]

coverage:
  - id: D1
    description: "launch() fails with Playwright's error first, then `rm -f .venv/.browser && make test`, the literal `playwright install --only-shell chromium`, and `BROWSER_INSTALL_ARGS=--with-deps`; the clause saying make test runs the install is gone; the change is text-only"
    requirement: REQ-launch-message-true
    verification:
      - kind: unit
        ref: "tests/test_browser_pins.py::test_the_browser_test_has_no_path_that_passes_without_the_browser (3 passed; red 1 failed, 2 passed in investigation/27-05-red-launch-pin.log)"
        status: pass
      - kind: integration
        ref: "PLAYWRIGHT_BROWSERS_PATH=<empty dir> pytest tests/test_browser.py -k shipped_viewer -> 1 failed with the new text (investigation/27-05-launch-fail-closed.log)"
        status: pass
    human_judgment: false
  - id: D2
    description: "A missing stamp makes make test run the playwright install recipe (read with make -n, nothing deleted)"
    requirement: REQ-launch-message-true
    verification:
      - kind: other
        ref: "make -n test BROWSER=<absent path> (investigation/27-05-stamp-dry-run.log)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The pins' environ allowance reads the statement, not the line (21 IN-03): a comment marker is flagged, a wrapped read with the marker on its second line is not"
    verification:
      - kind: unit
        ref: "tests/test_browser_pins.py::test_an_environ_read_is_allowed_by_its_statement_not_its_line (red 1 failed in investigation/27-05-red-environ-rule.log; green 4 passed)"
        status: pass
    human_judgment: false
  - id: D4
    description: "_js_number writes -0 as 0 and refuses a value JavaScript writes with an exponent (23 IN-11); fixture_hash refuses a bool, null or other non-scalar param (21 IN-02); serve_stl_from's docstring re-wrapped (22 IN-02)"
    verification:
      - kind: unit
        ref: "tests/test_browser.py::test_the_oracle_reads_a_link_as_the_page_does and ::test_a_fixture_link_refuses_a_value_no_person_would_type (red 2 failed in investigation/27-05-red-harness-info.log; green 2 passed)"
        status: pass
      - kind: integration
        ref: "make test PYTEST_ARGS='tests/test_browser.py tests/test_browser_pins.py -n0 --no-cov -q' -> 7 passed in 25.41s (real browser)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The launch-message debt item is Status: resolved, git mv-ed, and its INDEX row moved in the fixing commit"
    verification:
      - kind: other
        ref: "docs/tech_debt/resolved/2026-10-10-launch-failure-message-names-a-stamp-that-skips-the-install.md, docs/tech_debt/INDEX.md"
        status: pass
    human_judgment: false

duration: 9min
completed: 2026-10-20
status: complete
---

# Phase 27 Plan 05: The launch message that names a working reinstall Summary

**The browser launch failure now prints Playwright's error first and names `rm -f .venv/.browser && make test` (the reinstall that works with the stamp present), pinned and seen red; the AST pins read an environ allowance from the statement; `_js_number` and `fixture_hash` check what their docstrings claim.**

## Performance

- **Duration:** 9 min (start estimated from the previous plan's final commit; PLAN_START_TIME was not captured)
- **Started:** 2026-10-20T13:49:00Z
- **Completed:** 2026-10-20T13:58:00Z
- **Tasks:** 3
- **Files modified:** 11 (6 source/doc, 5 investigation logs)

## Accomplishments

- `launch()` fails with `the headless shell did not start. Playwright said: {error}` first, then the advice. The old clause "`make test` runs the install stamp for you" is gone: the stamp `.venv/.browser` only re-runs when `pyproject.toml` or `requirements.txt` change, so with the stamp present and the shell gone `make test` skipped the install.
- The pin `REINSTALL_COMMAND` sits beside `INSTALL_COMMAND`; both are found in one `ast.Constant` of `launch()`.
- The `environ` allowance in the pins is now a string constant equal to `SPUR_` or `PLAYWRIGHT_BROWSERS_PATH` inside the read's own statement (21 IN-03); the docstring calls the pins a tripwire.
- `_js_number` (and the copy `_page_string`) assert the range JavaScript writes positionally and write `-0` as `0` (23 IN-11); `fixture_hash` refuses a non-scalar param (21 IN-02); `serve_stl_from`'s ragged docstring is re-wrapped (22 IN-02).

## Task Commits

1. **Task 1: launch message names the reinstall that works, pinned, shown failing closed, item retired** - `a393e50` (fix)
2. **Task 2: environ allowance read from the statement** - `0ed2057` (test)
3. **Task 3: `_js_number` range and `-0`, `fixture_hash` type check, docstring re-wrap** - `4d43b64` (test)

**Plan metadata:** the `docs(27-05)` commit that carries this file.

## Reds, shown readings, and gate

| Reading | First failure line | Log |
|---|---|---|
| Reinstall pin against the old text | `AssertionError: launch() must name rm -f .venv/.browser && make test when it fails: the stamp alone skips the install`; `1 failed, 2 passed in 0.07s` | `investigation/27-05-red-launch-pin.log` |
| Environ rule against the line rule | `assert 0 == 1` on `_problems("a.py", 'import os\nos.environ["X"]  # SPUR_\n')`; `1 failed, 3 deselected` | `investigation/27-05-red-environ-rule.log` |
| `-0` and `fixture_hash` before the fix | `AssertionError: assert {'dep': 'Needs Gate above -0'} == {'dep': 'Needs Gate above 0'}` and `Failed: DID NOT RAISE AssertionError`; `2 failed, 1 deselected` | `investigation/27-05-red-harness-info.log` |

- **Fail closed** (empty `PLAYWRIGHT_BROWSERS_PATH`, `-k shipped_viewer`): `1 failed, 1 deselected`. The message as printed begins `Failed: the headless shell did not start. Playwright said: BrowserType.launch: Executable doesn't exist at <empty dir>/chromium_headless_shell-...`, shows Playwright's own box, and ends with `If the shell is missing, \`rm -f .venv/.browser && make test\` installs it again: the stamp alone skips the install while it is present (\`.venv\` is the default VENV). Outside make, run \`playwright install --only-shell chromium\` with PLAYWRIGHT_BROWSERS_PATH=<empty dir>. On Linux, a missing shared library needs \`BROWSER_INSTALL_ARGS=--with-deps\` on that make command.` (`investigation/27-05-launch-fail-closed.log`). The empty-`PLAYWRIGHT_BROWSERS_PATH` edge also prints the path, and with the variable unset the message prints `<unset: Playwright's default cache>` (the `os.environ.get` default is unchanged).
- **Stamp dry run** (`make -n test BROWSER=<absent path>`): prints `.venv/bin/python -m playwright install  --only-shell chromium` then `touch <absent path>`, then the pytest line (`investigation/27-05-stamp-dry-run.log`). Nothing was run or deleted; `.venv/.browser` and `.venv/ms-playwright` still exist.
- **Real browser run** after Task 3: `make test PYTEST_ARGS="tests/test_browser.py tests/test_browser_pins.py -n0 --no-cov -q"` gave `7 passed in 25.41s` (every `_js_number` caller and the golden sweep through `fixture_hashes`).
- `git diff --exit-code v0.5 -- tests/regression/` exited 0.
- **`make verify` result line** (exit 0): `Required test coverage of 96.0% reached. Total coverage: 97.99%` and `1333 passed in 198.65s (0:03:18)`.

## Files Created/Modified

- `tests/browser_session.py` - new `launch()` message; `_js_number` range check and `-0`; `fixture_hash` type check; `serve_stl_from` docstring re-wrapped
- `tests/test_browser_pins.py` - `REINSTALL_COMMAND` and its assertion; `_problems(name, source)` with the statement-scoped allowance; `test_an_environ_read_is_allowed_by_its_statement_not_its_line`; docstring softened
- `tests/test_browser.py` - `-0.0` and exponent cases in `test_the_oracle_reads_a_link_as_the_page_does`; `test_a_fixture_link_refuses_a_value_no_person_would_type`
- `tests/test_selector.py` - `_page_string` mirrors `_js_number`
- `docs/tech_debt/resolved/2026-10-10-launch-failure-message-names-a-stamp-that-skips-the-install.md`, `docs/tech_debt/INDEX.md` - the retired item and its moved row (`Resolved in:` is the fixing commit's subject)

## Decisions Made

See `key-decisions` above. One reading for the verifier: the statement-scoped allowance is looser than the line rule in one direction (an `environ` read in the header of a compound statement is allowed if a marker constant sits anywhere in that statement's body). No such shape exists in the scan set today, and the pins are documented as a tripwire.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] mypy rejected the climb to the enclosing statement**
- **Found during:** Task 2 (`make verify.fast`)
- **Issue:** `statement = node` took the narrower type `Attribute | Name | ImportFrom`, so `statement = parents[statement]` failed `[assignment]`.
- **Fix:** annotated `statement: ast.AST = node`.
- **Files modified:** `tests/test_browser_pins.py`
- **Verification:** `make verify.fast` passed (932 passed)
- **Committed in:** `0ed2057`

**2. [Rule 3 - Blocking] ruff PT018 on a compound assertion in `fixture_hash`**
- **Found during:** Task 3 (`make verify`)
- **Issue:** `assert isinstance(...) and not isinstance(value, bool), (...)` is a compound assertion.
- **Fix:** computed `scalar = isinstance(value, int | float | str) and not isinstance(value, bool)` and asserted `scalar` with the same message; the plan's grep for `not isinstance(value, bool)` still holds.
- **Files modified:** `tests/browser_session.py`
- **Verification:** `make verify` exited 0
- **Committed in:** `4d43b64`

---

**Total deviations:** 2 auto-fixed (2 blocking, lint and type only)
**Impact on plan:** none on behaviour; both are the gate's own style rules.

## Issues Encountered

- The first `sed -i` for a docstring shortening used the GNU form and failed on macOS; redone with `sed -i ''` before any commit.
- The fail-closed log was captured one docstring edit before the final commit; the message text it shows is the committed text (only `launch()`'s docstring first line differs).
- The Task 3 plan expected the red to fail first on `-0`, so the exponent cases are exercised only after that fix; they were seen green together with it (`2 passed`).

## Debt filed

No debt item was filed. One retired: `docs/tech_debt/resolved/2026-10-10-launch-failure-message-names-a-stamp-that-skips-the-install.md`.

## Known Stubs

None.

## Threat Flags

None. The change adds no endpoint, auth path, file access or schema; T-27-16 (text-only launch change), T-27-17 (statement-scoped allowance) and T-27-18 (no browser or stamp deleted) are mitigated as planned.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 27-06 can touch `tests/browser_session.py` for the `MIN_GROUP_MEMBERS` comment; this plan's edits to the file are committed.
- `docs/tech_debt/INDEX.md` is free for 27-06.

## Self-Check: PASSED

- Files: `tests/browser_session.py`, `tests/test_browser_pins.py`, `tests/test_browser.py`, `tests/test_selector.py`, the retired debt item, the five `27-05-*.log` files all exist.
- Commits `a393e50`, `0ed2057`, `4d43b64` are ancestors of HEAD.

---
*Phase: 27-ledger-tests-and-harness*
*Completed: 2026-10-20*
