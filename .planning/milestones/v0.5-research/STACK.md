# Stack Research — Milestone v0.5 Honest Form

**Domain:** parametric involute spur gear generator (shipped); this file covers only what the six v0.5 items need
**Researched:** 2026-10-10
**Overall confidence:** HIGH for the browser stack on macOS arm64 and for the pydantic and wheel questions (all run on this host against the pinned tree); MEDIUM for the Linux CI side (run in an `ubuntu:24.04` linux/amd64 container under OrbStack, not on a GitHub runner)

Confidence tags: **[HIGH]** = run or read locally this session; **[MEDIUM]** = vendor docs fetched this session, or a local run on a stand-in for the real target; **[LOW]** = single source or absence of evidence; **ASSUMPTION** = not verified, surface before acting (L08, CLAUDE.md).
Versions are from the PyPI JSON API on 2026-10-10 (Context7 MCP tools were not available in this session). The scratch probes live outside the repo (the session scratchpad) and are not committed; the phase re-derives them as tests.

---

## Verdict

| Item | Stack change | Verdict |
|------|--------------|---------|
| 1. Browser test of the viewer | `playwright` (Python) in the `[dev]` extra, plus a one-off browser download | Add. Works first try, no WebGL flags, 3.2 s for four tests. |
| 2. Conditional fields (`enabled_when`) | none | `json_schema_extra` carries a nested object unchanged (verified). |
| 3. Bore-shape selector | none | Vanilla JS in `app.js`. |
| 4. `root_shape` in the download name | none | Pure Python slug change. |
| 5. Re-set the gate bar | none | A measurement. The browser test adds to the reading, so measure after it lands. |
| 6. `make venv` under `PIP_CONSTRAINT` on arm64 | none | Resolution probe passes: no pin lacks a macOS arm64 cp312 wheel. |

The 31-pin runtime closure (`requirements.txt`), the Dockerfile and `docker/refresh-requirements.sh` do not change.
`refresh-requirements.sh` resolves `/src` (runtime dependencies only), so a `[dev]` addition never reaches it. [HIGH, file read]

---

## Recommended Stack

### New: browser-driven test (item 1)

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `playwright` (Python) | `1.63.0` (released 2026-09-15; `requires-python >=3.10`; pulls `pyee>=13,<14` and `greenlet>=3.1.1`) | Drives headless Chromium against the real server; auto-waiting `expect(...)` assertions | Pure wheel for macOS arm64 (`py3-none-macosx_11_0_arm64`, 40 MB) and manylinux x86_64 (45 MB); no sdist, so it installs under `PIP_CONSTRAINT`. Ships `py.typed`. Bundles its own Node driver inside the wheel, so no system Node, no npm, no `setup-node` in the `test (3.12)` job. [HIGH] |
| Chrome Headless Shell (via `playwright install`) | `153.0.8010.12` (Playwright revision 1243) | The browser the test runs in | Playwright's default for `headless=True`. Gives WebGL 2 through SwiftShader on macOS arm64 and on Linux, with no flags (measured below). Smallest download. [HIGH] |

**Do not add `pytest-playwright` by default.** It works here (measured below), but it is a pytest plugin that autoloads for the whole suite and drags in `python-slugify` and `text-unidecode`. What it adds is a `page` fixture and trace/screenshot-on-failure. Two session fixtures (browser, server URL) are about 25 lines of conftest. If trace-on-failure proves worth it for CI debugging, adopting it is a drop-in: `pytest-playwright==0.10.0` (released 2026-10-08, two days old, so pin it, do not take a floating range).

### Unchanged: everything else

