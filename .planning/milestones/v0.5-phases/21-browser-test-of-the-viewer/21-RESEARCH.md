# Phase 21: Browser Test of the Viewer - Research

**Researched:** 2026-10-10
**Domain:** Playwright (Python, sync API) driving the shipped vanilla-JS/three.js viewer against a real `uvicorn` subprocess, admitted into a Make/pytest-xdist/pre-commit gate
**Confidence:** HIGH on everything tagged `[VERIFIED: local run]` (run this session on the dev host, scratch venv, repo untouched); MEDIUM on Linux/CI (one `ubuntu:24.04` container, not a runner); LOW on anything `[ASSUMED]`.

**Evidence legend.** The milestone files tag figures MEASURED / READ / DOCS / ASSUMPTION; this file carries those tags through unchanged where it quotes them (`MEASURED (STACK)` etc.) and adds its own: `[VERIFIED: local run]` = executed this session on the host below, in a scratch venv under the session scratchpad (nothing installed into `.venv`, nothing written to the repo); `[VERIFIED: path:lines]` = file opened this session, values quoted; `[CITED: url]` = vendor docs fetched this session; `[ASSUMED]` = not verified here. The scratch prototype is not committed. Every number the phase needs as a bar is re-taken inside the repo by the spike, because "a number the tool prints is a number someone will cut metal to" (L08) applies to gate figures too.

Host for every local run: Apple M5 Max, 18 CPUs, 64 GiB, macOS arm64, Python 3.12.15, Playwright 1.63.0, Chrome Headless Shell 153.0.8010.12 (revision 1243), 1-minute load 5 to 15 during the session (10 logged-in users): **the host was never idle**, so every timing below is an upper bound, not a bar.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

### Kickoff decisions confirmed (REQUIREMENTS.md records them; no measurement contradicted them)
- **D-01:** **Decision 1 — O1.** `tests/test_browser.py` runs inside `make verify`'s `test`
  and CI's `test (3.12)`; excluded from `test.fast` and `test-image` by name;
  `tests/test_hooks.py`'s `HEAVY_TEST_FILES` (`tests/test_hooks.py:24`) extended in the same
  commit and seen red when the `--ignore` is missing. The A/B price (D-10) goes in front of
  the human before the phase closes; an order-of-magnitude contradiction of the 3.2–3.8 s
  research figure reopens this. — **Reversibility:** costly — undoing means O2/O3/O4, a
  superseding `Lxx`, and for O4 `required-jobs.txt` plus the GitHub ruleset.
- **D-02:** **Decision 2 — hard failure, no opt-out.** A missing headless shell fails the
  test; no `importorskip`, no skip marker, no environment variable, in CI or locally; a pin
  fails if one appears. Message wording is D-06.
- **D-03:** **Decision 4 — no `pytest-playwright`.** Plain `playwright` pinned exactly in
  the `[dev]` extra (`pyproject.toml:20`; 1.63.0 at research time); the default Chrome
  Headless Shell, never `channel="chromium"`; `mypy --strict` passes with typed wrappers
  around `page.evaluate`.

### The scene observable (decision 3)
- **D-04:** **`canvas.dataset.triangles` only — the init-script draw counter is not built.**
  One line in `showModel` (`app.js:303`) after `scene.add(mesh, edges)` writes the triangle
  count of the parsed geometry (STL from `STLLoader` is non-indexed, so
  `position.count / 3`). The test fetches the same `api/model.stl?…&quality=preview` the
  page loaded and compares against the uint32 at byte 80 of the binary STL. Rejected: the
  `page.add_init_script` wrapper over `drawArrays`/`drawElements` (ARCH flagged it VERIFY IN
  SPIKE; it couples the test to three.js's draw path and the `EdgesGeometry` overlay, and a
  failed spike would leave the phase without an observable); both (a second observable to
  maintain for no extra proof). — **Reversibility:** costly — the `Lxx` names this line as
  the milestone's one production change and Phases 23–24's browser assertions sit on it.
- **D-05:** **Canvas non-blank check is a PNG byte-size ratio.** `locator('#canvas').screenshot()`
  before the first build (the blank control, same page) and after; assert the ratio clears
  a bar set from the spike's own reading and recorded beside it in `bench/RESULTS.md`
  (research starting points, not bars: 38,908 B vs 3,393 B on SwiftShader). Compositor
  readback, so `preserveDrawingBuffer: false` is irrelevant. Rejected: distinct-pixel count
  decoded in-page (more code, a typed `evaluate` wrapper for one coarse check); recording
  both.

### Browser install home
- **D-06:** **The shell lives under `.venv`: the Makefile exports
  `PLAYWRIGHT_BROWSERS_PATH := $(VENV)/ms-playwright` for the install stamp and for `test`.**
  The host's `chromium-1228` (another project) is never touched, `make clean` removes the
  browser with the venv, CI starts empty anyway (no cache — Playwright's own docs). The
  install is a Makefile stamp depending on `$(STAMP)` and a prerequisite of `test` only,
  never of `verify.static` or `test.fast`; `--with-deps` reaches it as a make variable from
  `ci.yml` (the runner needs the apt libraries; `.venv` does not exist before `make verify`,
  so the install cannot be a separate CI step). Rejected: the shared cache with
  `--no-remove` (isolation hangs on a flag never being dropped; `make clean` leaves ~200 MB
  behind); `conftest.py` setting the variable when unset (two places would know the path).
  — **Reversibility:** reversible — one Makefile variable.
- **D-07:** **The red test names the install command and the make path.** The message
  carries `playwright install --only-shell chromium` (REQ-browser-fails-closed) with the
  `PLAYWRIGHT_BROWSERS_PATH` the gate uses spelled out, and says `make test` (the stamp)
  runs it. A developer who ran bare `.venv/bin/pytest tests/test_browser.py` without the
  variable sees why it missed — the fail-closed rule holds; the message explains it.

### Golden request sweep (REQ-browser-golden-request-sets)
- **D-08:** **Route-captured, no builds.** One page; for each of the 44 records in
  `tests/regression/pre_v0_2.json` (`records`, keyed by name, each with `params`) the test
  sets `location.hash` from the record's params (`hashchange` calls `readHash(); update()`
  directly, `app.js:340` — no debounce); `page.route` captures the `api/info?…` request URL
  and aborts `api/model.stl` so no preview build runs. The pinned value is the `api/info`
  query string the form sends (it includes `mate_teeth` where a record sets it — the
  `README:info-mate-40+mate=40` record goes through `mateInput`, not `fields`). The
  server's acceptance of every set is already proved by `tests/regression`. Rejected: 44
  real builds per gate run (unmeasured kernel cost for a proof the regression suite already
  carries); route-captured plus one real build per bore family (the scenario test already
  draws a real part; more builds buy no new proof).
- **D-09:** **The pin is a committed file with a regen script behind a make target.**
  `tests/regression/golden_requests.json`: one entry per fixture record under the same name
  as `pre_v0_2.json`, value the exact query string. Written by a capture script (precedent:
  `make fixture.regen` → `tests/regression/capture.py`; the new target needs the browser
  stamp, since the capture drives the real page); the browser test asserts equality.
  Phases 23–24 must show an empty diff on this file, and a deliberate change is a regen
  commit saying what moved and why. Rejected: a Python predictor re-implementing
  `gearQuery()` (a second implementation, and "committed before any form change" would
  mean only the predictor); the test rewriting the file under a flag (an environment
  opt-out, which this project refuses). — **Reversibility:** costly — Phases 23–24's
  "same fields are sent" proof is this file's empty diff.

### Server topology and the admission price
- **D-10:** **One scenario test function, one server per gate run.** `tests/test_browser.py`
  holds one test walking every scenario in order — `webgl2` asserted first, then
  form-from-schema, first build drawn, invalid field marked, warning rendered, link round
  trip on all three paths, the golden sweep, the `#root_shape=bogus` pin — with a
  module-scoped fixture for the `uvicorn` subprocess. Under the current `--dist load` it
  lands on one xdist worker, so one `uvicorn` and one `BuildPool`; each step's assertion
  message carries the step name so a red line still says what broke. No scheduling change
  (`xdist_group` is a no-op under `--dist load`; changing scheduling is a gate-time change
  the roadmap flags for plan-phase and this choice avoids). Rejected: one test per REQ
  with a per-worker server (up to 8 `uvicorn`+`BuildPool` subprocesses, ~2–3 GiB RSS each,
  on a 4-vCPU runner); a cross-worker shared server through a lock file (coordination code
  in the fixture for readable red lines the step names already give).
- **D-11:** **The test server runs the pool the product ships: `SPUR_BUILD_WORKERS` at its
  default of 2**, no override in the fixture's environment (~2.9 GiB RSS at N=2, research
  memory read). The no-orphan check after `killpg` covers both children. Rejected: 1 (a
  shape the product does not run by default).
- **D-12:** **The admission A/B reading is N=3 per arm, interleaved.** Six full-gate runs,
  A/B/A/B/A/B (with and without `tests/test_browser.py`), `uptime` before and after each,
  host, load and `HEAD` beside each figure; flake-failed runs (the resource-tracker `must`
  debt, four recorded occurrences) are listed apart, classified, and re-run with a budget
  of N+3 attempts — never dropped silently, never a `filterwarnings` entry. This reading
  admits the file and sets no bar; Phase 25 sets the bar under its own pre-registered rule.
  Rejected: N=5 per arm (ten runs, ~32 min at the 193 s mean, for a reading that only
  admits).

