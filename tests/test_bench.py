"""Pure tests for `bench.memory`'s capping predicate (CR-02 review) -- no Docker daemon
needed; `_is_capped` is a plain function over two byte counts. Also covers
`bench.build_time`'s sweep file and budget predicate (08-04): the Phase 8 hex-bore sweep
is D-11's exact cross product, and `Timing.inside` pins the budget boundary. Also pins
the Phase 9 keyway sweep (09-04): its own cross product, with the largest keyway each
rule allows sitting exactly one step from a refusal. Also pins the Phase 10 tip-chamfer
sweep (10-04): its own cross product, with each largest chamfer sitting exactly on its
limit. Also pins the Phase 11 body-cutout sweeps (11-06), re-run at Task 2's gate
decision (D-18's `le` lowered to 60 holes / 40 spokes): the hole and spoke cross
products, with only the module-1.75 large-hole row still on a refusal boundary (its
rim-wall bound is count-independent); the honeycomb cross product, raised to
`HEX_CELL_CAP` on every row. Also pins Phase 12's `stl_size()` helper and `report()`'s
two new fine-STL columns and `**Largest fine STL:**` line (12-02, D-16): a length
that disagrees with the header's triangle count is refused (never a plausible wrong
count, L08); an empty sweep is refused rather than printed as a passing table; and the
composed sweep itself (12-02, D-01), stacking each cutout's heaviest row with the tip
chamfer at its cap and both recesses on the heaviest bore its hub rule allows, at both
modules, beside the six single-feature baselines re-run unchanged. Also pins
`bench.export_cost`'s D-18 rule (12-04): `select_gzip_level` reproduces L19's own reading
on L19's own recorded table, is adopted or held exactly on both of L19's bars (>=10%
shrink, <=1.5x wall), and compares level 9 against whichever level is currently adopted,
not always against level 1. Also pins `maxrss_bytes`'s Darwin/Linux unit split (L24).

Run as `.venv/bin/python -m pytest tests/test_bench.py -q` **from the repo root** -- the
`-m` form is what puts the repo root on `sys.path`, which is what makes `import bench`
resolve at all: `bench` is not installed into the venv (it isn't listed in
`pyproject.toml`'s `[tool.hatch.build.targets.wheel] packages`), there is no
`tests/__init__.py` to do it another way, and `tests/conftest.py` (which exists for the
logger reset) puts `tests/` on `sys.path`, not the repo root, so it does not help either.
A bare `.venv/bin/pytest` would not find `bench` (hard_fact_4, 260924-bv5-PLAN.md).
"""

from __future__ import annotations

import itertools
import math
from pathlib import Path

import httpx
import pytest
from pydantic import ValidationError

from bench.build_time import DEFAULT_SWEEP, Timing, load_sweep, report, stl_size
from bench.export_cost import GzipRow, maxrss_bytes, select_gzip_level
from bench.latency import (
    _SCENARIOS,
    DEFAULT_SCENARIOS,
    RECORDED_BASELINE,
    _composed_rows,
    _fetch,
    _identical_rows,
    _report_markdown,
)
from bench.memory import _CAP_TOLERANCE_FRACTION, _SWEEP_MEM_LIMIT_BYTES, _is_capped
from bench.trochoid import (
    ORACLE_BAR_MM,
    _oracle,
    check_curve,
    premise_holds,
    rack,
    sweep_cases,
)
from bench.trochoid_part import CHAMFER_ROWS, chamfer_verdict
from spur.calc import (
    HEX_CELL_CAP,
    RootCurve,
    cutter,
    hex_cells,
    profile,
    root_mode,
    tip_chamfer_effective,
    tip_chamfer_limit,
    trochoid_root,
)
from spur.params import GearParams


def test_a_peak_equal_to_the_ceiling_is_capped() -> None:
    """A sampled peak that reads the ceiling exactly -- what the two capped rows on
    file (bench/RESULTS.md's first sweep attempt) actually read -- is capped."""
    assert _is_capped(_SWEEP_MEM_LIMIT_BYTES, _SWEEP_MEM_LIMIT_BYTES)


def test_a_peak_well_below_the_ceiling_is_not_capped() -> None:
    """The N=1 and N=2 peaks this sweep actually recorded (bench/RESULTS.md's Memory
    sweep: 2052.1 MiB, 2878.5 MiB) against the sweep's own ceiling -- the honest,
    uncapped cases this predicate must never call capped."""
    n1_peak_bytes = round(2052.1 * 1024**2)
    n2_peak_bytes = round(2878.5 * 1024**2)
    assert not _is_capped(n1_peak_bytes, _SWEEP_MEM_LIMIT_BYTES)
    assert not _is_capped(n2_peak_bytes, _SWEEP_MEM_LIMIT_BYTES)


def test_the_tolerance_boundary_is_pinned_from_both_sides() -> None:
    """A peak just inside `_CAP_TOLERANCE_FRACTION` of the ceiling is capped; a peak
    one byte below that is not -- pins the exact boundary, not just the extremes."""
    threshold = _SWEEP_MEM_LIMIT_BYTES * (1 - _CAP_TOLERANCE_FRACTION)
    just_inside = math.ceil(threshold)  # the smallest integer peak that satisfies
    # peak_bytes >= threshold -- one byte less would read as "well below" instead.
    just_outside = just_inside - 1
    assert _is_capped(just_inside, _SWEEP_MEM_LIMIT_BYTES)
    assert not _is_capped(just_outside, _SWEEP_MEM_LIMIT_BYTES)


def test_the_hex_bore_sweep_is_every_combination_d_11_names() -> None:
    """The committed Phase 8 sweep is D-11's full cross product -- 200 teeth,
    module {1.75, 10} (module drives fine-STL export time, planning probe: 0.64s to
    1.14s), bore_hex {200, 12.7}, recess_sides {both, none}, bore_chamfer {0.4, 3} (3 is
    the field's `le`; no hex rule binds at 200 teeth). Every row is therefore a buildable
    gear under 08-03's rules -- load_sweep would have raised otherwise."""
    sets = load_sweep(DEFAULT_SWEEP)
    assert len(sets) == 16
    got = {(p.teeth, p.module, p.bore_hex, p.recess_sides, p.bore_chamfer)
           for _, p in sets}
    want = set(itertools.product((200,), (1.75, 10.0), (200.0, 12.7),
                                  ("both", "none"), (0.4, 3.0)))
    assert got == want


def test_a_set_is_inside_the_timeout_until_its_build_plus_slower_export_passes_it() -> None:
    """`SPUR_BUILD_TIMEOUT` wraps one build plus one export -- the slower of the two
    exports, not both summed. Exactly the timeout is still inside it. The two trailing
    integers are the fine-STL byte and triangle counts (D-16) -- 0 here because this
    test is about the timeout boundary, not the STL size."""
    assert Timing("x", 20.0, 10.0, 1.0, 0, 0).inside(30)
    assert not Timing("x", 20.0, 10.01, 1.0, 0, 0).inside(30)
    assert not Timing("x", 20.0, 1.0, 10.01, 0, 0).inside(30)


