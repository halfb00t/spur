# Architecture Research: v0.7 Splined Shaft (a second part type)

**Domain:** adding an external DIN 5480 splined shaft with plain shank as a SIBLING part beside the gear, on the shipped spur app
**Researched:** 2026-10-23
**Confidence:** HIGH for every file/line fact (read in the tree at `2772480`) and for the one probe run (FastAPI query models, below); MEDIUM for the recommended module split and web-form shape (design judgement, not yet built); LOW where marked `ASSUMPTION`.

Scope: how a second part type plugs into the existing seams. Standard-specific content (DIN 5480 formulas, tables, M_Re method) belongs to STACK/FEATURES/PITFALLS and is only touched here where it changes the build order.

## 1. Findings that change the plan (read first)

| # | Finding | Evidence | Consequence |
|---|---------|----------|-------------|
| F1 | **Every gear URL stays safe only if the shaft gets its own routes.** An unknown query key on a gear route is silently ignored today: `GET /api/model.stl?part=shaft&bogus=1` returns 200 (probe run in the repo venv, 2026-10-23). A `part=` switch on `/api/info` or `/api/model.{fmt}` would therefore make a typo or a stale link build the default gear without a word (L08 spirit) and would force `model()` to branch on a key it cannot validate. | probe: `Annotated[Model, Query()]` route, extra key -> 200; `app.py:378-387` | Dispatch by **path prefix** `/api/shaft/...`, never by a query key. The three gear routes (`app.py:373-387`) are not touched, so `/api/schema`, `/api/info`, `/api/model.*` and every shared link are byte-for-byte what they are. |
| F2 | **`model_fields_set` cannot tell "user set it" from "default" on a FastAPI query model.** Probe: a request with no query string reports `model_fields_set == {'module','teeth'}` (all fields). CLI is different: `cli._params` builds its dict from non-`None` flags only (`cli.py:59-61`). | probe output `['module','teeth']` for an empty query | Any "designation conflicts with an explicit field" rule (L03: direct conflict = 422) must read **`request.query_params` keys** on the API and the non-`None` dict on the CLI, then call ONE shared pure function. Do not use `model_fields_set`. |
| F3 | **The 90-line `model()` body (`app.py:386-504`) is the product's admission/cache/error contract and must not be copied.** It owns `_EXPORTS` keying (`:401`), `_build_slot` (`:417`), the four exception->status mappings (`:435-471`), `export_served` and `Content-Disposition` from `params.slug()` (`:496`). A shaft route that duplicates it forks a pinned contract (L04, L12, L19, L37). | read | First commit of the interface work is a **pure move**: extract `async def _serve_model(params, fmt, quality, request, backend) -> Response` from `model()`; gear `model()` becomes `_serve_model(_gear(q), ...)`. Proof: the whole existing `tests/test_api.py` + golden requests unchanged. This is a boundary refactor, scoped and surfaced (CODING_VALUES "Tech debt and refactoring"), so it goes to the human as a stop-and-ask with the recommendation "extract, do not duplicate". |
| F4 | **The kernel lock, the solid cache and the export cache already key correctly for a second class.** `_build_cached = lru_cache(...)(_build_checked)` (`model.py:801`) and `_EXPORTS` key `(params, fmt, quality, encoding)` (`app.py:401`) hash the params object; pydantic equality includes the class (`app.py:244-247` says so) and a probe shows `hash(GearParams()) != hash(ShaftParams())`, `G() != S()`. `pool.executor_for` is `hash(p) % workers` (`pool.py:100-101`), `_write_export` uses only `p.slug()` (`model.py:811`), `records._gear_fields` uses `p.slug()` and `model_dump(exclude_defaults=True)` (`records.py:180`). | read + probe | The worker pool, the export path, both caches and the log records are reused **with type widening only**, provided `ShaftParams` is frozen, hashable and has `slug()`. No new cache, no new pool, no new lock. |
| F5 | **`app.js` pins make a second hard-coded dims table and any quoted field name a test failure.** `test_every_key_the_ui_reads_is_a_derived_dimensions_field` requires every line shaped `['word',` in the whole file to lie inside `const DIMS = [...]` (`tests/test_api.py:176-180`), and `test_the_shareable_link_round_trips_every_field_through_generic_code` forbids any quoted `GearParams` field name outside DIMS (`:314-335`) and counts exactly one `fields.set(` (`:340`). The shaft shares two names with the gear (`teeth`, `module`). | read | Shaft result rows must **not** be a second row table in `app.js`. Carry them in the shaft schema (section 4.5) so the page stays generic (L02). Part-specific URLs live in one descriptor object keyed by an unquoted-field-free structure. |
| F6 | **The browser sweep pins the gear page's every request.** `tests/regression/golden_requests.json` holds the exact `api/info` query for each of the 44 fixture links; the browser test also asserts the hash never carries a key outside `set(properties) | {"mate_teeth"}` (`tests/test_browser.py:697-714`). | read | The gear path through `app.js` must emit byte-identical requests and a hash with no `part` key. `part=shaft` appears only after the user picks the shaft. `golden_requests.json` and `pre_v0_2.json` get **no diff** (`git diff --exit-code`), and are never `regen`'d by this milestone (L26/D-09). |
| F7 | **A tolerance field is a public URL token the day it ships (L05).** Field names, defaults and (for a `Literal`) the existing allowed values of `ShaftParams` become a contract exactly like `GearParams`'. The fit tables arrive last, but the field that selects a fit cannot be renamed or re-defaulted after the interface ships. | L05; PROJECT.md "tables phase blocked" | Freeze the **name set and defaults** of `ShaftParams` in the first phase (including the tolerance fields), even though the tables that give them numbers come last. Allowed values may grow later (additive); a default may not move. |
| F8 | **DIN-5480-specific constants are needed by the maths and the solid, not only by the tolerance tables.** Tip, root, form diameters and the tooth thickness the solid is cut to come from the standard, and PROJECT.md says the tables phase is blocked on the human's copy. | PROJECT.md "Rules this milestone lives by" | The user-proposed order (maths -> solid -> interfaces -> tables) only holds if "tables" is split in two (section 8): **T1 dimension tables / constants** (feeds the maths oracle) and **T2 fit-tolerance tables** (feeds fit limits, M_Re at fit, the designation's fit). Ask the human for the copy's path **before Phase 1 starts**; it is the long-lead dependency. |

