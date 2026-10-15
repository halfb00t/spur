# Phase 22: Download Name Carries the Root - Context

**Gathered:** 2026-10-11
**Status:** Ready for planning

<domain>
## Phase Boundary

`GearParams.slug()` (`src/spur/params.py:190`) appends `_trochoid` exactly when
`calc.root_mode` builds the hob root for those parameters. Every radial part, and every
request whose trochoid is ignored or refused by `root_mode`, keeps today's name byte for
byte: `spur_z{teeth}_m{module:g}_pa{pressure_angle:g}`. `slug()` stays total — it is
called inside `build.failed` and `queue.refused` records. The `Content-Disposition`
header (`app.py:496`), the record's `slug` (`records.py:180`) and the temp export stem
(`model.py:807`) all keep calling `slug()` unchanged; the suffix reaches them through
the one definition.

Proof: `tests/test_api.py` reads `Content-Disposition` for STL and STEP at 23 teeth
(`_trochoid`) and 40 teeth (today's name); the browser scenario gains one named step that
clicks `#dl-stl` on a 23-tooth trochoid part and reads `suggested_filename`; pure tests
call `slug()` on a refused and an ignored request; the `build.failed` test asserts the
record's `slug` on a trochoid request. One new `Lxx` lists every grepped consumer of the
old names before they move, states that no cache is keyed by slug, and retires the idea
file. `git diff --exit-code tests/regression/pre_v0_2.json` is clean (the fixture holds
no `spur_z` string).

Fixed by ROADMAP: a suffix, not a prefix; `_trochoid` is the only non-default root value;
no other root value is invented; no `GearParams` field; no `app.js` edit.

**Evidence conflict found at discuss time:** ROADMAP's "reuses Phase 21's
`expect_download` harness" is false — `tests/test_browser.py` asserts the `#dl-stl` href
but never clicks it; no `expect_download` exists in `tests/`. This phase builds the
download step (D-04..D-07). REQUIREMENTS.md's `docs/http-api.md` is
`docs/architecture/http-api.md`.

</domain>

<decisions>
## Implementation Decisions

### Suffix rule and totality
- **D-01:** **Decision 12 — the suffix follows the effective root.** `slug()` appends
  `_trochoid` when `root_mode(p, profile(p), requested=p.root_shape, rho=p.root_fillet).mode
  == "trochoid"`, never from `p.root_shape` alone. A 40-tooth `root_shape=trochoid` request
  (ignored: "nothing radial to replace") downloads under today's name. A name is a claim
  about the part (L08); this is the third consumer of L38's single predicate (after
  `derive()` and `model._build`). Cost accepted with the figure in front of the human:
  `profile()` + `root_mode()`, 10–30 µs (19-09, `derive()` 10.3 µs radial / 30 µs
  trochoid), zero solver work for a radial request (`root_mode` returns at
  `requested != "trochoid"` before building the cutter). Rejected: requested root (pure
  string, but names a root the part lacks and contradicts REQ-slug-carries-effective-root).
  — **Reversibility:** costly — the `Lxx` records the rule, `http-api.md` states it, the
  browser pin and the `test_api.py` pins assert it; switching to requested renames every
  ignored-request download a second time.
- **D-02:** **No guard: totality is by construction and proved by test.** No `try/except`
  in `slug()`. On a validated `GearParams`, `root_mode` returns a `RootReason` string for
  every refusal and never raises: `cutter()` raises `ValueError` only for a non-finite or
  negative `rho`, which Pydantic's `root_fillet` bounds reject first; `_root_curve` returns
  reasons; `_junction` returns `None` on a failed bracket (31,446-case sweep, 556,920
  combinations for F9). Tests call `slug()` on a `tip land gone` request and on a 40-tooth
  ignored request and get today's name. Rejected: fallback to the radial name on exception
  (a plausible name is a false claim, L08, and hides a `calc` bug behind a filename);
  fallback to a marked name such as `_root-unknown` (invents a third root value the
  roadmap boundary excludes).
