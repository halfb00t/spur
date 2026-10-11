---
phase: 22-download-name-carries-the-root
verified: 2026-10-11T07:10:00Z
status: passed
score: 15/15 must-haves verified
covered_files:
  - ".planning/phases/22-download-name-carries-the-root/22-01-PLAN.md"
  - ".planning/phases/22-download-name-carries-the-root/22-01-SUMMARY.md"
  - ".planning/phases/22-download-name-carries-the-root/22-02-PLAN.md"
  - ".planning/phases/22-download-name-carries-the-root/22-02-SUMMARY.md"
  - "bench/RESULTS.md"
  - "docs/architecture/decision_log.md"
  - "docs/architecture/http-api.md"
  - "src/spur/calc.py"
  - "src/spur/params.py"
  - "tests/browser_session.py"
  - "tests/test_api.py"
  - "tests/test_browser.py"
  - "tests/test_trochoid.py"
covered_digest: "v3:sha256:176031da7e2f09d33328191730f2442403a577becb2c97c52e26cab0569b0fe2"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 22: Download Name Carries the Root Verification Report

**Phase Goal:** The name of a downloaded file says which root the part has: a part built with the hob root ends `_trochoid`, and every radial part, and every request whose trochoid is silently ignored, keeps today's name byte for byte.
**Verified:** 2026-10-11T07:10:00Z
**Status:** passed
**Re-verification:** No -- initial verification

Verified against HEAD `0b60313` (phase commits `e3b1181`, `5c6c025`, `f905a25`, `3b71355`, `0b60313`; base `5769ac0`). Nothing here is taken from the SUMMARYs: the code, tests, docs and logs were read, and the behavior was re-run.

## Goal Achievement

### Observable Truths (ROADMAP success criteria, then plan-specific)