## 2. System overview (target state)

```
                       web UI (static/app.js)          CLI (cli.py)            HTTP client
                       part select + PARTS descriptor  `spur ...`  `spur shaft ...`
                              |                              |                      |
   GET /api/schema ---------->|                              |                      |
   GET /api/shaft/schema ---->|   (gear routes UNCHANGED)    |                      |
   GET /api/info, /api/model.{stl,step}                      |                      |
   GET /api/shaft/info, /api/shaft/model.{stl,step}          |                      |
                              v                              v                      v
 +----------------------- app.py (serving process, kernel-free) ---------------------------+
 | gear routes ---------+                                                                  |
 | shaft routes --------+--> _serve_model(params: Part, fmt, quality, request, backend)    |
 |   _shaft(q) resolves designation / strips query extras                                  |
 |   _EXPORTS (bytes LRU)  BUILD_QUEUE (one admission bound for both parts)  gzip L19      |
 +------------------------------------------+---------------------------------------------+
                                            | backend = pool.export(p: Part, fmt, quality)
                                            v
 +-------------------------------- pool.py (BuildPool, N spawn workers) -----------------+
 |   executor_for(p) = hash(p) % N      _run_with_timeout (30 s, terminate, replace)      |
 +------------------------------------------+---------------------------------------------+
                                            | importlib "spur.model"  (inside a worker only)
                                            v
 +-------------------------------- worker process (kernel) -------------------------------+
 |  model.export(p: Part, fmt, quality)   _LOCK   _build_cached   _write_export   malloc_trim|
 |        |  isinstance(p, ShaftParams)?                                                    |
 |        +--> gear pipeline (_build, unchanged)                                            |
 |        +--> shaft_model.build_shaft(p)   <- NEW, the only other module that imports cq   |
 +--------------------------------------------------------------------------------------+

 pure, kernel-free, logger-free:
   gear : params.py  calc.py                          (UNCHANGED)
   shaft: shaft_params.py  shaft_calc.py  din5480.py  din5480_tables.py     (NEW)
   shared type only: parts.py  (Part = GearParams | ShaftParams)            (NEW)
```

## 3. Component responsibilities: new vs modified

### New modules (src/spur/)

