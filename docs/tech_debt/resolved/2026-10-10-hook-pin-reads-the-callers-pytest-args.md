# The shared-recipe hook pin reads the caller's `PYTEST_ARGS`, so `make verify PYTEST_ARGS="--ignore=..."` fails it

Severity: nice
Status: resolved
Date: 2026-10-10
Resolved in: test(26): the hook pins read the Makefile, not the caller's PYTEST_ARGS
Source: 21-07, A/B arm A's first attempt (`.planning/phases/21-browser-test-of-the-viewer/investigation/21-07-A-1.log`)
Related files:
- `tests/test_hooks.py:36` (`_make_env`), `tests/test_hooks.py:63` (`_dry_run`), `tests/test_hooks.py:125` (`assert "--ignore=" not in whole_pytest`)
- `Makefile:6` (`PYTEST_ARGS ?=`), `Makefile:177` (the `test` recipe)

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

## Resolution (2026-10-15)

`_MAKE_VARIABLES` in `tests/test_hooks.py` gained `"PYTEST_ARGS"`, so `_make_env()` drops a caller's flags with make's own
and every `make` the hook tests start reads the Makefile's recipe. Two tests pin it, each seen red against the unfixed
`_make_env()` first (`2 failed, 7 deselected`):
`test_the_pin_ignores_pytest_args_set_in_the_environment` and
`test_the_pin_ignores_pytest_args_handed_down_from_the_make_command_line`. `Makefile` is unchanged.

| Form | Before | After |
|---|---|---|
| environment (`PYTEST_ARGS=--ignore=tests/test_browser.py pytest <pin>`) | `1 failed` | `1 passed` |
| make command line (`make test PYTEST_ARGS="--ignore=tests/test_browser.py tests/test_hooks.py ..."`) | `1 failed, 6 passed`, `Error 1` | `9 passed` |
| empty (`PYTEST_ARGS=`) | `1 passed` | `1 passed` |

The reading and the whole logs: `bench/RESULTS.md`, "The hook pin and the caller's PYTEST_ARGS (26-01)".
