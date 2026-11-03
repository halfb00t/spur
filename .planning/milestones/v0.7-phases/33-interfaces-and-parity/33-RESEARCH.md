# Phase 33: Interfaces and Parity - Research

**Researched:** 2026-10-27
**Domain:** a second part type (DIN 5480 shaft) added to a FastAPI + argparse + vanilla-JS app; one server-side link-token rule; a browser-proved part switch
**Confidence:** HIGH for every in-repo fact and for the two probes run this session (Chromium number box, FastAPI dependency ordering); MEDIUM for the app.js shape (design, not built); the xdist claim is `[ASSUMED]`.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Carried forward (locked before this discussion; do not re-ask)
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

#### WR-02: a token the number box blanks but the API accepts
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

#### Designation as input (API and CLI)
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

#### Web designation
- **D-10:** **Print-only.** The page shows the designation as a `unit: ""` result row and has no
  paste box. There is no `GET /api/shaft/designation` route. The page holds no designation
  grammar (L02).
- **D-11:** A page link carrying `designation=` is **ignored**, like any unknown key (L44 D-06).
  Page links carry flat fields only, and Copy link writes flat fields.

#### Part switch
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

### Deferred Ideas (OUT OF SCOPE)
- A designation paste box on the web page, with `GET /api/shaft/designation?text=`. Declined for
  v0.7 (D-10). Revisit if users ask to type a designation in the page.
- A `<select>` part control. Reconsider when a third part type arrives (L46 spline families).
- Applying the D-02 strict number rule to the CLI. Declined (D-03): there is no number box, so
  there is no WR-02.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-shaft-api | `/api/shaft/schema`, `/info`, `/model.stl`, `/model.step` with the gear routes' admission, cache and error contract | `_serve_model` is already the shared serving half (app.py:385); route skeletons and the `_shaft()` strip-to-`ShaftParams` rule in Architecture Patterns 1-2; 422 envelope shapes observed |
| REQ-shaft-cli | `spur shaft info\|export` builds the same part and prints the same numbers | cli.py structure read; duplicate-not-abstract skeleton in Pattern 5; import-linter doorway constraint |
| REQ-shaft-web | part switch, shaft preview, schema-carried rows, designation row, downloads, `part=shaft` link round trip, bad `part` refused, browser test | app.js pins that constrain every edit (Pitfalls 1-9), `fit` is a string field the form cannot render today (Pitfall 1), the `.hidden=` guard (Pitfall 4), browser-test recorder constraints (Pitfall 8) |
| REQ-designation-input | designation in place of the fields (API + CLI); conflict is a 422 naming the fields | prototype run: a `Depends` pre-check beats model validation, so the conflict sentence wins (Pattern 2, Pitfall 5) |
| REQ-shaft-parity | one parametrised test, web = API = CLI on every shaft number and the download name | three readers, one comparison rule, the download-name fact for the CLI (Open Question 2), xdist/server cost (Pitfall 9) |
| REQ-wr02-fixed | a token the number box blanks but the API accepts is refused; debt item retired in the fixing commit | Chromium probe of 89 tokens, the four-condition rule that matches it, the invariant-form test (Pattern 3, Chromium Table) |
</phase_requirements>

## Project Constraints (from CLAUDE.md / AGENTS.md)

- `make verify` is the gate; state the command and result line in the reply. `make check` adds Docker checks. [VERIFIED: /Users/half/git/halfb00t/spur/CLAUDE.md "How to verify"]
- Two standing rules: a printed number is a number someone cuts metal to, so an uncomputable value is a warning and no number (L08); a parameter the user did not set must never silently change the part, a direct conflict is a `422`, not a guess (L03, L05).
- Stop and ask on: an architectural claim not in the decision log, a locked decision that looks wrong, unverified library behaviour, conflicting evidence, a destructive operation, a stability-for-speed trade. This research raises Open Questions 1, 2 and 7 as ask-first items.
- New non-trivial choice -> 2-3 options + recommendation, then a new `Lxx`. Next free id is **L49** (L48 is the last entry). [VERIFIED: grep of `^## L` in docs/architecture/decision_log.md, last line `## L48 — How Phase 32 builds the DIN 5480 shaft's solid`]
- New behaviour ships with its tests in the same change; measured claims are recorded, not estimated; `TODO`/`pass`/unreachable branches fail `make verify`.
- Debt and ideas live in files (`docs/tech_debt/active/`, `docs/ideas/`) with an INDEX row; on fixing debt: `Status: resolved`, commit sha, `git mv` to `resolved/`, move the INDEX row, all in the fixing commit. State before the final reply whether an item was filed.
- Code style (docs/CODING_VALUES.md): comments carry the measurement or constraint; `calc.py`-style maths never imports `cadquery`; vendor types stop at their boundary; a parameter is validated once at the model boundary; `Any` is not written (mypy `disallow_any_explicit`); English throughout.
- Conventional Commits, one concern per commit. Surgical edits: do not refactor adjacent code.

## Summary

Phase 33 puts the finished shaft (31 maths, 32 solid) behind three front ends and fixes WR-02 on the same edit. Almost everything it needs already exists: `_serve_model` is already extracted and part-agnostic [VERIFIED: src/spur/app.py:385-509], `Part = GearParams | ShaftParams` [VERIFIED: src/spur/parts.py:16], `model._build` dispatches the shaft, and the pool, records and caches key on the params object. The new work is thin glue plus three delicate edges: (1) the `app.js` rewrite, which is fenced by ~45 token pins and two regex guards in `tests/test_api.py`; (2) one server-side rule that must match what Chromium's number box does, which I probed this session; (3) a test that proves three interfaces agree, which has to fit the browser test's recorder and the gate's xdist layout.

Four things are NOT in CONTEXT.md and the planner must handle them. (a) `fit` is `type: "string"` in the shaft schema with no `enum`, and `buildForm()` renders every non-enum property as `<input type=number>`, so the shaft form would render a number box for `8f`, blank it, and send nothing: the form needs a text-input branch. (b) The active **must** debt item `2026-10-27-shaft-volume-guard-accepts-an-uncut-chamfer.md` names "Phase 33 starts ... fix before that phase ships" as its trigger. (c) The `window.addEventListener('hashchange', () => { readHash(); update(); });` token is pinned verbatim, and D-14 requires the handler to await a form rebuild on a part change, so that pin must be amended with a logged reason (the L44 precedent). (d) The static guard `writes_a_field_shut` forbids `.hidden =`, `.style.display` and `classList.add('hidden')` anywhere in `app.js`, so hiding the mate box on the shaft has to be CSS driven by a `data-part` attribute.

