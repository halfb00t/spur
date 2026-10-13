# Phase 24: Bore-Shape Selector - Pattern Map

**Mapped:** 2026-10-12 (HEAD 6c8fb15)
**Files analyzed:** 13 new/modified
**Analogs found:** 13 / 13 (all analogs are git-tracked source; no mirror paths)

Line numbers are from the current tree. Where 24-RESEARCH.md measured something (pick event order,
no-match state, mypy typing, pin arithmetic), this file points at it instead of repeating it.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/spur/params.py` (model_config selector list + option helper) | model/config | transform (schema metadata) | `params.py` `when()` :17, `_extra()` :29 | exact (same file) |
| `src/spur/static/app.js` (`buildSelectors`, `deriveSelectors`, pick handler, stash) | component | event-driven | `app.js` relations section :129-175 + wiring :401-416 | exact (same file) |
| `src/spur/static/style.css` (`.pending`, selector wrapper) | config (style) | n/a | `style.css` `.field.inactive` :122-124 | exact |
| `tests/test_selector.py` (NEW, kernel-free) | test | transform | `tests/test_relations.py` | exact |
| `tests/browser_session.py` (`Swept`, `sweep()`, Python derivation) | test utility | request-response | `expected_inactive()` :323, `eval_inactive()` :298, `sweep()` :476 | exact (same file) |
| `tests/test_browser.py` (golden sweep extension, new step, request listener) | test | request-response | `golden sweep` :563, `inert fields` :615 | exact (same file) |
| `tests/test_api.py` (pins tightened) | test | transform (source scan) | `test_the_shareable_link_round_trips_every_field_through_generic_code` :173 | exact (same file) |
| `docs/architecture/decision_log.md` (L42) | doc | n/a | L41 at :2567 | exact |
| `docs/architecture/web-ui.md` (selector paragraph) | doc | n/a | relation paragraph :17-28 | exact |
| `docs/ideas/` retirement + INDEX | doc | n/a | `docs/ideas/retired/2026-09-29-conditional-form-fields.md` + `INDEX.md` Retired table | exact |
| `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md` + INDEX row :39 | doc | n/a | its own "Next step" paragraph | exact |
| `bench/RESULTS.md` (`## Bore-shape selector (Phase 24)`) | doc | n/a | `## Conditional form fields (Phase 23)` :5318 | exact |
| `tests/test_relations.py` (optional one-line keyword-collision) | test | transform | `test_no_extra_key_is_a_json_schema_keyword` :348 | exact (see Finding 2; D-12 prefers the assertion in `test_selector.py`) |

## Pattern Assignments

### `src/spur/params.py` (model, schema metadata)

**Analog:** `src/spur/params.py` itself.

**Imports already present** (:8-14): `JsonDict` from `pydantic.config`, `ConfigDict`, `Literal`. No new import.

**Condition builder to reuse** (:17-27): `when(field, op: Literal["eq","gt"], value) -> JsonDict` returns `{"field","op","value"}`. Every option condition goes through it (L41: selector options are `when()` conditions, not a second vocabulary).

**List-invariance copy** (:29-42), the fix the option helper must copy:
```python
        # The copy is the type fix: `list[JsonDict]` is not a `JsonValue` by list
        # invariance, so assigning it directly fails `mypy --strict`; `list(...)` of it
        # passes (23-RESEARCH Pitfall 1, measured).
        extra["enabled_when"] = list(enabled_when)
```

**Attachment point** (:56): `model_config = ConfigDict(frozen=True)` becomes `ConfigDict(frozen=True, json_schema_extra={"selectors": [...]})`. The measured-good shape is 24-RESEARCH Pattern 1 (`_option(label, *conditions)` returning `{"label": label, "when": list(conditions)}`, one `BORE_SHAPE: JsonDict = {"title","group","options":[...]}`). Pass the list inline or `list(...)` it: a pre-built `list[JsonDict]` variable in the dict fails mypy (Finding 3). No `# type: ignore` (Makefile `no-fake-done`). Keep lines under 100 columns and comments free of code-like text (ruff E501, ERA).

**Option set** is D-02 verbatim, declaration order Round, D-flat, Hex, No bore. Field titles the pending reason will read: `bore_d` "Bore Ø" (:102), `bore_flat` "D-flat" (:105), `bore_hex` "Hex bore A/F" (:123).

**Existing Bore comment block** (:96-101) explains the relations in terms of calc; add a sentence there, with the measurement or constraint, for the selector (CODING_VALUES: comments carry the why).

