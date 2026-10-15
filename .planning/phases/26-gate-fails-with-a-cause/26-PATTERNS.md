# Phase 26: Gate Fails With a Cause - Pattern Map

**Mapped:** 2026-10-15
**Files analyzed:** 13 new/modified
**Analogs found:** 12 / 13 (all analogs verified git-tracked; no mirror paths)

Nearly every file here is edited in place, so the "analog" is mostly a sibling block inside the same file. Line numbers are against the tree today (equal to `v0.5` outside `.planning/` and `docs/`).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `Makefile` (`test` recipe, 176-177) | config | batch | `Makefile` `test.fast` (201-205) | same-file exact |
| `Makefile` (`test-image` recipe, 217-226) | config | batch | its own `--ignore=tests/test_browser.py` + comment | same-file exact |
| `pyproject.toml` `[tool.pytest.ini_options]` (122-130) | config | n/a | same block (`--strict-config`) | same-file exact |
| `tests/test_hooks.py` (`_make_env`, new env-form tests) | test | request-response (subprocess `make -n`) | `_make_env` / `_dry_run` (34-67) | exact |
| `tests/test_hooks.py` (`test-image` pin, 181-190) | test | request-response | `test_verify_and_verify_fast_share...` (93-128, exact-set pin) | role-match |
| `tests/test_pool.py` (autouse fixture, `del manager`) | test | event-driven | `tests/conftest.py` autouse root-logger fixture | role-match |
| `tests/test_pool.py` (forced-GC subprocess gate test) | test | batch (subprocess) | `tests/test_hooks.py` `subprocess.run(..., env=_make_env())` | partial |
| `tests/test_browser.py` (twin step 1532-1611, `_follow_link` 204) | test | event-driven | same file: `expect_request(... timeout=BUILD_WAIT_MS)` at 272/386/410, `_wait_until_parked` 585 | exact |
| `.github/workflows/ci.yml` (throwaway branch only) | config | n/a | `spike/21-linux-runner` (`a6a4fc5`) | precedent |
| `bench/RESULTS.md` (append `## Gate fails with a cause (Phase 26)`) | record | append-only | 21-08 (5169) and 21-02 (4857) subsections | exact |
| `docs/tech_debt/active/*.md` -> `resolved/` (3 retired, 2 updated) | record | CRUD | `resolved/2026-09-25-test-pool-wedged-worker-flakes-on-the-github-runner.md` | exact |
| `docs/tech_debt/INDEX.md` row moves | record | CRUD | Resolved table rows (line 45+) | exact |
| Acceptance-protocol doc (committed before interleaved runs) | record | n/a | `bench/RESULTS.md` "The rule (25-01)" (5545-5600) | exact |

## Pattern Assignments

### `Makefile` `test` recipe (config, batch)

**Analog:** `Makefile` 176-177 plus `test.fast` 201-205.

