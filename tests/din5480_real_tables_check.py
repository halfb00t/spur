"""The real DIN 5480 table file held to what the human approved and accepted (34-16).

Run only by `make tables.test FILE=<the table file>`. The file is the human's, private and
git-ignored, so it is never in CI. This module is deliberately not named `test_*.py`: pytest
does not collect it, so `make verify` neither runs nor skips it. A skip would read in the
gate's result line as unfinished work, and no test in this suite skips today.

It reads `SPUR_DIN5480_TABLES` at import (tests/conftest.py unsets it before every test) and
fails, never skips, when it is unset. It holds no value of the standard: the approved anchors
come from tests/test_din5480_anchors.py and everything else is read from the file it is given.
What it holds are keys (module, d_B, z) of the findings the human accepted at the 34-15
checkpoint, 2026-10-31, and counts and tolerances the repository already names.

How the exact digits are held. Every comparison to an approved anchor is `==`, never an
approximation: Table 7 cells are whole micrometres compared as integers, Part 2's d_Ff1, D_M
and M1 are decimals parsed from the file and compared to the literal the anchors file prints,
and the three limit thicknesses are compared rounded to the third decimal. A cell changed by
one in its last digit fails the test of that cell.
"""

from __future__ import annotations

import functools
import math
import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic import ValidationError
from test_din5480_anchors import (
    PAGE_EXAMPLE_M1_MIN,
    PART_2_CONTACT,
    PART_2_ROWS,
    ROW,
    TABLE_7_ANCHORS,
    TABLE_7_THICKNESS,
)

from scripts.din5480_tables_tool import shortfalls
from spur import din5480, din5480_tables
from spur.din5480 import parse_designation
from spur.din5480_tables import M1_TOLERANCE, FitTolerance, Tables, part_2_provenance
from spur.shaft_calc import GUARD_MARGIN_FACTOR, derive_shaft, pin_contact_window
from spur.shaft_params import ShaftParams

PATH = os.environ.get(din5480_tables.ENV_VAR)

Key = tuple[float, float, int]

# 34-15 checkpoint, 2026-10-31, the human's replies: F1 accepted, F2 accepted. Each set holds the
# keys of the findings accepted as printed, and nothing else may be in the sweep's result.
#
# F1: the 11 sizes the shaft's shift range refuses (a 422 "infeasible model" for every fit),
# kept under docs/tech_debt/active/2026-10-26-shaft-shift-range-narrower-than-din-5480-
# exceptions.md. (module, d_B, z).
ACCEPTED_REFUSED: frozenset[Key] = frozenset({
    (0.6, 40.0, 64), (0.6, 47.0, 76), (0.75, 47.0, 60), (0.75, 50.0, 64), (0.8, 50.0, 60),
    (0.8, 55.0, 66), (0.8, 58.0, 70), (1.25, 78.0, 60), (1.5, 100.0, 64), (1.75, 110.0, 60),
    (1.75, 120.0, 66),
})
# The sizes whose M_Re (nominal, maximum or minimum) is null at the pin-contact guard for some
# fit the tool can build. The sweep found none; the human accepted that count (F2).
ACCEPTED_GUARD: frozenset[Key] = frozenset()
# The size x letter combinations whose tip land or tooth space closes at the maximum-material
# thickness. The sweep found none.
ACCEPTED_TOOTH: frozenset[tuple[Key, str]] = frozenset()


@functools.cache
def _load(path: str) -> Tables:
    return din5480_tables.load_file(Path(path))


@pytest.fixture
def real() -> Iterator[Tables]:
    """The human's file, installed for one test and forgotten after it."""
    if not PATH:
        pytest.fail("set FILE: make tables.test FILE=<the table file>")
    tables = _load(PATH)
    din5480_tables.install(tables)
    yield tables
    din5480_tables.reset()


def _shaft(key: Key, fit: str = "8f") -> ShaftParams:
    module, reference_d, teeth = key
    return ShaftParams(reference_d=reference_d, module=module, teeth=teeth, fit=fit,
                       shank_length=0)


def _guard_sweep(tables: Tables) -> tuple[set[Key], set[Key]]:
    """(sizes ShaftParams refuses, sizes with an M_Re null for some fit it accepts)."""
    fits = [f"{c}{letter}" for c in tables.tolerance_classes for letter in tables.letters]
    refused: set[Key] = set()
    null: set[Key] = set()
    for row in tables.sizes:
        for fit in fits:
            try:
                p = _shaft(row.key, fit)
            except ValidationError:
                refused.add(row.key)
                continue
            d = derive_shaft(p)
            if None in (d.measure_over_pins, d.measure_over_pins_max, d.measure_over_pins_min):
                null.add(row.key)
    return refused, null


# --- the approved anchors, exactly -------------------------------------------------------


