# Phase 26: Gate Fails With a Cause - Research

**Researched:** 2026-10-15
**Domain:** test-harness and CI hygiene (pytest 9.1.1 / pytest-xdist 3.8.0 / pytest-cov 7.1.0, GNU Make 4.4.1, Playwright 1.63.0 sync API, CPython 3.12.15 `multiprocessing`, GitHub Actions `ubuntu-26.04`, Docker)
**Confidence:** HIGH on everything re-measured or re-read this session (every file:line, the flake reproduction and its three arms, the `faulthandler_timeout` / `--strict-config` check, the hook-pin red in both forms, the Playwright baseline race); MEDIUM on the `make test-image` red set (static prediction only, per D-11 it is the first measurement of that item) and on Ubuntu 26 (nothing runs until the human pushes).

**Scope note.** The milestone research (`.planning/research/`) already covers the domain. This file does not repeat it. It (1) re-grounds every reference against the tree as of today, (2) measures the mechanics the planner needs, (3) adds the Validation Architecture. Where this file and a milestone file disagree, this file is newer and was measured on this host.

**Provenance tags used:** `[VERIFIED: file:lines]` = opened this session, value quoted. `[MEASURED]` = I ran it this session (probe scripts in the session scratchpad, no tracked file touched). `[CITED: path]` = read in a repo document. `[ASSUMED]` = inference, listed in the Assumptions Log.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Locked before this discussion (roadmap / kickoff, not re-asked):
- Hang evidence is dump-only; `faulthandler_exit_on_timeout` waits for a first captured hang.
- Ubuntu 26 is pre-classified now on a throwaway PR; only the human may pin `ubuntu-24.04`.
- The hook-pin fix's shape (strip `PYTEST_ARGS` in `_make_env()` vs `PYTEST_ARGS=` on the dry-run command line) is the planner's call; both caller forms tested red first.
- No `src/spur/pool.py` change, no `filterwarnings` entry, no rerun plugin, no `shutdown(wait=True)`, no new dependency (`pytest-timeout` out).

**Flake fix and proof runs**
- **D-01:** The flake fix is **arms B and C together**, in `tests/test_pool.py` only: a module-level autouse fixture whose teardown calls `gc.collect()` (B — the guard that covers any future test with the same `manager` / `pytest.raises` pattern) **and** `del manager` after last use in the three producer tests STACK identified (C — removes the cycle at its source). One fix commit; the debt item `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md` is retired in that commit, quoting the forced-GC table. The success line reads "located and fixed from a reproduction", never "gone".
- **D-02:** The forced-GC-in-lock reproduction (patch `ResourceTracker._check_alive` to call `gc.collect()` first, so cyclic garbage holding a semaphore is finalised re-entrantly) is **committed as a gate test**, not left in a scratchpad. It must be seen red against the unfixed file (STACK: arm A fails 3 of 3) and green after B + C; the red is recorded in the commit or plan summary. Its gate cost is measured and recorded. Shape (subprocess pytest run vs in-process patch) is the planner's call, provided the patch cannot leak into other tests on the same xdist worker.
- **D-03:** STACK's reproduction is **re-run on this host first** (READ-from-STACK until then). If it does not reproduce here, the fix does not land: the item is re-deferred with the measurement that failed to reproduce it (SC3, L08).
- **D-04:** The natural-rate acceptance run is **10 before + 10 after, interleaved** (A1 B1 … A10 B10), `tests/test_pool.py` + `tests/test_api.py` at `-n 8 --cov`. Cap, arms and stop rule committed before the run starts. Effective `-n`, tool versions, host load and signature-classified reds recorded in `bench/RESULTS.md` (appended, never rewritten). Read as "consistent, not conclusive" — 0 of 10 by luck is 15–30 %; the forced-GC test is the proof.
- **D-05:** Twin-selectors repeat proof: **20 local runs** of `tests/test_browser.py` at `-n 8`, count recorded, **plus the post-merge `main` CI run read green** (main is where it failed, 2 of the last 8 runs). This is in addition to the delayed-STL-route red (old step) → green (new step) proof SC2 already requires.

**Hang evidence**
- **D-06:** `-v --durations=<N>` goes on the **`test` recipe, so every `make verify`** (local and CI) prints test ids on start and finish. The one recorded hang was local, under the harness; evidence helps only if it is on when the hang happens. Not on `test.fast`. `tests/test_hooks.py`'s shared-recipe pin compares the pytest lines only through `-n <N>` (research C2), so a flag after the worker count stays inside it — verify, don't assume.
- **D-07:** `faulthandler_timeout = 120` in `pyproject.toml` `[tool.pytest.ini_options]`, **set now from a recorded local `--durations` reading, then confirmed on the phase's first CI run**: read CI's `--durations`, record it, and change the value only if CI's slowest test × 2 exceeds 120 s. The plan names the confirm step as a task, not a hope.
- **D-08:** The deliberately stalled test is a **throwaway**: a temporary test file run once at `-n 8 --cov` with a short timeout override, its whole log kept under the phase's `investigation/` directory and quoted in `bench/RESULTS.md`. Nothing that sleeps is committed.
- **D-09:** Gate cost of the added flags: **3 + 3 `make test` runs interleaved** (A B A B A B), 1-minute load logged per run, no idle wait. Recorded against L43's 300 s bar. If the before/after delta exceeds 5 %, stop and ask before escalating to Phase 25's quiet-host protocol.
- **D-10:** The hang item stays `active` with a runbook stating what the evidence cannot see (a stall after the last test, outside `faulthandler_timeout`'s per-item window) and the operator step for that window. No cause is claimed.

**`make test-image`**
- **D-11:** **Rule pre-committed, checkpoint on surprise.** Run `make test-image` once first and record its whole red set (the research's two `tests/test_bench.py` exit-128 tests are a guess, not the reading). The fix: mount `bench/` and `scripts/` read-only, set `PYTHONPATH=/app/src:/app`, and `--ignore` only files that need `make`, git, the Dockerfile or `.github`. The executor proceeds if every recorded red fits that rule; if any red has another cause, it stops and asks. Excluding `tests/test_calc.py` / `tests/test_trochoid.py` by name is rejected (guts the image suite's maths coverage).
- **D-12:** A host-only file's reason is carried by **`--ignore` in the recipe plus a recipe comment** naming why, matching the existing `--ignore=tests/test_browser.py` pattern. No `skipif` added to test files.
- **D-13:** Guard after the fix: **extend `tests/test_hooks.py`'s existing `test-image` pin** (`test_the_image_suite_ignores_the_browser_test`) to the new mounts, `PYTHONPATH` and `--ignore` list. Tightened, never deleted. Running `test-image` in CI is out of scope (deferred).

**Ubuntu 26 throwaway PR**
- **D-14:** Branch **from `main` at the `v0.5` tag** (`26ddd74`), e.g. `spike/26-ubuntu-26`, one commit changing only the three `runs-on` lines in `.github/workflows/ci.yml` to `ubuntu-26.04`. It reads the shipped tree on the new image — what the rollout will run. A twin-selectors red there is classified as the known main-only red, not an Ubuntu 26 cause.
- **D-15:** **Executor prepares, the human pushes.** The executor creates the branch and commit locally and stops at a checkpoint with the exact `git push` and `gh pr create --draft` lines. The human runs them; the executor resumes, pulls each job's whole log with `gh run view --log`, and classifies `test (3.12)`, `vendor-bundle` and `image` in `bench/RESULTS.md` (`Image:` line from `Set up job`, per-job result) before any `ci.yml` edit lands. PR closed unmerged; the branch is the human's to delete (`spike/21-linux-runner` precedent). A red job is not fixed: options go to the human.
- **D-16:** **If the clock is missed** (jobs not finished, or the 26.04 queue stalls, before the rollout reaches the repo): classify whatever ran with its timestamp against the first migrated `main` run, mark SC5 "not met as written" with the reason, and continue the phase. Phase 29 still reads the migrated run. No pin without the human.

### Claude's Discretion
- The hook-pin fix's shape (roadmap: planner's call; both caller forms tested red first).
- Exactly how the twin-selectors step waits for the link's own STL request and the 350 ms debounce before taking its baseline; folding 24 CX-05 and 21 IN-04a (`_follow_link` on `BUILD_WAIT_MS`) into the same change.
- `--durations` count (STACK suggests 25).
- Whether the forced-GC gate test lives in `tests/test_pool.py` or beside it, provided D-02 holds.

