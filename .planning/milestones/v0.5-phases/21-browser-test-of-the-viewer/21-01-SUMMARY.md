---
phase: 21-browser-test-of-the-viewer
plan: 01
subsystem: testing
tags: [playwright, chrome-headless-shell, webgl2, uvicorn, pytest, makefile]

requires:
  - phase: 20
    provides: the shipped viewer (app.js) and the gate this plan keeps green
provides:
  - playwright==1.63.0 pinned exactly in the dev extra, its headless shell installed under .venv by a Makefile stamp
  - canvas.dataset.triangles, the milestone's one production line
  - tests/browser_session.py (serve, group_members, stop_group, launch, typed evaluate wrappers, stl_triangles, step)
  - tests/browser_scenarios.py, the staging scenario (webgl2, form built, first build drawn, href after showModel)
  - the macOS spike readings and seven assertions seen red once, in bench/RESULTS.md
affects: [21-02, 21-03, 21-04, 21-05, 21-06, 21-07, 21-08, 23, 24]

actuals:
  tokens: 7900
  tasks: 3
  commits: 4

plan_head_before: a310cd3ff119c22d6fcc8c6019815b8f3738e1b6
plan_head_after: 505ebe71ee1c66dce316b099df0800b1f5f3843f
commits: 4

tech-stack:
  added: [playwright 1.63.0 (dev only), pyee 13.0.1 (transitive), greenlet 3.5.6 (transitive)]
  patterns:
    - server on a pre-bound 127.0.0.1 socket passed by --fd, own session, group kill with a ps-scoped survivor check
    - browser launched in the test body so a missing shell is FAILED with the install command
    - page.evaluate assigned to object and narrowed (mypy --strict, no Any)

key-files:
  created:
    - tests/browser_session.py
    - tests/browser_scenarios.py
  modified:
    - pyproject.toml
    - Makefile
    - src/spur/static/app.js
    - bench/RESULTS.md

key-decisions:
  - "PNG_RATIO_BAR is 4.9: PD-03 applied to the macOS reading 9.93 (blank 3,917 B, drawn 38,908 B); 21-02 re-sets it from the lower of two hosts"
  - "serve() asks its caller whether the group floor applies at teardown: pool workers start on first use (2 members before the first build, 3 after), so a test that failed before building reports once"
  - "BUILD_WAIT_MS stays 45,000 ms: the slowest build-bound step read 2.53 s, under PD-04's 15 s"
  - "The headless shell lives under the absolute .venv/ms-playwright; the host cache listed the same three entries before and after"

patterns-established:
  - "A deliberate break is made in the working tree, run once, its first failure line copied, then reverted with git checkout -- <file> before the next"
  - "Every asserted bar sits beside the reading that set it, in a comment and in bench/RESULTS.md"

requirements-completed: [REQ-browser-server-fixture, REQ-browser-first-build-drawn, REQ-browser-fails-closed, REQ-browser-stack-pinned]

coverage:
  - id: D1
    description: "playwright==1.63.0 pinned exactly in dev; the shell installs under .venv/ms-playwright through the $(BROWSER) stamp; the host cache is unchanged"
    requirement: REQ-browser-stack-pinned
    verification:
      - kind: other
        ref: "make .venv/.browser; ls ~/Library/Caches/ms-playwright before and after (chromium_headless_shell-1228, chromium-1228, ffmpeg-1011)"
        status: pass
    human_judgment: false
  - id: D2
    description: "A real uvicorn on a pre-bound socket in its own session, torn down by group kill with no survivor and a non-vacuity floor of 3"
    requirement: REQ-browser-server-fixture
    verification:
      - kind: integration
        ref: "tests/browser_scenarios.py#test_the_shipped_viewer_in_a_real_browser"
        status: pass
    human_judgment: false
  - id: D3
    description: "webgl2 asserted first; the first part drawn against a blank control above PNG_RATIO_BAR; data-triangles equal to the STL header; the href only after showModel"
    requirement: REQ-browser-first-build-drawn
    verification:
      - kind: integration
        ref: "tests/browser_scenarios.py#test_the_shipped_viewer_in_a_real_browser"
        status: pass
    human_judgment: false
  - id: D4
    description: "A missing headless shell is a FAILED test naming playwright install --only-shell chromium"
    requirement: REQ-browser-fails-closed
    verification:
      - kind: other
        ref: "PLAYWRIGHT_BROWSERS_PATH=<empty dir> pytest tests/browser_scenarios.py -> 1 failed (bench/RESULTS.md, Seen red once)"
        status: pass
    human_judgment: false

duration: 28min
completed: 2026-10-10
status: complete
---

# Phase 21 Plan 01: The Browser Spike Summary

