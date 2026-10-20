---
phase: 27-ledger-tests-and-harness
reviewed: 2026-10-20T00:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - tests/process_group.py
  - tests/test_browser_pins.py
  - tests/test_process_group.py
findings:
  critical: 0
  warning: 1
  info: 7
  total: 8
status: issues_found
---

# Phase 27: Code Review Report

**Reviewed:** 2026-10-20
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Summary

Incremental re-review of `git diff a4091f9..HEAD` on the three test-harness files, the fix commits 5bf2a0f (WR-01), 2e724cf (WR-02) and 41212d5 (WR-03). Ran `.venv/bin/python -m pytest tests/test_browser_pins.py tests/test_process_group.py --no-cov -q`: 15 passed. I also probed `_problems` (old and new) with `python -I` against hand-written sources.

Prior findings:

- **Prior WR-01 (environ allowance walked the whole compound statement): closed for the reported cases.** The `if`-header, default-argument and `except`-header reproductions now report one problem each, and the legitimate scrub shape still passes. The new climb introduced a regression, see WR-04 below, and leaves a narrower residual gap, see IN-07.
- **Prior WR-02 (teardown left the scan set): closed.** `process_group.py` is in `_scan_set`, the main pin asserts it, and a tmp-tree test with a `pytest.skip` in that module reports exactly one problem at `process_group.py:5`. The real module is clean under the widened scan.
- **Prior WR-03 (reader failure skipped SIGKILL and the reap): closed.** `except` now covers `CalledProcessError`, `TimeoutExpired`, `OSError` and `ValueError`. `ps` runs with `timeout=PS_BOUND_S`, and `subprocess.run` kills the child on timeout before raising. I traced the loop: a failed read in the SIGTERM phase goes straight to SIGKILL, and a successful read in the SIGKILL phase resets `survivors`, so the "unknown" failure is raised only when the last read failed. Reap and both failure messages are unchanged. The parametrized rows and the timeout test match the code.

One new defect from the WR-01 fix; no Critical findings. Info findings IN-01 to IN-06 from the prior review are carried forward unchanged in substance (IN-01 and IN-02 have shifted line numbers; the other four are in files this diff did not touch).

## Warnings

### WR-04: The WR-01 fix makes `_problems` raise `KeyError` on a module-level `from os import environ`

**File:** `tests/test_browser_pins.py:119-122`
**Issue:** `ast.ImportFrom` is itself an `ast.stmt`, and the loop now tests `parents[expression]` rather than `expression`. For an `environ` import at module level, the node's parent is the `ast.Module`, which is not in `clause`, so the loop climbs to the `Module`, then looks up `parents[Module]` and raises `KeyError`. Reproduced with `python -I`:

```
_problems("x.py", "from os import environ\n")  -> KeyError: <ast.Module ...>   (new code)
                                                -> ['x.py:1: `environ` in ...']  (a4091f9)
_problems("x.py", "def f():\n    from os import environ\n") -> one problem (both)
```

The pin still goes red, so nothing passes silently. But the scan aborts on the first such file, so every other problem in the scan set is hidden, and the failure message is a bare `KeyError` instead of the "a path that passes without the browser (D-02)" report. A top-level `from os import environ` is the most natural way for a future edit to introduce this read, and the old code reported it. No test row covers an `ImportFrom`.
**Fix:** Stop at a node that is already a statement, then climb:

```python
expression: ast.AST = node
while not isinstance(expression, ast.stmt) and not isinstance(parents[expression], clause):
    expression = parents[expression]
```

Add a row `'from os import environ\n'` to the self-test expecting one problem (an `ImportFrom` holds no marker constant, so it is always reported).

## Info

### IN-01: `_sleeper` sends `killpg` to a pid its own test already reaped

**File:** `tests/test_process_group.py:38-43`
**Issue:** After `stop_group` has called `proc.wait`, the fixture's `finally` still runs `os.killpg(proc.pid, SIGKILL)`. `stop_group`'s docstring says a reaped leader's pid can be reused and a group signal could then reach an unrelated group. The same hazard is reintroduced here, in test code. The window is tiny, but the guard is one line. (Carried forward from the prior review; line numbers updated, finding unchanged.)
**Fix:** `if proc.returncode is None:` before the `killpg`, keeping the final `subprocess.Popen.wait(proc, timeout=5)`.

### IN-02: `_instrument` records `poll` events that `stop_group` never produces, and test 1 asserts only `events[0]`

**File:** `tests/test_process_group.py:46-75, 86-88`
**Issue:** `stop_group` calls `proc.wait` but never `proc.poll`, so the `poll` recorder is dead. The first test's name promises "before `ps` is read or the leader reaped", and it checks only `events[0] == "signal SIGTERM"`. That is sufficient for the stated order, but the `poll`/`wait` instrumentation adds nothing a reader can rely on. (Carried forward; line numbers updated.)
**Fix:** Drop the `poll` wrapper, or assert the positions that matter, e.g. `events.index("wait") > events.index("signal SIGTERM")`.