def test_a_binary_stl_is_sized_by_its_length_and_the_triangle_count_its_header_names() -> None:
    """`stl_size()` reads the header's own 4-byte triangle count (bytes 80-84,
    little-endian) rather than walking the facets (RESEARCH.md "Don't Hand-Roll") -- a
    synthetic 84 + 50 * 2 byte STL with a header that says 2 triangles."""
    data = bytes(80) + (2).to_bytes(4, "little") + bytes(50 * 2)
    assert stl_size(data) == (184, 2)


def test_an_stl_whose_length_disagrees_with_its_header_is_refused() -> None:
    """A truncated file -- or an ASCII STL that happens to carry 80 header-like bytes --
    must never yield a plausible-but-wrong triangle count (L08): the header says 2
    triangles but the file is one triangle short."""
    data = bytes(80) + (2).to_bytes(4, "little") + bytes(50)
    with pytest.raises(ValueError, match="184"):
        stl_size(data)


def test_the_report_names_the_largest_fine_stl_and_breaks_a_tie_by_file_order() -> None:
    """Two rows tied for the largest fine STL, and tied for the heaviest worst_request:
    both lines name the first in the list -- `max()`'s documented behaviour (the edge
    a pinned test, not an assumption). Also pins the two new report columns."""
    timings = [
        Timing("a", 1.0, 1.0, 1.0, 1000, 10),
        Timing("b", 1.0, 1.0, 1.0, 1000, 10),  # ties "a" on both worst_request and stl_bytes
        Timing("c", 0.5, 0.5, 0.5, 500, 5),
    ]
    text = report(Path("x.json"), timings, 30, (1.23, 4.56, 7.89))
    assert "| Fine STL (bytes) | Triangles |" in text
    assert "| a | 1.00 | 1.00 | 1.00 | 2.00 | yes | 1000 | 10 |" in text
    assert "**Heaviest:** a -- 2.00 s of 30 s." in text
    assert "**Largest fine STL:** a -- 1000 bytes, 10 triangles." in text


def test_an_empty_sweep_is_refused_rather_than_reported() -> None:
    """An empty sweep is refused loudly, not printed as an empty table that reads as a
    pass."""
    with pytest.raises(ValueError, match="empty"):
        report(Path("empty.json"), [], 30, (0.0, 0.0, 0.0))


def test_the_report_prints_the_load_it_was_given_rather_than_reading_one_itself() -> None:
    """12-03 fix: `report()` used to call `os.getloadavg()` itself, after every row in
    the sweep had already built -- for a multi-minute sweep that made its own "Load
    averages at start" line an end-of-run reading, not a start-of-run one
    (bench/RESULTS.md "Composed build and export time (Phase 12)" intro;
    12-02-SUMMARY.md). A distinctive, made-up load tuple passed in here proves the
    printed figures are the ones the caller supplied -- this is the only way to pin
    "reads no load itself" as a behaviour: `os.getloadavg()`'s real return value is
    whatever the test host happens to read at the moment the test runs, so a live call
    inside `report()` could coincidentally print the same numbers and this test would
    not catch it. A value no real host would ever report (99.99) rules that out."""
    timings = [Timing("a", 1.0, 1.0, 1.0, 100, 1)]
    text = report(Path("x.json"), timings, 30, (99.99, 88.88, 77.77))
    assert "- Load averages at start: 99.99, 88.88, 77.77" in text


def test_the_keyway_bore_sweep_is_every_combination_with_the_largest_keyway_each_rule_allows() -> None:  # noqa: E501
    """The committed Phase 9 sweep is 200 teeth on the largest bore the rules allow
    (bore_d 200, the field's `le`); module {1.75, 10} because module drives fine-STL
    export time (Phase 8's probe); round and D-flat {0, 150} because the D-flat is the
    composition D-02 guards; bore_chamfer {0.4, 3} (3 is the largest D-12's rule allows
    here -- the field's `le` binds, the chamfered mouth sits well inside the root at
    module 1.75); and, for each (module, bore_flat) pair, both the largest keyway the
    rules allow and a 3 x 1.4 mm keyway. The large keyway alone is not enough to find the
    heaviest row: the planning probe found the largest keyway at module 1.75 pushes the
    face recess out entirely, making those rows lighter than a keyed gear that keeps its
    recess (09-CONTEXT.md Claude's Discretion: sweep rows) -- so the sweep measures both
    rather than assuming the biggest keyway is the heaviest.

    Every row is a buildable gear under 09-03's rules -- load_sweep would have raised
    otherwise. Each large keyway also sits exactly one step (0.05 mm) from a refusal:
    +0.05 on keyway_width is refused by D-11 (round) or D-02 (D-flat); +0.05 on
    keyway_depth is refused by D-10 at module 1.75, where the root circle binds first, or
    by keyway_depth's own `le` (200) at module 10, where the field's own bound binds
    before the root ever would.
    """
    sets = load_sweep(DEFAULT_SWEEP.parent / "keyway_bore.json")
    assert len(sets) == 32

    # The largest keyway (width, depth) each rule allows, per (module, bore_flat) --
    # 09-04-PLAN.md's own measured numbers, re-proven live by the +0.05 loop below.
    largest_keyway: dict[tuple[float, float], tuple[float, float]] = {
        (1.75, 0.0): (199.95, 40.3),
        (1.75, 150.0): (99.3, 65.0),
        (10.0, 0.0): (199.95, 200.0),
        (10.0, 150.0): (99.3, 200.0),
    }

    want = set()
    for (module, flat), (width, depth) in largest_keyway.items():
        for keyway_width, keyway_depth in ((width, depth), (3.0, 1.4)):
            for recess, chamfer in itertools.product(("both", "none"), (0.4, 3.0)):
                want.add((200, module, 200.0, flat, keyway_width, keyway_depth,
                          recess, chamfer))
    got = {(p.teeth, p.module, p.bore_d, p.bore_flat, p.keyway_width, p.keyway_depth,
            p.recess_sides, p.bore_chamfer) for _, p in sets}
    assert got == want

    for _, p in sets:
        if (p.keyway_width, p.keyway_depth) == (3.0, 1.4):
            continue  # the small keyway is not on any rule's edge -- nothing to pin
        for field, value in (("keyway_width", p.keyway_width + 0.05),
                             ("keyway_depth", p.keyway_depth + 0.05)):
            with pytest.raises(ValidationError):
                GearParams.model_validate({**p.model_dump(), field: value})


