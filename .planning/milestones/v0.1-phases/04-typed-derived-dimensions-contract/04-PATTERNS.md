# Phase 4: Typed Derived-Dimensions Contract - Pattern Map

**Mapped:** 2026-09-24
**Files analyzed:** 13 (all modified — this phase creates no new files, per RESEARCH.md
"Recommended Project Structure": `DerivedDimensions` lives inside `calc.py`,
`HealthReport`/`PoolState` inside `app.py`)
**Analogs found:** 13 / 13 (every file's closest analog is itself, at an earlier commit
shape, or a sibling file in the same module — this is a same-repo typing-contract
retrofit, not new-surface work)

## File Classification

| Modified File | Role | Data Flow | Closest Analog | Match Quality |
|----------------|------|-----------|-----------------|----------------|
| `src/spur/calc.py` (`DerivedDimensions` model + `derive()` signature) | model (pure-domain value object) | transform (params → typed dimensions) | `src/spur/params.py::GearParams` (frozen `BaseModel`, `ConfigDict(frozen=True)`) | exact — same file family, same `_f()`/`Field()` metadata convention, same "frozen, validated on construction" contract |
| `src/spur/calc.py` (`derive()`/`with_mate()` merge, D-02) | transform / service function | request-response (single construction site) | `src/spur/calc.py::profile()` → `Profile` (compute-then-construct, `Profile` sits next to `profile()`) | exact — same file, same "compute every value, then build the frozen value object once" shape |
| `src/spur/app.py` (`HealthReport`/`PoolState` models) | model (web-layer response contract) | request-response | `src/spur/app.py::InfoQuery`/`ModelQuery` (`GearParams` subclasses with `Field()`) | role-match — same file, same `Field(description=...)` convention, but `HealthReport`/`PoolState` are plain `BaseModel`s, not `GearParams` subclasses |
| `src/spur/app.py` (`_BlobCache` key typing) | utility (cache) | CRUD (LRU get/put) | `src/spur/app.py` itself, `_BlobCache.get`/`.put` (60–75) — no external analog needed, this is a pure `Any`→concrete-type narrowing | exact |
| `src/spur/app.py` (`health()`) | route/controller | request-response | `src/spur/app.py::info()` (post-fix shape) / itself pre-fix | exact — same file, same "compute payload dict, return it" → "construct typed model, return it" shape |
| `src/spur/app.py` (`schema()`) | route/controller | request-response | `src/spur/app.py::health()`/`info()` (sibling routes in the same file) | role-match — different return convention (D-07: library alias, not a spur model) |
| `src/spur/app.py` (`info()`) | route/controller | request-response | `src/spur/app.py::model()` (322+, the sibling `/api/model.{fmt}` route already returning a typed `Response`) | exact |
| `src/spur/params.py` (`_f()` → generic) | utility (Field-builder wrapper) | transform | itself, pre-fix — a `TypeVar`-generic rewrite of the same function, same call sites (`teeth: int = _f(19, ...)`) | exact |
| `src/spur/pool.py` (`_run_with_timeout`) | service (async worker-pool boundary) | request-response (bounded by timeout) | itself, pre-fix — `Callable[..., bytes]` → `ParamSpec` on the same signature | exact |
| `src/spur/cli.py` (`_add_gear_args`, `cmd_info`, `cmd_export`) | CLI command / controller | request-response (argparse → stdout) | itself, pre-fix — mechanical `Any` → `object`/model-attribute rewrite | exact |
| `src/spur/static/app.js` (`DIMS`, `renderInfo()`) | component (browser render) | request-response (fetch → DOM) | itself — **no code change expected**, only the belt test (D-12) reads it | exact (unchanged file; analog is for the new *test*, see below) |
| `tests/test_calc.py` | test | unit | itself, pre-fix — `d["pitch_d"]` → `d.pitch_d` rewrite; `test_impossible_pairs_have_no_centre_distance` (133–145) is the one behavioural test that must move off `with_mate` | exact |
| `tests/test_api.py` | test | integration (HTTP) | itself — `test_info_with_mate` (57–60), the 422 tests (63–73), `_field` (327), module-level bare `client = TestClient(app)` (14) | exact |
| `tests/test_cli.py` | test | integration (subprocess-free CLI invocation) | itself — `test_info_reports_the_mate_it_was_asked_about` (11–15) is D-13's half-analog | exact |
| `tests/test_model.py` | test | unit | itself — `kw: dict[str, Any]` parametrize (17, 28) | exact |
| `tests/test_records.py::test_calc_module_stays_log_free` | test | unit (regex belt on source text) | itself — D-12's literal template | exact |
| `docker/smoke.py` | utility (build-time smoke test, ASGI) | request-response (raw ASGI) | itself — `MutableMapping[str, Any]` → `MutableMapping[str, object]` + one `cast(bytes, ...)` at line 29's `body.extend(...)` | exact |
| `pyproject.toml` `[tool.mypy]` | config | — | itself — the comment block at lines 90–93 | exact |
| `docs/architecture/decision_log.md` | docs | — | `## L20` (314, the most recent entry — append style) | exact |
| `docs/tech_debt/active/2026-09-21-untyped-info-contract.md` | docs (debt file) | — | any file already in `docs/tech_debt/resolved/` for the `git mv` + `Status: resolved` lifecycle shape | role-match |

