---
phase: 11-body-cutouts
reviewed: 2026-09-29T00:00:00Z
depth: standard
files_reviewed: 23
files_reviewed_list:
  - bench/honeycomb_spike.py
  - bench/RESULTS.md
  - bench/sweeps/hole_cutout.json
  - bench/sweeps/honeycomb.json
  - bench/sweeps/spoke_cutout.json
  - docs/architecture/decision_log.md
  - docs/architecture/gear-maths/implementation.md
  - docs/architecture/solid-model/tactics.md
  - docs/ideas/2026-09-29-conditional-form-fields.md
  - docs/ideas/2026-09-29-cutout-rotation-field.md
  - docs/ideas/2026-09-29-teeth-dependent-honeycomb-cap.md
  - docs/ideas/INDEX.md
  - docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md
  - docs/tech_debt/INDEX.md
  - README.md
  - src/spur/calc.py
  - src/spur/model.py
  - src/spur/params.py
  - src/spur/static/app.js
  - tests/test_api.py
  - tests/test_bench.py
  - tests/test_calc.py
  - tests/test_cli.py
  - tests/test_model.py
findings:
  critical: 0
  warning: 5
  info: 1
  total: 6
status: issues_found
---

# Phase 11: Code Review Report

**Reviewed:** 2026-09-29
**Depth:** standard
**Files Reviewed:** 23
**Status:** issues_found

## Summary

Phase 11 adds three body-cutout patterns (spokes, lightening holes, honeycomb) to the
CadQuery gear generator. I read `calc.py`, `model.py`, `params.py` and `app.js` in full,
traced the new `_cut_body`/`_spoke_sector`/`_fillet_corner(inside=)` geometry, and
independently numerically re-derived the new `inside=True` fillet-tangent quadratic
(`_fillet_corner`) outside pytest — it produces a geometrically valid tangent circle
(confirmed centre distance, tangency to both circle and line). I also traced the
cross-feature safety argument (bore/keyway vs. cutout patterns all sharing
`bore_mouth_limit(p)` as one conservative datum) and found it sound: a keyway, a hex
bore's corners, and every cutout pattern's hub-side wall check are all bounded off the
same global "farthest reach" scalar, so no combination of keyway + cutout can silently
overlap. No BLOCKER-level correctness or security defect was found in the shipped
`calc.py`/`model.py`/`params.py`/`app.js` code path.

An external reviewer lane (codex) supplied 7 claims against this same file scope. I
independently re-read every cited line before accepting or rejecting each one (see
below); one claim (D-flat wall "exactness") is rejected — the code and its schema
docstring already correctly document the lower-bound behaviour it describes, so there is
no discrepancy. The other six are confirmed against the current source and are folded in
below with `(external: codex)`. The most substantive of these is the honeycomb spike's
`slower()`/verdict logic, which can silently discard a failed build trial in favour of a
successful one and never checks the confirmation or spelling rows for validity — a
methodology gap in the one script whose output (`HEX_CELL_CAP = 120`) is baked into
`calc.py` as a constant that caps every honeycomb gear built in production.

The remaining findings are documentation-accuracy gaps (a decision-log entry that
inverts its own test's conclusion, a wrong function signature in the architecture doc, a
README claim that contradicts `check()`'s actual half-set behaviour, and a bench doc that
misstates a field default) plus one test-coverage gap (the filleted-spoke removed-volume
proof has no closed-form cross-check, unlike every other cutout pattern). None of these
affect the numbers `derive()` prints or the parts the kernel builds today.

## Warnings

### WR-01: Honeycomb spike can hide a failed trial and report `Verdict: held` regardless (external: codex)

**File:** `bench/honeycomb_spike.py:170-174, 298-304`
**Issue:** `slower(a, b)` keeps whichever of the two timed trials has the larger
`request_s` (`bare_s + cut_s + max(stl_s, step_s)`). A trial whose cut/build fails sets
`why` to the exception name but always has `stl_s = step_s = 0.0`, so its `request_s` is
almost always *smaller* than a successful trial's (which pays real export time). That
means `slower()` systematically prefers the successful run over the failed one, and the
failed run's `why` never reaches `cost_rows`, `confirm_row.ok()`, or the verdict. Worse,
the verdict's `reasons` list (lines 298-304) checks `confirm_row.request_s > BUDGET_S`
but never checks `confirm_row.why == ""`/`confirm_row.ok()`, and never checks
`spelling_rows` for validity at all — so a real, reproducible build failure on either the
confirmation row or any spelling row can be silently dropped and the script still prints
`**Verdict:** held`. This is the script whose measured output produced
`HEX_CELL_CAP = 120` in `src/spur/calc.py`, a constant that caps every honeycomb request
in production (L08) — a methodology gap here undermines confidence in that number, not
just the bench doc.
**Fix:**
```python
def ok(self) -> bool:
    return self.why == "" and self.cells <= self.target

# slower() should never discard a failure in favour of a success:
def slower(a: CostRow, b: CostRow) -> CostRow:
    if bool(a.why) != bool(b.why):
        return a if a.why else b  # a failure always "wins" so it can't be hidden
    return a if a.request_s >= b.request_s else b

# and the verdict should check every retained row, not just cost_rows:
if not confirm_row.ok():
    reasons.append("the module-1.75 confirmation row failed")
if not all(row.ok() for row in spelling_rows.values()):
    reasons.append("a cut-spelling row failed")
```

### WR-02: L30 decision-log entry inverts its own test's conclusion (external: codex)