def test_the_tip_chamfer_sweep_is_every_combination_d_06_names() -> None:
    """The committed Phase 10 sweep is D-06's 9 rows, at 200 teeth (the 400-edge case
    10-01's spike found the most expensive single operation this project has measured):
    module {1.75, 10} because module drives fine-STL export time (Phase 8's probe);
    tip_chamfer {0.4, the largest each module allows} -- the pitch circle binds at
    1.75 mm (module 1.75), the field's own `le` binds at 3 mm (module 10); recess_sides
    {both, none} because a recess changes the bare build, the heaviest factor Phase 8
    and 9 both found; and one module-0.2 row, the finest tips this model allows, at the
    backlash (0.07) that keeps its tooth tip above check()'s 0.05 mm floor. 10-01 also
    found the chamfer's cost does not change with `c` (edge count dominates, not depth
    or module), so the 0.4 mm rows are here as a check on that finding, not because
    they are expected to be the heaviest.

    Every row is therefore a buildable gear under 10-02's rules -- load_sweep would
    have raised otherwise.
    """
    sets = load_sweep(DEFAULT_SWEEP.parent / "tip_chamfer.json")
    assert len(sets) == 9

    module_chamfer_pairs = ((1.75, 0.4), (1.75, 1.75), (10.0, 0.4), (10.0, 3.0))
    want = {
        (200, module, 0.1, chamfer, recess)
        for module, chamfer in module_chamfer_pairs
        for recess in ("both", "none")
    }
    want.add((200, 0.2, 0.07, 0.2, "both"))
    got = {(p.teeth, p.module, p.backlash, p.tip_chamfer, p.recess_sides)
           for _, p in sets}
    assert got == want

    for _, p in sets:
        assert (p.bore_d, p.bore_flat, p.bore_chamfer, p.face_width) == (9.0, 8.0, 0.4, 7.5)

    for _, p in sets:
        if p.tip_chamfer == 0.4:
            continue  # not on any limit -- nothing to pin here
        assert tip_chamfer_effective(p) == p.tip_chamfer
        if p.module == 10.0:
            # 3 mm is the field's own `le`: one step past it is a field-level refusal,
            # not a capped-and-warned value.
            with pytest.raises(ValidationError):
                GearParams.model_validate({**p.model_dump(), "tip_chamfer": p.tip_chamfer + 0.05})
        else:
            bumped = GearParams.model_validate(
                {**p.model_dump(), "tip_chamfer": p.tip_chamfer + 0.05})
            assert tip_chamfer_effective(bumped) == p.tip_chamfer

    module_02_set = next(p for _, p in sets if p.module == 0.2)
    with pytest.raises(ValidationError):
        GearParams.model_validate({**module_02_set.model_dump(), "backlash": 0.08})


def test_the_hole_cutout_sweep_is_every_combination_the_plan_names() -> None:
    """The committed Phase 11 hole sweep is 11-06-PLAN.md's `<interfaces>` cross product,
    re-run at Task 2's gate decision: 200 teeth, `hole_count` 60 (D-18's `le` lowered from
    200 -- the 200-hole row crossing the module-1.75 recess groove read 41.85 s of
    SPUR_BUILD_TIMEOUT=30 s, bench/RESULTS.md "Body cutout build and export time
    (Phase 11)"); module {1.75, 10} because module drives fine-STL export time (Phase 8's
    probe); the same small hole (`hole_d` 1) and large hole (`hole_d` 4.9 at module 1.75,
    5.85 at module 10) the first run measured -- 09-04's lesson that the heaviest row is
    not always the largest feature, so both sizes are kept; and `recess_sides` {both,
    none} because a recess is the heaviest factor every prior phase's sweep has found.

    Every row is therefore a buildable gear under 11-03's rules -- `load_sweep` would have
    raised otherwise. The module-1.75 large-hole row still sits exactly one step (0.05 mm)
    from a refusal at the lower `hole_count`: its rim-wall bound (0.4125 mm) does not
    depend on the count, only on `hole_d` and `hole_circle_d`. The module-10 large-hole row
    does not: its bound at `le` 200 was the neighbour gap (count-dependent), which loosens
    at 60 holes -- measured accepted at `hole_d` 5.9, no longer refused -- so only the
    module-1.75 row is pinned here.
    """
    sets = load_sweep(DEFAULT_SWEEP.parent / "hole_cutout.json")
    assert len(sets) == 8

    want = {
        (200, 1.75, 60, 1.0, 183.4, "both"),
        (200, 1.75, 60, 1.0, 183.4, "none"),
        (200, 1.75, 60, 4.9, 339.9, "both"),
        (200, 1.75, 60, 4.9, 339.9, "none"),
        (200, 10.0, 60, 1.0, 400.0, "both"),
        (200, 10.0, 60, 1.0, 400.0, "none"),
        (200, 10.0, 60, 5.85, 400.0, "both"),
        (200, 10.0, 60, 5.85, 400.0, "none"),
    }
    got = {(p.teeth, p.module, p.hole_count, p.hole_d, p.hole_circle_d, p.recess_sides)
           for _, p in sets}
    assert got == want

    for _, p in sets:
        if p.hole_d != 4.9 or p.module != 1.75:
            continue  # only the module-1.75 large-hole row's rim-wall bound is still
            # count-independent at hole_count=60 -- see the docstring's measured note
        with pytest.raises(ValidationError):
            GearParams.model_validate({**p.model_dump(), "hole_d": p.hole_d + 0.05})


def test_the_spoke_cutout_sweep_is_every_combination_the_plan_names() -> None:
    """The committed Phase 11 spoke sweep is 11-06-PLAN.md's `<interfaces>` cross product,
    re-run at Task 2's gate decision, then re-run again at Task 3's own gate: 200 teeth,
    `spoke_count` 32 (D-03's gate lowered `le` again, 40 -> 32 -- 12-03-PLAN.md Task 2's
    human decision, "lower-le: spoke_count 32"; bench/RESULTS.md "Composed build and
    export time (Phase 12)", "### Gate probe": the module=10 keyed-bore composed row
    measured 32.03 s of SPUR_BUILD_TIMEOUT=30 s at 40 arms, 32 the largest count still
    inside budget at 29.41 s); module {1.75, 10} (Phase 8's export-time probe); the same
    large sectors (`spoke_width` 0.4, `hub_d` 52, `rim_wall` 0.4) and small sectors
    (`spoke_width` 4.3 at module 1.75, 5.85 at module 10) the first run measured, at both
    modules -- the planning probe found spoke sectors the heaviest cutout by far, so both
    sector shapes are kept; and `recess_sides` {both, none}.

    Every row is therefore a buildable gear under 11-04's rules -- `load_sweep` would have
    raised otherwise. Neither large-sector row still sits at a refusal boundary at the
    lower `spoke_count`: the hub-opening wall each `spoke_width` was picked against at
    `le` 200 widens with fewer arms (fewer feet sharing the hub ring) -- measured accepted
    at `spoke_width` + 0.05 for both the module-1.75 and module-10 rows at `le` 40 -- so no
    refusal-boundary pin survives either gate's decision, and 32 arms only widens the
    opening further.
    """
    sets = load_sweep(DEFAULT_SWEEP.parent / "spoke_cutout.json")
    assert len(sets) == 8

    want = {
        (200, 1.75, 32, 0.4, 52.0, 0.4, 5.0, "both"),
        (200, 1.75, 32, 0.4, 52.0, 0.4, 5.0, "none"),
        (200, 1.75, 32, 4.3, 300.0, 10.0, 5.0, "both"),
        (200, 1.75, 32, 4.3, 300.0, 10.0, 5.0, "none"),
        (200, 10.0, 32, 0.4, 52.0, 0.4, 5.0, "both"),
        (200, 10.0, 32, 0.4, 52.0, 0.4, 5.0, "none"),
        (200, 10.0, 32, 5.85, 400.0, 100.0, 5.0, "both"),
        (200, 10.0, 32, 5.85, 400.0, 100.0, 5.0, "none"),
    }
    got = {(p.teeth, p.module, p.spoke_count, p.spoke_width, p.hub_d, p.rim_wall,
            p.spoke_fillet, p.recess_sides) for _, p in sets}
    assert got == want