### Claude's Discretion
- The concrete scenario parameters: which out-of-range value marks which field, and which
  warning-producing link is compared for equality against `/api/info`. The research names
  `#bore_hex=6` (warns every time on default `bore_d`/`bore_flat`) as the hex-link golden
  baseline; the planner picks and records the parameters.
- What `canvas.dataset.triangles` reads after a failed build. Leaving the previous count in
  place matches the status text "Showing the last valid gear"; the planner decides and the
  test asserts whatever is chosen.
- Whether the golden pin also records the `api/model.stl` query (`q` plus
  `quality=preview`) beside the `api/info` query, or derives it.
- Where the spike's readings and the deliberate-break evidence ("each assertion seen red
  once") are recorded — `bench/RESULTS.md` sections with host state are the precedent
  (`### The gate, priced (19-09)`).
- The exact Makefile names (`$(BROWSER)` stamp, the regen target, a `test.ui` convenience
  target if any), the `.gitignore` entry for browser artifacts, and how `ci.yml` passes
  `--with-deps`.
- The typed-wrapper shape around `page.evaluate`, the `expect` default timeout, and the
  wait signals — content-based (a rendered field count, a status text, a non-empty
  `#dl-stl[href]` set after `showModel` returns), never an empty status or a bare href
  (both pass before the 350 ms debounce fires).

### Deferred Ideas (OUT OF SCOPE)
None new — discussion stayed within phase scope. Already deferred by REQUIREMENTS.md "Form
follow-ups" and touched here only as pins: the `#root_shape=bogus` blank-select behaviour
(pinned, filed as debt in this phase, not fixed); the stale-response test under a slow
build; re-sweeping the xdist knee on the 18-CPU host. The init-script draw counter is
rejected (D-04), not deferred.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-browser-server-fixture | Real `uvicorn` subprocess, pre-bound `127.0.0.1` socket via `--fd`, `start_new_session=True`, `killpg` teardown, no surviving `BuildPool` child | Fixture pattern verified end to end incl. uvicorn 0.53.0 (the CI pin); orphan check design and its macOS EPERM trap; leader-only kill left 2 survivors >= 10 s, `killpg` 0.22 s (Pitfalls P2, P3; Code Examples 1) |
| REQ-browser-form-from-schema | Rendered groups/fields equal `/api/schema` in order, counts read at test time, CSS custom properties non-empty | Expected order derivable from schema (`group` key, first-appearance order); property names quoted from `app.js:274,282-284`; verified 31 fields = schema (Code Examples 4) |
| REQ-browser-first-build-drawn | webgl2 asserted first; `#dl-stl` href only after `showModel`; canvas non-blank vs blank control; `canvas.dataset.triangles` == STL header | Parked-route blank control; 3,917 B vs 38,908 B (9.93x); dataset line verified equal to STL header (9066 == 9066) and retained after a 422; truncated-STL scenario proves href ordering (Code Examples 2, 5, 6) |
| REQ-browser-invalid-field-marked | Out-of-range value marks its field via `detail[].ctx.fields`; message names the field | `ctx.fields` exists only on `infeasible` errors (`params.py:184-187`); `#bore_flat=3` is the single-field `ctx.fields` case (measured), `#teeth=2` goes through `loc[1]` instead (Pitfall P8) |
| REQ-browser-warning-rendered | Warning-producing link renders exactly `/api/info` `warnings` | `#module=1&pressure_angle=14.5` (two warnings) and `#bore_hex=6` (one) measured; equality of ordered lists; STL must NOT be aborted or `fail()` wipes the warnings (Pitfall P7) |
| REQ-browser-link-round-trip | Every hash field reaches the form; query equals hash on fresh load, Reset, `hashchange`; debounce waited out on content | Same-hash assignment fires no `hashchange` (Pitfall P5); query is schema-ordered with defaults dropped, so compare as pair sets; wait signals table (Pitfall P6) |
| REQ-browser-golden-request-sets | Pin the `api/info` query for each of the 44 records | Sweep measured: 43 non-empty records in 0.09 to 0.15 s, 44 distinct queries, 16 of 43 differ from the raw params; the `{}` record needs the fresh-load capture (Pitfall P5; Code Examples 7) |
| REQ-browser-fails-closed | Missing shell fails with a message naming `playwright install --only-shell chromium`; no skip/opt-out; pin fails if one appears | Playwright's own error says only `playwright install`; the test must catch `playwright.sync_api.Error` and `pytest.fail`; static pin design in a light file (Code Examples 3; Validation) |
| REQ-browser-in-the-gate | Inside `make verify`/CI, excluded from `test.fast`/`test-image` by name, `HEAVY_TEST_FILES` pin, A/B cost, one `Lxx` | `make -n` hazard in `test_hooks.py` verified and fixed with `make -n -o <stamp>`; ordering hazard for the exclusion commit (Pitfall P1, Open Questions 1); Makefile stamp skeleton; A/B protocol |
| REQ-browser-stack-pinned | Exact `playwright` pin in `[dev]`, no `pytest-playwright`, default shell, Linux path on a real runner, strict mypy with typed wrappers | mypy 2.4.0 strict + `disallow_any_explicit` passes with wrappers, fails (`no-any-return`) without; ruff 0.16.10 findings; Linux container run through `sudo` (67 s) (Standard Stack; Code Examples 3) |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

Extracted from `/Users/half/git/halfb00t/spur/CLAUDE.md` (a symlink to `AGENTS.md`), treated with the authority of locked decisions:

- **The gate is `make verify`** (ruff, `mypy --strict`, import-boundary contracts, unfinished-work scan, pytest). State the command and the result line in every reply; predicting is not running. `make check` adds Docker-only checks.
- **Python 3.12 only** (L23); stack is locked in `docs/architecture/decision_log.md` (cite by `Lxx`).
- **Stop and ask** when: an architectural claim is not in the decision log; a locked decision looks wrong; library behaviour is unverified after a real check; evidence conflicts; a destructive operation is involved; a choice trades stability for speed.
- **Two standing rules:** a printed number is one someone will cut metal to (L08); a parameter the user did not set must never silently change the part, defaults stay put (L05), a direct conflict is a `422` (L03).
- **Simplest thing that works**, surgical edits, one concern per commit, Conventional Commits in normal prose (not caveman).
- **New behaviour ships with its tests in the same change.** Performance and memory claims are measured and recorded. No `TODO`/`FIXME`/`XXX`/`HACK`/`NotImplementedError`, no `pass`/unreachable branches (`make verify` greps the markers in `*.py`, `*.js`, `*.sh`).
- **Debt and ideas live in files** (`docs/tech_debt/active/`, `docs/ideas/`, from `TEMPLATE.md`, INDEX row in the same commit); retire an item only in the commit that closes it (status, sha, `git mv`, INDEX row). State at the end of the reply whether any item was filed and its path. **Blocker severity: fix now or stop and ask.**
- **Code style** (`docs/CODING_VALUES.md`, read): comments carry the measurement or the constraint; `calc.py` never imports `cadquery`; vendor types stop at their boundary; English throughout; `Any` is not written (L21, `disallow_any_explicit`); a new dependency is a decision, ask first (already taken: D-03); prefer the standard library.
- **No `filterwarnings` entry** for the resource-tracker flake (REQUIREMENTS, CONTEXT D-12).
- **Project skills:** `.ai_skills/` holds only `README.md` (no skills); `.claude/skills/` holds only `README.md`. Nothing to load.

## Summary

The browser test is a small amount of test code on top of a stack that works first try: Playwright 1.63.0 (sync API), the default Chrome Headless Shell on SwiftShader, a `uvicorn` subprocess on a pre-bound socket, one scenario test. I built and ran a prototype of the whole scenario (webgl2, form-from-schema, parked-route blank control, first build, 422 marks on both paths, warning equality, truncated STL, the 43-record sweep, Reset, a patched `app.js` with the `canvas.dataset.triangles` line) in a scratch venv with the project's own pytest config (`filterwarnings = error`, `--strict-markers`) and with `--cov` under the project's `concurrency = ["multiprocessing", "thread"]`: it passes, produces no warning, loses no coverage for tests that run after it on the same worker, and costs 4.4 to 6.9 s `-n0` at a host load of 7 to 8. That is the same order of magnitude as the 3.2 to 3.8 s research figure, so D-01's "order of magnitude" reopen trigger is not near.

What the prototype found that the milestone files did not: (1) adding `$(BROWSER)` as a prerequisite of `test` makes `make -n verify` print the install recipe whenever the stamp is absent or stale, which breaks `tests/test_hooks.py`'s `whole_static == fast_static` assertion inside the commit-time slice on any machine that has run `verify.fast` but not `test`; `make -n -o <stamp>` fixes it (verified). (2) A `location.hash` assignment equal to the current fragment fires no `hashchange`, so the `{}` record (empty hash) hangs the sweep until its timeout; capture that record from the fresh-load request and fail fast on any other equal-hash case. (3) `ctx.fields` is set only by the model validator (`params.py:184-187`), so the roadmap's "out-of-range value marks its field through `ctx.fields`" is `#bore_flat=3`, not `#teeth=2` (which goes through `loc[1]`). (4) Aborting `api/model.stl` makes `fail()` replace the warnings with "Request failed", so the warning scenario must let the real build run. (5) Playwright's missing-browser error says `playwright install`, not `--only-shell chromium`, so the test must catch it and re-raise with the required wording. (6) The commit hook runs `make verify.fast`, which collects any `tests/test_*.py` it finds: the exclusion edits must land in or before the commit that adds `tests/test_browser.py` (Open Question 1 on how to honour the roadmap's order).

