# Phase 21: Browser Test of the Viewer - Context

**Gathered:** 2026-10-10
**Status:** Ready for planning

<domain>
## Phase Boundary

`tests/test_browser.py` drives the shipped `src/spur/static/app.js` in Playwright's default
Chrome Headless Shell against a real `uvicorn` subprocess, inside `make verify` and CI's
`test (3.12)` job, and proves what the Python tests structurally cannot see: the form builds
from `/api/schema`, an invalid field is marked through the 422 `detail[].ctx.fields` path, a
warning renders as exactly the `/api/info` text, the first STL is drawn, every hash field
round-trips on fresh load, Reset and `hashchange`. It pins the query string the form sends
for each of the 44 fixture records before any later phase changes the form, and pins
`#root_shape=bogus` as it behaves today (filed as debt, not fixed). The file is excluded
from `make verify.fast` and `make test-image` by name in the commit that adds it, priced
A/B in `bench/RESULTS.md`, proved green on a real `ubuntu-latest` run, and recorded in one
`Lxx` that amends L13 and L36 and restates L11 unchanged.

The only production change is one line in `app.js`: `canvas.dataset.triangles`. No
`GearParams` field, no `calc`, `model`, `pool`, `app` or `cli` edit;
`git diff --exit-code tests/regression/pre_v0_2.json` is clean after every task. Order
inside the phase is fixed by the roadmap: spike first (WebGL, the Linux runner, strict
typing), then the server fixture and the scenarios, then gate admission in one commit, then
the cost and the `Lxx`.

</domain>

<decisions>
## Implementation Decisions

### Kickoff decisions confirmed (REQUIREMENTS.md records them; no measurement contradicted them)
- **D-01:** **Decision 1 — O1.** `tests/test_browser.py` runs inside `make verify`'s `test`
  and CI's `test (3.12)`; excluded from `test.fast` and `test-image` by name;
  `tests/test_hooks.py`'s `HEAVY_TEST_FILES` (`tests/test_hooks.py:24`) extended in the same
  commit and seen red when the `--ignore` is missing. The A/B price (D-10) goes in front of
  the human before the phase closes; an order-of-magnitude contradiction of the 3.2–3.8 s
  research figure reopens this. — **Reversibility:** costly — undoing means O2/O3/O4, a
  superseding `Lxx`, and for O4 `required-jobs.txt` plus the GitHub ruleset.
- **D-02:** **Decision 2 — hard failure, no opt-out.** A missing headless shell fails the
  test; no `importorskip`, no skip marker, no environment variable, in CI or locally; a pin
  fails if one appears. Message wording is D-06.
- **D-03:** **Decision 4 — no `pytest-playwright`.** Plain `playwright` pinned exactly in
  the `[dev]` extra (`pyproject.toml:20`; 1.63.0 at research time); the default Chrome
  Headless Shell, never `channel="chromium"`; `mypy --strict` passes with typed wrappers
  around `page.evaluate`.

### The scene observable (decision 3)
- **D-04:** **`canvas.dataset.triangles` only — the init-script draw counter is not built.**
  One line in `showModel` (`app.js:303`) after `scene.add(mesh, edges)` writes the triangle
  count of the parsed geometry (STL from `STLLoader` is non-indexed, so
  `position.count / 3`). The test fetches the same `api/model.stl?…&quality=preview` the
  page loaded and compares against the uint32 at byte 80 of the binary STL. Rejected: the
  `page.add_init_script` wrapper over `drawArrays`/`drawElements` (ARCH flagged it VERIFY IN
  SPIKE; it couples the test to three.js's draw path and the `EdgesGeometry` overlay, and a
  failed spike would leave the phase without an observable); both (a second observable to
  maintain for no extra proof). — **Reversibility:** costly — the `Lxx` names this line as
  the milestone's one production change and Phases 23–24's browser assertions sit on it.
- **D-05:** **Canvas non-blank check is a PNG byte-size ratio.** `locator('#canvas').screenshot()`
  before the first build (the blank control, same page) and after; assert the ratio clears
  a bar set from the spike's own reading and recorded beside it in `bench/RESULTS.md`
  (research starting points, not bars: 38,908 B vs 3,393 B on SwiftShader). Compositor
  readback, so `preserveDrawingBuffer: false` is irrelevant. Rejected: distinct-pixel count
  decoded in-page (more code, a typed `evaluate` wrapper for one coarse check); recording
  both.

