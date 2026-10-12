# Phase 24: Bore-Shape Selector - Research

**Researched:** 2026-10-12
**Domain:** schema-carried UI selector over flat form fields (pydantic `json_schema_extra`, vanilla-JS form, Playwright browser test, kernel-free pytest)
**Confidence:** HIGH (every figure below was read from the tree or measured in `.venv` / the headless shell on 2026-10-12, HEAD `87462cb`; the few `[ASSUMED]` items are in the Assumptions Log)

Provenance tags used here: `MEASURED` (ran it this session, output quoted or summarised), `READ` (opened the file this session, path:line and verbatim quote), `DOCS` (official documentation fetched this session). The claim tags `[VERIFIED: ...]`, `[CITED: ...]`, `[ASSUMED]` follow the agent contract. Scratch artefacts (patched copy of `src/spur`, probes) live in the session scratchpad, not in the repo; `git status --short` was empty after every run.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### The gate (kickoff decision 9, the open half)
- **D-01:** **Build it; the phase is not skipped.** The roadmap's second skip trigger
  ("the schema-carried route cannot be built without weakening the field-name pin") does
  not fire: MEASURED at discuss-phase with the dev venv's pydantic,
  `ConfigDict(json_schema_extra={"selectors": [...]})` on a model emits the key at the top
  level of `model_json_schema()`, nested lists and dicts verbatim and key-sorted, and a
  subclass (`InfoQuery`, `ModelQuery` in `app.py`) inherits it. Every option is expressible
  in the L41 grammar (D-02), so `app.js` names no bore field. — **Reversibility:**
  reversible until the first commit; afterwards the skip path is a revert of the phase
  plus the roadmap's `Skipped (cut)` bookkeeping.

#### Option set and totality (kickoff decision 10)
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

#### Schema carriage (S1, as taken at kickoff; the constraints fixed here)
- **D-05:** **A model-level `json_schema_extra` on `GearParams.model_config`, one list of
  selector objects, each option an object `{label, when: [...]}` in the L41 vocabulary
  and nothing else.** No second condition grammar, no `writes`/`clears` key (D-07, D-10).
  The key name and the exact object shape are Claude's discretion (recommendation below);
  option tables are objects, never `['word', ...]` rows (ROADMAP boundary, PITFALLS
  BS-4). `InfoQuery`/`ModelQuery` inherit the key into their OpenAPI component schemas,
  as they already do `group`/`unit` — harmless, and the `test_openapi_documents_the_typed_
  contracts` test re-runs with it. The keyword-collision test extends to the new key.

#### Derivation: loading never writes
- **D-06:** **The shown option is the one whose conditions all hold over the effective
  values, through the same `holds()` and `effective()` the relations use** (an emptied
  box reads as the schema default, 23 D-18). Re-derived at the end of `readHash()`
  (fresh load and `hashchange`), in the form `input` listener and in `#reset` — the three
  call sites of `applyRelations()` (23 D-19) — and never on a build response, so the
  state follows the fields under a 422. Derivation never writes a field and never assigns
  the select a value with no matching option (BS-3): totality (D-02) is what makes that
  true, and the grid test (D-12) is what proves it.

#### What a pick writes (kickoff decision 11; SUMMARY row 13)
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

#### Proof
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

### Deferred Ideas (OUT OF SCOPE)
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
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-selector-schema-carried | options live on the model as schema metadata in the `enabled_when` vocabulary; `app.js` names no bore field; the field-name pin and DIMS-key pin hold | Findings 1-3 (model-level key emits at top level, exact mypy typing, OpenAPI unchanged); Pin map (which `test_api.py` assertions stay byte-identical and which tokens must be rewritten) |
| REQ-selector-derives-and-writes-through | state derived on load, never writes; a change writes only minimum `"0"` fields, stash restores, no `fields` entry, no foreign key in any `/api/*` request or the hash | Findings 4-9 (event bubbling, no-match state, write-rule ordering, stash edge cases, per-page request listener); Code Examples |
| REQ-selector-round-trips-per-state | model-driven round trip per state; 44 golden request sets unchanged | Findings 10-12 (`derive()` is blind between Round and D-flat; golden links reach 3 of 4 states; doctored-option reds measured); Validation Architecture |
</phase_requirements>

## Summary

The schema-carried route is buildable with no weakening of any pin. MEASURED: a model-level `ConfigDict(frozen=True, json_schema_extra={"selectors": [...]})` emits one new top-level key, `selectors`, in `GearParams.model_json_schema()` and `/api/schema` differs from today's only by that key (`properties` byte-identical); `InfoQuery.model_json_schema()` and `ModelQuery.model_json_schema()` inherit it, but **`/openapi.json` is byte-identical before and after** (FastAPI flattens the `Query()` models into `parameters`, so the key never reaches OpenAPI; CONTEXT D-05's "into their OpenAPI component schemas" is wrong, see Drift table). `mypy --strict` accepts a `list[JsonDict]` built inline or through a `JsonDict`-returning helper; it rejects a pre-built `list[JsonDict]` variable placed into a dict by list invariance (the same trap L41 hit).

Three facts the CONTEXT does not hold change how the plans must be written. (1) A `<select>` pick fires `input` (bubbling) then `change`; the form-level `input` listener, which is a pinned token, would run `applyRelations(); scheduleUpdate()` on every pick, re-derive the select back to the old state before the pick handler can act, and send a duplicate `api/info` after 350 ms, so the selector's own handler must be on `input` with `stopPropagation()` (MEASURED, DOCS). (2) "Exactly one option holds" is true over non-negative triples only; the form accepts `-1` (MEASURED: `input.value = '-1'` stays `-1`), 13 of 27 cells of a `{-1, 0, 6}` grid match no option, and a `find()` returning `undefined` that is then dereferenced throws out of `readHash()` and skips `update()` (the WR-01 incident class). (3) `derive()` cannot tell Round from D-flat: `derive(GearParams()) == derive(GearParams(bore_flat=0))` is `True`, so the REQ-selector-round-trips-per-state test must assert the flat-field set and option truth, not the `derive()` document alone.

Gate state at HEAD: `make verify.fast` 896 passed, 16.16 s real; browser file `2 passed in 13.09s` with `golden sweep` 0.32 s and `inert fields` 1.31 s (MEASURED, load 2.45 / 4.74). Nothing is installed; no package changes.

**Primary recommendation:** declare one `BORE_SHAPE`-style `JsonDict` (or inline list) of `{title, group, options:[{label, when}]}` on `model_config`, render it from a function called at the end of `buildForm()`, attach a selector handler on `input` that stops propagation and plans before it writes (pending check first, then writes, then `applyRelations(); deriveSelectors(); update()`), and make `deriveSelectors()` total on a no-match state and caught per selector the way `applyRelations()` is.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Which bore shapes exist and which field values mean each (options + conditions) | API / Backend (the model, `params.py`, emitted by `/api/schema`) | — | L02: one model, three front ends; the form carries no bore word |
| Deriving the shown shape from the flat fields | Browser / Client (`deriveSelectors()` over `holds()`/`effective()`) | — | State of the form is the browser's; same evaluator as the relations |
| Writing the minimum flat fields on a pick, stash, pending | Browser / Client | — | A pick is a discrete UI edit that must produce a link the typed fields could have made (L05) |
| Refusing a keyway over Hex / No bore | API / Backend (`calc.check`, 422) | Browser (marks `.invalid`) | Server stays the authority on refusals (D-10, 23 D-20) |
| Proving options total/exclusive and the write rule | Test tier (kernel-free pytest) | Browser test (Playwright) | Two evaluators that share no code (Python and JS) agreeing is the proof (23 D-14) |
| Warning that a Hex part ignores default `bore_d`/`bore_flat` | API / Backend (`calc.py:1166`) | — | Out of scope here; debt file trigger fires and is restated (D-17) |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pydantic | 2.13.5 (pin `>=2.7`) [VERIFIED: `.venv` `importlib.metadata`] | `ConfigDict(json_schema_extra=...)` model-level key | already the model layer; MEASURED to emit the key |
| vanilla JS in `src/spur/static/app.js` | n/a | `buildSelectors()` / `deriveSelectors()` / pick handler | L11: runtime needs no Node |
| pytest 9.1.1 + xdist + cov | 9.1.1 [VERIFIED: `.venv`] | `tests/test_selector.py` (kernel-free, commit slice) | existing |
| Playwright (Chrome Headless Shell) | 1.63.0 [VERIFIED: `.venv`], shell `chromium_headless_shell-1243` [VERIFIED: `ls .venv/ms-playwright`] | browser step + request listener | existing, pinned exactly (`tests/test_browser_pins.py`) |
| mypy `--strict`, ruff | mypy 2.3.1, ruff 0.16.8 [VERIFIED: `.venv`] | gate | existing |

### Supporting
None new. `when()` (`src/spur/params.py:17`) builds each condition; `tests/test_relations.py::_conditions` (`:111`) and `_condition_holds` (`:258`) are the Python evaluator (imports work: `PYTHONPATH=tests python -c "from test_relations import _conditions, _condition_holds, _properties"` printed `import ok`, MEASURED).