## Pattern Assignments

### `src/spur/calc.py` — `DerivedDimensions` model + `derive()` (D-01, D-02, D-03, D-09, D-10)

**Analog:** `src/spur/params.py::GearParams` (frozen-model convention) +
`src/spur/calc.py::Profile`/`profile()` (compute-then-construct-once convention, same file)

**Imports pattern** — `calc.py` currently has no pydantic import at all (only
`GearParams` under `TYPE_CHECKING`); `params.py` shows the runtime-import shape to add
(`src/spur/params.py:8-13`):
```python
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_core import PydanticCustomError
```
`calc.py`'s own current head (`src/spur/calc.py:1-11`), which the `TYPE_CHECKING` guard
must be kept exactly as-is (D-09: "the `TYPE_CHECKING` guard exists for the `params →
calc.check` import cycle, not to avoid pydantic, and stays"):
```python
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .params import GearParams
```
Add `from pydantic import BaseModel, ConfigDict, Field` alongside (not replacing) the
`TYPE_CHECKING` block; drop the now-unused `Any` import from `typing` once `dict[str,
Any]` is gone from this file (D-04 house rule: `Any` is not written in this codebase).

**Frozen-model-next-to-its-builder pattern** (`Profile` sits next to `profile()`,
`src/spur/calc.py:22-42`, the literal structural analog `DerivedDimensions` copies —
note this is a `@dataclass(frozen=True)`, not `BaseModel`; D-09 explicitly rejects that
kind for the new model, "a frozen `@dataclass` with Pydantic only at the API edge was
rejected", but the *placement* convention — value type declared immediately above/below
the function that builds it — is what to copy):
```python
@dataclass(frozen=True)
class Profile:
    z: int
    m: float
    alpha: float    # pressure angle, radians
    r: float        # pitch radius
    rb: float       # base radius
    ra: float       # tip radius
    rf: float       # root radius
    psi_p: float    # half tooth-thickness angle at the pitch circle
```

**`_f()`'s `title`/`description`/`json_schema_extra` convention** (`src/spur/params.py:16-22`)
— D-03's literal metadata convention to mirror on every `DerivedDimensions` field
(no `title`/`group`/`unit`-as-string-arg needed here; RESEARCH.md Pattern 1 already
shows the target shape — `description=` and `json_schema_extra={"unit": "mm"}` per field,
**no `default=`** on optional fields, per Pitfall 2):
```python
def _f(default: Any, ge: float, le: float, *, title: str, group: str,
       unit: str = "", step: float | None = None, help: str = "") -> Any:
    extra: dict[str, Any] = {"group": group, "unit": unit}
    if step is not None:
        extra["step"] = step
    return Field(default, ge=ge, le=le, title=title, description=help,
                 json_schema_extra=extra)
```

**Core transform pattern — compute everything first, then one construction call**
(`derive()`'s current body, `src/spur/calc.py:163-215`; this is the exact shape to keep,
only the trailing `return {...}` dict literal becomes `return DerivedDimensions(...)`,
and the local `r3()` nested function — currently defined at line 196 — is applied to
`rfil`/`rec_fil` too per D-10, not just the values already passing through it):
```python
def derive(p: GearParams) -> dict[str, Any]:
    """Derived dimensions plus the numbers you'd measure on a real gear to verify them."""
    pr = profile(p)
    tip, root, gap = _tooth(pr)
    k, w = span_measurement(p)
    odd = p.teeth % 2 == 1
    over_tips = 2 * pr.ra * (math.cos(math.pi / (2 * p.teeth)) if odd else 1.0)

    warnings: list[str] = []
    if tip < MIN_TIP_FDM:
        warnings.append(f"Tip is only {tip:.2f} mm wide; FDM needs about {MIN_TIP_FDM} mm.")
    rfil = root_fillet(p)
    # ... (each warning appended as its precondition is computed) ...

    def r3(v: float | None) -> float | None:
        return None if v is None else round(v, 3)

    return {
        "pitch_d": r3(2 * pr.r),
        # ... every field, dict literal today, DerivedDimensions(...) call after this phase
        "root_fillet": rfil,        # <- currently UNROUNDED; D-10 wraps this in r3() too
        "recess_fillet": rec_fil if rr else None,  # <- also currently unrounded
        "warnings": warnings,
    }
```
D-02's mate absorption — `centre_distance()` (`src/spur/calc.py:243-260`, unchanged) and
`with_mate()`'s current body (`src/spur/calc.py:262-272`, **deleted**, its two lines of
logic — the mate fields plus the "cannot mesh" warning — move *into* `derive()`'s existing
compute-then-return sequence, before the single `DerivedDimensions(...)` call, exactly
where the `warnings.append(...)` calls already live above):
```python
def with_mate(info: dict[str, Any], p: GearParams, mate_teeth: int,
              mate_shift: float = 0.0) -> dict[str, Any]:
    aw = centre_distance(p, mate_teeth, mate_shift)
    out = {**info, "mate_teeth": mate_teeth,
           "centre_distance": None if aw is None else round(aw, 3)}
    if aw is None:
        out["warnings"] = [*info.get("warnings", ()),
                           f"A {mate_teeth}-tooth gear cannot mesh with this one at any "
                           f"centre distance: a total profile shift of "
                           f"{p.profile_shift + mate_shift:+g} is too negative for "
                           f"{p.teeth + mate_teeth} teeth."]
    return out
```
This `model_copy(update=)`-shaped patching is exactly what D-02 forbids for the new
code ("never patched into a frozen object via `model_copy(update=)`") — the mate
computation must be inlined into `derive()`'s own warnings-then-construct sequence, not
kept as a post-hoc patch function.

**RESEARCH.md's verified target shape** (illustrative, combine with the real field list
above — `derive()` and `with_mate()` merged, ghost-error mitigation included):
```python
class DerivedDimensions(BaseModel):  # type: ignore[explicit-any]
    # pydantic-mypy plugin, at this project's default `init_typed=False`, attributes an
    # "explicit-any" [explicit-any] diagnostic to a BaseModel's own class line whenever
    # any field's default is built through a *recognised* pydantic.Field(...) call --
    # verified against InfoQuery/ModelQuery (app.py:201/:206) and a scratch class shaped
    # like this one. See 04-RESEARCH.md Pitfall 1.
    model_config = ConfigDict(frozen=True)

    pitch_d: float = Field(description="Pitch diameter.", json_schema_extra={"unit": "mm"})
    span_teeth: int = Field(description="Teeth spanned for the span measurement.")
    warnings: list[str] = Field(description="Warnings about capped or infeasible values.")

    # Optional fields: NO default= -- required-and-nullable in OpenAPI (D-01, Pitfall 2).
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

**Error handling:** no new error path — `derive()` never raises today and must not
start; `check()` (`src/spur/calc.py:118-152`, unchanged this phase) remains the sole
place infeasibility becomes a `ValidationError`, via `GearParams`'s
`@model_validator(mode="after")` (`src/spur/params.py:77-87`). `DerivedDimensions`
construction is "validated on construction, no `model_construct`" (D-09) — a
`derive()` bug producing the wrong type fails loudly as a `pydantic.ValidationError`
inside `derive()`, not silently.

---

### `src/spur/app.py` — `HealthReport`/`PoolState` (D-05, D-06)

**Analog:** `src/spur/app.py::InfoQuery`/`ModelQuery` (`Field()` convention, same file)

**Imports pattern** — `app.py`'s current pydantic import (`src/spur/app.py:29`, already
present, only `Field` imported today):
```python
from pydantic import Field
```
Add `BaseModel`, `ConfigDict` alongside it for the two new models.

