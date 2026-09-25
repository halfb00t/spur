# Phase 4: Typed Derived-Dimensions Contract - Research

**Researched:** 2026-09-24
**Domain:** Python typing (mypy strict + `disallow_any_explicit`) over a Pydantic v2 /
FastAPI response contract
**Confidence:** HIGH — every claim in this document was verified this session by reading
the installed source in `.venv`, running `mypy`/`pytest` against real or scratch files, or
reading the actual repo files cited. No package research was needed (zero new
dependencies); the work is entirely inside the already-installed `fastapi`/`pydantic`/
`mypy` toolchain.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Wire shape and mate composition**
- **D-01:** One **flat** `DerivedDimensions`. Fields that always exist are plain
  (`pitch_d: float`, `span_teeth: int`, `warnings: list[str]`, …); fields that depend on
  the parameters are explicit `X | None` (`bore_effective`, `recess_id`, `recess_od`,
  `recess_fillet`, `web`, `mate_teeth`, `centre_distance`). `mate_teeth` and
  `centre_distance` are **always present**, `null` when no mate was asked for — today
  they are absent. That is the one client-visible change: `/api/info` and `spur info`
  gain two `null` keys without a mate. The UI already reads
  `info.centre_distance != null`; recess/bore fields already serialise as `null`. One
  OpenAPI schema, no conditional keys. Nested sub-documents were rejected (a wire break
  for the 17 keys `app.js`'s `DIMS` table reads flat); byte-for-byte freezing via
  `exclude_unset` was rejected (a conditional-keys contract OpenAPI cannot state
  honestly). — **Reversibility:** one-way — a published response shape read by the UI,
  the CLI's stdout and any script parsing `spur info`; taking the keys away later breaks
  readers that came to depend on them.
- **D-02:** `derive(p, mate_teeth=None, mate_shift=0.0)` absorbs `with_mate()`, which is
  **deleted**. One construction site: the mate fields and the "cannot mesh" warning are
  computed before the model is built, never patched into a frozen object via
  `model_copy(update=)`. Callers to update: `app.info`, `cli.cmd_info`,
  `tests/test_calc.py` (import + `test_impossible_pairs_have_no_centre_distance`), and six
  docs files (listed under canonical refs). `mate_shift` stays a Python-only keyword
  (it is not on `InfoQuery` or the CLI today; exposing it is a new capability).
- **D-03:** Every field carries a one-line `description` and, for lengths,
  `json_schema_extra={"unit": "mm"}` — the same convention `GearParams._f` uses, so
  `/openapi.json` reads like the input schema does. `span_teeth` is a count, `warnings`
  a list; neither gets a unit. The UI's `DIMS` label table stays in `app.js`; making the
  UI consume schema labels is deferred.

**Ratchet scope beyond `derive()`**
- **D-04:** `disallow_any_explicit = true` in the global `[tool.mypy]` block. **No
  per-module override** for `tests.*`/`docker.*`/`bench.*` — a carve-out is a second
  ratchet, the shape this phase retires. The comment block that currently explains why
  the rule is off is replaced (and its stale pointer to
  `2026-09-21-typed-info-contract.md` — the file is `untyped-info-contract.md` — goes
  with it). House rule from here: `Any` is not written in this codebase; a genuinely
  untyped value is `object`, everything else is its real type.
- **D-05:** `/api/health` gets a typed `HealthReport` (`status`, `version`,
  `pool: PoolState | None`) with `PoolState` (`workers`, `queue_available`,
  `workers_replaced`). Same class of thing as the info contract — a published response
  the checker could not see — and Phase 2 D-13 already named it the contract "Phase 4's
  typed OpenAPI work inherits". `dict[str, object]` was rejected as `Any` spelled
  differently. — **Reversibility:** one-way — published contract (Phase 2 D-13); the
  Docker `HEALTHCHECK` and the UI read `status`/`version`, which do not move.
- **D-06:** Under a bare `TestClient` (no lifespan, no pool) `/api/health` emits
  `"pool": null` rather than omitting the key: one null-over-absent policy for the whole
  API (matches D-01). `response_model_exclude_none` was rejected as a per-endpoint
  serialisation flag that would also hide future `None` fields. `health()`'s docstring
  paragraph about absence is rewritten to say `null`. Every real start runs the
  lifespan, so production output is unchanged.
- **D-07:** `/api/schema` gets **no** spur model — a JSON-Schema document is pydantic's
  shape, not ours. Annotate it with pydantic's own `JsonSchemaValue` alias (the `Any`
  inside a library alias is not "explicit" in our code) or `dict[str, object]`;
  **research confirms which one FastAPI accepts as a return annotation** without
  changing the served document.
- **D-08:** The remaining sites are mechanical and are Claude's discretion (below), with
  one research item: `tests/test_calc.py` and `tests/test_model.py` unpack
  `GearParams(**kw)` from `kw: dict[str, Any]`; with `dict[str, object]` mypy may reject
  the `**` unpack, in which case `GearParams.model_validate(kw)` is the fix.

**Model home, kind and rounding**
- **D-09:** `DerivedDimensions` is a **frozen Pydantic `BaseModel` defined in `calc.py`**,
  next to `derive()` the way `Profile` sits next to `profile()`, and **validated on
  construction** (no `model_construct`; a `derive()` bug that yields the wrong type must
  fail). `calc.py` imports pydantic at runtime — it already receives a pydantic
  `GearParams` on every call; the `TYPE_CHECKING` guard exists for the
  `params → calc.check` import cycle, not to avoid pydantic, and stays. The import-linter
  contracts forbid `cadquery`/`OCP`/`logging` from `calc.py`, not pydantic — no contract
  changes. A frozen `@dataclass` with Pydantic only at the API edge was rejected (two
  spellings of one contract; the roadmap says Pydantic model); `params.py` was rejected
  (would turn the lazy `params → calc` import into a real cycle).
- **D-10:** Rounding stays **at construction** via `r3()`, as
  `docs/architecture/gear-maths/tactics.md` documents, and becomes **uniform**: today
  `root_fillet` and `recess_fillet` are returned raw while every other length is rounded
  to 3 dp. Both now go through `r3()`. The wire changes only when a fillet was capped
  (e.g. `0.4123456 → 0.412`); 1 µm, below any tolerance the tool reports against. A
  `field_serializer` was rejected: `derive()` would no longer return the numbers that get
  printed.

**Proof the contract holds (the tests this phase ships)**
- **D-11:** One test on `/openapi.json`: `/api/info`'s `200` response `$ref`s
  `DerivedDimensions`; the component lists every field name; a length field carries
  `unit: mm`; `/api/health` `$ref`s `HealthReport`. Literal names, so a stray
  `response_model=None` or a renamed field fails the gate. No snapshot file.
- **D-12:** A regex belt on the UI, the pattern of
  `tests/test_records.py::test_calc_module_stays_log_free`: read
  `src/spur/static/app.js`, extract the `DIMS` key strings plus `centre_distance` and
  `warnings`, assert each is a `DerivedDimensions` field. `detail[].ctx.fields` is
  already pinned by `test_infeasible_parameters_name_their_fields` and the `422` tests in
  `tests/test_api.py`; nothing in this phase touches `check()` or the `422` path.