| Module | Responsibility | May import | Must not import |
|--------|----------------|------------|-----------------|
| `shaft_params.py` | `ShaftParams`: frozen, hashable pydantic model, field metadata (`group`/`unit`/`step`) via the existing `_f`/`when` builders, `_feasible` validator calling `shaft_calc.check_shaft` by local import (the `params.py:255-265` pattern), `slug()`, schema-carried result rows (4.5), `resolve_shaft(designation, given)` (4.3) | `pydantic`, `spur.params` (builders only), local import of `shaft_calc`, `din5480` | `cadquery`/`OCP`, `spur.model`, `spur.shaft_model`, `spur.records`, `logging` |
| `shaft_calc.py` | `check_shaft(p)` (refuse/cap lists, the `calc.check` role), `derive_shaft(p) -> ShaftDimensions` (typed frozen model, every key always present, `null` where it does not apply, `warnings` list: the `DerivedDimensions` role, L21), shaft outline description the solid consumes (radii/angles, no kernel types) | `pydantic`, `math`, `din5480` | same as above, plus `spur.calc` (see 4.7: independence) |
| `din5480.py` | Pure DIN 5480 maths: basic dimensions from d_B/m/z, profile shift, tooth thickness at a diameter, M_Re over pins/balls, designation format and parse. Constants live in one block with clause citations | `math`, `din5480_tables` | as `shaft_calc` |
| `din5480_tables.py` | Transcribed data only: typed literal tables, one citation (clause/table) per entry, `None` for anything not transcribed. A lookup outside the data returns `None` and the caller warns (L08) | nothing | everything else |
| `shaft_model.py` | `build_shaft(p) -> cq.Solid`: spline outline extrude, end chamfer, shank, `isValid`/one-solid assertion, edge selectors that raise `BuildError` on empty selection (L26 rule) | `cadquery`, `spur.model` (the `_body`, `_shape_of`, `TOL` narrowers), `spur.shaft_calc`, `spur.build_errors` | `spur.app`, `fastapi`, `spur.pool` |
| `parts.py` | `Part = GearParams | ShaftParams` and nothing else, so `pool`, `app`, `records`, `model`, `cli` name the union without importing each other | `spur.params`, `spur.shaft_params` | everything else |

Why a flat `shaft_*`/`din5480*` split and not a subpackage: the package is flat (`.planning/codebase/STRUCTURE.md`), the import-linter contracts name modules, and the docs say "promote to a directory when it stops holding it". `shaft_*` names the **part type**, `din5480*` names the **standard**; a later ISO 4156 / DIN 5481 family adds `iso4156.py` beside `din5480.py` and reuses `ShaftParams` only if the human decides the parameter model generalises (it may not: out of scope here).

### Modified modules (smallest edit each)

