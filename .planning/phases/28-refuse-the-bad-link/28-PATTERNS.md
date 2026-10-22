# Phase 28: Refuse the Bad Link - Pattern Map

**Mapped:** 2026-10-21
**Files analyzed:** 22 (new/modified, grouped below)
**Analogs found:** 22 / 22 (all tracked in git; `git ls-files` checked for the app/test/docs files and all nine `*-REVIEW-DISPOSITION.md` files)

Tracked-source note: no analog is a gitignored mirror. Disposition files for phases 10-24 live under `.planning/milestones/v0.N-phases/...` (tracked); 26 and 27 under `.planning/phases/...`.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/spur/static/app.js` (rejected map, `readHash`, `gearQuery`, `update`, listeners, Reset) | client form/URL-fragment state | request-response + event-driven | same file: `stash` Map (L300) + `readHash`/`gearQuery` (105-120) | exact (in-file) |
| `src/spur/static/app.js` (`root_fillet` DIMS row) | client label | transform | same file: `span` / `hex_cell_effective` rows (lines 17, 39) | exact |
| `src/spur/static/app.js` (24 IN-01 stash comment, 24 IN-02 wording) | comment/text | n/a | `stash` comment block (292-299) | exact |
| `tests/test_browser.py` (replace `root_shape=bogus as today`, drop `BOGUS_LINK`/`TODAY`, fix 1603/1614 cites) | test | request-response (Playwright) | the step it replaces (~1802-1857) + `invalid field marked` (~791-826), helpers `_follow_link`, `_api_get`, `_expected_422` | exact |
| `tests/test_api.py` (extend source-pin tuple ~253-289) | test (static source pins) | transform | the tuple itself | exact |
| `tests/test_browser_pins.py` (comment only, 27 IN-11, lines 126-128) | test comment | n/a | same lines | exact |
| `docs/architecture/decision_log.md` (append L44) | doc | append-only log | L40-L43 (headings at 2482, 2600, 2715, 2862) | exact |
| `docs/architecture/web-ui.md` (lines 79-81) | doc | n/a | the sentence it edits | exact |
| `docs/tech_debt/active/2026-10-21-phase-18-review-info-findings-deferred.md` (new, nice) | debt item | n/a | `docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md` + `TEMPLATE.md` | role-match |
| `docs/tech_debt/active/2026-10-21-tip-chamfer-effective-gate-reads-the-request.md` (new, must) | debt item | n/a | `TEMPLATE.md`; Severity `must` peers in INDEX | role-match |
| `docs/tech_debt/active/...root-shape-bogus-loads-a-blank-select.md` to `resolved/` | debt retire | n/a | Pitfall 8 precedents (`0fd2b98`, `b9755ad`, `991ba24`, `5a3332f`) | exact |
| `docs/tech_debt/active/2026-10-09-phase-19-review-...-deferred.md` to `resolved/` | debt retire | n/a | same | exact |
| `docs/tech_debt/INDEX.md` (rows 19, 32, 33; two new rows) | index | n/a | existing Active/Resolved tables | exact |
| `docs/ideas/2026-10-21-<slug>.md` (new, 24 IN-01 behavioural half) + `docs/ideas/INDEX.md` row | idea | n/a | `docs/ideas/TEMPLATE.md`; `2026-10-15-run-make-test-image-in-ci.md` | role-match |
| `src/spur/calc.py` (`root_mode` docstring, 18 IN-07) | docstring | n/a | docstring at `calc.py:1674-1690` | exact |
| `Makefile` (comment at ~226, D-17) | comment | n/a | same lines | exact |
| `bench/RESULTS.md` (new `## Refuse the bad link (Phase 28)` + `### Seen red once (Phase 28)`) | bench record | n/a | `### Seen red once (Phase 27)` at line 6591 | exact |
| `*-REVIEW-DISPOSITION.md` for 10, 18, 19, 21, 22, 23, 24, 26, 27 | triage record | n/a | commit `9001695` (Phase 14-16 triage) + `26-REVIEW-DISPOSITION.md` shape | exact |
| `.planning/phases/26-gate-fails-with-a-cause/26-REVIEW-DISPOSITION.md` hang item (`docs/tech_debt/active/2026-10-10-make-verify-hung-...md` lines 8, 61, D-17) | comment/path cites | n/a | same | exact |

