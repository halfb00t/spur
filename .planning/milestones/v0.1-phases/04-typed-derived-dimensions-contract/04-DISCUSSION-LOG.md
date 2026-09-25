# Phase 4: Typed Derived-Dimensions Contract - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-24
**Phase:** 4-Typed Derived-Dimensions Contract
**Areas discussed:** Wire shape & mate composition, Ratchet scope beyond derive(), Model home/kind/rounding, Proof the contract holds

**Grounding run before the discussion:** `.venv/bin/mypy --disallow-any-explicit src tests docker bench` at `538d26f` → 22 errors in 9 files (16 in `src/`, 4 in `tests/`, 2 in `docker/`). Only `calc.py:163` and `calc.py:256` are the sites the debt file names. Also found: `pyproject.toml:93` cites `2026-09-21-typed-info-contract.md`; the file is `untyped-info-contract.md`. And `root_fillet`/`recess_fillet` are returned unrounded while every other length goes through `r3()`.

---

## Wire shape & mate composition

### Q1 — How faithful must the new JSON be to today's wire shape?

| Option | Description | Selected |
|--------|-------------|----------|
| Flat, mate keys always present | One flat model, every conditional field explicit `X \| None`; `mate_teeth`/`centre_distance` serialise as null when no mate. One OpenAPI schema, no conditional keys. Only visible change: two null keys without a mate. | ✓ |
| Frozen byte-for-byte | Same keys, same absent-vs-null split, same rounding via `exclude_unset` or a `MatedDimensions` subclass. Zero client-visible change; OpenAPI cannot state "present only with a mate". | |
| Nested sub-documents | `recess`, `mate`, `bore` sub-objects. Cleanest types; a wire break for `app.js` `DIMS`, `#centre-distance`, the CLI test, http-api.md and any script parsing `spur info`. | |

**User's choice:** Flat, mate keys always present.
**Notes:** Recorded with a precision the option text glossed: always-present numbers are plain `float`/`int`, not `| None` — only the conditional fields are Optional.

### Q2 — How does the mate get into the model?

| Option | Description | Selected |
|--------|-------------|----------|
| `derive(p, mate_teeth=None)` absorbs it | One entry point, one construction site; `with_mate()` deleted; app/cli/two tests/docs updated. | ✓ |
| Keep `with_mate(dims, p, z2) -> DerivedDimensions` | Narrowest diff; body becomes `model_copy(update=)` with a rebuilt warnings list; a frozen model built partial then copied, validation bypassed. | |

**User's choice:** `derive(p, mate_teeth=None)` absorbs it.

### Q3 — Do DerivedDimensions fields carry OpenAPI metadata or just types?

| Option | Description | Selected |
|--------|-------------|----------|
| Types plus a one-line description and unit | `description` per field, `json_schema_extra={"unit": "mm"}` on lengths — same convention as `GearParams._f`. UI `DIMS` table stays in app.js. | ✓ |
| Bare types only | Names and types only; descriptions could be added later without a wire change. | |

**User's choice:** Types plus description and unit.

---

## Ratchet scope beyond derive()

### Q1 — Does /api/health get a typed response model?

| Option | Description | Selected |
|--------|-------------|----------|
| Typed `HealthReport` with `pool: PoolState \| None` | Same class of thing as the info contract; ~10 lines; OpenAPI documents the pool fields. Caveat: `pool` serialises as null under a bare TestClient unless excluded. | ✓ |
| `dict[str, object]` | Narrowest change; satisfies the rule; `Any` spelled differently for a contract D-13 called one-way. | |

**User's choice:** Typed `HealthReport`.

### Q2 — Rule on for tests/docker/bench too, or a per-module carve-out?

| Option | Description | Selected |
|--------|-------------|----------|
| Global: fix the 6 sites | `object` or the real type; research confirms `GearParams(**kw)` still type-checks or `model_validate(kw)` is used. No second ratchet. | ✓ |
| Carve out `tests.*` / `docker.*` / `bench.*` | `[[tool.mypy.overrides]]` with the rule off; a named exemption in the config. | |

**User's choice:** Global.

### Q3 — Under a bare TestClient, does /api/health emit `"pool": null` or omit the key?

