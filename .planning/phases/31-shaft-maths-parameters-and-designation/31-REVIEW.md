---
phase: 31-shaft-maths-parameters-and-designation
reviewed: 2026-10-26T00:00:00Z
depth: standard
files_reviewed: 13
files_reviewed_list:
  - bench/RESULTS.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/active/2026-10-23-parts-one-line-widening-claim-is-false.md
  - pyproject.toml
  - src/spur/din5480.py
  - src/spur/parts.py
  - src/spur/shaft_calc.py
  - src/spur/shaft_params.py
  - tests/shaft_oracle.py
  - tests/test_din5480.py
  - tests/test_din5480_anchors.py
  - tests/test_shaft_calc.py
  - tests/test_shaft_params.py
findings:
  critical: 0
  warning: 5
  info: 5
  total: 10
status: issues_found
---

# Phase 31: Code Review Report

**Reviewed:** 2026-10-26
**Depth:** standard
**Files Reviewed:** 13
**Status:** issues_found

## Summary

The maths is sound where I could test it. I ran four checks myself:

- ruff, `mypy --strict` on the three shaft modules, and the four shaft test files all pass (986 passed).
- I swept about 12,500 valid shafts (modules 0.5 to 10, z 6 to 82, x -0.05 to +0.45) through `derive_shaft`. None had a null pin, and no even-z shaft had a null `measure_over_pins`. The "guard cannot fire from `derive_shaft`" claim holds.
- I re-measured the D-20 comment over 31,416 cases with a pin rounded to 0.01 mm. The margins are 0.621*m above the internal d_Ff and 0.886*m below d_a. That matches the "0.62 / 0.886" in `shaft_calc.py`.
- I probed the parser with 15 hostile and odd inputs. The ASCII-only classes, `fullmatch` and the length bound hold. There is no ReDoS surface (the patterns are linear and the input is capped at 64 characters).

I found no BLOCKER. No printed number is wrong for the combination it claims. The five warnings are:

- a self-contradictory refusal message;
- a measure over pins that is printed beside a fit designation without saying it ignores the fit;
- a hobbing-only warning on `root_d`;
- an unpicklable exception;
- a parser docstring that says more than the parser does.

D3 (shift range) and D5 (fit shape) are filed debt and are not re-reported. D4 (D_Re/M_Re vs D_M/M1) is touched only in IN-03.

## Warnings

### WR-01: The refusal message contradicts itself near the range edges

**File:** `src/spur/shaft_calc.py:128-133`
**Issue:** The shift is printed with `{x:+.3f}` and the range with `{X_MIN:+.2f}`/`{X_MAX:+.2f}`. Because `check_shaft` refuses anything beyond the edge by more than 1e-9, any refused shift in (0.4500, 0.4505) prints as "+0.450" and then says it is "outside the range -0.05 to +0.45". I reproduced it:

```
ShaftParams(reference_d=25.001)
  -> "needs a profile shift of +0.450, outside the range -0.05 to +0.45"
```

The default shaft (25 / 1.25 / 18) sits exactly on the upper edge, and the form's `reference_d` step is 0.05. So the first nudge of a field off the default lands in this region. The same happens at the lower edge ("-0.050 ... -0.05"). The user is told 0.450 is outside 0.45 and cannot tell which field to move or by how much. This is the L03 refusal's only explanation.
**Fix:** Print enough digits to show the overshoot, or say which side was crossed and by how much:

```python
side = "above" if x > din5480.X_MAX else "below"
f"... needs a profile shift of {x:+.4f}, {side} the allowed {din5480.X_MIN:+.2f} to {din5480.X_MAX:+.2f}. ..."
```

Add a test row for `reference_d=25.001` that asserts the printed shift differs from the printed edge.

### WR-02: `measure_over_pins` is printed next to a fit designation but is the nominal-thickness measure, and no warning says so

**File:** `src/spur/shaft_calc.py:43-47, 195-196` (and `src/spur/din5480.py:124-157`)
**Issue:** `derive_shaft` returns `designation="W ...x8f"` and `measure_over_pins` computed at the nominal tooth thickness `s`. The warning that accompanies it (`THEORETICAL_PIN`) says only "M_Re is for this pin". The caveat that it is the nominal-thickness measure, with no allowance or tolerance for the fit, lives only in the `ShaftDimensions.measure_over_pins` field description. A front end that renders `warnings` does not show it.