## Pattern Assignments

### `src/spur/static/app.js` : rejected map and bad-link refusal (client state, event-driven)

**Analog:** `stash` Map in the same file (declared in the selectors section; cleared on Reset on the pinned line).

**Declaration precedent** (app.js:292-300, the `stash` comment and `const stash = new Map();`). Declare `rejected` as `new Map()` near `const defaults = {};` (line 11), NOT in the relations/selectors sections (their guards forbid `.value =`, `tests/test_api.py:376-402`).

**Current `readHash` and `gearQuery` (app.js:105-120), pinned lines marked:**
```js
function readHash() {
  const h = new URLSearchParams(location.hash.slice(1));
  for (const [name, { input }] of fields) input.value = h.get(name) ?? defaults[name];   // PINNED
  mateInput.value = h.get('mate_teeth') ?? '';                                            // PINNED tail
  applyRelations();
  deriveSelectors();
}
function gearQuery() {
  const q = new URLSearchParams();
  for (const [name, { input }] of fields) {
    if (input.value !== '' && String(input.value) !== String(defaults[name])) q.set(name, input.value); // PINNED
  }
  return q;
}
```

**Pattern to apply (RESEARCH-verified prototype; names are discretion):**
```js
const rejected = new Map(); // name -> raw token its control could not hold (L44)
function refuse(name, input, token) {
  if (token && input.value === '') rejected.set(name, token);
}
// readHash: rejected.clear(); pinned loop; read-back loop; mate assigned once early + refuse('mate_teeth', ...); pinned tail unchanged
// gearQuery: first line in the loop: if (rejected.has(name)) { q.set(name, rejected.get(name)); continue; }
// update() (app.js:244): const mate = mateInput.value || rejected.get('mate_teeth') || '';
// wiring: form.addEventListener('input', (e) => rejected.delete(e.target.name));   // NEW separate line; existing form 'input' listener is pinned
//         mateInput.addEventListener('input', () => rejected.delete('mate_teeth')); // NEW; leave app.js:609 scheduleUpdate line alone
// Reset (app.js:615-622): add `rejected.clear();` on a NEW line before the pinned `mateInput.value = ''; stash.clear(); ...`
```

**Constraints (from `tests/test_api.py`):** no line starting `['word',` outside `DIMS` (157-165, 173-182); no quoted GearParams field name or `.module`-style property outside `DIMS` (295-311); `fields.set(` appears once (317); `'mate_teeth'` is allowed (not a GearParams field); selector `<select>`s (name `''`) are not swept (only `fields` and the mate box are read back).

**Error path:** unchanged. `problems()` (app.js:187-202) and `fail()` already mark `loc[1]`/`ctx.fields` and return before the STL request. Do not edit them.

---

### `src/spur/static/app.js` : `root_fillet` label (client label, transform)

**Analog:** `DIMS` rows with label functions (app.js:17 and 39):
```js
['span', (d) => `Span over ${d.span_teeth} teeth`],
['hex_cell_effective', (d) => `Honeycomb cell A/F (${d.hex_cell_count} cells)`],
```
Current row (app.js:23): `['root_fillet', 'Root fillet used'],`. Replace with:
```js
['root_fillet', (d) => (d.root_form_d != null ? 'Hob tip radius used' : 'Root fillet used')],
```
Key confirmed: `calc.py:1700-1708` (`curve` non-None implies `cutter` non-None), `calc.py:1091-1095`, `calc.py:1292`. Loose `!= null`. Own commit; also retires the Phase 19 debt item (its own Next step says so).

---

### `src/spur/static/app.js` : 24 IN-01 comment (292-299) and 24 IN-02 / CX-03 wording

**Analog:** the existing `stash` comment block (quoted above in context). Pitfall 5: this block is inside `-- selectors (L42)`; `tests/test_api.py:401-402` counts `.value =` matches there INCLUDING comments and requires exactly one. The rewritten comment must not spell a value assignment. Each fix is its own commit.

---

### `tests/test_browser.py` : replace step `root_shape=bogus as today` (test, request-response)

**Analog:** the old step (~1802-1857) for harness shape; `invalid field marked` (~791-826) for assertions; helpers `_follow_link` (211-224), `_api_get` / `_expected_422` (135-208).

