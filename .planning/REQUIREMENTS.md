# Requirements: spur — milestone v0.5 Honest Form

**Defined:** 2026-10-10
**Core Value:** A number this tool prints is a number someone will cut metal to — every
dimension is computed honestly or reported as a warning, never guessed (L08).

Scope fixed in `PROJECT.md` ("Current Milestone: v0.5 Honest Form"). Research pass:
`.planning/research/SUMMARY.md` is the entry point; its "Where the Four Files Disagree"
table is authoritative over any single research file, and every figure quoted below carries
its evidence tag (MEASURED / READ / DOCS) from the file that produced it. The choices the
human took at kickoff (2026-10-10) are baked into the wording: the browser test **first**
and **inside the gate** (O1), the browser missing is a **hard failure** with no opt-out,
relations are **calc-backed only** (the two unbacked rows dropped — they would have rewritten
14 fixture records' `warnings`), inert fields are **dimmed and editable**, the selector is
**schema-carried** (S1), the download suffix follows the **effective** root, and the gate
bar is re-set under a **new, pre-registered idle-host rule**, not L34's loaded-host method.

REQ-IDs continue the project's `REQ-slug` convention (`milestones/v0.4-REQUIREMENTS.md`).

## Rules every requirement lives by

- **Same part, same links.** `tests/regression/pre_v0_2.json` (44 records, 85 cases,
  `warnings` included) stays byte-identical to the `v0.4` tag through every commit of this
  milestone. No new `GearParams` field; `enabled_when` and the selector's options are schema
  metadata (`json_schema_extra`), not fields. No new `calc` warning may fire on a fixture
  record — that is why the `recess_*`-under-`none` and `bore_flat`-at-`bore_d=0` relations
  are not declared (10 and 4 records sit on those defaults; READ at kickoff). Every shared
  link sends the same fields with the same meaning (L05).
- **The form is generated from `/api/schema` and nothing else** (L02). A relation and a
  selector option live on the model and reach `app.js` through the schema; `app.js` carries
  no `GearParams` field name outside `DIMS`. The pins in `tests/test_api.py` that enforce
  this are tightened under the new `Lxx`, never deleted or allow-listed to get green
  (PITFALLS CF-1).
- **A green gate means the browser ran.** `tests/test_browser.py` has no skip path and no
  environment opt-out; a missing browser is a red `make verify` naming the install command.
- **Measured, never tuned** (L08, L34). The browser test's gate cost is an A/B reading, the
  bar's rule is written down before the first reading, and the human sets the bar from the
  readings. Research figures are starting points, not bars.
- **No Node at runtime** (L11) stays true: `playwright`'s driver is bundled in the wheel and
  used at test time only; the 31-pin runtime closure, the Dockerfile and
  `refresh-requirements.sh` do not move.
- **An idea or debt item is retired only in the commit that closes it** (CLAUDE.md): status,
  sha, `git mv`, INDEX row, same commit.

## v0.5 Requirements

### Browser test — the viewer under a real browser (first)

- [ ] **REQ-browser-server-fixture**: the browser test runs against a real `uvicorn`
  subprocess bound to a socket the fixture pre-binds on `127.0.0.1` and passes down with
  `--fd` (no port race under 8 xdist workers — MEASURED, PITFALLS BT-5), started with
  `start_new_session=True` and torn down by killing the process group; the fixture proves no
  `BuildPool` child survives teardown (children outlived a plain `SIGKILL` by 6 s —
  MEASURED, PITFALLS BT-4). No in-process server thread: `app` is a singleton whose lifespan
  and `dependency_overrides` the `TestClient` tests on the same worker share (READ, ARCH).
- [x] **REQ-browser-form-from-schema**: the test reads `/api/schema` and asserts the rendered
  form carries exactly its groups and fields, in its order — every count read from the schema
  at test time, never hard-coded; the CSS custom properties the renderer reads are non-empty.
- [x] **REQ-browser-first-build-drawn**: after a fresh load the `#dl-stl` href is set only
  after `showModel` returns, the canvas is non-blank against a blank control (the bar — PNG
  size ratio or distinct-pixel count, 38,908 B vs 3,393 B / 11,478 pixels MEASURED on
  SwiftShader — recorded with the reading that set it), and `canvas.dataset.triangles`
  equals the triangle count of the STL the page loaded — the one production line this
  milestone adds to `app.js`, named in the `Lxx`. A `webgl2` context is asserted before
  anything else: `app.js:229` builds `WebGLRenderer` at module top level, so without WebGL
  there is no form (READ; 0 fields under `--disable-3d-apis` MEASURED).
- [x] **REQ-browser-invalid-field-marked**: an out-of-range value marks its field through
  the 422 `detail[].ctx.fields` path and the rendered message names the field.
- [x] **REQ-browser-warning-rendered**: a warning-producing link renders exactly the
  `warnings` text `/api/info` returns for the same query — equality, not containment.
- [x] **REQ-browser-link-round-trip**: every field set in the hash reaches the form, and the
  query `app.js` sends equals the hash — on all three programmatic-value paths (fresh load,
  Reset, `hashchange`). The debounce is waited out on content, never on an empty status or
  a bare href (both pass before the 350 ms debounce fires — MEASURED, PITFALLS BT-6).
- [ ] **REQ-browser-golden-request-sets**: for each of the 44 fixture records' parameter
  sets, the query string the form sends is pinned by the browser test before any form
  change lands, so Phases 23–24 prove "the same fields are sent" rather than assert it.
- [ ] **REQ-browser-fails-closed**: a missing headless shell fails the test with a message
  naming `playwright install --only-shell chromium`; no `importorskip`, no skip marker, no
  environment opt-out, in CI or locally.
- [ ] **REQ-browser-in-the-gate**: `tests/test_browser.py` runs inside `make verify` and CI's
  `test (3.12)` job (the browser installed by a Makefile stamp, with
  `PLAYWRIGHT_BROWSERS_PATH` isolated or `--no-remove` so Playwright's browser GC cannot
  delete another project's cached browser — this host holds `chromium-1228`, MEASURED,
  STACK); excluded from `make verify.fast` and `make test-image` by name in the same commit
  that adds the file, with `test_hooks.py`'s `--ignore` pin extended so the exclusion cannot
  silently lapse (PITFALLS BT-2); its isolated cost (3.21 s serial / 3.80 s at `-n 2`
  MEASURED, STACK) and its A/B cost under the full gate recorded in `bench/RESULTS.md`; one
  `Lxx` records the admission and amends L13 and L36 (L11 restated, unchanged).
- [ ] **REQ-browser-stack-pinned**: `playwright` pinned exactly in the `[dev]` extra (1.63.0
  at research time); no `pytest-playwright`; the default Chrome Headless Shell, never
  `channel="chromium"` (new headless draws on the host GPU, so dev and CI would differ —
  MEASURED, STACK); the Linux path proven on a real `ubuntu-latest` run before the phase
  closes (only an `ubuntu:24.04` container was measured); strict mypy passes with typed
  wrappers around `page.evaluate` (returns `Any`).

### Download name — the file says which root it has

- [ ] **REQ-slug-carries-effective-root**: `GearParams.slug()` appends `_trochoid` only when
  `calc.root_mode` applies the hob root for those parameters; a radial part and an ignored
  trochoid request (`root_shape=trochoid` is a silent no-op at z = 30, 41, 60 — MEASURED,
  FEATURES) keep today's name byte-for-byte. `slug()` stays total — it is called inside
  failure-path log records (READ, PITFALLS SL-2). Tested at z = 23 (applies) and z = 40
  (ignored).
- [ ] **REQ-slug-consumers-read-first**: the `Lxx` lists every consumer of the old names
  before they move — `Content-Disposition` (`app.py`), the record's `slug` (`records.py`),
  `docs/http-api.md`, the two `test_api.py` pins (the trochoid one flips deliberately; the
  radial default one must not) — and records that no cache is keyed by slug (READ: the
  export cache key is `(params, fmt, quality, encoding)`). The idea file is retired in the
  same commit.

### Conditional fields — the form says a field is inert before it is typed

- [ ] **REQ-enabled-when-metadata**: `_f()` accepts an `enabled_when` relation carried in
  `json_schema_extra` and emitted unchanged by `model_json_schema()` (nested dicts/lists
  verbatim, key-sorted at every level — MEASURED, STACK; so a relation never depends on key
  order); the two bare-`Field` `Literal` fields carry it the same way; the grammar is
  project-defined, AND-only, fixed at discuss-phase (the four files propose four shapes), and
  a test proves the key collides with no JSON Schema vocabulary word.
- [ ] **REQ-relations-calc-backed**: every declared relation is one `calc` already warns
  about — `bore_d`/`bore_flat` under `bore_hex > 0`; each cutout group's dimensions while its
  count field is 0 — or refuses — `keyway_width`/`keyway_depth` under `bore_hex > 0` (a 422,
  carrying its own "refused" reason wording; never gated on each other: width alone and depth
  alone are both 422 — MEASURED, PITFALLS CF-2). A parity test proves per row that with the
  relation false, changing the dependent field changes nothing in `derive()` except
  `warnings` (or yields the 422 for the refused class), and fails when the schema and `calc`
  drift. No relation is declared that `calc` does not back.
- [ ] **REQ-dim-and-editable**: an inert field is dimmed (`.field.inactive`) with a reason
  built from the gate field's `title`, stays editable and keeps its value, and is still sent
  — `gearQuery()` reads `input.value` (READ, FEATURES), so the URL/API contract is untouched;
  never `disabled` or hidden (a shared link like `#spoke_count=0&hub_d=40` would load a field
  the user cannot clear); re-evaluated on `input`, `readHash`, Reset and `hashchange`.
- [ ] **REQ-form-walk-proves-relations**: the model-driven field walk extends to every
  relation (schema → form, generic code only); the browser test asserts the dim state of each
  declared relation under the golden request sets; `tests/test_api.py`'s `app.js` pins are
  tightened under one `Lxx` that supersedes 08 D-09 and keeps L02.

### Bore-shape selector — pick the shape, keep the flat contract

- [ ] **REQ-selector-schema-carried**: the selector's options (round / D-flat / hex — a
  fifth "no bore" entry and the keyway's place outside the select decided at discuss-phase)
  live on the model as schema metadata in the same condition vocabulary as `enabled_when`;
  `app.js` renders it from the schema with no bore field name in JS, so the existing
  field-name pin holds unchanged (FEATURES finding 3, ARCH §5.1).
- [ ] **REQ-selector-derives-and-writes-through**: the select's state is derived from the
  flat fields on load and never writes on load; a change writes only the minimum switch-off
  fields, as explicit `"0"` never `''`, remembers values the user typed for restore, and adds
  no entry to the `fields` map — the browser test asserts no non-`GearParams` key in any
  `/api/*` request or in the hash (PITFALLS BS-1); what Hex or D-flat writes when its own
  field is 0 (a pending UI state or a starter value) is decided at discuss-phase.
- [ ] **REQ-selector-round-trips-per-state**: a model-driven round-trip test per selector
  state proves the composed document identical through the selector path, and the 44
  golden request sets are unchanged by the selector's presence.

### Gate bar, venv probe, ledger — measure the shipped gate once (last)

- [ ] **REQ-gate-rule-pre-registered**: before any reading, `bench/RESULTS.md` carries the
  idle threshold (precedent: load < 1.5, Phase 12), the cool-down between runs, N ≥ 5 per
  arm, the give-up rule, and the A/B design — the full gate with and without
  `tests/test_browser.py`, interleaved. This is a new method, not L34's (Phase 15 D-04 read
  loads 5–30 and took the largest of three — READ, ARCH §7.1 / PITFALLS GB-1); the `Lxx` says
  so.