**Primary recommendation:** Build exactly what CONTEXT D-01 to D-12 lock: one module-scoped subprocess server (pre-bound `127.0.0.1` socket, `--fd`, new session, process-group kill, `ps`-based no-survivor check), one browser launched inside the test body so a missing shell is a `FAILED` with the required wording, one scenario test with step-named assertion messages, route-captured sweep with the `{}` record taken from the fresh load, the single `canvas.dataset.triangles` line, an absolute-path `PLAYWRIGHT_BROWSERS_PATH` under `.venv`, `make -n -o` in `test_hooks.py`, and take every bar from a reading recorded in `bench/RESULTS.md`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Form generated from the schema | Browser (`app.js` `buildForm`) | API (`/api/schema` = `GearParams.model_json_schema()`) | L02: the model owns the schema, the page renders it; the test reads both and compares |
| 422 marking and message rendering | Browser (`problems()`, `showMessages`) | API (`detail[].ctx.fields`, built in `params.py:_feasible`) | The shape is produced server-side, consumed client-side; only a browser sees the consumer |
| Warning text | API (`derive().warnings`) | Browser (`renderInfo`) | The test asserts the browser shows exactly what the API returned |
| Hash <-> form <-> query round trip | Browser (`readHash`, `gearQuery`, `update`) | API (the receiving `/api/info`) | Pure client logic; the server is only the capture target |
| Triangle count of the drawn part | Browser (new `showModel` line) | API (STL header, byte 80) | The only scene observable; compared with the bytes the server served |
| Build execution | API process + `BuildPool` workers | Test process (waits, never builds) | L17/L18: the serving process never imports the kernel; the test uses the product's real pool (D-11) |
| Headless browser lifecycle | Test process (Playwright driver, bundled Node) | Makefile stamp (install) | Test-time only; L11's "no Node at runtime" concerns the shipped image |
| Gate admission and slicing | Makefile + `tests/test_hooks.py` pins | `ci.yml` (install args) | L13/L36: one definition of passing; exclusion by name, never a marker |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `playwright` (Python) | `==1.63.0` [CITED: pypi.org/pypi/playwright/json, latest per `pip index versions` this session] [WARNING: flagged as suspicious by the legitimacy seam (too-new, unknown-downloads, no-repository) - evidence below; the human locked it in D-03, the planner still adds a `checkpoint:human-verify` before the first install] | Browser driver, auto-waiting `expect`, route capture | Microsoft's official binding; 85 releases since 2021-02-24; pure wheels for macOS arm64 and manylinux; ships `py.typed`; bundles its Node driver so L11 is untouched |
| Chrome Headless Shell | `153.0.8010.12` (Playwright revision 1243) [VERIFIED: local run, `browser.version`] | The browser | Default for `headless=True`; WebGL2 on SwiftShader on both OSes with no flags; 198 MB isolated |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pyee` | 13.0.1 (transitive) [VERIFIED: local run `pip list`] | Playwright event emitter | Pulled by `playwright`; `pyee>=13,<14` per STACK |
| `greenlet` | 3.5.6 (transitive) [VERIFIED: local run `pip list`] | Sync-API dispatcher | Pulled by `playwright`; coverage + `filterwarnings=error` + greenlet verified clean (Pitfall P11) |
| `pytest-xdist` / `pytest-cov` | already in `[dev]` | Gate workers and floor | Unchanged |
| stdlib `socket`, `subprocess`, `signal`, `tempfile`, `urllib.request`, `struct`, `json` | stdlib | Fixture, STL header, schema fetch | Prefer the standard library (CODING_VALUES) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| plain `playwright` | `pytest-playwright 0.10.0` | Rejected by D-03: autoloads suite-wide, drags `python-slugify` and `text-unidecode` |
| default headless shell | `channel="chromium"` | Never: renders on the host GPU (Apple Metal here), dev and CI would differ (MEASURED, STACK) |
| subprocess server | in-process uvicorn thread | Rejected: `app` is a singleton shared with `TestClient` tests (READ, ARCH 3.1) |
| PNG byte ratio | pixel count in page | Rejected by D-05 |

**Installation** (the gate does this; humans never type it):
```bash
# pyproject.toml [project.optional-dependencies].dev gains one exact line:
#     "playwright==1.63.0",
make test          # $(STAMP) installs the wheel, $(BROWSER) installs the shell under $(VENV)/ms-playwright
```
**Version verification:** `pip index versions playwright` printed `playwright (1.63.0)` as LATEST [VERIFIED: local run, 2026-10-10]. PyPI JSON: author "Microsoft Corporation", project URL `https://github.com/Microsoft/playwright-python`, first upload 2021-02-24, 85 releases, files include `playwright-1.63.0-py3-none-macosx_11_0_arm64.whl` (42.9 MB) and `playwright-1.63.0-py3-none-manylinux1_x86_64.whl` (48.2 MB) [VERIFIED: local run, PyPI JSON].

**Install timings** [VERIFIED: local run]: macOS arm64, `PLAYWRIGHT_BROWSERS_PATH=<scratch>/ms-playwright python -m playwright install --only-shell chromium` = 16.4 s, 198 MB (`chromium_headless_shell-1243` + `ffmpeg-1011`); the host's `~/Library/Caches/ms-playwright` still held exactly `chromium_headless_shell-1228`, `chromium-1228`, `ffmpeg-1011` afterwards (D-06's isolation keeps the other project's browser). `ubuntu:24.04` linux/amd64 container (OrbStack), **non-root user with passwordless sudo**: `playwright install --with-deps --only-shell chromium` = 67 s total, WebGL2 `ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (Subzero) ...))`. Playwright escalated through `sudo` by itself; this is a container, not a runner (SC5 still needs the real run).

## Package Legitimacy Audit

Ran `query package-legitimacy check --ecosystem pypi playwright pyee greenlet` [VERIFIED: local run]:

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `playwright` | PyPI | first upload 2021-02-24, 85 releases, latest 2026-09-15 | unknown to the seam (PyPI JSON carries none) | `github.com/Microsoft/playwright-python` in `project_urls` (seam read `repoUrl: null`) | SUS (`too-new`, `unknown-downloads`, `no-repository`) | Keep, flagged: seam signals are metadata gaps and a 3-week-old latest release, not a name-squat; the human chose it (D-03). Planner adds `checkpoint:human-verify` before the first install (confirm `playwright==1.63.0`, publisher Microsoft) |
| `pyee` | PyPI | latest 2026-08-13 | unknown | not read by seam | SUS (`unknown-downloads`, `no-repository`) | Transitive of `playwright` (`pyee>=13,<14`); covered by the same checkpoint (review `pip install --dry-run` output) |
| `greenlet` | PyPI | latest 2026-09-14 | unknown | `greenlet.readthedocs.io` | SUS (`too-new`, `unknown-downloads`) | Transitive of `playwright`; same checkpoint |

**Packages removed due to SLOP verdict:** none.
**Packages flagged SUS:** `playwright`, `pyee`, `greenlet` (planner inserts one `checkpoint:human-verify` before the pin lands; none of the three enters `requirements.txt`, the Dockerfile or `refresh-requirements.sh`). Registry check ran on the right ecosystem (`pip index versions`); PyPI packages have no `postinstall`.

## Architecture Patterns

### System Architecture Diagram

```
 make test / make verify                          (PLAYWRIGHT_BROWSERS_PATH = abs($(VENV))/ms-playwright)
   |
   |-- $(STAMP): pip install -e '.[dev]'  (+ playwright==1.63.0)
   |-- $(BROWSER): python -m playwright install [--with-deps] --only-shell chromium
   v
 pytest -n 8 --cov  ---> xdist worker gwK (the ONE worker that receives test_the_viewer)
                          |
   module fixture `server`|  bind 127.0.0.1:0, listen --> Popen(python -m uvicorn spur.app:app --fd N,
                          |        pass_fds, start_new_session=True, env minus SPUR_*, log -> tempfile)
                          |        poll /api/health until "pool" is non-null  (0.18-0.24 s measured)
                          |           uvicorn --> BuildPool (2 spawn workers) --> kernel
                          |  (teardown) killpg(TERM) -> wait -> ps-scan the group -> killpg(KILL) if any
                          v
   test body              launch Chrome Headless Shell (catch Error -> pytest.fail with required wording)
                          |  step 0  webgl2 context non-null           (else: no form at all, app.js:229)
                          |  step 1  schema vs DOM (groups, names, order, CSS vars)
                          |  step 2  park api/model.stl -> blank canvas PNG -> release -> drawn PNG
                          |          wait #dl-stl[href]; dataset.triangles == STL header(byte 80)
                          |  step 3  422 marks:  #bore_flat=3 (ctx.fields)  [#teeth=2 (loc[1])]
                          |  step 4  warning equality vs /api/info.warnings (real build, STL NOT aborted)
                          |  step 5  round trip: fresh load / Reset / hashchange   (request-URL content waits)
                          |  step 6  golden sweep: 44 records -> api/info query -> == golden_requests.json
                          |  step 7  #root_shape=bogus pin
                          v
   golden_requests.json <--- regen: make <target> -> tests/<capture script> (same sweep helper) --> git diff
```

