# Phase 33: Interfaces and Parity - Context

**Gathered:** 2026-10-27
**Status:** Ready for planning

<domain>
## Phase Boundary

The shaft that Phases 31 and 32 built becomes usable from all three front ends:

- `/api/shaft/schema`, `/api/shaft/info`, `/api/shaft/model.stl` and `/api/shaft/model.step`.
  They use the gear routes' admission, cache and error contract, with `_serve_model` as the
  second caller.
- `spur shaft info|export`.
- A Gear | Shaft switch on the web page.

The API and the CLI also accept a designation in place of the four spline fields. One
parametrised test proves the web page, the API and the CLI agree on every shaft number and on the
download name. WR-02 is fixed on the same edit of `refuse()`/`gearQuery()` that the part switch
makes, and its debt item is retired in the fixing commit.

Not in this phase:
- No tolerance-table value and no fit window (Phase 34).
- No designation input on the web page (D-10).
- No new `GearParams` field. No edit to `params.py`, `calc.py`, `tests/regression/`, `ci.yml` or
  `requirements.txt` (30 D-11).
- The gear `/api/schema` response stays byte-equal.

</domain>

<decisions>
## Implementation Decisions

### Carried forward (locked before this discussion; do not re-ask)
- All new routes live under `/api/shaft/`. The gear routes, their query keys and the gear
  `/api/schema` bytes do not change (L46, Phase 30 route-table pin, `make gear.unchanged`).
- The shaft field names and defaults: `reference_d`, `module`, `teeth`, `fit`, `splined_length`,
  `end_chamfer`, `shank_d`, `shank_length`. The default is `W 25x1.25x18x8f` (31 D-01..D-04,
  L47). Switching part never carries values across (31 D-03).
- `end_chamfer_effective` goes on the wire with the other `ShaftDimensions` keys (32 D-06).
- The shaft's result rows come from a schema-carried `dims` key: a model-level
  `json_schema_extra` list of `{key, label, unit}` on `/api/shaft/schema`, with `unit: ""` rows
  rendered as text (the designation). They do not come from a second row table in `app.js`; two
  `tests/test_api.py` pins forbid that. The gear keeps its existing `DIMS` array, because the gear
  schema must stay byte-equal (research ARCHITECTURE §4.5).
- A gear link never carries a `part` key. The shaft link is `part=shaft&<non-default shaft
  fields>` (L46, research §5).
- The CLI is a `spur shaft info|export` sub-command group. It duplicates the gear's ~15 lines
  and does not abstract over the part. The existing `spur info/export` argv is untouched, and
  the CLI never imports `app`/`fastapi`/`starlette` (L04, research §4.4).
- The conflict rule reads `request.query_params` keys on the API and the non-`None` flag dict on
  the CLI, and never `model_fields_set` (research F2). Both call one shared pure function, e.g.
  `shaft_params.resolve_shaft(designation, given)`.
- **Phase close:** record the `make verify` result line. `git diff --exit-code v0.6 --
  tests/regression/ .github/workflows/ci.yml` must be empty.

### WR-02: a token the number box blanks but the API accepts
- **D-01:** **The API refuses it with a 422.** The page's existing L44 mechanism does the rest:
  the `rejected` map sends the token as given, `problems()` marks the field, `fail()` returns
  before the STL request, and no part is drawn. The form and the part then agree: a blank box
  never sits over a non-default part. The refusal lives in the `app.py` query layer, e.g. a
  dependency or pre-check over `request.query_params` that runs before pydantic. It does not live
  in `params.py` (frozen, 30 D-11), and it must not change the gear `/api/schema` bytes. Log a
  new `Lxx` that amends L44's paragraph **The server decides** (that paragraph built these
  tokens), with the gear-side 200-to-422 move recorded as an invalid-link change of the L44/L46
  class. The fixture check at discuss time found no such token in
  `tests/regression/golden_requests.json` or `pre_v0_2.json`. The golden sweep proves it.
  — **Reversibility:** costly — once shipped, accepting the tokens again turns refused links
  back into builds under a blank box. Undoing it needs another Lxx and moves the browser steps,
  the pins and `web-ui.md` together.
