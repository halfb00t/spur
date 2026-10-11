# Phase 22: Download Name Carries the Root - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-11
**Phase:** 22-download-name-carries-the-root
**Areas discussed:** Suffix rule and totality, Browser proof of the name, Lxx and test pins

**Finding presented before the areas:** ROADMAP's "reuses Phase 21's `expect_download`
harness" does not hold — `grep expect_download tests/` is empty; Phase 21 asserts the
`#dl-stl` href and never clicks it. `#dl-stl` requests `quality=fine`. REQUIREMENTS.md's
`docs/http-api.md` is `docs/architecture/http-api.md`. Research found three consumers the
REQ list omits (`model.py:807`, `bench/export_cost.py:176`, `tests/test_model.py:2021`).

---

## Suffix rule and totality

### Decision 12 — which root does the suffix follow?

| Option | Description | Selected |
|--------|-------------|----------|
| Effective root (Recommended) | `_trochoid` only when `root_mode().mode == 'trochoid'`; 40-teeth request keeps today's name; third consumer of L38's predicate; local `calc` import in `slug()` | ✓ |
| Requested root | `root_shape == 'trochoid'`, pure string; names a root the part lacks at 40 teeth; contradicts REQ-slug-carries-effective-root | |

**User's choice:** Effective root
**Notes:** Cost shown: `profile()` + `root_mode()` 10–30 µs (19-09), zero solver work for a radial request.

### How does `slug()` stay total?

| Option | Description | Selected |
|--------|-------------|----------|
| No guard; prove by test (Recommended) | `root_mode` returns reasons, never raises on validated params (`cutter()`'s `ValueError` is pre-empted by Pydantic bounds); tests on a refused and an ignored request | ✓ |
| try/except, fall back to the radial name | Keeps the failure record alive but prints a possibly false name (L08) and hides a `calc` bug | |
| try/except, fall back to a marked name | Honest about failure but invents a third root value the roadmap excludes | |

**User's choice:** No guard; prove by test

### Where does the effective-root question get asked?

| Option | Description | Selected |
|--------|-------------|----------|
| Inside `slug()`, local import (Recommended) | Mirrors `_feasible` at `params.py:180`; `app.py`, `records.py`, `model.py` unchanged | ✓ |
| New `calc.effective_root(p)` helper | A named one-liner; a pass-through with one caller | |

**User's choice:** Inside `slug()`, local import

### Continue gate

| Option | Description | Selected |
|--------|-------------|----------|
| Next area | Lock the three answers; uncached repeated `slug()` calls are Claude's discretion | ✓ |
| More questions | e.g. the record's slug for a refused 23-tooth trochoid request | |

---

## Browser proof of the name

### How does the browser prove the name the user sees?

| Option | Description | Selected |
|--------|-------------|----------|
| Real click, `expect_download` (Recommended) | Set the 23-tooth trochoid hash, wait for the href, click `#dl-stl`, assert `suggested_filename`; one fine build on the gate's server | ✓ |
| `page.request.get(href)`, read header | Same server cost, no browser download event; duplicates the Python pin | |
| Route-capture only, no build | Asserts the href; the name is set by the server header — proves nothing SC1 asks | |

**User's choice:** Real click, `expect_download`

### Which download does the browser click?

| Option | Description | Selected |
|--------|-------------|----------|
| STL only (Recommended) | One fine build; STEP pinned in `test_api.py` on the same params | ✓ |
| STL and STEP | Two browser requests for a header the Python test already reads | |

**User's choice:** STL only

### How is the download step's gate cost recorded?

| Option | Description | Selected |
|--------|-------------|----------|
| Step timing only (Recommended) | Wall seconds printed by the step; three readings with host state in `bench/RESULTS.md`; Phase 25 absorbs it | ✓ |
| L39-style A/B, N=3 per arm | Six full-gate runs (~20 min); the whole-file admission precedent, disproportionate for one step | |
| No reading | Breaks "a gate cost is measured before it is accepted" for this change | |

**User's choice:** Step timing only

### Where does the download step sit in the scenario?

| Option | Description | Selected |
|--------|-------------|----------|
| New named step, after the sweep (Recommended) | `with step("download name")` between `golden sweep` and `root_shape=bogus as today` | ✓ |
| Extend `first build drawn` | Moves Phase 21's PNG-ratio bar and `data-triangles` reading onto another part | |

**User's choice:** New named step, after the sweep

### Continue gate

| Option | Description | Selected |
|--------|-------------|----------|
| Next area | Lock; `BUILD_WAIT_MS` and the hash are Claude's discretion | ✓ |
| More questions | e.g. saving the download and checking the STL header | |

---

## Lxx and test pins

### What does the `Lxx` list as consumers?

| Option | Description | Selected |
|--------|-------------|----------|
| Every call site, grepped (Recommended) | The REQ's four plus `model.py:807`, `bench/export_cost.py:176`, `tests/test_model.py:2021`, the four truthy asserts, `test_records.py` synthetic slugs, the CLI (unaffected), "no cache is keyed by slug"; doc path corrected | ✓ |
| The REQ's four only | Matches the requirement text; leaves three real call sites off the record | |

**User's choice:** Every call site, grepped

### Which formats does the 40-teeth ignored pin cover?

| Option | Description | Selected |
|--------|-------------|----------|
| STL and STEP, parametrized (Recommended) | Mirror `test_model_download`'s table; 23 and 40 teeth in both formats; `quality=preview` | ✓ |
| STL only | One header read; SC1 says "STL and STEP" for 23 teeth | |

**User's choice:** STL and STEP, parametrized

### Shape of the SC2 totality test?

| Option | Description | Selected |
|--------|-------------|----------|
| Pure `slug()` tests + one record assertion (Recommended) | `slug()` on `tip land gone` (pressure angle 33.5), 40 teeth, 23 teeth; `build.failed` test gains a trochoid-request variant asserting the record's `slug` | ✓ |
| Full record tests for every refusal reason | Five fixtures for one claim the pure tests prove | |

**User's choice:** Pure `slug()` tests + one record assertion

### Commit shape?

| Option | Description | Selected |
|--------|-------------|----------|
| One semantic commit (Recommended) | Code, pins, tests, browser step, doc, `Lxx`, idea retirement together; bench readings may follow in a second commit | ✓ |
| `Lxx` first, then code | Literal "written before the names move"; the entry could not cite the code sha; log is append-only | |

**User's choice:** One semantic commit

### Done gate

| Option | Description | Selected |
|--------|-------------|----------|
| I'm ready for context | Write CONTEXT.md and this log, commit, update STATE.md | ✓ |
| Explore more gray areas | e.g. the `Lxx`'s amendment targets | |

---

## Claude's Discretion

- Repeated `slug()` calls per request stay uncached.
- The browser step's hash, wait signal, timeout, and whether it also checks the STL body.
- Where the pure `slug()` tests live; whether the `build.failed` assertion is a new
  parametrize row or a sibling test, and its cache-dodging tooth count.
- The `Lxx` id and whether it amends L39 or only cites it.
- The `bench/RESULTS.md` subsection shape.

## Deferred Ideas

None new. Not raised: a CLI default output name from `slug()`; `root_fillet` in the name
(rejected by FEATURES `:227`).
