# Phase 17: Debt First — Commit Gate and Pool Race - Pattern Map

**Mapped:** 2026-10-06
**Files analyzed:** 20 (no RESEARCH.md; list from CONTEXT.md, ROADMAP, REQUIREMENTS)
**Analogs found:** 20 / 20 (all tracked; every path below verified in `git ls-files` or read from the tracked tree)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match |
|---|---|---|---|---|
| `src/spur/pool.py` (`_run_with_timeout`, `recreate_for`, `shutdown`) | service | request-response + event-driven (executor lifecycle) | itself: `recreate_for` identity guard (99-155) | exact (in-file) |
| `tests/test_pool.py` (2 new tests) | test | request-response | `test_two_same_slot_deaths_from_one_incident_replace_the_worker_once` (492), `test_a_wedged_build_is_terminated_and_its_worker_replaced` (139) | exact |
| `bench/latency.py` (`_SCENARIOS`, `_fetch`, new scenario) | utility (bench) | request-response, concurrent | `scenario_composed` / `run_composed` (219) + `_fetch` (181) | exact |
| `tests/test_bench.py` | test | transform | registry assertion (604), `_fetch` MockTransport test (~614) | exact |
| `bench/RESULTS.md` | doc | batch | section "Composed worst row under ten concurrent builds (Phase 13)" (line 472) with its "### Host state" | exact |
| `Makefile` (`verify.static`, `verify.fast`, `test.fast`, hook stamp) | config | batch | `verify` (50), `test` (111-112), `$(STAMP)` (33-42) | exact |
| `.pre-commit-config.yaml` | config | event-driven (git hooks) | itself (`verify`, `no-skip-token` stage pinning) | exact |
| `docs/HOW_TO_DEVELOP.md` (§0 ~18-28, §6 ~115-128) | doc | n/a | itself | exact |
| `README.md` (:71, :92-95, :284-290) | doc | n/a | itself | exact |
| `docs/architecture/packaging.md` (:47-52) | doc | n/a | itself | exact |
| `.github/workflows/ci.yml` (comment 24-38) | config | n/a | itself | exact |
| `scripts/pr_land.py` (:61-67 comment) | utility | n/a | itself (comment only) | exact |
| `docs/architecture/decision_log.md` (2 new `Lxx`, amend L13/L34) | doc | n/a | L34 (1635), L35 (1778): "(amends Lxx)", "Date:", measured-number paragraphs, dated "**Amendment (...)**" | exact |
| `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-...md` | doc | n/a | `docs/tech_debt/TEMPLATE.md` + resolved-file convention | exact |
| `docs/tech_debt/active/2026-10-02-same-slot-...md` | doc | n/a | same | exact |
| `docs/tech_debt/INDEX.md` | doc | n/a | its own Active table rows | exact |
| `docs/tech_debt/resolved/` (git mv targets, tip-chamfer dated note) | doc | n/a | `resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md:63` | exact |
| optional hook-drift test (e.g. `tests/test_hooks.py`) | test | transform | `tests/test_no_fake_done.py` (reads a copy of the Makefile text) | role-match (not read in full; planner reads it) |
| `docs/tech_debt/active/2026-10-04-...coverage-flush...md`, `...resource-tracker-flake...md` | doc (read only) | n/a | read and record outcome | n/a |

## Pattern Assignments

### `src/spur/pool.py` (service, request-response)

**Analog:** the file's own identity guard, `recreate_for` (lines 123-125, 151-155).

**Existing guard to mirror** (lines 123-125):
```python
i = hash(p) % self.workers
if self._executors[i] is not executor:
    return  # someone else already replaced this slot for this incident
```

**Site to change** (lines 204-206, the `except TimeoutError` branch). Today it reads `executor._processes.values()` unconditionally. After a same-slot sibling already replaced the slot, `shutdown(wait=False)` has set `_processes = None`, so the second caller hits `AttributeError`, which has no handler in `app.py` and surfaces as a raw 500.
```python
for proc in executor._processes.values():
    proc.terminate()
self.recreate_for(p, executor, "timeout")
raise BuildTimeout(...) from None
```
Fix shape (D, locked in CONTEXT): wrap terminate-and-replace in `if self.executor_for(p) is executor and executor._processes is not None:`. No `await` inside. The `raise BuildTimeout(...) from None` stays outside the `if`, so a second same-slot timeout still gives the documented 503 timeout. Keep the comment style: carry the measurement or constraint that forced the choice (see the 185-203 comment block).