Nothing for items 2–5. The relation travels as `json_schema_extra`, the selector is vanilla JS, the slug is Python, and the bar is a measurement. See the sections below.

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pytest-xdist` | already in `[dev]` (3.8.0) | Parallel test workers | Each worker starts its own server on its own free port, so no coordination is needed. 4 viewer tests passed at `-n 2` in 3.8 s. [HIGH] |
| stdlib `subprocess` + `socket` + `urllib.request` | stdlib | Start `python -m spur serve --port N` on a free port; poll `/api/health` | The server was health-ready 0.20 s after spawn (BuildPool workers start lazily; first preview STL 1.59 s). [HIGH] |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `python -m playwright install --only-shell chromium` | Downloads the headless shell only (195 MB on macOS arm64, 261 MB on Linux, plus a 2.5–4.9 MB ffmpeg) | `--only-shell` is documented for exactly this case: headless-only, `channel` not set. Without it, `install chromium` also fetches the full 359 MB Chromium (556 MB total, 43.6 s on this host). [HIGH, measured; MEDIUM, docs] |
| `--with-deps` | Installs the Linux system libraries (apt) | Needed on `ubuntu-latest`. Measured in a bare `ubuntu:24.04` container: 49 s for apt deps plus shell plus ffmpeg. A GitHub runner image carries some of these already, so its cost is **unmeasured**. |

---

## Installation

```bash
# pyproject.toml [project.optional-dependencies].dev gains one line (same loose-range
# style as the other dev entries; the closure in requirements.txt does not move):
#     "playwright>=1.63",

make venv                                        # as today; picks up playwright
.venv/bin/python -m playwright install --only-shell chromium     # macOS dev host
.venv/bin/python -m playwright install --with-deps --only-shell chromium   # ubuntu-latest
```

Resolution check under the real constraint, run on this host with the closure as `PIP_CONSTRAINT`:
`pip install --dry-run --ignore-installed --only-binary=:all: -e '.[dev]' playwright==1.63.0` gave 0 errors. It adds `playwright`, `pyee 13.0.1` and `greenlet 3.5.6` to the venv. With `pytest-playwright==0.10.0` it also adds `python-slugify 9.1.3` and `text-unidecode 1.3`. [HIGH]

---

## Browser stack: why Playwright for Python

| Criterion | Playwright (Python) | Selenium 4.51.0 (2026-10-09) |
|-----------|---------------------|------------------------------|
| No Node on the host | Node 24.21.0 is inside the wheel (122 MB binary, 135 MB installed); the host needs none [HIGH] | No Node |
| Waiting | `expect(locator).to_have_...()` auto-retries; the form builds asynchronously after `fetch('api/schema')`, a 350 ms debounce and a build | Explicit `WebDriverWait` everywhere |
| Browser management | `playwright install` pins a Chromium revision to the library version | Driver and browser matched by Selenium Manager (**ASSUMPTION**, not verified this session) |
| WebGL headless | Works with defaults on both OSes (measured) | Would need hand-set Chrome flags (**ASSUMPTION**, not tested) |
| Typing under `mypy --strict` | `py.typed` present (file confirmed). A strict mypy run was **not** completed: the `--target` scratch layout shadowed `typing_extensions`. First thing for the phase to check against `disallow_any_explicit`. | Not checked |

Choose Selenium only if the project later needs a real branded Chrome or Safari through a WebDriver grid. It does not.

### How headless Chromium gets WebGL (item 1's crux)

`app.js` builds `new WebGLRenderer({ canvas })` at module top level (line 229). Without a WebGL context that throws during module evaluation, so **the whole page is dead, form included**. WebGL is load-bearing for every assertion, not only the "STL loads" one. [HIGH, code read]

Measured with Playwright 1.63.0 / Chrome Headless Shell 153.0.8010.12, `getContext('webgl2')` then `WEBGL_debug_renderer_info`:

| Host | Launch | WebGL | Renderer |
|------|--------|-------|----------|
| macOS 27 arm64 (M5 Max) | default (`headless=True`, shell) | WebGL 2.0 | ANGLE, Vulkan, **SwiftShader** (LLVM) |
| macOS arm64 | `--use-angle=swiftshader --enable-unsafe-swiftshader` | same | same SwiftShader |
| macOS arm64 | `--disable-gpu` | same | same SwiftShader |
| macOS arm64 | `channel="chromium"` (new headless, full Chromium) | WebGL 2.0 | **Apple Metal, M5 Max** (the real GPU) |
| `ubuntu:24.04`, linux/amd64 container, shell only | default | WebGL 2.0 | ANGLE, Vulkan, **SwiftShader** (Subzero) |
| same container | the two flag variants | same | same SwiftShader |

The flags change nothing, so none are needed. Do not add them (**ASSUMPTION** worth a one-line guard: if a later Chromium revision stops falling back to SwiftShader by default, the failure is a dead page and the fix is the two flags above, tested then). Use the default headless shell, **not** `channel="chromium"`: the shell renders on SwiftShader on both OSes, the new headless path renders on whatever GPU the host has, so the same test would draw through different rasterisers on a dev Mac and on CI. [HIGH locally; Linux is MEDIUM, a container and not a GitHub runner]

**How to assert "the STL loaded into the scene".** Scene objects are module-scoped in `app.js`, so a test cannot read them, and the stack does not change that. Two observable facts do work:

1. `#dl-stl` loses `aria-disabled` only after `showModel()` ran without throwing (`setDownloads(q)` follows it).
2. A canvas element screenshot (`page.locator('#canvas').screenshot()`) of the drawn gear is much larger than one of the blank control, which is the same page loaded with `#teeth=2`, a link the server refuses, so no mesh ever arrives. Measured PNG sizes: blank **3,393 bytes**, drawn **38,908 bytes** (11.5×). Assert a ratio with margin (3× passed the probe), not golden pixels: SwiftShader output is deterministic per renderer, but a golden image would couple the test to a Chromium revision and to Pillow, which is not in the 31-pin closure. [HIGH]