- **D-03:** **The call lives inside `slug()` through a local import.** `from .calc import
  profile, root_mode` inside the method body, the pattern `_feasible` already uses at
  `params.py:180` (module-level would be circular: `calc` imports `GearParams`). No
  `calc.effective_root()` helper: a one-line pass-through with one caller. `app.py`,
  `records.py`, `model.py` are not edited (research ARCHITECTURE §6.1). The import-linter
  contracts are unaffected: `spur.params` → `spur.calc` is already a live edge.

### Browser proof of the name
- **D-04:** **A real click with `page.expect_download()`.** The scenario sets
  `location.hash` to a 23-tooth `root_shape=trochoid` state, waits for the `#dl-stl` href
  (content-based, 21 D-04 wait discipline), then `with page.expect_download() as d:
  page.click("#dl-stl")` and asserts `d.value.suggested_filename ==
  "spur_z23_m1.75_pa25_trochoid.stl"` — equal to the `Content-Disposition` the API test
  reads for the same params. This is what the user sees and what ROADMAP SC1 names. The
  anchor has no `download` attribute; navigation to an `attachment` response fires the
  event. The link requests `quality=fine` (`ModelQuery` default, `app.py:238`), so the
  step is one fine build of a 23-tooth trochoid part on the gate's `uvicorn`. Rejected:
  `page.request.get(href)` header read (same server cost, no browser download event,
  duplicates the Python pin); route-capture of the href (the name is set by the server
  header, not the href — proves nothing SC1 asks).
- **D-05:** **STL only in the browser.** STEP's `Content-Disposition` at the same params
  is pinned in `tests/test_api.py` (D-08); both formats are the one `slug()` call. One
  extra build in the gate, not two.
- **D-06:** **Gate cost: the step's own timing, no full-gate A/B.** The step prints its
  wall seconds the way `first build drawn` prints the PNG ratio; three readings with host
  state (`bench.machine_facts()`, load before → after, `HEAD`, UTC) go into
  `bench/RESULTS.md` under a `## Download name carries the root (Phase 22)` heading.
  Phase 25 re-sets the bar on the final `HEAD` and absorbs this step. Rejected: L39-style
  N=3-per-arm A/B (six ~190 s gate runs for one build in one step); no reading (breaks
  "a gate cost is measured before it is accepted" for this change alone).
- **D-07:** **A new named step after `golden sweep`, before `root_shape=bogus as
  today`.** `with step("download name"):` in the single scenario function (21 D-10: one
  function, one server). By then the sweep's aborted-STL routes are gone and the step's
  hash does not disturb earlier state. Rejected: re-pointing `first build drawn` at a
  23-tooth trochoid part (moves Phase 21's recorded PNG-ratio bar and `data-triangles`
  reading onto another part for no new proof).

### Lxx and test pins
- **D-08:** **`tests/test_api.py` pins STL and STEP at both tooth counts, parametrized.**
  Mirror `test_model_download`'s `(fmt, ctype, magic)` table: 23 teeth trochoid →
  `filename="spur_z23_m1.75_pa25_trochoid.{fmt}"`; 40 teeth trochoid → today's name in
  both formats; `quality=preview`. The existing `:412` assertion inside
  `test_a_root_shape_link_is_served_with_the_root_it_cut` flips deliberately in the same
  commit and its docstring's "ignores root_shape (19-RESEARCH Open Question 6)" sentence
  is rewritten; `:720` (`spur_z21_m1.75_pa25.{fmt}`, radial default) is not touched.
- **D-09:** **SC2 shape: pure `slug()` tests plus one record assertion.** Pure tests (in
  `tests/test_calc.py` or beside the params tests) call `slug()` on a `tip land gone`
  request (pressure angle 33.5 — params in `tests/test_trochoid.py:188`), on 40 teeth
  trochoid, and on 23 teeth trochoid, asserting today's name, today's name and
  `_trochoid`. In `tests/test_api.py`, the `build.failed` test at `:1059` gains a
  trochoid-request variant (or a sibling) asserting the record's `slug` equals
  `params.slug()` for that request — the record carries the suffix for a 23-tooth
  request whose build failed, because the root the part would have is the trochoid.
  Rejected: driving `build.failed`/`queue.refused` for all five `RootReason` values
  (five fixtures for a claim the pure tests prove).
