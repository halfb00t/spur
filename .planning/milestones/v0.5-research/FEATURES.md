# Feature Research

**Domain:** schema-driven web form + three.js viewer for a parametric CAD generator, milestone v0.5 "Honest Form" (browser test, conditional fields, bore-shape selector, download name)
**Researched:** 2026-10-10
**Confidence:** MEDIUM-HIGH overall. Claims about this repo are HIGH (read in source or reproduced by running `GearParams`/`derive()` and a browser spike on this host). UX conventions are MEDIUM (vendor docs and accessibility write-ups, read 2026-10-10). Headless WebGL on Linux/CI/Docker is LOW: it was only run on macOS arm64.

Scope: only the four NEW features. Involute geometry, bores, cutouts, shareable links, the cap-and-warn/422 contract and the rest are not re-researched; they appear as dependencies. Every claim is tagged **[repo]** (read or run here), **[src]** (a cited convention) or **[judgement]** (this researcher's call; challenge it at discuss-phase).

## Findings the roadmap must know first

1. **hex x keyway is a 422, not an "ignored" warning** [repo: `GearParams(bore_hex=6, keyway_width=3, keyway_depth=1.4)` raises "A keyway cannot be cut into a hex bore: set bore_hex to 0 ... or set keyway_width and keyway_depth to 0", `calc.py` ~653]. The milestone brief groups it with the ignored-field cases, but only `bore_d`/`bore_flat` under hex (and the cutout dimensions at count 0) are warn-and-ignore. A keyway needing `bore_d > 0` is also a 422. If the keyway fields were natively `disabled` the 422 text would tell the user to edit fields they cannot edit. So the form needs two classes of relation, **inert** (warned) and **refused** (422), and the treatment must keep the field editable in both.
2. **`?bore_hex=6` warns on every use**, because `bore_d` (9) and `bore_flat` (8) default non-zero [repo, reproduced: "Hex bore replaces the round profile: bore_d (9 mm) and bore_flat (8 mm) are ignored."]. Dimming those two fields is the single most visible win of conditional fields. The warning must stay in the API response (it is honest output); `app.js` must not filter it.
3. **A UI-only selector in `app.js` collides with an existing pin and with the milestone's own rule** [repo]. `tests/test_api.py::test_the_shareable_link_round_trips_every_field_through_generic_code` (lines 162-214) fails if any quoted `GearParams` field name, or `.<field>` access, appears in `app.js` outside `DIMS`, and its comment names "a conditional-field or bore-selector patch" as the thing it forbids. PROJECT.md says both "a UI-only select in `app.js`" and "a field relation lives in schema metadata, never hard-coded in `app.js`". These cannot both hold. Surface it (CLAUDE.md "evidence conflicts").
4. **`root_shape=trochoid` is a no-op for most larger gears** [repo, reproduced at 25 degrees: z=19 and 23 build the hob root; z=30, 41, 60 print "No radial root to replace ... the trochoid root request is ignored."]. A file named `..._trochoid` for a z=41 request would name a root the part does not have. The name should come from the effective root mode, not the request (L08 spirit).
5. **`gearQuery()` reads `input.value`, not `FormData`** [repo, `app.js:103-109`]. Disabled or hidden inputs are still sent, so any dim/disable/hide treatment leaves the URL and API contract (L05) untouched unless the code deliberately excludes a field. Good: nothing to build for "sent as-is"; it is the default.
6. **A headless browser test is cheap in wall time here** [repo, measured]. Spike on this host (macOS arm64, Python `playwright` 1.63.0, cached `chrome-headless-shell` 1228, uvicorn serving the real app): form build + first STL + invalid field + warning + link round trip in **2.2-4.1 s total**, browser launch 0.2-0.3 s, WebGL2 context available with no flags (ANGLE over SwiftShader). Cost is in install weight (below), not run time.
7. **Dependency order**: browser test -> conditional fields -> selector; the download name is independent. Both UI ideas named "a browser test exists" as their trigger (`docs/ideas/2026-09-27-...`, `2026-09-29-...`).

---

## Category 1 - Browser test for the viewer

### What the minimum credible assertion set is

The failure modes named by the idea file are ones Python cannot see: a renamed CSS custom property, a `detail[].ctx.fields` shape change, an ordering bug in the debounce/abort loop. A test is worth its cost if each assertion maps to one of those or to a stage of the pipeline (schema -> form -> request -> render -> scene).

### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Real server fixture (uvicorn on an ephemeral port, torn down after) | `TestClient` has no socket; a browser needs one | MEDIUM | The only non-trivial piece. App imports the CadQuery pool; start once per session, not per test. [judgement] |
| Form builds from `/api/schema` | Idea file item 1 | LOW | Assert `.field` count == `len(schema.properties)` and `fieldset` count == distinct `group` values, **both read from `/api/schema` inside the test**, never hard-coded (spike: 31 fields, 7 groups). Adding a field must not break the test. |
| First build completes: `#dl-stl` gains `href`, no `pageerror` | Proxy for "STL loaded into the scene" | LOW | `setDownloads(q)` runs only after `showModel(buf)` returned, so a parse or scene failure lands in `fail()` and the href never appears [repo, `app.js:208-213`]. No production hook needed. |
| Canvas is not blank | A scene can "load" and draw nothing (lights, camera, theme colour) | LOW | Element screenshot of `#canvas`, assert more than one distinct pixel colour (spike: 11,478 distinct RGBA values). Do not compare to a golden image. |
| Invalid field marked + message rendered | Idea file item 2 | LOW | Fill `bore_flat=3`; assert `.field.invalid` contains `input[name=bore_flat]`, one `p.error`, downloads `aria-disabled`. Reproduced in spike. |
| Warning rendered | Idea file item 3 | LOW | Set `bore_hex=6`; assert the count and text of `#messages p.warning` equal the `warnings` of `GET /api/info` for the same query fetched in the test. Matches the repo's rule that tests capture sentences from `derive()`, never type them (L33). |
| Shareable-link round trip in the browser | The static token pin proves the code shape, not that it works | LOW | After an edit `location.hash == "#bore_hex=6"`; a fresh page at that URL has the input at 6 and `#dl-stl` href containing `bore_hex=6`; Reset empties the hash. |
| CSS custom properties the JS reads are non-empty | The idea file's first named failure mode | LOW | `getComputedStyle(document.documentElement).getPropertyValue(name)` for `--view-bg`, `--grid`, `--mesh`, `--edge` (the four `css()` reads). One loop. |
| Fail loudly if the browser is missing | A silent skip is a false green; CLAUDE.md "nothing is done until checks pass" | LOW | Decision for discuss-phase, but the default answer is fail, not skip. [judgement] |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Stale-response ordering test | Guards the `seq`/`AbortController` loop the idea file names | MEDIUM | `page.route` to delay the first `/api/info`, edit again, assert the final hash/dims belong to the second edit. Timing-sensitive; only worth it if made deterministic with the route hook. |
| Dark-theme re-theme path | `applyTheme` on `prefers-color-scheme` change | LOW | `color_scheme="dark"` context, canvas still non-blank. One line once the harness exists. |
| Console-error guard on the happy path only | Catches uncaught regressions | LOW | Assert on `pageerror`, and on `console.error` only before the invalid-field step. Spike showed WebGL "GPU stall due to ReadPixels" **warnings** and an expected `422` console **error** on the invalid path, so "no console noise" is wrong. |
| Harness shaped for reuse by features 2 and 3 | The conditional/selector assertions are the test's first real consumers | LOW | One `page` fixture that has waited for the form; the next two features add rows, not a second harness. |

### Anti-Features (over-reach)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Golden-image / pixel-diff of the 3D view | "Visual regression" is the textbook WebGL test | SwiftShader vs a real GPU, device pixel ratio and theme all change pixels; the sources on WebGL testing say to lock determinism first and prefer state assertions [src, MEDIUM] | Non-blank canvas + `#dl-stl` href |
| Asserting `#dims` numbers | Looks like end-to-end coverage | Python owns every number (L08); asserting them twice makes two truths | Assert only that rows render for a known key |
| Camera/orbit/Fit/fps tests | Viewer is "the product" | Tests three.js, not spur; fps is host-dependent | None |
| Firefox/WebKit matrix | Cross-browser | `app.js` has no engine-specific code [ASSUMPTION]; triples install weight | One engine: Chromium headless shell |
| `window.__spur = { scene }` test hook | Direct "is the mesh in the scene" | Production code change to serve the test; the DOM proxy already proves it | `#dl-stl` href + canvas pixels |
| jsdom/happy-dom with a stubbed three bundle | Cheaper than a browser | Cannot see WebGL, CSS custom properties, layout or request ordering; asserts against the stub [judgement] | Real headless Chromium |
| Browser inside the runtime image / `make check` smoke | Symmetry with CI | L11: the image needs no Node; same spirit for a browser [judgement] | Run from the dev venv against a local server |

### Cost and gate facts the Lxx needs (the milestone's first decision)

- **Install weight [repo, measured]:** `pip install playwright` adds 3 packages (`playwright` 1.63.0, `greenlet` 3.5.6, `pyee` 13.0.1; 135 MB in site-packages because it bundles a Node driver). Browser binaries live **outside** the venv: `chrome-headless-shell` 192 MB, full Chromium 344 MB on this host (`~/Library/Caches/ms-playwright`, Linux `~/.cache/ms-playwright`). `playwright install --only-shell chromium` avoids the 344 MB [src: playwright.dev/python/docs/browsers].
- **Version coupling [repo, measured]:** Playwright 1.63.0 wants browser revision 1243; this host's cache held 1228. Any version bump re-downloads ~190 MB. Pin it in the closure `PIP_CONSTRAINT` already uses (L12/L34).
- **L36 interaction [repo]:** `verify.fast` is "every test file but four" via `--ignore=` (Makefile ~173) under a 30 s commit cap. A browser test file must be added to that ignore list or it lands in pre-commit.
- **Run time:** the whole assertion set is ~2-4 s plus server start; the gate delta is not measured here (L08: measure before accepting, against the re-set L34 bar).
- **Not verified:** Linux GitHub Actions. Sources say headless Chromium falls back to SwiftShader for WebGL and newer builds want `--enable-unsafe-swiftshader`; on macOS no flag was needed [src, MEDIUM; repo]. Treat CI WebGL as LOW until a CI run prints a context.

---

## Category 2 - Conditional form fields

### How the dependency is declared (conventions)

| Mechanism | What it is | Fit for spur |
|-----------|------------|--------------|
| JSON Schema `if/then/else`, `dependentRequired`, `dependentSchemas` | Pure validation keywords; "no mention of UI implications" [src: json-schema.org] | Wrong tool. They say whether data is valid, not whether a field is shown. [src, MEDIUM] |
| JSON Forms `rule` | Lives in the **UI schema**, separate from the data schema: `effect` (SHOW/HIDE/ENABLE/DISABLE) + `condition` (a `scope` pointer + a JSON Schema validated against that data) [src: jsonforms.io rules, MEDIUM] | Closest precedent: a small effect + a schema fragment per referenced field. Docs are silent on the data of hidden controls. |
| react-jsonschema-form | Reveals fields from `dependencies`; UI hints (`ui:*`) live in a separate uiSchema [src, MEDIUM] | Same split: data schema stays validation-only. |
| Custom extension key (`enabled_when`) | Metadata beside `group`/`unit` in `json_schema_extra`; pydantic emits nested dicts/lists verbatim [repo, verified: `{"enabled_when": {...}, "also": [...]}` round-trips] | **Recommended.** Keeps `/api/schema` the only source (L02); the data schema and every other consumer are unchanged. |
| OpenSCAD Customizer | No conditional visibility at all; only a `[Hidden]` group (hidden variables stay stored in JSON but are not read back) [src: manual, HIGH] | Gating is beyond the baseline of the closest "parameters to a printable part" tool; it is a differentiator against it, not a table stake of the genre. |

Vocabulary actually needed [repo, derived from `calc.py`]: a **conjunction** of per-field tests where each test is "equals 0" or "greater than 0" on a numeric flat field. Examples: `bore_d`, `bore_flat` need `bore_hex == 0`; `keyway_*` need `bore_hex == 0` AND `bore_d > 0`; spoke dimensions need `spoke_count > 0`; hole dimensions need `hole_count > 0`; `hex_wall` needs `hex_cell > 0`. No OR, no enums, no cross-group. A JSON-Schema-flavoured fragment per field (`{"const": 0}`, `{"exclusiveMinimum": 0}`) evaluated by a ~10-line JS function is the smallest thing that covers it. [judgement]

### The relation inventory (calc-backed only)

| Dependent field(s) | Gate | calc's signal today | Class |
|--------------------|------|---------------------|-------|
| `bore_d`, `bore_flat` | `bore_hex > 0` closes it | warning "Hex bore replaces the round profile ..." | inert |
| `keyway_width`, `keyway_depth` | `bore_hex > 0` closes it | **422** "A keyway cannot be cut into a hex bore" | refused |
| `keyway_width`, `keyway_depth` | `bore_d == 0` closes it | **422** "A keyway needs a round bore" | refused |
| `spoke_width`, `hub_d`, `rim_wall`, `spoke_fillet` | `spoke_count == 0` | warning "No spoke arms with spoke_count 0 ..." | inert |
| `hole_d`, `hole_circle_d` | `hole_count == 0` | warning "No lightening holes ..." | inert |
| `hex_wall` | `hex_cell == 0` | warning "No honeycomb with hex_cell 0 ..." | inert |

Relations that **look** inert but have **no** calc signal (reproduced: `bore_d=0` and `bore_flat=0` produce no warning): `bore_flat` when `bore_d == 0`; `recess_depth/width/inner_d/fillet` when `recess_sides == none`; `bore_chamfer`/`bore_clearance` with no bore. Declaring these would make the UI say "inert" where the API says nothing, contradicting Core Value. Add the warning first or leave them out; recommend leave out and file an idea. [judgement]

### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| `enabled_when` metadata on the model, evaluated by generic code in `app.js` | L02; the form is generated from `/api/schema` and nothing else; keeps the existing field-name pin green | MEDIUM | `app.js` names no field. Needs an Lxx superseding 08 D-09 (the idea file says so). |
| A parity test: every declared relation matches calc | Core Value (L08): the UI must not say "inert" where calc does not | MEDIUM | For each dependent field set off-default with its gate closed, assert `derive()` warns (inert) or construction raises (refused). Fails when the schema and calc drift. [judgement] |
| Dim, **do not disable**: keep the control editable, values untouched | The refused pair above; also users may legitimately type a dimension before its count | LOW | CSS class on `.field` (the label wrapper already exists); no `disabled` attribute. Native `disabled` removes focus, so a 422 pointing at a disabled field is a dead end (finding 1). See comparison below. |
| Re-evaluate on every `input`, after `readHash()`, after Reset and on `hashchange` | The state must match the values at all times, including a link that loads with a closed gate | LOW | Four call sites, one function. Treat `''` as the field's default (`gearQuery` omits `''`), or clearing a field would misread the gate. |
| A reason, in place, derived from the schema | A dim with no reason is the "disabled with no explanation" complaint [src] | LOW | Generate "Used when {title of gate field} is above 0" from the gate field's `title`; no extra metadata, no hard-coded text. Link it with `aria-describedby` so assistive tech gets it without anything appearing or disappearing. |
| Covers the six relation rows above | The brief's scope | LOW | Metadata on 15 fields. |
| Values kept and sent as-is | L05: a link means what it meant | none | Falls out of `gearQuery()` (finding 5). |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Different look for refused vs inert | Tells the user "this combination will be rejected", not just "has no effect" | LOW | Same mechanism, second class name. Only the keyway rows use it. |
| Browser assertions for each class | The first real consumer of Category 1 | LOW | Load `#bore_hex=6`: `bore_d`, `bore_flat`, `keyway_*` wrappers dimmed; load `#spoke_count=6`: spoke dims live. |
| Open the group's dependents when the gate opens (focus nothing) | Smooth set-count-then-dimension flow | none | Free: dim is removed on `input`. |

### Anti-Features

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Hide** inert fields | Cleaner form | Typing `0` in a count makes four fields vanish under the cursor (layout shift); a hidden field with a value still shapes or refuses the part (a 422 about fields the user cannot see); GOV.UK notes reveals are not always announced (WCAG 4.1.2) [src, MEDIUM] | Dim in place |
| Native `disabled` | The standard HTML mechanism; skipped in tab order; not submitted | Dead end on the refused pair; blocks set-dimension-before-count; Roselli argues against disabling form fields and prefers helper text [src, MEDIUM]; `disabled` is "not sent" by HTML rules [src, MEDIUM] which is **not** how spur's URL behaves | `aria-describedby` reason + dim |
| Clearing/zeroing a dependent when its gate closes | Tidy state | Silently changes a value the user set (L03 "did the user ask for this?"), loses numbers, rewrites URLs | Keep values; warnings remain the backstop |
| Filtering the ignored-field warnings out of the UI | Redundant once dimmed | The API/CLI still emit them and the warning is the honest reactive signal; hiding it in one front end breaks parity (L02) | Show them; fix the default-noise in calc as its own item |
| Re-implementing `check()` in JS to predict 422s | "Tell them before" | A second source of truth for refusals; the 422 owns them | Gate only on the six calc-backed relations |
| JSON Schema `if/then/dependentSchemas` as the declaration | "Standard" | Validation-only keywords [src]; other schema consumers would read UI intent as validation | `enabled_when` extension key |
| A second `visible_when` key, boolean fields, OR/enum conditions | Flexibility | Nobody asked; the six rows need none (project refuses speculative flexibility) | Add when a real relation needs it |
| Cutout "pick one" lock (dim the other two groups' counts while one is on) | Same shape as the bore selector; L30 refuses two patterns with a 422 | Out of the brief; it is the refused class and needs its own design | File under `docs/ideas/` |

---

## Category 3 - Bore-shape selector over flat fields

### How "pick one" over a flat contract is presented

- **Derive on load, write through on change.** The select is a *view* of the flat fields: its state is computed from them after `readHash()`, after Reset, on `hashchange` and after any edit to a bore field; choosing an option writes flat fields back. The select never enters the `fields` map, so it is never in the URL or `gearQuery()`. [judgement; follows from L05 and the brief]
- **Precedence must mirror calc**, not be invented [repo]: `bore_hex > 0` -> Hex (it "replaces the round profile"); else `bore_d == 0` -> no bore; else `bore_flat > 0` -> D-flat; else Round. The default part is a **D-flat** gear (`bore_flat` default 8), not a round one.
- **Fields of non-selected shapes** (the question asked): three conventions exist, *kept and sent*, *disabled and omitted* (native form semantics [src]) and *cleared*. For spur: **kept** for the inert pair (`bore_d`/`bore_flat` under Hex), so switching back loses nothing and the URL shape equals what typing in the hex field produces today; **zeroed with an in-memory stash** only for the pair that would otherwise be refused (`keyway_*` under Hex or No bore), because the user's explicit pick is what creates the conflict, and the stash makes it reversible. [judgement]
- **Keyway stays out of the select.** It is a modifier whose state is its two fields (ARCHITECTURE Q3, L27/L28); under Hex the conditional fields already dim it. A composite option ("Round + keyway", "D-flat + keyway") doubles the list. The brief lists "keyway-as-modifier" in the select; recommend against and confirm. [judgement]

### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Select with Round / D-flat / Hex, state derived on load | The brief | MEDIUM | Derived from flats, precedence above. |
| **Total** derivation: also a "No bore" option | `bore_d=0, bore_hex=0` is a legal part (no warning, reproduced); without an option the select must lie (show Round with a 0 bore) | LOW | The brief lists four shapes; this is a fifth state forced by totality. Surface as a decision. |
| Re-derive on every edit of a bore field, Reset and `hashchange` | Else the select goes stale the moment someone types into `bore_hex` | LOW | Same call sites as the conditional-field refresh. |
| Write-through changes flat fields only; URL, API, CLI contract unchanged | L05, L02, "no new GearParams field" | LOW | `bore_shape` never appears in the URL. A link made by the selector is a link the typed fields could have made. |
| Round: `bore_hex=0`, `bore_flat=0`. D-flat: `bore_hex=0`, `bore_flat` = stash or the schema default (8). No bore: `bore_d=0`, `bore_hex=0`, keyway pair 0. Hex: keyway pair 0, leave the rest | The minimum write that makes the shape true and avoids a 422 | LOW | Defaults come from the schema (`defaults[name]`, absolute mm, L05); no number is invented. |
| Choosing Hex does not invent an across-flats | Any default A/F is a dimension someone cuts to (L08) | LOW | `bore_hex == 0` cannot be derived as Hex, so "Hex chosen, A/F still 0" is **UI-only transient state**: show Hex, focus the A/F field, leave the part as the flats say until a number is typed. |
| Browser test of the round trip | Both ideas name a browser test as the trigger | LOW | Load `#bore_hex=6` -> Hex; pick D-flat -> hash drops `bore_hex`; pick Hex then type 6 -> keyway pair 0; Reset -> D-flat. |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Stash/restore of the zeroed keyway values | Flip-flopping shapes does not lose typed numbers | LOW | A `Map` in memory; ~5 lines. |
| Prevents the one 422 the bore group has | hex x keyway never reaches the server from the form | LOW | A by-product of the keyway write. |

### Anti-Features

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Model-level `bore_type` field | "Schema-driven select" | Forbidden this milestone (no new field); the keyway is a modifier, not a type (ARCHITECTURE Q3); needs an L05 alias story for every link | Derived UI-only view |
| `bore_shape` in the URL | Selector state survives reload | A second way to say the same thing; drifts from the flats; changes what links contain | Re-derive from flats |
| Zero `bore_d`/`bore_flat` on choosing Hex | Silences the ignored-field warning | Creates new link shapes (`bore_hex=6&bore_d=0&bore_flat=0`), loses the user's bore, and papers over a calc warning that fires on defaults (finding 2) | Keep them dimmed; fix the warning noise separately |
| Composite options (Round + keyway ...) | One control for everything | Option explosion; keyway is not exclusive with round/D-flat | Keyway stays two fields |
| Seeding Hex with a "sensible" A/F | Avoids the transient state | An invented dimension (Core Value); the help text's stock sizes are hints, not defaults | Focus the field |
| Radio group / segmented control | Looks better | The brief says `<select>`; no evidence it is needed | `<select>` |
| Selector for the three cutout patterns | Same "pick one" shape | Out of scope; the refused class | `docs/ideas/` |

### Where the logic lives (open decision, finding 3)

| Option | Upside | Downside |
|--------|--------|----------|
| A. Selector declared in schema metadata (options, the fields each writes, precedence) and rendered by generic code | `app.js` stays field-agnostic; the pin and L02 hold; precedence is not a second copy of calc's | New metadata vocabulary; the largest of the four items |
| B. Hard-code the bore logic in `app.js`, amend the pin by an Lxx and carve out L02 | Smallest code, matches the brief's wording | First bore-specific logic in `app.js`; the precedence is duplicated in JS and must be parity-tested against calc; weakens the pin that was written to stop exactly this |
| C. B in a second `.js` file | Dodges the pin by file, not intent | Gaming the check; reject [judgement] |

Recommendation: A if the budget allows, otherwise defer the selector and keep the conditional fields (which already dim the inert pair and the keyway). It is the most discretionary item. [judgement]

---

## Category 4 - Download file name carries the root shape

### Conventions for a variant in a file name

- The `filename` parameter is an ASCII token in `Content-Disposition` (RFC 6266; `filename*` exists for non-ASCII) [src, MEDIUM]; the current slug already uses only `[A-Za-z0-9._]` and a variant suffix stays inside that.
- Browsers disambiguate duplicates by appending a counter, which is the symptom the idea file describes [idea file; not independently verified here].
- Encoding a variant *without renaming existing files* means the default carries no marker and only the non-default adds one. That is how the product already treats parameters: `gearQuery()` sends only values that differ from defaults. [judgement, consistent with repo]

### Pins to read first [repo]

| Where | What it pins | Effect of "suffix only when not radial" |
|-------|--------------|-----------------------------------------|
| `tests/test_api.py` ~376-412 | Asserts the radial and trochoid (z=23) dispositions are **equal** and `filename="spur_z23_m1.75_pa25.stl"` | The one assertion that must flip, deliberately |
| `tests/test_api.py:720` | `spur_z21_m1.75_pa25.{fmt}` (default radial) | Stays green |
| `src/spur/records.py:180` | `slug` is a log field, not a file | Same suffix appears in `build.*`/`export.served` records for trochoid only |
| `tests/test_records.py` | Literal fabricated `"spur_z19"` | Unaffected |
| `bench/export_cost.py:176`, `model.py:807` | Slug names a temp file | Unaffected |
| `docs/architecture/http-api.md:43` | Documents `params.slug()` | One sentence to update |
| CLI | `-o` is required and the caller's own name | Unaffected |

### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Radial downloads keep today's exact name | The brief: do not rename every existing download | LOW | `spur_z19_m1.75_pa25.stl` unchanged; the default and every existing link are unaffected. |
| Trochoid gets a suffix: `spur_z19_m1.75_pa25_trochoid.stl` | The point of asking for it is that the roots differ | LOW | Suffix, not prefix, so `spur_z19_*` still groups variants. [judgement] Same function names STL and STEP. |
| Name from the **effective** root mode (finding 4) | A name is a claim about the part (L08) | LOW-MEDIUM | `slug()` consults `root_mode` only when `root_shape == "trochoid"` (cost ~tens of microseconds per Phase 18's 31,446-case sweep, 1.7 s; zero for radial). Alternative: name by request, simpler and pure but can name a root the part lacks. Decide at discuss. |
| One definition: HTTP header and record `slug` both from `GearParams.slug()` | Two spellings would drift | LOW | |
| Own `Lxx` that lists what pinned the old name | The idea file requires it | LOW | The table above is the list. |

### Differentiators

None worth building. The idea file's trigger ("a user reports mixing them up") has not fired; this item is cheap hygiene, not a differentiator.

### Anti-Features

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Encode every non-default parameter or a hash in the name | Names fully identify the part | Renames every non-trivial download; long unstable names; the idea file says most parameters already share a name and accepts it | Suffix only the variant whose difference is the point |
| `_radial` on the default | Symmetry | Renames every existing download | Default carries no marker |
| A generic "append every non-default Literal" rule | Future-proof | `recess_sides=none` and `root_shape` would rename existing downloads of links that exist today | Handle `root_shape` only; add per feature under its own Lxx |
| Include `root_fillet` in the name (`_trochoid_r0.5`) | Identifies the hob | Over-encodes; the value is in the link | None |
| Counter or timestamp suffix | Avoids overwrites | Server is stateless; names stop being reproducible | Distinct variant names |
| Prefix (`trochoid_spur_z19...`) | Visible first | Breaks sort adjacency and `spur_z19_*` globs | Suffix |

---

## Feature Dependencies

```
Browser test (harness, 8 assertions)
    +--enables--> Conditional fields   (assertions for dim classes; idea-file trigger)
    +--enables--> Bore-shape selector  (assertions for derive/write-through; idea-file trigger)

Conditional fields (enabled_when metadata + generic evaluator + calc-parity test)
    +--feeds--> Bore-shape selector    (same refresh call sites; keyway dim under Hex; the metadata
                                        is the natural home for the shape/field relation)

Bore-shape selector --conflicts-with--> field-name pin in tests/test_api.py (unless metadata-driven or the pin is amended by an Lxx)

Download name  (independent; own Lxx; flips one assertion in tests/test_api.py)
```

### Dependency Notes

- **Browser test before both UI items:** both ideas were deferred "until a browser test exists"; and the test is the only thing that can see dim/derive/write-through behaviour.
- **Conditional fields before the selector:** not a technical hard requirement (the selector can write fields without it) but the selector without it leaves the refused pair reachable by typing, and the precedence ("hex wins") would exist in two places. After conditional fields land, the selector's remaining value is discoverability of Hex and avoiding the one 422.
- **Selector vs pin:** see Category 3, "Where the logic lives".
- **Download name** touches `params.py`, `records.py`, two tests and one doc; no overlap with the form work, so it can ride any phase or stand alone.
- **Fixture:** none of the four touches `GearParams` fields or `derive()`; the 44-record fixture stays byte-identical [brief; the name change is not in the fixture, which pins `derive()` and `build()` outputs].

## MVP Definition

### Launch With (v0.5)

- [ ] Browser test: server fixture + form built + first build/`#dl-stl` href + non-blank canvas + invalid marked + warning equals API + link round trip + CSS custom properties; fail loud if no browser; one Lxx pricing the gate cost beside L34
- [ ] Conditional fields: `enabled_when` metadata on the 15 fields (six rows), generic evaluator, dim-and-editable, in-place reason, parity test against calc, browser assertions; one Lxx superseding 08 D-09
- [ ] Download name: `_trochoid` suffix from the effective root, pins updated, one Lxx

### Add After Validation (v0.5.x, if the milestone has room)

- [ ] Bore-shape selector (metadata-driven, Option A) - trigger: browser test exists and conditional fields are in; the largest and most discretionary item
- [ ] Stale-response ordering test - trigger: any report of a stale preview
- [ ] Refused-vs-inert styling - trigger: the dim alone proves unclear

### Future Consideration

- [ ] Calc-backed warnings for the silent relations (`bore_flat` at `bore_d=0`, `recess_*` at `recess_sides=none`), then gating them - they need the warning first (L08)
- [ ] Stop the hex warning firing on default `bore_d`/`bore_flat` - touches API output, so its own item and fixture check
- [ ] Cutout "pick one" lock - same shape as the selector; refused class
- [ ] Browser test on CI Linux/Docker - unverified here

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Browser test, minimum set | HIGH (protects the product's UI; unblocks two items) | MEDIUM (server fixture, install weight, gate cost) | P1 |
| Conditional fields (inert + refused rows, dim-editable) | HIGH (removes the always-on hex warning's confusion) | MEDIUM | P1 |
| Parity test: `enabled_when` vs calc | HIGH (Core Value) | MEDIUM | P1 |
| Download name suffix | MEDIUM | LOW | P1 |
| Bore-shape selector | MEDIUM (discoverability once fields dim) | MEDIUM-HIGH (metadata design or pin amendment) | P2 |
| Stale-response test | MEDIUM | MEDIUM | P3 |
| Refused-vs-inert styling | LOW-MEDIUM | LOW | P3 |
| Stash/restore of keyway values | LOW-MEDIUM | LOW | P2 (ships with selector) |

**Priority key:** P1 must have for the milestone; P2 should have, add when possible; P3 nice to have.

## Comparison With Other Tools

| Concern | OpenSCAD Customizer | JSON Forms / rjsf | Native HTML form | spur v0.5 plan |
|---------|--------------------|-------------------|------------------|----------------|
| Declare a dependency | None; `[Hidden]` group only [src] | Rule/`dependencies` in a UI layer, data schema stays validation [src] | None | `enabled_when` in `json_schema_extra` |
| Pick-one over parameters | Dropdown comment `// [a, b, c]` sets one value [src] | Enum + rule per branch [src] | `<select>` / radios | `<select>` derived from flats; flats stay the contract |
| Values of an inapplicable field | Stay in the script | Docs silent | `disabled` -> not submitted [src] | Kept and sent (dimmed, editable) |
| Gear generators (FreeCAD gears, KISSsoft, web generators) | Not surveyed here; desktop dialogs not researched | - | - | - |

## Open Decisions to Surface (CLAUDE.md "stop and ask")

1. **Selector home** - metadata (A) vs hard-coded + pin amendment (B). Evidence conflict inside PROJECT.md (finding 3). Recommend A, or defer the selector.
2. **Dim-and-editable vs native `disabled`** - recommend dim-and-editable because of the hex x keyway 422 (finding 1).
3. **"No bore" option; keyway outside the select** - recommend both (totality; modifier, not a shape).
4. **Name by effective root vs by request** - recommend effective (finding 4).
5. **Browser test in `make verify`: fail-loud vs skip; excluded from `verify.fast`** - recommend fail-loud and excluded; price it beside L34 before accepting.
6. **Hex warning noise on defaults** - file as debt/idea; do not filter in `app.js`.

## Sources

- Repo, read 2026-10-10 **[HIGH]**: `src/spur/static/app.js`, `src/spur/params.py`, `src/spur/calc.py` (ignored/refused rules ~653-667, 1160-1250; `root_mode` ~1675-1710), `tests/test_api.py` (pin 162-214; filename 376-412, 720), `docs/ideas/` (four files), `docs/architecture/decision_log.md` (L02, L05, L11), `.planning/PROJECT.md`.
- Reproduced here **[HIGH]**: hex x keyway 422; `?bore_hex=6` warning on defaults; `bore_d=0`/`bore_flat=0` silent; trochoid no-op at z=30/41/60; `json_schema_extra` nested dict emitted verbatim; headless spike (Playwright 1.63.0, chrome-headless-shell 1228, macOS arm64, 2.2-4.1 s, 31 fields/7 groups, 11,478 distinct canvas pixels).
- JSON Schema conditionals are validation-only: https://json-schema.org/understanding-json-schema/reference/conditionals **[MEDIUM]**
- JSON Forms rules (effects, scope + schema condition): https://jsonforms.io/docs/uischema/rules/ **[MEDIUM]**
- react-jsonschema-form dependencies: https://rjsf-team.github.io/react-jsonschema-form/docs/json-schema/dependencies/ **[MEDIUM]**
- `disabled` vs `aria-disabled`: https://kittygiraudel.com/2024/03/29/on-disabled-and-aria-disabled-attributes/ **[MEDIUM]**
- `inert`: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/inert **[MEDIUM]**
- Disabled form controls guidance (Roselli and summaries): https://hidde.blog/links/dont-disable-form-fields/ **[MEDIUM]**
- GOV.UK conditional reveals and WCAG 4.1.2: https://design-system.service.gov.uk/components/radios/ **[MEDIUM]**
- OpenSCAD Customizer manual: https://files.openscad.org/documentation/manual/Customizer.html **[HIGH]**
- Playwright browsers, headless shell, cache paths: https://playwright.dev/python/docs/browsers **[MEDIUM]**
- Headless Chromium WebGL / SwiftShader flags: https://chromium.googlesource.com/chromium/src/+/da170c2267b2201954efe1c8fa5d2d89ab09f7bf/docs/gpu/swiftshader.md and https://microlink.io/blog/webgl-without-a-gpu **[MEDIUM, third-party; CI behaviour unverified]**
- Content-Disposition `filename` / `filename*`: RFC 6266 (https://www.greenbytes.de/tech/specs/draft-ietf-httpbis-content-disp-04.html) **[MEDIUM]**

---
*Feature research for: spur v0.5 Honest Form (browser test, conditional fields, bore-shape selector, download name)*
*Researched: 2026-10-10*
