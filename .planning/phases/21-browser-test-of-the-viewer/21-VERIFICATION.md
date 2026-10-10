---
phase: 21-browser-test-of-the-viewer
verified: 2026-10-10T15:30:00Z
status: passed
score: 5/5 must-haves verified
covered_files:
  - ".github/workflows/ci.yml"
  - ".planning/phases/21-browser-test-of-the-viewer/21-01-PLAN.md"
  - ".planning/phases/21-browser-test-of-the-viewer/21-01-SUMMARY.md"
  - ".planning/phases/21-browser-test-of-the-viewer/21-02-PLAN.md"
  - ".planning/phases/21-browser-test-of-the-viewer/21-02-SUMMARY.md"
  - ".planning/phases/21-browser-test-of-the-viewer/21-03-PLAN.md"
  - ".planning/phases/21-browser-test-of-the-viewer/21-03-SUMMARY.md"
  - ".planning/phases/21-browser-test-of-the-viewer/21-04-PLAN.md"
  - ".planning/phases/21-browser-test-of-the-viewer/21-04-SUMMARY.md"
  - ".planning/phases/21-browser-test-of-the-viewer/21-05-PLAN.md"
  - ".planning/phases/21-browser-test-of-the-viewer/21-05-SUMMARY.md"
  - ".planning/phases/21-browser-test-of-the-viewer/21-06-PLAN.md"
  - ".planning/phases/21-browser-test-of-the-viewer/21-06-SUMMARY.md"
  - ".planning/phases/21-browser-test-of-the-viewer/21-07-PLAN.md"
  - ".planning/phases/21-browser-test-of-the-viewer/21-07-SUMMARY.md"
  - ".planning/phases/21-browser-test-of-the-viewer/21-08-PLAN.md"
  - ".planning/phases/21-browser-test-of-the-viewer/21-08-SUMMARY.md"
  - "Makefile"
  - "bench/RESULTS.md"
  - "docs/architecture/decision_log.md"
  - "pyproject.toml"
  - "src/spur/static/app.js"
  - "tests/browser_session.py"
  - "tests/capture_requests.py"
  - "tests/regression/golden_requests.json"
  - "tests/test_browser.py"
  - "tests/test_browser_pins.py"
  - "tests/test_hooks.py"
covered_digest: "v3:sha256:4aee427a552831f6af1ed31344c751f25c954a982bdc62b2f5c51078d6dbda17"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 21: Browser Test of the Viewer Verification Report

**Phase Goal:** A real headless browser loads the shipped page inside `make verify` and CI and proves what the Python tests structurally cannot see (the form builds from `/api/schema`, an invalid field is marked, a warning renders, the first STL is drawn) at a measured gate price, failing loudly when it cannot run, with the request each of the 44 fixture records makes pinned before any later phase changes the form.
**Verified:** 2026-10-10
**Status:** passed
**Re-verification:** No, initial verification

I started from the hypothesis that the goal was missed and tried to falsify it. I read the test code, the Makefile, CI, pyproject, `app.js` and the golden pin. I ran `tests/test_browser.py` in my own process and the pin and hook tests. I confirmed the CI run against `gh`. SUMMARY.md claims were used only as pointers.

## Goal Achievement

