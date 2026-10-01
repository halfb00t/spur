"""The family and refusal tables shared by `tests/test_calc.py` (12-05, this phase's
calc-level composition matrix, D-07/D-08) and `tests/test_cli.py` (12-07's API/CLI
routing rows, `12-05-PLAN.md` `key_links`).

Not collected: no `test_` prefix (`tests/regression/corpus.py`'s precedent for a shared,
non-collected data module under `tests/`). Every table here is written out by hand from
the planning probe -- never computed by calling `spur.calc`'s own functions (the code
under test) to build its own expectation, because a tautological test is a plausible
wrong number (L08, CLAUDE.md).
"""

from __future__ import annotations

# --- Tier 1: the 96-row bore x cutout x recess x tip-chamfer cross product (D-07) -----
# Each dict is `{**bore, **cutout, **recess, **tip}` through `GearParams.model_validate`.
# All four tables key by the id used in the parametrized test's row id
# ("{bore}-{cutout}-{recess}-{tip}").

BORES: dict[str, dict[str, object]] = {
    "round": {"bore_flat": 0},   # bore_d stays the 9 mm default; no D-flat, no keyway
    "d-flat": {},                # bore_d 9, bore_flat 8 -- both defaults, a D-flat bore
    "keyed": {"bore_flat": 0, "keyway_width": 3, "keyway_depth": 1.4},
    "hex": {"bore_hex": 6},
}
CUTOUTS: dict[str, dict[str, object]] = {
    "none": {},
    # hub_d 13.2 clears the keyed bore's 6.179 mm floor-corner datum
    # (keyway_corner_radius on the default 9 mm bore with a 3 x 1.4 mm keyway) with
    # margin, so the keyed-spokes row builds a valid part instead of refusing (D-07
    # tier 1's keyed-spokes adjacency row).
    "spokes": {"spoke_count": 4, "spoke_width": 2, "hub_d": 13.2, "rim_wall": 1,
               "spoke_fillet": 1},
    "holes": {"hole_count": 6, "hole_d": 4, "hole_circle_d": 20},
    "cells": {"hex_cell": 3, "hex_wall": 1},
}
RECESSES: dict[str, dict[str, object]] = {
    "both": {},
    "top": {"recess_sides": "top"},
    "none": {"recess_sides": "none"},
}
TIPS: dict[str, dict[str, object]] = {
    "off": {},
    "on": {"tip_chamfer": 1.75},   # the default 19-tooth gear's pitch-circle cap, no warning
}

# The `DerivedDimensions` fields that are non-null on every tier-1 row, regardless of
# family (measured this session, `12-05-PLAN.md <interfaces>`).
ALWAYS: frozenset[str] = frozenset({
    "pitch_d", "tip_d", "root_d", "base_d", "caliper_over_tips", "tip_thickness",
    "root_thickness", "root_gap", "root_fillet", "span_teeth", "span",
})

# Non-null fields each bore family adds on top of ALWAYS.
BORE_FIELDS: dict[str, frozenset[str]] = {
    "round": frozenset({"bore_effective"}),
    "d-flat": frozenset({"bore_effective"}),
    "keyed": frozenset({"bore_effective", "keyway_floor_to_wall", "keyway_width_effective"}),
    "hex": frozenset({"hex_across_flats", "hex_across_corners"}),
}

# Non-null fields each cutout family adds on top of ALWAYS | BORE_FIELDS[...].
CUTOUT_FIELDS: dict[str, frozenset[str]] = {
    "none": frozenset(),
    "spokes": frozenset({"cutout_hub_wall", "cutout_rim_wall", "spoke_fillet_effective"}),
    "holes": frozenset({"cutout_hub_wall", "cutout_rim_wall"}),
    "cells": frozenset({"cutout_hub_wall", "cutout_rim_wall", "hex_cell_effective",
                        "hex_cell_count"}),
}

# Non-null fields each recess setting adds on top of ALWAYS | BORE_FIELDS[...].
RECESS_FIELDS: dict[str, frozenset[str]] = {
    "both": frozenset({"recess_id", "recess_od", "recess_fillet", "web"}),
    "top": frozenset({"recess_id", "recess_od", "recess_fillet", "web"}),
    "none": frozenset(),
}

# Non-null fields the tip chamfer adds on top of ALWAYS | BORE_FIELDS[...].
TIP_FIELDS: dict[str, frozenset[str]] = {
    "off": frozenset(),
    "on": frozenset({"tip_chamfer_effective"}),
}

# The exact hex-replaces-round warning sentence at the default 9 mm bore_d / 8 mm
# bore_flat (both nonzero, so both are named -- src/spur/calc.py's `p.bore_hex > 0`
# branch, the module's own docstring naming which function it is in).
HEX_IGNORES_ROUND = ("Hex bore replaces the round profile: bore_d (9 mm) and "
                     "bore_flat (8 mm) are ignored.")