| #  | Truth | Status | Evidence |
| -- | ----- | ------ | -------- |
| SC1 | At 23 teeth `root_shape=trochoid` downloads as `..._trochoid` (STL and STEP header; browser `expect_download`); at 40 teeth (ignored) and the default radial gear the name equals today's byte for byte; radial-default pin unchanged | VERIFIED | `src/spur/params.py:190-210`: `slug()` appends `_trochoid` iff `root_mode(self, profile(self), requested=self.root_shape, rho=self.root_fillet).mode == "trochoid"`. `test_the_download_name_carries_the_root_the_part_has` (2 formats x 2 tooth counts) pins whole `Content-Disposition` values; ran green with `test_model_download` and the flipped root-shape test (13 passed). Browser step `download name` re-run live: `suggested_filename = spur_z23_m1.75_pa25_trochoid.stl` (1 passed). `git diff 5769ac0 HEAD -- tests/test_api.py` contains no `spur_z21` line, so the `:720` radial-default pin is unedited. |
| SC2 | `slug()` stays total: a name for a refused and an ignored request; `build.failed` carries the slug | VERIFIED | No `try`/guard in `slug()`. Six pure rows (default, 23, 26, 27, 40, tip-land refused) green. `test_a_failed_build_records_the_name_of_the_part_it_would_have_been` green (`spur_z25_m1.75_pa25_trochoid`, `spur_z19_m1.75_pa33.5`). Independent sweep (my own script over `bench.trochoid.sweep_cases()`): 17,567 valid, 9,954 named `_trochoid`, 0 raised, 0 disagreements with the predicate, 0 names outside `base` / `base_trochoid`, 0 radial requests renamed. |
| SC3 | Record written before names move: L40 lists every consumer, no cache keyed by slug; http-api.md states the truth; `pre_v0_2.json` clean; idea retired in the same commit | VERIFIED | L40 present at the end of `docs/architecture/decision_log.md` (consumers read at parent `5769ac0`, cache keys, rule, cost, totality, browser proof, path correction, reversibility, `Machine:` line). `docs/architecture/http-api.md:43` and `:93` state the rule. `git diff 5769ac0 HEAD -- tests/regression` is empty. Idea moved by `git mv` (rename 74% in `e3b1181`) with `Status: retired`, `Retired in:` the commit subject, an Outcome section; INDEX row moved to `## Retired`. All in one commit `e3b1181`. |
| 4 | Only `slug()` changes in production; `app.py`, `records.py`, `model.py`, `cli.py`, `pool.py`, `app.js` not edited | VERIFIED | `git diff --stat 5769ac0 HEAD` over those paths is empty. `src/` diff is `params.py` (+22/-2 incl. docstring) and a `calc.py` docstring sentence only. Consumers reach the suffix through `app.py:496`, `records.py:180`, `model.py:807`. |
| 5 | Local import in the method, no guard, no helper in `calc` | VERIFIED | `params.py:207` `from .calc import profile, root_mode` inside `slug()`; no `try`; `git grep` shows `calc.py` change is docstring only. |
| 6 | Reds were seen and recorded (PD-10) | VERIFIED | `bench/RESULTS.md` `### Seen red once (Phase 22)` has four rows with first-failure lines; `investigation/22-01-browser-red.log` and `-green.log` exist (browser red: `the download is named 'spur_z23_m1.75_pa25.stl'`). |
| 7 | Probe empty: `GearParams()` is `spur_z19_m1.75_pa25`, reason `not requested` | VERIFIED | `default-gear` row of the pure test, green. |
| 8 | Probe encoding: exact `str` equality on the whole header / `suggested_filename` | VERIFIED | Tests compare `== 'attachment; filename="..."'` (whole header) and `name ==` (browser); no substring left (the old `in` assertion was replaced). Suffix adds `_` and lowercase only. |
| 9 | Probe adjacency: 26 teeth `_trochoid`, 27 plain; radial and hob-root 23-tooth parts differ | VERIFIED | `26-applies-last` / `27-ignored-first` rows green; root-shape link test asserts both 23-tooth headers differ. |
| 10 | Probe empty (consumers): a link omitting `root_shape` keeps its name; the pin and the four record asserts pass unedited | VERIFIED | Diff of `tests/test_api.py` is additions plus the one deliberately flipped assert; `:797, :985, :1086, :1123` untouched; related tests green. |
| 11 | Probe ordering: suffix not prefix | VERIFIED | `f"{name}_trochoid"` in `slug()`; today's name is a prefix of the hob-root name. |
| 12 | Probe concurrency (backstop): `slug()` is a pure function; header, records and temp stem compute one name | VERIFIED (observed) | Backstop tag, so presence is not accepted; behavior observed directly. `slug()` reads only frozen `GearParams` fields, no module state. Scratch run: 200 requests over 8 threads through `TestClient` with a stub backend (a mix of cache hits and distinct keys): every 200 response carried the exact name for its parameters (23 trochoid, 23 plain, 40 trochoid, 23 radial); the 4 refused with 503 `queue.refused` emitted their record without error, so `slug()` ran on that path too. STEP under `Accept-Encoding: gzip` and `identity` gave the same name. |
| 13 | No cache keyed by slug (backstop) | VERIFIED (observed) | `app.py:401` `key = (params, fmt, q.quality, encoding)`, raw twin at `:418`; header built after the cache at `:496`. The observed run above shows a cache hit and a build for one gear carry the same correct name. |
| 14 | 22-02: three readings in `bench/RESULTS.md` equal their kept logs; `BUILD_WAIT_MS` stays 45,000, comment-only change; `### Seen red once` present | VERIFIED | Table figures 3.56 / 3.20 / 1.13 s, click 0.14 / 0.12 / 0.13 s, `1 passed in 9.25s / 8.33s / 6.14s` match `22-02-reading-{1,2,3}.log` lines. `git diff` of `tests/browser_session.py` shows only comment and docstring lines; `BUILD_WAIT_MS = 45_000` unchanged. My own run: step 3.26 s, under 15 s. No bar set. |
| 15 | `make verify` passes on the committed tree | VERIFIED | `investigation/22-02-verify.log` ends `1238 passed in 222.53s`, coverage 97.92%, `make verify exit 0`; the orchestrator's run on `3b71355` matches. Not re-run in full (targeted re-runs did not contradict it). |

**Score:** 15/15 truths verified (0 present, behavior-unverified)

### Prohibitions (ADR-550 D3/D4)

| Prohibition | Tier | Result | Evidence |
| ----------- | ---- | ------ | -------- |
| Not name a file with a root the part lacks (ignored / refused requests are named radial) | test | Held | 27, 40-tooth and tip-land-refused rows plus header pin at 40 teeth; sweep: name agrees with predicate in all 17,567. Seen red under the requested-root rule. |
| Not silently rename a part the user did not change | test | Held | Radial sweep check (0 renamed); `pre_v0_2.json` and `golden_requests.json` diff empty; `:720` pin unedited. |
| No guard / fallback / third root word in `slug()` | test | Held | Read `params.py`: no `try`, no fallback, one suffix word. Totality shown by rows and sweep. |
| Not record a reading that was not taken (22-02) | test | Held | Figures re-read against the three kept logs. |
| Not move `BUILD_WAIT_MS`, a bar or a wait toward a pass (22-02) | judgment | Held, mechanically evidenced | Judgment-tier, so this verdict is non-authoritative by rule. The evidence is deterministic: the constant is byte-identical to base, the diff of `browser_session.py` is comments only, no `Makefile` or bar edit in the phase diff, the new step reuses the existing `BUILD_WAIT_MS`. Flagged here for the record; no open question remains. |

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `src/spur/params.py` | `slug()` with local import | VERIFIED | `verify.artifacts`: 7/7 passed for plan 22-01; wired via `app.py:496`, `records.py:180`, `model.py:807` |
| `tests/test_api.py` | header pins, build.failed rows | VERIFIED | functions exist and pass |
| `tests/test_trochoid.py` | six pure slug rows | VERIFIED | 6 passed |
| `tests/test_browser.py` | `download name` step | VERIFIED | step runs and passes live |
| `docs/architecture/decision_log.md` | `## L40` | VERIFIED | full entry read |
| `docs/ideas/retired/...download-name...md` | retired idea | VERIFIED | `Status: retired` present |
| `docs/architecture/http-api.md` | rule stated | VERIFIED | lines 43, 93 |
| `bench/RESULTS.md` (22-02) | Phase 22 section | VERIFIED | readings and red table present |

