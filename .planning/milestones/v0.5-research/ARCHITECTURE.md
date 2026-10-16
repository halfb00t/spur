# Architecture Research: v0.5 "Honest Form"

**Domain:** Subsequent milestone on a shipping parametric-CAD web app (FastAPI + CadQuery + vanilla-JS/three.js viewer)
**Researched:** 2026-10-10
**Confidence:** MEDIUM overall. Every claim about *existing* code is HIGH (read from the files named). Claims about headless-Chromium WebGL, xdist scheduling and the cost of the browser test are MEDIUM/LOW: nothing in this document was run, and each is tagged `ASSUMPTION` or `VERIFY IN SPIKE` where it matters.

Scope rule held throughout: no new `GearParams` field, no change to what any existing shareable link means (L05), the 44-record fixture untouched (L26), the form generated from `/api/schema` alone (L02).

---

## 1. Standard Architecture

### System overview: what exists, and where v0.5 plugs in

```
                       ┌──────────────────────── tests (pytest, -n 8, --cov) ───────────────────────┐
                       │  test_api  test_cli  test_model  test_pool  ...   NEW: test_browser.py      │
                       │                                                       │ (heavy tier)        │
                       └───────────────────────────────────────────────────────┼─────────────────────┘
                                                                               │ spawns
  GearParams (params.py) ── model_json_schema() ──► GET /api/schema ──┐        ▼
   _f(): group, unit, step                      (app.py:373, no edit) │   ┌───────────────────────┐
   NEW: enabled_when, selector metadata                               │   │ subprocess: uvicorn   │
   MOD: slug()  ──► app.py:496 Content-Disposition (no edit)          │   │ spur.app:app --fd N   │
              └──► records.py:180 _gear_fields  (no edit)             │   │  └ BuildPool workers  │
                                                                      ▼   └───────────▲───────────┘
  static/app.js (372 lines)                                                           │ http
   buildForm ─ stores relations ─► NEW applyRelations() ─► .field.inactive            │
   readHash/gearQuery (flat fields, URL contract UNCHANGED)                   headless Chromium (Playwright, sync API)
   NEW: bore selector (derived, never serialised)                              asserts on DOM, download name,
   update() ─► /api/info + /api/model.stl ─► showModel() ─► WebGLRenderer      draw calls (init-script), not on app.js internals
```

