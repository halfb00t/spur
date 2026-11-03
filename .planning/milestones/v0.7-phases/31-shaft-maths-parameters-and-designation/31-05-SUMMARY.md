---
phase: 31-shaft-maths-parameters-and-designation
plan: 05
subsystem: shaft-maths
tags: [din5480, checkpoint, human-action, partial-pass, tech-debt]

requires:
  - phase: 31-shaft-maths-parameters-and-designation
    provides: the formulas, the oracle, pins and the guard, the designation codec (31-01 to 31-04)
provides:
  - the whole gate green on the pre-checkpoint tree (investigation/31-05-verify.log)
  - the prediction script and table from the shipped pipeline (investigation/31-05-predictions.py and .log)
  - the checkpoint result: three approved rows from DIN 5480-1:2006-03 compared, ten clause answers recorded, divergences listed against file and line
  - a must-severity debt item for the anchor rows Part 1 cannot supply
affects: [31-06, phase-33, phase-34]

plan_head_before: 6aa09e4362444c9b79e815e717a20b93362b4668
plan_head_after: 0c03aa012c78f7b2adc69ff057103db7453f75be

actuals:
  tokens: 5900    # chars/4 (23062 chars) over the script, the predictions log, the debt item and this SUMMARY; the verify log is evidence, not counted
  tasks: 2
  commits: 2      # measured: git rev-list --count 6aa09e4..HEAD, before this SUMMARY's own commit

tech-stack:
  added: []
  patterns:
    - "a checkpoint that compares typed values to the digit the copy prints, with the limit rows checked as limits"

key-files:
  created:
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-05-predictions.py
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-05-predictions.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-05-verify.log
    - docs/tech_debt/active/2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing.md
  modified:
    - docs/tech_debt/INDEX.md

key-decisions:
  - "The checkpoint is a PARTIAL PASS: Part 1 has no size tables, so the anchor minimum (two basic-dimension rows, W30x2x14 ideally) is not met; 31-06 may proceed and pins the three approved rows only"
  - "Odd-z M_Re stays unprinted: no odd-z row was supplied"
  - "d_Ff is checked as a limit (predicted <= printed max for a shaft), not as equality, unless Part 2 prints a construction value"
  - "s and M agree to the last printed digit (|ours - copy| <= half a unit)"

requirements-completed: []

duration: continuation about 10 min (task 1 ran in the earlier session)
completed: 2026-10-26
status: complete
---

# Phase 31 Plan 05: The DIN 5480 Checkpoint Summary

**The gate was green before the human was asked, and the copy's three approved W 120x3x38x8f values agree with the shipped code to the last printed digit (d_a1, M1 minimum) or as a limit (d_Ff1 maximum); the checkpoint is a partial pass, because DIN 5480 Part 1 holds no size tables, and one printed number (root_d) is process-dependent in the copy where the code states one process.**

## Performance

