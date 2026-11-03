# Phase 33: Interfaces and Parity - Pattern Map

**Mapped:** 2026-10-27
**Files analyzed:** 22 new/modified
**Analogs found:** 21 / 22 (all paths verified git-tracked via `git ls-files`)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match |
|---|---|---|---|---|
| `src/spur/shaft_model.py` (`_guard_volume`, lines ~130-141) | service (kernel guard) | transform | itself (fix in place) | exact |
| `tests/test_shaft_model.py` (new guard test) | test | transform | same file, `test_a_cone_past_the_tooth_height_is_refused_by_the_volume_bracket` (:314) | exact |
| `src/spur/shaft_params.py` (`resolve_shaft`, `dims` schema key, optional `enabled_when`) | model + pure utility | transform | `src/spur/params.py:87` (`json_schema_extra` inline list); `cli.py:59-68` error style | role-match |
| `src/spur/app.py` (shaft routes, `ShaftInfoQuery`/`ShaftModelQuery`, `_shaft()`, WR-02 + conflict `Depends`) | controller/route | request-response | `app.py` `InfoQuery`/`ModelQuery`/`_gear`/`info`/`model` (:236-262, :374-385, :509-518) | exact |
| `src/spur/cli.py` (`shaft` group) | CLI | request-response | `cli.py` `_add_gear_args`, `_params`, `cmd_info`, `cmd_export` (:42-116) | exact |
| `src/spur/static/app.js` (part state, text branch, dims renderer, switch, `followHash`) | component | event-driven | `app.js` `buildForm` (:54-110), `readHash` (:119), `update` (:261) | exact (self) |
| `src/spur/static/index.html` (toggle above `#params`) | component | event-driven | existing `<aside>` / `#params` (index.html:19) | role-match |
| `src/spur/static/style.css` (`.part-switch`, `[data-part=shaft] .mate`) | config | n/a | existing style.css | role-match |
| `tests/test_shaft_interfaces.py` (new, light) | test | request-response | `tests/test_cli.py:67` + `tests/test_seam.py:152` (TestClient, `_query_keys`) | role-match |
| `tests/shaft_parity.py` (new shared readers) | test helper | transform | `tests/browser_session.py`, `tests/composition.py` | partial |
| `tests/test_api.py` (pin amendments, dims test replacing regex-over-JS) | test | transform | same file :173-182, :265-345, :351-393 | exact |
| `tests/test_cli.py` (shaft cases) | test | request-response | same file :67-98 | exact |
| `tests/test_seam.py` (route-table pin, shaft keys) | test | transform | same file :126-160 | exact |
| `tests/test_browser.py` (shaft steps, flip `ACCEPTED_LINK`, per-field WR-02 sweep, parity step) | test | request-response | same file :122, :2061-2095 | exact |
| `tests/test_browser_pins.py` | test | transform | same file :60-80, :242-262 | exact |
| WR-02 pure token-table test | test | transform | `tests/test_seam.py` style (TestClient parametrised) | role-match |
| `bench/RESULTS.md` (Phase 33 heading) | doc | n/a | `### The heaviest shaft (32-05)` (:7082), `### Seen red once (Phase 32)` (:7240), `### Phase close checks (32-06)` | exact |
| `docs/architecture/decision_log.md` (new L49) | doc | n/a | L44/L46/L48 entries | exact |
| `docs/architecture/web-ui.md`, `README.md` | doc | n/a | existing | exact |
| `docs/tech_debt/active/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md` -> `resolved/` + INDEX | doc | n/a | AGENTS.md debt workflow | exact |
| `docs/tech_debt/active/2026-10-27-shaft-volume-guard-accepts-an-uncut-chamfer.md`, `...-shaft-contention-row.md` -> `resolved/` | doc | n/a | same | exact |
| Contention run (last plan) | bench | batch | `bench/RESULTS.md` L37 ten-concurrent section | role-match |

## Pattern Assignments

### `src/spur/app.py` shaft routes (controller, request-response)

**Analog:** `src/spur/app.py` gear routes.

**Query-model + strip pattern** (app.py:236-253):
```python
class InfoQuery(GearParams):
    mate_teeth: int | None = Field(None, ge=6, le=1000, title="Mating gear teeth",
                                   description="Also report the centre distance to this gear.")

class ModelQuery(GearParams):
    quality: Literal["preview", "fine"] = Field(
        "fine", description="STL tessellation: preview (coarse, small) or fine.")

def _gear(q: GearParams) -> GearParams:
    return GearParams(**q.model_dump(include=set(GearParams.model_fields)))
```
Copy: `ShaftInfoQuery(ShaftParams)` adds `designation: str | None = Field(None, ...)`; `ShaftModelQuery(ShaftParams)` adds `quality`. `_shaft(q)` strips to plain `ShaftParams` (cache-key equality includes class), overlays `parse_designation(...)._asdict()` when set, and maps `ValidationError` to a 422 with `loc ["query","designation"]` (see RESEARCH Pattern 1; otherwise 500).