**File:** `docs/architecture/decision_log.md:1218-1221`
**Issue:** The entry states "Every refusal was pinned one field-step either side on the
real kernel — the boundary itself builds, one step past it does not" for every cutout
`MIN_WALL` rule. But `tests/test_model.py::test_the_kernel_cuts_one_valid_solid_past_each_cutout_rule`
(lines 1026-1036) does exactly the opposite: it bypasses validation with `model_copy()`
and asserts the kernel *does* cut a valid solid one field-step past every one of these
rules — that's the whole point of the test and its own docstring ("the kernel still cuts
one valid solid one 0.05 mm field-step past every cutout wall rule... these are the
part's own MIN_WALL, not a kernel limit"). The decision log's wording says the opposite
of what was measured and shipped, and a future reader citing L30 would draw the wrong
conclusion about whether these are kernel limits or design choices.
**Fix:** Correct the sentence to distinguish validation refusal from kernel capability,
e.g.: "the boundary itself builds and `check()` accepts it; one step past it `check()`
refuses, but the kernel itself still cuts a valid solid there (pinned, validation
bypassed) — proof the rule is the part's own MIN_WALL, not a kernel limit."

### WR-03: `implementation.md` documents `cell_count_floor` with a `cap` argument it does not take (external: codex)

**File:** `docs/architecture/gear-maths/implementation.md:32`
**Issue:** The table entry reads `cell_count_floor(cap, cell, wall, inner, outer)`. The
actual function (`src/spur/calc.py:444`) is
`def cell_count_floor(cell: float, wall: float, inner: float, outer: float) -> float:` —
four parameters, no `cap`; the cap comparison happens in the caller, `cells_within`.
Anyone calling `cell_count_floor` as documented gets a `TypeError`.
**Fix:** Update the doc row to `cell_count_floor(cell, wall, inner, outer)`.

### WR-04: README claims the "reverse half-set" cutout case is rejected; it is accepted and warned instead

**File:** `README.md:151-152`
**Issue:** "a half-set pattern — a count with a dimension still 0, or the reverse — is
rejected, naming the zero fields." Only the forward direction (count set, a dimension
still 0) is a 422 — `calc.check()`'s `zero = [...]` blocks for spokes/holes/hex all fire
only inside `elif p.spoke_count > 0` / `elif p.hole_count > 0` / `elif p.hex_cell > 0`.
The reverse (a dimension set, count still 0) builds nothing and only warns — see
`derive()`'s three "ignored" warning blocks (`calc.py` ~1047-1087) — and the project's
own decision log documents this correctly: "the reverse (a dimension set with the count
at 0) builds nothing and warns, naming the ignored fields (D-15)." The README
contradicts the actual API behaviour and the project's own decision record.
**Fix:** Reword to match D-15: "...a half-set pattern — a count with a dimension still 0
— is rejected, naming the zero fields; the reverse (a dimension set with the pattern's
count at 0) builds nothing and warns instead, naming the ignored fields."

### WR-05: The filleted-spoke removed-volume proof has no closed-form cross-check (external: codex, extended)

**File:** `tests/test_model.py:1224-1240` (see also `1186-1263`)
**Issue:** `test_each_cutout_is_exactly_what_derive_prints_on_the_built_solid`/
`test_the_cutout_proof_fails_when_the_cutout_step_is_skipped` check holes, sharp spokes
and honeycomb cells against an independent closed-form area/volume formula "to 1e-9 mm3"
(the project's own stated bar). The filleted-spoke case — the one pattern using the new,
non-trivial `_fillet_corner(inside=True)` mirrored-quadratic geometry added by this
phase — is checked only against a pinned literal (`d_volume=2934.725405`) measured once
on the current kernel, with no independent formula, exactly as the decision log itself
states ("no closed form for a filleted sector's removed volume -- pinned, not derived").
I independently re-derived the `inside=True` tangent-circle math outside pytest and
confirmed it is geometrically self-consistent for the case I tried, so I found no actual
defect — but the pinned-only check means a systematic geometry error in this new code
path (wrong tangent root, wrong sign, wrong side) would be invisible to `make verify`
forever: any wrong-but-stable value the kernel produces gets captured as "correct" the
first time the test is written. The `isInside()` hub/rim-wall probe in the same test
provides some independent signal but does not touch the fillet radius itself.
**Fix:** Not blocking, but worth closing the gap: derive an independent closed-form for
the filleted-sector volume (the sharp-sector area minus four circular-segment corrections
of radius `spoke_fillet_effective(p)`, the same shape as the sharp-bar formula already
used) and assert against it to the same 1e-9 mm3 bar the other three patterns get, or
file this as tech debt naming the gap explicitly (per `CLAUDE.md`'s tech-debt process)
rather than leaving it implicit in a docstring comment.

## Info

### IN-01: `bench/RESULTS.md` and `test_bench.py` misstate the honeycomb field's default and legal range (external: codex)

**File:** `bench/RESULTS.md:971`, `tests/test_bench.py:273`
**Issue:** Both say `hex_cell` at 3 mm is "the field default" and/or "the smallest legal
request." `hex_cell`'s actual default is `0.0` (`src/spur/params.py:147`,
`hex_cell: float = _f(0.0, 0, 100, ...)`), and `calc.check()` accepts any positive value
down to its 0.001 mm cut resolution (`round(p.hex_cell, 3) == 0` is the only floor) — 3 mm
is simply the value the sweep chose to measure, not a schema minimum.
**Fix:** Reword both to "held at 3 mm, the sweep's own chosen input" rather than
"the field default (3 mm, the smallest legal request)".

---

_Reviewed: 2026-09-29_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
