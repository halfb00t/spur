# Project Research Summary

**Project:** spur — milestone v0.6 Clean Ledger (debt sweep)
**Domain:** verification gate, test harness, CI and one form behaviour of a shipped parametric gear generator
**Researched:** 2026-10-15
**Confidence:** MEDIUM-HIGH (mechanisms and repo facts HIGH; the 98 % hang and Ubuntu 26 on a real runner unresolved by design)

Tags follow the inputs: **MEASURED** (run 2026-10-15 by a researcher), **READ** (source/repo/fetched page), **UNVERIFIED** (inference). **READ-from-STACK** marks a STACK.md MEASURED claim the synthesis did not re-run.

## Executive Summary

v0.6 adds no feature and no `GearParams` field. It makes the gate fail with a cause or pass, retires the open `must` debt, triages every open review info finding, and changes exactly one behaviour: a bogus shared link is refused instead of silently building the default part. Every valid link, the 44-record fixture and `tests/regression/*.json` stay byte-identical to `v0.5` (L05, L26). Nothing new is installed; Playwright stays 1.63.0 and Python 3.12 (L23).

Central result: the `resource_tracker` flake is no longer a "run loops and hope" item. STACK located the cause (READ-from-STACK): three `tests/test_pool.py` tests leave one executor's five semaphores to cyclic garbage; a GC pass landing inside the tracker lock turns the CPython 3.12 reentrancy warning into five unraisable errors under `filterwarnings = error`. Test hygiene — not xdist, coverage or `src/spur`. A 12-line stdlib script reproduces it on demand, and a forced-GC check separated the fix arms. The 98 % hang stays evidence-capture only (dump-only `faulthandler_timeout` plus `-v --durations`), no guessed fix.

Main risks are over-claiming and pin breakage. Mitigations: tag every claim; never write "flake gone" — write "located, fixed from a reproduction, acceptance recorded"; see each new guard test red first; edit `app.js` around `tests/test_api.py`'s token pins; keep the date-gated Ubuntu 26 item from blocking the close.

One recurring defect is on nobody's list. **`main` CI is red on 2 of the last 8 runs** (orchestrator-verified: 38347283201 at 94dfc19, 38680454993 at 26ddd74 = the v0.5 tag), both at browser step "twin selectors"; PR runs of the same commits were green. Not filed in `docs/tech_debt`. It joins the gate-reliability phase.

## Conflicts Between the Four Files — Resolved

