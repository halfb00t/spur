"""A synthetic DIN 5480 table document for the light tests; not collected.

Every number here is invented or computed by a formula, except the approved anchors, each
named with its source (D-01, D-07): the D_M and M1 of four DIN 5480-2:2006-05 rows (W 25x1.25x18,
W 26x1.25x19, W 30x2x14, W 30x2x13, pinned in tests/test_din5480_anchors.py) and, from
DIN 5480-1:2006-03 cl. 9.1, Fig. 6 (W 120x3x38x8f), the gauge pin 6.000 and d_Ff1 max 113.91.
Nothing was copied from the private file, so a diff of this file against it shows no
agreement beyond those anchors. The invented parts say so where they are made.
"""

from __future__ import annotations

from pathlib import Path

from spur import din5480
from spur.din5480_tables import (
    TABLE_7_PROVENANCE,
    ClassRow,
    ColumnRow,
    DeviationRow,
    SizeRow,
    Tables,
    ToleranceRow,
    canonical,
    parse,
    part_2_provenance,
)

# (module, reference_d, teeth, pin_d_mm, m1_mm): the four approved Part 2 rows.
_PART_2_ANCHORS = (
    (1.25, 25.0, 18, 2.75, 28.050),
    (1.25, 26.0, 19, 2.75, 29.026),
    (2.0, 30.0, 14, 4.0, 34.144),
    (2.0, 30.0, 13, 5.0, 35.984),
)


def _form_d_max(module: float, reference_d: float, teeth: int) -> float:
    """INVENTED by formula: the construction's form diameter less 0.05*m. Part 2's d_Ff1 max
    of these four rows is not approved, so no printed value stands here."""
    x = din5480.profile_shift(reference_d, module, teeth)
    internal = din5480.form_diameter(module, teeth, x * module, din5480.H_FP, din5480.RHO_FP)
    return round(internal - 0.05 * module, 2)


def _sizes() -> tuple[SizeRow, ...]:
    rows = [
        SizeRow(provenance=part_2_provenance(m), module=m, reference_d=d, teeth=z,
                pin_d_mm=pin, m1_mm=m1, form_d_max_mm=_form_d_max(m, d, z))
        for m, d, z, pin, m1 in _PART_2_ANCHORS
    ]
    # Part 1 Fig. 6: the gauge pin 6.000 and d_Ff1 max 113.91 are approved. The M1 is
    # COMPUTED at that pin and the nominal thickness, because Part 2's M1 for this row is not
    # approved.
    x = din5480.profile_shift(120.0, 3.0, 38)
    s = din5480.tooth_thickness(3.0, x * 3.0)
    reading = din5480.measure_over_pins(3.0, 38, s, 6.0)
    assert reading is not None
    rows.append(SizeRow(provenance=part_2_provenance(3.0), module=3.0, reference_d=120.0,
                        teeth=38, pin_d_mm=6.0, m1_mm=round(reading[0], 3),
                        form_d_max_mm=113.91))
    return tuple(rows)


def _table_7() -> tuple[
        tuple[DeviationRow, ...], tuple[ClassRow, ...],
        tuple[ToleranceRow, ...], tuple[ColumnRow, ...]]:
    """ALL INVENTED: three columns, three letters, three classes, five tolerance rows."""
    p = TABLE_7_PROVENANCE
    deviations = tuple(DeviationRow(provenance=p, letter=letter, a_s_um=a_s) for letter, a_s in (
        ("f", (-21, -17, -13)), ("h", (0, 0, 0)), ("k", (5, 7, 9))))
    classes = tuple(ClassRow(provenance=p, tolerance_class=c, row_by_column=rows) for c, rows in (
        (7, (1, 2, 3)), (8, (2, 3, 4)), (9, (3, 4, 5))))
    # Row 2 is the default shaft's (fit 8f). Its T_eff carries one extra micrometre so the
    # default shaft's s_max and M_Re max are not a pair a real table gives for that size.
    tolerances = tuple(ToleranceRow(provenance=p, row=r, t_g_um=(9 + 6 * r) + t_eff,
                                    t_act_um=9 + 6 * r, t_eff_um=t_eff)
                       for r in range(1, 6) for t_eff in (6 + 4 * r + (r == 2),))
    # The edges put the default shaft's d_B 25 exactly on an edge, as the real table does
    # (34-RESEARCH Pitfall 1).
    columns = tuple(ColumnRow(provenance=p, module_min_mm=lo, module_max_mm=hi,
                              d_b_over_mm=over, d_b_upto_mm=upto, column=c)
                    for lo, hi, over, upto, c in (
        (0.5, 1.5, None, 25.0, 1), (0.5, 1.5, 25.0, None, 2),
        (1.75, 4.0, None, 100.0, 2), (1.75, 4.0, 100.0, None, 3),
        (5.0, 10.0, None, None, 3)))
    return deviations, classes, tolerances, columns


def text() -> str:
    deviations, classes, tolerances, columns = _table_7()
    return canonical(Tables(schema_version=1, sizes=_sizes(), deviations=deviations,
                            classes=classes, tolerances=tolerances, columns=columns))


def build() -> Tables:
    return parse(text())


def write(path: Path) -> Path:
    path.write_text(text(), encoding="utf-8")
    return path