def test_the_honeycomb_sweep_runs_at_the_cap() -> None:
    """The committed Phase 11 honeycomb sweep is 11-06-PLAN.md's `<interfaces>` cross
    product: 200 teeth (D-11's cap-measuring configuration); module {1.75, 10} (Phase 8's
    export-time probe, and 11-02's own confirmation that the smaller module is the
    heavier one); `hex_cell` 3 (the sweep's own chosen input, exactly what 11-02's spike
    used; the field's default is 0 = off); `hex_wall` {0.4, 5} (the widest span the field
    allows without narrowing the web so far no cell fits) x `recess_sides` {both, none}.
    Every one of the four gears (module x recess) is raised past `hex_cell` 3 to the
    largest whole-cell size that still fits `HEX_CELL_CAP` cells (D-13's raise-to-fit) --
    11-02's spike measured this exact configuration at 7.15 s of the 7.5 s share, so every
    row here is expected to run at the cap, not below it.

    Every row is therefore a buildable gear under 11-05's rules -- `load_sweep` would
    have raised otherwise.
    """
    sets = load_sweep(DEFAULT_SWEEP.parent / "honeycomb.json")
    assert len(sets) == 8

    want = {
        (200, 1.75, 3.0, 0.4, "both"),
        (200, 1.75, 3.0, 0.4, "none"),
        (200, 1.75, 3.0, 5.0, "both"),
        (200, 1.75, 3.0, 5.0, "none"),
        (200, 10.0, 3.0, 0.4, "both"),
        (200, 10.0, 3.0, 0.4, "none"),
        (200, 10.0, 3.0, 5.0, "both"),
        (200, 10.0, 3.0, 5.0, "none"),
    }
    got = {(p.teeth, p.module, p.hex_cell, p.hex_wall, p.recess_sides) for _, p in sets}
    assert got == want

    for _, p in sets:
        size, cells = hex_cells(p, profile(p).rf)
        assert size > 3
        assert 0 < len(cells) <= HEX_CELL_CAP


