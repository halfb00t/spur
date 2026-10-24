"""The shaft's one parameter model: `ShaftParams`, validated once at its boundary.

Phase 31 fills this file under L46. Its field names and defaults are frozen by a test
there, and may still change by a logged decision until Phase 33 publishes the first shaft
link; from then on L05 applies to them in full, as it does to the gear's.

The file exists before its code because the import-linter contracts in pyproject.toml name
it. import-linter refuses a contract whose source module does not exist, so the walls
that keep the shaft maths away from the CAD kernel, the solid, the logger and the gear
maths could not go in force first without it (D-12, 30-RESEARCH Resolved Unknown 1).
Until Phase 31 it holds this docstring and nothing else.
"""
