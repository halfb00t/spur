# Phase 23: Conditional Form Fields - Context

**Gathered:** 2026-10-11
**Status:** Ready for planning

<domain>
## Phase Boundary

An `enabled_when` relation is declared on `GearParams` as `json_schema_extra` metadata
(through `_f()`, and carried the same way by the two bare-`Field` `Literal` fields), emitted
unchanged by `model_json_schema()` and so by `/api/schema`, and rendered by generic `app.js`
code as `.field.inactive`: dimmed, with a reason built from the gate field's `title`, still
editable, value kept, still sent. Every declared relation is one `calc` already backs — the
ignored-field warnings for `bore_d`/`bore_flat` under a hex bore and for each cutout group's
dimensions while its count is 0, and the keyway pair's 422 under a hex bore — and a
kernel-free parity test goes red when the schema and `calc` drift. The Phase 21 browser test
asserts the dim state under the 44 golden request sets and under one flip link per gate, and
`tests/regression/golden_requests.json` shows an empty diff: no link sends a different field
or a different value than it does today.

No new `GearParams` field. No `calc`, `model`, `pool`, `app.py` or `cli` edit. `git diff
--exit-code tests/regression/pre_v0_2.json tests/regression/golden_requests.json` is clean
after every task. `app.js` carries no `GearParams` field name outside `DIMS`; the
`tests/test_api.py` pins are tightened under one `Lxx` (L41, the next free number) that
supersedes 08 D-09 and keeps L02 — never deleted or allow-listed. The two unbacked relations
(`recess_*` under `recess_sides=none`, `bore_flat` at `bore_d=0`) are not declared and get an
idea file; the hex warning that fires on default `bore_d`/`bore_flat` gets a debt file
(`calc` change, never filtered in `app.js`); the conditional-fields idea is retired in the
commit that closes it. Distinct styling for refused versus inert fields stays deferred
(REQUIREMENTS.md "Form follow-ups").

</domain>

<decisions>
## Implementation Decisions

### Relation grammar (kickoff decision 6)
- **D-01:** **A bare JSON list of `{field, op, value}` objects; the list is the AND.**
  `"enabled_when": [{"field": "bore_hex", "op": "eq", "value": 0}]`. No wrapper object, no
  `all`/`any`, no JSON-Schema-flavoured fragment. `model_json_schema()` key-sorts object
  keys (`field, op, value`) and keeps list order (MEASURED, STACK.md) — nothing in the
  grammar depends on either. Rejected: `{"all": [...]}` (reserves room for an OR nobody
  declares); `{"bore_hex": {"const": 0}}` (JSON Schema keywords inside a key that is not JSON
  Schema — a consumer validating against `/api/schema` could read them as constraints,
  PITFALLS CF-3). — **Reversibility:** costly — Phase 24's selector options are written in
  this vocabulary and the L41 entry names it; changing the shape later means two evaluators,
  the walk, the browser evaluator and the selector metadata move together.
