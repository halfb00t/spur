---
phase: 21-browser-test-of-the-viewer
reviewed: 2026-10-10T00:00:00Z
depth: standard
files_reviewed: 22
files_reviewed_list:
  - .github/workflows/ci.yml
  - .gitignore
  - .pre-commit-config.yaml
  - bench/RESULTS.md
  - docs/architecture/decision_log.md
  - docs/architecture/web-ui.md
  - docs/ideas/INDEX.md
  - docs/ideas/retired/2026-09-21-browser-test-for-the-viewer.md
  - docs/tech_debt/active/2026-10-10-hook-pin-reads-the-callers-pytest-args.md
  - docs/tech_debt/active/2026-10-10-root-shape-bogus-loads-a-blank-select.md
  - docs/tech_debt/active/2026-10-10-test-image-collects-tests-that-read-host-files.md
  - docs/tech_debt/active/2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md
  - docs/tech_debt/INDEX.md
  - Makefile
  - pyproject.toml
  - src/spur/static/app.js
  - tests/browser_session.py
  - tests/capture_requests.py
  - tests/regression/golden_requests.json
  - tests/test_browser_pins.py
  - tests/test_browser.py
  - tests/test_hooks.py
findings:
  critical: 0
  warning: 3
  info: 4
  total: 7
status: issues_found
---

# Phase 21: Code Review Report

**Reviewed:** 2026-10-10
**Depth:** standard
**Files Reviewed:** 22
**Status:** issues_found

## Summary

The phase adds a headless-browser scenario test plus its session helper, a golden-request
regenerator, pins, Makefile/CI wiring, and a one-line product change (`canvas.dataset.triangles`).
I read every executable file and ran `tests/test_browser_pins.py tests/test_hooks.py
tests/test_browser.py -n0 --no-cov -q` on the dev host: 10 passed in 3.95 s, group members before
the kill 3.

Checked and found sound: process-group teardown ordering (`finally` inside `finally`, leader reaped
after the group scan so the pgid cannot be recycled); `SPUR_*` scrub; the pre-bound socket passed by
`--fd` (loopback only, kernel-assigned port); no skip/xfail/importorskip path (the `launch` failure is
`pytest.fail`, and the AST pin covers the common spellings); `capture_requests.py` writes only
`GOLDEN_PATH`; playwright is dev-only; the `-o` dry-run fix and the `test`/`test.fast`/`test-image`
exclusions are consistent with `HEAVY_TEST_FILES`; `time.sleep(0.05)` in `stop_group` is a poll on a
real condition with a bound; the `floor_applies` deviation is sound (it only skips the floor when the
test already failed, and survivors are still checked either way).

No security issue and no correctness bug that makes the browser test pass without the browser.
Defects are in teardown robustness, a factually wrong invariant description that the records repeat,
and the remediation message of a missing shell.

## Warnings

### WR-01: `stop_group` can leak the whole server group if `ps` fails

**File:** `tests/browser_session.py:116` (also `:121`, `:124`)
**Issue:** `stop_group` begins with `survivors = group_members(pgid)` before any signal is sent.
`group_members` runs `ps` with `check=True` and parses with `int()`. If `ps` is missing or exits
non-zero (a minimal container, a sandbox, a transient failure), `CalledProcessError` propagates out of
`stop_group` before `os.killpg(SIGTERM)` is reached, so uvicorn, the resource tracker and the pool
worker outlive the test run. The same exception after the SIGTERM (line 121) skips the SIGKILL
escalation. The first assignment is also dead: the loop overwrites it before use (line 121). Teardown
that cannot kill is the one failure this helper exists to prevent.
**Fix:** Signal first, scan second, and never let a scan failure stop the kill:
```python
def stop_group(proc, log):
    pgid = proc.pid
    survivors: list[int] = []
    bound = TERM_BOUND_S
    for sig, bound in ((signal.SIGTERM, TERM_BOUND_S), (signal.SIGKILL, KILL_BOUND_S)):
        _signal_group(pgid, sig)
        deadline = time.monotonic() + bound
        while True:
            survivors = group_members(pgid)
            if not survivors or time.monotonic() >= deadline:
                break
            time.sleep(0.05)
        if not survivors:
            break
    ...
```
and, in the `finally` of `serve`, call `_signal_group(proc.pid, signal.SIGKILL)` if the scan raises, so
a broken `ps` still ends in a dead group (and a loud failure).

### WR-02: `MIN_GROUP_MEMBERS` is documented as "uvicorn plus 2 workers"; the 3 members are uvicorn, the resource tracker and ONE worker

