---
phase: 30-scope-seam-and-gear-safety-guard
reviewed: 2026-10-23T00:00:00Z
depth: standard
files_reviewed: 17
files_reviewed_list:
  - Makefile
  - pyproject.toml
  - scripts/gear_unchanged.py
  - src/spur/app.py
  - src/spur/model.py
  - src/spur/pool.py
  - src/spur/records.py
  - src/spur/parts.py
  - src/spur/shaft_params.py
  - src/spur/shaft_calc.py
  - src/spur/shaft_model.py
  - src/spur/din5480.py
  - src/spur/din5480_tables.py
  - tests/test_api.py
  - tests/test_gear_unchanged.py
  - tests/test_hooks.py
  - tests/test_seam.py
findings:
  critical: 0
  warning: 3
  info: 4
  total: 7
status: issues_found
---

# Phase 30: Code Review Report

**Reviewed:** 2026-10-23
**Depth:** standard
**Files Reviewed:** 17
**Status:** issues_found

## Summary

Reviewed the phase diff (`54f1842..HEAD`) for all 17 files. I ran the phase's own checks:
`make verify.static` is green (ruff, mypy, 10 import contracts kept, no-fake-done,
`gear.unchanged` reads "8723 bytes ... byte-equal to v0.6" in 0.44 s), and
`tests/test_seam.py`, `tests/test_gear_unchanged.py` and `tests/test_hooks.py` pass (29
passed). I found no correctness bug in the shipped gear path, and nothing here can change a
printed number or a gear link.

The weaknesses are in robustness. `gear.unchanged` can hang a hook, one test can flake, and
the `Part` seam claims more than it delivers.

**Orchestrator note (`_serve_model`, commit ca60285).** Verified. The docstring "Moved byte
for byte" is inaccurate, but behavior is unchanged.
- The diff shows `q.quality` replaced by a `quality` parameter at 10 sites.
- `params = _gear(q)` was lifted out of the body into the route.
- `_gear(q)` now runs before `request_id` is minted instead of after. That is unobservable,
  because `_gear` raises before any record is emitted in either order.
- `key`, `raw_key`, the slot, the error mapping, the records and the response headers are
  textually identical.
- The 503 wording change is in a separate commit (92fc0d4) and is pinned by a new test.
- The docstring is wrong as written, but there is no behavior defect (IN-01).

## Warnings

### WR-01: `gear.unchanged` runs git and a probe with no timeout and no prompt guard, in a hook that has hung before

**File:** `scripts/gear_unchanged.py:73-77, 89, 111-115`
**Issue:**
- `_git()` and `schema_of()` call `subprocess.run` with no `timeout`.
- `ensure_tag` runs `git fetch origin tag v0.6` whenever the tag is not local. Git can then
  block on a credential prompt, because stdin and the tty are not detached and
  `GIT_TERMINAL_PROMPT` is not set. A dead network can also wedge the fetch.
- This runs in `verify.static`, hence in the pre-commit hook. The hook's budget is the 30 s
  hard cap of gsd's SDK commit (L36), and the repo already carries a tech-debt item for a
  `make verify` hang (`docs/tech_debt/active/2026-10-10-make-verify-hung-...`).
- D-05 says a failed fetch must fail the gate. A hung fetch neither passes nor fails, which
  is worse than either.

**Fix:**
```python
def _git(root: Path, *args: str, timeout: float = 60) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "--no-optional-locks", *args], cwd=root, capture_output=True, check=False,
        stdin=subprocess.DEVNULL, timeout=timeout,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )
```
Catch `subprocess.TimeoutExpired` and raise `SystemExit("gear.unchanged: ... timed out")`.
Do the same for the probe in `schema_of`, which imports the whole app.

### WR-02: `test_the_check_leaves_the_repository_as_it_found_it` can flake on racy index entries

**File:** `tests/test_gear_unchanged.py:183-195`
**Issue:**
- The test reads `index_before` and only then runs `_git(work, "status", "--porcelain")`.
- The test's `_git` helper does not pass `--no-optional-locks`, so `status` may refresh and
  rewrite `.git/index`. Git does this for "racily clean" entries, where a file's mtime is not
  older than the index's. That happens on coarse-timestamp filesystems such as tmpfs or
  overlayfs, and the scratch repo was written and committed within milliseconds.
- If `status` rewrites the index, the final `index_before ==` assertion fails even though
  `check()` wrote nothing. The test can then blame the code under test for the test's own
  `git status`.

