---
phase: 27-ledger-tests-and-harness
reviewed: 2026-10-20T00:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/resolved/2026-10-20-environ-pin-raises-keyerror-on-module-level-import.md
  - tests/test_browser_pins.py
findings:
  critical: 0
  warning: 0
  info: 7
  total: 7
status: issues_found
---

# Phase 27: Code Review Report

**Reviewed:** 2026-10-20
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Summary

Incremental re-review of `git diff ebeffcf..HEAD` on the three files: the WR-04 fix (27628ef: the `_problems` climb stops at a node that is already an `ast.stmt`, plus `test_an_import_of_environ_is_reported_not_a_crash`) and the tech-debt resolve (27628ef, b9755ad). Ran `.venv/bin/python -m pytest tests/test_browser_pins.py --no-cov -q`: 11 passed. I probed `_problems` with `python -I` against hand-written sources.

Prior findings:

- **Prior WR-04 (module-level `from os import environ` raised `KeyError`): closed.** Reproduced the old failure shape against the new code and it now returns one problem: `from os import environ` -> `['x.py:1: `environ` in `from os import environ`']`. The aliased form (`as e`) and the in-function form also report one problem each. A marker constant on a later line does not allow the import (`from os import environ` then `x = "SPUR_"` -> still one problem), so the "an import is always reported" claim in the new test docstring holds. The two new test rows cover the module-level and in-function forms.
- **No regression in the WR-01 cases.** The `if`-header, default-argument and `except`-header sources still report one problem each (the parametrized test passes). The legitimate shapes still pass: the `SPUR_` scrub in an `if` header, and `os.environ.get("PLAYWRIGHT_BROWSERS_PATH")` in a plain assignment. `match`/`case`, decorator, `with` header and class-base reads are all still reported. The new `isinstance(expression, ast.stmt)` test only fires on a node that is itself a statement, which for the watched names can only be an `ImportFrom`; every `Attribute`/`Name` read still climbs exactly as before.
- **IN-07 behavior unchanged.** `def f(a=os.environ.get("S"), b="SPUR_"): pass` still returns `[]` (the climb ends under the `arguments` node, not at a statement). The fix neither widens nor narrows this; IN-07 stays open with its line range updated.
- **Debt move follows CLAUDE.md.** `Status: resolved`; `Resolved in: 27628ef` is a sha (an improvement on the subject-line fields in IN-06); the file sits in `docs/tech_debt/resolved/`; the INDEX row is in the Resolved table and there is no leftover row in Active (checked with grep) and no stale file in `active/`. The sha was named in a follow-up commit (b9755ad) because a commit cannot hold its own sha; that is unavoidable and consistent with the rule. The resolved file's `Related files:` line still cites `tests/test_browser_pins.py:119-122`, which is the pre-fix range; cosmetic for a closed item and not worth a finding.

No new Critical or Warning findings. Info findings IN-01 to IN-07 are carried forward unchanged in substance; the only change is IN-07's line range, which shifted with the added comment lines.

## Info

### IN-01: `_sleeper` sends `killpg` to a pid its own test already reaped

**File:** `tests/test_process_group.py:38-43`
**Issue:** After `stop_group` has called `proc.wait`, the fixture's `finally` still runs `os.killpg(proc.pid, SIGKILL)`. `stop_group`'s docstring says a reaped leader's pid can be reused and a group signal could then reach an unrelated group. The same hazard is reintroduced here, in test code. The window is tiny, but the guard is one line. (Carried forward; file not in this diff.)
**Fix:** `if proc.returncode is None:` before the `killpg`, keeping the final `subprocess.Popen.wait(proc, timeout=5)`.

### IN-02: `_instrument` records `poll` events that `stop_group` never produces, and test 1 asserts only `events[0]`

**File:** `tests/test_process_group.py:46-75, 86-88`
**Issue:** `stop_group` calls `proc.wait` but never `proc.poll`, so the `poll` recorder is dead. The first test's name promises "before `ps` is read or the leader reaped", and it checks only `events[0] == "signal SIGTERM"`. That is sufficient for the stated order, but the `poll`/`wait` instrumentation adds nothing a reader can rely on. (Carried forward; file not in this diff.)
**Fix:** Drop the `poll` wrapper, or assert the positions that matter, e.g. `events.index("wait") > events.index("signal SIGTERM")`.

### IN-03: `_page_string` in `test_selector.py` is a second copy of `_js_number`, and the copy's new guard and `-0` rule are untested

