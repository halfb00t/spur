# The shaft's volume guard accepts a chamfer that was never cut

Severity: must
Status: resolved
Resolved in: fix(shaft): refuse a chamfer the kernel never cut (end-face read-back) (gsd/phase-33-interfaces-and-parity)
Date: 2026-10-27
Source: Phase 32 code review, 32-REVIEW.md WR-01 (confirmed by the phase verifier, 32-VERIFICATION.md)
Related files:
- src/spur/shaft_model.py:136-141 (`_guard_volume`)
- tests/test_shaft_model.py

## Context
`_guard_volume` brackets the built volume as `[upper - c*(area - pi*rf^2), upper]`, where `upper` is the
uncut prism plus shank. A solid with no chamfer at all sits exactly on the upper edge and passes. The
reviewer built `ShaftParams(end_chamfer=0)` and called `_guard_volume(solid, area, rf, 1.0, ...)`: it
returned without raising. The bounding-box check cannot see a missing chamfer either, because the cone
changes neither the z extent nor the widest radius.

## Why it matters
If the cone intersect ever returned the body unchanged (a kernel no-op, or a later edit to `_cone`),
`derive_shaft` would still print `end_chamfer_effective = c`: a number someone cuts metal to that is not on
the part (L08). The module docstring promises the guards turn each silent failure into a `BuildError`.
Today only the test-suite readbacks (`test_the_default_shaft_reads_back_its_applied_chamfer`, the STL
end-face test) catch it; nothing does at run time.

## Next step
For `c > 0`, refuse `cut = upper - volume <= 0` with a `BuildError` (the reviewer's minimum; a closed-form
lower bound is the stronger option), plus a test that hands `_guard_volume` an uncut solid with `c > 0`
and expects `BuildError`, seen red once. Revisit when Phase 33 starts (it exposes shaft downloads); fix
before that phase ships.

## Resolution
The next step's volume test (`upper - volume <= 0`) was replaced by an end-face read-back in `_guard_volume`: on the
heaviest shaft an honest 0.001 mm chamfer reads `upper - volume = -0.215 mm^3` (the face area's own error outweighs so
small a cut), so that test would refuse a good part, while the largest vertex radius of the one planar face at z = 0
matches `tip_d/2 - c` within 1.7e-13 mm on every probed row and an uncut face is off by the whole chamfer
(`bench/RESULTS.md` `### The applied chamfer, read off the end face (33-02)`). Held by
`test_a_chamfer_the_kernel_never_cut_is_refused`, seen red once (`DID NOT RAISE`).