- [ ] **REQ-gate-bar-reset**: the readings are recorded with load, machine and `HEAD`; the
  human sets the bar from them; one `Lxx` amends L34; the stale `63.555 s` / `~64 s`
  sentences in `Makefile`, `.pre-commit-config.yaml` and `docs/HOW_TO_DEVELOP.md` are
  rewritten and IN-03 is retired in the same commit.
- [ ] **REQ-venv-constraint-probe**: in a linked worktree or scratch clone — never the main
  checkout, where `make venv VENV=…` runs `pre-commit install` and bakes that venv's python
  into the shared hook shim (READ, PITFALLS VP-1) — `make venv` under
  `PIP_CONSTRAINT=requirements.txt` is run and `make verify`'s result line, `pip check` and
  the freeze diff recorded (all 31 pins resolve as arm64 wheels — MEASURED, STACK; the
  constraint downgrades `fastapi`/`starlette`/`uvicorn` to the pins). Green: `$(STAMP)`
  gains the constraint and L34's CI sentence widens in the same `Lxx` as the bar. Red: which
  pins fail is recorded and the idea stays filed. Either way `.git/hooks/pre-commit` still
  names `.venv/bin/python` afterwards, and the probe never runs during a gate reading.
- [ ] **REQ-pi5-claim-softened**: README states the hardware every number came from and
  makes no Raspberry Pi 5 claim without a measurement; the idea is retired.