- **D-10:** **The `Lxx` lists every grepped consumer, not the REQ's four.** The record
  names: `app.py:496` `Content-Disposition`; `records.py:180` `_gear_fields` feeding the
  four emitters (`build.started`, `build.failed`, `export.served`, `queue.refused` at
  `:218,231,255,267`); `model.py:807` temp export stem; `bench/export_cost.py:176`;
  `tests/test_model.py:2021`; `docs/architecture/http-api.md:43` and `:93`; the two
  `test_api.py` pins (`:412` flips, `:720` must not); the four truthy `slug` asserts
  (`test_api.py:797, 985, 1086, 1123`, unaffected); `tests/test_records.py:60,89,95`
  synthetic `spur_z19` (not tied to `slug()`); the CLI (`-o` is the caller's name,
  `cli.py:141`, unaffected); frozen history under `.planning/**` and
  `docs/tech_debt/resolved/` (not edited). It states that no cache is keyed by slug:
  the export blob cache key is `(params, fmt, q.quality, encoding)` (`app.py:401`), the
  solid cache is keyed on the `GearParams` object, `pool.py` routes by parameter hash,
  and the header is built at response time outside the byte cache. It notes that log
  greps keyed on slug see a new value for effective-trochoid gears only. It corrects
  REQUIREMENTS.md's `docs/http-api.md` to `docs/architecture/http-api.md`.
- **D-11:** **One semantic commit.** `slug()`, both `test_api.py` pins, the SC2 tests,
  the browser step, `docs/architecture/http-api.md`, the `Lxx` (next free id after L39)
  and the idea retirement (`Status: retired`, `Retired in:` line, `git mv` into
  `docs/ideas/retired/`, INDEX row moved to `## Retired` — precedent
  `docs/ideas/retired/2026-09-21-browser-test-for-the-viewer.md`) land together. The
  consumer list is written into the `Lxx` from the grep before the code moves; the
  entry is written with the shas in hand (L38/L39 precedent, append-only log). The
  `bench/RESULTS.md` readings may follow in a second commit if read after. Rejected:
  `Lxx` first, code second (the entry could not cite the code sha).

### Claude's Discretion
- Multiple `slug()` calls per request (two record emitters, the header, the worker's temp
  stem) stay uncached: under 0.2 ms per request at the measured 10–30 µs; `GearParams`
  is frozen but a `cached_property` is not worth the Pydantic interaction.
- The exact hash the browser step sets (`#teeth=23&root_shape=trochoid` or a fuller
  state), the wait signal before the click (href content, never an empty status), the
  `expect_download` timeout (`BUILD_WAIT_MS` or its own), and whether the step also saves
  the download and checks the STL header (the name is the requirement; the body check is
  optional).
- Where the pure `slug()` tests live (`tests/test_calc.py` beside the `root_mode` tests,
  or a params test file) and whether they parametrize over the three cases.
- Whether the `build.failed` slug assertion is a new parametrize row on `:1059` or a
  sibling test; `teeth=71` is that test's cache-dodging count — the trochoid variant
  needs a count no other test downloads and where the hob root applies (below 27 at the
  default module and angle).
- The `Lxx` id and heading, and whether it amends L39 (the scenario gains a step; L39's
  "one real build" sentence) or only cites it. Amending is the honest reading if L39
  states the build count.
- The `bench/RESULTS.md` subsection shape, copying `### The browser test, priced (21-07)`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scope and requirements
- `.planning/ROADMAP.md` — Phase 22 entry (`:266–303`): goal, three success criteria,
  Decision 12, boundaries; the Process Notes (`:504`) on branches, the gate, `Lxx`
  append-only, fixture discipline, debt retirement
- `.planning/REQUIREMENTS.md` — `REQ-slug-carries-effective-root`,
  `REQ-slug-consumers-read-first` (`:99–110`); "Rules every requirement lives by"