### Alternatives Considered
Locked by CONTEXT (S1 schema-carried; a `BORE_SHAPES` constant in `app.js` was rejected at kickoff). Not re-opened.

**Installation:** none. **Version verification:** versions above were read from the dev venv on 2026-10-12.

## Package Legitimacy Audit

No external package is installed or changed by this phase, so the Package Legitimacy Gate is not applicable. Packages removed due to SLOP: none. Packages flagged SUS: none. No `[ASSUMED]` package names.

## Architecture Patterns

### System Architecture Diagram

```
 params.py  GearParams.model_config(json_schema_extra={"selectors":[...]})
      |
      v   GET /api/schema  (properties unchanged + one new top-level key)
 app.js buildForm()
      |-- loop over schema.properties  --> fields Map (pinned loop, untouched)
      |-- after the loop: buildSelectors(schema.selectors)
      |        creates wrapper(own class, NOT label.field) + <select> (no name, id from metadata)
      |        inserted as first row of the fieldset whose legend == selector.group
      v
 readHash() ----------------+
 form 'input' listener -----+--> applyRelations(); deriveSelectors()   (3 call sites, D-06)
 #reset (+ stash.clear()) ---+          |
                                         v
        shown = options.find(o => o.when.every(holds))   (holds/effective shared with relations)
        select.selectedIndex = shown ? index : -1 ; wrapper.classList.remove('pending')

 select 'input' event (user pick; stopPropagation so the form listener does not run)
      |
      v   plan first:  chosen.when -> eq writes (Number(effective(f)) !== value)
      |                              gt fields with Number(effective(f)) <= value
      |                                  -> stash.has(f) and Number(stash.get(f)) > value ? restore : pending
      +-- pending: no write, wrapper.pending, focus gt field, its .reason = need(...)   (no request, no hash)
      +-- else: stash+write "0" / restore stash ; applyRelations(); deriveSelectors(); update()
                                                  |
                                                  v  /api/info?<flat fields only>  (STL as today)
```

### Recommended Project Structure
```
src/spur/params.py                 # + selector option helper + model_config key (no new field)
src/spur/static/app.js             # + selectors section OUTSIDE the "-- relations (L41)" .. "-- messages" region
src/spur/static/style.css          # + .pending (existing custom properties only) + selector wrapper sharing .field grid rules
tests/test_selector.py             # new, kernel-free, commit slice
tests/browser_session.py           # Swept gains the select's shown option; Python derivation helper
tests/test_browser.py              # golden-sweep comparison, one new step, scenario-wide request recorder
tests/test_api.py                  # pins tightened (token list), schema-test assertion
tests/test_relations.py            # keyword-collision extended to the model-level key (see Finding 3)
docs/architecture/{decision_log,web-ui}.md, README.md:138, docs/ideas/*, docs/tech_debt/*, bench/RESULTS.md
```

