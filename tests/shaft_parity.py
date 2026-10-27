"""The one fixed set of shafts, and the readers every part of D-21 uses (REQ-shaft-parity).

D-21 has two parts and they share this set so that the web, the API and the CLI are read over
the same shafts. 33-05's tests/test_shaft_parity.py is part two; 33-08's browser step imports
`SHAFTS`, `displayed` and `web_rows` for part one.

The rule each comparison uses (the planner's choice, CONTEXT "Claude's Discretion"):

- API against CLI: raw-equal as parsed JSON, and in `ShaftDimensions` key order. No tolerance
  anywhere: both interfaces print the one `ShaftDimensions` through the same serialiser, so
  a difference of one ulp is a real difference, and `differences()` says so.
- The download name: the API's `Content-Disposition` filename against `ShaftParams.slug()`
  plus the suffix, as ASCII strings, byte for byte (D-17).
- Web against API: at the displayed text only, a row's `label` and the text `fmt()` in
  app.js would print (`web_rows`), because the page rounds to three decimals.

Why each shaft is in the set (numbers measured at planning with `derive_shaft`):

- `default`: the empty link, W 25x1.25x18x8f; profile shift 0.45, the upper edge of the
  range; slug `spur_shaft_w25x1.25x18`; `measure_over_pins` 27.999.
- `w30x2x14`: profile shift -0.05, the lower edge; `measure_over_pins` 33.685.
- `odd-z`: W 26x1.25x19, an odd tooth count, where no measurement over pins exists:
  `measure_over_pins` is null (L08), shift 0.35.
- `no-shank-no-chamfer`: `shank_length` 0, the field's minimum, and `end_chamfer` 0, so
  `end_chamfer_effective` is null; its slug equals the default's, which is the adjacency
  the name test pins (the solid's fields are not in the name).

`form_d` is null for every shaft: no shaft in the set has a form diameter to print.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from decimal import ROUND_HALF_UP, Decimal

SHAFTS: dict[str, dict[str, float | int | str]] = {
    "default": {},
    "w30x2x14": {"reference_d": 30, "module": 2, "teeth": 14},
    "odd-z": {"reference_d": 26, "module": 1.25, "teeth": 19},
    "no-shank-no-chamfer": {"shank_length": 0, "end_chamfer": 0},
}


def cli_argv(values: Mapping[str, float | int | str]) -> list[str]:
    """`spur shaft info` arguments for `values`, a field name becoming its flag."""
    argv = ["shaft", "info"]
    for name, value in values.items():
        argv += ["--" + name.replace("_", "-"), str(value)]
    return argv


def displayed(v: float) -> str:
    """The text app.js `fmt()` prints for `v`: `Number(v).toFixed(3).replace(/\\.?0+$/, '')`.

    JavaScript's `toFixed` rounds the exact binary value half away from zero, so the port
    quantizes `Decimal(abs(v))` (exact, not the shortest repr) half up and puts the sign
    back only for a negative number: `-0.0001` reads `-0` in the browser and `-0.0` reads
    `0`. 33-08 checks this port against the browser itself.
    """
    text = str(Decimal(abs(v)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))
    if v < 0:
        text = "-" + text
    return re.sub(r"\.?0+$", "", text, count=1)


def differences(left: Mapping[str, object], right: Mapping[str, object]) -> list[str]:
    """One line per key whose value differs, or whose position differs. Never a tolerance."""
    missing = object()
    lines = [f"{key}: {left.get(key, missing)!r} != {right.get(key, missing)!r}"
             for key in dict.fromkeys([*left, *right])
             if left.get(key, missing) != right.get(key, missing)]
    if not lines:
        lines = [f"position {i}: {a!r} != {b!r}"
                 for i, (a, b) in enumerate(zip(left, right, strict=True)) if a != b]
    return lines


def web_rows(doc: Mapping[str, object], dims: Sequence[Mapping[str, str]]) -> list[tuple[str, str]]:
    """The `(label, text)` rows the page prints for `doc`, in `dims` order (33-06's rule).

    A null value is not printed. A number reads `displayed(v)` and, when the row has a unit,
    a space and the unit; a string reads as itself.
    """
    rows: list[tuple[str, str]] = []
    for row in dims:
        value = doc[row["key"]]
        if value is None:
            continue
        if isinstance(value, str):
            rows.append((row["label"], value))
        elif isinstance(value, (int, float)):
            unit = f" {row['unit']}" if row["unit"] else ""
            rows.append((row["label"], displayed(value) + unit))
        else:
            raise TypeError(f"{row['key']}: a {type(value).__name__} is not a printable row")
    return rows
