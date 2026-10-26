---
phase: 31-shaft-maths-parameters-and-designation
verified: 2026-10-26T23:00:00Z
status: passed
score: 5/5 must-haves verified (0 overrides relied on)
covered_files:
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-01-PLAN.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-01-SUMMARY.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-02-PLAN.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-02-SUMMARY.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-03-PLAN.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-03-SUMMARY.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-04-PLAN.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-04-SUMMARY.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-05-PLAN.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-05-SUMMARY.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-06-PLAN.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-06-SUMMARY.md"
  - "bench/RESULTS.md"
  - "docs/architecture/decision_log.md"
  - "docs/ideas/2026-10-26-print-odd-tooth-count-measure-over-pins.md"
  - "docs/tech_debt/active/2026-10-26-form-diameter-construction-exceeds-din5480-2-maximum.md"
  - "docs/tech_debt/resolved/2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing.md"
  - "src/spur/din5480.py"
  - "src/spur/parts.py"
  - "src/spur/shaft_calc.py"
  - "src/spur/shaft_params.py"
  - "tests/shaft_oracle.py"
  - "tests/test_din5480.py"
  - "tests/test_din5480_anchors.py"
  - "tests/test_shaft_calc.py"
  - "tests/test_shaft_params.py"
covered_digest: "v3:sha256:4d4c723a3653f9801c601a94f12b6a9f22e199b23575c8f06f12ea2562cba947"
behavior_unverified: 0
overrides_applied: 0
# History only. This override was the basis of the previous report's pass of truth 2. It is no
# longer relied on: truth 2 is VERIFIED directly on the DIN 5480-2 anchors (see below).
overrides:
  - must_have: "d_B, tip, root and nominal thickness agree with at least two anchor rows from the copy"
    reason: "DIN 5480 Part 1 has no size tables; one designation (W 120x3x38x8f, cl. 9.1 Fig. 6) is anchored for the tip; the rest is filed as must-severity debt 2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing. Accepted at the 31-05 checkpoint (partial pass + debt); accepted_by entered by the agent on the human's explicit instruction."
    accepted_by: "Andrew S"
    accepted_at: "2026-10-26"
re_verification:
  previous_status: passed
  previous_score: 5/5 (includes 1 override)
  gaps_closed:
    - "SC2 / REQ-shaft-basic-dims: at least two copy anchor rows (previously carried by the override and a must-severity debt item)"
  gaps_remaining: []
  regressions: []
deferred: []
advisory:
  - finding: "The resolved anchor debt item and its INDEX row give `Resolved in:` as a commit subject ('test(31): anchor four DIN 5480-2 rows and close the Part 1 anchor gap'), not a sha. CLAUDE.md asks for the sha. The commit is 45b6565, found with git log."
    category: other
    reason: "Bookkeeping. The subject is unique and resolves to 45b6565 today. The repo already tracks the wider problem of shas that squash-merge orphans (docs/tech_debt/active/2026-10-05-resolved-in-shas-point-at-squashed-branch-commits.md), which is probably why a subject was chosen. Add the sha beside the subject."
    evidence_status: "reproduced: read the file header; git log --oneline -1 45b6565"
  - finding: "T-31-13 residue: three docs state derived statistics of unnamed Part 2 rows (shift of the 11 refused rows 0.617 to 0.879, z >= 60, m 0.6 to 1.75; construction minus maximum -0.031 to +0.174*m; 16 of 721 pins match). No row can be identified from them."
    category: other
    reason: "Aggregates and extremes, not table values. They are not in the approved set, but they carry no per-row figure and no designation. Say so if the human wants a stricter reading of 'nothing else from the copy is committed'."
    evidence_status: "reproduced: read the three files"
  - finding: "ROADMAP SC3 / REQ-mre-nominal say odd z stays null until an odd-z anchor row confirms it. Two odd rows now confirm the factor (M1 at the tabulated pin, 211 of 211 odd rows in the scratch comparison) and the shaft still prints null for odd z, by the human's choice."
    category: other
    reason: "Not a gap: the criterion bounds when null is required, not when a number must print, and an honest null is the L08 default. The choice is filed as docs/ideas/2026-10-26-print-odd-tooth-count-measure-over-pins.md with the caveat that an odd M_Re at the tool's theoretical pin is not the tabulated pin's M1."
    evidence_status: "reproduced: 0 of 29,668 accepted odd-z shafts in the grid print measure_over_pins"