**Primary recommendation:** build bottom-up in this order: a baseline `make verify` reading and the Chromium probe record; the volume-guard debt fix; the pure shared layer in `shaft_params.py` (`resolve_shaft`, `dims` schema key); the WR-02 rule as a `Depends` pre-check on all four number-taking API routes plus the shaft routes, landed with the pin flip, the Lxx and the debt retirement as ONE commit; the CLI group; then the page and its browser steps; then the parity step, docs, README, `bench/RESULTS.md`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Shaft numbers (`derive_shaft`) and designation codec | API / Backend (pure modules `shaft_calc`, `din5480`) | CLI (same call) | One definition of every number; pure, kernel-free (import contracts) |
| Designation-vs-fields rule, designation resolution | API / Backend (pure `shaft_params`) | CLI | One shared function so the sentence is identical on both (L03) |
| WR-02 "token as written" refusal | API / Backend (`app.py` query layer) | Browser (unchanged `rejected` map carries the token) | The server words refusals (L02); the page never parses a token |
| Admission, cache, gzip, error mapping, records | API / Backend (`_serve_model`) | Worker pool | Already shared; the shaft is its second caller |
| Result rows for the shaft | API / Backend (schema-carried `dims`) | Browser renders generically | L02 and the two `app.js` pins forbid a row table in JS |
| Part switch, hash `part=`, bad-`part` message | Browser / Client | — | No route takes `part`; the narrow logged exception of D-15 |
| Download filename | API / Backend (`Content-Disposition` from `slug()`) | Browser saves it | The page sets no filename; Playwright reads `suggested_filename` |
| Solid, STL/STEP bytes | Worker process (`model.export` -> `shaft_model`) | — | Unchanged; the CLI reaches it through `model.export` only |

## Standard Stack

No new dependency (a stated boundary). Everything below is already pinned and in use.

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.141.1 | routes, `Depends`, Query models | already the app [VERIFIED: requirements.txt `fastapi==0.141.1`] |
| Pydantic | 2.13.5 | `ShaftParams`, `ConfigDict(json_schema_extra=...)` | already the parameter layer [VERIFIED: requirements.txt `pydantic==2.13.5`] |
| Starlette | 1.6.0 | `Request.query_params.multi_items()` | via FastAPI [VERIFIED: requirements.txt `starlette==1.6.0`] |
| argparse | stdlib | `spur shaft` nested sub-parsers | the existing CLI parser (L04) |
| Playwright (Python) | 1.63.0 exact pin | browser steps, `expect_download` | already the gate's browser [VERIFIED: pyproject.toml `"playwright==1.63.0"`] |
| Chromium headless shell | 153.0.8010.12 | the number-box probe and browser test | [VERIFIED: probe user agent `HeadlessChrome/153.0.8010.12`, this session] |
| pytest + xdist + cov | per pyproject | tests | existing; `filterwarnings = ["error", ...]` is on |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `Depends` pre-check for WR-02 | a Starlette middleware that rewrites the query | a middleware would also touch `/api/schema`, `/api/health` and static; the dependency is per route and adds no OpenAPI parameter |
| `Annotated[ShaftInfoQuery, Query()]` + pre-check | a hand-parsed `Request` dependency | the Query model keeps `/docs` and `/openapi.json` describing the keys; recommended |
| native `<input type=radio>` for the toggle | `role=radio` buttons | native radios give arrow-key navigation and the group for free (D-12 "keyboard-reachable as a radio group") |
| regex for the WR-02 rule (hand-written, spec-derived) | the four-condition rule below | the HTML spec's "valid floating-point number" is NOT what Chromium does (it holds `1.e1`, `00022`); D-02 says match the probe |

**Installation:** none. **Version verification:** versions above are the repo's pins, read from `requirements.txt` and `pyproject.toml` this session; nothing is installed.

## Package Legitimacy Audit

No external package is installed or added in this phase (boundary: "no new dependency"), so there is nothing to run through `package-legitimacy check`. Packages removed `[SLOP]`: none. Packages flagged `[SUS]`: none.

## Architecture Patterns

### System Architecture Diagram

```
 browser (app.js)                         HTTP client                    CLI (cli.py)
   |  hash: ""  or  "part=shaft&f=v"        |                               |
   |  toggle (radios, outside #params)      |                               |
   v                                        v                               v
 partOf(hash) --bad--> message, nothing built
   | gear                  | shaft
   v                       v
 fetch api/schema      fetch api/shaft/schema   (+ dims rows)                 spur shaft info|export
 api/info?..           api/shaft/info?..                                      argparse -> non-None dict
 api/model.stl?..      api/shaft/model.stl?..                                      |
   |                       |                      |                                |
   +---------------+-------+----------------------+                                |
                   v                                                              |
   app.py  [dependency 1: number-as-written pre-check (gear + shaft number keys)] |
           [dependency 2 (shaft only): designation vs spline-field key conflict]   |
           Query model validates (FastAPI) --> _shaft(q): designation -> fields    |
                   |                                                              |
                   |        shaft_params.resolve_shaft(designation, given) <------+  (same function,
                   |        (pure; din5480.parse_designation inside)                  same sentences)
                   v
   info route: derive_shaft(p) -> ShaftDimensions (13 keys)      cli: derive_shaft(p).model_dump_json(indent=2)
   model route: _serve_model(p, fmt, quality, request, backend)
        cache -> _build_slot -> pool.export -> worker: model.export -> shaft_model.build_shaft
        -> gzip in slot -> Content-Disposition: attachment; filename="<p.slug()>.<fmt>"
```

### Recommended Project Structure
```
src/spur/
├── app.py            # + shaft routes, number-as-written dependency, ShaftInfoQuery/ShaftModelQuery, _shaft()
├── cli.py            # + `shaft` sub-parser group (info, export); gear argv untouched
├── shaft_params.py   # + model_config json_schema_extra {"dims": [...]}, resolve_shaft(), optional enabled_when
├── static/
│   ├── index.html    # + part switch above #params; title/aria/hint swapped by the descriptor
│   ├── app.js        # + part state, text-input branch, dims renderer, switch handler (see Pitfalls)
│   └── style.css     # + .part-switch, [data-part=shaft] .mate { display: none }
tests/
├── shaft_parity.py   # NEW shared readers (api_numbers, cli_numbers, web_numbers) + the fixed SHAFTS set
├── test_shaft_interfaces.py  # NEW, light (info/schema/422/designation; no kernel build) -- runs in the commit slice
├── test_api.py / test_cli.py # shaft route + CLI tests that build STL/STEP go in these (already "heavy")
└── test_browser.py   # + shaft steps; ACCEPTED_LINK and its step flip
```