The load-bearing structural fact: **`/api/schema` is `GearParams.model_json_schema()` with no transformation** (`app.py:373-375`), and `app.py` and `records.py` consume `slug()` only by calling it. So all four user-visible features (relations, selector, slug, and the browser test's view of them) are reached by editing `params.py`, `app.js`, `style.css` and tests. **`app.py`, `records.py`, `calc.py`, `model.py`, `pool.py`, `cli.py` need no edit** (one optional exception for the slug, §6).

### Component responsibilities (new vs modified, per file)

| File | Status | v0.5 change |
|------|--------|-------------|
| `src/spur/params.py` | MOD | `_f()` gains `enabled_when`; ~14 numeric fields get relations; selector metadata; `slug()` suffix for a non-default root. No new field. |
| `src/spur/static/app.js` | MOD | `buildForm` keeps each field's relations; `applyRelations()`; selector built from schema metadata. No field name written in the file (§4, §5). |
| `src/spur/static/style.css` | MOD | `.field.inactive`, a "set but ignored" tone, selector styling. |
| `src/spur/static/index.html` | none | The form is built by JS into `<form id="params">`. |
| `src/spur/app.py`, `records.py`, `calc.py`, `model.py`, `pool.py`, `cli.py` | none | Schema route and `Content-Disposition` call existing code. |
| `tests/test_browser.py` | NEW | Server fixture, browser fixture, scenarios (§3). One file, so it fits the existing "heavy file" machinery. |
| `tests/test_params_relations.py` | NEW (light) | Relation well-formedness + the inertness proof (§4). Runs in `verify.fast` (needs no TestClient, no kernel). |
| `tests/test_hooks.py` | MOD | `HEAVY_TEST_FILES` gains `"test_browser"` (the assertion at line 121 builds `tests/{n}.py` from it). |
| `tests/test_api.py` | MOD | Lines ~376/412: the trochoid download name flips; ~720 (radial default) must NOT change; `test_schema_drives_the_form` gains a relation assertion. |
| `tests/test_cli.py` | MOD | The model-driven field walk (`:198`) extended (§4). |
| `Makefile` | MOD | `$(BROWSER)` stamp, `test.ui`, `test.fast --ignore=tests/test_browser.py`, `.PHONY`, comments quoting `63.555 s`. |
| `.pre-commit-config.yaml` | MOD (comment) | "four heavy files" and `63.555 s`. |
| `.github/workflows/ci.yml` | MOD | Browser install (args + cache) inside the existing `test (3.12)` job. `required-jobs.txt` unchanged. |
| `pyproject.toml` | MOD | `[dev]` += `playwright`. (`markers` only if a marker is chosen; §3.5 recommends not.) |
| `docs/architecture/decision_log.md` | MOD | Up to five new `Lxx` (browser-in-gate amending L11/L13/L36; relations superseding 08 D-09; selector; slug; L34 re-set). |
| `docs/architecture/web-ui.md`, `http-api.md`, `docs/HOW_TO_DEVELOP.md`, `README.md` | MOD | "There is no browser test" (web-ui.md "Tests"), `http-api.md:43,93`, the `~64 s` gate figure, the reverify paragraph, the Pi 5 sentence. |
| `bench/RESULTS.md` | MOD (append) | Browser-test price; idle-host gate reading. |

---

## 2. Recommended Project Structure (additions only)

```
tests/
├── test_browser.py            # NEW  server + browser fixtures + scenarios; heavy tier
├── test_params_relations.py   # NEW  schema/relation proofs; light tier (runs at commit)
bench/RESULTS.md               # +    "Browser test admitted (Phase N)", "The gate re-set (Phase M)"
```

### Structure rationale

- **One file, not a `tests/browser/` directory.** `test.fast` excludes by `--ignore=tests/<name>.py` and `test_hooks.py` pins that set as `{f"tests/{n}.py" for n in HEAVY_TEST_FILES}` (`:121`). A file is a one-token edit; a directory breaks the helper's shape. Fixtures live in the same module (module-scoped) so `tests/conftest.py` and every other file stay unaware of Playwright.
- **Relation proofs split in two.** The pure-schema half is cheap and belongs at the commit boundary (L36 sells "a new test file runs at commit until someone names it heavy"); the browser half is heavy by nature.

---

## 3. (a) The browser test: reaching the real app

### 3.1 Server fixture: three designs

| Design | How | Verdict |
|--------|-----|---------|
| **A. Subprocess uvicorn on an inherited socket (recommended)** | Test binds `127.0.0.1:0`, `listen()`s, passes the fd with `pass_fds`, runs `python -m uvicorn spur.app:app --fd N` with `start_new_session=True`. Readiness: poll `/api/health` until `pool` is non-null (`app.py:361`). Teardown: SIGTERM the process group, wait, then SIGKILL. | Real lifespan, real `BuildPool`, real gzip middleware, real abort behaviour. No import-time coupling to the test process. |
| B. uvicorn in a thread of the pytest process | `uvicorn.Server(Config(app, port=0))` on a thread | **Reject.** `app` is a module-level singleton (`app.py:166`): `tests/test_pool.py` runs `with TestClient(app)` thirteen-plus times, and each lifespan ends in `del app.state.pool` (`app.py:163`). Two lifespans on one `app` in one process collide. `MAX_QUEUED_BUILDS`/`BUILD_QUEUE` are computed at import (`app.py:101-102`), so `SPUR_BUILD_WORKERS` set later changes nothing. `test_api.py` installs `dependency_overrides[build_backend]` at module scope on the same object. |
| C. No server: Playwright `page.route("**/*")` fulfilled from a `TestClient(app)` with the inline backend | Fake origin, static files and `/api/*` answered in-process | Cheapest (no port, no pool, no process) but tests a transport the product does not use: no gzip middleware, no `Content-Disposition` navigation download, no real `AbortController` against a live socket. Keep as the **fallback** if A proves too slow or flaky on the CI runner. |

**Why `--fd` and not a picked port.** The suite runs on up to 8 xdist workers (`PYTEST_WORKERS`, Makefile `:146`; CI clamps to 4). If each worker that runs a browser test picks "a free port" by bind-close-reuse, two can race. Binding in the parent and handing the open socket to the child removes the race entirely, and each worker owns its own socket, so no cross-worker coordination exists to get wrong. (`spur serve` is not exercised by this fixture; the CI `image` job already curls the packaged entrypoint, and `cmd_serve` is `configure()` plus one `uvicorn.run`.)

**Fixture hygiene specific to this repo:**

- Build the child's environment explicitly: copy `os.environ`, **drop every `SPUR_*`**, then set what the test needs. `bench/RESULTS.md` "Host state" records "SPUR_* environment: none set"; a developer's exported `SPUR_BUILD_TIMEOUT` must not change what the test measures.
- `SPUR_BUILD_WORKERS`: leave at the shipped default of 2 (`app.py:137`) unless the admission measurement says startup is the problem. With 2 workers `SPUR_MAX_QUEUED_BUILDS` derives to 4 (`app.py:98`). The documented known gap, that aborting a fetch does not cancel the server build (`web-ui.md` "Known gap"), means a test that edits fast can queue builds and get a `503 busy`. **The test must wait for each build to settle before the next edit** (wait on the new `href`, not on timers).
- Write the child's stderr to a temp file, not a `PIPE` (deadlock on a full pipe), and print its tail on any fixture failure. `filterwarnings = ["error"]` (pyproject) turns a leaked `ResourceWarning` (unclosed socket/Popen) into a test failure, so close the listening socket in a `finally`.
- Readiness timeout generous (order of 120 s): the repo's own docs say a cold page cache takes "a couple of minutes", and `BuildPool` warms eagerly (spawn + `cadquery` import) before `lifespan` yields.
- Coverage: the server is a plain `subprocess`, which `concurrency = ["multiprocessing", "thread"]` does not follow, and pytest-cov 7 has no subprocess hook. So the child contributes **zero** `src/` coverage. That is neutral for `fail_under = 96` (97.92 % today), not a gain and not a loss.

### 3.2 xdist: one server per worker that runs a browser test

`--dist load` (the default here) gives no ordering guarantee (pytest-xdist docs, LOW tier via web search), so browser tests can land on several workers, each paying server + Chromium start-up. Three ways to bound it:

1. **`@pytest.mark.xdist_group("browser")` on the module + `--dist loadgroup`** in the `test` recipe. Grouped tests share one worker; ungrouped tests schedule exactly as `load`. One flag on the Makefile `pytest` line; `test_hooks.py` compares the two recipes only up to `-n N` (`through_worker_count`), so add it after `-n`. Deterministic. **Recommended.**
2. One scenario-walk test function (no scheduling change; failure messages name the step). Simplest; coarser failures.
3. Accept N servers (correct, just wasteful: each worker is isolated by its own socket).

`test_hooks.py:113` also asserts `"--ignore=" not in whole_pytest`; nothing here adds an `--ignore` to the whole gate.

### 3.3 What the test can assert about the three.js scene from outside

`renderer`, `scene`, `mesh`, `box` are module-scoped `const`/`let` inside an ES module (`app.js:229-250`): **nothing is on `window`**, and the quality gate rules out adding a hook. The ladder, strongest evidence per unit of fragility first:

| # | Evidence | Mechanism (no production change) | Fragility |
|---|----------|----------------------------------|-----------|
| 1 | Form built from the schema | `#params .field` count and group order equal what `GearParams.model_fields` / `json_schema_extra["group"]` say (computed in Python from the model, not from the schema consumer) | Low |
| 2 | Invalid field marked | Load a link the API answers 422 with `ctx.fields`; assert `.field.invalid` contains exactly those inputs. Take the expected set from the test's own `urllib` call to the same server. | Low |
| 3 | Warning renders | `#messages p.warning` text contains the sentence `derive()` emits (e.g. "Hex bore replaces the round profile") | Low |
| 4 | **STL reached the scene** | In `update()`, `setDownloads(q)` runs only *after* `showModel(buf)` returned (`app.js:212-213`). So `#dl-stl` having an `href`, no `aria-disabled`, empty `#status` and no `p.error` proves `loader.parse` + scene insertion did not throw. | Low |
| 5 | Geometry actually submitted to the GPU | `page.add_init_script` wraps `WebGL2RenderingContext.prototype.drawArrays/drawElements` to count vertices drawn with mode `TRIANGLES`; assert it equals 3 × the triangle count in the STL header (uint32 at byte 80) of the same file fetched by the test. Deterministic, hardware-independent. | Medium. `VERIFY IN SPIKE`: confirm three's STL path uses `drawArrays` and the count survives the edge overlay and rAF coalescing. |
| 6 | Pixels | `locator('#canvas').screenshot()` then count non-background pixels *in the page* (decode via `Image` + 2D canvas in `evaluate`; no Pillow). Background from `getComputedStyle(documentElement).getPropertyValue('--view-bg')`. Coarse threshold only. | High. `toDataURL()` on the canvas is unreliable: `new WebGLRenderer({ canvas, antialias: true })` leaves `preserveDrawingBuffer` false. |
| 7 | Download name | `with page.expect_download() as d: click('#dl-stl')`; assert `d.value.suggested_filename`. The anchor has no `download` attribute; navigation to a `Content-Disposition: attachment` response fires the event. This is what the user sees, and it is the browser-level proof for §6. | Low. Note the link requests the default quality (a second, fine build). |

**Rejected: `window.__spur = {scene}` or any exported handle.** It changes the production surface and invites the test to couple to internals; the init-script route above needs none. **Rejected: asserting pixel-exact colours** (SwiftShader and GPU output differ).

**Load-bearing coupling (HIGH, from reading the file).** `const renderer = new WebGLRenderer(...)` runs at module top level (`app.js:229`), *before* the async IIFE that calls `buildForm()` (`:361`). If Chromium cannot create a WebGL context, the module throws and **the form never builds**. Every form assertion therefore depends on WebGL in the test browser. Fail early with an explicit message (a one-line `page.evaluate` that creates a WebGL context, asserted before any scenario), and pass launch arguments for CPU rendering. `VERIFY IN SPIKE` (LOW, web search): headless Chromium on a GPU-less Linux runner generally needs `--enable-unsafe-swiftshader` (optionally `--use-gl=angle --use-angle=swiftshader-webgl`) for WebGL; confirm on macOS arm64 and on `ubuntu-latest` before writing a single scenario. This spike is the first task of the browser phase.

**Wait conditions (HIGH).** `update()` calls `setDownloads(null)` synchronously and the next `update()` is debounced 350 ms (`app.js:221-224`), so "href is set" is ambiguous right after an edit (the old href is still there until the debounce fires). Wait on the *expected* href substring (`bore_hex=6`) or on `location.hash`, never on `#status === ''` alone (it is `''` before the first update too).

### 3.4 `window`-level state the existing static test already pins

`test_the_shareable_link_round_trips_every_field_through_generic_code` (`test_api.py:162`) asserts, by regex over `app.js`, that **no GearParams name appears as a quoted literal or as `.name` outside the `DIMS` block**. It is the standing guard on L02's spirit, it stays (cheap, and the browser test does not replace it), and it **constrains the new JS**: the relation evaluator and the selector may not name `bore_hex`, `spoke_count`, etc. (§4, §5 are designed around that).

### 3.5 Where the browser test sits in the gate: every option with its consequences

Facts that decide it (HIGH): `make verify` = `verify.static` + one `test` recipe; `verify.fast` = `verify.static` + `test.fast`; `tests/test_hooks.py:86-121` pins "exactly one pytest line" per recipe, `--cov` in the whole, `--no-cov` in the slice, and the exact `--ignore` set; L36 sells exclusion-by-name "never a marker". Gate wall time today is 192.94 s mean (Phase 19, accepted `accept-A`) against L34's 66 s; CI runs `-n 4` on 4 vCPUs.

| Option | `verify.fast` (30 s kill, 11.4 s today) | `make verify` (pre-push, CI, `worktree.land`) | CI `test (3.12)` | Coverage | What must be edited |
|--------|------|------|------|------|------|
| **O1. In `test` (so in `verify`), excluded from `test.fast`; plus `make test.ui` for the file alone (recommended)** | Unchanged: `--ignore=tests/test_browser.py` | Runs inside the `-n` pool; cost = its own duration if it lands in the tail, up to + its full duration if dispatched last. `ASSUMPTION` (unmeasured): one worker, 10-25 s. Collection order puts `test_browser.py` early in the alphabet; grouping (§3.2) makes it deterministic. | Same job, no new required check. Needs Chromium on the runner: `playwright install [--with-deps] chromium`, cacheable. | None (child unmeasured) | `Makefile` (`test.fast` ignore, `$(BROWSER)` stamp as a prerequisite of `test`, `test.ui`), `test_hooks.py` (`HEAVY_TEST_FILES`), `.pre-commit-config.yaml` comment, `test-image` (§below), docs, new `Lxx` amending L36 |
| O2. `make test.ui` only, not in `verify` or CI | Unchanged | Unchanged | Unchanged | None | Almost nothing, **but** a UI regression merges unseen. Defeats the purpose (it is the trigger both UI features named) and breaks L13's "one definition of passing". Acceptable only as a stop-gap inside the browser phase. |
| O3. A second, sequential stage: `verify: verify.static test test.ui` | Unchanged | Adds exactly T_ui to the wall (not hidden in a tail); the browser is isolated from the 8-worker CPU contention, which lowers flake risk. `test` must then ignore the file or run it twice. | Same | None | **Breaks `test_hooks.py:92` (`len(pytest_lines) == 1`) and L36 D-03's "ends in one pytest recipe"**; needs a superseding `Lxx` and a rewrite of that test. The most invasive option. |
| O4. A separate CI job `ui (3.12)` | Unchanged | Not run by `make verify`; local pre-push does not see UI regressions | Runs in parallel, CI wall unchanged | None | New job must be added to `.github/workflows/required-jobs.txt` (drift-tested by `tests/test_pr_land.py`) **and** to the live ruleset on `main` (a GitHub setting the human changes). Violates L13. |
| O5. Also in `verify.fast` | Adds browser launch + server warm-up to a slice with ~19 s of headroom; a cold start or contended CPU can cross the 30 s SDK kill, and a killed commit leaves an **orphan hook running** (L36 D-07), now holding a server and a Chromium | Same as O1 | Same | None | Reject. |

**Consequences common to O1/O3:**

- `mypy src tests docker bench scripts` (`make typecheck`) imports `playwright` from `tests/test_browser.py`, so `[dev]` must carry it for **every** tier including `verify.fast`; only the *browser binary* is optional for `verify.fast`.
- `make test-image` runs `pip install pytest httpx` then `pytest` over the whole `tests/`: `import playwright` fails at collection. Add `--ignore=tests/test_browser.py` there (that target already runs a partial toolchain). Do not paper over it with a silent `importorskip`: a skipped UI test is exactly the "silent partial success" this repo rejects. Missing browser in `verify`/CI must be a loud failure with the `playwright install` hint.
- **Browser install placement.** `.venv` is created *inside* `make verify` (the `$(STAMP)` recipe), so a CI step before it cannot call `.venv/bin/playwright`. Keep local and CI identical with a Makefile stamp, `$(VENV)/.browser: $(STAMP)` running `$(PY) -m playwright install $(BROWSER_INSTALL_ARGS) chromium`, and let CI pass `BROWSER_INSTALL_ARGS=--with-deps`. Browsers are cached outside the venv (`~/Library/Caches/ms-playwright`, `~/.cache/ms-playwright`), so `make clean` does not remove them and worktrees share them; key a CI `actions/cache` entry on the playwright version.
- `PIP_CONSTRAINT: requirements.txt` (CI) only constrains names listed in the 31-line runtime closure; `playwright`, `greenlet`, `pyee` are not in it. Check `typing-extensions` compatibility during the `make venv` probe (§8 Phase E).
- The Playwright wheel bundles its own Node-based driver. That is the honest answer to L11's "Node at test time": **no system Node is required** and `vendor-bundle` remains the only job with `setup-node`; but a Node process does run during the test. Say so in the new `Lxx`. (STACK researcher owns pricing the wheel/browser size.)

**Recommendation: O1**, with the file grouped on one xdist worker, the server as design A, and the `Lxx` recording: headless browser admitted to `verify`/CI, excluded from the commit slice, cost measured before accepted (§7).

---

## 4. (b) `enabled_when`: data flow end to end

### 4.1 Where the relation is declared and how it travels

```
params.py  _f(..., enabled_when=[when("spoke_count", "gt", 0)])
   │  extra["enabled_when"] = [{"field": "spoke_count", "op": "gt", "value": 0}]
   ▼  Field(json_schema_extra=extra)
GearParams.model_json_schema()["properties"]["hub_d"]["enabled_when"]      (pydantic merges the dict verbatim)
   ▼  GET /api/schema  (app.py:373, no edit)
buildForm(): relations.set("hub_d", prop.enabled_when ?? [])
   ▼  applyRelations()  (initial, every `input`, readHash, reset, update)
.field.inactive on label.field
```

**Shape (recommended).** Always a list of AND-ed conditions; each `{field, op, value}` with `op ∈ {eq, ne, gt, ge}` and a number or string `value`. One uniform shape keeps the JS to a dozen lines and serves the selector too (§5). AND-only is a deliberate limit: an OR case (e.g. `bore_chamfer` live when either `bore_d` or `bore_hex` is set) stays unconditioned, which is honest, not a bug.

**`_f()` change** (`params.py:17`): add `enabled_when: list[JsonDict] | None = None`, assign `extra["enabled_when"]` as a `list[JsonValue]` (mypy strict + `disallow_any_explicit`: `list[dict[str, JsonValue]]` is not assignable to `list[JsonValue]` by invariance; build it typed). A tiny `when(field, op, value) -> JsonDict` keeps call sites to one line. The two `Literal` fields built with bare `Field(...)` (`root_shape`, `recess_sides`) are only ever *drivers*, so they need no change.

**Proposed relation set** (to be settled by the proof in §4.3, not asserted from memory):

| Dependents | Active when |
|------------|-------------|
| `bore_d`, `bore_flat` | `bore_hex eq 0` (hex replaces the round profile; `calc.py:1159-1167` already warns "ignored") |
| `keyway_width`, `keyway_depth` | `bore_hex eq 0` and `bore_d gt 0` (hex x keyway is a 422; no bore is a 422) |
| `recess_depth`, `recess_width`, `recess_inner_d`, `recess_fillet` | `recess_sides ne "none"` |
| `spoke_width`, `hub_d`, `rim_wall`, `spoke_fillet` | `spoke_count gt 0` (`calc.py:1207-1218`) |
| `hole_d`, `hole_circle_d` | `hole_count gt 0` (`calc.py:1220-1229`) |
| `hex_wall` | `hex_cell gt 0` (`calc.py:1241-1247`) |

**Drivers are never dependents.** The three cutout selectors are mutually exclusive (a 422 naming every set selector), but making `spoke_count` inactive "when `hole_count > 0`" would trap a user who opens a link with both set (it is a 422) with both dimmed. Mutual exclusion stays the server's 422; the form never dims a driver.

### 4.2 How `buildForm` applies it with no field-specific JS

```js
// evaluation uses the SAME effective value gearQuery() sends, so the dim state can never
// disagree with what the server receives (an emptied number box means "default").
const effective = (n) => { const v = fields.get(n).input.value; return v === '' ? defaults[n] : v; };
const holds = ({ field, op, value }) => {
  const a = typeof value === 'number' ? Number(effective(field)) : String(effective(field));
  return op === 'eq' ? a === value : op === 'ne' ? a !== value : op === 'gt' ? a > value : a >= value;
};
```

Call `applyRelations()` from: end of `readHash()` (covers first load and `hashchange`), the form `input` listener *before* `scheduleUpdate` (so dimming does not wait the 350 ms debounce), and the `#reset` handler (it writes `input.value` directly and bypasses `input` events, `app.js:345-349`). Do not hang it on a successful build: the state must follow the fields even when the server answers 422. No field name appears in the file, so the static generic-code test still passes.

### 4.3 The two traps this design must avoid (HIGH, derived from the code)

1. **Never use the HTML `disabled` attribute on a field that holds a value.** A shared link such as `#spoke_count=0&hub_d=40` loads with `hub_d` carrying 40; the server warns "hub_d (40 mm) is ignored". A disabled input cannot be focused, so the user *cannot clear it* and the link keeps warning. L05 forbids the UI from silently zeroing it. Design: **inactive = visual only** (`.field.inactive`, dim, a "ignored while <driver title> is <value>" hint built from the relation and the schema `title`s), the input stays editable and tab-reachable; if an inactive field holds a non-default value, switch it to a "set but ignored" tone that mirrors the server's own warning. If the human insists on true `disabled`, restrict it to fields at their default.
2. **A relation is a second statement of a rule `calc.py` already owns.** Drift is the risk: dim a field that is in fact live and the form lies. Guard it with a proof that is one-directional on purpose (L08): *with the relation false, changing the dependent field changes nothing in `derive(p)` apart from `warnings`* (and, for the few that matter, not the built volume). The converse (relation true implies live) need not hold. This is a calc-only test (no kernel), runs at commit in `tests/test_params_relations.py`, and it will settle the open rows above (`bore_flat` with `bore_d == 0`; the recess rows, which have no "ignored" sentence to cross-check, so inertness is the only possible proof).

### 4.4 Extending the model-driven field walk

`test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order` (`test_cli.py:198`) already walks `GearParams.model_fields`. Add, never reading `app.js` or the schema as the source of truth:

- **Schema:** for each field whose `json_schema_extra` carries `enabled_when`, `props[name]["enabled_when"]` equals it (JSON round-trip), every `field` exists in `model_fields`, `op` is in the allowed set, `value`'s type matches the driver's annotation (number for numeric, a member of the enum for `Literal`), no dependent is also a driver (depth 1, no cycles).
- **Form (browser tier):** from the model, compute the expected inactive set for a handful of states (defaults, then each driver flipped: `bore_hex=6`, `spoke_count=3`, `hole_count=3`, `hex_cell=3`, `recess_sides=none`) with a ten-line Python evaluator; set `location.hash`, wait for `hashchange` handling, and compare `.field.inactive` to it. One page, no builds needed (422s are fine, the state is independent of them).
- **Link with a set-but-ignored value** (`#hub_d=40`): field not `disabled`, marked ignored, value kept in the query, server warning displayed, hash unchanged by the dimming.

`/api/schema` carrying the key also needs one added assertion in `test_schema_drives_the_form` (`test_api.py:58`).

**Decision log:** a new `Lxx` supersedes **08 D-09** (a phase-8 context decision, not an `Lxx`); **L02 is kept and is the argument**: the relation lives on the model and reaches the form through the schema.

---

## 5. (c) The bore-shape selector

### 5.1 The conflict to surface at discuss-phase (HIGH)

PROJECT.md asks for "a UI-only select in `app.js`" and also says "a field relation lives in schema metadata on the model, never hard-coded in `app.js`". A select whose options are *round / D-flat / hex / none* **is** a relation (shape = f(`bore_d`, `bore_flat`, `bore_hex`)). Written literally in JS it forces named fields into `app.js` and fails the standing generic-code test (§3.4), whose own comment names "a conditional-field or bore-selector patch" as the thing it exists to catch. Two designs:

| | Where the shape table lives | Consequence |
|---|---|---|
| **S1 (recommended): schema-carried** | A model-level `json_schema_extra` (`ConfigDict`) entry, e.g. `selectors: [{title, group, options: [{label, when: [...conditions...]}]}]`, written in the *same condition vocabulary* as §4. `app.js` stays field-name-free; one evaluator serves relations and the selector. | No new `GearParams` field (metadata only). `InfoQuery`/`ModelQuery` subclass `GearParams` (`app.py:232,237`) and inherit the config, so their OpenAPI component schemas carry the key too (harmless; `group`/`unit` already do). Honours the milestone rule as written. |
| S2: bore-specific JS | `if (bore_hex > 0)` in `app.js` | Matches the idea file's wording ("accepting the first bore-specific logic in `app.js`") but breaks the milestone's own rule and requires an explicit allow-list in the generic-code test, i.e. weakening the guard. |

### 5.2 Behaviour (design S1)

- **Derived, not stored.** On load and on `hashchange` the selected option is the first whose conditions hold over the current field values (the §4 `holds`). It is never written to the URL: `readHash` and `gearQuery` are untouched, so every shared link sends exactly the flat fields it always did (L05).
- **Four states from the flat fields:** hex (`bore_hex > 0`); D-flat (`bore_hex == 0`, `bore_d > 0`, `bore_flat > 0`); round (`bore_hex == 0`, `bore_d > 0`, `bore_flat == 0`); none (`bore_hex == 0`, `bore_d == 0`). The shipped default (`bore_d 9`, `bore_flat 8`) is **D-flat**. The keyway is a modifier of round and D-flat (L27 research rejected a `bore_type` discriminator for exactly that reason), so it stays a set of fields governed by the §4 relation, not a fifth option.
- **A choice writes only switch-offs, never invents a dimension.** Selecting Round writes `bore_flat = 0` and `bore_hex = 0`; selecting None writes `bore_d = 0` and `bore_hex = 0`. Selecting Hex or D-flat when `bore_hex`/`bore_flat` is 0 cannot write a size (no `eq`-style condition produces one): the select stays on the chosen option as pending UI state, the matching field is un-dimmed and focused, and the part is unchanged until the user types. A reload re-derives and drops the pending choice. This is the one rule that keeps "a parameter the user did not set must never silently change the part" true for a control that offers choices. `ASSUMPTION`: the human may prefer a starter value (the schema default for `bore_flat` is 8); that is a UX decision to put to them with both priced, not a research default.
- **Selecting Hex does not zero `bore_d`/`bore_flat`.** Non-destructive and reversible; the dimmed fields plus the existing server sentence ("Hex bore replaces the round profile: bore_d (9 mm) and bore_flat (8 mm) are ignored") stay accurate.

### 5.3 Interaction with the existing ignored-field warnings

The warnings come from `derive()` and render through `renderInfo` to `showMessages` (`app.js:152`). Nothing in v0.5 suppresses them. The selector and the relations *predict* them (dimmed fields) but the server remains the authority, so the idea file's claim that a selector "prevents the ignored combination" is only visually true. The browser test pins the agreement: a field shown inactive-and-set and a warning naming the same field must appear together.

---

## 6. (d) The slug change

### 6.1 Every consumer of `GearParams.slug()` (HIGH, grepped)

| Consumer | Location | Effect of a new slug | Action |
|----------|----------|----------------------|--------|
| Definition | `params.py:190` | the change | edit |
| Download name | `app.py:496` `Content-Disposition: attachment; filename="{slug}.{fmt}"` | the user-visible rename; built per response, **outside** the `_EXPORTS` byte cache (`app.py:494-504`), so no stale name can be served from cache | none |
| Structured records | `records.py:180` `_gear_fields` -> `build.started`, `build.failed`, `export.served`, `queue.refused` (4 emitters at `:218,231,255,267`) | the `slug` field of every per-request record changes for affected gears; `params` is separate and unchanged | none; note in the `Lxx` that log greps keyed on slug see a new value for non-default roots only |
| Temp file stem | `model.py:807`, `bench/export_cost.py:176`, `tests/test_model.py:2021` | a `tempfile` stem the user never sees | none |
| Docs | `docs/architecture/http-api.md:43` (and `:93` for records) | wording | update |
| Frozen history | `.planning/**`, `docs/tech_debt/resolved/…no-structured-logging.md` | contain old example slugs | do not edit |

CLI: `spur export -o` takes the caller's own name (`cli.py:141`); no slug use. `tests/regression/pre_v0_2.json` contains **no** `spur_z` string, so the fixture cannot move.

### 6.2 What pins the old names

- `tests/test_api.py:412` asserts `filename="spur_z23_m1.75_pa25.stl"` for a **trochoid** download, with a docstring at `:376` explaining the slug "ignores root_shape (19-RESEARCH…)". This one must flip, deliberately, in the slug commit.
- `tests/test_api.py:720` asserts `spur_z21_m1.75_pa25.{fmt}` for a **default (radial)** gear. This must **not** change.
- `tests/test_records.py:60,89,95` use a synthetic `slug="spur_z19"`; not tied to `slug()`.

### 6.3 Recommended shape

Append a suffix **only when the root is not the default**, keeping every existing name, every logged slug and the `:720` pin byte-identical (the same "absent means unchanged" discipline as L05, applied to names):

```python
base = f"spur_z{self.teeth}_m{self.module:g}_pa{self.pressure_angle:g}"
return base if root_is_radial else f"{base}_trochoid"
```

**One decision for discuss-phase:** `root_is_radial` by *request* (`self.root_shape == "radial"`, a pure string, simple) or by *effect* (`calc.root_mode(...).mode`). The field help says trochoid applies "where the base circle lies above the root circle and warned about elsewhere", so a request for it on a 30-tooth gear builds a **radial** part with a warning (`calc.py:1707`): a request-based name would label a radial part "trochoid". An effect-based name is the honest one and is the third consumer of the single predicate L38 built; cost: a local import of `calc` in `params.py` (the pattern `_feasible` already uses at `params.py:180`) and a `profile(p)` + `root_mode` call per record emission (`derive()` measured 10-30 us). Recommend effect-based; flag it, since it makes `slug()` depend on a solver. Either way: new `Lxx`, and the browser test's `expect_download` (§3.3 row 7) is the end-to-end proof of the user-visible name.

---

## 7. (e) Re-setting the gate bar: a protocol consistent with how L34 was set

### 7.1 Correct the premise before copying a method

L34 was **not** set on an idle host. The Phase 15 method is explicitly "Phase 12's D-10 method *without a quiet bar*" (D-04): runs in one session, load read before each, "no waiting for a quiet host"; the B runs that fixed the bar read at loads 5.3 to 30 (`bench/RESULTS.md` "Gate decision", "Before and after"). The bar was **the largest of three `-n 8 --cov` runs (65.83 s) rounded up to 66 s**, then confirmed as mean(B) = 63.555 s of an alternating A/B pair. The idle-host requirement in PROJECT.md is therefore a *new* method, not a repeat. The repo's own quiet-host precedent is the latency work: Phase 12's 1-minute load below 1.5 on a 12-core host, and Phase 13's quiet gate sampled every 30 s (`bench/RESULTS.md` Latency section; runs that never released the gate were recorded non-decisive and never counted).

Also: L34's bar is for the host it was read on (12-CPU M2 Max). The current dev host is an 18-CPU M5 Max; `PYTEST_WORKERS` is still 8 (`min(8, nproc)`), but the N = 8 knee was swept on 12 CPUs and is stale for 18. Re-sweeping is **out of scope** unless the human wants it; record the stale knee as a known limit in the new `Lxx`.

### 7.2 Protocol (keep R1-R5, add one gate and one rule)

Keep Phase 15's recipe unchanged: R1 `pgrep` clear; R2 read `sysctl -n vm.loadavg`; R3 one `/usr/bin/time -p make verify` with the 1 Hz process-tree RSS sampler; R4 read wall, pytest result line, peak RSS, coverage TOTAL; R5 a red run is recorded with its node ids and never replaced. Add:

1. **Idle gate (fixed before any number is read):** do not start a run until the 1-minute load is below a threshold X (Phase 12's precedent is 1.5) and `pgrep` is clear; record load before and after. A `make verify` raises the 1-minute average by its own eight workers (Phase 19 saw 3.16 -> 16.71), so a **cool-down between runs is mandatory** (the 1-minute average decays on a ~60 s constant; budget minutes, not seconds). State X, the sampling interval and the give-up rule in `bench/RESULTS.md` before reading.
2. **Statistic and bar rule (fixed before reading):** N = 3 green runs, the bar is the largest rounded up to a whole second (L34's rule), the mean reported beside it. Because the resource-tracker flake (`ReentrantCallError`, a `must` debt) can redden a run, attempt until three green, recording every red (19-01 did this: four runs, one red).
3. **Human checkpoint** (L34 D-01 style): the human reads the table and sets the bar; the `Lxx` carries the reading, the host facts (`bench.machine_facts()`), and `HEAD`. Never tuned toward a pass (L08).

### 7.3 Two readings, and why they are different jobs

- **Admission price of the browser test (at the browser phase).** "A gate cost is measured before it is accepted." Use the same code with and without the file: **A = `make verify PYTEST_ARGS="--ignore=tests/test_browser.py"`**, **B = `make verify`**, alternating A1 B1 A2 B2 A3 B3 (Phase 15's alternation; `PYTEST_ARGS` comes last in the recipe, so the flag wins). The only variable is the browser file; no checkout switching, no second venv. mean(B) - mean(A) is the browser test's cost. Record a `verify.fast` row too (must be unchanged, 11.3-11.5 s) and CI's wall from its first run.
- **The re-set (at milestone close).** Idle-host N = 3 on the final `HEAD`, after relations, selector and slug tests have landed (they add light tests), so the new bar describes the gate the milestone ships. This is the reading the new `Lxx` cites.

### 7.4 What the re-set must edit in the same commit (IN-03 and friends)

`Makefile` comments quoting `63.555 s` (the `test.fast` block, around `:152-157`); `.pre-commit-config.yaml` header ("measured 63.555 s"); `docs/HOW_TO_DEVELOP.md` section 0 ("~64 s"); L13's "~11 s" is already stale history, do not touch. Retire `docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md` IN-03 in the commit that re-sets the bar (it says so itself); IN-01/02/04 are separate and stay unless `model.py`/`DIMS` is touched. No check will enforce the new number: a wall-time assertion on shared hardware "would flap until someone stopped believing it" (Makefile, bench section, D-16). The bar remains a recorded figure, as the `test.fast` comment already admits for the 30 s budget.

**Single L34 amendment.** The `PIP_CONSTRAINT` venv probe also amends L34 if adopted. Take it in the same phase as the re-set so L34 is amended once.

---

## 8. Suggested build order, with dependencies

```
 A. Browser test ─────────────► B. Conditional fields ───► C. Bore selector
   (spike WebGL → fixture →            (needs A: trigger +        (needs B: shares evaluator
    scenarios → gate admission          regression net for         and metadata vocabulary;
    + A/B price → CI)                   the app.js edit)           needs A)
        │
        ├──────────────────────────► D. Download name  (independent; after A so the
        │                                browser asserts the real suggested_filename)
        ▼
 E. Closing phase: idle-host re-set + L34 Lxx + PIP_CONSTRAINT probe + ledger items
    (needs A..D landed so the final HEAD's gate is what is measured)
```

| Phase | Contents | Depends on | Why this position |
|-------|----------|-----------|-------------------|
| **A. Browser test** | Spike: WebGL context in headless Chromium on macOS arm64 and `ubuntu-latest` (first task, because a failure here stops everything). Server fixture (design A). Scenarios 1-4 of §3.3 on the existing, relation-free form, plus the init-script draw-count if the spike confirms it. Gate admission (O1): `test.fast` ignore, `test_hooks.py`, `$(BROWSER)` stamp, `test.ui`, CI install/cache, `test-image` ignore, docs. A/B price (§7.3). `Lxx`. | none | Both UI ideas name "a browser test exists" as their trigger; it is also the regression net for every later `app.js` edit. |
| **B. Conditional fields** | `_f(enabled_when)`, relation set, `applyRelations()`, CSS, `test_params_relations.py` (inertness), field-walk extension, browser state walk, `Lxx` superseding 08 D-09. | A | The schema vocabulary C reuses. |
| **C. Bore selector** | Selector metadata (S1) or the S2 decision, derive/write rules, browser tests incl. "link with a set-but-ignored value", `Lxx`. | A, B | Largest UX risk; one concern per commit; reuses B's evaluator. |
| **D. Download name** | `slug()`, request-vs-effect decision, flip `test_api.py:412`, keep `:720`, `http-api.md`, `Lxx`; add `expect_download` assertion to the browser test. | A (for the browser assertion only) | Technically independent of B/C; can move earlier or later. |
| **E. Closing** | Idle-host N = 3 reading, bar, `Lxx` amending L34, Makefile/pre-commit/HOW_TO_DEVELOP comments, IN-03 retired; `PIP_CONSTRAINT` probe on the final dev closure (it includes `playwright`); HOW_TO_DEVELOP reverify paragraph; README Pi 5 sentence. | A-D | Measures the shipped gate once; amends L34 once. |

**Research flags for phases**

- **A: deeper research / spike needed.** WebGL in headless Chromium (CI and macOS), `filterwarnings = error` against the Playwright plugin or sync API, init-script draw-count viability, cost under `-n 8`/`-n 4`.
- **B: standard patterns,** but the inertness proof will surface relation rows that are not actually inert; budget for dropping some.
- **C: needs a human decision first** (S1 vs S2; starter value vs pending state) before planning.
- **D: one small decision** (request vs effect).
- **E: standard,** but the idle-gate threshold and cool-down need fixing before any run.

---

## 9. Patterns to follow

1. **Schema-carried metadata, generic consumer.** Relations and selector options are data on the model, evaluated by one generic function in `app.js` (L02). The existing `group`/`unit`/`step` keys are the precedent.
2. **One-directional honesty proof.** Prove "relation false implies inert", not the converse (L08: never dim a live field).
3. **Evaluate against what is sent.** Relation/selector evaluation uses the same effective value as `gearQuery()` (empty means default).
4. **Test through the product's own seams.** Real uvicorn, real pool, real browser; observe through DOM, download events and an init-script, never through a production hook.
5. **Exclusion by name for the commit slice** (L36), so a new heavy file is opted out explicitly.

## 10. Anti-patterns to avoid

| Anti-pattern | Why it is wrong here | Instead |
|--------------|----------------------|---------|
| Exporting `scene`/`mesh` on `window` for the test | Changes production surface; couples test to internals | Init-script draw-call count + DOM end-state |
| In-process uvicorn thread | Two lifespans on the `app` singleton; import-time queue constants | Subprocess on an inherited socket |
| `skip` when Chromium is absent | Silent partial success; a green gate that did not run the UI | Fail loudly with the install command |
| `disabled` on a field that may hold a value | User cannot clear a value that is in a shared link | Visual `inactive`, editable |
| Serialising the selector into the hash | Changes what links mean (L05) | Derive on load; write only flat fields |
| A second pytest recipe in `verify` (O3) | Breaks `test_hooks.py:92` and L36 D-03 | O1 |
| A marker for the fast slice | L36: "never a marker"; a new file would run at commit untagged | `--ignore=` |
| Renaming default-radial downloads | Breaks the `:720` pin and every logged slug for no benefit | Suffix only the non-default |
| Tuning the new bar or the idle threshold after seeing numbers | L08 / L34 | Fix X, N and the rule first |
| Pixel-exact canvas assertions | SwiftShader vs GPU output differs | Draw counts; coarse pixel check at most |

---

## 11. Gate and CI cost considerations (replaces "scaling")

| Concern | Today | With O1 (estimate, unmeasured) | Mitigation |
|---------|-------|-------------------------------|------------|
| `make verify` wall, dev host | 192.94 s mean (161.7-208.6), L34 bar 66 s | + 0 to ~T_ui (`ASSUMPTION` 10-25 s) | Early dispatch + grouping; measured by the A/B in §7.3 |
| `make verify.fast` | 11.4-11.5 s of 30 s | unchanged | `--ignore` + `test_hooks.py` pin |
| CI `test (3.12)` | ~200 s at `-n 4` | + Chromium install (cached) + test; 4 vCPUs share software GL with `-n 4` | Generous waits, no timing asserts, cache the browser |
| Peak memory (gate) | ~6.6 GB summed RSS (upper bound) | + server, 2 pool workers, Chromium | Single browser worker (grouping) |
| First run after `make clean` | pages in ~1.4 GB of OpenCascade | + Chromium download | Document in HOW_TO_DEVELOP |

## 12. Integration points summary

### External services / tools

| Tool | Integration | Notes |
|------|-------------|-------|
| Playwright (Python, sync API) | `[dev]` extra; browser via Makefile stamp | Bundles a Node driver; no system Node. STACK researcher prices size/version. |
| pytest-xdist | `@pytest.mark.xdist_group("browser")` + `--dist loadgroup` | Ungrouped tests schedule as before. |
| GitHub Actions | Inside `test (3.12)`; cache `ms-playwright` | `required-jobs.txt` and the ruleset untouched under O1. |

### Internal boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `params.py` -> `app.js` | `/api/schema` JSON only | The only channel for relations and selector (L02). |
| `params.py` -> `app.py`/`records.py` | `slug()` call | No edit to either. |
| `calc.py` <-> relations | Test-time only (inertness proof) | The relation is not generated from `calc`'s ignored lists; a test pins them together. |
| Test process <-> server | HTTP on an inherited socket | Child env scrubbed of `SPUR_*`. |

## Open decisions for discuss-phase (none are research defaults)

1. Browser in the gate: O1 vs O3 vs O4 (recommend O1); one `Lxx` amending L11, L13, L36.
2. Selector: schema-carried (S1) vs bore-specific JS (S2); whether choosing D-flat/Hex writes a starter value.
3. Slug: request-based vs effect-based root naming.
4. Idle threshold X, run count N, cool-down rule; whether to re-sweep the xdist knee on the 18-CPU host.
5. Inactive field: visual-only (recommended) vs `disabled` limited to default values.

## Sources

- Code read (HIGH): `src/spur/params.py`, `static/app.js`, `app.py` (lifespan `:121-163`, schema `:373`, export `:420-504`), `records.py:171-180`, `calc.py:1145-1260`, `cli.py:20-100,125-170`, `tests/test_api.py:18-220`, `tests/test_cli.py:198-253`, `tests/test_hooks.py`, `tests/conftest.py`, `Makefile`, `pyproject.toml`, `.github/workflows/ci.yml`, `.pre-commit-config.yaml`.
- Decisions and measurements (HIGH): `docs/architecture/decision_log.md` L02, L05, L11, L13, L34, L36; `bench/RESULTS.md` "The gate, measured and pinned (Phase 15)" (Method R1-R5, xdist sweep, Gate decision, Before and after) and "The gate, priced (19-09)"; `docs/ideas/` (browser test, conditional fields, bore selector, download name); `docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md`; `docs/architecture/web-ui.md`.
- Web (LOW tier by provider, cross-read with Chromium docs; verify in the spike): SwiftShader opt-in for headless/GPU-less rendering, https://chromium.googlesource.com/chromium/src/+/798e59c5275d4131797e8ea2e96e6c6000256b58/docs/gpu/swiftshader.md ; pytest-xdist distribution modes and `loadgroup`, https://pytest-xdist.readthedocs.io/en/stable/distribution.html

---
*Architecture research for: spur v0.5 Honest Form*
*Researched: 2026-10-10*
