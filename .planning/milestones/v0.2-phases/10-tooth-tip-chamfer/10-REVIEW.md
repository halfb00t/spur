---
phase: 10-tooth-tip-chamfer
reviewed: 2026-09-28T00:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - src/spur/calc.py
  - tests/test_calc.py
findings:
  critical: 1
  warning: 0
  info: 2
  total: 3
status: issues_found
---

# Phase 10: Code Review Report

**Reviewed:** 2026-09-28T00:00:00Z
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

Incremental re-review of the one fix commit since the previous 10-REVIEW.md
(`54fe020`, "fix(10): WR-01 warn when a tip chamfer request rounds away to nothing"),
scoped to `git diff 367d77a..HEAD -- src/spur/calc.py tests/test_calc.py`. Ran
`.venv/bin/python -m pytest tests/test_calc.py -q` (91 passed) and hand-verified the
new branch against the pinned kernel via the REPL (not predicted).

**WR-01 (previous review): verified fixed for the case it targeted.** The comparison in
`derive()` now reads `if tch < p.tip_chamfer:` instead of
`if tch < round(p.tip_chamfer, 3):`, so `GearParams(tip_chamfer=0.0004)` — which used to
round to `0.0` on both sides of the old comparison and warn nothing — now produces one
"Tip chamfer reduced to 0 mm ..." warning, matching root_fillet/recess_fillet's own
raw-request comparison. Confirmed by hand and by the new
`test_a_sub_print_precision_tip_chamfer_request_still_warns`.