The anchor test itself shows the size of the gap. The copy's M1 minimum for W 120x3x38x8f is taken at s = 6.180, 0.091 mm below the nominal 6.271 (`tests/test_din5480_anchors.py:57-71`). A user who reads "8f" and "M_Re" together and cuts to the printed M will not land in the standard's tolerance band. This breaks the project's first rule: a number someone will cut metal to.
**Fix:** Add one sentence to `THEORETICAL_PIN`, or a separate warning emitted whenever `measure_over_pins` is non-null, for example: "M_Re is the measure at the nominal tooth thickness; it carries no allowance or tolerance for the fit." Pin it in `test_the_default_shaft_prints_its_pin_and_measure_over_pins`. Phase 34 can remove it when it passes limit thicknesses.

### WR-03: The `root_d` warning names only hobbing; the copy names more processes

**File:** `src/spur/shaft_calc.py:57-61, 93-96`
**Issue:** `root_d` is labelled the theoretical (broaching) root. The only process-dependent correction offered is "A hobbed shaft's root is 0.1*m smaller". The 31-05 checkpoint (A3 and D2) records that the copy names four processes, with a larger dedendum factor for mill-broaching and a larger one still for cold rolling. A shaft made by those processes has a root more than 0.1*m below the printed `root_d` (by about 0.2*m at h_fP 0.65), and the warning gives it no hint. D1 (hobbed) is fixed, but D1's own reasoning ("a user who ... reads root_d is given a diameter too large") applies to the other processes too. `docs/ideas/…shaft-manufacturing-process-field.md` is filed, but nothing user-visible says the correction list is incomplete.
**Fix:** Reword the sentence so it does not read as the complete list, for example: "The root diameter is the theoretical (broaching) root. Other processes cut a deeper root: hobbing by 0.1*m (…), and the standard names larger depths for other processes (DIN 5480-1 cl. 7.1)." Update the `root_d` field description the same way.

### WR-04: `DesignationError` cannot be pickled, copied or re-raised across a process boundary

**File:** `src/spur/din5480.py:201-206`
**Issue:** The class takes two required arguments (`token`, `message`) but calls `super().__init__(message)`, so `self.args == (message,)`. `pickle.loads(pickle.dumps(e))` and `copy.copy(e)` both fail with `TypeError: DesignationError.__init__() missing 1 required positional argument: 'message'` (reproduced). The repo has a worker pool (`pool.py`, L04/L07), and Phase 33 will parse designations on the request path. Any path that ships the exception between processes, or a framework that copies it, will fail with the wrong error instead of the 422 with the token.
**Fix:**

```python
def __init__(self, token: str, message: str) -> None:
    super().__init__(token, message)
    self.token = token
    self.message = message

def __str__(self) -> str:
    return self.message
```

Add a pickle round-trip assertion to `test_an_unparseable_designation_is_refused_naming_its_token`.

### WR-05: `parse_designation` accepts leading zeros in the number tokens but refuses them in the fit; its docstring says otherwise

**File:** `src/spur/din5480.py:188-189, 220-259`
**Issue:** The docstring says the parser "accepts exactly the canonical form plus no space after W, an upper-case X and `,`". `_NUMBER = r"[0-9]+(?:[.,][0-9]+)?"` and `_TEETH = r"[0-9]+"` also accept leading zeros. I confirmed that `W 0025x01.25x018x8f` and `W 25x1.25x0018x8f` parse to the default shaft. The fit pattern refuses `08f` (the `FIT_PATTERN` leading `[1-9]`, and the `08f` refusal in `REFUSED_DESIGNATIONS`). The two rules disagree.

No row in `REFUSED_DESIGNATIONS` or the accepted variants covers leading zeros, so the behaviour is unspecified and unpinned. A Phase 33 link or cache key built from the designation text would see several spellings of one shaft.
**Fix:** Decide the rule. To match "exactly the canonical form", tighten the patterns, for example `_TEETH = r"[1-9][0-9]*"` and `_NUMBER = r"(?:0|[1-9][0-9]*)(?:[.,][0-9]+)?"`, and add the leading-zero rows to `REFUSED_DESIGNATIONS`. Otherwise add them as accepted variants and correct the docstring.