**File:** `tests/browser_session.py:49-51` (and `:162-166`); repeated in `bench/RESULTS.md:4768`, `:4817`, `:4902`
**Issue:** I started the server through `serve()` and listed its group with `ps`. After `/api/health`
the group is uvicorn plus `multiprocessing.resource_tracker` (2 members). After one preview build it is
those two plus a single `multiprocessing.spawn` worker (3 members); a second build on a different
gear did not add a fourth (`BuildPool` holds two single-worker executors and `executor_for` picks one
per gear, each spawning on first use). So the comment "uvicorn plus the shipped pool of 2 workers", the
RESULTS rows "3 (uvicorn and two pool workers)" and "the two pool workers were killed by group id
afterwards" are wrong, and the floor of 3 proves "uvicorn, tracker and at least one worker", not that
the shipped pool of two ran. The floor still does its stated job (a post-kill zero is not a blind
reader), but the records state a measurement that was not what was seen, in a project whose rule is
that recorded numbers be honest. The `SPUR_*` scrub, not this floor, is what keeps the pool at the
default.
**Fix:** Correct the comment and the three RESULTS rows to "uvicorn, the multiprocessing resource
tracker and the one pool worker the first build spawned". If the test is meant to evidence two
workers, drive a second build that lands on the other executor and raise the floor to 4.

### WR-03: A missing-shell failure tells the reader `make test` will fix it, but a current `$(BROWSER)` stamp makes `make test` do nothing

**File:** `tests/browser_session.py:216-221`, `Makefile:91-93`
**Issue:** `launch()` says "`make test` runs the install stamp for you" for every `playwright.Error`.
`$(BROWSER)` depends only on `$(STAMP)` (pyproject.toml). If `.venv/ms-playwright` is deleted, partly
downloaded, or on a different revision than the stamp, `.venv/.browser` still exists, so `make test`
skips the install and fails again with the same message. The text also misdiagnoses unrelated launch
failures (missing system libraries on a Linux dev host need `--with-deps`, not a reinstall) as "not
installed".
**Fix:** Make the message accurate and actionable, e.g. "run `rm .venv/.browser && make test`
(Linux hosts missing system libraries: `make test BROWSER_INSTALL_ARGS=--with-deps`)", and print
`Playwright said:` first so a library error is not hidden behind the install advice. Optionally make
the stamp recipe check `$(PLAYWRIGHT_BROWSERS_PATH)` exists, e.g. `$(BROWSER): $(STAMP)` plus
`rm -f $(BROWSER)` when the directory is absent.

## Info

### IN-01: Dead assignment and misleading bound in the survivor failure message

**File:** `tests/browser_session.py:117-118`, `:130-133`
**Issue:** `bound = TERM_BOUND_S` is overwritten by the loop target on line 118. When both signals ran,
the message reads "after SIGTERM, SIGKILL and 5 s", naming only the SIGKILL bound.
**Fix:** Drop line 117; format the message with `TERM_BOUND_S` and `KILL_BOUND_S`.

### IN-02: `fixture_hash` accepts non-string scalars it would encode wrongly

**File:** `tests/browser_session.py:298-307`, `:310-328`
**Issue:** `str(value)` turns a JSON `true`/`null` into `True`/`None`, which no person would type into
a link. Today the fixture holds only int, float and str (checked), so nothing is wrong; a future
bool-valued field would silently pin a wrong query in `golden_requests.json`.
**Fix:** In `fixture_hashes`, assert `isinstance(value, int | float | str) and not isinstance(value, bool)`
per param.

### IN-03: The "no path that passes without the browser" scan is line-based and spelling-based

**File:** `tests/test_browser_pins.py:96-101`, `:36-40`
**Issue:** The `environ` allowance is granted by any marker substring on the node's first line, so
`os.environ["X"]  # SPUR_` passes, and a multi-line `os.environ.get(\n "PLAYWRIGHT_BROWSERS_PATH")`
fails falsely. Spellings such as `getattr(pytest, "skip")`, an empty `parametrize`, or a conditional
`return` before the first `step` are not seen. Today none exist; the pin is a tripwire, not a proof,
and its docstring ("no path that passes") reads stronger than it is.
**Fix:** Soften the docstring, or match on the string constant (`ast.Constant` equal to `"SPUR_"` /
`"PLAYWRIGHT_BROWSERS_PATH"` inside the `environ` call) instead of the source line.

### IN-04: Inconsistent waits and a hot loop in `test_browser.py`

**File:** `tests/test_browser.py:179`, `:245-255`
**Issue:** `_follow_link` waits with Playwright's default 30 s while every other request wait uses
`BUILD_WAIT_MS` (45 s), so under the CI starvation the constants document the same step can time out at
two different bounds. `_wait_until_parked` spins `page.evaluate("0")` with no pause; the comment
explains why a sleep cannot work, but the loop is unthrottled for up to 45 s.
**Fix:** Pass `timeout=BUILD_WAIT_MS` in `_follow_link`; give the park loop a cheap yield, e.g.
`page.wait_for_timeout(50)` (a Playwright round trip that also lets the route handler run).

---

_Reviewed: 2026-10-10_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