**Routes** (app.py:374-385, 509-518):
```python
@app.get("/api/schema")
def schema() -> JsonSchemaValue:
    return GearParams.model_json_schema()

@app.get("/api/info")
def info(q: Annotated[InfoQuery, Query()]) -> DerivedDimensions:
    return derive(_gear(q), mate_teeth=q.mate_teeth)

@app.get("/api/model.{fmt}", response_class=Response,
         responses={200: {"content": {t: {} for t in MEDIA_TYPES.values()}}})
async def model(fmt: Literal["stl", "step"], q: Annotated[ModelQuery, Query()],
                request: Request,
                backend: Annotated[BuildBackend, Depends(build_backend)]) -> Response:
    return await _serve_model(_gear(q), fmt, q.quality, request, backend)
```
Shaft siblings: `/api/shaft/schema`, `/api/shaft/info` (returns `ShaftDimensions` from `shaft_calc`), `/api/shaft/model.{fmt}` calling `_serve_model(_shaft(q), ...)`. `_serve_model` (:385-509) is already part-agnostic; do not copy it. Download name comes from `params.slug()` at the end (`Content-Disposition`).

**422 envelope** (app.py:443-444, 283-289):
```python
raise HTTPException(422, detail=[{"loc": ["query"], "msg": str(exc), "type": "build_error"}])
```
WR-02 and conflict dependencies use the same envelope with `loc ["query", name]` and a `type` (`number_as_written`, `conflict`). They take only `Request`, so no OpenAPI parameter is added (gear `/api/schema` bytes and `test_the_gear_routes_take_the_v0_6_query_keys` unaffected). Attach via `dependencies=[Depends(...)]` on `/api/info`, `/api/model.{fmt}` and the shaft routes. Imports already present: `Depends, FastAPI, HTTPException, Query, Request`.

---

### `src/spur/cli.py` shaft group (CLI, request-response)

**Analog:** cli.py:42-116, 119-149.

**Flag generation** (:42-56): copy `_add_gear_args` over `ShaftParams.model_fields`; use a different group header than `"gear parameters (defaults in brackets)"` (tests/test_cli.py partitions on it). `type=field.annotation` works for str/int/float; no Literal fields on the shaft.

**Params + error pattern** (:59-68):
```python
def _params(ns):
    values = {k: v for k in GearParams.model_fields if (v := getattr(ns, k)) is not None}
    try:
        return GearParams(**values)
    except ValidationError as exc:
        for err in exc.errors():
            where = ".".join(str(x) for x in err["loc"])
            msg = err["msg"].removeprefix("Value error, ")
            print(f"error: {where + ': ' if where else ''}{msg}", file=sys.stderr)
        raise SystemExit(2) from None
```
Shaft: pass the non-None dict (incl. `designation`) to the shared `shaft_params.resolve_shaft(designation, given)`; conflict or unparseable designation prints `error: ...` and exits 2.

**info/export** (:90-116): `print(derive_shaft(p).model_dump_json(indent=2))`; export imports `model.export` lazily (never `shaft_model`, never `app`/`fastapi`), infers format from suffix, `BuildError -> SystemExit`, prints warnings to stderr. Register via `sub.add_parser("shaft")` then nested `.add_subparsers(dest="shaft_cmd", required=True)`; leave the gear `info`/`export` registration (:133-146) untouched. Module docstring line 1 lists the commands; update it.

---

### `src/spur/shaft_params.py` (model + pure utility)

**Analog for schema key:** params.py:87
```python
model_config = ConfigDict(frozen=True, json_schema_extra={"selectors": [_BORE_SHAPE]})
```
Shaft currently has `model_config = ConfigDict(frozen=True)` (shaft_params.py:31). Add `json_schema_extra={"dims": [{"key":..., "label":..., "unit":...}, ...]}` as an INLINE list (a pre-built `list[JsonDict]` variable fails mypy strict, per the comment in params.py). Row keys are the `ShaftDimensions` fields (shaft_calc.py:153-196) minus `warnings`.

**Error style for `resolve_shaft`:** `PydanticCustomError("infeasible", "{message}", {"message":..., "fields":[...]})` (shaft_params.py:79-89) gives the `ctx.fields` shape `problems()` reads. The function stays pure (no kernel, no logger imports; the import contracts in `tests/test_seam.py:84-118` enforce this). `SPLINE_KEYS = ("reference_d", "module", "teeth", "fit")`; the conflict reads key presence, never `model_fields_set`.

