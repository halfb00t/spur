# Phase 23: Conditional Form Fields - Pattern Map

**Mapped:** 2026-10-11
**Files analyzed:** 17 (1 production Python, 2 production static, 7 test files, 7 docs/bench/ledger)
**Analogs found:** 16 / 17 (one partial: the pure-Python parity module has no exact sibling)
**Verified against:** working tree, branch `gsd/phase-23-conditional-form-fields`. Every analog is ordinary tracked source (`git ls-files` checked for `tests/browser_session.py`, `src/spur/static/app.js`, `tests/test_api.py`, `tests/test_cli.py`, `docs/ideas/2026-09-29-conditional-form-fields.md`, `docs/ideas/retired/*`). No gitignored mirror paths are named.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/spur/params.py` (`when()`, `_extra()`, `enabled_when` on `_f()`, 2 `Literal` fields, 11 declarations) | model / config | transform | `_f()` itself (`params.py:17-23`) and the two bare `Field(...)` calls (`:59-65`, `:102-104`) | exact (edited in place) |
| `src/spur/static/app.js` (`effective`, `holds`, `applyRelations`, reason span, 3 call sites) | component | event-driven | `problems()` (`app.js:121-135`) marking `wrap.classList.add('invalid')`; `buildForm()` (`:47-93`) | exact |
| `src/spur/static/style.css` (`.field.inactive`, `.field .reason`) | config (style) | n/a | `.field.invalid` (`style.css:112-115`), `.field small` (`:105`, `:187-188`) | exact |
| `tests/test_relations.py` (NEW, commit slice) | test | transform | `tests/test_cli.py:198` model-driven walk (walk pattern); `tests/test_trochoid.py:85-88,176-200` (kernel-free `derive`/`GearParams` rows); `tests/test_browser_pins.py` (commit-slice, kernel-free shape) | role-match (no module proves a schema/calc parity today) |
| `tests/test_api.py` (3 `app.js` pins tightened, `test_schema_drives_the_form` +1) | test | request-response | same tests, edited in place (`:58-62`, `:123-141`, `:162-215`, `~:393-396`) | exact |
| `tests/test_cli.py` (walk +1 check) | test | request-response | same test (`:198-240`) | exact |
| `tests/browser_session.py` (`sweep()` return shape, Python evaluator, flip links) | utility (test support) | request-response | `sweep()` (`:339-377`), `fixture_hashes()` (`:318`), `eval_str_list` (`:257`) | exact |
| `tests/capture_requests.py` (1-line adaptation) | utility | batch | itself (`capture_requests.py` `sent = sweep(...)`) | exact |
| `tests/test_browser.py` (`golden sweep` extended, new `inert fields` step) | test (e2e) | request-response | `golden sweep` (`:527-556`), `download name` (`:558-583`), `_follow_link` (`:171-182`), `_title` (`:131`) | exact |
| `tests/test_browser_pins.py` (only if a new watched-name guard is needed; likely no edit) | test | n/a | itself | exact |
| `docs/architecture/decision_log.md` (L41) | doc | n/a | L39 (`:2299`), L40 (`:2451`) | exact |
| `docs/architecture/web-ui.md` (relation paragraph) | doc | n/a | its existing "knows no gear geometry" bullet | exact |
| `docs/ideas/` (new: unbacked relations) + `INDEX.md` | doc | n/a | `docs/ideas/TEMPLATE.md`; an existing `docs/ideas/2026-09-2*.md` | exact |
| `docs/ideas/2026-09-29-conditional-form-fields.md` -> `docs/ideas/retired/` + INDEX row | doc | n/a | `docs/ideas/retired/2026-10-08-download-name-carries-the-root-shape.md` (Phase 22 retirement) | exact |
| `docs/tech_debt/active/2026-10-11-hex-warning-on-default-bore-fields.md` (new) + INDEX row | doc | n/a | `docs/tech_debt/active/2026-10-10-group-floor-of-3-is-not-two-pool-workers.md` | exact |
| `bench/RESULTS.md` (`## Conditional form fields (Phase 23)`) | doc | n/a | `## Download name carries the root (Phase 22)` (`bench/RESULTS.md:5252`) | exact |
| `tests/regression/pre_v0_2.json`, `golden_requests.json` | fixture | n/a | NOT EDITED; `git diff --exit-code` after every task | n/a |