**File:** `tests/test_selector.py:226-239`
**Issue:** Both copies gained the same range assert and `+ 0`. The browser module's copy is covered by `test_the_oracle_reads_a_link_as_the_page_does` (the `-0.0` row, the `1e21` and `1e-7` raises). The selector copy has no test, so the two can drift apart silently. The assert message also misreports non-finite input: `nan` or `inf` fails the range test and gets "JavaScript writes this with an exponent". (Carried forward unchanged; file not in this diff.)
**Fix:** One row each for `-0.0` and an out-of-range value against `_page_string`. Optionally replace the `assert` with `math.isfinite(number)` first, so the message is right.

### IN-04: Nothing pins that `_build` passes its own `rm` to `_chamfer_tips`

**File:** `tests/test_model.py:899, 926, 976` (with `src/spur/model.py:640, 783`)
**Issue:** The point of 19-REVIEW IN-01 is that the chamfer limit reads the curve the part was cut from and does not solve it again. The updated monkeypatches (`lambda solid, _p, _pr, _rm: solid`, `lambda _p, _rm=None: ...`) accept either calling shape, so reverting `_chamfer_tips` to `tip_chamfer_effective(p)` would leave every test green. The change is correct today, but unguarded. (Carried forward unchanged; file not in this diff.)
**Fix:** One test that patches `spur.model.root_mode` with a counting wrapper and asserts a single call per `_build`, or patches `tip_chamfer_effective` with `lambda _p, rm: seen.append(rm)` and asserts `seen[0] is not None`.

### IN-05: `test_the_host_state_reads_unknown_where_git_cannot_name_head` patches the process-wide `subprocess.run`

**File:** `tests/test_bench.py:1084`
**Issue:** `monkeypatch.setattr("bench.trochoid_part.subprocess.run", no_head)` resolves through the `subprocess` module object, so it replaces `subprocess.run` for every caller while the test runs, not only the bench module. It is safe now because `_host_state` calls `run` only for `git`, but any later `subprocess.run` in `_host_state` (or a fixture) would get the failure for the wrong reason. (Carried forward unchanged. The `test_ps_is_run_with_a_timeout` test in `tests/test_process_group.py:127` does the same and notes it in a comment; it is safe there because the patched window holds one call.)
**Fix:** Patch `bench.trochoid_part.subprocess` with a `types.SimpleNamespace(run=no_head, CalledProcessError=subprocess.CalledProcessError)`, or accept the global patch and say so in a comment.

### IN-06: The `Resolved in:` fields of the five resolved debt items hold commit subjects, not shas

**File:** `docs/tech_debt/resolved/2026-10-10-group-floor-of-3-is-not-two-pool-workers.md:5` and the four sibling files
**Issue:** `CLAUDE.md` says to "add the commit sha" on resolve. The INDEX rows say "see the file's own `Resolved in:` field", which then gives a subject line. A subject is not stable if the commits are rebased or squashed, and it cannot be used with `git show`. (Some older resolved rows in the INDEX already use subjects, so this follows precedent. It is still weaker than the rule. The newest resolved item, the environ pin one, does use a sha, so the five older ones are now the outliers.) (Carried forward unchanged.)
**Fix:** After the fix commits land, replace each subject with the short sha in a follow-up `docs` commit.

### IN-07: The climb stops at `arguments`, so one default argument's marker allows another default's `environ` read

**File:** `tests/test_browser_pins.py:119-129`
**Issue:** The WR-01 fix ends the climb under the statement, but a default argument's parent is the `ast.arguments` node, which holds every default, annotation and keyword-only default of the function. The "expression" searched for a marker is then the whole parameter list. Reproduced again on the current code: `def f(a=os.environ.get("S"), b="SPUR_"): pass` returns `[]`, as do the `lambda a=os.environ["S"], b="SPUR_": 0` and annotation forms. The same width exists for any sibling inside one expression (`{"a": os.environ["S"], "b": "SPUR_"}`, `f(os.environ["S"], "SPUR_")`); that one is inherent to a marker-in-expression rule and the module docstring already calls the pin a tripwire. The `arguments` case is different only in that the two things are not one expression to a reader. It is unlikely to occur by accident.
**Fix:** Optional. Also stop the climb when the parent is `ast.arguments`, so the unit is the single default expression (`expression` is then the default value or annotation itself). Or say in the module docstring that the unit is the statement's top-level child expression, which may span a whole parameter list.

---

_Reviewed: 2026-10-20_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
