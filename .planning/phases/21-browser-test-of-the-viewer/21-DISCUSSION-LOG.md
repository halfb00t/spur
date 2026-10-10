# Phase 21: Browser Test of the Viewer - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-10
**Phase:** 21-browser-test-of-the-viewer
**Areas discussed:** Scene observable (decision 3), Browser install home, Golden request sweep, Server topology & A/B pricing

Carried forward from kickoff without re-litigation (REQUIREMENTS.md, 2026-10-10): decision 1
(O1 — inside `test`, excluded from `test.fast` / `test-image`), decision 2 (missing browser
is a hard failure, no opt-out), decision 4 (no `pytest-playwright`; exact `playwright` pin;
default headless shell). The user confirmed them by selecting the four areas below and not
reopening any.

---

## Scene observable (decision 3)

| Option | Description | Selected |
|--------|-------------|----------|
| `canvas.dataset.triangles` only | One line in `showModel` after `scene.add`; test reads uint32 at byte 80 of the same STL; init-script counter not built | ✓ |
| Init-script draw counter only | `page.add_init_script` wrapping `drawArrays`/`drawElements`; zero production change; ARCH flagged VERIFY IN SPIKE | |
| Both | Dataset line asserted; counter kept only if trivially green | |

**User's choice:** `canvas.dataset.triangles` only (recommended).
**Notes:** none.

| Option | Description | Selected |
|--------|-------------|----------|
| PNG byte-size ratio | `locator('#canvas').screenshot()` blank control vs after first build; bar set from the spike reading | ✓ |
| Distinct-pixel count in page | Decode via `Image` + 2D canvas in `page.evaluate`; typed wrapper needed | |
| Record both, assert ratio | Both readings in `bench/RESULTS.md`; only the ratio asserted | |

**User's choice:** PNG byte-size ratio (recommended).
**Notes:** none.

---

## Browser install home

| Option | Description | Selected |
|--------|-------------|----------|
| `PLAYWRIGHT_BROWSERS_PATH` under `.venv` | Makefile exports `$(VENV)/ms-playwright` for the stamp and for `test`; `make clean` removes it; bare pytest without the variable fails closed | ✓ |
| Shared cache + `--no-remove` | Default `ms-playwright` cache; GC opt-out by flag; bare pytest works; `make clean` leaves ~200 MB | |
| Under `.venv`, plus conftest sets the variable | Same isolation; `conftest.py` sets the path when unset; two places know it | |

**User's choice:** `PLAYWRIGHT_BROWSERS_PATH` under `.venv` (recommended).
**Notes:** none.

| Option | Description | Selected |
|--------|-------------|----------|
| Install command + the make path | Names `playwright install --only-shell chromium` with the gate's `PLAYWRIGHT_BROWSERS_PATH` spelled out, and says `make test` runs it | ✓ |
| Install command only | The REQ wording verbatim, no mention of make | |

**User's choice:** Install command + the make path (recommended).
**Notes:** none.

---

## Golden request sweep

| Option | Description | Selected |
|--------|-------------|----------|
| Route-captured, no builds | One page; `location.hash` per record; `page.route` captures `api/info?…` and aborts `api/model.stl` | ✓ |
| Real builds for every record | Same hash path with `api/model.stl` served; 44 preview builds per gate run | |
| Route-captured, plus one real build per bore family | Sweep as above plus a handful of real builds asserting `dataset.triangles` | |

**User's choice:** Route-captured, no builds (recommended).
**Notes:** none.

| Option | Description | Selected |
|--------|-------------|----------|
| Committed JSON + regen script | `tests/regression/golden_requests.json` keyed like `pre_v0_2.json`; capture script behind a make target; test asserts equality | ✓ |
| Python predictor, no file | Expected string derived from params in Python; a second `gearQuery()` | |
| Committed JSON, refreshed by the test itself | Test rewrites under a flag/env — an environment opt-out | |

**User's choice:** Committed JSON + regen script (recommended).
**Notes:** none.

---

## Server topology & A/B pricing

| Option | Description | Selected |
|--------|-------------|----------|
| One scenario test, one server | One test function walking every scenario; module fixture; one xdist worker, one `uvicorn` + one `BuildPool`; step names in assertion messages | ✓ |
| Several tests, server per worker | One test per REQ; up to 8 servers (~2–3 GiB RSS each) unless scheduling changes | |
| Several tests, one shared server via a lock file | Cross-worker election through a lock/port file | |

**User's choice:** One scenario test, one server (recommended).
**Notes:** none.

| Option | Description | Selected |
|--------|-------------|----------|
| Shipped default, 2 | No `SPUR_BUILD_WORKERS` override; ~2.9 GiB RSS; two children in the orphan check | ✓ |
| 1 | `SPUR_BUILD_WORKERS=1`; ~2.0 GiB; a shape the product does not run by default | |

**User's choice:** Shipped default, 2 (recommended).
**Notes:** none.

| Option | Description | Selected |
|--------|-------------|----------|
| N=3 per arm, interleaved | Six gate runs A/B/A/B/A/B; uptime before/after; flake runs listed apart, budget N+3; admits the file, sets no bar | ✓ |
| N=5 per arm, interleaved | Ten gate runs; PITFALLS GB-2's N≥5 with min/median/max | |

**User's choice:** N=3 per arm, interleaved (recommended).
**Notes:** none.

---

## Claude's Discretion

- Concrete scenario parameters for the invalid-field and warning checks (research names
  `#bore_hex=6` as the hex-link baseline).
- What `canvas.dataset.triangles` reads after a failed build.
- Whether the golden pin also records the `api/model.stl` query.
- Where the spike readings and deliberate-break evidence are recorded (`bench/RESULTS.md`
  precedent).
- Makefile target names, the `.gitignore` entry, how `ci.yml` passes `--with-deps`.
- Typed `page.evaluate` wrappers, `expect` timeout, content-based wait signals.

## Deferred Ideas

None new. The `#root_shape=bogus` behaviour is pinned and filed as debt in this phase per
REQUIREMENTS.md "Form follow-ups"; the init-script draw counter is rejected, not deferred.
