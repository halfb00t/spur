# Pitfalls Research

**Domain:** Adding a headless-browser test of the viewer, schema-driven conditional form fields, a UI-only bore-shape selector, a `slug()` change, a re-set gate bar and a constrained `make venv` probe to an existing, shipped parametric spur-gear generator (`spur`, milestone v0.5 Honest Form)
**Researched:** 2026-10-10
**Confidence:** HIGH for everything tagged MEASURED or READ (executed or read on 2026-10-10 on the host below); MEDIUM for DOCS (fetched documentation, not re-executed); LOW for anything tagged UNVERIFIED.

**Evidence tags used below**

- **MEASURED** - run on 2026-10-10 on the dev host: Apple M5 Max, 18 CPUs, macOS arm64, Python 3.12.15, Playwright 1.63.0 (Chromium 153.0.8010.12, headless shell build `chromium_headless_shell-1243`), pip 26.2.1, uvicorn 0.54.0, pydantic 2.13.5, pytest-xdist 3.8.0. Scratch scripts live in the session scratchpad and were not committed; a plan that leans on a number must re-create the measurement inside the repo.
- **READ** - a repo file at the line named, or upstream source/PyPI metadata read today.
- **DOCS** - an upstream documentation page fetched today.
- **UNVERIFIED** - inference or memory; no check was possible here (no Docker daemon, no Linux host, no GitHub runner).

**Phase labels (role names, the roadmap numbers from 21):**

- **BT** - the browser test of the viewer (server fixture, browser install, gate placement).
- **CF** - conditional form fields (`enabled_when` in `json_schema_extra`, rendered by `app.js`).
- **BS** - the bore-shape selector.
- **SL** - the `slug()` change that carries `root_shape`.
- **GB** - the L34 gate-bar re-set.
- **VP** - the `make venv` under `PIP_CONSTRAINT` probe.
- **LG** - the two small ledger items (reverify recipe, Pi 5 claim).

---

## Critical Pitfalls

### Pitfall BT-1: No WebGL context kills the whole form, not just the viewer

**What goes wrong:** On a runner where Chromium cannot create a WebGL2 context, `app.js` throws at module top level (`const renderer = new WebGLRenderer({ canvas, antialias: true })`, `app.js:229`) before the wiring IIFE at the bottom runs, so `buildForm()` never executes. A test written to check "the form builds from `/api/schema`" then fails with a timeout that looks like a schema problem. MEASURED: launching with `--disable-3d-apis` gave 0 form fields (wait timed out at 8 s) and the console error `THREE.WebGLRenderer: A WebGL context could not be created`. The vendored three.js is 0.186.0 (READ, `web/package.json`), which is WebGL2-only.

**Why it happens:** The viewer and the form share one module with no feature detection. It is also a real product defect: a user with WebGL disabled gets a blank form.

**Consequences:** A GPU-less CI runner that lacks a software GL path produces a red required check with a misleading symptom.

**How to avoid:**
1. Launch the Playwright-managed headless shell with its defaults. READ: Playwright's own launcher always pushes `--enable-unsafe-swiftshader` (`chromium.ts`, "See https://issues.chromium.org/issues/40277080"). MEASURED: the default headless shell reported `ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device ...))` even on this GPU Mac, so macOS and CI use the same software GL stack. `channel="chromium"` (new headless) reported `ANGLE Metal Renderer: Apple M5 Max` - a different stack - so do not use it; local and CI would stop being comparable. `--disable-gpu` was harmless on this build (still SwiftShader) but adds nothing; do not pass GL flags.
2. The fixture asserts `canvas.getContext('webgl2')` is non-null first and fails with a message that names WebGL, before any form assertion.
3. Treat Linux behaviour as UNVERIFIED until a CI spike branch has run it: no Docker daemon was available here. Chromium's SwiftShader doc says WebGL needs `--enable-unsafe-swiftshader` on current builds (DOCS, via search results); Playwright's launcher already supplies it.
4. File the "dead form without WebGL" gap as a `nice` debt item (the form could build before the renderer is created). Do not fix it inside the browser-test phase; the phase's job is to prove the shipped `app.js`.

**Warning signs:** `wait_for_function` timeouts on form fields only in CI; console error text containing `WebGLRenderer`.

**Phase to address:** BT (first plan: the WebGL precondition and the CI spike).

---

### Pitfall BT-2: A new test file silently joins the 30 s commit slice

**What goes wrong:** `make verify.fast` excludes the four heavy files by name (`--ignore=tests/test_model.py ... test_pool.py test_api.py test_cli.py`). The Makefile comment says why: "a new test file runs at commit until someone names it heavy" (READ, `Makefile:154`). A `tests/test_browser.py` therefore runs at pre-commit, needs a browser binary and a server, and has to fit in the SDK's hard 30 s kill. The slice is 11.4 s today (READ, `bench/RESULTS.md` 19-09: 824 tests, 11.39-11.54 s). Nothing in `tests/test_hooks.py` pins the ignore list (READ: it checks the shared static prefix and the hook ids only).

**Why it happens:** Exclusion-by-name is deliberate (L36) and has no check that a heavy file was added to it.

**How to avoid:** In the same commit that adds the browser test file, add `--ignore=tests/test_browser.py` to `test.fast` and amend L36 in the new `Lxx`. Add a test that fails when a test file imports `playwright` and is not in the ignore list, in the style of `tests/test_hooks.py`, so the next browser file cannot repeat this. Pure-Python tests for the new schema metadata and slug stay in the fast slice on purpose (they are cheap).

**Warning signs:** `make verify.fast` over 20 s; a commit that times out in the SDK after the BT phase lands; `Executable doesn't exist` at commit time on a fresh clone.

**Phase to address:** BT.

---

### Pitfall BT-3: A skip-if-no-browser makes the gate green with zero browser coverage