| # | Conflict | Winner | Why |
|---|---|---|---|
| C1 | **Flake plan.** PITFALLS/ARCHITECTURE: whole-suite `-n 8 --cov` vs `--no-cov` loops with a pre-committed stop rule. STACK: located cause, reproduction, forced-GC check. | **STACK** (READ-from-STACK) | A deterministic reproduction satisfies L08. STACK explains why loops cannot separate arms: 2026-10-09 isolation read 0/60 because garbage only matters when GC lands in a µs lock window. `--no-cov` also fails (1/1 whole-suite, 1/4 two-file, `ubuntu:26.04` container), so coverage is not necessary. Loops demoted to one before/after acceptance run keeping PITFALLS' discipline (committed cap and arms, signature-classified reds, no "resolved" on a quiet fortnight). PITFALLS' `gc.set_threshold` amplifier dropped (STACK: 0/6, hides the bug). ARCHITECTURE's test `shutdown(wait=True)` superseded by STACK's arms. |
| C2 | **Hang evidence.** STACK: `faulthandler_timeout=120` + `-v --durations`. PITFALLS: flushed per-worker journal. `tests/test_hooks.py` pins the recipe. | **STACK by default, journal as fallback** | STACK MEASURED under xdist + cov that `-v` prints controller-side test ids on start and finish and worker stack dumps reach the terminal; PITFALLS had both UNVERIFIED/wrong. ARCHITECTURE READ the pin: it compares the two pytest lines only through `-n <N>`, so a flag after the worker count is safe; an ini option in `pyproject.toml` applies to both targets with no recipe fork. Journal (~10 lines in `conftest.py`, timestamps, survives SIGTERM) only if `-v` proves insufficient. All three agree `faulthandler_timeout` cannot see a post-last-test stall. |
| C3 | **Phase labels.** ARCHITECTURE 26–29; PITFALLS A–F. | **ARCHITECTURE numbering** | Continues from Phase 25. PITFALLS' letters kept as scope tags. |
| C4 | **Slug totality scope.** Milestone/FEATURES: "every refusal reason". ARCHITECTURE/PITFALLS: 2 of 6 reasons (`bracket degenerate`, `curve invalid`) are unreachable by validated parameters. | **ARCHITECTURE + PITFALLS** (both MEASURED; `tests/test_calc.py:1603-1604`) | Real seeded cases for reachable reasons with per-bucket non-empty asserts; the two unreachable forced by patching `spur.calc._root_curve` and labelled forced. PITFALLS: uniform draws hit the cheap branch 89 %, so stratify to the undercut region. The milestone sentence is met in a qualified form. |
| C5 | **Failed-build name test.** FEATURES: private key (`face_width=7.7`). ARCHITECTURE/PITFALLS: `monkeypatch.setattr` a fresh `_BlobCache`. | **monkeypatch** | `_BlobCache` has no `clear()`; a unique-key convention is the hand-kept rule being removed. |
| C6 | **Bogus-link breadth.** FEATURES (MEASURED in a real browser): general — enums plus non-numeric text in number boxes. ARCHITECTURE: enums in, number boxes filed. PITFALLS: enums only, empty-string policy undecided. | **FEATURES for the facts; scope is a human decision** | Only FEATURES ran it: `teeth=abc`, `mate_teeth=abc` silently build the default today. `recess_sides=bogus` is the same defect regardless, so the fix must be generic over enums (L02; `test_api.py:277-283` forbids per-field code). |
| C7 | **Info 19 IN-01/02.** FEATURES/ARCHITECTURE: fix (one `model.py` line + bench cleanup). PITFALLS: refactor, defer. | **FEATURES + ARCHITECTURE, guarded** | Cheap; the fixture proves no number moves. Own commit; `tests/test_model.py:899` patches `_chamfer_tips` with a 3-arg lambda and must change with the signature. Lowest-risk row to drop if the human wants no `model.py` diff. |
| C8 | **Launch-failure message.** STACK: run `playwright install` on every `make test` (0.24 s when present). Others: message-only. | **Message-only** | Smaller; no `Makefile` stamp change, no `tests/test_hooks.py` pin churn. File STACK's idea in `docs/ideas/`. Keep the literal `playwright install --only-shell chromium` `test_browser_pins.py:105-127` requires. |
| C9 | **Hook pin fix.** ARCHITECTURE: strip `PYTEST_ARGS` in `_make_env()`. STACK: `PYTEST_ARGS=` on the dry-run command line. | **Either; test both forms** | STACK MEASURED both work on GNU Make 4.4.1. PITFALLS: the command-line form is what bit 21-07, so the new test must be red for both forms before the fix. |
| C10 | **Ubuntu 26 timing.** STACK: pre-classify now on a throwaway `runs-on: ubuntu-26.04` PR. ARCHITECTURE: optional. PITFALLS: human decision. | **Recommend, flagged for the human** | The label exists today; the rollout runs 2026-10-19 → 2026-11-19, so "first run naming 26" is not a clean date. STACK's container run passed the Playwright install and the browser test (5 passed). A real runner is unproven. Pinning `ubuntu-24.04` stays the human's call. |

## Key Findings

### Stack (STACK.md)

Add nothing. Hold pytest 9.1.1, pytest-xdist 3.8.0, pytest-cov 7.1.0, `playwright==1.63.0` (1.64.0 out 2026-10-13 would move the headless-shell revision and the canvas-PNG bar), CPython 3.12. 3.12 is security-only, so gh-131788 will not arrive there — fix in tests.