### IN-03: `_page_string` in `test_selector.py` is a second copy of `_js_number`, and the copy's new guard and `-0` rule are untested

**File:** `tests/test_selector.py:226-239`
**Issue:** Both copies gained the same range assert and `+ 0`. The browser module's copy is covered by `test_the_oracle_reads_a_link_as_the_page_does` (the `-0.0` row, the `1e21` and `1e-7` raises). The selector copy has no test, so the two can drift apart silently. The assert message also misreports non-finite input: `nan` or `inf` fails the range test and gets "JavaScript writes this with an exponent". (Carried forward unchanged; file not in this diff.)
**Fix:** One row each for `-0.0` and an out-of-range value against `_page_string`. Optionally replace the `assert` with `math.isfinite(number)` first, so the message is right.

### IN-04: Nothing pins that `_build` passes its own `rm` to `_chamfer_tips`

**File:** `tests/test_model.py:899, 926, 976` (with `src/spur/model.py:640, 783`)
**Issue:** The point of 19-REVIEW IN-01 is that the chamfer limit reads the curve the part was cut from and does not solve it again. The updated monkeypatches (`lambda solid, _p, _pr, _rm: solid`, `lambda _p, _rm=None: ...`) accept either calling shape, so reverting `_chamfer_tips` to `tip_chamfer_effective(p)` would leave every test green. The change is correct today, but unguarded. (Carried forward unchanged.)
**Fix:** One test that patches `spur.model.root_mode` with a counting wrapper and asserts a single call per `_build`, or patches `tip_chamfer_effective` with `lambda _p, rm: seen.append(rm)` and asserts `seen[0] is not None`.

### IN-05: `test_the_host_state_reads_unknown_where_git_cannot_name_head` patches the process-wide `subprocess.run`

**File:** `tests/test_bench.py:1084`
**Issue:** `monkeypatch.setattr("bench.trochoid_part.subprocess.run", no_head)` resolves through the `subprocess` module object, so it replaces `subprocess.run` for every caller while the test runs, not only the bench module. It is safe now because `_host_state` calls `run` only for `git`, but any later `subprocess.run` in `_host_state` (or a fixture) would get the failure for the wrong reason. (Carried forward unchanged. The new `test_ps_is_run_with_a_timeout` in `tests/test_process_group.py:127` does the same and notes it in a comment; it is safe there because the patched window holds one call.)
**Fix:** Patch `bench.trochoid_part.subprocess` with a `types.SimpleNamespace(run=no_head, CalledProcessError=subprocess.CalledProcessError)`, or accept the global patch and say so in a comment.

### IN-06: The `Resolved in:` fields of the five resolved debt items hold commit subjects, not shas

**File:** `docs/tech_debt/resolved/2026-10-10-group-floor-of-3-is-not-two-pool-workers.md:5` and the four sibling files
**Issue:** `CLAUDE.md` says to "add the commit sha" on resolve. The INDEX rows say "see the file's own `Resolved in:` field", which then gives a subject line. A subject is not stable if the commits are rebased or squashed, and it cannot be used with `git show`. (Some older resolved rows in the INDEX already use subjects, so this follows precedent. It is still weaker than the rule.) (Carried forward unchanged.)
**Fix:** After the fix commits land, replace each subject with the short sha in a follow-up `docs` commit.

### IN-07: The climb stops at `arguments`, so one default argument's marker allows another default's `environ` read

**File:** `tests/test_browser_pins.py:119-127`
**Issue:** The WR-01 fix ends the climb under the statement, but a default argument's parent is the `ast.arguments` node, which holds every default, annotation and keyword-only default of the function. The "expression" searched for a marker is then the whole parameter list. Reproduced: `def f(a=os.environ.get("SKIP"), b="SPUR_"): pass` returns `[]`, as do the `lambda a=os.environ["S"], b="SPUR_": 0` and annotation forms. The same width exists for any sibling inside one expression (`{"a": os.environ["S"], "b": "SPUR_"}`, `f(os.environ["S"], "SPUR_")`); that one is inherent to a marker-in-expression rule and the module docstring already calls the pin a tripwire. The `arguments` case is different only in that the two things are not one expression to a reader. It is unlikely to occur by accident.
**Fix:** Optional. Also stop the climb when the parent is `ast.arguments`, so the unit is the single default expression (`expression` is then the default value or annotation itself). Or say in the module docstring that the unit is the statement's top-level child expression, which may span a whole parameter list.

---

_Reviewed: 2026-10-20_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
