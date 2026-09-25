# Phase 4: Typed Derived-Dimensions Contract - Context

**Gathered:** 2026-09-24
**Status:** Ready for planning

<domain>
## Phase Boundary

`derive()` returns a frozen Pydantic `DerivedDimensions` model instead of `dict[str, Any]`;
mypy's `disallow_any_explicit` is turned on for the whole `make typecheck` scope
(`src tests docker bench`) and `make verify` passes with it on; `/openapi.json` documents
the typed shape; the web UI's, CLI's and API's reads of the document keep working and are
proven by tests; `docs/tech_debt/active/2026-09-21-untyped-info-contract.md` ends the phase
`Status: resolved`, `git mv`'d, INDEX row moved, in the same commit as the fix; L14 is
superseded by an appended `L21`, not edited.

Requirement: REQ-typed-derived-dimensions.

**Measured, not assumed:** `mypy --disallow-any-explicit src tests docker bench` at
`538d26f` reports **22 errors in 9 files** — `calc.py` ×2 (`derive`, `with_mate`),
`app.py` ×10 (`_BlobCache` key ×3, `InfoQuery`/`ModelQuery` ×2, `health` ×2, `schema`,
`info`), `params.py` ×3 (`_f`), `cli.py` ×1, `pool.py` ×1, `tests/test_calc.py` ×2,
`tests/test_model.py` ×1, `tests/test_api.py` ×1, `docker/smoke.py` ×2. The debt file
names only the first two. All 22 are in scope; the mypy config is global.

Not in this phase: any new gear geometry; exposing `mate_shift` on the wire; a
browser-driven UI test; the UI reading labels/units from the schema; any change to the
`warnings` sentences or the `422` `detail[].ctx.fields` shape; CI observation (Phase 5).

</domain>

<decisions>
## Implementation Decisions

### Wire shape and mate composition
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

### Ratchet scope beyond `derive()`
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

### Model home, kind and rounding
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

### Proof the contract holds (the tests this phase ships)
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