**`enabled_when` (D-18, optional):** use `when("shank_length", "gt", 0)` from params.py:18 on `shank_d`, only after a kernel test (analog `test_shaft_model.py:234`, `_with_applied_chamfer` helper style) proves equal solids.

`slug()` (:91-99) stays unchanged; update only its "Provisional" docstring when L49 freezes it.

---

### `src/spur/shaft_model.py` `_guard_volume` fix + test (D-16)

**Analog:** shaft_model.py:130-141, bracket check:
```python
upper = area * length + math.pi * (shank_d / 2) ** 2 * shank_length
lower = upper - c * (area - math.pi * rf ** 2)
...
if (not lower * (1 - VOLUME_BRACKET_SLACK) <= volume <= upper * (1 + VOLUME_BRACKET_SLACK)
        or abs(box.zmax - box.zmin - (length + shank_length)) > TOL):
    raise BuildError(...)
```
Read the debt item for the defect. **Test analog** (tests/test_shaft_model.py:314-322):
```python
def test_a_cone_past_the_tooth_height_is_refused_by_the_volume_bracket(monkeypatch) -> None:
    _with_applied_chamfer(monkeypatch, 10.0)
    with pytest.raises(BuildError, match="not the shape that was asked for"):
        build_shaft(ShaftParams())
```
New test uses the same `_with_applied_chamfer` monkeypatch; record the red in `bench/RESULTS.md`.

---

### `src/spur/static/app.js` (component, event-driven)

**Analog:** itself. Key excerpts to preserve or branch from:

`buildForm()` (:54-110) is generic; the number branch (:73-83) is `input.type='number'` for everything non-enum. Add a `prop.type === 'string'` branch (text, `maxLength`, `pattern`, `spellcheck=false`) and keep the `if (prop.enum)` branch byte-identical (shaft `fit` is a string without enum). `buildForm(which)` must fetch `api/schema` or `api/shaft/schema` and clear `form`, `fields`, `defaults`, `selectors`, `stash`, `rejected`, the debounce timer, and bump `seq`.

`refuse()` / `readHash()` / `gearQuery()` (:115-135): keep generic; part detection runs before `readHash()`. `update()` (:261-300): keep `const infoQ = new URLSearchParams(q);` and `history.replaceState(null, '', hash ? ...)` tokens; `part` goes into the hash only (first key), never into `q`/`infoQ`. Fetch bases (`api/info`, `api/model.stl`) come from the part descriptor; `fail()` text `'Showing the last valid gear'` (:281) must become part-neutral or the scene cleared on a switch.

`renderInfo` (:223): shaft path loops `schema.dims`; render by value type (`typeof v === 'string'` -> text, else `fmt(v)` plus unit), skip `null` (D-22). Gear keeps its `DIMS` array.

Hide the mate box via `document.body.dataset.part` and CSS only; `.hidden =`, `.style.display`, `classList.add('hidden')`, `.innerHTML` fail `writes_a_field_shut` (tests/test_api.py:351-393). Part texts and the bad-`part` message use `textContent`. Replace the pinned `hashchange` token (test_api.py:275) with a `followHash` that awaits `buildForm(part)` first; log the swap in L49. No quoted gear/shaft field names outside `DIMS`; no new line starting `['word',` outside `DIMS`; `fields.set(` count stays 1.

---

### `tests/test_api.py` pins

Excerpts to read before editing app.js: :173-182 (DIMS-row guard), :265-345 (about 45 collapsed-token pins), :328-334 (no quoted field names), :351-393 (`writes_a_field_shut`). Replace the regex-over-JS row check for the shaft with a Python test: `{r["key"] for r in dims} <= set(ShaftDimensions.model_fields)` and the complement equals `{"warnings"}`.

---

### `tests/test_seam.py` (route-table pin)

Excerpt (:152-160):
```python
def test_the_gear_routes_take_the_v0_6_query_keys() -> None:
    fields = set(GearParams.model_fields)
    assert _query_keys("/api/info") == fields | {"mate_teeth"}
    assert _query_keys("/api/model.{fmt}") == fields | {"quality"}
    assert _query_keys("/api/schema") == set()
```
Add the same shape for the shaft routes (`set(ShaftParams.model_fields) | {"designation"}`, `| {"quality"}`). `test_every_route_beyond_v0_6_lives_under_the_shaft_prefix` (:126) already covers the prefix.

---

