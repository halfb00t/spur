---
phase: 27-ledger-tests-and-harness
fixed_at: 2026-10-20T00:00:00Z
review_path: .planning/phases/27-ledger-tests-and-harness/27-REVIEW.md
iteration: 1
findings_in_scope: 7
fixed: 6
skipped: 1
status: partial
---

# Phase 27: Code Review Fix Report

**Fixed at:** 2026-10-20
**Source review:** .planning/phases/27-ledger-tests-and-harness/27-REVIEW.md
**Iteration:** 1 (this is the Info-scope pass, `fix_scope: all`, as numbered by the orchestrator; the earlier WR-01..WR-04 reports this file replaced were committed already and are not repeated here)

**Summary:**
- Findings in scope: 7 (IN-01 to IN-07; no Critical or Warning findings open)
- Fixed: 6
- Skipped: 1 (IN-04)

**Verification ran in the main checkout** (`workflow.use_worktrees` is `false`, so no worktree was created). Each fix was checked with the affected test file, `ruff check` and `mypy --strict` on that file before its commit; the commit hook then ran `make verify.fast` (Passed every time). Final gate, run once the last commit landed:

```
make verify
======================= 1346 passed in 225.37s (0:03:45) =======================
Required test coverage of 96.0% reached. Total coverage: 97.99%
```

Exit status 0. (`make verify` was in fact run twice at the end, the first time through a `tail` that hid the exit code; both runs read 1346 passed.)

## Fixed Issues

### IN-01: `_sleeper` sends `killpg` to a pid its own test already reaped

**Files modified:** `tests/test_process_group.py`
**Commit:** c22742e
**Applied fix:** The fixture's `killpg` now runs only while `proc.returncode is None`, with a comment saying why; the final class-level `wait` is kept. The same pid-reuse hazard `stop_group` guards against is no longer reintroduced in test code.

### IN-02: `_instrument` records `poll` events that `stop_group` never produces

**Files modified:** `tests/test_process_group.py`
**Commit:** d7426e0
**Applied fix:** Confirmed with grep that `tests/process_group.py` calls `proc.wait` and never `proc.poll`, then dropped the `poll` wrapper, its `monkeypatch.setattr` and the word "poll" in the docstring. The review's first option (drop the dead recorder) was the simpler of the two; the existing `events[0] == "signal SIGTERM"` assertion already carries the stated order.

### IN-03: `_page_string` in `test_selector.py` is an untested copy of `_js_number`

**Files modified:** `tests/test_selector.py`
**Commit:** d91ce2f
**Applied fix:** Added `test_the_page_string_reads_a_number_as_the_page_does` with the rows that pin the original in `tests/test_browser.py` (`-0.0` to `0`, `1.0`, `0.05`, `1e-6`, `1e16`, and the `1e21` and `1e-7` raises). The optional `math.isfinite` message change was not made: no caller passes `nan` or `inf`, and it would edit the function rather than pin it.

### IN-05: `test_the_host_state_reads_unknown_where_git_cannot_name_head` patches the process-wide `subprocess.run`

**Files modified:** `tests/test_bench.py`
**Commit:** c8cf8b4
**Applied fix:** The test now replaces `bench.trochoid_part.subprocess` with a `types.SimpleNamespace(run=no_head, CalledProcessError=...)` instead of patching `.run` on the shared module, so no other `subprocess.run` caller sees the failure. Chose this over the comment-only option because it is a three-line change that removes the hazard.

### IN-06: `Resolved in:` fields of five resolved debt items hold commit subjects, not shas

**Files modified:** `docs/tech_debt/INDEX.md` and the five files under `docs/tech_debt/resolved/`: `2026-10-10-group-floor-of-3-is-not-two-pool-workers.md`, `2026-10-10-launch-failure-message-names-a-stamp-that-skips-the-install.md`, `2026-10-10-stop-group-reads-ps-before-it-signals.md`, `2026-10-15-failed-build-name-test-depends-on-cache-order.md`, `2026-10-15-slug-totality-is-not-guarded-in-the-gate.md`
**Commit:** 0fd2b98
**Applied fix:** Each sha was resolved with `git log --grep` on the exact subject (one hit each), and checked with `git show --name-status` to be the commit that renamed that item from `active/` to `resolved/`:

