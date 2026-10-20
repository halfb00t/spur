---
phase: 27-ledger-tests-and-harness
reviewed: 2026-10-20T00:00:00Z
depth: standard
files_reviewed: 23
files_reviewed_list:
  - bench/RESULTS.md
  - bench/trochoid_part.py
  - docs/architecture/decision_log.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md
  - docs/tech_debt/resolved/2026-10-10-group-floor-of-3-is-not-two-pool-workers.md
  - docs/tech_debt/resolved/2026-10-10-launch-failure-message-names-a-stamp-that-skips-the-install.md
  - docs/tech_debt/resolved/2026-10-10-stop-group-reads-ps-before-it-signals.md
  - docs/tech_debt/resolved/2026-10-15-failed-build-name-test-depends-on-cache-order.md
  - docs/tech_debt/resolved/2026-10-15-slug-totality-is-not-guarded-in-the-gate.md
  - src/spur/model.py
  - tests/browser_session.py
  - tests/composition.py
  - tests/process_group.py
  - tests/test_api.py
  - tests/test_bench.py
  - tests/test_browser.py
  - tests/test_browser_pins.py
  - tests/test_model.py
  - tests/test_process_group.py
  - tests/test_relations.py
  - tests/test_selector.py
  - tests/test_trochoid.py
findings:
  critical: 0
  warning: 3
  info: 6
  total: 9
status: issues_found
---

# Phase 27: Code Review Report

**Reviewed:** 2026-10-20
**Depth:** standard
**Files Reviewed:** 23
**Status:** issues_found

## Summary

Reviewed the diff from `deb7c23` to HEAD. Ran `.venv/bin/python -m ruff check .` (all checks passed), `.venv/bin/python -m mypy src tests docker bench scripts` (no issues in 51 files), and the changed tests directly (`test_process_group`, `test_browser_pins`, `test_selector`, `test_relations`: 82 passed; the `slug`, `download_name`, `host_state`, `failed_build`, `openapi` and `tip_chamfer` selections: 40 passed). I did not run the full `make verify`.