**`_closed` flag**: add `self._closed = False` in `__init__` (after line 94) and `self._closed = True` as the first statement of `shutdown()` (lines 224-226). `recreate_for` returns early when `_closed`, placed beside the identity guard (line 124). Without it `shutdown()` then a late timeout creates a fresh executor nobody shuts down.

**Constraint:** `pool.py` has no static path to cadquery (import-boundary contract). Add nothing that imports it.

---

### `tests/test_pool.py` (test, request-response)

**Analog 1 (deterministic stale-executor test):** `test_a_wedged_build_is_terminated_and_its_worker_replaced` (139-200). Pattern: `with TestClient(app):` then `pool = app.state.pool`, an injected short `pool.timeout = 0.2` restored in `finally`, `asyncio.run(pool._run_with_timeout(params, _sleep_past_timeout, 5.0))` inside `pytest.raises(BuildTimeout)`, then `manager.join(timeout=5)` and an `exitcode == -signal.SIGTERM` check. Reuse the helpers at top: `_sleep_past_timeout(seconds)` (31), `_die()` (42), `_event_records` (53), `_field` (62). Imports to reuse (lines 12-28): `asyncio, logging, os, signal, threading, pytest, TestClient, app, BuildTimeout, GearParams`.

For the stale case, call `pool.recreate_for(params, executor, "timeout")` first so `pool.executor_for(params) is not executor` and `executor._processes is None`, then drive `_run_with_timeout` against the stale executor and assert `BuildTimeout`, not `AttributeError`. Seen red before the fix.

**Analog 2 (same-tick sibling):** `test_two_same_slot_deaths_from_one_incident_replace_the_worker_once` (492-527):
```python
async def _drive() -> list[object]:
    first = asyncio.create_task(pool._run_with_timeout(params, _die))
    second = asyncio.create_task(pool._run_with_timeout(params, _die))
    return cast(list[object],
                await asyncio.gather(first, second, return_exceptions=True))
first_result, second_result = asyncio.run(_drive())
```
Adapt with `_sleep_past_timeout` and a short `pool.timeout`. Accept `BuildTimeout` or `BrokenProcessPool` for the sibling. Assert `pool.replaced == replaced_before + 1` and `len(_event_records(caplog, "worker.replaced")) == 1`. Use `caplog.set_level(logging.INFO)`.

**Unchanged:** `test_four_same_slot_requests_all_refuse_without_cancellation` (400, 0.5 s gap) and `test_executor_processes_attribute_still_exists` (112; the `_processes` tripwire). `filterwarnings = ["error"]` is on: shut down any executor the test creates (see 132-136).

Run the new tests repeatedly under `-n 8 --cov` and `-n 4` (`make test PYTEST_ARGS="tests/test_pool.py -q"`; note a subset needs `--no-cov` per the Makefile comment at 90-97).

---

### `bench/latency.py` (utility, request-response, concurrent)

**Analog:** `run_composed` (219-262) and `_fetch` (181-206); registry at 321-332.

**Registry** (321-332): add the new scenario to `_SCENARIOS` only, never to `DEFAULT_SCENARIOS = ("concurrent", "single")`. `main()` reads `DEFAULT_SCENARIOS` (line 401), so the no-argument run is unaffected.

**`_fetch` keyword** (181-206): add `record_500: bool = False`. Default behaviour must stay (`response.raise_for_status()` raising on a 500) because `tests/test_bench.py` pins `HTTPStatusError` for case "500". With `record_500=True`, a 500 becomes `status = "500"` instead of raising. The existing branch shape:
```python
if response.status_code == 503:
    ...
    status = f"503 {reason}"
else:
    response.raise_for_status()
    status = "200"
```
**Reuse `run_composed`**: it calls `_composed_rows()` itself (line ~230). Give it `rows` and a label parameter (default behaviour unchanged), then the new scenario passes `[worst_row] * 10` and `record_500=True`. Keep its fresh-server guards (`held`, `_pool_state`, 10 s deadline loop) because they refuse a non-fresh server. Note a caveat: ten identical rows are one cache key, so verify admission and slot behaviour still read correctly (the "worst row served without holding a slot" error).

`_report_markdown` suppresses the baseline line only for `name == "composed"`; extend that condition to the new name (test at `tests/test_bench.py` ~"omits the single/concurrent baseline line").

---

### `tests/test_bench.py` (test)

**Registry assertion to update deliberately** (line ~604, in `test_the_no_argument_latency_run_is_still_concurrent_then_single`):
```python
assert DEFAULT_SCENARIOS == ("concurrent", "single")
assert set(_SCENARIOS) == {"concurrent", "single", "composed"}
```
**`_fetch` test pattern** (`test_a_503_is_recorded_by_the_reason_the_server_gave`, ~614-640): `httpx.MockTransport` handler keyed on `request.url.params["case"]`; the default path still `pytest.raises(httpx.HTTPStatusError)` on a 500. Add a sibling test asserting `_fetch(..., record_500=True)` returns `status == "500"`. No network.

