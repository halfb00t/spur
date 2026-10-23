"""The shaft solid: the only shaft module allowed to touch the CAD kernel.

Phase 32 fills this file. Like model.py for the gear it is the one doorway to cadquery and
OCP for the shaft, and it is reached only through model, never imported by app, cli, pool,
records or parts, so the serving process stays free of OpenCascade (L17).

The file exists before its code because the import-linter contracts in pyproject.toml
name it, and a mistyped name there would be silently accepted, so tests/test_seam.py pins
that the file is present. The walls are in force before any shaft code (D-12, L46). Until
Phase 32 it holds this docstring and nothing else.
"""
