# Project Research Summary

**Project:** spur, milestone v0.5 "Honest Form" (a subsequent milestone on a shipping app; the research covers only the new work)
**Researched:** 2026-10-10
**Confidence:** MEDIUM-HIGH. Repo and macOS arm64 claims are HIGH (MEASURED or READ). Linux and GitHub-runner claims are MEDIUM or UNVERIFIED.

Evidence tags carry through from the four files. MEASURED means run on the dev host (M5 Max, macOS arm64, Python 3.12.15, Playwright 1.63.0). READ means a repo file or upstream source. DOCS means vendor documentation fetched. UNVERIFIED and ASSUMPTION mean inference. [judgement] means a FEATURES.md call.

## Executive Summary

v0.5 adds no geometry and no `GearParams` field. It makes the form honest about what each field does, and it puts a real browser behind that claim. The work is:
- a headless-browser test of the viewer;
- `enabled_when` relations in `json_schema_extra`, rendered by generic `app.js` code;
- a bore-shape selector;
- a `_trochoid` suffix on the download name;
- a measured re-set of the L34 gate bar;
- three ledger items.

All four files agree on the architecture. `/api/schema` is `GearParams.model_json_schema()` untransformed (READ, `app.py:373`). So `app.py`, `records.py`, `calc.py`, `model.py`, `pool.py` and `cli.py` need no edit.

The recommended approach:
- **Browser test:** Playwright (Python, sync API) with the default Chrome Headless Shell. WebGL2 comes through SwiftShader with no flags (MEASURED). It runs against a real uvicorn subprocess, sits inside `make verify` and CI, and is excluded from `verify.fast` by name (L36). It fails closed if the browser is missing.
- **Relations:** a project-defined data structure evaluated by about 15 lines of vanilla JS.
- **Inert fields:** dimmed and still editable, never natively `disabled`.
- **Order:** browser test, then the form work in dependency order, then one closing phase that measures the shipped gate once and amends L34 once.

The main risks are about honesty (L08):
1. Every declared relation must be backed by `calc`, so a parity test is mandatory. Some proposed relations will fail it.
2. hex × keyway is a 422, not an ignored field.
3. The existing test `test_the_shareable_link_round_trips_every_field_through_generic_code` forbids field names in `app.js`, and the selector collides with it unless its logic is schema-carried.
4. L34 was not set on an idle host.
5. A skipped browser test gives a green gate with no UI coverage.

## Key Findings

### Stack (STACK.md)
- **`playwright` 1.63.0 in `[dev]`.**
  - Pure wheels for macOS arm64 and manylinux, no sdist, so it installs under `PIP_CONSTRAINT`.
  - It bundles a 130-135 MB Node driver, so no system Node is needed and L11 is untouched.
  - MEASURED: the dry-run resolved with 0 errors.
- **Chrome Headless Shell 153.0.8010.12 (revision 1243)** via `playwright install --only-shell chromium`. About 195 MB on macOS arm64, against 556 MB for the full browser (MEASURED).
- **`json_schema_extra` nested relation.** Pydantic 2.13.5 emits nested dicts and lists verbatim, key-sorted at every level (MEASURED). `JsonDict` passes `mypy --strict`. DOCS only say "a dict or callable", so the merge behaviour comes from the run, not from a promise.
- **No new library** for the evaluator, the selector, the slug or the server fixture. Do not use Pydantic `if/then` or `dependentSchemas`.
- **Runtime closure unchanged.** The 31 pins, the Dockerfile and `refresh-requirements.sh` do not move (READ).
- **WebGL is load-bearing.** `app.js:229` builds `WebGLRenderer` at module top level, so without WebGL the whole page is dead, form included (READ; PITFALLS MEASURED 0 form fields under `--disable-3d-apis`).
- **Use the default shell, never `channel="chromium"`.** The shell renders on SwiftShader on both OSes. New headless uses the host GPU (Apple Metal here), so dev and CI would draw differently (MEASURED).
- **Four-test scenario:** 3.21 s serial, 3.80 s at `-n 2` (MEASURED).
- **Item 6 probe, resolution only:** none of the 31 pins lacks a macOS arm64 cp312 wheel (MEASURED, two checks). The real delta of adopting the constraint is that `fastapi`, `starlette` and `uvicorn` get downgraded to the pins.