The production change (`model.py`: `_chamfer_tips` takes `_build`'s `rm`) is correct. `tip_chamfer_effective(p, rm)` and `tip_chamfer_limit(p, rm)` accept `rm`, and `_build` solves `rm` with the same arguments the default path would use. No Critical findings. The weaknesses are in the new test tripwires: the `_problems` allowance in `test_browser_pins.py` is wider than the stated rule, the move of the teardown shrank the scanned surface, and `stop_group` still has a failure path that skips the signals. The stated purpose of those tripwires is that a green gate cannot lie.

## Warnings

### WR-01: `_problems` environ allowance walks a compound statement's whole body, so the new "own statement" rule is bypassable

**File:** `tests/test_browser_pins.py:96-108`
**Issue:** The rule is documented as "a marker constant in the read's own statement". The code climbs from the `environ` node to the nearest `ast.stmt` and then runs `ast.walk(statement)` over it. When the read sits in the header of a compound statement (`if`, `while`, `with`, `for`, or a `def`'s default arguments or decorators), that statement includes its entire body. Any `"SPUR_"` or `"PLAYWRIGHT_BROWSERS_PATH"` constant anywhere in the body then allows the read. I reproduced both cases against the committed function with `python -I`:

```
_problems("c.py", 'import os\nif os.environ.get("CI_NO_BROWSER"):\n    x = "SPUR_"\n')  -> []
_problems("d.py", 'import os\ndef f(a=os.environ.get("SKIP")):\n    """d"""\n    return "PLAYWRIGHT_BROWSERS_PATH"\n') -> []
```

Both should be reported. The new self-test (`test_an_environ_read_is_allowed_by_its_statement_not_its_line`) covers only the comment case and the wrapped-assignment case, so it does not see this.
**Fix:** Stop the climb at the expression that is a direct child of a statement, and look for markers only inside that expression:

```python
node_expr: ast.AST = node
while not isinstance(parents[node_expr], ast.stmt):
    node_expr = parents[node_expr]
if any(isinstance(c, ast.Constant) and c.value in ALLOWED_ENVIRON_MARKERS
       for c in ast.walk(node_expr)):
    continue
```

For a header read such as `x = {k: v for k, v in os.environ.items() if not k.startswith("SPUR_")}`, the top expression is the comprehension, which holds the marker, so the legitimate scrub still passes. Add the two reproductions above as rows in the self-test.

### WR-02: Moving the teardown to `tests/process_group.py` took it out of the pin's scan set

**File:** `tests/test_browser_pins.py:50-55`, `tests/process_group.py`
**Issue:** `_scan_set()` globs `tests/*browser*.py` plus `capture_requests.py`. Before this phase, `stop_group`, `group_members` and `_signal_group` lived in `browser_session.py`, so a `pytest.skip`, `xfail` or `environ` read added to them failed the pin. After the move they live in `tests/process_group.py`, which no longer matches the glob. The teardown runs in the browser test's fixture (`serve()`), so a skip spelling there can still turn the browser test into a pass without it running. That is the exact lie this file exists to catch. The module docstring and `RESULTS.md` do not mention the narrowed scope.
**Fix:** Add the module to the set, e.g. `found.add(REPO_ROOT / "tests" / "process_group.py")` beside `capture_requests.py`, and extend the docstring. The module should be clean already: it has no skip spelling and no `environ` read.

### WR-03: `stop_group` still lets a failure in the reader skip SIGKILL and the reap

**File:** `tests/process_group.py:64-74` (with `group_members`, lines 36-48)
**Issue:** The fix's stated invariant is "a reader that fails must not stop the signals (the orphan T-21-02)". The `except` catches only `CalledProcessError` and `OSError`. `group_members` also does `int(fields[0])` and `int(fields[2])` on `ps` output, so a `ValueError` (an unexpected row on some `ps` implementation) propagates out of the loop after SIGTERM only. SIGKILL is never sent and `proc.wait` never runs. The group can then be left alive, the leader unreaped, and the test reports an unrelated `ValueError`. `ps` is also run with no timeout, so a hung `ps` blocks the teardown indefinitely after SIGTERM.
**Fix:** Cover the whole read, and bound it:

```python
except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError, ValueError):
    survivors = None
    continue
```

and pass `timeout=5` to the `ps` call in `group_members`. Alternatively, wrap the loop in `try/finally` so the SIGKILL and the reap always run.

## Info

### IN-01: `_sleeper` sends `killpg` to a pid its own test already reaped

**File:** `tests/test_process_group.py:36-40`
**Issue:** After `stop_group` has called `proc.wait`, the fixture's `finally` still runs `os.killpg(proc.pid, SIGKILL)`. `stop_group`'s docstring says a reaped leader's pid can be reused and a group signal could then reach an unrelated group. The same hazard is reintroduced here, in test code. The window is tiny, but the guard is one line.
**Fix:** `if proc.returncode is None:` before the `killpg`, keeping the final `subprocess.Popen.wait(proc, timeout=5)`.

### IN-02: `_instrument` records `poll` events that `stop_group` never produces, and test 1 asserts only `events[0]`

**File:** `tests/test_process_group.py:46-72, 87-91`
**Issue:** `stop_group` calls `proc.wait` but never `proc.poll`, so the `poll` recorder is dead. The first test's name promises "before `ps` is read or the leader reaped", and it checks only `events[0] == "signal SIGTERM"`. That is sufficient for the stated order, but the `poll`/`wait` instrumentation adds nothing a reader can rely on.
**Fix:** Drop the `poll` wrapper, or assert the positions that matter, e.g. `events.index("wait") > events.index("signal SIGTERM")`.

### IN-03: `_page_string` in `test_selector.py` is a second copy of `_js_number`, and the copy's new guard and `-0` rule are untested

**File:** `tests/test_selector.py:226-239`
**Issue:** Both copies gained the same range assert and `+ 0`. The browser module's copy is covered by `test_the_oracle_reads_a_link_as_the_page_does` (the `-0.0` row, the `1e21` and `1e-7` raises). The selector copy has no test, so the two can drift apart silently. The assert message also misreports non-finite input: `nan` or `inf` fails the range test and gets "JavaScript writes this with an exponent".
**Fix:** One row each for `-0.0` and an out-of-range value against `_page_string`. Optionally replace the `assert` with `math.isfinite(number)` first, so the message is right.

### IN-04: Nothing pins that `_build` passes its own `rm` to `_chamfer_tips`

**File:** `tests/test_model.py:899, 926, 976` (with `src/spur/model.py:640, 783`)
**Issue:** The point of 19-REVIEW IN-01 is that the chamfer limit reads the curve the part was cut from and does not solve it again. The updated monkeypatches (`lambda solid, _p, _pr, _rm: solid`, `lambda _p, _rm=None: ...`) accept either calling shape, so reverting `_chamfer_tips` to `tip_chamfer_effective(p)` would leave every test green. The change is correct today, but unguarded.
**Fix:** One test that patches `spur.model.root_mode` with a counting wrapper and asserts a single call per `_build`, or patches `tip_chamfer_effective` with `lambda _p, rm: seen.append(rm)` and asserts `seen[0] is not None`.

### IN-05: `test_the_host_state_reads_unknown_where_git_cannot_name_head` patches the process-wide `subprocess.run`

**File:** `tests/test_bench.py:1084`
**Issue:** `monkeypatch.setattr("bench.trochoid_part.subprocess.run", no_head)` resolves through the `subprocess` module object, so it replaces `subprocess.run` for every caller while the test runs, not only the bench module. It is safe now because `_host_state` calls `run` only for `git`, but any later `subprocess.run` in `_host_state` (or a fixture) would get the failure for the wrong reason.
**Fix:** Patch `bench.trochoid_part.subprocess` with a `types.SimpleNamespace(run=no_head, CalledProcessError=subprocess.CalledProcessError)`, or accept the global patch and say so in a comment.

### IN-06: The `Resolved in:` fields of the five resolved debt items hold commit subjects, not shas

**File:** `docs/tech_debt/resolved/2026-10-10-group-floor-of-3-is-not-two-pool-workers.md:5` and the four sibling files
**Issue:** `CLAUDE.md` says to "add the commit sha" on resolve. The INDEX rows say "see the file's own `Resolved in:` field", which then gives a subject line. A subject is not stable if the commits are rebased or squashed, and it cannot be used with `git show`. (Some older resolved rows in the INDEX already use subjects, so this follows precedent. It is still weaker than the rule.)
**Fix:** After the fix commits land, replace each subject with the short sha in a follow-up `docs` commit.

---

_Reviewed: 2026-10-20_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
