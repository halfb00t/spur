# CI resolves the kernel from an unpinned range; the fixture pins one kernel exactly

Severity: must
Status: resolved
Date: 2026-09-26
Resolved in: 839dfea -- proven by CI run https://github.com/halfb00t/spur/actions/runs/37181871926
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

## Resolution (2026-10-04)

Mechanism (15-CONTEXT.md D-13): `requirements.txt`, the L12 closure the image installs, is
now a pip constraints file for CI. The `make verify PYTHON=python` step of the `test` job
carries `env: PIP_CONSTRAINT: requirements.txt`, so the pip self-upgrade and the
`pip install -e '.[dev]'` that `$(STAMP)` runs inside `make verify` both resolve under its 31
exact pins, `cadquery 2.8.0` and `cadquery-ocp 7.9.3.1.1` among them; the dev extras and the
packages `docker/refresh-requirements.sh` prunes stay free. Neither option this file first
named was taken: installing `requirements.txt` before the dev extras would pull the pruned
~550 MB of cadquery's transitive dependencies back in with the second install, and an upper
bound in `pyproject.toml` pins every environment yet leaves `cadquery-ocp` held only by
cadquery 2.8.0's own `<8.0,>=7.9.3.1` cap, so a 7.9.x patch would still move under the
fixture. L34 logs the choice against L12's "why floors and ranges" rationale.

Where the pin is written down (D-15): the comment above the step in `.github/workflows/ci.yml`
and the docstring of `test_the_fixture_was_captured_on_the_kernel_this_run_uses`, which names
`requirements.txt` as the pin, `docker/refresh-requirements.sh` as what moves it and
`make fixture.regen` as the fixture's own move. `tests/regression/pre_v0_2.json` is untouched.

Proof: the `ci(15-05)` commit `839dfea`, run 37181871926 on the draft phase PR #18 (success).
The new step `kernel pair this run resolved` printed `cadquery 2.8.0 cadquery-ocp 7.9.3.1.1`
and pytest read `927 passed in 203.16s (0:03:23)`, the tripwire among them. Locally, a dry run
under the constraint resolved the same pair, and a scratch constraint file with
`cadquery-ocp==8.0.1.0.0` made pip fail with `ResolutionImpossible`, so the constraint fails
closed instead of resolving another kernel quietly. See `bench/RESULTS.md`, `### CI run`.

One correction to D-16's premise: pip's install output is not "absent on a cache hit" in this
workflow. setup-python's pip cache restores downloads, not the venv, so the `Successfully
installed` line names the pair even on a hit (run 37116412012 hit the cache and printed it;
so did run 37181871926). The print step stands as the cheaper-to-read proof, not the only one
(D-16 addendum, 15-RESEARCH Pitfall 14).

Not done here: a local `make venv` stays unconstrained. The closure's macOS arm64 wheel
availability is unproven, so that path is filed as
`docs/ideas/2026-10-03-constrain-make-venv-to-the-closure.md` (D-14), and the tripwire test
remains the local remedy: it names a mismatched venv.