### Features (FEATURES.md)
**Must have:**
- **Browser test:** server fixture, form built from the schema (counts read from `/api/schema`, never hard-coded), `#dl-stl` href after the first build, non-blank canvas, invalid field marked, warning text equal to `/api/info`, link round trip, CSS custom properties non-empty, and a loud failure if the browser is missing.
- **Conditional fields:** `enabled_when` metadata, a generic evaluator, dim-and-editable, a reason derived from the gate field's `title`, re-evaluation on `input`, `readHash`, Reset and `hashchange`, and a calc parity test.
- **Download name:** radial keeps today's name; trochoid gets a `_trochoid` suffix (suffix, not prefix).

**Should have:** the bore-shape selector (P2, "the most discretionary item", defer if the budget is short) and stash/restore of zeroed keyway values.

**Defer:**
- stale-response test;
- refused-vs-inert styling;
- calc warnings for the silent relations;
- the hex-warning-on-defaults noise (reproduced: `?bore_hex=6` warns every time; `app.js` must not filter it);
- the cutout "pick one" lock.

**Findings the roadmap must know:**
1. hex × keyway is a 422 (reproduced, `calc.py` ~653). The inventory has two classes: inert (warned) and refused (422).
2. `root_shape=trochoid` is a no-op at z=30, 41 and 60 (reproduced), so a name from the request can name a root the part lacks.
3. `gearQuery()` reads `input.value`, not `FormData` (READ), so dim, disable and hide all leave the URL contract (L05) untouched.

### Architecture (ARCHITECTURE.md)
- **Pattern:** metadata on the model, one generic consumer in `app.js`, relations evaluated against the value `gearQuery()` sends.
- **Files:**
  - `params.py`: `_f(enabled_when)`, selector metadata, `slug()`.
  - `app.js` and `style.css`: `applyRelations()` and `.field.inactive`.
  - `tests/test_browser.py`: new, heavy tier.
  - `tests/test_params_relations.py`: new, light tier, the one-directional inertness proof (relation false means changing the dependent changes only `warnings`).
  - Makefile: `$(BROWSER)` stamp and `test.ui`.
  - CI: browser install inside `test (3.12)`.
  - Up to five new `Lxx`.
- **Server fixture:** a subprocess on a pre-bound socket with `--fd`. An in-process thread is rejected because `app` is a singleton (lifespans collide, queue constants are fixed at import, `dependency_overrides` is shared).
- **Gate placement:** option O1 (inside `test`, excluded from `test.fast`) is recommended. O3 breaks `test_hooks.py:92`. O4 needs `required-jobs.txt` and the GitHub ruleset.

### Pitfalls (PITFALLS.md), top six
1. **BT-1: no WebGL kills the form.** Use the default shell, assert `getContext('webgl2')` first, and spike Linux on CI.
2. **BT-2 / BT-3: the slice and the vacuous skip.**
   - A new test file joins the 30 s slice by default.
   - Add `--ignore` in the same commit, and a test that enforces it.
   - Never `importorskip`.
   - `make test-image` needs the ignore too (ARCHITECTURE and PITFALLS agree).
3. **BT-4 / BT-5: server isolation.**
   - Use a subprocess with a pre-bound `127.0.0.1` socket, `start_new_session=True` and `killpg`.
   - MEASURED: pool children survived a server `SIGKILL` for 6 s.
   - MEASURED: `--fd` works with a TCP socket on uvicorn 0.54.0.
4. **CF-1 / CF-2: the pins and the refusals.**
   - Never delete a pin; tighten it under the `Lxx`.
   - `test_every_key_the_ui_reads_is_a_derived_dimensions_field` harvests `['word',` lines as DIMS keys.
   - MEASURED: `keyway_width` alone and `keyway_depth` alone are both 422, so gating each on the other deadlocks both.
   - MEASURED: `recess_*` at `none` and `bore_d=0, bore_flat=5` return 200 with `warnings: []`.