### Pattern 1: model-level schema key, typed for `mypy --strict`
**What:** `selectors` list on `model_config`, options built with `when()`.
**When to use:** the one place option data lives.
**Example (MEASURED: this exact shape passed `mypy --strict` with the repo's `pyproject.toml` and the pydantic plugin, `Success: no issues found in 1 source file`; ruff flagged only two E501 because the scratch lines were >100 columns):**
```python
# Source: scratch copy of src/spur/params.py, session scratchpad; when() is params.py:17
def _option(label: str, *conditions: JsonDict) -> JsonDict:
    return {"label": label, "when": list(conditions)}      # list(...) copy: the invariance fix

BORE_SHAPE: JsonDict = {
    "title": "Bore shape", "group": "Bore",
    "options": [
        _option("Round", when("bore_hex", "eq", 0), when("bore_d", "gt", 0),
                when("bore_flat", "eq", 0)),
        _option("D-flat", when("bore_hex", "eq", 0), when("bore_d", "gt", 0),
                when("bore_flat", "gt", 0)),
        _option("Hex", when("bore_hex", "gt", 0)),
        _option("No bore", when("bore_hex", "eq", 0), when("bore_d", "eq", 0)),
    ],
}
# in GearParams:
model_config = ConfigDict(frozen=True, json_schema_extra={"selectors": [BORE_SHAPE]})
```
The failing shape (MEASURED, both variants): assigning a pre-built `list[JsonDict]` variable as a dict value, e.g. `json_schema_extra={"selectors": SELS}` with `SELS: list[JsonDict] = [BORE_SHAPE]`, or `"options": _OPTS` with `_OPTS: list[JsonDict]`, gives
`error: Dict entry 0 has incompatible type "str": "list[JsonDict]"; expected "str": "int | float | str | list[JsonValue] | JsonDict | None"  [dict-item]`. An inline list literal, or `list(...)` of the variable, passes. No `# type: ignore` (the `no-fake-done` target refuses a suppression in `src/spur`, `Makefile:142`).

### Pattern 2: reuse the relations' evaluator, outside the relations region
**What:** `deriveSelectors()` and the pick handler call `holds()`, `effective()` and `need()` (`app.js:131`, `:123`, `:142`) but live in their own `// ---- selectors (L42)` banner placed **outside** the span the `test_api.py` regex captures (see Pin map, "writes_a_value").

### Anti-Patterns to Avoid
- **Registering the select in `fields` or giving it a `name`:** it would join `gearQuery()` and the URL (BS-2) and `form#params [name]`.
- **`options.find(...)` result used unguarded:** `undefined` on out-of-range input throws out of `readHash()` and skips `update()` (Finding 5).
- **Listening on `change` and letting `input` bubble to the form:** the form listener re-derives first (Finding 4).
- **A `Map` of rows `['eq', ...]`:** harvested as a DIMS key by `test_api.py:136`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Condition evaluation in JS | a second grammar/evaluator | `holds()`/`effective()`/`need()` (`app.js:123-145`) | BS-4: one evaluation pass; unknown op already throws |
| Condition evaluation in Python tests | a copy | `_conditions`, `_condition_holds`, `_properties` from `tests/test_relations.py` | D-12; import mechanically verified |
| Condition construction in the model | raw dicts | `when()` (`params.py:17`) | `Literal` op is a `mypy --strict` error at the call site |
| Per-page request capture | a `page.on` on the main page only | one recorder attached to every page the scenario opens (Finding 9) | each `browser.new_page()` is its own context (MEASURED) |
| Expected reason text / titles in the browser test | literals | `_title()` (`test_browser.py:140`), `_js_number()` (`browser_session.py:312`), `_holds()` (`:303`) | derive from `/api/schema` |
| Golden regeneration | editing `golden_requests.json` | `make golden.regen` (`Makefile:277`), run only to prove byte-identity | pin moves only by its regen target in its own commit |

**Key insight:** the selector is a second *reader* of the same conditions; every new moving part is either the schema list, the DOM wrapper, or the plan-then-write rule. Anything that interprets a condition differently from `holds()` is the bug class BS-4 names.

## Verified facts (CONTEXT claims re-checked against the live tree, HEAD `87462cb`)

### Drift table
| CONTEXT reference | Current | Note |
|---|---|---|
| `params.py` `_extra()` `:30`, `_f()` `:45` | `_extra` def at `:29`, `_f` def at `:44` | off by one; `when()` `:17`, `model_config` `:56`, Bore group `:96-133` and the five field lines `:102 :105 :108 :115 :123` are exact |
| D-05: `InfoQuery`/`ModelQuery` "inherit the key into their OpenAPI component schemas" | `InfoQuery.model_json_schema()` and `ModelQuery.model_json_schema()` contain `selectors` (MEASURED `True`/`True`); `/openapi.json` has no `InfoQuery`/`ModelQuery` component and no `selectors` text; `cmp` of the sorted-JSON dumps before/after: `openapi identical` | the key reaches `/api/schema` only. `test_openapi_documents_the_typed_contracts` needs no change and says nothing about the new key; L42 must not claim it appears in OpenAPI |
| `app.py` `InfoQuery :232`, `ModelQuery :237`, schema route `:373-375` | exact | `return GearParams.model_json_schema()` untransformed |
| `app.js` lines in `<canonical_refs>` (`:10-11 :47 :53 :99 :103 :111 :123 :131 :142 :158 :239 :284 :403 :405 :410`) | all exact | `style.css` `:91 :112 :122-124 :125-126` exact |
| `test_api.py` `:173`, tokens `:205-226` | exact (`for snippet in (` at `:205`, loop end `:226`) | no-field-name rule: comment block starts `:228`, `rest = ...` `:234`, `for name in GearParams.model_fields:` `:242`, `writes_a_field_shut` `:259`, `relations = re.search(...)` `:307`, `writes_a_value` `:310` |
| `test_relations.py` `:111 :258 :313 :348` | exact | `OPS` `:59`, `EXTRA_KEYS` `:61`, `KEYWORDS_2020_12` `:67`, `LEGACY` `:81` |
| `test_browser.py` steps `:320 :329 :563 :615 :814 :877 :904` | exact | also `webgl2 :307`, `first build drawn :365`, `href after showModel :394`, `invalid field marked :412`, `warning rendered :449`, `link round trip :490` |
| `browser_session.py` `:268 :273 :298 :303 :323 :376 :476 :524` | exact | `Swept :469`, `eval_pairs :279`, `_js_number :312` |
| `calc.py` keyway refusals `:652-667`, hex sentence `:1166` | exact | the f-string `Hex bore replaces the round profile: ...` is at `:1166` |
| `Makefile golden.regen :277`, `HEAVY_TEST_FILES :25`, `ideas/INDEX.md :13`, `bench/RESULTS.md :5318` | exact | |
| hex-warning debt "Next step"/INDEX row | file at `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md`, INDEX row `docs/tech_debt/INDEX.md:39` | trigger wording below |
| root_shape=bogus debt "Related files" line numbers (`66-69`, `96-100`, `103-109`) | stale since L41 (enum branch is still `app.js:66-69`; `readHash` is `:103-108`, `gearQuery` `:111-117`) | not this phase's to fix; the trigger text is unchanged |

### Exact current tokens of the pins [VERIFIED: tests/test_api.py:205-226, read verbatim]
The 19 collapsed-whitespace substrings of `test_the_shareable_link_round_trips_every_field_through_generic_code` (`re.sub(r"\s+", " ", snippet) in collapsed_source`):
1. `for (const [name, prop] of Object.entries(schema.properties)) {`
2. `fields.set(name, { input, wrap, title, rels: prop.enabled_when ?? [], reason });`
3. `for (const [name, { input }] of fields) input.value = h.get(name) ?? defaults[name];`
4. `mateInput.value = h.get('mate_teeth') ?? ''; applyRelations(); }`
5. `q.set(name, input.value)`
6. `const infoQ = new URLSearchParams(q);`
7. ``history.replaceState(null, '', hash ? `#${hash}` : location.pathname + location.search);``
8. `navigator.clipboard.writeText(location.href)`
9. `window.addEventListener('hashchange', () => { readHash(); update(); });`
10. `form.addEventListener('input', () => { applyRelations(); scheduleUpdate(); });`
11. `mateInput.value = ''; applyRelations(); update();`
12. `return input.value === '' ? defaults[name] : input.value;`
13. `const have = Number(effective(field));`
14. `default: throw new Error(`
15. `for (const { input, wrap, rels, reason } of fields.values()) {`
16. `const off = rels.map(holds).includes(false);`
17. `wrap.classList.toggle('inactive', off);`
18. `reason.textContent = off ?`
19. `input.setAttribute('aria-describedby', reason.id)`

Other assertions in the same test (all must keep holding):
- **DIMS cut-out + field-name rule** (`:232-246`): `rest` = source minus the `const DIMS = [ ... ];` block; for every name in `GearParams.model_fields`: `not re.search(r"""['"]""" + re.escape(name) + r"""['"]""", rest)` and `not re.search(r"\." + re.escape(name) + r"\b", rest)`. This covers comments too: a quoted field name in an `app.js` comment fails it. The 31 names (MEASURED) include `module` and `teeth`; no selector-natural JS property (`title`, `group`, `options`, `label`, `when`, `field`, `op`, `value`) is a field name.
- **`writes_a_field_shut`** (`:259-270`) over the whole `app.js`: `.disabled|.hidden|.readOnly|.inert =`, `setAttribute/toggleAttribute('disabled'|'hidden'|'readonly'|'inert')`, `classList.add/toggle('hidden'|'disabled'|'readonly'|'inert')`, `.innerHTML`, `insertAdjacentHTML`, `.style.display|visibility|pointerEvents|opacity`, `.style.setProperty('display'|...)`. `classList.toggle('pending', ...)`, `new Option(...)`, `selectedIndex =` and `focus()` are not matched.
- **`writes_a_value`** (`:310`) applied to `relations.group(1)` where `relations = re.search(r"-- relations \(L41\)\n(.*?)\n// -+ messages\n", source, re.DOTALL)` (`:307`): `\.value\s*=(?!=)|\.(?:reset|setRangeText)\(|removeAttribute\(\s*['\"]value['\"]`. The span from the `-- relations (L41)` banner to the `// ---- messages` banner must contain no `.value =`. `selectedIndex = i` does **not** match, but the pick handler's `input.value = String(value)` does, so the selectors section must sit outside that span (before the relations banner, or after the messages banner). The banner strings `-- relations (L41)` and `// ---- messages` must not be edited.
- **`test_every_key_the_ui_reads_is_a_derived_dimensions_field`** (`:126-153`): `dims_keys = re.findall(r"^\s*\['(\w+)',", source, re.MULTILINE)` must equal the same harvest of the `DIMS` block alone, and `len >= 15`. No line of `app.js` outside `DIMS` may start with `['word',`.
- `test_schema_drives_the_form` (`:58-65`): add one selectors assertion here.

Which tokens a design edits (this is the "tightened, never deleted" arithmetic the plans need): if `deriveSelectors();` is written next to `applyRelations();` at the three call sites then tokens **4, 10 and 11** are rewritten to the longer strings (`... applyRelations(); deriveSelectors(); }`, `... { applyRelations(); deriveSelectors(); scheduleUpdate(); }`, `... applyRelations(); deriveSelectors(); update();`). Token 3 and token 4 stay intact if the call is placed between the `for` line and the `mateInput.value` line of `readHash()`. If the call is made *inside* `applyRelations()` (after its `for`), no existing token changes at all. ROADMAP SC1's "field-name pin and DIMS-key pin hold with an empty diff" is about the `for name in GearParams.model_fields` rule and the `['word',` harvest, which stay byte-identical under any of these; the token list is what D-16 says to tighten. The two readings are compatible; the plans should say which.

### Browser-test hooks the new code must not break [VERIFIED: tests/test_browser.py, tests/browser_session.py]
- `form built` (`:320-327`): `expect(page.locator("form#params [name]")).to_have_count(field_count)` with `field_count = len(properties)`; a nameless select is not counted.
- `form from schema` (`:329-363`): `rendered` = `[...document.querySelectorAll('form#params [name]')].map(e => e.name)` must equal the schema's grouped order; `legends = page.locator("form#params legend").all_text_contents()` must equal `list(groups)` (so no extra `legend`, and the selector does not add a group); `shown = page.locator("form#params label.field .name").all_text_contents()` must equal the field titles (so a selector wrapper that is `label.field` with a `.name` span **fails** unless this list is extended; an own class avoids it).
- `inert fields` (`:615-812`): the shown-reasons JS is `[...document.querySelectorAll('form#params label.field')].filter(l => getComputedStyle(l.querySelector('.reason')).display !== 'none').map(l => l.querySelector('[name]').name)`: a `label.field` wrapper with no `[name]` child makes `l.querySelector('[name]')` `null` and `.name` throw, and one with no `.reason` throws in `getComputedStyle(null)`. Another query lists every `form#params .reason` whose `aria-hidden !== 'true'` as a failure: any `.reason` element the selector adds must be `aria-hidden="true"`. `form#params [aria-describedby]` is mapped by `e.name`.
- `INACTIVE_PAIRS` (`browser_session.py:273`): `form#params label.field.inactive` -> `l.querySelector('[name]').name` / `.reason`; `FORM_PAIRS` (`:268`): `form#params [name]`. Neither sees a nameless select in a non-`label.field` wrapper.
- `golden sweep` (`:563-613`): asserts `swept[name].query == pinned[name]` and the dimmed set equals `expected_inactive(...)`; the comment at `:571` already says "Phases 23-24 change the form and must leave this file's diff empty (D-09)".
- `sweep()` (`browser_session.py:476-521`): the fresh-load record (empty link) is read from the first page load (`fresh_inactive = eval_inactive(page)`), every other record after `hashchange`; a new select read must be taken at both places. `Swept` is `NamedTuple(query, inactive)` (`:469`); its only consumers are `test_browser.py` and `tests/capture_requests.py:40-44` (`{name: s.query for name, s in swept.items()}`), so a third field is safe for the regen script (23-RESEARCH Pitfall 6).
- `tests/test_browser_pins.py` scans every `tests/*browser*.py` plus `tests/capture_requests.py` for AST `Name`/`Attribute`/`ImportFrom` spellings in `{importorskip, skip, skipif, xfail, pytestmark, getenv, environ}` (`environ` allowed on lines naming `SPUR_` or `PLAYWRIGHT_BROWSERS_PATH`). New browser-test identifiers must avoid those words (for example a local named `skip`). `tests/test_selector.py` is not in that scan set.

### Hex-warning debt and root_shape=bogus debt [READ]
- `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md`, "Next step" ends: `Revisit when Phase 24's bore-shape selector ships (choosing Hex leaves both defaults, so every hex part warns) or a user reports the warning as noise.` INDEX row (`docs/tech_debt/INDEX.md:39`) trigger column: `Phase 24's bore-shape selector ships (choosing Hex leaves bore_d and bore_flat at their defaults, so every hex part warns), or a user reports the warning as noise`. The file's `Related files` are `src/spur/calc.py:1166`, `src/spur/params.py:102` and `:105`, and the `warning rendered` step. D-17 restates the "Next step" paragraph; the INDEX row's trigger column should follow in the same commit. MEASURED: `derive(GearParams(bore_hex=6))` warns `Hex bore replaces the round profile: bore_d (9 mm) and bore_flat (8 mm) are ignored.` so every selector-made Hex part (which keeps `bore_d=9`, `bore_flat=8`, D-11) carries that warning.
- `docs/tech_debt/active/2026-10-10-root-shape-bogus-loads-a-blank-select.md`: `Revisit when Phase 23 or 24 touches `buildForm`'s enum rendering, or when a user reports a link that loaded a blank select.` The enum rendering is `app.js:66-69` (`if (prop.enum) { input = document.createElement('select'); for (const v of prop.enum) input.add(new Option(v, v)); }`). A selector built by a new function called after the `for` loop at the end of `buildForm()` adds lines to `buildForm()` but does not touch that branch; L41 verified this by comparing the branch, `gearQuery()` and the `DIMS` block as byte-identical in the 23-01 verify, which the L42 verify can repeat. The selector's own no-match state (Finding 5) is the same *failure class* as that debt (a select with no matching option reads `''`, `selectedIndex -1`), so the plan must handle it in the selector's code, not lean on the debt.

## Findings the CONTEXT does not hold

### Finding 1: model-level emission, inheritance, and OpenAPI [MEASURED]
Scratch copy of the whole `src/spur` package with the Pattern 1 edit, imported via `PYTHONPATH` (confirmed `spur.__file__` pointed at the scratch copy):
- `list(GearParams.model_json_schema())` -> `['description', 'properties', 'selectors', 'title', 'type']`; before the edit `['description', 'properties', 'title', 'type']`. Comparing the two JSON dumps with `selectors` popped from the new one: identical (`properties` untouched).
- `selectors[0]` is emitted verbatim, key-sorted per object (`group, options, title`; each condition `field, op, value`), list order kept.
- `"selectors" in InfoQuery.model_json_schema()` -> `True`; `ModelQuery` -> `True`; `GearParams.model_config["frozen"]` still `True`.
- `app.openapi()` before/after: `cmp` reports identical; `InfoQuery`/`ModelQuery` are not in `components.schemas`.
- With the edit, `tests/test_relations.py` + `tests/test_api.py -k "relation or schema or openapi or keyword or extra or construction or literal or shareable"` -> `59 passed, 59 deselected in 6.17s`: nothing existing goes red.

### Finding 2: what the existing tests are blind to for a model-level key [READ + MEASURED]
- `test_no_extra_key_is_a_json_schema_keyword` (`test_relations.py:348-358`) builds `contributed` only from `GearParams.model_fields[...].json_schema_extra`; the model-level key is invisible to it (that is why the 59 above still pass). The CF-3 guarantee ("no key the model contributes is a JSON Schema word") therefore needs an explicit assertion for `selectors`: `"selectors" not in KEYWORDS_2020_12 | LEGACY` (importable names, `test_relations.py:67`, `:81`). Scope it to the top-level key. Nested keys inside the selector object include `title`, which **is** in `KEYWORDS_2020_12` (`test_relations.py:78`); that is harmless because a validator does not interpret the value of an unknown keyword as a schema, but a naive recursive collision check would fail on it. D-05 says "the keyword-collision test extends to the new key": a one-line assertion in `test_selector.py` satisfies it without touching `test_relations.py`; editing `test_relations.py` is also allowed (it is the collision test's home) but D-12 scoped that file to field-relation proofs.
- `test_every_relation_is_well_formed_and_emitted_unchanged` (`:313`) iterates `GearParams.model_fields` only; the selector's `when` lists get no well-formedness check until `test_selector.py` runs `_conditions()` over them.
- `test_both_construction_styles_build_their_extra_through_one_helper` (`:361`) AST-counts `Field(..., json_schema_extra=...)` calls (expects 3); a `ConfigDict(...)` call is not a `Field` call, so it stays 3.
- `tests/test_cli.py::test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order` (`:198`) reads `["properties"]` only; unaffected.

### Finding 3: exact `mypy --strict` typing [MEASURED]
Pattern 1 above. `ConfigDict.json_schema_extra` accepts a `JsonDict`; `list(conditions)` of a `tuple[JsonDict, ...]` inside a `JsonDict`-annotated dict literal type-checks (no `JsonValue` annotation needed); a stored `list[JsonDict]` variable does not (error text above). The pydantic mypy plugin (`pyproject.toml` `plugins = ["pydantic.mypy"]`) was active. `from __future__ import annotations` is already at `params.py:8` and does not matter for a class-body expression. ruff selects `E501` at 100 columns and `ERA` (commented-out code): keep option lines under 100 and keep any comment from containing code-like text such as `when("bore_hex", "eq", 0)`.

### Finding 4: a select pick bubbles `input` to the pinned form listener [MEASURED + DOCS]
Probe (Chromium headless shell, `page.select_option`): a `<select>` inside a `<form>` logged `['sel:input', 'form:input:s:true', 'sel:change', 'form:change:s']` (target-phase `input`, then `input` bubbled to the form, then `change`). Programmatic `select.value = ...` and `select.selectedIndex = ...` fire no event (empty log). DOCS: the HTML Living Standard's "send select update notifications" fires `input` (bubbles, composed) and then `change` (bubbles) at the select. [CITED: html.spec.whatwg.org/multipage/form-elements.html#send-select-update-notifications]
Consequence for `form.addEventListener('input', () => { applyRelations(); scheduleUpdate(); });` (`app.js:403`, pinned token 10): on a pick it runs before any `change` handler. With `deriveSelectors()` added beside `applyRelations()` it would snap the select back to the derived option (the click looks undone, D-09's rejected option), clear the pending `.reason`, and `scheduleUpdate()` would fire a duplicate `api/info` 350 ms later, which breaks the browser step's "pending pick sends no request" assertion. The handler must therefore be on the select's `input` event and call `event.stopPropagation()` (target phase runs before the form's bubble phase), or the form listener must be given a target guard (which rewrites token 10 further). `stopPropagation` keeps the form listener, and its token, unchanged apart from the derive call.
Keystroke typing into a numeric field is unaffected: its `input` event targets the number input, runs the form listener, and `deriveSelectors()` there is what ends a pending state with "a typed number lands on the chosen option".

### Finding 5: totality holds on [0, inf) only; the form accepts negatives [MEASURED]
- Python grid over `{0, default-or-6}` for `bore_d`, `bore_flat`, `bore_hex` (8 cells) and `{0, default-or-6, maximum}` (27 cells): every cell has exactly one option; defaults derive as `['D-flat']`.
- With `-1` in the grid (`{-1, 0, 6}`, 27 cells): 13 cells match no option, none match two. `<input type=number min=0>` keeps `'-1'` (`i.value = '-1'` -> `'-1'`, `Number` -> `-1`), so `#bore_d=-1` and typing `-1` reach `holds()` with `-1`. `'1e999'`, `'abc'`, `'NaN'`, `'Infinity'` and padded strings sanitize to `''` (then `effective()` returns the default); `'-0'` -> `Number(-0) === 0` is `true`; `'1e-400'` keeps its text and `Number` gives `0`; `'0.0'`, `'00'`, `'9.0'` keep their text (so the write rule's `Number(effective(f)) !== value` comparison, not a string comparison, is what keeps a re-formatted `0.0` from being rewritten).
- The server answers a negative with a 422 (`ge=0`), so this is the 422 path D-06 wants the select to "follow the fields under". With `shown === undefined`, `shown.label` (or any dereference) throws inside `readHash()`/the `input` listener, and the `readHash(); update();` pair never reaches `update()`: the WR-01 incident, which is documented at `app.js:151-157` for `applyRelations()` and fixed there with a per-field `try/catch`. The same applies to an unknown `op` in a selector option (`holds()` throws by design, `app.js:136`): `deriveSelectors()` must be total and caught per selector, and decide what the select shows with no matching option (`selectedIndex = -1` is the blank state the existing enum debt documents; an explicit extra "no matching shape" option would be a second state to prove). The browser step needs one out-of-range link (for example the minimum minus one step of `bore_d`, derived from the schema) that asserts the form still builds the part.

### Finding 6: `derive()` cannot tell Round from D-flat; the round-trip test must carry more [MEASURED]
`derive(GearParams()).model_dump() == derive(GearParams(bore_flat=0)).model_dump()` -> `True`, differing keys `set()`. Likewise `derive(No bore with flat 8) == derive(No bore with flat 0)` -> `True`. `bore_effective`/`hex_across_flats`/`hex_across_corners`: default and Round `9.15 / None / None`; Hex (`bore_hex=6`) `None / 6.15 / 7.101` plus the warning `Hex bore replaces the round profile: bore_d (9 mm) and bore_flat (8 mm) are ignored.`; No bore `None / None / None`. `GearParams() == GearParams(bore_flat=0)` -> `False` (params differ, hashes differ). So a test that asserts only "`derive()` of the selector path equals `derive()` of the typed path" passes for a Round pick that writes nothing. SC3's wording is about the composed `derive()` document, which stays as asserted; D-12(c) already adds "the resulting `GearParams` makes the option hold". Add the changed-field set (selector path vs the typed flat dict) as a third assertion, and anchor the option labels to what `derive()` *can* see (Hex <-> `hex_across_flats is not None`; No bore <-> `bore_effective is None and hex_across_flats is None`; Round/D-flat <-> `bore_effective is not None`). Round versus D-flat is distinguishable only by the field help text (`bore_flat`: "0 = round bore", `params.py:106`) and the kernel (`model.py`, out of this slice), so a swapped Round/D-flat label pair is not caught by any kernel-free check; the browser step's expected link shapes (Round -> `bore_flat=0`) are what pin it.

### Finding 7: doctored options and what the grid check says [MEASURED]
Exclusivity/totality over the 8-cell `{0, positive}` grid, against deliberately wrong option lists (cells that match not-exactly-one option, of 8): good 0; D-flat's `bore_flat gt 0` -> `bore_hex gt 0` (wrong field) 1 cell (`(9.0, 8.0, 0)` matches none); Round's `bore_flat eq 0` -> `gt 0` (wrong op) 2 cells (`(9.0, 0, 0)` none, `(9.0, 8.0, 0)` both Round and D-flat); Round loses `bore_flat eq 0` (overlap) 1 cell (`(9.0, 8.0, 0)` both); No bore dropped (gap) 2 cells. These are the predictions for D-12(d)'s "wrong field, wrong op, overlapping option". As Phase 23 did, structure the checker as a function taking the selector list as an argument so a doctored copy can be fed to it permanently (23-RESEARCH Pitfall 2, "Make the evidence permanent"), and record one red on the real model too.

### Finding 8: the 44 golden links reach three of the four states [MEASURED]
Applying the D-02 options to `fixture_hashes()` (default-filled like `expected_inactive`): D-flat 32, Round 4, No bore 8, Hex 0. Example records: `README:export-defaults` (empty link) D-flat; `README:export-teeth-24` (`bore_flat=0&module=1&pressure_angle=20&teeth=24`) Round; `test_api.py::test_impossible_mate_is_a_warning_not_a_number` (`bore_chamfer=0&bore_d=0&bore_flat=0&...`) No bore. No fixture record sets `bore_hex` (consistent with the debt file), so the `golden sweep` cannot exercise Hex derivation; the new step's `#bore_hex=6` load must (D-13 already says so).

### Finding 9: the scenario has six independent pages; one `page.on("request")` sees one [MEASURED]
`test_browser.py` opens `browser.new_page()` six times (`:305` main, `:503` `page2`, `:580` `sweep_page`, `:623` `fresh`, `:830` `bad`, `:886` `fresh`). MEASURED: two `browser.new_page()` pages have `p1.context is p2.context` -> `False`, and a `p1.on("request")` listener did not see a request made by `p2`. D-14's "a `page.on("request")` listener installed before the first step records every `/api/*` request" therefore covers the main page only, and the 44-link sweep (on `sweep_page`) is the page whose requests matter most. Two ways to cover all pages: (a) one `context = browser.new_context()` with `context.on("request", ...)` and `context.new_page()` at the six sites (and `sweep()` still takes a `Page`); (b) a helper that opens a page and attaches the same recorder, replacing the six calls. `tests/capture_requests.py:40` is unaffected (it does not record). The hash half of BS-2 is cheap: `update()` builds the hash from the same `infoQ` it sends (`app.js:242-245`), so each `/api/info` query's keys are the hash's keys by construction; a direct `location.hash` read is still wanted where the step already reads `FRAGMENT`. `Request` events fire for routed/aborted STL requests too (the sweep's `expect_request` on `/api/info` relies on the same event with the STL route aborted).

### Finding 10: the write rule's order and the stash's edges (CONTEXT internal tension) [READ]
- `<specifics>` sketches the rule as "write `eq` conditions, then for each `gt` with `Number(effective(field)) === 0` restore the stash or mark pending". D-09 says a pending pick "writes nothing", and D-12(c) says "when a `gt` field is 0 the rule writes nothing and the state is unchanged". Example where the orders differ: link `#bore_hex=6&bore_d=0`, pick Round: the `eq` writes would zero `bore_hex` (and `bore_flat` if set) while `bore_d` has no stash, leaving a changed part (it becomes the No bore state) under a "pending Round". The plan-then-write order (decide pending from the `gt` conditions first, then perform any writes) is the one D-09/D-12 require. The Python mirror in `test_selector.py` must be written in the same order; its "pending leaves the flats unchanged" assertion is what fails the sketch's order.
- Options' `eq` and `gt` field sets are disjoint per option (Round: eq `bore_hex`, `bore_flat` / gt `bore_d`; D-flat: eq `bore_hex` / gt `bore_d`, `bore_flat`; Hex: gt `bore_hex`; No bore: eq `bore_hex`, `bore_d`), so one pick never zeroes a field it then needs. A walk assertion for that disjointness is cheap and keeps it true for a future selector.
- The restore must be checked against the condition: a stash holding `'-1'` or `'0.0'`, restored into a `gt 0` field, still leaves the option false. Use `stash.has(field)` (a stashed `''` from an emptied box is falsy but restores correctly to the default) and re-test `Number(value) > condition.value` after choosing the stash string; otherwise treat as pending.
- D-08 clears the stash on Reset only. `hashchange` and `readHash()` do not clear it, so a stash taken under link A survives into link B (for example Round stashes `bore_flat='8'`; the user opens `#bore_flat=0&teeth=24`; picking D-flat restores `8`, a value link B never contained). This is a permitted-but-surprising reading of D-08, not a contradiction of it; see Open Question 2.
- Pick -> request: a pick that writes calls `applyRelations()`, `deriveSelectors()` and `update()` directly; `update()` rewrites the hash with `history.replaceState` (no `hashchange`), and `gearQuery()` keeps `bore_flat=0` because `String('0') !== String(8)` (`app.js:114`), giving `#bore_flat=0` as D-07 states.

### Finding 11: pending state wiring [READ]
`applyRelations()` rewrites every field's `reason.textContent` and the `aria-describedby` of every field on every call (`app.js:159-170`), and `update()` does not touch them. So a pending `.reason` text on the target field survives until the next `applyRelations()`, which is exactly "pending ends at the next re-derive" provided `deriveSelectors()` always runs with it and clears `.pending`. The pending row needs `aria-describedby` on the target input (set by the selector code, removed by `applyRelations()`'s `else` branch) or screen readers miss it. `need({field, op, value})` (`app.js:142`) already builds `${title} above ${value}` / `${title} = ${value}` from `fields.get(field).title`; the pending wording is a prefix on top of it, and the test derives the same string with `_title()` and `_js_number()`. `focus()` fires no `input` event. `.field .reason { grid-column: 1 / -1 }` and `.field .reason:empty { display: none }` (`style.css:125-126`) only apply inside `.field`; the target field's `.reason` is inside its own `label.field`, so the pending text renders there with no new CSS. `.pending` itself should extend the `.field.inactive` tone (`style.css:122-124`: `color: var(--muted)` and `border-style: dashed`, no opacity) using only custom properties defined in both themes (`--muted`, `--line`, `--accent`, `--fg`, `style.css:1-35`). The `.field` grid, input/select styling (`style.css:91-109`) are written against `.field`, so an own-class wrapper must list itself in those rules.

### Finding 12: environment and baselines [MEASURED]
HEAD `87462cb`, clean tree. `make verify.fast`: `896 passed in 15.49s`, `real 16.16`, exit 0 (load averages 2.45 4.47 3.70). `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"`: `2 passed in 13.09s`; steps: `webgl2` 0.03, `form built` 0.10, `form from schema` 0.02, `first build drawn` 3.94, `href after showModel` 0.04, `invalid field marked` 0.12, `warning rendered` 0.28, `link round trip` 0.38, `golden sweep` 0.32, `inert fields` 1.31, `unknown relation op` 4.10, `download name` 1.16, `root_shape=bogus as today` 0.10 s (13 steps; the scenario is one of the 2 tests; the other is the oracle test). `bench.machine_facts()` -> `12 CPUs, arm64, 32.0 GiB RAM`; Python 3.12.13, playwright 1.63.0, pytest 9.1.1. Node v22.23.1 and Docker 29.4.0 are present but unused (the gate needs no Docker).

## Runtime State Inventory

Omitted: this is not a rename/refactor/migration phase (no string is renamed, no stored data, service config, OS registration, secret or build artefact carries a bore-shape name; nothing persists the selector: it is never in the URL, `localStorage` or a cookie).

## Common Pitfalls

### Pitfall 1: the form `input` listener re-derives the select before the pick handler runs
**What goes wrong:** pick fires `input` (bubbles to `form`) then `change`; the pinned listener runs `applyRelations(); ...` first and snaps the select back; `scheduleUpdate()` then sends a duplicate request after 350 ms.
**Why:** `form.addEventListener('input', ...)` (`app.js:403`, token 10) is on the form, and a select inside the form bubbles.
**How to avoid:** selector handler on the select's `input` with `event.stopPropagation()`. MEASURED order above.
**Warning signs:** a pending pick whose `.pending` class vanishes immediately; an `api/info` request appearing 350 ms after a pending pick.

### Pitfall 2: no matching option throws out of `readHash()`
**What goes wrong:** `#bore_d=-1` (or a typed `-1`) makes every option false; `shown.label` throws; `update()` is skipped; the part, dimensions and download links go stale while the form moves (WR-01 class, L08).
**How to avoid:** total `deriveSelectors()` (`selectedIndex = -1`, no `.pending`, no throw), a per-selector `try/catch` as in `applyRelations()` for an unknown op, and one schema-derived out-of-range link in the new step. Do not claim totality for the browser; claim it for `GearParams`-valid triples.

### Pitfall 3: the `writes_a_value` span
**What goes wrong:** putting the pick handler (`input.value = String(value)`) between the `-- relations (L41)` banner and the `// ---- messages` banner makes `test_the_shareable_link_round_trips_every_field_through_generic_code` red. **How to avoid:** a new banner outside that span.

### Pitfall 4: a wrapper that is `label.field` without a `[name]` child
**What goes wrong:** `inert fields` throws a `TypeError` in the shown-reasons evaluation, `form from schema`'s title list gains an entry. **How to avoid:** own wrapper class (D-16 option A), or extend both reads deliberately (D-16 option B) and re-run both steps.

### Pitfall 5: `derive()` equality alone passes a no-op pick
See Finding 6. A Round pick that writes nothing leaves the document identical to the default's.

### Pitfall 6: the request listener sees one page
See Finding 9. A listener on the main `page` leaves the 44-link sweep unguarded.

### Pitfall 7: the Hex pick carries the hex warning
Every selector-made Hex part (defaults `bore_d=9`, `bore_flat=8` kept, D-11) warns `bore_d (9 mm) and bore_flat (8 mm) are ignored`. That is the debt file's trigger firing; do not filter it in `app.js` (the debt file says so) and do not add a `warning rendered`-style assertion that a selector-made Hex link is silent.

### Pitfall 8: fragment assignment races on a fresh page
23-RESEARCH Pitfall 9 / 22 Pitfall 2: a fragment assigned after `goto("/")` can be erased before `buildForm()` returns (one in about a dozen runs). For `#bore_hex=6` and `#bore_d=0` loads put the fragment on the `goto` URL with `serve_stl_from(page, stl)` (as `inert fields` does); use `_follow_link` only on an already-built page.

### Pitfall 9: running the browser file outside `make`
The Makefile exports `PLAYWRIGHT_BROWSERS_PATH := $(abspath $(VENV))/ms-playwright`; a bare `pytest tests/test_browser.py` looks in the default cache and fails with `Executable doesn't exist` (23-RESEARCH Pitfall 11). Use the `make test PYTEST_ARGS=...` commands below.

### Pitfall 10: the `whole-word` unfinished-work scan
`make no-fake-done` greps `*.py` and `*.js` for whole words `TODO|FIXME|XXX|HACK|NotImplementedError` (`Makefile:141-144`). The word "pending" is fine.

## Code Examples

### The pick plan, order-correct (illustrative JS; values and names from D-02/D-07/D-08, shape is a sketch for the plans to refine)
```javascript
// Not a field name anywhere: everything comes from selector.options[i].when.
function planPick(chosen) {
  const writes = [];            // [field, value-string, stash-string|undefined]
  let pending = null;           // the condition that cannot be made true
  for (const c of chosen.when) {
    if (c.op === 'eq' && Number(effective(c.field)) !== c.value) {
      writes.push({ field: c.field, to: String(c.value), was: fields.get(c.field).input.value });
    }
  }
  for (const c of chosen.when) {
    if (c.op !== 'gt' || holds(c)) continue;
    const kept = stash.has(c.field) ? stash.get(c.field) : null;
    if (kept !== null && Number(kept === '' ? defaults[c.field] : kept) > c.value) {
      writes.push({ field: c.field, to: kept, was: undefined });   // restore: not stashed again
    } else {
      pending = c; break;                                         // no write at all
    }
  }
  return pending ? { pending } : { writes };
}
```
`holds(c)` here reads `effective(c.field)`; a zeroing write earlier in `writes` is on a different field (the disjointness above), so evaluating `holds` before the writes is sound.

### Python mirror of the same rule (kernel-free, for `tests/test_selector.py`)
```python
def pick(flat: dict[str, float], stash: dict[str, float], chosen: list[Condition],
         defaults: dict[str, float]) -> dict[str, float] | None:
    """None = pending (writes nothing). Else the flats after the pick."""
    def have(f: str) -> float:                            # effective(): an absent key is the default
        return flat.get(f, defaults[f])

    after = dict(flat)
    for field, op, value in chosen:
        if op == "gt" and not have(field) > value:
            kept = stash.get(field)
            if kept is None or not kept > value:
                return None
            after[field] = kept
        elif op == "eq" and have(field) != value:
            after[field] = value                          # the browser writes the string "0"
    return after
```
(Illustrative sketch, not run. The pending check precedes any write, as in the JS sketch.) The assertions per state: `GearParams(**after)` validates; every condition of `chosen` holds on it (`_condition_holds`); `set(after) - set(flat)` equals the predicted minimum; `derive(GearParams(**after)).model_dump() == derive(GearParams(**typed_flat)).model_dump()`; the label's `derive()` class (Finding 6).

### Request recorder across pages (browser test; sketch)
```python
seen: list[str] = []
context = browser.new_context()
context.on("request", lambda request: seen.append(request.url) if "/api/" in request.url else None)
page = context.new_page()   # and context.new_page() at the five other sites
# after every step:  names = {k for url in seen for k, _ in urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query)}
#                    assert names <= set(properties) | {"quality", "mate_teeth"}
```
(`properties` is the schema's property map the test already holds; no field name is a literal.)

### Select read for `sweep()` / `Swept` (names no bore word)
```python
SELECTED_OPTION = (
    "() => [...document.querySelectorAll('form#params select:not([name])')]"
    ".map(s => s.selectedIndex < 0 ? '' : s.options[s.selectedIndex].text)"
)
```
(one entry per selector; a second selector later is a longer list, not a new key).

## State of the Art

| Old approach | Current approach | When changed | Impact |
|--------------|------------------|--------------|--------|
| A `BORE_SHAPES` constant in `app.js` (PITFALLS BS-4's pragmatic route) | model-level `json_schema_extra` list in the L41 vocabulary | Phase 24 kickoff decision 9, D-01 | `app.js` names no bore field; the field-name pin is untouched |
| "No conditional form behaviour" (08 D-09) | `enabled_when` (L41, Phase 23) | 2026-10-11 | the evaluator the selector reuses |

**Deprecated/outdated:** none relevant.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Firefox/Safari fire `input` then `change` for a user pick as the HTML spec says (only Chromium headless shell was measured) | Finding 4 | If a browser fired only `change`, `stopPropagation()` on `input` would never run and the selector would not work there; the gate tests Chromium only |
| A2 | The new step's cost on `ubuntu-latest` is not measured here (the step builds nothing; macOS reading only) | Validation Architecture | A CI-only slowness would show on the PR's first CI run, not in the local readings |
| A3 | A recorder via a shared `browser.new_context()` does not change the behaviour of the existing steps (each currently runs in an isolated context) | Finding 9 | A step that relied on a fresh cookie/storage state could behave differently; option (b) (a helper that attaches the recorder to each independent page) avoids it |

## Open Questions

1. **Where does `deriveSelectors()` sit relative to `applyRelations()`, and which pin tokens are rewritten?**
   - Known: beside it at three sites rewrites tokens 4, 10, 11; inside it rewrites none; D-06 and D-16 say three call sites and tightened pins.
   - Unclear: nothing contradicts; only the plan must pick and say so in L42.
   - Recommendation: follow D-06/D-16 (beside, three sites, tokens 4/10/11 rewritten longer, new tokens for the selector loop, write rule, stash, `stopPropagation`).
2. **Does a `hashchange` (or any `readHash()`) clear the stash?**
   - Known: D-08 clears on Reset only; reload clears by being a reload (Finding 10).
   - Unclear: a stash from link A surviving into link B.
   - Recommendation: keep D-08 as written (smallest rule); if the human wants it cleared, a `stash.clear()` at the top of `readHash()` is one more token and one more browser assertion. Surface at plan check.
3. **What does the select show for an out-of-range triple?**
   - Known: `selectedIndex = -1` is the blank state (Finding 5), and the server 422s the same link.
   - Unclear: blank versus an explicit extra option.
   - Recommendation: blank, uncaught-throw-free, with one browser assertion; an extra option is a fifth state to prove and is the human's call.
4. **Wrapper class (D-16 leaves it to Claude).** Recommendation: an own class (not `label.field`), so the two existing reads (`form from schema` titles, `inert fields` shown-reasons) stay byte-identical; share the grid/input rules in `style.css` by listing the new class in the `.field` selectors.
5. **Request recorder shape (Finding 9).** Recommendation: attach the recorder to every page via one helper or a shared context; choose in the plan, state in the step's comment which pages it covers.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `.venv` Python | all tests | yes | 3.12.13 | — |
| pydantic / mypy / ruff / pytest | gate | yes | 2.13.5 / 2.3.1 / 0.16.8 / 9.1.1 | — |
| Playwright + Chrome Headless Shell | browser step | yes | 1.63.0 / `chromium_headless_shell-1243` | `make test` installs it via the `$(BROWSER)` stamp |
| `make` | every command below | yes | — | — |
| Docker | only `make check` (not needed for `make verify`) | yes | 29.4.0 | not required |
| Node | only `make vendor-check` (bundle unchanged by this phase) | yes | v22.23.1 | not required |

**Missing dependencies with no fallback:** none. **With fallback:** none.

## Validation Architecture

`.planning/config.json` has no `workflow.nyquist_validation` key (it holds `workflow._auto_chain_active`, `workflow.use_worktrees`, `workflow.ui_safety_gate`, `git.branching_strategy`), so the section is included.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 + xdist + cov; Playwright 1.63.0 (Chrome Headless Shell) for `tests/test_browser.py` |
| Config file | `pyproject.toml` (`filterwarnings = ["error", ...]`, `fail_under = 96`, mypy strict + `disallow_any_explicit` over `tests/`) |
| Quick run command | `make verify.fast` (static steps + the commit slice; `896 passed`, 16.16 s at HEAD; L36 kill 30 s); `tests/test_selector.py` joins it |
| Targeted kernel-free | `make test.fast PYTEST_ARGS="tests/test_selector.py -n0 -q -rf"` |
| Targeted API pins | `make test PYTEST_ARGS="tests/test_api.py -n0 --no-cov -q -k 'schema_drives_the_form or openapi_documents or every_key_the_ui_reads or shareable_link_round_trips or root_shape_link'"` (23-01's command, reused verbatim) |
| Targeted browser | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"` |
| Browser pins | `make test.fast PYTEST_ARGS="tests/test_browser_pins.py -n0 -q"` |
| Golden pin byte-identity | `make golden.regen` then `git diff --exit-code tests/regression/golden_requests.json` (23-03 pattern, log `23-03-golden-regen.log`) |
| Full suite command | `make verify` (ruff, mypy `--strict`, import-linter, unfinished-work scan, pytest `-n 8` with coverage; about 290-300 s at Phase 23) |

Log-file conventions (Phase 22/23, reused): kept under `.planning/phases/24-bore-shape-selector/investigation/`, named `24-NN-<what>.log` (`24-01-browser-red.log`, `24-01-browser-green.log`, `24-NN-selector-red.log`, `24-NN-wrong-option-red.log`, `24-NN-golden-regen.log`, `24-NN-reading-{1,2,3}.log`, `24-NN-verify.log`). Every log ends with its own exit line:
- browser: `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s" > .planning/phases/24-bore-shape-selector/investigation/24-NN-reading-N.log 2>&1; echo "make test exit $?" >> .planning/phases/24-bore-shape-selector/investigation/24-NN-reading-N.log`
- commit slice: `{ /usr/bin/time -p make verify.fast; } > .../24-NN-slice-N.log 2>&1; echo "make verify.fast exit $?" >> .../24-NN-slice-N.log`
- gate: `make verify > .../24-NN-verify.log 2>&1; echo "make verify exit $?" >> .../24-NN-verify.log`
A non-green run is kept as `24-NN-red-N.log` and classified before the next run (23-04's rule: a second red stops the plan; the known `resource-tracker` flake debt `2026-10-06-resource-tracker-flake-fails-the-gate` has a fixed signature). Thresholds 23-04 used: the new step over 15 s, or a `make verify.fast` over 25 s, stops the plan with a `checkpoint:decision` (never move a wait or a bar).

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-selector-schema-carried | `/api/schema` carries `selectors`; each option's `when` well-formed (`_conditions`), fields in `model_fields` and numeric, `title`/`label`/`group` non-empty strings, `eq`/`gt` field sets disjoint per option, `"selectors"` not a JSON Schema word; emitted list equals the model's | unit (kernel-free) | `make test.fast PYTEST_ARGS="tests/test_selector.py -n0 -q -rf"`; names of the shape `test_every_selector_option_is_well_formed_and_emitted_unchanged`, `test_selectors_is_not_a_json_schema_keyword` | no - Wave 0 |
| same | a `GET /api/schema` assertion beside `test_schema_drives_the_form` (`props` check) and the field-name / DIMS-key pins unchanged | integration (`TestClient`) | the targeted API-pins command | file yes, edit |
| same | `app.js` names no bore field; selectors section outside the relations span; new exact tokens (selector loop over `schema.selectors`, three derive calls, the write rule, the stash, `stopPropagation`) | static | the targeted API-pins command (`test_the_shareable_link_round_trips_every_field_through_generic_code`) | yes, rewritten in-task |
| REQ-selector-derives-and-writes-through | exactly one option holds on the `{0, positive}` grid and at the defaults (D-flat); labels anchored to `derive()` classes | unit | `tests/test_selector.py`, `test_exactly_one_option_holds_on_the_grid_and_the_default_is_dflat` | no - Wave 0 |
| same | the Python pick mirror: writes only `eq` conditions' fields, plans before it writes, pending writes nothing, stash restore re-tested against the condition, picking the shown option writes nothing | unit | `tests/test_selector.py`, `test_a_pick_writes_the_minimum_and_a_pending_pick_writes_nothing` | no - Wave 0 |
| same | derivation under the 44 golden links equals the Python derivation; `golden_requests.json` and `pre_v0_2.json` diff empty | e2e + git | targeted browser command; `git diff --exit-code tests/regression/pre_v0_2.json tests/regression/golden_requests.json` after every task | step edit; files exist |
| same | picks from the default and each reachable state: captured `api/info` query equals the mirror's; pending Hex: no request, hash unchanged, `.pending`, `bore_hex` focused; typing lands on Hex; stash restore; Reset clears the stash; `#bore_hex=6` loads Hex with `bore_d`/`bore_flat` dimmed; `#bore_d=0` loads No bore; one out-of-range link keeps building; the keyed Hex link keeps its `.invalid`/`.inactive` pair | e2e | targeted browser command (one new named step after `inert fields`) | no - Wave 0 (the step) |
| same | no non-`GearParams` key in any `/api/*` request or the hash, across all six pages | e2e | targeted browser command (recorder + assertion after every step and at the end) | no - Wave 0 |
| REQ-selector-round-trips-per-state | per state (Round, D-flat, Hex, No bore) and from the default: the selector path and the typed path give the same `GearParams`, the same `derive()` document, and the chosen option holds | unit | `tests/test_selector.py`, `test_each_state_round_trips_through_the_selector_and_through_the_flat_fields` (parametrised over the schema's options, no label literal) | no - Wave 0 |
| same | meta-reds: a doctored selector list (wrong field / wrong op / overlap / gap) is fed to the checker and turns it red | unit | `tests/test_selector.py`, `test_a_wrong_option_goes_red` | no - Wave 0 |
| closing | idea retired with INDEX row moved; debt "Next step" restated; L42 appended; `web-ui.md` paragraph; README `:138` mentions `selectors` | doc + git | `test -f docs/ideas/retired/2026-09-27-bore-shape-selector-in-the-web-form.md`; `git grep -c "bore-shape-selector" docs/ideas/INDEX.md`; the commit-subject precondition check pattern from 23-04 | n/a |

### Failure signals (what each is when red)
- Exclusivity/totality: a cell lists the labels that matched (`[]` = gap, two labels = overlap), as in Finding 7.
- Round-trip: `set(after) - set(flat) != predicted`, a validation error, or the chosen option false on the result; a no-op Round pick fails the changed-field assertion, not the `derive()` equality.
- Pins: the failing token string is the assertion message (`assert re.sub(...) in collapsed_source, snippet`).
- Browser: the step name rides the failure as a note (`step: <name>`); the golden-sweep message names the record and the select value it read versus the Python derivation; the request recorder message names the page, the step and the foreign key.

### Sampling Rate
- **Per task commit:** `make verify.fast` (pre-commit hook) plus the task's targeted line, plus `git diff --exit-code tests/regression/pre_v0_2.json tests/regression/golden_requests.json`.
- **Per wave merge:** the API-pins command and the browser command, each log kept.
- **Phase gate:** `make verify` green, log kept ending `make verify exit 0`; state the command and its result line (CLAUDE.md).

### Red-first evidence the project expects (Phase 23's record, reused)
Each new proof is run red once before the code it pins exists, or with one deliberate break, and the first failure line is recorded in the plan SUMMARY (`## Seen red`) and in `bench/RESULTS.md` under `### Seen red once (Phase 24)` as a table `| Plan | Test or step | Deliberate break | First failure line | Reverted |`:
- the pins: `test_the_shareable_link_round_trips_every_field_through_generic_code` and `test_schema_drives_the_form` written against the unchanged `params.py`/`app.js` (23-01: `KeyError: 'enabled_when'` and `AssertionError: fields.set(...)`, no kept log; keep a log this time);
- `tests/test_selector.py` against a model with no `selectors` key (TDD red, log `24-NN-selector-red.log`, like `23-02-relations-red.log`: `3 failed, 7 passed`);
- a wrong option on the real model (wrong field, wrong op, overlap), each `make test.fast PYTEST_ARGS="tests/test_selector.py -n0 -q -rf" > .../24-NN-wrong-option-red.log`, reverted by copying the saved good `params.py` back and proving it with `cmp` plus a `grep -c` count (23-02's method) or `git checkout -- <file>` plus `git diff --exit-code -- <file>` (23-03's method);
- browser reds by deliberate break, one each: delete the `deriveSelectors()` call from `readHash()` (`golden sweep` select read), delete it from `#reset`, drop `stopPropagation` (the pending pick sends a request), drop the stash restore; first failure line and `step:` note copied from the kept log;
- the fixed regen proof: `make golden.regen` writes a byte-identical `golden_requests.json` (`23-03-golden-regen.log`).
The gate-cost reading follows 22 D-06 / 23-04 (`### The inert-fields step, priced (23-04)` in `bench/RESULTS.md`): `## Bore-shape selector (Phase 24)`, `#### Host state` (`bench.machine_facts()` -> `12 CPUs, arm64, 32.0 GiB RAM`; chip via `sysctl -n machdep.cpu.brand_string`; `sw_vers -productVersion`, `uname -r`; Python, playwright, pytest versions; `HEAD`; UTC read window; `ps -A -o %cpu=,comm= | sort -nr | head -5` for background load), `#### Readings` table `| Run | Result line | step <name> (s) | step golden sweep (s) | step first build drawn (s) | 1-minute load before -> after | UTC start |` for three runs one at a time in the foreground, and "other readings are quoted, not compared". Today's quoted baselines: `golden sweep` 0.32 s, `inert fields` 1.31 s, `first build drawn` 3.94 s, whole file `2 passed in 13.09s` (this research, load 4.74); the commit slice 16.16 s (load 2.45). 23-04 also took three `make verify.fast` readings once a proof module joined the slice; `tests/test_selector.py` does the same, so repeating that table is consistent with L36 even though D-15 names only the step.

### Wave 0 Gaps
- [ ] `tests/test_selector.py` (kernel-free, imports `_conditions`, `_condition_holds`, `_properties`, `KEYWORDS_2020_12`, `LEGACY` from `test_relations`; cross-test import verified to work, but `tests/test_hooks.py` documents a preference for a copy over one ("three lines beat a cross-test import"), `tests/composition.py` is the shared-module precedent: D-12 already chose the import)
- [ ] `selectors` on `GearParams.model_config` (the red state for the test above is its absence)
- [ ] `deriveSelectors()` / `buildSelectors()` / pick handler / stash in `app.js`; `.pending` and the wrapper class in `style.css`
- [ ] browser step (name and placement after `inert fields` are discretion), `Swept` third field, the select read in `sweep()` (both the fresh-load branch and the `hashchange` branch), the request recorder and its end-of-step assertion
- [ ] pin rewrite in `tests/test_api.py` (tokens 4/10/11 per the placement chosen, new tokens, the selector-section placement assertion)
- Framework install: none.

### Manual-only
| Behavior | Requirement | Why Manual | Test Instructions |
|---|---|---|---|
| The pending state and the selector row read well in both themes (dashed tone, reason row, focus ring) | REQ-selector-derives-and-writes-through | the step proves the rules exist and the computed values differ, not that it reads well (23-VALIDATION's same judgement row) | open `/`, pick Hex, check the select and `Hex bore A/F` in light and dark; type `6` and check the dim on `Bore Ø`/`D-flat` |

## Security Domain

`security_enforcement` is absent from `.planning/config.json`, so this section is included.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | server-side `GearParams` bounds stay the authority; the selector adds no client trust (writes are the same strings a user types); labels/titles reach the DOM through `textContent` / `new Option(text, value)` only |
| V6 Cryptography | no | — |

### Known Threat Patterns for this stack
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Schema-supplied label or title rendered as markup (DOM XSS) | Tampering/Elevation | never `innerHTML`/`insertAdjacentHTML`; the `writes_a_field_shut` regex in `test_api.py` already bans both across `app.js` (T-23-01) |
| Selector name leaking into the URL / API (parameter pollution; the server ignores unknown query keys) | Tampering | no `name`, not in `fields`, request-subset assertion across every page (BS-2, D-14) |
| An unreadable selector option (unknown op) silently choosing a state | Tampering | `holds()` throws; caught per selector; shown state undetermined, never "active" |
| Stash holding user input | Information disclosure | in-memory `Map` only; never written to storage or the URL; cleared on Reset |

## Project Constraints (from CLAUDE.md)

- Gate is `make verify` (ruff, mypy `--strict`, import-boundary contracts, unfinished-work scan, pytest); state the command and the result line in the reply. `make verify.fast` is the commit-time slice (hook, 30 s kill, L36).
- Two standing rules: a number the tool prints is a number someone will cut metal to (L08); a parameter the user did not set must never silently change the part, defaults stay absolute mm (L05), a direct conflict is a 422 not a guess (L03). The pending state and the plan-then-write order are this phase's expression of the second rule.
- Stop and ask when: an architectural claim is not in the decision log; a locked decision looks wrong; library behaviour is unverified; evidence conflicts (D-05's OpenAPI claim and the `<specifics>` write-order sketch are two such conflicts, both recorded above for the plan check); a destructive operation is involved.
- New non-trivial choice -> options + recommendation -> human picks -> new `Lxx` (L42 is next). Cite decisions by id.
- Keep it simple; surgical edits; one concern per commit; Conventional Commits, normal prose; commits end with the attribution line from the session reminder.
- New behaviour ships with its tests in the same change; no `TODO`/`pass`/unreachable branches; `make verify` fails on the markers.
- Capture ideas/debt as one file per item from `docs/<dir>/TEMPLATE.md` with an INDEX row in the same commit; flip debt to resolved in the fixing commit; state in the final reply whether anything was filed.
- Code style (`docs/CODING_VALUES.md`): comments carry the measurement or constraint; `calc.py` never imports `cadquery`; vendor types stop at their boundary; validate once at `GearParams`; English throughout.
- Project skills: none (`.claude/skills/README.md` and `.ai_skills/README.md` list none).

## Sources

### Primary (HIGH confidence)
- Repo files read this session with line citations above: `src/spur/params.py`, `src/spur/app.py`, `src/spur/calc.py:648-670,1160-1170`, `src/spur/static/app.js`, `src/spur/static/style.css`, `src/spur/static/index.html`, `tests/test_api.py`, `tests/test_relations.py`, `tests/test_cli.py:198-258`, `tests/test_browser.py`, `tests/browser_session.py`, `tests/capture_requests.py`, `tests/test_browser_pins.py`, `tests/test_hooks.py:15-60`, `Makefile`, `pyproject.toml`
- `.planning/phases/24-bore-shape-selector/24-CONTEXT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` (Phase 24), `.planning/STATE.md`, `.planning/research/PITFALLS.md` (BS-1..BS-4)
- `.planning/phases/23-conditional-form-fields/` (`23-RESEARCH.md` Common Pitfalls and Validation Architecture, `23-VALIDATION.md`, `23-02-SUMMARY.md`, `23-04-PLAN.md` commands), `.planning/phases/22-download-name-carries-the-root/22-VALIDATION.md`, `bench/RESULTS.md` `## Conditional form fields (Phase 23)` (`:5318`)
- `docs/architecture/decision_log.md` L41 (`:2567`), `docs/architecture/web-ui.md`, `docs/ideas/{INDEX.md,TEMPLATE.md,2026-09-27-bore-shape-selector-in-the-web-form.md,retired/2026-09-29-conditional-form-fields.md}`, `docs/tech_debt/{INDEX.md, active/2026-10-11-hex-bore-warns-about-default-bore-fields.md, active/2026-10-10-root-shape-bogus-loads-a-blank-select.md}`
- HTML Living Standard, "send select update notifications": https://html.spec.whatwg.org/multipage/form-elements.html#send-select-update-notifications (fetched this session)
- MEASURED probes (session scratchpad, not committed): `probe_params.py`, patched `srccopy/spur/params.py` run through mypy/ruff/pytest/openapi comparisons, `events_probe.py`, `num_probe.py`, grid and doctored-option scripts, a two-page context probe, `derive()` equality probes, `baseline-browser.log`, `baseline-fast.log`

### Secondary (MEDIUM confidence)
- none

### Tertiary (LOW confidence)
- none (the cross-browser event-order claim is the only extrapolation; see A1)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH, nothing new; versions read from the venv.
- Architecture: HIGH, measured emission/typing/events; the plan-then-write and no-match findings are derived from CONTEXT's own rules plus measured browser behaviour.
- Pitfalls: HIGH for the five MEASURED ones (bubbling, negatives, derive blindness, per-page listener, OpenAPI); MEDIUM for hashchange/stash semantics (a reading of D-08, recorded as Open Question 2).

**Research date:** 2026-10-12
**Valid until:** 2026-11-11 (stable local code; invalidated by any edit to `app.js`, `test_api.py`'s token list, `browser_session.py` or the pydantic/playwright pins)
