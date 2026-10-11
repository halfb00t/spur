# Phase 23: Conditional Form Fields - Research

**Researched:** 2026-10-11
**Domain:** schema-carried field relations (Pydantic `json_schema_extra`) rendered by a vanilla-JS form; kernel-free proof against `calc.derive()`; Playwright proof of the dim state
**Confidence:** HIGH (every load-bearing claim was either read in the live tree this session or run this session)

Tags used below: `[VERIFIED: ...]` = read or run this session (MEASURED / READ in the milestone research files' sense);
`[CITED: url]` = official docs; `[ASSUMED]` = not verified (all collected in the Assumptions Log).

<user_constraints>
## User Constraints (from CONTEXT.md)

Copied from `23-CONTEXT.md`. The bold decision statements are verbatim; the "Rejected: ..." rationale
sentences are not repeated here, they live in CONTEXT.md and bind equally.

### Locked Decisions

- **D-01:** **A bare JSON list of `{field, op, value}` objects; the list is the AND.**
  `"enabled_when": [{"field": "bore_hex", "op": "eq", "value": 0}]`. No wrapper object, no `all`/`any`, no
  JSON-Schema-flavoured fragment. (`model_json_schema()` key-sorts object keys and keeps list order; nothing in
  the grammar depends on either.) Reversibility: costly (Phase 24's selector options are written in this vocabulary).
- **D-02:** **Operators: `eq` and `gt` only.** A relation that needs `ne`, `ge`, `lt` or an OR is a stop-and-ask
  for the human (PITFALLS CF-3). Both evaluators (JS and the test's Python one) reject an unknown op loudly.
- **D-03:** **`value` is a number; `field` names a numeric `GearParams` field.** No string values, no `Literal`
  drivers. The JS compares `Number(effective(field))`; the model-driven test rejects a string value or a
  non-numeric driver.
- **D-04:** **A typed `when()` helper plus the model-driven walk catch a malformed relation.**
  `when(field: str, op: Literal["eq", "gt"], value: float) -> JsonDict` in `params.py`;
  `_f(..., enabled_when=[when("bore_hex", "eq", 0)])`. The walk (`test_relations.py`, D-13) proves every `field`
  is in `model_fields` and numeric, `op` is in the set, `value` is a number, no dependent is also a driver
  (depth 1), and the schema emits the list unchanged.
- **D-05:** **One neutral wording for both classes; no class marker in the metadata.** No second
  `json_schema_extra` key; the keyword-collision test covers the one key `enabled_when`.
- **D-06:** **Wording: `Needs {gate title} = 0` for `eq 0`, `Needs {gate title} above 0` for `gt 0`; several
  conditions join with ` and `.** `Needs Hex bore A/F = 0` on `bore_d`, `bore_flat`, `keyway_width`,
  `keyway_depth`; `Needs Spoke arms above 0` on `spoke_width`, `hub_d`, `rim_wall`, `spoke_fillet`;
  `Needs Lightening holes above 0` on `hole_d`, `hole_circle_d`; `Needs Honeycomb cell A/F above 0` on
  `hex_wall`. Built from the schema's `title` and the relation, nothing hard-coded.
- **D-07:** **The reason renders in its own `<span class="reason">` inside the label wrapper, filled and visible
  only while `.field.inactive`, linked by `aria-describedby`.** The help `<small>` keeps its
  hidden-until-`:focus-within` rule.
- **D-08:** **One tone: `.field.inactive` only.** No second class for an inactive field that holds a non-default value.
- **D-09:** **The roadmap's set, unchanged.** `bore_d`, `bore_flat` <- `bore_hex eq 0`; `spoke_width`, `hub_d`,
  `rim_wall`, `spoke_fillet` <- `spoke_count gt 0`; `hole_d`, `hole_circle_d` <- `hole_count gt 0`; `hex_wall`
  <- `hex_cell gt 0`; `keyway_width`, `keyway_depth` <- `bore_hex eq 0` (the refused class, each alone a 422,
  never gated on each other). Every driver is a pure driver (depth 1). A row that fails the parity proof is
  dropped with its reason recorded, never declared on a guess.
- **D-10:** **The parity test proves the forward direction and reverse coverage.** Forward: per declared row, with
  the relation false, changing the dependent changes nothing in `derive()` except `warnings` (for the keyway pair
  under hex, `GearParams` construction raises naming `bore_hex`, `keyway_width`, `keyway_depth`), and the test
  was seen red against a deliberately wrong relation. Reverse coverage: no numeric field outside the declared
  dependents is ever named by a `derive()` "ignored" sentence (each undeclared field set off-default alone,
  under defaults).
- **D-11:** **Each dependent is perturbed at its two bounds: `ge + step` and `le`.** Two `derive()` calls per
  dependent, kernel-free.
- **D-12:** **The proofs are kernel-free and live in a new `tests/test_relations.py`, in the commit slice
  (`make verify.fast`).** One module for the walk (D-04), the calc parity rows (D-10, D-11), and the test that
  `enabled_when` is in no JSON Schema 2020-12 vocabulary (a static keyword list in the test).
  `tests/test_cli.py`'s `test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order` gains only the
  check that `/api/schema` emits each relation unchanged; `tests/test_api.py`'s `test_schema_drives_the_form`
  gains one relation assertion.
- **D-13:** The file is light by construction: it imports `spur.params` and `spur.calc`, never `cadquery`,
  `TestClient` or `playwright`.
- **D-14:** **The expected inactive set comes from a Python evaluator over `/api/schema`, in the test.** About ten
  lines in `tests/browser_session.py`; model-driven, names no field. A committed `golden_inactive.json` and
  hand-listed expected sets are rejected.
- **D-15:** **Beyond the 44 golden sets, one model-driven flip link per distinct gate condition.** For each
  distinct `{field, op, value}` gate in the schema, derive a link setting that gate to an in-range value that
  flips it (four links today, none named in the test). The server may answer 422; the dim state is independent of
  the response and the test says so in its assertion message. Plus the roadmap's `#spoke_count=0&hub_d=40`.
- **D-16:** **`sweep()` reads the inactive set in the same pass; one new step `inert fields` after `golden
  sweep`.** The `golden sweep` step compares both the query (the unchanged pin) and the inactive set. The new step
  holds the flips, the `hub_d=40` link, the reason text, and the `input` and Reset paths. One function, one server.
- **D-17:** **"Still a field" is proved by a real keystroke into the dimmed field.** Load
  `#spoke_count=0&hub_d=40`: `hub_d` is `.inactive`, holds 40, the sent query is `hub_d=40`, the reason reads
  `Needs Spoke arms above 0`. `fill` `hub_d` with another value: the next `api/info` request carries it and
  `hub_d` is still `.inactive`. Type a non-zero count into `spoke_count`: `hub_d` loses `.inactive` before the
  350 ms debounce fires. Click Reset: the inactive set is the default one (the seven cutout dims).
- **D-18:** **The evaluator reads the same effective value `gearQuery()` sends:** an emptied number box
  (`input.value === ''`) reads as the schema default.
- **D-19:** **`applyRelations()` is one function called from the end of `readHash()` (fresh load and
  `hashchange`), from the form `input` listener before `scheduleUpdate`, and from the `#reset` handler** - never
  hung on a successful build. A gate named in a relation but absent from `fields` is a red walk (D-04), not a
  silent no-op.
- **D-20:** **Drivers are never dependents and the form never dims a driver.** The cutout "pick one" mutual
  exclusion stays the server's 422.

### Claude's Discretion

- The hex-warning debt file's severity and trigger (recommendation in CONTEXT: `nice`; trigger "Phase 24's
  selector ships ... or a user reports the warning as noise"; never fixed here, never filtered in `app.js`).
- Whether `.invalid` and `.inactive` coexist on the keyway pair under hex (recommendation: they coexist;
  `problems()` adds `.invalid`, `applyRelations()` owns `.inactive`, neither clears the other; `.invalid` gets
  the stronger mark).
- The gate-cost reading for the new step (22 D-06's pattern: three readings with host state under
  `## Conditional form fields (Phase 23)` in `bench/RESULTS.md`; no full-gate A/B).
- How the two bare-`Field` `Literal` fields carry the key (one shared path for the extra; a test proves a
  `Literal` field given `enabled_when` emits it unchanged).
- The dim visual (opacity on the whole label versus the control only; the muted colour token) and the `.reason`
  span's typography - within the existing custom properties.
- The exact token the `fields.set(name, { input, wrap, title })` pin is rewritten to (stricter, under L41; no new
  JS table of the `['word',` shape).
- The deliberately-wrong-relation evidence (a monkeypatched relation seen red once, recorded in the SUMMARY).
- L41's text (supersedes 08 D-09, keeps L02, names the grammar, the declared set, the reason rule, the pins it
  rewrites and the two files it files; L39/L40's paragraph shape).

### Deferred Ideas (OUT OF SCOPE)

- `keyway_* <- bore_d gt 0` (the "keyway needs a round bore" 422 as a second condition) - not declared.
- Refused-vs-inert styling and a class marker in the metadata.
- The two unbacked relations (`recess_*` under `recess_sides=none`, `bore_flat` at `bore_d=0`) with a `calc`
  warning first - this phase files the idea, does not declare them.
- The hex warning on default `bore_d`/`bore_flat` - this phase files the debt; a `calc` change, never filtered
  in `app.js`.
- Cutout "pick one" lock.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-enabled-when-metadata | `_f()` accepts `enabled_when` in `json_schema_extra`, emitted unchanged; the two bare-`Field` `Literal` fields carry it the same way; project-defined AND-only grammar; keyword-collision test | Emission measured (nested list of dicts, key-sorted, list order kept, both construction styles); `mypy --strict` invariance trap and its fix; JSON Schema 2020-12 keyword list for the collision test; shared `_extra()` builder for the two `Literal` fields |
| REQ-relations-calc-backed | every declared relation is one `calc` backs; parity test goes red on drift; keyway pair is the refused class | Parity run over all 11 dependents at both bounds (all `{warnings}`-only); keyway 422 measured alone/both/at bounds; reverse-coverage run over every numeric field; the derive-invariance proof is necessary but not sufficient (`bore_chamfer` counter-example), so the warning-names check is added |
| REQ-dim-and-editable | `.field.inactive`, reason from the gate's `title`, editable, value kept, still sent; re-evaluated on `input`, `readHash`, Reset, `hashchange` | Draft `applyRelations()` pin-checked against the live `app.js` pins; call-site map; CSS/opacity vs `.invalid` pitfall; same-task read for "before the debounce"; Playwright shape |
| REQ-form-walk-proves-relations | model-driven walk extends to every relation; browser test asserts dim state under the golden sets; `test_api.py` pins tightened under one `Lxx` | Golden fixture measured (no record sets a gate); sweep return-shape change and its second consumer; the three `app.js` pins (not two) and what each needs; `['word',` harvest-safe JS shapes |
</phase_requirements>

## Summary

The phase is small in code and large in proof. Production change: one `when()` helper, one `_extra()` builder
shared by `_f()` and the two `Literal` `Field(...)` calls, eleven `enabled_when=[...]` keywords in `params.py`;
about forty lines of generic JS in `app.js` (`effective`, `holds`, `applyRelations`, a `reason` span per field);
two CSS rules. Everything else is tests, one `Lxx`, two ledger files and one retirement. No `calc`, `model`,
`pool`, `app.py` or `cli` edit is needed, and the two regression files cannot move because `gearQuery()` is not
touched. [VERIFIED: read params.py, app.js, calc.py, app.py this session]

Every CONTEXT assumption that could be run was run. The declaration compiles under `mypy --strict`
(with `list(enabled_when)`, see Pitfall 1) and emits exactly the shape D-01 wants; the parity table is green for
all eleven dependents at both bounds; the keyway pair is a 422 alone, together and at bounds, each time naming
`bore_hex`, `keyway_depth`, `keyway_width`; the reverse-coverage scan finds "ignored" sentences naming only
declared dependents; a draft `applyRelations()` passes every existing `app.js` pin except the one token CONTEXT
already says is rewritten. The research also found three things CONTEXT does not name: the forward
derive-invariance proof alone would accept a wrong relation (`bore_chamfer` under a hex bore changes nothing in
`derive()`, not even `warnings`), `tests/test_api.py` has a *third* `app.js` pin (a `gearQuery()` token in the
`root_shape` test, around line 395), and `sweep()` has a second consumer (`tests/capture_requests.py`) that its
return-type change would break.

**Primary recommendation:** Land it in four commits-worth of plans in this order - (1) model + kernel-free
proofs, (2) `app.js`/CSS + the `test_api.py` pin rewrite + L41 (one commit, because the pin and the JS cannot be
green apart), (3) browser proof, (4) docs, ledger, bench reading - and add one check to D-10's forward proof
beyond derive-invariance: with the relation false, the "ignored" warning must name the dependent at the
perturbed value.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Declaring which fields a gate makes inert | API / Backend (the Pydantic model, `params.py`) | - | The model is the one source of field metadata (L02); the relation is a second statement of a rule `calc` owns, so it lives beside the field, not in the UI |
| Carrying the relation to clients | API / Backend (`/api/schema`, unchanged route) | - | `app.py:373-375` returns `GearParams.model_json_schema()` untransformed [VERIFIED: app.py:373-375 read] |
| Proving relation == calc behaviour | API / Backend tests (kernel-free, `derive()` / `GearParams(...)`) | - | `derive()` is the authority on "ignored"; no browser, no kernel needed |
| Evaluating a relation over current form values | Browser / Client (generic JS in `app.js`) | - | Only the form knows the unsent, unvalidated values; evaluation must read the same effective value `gearQuery()` sends |
| Rendering dim + reason | Browser / Client (CSS class + `<span class="reason">`) | - | Pure presentation; the server's warning / 422 stays the authority |
| Deciding what a field *means* when inert (ignored vs refused) | API / Backend (`calc.derive` warning / `check()` 422) | - | The UI makes no claim beyond "needs X"; D-05 |
| Proving the dim state in a real page | Browser test (`tests/browser_session.py` + `test_browser.py`) | - | Second, independent Python evaluator over `/api/schema` (D-14) |

## Standard Stack

### Core (all already in the tree; nothing is installed)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pydantic | 2.13.5 [VERIFIED: `.venv/bin/python -c "import pydantic;print(pydantic.VERSION)"`] | `json_schema_extra` carries the relation; `pydantic.config.JsonDict` types it | Already the model layer; emission measured below |
| pytest | pinned in `pyproject.toml` (suite ran: 840 passed) | `tests/test_relations.py` | The existing runner; `filterwarnings = ["error", ...]` applies |
| playwright | 1.63.0 [VERIFIED: pyproject.toml:29 `"playwright==1.63.0"`; `.venv/bin/pip list`] | the extended browser scenario | Phase 21's pinned closure |
| vanilla JS | - | `applyRelations()` | L11: the runtime needs no Node; no JSON-Schema evaluator exists or is needed in the browser |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| bare list of `{field, op, value}` | JSON Schema `if`/`then`/`dependentSchemas` | Nothing client-side evaluates them; locked out by D-01 anyway [CITED: STACK.md, this milestone] |
| `jsonschema` lib for the collision test | a static keyword list in the test | `jsonschema` is not installed in `.venv` [VERIFIED: `import jsonschema` -> ModuleNotFoundError]; D-12 chose the static list |

**Installation:** none. No package is added by this phase.

## Package Legitimacy Audit

No external package is installed or added to any requirements file by this phase, so the legitimacy gate has
nothing to evaluate.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| (none) | - | - | - | - | - | - |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
 DECLARATION (build time)                      PROOF (commit slice, kernel-free)
 params.py                                     tests/test_relations.py
 _f(..., enabled_when=[when("bore_hex","eq",0)])    walk model_fields / schema  --> grammar well-formed, depth 1
 Field(... json_schema_extra=_extra(...))  x2       keyword list                --> key collides with no 2020-12 word
        |                                           derive()/GearParams()        --> relation false => only `warnings`
        v                                                                           moves (or 422 naming gate+dependent)
 GearParams.model_json_schema()                     derive().warnings           --> "ignored" sentence names dependent
        |                                           reverse scan                 --> no undeclared field is ever "ignored"
        v
 GET /api/schema  (app.py:373, unchanged)
        |
        v   RUNTIME (browser)
 buildForm(): per property -> fields.set(name, { input, wrap, title, rels, reason })
        |
        |  readHash() end ----------------+      (fresh load, hashchange)
        |  form 'input' listener ---------+--> applyRelations()  -- reads effective(gate) = input.value || default
        |  #reset handler ----------------+        |
        v                                          v
 update() -> /api/info, /api/model.stl     label.field.inactive + span.reason text + aria-describedby
 (gearQuery() UNCHANGED: still sends every   (never `disabled`, never hidden, value kept)
  non-default value, inactive or not)

 BROWSER PROOF (gate, not commit slice)
 sweep(): for each of 44 hashes -> sent query (== golden pin)  AND  inactive names (== python evaluator over /api/schema)
 "inert fields" step: 4 model-derived flip links, #spoke_count=0&hub_d=40, fill into dimmed field, Reset
```

### Recommended Project Structure

```
src/spur/params.py            # when(), _extra(), enabled_when keyword on _f(); 11 declarations
src/spur/static/app.js        # effective(), holds(), applyRelations(), reason span; +3 call sites
src/spur/static/style.css     # .field.inactive, .field .reason
tests/test_relations.py       # NEW, commit slice: walk, keyword collision, parity, reverse coverage, meta-red
tests/test_api.py             # pins tightened under L41; test_schema_drives_the_form +1 assertion
tests/test_cli.py             # model-driven walk +1 check (heavy tier)
tests/browser_session.py      # sweep() returns query + inactive set; python evaluator; flip-link derivation
tests/test_browser.py         # golden sweep compares both; new step `inert fields`
tests/capture_requests.py     # 1-line adaptation to sweep()'s new return shape
docs/architecture/decision_log.md  # L41
docs/architecture/web-ui.md        # relation paragraph (replaces "knows no gear geometry" bullet's silence)
docs/ideas/ , docs/tech_debt/active/ , bench/RESULTS.md
```

### Pattern 1: one extra-builder for both construction styles (REQ-enabled-when-metadata)

**What:** `_f()` builds `extra` inline; `root_shape` (`params.py:59-65`) and `recess_sides` (`:102-104`) hand-write
`json_schema_extra={"group": ..., "unit": ""}`. A relation added only to `_f()` is silently dropped for the two
`Literal` fields (CF-3). Factor the `extra` construction into one private function and have all three call it.
**When to use:** any field that may carry `group`/`unit`/`step`/`enabled_when`.
**Example** (prototype, run under `mypy --strict --config-file pyproject.toml`: "Success: no issues found"):

```python
# Source: scratchpad prototype run this session against the project's mypy config
def when(field: str, op: Literal["eq", "gt"], value: float) -> JsonDict:
    return {"field": field, "op": op, "value": value}

def _extra(group: str, unit: str = "", step: float | None = None,
           enabled_when: list[JsonDict] | None = None) -> JsonDict:
    extra: JsonDict = {"group": group, "unit": unit}
    if step is not None:
        extra["step"] = step
    if enabled_when is not None:
        extra["enabled_when"] = list(enabled_when)   # NOT `= enabled_when`: Pitfall 1
    return extra
```

`_f(...)` then calls `json_schema_extra=_extra(group, unit, step, enabled_when)`; the two `Literal` fields pass
`json_schema_extra=_extra("Teeth")` / `_extra("Recess")`, which reproduces today's `{"group": g, "unit": ""}`
exactly. Measured emission for a field with two conditions and for a `Literal` field with one:

```
{"default": 0.0, "description": "", "enabled_when": [{"field": "a", "op": "gt", "value": 0}, {"field": "c", "op": "eq", "value": 0}], "group": "g", "maximum": 3, "minimum": 0, "title": "B", "type": "number", "unit": ""}
{"default": "x", "enabled_when": [{"field": "a", "op": "eq", "value": 0}], "enum": ["x", "y"], "group": "g", "title": "S", "type": "string", "unit": ""}
```
[VERIFIED: ran the prototype, pydantic 2.13.5]. Object keys are sorted (`field, op, value`), list order is kept,
`0` stays the int `0`.

### Pattern 2: the generic evaluator and `applyRelations()` (REQ-dim-and-editable)

**What:** relations are stored per field at `buildForm()` time; one function re-derives every field's class.
**Example** (draft; pin-checked, see "Verified facts" below):

```js
/** The value gearQuery() would send: an emptied number box reads as its default (D-18). */
const effective = (name) => {
  const { input } = fields.get(name);          // an absent gate throws here: loud, not a silent no-op (D-19)
  return input.value === '' ? defaults[name] : input.value;
};

function holds({ field, op, value }) {
  const have = Number(effective(field));
  switch (op) {                                 // a switch, not a table: Pitfall 5
    case 'eq': return have === value;
    case 'gt': return have > value;
    default: throw new Error(`unknown enabled_when op: ${op}`);
  }
}

const need = ({ field, op, value }) =>
  `${fields.get(field).title} ${op === 'eq' ? `= ${value}` : `above ${value}`}`;

function applyRelations() {
  for (const { input, wrap, rels, reason } of fields.values()) {
    const off = !rels.every(holds);             // [] -> every() is true -> never inactive (drivers, selects)
    wrap.classList.toggle('inactive', off);
    reason.textContent = off ? `Needs ${rels.map(need).join(' and ')}` : '';
    if (off) input.setAttribute('aria-describedby', reason.id);
    else input.removeAttribute('aria-describedby');
  }
}
```

`buildForm()` creates `reason = Object.assign(document.createElement('span'), { className: 'reason', id:
\`reason-${name}\` })`, appends it between `control` and the help `<small>`, and stores
`fields.set(name, { input, wrap, title, rels: prop.enabled_when ?? [], reason })`. `readHash()` ends with
`applyRelations();`, the form listener becomes `() => { applyRelations(); scheduleUpdate(); }`, and `#reset`
calls `applyRelations()` after resetting values and before `update()`. The `hashchange` line
`window.addEventListener('hashchange', () => { readHash(); update(); });` is itself pinned verbatim and must not
change; `applyRelations()` rides inside `readHash()`. `gearQuery()` is not edited.

### Pattern 3: the parity proof, with the extra check (REQ-relations-calc-backed)

Read bounds from the *schema* the form sees (`prop["minimum"]`, `prop["maximum"]`, `prop["step"]`), not from
pydantic metadata. For each relation row: close the gate (a value for which the first condition does not hold),
build the baseline, perturb the dependent at `minimum + step` and `maximum`, and:

```python
base = derive(GearParams(**gate)).model_dump()
for value in (lo + step, hi):
    assert value != prop["default"]                      # a no-op perturbation proves nothing
    try:
        p = GearParams(**gate, **{dep: value})
    except ValidationError as e:                         # refused class
        ctx = e.errors()[0]["ctx"]["fields"]             # ['bore_hex', 'keyway_depth', 'keyway_width'] (measured)
        assert {driver, dep} <= set(ctx)
    else:                                                # inert class
        doc = derive(p).model_dump()
        assert {k for k in doc if doc[k] != base[k]} == {"warnings"}
        assert f"{dep} ({value:g} mm)" in " ".join(doc["warnings"])   # the extra check
```

Classify rows by *outcome*, and pin the refused set as a literal frozenset in the test (`{"keyway_width",
"keyway_depth"}`) so a row that silently changes class goes red. Why the extra `ignored`-names check: Pitfall 2.

### Anti-Patterns to Avoid

- **`disabled` / `hidden` / clearing the value** on an inert field: a `#spoke_count=0&hub_d=40` link would load a field the user cannot clear (REQ-dim-and-editable, ARCH 4.3).
- **Hanging `applyRelations()` on a successful build** (`renderInfo`/`showModel`): a 422 would leave the previous state (CF-4).
- **Filtering the hex warning in `app.js`** to hide the `bore_d`/`bore_flat` noise: it is `calc` debt, filed not fixed.
- **A table of rows for operators** (`[['eq', ...]]`): trips the `['word',` DIMS harvest (Pitfall 5).
- **Editing `tests/regression/*.json`** to make a test green: the diff must be empty after every task.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON Schema keyword list for the collision test | A guessed list | The 2020-12 vocabulary list in "Code Examples" below, cited | A wrong list passes the test and still collides later |
| Perturbation bounds | Hard-coded `0.05` / `200` per field | `minimum`, `maximum`, `step` from `GearParams.model_json_schema()` | New relations get proved with no test edit (model-driven, D-14's spirit) |
| Flip-link derivation | A hand-listed link per gate | Derive from each distinct gate in the schema | A fifth relation adds its own link with no test edit (D-15) |
| Inactive-set prediction | A committed `golden_inactive.json` | A ~10-line Python evaluator over `/api/schema` (D-14) | A committed set pins the JS against itself |
| Re-implementing `check()` in JS | A client copy of "keyway needs a round bore" etc. | The server's 422 + `.invalid` mark (already there) | A second statement of the rule drifts |

**Key insight:** the relation is already a second statement of rules `calc` owns. The only defence is a
proof that is cheap, runs at commit, and fails on drift in both directions - so every shortcut that makes the
proof weaker (derive-invariance alone, hand-listed rows) is the one to refuse.

## Verified facts (CONTEXT claims re-checked against the live tree)

| Claim | Result |
|-------|--------|
| `_f()` at `params.py:17-23`, `root_shape` `:59`, `recess_sides` `:102` | Confirmed [VERIFIED: params.py read]. `root_shape` / `recess_sides`: `json_schema_extra={"group": "Teeth", "unit": ""}` and `{"group": "Recess", "unit": ""}` |
| `/api/schema` unchanged | `@app.get("/api/schema") def schema() -> JsonSchemaValue: return GearParams.model_json_schema()` [VERIFIED: app.py:373-375] |
| `check()` skips the dependent with the gate closed | `elif p.spoke_count > 0:` (`calc.py:781`), `elif p.hole_count > 0:` (`:836`), `elif p.hex_cell > 0:` (`:878`), hex branch `if p.bore_hex > 0:` (`:669`, with the comment "so bore_d and bore_flat are not checked here"). CONTEXT's "`:781` and `:836`" is right; `:878` is the honeycomb branch it omits [VERIFIED: calc.py read] |
| keyway x hex refusal | `has_keyway = p.keyway_width > 0 or p.keyway_depth > 0` (`:652`); the refusal text is `"A keyway cannot be cut into a hex bore: set bore_hex to 0 for a keyed round or D-flat bore, ..."` with fields `("bore_hex", "keyway_depth", "keyway_width")`. CONTEXT cites `:653-657`; the block starts at `:652` (cosmetic drift) [VERIFIED: calc.py:652-660] |
| the four "ignored" sentences | `:1159` hex, `:1207` spokes, `:1220` holes, `:1231` honeycomb (`if p.hex_cell > 0:` ... `else: ... if p.hex_wall > 0:`). CONTEXT's `:1241-1247` is the honeycomb sentence inside that else-branch [VERIFIED: calc.py read] |
| `app.js` anchors | `fields.set(name, { input, wrap, title });` at `:92`; `readHash` `:96`; `gearQuery` `:103`; `problems` `:121`; `update` `:176`; `form.addEventListener('input', scheduleUpdate);` `:340`; `hashchange` `:342`; `#reset` `:347` [VERIFIED: app.js read] |
| Fixture sets no gate field | Of 44 records in `pre_v0_2.json`, none carries `bore_hex`, `spoke_count`, `hole_count` or `hex_cell`; none carries any of the 7 cutout dims; 14 carry `bore_d` and/or `bore_flat` (always with `bore_hex` unset). So under every golden set the inactive set is `{spoke_width, hub_d, rim_wall, spoke_fillet, hole_d, hole_circle_d, hex_wall}` [VERIFIED: ran a script over `tests/regression/pre_v0_2.json`; 44 records in `golden_requests.json` too] |
| `test_hooks.py` heavy list | `HEAVY_TEST_FILES = ("test_model", "test_pool", "test_api", "test_cli", "test_browser")` (`:24`); `test.fast` excludes by `--ignore`, so a new `tests/test_relations.py` joins the commit slice automatically [VERIFIED: test_hooks.py:24, Makefile `test.fast` read] |
| next free Lxx | `decision_log.md` last heading is `## L40 — The download name carries the root ...` (`:2451`) so L41 is next [VERIFIED: grep of `^## ` headings] |

### Drift in CONTEXT.md references (all minor)
- CONTEXT lists two `test_api.py` pins to tighten; there is a **third** `app.js` pin: in the `root_shape` test (`test_api.py` ~`:393-396`), `assert ("if (input.value !== '' && String(input.value) !== String(defaults[name])) " "q.set(name, input.value);") in source`. It pins `gearQuery()` byte for byte (whitespace-collapsed). It needs no change - this phase must not touch `gearQuery()` - but the planner must know it exists so no refactor of `gearQuery()` is smuggled in. [VERIFIED: test_api.py:393-396 read]
- `tests/test_browser.py` anchors (`:258`, `:527`, `:558`, `:585`) and `browser_session.py` (`fixture_hashes :318`, `sweep :339`) are exact [VERIFIED].

## Runtime State Inventory

Not a rename/refactor/migration phase (a new metadata key and a new CSS class). Omitted by design; nothing stored,
registered or cached embeds a renamed string. The one persisted artifact that could move is
`tests/regression/golden_requests.json`; it cannot, because `gearQuery()` is untouched.

## Common Pitfalls

### Pitfall 1: `extra["enabled_when"] = enabled_when` fails `mypy --strict`
**What goes wrong:** `list[JsonDict]` is not assignable to `JsonValue` by list invariance.
**Measured:** `error: Incompatible types in assignment (expression has type "list[JsonDict]", target has type "JsonValue")  [assignment]`; `extra["enabled_when"] = list(enabled_when)` -> "Success: no issues found" [VERIFIED: ran mypy with the project config on a scratch module].
**How to avoid:** copy through `list(...)` as in Pattern 1. Do not add a `# type: ignore` (no `Any`, no suppressions in this codebase, L21).

### Pitfall 2: derive-invariance alone does not prove a relation (the forward proof is necessary, not sufficient)
**What goes wrong:** `derive()` reports numbers, not geometry. `bore_hex=6` with `bore_chamfer=1.0` changes **nothing** in `derive()` - not even `warnings` (MEASURED: changed keys `[]`) - though the chamfer does shape the hex bore mouth (`calc.py` `bore_mouth_limit`). A wrong relation `bore_chamfer <- bore_hex eq 0` would pass D-10's forward check.
**How to avoid:** add the check that makes SC2's words true ("one `calc` already warns about"): with the relation false and the dependent at the perturbed value, an "ignored" warning names `dep (value mm)`. `bore_chamfer` fails it (no sentence). The refused class is covered by the 422 naming gate + dependent.
**Measured wrong-relation evidence for the SUMMARY** (use these, not invented ones): (a) `recess_depth <- bore_hex eq 0`: `derive()` changed `['web']` -> red on derive-invariance; (b) `bore_chamfer <- bore_hex eq 0`: no change -> red **only** on the warning-names check; (c) dropping the `spoke_fillet` declaration: its "ignored" sentence still fires (`"No spoke arms with spoke_count 0: spoke_fillet (0.05 mm) is ignored."`) -> red on reverse coverage [VERIFIED: ran all three].
**Make the evidence permanent:** structure the checker as a function taking the relation map, and add a test that feeds it (a) and (b) in a doctored copy of the schema and asserts it raises `AssertionError`. "Seen red once" then stays seen.

### Pitfall 3: the warning names the *other* field at its default
`bore_hex=0.05, bore_d=0.05` warns `"... bore_d (0.05 mm) and bore_flat (8 mm) are ignored."` - the unperturbed `bore_flat (8 mm)` is a default the user never set (PITFALLS M-7). Check membership of the exact `dep (value:g mm)` fragment, never equality of the whole sentence.

### Pitfall 4: `opacity` on the control also dims the `.invalid` outline
The keyway pair under `#bore_hex=6&keyway_width=3&keyway_depth=1.4` is both inactive and invalid (the 422 names `bore_hex`, `keyway_depth`, `keyway_width`). If the dim is `opacity` on `.field` or `.control`, the accent outline is dimmed too, defeating "`.invalid` gets the stronger mark". Dim `.name` and the input's colour/background through existing custom properties (`--muted`), or restore `.field.invalid .control { opacity: 1 }` after the inactive rule. `.reason` must not inherit the dim (D-07: it has to be readable). `pointer-events` must stay as is: Playwright `fill` and a real user both need the field live. [ASSUMED: Playwright's `fill` actionability checks visible/enabled/editable and an opacity < 1 element passes; the planned `inert fields` step is itself the test - A2]

### Pitfall 5: the `['word',` DIMS harvest and an operator table
`test_every_key_the_ui_reads_is_a_derived_dimensions_field` harvests every line matching `^\s*\['(\w+)',` (`test_api.py:133`) and requires each to be a `DerivedDimensions` field. A `Map` literal of rows such as `['eq', ...]` is read as a DIMS key and fails. Use the `switch` in Pattern 2 (draft harvest: 26 keys, unchanged). Do **not** write `OPS[op]` against a plain object either: `OPS['constructor']` resolves up the prototype chain and an unknown op would not throw. [VERIFIED: ran the existing regex over the draft `app.js`: 26 DIMS keys]

### Pitfall 6: `sweep()` has two callers, and its return type is a contract
`sweep()` returns `dict[str, str]` (name -> query); `tests/capture_requests.py` does `sent = sweep(...)`, `len(sent)`, and `json.dumps({"records": sent, ...})`. Returning `(query, inactive)` pairs breaks the regen script and would change what `make golden.regen` writes. Return a small `NamedTuple` (`query`, `inactive`) and adapt `capture_requests.py` in one line (`{n: s.query for n, s in swept.items()}`), then prove the pin is byte-identical: `make golden.regen && git diff --exit-code tests/regression/golden_requests.json` (the docstring states a regen on unchanged code is byte-identical; run it, do not commit it). `tests/test_browser_pins.py` AST-scans `tests/*browser*.py` and `capture_requests.py` for the names `importorskip, skip, skipif, xfail, pytestmark, getenv, environ`: never use `skip` (or any watched name) as an identifier in the new code [VERIFIED: test_browser_pins.py:46-49 read].

### Pitfall 7: reading the inactive set after the request is the right moment, and it is deterministic
`hashchange` runs `readHash()` (which now ends in `applyRelations()`) and then `update()`, which fires the fetch synchronously; `expect_request` returns after that, so a `page.evaluate` right after it reads the state for *this* link. Hang `applyRelations()` anywhere that runs after `await` and this guarantee goes away.

### Pitfall 8: "before the 350 ms debounce" cannot be proved by a late read
A class read 100 ms after `fill` is the same whether `applyRelations()` ran before or after `scheduleUpdate`'s timer. Prove it in one JS task: set the value, dispatch `input`, read the class in the same `page.evaluate` (no timer can fire in between). Keep the real-keystroke `fill` for the "still a field" half (D-17), where the proof is that the next `api/info` request carries the value.

### Pitfall 9: a fragment assigned after `goto("/")` can be erased
Phase 22 reproduced it (one lost in about a dozen runs): `buildForm()` can finish after the assignment and `readHash()` reads the empty hash. For `#spoke_count=0&hub_d=40` put the fragment on the `goto` URL, as the `download name` step does (`fresh.goto(server + "/#teeth=23&root_shape=trochoid")`). For links on an already-built page use the `hashchange` path (`_follow_link`), which needs the fragment to differ from the current one. [VERIFIED: test_browser.py `download name` step comment, read]

### Pitfall 10: Python-side reason text must format numbers like JS
JS renders `${value}` (`0` -> `0`). `json.loads` of `0.0` gives `0.0` -> `"0.0"`. Build the expected text with `f"{value:g}"`, and have the walk reject non-integer-valued gate values for the three `gt 0`/`eq 0` gates only if a future relation needs them (not needed today: all values are the int `0`).

### Pitfall 11: running the browser test outside `make`
The Makefile exports `PLAYWRIGHT_BROWSERS_PATH := $(abspath $(VENV))/ms-playwright` (`Makefile:28`). `pytest tests/test_browser.py` directly looks in `~/Library/Caches/ms-playwright`, finds revision 1243 missing and fails with `Executable doesn't exist` (reproduced). Targeted runs: `PLAYWRIGHT_BROWSERS_PATH=$PWD/.venv/ms-playwright .venv/bin/python -m pytest tests/test_browser.py --no-cov -s -q -p no:cacheprovider` (worked: 1 passed in 6.50 s) or `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"`.

### Pitfall 12: `.name` locators and the new `.reason` span
`test_browser.py` reads `label.field .name` for titles and `label.field.invalid .name` for marks. A `.reason` span is a separate class, so those locators are unaffected - but do not reuse the class `name`, and do not put the reason inside `.control` (the `.field` grid is `1fr 8.5rem`; the reason needs `grid-column: 1 / -1`).

### Pitfall 13: the `root_shape=bogus` debt trigger
`docs/tech_debt/active/2026-10-10-root-shape-bogus-loads-a-blank-select.md` fires when this phase touches `buildForm`'s enum rendering. This phase edits `buildForm()` but must not touch the `if (prop.enum) { ... }` branch (`app.js:66-69`). `applyRelations()` iterates `select` fields too, with `rels = []`, which is inert for them. Leave the branch alone and the `root_shape=bogus as today` step stays valid.

## Code Examples

### Keyword-collision test (REQ-enabled-when-metadata)

```python
# Source: https://json-schema.org/draft/2020-12/json-schema-validation and .../json-schema-core
# (core, applicator, unevaluated, validation, format, content, meta-data vocabularies) [CITED]
KEYWORDS_2020_12 = frozenset({
    "$id", "$schema", "$ref", "$anchor", "$dynamicRef", "$dynamicAnchor", "$vocabulary", "$comment", "$defs",
    "prefixItems", "items", "contains", "additionalProperties", "properties", "patternProperties",
    "dependentSchemas", "propertyNames", "if", "then", "else", "allOf", "anyOf", "oneOf", "not",
    "unevaluatedItems", "unevaluatedProperties",
    "type", "const", "enum", "multipleOf", "maximum", "exclusiveMaximum", "minimum", "exclusiveMinimum",
    "maxLength", "minLength", "pattern", "maxItems", "minItems", "uniqueItems", "maxContains", "minContains",
    "maxProperties", "minProperties", "required", "dependentRequired",
    "format", "contentEncoding", "contentMediaType", "contentSchema",
    "title", "description", "default", "deprecated", "readOnly", "writeOnly", "examples",
})
assert "enabled_when" not in KEYWORDS_2020_12            # and the draft-7 legacy words below
LEGACY = frozenset({"definitions", "dependencies", "additionalItems"})
```
Also assert that every key a field's `json_schema_extra` contributes (`group`, `unit`, `step`, `enabled_when`)
is outside `KEYWORDS_2020_12 | LEGACY`, so the *next* extra key added is checked too. Neither `enabled_when` nor
`enabledWhen` appears in either spec page [CITED: json-schema.org/draft/2020-12/json-schema-validation, fetched
this session; the core page was truncated at the applicator vocabulary, so `anyOf/if/then/else/dependentSchemas`
come from the validation spec's cross-reference list].

### Python evaluator for the browser test (D-14), names no field

```python
def _inactive(properties: dict[str, dict[str, object]], values: dict[str, str]) -> set[str]:
    def have(name: str) -> float:
        raw = values.get(name)
        return float(properties[name]["default"] if raw in (None, "") else raw)   # D-18
    out: set[str] = set()
    for name, prop in properties.items():
        for cond in prop.get("enabled_when", []):                                  # type-narrow in real code
            a, op, v = have(cond["field"]), cond["op"], cond["value"]
            if not (a == v if op == "eq" else a > v if op == "gt" else _unknown(op)):
                out.add(name)
    return out
```
(`_unknown` raises - D-02. Expected reason text: `"Needs " + " and ".join(f"{_title(properties, c['field'])} " + (f"= {c['value']:g}" if c["op"] == "eq" else f"above {c['value']:g}") ...)`.)

### Reading the inactive names in the page, names no field

```python
eval_str_list(page, "() => [...document.querySelectorAll('form#params label.field.inactive')]"
                    ".map(l => l.querySelector('[name]').name)")
```

### Flip links, model-derived (D-15)

For each distinct `(field, op, value)` over all `enabled_when` lists: candidates `[minimum + step, maximum]` from
`properties[field]`; take the first for which the evaluator's answer for that condition differs from its answer at
the schema default; link = `f"{field}={candidate}"`. Four links today (`bore_hex=0.05`, `spoke_count=1`,
`hole_count=1`, `hex_cell=0.05`); `bore_hex=0.05` answers 200 (measured), the others 422 (half-set cutouts) -
the dim state is independent of the answer.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| 08 D-09 "no conditional form behaviour"; ignored-field warnings are the only signal | schema-carried relation + generic dim (L41 supersedes 08 D-09, keeps L02) | this phase | The form says it before it is typed; the server's warning/422 stays the authority |
| Phase 12's reason for "not taken": no browser test | Phase 21's browser test (L39) exists | 2026-10-10 | The idea's own trigger has fired |

**Deprecated/outdated:** none relevant.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The core JSON Schema page was truncated at its applicator vocabulary; `anyOf`, `if`, `then`, `else`, `dependentSchemas` are taken from the validation spec's cross-reference list, which is the same vocabulary | Code Examples (keyword list) | A missing 2020-12 word in the static list; harmless for `enabled_when` (not a word in either page) but the "next extra key" check could miss a word. Low |
| A2 | Playwright 1.63 `fill` succeeds on a visible input whose ancestor has `opacity < 1` (actionability = visible + enabled + editable) | Pitfall 4 | The `inert fields` step fails at `fill`; fix is CSS only (do not use `pointer-events: none` or `visibility`). The step is the test |
| A3 | `bore_chamfer` shapes the hex bore mouth, so a relation gating it would be false | Pitfall 2 | Only the justification wording; the measurement (no `derive()` change, no warning) stands regardless |
| A4 | Hex bore at `0.05 mm` across flats with a flip link is an acceptable fixture state (answers 200 on the API; measured on `GearParams`/`derive`, not through HTTP) | Flip links | Flip link for `bore_hex` answers an unexpected status; the dim assertion is independent of status by D-15 |

## Open Questions

1. **Gate value for closing `eq` rows in the parity test**
   - What we know: `bore_hex` at `0.05` and at `6` both give a `{warnings}`-only diff for `bore_d`/`bore_flat` at both bounds (measured both).
   - What's unclear: none that blocks. Recommendation: close `eq` gates with `minimum + step` generically (no field-specific number), close `gt` gates at their default (0), assert the closed state constructs.
2. **Where the refused-set literal lives**
   - Recommendation: a module constant `REFUSED = frozenset({"keyway_width", "keyway_depth"})` in `tests/test_relations.py`, with a comment citing CF-2; the test names fields, which tests may do (only `app.js` may not).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | everything | yes | 3.12.13 [VERIFIED: `.venv/bin/python --version`] | - |
| `.venv` with dev extras | tests, mypy | yes | pydantic 2.13.5, playwright 1.63.0 | - |
| Headless Chromium shell for playwright 1.63.0 | browser steps | yes, via `PLAYWRIGHT_BROWSERS_PATH=$PWD/.venv/ms-playwright` (revision 1228 in `.venv/ms-playwright`; revision 1243 absent from `~/Library/Caches`) | stamp `.venv/.browser` present | `make test`/`make golden.regen` export the variable themselves |
| `make` targets (`verify`, `verify.fast`, `golden.regen`) | gate | yes | - | - |
| Docker | `make check` only | not probed (not needed by this phase) | - | `make verify` needs none |
| node | not needed (runtime needs no Node, L11; `node --check` not used) | - | - | - |

**Baselines measured this session (host: macOS, 1-minute load 3.57 -> 7.36 during the browser run, 2026-10-11, HEAD `fed44fe`):**
`make verify.fast` = **840 passed in 17.06 s**, 17.866 s wall (budget 30 s, L36) [MEASURED]; `tests/test_browser.py` alone =
1 passed, 6.50 s wall, `golden sweep` 0.28 s for 44 records, `download name` 1.13 s, `first build drawn` 3.03 s [MEASURED].
The parity script (18 `derive()` calls incl. construction) took 1.46 ms [MEASURED], so `test_relations.py` adds well under a second to the commit slice.

**Missing dependencies with no fallback:** none.

## Validation Architecture

`.planning/config.json` has no `workflow.nyquist_validation` key (it holds `workflow._auto_chain_active`,
`workflow.use_worktrees`, `git.branching_strategy`), so the section is included.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest + pytest-xdist + pytest-cov; Playwright 1.63.0 for the browser file |
| Config file | `pyproject.toml` (`filterwarnings = ["error", "ignore::DeprecationWarning:starlette.*", "ignore:Using \`httpx\`"]`, `fail_under = 96`) |
| Quick run command | `make verify.fast` (static steps + every test file but the five heavy ones; 17.9 s today) |
| Targeted (kernel-free) | `make test.fast PYTEST_ARGS="tests/test_relations.py -n0"` |
| Targeted (API/CLI) | `make test PYTEST_ARGS="tests/test_api.py tests/test_cli.py -n0 --no-cov -q"` |
| Targeted (browser) | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"` |
| Full suite command | `make verify` |

### Phase Requirements -> Test Map

| Req / SC | Behavior | Test Type | Automated Command | File Exists? |
|----------|----------|-----------|-------------------|-------------|
| REQ-enabled-when-metadata / SC1 | schema emits every relation unchanged; `_f()` and the two `Literal` fields carry it; key collides with no 2020-12 word; `GearParams` gained no field | unit (kernel-free) | `make test.fast PYTEST_ARGS="tests/test_relations.py -n0"` | no - Wave 0 |
| same | `/api/schema` over HTTP emits each relation; `test_schema_drives_the_form` +1 assertion | integration | `make test PYTEST_ARGS="tests/test_api.py tests/test_cli.py -n0 --no-cov -q"` | yes, edited |
| REQ-enabled-when-metadata | a throwaway model with a `Literal` field given `enabled_when` emits it (CF-3's silent-drop trap) | unit | `tests/test_relations.py` | no - Wave 0 |
| REQ-relations-calc-backed / SC2 | per row, relation false => only `warnings` moves and names `dep (value mm)`; keyway pair 422 naming gate + dependent, alone and together; reverse coverage; wrong relations (a),(b),(c) turn the checker red | unit (kernel-free) | `tests/test_relations.py` | no - Wave 0 |
| same | `git diff --exit-code tests/regression/pre_v0_2.json tests/regression/golden_requests.json` clean | git | the command, after every task | yes |
| REQ-dim-and-editable / SC3 | dim state per record under the 44 golden sets; `.field.inactive`, reason text, still editable and sent; re-evaluated on `input`, `readHash`, Reset, `hashchange` | e2e (real uvicorn + headless shell) | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"` | step new, file exists |
| REQ-form-walk-proves-relations / SC4 | the three `app.js` pins tightened under L41, none deleted; the walk covers every relation | static | `make test PYTEST_ARGS="tests/test_api.py -n0 --no-cov -q"` | yes, edited |
| SC4 | idea retired with INDEX row moved; debt file and idea file filed with INDEX rows | doc review | `test -f docs/ideas/retired/2026-09-29-conditional-form-fields.md`; `git grep -c "conditional-form" docs/ideas/INDEX.md` | n/a |

### What each is when red
- Forward parity: `recess_depth <- bore_hex eq 0` -> `changed == {'web'}`, not `{'warnings'}` (measured).
- Warning-names check: `bore_chamfer <- bore_hex eq 0` -> no `ignored` sentence names it (measured: `derive()` unchanged) - the only check that catches it.
- Reverse coverage: removing the `spoke_fillet` declaration -> `spoke_fillet (0.05 mm)` is named by an "ignored" sentence while undeclared.
- Refused class: a keyway row that stops raising (a future `check()` change) or raises without naming the gate.
- Browser: an evaluator that reads `input.value` without the `''` -> default rule disagrees on an emptied box; a `disabled` input fails `fill`; a stripped value fails the sent-query assertion; `applyRelations()` hung on build success leaves a stale state under a 422 flip link.

### Sampling Rate
- **Per task commit:** `make verify.fast` (the commit hook; must stay under 30 s, L36) plus the relevant targeted line; `git diff --exit-code` on the two regression files.
- **Per wave merge:** targeted `test_api.py` + `test_cli.py` + `test_browser.py`.
- **Phase gate:** `make verify` green before `/gsd-verify-work`; state the command and its result line.

### Wave 0 Gaps
- [ ] `tests/test_relations.py` - walk, keyword collision, parity (forward + warning-names), reverse coverage, wrong-relation meta-test, `Literal` carrier probe (covers SC1, SC2)
- [ ] pin rewrite + `test_schema_drives_the_form` assertion in `tests/test_api.py`; walk check in `tests/test_cli.py`
- [ ] `sweep()` return shape, evaluator and flip-link derivation in `tests/browser_session.py`; adapt `tests/capture_requests.py`; `golden sweep` extended and `inert fields` step added in `tests/test_browser.py`
- No new framework, config or fixture file.

## Security Domain

`security_enforcement` is absent from `.planning/config.json`, so it is treated as enabled. The phase adds no
endpoint, input path or dependency; the surface is DOM text built from server-controlled schema strings.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | the project has none by design (tech debt `no-authentication`) |
| V3 Session Management | no | - |
| V4 Access Control | no | - |
| V5 Input Validation | yes | unchanged: `GearParams` validates once at the boundary (L-code rule); `enabled_when` is read-only metadata; the browser evaluator throws on an unknown op |
| V6 Cryptography | no | - |
| V14/Output encoding (DOM) | yes | write the reason with `textContent`, never `innerHTML`; the `id`/`aria-describedby` values are built from field names that are `GearParams` identifiers |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Schema string injected as HTML (`title`, relation text) | Tampering / XSS | `textContent` (Pattern 2); `title` is model-declared, not user input |
| A relation hides a server refusal (UI claims more than the server) | Spoofing (of state) | dim only, never `disabled`/hidden; the 422/warning stays the authority (D-05, D-08); keyway pair keeps its `.invalid` mark |
| Silently dropped relation (typo'd field) | Repudiation of a constraint | the model-driven walk makes it a red test (D-04); an absent gate throws in `effective()` |

## Project Constraints (from CLAUDE.md)

- The gate is `make verify`; state the command and its result line. `make verify.fast` is the commit slice (under 30 s, L36).
- Two standing rules: a printed number is a number someone cuts metal to (L08); a parameter the user did not set never silently changes the part, defaults stay absolute (L05, L03). This phase changes no number and no sent field.
- Stop and ask on: a locked decision that looks wrong (L-numbers), an architectural claim not in the decision log, evidence conflicts. A relation needing `ne`/`ge`/`lt`/OR is that stop (D-02).
- New decision -> options + recommendation -> logged as `Lxx` (L41 here). Do not re-litigate logged decisions.
- Python 3.12 only; vanilla JS, no Node at runtime; `mypy --strict` with `disallow_any_explicit` over `tests/` too; no `TODO`/`FIXME`/`XXX`/`HACK`/`NotImplementedError` in `*.py`/`*.js` (the `no-fake-done` scan).
- Comments explain *why* and carry the measurement or constraint. `calc.py` never imports `cadquery`; vendor types stop at their boundary; a parameter is validated once at `GearParams`.
- Surgical edits; one concern per commit; Conventional Commits; English throughout.
- Ideas and debt are files, one per item, from `docs/<dir>/TEMPLATE.md`, with the INDEX row in the same commit; resolved/retired items move in the commit that closes them. State before the final reply whether any item was filed and its path.
- New behaviour ships with its tests in the same change; performance/memory claims are measured and recorded (this phase's one: the `inert fields` step's wall seconds, three readings, in `bench/RESULTS.md`).

## Sources

### Primary (HIGH confidence)
- The live tree, read this session: `src/spur/params.py`, `src/spur/calc.py` (`check`, `derive`), `src/spur/app.py:373-375`, `src/spur/static/app.js`, `src/spur/static/style.css`, `tests/test_api.py`, `tests/test_cli.py`, `tests/test_browser.py`, `tests/browser_session.py`, `tests/capture_requests.py`, `tests/test_browser_pins.py`, `tests/test_hooks.py`, `Makefile`, `pyproject.toml`, `docs/ideas/*`, `docs/tech_debt/*`
- Commands run this session: the 18-case parity script, the keyway 422 script, the reverse-coverage script over every numeric field, the three wrong-relation probes, the `mypy --strict` prototype (pass and invariance failure), the draft-`app.js` pin check, `make verify.fast`, `tests/test_browser.py`
- `.planning/research/{SUMMARY,ARCHITECTURE (s4),PITFALLS (CF-1..CF-4, M-7, m-1, m-3),STACK}.md` (the milestone's own measurements; re-confirmed above where it mattered)
- https://json-schema.org/draft/2020-12/json-schema-validation - keyword list [CITED]

### Secondary (MEDIUM confidence)
- https://json-schema.org/draft/2020-12/json-schema-core - core/applicator keywords (page truncated; see A1)

### Tertiary (LOW confidence)
- none

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - nothing new; versions read from the tree.
- Architecture: HIGH - the declaration, emission, parity, pin-compat and call-site map were all executed against the live code.
- Pitfalls: HIGH for 1, 2, 3, 5, 6, 9, 11 (reproduced or read); MEDIUM for 4 (visual; the planned browser step is the test).

**Research date:** 2026-10-11
**Valid until:** 2026-11-10 (stable: pinned closure; the only moving part is the host's Playwright browser revision)