- [ ] **REQ-reverify-recipe**: one paragraph in `docs/HOW_TO_DEVELOP.md` §6 beside the
  ship-note workaround — a fix after verification re-stales the report; re-dispatch
  `gsd-verifier` with the delta, commit, re-ship — or `.ai_skills/reverify-phase` if the
  record shows the loop has hit three times; the idea is retired.

## Future Requirements

Deferred to a later milestone. Tracked here, not in this roadmap.

### Form follow-ups (v0.5.x)

- A stale-response test (the debounce/abort loop under a slow build).
- Distinct styling for refused (422) vs inert (warned) fields.
- The cutout "pick one" lock across the three pattern groups.
- The two unbacked relations — `recess_*` under `recess_sides=none`, `bore_flat` at
  `bore_d=0` — with a `calc` warning first; dropped at kickoff because the warning would
  rewrite 14 fixture records (idea to file in Phase 23).
- The hex warning that fires on default `bore_d`/`bore_flat` (`?bore_hex=6` warns every
  time — reproduced, FEATURES); a `calc` change, filed as debt in Phase 23, never filtered
  in `app.js`.
- `#root_shape=bogus` becomes the default through the blank select where the API returns
  422 (MEASURED, PITFALLS); pinned by the browser test and filed as debt, not fixed here.