| File:line | Change | Gear-visible effect |
|-----------|--------|---------------------|
| `model.py:772` `_build(p)`, `:791`, `:804`, `:809`, `:833` | Widen `p: GearParams` to `Part`. At the top of `_build`: `if isinstance(p, ShaftParams): from .shaft_model import build_shaft; return build_shaft(p)` (local import: `shaft_model` imports `model`'s narrowers, so a module-level import would be circular; same pattern as `params.py:257`, `slug()` `:283`). Everything else in `export`/`_write_export` is already part-agnostic | none; `_build_cached` key space gains a second class |
| `pool.py:53`, `:100`, `:103`, `:164`, `:252` | Type-only: `GearParams` -> `Part`. `_warm` (`:41`) also imports `spur.shaft_model` so the first shaft request does not pay the import | none |
| `records.py:171`, `:211-259` | Type-only widening to `Part`. **Do not add a `part` key** to records: `tests/test_records.py:60` pins the key set and the shaft is already identified by its `slug` prefix (`spur_shaft_...` vs `spur_z...`) | none |
| `app.py` | (a) extract `_serve_model` (F3, own commit); (b) widen `BuildBackend` (`:117`) to `Part`; (c) `_build_slot`'s 503 text says "gears" (`:285`): reword to a part-neutral noun in the same commit, one test; (d) add `ShaftInfoQuery`/`ShaftModelQuery` (the `InfoQuery`/`ModelQuery` pattern, `:232-239`), `_shaft(q, request)` (the `_gear` role, `:242`), three routes under `/api/shaft/` | gear routes, schema, status codes, headers unchanged; only the 503 prose changes (a response string, not a request or a part) |
| `cli.py:42`, `:59`, `:99`, `:119` | Parametrise `_add_gear_args`/`_params` on the model class (keep the gear header string `"gear parameters (defaults in brackets)"` byte-identical: `tests/test_cli.py:199-263` partitions on it). Add a `shaft` sub-command group with `info` and `export` (4.4) | `spur info/export/serve` argv and output unchanged |
| `static/app.js`, `index.html`, `style.css` | Part descriptor + part select + hash `part=shaft` (section 5) | gear requests and hash unchanged (F6) |
| `pyproject.toml:177-222` | Import-linter contracts (section 6) | none |
| `docs/architecture/overview.md`, `http-api.md`, `cli.md`, `web-ui.md`, new `shaft.md`; `README.md`; `AGENTS.md` "What we're building" | Product scope text. `README` shell examples are tests (`tests/test_cli.py:101`), so every shaft example added there runs in the gate | doc only |

### Explicitly NOT touched

`params.py`, `calc.py` (zero lines), `tests/regression/pre_v0_2.json`, `tests/regression/golden_requests.json`, `requirements.txt`, `ci.yml`. If a diff to any of them appears, it is a bug in the phase (L26, D-03/D-09).

## 4. Integration decisions (each needs a logged `Lxx` before the phase that builds it)

### 4.1 Where the shaft parameter model lives

`shaft_params.ShaftParams`, sibling of `GearParams`, never fields on it (PROJECT.md target feature 1; L05 forbids moving the gear). It reuses `params._f`, `params.when` and `params._extra` by import: zero edits to `params.py`, so the gear schema cannot move. Cost: importing underscore names across modules. The alternative (moving the four helpers to a `fieldmeta.py`) is a cleaner module graph but a diff on `params.py`; recommend the import, and move the helpers only if the human prefers (then prove `GearParams.model_json_schema()` equal before and after).

Field set (names frozen by F7; `ASSUMPTION`: the numeric defaults are the PROJECT.md example `W 25x1.25x18x8f`, so the default shaft is the standard's own designation): reference diameter `d_B`, `module`, `teeth`, tolerance fit (quality + deviation), splined length, end chamfer, shank diameter, shank length. d_B, module and teeth are three inputs with the profile shift **derived** (per PROJECT.md "profile shift as the standard derives it"), so there is no redundant triple to reconcile. Pressure angle is not a field (the standard fixes it).

### 4.2 Dispatch by part type

| Layer | Mechanism | Why |
|-------|-----------|-----|
| HTTP | Path prefix: `/api/shaft/schema`, `/api/shaft/info`, `/api/shaft/model.{stl,step}` | F1. No collision with `/api/model.{fmt}`: probe shows both resolve independently |
| Pool / worker | Type of the params object (`isinstance` in `model._build`) | the object already crosses the process boundary by pickle; no string tag to get wrong |
| Records / logs | None needed; `slug()` prefix distinguishes | F4 |
| CLI | Sub-command group `spur shaft info|export` | gear and shaft share flag names (`--teeth`, `--module`) with different ranges and defaults; one shared flag namespace would need two-phase parsing. Existing `spur info/export` argv untouched |
| Web | Part descriptor in `app.js` (section 5) | |
| Slug / download name | `ShaftParams.slug()` -> `spur_shaft_W{d_B:g}x{m:g}x{z}_{fit}` (filename-safe, no space) | cannot collide with `spur_z...`; like the gear slug it is a name, not a cache key (L40) |

Rejected: a `part` query key on shared routes (F1); `/api/{part}/...` generic path (would shadow `/api/health` and `/api/schema`); one union-typed `GearParams`-style model with `part` as a field (breaks L05, the schema and 44 golden requests).

### 4.3 Designation as input, one rule in one place

`din5480.parse_designation(text)` returns the four flat values (d_B, module, teeth, fit) or raises a message; `shaft_params.resolve_shaft(designation, given: Mapping[str, object]) -> ShaftParams` is the only place that (a) refuses `designation` together with any explicit flat field (L03, names the fields), (b) builds the model. API: `_shaft(q, request)` passes `request.query_params` keys as `given` (F2); CLI passes its non-`None` dict; the web page does not hold the grammar (L02): if it accepts a pasted designation, it calls a small read-only `GET /api/shaft/designation?text=` that returns the flat fields, and writes only flat fields into the form, the L42 pattern. The link carries flat fields, never the designation. The printed designation is a result row (`designation`, string). Open for discuss-phase: ship the paste box or print-only in the web UI (print-only is the cheaper first cut).

Check on the error shape: `loc` for a bad designation must be `["query","designation"]`, same envelope as `app.py:438` so `problems()` in `app.js:206-221` renders it.

### 4.4 CLI

```
spur shaft info   [--d-b ... --module ... --teeth ... --fit ... | --designation "W 25x1.25x18x8f"]
spur shaft export -o shaft.step [--format] [--quality] [same flags]
```

`cmd_shaft_export` is `cmd_export` with `ShaftParams` and `derive_shaft(p).warnings`; calls `model.export` (the dispatching one), so no CLI-side kernel dispatch. Exit codes follow L03/`cli.py:59-68`: refusal exit 2, `BuildError` exit 1. Duplicate the ~15 lines rather than abstract over the part (three similar lines beat a premature abstraction); revisit at the third part. The `cli` import-linter contracts already cover it (it imports `model` lazily, `cli.py:102`).

### 4.5 Web form and result rows stay schema-driven

`/api/shaft/schema` returns `ShaftParams.model_json_schema()`; the generic `buildForm()` already renders `properties` by `group`/`unit`/`step`/`enum`/`enabled_when` (`app.js:54-110`). For the result rows add a model-level key in `json_schema_extra`, **`dims`: a list of `{key, label, unit}`** (the same trick as `selectors`, `params.py:87`), rendered by generic code. Reasons: F5 (no second `['key', 'Label']` table in JS, no per-part knowledge in the page, L02), and the "every key the UI reads is a field of the response model" test becomes a **Python** test on `ShaftDimensions` instead of a regex over JS. `unit: ""` rows render as text (the `designation`), since `renderInfo` today assumes `fmt(v) + " mm"` (`app.js:231`). Fit-limit pairs (min/max tooth thickness, M_Re min/max) are separate flat scalar keys, not nested objects.

### 4.6 Worker pool and export path reuse (no new work)

Admission (`BUILD_QUEUE`, `app.py:102`), gzip inside the slot (L19), `_EXPORTS` LRU, `BuildPool` affinity/timeout/replacement, `malloc_trim`, `SPUR_SOLID_CACHE` (4 entries shared across parts) all apply unchanged. What must be **measured, not assumed** (CLAUDE.md, L07/L17/L37): (a) heaviest allowed shaft build time against `SPUR_BUILD_TIMEOUT=30` s (a long, many-toothed spline fused with a shank and chamfered is a boolean on a many-faced prism; the field `le` bounds are set from a sweep, the way `spoke_count` was lowered 200->40->32, `params.py:182-199`); (b) resident memory with one shaft solid beside gear solids in a worker (L17's 4 GiB `mem_limit` was measured on gear corpora only); (c) STL size at `quality=fine` for a long shaft (gzip level was chosen on 9 MB and 17 MB gear STLs, `app.py:172-210`). Add a `bench/` row for each; no estimate goes in a comment.

### 4.7 Sibling independence

Shaft maths shares no code with `calc.py`: it re-writes the 3-line `inv()` (`calc.py:117-119`) instead of importing it. This keeps the oracle independent (precedent: `tests/trochoid_oracle.py` shares no code with `calc`) and means a future change to gear maths cannot move a shaft number, nor the reverse (L05/L26 in both directions). `shaft_model` importing `model`'s `_body`/`_shape_of`/`TOL` is the one deliberate cross-edge (kernel narrowers, L35); if the human dislikes importing private names, move those two functions to a `kernel_types.py` as its own commit.

## 5. Web form: switching part type and encoding it in links

State: `part` in `{gear, shaft}`; a `PARTS` descriptor object holds, per part: schema URL, info URL, model URL base, whether the mate box shows, header/aria text. `fields`, `defaults`, `rejected`, `stash`, `selectors` are cleared and rebuilt on a switch (they are module-level today: `app.js:8-15`, `:322`, `:329`).

| Aspect | Gear (unchanged) | Shaft (new) |
|--------|------------------|-------------|
| Hash | non-default fields (+ `mate_teeth`), **no `part` key**, ever | `part=shaft&` + non-default shaft fields |
| `buildForm` source | `api/schema` | `api/shaft/schema` |
| Info / STL / download | `api/info`, `api/model.stl`, `api/model.{kind}` | `api/shaft/info`, `api/shaft/model.stl`, `api/shaft/model.{kind}` |
| Mate-teeth row | shown | hidden, `mate_teeth` neither read nor sent |
| `gearQuery()` | byte-identical output (F6) | same function over the shaft `fields` |
| Unknown `part=` value | n/a | any non-empty `part` other than `shaft` is **refused visibly** (L44 precedent: invalid links may change behaviour, valid ones may not). `part=gear` is not accepted as a second spelling of the gear link |

Mechanics to keep right:
- `buildForm()` is async and `readHash()` sync (`app.js:119-128`, `:240-252`): boot becomes read `part` from the hash, `await buildForm(part)`, `readHash()`, `update()`. A `hashchange` that changes `part` must await a rebuild before `readHash()`; a same-part `hashchange` stays the synchronous path of today.
- The part select lives in `<aside>` **outside** `#params`, so `form`'s `input` listeners (`app.js:211-213`) never see it and it is never a field (the L42 rule: a view, not a field; the `fields.set(` count stays 1).
- `Reset` resets the current part only. Switching part does not carry values across (the names overlap but the ranges and defaults do not: sending gear `teeth=19` into a shaft is a different part).
- `showModel` refits when size changes more than 30 % (`app.js:609-613`), so a switch refits; camera/grid assume a part standing on Z. A shaft is long on Z; check `placeGrid()`/`fit()` visually (the browser test reads only `canvas.dataset.triangles`).
- Headings: `index.html` has gear-only strings (`<title>`, `.sub`, `aria-label="3D preview of the gear"`, the `.hint`). Gear defaults stay as the static text; the descriptor swaps them on the shaft.

Risk to flag: a pre-existing gear link that happens to carry a stray `part=...` token used to load the default gear; after v0.7 it is refused. That is an invalid link, the same class as L44, and no fixture or README link carries one (`grep -c '"part'` over both `tests/regression/*.json` files reads 0); record it in the `Lxx`.

## 6. Import-boundary contracts to add (`pyproject.toml`, after line 222)

Today's contracts list `spur.calc`, `spur.params`, `spur.cli` for the kernel (`:186`), `spur.calc` for the logger (`:210`), `spur.app` indirectly for the kernel (`:221`). New modules are not covered by any of them until listed, and the first contract is `allow_indirect_imports = true`, so a pure module could reach the kernel through `spur.model` unnoticed. Add (each in the same commit that adds the module, since import-linter rejects names that do not exist yet):

1. **"The shaft maths stays free of the CAD kernel and the solid"**: `source_modules = [spur.shaft_params, spur.shaft_calc, spur.din5480, spur.din5480_tables]`, `forbidden_modules = [cadquery, OCP, spur.model, spur.shaft_model]`, `allow_indirect_imports = false`. Stricter than the gear's (which allows indirect), cheap to satisfy, closes the hole above.
2. **"The shaft maths stays free of the logger"**: same four sources, forbidden `spur.records`, `logging` (mirrors `:202-211`; `shaft_params` imports `spur.params`, which does not import records).
3. **Extend the existing "serving process" contract** only by being true already: `spur.app` -> `shaft_params`/`shaft_calc`/`parts` are kernel-free, `shaft_model` is reached only through `model`'s local import inside a worker. Its `allow_indirect_imports = false` therefore proves the shaft never entered the parent. Verify by deliberately importing `shaft_model` from `app` once and watching `make lint-imports` fail (the repo's own standard: "verified by deliberately introducing one", CODING_VALUES "Coupling").
4. **"The kernel doorways are model and shaft_model"**: `type = "forbidden"`, `source_modules = [spur.app, spur.cli, spur.pool, spur.records, spur.parts]`, `forbidden_modules = [spur.shaft_model]`, `allow_indirect_imports = false`. `cli` and `pool` import the kernel only at runtime through `model`/`importlib` (`pool.py:63`, `cli.py:102`), so none may name `shaft_model`; this keeps "one doorway through `model.export`" true in the module graph after a second kernel module exists. (`pool._warm` imports it by `importlib` string, which import-linter does not see; that is the established pattern, `pool.py:41-50`.)
5. **"Gear maths does not know the shaft"**: `source_modules = [spur.calc, spur.params]`, `forbidden_modules = [spur.shaft_params, spur.shaft_calc, spur.din5480, spur.din5480_tables, spur.shaft_model, spur.parts]`, `allow_indirect_imports = false`. This is the structural half of "every gear link builds the same part".
6. **Tests that pin the contracts' claims** (the repo pairs each contract with a regex test: `tests/test_records.py:246`): a test that `shaft_calc`/`din5480` source files contain no `import logging`/`cadquery`, and that `ShaftParams` is frozen and hashable, and `hash(ShaftParams()) != hash(GearParams())`.

`spur.model` importing `shaft_model` lazily is a gear-side edge to a shaft module, so contract 5 deliberately excludes `spur.model` from its sources.

## 7. Data flow

### Request flow: shaft STL preview

```
page: #part=shaft&teeth=20
  -> buildForm(api/shaft/schema)  -> fields rendered from ShaftParams schema (groups/units/enabled_when)
  -> update():  GET api/shaft/info?teeth=20          -> ShaftDimensions (typed, nulls + warnings)
                GET api/shaft/model.stl?teeth=20&quality=preview
     app.py:  ShaftModelQuery (FastAPI validates ranges) -> _shaft(q, request) -> ShaftParams (validated ONCE, check_shaft in the model validator)
              _serve_model(params, "stl", "preview"):  _EXPORTS key (params, fmt, quality, enc)
              miss -> _build_slot -> pool.export(params) -> worker: model.export -> _build -> build_shaft
              -> bytes -> gzip in slot -> Content-Disposition spur_shaft_...stl
```

### Parity (the REQ-three-interfaces pattern, reused)

CLI and API print the same document: `spur shaft info` prints `derive_shaft(p).model_dump_json(indent=2)` as `cli.py:96` does for the gear; `tests/test_cli.py:67` (`test_cli_and_api_print_the_same_document`) is the template, one parity test per shaft feature. A refusal reads the same on both (`test_every_refusal_reads_the_same_on_the_api_and_the_cli`, `:434`).

### State

Nothing persisted, nothing new (CODING_VALUES "State"). The shaft adds no module-level state; the one lock and the one solid cache stay in `model.py`.

## 8. Suggested build order (phases)

Honouring dependencies and the human's order (maths -> solid -> interfaces -> tables), with the one correction from F8 and F7.

| Phase | Content | Gear-safety proof | Needs the DIN copy? |
|-------|---------|-------------------|---------------------|
| **A. Seam and contracts** | New `Lxx` widening product scope and amending L02 ("one parameter model **per part type**, three front ends each"). `parts.py`; type widening in `pool`/`records`/`model` signatures; `model._build` dispatch stub; the extract-`_serve_model` pure move; 503 wording; import-linter contracts 1-5 with empty-but-real modules | `git diff --exit-code tests/regression/`, `make verify` unchanged count, `/api/schema` JSON equal before/after | no |
| **B. Shaft maths (pure)** | `ShaftParams` with the **frozen field set and defaults** (F7), `shaft_calc`, `din5480` basic dimensions, profile shift, tooth thickness, M_Re. Independent oracle for M_Re from the built outline geometry (shares no code, like `trochoid_oracle.py`); every DIN-specific constant behind one cited block; anything not yet proved returns `None` + warning | n/a (new files) | **yes for the constants and the dimension-table oracle (T1)**; M_Re's geometric oracle needs only the maths |
| **C. Solid** | `shaft_model.build_shaft`: outline, extrude, chamfer, shank; one-valid-solid assertion; edge selectors that raise on empty (L26); proved against the closed-form cross-section area x length + shank volume, watertight STL, bbox; heaviest-allowed build time and worker RSS measured and recorded (4.6), `le` bounds set from the sweep | gear fixture replay still 85 cases green | uses T1 constants |
| **D. Interfaces** | API routes + `ShaftInfoQuery`/`ShaftModelQuery`/`_shaft`; `resolve_shaft` and designation round trip; CLI `shaft` group; web part select, descriptor, `dims` rows, hash `part=shaft`; parity tests per feature; browser scenario for shaft (load, edit, 422 marks, link round trip, switch back to gear emits no `part`); README examples; docs | `golden_requests.json` no diff, 44-link browser sweep green | no |
| **E. Fit tables (T2)** | Transcribe DIN 5480-2 tolerance fields with clause/table citations, second read, then fit limits on tooth thickness, M_Re at fit, designation fit, allowed tolerance values grow (additive); out-of-table values warn with no number | n/a | **yes (T2)** |

Ordering rationale: A first because every later phase leans on `Part`, the contracts and the extracted `_serve_model`, and A is the only phase that edits gear files, so its gear-safety proof is cleanest alone. B before C because the solid consumes only numbers B proves (the `calc` decides / `model` acts split). C before D so the interfaces never expose a part the kernel cannot build. E last because T2 is blocked on the human's copy and only feeds the tolerance-dependent rows, which the earlier phases already print as `null` with a sentence. If the copy arrives early, T1 can be transcribed inside B; if it arrives late, A and the geometry-only part of B proceed and B's DIN constants wait.

### Research flags for phases

- A: stop-and-ask on the `_serve_model` extraction and the `Lxx` wording; standard patterns otherwise.
- B: **needs the copy and deeper standard-specific research** (formulas, M_Re method for the DIN 5480 flank-centred case, pin/ball size rule); keep out of this file.
- C: needs a kernel spike: spline outline as 16-point flank polylines vs `makeSpline` (the gear uses polylines + arcs, `FLANK_POINTS = 16`, `model.py:58`; the trochoid root uses one `makeSpline` per side), build-time and facet-count at the largest tooth count; the end chamfer's edge selection must follow the L26 "never silently select nothing" rule.
- D: standard patterns; the web hash/boot rewrite (section 5) is the only delicate part, covered by the browser test.
- E: transcription risk, not architecture.

## 9. Anti-patterns to avoid

1. **Adding `part` (or any shaft field) to `GearParams`, or a `part` query key to gear routes.** Breaks L05 and F1.
2. **Importing `calc` helpers into shaft code "to save lines".** Couples the oracle to the thing it checks and lets a gear change move a shaft number (4.7).
3. **Copying `model()` into a shaft route.** Forks admission, caching, error mapping (F3).
4. **A second pool or lock for shafts.** Every kernel call must be inside `model._LOCK` (L06/L18); dispatching inside `model._build` guarantees it, a separate `shaft_model.export` would not.
5. **A second hard-coded rows table in `app.js` or a regenerated golden file.** Breaks F5/F6 pins and the "form is generated from the schema" rule (L02, v0.5 rule).
6. **Printing a DIN-specific number from an unverified constant while the tables are pending.** Return `None` + a sentence (L08); the number appears in the phase that cites its clause.
7. **Silently accepting a stray `part=` or a designation that disagrees with explicit fields.** Refuse (L03, L44).

## 10. Decisions this research raises against the log (flag, do not decide)

| Lxx | Tension | Recommendation |
|-----|---------|----------------|
| **L02** "`GearParams` is the single definition of a gear" | Two models now. The spirit (one model per part feeding schema, flags, query) holds; the sentence does not | New `Lxx` amending L02 to "one model per part type", same entry widens the product scope (PROJECT.md target feature 1) |
| **L05** | Shaft links become a second frozen contract; a stray `part=` on the gear page changes from ignored to refused | Freeze shaft names/defaults in Phase B (F7); log the `part=` refusal as an L44-class invalid-link change |
| **L06/L18** | "Every OCCT call goes through one RLock **in `model.py`**" | Stays literally true if dispatch is in `model._build`; if `shaft_model` ever gets its own `export`, it breaks. Keep the single entry |
| **L12, L19, L37** | One admission bound, one gzip level, one 30 s timeout now cover a second part with unmeasured cost | Measure (4.6) before accepting; amend L37 only if a shaft row exceeds 30 s |
| **L17** | `mem_limit: 4g` was measured on gear corpora | One N=2 sweep with a shaft in the mix, recorded in `bench/RESULTS.md`; no change unless it moves the peak |
| **L21** | `ShaftDimensions` must be typed, frozen, every key present, no explicit `Any` | Follow the pattern; `init_typed`/`init_forbid_extra` already set globally |
| **L26** | Regression fixture is gear-only | Do not extend `pre_v0_2.json`. Optionally add a separate small `tests/regression/shaft_v0_7.json` with its own `make` target so later spline families inherit a guard; not required for v0.7 |
| **L41/L42** | `enabled_when` / `selectors` are `GearParams` conventions | Reuse the same vocabulary on `ShaftParams` (e.g. the shank fields dim when shank length is 0); no new grammar |
| **L43** | Gate bar 300 s | Shaft tests add cost; measure the delta in `make verify` before Phase D closes and record it, as every prior milestone did |

None of the above contradicts a logged decision outright; L02's wording and the L05 corner are the two that need a new entry before code lands.

## Sources

- Code read at `2772480`: `src/spur/{params,app,cli,pool,model,records,build_errors,calc}.py`, `src/spur/static/{app.js,index.html}`, `pyproject.toml` (import-linter contracts `:166-222`), `tests/test_api.py`, `tests/test_cli.py`, `tests/test_browser.py`, `tests/regression/*`, `docker/smoke.py` (HIGH).
- `docs/architecture/{overview,http-api,web-ui}.md`, `docs/architecture/decision_log.md` L02-L06, L12, L17-L19, L21, L26, L37, L40-L45, `docs/CODING_VALUES.md`, `AGENTS.md`, `.planning/PROJECT.md` "Current Milestone v0.7", `.planning/codebase/STRUCTURE.md` (HIGH).
- Probe run 2026-10-23 in the repo venv (FastAPI `Annotated[Model, Query()]`): extra query key ignored; `model_fields_set` reports defaults as set; `/api/model.{fmt}` and `/api/shaft/model.{fmt}` coexist; `hash`/`==` differ across two frozen pydantic classes (HIGH, reproducible; script in the session scratchpad only).
- DIN 5480 content deliberately not researched here: see STACK/FEATURES/PITFALLS.

---
*Architecture research for: spur v0.7 Splined Shaft (second part type)*
*Researched: 2026-10-23*
