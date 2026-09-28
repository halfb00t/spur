---
phase: 10-tooth-tip-chamfer
fixed_at: 2026-09-28T20:41:07+06:00
review_path: .planning/phases/10-tooth-tip-chamfer/10-REVIEW.md
iteration: 2
findings_in_scope: 2
fixed: 2
skipped: 0
status: all_fixed
---

# Phase 10: Code Review Fix Report

**Fixed at:** 2026-09-28T20:41:07+06:00
**Source review:** .planning/phases/10-tooth-tip-chamfer/10-REVIEW.md
**Iteration:** 2

**Summary (cumulative across both fix passes on this REVIEW.md):**
- Findings in scope (`fix_scope: critical_warning`): 2 (WR-01 from iteration 1, CR-01
  from this iteration 2 — the re-review that iteration 1's fix triggered found CR-01;
  IN-01 and IN-02 are Info, out of scope both passes)
- Fixed: 2
- Skipped: 0

## Fixed Issues

### WR-01: A `tip_chamfer` request under 0.0005 mm is silently rounded to nothing, with no warning

**Files modified:** `src/spur/calc.py`, `tests/test_calc.py`
**Commit:** `54fe020`
**Applied fix:** `derive()`'s tip-chamfer warning gate compared
`tip_chamfer_effective(p)` against `round(p.tip_chamfer, 3)` — both sides rounded to 3
dp — so a request below 0.0005 mm rounded to `0.0` on both sides and the comparison
`0.0 < 0.0` never fired, silently dropping the chamfer with no warning. Changed the
right-hand side to the raw, unrounded `p.tip_chamfer`, matching how `root_fillet` and
`recess_fillet` already compare their own applied-vs-requested values a few lines above
(`rfil < p.root_fillet`). Re-verified by hand that this still protects the print-residue
case the surrounding comment describes (`teeth=200, module=0.2, tip_chamfer=0.2`: the
pitch-circle limit is `0.1999999999999993`, which rounds to the same `0.2` the request
carries, so `tch (0.2) < p.tip_chamfer (0.2)` stays `False` and no warning fires) —
confirmed against all 14 existing rows of
`test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first` by tracing the arithmetic,
then by running the suite (all still pass, output below).

Added `test_a_sub_print_precision_tip_chamfer_request_still_warns` in
`tests/test_calc.py`, proving `GearParams(tip_chamfer=0.0004)` now produces exactly one
`"Tip chamfer reduced to 0 mm ..."` warning where before it produced none.

**Superseded by CR-01 below:** this iteration-1 fix compared the raw request
(`p.tip_chamfer`) directly, which — as the follow-up review (this same 10-REVIEW.md)
found — also made the warning fire on *any* ordinary request with more precision than
the model prints (e.g. `0.1234`), and in that case borrowed
`tip_chamfer_limit(p)[1]`'s reason text even when no limit was anywhere near binding.
CR-01 (below) replaces this comparison with a two-branch version that keeps the fix's
intent (a fully-rounded-away request still warns) while removing the false-cause defect.
The regression test this entry added was itself rewritten under CR-01 (see below) to
assert the full warning string instead of a prefix, since the prefix-only assertion is
exactly what let CR-01 slip through this pass's own `make verify`.

**Verification evidence at the time (commands run, not predicted):**

```
$ .venv/bin/python -m pytest tests/test_calc.py -q
........................................................................ [ 79%]
...................                                                      [100%]
91 passed in 0.14s
```

```
$ make verify
... (ruff, mypy --strict, import-linter contracts: all pass)
======================= 454 passed in 104.50s (0:01:44) ========================
```

