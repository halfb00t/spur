# Stack Research

**Domain:** v0.6 "Clean Ledger" -- the tooling facts a debt sweep leans on (CPython 3.12 `multiprocessing`, pytest / pytest-xdist / pytest-cov, Playwright, GitHub Actions). No product feature, so this is not a stack-selection document: it says which versions are pinned, which behaviours the fixes depend on, and what NOT to add.
**Researched:** 2026-10-15
**Confidence:** HIGH on the resource-tracker mechanism and the evidence flags (measured here, mechanism read in the installed CPython source); MEDIUM on Ubuntu 26.04 (measured in a container, never on a real runner); LOW on the cause of the 98 % hang (no reproduction exists, and this document does not claim one).

**Evidence tags used on every claim:**
- **MEASURED** -- I ran it on 2026-10-15 (macOS arm64 host, CPython 3.12.15, pytest 9.1.1; or an `ubuntu:26.04` container, x86_64). Counts are given.
- **READ** -- read in installed source, the repo, an official page or an upstream issue. Source named.
- **UNVERIFIED** -- inference or assumption; do not act on it without a check.

---

## Decisions in one place

| # | Decision | Why |
|---|----------|-----|
| 1 | Add **no** runtime dependency and **no** new dev dependency. | Every fix below is reachable with pytest 9.1.1's own flags, the stdlib and `make`. `pytest-timeout` is not needed (pytest >= 9.0 ships `faulthandler_exit_on_timeout`). |
| 2 | The reentrant `resource_tracker` warning is a **test-hygiene** defect (cyclic garbage holding executor semaphores), not xdist, not coverage and not `src/spur`. Fix it in `tests/test_pool.py`. | MEASURED: three tests leave one executor's 5 semaphores to the cyclic GC in 4 of 4 runs; a 10-line forced-GC script reproduces the exact 5-warning chain on demand; `--no-cov` reproduces it too. |
| 3 | The fallback trigger's whole-suite `--cov` vs `--no-cov` loops are **no longer the right experiment**. A captured, deterministic reproduction exists (below); verify the fix against it and against a before/after loop of the two process-spawning files. | The 2026-10-09 isolation (0 of 60) failed to separate the arms because the garbage only matters when a GC pass lands inside a microsecond lock window; the mechanism is independent of both. |
| 4 | Hang evidence = `-v` + `--durations` on the gate recipe and `faulthandler_timeout` in `pyproject.toml`. `faulthandler_exit_on_timeout` is a **separate human decision** (it turns a hang into a named failure but is a gate-semantics change and floors `pytest` at 9.0). | MEASURED on xdist + cov. Dump-only is pure evidence capture, which is what the debt file asks for; exit-on-timeout is a fix and L08 says no fix without a reproduction. |
| 5 | Do **not** pin `ubuntu-24.04` pre-emptively. Pre-classify Ubuntu 26.04 **now** on a throwaway branch with `runs-on: ubuntu-26.04`; do not wait for 2026-10-19. | The label exists today; the migration rolls out over a month, so "the first run that names Ubuntu 26" is not a clean date gate. Container evidence says the Playwright install and the browser test pass. |
| 6 | Hold `playwright==1.63.0`. Do not take 1.64.0 (released 2026-10-13) in a debt sweep. | A bump changes the headless-shell revision (1243 -> ?), invalidates the `$(BROWSER)` stamp and the canvas-PNG bar read on 153.0.8010.12. 1.63.0 already supports Ubuntu 26.04. |

---

## Recommended Stack

### Core Technologies (already pinned or installed -- nothing new)

| Technology | Version (this repo) | Latest on PyPI 2026-10-15 | Role in this milestone | Verdict |
|------------|---------------------|---------------------------|------------------------|---------|
| CPython | 3.12.15 local (Homebrew); 3.12.14 on the Ubuntu 24.04 runner; Ubuntu 26.04 runner image caches 3.12.14 (READ, runner-images `Ubuntu2604-Readme.md`) | -- | The reentrancy is in its stdlib. 3.12 is **security-only** (READ, devguide.python.org/versions): no upstream fix will land. | Stay on 3.12 (L23). Work around in tests. |
| pytest | 9.1.1 installed; `pyproject` floor `pytest>=8` | 9.1.1 (2026-06-19) | `faulthandler_timeout`, `faulthandler_exit_on_timeout` (>= 9.0.0), unraisable-exception plumbing | Keep. Raise the floor to `pytest>=9` **only if** `faulthandler_exit_on_timeout` is adopted (see below). |
| pytest-xdist | 3.8.0 | 3.8.0 (2025-07-01) | `-n 8` scheduler; execnet 2.1.2 underneath | Keep. |
| pytest-cov | 7.1.0 (coverage 7.16.2) | 7.1.0 / 7.16.2 | `--cov`, `[tool.coverage.run] concurrency = ["multiprocessing","thread"]`, `sigterm = true` | Keep. Not implicated in the flake (MEASURED, below). |
| Playwright (Python) | `==1.63.0` exact in `[dev]` (READ `pyproject.toml`), driver `playwright-core 1.63.0`, headless shell revision 1243 = Chrome 153.0.8010.12 | **1.64.0 (2026-10-13)** | Browser test on Linux and macOS | Hold. |
| GitHub `ubuntu-latest` | Ubuntu 24.04 until the migration | -- | `ci.yml` has three jobs on `ubuntu-latest` | Pre-classify on `ubuntu-26.04`. |