- Re-sweeping the xdist knee on the 18-CPU host (the N = 8 knee was swept on 12 CPUs).

### Carried candidates (triggers not fired)

- The gear family — helical first, then internal/ring, then rack; bevel needs a
  product-scope decision (v0.6 candidate).
- The hob-root default flip (D-09: a real fit report or a mating-pair request below
  z_min); a cutout rotation field (a real part asks); the teeth-dependent honeycomb cap
  (D-12 plus a measured sweep).
- Trochoid follow-ups: mate interference against the form diameter; ISO 6336-3 critical
  section (geometry only); an editable dedendum (needs an L05 decision).

### Deferred `nice` debt (external triggers, not fired)

Server-side cancellation; no built-in authentication; Enji Guard; the eleven composed
cutout literals at `rel=1e-6`; the sometimes-lost worker-coverage flush; the
resource-tracker flake (`must` — every failed gate log during Phase 21 is kept and
classified against the four recorded occurrences; no `filterwarnings` entry); the wedged
worker at exit; the xdist worker segfault at exit; Phase 7's Manual-Only Nyquist rows;
`Resolved in:` shas on squashed branches; the English-throughout check.

## Out of Scope

| Feature | Reason |
|---------|--------|
| A Node test runner, a JS framework, a second form library | L11: no Node at runtime; the form stays vanilla JS generated from the schema |
| Pydantic / JSON Schema `if`/`then`, `dependentSchemas` for relations | validator vocabulary; the form needs a display relation, not validation (STACK) |
| Hiding or `disabled`-ing inert fields | a value in a shared link would load into a field the user cannot clear (ARCH §4.3) |
| A model-level `bore_type` field | changes what existing links mean (L05) and adds a `GearParams` field |
| Any new `calc` warning that fires on a fixture record | rewrites `pre_v0_2.json` (14 records on the two unbacked rows) — L26 |
| Caching `ms-playwright` in CI | Playwright's own docs advise against it (DOCS, STACK / PITFALLS) |
| `pytest-playwright` | 0.10.0 autoloads suite-wide; plain `playwright` coexists with the suite (MEASURED, STACK) |
| Measuring on a Raspberry Pi 5 | nobody has the hardware; the claim is softened instead |
| Regenerating the fixture | no phase touches a `GearParams` field or `derive()`'s output |
| The default root flip, a rotation field, a honeycomb cap | their named triggers have not fired |

