# Phase 28: Refuse the Bad Link - Research

**Researched:** 2026-10-21
**Domain:** vanilla-JS form/URL-fragment handling (`src/spur/static/app.js`), Playwright browser-test pins, review-ledger triage
**Confidence:** HIGH (the fix was prototyped and run against the real page, the real pins and the real browser test; see "Prototype evidence")

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Bad-value mechanism (REQ-bad-link-refused)**
- **D-01:** One shared `rejected` map (field name to raw token) covers selects and number boxes. `readHash` fills it, and `gearQuery` sends `rejected.get(name)` for a rejected field in place of the control's value. No stray `<option>` in the select, no placeholder in the number box: the control shows blank or empty, and the server's message plus the field outline say why. One code path.
  - Why not the stray option (ARCHITECTURE 3.7): kickoff put number boxes in scope, and a `type=number` box sanitises `abc` to `''` before code can read it (MEASURED, FEATURES A.2). A side map is needed regardless, so a select-only second mechanism adds cleanup rules for no contract gain.
  - The map is a `Map`/object, never rows in the `['word',` shape (they are harvested as `DIMS` keys, `tests/test_api.py:157-165`).
- **D-02:** Detection: assign the token, then read the control back. A non-empty raw token that reads back as `''` is rejected (select at `selectedIndex` -1, number box sanitised). No per-type enum or numeric check. This covers `bogus`, `Trochoid` (case) and `abc` with one rule. Values the control holds (`22.5`, `-5`, `1e1`) already reach the API and are refused there today, unchanged.
  - Scope is `fields` (GearParams form fields) plus the mate box (D-05). Selector selects (`buildSelectors`, `s.select`) also use `selectedIndex` -1 to mean "no option holds" (`app.js:341-369`). They are not link fields and must not be swept into the map.
  - The pre-pass runs around the pinned `readHash` line (`for (const [name, { input }] of fields) input.value = h.get(name) ?? defaults[name];`) and the pinned end (`mateInput.value = h.get('mate_teeth') ?? ''; applyRelations(); deriveSelectors(); }`), not as a rewrite of them (`tests/test_api.py:240-241`).

**Mark and clear rules**
- **D-03:** A rejected token leaves the map on: an edit of **that** field, Reset, or the next `readHash` (hashchange, back/forward). Editing a different field keeps sending the bad token, so the build stays refused and the address bar stays truthful. "Any edit clears all" was rejected: it is today's bug one keystroke later.
- **D-04:** The fragment keeps the raw token (it is rebuilt from `gearQuery`, which now sends it), so Copy link copies the link as given. The page sends no STL request for it and draws no default part. Both come from the existing path: info is fetched first and `fail()` returns before the STL request.
- **D-05:** `mate_teeth=abc`: the token is sent, the 422 blocks the build, and the server's bare message is shown ("Input should be a valid integer, unable to parse string as an integer", no "Mate teeth:" prefix). **The mate box gets no outline**, because `mate_teeth` is not in `fields` and `problems()` stays unchanged. `L44` records this gap, and the plan states it against success criterion 1 ("mark the field") as the approved reading for the mate box. The literal `'mate_teeth'` already appears in `app.js` and is not a `GearParams` field, so the "no quoted field name outside `DIMS`" rule does not apply to it.
- **D-06:** Blank stays default (kickoff). `L44` states the deliberate mismatch: the page treats `root_shape=` and `teeth=` as "use the default" (a shared link that blanks a field relies on L05), while the API answers 422 for `''` (`literal_error` / `int_parsing`, MEASURED). That is a stricter, separate boundary. No code change and no debt item.

**`L44` content (REQ-bad-link-decision-logged)**
- **D-07:** `L44` records: what is refused (a non-blank token its control cannot hold, D-02), the mechanism (D-01), the clear rules (D-03), blank kept as default with the API mismatch (D-06), unknown keys still ignored, the mate box's message-without-outline (D-05). It amends L39's `root_shape=bogus as today` pin and supersedes L42's recorded observation that the `if (prop.enum)` / `gearQuery` / `readHash` lines are byte-identical. L39 and L42 get no edits: the amendment lives in L44 (append-only log). The pin flip, `docs/architecture/web-ui.md:80`, the debt item's retirement (`2026-10-10-root-shape-bogus-loads-a-blank-select.md` to `resolved/`, INDEX row moved) and the fix land in one commit.
- **D-08:** Red-first, per PITFALLS: (1) apply the fix with the old pin untouched and record the `root_shape=bogus as today` step's first failure line (that step, not an earlier one); (2) rewrite the pin to the new contract plus steps for `recess_sides=bogus`, `teeth=abc`, `mate_teeth=abc`, recovery on edit and Reset, and "valid link leaves nothing marked"; (3) revert only the `app.js` fix and record the new pin going red. Both lines go under "Seen red once". Old step names stay in `bench/RESULTS.md` as history.

**`root_fillet` label (REQ-root-fillet-label-follows-root)**
- **D-09:** While a hob root is in force the row reads **"Hob tip radius used"**. A radial root keeps "Root fillet used". The value under the hob root is `rm.cutter.rho` (`calc.py:1091-1095`).
- **D-10:** The label is a function of the info document `d`, in the same shape as the `span` and `hex_cell_effective` rows (`app.js:17,39`). It keys on a value only the hob root produces: `root_form_d` is `None` exactly when `rm.curve is None` (`calc.py:1292`), so `d.root_form_d != null` is the candidate key. It follows the root the server built, not the one requested (a trochoid request can fall back to radial). Reading the form's `root_shape` was rejected: it puts a field name outside `DIMS` and shows the request, not the build.
  - ASSUMPTION: `rm.curve is not None` implies `rm.cutter is not None`, so `root_form_d` present means the hob branch at `calc.py:1091` ran. The researcher or planner confirms this in `root_mode` before relying on it.
  - Text only. No part, number or request moves. Its own commit.

