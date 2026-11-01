---
phase: 34-fit-tables-and-tolerance-window
reviewed: 2026-10-31T00:00:00Z
depth: standard
files_reviewed: 40
files_reviewed_list:
  - .dockerignore
  - .gitignore
  - bench/RESULTS.md
  - docs/architecture/cli.md
  - docs/architecture/decision_log.md
  - docs/architecture/http-api.md
  - docs/architecture/packaging.md
  - docs/ideas/INDEX.md
  - docs/ideas/retired/2026-10-26-print-odd-tooth-count-measure-over-pins.md
  - docs/tech_debt/active/2026-10-31-din5480-tables-loader-refusals-not-reached-by-a-test.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/resolved/2026-10-26-fit-pattern-accepts-fits-outside-the-standards-set.md
  - Makefile
  - README.md
  - scripts/din5480_read1.py
  - scripts/din5480_tables_tool.py
  - src/spur/app.py
  - src/spur/cli.py
  - src/spur/din5480_tables.py
  - src/spur/din5480.py
  - src/spur/pool.py
  - src/spur/shaft_calc.py
  - src/spur/shaft_model.py
  - src/spur/shaft_params.py
  - tests/browser_session.py
  - tests/conftest.py
  - tests/din5480_real_tables_check.py
  - tests/din5480_tables_fixture.py
  - tests/shaft_parity.py
  - tests/test_browser.py
  - tests/test_cli.py
  - tests/test_din5480_anchors.py
  - tests/test_din5480_read1.py
  - tests/test_din5480_tables_tool.py
  - tests/test_din5480_tables.py
  - tests/test_pool.py
  - tests/test_shaft_calc.py
  - tests/test_shaft_interfaces.py
  - tests/test_shaft_model.py
  - tests/test_shaft_parity.py
findings:
  critical: 0
  warning: 4
  info: 7
  total: 11
status: issues_found
---

# Phase 34: Code Review Report

**Reviewed:** 2026-10-31
**Depth:** standard
**Files Reviewed:** 40
**Status:** issues_found

## Summary

Reviewed the loader (`din5480_tables.py`), the window and limit maths in `shaft_calc.py`, the solid change in
`shaft_model.py`, the pool, CLI and app wiring, the two developer scripts, the docs and the tests added in this
phase. `bench/RESULTS.md` and `decision_log.md` were read as phase diffs against `ddfb3ea` only.

The production maths is sound against L08, L03 and L05: the tier logic in `derive_shaft`, the exact-key lookup,
the window guard, the worker hand-off of the parent's one `Tables` object and the startup refusal all behave as
L50 says. No table value was found in a tracked file beyond the approved anchors and no path reaches an API
warning. Nothing at BLOCKER level.

The defects are at the edges: a privacy guard in a script that fails open, a deployment instruction that
contradicts the container's user, a loader that accepts tolerance rows whose signs and order make the printed
limits nonsense, and a two-reads gate that one typo defeats. Probes for WR-01 and WR-03 were run with the synthetic
fixture and a throw-away repository, never the private file.

Not re-filed, per the brief: loader refusal lines not reached by a test, the browser test's 5 s wait, the shift
range narrower than DIN's exceptions, the missing Table 12 row.

## Warnings

### WR-01: `ensure_ignored` fails open on any git fatal error, and creates directories before it checks

**File:** `scripts/din5480_read1.py:165-175`
**Issue:** The guard that keeps a read of the licensed copy out of a tracked path treats exit status 128 as
"not inside a repository, nothing can be tracked". Git exits 128 for every fatal error, not only that one. A
corrupt `.git`, a `safe.directory` / dubious-ownership refusal or an unreadable repository all return 128, and the
guard then passes and the read is written. Reproduced with a throw-away repository whose `HEAD` was garbage: the
command printed `fatal: not a git repository` and returned 128, identical to a directory outside any repository.
This is the D-01 hard rule (a committed value is public history), enforced by a check that passes when git cannot
answer. The same function also calls `path.parent.mkdir(parents=True, exist_ok=True)` before the check, so a
refused path still leaves new directories in the working tree. `scripts/din5480_tables_tool.py` imports and relies
on this function for `join` and `assemble`.
**Fix:**
```python
def ensure_ignored(path: Path) -> None:
    path = path.resolve()
    anchor = next(p for p in (path.parent, *path.parent.parents) if p.exists())
    inside = subprocess.run(["git", "-C", str(anchor), "rev-parse", "--is-inside-work-tree"],
                            check=False, capture_output=True, text=True)
    if inside.returncode != 0 and "not a git repository" not in inside.stderr:
        raise SystemExit(f"refusing to write {path}: git cannot say whether it is ignored")
    if inside.returncode == 0:
        code = subprocess.run(["git", "-C", str(anchor), "check-ignore", "-q", str(path)],
                              check=False, capture_output=True).returncode
        if code != 0:
            raise SystemExit(f"refusing to write {path}: git does not ignore it (D-01)")
    path.parent.mkdir(parents=True, exist_ok=True)
```
Add a test with a corrupt repository that expects the refusal.