Console noise to allow: `GPU stall due to ReadPixels` warnings (SwiftShader plus screenshot) and one `422` resource error from the deliberately invalid link.

### Measured scenario, all four target behaviours

Run against the real server through the project's own pytest config (`filterwarnings = error`, `--strict-markers`):

| Behaviour | Selector / link | Result |
|-----------|-----------------|--------|
| Form builds from `/api/schema` | `form#params [name]` count = 31 | Pass |
| Invalid field marked | `#teeth=2` → exactly one `label.field.invalid`; message `Teeth: Input should be greater than or equal to 6` | Pass |
| Warning renders | `#module=1&pressure_angle=14.5` → `#messages .warning` contains "undercut" | Pass |
| STL draws | as above | Pass |

Four tests: **3.21 s** serial (`-n0`), **3.80 s** at `-n 2`, on the 18-CPU M5 Max. A plain-API script doing the same on one page took 6.5 s, most of it Pillow work in my probe, not Playwright. [HIGH]

---

## Item 1's open decision, priced: in `make verify`, or separate

| | A. Inside `make verify` (push, CI) and outside `verify.fast` | B. Separate target and CI job |
|---|---|---|
| Test-time cost | +3.2–3.8 s on a 192.94 s mean: about 1.7–2.0 %, inside the 162–240 s spread already recorded | 0 on `verify` |
| Install cost | One browser download: 43.6 s here (556 MB with the full browser, about 200 MB with `--only-shell`); 49 s in a bare Ubuntu container with apt deps. Not in the venv's 1.4 GB, but about 135 MB of wheel is | Same, but only for developers and runners that opt in |
| Node at test time | None (bundled driver). The L11 "no Node at runtime" rule is untouched; `vendor-bundle` stays the only Node job | Same |
| Definition of passing | One, in three places (L13, L36) | Two. A UI regression passes `pre-push` and fails later on CI only. L13's rule is bent |
| Required jobs | None. `test (3.12)` runs it | New job: edits `required-jobs.txt`, the ruleset on `main`, and `tests/test_pr_land.py`'s drift test |
| Commit stage | Add `--ignore=tests/test_viewer.py` to `test.fast` (it needs the download, and the 30 s SDK kill is the constraint, L36) | n/a |

**Recommendation: A.** It is the cheaper way to keep the one-gate promise, and its measured cost is noise next to the L34 bar being re-set. This is the human's call at discuss-phase. The honest tradeoffs to carry in are in the next list.

