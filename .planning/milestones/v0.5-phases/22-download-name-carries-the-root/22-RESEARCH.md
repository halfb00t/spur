# Phase 22: Download Name Carries the Root - Research

**Researched:** 2026-10-11
**Domain:** one pure-Python method (`GearParams.slug()`), its consumers, and one Playwright download step
**Confidence:** HIGH (every claim below was read in the tree or run in this session; the three exceptions are tagged `[ASSUMED]`)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
Copied from `22-CONTEXT.md` `<decisions>`, shortened to the rule each one states. The full text, with
the rejected alternatives, is in CONTEXT.md and is not re-opened here.

- **D-01 (Decision 12): the suffix follows the effective root.** `slug()` appends `_trochoid` when
  `root_mode(p, profile(p), requested=p.root_shape, rho=p.root_fillet).mode == "trochoid"`, never from
  `p.root_shape` alone. A 40-tooth `root_shape=trochoid` request downloads under today's name. Rejected:
  the requested root.
- **D-02: no guard.** No `try/except` in `slug()`; totality is by construction and proved by test. Rejected:
  a fallback to the radial name on exception; a marked name such as `_root-unknown`.
- **D-03: the call lives inside `slug()` through a local import** (`from .calc import profile, root_mode`
  in the method body, the pattern `_feasible` uses). No `calc.effective_root()` helper. `app.py`,
  `records.py`, `model.py` are not edited.
- **D-04: a real click with `page.expect_download()`** on `#dl-stl` at 23 teeth `root_shape=trochoid`,
  asserting `suggested_filename == "spur_z23_m1.75_pa25_trochoid.stl"`. Rejected: `page.request.get(href)`;
  route-capture of the href.
- **D-05: STL only in the browser**; STEP is pinned in `tests/test_api.py`.
- **D-06: gate cost is the step's own timing**, three readings with host state in `bench/RESULTS.md` under
  `## Download name carries the root (Phase 22)`. No full-gate A/B.
- **D-07: a new named step after `golden sweep`, before `root_shape=bogus as today`**, in the single scenario
  function.
- **D-08: `tests/test_api.py` pins STL and STEP at both tooth counts, parametrized**, mirroring
  `test_model_download`'s `(fmt, ctype, magic)` table. The `:412` assertion flips and its docstring is
  rewritten; `:720` is not touched.
- **D-09: SC2 is pure `slug()` tests plus one record assertion**: `tip land gone`, 40 teeth trochoid and
  23 teeth trochoid; and the `build.failed` test gains a trochoid-request variant asserting the record's
  `slug`.