`git diff --exit-code tests/regression/pre_v0_2.json` — no output, exit 0: the
regression fixture is byte-unchanged, confirming the fix does not change any previously
committed derived-dimensions output (this fix only adds a warning string for a case
that previously produced none, and cannot itself change `tch`'s numeric value).

Both commands ran directly in the main checkout (`workflow.use_worktrees: false` in
`.planning/config.json` — no isolated worktree was created for this run; the fixer
edited and committed on `gsd/phase-10-tooth-tip-chamfer` directly).

### CR-01: The tip-chamfer warning states a false geometric cause whenever rounding, not a limit, changes the value

**Files modified:** `src/spur/calc.py`, `tests/test_calc.py`
**Commit:** `60d02f7`
**Applied fix:** Per the design the human locked on 2026-09-28 (not REVIEW.md's own
"warn on every print-precision rounding" suggestion — a sub-µm rounding of a nonzero
request stays silent, like every other 3-dp field in this codebase; only a request that
rounds all the way to nothing warns, and it warns with its true cause). Split the single
`if tch < p.tip_chamfer:` gate in `derive()` into two branches:

```python
tch = tip_chamfer_effective(p)
if tch < round(p.tip_chamfer, 3):
    warnings.append(f"Tip chamfer reduced to {tch:g} mm {tip_chamfer_limit(p)[1]}.")
elif p.tip_chamfer > 0 and tch == 0.0:
    warnings.append(f"Tip chamfer {p.tip_chamfer:g} mm is below the 0.001 mm resolution "
                    "it is cut at and was not cut.")
```

First branch: the original 3-dp comparison from before `54fe020`, restored — a limit
binds only when it is below the request at the 0.001 mm resolution the chamfer is cut
at (`tip_chamfer_effective` rounds to 3 dp; `model.py` cuts exactly that value, L08).
This keeps a limit's own float residue silent (`0.1999999999999993` at 200 teeth,
module 0.2) *and* keeps an ordinary request like `0.1234` → `0.123` silent — that
rounding is the model's own print resolution, shared by `root_fillet`, `recess_fillet`
and `bore_chamfer`, not a reduction, so attributing it to `tip_chamfer_limit(p)[1]` was
the false cause CR-01 found.

Second branch: the one rounding case where the built part materially differs from the
request — a chamfer was asked for and none was cut — so it warns (the standing rule: a
parameter the user set never silently changes the part), and it names the real cause
(print resolution), never a limit. `tch == 0.0` is exact here because
`tip_chamfer_effective` already returns the rounded value, so no tolerance comparison is
needed.

Did not touch `tip_chamfer_effective`, `tip_chamfer_limit`, `model.py`, or the
`tip_chamfer_effective=... if p.tip_chamfer > 0 else None` field gate — IN-02 stays out
of scope (Info-severity). Side effect worth recording for whoever picks up IN-02: the
`tip_chamfer=0.0004` case now prints `tip_chamfer_effective: 0.0` *with* an honest
warning (print resolution, not a fabricated limit) — the field's `0.0` vs `null`
question IN-02 raises is unchanged by this fix.

Rewrote `test_a_sub_print_precision_tip_chamfer_request_still_warns` to assert the full
warning string for `GearParams(tip_chamfer=0.0004)` (exact text above with `0.0004`),
`tip_chamfer_effective(p) == 0.0`, and that no `"reduced to"` warning is present —
CR-01's own lesson is that a prefix assertion cannot see a wrong suffix, which is
exactly how the false-cause bug slipped through the prior pass's test. Added
`pytest.param({"tip_chamfer": 0.1234}, 0.123, None, id="print-precision-inside")` to
`test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first`'s table: a request well
inside every limit but not 3-dp-aligned must stay silent under the new design (unlike
REVIEW.md's own suggested fix, which would have warned on this row too).

**Verification evidence (commands run, not predicted):**

```
$ python -c "import ast; ast.parse(open('src/spur/calc.py').read())"
SYNTAX_OK
$ python -c "import ast; ast.parse(open('tests/test_calc.py').read())"
SYNTAX_OK
$ .venv/bin/python -m pytest tests/test_calc.py -q
........................................................................ [ 78%]
....................                                                    [100%]
92 passed in 0.14s
$ make verify
.venv/bin/python -m ruff check .            -> All checks passed!
.venv/bin/python -m mypy src tests docker bench scripts -> Success: no issues found in 34 source files
.venv/bin/lint-imports                      -> Contracts: 5 kept, 0 broken.
.venv/bin/python -m pytest                  -> 455 passed in 98.11s (0:01:38)
$ git diff --exit-code tests/regression/pre_v0_2.json
(no output, exit 0 -- fixture byte-unchanged)
```

Test count moved 91 -> 92 (one new parametrize row) and 454 -> 455 (`make verify`'s
full suite, same +1) purely from the added `print-precision-inside` row; no existing
test's expected value changed.

Both commands ran directly in the main checkout (`workflow.use_worktrees: false` in
`.planning/config.json` — no isolated worktree was created for this run; the fixer
edited and committed on `gsd/phase-10-tooth-tip-chamfer` directly, commit `60d02f7`).

## Skipped Issues

None — both in-scope findings (WR-01, CR-01) are fixed. IN-01 and IN-02 are
Info-severity and out of `fix_scope: critical_warning`; they were not attempted (IN-02's
entanglement with CR-01's message text is noted above but its `0.0`-vs-`null` question
is deliberately left for a separate follow-on, per the fixer's brief not to widen this
change further).

---

_Fixed: 2026-09-28T20:41:07+06:00_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 2_
