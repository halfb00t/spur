"""Pure tests for `bench.memory`'s capping predicate (CR-02 review) -- no Docker daemon
needed; `_is_capped` is a plain function over two byte counts.

Run as `.venv/bin/python -m pytest tests/test_bench.py -q` **from the repo root** -- the
`-m` form is what puts the repo root on `sys.path`, which is what makes `import bench`
resolve at all: `bench` is not installed into the venv (it isn't listed in
`pyproject.toml`'s `[tool.hatch.build.targets.wheel] packages`), and there is no
`tests/__init__.py` or `conftest.py` anywhere in this repo to do it another way. A bare
`.venv/bin/pytest` would not find `bench` (hard_fact_4, 260924-bv5-PLAN.md).
"""

from __future__ import annotations

import math

from bench.memory import _CAP_TOLERANCE_FRACTION, _SWEEP_MEM_LIMIT_BYTES, _is_capped


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