coincidental_reliance_items: []
human_verification: []
---

# Phase 31: Shaft Maths, Parameters and Designation Verification Report

**Phase Goal:** A user can ask the pure maths for a DIN 5480 external shaft from reference diameter, module, tooth count and tolerance field and get honest numbers: the profile shift the standard derives, tip and root diameters, nominal tooth thickness, measurement over pins at nominal thickness, each proved against an independent oracle and against rows of the copy, with the form diameter and odd-z M_Re `null` until proven, and a designation that prints and parses back to the same shaft. No solid, no route, no page yet.
**Verified:** 2026-10-26T23:00:00Z (HEAD `16746fe`)
**Status:** passed
**Re-verification:** Yes. Scope is `a7a7df3..HEAD`: the DIN 5480-2 anchor follow-up (45b6565 and the two debt/idea filings), the review of it (33 of 33 findings fixed) and the resulting text changes.

## What changed, read from the diff

`git diff a7a7df3..HEAD -- src` is two files and three kinds of change: comments and docstrings in `din5480.py` and `shaft_calc.py`, and three printed strings (`THEORETICAL_PIN`, `ODD_Z_UNCONFIRMED` and the `measure_over_pins` field description). No formula, bound, default or constant moved. `git diff v0.6 --stat -- src/spur/calc.py src/spur/params.py requirements.txt` is empty. The tests gain the Part 2 anchors and a reworded pin-sentence test.

## Truth 2, checked directly (previously PASSED by override)

Truth: "d_B, tip, root and nominal thickness agree with the independent oracle and with at least two anchor rows from the copy."

**The override is no longer relied on.** It stays in the frontmatter, verbatim, as history of how the previous report passed this truth. The truth is now VERIFIED on evidence.

What I read and ran:

1. `tests/test_din5480_anchors.py` pins five designations: W 120x3x38x8f (Part 1, cl. 9.1 Fig. 6, tip only) and four DIN 5480-2:2006-05 rows (Tables 12/13 at m 1.25, 18/19 at m 2). Each Part 2 row pins x*m, s1, da1, df1, D_M and M1 as hard-coded literals with half a unit of the printed digit as tolerance. The expected values are not computed from `spur`, so the assertions cannot move with the code.
2. The four Part 2 rows each cover all four quantities of the truth (shift/d_B, tip da1, root df1, nominal thickness s1): that is four rows, not two. Two are odd tooth counts, and W 30x2x14 and W 30x2x13 sit on the two edges of the shift range (-0.05 and +0.45). The truth also asks for the oracle: `shaft_oracle.measure` is compared to the code at 1e-9 in the same test, and the oracle imports `math` only.
3. `pytest tests/test_din5480_anchors.py`: `11 passed`. With the four shaft test files: `1018 passed in 2.61s`.
4. Each value assertion bites. Eight kept logs under `investigation/31-part2-red-*.log` show the first failing assertion for: shift (`ADDENDUM_FACTOR` 0.45 to 0.46), printed shift, s1 (`tan` to `sin`), da1 alone, df1 (`H_FP` 0.55 to 0.60), the odd factor, the oracle cross-check and the odd null. I ran one more myself on a scratch copy (`/private/tmp/.../scratchpad/mut`, import path asserted to resolve there): the odd factor `cos(pi/(2*z))` replaced by `1.0` gives `2 failed, 9 passed`, both failures on the two odd rows at the M1 line (`Obtained: 36.211, Expected: 35.984`). The main tree was not touched.
5. I cannot check the 24 pinned digits against the standard: I do not hold the copy. They are the values the human approved by name (L47 amendment, 31-VALIDATION). That approval is the evidence for the digits; the tests prove the code reproduces them.