| Option | Description | Selected |
|--------|-------------|----------|
| null, consistent with the info decision | One null-over-absent policy for the whole API; only visible in tests; docstring rewritten. | ✓ |
| Omit, via `response_model_exclude_none` | Byte-identical today; a per-endpoint flag that also hides future None fields; two policies across the API. | |

**User's choice:** null.

---

## Model home, kind & rounding

### Q1 — What kind of object is DerivedDimensions, and where does it live?

| Option | Description | Selected |
|--------|-------------|----------|
| Frozen Pydantic `BaseModel` in `calc.py` | Next to `derive()` like `Profile` next to `profile()`; runtime pydantic import is fine (calc already takes a pydantic `GearParams`); contracts unchanged; validated on construction. | ✓ |
| Frozen `@dataclass` in `calc.py`, Pydantic at the API edge | Keeps calc free of a runtime pydantic import; needs a TypeAdapter/pydantic dataclass for OpenAPI and CLI JSON; two spellings of one contract; roadmap says Pydantic. | |
| `BaseModel` in `params.py` next to `GearParams` | Both wire contracts in one file; turns the lazy `params → calc.check` import into a real cycle. | |

**User's choice:** Frozen `BaseModel` in `calc.py`.

### Q2 — Where does the 3-dp rounding happen, and does it become uniform?

| Option | Description | Selected |
|--------|-------------|----------|
| At construction, uniform across every length | Keep `r3()` in `derive()`; `root_fillet` and `recess_fillet` now rounded too; wire changes only for a capped fillet (1 µm). | ✓ |
| At construction, exactly as today | Two fillets stay unrounded; inconsistency preserved and now visible in a typed model. | |
| In a `field_serializer` | Model holds full precision, JSON rounds on the way out; `derive()` no longer returns the printed numbers. | |

**User's choice:** At construction, uniform.

---

## Proof the contract holds

### Q1 — What proves "the OpenAPI document reflects the typed shape"?

| Option | Description | Selected |
|--------|-------------|----------|
| One test on `/openapi.json` | Assert `/api/info` 200 `$ref`s `DerivedDimensions`, component lists every field, a length carries `unit: mm`; `/api/health` → `HealthReport`. | ✓ |
| Return-annotation inference plus mypy, no test | Nothing at runtime proves the generated document. | |
| Snapshot the whole `openapi.json` | Strongest and brittle. | |

**User's choice:** One test on `/openapi.json`.

### Q2 — What proves "the web UI's existing reads keep working" without a browser?

| Option | Description | Selected |
|--------|-------------|----------|
| Regex belt: app.js `DIMS` keys ⊆ model fields | Same pattern as `test_calc_module_stays_log_free`; `detail[].ctx.fields` already pinned by existing 422 tests. | ✓ |
| Existing API tests only | Cover 5 of the 17 keys the UI reads. | |
| A browser-driven test | Out of scope; a `docs/ideas/` item. | |

**User's choice:** Regex belt.

### Q3 — Is there a CLI-vs-API equivalence test?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes: `spur info` JSON == `/api/info` JSON | With and without a mate; asserts mate keys present-and-null; closes the REQ-three-interfaces acceptance gap as a side effect. | ✓ |
| No: the model is the proof | Equality follows from the type; a serialiser divergence would go unnoticed. | |

**User's choice:** Yes.

---

## Claude's Discretion

- Spelling of each mechanical `Any` removal (`_BlobCache` key, `params._f` generic, `cli` kwargs, `pool` `Callable`, tests' `_field`, `smoke.py` ASGI callables).
- Where `HealthReport`/`PoolState` live (`app.py` expected).
- `/api/schema` annotation — `JsonSchemaValue` vs `dict[str, object]`, whichever FastAPI accepts (research).
- CLI JSON rendering (`model_dump_json` vs `json.dumps(model_dump())`).
- `mate_shift` stays a Python-only kwarg.
- Field order in the model.
- Sequencing of docs / `L21` / debt move against code commits.
- Measure `derive()`'s per-call model-construction cost once and record it.

## Deferred Ideas

- UI reads labels/units from the OpenAPI schema instead of the `DIMS` table.
- Exposing `mate_shift` on the wire.
- Browser-driven UI test (existing `docs/ideas/` item).
- Snapshot-testing `/openapi.json`.
- Frozen dataclass + edge-only Pydantic variant.
