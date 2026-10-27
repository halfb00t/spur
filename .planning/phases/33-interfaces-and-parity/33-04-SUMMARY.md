---
phase: 33-interfaces-and-parity
plan: 04
subsystem: api
tags: [fastapi, shaft, din5480, designation, schema-dims, serve-model, l49, decision-log]

requires:
  - phase: 33-interfaces-and-parity
    provides: "33-03's _numbers_as_written dependency and L49; 33-02's shank_d relation; Phase 32's shaft solid and derive_shaft"
provides:
  - "GET /api/shaft/schema, /api/shaft/info and /api/shaft/model.{stl,step} through the gear's _serve_model, unchanged"
  - "ShaftParams.model_config json_schema_extra dims: twelve {key, label, unit} rows in ShaftDimensions order"
  - "src/spur/shaft_params.py: SPLINE_KEYS, DesignationConflict, designation_clash, clash_message, resolve_shaft (shared with 33-05's CLI)"
  - "422 types conflict (ctx.fields) and designation at loc [query, designation]; an infeasible designation is a 422 there with the model's own type"
  - "the shaft download name spur_shaft_w25x1.25x18.<fmt> frozen (D-17)"
affects: [33-05, 33-06, 33-07, 33-08, 33-09]

actuals:
  tokens: 8514   # chars/4 over every added line of the three code and doc commits since 1e0e366 (34054 chars); the estimate of 90000 counted reads and a ~250-line test file
  tasks: 3
  commits: 3
plan_head_before: 1e0e3664aa0ef63edd3fbca77dfd181be27fa320
plan_head_after: c9e0419bfffd0f3c06194cf7ff969d1ac9e5b635

tech-stack:
  added: []
  patterns:
    - "a second part's routes reuse _serve_model with a query model subclass stripped back to the plain params class (_shaft), so equal parts share one cache key"
    - "a conflict is decided on query key presence in a route dependency before any value is parsed, by one pure function shared with the CLI"
    - "a model's result rows ride its schema as json_schema_extra, with a light test keeping them complete against the result model"

key-files:
  created:
    - tests/test_shaft_interfaces.py
  modified:
    - src/spur/app.py
    - src/spur/shaft_params.py
    - tests/test_api.py
    - tests/test_seam.py
    - docs/architecture/decision_log.md
    - docs/architecture/http-api.md
    - README.md

key-decisions:
  - "DesignationConflict keeps the plan's (and 33-05's) name with a noqa N818, the precedent being BuildTimeout in build_errors.py"
  - "resolve_shaft builds with ShaftParams.model_validate on a merged dict, not a ** call, so mypy --strict needs no type: ignore (the gate forbids one)"
  - "the solid fields _shaft hands resolve_shaft are every ShaftParams field but SPLINE_KEYS, so a field added later joins the solid without a second list"

patterns-established:
  - "Pattern: _designation_conflict first in dependencies, _numbers_as_written second; the conflict wins over a number error"

requirements-completed: [REQ-shaft-api, REQ-designation-input]