No `calc`, `model`, `pool`, `app.py`, `cli` edit. `InfoQuery.model_json_schema()` inherits the key but `/openapi.json` is byte-identical (24-RESEARCH Drift table); L42 must not claim it reaches OpenAPI.

---

### `src/spur/static/app.js` (component, event-driven)

**Analog:** `app.js` relations section (:129-175) and wiring (:401-416). Place the new code under its own banner OUTSIDE the span `-- relations (L41)` ... `// ---- messages` (test_api.py `writes_a_value` forbids `.value =` inside that span; the pick handler writes `input.value`). Do not edit those two banner strings.

**State and shared evaluator to reuse** (:10-11, :123-146):
```javascript
const fields = new Map(); // name -> { input, wrap, title, rels, reason }
const defaults = {};

function effective(name) {
  const { input } = fields.get(name);
  return input.value === '' ? defaults[name] : input.value;
}
function holds({ field, op, value }) {
  const have = Number(effective(field));
  switch (op) {
    case 'eq': return have === value;
    case 'gt': return have > value;
    default: throw new Error(`Unknown enabled_when op: ${op}`);
  }
}
function need({ field, op, value }) {
  const { title } = fields.get(field);
  return op === 'eq' ? `${title} = ${value}` : `${title} above ${value}`;
}
```

