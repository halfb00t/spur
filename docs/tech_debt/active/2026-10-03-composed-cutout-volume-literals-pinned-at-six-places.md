# The composed-solid cutout volumes are 6 dp literals asserted at rel=1e-6

Severity: nice
Status: active
Date: 2026-10-03
Source: 14-02 Task 3 (tightening the shared cutout assertion to abs=1e-9)
Related files:
- tests/test_model.py (`test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore`,
  `test_the_recess_fillet_and_cutout_proofs_hold_with_a_single_sided_recess`,
  `_assert_the_cutout_is_what_derive_prints`'s `volume_rel`)

## Context
Phase 14 asserts the four cutout proof rows (holes, sharp spokes, filleted spokes, cells)
at `abs=1e-9` mm3 against closed forms. Fifteen further rows reuse the same assertion on
composed solids (a tip chamfer or a one-sided recess together with a cutout). Their
`d_volume` is a literal measured to 6 decimals on the pinned kernel, because no closed
form exists after an arbitrary boolean, and a 6 dp literal cannot meet 1e-9. They pass
`volume_rel=1e-6`, the bar they had before Phase 14, so the shared assertion keeps its
`abs=1e-9` default for every formula row.

## Why it matters
Those rows would catch a wrong-but-stable cutout only if it moved the volume by more than
one part in a million (about 2.6e-4 mm3 on a 264 mm3 row). A systematic error smaller than
that on a composed solid is invisible. The composition itself is what these rows prove;
the cutout's own volume is proven to 1e-9 on the plain solid.

## Next step
Revisit when the kernel pair is bumped: re-measure the fifteen literals at full precision
and decide then whether to pin them at 1e-9, or derive them as the plain-solid closed form
plus the composition's own measured delta.
