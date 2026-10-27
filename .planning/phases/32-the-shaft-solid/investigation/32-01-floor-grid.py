"""The float evidence for the applied end chamfer's floor rule (Phase 32, plan 32-01).

The human picks the applied chamfer's rounding rule at 32-01's checkpoint, and the research
did not run its assumption A2 (32-RESEARCH). This prints five labelled lines, one per
measurement, so the pick rests on counts and not on a prediction:

1. every three-place decimal from 0.000 to 500.000 floored by `floor(v*1000 + 1e-9)/1000`:
   how many do not come back as themselves;
2. the same without the `+ 1e-9`: how many, and the first three;
3. every four-place decimal from 0.0000 to 500.0000: how many floor above their input, and
   the largest excess;
4. the shaft grid (module, teeth, shift): the feasible rows, how many floor the tooth-height
   cap away from the module, and how many lattice chamfers at the cap or one or two steps
   below it put the cone start within 1e-9..1e-4 mm of the root circle (the band where the
   kernel hung at +-3e-7, 32-nearcap.log);
5. two splined lengths where the half-even `round(v, 3)` lands above the length (the empty
   shape of 32-round-up.log), beside the floored value.

A different count from the one the plan quotes is reported as measured, never adjusted.
"""

from __future__ import annotations

import math

from spur.din5480 import (
    H_FP,
    X_EPS,
    X_MAX,
    X_MIN,
    profile_shift,
    root_diameter,
    tip_diameter,
)

GUARD = 1e-9  # the epsilon of the rule under test
MODULES = (0.5, 0.6, 0.75, 0.8, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0)
BAND_LOW, BAND_HIGH = 1e-9, 1e-4  # mm, the offsets from the root circle that must not occur


def floor_guarded(v: float) -> float:
    """The rule under test: floor to 0.001 with a 1e-9 guard."""
    return math.floor(v * 1000 + GUARD) / 1000


def floor_exact(v: float) -> float:
    """The same without the guard."""
    return math.floor(v * 1000) / 1000


def three_places() -> tuple[int, int, list[str]]:
    """Mismatches with and without the guard over 0.000..500.000, and the first unguarded three."""
    guarded = unguarded = 0
    first: list[str] = []
    for i in range(500_001):
        s = f"{i // 1000}.{i % 1000:03d}"
        v = float(s)
        if floor_guarded(v) != v:
            guarded += 1
        if floor_exact(v) != v:
            unguarded += 1
            if len(first) < 3:
                first.append(s)
    return guarded, unguarded, first


def four_places() -> tuple[int, float]:
    """How many of 0.0000..500.0000 floor above themselves, and the largest excess."""
    above, worst = 0, 0.0
    for i in range(5_000_001):
        v = float(f"{i // 10000}.{i % 10000:04d}")
        f = floor_guarded(v)
        if f > v:
            above += 1
            worst = max(worst, f - v)
    return above, worst


def shaft_grid() -> tuple[int, int, int]:
    """Feasible rows, rows whose floored tooth height is not the module, and band hits."""
    rows = off_module = band_hits = 0
    for m in MODULES:
        for z in range(6, 83):
            for j in range(11):
                x = round(-0.05 + 0.05 * j, 2)
                reference_d = round(m * z + 2 * x * m + 1.1 * m, 2)
                shift = profile_shift(reference_d, m, z)
                if not X_MIN - X_EPS <= shift <= X_MAX + X_EPS:
                    continue
                rows += 1
                tip = round(tip_diameter(reference_d, m), 3)
                root = round(root_diameter(m, z, shift * m, H_FP), 3)
                cap = floor_guarded((tip - root) / 2)
                if cap != m:
                    off_module += 1
                steps = round(cap * 1000)
                for k in range(3):
                    c = (steps - k) / 1000
                    if BAND_LOW < abs(tip / 2 - c - root / 2) < BAND_HIGH:
                        band_hits += 1
    return rows, off_module, band_hits


def main() -> int:
    guarded, unguarded, first = three_places()
    print(f"(1) three-place decimals 0.000..500.000 (500001), mismatches with +1e-9: {guarded}")
    probe = 0.29  # the plan expected 0.29 * 1000 = 289.99999999999994 (not so, see the line)
    print(
        f"(2) the same without +1e-9, mismatches: {unguarded}, first three: {first}; "
        f"probe 0.29: 0.29 * 1000 = {probe * 1000!r}, floors to {floor_exact(probe)}"
    )
    above, worst = four_places()
    print(
        "(3) four-place decimals 0.0000..500.0000 (5000001) flooring above input: "
        f"{above}, largest excess: {worst:g}"
    )
    rows, off_module, band_hits = shaft_grid()
    print(
        f"(4) shaft grid, feasible rows: {rows}, floored tooth height != module: {off_module}, "
        f"lattice chamfers (cap, cap-0.001, cap-0.002) in the 1e-9..1e-4 band: {band_hits}"
    )
    lengths = "; ".join(
        f"length {ls}: round(v, 3) = {round(ls, 3)}, floored = {floor_guarded(ls)}"
        for ls in (2.0006, 5.0007)
    )
    print(f"(5) splined lengths, half-even round against floor: {lengths}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