@pytest.mark.parametrize("name", TABLE_7_ANCHORS)
def test_the_file_holds_the_approved_table_7_cells(real: Tables, name: str) -> None:
    """DIN 5480-1:2006, Table 7: column, A_s, T_G, T_act and T_eff, whole micrometres."""
    d = parse_designation(name)
    column, a_s, t_g, t_act, t_eff = TABLE_7_ANCHORS[name]
    assert real.column_for(d.module, d.reference_d) == column
    assert real.fit(d.module, d.reference_d, d.fit) == FitTolerance(a_s, t_g, t_act, t_eff)


@pytest.mark.parametrize("name", TABLE_7_ANCHORS)
def test_the_files_cells_give_the_approved_limit_thicknesses(real: Tables, name: str) -> None:
    d = parse_designation(name)
    tol = real.fit(d.module, d.reference_d, d.fit)
    assert tol is not None
    xm = din5480.profile_shift(d.reference_d, d.module, d.teeth) * d.module
    s1 = din5480.tooth_thickness(d.module, xm)
    limits = din5480.thickness_limits(s1, tol.a_s_um, tol.t_g_um, tol.t_eff_um)
    assert tuple(round(v, 3) for v in limits) == TABLE_7_THICKNESS[name]


@pytest.mark.parametrize("name", PART_2_CONTACT)
def test_the_file_holds_the_approved_form_diameter_and_pin(real: Tables, name: str) -> None:
    """DIN 5480-2: d_Ff1 maximum and the gauge pin D_M, and the clause, tables and pages."""
    d = parse_designation(name)
    d_ff1, pin, clause, tables, pages = PART_2_CONTACT[name]
    row = real.size(d.module, d.reference_d, d.teeth)
    assert row is not None
    assert row.form_d_max_mm == d_ff1
    assert row.pin_d_mm == pin
    assert (row.provenance.clause, row.provenance.table, row.provenance.pages) == (
        clause, tables, pages)
    assert row.provenance == part_2_provenance(d.module)


@pytest.mark.parametrize("row", PART_2_ROWS, ids=[r[0] for r in PART_2_ROWS])
def test_the_file_holds_the_approved_part_2_rows(
        real: Tables, row: tuple[str, str, float, int, float, float, float, float, float],
) -> None:
    """DIN 5480-2: the tabulated pin D_M and M1 of each approved row, as printed."""
    name, _, _, _, _, _, _, pin, m1 = row
    d = parse_designation(name)
    size = real.size(d.module, d.reference_d, d.teeth)
    assert size is not None
    assert size.pin_d_mm == pin
    assert size.m1_mm == m1


def test_the_page_example_prints_its_three_thicknesses_and_m_re_min(real: Tables) -> None:
    """DIN 5480-1:2006-03, cl. 9.1, Fig. 6 (CONTEXT D-05), through `derive_shaft`."""
    d = parse_designation(ROW)
    shaft = derive_shaft(ShaftParams(reference_d=d.reference_d, module=d.module,
                                     teeth=d.teeth, fit=d.fit))
    assert (shaft.max_effective_thickness, shaft.max_actual_thickness,
            shaft.min_actual_thickness) == TABLE_7_THICKNESS[ROW]
    assert shaft.measure_over_pins_min == PAGE_EXAMPLE_M1_MIN


# --- the file is complete and agrees with itself -----------------------------------------


def test_the_file_is_complete(real: Tables) -> None:
    assert shortfalls(real) == []


def test_every_size_agrees_with_its_m1_at_the_tabulated_pin(real: Tables) -> None:
    """The computed M at the tabulated pin and the nominal thickness against the printed M1."""
    off: list[Key] = []
    for row in real.sizes:
        x = din5480.profile_shift(row.reference_d, row.module, row.teeth)
        reading = din5480.measure_over_pins(
            row.module, row.teeth, din5480.tooth_thickness(row.module, x * row.module),
            row.pin_d_mm)
        if reading is None or abs(reading[0] - row.m1_mm) > M1_TOLERANCE:
            off.append(row.key)
    assert off == []


def test_the_guard_form_term_is_each_rows_d_ff1_maximum(real: Tables) -> None:
    off: list[Key] = []
    for row in real.sizes:
        p = ShaftParams.model_construct(reference_d=row.reference_d, module=row.module,
                                        teeth=row.teeth, fit="8f", shank_length=0,
                                        splined_length=30.0, end_chamfer=1.0, shank_d=25.0)
        low, _ = pin_contact_window(p, row.form_d_max_mm)
        if low - GUARD_MARGIN_FACTOR * row.module != pytest.approx(row.form_d_max_mm):
            off.append(row.key)
    assert off == []