### Observable Truths (the 5 ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A fresh load builds the page the schema describes and draws the first part (webgl2 asserted first; form groups/fields/order equal `/api/schema`, counts read at test time; theme CSS vars non-empty; `#dl-stl` href only after `showModel`; canvas non-blank vs blank control at a recorded bar; `canvas.dataset.triangles` equals the STL header count) | VERIFIED | I ran the test myself (`PLAYWRIGHT_BROWSERS_PATH=.venv/ms-playwright ... -n0`): `1 passed in 3.37s`. Printed output: `webgl2 renderer: ANGLE (... SwiftShader ...)` is the first step. `schema: 31 fields in 7 groups`, with the expected names, legends and titles built from `properties` at test time (`test_browser.py:292-326`, no literal counts). Four `THEME_VARIABLES` asserted non-empty. `canvas PNG blank 3917 B, drawn 38908 B, ratio 9.93 (bar 4.9); data-triangles 9066, STL header 9066`. The `href after showModel` step makes the STL body 10 bytes so `showModel` throws, then asserts the href is still absent and `aria-disabled=true` (`:357-371`). `PNG_RATIO_BAR = 4.9` is derived and recorded in `browser_session.py:53-62` from two hosts' readings. The one production line is present at `app.js:314`: `canvas.dataset.triangles = String(geometry.attributes.position.count / 3);`. Behavior-dependent truth ("href set only after showModel returns") has a behavioral test that passed, and a recorded red break (`setDownloads` moved above `showModel`). |
| 2 | Interactions, links and baselines proved: 422 marks field via `ctx.fields` and names it; warnings equal `/api/info` exactly; every hash field reaches the form and the sent query equals the hash on fresh load, Reset and `hashchange` (debounce waited on content); 44 golden request sets pinned; `#root_shape=bogus` pinned as today and filed as debt; each assertion seen red once | VERIFIED | `invalid field marked`: `bore_flat=3` (ctx.fields path) and `teeth=2` (loc path); expectations come from the API's own 422 body for the very query the page sent (`:375-410`); `expect(...).to_have_text(texts)` and the marked-set equality. Observed: `marked ['D-flat']` and `marked ['Teeth']`. `warning rendered`: `rendered_warnings == warnings` list equality on links answering 2, 1 and 0 warnings (observed `[2, 1, 0]`). `link round trip`: `_assert_link_applied` on fresh load (second page), `hashchange`, the default-dropped case and Reset. Waits are `expect_request` on `/api/info`, not on status or href. `golden sweep`: `tests/regression/golden_requests.json` holds 44 records and its key set equals `pre_v0_2.json`'s 44 (checked by script), 44 distinct queries; the test is `pinned[name] != swept[name]` per record and passes. `root_shape=bogus`: pinned (select reads `''` at index -1, page sends `teeth=22`, API says 422); debt file `docs/tech_debt/active/2026-10-10-root-shape-bogus-loads-a-blank-select.md` exists. `bench/RESULTS.md` "Seen red once (Phase 21)" holds 25 rows with the deliberate break and first failure line for every step and pin. |
| 3 | The harness cannot lie: real `uvicorn` on a pre-bound `--fd` socket, `start_new_session=True`, process group killed, survivors check; repeatable at `-n 8`; missing shell fails naming the install command with no skip path; `playwright` pinned exactly in `[dev]`, no `pytest-playwright`, default shell, never `channel=`; `mypy --strict` passes | VERIFIED | `browser_session.py:serve` binds `127.0.0.1:0`, passes `pass_fds=(fd,)` and `--fd`, `start_new_session=True`, scrubs `SPUR_*` from the env, waits for a non-null `/api/health` `pool`. `stop_group` does SIGTERM then SIGKILL to the group and `pytest.fail`s on survivors; the floor `>= MIN_GROUP_MEMBERS` is asserted first so a zero is a real zero (observed `server group members before the kill: 3`). Fail-closed observed live: my first run, with no `PLAYWRIGHT_BROWSERS_PATH`, was a FAILED test (not skip, not ERROR) with `run \`playwright install --only-shell chromium\``; the second run with the stamp's path passed. `test_browser_pins.py` (AST scan for `importorskip/skip/skipif/xfail/pytestmark/getenv`, `environ`, `channel=`; exact pin regex; closure and Dockerfile free of playwright; `pytest_playwright` not importable) passes, 3 of 3. `pyproject.toml` dev: `playwright==1.63.0`. `git diff a310cd3 HEAD` on `requirements.txt`, `Dockerfile` and `docker/` is empty (L11). `mypy --strict` on the four new test modules: `Success: no issues found in 4 source files`. `ruff check tests src`: all passed. `-n 8` repeat evidence is recorded in `bench/RESULTS.md` (21-06 admission readings) and the whole 1226-test gate passed at `-n 8` locally and `-n 4` on CI. I did not re-run it, per instruction. |
| 4 | The gate admits the browser at a measured price: inside `make verify` and CI `test (3.12)`, installed by a Makefile stamp with isolated `PLAYWRIGHT_BROWSERS_PATH`; excluded from `verify.fast` and `test-image`; `HEAVY_TEST_FILES` pin extended and seen red; `bench/RESULTS.md` isolated and A/B cost; one `Lxx` amends L13 and L36, restates L11; idea retired | VERIFIED | `Makefile`: `BROWSER := $(VENV)/.browser`; `export PLAYWRIGHT_BROWSERS_PATH := $(abspath $(VENV))/ms-playwright`; `$(BROWSER): $(STAMP)` runs `playwright install $(BROWSER_INSTALL_ARGS) --only-shell chromium`; `test: $(STAMP) $(BROWSER)`; `test.fast` and `test-image` carry `--ignore=tests/test_browser.py`; `golden.regen: $(STAMP) $(BROWSER)`. `.venv/ms-playwright` holds the shell; the host cache is untouched by design. CI: `.github/workflows/ci.yml` runs `make verify PYTHON=python` with `BROWSER_INSTALL_ARGS: --with-deps`. `tests/test_hooks.py:25`: `HEAVY_TEST_FILES = (..., "test_browser")`, with assertions at `:128` and `:171`; `tests/test_hooks.py` passes (6 of 6), and the red break is recorded in the "Seen red" table. `bench/RESULTS.md` "Browser test of the viewer (Phase 21)" holds the isolated reading (4.23 s serial, 4.57 s at `-n 2`), the six-run A/B (B minus A -2.47 s inside a 47.09 s spread, reported honestly as not separable from load), and the human's `accept`. `docs/architecture/decision_log.md:2299` L39 exists with the amendments, the named production line and L11 restated. The idea is in `docs/ideas/retired/` and the INDEX row points there. |
| 5 | The Linux path is proved on a real `ubuntu-latest` run: installs the shell, `tests/test_browser.py` green with webgl2 asserted, run id and wall time recorded in `bench/RESULTS.md` | VERIFIED | `gh run view 38059369744`: `conclusion: success`, `headSha: 88df5cf9610e199203b56b9ae6f18a9dc0125953`. The saved log shows `python -m playwright install --with-deps --only-shell chromium`, `Downloading Chrome Headless Shell 153.0.8010.12`, and `1226 passed in 887.92s`. `bench/RESULTS.md` records run id, head, wall time (16 min 8 s) and the earlier 38044109910 spike. The `git diff 88df5cf HEAD` over `src tests Makefile pyproject.toml .github` is empty, so the CI-verified code is the code now on the branch. webgl2 is the first assertion of the single test function and a pass means it held; there is no skip path (pins). Caveat in Advisory below: the pytest `-q` log does not print per-test names, so "test_browser ran" rests on the absence of any skip path plus the test being collected by `make test`, not on a named PASSED line. |