### Recommended Project Structure
```
tests/
├── test_browser.py             # NEW  heavy tier: the module `server` fixture + ONE scenario test
├── browser_session.py          # NEW  (assumed) not collected: server start/stop, shell launch, typed wrappers, sweep()
├── capture_requests.py         # NEW  (assumed) regen script; shares sweep() with the test; run as `python tests/capture_requests.py`
├── test_browser_pins.py        # NEW  (assumed) light tier, imports no playwright: no-skip / no-opt-out / stack pins
├── test_hooks.py               # MOD  HEAVY_TEST_FILES += "test_browser"; make -n -o <stamp>; test-image pin
└── regression/golden_requests.json   # NEW  44 entries, name -> exact api/info query string
Makefile  .github/workflows/ci.yml  pyproject.toml  .gitignore  .pre-commit-config.yaml (comment)  # MOD
src/spur/static/app.js              # MOD  one line (canvas.dataset.triangles)
docs/{architecture/decision_log.md,architecture/web-ui.md,ideas/*,tech_debt/*}  bench/RESULTS.md   # MOD / NEW
```
A flat helper beside the test (like `composition.py`) avoids `sys.path` games: `tests/` is on `sys.path` under pytest's default import mode, and `python tests/capture_requests.py` puts `tests/` first. `tests/regression/capture.py` imports its sibling `corpus` the same way. [ASSUMED: file names and the flat layout are a recommendation; `bench/trochoid.py:575` is the precedent for inserting `tests/` on `sys.path` if the planner prefers the script under `tests/regression/`.]

### Pattern 1: Subprocess server on a pre-bound socket (verified)
**What:** bind in the parent, pass the descriptor, own the process group, prove nobody survives.
**When:** every browser run. Rejected alternatives: ARCH 3.1 B (thread) and C (no server).
**Verified behaviour** [VERIFIED: local run]: `python -m uvicorn spur.app:app --fd N` serves the real app with a TCP socket; **uvicorn 0.53.0 (the version `requirements.txt` pins for CI) also serves a TCP socket on `--fd`**, so the CI constraint does not change the mechanism. `/api/health` read `{'status': 'ok', 'version': '0.1.0', 'pool': {'workers': 2, 'queue_available': 4, 'workers_replaced': 0}}` 0.18 to 0.24 s after spawn; the first preview STL then took about 2.7 to 3.7 s at host load 8.
**Teardown, three modes measured** (3 group members before: uvicorn + 2 pool workers): `killpg(SIGKILL)` gone in 0.22 s; `killpg(SIGTERM)` gone in 0.22 s; **kill of the leader only: both pool workers still alive after the 10 s bound**. Your teardown must be the group kill; the leader-only kill is the red-once break for REQ-browser-server-fixture.

### Pattern 2: Fail closed, as a `FAILED`, with the required wording
Launch inside the test body (or a context-manager helper it enters), not in a fixture: a `pytest.fail` in a fixture reports `ERROR`, in the body `FAILED`. Catch `playwright.sync_api.Error` (public alias of `playwright._impl._errors.Error`) [VERIFIED: local run]. The message must carry `playwright install --only-shell chromium`, the effective `PLAYWRIGHT_BROWSERS_PATH` (or "unset: Playwright used its default cache"), and "`make test` runs the install stamp" (D-07).

### Pattern 3: Content-based waits (BT-6 applied to this app)
| Moment | Wait on | Never |
|--------|---------|-------|
| form built | `form#params [name]` count == `len(schema properties)` | empty `#status` |
| first build done | `#dl-stl` has attribute `href` (absent until the first success: `setDownloads(null)` removes it, `app.js:164`) | `#status == ''` |
| later build done | `#dl-stl` `href` == `"api/model.stl?" + <query in FORM order>` | a bare href (the previous state's href is still there) |
| 422 shown | `#messages .error` has the expected text | `.error` count == 1 (a stale error from the previous state matches at once) |
| request-path assertions | `page.expect_request(lambda r: "/api/info" in r.url)` around the action | `wait_for_timeout` anywhere |
| build-bound waits | explicit `timeout=` derived from `SPUR_BUILD_TIMEOUT` (default 30 s, `app.py:151`): 45 s | the library default for builds |

`expect`'s default timeout is **5000 ms** [VERIFIED: local run, Playwright's own log line `Expect "to_have_count" ... with timeout 5000ms`]. That is enough for DOM-only waits and **not** for a build on a 4-vCPU runner running `-n 4` beside kernel-heavy tests (first build 2.7 to 3.7 s here at load 8; PITFALLS BT-6 MEASURED 4.83 s cold). Pass `timeout=` on build-bound waits only, so a DOM regression still fails in 5 s.

### Pattern 4: Typed wrappers (verified under the project's own mypy and ruff)
See Code Examples 3. `page.evaluate` returns `Any`; assigning to `object` then narrowing passes `mypy --strict` with `disallow_any_explicit`; returning it directly fails with `no-any-return` [VERIFIED: local run, project mypy 2.4.0 with `--python-executable` pointing at the scratch venv].

### Pattern 5: Makefile stamp (skeleton; dry-run verified)
```make
# D-06: the browser lives with the venv. Absolute, because Playwright resolves a relative
# PLAYWRIGHT_BROWSERS_PATH against the driver's cwd (measured: launched from the scratch dir,
# "Executable doesn't exist at /private/tmp/ms-playwright/..." from /tmp).
export PLAYWRIGHT_BROWSERS_PATH := $(abspath $(VENV))/ms-playwright
BROWSER              := $(VENV)/.browser
BROWSER_INSTALL_ARGS ?=

$(BROWSER): $(STAMP)
	$(PY) -m playwright install $(BROWSER_INSTALL_ARGS) --only-shell chromium
	@touch $@

test: $(STAMP) $(BROWSER)  ## run the test suite (a cold first run is page cache, not the tests)
```
Because `$(BROWSER)` depends on `$(STAMP)` (which depends on `pyproject.toml`), a Playwright version bump re-runs the install on the next gate run (BT-8 drift), and `make clean` removes the browser with the venv. `test.fast`, `verify.static` and `lint`/`typecheck` do not depend on it. CI passes `BROWSER_INSTALL_ARGS=--with-deps` (env on the step or on the `make` line). A first `make test` in a fresh worktree downloads ~200 MB again (16.4 s measured here), because each worktree has its own `.venv`.

### Anti-Patterns to Avoid
- **`page.route(pattern, some_list.append)`**: crashes at runtime (`AttributeError: 'builtin_function_or_method' object has no attribute '_pw_impl_instance_'`) although mypy accepts it [VERIFIED: local run]. Use `lambda r: parked.append(r)`.
- **A global `ps | grep` orphan check**: the host currently holds eight orphaned `multiprocessing` children (PPID 1, 2 h 23 m to 2 h 27 m old, not from this session) [VERIFIED: local run, `ps`]. Scope the check to the fixture's own process group.
- **`os.killpg(pgid, 0)` as the only liveness probe on macOS**: a group holding only zombies answers `PermissionError` (EPERM), not `ProcessLookupError` [VERIFIED: local run]. Use `ps -A -o pgid=,stat=` and ignore `Z` states, or treat EPERM as "check ps".
- **Aborting `api/model.stl` in a scenario that asserts warnings**: `fail()` then replaces the warnings with "Request failed: ..." (Pitfall P7).
- **`page.clock`, golden images, Pillow, `--no-sandbox`, GPU flags, `channel=`**: see STACK "What NOT to Use".

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Waiting for the page | `time.sleep` / `wait_for_timeout` loops | `expect(...)`, `expect_request`, `expect_response` | Auto-retry; the 350 ms debounce and the build make any sleep either flaky or slow |
| Free port | bind-close-reuse | pre-bound socket + `--fd` | Removes the race under 8 workers (PITFALLS BT-5) |
| STL triangle count | an STL parser | `struct.unpack("<I", raw[80:84])` | The binary header holds it; the project's own topology test parses with `struct` |
| Browser download | curl/unzip of the shell | `playwright install --only-shell chromium` | Revision pinned to the wheel |
| Query-string comparison | string equality on hand-ordered params | `urllib.parse.parse_qsl` + sorted pairs for hash-vs-query; exact string for the golden pin | The form emits schema order and drops defaults; the pin wants the exact string, the round trip wants set equality |
| Process-tree bookkeeping | psutil | `start_new_session=True` + `killpg` + one `ps` call | No new dependency (CODING_VALUES) |

**Key insight:** every hard part (waiting, process groups, browser versioning) already has a primitive; the only code worth writing is the five-step fixture and the typed wrappers.

## Common Pitfalls

### Pitfall P1: The commit hook collects the file the moment it is committed
**What goes wrong:** `verify.fast` is `test.fast` over every test file but the named ones; a committed `tests/test_browser.py` is collected at commit, needs a browser and a server, and can exceed the SDK's 30 s kill (L36, BT-2).
**How to avoid:** the exclusion edits (`--ignore` in `test.fast` and `test-image`, `HEAVY_TEST_FILES`) must exist no later than the commit that adds the file. `--ignore=` of a path that does not exist yet is harmless, and the `HEAVY_TEST_FILES` pin compares Makefile text with the tuple, not file existence, so the exclusion can land first. See Open Question 1 for the roadmap-order tension.
**Warning signs:** `make verify.fast` over 20 s; `Executable doesn't exist` at commit time.

