# `make test-image` collects test files that read files the image does not hold

Severity: nice
Status: active
Date: 2026-10-10
Source: Phase 21, 21-06 -- adding `tests/test_browser_pins.py` (reads `Dockerfile`) and excluding the browser test from `test-image`
Related files:
- `Makefile` -- `test-image` (mounts only `src/`, `tests/` and `pyproject.toml`)
- `tests/test_browser_pins.py` -- `test_playwright_is_pinned_exactly_in_dev_and_never_in_the_runtime_closure` reads `Dockerfile`
- `tests/test_hooks.py` -- reads `Makefile` and `.pre-commit-config.yaml` and runs `make`

## Context
`make test-image` runs the whole `tests/` directory inside the image, which holds `requirements.txt`, `docker/`,
`pyproject.toml` and `src/`, but no `Dockerfile`, `Makefile` or `.pre-commit-config.yaml`, and the slim base has no `make`.
`tests/test_hooks.py` therefore cannot pass there, and 21-06's pins module now cannot either (it reads the `Dockerfile`).
ASSUMPTION: the image suite is already red on `test_hooks.py` today; Docker was not running when this was written, so it
was not run. CI's `image` job runs the smoke test, not `test-image`, so nothing in the gate would notice.

## Why it matters
`test-image` is documented as a way to run the suite without a local Python (`docs/HOW_TO_DEVELOP.md`). If it is red
for host-file reasons, a person using it cannot tell those failures from real ones.

## Next step
Revisit when `make test-image` is next run for real: read its result, then either mount the files those tests read or
exclude them by name, the way 21-06 excluded `tests/test_browser.py`.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