Docstrings carry the D-number and measurement that forced the assertion; match that.

---

### `bench/RESULTS.md` (doc)

**Analog:** section at line 472, "### Composed worst row under ten concurrent builds (Phase 13)", and the "### Host state" blocks (e.g. 1134, 2211): machine, Python, kernel, HEAD, sweep file, date/time, 1-min load. Append the before tables (up to three attempts, each hit or miss, D-15), then the after-fix table with zero 500s, then the dated margin note (D-12) near "### `SPUR_BUILD_TIMEOUT`" (599). Label the margin number "at this load" beside SC3's 29.42 s / 30 004 ms.

---

### `Makefile` (config, batch)

**Analog:** `verify` (line 50), `test` (111-112), `$(STAMP)` (33-42), `.PHONY` (23-26), help regexp (`^[a-z][a-z.-]*:.*##`, so dotted names like `verify.fast` list in `make`).

Current:
```make
verify: lint typecheck lint-imports no-fake-done test  ## the gate: ...
test: $(STAMP)
	$(PY) -m pytest -n $(PYTEST_WORKERS) --cov --cov-report=term $(PYTEST_ARGS)
```
Target shape (D-03):
```make
verify.static: lint typecheck lint-imports no-fake-done
verify: verify.static test
verify.fast: verify.static test.fast
test.fast: $(STAMP)
	$(PY) -m pytest -n $(PYTEST_WORKERS) --no-cov \
	  --ignore=tests/test_model.py --ignore=tests/test_pool.py \
	  --ignore=tests/test_api.py --ignore=tests/test_cli.py $(PYTEST_ARGS)
```
Add the new names to `.PHONY`. Check `pyproject.toml` `addopts` for whether `--cov` is configured there (the existing `test` recipe passes `--cov` explicitly, which suggests it is not). Make-order caveat: `verify: verify.static test` runs in listed order under plain `make`; `make -j` would reorder, which the existing line already tolerates.

**Hook stamp (D-06, discretion):** model on `$(STAMP)`, which touches a file:
```make
HOOKS := $(VENV)/.hooks-installed
$(HOOKS): .pre-commit-config.yaml $(STAMP)
	$(VENV)/bin/pre-commit install
	@touch $@
```
and make `verify.static` depend on it, plus `venv`. `pre-commit` is a dev extra (installed via `.[dev]`). Comments must carry the measurement (63.555 s warm; 11 s slice) in the style of the PYTEST_WORKERS comment (99-109).

---

### `.pre-commit-config.yaml` (config, event-driven)

**Analog:** the file itself. Keep the one-stage-per-hook rule and its explanatory comment (28-31).

Changes: line 18 becomes `default_install_hook_types: [pre-commit, commit-msg, pre-push]`; `verify` (22-32) keeps `entry: make verify`, `stages: [pre-push]`; add a sibling hook:
```yaml
- id: verify-fast
  name: make verify.fast (static checks + the sub-30 s pytest slice)
  entry: make verify.fast
  language: system
  pass_filenames: false
  always_run: true
  stages: [pre-commit]
```
`no-skip-token` (33-43) is untouched. Rewrite header lines 1-17 (install note at line 5 becomes "run `make venv` once"; 15-17 re-install note). Hook entries must match the Makefile target names; a drift test is recommended.

---

### Doc sites (all edited in the hook `Lxx` commit)

| Site | Current text to correct |
|---|---|
| `.pre-commit-config.yaml` 1-17 header | "same command ... three places"; "Install once per clone: pre-commit install" |
| `docs/HOW_TO_DEVELOP.md` 20-24 (§0) | "The same `make verify` runs in the pre-commit hook, in CI ... and inside `make worktree.land`" |
| `docs/HOW_TO_DEVELOP.md` ~115-128 (§6) | add the D-07 killed-commit rule and D-09 "run `make verify` before every push" |
| `README.md` 286-289 | "The same command runs in the pre-commit hook, in CI ..." |
| `README.md` 71 and 92-95 | `SPUR_BUILD_TIMEOUT` row and the `503` paragraph: add the one-sentence limit (D-12) |
| `docs/architecture/packaging.md` 49-51 | "the pre-commit hook (`.pre-commit-config.yaml`), CI ..., and `make worktree.land`" |
| `.github/workflows/ci.yml` 24-26 | "The same gate a developer runs locally ... enforced in three places" (comment only) |
| `scripts/pr_land.py` 64-67 | comment "~42 s pre-commit hook" is stale; comment-only edit |
| `docs/architecture/decision_log.md` | append, never contradict: see below |