### Pattern 1: Shaft routes are the gear routes' siblings (REQ-shaft-api)
**What:** a `ShaftInfoQuery(ShaftParams)` carrying `designation: str | None`, a `ShaftModelQuery` adding `quality`, a `_shaft(q)` that strips back to a plain `ShaftParams` so `info` and `model` share cache keys (pydantic equality includes the class, as `_gear()` documents at app.py:243-250), and `_serve_model` as the second caller.
**Example (prototype run in a scratch FastAPI app against the real `ShaftParams`; every printed result below was observed):**
```python
# Source: scratch prototype, run 2026-10-27 in the repo venv (not committed)
class ShaftInfoQuery(ShaftParams):
    designation: str | None = Field(None, description="DIN 5480 designation, in place of the spline fields")

@app.get("/api/shaft/info", dependencies=[Depends(_numbers_as_written_shaft), Depends(_designation_conflict)])
def shaft_info(q: Annotated[ShaftInfoQuery, Query()]) -> ShaftDimensions:
    return derive_shaft(_shaft(q))
```
Observed: `{}` -> 200; `designation=W 30x2x14x8f` -> 200 with 30/2/14; `designation=...&splined_length=50` -> 200 (D-08); `designation=bogus` -> 422 `loc ["query","designation"]`, `"The designation must start with the type letter W, not 'bogus'."`; `designation=W 25x1.25x18x8F` -> 422 naming the fit token `8F`. OpenAPI lists the nine keys `reference_d ... shank_length, designation`.
**`_shaft(q)`** must (a) return `ShaftParams(**q.model_dump(include=set(ShaftParams.model_fields)))` when no designation, (b) overlay `parse_designation(...)._asdict()` when there is one, then build `ShaftParams(...)` and map a `ValidationError` (the Query model validated the DEFAULT spline fields, which are feasible; the designation's own values are validated only by this second build, so an infeasible designation such as `W 100x1x20x8f` fails here) to a 422 `HTTPException` with `loc ["query","designation"]` and the codec/validator message. Observed for `W 100x1x20x8f`: `type "infeasible"`, message "A reference diameter of 100 mm with module 1 and 20 teeth needs a profile shift of +39.4500, above the allowed range -0.05 to +0.45. ...". Without the mapping this is an unhandled `ValidationError` -> 500.

### Pattern 2: The designation-vs-field conflict is a `Depends` pre-check, not a model rule (REQ-designation-input)
**What:** FastAPI solves `dependencies=[...]` and sub-dependencies before it validates the Query model, and an `HTTPException(422, detail=[...])` raised there propagates at once. This matters: `?designation=W 30x2x14x8f&module=3` would otherwise reach model validation with `module=3` against the default 25 mm / 18 teeth and answer "needs a profile shift of -5.3833", which hides the real problem.
**Example:**
```python
# Source: scratch prototype, observed: 422 {"loc": ["query","designation"], "type": "conflict",
#   "msg": "designation cannot be combined with module", "ctx": {"fields": ["designation","module"]}}
def _designation_conflict(request: Request) -> None:
    keys = set(request.query_params)
    if "designation" in keys and (clash := [k for k in SPLINE_KEYS if k in keys]):
        raise HTTPException(422, detail=[{"loc": ["query", "designation"], "type": "conflict",
            "msg": conflict_sentence(clash), "ctx": {"fields": ["designation", *clash]}}])
```
Put the **sentence and the key list** in the pure function (`shaft_params`), so the CLI prints the same words. `SPLINE_KEYS = ("reference_d", "module", "teeth", "fit")`; the rule reads key PRESENCE (D-07: whatever the values), never `model_fields_set` (ARCHITECTURE F2: on a FastAPI query model an empty query reports every field as set) [CITED: .planning/research/ARCHITECTURE.md F2].
**CLI side:** `given = {k: v for k in SPLINE_KEYS if (v := getattr(ns, k)) is not None}`; conflict or unparseable designation -> `error: ...` on stderr, `SystemExit(2)` (the `_params` pattern, cli.py:59-68).

### Pattern 3: WR-02 is a pre-check that matches the Chromium table (REQ-wr02-fixed)
**What:** one dependency, applied with `dependencies=[Depends(...)]` on `/api/info`, `/api/model.{fmt}` and the three shaft routes that take numbers. It walks `request.query_params.multi_items()`, and for each key that names a number field of that route's model (annotation `int` or `float`; `mate_teeth` on the info route only) refuses a value the number box would blank. A `Request`-only dependency adds no OpenAPI parameter, so `test_the_gear_routes_take_the_v0_6_query_keys` (tests/test_seam.py:152-160) and the gear `/api/schema` bytes are untouched.
**The rule that matches the probe** (4 conditions; derived from the 89-token table below, and checked against it):
```python
def _as_written(token: str) -> bool:
    """True when a Chromium number box blanks this token although pydantic may read it."""
    return token != token.strip() or "_" in token or token.startswith("+") or token.endswith(".")
```
Run against all 89 probed tokens: it refuses every token that Chromium blanks and pydantic accepts, and refuses no token Chromium holds. The one probed token it does not refuse that Chromium blanks and pydantic parses is a 400-digit integer (Blink overflows it to infinity; pydantic reads a big `int`); the field bounds (`le=...`) already answer 422 for it, so it never builds under a blank box. State the pin as an **invariant**, not as rule equality: "no token exists that Chromium blanks and the API answers 200 for". D-02's stop-and-ask is about exactly this disagreement; it is not a rule defect because the API still refuses.
**Response:** `HTTPException(422, detail=[{"loc": ["query", name], "type": "number_as_written", "msg": ...}])`, one entry per offending key (collect all, do not stop at the first). The unchanged `problems()` reads `d.loc[1]` and `d.ctx.fields` (app.js:210-217).
**Suggested wording (D-04):** `"5." is not a number as written; write it as 5 or 5.0` for a float field, `"22." ... write it as 22` for an int field; the unambiguous canonical form is `token.strip().replace("_", "").lstrip("+").rstrip(".")` when that parses as the field's type, otherwise `write it as a plain number, e.g. 22 or 2.5`.

### Pattern 4: `dims` rows travel in the schema (REQ-shaft-web)
`model_config = ConfigDict(frozen=True, json_schema_extra={"dims": [ {"key": ..., "label": ..., "unit": ...}, ... ]})` on `ShaftParams`, an **inline** list, as the gear's `selectors` is [VERIFIED: src/spur/params.py:87 `model_config = ConfigDict(frozen=True, json_schema_extra={"selectors": [_BORE_SHAPE]})`; the comment above it records that a pre-built `list[JsonDict]` variable fails `mypy --strict`]. The rows are the `ShaftDimensions` keys [VERIFIED: src/spur/shaft_calc.py:153-196]: `reference_d, profile_shift, profile_shift_mm, pitch_d, tip_d, root_d, nominal_thickness, form_d, pin_d, measure_over_pins, end_chamfer_effective, designation` (+ `warnings`, rendered by `showMessages`, not as a row). Replace the regex-over-JS test with a Python test: `{r["key"] for r in dims} <= set(ShaftDimensions.model_fields)`, and `set(ShaftDimensions.model_fields) - {r["key"]...} == {"warnings"}` so a new key cannot ship unrendered.
**Render by value type, not by `unit`:** `profile_shift` is a dimensionless NUMBER whose unit is `""` [VERIFIED: shaft_calc.py:155-157 `json_schema_extra={"unit": ""}`], and `designation` is a STRING with no unit. CONTEXT's "`unit: ""` rows rendered as text" would print `0.45` as text without `fmt()`. Rule: `typeof v === 'string'` -> text; number -> `fmt(v)` plus ` ${unit}` when `unit` is non-empty.

### Pattern 5: the CLI group duplicates ~15 lines (REQ-shaft-cli)
```
spur shaft info   [--reference-d V --module V --teeth V --fit V ... | --designation "W 25x1.25x18x8f"]
spur shaft export -o file.{stl,step} [--format] [--quality] [same flags]
```
`sub.add_parser("shaft")` then `.add_subparsers(dest="shaft_cmd", required=True)`; flags generated from `ShaftParams.model_fields` the way `_add_gear_args` does (cli.py:42-56; `type=field.annotation` works for `str`, `int`, `float`); `cmd_shaft_info` prints `derive_shaft(p).model_dump_json(indent=2)`; `cmd_shaft_export` calls `model.export(p, fmt, quality)` lazily and prints `derive_shaft(p).warnings` to stderr. Use a different argument-group header than the gear's: tests/test_cli.py partitions on `"gear parameters (defaults in brackets):\n"` [VERIFIED: tests/test_cli.py `out.partition("gear parameters (defaults in brackets):\n")`]. The CLI must name no `shaft_model` (contract "The kernel doorways are model and shaft_model", pyproject.toml:250) and no `app`/`fastapi`/`starlette` (contract at :193).

### Pattern 6: `app.js` part state without breaking a pin
Keep these generic and shared, change only what the table in Pitfalls says. Sketch of the moving parts: a module-level `part` (`'gear' | 'shaft' | null` for a bad link); `PARTS` as an object keyed by an unquoted-field-free structure (URLs and texts only, never field names); `buildForm(which)` clears `form`, `fields`, `defaults`, `selectors`, `stash`, `rejected` then rebuilds; `renderInfo` picks `schema.dims` when present else the gear `DIMS`; `setDownloads` and `update()` read the info/model URL base from the descriptor; one `followHash()` that decides rebuild-or-not before `readHash()`.

### Anti-Patterns to Avoid
- **A `part` query key on any route.** A gear route ignores unknown keys, so it would build the default gear silently (F1). The page's `part` lives in the hash only and is never sent.
- **`model_fields_set` for the conflict rule** (F2).
- **A second `['key', 'Label']` table in `app.js`** (two pins, F5).
- **Hand-writing the WR-02 rule from the HTML spec.** Chromium holds `1.e1`, `5.e1`, `00022`, `1e-400` that the spec's grammar rejects or that a tidy regex would refuse; the table is the authority (D-02).
- **Hiding the mate box with `.hidden =` / `.style.display`** (guard, Pitfall 4).
- **Rendering `fit` as a number box** (Pitfall 1).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Admission, cache, gzip, error mapping, records for shaft downloads | a second copy of `model()` | `_serve_model(...)` | it is the pinned contract (L04, L12, L19, L37); already extracted |
| Designation grammar | a page-side or route-side parser | `din5480.parse_designation` / `format_designation` | codec is proved (31); refusal text names the bad token already |
| Result-row list for the shaft | a JS table | schema `dims` | pins forbid it |
| Which tokens Chromium blanks | a spec-derived regex | the probed table + the four-condition rule + a live Chromium re-check in the browser test | the spec and Blink disagree |
| 422 envelope | a new error shape | `HTTPException(422, detail=[{"loc":["query", name], "msg":..., "type":...}])` (the `_build_slot` / `model()` pattern, app.py:283-289, 443-444) | `problems()` already reads it |
| Radio keyboard behaviour | arrow-key handlers | native `<input type="radio">` in a `<fieldset>` | the browser supplies the group semantics |
| Download filename | naming in JS | the server's `Content-Disposition` from `slug()` | the page sets none; `Playwright download.suggested_filename` reads it |

**Key insight:** every piece this phase needs already exists once; the failure mode is a second copy (a second row table, a second admission path, a second grammar) that drifts.

## Common Pitfalls

### Pitfall 1: `fit` renders as a number box (not in CONTEXT)
**What goes wrong:** `buildForm()` creates a `<select>` only for `prop.enum`, otherwise `input.type = 'number'` [VERIFIED: src/spur/static/app.js:73-83]. The shaft schema's `fit` is `{"type":"string","pattern":"^[1-9][0-9]?[a-z]$","maxLength":3,"default":"8f",...}` with no `enum` [VERIFIED: `ShaftParams.model_json_schema()` printed this session; `FIT_PATTERN = r"^[1-9][0-9]?[a-z]$"` at src/spur/din5480.py:47]. A number box sanitises `8f` to `''`, `readHash()` would treat the default as rejected, and the form sends nothing for the fit.
**How to avoid:** add a text branch driven by `prop.type === 'string'` (generic, no field name): `input.type = 'text'`, `input.maxLength = prop.maxLength`, `input.pattern = prop.pattern` (the `pattern` attribute is advisory; the server stays the authority, L02), `input.spellcheck = false`. A text box never reads back `''` for a non-empty token, so `refuse()` is inert for it. Keep the `if (prop.enum)` branch byte-identical (L44 says it is unchanged).
**Warning signs:** the shaft page's first `api/shaft/info` request lacks `fit`, or the browser test's field-value check shows `''` for `fit`.

### Pitfall 2: the `app.js` token pins
`tests/test_api.py:265-311` asserts ~45 whitespace-collapsed substrings of `app.js`. Edits to these lines need either to leave the token byte-identical or an amendment logged in the Lxx (the L44 amendments of 2026-10-21/22 are the precedent: "keeps every earlier token ... or logs why").

| Token (verbatim, test_api.py) | Phase 33 consequence |
|---|---|
| `window.addEventListener('hashchange', () => { readHash(); update(); });` (:275) | **must change**: D-14 needs `await buildForm(part)` before `readHash()` on a part change. Replace with one `followHash` call and record the token swap in the Lxx (precedent: L44 amendment D-22 replaced a token with a longer one) |
| `history.replaceState(null, '', hash ? \`#${hash}\` : location.pathname + location.search);` (:273) | keep. For the shaft, `hash` must start `part=shaft`, so compute `hash` from a copy of the query with `part` first; the sent `infoQ` must NOT carry `part` |
| `const infoQ = new URLSearchParams(q);` (:272) | keep; do not add `part` to `q` or `infoQ` |
| `if (rejected.has(name)) { q.set(name, rejected.get(name)); continue; }` (:306), `q.set(name, input.value)` (:271) | keep `gearQuery()` unchanged; it is generic over `fields` |
| `const mate = mateInput.value \|\| rejected.get('mate_teeth') \|\| '';` (:307) | keep; on the shaft, simply do not send `mate` (and do not put it in the hash) |
| the 162-column readHash-end token (:270) | keep byte for byte; part detection happens before `readHash()` |
| `for (const [name, prop] of Object.entries(schema.properties)) {` (:266), `fields.set(name, { input, wrap, title, rels: prop.enabled_when ?? [], reason });` (:267), `buildSelectors(schema.selectors ?? [], groups);` (:287) | keep; shaft has no `selectors`, the `?? []` already covers it |
| `rejected.clear(); mateInput.value = ''; stash.clear(); applyRelations(); deriveSelectors(); update();` (:310) and its shorter twin (:278) | keep Reset as is; it already resets only the current part's `fields` |

Also: `collapsed_source.count("fields.set(") == 1` (:340) and the L42 section guards (exactly one value write in the `-- selectors (L42)` section; none in the `-- relations (L41)` section, :399-424). New `.value =` writes must land outside those two sections.

### Pitfall 3: the quoted-field-name and row-shape guards
`test_the_shareable_link_round_trips_every_field_through_generic_code` forbids, outside `const DIMS = [...]`, any quoted `GearParams` field name and any `.<field>` access [VERIFIED: tests/test_api.py:328-334]. `ShaftParams` shares `teeth` and `module` with the gear, so a descriptor must never quote them. And `test_every_key_the_ui_reads_is_a_derived_dimensions_field` requires that every line shaped `^\s*\['(\w+)',` lies inside the DIMS block [VERIFIED: tests/test_api.py:173-182], so no new array-of-arrays literal may start a line that way (use objects, or put the first element on a different shape of line). Keep `.span_teeth`, `info.centre_distance`, `info.warnings`, `.hex_cell_count` in the source (:184-186).

### Pitfall 4: the "never shut a field" regex forbids the obvious way to hide the mate box
`writes_a_field_shut` matches `.disabled =`, `.hidden =`, `.readOnly =`, `.inert =`, `setAttribute/toggleAttribute('hidden'|'disabled'...)`, `classList.add/toggle('hidden'|...)`, `.innerHTML`, `insertAdjacentHTML`, `.style.display|visibility|pointerEvents|opacity` and asserts `not writes_a_field_shut.search(source)` over the WHOLE of `app.js` [VERIFIED: tests/test_api.py:351-393]. So: set `document.body.dataset.part = 'shaft'` (not matched) and hide with CSS (`[data-part="shaft"] .mate { display: none; }`). The part texts (`<title>`, `.sub`, `aria-label`, `.hint`) go in with `textContent` / `setAttribute('aria-label', ...)`, never `innerHTML` (the bad-`part` message echoes the hash value, so `textContent` is also the XSS control).

### Pitfall 5: the conflict message loses to the model's own 422
See Pattern 2. A test must assert that `designation=W 30x2x14x8f&module=3` answers the conflict sentence naming `designation` and `module`, NOT the profile-shift sentence. Presence of `module=1.25` (the default) is still a conflict (D-07).

### Pitfall 6: stale state across a part switch
`fields`, `defaults` (a `const {}` object, app.js:11), `rejected`, `stash`, `selectors` (a `const []`) and the pending `debounce` timer are module-level [VERIFIED: app.js:10-15, :305-309, :322, :329]. A rebuild must clear them all (`form.replaceChildren()`, `fields.clear()`, delete every key of `defaults`, `selectors.length = 0`, `stash.clear()`, `rejected.clear()`, `clearTimeout(debounce)`), bump the `seq`/`inflight` guard so an in-flight request of the other part cannot land, and guard two rapid toggles with a build-sequence number (the second `fetch` of a schema can finish first). The old mesh stays in the scene across a switch and `fail()` then says `Showing the last valid gear` [VERIFIED: app.js:281]; clear the scene on a switch (or reword to "last valid part") so a gear is never shown under a shaft's 422. No test pins that string (grep: only `app.js:281`).

### Pitfall 7: bad `part` leaves the form live
D-15: gear form shown, nothing built, neither radio checked. Any later field edit calls `scheduleUpdate()` -> `update()`, which would rewrite the hash (dropping `part=bogus`) and build the gear. Decide explicitly (Open Question 3). Recommendation: while `part === null`, `update()` shows the message and returns; the Gear/Shaft switch or a new `hashchange` ends it. The refusal text uses `textContent` and quotes the raw value.

### Pitfall 8: the browser test's recorder and routes are gear-shaped
- `no_foreign_key` allows only `set(properties) | {"quality","mate_teeth"}` as query keys and `set(properties) | {"mate_teeth"}` as hash keys, over EVERY recorded request of every page [VERIFIED: tests/test_browser.py:701-714, :2132]. Shaft pages send `reference_d`, `fit`, ... and a hash with `part`. Use a separate recorder list for shaft pages with the shaft schema's key set, or make `foreign_keys` path-aware; do not append shaft URLs to the gear `seen`.
- `STL_ROUTE = "**/api/model.stl*"` and the `"/api/info" in request.url` waits do not match `/api/shaft/...` [VERIFIED: tests/browser_session.py:39; tests/test_browser.py:241-243]: shaft pages need their own route glob and `expect_request` predicate.
- The test file defines `test_the_shipped_viewer_in_a_real_browser` and `tests/test_browser_pins.py` requires exactly one module to define it and bans `skip`, `skipif`, `importorskip`, `xfail`, `pytestmark`, `getenv` and stray `environ` reads in every `*browser*` module [VERIFIED: tests/test_browser_pins.py:60-80, :242-262].
- `_follow_link` asserts the new fragment differs from the current one; an empty-to-`part=shaft` jump is fine, same-fragment is not.

### Pitfall 9: one parametrised test and xdist
`make test` runs `pytest -n 8` and `test_browser.py` has a module-scoped `server` fixture that starts a uvicorn and a `BuildPool` [VERIFIED: tests/test_browser.py:141-153; Makefile `test:` recipe]. `[ASSUMED]` default `--dist load` can place two functions of one module on different workers, each paying a server start (and the group-floor check in `serve()` teardown). To keep one server: do the web side as a STEP inside `test_the_shipped_viewer_in_a_real_browser` iterating the fixed set (data-driven), with the API and CLI readers in a shared non-browser module and a fast API-vs-CLI parametrised test beside it. Measure before trusting this (Open Question 4).

### Pitfall 10: `shank_length=0` and `fit` do not change the download name
`slug()` is `f"spur_shaft_w{self.reference_d:g}x{self.module:g}x{self.teeth}"` [VERIFIED: src/spur/shaft_params.py:99]. Measured: the default and `shank_length=0` both give `spur_shaft_w25x1.25x18`; a different `fit`, `splined_length`, `end_chamfer`, `shank_d` give the same stem too. So the "same download name" half of the parity test cannot tell several fixed-set shafts apart and its perturbation test must perturb `reference_d`/`module`/`teeth`. The docstring says the slug is "Provisional until Phase 33 owns the download name (L40)" [VERIFIED: shaft_params.py:91-98]: Phase 33 must confirm or change it in the new Lxx (Open Question 2).

### Pitfall 11: Python `strip()` vs the number box
The rule uses `token != token.strip()`; Python strips `\x1c-\x1f` that Rust (pydantic) does not, so such a token is refused with the "not a number as written" sentence instead of pydantic's. Harmless (it was a 422 either way). The probe shows Chromium blanks NBSP, EM SPACE, `\x0b`, `\x0c`, U+2028 around digits, all of which `str.strip()` removes.

### Pitfall 12: `+` in a URL query is a space
`URLSearchParams` and Starlette decode `+` as a space, so `#teeth=+22` reaches the box as `' 22'` and the page sends it back as `teeth=+22` which the server reads as `' 22'`; `%2B22` reads as `+22`. Both are blank-in-box and both start with whitespace or `+`, so the rule covers both. A test token list should include both spellings.

### Pitfall 13: viewer framing
The default shaft spans x,y in -12.5..12.5 and z in 0..50 [VERIFIED: STL of `ShaftParams()` built in-process this session: min `[-12.5 -12.5 0.]`, max `[12.5 12.5 50.]`, 209,484 bytes, 4,188 triangles, 0.74 s]. `placeGrid()` sizes the grid from `max(x extent, y extent) * 1.6 = 40` against a 50 mm shaft [VERIFIED: app.js:561]. It is a visual check (CONTEXT discretion); if the grid looks short, take the largest of the three extents for the shaft only so the gear's grid does not move.

## Code Examples

### Observed Chromium table (D-02, the record `bench/RESULTS.md` needs)
Probe: Playwright 1.63.0, `HeadlessChrome/153.0.8010.12`, a blank page with one `<input type=number step=any>` (and one `step=1`; identical), each token assigned through `.value` and read back. Run 2026-10-27. API column = `pydantic.TypeAdapter(int)` / `TypeAdapter(float)` lax parse of the same string (what FastAPI does for a Query-model number field), then the field's `ge/le` decides.
```
BLANK in the box, parsed by pydantic (these are the WR-02 class; the rule must refuse each):
  ' 22' '22 ' '\t22' '22\n' '22\x0b' '\x0c22' '22\u2028' '\xa0 22' '22\xa0' '\u200322' '22\u2003'   (int and float; written as escapes here, the probe sent the real characters)
  '1_0' '2_2' '1_000'                                                                              (int and float)
  '+5' '+22' '+0'                                                                                  (int and float)
  '22.' '5.' '2.' '0.' '-5.'                                                                       (float only; int refuses by itself)
  '+.5' '+5e1' '+1e1' '1e1_0'                                                                      (float only)
BLANK, pydantic parses, bounds refuse (already 422): 'Infinity' 'inf' '-inf' 'infinity' 'NaN' 'nan' '1e400' '1e309' '-1e309' and a 400-digit integer
BLANK, pydantic refuses (already 422): 'abc' '0x10' '1e' '1e+' '--5' '1,5' '0.5.' '- 5' '1__0' '_1' '1_' '-+5' '+-5' '0b1' '5.e' '.e1' '-.' '1e0.5' '1.5.2' '1 0' '1\xa00' '%' U+0663 U+FF12U+FF12 U+FEFF around digits
HELD (box reads the token back; the rule must NOT refuse):
  '22' '2.5' '-1' '1e1' '.5' '-.5' '1E+1' '1e+1' '1e-1' '00022' '0022' '022' '-0' '5.0' '1.e1' '5.e1' '5e0' '5E0' '1E5' '00.5' '-.5e1' '0e0' '1e-400' '1e308' '0.1e1'
```
Three facts the debt item did not have: Chromium holds leading zeros and `1.e1`/`5.e1` but blanks a trailing `.`; every Unicode space around a number blanks it; `+` is blanked even before `.5`. The earlier 28-01 table (`bench/RESULTS.md` `### Tokens a control cannot hold (28-01)`, Chromium 153.0.8010.12 as well) agrees on the rows it shares. The planner re-runs this probe as plan 1 and records the table under a Phase 33 heading (D-02).

### The two tests that pin it
```python
# Source: recommended shape; not yet written
# 1. pure (commit slice): the rule against the committed table
@pytest.mark.parametrize(("token", "chromium_blank"), TABLE)
def test_no_token_is_blank_in_the_box_and_built_by_the_api(token, chromium_blank): ...
    # for field in (int gear field, float gear field, mate_teeth, int shaft field, float shaft field):
    #   status = client.get(route, params={field: token}).status_code
    #   assert not (chromium_blank and status == 200)
    #   if not chromium_blank: assert status != 422-with-our-type   # a held token is never refused by the rule
# 2. browser (gate): re-probe Chromium for every TABLE token; assert its blank/held answer equals the table
```
This is what turns a Chromium bump from a silent drift into a red test.

### The browser proof "over every number field and mate_teeth"
37 inputs (29 gear numbers + `mate_teeth` + 7 shaft numbers) [VERIFIED: `GearParams.model_fields` has 31 entries of which 29 are `int`/`float`; `ShaftParams` has 8 of which 7; printed this session]. One link per input is enough in the browser (`#<field>=+<its default>`, accepted by pydantic for both int and float, blanked by the box): follow it on a page whose STL route aborts (the golden sweep's technique, `sweep()` reads 0.09-0.15 s per link per its docstring), assert the sent query carries the token, the API answers 422 with `loc ["query", field]`, the box reads `''`, the field is marked `.invalid` (not for `mate_teeth`), no STL request follows and the download href is absent. About 37 links at ~0.15 s is ~6 s; the full token table is walked in the cheap tests above, not per field in the browser.

### Shaft `info` row rendering rule
```js
// Source: recommended; render by value type (profile_shift has unit "" and is a number)
const text = typeof v === 'string' ? v : `${fmt(v)}${unit ? ` ${unit}` : ''}`;
```
A `null` value: follow the gear's `if (v === null || v === undefined) continue;` (app.js:227) so a row is absent rather than implying a number (L08); `form_d` is `null` for every shaft and `measure_over_pins` for an odd tooth count, and `warnings` list why (`ODD_Z_UNCONFIRMED`, `FORM_DIAMETER_UNPROVEN`). Open Question 6 if a dash is preferred.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| WR-02 token "sent and built as the server reads it" (L44 *The server decides*) | token refused at the API with a 422 | this phase (new Lxx amends L44) | gear-side 200 -> 422 for ` 22`, `1_0`, `5.`, `+5`... ; invalid-link class, no fixture token affected |
| gear-only page, static title/hint | part descriptor swaps text; mate box hidden by CSS on the shaft | this phase | gear text stays the static default |
| `slug()` provisional | confirm or change in the Lxx | this phase (L40 handoff) | published download names |

**Deprecated/outdated:** `ACCEPTED_LINK = "face_width=5."` pinned as built (tests/test_browser.py:122, :2087-2095) flips to refused (D-05).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | xdist default `--dist load` can schedule a second function of `test_browser.py` on a different worker, starting a second server | Pitfall 9 | low: if wrong, a separate parity function is fine; if right and ignored, extra server start per worker |
| A2 | A text `<input>` with `pattern`/`maxlength` attributes is acceptable for `fit` (advisory only; the server decides) | Pitfall 1 | low; the alternative is no client hint at all |
| A3 | `+<default>` is a sufficient single per-field token for the browser sweep because the full table is walked elsewhere | Code Examples | medium: the human may want the whole table per field in the browser (cost ~ 37 x 12 links ~ 65 s) |
| A4 | Recommendation that an edit does NOT end a bad-`part` state (switch or new link does) | Pitfall 7 | UX choice; D-15 says only "nothing is built" |
| A5 | The CLI has no download name; "same download name" is satisfied by web == API plus `slug()` on the CLI-built params | Open Question 2 | the human may expect the CLI to name its output |
| A6 | `enabled_when` on `shank_d` (inert at `shank_length` 0) would need an L41-style proof test | Open Question 5 | if added without proof it breaks the L41 rule that a relation is backed by the maths |

## Open Questions

1. **The active `must` debt item that names Phase 33 as its trigger.**
   - What we know: `docs/tech_debt/active/2026-10-27-shaft-volume-guard-accepts-an-uncut-chamfer.md` (Severity: must) says "Revisit when Phase 33 starts (it exposes shaft downloads); fix before that phase ships." CONTEXT.md does not mention it. The fix is in `src/spur/shaft_model.py:136-141` (`_guard_volume`) plus a test in `tests/test_shaft_model.py`, seen red once; it also touches the file that triggers `2026-10-27-shaft-model-two-guard-lines-no-passing-test-reaches.md` (nice).
   - What's unclear: whether the human wants it inside Phase 33 or accepts shipping downloads first.
   - Recommendation: schedule it as the first code task (small, kernel-side, before any download route publishes), retire the item in its own commit, and tell the human (AGENTS.md "stop and ask" on a conflict between a debt trigger and the phase scope).

2. **Download name: who owns it, and what does the CLI do?**
   - What we know: `slug()` leaves the fit and the solid fields out; the default and `shank_length=0` share a name. The CLI writes to `-o <path>` and names nothing. Success criterion 3 says "the same download name".
   - What's unclear: whether "download name" for the CLI means a default output filename, and whether the fit belongs in the name (ARCHITECTURE §4.2 proposed `spur_shaft_W{d_B:g}x{m:g}x{z}_{fit}`; Phase 31 chose to leave it out).
   - Recommendation: keep `slug()` as is (a name, not a cache key, L40), freeze it in the Lxx, and make the parity test compare the web `suggested_filename` and the API `Content-Disposition` byte for byte plus `ShaftParams(**cli_values).slug()` for the CLI. Do not add a CLI default filename. Ask the human to confirm.

3. **Bad-`part` state: what ends it?** (Pitfall 7.) Recommend: the Gear/Shaft switch or a new `hashchange`; an edit and Reset do not build.

4. **Where does the parity test live so the gate pays one server?** Recommend a step inside `test_the_shipped_viewer_in_a_real_browser` plus a fast non-browser API-vs-CLI parametrised test over the same fixed set; measure the gate delta either way (criterion 5).

5. **`enabled_when` on `shank_d` when `shank_length` is 0?** (L48 handed it to this phase.) Cheap to declare (`when("shank_length", "gt", 0)`, params.py:18) but L41 requires a proof that the field truly does nothing there (build two shafts differing only in `shank_d` at `shank_length=0` and compare). Recommend yes if the proof is one small kernel test; otherwise defer and file an idea.

6. **Null row display.** Recommend skip-the-row (the gear's rule, one code path) because the warnings list already explains `form_d` and an odd-count `measure_over_pins`; a dash row is the alternative.

7. **Contention row** (`docs/tech_debt/active/2026-10-27-shaft-contention-row.md`, nice, trigger "Phase 33 adds `/api/shaft/model.{fmt}`"). It is a measurement through the real server (ten concurrent heaviest-shaft requests, as L37 did). Not in the success criteria; recommend a last, optional plan, otherwise re-defer with a reason. Needs the human's call.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 venv | everything | yes | 3.12.15 (`.venv/bin/python`) | none needed |
| GNU make | `make verify` | yes | 4.4.1 | none |
| Chromium headless shell | browser steps, token probe | yes | 153.0.8010.12 in `.venv/ms-playwright/chromium_headless_shell-1243` | `rm -f .venv/.browser && make test` reinstalls (L39) |
| git tag `v0.6` | `make gear.unchanged`, phase close diff | yes | annotated tag (`git cat-file -t v0.6` -> `tag`) | CI fetches it |
| Docker | only `make check` / `make smoke` | yes | 29.8.2 | not needed for `make verify` |
| Node | not needed (vendored bundle) | not probed | — | — |

**Missing dependencies with no fallback:** none.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (+ pytest-xdist 8 workers, pytest-cov floor 96), Playwright 1.63.0 for the browser |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (`--strict-markers --strict-config`, `filterwarnings = ["error", ...]`) |
| Quick run command | `.venv/bin/python -m pytest tests/test_seam.py tests/test_shaft_params.py tests/test_shaft_interfaces.py --no-cov -n0 -q` (light, no kernel) |
| Per-file heavy runs | `make test PYTEST_ARGS="tests/test_api.py tests/test_cli.py --no-cov -n0 -q"`; browser: `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"` |
| Commit slice | `make verify.fast` (must stay under 30 s; new LIGHT test files join it automatically, `test_api.py`, `test_cli.py`, `test_browser.py`, `test_model.py`, `test_pool.py`, `test_shaft_model.py` are excluded by name [VERIFIED: Makefile:228-232]) |
| Full suite command | `make verify` (static prefix incl. `gear.unchanged`, then pytest `-n 8 --cov`) |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-shaft-api | schema/info/stl/step answer; `dims` key present; gear `/api/schema` bytes equal; shaft route table additions only | unit/integration | `pytest tests/test_shaft_interfaces.py tests/test_seam.py tests/test_api.py -k shaft` | no -> Wave 0 |
| REQ-shaft-api | invalid shaft is a 422 naming the field; same admission/cache/errors via `_serve_model` | integration | `pytest tests/test_api.py -k shaft` | no -> Wave 0 |
| REQ-shaft-cli | `spur shaft info/export` numbers equal the API; exit 2 on refusal; README commands run | integration | `pytest tests/test_cli.py -k shaft` | no -> Wave 0 |
| REQ-designation-input | designation alone builds; + spline field = 422 naming both; + solid field fine; bad token named; infeasible designation = 422 not 500 | unit | `pytest tests/test_shaft_interfaces.py -k designation` | no -> Wave 0 |
| REQ-shaft-web | switch both ways, preview drawn, rows from schema, designation row, STL+STEP download, `part=shaft` round trip, gear link has no `part`, bad `part` refused visibly | browser | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"` | partly (add steps) |
| REQ-shaft-web | `app.js` still obeys every pin; no second row table; `fields.set(` count 1; no `.hidden =` | static | `pytest tests/test_api.py -k "shareable or every_key"` | yes (amend one token) |
| REQ-shaft-parity | web = API = CLI for every shaft number and the download name over the fixed set; red once on a perturbed number | browser + integration | browser step + `pytest tests/test_shaft_interfaces.py -k parity` | no -> Wave 0 |
| REQ-wr02-fixed | no token is blank-in-box and 200-at-API (table walk); Chromium re-probe equals the table; per-field browser sweep over 37 inputs; golden sweep still sends the 44 pinned queries; `ACCEPTED_LINK` flipped | unit + browser | `pytest tests/test_shaft_interfaces.py -k as_written`; browser steps | no -> Wave 0 |
| (criterion 5) | gate delta recorded; `make gear.unchanged` green; `git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml` empty | gate | `make verify`; the diff command | n/a |

### Sampling Rate
- **Per task commit:** the quick run command above (kernel-free) plus the touched file.
- **Per wave merge:** `make verify.fast`, and the browser file when `app.js` or `test_browser.py` moved.
- **Phase gate:** `make verify` green, result line recorded in `bench/RESULTS.md` against a baseline taken BEFORE the first code commit (Phase 32 did this at 32-01; Phase 32 close reads `2644 passed in 233.83s`, `real 234.78`), same host, browser test included.

### Wave 0 Gaps
- [ ] `tests/shaft_parity.py` — fixed shaft set (default; `reference_d=30 module=2 teeth=14`; an odd-count shaft such as `26x1.25x19`; `shank_length=0`) and the three readers; M_Re is `None` for `26x1.25x19`, `form_d` is `None` for all [VERIFIED: derive_shaft run this session]
- [ ] `tests/test_shaft_interfaces.py` — light TestClient tests (needs the autouse inline-backend override only if it builds; keep builds in `test_api.py`)
- [ ] a perturbation test: the parity comparison goes red when one displayed number is nudged, recorded under "Seen red once (Phase 33)" in `bench/RESULTS.md`
- [ ] the committed Chromium token table and its two walkers
- [ ] amend `tests/test_api.py` for the hashchange token (Lxx) and add the `dims` Python test
- [ ] amend `tests/test_cli.py` for the `shaft` help partition and README commands

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | the service has none (docs/tech_debt `no-authentication`, nice) |
| V3 Session Management | no | none |
| V4 Access Control | no | none |
| V5 Input Validation | yes | Pydantic bounds on every number; `FIT_PATTERN` + `max_length=3` on `fit`; `DESIGNATION_MAX_LENGTH = 64` caps every designation regex input [VERIFIED: din5480.py:210]; the new "as written" pre-check; a designation that parses is re-validated by `ShaftParams` |
| V6 Cryptography | no | none |

### Known Threat Patterns for this stack
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Reflected content: 422 messages and the bad-`part` message echo user text | Tampering/XSS | the page writes messages with `textContent` only; the `.innerHTML`/`insertAdjacentHTML` ban is a gate guard (tests/test_api.py:351-393); responses are `application/json` |
| Resource exhaustion via expensive builds | DoS | unchanged: `_build_slot` bound, 30 s timeout, `SPUR_MAX_QUEUED_BUILDS`; shaft bounds were swept in 32 (L47 amendment) |
| ReDoS in the designation codec | DoS | inputs capped at 64 characters before any regex; bounded character classes |
| `designation` as a new public query key | Tampering | key is documented, one-way (D-09); unknown keys elsewhere stay ignored |
| Stray `part=` on a gear link used to build the default gear silently | Tampering (L05) | refused visibly on the page (D-15); never a query key |

## Sources

### Primary (HIGH confidence) — read or run this session
- `src/spur/app.py`, `cli.py`, `shaft_params.py`, `shaft_calc.py`, `din5480.py`, `parts.py`, `params.py` (read in full or in the cited ranges)
- `src/spur/static/app.js`, `index.html`, `style.css` (read)
- `tests/test_api.py` (1-480), `test_seam.py`, `test_cli.py` (1-275, 425-470), `test_browser.py` (1-270, 575-1080, 1840-2143), `browser_session.py`, `test_browser_pins.py`
- `docs/architecture/decision_log.md` L44 (2948-3027), L46 (3062-3101), L47 (3103-3223), L48 (3225-3306)
- `docs/tech_debt/active/` WR-02 item, volume-guard item, contention item; `docs/tech_debt/INDEX.md`
- `bench/RESULTS.md` `### Tokens a control cannot hold (28-01)`, `## The shaft solid (Phase 32)` gate baseline/delta/close-checks format
- `.planning/research/ARCHITECTURE.md` §1, §4, §5, §6, §8
- Chromium 153.0.8010.12 number-input probe (89 tokens) and pydantic 2.13.5 `TypeAdapter` parse of the same tokens, run in the repo venv
- FastAPI prototype run in the repo venv: dependency-before-model ordering, designation flow, infeasible mapping, OpenAPI key list

### Secondary (MEDIUM confidence)
- none beyond the above

### Tertiary (LOW confidence)
- xdist scheduling behaviour (A1), UX recommendations on a bad `part` (A4)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependency, all pins read from the repo
- Architecture: HIGH for the server side (prototyped), MEDIUM for `app.js` (design under 45 pins, not built)
- Pitfalls: HIGH — each traced to a file and line this session; Pitfall 9 is `[ASSUMED]`

**Research date:** 2026-10-27
**Valid until:** 2026-11-26 (the Chromium table is tied to Playwright 1.63.0; re-probe if the pin moves)