### Supporting Libraries

None added. `pytest-timeout 2.4.0` (2025-05-05) exists and would also work with xdist, but it is a new dev dependency that duplicates `faulthandler_exit_on_timeout` on pytest 9. Its compatibility with pytest 9.1.1 was not checked (UNVERIFIED) -- one more reason not to reach for it.

### Development Tools (flags and config this milestone should use)

| Tool | Purpose | Notes |
|------|---------|-------|
| `-o faulthandler_timeout=N` / `[tool.pytest.ini_options] faulthandler_timeout = N` | Dump every thread's stack of any test (setup + call + teardown) still running after N s | MEASURED under `-n 2` and `-n 2 --cov`: prints `Timeout (0:00:02)!`, the worker's thread stacks, and `File ".../test_hang.py", line 6 in test_slow`. Fires **once** per test (no repeat), does not kill. Worker stderr reaches the terminal even though capture is on (pytest dup()s fd 2 at configure -- READ `_pytest/faulthandler.py`). The frame shows the function, not the parametrize id, so pair it with `-v`. |
| `-v` | Test id on start **and** on finish | MEASURED under `-n 2`: the controller prints `tests/x.py::name ` when a test starts (no worker id) and `[gwN] [ 71%] PASSED tests/x.py::name` when it ends. In-flight set = started minus finished. Full 1318-test `-n 8` run: 175 KB of log. |
| `--durations=25` | Slowest 25 test phases | Printed at the end only -- **lost if the run hangs**. It records the sizing data for N, not the hang. |
| `make test PYTEST_ARGS="-v --durations=25"` | The invocation to use | `PYTEST_ARGS` comes last in the recipe (READ `Makefile`). **Never run `.venv/bin/python -m pytest` directly for evidence runs:** MEASURED, the browser test then fails (`Executable doesn't exist at ~/Library/Caches/ms-playwright/...`) because `make` is what exports `PLAYWRIGHT_BROWSERS_PATH=$(VENV)/ms-playwright`. |
| `python -X dev`, `PYTHONFAULTHANDLER` | -- | Not needed: pytest's faulthandler plugin is on by default (READ). |

---

## 1. The `resource_tracker` reentrant-cleanup warning

### Mechanism (READ + MEASURED)

1. `ProcessPoolExecutor(mp_context=spawn)` builds its call queue and result queue at construction. That is **five** named semaphores (`SemLock`), each registered with `multiprocessing.resource_tracker` and each given a `util.Finalize(self, SemLock._cleanup, ...)` (READ `multiprocessing/synchronize.py` lines 79-88).
2. `SemLock._cleanup` calls `resource_tracker.unregister`, which goes `_send -> ensure_running` and takes the tracker's `threading.RLock`.
3. `ensure_running` and `_stop_locked` refuse a nested entry: `if self._lock._recursion_count() > 1: raise ReentrantCallError` (READ `resource_tracker.py` in 3.12.15, comment `gh-109629`: "an explicit call to the ResourceTracker gets interrupted by a garbage collection, invoking a finalizer ... that itself calls back into ResourceTracker"). `_send` catches it and calls `warnings.warn("ResourceTracker called reentrantly for resource cleanup, which is unsupported. The semaphore object ... might leak.")`.
4. Under `filterwarnings = ["error"]` that `warn` raises inside a `Finalize` callback; the interpreter reports it as an unraisable exception; pytest 9.1.1 turns it into `PytestUnraisableExceptionWarning` and, with five of them, an `ExceptionGroup` of five at the end of whichever test's phase was running (READ `_pytest/unraisableexception.py`). **Five warnings = one executor's worth of semaphores** -- the count in occurrences 2, 3 and 5 of the debt file.
5. It needs three things at once: an executor that became **cyclic garbage** (so only the cyclic GC frees it, not refcounting); an automatic GC pass that happens to run while some thread is **inside** the tracker's lock (a window of a few bytecodes in `ensure_running`); and `filterwarnings = error`. Without the third, the same event is one `UserWarning` line per semaphore and nothing fails (READ halfb00t/screw PR #7).

### Why the test that fails is never the test that caused it (MEASURED)

pytest 9.1.1 calls `gc.collect()` only at `pytest_unconfigure` (session end); per-phase it just drains an already-queued deque (READ `unraisableexception.py` lines 146-188). So cyclic garbage lingers until an automatic pass, and whichever test is running then is blamed. That is why the five occurrences name five different tests (`test_a_dying_worker...`, `test_three_same_tick...`, `test_health_reports_pool_state`, ...).

**Producer tests, MEASURED** with a diagnostic pytest plugin (kept in the scratchpad, not committed: it stamps each `SemLock` with the test that created it and records which are freed inside a `gc.callbacks` pass): `tests/test_pool.py` alone, `-n0 --no-cov`, 4 runs of 4. In every run exactly three tests left five semaphores to the cyclic GC:

- `test_a_wedged_build_is_terminated_and_its_worker_replaced`
- `test_a_stale_executor_timeout_is_a_build_timeout_not_an_attribute_error`
- `test_three_same_tick_same_slot_timeouts_each_end_in_a_documented_refusal`

All three do `manager = executor._executor_manager_thread`, then `with pytest.raises(BuildTimeout): asyncio.run(...)`. The cycle is the held exception/traceback/frame plus `manager`, which holds the executor's queues. `src/spur/pool.py` is **not** implicated: no production code path keeps these references.

### A captured reproduction exists (MEASURED) -- this satisfies "never fixed without one" (L08)

```python
# rt_repro.py -- ~12 lines, stdlib only. GC is forced inside the tracker lock the way an
# automatic pass would land there.
import gc, sys, multiprocessing as mp, warnings
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import resource_tracker as rt
ctx = mp.get_context("spawn")
ex = ProcessPoolExecutor(max_workers=1, mp_context=ctx)   # 5 named semaphores
ex.me = ex; del ex                                        # cyclic garbage
orig = rt.ResourceTracker._check_alive
def noisy(self): gc.collect(); return orig(self)          # runs under the RLock
rt.ResourceTracker._check_alive = noisy
warnings.simplefilter("error"); got = []
sys.unraisablehook = lambda a: got.append(repr(a.exc_value))
ctx.Lock()                                                # register -> ensure_running -> _check_alive
print(len(got))
```

Result: **5 unraisable `UserWarning("ResourceTracker called reentrantly ...")` in 4 of 4 runs**; with `gc.collect()` called *before* the patch (garbage freed outside the lock) or without the cycle: **0**. This is the whole bug in miniature and it is independent of xdist, pytest-cov and the OS.

### The fallback trigger's question is answered (MEASURED)

"Does `-n 8 --no-cov` also fail?" Yes. In an `ubuntu:26.04` container (CPython 3.12.15, x86_64), one whole-suite `-n 8 --no-cov` run failed `tests/test_pool.py::test_three_same_tick_same_slot_timeouts_each_end_in_a_documented_refusal` with the five-warning chain (1 failed, 1315 passed), and a two-file loop (`tests/test_pool.py tests/test_api.py`, `-n 8 --no-cov`) failed 1 of 4. So coverage's `multiprocessing` concurrency is **not required**. The same two-file loop read 0 of 60 on macOS on 2026-10-09: the rate is host- and timing-dependent, which is exactly why isolation loops on the dev host could not see it.

### Fix options, ranked

Acceptance harness (MEASURED, 6 lines, loaded with `-p gclock`, not committed): patch `ResourceTracker._check_alive` to call `gc.collect()` first. It runs under the tracker lock on every register/unregister, so any cyclic garbage still holding a semaphore is finalised re-entrantly, deterministically.

