# Phase 24: Bore-Shape Selector - Context

**Gathered:** 2026-10-12
**Status:** Ready for planning

<domain>
## Phase Boundary

A `<select>` titled "Bore shape" at the top of the Bore fieldset, built by generic `app.js`
code from a model-level `json_schema_extra` entry on `GearParams` that lists its options in
the L41 condition vocabulary (`when()` lists; `eq`/`gt`, numbers, numeric fields). Its state
is derived from `bore_d`, `bore_flat` and `bore_hex` through the same `holds()` the
relations use, at the same three call sites as `applyRelations()`; it never writes on load.
A pick writes only the fields of the chosen option's `eq` conditions, as explicit `"0"`;
a `gt 0` field the pick needs restores the user's own stashed value or leaves the pick
pending, visibly, until a number is typed. The select is not in `fields`, never in the URL
or any `/api/*` request; the API, the CLI and every shared link are unchanged (L05). The
keyway stays two fields outside the select; its 422s stay the server's.

Proved by a new kernel-free `tests/test_selector.py` (metadata walk, exclusivity and
totality of the four states, a round-trip per state through `derive()`), by the browser
test (the select's state under the 44 golden links in the same `sweep()` pass, one new step
for the picks, a scenario-wide assertion that no non-`GearParams` key reaches `/api/*` or the
hash), and by an empty diff on `tests/regression/pre_v0_2.json` and
`tests/regression/golden_requests.json` after every task. One `Lxx` (L42, the next free
number) records it; the bore-shape idea is retired in the commit that closes the phase.