- **D-02:** **Operators: `eq` and `gt` only.** The five declared relations use exactly
  `eq 0` and `gt 0`; Phase 24's four bore states need nothing else. A relation that needs
  `ne`, `ge`, `lt` or an OR is a stop-and-ask for the human (PITFALLS CF-3), not a silent
  extension. Both evaluators (JS and the test's Python one) reject an unknown op loudly.
- **D-03:** **`value` is a number; `field` names a numeric `GearParams` field.** No string
  values, no `Literal` drivers. The JS compares `Number(effective(field))`; the model-driven
  test rejects a string value or a non-numeric driver. A `Literal` gate, if one is ever
  declared, arrives with its own op and its own decision.
- **D-04:** **A typed `when()` helper plus the model-driven walk catch a malformed
  relation.** `when(field: str, op: Literal["eq", "gt"], value: float) -> JsonDict` in
  `params.py`; `_f(..., enabled_when=[when("bore_hex", "eq", 0)])`, so a bad op fails
  `mypy --strict` at the call site. The walk (`test_relations.py`, D-13) proves every `field`
  is in `model_fields` and numeric, `op` is in the set, `value` is a number, no dependent is
  also a driver (depth 1), and the schema emits the list unchanged. A typo'd field name is a
  red test, never a relation that silently never fires (CF-3). Rejected: raw dicts at the
  call sites (mypy sees `JsonDict`, cannot check `op`); an import-time assertion after the
  class body (a second place that knows the grammar in production code, for a mistake only a
  developer can make).

### Dim reason: wording and placement (kickoff decision 7, the open part)
- **D-05:** **One neutral wording for both classes; no class marker in the metadata.** The
  reason must be true for an ignored field (it needs the condition to matter) and for a
  refused one (it needs the condition to be allowed), so it states the need, not the
  consequence. The server's warning or 422 stays the authority on what happens. No second
  `json_schema_extra` key; the keyword-collision test covers the one key `enabled_when`.
  Rejected: "Ignored while …" (false for the keyway — a 422 is not ignoring); a
  `when_disabled: "refused"` marker (grows the vocabulary SC1 says is one key; the
  refused-vs-inert styling it would serve is deferred).
- **D-06:** **Wording: `Needs {gate title} = 0` for `eq 0`, `Needs {gate title} above 0`
  for `gt 0`; several conditions join with ` and `.** With today's titles: `Needs Hex bore
  A/F = 0` on `bore_d`, `bore_flat`, `keyway_width`, `keyway_depth`; `Needs Spoke arms above
  0` on `spoke_width`, `hub_d`, `rim_wall`, `spoke_fillet`; `Needs Lightening holes above 0`
  on `hole_d`, `hole_circle_d`; `Needs Honeycomb cell A/F above 0` on `hex_wall`. The text is
  built from the schema's `title` and the relation, nothing hard-coded. Rejected: "{title}
  must be 0" (reads as an instruction to change the gate, wrong for the keyway where zeroing
  the keyway is the other valid fix); appending the gate's current value (more text,
  re-rendered on every input, the gate is a few lines up in the same group).
- **D-07:** **The reason renders in its own `<span class="reason">` inside the label
  wrapper, filled and visible only while `.field.inactive`, linked by `aria-describedby`.**
  The phase's point is "says it before it is typed"; a reason that appears on focus says it
  after. The help `<small>` keeps its hidden-until-`:focus-within` rule. Rejected: the
  `title` attribute only (hover-only, invisible on touch); prepending to the help `<small>`
  (hidden exactly when the dim state is first seen).
- **D-08:** **One tone: `.field.inactive` only.** No second class for an inactive field that
  holds a non-default value. The rendered warning already names set-but-ignored values in
  the server's words; a second visual claim about the same fact is a UI-side rule L02 keeps
  out. Rejected: `.inactive.set` (a second CSS rule, a second assertion, a value-vs-default
  comparison in the evaluator).

### Relation set and the calc proof (SC2)
- **D-09:** **The roadmap's set, unchanged.** `bore_d`, `bore_flat` ← `bore_hex eq 0`;
  `spoke_width`, `hub_d`, `rim_wall`, `spoke_fillet` ← `spoke_count gt 0`; `hole_d`,
  `hole_circle_d` ← `hole_count gt 0`; `hex_wall` ← `hex_cell gt 0`; `keyway_width`,
  `keyway_depth` ← `bore_hex eq 0` (the refused class, each alone a 422, never gated on each
  other — CF-2). Every driver is a pure driver (depth 1, the walk's invariant). Considered
  and not taken: `keyway_* ← bore_hex eq 0 AND bore_d gt 0` (calc-backed — "A keyway needs a
  round bore" is a 422 — but it makes `bore_d` both dependent and driver: under hex `bore_d`
  is dimmed and decides the keyway's dim; the no-bore keyway stays a visible 422 the invalid
  mark already points at). A row that fails the parity proof is dropped with its reason
  recorded, never declared on a guess (ROADMAP SC2).
- **D-10:** **The parity test proves the forward direction and reverse coverage.** Forward
  (SC2): per declared row, with the relation false, changing the dependent changes nothing in
  `derive()` except `warnings` — or, for the keyway pair under hex, `GearParams` construction
  raises naming `bore_hex`, `keyway_width`, `keyway_depth` — and the test was seen red
  against a deliberately wrong relation. Reverse coverage: no numeric field outside the
  declared dependents is ever named by a `derive()` "ignored" sentence (each undeclared field
  set off-default alone, under defaults), so a future `calc` ignored-rule without a relation
  goes red at commit. Rejected: forward only (the minimum; a new ignored-warning with no
  relation would be caught by a human noticing the form stayed live); the converse "relation
  true ⇒ live" (false today for half-set cutout rows, which are 422s — ARCH §4.3 says the
  converse need not hold).
- **D-11:** **Each dependent is perturbed at its two bounds: `ge + step` and `le`.** With
  the gate closed, `check()` skips the dependent (`calc.py:669` for the hex branch, `:781`
  and `:836` for the cutout branches), so any in-range value must change nothing but
  `warnings`; the extremes are where a rule not gated on the relation would bite. Two
  `derive()` calls per dependent, kernel-free. Rejected: the midpoint only (misses a rule
  that fires at a bound); a five-value sweep (no distinct proof for the extra rows).
- **D-12:** **The proofs are kernel-free and live in a new `tests/test_relations.py`, in
  the commit slice (`make verify.fast`).** One module for the grammar's three proofs: the
  well-formedness walk over `GearParams.model_fields` (D-04), the calc parity rows (D-10,
  D-11), and the test that `enabled_when` is in no JSON Schema 2020-12 vocabulary (a static
  keyword list in the test, CF-3). `tests/test_cli.py`'s
  `test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order` gains only the
  check that `/api/schema` emits each relation unchanged; `tests/test_api.py`'s
  `test_schema_drives_the_form` gains one relation assertion. Rejected: appending to
  `tests/test_calc.py` (the walk and the keyword test sit oddly beside root geometry in the
  suite's largest file); extending only the `test_cli.py` walk (`test_cli` is in
  `HEAVY_TEST_FILES`, `tests/test_hooks.py:24`, so a wrong relation would be caught at
  pre-push, not at commit).
- **D-13:** The file is light by construction: it imports `spur.params` and `spur.calc`,
  never `cadquery`, `TestClient` or `playwright`; the import-boundary contracts already
  forbid `calc` importing the kernel.

### Browser proof shape (SC3)
- **D-14:** **The expected inactive set comes from a Python evaluator over `/api/schema`,
  in the test.** About ten lines in `tests/browser_session.py`: read each property's
  `enabled_when`, evaluate it over the link's values with the schema defaults filled in,
  yield the expected `.field.inactive` names and the expected reason text (D-06) from the
  gates' titles. Model-driven like the `form from schema` step; names no field. A deliberate
  second implementation: two evaluators (JS and Python) that must agree on 44+ states is the
  proof. 21 D-09 rejected a Python predictor for the query string because `gearQuery()` has
  no spec to derive from; the grammar fixed in D-01..D-03 is that spec. Rejected: a committed
  `golden_inactive.json` with a regen target (pins the JS against itself — a wrong evaluator
  is captured as the truth on the first regen); hand-listed expected sets per driver state (a
  relation added on the model is invisible until someone edits the list).
- **D-15:** **Beyond the 44 golden sets, one model-driven flip link per distinct gate
  condition.** MEASURED: none of the 44 records sets a gate field (`bore_hex`, `spoke_count`,
  `hole_count`, `hex_cell` are all post-v0.2), so under every golden set the inactive set is
  the same seven cutout dims and the bore four are live; the other state of each relation
  needs links the fixture lacks. For each distinct `{field, op, value}` gate in the schema,
  derive a link setting that gate to an in-range value that flips it (four links today, none
  named in the test; a fifth relation adds its own with no test edit). The server may answer
  422 (a half-set cutout); the dim state is independent of the response and the test says so
  in its assertion message. Plus the roadmap's `#spoke_count=0&hub_d=40`. Rejected:
  hand-picked links chosen to answer 200 (readable, but a new relation is invisible until the
  list grows).
- **D-16:** **`sweep()` reads the inactive set in the same pass; one new step `inert
  fields` after `golden sweep`.** `sweep()` (`tests/browser_session.py:339`) already walks the
  44 hashes on an STL-aborted page; it also reads the `.field.inactive` names per hash, and
  the `golden sweep` step compares both the query (the unchanged pin) and the inactive set
  (D-14's evaluator). The new step holds the flips (D-15), the `hub_d=40` link, the reason
  text, and the `input` and Reset paths (D-17). One function, one server (21 D-10). Rejected:
  a second 44-record pass in a new step (~44 extra `hashchange`s for nothing the first pass
  could not read); two new steps.
- **D-17:** **"Still a field" is proved by a real keystroke into the dimmed field.** Load
  `#spoke_count=0&hub_d=40`: `hub_d` is `.inactive`, holds 40, the sent query is `hub_d=40`
  (`spoke_count=0` is the default and is omitted), the reason reads `Needs Spoke arms above
  0`. `fill` `hub_d` with another value: the next `api/info` request carries it and `hub_d` is
  still `.inactive`. Type a non-zero count into `spoke_count`: `hub_d` loses `.inactive`
  before the 350 ms debounce fires (the `input` path runs before `scheduleUpdate`). Click
  Reset: the inactive set is the default one (the seven cutout dims). The `hashchange` path
  is the sweep itself; the fresh-load path is the sweep's empty record and the flip links. A
  `disabled` or hidden input fails `fill`; a stripped value fails the query check. Rejected:
  attribute checks only (never proves a keystroke reaches the request through a dimmed field,
  which is what kickoff decision 5 bought).

### Evaluation semantics (research-fixed, carried as decisions)
- **D-18:** **The evaluator reads the same effective value `gearQuery()` sends:** an emptied
  number box (`input.value === ''`) reads as the schema default. The dim state can never
  disagree with what the server receives (ARCH §4.2; FEATURES table stakes).
- **D-19:** **`applyRelations()` is one function called from the end of `readHash()`
  (fresh load and `hashchange`), from the form `input` listener before `scheduleUpdate`, and
  from the `#reset` handler** — never hung on a successful build, so the state follows the
  fields when the server answers 422 (PITFALLS CF-4). A gate named in a relation but absent
  from `fields` is a red walk (D-04), not a silent no-op.
- **D-20:** **Drivers are never dependents and the form never dims a driver.** The cutout
  "pick one" mutual exclusion stays the server's 422 (ARCH §4.1); the lock idea stays in
  REQUIREMENTS.md "Form follow-ups".

### Claude's Discretion
- **The hex-warning debt file's severity and trigger.** Recommendation: `nice`, trigger
  "Phase 24's selector ships (choosing Hex leaves `bore_d`/`bore_flat` at their defaults, so
  the warning fires on every hex part) or a user reports the warning as noise". It is a
  `calc` change that rewrites `warnings` for every hex link and the Phase 21 `warning
  rendered` golden baseline (`#bore_hex=6`), so it is never fixed in this phase and never
  filtered in `app.js`.
- **Whether `.invalid` and `.inactive` coexist** on the keyway pair under hex (the 422 names
  `bore_hex`, `keyway_width`, `keyway_depth`). Recommendation: they coexist; `problems()`
  adds `.invalid` and `applyRelations()` owns `.inactive`, neither clears the other; the CSS
  gives `.invalid` the stronger mark. The browser test may assert both on the keyway under
  `#bore_hex=6&keyway_width=3&keyway_depth=1.4`.
- **The gate-cost reading for the new step**: 22 D-06's pattern — the step prints its own
  wall seconds, three readings with host state (`bench.machine_facts()`, load before →
  after, `HEAD`, UTC) under a `## Conditional form fields (Phase 23)` heading in
  `bench/RESULTS.md`; no full-gate A/B (the step builds nothing — the STL route is aborted,
  the flips are four `hashchange`s). Phase 25 re-sets the bar on the final `HEAD`.
- **How the two bare-`Field` `Literal` fields carry the key** (SC1: "the same way"). Both
  construction styles must share one path for the extra — either `_f()` grows a sibling
  `_choice()` helper that builds the same `extra` dict, or the two `Field(...)` calls take
  `json_schema_extra` from the one builder. A test proves a `Literal` field given
  `enabled_when` emits it unchanged, even though no declared relation gates one (CF-3's
  "dropped for the Literal fields with no error" trap).
- **The dim visual** (opacity on the whole label versus the control only; the muted colour
  token) and the `.reason` span's typography — within the existing custom properties
  (`THEME_VARIABLES` are pinned non-empty by the browser test).
- **The exact token the `fields.set(name, { input, wrap, title })` pin is rewritten to**
  once each field's relation (and `.reason` span) is stored — rewritten to the new exact
  token, stricter, under L41 (PITFALLS CF-1); the `['word',` harvest means no new JS table
  of that shape (ROADMAP boundary).
- **The deliberately-wrong-relation evidence**: a monkeypatched relation seen red once,
  recorded in the plan SUMMARY the way Phase 21 recorded "each assertion seen red once".
- **L41's text**: supersedes 08 D-09, keeps L02 as the argument (the relation lives on the
  model and reaches the form through the schema), names the grammar (D-01..D-03), the
  declared set (D-09), the reason rule (D-06), the pins it rewrites, and the two files it
  files; L39/L40's paragraph shape, every figure cited to a SUMMARY sha or `bench/RESULTS.md`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scope and requirements
