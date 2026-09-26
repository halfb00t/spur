# CI resolves the kernel from an unpinned range; the fixture pins one kernel exactly

Severity: must
Status: active
Date: 2026-09-26
Source: Phase 7 planning (07-01)
Related files:
- tests/regression/pre_v0_2.json (provenance header: `cadquery`, `cadquery-ocp`)
- tests/regression/test_pre_v0_2.py:test_the_fixture_was_captured_on_the_kernel_this_run_uses
- pyproject.toml (`cadquery>=2.5`)
- .github/workflows/ci.yml (`make verify PYTHON=python` on a fresh venv)

## Context

`tests/regression/pre_v0_2.json` pins exact face and edge counts, exact volume (rel=1e-6)
and exact bounding-box corners (abs=1e-6) captured on one resolved kernel pair: cadquery
2.8.0 / cadquery-ocp 7.9.3.1.1 (read 2026-09-26, this repo's `.venv`; CI run 36214108989
resolved the same pair). CI's `make verify PYTHON=python` builds a fresh venv from
`pyproject.toml`'s `cadquery>=2.5` range at run time — it does not pin a version. Today
CI and the fixture agree only because cadquery 2.8.0's own dependency spec caps
`cadquery-ocp<8.0,>=7.9.3.1`, and cadquery-ocp 8.0.1.0.0 is already published on PyPI but
outside that cap. The moment a cadquery release lifts or changes that cap, CI's fresh
resolve can land on a different `cadquery-ocp`, and the fixture's exact-value assertions
compare against numbers captured on a kernel CI no longer runs.

## Why it matters

A kernel-driven OCCT topology change (a different face count, a shifted bounding-box
corner, a different volume) would turn CI red on `tests/regression/` with no code change
in this repository to explain it (Pitfall 11 from Phase 7 research). Left silent, that
reads as "the regression fixture broke" when the real cause is upstream and unrelated —
exactly the failure mode the fixture's own
`test_the_fixture_was_captured_on_the_kernel_this_run_uses` test exists to name instead
of hide: it fails one specific test stating both version pairs, rather than dozens of
unexplained topology mismatches. It does not, however, stop CI from going red in the
first place — it only makes the red legible once it happens.

## Next step

Revisit when a fresh `pip install -e '.[dev]'` resolves a `cadquery`/`cadquery-ocp` pair
different from the fixture's `provenance` header (the kernel-version test will name both
pairs the moment this happens). At that point the options are: pin CI to install from
`requirements.txt`'s locked versions before `make verify` (consistent with how the
project already locks deployment dependencies, L12), or add an explicit upper bound in
`pyproject.toml`'s `cadquery` range. Either is a decision against L12's "why floors and
ranges are chosen this way" and needs the human, not an autonomous fix.