Design notes for the phase (**ASSUMPTION** unless marked):
- **Fail closed.** If the browser is missing, the test errors with Playwright's own "Executable doesn't exist" message. Do not `importorskip` or `skip` it; a skipped gate step is the false-green this project refuses (L08 in spirit).
- **Own the install in the Makefile**, as a stamp that depends on `$(STAMP)` and is a prerequisite of `test` only, never of `verify.fast`. CI cannot install the browser before the venv exists (`.venv` appears only when `make verify` runs), so the recipe must call `$(PY) -m playwright install ...`, with the `--with-deps` flag passed as a variable from `ci.yml`. Whether the runner's `sudo apt-get` works through Playwright's `--with-deps` on `ubuntu-latest` is unverified.
- **Isolate the browser cache.** The default cache is `~/Library/Caches/ms-playwright` (macOS) or `~/.cache/ms-playwright` (Linux). This host already holds `chromium-1228` for another project, and Playwright deletes browser versions that no registered client needs (docs: `PLAYWRIGHT_SKIP_BROWSER_GC=1` / `--no-remove` to opt out). Installing revision 1243 into the shared cache could remove another project's browser. Either set `PLAYWRIGHT_BROWSERS_PATH` under `.venv` for the install and the test (the same variable must reach both) or use `--no-remove`.
- **Do not cache the browser in CI.** Playwright's CI doc says restore time is comparable to download time and recommends `--only-shell` instead. [MEDIUM, docs fetched]
- **CPU contention is unmeasured.** SwiftShader is software rendering and shares CPUs with the eight xdist workers. `tests/test_pool.py` injects 0.2 s and 1.0 s timeouts that a starved 4-vCPU runner already threatens. Measure the gate with the viewer test present on a loaded run before accepting. An `xdist_group` marker (registered by xdist itself) would at least serialise the four tests.
- **Server per test session**: spawn `sys.executable -m spur serve --port <free>` as a subprocess. It is not measured by `coverage` (only multiprocessing children are), so coverage (97.92 % against `fail_under = 96`) neither gains nor loses from it.

---

## Conditional fields: `json_schema_extra` carries a nested relation (item 2)

Question: does Pydantic v2 accept arbitrary nested keys and emit them unchanged? **Yes.** Pydantic 2.13.5, the pinned version, run on a model shaped like `GearParams` fields (`Field(..., ge=, le=, json_schema_extra={...})` and a `Literal` field): [HIGH]

- A dict holding nested objects, lists, ints, floats, `None`, `True` and strings appeared in `model_json_schema()["properties"][name]["enabled_when"]` with an equality assertion passing against the Python input.
- Output is key-sorted at every level (`all, field, nested, op, value`). Lists keep their order. A relation must therefore never depend on key order.
- It sits beside `group`, `unit`, `minimum`, `maximum`, `enum` and `default`; `Literal` fields (`root_shape`, `recess_sides`) emit `enum` and carry the extra the same way.
- `pydantic.config.JsonDict` is a recursive alias (`dict[str, int | float | str | bool | None | list[JsonValue] | JsonDict]`). A nested relation typed as `JsonDict` passes `mypy --strict --config-file pyproject.toml` with `disallow_any_explicit` on. It needs no `Any` and no suppression.
- Docs say only "A dict or callable to provide extra JSON schema properties" and do not describe merge behaviour (fetched 2026-10-10). The behaviour above is what was run, not what is promised. The existing `_f()` helper in `params.py` already builds `extra: JsonDict`; the cheapest extension is one optional `enabled_when: JsonDict | None` keyword on it, and the same key on the direct `Field(..., json_schema_extra=...)` calls (`root_shape`, `recess_sides`).
- `/api/schema` returns `GearParams.model_json_schema()` directly (`app.py:374`), so no route change is needed, and `app.js` reads `prop.enabled_when` beside `prop.group` and `prop.unit`.

No JSON-Schema-evaluating library is needed in the browser. The relation language is the product's own, to be fixed at discuss-phase, and a field-equals, field-greater-than and all/any evaluator is about fifteen lines of vanilla JS. Do not use JSON Schema's `if`/`then` or `dependentSchemas`: nothing in the stack evaluates them client-side, and Pydantic would not emit them from `json_schema_extra` in a form `app.js` could use without a validator.

## Bore-shape selector and `root_shape` slug (items 3 and 4)

No stack. The selector is a `<select>` that `app.js` creates after `buildForm()` and derives from the flat fields on load; it keeps sending the flat fields (L05). The slug is `GearParams.slug()` in Python. Check that `root_shape` values (`radial`, `trochoid`) are already safe for `Content-Disposition`, and read what pins the old names (records, tests) first, as the idea file says. Both are testable through the browser test (the selector) and the existing suite (the slug).

## Item 5: re-setting the gate bar

No stack. Take the idle-host reading **after** the viewer test lands, since this research priced it at +3.2–3.8 s, and read both with the host idle (the recorded 162–240 s spread was taken under load).