- **Flake fix (READ-from-STACK):** module-level autouse fixture in `tests/test_pool.py` whose teardown calls `gc.collect()` (arm B, 4 lines); optionally `del manager` in the three producer tests (arm C, 3 lines). Forced-GC check: baseline fails 3/3, B and C 0/3. Container natural loop: baseline 1/10, B and C 0/10 — consistent, not conclusive. Cost ~10 ms/test in one file. Do not touch `src/spur/pool.py`; do not filter the warning.
- **Producers:** `test_a_wedged_build_is_terminated_and_its_worker_replaced`, `test_a_stale_executor_timeout_is_a_build_timeout_not_an_attribute_error`, `test_three_same_tick_same_slot_timeouts_each_end_in_a_documented_refusal`. The failing test is a victim of whichever GC pass fired, never the producer.
- **Hang:** `faulthandler_timeout = 120` in `[tool.pytest.ini_options]` (dump-only) and `-v --durations=25` in the `test` recipe. 120 s ≈ 2.3× the estimated CI slowest test (~52 s); re-read from the first CI `--durations` (UNVERIFIED for CI). Evidence runs go through `make` — only `make` exports `PLAYWRIGHT_BROWSERS_PATH`.
- **Small-item facts (MEASURED):** `BuildPool` slots by `hash(p) % workers` with a per-process hash seed, so after two builds the group is uvicorn + `resource_tracker` + 1 or 2 workers — the floor of 3 is a valid non-vacuity bound. `make test-image` has no `.git`, so two `tests/test_bench.py` tests fail with exit 128. `GET /api/info?root_shape=bogus` already answers 422 `literal_error`, so the bogus-link fix is client-side only.

### Features (FEATURES.md)

**Must have (table stakes):**
- **Bogus link refused** through the existing field-agnostic 422 path (`problems()`/`fail()`): server text (L02), fragment keeps the offending token, no STL request, editing the field or Reset clears it, valid links send exactly what they sent. Pin `root_shape=bogus as today` flips in the same commit (`tests/test_browser.py:1754-1808`, `BOGUS_LINK`/`TODAY` `:97-103`); new `L44`; debt file to `resolved/` in that commit.
- The two Phase 22 `must` tests; `stop_group` signal-before-`ps`; group-floor comment + dated corrections under the two `bench/RESULTS.md` rows (readings never rewritten).
- Flake outcome recorded; hang evidence armed (item stays `active`); Ubuntu 26 classified from the whole log.
- Every open info finding of Phases 19, 21–24 dispositioned: 19 rows, 16 distinct (19 IN-03 already resolved; 24 IN-04 already filed; 24 CX-03 duplicates 24 IN-02). ≈15 FIX, 6 CLOSE with a written reason, 1 FILE (stash invalidation, the behavioural half of 24 IN-01).
- The three `nice` items.

**Defer / reject:** client-written error wording; refusing blank values; `type=text` number inputs; refusing unknown keys; a fallback-to-default banner; Phase 10 IN-02 (changes a printed value); hex-warning titles (already an idea); marking the mate box on a `mate_teeth` 422 (file as idea).

**Info findings that are not cosmetic** (PITFALLS: the test can pass vacuously): 24 CX-05 (zero-request assert can pass before the 350 ms debounce), 23 IN-08 (`CUTOUT_STATES` gives the honeycomb gate one open value), 23 IN-11 (`_js_number` range, `-0.0`), 21 IN-03, 21 IN-04.

### Architecture (ARCHITECTURE.md)

No new component. The only runtime edit is one generic branch in `src/spur/static/app.js` (`readHash`/`gearQuery`); everything else is the verification chain.

**Constraints the plans must carry:**
1. `tests/test_api.py:240-241` pins exact lines: the `readHash` line `input.value = h.get(name) ?? defaults[name]`, the `readHash` end, the `gearQuery` token, the Reset line. `test_api.py:277-283` forbids quoted field names outside `DIMS`. The bogus-link code is a pre-pass around the pinned lines, generic over `prop.enum`. A new row-shaped `['word',` table is harvested as a `DIMS` key.
2. `tests/test_hooks.py` pins the recipe prefix, the five heavy files, the `test-image` `--ignore`, the stamps. Hook pin goes first.
3. `tests/test_browser_pins.py::_scan_set()` globs `tests/*browser*.py` with a no-skip spelling scan, so the new `stop_group` unit test lives in a file without `browser` in its name (e.g. `tests/test_group_teardown.py`), well under a second for `make verify.fast`.
4. `git diff --exit-code tests/regression/` empty at every phase close; `bench/RESULTS.md` append-only with dated corrections; next free decision id `L44`; L40 takes a dated amendment, not a rewrite.
5. `make no-fake-done` greps `TODO|FIXME|XXX|HACK|NotImplementedError` as whole words in `*.py *.js *.sh`; `mypy --strict` covers `tests bench scripts docker`; `verify.fast` is killed at 30 s (≈11 s used), so new commit-slice tests must be milliseconds.

