# The filleted-spoke removed-volume proof has no closed-form cross-check

Severity: must
Status: active
Date: 2026-09-29
Source: 11-REVIEW.md WR-05 (external: codex, extended)
Related files:
- tests/test_model.py (`test_each_cutout_is_exactly_what_derive_prints_on_the_built_solid`,
  `test_the_cutout_proof_fails_when_the_cutout_step_is_skipped`, lines ~1224-1240 and
  ~1186-1263)
- src/spur/model.py (`_fillet_corner`, `inside=True` branch)
- docs/architecture/decision_log.md (L30: "no closed form for a filleted sector's removed
  volume -- pinned, not derived")

## Context
Every other cutout pattern's removed-volume assertion is checked against an independent
closed-form area/volume formula to 1e-9 mm3 (the project's own stated bar): holes against
`pi * r^2 * face_width`, sharp spokes against the bar-area formula, honeycomb cells
against the hexagon-area formula. The filleted-spoke case — the one pattern that exercises
the new, non-trivial `_fillet_corner(inside=True)` mirrored-quadratic tangent-circle
geometry added by this phase — is checked only against a pinned literal
(`d_volume=2934.725405`) measured once on the current kernel, exactly as L30 already
states. The reviewer independently re-derived the `inside=True` tangent-circle math
outside pytest and found it geometrically self-consistent for the case tried, so there is
no known defect today — but the pinned-only check means a systematic geometry error in
this code path (wrong tangent root, wrong sign, wrong side) would be invisible to
`make verify` forever: any wrong-but-stable value the kernel produces gets captured as
"correct" the first time such a test is written. The `isInside()` hub/rim-wall probe in
the same test provides some independent signal but never touches the fillet radius
itself.

## Why it matters
A silent regression in `_fillet_corner`'s `inside=True` branch — or a future OCP/CadQuery
kernel bump that changes tangent-circle root selection at the margins — would move the
pinned literal without any independent formula flagging the drift as wrong rather than as
a new "measured" baseline to re-pin. That is exactly the failure mode L08 exists to
prevent for every other cutout pattern; the filleted-spoke row is the one gap.

## Next step
Derive an independent closed-form for the filleted-sector volume (the sharp-sector area
minus four circular-segment corrections of radius `spoke_fillet_effective(p)`, the same
shape as the sharp-bar formula already used) and assert against it to the same 1e-9 mm3
bar the other three patterns get. The phase itself already decided the filleted row stays
pinned for now (decision log L30) — this file exists so that decision has a named trigger
instead of living only in a docstring comment.

## Revisit when
`_fillet_corner` is next touched (a bugfix, a sign-convention change, a mirrored-branch
edit), or the pinned CadQuery/OCP kernel version is bumped — either event invalidates the
pinned literal's provenance and is the moment to either re-derive the closed form or
re-pin with fresh measurement plus this same absent cross-check.