**Core pattern — sibling `Field()`-decorated model in the same file**
(`src/spur/app.py:201-207`, the literal shape to copy, minus the `GearParams`
inheritance since `HealthReport`/`PoolState` are standalone, not gear-parameter
subtypes):
```python
class InfoQuery(GearParams):
    mate_teeth: int | None = Field(None, ge=6, le=1000, title="Mating gear teeth",
                                   description="Also report the centre distance to this gear.")


class ModelQuery(GearParams):
    quality: Literal["preview", "fine"] = Field(
        "fine", description="STL tessellation: preview (coarse, small) or fine.")
```
Note: `InfoQuery.mate_teeth` uses `Field(None, ...)` — a **positional default**, which is
D-01/Pitfall 2's forbidden shape for `DerivedDimensions`'/`HealthReport`'s own
always-present-nullable fields, but is *correct* here since `mate_teeth` on the *query*
model is genuinely optional-and-omittable (the client may not ask for a mate at all) —
do not copy this positional-default shape onto `HealthReport.pool`, which D-06 requires
present-and-`null`, never absent.

**`health()`'s current body — the dict-assembly shape to replace**
(`src/spur/app.py:272-310`, extensive docstring must be preserved/adapted, only the
`payload["pool"] = {...}` inline-dict and the final return type change):
```python
@app.get("/api/health")
def health() -> dict[str, Any]:
    """... (docstring, D-06 rewrites the "absent" paragraph to say "null") ..."""
    pool: BuildPool | None = getattr(app.state, "pool", None)
    payload: dict[str, Any] = {"status": "ok", "version": __version__}
    if pool is not None:
        payload["pool"] = {
            "workers": pool.workers,
            "queue_available": MAX_QUEUED_BUILDS - _in_flight_builds,
            "workers_replaced": pool.replaced,
        }
    return payload
```
Target shape (D-05/D-06 — `pool: PoolState | None`, always present, `None` not absent
under a bare `TestClient`):
```python
@app.get("/api/health")
def health() -> HealthReport:
    pool: BuildPool | None = getattr(app.state, "pool", None)
    return HealthReport(
        status="ok", version=__version__,
        pool=None if pool is None else PoolState(
            workers=pool.workers,
            queue_available=MAX_QUEUED_BUILDS - _in_flight_builds,
            workers_replaced=pool.replaced,
        ),
    )
```

**Error handling:** unchanged — `health()` never raises; the `dict.get`/`getattr`
absence-check (`getattr(app.state, "pool", None)`) is the one conditional, kept as-is.

---

### `src/spur/app.py` — `schema()` (D-07)

**Analog:** RESEARCH.md's verified `JsonSchemaValue` return annotation (Code Examples
section) — no in-repo analog needed, this is a one-line signature change.