### Critical Pitfalls (PITFALLS.md, filtered by the resolutions above)

1. **Declaring the flake gone on a quiet run.** Zero reds in N only bounds the rate near 3/N. The fix rests on the captured reproduction; the acceptance run has its cap and arms committed before it starts; the success line says "located and fixed from a reproduction".
2. **Symptom fixes.** No `filterwarnings` entry, no blanket `ignore::pytest.PytestUnraisableExceptionWarning`, no `shutdown(wait=True)` in `BuildPool`, no rerun plugin. Call arm B a mitigation of the precondition, not a removal of the warning.
3. **Vacuous guard tests.** Slug totality: stratified undercut draws, per-bucket non-empty asserts, local `random.Random(n)`, red against a patched `_junction`/`_root_curve`. Name test: `monkeypatch` self-restores; prove it by pre-seeding the cache so the old test reds.
4. **`stop_group` reorder hazards.** No `proc.poll()`/`wait()` before the signals (PID reuse); keep the SIGTERM grace; a failed `ps` means "survivors unknown" and still fails; the leader-only break (`bench/RESULTS.md` row 21-01) must still red; the unit test cleans up its own group.
5. **L05 trap and pin flip.** Fixture and golden byte-identical to `v0.5`; old pin seen red against the fix, new pin seen red with the fix reverted, both recorded in "Seen red once".
6. **Ubuntu 26.** No fix before classification; one run is not the migration; record the `Image:` line per run in the window; read all three jobs (`test (3.12)`, `vendor-bundle`, `image`); classification table in `bench/RESULTS.md` before any `ci.yml` edit.
7. **Info triage without reasons.** One disposition per finding in its `*-REVIEW-DISPOSITION.md`: `fixed` + sha, `deferred` + path, or `skipped` + one-line reason. Zero `open` at close.

## Implications for Roadmap

Phase numbers continue at 26. PITFALLS' scope letters in brackets. One concern per commit; each debt item retired in its fixing commit.

### Phase 26: Gate Fails With a Cause [A + F1 + cheap gate items]
**Rationale:** the flake, the "twin selectors" red and the hook-pin failure pollute every later gate reading with false reds. Touches `Makefile`, `pyproject.toml`, `tests/test_hooks.py`, `tests/test_pool.py`, `tests/test_browser.py`.
**Delivers, in order:**
1. Hook pin ignores the caller's `PYTEST_ARGS` (env-var and command-line forms both red first).
2. **Twin-selectors race** (runs 38347283201, 38680454993): wait for the STL request, settle past the 350 ms debounce, then take the baseline. Folds in 24 CX-05 and 21 IN-04a (`_follow_link` → `BUILD_WAIT_MS`). File the debt item and retire it in the fixing commit. The mechanism is ARCHITECTURE's ASSUMPTION from two logs with no local reproduction; logs plus a delayed-route red proof serve as the capture.
3. **Flake:** arm B (optionally C) in `tests/test_pool.py` from STACK's reproduction. Acceptance: forced-GC red → green, plus one interleaved before/after run with a pre-committed cap; record effective `-n`, tool versions and signature-classified reds in `bench/RESULTS.md`; retire the item quoting the table.
4. **Hang evidence:** `faulthandler_timeout` + `-v --durations`; one `--durations` reading sets the final timeout; cost priced against the 300 s bar (L43). The item stays `active` and gains a runbook stating the exit-window limit.
5. **`make test-image`:** run it first, read the reds, then the option the human picks.
6. Ubuntu 26 pre-classification on a throwaway PR before 2026-10-19, if the human agrees.

**Avoids:** pitfalls 1, 2, 3 (first part), 6 (partly), 16, 17.

