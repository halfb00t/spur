# Phase 32: The Shaft Solid - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-27
**Phase:** 32-the-shaft-solid
**Areas discussed:** Root form in the solid, End chamfer meaning, Shank vs spline rules, Bounds sweep policy

---

## Root form in the solid

| Option | Description | Selected |
|--------|-------------|----------|
| Radial + root arc | The involute runs as low as the geometry allows, then a radial line and an arc at root_d. Same idea as the gear's default. | ✓ |
| Rack-generated trochoid | The hob's fillet (h_fP 0.55, rho_fP 0.16). rho_fP is unconfirmed, and the construction sits above d_Ff1 max on 483/719 rows. | |
| Opt-in like the gear | Radial default plus a root_shape field (L38 pattern). New field, new scope. | |

**User's choice:** Radial + root arc

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, one sentence | A warning says the root fillet is a construction, not the hob's cut. | ✓ |
| No sentence | No printed number depends on the fillet. | |

**User's choice:** Yes, one sentence

---

## End chamfer meaning

| Option | Description | Selected |
|--------|-------------|----------|
| 45°, size at the tip | Fixed 45° cone; the axial length equals the radial depth. | ✓ |
| 30° lead-in, axial length | Shallower cone; the radial depth is the length times tan 30°. | |
| Angle as a new field | A ninth field. | |

**User's choice:** 45°, size at the tip

| Option | Description | Selected |
|--------|-------------|----------|
| Cap and warn | L29/L45 precedent; capped at the tooth height and splined_length. | ✓ |
| 422 naming end_chamfer | Letter of L03; a default chamfer could cause a 422. | |
| 422 if set, cap if default | Needs fields-set tracking across all interfaces. | |

**User's choice:** Cap and warn

| Option | Description | Selected |
|--------|-------------|----------|
| New end_chamfer_effective key | L45 pattern, null when not cut; L47 amendment for a 13th key. | ✓ |
| Warning sentence only | The twelve keys stay. | |

**User's choice:** New end_chamfer_effective key

---

## Shank vs spline rules

| Option | Description | Selected |
|--------|-------------|----------|
| All, no cross-field refusal | Every regime gets a kernel row with the closed-form volume. | ✓ |
| Refuse below root_d | A 422 as policy, not geometry. | |
| Require shank_d ≥ tip_d | Refuses turned-down designs. | |

**User's choice:** All, no cross-field refusal

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, when a shank exists | Geometry-only sentence: no relief groove, no run-out, full-form prism. | ✓ |
| No warning | The field help suffices. | |

**User's choice:** Yes, when a shank exists

---

## Bounds sweep policy

| Option | Description | Selected |
|--------|-------------|----------|
| Lower bounds until it fits | No shaft link exists until Phase 33. | ✓ |
| Keep bounds, document 503 | L37 precedent. | |
| Stop and ask with numbers | One extra round trip. | |

**User's choice:** Lower bounds until it fits

| Option | Description | Selected |
|--------|-------------|----------|
| Solid fields; ask for spline | The four solid fields are free; stop and ask before moving a spline bound. | ✓ |
| All eight fields' bounds | Log any change as an L47 amendment. | |

**User's choice:** Solid fields; ask for spline

---

## Claude's Discretion

- Flank representation (polyline vs makeSpline), the root arc size, the small-z involute join and the tip corner.
- Read-back tolerances, sweep rows, and the gate delta.
- `enabled_when` on shank fields now or in Phase 33.
- Cache sharing between parts, measured if memory changes.

## Deferred Ideas

- A trochoid root / `root_shape` on the shaft (revisit with the form-diameter debt, Phase 34).
- An `end_chamfer_angle` field.
- A relief groove or hob run-out zone.