## Pattern Assignments

### `src/spur/params.py` (model, transform)

**Analog:** `_f()` and the two bare `Field(...)` calls, same file.

**Current builder** (`params.py:17-23`), the thing `_extra()` factors out:
```python
def _f[T](default: T, ge: float, le: float, *, title: str, group: str,
          unit: str = "", step: float | None = None, help: str = "") -> T:
    extra: JsonDict = {"group": group, "unit": unit}
    if step is not None:
        extra["step"] = step
    return Field(default, ge=ge, le=le, title=title, description=help,
                 json_schema_extra=extra)
```

**The two Literal fields that must share the path** (the CF-3 silent-drop trap):
```python
    root_shape: Literal["radial", "trochoid"] = Field(
        "radial", title="Root shape", description="...",
        json_schema_extra={"group": "Teeth", "unit": ""})          # params.py:59-65
    recess_sides: Literal["both", "top", "bottom", "none"] = Field(
        "both", title="Recess sides", description="Which faces get an annular groove.",
        json_schema_extra={"group": "Recess", "unit": ""})        # params.py:102-104
```

**Target shape** (RESEARCH Pattern 1, run under project `mypy --strict`). Imports already present: `Literal`, `JsonDict`.
```python
def when(field: str, op: Literal["eq", "gt"], value: float) -> JsonDict:
    return {"field": field, "op": op, "value": value}

def _extra(group: str, unit: str = "", step: float | None = None,
           enabled_when: list[JsonDict] | None = None) -> JsonDict:
    extra: JsonDict = {"group": group, "unit": unit}
    if step is not None:
        extra["step"] = step
    if enabled_when is not None:
        extra["enabled_when"] = list(enabled_when)   # NOT `= enabled_when`: list invariance fails mypy --strict
    return extra
```
`_f()` gains `enabled_when: list[JsonDict] | None = None` and calls `json_schema_extra=_extra(group, unit, step, enabled_when)`; the two `Literal` fields become `json_schema_extra=_extra("Teeth")` / `_extra("Recess")` (byte-identical emission to today).

**Declaration site shape** (example on an existing field, `params.py:129-143`):
```python
    spoke_width: float = _f(0.0, 0, 100, title="Arm width", group="Spokes", unit="mm",
                            step=0.05, enabled_when=[when("spoke_count", "gt", 0)],
                            help="Width of each arm, the same along its whole length.")
```
Eleven declarations: `bore_d`, `bore_flat`, `keyway_width`, `keyway_depth` <- `when("bore_hex","eq",0)`; `spoke_width`, `hub_d`, `rim_wall`, `spoke_fillet` <- `when("spoke_count","gt",0)`; `hole_d`, `hole_circle_d` <- `when("hole_count","gt",0)`; `hex_wall` <- `when("hex_cell","gt",0)`. Do not touch any `calc`/`model`/`pool`/`app.py`/`cli` file; add no `GearParams` field. Comments carry the measurement (module convention); no `# type: ignore`, no `Any`.

---

### `src/spur/static/app.js` (component, event-driven)

**Analog:** `problems()` is the precedent for marking a `label.field` from data; `buildForm()` is where the per-field record is built.

**Class-marking precedent** (`app.js:121-135`):
```js
      for (const name of [d.loc?.[1], ...(d.ctx?.fields ?? [])]) {
        fields.get(name)?.wrap.classList.add('invalid');
      }
```
`problems()` owns `.invalid`; `applyRelations()` owns `.inactive`; neither clears the other (keyway pair coexists).