### Pitfall P2: `make -n` stops being environment independent
**What goes wrong:** `test_verify_and_verify_fast_share_one_static_prefix_and_one_pytest_recipe` runs `make -n verify` and `make -n verify.fast` and asserts the lines before the pytest line are identical (`tests/test_hooks.py:90-102`). With `$(BROWSER)` a prerequisite of `test`, `make -n verify` also prints `playwright install ...` and `touch .venv/.browser` whenever the stamp is missing or older than `$(STAMP)`; `verify.fast` does not. Measured diff: lines 14 to 16 of the `verify` dry run were `PLAYWRIGHT_BROWSERS_PATH=... playwright install --only-shell chromium`, `touch .venv/.browser`, then the pytest line, against pytest only for `verify.fast` [VERIFIED: local run, scratch Makefile copy]. That slice test runs in the **commit** hook, so any checkout that has run `verify.fast` but not yet `test` (every fresh clone, and every Playwright bump) would fail its next commit.
**How to avoid:** pass `-o <stamp path>` ("consider the file very old and do not remake it") in `_dry_run`: with it the dry run was byte-identical to today's [VERIFIED: local run, GNU Make 4.4.1, `diff` empty, stamp absent]. Keep the stamp path in one place the test can read (e.g. `BROWSER` echoed by `make -pn`, or a constant beside `HEAVY_TEST_FILES`). Add a second assertion that `make -n test` (without `-o`) names `$(BROWSER)` as a prerequisite so the admission cannot silently lapse.

### Pitfall P3: Orphans survive a leader-only kill
**What goes wrong:** MEASURED here: after `proc.kill()` of the uvicorn pid, both pool workers were still alive 10 s later. Timeout-killed or crashed xdist workers make this real (debt `xdist-worker-segfaults-in-occt-at-exit`).
**How to avoid:** Pattern 1; assert zero live members of the group after teardown within a bound, escalate to `killpg(SIGKILL)` and then fail the test naming the survivor; never use `proc.kill()` alone.

### Pitfall P4: No WebGL means no form (BT-1)
`const renderer = new WebGLRenderer({ canvas, antialias: true });` is at module top level (`app.js:229`). Assert `getContext('webgl2')` is non-null **first**, with a message naming WebGL (MEASURED, PITFALLS: 0 form fields under `--disable-3d-apis`). The default shell needs no flags (MEASURED here: SwiftShader LLVM on macOS, Subzero in the Linux container).

### Pitfall P5: A no-op hash assignment fires no `hashchange`
**What goes wrong:** `README:export-defaults` has `params == {}`, so its hash is `''`; on a page whose fragment is already empty, `location.hash = ''` fires nothing and `expect_request` waits for its full timeout (hung 3 of 3 runs, then 30 s in pytest) [VERIFIED: local run]. The same happens for any record whose raw hash equals the previous record's *normalized* hash, because `update()` rewrites the fragment with `history.replaceState` (`app.js:182`) and `replaceState` fires no event. A guard that nudges the hash to a dummy value first races: that nudge's own request can be captured as the record's request.
**How to avoid:** take the `{}` record from the fresh-load request (`expect_request` around `page.goto(base + "/")`: `readHash(); update()` runs at load, `app.js:370-371`), loop the other 43 with one `expect_request` per assignment, and compare `location.hash.slice(1)` to the target **before** assigning: if equal, raise with the record name instead of hanging. In file order none of the other 43 collided (3 of 3 runs, 43 of 43 captured) [VERIFIED: local run], but the JSON order can change on a regen.

### Pitfall P6: The wait signal exists before the request does (BT-6)
`update()` calls `setDownloads(null)` and `setStatus('Building…')` synchronously but `scheduleUpdate` waits 350 ms (`app.js:223`) for `input` events (typing); `hashchange`, Reset and the load call `update()` directly. After `fill(...)` an empty `#status` and the old `href` are already true. Also: `expect(page.locator("#messages .error")).to_have_count(1)` matched a stale error from the previous hash in my probe and only worked by timing luck. Wait on text, URL or `href` content; the `#dl-stl` href is built in **form (schema) order**, not hash order (`app.js:106` loops `fields`), so compute the expected string from the schema order or compare parsed pairs.

### Pitfall P7: Aborting the STL erases the warnings
`fail()` calls `showMessages(errors)` (`app.js:192-197`), which replaces the whole `#messages` box. With `api/model.stl` aborted, a 200 `/api/info` renders its warnings and then immediately loses them to "Request failed: ..." [VERIFIED: local run: `#bore_hex=6` showed `[]`]. The warning scenario (step 4) must let the real build run. The sweep and the round-trip scenarios may abort the STL because they assert only on requests and form state.

### Pitfall P8: `ctx.fields` is not on every 422
`detail[].ctx.fields` exists only for the model validator's `infeasible` error (`params.py:184-187`: `PydanticCustomError("infeasible", "{message}", {"message": ..., "fields": fields})`). Field-level range errors (`teeth=2`) have `loc: ["query", "teeth"]` and `ctx: {"ge": 6}`. `problems()` marks both (`app.js:127`: `for (const name of [d.loc?.[1], ...(d.ctx?.fields ?? [])])`). Measured: `#bore_flat=3` -> API 422, `loc ['query']`, `ctx {'message': 'D-flat must be between 4.5 and 9 mm (flat to opposite side).', 'fields': ['bore_flat']}`; the page marked exactly `['D-flat']` and rendered that sentence (no "Title:" prefix, because `fields.get(d.loc?.[1])` is undefined) [VERIFIED: local run]. `tests/test_api.py::test_infeasible_is_422_with_fields` asserts the same API shape for `bore_flat=3`. Recommend `#bore_flat=3` for REQ-browser-invalid-field-marked, with `#teeth=2` as a second `loc[1]` assertion (marks `['Teeth']`, message `Teeth: Input should be greater than or equal to 6`). A two-field case (`spoke_count=3&hole_count=3`) marks `['Spoke arms', 'Lightening holes']`.

### Pitfall P9: Playwright's missing-browser message is not the required one
Verified output with the host cache (no revision 1243) and with an empty isolated path: `BrowserType.launch: Executable doesn't exist at <path>/chromium_headless_shell-1243/...` plus a banner saying `playwright install`. Neither says `--only-shell chromium` nor mentions `make test` [VERIFIED: local run]. Catch and re-raise (Pattern 2).

### Pitfall P10: Gate-text drift
"four heavy ones" appears in `Makefile:88,153,171` and `.pre-commit-config.yaml` (header and hook name); `docs/architecture/web-ui.md:51` says "There is no browser test." Update these in the admission commit. Do **not** touch the `63.555 s` / `~64 s` sentences: Phase 25 owns them (REQ-gate-bar-reset). `.pre-commit-config.yaml` edits re-trigger the `$(HOOKS)` stamp (`pre-commit install`) on the next gate run in the main checkout only; expected.

### Pitfall P11: Coverage, greenlets and `filterwarnings = error`
PITFALLS BT-9 left "does Playwright's greenlet break coverage" UNVERIFIED. Run with the project's `[tool.coverage.run]` (`concurrency = ["multiprocessing", "thread"]`, `parallel`, `sigterm`, `branch`) under `--cov` at `-n 2`, with `filterwarnings = ["error", ...]` and `--strict-markers --strict-config`: passed, no `CoverageWarning`, and a helper module exercised by a test that ran **after** the browser test on the same worker still read 100.00 % (browser-first, helper-alone and `-n 1` orders all identical) [VERIFIED: local run, scratch project with `source = ["tests"]`]. The browser test file itself reads partial coverage; it is outside `source = ["src/spur"]`, so the floor (`fail_under = 96`, last baseline 97.92 %, PITFALLS) neither gains nor loses. The server is a plain subprocess and contributes no `src/` coverage. Leave `[tool.coverage.run]` alone; record TOTAL before and after in the A/B.

### Pitfall P12: Lint traps in new test code
Project ruff (0.16.10, rules `E F W I N UP B SIM C4 PTH TID ARG ERA TRY LOG G PT RUF`, line length 100) flagged my probe on `E501` and `PT018` (compound assert) [VERIFIED: local run]. `make no-fake-done` greps `TODO|FIXME|XXX|HACK|NotImplementedError` as whole words in `*.py`, `*.js`, `*.sh` (`Makefile:117-118`): do not write those words in comments. `ERA` flags commented-out code.

### Pitfall P13: The A/B arm flag and the stamp
Arm A is `make verify PYTEST_ARGS="--ignore=tests/test_browser.py"` (`$(PYTEST_ARGS)` is last on the `test` recipe line, `Makefile:150`, so it wins). It still has the `$(BROWSER)` prerequisite; with the stamp present that costs nothing. Record `uptime` before and after each run (host load was 5 to 15 here).

## Code Examples

Verbatim values these examples rely on (opened this session):