**Triage scope (REQ-info-findings-triaged, REQ-old-info-findings-triaged)**
- **D-11:** Phase 26 IN-01..05 (five `| info | open |` rows in `26-REVIEW-DISPOSITION.md`, listed in neither REQUIREMENTS nor the roadmap) are triaged in this phase with the same vocabulary. Cheap fixes only where this phase already edits the file. The rest are `deferred` + path or `skipped` + a one-line reason. The close grep extends to Phase 26: `grep -n '| info | open |'` over the Phase 10, 18, 19, 21-24 **and 26** `*-REVIEW-DISPOSITION.md` files prints nothing.
- **D-12:** The Phase 18 leftovers (everything except IN-02 and IN-06, closed as overtaken, and IN-07, whose docstring is fixed) go into one `nice` debt item whose trigger is **the next phase that changes the trochoid / hob-root maths in `calc.py` or its tests**.
- **D-13:** 10 IN-02 (`tip_chamfer_effective`'s null-gate reads `p.tip_chamfer`, not the applied `tch`; it changes a printed value) is filed as a `docs/tech_debt/active/` item, **Severity: must**, whose next step is a human decision: fix under a new `Lxx` with its own `make fixture.regen` commit, or keep it with a reason. Not fixed in this phase.
- **D-14:** The roadmap's in-phase fixes stand: 24 IN-01 (the stash comment), 24 IN-02 / CX-03 (the "Could not build the form" wording), each its own commit in `app.js`. The behavioural half of 24 IN-01 (selector stash invalidation) is filed as an idea. The disposition cells are written from `27-TRIAGE.md`'s draft, so the close is a reading.

### Claude's Discretion
- Exact name and placement of the map and its helper, provided the pinned tokens hold.
- New browser step names (e.g. `root_shape=bogus is refused`).
- Commit order inside the phase, keeping one concern per commit (fix + pin + L44 + docs + debt retirement as one; label; 24 IN-01; 24 IN-02 / CX-03; triage records).

### Deferred Ideas (OUT OF SCOPE)
- Outlining the mate box on a `mate_teeth` 422 (needs `problems()` to know a non-`fields` input). Recorded in `L44` as a known gap, not filed. Raise it if a user reports it.
- Showing the rejected token inside the control (stray select option, number placeholder). Considered, rejected for D-01.
- Whether the API should accept `''` as "default". Recorded in `L44` (D-06), not filed.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-bad-link-refused | A link carrying a non-blank value its control cannot hold keeps the token in the fragment, sends it, is marked through the 422 path with the server's text; no part built; edit/Reset clears; generic; blank = default | Prototype (below) passes every pin and the golden sweep; 422 bodies for all four links measured; pin inventory quoted verbatim |
| REQ-bad-link-decision-logged | `L44` logged, `root_shape=bogus as today` rewritten red-first both ways, `web-ui.md` true, debt item retired | Old pin goes red at a named line against the prototype; harness helpers for the new step; doc lines and INDEX mechanics located |
| REQ-root-fillet-label-follows-root | `root_fillet` label stops reading "Root fillet used" under a hob root; text only; own commit | D-10 assumption confirmed in `calc.py`; label prototype measured on three links; pins unaffected |
| REQ-info-findings-triaged | Open info findings of 19, 21-24 dispositioned | Current open rows listed per file; 27-TRIAGE shas verified to exist; file-edit mechanics (front matter AND table) |
| REQ-old-info-findings-triaged | Phase 18 IN-01..08, Phase 10 IN-01/02 dispositioned | Per-finding liveness re-checked against the tree this session (18 IN-01 is already fixed) |
</phase_requirements>

## Summary

The fix is small and fits entirely around the pinned tokens: one `Map` declared in the form section of `app.js`, a read-back loop after the pinned `readHash` line, one extra read-back for the mate box before the pinned `readHash` tail, one early-`continue` branch in `gearQuery`, a one-line `mate` change in `update()`, two new `input` listeners (the form's and the mate box's), and one `rejected.clear()` line before the pinned Reset line. I applied exactly that to a copy of `app.js` and ran it through the real page: all four bad links send their token, keep it in the fragment, show the server's own text, make no STL request and leave `data-triangles` unchanged; editing the field and Reset clear the refusal; the 44-record golden sweep is unchanged; the four static pins in `tests/test_api.py` pass; and the existing browser test is green on every step except `root_shape=bogus as today`, which goes red at its first sub-assertion (`/api/info was sent 'teeth=22&root_shape=bogus'`). The repo was restored after each run (`git status` clean).

Two things in the CONTEXT need the planner's eye. First, the control-cannot-hold rule (D-02) also catches tokens the **API accepts**: `teeth=%2022`, `teeth=22%20`, `teeth=1_0`, `face_width=22.`, `face_width=5.` and `face_width=%2B5` are blanked by a number box but answer 200 from the API (MEASURED below). After the fix the page sends them and builds the part the server reads, with a blank control; before, it silently built the default. That is consistent with "the server decides" but `L44` should say it, and no test may use such a token as a "bad" example. Second, the review ledger is wider than the CONTEXT says: Phase 27's own `27-REVIEW-DISPOSITION.md` has two `| info | open |` rows (IN-11, IN-12), and several non-info rows in Phases 21 and 22 still read `open`/`deferred` for work Phase 27 finished. D-11 extended the close grep to Phase 26 for the same reason; Phase 27 needs the same human call (Open Question 1).

**Primary recommendation:** Implement the verified prototype shape (below) as commit 1 with the L44 entry, the flipped browser step, `web-ui.md:80` and the debt retirement; do the label as a one-line `DIMS` row change keyed on `d.root_form_d != null` in its own commit; do the triage as hand edits of both the YAML front matter and the table of each `*-REVIEW-DISPOSITION.md`, in a final docs commit that cites the earlier shas.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Detect that a link token cannot be held by its control | Browser / Client (`readHash`) | — | Only the browser can read a control back after assignment; the server never sees the sanitised value |
| Carry the raw token to the API | Browser / Client (`gearQuery`, `update`) | — | The side map exists because the control cannot hold the token |
| Decide the token is invalid and word the refusal | API / Backend (pydantic 422) | Browser (`problems()` renders it) | L02: no client-written wording; the form is generated from the schema |
| Mark the field | Browser (`problems()` keyed on `loc[1]`/`ctx.fields`) | — | Already field-agnostic; unchanged |
| `root_fillet` row label | Browser (`DIMS` label function) | API (`root_form_d` null/non-null is the discriminator) | Label follows the build the server did, read from the info document |
| Triage ledger | Planning files (`.planning/**/*-REVIEW-DISPOSITION.md`) | `docs/tech_debt/`, `docs/ideas/` | Records only; no runtime tier |

## Standard Stack

No package is added, removed or upgraded. Everything runs on what is installed.

| Tool | Version | Purpose | Source |
|------|---------|---------|--------|
| Python | 3.12.15 | all tests | [VERIFIED: `make test` header this session, "Python 3.12.15, pytest-9.1.1"] |
| pytest / pytest-xdist / pytest-cov | 9.1.1 / 3.8.0 / 7.1.0 | gate | [VERIFIED: same header] |
| Playwright (Python) + Chrome Headless Shell | pinned `==` in `[dev]`; shell `chromium_headless_shell-1243` | browser test | [VERIFIED: `ls .venv/ms-playwright`] |
| vanilla JS in `app.js` | no build step | the fix | [VERIFIED: Read `src/spur/static/app.js`] |

**Installation:** none. **Package Legitimacy Audit:** not applicable, this phase installs no external package.

## Architecture Patterns

### System Architecture Diagram

```
 #root_shape=bogus&teeth=abc&mate_teeth=abc        (shared link, or hashchange / back / forward)
        |
        v
 readHash()  -- rejected.clear()
        |-- pinned loop: input.value = h.get(name) ?? defaults[name]      (select -> '' / idx -1; number box -> '')
        |-- NEW read-back loop: token non-empty AND control reads ''  --> rejected.set(name, token)
        |-- NEW mate read-back (assign, read, then the pinned tail assigns again)
        '-- pinned tail: mateInput.value = ...; applyRelations(); deriveSelectors(); }
        |
        v
 update()
   q = gearQuery():   rejected.has(name) ? q.set(name, token)  [NEW]   : (pinned default-dropping branch)
   mate = control value, else rejected 'mate_teeth' token                [NEW]
   history.replaceState(... #q)         <-- fragment keeps the raw token
        |
        v
 fetch api/info?...bogus...  --422-->  problems(res)  (unchanged)
        |                               .invalid on label.field for loc[1] / ctx.fields ; text = "<Title>: <server msg>"
        |                               mate_teeth: loc[1] not in `fields` -> bare msg, no outline (D-05)
        v
 fail(errors) (unchanged): messages shown, #dims emptied, return BEFORE api/model.stl  --> no STL request, no new part
        ^
 clears:  input on THAT field | Reset | next readHash          (editing another field keeps sending the token)
```

### Recommended edit footprint (all in `src/spur/static/app.js`)

```
const defaults = {};
const rejected = new Map();   // top of file, NOT inside the relations or selectors sections
function refuse(...)          // directly above readHash(), form section
readHash()                    // rejected.clear(); pinned loop; read-back loop; mate read-back; pinned tail
gearQuery()                   // one early-continue branch before the pinned `if`
update()                      // `const mate = ...` gains the rejected fallback
wiring                        // two NEW addEventListener lines; Reset gains one line BEFORE the pinned one
DIMS                          // root_fillet row becomes a label function (separate commit)
```

### Pattern 1: Pre-pass / post-pass around pinned lines (the verified shape)

**What:** keep every pinned line byte-intact (after the tests' whitespace collapse) and add statements between them.
**When to use:** any change to `readHash`, `gearQuery`, `update` wiring or Reset.
**Example (this is the code I ran; it is a prototype, not a final patch):**
```js
// Source: prototype measured in this session (scratchpad/proto.py); names are Claude's discretion.
const rejected = new Map(); // name -> the raw token its control could not hold (L44)

// Called after the control was assigned the token. A non-empty token that reads back '' is one the
// control cannot hold: a select with no such option, or a number box that sanitised it.
function refuse(name, input, token) {
  if (token && input.value === '') rejected.set(name, token);
}

function readHash() {
  const h = new URLSearchParams(location.hash.slice(1));
  rejected.clear();
  for (const [name, { input }] of fields) input.value = h.get(name) ?? defaults[name];   // pinned, unchanged
  for (const [name, { input }] of fields) refuse(name, input, h.get(name));
  mateInput.value = h.get('mate_teeth') ?? '';          // assigned here only to read it back
  refuse('mate_teeth', mateInput, h.get('mate_teeth'));
  mateInput.value = h.get('mate_teeth') ?? ''; applyRelations(); deriveSelectors(); }  // pinned tail, unchanged
```
```js
function gearQuery() {
  const q = new URLSearchParams();
  for (const [name, { input }] of fields) {
    if (rejected.has(name)) { q.set(name, rejected.get(name)); continue; }
    if (input.value !== '' && String(input.value) !== String(defaults[name])) q.set(name, input.value); // pinned, unchanged
  }
  return q;
}
// update():   const mate = mateInput.value || rejected.get('mate_teeth') || '';
// wiring:     form.addEventListener('input', (e) => rejected.delete(e.target.name));
//             mateInput.addEventListener('input', () => rejected.delete('mate_teeth'));   // a NEW line; leave the scheduleUpdate line alone
// Reset:      rejected.clear();   // between the `for` line and the pinned `mateInput.value = ''; stash.clear(); ...` line
```
Notes the prototype taught: (a) the mate box cannot be read back after the pinned tail, because `applyRelations();` follows in the same pinned token, so the mate is assigned once early just to be read back; (b) the form's `input` listener must be a separate `addEventListener` call, since the existing one is pinned to the exact `() => { applyRelations(); deriveSelectors(); scheduleUpdate(); }` text; (c) selector `<select>`s have `name === ''`, so `rejected.delete(e.target.name)` is a harmless `delete('')` for them.

### Anti-Patterns to Avoid
- **A row-shaped table for the map** (`['root_shape', ...]` at a line start): harvested as a `DIMS` key and fails `tests/test_api.py:173-182`. Use a `Map`. Also keep any line that starts with `['word',` out of the file except inside `DIMS`. The mate pair must not be written as a line-leading `['mate_teeth', mateInput]`.
- **Putting new code in the relations or selectors sections.** Their guards forbid `.value =` there (`tests/test_api.py:376-402`). The `rejected` declaration, `refuse` and `readHash` all sit in the form section.
- **Sweeping selector selects into the map.** They use `selectedIndex` -1 for "no option holds"; only `fields` and the mate box are read back.
- **Client-written wording.** Never append "got 'bogus'" (changes `_expected_422`'s text equality and breaks L02).
- **"Any edit clears all"** (rejected, D-03).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Is the token valid? | An enum-membership or numeric regex in `app.js` | Send it; the API's 422 | L02, and the read-back rule already covers `bogus`, `Trochoid`, `abc` with one line |
| Marking the field and wording the error | New client marking or message code | `problems()` / `fail()` unchanged | Field-agnostic on `loc[1]` and `ctx.fields`; measured to mark `Root shape`, `Recess sides`, `Teeth` |
| Test oracle for the refusal | Literal expected strings | `_api_get` + `_expected_422` in `tests/test_browser.py:135-208` | They compare the page to the API's own body; `mate_teeth` yields an empty `marked` set and a bare text automatically |
| Waiting for requests | `time.sleep` | `page.expect_request`, `expect(...).to_have_text`, `wait_for_timeout` | Under the sync API, events are dispatched only while a Playwright call is in flight (my own `sleep`-based script printed empty request lists for requests that had been sent) |
| Disposition files | A script that rewrites them | Hand edits of front matter + table | Precedent `9001695`; there is no tool in the repo |

## Verbatim pin inventory (what the fix must not break)

All read this session. `collapsed_source` is `re.sub(r"\s+", " ", source)`; each snippet is collapsed the same way and must be a substring.

`tests/test_api.py:253-289` (`test_the_shareable_link_round_trips_every_field_through_generic_code`), snippets that touch this phase:
```
"for (const [name, { input }] of fields) input.value = h.get(name) ?? defaults[name];",
"mateInput.value = h.get('mate_teeth') ?? ''; applyRelations(); deriveSelectors(); }",
"q.set(name, input.value)",
"const infoQ = new URLSearchParams(q);",
"history.replaceState(null, '', hash ? `#${hash}` : location.pathname + location.search);",
"window.addEventListener('hashchange', () => { readHash(); update(); });",
"form.addEventListener('input', () => { applyRelations(); deriveSelectors(); scheduleUpdate(); });",  # noqa: E501
"mateInput.value = ''; stash.clear(); applyRelations(); deriveSelectors(); update();",
```
`tests/test_api.py:580-581` (in the `root_shape` schema test):
```
assert ("if (input.value !== '' && String(input.value) !== String(defaults[name])) "
        "q.set(name, input.value);") in source
```
Rules that bind new code:
- `tests/test_api.py:173-182`: `dims_keys = re.findall(r"^\s*\['(\w+)',", source, re.MULTILINE)`; must equal the same findall inside `const DIMS = \[.*?\];` and be a subset of `DerivedDimensions.model_fields`. A new row-shaped line anywhere else fails.
- `tests/test_api.py:295-311`: with the `DIMS` block cut out, no `GearParams` field name may appear as a complete quoted string (`['"]name['"]`) and none may appear as `\.name\b`. GearParams fields: `teeth, module, pressure_angle, profile_shift, backlash, root_fillet, tip_chamfer, root_shape, face_width, bore_d, bore_flat, keyway_width, keyway_depth, bore_hex, bore_clearance, bore_chamfer, recess_sides, recess_depth, recess_width, recess_inner_d, recess_fillet, spoke_count, spoke_width, hub_d, rim_wall, spoke_fillet, hole_count, hole_d, hole_circle_d, hex_cell, hex_wall` [VERIFIED: `GearParams.model_fields` run this session]. `module` is the risky word (`.module`).
- `tests/test_api.py:317`: `collapsed_source.count("fields.set(") == 1`. Do not call `fields.set(`.
- `tests/test_api.py:328-370`: `writes_a_field_shut` must not match the whole source (`.disabled =`, `.hidden =`, `.readOnly =`, `.inert =`, `.innerHTML`, `insertAdjacentHTML`, `.style.display|visibility|pointerEvents|opacity`, `classList.add|toggle('hidden'|'disabled'|...)`).
- `tests/test_api.py:376-402`: `writes_a_value = \.value\s*=(?!=)|...` must find nothing in the relations section and exactly **one** match in the selectors section (comments included). **The 24 IN-01 comment rewrite lives in the selectors section: it must not spell a value assignment.**
- `tests/test_browser_pins.py`: the scan set (`*browser*.py`, `capture_requests.py`, `process_group.py`) must not contain the attributes/names `importorskip, skip, skipif, xfail, pytestmark, getenv`, or an `environ` read outside the allowance. New steps must not use `.skip`.
- `make no-fake-done`: no `TODO|FIXME|XXX|HACK|NotImplementedError` word in `*.py`/`*.js`.

## The 422 bodies (MEASURED with `TestClient`, `/api/info`)

| Query | Status | `loc` | `msg` (verbatim) |
|---|---|---|---|
| `root_shape=bogus&teeth=22` | 422 | `["query","root_shape"]` | `Input should be 'radial' or 'trochoid'` |
| `recess_sides=bogus` | 422 | `["query","recess_sides"]` | `Input should be 'both', 'top', 'bottom' or 'none'` |
| `teeth=abc` | 422 | `["query","teeth"]` | `Input should be a valid integer, unable to parse string as an integer` |
| `mate_teeth=abc` | 422 | `["query","mate_teeth"]` | same integer text |
| `root_shape=Trochoid` | 422 | `literal_error` | same enum text |
| `root_shape=` / `teeth=` / `mate_teeth=` | 422 | `literal_error` / `int_parsing` | the API refuses blank (D-06's mismatch, MEASURED) |

What the page shows in the prototype run (real Chrome, `#messages .error` and `label.field.invalid .name`): `"Root shape: Input should be 'radial' or 'trochoid'"` marking `Root shape`; `"Recess sides: Input should be 'both', 'top', 'bottom' or 'none'"` marking `Recess sides`; `"Teeth: Input should be a valid integer, unable to parse string as an integer"` marking `Teeth`; for `mate_teeth=abc` the bare text with **no** field marked. `_expected_422` already produces exactly these (title prefix only when `loc[1]` is a schema property).

## Prototype evidence (all MEASURED this session, repo restored after each run)

| Check | Result |
|---|---|
| Four bad links via `hashchange` on a page that already drew a part | request `api/info?...<token>...` only; no `api/model.stl`; hash keeps the token (`#teeth=22&root_shape=bogus`, `#recess_sides=bogus`, `#teeth=abc`, `#mate_teeth=abc`); `data-triangles` stays `9066`; status `Showing the last valid gear`; `#dl-stl` has no `href` |
| `root_shape` select after the link | `selectedIndex` -1; `teeth=abc` box reads `''` |
| Edit a different field (`module`) | hash becomes `#teeth=abc&module=3`: the bad token is kept and the error stays |
| Edit the rejected field (`teeth` to 21) | hash `#teeth=21&module=3`, no error, no `.invalid` |
| Reset from `root_shape=bogus&teeth=22` | hash `''`, no error, no `.invalid` |
| Edit the mate box after `mate_teeth=abc` | hash `#mate_teeth=30`, no error |
| 44-record golden sweep with patched `app.js` | `moved == {}` against `tests/regression/golden_requests.json` |
| `tests/test_api.py -k "shareable_link or every_key_the_ui or root_form_d_is_never or root_shape"` | `4 passed` |
| Full `tests/test_browser.py` with the prototype in place | 22.9 s; every step green through `download name`; `root_shape=bogus as today` red |
| Old pin's first failure line | `AssertionError: today's behaviour, filed as debt: docs/tech_debt/active/2026-10-10-root-shape-bogus-loads-a-blank-select.md: /api/info was sent 'teeth=22&root_shape=bogus'` / `assert 'teeth=22&root_shape=bogus' == 'teeth=22'` / `step: root_shape=bogus as today` (log kept in scratchpad `browser_red.log`; the executor must re-record against the real patch) |
| Baseline browser test (clean tree) | `3 passed in 23.46 s`, `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"` |
| `git diff --exit-code v0.5 -- tests/regression/` | empty today |

### Tokens a number box blanks, and what the API says (MEASURED: Chrome Headless Shell + `TestClient`)

| Token | Control reads | `teeth` | `face_width` |
|---|---|---|---|
| `abc`, ` `, `0x10`, `NaN`, `Infinity`, `1e`, `--5`, `22,5`, Arabic-Indic digits, `1e400` | `''` (rejected by D-02) | 422 | 422 |
| ` 22` / `22 ` (space) | `''` | **200** | **200** |
| `1_0` | `''` | **200** | **200** |
| `22.`, `5.` | `''` | 422 | **200** |
| `+5` (`%2B5`) | `''` | 422 (range) | **200** |
| `.5`, `1e1`, `1E1`, `-5`, `22.5` | held by the control (not rejected, reach the API as today) | 422 | mixed |

Select: `bogus`, `Trochoid`, `trochoid ` (trailing space), `''`, ` ` all read `['', -1]`; `radial` reads `['radial', 0]`.

Consequence for `L44` and the plan: for the 200 rows the page now sends the token and builds the server's reading while the box shows blank. That is honest to the link and is not a defect, but `L44` should state "the server decides what a token the control cannot hold means", and the browser step's "bad" examples must be tokens the API refuses (`bogus`, `abc`). Cross-browser: the sanitisation on assignment is the HTML value-sanitization algorithm [ASSUMED: the project's browser test runs Chrome Headless Shell only, so only Chromium behaviour is measured].

## Existing browser harness (what the new step builds on)

- Run: `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"` (23 s). It is one function, `test_the_shipped_viewer_in_a_real_browser`, walking `with step("name", no_foreign_key):` blocks against one server; `step()` adds a `step: <name>` note on failure (`tests/browser_session.py:757-773`).
- `no_foreign_key` (test_browser.py:671-684) runs after every step: request keys must be GearParams fields, `quality` or `mate_teeth`; hash keys must be fields or `mate_teeth`. A kept `root_shape=bogus` key is a field, so it passes.
- The main `page` is wired with `serve_stl_from(page, stl)` (every STL request is fulfilled with the first build's bytes; it builds nothing). For a "no STL request" assertion use the recorder list `seen` (appended by `record_api`, all `/api/` URLs of that page) and count `/api/model.stl` entries before and after, after the 422 text is on screen plus `page.wait_for_timeout(DEBOUNCE_SETTLE_MS)` (1000 ms, test_browser.py:73). `fail()` returns before the STL fetch, so by the time `#messages .error` shows the text, no STL request can follow from that `update()`.
- "Draws no default part": on the main page assert `canvas.get_attribute("data-triangles")` equals the earlier `declared`, as `invalid field marked` does (test_browser.py:813-816). For the strongest form, open a **fresh page with the fragment on the `goto` URL** (a fragment assigned after load can be erased before `buildForm()` returns, see the `download name` step comment, test_browser.py:1776-1783) and assert `data-triangles` is `None`, the STL list stays empty and `#dl-stl` has no `href`.
- `_follow_link(page, fragment)` (test_browser.py:211-224) returns the page's `/api/info` query and asserts the fragment differs from the current one (no `hashchange` otherwise).
- The oracle for the text: `status, body = _api_get(server, "/api/info", sent)`; `marked, texts = _expected_422(properties, body)`; `expect(page.locator("#messages .error")).to_have_text(texts)`; `set(page.locator("label.field.invalid .name").all_text_contents()) == marked`. For `mate_teeth=abc`, `marked == set()` and the invalid count is 0 (the approved D-05 gap).
- Old step to replace: test_browser.py:1802-1857 (`root_shape=bogus as today`), constants `BOGUS_LINK = "root_shape=bogus&teeth=22"` and `TODAY` at lines 104-109 (they name the debt file path, which moves; drop `TODAY`). Old step names stay in `bench/RESULTS.md` rows (lines 4829, 5075, 5297, 5369, 5477) as history.
- Recovery interactions: `page.fill('[name=teeth]', '21')` fires `input` and the debounce (350 ms) sends one request; `select.select_option(...)` for an enum; `page.click('#reset')`. Wrap each action in `page.expect_request(lambda r: "/api/info" in r.url, timeout=BUILD_WAIT_MS)`.
- Suggested step set (names are discretion): `root_shape=bogus is refused` covering the four links, `recess_sides` and enum recovery, `teeth` edit recovery, a different-field edit keeping the token, Reset, the mate box (message without outline, recovery by typing), a fresh-page load of one bad link (no STL, no triangles), and "a valid link leaves nothing marked" (reuse the end of `invalid field marked`: `teeth=23` then `label.field.invalid` count 0).

## Common Pitfalls

### Pitfall 1: Reading the control back after the pinned tail
**What goes wrong:** the mate box is assigned only in the pinned tail, which also contains `applyRelations(); deriveSelectors(); }`; a read-back placed after it is outside `readHash`.
**How to avoid:** assign the mate once in the pre-pass (as the prototype does), read it back, let the pinned tail assign it again.
**Warning signs:** `mate_teeth=abc` builds the default again, or the pinned-tail snippet goes red.

### Pitfall 2: Red for the wrong reason (PITFALLS 10)
**What goes wrong:** the "old pin red" is recorded from an earlier step, or the new pin is never seen red.
**How to avoid:** order (1) apply the fix, run the browser test, copy the first failure line of **`root_shape=bogus as today`** (prototype: `/api/info was sent 'teeth=22&root_shape=bogus'`); (2) rewrite the step; (3) revert only the `app.js` fix with `git checkout`/`git stash` of that one file and record the new step's first failure line. Keep logs under `.planning/phases/28-refuse-the-bad-link/investigation/` (the phase-27 precedent) and add a `### Seen red once (Phase 28)` table under a new `## Refuse the bad link (Phase 28)` section of `bench/RESULTS.md`, in the existing table shape (Plan | Test or step | Deliberate break | First failure line | Reverted).

### Pitfall 3: Stale rejection after a programmatic write
**What goes wrong:** `write()` in the selectors section (a bore-shape pick) sets a field's `.value` without an `input` event on that field. A link such as `bore_hex=abc` followed by a pick that writes `bore_hex` leaves the control at `'0'` while `gearQuery` still sends `abc`.
**How to avoid (optional hardening, planner's call):** make the map entry bite only while the control is still blank (`rejected.has(name) && input.value === ''`); the own-field listener is still required for a user who empties the box. Not exercised by the four contract links; add a small browser case only if the hardening is adopted.

### Pitfall 4: A relation gate that is itself rejected
`effective()` reads `input.value === '' ? defaults[name] : input.value`, so a rejected gate (e.g. `bore_hex=abc`) dims other fields as if it were the default. The 422 stops the build anyway; no change needed, but do not write a test that asserts dimming under a rejected gate.

### Pitfall 5: Comment edits in the selectors section
24 IN-01's comment is `app.js:294-299`, inside `-- selectors (L42)`. `tests/test_api.py:401-402` counts `.value =` matches in that section **including comments** and requires exactly one. Describe the stash without writing an assignment.

### Pitfall 6: `app.js:NNN` citations drift
Tests, bench and docs cite line numbers (`app.js:262-272`, `:643-644`, `:229`, `:289`, `:340`; test_browser.py:6, 72, 690, 1603, 1614; browser_session.py:678; decision_log.md:2372; RESULTS.md:4814, 6069, 6072). Several are already stale. No test pins them. Phase 26 IN-03 is exactly this: fix the two in `test_browser.py` (1603, 1614) by citing `update()` / the bootstrap by name, in the same commit as that file's step rewrite.

### Pitfall 7: Wiring an existing listener line
`mateInput.addEventListener('input', scheduleUpdate);` is not pinned, but rewriting it buys nothing; add a second listener line instead (prototype changed it and passed, either works).

### Pitfall 8: `Resolved in:` cannot name its own sha
A commit cannot contain its own sha. Precedent: retire with the commit subject in the file, then a tiny follow-up commit writes the short sha (`0fd2b98`, `b9755ad`, `991ba24`, `5a3332f`). Do the same for the root-shape and Phase 19 debt items.

### Pitfall 9: Very long tokens
A multi-KiB token in the fragment is now sent in the query; the server's header limit then answers a non-JSON error and `problems()` falls into its `catch` ("<status> <text>"). Previously such a token was silently dropped. Acceptable; do not add a length check (no client validation, L02). [ASSUMED: server limit behaviour not measured.]

## The `root_fillet` label (D-09, D-10)

- D-10's assumption is **confirmed**. `root_mode` returns `RootMode("trochoid", None, c, curve)` only after `c = cutter(p, rho)`, so `curve is not None` implies `cutter is not None` [VERIFIED: `src/spur/calc.py:1700-1708`: `c = cutter(p, rho)` … `return RootMode("trochoid", None, c, curve)`]. `derive()` reads the hob branch at `if rm.curve is not None and rm.cutter is not None:` then `rfil = rm.cutter.rho` [VERIFIED: `calc.py:1091-1095`] and `root_form_d=None if rm.curve is None else r3(2 * rm.curve.points[-1][0])` [VERIFIED: `calc.py:1292`]. So `d.root_form_d != null` is exactly the hob-branch predicate. Use loose `!= null` (0 would be a legal non-null number).
- Row after the change (the same shape as the `span` row):
```js
['root_fillet', (d) => (d.root_form_d != null ? 'Hob tip radius used' : 'Root fillet used')],
```
- Measured in the real page (label patched via route): default link `Root fillet used 0.5 mm`; `teeth=23&root_shape=trochoid` -> `Hob tip radius used 0.5 mm`; `teeth=42&root_shape=trochoid` (request falls back to radial, `rb <= rf`) -> `Root fillet used 0.484 mm`; `teeth=23` -> `Root fillet used 0.5 mm`. The four static pins still pass with the row changed.
- No test pins the string today (`grep` finds it only in `app.js:23`, a debt file and archived plans). New proof, in the label commit: a browser assertion over a hob link, a radial link and a fallback link where the expected label is derived from the API body (`'Hob tip radius used' if body['root_form_d'] is not None else 'Root fillet used'`) and the golden sweep unchanged; seen red against the old label first. Note `fail()`/an aborted STL empties `#dims`; assert on a page whose STL is fulfilled (the main page's `serve_stl_from`) or let the build run, as my probe did.
- Same commit: retire `docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md` (its own "Next step" says so), move its INDEX row (line 32), and flip the Phase 19 disposition rows (below).

## Triage inventory (state at HEAD `d0bd536`)

Every file has **two** representations: YAML front matter (`findings[].disposition`, `open: N`, `total: N`) and the table. Edit both (precedent `9001695`: `open: 0` after triage, table Source cell carries the sha or reason). The close grep reads only the table. Disposition vocabulary: `fixed`, `deferred`, `skipped`, `open`.

| File | Open info rows now | Proposed (from 27-TRIAGE, re-verified) |
|---|---|---|
| 10 (`milestones/v0.2-phases/10-tooth-tip-chamfer/`) | IN-01, IN-02 | IN-02: `deferred` + the new `must` decision item (D-13; live, `calc.py` still has `tip_chamfer_effective=r3(tch) if p.tip_chamfer > 0 else None`). IN-01: live (`bench/tip_chamfer_spike.py:201,286` hard-code `3.0`); fold into the Phase 18 `nice` item as its own line with a trigger (next edit of `bench/tip_chamfer_spike.py` or the `tip_chamfer` bound), or `skipped` with a reason. Either is within D-12/D-13; planner/human pick |
| 18 (`milestones/v0.4-phases/18-trochoid-maths-proved/`) | IN-01..IN-08 | IN-01 **already fixed**: `_ROOT_SENTENCES["rho capped"]` now reads "within 0.001 mm of the largest" [VERIFIED: calc.py, text quoted; introduced by `767317b` Phase 19]; mark `fixed` + `767317b`. IN-02 `skipped` (overtaken: `RootMode.curve` exists, calc.py:1668). IN-06 `skipped` (overtaken: the flake item is resolved, `docs/tech_debt/resolved/2026-10-06-resource-tracker-flake-fails-the-gate.md`). IN-07 `fixed` by a one-line `root_mode` docstring addition (below). IN-03, IN-04, IN-05, IN-08 are live [VERIFIED this session: bench/trochoid.py:216-224 never compares `eps` with the shipped constant; `sys.path.insert` at :575; ROOT_CURVE_POINTS comment unchanged at calc.py:66-72; `-0.0` row in tests/test_trochoid.py:395]: `deferred` + the single `nice` item (D-12) |
| 19 (`milestones/v0.4-phases/19-the-trochoid-in-the-part/`) | none (rows read `skipped`, source `19-REVIEW-FIX.md`, no reason) | Replace with 27-TRIAGE's rows: IN-01 `fixed` `f7d0366`; IN-02 `fixed` `9c62fac` (bench half) and `skipped` for the near-copies (reason in 27-TRIAGE); IN-03 `fixed` `34270c8`; IN-04 `fixed` `9c62fac` (`_host_state`) plus the label commit's sha. A row holds one disposition: use `fixed` with both shas in the Source cell |
| 21 (`milestones/v0.5-phases/21-browser-test-of-the-viewer/`) | IN-01..IN-04 (and WR-01..03 `open`) | IN-01 `fixed` `a7c5f78`; IN-02 `fixed` `4d43b64`; IN-03 `fixed` `0ed2057`; IN-04 `fixed` `1981d93` (PR #41; branch commit `6ff1269`) for 04a, with 04b named in the Source cell as the existing `docs/tech_debt/active/2026-10-15-wait-until-parked-spins-without-a-pause.md` (the roadmap lists 21 IN-04 as a vacuous-pass finding that must be `fixed`; 04a is the vacuity). WR-01 `a7c5f78`, WR-02 `99e2b7d`, WR-03 `a393e50` -> `fixed` (outside the grep, but they are false as written) |
| 22 (`.../22-download-name-carries-the-root/`) | IN-01..IN-03 (WR-01/02 `deferred`) | IN-01 `c30ebd0`, IN-02 `4d43b64`, IN-03 `d7f069d`, all `fixed`. WR-01 (`345ee08`) and WR-02 (`c47bfc4`) -> `fixed`; their debt files are now in `resolved/` |
| 23 (`.../23-conditional-form-fields/`) | IN-08, IN-11 | IN-08 `fixed` `c30ebd0`; IN-11 `fixed` `4d43b64` |
| 24 (`.../24-bore-shape-selector/`) | IN-01, IN-02, IN-03, IN-04, CX-03, CX-05 | IN-01 `fixed` (this phase's comment commit; the behavioural half filed as an idea); IN-02 and CX-03 `fixed` (this phase's wording commit); IN-03 `fixed` `c30ebd0`; IN-04 `deferred` + `docs/ideas/2026-10-14-hex-warning-names-fields-by-form-title.md`; CX-05 `fixed` `1981d93` / `6ff1269` |
| 26 (`.planning/phases/26-gate-fails-with-a-cause/`) | IN-01..IN-05 | IN-03 `fixed` in this phase's `test_browser.py` commit (cite `update()` by name at test_browser.py:1603 and 1614). IN-01 (second hook-pin test adds no discrimination, `tests/test_hooks.py:164`) and IN-02 (test name, `:229`): file not edited by Phase 28 -> `skipped` with a one-line reason (IN-01: kept as documentation, the review's own first option) or `deferred` to a `nice` item. IN-04 (planning paths in comments dangle once v0.6 is archived; `Makefile:226`, hang item lines 8 and 61): decision for the planner, see Open Question 3. IN-05 (unmeasured fixture cost, `tests/test_pool.py:56`): `skipped`/`deferred` |
| 27 (`.planning/phases/27-ledger-tests-and-harness/`) | **IN-11, IN-12** | Not in CONTEXT or the roadmap: Open Question 1 |

**Facts the cells depend on.** Every sha in 27-TRIAGE resolves in the local object store (`git log -1` run on 16 of them). Only `1981d93` and `cbbe730` are ancestors of `HEAD`; the rest are branch commits squashed into `1434a47`, which is the house convention (`2026-10-05-resolved-in-shas-point-at-squashed-branch-commits.md`). `94bccc4`, cited in 24's existing cells, does not exist locally (leave it).

**The 18 IN-07 docstring.** `root_mode` (`calc.py:1672`) calls `cutter(p, rho)` before any refusal when trochoid is requested (`c = cutter(p, rho)`, calc.py:1702), and `cutter` raises `ValueError(f"tip radius must be a finite, non-negative millimetre value, got {rho!r}")` (calc.py:1415-1416). Add one line to the `root_mode` docstring: a `rho` that is not a finite, non-negative millimetre value raises `ValueError` from `cutter` before any reason is decided; with nothing requested it is not read. Docstring only: no number moves; no test pins the docstring.

**Files to create (nice/must/idea), from `docs/*/TEMPLATE.md`, plus an INDEX row each in the same commit:**
- `docs/tech_debt/active/2026-10-21-phase-18-review-info-findings-deferred.md`, `Severity: nice`, trigger "the next phase that changes the trochoid / hob-root maths in `calc.py` or its tests" (IN-03, IN-04, IN-05, IN-08 and, if folded, 10 IN-01).
- `docs/tech_debt/active/2026-10-21-tip-chamfer-effective-gate-reads-the-request.md`, `Severity: must`, next step is the human's decision (D-13): fix under a new `Lxx` with its own `make fixture.regen` commit, or keep with a reason (10 IN-02 changes a printed value, L08).
- `docs/ideas/2026-10-21-...-stash-entry-dies-with-a-hand-edit.md` for the behavioural half of 24 IN-01 (24-REVIEW's fix: delete the stash entry when its box is edited by hand).
- INDEX rows for the two debt items; `docs/tech_debt/INDEX.md` Active table (rows 19, 32, 33 are the ones this phase touches or answers: row 19 root-shape moves to Resolved, row 32 Phase 19 item moves to Resolved; row 33 `_wait_until_parked` stays active, its trigger "Phase 28's info-finding triage" should be restated since the triage happens here).

## `L44` and docs mechanics

- `docs/architecture/decision_log.md` is append-only; the last entry is L43 at line 2862 (`## L43 — ...`, `Date: 2026-10-14.`). Append `## L44 — A link token its control cannot hold is sent and refused by the API, never rebuilt as the default (amends L39's pin, supersedes L42's byte-identical observation; keeps L02, L03, L05, L08)` with a `Date:` line, the content list of D-07, a `Reversibility.` and a `Reason:` paragraph as L40-L43 do. Cite measured figures to `bench/RESULTS.md` sections, never re-estimated (the entries' own rule). State the token-the-API-accepts consequence (table above) and the unchanged blank rule with the API mismatch.
- L39's relevant text sits at decision_log.md:2393-2394 and :2448; L42's byte-identical sentence at :2795-2802 and :2683. None is edited.
- `docs/architecture/web-ui.md:79-81` ends "`GearParams` lacks (L42). `#root_shape=bogus` is pinned as today's behaviour and filed as debt." Replace with the new contract (the four links are refused through the 422 path, L44). Optionally add one sentence under `## Errors` (line 47) and mention the `rejected` map under `## Shape` (line 32-36). The README does not describe this behaviour.
- `bench/RESULTS.md`: add `## Refuse the bad link (Phase 28)` with the step timings and `### Seen red once (Phase 28)` (existing sections end at Phase 27, line 6508/6591).
- Keep `.planning/` per-phase evidence logs in `.planning/phases/28-refuse-the-bad-link/investigation/`.

## Code Examples

### Disposition edit (both places, from the Phase 16/14 precedent)
```
findings:
  - id: IN-02
    severity: info
    disposition: fixed          # was: open
...
open: 0                          # recount
...
| IN-02 | info | fixed | 4d43b64 (branch commit; squashed into 1434a47) |   # was: | IN-02 | info | open | - |
```

### A browser assertion for the refusal (shape only; helpers exist)
```python
# Source: composed from tests/test_browser.py:177-224 and 791-826
sent = _follow_link(page, "teeth=abc")
status, body = _api_get(server, "/api/info", sent)
assert status == 422
marked, texts = _expected_422(properties, body)
expect(page.locator("#messages .error")).to_have_text(texts)
assert set(page.locator("label.field.invalid .name").all_text_contents()) == marked
assert eval_str(page, FRAGMENT) == "teeth=abc"
```

## State of the Art

| Old approach | Current approach | When changed | Impact |
|---|---|---|---|
| Link value the control cannot hold is dropped silently, default part built, fragment rewritten | Token kept in a side map, sent, refused by the API | Phase 28 / L44 | A parameter the user set never silently changes the part (L03, L05) |
| `root_fillet` row always "Root fillet used" | Label follows the built root | Phase 28 | Text only |

**Deprecated/outdated:** the `root_shape=bogus as today` step and its `BOGUS_LINK`/`TODAY` constants; `web-ui.md:80`'s "pinned as today's behaviour"; L42's "byte-identical" observation (superseded by L44).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Assigning an unparseable value to `input[type=number]` blanks it in Firefox and Safari as in Chromium | Prototype evidence | Only Chrome Headless Shell is tested by the gate; real users on another engine could see different tokens rejected. Low for the gate, medium for L44's wording |
| A2 | An over-long fragment token yields a non-JSON server error that `problems()` catches | Pitfall 9 | Cosmetic message only |
| A3 | Proposed dispositions for Phase 26 IN-01, IN-02, IN-04, IN-05 and Phase 10 IN-01 (skip vs defer) | Triage inventory | Human preference; the grep passes either way |
| A4 | Phase 27's two open info rows are meant to be in the close | Summary / Open Question 1 | If out of scope, the milestone closes with two `open` rows in an adjacent phase's file |

## Open Questions

1. **Phase 27's own `27-REVIEW-DISPOSITION.md` has `| info | open |` for IN-11 and IN-12** (the `per statement` comment in `tests/test_browser_pins.py:126-128` and its missing pin). CONTEXT D-11 extended the close grep to Phase 26 for the same reason but predates this file's last stamp (`recorded: 2026-10-21T07:04:04Z`).
   - What we know: IN-11 is a comment-only fix (review gives the replacement text); IN-12 asks for a pin of the documented over-allowance. Phase 28 does not otherwise edit `tests/test_browser_pins.py`.
   - Recommendation: ask the human to extend the close to Phase 27; then IN-11 `fixed` (comment only, own commit) and IN-12 `skipped`/`deferred` with a reason, and the close grep covers 10, 18, 19, 21-24, 26 and 27.
2. **How to record 21 IN-04 when the roadmap says "fixed" but 04b is a deferred debt item.** Recommendation: `fixed` for the row (04a is the vacuous-pass half, fixed by `1981d93`), 04b named in the Source cell with its existing debt path. Confirm with the human; the alternative is a one-line `wait_for_timeout` fix of `_wait_until_parked` in a file this phase edits, which would let the row be `fixed` outright and the debt item retire (cost: the helper's comment says the round trip, not a sleep, lets the route handler run; `wait_for_timeout` is itself a Playwright call so it also pumps events).
3. **26 IN-04 (planning paths in comments will dangle at the v0.6 archive).** D-11 says cheap fixes only in files the phase already edits; `Makefile:226` and the hang item are not. The archive is imminent, so the cheap comment edit is worth doing now. Recommendation: do it as a separate comment-only commit citing `bench/RESULTS.md` sections, or `deferred` with that reason. The planner decides; either satisfies the grep.
4. **Phase 10 IN-01 placement** (fold into the Phase 18 `nice` item vs `skipped`). Recommendation: fold, with its own trigger line.
5. **Optional hardening** of Pitfall 3 (`input.value === ''` guard). Recommendation: adopt only if a test is added with it; the contract does not need it.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `.venv` (python3.12) | everything | yes | 3.12.15 | — |
| Chrome Headless Shell | browser test | yes | `chromium_headless_shell-1243` in `.venv/ms-playwright` | `rm -f .venv/.browser && make test` reinstalls |
| `make` | gate | yes | system | — |
| git tag `v0.5` | success criterion 2 | yes | `git tag` lists v0.3, v0.4, v0.5 | — |
| Docker / Node | `make check` only | not probed | — | not needed for this phase's close (`make verify` needs neither) |

**Missing dependencies with no fallback:** none.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (+ xdist 3.8.0, cov 7.1.0), Playwright sync API for the browser file |
| Config file | `pyproject.toml` |
| Quick run command | `.venv/bin/python -m pytest --no-cov -n0 -q -p no:cacheprovider tests/test_api.py -k "shareable_link or every_key_the_ui or root_form_d_is_never or root_shape"` (4 passed, about 2 s) |
| Browser run command | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"` (3 passed, 23 s clean tree) |
| Full suite command | `make verify` (ruff, mypy `--strict`, import contracts, unfinished-work scan, pytest; bar 300 s on this host, L43) |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-bad-link-refused | four links: token sent, fragment keeps it, server text, mark (mate: none), no STL, no new triangles; edit/Reset clear; different-field edit keeps | browser | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"` | step rewrite, Wave 1 |
| REQ-bad-link-refused | generic over the schema; pinned tokens hold; new tokens pinned | static | `pytest tests/test_api.py -k shareable_link` | extend the tuple at test_api.py:253-288 |
| REQ-bad-link-refused | valid links unchanged | browser + diff | golden sweep step; `git diff --exit-code v0.5 -- tests/regression/` | exists |
| REQ-bad-link-decision-logged | old pin red vs fix; new pin red with fix reverted | manual-with-record | commands in Pitfall 2; logs in `investigation/`; rows in `bench/RESULTS.md` | Wave 1 |
| REQ-bad-link-decision-logged | L44 present, debt item moved, web-ui.md true | grep | `grep -n '^## L44' docs/architecture/decision_log.md`; `test -f docs/tech_debt/resolved/2026-10-10-root-shape-bogus-loads-a-blank-select.md`; `grep -n "pinned as today" docs/architecture/web-ui.md` prints nothing | n/a |
| REQ-root-fillet-label-follows-root | hob link -> "Hob tip radius used"; radial and fallback -> "Root fillet used"; label equals function of API `root_form_d` | browser | same browser command | new assertions in a step, Wave 1 (red first against the old label) |
| REQ-info-findings-triaged | zero `| info | open |` | grep | `grep -rn '| info | open |' <the REVIEW-DISPOSITION files of 10, 18, 19, 21-24, 26 (and 27 if extended)>` prints nothing | n/a |
| REQ-old-info-findings-triaged | 18/10 rows dispositioned; nice + must items filed with INDEX rows | grep/read | same grep; `ls docs/tech_debt/active` | n/a |
| 24 IN-02 / CX-03 | wording | browser (cheap) | route `**/api/schema` with a selector naming a group no field has; expect `#messages .error` to start `Could not build the form:`; seen red against the old wording | new, small, optional but recommended (no test pins the string today) |

### Sampling Rate
- **Per task commit:** the quick `test_api.py` command above plus the browser command whenever `app.js` or `test_browser.py` moved.
- **Per wave merge:** `make verify`.
- **Phase gate:** `make verify` result line recorded, and `git diff --exit-code v0.5 -- tests/regression/` empty, and the triage grep empty.

### Wave 0 Gaps
- None for infrastructure: framework, shell and harness all exist and ran green this session. The new steps and pin tokens are the phase's own deliverables.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication / V3 Session | no | none exists in this project (no authentication, documented debt) |
| V4 Access Control | no | — |
| V5 Input Validation | yes | The server stays the validator (pydantic, unchanged). The client adds no validation, only stops discarding input before the server sees it |
| V6 Cryptography | no | — |
| V14 Config / output encoding | yes | The raw token is never written into the DOM: messages go through `textContent` (`showMessages`), the token reaches the URL only through `URLSearchParams`, which percent-encodes it |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| DOM XSS via a crafted fragment | Tampering | Token is only placed in a query string and `history.replaceState` via `URLSearchParams.toString()`; no `innerHTML`; `tests/test_api.py:328-370` forbids `.innerHTML`/`insertAdjacentHTML` anywhere in `app.js` |
| Reflected content in the 422 body | Information disclosure | Server messages shown are `msg` only; the body's `input` echo is not rendered |
| Header-size abuse with a huge token | DoS | Server limits apply; no client change (Pitfall 9) |

## Project Constraints (from CLAUDE.md)

- `make verify` is the gate; state the command and the result line in the final reply. `make check` adds Docker checks (not needed here).
- A number the tool prints is a number someone will cut metal to (L08); a parameter the user did not set never silently changes the part (L05); trim vs conflict is L03 (422). This phase is the L03/L05 fix for links.
- Stop and ask on: an architectural claim not in the decision log, a locked decision that looks wrong, unverified library behaviour, conflicting evidence, destructive operations. New non-trivial choice: 2-3 options, recommendation, log as `Lxx`.
- One concern per commit; semantic checkpoints; Conventional Commits in normal prose (commit text is not caveman). New behaviour ships with tests in the same change. Claims about performance are measured and recorded.
- Comments carry the measurement or constraint; vendor types stop at their boundary; a parameter is validated once at `GearParams`; English throughout; no `TODO`/`pass`/unreachable branches (the gate scans for the markers).
- Debt/idea capture: one file per item, `YYYY-MM-DD-slug.md` from `docs/<dir>/TEMPLATE.md`, INDEX row in the same commit; on fixing debt flip `Status: resolved`, add the sha, `git mv` to `resolved/`, move the INDEX row; state in the final reply whether any item was filed and its path.
- Use `make` targets, not ad-hoc shell. Cross-CLI review: the writer does not review the diff.
- User-facing replies caveman-terse; code ponytail-simple.

## Sources

### Primary (HIGH confidence)
- Read this session: `src/spur/static/app.js` (whole file), `tests/test_api.py` 120-470 and 560-650, `tests/test_browser.py` 1-330, 545-880, 940-1020, 1596-1620, 1765-1873, `tests/browser_session.py` 1-262, 600-773, `tests/test_browser_pins.py` 1-140, `Makefile`, `src/spur/static/index.html`, `src/spur/calc.py` 1075-1105, 1280-1300, 1405-1416, 1660-1795, `docs/architecture/web-ui.md`, `docs/architecture/decision_log.md` (L39, L42, L43 excerpts), debt files and INDEXes, all `*REVIEW-DISPOSITION.md` files, `27-TRIAGE.md`, `26-REVIEW.md`, `18-REVIEW.md`, `10-REVIEW.md`, `24-REVIEW.md`, research `FEATURES.md` Part A/B, `ARCHITECTURE.md` 3.7, `PITFALLS.md` 9-10.
- Executed this session: `TestClient` 422 bodies; Chrome Headless Shell token read-back; patched-`app.js` page runs; patched-`app.js` against `test_api.py` pins and the full `tests/test_browser.py` (restored with `git checkout`, `git status` clean); golden sweep; `git diff --exit-code v0.5 -- tests/regression/`.

### Secondary (MEDIUM confidence)
- HTML Standard number-input value sanitization: not retrievable in the page excerpt fetched (the fetched page was truncated before the section), so the cross-engine claim is `[ASSUMED]` (A1).

### Tertiary (LOW confidence)
- none

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - nothing changes.
- Architecture / fix shape: HIGH - prototyped and run against every pin and the browser test.
- Pitfalls: HIGH for pins and harness (read and run); MEDIUM for Pitfall 3 and 9 (reasoned, not exercised).
- Triage proposals: MEDIUM - liveness and shas verified; skip-vs-defer choices are the human's.

**Research date:** 2026-10-21
**Valid until:** 2026-11-04 (the pins and line numbers move with any `app.js` or `test_browser.py` edit; re-read them if Phase 28 slips)