def test_the_tabulated_pin_touches_inside_the_window_at_every_thickness(real: Tables) -> None:
    """Every size x fit x (nominal, s_max, s_min), straight against `pin_contact_window`."""
    fits = [f"{c}{letter}" for c in real.tolerance_classes for letter in real.letters]
    off: set[Key] = set()
    for row in real.sizes:
        p = ShaftParams.model_construct(reference_d=row.reference_d, module=row.module,
                                        teeth=row.teeth, fit="8f", shank_length=0,
                                        splined_length=30.0, end_chamfer=1.0, shank_d=25.0)
        xm = din5480.profile_shift(row.reference_d, row.module, row.teeth) * row.module
        s1 = din5480.tooth_thickness(row.module, xm)
        low, high = pin_contact_window(p, row.form_d_max_mm)
        for fit in fits:
            tol = real.fit(row.module, row.reference_d, fit)
            assert tol is not None
            _, s_max, s_min = din5480.thickness_limits(s1, tol.a_s_um, tol.t_g_um, tol.t_eff_um)
            for s in (s1, s_max, s_min):
                reading = din5480.measure_over_pins(row.module, row.teeth, s, row.pin_d_mm)
                if reading is None or not low <= reading[1] <= high:
                    off.add(row.key)
    assert off == set()


# --- the sweeps the human accepted at 34-15 ----------------------------------------------


def test_the_guard_sweep_finds_the_accepted_findings_and_no_other(real: Tables) -> None:
    refused, null = _guard_sweep(real)
    assert refused == ACCEPTED_REFUSED
    assert null == ACCEPTED_GUARD


def test_the_tip_land_and_overlap_sweep_finds_the_accepted_findings_and_no_other(
        real: Tables) -> None:
    """At the printed maximum-material thickness written as `build_shaft` writes it: the tip
    land stays open (half angle at the tip radius > 0) and the space stays open (half angle at
    the root radius < pi/z). One class stands for all: A_s depends on the letter and the
    column only."""
    tolerance_class = real.tolerance_classes[0]
    failed: set[tuple[Key, str]] = set()
    for row in real.sizes:
        m, z, d_b = row.module, row.teeth, row.reference_d
        xm = din5480.profile_shift(d_b, m, z) * m
        s1 = din5480.tooth_thickness(m, xm)
        tip_d = round(din5480.tip_diameter(d_b, m), 3)
        root_d = round(din5480.root_diameter(m, z, xm, din5480.H_FP), 3)
        for letter in real.letters:
            tol = real.fit(m, d_b, f"{tolerance_class}{letter}")
            assert tol is not None, (row.key, letter)
            s_vmax = round(s1 + tol.a_s_um / 1000, 3)
            xm_flank = (s_vmax - math.pi * m / 2) / (2 * math.tan(din5480.ALPHA))
            if (din5480.flank_half_angle(m, z, xm_flank, tip_d / 2) <= 0
                    or din5480.flank_half_angle(m, z, xm_flank, root_d / 2) >= math.pi / z):
                failed.add((row.key, letter))
    assert failed == ACCEPTED_TOOTH


# --- the range edges: "über x bis y" is x < d_B <= y, confirmed at 34-15 -----------------


def test_every_printed_range_edge_reads_as_the_range_it_closes(real: Tables) -> None:
    """For each column row and each module of its group: d_B on the upper bound y is this
    row's column and one float step above is the next range's (None when none starts at y);
    d_B on a lower bound x is the previous range's column (None when none ends at x) and one
    step above is this row's."""
    off: list[tuple[float, float, float]] = []
    for c in real.columns:
        modules = sorted({s.module for s in real.sizes
                          if c.module_min_mm <= s.module <= c.module_max_mm})
        group = [n for n in real.columns
                 if (n.module_min_mm, n.module_max_mm) == (c.module_min_mm, c.module_max_mm)]
        for m in modules:
            if c.d_b_upto_mm is not None:
                y = c.d_b_upto_mm
                above = [n.column for n in group if n.d_b_over_mm == y]
                if (real.column_for(m, y) != c.column
                        or real.column_for(m, math.nextafter(y, math.inf))
                        != (above[0] if above else None)):
                    off.append((c.module_min_mm, m, y))
            if c.d_b_over_mm is not None:
                x = c.d_b_over_mm
                below = [n.column for n in group if n.d_b_upto_mm == x]
                if (real.column_for(m, x) != (below[0] if below else None)
                        or real.column_for(m, math.nextafter(x, math.inf)) != c.column):
                    off.append((c.module_min_mm, m, x))
    assert off == []


def test_a_tabulated_size_on_an_edge_is_not_off_table_and_one_float_step_off_is(
        real: Tables) -> None:
    """The size key is the exact float (34-02): the tabulated d_B has its row and a column,
    and the next float above has no row."""
    off: list[Key] = []
    for row in real.sizes:
        m, d_b, z = row.key
        if (real.size(m, d_b, z) is None or real.column_for(m, d_b) is None
                or real.size(m, math.nextafter(d_b, math.inf), z) is not None
                or real.size(m, math.nextafter(d_b, -math.inf), z) is not None):
            off.append(row.key)
    assert off == []
