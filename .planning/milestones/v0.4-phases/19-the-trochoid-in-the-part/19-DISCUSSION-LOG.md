# Phase 19: The Trochoid in the Part - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-08
**Phase:** 19-The Trochoid in the Part
**Areas discussed:** The two new fields, Root numbers under the trochoid, Undercut waist floor, The flip's schedule (Phase 20)

---

## The two new fields

| Option | Description | Selected |
|--------|-------------|----------|
| Reinterpret root_fillet as ρ | One knob; root_fillet is the hob tip radius in trochoid mode, the analytic fillet in radial mode; capped and warned by cutter() | ✓ |
| New field cutter_tip_radius (mm) | Separate mm field; root_fillet ignored-and-warned under trochoid (L27 precedent) | |
| New field, ρ as a module factor | ISO 53 style ρ*; breaks L05's absolute-mm rule | |

**User's choice:** Reinterpret root_fillet as ρ (recommended)

| Option | Description | Selected |
|--------|-------------|----------|
| root_shape: radial \| trochoid | Research candidate; values fixed by 18 D-03; Literal, default radial, group Teeth | ✓ |
| root_mode: radial \| trochoid | Matches calc.root_mode's name | |
| root: analytic \| hob | Shorter; diverges from the Phase 18 literal | |

**User's choice:** root_shape: radial | trochoid (recommended)
**Notes:** "Next area" after two questions; help text, README row and form placement left to Claude.

---

## Root numbers under the trochoid

| Option | Description | Selected |
|--------|-------------|----------|
| Null + warning | root_thickness/root_gap widen to float \| None with one warning; radial mode unchanged | ✓ |
| Redefine at the form circle | Both keep a number at the cutter-envelope junction, root_form_d beside them | |
| Null the old two, add form-circle fields | New form_thickness/form_gap fields | |

**User's choice:** Null + warning (recommended)

| Option | Description | Selected |
|--------|-------------|----------|
| Ship root_form_d, labelled cutter-envelope junction | 2× junction radius, 3 dp, null in radial mode; never ISO 21771 | ✓ |
| Do not ship it | No new number | |

**User's choice:** Ship it (recommended)

| Option | Description | Selected |
|--------|-------------|----------|
| In the existing root_fillet derived field | derive() prints the capped ρ under trochoid; description names the cap by mode | ✓ |
| New derived field cutter_tip_radius | Two numbers for one knob | |

**User's choice:** In the existing root_fillet derived field (recommended)

---

## Undercut waist floor

| Option | Description | Selected |
|--------|-------------|----------|
| Print the waist, warn below a floor | New derived field; one warning naming teeth, profile_shift, pressure_angle; the gear still builds | ✓ |
| 422 below the floor (L03) | Refuse naming the three fields; no preview | |
| Refuse like tooth severed | Radial fallback with a new reason | |

**User's choice:** Print the waist, warn below a floor (recommended)

| Option | Description | Selected |
|--------|-------------|----------|
| Measured in the phase, then pinned | Bench finds where the built waist stops being a tooth; floor set with headroom, recorded with date and host | ✓ |
| A module fraction, e.g. 0.1·m | Picked before the measurement | |
| An absolute mm value, e.g. 0.2 mm | MIN_WALL-style floor | |

**User's choice:** Measured in the phase, then pinned (recommended)

---

## The flip's schedule (Phase 20)

| Option | Description | Selected |
|--------|-------------|----------|
| Defer past v0.4, named trigger | Phase 20 Skipped (O4, flip deferred); the Lxx names the trigger and regen rules | ✓ |
| Run Phase 20 in v0.4 | One flip commit after 19; narrow or broad definition next | |
| Decide after Phase 19's measurements | Lxx records the choice open with a checkpoint at Phase 19's close | |

**User's choice:** Defer past v0.4, named trigger (recommended)

| Option | Description | Selected |
|--------|-------------|----------|
| A real fit report or a mating-pair request below z_min | The 2026-09-21 idea file's own trigger | ✓ |
| The next milestone that touches root geometry | Tied to work, not demand | |
| You decide the wording | Claude writes it from the two above | |

**User's choice:** A real fit report or a mating-pair request below z_min (recommended)

---

## Claude's Discretion

- root_fillet help text and README wording; root_shape's position in the Teeth group; the waist field's name and the warning sentences.
- The kernel-tier bar and sample count after the deviation methods are reconciled; the structural guards' thresholds.
- How _outline carries the spline per side; how spline_start / tip_chamfer_limit are threaded the junction radius.
- The compose matrix's rows; the bench script shape for the waist floor and the heaviest low-tooth row.
- The Lxx's placement and the exact superseding/amending wording for L09, L10, L33.

## Deferred Ideas

- The default flip (Phase 20): Skipped (O4, flip deferred), owned by REQUIREMENTS.md "Trochoid follow-ups" with the named trigger.
- Form-circle thickness/gap fields (rejected in D-03).
- A separate cutter_tip_radius field (rejected in D-01).