No new `GearParams` field. No `calc`, `model`, `pool`, `app.py` or `cli` edit. `app.js`
carries no bore field name outside `DIMS`; the `tests/test_api.py` pins are tightened under
L42, never deleted or allow-listed. The hex warning that names the default `bore_d`/
`bore_flat` is not fixed here (its trigger fires when this phase ships; a `/gsd-quick`
follows, before Phase 25's gate reading).

</domain>

<decisions>
## Implementation Decisions

### The gate (kickoff decision 9, the open half)
- **D-01:** **Build it; the phase is not skipped.** The roadmap's second skip trigger
  ("the schema-carried route cannot be built without weakening the field-name pin") does
  not fire: MEASURED at discuss-phase with the dev venv's pydantic,
  `ConfigDict(json_schema_extra={"selectors": [...]})` on a model emits the key at the top
  level of `model_json_schema()`, nested lists and dicts verbatim and key-sorted, and a
  subclass (`InfoQuery`, `ModelQuery` in `app.py`) inherits it. Every option is expressible
  in the L41 grammar (D-02), so `app.js` names no bore field. — **Reversibility:**
  reversible until the first commit; afterwards the skip path is a revert of the phase
  plus the roadmap's `Skipped (cut)` bookkeeping.

### Option set and totality (kickoff decision 10)
- **D-02:** **Four options, in this declaration (and display) order, each a `when()`
  list:**
  - Round: `[when("bore_hex", "eq", 0), when("bore_d", "gt", 0), when("bore_flat", "eq", 0)]`
  - D-flat: `[when("bore_hex", "eq", 0), when("bore_d", "gt", 0), when("bore_flat", "gt", 0)]`
  - Hex: `[when("bore_hex", "gt", 0)]`
  - No bore: `[when("bore_hex", "eq", 0), when("bore_d", "eq", 0)]`

  Exactly one option holds for every non-negative triple, so derivation needs no
  precedence rule and order is display only; the shipped default (`bore_d` 9,
  `bore_flat` 8, `bore_hex` 0) derives as D-flat. A fifth "No bore" option is required
  by totality: `bore_d=0, bore_hex=0` is a legal 200 with no warning (PITFALLS BS-1,
  MEASURED), and without it the select would lie (Round at a 0 bore) or go blank (BS-3).
  Rejected: four shapes with a disabled placeholder (totality unprovable); No bore first
  (the off state reads better last, as `0 = none` does in the help text); D-flat first
  (the default first, but D-flat before Round reads oddly). — **Reversibility:** costly —
  L42 names the four states, the round-trip test has a row per state, and the browser
  step and the golden sweep's select read assert them.
- **D-03:** **The keyway stays outside the select.** It is a modifier of Round and D-flat
  (L27 research rejected a `bore_type` discriminator for this; 23 D-09), already dimmed
  under Hex by L41, and each of its 422s stays the server's. Rejected: composite options
  (Round + keyway, D-flat + keyway — six entries, each keyed one pending until both fields
  are typed, and the keyway made exclusive with shapes it composes with).
- **D-04:** **First row of the Bore fieldset, before `Bore Ø`, titled "Bore shape".** Title,
  option labels and the fieldset come from the metadata (`title`, `label`, `group`),
  nothing from JS. It looks like a `.field` row (name, control) but is never entered in
  `fields` and is built by code outside the `Object.entries(schema.properties)` loop (a
  pinned token; PITFALLS BS-2). Rejected: a control in the `legend` row (new CSS; the
  browser test's label read would not find it).

### Schema carriage (S1, as taken at kickoff; the constraints fixed here)
- **D-05:** **A model-level `json_schema_extra` on `GearParams.model_config`, one list of
  selector objects, each option an object `{label, when: [...]}` in the L41 vocabulary
  and nothing else.** No second condition grammar, no `writes`/`clears` key (D-07, D-10).
  The key name and the exact object shape are Claude's discretion (recommendation below);
  option tables are objects, never `['word', ...]` rows (ROADMAP boundary, PITFALLS
  BS-4). `InfoQuery`/`ModelQuery` inherit the key into their OpenAPI component schemas,
  as they already do `group`/`unit` — harmless, and the `test_openapi_documents_the_typed_
  contracts` test re-runs with it. The keyword-collision test extends to the new key.

### Derivation: loading never writes
- **D-06:** **The shown option is the one whose conditions all hold over the effective
  values, through the same `holds()` and `effective()` the relations use** (an emptied
  box reads as the schema default, 23 D-18). Re-derived at the end of `readHash()`
  (fresh load and `hashchange`), in the form `input` listener and in `#reset` — the three
  call sites of `applyRelations()` (23 D-19) — and never on a build response, so the
  state follows the fields under a 422. Derivation never writes a field and never assigns
  the select a value with no matching option (BS-3): totality (D-02) is what makes that
  true, and the grid test (D-12) is what proves it.

### What a pick writes (kickoff decision 11; SUMMARY row 13)
- **D-07:** **A pick writes, for each `eq` condition of the chosen option, that
  condition's `value` into its `field` when `Number(effective(field)) !== value`, as the
  string `"0"` (today every `eq` value is 0), never `''` — and nothing else.** The
  writes are derived from the option's own conditions; no second metadata key. Minimum by
  construction: Round from the default part writes `bore_flat` only (`bore_hex` is
  already 0) and the hash becomes `#bore_flat=0`; No bore writes `bore_d` only →
  `#bore_d=0`; D-flat from Hex writes `bore_hex` only; Hex writes nothing (D-08/D-09).
  Picking the option already shown writes nothing. A link made by the selector is a link
  the typed fields could have made (L05). — **Reversibility:** costly — the Python mirror
  of this rule in `tests/test_selector.py` and the browser step's expected queries encode
  it; the L42 entry states it.
- **D-08:** **One stash rule for every field a pick zeroes.** When D-07 writes `"0"` into
  a field, the string the box held is stashed under the field's name, in memory. A pick
  whose `gt 0` condition is false restores the stash for that field if present (the
  user's own number, never a starter) and otherwise leaves the pick pending (D-09). The
  same rule serves Hex (`bore_hex`), D-flat (`bore_flat`) and Round/D-flat's `bore_d`
  after No bore. Reset clears the stash; a reload clears it by being a reload. Rejected:
  a starter value — the schema default 8 for `bore_flat` (a flat the user did not type,
  and a second rule because `bore_hex` has no default); Hex pending-only beside a D-flat
  stash (two rules — the human first picked it, then chose one rule for both); a stash
  that survives Reset (a pick after Reset would restore a pre-Reset value).
- **D-09:** **Pending: no write, visible as such.** The select keeps the chosen option and
  its wrapper gets `.pending` (the dashed-border tone L41 gave `.inactive`); the `gt 0`
  field whose value is 0 is focused and its own `.reason` row (L41's span) is filled with a
  need built from that field's schema title (wording is discretion; the browser test
  derives the expected text from the schema). The part, the hash and the requests are
  unchanged: a pick that cannot be made true writes nothing (the second standing rule).
  Pending ends at the next re-derive (D-06): a typed number lands on the chosen option,
  anything else (another field edited, `hashchange`, Reset, reload) shows the derived
  state again. A reload never remembers a pick (ARCH §5.2). Rejected: the select snapping
  back on the next re-derive immediately (honest, but the click looks undone); a pending
  state that survives edits to other fields (more state for no proof).
- **D-10:** **The keyway pair is left alone when Hex or No bore is picked over a keyed
  bore.** The server's 422 (`A keyway cannot be cut into a hex bore …` / `A keyway needs a
  round bore …`) marks `keyway_width`/`keyway_depth` `.invalid` (and `.inactive` under
  Hex, L41), with the server's own fix text; the server stays the authority on refusals
  (23 D-20). Cost accepted: picking Hex on a keyed gear shows a red form until the user
  zeroes the keyway. Rejected: a `clears: [...]` key per option with a stash (FEATURES —
  prevents the bore group's one 422 from the form, but a second vocabulary key whose
  fields the walk must separately prove); zeroing every field whose relation turns false
  after the write (also zeroes the inert `bore_d`/`bore_flat` under Hex — new link
  shapes, loses the bore; FEATURES and ARCH both reject it).
- **D-11:** **`applyRelations()` reads the fields, never the select.** Under a pending
  Hex, `bore_d` and `bore_flat` stay live because `bore_hex` is still 0; the moment a
  number is typed they dim with `Needs Hex bore A/F = 0` as today. No relation is declared
  on the select and the select is never a driver.

### Proof
- **D-12:** **A new `tests/test_selector.py`, kernel-free, in the commit slice (not in
  `HEAVY_TEST_FILES`), importing the Python evaluator from `tests/test_relations.py` so
  there is one Python evaluator.** It proves: (a) the walk — every option's `when` is
  well-formed by 23 D-04's rules (field in `model_fields` and numeric, op in `{eq, gt}`,
  value a number), `title`/`label`/`group` are non-empty strings, and `/api/schema` emits
  the list unchanged; (b) exclusivity and totality — over the 2³ grid of each of
  `bore_d`, `bore_flat`, `bore_hex` at 0 and at an in-range positive value, plus the
  defaults, exactly one option holds; (c) the round-trip per state (REQ-selector-round-
  trips-per-state) — from each of the four states and the default, apply the Python
  mirror of D-07/D-08 for each option: when the chosen option's `gt` fields are non-zero
  the resulting `GearParams` makes it hold and `derive()` equals `derive()` of the same
  flats typed directly (identical document); when a `gt` field is 0 the rule writes
  nothing and the state is unchanged (pending); (d) each proof seen red once against a
  deliberately wrong option (a wrong field, a wrong op, an option that overlaps another),
  recorded in the SUMMARY the way Phase 23 recorded its wrong-relation evidence. Rejected:
  extending `tests/test_relations.py` (23 D-12 scoped it to the field-relation proofs;
  the file would grow past what it is named for).
- **D-13:** **The browser proves derivation under the 44 golden links in the same pass,
  and the picks in one new step.** `sweep()` reads the select's shown option per hash
  (one more `eval_str`), and the `golden sweep` step compares it to the Python derivation
  over the link's values — with the golden file's empty diff this is the "loading never
  writes" proof (ROADMAP SC2). One new named step (name and placement after `inert fields`
  are discretion), STL routes aborted as in the sweep: pick each option from the default
  and from each other reachable state and compare the captured `api/info` query to the
  Python rule's prediction; a pending pick (Hex from the default) leaves the query, the
  hash and the select's `.pending` as D-09 says and focuses `bore_hex`; typing a number
  then lands on Hex; the stash restores a zeroed value (D-flat → Round → D-flat puts the
  box back to what it held); Reset clears the stash and shows D-flat; `#bore_hex=6` loads
  as Hex with `bore_d`/`bore_flat` dimmed; `#bore_d=0` loads as No bore. Everything
  expected is derived from `/api/schema` at test time; no option label or field name is a
  literal in the test.
- **D-14:** **The no-foreign-key assertion is scenario-wide.** A `page.on("request")`
  listener installed before the first step records every `/api/*` request; after every
  step and at the end the test asserts each request's parameter names are a subset of
  `GearParams.model_fields | {quality, mate_teeth}` (read from the schema at test time)
  and the hash's keys a subset of `model_fields | {mate_teeth}` (PITFALLS BS-2). Covers
  the sweep, the flips and the picks alike; a future leak anywhere goes red. Rejected:
  asserting inside the selector step only (leaves the other twelve steps unguarded).
- **D-15:** **Gate cost: 22 D-06's pattern.** The new step prints its own wall seconds;
  three readings with host state (`bench.machine_facts()`, load before → after, `HEAD`,
  UTC) go under `## Bore-shape selector (Phase 24)` in `bench/RESULTS.md`; no full-gate
  A/B (the step builds nothing — STL aborted, a handful of `api/info` requests). Phase 25
  re-sets the bar on the final `HEAD`.
- **D-16:** **Pins tightened under L42, never deleted (PITFALLS CF-1).**
  `test_the_shareable_link_round_trips_every_field_through_generic_code` gains exact
  tokens for the selector's loop over the metadata, the derive call at the three sites,
  the write rule and the stash; the `['word',` harvest means no JS table of that shape.
  The select element carries **no `name` attribute**, so `form#params [name]` (FORM_PAIRS,
  `form built`'s count, `form from schema`'s names, INACTIVE_PAIRS) is unaffected; its
  wrapper is either not `label.field` (an own class sharing the grid rules) or the `form
  from schema` title list is extended to read the selectors' titles from the schema —
  stricter either way, Claude's choice. The `root_shape=bogus` debt's trigger ("Phase 23
  or 24 touches `buildForm`'s enum rendering") does not fire: the selector is built
  outside the `prop.enum` branch; if a task must touch that branch, the trigger fires and
  the debt is handled, not stepped around.
- **D-17:** **Closing the phase.** L42 appended to `docs/architecture/decision_log.md`
  (L41's paragraph shape; every figure cited to a SUMMARY sha or `bench/RESULTS.md`);
  `docs/architecture/web-ui.md` gains the selector paragraph; `docs/ideas/2026-09-27-bore-
  shape-selector-in-the-web-form.md` retired (`git mv` to `docs/ideas/retired/`, INDEX row
  moved) in the commit that closes the phase; the hex-warning debt file's "Next step" is
  restated in that commit as "trigger fired: the selector shipped in <sha>; fix as a
  `/gsd-quick` before Phase 25's reading". `git diff --exit-code
  tests/regression/pre_v0_2.json tests/regression/golden_requests.json` is clean after every
  task.

### Taken at plan-phase (research found the code disagrees with the text above)
- **D-18:** **No option holds → a blank select, no throw, no write.** D-02's totality is
  over non-negative triples; the form accepts `-1`, and 13 of 27 cells of a `{-1, 0, 6}`
  grid match no option (MEASURED, 24-RESEARCH). `deriveSelectors()` is total and caught per
  selector, as `applyRelations()` is per item: when `find()` returns nothing the select's
  `selectedIndex` is `-1`, nothing is written, and `readHash()` goes on to `update()` (a
  negative value is the server's 422, as today). The grid test (D-12 b) covers the negative
  cells and the browser proves no throw. Rejected: keeping the last shown option (the select
  would lie about the fields, BS-3, and needs state the derivation otherwise has none of).
- **D-19:** **`hashchange` leaves the stash alone.** Only Reset and a reload clear it, exactly
  as D-08 says; a hash navigation re-derives the shown option (D-06) and a later pick can
  still restore a value the user typed. Rejected: clearing on `hashchange` (a fourth call
  site for the stash rule and one more browser expectation, for no proof).

### Claude's Discretion
- **The schema key and option shape.** Recommendation: `selectors: [{title: "Bore shape",
  group: "Bore", options: [{label, when}]}]` — a list so a second selector (the cutout
  "pick one", deferred) is one more entry, not a new key.
- **The select's DOM identity and CSS.** No `name`; an `id` derived from the metadata
  (never a literal bore word in JS); `.pending` within the existing custom properties
  (`THEME_VARIABLES` are pinned non-empty).
- **Pending reason wording**, built from the target field's schema title; the browser test
  derives the expectation from the schema.
- **Pick → request timing.** Recommendation: a pick that writes calls `applyRelations()`
  then `update()` directly, as `hashchange` does (a discrete action, not a keystroke
  stream); a pending pick calls neither (nothing changed).
- **Step name and placement** among the thirteen steps; how `Swept` carries the select's
  value.
- **L42's text**: names the vocabulary's extension to a model-level selector list
  (D-05), the four states (D-02), the derive/write/stash/pending rules (D-06..D-09), the
  keyway left to the 422 (D-10), the pins it tightens (D-16), the files it retires and
  restates (D-17); keeps L02 and L05 as the argument; follows L41, supersedes nothing.
- **The deliberately-wrong-option red evidence** and its SUMMARY record.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scope and requirements
- `.planning/ROADMAP.md` — Phase 24 entry: goal, three success criteria, skip condition,
  kickoff decisions 9–11, boundaries (UI-only; option tables are objects), research flag
- `.planning/REQUIREMENTS.md` — `REQ-selector-schema-carried`,
  `REQ-selector-derives-and-writes-through`, `REQ-selector-round-trips-per-state`; "Form
  follow-ups (v0.5.x)" (the cutout lock, refused-vs-inert styling, the hex-warning debt)
- `.planning/PROJECT.md` — milestone v0.5 intent, the four rules it lives by, success
  metric 2 ("a bore shape is picked, not inferred from a warning")

### Research (figures carry MEASURED / READ / DOCS tags; SUMMARY's disagreement table is authoritative)
- `.planning/research/SUMMARY.md` — "Where the Four Files Disagree" rows 1 and 13;
  "Decisions Reserved for the Human" 9–11
- `.planning/research/FEATURES.md` — finding 3 (the pin collision S1 resolves); Category 3:
  derive-on-load/write-through, the precedence that mirrors calc, the table stakes
  (totality, no invented A/F), the anti-features (a `bore_type` field, `bore_shape` in the
  URL, zeroing `bore_d`/`bore_flat` on Hex, a seeded A/F, composite options)
- `.planning/research/ARCHITECTURE.md` — §5.1 (S1 vs S2), §5.2 (derived not stored; a
  choice writes switch-offs only; pending state; Hex does not zero the round profile),
  §5.3 (the warnings stay the server's); §4 for the evaluator the selector reuses
- `.planning/research/PITFALLS.md` — BS-1 (L05: emptied box reads as default, `Number()`
  not re-formatting, explicit `"0"`, the fifth state), BS-2 (the name leak; the
  request-subset assertion), BS-3 (a select with no matching option goes blank), BS-4 (one
  evaluation pass, CF before BS)
- `.planning/research/STACK.md` — `json_schema_extra` nested emission (verbatim,
  key-sorted); `JsonDict` under `mypy --strict`

### Decisions L42 follows or keeps
- `docs/architecture/decision_log.md` — L41 (the grammar, the declared set, the reason
  rule, the pins; the previous entry — L42 follows its shape), L02 (one model, three front
  ends — kept and the argument), L03, L05 (links mean what they meant), L08, L27 (hex
  replaces the round profile), L36 (commit slice), L39 (the browser test's shape), L40
- `.planning/phases/23-conditional-form-fields/23-CONTEXT.md` — D-01..D-04 (the grammar
  and `when()`), D-05 (one key, no class marker), D-12/D-13 (`test_relations.py`'s scope
  and lightness), D-14..D-19 (the Python evaluator in the test, the flip links, `sweep()`
  extended in one pass, the keystroke proof, effective values, the three call sites), D-20
  (drivers never dimmed; refusals stay the server's)
- `.planning/phases/21-browser-test-of-the-viewer/21-CONTEXT.md` — D-08/D-09 (the
  route-captured golden sweep and the committed pin with `make golden.regen`; Phase 24 must
  show an empty diff), D-10/D-11 (one scenario, one server)
- `.planning/phases/22-download-name-carries-the-root/22-CONTEXT.md` — D-06 (a step's own
  gate-cost reading), D-07 (a new named step's placement)

### The code under change and the pins it meets
- `src/spur/params.py` — `when()` (:17), `_extra()` (:30), `_f()` (:45),
  `GearParams.model_config = ConfigDict(frozen=True)` (:56, where the selector list is
  added), the Bore group (:96–133: `bore_d` :102, `bore_flat` :105, `keyway_width` :108,
  `keyway_depth` :115, `bore_hex` :123); field titles are the pending reason's words
- `src/spur/calc.py` — the keyway refusals (:652–667: hex × keyway, no-bore keyway,
  half-set) the selector leaves to the server; the hex "ignored" sentence (:1166)
- `src/spur/app.py` — `/api/schema` is `GearParams.model_json_schema()` untransformed
  (:373–375); `InfoQuery` (:232) and `ModelQuery` (:237) inherit the config; no edit
- `src/spur/static/app.js` — `fields` and `defaults` (:10–11), `buildForm()` (:47; the
  pinned loop :53, the `fields.set` token :99), `readHash()` (:103), `gearQuery()` (:111),
  `effective()` (:123), `holds()` (:131), `need()` (:142), `applyRelations()` (:158),
  `update()` (:239), `scheduleUpdate` (:284), the `input` listener (:403), `hashchange`
  (:405), `#reset` (:410)
- `src/spur/static/style.css` — `.field` grid (:91), `.field.invalid` (:112),
  `.field.inactive` (:122–124), `.field .reason` (:125–126)
- `tests/test_api.py` — `test_the_shareable_link_round_trips_every_field_through_generic_code`
  (:173; the exact tokens :205–226, the no-field-name rule outside `DIMS` :228–),
  `test_schema_drives_the_form`, `test_openapi_documents_the_typed_contracts`,
  `test_every_key_the_ui_reads_is_a_derived_dimensions_field` (the `['word',` harvest)
- `tests/test_relations.py` — `_conditions()` (:111), `_condition_holds()` (:258), the
  well-formedness walk `test_every_relation_is_well_formed_and_emitted_unchanged` (:313),
  `test_no_extra_key_is_a_json_schema_keyword` (:348) — the evaluator and the walk the new
  file imports or mirrors
- `tests/test_browser.py` — the scenario function and its steps: `form built` (:320,
  counts `form#params [name]`), `form from schema` (:329, names and `label.field .name`
  titles), `golden sweep` (:563), `inert fields` (:615), `unknown relation op` (:814),
  `download name` (:877), `root_shape=bogus as today` (:904); `_title()`
- `tests/browser_session.py` — `FORM_PAIRS` (:268), `INACTIVE_PAIRS` (:273),
  `eval_inactive()` (:298), `_holds()` (:303), `expected_inactive()` (:323),
  `flip_links()` (:376), `sweep()` (:476) and `Swept`, `step()` (:524)
- `tests/test_browser_pins.py` — the commit-slice precedent (AST pins, no playwright
  import)
- `tests/test_hooks.py` — `HEAVY_TEST_FILES` (:25); `test_selector.py` is not in it
- `tests/regression/pre_v0_2.json`, `tests/regression/golden_requests.json` — empty diff
  after every task; `Makefile` `golden.regen` (:277) is the only way either moves
- `docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md` and
  `docs/ideas/INDEX.md` (:13) — retired in the closing commit (`docs/ideas/retired/`)
- `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md` — its
  trigger names this phase's ship; restated, not fixed, here
- `docs/tech_debt/active/2026-10-10-root-shape-bogus-loads-a-blank-select.md` — its
  trigger (`buildForm`'s enum rendering) is not touched by the selector's own code
- `docs/architecture/web-ui.md` — the viewer's design record (:17–28 the relation
  paragraph); gains the selector paragraph
- `bench/RESULTS.md` — `## Conditional form fields (Phase 23)` (:5318): the per-step
  reading's format

### Standards
- `docs/CODING_VALUES.md` — comments carry the measurement or constraint; vendor types
  stop at their boundary
- `CLAUDE.md` — the gate, the two standing rules, debt and idea filing rules

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `when()` and `_extra()` in `params.py`: the selector's options are `when()` lists, so
  the typed `op` check and the `list(...)` copy for `mypy --strict` already exist; the
  model-level list goes on `model_config` beside `frozen=True`.
- `holds()` / `effective()` / `need()` in `app.js`: derivation is `options.find(o =>
  o.when.every(holds))`; the pending reason is built the way `need()` builds the dim
  reason, from a schema title.
- `applyRelations()`'s three call sites (end of `readHash()`, the `input` listener,
  `#reset`) are the selector's re-derive sites — one `deriveSelectors()` call beside each.
- `.field.inactive`'s dashed-border tone and the `.reason` span: `.pending` reuses the
  tone; the target field's existing `.reason` row carries the pending text.
- `tests/test_relations.py`'s `_conditions()`/`_condition_holds()` and the walk: the
  Python evaluator and the well-formedness rules `test_selector.py` imports or mirrors.
- `tests/browser_session.py`'s `expected_inactive()` (a Python evaluator over the schema
  and a link) and `sweep()` (44 hashes on an STL-aborted page, one `Swept` per record):
  the select's expected option per link is the same shape of function; `Swept` gains one
  field.
- `tests/test_browser.py`'s `_title()` and the `with step(...)` scenario; 22 D-06's
  per-step reading in `bench/RESULTS.md`.
- `docs/ideas/retired/` and the INDEX conventions for the retirement; L41 for L42's shape.

### Established Patterns
- The form is generated from `/api/schema` and nothing else (L02, L41); per-field or
  per-group knowledge lives on the model as metadata.
- Tests test the real thing (real `uvicorn`, real browser, real `derive()`), derive every
  expectation from the schema at test time, and name no field or label as a literal.
- Two evaluators that must agree (JS and the test's Python) are the proof (23 D-14).
- A pin changes only to a stricter one, under an `Lxx` that says which (CF-1).
- The fixture and the golden pin move only by their regen targets in their own commits.
- Comments carry the measurement or constraint (`CODING_VALUES.md`).

### Integration Points
- `src/spur/params.py` `model_config`: the selector list.
- `src/spur/static/app.js`: a build function for selectors called from `buildForm()` after
  the pinned loop (the Bore fieldset exists by then); `deriveSelectors()` at the three
  call sites; the `change` handler that writes/stashes/pends; `style.css` `.pending`.
- `tests/test_selector.py` (new, commit slice); `tests/browser_session.py` `sweep()` +
  the Python derivation; `tests/test_browser.py` the extended `golden sweep`, the new
  step and the scenario-wide request listener; `tests/test_api.py` pins rewritten.
- `docs/architecture/decision_log.md` L42; `docs/architecture/web-ui.md`; `README.md` if
  it describes the form.
- `docs/ideas/` (one retired), `docs/tech_debt/active/` (one trigger restated), each with
  its INDEX row in the same commit; `bench/RESULTS.md` the step's three readings.

</code_context>

<specifics>
## Specific Ideas

- The four options verbatim in D-02; display order Round, D-flat, Hex, No bore.
- Link shapes the browser step expects (derived, not typed, in the test): default part +
  Round → `api/info?bore_flat=0`, hash `#bore_flat=0`; default + No bore → `#bore_d=0`;
  default + Hex → no request, no hash change, select `.pending`, `bore_hex` focused;
  then typing `6` → `#bore_hex=6`, `bore_d`/`bore_flat` dimmed `Needs Hex bore A/F = 0`,
  select on Hex; D-flat → Round → D-flat puts `bore_flat` back to the `8` the box held
  (a default, so the hash is empty again); `#bore_hex=6&keyway_width=3&keyway_depth=1.4`
  loads as Hex with the keyway pair `.invalid` and `.inactive` — the selector changes
  nothing there.
- The derivation in spirit: `const shown = options.find(o => o.when.every(holds))`;
  totality means `shown` is never `undefined`, and the grid test is what lets the JS
  assume it.
- The write rule in spirit: `for (const {field, op, value} of chosen.when) if (op === 'eq'
  && Number(effective(field)) !== value) { stash.set(field, input.value); input.value =
  String(value); }` then, for each `gt` condition with `Number(effective(field)) === 0`,
  restore `stash.get(field)` or mark pending and focus.

</specifics>

<deferred>
## Deferred Ideas

- **A `clears` key (zero the keyway pair with a stash on Hex / No bore)** — rejected in
  D-10 for one vocabulary; revisit if users report the red form on picking Hex over a
  keyed bore as a surprise.
- **A starter value for D-flat (the schema default 8)** — rejected in D-08; revisit only on
  a user report that pending is unclear.
- **The hex warning on default `bore_d`/`bore_flat`** — its trigger fires when this phase
  ships; decided here as a `/gsd-quick` after Phase 24 lands and before Phase 25's gate
  reading (a `calc` change plus the `warning rendered` baseline; kept out of a UI-only
  phase). The debt file's "Next step" is restated in the closing commit (D-17).
- **A second selector for the cutout "pick one"** — REQUIREMENTS.md "Form follow-ups"; the
  list shape in D-05 leaves room for it as one more entry.
- **Refused-vs-inert styling** — REQUIREMENTS.md "Form follow-ups"; the keyway pair under
  a picked Hex is the case that would benefit.

None of these entered this phase's scope — discussion stayed within the roadmap boundary.

</deferred>

---

*Phase: 24-bore-shape-selector*
*Context gathered: 2026-10-12*