**Pinned playwright 1.63.0 with its headless shell under .venv, a real uvicorn on a pre-bound socket, and a staging scenario that draws the first part in Chrome Headless Shell with `data-triangles` equal to the STL header (9066 = 9066)**

## Performance

- **Duration:** 28 min
- **Started:** 2026-10-10T09:17:55Z
- **Completed:** 2026-10-10T09:46:12Z
- **Tasks:** 3 (Task 1 a checkpoint, answered before this agent began)
- **Files modified:** 6 (4 modified, 2 created)

## Accomplishments

- The tracer works end to end on macOS: webgl2 present (SwiftShader), the form built from the schema (31 fields), the first part drawn at 9.93x its blank control, the scene's triangle count equal to the STL header, the download link absent until `showModel` returns.
- Seven deliberate breaks each seen red once and reverted (`bench/RESULTS.md`, `### Seen red once (Phase 21)`); the fail-closed run reads `1 failed` with the literal install command.
- The staging module stays uncollected: `make verify` read `1220 passed in 167.55s (0:02:47)`, coverage 97.92 % against the 96 % floor, at the final HEAD.

## Task Commits

1. **Task 1: legitimacy checkpoint** - no commit (read-only; answered `approved`)
2. **Task 2: tracer** - `0c89e9b` (build: pin and install stamp), `c479d15` (test: app.js line, session helper, staging scenario)
3. **Task 2 follow-up: deviation fix** - `593de97` (fix: early failures reported once)
4. **Task 3: readings and red-once evidence** - `505ebe7` (docs)

**Plan metadata:** the commit that carries this file (docs: complete plan)

## Task 1 approval (verbatim)

The human's answer to the blocking legitimacy checkpoint was `approved`, meaning pin `playwright==1.63.0` exactly in the `[dev]` extra. The dry run the previous agent reported, and the human saw:

| Package | Version | Wheel |
|---------|---------|-------|
| playwright | 1.63.0 | `playwright-1.63.0-py3-none-macosx_11_0_arm64.whl` |
| greenlet | 3.5.6 | `greenlet-3.5.6-cp312-cp312-macosx_11_0_universal2.whl` |
| pyee | 13.0.1 | `pyee-13.0.1-py3-none-any.whl` |

PyPI metadata read for playwright 1.63.0: author Microsoft Corporation; homepage `https://github.com/Microsoft/playwright-python`; requires `pyee<14,>=13` and `greenlet<4.0.0,>=3.1.1`; license field empty; wheels uploaded 2026-09-15; a manylinux x86_64 wheel is present. pyee: author Josh Holbrook (14.0.0 newest, capped `<14`, so 13.0.1). greenlet: author Alexey Borzenkov. None of the three entered `requirements.txt`, the `Dockerfile` or `docker/refresh-requirements.sh`. `pip list` after the install showed exactly these three versions.

## Files Created/Modified

- `pyproject.toml` - one line, `"playwright==1.63.0",` in the dev extra
- `Makefile` - `BROWSER_INSTALL_ARGS ?=`, `BROWSER := $(VENV)/.browser`, the absolute `export PLAYWRIGHT_BROWSERS_PATH`, rule `$(BROWSER): $(STAMP)`; `test`, `test.fast`, `.PHONY` untouched
- `src/spur/static/app.js` - the comment and `canvas.dataset.triangles = String(geometry.attributes.position.count / 3);` after `scene.add(mesh, edges);`
- `tests/browser_session.py` - serve, group_members, stop_group, launch, five typed evaluate wrappers, stl_triangles, step; constants BUILD_WAIT_MS 45,000, MIN_GROUP_MEMBERS 3, PNG_RATIO_BAR 4.9
- `tests/browser_scenarios.py` - the module fixture `server` and `test_the_shipped_viewer_in_a_real_browser`
- `bench/RESULTS.md` - `## Browser test of the viewer (Phase 21)` with the spike readings and the red-once table

## Readings (full tables in bench/RESULTS.md)

- Install: 20.46 s `real` (includes the `$(STAMP)` pip re-resolve), 198 MB under `.venv/ms-playwright`. Host cache before and after: `chromium_headless_shell-1228`, `chromium-1228`, `ffmpeg-1011`.
- Renderer: `ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (LLVM 10.0.0) (0x0000C0DE)), SwiftShader driver)`. Shell 153.0.8010.12.
- Canvas PNG: blank 3,917 B, drawn 38,908 B, ratio 9.93. PD-03 gives 9.93 / 2 = 4.96, rounded down to 4.9, which is not under 2.0, so it is asserted and no decision checkpoint was needed. Reading context: Apple M5 Max, macOS 27.0.1, load 3.3, 2026-10-10, HEAD a310cd3 (tree) then 593de97.
- Triangles: `data-triangles` 9066, STL header 9066.
- Isolated cost: 3.40 to 3.43 s of pytest (3.59 to 3.64 s with `make`) over three runs at load 4.7, beside the research's 3.21 s serial figure.
- Fixture: pool ready 0.20 to 0.21 s after spawn; 3 group members before the kill; group gone 0.24 to 0.25 s after SIGTERM.
- `expect` default timeout: 5000 ms. Slowest build-bound step 2.53 s, so `BUILD_WAIT_MS` stays 45,000 ms.
- `git status --porcelain --ignored` after a green run: nothing outside `.venv/` and the ignores already in place.