coverage:
  - id: D1
    description: "The shaft is served at /api/shaft/schema (with twelve dims rows), /api/shaft/info (derive_shaft's document) and /api/shaft/model.{stl,step} under its frozen name, with the gear's admission, cache, gzip and error contract"
    requirement: "REQ-shaft-api"
    verification:
      - kind: integration
        ref: "tests/test_shaft_interfaces.py#test_the_rows_are_every_dimension_but_the_warnings_in_order_with_their_own_units"
        status: pass
      - kind: integration
        ref: "tests/test_shaft_interfaces.py#test_info_with_no_query_is_the_default_shafts_document"
        status: pass
      - kind: integration
        ref: "tests/test_api.py#test_a_shaft_downloads_as_stl_and_step"
        status: pass
      - kind: integration
        ref: "tests/test_api.py#test_a_saturated_service_refuses_a_shaft"
        status: pass
    human_judgment: false
  - id: D2
    description: "The as-written refusal applies to every shaft number field on info and model"
    requirement: "REQ-shaft-api"
    verification:
      - kind: integration
        ref: "tests/test_shaft_interfaces.py#test_a_plus_sign_is_refused_as_written_on_every_shaft_number_field"
        status: pass
    human_judgment: false
  - id: D3
    description: "A designation builds the same shaft as its four fields, combines freely with the solid fields, shares one cache entry with its flat link, and is accepted in the codec's spellings"
    requirement: "REQ-designation-input"
    verification:
      - kind: integration
        ref: "tests/test_shaft_interfaces.py#test_a_designation_is_the_same_shaft_as_its_four_fields"
        status: pass
      - kind: integration
        ref: "tests/test_shaft_interfaces.py#test_a_designation_combines_freely_with_the_solid_fields"
        status: pass
      - kind: integration
        ref: "tests/test_api.py#test_a_designation_and_its_fields_share_one_cached_shaft"
        status: pass
    human_judgment: false
  - id: D4
    description: "A designation beside reference_d, module, teeth or fit is a 422 conflict on key presence before any value is parsed; unparseable, empty, overlong, non-ASCII and infeasible designations are 422s at designation, never a 500"
    requirement: "REQ-designation-input"
    verification:
      - kind: integration
        ref: "tests/test_shaft_interfaces.py#test_a_spline_field_beside_a_designation_is_a_conflict_on_key_presence"
        status: pass
      - kind: integration
        ref: "tests/test_shaft_interfaces.py#test_an_infeasible_designation_is_a_422_with_the_models_sentence"
        status: pass
      - kind: other
        ref: "a throwaway 1809-case fuzz of /api/shaft/info?designation= (random strings plus 300 structured near-valid ones): 0 answers other than 200 or 422"
        status: pass
    human_judgment: false
  - id: D5
    description: "The gear routes, their keys and the gear /api/schema bytes are unchanged"
    requirement: "REQ-shaft-api"
    verification:
      - kind: other
        ref: "make gear.unchanged"
        status: pass
      - kind: integration
        ref: "tests/test_seam.py#test_the_shaft_routes_take_the_shaft_fields"
        status: pass
    human_judgment: false
  - id: D6
    description: "L49's paragraph The shaft's API, http-api.md and the README read true and say what shipped"
    requirement: "REQ-shaft-api"
    verification: []
    human_judgment: true
    rationale: "A decision-log entry's and the docs' wording is read by a person; the greps in the plan only prove the paragraph and the routes are named"

duration: 11min
completed: 2026-10-27
status: complete
---

# Phase 33 Plan 04: The shaft's API and the designation Summary

**The shaft is on the API at `/api/shaft/schema`, `/info` and `/model.{stl,step}` through the gear's own `_serve_model`, its twelve result rows ride its schema as `dims`, and `designation=W 30x2x14x8f` takes the place of the four spline fields: a designation beside any of them is a `422 conflict` on key presence, and every bad or infeasible designation is a `422` at `designation`, never a `500`.**

## Performance

- **Duration:** 11 min
- **Started:** 2026-10-27T16:33Z
- **Completed:** 2026-10-27T16:44Z (the code and doc commits; the full `make verify` of 3 min 36 s sits inside it)
- **Tasks:** 3 (1 tracer, 2 auto)
- **Files modified:** 8 (1 created test file, 7 modified)

## Accomplishments