### WR-02: The documented file mode makes the table file unreadable to the container's user

**File:** `README.md:86`, `docs/architecture/packaging.md:84` (with `Dockerfile:33-34`)
**Issue:** The README says to keep the table file "readable by the service user only (mode 0600)". The packaging
page tells the operator to bind-mount `./private/din5480-tables.json` read-only into the container. The image runs
as `--uid 10001` (`Dockerfile:33-34`). A 0600 file owned by the host user is not readable by uid 10001 on a Linux
bind mount, so `load_file` fails with `cannot be read (Permission denied)` and, by D-04, the container exits at
startup. Following both documents together produces a container that refuses to start. "The service user" is
never defined and the packaging page gives no ownership or mode.
**Fix:** In `packaging.md` state the working recipe, for example `chown 10001 private/din5480-tables.json &&
chmod 0400 private/din5480-tables.json`, or mode 0444 on a directory only the operator can enter. Reword the
README line to name uid 10001 for the container case.

### WR-03: `problems()` accepts tolerance rows whose signs and order make the printed limits impossible

**File:** `src/spur/din5480_tables.py:274-279`
**Issue:** The structural check for a tolerance row is `T_G == T_act + T_eff` and `abs(v) <= UM_LIMIT`. Nothing
requires `T_G > 0`, `T_act >= 0` or `0 <= T_eff <= T_G`. A consistent row with all three negated loads clean.
Probed with the synthetic fixture: a row with the three fields negated loaded, and the default shaft then printed
`s_vmax 2.592`, `s_max 2.606`, `s_min 2.627`, which is s_max above s_vmax and s_min above s_max. A second probe
with `T_act = -5` and `T_eff = T_G + 5` also loaded and printed `s_max 2.552` and `s_min [retired fixture value]`, so s_max below s_min. These are
numbers someone cuts metal to (L08), and a sign slip is the failure class the loader already guards against
elsewhere (`_BAD_MINUS`). The same gap lets one `A_s` cell of 900 um load and print an s_vmax of 3.513 against a
nominal 2.613.
**Fix:** In the tolerance loop:
```python
if tol.t_act_um < 0 or tol.t_eff_um < 0:
    found.append(f"{at}: T_act or T_eff is negative")
```
That implies `T_G >= T_eff >= 0`. Add a case to `BROKEN` in `tests/test_din5480_tables.py`, and see it red. Consider
also refusing a file whose derived `s_min <= s_max <= s_vmax` fails for any listed size, which catches a bad `A_s`.

### WR-04: `assemble` accepts one read passed twice, so its "two independent reads agree" gate is one typo wide

**File:** `scripts/din5480_tables_tool.py:245-260`
**Issue:** D-08 says the table file exists only once two independent reads agree. `cmd_assemble` diffs
`part2[0]` against `part2[1]` and `table7[0]` against `table7[1]` and never checks that the two paths differ.
`make tables.assemble P2A=x P2B=x ...` (a copy-paste slip in a four-variable command) writes the table file after
comparing a read with itself, and prints the same success line. The tests pass the same file for both sides on purpose
(`tests/test_din5480_tables_tool.py:243-246` and the two refusal tests), so the gap is built in to the test setup.
**Fix:** Refuse in `cmd_assemble` when `args.part2[0].resolve() == args.part2[1].resolve()` (same for `table7`),
naming the option. Give the tests a byte-identical copy as the second read instead of the same path.

## Info

### IN-01: `limit_measurement`'s `odd_confirmed` parameter and its odd-count branch are unreachable in production