---

## Item 6 probe: `PIP_CONSTRAINT=requirements.txt` on macOS arm64

**Result: none of the 31 pins lacks a macOS arm64 cp312 wheel on PyPI.** [HIGH]

Two independent checks, 2026-10-10, this host (macOS 27, arm64, Python 3.12.15):

1. PyPI JSON for each of the 31 `name==version` pins: every one has either a pure `py3-none-any` wheel or a macOS arm64 (or universal2) wheel that cp312 can use.
2. `PIP_CONSTRAINT=requirements.txt pip install --dry-run --ignore-installed --only-binary=:all: --report … -e '.[dev]'` resolved **87 packages**, with all 31 pins at their pinned version, **all as binary wheels**, no sdist, no conflict.

The suspected gaps, specifically:

| Pin | Wheel on this host | Size |
|-----|--------------------|------|
| `vtk==9.6.2` | `cp312-cp312-macosx_11_0_arm64` | 102 MB |
| `casadi==3.8.1` | `cp311-abi3-macosx_11_0_arm64` (the `abi3` tag covers 3.12; no `cp312` file exists) | 49 MB |
| `nlopt==2.11.0` | `cp312-cp312-macosx_11_0_arm64` | under 1 MB |
| `cadquery-ocp==7.9.3.1.1` | `cp312-cp312-macosx_11_0_arm64` | 59 MB |
| `numpy==2.5.3` | `cp312-cp312-macosx_14_0_arm64` | 5 MB |
| `pydantic_core==2.46.5`, `PyYAML==6.0.3` | `cp312-cp312-macosx_11_0_arm64` | under 1 MB each |
| `ezdxf==1.4.4` | `cp312-cp312-macosx_11_0_arm64` (plus a pure wheel) | 2 MB |
| `fonttools==4.65.0` | `cp312-cp312-macosx_10_13_universal2` (plus a pure wheel) | 2 MB |

