# Eleven composed-solid cutout volumes are 6 dp literals asserted at rel=1e-6

Severity: nice
Status: active
Date: 2026-10-03
Source: 14-02 Task 3 (tightening the shared cutout assertion to abs=1e-9); narrowed by 14-04 (14-UAT.md G-14-5)
Related files:
- tests/test_model.py (`test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore`,
  `test_the_recess_fillet_and_cutout_proofs_hold_with_a_single_sided_recess`,
  `_assert_the_cutout_is_what_derive_prints`'s `volume_rel` and `volume_abs`, `_holes_volume`)

## Context
Phase 14 asserts the four cutout proof rows (holes, sharp spokes, filleted spokes, cells)
at `abs=1e-9` mm3 against closed forms. Fifteen further rows reuse the same assertion on
composed solids (a tip chamfer or a one-sided recess together with a cutout).

Since 14-04, four of them assert the web formula `6*pi*(hole_d/2)**2*web` (`_holes_volume`)
instead of a literal, because the six holes lie wholly inside the recess annulus: the d-flat,
round and keyed holes rows (tip chamfer, both recesses) and the single-sided holes row.
Measured 2026-10-03 on cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1, their kernel-formula gaps
are 5.85e-10, 5.94e-10 and 6.55e-10 mm3 on the three tip rows and 2.79e-12 mm3 on the
single-sided row (copied from the test docstrings). The tip chamfer causes the tip rows'
offset: the d-flat row without it measured 1.36e-12 mm3. So the three tip rows assert at
`abs=1e-8` (about 15x their largest gap, the human's answer at 14-04's checkpoint, logged
in L33) and the single-sided row at `abs=1e-9`.

The other eleven keep a 6 dp literal at `volume_rel=1e-6`, because their closed form is
not derived here: the d-flat, round, hex and keyed spokes and cells rows, hex-holes, and the
single-sided spokes and cells rows. A 6 dp literal cannot meet 1e-9. They keep the bar
they had before Phase 14, so the shared assertion keeps its `abs=1e-9` default for every
formula row.

## Why it matters
Those eleven rows would catch a wrong-but-stable cutout only if it moved the volume by more
than one part in a million (about 2.6e-4 mm3 on the 264 mm3 hex-holes row). A systematic
error smaller than that on a composed solid is invisible. The composition itself is what
these rows prove; the cutout's own volume is proven to 1e-9 on the plain solid.

## Next step
Derive the eleven. For the spokes and cells rows, the form is a polar (spokes) or
polygon-versus-circle (cells) integral split at the recess radii, plus the floor fillet's
torus on the single-sided rows. For hex-holes, it is the web formula plus the full-thickness
sliver where the holes cross the hex-shifted recess outer wall at 11.994 mm
(`_filleted_spoke_volume` is the precedent for a derived oracle). A derived tip-chamfered
row meets the kernel offset 14-04 measured, so measure it against the bar before it moves.
Revisit when the kernel pair is bumped, or when a composed-solid row is next re-pinned.