## Traceability

Filled by the roadmap (2026-10-10). Every requirement maps to exactly one phase.

| Requirement | Phase | Status |
|-------------|-------|--------|
| REQ-browser-server-fixture | Phase 21 | Pending |
| REQ-browser-form-from-schema | Phase 21 | Complete |
| REQ-browser-first-build-drawn | Phase 21 | Complete |
| REQ-browser-invalid-field-marked | Phase 21 | Complete |
| REQ-browser-warning-rendered | Phase 21 | Complete |
| REQ-browser-link-round-trip | Phase 21 | Complete |
| REQ-browser-golden-request-sets | Phase 21 | Pending |
| REQ-browser-fails-closed | Phase 21 | Pending |
| REQ-browser-in-the-gate | Phase 21 | Pending |
| REQ-browser-stack-pinned | Phase 21 | Pending |
| REQ-slug-carries-effective-root | Phase 22 | Pending |
| REQ-slug-consumers-read-first | Phase 22 | Pending |
| REQ-enabled-when-metadata | Phase 23 | Pending |
| REQ-relations-calc-backed | Phase 23 | Pending |
| REQ-dim-and-editable | Phase 23 | Pending |
| REQ-form-walk-proves-relations | Phase 23 | Pending |
| REQ-selector-schema-carried | Phase 24 | Pending |
| REQ-selector-derives-and-writes-through | Phase 24 | Pending |
| REQ-selector-round-trips-per-state | Phase 24 | Pending |
| REQ-gate-rule-pre-registered | Phase 25 | Pending |
| REQ-gate-bar-reset | Phase 25 | Pending |
| REQ-venv-constraint-probe | Phase 25 | Pending |
| REQ-pi5-claim-softened | Phase 25 | Pending |
| REQ-reverify-recipe | Phase 25 | Pending |

**Coverage:**
- v0.5 requirements: 24 total
- Mapped to phases: 24
- Unmapped: 0
- Per phase: Phase 21 — 10; Phase 22 — 2; Phase 23 — 4; Phase 24 — 3; Phase 25 — 5

Phase 24 is discretionary (ROADMAP.md, its "Skip condition"). If it is skipped, its three
requirements move to Future Requirements by an explicit edit with the human, rather than
staying mapped to a phase that did not run.

---
*Requirements defined: 2026-10-10*
*Last updated: 2026-10-10 after roadmap creation (Phases 21–25)*