- `src/spur/static/app.js:229` `const renderer = new WebGLRenderer({ canvas, antialias: true });`
- `:274` `const colour = css('--grid');` `:282` `scene.background = new Color(css('--view-bg'));` `:283` `material.color.set(css('--mesh'));` `:284` `edgeMaterial.color.set(css('--edge'));`
- `:196` `setStatus(mesh ? 'Showing the last valid gear' : '');` `:206-207` `const stlQ = new URLSearchParams(q);` / `stlQ.set('quality', 'preview');` `:223` `debounce = setTimeout(update, 350);`
- `:311-313` `mesh = new Mesh(geometry, material);` / `edges = new LineSegments(new EdgesGeometry(geometry, 40), edgeMaterial);` / `  scene.add(mesh, edges);`
- `:340` `window.addEventListener('hashchange', () => { readHash(); update(); });` `:345-349` the `#reset` handler (`for (const [name, { input }] of fields) input.value = defaults[name];`, `mateInput.value = '';`, `update();`)
- `index.html` (opened via shell, lines 19-43): `<form id="params" autocomplete="off">`, `<button type="button" id="reset">`, `<canvas id="canvas" aria-label="3D preview of the gear">`, `<div id="status" role="status">`, `<a id="dl-stl" class="btn primary" aria-disabled="true">`, `<div id="messages" aria-live="polite">`, `<input id="mate-teeth" ...>`
- `src/spur/cli.py:86` `uvicorn.run("spur.app:app", host=ns.host, port=ns.port, workers=ns.workers,`; `app.py:151` `int_env("SPUR_BUILD_TIMEOUT", 30)`; `app.py:137` `int_env("SPUR_BUILD_WORKERS", 2),`
- `Makefile:149-150`: `test: $(STAMP)  ## run the test suite (a cold first run is page cache, not the tests)` / `$(PY) -m pytest -n $(PYTEST_WORKERS) --cov --cov-report=term $(PYTEST_ARGS)`; `:171-174` `test.fast` with `--ignore=tests/test_model.py --ignore=tests/test_pool.py \` / `--ignore=tests/test_api.py --ignore=tests/test_cli.py $(PYTEST_ARGS)`; `:186-192` `test-image` runs `python -m pytest -q -p no:cacheprovider $(PYTEST_ARGS)` inside the image after `pip install -q --root-user-action=ignore pytest httpx`
- `tests/test_hooks.py:24` `HEAVY_TEST_FILES = ("test_model", "test_pool", "test_api", "test_cli")`; `:121` `assert ignored == {f"tests/{n}.py" for n in HEAVY_TEST_FILES}`

### 1. Server fixture (module scope; the shape that ran green)
```python
@pytest.fixture(scope="module")
def server() -> Iterator[str]:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    sock.listen(128)
    env = {k: v for k, v in os.environ.items() if not k.startswith("SPUR_")}  # D-11: shipped pool size
    with tempfile.TemporaryFile() as log:  # a PIPE would deadlock on a full buffer
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "spur.app:app", "--fd", str(sock.fileno())],
            pass_fds=[sock.fileno()], start_new_session=True, stdout=log, stderr=log, env=env)
        base = f"http://127.0.0.1:{sock.getsockname()[1]}"
        try:
            wait_until_pool_is_up(base, proc, deadline_s=120)   # urlopen /api/health, "pool" non-null
            yield base
        finally:
            stop_group(proc)        # killpg(TERM) -> wait(10) -> live members? -> killpg(KILL) -> fail if any
            sock.close()
```
`stop_group` must escalate and **fail** when a live member remains (use `ps -A -o pgid=,stat=,pid=` filtered to the group, ignoring `Z`). On a failure, print the tail of `log`.

### 2. Parked-route blank control and the drawn state
```python
parked: list[Route] = []
page.route("**/api/model.stl*", lambda r: parked.append(r))   # NOT parked.append
page.goto(base + "/")
...                                                           # step 0/1 run here
wait_until(lambda: bool(parked))                              # bounded poll, no sleep-per-assert
blank = page.locator("#canvas").screenshot()                  # form built, info shown, STL not yet
assert page.locator("#dl-stl").get_attribute("href") is None
parked[0].continue_()
expect(page.locator("#dl-stl")).to_have_attribute("href", "api/model.stl", timeout=45_000)
drawn = page.locator("#canvas").screenshot()
```
Measured on this host: blank **3,917 B**, drawn **38,908 B**, ratio **9.93** (STACK's separate-page blank was 3,393 B; its drawn figure 38,908 B is identical, so the drawn render is deterministic for this Chromium/SwiftShader). Linux (Subzero, not LLVM) is unmeasured: take the bar from the lower of the two hosts' ratios with margin (STACK's probe passed at 3x). `[ASSUMED]` that Linux differs; the runner reading decides.

### 3. Fail-closed launch and typed wrappers (mypy strict clean)
```python
def launch(pw: Playwright) -> Browser:
    try:
        return pw.chromium.launch()
    except Error as e:                       # playwright.sync_api.Error
        pytest.fail(
            "headless shell missing: run `playwright install --only-shell chromium` "
            f"(PLAYWRIGHT_BROWSERS_PATH={os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '<unset: default cache>')}); "
            "`make test` runs the install stamp.\n" + str(e))

def eval_int(page: Page, expression: str) -> int:
    value: object = page.evaluate(expression)         # Any -> object, then narrow
    assert isinstance(value, int), (expression, value)
    return value
```
`return page.evaluate(expression)` from `-> int` fails `mypy --strict`: `error: Returning Any from function declared to return "int"  [no-any-return]` [VERIFIED: local run]. Wrappers needed: int, `str | None`, `list[str]`, `list[tuple[str, str]]` (form name/value pairs), `bool`.

### 4. Schema-derived expectations
```python
props: dict[str, dict[str, object]] = schema["properties"]
groups: dict[str, list[str]] = {}
for name, p in props.items():
    groups.setdefault(str(p.get("group", "Other")), []).append(name)   # app.js:55 `prop.group ?? 'Other'`
expected = [n for g in groups.values() for n in g]                        # groups by first appearance
expect(page.locator("form#params [name]")).to_have_count(len(expected))
assert page.eval_on_selector_all("form#params [name]", "els => els.map(e => e.name)") == expected
assert page.locator("form#params legend").all_text_contents() == list(groups)
for var in ("--view-bg", "--grid", "--mesh", "--edge"):
    assert get_css_var(page, var), var
```
Measured: 31 fields on the current schema; never hard-code the 31.

### 5. The one production line (verified in a patched copy served via `PYTHONPATH`)
```js
  scene.add(mesh, edges);
  canvas.dataset.triangles = String(geometry.attributes.position.count / 3);