5. **VP-1: venv hook clobbering.** `make venv VENV=.venv-proof` in the main checkout runs `pre-commit install`, which bakes that venv's python into the shared shim (READ: `INSTALL_PYTHON` in `.git/hooks/pre-commit`). Use a scratch clone or a linked worktree.
6. **GB-1 / GB-2: no idle host, and the spread beats the effect.** Three runs read 208.52, 161.71 and 208.60 s (READ, 19-09). Fix the rule before the first reading.

## Where the Four Files Disagree

None of these is resolved here.

| # | Topic | What each file says |
|---|---|---|
| 1 | Selector logic home (known tension 1) | PROJECT.md says both "UI-only select in `app.js`" and "relation lives in schema metadata, never hard-coded in `app.js`". FEATURES finding 3 and ARCH §5.1 say these cannot both hold. FEATURES: Option A (metadata) or defer; a second `.js` file is gaming the pin. ARCH: S1, a model-level `selectors` entry in the same condition vocabulary; S2 needs an allow-list that weakens the pin. PITFALLS BS-4: a `BORE_SHAPES` constant in `app.js` under an `Lxx`, plus a model-driven round-trip test against `calc`. |
| 2 | "Idle-host" re-set vs how L34 was set (known tension 2) | PROJECT.md says "idle-host". ARCH §7.1 and PITFALLS GB-1 correct it from `bench/RESULTS.md` (READ): Phase 15 D-04 set the bar with no quiet host, loads 5.3-30. The bar is the largest of three `-n 8 --cov` runs (65.83 s) rounded to 66 s, then mean(B) = 63.555 s. The quiet-host precedent is Phase 12 (load below 1.5). An idle re-set is a new method. STACK only says "measure idle after the browser test lands". |
| 3 | Slug: requested vs effective (known tension 3) | FEATURES, ARCH and PITFALLS recommend effective (`calc.root_mode`). STACK takes no side. Cost: `slug()` depends on a solver, about 10-30 µs (MEASURED, 19-09). PITFALLS SL-2: `slug()` is called inside failure-path records, so it must be total. |
| 4 | Dim-and-editable vs `disabled` (known tension 4) | All three recommend dim-and-editable. ARCH §4.3 allows `disabled` only for fields at their default. A disabled field cannot be cleared, so a value in a shared link such as `#spoke_count=0&hub_d=40` would be stuck. |
| 5 | Keyway in the relation system | FEATURES and ARCH include `keyway_*` (FEATURES calls it the "refused" class). PITFALLS CF-2 says `enabled_when` should cover "ignored" cases only, so refusals stay visible 422s. |
| 6 | Unbacked relations (`recess_*`, `bore_flat` at `bore_d` 0) | FEATURES: leave out and file an idea. ARCH: includes the recess row, to be settled by the proof. PITFALLS: a human decision. |
| 7 | Relation grammar | STACK: nested `all/any`. FEATURES: a JSON-Schema-flavoured fragment (`{"const": 0}`). ARCH: a list of `{field, op, value}` with `op` in `eq, ne, gt, ge`. PITFALLS: `{field, gt}` or `{field, eq}` plus `all`. All say AND-only suffices. |
| 8 | Asserting "STL in the scene" | STACK and FEATURES: `#dl-stl` href plus a canvas check (PNG size ratio 3,393 vs 38,908 bytes, or 11,478 distinct pixels, both MEASURED). ARCH adds an init-script draw count (VERIFY IN SPIKE). PITFALLS BT-7 proposes a production line `canvas.dataset.triangles`, the only production change any file suggests. |
| 9 | WebGL flags | ARCH: pass CPU-render args (LOW). STACK (MEASURED) and PITFALLS (READ: Playwright already adds `--enable-unsafe-swiftshader`): none needed. |
| 10 | Server port and worker cost | STACK: "free port". ARCH and PITFALLS: pre-bound socket with `--fd`. ARCH: `xdist_group` with `--dist loadgroup`. PITFALLS (DOCS): the mark is a no-op under the current `--dist load`, and changing suite scheduling is a gate-time change, so it prefers one scenario test. |
| 11 | Playwright pin and plugin | STACK: `playwright>=1.63`; `pytest-playwright` optional, pin 0.10.0 exactly if used. PITFALLS: pin `playwright` exactly; avoid `pytest-playwright`. |
| 12 | CI browser cache | ARCH: cache `ms-playwright`. STACK and PITFALLS (DOCS): caching is not recommended. |
| 13 | Selector write-through | FEATURES: zero the keyway pair on Hex or None, with a stash. ARCH: writes switch-offs only, no keyway zeroing. PITFALLS BS-1: minimum fields, explicit `"0"` never `''`, remember typed values, never write on load. |
| 14 | Gate-reading N | ARCH: N=3, the bar is the largest run rounded up. PITFALLS GB-2: N≥5 per arm, interleaved A/B, min/median/max. |
| 15 | Missing-browser opt-out | ARCH and FEATURES: fail loudly, no skip. PITFALLS: no skip, but a printed `SPUR_NO_BROWSER=1` opt-out refused when `CI` is set. |

