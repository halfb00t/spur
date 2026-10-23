"""The pure shaft maths behind the numbers the tool prints for a shaft.

Phase 31 fills this file. It copies calc.py's patterns (one function per quantity, a
value that cannot be computed honestly comes back as a warning and no number, L08) and
never imports from calc.py: gear and shaft numbers stay uncoupled, the way
`_involute_angle` was copied rather than shared.

Like calc.py it runs on every keystroke, so it must stay free of the CAD kernel, the
solid and the logger. The file exists before its code because the import-linter contracts
in pyproject.toml name it, and import-linter refuses a contract whose source module does
not exist; with the file in place the walls are in force before any shaft code (D-12,
L46). Until Phase 31 it holds this docstring and nothing else.
"""
