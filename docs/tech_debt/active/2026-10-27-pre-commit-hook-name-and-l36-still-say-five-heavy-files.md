# The pre-commit hook's name and L36's amendment still say "five heavy files"

Severity: nice
Status: active
Date: 2026-10-27
Source: 32-03 Task 2 (tests/test_shaft_model.py named heavy after `make verify.fast` read 20.97 s)
Related files:
- .pre-commit-config.yaml:24
- docs/architecture/decision_log.md (L36, and the 21-06 amendment that counts "five")

## Context
`tests/test_shaft_model.py` is the sixth file `make test.fast` excludes. The Makefile's help
line, recipe comment and `test.fast` description were updated to "six"; the display name of
the `verify-fast` hook in `.pre-commit-config.yaml` still says "every test file but the five
heavy ones", and L36's text and its 21-06 amendment still count five (the amendment is a dated
record, so the fix is a new amendment line, not an edit). `.pre-commit-config.yaml` was left
alone because the Makefile's `$(HOOKS)` stamp depends on it: touching it mid-commit makes the
next `make` run `pre-commit install` from inside a running hook.

## Why it matters
Only wording: the hook still excludes exactly what `HEAVY_TEST_FILES` pins. A reader counting
the files from the hook name finds six `--ignore` flags against "five".

## Next step
Change "five" to "six" in the hook name in a commit of its own (outside a hook run), and add
the sixth file to L36 with the next L36 amendment. Revisit when `.pre-commit-config.yaml` is next
edited.