# --- Every locked refusal x every other family switched on, at the calc level (D-08) --
# The 9 bore refusals and 14 cutout refusals below are each an "alone" set that check()
# already refuses on its own (the un-composed values `tests/test_calc.py`'s own
# refusal tests already pin); `tests/test_calc.py`'s composition test merges each with
# every id in `BORE_REFUSAL_FAMILIES`/`CUTOUT_REFUSAL_FAMILIES` as
# `{**family, **refusal}`, so the refusal's own values always win.

# test_calc.py's own SPOKE dict (spoke_count 4, spoke_width 2, hub_d 12, rim_wall 1) --
# the spoke refusal rows are all one field past this base.
SPOKE_BASE: dict[str, object] = {"spoke_count": 4, "spoke_width": 2, "hub_d": 12,
                                 "rim_wall": 1}

BORE_REFUSALS: dict[str, dict[str, object]] = {
    "hex-keyway": {"bore_hex": 6, "keyway_width": 3, "keyway_depth": 1.4},
    "keyway-no-bore": {"bore_d": 0, "keyway_width": 3, "keyway_depth": 1.4},
    "keyway-half-set": {"keyway_width": 3},
    "keyway-too-deep": {"keyway_width": 3, "keyway_depth": 9.4},
    "keyway-into-flat": {"keyway_width": 6.5, "keyway_depth": 1.4},
    "keyway-too-wide": {"bore_flat": 0, "keyway_width": 9, "keyway_depth": 1.4},
    "hex-corner": {"bore_hex": 24.2, "bore_chamfer": 0},
    "hex-mouth": {"bore_hex": 23.4},
    "round-chamfer-reach": {"bore_d": 24.75, "bore_chamfer": 2, "bore_flat": 0},
}
CUTOUT_REFUSALS: dict[str, dict[str, object]] = {
    "two-patterns": {**SPOKE_BASE, "hole_count": 6, "hole_d": 4, "hole_circle_d": 20},
    "half-set-spokes": {"spoke_count": 4},
    "half-set-holes": {"hole_count": 6},
    "half-set-cells": {"hex_cell": 3},
    "hole-hub": {"hole_count": 6, "hole_d": 4, "hole_circle_d": 14.7},
    "hole-rim": {"hole_count": 6, "hole_d": 4, "hole_circle_d": 24.1},
    "hole-neighbour": {"teeth": 40, "hole_count": 6, "hole_d": 19.65, "hole_circle_d": 40},
    "spoke-arm": {**SPOKE_BASE, "spoke_width": 0.35},
    "spoke-rim": {**SPOKE_BASE, "rim_wall": 0.35},
    "spoke-hub": {**SPOKE_BASE, "hub_d": 10.7},
    "spoke-annulus": {**SPOKE_BASE, "rim_wall": 8.05},
    "spoke-opening": {"spoke_count": 12, "spoke_width": 2.72, "hub_d": 12, "rim_wall": 0.4},
    "cell-wall": {"hex_cell": 3, "hex_wall": 0.35},
    "cell-no-fit": {"hex_cell": 5.1, "hex_wall": 1},
}

# A cutout refusal's own "switched-on hex" family uses 8 mm, not the tier-1 table's 6 mm
# (`BORES["hex"]`): a 6 mm hex's chamfered mouth (4.01 mm) sits inside the default
# D-flat's (4.975 mm), so a hub refusal composed with hex 6 would stop refusing and that
# row would prove nothing. An 8 mm hex's mouth is 5.167 mm, wider than the default round
# bore's, so every hub/rim refusal still refuses with a hex bore switched on.
REFUSAL_HEX: dict[str, object] = {"bore_hex": 8}

# Switched on beside each bore refusal (D-08: "every other family"): the three cutout
# patterns' tier-1 dicts, both non-default recess settings, and the tip chamfer.
BORE_REFUSAL_FAMILIES: dict[str, dict[str, object]] = {
    "spokes": CUTOUTS["spokes"],
    "holes": CUTOUTS["holes"],
    "cells": CUTOUTS["cells"],
    "recess-top": RECESSES["top"],
    "recess-none": RECESSES["none"],
    "tip": TIPS["on"],
}
# Switched on beside each cutout refusal: the three other bore shapes (hex at
# REFUSAL_HEX, not the tier-1 6 mm), both non-default recess settings, and the tip
# chamfer.
CUTOUT_REFUSAL_FAMILIES: dict[str, dict[str, object]] = {
    "round": BORES["round"],
    "keyed": BORES["keyed"],
    "hex": REFUSAL_HEX,
    "recess-top": RECESSES["top"],
    "recess-none": RECESSES["none"],
    "tip": TIPS["on"],
}