### Browser install home
- **D-06:** **The shell lives under `.venv`: the Makefile exports
  `PLAYWRIGHT_BROWSERS_PATH := $(VENV)/ms-playwright` for the install stamp and for `test`.**
  The host's `chromium-1228` (another project) is never touched, `make clean` removes the
  browser with the venv, CI starts empty anyway (no cache — Playwright's own docs). The
  install is a Makefile stamp depending on `$(STAMP)` and a prerequisite of `test` only,
  never of `verify.static` or `test.fast`; `--with-deps` reaches it as a make variable from
  `ci.yml` (the runner needs the apt libraries; `.venv` does not exist before `make verify`,
  so the install cannot be a separate CI step). Rejected: the shared cache with
  `--no-remove` (isolation hangs on a flag never being dropped; `make clean` leaves ~200 MB
  behind); `conftest.py` setting the variable when unset (two places would know the path).
  — **Reversibility:** reversible — one Makefile variable.
- **D-07:** **The red test names the install command and the make path.** The message
  carries `playwright install --only-shell chromium` (REQ-browser-fails-closed) with the
  `PLAYWRIGHT_BROWSERS_PATH` the gate uses spelled out, and says `make test` (the stamp)
  runs it. A developer who ran bare `.venv/bin/pytest tests/test_browser.py` without the
  variable sees why it missed — the fail-closed rule holds; the message explains it.

### Golden request sweep (REQ-browser-golden-request-sets)
- **D-08:** **Route-captured, no builds.** One page; for each of the 44 records in
  `tests/regression/pre_v0_2.json` (`records`, keyed by name, each with `params`) the test
  sets `location.hash` from the record's params (`hashchange` calls `readHash(); update()`
  directly, `app.js:340` — no debounce); `page.route` captures the `api/info?…` request URL
  and aborts `api/model.stl` so no preview build runs. The pinned value is the `api/info`
  query string the form sends (it includes `mate_teeth` where a record sets it — the
  `README:info-mate-40+mate=40` record goes through `mateInput`, not `fields`). The
  server's acceptance of every set is already proved by `tests/regression`. Rejected: 44
  real builds per gate run (unmeasured kernel cost for a proof the regression suite already
  carries); route-captured plus one real build per bore family (the scenario test already
  draws a real part; more builds buy no new proof).
- **D-09:** **The pin is a committed file with a regen script behind a make target.**
  `tests/regression/golden_requests.json`: one entry per fixture record under the same name
  as `pre_v0_2.json`, value the exact query string. Written by a capture script (precedent:
  `make fixture.regen` → `tests/regression/capture.py`; the new target needs the browser
  stamp, since the capture drives the real page); the browser test asserts equality.
  Phases 23–24 must show an empty diff on this file, and a deliberate change is a regen
  commit saying what moved and why. Rejected: a Python predictor re-implementing
  `gearQuery()` (a second implementation, and "committed before any form change" would
  mean only the predictor); the test rewriting the file under a flag (an environment
  opt-out, which this project refuses). — **Reversibility:** costly — Phases 23–24's
  "same fields are sent" proof is this file's empty diff.

### Server topology and the admission price
- **D-10:** **One scenario test function, one server per gate run.** `tests/test_browser.py`
  holds one test walking every scenario in order — `webgl2` asserted first, then
  form-from-schema, first build drawn, invalid field marked, warning rendered, link round
  trip on all three paths, the golden sweep, the `#root_shape=bogus` pin — with a
  module-scoped fixture for the `uvicorn` subprocess. Under the current `--dist load` it
  lands on one xdist worker, so one `uvicorn` and one `BuildPool`; each step's assertion
  message carries the step name so a red line still says what broke. No scheduling change
  (`xdist_group` is a no-op under `--dist load`; changing scheduling is a gate-time change
  the roadmap flags for plan-phase and this choice avoids). Rejected: one test per REQ
  with a per-worker server (up to 8 `uvicorn`+`BuildPool` subprocesses, ~2–3 GiB RSS each,
  on a 4-vCPU runner); a cross-worker shared server through a lock file (coordination code
  in the fixture for readable red lines the step names already give).
- **D-11:** **The test server runs the pool the product ships: `SPUR_BUILD_WORKERS` at its
  default of 2**, no override in the fixture's environment (~2.9 GiB RSS at N=2, research
  memory read). The no-orphan check after `killpg` covers both children. Rejected: 1 (a
  shape the product does not run by default).
- **D-12:** **The admission A/B reading is N=3 per arm, interleaved.** Six full-gate runs,
  A/B/A/B/A/B (with and without `tests/test_browser.py`), `uptime` before and after each,
  host, load and `HEAD` beside each figure; flake-failed runs (the resource-tracker `must`
  debt, four recorded occurrences) are listed apart, classified, and re-run with a budget
  of N+3 attempts — never dropped silently, never a `filterwarnings` entry. This reading
  admits the file and sets no bar; Phase 25 sets the bar under its own pre-registered rule.
  Rejected: N=5 per arm (ten runs, ~32 min at the 193 s mean, for a reading that only
  admits).