**But the fix introduces a new, broader defect (CR-01, independently confirmed from the
codex evidence file's P3 finding):** the warning's *reason* clause
(`tip_chamfer_limit(p)[1]`) is not actually tied to what caused the reduction. It always
reports whichever of the three geometric limits is numerically smallest for the current
parameters — even when none of them bound the value at all, and the entire "reduction"
is 3-decimal-place rounding of an ordinary request. I reproduced this for
`tip_chamfer=0.1234` (not merely the sub-0.0005 mm edge case the fix's own test covers):
the pitch-circle limit for the default gear is `1.75` mm, nowhere close to binding, yet
`derive()` prints "Tip chamfer reduced to 0.123 mm to keep it above the pitch circle." —
a fabricated cause for an entirely mundane 3-dp rounding step. This is exactly the class
of thing CLAUDE.md's standing rule exists to prevent ("A number the tool prints is a
number someone will cut metal to... never a plausible one"): the *number* here (`0.123`)
is correct, but the *stated reason* is a plausible-sounding falsehood, unlike
`root_fillet`/`recess_fillet`'s single fixed reason strings, which are always true
because those fields have only one capping source. `tip_chamfer_limit`'s three
candidate reasons make this new comparison's simplicity (compare raw vs. applied, borrow
the smallest limit's text) unsound: picking "the smallest limit's reason" is only valid
when that limit is what actually reduced the value.

## Critical Issues

### CR-01: The tip-chamfer warning states a false geometric cause whenever rounding, not a limit, changes the value (external: codex)

**File:** `src/spur/calc.py:544-552`

**Issue:** The fixed comparison is:

```python
tch = tip_chamfer_effective(p)
if tch < p.tip_chamfer:
    warnings.append(f"Tip chamfer reduced to {tch:g} mm {tip_chamfer_limit(p)[1]}.")
```

`tip_chamfer_effective(p)` is `round(min(p.tip_chamfer, tip_chamfer_limit(p)[0]), 3)`.
The `tch < p.tip_chamfer` test only tells you the *final rounded value* differs from the
*raw request* — it does not tell you *why*. There are two structurally different reasons
that inequality can be true:

1. `tip_chamfer_limit(p)[0] < p.tip_chamfer` — a real geometric limit bound the value.
   Here `tip_chamfer_limit(p)[1]` is the correct explanation.
2. `tip_chamfer_limit(p)[0] >= p.tip_chamfer`, but `round(p.tip_chamfer, 3) !=
   p.tip_chamfer` — the request itself had more precision than the model prints, and
   plain 3-decimal rounding (not any limit) produced the visible difference. Here
   `tip_chamfer_limit(p)[1]` is **not** the reason at all; the geometric limit is not
   remotely close to binding.

Verified directly against the pinned code (not predicted):

```
>>> from spur.params import GearParams
>>> from spur.calc import derive, tip_chamfer_effective, tip_chamfer_limit
>>> p = GearParams(tip_chamfer=0.1234)
>>> tip_chamfer_limit(p)
(1.75, 'to keep it above the pitch circle')
>>> tip_chamfer_effective(p)
0.123
>>> derive(p).warnings
('Tip chamfer reduced to 0.123 mm to keep it above the pitch circle.',)
```

The pitch-circle cap is `1.75` mm; the request (`0.1234`) is nowhere near it. The
"reduction" from `0.1234` to `0.123` is ordinary 3-dp rounding, yet the warning asserts a
geometric cause that is false for this call. This is not confined to the sub-0.0005 mm
edge case the fix's own test (`test_a_sub_print_precision_tip_chamfer_request_still_warns`)
covers — it fires for **any** `tip_chamfer` value with more precision than 3 decimal
places, wherever that value sits well inside all three limits. That is a large,
easily-reachable input space for any direct `/api/info`, `/api/model.stl` or
`spur export --tip-chamfer` caller sending a value with 4+ significant decimals (exactly
the caller class `calc.py`'s own `ROOT_CONTACT` docstring already worries about for
`bore_d`); the web UI's 0.05 mm step happens not to trigger it, but nothing in the model
enforces that step (same gap `ROOT_CONTACT`'s docstring notes for other fields).

The new regression test only checks the message *prefix*
(`tip_warnings[0].startswith("Tip chamfer reduced to 0 mm")`), so it cannot catch a wrong
*suffix* — the false reason clause passes unnoticed. `make verify` and
`pytest tests/test_calc.py -q` both stay green with this bug present (91 passed,
confirmed above).

**Fix:** Only attribute the reduction to a geometric limit when that limit is actually
what produced the value; otherwise state plainly that the request was rounded to the
model's print precision. For example, compare the *limit* against the *raw request* to
decide which explanation applies:

```python
tch = tip_chamfer_effective(p)
limit, reason = tip_chamfer_limit(p)
if round(limit, 3) < round(p.tip_chamfer, 3):
    warnings.append(f"Tip chamfer reduced to {tch:g} mm {reason}.")
elif tch < p.tip_chamfer:
    # No geometric limit bound this request; the model only prints 3 dp, and this
    # request had more precision than that.
    warnings.append(f"Tip chamfer reduced to {tch:g} mm; requested value was rounded "
                    "to the model's print precision.")
```
Add a test with a value like `0.1234` (well inside every limit but not 3-dp-aligned) that
asserts the *full* warning string, not just its prefix, so this class of message-content
bug cannot regress silently again.

## Info

### IN-01: Bench spike hardcodes the `tip_chamfer` field's `le=3` bound in two places

**File:** `bench/tip_chamfer_spike.py:201`, `bench/tip_chamfer_spike.py:286`

**Issue:** Carried forward unchanged from the previous review — out of this diff's
scope (`bench/tip_chamfer_spike.py` was not touched by `54fe020`), still valid: verified
lines 201 and 286 are unchanged and still hardcode the literal `3.0` that mirrors
`GearParams.model_fields["tip_chamfer"]`'s `le=3` bound by hand, with no test in
`make verify`'s pytest run guarding against drift if that field bound ever changes.

**Fix:** Unchanged from the previous review: read the bound from the field
(`GearParams.model_fields["tip_chamfer"].metadata`) instead of repeating the literal.

### IN-02: `DerivedDimensions.tip_chamfer_effective`'s null-gate reads the raw field, not the applied value

**File:** `src/spur/calc.py:621`

**Issue:** `tip_chamfer_effective=r3(tch) if p.tip_chamfer > 0 else None` still gates on
the raw request rather than on `tch`. As the fix report notes, WR-01's fix resolved the
*silent* half of this (a request that rounds to nothing now always ships with a
"reduced" warning), but the field still prints a non-`null` `0.0` rather than `null`
("no tip chamfer") for that case, and — per CR-01 above — the accompanying warning can
now carry a fabricated geometric reason rather than an honest one. The two remaining
questions (whether `0.0` vs `null` is more honest for this field, and CR-01's message
content) are entangled: fixing CR-01's message text does not by itself resolve whether
`0.0` is the right printed value here.

**Fix:** Low priority, and coupled to CR-01's resolution — reconsider `tch > 0` as the
null-gate once the warning text itself is fixed, since `tch` (not the raw request) is
what the built part actually reflects.

---

_Reviewed: 2026-09-28T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