## Decisions Made

- The ratio bar is 4.9 (above). The mesh-less scene (grid and background) reads 4.24, so the bar separates a gear from an empty scene by a narrow margin on this host; 21-02 sets the final bar from the lower of two hosts.
- `serve(floor_applies=...)`: see Deviations.
- A step named `form built` wraps the form-count and parked-STL waits (the plan left them unnamed); the stricter `form from schema` step stays 21-03's.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] A test that failed before its first build reported two failures**
- **Found during:** Task 3 (the `webgl2` break)
- **Issue:** the non-vacuity floor (3 members before the kill) fired in teardown even when the test had failed before any build. Pool workers start on first use: the group read 2 members after `/api/health` reported a pool and 3 after one preview build. The run read `1 failed, 1 error`, which breaks the plan's own `1 failed` requirement for a missing shell (D-02).
- **Fix:** `serve()` takes a `floor_applies` callable (default: always); the scenario fixture passes a check that `request.session.testsfailed` did not rise, so a failed test is reported once and a passing run still asserts the floor.
- **Files modified:** `tests/browser_session.py`, `tests/browser_scenarios.py`
- **Verification:** the `webgl2` break re-run reads `1 failed`; the fail-closed break reads `1 failed in 0.69s`; the passing run still prints `server group members before the kill: 3`.
- **Committed in:** `593de97`

### Other departures

- The app.js comment is one line (the plan allowed two lines of addition in total, comment and statement).
- Task 3's "orphan check" break needed a manual clean-up: the two deliberately orphaned pool workers (pids 66059 and 66066) were killed by group id afterwards, and an aborted timing script left one uvicorn (group 66634) that was killed the same way. `ps` showed no `uvicorn spur.app:app --fd` process afterwards.

**Total deviations:** 1 auto-fixed (Rule 1). **Impact:** one correctness fix in the new test code; no product change beyond the planned line.

## Issues Encountered

- The plan commit ledger the previous agent reported did not exist on disk; it was created at the start of this continuation with the base `a310cd3` (HEAD had not moved, no plan commit existed).
- `gsd_run` was not on PATH in the Bash tool; the resolver block was used for the state updates.
- No gate or test failure occurred, so there are no failed logs to file under `investigation/` and none to match against the resource-tracker flake signature.

## Handoffs

- **21-05 (the sweep and capture script):** the sweep aborts the STL route, so it builds nothing and the pool holds 2 members at teardown. Call `serve(floor_applies=lambda: False)` there, or build once; the default asserts 3.
- **21-02:** re-set `PNG_RATIO_BAR` from the lower of the macOS (9.93) and ubuntu-latest ratios; check `ps -A -o pgid=,stat=,pid=` columns on Linux procps (RESEARCH A4).
- **21-06:** the `server` fixture reads `request.session.testsfailed`; keep it when the module is renamed.

## Known Stubs

None.

## Threat Flags

None. The only new network surface is the test fixture's socket on 127.0.0.1, which the plan's threat model (T-21-01) already covers.

## User Setup Required

None - no external service configuration required. `make test` will run the shell install stamp once 21-06 admits it; until then `make .venv/.browser` installs it.

## Next Phase Readiness

21-02 can run the Linux spike: the module, the stamp and the bar mechanism exist. No blockers.

## Self-Check: PASSED

- Files found: `tests/browser_session.py`, `tests/browser_scenarios.py`, `bench/RESULTS.md`, `src/spur/static/app.js`, `pyproject.toml`, `Makefile`
- Commits found on HEAD: `0c89e9b`, `c479d15`, `593de97`, `505ebe7`
- Plan checks re-run: quick run `1 passed`; `make lint typecheck` clean; `git diff --exit-code 592506f` over the fixture, `tests/test_api.py` and the product modules other than app.js exits 0; `make verify` `1220 passed in 167.55s (0:02:47)`; the Task 3 readings script printed `21-01 readings and 7 red rows recorded`.

---
*Phase: 21-browser-test-of-the-viewer*
*Completed: 2026-10-10*