Verdict: VERIFIED. The shortfall that the override covered (one row) is gone: four independent rows from the second part, plus the Part 1 tip row.

## L08 / L05: no printed number, default or bound moved

I extracted `a7a7df3` and `HEAD` with `git archive src` into two scratchpad trees, ran one script per tree in its own process (`python -I`, `spur.__file__` asserted to be inside the tree), and compared the JSON dumps. The oracle supplied d_B so the grid lies on and around the feasible region.

Grid: 13 modules (0.5 to 10) x 77 tooth counts (6 to 82) x 4 fits (8f, 7h, 9g, 6g) x 19 reference diameters per cell (the oracle d_B at 16 profile shifts from -0.06 to +0.46, which spans both range edges, plus 25.0 and two nudged values). That is **76,076 evaluations, all distinct**: 60,108 accepted (29,668 odd z, 30,440 even z) and 15,968 refused.

| Check | Result |
|-------|--------|
| Every non-warning field of every accepted shaft (the whole `model_dump` less `warnings`) | 0 differences in 60,108 |
| Refusal text of the 15,968 refused shafts | 0 differences |
| Accepted/refused status of any cell | 0 changed |
| `ShaftParams` JSON schema (field names, defaults, bounds, patterns) | equal |
| `ShaftParams()` defaults (`model_dump`) | equal |
| Default shaft (25 / 1.25 / 18 / 8f) | non-warning output equal: tip 24.75, root 22.25, pin 2.73, M_Re 27.999, shift 0.562, thickness 2.613, form_d null |
| Warning count per shaft | equal everywhere |
| `ShaftDimensions` JSON schema | differs in exactly one string: the `measure_over_pins` description, "(unconfirmed)" became "(not given yet)". Keys, types, bounds and every other property are equal |
| Warning strings that differ | exactly two, each in the old and new form (four strings) |

The differing strings, in full:

- `THEORETICAL_PIN` (60,108 shafts). Old: "...rounded to 0.01 mm. The tool computes this pin; it has not been compared with a tabulated D_Re." New: "...rounded to 0.01 mm. DIN 5480-2 tabulates its own measuring pin D_M for the sizes it lists, and for most of them it differs from this pin."
- `ODD_Z_UNCONFIRMED` (29,668 odd-z shafts). Old: "The measurement over pins M_Re is not given for an odd tooth count until a DIN 5480 row confirms the odd-tooth formula; the pin diameter is still given." New: "The measurement over pins M_Re is not given for an odd tooth count yet; the pin diameter is still given."
- The `measure_over_pins` field description: "Null for an odd tooth count (unconfirmed) and when..." became "Null for an odd tooth count (not given yet) and when...".

L05 holds: no default, bound or field name moved. L08 holds: no number moved. Printed text changed in three places, all to say what is now true (the old pin sentence and the "until a row confirms" wording were false after the Part 2 comparison). `make gear.unchanged` is being run by the orchestrator; I did not re-run it. `calc.py`, `params.py` and `requirements.txt` are empty against `v0.6`.

## form_d and odd-z M_Re stay null

From the same grid, new tree:

| Check | Result |
|-------|--------|
| `form_d` non-null | 0 of 60,108 |
| Odd z, `measure_over_pins` non-null | 0 of 29,668 |
| Even z, `measure_over_pins` null | 0 of 30,440 |
| Odd z, `pin_d` still printed | yes (the odd sentence says so; unchanged against `a7a7df3`) |

The form sentence is in the warnings of the default shaft. `test_anchor_w120x3x38x8f_form_diameter_is_a_limit_not_a_construction` and the odd-row null assertion (seen red, `31-part2-red-odd-gate.log`) hold the two nulls.