## Decisions Reserved for the Human (discuss-phase)

1. Does a headless browser belong in `make verify`? Options: O1 (recommended by all four), O2, O3, O4. STACK prices O1 at +3.2-3.8 s on a 192.94 s mean (MEASURED). One `Lxx` amends L11, L13 and L36.
2. Missing browser: hard fail, or hard fail plus a printed, CI-refused opt-out.
3. Whether to add the one production line `canvas.dataset.triangles`.
4. Whether to adopt `pytest-playwright`.
5. Dim-and-editable, or `disabled` limited to default values.
6. Relation grammar scope.
7. Whether keyway gets a relation, and a separate "refused" style.
8. Whether unbacked relations stay undimmed or get a warning first.
9. Selector logic home: schema (S1) or a `BORE_SHAPES` constant (S2). Also whether to defer the selector at all.
10. A fifth "No bore" option, with keyway kept outside the select.
11. What Hex or D-flat writes when the matching field is 0: a pending UI state (all files lean this way) or a starter value (`bore_flat` default is 8).
12. Slug by requested or effective root.
13. The idle threshold X (precedent 1.5), cool-down, N, and the give-up rule, all fixed before any reading. The human then sets the bar.
14. Whether to re-sweep the xdist knee on the 18-CPU host (the N=8 knee was swept on 12 CPUs).
15. Whether to adopt `PIP_CONSTRAINT` in `make venv` if the probe passes.

## Implications for Roadmap

Five phases, numbered from 21.

**Phase 21: Browser Test of the Viewer**
- **Why first:** both UI ideas named "a browser test exists" as their trigger. It is the only thing that can see dim, derive and write-through behaviour. It carries the golden baselines: request sets for the 44 records, the hex-link warning, and the `root_shape=bogus` blank-select behaviour.
- **Delivers:**
  - the WebGL and CI spike as the first task;
  - the subprocess server fixture;
  - scenarios for all three programmatic-value paths (fresh load, Reset, `hashchange`);
  - gate admission: `test.fast --ignore`, `HEAVY_TEST_FILES`, the `$(BROWSER)` stamp, `test.ui`, the CI install, the `test-image` ignore, and a `.gitignore` entry for browser artifacts;
  - the isolated price of the file;
  - one `Lxx` amending L11, L13 and L36;
  - the reverify paragraph in `HOW_TO_DEVELOP.md` §6 (cheapest early, PITFALLS M-5).
- **Install constraint:** the browser install must be a Makefile step, because `.venv` does not exist before `make verify`. Isolate `PLAYWRIGHT_BROWSERS_PATH` or pass `--no-remove`, because this host holds `chromium-1228` and Playwright's browser GC could delete another project's browser.
- **Avoids:** BT-1 to BT-11, M-1 to M-4.