**Build site:** a function called at the end of `buildForm()` (after the pinned loop closes at :100, so the Bore fieldset exists in `groups`). Fieldset lookup uses the `groups` Map built at :50-62 (keyed by group title; the legend text equals the selector's `group`). The selector must be a first child row after the `legend`, built outside `Object.entries(schema.properties)` (pinned token 1, :53). `buildForm()` currently has no return value and `schema` is local; pass `schema.selectors` and `groups` into the new function.

**DOM row copied from the field row** (:73-91): `.name` span, `.control` span, a `.reason`-style span with `aria-hidden="true"` (browser test `inert fields` fails on any non-hidden `.reason`). Constraints (D-16, 24-RESEARCH): the `<select>` has NO `name`; the wrapper is NOT `label.field` (own class sharing the grid rules), or `form from schema`'s `label.field .name` list is extended; an `id` derived from metadata, no bore word.
```javascript
    const nameEl = Object.assign(document.createElement('span'), { className: 'name', textContent: title });
    ...
    reason.setAttribute('aria-hidden', 'true');
```
Enum options precedent (:66-69, do NOT touch this branch; the root_shape=bogus debt trigger): `input.add(new Option(v, v));` use `new Option(label, index)` in the new function.

**Derive pattern** (copy applyRelations' per-item try/catch, :158-173):
```javascript
  for (const { input, wrap, rels, reason } of fields.values()) {
    try { ... } catch (err) {
      wrap.classList.remove('inactive');
      reason.textContent = `Cannot tell whether this field is used: ${err.message}`;
```
`deriveSelectors()`: per selector `options.find(o => o.when.every(holds))`, caught per selector, total on no match (`selectedIndex = -1`; negatives such as `#bore_d=-1` match no option, Finding 5) so a throw never skips `update()`. Clears `.pending`. Never writes a field.

**Call sites (three, D-06):** end of `readHash()` (:103-108), the form `input` listener (:403), `#reset` (:410-415):
```javascript
form.addEventListener('input', () => { applyRelations(); scheduleUpdate(); });
window.addEventListener('hashchange', () => { readHash(); update(); });
$('#reset').addEventListener('click', () => {
  for (const [name, { input }] of fields) input.value = defaults[name];
  mateInput.value = '';
  applyRelations();
  update();
});
```
Adding `deriveSelectors();` rewrites pinned tokens 4, 10, 11 to longer strings (24-RESEARCH pin arithmetic); calling it inside `applyRelations()` changes none. Plans must state which. `#reset` also does `stash.clear()`.

**Pick handler:** on the select's `input` event with `event.stopPropagation()` (a pick bubbles `input` to the form listener, which would re-derive and schedule a duplicate request; MEASURED, Finding 4). Plan first (pending check), then write: for each `eq` condition of the chosen option where `Number(effective(field)) !== value`, stash `input.value` and set `input.value = String(value)`; for each `gt` condition with `Number(effective(field))` not above the threshold, restore the stash or mark pending (wrapper `.pending`, focus the field, fill its own `.reason` via `need()`; no write, no request, no hash). A writing pick then calls `applyRelations(); deriveSelectors(); update();` directly (as `hashchange` does). The select is never in `fields`, never read by `applyRelations()` (D-11).

**Guards the new code must not trip** (tests/test_api.py :228-270): no quoted field name or `.field_name` access outside `DIMS` (even in comments); no `.disabled/.hidden/.readOnly/.inert =`, `.innerHTML`, `.style.display|...`; no line starting `['word',` outside `DIMS`. `classList.toggle('pending', ...)`, `selectedIndex =`, `focus()`, `new Option` are not matched.

---

### `src/spur/static/style.css` (`.pending`)

**Analog:** `.field.inactive` (:122-124) and `.field` grid (:91-96):
```css
.field.inactive .name, .field.inactive .unit,
.field.inactive input, .field.inactive select { color: var(--muted); }
.field.inactive input, .field.inactive select { border-style: dashed; }
.field .reason { grid-column: 1 / -1; font-size: .78rem; color: var(--fg); }
.field .reason:empty { display: none; }
```
`.pending` reuses the tone (`--muted`, dashed control border) with only the existing custom properties (THEME_VARIABLES pinned non-empty). If the wrapper is not `label.field`, share the grid rules by adding its class to the `.field` selectors (:91-96, :104-111). No opacity, pointer-events or visibility (see the comment above :122).

---

### `tests/test_selector.py` (NEW, test, transform)

**Analog:** `tests/test_relations.py` (kernel-free, commit slice). Not in `HEAVY_TEST_FILES` (`tests/test_hooks.py:25` lists `test_model, test_pool, test_api, test_cli, test_browser`; do not add it).

**Imports to copy** (test_relations.py :37-49): `from spur.calc import derive`, `from spur.params import GearParams, when`, `from collections.abc import Mapping, Sequence`, `from functools import cache`. Reuse the evaluator by import, not copy (D-12; MEASURED to work with `PYTHONPATH=tests`; check how pytest's rootdir/`conftest` puts `tests` on the path before writing `from test_relations import ...`):
```python
Condition = tuple[str, str, float]                    # :50
def _properties() -> dict[str, dict[str, object]]:    # :94
def _conditions(value: object) -> list[Condition]:    # :111  the one judge of the grammar
def _condition_holds(op: str, have: float, threshold: float) -> bool:   # :258
    return have == threshold if op == "eq" else have > threshold
```
Note `_conditions` asserts `set(item) == {"field","op","value"}`, a non-empty list, and `op in OPS`; it is the walk for each option's `when`.

**Walk pattern to mirror** (test_relations.py :313-345): iterate, assert `emitted == raw`, `list(condition) == ["field","op","value"]`, driver in `GearParams.model_fields`, `GearParams.model_fields[driver].annotation in (int, float)`, and no two conditions share one object (`len({id(o) ...}) == len(...)`). Selector additions: `title`/`label`/`group` non-empty strings; `/api/schema` `selectors` equals `GearParams.model_config["json_schema_extra"]["selectors"]`.

**Keyword collision for the model-level key** (Finding 2): `test_no_extra_key_is_a_json_schema_keyword` (:348-358) only inspects field-level extras. Add `assert "selectors" not in KEYWORDS_2020_12 | LEGACY` (import the names, :67, :81), top-level key only; nested `title` IS a keyword (:78), so do not recurse.

**Proofs required (D-12):** (b) grid over `{0, in-range positive}` for `bore_d`, `bore_flat`, `bore_hex` plus defaults: exactly one option holds. (c) per-state round trip using a Python mirror of D-07/D-08; assert the changed-field set vs the typed dict and option truth, not only `derive()` equality (`derive()` cannot tell Round from D-flat, Finding 6; anchor labels to `bore_effective`, `hex_across_flats`). (d) each proof seen red once against a deliberately wrong option (wrong field, wrong op, overlap), recorded in the SUMMARY (Phase 23 precedent). Derive expectations from the schema; no option label or field name as a literal where avoidable.

---

### `tests/browser_session.py` (test utility)

**Analog:** same file. Expected-state function over the schema and a link: `expected_inactive()` (:323), with `_holds()` (:303) and `_js_number()` (:312) as the shared helpers.

**`_holds`** (:303-309), reuse for the Python derivation (it raises on an unknown op, as `holds()` does):
```python
def _holds(owner: str, op: object, have: float, wanted: float) -> bool:
    if op == "eq": return have == wanted
    if op == "gt": return have > wanted
    raise AssertionError(f"{owner}: the op {op!r} is neither 'eq' nor 'gt' (D-02)")
```
Add `expected_shape(selectors, link)`-style function: read `selectors` from `/api/schema`, an omitted/blank field reads as its default (`properties[name]["default"]`), return the option label whose conditions all hold. It names no field.

**Page read:** model on `eval_inactive` (:298-300) + `INACTIVE_PAIRS` (:273-276) / `eval_str(page, "() => ...")` used in `sweep()`. New JS read of the select's selected option text (nameless select, so it is not seen by `FORM_PAIRS` :268).

**`Swept`** (:469-473) is `NamedTuple(query, inactive)`: add a third field. Only other consumer is `tests/capture_requests.py:40-44` (`{name: s.query ...}`), safe. In `sweep()` (:476-521) read the select at BOTH places: the fresh-load record (`fresh_inactive = eval_inactive(page)`) and after each hashchange (`Swept(urllib.parse.urlsplit(request.value.url).query, eval_inactive(page))`). Avoid identifiers in `tests/test_browser_pins.py`'s banned set (`importorskip, skip, skipif, xfail, pytestmark, getenv, environ`).

---

### `tests/test_browser.py` (test, request-response)

**Analog:** same file. Golden sweep (:563-613), inert fields (:615-812), `step()` (browser_session.py :524-534).

**Golden sweep extension:** after the existing `dim_differs` check (:597-602), add the same shape for the select:
```python
                dim_differs = "; ".join(
                    f"{name}: the page dims {swept[name].inactive}, the schema says {want}"
                    for name, want in wanted_dim.items()
                    if swept[name].inactive != want
                )
                assert not dim_differs, f"golden sweep: the dimmed sets differ: {dim_differs}"
```
Compare `swept[name].shape` with the Python derivation per link; include a "not vacuous" assertion like `assert any(wanted_dim.values()), ...` (golden links reach 3 of 4 states, Finding 11; the new step covers the rest).

**New step** (after `inert fields`, own `with step("...")`, STL routes aborted as in `sweep()`: `page.route(STL_ROUTE, lambda route: route.abort())`; `page.expect_request(lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS)`). Titles from `_title(properties, name)` (:140-144); never literals. Cases are listed in D-13 and 24-CONTEXT Specifics. Include one out-of-range link (Finding 5) asserting the form still builds the part. The `inert fields` step shows the pattern for focused/`.reason` assertions and for the `aria-hidden` failure query; any `.reason` the selector adds must be `aria-hidden="true"`.

**Scenario-wide request listener (D-14):** `page.on("request", ...)` before the first step, on every page the scenario opens (each `browser.new_page()` is its own context, Finding 9; the `golden sweep` page and `inert fields` page are created inside steps). Assert parameter names are a subset of `GearParams.model_fields | {quality, mate_teeth}` taken from the schema, and hash keys a subset of `model_fields | {mate_teeth}`.

**Hooks the new DOM must keep intact:** `form built` (:320, `form#params [name]` count = `len(properties)`), `form from schema` (:329, names, `legend` list equals groups, `label.field .name` equals field titles), `INACTIVE_PAIRS`.

---

### `tests/test_api.py` (pins tightened under L42)

**Analog:** `test_the_shareable_link_round_trips_every_field_through_generic_code` (:173-). The tuple at :205-226 is collapsed-whitespace substring matches:
```python
        assert re.sub(r"\s+", " ", snippet) in collapsed_source, snippet
```
Edits: rewrite tokens 4, 10, 11 only if `deriveSelectors();` is written beside `applyRelations();` at the call sites; ADD tokens for the selector loop over `schema.selectors`, the three derive calls, the write rule and the stash; update the preceding comment block (the "L41 rewrote..." paragraph at ~:195-204) with an L42 paragraph. Never delete a token. The `rest`-minus-`DIMS` field-name rule (:232-246), `writes_a_field_shut` (:259), `writes_a_value` on the relations span (:307-310) and the `['word',` harvest (:126-153) stay byte-identical. `test_schema_drives_the_form` (:58-65) gains one selectors assertion.

---

### `docs/architecture/decision_log.md` (L42)

**Analog:** L41 (:2567-). Shape: heading `## L42 — <claim> (<keeps/supersedes>)`, `Date: 2026-10-12.`, a paragraph naming what stays (L02, L05; follows L41, supersedes nothing), a "Every figure is cited to the SUMMARY sha or bench/RESULTS.md" sentence, then bold-lead paragraphs: `**The carriage**` (D-05), `**The four states**` (D-02), `**Derive / write / stash / pending**` (D-06..D-09), `**The keyway left to the 422**` (D-10), `**The pins it tightens**` (D-16), `**Retired and restated**` (D-17), each ending with its `**Reversibility: ...**`. Do not claim the key reaches OpenAPI.

### `docs/architecture/web-ui.md`

**Analog:** the relation bullet (:17-28): add one bullet after it with the same voice (generic code reads `selectors` from the schema, derives from the fields, never writes on load, is not a field).

### `docs/ideas/` retirement

**Analog:** `docs/ideas/retired/2026-09-29-conditional-form-fields.md` header:
```
Date: 2026-09-29
Status: retired
Retired in: test(23): one flip link ... -- retire the conditional-fields idea
```
`git mv docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md docs/ideas/retired/`, set `Status: retired` and `Retired in:` to the closing commit's subject, delete its row in INDEX `## Open` (the 2026-09-27 row, :13) and add a row to `## Retired` in the format `| date | [title](retired/file.md) | commit subject |`. Same commit as the phase close.

### `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md`

Replace the last sentence of `## Next step` ("Revisit when Phase 24's bore-shape selector ships ... or a user reports the warning as noise.") with "trigger fired: the selector shipped in <sha>; fix as a `/gsd-quick` before Phase 25's reading". Update the `docs/tech_debt/INDEX.md:39` trigger column in the same commit. Do not resolve or move the file.

### `bench/RESULTS.md`

**Analog:** `## Conditional form fields (Phase 23)` (:5318-): intro paragraph (what is priced, no bar set, Phase 25 re-sets it, HEAD sha, `git status --porcelain` clean), then `### ... priced (NN-NN)` with "Three readings of `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"`, one at a time in the foreground, `uptime` before and after", then `#### Host state` bullets (`bench.machine_facts()`, chip, OS, Python/playwright/pytest versions). New heading `## Bore-shape selector (Phase 24)`; figures copied from kept logs, not estimated.

---

## Shared Patterns

### One evaluator, three readers
**Source:** `app.js` `effective()`/`holds()`/`need()` :123-146; `tests/test_relations.py` `_conditions`/`_condition_holds`; `tests/browser_session.py` `_holds`.
**Apply to:** `deriveSelectors`, pick handler, `test_selector.py`, `expected_shape`. No second grammar or evaluator (BS-4).

### Derived, never written on load; a pick writes only `"0"`
**Source:** `applyRelations()` comment (:148-157) and the L05 rule: "never disables, hides or clears the field"; "never from a build's success".
**Apply to:** `deriveSelectors()` and the pick handler. Call only at the three sites; not in `update()`.

### Catch per item so a throw never skips `update()`
**Source:** `applyRelations()` try/catch (:160-172), WR-01 incident (comment :151-157).
**Apply to:** `deriveSelectors()` (no-match and unknown-op).

### Metadata via `when()` with the list copy
**Source:** `params.py` :17-42.
**Apply to:** every option in `model_config`.

### Schema-derived test expectations
**Source:** `_title()` (`test_browser.py:140`), `expected_inactive()`, `_js_number()`.
**Apply to:** all browser assertions: no option label or field name as a literal.

### Pins are tightened, never deleted; goldens stay byte-identical
**Source:** `test_api.py` :195-226 comment and tuple; `git diff --exit-code tests/regression/pre_v0_2.json tests/regression/golden_requests.json` after every task; `make golden.regen` (Makefile :277) is the only mover.

### Gate
**Source:** `make verify` (ruff, mypy --strict, import contracts, unfinished-work scan, pytest). State the command and the result line.

## No Analog Found

None. Two sub-pieces have no code precedent in the tree and use RESEARCH.md: (1) a model-level `json_schema_extra` (no existing `ConfigDict(json_schema_extra=...)`; use 24-RESEARCH Pattern 1, MEASURED under `mypy --strict`); (2) a scenario-wide `page.on("request")` recorder across several pages (no existing one; the closest are the per-step `page.expect_request(...)` calls in `sweep()`).

## Metadata

**Analog search scope:** `src/spur/params.py`, `src/spur/static/{app.js,style.css}`, `tests/{test_relations,test_api,test_browser,browser_session,test_hooks}.py`, `docs/architecture/`, `docs/ideas/`, `docs/tech_debt/`, `bench/RESULTS.md`.
**Tracked-source gate:** `git ls-files` confirmed for `src/spur/static/app.js`, `tests/test_relations.py`, `tests/browser_session.py` and the ideas file; all analogs are ordinary tracked repo paths with no capability-mirror paths.
**Pattern extraction date:** 2026-10-12
