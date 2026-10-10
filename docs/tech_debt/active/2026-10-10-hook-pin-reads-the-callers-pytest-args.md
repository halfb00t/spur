# The shared-recipe hook pin reads the caller's `PYTEST_ARGS`, so `make verify PYTEST_ARGS="--ignore=..."` fails it

Severity: nice
Status: active
Date: 2026-10-10
Source: 21-07, A/B arm A's first attempt (`.planning/phases/21-browser-test-of-the-viewer/investigation/21-07-A-1.log`)
Related files:
- `tests/test_hooks.py:34` (`_make_env`), `tests/test_hooks.py:58` (`_dry_run`), `tests/test_hooks.py:90` (`assert "--ignore=" not in whole_pytest`)
- `Makefile:6` (`PYTEST_ARGS ?=`), `Makefile:170` (the `test` recipe)

## Context
`test_verify_and_verify_fast_share_one_static_prefix_and_one_pytest_recipe` runs `make -n verify` and
`make -n verify.fast` and compares the pytest lines. `_make_env()` strips make's own flags and jobserver from the child's
environment, but not `PYTEST_ARGS`. make exports a command-line variable to the recipe's environment, so under
`make verify PYTEST_ARGS="--ignore=tests/test_browser.py"` the pin's own dry run takes it through `PYTEST_ARGS ?=` and reads
`--ignore=` in the whole gate's recipe: `1 failed, 1224 passed in 164.55s`. Read on the working tree, a plain environment
variable (`PYTEST_ARGS=--ignore=tests/test_browser.py pytest tests/test_hooks.py::<that test>`) fails it the same way.
`PYTEST_ADDOPTS` does not reach the dry run, which is how 21-07 ran arm A.

## Why it matters
Anyone narrowing the gate with `PYTEST_ARGS="--ignore=..."` gets a red run that has nothing to do with their change, and a
gate that goes red for no code reason teaches people to retry. It cost 21-07 one 165 s run.

## Next step
Drop `PYTEST_ARGS` from `_make_env()`'s result (or pass `PYTEST_ARGS=` on the dry run's command line), and add a case that
runs the pin with the variable set. Revisit when `tests/test_hooks.py` is next touched or the next time a narrowed
`make verify` is wanted.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