**File:** `src/spur/shaft_calc.py:380-406`
**Issue:** `derive_shaft` is the only production caller and passes `odd_confirmed=True` every time, so the
`if p.teeth % 2 and not odd_confirmed: return LimitReading(None, ())` return at line 405 and the parameter that
gates it cannot run outside a test. CODING_VALUES says not to leave unreachable branches as if finished. The
existing debt item lists line 405 as "reached by no test" and proposes adding a test, which would pin dead code.
**Fix:** Drop the parameter and the branch (the limit is only ever computed for a listed size), or keep it and
correct the debt note to say it is dead rather than untested.

### IN-02: A code comment still points at the debt file this phase moved to `resolved/`

**File:** `src/spur/din5480.py:211` (also `:165`)
**Issue:** The `form_diameter` docstring cites `docs/tech_debt/active/2026-10-26-form-diameter-construction-
exceeds-din5480-2-maximum.md`, which Phase 34 `git mv`'d to `docs/tech_debt/resolved/`. The path is dead. Line 165
(`measure_over_pins`) still says "Phase 34 can pass limit thicknesses unchanged", which is now done.
**Fix:** Point at `resolved/` and reword line 165 to the present tense.

### IN-03: `SCHEMA_VERSION` is defined and never used

**File:** `src/spur/din5480_tables.py:32`
**Issue:** `SCHEMA_VERSION = 1` has no reader. The schema uses the literal `Literal[1]` (line 143), and
`scripts/din5480_read1.py:203`, `scripts/din5480_tables_tool.py:221,258` and the tests write the bare `1`. A version
bump would have four places to miss.
**Fix:** Remove the constant, or use it in the scripts and derive the `Literal` from it.

### IN-04: `load_file` reads the whole file before enforcing the size cap on what it read

**File:** `src/spur/din5480_tables.py:343-358`
**Issue:** The cap is checked on `stat().st_size`, then `read_bytes()` reads everything, then the cap is checked
again on `len(raw)`. The second check can only fire after the memory is spent, so it bounds nothing, and it is
the line the file-size test cannot tell from the first. The comment calls the cap "hygiene against a wrong path
naming a large file", which `stat` already covers.
**Fix:** `with path.open("rb") as f: raw = f.read(MAX_FILE_BYTES + 1)` and a single cap check on `len(raw)`.

### IN-05: Two real-file and anchor assertions are tautologies

**File:** `tests/din5480_real_tables_check.py:190-199`, `tests/test_din5480_anchors.py` (`low == approx(d_ff1 + GUARD_MARGIN_FACTOR * p.module)`)
**Issue:** `test_the_guard_form_term_is_each_rows_d_ff1_maximum` asserts `low - margin == form_d_max` where `low`
is `pin_contact_window(p, form_d_max)[0]`, which the function defines as `form_d_max + margin`. It cannot fail
except through float noise and checks nothing about the file. The same shape appears as the first assertion in
the anchors test; its second assertion (`low < contact < high`) is the real one.
**Fix:** Delete the real-file test, or replace it with the property that matters: the tabulated pin's contact at
nominal thickness lies above `form_d_max`, per row.

### IN-06: A file with Table 7 only partly present loads and then prints a false sentence

**File:** `src/spur/din5480_tables.py:266`, `src/spur/shaft_calc.py:476-479`
**Issue:** The column-selection check runs only `if t.columns:`. A file with sizes, deviations and classes but an
empty `columns` list loads, and every fit then reads "the fit 8f is not in DIN 5480-1 Table 7, whose shaft
deviations are f, h and k": a claim about the standard that is really a claim about a truncated file (reproduced
with the synthetic fixture). The tool's own comment accepts a missing letter reading as "fit outside Table 7", and
completeness is a transcription-time check by L50, so this is a logged trade-off. The sentence is still untrue.
**Fix:** In `problems()`, refuse a file where the four Table 7 lists are neither all empty nor all non-empty.
`test_a_document_of_empty_row_tuples_loads` keeps passing.

### IN-07: Read 1 matches digits with `\d`, against the repository's own stated rule

**File:** `scripts/din5480_read1.py:53,81`
**Issue:** `_NUM` and `_tooth_count` use `\d`, which matches Unicode digits, and `float()` / `int()` accept them.
`src/spur/din5480.py:220-223` records exactly this as a pitfall and uses `[0-9]` for it. A `pdftotext` token
with a non-ASCII digit would be read as a number rather than raise as a row-shaped line holding a non-number.
**Fix:** `re.compile(r"^-?[0-9]+(\.[0-9]+)?$")` and `re.fullmatch(r"[0-9]+", token)`.

---

_Reviewed: 2026-10-31_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