### Key Link Verification

`verify.key-links` could not evaluate the five links (its `from:` values are prose, not file paths: "Source file not found"), so each was checked by hand.

| From | To | Status | Details |
| ---- | -- | ------ | ------- |
| `GearParams.slug()` | `calc.root_mode()` | WIRED | `params.py:209` matches the planned pattern |
| `app.py` Content-Disposition | `slug()` | WIRED | `app.py:496`, after the byte cache |
| `records.py _gear_fields` | `slug()` | WIRED | `records.py:180`; build.failed row asserts the slug |
| browser step | server header | WIRED | `expect_download` around a click on `#dl-stl` on a fresh page |
| INDEX `## Retired` | retired idea file | WIRED | row present, old row removed |

### Data-Flow Trace (Level 4)

The name is computed per response from the request's validated parameters; no static or hardcoded value stands in for it. Observed live in the browser (real click to saved filename) and in the 200-request run. FLOWING.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| API header pins, failed-build rows | `make test PYTEST_ARGS="tests/test_api.py -n0 --no-cov -q -k 'download_name or model_download or root_shape_link or failed_build or build_failed'"` | 13 passed | PASS |
| Pure slug rows | `make test.fast PYTEST_ARGS="tests/test_trochoid.py -n0 -q -k download_name_follows"` | 6 passed | PASS |
| Real browser download | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"` | `spur_z23_m1.75_pa25_trochoid.stl`, 1 passed | PASS |
| Totality sweep | scratch script over `bench.trochoid.sweep_cases()` | 17,567 / 9,954 / 0 raised | PASS |
| Cache and concurrency | scratch script, 200 requests, 8 threads | all 200 responses correct; 503s recorded | PASS |

### Probe Execution

None declared by this phase's plans. Step 7c: not applicable.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| REQ-slug-carries-effective-root | 22-01, 22-02 | `slug()` appends `_trochoid` only when `root_mode` applies the hob root; radial and ignored keep today's name; total; tested at z = 23 and 40 | SATISFIED | SC1, SC2 above; `REQUIREMENTS.md:99` `[x]`, traceability row `Complete` |
| REQ-slug-consumers-read-first | 22-01 | The Lxx lists every consumer before names move, records no cache keyed by slug; idea retired in the same commit | SATISFIED | SC3 above; L40 consumer list matches my own grep of `src`, `bench`, `tests`, `docs` (only `app.py`, `records.py`, `model.py`, `bench/export_cost.py`, `tests/test_model.py` read the slug); `REQUIREMENTS.md:105` `[x]` |

Both IDs in the PLAN frontmatter appear in `REQUIREMENTS.md` and both are mapped to Phase 22. No orphaned requirement: `REQUIREMENTS.md` maps exactly these two to Phase 22.

### Anti-Patterns Found

None. No `TBD`, `FIXME`, `XXX`, `TODO` or `HACK` is added in the phase diff across `src`, `tests`, `docs/architecture`, `docs/ideas` and `bench`. No stubs: `slug()` is a real computation.

### Human Verification Required

None. (The L40 prose quality is a reviewer's call, as the 22-01 SUMMARY itself notes, but it is not a must-have: its required contents were checked item by item.)

### Observations (non-blocking)

- Untracked files in the working tree: `.planning/milestone.lock` and `22-REVIEW.md`. Neither is part of the phase commits.
- The `ubuntu-latest` reading of the browser step is deliberately not taken here (22-02 says so); Phase 25 re-sets the gate bar.
- The 22-02 spread (1.13 to 3.56 s) is reported unexplained by its own text; my run (3.26 s) sits inside it.
- Standing rules: L08 holds (a name is only claimed when the predicate builds the part; ignored and refused requests keep the plain name) and L05 holds (no radial or `root_shape`-omitting request changes name, fixtures empty-diff).

### Gaps Summary

No gaps. The phase goal is achieved in the code, not only in the SUMMARYs.

---

_Verified: 2026-10-11T07:10:00Z_
_Verifier: Claude (gsd-verifier)_