**Current** (`src/spur/app.py:314-315`):
```python
@app.get("/api/schema")
def schema() -> dict[str, Any]:
    return GearParams.model_json_schema()
```
**Target** (verified byte-identical output vs `dict[str, object]` this session per
RESEARCH.md):
```python
from pydantic.json_schema import JsonSchemaValue

@app.get("/api/schema")
def schema() -> JsonSchemaValue:
    return GearParams.model_json_schema()
```

---

### `src/spur/app.py` — `info()` (D-01, D-02)

**Analog:** `src/spur/app.py::model()` (322+, the sibling typed-return route in the same
file — already returns a concrete `Response`, not `dict[str, Any]`, so it is the
"already-typed route" shape to match)

**Current** (`src/spur/app.py:319-323`):
```python
@app.get("/api/info")
def info(q: Annotated[InfoQuery, Query()]) -> dict[str, Any]:
    """Derived dimensions. With `mate_teeth`, also the centre distance to that gear."""
    params = _gear(q)
    out = derive(params)
    return with_mate(out, params, q.mate_teeth) if q.mate_teeth else out
```
**Target** (D-02: one construction site — `derive()` itself now takes `mate_teeth`):
```python
@app.get("/api/info")
def info(q: Annotated[InfoQuery, Query()]) -> DerivedDimensions:
    """Derived dimensions. With `mate_teeth`, also the centre distance to that gear."""
    params = _gear(q)
    return derive(params, mate_teeth=q.mate_teeth)
```

---

### `src/spur/app.py` — `_BlobCache` key typing (mechanical, Claude's Discretion)

