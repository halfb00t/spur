# Feature Research

**Domain:** a debt sweep on an existing parametric spur-gear generator (schema-driven web form, URL-hash state, FastAPI, CLI), milestone v0.6 Clean Ledger
**Researched:** 2026-10-15
**Confidence:** HIGH for what the code does today (read and measured in a real browser); MEDIUM for "what other URL-state libraries do" (web search snippets, not cached through the research-store seam); LOW only where a row says UNVERIFIED.

Evidence tags used below: **MEASURED** = I ran it on 2026-10-15 (real uvicorn + Chrome Headless Shell from `.venv/ms-playwright`, script in the session scratchpad, not committed). **READ** = read in the file cited. **UNVERIFIED** = inferred, not run.

"Feature" here means "behaviour of a fix". No new product capability is in scope. The one filter on everything: anything that would move a valid link's part, or change what a valid link sends, is an anti-feature (L05; the 44-record fixture and `tests/regression/golden_requests.json` stay byte-identical).

---

## Part A. The bogus-enum link, and how general it really is

### A.1 What other URL-state apps do (convention)

Three families, all seen in mainstream tooling [MEDIUM, web search, not cached]:

| Family | Example | Behaviour on an out-of-domain value | Fit for spur |
|---|---|---|---|
| Coerce to default | nuqs parsers: a value that is not valid state makes the parser return `null`, so the app shows its default; Zod `.catch()` in TanStack Router | silent fallback | Rejected by the human's pick. It is exactly today's bug (L03/L08: never guess). |
| Refuse as an error state | TanStack Router `validateSearch` that throws: the route goes to its `errorComponent` | whole view replaced by an error | Heavier than needed; spur already has a per-field error surface. |
| Keep the value, flag it | react-jsonschema-form: formData keeps the value, ajv reports "must be equal to one of the allowed values" against the field | field stays marked, nothing is built or submitted until fixed | This is spur's existing 422 path. Use it. |