- **D-13:** One CLI-vs-API equivalence test: for the same parameters, with and without a
  mate, `json.loads(spur info stdout) == client.get("/api/info").json()`, and without a
  mate both carry `mate_teeth`/`centre_distance` present-and-`null`. Two serialisers
  (`model_dump_json` on the CLI, FastAPI's response path) must agree on floats and
  `None`. Closes the acceptance gap `REQUIREMENTS.md` records for REQ-three-interfaces
  as a side effect.
- Existing tests move from `d["pitch_d"]` to `d.pitch_d`; `test_default_dimensions`'s
  pinned numbers (`13.013`, `25.013`, `0.5`, …) must not move (L05).

**Bookkeeping this phase owes (from CLAUDE.md, not discussed — required)**
- **D-14:** Append **`L21`** to `docs/architecture/decision_log.md`, superseding L14:
  the rule is on, the model and its home (D-09), null-over-absent (D-01/D-06), the
  `object`-not-`Any` house rule (D-04), uniform rounding (D-10). L14's body is not
  edited. — **Reversibility:** one-way — the log is append-only by policy.
- **D-15:** Docs that state the old contract are updated in the same change:
  `docs/architecture/gear-maths/tactics.md` (§Reports list, the `derive(p) -> dict[str,
  Any]` line and its "tracked (L14)" sentence, the `with_mate` line, the rounding
  paragraph), `docs/architecture/gear-maths/implementation.md` (the `derive`/`with_mate`
  table rows), `docs/architecture/gear-maths/strategy.md` and
  `docs/architecture/gear-maths/errors_and_logging.md` (their `with_mate()` mentions),
  `docs/architecture/http-api.md` (endpoint table: `/api/info` → `DerivedDimensions`,
  `/api/health` → `HealthReport`; the D-13 paragraph that anticipates "Phase 4's typed
  OpenAPI work"), `pyproject.toml` (the `[tool.mypy]` comment), `README.md` only if it
  shows `spur info` output.
- **D-16:** Debt-file lifecycle per CLAUDE.md: `Status: resolved`, commit sha recorded,
  `git mv` to `docs/tech_debt/resolved/`, `docs/tech_debt/INDEX.md` row moved — in the
  same commit as the fix.

### Claude's Discretion
Decided by the planner/executor, not by the human — but do not drop them:
- The exact spelling of each mechanical `Any` removal: `_BlobCache`'s key (the real
  `tuple[GearParams, str, str, str]` or a `TypeAlias` next to the cache); `params._f` as
  a `TypeVar`-generic so `teeth: int = _f(19, …)` still type-checks, with `extra` as
  pydantic's `JsonDict`; `cli._add_gear_args`'s `kw` as `dict[str, object]`;
  `pool._run_with_timeout`'s `Callable[..., bytes]` (the only candidate on the flagged
  line — verify) as a concrete signature or `Protocol`; `tests/test_api.py::_field`
  returning `object`; `docker/smoke.py`'s ASGI callables as `MutableMapping[str, object]`.
- Where `HealthReport`/`PoolState` live — `app.py` is the obvious home (web-layer types,
  and the serving process must stay kernel-free, which `app.py` already is).
- Whether `InfoQuery`/`ModelQuery` keep using `Field()` directly (their flagged lines are
  `_f`-style `Any` leaks, not design) once `_f` is generic.
- How the CLI renders JSON (`model_dump_json(indent=2)` vs
  `json.dumps(model_dump(), …)`) — D-13's test settles whichever is chosen.
- Field order in the model (the UI does not depend on it; keep today's key order for
  humans reading `spur info`).
- Sequencing of docs (D-15), `L21` (D-14) and the debt move (D-16) against the code
  commits — CLAUDE.md already fixes that the debt move lands with the fix.
- **Measure, don't estimate:** `derive()` now constructs and validates one model per call
  and the UI calls `/api/info` on every debounced keystroke. Record the per-call cost
  once (µs expected) so the "fast enough to run on every keystroke" docstring stays a
  measured claim.