Keep the three-place wording true: the same `make verify` still runs in three places (pre-push, CI, `worktree.land`) and commit stage runs a named prefix of it.

---

### `docs/architecture/decision_log.md` (two new entries, L36 hook then L37 margin)

**Analog:** L34 (line 1635) and L35 (1778). Format:
```
## L34 — <title> (amends L12 and L13)

Date: 2026-10-04.

L12 and L13 stay as written; this entry amends ... with what Phase 15 measured ...

**The measured gate** (D-01 to D-08). ...

**Amendment (2026-10-06, 15-REVIEW WR-01 and IN-03).** ...
```
L36 must quote: the re-priced subset time with its host load figure and date (D-02), the orphan measurement (git 2.54.0, Node `spawnSync`, parent PID 1), the scratch-repo pre-push result (D-05), the upstream issue URL and date (D-08), which commits can now be red and that `main` cannot receive one (L22). Amends L13 and L34's closing sentence. L37 quotes the row's full parameter line, 29.42 s alone, 30 004 ms under SC3, the identical-row figure with its load, and the revisit trigger (D-13). Cite the symbol `COMMIT_TIMEOUT_MS`, not a line number.

---

### Debt files and INDEX (doc)

**Analog:** `docs/tech_debt/TEMPLATE.md` fields (Severity, Status, Date, Source, Related files, Context) plus the resolved convention in CLAUDE.md: `Status: resolved`, `Resolved in: <sha>`, `git mv` into `resolved/`, move the INDEX row, all in the fixing commit. The commit-timeout file retires in the hook commit; the race file only in the commit closing both race and margin. Active-file header carries a stale `commands.cjs:3655` line reference; cite `COMMIT_TIMEOUT_MS` when editing. INDEX row format (Active table): `| severity | [title](active/file.md) | trigger |`; the resolved table is further down in the same file (planner reads it for the exact column set).

The two `nice` debts (`2026-10-04-worker-coverage-flush-is-sometimes-lost.md`, `2026-10-06-resource-tracker-flake-fails-the-gate.md`) are read-only tasks: record the outcome in the plan SUMMARY.

## Shared Patterns

### Comments carry the measurement
**Source:** `Makefile` 90-109 (PYTEST_WORKERS), `src/spur/pool.py` 126-150.
Every new knob or guard cites the run that set it; dated, with host load. Apply to the Makefile, pool.py, hook config and both `Lxx`.

### One stage per hook
**Source:** `.pre-commit-config.yaml` 28-32. Every hook pins `stages`; unpinned hooks run twice once more stage types are installed.

### Tests run injected short timeouts, then restore
**Source:** `tests/test_pool.py` 156-170 (`pool.timeout = 0.2` in try/finally). Apply to both new pool tests.

### Subset runs need `--no-cov`
**Source:** `Makefile` 90-97 (`fail_under = 96` reads a partial run as a failure). Apply to `test.fast`.

### Bench is not gate
**Source:** `bench/latency.py` 327-332. A scenario that times out and replaces a worker never enters `DEFAULT_SCENARIOS`.

### Tracked-source check
All analog paths above are tracked (`git ls-files` confirmed for `bench/latency.py`, `bench/RESULTS.md`, `tests/test_pool.py`, `tests/test_bench.py`). No mirrors referenced.

## No Analog Found

| File | Role | Reason |
|---|---|---|
| Hook-drift test (optional) | test | No test reads `.pre-commit-config.yaml` today; closest is `tests/test_no_fake_done.py` (reads Makefile text). Planner should read it before writing. |
| Scratch-repo pre-push verification (D-05) | proof | Not code; a plan task with its result recorded in L36 |
| Upstream gsd-core issue (D-08) | proof | Not code; `gh issue create` against open-gsd/gsd-core, URL recorded in L36 |

## Metadata

**Analog search scope:** `src/spur/pool.py`, `tests/test_pool.py`, `tests/test_bench.py`, `bench/latency.py`, `bench/RESULTS.md` headings, `Makefile`, `.pre-commit-config.yaml`, `docs/HOW_TO_DEVELOP.md`, `README.md`, `docs/architecture/{packaging,decision_log}.md`, `.github/workflows/ci.yml`, `scripts/pr_land.py`, `docs/tech_debt/`.
**Files scanned:** ~16
**Pattern extraction date:** 2026-10-06