### Claude's Discretion
- The concrete scenario parameters: which out-of-range value marks which field, and which
  warning-producing link is compared for equality against `/api/info`. The research names
  `#bore_hex=6` (warns every time on default `bore_d`/`bore_flat`) as the hex-link golden
  baseline; the planner picks and records the parameters.
- What `canvas.dataset.triangles` reads after a failed build. Leaving the previous count in
  place matches the status text "Showing the last valid gear"; the planner decides and the
  test asserts whatever is chosen.
- Whether the golden pin also records the `api/model.stl` query (`q` plus
  `quality=preview`) beside the `api/info` query, or derives it.
- Where the spike's readings and the deliberate-break evidence ("each assertion seen red
  once") are recorded — `bench/RESULTS.md` sections with host state are the precedent
  (`### The gate, priced (19-09)`).
- The exact Makefile names (`$(BROWSER)` stamp, the regen target, a `test.ui` convenience
  target if any), the `.gitignore` entry for browser artifacts, and how `ci.yml` passes
  `--with-deps`.
- The typed-wrapper shape around `page.evaluate`, the `expect` default timeout, and the
  wait signals — content-based (a rendered field count, a status text, a non-empty
  `#dl-stl[href]` set after `showModel` returns), never an empty status or a bare href
  (both pass before the 350 ms debounce fires).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scope and requirements
- `.planning/ROADMAP.md` — Phase 21 entry: goal, five success criteria, the four
  human decisions, boundaries, research flag, fixed task order
- `.planning/REQUIREMENTS.md` — the ten `REQ-browser-*` requirements, the "Rules every
  requirement lives by", "Form follow-ups" (the `#root_shape=bogus` debt), "Out of Scope"
- `.planning/PROJECT.md` — milestone v0.5 intent and success metrics

### Research (figures carry MEASURED / READ / DOCS tags; SUMMARY's disagreement table is authoritative)
- `.planning/research/SUMMARY.md` — "Where the Four Files Disagree" rows 8–12, 14, 15;
  "Decisions Reserved for the Human" 1–4
- `.planning/research/STACK.md` — Playwright 1.63.0 / Chrome Headless Shell 153.0.8010.12,
  `--only-shell`, `--with-deps`, `PLAYWRIGHT_BROWSERS_PATH`, browser GC, WebGL probe
  results, install costs, the `[dev]` pin and `PIP_CONSTRAINT` dry run
- `.planning/research/ARCHITECTURE.md` — the server fixture design (pre-bound socket,
  `--fd`, `killpg`), scenario list §3.3, the rejected init-script and `window.__spur`
  routes, §7.3 A/B price
- `.planning/research/PITFALLS.md` — BT-1 to BT-11 (no-WebGL form death, the 30 s slice,
  vacuous skips, shared globals, ports and orphans, wrong wait signals, no scene
  observable, install drift, coverage in a subprocess, flake attribution, a second
  definition of passing)
- `.planning/research/FEATURES.md` — the hex-link warning and `#root_shape=bogus`
  reproductions

### Decisions the `Lxx` amends or restates
- `docs/architecture/decision_log.md` — L02 (one parameter model, three front ends), L11
  (three.js vendored; no Node at runtime — restated unchanged), L13 (`make verify` is the
  gate — amended), L34 (gate measured, eight workers, coverage floor; the 66 s bar), L36
  (commit stage a named prefix under 30 s — amended), L38 (`root_shape` opt-in)
- `.planning/milestones/v0.4-phases/17-debt-first-commit-gate-and-pool-race/17-CONTEXT.md`
  — D-02..D-06: `test.fast` selects by exclusion; the Makefile shape `verify.static` /
  `verify` / `verify.fast`; the gate installs the hooks through `$(STAMP)` / `$(HOOKS)`

### The code under test and the gate it joins
- `src/spur/static/app.js` — `buildForm()` (:47), `readHash()` (:96), `gearQuery()` (:103),
  `problems()` (:122, the 422 `detail[].ctx.fields` path), `update()` (:176, debounce 350 ms
  at :220), `WebGLRenderer` at module top level (:229), `showModel()` (:303), wiring (:337)
- `docs/architecture/web-ui.md` — the viewer's design record
- `Makefile` — `$(STAMP)` / `$(HOOKS)` stamps (:34–75), `verify` / `verify.fast` /
  `test` / `test.fast` (:86–174), `test-image` (:186)
- `tests/test_hooks.py` — `HEAVY_TEST_FILES` (:24) and the `--ignore` pin (:121)
- `.github/workflows/ci.yml` — the `test (3.12)` job runs `make verify PYTHON=python` with
  `PIP_CONSTRAINT: requirements.txt`
- `tests/regression/pre_v0_2.json` and `tests/regression/capture.py` — the 44 records
  (`records` keyed by name, each with `params`) and the regen precedent