### Deferred Ideas (OUT OF SCOPE)
- Run `make test-image` in CI (a new CI job) so the image suite cannot rot red again — a new capability; candidate for `docs/ideas/`.
- `faulthandler_exit_on_timeout` (REQ-hang-fails-named) — after the first captured hang (already in REQUIREMENTS "Future Requirements").
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-hook-pin-ignores-caller-args | Shared-recipe pin passes when the caller sets `PYTEST_ARGS`, env and `make` command-line forms; red for both before the fix | Section "Item 1": both forms reproduced red this session; exact env a recipe hands down measured; fix shape and test shape |
| REQ-ubuntu26-preclassified | Throwaway PR (`runs-on: ubuntu-26.04` only) runs all three jobs before the rollout; whole logs classified in `bench/RESULTS.md` | Section "Item 2": branch base, clock (rollout 2026-10-19), what to read, precedent format |
| REQ-twin-selectors-race-fixed | Baseline taken after the page's own STL request; delayed-route proof old red / new green; fold CX-05 and IN-04a; retire `must` item | Section "Item 3": mechanism confirmed in `app.js`; probe shows which delay flips the old step (the INFO response, not the STL route); step design |
| REQ-tracker-flake-fixed-from-repro | Reproduction re-run on this host; fix in `tests/test_pool.py` only; forced-GC red then green; committed 10+10 run | Section "Item 4": reproduction, control and arms A/B/C re-run here; subprocess gate-test shape; pitfalls found while probing |
| REQ-hang-leaves-evidence | Stalled test leaves id + stack dump; timeout from recorded `--durations`; gate cost vs 300 s; hang item stays active with runbook | Section "Item 5": `--strict-config` accepts the key; pin stays inside `-n <N>`; dump log shape captured |
| REQ-test-image-runs-what-it-claims | `test-image` run once, red set recorded, then passes; every skip has a named reason | Section "Item 6": static prediction of the red set; why `PYTHONPATH=/app` is redundant but harmless; pin extension |
</phase_requirements>

## Summary

Every file:line the CONTEXT and milestone research cite still holds against the tree today, with three small drifts (all in debt-item prose, listed in "Drift report"). The six items are independent enough to plan as six commits in the roadmap's fixed order. Nothing here needs a new dependency, and nothing needed a tracked file changed to research it.

Four things the planner would otherwise get wrong. (a) The twin-selectors race is not a debounce race: `app.js` calls `update()` directly on load (`app.js:643-644`), so no 350 ms timer is pending at the baseline. The race is that `/api/info` (a server build) must answer before the page issues its STL fetch, so the STL request can land after the baseline. Delaying the **STL route** does nothing to when that request is issued; delaying the **`/api/info` response** does, and turned the old step red 4 of 4 in a stand-in page [MEASURED]. The 350 ms debounce matters at the other end, for CX-05: the zero-request assertion needs a settle past 350 ms **after** the two picks. (b) A forced-GC gate test that runs the three producers in a subprocess costs about 10 s of wall on one worker and must live in `tests/test_pool.py`, not a new file: a new file would join `verify.fast` (30 s kill) because `HEAVY_TEST_FILES` is an exact five-file pin. (c) A driver script that calls `pytest.main` under `spawn` re-executes itself in every pool worker unless it is a `-c` string or has a `__main__` guard; my first probe fell into this and printed nonsense. (d) A partial `--cov` run at the acceptance step ends with a "Required test coverage of 96.0% not reached" failure line unless `--cov-fail-under=0` is passed; that is not the flake's signature and must not be counted as a red.

**Primary recommendation:** Plan six commits in roadmap order, each opening with its first-measurement task (hook-pin red in both forms; push checkpoint for the throwaway PR; the old twin-selectors step red under a parked `/api/info` route; flake reproduction red/green; local `--durations` reading; `make test-image` red set). Prefer the smallest shape at each decision point: strip `PYTEST_ARGS` in `_make_env()`, wait on the STL **request** in the twin step, a `python -c` subprocess for the forced-GC test, and `--ignore` plus comment for host-only files.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Hook-pin recipe comparison (`make -n` dry runs) | Test harness (`tests/test_hooks.py`) | Build system (`Makefile`) | The pin parses the Makefile's printed recipe; the fix is in how the test builds the child environment |
| Twin-selectors request-count assertion | Browser test (`tests/test_browser.py`, Playwright) | Viewer JS (`app.js`, read-only here) | The defect is in the test's baseline; `app.js` is the behaviour under test and does not change |
| Flake guard (GC outside the tracker lock) | Test harness (`tests/test_pool.py`) | CPython stdlib (`resource_tracker`) | The cycle is in test locals; `src/spur/pool.py` is not implicated and must not change |
| Hang evidence (`-v`, `--durations`, `faulthandler_timeout`) | Build system (`Makefile` `test` recipe) | pytest ini (`pyproject.toml`) | Flags in the recipe, timeout in ini so every pytest run gets it |
| Image suite correctness (`test-image`) | Build system (`Makefile` recipe) | Container (Dockerfile / `.dockerignore`) | The recipe decides what is mounted and ignored; the image content is fixed |
| Ubuntu 26 pre-classification | CI (`.github/workflows/ci.yml` on a throwaway branch) | Records (`bench/RESULTS.md`) | The evidence is the runner's logs; the only committed artifact is the record |

## Standard Stack

No new packages. Everything is already installed and pinned.

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | 9.1.1 `[VERIFIED: .venv/bin/python -m pytest --version -> pytest 9.1.1]` | `faulthandler_timeout`, `-v`, `--durations`, unraisable plumbing | Already the project's runner; `faulthandler_timeout` is built in |
| pytest-xdist | 3.8.0 `[VERIFIED: pip list]` | `-n 8` scheduler | Gate recipe |
| pytest-cov | 7.1.0 (coverage 7.16.2) `[VERIFIED: pip list]` | `--cov`, `fail_under = 96` | Gate recipe |
| playwright | 1.63.0 `[VERIFIED: pip list]`, headless shell `chromium_headless_shell-1243` present in `.venv/ms-playwright` | Twin-selectors proof | Held by L23 / REQUIREMENTS |
| GNU Make | 4.4.1 `[VERIFIED: make --version]` | Dry-run pins, recipes | Existing |
| CPython | 3.12.15 `[VERIFIED: .venv/bin/python --version]` | Reproduction | L23 |

### Supporting
None added. `gh` (authenticated as `halfb00t`, ssh git protocol) and Docker (OrbStack, daemon up, no `spur` image built yet) are on the host `[VERIFIED: gh auth status, docker ps, docker image ls spur]`.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `faulthandler_timeout` | `pytest-timeout` | New dev dependency; out by REQUIREMENTS |
| In-process monkeypatch for the forced-GC test | `python -c` subprocess running `pytest.main` | In-process cannot make the producers run before the victim deterministically under xdist scheduling; subprocess can. See Item 4 |

**Installation:** none.

**Version verification:** versions above read from the installed venv this session; no registry query was needed because nothing is installed.

## Package Legitimacy Audit

No external packages are installed by this phase. Audit not applicable; the `package-legitimacy` seam was not run because there is nothing to check.

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Drift Report (CONTEXT / milestone research against the tree today)

| Reference | Claimed | Found | Status |
|-----------|---------|-------|--------|
| `Makefile` `test` recipe | lines 176-177 | `test: $(STAMP) $(BROWSER)` at 176, `$(PY) -m pytest -n $(PYTEST_WORKERS) --cov --cov-report=term $(PYTEST_ARGS)` at 177 `[VERIFIED: Makefile:176-177]` | holds |
| `PYTEST_ARGS ?=` | line 6 | `PYTEST_ARGS ?=` at 6 `[VERIFIED: Makefile:6]` | holds |
| `Makefile` `test-image` | line 219 | recipe 219-226; comment 217-218 `[VERIFIED: Makefile:217-226]` | holds |
| `_make_env` / `_dry_run` | 34 / 58 | 34 / 58 `[VERIFIED: tests/test_hooks.py:34,58]` | holds |
| `test_the_image_suite_ignores_the_browser_test` | 181 | 181 `[VERIFIED: tests/test_hooks.py:181]` | holds |
| Pin's `-n <N>` comparison | "through `-n <N>`" | `through_worker_count` at 114-116 slices `words[: words.index("-n") + 2]`, compared at 118; `assert "--ignore=" not in whole_pytest` at **120** `[VERIFIED: tests/test_hooks.py:114-120]` | holds; hook-pin debt item cites line **90** and `Makefile:170` (stale, see below) |
| `BUILD_WAIT_MS` import / `_follow_link` | 39 / 204 | 39 / 204; its `expect_request` has **no** `timeout=` at 213 `[VERIFIED: tests/test_browser.py:204-215]` | holds |
| `wait_for_request(... timeout=BUILD_WAIT_MS)` patterns | 272, 386, 410 | 272, 386, 410 (they are `expect_request(...)`, not `wait_for_request`) | holds, name differs |
| Twin step | baseline ~1576, assert ~1611 | step opens 1532; `requests_before = len(seen)` 1576; assert 1611 `[VERIFIED: tests/test_browser.py:1532,1576,1611]` | holds |
| `tests/test_pool.py` | 18 tests, manager handling ~159-194 | 18 `def test_`; STACK says "the 20-test file" (stale); `manager = ...` at 163, 556, 610 `[VERIFIED: grep]` | holds; STACK's count is stale |
| Three producer tests | named in STACK | `test_a_wedged_build_is_terminated_and_its_worker_replaced` (143), `test_a_stale_executor_timeout_is_a_build_timeout_not_an_attribute_error` (527), `test_three_same_tick_same_slot_timeouts_each_end_in_a_documented_refusal` (585) | holds |
| `pyproject.toml` `[tool.pytest.ini_options]` | `--strict-config`, `filterwarnings` | `addopts = "--strict-markers --strict-config"`, `xfail_strict = true`, `filterwarnings = ["error", "ignore::DeprecationWarning:starlette.*", "ignore:Using `httpx`"]`, **no** `faulthandler_timeout` yet `[VERIFIED: pyproject.toml, [tool.pytest.ini_options]]` | holds |
| `ci.yml` `runs-on` | lines 13, 61, 77 | `runs-on: ubuntu-latest` at 13, 61, 77 `[VERIFIED: grep]` | holds |
| `required-jobs.txt` | three names | `test (3.12)`, `vendor-bundle`, `image` `[VERIFIED: file]` | holds; no test asserts a `runs-on` value (`grep ubuntu\|runs-on tests/*.py` hits comments only) |
| `v0.5` tag | `26ddd74` | `git rev-parse v0.5` prints `9fd57a1...` (an annotated tag object); `git rev-parse 'v0.5^{commit}'` = `26ddd74b52ec91981c88773e1c2e2974d084d034`; local `main` = `origin/main` = `26ddd74` | holds; `git checkout v0.5` / `git switch -c spike/26-ubuntu-26 v0.5` both land on the commit |
| Hook-pin debt item file refs | `Makefile:170`, `test_hooks.py:90` | now `Makefile:177`, `test_hooks.py:120` | **drift**, prose only; the retire commit rewrites the item anyway |
| Hang debt item file refs | `Makefile:170` | now `Makefile:177` | **drift**; refresh while adding the runbook |
| Shipped tree vs `v0.5` | milestone branch has only planning/docs commits | `git diff --stat v0.5 HEAD -- . ':!.planning' ':!docs'` is empty `[MEASURED]` | holds: the working tree's code and `ci.yml` equal `v0.5` |
| Unassigned finding half | CONTEXT folds only 21 IN-04a | `_wait_until_parked` at 585-593 still spins `page.evaluate("0")` with no pause `[VERIFIED: tests/test_browser.py:585-593]`; review text IN-04 has both halves `[CITED: 21-REVIEW.md:160-170]` | **open**, see Open Question 1 |