**Analog:** itself (`src/spur/app.py:57-88`), plus the real call site comment already
in the file naming the key shape:
```python
# Keyed on (params, fmt, quality, encoding) -- "identity" or "gzip" -- so both encodings
# of a gear are first-class variants of the one cache, sharing the one byte budget, ...
```
Current (`src/spur/app.py:57-75`):
```python
class _BlobCache:
    def __init__(self, budget: int) -> None:
        self._budget = budget
        self._items: OrderedDict[Any, bytes] = OrderedDict()
        self._bytes = 0

    def get(self, key: Any) -> bytes | None:
        ...

    def put(self, key: Any, data: bytes) -> None:
        ...
```
Target: `Any` → `tuple[GearParams, str, str, str]` (the real, already-documented key
shape) in all three sites (`_items`'s type param, `get`'s `key`, `put`'s `key`), or a
named `TypeAlias` next to the class if the tuple recurs elsewhere.

---

### `src/spur/params.py` — `_f()` generic (D-08, Claude's Discretion, RESEARCH.md verified)

**Analog:** itself, pre-fix (`src/spur/params.py:16-22`) — see Core pattern block above
for the current body.

**Target** (RESEARCH.md Code Examples, verified this session — `teeth: int = _f(19,
...)` still resolves to `int` under mypy):
```python
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
**Known cost (RESEARCH.md Pitfall 1):** this introduces one new
`# type: ignore[explicit-any]` on `class GearParams(BaseModel):`
(`src/spur/params.py:25`) — the ghost error moves from `_f()`'s own body (3 errors) to
the class line (1 error), a net improvement, not a full elimination. Comment the ignore
with the same citation pattern as RESEARCH.md's `DerivedDimensions` example.

---

### `src/spur/pool.py` — `_run_with_timeout` (D-08 research item, Pattern 2)

**Analog:** itself, pre-fix (`src/spur/pool.py:153-154`), plus `tests/test_pool.py`'s
three real call shapes that any replacement signature must type-check against
(`build_export(p, fmt, quality)`, `_sleep_past_timeout(seconds)`, `_die()`).

**Current:**
```python
async def _run_with_timeout(
    self, p: GearParams, func: Callable[..., bytes], *args: object,
) -> bytes:
```
**Target** (RESEARCH.md Pattern 2, verified zero errors against all three real callers;
`Protocol` with `*args: object` does **not** type-check — do not use it):
```python
from typing import ParamSpec

P = ParamSpec("P")

async def _run_with_timeout(
    self, p: GearParams, func: Callable[P, bytes], *args: P.args, **kwargs: P.kwargs,
) -> bytes:
```

---

### `src/spur/cli.py` — `_add_gear_args`, `cmd_info`, `cmd_export` (D-02, mechanical)

**Analog:** itself, pre-fix (`src/spur/cli.py:22-30`, `65-71`, `74-88`).

**`_add_gear_args`'s `kw` — current** (`src/spur/cli.py:22-30`):
```python
def _add_gear_args(ap: argparse.ArgumentParser) -> None:
    g = ap.add_argument_group("gear parameters (defaults in brackets)")
    for name, field in GearParams.model_fields.items():
        kw: dict[str, Any] = {"dest": name, "default": None, "metavar": "V",
                    "help": f"{field.description} [{field.default}]".replace("%", "%%")}
        if get_origin(field.annotation) is Literal:
            kw["choices"] = list(get_args(field.annotation))
            kw.pop("metavar")
        else:
            kw["type"] = field.annotation
        g.add_argument("--" + name.replace("_", "-"), **kw)
```
Target: `kw: dict[str, object]` (mechanical; `argparse`'s `dest=`/`default=`/`help=`/
`type=`/`choices=` values are heterogeneous by nature — `**kw` into `add_argument`
type-checks the same way `GearParams(**kw)` does per RESEARCH.md's D-08 finding).

**`cmd_info` — current** (`src/spur/cli.py:65-71`, D-02's merge site):
```python
def cmd_info(ns: argparse.Namespace) -> None:
    from .calc import derive, with_mate

    p = _params(ns)
    out = derive(p)
    if ns.mate_teeth:
        out = with_mate(out, p, ns.mate_teeth)
    print(json.dumps(out, indent=2, ensure_ascii=False))
```
Target (`with_mate` import removed; `derive`'s new `mate_teeth=` keyword absorbs the
`if`; JSON rendering is D-13's "Claude's Discretion" — `model_dump_json(indent=2)` is
the pydantic-native equivalent of today's `json.dumps(out, indent=2, ensure_ascii=False)`,
and D-13's CLI-vs-API equivalence test settles whichever is chosen):
```python
def cmd_info(ns: argparse.Namespace) -> None:
    from .calc import derive

    p = _params(ns)
    out = derive(p, mate_teeth=ns.mate_teeth)
    print(out.model_dump_json(indent=2))
```

**`cmd_export`'s `derive(p)["warnings"]` — current** (`src/spur/cli.py:87`):
```python
    for warning in derive(p)["warnings"]:
        print(f"warning: {warning}", file=sys.stderr)
```
Target: `derive(p).warnings` — attribute access, same iteration.

---

### `docker/smoke.py` — ASGI `receive`/`send` (D-08, mechanical, Pitfall 3)

**Analog:** itself, pre-fix (`docker/smoke.py:24-29`).

**Current:**
```python
from collections.abc import MutableMapping
from typing import Any

async def receive() -> MutableMapping[str, Any]:
    return pending.pop(0) if pending else {"type": "http.disconnect"}

async def send(message: MutableMapping[str, Any]) -> None:
    nonlocal status
    if message["type"] == "http.response.start":
        status = message["status"]
    elif message["type"] == "http.response.body":
        body.extend(message.get("body", b""))
```
Target: `MutableMapping[str, Any]` → `MutableMapping[str, object]` on both signatures,
**plus** one `cast(bytes, ...)` at the one call site that breaks under the widened type
(RESEARCH.md Pitfall 3, verified this session — `object` is not
`Iterable[SupportsIndex]`):
```python
from typing import cast

    elif message["type"] == "http.response.body":
        body.extend(cast(bytes, message.get("body", b"")))
```
Do not widen further than this one call site — a blanket `TypedDict` rewrite is
explicitly rejected in RESEARCH.md's Alternatives Considered table as oversized for a
2-line smoke test.

---

### `tests/test_calc.py` — attribute access + `with_mate` removal (D-02, existing tests)

**Analog:** itself (`tests/test_calc.py:1-176`, full file already read — small enough
for one pass).

**Import line to change** (`tests/test_calc.py:7-16`):
```python
from spur.calc import (
    MIN_WALL,
    bore_radius,
    centre_distance,
    derive,
    inv,
    profile,
    span_measurement,
    with_mate,
)
```
`with_mate` import removed (D-02: deleted).

**`d["key"]` → `d.key` rewrite pattern** — every one of `test_default_dimensions`
(20-32), `test_caliper_reading_is_short_for_odd_tooth_counts` (35-38),
`test_higher_pressure_angle_gives_finer_tips_and_thicker_roots` (53-56),
`test_root_fillet_is_capped_with_a_warning` (67-70),
`test_tooth_thickness_and_gap_are_measured_on_the_same_circle` (91-101),
`test_oversized_recess_is_narrowed_to_fit_and_says_so` (104-110),
`test_small_gear_keeps_the_stock_bore_and_recess` (113-118),
`test_recess_is_dropped_when_there_is_no_room_at_all` (121-124),
`test_recess_fillet_is_capped_to_the_narrowed_groove` (127-130). Example
(`test_default_dimensions`, 20-32 — the L05 pinned-values tripwire, numbers must not
move):
```python
def test_default_dimensions() -> None:
    d = derive(GearParams())
    assert d["pitch_d"] == pytest.approx(33.25)
    assert d["tip_d"] == pytest.approx(36.75)
    ...
    assert d["warnings"] == []
```
→
```python
def test_default_dimensions() -> None:
    d = derive(GearParams())
    assert d.pitch_d == pytest.approx(33.25)
    assert d.tip_d == pytest.approx(36.75)
    ...
    assert d.warnings == []
```

**`test_impossible_pairs_have_no_centre_distance`** (`tests/test_calc.py:133-145`) —
the one test exercising `with_mate` directly, must move to `derive(p, mate_teeth=mate)`:
```python
def test_impossible_pairs_have_no_centre_distance(kw: dict[str, Any], mate: int) -> None:
    p = GearParams(bore_d=0, bore_flat=0, bore_chamfer=0, recess_sides="none", **kw)
    assert centre_distance(p, mate) is None
    out = with_mate(derive(p), p, mate)
    assert out["centre_distance"] is None
    assert any("cannot mesh" in w for w in out["warnings"])
```
→
```python
def test_impossible_pairs_have_no_centre_distance(kw: dict[str, object], mate: int) -> None:
    p = GearParams(bore_d=0, bore_flat=0, bore_chamfer=0, recess_sides="none", **kw)
    assert centre_distance(p, mate) is None
    out = derive(p, mate_teeth=mate)
    assert out.centre_distance is None
    assert any("cannot mesh" in w for w in out.warnings)
```
Note the `kw: dict[str, Any]` parametrize type at line 79 and 137 (same pattern) also
becomes `dict[str, object]` (RESEARCH.md D-08: `GearParams(**kw)` type-checks fine
against it, `model_validate()` is not required).

---

### `tests/test_api.py` — health/info/422 tests + `_field` (D-05, D-06, D-08, D-11 new test)

**Analog:** itself — module-level fixture and imports (`tests/test_api.py:1-38`).

**`test_health`** (`tests/test_api.py:40-41`) — unaffected by D-06's `pool: null`
change (only reads `["status"]`, still valid on the typed model's `.model_dump()`):
```python
def test_health() -> None:
    assert client.get("/api/health").json()["status"] == "ok"
```
No change needed here; D-06's new behaviour (`"pool": null` under the bare module-level
`client = TestClient(app)` at line 14, which never runs the lifespan) is implicitly
already exercised — a new assertion (`.json()["pool"] is None`) is Claude's Discretion
to add, not required by CONTEXT.md.

**`test_info_with_mate`** (`tests/test_api.py:57-60`) — unaffected by D-01 (still reads
`.json()["centre_distance"]`, present either way):
```python
def test_info_with_mate() -> None:
    r = client.get("/api/info", params={"teeth": 21, "mate_teeth": 40})
    assert r.status_code == 200
    assert r.json()["centre_distance"] == pytest.approx(1.75 * 61 / 2)
```

**422 tests** (`tests/test_api.py:63-74`) — explicitly out of scope
("`detail[].ctx.fields` is already pinned... nothing in this phase touches `check()` or
the `422` path" — CONTEXT.md D-12), no change:
```python
def test_infeasible_is_422_with_fields() -> None:
    r = client.get("/api/info", params={"bore_flat": 3})
    assert r.status_code == 422
    detail = r.json()["detail"][0]
    assert "D-flat" in detail["msg"]
    assert detail["ctx"]["fields"] == ["bore_flat"]
```

**`_field`** (`tests/test_api.py:327-334`) — Claude's Discretion, `Any` → `object`:
```python
def _field(rec: logging.LogRecord, name: str) -> Any:
    return getattr(rec, name)
```
→ `-> object`, same body.

**D-11's new test (Wave 0 gap, no existing analog — write fresh, pattern below)** —
add near `test_schema_drives_the_form` (`tests/test_api.py:52-56`, the closest existing
"read `/api/...` JSON, assert on nested keys" shape):
```python
def test_schema_drives_the_form() -> None:
    props = client.get("/api/schema").json()["properties"]
    assert props["teeth"]["group"] == "Teeth"
    assert props["module"]["unit"] == "mm"
    assert props["recess_sides"]["enum"] == ["both", "top", "bottom", "none"]
```
D-11 target shape (literal names per CONTEXT.md — `/api/info`'s `200` response `$ref`s
`DerivedDimensions`, component lists every field name, a length field carries
`unit: mm`, `/api/health` `$ref`s `HealthReport`):
```python
def test_openapi_documents_the_typed_contracts() -> None:
    doc = client.get("/openapi.json").json()
    info_ref = doc["paths"]["/api/info"]["get"]["responses"]["200"]["content"] \
        ["application/json"]["schema"]["$ref"]
    assert info_ref == "#/components/schemas/DerivedDimensions"
    dims = doc["components"]["schemas"]["DerivedDimensions"]["properties"]
    assert set(dims) == {"pitch_d", "tip_d", ..., "mate_teeth", "centre_distance", "warnings"}
    assert dims["pitch_d"]["unit"] == "mm"
    health_ref = doc["paths"]["/api/health"]["get"]["responses"]["200"]["content"] \
        ["application/json"]["schema"]["$ref"]
    assert health_ref == "#/components/schemas/HealthReport"
```

---

### `tests/test_cli.py` — D-13's CLI-vs-API equivalence test (new, Wave 0 gap)

**Analog:** `test_info_reports_the_mate_it_was_asked_about`
(`tests/test_cli.py:11-15`) for the CLI-invocation half, `tests/test_api.py`'s
`client = TestClient(app)` (line 14) for the API half — D-13 combines both:
```python
def test_info_reports_the_mate_it_was_asked_about(capsys: pytest.CaptureFixture[str]) -> None:
    cli.main(["info", "--teeth", "19", "--mate-teeth", "40"])
    out = json.loads(capsys.readouterr().out)
    assert out["mate_teeth"] == 40
    assert out["centre_distance"] == pytest.approx(51.625)
```
Target shape for D-13 (new test — place in `tests/test_cli.py` since it needs `cli.main`,
or `tests/test_api.py` since it needs `client`; either file already imports the other
piece's sibling module):
```python
def test_cli_and_api_agree_on_the_same_gear(capsys: pytest.CaptureFixture[str]) -> None:
    for extra in ([], ["--mate-teeth", "40"]):
        cli.main(["info", "--teeth", "21", *extra])
        cli_out = json.loads(capsys.readouterr().out)
        params = {"teeth": 21} | ({"mate_teeth": 40} if extra else {})
        api_out = client.get("/api/info", params=params).json()
        assert cli_out == api_out
        if not extra:
            assert cli_out["mate_teeth"] is None
            assert cli_out["centre_distance"] is None
```

---

### `tests/test_model.py:28` and `tests/test_records.py::test_calc_module_stays_log_free` (D-08, D-12)

**`tests/test_model.py`** (`tests/test_model.py:17-28`) — same `kw: dict[str, Any]` →
`dict[str, object]` mechanical rewrite as `test_calc.py`:
```python
@pytest.mark.parametrize("kw", [
    {},
    ...
])
def test_builds_one_valid_solid(kw: dict[str, Any]) -> None:
    p = GearParams(**kw)
```
→ `kw: dict[str, object]`.

**`tests/test_records.py::test_calc_module_stays_log_free`** (`tests/test_records.py:242-252`)
— the literal belt-test template D-12 copies against `app.js` instead of `calc.py`:
```python
def test_calc_module_stays_log_free() -> None:
    """L01, REQ boundary: ..."""
    source = Path(calc_module.__file__).read_text()
    assert not re.search(
        r"^\s*(import|from)\s+(logging|\.records|spur\.records)\b", source, re.MULTILINE)
```
D-12 target shape (new test — either extend `tests/test_records.py` or a new
`tests/test_static.py`; RESEARCH.md's Wave 0 Gaps section leaves the file choice open):
```python
def test_app_js_dims_table_names_real_derived_dimensions_fields() -> None:
    """D-12 belt, the pattern of test_calc_module_stays_log_free: app.js's DIMS table
    (and the two keys read outside it) must name real DerivedDimensions fields, or a
    renamed/dropped field silently breaks the UI with no static check to catch it."""
    source = Path("src/spur/static/app.js").read_text()
    keys = set(re.findall(r"^\s*\['(\w+)',", source, re.MULTILINE))
    keys |= {"centre_distance", "warnings"}
    assert keys <= set(DerivedDimensions.model_fields)
```

---

## Shared Patterns

### Frozen, validated-on-construction Pydantic model
**Source:** `src/spur/params.py::GearParams` (`ConfigDict(frozen=True)`,
`src/spur/params.py:25-28`)
**Apply to:** `DerivedDimensions` (`calc.py`), `HealthReport`/`PoolState` (`app.py`)
```python
class GearParams(BaseModel):
    """Involute spur gear with optional D-bore and annular face recesses."""

    model_config = ConfigDict(frozen=True)
```

### `Field(description=..., json_schema_extra={"unit": "mm"})` metadata convention
**Source:** `src/spur/params.py::_f()` (`src/spur/params.py:16-22`)
**Apply to:** every field of `DerivedDimensions`/`HealthReport`/`PoolState` (D-03).
Lengths get `json_schema_extra={"unit": "mm"}`; counts (`span_teeth`, `workers`) and
lists (`warnings`) get neither.

### `# type: ignore[explicit-any]` ghost-error mitigation on model class lines
**Source:** RESEARCH.md Pitfall 1 (verified this session; already present in the
baseline on `InfoQuery`/`ModelQuery`, `src/spur/app.py:201`/`:206`, caused by their
direct `Field()` calls)
**Apply to:** `class GearParams(BaseModel):` (once `_f` goes generic),
`class DerivedDimensions(BaseModel):`, `class HealthReport(BaseModel):`,
`class InfoQuery(GearParams):`, `class ModelQuery(GearParams):`, and
`class PoolState(BaseModel):` only if it uses `Field()` (plain typed attributes with no
`Field()` call do not need it — see RESEARCH.md Assumptions Log A2). Every ignore
carries an explanatory comment citing 04-RESEARCH.md, per the security note in
RESEARCH.md's Known Threat Patterns table (an undocumented/blanket ignore is
indistinguishable from a real `Any` leak at future review).
```python
class DerivedDimensions(BaseModel):  # type: ignore[explicit-any]
    # pydantic-mypy plugin, at this project's default `init_typed=False`, attributes an
    # "explicit-any" [explicit-any] diagnostic to a BaseModel's own class line whenever
    # any field's default is built through a *recognised* pydantic.Field(...) call --
    # verified this session (04-RESEARCH.md Pitfall 1) against InfoQuery/ModelQuery
    # (already in the 22-error baseline) and a scratch class shaped like this one.
```

### Required-and-nullable, never optional-with-`default=None`
**Source:** RESEARCH.md Pitfall 2 (verified live against `/openapi.json`)
**Apply to:** `DerivedDimensions.mate_teeth`/`.centre_distance`/`.bore_effective`/
`.recess_id`/`.recess_od`/`.recess_fillet`/`.web`, `HealthReport.pool`. None of these
get `default=` in their `Field(...)` call — the constructor always supplies a value
(`None` or real), matching D-09's "no `model_construct`" rule.

### Uniform rounding at construction, via `r3()`
**Source:** `src/spur/calc.py:196-197` (the nested `r3()` inside `derive()`, already
applied to most fields)
**Apply to:** `root_fillet` and `recess_fillet` specifically (D-10 — today the only two
fields returned raw/unrounded; both must go through the same `r3()` call as every other
length before this phase ships).

### Import-linter contracts, unchanged
**Source:** `pyproject.toml` `[tool.importlinter]` (not read this session in full, but
canonical_refs confirms: `calc.py` may import pydantic — already does via `GearParams`
at runtime under `TYPE_CHECKING` — but not `cadquery`/`OCP`/`logging`/`spur.records`)
**Apply to:** `calc.py`'s new top-level `from pydantic import BaseModel, ConfigDict,
Field` — legal, no contract change needed (RESEARCH.md's Architectural Responsibility
Map and Established Patterns sections both confirm this explicitly).

### mypy ratchet — `disallow_any_explicit = true`, no per-module override
**Source:** `pyproject.toml:80-93` (`[tool.mypy]`, current comment block to replace)
**Apply to:** the whole `[tool.mypy]` block — global, not `[[tool.mypy.overrides]]`
scoped, per D-04 ("No per-module override for `tests.*`/`docker.*`/`bench.*` — a
carve-out is a second ratchet, the shape this phase retires").
```toml
[tool.mypy]
python_version = "3.12"
plugins = ["pydantic.mypy"]   # without it mypy cannot see the generated model __init__
strict = true
warn_unreachable = true
enable_error_code = ["ignore-without-code", "redundant-expr", "truthy-bool", "possibly-undefined"]
# disallow_any_explicit is deliberately OFF. The API's derive()/info() contracts are
# `dict[str, Any]` by design (a JSON document whose keys vary with the parameters), so
# turning it on today would fail the gate on code that is correct. It is a ratchet, not
# an exemption: see docs/tech_debt/active/2026-09-21-typed-info-contract.md.
```
→ `disallow_any_explicit = true` added to the block; the whole comment paragraph above
(including the stale `typed-info-contract.md` filename pointer, D-15) replaced with a
comment explaining the new house rule (D-04: "`Any` is not written in this codebase; a
genuinely untyped value is `object`, everything else is its real type") and citing L21.

### Debt-file lifecycle (`git mv`, `Status: resolved`, INDEX row move)
**Source:** CLAUDE.md's "Capturing ideas and debt" section + `docs/tech_debt/INDEX.md`'s
existing "Resolved" table shape (`docs/tech_debt/INDEX.md:24-30`, header only read this
session — the row format is `| Item | Resolved in |`)
**Apply to:** `docs/tech_debt/active/2026-09-21-untyped-info-contract.md` (D-16) — flip
`Status: resolved`, add the commit sha, `git mv` to `docs/tech_debt/resolved/`, move its
`docs/tech_debt/INDEX.md` row from "Active" (`docs/tech_debt/INDEX.md:19`, currently
`| must | [The info contract is \`dict[str, Any]\`](active/2026-09-21-untyped-info-contract.md) | a client depends on the shape, or a third consumer appears |`)
to "Resolved" — all in the same commit as the code fix, per CLAUDE.md.

### Decision-log append style
**Source:** `docs/architecture/decision_log.md` — most recent entry `## L20 — Structured
JSON logging, configured at two idempotent call sites` (line 314, read via grep only,
not full text — the file is large; header format alone is the copyable pattern: `## L{n}
— {one-line summary}`, with a "supersedes L{m}" suffix when applicable, e.g. `## L18 —
One lock, and what it no longer costs (supersedes L06)`, line 214)
**Apply to:** the new `## L21` entry (D-14) — `## L21 — {summary} (supersedes L14)`,
appended after L20, with L14's own body (`docs/architecture/decision_log.md:128-143`)
left untouched (append-only policy).

## No Analog Found

None — every file this phase touches already exists with a same-file or same-module
analog (this is a typing/contract retrofit across existing files, not new-surface work).
The three genuinely new *tests* (D-11, D-12, D-13) each have a named structural analog
(`test_schema_drives_the_form` for D-11's "read a JSON endpoint, assert nested keys"
shape; `test_calc_module_stays_log_free` for D-12's regex-belt shape;
`test_info_reports_the_mate_it_was_asked_about` + the module-level `client` for D-13's
two-serialiser-equivalence shape) — see their Pattern Assignments above.

## Metadata

**Analog search scope:** `src/spur/` (all 6 touched modules), `tests/` (5 touched test
files), `docker/smoke.py`, `pyproject.toml`, `docs/architecture/decision_log.md`,
`docs/tech_debt/` — the full canonical_refs file list from 04-CONTEXT.md; no `Glob`/
`Grep`-based external search was needed since every analog is the file itself (pre-fix
shape) or a sibling in the same module, all already enumerated in CONTEXT.md's
`<canonical_refs>` and RESEARCH.md's Ratchet Baseline table.
**Files scanned:** 20 (13 modified files + `docs/tech_debt/INDEX.md` +
`docs/architecture/decision_log.md` + 5 further `docs/architecture/gear-maths/*.md`/
`http-api.md`/`web-ui.md` files named under D-15, read only via `grep`/`git ls-files`
for tracked-status and line-location confirmation, not full content — their prose edits
are D-15's job, not a pattern-copy target, since they document the contract rather than
implement it).
**Pattern extraction date:** 2026-09-24