**Step/harness skeleton to copy** (old step, test_browser.py ~1802-1830):
```python
with step("root_shape=bogus as today", no_foreign_key):
    assert eval_str(page, FRAGMENT) != BOGUS_LINK, ...
    with page.expect_request(lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS) as info_request:
        page.evaluate("(f) => { location.hash = f; }", BOGUS_LINK)
    info_query = urllib.parse.urlsplit(info_request.value.url).query
    select = "() => document.querySelector('select[name=root_shape]')"
    select_value = eval_str(page, f"() => ({select})().value")
    select_index = eval_int(page, f"() => ({select})().selectedIndex")
```
**New oracle shape** (RESEARCH, composed from 177-224 and 791-826):
```python
sent = _follow_link(page, "teeth=abc")
status, body = _api_get(server, "/api/info", sent)
assert status == 422
marked, texts = _expected_422(properties, body)
expect(page.locator("#messages .error")).to_have_text(texts)
assert set(page.locator("label.field.invalid .name").all_text_contents()) == marked
assert eval_str(page, FRAGMENT) == "teeth=abc"
```
Steps wanted (D-08): `root_shape=bogus`, `recess_sides=bogus`, `teeth=abc`, `mate_teeth=abc` (`marked == set()`, no `.invalid`), edit-own-field recovery, different-field edit keeps token, Reset recovery, fresh-page load of one bad link (fragment on the `goto` URL; `data-triangles` is `None`, no STL, `#dl-stl` has no `href`), valid link leaves `label.field.invalid` count 0. "No STL" via recorder `seen` count of `/api/model.stl` before/after plus `page.wait_for_timeout(DEBOUNCE_SETTLE_MS)`; "no new part" via `data-triangles` equals earlier `declared`. Use bad tokens the API refuses only (`bogus`, `abc`), never `22.` etc. Wrap actions in `page.expect_request(lambda r: "/api/info" in r.url, timeout=BUILD_WAIT_MS)`. No `.skip` (pins scan). Drop `BOGUS_LINK`/`TODAY` (lines 104-109, they cite the moving debt path). Cite `update()` by name at lines ~1603 and 1614 (26 IN-03).

**Red-first order (D-08, Pitfall 2):** apply fix, run old step, record first failure line of that step (prototype: `/api/info was sent 'teeth=22&root_shape=bogus'`); rewrite; revert only `app.js`, record new pin red. Logs to `.planning/phases/28-refuse-the-bad-link/investigation/`. Command: `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"`.

---

### `tests/test_api.py` : source-pin tuple (test, static transform)

**Analog:** the tuple at ~253-289 (`test_the_shareable_link_round_trips_every_field_through_generic_code`). Snippets compared against `collapsed_source = re.sub(r"\s+", " ", source)`:
```python
"for (const [name, { input }] of fields) input.value = h.get(name) ?? defaults[name];",
"mateInput.value = h.get('mate_teeth') ?? ''; applyRelations(); deriveSelectors(); }",
"form.addEventListener('input', () => { applyRelations(); deriveSelectors(); scheduleUpdate(); });",
"mateInput.value = ''; stash.clear(); applyRelations(); deriveSelectors(); update();",
```
Add tokens for the new lines (e.g. the `rejected.has(name)` early-continue, the two new listener lines, `rejected.clear();`). Also `test_api.py:580-581` pins `if (input.value !== '' && String(input.value) !== String(defaults[name])) q.set(name, input.value);`; keep it byte-intact. Quick run: `.venv/bin/python -m pytest --no-cov -n0 -q -p no:cacheprovider tests/test_api.py -k "shareable_link or every_key_the_ui or root_form_d_is_never or root_shape"`.

---

### `tests/test_browser_pins.py` (27 IN-11, comment only)

**Analog:** the lines themselves (126-128): `# The allowance is per statement: ...` which RESEARCH/27-REVIEW says is wrong; replace with the review's text (27-REVIEW IN-11). Comment-only commit; no `skip/xfail/getenv` words may be introduced.

---

### `docs/architecture/decision_log.md` : append `L44`