## Architecture Patterns

### System Architecture Diagram

```
                        make verify  (the gate; PYTEST_ARGS comes last)
                              |
        +---------------------+----------------------------+
        |                                                  |
  verify.static                                   test  ->  pytest -n 8 --cov --cov-report=term
  (ruff, mypy, lint-imports, no-fake-done)               [+ -v --durations=N        <- Item 5]
                                                          [ini: faulthandler_timeout = 120  <- Item 5]
                                                                |
        +-----------------------+-------------------+-----------+----------------+
        |                       |                   |                            |
  tests/test_hooks.py     tests/test_pool.py   tests/test_browser.py        (everything else)
  make -n dry runs        real spawn workers   real uvicorn + headless shell
  child env = _make_env() autouse gc.collect   twin step: goto(link) -> wait for the
  [strip PYTEST_ARGS]     [Item 1, 6]          link's own /api/model.stl REQUEST ->
  test-image pin          + forced-GC gate     baseline -> two pending picks ->
  [Item 1, 6]             test (subprocess)    settle > 350 ms -> assert zero requests
                          [Item 4]             [Item 3]

  make test-image -> docker run (src, tests, pyproject, bench, scripts mounted :ro)
                     python -m pytest -q --ignore=<host-only files>        [Item 6]

  throwaway branch spike/26-ubuntu-26 (v0.5 tree, three runs-on lines changed)
     -> human pushes -> draft PR -> ci: test (3.12) | vendor-bundle | image
     -> gh run view --log -> classification in bench/RESULTS.md (never merged)    [Item 2]
```

### Recommended Project Structure
No new directories except the phase's `investigation/` (created by the plan for D-08/D-15 logs). One new test file is not recommended (see Item 4).
```
tests/test_hooks.py          # _make_env strips PYTEST_ARGS; new env-form tests; image pin extended; -v/--durations asserted
tests/test_browser.py        # twin step baseline + settle; _follow_link timeout
tests/test_pool.py           # autouse gc fixture, 3x del manager, forced-GC subprocess gate test
Makefile                     # test recipe flags; test-image mounts/PYTHONPATH/--ignore + comment
pyproject.toml               # faulthandler_timeout
bench/RESULTS.md             # appended "## Gate fails with a cause (Phase 26)" with one subsection per measurement
.planning/phases/26-gate-fails-with-a-cause/investigation/   # throwaway-stall log, test-image first-run log, CI logs
```

### Pattern 1: Strip the caller's variable in the child's environment (Item 1)
**What:** `_make_env()` already removes make's own `MAKEFLAGS`, `MFLAGS`, `MAKELEVEL`; add `PYTEST_ARGS` to that removal. One edit covers every make-spawning test (`_dry_run`, the `-W` forced-install dry runs, the `requirements.txt` dry run, the hook-stamp tests), not just the one pin.
**Why not `PYTEST_ARGS=` on the command line:** also works, but must be repeated at each `make` call site (there are five), and a command-line variable overrides the Makefile's own `?=` for the dry run only by being on that one line.
**Example (shape, not final code):**
```python
# tests/test_hooks.py
_MAKE_VARIABLES = ("MAKEFLAGS", "MFLAGS", "MAKELEVEL")   # [VERIFIED: tests/test_hooks.py:24]
# add: "PYTEST_ARGS" -- a caller narrowing the gate sets it, and the dry run would print it
# into the recipe the pin compares (--ignore= then fails `assert "--ignore=" not in ...`).
```

### Pattern 2: Wait on the request that ends the race, then count (Item 3)
**What:** the baseline is the count after the page's own `/api/model.stl` request has been seen, and the zero-request assertion is made only after a settle longer than the 350 ms debounce.
**Example (shape):**
```python
# Source: probe2.py in the session scratchpad, Playwright 1.63.0 sync API, run against a stand-in page
with twins_page.expect_request(lambda r: "/api/model.stl" in r.url, timeout=BUILD_WAIT_MS):
    twins_page.goto(server + "/#" + link)       # the link's own build: info, then STL
requests_before = len(seen)                     # nothing of the link's is still in flight
# ... the two pending picks ...
twins_page.wait_for_timeout(DEBOUNCE_SETTLE_MS) # > 350 ms (app.js:289) so a stray scheduleUpdate() has fired
assert len(seen) == requests_before, ...
```
Order inside `expect_request`: the listener `record_api` registered first appends to `seen` before the waiter resolves; the probe read `before 2` on the new shape, so the STL URL was already counted [MEASURED].

### Pattern 3: Run the forced-GC check in a fresh interpreter (Item 4)
**What:** `subprocess.run([sys.executable, "-c", SCRIPT, *ids], cwd=REPO_ROOT, env=<scrubbed>)`. The script patches `ResourceTracker._check_alive` to call `gc.collect()` first, then `sys.exit(pytest.main([...ids]))`. A fresh interpreter is the only form where the patch cannot leak onto other tests on the same xdist worker, and the only one that runs the producers right before the victim.

### Anti-Patterns to Avoid
- **A driver script file without a `__main__` guard around `pytest.main`:** under `spawn`, every pool worker re-imports the main module and re-runs pytest. My first probe printed 4 blocks per run and 58-72 `_check_alive` calls; the corrected one read 94 calls and a clean verdict [MEASURED]. Use `python -c`, or guard.
- **Delaying the STL route to prove the race:** the route's state (aborted or parked) did not change the outcome (4 of 4 red for both) [MEASURED]. The request is recorded when issued.
- **A `time.sleep` inside a route handler as the "delay":** the sync API runs handlers on the dispatcher; the sleep blocks event delivery, so `expect_request` returned only after the handler finished (0.415 s for a 0.4 s sleep) and the old step's baseline moved with it [MEASURED]. Park the route instead and release it from the test.
- **New test file for the forced-GC test:** a file not named in `HEAVY_TEST_FILES` joins `verify.fast` automatically (the exclusion form is deliberate, L36), and ~10 s breaks the 30 s kill budget.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Per-test timeout / stack dump | A watchdog thread or signal handler in conftest | `faulthandler_timeout` ini key | Built in, accepted under `--strict-config` [MEASURED], dumps every thread's stack |
| Test-start / test-finish ids | A logging hook | `-v` | xdist controller prints `path::name` at start and `[gwN] [ NN%] PASSED path::name` at finish [MEASURED] |
| A delayed response in Playwright | `time.sleep` in a handler | Park the `Route` in a list and `continue_()` it from the test (pattern at `tests/test_browser.py:669`, `_wait_until_parked`) | Handlers only run during a Playwright call; sleeping blocks the dispatcher |
| Waiting for a request | A poll loop on `len(seen)` | `page.expect_request(predicate, timeout=BUILD_WAIT_MS)` | Already the file's idiom (272, 386, 410, 1568-1570) |
| A reentrant-GC reproducer | `gc.set_threshold` stress | Patch `_check_alive` to `gc.collect()` | Tight thresholds free the garbage before the tracker is entered and hide the bug (STACK, 0 of 6) |

**Key insight:** every item here is a few lines. The cost is in proving each one red first and recording the measurement; do not add machinery.

## Item-by-item mechanics

### Item 1 - hook pin and `PYTEST_ARGS` (REQ-hook-pin-ignores-caller-args)

**Both forms reproduced red this session on the unfixed tree** `[MEASURED]`, pin `tests/test_hooks.py::test_verify_and_verify_fast_share_one_static_prefix_and_one_pytest_recipe`:
- Environment form: `PYTEST_ARGS="--ignore=tests/test_browser.py" .venv/bin/python -m pytest <pin> -n0 --no-cov -q` -> `1 failed in 0.03s`, failing at `tests/test_hooks.py:120` (`assert "--ignore=" not in whole_pytest`).
- Command-line form: `make test PYTEST_ARGS="--ignore=tests/test_browser.py <pin> -n0 --no-cov -q -p no:cacheprovider"` -> the same failure, then `make: *** [Makefile:177: test] Error 1`.