- `tests/test_api.py` — the untouched pins:
  `test_the_shareable_link_round_trips_every_field_through_generic_code` (:162) and
  `test_every_key_the_ui_reads_is_a_derived_dimensions_field` (:123)
- `bench/RESULTS.md` — `### The gate, priced (19-09)`: the host-state and three-run table
  format the A/B reading follows; the 192.94 s mean on the M5 Max, L34's 66 s bar on the
  M2 Max
- `docs/ideas/2026-09-21-browser-test-for-the-viewer.md` — retired in the commit that
  closes the phase
- `pyproject.toml` — `[dev]` extra (:20), `[tool.pytest.ini_options]` with
  `filterwarnings = ["error", …]` (:121)

### Standards
- `docs/CODING_VALUES.md` — comments carry the measurement or constraint; vendor types stop
  at their boundary
- `CLAUDE.md` — the gate, the two standing rules, debt filing rules

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/regression/capture.py` + `make fixture.regen`: the regen-script-behind-a-target
  pattern the golden request pin copies (D-09).
- `tests/regression/pre_v0_2.json` `records[name].params`: the 44 parameter sets the sweep
  loads through the hash; the defaults record is `{}`.
- `Makefile` stamps (`$(STAMP)`, `$(HOOKS)`): the browser stamp follows the same shape —
  a file under `.venv`, a dependency chain, no `|| true`.
- `tests/test_hooks.py`: already proves the `test.fast` `--ignore` set equals
  `HEAVY_TEST_FILES`; extending the tuple is the pin.
- `bench/RESULTS.md` section format: host state, runs table with `real`, load before →
  after, UTC; the A/B reading reuses it.
- `docs/tech_debt/TEMPLATE.md`, `docs/ideas/TEMPLATE.md` and their `INDEX.md`: the
  `#root_shape=bogus` debt file and the idea retirement.

### Established Patterns
- Tests test the real thing, never a mock of it (TESTING.md): real `uvicorn`, real
  `BuildPool`, real browser; observe through DOM, requests and the one dataset attribute.
- Test names read as requirements (`test_<requirement_as_phrase>`); one scenario test still
  names each step in its assertion messages (D-10).
- `filterwarnings = ["error", …]`: any warning Playwright's sync API emits is a failure
  unless it is real; no entry is added for the resource-tracker flake.
- `mypy --strict` over `tests/` too (`make typecheck` runs `src tests docker bench
  scripts`): `page.evaluate` returns `Any` and must be wrapped.
- Exclusion over inclusion in `test.fast` (17 D-04): the new file is named in `--ignore`,
  not marked.
- `app.js` field genericity pins in `tests/test_api.py` (:123, :162) are not touched; the
  one new `app.js` line must not add a `['word',` row or a `GearParams` field name.

### Integration Points
- `src/spur/static/app.js:303` `showModel` — the one production line.
- `Makefile` `test:` recipe — gains the browser stamp prerequisite and exports
  `PLAYWRIGHT_BROWSERS_PATH`; `test.fast:` gains `--ignore=tests/test_browser.py`;
  `test-image:` excludes the file by name.
- `.github/workflows/ci.yml` `test` job — passes the `--with-deps` make variable; the real
  `ubuntu-latest` run id and wall time go into `bench/RESULTS.md`.
- `pyproject.toml` `[dev]` — `playwright==<exact>`; the 31-pin runtime closure,
  `Dockerfile` and `docker/refresh-requirements.sh` do not move.
- `.gitignore` — browser artifacts (screenshots, traces if any).
- `docs/architecture/decision_log.md` — the new `Lxx`.

</code_context>

<specifics>
## Specific Ideas

- "A green gate means the browser ran": the fail-closed message explains the `.venv` path so
  a bare `pytest` run that misses the browser is a clear red, not a confusing one (D-07).
- The sweep must stay cheap — hash-driven, request-captured, the STL route aborted — so the
  file's isolated cost stays near the 3.2–3.8 s research figure (D-08); the scenario test
  draws exactly one real part.
- The A/B table copies the 19-09 shape: host, `HEAD`, UTC, load before → after, result line,
  `real`; flake runs in their own rows (D-12).
- Research figures (PNG sizes, pixel counts, 3.21 s / 3.80 s) are starting points; every
  bar the test asserts is set from a reading taken in this phase and recorded with it.

</specifics>

<deferred>
## Deferred Ideas

None new — discussion stayed within phase scope. Already deferred by REQUIREMENTS.md "Form
follow-ups" and touched here only as pins: the `#root_shape=bogus` blank-select behaviour
(pinned, filed as debt in this phase, not fixed); the stale-response test under a slow
build; re-sweeping the xdist knee on the 18-CPU host. The init-script draw counter is
rejected (D-04), not deferred.

</deferred>

---

*Phase: 21-browser-test-of-the-viewer*
*Context gathered: 2026-10-10*