**Analog:** L43 at line 2862 (heading + `Date:` + prose paragraphs + `Reversibility.` + `Reason:`). Heading style:
```
## L43 — The gate's bar is 300 s on the 18-CPU Apple M5 Max, ... (amends L34)

Date: 2026-10-14.

L34 stays as written. L43 amends ...
```
Closer analog for "amends/supersedes without editing the earlier entry": L42 at 2715 (cites L39/L41). Content per D-07: refused tokens (D-02), mechanism (D-01), clear rules (D-03), blank stays default and API 422s on `''` (D-06), unknown keys ignored, mate box message-without-outline (D-05), tokens the API accepts but a number box blanks (` 22`, `1_0`, `22.`/`5.`/`+5` for `face_width`) now sent and built as the server reads them. Amends L39 (text at ~2393-2394, 2448), supersedes L42's byte-identical sentence (~2795-2802, 2683). Do NOT edit L39/L42. Cite measurements to `bench/RESULTS.md` sections.

---

### `docs/architecture/web-ui.md` lines 79-81

Replace the sentence "`#root_shape=bogus` is pinned as today's behaviour and filed as debt." with the new contract (four links refused through the 422 path, L44). Optionally one sentence under `## Errors` (line 47) and the `rejected` map under `## Shape` (32-36). Verify: `grep -n "pinned as today" docs/architecture/web-ui.md` prints nothing.

---

### New debt items (nice for Phase 18 + 10 IN-01; must for 10 IN-02)

**Analog:** `docs/tech_debt/TEMPLATE.md`:
```
# <short title>

Severity: <blocker | must | nice>
Status: active
Date: YYYY-MM-DD
Source: <task / review / conversation that surfaced it>
Related files:
- <path:line>

## Context
## Why it matters
## Next step     <- "revisit when <trigger>"
```
Existing sibling for tone: `2026-10-09-phase-19-review-info-findings-deferred.md`. INDEX row shape (docs/tech_debt/INDEX.md Active table): `| nice | [Title](active/<file>.md) | <trigger> |`. Triggers: Phase 18 item = next phase changing trochoid/hob-root maths in `calc.py` or tests (D-12), plus a separate trigger line for 10 IN-01 (`bench/tip_chamfer_spike.py:201,286` hard-code `3.0`, D-18); 10 IN-02 item is `must`, Next step = human decision (fix under new `Lxx` with its own `make fixture.regen` commit, or keep with reason, D-13). Row 33 (`_wait_until_parked`) trigger mentions "Phase 28's info-finding triage"; restate it.

### Debt retirement mechanics

`git mv docs/tech_debt/active/2026-10-10-root-shape-bogus-loads-a-blank-select.md docs/tech_debt/resolved/`, flip `Status: resolved`, move INDEX row 19 to the Resolved table (`| [Title](resolved/...) | <sha or subject> |`). Pitfall 8: a commit cannot name its own sha; follow precedent: subject in the file, tiny follow-up commit writes the sha. Same for the Phase 19 item (row 32).

### New idea file

**Analog:** `docs/ideas/TEMPLATE.md` (Date / Source / Related files / Context / Why it matters / Next step), INDEX row `| 2026-10-21 | [Title](file.md) | <why not now> |` in `docs/ideas/INDEX.md` Open table, same commit.

---

### `*-REVIEW-DISPOSITION.md` files (triage records)

**Analog:** commit `9001695` and `26-REVIEW-DISPOSITION.md`. Two representations; edit BOTH:
```yaml
findings:
  - id: IN-03
    severity: info
    disposition: open        # -> fixed | deferred | skipped
    title: "..."
open: N                       # recount; `total:` unchanged
```
```
| Finding | Severity | Disposition | Source |
| IN-03 | info | open | - |      ->   | IN-03 | info | fixed | <sha> (branch commit; squashed into 1434a47) |
```
Vocabulary: `open`, `fixed`, `skipped`, `deferred`; deferred/skipped put the reason or debt path in the Source cell. One disposition per row (19 IN-02/IN-04: `fixed`, both shas in Source). Sources of draft cells: `27-TRIAGE.md`; shas verified to exist locally. 21 IN-04: `fixed` for 04a (`1981d93`), 04b named via `docs/tech_debt/active/2026-10-15-wait-until-parked-spins-without-a-pause.md` (D-16). 27 IN-11 `fixed` (comment commit), IN-12 `skipped`/`deferred` with reason (D-15). 18 IN-01 `fixed` `767317b`; IN-02, IN-06 `skipped` (overtaken); IN-07 `fixed` (docstring commit); IN-03/04/05/08 `deferred` to the nice item. Close gate: `grep -n '| info | open |'` over the nine files prints nothing.