- `.planning/ROADMAP.md` — Phase 23 entry: goal, four success criteria, kickoff decisions
  5–8, boundaries (CF-1 pins; the `['word',` harvest), research flag
- `.planning/REQUIREMENTS.md` — `REQ-enabled-when-metadata`, `REQ-relations-calc-backed`,
  `REQ-dim-and-editable`, `REQ-form-walk-proves-relations`; "Form follow-ups (v0.5.x)" (the
  deferred refused styling, the pick-one lock, the two unbacked relations, the hex-warning
  debt, the `#root_shape=bogus` debt)
- `.planning/PROJECT.md` — milestone v0.5 intent and the four rules it lives by

### Research (figures carry MEASURED / READ / DOCS tags; SUMMARY's disagreement table is authoritative)
- `.planning/research/SUMMARY.md` — "Where the Four Files Disagree" rows 4–7; "Decisions
  Reserved for the Human" 5–8
- `.planning/research/FEATURES.md` — Category 2: the relation inventory (calc-backed only),
  the table stakes, the anti-features (hide, `disabled`, clearing, filtering warnings,
  re-implementing `check()` in JS), the reproduced hex × keyway 422 and `bore_d=0`
  silence
- `.planning/research/ARCHITECTURE.md` — §4 `enabled_when` data flow end to end (§4.1
  declaration, §4.2 `applyRelations()` with no field-specific JS, §4.3 the two traps, §4.4
  extending the model-driven walk); §5.1–5.2 only for the vocabulary Phase 24 reuses