## T-31-13: no DIN 5480 value beyond the approved ones

- `git diff a7a7df3..HEAD --name-status`: no table file, no data file; the only new files are eight red logs, one idea and one debt item. `src/spur/din5480_tables.py` is the 11-line docstring-only seam from Phase 30.
- Every DIN 5480 value in the diff is one of the approved ones: the 24 literals in `PART_2_ROWS` (4 rows x x*m, s1, da1, df1, D_M, M1), the three Part 1 values, and the D_M values 2.75 and 4.0 / 5.0 as quoted in comments and the review (the tool's own theoretical pins quoted beside them, 2.73, 2.62, 3.83, 4.72, are tool output). The red logs print the tool's wrong values on the left of `==` and the approved literal on the right.
- Other numbers are counts and ratios from the scratch comparison (719, 720, 721, 483, 44, 211, 510, 16, 11), not rows. Three docs carry min/max of unnamed rows; see the advisory. No designation outside the five approved is named with a value.
- `31-SECURITY.md` T-31-13 and T-31-15 are updated to match.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1: frozen `ShaftParams` contract; shift from d_B; epsilon edge; refusal naming the range; gear untouched | VERIFIED | Schema and defaults equal to `a7a7df3` over the grid; 15,968 refusals identical; `calc.py`/`params.py`/`requirements.txt` empty vs `v0.6`; W 30x2x14 and W 30x2x13 (the two edges) accepted and pinned to Part 2 |
| 2 | SC2: d_B, tip, root and thickness agree with the oracle and with at least two copy anchor rows | VERIFIED | Four Part 2 rows plus the Part 1 tip row, literals not derived from the code, red logs for each assertion; oracle independent (`math` only). No longer relies on the override |
| 3 | SC3: d_Ff `null` with a sentence; even-z M_Re and D_Re agree with the oracle; guard or `null`; odd z `null` | VERIFIED | form_d null 0/60,108 non-null; odd-z M_Re null in all 29,668; even z printed in all 30,440; guard branches covered by direct-call tests (passing); the odd factor itself is now confirmed by two odd rows, null is kept by the human's choice |
| 4 | SC4: designation prints and parses back; `.` and `,`; refusal names the token; fit shape only | VERIFIED | Codec code untouched by this round; codec tests pass; designation field identical in every accepted grid shaft |
| 5 | SC5: gate delta recorded; Phase 30 check green | VERIFIED | `bench/RESULTS.md` carries the delta and the Part 2 red rows. `lint-imports`: 10 kept, 0 broken (run by me). `make verify` and `make gear.unchanged`: run by the orchestrator on this tree, not by me |

**Score:** 5/5 truths verified, 0 present-but-behavior-unverified, 0 relying on an override.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/din5480.py` | formulas, constants, codec | VERIFIED | Real maths, no table data; comments only changed in this round |
| `src/spur/shaft_calc.py` | `derive_shaft`, `check_shaft`, pin guard | VERIFIED | `form_d=None` always; odd gate present; three strings changed |
| `src/spur/shaft_params.py` | `ShaftParams` | VERIFIED | Unchanged |
| `tests/shaft_oracle.py` | independent oracle | VERIFIED | Imports `math` only |
| `tests/test_din5480_anchors.py` | copy anchors | VERIFIED | 11 tests, five approved designations, literal expectations |
| `src/spur/din5480_tables.py` | Phase 34 loader seam | VERIFIED (empty by design) | Docstring only; no value |

### Key Link Verification

| From | To | Status | Details |
|------|----|--------|---------|
| `ShaftParams._feasible` | `shaft_calc.check_shaft` | WIRED | 15,968 grid refusals surface as validation errors, same text as before |
| `derive_shaft` | `din5480.*` | WIRED | All formulas called; anchors exercise `derive_shaft` and `din5480.*` directly |
| `shaft_oracle` | `spur` | INTENTIONALLY ABSENT | Oracle imports no `spur` |
| shaft maths | gear maths | ABSENT (required) | `lint-imports`: 10 kept, 0 broken |

### Data-Flow Trace (Level 4)

Not applicable: pure functions, no rendering or data source.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Anchors | `pytest tests/test_din5480_anchors.py` | 11 passed | PASS |
| Shaft tests | `pytest` on the four shaft test files | 1018 passed in 2.61s | PASS |
| No number/default/bound/refusal moved | scratch compare, `a7a7df3` vs `HEAD`, 76,076 evaluations | 0 non-warning diffs, 0 refusal diffs, params schema and defaults equal | PASS |
| Nulls hold | same grid | form_d 0 non-null; odd-z M_Re 0 non-null; even-z 0 null | PASS |
| Odd-factor mutation bites | scratch copy, `centre_circle *= 1.0` | 2 failed (both odd rows), 9 passed | PASS |
| Lint, types | `ruff check src tests`; `mypy --strict` on din5480, shaft_calc, shaft_params | clean | PASS |
| Import contracts | `lint-imports` | 10 kept, 0 broken | PASS |
| Full gate and gear check | orchestrator: `make verify`, `make gear.unchanged` | cited, not re-run by me | CITED |

### Probe Execution

SKIPPED: no probes declared by this phase.

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|-------------|-------------|--------|----------|
| REQ-shaft-params | 31-01, 31-04, 31-05, 31-06 | SATISFIED | Schema and defaults equal to `a7a7df3`; validated once at the boundary |
| REQ-profile-shift-from-dB | 31-01, 31-02, 31-05, 31-06 | SATISFIED | Shift from d_B pinned on four Part 2 rows incl. both edges; range narrower than the copy's exceptions is filed (must debt, 11 rows refused) and errs toward refusing |
| **REQ-shaft-basic-dims** | 31-01, 31-02, 31-04, 31-05, 31-06 | **SATISFIED: can be marked complete** | Oracle agreement, plus four Part 2 rows and one Part 1 row, all four quantities covered by the Part 2 rows. The only thing that held it Pending (one anchor row, not two) is gone |
| REQ-form-diameter-honest | 31-03, 31-05, 31-06 | SATISFIED | form_d null for every shaft, with a sentence; Part 2 prints d_Ff1 only as a maximum, so the construction is never printed |
| REQ-mre-nominal | 31-03, 31-05, 31-06 | SATISFIED | Even z agrees with the oracle and with M1 of Part 2 at the tabulated pin; odd z null by the human's choice (see advisory) |
| REQ-designation-codec | 31-04, 31-06 | SATISFIED | Unchanged since the last report; tests pass |

No orphans. REQUIREMENTS.md still shows REQ-shaft-basic-dims unchecked (line 60) and Pending (line 164); I did not edit it.

### Anti-Patterns Found

None. `grep TBD|FIXME|XXX|TODO|HACK` over the phase's source and test files is empty. The previous report's IN-10 and IN-11 advisories (stale docstring and stale comment) are fixed in this diff, so they are closed, not carried.

### Human Verification Required

None. The one human decision this round needed was making the four rows available and approving them by name; it is recorded in the L47 amendment.

### Gaps Summary

No open gaps. The anchor shortfall that the override covered is closed on evidence: four DIN 5480-2 rows, pinned as literals, each seen red, plus the Part 1 tip row. No printed number, default, bound, refusal or schema field changed across 76,076 evaluations; only three printed strings did, each to a more accurate sentence. The nulls (form_d, odd-z M_Re) hold. The open items are two must-severity debt entries (form-diameter construction above Part 2's maximum, for Phase 34; shift range narrower than the exceptions) and an idea (print odd-z M_Re), all filed and none blocking this phase. Three advisories are above.

**REQ-shaft-basic-dims verdict: SATISFIED. The orchestrator can mark it complete** (line 60 to `[x]`, line 164 to `Complete`).

---

_Verified: 2026-10-26T23:00:00Z_
_Verifier: Claude (gsd-verifier)_