### `tests/test_cli.py` / `tests/test_shaft_interfaces.py` (API vs CLI parity)

**Analog:** tests/test_cli.py:67-98:
```python
client = TestClient(spur.app.app)
cli.main(["info", "--teeth", "21"])
cli_out = json.loads(capsys.readouterr().out)
api_out = client.get("/api/info", params={"teeth": 21}).json()
assert cli_out == api_out
assert list(cli_out) == list(DerivedDimensions.model_fields)
```
Parametrise over the fixed shaft set (default, W30x2x14, one odd-z, `shank_length=0`) using `["shaft","info", ...]` vs `/api/shaft/info`; raw-equal. Download name: `ShaftParams(**cli_values).slug()` vs the API `Content-Disposition`. Error exit: see test_cli.py:266 (`exit 2`, names the problem).

---

### `tests/test_browser.py` (shaft steps, WR-02 flip, web-vs-API parity)

**Flip** (:122, :2087-2095): `ACCEPTED_LINK = "face_width=5."` comment/expectation change from built to refused. Current block asserts status 200 and `#dl-stl` href; new block asserts 422 (`_api_get(server, "/api/info", sent)`), `label.field.invalid` count 1, no `#dl-stl` href, no STL request. Reuse the structure of the `BLANK_LINK` assertions above it (:2064-2075). Wrap in `with step("...", no_foreign_key):`.

Constraints: `no_foreign_key` (:704, :2132) allows gear keys only, so shaft pages need their own recorder key set and their own route glob (`STL_ROUTE` in `tests/browser_session.py:39` is gear-shaped; `"/api/info" in request.url` does not match `/api/shaft/info`). `_follow_link` requires a changed fragment. Parity is a step inside `test_the_shipped_viewer_in_a_real_browser` (single server, module-scoped fixture :141-153). `tests/test_browser_pins.py` bans skip/xfail/getenv in `*browser*` modules, and requires exactly one module defining that test.

## Shared Patterns

### 422 envelope
**Source:** `src/spur/app.py:443-444`
**Apply to:** WR-02 dependency, designation conflict, `_shaft()` ValidationError mapping.
`HTTPException(422, detail=[{"loc": ["query", name], "type": ..., "msg": ...}])`; `problems()` in app.js reads `d.loc[1]` and `d.ctx.fields`.

### One shared pure rule for API and CLI
**Source:** new `shaft_params.resolve_shaft`; error print style `cli.py:63-68`.
**Apply to:** `_shaft()`/dependency in app.py and `cmd_shaft_*` in cli.py. The same sentence on both.

### "Seen red once" record
**Source:** `bench/RESULTS.md` `### Seen red once (Phase 32)` (:7240).
**Apply to:** every new guard/pin: volume guard, WR-02 flip, parity perturbation, `part` pins. Add a Phase 33 heading plus the Chromium table (`### Tokens a control cannot hold (28-01)` is the earlier record).

### Debt retirement in the fixing commit
**Source:** AGENTS.md. Items: `2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md` (with WR-02 commit), `2026-10-27-shaft-volume-guard-accepts-an-uncut-chamfer.md` (own commit), `2026-10-27-shaft-contention-row.md` (last plan). `Status: resolved`, sha, `git mv` to `resolved/`, INDEX row moved.

### Import boundaries
`spur.cli` names neither `shaft_model` nor `app`/`fastapi`/`starlette` (pyproject contracts at ~:193, :250); shaft maths modules import no kernel, logger or gear maths (tests/test_seam.py:84-118). Run `make verify` and `make gear.unchanged`; `git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml` stays empty.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| Part toggle (radio group in `index.html` + `app.js` handler) | component | event-driven | No existing control outside `#params`; use a native `<fieldset>` of `<input type=radio>` per RESEARCH, copy only the class/label conventions of the existing `<aside>` |
| WR-02 Chromium-table re-probe test (browser) | test | request-response | Closest is the golden sweep technique in `tests/test_browser.py` (aborted STL route, `sweep()`); the table walk itself is new (RESEARCH "Observed Chromium table") |
| `tests/shaft_parity.py` shared readers | test helper | transform | No existing multi-interface reader module; shape it like `tests/browser_session.py` |

## Metadata

**Analog search scope:** `src/spur/`, `tests/`, `bench/RESULTS.md`, `docs/tech_debt/active/`
**Files scanned:** ~15 read in part or whole, plus greps over the rest
**Pattern extraction date:** 2026-10-27
**Note:** RESEARCH.md was read to line 482 of 585; remaining lines (past Open Question 6) not loaded. `index.html`, `style.css`, `docs/architecture/web-ui.md` and the decision-log entries were located, not read.