### Phase 27: Ledger Tests and Harness [B + C + F]
**Rationale:** test-only plus one `model.py` line — low behaviour risk; finish before 2026-10-19 where small. `stop_group` must precede Phase 28, whose red-first protocol runs the browser repeatedly.
**Delivers:** slug totality and failed-build name tests (22 IN-01, 24 IN-03 in the same files); `stop_group` fix with a non-browser unit test; group-floor comment and dated corrections under both RESULTS rows (macOS listing MEASURED today: 2 → 3 → 4; Linux listing from a member-command print in the next CI log); text-only launch message; info 21 IN-01/02/03, 22 IN-02, 23 IN-08, 23 IN-11; 19 IN-01/02 and `_host_state`; L40 dated amendment (22 IN-03); draft triage table.
**Avoids:** pitfalls 3 (second part), 4, 7, 8, 12, 13, 15.

### Phase 28: Refuse the Bogus Link [D]
**Rationale:** the only user-visible change, so it needs a decision record (`L44`); edits the most-pinned file. Discuss-phase first with the open decisions below.
**Delivers:** generic `readHash`/`gearQuery` pre-pass (shared `rejected` map per FEATURES, or a stray option per ARCHITECTURE — settled at discuss-phase); `problems()`/`fail()` unchanged; browser step rewritten with both reds recorded; `L44`; `docs/architecture/web-ui.md:80` rewritten; debt item retired. Same file, separate commits: 24 IN-02 wording ("Could not build the form"), 24 IN-01 comment, optionally the 19 IN-04a label. Phase close: `git diff --exit-code tests/regression/` empty; info triage zero `open`.
**Avoids:** pitfalls 5, 12.

### Phase 29: Ubuntu 26 Final Reading [E] — date-gated, last
**Rationale:** cannot be scheduled; the rollout runs 2026-10-19 → 2026-11-19.
**Delivers:** starting at the first `ubuntu-latest` run whose `Set up job` names 26.04, classification from the whole log of all three jobs before any `ci.yml` edit. Green → dated `bench/RESULTS.md` reading, item resolved. Red → offer `runs-on: ubuntu-24.04` to the human only. If no 26.04 run by the close, the milestone closes with the item open and its trigger restated.

### Research Flags

- **Needs discuss-phase, not more research:** Phase 28 (scope, label, mechanism); Phase 26 `test-image`.
- **Needs a first real measurement before planning:** `make test-image` (never run in research); CI `--durations` for the timeout; a real Ubuntu 26 runner.
- **Standard patterns (skip research-phase):** Phase 27; Phase 26 items 1–3; Phase 29 (procedure fixed by the debt file).

## Open Human Decisions (listed, not decided)

1. **Bogus-link scope.** (a) Enum-only (`root_shape`, `recess_sides`) vs also non-numeric number-box text (`teeth=abc`, `mate_teeth=abc`) — FEATURES recommends including number boxes, MEASURED as silently building the default. (b) Blank (`root_shape=`, `teeth=`): keep "blank means default" (FEATURES recommends; the page defines it today) or refuse (the API answers 422). `L44` must state whichever boundary is chosen.
2. **IN-04a label change.** Make `['root_fillet', 'Root fillet used']` a function of the document while a hob root is in force. Text-only — no part, number or request moves — but a second visible change beside the bogus link. Fix, or close with a reason?
3. **Phase 18 and Phase 10 info findings — in or out.** Outside the milestone text, still `open`: Phase 18 IN-01..08, Phase 10 IN-01/02. FEATURES recommends closing 18 IN-02, IN-06 (overtaken), fixing the IN-07 docstring line, filing the rest as one `nice` item (trigger: `bench/trochoid.py` or `calc.cutter` next touched), and filing Phase 10 IN-02 as a decision (it changes a printed value). Liveness of most rows UNVERIFIED.
4. **`faulthandler_exit_on_timeout` — now or later.** Turns a hang into a named failure (MEASURED under xdist + cov) but changes gate semantics, raises the dev floor to `pytest>=9`, and drops coverage data (so `fail_under = 96` adds a second failure line). STACK recommends dump-only now; decide after the first captured hang.
5. **`make test-image` — mount `bench/` and `scripts/`, or exclude by name.** Excluding `tests/test_calc.py` and `tests/test_trochoid.py` (both import `bench`) would gut the image suite. ARCHITECTURE/PITFALLS recommend mounting read-only with `PYTHONPATH=/app/src:/app` and `--ignore` only for files needing `make`/git/Dockerfile/`.github`. Run `make test-image` once first.