```
Read it with `page.locator("#canvas").get_attribute("data-triangles")`. Default preview: `9066` == STL header `9066` (453,384 bytes) [VERIFIED: local run]. After both a `loc[1]` 422 and a `ctx.fields` 422 the attribute still read the previous count (a failed build never reaches `showModel`), which matches "Showing the last valid gear" and costs no code: recommend asserting the retained count. Pin-safe: `triangles`, `dataset`, `position`, `attributes`, `geometry`, `canvas` are not `GearParams` fields (`GearParams.model_fields` printed this session), the line has no quote characters and no `['word',` row, so `tests/test_api.py:162` and `:123` are untouched [VERIFIED: local run, the two regexes read in the file].

### 6. href only after `showModel` returns
Fulfil `api/model.stl` with a 10-byte body: the page shows `Request failed: Offset is outside the bounds of the DataView`, `#dl-stl` keeps no `href`, `aria-disabled` stays [VERIFIED: local run]. Red-once: move `setDownloads(q);` above `showModel(buf);` in `app.js` and the href appears beside the error. (A same-tick snapshot cannot tell the two orders apart on success; the throwing `showModel` is the only observable of the ordering.)

### 7. Sweep helper
```python
def sweep(page: Page, records: dict[str, Record]) -> dict[str, str]:
    sent: dict[str, str] = {}
    page.route("**/api/model.stl*", lambda r: r.abort())      # D-08: no builds
    with page.expect_request(lambda r: "/api/info" in r.url) as first:
        page.goto(base + "/")                                   # the {} record IS the fresh load
    for name, rec in records.items():
        h = urlencode({**rec["params"], **({"mate_teeth": rec["mate_teeth"]} if "mate_teeth" in rec else {})})
        if not h:
            sent[name] = urlsplit(first.value.url).query; continue
        if page.evaluate("() => location.hash.slice(1)") == h:
            raise AssertionError(f"{name}: hash equals the current fragment, no hashchange would fire")
        with page.expect_request(lambda r: "/api/info" in r.url) as ri:
            page.evaluate("h => { location.hash = h }", h)
        sent[name] = urlsplit(ri.value.url).query
    return sent
```
Measured result: 44 records, **44 distinct queries**, all `/api/info` responses `200`, 0.09 to 0.15 s for the 43 hash-driven records. Samples: `README:export-teeth-24` -> `teeth=24&module=1&pressure_angle=20&bore_flat=0` (schema order, hash had `bore_flat` first); `README:info-mate-40+mate=40` -> `mate_teeth=40` (`teeth=19` is the default so it is dropped); `test_calc.py::test_span_measurement[2]` -> `module=1.0&pressure_angle=20&bore_d=0&recess_sides=none` (`1.0` kept verbatim). Five records carry a record-level `mate_teeth` (40, 40, 40, 40, 12).

### 8. `#root_shape=bogus` as it behaves today (the pin)
`#root_shape=bogus&teeth=22` -> select `value` `''`, `selectedIndex` `-1`; requests `/api/info?teeth=22` and `/api/model.stl?teeth=22&quality=preview` (no `root_shape`); fragment rewritten to `#teeth=22`; `#status` `''`, 0 errors, 0 warnings; the API alone answers `422 Input should be 'radial' or 'trochoid'` [VERIFIED: local run]. Assert exactly that, name the pin as today's behaviour, file the debt.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Playwright installs all browsers | `--only-shell` for headless-only | in 1.63.0 docs [CITED: playwright.dev/python/docs/browsers] | 198 MB vs 556 MB |
| `pytest-cov` subprocess hook | removed in 7.0.0 | READ, `pyproject.toml` comment | The server child is unmeasured; neutral for the floor |
| Cache browsers in CI | not recommended | [CITED: playwright.dev/python/docs/ci] "restore time is comparable to download time" | No `actions/cache` (also REQUIREMENTS Out of Scope) |

**Deprecated/outdated:** `ARCHITECTURE.md` 3.3 rows 5 to 6 (init-script draw counter, in-page pixel decode) and its CPU-render launch args are superseded by D-04, D-05 and the measurement that the default shell needs no flags; its `xdist_group` + `--dist loadgroup` suggestion is superseded by D-10; its "cache `ms-playwright`" by the Playwright CI doc.

## Runtime State Inventory

Not applicable: Phase 21 is not a rename, refactor or migration phase. The only production edit is one additive line in `app.js`.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `ubuntu-latest` (currently Ubuntu 24.04 [CITED: github.com/actions/runner-images README]) runs `playwright install --with-deps --only-shell chromium` through `sudo` with no extra step; only a non-root + sudo container was run | Standard Stack; Pattern 5 | First CI run red; SC5 exists to find this, budget a draft-PR iteration loop |
| A2 | The PNG ratio on Linux/Subzero differs from macOS/LLVM, so the bar must come from the lower of two readings | Code Examples 2 | A bar set from the macOS reading alone could be red on CI |
| A3 | 45 s on build-bound waits and 5 s on DOM waits suffice on a 4-vCPU runner at `-n 4` | Pattern 3 | Flaky CI; widen after reading the runner |
| A4 | `ps -A -o pgid=,stat=,pid=` has the same columns and `Z` state on Linux procps as on macOS | Pattern 1; Code Examples 1 | Orphan check false-green/false-red on CI; verify in the spike on the runner |
| A5 | Playwright verifies the integrity of the browser archive it downloads from `cdn.playwright.dev` | Security Domain | Supply-chain assumption; the pin on the wheel is the project's control |
| A6 | The helper/capture-script layout (flat in `tests/`) and file names `browser_session.py`, `capture_requests.py`, `test_browser_pins.py` | Project Structure | Rename only |
| A7 | A runner has enough RAM for server + 2 pool workers + Chromium beside 4 xdist workers (~2.9 GiB server side, D-11, plus ~387 MiB for Chromium, PITFALLS BT-5 MEASURED) | Summary | OOM on CI; runner RAM unverified |
| A8 | `ubuntu-latest` stays 24.04 for the phase (the label migrates gradually over 1 to 2 months per the README); the Playwright pin, not the runner, decides the browser build, but the apt set differs per release | Pattern 5 | A `--with-deps` surprise mid-phase |
| A9 | The `#root_shape=bogus` debt should be filed `must` (not `blocker`, not `nice`) | Open Questions 3 | CLAUDE.md: a blocker must be fixed now or the human asked |

## Open Questions

1. **How is the roadmap's fixed order (scenarios, then admission in one commit) reconciled with "excluded ... in the same commit that adds the file" (SC4)?**
   - What we know: the commit hook runs `verify.fast`, which collects any `tests/test_*.py` not named in `--ignore` (L36). `--ignore` of a missing file is harmless; the `HEAVY_TEST_FILES` pin reads Makefile text only (`tests/test_hooks.py:118-121`).
   - What's unclear: whether the human reads "same commit" literally.
   - Recommendation: first task after the spike commits only the exclusion plumbing (Makefile `test.fast` and `test-image` ignores, `HEAVY_TEST_FILES`, the `-o` fix, the dev pin, `.gitignore`) with no test file, shown red by removing the ignore; later commits may then add `tests/test_browser.py` freely; the stamp, the `test` prerequisite, `ci.yml`, docs and the `Lxx` are the admission commit. This is stricter than the letter (the exclusion precedes the file). Alternative: keep `tests/test_browser.py` uncommitted until the admission commit. Surface the choice at plan-check.

2. **Which 422 scenario does REQ-browser-invalid-field-marked mean?**
   - What we know: `ctx.fields` is only on `infeasible` errors (P8).
   - Recommendation: `#bore_flat=3` as the required scenario (single field, `tests/test_api.py` precedent), `#teeth=2` as a second assertion for `loc[1]`.

3. **Severity of the `#root_shape=bogus` debt file.**
   - What we know: the user-set value silently becomes the default and the fragment is rewritten; no number is wrong and the part is the default part, but it is a silent drop of an explicit input (L03/L05 spirit). REQUIREMENTS says "filed as debt, not fixed".
   - Recommendation: `must` with the trigger "Phase 24 (selector) or any change to `buildForm`'s enum rendering"; if the human wants `blocker`, CLAUDE.md requires fixing it now. Ask in the plan checkpoint.

4. **Linux bars (PNG ratio, timeouts) and the `ps` portability.** Only a runner reading settles A2, A3, A4; the spike's draft PR must print the renderer string, PNG sizes and per-step times.

5. **Does the golden pin carry the STL query?** Recommend no: info query only, as D-09 words it. The STL request is `q` plus `quality=preview` by construction (`app.js:206-207`) and step 2 already proves one real pair.

6. **`test.ui` target.** Not needed for validation (`make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov"` runs the file with the stamp and the variable); add only if the planner wants the shorthand.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 | everything | yes | 3.12.15 (`.venv`) | none needed |
| `playwright` wheel in project `.venv` | the test | no (`ModuleNotFoundError`) | scratch venv has 1.63.0 | the `$(STAMP)` installs it once the `[dev]` pin lands |
| Headless shell 1243 in project | the test | no | scratch install only | `$(BROWSER)` stamp |
| Host Playwright cache (other project) | must survive | yes | `chromium-1228`, `chromium_headless_shell-1228`, `ffmpeg-1011` | untouched by D-06 |
| Network to `cdn.playwright.dev` | install | yes | 198 MB in 16.4 s | none |
| Docker (OrbStack) | optional Linux probe | yes | 29.8.2, `ubuntu:24.04` image local | not a substitute for SC5 |
| `gh` | reading the real CI run id and wall time | yes | 2.102.0 | the Actions UI |
| A pushed branch / draft PR | SC5 (real `ubuntu-latest` run) | not yet | `origin` = `git@github.com:halfb00t/spur.git` | none: push is a human action (checkpoint) |
| Idle host for A/B | D-12 | no | load 5 to 15, 10 users | record load beside every figure; the reading admits, sets no bar |
| Node on the host | not required | yes (homebrew) | n/a | the wheel bundles its own |

**Missing with no fallback:** none blocking research. **Blocking for SC5:** a push by the human.

## Validation Architecture

Nyquist validation is enabled (`workflow.nyquist_validation` absent in `.planning/config.json`, treated as enabled).

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 + pytest-xdist 3.8.0 + pytest-cov (`[dev]`), `playwright==1.63.0` (new) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (`--strict-markers --strict-config`, `filterwarnings = ["error", ...]`) |
| Quick run command | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"` (needs the stamp and the exported path; `--no-cov` is mandatory for partial runs) |
| Light pins | `.venv/bin/python -m pytest tests/test_hooks.py tests/test_browser_pins.py -n0 --no-cov -q` |
| Full suite command | `make verify` (result line + coverage TOTAL recorded) |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test (file::step) | Observable | Red-once break (revert after) | Command |
|--------|----------|-------------------|------------|-------------------------------|---------|
| REQ-browser-server-fixture | real subprocess on pre-bound socket; nothing survives | `test_browser.py::server` fixture + `test_the_viewer` (teardown) | `GET /api/health` has non-null `pool`; zero live `ps` members of the group after teardown | replace `killpg` with `proc.kill()`: expect the survivor failure naming 2 pids (measured: 2 survivors >= 10 s) | quick run |
| REQ-browser-form-from-schema | form == schema, order, CSS vars | `test_the_viewer` step "form-from-schema" | DOM `name` list == schema-derived list; legends == groups; `--view-bg/--grid/--mesh/--edge` non-empty | in a scratch copy of `app.js`: reverse `Object.entries(schema.properties)`; rename `--grid` in `style.css` | quick run |
| REQ-browser-first-build-drawn | webgl2; href after `showModel`; non-blank; triangles == STL header | steps "webgl2", "first build drawn", "href after showModel" | `getContext('webgl2')` non-null; PNG ratio >= recorded bar; `data-triangles == header(byte 80)`; truncated-STL page has no `href` | launch with `--disable-3d-apis` (webgl2 step names WebGL); comment out `scene.add(mesh, edges)` (ratio fails, triangles pass); change `/ 3` to `/ 9` (equality fails); move `setDownloads(q)` above `showModel(buf)` (truncated STL shows an `href`) | quick run |
| REQ-browser-invalid-field-marked | 422 marks fields, message names them | step "invalid field marked" (`#bore_flat=3`, `#teeth=2`) | `label.field.invalid .name` == `['D-flat']` / `['Teeth']`; error text contains `D-flat must be between 4.5 and 9 mm` | delete `...(d.ctx?.fields ?? [])` (the `ctx.fields` case reds), delete `d.loc?.[1],` (the `loc[1]` case reds) | quick run |
| REQ-browser-warning-rendered | rendered warnings == `/api/info` warnings (equality) | step "warning rendered" (`module=1&pressure_angle=14.5`, `bore_hex=6`) | `.warning` texts list == `info["warnings"]` list | `info.warnings.slice(0, 1)` in `renderInfo` (containment would still pass, equality reds) | quick run |
| REQ-browser-link-round-trip | hash -> form -> query on load, Reset, `hashchange` | step "link round trip" x3 | every hash field's `input.value`; `parse_qsl(query)` pairs == hash pairs; fragment normalised; Reset: empty query, all inputs == schema default, `#mate-teeth` empty | remove `readHash();` from the load path, from the `hashchange` listener, and the default loop from `#reset` (one break per path) | quick run |
| REQ-browser-golden-request-sets | 44 queries pinned | step "golden sweep" + regen target | sweep result == `tests/regression/golden_requests.json` (44 entries, same keys as `pre_v0_2.json`); `git diff --exit-code tests/regression/pre_v0_2.json` clean | make `gearQuery()` skip one field, or edit one JSON entry | quick run; regen: the new make target |
| REQ-browser-fails-closed | missing shell = FAILED with wording; no skip path | `test_browser.py` (launch helper) + `test_browser_pins.py` | message contains `playwright install --only-shell chromium` and the path; pin finds no `importorskip`/`pytest.skip`/`skipif`/`xfail`/opt-out env read | `PLAYWRIGHT_BROWSERS_PATH=$(mktemp -d) make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov"` (the Makefile export wins, so run the pytest binary with the variable set by hand for this one); add `pytest.importorskip("playwright")` and see the pin red | quick run; light pins |
| REQ-browser-in-the-gate | excluded from `test.fast` and `test-image`; runs in `test`; priced | `tests/test_hooks.py` (extended) | `ignored == {tests/{n}.py for n in HEAVY_TEST_FILES}` incl. `test_browser`; `make -n -o <stamp> test-image` contains `--ignore=tests/test_browser.py`; `make -n test` names the stamp; `make verify.fast` < 30 s | delete `--ignore=tests/test_browser.py` from `test.fast` (pin reds); from `test-image` (pin reds); drop `-o` (the stamp-absent dry run reds the prefix test) | light pins; `make verify.fast`; A/B per D-12 |
| REQ-browser-stack-pinned | exact pin, no plugin, default shell, strict typing, Linux proof | `tests/test_browser_pins.py` + `make typecheck` + CI run | `pyproject.toml` dev has `playwright==`; no `pytest-playwright`; `requirements.txt`/Dockerfile/`refresh-requirements.sh` have no `playwright`; no `channel=` in test files; `mypy` green; real runner run green with `webgl2` printed | change the pin to `>=`; add `channel="chromium"`; return `page.evaluate(...)` unwrapped (mypy `no-any-return`) | light pins; `make typecheck`; CI run id in `bench/RESULTS.md` |

### Sampling Rate
- **Per task commit:** `make verify.fast` (<= 30 s, includes the light pins) plus the quick run for any task that touches `tests/test_browser.py`, `browser_session.py`, `app.js` or the Makefile stamp.
- **Per wave merge:** the quick run, `make typecheck`, `git diff --exit-code tests/regression/pre_v0_2.json`.
- **Phase gate:** one full `make verify` green with the result line and coverage TOTAL recorded, the D-12 A/B (6 runs, flake runs listed apart), the real `ubuntu-latest` run, every "seen red once" recorded in `bench/RESULTS.md`.

### Wave 0 Gaps
- [ ] `tests/test_browser.py`, `tests/browser_session.py` - the whole test (REQ-browser-*)
- [ ] `tests/test_browser_pins.py` - no-skip, no-opt-out, stack pins (REQ-browser-fails-closed, -stack-pinned)
- [ ] `tests/regression/golden_requests.json` + `tests/capture_requests.py` + a make target needing `$(BROWSER)` (REQ-browser-golden-request-sets)
- [ ] `tests/test_hooks.py` edits: `HEAVY_TEST_FILES`, `-o`, `test-image` pin (REQ-browser-in-the-gate)
- [ ] `pyproject.toml` `playwright==1.63.0`; Makefile `$(BROWSER)` stamp + export; `ci.yml` `BROWSER_INSTALL_ARGS`; `.gitignore` entry for whatever artifact directory the test writes (decide in the spike: none is written unless a failure screenshot is added)
- [ ] Install: first `make test` after the pin lands (checkpoint on the SUS-flagged packages first)

## Security Domain

`security_enforcement` is absent in config, so it is treated as enabled. This phase adds test-time code only; the shipped surface changes by one `dataset` attribute assignment.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | the app has none (debt `no-authentication`) |
| V3 Session Management | no | n/a |
| V4 Access Control | no | n/a |
| V5 Input Validation | partly | the test feeds hash values to the real form; validation stays at the `GearParams` boundary (unchanged) |
| V6 Cryptography | no | none hand-rolled |
| V14 Configuration / supply chain | yes | exact `playwright==` pin; browser fetched over HTTPS from `cdn.playwright.dev` (seen in the install log); nothing added to the runtime closure |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Test server reachable from the network | Information disclosure | bind the pre-bound socket on `127.0.0.1` only (REQ-browser-server-fixture) |
| Orphaned server/pool holding resources after a crash | Denial of service | `start_new_session=True`, group kill, survivor check |
| Developer environment leaking into the server under test (`SPUR_*`) | Tampering | scrub `SPUR_*` from the child env (bench/RESULTS.md records "SPUR_* environment: none set") |
| Shell injection through a built command | Tampering | fixed argument list, no `shell=True` (precedent: `capture.py`'s `git()` helper, T-07-03) |
| Unpinned browser/driver drift | Tampering | exact pin; `$(BROWSER)` re-runs on any `pyproject.toml` change |
| `sudo apt-get` on a runner via `--with-deps` | Elevation of privilege | CI-only, GitHub-hosted ephemeral runner; local dev never uses `--with-deps` |
| Browser download integrity | Tampering | `[ASSUMED]` Playwright verifies archives (A5) |

## Sources

### Primary (HIGH confidence)
- Local runs 2026-10-10 (scratch venv under the session scratchpad; macOS arm64; project `.venv` tools used read-only): Playwright 1.63.0 install, launch, WebGL probe, `expect` timeout, canvas screenshots, `dataset.triangles` in a patched copy served via `PYTHONPATH`, sweep, 422 probes, truncated STL, `#root_shape=bogus`, fail-closed messages, orphan modes, `make -n` dry runs with a scratch Makefile, strict mypy 2.4.0 and ruff 0.16.10 on a probe, pytest + `--cov` + `filterwarnings=error` + `-n 2`, uvicorn 0.53.0 `--fd`, `ubuntu:24.04` container install through `sudo`.
- Repo files opened: `CONTEXT.md`, `REQUIREMENTS.md`, `STATE.md` (head), `ROADMAP.md` (Phase 21), `.planning/research/{SUMMARY,STACK,ARCHITECTURE,PITFALLS}.md`, `src/spur/static/app.js` (whole), `src/spur/static/index.html` (lines 1-43), `src/spur/params.py` (150-220), `Makefile` (whole), `tests/test_hooks.py` (whole), `tests/test_api.py` (100-240), `tests/conftest.py`, `tests/regression/capture.py`, `tests/regression/pre_v0_2.json` (parsed), `pyproject.toml`, `.github/workflows/ci.yml`, `required-jobs.txt`, `.pre-commit-config.yaml`, `.gitignore`, `docs/architecture/decision_log.md` (L11, L13, L34, L36, L38 head), `docs/CODING_VALUES.md`, `bench/RESULTS.md` (`### The gate, priced (19-09)`), the browser-test idea, the resource-tracker debt, both INDEX files, `docs/architecture/web-ui.md`.
- PyPI JSON for `playwright` (publisher, URLs, wheel list).

### Secondary (MEDIUM confidence)
- [CITED: playwright.dev/python/docs/browsers] `--only-shell`, `--with-deps`, default cache locations, browser GC and `PLAYWRIGHT_SKIP_BROWSER_GC` / `--no-remove`.
- [CITED: playwright.dev/python/docs/ci] `pip install playwright` + `playwright install --with-deps`; caching browser binaries not recommended.
- [CITED: github.com/actions/runner-images README] `ubuntu-latest` = Ubuntu 24.04, gradual `-latest` migration.
- `ubuntu:24.04` linux/amd64 container (OrbStack): a stand-in, not a runner.

### Tertiary (LOW confidence)
- Runner RAM/vCPU figures (not fetched), apt behaviour on a real runner, Playwright download integrity (A5, A7).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH on macOS (every claim run), MEDIUM on Linux (container only)
- Architecture: HIGH (fixture, sweep, wrappers, Makefile dry run all executed)
- Pitfalls: HIGH for P1 to P9, P11, P12 (reproduced or read this session); MEDIUM for P13 and the Linux-dependent items
- Gate cost: the 4.4 to 6.9 s isolated figure is a scratch-prototype reading at host load 7 to 8, not a bar; the A/B under D-12 is the admission reading

**Research date:** 2026-10-10
**Valid until:** 2026-11-09 (30 days; re-check if `playwright` > 1.63.0 is wanted, because a new wheel means a new shell revision and a re-measured PNG reading)