- **Routes and keys as shipped.** `GET /api/shaft/schema` (no keys), `GET /api/shaft/info` (the eight `ShaftParams` fields plus `designation`), `GET /api/shaft/model.{fmt}` (the same plus `quality`, default `fine`). The model route is `return await _serve_model(_shaft(q), fmt, q.quality, request, backend)`: `_serve_model` has no deleted line against `6800769`. `ShaftInfoQuery(ShaftParams)` adds `designation`; `ShaftModelQuery(ShaftInfoQuery)` adds `quality`. The seam test pins the keys: `fields | {"designation"}`, `fields | {"designation", "quality"}`, and no key on the schema.
- **The dims rows.** `ShaftParams.model_config = ConfigDict(frozen=True, json_schema_extra={"dims": [...]})`, twelve inline `{key, label, unit}` rows in `ShaftDimensions` order, `warnings` left out: `reference_d` "Reference Ø d_B" mm, `profile_shift` "Profile shift x" "", `profile_shift_mm` "Profile shift x·m" mm, `pitch_d` "Pitch Ø", `tip_d` "Tip Ø", `root_d` "Root Ø", `nominal_thickness` "Nominal tooth thickness", `form_d` "Form Ø d_Ff", `pin_d` "Pin Ø D_Re", `measure_over_pins` "Measurement over pins M_Re", `end_chamfer_effective` "End chamfer used" (all mm), `designation` "Designation" "". A light test compares keys, order and units against `ShaftDimensions` field by field.
- **The 422 shapes.** Conflict: `{"loc": ["query", "designation"], "type": "conflict", "msg": "The designation sets reference_d, module, teeth and fit, so it cannot be given together with teeth.", "ctx": {"fields": ["designation", "teeth"]}}`, with each present key in spline order (`reference_d=&fit=` gives `["designation", "reference_d", "fit"]`). Unreadable designation: type `designation`, the codec's sentence (`8F` named, `+30` named, the 64-character cap, `N` hub refused). Infeasible (`W 6x0.5x6x8f`): type `infeasible`, the model's profile-shift sentence, same `loc`. A shaft the fields' bounds refuse (`W 900x...`) is the field's own type at the same `loc`.
- **One function decides the clash.** `designation_clash(keys)` runs in `_designation_conflict` (first in both routes' `dependencies`, before `_numbers_as_written`) and again inside `resolve_shaft`, which raises `DesignationConflict` itself, so no caller can let a designation win. 33-05's CLI imports the same functions.
- **Shared cache.** `_shaft` resolves a designation to the four spline fields and returns a plain `ShaftParams`: the light test sees the backend called once with an equal `ShaftParams` for the designation link and its flat link, and the heavy test (`test_a_designation_and_its_fields_share_one_cached_shaft`) shows the second served without a second build.
- **No 500.** A throwaway fuzz of 1809 designation strings (1500 random over the codec's alphabet plus `+`, `-`, `_`, `e`, a non-ASCII digit and `×`; 300 near-valid with bounds and fit edge cases; 9 hand-picked) answered only 200 or 422. The fuzz script lived in the scratchpad and is not committed; the committed tests cover the named cases.
- **Docs.** L49 gained the paragraph **The shaft's API** (28 lines added, 0 deleted in the committing diff), `http-api.md` the three routes, the 422 types, a curl pair and the test files, the README `## API` the four shaft rows and one designation `curl`. `ShaftParams.slug()`'s docstring now names the frozen download name (L49, D-17).
- **Gate figures.** `make verify.fast`: `2291 passed in 11.38s`, `real 12.375 s` (limit 30 s, 1-minute load 4.94 at start). `make verify` (exit 0): `2742 passed in 215.57s (0:03:35)`, `real 3:36.50`, coverage 98.43 %, `Contracts: 10 kept, 0 broken.`, `gear.unchanged` green. 1-minute load average: 5.38 before the run, 8.35 after it (the host was not idle, so the time is no claim about the plan; 33-03 read 314.50 s at an unrecorded load, 33-01's baseline was 229.17 s). 33-09 owns the gate delta.

## Task Commits

1. **Task 1: Tracer: the default shaft through `/api/shaft/schema`, `/info` and `/model.{fmt}`, rows carried by the schema** - `b50fd9d` (feat)
2. **Task 2: A designation in place of the spline fields; a clash is a 422 on key presence** - `a6c9442` (feat)
3. **Task 3: The shared cache, the API docs and L49's API paragraph; the download name frozen** - `c9e0419` (docs)

**Plan metadata:** the `docs(33-04): complete ...` commit that adds this file (hash in the orchestrator's return).

## Files Created/Modified

- `src/spur/app.py` - `ShaftInfoQuery`, `ShaftModelQuery`, `_designation_conflict`, `_shaft`, the three routes, the module docstring
- `src/spur/shaft_params.py` - `dims` in `model_config`, `SPLINE_KEYS`, `DesignationConflict`, `designation_clash`, `clash_message`, `resolve_shaft`, the `slug()` docstring
- `tests/test_shaft_interfaces.py` - 70 light cases (rows, info, as-written, download, designation); stub backend
- `tests/test_seam.py` - `test_the_shaft_routes_take_the_shaft_fields`
- `tests/test_api.py` - `test_a_shaft_downloads_as_stl_and_step`, `test_a_saturated_service_refuses_a_shaft`, `test_a_designation_and_its_fields_share_one_cached_shaft`
- `docs/architecture/decision_log.md`, `docs/architecture/http-api.md`, `README.md` - as above

## Decisions Made

Three small choices inside the plan's room, listed in `key-decisions`: the `noqa: N818` on the name 33-05 imports, `model_validate` over a `**` call (the gate forbids `type: ignore`), and the solid fields derived as `ShaftParams` fields minus `SPLINE_KEYS`. No new `Lxx` was needed: every paragraph went under L49.

## Deviations from Plan

None - plan executed exactly as written, with notes that are not rule deviations:

- `test_a_saturated_service_refuses_a_shaft` asks for `splined_length=31`, not the default shaft: the byte cache answers a cached shaft before the queue is asked (the first red-to-green run answered `200`), and the default shaft's preview STL is cached by the download test in the same module. The gear test has no such neighbour.
- The plan's `SPLINE_KEYS == Designation._fields` is a test, not a module-level `assert`: an `assert` in `src` is stripped by `-O`.
- 33-01's artifact table lists `_shaft(q, request)`; this plan's own artifact table and routes use `_shaft(q)`, and the conflict is a dependency, so `request` is not needed.

**Total deviations:** 0.

## Issues Encountered

None. Ruff's `N818` and `SIM108`, and four `mypy --strict` errors from `**dict[str, object]` calls in the new tests, were fixed before the second commit.

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None beyond the plan's register. T-33-08 (a designation beside a spline field) is mitigated twice and tested for each key; T-33-09 (regex cost) by the codec's 64 code-point cap, tested at the cap and above it; T-33-10 (the shared queue) by the `503 busy` test; T-33-11 (a 500 on an infeasible designation) by `_shaft`'s mapping, tested and fuzzed; T-33-12 (gear contract drift) by `gear.unchanged`, the seam pins and the route-prefix pin.

## Debt and ideas filed

None filed. One observation, not filed as debt because it changes no number and no part: a repeated `designation` key reaches pydantic, which reads the last value (`designation=junk&designation=W 30x2x14x8f` builds the shaft, `...=W 30x2x14x8f&designation=junk` is a 422 at `designation`); the as-written rule checks every value of a repeated key, the designation has no such check. Checked by hand, not pinned by a test; never a 500.

## Next Phase Readiness

- 33-05 imports `SPLINE_KEYS`, `DesignationConflict`, `designation_clash`, `resolve_shaft` and `clash_message` from `shaft_params`; the API's sentences are the CLI's to match.
- 33-06 and 33-07 read `dims` from `/api/shaft/schema` and the numbers from `/api/shaft/info`; the shaft's field metadata (`group`, `unit`, `step`, `enabled_when`) is in the same schema. `refuse()` and `gearQuery()` are untouched (C1): `git diff 6800769 -- src/spur/params.py src/spur/cli.py src/spur/static/app.js` prints nothing.
- 33-08 repeats the browser as-written proof on the shaft's seven number inputs; 33-09 measures ten concurrent heaviest shafts (T-33-10).
- REQ-shaft-api and REQ-designation-input are declared by later plans too, so they stay open until the last declaring plan finishes.

## Self-Check: PASSED

- Created file exists: `tests/test_shaft_interfaces.py`.
- Commits `b50fd9d`, `a6c9442` and `c9e0419` are ancestors of HEAD; `git rev-list --count 1e0e366..HEAD` was 3 (the measured `commits:`).
- `grep -nE '^@app\.get\("/api/shaft/' src/spur/app.py` lists three routes; `grep -c '_serve_model(_shaft(q)'` prints 1; `ShaftParams.model_json_schema()['dims']` has 12 rows; `grep -c 'Provisional until Phase 33' src/spur/shaft_params.py` prints 0.

---
*Phase: 33-interfaces-and-parity*
*Completed: 2026-10-27*