## Info

### IN-01: Debt items point at stale line numbers

**File:** `docs/tech_debt/active/2026-10-26-shaft-shift-range-narrower-than-din-5480-exceptions.md` (Related files)
**Issue:** It cites `src/spur/din5480.py:34 (X_MAX)` and `src/spur/shaft_calc.py:105 (check_shaft)`. After the 31-06 edits, `X_MAX` is at `din5480.py:40` (line 34 is the `RHO_FP` comment) and `check_shaft` is at `shaft_calc.py:119`. The same drift appears in the 31-05 summary's references, which are historical.
**Fix:** Cite by symbol (`din5480.X_MAX`, `shaft_calc.check_shaft`), not by line, in the debt items.

### IN-02: Stale module docstring in `tests/test_shaft_calc.py`

**File:** `tests/test_shaft_calc.py:3-4`
**Issue:** It says "The formulas are ASSUMPTIONS until the 31-05 checkpoint records their clauses, so these numbers pin what the code does, not what the standard says." The checkpoint has run and `din5480.py` now cites clauses for the tip, root, shift and thickness. The docstring misstates the confidence of these tests.
**Fix:** Reword to name what is still unconfirmed (pin, M_Re, form diameter) and point at the anchors file.

### IN-03: `THEORETICAL_PIN` makes a claim no seen page supports, and stays when the pin is null

**File:** `src/spur/shaft_calc.py:43-47, 197-198`
**Issue:**
1. The text says "It is not the D_Re that DIN 5480 tabulates." The 31-05 checkpoint (D4) records that Part 1 shows no such tabulation, so this is unverified against any page the project has seen. That is a user-facing factual claim without a source.
2. `derive_shaft` always appends `THEORETICAL_PIN`, even when `pin_measurement` returned `pin_d=None` with its own "D_Re not given" sentence. The two would then contradict each other. This is unreachable today (my sweep found no null pin), but the Phase 34 code path that makes it reachable is already described in `pin_measurement`'s docstring.
**Fix:** Say "the tool computes this pin; it has not been compared with a tabulated D_Re". Append `THEORETICAL_PIN` only when `reading.pin_d is not None`.

### IN-04: The 0.1*m drop is written twice and `HOBBED_ROOT_DROP` is not tied to `H_FP`

**File:** `src/spur/shaft_calc.py:54, 60-61`
**Issue:** `HOBBED_ROOT_DROP = 0.1` feeds the computed value, but the sentence hard-codes "0.1*m" twice. The constant is also independent of the 0.55 (`H_FP`) and 0.60 (hobbing) in `din5480.py`, although it is exactly `2*(0.60 - 0.55)`. Changing one place leaves the sentence or the other constant wrong. `test_the_dedendum_constant_moves_the_root_and_not_the_shift` already monkeypatches `H_FP` to 0.60 and then gets a "hobbed" warning that subtracts 0.1*m from a root that is already hobbed.
**Fix:** Format the factor into the sentence from the constant. Derive the constant from `din5480` (named `H_FP_HOBBING = 0.60`), or state the coupling in a comment.

### IN-05: The default shaft sits on the range edge, and `shaft_params` imports the gear's private helpers

**File:** `src/spur/shaft_params.py:14-15, 25-31`
**Issue:**
- (a) D-19 chose a default exactly on X_MAX. `reference_d` 25.05, `teeth` 17 and `module` 1.2 each refuse ("not a bug, L03"). The form's stepper therefore turns the default red on the first click up. This is by decision, but it is worth stating in the field `help` so the 422 is not a surprise. It also feeds WR-01.
- (b) `from .params import _extra, _f` pulls underscore-private names from the gear module. The import-linter contracts allow it (indirect only), but a rename in `params.py` would break the shaft with no contract signal. Coupling the gear's `_f` to the shaft's field metadata is the one remaining link between the two models.
**Fix:** (a) Add "Shifts outside -0.05..+0.45 are refused" to the `reference_d`/`module`/`teeth` help. (b) Optionally promote `_f`/`_extra` to a public shared helper, or note the intentional coupling in a comment.

---

_Reviewed: 2026-10-26_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
