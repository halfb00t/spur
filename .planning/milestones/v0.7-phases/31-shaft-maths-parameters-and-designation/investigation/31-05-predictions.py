"""Print our DIN 5480 predictions for the human to compare with the copy (31-05).

One line per designation: x, xm, d, d_a, d_f at h_fP 0.55 and 0.60, s, the internal d_Ff at
both h_fP, the theoretical pin and its rounded value, M_Re at the rounded pin with its contact
diameter, then the ShaftDimensions the API would serve as one JSON object. Only the public
functions Phase 33 serves are used: parse_designation, ShaftParams, derive_shaft and
din5480's raw functions. Every number is an ASSUMPTION until the checkpoint confirms its
clause; 31-06 re-runs this on the human's own rows.

    .venv/bin/python 31-05-predictions.py                  # the five shafts of this plan
    .venv/bin/python 31-05-predictions.py "W 30x2x14x8f"   # any designation
"""

from __future__ import annotations

import sys

from spur import din5480
from spur.shaft_calc import PIN_DECIMALS, derive_shaft
from spur.shaft_params import ShaftParams

DEFAULT_DESIGNATIONS = (
    "W 25x1.25x18x8f",
    "W 25x1.25x19x8f",
    "W 30x2x14x8f",
    "W 70x3x22x6f",
    "W 120x3x38x8f",
)
H_FPS = (0.55, 0.60)


def predict(text: str) -> str:
    des = din5480.parse_designation(text)
    p = ShaftParams(reference_d=des.reference_d, module=des.module, teeth=des.teeth,
                    fit=des.fit)
    m, z = p.module, p.teeth
    x = din5480.profile_shift(p.reference_d, m, z)
    xm = x * m
    s = din5480.tooth_thickness(m, xm)
    theoretical = din5480.theoretical_pin_diameter(m, z, xm)
    pin = round(theoretical, PIN_DECIMALS)
    reading = din5480.measure_over_pins(m, z, s, pin)
    if reading is None:
        measured = "M_Re=none contact=none"
    else:
        measured = f"M_Re={reading[0]:.4f} contact={reading[1]:.4f}"
        if z % 2:
            measured += " (odd z, not printed)"
    root = " ".join(f"d_f@{h:.2f}={din5480.root_diameter(m, z, xm, h):.3f}" for h in H_FPS)
    form = " ".join(
        f"d_Ff@{h:.2f}={din5480.form_diameter(m, z, xm, h, din5480.RHO_FP):.3f}"
        for h in H_FPS)
    dims = derive_shaft(p)
    return (f"{dims.designation} x={x!r} xm={xm:.4f} d={m * z:.3f} "
            f"d_a={din5480.tip_diameter(p.reference_d, m):.3f} {root} s={s:.4f} {form} "
            f"D_theoretical={theoretical:.5f} D_rounded={pin:.{PIN_DECIMALS}f} {measured} "
            f"json={dims.model_dump_json()}")


def main(argv: list[str]) -> int:
    designations = argv or list(DEFAULT_DESIGNATIONS)
    print("designation, then labelled predictions (ASSUMPTION until the copy confirms)")
    for text in designations:
        print(predict(text))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