---

### `src/spur/calc.py` `root_mode` docstring (18 IN-07, docstring only)

**Analog:** `calc.py:1674-1690`, numbered-refusal-order docstring. Add one line: a `rho` that is not a finite, non-negative mm value raises `ValueError` from `cutter` (`calc.py:1415-1416`) before any reason is decided; with nothing requested it is not read (`calc.py:1700`: `return RootMode("radial", "not requested", None)` precedes `cutter(p, rho)`). No number moves.

### `Makefile` ~226 and hang debt item (26 IN-04, D-17)

**Analog:** current comment text:
```
# What the image suite does not run, ... each traced to a red read on the
# unfixed recipe (.planning/phases/26-gate-fails-with-a-cause/investigation/26-06-redset.md).
```
Re-point at a durable source (`bench/RESULTS.md` section or `docs/`). Comment-only commit, also touching `docs/tech_debt/active/2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md` lines 8 and 61.

### `bench/RESULTS.md`

**Analog:** `### Seen red once (Phase 27)` (line 6591):
```
### Seen red once (Phase 27)
Each deliberate break was run red once and reverted, ... first failure line is copied from the kept log named in the row ...
| Plan | Test or step | Deliberate break | First failure line | Reverted |
|---|---|---|---|---|
```
New `## Refuse the bad link (Phase 28)` section with step timings and `### Seen red once (Phase 28)` in this table shape (old pin red vs fix; new pin red with `app.js` fix reverted; label red vs old label). Old step names elsewhere in the file stay as history.

## Shared Patterns

### Pinned-token discipline
**Source:** `tests/test_api.py:253-289`, `173-182`, `295-317`, `328-402`. **Apply to:** every `app.js` edit. Add statements between pinned lines, never rewrite them; no row-shaped `['word',` outside `DIMS`; no GearParams field name quoted outside `DIMS`; no value writes in relations/selectors sections (selectors: exactly one, comments counted).

### Server decides, no client wording (L02)
**Source:** `problems()` / `fail()` in app.js:187-202 with test oracle `_expected_422`. **Apply to:** all refusal code and tests. No enum or numeric regex, no "got 'bogus'" suffix.

### One concern per commit; fix + pin + L44 + docs + debt retirement together
**Source:** CONTEXT D-07, CLAUDE.md. Commit order: (1) refusal fix with pin, L44, web-ui.md, debt retirement; (2) label; (3) 24 IN-01; (4) 24 IN-02/CX-03; (5) 27 IN-11 comment; (6) 26 IN-04 comments; (7) 18 IN-07 docstring; (8) debt/idea files; (9) disposition records.

### Debt/idea capture
**Source:** `docs/tech_debt/TEMPLATE.md`, `docs/ideas/TEMPLATE.md`, INDEX files. INDEX row in the same commit as the file.

### Gate
`make verify` (state the result line); browser command above; `git diff --exit-code v0.5 -- tests/regression/` stays empty; no `TODO|FIXME|XXX|HACK|NotImplementedError` in `*.py`/`*.js`.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| (none) | | | Every file has an in-repo analog. The rejected-map read-back (`refuse`) has no prior code twin but follows the `stash` Map precedent; the verified shape is in 28-RESEARCH.md. |

## Metadata

**Analog search scope:** `src/spur/static/app.js`, `src/spur/calc.py`, `tests/test_browser.py`, `tests/test_api.py`, `tests/test_browser_pins.py`, `docs/architecture/`, `docs/tech_debt/`, `docs/ideas/`, `bench/RESULTS.md`, `Makefile`, `.planning/**/*-REVIEW-DISPOSITION.md`
**Files scanned:** about 25 (targeted reads; RESEARCH.md holds the verbatim pin inventory)
**Line numbers drift with any `app.js` or `test_browser.py` edit; re-read before editing.**
**Pattern extraction date:** 2026-10-21