- **D-02:** **"Non-canonical" means exactly what a Chromium number input reads back as blank.**
  It is not a hand-written regex. The planner probes it in the browser first, over every gear
  number field, `mate_teeth` and every shaft number field. The probe set must include at least:
  ` 22`, `22 `, `%2022`, `1_0`, `22.`, `5.`, `+5`, `+22`, `2.`, and controls that must stay
  accepted: `22`, `2.5`, `-1`, `1e1`, `.5`. The token list in the debt item is inferred, not
  observed; record the observed table in `bench/RESULTS.md`. The server rule is then written to
  match that table and pinned by a test that walks it. If Chromium holds a token that the rule
  would refuse, or blanks one that the rule accepts, stop and ask.
- **D-03:** **Reach: the gear and shaft API query layers, through one shared rule. The CLI is
  unchanged.** argparse's `int`/`float` parsing stays as it is: the CLI has no number box, so
  WR-02 cannot occur there. The parity fixtures use canonical values only.
- **D-04:** **The 422 wording quotes the token and suggests the canonical form when it is
  unambiguous.** Example: `"5." is not a number as written; write it as 5 or 5.0`. When no single
  canonical form is obvious, say `write it as a plain number, e.g. 22 or 2.5`. The `loc` names
  the field (`["query", "<field>"]`, the `app.py` 422 envelope), so the unchanged `problems()`
  marks the box. For `mate_teeth` the message shows with no outline (L44 D-05, unchanged).
- **D-05:** `tests/test_browser.py`'s `ACCEPTED_LINK = "face_width=5."` and the step
  `blank, unknown and accepted tokens` flip from "built" to "refused". Each is seen red once
  against the old behaviour and the red is recorded under a Phase 33 heading in
  `bench/RESULTS.md`. Blank values (`teeth=`) still mean the default on the page (L44 D-06,
  unchanged).
- **D-06:** Retire the debt item
  `docs/tech_debt/active/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md` in the
  fixing commit: `Status: resolved`, the sha, `git mv` into `resolved/`, and the INDEX row moved.

### Designation as input (API and CLI)
- **D-07:** **A designation together with any of `reference_d`, `module`, `teeth` or `fit` is a
  422, whatever the values.** The message names `designation` and each overlapping field. The
  rule is deliberately stricter than REQ-designation-input's "contradicts", so there is no
  equality question across `25`, `25.0` and `25,0` (research §4.3).
- **D-08:** A designation combines freely with the four solid fields
  (`splined_length`, `end_chamfer`, `shank_d`, `shank_length`). The designation describes the
  spline, not the solid. `?designation=W 30x2x14x8f&splined_length=50` is valid.
- **D-09:** The input key is `designation` on the API and `--designation` on the CLI, the same
  word as the result row `designation`. An unparseable designation is a 422 with `loc`
  `["query","designation"]` naming the bad token (the codec's existing refusal text). On the CLI
  it is exit 2.
  — **Reversibility:** one-way — `designation` becomes a public URL query key when Phase 33
  ships (L05).

### Web designation
- **D-10:** **Print-only.** The page shows the designation as a `unit: ""` result row and has no
  paste box. There is no `GET /api/shaft/designation` route. The page holds no designation
  grammar (L02).
- **D-11:** A page link carrying `designation=` is **ignored**, like any unknown key (L44 D-06).
  Page links carry flat fields only, and Copy link writes flat fields.

### Part switch
- **D-12:** **A Gear | Shaft two-button radio toggle** at the top of `<aside>`, above and
  outside `#params`. The form's `input` listeners never see it and it is never a field (the L42
  rule: the `fields.set(` count stays 1). It must be keyboard-reachable as a radio group.