**Element-building idiom to copy for the reason span** (`app.js:77-90`):
```js
    const nameEl = Object.assign(document.createElement('span'), { className: 'name', textContent: title });
    const control = Object.assign(document.createElement('span'), { className: 'control' });
    control.append(input, unit);
    wrap.append(nameEl, control);
    if (prop.description) {
      wrap.append(Object.assign(document.createElement('small'), { textContent: prop.description }));
    }
    groups.get(group).append(wrap);
    fields.set(name, { input, wrap, title });
```
Insert the `<span class="reason" id="reason-NAME">` between `control` and the help `<small>`. Do NOT reuse class `name` (test locators `label.field .name`) and do not put it inside `.control` (grid is `1fr 8.5rem`). Do not touch the `if (prop.enum) {...}` branch (`:66-69`; the `root_shape=bogus` debt trigger).

**Store** (replaces `:92`): `fields.set(name, { input, wrap, title, rels: prop.enabled_when ?? [], reason });` (this changes pinned token `"fields.set(name, { input, wrap, title });"`; see test_api pins).

**New functions** (RESEARCH Pattern 2; a `switch`, never a `['eq', ...]` table, to stay out of the `^\s*\['(\w+)',` DIMS harvest; `textContent` only, never `innerHTML`):
```js
const effective = (name) => {
  const { input } = fields.get(name);          // an absent gate throws: loud, not silent (D-19)
  return input.value === '' ? defaults[name] : input.value;   // same rule gearQuery() sends (D-18)
};
function holds({ field, op, value }) {
  const have = Number(effective(field));
  switch (op) {
    case 'eq': return have === value;
    case 'gt': return have > value;
    default: throw new Error(`unknown enabled_when op: ${op}`);
  }
}
const need = ({ field, op, value }) =>
  `${fields.get(field).title} ${op === 'eq' ? `= ${value}` : `above ${value}`}`;
function applyRelations() {
  for (const { input, wrap, rels, reason } of fields.values()) {
    const off = !rels.every(holds);
    wrap.classList.toggle('inactive', off);
    reason.textContent = off ? `Needs ${rels.map(need).join(' and ')}` : '';
    if (off) input.setAttribute('aria-describedby', reason.id);
    else input.removeAttribute('aria-describedby');
  }
}
```

**Call sites** (exactly three, never on build success, CF-4):
- `readHash()` (`app.js:96-100`): append `applyRelations();` as the last statement (after `mateInput.value = ...`).
- form listener (`app.js:340`): `form.addEventListener('input', scheduleUpdate);` becomes `form.addEventListener('input', () => { applyRelations(); scheduleUpdate(); });`
- `#reset` handler (`app.js:347-351`): call `applyRelations();` after the value reset loop and `mateInput.value = ''`, before `update();`.

**Untouchable verbatim (pinned):** `gearQuery()` body (`app.js:103-109`), and
`window.addEventListener('hashchange', () => { readHash(); update(); });` (`app.js:342`).

---

### `src/spur/static/style.css` (config, n/a)

**Analog:** `.field.invalid` (`style.css:112-115`) and the help-`small` rules.
```css
.field small { grid-column: 1 / -1; color: var(--muted); font-size: .78rem; }
.field.invalid input, .field.invalid select {
  border-color: var(--accent);
  outline: 1px solid var(--accent);
}
/* Field help appears while the field has focus; the title attribute covers hover. */
.field small { display: none; }
.field:focus-within small { display: block; }
```
Add `.field.inactive` (dim `.name` and input colour via `var(--muted)`; do NOT put `opacity` on the whole `.field`/`.control`, it dims the `.invalid` outline, RESEARCH Pitfall 4; no `pointer-events: none`, no `visibility`), and `.field .reason { grid-column: 1 / -1; ... }` hidden when empty (`:empty { display: none }`) and not inheriting the dim. Only existing custom properties (`THEME_VARIABLES` pinned non-empty by the browser test).