**What a recipe's environment actually holds** `[MEASURED: scratch Makefile with PYTEST_ARGS ?=, GNU Make 4.4.1]`:
- Command-line form: `MAKEFLAGS= -- PYTEST_ARGS=--ignore=x`, `MAKELEVEL=1`, `MFLAGS=`, **`PYTEST_ARGS=--ignore=x`**.
- Environment form: `MAKEFLAGS=`, `MAKELEVEL=1`, `MFLAGS=`, `PYTEST_ARGS=--ignore=x`.
`_make_env()` strips the first three and so removes the variable's second carrier (`MAKEFLAGS`) but not `PYTEST_ARGS` itself. That is the whole defect.

**Recommendation (planner's call, made concrete):** strip `PYTEST_ARGS` in `_make_env()`. Tests, written first and seen red:
1. Env form: `monkeypatch.setenv("PYTEST_ARGS", "--ignore=tests/test_browser.py")`, call the existing pin function.
2. Command-line form as the recipe hands it down: set `PYTEST_ARGS`, `MAKEFLAGS=" -- PYTEST_ARGS=--ignore=tests/test_browser.py"`, `MAKELEVEL=1`, `MFLAGS=""` together, call the pin. Because `_make_env()` already strips the `MAKEFLAGS` trio, this case is red before only through `PYTEST_ARGS`; it exists to document the shape make hands down, not to add a second mechanism.
3. Record the two end-to-end runs above (env and `make test PYTEST_ARGS=...`) red before and green after in the plan summary; they exercise the real hand-down.
Keep the existing pin test unchanged apart from the call-it-twice reuse; `tests/test_hooks.py` runs in 0.60 s for all 7 tests `[MEASURED]`, so red/green cycles are free.

**Pin tightening that rides with Item 5 (same file, same pin):** assert `-v` and a `--durations=` word are in `whole_pytest` and absent from `fast_pytest`, so D-06's "not on `test.fast`" is guarded, not just stated.

### Item 2 - Ubuntu 26 throwaway PR (REQ-ubuntu26-preclassified)

- **Clock:** `ubuntu-latest` begins moving to 26.04 on 2026-10-19, complete 2026-11-19 `[CITED: .planning/research/STACK.md section 3, github.blog changelog 2026-09-17]`. Today is 2026-10-15: four days. A run of the three jobs takes roughly 8 to 16 minutes of wall (main runs: 7m50s to 13m30s `[MEASURED: gh run list --branch main]`). Put the push checkpoint as early in the plan as the roadmap order allows (right after Item 1's commit) and say so in the checkpoint text.
- **Branch:** `git switch -c spike/26-ubuntu-26 v0.5` (commit `26ddd74`, also `main`/`origin/main`). One commit, only `.github/workflows/ci.yml` lines 13, 61, 77 `ubuntu-latest` -> `ubuntu-26.04`. The label exists and is generally available `[CITED: STACK.md section 3]`.
- **Not breaking anything else:** no test asserts a `runs-on` value; `required-jobs.txt` and `tests/test_pr_land.py` constrain job **names** only `[VERIFIED: grep ubuntu\|runs-on tests/*.py -> comment hits only; tests/test_pr_land.py:268-290]`. A matrix leg would rename the required check; do not use one.
- **Push checkpoint lines for the human:** `git push -u origin spike/26-ubuntu-26` then `gh pr create --draft --base main --head spike/26-ubuntu-26 --title "spike(26): ubuntu-26.04 pre-classification -- DO NOT MERGE" --body "Throwaway. Three runs-on lines only. Closed unmerged."` (precedent: draft PR #32, `spike(21): browser tracer on ubuntu-latest -- DO NOT MERGE` `[CITED: bench/RESULTS.md:4864]`). `ci.yml` triggers on `pull_request` so a draft PR runs the three jobs `[VERIFIED: .github/workflows/ci.yml:3-6]`.
- **What to pull and record** (format precedent `bench/RESULTS.md` "Linux runner spike (21-02)" at 4857 and "The Linux path on the real runner (21-08)" at 5169): `gh run view <id> --log` per job; the `Image:` line and version from `Set up job` (precedent: `ubuntu-24.04`, `20261004.327.1`); per-job result; `test (3.12)` wall and the `pytest` result line; Playwright install seconds; WebGL renderer string; `nproc`/`-n`. Compare with the 24.04 reading at 4874-4880 and the container reading in STACK section 3.
- **Classification rule for a red:** the shipped tree has the twin-selectors race and the resource-tracker flake. A red whose log shows `twin selectors: 1 request(s) sent by two pending picks` or five `ResourceTracker called reentrantly` lines is the known main red, not an Ubuntu 26 cause (D-14). Any other red: stop, options to the human (they alone may pin `ubuntu-24.04`).
- **Stale-risk:** none of this runs until the human pushes. D-16 covers the missed-clock case.

### Item 3 - twin selectors (REQ-twin-selectors-race-fixed)

**Mechanism, re-grounded in source.** `app.js` runs `update()` directly at load (`update();` at `app.js:643-644`, after `readHash();`); `update()` fetches `api/info?...`, and only after that response parses does it fetch `api/model.stl?...` (`app.js:242-273`) `[VERIFIED: src/spur/static/app.js:242-273, 640-645]`. `scheduleUpdate()` (the 350 ms `setTimeout(update, 350)`, `app.js:286-290`) is called only from the form's `input` listener and the mate box (`app.js:608-609`) `[VERIFIED]`. So at load no debounce timer is pending. The step's baseline (`tests/test_browser.py:1576`) is read after `expect_request("/api/info")` plus two `evaluate` round trips; the link's own STL request is issued after the info **response**, so on a slow runner it lands after the baseline and inside the window counted at 1611. That matches both CI captures (`assert 269 == 268`, `assert 266 == 265`: exactly one extra request) `[CITED: docs/tech_debt/active/2026-10-15-twin-selectors-step-reds-main.md]`.

**Which delay turns the old step red** `[MEASURED]`, stand-in page (`fetch /api/info` then `fetch /api/model.stl`), real headless shell 1243, old step shape (baseline right after `expect_request(info)` and two `evaluate("0")`):
| Setup | Old-step (before, after) over 4 runs |
|---|---|
| `/api/info` served after a 150 ms server sleep, STL route `abort()` | (1, 2) x 4 |
| same, STL route parked (never resolved) | (1, 2) x 4 |
| `/api/info` route **parked**, released after the baseline | (1, 2) |
| `/api/info` parked, released **then** `expect_request(STL)` **then** baseline (the new shape) | (2, 2) |
The STL route's state is irrelevant; what matters is how long after the baseline the STL **request** is issued, and that is set by the `/api/info` response. SC2 says "a delayed STL route makes the old step red"; the lever that does is a delayed `/api/info` response. The roadmap allows the plan to say so before any fix lands (its own words: "if the delayed route does not turn the old step red, the plan says so"). Do that explicitly.

**Concrete proof setup (sync API):**
1. On `twins_page`, add `info_parked: list[Route] = []` and `twins_page.route("**/api/info*", lambda route: info_parked.append(route))` beside the existing schema and STL routes (a lambda, never the bound `append`: `tests/test_browser.py:667-668` records that Playwright rejects a builtin method as a handler). There is no existing `INFO_ROUTE` constant (only `STL_ROUTE = "**/api/model.stl*"` at `tests/browser_session.py:39`).
2. After `goto`, `expect_request(info)` returns while the route is parked (event is emitted without the handler resolving) [MEASURED]; use `_wait_until_parked(page, info_parked)` (the file's helper at 585) if the order needs a round trip.
3. **Old step red:** keep the old baseline line, then `info_parked[0].continue_()` and let the picks run; the STL request lands in the window; the 1611 assertion fails with `1 request(s) sent by two pending picks`. Record that failure text.
4. **New step green:** `with twins_page.expect_request(STL predicate): info_parked[0].continue_()` then take the baseline; assertion holds.
5. Commit shape: the delay is part of the committed step (a parked-then-released info route costs milliseconds) so the step is deterministic on any host; the red is recorded by running the old two lines against it once before the fix lands.

**CX-05 (the vacuous-pass half), different direction.** The review says the zero-request assertion "could pass before a queued 350 ms debounce fires" `[CITED: 24-REVIEW-DISPOSITION.md:54-57]`. A stray `scheduleUpdate()` would send its request 350 ms later; asserting immediately passes vacuously. Fix: `twins_page.wait_for_timeout(<350 + margin>)` after the second pick and before the count assertion (name a constant beside `BUILD_WAIT_MS` or in the step, e.g. 500). Red control for this half (throwaway, not committed): after the picks, dispatch a bubbling `input` event on one form field with `twins_page.evaluate(...)`; the old (assert-immediately) step still passes, the new (settle) step fails. This is cleaner than deleting `event.stopPropagation()` at `app.js:432`, which would also trip the earlier `PENDING_AT` assertions first.

**IN-04a:** `_follow_link` at `tests/test_browser.py:213` is `page.expect_request(lambda request: "/api/info" in request.url)` with no timeout; add `timeout=BUILD_WAIT_MS` like 272/386/410. Trivial; fold into the same commit per D-05/Discretion.

**Repeat proof (D-05):** 20 local runs of `tests/test_browser.py` at `-n 8` (`make test PYTEST_ARGS="tests/test_browser.py tests/test_browser_pins.py --no-cov -q"`); `make test` is required, not bare pytest: only make exports `PLAYWRIGHT_BROWSERS_PATH` (`Makefile:30`; STACK measured the bare form failing with `Executable doesn't exist`). The browser file is one test function (one `step` after another), so `-n 8` here adds no parallelism within it; the point is the same load shape as the gate. Count passes and record failures by step name. Plus read the first post-merge `main` CI run green.

### Item 4 - resource-tracker flake (REQ-tracker-flake-fixed-from-repro)

**D-03 satisfied: the reproduction holds on this host** `[MEASURED]` (macOS arm64, Apple M5 Max, CPython 3.12.15, 1-minute load about 3.7-4.2):
- Stdlib script (STACK's `rt_repro.py`): printed `5` in **5 of 5** runs; control with `gc.collect()` before the patch printed `0`; control without the cycle printed `0`. (stderr also shows `leaked semaphore` and `No such file` warnings at exit; count stdout only.)
- Forced-GC against `tests/test_pool.py` (3 producers + the victim, `-n0 --no-cov`, `_check_alive` patched): **arm A (unfixed) failed 3 of 3**, always `test_a_closed_pool_never_builds_a_replacement_worker`, each with 5 `called reentrantly` lines; 94 patched calls per run; wall 9.95-10.16 s.
- The same four tests against scratch copies of the file (copy of `pyproject.toml` so `filterwarnings = error` applies; positive control: the unmodified copy failed the same way): **arm B (autouse `gc.collect()` teardown) 0 of 3 failures; arm C (`del manager` after the `is_alive` assertion in the three producers) 0 of 3**. Both 4 passed in about 9.7 s. This is STACK's table, now READ-from-STACK -> MEASURED on this host.

So the fix lands. Per D-03 these numbers are the "re-run first" record; the plan still re-runs them as its first task with its own committed command and writes them to `bench/RESULTS.md`.

**Exact edit points for C** `[VERIFIED: tests/test_pool.py]`: `manager = executor._executor_manager_thread` at 163, last use `assert not manager.is_alive(), ...` at 194 (then `del manager`); `manager = live._executor_manager_thread` at 556, last use at 581; `manager = live._executor_manager_thread` at 610, last use at 638. Insert `del manager` on the line after each last use.

**Fix B:** module-level `@pytest.fixture(autouse=True)` in `tests/test_pool.py` that yields and then `gc.collect()`. Cost measured by STACK at about 10 ms per test (19.7 s -> 19.9 s for the file). Nothing else in `tests/conftest.py` needs to change (the root-logger reset fixture there is unrelated).

**Gate-test shape (D-02), recommendation: subprocess, `python -c`, in `tests/test_pool.py`.**
- Why not in-process: a `monkeypatch.setattr(ResourceTracker, "_check_alive", ...)` is undone at teardown so it cannot leak, but garbage from earlier tests on that worker is whatever xdist scheduled; the producers are not guaranteed to have run just before. Only a fresh interpreter that runs the three producers and then a victim makes the check deterministic.
- Why in `tests/test_pool.py`: it is already one of the five `--ignore`d heavy files for `verify.fast` (`tests/test_hooks.py:HEAVY_TEST_FILES`), and the pin there asserts the exact set; a new file would run at commit time and the subprocess costs about 10 s of the 30 s kill budget.
- Script (all in the test body, passed with `-c`): import `gc`, `pytest`, `multiprocessing.resource_tracker as rt`; `orig = rt.ResourceTracker._check_alive` (raises `AttributeError` if CPython ever removes it: loud, never vacuous); wrapper counts calls, calls `gc.collect()`, returns `orig(self)`; `sys.exit(pytest.main(["-p", "no:cacheprovider", "--no-cov", "-n0", "-q", *ids]))`; print the call count. Test asserts exit 0 **and** call count > 0.
- Ids: the three producers plus `test_a_closed_pool_never_builds_a_replacement_worker`; they are named in the gate test as `tests/test_pool.py::...` strings. Add a guard that each id exists (`pytest.main(["--collect-only"...])` is overkill; a typo gives exit 4 and the test fails, which is loud enough).
- Environment: run with `cwd=REPO_ROOT` (so `pyproject.toml`'s `filterwarnings = error` applies, which is what makes it red) and an env scrubbed of `PYTEST_ADDOPTS` and `PYTEST_ARGS` (Phase 25's arms used `PYTEST_ADDOPTS`; an inherited `--ignore` would silently drop a producer). Keep `PYTHONPATH` as is.
- Recursion: the subprocess does not select the gate test itself, so no recursion.
- Red proof order: write the gate test first with the fix lines absent, run it (expected red, victim `test_a_closed_pool_never_builds_a_replacement_worker`, 5 reentrant lines), then apply B + C, run again (green), record both outputs.
- **Gate cost (D-02):** measured 9.7-10.2 s wall for the four tests in one subprocess; it runs on one xdist worker in parallel with `tests/test_model.py` (74 % of pytest seconds `[CITED: Makefile comment, bench/RESULTS.md "Per-file share"]`), so critical-path cost is probably small, but the plan must measure it (D-02) rather than rely on this.

**Acceptance run (D-04) mechanics:**
- Effective `-n`: `PYTEST_WORKERS` is `min(8, online CPUs)`; this host has 18 CPUs `[MEASURED: getconf]`, so 8. On CI's 4-vCPU runner it is 4.
- A partial `--cov` run ends with `FAIL Required test coverage of 96.0% not reached. Total coverage: 0.00%` `[MEASURED]`; that line is not the flake's signature. Add `--cov-fail-under=0` to the acceptance command (probed: the line disappears, `1 passed`), or keep `--no-cov` for the arms and say so. D-04 says `--cov`; recommend `--cov --cov-fail-under=0` and record both flags.
- Signature (committed rule, PITFALLS): a red counts as the flake only if the log contains `ReentrantCallError` or `ResourceTracker called reentrantly`; any other red is its own row `[CITED: .planning/research/PITFALLS.md:60]`.
- The arms are "before" = tree at the commit before the fix, "after" = fix commit; use two checkouts (`git worktree add`) or `git stash`-free alternation of a pinned `tests/test_pool.py` per arm. The plan must commit the cap, arms and stop rule before the first run (REQUIREMENTS).
- Expected duration: `tests/test_pool.py + tests/test_api.py` is about 20 s plus startup per run, 20 runs -> well under 15 minutes.

### Item 5 - hang evidence (REQ-hang-leaves-evidence)

- **`--strict-config` accepts the key** `[MEASURED]`: a scratch `pyproject.toml` with `addopts = "--strict-markers --strict-config"` and `faulthandler_timeout = 120` ran `1 passed`; renaming the key to `bogus_key` gave `ERROR: Unknown config option: bogus_key`, exit 4 (so the check is real). `pytest --help` lists `faulthandler_timeout (string)` and `faulthandler_exit_on_timeout (bool)`. It is a string key; write `faulthandler_timeout = 120` (TOML integer) as STACK did, or `"120"`; the integer form worked in the probe.
- **Applies to every pytest run**, including `make test.fast`, `make test-image` (pyproject is mounted) and direct `pytest`. The decision to keep `-v --durations` off `test.fast` is about the recipe flags only. Dump-only is harmless on the fast slice.
- **The `-n <N>` pin stays satisfied** `[MEASURED by reading the code]`: `through_worker_count` is `" ".join(words[: words.index("-n") + 2])` (`tests/test_hooks.py:114-116`); the printed line is `.venv/bin/python -m pytest -n 8 --cov --cov-report=term ...`; `-v --durations=25` after `--cov-report=term` (or anywhere after `-n 8`) is outside the compared prefix. Also confirmed: `assert "--cov" in whole_pytest` (119) and `"--ignore=" not in` (120) are unaffected. After the edit, run the pin once; do not assume.
- **Where to put the flags:** `$(PY) -m pytest -n $(PYTEST_WORKERS) --cov --cov-report=term -v --durations=25 $(PYTEST_ARGS)`. `PYTEST_ARGS` stays last so a caller's `-q` cancels `-v` (pytest verbosity is additive: `-v -q` = 0). Update the long comment above the `test` recipe (lines 156-163), which currently explains `PYTEST_ARGS` and `--cov-report=term`; add one sentence for `-v --durations` and `faulthandler_timeout` with the reason (D-06) and the measured cost.
- **Dump log shape** `[MEASURED]`, `-n 2 -v --durations=3 -o faulthandler_timeout=1`: the controller prints `test_stall.py::test_stalls ` (start, no worker id) and, when others finish, `[gw0] [ 66%] PASSED ...`; the worker's dump appears on stderr, can start mid-line right after a controller line (`PASSED test_stall.py::test_ok Timeout (0:00:01)!`), and shows `File ".../test_stall.py", line 2 in test_stalls`. It names the function, not the parametrize id: pair it with the `-v` start line. In-flight set = started minus finished. (The runbook text must say this.)
- **Stalled-test throwaway (D-08):** file under `tests/` (e.g. `tests/test_zz_stall_probe.py`, untracked, deleted afterwards; `git status --short` must be clean at the end) with `def test_stalls(): time.sleep(<more than the override>)`. Command: `make test PYTEST_ARGS="tests/test_zz_stall_probe.py -o faulthandler_timeout=5 --cov-fail-under=0 2>&1 | tee .planning/phases/26-.../investigation/26-0N-stall.log"` (run at `-n 8 --cov` as D-08 says; with one test, xdist starts eight workers anyway). The probe file contains `time.sleep`, which `no-fake-done` does not flag (its markers are TODO/FIXME/XXX/HACK/NotImplementedError), but do not commit it.
- **Local `--durations` reading (D-07, first task):** `make test PYTEST_ARGS="--durations=25"` is a full gate (about 3 to 4 minutes on this host, 179-195 s for the two Phase 25 readings `[CITED: bench/RESULTS.md:5712-5760]`); combine it with D-09's "after" arm so one run serves both, or run it once separately. STACK's starting reading: slowest phases 25.77, 22.24, 20.52 s locally; about 52 s on CI (401.82 s wall on 4 vCPUs) `[CITED: STACK.md section 2]`. 120 s is 2.3x the CI estimate; D-07's rule: change only if CI's slowest x 2 exceeds 120 s.
- **Confirm-on-CI task (D-07):** after the phase branch's first CI run, read `--durations` from the `test (3.12)` log, record it, apply the x2 rule. The branch is the human's to push, so this is a checkpoint like Item 2's.
- **Gate cost (D-09):** 3 + 3 `make test` interleaved, 1-minute load recorded per run, delta > 5 % -> stop and ask. Phase 25's two readings (195.23 s and 179.21 s, both non-decisive, loads 4-7) show run-to-run spread of the same order as 5 %; say plainly in the record that a 5 % delta on three runs per arm is inside that spread, and read it as the human asked ("stop and ask"), not as a verdict.
- **Runbook (D-10):** add to the hang item `docs/tech_debt/active/2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md`: how to read the log (started-minus-finished from `-v`; the dump names the function; `Timeout (0:02:00)!`), what it cannot see (the window after the last item and before worker exit: the faulthandler timer is armed per item `[CITED: STACK.md section 2, _pytest/faulthandler.py]`), and the operator step for that window (`kill -ABRT <pid>` on the stalled xdist worker, UNVERIFIED here, writes a crash report on macOS; on Linux CI none). Keep `Status: active`; no cause claimed. Refresh the stale `Makefile:170` reference to `177`.

### Item 6 - `make test-image` (REQ-test-image-runs-what-it-claims)

**Environment:** Docker daemon is up (OrbStack), no `spur` image exists yet, so the first `make test-image` builds it (`pip install --no-deps -r requirements.txt`, minutes). The recipe runs `python -m pytest -q -p no:cacheprovider` with **no** `-n`, so it is serial `[VERIFIED: Makefile:219-226]`; the Makefile comment prices serial at about 4x the xdist gate (`Makefile:165-166`, "suite would run -n 0 (serial, 4x the cost)"), which would put the first full run near 10 to 15 minutes `[ASSUMED]`. Run it in the background with a generous timeout and keep the whole log (D-11).

**Static prediction of the red set (UNVERIFIED until the first run; D-11 makes the run authoritative).** What is in the image: `/app` holds `requirements.txt`, `pyproject.toml` (overlaid by the mount), `README.md`, `docker/`, `src/` (overlaid); `.dockerignore` excludes `Dockerfile`, `docs`, `.github`, `tests`, `web`, `compose.yaml`; the slim base has no `make` and (almost certainly) no `git` `[VERIFIED: Dockerfile, .dockerignore]`.
| Test file | Needs | Predicted in the image with `bench/`+`scripts/` mounted |
|---|---|---|
| `tests/test_calc.py:27`, `tests/test_trochoid.py:21-22` | `import bench.trochoid` | collect OK once `bench/` is mounted (repo root on `sys.path`, see below); red without it |
| `tests/test_bench.py` (imports `bench.*`, line 45-65; reads `bench/sweeps/composed.json` at 915) | `bench/`; `git rev-parse` in `bench.build_time` / `bench.trochoid_part` (`bench/build_time.py:132`, `bench/trochoid_part.py:333`) | tests that call those fail (no git / no `.git`); research saw exit 128 with a git binary and no `.git` |
| `tests/test_skip_tokens.py` | `scripts.skip_tokens` via `python -m scripts.skip_tokens` with `cwd=REPO_ROOT` (`:185-192`) | OK once `scripts/` is mounted and cwd is `/app` |
| `tests/test_pr_land.py` | `scripts.pr_land`; reads `.github/workflows/ci.yml` (`:273,283`) and `required-jobs.txt` | red on the two `.github` tests; rest pure |
| `tests/test_hooks.py` | `make`, `Makefile`, `.pre-commit-config.yaml` | red (no make, no files) |
| `tests/test_no_fake_done.py` | `Makefile`, `make`, `git init` | red |
| `tests/test_browser_pins.py` | `Dockerfile` (`:138-139`), `tests/*browser*.py`, `playwright` text | red on the Dockerfile read |
| `tests/test_browser.py` | `playwright` | already `--ignore`d |
| `tests/test_cli.py:149`, `tests/test_api.py:190` | `README.md` | present in the image (`COPY pyproject.toml README.md ./`) so should pass |
| `tests/regression/*` | `requirements.txt`, `tests/regression/*.json` | `requirements.txt` is in the image; should pass |
Every predicted red fits D-11's rule (make, git, Dockerfile, `.github`), except possibly individual `tests/test_bench.py` tests whose git need would argue for `--ignore=tests/test_bench.py` as a whole file (the rule allows it: "files that need git"); that loses `bench`'s non-git unit tests in the image, which the first run's actual set will show. If anything else is red (a missing system library, a wrong pytest in the image, an arch-specific tolerance), D-11 says stop and ask.

**`PYTHONPATH=/app/src:/app` is redundant but harmless.** The recipe's last command is `python -m pytest` with `-w /app`; the `-m` form puts the current directory on `sys.path` `[CITED: tests/test_bench.py:24-30 docstring]`, which is exactly why `bench` resolves. What is actually missing today is the **mounts**, not the path. Keep the PYTHONPATH change as D-11 decided; just do not expect it to be what turns the red set green, and say so in the recipe comment so a later reader does not "fix" the wrong thing.

**Recipe shape:** add `-v "$(CURDIR)/bench:/app/bench:ro" -v "$(CURDIR)/scripts:/app/scripts:ro"`, `-e PYTHONPATH=/app/src:/app`, and one `--ignore=tests/<file>.py` per host-only file, each with a comment line naming its reason (make / git / Dockerfile / `.github`), matching the existing browser comment at `Makefile:217-218` (D-12). The comment currently says "tests/test_hooks.py reads this recipe"; keep the cross-reference.

**Pin extension (D-13):** `test_the_image_suite_ignores_the_browser_test` (`tests/test_hooks.py:181-190`) only parses from the ` -m pytest ` line. To assert mounts and `PYTHONPATH` it must also read the `docker run ...` line(s) before it; `make -n` prints the continuation lines separately, so rejoin from the line containing `docker run`. Assert, as exact sets like the heavy-file pin does: the ignored files (so a silent new `--ignore` is a red), the mounted sources (`src`, `tests`, `pyproject.toml`, `bench`, `scripts`, all `:ro`), and `PYTHONPATH=/app/src:/app`. Rename the test to what it now pins; "tightened, never deleted".

## Common Pitfalls

### Pitfall 1: Counting the coverage floor failure as a red
**What goes wrong:** a partial run with `--cov` prints `FAIL Required test coverage of 96.0% not reached` and exits non-zero, so every acceptance run is "red".
**Why:** `fail_under = 96` (`pyproject.toml`) applies to any `--cov` run `[MEASURED]`.
**How to avoid:** `--cov-fail-under=0` on acceptance and stall-probe runs; classify reds by the flake signature only.
**Warning signs:** a run with `N passed` and exit 1.

### Pitfall 2: A pytest driver that spawn re-runs
**What goes wrong:** a script calling `pytest.main` without a `__main__` guard is re-executed by every `spawn` pool worker; output multiplies and call counts balloon (58-72 vs 94 in my probe).
**How to avoid:** `python -c` (no `__file__`, spawn skips main re-import) or a guard.

### Pitfall 3: The inherited `PYTEST_ADDOPTS` / `PYTEST_ARGS` in a nested run
**What goes wrong:** Phase 25's arm A set `PYTEST_ADDOPTS="--ignore=tests/test_browser.py"`; a nested pytest inherits it and can silently drop an id.
**How to avoid:** scrub both from the subprocess env in the forced-GC test; strip `PYTEST_ARGS` in `_make_env()`.

### Pitfall 4: Proving the twin step red with the wrong delay
**What goes wrong:** delaying the STL route leaves the old step as it was.
**How to avoid:** park `/api/info`, release after the baseline (old) or release then wait for the STL request (new); record both.

### Pitfall 5: `make test-image` red for a reason D-11 does not cover
**What goes wrong:** the executor assumes every red fits the rule.
**How to avoid:** classify each red against the four causes (make, git, Dockerfile, `.github`) in a table in the record; any red outside them is the stop-and-ask trigger.

### Pitfall 6: The 20-run browser loop under `make test` rebuilding stamps
**What goes wrong:** the first `make test` after a `pyproject.toml` edit (Item 5 adds `faulthandler_timeout`) reinstalls the venv and the headless shell because `$(STAMP)` depends on `pyproject.toml`.
**Why:** `$(STAMP): pyproject.toml requirements.txt` (`Makefile:57`), `$(BROWSER): $(STAMP)`.
**How to avoid:** accept one slower first run after the ini edit and do not time it; note it in the record. (Item order puts Item 3's repeat runs before Item 5's ini edit, which avoids it for the 20 runs.)

## Code Examples

### Hook-pin env form test (shape)
```python
# Source: tests/test_hooks.py patterns; reproduction measured this session
def test_the_pin_ignores_the_callers_pytest_args(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYTEST_ARGS", "--ignore=tests/test_browser.py")
    test_verify_and_verify_fast_share_one_static_prefix_and_one_pytest_recipe()
```
(`import pytest` is not yet imported in `tests/test_hooks.py`; the file's imports are `os, re, shutil, subprocess, Path` `[VERIFIED: tests/test_hooks.py:12-18]`.)

### Forced-GC gate test (shape)
```python
# Source: scratchpad gcrun.py, measured 3/3 red unfixed, 3/3 green with arms B or C
_FORCED_GC = """
import gc, sys
from multiprocessing import resource_tracker as rt
import pytest
orig = rt.ResourceTracker._check_alive
calls = 0
def forced(self):
    global calls
    calls += 1
    gc.collect()          # under the tracker's RLock, as an automatic pass would land there
    return orig(self)
rt.ResourceTracker._check_alive = forced
code = pytest.main(["-p", "no:cacheprovider", "--no-cov", "-n0", "-q", *sys.argv[1:]])
print("check_alive calls:", calls)
sys.exit(code)
"""
# subprocess.run([sys.executable, "-c", _FORCED_GC, *ids], cwd=REPO_ROOT, env=scrubbed, ...)
```
Note `sys.argv[1:]` under `-c` holds the ids (argv[0] is `-c`).

### Twin step baseline (shape)
See Pattern 2. Settle constant: name it next to the 350 ms fact (`app.js:289`), e.g. `DEBOUNCE_MS = 350` plus margin.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `pytest-timeout` for per-test stacks | `faulthandler_timeout` (and `faulthandler_exit_on_timeout`, pytest >= 9.0) | pytest 9.x | No new dependency; exit-on-timeout deferred by the human |
| Milestone research "delayed STL route" for the race proof | Delay the `/api/info` response | measured this session | The STL route's state does not move the old step |

**Deprecated/outdated:** STACK's "20-test file" count for `tests/test_pool.py` (it is 18); the two debt items' `Makefile:170`.

## Runtime State Inventory

Not a rename/refactor/migration phase. Omitted per the output contract. (The one stateful item is the throwaway branch/PR on the remote, which is the human's to delete, D-15.)

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The first `make test-image` red set is the one predicted in the Item 6 table (make, git, Dockerfile, `.github` reasons only) | Item 6 | A red with another cause triggers D-11's stop-and-ask; small cost, but the plan's `--ignore` list would change |
| A2 | The first full serial `make test-image` takes roughly 10 to 15 minutes (the Makefile's "4x the cost" comment applied to a ~3 minute gate) | Item 6 | Executor sets too short a timeout and the run is killed; give it a generous cap |
| A3 | `python:3.12-slim-bookworm` has no `git` binary | Item 6 | If git exists, `test_bench` failures would read exit 128 (no `.git`) rather than `FileNotFoundError`; the classification (git) is the same either way |
| A4 | The stand-in-page probe (fake `/api/info` and `/api/model.stl`) transfers to the real viewer: the old twin step goes red under a parked `/api/info` route | Item 3 | The real step is the proof; if the old step does not go red against the real app, the plan must say so before any fix lands (the roadmap's own rule) |
| A5 | A 500 ms settle is enough margin past the 350 ms debounce on CI | Item 3 | Too short -> CX-05 half stays flaky-vacuous; pick a margin and measure it on the first CI run |
| A6 | `kill -ABRT <pid>` prints all thread stacks for a stalled xdist worker (carried from STACK, not run here) | Item 5 | Runbook step wrong; the runbook already labels it unverified |
| A7 | The throwaway PR's three jobs finish within the four days before the rollout starts, and the human pushes in time | Item 2 | D-16 covers it (classify with timestamp, SC5 "not met as written") |
| A8 | Three-per-arm gate-cost runs cannot resolve a 5 % delta against Phase 25's run-to-run spread | Item 5 | The "stop and ask" rule triggers on noise; state the spread in the record |

## Open Questions

1. **IN-04b, the hot loop in `_wait_until_parked` (`tests/test_browser.py:585-593`).**
   - What we know: 21 IN-04 has two halves; CONTEXT/ROADMAP fold only IN-04a (`_follow_link` timeout). REQUIREMENTS lists 21 IN-04 among findings that must be "fixed, not skipped" but maps no phase to fix it; Phase 28 owns only the triage record.
   - What's unclear: whether Phase 26 should fix the loop's missing yield (`page.wait_for_timeout(50)`) while the step is open anyway.
   - Recommendation: stay in scope (IN-04a only) and put "IN-04b unassigned" in the plan summary so Phase 27/28 picks it up; it is a one-line change in the same file if the human wants it folded.

2. **Should the throwaway PR be pushed before Item 1's commit lands?**
   - What we know: the PR branch is cut from `v0.5` and does not contain Item 1; the roadmap fixes the order (1 then 2) for the recipe-truth reason, but the clock is 2026-10-19.
   - Recommendation: keep the order, but do Item 2's local branch-and-commit step immediately after Item 1 and make the push checkpoint the first thing the human sees; item 1 takes minutes.

3. **`tests/test_bench.py`: whole-file `--ignore` or not?** Only the first `make test-image` run can say which of its tests fail and why. The D-11 rule permits ignoring the file if any of its failures need git. Decide from the recorded set, not from this prediction.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 venv | all items | yes | 3.12.15 | -- |
| pytest / xdist / cov / playwright | all items | yes | 9.1.1 / 3.8.0 / 7.1.0 / 1.63.0 | -- |
| Headless shell | Item 3 | yes | `chromium_headless_shell-1243` in `.venv/ms-playwright` | `make test` reinstalls via the `$(BROWSER)` stamp |
| GNU Make | Items 1, 5, 6 | yes | 4.4.1 | -- |
| git | Items 2, 4 | yes | 2.56.0 | -- |
| gh CLI | Item 2 | yes, logged in as `halfb00t` (ssh) | -- | the human pushes anyway (D-15) |
| Docker daemon | Item 6 | yes (OrbStack), no `spur` image yet | Client 29.8.2 | `make test-image` builds it |
| Network / GitHub Actions | Item 2 | the human's push | -- | D-16 |

**Missing dependencies with no fallback:** none. The only external actor is the human's push and PR (Items 2 and the D-07 CI confirm).
**Host:** Apple M5 Max, 18 CPUs, `PYTEST_WORKERS` = 8, 1-minute load 3.4-4.2 during research `[MEASURED: uptime]`. Record load per run as D-04 and D-09 require.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 + pytest-xdist 3.8.0 + pytest-cov 7.1.0 (`[VERIFIED: pip list]`) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (`--strict-markers --strict-config`, `filterwarnings = error`) |
| Quick run command | `.venv/bin/python -m pytest tests/test_hooks.py -n0 --no-cov -q -p no:cacheprovider` (0.60 s, 7 passed) |
| Full suite command | `make verify` (the gate; 1318 tests collected today `[MEASURED: --collect-only]`) |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-hook-pin-ignores-caller-args | Pin passes with `PYTEST_ARGS` set (env and make command-line) | unit | `PYTEST_ARGS="--ignore=tests/test_browser.py" .venv/bin/python -m pytest tests/test_hooks.py -n0 --no-cov -q` and `make test PYTEST_ARGS="--ignore=tests/test_browser.py tests/test_hooks.py -n0 --no-cov -q"` | new tests in `tests/test_hooks.py` -> Wave 0 |
| REQ-twin-selectors-race-fixed | Zero requests from two pending picks, baseline after the link's STL request, settle past 350 ms | browser integration | `make test PYTEST_ARGS="tests/test_browser.py tests/test_browser_pins.py --no-cov -q"` | step exists; edit in place |
| REQ-tracker-flake-fixed-from-repro | No reentrant warning when GC is forced in the tracker lock after the producers | integration (subprocess) | `.venv/bin/python -m pytest tests/test_pool.py -n0 --no-cov -q -k forced_gc` | new test in `tests/test_pool.py` -> Wave 0 |
| REQ-hang-leaves-evidence | A stalled test names itself (id from `-v`, stacks from `faulthandler_timeout`) | manual-only (throwaway) | `make test PYTEST_ARGS="tests/test_zz_stall_probe.py -o faulthandler_timeout=5 --cov-fail-under=0"` | throwaway, never committed; the guard that stays is the pin asserting `-v`/`--durations` in the `test` recipe |
| REQ-test-image-runs-what-it-claims | `make test-image` passes; every skip is a named `--ignore` | integration (Docker) | `make test-image` | recipe exists; pin to extend in `tests/test_hooks.py` |
| REQ-ubuntu26-preclassified | Three jobs ran on `ubuntu-26.04`; logs classified | manual-only (CI, human push) | `gh run view <id> --log` per job | none; the artifact is the `bench/RESULTS.md` record |

### What failure looks like (so each guard is checkable)
| Guard | Red looks like |
|---|---|
| Hook pin, env/cmdline form | `assert "--ignore=" not in whole_pytest` failing at `tests/test_hooks.py:120` with `PYTEST_ARGS` set `[MEASURED]` |
| Twin step, old shape under a parked `/api/info` | `AssertionError: twin selectors: 1 request(s) sent by two pending picks` |
| Twin step CX-05 control | a stray `input` event after the picks: old assert-immediately passes, new settle assert fails with the same message |
| Forced-GC gate test, unfixed `test_pool.py` | subprocess exit 1, `FAILED tests/test_pool.py::test_a_closed_pool_never_builds_a_replacement_worker`, five `ResourceTracker called reentrantly` lines `[MEASURED]` |
| `-v`/`--durations` pin | `-v` missing from the `test` recipe line, or present in `test.fast`'s |
| Image pin | an `--ignore`, mount or `PYTHONPATH` that differs from the committed exact sets |
| Stalled test | none (evidence, not a failure): `Timeout (0:00:05)!` plus a `File ".../test_zz_stall_probe.py", line N in test_stalls` frame, with the id in the `-v` start line |

### Measurement records that land in `bench/RESULTS.md` (one new section, appended, `## Gate fails with a cause (Phase 26)`)
Each with command, host (`bench.machine_facts()` line: 18 CPUs, arm64, Apple M5 Max), 1-minute load before -> after, tool versions (pytest 9.1.1, xdist 3.8.0, cov 7.1.0, CPython 3.12.15), effective `-n`, HEAD sha:
1. **26-0a Hook-pin red/green** (both forms, before and after).
2. **26-0b Ubuntu 26 pre-classification**: run ids, `Image:` line and version, per-job result, install seconds, renderer, `-n`, wall, classification of any red (known main red vs new).
3. **26-0c Twin selectors**: old step red under parked `/api/info` (failure text), new green, CX-05 control red/green, 20 local runs count, first post-merge `main` run id and result.
4. **26-0d Flake**: stdlib reproduction (n of n), forced-GC arm A/B/C table (n of 3 each), gate-test cost (seconds), 10+10 interleaved run table with signature-classified reds, cap/arms/stop rule (committed before), "consistent, not conclusive" sentence.
5. **26-0e Hang evidence**: local `--durations` top 25, chosen timeout and reason, CI `--durations` and the x2 rule outcome, the throwaway-stall log path and quoted dump, 3+3 gate-cost table with loads and the 5 % reading.
6. **26-0f test-image**: first-run whole red set (before any fix) with each red classified, the fix, the passing run, per-skip reasons.

### Sampling Rate
- **Per task commit:** the quick command for the touched file (`tests/test_hooks.py` 0.6 s; `tests/test_pool.py` about 20 s at `-n0 --no-cov`; the browser file about 45 s via `make test PYTEST_ARGS=... --no-cov`).
- **Per wave merge:** `make verify`, result line recorded.
- **Phase gate:** `make verify` green and `git diff --exit-code v0.5 -- tests/regression/` empty; `git diff v0.5 -- src/spur/pool.py` empty; no `filterwarnings` line changed (ROADMAP phase-close and SC3).

### Wave 0 Gaps
- [ ] New env-form tests in `tests/test_hooks.py` (red first, both shapes).
- [ ] The forced-GC subprocess gate test in `tests/test_pool.py` (red first against the unfixed file).
- [ ] `investigation/` directory under the phase for stall, test-image, CI and acceptance logs.
- [ ] A committed acceptance protocol (cap, arms, stop rule) before the first interleaved run (REQUIREMENTS rule).
- [ ] Framework install: none.

## Security Domain

`security_enforcement` is absent from `.planning/config.json`, so it is treated as enabled. This phase changes tests, a Makefile recipe, an ini key and CI scratch config; it adds no endpoint, input parser or secret.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | -- |
| V3 Session Management | no | -- |
| V4 Access Control | no | -- |
| V5 Input Validation | no (no new input surface; the subprocess gets fixed argv and test ids) | fixed argv list, no shell, no f-string into `-c` |
| V6 Cryptography | no | -- |

### Known Threat Patterns
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Mounting the repo into a root container (`--user root` in `test-image`) | Tampering | the new `bench/` and `scripts/` mounts are `:ro`, like `src`, `tests`, `pyproject.toml` (`Makefile:220-222`) |
| Throwaway PR running the full workflow on `pull_request` | Elevation | same-repo PR, no new secrets, `runs-on` only; closed unmerged; `--with-deps` already uses sudo on the runner and that was read green on 24.04 (`bench/RESULTS.md:4923`) |
| Shell injection through `PYTEST_ARGS` | Tampering | not a new risk: the variable is already interpolated by make into a recipe; the fix removes it from the test child's env |

## Project Constraints (from CLAUDE.md)

- **The gate is `make verify`.** Nothing is "done" until it passes; state the command and the result line in the reply. `make check` adds Docker checks.
- **Stop and ask first** when: an architectural claim isn't in the decision log; a locked decision looks wrong; library behaviour is unverified after a real check; evidence conflicts (doc vs code vs decision); a destructive operation is involved; a choice trades stability for speed. Ask format: trigger, 2-3 options, recommendation, wait. (The `make test-image` unexpected-red case in D-11 is this rule.)
- **Decisions** are logged as `Lxx` in `docs/architecture/decision_log.md`; ground claims in evidence; flag guesses as `ASSUMPTION:` and surface before acting.
- **Standing rules:** a printed number is a number someone cuts metal to (L08); a parameter the user did not set must never silently change the part (L05). Neither touched by this phase; `git diff --exit-code v0.5 -- tests/regression/` empty at close.
- **Keep it simple and small:** surgical edits; one concern per commit; commits are semantic checkpoints; Conventional Commits, normal prose (not caveman); commit trailer per the harness attribution reminder.
- **Finishing work:** new behaviour ships with its tests in the same change; performance claims are measured and recorded, not estimated; no `TODO`, `pass`, unreachable branches (`make verify` greps for markers; do not write the words TODO/FIXME/XXX/HACK/NotImplementedError even in comments or strings under `*.py`, `*.js`, `*.sh`).
- **Debt and ideas:** one file per item in `docs/<dir>/`, add an INDEX row in the same commit; on fixing debt flip `Status: resolved`, add the commit sha, `git mv` to `docs/tech_debt/resolved/`, move the INDEX row, all in the fix commit. Before the final reply state whether any item was filed and its path. Retire here: hook-pin (nice), twin-selectors (must), resource-tracker (must), test-image (nice). Keep active: hang (gains runbook), Ubuntu 26 (Phase 29). The deferred `test-image`-in-CI idea goes to `docs/ideas/`.
- **Tools:** reuse `make` targets; user-facing text terse; code in the ponytail style (simplest thing that works).
- **Code style (`docs/CODING_VALUES.md`):** comments explain why and carry the measurement or constraint; match the existing comment density in the files touched; English throughout.
- **Cross-CLI review:** whoever wrote the diff does not review it.

## Sources

### Primary (HIGH confidence) - opened or run this session
- `Makefile` 1-260 (recipes `test`, `test.fast`, `test-image`; comments at 156-175, 217-226)
- `tests/test_hooks.py` 1-260; `tests/test_browser.py` 25-45, 150-290, 570-610, 655-760, 1500-1640; `tests/browser_session.py` 36-54, 762-777; `tests/test_pool.py` 1-60, 143-207, 527-642
- `src/spur/static/app.js` 240-330, 395-435, 596-645
- `pyproject.toml`; `.github/workflows/ci.yml`; `.github/workflows/required-jobs.txt`; `Dockerfile`; `.dockerignore`
- `.planning/research/STACK.md` 1-215; `.planning/REQUIREMENTS.md`; `.planning/ROADMAP.md` Phase 26; `26-CONTEXT.md`
- `docs/tech_debt/active/` hook-pin, twin-selectors, resource-tracker, hang, test-image items; `docs/tech_debt/INDEX.md`
- `bench/RESULTS.md` 4857-4935, 5545-5760; `docs/architecture/decision_log.md` L43
- `21-REVIEW.md:150-170`, `21-REVIEW-DISPOSITION.md`, `24-REVIEW-DISPOSITION.md:45-70`
- Probes (session scratchpad, no tracked file touched): `rt_repro.py` (5 of 5), `gcrun.py` arms A/B/C, `ini/` (`--strict-config` and dump shape), `probe.py` / `probe2.py` / `probe3.py` (Playwright), scratch Makefile (recipe env), `pytest --cov-fail-under=0`
- `gh run list --branch main`, `gh auth status`, `docker ps`, `docker image ls spur`, `getconf`, `uptime`

### Secondary (MEDIUM confidence)
- `.planning/research/STACK.md` section 3 (Ubuntu 26.04 announcement and container evidence), carried as `[CITED]`, not re-fetched

### Tertiary (LOW confidence)
- None used as a basis for a recommendation; unverified items are in the Assumptions Log.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - installed versions read from the venv; no new packages.
- Architecture / mechanics: HIGH for Items 1, 4, 5 (re-run on this host); MEDIUM-HIGH for Item 3 (mechanism read in `app.js` and probed on a stand-in page; the real-app red is the plan's first task); MEDIUM for Item 6 (static prediction) and Item 2 (nothing runs yet).
- Pitfalls: HIGH - four of six were hit and measured while researching.

**Research date:** 2026-10-15
**Valid until:** 2026-10-19 for Item 2 (the rollout starts); 30 days for the rest (pinned toolchain, L23 / REQUIREMENTS hold it fixed).