- **D-10: the `Lxx` lists every grepped consumer** (not the REQ's four), states that no cache is keyed by
  slug, and corrects `docs/http-api.md` to `docs/architecture/http-api.md`.
- **D-11: one semantic commit** carries `slug()`, both pins, the SC2 tests, the browser step, the doc, the
  `Lxx` and the idea retirement. `bench/RESULTS.md` readings may follow in a second commit.

### Claude's Discretion
- Multiple `slug()` calls per request stay uncached (`cached_property` is not worth the Pydantic interaction).
- The exact hash the browser step sets, the wait signal before the click, the `expect_download` timeout,
  whether the step saves the download and checks the STL header.
- Where the pure `slug()` tests live and whether they parametrize.
- Whether the `build.failed` slug assertion is a new parametrize row on `:1059` or a sibling test.
- The `Lxx` id and heading, and whether it amends L39 or only cites it.
- The `bench/RESULTS.md` subsection shape.

### Deferred Ideas (OUT OF SCOPE)
None new. Not raised and not in scope: a default output name from `slug()` for the CLI's `-o`; encoding
`root_fillet` in the name (`_trochoid_r0.5`, rejected by FEATURES `:227` as over-encoding).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-slug-carries-effective-root | `slug()` appends `_trochoid` only when `root_mode` applies the hob root; radial and ignored requests keep today's name byte for byte; `slug()` stays total; tested at z = 23 and z = 40 | Section "Verified facts" (the predicate, the 27-tooth threshold, the prototype run), "Code Examples" (the new body), Validation Architecture rows V1-V6 |
| REQ-slug-consumers-read-first | The `Lxx` lists every consumer of the old names before they move, records that no cache is keyed by slug, retires the idea in the same commit | "Consumer inventory" (the grep, re-run this session), "The Lxx and the retirement" |
</phase_requirements>

## Summary

The production change is three lines in `src/spur/params.py` (`slug()`), and it was prototyped and run in this
session on a scratch copy of the package (the repo tree is untouched, `git status` clean at `dc72f6c`). Every
consumer reaches the suffix through the one definition, so `app.py`, `records.py` and `model.py` need no edit.
The prototype gave `spur_z23_m1.75_pa25_trochoid` at 23 teeth, `spur_z40_m1.75_pa25` at 40, the radial default
unchanged, and it raised nothing over 17,567 valid cases of the project's own 31,446-case sweep grid. Through a
`TestClient` on the prototype, `Content-Disposition` read `spur_z23_m1.75_pa25_trochoid.{stl,step}` and
`spur_z40_m1.75_pa25.{stl,step}`. [VERIFIED: prototype runs in this session, scratchpad, see "Verified facts"]

CONTEXT.md is decision-complete and its references are almost all accurate. Four things need correcting before
planning, and one of them changes the shape of the browser step:

1. **The browser step must not run on the scenario's main `page`.** That page carries
   `serve_stl_from(page, stl)` (`tests/test_browser.py:373`), a `**/api/model.stl*` route that fulfils every STL
   request with the first build's bytes and no `Content-Disposition`. Clicking `#dl-stl` there downloads as
   `model.stl` (reproduced). The step needs a fresh `browser.new_page()` with no route, the way `golden sweep`
   and `link round trip` already use their own pages.
2. **A hash set after `page.goto("/")` can be lost** (1 of about a dozen unguarded runs ended on the default `api/model.stl`
   href for 40 s). Use `page.goto(base + "/#teeth=23&root_shape=trochoid")` or wait for the form first.
3. **`step()` lives in `tests/browser_session.py:373`, not `tests/test_browser.py:373`.** The scenario file is
   `tests/test_browser.py`; `tests/browser_scenarios.py` does not exist.
4. **D-11 (one commit) and "the entry is written with the shas in hand" cannot both hold for the sha of that
   same commit.** See Open Question 1.

**Primary recommendation:** edit `slug()` as in "Code Examples"; add the step on a fresh route-free page with
the hash in the `goto` URL and no extra route (the preview and the fine download share one solid build,
3.28 s for the whole step measured here); write L40 from the consumer grep in "Consumer inventory" before the
code moves.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Deciding the file name (`_trochoid` suffix) | API / Backend (`GearParams.slug()`) | — | One pure method on the model; the header, the records and the temp stem all call it |
| Applying the name as `Content-Disposition` | API / Backend (`app.py:496`) | — | Built per response, outside the byte cache; unchanged |
| Naming the file the user sees | Browser / Client | — | The browser derives `suggested_filename` from the response header; `app.js` has no `download` attribute and no name logic, and is not edited |
| The predicate "does the hob root apply" | API / Backend (`calc.root_mode`) | — | L38's single predicate; `slug()` becomes its third caller (after `derive()` and `model._build`) |
| Record `slug` field | API / Backend (`records._gear_fields`) | — | Calls `p.slug()`; unchanged |

## Standard Stack

No new package. Nothing is installed by this phase.

### Core (already in the tree)
| Library | Version | Purpose | Why |
|---------|---------|---------|-----|
| pydantic (frozen `GearParams`) | in `requirements.txt` | the model `slug()` lives on | `model_config = ConfigDict(frozen=True)` at `params.py:31` [VERIFIED: grep this session] |
| playwright | 1.63.0 | the download step | pinned exactly in `[dev]` (`pyproject.toml:29`: `"playwright==1.63.0",`); `playwright.__version__` does not exist, `pip list` reads `playwright 1.63.0` [VERIFIED: `.venv/bin/pip list`] |
| pytest 9.1.1, pytest-xdist 3.8.0, pytest-cov 7.1.0, mypy 2.3.1, ruff 0.16.8, import-linter 2.15 | — | the gate | [VERIFIED: `.venv/bin/pip list`] |

### Alternatives Considered
None: CONTEXT.md locks every choice. **Installation:** none.

## Package Legitimacy Audit

No external package is installed by this phase, so the gate (`gsd_run query package-legitimacy check`) has
nothing to check. `playwright==1.63.0` is already pinned and was admitted by Phase 21 (L39, REQ-browser-stack-pinned).

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Verified facts (the claims CONTEXT.md and the orchestrator asked to be checked)

All line numbers are against the working tree on branch `gsd/phase-22-download-name-carries-the-root`, HEAD
`dc72f6c`, clean.

### The code under change

| Claim | Result | Evidence |
|-------|--------|----------|
| `slug()` is at `params.py:190` | **Correct** | `params.py:190`: `def slug(self) -> str:`; `:191`: `"""Short, filename-safe identifier."""`; `:192`: `return f"spur_z{self.teeth}_m{self.module:g}_pa{self.pressure_angle:g}"` [VERIFIED: params.py:190-192] |
| `_feasible`'s local `calc` import is at `:180` | **Correct** | `params.py:179`: `def _feasible(self) -> GearParams:`; `:180`: `from .calc import check  # local import: calc only needs the attributes` [VERIFIED: params.py:179-180] |
| `GearParams` is frozen | **Correct** | `params.py:31`: `model_config = ConfigDict(frozen=True)` [VERIFIED] |
| `calc` imports `GearParams` for typing only (so a module-level import in `params.py` would be circular) | **Correct** | `calc.py:14-16`: `if TYPE_CHECKING:` ... `from .params import GearParams`; `calc.py:112` comment "calc.py imports params for typing only" [VERIFIED] |
| `root_mode` signature | **Correct** | `calc.py:1662-1663`: `def root_mode(p: GearParams, pr: Profile,` / `*, requested: RootShape = "radial", rho: float = 0.0) -> RootMode:` [VERIFIED: calc.py:1662-1663] |
| `RootMode.mode` values | `RootShape = Literal["radial", "trochoid"]` at `calc.py:1356`; `RootMode.mode: RootShape` at `:1654`; `reason` is `None` exactly when trochoid | [VERIFIED: calc.py:1356, 1653-1659] |
| `RootReason` values | `Literal["not requested", "nothing radial to replace", "tip land gone", "bracket degenerate", "curve invalid", "tooth severed"]` | [VERIFIED: calc.py:1357-1358] |
| `root_mode` returns at `requested != "trochoid"` before building the cutter | **Correct** | `calc.py:1690`: `if requested != "trochoid":` returns `RootMode("radial", "not requested", None)`; `:1692`: `c = cutter(p, rho)` [VERIFIED: calc.py:1690-1692] |
| The three existing callers pass `requested=p.root_shape, rho=p.root_fillet` | **Correct** | `calc.py:354`, `calc.py:1086`, `model.py:773`: `rm = root_mode(p, pr, requested=p.root_shape, rho=p.root_fillet)` [VERIFIED] |
| `profile(p, backlash=None)` | `calc.py:158`: `def profile(p: GearParams, backlash: float | None = None) -> Profile:` | [VERIFIED] |
| `Content-Disposition` at `app.py:496` | **Correct** | `headers = {"Content-Disposition": f'attachment; filename="{params.slug()}.{fmt}"',` [VERIFIED: app.py:496] |
| Export cache key | **Correct**, `app.py:401`: `key = (params, fmt, q.quality, encoding)`; the raw-key twin is `:418` `raw_key = (params, fmt, q.quality, "identity")` | [VERIFIED: app.py:401, 418] |
| `ModelQuery.quality` default is `"fine"` | **Correct** (field starts `:238`, the default literal is on `:239`): `"fine", description="STL tessellation: preview (coarse, small) or fine."` | [VERIFIED: app.py:238-239] |
| `records.py:180` `_gear_fields` | **Correct**: `return {"slug": p.slug(), "params": p.model_dump(exclude_defaults=True)}`; four emitters call it at `:218, 231, 255, 267` (`build_started`, `export_served`, `build_failed`, `queue_refused`) | [VERIFIED: records.py:180, 211-267] |
| Temp export stem `model.py:807` | **Correct**: `path = Path(d) / f"{p.slug()}.{fmt}"` | [VERIFIED: model.py:807] |
| `bench/export_cost.py:176`, `tests/test_model.py:2021` | **Correct**: both `f"{...slug()}.stl"` stems | [VERIFIED: grep] |
| CLI uses no slug | `grep -rn slug src` lists only `params.py:190`, `records.py:172,180`, `app.py:496`, `model.py:807`; `cli.py` is absent | [VERIFIED: grep this session] |

### The thresholds and the numbers

- **The hob root applies up to 26 teeth and is ignored from 27 on** at the default module (1.75), angle (25) and
  `root_fillet` (0.5), with the bore off. Output of the prototype for z = 14 to 31: `spur_z26_m1.75_pa25_trochoid`,
  `spur_z27_m1.75_pa25`. With the default 9 mm bore, z = 22 to 26 also validate. This agrees with the
  `test_a_root_shape_link...` docstring "from 27 teeth on at the default module and angle". [VERIFIED: prototype run]
- **Cost of the new `slug()`** (`timeit`, 2,000 calls, Apple M2 Max, load about 5, this session):
  radial default 2.3 us; 40 teeth ignored 5.3 us; `tip land gone` 5.3 us; 27 teeth ignored 5.2 us;
  **23 teeth trochoid 39.1 us**. CONTEXT.md quotes "10-30 us" from 19-09's `derive()`; the trochoid figure
  here is slightly above that range, still about 0.04 ms per call and under 0.2 ms per request with the five
  calls (two records, header, worker stem). The `Lxx` should quote these figures, not the 19-09 ones.
  [VERIFIED: measured]
- **Totality sweep.** `bench.trochoid.sweep_cases()` (31,446 cases) with `root_shape="trochoid"` and the case's
  `root_fillet`: 17,567 constructed a valid `GearParams` (13,879 did not: the added `root_fillet` or the gear
  is refused by validation, which never reaches `slug()`). On the 17,567: **0 raised**; 9,954 got `_trochoid`;
  the rest kept the plain name by reason (6,674 `nothing radial to replace`, 866 `tip land gone`, 73
  `tooth severed`); in every case `slug().endswith("_trochoid")` equals `root_mode(...).mode == "trochoid"`.
  1.7 s. [VERIFIED: scratch script `exp_total.py`]
- The prototype's `tip land gone` case (`teeth=19, module=1.75, profile_shift=-0.4, backlash=0.10,
  pressure_angle=33.5, root_shape=trochoid`, bore off) returns `spur_z19_m1.75_pa33.5`. The same fields are the
  `id="default-backlash-33.5-has-none"` row of `tests/test_trochoid.py` (the `pytest.param` is at `:176-179`,
  the test body whose `root_mode` call reads `requested="trochoid", rho=0.0` is at `:195`; CONTEXT.md's
  `:188` is the docstring region between them). The `_gear` helper that turns the bore off is at
  `tests/test_trochoid.py:85-88`: `{"bore_d": 0, "bore_flat": 0, "bore_chamfer": 0, "recess_sides": "none", **fields}`.
  [VERIFIED: test_trochoid.py:85-88, 176-179, 195]

### Drift in CONTEXT.md references (all minor)

| CONTEXT.md says | Actual |
|---|---|
| `step()` at `tests/test_browser.py:373` | `step()` is `tests/browser_session.py:373` (`@contextlib.contextmanager def step(name: str) -> Iterator[None]:`); `test_browser.py` imports it. In `test_browser.py`: `_api_get` `:107` OK, `_follow_link` `:170` OK, `first build drawn` `:328` OK, `golden sweep` `:526` OK, `root_shape=bogus as today` `:557` OK |
| "`tests/test_browser.py` / `tests/browser_scenarios.py`" (orchestrator's two names) | The scenario file is **`tests/test_browser.py`**; `tests/browser_scenarios.py` does not exist (`ls tests/`). Shared machinery is `tests/browser_session.py` (not collected) |
| `tests/test_trochoid.py:188` for the `tip land gone` params | The params are `:176-179`; `:188` is inside the docstring |
| `test_api.py:1059` for the `build.failed` test | Correct: `def test_a_failed_build_emits_build_failed_naming_the_class_and_the_level(` is `:1059`; its `teeth=71` request is `:1075` |
| "L39's 'one real build' sentence" | There is no such sentence in L39 (`grep` for it finds nothing). The invariant lives in code comments: `tests/browser_session.py::serve_stl_from` ("After the first real build every step builds nothing on the server") and `tests/test_browser.py:416`. The new step breaks that invariant, so those comments need a word (see Pitfall 4). L39 itself states no build count, so it can be cited rather than amended |
| The REQ's `docs/http-api.md` | Real path `docs/architecture/http-api.md` (`:43`, `:93`) [VERIFIED] |
| Next free `Lxx` | **L40**. `grep -n "^## L4" docs/architecture/decision_log.md` finds none; the last heading is `## L39 — A headless browser runs the shipped viewer ...` at `:2299`. No `L40`+ is reserved in `ROADMAP.md`, `REQUIREMENTS.md`, `STATE.md`, `PROJECT.md` or `docs/` (`grep`) [VERIFIED] |
| `spur_z` in the fixtures | `grep -c "spur_z" tests/regression/pre_v0_2.json tests/regression/golden_requests.json` gives `0` and `0`; `git diff --exit-code tests/regression/pre_v0_2.json` is clean now [VERIFIED] |

### Consumer inventory (the grep, re-run this session)

`grep -rn "slug\|Content-Disposition\|spur_z\|filename=" ...` over `src bench Makefile docs .github README.md tests`
(excluding `.venv`, `.planning`, `docs/tech_debt/resolved`):

| Consumer | Location | Moves? | Note |
|---|---|---|---|
| Definition | `params.py:190` | the edit | |
| `Content-Disposition` | `app.py:496` | name moves for effective-trochoid parts only | per response, outside the `_EXPORTS` byte cache |
| Record `slug` | `records.py:180` -> four emitters `:218, 231, 255, 267` | for effective-trochoid gears only | `params` is separate, unchanged |
| Worker temp stem | `model.py:807` | yes, invisible | a `tempfile` directory name |
| `bench/export_cost.py:176`, `tests/test_model.py:2021` | temp stems | yes, invisible | not pins |
| Doc | `docs/architecture/http-api.md:43` (`the bytes, with Content-Disposition from params.slug()`), `:93` (records carry "the gear's `slug`") | wording | `:43` needs the new truth stated |
| Pin that flips | `tests/test_api.py:412` `assert 'filename="spur_z23_m1.75_pa25.stl"' in ...`; the docstring at `:376`; `:411` (equality with the radial header) also becomes false and must go | deliberate | `:411` is an assertion CONTEXT.md does not mention: `assert r.headers["content-disposition"] == radial.headers["content-disposition"]` (the radial and trochoid headers will differ). Keep `:404` (the radial download) only if it still serves a purpose (`assert r.content != radial.content` at `:410` uses it) |
| Pin that must not move | `tests/test_api.py:720` `assert r.headers["content-disposition"] == f'attachment; filename="spur_z21_m1.75_pa25.{fmt}"'` | no | |
| Truthy `slug` asserts | `tests/test_api.py:797, 985, 1086, 1123` (`assert _field(..., "slug")`) | no | |
| Synthetic `spur_z19` | `tests/test_records.py:60, 89, 95` | no | not tied to `slug()` |
| `docs/review-2026-09-21.md:13` | names `Content-Disposition` as a thing checked | no | frozen history |
| `tests/test_browser_pins.py:52` | `filename=str(path)` is `ast.parse`, unrelated | no | |
| CLI | `-o` is the caller's name; `cli.py` has no slug use | no | |
| Frozen history | `.planning/**`, `docs/tech_debt/resolved/` | not edited | |

Caches: key `(params, fmt, q.quality, encoding)` at `app.py:401`; the solid cache `_build_cached` is keyed on the
`GearParams` object; none is keyed by slug. [VERIFIED: app.py:401; CONTEXT D-10 for `pool.py`]

## Architecture Patterns

### System Architecture Diagram

```
GET /api/model.stl?teeth=23&root_shape=trochoid
        |
        v
 FastAPI query model (ModelQuery) --422 if GearParams refuses--> (no slug is ever computed)
        |  _gear(q): plain GearParams (validated once, trusted after)
        v
 build_started(request, params) --> records._gear_fields(p) --> p.slug() --+
        |                                                                   |
  cache key (params, fmt, quality, encoding) -> hit? -> bytes               |
        | miss                                                              |
        v                                                                   |
 BuildPool worker -> model.export -> _write_export: temp stem p.slug() -----+-->  GearParams.slug()
        |  (BuildError / Timeout / BrokenProcessPool)                       |       |
        v                                                                   |       v
 build_failed(...) / queue_refused(...) --> _gear_fields(p) --> p.slug() ---+    spur.calc.profile(p)
        |                                                                           spur.calc.root_mode(p, pr,
 export_served(...) --> p.slug()                                                      requested=p.root_shape,
        |                                                                             rho=p.root_fillet).mode
        v                                                                           == "trochoid" ?  "_trochoid" : ""
 Response header: Content-Disposition: attachment; filename="<slug>.<fmt>"   (built at response time, after the cache)
        |
        v
 Browser: <a id="dl-stl" href="api/model.stl?..."> (no download attribute) -> navigation -> attachment -> Download event
          suggested_filename == slug + ".stl"
```

### Recommended change (files)
```
src/spur/params.py                       # slug(): the only production edit
tests/test_calc.py (or beside it)        # pure slug() tests: refused, ignored, applies, radial default
tests/test_api.py                        # flip :411-412 + docstring; new parametrized header test; build.failed slug
tests/test_browser.py                    # new step "download name" between golden sweep and bogus
tests/browser_session.py                 # comment only (BUILD_WAIT_MS slowest-step note; serve_stl_from invariant)
docs/architecture/http-api.md            # :43 (and :93 wording)
docs/architecture/decision_log.md        # L40
docs/ideas/ -> docs/ideas/retired/       # the retirement
bench/RESULTS.md                         # three readings (may be a second commit)
.planning/REQUIREMENTS.md, ROADMAP.md    # path correction docs/http-api.md -> docs/architecture/http-api.md (D-10)
```

### Pattern 1: the one definition (D-01, D-03)
**What:** compute the suffix from the same predicate that builds the part, via a local import.
**When to use:** only here. See "Code Examples".

### Pattern 2: a download step on its own page (D-04, D-07)
**What:** `browser.new_page()`, no STL route, hash in the `goto` URL, a content-based wait on the exact `href`,
then `with page.expect_download(timeout=BUILD_WAIT_MS) as download: page.click("#dl-stl")`.
**Why its own page:** the main `page` serves every STL request from a fixed byte string (Pitfall 1).

### Anti-Patterns to Avoid
- **`try/except` around the predicate** (rejected by D-02): a plausible name is a false claim (L08).
- **`p.root_shape == "trochoid"` as the test:** names a root the part may lack (SL-2).
- **A route on the download page that fulfils `**/api/model.stl*` unconditionally:** the download then has no
  `Content-Disposition` (Pitfall 1).
- **Setting `location.hash` immediately after `page.goto("/")`** (Pitfall 2).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| "Does the hob root apply" | a copy of `rb <= rf` and the tip-land test in `slug()` | `calc.root_mode(...)` | L38's single predicate; a copy drifts (the five `RootReason` branches include a solver) |
| The download event | `page.request.get(href)` header read, or a captured route | `page.expect_download()` + click | D-04: it is what the user sees; verified to fire (below) |
| Filename safety | an escaping layer | nothing | the name is `[A-Za-z0-9._]` plus the literal `_trochoid` (see Security) |
| Per-request name caching | `cached_property` / `lru_cache` | nothing | measured 2-39 us (D-01 discretion) |

## Runtime State Inventory

This is not a rename of a stored identifier, but the output name changes for effective-trochoid parts, so the
five categories are answered explicitly:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None. No datastore keys on the slug. The records are JSON lines on stderr, not stored by the app; the byte cache `_EXPORTS` is in memory, keyed `(params, fmt, quality, encoding)` (`app.py:401`) | none; the `Lxx` says log greps keyed on slug see a new value for effective-trochoid gears only |
| Live service config | None in the repo (no n8n, Datadog, Cloudflare config). `.github/workflows/ci.yml` and `required-jobs.txt` do not mention a slug (grep) | none |
| OS-registered state | None | none |
| Secrets and env vars | None reference a slug | none |
| Build artifacts / installed packages | None: the name is computed at request time. A running server must restart to pick up the edit (normal) | none |

## Common Pitfalls

### Pitfall 1: the click on the scenario's main page downloads `model.stl`
**What goes wrong:** the step reads `suggested_filename == "model.stl"` and the assertion fails with a message
that looks like a server bug.
**Why it happens:** `tests/test_browser.py:373` calls `serve_stl_from(page, stl)`, which installs
`page.route(STL_ROUTE, lambda route: route.fulfill(status=200, body=stl))` with `STL_ROUTE = "**/api/model.stl*"`
(`browser_session.py:38, 279-288`). The `<a href="api/model.stl?...">` navigation matches that glob, so the
response is the route's: no `Content-Disposition`, and Chromium derives the name from the URL path.
**Reproduced:** on a page with that route, `suggested_filename: model.stl`, URL
`.../api/model.stl?teeth=23&root_shape=trochoid`. [VERIFIED: scratch `exp_dl.py hazard`]
**How to avoid:** `fresh = browser.new_page()` (own context, no route), close it in a `finally` like `sweep_page`.
**Warning signs:** the filename is `model.stl` instead of `spur_z...`.

### Pitfall 2: a hash set after `goto("/")` can be erased before the form exists
**What goes wrong:** the wait on `#dl-stl[href]` times out (45 s) with the href stuck at `api/model.stl`
(the default part).
**Why it happens:** `app.js` registers `hashchange` at module top level (`:342`) but builds the form in an async
IIFE (`:366-373`: `await buildForm();` then `readHash();` then `update();`). A `hashchange` that fires before `buildForm`
returns runs `update()` with no fields; `update()` runs `history.replaceState(null, '', hash ? ... :
location.pathname + location.search)` (`:182`), which erases the fragment, and the later `readHash()` finds
none. [ASSUMED: the mechanism is read from `app.js`, not reproduced step by step; the symptom is observed]
**Observed:** 1 failure in about a dozen unguarded runs (`page.goto(base + "/")` then `page.evaluate("() => { location.hash = ... }")`),
the first run of the session; 8 passed. With `page.goto(base + "/#teeth=23&root_shape=trochoid")` (the
fresh-load path, no `hashchange`) 1 of 1 plus the pytest run passed; with a wait for 31 form fields before the
hash 1 of 1 passed. [VERIFIED: scratch runs; the sample is small]
**How to avoid:** put the fragment in the `goto` URL (what a shared link does), then wait on the exact
`href`; or wait `to_have_count(field_count)` first, as `form built` does. D-04 says "sets `location.hash`";
that is satisfied by either, and the exact hash is Claude's discretion.

### Pitfall 3: the wait must be on the exact href, not on a bare href
`expect(page.locator("#dl-stl")).to_have_attribute("href", "api/model.stl?teeth=23&root_shape=trochoid", ...)`.
`href` is set only after `showModel` returns (`app.js:212-213`: `showModel(buf);` then `setDownloads(q);`), and the
href carries no `quality` parameter (`setDownloads` builds `api/model.${kind}?${q}` from the form query, not from
`stlQ`), so the click requests `ModelQuery`'s default `quality=fine`. Query order is the form's, and
`teeth=23&root_shape=trochoid` was the observed href. [VERIFIED: app.js:155-167, 207-213; scratch run]

### Pitfall 4: the new step is build-bound and becomes the slowest one
The step's real cost is one 23-tooth trochoid build. Measured in a pytest process (`-n0 --no-cov -s`, M2 Max,
load about 5): `step download name: 3.28 s`, then `1 passed in 4.02s`. The preview STL (page load) builds the
solid; the fine download then re-meshes the same cached solid in about 0.13 s (click to download: 0.12-0.38 s over
7 runs; 2.72 s when the preview was faked and the fine request had to build). So the step is **about one build
plus a re-mesh**, not two builds. `tests/browser_session.py:41-47` records `first build drawn` as the "slowest
build-bound step" (2.53 s macOS, 4.75 s ubuntu-latest) and `BUILD_WAIT_MS = 45_000` rests on PD-04's 15 s rule.
This step reads above 2.53 s, so that comment is no longer true of macOS; it stays under 15 s, so
`BUILD_WAIT_MS` does not move. Edit the comment with this step's reading (comments carry the measurement).
The ubuntu-latest figure is not measured here. [VERIFIED: measured macOS; ubuntu-latest `[ASSUMED]` under 15 s]
Also update the `serve_stl_from` docstring/`:416` wording "after the first real build every step builds nothing".

### Pitfall 5: the group-floor assertion in `serve()`
`serve()` asserts at teardown that the process group still shows 3 members, "uvicorn plus the shipped pool"
(`browser_session.py:49-51, 195`). When a test body does no build, the floor fails (the scratch `hazard` run
failed there, "saw [..., ...]"). Not a risk for the real scenario, which builds first; it is a trap for any
scratch script. (There is open debt on the member set: `docs/tech_debt/active/2026-10-10-group-floor-of-3-is-not-two-pool-workers.md`.)

### Pitfall 6: the byte cache and the build-failed test
`_EXPORTS` is keyed on the whole `GearParams`, including `root_shape`. The `build.failed` test overrides the
backend with a raising one, so a count that any other test already downloaded (same params, fmt, quality) would
be answered from cache and the backend never runs. For the trochoid variant pick **teeth=25** with
`root_shape=trochoid`: `grep` finds no other `25` download in `tests/test_api.py`, `tests/test_pool.py` or
`tests/test_cli.py`; **teeth=26 is taken** (`tests/test_cli.py:646, 682` download `teeth=26, root_shape=trochoid`,
`quality=preview`); 23 is taken (`test_api.py:404-405`), 22 and 24 are used elsewhere in `test_api.py`
(`:851`, `:743`). 25 applies the hob root (the applies range is up to 26). [VERIFIED: grep; prototype threshold run]

### Pitfall 7: `filterwarnings = ["error", ...]`
Any warning on the download path fails the test. The scratch test with the real step ran under the repo's
`pyproject.toml` (`-c pyproject.toml --rootdir`) and passed with no warning. [VERIFIED: pytest run in this session]

## Code Examples

### `slug()` (D-01, D-03)
```python
# src/spur/params.py -- the only production edit
def slug(self) -> str:
    """Short, filename-safe identifier. Ends `_trochoid` exactly when the hob root is
    what gets built for these parameters (L38's predicate), not when it was asked for:
    a request `root_mode` ignores or refuses names the part it gets, which is radial."""
    from .calc import profile, root_mode  # local import: calc imports GearParams

    name = f"spur_z{self.teeth}_m{self.module:g}_pa{self.pressure_angle:g}"
    rm = root_mode(self, profile(self), requested=self.root_shape, rho=self.root_fillet)
    return f"{name}_trochoid" if rm.mode == "trochoid" else name
```
This body, with the same logic, produced every output quoted above. Add the measured cost (2.3 us radial,
5.3 us ignored/refused, 39 us applies) to the comment per `docs/CODING_VALUES.md`. [VERIFIED: prototype]

### `tests/test_api.py`: the header pins (D-08)
```python
@pytest.mark.parametrize(("fmt", "ctype", "magic"), [
    ("stl", "model/stl", None),
    ("step", "model/step", b"ISO-10303-21;"),
])
@pytest.mark.parametrize(("teeth", "stem"), [
    (23, "spur_z23_m1.75_pa25_trochoid"),   # the hob root applies
    (40, "spur_z40_m1.75_pa25"),            # ignored: nothing radial to replace
])
def test_the_download_name_carries_the_root_the_part_has(
        fmt: str, ctype: str, magic: bytes | None, teeth: int, stem: str) -> None:
    r = client.get(f"/api/model.{fmt}", params={"teeth": teeth, "root_shape": "trochoid",
                                                 "quality": "preview"})
    assert r.status_code == 200
    assert r.headers["content-type"] == ctype
    assert r.headers["content-disposition"] == f'attachment; filename="{stem}.{fmt}"'
```
Prototype run through `TestClient` + inline backend gave exactly these four headers (STL 0.71 s / 0.43 s,
STEP 0.06 s / 0.08 s, after the solid cache is warm; the whole test is about 1.3 s).
The existing `:412` assertion becomes `'filename="spur_z23_m1.75_pa25_trochoid.stl"' in ...` and `:411` (equality
with the radial header) must be removed or inverted (`!=`), because it is now false.

### The `build.failed` slug (D-09)
Reuse `test_a_failed_build_emits_build_failed_naming_the_class_and_the_level`'s override pattern
(`:1059-1100`); add a sibling (or a parametrize axis for the request) that sends
`{"quality": "preview", "teeth": 25, "root_shape": "trochoid"}` with `BuildError(...)` and asserts
`_field(failed[0], "slug") == "spur_z25_m1.75_pa25_trochoid"`. A literal, because a filename pin is one by
design (CONTEXT, Established Patterns). The record emitter calls `p.slug()` on the validated params, so this
passes with the same one-line change.

### The browser step (D-04, D-07), typed for `mypy --strict`
```python
with step("download name"):
    fresh = browser.new_page()   # not `page`: its STL route has no Content-Disposition
    try:
        fresh.goto(server + "/#teeth=23&root_shape=trochoid")
        expect(fresh.locator("#dl-stl")).to_have_attribute(
            "href", "api/model.stl?teeth=23&root_shape=trochoid", timeout=BUILD_WAIT_MS
        )
        with fresh.expect_download(timeout=BUILD_WAIT_MS) as download:
            fresh.click("#dl-stl")
        name = download.value.suggested_filename
    finally:
        fresh.close()
    assert name == "spur_z23_m1.75_pa25_trochoid.stl", f"the download is named {name!r}"
```
`Page.expect_download(predicate=None, *, timeout=None) -> EventContextManager["Download"]` and
`Download.suggested_filename -> str` (installed `playwright/sync_api/_generated.py:13233-13238, 7913`), so no
`Any` leaks and no `eval_*` wrapper is needed. `mypy --strict` over a file using exactly these calls reported
no error on them (the only error was the scratch file's own `browser_session` import path). The anchor has no
`download` attribute (`index.html:36`: `<a id="dl-stl" class="btn primary" aria-disabled="true">Download STL</a>`;
`app.js` never sets one, only `href`), and the click on it fired the Download event in headless Chromium in every run where
the page had no unconditional STL route (11 of 11, plus the conditional-route variant). [VERIFIED: installed package + runs]
Optionally print the wall seconds the way `first build drawn` prints its ratio; `step()` already prints
`step download name: N.NN s`.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `.venv` (Python 3.12) | everything | yes | 3.12 (`.venv/lib/python3.12`) | — |
| playwright | the browser step | yes | 1.63.0 | — |
| Chrome Headless Shell **for 1.63.0** (`chromium_headless_shell-1243`, browser 153.0.8010.12) | the browser step | **not in the repo's `.venv/ms-playwright`** (the directory does not exist yet) and **not in the host cache** `~/Library/Caches/ms-playwright`, which holds `chromium_headless_shell-1208` and `-1228` | installs in 23.1 s via `python -m playwright install --only-shell chromium` | `make test` / `make verify` run the install stamp (`$(BROWSER)`, `Makefile:91-92`) themselves; I installed it into the scratchpad `PLAYWRIGHT_BROWSERS_PATH`, not the repo |
| uvicorn, FastAPI TestClient | the browser step, `test_api.py` | yes | — | — |
| Docker | `make check` only | not probed | — | `make verify` needs none |

**Missing dependencies with no fallback:** none. The executor's first `make verify` / `make test` run installs
the shell (about 20 s, 198 MB). A bare `.venv/bin/python -m pytest tests/test_browser.py` without
`PLAYWRIGHT_BROWSERS_PATH=$(pwd)/.venv/ms-playwright` and without the stamp fails the test by design (the
message names `playwright install --only-shell chromium`); run browser tests through `make test`.

**Host differs from Phase 21's readings.** This session's host is an Apple M2 Max, 12 CPUs, load 5-6
(`sysctl`, `uptime`); Phase 21's readings in `bench/RESULTS.md` were on an Apple M5 Max, 18 CPUs. D-06's three
readings carry `bench.machine_facts()` and must not be compared with the 21-07 table.

## Validation Architecture

`.planning/config.json` has no `workflow.nyquist_validation` key (it holds only `workflow._auto_chain_active`,
`workflow.use_worktrees` and `git.branching_strategy`), so the section is included.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 + pytest-xdist 3.8.0 + pytest-cov 7.1.0; Playwright 1.63.0 for the browser file |
| Config file | `pyproject.toml` (`filterwarnings = ["error", "ignore::DeprecationWarning:starlette.*", "ignore:Using `httpx`"]`, `fail_under = 96` coverage) |
| Quick run command | `make test.fast` (commit slice, runs `tests/test_calc.py` and `tests/test_trochoid.py`, excludes `test_model/test_pool/test_api/test_cli/test_browser`) |
| Phase-targeted | `make test PYTEST_ARGS="tests/test_api.py tests/test_calc.py -n0 --no-cov -q"` and `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"` (the Phase 21 shape; `-s` prints the `step` lines in the main process only) |
| Full suite command | `make verify` (ruff, mypy `--strict`, import-linter, unfinished-work scan, pytest at `-n 8` with coverage) |

How the browser file is admitted to the gate: it is the module `tests/test_browser.py` with one test,
`test_the_shipped_viewer_in_a_real_browser`; it runs inside `make verify`'s `test` (the `$(BROWSER)` stamp is a
prerequisite of `test`), is excluded from `make test.fast` by `--ignore=tests/test_browser.py` (`Makefile:197`)
and from `make test-image` (`:218`), and `tests/test_hooks.py:25`
(`HEAVY_TEST_FILES = ("test_model", "test_pool", "test_api", "test_cli", "test_browser")`) pins both exclusions.
`tests/test_browser_pins.py` AST-scans every `tests/*browser*.py` for skip paths; a new `expect_download` step
uses none of the watched names. No gate wiring changes in this phase. [VERIFIED: Makefile, test_hooks.py,
test_browser_pins.py read]

### Phase Requirements -> Test Map

| ID | Success criterion | Behavior | Test type | Command | File exists? |
|----|-------------------|----------|-----------|---------|--------------|
| V1 | SC1 | z=23 `root_shape=trochoid` downloads as `..._trochoid`, STL and STEP | integration (`TestClient`) | `make test PYTEST_ARGS="tests/test_api.py -n0 --no-cov -q -k download_name"` | no, new (Wave 0 in the same commit) |
| V2 | SC1 | z=40 ignored request and the radial default keep today's name | integration | same test (z=40 rows) plus untouched `test_model_download` (`:712-720`) | yes (`:720`), z=40 rows new |
| V3 | SC1 | the flipped pin: `:412` now `..._trochoid.stl` | integration | `... -k test_a_root_shape_link_is_served_with_the_root_it_cut` | yes, edited |
| V4 | SC1 | the browser's own `suggested_filename` on the same link | e2e (real uvicorn + headless shell) | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"` | step new, file exists |
| V5 | SC2 | `slug()` is total: a name for a request `root_mode` refuses (`tip land gone`, angle 33.5) and for one it ignores (z=40) | unit (no kernel) | `make test.fast PYTEST_ARGS="-k slug"` or `make test PYTEST_ARGS="tests/test_calc.py -n0 --no-cov -q -k slug"` | no, new |
| V6 | SC2 | `build.failed` for a trochoid request carries its `slug` | integration (caplog) | `... tests/test_api.py -k build_failed` | sibling new |
| V7 | SC3 | fixture and golden pin untouched | git | `git diff --exit-code tests/regression/pre_v0_2.json tests/regression/golden_requests.json` | yes |
| V8 | SC3 | the `Lxx` lists the consumers and the cache statement; `docs/architecture/http-api.md` states the new truth; the idea file is moved and the INDEX row is in `## Retired` | doc review | `git diff --stat`; `grep -n "L40" docs/architecture/decision_log.md`; `test -f docs/ideas/retired/2026-10-08-download-name-carries-the-root-shape.md`; `grep -c "download-name" docs/ideas/INDEX.md` | n/a |

### What each is when red
- V1: with the old `slug()`, the header is `filename="spur_z23_m1.75_pa25.stl"` and the equality fails naming both strings.
- V2: a `slug()` that looks at `p.root_shape` alone (the rejected rule) fails the z=40 row with `..._trochoid` where today's name is expected.
- V4: on the main page (Pitfall 1) it fails with `model.stl`; on the old `slug()` it fails with `spur_z23_m1.75_pa25.stl`. Run it red once against `git stash`ed `slug()` and record it, as Phase 21 did (`### Seen red once`).
- V5: a `try/except`-less `slug()` that raised on a refused request would be an exception, not a name; also red if `slug()` returned the `_trochoid` name for the `tip land gone` case.
- V6: red if the record's `slug` were computed from the request (`_trochoid` appended for a refused request) or missing.
- V7: red on any change to the fixtures; `grep -c spur_z` is 0 in both files now.

### Sampling Rate
- **Per task commit:** `make verify.fast` (the commit hook runs it, under 30 s, L36; it covers V5) and the targeted pytest lines above.
- **Per wave merge:** the targeted `test_api.py` + `test_browser.py` runs.
- **Phase gate:** `make verify` green before `/gsd-verify-work`; state the command and its result line (CLAUDE.md).

### Wave 0 Gaps
- [ ] pure `slug()` tests (V5) in `tests/test_calc.py`, which imports `GearParams` and `spur.calc` already (`:58`, `:29`) and sits in the commit slice
- [ ] the parametrized header test (V1, V2), the `build.failed` sibling (V6) in `tests/test_api.py` (heavy file, excluded from the commit slice, so run it explicitly)
- [ ] the `download name` step (V4) in `tests/test_browser.py`
- No new framework, config or fixture file.

## Security Domain

`security_enforcement` is not set in `.planning/config.json`, so it is treated as enabled.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2/V3/V4 (auth, session, access) | no | the project has no authentication (known `nice` debt) |
| V5 Input Validation | yes | the name is built from validated fields only: `teeth` an int, `module` and `pressure_angle` floats formatted with `:g`, and a fixed literal `_trochoid`; validated once at the `GearParams` boundary |
| V6 Cryptography | no | — |
| V12 Files / Response headers | yes | `Content-Disposition: attachment; filename="..."` must not take attacker-controlled characters |

### Known Threat Patterns
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Header injection through the filename | Tampering | no free text reaches the name; `root_shape` is a `Literal["radial","trochoid"]` (`calc.py:1356`) and the suffix is a literal chosen by `root_mode`, not echoed from the request. `:g` on a bounded float can emit an exponent form (`1e-05`), still within `[A-Za-z0-9.+-]` |
| Wrong-name claim (L08) | Repudiation/Info | the name follows the effective root (D-01), so a file never claims a root the part lacks |

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `slug()` names teeth, module, angle only; the trochoid and radial parts share a name (19-RESEARCH Open Question 6) | name carries `_trochoid` when the hob root is built | this phase | only effective-trochoid downloads rename |

**Deprecated/outdated:** the docstring sentence at `tests/test_api.py:376` ("it ignores root_shape ...") becomes false and must be rewritten.

## The Lxx and the retirement

- **Id:** `L40`. Heading shape from L38/L39: `## L40 — The download name carries the root the part has, and no cache is keyed by slug (amends L38)`
  (title is Claude's discretion; whether it amends L39 is a non-question, L39 states no build count).
- **Body must carry** (D-10), in this order, written from the "Consumer inventory" table before the code moves:
  the consumers; that `:411`-`:412` flip while `:720` and the four truthy asserts do not; that no cache is keyed by
  slug (`app.py:401` key, the solid cache keyed on `GearParams`, `pool.py` routes by parameter hash, the header is
  built after the byte cache); the effective-vs-requested rule with its measured cost (2.3 / 5.3 / 39 us, M2 Max,
  load about 5, this session); totality by construction with the 17,567-case sweep result; that log greps on
  slug see a new value for effective-trochoid gears only; the CLI's non-involvement; the
  `docs/http-api.md` -> `docs/architecture/http-api.md` correction; the browser step's measured price
  (3.28 s, one build plus a re-mesh) and the fact that it runs on its own page.
- **Reversibility line** (CONTEXT D-01): costly.
- **Retirement shape** (precedent `docs/ideas/retired/2026-09-21-browser-test-for-the-viewer.md`, read this
  session): header lines `Status: retired` and `Retired in: <commit subject>` inserted after `Date:`; an
  `## Outcome` section at the end; `git mv docs/ideas/2026-10-08-download-name-carries-the-root-shape.md
  docs/ideas/retired/`; in `docs/ideas/INDEX.md` delete the row from `## Open` (it is the last row there) and add
  to `## Retired` a row `| 2026-10-08 | [The download's file name does not carry the root shape](retired/2026-10-08-download-name-carries-the-root-shape.md) | <commit subject> |`.
  The precedent file names no sha; the "sha" step in `CLAUDE.md` is for tech-debt items.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The lost-hash race of Pitfall 2 is caused by a `hashchange` before `buildForm` returns, with `update()`'s `replaceState` erasing the fragment | Pitfall 2 | Low: the recommended `goto(url#hash)` avoids the path in either case, and the symptom (1 in 9) is observed |
| A2 | The new step stays under 15 s on `ubuntu-latest` (4 vCPU, where `first build drawn` read 4.75 s) | Pitfall 4 | Low: `BUILD_WAIT_MS` (45 s) would still hold; the executor reads it at the first CI run (Phase 21's PR #33 is already merged to the branch history) |
| A3 | `expect_download` fires the same way in the Linux headless shell as on macOS | Pattern 2 | Low: same Chromium engine; the first CI run is the check |

## Open Questions

1. **D-11 "one commit" versus "the entry is written with the shas in hand".**
   - What we know: the single commit that adds L40 cannot cite its own sha; L38/L39 cite earlier plan commits
     because those phases had many. The idea precedent's `Retired in:` is the commit subject, not a sha.
   - What's unclear: whether the human wants L40 to cite `dc72f6c` (the base) only, or a second docs commit
     that adds the code sha.
   - Recommendation: cite the base `dc72f6c` and the measured figures in L40, put the commit subject in
     `Retired in:` (decide the subject text first, it is self-referential), and let the `bench/RESULTS.md`
     second commit (already permitted by D-11) be the only place a later sha appears.
2. **`tests/test_api.py:411`** (equality of the radial and trochoid `Content-Disposition`) is not mentioned in
   CONTEXT.md. It is false after the change; the plan must remove or invert it with `:412`. Recommendation: delete
   `:411` and keep the `r.content != radial.content` byte check (`:410`), which is how the test knows the cache
   did not answer both.
3. **Where the REQUIREMENTS.md / ROADMAP.md path correction lands.** D-10 says the `Lxx` corrects it; the files
   themselves (`REQUIREMENTS.md:107`, `ROADMAP.md` SC3 line) still say `docs/http-api.md`. Recommendation: edit
   both in the same commit; they are planning docs, not code.

## Project Constraints (from CLAUDE.md)

- The gate is `make verify`; state the command and the result line in the reply. `make check` needs Docker.
- Two standing rules: a printed number is a number someone cuts metal to (L08: the name is a claim about the
  part, here followed to the effective root); a parameter the user did not set must never silently change the
  part (L05: defaults unmoved, so every radial name is byte-identical).
- Stop and ask on an architectural claim not in the decision log, a locked decision that looks wrong, an
  unverified library behaviour after a real check, conflicting evidence. Flagged here: Open Question 1.
- New non-trivial choice -> a new `Lxx` (here L40). Ground claims in evidence; flag guesses `ASSUMPTION:`.
- Keep it simple: no helper, no cache, no guard (D-02, D-03); surgical edits; one concern per commit
  (D-11 is the human's call).
- New behaviour ships with its tests in the same change; performance claims are measured and recorded.
- No `TODO`, `pass` or unreachable branches (`make verify` scans for the markers).
- Comments explain why and carry the measurement. `calc.py` never imports `cadquery`; vendor types stop at
  their boundary; a parameter is validated once at the `GearParams` boundary; English throughout.
- Idea/debt filing: retire the idea in the closing commit (status, `git mv`, INDEX row). **This research filed
  no idea or debt item.** Candidate to file or fold into the plan: the stale "slowest build-bound step" comment
  (Pitfall 4) is a code-comment edit in the same change, not a debt item.
- Cross-CLI review: whoever wrote the diff does not review it.

## Sources

### Primary (HIGH confidence)
- The working tree at `dc72f6c`: `src/spur/params.py`, `calc.py`, `app.py`, `records.py`, `model.py`,
  `static/app.js`, `static/index.html`; `tests/test_api.py`, `test_browser.py`, `browser_session.py`,
  `test_browser_pins.py`, `test_hooks.py`, `test_trochoid.py`, `test_calc.py`, `test_cli.py`; `Makefile`;
  `pyproject.toml`; `docs/architecture/decision_log.md` (L38, L39), `http-api.md`; `docs/ideas/`;
  `bench/RESULTS.md` (21-07); `.planning/` CONTEXT, REQUIREMENTS, ROADMAP, research/ARCHITECTURE.md §6.
- The installed package `.venv/lib/python3.12/site-packages/playwright/sync_api/_generated.py` (1.63.0).
- Scratch runs in this session (prototype `slug()` on a copy of the package, `TestClient`, uvicorn + headless
  shell, pytest under the repo's `filterwarnings = error`); scripts and the copied package are in the session
  scratchpad, nothing under the repo was modified.

### Secondary / Tertiary
- None. No web source was needed: the question is internal to the repo and the installed package.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH, nothing new.
- Architecture: HIGH, the change was prototyped end to end and run.
- Pitfalls: HIGH for 1, 3-7 (reproduced or read); MEDIUM for 2 (symptom observed 1 in 9, cause read not reproduced).

**Research date:** 2026-10-11
**Valid until:** 2026-11-10, or until `slug()`, `root_mode()`, `app.js`'s `update()` or the Playwright pin moves.
