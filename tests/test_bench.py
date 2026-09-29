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
`HEX_CELL_CAP` on every row.

Run as `.venv/bin/python -m pytest tests/test_bench.py -q` **from the repo root** -- the
`-m` form is what puts the repo root on `sys.path`, which is what makes `import bench`
resolve at all: `bench` is not installed into the venv (it isn't listed in
`pyproject.toml`'s `[tool.hatch.build.targets.wheel] packages`), and there is no
`tests/__init__.py` or `conftest.py` anywhere in this repo to do it another way. A bare
`.venv/bin/pytest` would not find `bench` (hard_fact_4, 260924-bv5-PLAN.md).
"""

from __future__ import annotations

import itertools
import math

import pytest
from pydantic import ValidationError

from bench.build_time import DEFAULT_SWEEP, Timing, load_sweep
from bench.memory import _CAP_TOLERANCE_FRACTION, _SWEEP_MEM_LIMIT_BYTES, _is_capped
from spur.calc import HEX_CELL_CAP, hex_cells, profile, tip_chamfer_effective
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
    exports, not both summed. Exactly the timeout is still inside it."""
    assert Timing("x", 20.0, 10.0, 1.0).inside(30)
    assert not Timing("x", 20.0, 10.01, 1.0).inside(30)
    assert not Timing("x", 20.0, 1.0, 10.01).inside(30)


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
    re-run at Task 2's gate decision: 200 teeth, `spoke_count` 40 (D-18's `le` lowered
    from 200 -- three of the four 200-sector recess-crossing rows read 65.70-68.70 s of
    SPUR_BUILD_TIMEOUT=30 s, bench/RESULTS.md "Body cutout build and export time
    (Phase 11)"); module {1.75, 10} (Phase 8's export-time probe); the same large sectors
    (`spoke_width` 0.4, `hub_d` 52, `rim_wall` 0.4) and small sectors (`spoke_width` 4.3 at
    module 1.75, 5.85 at module 10) the first run measured, at both modules -- the
    planning probe found spoke sectors the heaviest cutout by far, so both sector shapes
    are kept; and `recess_sides` {both, none}.

    Every row is therefore a buildable gear under 11-04's rules -- `load_sweep` would have
    raised otherwise. Neither large-sector row still sits at a refusal boundary at the
    lower `spoke_count`: the hub-opening wall each `spoke_width` was picked against at
    `le` 200 widens with fewer arms (fewer feet sharing the hub ring) -- measured accepted
    at `spoke_width` + 0.05 for both the module-1.75 and module-10 rows -- so no
    refusal-boundary pin survives the gate's decision.
    """
    sets = load_sweep(DEFAULT_SWEEP.parent / "spoke_cutout.json")
    assert len(sets) == 8

    want = {
        (200, 1.75, 40, 0.4, 52.0, 0.4, 5.0, "both"),
        (200, 1.75, 40, 0.4, 52.0, 0.4, 5.0, "none"),
        (200, 1.75, 40, 4.3, 300.0, 10.0, 5.0, "both"),
        (200, 1.75, 40, 4.3, 300.0, 10.0, 5.0, "none"),
        (200, 10.0, 40, 0.4, 52.0, 0.4, 5.0, "both"),
        (200, 10.0, 40, 0.4, 52.0, 0.4, 5.0, "none"),
        (200, 10.0, 40, 5.85, 400.0, 100.0, 5.0, "both"),
        (200, 10.0, 40, 5.85, 400.0, 100.0, 5.0, "none"),
    }
    got = {(p.teeth, p.module, p.spoke_count, p.spoke_width, p.hub_d, p.rim_wall,
            p.spoke_fillet, p.recess_sides) for _, p in sets}
    assert got == want


def test_the_honeycomb_sweep_runs_at_the_cap() -> None:
    """The committed Phase 11 honeycomb sweep is 11-06-PLAN.md's `<interfaces>` cross
    product: 200 teeth (D-11's cap-measuring configuration); module {1.75, 10} (Phase 8's
    export-time probe, and 11-02's own confirmation that the smaller module is the
    heavier one); `hex_cell` 3 (the field's own default, exactly what 11-02's spike used);
    `hex_wall` {0.4, 5} (the widest span the field allows without narrowing the web so
    far no cell fits) x `recess_sides` {both, none}. Every one of the four gears (module x
    recess) is raised past `hex_cell` 3 to the largest whole-cell size that still fits
    `HEX_CELL_CAP` cells (D-13's raise-to-fit) -- 11-02's spike measured this exact
    configuration at 7.15 s of the 7.5 s share, so every row here is expected to run at
    the cap, not below it.

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
