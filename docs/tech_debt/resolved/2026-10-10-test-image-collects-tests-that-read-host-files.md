# `make test-image` collects test files that read files the image does not hold

Severity: nice
Status: resolved
Resolved in: fix(26): make test-image mounts what its tests read and ignores only host-only files by name
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

## Resolution
2026-10-15 (Phase 26, 26-06). The ASSUMPTION above is now measured. `make test-image` on the unfixed recipe stopped at 5
collection errors (`bench` and `scripts` not importable); with the mounts applied by hand it read **29 failed, 1290 passed
in 863.84s**: 14 `make`, 11 `.github`, 2 `git`, 1 Dockerfile, and one test (`test_pool.py` forced-GC) that needs
pytest-cov and pytest-xdist in the image. The fix mounts `bench/` and `scripts/` read-only, sets `PYTHONPATH=/app/src:/app`,
installs the two plugins (a human-approved deviation from D-11's literal text) and ignores six files by name with a
reason each. After: `make test-image` exit 0, `1201 passed in 888.34s`, no collection error, no skip. Record:
`bench/RESULTS.md` "make test-image (26-06)". Whole-file ignores drop 47 passing tests in `tests/test_pr_land.py` and 41
in `tests/test_bench.py`; `make verify` still runs them. Nothing runs `make test-image` in CI
(`docs/ideas/2026-10-15-run-make-test-image-in-ci.md`).

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