def test_the_composed_sweep_stacks_each_cutout_on_its_heaviest_bore_beside_six_baselines() -> None:
    """The Phase 12 composed sweep (12-CONTEXT.md D-01): what Phases 10 and 11 could
    only add up as an arithmetic total, actually built as one part. Each of the three
    cutout patterns' own recorded heaviest row (bench/RESULTS.md, D-01's numbers) is
    stacked with the tip chamfer at that gear's own cap and both recesses, on the
    heaviest bore its own hub rule allows -- separately a hex bore and a keyed round
    bore -- at module 1.75 and module 10 (12 rows), plus the six single-feature heaviest
    rows re-run unchanged as same-host baselines (6 rows). 09-04's lesson stands: the
    heaviest row was not always the largest feature, so both modules are measured for
    every pattern rather than assumed from one.

    Every row is therefore a buildable gear under the live composition rules -- load_sweep
    would have raised otherwise (bench.build_time.load_sweep's own contract). The hex
    bore's size (`bore_hex` 43.35 for the spokes' `hub_d` 52, 156.3 for the module-1.75
    holes, 200 -- the field's own `le` -- everywhere else) is the largest each hub rule
    allows, computed from `bore_mouth_limit` against the cutout's hub datum
    (bore_hex 200 mm reaches 115.47 mm at the corners and conflicts with the spoke row's
    26 mm hub and the module-1.75 hole row's 91.2 mm inner edge -- 12-CONTEXT.md
    `<specifics>`); one step (0.05 mm) past it is refused naming the cutout's own hub
    fields, never the bore's. The keyed round bore (`bore_d` 9, `bore_flat` 0,
    `keyway_width` 3, `keyway_depth` 1.4 -- the default bore's own keyway) composes with
    every cutout row unchanged: its floor corner sits at ~6.18 mm, well inside every
    cutout's hub datum. `tip_chamfer` is each gear's own cap: 1.75 mm at module 1.75 (the
    pitch circle binds, `tip_chamfer_limit`'s "to keep it above the pitch circle"
    reason), 3 mm at module 10 (the field's own `le`; the analytic caps sit at 3.375 mm,
    uncapped).
    """
    sets = load_sweep(DEFAULT_SWEEP.parent / "composed.json")
    assert len(sets) == 18

    want = [
        {"teeth": 200, "tip_chamfer": 1.75, "bore_hex": 43.35, "spoke_count": 32,
         "spoke_width": 0.4, "hub_d": 52.0, "rim_wall": 0.4, "spoke_fillet": 5.0},
        {"teeth": 200, "tip_chamfer": 1.75, "bore_flat": 0.0, "keyway_width": 3.0,
         "keyway_depth": 1.4, "spoke_count": 32, "spoke_width": 0.4, "hub_d": 52.0,
         "rim_wall": 0.4, "spoke_fillet": 5.0},
        {"teeth": 200, "module": 10.0, "tip_chamfer": 3.0, "bore_hex": 43.35,
         "spoke_count": 32, "spoke_width": 0.4, "hub_d": 52.0, "rim_wall": 0.4,
         "spoke_fillet": 5.0},
        {"teeth": 200, "module": 10.0, "tip_chamfer": 3.0, "bore_flat": 0.0,
         "keyway_width": 3.0, "keyway_depth": 1.4, "spoke_count": 32, "spoke_width": 0.4,
         "hub_d": 52.0, "rim_wall": 0.4, "spoke_fillet": 5.0},
        {"teeth": 200, "tip_chamfer": 1.75, "bore_hex": 156.3, "hole_count": 60,
         "hole_d": 1.0, "hole_circle_d": 183.4},
        {"teeth": 200, "tip_chamfer": 1.75, "bore_flat": 0.0, "keyway_width": 3.0,
         "keyway_depth": 1.4, "hole_count": 60, "hole_d": 1.0, "hole_circle_d": 183.4},
        {"teeth": 200, "module": 10.0, "tip_chamfer": 3.0, "bore_hex": 200.0,
         "hole_count": 60, "hole_d": 5.85, "hole_circle_d": 400.0},
        {"teeth": 200, "module": 10.0, "tip_chamfer": 3.0, "bore_flat": 0.0,
         "keyway_width": 3.0, "keyway_depth": 1.4, "hole_count": 60, "hole_d": 5.85,
         "hole_circle_d": 400.0},
        {"teeth": 200, "tip_chamfer": 1.75, "bore_hex": 200.0, "hex_cell": 3.0,
         "hex_wall": 0.4},
        {"teeth": 200, "tip_chamfer": 1.75, "bore_flat": 0.0, "keyway_width": 3.0,
         "keyway_depth": 1.4, "hex_cell": 3.0, "hex_wall": 0.4},
        {"teeth": 200, "module": 10.0, "tip_chamfer": 3.0, "bore_hex": 200.0,
         "hex_cell": 3.0, "hex_wall": 5.0},
        {"teeth": 200, "module": 10.0, "tip_chamfer": 3.0, "bore_flat": 0.0,
         "keyway_width": 3.0, "keyway_depth": 1.4, "hex_cell": 3.0, "hex_wall": 5.0},
        {"teeth": 200, "bore_hex": 200.0},
        {"teeth": 200, "bore_d": 200.0, "bore_flat": 150.0, "keyway_width": 3.0,
         "keyway_depth": 1.4},
        {"teeth": 200, "tip_chamfer": 1.75},
        {"teeth": 200, "hole_count": 60, "hole_d": 1.0, "hole_circle_d": 183.4},
        {"teeth": 200, "module": 10.0, "spoke_count": 32, "spoke_width": 0.4,
         "hub_d": 52.0, "rim_wall": 0.4, "spoke_fillet": 5.0},
        {"teeth": 200, "hex_cell": 3.0, "hex_wall": 0.4},
    ]
    got = [p.model_dump(exclude_defaults=True) for _, p in sets]
    assert got == want

    # Each hex row below 200 sits exactly one 0.05 mm step from the largest bore_hex
    # its cutout's own hub rule allows -- the refusal names the cutout's hub fields,
    # never bore_hex itself (D-01's "the heaviest bore its hub rule allows"). A row at
    # 200 sits on the field's own `le` instead: one step past it is a plain field-level
    # refusal with no hub sentence, so it is excluded here.
    for _, p in sets:
        if p.bore_hex <= 0 or p.bore_hex >= 200:
            continue
        hub_fields = {"hub_d"} if p.spoke_count > 0 else {"hole_circle_d", "hole_d"}
        with pytest.raises(ValidationError) as exc_info:
            GearParams.model_validate({**p.model_dump(), "bore_hex": p.bore_hex + 0.05})
        assert set(exc_info.value.errors()[0]["ctx"]["fields"]) == hub_fields

    # Each composed row's tip_chamfer is that gear's own cap, not an assumed constant --
    # tip_chamfer_limit depends only on the tooth profile (teeth, module, pressure_angle,
    # profile_shift, backlash, root_fillet), never on the bore, so the hex and keyed rows
    # at the same module share the same limit.
    for _, p in sets[:12]:
        if p.module == 1.75:
            assert p.tip_chamfer == round(tip_chamfer_limit(p)[0], 3)
        else:
            assert p.module == 10.0
            assert tip_chamfer_effective(p) == 3.0
            assert tip_chamfer_limit(p)[0] > 3

    # The six baselines (rows 13-18) are re-run unchanged: each label is one load_sweep
    # would read from the row's own original sweep file (D-01 -- a same-host baseline,
    # not a re-derived one).
    baseline_sources = ("hex_bore", "keyway_bore", "tip_chamfer", "hole_cutout",
                        "spoke_cutout", "honeycomb")
    baseline_labels = [label for label, _ in sets[12:]]
    assert len(baseline_labels) == 6
    for label, source in zip(baseline_labels, baseline_sources, strict=True):
        original_labels = {lbl for lbl, _ in load_sweep(DEFAULT_SWEEP.parent / f"{source}.json")}
        assert label in original_labels


def test_l19s_rule_applied_to_its_own_table_keeps_level_1() -> None:
    """L19's own recorded table (`src/spur/app.py`'s `_GZIP_LEVEL` comment): neither
    level 6 nor level 9 reaches the 10% shrink bar over level 1 (8.7% and 8.66%), so the
    rule keeps level 1 -- the same reading L19 itself recorded by hand (D-18)."""
    rows = [
        GzipRow(level=1, single_ms=51.5, out_bytes=2_632_467, concurrent_ms=74.4),
        GzipRow(level=6, single_ms=147.9, out_bytes=2_403_312, concurrent_ms=198.9),
        GzipRow(level=9, single_ms=788.0, out_bytes=2_404_371, concurrent_ms=925.5),
    ]
    assert select_gzip_level(rows) == 1


def test_a_higher_gzip_level_is_adopted_exactly_on_both_of_l19s_bars() -> None:
    """A level 6 row exactly 10% smaller than level 1, with a 10-concurrent wall exactly
    1.5x level 1's, is adopted; 1 byte less shrink, or a wall 1.5x plus a millisecond,
    holds level 1 instead (D-18's two bars, tested at both edges). Level 9 is held equal
    to level 1 in every row here so it can never itself be adopted, isolating level 6's
    own boundary."""
    level1 = GzipRow(level=1, single_ms=50.0, out_bytes=1_000_000, concurrent_ms=100.0)
    inert_level9 = GzipRow(level=9, single_ms=500.0, out_bytes=1_000_000, concurrent_ms=100.0)

    at_both_bars = GzipRow(level=6, single_ms=100.0, out_bytes=900_000, concurrent_ms=150.0)
    assert select_gzip_level([level1, at_both_bars, inert_level9]) == 6

    one_byte_short_of_the_shrink_bar = GzipRow(
        level=6, single_ms=100.0, out_bytes=900_001, concurrent_ms=150.0)
    assert select_gzip_level([level1, one_byte_short_of_the_shrink_bar, inert_level9]) == 1

    one_millisecond_past_the_wall_bar = GzipRow(
        level=6, single_ms=100.0, out_bytes=900_000, concurrent_ms=150.001)
    assert select_gzip_level([level1, one_millisecond_past_the_wall_bar, inert_level9]) == 1


