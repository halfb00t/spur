"""The loader for the DIN 5480 table values, which are private and gitignored.

Phase 34 fills this file. The table values are kept private and gitignored, so they never
enter the repository; this module will read them from a local file and report plainly
when it is absent, instead of falling back to a number that merely looks right (L08).

The file exists before its code because the import-linter contracts in pyproject.toml
name it, and import-linter refuses a contract whose source module does not exist; with
the file in place the walls are in force before any shaft code (D-12, L46). Until Phase 34
it holds this docstring and nothing else.
"""