| Arm | Change (in `tests/test_pool.py` only) | Forced-GC-in-lock, macOS, `test_pool.py`, `-n0 --no-cov`, 3 runs | Natural loop, `ubuntu:26.04` container, `test_pool.py` + `test_api.py`, `-n 8 --no-cov`, 10 interleaved rounds | Cost |
|-----|------|------|------|------|
| A | none (baseline) | **FAILED 3 of 3**, always `test_a_closed_pool_never_builds_a_replacement_worker` -- a *victim*, not a producer | **1 of 10** (`test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced`, five reentrant lines -- the same victim as CI occurrence 3). Earlier in the same container: 1 of 4, and 1 of 1 whole-suite | -- |
| B | module-level `@pytest.fixture(autouse=True)` whose teardown calls `gc.collect()` (4 lines) | 0 of 3 | 0 of 10 | about 10 ms per test; the 20-test file read 19.7 s -> 19.9 s |
| C | `del manager` after the last use in the three producer tests (3 lines, what halfb00t/screw PR #7 did) | 0 of 3 | 0 of 10 | none |

Read the natural-loop column as consistent, not conclusive: at the observed rate (about 1 in 5-10 in the container) 0 of 10 has a 15-30 % chance by luck alone. The forced-GC column is the proof, because it removes the luck. With arm B the producers' garbage is freed in their own `[teardown]` at `gen=2` with the tracker lock not held (MEASURED with the creator/free probe, 3 of 3 runs); with arm C the probe sees no semaphore freed by the cyclic GC at all (3 of 3).

**Recommendation: B as the fix, C as optional root-cause cleanup.** B is four lines, covers any future test that keeps the `manager` / `pytest.raises` pattern, and confines the cost to the one file that spawns executors (the probe saw `test_api.py`'s lifespan pools produce no cyclic semaphores). C alone depends on remembering the pattern. Neither touches `src/spur/`. Retire the debt item in the commit that lands the fix, quoting the forced-GC result and the 3-of-3 / 0-of-3 table.

### What NOT to do for this item

| Avoid | Why | Instead |
|-------|-----|---------|
| `filterwarnings = ["ignore:ResourceTracker called reentrantly"]` or `ignore::pytest.PytestUnraisableExceptionWarning` | Hides a symptom whose cause is now located; the debt file already forbids the blanket form. | Break the cycle or collect it outside the lock. |
| `gc.set_threshold(...)` stress as a reproducer | MEASURED 0 of 6 failures (threshold0 = 5 and 50, three runs each, `test_pool.py`, `-n0`): a tight threshold frees the garbage *before* the tracker is next entered, so it hides the bug. | The forced-GC-inside-the-lock script above. |
| `shutdown(wait=True)` in `BuildPool` | The cycle is in test locals, not in the pool; production would pay a join for nothing and the wedged-worker debt item (a build holding exit) would get worse. | Leave `pool.py` alone. |
| Upgrading Python for the upstream fix | The fix (cpython PR #131787, `gh-131788`) merged to main 2025-08-13 and to 3.14 on 2025-10-17; the 3.13 backport was **reverted** (regressions in loky/joblib); 3.12 was not backported and is security-only (READ). Also `cadquery-ocp` has no wheels past 3.12 (L23). | Fix in tests. |
| Moving the pool to `forkserver`/`fork` | Different start-method semantics, D-02 and the spawn rationale (`pool.py` line 35), and the tracker is shared by every start method. | Keep `spawn`. |

---

## 2. The whole-suite hang at ~98 % (evidence capture, not a fix)

### What the tooling says about where it can and cannot be (READ unless tagged)

- **A hang in worker exit is bounded.** `NodeManager.teardown_nodes` calls `group.terminate(EXIT_TIMEOUT)` with `EXIT_TIMEOUT = 10` and execnet then kills the popen gateway (READ `xdist/workermanage.py:45,116`, `execnet/multi.py:210-245`). A wedged `BuildPool` child holding the interpreter's exit (the wedged-worker debt item, 8.10 s measured) cannot hold an xdist worker beyond ~10 s. So a 600 s silence is **not** an exit hang of one worker. It is a test that never returned, a stall of the controller, or of the whole host. (UNVERIFIED inference from the source; no run observed it.)
- **Arithmetic from the debt file (UNVERIFIED):** 94 % line (1147 reported) plus 50 dots = about 1197 of 1220 reported, so about 23 outstanding. xdist `load` keeps at least two tests queued per worker (READ `xdist/scheduler/load.py:195`), so the normal tail of an 8-worker run is about 8 x 3 = 24 in flight or queued. That fits *every worker still holding tail items when output stopped* -- i.e. a global stall -- better than a single stuck worker, which would strand about 3. The evidence capture below is designed to tell these apart.
- **Unbounded waits exist in the suite (READ).** `tests/test_pool.py` has 10 `submit(os.getpid).result()` calls with no timeout (lines 88, 129, 157, 205, 233, 446, 492, 554, 608, 640) on a freshly spawned worker. A spawn child that never finishes `_warm` hangs the test forever instead of failing. A candidate location, not a finding. `faulthandler_timeout` would show `concurrent/futures/_base.py ... wait` as the top frame.
- **Coverage defers SIGTERM (READ `coverage/control.py:655-663,756-762`).** With `sigterm = true` the child installs a *Python-level* SIGTERM handler; a worker blocked inside a long OCCT C++ call does not run it until the call returns, so `proc.terminate()` in `BuildPool` is not immediate under `--cov`. No current test terminates a real build (the wedged tests sleep in Python), so this is latent. UNVERIFIED as a cause.

### Recommended evidence capture (all zero-dependency)

```toml
# pyproject.toml [tool.pytest.ini_options]
faulthandler_timeout = 120          # dump-only
```

```make
# Makefile, `test` recipe only (not test.fast): ids on start and finish, durations at the end
$(PY) -m pytest -n $(PYTEST_WORKERS) --cov --cov-report=term -v --durations=25 $(PYTEST_ARGS)
```

**Why 120 s.** MEASURED slowest test phases in one whole-suite `-n 8 --cov` run on the 18-CPU M5 Max host at load about 5 (200.0 s wall, 1317 passed): 25.77 s (`test_every_feature_proof_holds_..._trochoid-d-flat-spokes`), 22.24 s, 20.52 s, then a 10-15 s plateau. The browser test took 43.8 s alone and 55.7 s inside the `-n 8` whole-suite run in the 26.04 container under x86 emulation. The last CI whole-suite run took 401.82 s on 4 vCPUs (READ, run 38680454993), about 2x the local wall, so about 52 s for the slowest test there. 120 s is about 2.3x that; a dump that fires on a healthy test is noise, so err high. Re-read the number from the first `--durations` output on CI before keeping it (UNVERIFIED for CI).

**Exit-on-timeout (human's call).** MEASURED under `-n 2 --cov` with `-o faulthandler_exit_on_timeout=true`: the stuck test's worker dumps its stacks and exits; xdist prints `[gw0] node down: Not properly terminated`, fails the test with `worker 'gw0' crashed while running 'test_hang.py::test_slow'`, runs the rest, and exits non-zero. Side effect: pytest-cov reports `failed workers ... failed to return coverage data` and the total drops (67 % in the toy run), so the coverage floor adds a second failure line. This is the built-in equivalent of `pytest-timeout`'s `thread` method and is what delivers the milestone sentence "fails with a cause, never hangs". It needs `pytest>=9.0.0` (READ pytest changelog, issue #13678): with `--strict-config` an older pytest rejects the unknown ini key, so the `[dev]` floor must go from `pytest>=8` to `pytest>=9` in the same commit. Recommended order: ship dump-only now (evidence), decide exit-on-timeout after the first captured hang or when the human wants the gate to stop being able to stall.

**Not covered by `faulthandler_timeout` (READ `_pytest/faulthandler.py`):** the window after the last item and before worker exit (the timer is armed per item inside `pytest_runtest_protocol`). For that window the operator step is: `kill -ABRT <pid>` on the stalled xdist worker -- pytest enables `faulthandler`, which handles SIGABRT and prints all thread stacks (READ Python docs; **UNVERIFIED here** -- not run, because on macOS it writes a crash report that would muddy the open `xdist-worker-segfaults-in-occt-at-exit` investigation). On Linux CI no report is written.

**Optional, only if `-v` proves insufficient:** a ~10-line `pytest_runtest_logstart` / `pytest_runtest_logreport` hook in `tests/conftest.py` that appends `HH:MM:SS.mmm START|END nodeid gwN` to a file and flushes. the controller sees both events (MEASURED: `-v` start lines and finish lines are printed by the controller), so it gives timestamps -- which `-v` lacks -- and survives a SIGTERM. Not recommended by default: more code in the gate than the debt item justifies.

### What NOT to do for this item

| Avoid | Why | Instead |
|-------|-----|---------|
| `pytest-timeout` | New dev dependency for a capability pytest 9 already has. | `faulthandler_timeout` (+ `faulthandler_exit_on_timeout`). |
| `--dist worksteal` | UNVERIFIED benefit; changes tail scheduling and therefore the 300 s bar's measurement basis (L43). | Leave `load`. |
| Guessing a fix (e.g. disabling `sigterm`, `shutdown(wait=True)`) | L08: no reproduction, no fix. | Capture and re-defer with the measurement. |
| `-p no:faulthandler`, `-s`, `--capture=no` | Removes the very dump this relies on or interleaves worker output. | Defaults. |

---

## 3. Ubuntu 26.04 and Playwright

### What GitHub has announced (READ)

- Announcement 2026-09-17 (`github.blog/changelog/2026-09-17-ubuntu-26-generally-available-and-latest-migration`, `actions/runner-images#14748`): `ubuntu-latest` moves from 24.04 to 26.04 **gradually from 2026-10-19, complete by 2026-11-19**. So the debt item's "first CI run after 2026-10-19 whose `Set up job` names Ubuntu 26" is a window of a month in which runs may land on either image; one green run on 24.04 after the 19th proves nothing.
- Labels `ubuntu-26.04` and `ubuntu-26.04-arm` are generally available now; `ubuntu-24.04` stays available as the pin. `halfb00t/spur` is public (READ `gh repo view`), so standard runners are free.
- Image `ubuntu-26.04` version `20260927.149.1`: kernel 7.0.0-1012-azure; system Python 3.14.4 with cached 3.10.21 / 3.11.16 / **3.12.14** / 3.13.15 / 3.14.7; Node system 24.21.0 (cached 22.23.3); Docker 29.4.2 and Buildx 0.37.1 (24.04 image: Docker 28.0.4); Chrome 154, Xvfb present (READ `Ubuntu2604-Readme.md`, `runner-images#14226` "Breaking changes"). The default Python moves 3.12 -> 3.14, which does not matter here because `setup-python@v5` puts 3.12 first and `make verify PYTHON=python` uses it.
- `ci.yml` job names are `test (3.12)`, `vendor-bundle`, `image`; `required-jobs.txt` and `tests/test_pr_land.py` constrain **names**, not `runs-on` (READ; no `runs-on` match in the test). A branch that changes only `runs-on` leaves the three required-check names unchanged.

### Playwright 1.63.0 on 26.04

- Official support arrived in **1.61.0** (READ microsoft/playwright#40117, PR #41290; 1.59.1 failed with "does not support chromium on ubuntu26.04-x64"). The pinned driver names `ubuntu26.04-x64` / `-arm64` and its `isOfficiallySupportedPlatform` is true for Ubuntu 26.04 (READ `playwright/driver/package/lib/coreBundle.js:8536`).
- The `--with-deps` apt set for chromium is **identical** between `ubuntu24.04-x64` and `ubuntu26.04-x64` in 1.63.0: 21 chromium libraries (`libasound2t64`, `libatk-bridge2.0-0t64`, `libgbm1`, `libnss3`, ...) plus the same `tools` list (`xvfb`, fonts) (READ, set-diff of the two arrays = empty). The headless shell download is the same `linux64/chrome-headless-shell-linux64.zip`, Chrome 153.0.8010.12 (READ, `browsers.json`, `coreBundle.js:32913`).
- Non-root `--with-deps` runs `sudo -- sh -c "apt-get update&& apt-get install ..."` (READ `coreBundle.js:32336-32341`); `install-deps --dry-run` simulates the apt install and exits non-zero if a package is missing (READ help text).

### Container evidence (MEASURED, 2026-10-15; caveat: a container, not the runner image)

Setup: `ubuntu:26.04` (26.04.1 LTS, x86_64 under emulation, glibc 2.43, **uutils coreutils 0.10.0**, procps-ng 4.0.4, `sudo` 1.9.17p2), non-root user `ci` with passwordless sudo, CPython 3.12.15 from `uv`, `pip install -e '.[dev]' -c requirements.txt` (the project's exact install shape, L43), tree from `git archive HEAD` (so no `.git`).

| Check | Result |
|-------|--------|
| `playwright install --with-deps --only-shell chromium` as root | OK, 56 s (emulated), same Chrome Headless Shell 153.0.8010.12 and FFmpeg 1011 |
| same, as non-root through `sudo` | OK, 52-57 s, three repeats |
| `playwright install-deps --dry-run chromium` afterwards | `All system dependencies are installed.`, exit 0 |
| `chromium.launch()` + WebGL | version 153.0.8010.12; renderer `ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (Subzero) ...))` -- the same SwiftShader family the 24.04 runner draws on |
| `tests/test_browser.py` + `tests/test_browser_pins.py`, `-n0 --no-cov` | **5 passed in 45.07 s** (the browser test 43.8 s), including the canvas PNG bar |
| `ps -A -o pgid=,stat=,pid=` (the `group_members` call in `tests/browser_session.py`) | works on procps-ng 4.0.4 |
| Whole suite, `-n 8 --no-cov` | **3 failed, 1315 passed in 268.8 s** -- one is the resource-tracker flake (above); the other two are `tests/test_bench.py` tests that run `git rev-parse --short HEAD` and fail with exit 128 **because my tree had no `.git`** (an artefact of the setup, not of 26.04; it is also what `make test-image` would hit, see below) |

**Not proven by this:** the real runner image (it preinstalls a different package set -- on 24.04 the log shows nine Playwright libraries "already the newest version"), the 4-vCPU `-n 4` timing, Docker 29.4.2 in the `image` job, `docker/build-push-action@v6` on the new image, and the whole `test (3.12)` job with `--cov`. The remaining risk is concentrated in those, which is why the throwaway-branch run below is still worth doing.

### Recommended classification step (before 2026-10-19)

A throwaway branch that changes only `runs-on: ubuntu-latest` -> `ubuntu-26.04` on the three jobs, opened as a PR so `ci` runs; read the whole `test (3.12)` log (apt, WebGL, timing, `--durations`); close the PR unmerged. Keep the order the debt file asks for -- classify from the whole log before any fix. If it is red, `runs-on: ubuntu-24.04` is the documented fallback and the human's call. If green, record the image version and the install seconds under a new `bench/RESULTS.md` reading, then resolve the item once an `ubuntu-latest` run on the migrated image also reads green (the gradual rollout means the pre-classification does not replace that final reading).

### What NOT to do for this item

| Avoid | Why | Instead |
|-------|-----|---------|
| Pinning `ubuntu-24.04` now | Postpones the problem to the end of 24.04's life and hides the browser test's new-image risk. | Pre-classify; pin only if red. |
| Bumping Playwright to 1.64.0 to "be safe on 26.04" | 1.61+ already supports it; a bump moves the browser revision and the canvas bar. | Hold 1.63.0. |
| Adding a matrix leg `os: [ubuntu-24.04, ubuntu-26.04]` to `test` | Renames the required check (`test (3.12, ubuntu-26.04)`) and breaks `required-jobs.txt` / the branch ruleset. | A separate throwaway branch or workflow. |
| Installing the apt libraries by hand in `ci.yml` | `--with-deps` already installs the same 21 packages on both images. | Keep `BROWSER_INSTALL_ARGS: --with-deps`. |

---

## 4. Facts for the small items (no new tooling)

| Item | Fact | Tag |
|------|------|-----|
| Hook pin reads the caller's `PYTEST_ARGS` | GNU Make 4.4.1: a variable given on the command line is exported to recipes' environment, so `_make_env()` (which strips make's flags but not this variable) hands it to the test's own `make -n`. `PYTEST_ARGS=--ignore=tests/x make -n -o .venv/.browser verify` prints the flag (1 match); adding `PYTEST_ARGS=` on that command line: 0; `env -u PYTEST_ARGS`: 0. Either fix works; command-line `PYTEST_ARGS=` is the smaller diff. | MEASURED |
| Launch-failure message names the wrong stamp | `playwright install --only-shell chromium` on an already-installed shell takes **0.24 s** and exits 0, so the `$(BROWSER)` stamp saves nothing; running the install on every `make test` removes the stale-stamp failure class instead of improving a message. On Linux, `playwright install-deps --dry-run chromium` is the cheap way to tell "missing shared libraries" from "missing binary" for the message. (`--with-deps` is not cheap: it runs `apt-get update` under sudo, so CI should keep passing it once.) Without `PLAYWRIGHT_BROWSERS_PATH`, Playwright 1.63.0's error reads "Executable doesn't exist at ~/Library/Caches/ms-playwright/... Looks like Playwright was just installed or updated". | MEASURED |
| Group floor is not "two pool workers" | `BuildPool` picks a worker with `hash(p) % workers`. `GearParams` contains `str` fields, so the hash is randomised per process: for `teeth=21` and `teeth=22` six fresh interpreters mapped the pair to `(0,0)` once, `(0,1)` twice and `(1,0)` three times. The number of live workers after two builds is therefore 1 or 2, not a constant, and the live group is uvicorn + `resource_tracker` (started at pool construction, READ `ensure_running`) + 1 or 2 workers. The floor of 3 is correct as a non-vacuity bound; to make the member count deterministic, export `PYTHONHASHSEED=0` to the server subprocess. | MEASURED / READ |
| `stop_group` reads `ps` before it signals | `ps -A -o pgid=,stat=,pid=` is valid on BSD ps (macOS) and procps-ng 4.0.4 (Ubuntu 26.04). Nothing to add; the fix is ordering in `tests/browser_session.py`. | MEASURED |
| `make test-image` collects host-only tests | The image mounts only `src/`, `tests/`, `pyproject.toml` and has no `.git`. Two `tests/test_bench.py` tests call `git rev-parse --short HEAD` and fail with exit 128 without a repository (MEASURED in the 26.04 container, same shape as the image). Add them to the list with `tests/test_hooks.py` (Makefile, `.pre-commit-config.yaml`, `make`) and `tests/test_browser_pins.py` (`Dockerfile`). Use `--ignore=` per file as 21-06 did. | MEASURED / READ |
| `#root_shape=bogus` | The server already refuses it: `GET /api/info?root_shape=bogus` and `/api/model.stl?root_shape=bogus&quality=preview` both answer **422** `{"detail":[{"type":"literal_error","loc":["query","root_shape"],"msg":"Input should be 'radial' or 'trochoid'","input":"bogus","ctx":{"expected":"'radial' or 'trochoid'"}}]}`. The blank-select-and-default behaviour is client side (`app.js` omits the unset field), so the fix is `app.js`-only and reuses the existing 422 marking path. | MEASURED |
| `slug()` totality; failed-build name cache order | Pure test work; no tooling. `spur.app._EXPORTS` is a per-process dict, so xdist scheduling decides the order. | READ |

---

## 5. A finding that is not on the milestone's list

**CI run 38680454993** (`ci` on `main`, the v0.5 close squash `26ddd74`, 2026-10-15 04:14Z) **failed**: `1 failed, 1317 passed in 401.82s`, `tests/test_browser.py::test_the_shipped_viewer_in_a_real_browser - AssertionError: twin selectors: 1 request(s) sent by two pending picks; assert 266 == 265` (READ, `gh run view --log-failed`; no resource-tracker chain in the log). The v0.5 PR head `8f3531a` (run 38678227683) and the previous main commit `cbbe730` (run 38673037695) were green. It is a Linux-only extra network request in one browser step, step "twin selectors" (0.41 s), not a `ReentrantCallError`. It is **not filed** in `docs/tech_debt/` (INDEX read). It is a gate-reliability defect of the same kind as the milestone's goal and one more unexplained red on the required `test (3.12)` check; the roadmap should either add it to the gate-reliability phase or file it with the log. Evidence is the run log only; not reproduced here.

---

## Installation

```bash
# Nothing to install. No runtime dependency, no new dev dependency.
# Only conditional change, if faulthandler_exit_on_timeout is adopted:
#   pyproject.toml [project.optional-dependencies] dev:  "pytest>=8"  ->  "pytest>=9"
# The installed pytest is already 9.1.1, so this changes the floor, not the environment.
```

Pre-flight for the Ubuntu 26.04 pre-classification (Docker, any host):

```bash
docker run --rm -it ubuntu:26.04 bash        # then, as a non-root sudo user:
#   uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -e '.[dev]' -c requirements.txt
#   PLAYWRIGHT_BROWSERS_PATH=$PWD/.venv/ms-playwright .venv/bin/python -m playwright install --with-deps --only-shell chromium
#   .venv/bin/python -m pytest tests/test_browser.py tests/test_browser_pins.py -n0 --no-cov
# The tree must carry its .git, or two tests/test_bench.py tests fail on `git rev-parse`.
```

---

## Alternatives Considered

| Recommended | Alternative | When to use the alternative |
|-------------|-------------|-----------------------------|
| `faulthandler_timeout` (+ optional `faulthandler_exit_on_timeout`) | `pytest-timeout 2.4.0` | pytest pinned below 9.0, or per-test `@pytest.mark.timeout(n)` overrides are wanted. Not the case here. |
| Autouse `gc.collect()` / `del manager` in `tests/test_pool.py` | Strengthening `BuildPool` to drop executors without cycles | Only if a production path is ever shown to create the cycle. MEASURED: none does. |
| Forced-GC-in-lock script as the reproduction | Whole-suite `-n 8 --cov` vs `--no-cov` loops | Never as the *primary* experiment: at the observed rate (2 in 12 local whole-suite runs, about 1 in 4 on Linux two-file loops) separating two arms needs more than 20 runs each (about 70 min per arm at 200 s per run). Keep one before/after loop as acceptance, not as diagnosis. |
| Pre-classify on `ubuntu-26.04` via a throwaway PR | Wait for the first `ubuntu-latest` run on the new image | Acceptable only if the human prefers zero CI changes; the cost is learning about a red browser test from a red required check on an unrelated PR. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Any new dependency (`pytest-timeout`, `pytest-rerunfailures`, `pytest-randomly`, `py-spy`) | Zero-new-deps is a project value; reruns would hide the flake (the habit the gate exists to prevent). | pytest 9.1.1's own flags. |
| `pytest-rerunfailures` / retry loops in the Makefile | Converts a located bug into an invisible one. | Fix the cycle. |
| `PYTHONFAULTHANDLER`, `-X dev` globally | Already on / unneeded; `-X dev` adds ResourceWarning noise under `filterwarnings = error`. | Defaults. |
| Playwright 1.64.0 now | See decision 6. | Revisit after the milestone as its own measured change. |
| `runs-on: ubuntu-24.04` pin as a first move | See section 3. | Classify first. |

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| pytest 9.1.1 | `faulthandler_exit_on_timeout` | Needs pytest >= 9.0.0 (READ changelog). `--strict-config` rejects the key on older pytest. `pyproject` floor is currently `>=8`. |
| pytest-xdist 3.8.0 + execnet 2.1.2 | `faulthandler_timeout`, `-v` | MEASURED: dumps come from workers; start lines come from the controller. A worker exit is reported as "worker 'gwN' crashed while running '<id>'". |
| pytest-cov 7.1.0 / coverage 7.16.2 | `faulthandler_exit_on_timeout` | A killed worker returns no coverage data and the total drops; `fail_under = 96` then adds a second failure. MEASURED on a toy suite. |
| CPython 3.12.15 | `multiprocessing.resource_tracker` with `RLock` + `ReentrantCallError` | Present in 3.12.15 (gh-109629; the first 3.12.x carrying it was not checked, UNVERIFIED). The "reentrancy-safe" rewrite (gh-131788) is **not** in 3.12. |
| Playwright 1.63.0 | Ubuntu 24.04 and 26.04 (x64, arm64) | Same 21-library chromium apt set on both; official support since 1.61.0. |
| `PIP_CONSTRAINT: requirements.txt` | dev extras | The closure pins runtime packages only. pytest, xdist, cov, coverage and execnet float to latest at venv creation; only `playwright==1.63.0` is exact. This milestone does not change that. |

## Sources

- Installed CPython 3.12.15 source: `multiprocessing/resource_tracker.py`, `multiprocessing/synchronize.py` -- READ, HIGH.
- Installed pytest 9.1.1: `_pytest/unraisableexception.py`, `_pytest/faulthandler.py`; pytest-xdist 3.8.0 `xdist/workermanage.py`, `xdist/scheduler/load.py`; execnet 2.1.2 `multi.py`; coverage 7.16.2 `control.py`; pytest-cov 7.1.0 `engine.py` -- READ, HIGH.
- Playwright 1.63.0 driver: `playwright/driver/package/lib/coreBundle.js` (host-platform table, apt dependency tables, install-deps sudo path), `browsers.json` -- READ, HIGH.
- https://github.com/python/cpython/issues/131788 and https://github.com/python/cpython/pull/131787 -- reentrancy-safe resource tracker; main 2025-08-13, 3.14 2025-10-17, 3.13 reverted, 3.12 not backported -- READ, HIGH.
- https://github.com/halfb00t/screw/pull/7 -- the same cause found and fixed with `del manager` in a sibling project on 3.12.15 / pytest 9.1.1 / xdist 3.8.0 (2/20 -> 0/20 natural gate failures) -- READ, MEDIUM (the author's own measurement, not independently reproduced; reproduced in mechanism here).
- https://devguide.python.org/versions/ -- 3.12 is security-only -- READ, HIGH.
- https://docs.pytest.org/en/stable/changelog.html -- `faulthandler_exit_on_timeout` introduced in 9.0.0 (issue #13678) -- READ, HIGH.
- https://github.com/microsoft/playwright/issues/40117 -- Ubuntu 26.04 support in Playwright 1.61.0 -- READ, MEDIUM (issue thread).
- https://github.blog/changelog/2026-09-17-ubuntu-26-generally-available-and-latest-migration, https://github.com/actions/runner-images/issues/14748, https://github.com/actions/runner-images/issues/14226, https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2604-Readme.md -- migration dates, labels, image contents -- READ, HIGH for dates and labels, MEDIUM for the package list (page was summarised).
- https://pypi.org/pypi/{playwright,pytest,pytest-xdist,pytest-cov,pytest-timeout,coverage,execnet}/json -- latest versions and dates, fetched 2026-10-15 -- READ, HIGH.
- GitHub Actions run 38680454993 (`gh run view --log-failed`) and the runs listed in section 5 -- READ, HIGH.
- Local measurements, 2026-10-15 (scripts in the research scratchpad, not committed): forced-GC reproduction; `SemLock` creator/free probe; `del manager` and autouse-`gc.collect()` before/after; `gc.set_threshold` stress; xdist + cov `faulthandler_timeout` / `exit_on_timeout` toy runs; whole-suite `--durations` run; `ubuntu:26.04` container installs, browser test, whole suite and two-file loops -- MEASURED.

---
*Stack research for: spur v0.6 Clean Ledger (debt sweep tooling facts)*
*Researched: 2026-10-15*