| Item | sha |
|---|---|
| group floor of 3 | `99e2b7d` |
| launch failure message | `a393e50` |
| `stop_group` reads `ps` first | `a7c5f78` |
| failed-build name test | `c47bfc4` |
| `slug()` totality | `345ee08` |

The five INDEX rows now read `` `sha` — see the file's own `Resolved in:` field ``, the same shape as the environ-pin row.

### IN-07: The climb stops at `arguments`, so one default argument's marker allows another default's `environ` read

**Files modified:** `tests/test_browser_pins.py`
**Commit:** 782fe9f
**Applied fix:** `ast.arguments` joins the node types the climb stops under, so the searched unit is the single default expression. Two rows added to the existing compound-statement test (a `def` and a `lambda`, each with a read in one default and `"SPUR_"` in another); with the one-token change reverted both rows fail, and with it all 13 tests in the file pass. Chose this over the docstring-only option because the code change is one token and the docstring option would document a known gap.
**Status note:** a logic change to the pin's own scan, so it carries "fixed: requires human verification" in the strict reading of the fixer rules. The scan is a test helper only; nothing printed to users depends on it.

## Skipped Issues

### IN-04: Nothing pins that `_build` passes its own `rm` to `_chamfer_tips`

**File:** `tests/test_model.py:899, 926, 976` (with `src/spur/model.py:640, 783`)
**Reason:** Both suggested fixes assert an internal call: a counting wrapper on `spur.model.root_mode` is an internal call count, and a stand-in on `tip_chamfer_effective` that checks `seen[0] is not None` asserts a private argument. `docs/CODING_VALUES.md` (Testing) bans "asserting private calls or internal call counts". The result is the same either way, because `tip_chamfer_effective(p)` re-derives the same `rm`, so there is no behavior a test could see; the cost of reverting is a second root solve, a performance matter that the rule says is measured, not asserted. Skipped rather than forcing a test the project's own standard rejects.
**Original issue:** The updated monkeypatches accept either calling shape, so reverting `_chamfer_tips` to `tip_chamfer_effective(p)` would leave every test green.

## Notes for the orchestrator

- No new problems found; no tech-debt item filed (none of the above is real debt beyond what is listed).
- IN-06 was scoped to the five Phase 27 items the review named. Nine older resolved items (phase 26 and earlier) still hold commit subjects: `2026-10-15-twin-selectors-step-reds-main.md`, `2026-10-06-resource-tracker-flake-fails-the-gate.md`, `2026-10-05-intel-context-repeats-superseded-figures.md`, `2026-10-05-no-fake-done-scan-is-blind-on-macos.md`, `2026-10-10-hook-pin-reads-the-callers-pytest-args.md`, `2026-10-11-hex-bore-warns-about-default-bore-fields.md`, `2026-10-20-pr-land-merges-a-stale-head.md`, `2026-10-15-twin-selectors-fix-awaits-the-post-merge-main-read.md`, and `2026-10-10-test-image-collects-tests-that-read-host-files.md`. They are outside this phase's review and were left alone.
- The active item `docs/tech_debt/active/2026-10-05-resolved-in-shas-point-at-squashed-branch-commits.md` already records that branch-commit shas stop being ancestors of `main` after the squash-merge (L22, L25). The five new shas are branch commits and are subject to that same caveat; they resolve on this branch and through the PR head ref.
- A slip while checking IN-07: a `git checkout --` on `tests/test_browser_pins.py` (used to undo a deliberate revert for the red check) also dropped the uncommitted fix; it was restored byte for byte from a backup copy before the commit. The committed state is the intended one.

---

_Fixed: 2026-10-20_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