**Phase 22: Download Name Carries `root_shape`**
- **Why here:** independent of the form work and low-risk. It reuses Phase 21's `expect_download` harness while it is fresh, and it can move later at no cost.
- **Delivers:**
  - a suffix only for a non-default root, so the `test_api.py:720` pin stays;
  - a deliberate flip of the `test_api.py:411-412` assertion;
  - `http-api.md:43` updated;
  - an `Lxx` listing what pinned the old names, and recording that no cache is keyed by slug (READ).
- **Avoids:** SL-1, SL-2. Test z=23 (applies) and z=40 (ignored).

**Phase 23: Conditional Form Fields**
- **Why before the selector:** it needs Phase 21 as its regression net, and it defines the evaluator the selector reuses. Building them separately gives two statements of "hex wins" (PITFALLS BS-4).
- **Delivers:**
  - `_f(enabled_when)`, and the same key on the two bare-`Field` Literal fields;
  - `applyRelations()` with dim-and-editable and a reason built from the gate field's `title`;
  - the calc parity test;
  - the model-driven field-walk extension;
  - a keyword-collision test;
  - the pins rewritten stricter under an `Lxx` that supersedes 08 D-09 (L02 kept).
- **Avoids:** CF-1 to CF-4, M-3, M-7. Budget for dropping rows that fail the parity proof. File the hex-warning noise as debt.

**Phase 24: Bore-Shape Selector**
- **Why here:** it needs Phase 21 (trigger) and Phase 23 (shared evaluator). It is the largest UX risk and the most discretionary item, so it can be cut without breaking anything else. It needs the human decision on logic location before planning.
- **Delivers:**
  - a `<select>` over hex, D-flat, round and none;
  - no entry in the `fields` map and none in the URL;
  - stash and restore of typed values;
  - a model-driven round-trip test per state;
  - browser tests for the 44-record request-set comparison and for "no non-field key in any `/api/*` request or hash".
- **Avoids:** BS-1 to BS-4. Write option tables as objects, not `['x', ...]` rows.

**Phase 25: Gate Bar Re-Set, Venv Probe, Ledger Close**
- **Why last:** the re-set must measure the shipped `HEAD`, so it needs Phases 21-24 landed. The re-set and the `PIP_CONSTRAINT` probe both amend L34, so they share this phase and L34 is amended once.
- **Probe constraints:**
  - It must not run during a gate measurement, because it loads the host.
  - It must not run in the main checkout. `make venv VENV=...` runs `pre-commit install` and rewrites the shared hook shim (READ, `Makefile:51`, `.git/hooks/pre-commit`).
  - Use a scratch clone or a linked worktree. The Makefile detects worktrees and skips the install (READ, `Makefile:71`).
  - Afterwards confirm that `.git/hooks/pre-commit` still names `.venv/bin/python`.
- **Delivers:**
  - the rule and threshold written into `bench/RESULTS.md` before any reading;
  - idle-host readings with load, machine and `HEAD`;
  - the human sets the bar;
  - one `Lxx` amending L34;
  - the stale `63.555 s` / `~64 s` comments in `Makefile`, `.pre-commit-config.yaml` and `HOW_TO_DEVELOP.md` rewritten, with IN-03 retired in the same commit;
  - the probe result (`make verify` result line, `pip check`, freeze diff);
  - the README Pi 5 sentence stating only the hardware the numbers came from.
- **Avoids:** GB-1 to GB-3, VP-1, M-6.

**Ordering rationale**
- BT comes first because both UI ideas named it as their trigger.
- CF comes before BS because the selector reuses the relation evaluation pass.
- SL is movable anywhere after BT.
- The gate re-set and the venv probe come last, together, to measure the shipped gate once.
- The 44-record fixture stays byte-identical because no phase touches `GearParams` fields or `derive()`. The slug is not in the fixture (READ: `pre_v0_2.json` has no `spur_z` string).

**Research flags**
- **Phase 21 needs a spike:**
  - Linux CI: the headless shell on `ubuntu-latest`, `--with-deps` via `sudo`, and the apt libraries.
  - Strict mypy on the Playwright-typed file.
  - Gate cost under eight-worker load on a 4-vCPU runner.