Non-blocking, also the human's call: the Ubuntu 26 pre-classification PR (C10); keeping the group floor at 3 with a comment-only fix vs forcing a second build; the `model.py` touch in 19 IN-01/02 (C7).

## Confidence Assessment

| Area | Confidence | Notes |
|---|---|---|
| Stack | HIGH | Mechanism READ in installed CPython/pytest source; reproduction and arm table are STACK's, not re-run by the synthesis. MEDIUM on Ubuntu 26.04 (container only). |
| Features | HIGH | Browser and API probes MEASURED; info inventory re-read against HEAD. MEDIUM on other URL-state libraries (search snippets). |
| Architecture | HIGH | File/line facts and pins READ at `3726242`. Debt-file line numbers are stale (ARCHITECTURE F8) — plan from ARCHITECTURE §3. LOW on the twin-selectors mechanism. |
| Pitfalls | MEDIUM-HIGH | Repo-specific parts HIGH; its hang-evidence claims and loop-heavy flake plan superseded by STACK. |

**Overall:** MEDIUM-HIGH.

### Gaps to Address

- Flake fix natural-loop acceptance is consistent, not conclusive (0/10 has a 15–30 % chance by luck); the forced-GC result is the proof. Re-run STACK's reproduction and arm table before landing.
- 98 % hang: no reproduction. STACK's arithmetic (~23 outstanding of ~1220 fits a global stall better than one stuck worker) is UNVERIFIED; `faulthandler_timeout` does not cover the post-last-test window; `kill -ABRT <pid>` on a stalled worker UNVERIFIED (not run, to avoid muddying the xdist OCCT segfault investigation); a shared root with the tracker flake is UNVERIFIED.
- Twin-selectors mechanism rests on two CI logs; no local reproduction.
- Unmeasured: `make test-image` red list; Linux process-group listing; a real Ubuntu 26 runner image.
- Number-box garbage MEASURED only by FEATURES; ARCHITECTURE/PITFALLS inferred.
- `faulthandler_timeout = 120` sized from local timings and one CI wall time; confirm against the first CI `--durations`.
- Which 3.12.x first carried the reentrancy guard is unchecked; quote no version in a decision.
- `tests/test_api.py` regexes guarding `app.js` not fully read; run that file early in Phase 28.

## Sources

### Primary (HIGH)
- Installed CPython 3.12.15 `multiprocessing/{resource_tracker,synchronize}.py`; pytest 9.1.1 `_pytest/{unraisableexception,faulthandler}.py`; pytest-xdist 3.8.0, execnet 2.1.2, coverage 7.16.2, pytest-cov 7.1.0 sources; Playwright 1.63.0 driver `coreBundle.js` and `browsers.json`.
- Repo at `3726242`: `app.js`, `params.py`, `pool.py`, `app.py`, `Makefile`, `pyproject.toml`, `ci.yml`, `tests/*`, `bench/RESULTS.md`, `decision_log.md`, `docs/tech_debt/active/*`, v0.5 phase REVIEW and DISPOSITION files (21–24).
- GitHub Actions runs 38347283201, 38680454993; orchestrator-verified red count on `main`.
- Each researcher's MEASURED probes of 2026-10-15 (forced-GC reproduction, `ubuntu:26.04` container runs, browser/API probe table, slug reason counts, process-group listing).

### Secondary (MEDIUM)
- cpython#109629, #131788 / PR #131787 (reentrancy; not backported to 3.12; 3.13 backport reverted); halfb00t/screw PR #7 (same cause, `del manager`); devguide.python.org/versions; GitHub changelog 2026-09-17 and actions/runner-images#14748, #14226; microsoft/playwright#40117 (Ubuntu 26.04 from 1.61.0); `actions/python-versions` manifest.

### Tertiary (LOW)
- TanStack Router, nuqs, react-jsonschema-form docs (search snippets; convention only).

---
*Research completed: 2026-10-15*
*Ready for roadmap: yes, after the five open decisions go to the human; Phases 26, 27 and 29 can be planned without them.*