### Bookkeeping this phase owes (from CLAUDE.md, not discussed — required)
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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The debt this phase retires
- `docs/tech_debt/active/2026-09-21-untyped-info-contract.md` — the shape it asks for
  ("a `DerivedDimensions` model (Pydantic …) with explicit optional fields, returned by
  `derive()` and serialised at the API boundary. Then turn `disallow_any_explicit` on"),
  the UI reads it protects. Must end the phase `Status: resolved`, sha recorded,
  `git mv`'d to `docs/tech_debt/resolved/`, row moved in `docs/tech_debt/INDEX.md`.
- `docs/tech_debt/INDEX.md` — the row that moves with it.

### Locked decisions and standards
- `docs/architecture/decision_log.md` — L14 (the ratchet; superseded by `L21`, not
  edited), L03 (cap-and-warn — `warnings` stays a list of sentences), L05 (defaults
  never rescale — `test_default_dimensions`'s numbers must not move), L08 (no plausible
  number — `centre_distance: None` stays), L13 (`make verify` is the gate), L02 (one
  `GearParams` drives all three interfaces — the same now holds for the output).
  Append-only.
- `CLAUDE.md` / `AGENTS.md` — the gate, the debt-file lifecycle, "one concern per commit",
  "claims about performance are measured".
- `docs/CODING_VALUES.md` — "Data contracts should be typed at boundaries"; the comment
  standard every new field description and rewritten comment must meet.

### Docs that state the old contract (D-15)
- `docs/architecture/gear-maths/tactics.md` §Reports and §Rounding — the
  `derive(p) -> dict[str, Any]` line, "The `Any` here is deliberate and tracked (L14)",
  the `with_mate` line, "rounded to 3 decimals … in `derive()`".
- `docs/architecture/gear-maths/implementation.md` — the `derive(p)` / `with_mate(...)`
  table rows.
- `docs/architecture/gear-maths/strategy.md` line 32 and
  `docs/architecture/gear-maths/errors_and_logging.md` line 19 — `with_mate()` mentions.
- `docs/architecture/http-api.md` — endpoint table (`/api/info`, `/api/health`), the
  `InfoQuery`/`ModelQuery` paragraph, the D-13 paragraph anticipating Phase 4.
- `docs/architecture/web-ui.md` §Errors — how `warnings` and `detail[].ctx.fields` are
  rendered (must keep working; nothing here changes).
- `pyproject.toml` `[tool.mypy]` — the comment block with the stale filename;
  `[tool.importlinter]` — the contracts `calc.py` must keep satisfying (no `cadquery`,
  `OCP`, `logging`, `spur.records`).

### Phase 2 / Phase 3 decisions this phase builds on
- `.planning/phases/02-cad-off-the-event-loop/02-CONTEXT.md` — D-02 (serving process is
  kernel-free — `HealthReport`/`PoolState` must be too), D-13 (`/api/health` is a
  published one-way contract; pool fields nest under `pool`).
- `.planning/phases/03-structured-logging-at-the-composition-boundary/03-CONTEXT.md` —
  D-17 (typed, intent-named signatures over dict assembly — the same stance this phase
  takes with the response), the `test_calc_module_stays_log_free` belt pattern D-12
  copies.

### Code this phase edits or reads
- `src/spur/calc.py` — `derive()` (lines 163–232), `with_mate()` (256–272, deleted),
  `Profile` (the frozen-dataclass neighbour), `r3()`, `root_fillet()`/`recess_fillet()`
  (the two unrounded values), the `TYPE_CHECKING` guard on `GearParams`.
- `src/spur/app.py` — `_BlobCache` (57–75), `InfoQuery`/`ModelQuery` (201–208),
  `health()` (272–310, docstring paragraph on `pool` absence), `schema()` (314),
  `info()` (319–323).
- `src/spur/params.py` — `_f()` (16–22): the `Field` wrapper and the
  `title`/`unit`/`json_schema_extra` convention D-03 copies.
- `src/spur/cli.py` — `_add_gear_args` (`kw`), `cmd_info` (`json.dumps`), `cmd_export`
  (`derive(p)["warnings"]`).
- `src/spur/pool.py` line 153 — `_run_with_timeout`'s `Callable[..., bytes]`.
- `src/spur/static/app.js` — `DIMS` (lines 13–28), `renderInfo()` (127–142): the 17
  keys the UI reads by name.
- `tests/test_calc.py` (`test_default_dimensions`, the `kw: dict[str, Any]`
  parametrizations at 79/137, `with_mate` at 143), `tests/test_api.py`
  (`test_info_with_mate`, the `422` tests, `_field` at 327, the module-level bare
  `TestClient` that D-06 affects), `tests/test_cli.py`
  (`test_info_reports_the_mate_it_was_asked_about`), `tests/test_model.py:28`,
  `tests/test_records.py::test_calc_module_stays_log_free` (the belt pattern),
  `docker/smoke.py` (26/29).

### Milestone context
- `.planning/REQUIREMENTS.md` — REQ-typed-derived-dimensions and its acceptance;
  REQ-three-interfaces' "acceptance: absent" note that D-13 closes.
- `.planning/ROADMAP.md` §Phase 4 — the four success criteria.
- `.planning/PROJECT.md` §Success Metric #2 — "`disallow_any_explicit` on … retired
  rather than re-deferred".

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Profile` (`calc.py`) — the frozen-dataclass-next-to-its-builder pattern
  `DerivedDimensions` sits beside; `derive()` already computes every value it needs
  before assembling the dict, so the constructor call is a rename of the return.
- `GearParams._f()` (`params.py`) — the `title`/`description`/`json_schema_extra`
  convention D-03 mirrors on the output side; becoming generic also fixes three of the
  22 errors.
- `pydantic.mypy` plugin — already on; `py.typed` already shipped; a frozen `BaseModel`
  with `ConfigDict(frozen=True)` is exactly `GearParams`'s shape.
- `tests/test_records.py::test_calc_module_stays_log_free` — the regex-belt pattern
  D-12 copies against `app.js`.
- `tests/test_api.py::test_info_with_mate`, the `422` tests, and
  `tests/test_cli.py::test_info_reports_the_mate_it_was_asked_about` — the existing
  by-name reads; D-13's equivalence test is a combination of the last two.
- FastAPI's return-annotation → `response_model` inference — `-> DerivedDimensions` and
  `-> HealthReport` are enough for `/openapi.json` to gain the components; no
  `response_model=` argument needed.

### Established Patterns
- Module boundaries are enforced by import-linter contracts. `calc.py` may import
  pydantic (it already depends on `GearParams` at runtime); it may not import
  `cadquery`, `OCP`, `logging` or `spur.records`. Nothing here needs a new contract.
- Vendor types stop at their boundary — pydantic is the project's own contract layer
  (L01), so a `BaseModel` crossing `calc → app/cli` is not a vendor leak; `cq` objects
  still stop at `model.py`.
- Every knob and every deliberate oddity carries its reason in a comment: the rewritten
  `[tool.mypy]` comment, the `health()` null paragraph and the two newly rounded fillets
  all need one.
- Tests are named as requirements; the three new tests (D-11–D-13) follow suit.
- `pytest` runs with `filterwarnings = error` — a pydantic deprecation warning from the
  model definition (e.g. a wrong `json_schema_extra` type) fails the suite.
- TDD RED evidence is verified by inspecting pytest output, not `gsd_run check
  tdd-red-evidence` (Phase 3 finding).

### Integration Points
- `calc.derive()` → `app.info()`, `cli.cmd_info()`, `cli.cmd_export()` (`.warnings`).
- `app.health()` → Docker `HEALTHCHECK` and `tests/test_api.py:41` read `status` only.
- `app.schema()` → `app.js buildForm()` reads `properties`; document unchanged.
- `/openapi.json` → D-11's test; nothing else in the repo reads it today.
- `pyproject.toml [tool.mypy]` → `make typecheck` → `make verify` → pre-commit and CI.
- `docs/` (D-15), `decision_log.md` (D-14), `docs/tech_debt/` (D-16).

</code_context>

<specifics>
## Specific Ideas

- The exact command that defines "done" for the ratchet, run before and after:
  `.venv/bin/mypy --disallow-any-explicit src tests docker bench` — 22 errors / 9 files
  at `538d26f`, must read 0.
- The 17 keys the UI reads, from `app.js` `DIMS` + `renderInfo()`: `pitch_d`, `tip_d`,
  `caliper_over_tips`, `span`, `span_teeth`, `root_d`, `base_d`, `tip_thickness`,
  `root_thickness`, `root_gap`, `root_fillet`, `bore_effective`, `recess_id`,
  `recess_od`, `recess_fillet`, `web`, `centre_distance`, plus `warnings`. Every one is a
  `DerivedDimensions` field under the same name.
- Target `spur info` output without a mate (D-01): today's document plus
  `"mate_teeth": null, "centre_distance": null`; with a mate, unchanged.
- `test_default_dimensions`'s pinned values are the L05 tripwire: `13.013`, `25.013`,
  `0.5`, `33.25`, `36.75`, `28.875`, `3.5` do not move. `recess_fillet` is `0.5` both
  raw and rounded, so D-10 leaves this test untouched.
- The stale pointer at `pyproject.toml:93` (`typed-info-contract.md` for
  `untyped-info-contract.md`) disappears with the comment block, not as a separate fix.

</specifics>

<deferred>
## Deferred Ideas

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

</deferred>

---

*Phase: 4-Typed Derived-Dimensions Contract*
*Context gathered: 2026-09-24*
