"""Pure tests for `bench.memory`'s capping predicate (CR-02 review) -- no Docker daemon
needed; `_is_capped` is a plain function over two byte counts. Also covers
`bench.build_time`'s sweep file and budget predicate (08-04): the Phase 8 hex-bore sweep
is D-11's exact cross product, and `Timing.inside` pins the budget boundary. Also pins
the Phase 9 keyway sweep (09-04): its own cross product, with the largest keyway each
rule allows sitting exactly one step from a refusal.

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