**Score:** 5/5 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tests/test_browser.py` | scenario function with all steps | VERIFIED | 614 lines, substantive, passes under my run |
| `tests/browser_session.py` | server fixture, launch, typed evaluate wrappers, sweep | VERIFIED | 382 lines, imported by the test and `capture_requests.py` |
| `tests/capture_requests.py` | the only writer of the golden pin | VERIFIED | reuses `serve`/`launch`/`sweep`; wired to `make golden.regen` |
| `tests/regression/golden_requests.json` | 44 pinned query strings | VERIFIED | 44 records, key set equals `pre_v0_2.json`, 44 distinct |
| `tests/test_browser_pins.py` | no-skip, exact pin, default shell pins | VERIFIED | 3 of 3 pass |
| `tests/test_hooks.py` (modified) | heavy-file and `--ignore` pins | VERIFIED | `test_browser` in `HEAVY_TEST_FILES`; 6 of 6 pass |
| `src/spur/static/app.js` | one added line | VERIFIED | `app.js:314`, the only `src/` change since `a310cd3` |
| `Makefile`, `pyproject.toml`, `.github/workflows/ci.yml` | stamp, pin, CI install | VERIFIED | diffs read above |
| `bench/RESULTS.md`, `docs/architecture/decision_log.md` (L39) | readings, `Lxx` | VERIFIED | sections present and cross-checked above |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `make test` | headless shell | `$(BROWSER)` stamp prerequisite | WIRED | `test: $(STAMP) $(BROWSER)`; pinned by `test_the_whole_gate_installs_the_browser...` |
| `make verify` | `tests/test_browser.py` | `test` recipe with no `--ignore` | WIRED | only `test.fast` and `test-image` ignore it |
| `showModel` | `canvas[data-triangles]` | `app.js:314` | WIRED | 9066 equals 9066 observed |
| `update()` | `#dl-stl` href | set after `showModel(buf)` | WIRED | failed-parse break leaves href unset |
| `make golden.regen` | `golden_requests.json` | `capture_requests.py` | WIRED | the test only reads the pin |
| CI `test (3.12)` | browser install | `BROWSER_INSTALL_ARGS: --with-deps` into the stamp | WIRED | log line seen |

### Data-Flow Trace (Level 4)

| Artifact | Data | Source | Real data | Status |
|----------|------|--------|-----------|--------|
| form fields | schema properties | live `/api/schema` fetched at test time | Yes (31 fields, 7 groups) | FLOWING |
| canvas | STL geometry | real `/api/model.stl` build through the pool | Yes (9066 triangles) | FLOWING |
| warnings and 422 text | `/api/info` | real server, compared with an independent HTTP call | Yes | FLOWING |
| golden pin | queries the page sent | real page sweep, not a Python copy of `gearQuery()` | Yes | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Browser test, whole scenario | `PLAYWRIGHT_BROWSERS_PATH=.venv/ms-playwright .venv/bin/python -m pytest tests/test_browser.py -n0 --no-cov -q -p no:cacheprovider -s` | `1 passed in 3.37s`, all 11 steps printed | PASS |
| Fails closed without the shell | same, with the variable unset | `1 failed`, message names `playwright install --only-shell chromium` | PASS (the intended failure) |
| Pins | `pytest tests/test_browser_pins.py` | 3 passed | PASS |
| Hook pins | `pytest tests/test_hooks.py` | 6 passed | PASS |
| Strict typing | `mypy --strict` on the four browser modules | no issues | PASS |
| Lint | `ruff check tests src` | all checks passed | PASS |
| CI run | `gh run view 38059369744 --json conclusion,headSha` | success at `88df5cf` | PASS |