- `.planning/PROJECT.md` — milestone v0.5 intent: no new `GearParams` field, fixture
  byte-identical to the `v0.4` tag
- `docs/ideas/2026-10-08-download-name-carries-the-root-shape.md` — the idea this phase
  retires; its consumer list and "needs its own decision (`Lxx`)"

### Research (figures carry MEASURED / READ tags)
- `.planning/research/ARCHITECTURE.md` §6 (`:243–275`) — every consumer of `slug()`
  grepped, what pins the old names, the recommended suffix shape; §3.3 row 7 (`:118`)
  the `expect_download` scenario and its "second, fine build" note
- `.planning/research/PITFALLS.md` SL-1, SL-2, SL-3 (`:308–337`) — pinned names,
  requested-vs-effective, cache keys checked; `:467, :501, :511, :527, :539, :567–569`
- `.planning/research/FEATURES.md` finding 4 (`:14`), table rows `:190–213`, `:227`
  (`_trochoid_r0.5` rejected as over-encoding)
- `.planning/research/STACK.md` `:19`, `:163–165` — "pure Python slug change", check
  `Content-Disposition` safety of the literal values

### Decisions the `Lxx` cites, amends or restates
- `docs/architecture/decision_log.md` — L05 (defaults absolute; absent means unchanged —
  applied here to names), L08 (never a plausible number — here, never a plausible name),
  L38 (`root_mode` the single predicate; `root_shape` opt-in; default unmoved), L39
  (the scenario test, one server, named steps, the admission reading)
- `.planning/phases/21-browser-test-of-the-viewer/21-CONTEXT.md` — D-04 (wait on content,
  never an empty status), D-08/D-09 (the golden sweep and its pin: this phase's hash
  must leave `tests/regression/golden_requests.json` untouched — the step sets a hash,
  it does not change the form), D-10 (one scenario function, step names in assertion
  messages), D-11 (`SPUR_BUILD_WORKERS` default 2), D-12 (the A/B shape this phase does
  not repeat)

### The code under change and its consumers
- `src/spur/params.py` — `slug()` (`:190`), `_feasible`'s local `calc` import (`:180`),
  `model_config = ConfigDict(frozen=True)` (`:31`), `root_shape` and `root_fillet` fields
- `src/spur/calc.py` — `profile()` (`:158`), `cutter()` (`:1380`; the `ValueError` for a
  bad `rho`), `_root_curve()` (`:1601`), `RootMode` / `root_mode()` (`:1653–1700`), the
  three existing callers (`:354`, `:1086`; `model.py:773`)
- `src/spur/app.py` — `ModelQuery.quality` default `"fine"` (`:238`), the export cache
  key (`:401`), `Content-Disposition` (`:496`)
- `src/spur/records.py` — `_gear_fields` (`:171–180`) and the four emitters
- `src/spur/model.py:807`, `bench/export_cost.py:176`, `tests/test_model.py:2021` — temp
  stems (unaffected, listed)