def test_level_9_is_compared_against_the_level_currently_adopted() -> None:
    """With 6 not adopted, 9 is compared against 1 (L19's own reading, A1); with 6
    adopted, 9 is compared against 6, not always against 1 -- the second row below
    would wrongly adopt level 9 if the comparison stayed pinned to level 1 (D-18)."""
    level1 = GzipRow(level=1, single_ms=50.0, out_bytes=1_000_000, concurrent_ms=100.0)

    # Level 6 held (only 5% smaller than 1): level 9 shrinks 20% off level 1 and its
    # wall is 1.4x level 1's -- adopted, compared against level 1.
    level6_held = GzipRow(level=6, single_ms=100.0, out_bytes=950_000, concurrent_ms=110.0)
    level9_beats_1 = GzipRow(level=9, single_ms=200.0, out_bytes=800_000, concurrent_ms=140.0)
    assert select_gzip_level([level1, level6_held, level9_beats_1]) == 9

    # Level 6 adopted (exactly at both bars, out_bytes 900_000): level 9's out_bytes
    # (850_000) is 15% smaller than level 1's -- past the 10% bar if compared there --
    # but only 5.6% smaller than level 6's, under the bar against the level actually
    # adopted. `concurrent_ms` is held at 100 -- inside *both* bases' wall bars (<=150
    # against level 1, <=225 against level 6) -- so the wall clause cannot decide this
    # row either way; only the shrink clause can, and it decides oppositely depending on
    # which level the comparison lands on. The real implementation compares against the
    # level actually adopted (6), so this row's shrink is under the bar and level 9 stays
    # unadopted: held at 6. A regression that re-pinned the comparison to level 1 would
    # read the 15% shrink past the bar, wall still clear, and wrongly adopt 9 -- flipping
    # this assertion's result to 9 and failing it (verified by hand against both the real
    # and a hand-rolled pinned-to-1 `_decisions`, see commit message).
    level6_adopted = GzipRow(level=6, single_ms=100.0, out_bytes=900_000, concurrent_ms=150.0)
    level9_beats_1_not_6 = GzipRow(level=9, single_ms=200.0, out_bytes=850_000, concurrent_ms=100.0)
    assert select_gzip_level([level1, level6_adopted, level9_beats_1_not_6]) == 6


def test_peak_rss_reads_bytes_on_macos_and_kibibytes_on_linux() -> None:
    """`ru_maxrss` is bytes on Darwin (macOS) and kibibytes on every other platform this
    project runs on (Linux, in the image) -- the same split L24's own reading needs
    a per-platform unit to be believed at all."""
    assert maxrss_bytes(1000, "Darwin") == 1000
    assert maxrss_bytes(1000, "Linux") == 1024000


def test_the_composed_latency_scenario_fires_the_worst_composed_row_first_then_the_next_nine_heaviest() -> None:  # noqa: E501
    """D-13: the ten rows SC3 fires are `bench/sweeps/composed.json`'s 0-based indices
    3, 1, 2, 0, 8, 5, 9, 11, 10, 4 (1-based 4, 2, 3, 1, 9, 6, 10, 12, 11, 5) -- the worst
    row (29.42 s alone, `bench/RESULTS.md` "### Re-run after the gate (lower-le:
    spoke_count 32)") first, then the re-run table's next nine heaviest by "Build +
    slower export" (28.92, 28.87, 28.61, 27.27, 24.91, 24.06, 22.26, 22.09, 16.80 s).
    Ten distinct keys so admission control (`MAX_QUEUED_BUILDS` 4) takes four of them and
    `hash(p) % workers` spreads the four admitted builds over both workers, stacking
    kernel work on the host rather than queuing every admitted build behind one worker.
    `_composed_rows()` reads the sweep file directly (not through `load_sweep`, which
    pulls `spur.model` -- and so cadquery -- into this harness's own measuring client);
    this test is the one place the two readings are checked to agree."""
    got = [GearParams.model_validate(r) for r in _composed_rows()]
    want = [load_sweep(DEFAULT_SWEEP.parent / "composed.json")[i][1]
            for i in (3, 1, 2, 0, 8, 5, 9, 11, 10, 4)]
    assert got == want
    assert len(got) == 10
    assert len({p.model_dump_json() for p in got}) == 10  # all ten distinct
    assert got[0].model_dump(exclude_defaults=True) == {
        "teeth": 200, "module": 10.0, "tip_chamfer": 3.0, "bore_flat": 0.0,
        "keyway_width": 3.0, "keyway_depth": 1.4, "spoke_count": 32,
        "spoke_width": 0.4, "hub_d": 52.0, "rim_wall": 0.4, "spoke_fillet": 5.0,
    }


def test_the_no_argument_latency_run_is_still_concurrent_then_single() -> None:
    """D-07/D-15/D-16: registering `composed` in `_SCENARIOS` must not put it into the
    no-argument run (`sorted(_SCENARIOS)` would put it first), where a timed-out worker
    it replaces could pollute the bar's own reading -- `DEFAULT_SCENARIOS` pins the
    order the no-argument run has always had. Phase 17 registers a fourth, `identical`
    (REQ-same-slot-timeout-race-reproduced), which times out and replaces workers by
    design and so stays out of the tuple for the same reason."""
    assert DEFAULT_SCENARIOS == ("concurrent", "single")
    assert set(_SCENARIOS) == {"concurrent", "single", "composed", "identical"}


def test_a_503_is_recorded_by_the_reason_the_server_gave() -> None:
    """`_fetch` turns a 200 into `"200"`, and a 503 into `"503 " + detail[0]["type"]`
    read from the body -- `busy`, `timeout` and `pool_broken` are `src/spur/app.py`'s
    own three 503 `type` values (`_build_slot`'s admission refusal, `BuildTimeout`,
    `BrokenProcessPool`). Any other status still raises (`_build`'s own rule). No
    network: `httpx.MockTransport` stands in for the server."""

    def handler(request: httpx.Request) -> httpx.Response:
        case = request.url.params["case"]
        if case == "200":
            return httpx.Response(200, content=b"stl-bytes")
        if case in ("busy", "timeout", "pool_broken"):
            return httpx.Response(
                503, json={"detail": [{"loc": ["query"], "type": case, "msg": case}]})
        return httpx.Response(500, content=b"boom")

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as client:
        outcome = _fetch("http://test", client, {"case": "200"})
        assert outcome.status == "200"
        assert outcome.params == "case=200"
        assert outcome.done >= outcome.sent

        for case in ("busy", "timeout", "pool_broken"):
            outcome = _fetch("http://test", client, {"case": case})
            assert outcome.status == f"503 {case}"

        with pytest.raises(httpx.HTTPStatusError):
            _fetch("http://test", client, {"case": "500"})