**What goes wrong:** `pytest.importorskip("playwright")` or a "skip when the browser is missing" fixture turns a fresh clone, a half-installed venv or a CI misconfiguration into a pass. The repo has been bitten by exactly this shape: `make no-fake-done` passed vacuously on macOS because `\b` is not implemented in the system regex (READ, `Makefile:102`, debt resolved in #23).

**How to avoid:**
1. No skip on a missing browser. A missing binary is a hard failure whose message says `make venv`.
2. An explicit, printed opt-out only (an environment variable such as `SPUR_NO_BROWSER=1`), refused when `CI` is set. The opt-out prints in the pytest header so a log shows it was taken.
3. A test that collects the browser test ids and asserts at least one exists, so a rename or a stray `--ignore` cannot silently empty the file.
4. `make test-image` (READ, `Makefile:186`) mounts the whole `tests/` directory and installs only `pytest httpx`; a module-level `import playwright` makes collection fail there. Decide: `--ignore` the file in that recipe, or import inside the fixture. Do not use `importorskip` to dodge it.

**Warning signs:** A pytest summary with a browser-file skip count; "0 browser tests collected" in a verbose run.

**Phase to address:** BT.

---

### Pitfall BT-4: An in-process server shares globals with the TestClient tests on the same xdist worker

**What goes wrong:** If the live server is a `uvicorn.Server` in a thread, it serves the same `spur.app.app` object that `tests/test_api.py` drives with `TestClient`. That module installs `app.dependency_overrides[build_backend]` in a module-scoped autouse fixture and pops it on exit (READ, `tests/test_api.py:25-41`), and `app.py` holds process-global `BUILD_QUEUE` and `_in_flight_builds` (READ, `app.py:102, 111`). pytest-xdist's default `--dist load` does not keep a module's tests together, so the override can appear or vanish while a browser test is mid-request. Without the override `build_backend()` raises `RuntimeError("Build pool not started")` (READ, `app.py:228`) and the page shows a 500 for no visible reason.

**How to avoid:** Run the server as a subprocess in its own interpreter. MEASURED: `python -m uvicorn spur.app:app --fd N` with `SPUR_BUILD_WORKERS=1` answered `/api/health` 0.16 s after spawn. The subprocess runs the real `BuildPool`, which is the production path (`build_backend` hard-fails without a pool by design), so this also keeps the test honest.

**Warning signs:** A browser test that passes with `-n 0` and fails at `-n 8`; 500s that mention the pool; a `test_api.py` failure that only appears when a browser test ran earlier on the same worker.

**Phase to address:** BT.

---

### Pitfall BT-5: Port collisions, orphaned servers and one server per worker

**What goes wrong:** Three separate failure modes.
1. *Per-worker duplication.* DOCS (pytest-xdist how-to): "tests in different processes requesting a high-level scoped fixture (for example `session`) will execute the fixture code more than once." At `-n 8`, a session fixture means up to 8 servers, 8 `BuildPool`s and 8 browsers. MEASURED: one Playwright driver plus headless shell with a WebGL2 canvas is 6 processes and about 387 MiB RSS (RSS double-counts shared pages, so an upper bound); times 8 is roughly 3 GiB before the servers' own pools.
2. *Port races.* "Find a free port, close it, start the server" has a window where another worker takes the port.
3. *Orphans.* MEASURED: after `SIGKILL` of the uvicorn process, both of its pool children were still alive 6 s later. A scratch experiment of mine also left a parentless uvicorn (PPID 1) when a script was killed by `timeout`; I had to clean it up by hand. A crashed xdist worker is not hypothetical: `docs/tech_debt/active/2026-10-09-xdist-worker-segfaults-in-occt-at-exit.md` records twelve of them on this host.

**How to avoid:**
1. Bind the listening socket in the fixture on port 0 and hand it to the child: `subprocess.Popen([...,"-m","uvicorn","spur.app:app","--fd",str(sock.fileno())], pass_fds=[sock.fileno()], start_new_session=True)`. MEASURED: works with a TCP socket (the installed uvicorn 0.54.0 wraps the descriptor with `socket.AF_UNIX`, READ `config.py` `bind_socket`, yet serving and `getsockname()` were correct). The parent already holds the socket, so there is no port race and no log parsing.
2. Teardown: `os.killpg(proc.pid, SIGTERM)`, wait a bounded time, then `SIGKILL` the group. Do not assert the exit code is 0: MEASURED, uvicorn exited with `-15` after `SIGTERM`. `start_new_session=True` is what makes the group kill reach the pool children.
3. Set `SPUR_BUILD_WORKERS=1` for the test server (READ: default 2, `app.py:125`).
4. Make one worker pay. Three options, in order of preference: (a) a single scenario test, so only one worker launches a server and a browser; (b) `@pytest.mark.xdist_group` plus `--dist loadgroup` - DOCS: the mark works only under `loadgroup`, and "Tests without the `xdist_group` mark are distributed normally as in the `--dist=load` mode", so the mark is a silent no-op under the current `addopts`, and switching the whole suite's scheduling is a gate-time change that must be measured; (c) a `FileLock` once-only fixture (DOCS, xdist how-to), which has no clean "last worker out" teardown. Start with (a).

**Warning signs:** `Address already in use`; `ps` showing `uvicorn spur.app:app` after the suite; memory pressure on a 4 vCPU CI runner (UNVERIFIED: runner RAM was not checked).

**Phase to address:** BT.

---

### Pitfall BT-6: Waiting on the wrong signal passes before the request exists

**What goes wrong:** `update()` debounces 350 ms, then runs `/api/info` then `/api/model.stl?quality=preview` with an abort-and-sequence guard (`seq`, `mine !== seq`). MEASURED, immediately after `fill("[name=teeth]", "21")`: `#status` text is `''` and `#dl-stl` has `href="api/model.stl"` (the previous state). A wait for "status is empty" or "download link has an href" is therefore already satisfied before the debounce fires. MEASURED with a `MutationObserver`: for a cached gear the "Building…" state exists for milliseconds (`["Building…", ""]`), so polling for it is a coin toss.

**Why it happens:** The UI has no explicit "settled" signal. Server caches (`_build_cached`, `_EXPORTS`, keyed `(params, fmt, quality, encoding)`, READ `app.py:401`) also make the second request for any gear fast, so test order changes what is observable. MEASURED: first STL ready 4.83 s after `goto` (pool spawn plus the OCP import), later loads 0.27-0.78 s.

**How to avoid:**
1. Wait on content, not on absence: the `#dl-stl` `href` containing the expected query (`teeth=21`), the hash, or `page.expect_response` on the exact URL.
2. For stale-response ordering, park the request, do not sleep. MEASURED recipe: a `page.route` handler that appends the `route` to a list and returns; change the field again; wait for the second result; then release the parked route. Result: final href `api/model.stl?teeth=24`, hash `#teeth=24`, and `continue_()` on the already-aborted route raised no error. The guard works; the test needs no timing.
3. Never block inside a sync-API route handler (for example waiting on a `threading.Event`). MEASURED: my first attempt deadlocked the page and hit a 60 s timeout. The mechanism (the sync dispatcher is blocked) is inferred, the timeout was observed.
4. Warm the server in the fixture (one preview build) with a bound derived from `SPUR_BUILD_TIMEOUT` (30 s), so the first test does not pay the cold build. Pass explicit timeouts; do not rely on the library default for `expect` (UNVERIFIED here: believed to be 5 s).
5. Do not use `page.clock`. DOCS: it fakes `requestAnimationFrame` as well as `setTimeout`/`Date`, and `app.js`'s `render()` is `requestAnimationFrame`-gated, so a faked clock would freeze the draw the test wants to see (inference). The 350 ms debounce is cheap in real time.
6. Do not assert the console is clean. MEASURED: SwiftShader emits `GPU stall due to ReadPixels` warnings on every run. Assert no `pageerror` and no console `error`.

**Warning signs:** Tests that pass alone and fail in a full run; a fixed `wait_for_timeout` anywhere in the file; green on the second run of a fresh server and red on the first.

**Phase to address:** BT.

---

### Pitfall BT-7: "The STL loaded into the scene" has no observable

**What goes wrong:** `mesh`, `scene` and `renderer` are module-scope `let`/`const` inside an ES module, so `page.evaluate` cannot read them. `renderer.render` runs from a `requestAnimationFrame`, and a WebGL canvas created without `preserveDrawingBuffer` reads back blank outside the draw (standard WebGL behaviour; UNVERIFIED here). The three signals the page does expose - the info rows, the warning, the download link - are all set before or independently of `showModel`.

**How to avoid:** Add one generic, field-name-free line in `showModel` that exposes a fact (for example `canvas.dataset.triangles = String(geometry.attributes.position.count / 3)`) and assert on it. Do not expose `window.__scene`. The alternative, a Playwright screenshot of the canvas clip checked for more than one distinct colour, works but is the weaker proof and varies with the GL stack. Never pixel-diff against a stored image: macOS and Linux differ in fonts and in GL. Check the one-line change against the token pins in `tests/test_api.py` before writing it (see CF-1).

**Phase to address:** BT.

---

### Pitfall BT-8: Browser install drift and the pinned-closure discipline

**What goes wrong:**
1. *Two sources of truth for the browser.* The Playwright wheel pins the browser build. MEASURED: playwright 1.63.0 installed `chromium-1243` and `chromium_headless_shell-1243` (Chromium 153.0.8010.12). A loose `playwright>=1` in the dev extra lets a `make venv` on one machine and CI on another resolve different Chromium builds. The existing discipline pins the runtime closure only (`requirements.txt`, 31 packages, `--no-deps`, L12); dev tools are loose ranges (`pytest>=8`, `ruff>=0.14`, READ `pyproject.toml`).
2. *A pip upgrade without a browser re-download.* `$(STAMP)` depends on `pyproject.toml` only. A `pip install -U` in an existing venv bumps the driver but not the browser, and the next run fails with `Executable doesn't exist` until `playwright install` is run.
3. *Install size and time.* MEASURED: `playwright install chromium` fetched the full Chromium, the headless shell and ffmpeg: 557 MB, 39.5 s on this host. The help output shows `--only-shell` (READ), which installs the headless shell alone. The driver inside the wheel is 130 MB (MEASURED) and bundles its own `node`, so the L11 worry about Node at test time does not apply to the Python route - but it must not enter `dependencies` or `requirements.txt`, or the image gains 130 MB.
4. *CI ordering.* `.venv` only exists after `make verify` creates it (READ, `ci.yml` comment on the `kernel pair` step), so a CI step cannot run `playwright install` before the venv exists. The install has to be a Makefile recipe step (inside or after `$(STAMP)`), with an OS-dependency step on Linux (`--with-deps` needs apt; UNVERIFIED whether `ubuntu-latest` already has the shared libraries for the headless shell).
5. *Caching.* DOCS (Playwright CI page): "Caching browser binaries is not recommended, since the amount of time it takes to restore the cache is comparable to the time it takes to download the binaries." Budget about 40 s of the `test (3.12)` job for the download and measure it on CI.
6. *OS support.* DOCS: Playwright lists Ubuntu 22.04 / 24.04 / 26.04 and macOS 14+. `ubuntu-latest` is a moving label, so the Playwright pin, not the runner, decides the browser.

**How to avoid:** Pin `playwright` exactly in `[project.optional-dependencies] dev` (a new, separately named tier: runtime closure vs dev pin, recorded in the `Lxx`). Keep it out of `dependencies`, `requirements.txt` and `docker/refresh-requirements.sh` (READ: the script resolves `pip install /src`, which is runtime only, so it stays clean unless someone edits the wrong table). Make the stamp recipe run `playwright install --only-shell chromium` after `pip install`, keyed to `pyproject.toml`. A test or `make` check compares `playwright --version`'s expected browser revision against the installed directory so drift produces one clear message.

**Warning signs:** `Executable doesn't exist at ~/Library/Caches/ms-playwright/...`; a CI run that downloads two browsers; a diff to `requirements.txt` in a phase that only added a dev tool.

**Phase to address:** BT (install and pin), with the `Lxx` in the same phase.

---

### Pitfall BT-9: Coverage accounting when the server runs in a subprocess

**What goes wrong:** Three traps.
1. A subprocess is not measured. READ: the repo's own comment says pytest-cov 7 dropped its subprocess hook (`pyproject.toml` `[tool.coverage.run]`); DOCS (pytest-cov changelog via search; coverage docs) agree: pytest-cov 7.0.0 removed it, and coverage's `patch = ["subprocess"]` is the replacement and "sets `parallel = True`" and needs a combine. So server lines run only by the browser test earn nothing, and no floor moves. That is acceptable: the `app.py` lines the browser exercises are already covered by `TestClient` tests.
2. Turning `patch = ["subprocess"]` on to "fix" it makes a `SIGKILL`ed server child leave a partial data file; `sigterm = true` only protects against `SIGTERM`. A truncated file can fail the combine step, which fails the whole gate. (Inference; UNVERIFIED.)
3. Adding `greenlet` to `concurrency` because Playwright's sync API uses greenlets (READ: `greenlet` is a Playwright dependency). The tests are outside `source = ["src/spur"]`, so nothing in `spur` runs inside a greenlet. Whether `greenlet` can be listed beside `thread` is UNVERIFIED; do not touch it.

**How to avoid:** Leave `[tool.coverage.run]` alone. Record the `app.py` and total coverage before and after the phase (baseline 97.92 % at `1220 tests`, floor 96) and state that the number did not move for a reason, not by luck. Do not move `fail_under` (the existing debt `2026-10-04-worker-coverage-flush-is-sometimes-lost.md` already says a total that wanders 0.22 points makes a tighter floor a coin toss).

**Phase to address:** BT.

---

### Pitfall BT-10: The `must` flake gets blamed on, or hidden by, the new test

**What goes wrong:** The `resource_tracker` `ReentrantCallError` chain has four recorded occurrences, all in whole-suite runs, one on CI (READ, `2026-10-06-resource-tracker-flake-fails-the-gate.md`). `filterwarnings = ["error"]` makes pytest raise the unraisable-exception warning in whichever test is running when the finalizer fires - the chain has surfaced in `test_pool.py` tests, "predating Phase 17". A new test file adds process churn per worker, so the next occurrence may land in a browser test and read as a browser flake. The reverse also happens: a real browser teardown problem gets filed as "the known flake".

MEASURED, so the browser teardown is not an established source: Playwright's sync API under `filterwarnings = error` and the `-p no:cacheprovider` pytest of the repo's style produced no warning in 6 runs (clean teardown 2, leaky fixture that never closes the browser 3, `-n 2` 1), and left no orphan driver or browser processes afterwards.

**How to avoid:**
1. Keep the whole log of every failed gate run during BT (`make verify 2>&1 | tee`), as 19-01 did, and classify each failure against the chain's signature (five reentrant-call warnings at the end of a call phase) before calling it new.
2. Do not add a `filterwarnings` entry and do not fix the flake in the same phase. The debt file's trigger is "the next `make verify` failure, with its whole log"; a combined change confounds it.
3. Close the browser and stop Playwright explicitly in the fixture (`browser.close(); pw.stop()`), even though a leak did no harm here.
4. Know what N buys: 2 whole-suite failures in 12 runs has a 95 % Wilson interval of about 5-45 % (calculated). A before/after comparison at N around 10 cannot see a change in this rate. State that in the record rather than claiming "no effect".

**Phase to address:** BT (logging discipline), GB (the runs that measure it).

---

### Pitfall BT-11: The decision "in or out of `make verify`" creates a second definition of passing

**What goes wrong:** If the browser test stays out of `make verify` (its own `make test.browser`, its own CI job), L13's "one definition of passing in three places" (dev shell/pre-push, CI, `pr.land`) now has two. A new required CI job also means edits to `.github/workflows/required-jobs.txt` and the GitHub ruleset on `main` (L22); `tests/test_pr_land.py` fails if `ci.yml` and `required-jobs.txt` disagree (READ). If it stays in, the pre-push hook and CI pay for it every time (see GB).

**How to avoid:** Price both routes at discuss-phase with measured numbers, not estimates: (a) the test alone, `pytest tests/test_browser.py -n0 --no-cov --durations=0` (cold server, warm server, browser launch separately); (b) the CI install cost (about 40 s measured locally for the download; measure on a runner). Whichever route is chosen, say in the `Lxx` which of the three places run the browser test, and make `pr.land`'s required-job list match.

**Phase to address:** BT (decision), GB (cost into the bar).

---

### Pitfall CF-1: The generic-code pins in `tests/test_api.py` will fail by design, and are easy to weaken

**What goes wrong:** READ, `tests/test_api.py:162-212`: `test_the_shareable_link_round_trips_every_field_through_generic_code` pins exact tokens of `app.js` (`fields.set(name, { input, wrap, title });`, `for (const [name, { input }] of fields) input.value = h.get(name) ?? defaults[name];`, `q.set(name, input.value)`, `history.replaceState(...)`, and others), and forbids any GearParams name as a quoted string, or as `.<field>`, outside the `DIMS` block. Its own comment names "the shape a conditional-field or bore-selector patch would add". So:
- A conditional renderer that adds a key to the `fields.set(...)` entry breaks a pin.
- A bore selector necessarily names `bore_d`, `bore_flat`, `bore_hex` and the keyway fields, breaking the "no field name" half.
- `test_every_key_the_ui_reads_is_a_derived_dimensions_field` harvests every line that starts `['word',` as a DIMS key (`^\s*\['(\w+)',`) and requires each to be a `DerivedDimensions` field. A selector options table written as `['round', ...]` rows is read as DIMS keys and fails it.

**Why it happens:** The pins were written to make exactly this change a deliberate act, and 08 D-09 locked "no conditional form behaviour".

**How to avoid:** The new `Lxx` supersedes 08 D-09 and the same commit rewrites the pins. Keep the intent: (i) the conditional renderer reads only schema metadata and names no field; (ii) the selector's field names live in one named constant block, carved out the way `DIMS` is, with a non-vacuous assertion that the carve-out regex matched (the existing test already has the "a regex that silently stopped matching must fail" guard - copy it); (iii) write option tables as objects (`{ value: 'round', ... }`), never as `['x', ...]` rows. Never delete a pin to get green; a pin changes only to a stricter or more specific one, and the `Lxx` says which.

**Warning signs:** A diff that removes a snippet from the pin tuple; a carve-out regex that matches the whole file.

**Phase to address:** CF (rewrite for the renderer), BS (carve-out for the selector).

---

### Pitfall CF-2: Encoding refusals as "disabled" creates deadlocks and false claims

**What goes wrong:** MEASURED against the running API:
- `keyway_width=3` alone and `keyway_depth=1.4` alone are both `422` ("A keyway needs both..."). If each is `enabled_when` the other is above 0, both are permanently disabled and the user can never set either.
- `spoke_count=4` plus `hole_count=4` is a `422` ("Only one body cutout pattern per part"). Disabling the other patterns when one is set stops the user switching without first zeroing it.
- `recess_sides=none` with `recess_depth=3` is `200` with `warnings: []`; `bore_d=0, bore_flat=5` is `200` with `warnings: []`. The server says nothing is inert in either case. A relation that dims these fields makes a claim the server does not confirm, and adding a warning to make it true changes `warnings` for existing links.
- `root_shape=trochoid, teeth=40` is ignored for a numeric reason (base circle above the root circle, `calc.py:1707`), which no field-value relation can express.

**Why it happens:** "Relevance depends on another field" sounds like one concept but covers three: *ignored* (server warns, 200), *refused* (server 422) and *numerically inert* (warned, depends on geometry).

**How to avoid:**
1. Define `enabled_when` narrowly: the field is *ignored by the server* when the condition is false, in exactly the cases where `calc.derive()` already emits an "ignored" warning. READ, `calc.py:1162-1247`: hex bore (`bore_d`, `bore_flat`), spokes (`spoke_width`, `hub_d`, `rim_wall`, `spoke_fillet` at `spoke_count` 0), holes (`hole_d`, `hole_circle_d` at `hole_count` 0), honeycomb (`hex_wall` at `hex_cell` 0). Refusals stay 422s and stay visible; the numeric trochoid case stays a warning.
2. Dim and annotate rather than set `disabled`, so a value stays editable and sendable. A `disabled` control still reads through `input.value` in `gearQuery()`, so it would still be sent, but it cannot be typed into; that is the deadlock.
3. A model-driven test over `GearParams.model_fields` (the style of `test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order`, `test_cli.py:198-242`): for each field with a relation, (a) the target fields exist; (b) the relation graph has no cycle and no field is gated only by fields that it gates; (c) with the condition false and the field set to a non-default value, `/api/info` is `200` and `warnings` names the field as ignored; (d) with the condition true, no ignored-warning names it. Run the same check on `bore_hex` versus `bore_d`/`bore_flat` so the L27 precedence is covered. This direction catches a relation that the server does not back; the reverse direction (every "ignored" warning has a relation) is a second assertion over the same list.
4. A relation the server does not back (the recess and `bore_d=0` cases) is a decision for the human, not a silent addition: either leave it undimmed, or add the warning as a separate, tested change with its own record. Note `bore_d=0, bore_flat=5` silently ignoring the D-flat is a pre-existing L08-shaped gap; file it.

**Phase to address:** CF.

---

### Pitfall CF-3: `json_schema_extra` is not policed, so collisions and drops are on you

**What goes wrong:** DOCS (pydantic JSON-schema page): a dict passed as `json_schema_extra` is added to the field's schema and "coexist[s] alongside generated properties". MEASURED on pydantic 2.13.5: a nested dict and a list for `enabled_when`, and a key literally named `if`, were all emitted verbatim; nothing refuses a JSON Schema keyword. So:
- A key that happens to be a keyword (`if`, `then`, `else`, `dependentRequired`, `readOnly`) is emitted as a real constraint to any consumer that validates against `/api/schema`. `enabled_when` itself is not a keyword (UNVERIFIED against the full 2020-12 vocabulary; check the list).
- The extra is attached per field. The `_f()` helper builds `extra: JsonDict` for numeric fields, but `root_shape` and `recess_sides` build their own `json_schema_extra={"group":..., "unit": ""}` (READ, `params.py:59-65`, `102-104`). A relation added only through `_f()` is dropped for the Literal fields with no error.
- A relation naming a field that does not exist (typo) silently never fires: in `app.js`, `fields.get(name)` is `undefined`.
- Nested values must stay `JsonValue`-typed or mypy `disallow_any_explicit` objects (READ: `JsonDict` from `pydantic.config` is already used).
- `/openapi.json` also embeds the model; `test_openapi_documents_the_typed_contracts` exists (READ, `test_api.py:65`), so add the key and re-run it rather than assuming FastAPI copes with a nested extra (UNVERIFIED).

**How to avoid:** Keep the vocabulary to one bare key (`enabled_when`) beside the existing bare `group`/`unit`/`step`, and add a test that no extra key is in the JSON Schema keyword set (a static list in the test). Carry the new metadata through one helper path for both construction styles. The model-driven test in CF-2 (a) covers the typo and drop cases. Keep the relation grammar to what the four ignored-field cases need (`{field, gt}` or `{field, eq}`, and `all`); the moment a fifth case needs `or`/`not`, stop and take it to the human instead of growing an expression language.

**Phase to address:** CF.

---

### Pitfall CF-4: The state is computed once, but values are changed programmatically in five places

**What goes wrong:** `app.js` writes input values without events in `readHash()`, the reset handler and `hashchange`; programmatic `.value =` does not dispatch `input`, and only `form.addEventListener('input', scheduleUpdate)` re-runs anything. If the conditional evaluation lives in an `input` listener, a link opened fresh (`readHash()` then `update()`), the Reset button and a back/forward navigation leave the previous dimming in place.

**How to avoid:** Evaluate relations in one function called from `update()` (which every path reaches) or immediately after `readHash()`/reset, not from an event. A BT test per path: open `#hole_count=4&hole_d=3`, assert the holes group is not dimmed and the spokes group is; press Reset; navigate with `history.back()`.

**Phase to address:** CF (design), BT (the three-path test).

---

### Pitfall BS-1: The selector rewrites or reinterprets what the user set (L05)

**What goes wrong:** The default part is a D-flat bore (`bore_d=9`, `bore_flat=8`, READ `params.py:72-75`), not a round one. A selector that "derives from the flat fields on load" has to reproduce the server's semantics exactly, and the form's existing semantics are subtle:
- An empty input is omitted from the query, so the server applies the default: `bore_flat` blank means 8 (D-flat), not 0. A selector that reads blank as 0 derives "round" while the server builds a D-flat.
- Defaults are compared as strings (`String(input.value) !== String(defaults[name])`), so `bore_d=9.0` is *kept* in the request set while `9` is dropped. A selector that normalises "9.0" to "9" changes the request set. Derive with `Number()`, never write back a re-formatted value.
- Precedence: `bore_hex > 0` replaces `bore_d` and `bore_flat` (L27). MEASURED: `#bore_hex=6&bore_d=7&bore_flat=5` sends all three, and the page warns `Hex bore replaces the round profile: bore_d (7 mm) and bore_flat (5 mm) are ignored.` The warning names two fields; hiding them (as a "hex" state might) hides the subject of the warning.
- A selector state of "Hex" with `bore_hex=0` means nothing to the server; writing a made-up default value (there is none: the default is 0) would silently change the part (the project's second standing rule). The selector must show the state the server computes, and a "chosen but incomplete" state must be visible as such.
- Switching "D-flat" to "Round" writes `bore_flat=0`, losing a value the user typed; switching back must restore the last typed value (remember it in memory, do not invent 8), and must never write `''`.
- `bore_d=0` with a D-flat set is `200` with no warning (MEASURED), a fifth state that the four-shape selector must either name or leave visible.

**How to avoid:**
1. The selector writes only on a user change of the selector, only the minimum fields, explicit `"0"` not `''`, and never on load.
2. Pin the baseline before writing it. MEASURED today (record it as the golden file in BT): `#bore_hex=6&bore_d=7&bore_flat=5&teeth=21` yields the requests `info?teeth=21&bore_d=7&bore_flat=5&bore_hex=6` and `model.stl?...&quality=preview`; the hash is rewritten to schema order and drops defaults (`#teeth=19&module=1.75&bore_flat=0` becomes `#bore_flat=0`). Compare request *sets* in canonical order, not raw hashes.
3. A BT-driven walk over the 44-record fixture (`tests/regression/pre_v0_2.json`): open each record as a link before and after the selector, and assert the `/api/info` and `/api/model.stl` query parameter sets are identical to the golden ones.
4. A model-driven server test that every state in the selector's constant round-trips: for each shape, the flat fields it writes are accepted and produce the shape's `bore_effective`/`hex_across_flats` result.

**Phase to address:** BS (design and tests), BT (golden baseline, which must land first).

---

### Pitfall BS-2: The selector's own name leaks into the link, and the server does not complain

**What goes wrong:** MEASURED: `GET /api/info?bore_shape=hex&teeth=21` returns `200` (unknown query parameters are ignored; READ `pyproject.toml` comment: "no model gains extra=forbid"). If the select is created through the generic `buildForm()` path, or registered in the `fields` map, `gearQuery()` sends `bore_shape=...`, the shared link grows an unknown parameter, and no test on the Python side notices. The contract "the URL/API/CLI stay flat" fails silently.

**How to avoid:** The select is not in `fields`. A BT test records every `/api/*` request with `page.on('request')` and asserts the parameter names are a subset of `GearParams.model_fields` plus `{quality, mate_teeth}`, and that the hash contains no non-field key. Also fix the order of operations: the selector is added to the Bore fieldset by code that does not touch the `Object.entries(schema.properties)` loop (a pinned token).

**Phase to address:** BS, verified in BT.

---

### Pitfall BS-3: A `<select>` assigned a value with no matching option goes blank and silently drops it

**What goes wrong:** MEASURED, an existing behaviour: `#root_shape=bogus&teeth=21` leaves the `root_shape` select at `selectedIndex -1` with `value ''`, the UI sends only `teeth=21`, and the hash is rewritten to `#teeth=21`. The API alone returns `422 Input should be 'radial' or 'trochoid'` for the same value (MEASURED), so the UI turns a refusal into a silent default. A bore-shape select that derives a value absent from its option list does the same thing to the bore.

**How to avoid:** Never assign a derived selector value that is not an option; cover every reachable derived state with an option (including the "none" and "incomplete" states). For the existing `root_shape` behaviour: pin it in the BT baseline first so it is a conscious fact, then file it as a debt item (a link carrying an invalid enum is changed to the default with no message - an L05-adjacent gap). Do not fix it in the same change as the selector.

**Phase to address:** BT (pin), BS (own selector), a debt file (existing gap).

---

### Pitfall BS-4: Two mechanisms for the same relation

**What goes wrong:** If conditional fields (CF) and the selector (BS) are built separately, the schema relation dims `bore_d`/`bore_flat` when `bore_hex > 0` while the selector derives its own state from the same fields with its own code. The two can disagree on load (`bore_hex=6` plus keyway fields, the 422 case), and the selector is the first bore-specific logic in `app.js`, in tension with the milestone rule "a field relation lives in schema metadata ... never hard-coded in `app.js`".

**How to avoid:** Build CF first and have the selector consume the same evaluation pass. Decide explicitly, with the human, how much of the selector is schema metadata: the pragmatic route is a single `BORE_SHAPES` constant in `app.js` under the new `Lxx` (the idea file's own wording: "accepting the first bore-specific logic in `app.js`"), plus the model-driven round-trip test in BS-1(4) so drift between that constant and `calc` is caught mechanically. Recommend this over inventing a model-level discriminator (the idea file says that is its own phase and needs an L05 story for every link).

**Phase to address:** CF before BS (ordering), discuss-phase for BS.

---

### Pitfall SL-1: The old names are pinned, and the default's name must not move

**What goes wrong:** READ:
- `tests/test_api.py:376-412` asserts that the trochoid and radial downloads have the same `Content-Disposition` (`filename="spur_z23_m1.75_pa25.stl"`), with a docstring that says so.
- `tests/test_api.py:716-720` pins `filename="spur_z21_m1.75_pa25.{fmt}"` for a default-radial gear.
- `docs/architecture/http-api.md:43` documents "`Content-Disposition` from `params.slug()`".
- `slug()` is also used for the temp export file name (`model.py:807`), `bench/export_cost.py:176`, `tests/test_model.py:2021`, and `records._gear_fields` (`records.py:180`) which puts it in every structured record.
A suffix on every name (including radial) changes the default gear's file name for every user and breaks line 720.

**How to avoid:** Append a suffix only for the non-default `root_shape` (for example `_trochoid`), so every radial name is byte-identical to today's. Flip the one assertion at line 411-412 to the new fact, update `http-api.md:43` and the idea file's record in the same commit, and add the end-to-end check in BT with `page.expect_download()` and `download.suggested_filename`. Tests that only assert the `slug` field is truthy (`test_api.py:797, 985, 1086, 1123`) and `test_records.py`'s synthetic `slug="spur_z19"` are unaffected.

**Phase to address:** SL.

---

### Pitfall SL-2: The name claims a root the part may not have

**What goes wrong:** `root_shape=trochoid` is *ignored* where the base circle lies above the root circle: MEASURED, `root_shape=trochoid&teeth=40` returns `200` with "...the trochoid root request is ignored", and the test docstring says that from 27 teeth on at the default module and angle "the two parts are the same". A slug built from the requested value labels a radial part "trochoid"; the idea's purpose (two different parts with one name) is inverted into two identical parts with two names. A file name is a claim about the part (L08's spirit).

**How to avoid:** Decide in the `Lxx`: (a) name the *requested* value and say so in `http-api.md`, or (b) name the *effective* root via `calc.root_mode(p)`. Prefer (b): `root_mode` is pure and cheap (MEASURED by 19-09: `derive()` 10.3 us radial, 30 us trochoid), and `params.py` already imports `calc` locally in `_feasible`. If (b), `slug()` must be total: it is called inside failure-path records (`build.failed`, `queue.refused`), so an exception from `root_mode` there would mask the original error. Test the 23-tooth case (applies) and the 40-tooth case (ignored) both ways.

**Phase to address:** SL.

---

### Pitfall SL-3: "Collides with cached exports keyed by slug" - checked, it does not

**What goes wrong:** The worry is that a renamed slug serves a stale name from a cache. READ: the export blob cache key is `(params, fmt, q.quality, encoding)` (`app.py:401`), the solid cache is keyed on the `GearParams` object, and `Content-Disposition` is built at response time from `params.slug()` (`app.py:496`); `pool.py` routes by parameter hash, and `grep slug` finds no use there. No cache is keyed by the slug.

**How to avoid:** Nothing to build; record this in the `Lxx` so the question is not asked again, and keep the existing assertion that the radial and trochoid bytes differ (it is how the test knows the cache did not answer both).

**Phase to address:** SL (recorded, not fixed).

---

### Pitfall GB-1: There is no idle host unless you wait for one, and the gate raises its own load

**What goes wrong:** L34's 66 s was not read on a quiet host: Phase 15's method says "no waiting for a quiet host", loads read were 6.53 and 9.09 (READ, `bench/RESULTS.md` 2208-2250), on a 12-CPU M2 Max. The 192.94 s reading is on an 18-CPU M5 Max with load 4.03 -> 9.06 across the runs, because each run's eight workers raise the next run's starting load (READ, 19-09 table). MEASURED right now: `uptime` showed load averages of 6.05 at the start of this session on this host, with 10 users logged in (other agent sessions share the machine). Back-to-back runs can never be "idle".

**How to avoid:**
1. Reuse the project's own quiet protocol (Phase 12 D-02): poll `sysctl -n vm.loadavg` about once a minute and start only when the 1-minute figure is under 1.5. READ: that wait took 6 minutes to fall from 4.40 to 1.30 once. Budget it: 10 runs are on the order of 90 minutes.
2. Phase 15's R1: before every run, `pgrep -fl '[p]ytest|[p]re_commit|[m]ake verify'` prints nothing, so no other session's gate is live.
3. Record load before and after, the power source and the time of day; flag a run that started over 1.5 and do not average it silently.
4. Write the rule that turns readings into a bar *before* the first reading (as L34 fixed its knee rule before the read), and let the human set the number. A bar set from the readings after seeing them is the "tuned toward a pass" that L08/L34 forbid.

**Phase to address:** GB.

---

### Pitfall GB-2: The spread is bigger than the effect being measured

**What goes wrong:** READ (19-09): three runs of `make verify` read 208.52, 161.71, 208.60 s (range 47 s, about 26 % of the mean) on one host. The kernel-tier tests are 12-26 s each, one of them 25.78 s on a single worker, so with eight workers the wall time is quantised by how the long tests pack, not only by host load. A browser test costing a few seconds disappears in that spread at N = 3.

**How to avoid:**
1. Price the browser test where it can be seen: in isolation (`pytest tests/test_browser.py -n0 --no-cov --durations=0`), reporting launch, server warm-up and scenario seconds, and the worst-case wall contribution (its longest single test goes on one worker's critical path).
2. For the whole-gate comparison, alternate A and B in one session on the same tree: A = `make verify PYTEST_ARGS="--ignore=tests/test_browser.py"`, B = `make verify`. That isolates the browser test exactly and needs no worktree (PYTEST_ARGS comes last in the recipe, READ `Makefile:131`). N of at least 5 per arm; report min, median and max, not only the mean.
3. Count flake-failed runs separately (about 1 in 6 whole-suite runs locally, BT-10): list them, keep them out of the mean, and plan N + 3 attempts.

**Phase to address:** GB, with the isolated price taken in BT.

---

### Pitfall GB-3: The bar belongs to a host, and four files quote the old one

**What goes wrong:** The bar was set on a 12-CPU M2 Max, the new reading is on an 18-CPU M5 Max, both with `PYTEST_WORKERS` 8. CI runs on a 4-vCPU runner at `-n 4`, where whole-suite runs read 128.16 s and 210.98 s (READ, the flake debt, runs 37460192883 and 37460451701). One number cannot be the bar for all three. Meanwhile the old figure is quoted in `Makefile:85` ("about 64 s to about 75 s, over L34's 66 s bar"), `Makefile:153` ("the whole gate is 63.555 s (L34)"), `.pre-commit-config.yaml:10` ("A warm `make verify` measured 63.555 s") and the Phase 19 review's IN-03 (READ, `2026-10-09-phase-19-review-info-findings-deferred.md`).

**How to avoid:** The `Lxx` names the host the bar belongs to and says what it is not (not a CI limit, not a promise to contributors). The same commit rewrites the three stale comments to cite the new `Lxx` and retires IN-03 (CLAUDE.md: retire a debt item only in the commit that closes it). Do not rescale across hosts; quote each reading with its machine, as 19-09 did.

**Phase to address:** GB.

---

### Pitfall VP-1: The arm64 wheel gap is not the risk; the proof venv clobbering the commit hooks is

**What goes wrong (the premise):** The idea file expects `vtk`, `casadi`, `nlopt` to lack arm64 wheels. MEASURED against PyPI JSON for all 31 pins in `requirements.txt` today: every one has either a pure-Python wheel or a macOS arm64 wheel (`vtk 9.6.2` `cp312 macosx_11_0_arm64`, `casadi 3.8.1` `cp311-abi3 macosx_11_0_arm64`, `nlopt 2.11.0`, `numpy 2.5.3`, `pydantic_core 2.46.5`, `PyYAML 6.0.3`, `cadquery-ocp 7.9.3.1.1`; `cadquery-ocp-proxy`, `cadquery 2.8.0` pure). The dev venv already runs `cadquery 2.8.0`, `cadquery-ocp 7.9.3.1.1`, `vtk 9.6.2`, `casadi 3.8.1`, `nlopt 2.11.0` (MEASURED, `pip freeze`). The probe is likely to install cleanly; plan for it to pass.

**What goes wrong (the actual hazards):**
1. *Hook clobbering.* `make venv VENV=.venv-proof` in the main checkout runs `$(VENV)/bin/pre-commit install`, and pre-commit bakes the installing venv's python into the shim. READ: `.git/hooks/pre-commit` currently has `INSTALL_PYTHON=/Users/half/git/halfb00t/spur/.venv/bin/python`, and the Makefile comment (`Makefile:51`) records the consequence: delete that venv and "every later commit would fail". The `$(HOOKS)` stamp is per venv, so re-running `make venv` for the real `.venv` would not reinstall them.
2. *Untracked 1.4 GB.* `.gitignore` lists `.venv/` and `venv/` only; `.venv-proof/` shows up in `git status` and is one `git add -A` from a commit.
3. *Versions move under the constraint.* The current dev venv is newer than the closure for `fastapi` (0.142.4 vs 0.141.1), `starlette` (1.7.0 vs 1.6.0) and `uvicorn` (0.54.0 vs 0.53.0) (MEASURED); the constraint downgrades them. CI already runs the pins on Linux, so a macOS-only difference is the thing to look for.
4. *`$(STAMP)` has no `requirements.txt` prerequisite.* Adopting the constraint without adding one means a later pin change never re-installs.
5. *pip 26.2 changed the meaning of the variable.* DOCS (pip news, 2026-07-29): "Constraints files, including `PIP_CONSTRAINT`, no longer affect isolated build environments. Use `--build-constraint` or the `PIP_BUILD_CONSTRAINT`". The venv here has pip 26.2.1 and `$(STAMP)` upgrades pip first. So `pip install -e .` builds `hatchling` unconstrained; that is fine for this project, but L34's "a conflicting pin fails closed" evidence was for runtime pins - do not extend it to build requirements.
6. *"Passes" proves little.* The dev venv already has the same kernel pair, so `test_the_fixture_was_captured_on_the_kernel_this_run_uses` already passes locally. The probe can show *no harm*, not benefit; its value is the version-delta list and a clean `pip check`.
7. *Dev tools are outside the closure.* The 31 pins are the runtime set; `pytest`, `mypy`, `ruff`, `playwright` float. "Single statement of what spur is tested against" is true only for runtime.
8. *arm64 Linux is a different claim.* A green macOS arm64 venv says nothing about the Docker `linux/arm64` image or the Pi 5 claim (LG).

**How to avoid:** Run the probe in a scratch `git clone` outside the repo (a clone has its own `.git/hooks`; a linked worktree also works - the Makefile detects it and skips the install, READ `Makefile:71`). Record: the venv creation time, `pip check`, the full `pip freeze` diff against `.venv`, `make verify` result line, and the load at start. If adopting, give `$(STAMP)` the prerequisite and `export PIP_CONSTRAINT := requirements.txt` in the recipe (a relative path works because `make` runs at the repo root), amend L34's CI sentence, and keep Playwright pinned in `[dev]` (BT-8).

**Phase to address:** VP.

---

## Moderate Pitfalls

### Pitfall M-1: Playwright artifacts and the repo's git hygiene

**What goes wrong:** Traces, screenshots and `test-results/` land in the working directory and are not in `.gitignore`; `.coverage.*` and `*.stl` are. A failing CI run wants artifacts, a local run leaves untracked directories.
**Prevention:** Add the artifact directory to `.gitignore` in the BT commit; write failure artifacts under `tmp_path`, and upload them from CI only on failure. Do not use `pytest-playwright` for this: it registers its own CLI options, fixtures and artifact directory in a suite whose `--strict-config` and `filterwarnings = error` have been tuned by hand (recommendation; the plugin's interplay with `-n 8` was not run here). Plain `playwright.sync_api` in one fixture is enough.

### Pitfall M-2: Type-checking the browser tests under `mypy --strict --disallow-any-explicit`

**What goes wrong:** MEASURED: `playwright` ships `py.typed`, so it type-checks, but `page.evaluate(...)` returns `Any` and returning it from a typed function gives `error: Returning Any from function declared to return "int" [no-any-return]`. `make typecheck` covers `tests` (READ, `Makefile`).
**Prevention:** Follow the repo's convention (`Any` is never written; `object` narrowed at use): `isinstance` the result of `evaluate`, or declare the helper's return as `object`. Expect to do this at every `evaluate` call, so wrap them in two or three typed helpers.

### Pitfall M-3: `no-fake-done` scans `*.js`

**What goes wrong:** `make no-fake-done` greps `*.py`, `*.js`, `*.sh` for `TODO|FIXME|XXX|HACK|NotImplementedError` (whole word). New `app.js` comments for the relation grammar or the selector that use those words fail the gate; the vendored bundle is excluded, `app.js` is not.
**Prevention:** Write the sentence out ("not yet handled: ...") and file the idea or debt instead.

### Pitfall M-4: Resource cost of eight Chromiums plus eight pools on a small runner

**What goes wrong:** CI's `ubuntu-latest` has 4 vCPUs (READ: the Makefile comment) and `PYTEST_WORKERS` clamps to 4 there, so at most 4 browsers and 4 pools; the injected 0.2 s and 1.0 s timeouts in `tests/test_pool.py` are already the sensitive ones on a starved runner (READ, `Makefile:142`). Extra CPU-hungry software-rendered WebGL from the browser test competes with them.
**Prevention:** Option BT-5(a) (one scenario, one worker). Measure the pool tests' pass rate on CI with the browser test present, using the run history, before and after.

### Pitfall M-5: Reverify loops will recur during this milestone (LG)

**What goes wrong:** `VERIFICATION.md` goes `stale` when any covered file changes after the report; this milestone edits the decision log (`Lxx`), `Makefile` comments, `README.md` and `docs/architecture/*.md` repeatedly, all of them typically in covered file sets. The idea file records that `/gsd-ship` blocked twice in one phase for this (READ, `docs/ideas/2026-09-28-reverify-after-post-verification-fixes.md`). Its own trigger for a skill is "hit three times".
**Prevention:** Take the one-paragraph `HOW_TO_DEVELOP.md` §6 recipe early in the milestone (it is a paragraph, not a skill), so the first stale block is a known step, not a new investigation. Promote to `.ai_skills/reverify-phase` only if the loop hits a third time (CLAUDE.md: add a skill when a workflow repeats).

### Pitfall M-6: Softening the Pi 5 claim must not become a new unmeasured claim (LG)

**What goes wrong:** README line 40 says a Raspberry Pi 5 "all work[s]"; every number in the tree is from a 12- or 18-CPU Apple host (READ, the idea file). Softening to "numbers measured on an M-series Mac" is right; adding "arm64 is verified" because the VP probe passed on macOS arm64 would be a new, wrong claim (VP-1 item 8).
**Prevention:** State the hardware the numbers came from and nothing more; the sentence cites no VP result.

### Pitfall M-7: A relation's "true" state changes the warning text the user sees

**What goes wrong:** MEASURED: `bore_hex=6, bore_d=7` warns `bore_d (7 mm) and bore_flat (8 mm) are ignored` - it names `bore_flat (8 mm)`, a *default* the user never set. A form that dims `bore_flat` is consistent, but a form that also hides it makes the warning refer to an invisible field.
**Prevention:** Dim, never hide, and keep the warnings exactly as they are (the API and CLI do not change in this milestone).

---

## Minor Pitfalls

### Pitfall m-1: `goto` with only a hash change is a same-document navigation

Opening `#hole_count=4` after a page is already loaded does not reload; the `hashchange` handler runs `readHash()` then `update()`. A test that expects a fresh page load will see stale state. (UNVERIFIED in Playwright specifics; the app side is READ at `app.js:340`.) Use a new page per scenario for "open this link", and `history.back()` for the navigation case.

### Pitfall m-2: Dated comments and docs drift

`docs/architecture/web-ui.md` and `http-api.md` describe the UI and the `Content-Disposition` rule; the BT, CF and SL changes each need their line there in the same commit (CLAUDE.md: new behaviour ships with its tests; docs ride along). `README` must not claim a browser test runs in `make verify` if the `Lxx` puts it elsewhere.

### Pitfall m-3: The in-app "Reset" and `defaults` for float fields

`defaults[name]` comes from JSON, so `0.0` becomes `0`. Any new JS that compares to a default must use the existing `String()` form or the numbers will disagree on `0` vs `0.0`.

### Pitfall m-4: A retired ledger item must ride the commit that closes it

CLAUDE.md: `Status: resolved`, the sha, `git mv` into `resolved/`, the INDEX row moved - in the fixing commit. v0.5 closes seven idea files and one debt item (IN-03 plus possibly IN-04 for the `root_fillet` label, which sits in the `DIMS` table the CF phase touches); do not batch them.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| `importorskip("playwright")` or skip-on-missing-browser | Gate green on a fresh clone and in the image test | Zero browser coverage with a green check; the `no-fake-done` macOS history repeated | Never; an explicit, printed, CI-refused opt-out only |
| Loosening the generic-code pins in `test_api.py` to fit the new JS | Fast green | The "form is generated from `/api/schema` only" rule (L02) stops being mechanically enforced | Never silently; only as a stricter pin under the new `Lxx` |
| `disabled` on every gated field | Looks finished | Deadlocks (keyway pair), traps (cutout patterns), unbacked claims (recess) | Never for refusals; dim-and-annotate for ignored-field cases only |
| Server in an in-process thread | No subprocess handling | Shared `app` globals and `dependency_overrides` with `TestClient` tests | Never in this suite |
| Slug carries the requested `root_shape` | One-line change | A radial part named "trochoid" where the request is ignored | Only if the `Lxx` records it as "requested" and the doc says so |
| Bar set from the first idle-looking reading | Closes IN-03 quickly | A number read at one load, one spread, one host; the next re-set repeats | Never; pre-register the rule, N >= 5 per arm, record min/median/max |
| `make venv VENV=.venv-proof` in the main checkout | Matches the idea file's wording | Hook shim points at a venv that is later deleted; every commit fails | Never; use a scratch clone or a linked worktree |
| Adding `playwright` to `dependencies` or the closure | One place to list it | 130 MB Node driver in the image; the closure stops being runtime-only | Never |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| pytest-xdist | Session fixture assumed once per run; `xdist_group` assumed to work under the default `--dist load` | Fixture runs once per worker (DOCS); `xdist_group` needs `--dist loadgroup` (DOCS); design for one worker paying |
| coverage + subprocess | Enabling `patch = ["subprocess"]` to count the server | Leave it off; the server lines are covered by `TestClient`; a killed child may leave partial data (UNVERIFIED) |
| `filterwarnings = error` | Blaming the browser, or filtering the chain | Keep the whole log; classify against the four known occurrences; no blanket filter |
| `make verify.fast` | New test file joins the 30 s slice automatically | Add `--ignore=` in the same commit and test the list |
| `make test-image` | `import playwright` at module top breaks collection in the image | Ignore the file in that recipe or import inside the fixture |
| uvicorn `--fd` | Passing a TCP socket to a flag documented for unix/systemd sockets | MEASURED to work on 0.54.0; keep a test that the fixture can serve one request so an upgrade that breaks it is caught |
| pip 26.2 | Assuming `PIP_CONSTRAINT` reaches build isolation | It does not as of 26.2 (DOCS); use `PIP_BUILD_CONSTRAINT` only if build deps need pinning |
| Playwright on CI | Pre-step `playwright install` before `make verify` | The venv does not exist before `make`; install inside the Makefile |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| One server, pool and browser per xdist worker | Memory and CPU spikes at suite start; the 0.2 s/1.0 s pool timeouts trip | One scenario test, one worker; `SPUR_BUILD_WORKERS=1` for the test server | `-n 8` locally (about 387 MiB per browser, MEASURED); `-n 4` on a CI runner |
| Cold first build in the browser test | First test red, rest green; 4.83 s measured against a 5 s style default | Warm the server in the fixture with a bound from `SPUR_BUILD_TIMEOUT` | Fresh page cache after `make clean` ("a couple of minutes", READ) |
| Software-rendered WebGL under load | Slow frames, `GPU stall` console noise | Assert structure, not frame timing; no console-clean assertion | Any run on the headless shell |
| Gate wall time quantised by long tests | 26 % spread across three runs | N >= 5 per arm, min/median/max, interleaved A/B | Always, at 8 workers with 12-26 s tests |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Test server bound to `0.0.0.0` | A local gear generator with no auth (REQ-no-auth-default) exposed on the network during the test run | The pre-bound socket is `127.0.0.1` only |
| Launching Chromium with `--no-sandbox` by hand | Playwright already adds it unless `chromiumSandbox` is set (READ); do not widen further | Use Playwright defaults; the page under test is this repo's own static files |
| Relation metadata evaluated as code | If `enabled_when` ever became an expression string, the form would `eval` server data | Keep it a data structure (`{field, gt}`), never a string to execute |
| `slug()` free text in a header | Header injection through `Content-Disposition` | The suffix comes from a `Literal`; `root_shape` can only be one of two literals |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Hiding ignored fields | The ignored-field warning names fields the user cannot see | Dim and annotate; keep every field visible and sendable |
| Selector shows "Hex" while the part is a D-flat | The UI claims a part it is not building | Show the state the server computes; a visible "enter across-flats" state |
| Switching shape forgets what the user typed | Lost data, silent change of the part | Remember last typed values in memory; never invent a default |
| Disabled field with no reason | "Why can't I click this?" | A short line saying which field makes it inert; same wording as the server's warning |
| Download name identical for two parts | The browser appends `(1)`; the user cannot tell which file is which | SL, with the requested/effective decision made explicitly |

## "Looks Done But Isn't" Checklist

- [ ] **Browser test:** often missing a hard failure for a missing browser - verify `SPUR_NO_BROWSER` is printed in the header when set, refused under `CI`, and that the collected-count test fails on an empty file.
- [ ] **Browser test:** often missing the `--ignore=` in `test.fast` - verify `make verify.fast` runs without launching a browser and still reads under 20 s.
- [ ] **Browser test:** often missing teardown of the server group - verify `pgrep -fl "uvicorn spur.app"` prints nothing after a full `make verify` and after a deliberately killed worker.
- [ ] **Browser test:** often passes only when the server is warm - verify a run from a cold server (fresh process, empty `_build_cached`) passes.
- [ ] **Browser test:** verify no `wait_for_timeout`/`sleep` and no `page.clock`.
- [ ] **CI:** often missing the OS-library step - verify a CI run on a branch prints the Chromium version, installs only the headless shell, and the pinned Playwright version appears in the log.
- [ ] **Conditional fields:** often missing the three programmatic paths - verify reset, `hashchange` and fresh load in the browser test.
- [ ] **Conditional fields:** verify the model-driven relation test also fails when a relation is removed from one field (a tripwire, as the repo does for other proofs).
- [ ] **Conditional fields:** verify `/openapi.json`, `/docs` and the CLI `--help` field walk still pass with the new key present.
- [ ] **Selector:** verify the 44-record fixture, opened as links, produces identical request parameter sets before and after the selector.
- [ ] **Selector:** verify no `/api/*` request and no hash carries a non-field key.
- [ ] **Selector:** verify a link with `bore_hex=6&bore_d=7&bore_flat=5` still sends all three and still shows the warning.
- [ ] **Slug:** verify the default radial name is byte-identical to `spur_z21_m1.75_pa25.stl`-style names, and that `suggested_filename` in the browser matches `Content-Disposition`.
- [ ] **Gate bar:** verify the rule was committed before the first reading, each reading has its load and its machine, and the three stale comments are rewritten in the same commit.
- [ ] **Venv probe:** verify `git status` is clean and `.git/hooks/pre-commit` still names `.venv/bin/python` after the probe.
- [ ] **Ledger:** verify each closed item has `Status: resolved`, a sha, its `git mv` and its INDEX row in the commit that closed it.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Hook shim points at a deleted proof venv | LOW | `rm .git/hooks/{pre-commit,commit-msg,pre-push}`; `rm .venv/.hooks-installed`; `make venv` (re-installs from `.venv`); read `INSTALL_PYTHON` in the shim |
| Orphaned test servers holding ports or memory | LOW | `pgrep -fl "uvicorn spur.app"`, then `kill -TERM -<pgid>`; fix the fixture's group kill |
| A pin in `test_api.py` weakened to get green | MEDIUM | Revert the pin change; re-derive the intended pin from the `Lxx`; re-run the field walk |
| Slug shipped with a suffix on radial names | MEDIUM | Revert to unsuffixed radial; every shared download name was changed in the interim - note it in the `Lxx` |
| Bar re-set from a loaded reading | LOW | Supersede with a new `Lxx` carrying the idle-protocol readings; the rule is already in the record |
| Flake attributed to the browser test (or the reverse) | LOW | Compare the failing log to the four recorded occurrences; run the failing test alone at `-n 0` |
| `requirements.txt` changed by accident for a dev tool | LOW | `git checkout requirements.txt`; add the dev pin to `[dev]` only |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| BT-1 no WebGL, form dead | BT | WebGL precondition test with its own message; CI spike run prints a GL renderer |
| BT-2 joins the 30 s slice | BT | `--ignore` in `test.fast`; test that fails if a Playwright-importing file is not ignored; `make verify.fast` < 20 s |
| BT-3 vacuous skip | BT | No skip on missing browser; opt-out printed and refused in CI; collected-count test |
| BT-4 shared globals | BT | Server is a subprocess; passes at `-n 8` repeatedly |
| BT-5 ports, orphans, per-worker cost | BT | Pre-bound socket; `killpg`; no orphans after kill; RSS measured at `-n 8` |
| BT-6 wrong wait signal | BT | Content-based waits; parked-route stale-response test; no sleeps |
| BT-7 no scene observable | BT | One generic dataset line asserted; no `window.__scene` |
| BT-8 install drift, pinning | BT | Exact `playwright` pin in `[dev]`; install in the stamp; closure unchanged |
| BT-9 coverage | BT | Coverage per file before/after recorded; `[tool.coverage.run]` unchanged |
| BT-10 flake attribution | BT, GB | Whole logs kept; Wilson interval stated; no filter added |
| BT-11 second definition of passing | BT | `Lxx` says which of the three places run it; `required-jobs.txt` matches `ci.yml` |
| CF-1 generic pins | CF, BS | Pins rewritten stricter under the `Lxx`; carve-out regex non-vacuous |
| CF-2 refusals as disabled | CF | Model-driven relation test (ignored-warning backed); graph has no cycle |
| CF-3 `json_schema_extra` collisions and drops | CF | One bare key; keyword-set test; both construction styles carried |
| CF-4 programmatic value changes | CF, BT | Reset, `hashchange` and fresh-load browser tests |
| BS-1 L05 rewriting | BS, BT | Golden request sets from the 44 fixture records; round-trip test per state |
| BS-2 name leak | BS, BT | Request-parameter-subset assertion over `/api/*` |
| BS-3 blank select | BT (pin), BS | Existing `root_shape=bogus` behaviour pinned and filed |
| BS-4 two mechanisms | CF before BS | Selector uses CF's evaluation pass |
| SL-1 pinned names | SL | One assertion flipped, default names unchanged, docs updated |
| SL-2 requested vs effective | SL | 23-tooth and 40-tooth tests under the chosen rule |
| SL-3 cache keys | SL | Recorded in the `Lxx` (checked) |
| GB-1 idle host | GB | Quiet protocol (<1.5 load), `pgrep` clean, load recorded |
| GB-2 spread | GB | Interleaved A/B, N >= 5, min/median/max |
| GB-3 host-bound bar, stale comments | GB | Host named in `Lxx`; three comments and IN-03 in the same commit |
| VP-1 hooks, ignore, versions, stamp | VP | Scratch clone or worktree; `pip check`; freeze diff; `.git/hooks` unchanged |
| M-5 reverify loop | LG (early) | Recipe paragraph in `HOW_TO_DEVELOP.md` §6 |
| M-6 Pi 5 | LG | README sentence cites no VP result |

**Sequencing implied by the pitfalls:**

1. BT first. It carries the golden baselines (request sets for the 44 records, the hex-link warning, the `root_shape=bogus` behaviour) that CF and BS are judged against, and its server fixture, install and gate-placement decision are what every later phase's cost sits on.
2. CF before BS (BS-4). BS reuses CF's evaluation pass.
3. SL is independent; it needs only BT's `suggested_filename` check, so it can sit anywhere after BT.
4. GB last, with the isolated price of the browser test taken in BT and the interleaved A/B taken once the test set is final. The registered rule is written before any reading.
5. VP is independent, but run it in a scratch clone and not while a GB measurement is in progress (it loads the host).
6. LG's reverify paragraph is cheapest early.

**Research flags for the discuss-phase steps:**

- BT: needs a CI spike (headless shell on `ubuntu-latest`, apt libraries, install time) and a human decision on in/out of `make verify`, priced.
- CF: needs a human decision on the relation grammar's scope and on whether a relation the server does not back (recess, `bore_d=0`) is added with a new warning or left alone.
- BS: needs a human decision on how much of the selector is hard-coded in `app.js` (BS-4) and what the "incomplete hex" state shows.
- SL: needs a human decision, requested vs effective.
- GB: needs the rule fixed before reading, and the human to set the number.
- VP: standard; low risk after the hazards above.

## Sources

- Repo (READ): `app.js` (`:229` renderer, `update()`, `readHash`, `gearQuery`), `params.py`, `calc.py:1162-1247, 1707`, `app.py:101-114, 203-209, 401, 496`, `tests/test_api.py` (`:25-41`, `:164-212`, `:376-412`, `:720`), `tests/test_cli.py:196-242`, `Makefile`, `pyproject.toml`, `.github/workflows/ci.yml`, `.pre-commit-config.yaml`, `.gitignore`, `bench/RESULTS.md` (Phase 15 method, 19-09 "The gate, priced"), `.git/hooks/pre-commit`, `docs/tech_debt/active/*` (resource-tracker flake, xdist segfault, coverage flush, Phase 19 review deferrals), `docs/ideas/*` (browser test, conditional fields, bore selector, download name, venv constraint, reverify, Pi 5).
- MEASURED 2026-10-10 (scratch scripts, not committed): headless GL stack on macOS arm64 for the default shell vs `channel="chromium"`; `--disable-3d-apis` form failure; first/later STL-ready times; `#status`/href state right after `fill`; parked-route stale-response ordering; process count and RSS of driver plus browser; `playwright install chromium` size and time; Playwright under `filterwarnings = error`; uvicorn `--fd` with a TCP socket; pool children surviving a server `SIGKILL`; baseline link behaviours (`root_shape=bogus`, hex link, default omission); API responses for the ignored/refused combinations; pydantic `json_schema_extra` nested emission; all 31 pins against PyPI JSON; `pip freeze` of the dev venv; mypy strict on a Playwright call.
- Upstream source READ: Playwright `chromium.ts` (`--enable-unsafe-swiftshader`), uvicorn `config.py` `bind_socket` (installed 0.54.0 and master).
- DOCS: pytest-xdist distribution and how-to pages (`xdist_group` and `--dist loadgroup`; session fixtures run per worker; FileLock pattern); Playwright Python browsers, CI, intro and clock pages (cache location, `--only-shell`, caching not recommended, Ubuntu 22.04/24.04/26.04, clock fakes `requestAnimationFrame`); coverage.py config (subprocess patch, `parallel`); pytest-cov 7.0.0 changelog (via search result); pip 26.2 release notes (constraints and build isolation); pydantic JSON-schema docs (`json_schema_extra` dict is merged); Chromium SwiftShader doc (via search result).
- UNVERIFIED and labelled in text: headless shell on `ubuntu-latest` without extra apt packages; `expect` default timeout; WebGL canvas readback without `preserveDrawingBuffer`; coverage partial-file behaviour on `SIGKILL`; `greenlet` beside `thread` in coverage `concurrency`; full JSON Schema 2020-12 keyword list vs `enabled_when`; FastAPI's handling of a nested extra in `/openapi.json`; same-document `goto` semantics in Playwright.

---
*Pitfalls research for: v0.5 Honest Form on the shipped spur gear generator*
*Researched: 2026-10-10*