Current:
```make
test: $(STAMP) $(BROWSER)  ## run the test suite (a cold first run is page cache, not the tests)
	$(PY) -m pytest -n $(PYTEST_WORKERS) --cov --cov-report=term $(PYTEST_ARGS)
```
Edit: put `-v --durations=25` AFTER `--cov-report=term` and BEFORE `$(PYTEST_ARGS)` (so a caller's `-q` cancels `-v`). `tests/test_hooks.py:114-116` compares only `words[: words.index("-n") + 2]`, so the flag stays outside the pinned prefix. Do NOT touch `test.fast` (202-205). Update the comment above `test` (about lines 156-163) with one sentence giving the reason and measured cost (comments carry the measurement, per CLAUDE.md).

### `Makefile` `test-image` recipe (config, batch)

**Analog:** itself, 217-226.

```make
test-image: image  ## run the test suite inside the image (needs no local python)
	docker run --rm $(PLATFORM_ARG) --user root -e PYTHONPATH=/app/src \
	  -v "$(CURDIR)/src:/app/src:ro" -v "$(CURDIR)/tests:/app/tests:ro" \
	  -v "$(CURDIR)/pyproject.toml:/app/pyproject.toml:ro" \
	  -w /app --entrypoint sh $(IMAGE) \
	  -c "pip install -q --root-user-action=ignore pytest httpx \
	      && python -m pytest -q -p no:cacheprovider \
	      --ignore=tests/test_browser.py $(PYTEST_ARGS)"
```
Copy this shape: add `-v "$(CURDIR)/bench:/app/bench:ro" -v "$(CURDIR)/scripts:/app/scripts:ro"`, `-e PYTHONPATH=/app/src:/app`, and one `--ignore=tests/<f>.py` per host-only file, each with a comment line naming its reason (make / git / Dockerfile / `.github`), as the existing browser comment at 217-218 does. Final ignore list comes only from the first recorded red set (D-11); any red outside the four causes is a stop-and-ask. Note in the comment that `PYTHONPATH=/app` is redundant (`python -m pytest` puts cwd on `sys.path`); the mounts are what fix it.

### `pyproject.toml` (config)

**Analog:** `[tool.pytest.ini_options]` lines 122-130.
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--strict-markers --strict-config"
xfail_strict = true
filterwarnings = [
    "error",
    ...
]
```
Add `faulthandler_timeout = 120` (TOML integer accepted under `--strict-config`, measured). No `filterwarnings` entry. Add a `#` comment with the recorded `--durations` reading that justifies 120. Editing this file retriggers `$(STAMP)` (reinstall), so do the Item 3 20-run loop before this edit.

### `tests/test_hooks.py` hook-pin fix (test, request-response)

**Analog:** `_make_env` / `_MAKE_VARIABLES`, lines 24 and 34-37.
```python
_MAKE_VARIABLES = ("MAKEFLAGS", "MFLAGS", "MAKELEVEL")
def _make_env() -> dict[str, str]:
    return {k: v for k, v in os.environ.items() if k not in _MAKE_VARIABLES}
```
Fix: add `"PYTEST_ARGS"` to the tuple (covers all five make-spawning call sites: `_dry_run` 58-67, the `-W` dry runs at 141-148 and 167-174, hook-stamp tests). Update the docstring/comment with why. New tests need `import pytest` (not yet imported; current imports are os, re, shutil, subprocess, Path at 16-20). Test shape (red first, both caller forms):
```python
def test_the_pin_ignores_the_callers_pytest_args(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYTEST_ARGS", "--ignore=tests/test_browser.py")
    test_verify_and_verify_fast_share_one_static_prefix_and_one_pytest_recipe()
```
Second form additionally sets `MAKEFLAGS=" -- PYTEST_ARGS=..."`, `MAKELEVEL=1`, `MFLAGS=""`. Failing assertion today: line 120 `assert "--ignore=" not in whole_pytest`.

### `tests/test_hooks.py` shared-recipe pin additions and `test-image` pin (test)

**Analog:** exact-set style at lines 122-128:
```python
ignored = {
    w.removeprefix("--ignore=") for w in fast_pytest.split() if w.startswith("--ignore=")
}
assert ignored == {f"tests/{n}.py" for n in HEAVY_TEST_FILES}
```
Copy for `test_the_image_suite_ignores_the_browser_test` (181-190): keep its recipe-rejoin loop (`while lines[end].endswith("\\")`), but rename it to what it now pins, and assert exact sets for the ignored files, the mounted sources (`src`, `tests`, `pyproject.toml`, `bench`, `scripts`, all `:ro`) and `PYTHONPATH=/app/src:/app`. `make -n` prints continuation lines separately, so start the rejoin from the line containing `docker run`. Also add: `-v` and `--durations=` in `whole_pytest`, absent from `fast_pytest`. Tightened, never deleted (D-13).

### `tests/test_pool.py` autouse fixture and `del manager` (test, event-driven)

**Analog:** the manager-thread block at 159-194 (`manager = executor._executor_manager_thread` at 163, last use `assert not manager.is_alive(), ...` at 194); same pattern at 556/581 and 610/638. Imports at 10-30 do not include `gc`; add `import gc`.

Edit C: insert `del manager` on the line after each last use (194, 581, 638). Edit B: module-level
```python
@pytest.fixture(autouse=True)
def _collect_garbage_outside_the_resource_tracker_lock() -> Iterator[None]:
    yield
    gc.collect()
```
with a comment carrying the forced-GC table (arm A 3/3 red, B and C 0/3) and why (cyclic garbage holding a semaphore finalised re-entrantly inside `ResourceTracker._check_alive`). Style reference: the root-logger reset autouse fixture in `tests/conftest.py`. No `src/spur/pool.py` change.

### `tests/test_pool.py` forced-GC gate test (test, batch/subprocess)

**Analog (partial):** `subprocess.run(..., cwd=REPO_ROOT, env=<scrubbed>, capture_output=True, text=True)` from `tests/test_hooks.py:141-148`. Put it in `tests/test_pool.py`, not a new file: `tests/test_hooks.py:25` `HEAVY_TEST_FILES` pins exactly five files out of `verify.fast`, and the subprocess costs about 10 s of the 30 s budget.
Shape: `[sys.executable, "-c", _FORCED_GC, *ids]`, where the script imports `gc`, `pytest`, `multiprocessing.resource_tracker as rt`, wraps `rt.ResourceTracker._check_alive` to call `gc.collect()` and count calls, then `sys.exit(pytest.main(["-p","no:cacheprovider","--no-cov","-n0","-q",*ids]))`. Use `-c`, never a script file (spawn re-runs it in every worker). Env scrubbed of `PYTEST_ADDOPTS` and `PYTEST_ARGS`, cwd = repo root (so `filterwarnings = error` applies). Assert exit 0 and call count > 0. Ids: the three producers plus `tests/test_pool.py::test_a_closed_pool_never_builds_a_replacement_worker`. Seen red with B+C absent, then green.

### `tests/test_browser.py` twin-selectors step (test, event-driven)

**Analog:** same file. Current baseline (1560-1577) waits only for `/api/info`:
```python
with twins_page.expect_request(
    lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
):
    twins_page.goto(server + "/#" + link)
...
requests_before = len(seen)
```
Fix: after the info wait, wait on the STL request (`expect_request(lambda r: "/api/model.stl" in r.url, timeout=BUILD_WAIT_MS)`) before `requests_before = len(seen)`, and `twins_page.wait_for_timeout(<over 350 ms>)` (named constant near `BUILD_WAIT_MS`, `app.js:289` debounce) before the zero-request assertion at 1611. The red proof parks `/api/info`: `info_parked: list[Route] = []` with `twins_page.route("**/api/info*", lambda route: info_parked.append(route))` (lambda, not bound `append`: see comment at 667-668), released with `info_parked[0].continue_()`. Reuse `_wait_until_parked(page, parked)` at 585-593 and the existing `STL_ROUTE` (`tests/browser_session.py:39`). Do not `time.sleep` in a handler. Delaying the STL route does not turn the old step red (measured).

`_follow_link` (204-215), IN-04a: change
```python
with page.expect_request(lambda request: "/api/info" in request.url) as sent:
```
to add `timeout=BUILD_WAIT_MS`, as at 272/386/410. Open question for the planner: the `_wait_until_parked` spin (`page.evaluate("0")` with no pause) is the unassigned second half of IN-04.

### `.github/workflows/ci.yml` (throwaway branch only)

**Analog:** precedent branch `spike/21-linux-runner` (`a6a4fc5`, draft PR #32, `spike(21): ... -- DO NOT MERGE`). Branch `git switch -c spike/26-ubuntu-26 v0.5`; one commit, three `runs-on: ubuntu-latest` lines (13, 61, 77) to `ubuntu-26.04`. No matrix (renames the required check). Executor stops before push; the human pushes and runs `gh pr create --draft`. Never lands on the phase branch.

### `bench/RESULTS.md` (record, append-only)

**Analog:** `### The Linux path on the real runner (21-08)` (5169) and `### Linux runner spike (21-02)` (4857). Append a new top-level `## Gate fails with a cause (Phase 26)` after Phase 25's section (5545 onward) and never rewrite earlier readings. Per-measurement subsection format:
- Intro line with who ran what and the log path under `.planning/phases/26-.../investigation/`.
- Run table: `| Run | Conclusion | Classification |`.
- `#### Host state` bullets: `Image` and version from `Set up job`, kernel, `nproc`, python/pytest/xdist/cov/playwright versions, read date, "load is not observable, every wall figure is one sample".
- `#### Readings` table: `| Reading | Value |` (job wall time, result line, coverage TOTAL, install seconds).
- A closing "What the log does and does not show" paragraph.
Sections needed: hook-pin red/green, Ubuntu 26 per-job classification, twin-step old-red/new-green plus 20-run count, forced-GC table plus 10+10 acceptance, `--durations` reading, throwaway stall log excerpt, 3+3 gate cost, `test-image` red set table with each red classified against make/git/Dockerfile/`.github`.

### Acceptance-protocol doc (record, committed before runs)

**Analog:** `bench/RESULTS.md` `### The rule (25-01)` (5555-5600): "committed alone, before any reading ... nothing in it changes once the first wait has started"; numbered items for host, what is measured, arms, cap, stop rule. Copy that structure for D-04 (10+10 interleaved A1 B1 ... A10 B10), D-05 (20 runs) and D-09 (3+3, stop and ask above 5 %). Include: `--cov --cov-fail-under=0` (else the coverage-floor line is counted wrongly), signature rule (a red counts as the flake only if the log holds `ReentrantCallError` or `ResourceTracker called reentrantly`), effective `-n`. Commit it as its own commit so `git log` orders it before every reading.

### Debt retirement (record, CRUD)

**Analog:** `docs/tech_debt/resolved/2026-09-25-test-pool-wedged-worker-flakes-on-the-github-runner.md`. Header fields: `Severity:`, `Status: resolved`, `Date:`, `Resolved in: <sha>`, `Source:`, `Related files:`; body `## Context`, `## Why it matters`, `## Next step` (what was done, quote the evidence). Procedure (footer comment of that file, and CLAUDE.md): set Status resolved, add sha, `git mv docs/tech_debt/active/<f> docs/tech_debt/resolved/<f>`, move the INDEX row from the Active table (rows 19-35) to the Resolved table (line 43+) with format:
```
| [Title](resolved/<file>.md) | `<sha>` -- see the file's own `Resolved in:` field |
```
All in the same commit as the fix. Retire: hook-pin (`2026-10-10-hook-pin-reads-the-callers-pytest-args.md`), twin-selectors (`2026-10-15-twin-selectors-step-reds-main.md`), test-image (`2026-10-10-test-image-collects-tests-that-read-host-files.md`), and resource-tracker (`2026-10-06-resource-tracker-flake-fails-the-gate.md`) only if D-03 reproduces; quote the forced-GC table and say "located and fixed from a reproduction". The sha problem: an item cannot hold its own commit's sha, so follow the repo's existing convention (see active item `2026-10-05-resolved-in-shas-point-at-squashed-branch-commits.md`). Hang item (`...make-verify-hung-at-98-percent...`) stays active with a runbook and refreshed `Makefile:170` to `177`; Ubuntu 26 item stays active.

## Shared Patterns

### Red first, then green, with the output recorded
**Source:** `.planning/research` and CONTEXT D-02; precedent in 21-08. **Apply to:** every code item. Write the test, run it against the unfixed tree, keep the failing output, apply the fix, rerun; record both in the commit or `bench/RESULTS.md`.

### Make-spawning tests scrub the environment
**Source:** `tests/test_hooks.py:34-47` (`_make_env`, `_clean_git_env`). **Apply to:** hook tests and the forced-GC subprocess (also scrub `PYTEST_ADDOPTS`/`PYTEST_ARGS`).

### Exact-set pins, not membership
**Source:** `tests/test_hooks.py:122-128`. **Apply to:** the `test-image` pin extension.

### Playwright waits are on the request, bounded by BUILD_WAIT_MS
**Source:** `tests/test_browser.py:272, 386, 410, 1568-1570`. **Apply to:** twin step, `_follow_link`.

### Comments carry the measurement
**Source:** CLAUDE.md and the comment blocks at `tests/test_pool.py:154-189`. **Apply to:** every new fixture, flag and ini key.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| Parked-route proof of a delayed `/api/info` response | test | event-driven | Closest is `_wait_until_parked` / the STL parked-route pattern at `tests/test_browser.py:585-593, 667-668`, but nothing parks `/api/info` yet; extend that pattern |

(The forced-GC `python -c` subprocess test also has only a partial analog; use RESEARCH Pattern 3.)

## Metadata

**Analog search scope:** `Makefile`, `pyproject.toml`, `tests/`, `bench/RESULTS.md`, `docs/tech_debt/{active,resolved,INDEX.md}`, `.github/workflows/ci.yml`
**Files scanned:** about 12 read or sampled; tracked status confirmed for `bench/RESULTS.md`, `.github/workflows/ci.yml`
**Pattern extraction date:** 2026-10-15
