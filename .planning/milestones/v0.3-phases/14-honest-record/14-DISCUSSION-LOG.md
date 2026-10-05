# Phase 14: Honest Record - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-02
**Phase:** 14-honest-record
**Areas discussed:** Warning text & threshold, Volume bar conflict, Closed form & tripwire, The record

Scouting before the questions found two things the requirements do not settle, both put
to the human: the shared removed-volume assertion is `rel=1e-6` while the record claims a
`1e-9 mm³` bar (an evidence conflict), and `src/spur/model.py:138` repeats README's
"non-working root zone" claim. All four areas offered were selected.

---

## Warning text & threshold

**What does the warning say about the chord's deviation from the involute?**

| Option | Description | Selected |
|--------|-------------|----------|
| No number | "…where it deviates from the involute." The 35 µm figures have no script in the repo; REQ allows quoting none. | ✓ |
| Per-gear, computed | calc.py computes this gear's max chord-to-involute distance and prints it. New product maths. | |
| Static bound, re-measured | A bench/ script re-measures the bound on the three configs; honest only with a sweep. | |

**When does the warning fire — raw float or at the printed 3-dp resolution?**

| Option | Description | Selected |
|--------|-------------|----------|
| Printed resolution | Fire when round(height, 3) > 0; 10-REVIEW CR-01's rule. | ✓ |
| Raw float | spline_start > pr.r exactly; can print "0.000 mm above". | |

**Which field(s) step across the crossing in the tests?**

| Option | Description | Selected |
|--------|-------------|----------|
| profile_shift + root_fillet | The two drivers README names, one step either side each. | ✓ |
| profile_shift only | The debt file's own axis. | |
| All three: x, root_fillet, module | Adds a module pair (m 3.95 / 4.05 at x 1.0, pa 14.5). | |

**Does the sentence name a remedy, or just the fact?**

| Option | Description | Selected |
|--------|-------------|----------|
| Fact + cause, no remedy number | "…where it deviates from the involute: the root fillet is larger than half the dedendum." | ✓ |
| Fact only | Shortest; user infers the cause. | |
| Fact + the fillet that keeps it below | Adds a computed settable number; a second thing to prove. | |

**User's choice:** all four recommended options.
**Notes:** After the area closed, the step rows were measured on the pinned code: at the
default 25° pressure angle the 0.5 mm fillet is capped at x 0.65/0.70 and no crossing
occurs — the profile-shift pair sits at pa 14.5 (x 0.65 −0.050 / 0.70 +0.0375); the
root-fillet pair at {x 0.75, pa 20} (0.40 −0.075 / 0.45 +0.025). The formula
`height = 2·root_fillet(p) − (1.25 − x)·m` reproduces the debt file's three numbers exactly.

---

## Volume bar conflict

**Which bar does the phase assert?** (today: `pytest.approx(d_volume, rel=1e-6)`)

| Option | Description | Selected |
|--------|-------------|----------|
| abs=1e-9 mm³ on all four rows | Make the claim true after measuring each row's kernel–formula gap in-phase. | ✓ |
| Keep rel=1e-6; record the agreement | Two numbers in the docstring and the Lxx. | |
| Tighten the filleted row only | Inconsistent bars inside one proof. | |

**If the filleted row's measured gap reads above the chosen bar, what happens?**

| Option | Description | Selected |
|--------|-------------|----------|
| Halt at a checkpoint with the numbers | 13 D-09's shape; the human picks. Never loosened silently. | ✓ |
| Loosen to the measured gap, record it | Risks baking a formula error in as a 'measured' bar. | |

**REQUIREMENTS.md / ROADMAP SC3 say the three rows "already meet" 1e-9. Correct it in this PR?**

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, in this PR | One sentence each: measured to 1e-9, asserted at rel 1e-6 until this phase. | ✓ |
| No, leave it; the Lxx states the facts | Planning docs are history. | |

**User's choice:** all three recommended options.
**Notes:** none.

---

## Closed form & tripwire

**Where does the closed form and its derivation live?**

| Option | Description | Selected |
|--------|-------------|----------|
| Test helper beside _spoke_bar_area | Pure math in tests/test_model.py, derivation in the docstring; the sharp-spoke precedent. | ✓ |
| bench/ script, imported by the test | A runnable derivation; crosses a boundary. | |

**Does the oracle solve the tangent geometry itself, or take the points from `_fillet_corner`?**

| Option | Description | Selected |
|--------|-------------|----------|
| Independent scalar solve | The helper re-derives the tangent points; a wrong root in model.py disagrees with it. | ✓ |
| Reuse _fillet_corner's points, compute areas only | Inherits model.py's root selection; does not retire the debt. | |

**What does the tripwire perturb in the inside=True solve?**

| Option | Description | Selected |
|--------|-------------|----------|
| Small shift of the root, valid solid | t + 0.01 mm; the part still builds; abs=1e-9 goes red. | ✓ |
| The far root (gross) | Likely a BuildError rather than a wrong volume. | |
| Both, as two rows | Two kernel builds for two claims. | |

**The tripwire parametrization carries the pinned literal 2934.725405. With the literal demoted, that row…**

| Option | Description | Selected |
|--------|-------------|----------|
| Takes d_volume from the same helper | One oracle shared by proof and tripwire. | ✓ |
| Keeps the literal | A second copy of the number being demoted. | |

**User's choice:** all four recommended options.
**Notes:** none.

---

## The record

**How many decision-log entries does the phase add?**

| Option | Description | Selected |
|--------|-------------|----------|
| One L33, two parts | L26–L32 are one per phase; two headed sections, one Reason. | ✓ |
| Two: L33 lead-in, L34 closed form | One id per topic; breaks the pattern. | |

**`src/spur/model.py:138` (`_outline` docstring) repeats the "non-working root zone" claim. Fix it?**

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, in the README commit | Same false claim; prose-only src/ change; fixture untouched. | ✓ |
| No — not in the requirement | The claim stays false in the code's comments. | |

**What does README's root-fillets bullet say about the condition and the numbers?**

| Option | Description | Selected |
|--------|-------------|----------|
| Formula + the default's number | 1.188 mm below on the default gear; above when root fillet > (1.25 − x)·m/2. Both proven by the tests. | ✓ |
| Condition in words, no numbers | REQ's own wording. | |
| Formula, no number | | |

**User's choice:** all three recommended options.
**Notes:** none.

---

## Claude's Discretion

- The warning's position in the tuple and its exact wording within the agreed content.
- Helper and test names; whether the module step pair is added.
- The tripwire's mechanism (perturbed copy vs wrapper) and the shift size.
- Plan order and L33's commit placement; the L33 title.
- Whether the per-row 1e-9 measurements also get a `bench/RESULTS.md` section (default: no).

## Deferred Ideas

- A per-gear chord-to-involute deviation in `derive()` (a `docs/ideas/` candidate).
- A `bench/` sweep of the chord deviation across the field ranges.
- The outline change keeping the lead-in below the pitch circle (already in REQUIREMENTS "Future").
- Refreshing `.planning/codebase/*.md` (process).