- **Phase 24** needs a human decision before planning.
- **Phase 22** has one small decision (requested vs effective).
- **Phase 23** uses standard patterns, but the parity proof will surface relation rows that are not inert.
- **Phase 25** uses standard patterns, but the idle threshold, cool-down and N must be fixed before any run.

## Confidence

| Area | Confidence | Notes |
|---|---|---|
| Stack | HIGH on macOS arm64; MEDIUM on Linux CI | Linux was an `ubuntu:24.04` container, not a GitHub runner. |
| Features | MEDIUM-HIGH | Repo claims were reproduced. UX conventions are MEDIUM. FEATURES rated Linux WebGL as LOW; STACK later measured the container. |
| Architecture | MEDIUM | Claims about existing code are HIGH. ARCH says nothing in it was run; STACK and PITFALLS have since measured several of its assumptions. |
| Pitfalls | HIGH for MEASURED and READ; MEDIUM for DOCS; LOW for UNVERIFIED | No Linux host, Docker daemon or runner was available. |

**Gaps:**
- **CI Linux:** unmeasured.
- **Browser-test gate cost under load:** ARCH's 10-25 s is an ASSUMPTION; STACK's 3.2-3.8 s is the isolated MEASURED figure.
- **Strict mypy:** `page.evaluate` returns `Any`, so it needs typed wrapper helpers.
- **Gate re-set spread:** the 19-09 spread is larger than any single effect. At N around 10, 2 failures in 12 runs has a 95% Wilson interval of about 5-45% (calculated).
- **`make verify` under `PIP_CONSTRAINT`:** only resolution was probed. Also, pip 26.2 no longer applies `PIP_CONSTRAINT` to build isolation (DOCS), and macOS arm64 green says nothing about the Docker `linux/arm64` image or the Pi 5.
- **Resource-tracker flake (a `must` debt):** keep every failed gate log during Phase 21 and classify it against the four recorded occurrences. Add no `filterwarnings` entry.
- **Existing silent behaviour to pin and file, not fix:** `#root_shape=bogus` becomes the default via the blank select, where the API returns 422 (MEASURED).
- **Other UNVERIFIED items:** the `expect` default timeout, canvas readback without `preserveDrawingBuffer`, coverage behaviour on a `SIGKILL`ed child, FastAPI's handling of a nested extra in `/openapi.json`, and same-document `goto` semantics in Playwright.
- **Ledger hygiene:** retire each idea or debt item in the commit that closes it (status, sha, `git mv`, INDEX row).

## Sources
Only what the four files cite:
- **HIGH (local runs and repo reads):**
  - pip dry-run under `PIP_CONSTRAINT`, Playwright installs, WebGL probes, the four-test scenario, reproduced API behaviours, `--fd` and `SIGKILL` experiments.
  - PyPI JSON for the 31 pins, `playwright`, `pytest-playwright` and `selenium`.
  - Repo files: `app.js`, `params.py`, `calc.py`, `app.py`, `records.py`, `cli.py`, `tests/test_api.py`, `test_cli.py`, `test_hooks.py`, `Makefile`, `pyproject.toml`, `ci.yml`, `.pre-commit-config.yaml`, `.git/hooks/pre-commit`, `decision_log.md`, `bench/RESULTS.md`, `docs/ideas/*`, `docs/tech_debt/active/*`, `PROJECT.md`.
  - Upstream source: Playwright `chromium.ts`, uvicorn `config.py`.
  - OpenSCAD Customizer manual.
- **MEDIUM:**
  - `ubuntu:24.04` container run.
  - Playwright browsers, CI, intro and clock docs.
  - Pydantic `json_schema_extra` docs.
  - pytest-xdist distribution and how-to pages.
  - coverage.py config, pytest-cov 7.0.0 changelog, pip 26.2 release notes.
  - JSON Schema conditionals, JSON Forms rules, rjsf dependencies.
  - kittygiraudel on `disabled` vs `aria-disabled`, MDN `inert`, hidde.blog, GOV.UK radios.
  - RFC 6266.
- **LOW:**
  - Chromium SwiftShader docs (two revisions cited).
  - microlink.io on WebGL without a GPU.
  - pytest-xdist scheduling guarantees (via web search).
