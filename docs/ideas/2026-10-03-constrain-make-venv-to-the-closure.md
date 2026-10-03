# Constrain `make venv` to the pinned closure, the way CI is

Date: 2026-10-03
Source: Phase 15 discuss-phase (15-CONTEXT.md D-14)
Related files:
- Makefile (`$(STAMP)`: `pip install -e '.[dev]'`)
- requirements.txt (the 31-package closure, resolved on linux/amd64)
- tests/regression/test_pre_v0_2.py (`test_the_fixture_was_captured_on_the_kernel_this_run_uses`)
- docs/architecture/decision_log.md (L12; L34 once Phase 15 lands)

## Context

Phase 15 makes CI's `test` job install under `-c requirements.txt`, so CI resolves the
exact `cadquery` / `cadquery-ocp` pair the regression fixture's provenance header names.
A developer's `make venv` still resolves `pyproject.toml`'s loose ranges. The two can
diverge; when they do, the fixture's kernel-version tripwire fails locally with "recreate
the venv to match" and nothing says how.

## Why it matters

One install path for every environment that claims to run the gate: a fresh clone gets
the kernel the fixture was captured on without reading a test's failure message first.
It also makes `requirements.txt` the single statement of "what spur is tested against",
which is what L12's closure already is for the image.

## Next step

Revisit when a fresh `make venv VENV=.venv-proof` on macOS arm64 under
`PIP_CONSTRAINT=requirements.txt` (or `-c`) installs cleanly and passes `make verify` —
the closure was resolved for linux/amd64 and the 31 pins' arm64 wheel availability is
unproven (vtk, casadi, nlopt are the likely gaps). If it does: `$(STAMP)` gains the
constraint and `requirements.txt` as a prerequisite, and L34's sentence about CI widens
to every environment, as an amendment. If it does not: record which pins have no arm64
wheel and leave this filed.