def test_a_500_is_recorded_only_when_the_caller_asks() -> None:
    """REQ-same-slot-timeout-race-reproduced: a 500 is not one of the service's three
    documented refusals, so `_fetch` raises on it by default (SC3's rule, pinned by
    `test_a_503_is_recorded_by_the_reason_the_server_gave`). The `identical` scenario
    exists to observe exactly that 500, so it passes `record_500=True` and the run
    finishes with the 500 in its table. Only a 500 is recorded: any other status
    still raises, with either value. No network: `httpx.MockTransport`."""

    def handler(request: httpx.Request) -> httpx.Response:
        case = request.url.params["case"]
        return httpx.Response(int(case), content=b"body")

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as client:
        outcome = _fetch("http://test", client, {"case": "500"}, record_500=True)
        assert outcome.status == "500"
        assert outcome.params == "case=500"

        with pytest.raises(httpx.HTTPStatusError):
            _fetch("http://test", client, {"case": "500"})
        with pytest.raises(httpx.HTTPStatusError):
            _fetch("http://test", client, {"case": "500"}, record_500=False)
        for record_500 in (False, True):
            with pytest.raises(httpx.HTTPStatusError):
                _fetch("http://test", client, {"case": "404"}, record_500=record_500)


def test_the_identical_scenario_fires_the_worst_composed_row_ten_times() -> None:
    """REQ-same-slot-timeout-race-reproduced (Phase 13's deferred queue-wait scenario):
    ten copies of the composed worst row (29.42 s alone, `bench/sweeps/composed.json`
    row 4) are one cache key, so D-07's hash affinity sends every admitted copy to one
    worker slot -- the same-slot double timeout SC3 hit by affinity luck. The row is
    the same one `_composed_rows()` fires first, and it validates to the sweep's own
    reading of that row."""
    rows = _identical_rows()
    assert len(rows) == 10
    assert all(row == _composed_rows()[0] for row in rows)
    assert GearParams.model_validate(rows[0]) == load_sweep(
        DEFAULT_SWEEP.parent / "composed.json")[3][1]


def test_the_composed_report_omits_the_single_concurrent_baseline_line() -> None:
    """WR-01: `_report_markdown` is reused for all three scenarios via `_run_scenario`.
    `RECORDED_BASELINE` is the debt file's `single`/`concurrent` numbers (D-17) -- printed
    unconditionally, it would appear under a `"composed"` heading too, where it has
    nothing to do with the composed sweep's own numbers and would invite a reader to
    compare the composed ratio against a baseline measured for a different scenario
    entirely. Omitted for `name="composed"` and, since Phase 17, `name="identical"`
    (the same composed worst row, ten times); still printed for the two scenarios it
    actually describes."""
    for name in ("composed", "identical"):
        omitted = _report_markdown(name, 0.001, 100, 0.002, 100, 1.0, 10, 0)
        assert RECORDED_BASELINE not in omitted
        assert "Recorded baseline" not in omitted
        assert "pass bar" not in omitted  # IN-02: no bar applies to these two

    for name in ("single", "concurrent"):
        report = _report_markdown(name, 0.001, 100, 0.002, 100, 1.0, 10, 0)
        assert RECORDED_BASELINE in report
        assert "Recorded baseline" in report
        assert "pass bar is <= 2.00x" in report


def test_the_trochoid_sweep_is_the_cross_product_the_plan_names() -> None:
    """The committed Phase 18 sweep is 18-03-PLAN.md's two grids, written out as literals
    here again so that a grid that quietly shrinks fails (18-RESEARCH Pitfall 1: STACK's
    "7,296" was not a floor of anything).

    Grid A is STACK's whole 7,980-case product: module 1; teeth 6 to 40, 60, 100, 200 (38);
    profile shift -0.6 (the field's limit, in place of the -1 GearParams rejects), -0.5,
    -0.2, 0, 0.2, 0.5, 1.0 (7); 14.5 / 20 / 25 degrees; backlash 0 and 0.10; tip radius
    0, 0.1, 0.25, 0.38 and 0.5 times the module, plus the cap request: 1,596 gears,
    9,576 cases, of which 1,489 are gears GearParams accepts. Grid B is the box corners:
    module 0.2 / 1.75 / 10; 18 tooth counts around every edge; nine pressure angles, the
    32.0 / 32.5 and 33.0 / 33.5 pairs either side of the tip-land limit among them;
    profile shift -0.6 / 0 / 1.0; backlash 0 / 0.10 / 1.0; tip radius 0, 0.25 m, 0.5 m,
    0.5 mm and the cap request: 4,374 gears, 21,870 cases, 1,924 accepted. The x = 1.0
    rows with a tip radius at or over the tip depth are kept, not dropped."""
    cases = list(sweep_cases())
    assert len(cases) == 9576 + 21870
    a = [(kwargs, rho) for grid, kwargs, rho in cases if grid == "A"]
    b = [(kwargs, rho) for grid, kwargs, rho in cases if grid == "B"]
    assert (len(a), len(b)) == (9576, 21870)

    def gear_key(kwargs: dict[str, object]) -> tuple[object, ...]:
        return tuple(kwargs[k] for k in
                     ("module", "teeth", "pressure_angle", "profile_shift", "backlash"))

    def axis(rows: list[tuple[dict[str, object], float]], name: str) -> set[object]:
        return {kwargs[name] for kwargs, _ in rows}

    assert len({gear_key(kwargs) for kwargs, _ in a}) == 1596
    assert len({gear_key(kwargs) for kwargs, _ in b}) == 4374
    assert axis(a, "module") == {1.0}
    assert axis(a, "teeth") == {*range(6, 41), 60, 100, 200}
    assert axis(a, "profile_shift") == {-0.6, -0.5, -0.2, 0.0, 0.2, 0.5, 1.0}
    assert axis(a, "pressure_angle") == {14.5, 20.0, 25.0}
    assert axis(a, "backlash") == {0.0, 0.10}
    assert {rho for _, rho in a} == {0.0, 0.1, 0.25, 0.38, 0.5, 3.0}
    assert axis(b, "module") == {0.2, 1.75, 10.0}
    assert axis(b, "teeth") == {6, 7, 8, 9, 10, 12, 14, 17, 18, 20, 25, 30, 40, 60, 100,
                                116, 117, 200}
    assert axis(b, "pressure_angle") == {14.5, 20.0, 25.0, 30.0, 32.0, 32.5, 33.0, 33.5, 35.0}
    assert axis(b, "profile_shift") == {-0.6, 0.0, 1.0}
    assert axis(b, "backlash") == {0.0, 0.10, 1.0}
    for module in (0.2, 1.75, 10.0):
        assert {rho for kwargs, rho in b if kwargs["module"] == module} == {
            0.0, 0.25 * module, 0.5 * module, 0.5, 3.0}
    assert -1.0 not in axis(a, "profile_shift") | axis(b, "profile_shift")
    assert all(kwargs["bore_d"] == 0 and kwargs["recess_sides"] == "none"
               for _, kwargs, _ in cases)

    def accepted(rows: list[tuple[dict[str, object], float]]) -> int:
        gears = {gear_key(kwargs): kwargs for kwargs, _ in rows}.values()
        count = 0
        for kwargs in gears:
            try:
                GearParams.model_validate(kwargs)
            except ValidationError:
                continue
            count += 1
        return count

    assert (accepted(a), accepted(b)) == (1489, 1924)