- **D-13:** **Every switch loads that part's defaults.** There is no per-part memory. The hash
  becomes empty for the gear and `#part=shaft` for the shaft, so the URL always equals the form.
  Reset resets the current part only.
- **D-14:** **History follows whatever a field edit does today.** The planner reads how
  `app.js` rewrites the hash on an edit (push or replace) and uses the same call for a switch.
  No new history rule. If it pushes, a `hashchange` that changes `part` must await
  `buildForm(part)` before `readHash()` (research §5).
- **D-15:** **A bad `part` value (`#part=bogus`, `#part=gear`, any non-empty value other than
  `shaft`) gets a page-worded message, and nothing is built.** Example: `Unknown part "bogus" in
  the link; use the Gear or Shaft switch`. It shows in the existing message area. The gear form
  is shown, nothing is drawn, and the toggle selects neither. This is a narrow, logged exception
  to "the server words refusals" (L02/L44): no route takes `part`, so no server can word it.
  Record it in the same new `Lxx` as D-01. `part=gear` is not a second spelling of the gear
  link (research §5).

### Claude's Discretion
- How precisely the parity test compares numbers. Raw JSON from the API, the CLI's printed JSON
  and the web table's displayed digits will differ by formatting. The planner picks one rule
  (e.g. compare at the web table's displayed precision, and raw-equal between API and CLI),
  records it beside the test, and sees it red once on a perturbed number.
- The fixed set of parity shafts. At minimum: the default, W30x2x14 (lower x edge), one odd-z
  shaft (M_Re `null`), and one with `shank_length=0`.
- How a `null` shaft row is shown (e.g. a dash with its warning listed). It must not imply a
  number (L08).
- `<title>`, `.sub`, the canvas `aria-label` and the `.hint` text per part, swapped by the part
  descriptor. The gear text stays the static default.
- The viewer framing for a long shaft along Z (`placeGrid()`/`fit()`), checked visually.
- The CLI flag spelling follows the existing generator (`--reference-d` from `reference_d`).
- Whether the shaft fields get `enabled_when` (dim the shank fields when `shank_length` is 0),
  left open by 32-CONTEXT.
- The README scope wording and shaft examples (moved here by 30 D-19). The README must not
  advertise a fit window before Phase 34.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scope and requirements
- `.planning/ROADMAP.md` §"Phase 33: Interfaces and Parity": goal, the 5 success criteria and
  the boundaries.
- `.planning/REQUIREMENTS.md`: REQ-shaft-api, REQ-shaft-cli, REQ-shaft-web,
  REQ-designation-input, REQ-shaft-parity, REQ-wr02-fixed.

### Decisions
- `docs/architecture/decision_log.md` L44 (line ~2948): the `rejected` map, `refuse()`, **The
  server decides** (amended by D-01), D-05 mate box and D-06 blank/unknown keys.
- `docs/architecture/decision_log.md` L46: part switch, stray `part=` refused, and the shaft link
  contract freezing at the first shaft link published here.
- `docs/architecture/decision_log.md` L47 and L48: shaft maths, field bounds and the solid. These
  are what goes on the wire.
- L02, L03, L04, L05 and L08 in the same file.

### Design research
- `.planning/research/ARCHITECTURE.md` §4.2 to §4.5 and §5: routes, `resolve_shaft`, CLI shape,
  the schema-carried `dims` rows, and the web part descriptor with its mechanics.
- `.planning/research/ARCHITECTURE.md` F2: why not `model_fields_set`.
- `.planning/research/PITFALLS.md`: stray `part=` and a designation that disagrees with fields.

### Debt being retired
- `docs/tech_debt/active/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md`: WR-02.
  Its token list is inferred, not observed.
- `bench/RESULTS.md` `### Tokens a control cannot hold (28-01)`: the earlier probe, `teeth` and
  `face_width` only.

### Prior phase context
- `.planning/phases/30-scope-seam-and-gear-safety-guard/30-CONTEXT.md`: D-07 (`_serve_model`),
  D-11 (frozen files) and D-19 (README moves here).
- `.planning/phases/31-shaft-maths-parameters-and-designation/31-CONTEXT.md`: D-01..D-05 (field
  names, defaults, designation print form).
- `.planning/phases/32-the-shaft-solid/32-CONTEXT.md`: D-06 (`end_chamfer_effective`) and
  `enabled_when` left open.

### Project
- `docs/architecture/web-ui.md`: the page's current behaviour. Update it with the part switch.
- `docs/CODING_VALUES.md`: the coding standard.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app.py:385` `_serve_model(params: Part, fmt, quality, request, backend)`: cache, slot, build,
  gzip, error mapping and records. The shaft model routes call it directly.
- `app.py:243` `_gear(q)` strips query extras before the cache key. A `_shaft(q, request)`
  mirrors it and also resolves the designation.
- `app.py:374` `/api/schema` returns `GearParams.model_json_schema()`. The shaft schema route
  does the same with `ShaftParams`, plus the model-level `dims` key.
- `cli.py:42` `_add_gear_args()` generates flags from `model_fields`, `cli.py:96` `info` prints
  JSON, and `cli.py:105` `export` picks the format by extension. Copy these for `shaft`.
- `din5480.py:252` `format_designation()` and `din5480.py:257` `parse_designation()` return a
  `Designation` (reference_d, module, teeth, fit).
- `shaft_params.py:91` `slug()` returns `spur_shaft_w{reference_d:g}x{module:g}x{teeth}` (no fit
  token). The parity test's download-name check reads this.
- `app.js`: `buildForm()` 54 is generic over `properties` (group, unit, step, enum,
  enabled_when). Also `refuse()` 115, `readHash()` 119, `gearQuery()` 132, `problems()` 206,
  `renderInfo()` 223 (loops the gear `DIMS` at 17-47, assumes mm), `update()` 261, `write()` 420,
  download naming 501, Reset 640 and Copy link 649.

### Established Patterns
- L44 `rejected` map: the page never parses a token. It sends what the control cannot hold and
  lets the server's 422 mark the field. D-01 relies on this unchanged.
- Each guard or pin is seen red once and the red is recorded in `bench/RESULTS.md`.
- The `tests/test_api.py` app.js token pins (~170-345) count tokens. Any `app.js` edit must keep
  every earlier token or log why (L44 amendments are the precedent).
- `tests/test_browser.py` uses a real uvicorn and BuildPool and walks `golden_requests.json`
  (~30 s). The new shaft steps add to the gate time; record the delta (criterion 5).

### Integration Points
- `index.html:19` `#params` inside `<aside>`. The toggle goes above it, inside `<aside>`.
- The Phase 30 route-table pin: the four shaft routes are additions under `/api/shaft/`.
- `make gear.unchanged`: proves every `app.py` edit leaves the gear untouched.
- The import contracts: `spur.cli` must not name `shaft_model`, and the CLI reaches the kernel
  through `model.export`.

</code_context>

<specifics>
## Specific Ideas

- WR-02 refusal text, user-approved shape: `"5." is not a number as written; write it as 5 or
  5.0`.
- Bad-part text shape: `Unknown part "bogus" in the link; use the Gear or Shaft switch`.
- A valid designation-plus-solid request: `?designation=W 30x2x14x8f&splined_length=50`.

</specifics>

<deferred>
## Deferred Ideas

- A designation paste box on the web page, with `GET /api/shaft/designation?text=`. Declined for
  v0.7 (D-10). Revisit if users ask to type a designation in the page.
- A `<select>` part control. Reconsider when a third part type arrives (L46 spline families).
- Applying the D-02 strict number rule to the CLI. Declined (D-03): there is no number box, so
  there is no WR-02.

</deferred>

---

*Phase: 33-interfaces-and-parity*
*Context gathered: 2026-10-27*