What this does **not** prove, and the phase must still run:
- `make verify` passing under the constraint. The existing `.venv` on this host was installed **unconstrained** and runs `fastapi 0.142.4`, `starlette 1.7.0` and `uvicorn 0.54.0` against the pins' `0.141.1`, `1.6.0` and `0.53.0`. Adopting the constraint downgrades those three; the kernel pair is already identical to the pin. That is the real delta of the experiment.
- The constraint pins only what it names. About 56 unpinned packages (trame, matplotlib, scipy, numba, pillow and others, all arm64 wheels in the resolution) still install, as today; `make venv` stays about 1.4 GB.
- Fixture parity: the regression fixture's tripwire compares kernel versions only, which match.
- Do the actual `make venv VENV=.venv-proof` in a throwaway directory, as the idea file says, and record the `make verify` result line.

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| `playwright` alone, hand-written session fixtures | `pytest-playwright 0.10.0` | If trace/video/screenshot-on-failure is wanted in CI. Verified to coexist with `filterwarnings = error`, `--strict-markers` and `-n 4` on 73 existing tests (4.89 s vs 5.11 s, no change). It is two days old at the time of writing: pin it exactly. |
| Headless shell, default launch | `channel="chromium"` (new headless) | Never for the gate: it renders on the host's real GPU (Apple Metal here), so dev and CI would draw through different rasterisers. |
| Playwright for Python | Selenium 4.51.0 | A branded-browser or grid need. None here. |
| Run the server as a subprocess | uvicorn in a thread of the test process | Rejected: BuildPool spawns worker processes and the serving process is import-linter-forbidden from the kernel; a subprocess matches production and keeps xdist workers independent. |
| Vanilla-JS relation evaluator in `app.js` | A JSON-Schema or form library in the browser | Never; L02 and the "one form, generated from `/api/schema`" rule. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `@playwright/test`, Vitest, Jest, Cypress, any npm test runner | Node at test time; a second package manager in the `test (3.12)` job; L11 | Playwright for Python (its Node is inside the wheel, not the project's) |
| jsdom / happy-dom | No WebGL; the page dies at `new WebGLRenderer` | A real headless browser |
| `pytest-asyncio` / the async Playwright API | A second event-loop model in a suite that does not use one; the sync API raises inside a running loop | `sync_playwright()` in fixtures |
| `pytest-base-url` | Pulls `requests` for one URL | A fixture that returns the URL |
| Pillow or golden-image comparison | Not in the closure; pins the test to a Chromium revision; first-run 5 MB-class fixtures | PNG byte-size ratio against the blank control |
| Branded Chrome / `channel="chrome"`, GPU flags, `--no-sandbox` | Different rasteriser per host; flags proven unnecessary | The default headless shell |
| Playwright in `requirements.txt`, the Dockerfile or the runtime closure | Breaks "31 pins, unchanged"; test-only | `[dev]` extra only (as `pytest-xdist` and `pytest-cov` are) |
| A Playwright Docker image for the CI job | `test (3.12)` runs on the runner with `setup-python`; changing the job's shape is a CI redesign | `playwright install --with-deps --only-shell chromium` |
| A JS framework, JSON Forms, react-jsonschema-form, `ajv` | Second form library; ~15 lines of evaluator do the job | Vanilla JS reading `prop.enabled_when` |
| Pydantic `if`/`then` or `dependentSchemas` for the relation | Nothing client-side evaluates them | A project-defined `enabled_when` object in `json_schema_extra` |

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| `playwright 1.63.0` | `pyee>=13,<14`, `greenlet>=3.1.1` | Resolves cleanly with the 31 pins as constraints. `pyee 14.0.0` exists but needs Python ≥3.12 and is excluded by `<14` (fine on 3.12). |
| `playwright 1.63.0` | Chrome Headless Shell `153.0.8010.12` | Revision 1243. A different Playwright version needs a different download, so a version bump re-downloads. |
| `pytest-playwright 0.10.0` | `pytest<10`, `playwright>=1.18` | The venv has `pytest 9.1.1`. |
| `playwright` `[dev]` addition | `PIP_CONSTRAINT: requirements.txt` in `ci.yml` | 0 errors in the dry-run. |

## Sources

- PyPI JSON API, 2026-10-10: `playwright` 1.63.0, `pytest-playwright` 0.10.0, `selenium` 4.51.0, `pyee`, `greenlet`, `pytest-base-url`, and all 31 pins in `requirements.txt` — [HIGH]
- Local runs, 2026-10-10 (macOS 27 arm64, Python 3.12.15, the project's `.venv`, nothing installed into it): `pip install --dry-run` resolution under `PIP_CONSTRAINT`; `playwright install chromium`; WebGL renderer probes; the four-test viewer scenario under the project's pytest config; plugin coexistence on 73 existing tests — [HIGH]
- `ubuntu:24.04`, linux/amd64 container via OrbStack: `playwright install --with-deps --only-shell chromium` and the WebGL probe — [MEDIUM] (not a GitHub runner image)
- https://playwright.dev/python/docs/browsers — `--only-shell`, `--no-shell`, `--with-deps`, cache locations, `PLAYWRIGHT_BROWSERS_PATH`, browser GC and `--no-remove` — [MEDIUM]
- https://playwright.dev/python/docs/ci — `playwright install --with-deps` on `ubuntu-latest`; caching browsers not recommended — [MEDIUM]
- https://pydantic.dev/docs/validation/latest/api/pydantic/config/ — `json_schema_extra` "A dict or callable to provide extra JSON schema properties" — [MEDIUM]; the nested-emit behaviour itself is from the local run — [HIGH]
- Repo files read: `.planning/PROJECT.md`, `requirements.txt`, `pyproject.toml`, `Makefile`, `.github/workflows/ci.yml`, `.pre-commit-config.yaml`, `docker/refresh-requirements.sh`, `src/spur/static/app.js`, `src/spur/static/index.html`, `src/spur/params.py`, the two idea files named in the brief.

## Gaps to carry forward

- Strict-mypy and ruff behaviour of Playwright-typed test code was not completed (scratch layout problem); first task of the browser-test phase.
- `--with-deps` through `sudo` on a real `ubuntu-latest` runner, and its wall-clock there.
- The gate re-measured with the viewer test present under eight-worker load, on a 4-vCPU runner.
- `make verify` under `PIP_CONSTRAINT` on this host (the probe covers resolution only).

---
*Stack research for: spur v0.5 Honest Form*
*Researched: 2026-10-10*