def test_check_curve_reports_a_curve_that_does_not_rise() -> None:
    """The sweep's per-curve checker has to be able to fail: a real curve (10 teeth,
    module 1, 20 degrees, tip radius 0.38 mm) reads clean, and the same curve with its
    second radius pulled under the first, a loop in the making, is reported."""
    p = GearParams.model_validate({"teeth": 10, "module": 1, "pressure_angle": 20,
                                   "profile_shift": 0, "backlash": 0, "bore_d": 0,
                                   "bore_flat": 0, "bore_chamfer": 0,
                                   "recess_sides": "none"})
    curve = trochoid_root(cutter(p, 0.38))
    assert curve is not None
    rk = rack(p, 0.38)
    assert check_curve(curve, rk) == []

    points = list(curve.points)
    points[1] = (points[0][0] - 0.01, points[1][1])
    bent = RootCurve(points=tuple(points), join=curve.join, waist=curve.waist)
    assert "radius does not strictly rise" in check_curve(bent, rk)


def test_check_curve_reports_a_crossing_whose_end_leaves_the_involute() -> None:
    """The join-band allowance is for tangent joins only (cross-review XR-01): the same
    10-tooth gear is deeply undercut (xi -1.21 mm, join `crossing`), and with the
    allowance applied to every negative xi its end point could sit 1.1e-2 rad off the
    involute unreported. The end half-angle pushed 1e-2 rad out must be reported."""
    p = GearParams.model_validate({"teeth": 10, "module": 1, "pressure_angle": 20,
                                   "profile_shift": 0, "backlash": 0, "bore_d": 0,
                                   "bore_flat": 0, "bore_chamfer": 0,
                                   "recess_sides": "none"})
    curve = trochoid_root(cutter(p, 0.38))
    assert curve is not None
    assert curve.join == "crossing"
    rk = rack(p, 0.38)
    assert check_curve(curve, rk) == []

    points = list(curve.points)
    radius, half = points[-1]
    points[-1] = (radius, half + 0.01)
    moved = RootCurve(points=tuple(points), join=curve.join, waist=curve.waist)
    assert "last half-angle 1.00e-02 rad off the involute" in check_curve(moved, rk)


def test_the_oracle_worker_reads_a_curve_clean_and_a_severed_tooth_as_a_gouge() -> None:
    """`bench.trochoid oracle`'s worker, on the two kinds of case it judges: the tracer
    gear's curve reads within the bar (about 1e-15 mm), and the 6-tooth, 14.5 degree,
    x -0.6, sharp-cutter gear, whose tooth the neighbouring spaces cut through, reads a
    gouge on its one flank with the neighbouring cutter teeth on (-0.139 mm, measured
    2026-10-08). A worker that read 0 on both would pass the whole product vacuously."""
    base = {"bore_d": 0, "bore_flat": 0, "bore_chamfer": 0, "recess_sides": "none",
            "module": 1.0, "backlash": 0.0}
    tracer = {**base, "teeth": 10, "pressure_angle": 20.0, "profile_shift": 0.0}
    severed = {**base, "teeth": 6, "pressure_angle": 14.5, "profile_shift": -0.6}
    assert 0 <= _oracle(("A", tracer, 0.38, "trochoid")) <= ORACLE_BAR_MM
    assert _oracle(("A", severed, 0.0, "severed")) < -1e-3


def test_the_d05_premise_line_sits_25_percent_either_side_of_0_14_m() -> None:
    """D-05's comparison line, fixed before the step was measured: D-01's premise holds
    within 25 % either side of 0.14*m. Pinned at points 1e-4*m inside and outside the
    band, never at its float64 edges: (1 - 0.25) * 0.14 is 0.10500000000000001, so 0.105
    itself falls a hair outside (checked at planning, 2026-10-07). The band scales with
    the module, and the sign of the gap does not matter."""
    for module, inside, outside in (
        (1.0, (0.11, 0.17), (0.1049, 0.1751)),
        (2.0, (0.22, 0.34), (0.2098, 0.3502)),
    ):
        assert all(premise_holds(g, module) for g in inside)
        assert all(premise_holds(-g, module) for g in inside)
        assert not any(premise_holds(g, module) for g in outside)
        assert not any(premise_holds(-g, module) for g in outside)


def test_the_chamfer_law_verdict_is_never_optimistic() -> None:
    """19-01's verdict on one bisected row: a chamfer that last built more than
    TIP_CHAMFER_MARGIN (0.001 mm) inside pred = ra - R_join is "optimistic" -- the only
    failing reading, because the cap would let a user ask for a chamfer the kernel cannot
    cut (L03, L08). One building past pred is "conservative", as L29's sixth row was. Pinned
    at points clear of the margin's float edge."""
    assert chamfer_verdict(1.0, 1.0) == "on the law"
    assert chamfer_verdict(1.0005, 1.0) == "on the law"
    assert chamfer_verdict(1.05, 1.0) == "conservative"
    assert chamfer_verdict(0.998, 1.0) == "optimistic"


def test_the_chamfer_rows_are_fourteen_trochoid_gears() -> None:
    """The spike's rows are 18-RESEARCH-era scratch rows typed out, never generated from
    calc: seven gears at tip radius 0 and 0.5 mm. Each is a trochoid gear, its junction
    sits where the scratch run read it (pred = ra - R_join, four places), and only the two
    6-tooth rows have the junction above the pitch circle -- the one place ra - R_join is
    the binding cap (F6)."""
    assert len(CHAMFER_ROWS) == 14
    assert len({row.label for row in CHAMFER_ROWS}) == 7
    assert {(row.label, row.rho) for row in CHAMFER_ROWS} == {
        (row.label, rho) for row in CHAMFER_ROWS for rho in (0.0, 0.5)}

    above_pitch = []
    for row in CHAMFER_ROWS:
        p = GearParams.model_validate(row.fields)
        pr = profile(p)
        rm = root_mode(p, pr, requested="trochoid", rho=row.rho)
        assert rm.mode == "trochoid", row.label
        assert rm.cutter is not None
        curve = trochoid_root(rm.cutter)
        assert curve is not None
        assert pr.ra - curve.points[-1][0] == pytest.approx(row.scratch_pred, abs=1e-4)
        if curve.points[-1][0] > pr.r:
            above_pitch.append(row)
    assert [(row.fields["teeth"], row.rho) for row in above_pitch] == [(6, 0.0), (6, 0.5)]