- `src/spur/cli.py:141` — `-o` is the caller's name; no slug
- `docs/architecture/http-api.md` — `:43` (the header sentence) and `:93` (records carry
  the gear's `slug`)

### Tests and pins
- `tests/test_api.py` — `test_a_root_shape_link_is_served_with_the_root_it_cut`
  (`:371–412`; the flipping pin and its docstring), `test_model_download` (`:712–720`;
  the untouched radial pin and the `(fmt, ctype, magic)` table to copy),
  `test_a_failed_build_emits_build_failed_naming_the_class_and_the_level` (`:1059`), the
  truthy `slug` asserts (`:797, 985, 1086, 1123`)
- `tests/test_trochoid.py:188–206` — the `tip land gone` configuration and how
  `root_mode` is called in tests
- `tests/test_calc.py:1578–1603` — the refusal tally (980 `tip land gone`, 73 `tooth
  severed`) the pure tests can draw a case from
- `tests/test_browser.py` — `step()` (`:373`), `_follow_link()` (`:170`), `_api_get()`
  (`:107`), `first build drawn` (`:328`; the href wait and the printed reading), `golden
  sweep` (`:526`) and `root_shape=bogus as today` (`:557`) — the new step goes between
  them
- `tests/browser_session.py` — `serve()`, `launch()`, typed `eval_*` wrappers, `sweep()`
- `tests/regression/pre_v0_2.json` — must show an empty diff;
  `tests/regression/golden_requests.json` — likewise
- `bench/RESULTS.md` — `### The browser test, priced (21-07)` (`:5030`) and `### Admission
  (21-06)` (`:4969`): the host-state and readings format the step timing copies

### Retirement precedent and standards
- `docs/ideas/retired/2026-09-21-browser-test-for-the-viewer.md`, `docs/ideas/INDEX.md`
  (`## Open` / `## Retired`) — the retirement shape
- `docs/CODING_VALUES.md`, `CLAUDE.md` — comments carry the measurement; the two standing
  rules; the gate; debt and idea filing

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `params.py:180` `_feasible`: the local-import-of-`calc` pattern `slug()` copies (D-03).
- `calc.root_mode()`: the predicate; called exactly as `derive()` does at `calc.py:1086`
  (`requested=p.root_shape, rho=p.root_fillet`).
- `tests/test_browser.py` `step()` context manager and the `first build drawn` step: the
  href wait and the `print(...)` reading line the download step copies.
- `tests/test_api.py` `test_model_download` parametrize table: the shape for the four
  header pins.
- `tests/test_trochoid.py:188` `tip land gone` params: the refused request for the
  totality test.
- `bench/RESULTS.md` Phase 21 subsections and `bench.machine_facts()`: the readings format.
- `docs/ideas/retired/` + INDEX `## Retired`: the retirement shape.

### Established Patterns
- One definition, many callers: `slug()` is consumed only by calling it, so the suffix
  reaches the header, the records and the temp stem through one edit (research §6.1).
- Absent means unchanged (L05) applied to names: every radial name is byte-identical.
- Tests capture sentences and names from the code's own answer where possible, but a
  filename pin is a literal by design (`:720` is one) — the flipped pin is a literal too.
- Tests test the real thing: real `uvicorn`, real browser, a real download event.
- `mypy --strict` over `tests/`: `page.expect_download()` returns a typed
  `EventContextManager[Download]`; `suggested_filename` is `str`.
- `filterwarnings = ["error", …]`: any Playwright warning on the download path fails.
- The fixture and the golden pin never move in a feature commit.

### Integration Points
- `src/spur/params.py:190` — the one production edit.
- `tests/test_api.py` — the flipped pin, the new parametrized header test, the
  `build.failed` slug assertion.
- `tests/test_browser.py` — the new `download name` step between `golden sweep` and
  `root_shape=bogus as today`.
- Pure totality tests — `tests/test_calc.py` or a params test file.
- `docs/architecture/http-api.md:43,93` — the new truth.
- `docs/architecture/decision_log.md` — the new `Lxx`.
- `docs/ideas/` — the retirement; `bench/RESULTS.md` — the readings.

</code_context>

<specifics>
## Specific Ideas

- "A name is a claim about the part": the suffix is decided by the predicate that built
  the part, so the record's `slug` for a refused or failed trochoid request still says
  what the part would have been (D-01, D-09).
- The browser proves the user-visible string (`suggested_filename`), not a header the
  Python test already reads; one build, one format (D-04, D-05).
- The step's cost is read and recorded, not estimated, but proportionately: three timed
  readings, not six gate runs (D-06).
- The `Lxx` is the record of what was read first — every consumer, the cache keys, the
  CLI's non-involvement, the doc-path correction (D-10).

</specifics>

<deferred>
## Deferred Ideas

None new — discussion stayed within phase scope. Not raised and not in scope: a default
output name from `slug()` for the CLI's `-o`; encoding `root_fillet` in the name
(`_trochoid_r0.5`, rejected by FEATURES `:227` as over-encoding).

</deferred>

---

*Phase: 22-download-name-carries-the-root*
*Context gathered: 2026-10-11*
