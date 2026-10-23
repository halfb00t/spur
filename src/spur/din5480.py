"""The DIN 5480 formulas, each cited by the clause it implements.

Phase 31 fills this file. It is pure arithmetic like shaft_calc.py, so it stays free of
the CAD kernel, the solid, the logger and the gear maths. A formula whose clause cannot be
cited does not go in: a number printed here is a number someone will cut metal to (L08).

The file exists before its code because the import-linter contracts in pyproject.toml
name it, and import-linter refuses a contract whose source module does not exist; with
the file in place the walls are in force before any shaft code (D-12, L46). Until Phase 31
it holds this docstring and nothing else.
"""