### Probe Execution

SKIPPED: the phase declares no `probe-*.sh`.

### Requirements Coverage

All 10 phase IDs appear in PLAN frontmatter and in REQUIREMENTS.md (marked `[x]` and `Complete`). No orphans: every Phase 21 row in the traceability table is claimed by at least one plan.

| Requirement | Source Plan(s) | Status | Evidence |
|-------------|----------------|--------|----------|
| REQ-browser-server-fixture | 21-01, 21-02, 21-06 | SATISFIED | `serve()`: pre-bound socket, `--fd`, new session, group kill and survivor check; observed group of 3 |
| REQ-browser-form-from-schema | 21-03 | SATISFIED | `form from schema` step, counts from schema at test time, theme vars |
| REQ-browser-first-build-drawn | 21-01, 21-02 | SATISFIED | webgl2 first, PNG ratio 9.93 against bar 4.9, triangles 9066 equal 9066, href-after-showModel step |
| REQ-browser-invalid-field-marked | 21-03 | SATISFIED | both 422 paths, text and marked set equal the API's body |
| REQ-browser-warning-rendered | 21-03 | SATISFIED | list equality on 2, 1 and 0 warnings |
| REQ-browser-link-round-trip | 21-04 | SATISFIED | fresh load, `hashchange`, default-dropped, Reset; content-based waits |
| REQ-browser-golden-request-sets | 21-05 | SATISFIED | 44 pinned, key set equals the fixture, compared per record |
| REQ-browser-fails-closed | 21-01, 21-06 | SATISFIED | observed failing live; AST pin forbids any skip path |
| REQ-browser-in-the-gate | 21-06, 21-07, 21-08 | SATISFIED | Makefile, CI, hook pins, `bench/RESULTS.md`, L39, idea retired |
| REQ-browser-stack-pinned | 21-01, 21-02, 21-06, 21-08 | SATISFIED | `playwright==1.63.0`, no plugin, no `channel=`, strict mypy, real ubuntu-latest run |

### Anti-Patterns Found

None blocking. `TBD`, `FIXME` and `XXX` grep over the four new test modules: no hits. No unreferenced debt markers in files this phase modified. `ruff` clean.

### Advisory (open code-review findings, not goal gaps)

`21-REVIEW-DISPOSITION.md` lists 7 findings, all still `open`, 0 critical: WR-01 (`stop_group` can leak the group if `ps` fails), WR-02 (the `MIN_GROUP_MEMBERS` comment says uvicorn plus 2 workers; the 3 members are uvicorn, the resource tracker and one worker), WR-03 (the missing-shell message says `make test` fixes it, but a current stamp makes `make test` a no-op for the install), and IN-01 to IN-04. None breaks a must-have. WR-02 is documentation, WR-01 is a teardown edge case on a host where `ps` fails, and WR-03 does not stop the message naming `playwright install --only-shell chromium`. The CLAUDE.md rule "don't leave debt unfiled" suggests the orchestrator either fix them or file them under `docs/tech_debt/active/` before closing the phase. This does not change the verdict.

The CI log is quiet-mode pytest, so it shows `1226 passed` and not a named `test_browser` PASSED line. The inference that the file ran on ubuntu-latest rests on three things: `make test` collects it, no skip path can exist (AST pin), and the 21-02 spike logged webgl2 renderer output. I rate that sufficient, not a gap.

### Deferred Items

None.

### Human Verification Required

None. The phase's own human decisions (the price `accept` at `3e8e8f9`, the opening of PR #33) are already recorded.

### Gaps Summary

No gaps. Every ROADMAP success criterion is backed by code I read and by a run I observed: the scenario passes end to end under my own process, it fails closed with the install command when the shell is absent, the 44-record pin matches the fixture, the gate wiring exists in Makefile and CI, the CI run at the current code's head is green, and the cost and decision records (`bench/RESULTS.md`, L39) are in place.

---

_Verified: 2026-10-10_
_Verifier: Claude (gsd-verifier)_