---

### `tests/test_relations.py` (NEW, commit slice; test, transform)

**Analog (shape):** `tests/test_browser_pins.py` (kernel-free, reads sources, milliseconds, no playwright), `tests/test_cli.py:198-240` (walks `GearParams.model_fields` and the schema, never the consumer's own list), `tests/test_trochoid.py:85-88` for building kernel-free params.

**Kernel-free params helper to copy** (`tests/test_trochoid.py:85-88`):
```python
def _gear(**fields: object) -> GearParams:
    """A test gear with the bore off: the default 9 mm bore refuses small gears."""
    return GearParams.model_validate(
        {"bore_d": 0, "bore_flat": 0, "bore_chamfer": 0, "recess_sides": "none", **fields})
```

**Model-driven walk idiom to copy** (`tests/test_cli.py:213-224`):
```python
    names = list(GearParams.model_fields)
    literal_fields = [n for n, f in GearParams.model_fields.items()
                      if get_origin(f.annotation) is Literal]
    props = TestClient(spur.app.app).get("/api/schema").json()["properties"]
```
In `test_relations.py` use `GearParams.model_json_schema()["properties"]` instead of `TestClient` (D-13: no `TestClient`, `cadquery`, `playwright`). Imports only `spur.params`, `spur.calc` (`derive`), `pydantic.ValidationError`, `pytest`.

**Contents (RESEARCH Patterns 3 and Code Examples):**
1. Walk: every `field` in `model_fields` and numeric; `op in {"eq","gt"}`; `value` a number (reject `str`, reject `bool`); no dependent is also a driver (depth 1); schema emits the list unchanged.
2. Keyword collision: `KEYWORDS_2020_12 | LEGACY` frozenset (RESEARCH "Keyword-collision test"); assert every key any field's `json_schema_extra` contributes (`group`, `unit`, `step`, `enabled_when`) is outside it.
3. Forward parity per row, bounds from the schema (`minimum`/`maximum`/`step`), at `minimum + step` and `maximum`; classify by outcome; `REFUSED = frozenset({"keyway_width", "keyway_depth"})` as a module constant citing CF-2; inert rows assert `changed == {"warnings"}` AND `f"{dep} ({value:g} mm)"` appears in the joined warnings (Pitfall 2; membership of the fragment, never equality, Pitfall 3); refused rows assert `ValidationError` ctx fields contain driver and dependent.
4. Reverse coverage: each undeclared numeric field set off-default alone must never be named by an "ignored" sentence.
5. Meta-red: the checker is a function taking the relation map; feed it doctored copies for `recess_depth <- bore_hex eq 0` (derive changes `web`) and `bore_chamfer <- bore_hex eq 0` (no ignored sentence) and assert `AssertionError`.
6. `Literal` carrier probe: a throwaway model with a `Literal` field built with `_extra(..., enabled_when=[when(...)])` emits it unchanged.

Do not name any field in a way `app.js` forbids; tests may name fields (only `app.js` may not). `calc` truth sources: hex branch `calc.py:669-672`, keyway x hex refusal `calc.py:652-660`, cutout branches `:781`, `:836`, `:878`, "ignored" sentences `:1159-1167`, `:1207-1218`, `:1220-1229`, `:1231+`. New file joins the commit slice automatically (`tests/test_hooks.py:24` `HEAVY_TEST_FILES` does not list it).

---

### `tests/test_api.py` (test, request-response; pins tightened under L41)

**Analog:** the same tests, edited in place. Never delete or allow-list a pin (CF-1).

**Pin 1: token list** (`test_api.py` ~`:177-190`, inside `test_the_shareable_link_round_trips_every_field_through_generic_code`). Change only this entry to the new exact token (stricter):
```python
        "fields.set(name, { input, wrap, title });",
        ...
        "window.addEventListener('hashchange', () => { readHash(); update(); });",   # must stay
```
Also add stricter tokens for the three call sites (`applyRelations();` in `readHash`, the `input` listener, the `#reset` handler), collapsed-whitespace match like the existing loop (`re.sub(r"\s+", " ", snippet) in collapsed_source`).

**Pin 2: no field name outside DIMS** (~`:196-215`): unchanged, now also a guard that `applyRelations()` carries no field name:
```python
    for name in GearParams.model_fields:
        assert not re.search(r"""['"]""" + re.escape(name) + r"""['"]""", rest), name
```

**Pin 3: DIMS harvest** (`:123-141`): `re.findall(r"^\s*\['(\w+)',", source, re.MULTILINE)`; the new JS must add no line of the `['word',` shape (use `switch`, Pitfall 5).

**Pin 4 (third, not named in CONTEXT)** (`~:393-396`, `root_shape` test): pins `gearQuery()` byte for byte:
```python
    assert ("if (input.value !== '' && String(input.value) !== String(defaults[name])) "
            "q.set(name, input.value);") in source
```
No change: this phase must not touch `gearQuery()`.

**`test_schema_drives_the_form` +1 assertion** (`:58-62`):
```python
def test_schema_drives_the_form() -> None:
    props = client.get("/api/schema").json()["properties"]
    assert props["teeth"]["group"] == "Teeth"
    assert props["module"]["unit"] == "mm"
    assert props["recess_sides"]["enum"] == ["both", "top", "bottom", "none"]
    # add: one relation, e.g. bore_d emits [{"field": "bore_hex", "op": "eq", "value": 0}] unchanged
```
`test_openapi_documents_the_typed_contracts` (`:65`) re-runs unedited with the nested extra.

---

### `tests/test_cli.py` (test, request-response; heavy tier)

**Analog:** `test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order` (`:198-240`), quoted above. Add inside the `for name in names:` loop only: for any `name` whose model `json_schema_extra` carries `enabled_when`, `props[name]["enabled_when"]` equals it; and every `field` in a relation is in `names`. Model-driven, no hand-listed rows. Leave the `literal_fields == ["root_shape", "recess_sides"]` pin alone.

---

### `tests/browser_session.py` (utility, request-response)

**Analog:** `sweep()` (`:339-377`), `fixture_hashes()` (`:318-337`), `eval_str_list` (`:257`).

**Return-shape change** (Pitfall 6): `sweep()` currently returns `dict[str, str]` (name -> query) and ends:
```python
        with page.expect_request(
            lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
        ) as request:
            page.evaluate("link => { location.hash = link; }", link)
        sent[name] = urllib.parse.urlsplit(request.value.url).query
    return sent
```
Return a `NamedTuple` (`query`, `inactive`), reading the inactive set in the same pass right after `expect_request` returns (Pitfall 7: `applyRelations()` ran inside `readHash()` before `update()` fired the fetch). The fresh-load/empty-link record reads it too. Inactive-name read (names no field):
```python
eval_str_list(page, "() => [...document.querySelectorAll('form#params label.field.inactive')]"
                    ".map(l => l.querySelector('[name]').name)")
```
Keep the existing `"equals the page's current fragment"` guard and the `page.route(STL_ROUTE, lambda route: route.abort())` line.

**New helpers** (D-14, D-15; ~10-line evaluator, RESEARCH "Python evaluator"): `_inactive(properties, values)` implementing `eq`/`gt` with an unknown op raising; expected reason text built with `f"{value:g}"` (Pitfall 10) from the gate titles; flip-link derivation: for each distinct `(field, op, value)` gate across the schema, candidates `[minimum + step, maximum]`, first that flips the condition vs the default, link `f"{field}={candidate}"`. Typed for `mypy --strict` with no `Any`. Never use `skip`, `getenv`, `environ`, `pytestmark`, `xfail` as identifiers (`test_browser_pins.py` AST scan).

---

### `tests/capture_requests.py` (utility, batch)

**Analog:** itself. One-line adaptation (Pitfall 6):
```python
            sent = sweep(browser.new_page(), base, hashes)     # today
```
becomes `swept = sweep(...)`; `sent = {n: s.query for n, s in swept.items()}`, so `json.dumps({"records": sent, ...})` is unchanged. Prove it: `make golden.regen && git diff --exit-code tests/regression/golden_requests.json`, then discard (run, do not commit).

---

### `tests/test_browser.py` (test e2e, request-response)

**Analog 1, `golden sweep`** (`:527-556`): extend in place; keep the pin comparison, add the inactive-set comparison against the Python evaluator over `/api/schema`, per record, message naming the record and both sets:
```python
                sweep_page = browser.new_page()
                try:
                    swept = sweep(sweep_page, server, hashes)
                finally:
                    sweep_page.close()
                moved = {
                    name: (pinned[name], swept[name])
                    for name in hashes
                    if swept[name] != pinned[name]
                }
```
(`swept[name]` becomes `swept[name].query`.)

**Analog 2, new `inert fields` step placement and fragment-on-goto** (`:558-583`, `download name`): own page, fragment on the `goto` URL (Pitfall 9), `with step("inert fields"):` placed after `golden sweep`, prints its own wall seconds (22 D-06 reading).
```python
                fresh = browser.new_page()
                try:
                    fresh.goto(server + "/#teeth=23&root_shape=trochoid")
                    expect(fresh.locator("#dl-stl")).to_have_attribute(
                        "href", "api/model.stl?teeth=23&root_shape=trochoid", timeout=BUILD_WAIT_MS
                    )
```
Use `fresh.goto(server + "/#spoke_count=0&hub_d=40")`. Then: `hub_d` `.inactive`, value 40, sent query `hub_d=40`, reason `Needs {_title(...spoke_count)} above 0`; real `fill` of `hub_d` -> next `api/info` carries it, still `.inactive`; one `page.evaluate` that sets `spoke_count`, dispatches `input`, reads the class in the same task (Pitfall 8, "before the 350 ms debounce"); click `#reset` -> inactive set equals the default seven cutout dims; keyway pair under `#bore_hex=6&keyway_width=3&keyway_depth=1.4` is both `.inactive` and `.invalid`.

**Analog 3, link on an already-built page** (`_follow_link`, `:171-182`):
```python
    current = eval_str(page, "() => location.hash.slice(1)")
    assert current != fragment, f"the page is already on #{fragment}: no hashchange would fire"
    with page.expect_request(lambda request: "/api/info" in request.url) as sent:
        page.evaluate("(f) => { location.hash = f; }", fragment)
    return urllib.parse.urlsplit(sent.value.url).query
```
For the model-derived flip links; assertion message says the dim state is independent of the 200/422 answer (D-15). Titles: `_title(properties, name)` (`:131`) mirrors `prop.title ?? name`; never hard-code reason text.

Run targeted: `PLAYWRIGHT_BROWSERS_PATH=$PWD/.venv/ms-playwright .venv/bin/python -m pytest tests/test_browser.py --no-cov -s -q -p no:cacheprovider` or `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"` (Pitfall 11).

---

### Docs, ledger and bench (doc, n/a)

- **`docs/architecture/decision_log.md` L41:** copy paragraph shape of L39 (`:2299`, `## L39 — ... (amends L13 and L36, restates L11)`, `Date:`, a lead paragraph that cites figures only to SUMMARY shas or `bench/RESULTS.md`, then **The choice** (D-xx ids) paragraphs). L41 supersedes 08 D-09, keeps L02, names grammar (D-01..D-03), declared set (D-09), reason rule (D-06), the rewritten pins, and the two files it files.
- **Idea retirement:** `git mv docs/ideas/2026-09-29-conditional-form-fields.md docs/ideas/retired/` and move its `INDEX.md` row, following `docs/ideas/retired/2026-10-08-download-name-carries-the-root-shape.md` (Phase 22). New idea file (unbacked `recess_*` / `bore_flat` relations) from `docs/ideas/TEMPLATE.md` with its INDEX row in the same commit.
- **Debt file** (`Severity: nice`, trigger per CONTEXT discretion), header shape from `docs/tech_debt/active/2026-10-10-group-floor-of-3-is-not-two-pool-workers.md`:
```
# <title>

Severity: must
Status: active
Date: 2026-10-10
Source: phase 21 code review, finding WR-02 (...)
Related files:
- tests/browser_session.py:49 (...)

## Context
```
  plus its `docs/tech_debt/INDEX.md` row.
- **`bench/RESULTS.md`:** new `## Conditional form fields (Phase 23)` beside `## Download name carries the root (Phase 22)` (`:5252`): three readings, `bench.machine_facts()`, load before -> after, `HEAD`, UTC; no A/B.
- **`docs/architecture/web-ui.md`:** gains the relation paragraph.

## Shared Patterns

### Metadata flows model -> schema -> generic form (L02)
**Source:** `src/spur/params.py:17-23`, `src/spur/app.py:373-375` (`/api/schema` returns `GearParams.model_json_schema()` untransformed; no edit).
**Apply to:** every file in this phase. No per-field knowledge in `app.js`; only `DIMS` may name `GearParams` fields (pin at `test_api.py` ~`:196-215`).

### Pins change only to stricter, under an Lxx (CF-1)
**Source:** `tests/test_api.py` pins (above). **Apply to:** the `app.js` edit and the `test_api.py` rewrite land in one commit; the pin and the JS cannot be green apart.

### Regression fixtures are read-only
**Source:** `tests/regression/pre_v0_2.json`, `tests/regression/golden_requests.json`. **Apply to:** every task: `git diff --exit-code tests/regression/pre_v0_2.json tests/regression/golden_requests.json` is clean. `gearQuery()` is not edited.

### Test-support conventions
**Source:** `tests/browser_session.py` (`step()` at `:380`, `eval_str*`, `BUILD_WAIT_MS`), `tests/test_browser_pins.py` (AST scan of watched names). **Apply to:** all browser test code: one scenario function, `with step("...")`, step name in every message; `mypy --strict` over `tests/` (no `Any`); `filterwarnings = ["error", ...]`.

### Typing and style
**Source:** `docs/CODING_VALUES.md`, `CLAUDE.md`. **Apply to:** all Python: comments carry the measurement or constraint; no `TODO`/`FIXME`/`XXX`/`HACK`/`NotImplementedError`; vendor types stop at their boundary; `calc.py` never imports `cadquery`.

### Ledger filing
**Source:** `docs/ideas/TEMPLATE.md`, `docs/tech_debt/TEMPLATE.md`, each dir's `INDEX.md`. **Apply to:** the two new files and the retirement, INDEX row in the same commit.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| (partial) `tests/test_relations.py` parity rows | test | transform | No existing test proves a schema-declared relation against `derive()` warnings/422; compose from `test_trochoid.py` (`_gear`, kernel-free `derive`), `test_cli.py` (model-driven walk) and RESEARCH Pattern 3 |

## Metadata

**Analog search scope:** `src/spur/`, `src/spur/static/`, `tests/`, `docs/ideas/`, `docs/tech_debt/active/`, `docs/architecture/`, `bench/RESULTS.md`
**Files scanned:** ~14 read in part (params.py, app.js, style.css, test_api.py, test_cli.py, test_browser.py, browser_session.py, capture_requests.py, test_browser_pins.py, plus phase 22 PATTERNS, CONTEXT, RESEARCH)
**Pattern extraction date:** 2026-10-11
