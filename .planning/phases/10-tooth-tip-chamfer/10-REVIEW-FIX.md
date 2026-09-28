---
phase: 10-tooth-tip-chamfer
fixed_at: 2026-09-28T14:22:13Z
review_path: .planning/phases/10-tooth-tip-chamfer/10-REVIEW.md
iteration: 1
findings_in_scope: 1
fixed: 1
skipped: 0
status: all_fixed
---

# Phase 10: Code Review Fix Report

**Fixed at:** 2026-09-28T14:22:13Z
**Source review:** .planning/phases/10-tooth-tip-chamfer/10-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope (`fix_scope: critical_warning` — no Critical findings existed, so
  this is WR-01 alone; IN-01 and IN-02 are Info, out of scope per the fixer's brief):
  1
- Fixed: 1
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

Side effect on IN-02 (out of scope, not independently touched): IN-02's "silent" half is
now resolved as a direct side effect of this fix — a request that rounds to nothing
always ships with an explanatory warning now. IN-02's other half (whether
`tip_chamfer_effective` should print `null` instead of `0.0` for this case, i.e. whether
the null-gate should read `tch > 0` rather than `p.tip_chamfer > 0`) is **not**
resolved — the field still prints `0.0`, not `null`, exactly as the review's own text
anticipated ("Once WR-01 is fixed the printed 0.0 will at least always ship with an
explanatory warning ... consider whether `tch > 0` is closer to the field's own
documented contract"). That remaining half is a separate, deliberately-not-widened
follow-on per the fixer's brief.

**Verification evidence (commands run, not predicted):**

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

## Skipped Issues

None — the single in-scope finding (WR-01) was fixed. IN-01 and IN-02 are Info-severity
and out of `fix_scope: critical_warning`; they were not attempted (IN-02's silent-drop
half is addressed as a documented side effect above, per the fixer's brief not to widen
the change further).

---

_Fixed: 2026-09-28T14:22:13Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