### Deferred Ideas (OUT OF SCOPE)
- **UI reads labels and units from the OpenAPI schema** instead of the hard-coded `DIMS`
  table — D-03 puts the metadata on the wire; consuming it in `app.js` is a separate
  capability. Revisit when a field is added to `DerivedDimensions` and someone forgets the
  `DIMS` row (D-12's belt only checks the other direction).
- **Exposing `mate_shift` on `/api/info` and `spur info`** — the maths supports it
  (`centre_distance(p, z2, mate_shift)`); the wire does not. New parameter, new
  capability, and a shareable-link field (L05) — its own decision.
- **A browser-driven test for the viewer/form** — existing `docs/ideas/` item; D-12's
  regex belt is the no-browser substitute for this phase.
- **Snapshot-testing `/openapi.json`** (rejected variant of D-11) — revisit only if the
  document gains consumers that need byte stability.
- **Frozen dataclass + edge-only Pydantic** (rejected variant of D-09) — revisit only if
  `calc.py` ever needs to run without pydantic importable, which nothing today asks for.

Not in this phase (per the CONTEXT.md Phase Boundary): any new gear geometry; exposing
`mate_shift` on the wire; a browser-driven UI test; the UI reading labels/units from the
schema; any change to the `warnings` sentences or the `422` `detail[].ctx.fields` shape;
CI observation (Phase 5).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-typed-derived-dimensions | `derive()` returns a `DerivedDimensions` model with explicit optional fields instead of `dict[str, Any]`; `disallow_any_explicit` is turned on in the mypy config and `make verify` passes with it on. | Verified baseline (22 errors / 9 files, line-by-line, reproduced at current HEAD — see "Ratchet Baseline"); verified fix for every one of the 22 lines, including a previously-undocumented pydantic-mypy-plugin interaction that adds *new* errors on every `BaseModel` class using `Field()` (see "Common Pitfalls" — Pitfall 1); verified OpenAPI shape for `X \| None` required-vs-nullable (D-01's "always present, null when absent" rule); verified CLI/API serialiser equivalence (D-13); verified no `DeprecationWarning` under `filterwarnings = error`. |
</phase_requirements>

## Summary

This phase is not really "add a Pydantic model" — that part is mechanical and low-risk
(the codebase already has the pattern: `GearParams`, frozen, validated on construction,
`_f()`'s `json_schema_extra` convention). The actual technical risk, confirmed by direct
experiment this session, is **`disallow_any_explicit` combined with the `pydantic.mypy`
plugin at its default settings (`init_typed = False`) adds a *second*, undocumented
category of error beyond the literal `dict[str, Any]` sites CONTEXT.md's baseline names**:
every `pydantic.BaseModel` subclass that assigns a field via a *recognised*
`pydantic.Field(...)` call (directly, through `Annotated[T, Field(...)]`, or through a
generic pass-through wrapper such as a `TypeVar`-ified `_f()`) gets exactly one
`explicit-any` error attributed to the **class definition line itself** — not to the
`Field()` call, not to a parameter. This is not a hypothetical: it is *already present* in
the verified 22-error baseline (`app.py:201` and `:206`, `InfoQuery`/`ModelQuery`'s own
class lines, caused by their direct `Field()` calls, not by `dict[str, Any]`), and it will
recur on the new `DerivedDimensions`/`HealthReport`/`PoolState` classes the moment they
use `Field(description=..., json_schema_extra=...)` per D-03 — confirmed by building a
scratch class shaped exactly like the planned `DerivedDimensions` and running the
project's own mypy config against it. The one verified, minimal mitigation is a single,
explicitly-commented `# type: ignore[explicit-any]` on each such class's definition line;
it fully suppresses the error with no `warn_unused_ignores` side effect under `strict`.

Every other D-07/D-08 research question CONTEXT.md posed resolved cleanly and in the
codebase's favour: `pydantic.json_schema.JsonSchemaValue` and `dict[str, object]` produce
byte-identical `/api/schema` output through FastAPI and both type-check
(`JsonSchemaValue` is literally `dict[str, Any]` re-exported from pydantic, so annotating
with it does not count as "explicit" in *our* code); `GearParams(**kw)` type-checks fine
against `kw: dict[str, object]` (pydantic's real `__init__` is `**data: Any` at this
project's plugin settings, so the `**`-unpack check never narrows per-field — the
`model_validate()` fallback CONTEXT.md flagged is not needed, though it remains a
reasonable, more-honest alternative); the CLI's `model_dump_json()` and FastAPI's
return-annotation-inferred response path serialise `None` and floats identically;
`X | None` fields declared **without** a `default=` are `required` *and* nullable in the
emitted OpenAPI (exactly D-01's "always present, `null` when absent" contract) while
`Field(default=None, ...)` makes the key optional instead — the model's optional fields
must **not** carry `default=None` if D-01 is to hold; `Callable[..., bytes]` in
`pool.py:153` genuinely is what `disallow_any_explicit` flags (`...` reads as an implicit
`Any`-args signature) and a `Protocol` with `*args: object` does *not* type-check against
the concrete, differently-arity test callables already in `tests/test_pool.py` — a
`ParamSpec` does, cleanly, with zero errors; and `MutableMapping[str, object]` for
`docker/smoke.py`'s ASGI `send`/`receive` breaks `bytearray.extend(message.get("body",
b""))` (an `object`-valued `.get()` is not `Iterable[SupportsIndex]`) and needs one
`cast(bytes, ...)` at that call site, not a blanket type change.

**Primary recommendation:** Build `DerivedDimensions` (and `HealthReport`/`PoolState`)
as plain frozen Pydantic `BaseModel`s with `Field(description=..., json_schema_extra=...)`
and **no `default=`** on the optional fields (every field passed explicitly by
`derive()`/`with_mate()`-successor and `health()`); make `params._f` a `TypeVar`-generic
wrapper as CONTEXT.md's discretion item suggests; and budget exactly one
`# type: ignore[explicit-any]`, with an explanatory comment citing this research, on each
of the five to six class lines (`GearParams` only if `_f` stays non-generic — it will not
need one if `_f` goes generic and its own body's `default`/`extra`/return annotations are
independently retyped; `InfoQuery`, `ModelQuery`, `DerivedDimensions`, `HealthReport`,
`PoolState` — `PoolState` only if it also uses `Field()`, plain type-only fields don't
need it) rather than trying to eliminate the mechanism entirely, which this session found
no way to do while keeping `Field()`'s `description=`/`json_schema_extra=` metadata D-03
requires.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Derived-dimensions typed contract (`DerivedDimensions`) | API / Backend (`calc.py`, pure-Python tier) | — | `calc.py` is explicitly the CAD-kernel-free, logger-free pure-maths tier (import-linter contracts); the model is data, not a kernel or web concern, and D-09 locks its home there next to `derive()`. |
| Health/pool-state typed contract (`HealthReport`/`PoolState`) | API / Backend (`app.py`, serving-process tier) | — | The serving process must stay kernel-free (Phase 2 D-02); these types describe *that* process's own state, not the gear maths, so they belong beside `health()`, not in `calc.py`. |
| mypy ratchet (`disallow_any_explicit`) | Build/Gate tooling (`pyproject.toml [tool.mypy]`) | — | A repo-wide static-analysis policy, not a runtime tier; it constrains every tier uniformly. |
| OpenAPI document shape | API / Backend (FastAPI return-annotation inference) | — | FastAPI derives `/openapi.json` from the endpoint return annotations; no separate schema-authoring tier exists in this app. |
| Web UI reads of the contract (`app.js` `DIMS`, `renderInfo()`) | Browser / Client | — | Unchanged this phase — the UI still reads flat, by-name keys; D-12's belt only proves the *names* stay valid, not a UI rewrite. |
| CLI reads of the contract (`cli.py cmd_info`/`cmd_export`) | CLI process (no server tier) | — | The CLI imports `calc`/`params` directly (import-linter forbids it importing `spur.app`/FastAPI); it renders the same typed model's `model_dump_json()`, not a redundant serialisation path. |

## Standard Stack

No new dependencies. Every library this phase touches is already in `pyproject.toml`.

### Core (already installed, versions verified this session)
| Library | Installed Version | Purpose | Why Standard |
|---------|-------------------|---------|--------------|
| `pydantic` | **2.13.5** [VERIFIED: `.venv/bin/pip show pydantic`, run this session] | The `DerivedDimensions`/`HealthReport`/`PoolState` models; `GearParams` already uses it (L01, L09). | Already the project's one validation/contract layer (L01); `pyproject.toml` pins `pydantic>=2.7`, well below the installed 2.13.5 — no upgrade needed. |
| `fastapi` | **0.141.1** [VERIFIED: `.venv/bin/pip show fastapi`, run this session] | Return-annotation → `response_model` inference for `/api/info`, `/api/health`, `/api/schema`. | Already the project's HTTP layer; `pyproject.toml` pins `fastapi>=0.115`, well below installed — no upgrade needed. |
| `mypy` | **2.3.1** [VERIFIED: `.venv/bin/pip show mypy`, run this session] | The ratchet gate itself (`disallow_any_explicit`). | Already the project's type checker; `pyproject.toml` pins `mypy>=1.18` — the installed 2.3.1 is current. `plugins = ["pydantic.mypy"]` already active. |

### Supporting
None new. `pydantic.json_schema.JsonSchemaValue` and `pydantic.config.JsonDict` are
already shipped inside the installed `pydantic` package (no separate import target).

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `Field(description=..., json_schema_extra=...)` directly on each field | `Annotated[T, Field(...)]` | Verified this session: **produces the exact same class-line ghost `explicit-any` error** (see Pitfall 1) — no advantage for this project, and it is a bigger diff from `GearParams`'s existing convention. Not recommended. |
| `# type: ignore[explicit-any]` on the model class line | `[pydantic-mypy] init_typed = True` plugin option | Verified this session: **does not fix the ghost error** (tested directly against the real `params.py` copy). Also a global plugin-behavior change with wider blast radius (affects every model's synthesized `__init__` typing) for zero measured benefit here — not recommended. |
| `ParamSpec` for `pool._run_with_timeout`'s `func` parameter | `Protocol` with `*args: object` | Verified this session: **the `Protocol` variant does not type-check** against the real, differently-arity callables `tests/test_pool.py` already passes (`build_export(p, fmt, quality)`, `_sleep_past_timeout(seconds)`, `_die()`) — mypy's callable-Protocol structural check requires the concrete function's own parameter list, not a blanket `*args`. `ParamSpec` (`P = ParamSpec("P")`; `func: Callable[P, bytes], *args: P.args, **kwargs: P.kwargs`) type-checks all three cleanly. |
| `MutableMapping[str, object]` uniformly for ASGI `send`/`receive` in `docker/smoke.py` | Leave `Any`, or type each message shape precisely | A precise per-message-type `TypedDict` union is the "correct" ASGI typing but is a much larger diff for a 2-line smoke test; the recommended fix is `MutableMapping[str, object]` **plus one `cast(bytes, message.get("body", b""))`** at the single line that needs a narrower type (`bytearray.extend()`). |

**Installation:** None — no new packages.

**Version verification (already run this session):**
```
$ .venv/bin/pip show fastapi pydantic mypy
Name: fastapi      Version: 0.141.1
Name: pydantic     Version: 2.13.5
Name: mypy         Version: 2.3.1
```

## Package Legitimacy Audit

**Not applicable — this phase installs no new external packages.** Every library used
(`pydantic`, `fastapi`, `mypy`) is already a declared, installed, in-use dependency; no
`npm view`/`pip index versions`/registry check is needed because nothing new is being
added to `pyproject.toml`.

## Architecture Patterns

### System Architecture Diagram

```
                    ┌─────────────────────────────────────────────┐
                    │              calc.py (pure, no I/O)          │
                    │                                               │
 GearParams ───────▶│  profile()/check()/span_measurement()/...    │
 (+ mate_teeth,     │        │                                     │
    mate_shift)     │        ▼                                     │
                    │  derive(p, mate_teeth=None, mate_shift=0.0)  │
                    │        │  computes mate fields + warning     │
                    │        │  BEFORE constructing the model      │
                    │        ▼                                     │
                    │  DerivedDimensions(...)  ◀── frozen, Pydantic│
                    │  (validated on construction; r3() applied    │
                    │   uniformly to every rounded length,         │
                    │   including root_fillet/recess_fillet)       │
                    └────────────────┬──────────────────────────────┘
                                      │  one typed value, three readers
              ┌───────────────────────┼───────────────────────────┐
              ▼                       ▼                           ▼
     app.py `/api/info`      cli.py `cmd_info`/`cmd_export`   (test suite:
     -> DerivedDimensions    -> .model_dump_json()             D-11/D-12/D-13)
     (FastAPI infers the        -> stdout                     openapi.json /
      OpenAPI component                                        app.js DIMS /
      from the return                                          CLI==API equiv.
      annotation; no
      response_model=)
              │
              ▼
     web UI (app.js `renderInfo()`, `DIMS` table) reads the SAME
     flat keys it reads today — unchanged this phase (D-01, D-12)


     Parallel, independent contract (D-05):
     app.py `/api/health` -> HealthReport(status, version, pool: PoolState | None)
     (pool is None only under a bare TestClient with no lifespan; every real
      deployment runs the lifespan and always populates it — D-06: null, not absent)
```

### Recommended Project Structure
No new files. `DerivedDimensions` lives in `src/spur/calc.py` (next to `derive()`,
matching `Profile`/`profile()`); `HealthReport`/`PoolState` live in `src/spur/app.py`
(Claude's Discretion, already the web-layer home per CONTEXT.md).

### Pattern 1: Frozen, validated-on-construction Pydantic model as a pure-function's return type
**What:** `derive()` returns a `DerivedDimensions` `BaseModel` instance instead of a
`dict[str, Any]`; every value is computed first, then passed to the constructor once.
**When to use:** Any function whose output is a JSON-shaped document read by multiple
interfaces (this project's existing `GearParams` already does the input-side half of
this).
**Example (illustrative — combine with Pitfall 1's `# type: ignore[explicit-any]` on the
class line; verified field-required/nullable behavior this session, see D-05 write-up
below):**
```python
# calc.py, next to Profile/profile() -- pattern matches GearParams (params.py)
from pydantic import BaseModel, ConfigDict, Field

class DerivedDimensions(BaseModel):  # type: ignore[explicit-any]
    # pydantic-mypy plugin, at this project's default `init_typed=False`, attributes an
    # "explicit-any" [explicit-any] diagnostic to a BaseModel's own class line whenever
    # any field's default is built through a *recognised* pydantic.Field(...) call --
    # verified this session against InfoQuery/ModelQuery (already in the 22-error
    # baseline, app.py:201/:206) and against a scratch class shaped like this one.
    # dict[str, Any]/Annotated[T, Field(...)]/a TypeVar-generic wrapper all reproduce it
    # identically; init_typed=True does not fix it. One ignore per model class is the
    # only verified mitigation that keeps Field()'s description=/json_schema_extra=.
    model_config = ConfigDict(frozen=True)

    pitch_d: float = Field(description="Pitch diameter.", json_schema_extra={"unit": "mm"})
    span_teeth: int = Field(description="Teeth spanned for the span measurement.")
    warnings: list[str] = Field(description="Warnings about capped or infeasible values.")

    # Optional fields: NO default= -- required-and-nullable in OpenAPI (D-01), see
    # "Common Pitfalls" Pitfall 2 for the verified required-vs-optional distinction.
    bore_effective: float | None = Field(
        description="Effective bore diameter (None with no bore).",
        json_schema_extra={"unit": "mm"})
    mate_teeth: int | None = Field(description="Mating gear teeth (None with no mate).")
    centre_distance: float | None = Field(
        description="Centre distance to the mate, or None if it cannot mesh.",
        json_schema_extra={"unit": "mm"})


def derive(p: GearParams, mate_teeth: int | None = None,
           mate_shift: float = 0.0) -> DerivedDimensions:
    ...  # every value computed first, exactly as today
    return DerivedDimensions(
        pitch_d=r3(2 * pr.r), ..., span_teeth=k,
        bore_effective=r3(2 * bore_radius(p)) if p.bore_d > 0 else None,
        mate_teeth=mate_teeth,
        centre_distance=None if aw is None else r3(aw),
        warnings=warnings,
    )
```

### Pattern 2: `ParamSpec` for a heterogeneous-arity callable crossing an execution boundary
**What:** `pool.py`'s `_run_with_timeout(self, p, func, *args)` is called with callables of
three different arities in production and tests (`build_export(p, fmt, quality)`,
`_sleep_past_timeout(seconds)`, `_die()`). `Callable[..., bytes]` is what
`disallow_any_explicit` flags at `pool.py:153` [VERIFIED: `mypy --disallow-any-explicit`
baseline run this session, and isolated reproduction: a bare `Callable[..., bytes]`
annotation alone triggers `explicit-any`].
**When to use:** Any wrapper that forwards `*args` to an injected callable without
constraining its own arity.
**Example (verified this session — type-checks with zero errors against all three real
call shapes; the `Protocol`-with-`*args: object` alternative does NOT type-check against
these same three calls):**
```python
from typing import ParamSpec
from collections.abc import Callable

P = ParamSpec("P")

async def _run_with_timeout(
    self, p: GearParams, func: Callable[P, bytes], *args: P.args, **kwargs: P.kwargs,
) -> bytes:
    ...
    future = loop.run_in_executor(executor, func, *args)  # positional-only, unaffected
    ...
```

### Anti-Patterns to Avoid
- **`Field(default=None, ...)` on an "always present, null when absent" field:** verified
  this session — it makes the OpenAPI key **optional**, not required-and-nullable,
  contradicting D-01's explicit contract for `mate_teeth`/`centre_distance`/the recess and
  bore fields. Omit `default=` entirely; pass every field explicitly at every
  `DerivedDimensions(...)` call site (which D-09's "validated on construction, no
  `model_construct`" rule already requires).
- **`MutableMapping[str, Any]` → `MutableMapping[str, object]` as a blind find-replace in
  `docker/smoke.py`:** breaks `bytearray.extend(message.get("body", b""))` (verified this
  session: `object` is not `Iterable[SupportsIndex]`). Needs one `cast(bytes, ...)` at
  that specific call, not a wider type.
- **Trying to eliminate the class-line ghost `explicit-any` by restructuring the field
  definition (`Annotated[...]`, `cast()` around `Field()`, constrained `TypeVar`s):** all
  four variants tried this session still produce the error. Stop at the
  `# type: ignore[explicit-any]` mitigation rather than spending further effort chasing a
  structural fix that does not exist at this pydantic/mypy version pair.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON-Schema-shaped return type for `/api/schema` | A custom `TypedDict`/model mirroring `GearParams.model_json_schema()`'s shape | `pydantic.json_schema.JsonSchemaValue` (verified this session: `JsonSchemaValue = dict[str, Any]`, re-exported by pydantic itself — using it as a return annotation is not "explicit" `Any` in *our* code, and it is byte-identical to `dict[str, object]` through FastAPI's `TestClient`) | pydantic already publishes the correct type for "a JSON Schema document"; inventing a parallel one adds a second thing that can drift from what `model_json_schema()` actually returns. |
| Heterogeneous-arity callable forwarding (`pool.py`) | A custom `Protocol`, a manual `*args: Any` escape hatch, or per-call-site overloads of `_run_with_timeout` | `ParamSpec` (`Callable[P, bytes]`, `*args: P.args`) | Verified: `ParamSpec` is the stdlib-correct tool for exactly this shape and type-checks cleanly against every real caller in the test suite; a hand-rolled `Protocol` demonstrably does not. |

**Key insight:** Nothing in this phase needs a new abstraction. Every one of the 22
baseline errors has either a direct, already-typed replacement in the standard library
(`ParamSpec`, `cast`, `TypeVar`) or a documented pydantic export (`JsonSchemaValue`,
`JsonDict`). The one genuinely new thing this phase needs to *know*, not build, is the
class-line ghost-error mitigation (Pitfall 1).

## Ratchet Baseline (Verified This Session)

```
$ .venv/bin/mypy --disallow-any-explicit src tests docker bench
```
run against the current tree (`state_head: 538d26f...`, current HEAD at research time) —
**exit code 1, `Found 22 errors in 9 files (checked 23 source files)`**, confirming
CONTEXT.md's cited number. Exact lines (CONTEXT.md's prose says "app.py ×10"; the verified
per-file breakdown below sums to 9 for `app.py`, and 2+3+1+2+1+1+9+2+1 = **22**, matching
the total — the prose miscounts by one, the total is correct):

| File | Lines | What's there | Planned fix |
|------|-------|---------------|-------------|
| `src/spur/calc.py` | 163, 256 | `derive()` / `with_mate()` return `dict[str, Any]` | `derive()` returns `DerivedDimensions`; `with_mate()` deleted (D-02) |
| `src/spur/params.py` | 16, 18, 25 | `_f()`'s `default: Any`, `extra: dict[str, Any]`, `-> Any` | `_f` generic (`TypeVar`); see Pitfall 1 for the tradeoff this introduces |
| `src/spur/pool.py` | 153 | `func: Callable[..., bytes]` | `ParamSpec` (Pattern 2, verified) |
| `src/spur/cli.py` | 25 | `kw: dict[str, Any]` in `_add_gear_args` | `dict[str, object]` (mechanical; `argparse` `dest=`/`default=`/`help=`/`type=`/`choices=` values are heterogeneous by nature, verify each assignment individually) |
| `src/spur/app.py` | 57, 60, 66 | `_BlobCache`'s `Any` key (3×) | `tuple[GearParams, str, str, str]` (verified against the real call site: `key = (params, fmt, q.quality, encoding)`) |
| `src/spur/app.py` | 201, 206 | `InfoQuery`/`ModelQuery` class lines — **already the Pitfall 1 ghost error**, not a `dict[str, Any]` leak | `# type: ignore[explicit-any]` on each class line |
| `src/spur/app.py` | 272, 303 | `health() -> dict[str, Any]` / `payload: dict[str, Any]` | `-> HealthReport`, construct `HealthReport(status=..., version=..., pool=...)` |
| `src/spur/app.py` | 314 | `schema() -> dict[str, Any]` | `-> JsonSchemaValue` (verified byte-identical output; see D-07 below) |
| `src/spur/app.py` | 319 | `info(...) -> dict[str, Any]` | `-> DerivedDimensions` |
| `docker/smoke.py` | 26, 29 | ASGI `receive`/`send`'s `MutableMapping[str, Any]` | `MutableMapping[str, object]` + one `cast(bytes, ...)` (Anti-Pattern above) |
| `tests/test_calc.py` | 79, 137 | `kw: dict[str, Any]` parametrize, unpacked into `GearParams(**kw)` | `dict[str, object]` — verified `GearParams(**kw)` type-checks fine against it (D-08, below) |
| `tests/test_model.py` | 28 | same pattern | same fix |
| `tests/test_api.py` | 327 | `_field(...) -> Any` (reads a dynamic `LogRecord` attribute) | `-> object` (Claude's Discretion item, already named) |

**New errors this phase's own additions are expected to introduce, budgeted above:**
`DerivedDimensions`, `HealthReport` (and `PoolState` if it uses `Field()`) each need their
own `# type: ignore[explicit-any]` on the class line — these are *not* reductions of the
22, they are the unavoidable cost of the new typed models under this plugin/mypy pairing,
verified this session against a scratch class shaped exactly like the planned
`DerivedDimensions`.

## Common Pitfalls

### Pitfall 1: `pydantic.mypy` + `disallow_any_explicit` flags the *class line*, not the `Field()` call
**What goes wrong:** Any `pydantic.BaseModel` subclass with at least one field assigned
via a call that mypy's `pydantic.mypy` plugin recognises as (or traces back to)
`pydantic.fields.Field(...)` gets exactly one `error: Explicit "Any" is not allowed
[explicit-any]` attributed to the **`class Foo(BaseModel):` line itself** — not to the
field, not to the `Field()` call's arguments.
**Why it happens:** `pydantic.Field`'s installed stub has two overloads; the one that
matches a literal default value (`Field(19, ...)`) types its `default` parameter as
`Any`. At this project's plugin settings (`plugins = ["pydantic.mypy"]`, no
`[pydantic-mypy]` section, so `init_typed` defaults to `False`), the plugin's synthesized
per-model field-type extraction surfaces that `Any` as a diagnostic tied to the class
definition. Verified this session across five isolated repros plus the project's own
pre-existing code:
- A bare `Field()` call directly in a model body → ghost error on the class line.
- The same call routed through a **non-generic** wrapper (`_f()` returning `Any`, exactly
  today's shape) → **no** ghost error — only `_f()`'s own explicit `Any` annotations are
  flagged (3 errors, all inside `_f`, none on `GearParams`'s class line — matches the
  verified baseline exactly).
- The same call routed through a **generic** (`TypeVar`) wrapper → ghost error
  **reappears** on the class line, regardless of whether the wrapper's `extra`/
  `json_schema_extra` argument is typed `dict[str, Any]`, `JsonDict`, or built as an
  inline dict literal with no annotation at all — the trigger is the wrapper's
  *genericity*, not the extra dict's type.
- `Annotated[T, Field(...)]` instead of `field: T = Field(...)` → same ghost error.
- `[pydantic-mypy] init_typed = True` → does **not** suppress it (tested directly).
- The project's own `InfoQuery`/`ModelQuery` (`app.py:201`/`:206`) already exhibit this —
  their flagged lines are their class definitions, caused by their direct `Field()` calls
  for `mate_teeth`/`quality`, not by any `dict[str, Any]`.
**How to avoid:** Budget one explicitly-commented `# type: ignore[explicit-any]` per
affected class line (verified: fully suppresses the error, no `warn_unused_ignores`
complaint under `strict`). Do not spend further time chasing a structural fix — none of
the four alternatives tried this session worked.
**Warning signs:** A "found N errors" count that doesn't match a line-by-line tally of
literal `Any`/`dict[str, Any]` sites in the diff — the gap is class-line ghost errors on
every new or touched `BaseModel`.

### Pitfall 2: `Field(default=None, ...)` silently changes a field from required-nullable to optional in OpenAPI
**What goes wrong:** D-01 requires `mate_teeth`/`centre_distance` (and the recess/bore
fields) to be **always present, `null` when absent** in the wire document. Declaring the
field as `x: T | None = Field(default=None, description=...)` does **not** produce that
shape.
**Why it happens:** Verified this session with a live FastAPI app + `TestClient` reading
`/openapi.json`: a field typed `T | None` **without** a `default=` argument to `Field()`
appears in the schema's `required` array *and* its `anyOf` includes `{"type": "null"}` —
exactly "required, nullable". The same field declared **with** `default=None` is
**absent** from `required` — a client-facing consumer (or a strict schema validator) may
treat it as omittable, which is not what D-01 promises. (Whether the *actual* JSON key is
emitted depends on the Python object always carrying a value at construction time — which
D-09's "validated on construction, every field passed" already guarantees — but the
*documented contract* in `/openapi.json` differs, and D-11's test reads the schema, not
just a live response.)
**How to avoid:** Every optional (`X | None`) field on `DerivedDimensions`/`HealthReport`/
`PoolState` should be declared **without** `default=` — the constructor call always
supplies a value (`None` or real), matching D-09's "no `model_construct`" rule anyway.
**Warning signs:** D-11's `/openapi.json` test failing on the `required` list even though
a manual `curl`/`TestClient` request looks correct — the two are genuinely different
checks.

### Pitfall 3: `dict[str, object]` breaks anywhere a `.get()`/indexed value flows into a narrower-typed stdlib call
**What goes wrong:** Widening an `Any`-typed `Mapping`/`dict` to `dict[str, object]` is
usually safe, but any downstream consumer that assumes a specific value type (e.g.
`bytearray.extend(message.get("body", b""))` in `docker/smoke.py`, which needs
`Iterable[SupportsIndex]`, not `object`) breaks.
**Why it happens:** `object` erases the value type entirely; anything more specific than
"exists" needs a narrowing step (`cast`, `isinstance`, or a `TypedDict`).
**How to avoid:** Fix the specific call site with a targeted `cast(bytes, ...)` (verified
this session) rather than reaching for a broader type change.
**Warning signs:** A `disallow_any_explicit` fix that trades one mypy error for a
different one (`arg-type` instead of `explicit-any`) at the same or a nearby line.

### Pitfall 4: `dict[str, object]` is *not* assignable to pydantic's `JsonDict`
**What goes wrong:** If `_f()`'s `extra` variable is typed `dict[str, object]` and passed
to `Field(json_schema_extra=extra)`, mypy raises `error: Argument "json_schema_extra" to
"Field" has incompatible type "dict[str, object]"; expected "JsonDict |
Callable[[JsonDict], None] | None"  [arg-type]` — verified this session.
**Why it happens:** `dict` is invariant in its value type; pydantic's `JsonDict` is
`dict[str, JsonValue]` (a recursive alias of `int | float | str | bool | None | list[...]
| dict[...]`), and `object` is not `JsonValue`.
**How to avoid:** Either keep the extra dict genuinely untyped-but-not-`Any` (an inline
dict literal with no separate variable annotation type-checks fine against `Field`'s
`JsonDict` parameter, since inference — not an explicit annotation — produces its type,
and inferred types are not what `disallow_any_explicit` flags), or annotate it `JsonDict`
directly (also verified to type-check against `Field`, and does **not** itself add a new
explicit-Any error beyond the usual Pitfall 1 class-line ghost).
**Warning signs:** Fixing one `explicit-any` on `extra`'s annotation produces a fresh
`arg-type` error on the `Field(...)` call it feeds.

## Code Examples

### `/api/schema`'s return annotation (D-07, resolved)
```python
# Source: verified this session — pydantic/json_schema.py:76 defines
# `JsonSchemaValue = dict[str, Any]`; import from pydantic.json_schema, NOT top-level
# `pydantic` (pydantic does not re-export the name at the package root, confirmed by
# ImportError this session).
from pydantic.json_schema import JsonSchemaValue

@app.get("/api/schema")
def schema() -> JsonSchemaValue:
    return GearParams.model_json_schema()
```
Verified this session with a live `TestClient`: this annotation and
`dict[str, object]` both produce byte-identical `/api/schema` responses (3233 bytes,
identical `json.loads()` output), and both type-check cleanly under
`--strict --disallow-any-explicit` with the project's `pydantic.mypy` plugin config.
`JsonSchemaValue` is preferred because it documents intent ("this is a JSON Schema
document") rather than an arbitrary object-valued dict.

### `_f()` as a generic wrapper (D-08/Claude's Discretion, with the Pitfall 1 cost noted)
```python
# params.py -- verified this session: teeth: int = _f(19, ...) still resolves to
# `reveal_type(...) -> "int"` under mypy with this signature.
from typing import TypeVar

T = TypeVar("T")

def _f(default: T, ge: float, le: float, *, title: str, group: str,
       unit: str = "", step: float | None = None, help: str = "") -> T:
    extra: JsonDict = {"group": group, "unit": unit}
    if step is not None:
        extra["step"] = step
    return Field(default, ge=ge, le=le, title=title, description=help,
                 json_schema_extra=extra)
```
Net effect on `params.py`'s own 3 baseline errors: reduces to 1 (`extra: JsonDict` no
longer flags — only if annotated `JsonDict`, not `dict[str, Any]`) **plus one new
class-line ghost error on `GearParams`** (Pitfall 1) — a net improvement (3 → 2), not a
full elimination. Route the residual through `# type: ignore[explicit-any]` on
`class GearParams(BaseModel):`.

### `GearParams(**kw)` against `kw: dict[str, object]` (D-08, resolved — no `model_validate()` needed)
```python
# Verified this session: mypy --strict --disallow-any-explicit reports
# "Success: no issues found" for this exact pattern.
def f(kw: dict[str, object]) -> GearParams:
    return GearParams(**kw)
```
Root cause (verified via `inspect.signature(GearParams.__init__)` at runtime →
`(self, /, **data: 'Any') -> 'None'`): at this project's plugin settings
(`init_typed=False`, the default, not overridden in `pyproject.toml`), pydantic's
generated `__init__` accepts `**data: Any` regardless of the model's field types, so
mypy's `**`-unpack check against it never narrows per-field — `dict[str, object]`
unpacks into it exactly as freely as `dict[str, Any]` did. This means switching
`tests/test_calc.py`/`tests/test_model.py`'s `kw: dict[str, Any]` to `dict[str, object]`
is a pure, safe mechanical rename; `GearParams.model_validate(kw)` also type-checks
(confirmed) and is a defensible, more-explicit alternative, but is not *required* by
mypy the way CONTEXT.md's research item speculated it might be.

## State of the Art

Not applicable in the usual "library X was replaced by Y" sense — this is a first-party
contract change inside an already-current stack. The one relevant "current approach" note:
`pydantic.mypy`'s default `init_typed = False` (verified against the installed 2.13.5) is
the setting responsible for both the *good* news (non-generic `_f()`/`GearParams(**kw)`
avoid extra errors today) and the *bad* news (Pitfall 1). Changing that plugin default is
out of scope for this phase (a global behavior change with unverified wider effects) but
is worth a `docs/ideas/` note if the ghost-error tax ever grows past a handful of classes.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Both `InfoQuery` and `ModelQuery` will continue using direct `Field()` calls (not routed through `_f()`) — CONTEXT.md leaves this Claude's Discretion, and this research assumes they stay as-is, each needing their own `# type: ignore[explicit-any]`. | Ratchet Baseline table; Pitfall 1 | Low — if the executor instead routes them through a generic `_f()`, the same ghost error recurs on their class lines regardless (verified: genericity, not directness, is the trigger), so the mitigation is the same either way. |
| A2 | `PoolState` will use `Field(description=...)` per the same convention as `HealthReport`/`DerivedDimensions`, and therefore also needs a `# type: ignore[explicit-any]` on its own class line. | Ratchet Baseline table; Pattern 1 | Low — if `PoolState`'s three `int`/`bool`-ish fields (`workers`, `queue_available`, `workers_replaced`) are declared as plain typed attributes with no `Field()` call at all (no `description=` required by D-03 for a nested pool sub-object, since D-03's wording is about `DerivedDimensions`' own fields), no ghost error appears — this needs a one-line confirmation from the executor when writing the class, not a research gap. |
| A3 | The measured ~1.7 µs/call proxy-model construction cost (20-field frozen `BaseModel`, synthetic values, this machine) is representative enough to ground the "fast enough for every keystroke" claim CONTEXT.md's discretion item asks to measure. | Performance note below | Low — it is a *proxy*, not the real `DerivedDimensions`; the executor must re-run the measurement against the actual class before writing it into a docstring, per CLAUDE.md's "claims about performance are measured, not estimated." |

**If this table is empty:** N/A — see above. Every load-bearing technical claim in this
document (the ratchet baseline, the OpenAPI required/optional distinction, the serialiser
equivalence, the `ParamSpec`/`Protocol` result, the `Callable[..., bytes]` flag site, the
`JsonSchemaValue`/`dict[str, object]` byte-identity, the `GearParams(**kw)` type-check
result, and all four Pitfall 1 variants) was verified by running a real command or reading
a real file this session, not assumed from training knowledge.

## Open Questions

1. **Does `HealthReport`/`PoolState` need `ConfigDict(frozen=True)`?**
   - What we know: D-09 mandates it for `DerivedDimensions`; D-05 does not explicitly say
     so for `HealthReport`/`PoolState`, and CONTEXT.md's Claude's Discretion list only
     settles *where* they live, not their `ConfigDict`.
   - What's unclear: whether frozen-ness matters for a response object that is
     constructed once per request and never mutated (functionally, `frozen=True` is a
     no-op safety net here, not load-bearing).
   - Recommendation: match `GearParams`/`DerivedDimensions`'s convention (frozen) for
     consistency — cheap, and keeps "every pydantic model in this codebase is frozen" as
     a single easy-to-state house rule. Not a blocking decision either way.

2. **Should `params._f` go generic at all, given the net error reduction is only 3→2?**
   - What we know: CONTEXT.md's Claude's Discretion explicitly suggests making `_f`
     generic; this research confirms it works but introduces the Pitfall 1 ghost error on
     `GearParams`'s own class line, netting only a 1-error improvement over leaving `_f`
     non-generic (which needs zero `# type: ignore` on `GearParams` itself, since the
     ghost only appears when the wrapper is generic).
   - What's unclear: whether the value of `_f(19, ...)` type-checking as `int` (rather
     than `Any`, with assignment compatibility unchecked) at every one of `GearParams`'s
     24 call sites is worth the one `# type: ignore[explicit-any]` it costs.
   - Recommendation: go generic anyway — CONTEXT.md's own house rule ("`Any` is not
     written in this codebase") is about *literal* `Any` in source, and a `TypeVar`
     genuinely eliminates that from `_f`'s own signature; the one remaining `# type:
     ignore` is a documented, verified, narrowly-scoped exception, not a re-introduction
     of `Any`.

## Environment Availability

Not applicable — this phase has no external service/tool dependencies beyond the already-
verified `.venv` (Python 3.12.13, `fastapi` 0.141.1, `pydantic` 2.13.5, `mypy` 2.3.1). No
Docker, database, or network dependency is touched.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 [VERIFIED: `pytest --version` output in `make verify` run this session], config in `pyproject.toml [tool.pytest.ini_options]`, `filterwarnings = ["error", "ignore::DeprecationWarning:starlette.*", "ignore:Using \`httpx\`"]` |
| Config file | `pyproject.toml` (no separate `pytest.ini`/`conftest.py` root config beyond fixtures) |
| Quick run command | `make test PYTEST_ARGS="tests/test_calc.py -q"` (per-file, the form Phase 3 used) |
| Full suite command | `make verify` (ruff + mypy strict + import-linter + no-fake-done + pytest) |
| Measured runtime | `make verify`: **41.8s wall** this session (99 tests, `pytest` alone 30.3s) — slower than L13's cited "~11s warm"; likely machine/load difference, not a regression signal. Record the executor's own measurement rather than trusting either number blindly. |

### Phase Requirements → Test Map
| Req ID (acceptance clause) | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-typed-derived-dimensions: `derive()` returns typed model | `DerivedDimensions` constructed, fields match today's dict keys | unit | `make test PYTEST_ARGS="tests/test_calc.py -q"` | ✅ existing (`test_default_dimensions` and friends move from `d["x"]` to `d.x`) |
| REQ-typed-derived-dimensions: ratchet on, `make verify` green | `mypy --strict` (with `disallow_any_explicit=true`) passes over `src tests docker bench` | static/type | `make typecheck` (or `.venv/bin/mypy src tests docker bench` directly) | ✅ existing target, new config value |
| REQ-typed-derived-dimensions: OpenAPI reflects the typed shape (D-11) | `/api/info`'s `200` response `$ref`s `DerivedDimensions`; component lists every field; a length field carries `unit: mm`; `/api/health` `$ref`s `HealthReport` | integration | `make test PYTEST_ARGS="tests/test_api.py -q -k openapi"` (new test, name TBD by planner) | ❌ Wave 0 — new test, pattern: read `client.get("/openapi.json").json()`, assert on `components.schemas.DerivedDimensions`/`HealthReport`, verified this session that FastAPI populates these from return-annotation inference alone (no `response_model=` needed) |
| REQ-typed-derived-dimensions: UI reads keep working (D-12) | `app.js`'s `DIMS` keys + `centre_distance`/`warnings` are all real `DerivedDimensions` field names | unit (regex belt, no browser) | `make test PYTEST_ARGS="tests/test_records.py -q -k app_js"` or a new test module — pattern from `tests/test_records.py::test_calc_module_stays_log_free` | ❌ Wave 0 — new test; the 15 keys are enumerated in the CONTEXT.md `<specifics>` section (verified against the live `app.js` this session: `pitch_d`, `tip_d`, `caliper_over_tips`, `span`, `root_d`, `base_d`, `tip_thickness`, `root_thickness`, `root_gap`, `root_fillet`, `bore_effective`, `recess_id`, `recess_od`, `recess_fillet`, `web`, plus `span_teeth`/`centre_distance`/`warnings` read outside the `DIMS` table) |
| REQ-typed-derived-dimensions: three interfaces agree (D-13) | CLI `spur info` stdout `json.loads()` equals `client.get("/api/info").json()`, with and without a mate; both carry `mate_teeth`/`centre_distance` present-and-`null` without one | integration | `make test PYTEST_ARGS="tests/test_cli.py -q -k equivalence"` (new test — needs both a CLI subprocess/import path and a `TestClient`, pattern similar to existing `tests/test_cli.py::test_info_reports_the_mate_it_was_asked_about`) | ❌ Wave 0 — new test; serialiser equivalence (`model_dump_json()` vs FastAPI's response path) independently verified this session at the Python level |
| Existing coverage that must not regress | `test_default_dimensions`'s pinned numbers (`33.25`, `36.75`, `28.875`, `3.5`, `13.013`, `25.013`, `0.5`, plus the `base_d` formula) | unit | `make test PYTEST_ARGS="tests/test_calc.py -q -k default_dimensions"` | ✅ existing, verified this session by reading the exact assertions in `tests/test_calc.py:20-32` |

### Sampling Rate
- **Per task commit:** `make test PYTEST_ARGS="<touched test file> -q"` (fast, file-scoped)
- **Per wave merge:** `make verify` (full gate: lint, typecheck with the new ratchet,
  import-linter, no-fake-done, full pytest)
- **Phase gate:** `make verify` green, with `disallow_any_explicit = true` actually present
  in `pyproject.toml` (not just passing because the flag was only passed on the CLI during
  research) — verify `make typecheck` (which reads `pyproject.toml`, not a CLI flag) is
  what's green, not a hand-run `mypy --disallow-any-explicit` invocation.

### Wave 0 Gaps
- [ ] An `/openapi.json` structural test (D-11) — new, no existing file covers this; add
      to `tests/test_api.py` (module already imports `client = TestClient(app)`).
- [ ] An `app.js` `DIMS`-vs-`DerivedDimensions` regex belt (D-12) — new; either extend
      `tests/test_records.py` (which already has the `test_calc_module_stays_log_free`
      regex pattern to copy) or a new `tests/test_static.py`.
- [ ] A CLI-vs-API equivalence test (D-13) — new; extend `tests/test_cli.py`, which
      already has `test_info_reports_the_mate_it_was_asked_about` as a close analogue.
- No framework/config gap: pytest, `TestClient`, and the CLI's own subprocess/import
  pattern are all already in place and exercised by the existing 99 passing tests.

## Security Domain

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | Out of scope (`REQ-no-auth-default`, unrelated to this phase) |
| V3 Session Management | No | No sessions in this app |
| V4 Access Control | No | Unrelated to this phase |
| V5 Input Validation | Yes, unchanged | `GearParams`'s existing Pydantic validation (`ge=`/`le=`, `model_validator`) remains the single input-validation boundary; this phase only changes the **output** contract, not input handling. No new validation surface is introduced. |
| V6 Cryptography | No | Not touched |

### Known Threat Patterns for this stack
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Response-shape drift silently breaking a client (renamed/dropped key with no static check) | Tampering/Information Disclosure (a consumer trusting an undocumented shape) | This is precisely what REQ-typed-derived-dimensions retires — a typed, OpenAPI-documented, test-proven (D-11/D-12/D-13) response contract replaces an untyped `dict[str, Any]` that could silently change shape. No new threat surface is introduced; an existing one (an unchecked output contract) is closed. |
| `# type: ignore[explicit-any]` used to silence a *real* type hole rather than a documented plugin quirk | Tampering (a genuine `Any` leak masquerading as "this is fine") | Every `# type: ignore[explicit-any]` this phase adds must carry the explanatory comment pattern shown in "Pattern 1" above, citing this research — an undocumented or blanket ignore would be indistinguishable from a real regression at future review. |

## Sources

### Primary (HIGH confidence — verified this session by running a command or reading an installed/repo file)
- `.venv/bin/pip show fastapi pydantic mypy` — installed versions (fastapi 0.141.1, pydantic 2.13.5, mypy 2.3.1).
- `.venv/bin/mypy --disallow-any-explicit src tests docker bench` — the verified 22-error/9-file baseline, run against current HEAD.
- `.venv/lib/python3.12/site-packages/pydantic/json_schema.py:76` — `JsonSchemaValue = dict[str, Any]`.
- `.venv/lib/python3.12/site-packages/pydantic/config.py:23-24` — `JsonValue`/`JsonDict` alias definitions.
- `.venv/lib/python3.12/site-packages/pydantic/fields.py:925-970` — `Field()`'s two overloads, `default: ellipsis` / `default: Any`, and `json_schema_extra: JsonDict | Callable[[JsonDict], None] | None`.
- `.venv/lib/python3.12/site-packages/pydantic/mypy.py:219-233` — `init_typed`/`init_forbid_extra` plugin settings, both default `False`.
- `inspect.signature(GearParams.__init__)` at runtime — `(self, /, **data: 'Any') -> 'None'`, confirming why `GearParams(**kw)` type-checks against `dict[str, object]`.
- Live `TestClient`/`FastAPI` app scratch scripts (this session, in the scratchpad directory) — `/api/schema` byte-identity for `JsonSchemaValue` vs `dict[str, object]`; `/openapi.json` required-vs-optional behavior for `X | None` fields with/without `default=None`; CLI-vs-API serialiser equivalence; no `DeprecationWarning` under `warnings.simplefilter("error")`.
- `src/spur/calc.py`, `src/spur/app.py`, `src/spur/params.py`, `src/spur/pool.py`, `src/spur/cli.py`, `src/spur/static/app.js`, `tests/test_calc.py`, `tests/test_model.py`, `tests/test_api.py`, `tests/test_pool.py`, `docker/smoke.py`, `pyproject.toml`, `docs/architecture/decision_log.md`, `docs/tech_debt/active/2026-09-21-untyped-info-contract.md` — all read directly this session for exact line numbers and current behavior.
- `make verify` — run to completion this session (99 passed, 41.8s wall).

### Secondary (MEDIUM confidence)
None — every claim in this document reached HIGH confidence via direct verification;
no web search was needed (this is entirely a first-party codebase + installed-library
investigation).

### Tertiary (LOW confidence)
None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies; versions read directly from `pip show`.
- Architecture (model placement, OpenAPI shape, serialiser equivalence): HIGH — every
  claim reproduced with a live FastAPI `TestClient` or `mypy` run this session.
- Pitfalls (especially Pitfall 1, the class-line ghost error): HIGH — reproduced from five
  independent angles (direct `Field()`, `Annotated[T, Field()]`, generic wrapper with
  three different `extra` typings, `init_typed=True`, and the project's own pre-existing
  `InfoQuery`/`ModelQuery` baseline errors), with a verified, minimal mitigation.

**Research date:** 2026-09-24
**Valid until:** Tied to the installed `fastapi`/`pydantic`/`mypy` versions above; if any
of the three is upgraded before this phase is planned/executed, re-run the baseline
`mypy --disallow-any-explicit` command and the Pitfall 1 scratch reproduction before
trusting this document's line numbers and error counts.