- **Duration:** continuation about 10 min; task 1 (gate and table) ran in the earlier session
- **Completed:** 2026-10-26
- **Tasks:** 2 (the tracer and the checkpoint)
- **Files modified:** 5 (script, two logs and the debt item with its INDEX row; the verify log is task 1's)

## Accomplishments

- Task 1 (`9e523f2`): `make verify` green, `2349 passed in 198.91s (0:03:18)`; the five-shaft table matches the research table. `src/` and `tests/` are untouched.
- Task 2: the human's answer is recorded below; the three approved rows are re-computed by the shipped functions and appended to `31-05-predictions.log`.
- A debt item filed for what Part 1 cannot supply (path in the last section).

## Checkpoint result

**Source and provenance.** DIN 5480-1:2006-03, read by the human from an unofficial English translation marked as an uncontrolled copy. Every citation below is to that document. No clause text and no table is copied here; only the three values the human approved by name are committed (T-31-13). Fig. 6 is an example in the standard, not normative.

**Verdict: PARTIAL PASS.** The plan's minimum was two basic-dimension anchor rows (W30x2x14 ideally), one d_Ff row and, if odd-z M_Re is to print, one odd-z row. Part 1 has no basic-dimension size tables, so the supplied evidence is one designation only: one basic-dimension row (d_a1), one d_Ff limit row and one measurement-over-pins row. The human decided: record a partial pass, let 31-06 proceed, pin the three approved rows, and file the rest as debt. The checkpoint is therefore not a proof across the size range; the phase's remaining claims rest on the formula confirmations (A1 to A10) and the vendor vectors.

### Approved rows (Block B) against the shipped code (Block C rule)

All three are W 120x3x38x8f, DIN 5480-1:2006-03, cl. 9.1, Fig. 6.

| Quantity | Copy | Ours | Rule | Verdict |
|---|---|---|---|---|
| d_a1 (tip, shaft) | 119.40 | 119.4000 (`din5480.tip_diameter(120, 3)`, in the log) | \|ours - copy\| <= 0.005 | agrees |
| d_Ff1 (max), shaft | 113.91 | internal construction 113.8802 at h_fP 0.55 and 113.5823 at 0.60 (never printed; `form_d` is null) | a limit: predicted <= printed max | holds; margin 0.03 at 0.55. This is not a proof of the construction, so `form_d` stays null (D-12, L08) |
| M1 minimum at D_M 6.000 and the row's own s 6.180 | 125.956 | 125.9560 (`din5480.measure_over_pins(3, 38, 6.180, 6.000)`; 125.95596 unrounded) | \|ours - copy\| <= 0.0005 | agrees (difference 0.00004) |

The M1 row uses the standard's gauge pin of 6.000 and the row's own thickness, not the code's printed pin (5.93) and nominal thickness (M_Re 125.9018 at s 6.2712); those are different inputs, which is why the code's `measure_over_pins` field does not equal the copy's M1.

### Answers A1 to A10 and C, as citations

| # | Item | Citation / answer | Against the code |
|---|---|---|---|
| A1 | shift from d_B | Part 1, cl. 6, Table 3: matches | consistent (`din5480.py:66`) |
| A2 | tip and h_aP | Part 1, cl. 6, Table 3: matches | consistent (`din5480.py:19-22`, `:79`) |
| A3 | root and h_fP | Part 1, cl. 6, Table 3 and cl. 7.1: formula matches; h_fP depends on the process, four processes named; a hobbed shaft's root is the theoretical root less 0.1*m | DIVERGES, see D1 and D2 |
| A4 | thickness | Part 1, cl. 6, Table 3: matches | consistent (`din5480.py:92`) |
| A5 | M_Re even | Not in Part 1 (refers to DIN 5480-15, 5.2.4.3 and Part 2); Part 1 symbols are D_M, M1, M2; the formula reproduces Fig. 6 (human's own computation, and the M1 row above by the shipped code) | symbol divergence D4 |
| A6 | M_Re odd | Part 1, cl. 4, eq. (1): equivalent to the code's odd factor; M2 is negative per DIN 3960 | consistent in form (`din5480.py:138-139`); stays unprinted, no odd-z row (`shaft_calc.py:46`) |
| A7 | shift range | Part 1, cl. 4 and Table 3: the code's range for the shaft; the copy also permits exceptions above it at larger tooth counts; the hub is the reverse | DIVERGES, see D3 |
| A8 | fit notation | Part 1, cl. 8 Example 1 and Table 7: `8f` is the spelling; the deviation letters and quality classes are a bounded set; Table 9 lists the common combinations | shape-only check is wider, see D5 |
| A9 | d_Ff | Part 1, Tables 3 and 4: limits tied to the mating part's tip diameter and a minimum clearance, not a construction; Fig. 6 prints the limits | consistent with D-12 (`shaft_calc.py:86`, `form_d` null) |
| A10 | D_Re gauge series | Not named in Part 1; DIN 3977 is only in the bibliography; Fig. 6's D_M is an example, not a series | consistent: the pin step stays 0.01 mm (`shaft_calc.py:28`) |
| C | d_Ff agreement rule | s and M: agreement to the last printed digit; d_Ff: a limit check unless Part 2 prints a construction value | applied above |

### Divergences against the code (nothing is edited in this plan)

The human's go-ahead for a fix: **not given for any of D1 to D5**. Each is for the orchestrator to put to the human before 31-06 (D-09 step 1). The numeric values named in the answers (the cold-rolling factor, the shift exceptions, the letter and class set) are in the checkpoint conversation and are not repeated here.

- **D1 (can make a printed number wrong for a user): root_d is the theoretical root only.** The copy (cl. 6 Table 3, cl. 7.1) makes the root diameter depend on the production process; a hobbed shaft's root is the theoretical root less 0.1*m. The code has one constant `H_FP = 0.55` (`din5480.py:30`, comment at `:27-29` says "the copy decides"), prints `root_d` from it (`shaft_calc.py:176`), and describes the field as just "Root diameter." (`shaft_calc.py:81`) with no warning (`shaft_calc.py:34-48`). 0.55 is the broaching and theoretical value; the already-computed h_fP 0.60 gives the hobbed root exactly (113.100 = 113.400 - 0.1*3 for W 120x3x38). A user who hobs the shaft and reads `root_d` is given a diameter 0.1*m too large. This is a decision, not an arithmetic error: either label the value as the theoretical root and warn, or add a process choice (which would be a user parameter, so L05 and L03 apply). Needs the human; D-07.
- **D2 (labelling, no printed number): the h_fP mapping.** The plan's A3 and the research name the 0.65 factor "shaping". The copy names the 0.65 process mill-broaching, and names a further process (cold rolling) with a larger factor. `form_diameter`'s validity comment (`din5480.py:149-150`, "for h_fP up to 0.65, plan-time check") covers neither the larger factor nor, therefore, any future use of it. No current output depends on it; the plan-time check must be repeated if a process factor above 0.65 is ever used.
- **D3 (refusal, not a wrong number): the shift range is narrower than the copy's.** `X_MAX = 0.45` (`din5480.py:34`) is enforced by `check_shaft` (`shaft_calc.py:105-120`), which refuses a combination the copy allows as an exception at larger tooth counts. The range for `form_diameter` is also stated to +0.45 (`din5480.py:149-150`). This errs on the honest side (L08, L03) but turns a valid standard shaft away. Needs the human: which tooth counts and what bound the exception has is in the copy, not in the code.
- **D4 (naming): symbols.** Part 1 calls the pin diameter D_M and the measures M1 and M2 (D_Re and M_Re are the later parts' names). The code, its warnings and the API descriptions say D_Re and M_Re (`shaft_calc.py:42-43`, `:46-47`, `:91`, `:95`, `:146`, `:152`). `THEORETICAL_PIN` also states "It is not the D_Re that DIN 5480 tabulates" (`shaft_calc.py:42-43`); Part 1 does not show that tabulation, so that sentence is unverified against any copy page seen so far (the debt item covers the Part 15 source).
- **D5 (no number involved): the fit check is wider than the standard's set.** `FIT_PATTERN` (`din5480.py:37`, used at `shaft_params.py:35`) accepts one or two digits and any lower-case letter. The standard's classes and letters are a bounded set, so `W 25x1.25x18x3z` parses and is echoed back as a designation (`shaft_calc.py:181`). `fit` takes part in no computed value. The code says so (`shaft_params.py:34`: the tables are Phase 34's), so this is by design (D-02), noted here so Phase 34 tightens it.

No contradiction found for A1, A2, A4, A6 (form), A9 or A10.

## Deviations from Plan

None. The plan's minimum anchor set was not reachable (Part 1 has no size tables); the human's decision to record a partial pass and file debt is the sanctioned route, not an executor deviation.

## Known Stubs

None.

## Threat Flags

None. No `src/` or `tests/` file changed; no table file was created. Only three approved values, each cited, were committed; the copy's other values and all clause text stayed out of the repository (T-31-13).

## Tech debt filed

`docs/tech_debt/active/2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing.md` (Severity: must; trigger: pages of DIN 5480 Part 2 or Part 15 become available), with its row in `docs/tech_debt/INDEX.md`, in commit `0c03aa0`.

## Next Phase Readiness

31-06 may proceed on the partial pass. It pins exactly the three approved rows (d_a1, d_Ff1 maximum as a limit, M1 minimum at the row's own s and D_M), cites them as DIN 5480-1:2006-03 cl. 9.1 Fig. 6 read from an unofficial translation, and applies D-09 to D1 to D5 only with the human's go-ahead. D1 should be put to the human first: it is the one divergence that can print a wrong root diameter.

## Self-Check: PASSED

- `31-05-predictions.py`, both logs and the debt item exist; `9e523f2` and `0c03aa0` are ancestors of HEAD.
- `git status --porcelain -- src tests` prints nothing.