- `.planning/research/PITFALLS.md` — CF-1 (pins tightened, never deleted), CF-2 (refusals
  as disabled: the keyway deadlock, the three classes), CF-3 (`json_schema_extra` is not
  policed; one bare key; both construction styles), CF-4 (five programmatic value writes)
- `.planning/research/STACK.md` — the `json_schema_extra` measurement: nested dicts and
  lists verbatim, key-sorted at every level, `JsonDict` passes `mypy --strict`, no
  JSON-Schema evaluator in the browser

### Decisions the `Lxx` supersedes, keeps or follows
- `docs/architecture/decision_log.md` — L02 (one parameter model, three front ends — kept
  and the argument), L03 (cap and warn, or refuse — never guess), L05 (defaults absolute,
  links mean what they meant), L08 (no number is better than a wrong number), L27 (hex
  replaces the round profile; `bore_d`/`bore_flat` ignored, never refused), L30 (one
  cutout pattern per part; D-15's ignored-dimension warnings), L36 (commit slice under
  30 s), L39 (the browser test's shape: one function, one server, `with step(...)`), L40
  (the previous entry; L41 follows its shape)
- `.planning/milestones/v0.2-phases/08-hex-bore/08-CONTEXT.md` — D-09 ("No conditional
  form behaviour", the decision L41 supersedes) and its Deferred Ideas trigger
- `.planning/phases/21-browser-test-of-the-viewer/21-CONTEXT.md` — D-04 (`canvas.dataset
  .triangles`, the wait discipline), D-08/D-09 (route-captured golden sweep; the committed
  pin with `make golden.regen`; Phases 23–24 must show an empty diff), D-10/D-11 (one
  scenario, one server, the shipped pool)
- `.planning/phases/22-download-name-carries-the-root/22-CONTEXT.md` — D-06 (a step's own
  gate-cost reading, no A/B), D-07 (a new named step's placement)

### The code under change and the pins it meets
- `src/spur/params.py` — `_f()` (:17–23, builds `extra: JsonDict`), the two bare-`Field`
  `Literal` fields `root_shape` (:59) and `recess_sides` (:102), the Bore group (:72–96),
  Spokes (:129–143), Holes (:155–161), Honeycomb (:166–173); field titles are the reason's
  words
- `src/spur/calc.py` — the keyway × hex refusal (:653–657) and the half-set/no-bore
  refusals beside it; the hex branch that skips `bore_d`/`bore_flat` checks (:669–672); the
  cutout branches (:781, :836); the four "ignored" sentences (:1159–1167 hex, :1207–1218
  spokes, :1220–1229 holes, :1241–1247 honeycomb)
- `src/spur/app.py` — `/api/schema` is `GearParams.model_json_schema()` with no
  transformation (:373–375); no edit
- `src/spur/static/app.js` — `buildForm()` (:47–93, the `fields` Map entry `{ input, wrap,
  title }` at :92), `readHash()` (:96), `gearQuery()` (:103, reads `input.value`, omits `''`
  and defaults), `problems()` (:121, the `.invalid` mark), `update()` (:176, debounce
  350 ms), the `input` listener (:340), `hashchange` (:342), `#reset` (:347)
- `src/spur/static/style.css` — `.field` grid (:91–111), `.field.invalid` (:112), the
  help `<small>` focus rule (:187–188)
- `tests/test_api.py` — the pins L41 tightens:
  `test_every_key_the_ui_reads_is_a_derived_dimensions_field` (:123, the `['word',`
  harvest) and `test_the_shareable_link_round_trips_every_field_through_generic_code`
  (:162, the exact tokens and the no-field-name rule outside `DIMS`);
  `test_schema_drives_the_form` (:58, gains one assertion);
  `test_openapi_documents_the_typed_contracts` (:65, re-run with the nested extra)
- `tests/test_cli.py` — `test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order`
  (:198, the model-driven walk; heavy tier)
- `tests/test_browser.py` — the scenario function (:258), `golden sweep` (:527),
  `download name` (:558), `root_shape=bogus as today` (:585); `_title()` (:131),
  `_golden_records()` (:198)
- `tests/browser_session.py` — `fixture_hashes()` (:318), `sweep()` (:339), `eval_str`,
  `eval_str_list`, `eval_pairs`
- `tests/test_browser_pins.py` — the commit-slice precedent: AST pins on the browser test,
  milliseconds, no playwright import
- `tests/test_hooks.py` — `HEAVY_TEST_FILES` (:24): `test_model`, `test_pool`, `test_api`,
  `test_cli`, `test_browser`; the new `test_relations.py` is not in it
- `tests/regression/pre_v0_2.json`, `tests/regression/golden_requests.json` — the two
  files whose diff must be empty after every task
- `docs/ideas/2026-09-29-conditional-form-fields.md` — retired in the commit that closes
  the phase (`git mv` to `docs/ideas/retired/`, INDEX row moved)
- `docs/ideas/TEMPLATE.md`, `docs/ideas/INDEX.md`, `docs/tech_debt/TEMPLATE.md`,
  `docs/tech_debt/INDEX.md` — the two files this phase files
- `docs/tech_debt/active/2026-10-10-root-shape-bogus-loads-a-blank-select.md` — its
  trigger is "Phase 23 or 24 touches `buildForm`'s enum rendering": this phase does not
  change how a `<select>` is built; if a task must, the trigger fires and the debt is
  handled, not stepped around
- `docs/architecture/web-ui.md` — the viewer's design record; gains the relation paragraph
- `bench/RESULTS.md` — `## Download name carries the root (Phase 22)`: the per-step
  reading's format

### Standards
- `docs/CODING_VALUES.md` — comments carry the measurement or constraint; vendor types stop
  at their boundary
- `CLAUDE.md` — the gate, the two standing rules, debt and idea filing rules

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `_f()` already builds `extra: JsonDict` beside `group`/`unit`/`step`; `enabled_when` is
  one more optional keyword on it. `pydantic.config.JsonDict` is recursive and passes
  `mypy --strict` with `disallow_any_explicit` (MEASURED, STACK.md).
- `buildForm()`'s `fields` Map (`name → { input, wrap, title }`) is where the relation and
  the `.reason` span are stored per field; `defaults[name]` is the effective value of an
  emptied box (D-18).
- `problems()` is the precedent for marking a `label.field` from server data
  (`wrap.classList.add('invalid')`); `applyRelations()` mirrors it with `inactive`.
- `_title(properties, name)` in `tests/test_browser.py` already turns a schema property
  into its displayed title — the reason's expected text is built from it.
- `sweep()` already drives all 44 hashes on an STL-aborted page and returns a per-record
  value; extending its return to carry the inactive set is one more `eval_str_list`.
- `tests/test_browser_pins.py` shows the commit-slice shape: kernel-free, milliseconds,
  reads sources, never imports playwright.
- `test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order` is the
  model-driven walk pattern (iterate `GearParams.model_fields`, never the consumer's list).
- `docs/ideas/TEMPLATE.md` / `docs/tech_debt/TEMPLATE.md` and their `INDEX.md` for the
  two files; `docs/ideas/retired/` for the retirement.
- L39 and L40 in `docs/architecture/decision_log.md` for L41's paragraph shape.

### Established Patterns
- The form is generated from `/api/schema` and nothing else (L02, 08 D-09's spirit); any
  per-field knowledge lives on the model as metadata.
- Tests test the real thing: real `uvicorn`, real browser, real `derive()`; the dim state
  is observed through the DOM and the captured request.
- Test names read as requirements; one scenario function with `with step(...)` per
  assertion, the step name in every message.
- A pin changes only to a stricter one, under an `Lxx` that says which (CF-1).
- The fixture and the golden request pin move only by their regen targets in their own
  commits; a feature commit never touches them.
- `filterwarnings = ["error", …]`; `mypy --strict` over `tests/` too.
- Comments carry the measurement or constraint (`CODING_VALUES.md`).

### Integration Points
- `src/spur/params.py` `_f()` and the two `Literal` `Field(...)` calls: the declaration.
- `src/spur/static/app.js` `buildForm()`, `readHash()`, the `input` listener, `#reset`:
  the four call sites of `applyRelations()`.
- `src/spur/static/style.css`: `.field.inactive` and `.field .reason`.
- `tests/test_relations.py` (new, commit slice): the three kernel-free proofs.
- `tests/browser_session.py` `sweep()` + the evaluator; `tests/test_browser.py` the
  extended `golden sweep` and the new `inert fields` step.
- `tests/test_api.py` pins rewritten; `tests/test_cli.py` walk extended.
- `docs/architecture/decision_log.md` L41; `docs/architecture/web-ui.md`; `README.md` if it
  describes the form's behaviour.
- `docs/ideas/` (one new, one retired) and `docs/tech_debt/active/` (one new), each with
  its INDEX row in the same commit.
- `bench/RESULTS.md`: the step's three readings.

</code_context>

<specifics>
## Specific Ideas

- The reason, verbatim per field (from today's titles): `Needs Hex bore A/F = 0` (bore_d,
  bore_flat, keyway_width, keyway_depth); `Needs Spoke arms above 0` (spoke_width, hub_d,
  rim_wall, spoke_fillet); `Needs Lightening holes above 0` (hole_d, hole_circle_d); `Needs
  Honeycomb cell A/F above 0` (hex_wall). If a title changes, the reason follows it — the
  test derives the expected text from the schema, never from a literal.
- The declaration, one line per field: `_f(..., enabled_when=[when("bore_hex", "eq", 0)])`.
- The JS evaluator, in spirit: `rels.every(({ field, op, value }) => op === 'eq' ?
  Number(effective(field)) === value : Number(effective(field)) > value)` with
  `effective(n)` returning the default for an emptied box; an unknown op throws.
- Under every one of the 44 golden sets the inactive set is exactly the seven cutout dims;
  the flips are the only states where a bore field dims or a cutout dim goes live.

</specifics>

<deferred>
## Deferred Ideas

- **`keyway_* ← bore_d gt 0`** (the "keyway needs a round bore" 422 as a second condition)
  — considered in D-09 and not declared: it would make `bore_d` a dependent and a driver.
  Revisit if a user reports the no-bore keyway 422 as a surprise; the depth-1 rule would
  need a stated relaxation.
- **Refused-vs-inert styling** and a class marker in the metadata — REQUIREMENTS.md "Form
  follow-ups"; D-05 keeps the vocabulary to one key until the dim alone proves unclear.
- **The two unbacked relations** (`recess_*` under `recess_sides=none`, `bore_flat` at
  `bore_d=0`) with a `calc` warning first — this phase files the idea (ROADMAP SC4); not
  declared because the warning would rewrite 14 fixture records.
- **The hex warning on default `bore_d`/`bore_flat`** — this phase files the debt
  (ROADMAP SC4); a `calc` change, never filtered in `app.js`.
- **Cutout "pick one" lock** — REQUIREMENTS.md "Form follow-ups"; the refused class across
  groups, D-20 keeps mutual exclusion the server's 422.

None of these entered this phase's scope — discussion stayed within the roadmap boundary.

</deferred>

---

*Phase: 23-conditional-form-fields*
*Context gathered: 2026-10-11*