Sources: [TanStack Router, validate search params](https://tanstack.com/router/latest/docs/framework/react/how-to/validate-search-params), [nuqs parsers](https://nuqs.dev/docs/parsers), [rjsf validation](https://react-jsonschema-form.readthedocs.io/en/v4.2.2/usage/validation/).

Convention in one line: a library that silently coerces is making the choice spur's L03/L08 forbid; the "keep it and mark it, let the validator speak" family is the one that matches a server that already owns validation (L02).

### A.2 What spur does today (MEASURED, 2026-10-15)

Page loaded at `/#<link>`, 2.5 s settle; "sent" is the `/api/*` requests the page made.

| Link | Sent by the page | Hash after | Marked / error shown | Verdict |
|---|---|---|---|---|
| `root_shape=bogus&teeth=22` | `info?teeth=22`, `model.stl?teeth=22&quality=preview` | `#teeth=22` | none, none | silent drop (the debt item); select `""` at index -1 |
| `recess_sides=bogus&teeth=22` | same | `#teeth=22` | none | same defect, second enum field |
| `root_shape=&teeth=22` (blank) | same | `#teeth=22` | none | blank select, default part |
| `teeth=abc` | `info?` (nothing), `model.stl?quality=preview` | `` (empty) | none | **same defect on a number box**: default 19-tooth part built from a link that said `teeth=abc` |
| `mate_teeth=abc&teeth=22` | `info?teeth=22` | `#teeth=22` | none | same defect on the mate box |
| `foo=1&teeth=22` | `info?teeth=22` | `#teeth=22` | none | unknown key dropped; API also ignores unknown keys (200), so not a defect |
| `teeth=22.5` | `info?teeth=22.5` | kept | `Teeth` marked; "Teeth: Input should be a valid integer, unable to parse string as an integer" | **already refused through the 422 path** |
| `teeth=-5` | `info?teeth=-5` | kept | `Teeth` marked; "Teeth: Input should be greater than or equal to 6" | already refused |
| `teeth=1e1` | `info?teeth=1e1` | kept | `Teeth` marked; int parse message | already refused |

API side (TestClient, MEASURED): `root_shape=bogus`, `recess_sides=bogus`, `root_shape=` and `root_shape=Trochoid` are 422 `literal_error` with `loc: ["query", "<field>"]`; `teeth=abc`, `teeth=` and `mate_teeth=abc` are 422 `int_parsing`; `foo=1` is 200; `root_shape=trochoid&root_shape=radial` is 200 (page resolves repeats first-wins, READ `URLSearchParams.get`, `tests/browser_session.py` `_given`).

### A.3 Why it drops (READ)

- `readHash()` (`src/spur/static/app.js:105-111`) does `input.value = h.get(name) ?? defaults[name]`. A `<select>` assigned a value with no matching option reads `''` / `selectedIndex -1`. An `<input type=number>` assigned text that is not a valid floating-point number is sanitised to `''` by the browser (MEASURED: `teeth` reads `''` after `#teeth=abc`).
- `gearQuery()` (`app.js:114-120`) skips `input.value === ''`, and `update()` rewrites the hash from that query (`app.js:247-248`), so the evidence also leaves the address bar.
- Numbers that parse but are out of range or the wrong integer-ness are never sanitised, so they already travel to the API and hit the 422 path. The gap is exactly the set of values a control **cannot hold**: an enum string with no option, and non-numeric text in a number box.

### A.4 What the 422 marking path does (READ, MEASURED)

`update()` clears `.invalid` on every field, hides downloads, aborts the previous request, fetches `api/info?...`. On a non-ok answer, `problems()` (`app.js:187-202`) takes the body's `detail[]`; for each item it adds `.invalid` to `fields.get(d.loc[1])` and to every name in `d.ctx.fields`, and returns `"<Field title>: <msg>"` (the `Value error, ` prefix removed). `fail()` (`app.js:258-263`) puts those in `#messages`, empties `#dims`, and sets the status to "Showing the last valid gear" only if a mesh already exists. The STL request is never made (info is fetched first and returns early). Downloads stay disabled. CSS: `.field.invalid input, .field.invalid select` gets the accent border and outline (`style.css:112`).

It is **field-agnostic**: it keys on `loc[1]` and `ctx.fields`, so it works for any `GearParams` field, enum or number, with no per-field code. It is exercised today for `bore_flat=3` (via `ctx.fields`), `teeth=2` (via `loc[1]`), and the hex+keyway pair (`tests/test_browser.py:764-799`, `:1099-1134`). `mate_teeth` is not a form field, so its 422 shows the message text but marks nothing (`fields.get('mate_teeth')` is undefined; READ).

Two enum fields exist (`root_shape`, `recess_sides`; READ `src/spur/params.py:115,168`) and neither is an `enabled_when` gate (READ, grep `when(` in params.py), so keeping a bad enum value interacts with no relation or selector logic.

### A.5 Is the fix general or root_shape-only? General.

The defect is one mechanism: **the page loses a link value its control cannot represent, before the request is built**. It affects both enums (MEASURED) and any non-numeric text in a number box including `mate_teeth` (MEASURED). A root_shape-only fix would leave `recess_sides=bogus` and `teeth=abc` building the default part silently, which is the same L03/L08 violation. The 422 path needs no change; the fix lives entirely in how `readHash`/`gearQuery` carry an unrepresentable value to the API so the server's own message and `loc` do the marking.

Recommended mechanism (one for all field types, smallest change): in `readHash`, after assigning, if the raw token is non-empty and the control cannot hold it (`select.selectedIndex === -1`, or number `input.value === ''`), remember it in a `rejected` map (name to raw string). `gearQuery` sends `rejected.get(name)` for that field. The map entry is cleared when the user edits that field, on Reset, and at the next `readHash`. Consequences, all following from existing code: the hash keeps the raw token (the address bar stays truthful and Copy link copies the bad link); the API's text appears unchanged ("Root shape: Input should be 'radial' or 'trochoid'"); the field is outlined; nothing builds; an unrelated edit does not silently drop the bad value because the map persists until that field is touched. For a select, showing the stray value as a temporary, removable option is a nicer variant of the same idea; for a number box nothing can show it (browser sanitisation), so the shared map is the common denominator. Complexity: Low (select) to Low-Medium (shared map plus the clear rules).

### A.6 Feature categories for the bogus-link fix

**Table stakes**

| Behaviour | Why | Complexity | Notes |
|---|---|---|---|
| A non-empty enum token with no matching option is sent to the API unchanged and refused through `problems()` (field marked, server text shown, no STL request, downloads disabled) | The human's pick; L03/L08; matches API and CLI (argparse choices) | Low | Same path as `teeth=2`; text comes from the server, no new client wording (L02) |
| The fragment keeps the offending token after the refusal | The evidence of what was asked must stay in the address bar; today it is rewritten away | Low | Falls out of sending the value: `update()` builds the hash from the same query |
| Same treatment for `recess_sides` | Second enum field, identical mechanism | Low | Free once the mechanism is shared |
| Same treatment for non-numeric text in number boxes (`teeth=abc`, `mate_teeth=abc`) | Same defect class measured today; otherwise a link meaning "teeth=abc" builds the 19-tooth default | Low-Medium | Needs the shared map because `type=number` cannot hold the text. This extends the human's enum-only pick: surface at discuss-phase as a scope confirmation, my recommendation is yes |
| Valid links unchanged: every one of the 44 fixture requests and every valid enum/number token sends exactly what it sent | L05, L26 | Low | Proved by `golden_requests.json` and `pre_v0_2.json` staying byte-identical; fixture's only string params are the valid `recess_sides` values `none` and `top` (MEASURED) |
| Recovery: choosing a real option or typing a number in the refused field clears the refusal and builds | A refusal with no exit is a trap | Low | Clear the map entry on that field's `input` event; Reset and a new hash navigation also clear it |
| The `root_shape=bogus as today` pin (`tests/test_browser.py:1754-1808`, `BOGUS_LINK`/`TODAY` at `:97-103`) flips in the same commit; add steps for `recess_sides`, a non-numeric number, recovery, and "valid link leaves nothing marked" | CLAUDE.md: a pin is changed by the commit that fixes the debt | Medium | The step's own oracle already uses `_api_get` + `_expected_422`; reuse them. The debt file moves to `resolved/` in the same commit |
| A new decision `L44` (L43 is the last) recording the shape | Debt file and PROJECT.md both require it | Low | Names: what is refused, what stays default (blank), where the text comes from |

**Differentiators (optional, low priority)**

| Behaviour | Value | Complexity | Notes |
|---|---|---|---|
| Show the rejected value in the select as a temporary option (`bogus`) | The user sees what the link said | Low | Select only; must be removed on next input. Not needed for the contract |
| Add the rejected input to the message ("got 'bogus'") from `detail[].input` | Clearer than the server's bare "Input should be ..." | Low-Medium | Changes the text `tests/test_browser.py::_expected_422` compares for equality; do only if the oracle changes with it |
| Mark the mate box invalid on a `mate_teeth` 422 | `mate_teeth` errors currently mark nothing | Low | Pre-existing, orthogonal; file as an idea rather than widen this fix |

**Anti-features (do not build)**

| Anti-feature | Why requested | Why problematic | Alternative |
|---|---|---|---|
| Client-side validation or a client-written error string for an unknown option | Looks like the fast fix | Duplicates the domain (the form is generated from `/api/schema`, L02); second wording to keep in sync with the API | Send it and let the 422 speak |
| Refusing a blank value (`root_shape=`, `teeth=`) | API answers 422 for blank | The page defines blank as the default everywhere (`effective()` `app.js:126-129`; test oracle `_given` blank-to-default, `IN-06` of Phase 23). The page never emits blanks, but a hand-edited link with one currently works. Refusing is a behaviour change for a link that today builds the default intentionally | Keep blank = default; state it in L44 |
| Switching number inputs to `type=text` so garbage can be held | Would let the box show `abc` | Loses spinners/min/max/inputmode behaviour for every valid user | Shared `rejected` map |
| Refusing unknown keys (`foo=1`) | Tidy | The API ignores them (200, MEASURED); links from older/newer versions would break | Keep ignoring; same as API |
| Falling back to default plus a warning banner | Gentler | It is the coerce-to-default family: it builds a part the user did not ask for (L03/L08) | Refuse |
| Reworking duplicate-key handling (first-wins vs API last-wins) | Parity | Not an invalid-link problem; the page sends its own single value | Out of scope |

---

## Part B. Open review info findings: complete inventory

Scope as stated: Phases 19 and 21-24. Every `open` or `deferred` info row in the REVIEW-DISPOSITION files, re-read against the tree at HEAD (`3726242`). IDs are as the review files use them. Class: **FIX** (do now, cheap, no part moves), **FILE** (becomes a `docs/ideas` or `docs/tech_debt` item with a trigger), **CLOSE** (closed with a written reason). "Co-fix" = same file/function as a milestone item, so it rides that commit.

Counts: 19 rows in scope (19: 4, 21: 4, 22: 3, 23: 2, 24: 6). 1 is already resolved (19 IN-03), 1 already filed (24 IN-04), 1 is a duplicate (24 CX-03 = IN-02), leaving 16 distinct findings to act on.

| ID | File:line (READ at HEAD) | One line | State | Class | Cost |
|---|---|---|---|---|---|
| 19 IN-01 | `src/spur/model.py:625-636` (`_chamfer_tips` calls `tip_chamfer_effective(p)` with no `rm`), comment at `:770` | `_build` says root_mode is asked once; `_chamfer_tips` re-solves it. Pure, cannot diverge today | live | FIX: pass `rm` through (`calc.tip_chamfer_effective(p, rm)` already takes it, `calc.py:371`), or soften the comment. Fixture and trochoid builds must stay byte-identical | Low |
| 19 IN-02 | `bench/trochoid_part.py:111-117` | stale "does not exist until 19-04" paragraph; re-solves with `trochoid_root(rm.cutter)` though `RootMode.curve` exists (`calc.py:1668`); `:1355` same | live | FIX (read `rm.curve`, delete the paragraph) | Low |
| 19 IN-02b | `bench/trochoid_part.py:172-210` vs `tests/test_model.py:68,86` | near-copies of `_root_edges`/`_oracle_reading` | live | CLOSE with reason: bench is outside the gate and importing `tests` from `bench` adds a dependency the contracts do not describe (18 IN-04 already notes this); revisit only if the slug-totality test wants a shared helper | none |
| 19 IN-03 | `Makefile` gate-cost comments | quoted the 63.555 s gate | **resolved** by 34270c8; the Makefile now cites L43 and 300 s (`Makefile:110-111,180`) | CLOSE (stale line in the debt file's Context; the file is retired when IN-01/02/04 land) | none |
| 19 IN-04a | `src/spur/static/app.js:23` | `['root_fillet', 'Root fillet used']` while a hob root is in force, where the value is the hob's tip radius | live | FIX as a label function of the document (same shape as the `span` and `hex_cell` rows, `app.js:17,39`). **Text-only change visible on valid trochoid links; no part, number or request moves.** Surface to the human: it is a second user-visible change beside the bogus link, and PROJECT.md's rule allows it (only parts/requests are frozen) | Low |
| 19 IN-04b | `bench/trochoid_part.py:329-334` | `_host_state` `check=True` on `git rev-parse` crashes outside a git checkout | live | FIX (print "unknown") | Low |
| 21 IN-01 | `tests/browser_session.py:117-118,130-133` | dead `survivors =` and `bound =` assignments; failure message names only the SIGKILL bound | live | FIX, co-fix with `stop_group` (must item) | Low |
| 21 IN-02 | `tests/browser_session.py:668-677` (`fixture_hash`) | `str(value)` would mis-encode a bool/null | live, latent (fixture holds only int/float/str, MEASURED) | FIX (one `isinstance` assert) since the file is already open | Low |
| 21 IN-03 | `tests/test_browser_pins.py:96-101` | the "no path that passes without the browser" scan is line- and spelling-based | live | CLOSE with reason (it is a tripwire, not a proof) plus soften its docstring | Low |
| 21 IN-04a | `tests/test_browser.py:204-215` (`_follow_link`) | waits at Playwright's 30 s default while other waits use `BUILD_WAIT_MS` (45 s) | live | FIX (pass `timeout=BUILD_WAIT_MS`); relevant to starved-runner flake reading and the Ubuntu 26 first run | Low |
| 21 IN-04b | `tests/test_browser.py:584-593` (`_wait_until_parked`) | `page.evaluate("0")` loop with no pause | live | CLOSE with reason: the comment at `:585-587` explains the round trip is what lets the route handler run; no measured cost. Reopen only if CPU burn is measured | none |
| 22 IN-01 | `tests/test_api.py:926,1293`, `tests/test_trochoid.py:88,208` | bore-off block duplicated | live | CLOSE (review: low value either way). If the slug-totality test adds a third copy, share `_BORE_OFF` instead | none/Low |
| 22 IN-02 | `tests/browser_session.py` `serve_stl_from` docstring | ragged reflow ("must be served and not the" / "request aborted") | live | FIX (re-wrap), co-fix in `browser_session.py` | Low |
| 22 IN-03 | `docs/architecture/decision_log.md:2573` | L40 quotes 1.13 s; the bench reads 1.13 to 3.56 s | live | FIX by a dated correction under the entry (the log's own convention: append, do not rewrite readings; same rule as the group-floor item) | Low |
| 23 IN-08 | `tests/test_relations.py:253-262,289` | `CUTOUT_STATES` gives the honeycomb gate only `hex_cell` 0.05, so `eq 0.05` is indistinguishable from `gt 0` except through an incidental `ValidationError` | live | FIX: add `"honeycomb (4)": {"hex_cell": 4, "hex_wall": 1}`, raise the cell count assertion, add the meta-test row, reword the docstring "each gate". Backs an L08 claim (a dimmed field must be one `calc` ignores) | Low-Medium |
| 23 IN-11 | `tests/browser_session.py:325-333` (`_js_number`) | silent mismatch with JS for `-0.0`, below 1e-6, at or above 1e21 | live, latent (thresholds are 0, 0.05, 1) | FIX (range assert, `+ 0` for -0), co-fix in `browser_session.py` | Low |
| 24 IN-01 | `src/spur/static/app.js:292-300,401` | stash can restore an older/default string or one from another link; comment says "the user's own string" | live | FIX the **comment only**. The behavioural fix (delete the stash entry on hand edit) changes what a pick writes and was accepted knowingly (D-19); FILE it as an idea, not a fix here | Low |
| 24 IN-02 = CX-03 | `src/spur/static/app.js:637-643` | selector build error is reported as "Could not load the parameter schema" and leaves a blank form | live; no test pins the string (MEASURED by grep) | FIX the wording ("Could not build the form: ..."). CLOSE Codex's larger proposal (isolate bad selectors and continue): speculative flexibility for a schema this repo serves itself; `tests/test_selector.py` and `test_schema_drives_the_form` catch a malformed entry before it ships | Low |
| 24 IN-03 | `tests/test_api.py:143` | `"selectors" not in client.get("/openapi.json").text` is a substring test; a description word turns the gate red | live | FIX (parse the JSON, walk for a key named `selectors`); same class as the hook-pin item (a gate red for no code reason) | Low |
| 24 IN-04 | (calc hex warning wording) | field names vs form titles | default-values half resolved by #37; title half filed as `docs/ideas/2026-10-14-hex-warning-names-fields-by-form-title.md` | CLOSE (already filed; cite the path in the disposition) | none |
| 24 CX-05 | `tests/test_browser.py:1580-1595` (`requests_before` ... `len(seen) == requests_before`) | zero-request assertion can pass before the 350 ms debounce fires | live | FIX (observe past the debounce before asserting); otherwise the assertion can pass vacuously | Low |

### Open info findings outside the stated scope (surfaced, not triaged)

The requirements step should decide whether these are in or out; the milestone text names only 19 and 21-24, but the dispositions still say `open`:

- **Phase 18, IN-01 to IN-08** (`v0.4-phases/18-*/18-REVIEW.md`, all `open`; the v0.4 close in MILESTONES.md named them as a candidate and the v0.5 close dropped the mention). One-liners: IN-01 cap sentence says "the largest" for a floored 3-dp value (`calc.py:961` region); IN-02 mode and curve not carried together (**largely overtaken**: `RootMode.curve` now exists, `calc.py:1668`); IN-03 epsilon bench cannot fail on the shipped constant (`bench/trochoid.py:54,216`); IN-04 bench hygiene (`sys.path.insert` per call, bare `ValueError` on `--stride 0`); IN-05 `ROOT_CURVE_POINTS` evidence not regenerable (`calc.py:66-72`); IN-06 flake trigger rolled forward on non-discriminating evidence (**superseded** by this milestone's flake work); IN-07 `root_mode` docstring does not state it can raise `ValueError` (`calc.py:1415`); IN-08 the `-0.0` row cannot tell signs apart. Liveness: IN-02, IN-06 overtaken; the rest not re-run [UNVERIFIED beyond the grep hits above]. Recommendation: close IN-02/IN-06 with reasons, FIX IN-07's docstring line, FILE the rest as one nice debt item with the trigger "`bench/trochoid.py` or `calc.cutter` next touched". Because several touch `calc.py` (a printed-number path), none should ride this sweep unless trivially documentary.
- **Phase 10, IN-01 and IN-02** (`v0.2-phases/10-*/10-REVIEW-DISPOSITION.md`, `open`): `bench/tip_chamfer_spike.py:201,286` hard-codes the `le=3` bound; `calc.py:1294` gates `tip_chamfer_effective` on the raw request (`p.tip_chamfer > 0`) rather than the applied value. Both live (READ). IN-02 is an L08 question about `0.0` vs `null` and would change a printed value: **not for this milestone**; FILE as `must`-candidate decision, do not fix in a debt sweep. IN-01 is bench-only: FILE or CLOSE.
- Every other `REVIEW-DISPOSITION.md` under `.planning/milestones/` (Phases 11-17, 25) has zero `open` rows (MEASURED by script).

---

## Part C. The other milestone items: expected behaviour of each fix

| Item | Expected behaviour when done | Evidence-based design notes | Complexity |
|---|---|---|---|
| `slug()` totality (must, `2026-10-15-slug-totality-is-not-guarded-in-the-gate.md`) | A seeded test drives `slug()` over a few hundred validated `root_shape="trochoid"` requests **including a case per `root_mode` refusal reason** (`bracket degenerate`, `curve invalid`, `tooth severed` are never reached today, READ debt file) and asserts `slug().endswith("_trochoid") == (root_mode(...).mode == "trochoid")` with no exception | In the commit slice (milliseconds). Reuse a slice of `bench.trochoid.sweep_cases()` if it reaches every reason; assert reason coverage inside the test so it cannot silently stop reaching one | Low-Medium |
| Failed-build name test (must) | Passes regardless of test order and xdist scheduling | Make the key private: `face_width=7.7` in both rows (no other test uses it) or `_EXPORTS.clear()` at the top. Prefer the private key: `_EXPORTS` is module state shared with the rest of `test_api.py` | Low |
| `stop_group` (must) | Sends SIGTERM, then SIGKILL after the bound, whether or not `ps` works; a failed `ps` is reported as "survivors unknown", never as a `CalledProcessError` that skipped the kill; the leader-only red from `bench/RESULTS.md` 21-01 still fires | Rides with 21 IN-01 (dead assignments). Fall back to a final unconditional `killpg(SIGKILL)` in `serve`'s `finally` | Low |
| Group-floor comment (must) | Comment and the two `bench/RESULTS.md` rows name the observed members (uvicorn, `multiprocessing.resource_tracker`, one spawned worker); dated corrections under the rows, readings not rewritten | List the group with `ps -o pid=,pgid=,command=` once per host first (the debt file flags this as ASSUMPTION). Decide whether the floor names the tracker or a second build is forced | Low |
| Flake: `resource_tracker` (must) | Whole-suite `make test` loops at `-n 8 --cov` and `-n 8 --no-cov` run now; outcome is a fix **from a captured reproduction** or a re-deferral carrying the loop counts | Four prior occurrences all came from whole-suite runs; two-file loops 0 of 60 (READ debt file). Rate is about 1 in 12 to 43 per gate (READ); to say "0 occurrences" with any confidence the loop count must be stated against that rate, not just "green". L08: never closed on a guess | Medium (mostly wall time) |
| 98 % hang (must) | No fix. The gate leaves evidence on the next hang: per-test ids and durations (`-v --durations=20`) kept in a log, plus a process-tree/stack snapshot at a watchdog limit before the harness kills it | The hang happened after about 1200 of 1220 reports, in the worker-exit / `BuildPool` shutdown / pytest-cov flush window (READ). pytest's `faulthandler_timeout` is per-test and so does not cover that window, and its output under xdist workers is UNVERIFIED; capture needs a session-level watchdog or an external stack dump. Choose the mechanism in discuss/plan with the gate's 300 s bar (L43) and the output volume in mind | Medium |
| Browser harness comment | Comment says what `ps` observes | Same commit family as the group-floor item | Low |
| Ubuntu 26 CI (must, date-gated) | Nothing changes before the first CI run whose `Set up job` names Ubuntu 26; that run is classified from its whole log (apt, WebGL, timeout) before any fix; green means a dated `bench/RESULTS.md` reading and the item resolves; red may pin `runs-on: ubuntu-24.04` only on the human's decision | Migration begins 2026-10-19 and completes by 2026-11-19 [MEDIUM, [runner-images#14748](https://github.com/actions/runner-images/issues/14748), fetched]. Notable: `setup-python` cannot install old patch versions on 26.04 (spur's CI passes `${{ matrix.python }}`; whether that is a minor pin is READ-able, not checked here), kernel 7.0, systemd 259.5. Playwright 1.63 names `ubuntu26.04` platforms (READ debt file). Today is 2026-10-15, so the phase is blocked on the clock and must be last or independently schedulable | Low to run, unknown if red |
| Hook pin reads `PYTEST_ARGS` (nice) | `make verify PYTEST_ARGS="--ignore=..."` no longer fails `test_verify_and_verify_fast_share_...` | Drop `PYTEST_ARGS` from `_make_env()` or pass `PYTEST_ARGS=` on the dry run; add a case with the variable set | Low |
| Launch-failure message (nice) | Message prints Playwright's own error first, then accurate advice (`rm .venv/.browser && make test`; Linux libraries via `--with-deps`) | Co-fix with 21 WR-03 wording; no test pins the old text (READ debt file) | Low |
| `make test-image` (nice) | Image suite no longer collects tests that read host-only files | Exclude by name as 21-06 did for `tests/test_browser.py`; Docker was not running when filed, so first step is to run it for real [ASSUMPTION in the debt file] | Low-Medium |

---

## Feature Dependencies

```
bogus-link fix (app.js readHash/gearQuery)
    ├──requires──> existing 422 path problems()/fail() (unchanged)
    ├──requires──> browser-test step flip (same commit) ──requires──> golden_requests.json unchanged (proof valid links unmoved)
    ├──guarded by─> tests/test_api.py app.js scans (write() statement count, "never disables/hides/clears a field" guard, DIMS-key and ['word', harvests)
    └──records───> new L44 + debt file moved to resolved/ (same commit)

app.js label (19 IN-04a) ──same file as──> bogus fix        (separate commit: one concern per commit)
app.js wording (24 IN-02) ──same file as──> bogus fix       (separate commit)

stop_group fix ──co-fix──> 21 IN-01, 21 IN-02, 22 IN-02, 23 IN-11   (all tests/browser_session.py)
group-floor comment ──after──> one live `ps` listing
slug totality test ──may share──> _BORE_OFF (22 IN-01)
failed-build name test ──independent of──> slug totality test (different file regions, same test_api.py)
test_browser.py edits: bogus pin flip + 21 IN-04a + 24 CX-05    (batch; one run of the 165-300 s gate)
flake loops ──precede──> 98 % hang evidence capture ──both touch──> Makefile `test` recipe / pytest invocation
Ubuntu 26 classification ──blocked until──> 2026-10-19 CI run
```

### Dependency notes

- The `app.js` fix is guarded by `tests/test_api.py` scans of `app.js` source (READ comments at `app.js:131-133,395-396`): the number of `write(` field writes in the selectors section, the no-disable/hide/clear guard, and harvests of `['word',` rows and `DIMS` keys. A `rejected` map that never disables, hides or clears a field is consistent with L41's rule; the exact regexes were not read, so run `tests/test_api.py` early. [UNVERIFIED]
- `tests/browser_session.py` is edited by four findings plus `stop_group`; do them as one concern ("browser harness teardown and helper hygiene") so the gate runs once.
- Everything that edits `tests/test_browser.py` reruns the browser step list inside `make verify`; batch them.

## MVP Definition (for the requirements step)

### Launch with (the milestone's table stakes)

- [ ] Bogus-enum refusal via the 422 path, general to both enums and non-numeric number text, blank = default, fragment keeps the token, pin flipped, `L44` logged, debt file retired in the same commit
- [ ] The two Phase 22 `must` tests (slug totality across all refusal reasons; failed-build name test order-independent)
- [ ] `stop_group` signals before it reads; group-floor comment and dated RESULTS corrections
- [ ] Flake loops run and outcome recorded (fix from a reproduction, or re-deferral with the loop counts); hang evidence capture
- [ ] Ubuntu 26 classified from the whole log, once the run exists
- [ ] Info findings: the 15 FIX rows plus 6 CLOSE-with-reason rows (and one FILE: the stash-invalidation idea) of Part B, each disposition written into the `*-REVIEW-DISPOSITION.md`
- [ ] The three nice items

### Add after (only if the human widens scope)

- [ ] Temporary-option display of the rejected value; "got '...'" in the message (changes `_expected_422`)
- [ ] Marking the mate box on its 422
- [ ] Stash invalidation on hand edit (24 IN-01 behaviour)
- [ ] Phase 18 and Phase 10 info findings (Part B tail)

### Defer

- [ ] Phase 10 IN-02 (`tip_chamfer_effective` null-gate): changes a printed value, not a sweep item
- [ ] Hex-warning titles (already an idea)

## Prioritisation

| Item | User value | Cost | Priority |
|---|---|---|---|
| Bogus link refusal (general) | HIGH (the only user-visible correctness fix) | LOW-MED | P1 |
| slug totality + failed-build name tests | MEDIUM (a 500 hides the real cause; order-dependent red) | LOW | P1 |
| stop_group + group-floor + harness co-fixes | MEDIUM | LOW | P1 |
| Flake loops + hang evidence | HIGH for the gate | MED | P1 |
| Ubuntu 26 classification | HIGH if it breaks CI | LOW-unknown | P1, date-gated |
| Info FIX rows | LOW each | LOW | P2 |
| Nice items | LOW | LOW | P2 |
| Label fix 19 IN-04a | LOW-MEDIUM (L08 honesty of a label) | LOW | P2, needs human OK as a second visible change |
| Differentiators in A.6 | LOW | LOW-MED | P3 |

## Sources

- Local reads (HIGH): `src/spur/static/app.js`, `src/spur/static/index.html`, `src/spur/static/style.css`, `src/spur/params.py`, `tests/test_browser.py`, `tests/browser_session.py`, `tests/test_relations.py`, `docs/tech_debt/INDEX.md` and `active/*.md`, `docs/architecture/decision_log.md` (L02, L03, L05, L08, L39-L43), all `.planning/milestones/*/*-REVIEW*.md` and `*-REVIEW-DISPOSITION.md`, `.planning/milestones/v0.5-MILESTONE-AUDIT.md` (its line 126 lists the same untriaged set).
- Measured (HIGH): the browser and API probe tables in A.2 (2026-10-15, script in the session scratchpad, not committed).
- [TanStack Router: validate search params](https://tanstack.com/router/latest/docs/framework/react/how-to/validate-search-params) (MEDIUM, search snippet)
- [nuqs parsers](https://nuqs.dev/docs/parsers) (MEDIUM, search snippet; `parseAsStringEnum`'s exact invalid-value result was not shown, only the general "return null when invalid" contract)
- [react-jsonschema-form validation](https://react-jsonschema-form.readthedocs.io/en/v4.2.2/usage/validation/) (MEDIUM, search snippet)
- [actions/runner-images#14748](https://github.com/actions/runner-images/issues/14748) (MEDIUM, fetched summary: migration 2026-10-19 to 2026-11-19)

Not done: the `research-plan` / `research-store` / `classify-confidence` seam was not invoked; the external findings above are tagged MEDIUM by hand and were not cached.

---
*Feature research for: spur v0.6 Clean Ledger (debt sweep)*
*Researched: 2026-10-15*