**Fix:** capture the index after the pre-check `status` call, so only `check()` sits between
the two reads:
```python
status_before = _git(work, "status", "--porcelain")
index_before = (work / ".git/index").read_bytes()
```
Alternatively, run the helper's status with `--no-optional-locks`.

### WR-03: `parts.py` promises a "one-line edit" widening; the gear-typed internals behind the seam make it false

**File:** `src/spur/parts.py:3-5` (with `src/spur/model.py:~795-835`, `src/spur/records.py:171`)
**Issue:**
- The docstring says Phase 31 "widens `Part` to `GearParams | ShaftParams` with a one-line
  edit here ... so none of those signatures is touched again".
- `model.build(p: Part)` and `model.export(p: Part)` pass `p` straight into
  `_build_cached` (`lru_cache` of `_build_checked(p: GearParams)`) and `_write_export(shape,
  p: GearParams, ...)`. Both internals are still typed `GearParams`.
- `records._gear_fields(p: Part)` reads gear-only attributes.
- Under `mypy --strict`, widening the alias will fail in those places, so the next phase has
  to touch more than one line.
- Today `Part = GearParams` makes the widened public signatures a documentation fiction. A
  `build(ShaftParams)` call would only fail at runtime inside `_build_checked`.

**Fix:** correct the docstring to say what widening will cost. Or, if the seam is meant to
be complete, type `_write_export`/`_build_checked` and the record helpers against `Part`
now. Do that in the same commit that introduces the alias, so the claim is true when
written.

## Info

### IN-01: `_serve_model` docstring says "Moved byte for byte"; it was not

**File:** `src/spur/app.py:385-393`
**Issue:** The body was edited at 10 `q.quality` sites and the `params = _gear(q)` line was
removed. Behavior is the same (see Summary), but this codebase's comments are its stated
asset (`docs/CODING_VALUES.md`, Vision), and an unverifiable "byte for byte" invites a
reviewer to skip the diff.
**Fix:** "Moved out of `model()` with `q.quality` replaced by the `quality` argument and
`_gear(q)` done by the caller; no other change."

### IN-02: `gear.unchanged` accepts any local `v0.6` tag, including a lightweight one made by mistake

**File:** `scripts/gear_unchanged.py:84-87`
**Issue:**
- `ensure_tag` only checks that `v0.6^{commit}` resolves. A developer who runs
  `git tag v0.6` on HEAD, or force-moves the tag, makes the check compare the tree with
  itself and read green forever.
- The module docstring calls the annotated tag "the one name for v0.6", but nothing checks
  that it is annotated.
- It also contradicts the module's own rule that the check "never passes without
  comparing".

**Fix:** require `git cat-file -t v0.6` to print `tag`, and fail with a message otherwise.

### IN-03: The docstring promises "every failure is a SystemExit"; four paths raise a traceback

**File:** `scripts/gear_unchanged.py:39, 73-77, 106, 119, 139`
**Issue:**
- These still exit nonzero, so nothing passes falsely. But they violate the stated contract
  and print no `gear.unchanged:` line.
- The paths are: `FileNotFoundError` when git is absent (the `test-image` comment records
  exactly this red); `UnicodeDecodeError` in `done.stdout.decode()` on a non-UTF-8 path;
  `ValueError` when the three-way unpack of probe stdout fails; `tarfile.FilterError` from
  `extractall(filter="data")`.
- `schema_of`'s non-zero-exit, non-200 and `baseline_src` failure branches have no test
  either; only the "imported spur from" and "empty" branches do.

**Fix:** wrap these in the same `SystemExit("gear.unchanged: ...")` pattern, and add one
test per branch with a stub probe or a fake `git`.

### IN-04: Both `shaft_model` belts are blind to a string import, the way `pool` already reaches the kernel

**File:** `tests/test_seam.py:103-108`, `pyproject.toml` ("The kernel doorways ..." contract)
**Issue:**
- `pool.py` reaches `spur.model` via `importlib.import_module("spur.model")` (D-05). That is
  the shape a future `import_module("spur.shaft_model")` in `pool` would take, and both the
  import-linter contract and `_import_lines` miss it. The contract comment concedes this for
  `model` but not for `shaft_model`.
- The practical risk is low, because `pool` is the only place that pattern lives.

**Fix:** add a one-line assertion that the string `"shaft_model"` does not appear in
`app`, `cli`, `pool`, `records` or `parts`, so the dynamic-import hole is closed by the belt.

---

_Reviewed: 2026-10-23_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
