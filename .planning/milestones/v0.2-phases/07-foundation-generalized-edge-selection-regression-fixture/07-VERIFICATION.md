---
phase: 07-foundation-generalized-edge-selection-regression-fixture
verified: 2026-09-26T13:10:00Z
status: passed
score: 4/4 must-haves verified
covered_files: [".planning/REQUIREMENTS.md", ".planning/phases/07-foundation-generalized-edge-selection-regression-fixture/07-01-PLAN.md", ".planning/phases/07-foundation-generalized-edge-selection-regression-fixture/07-01-SUMMARY.md", ".planning/phases/07-foundation-generalized-edge-selection-regression-fixture/07-02-PLAN.md", ".planning/phases/07-foundation-generalized-edge-selection-regression-fixture/07-02-SUMMARY.md", "Makefile", "bench/RESULTS.md", "docs/architecture/decision_log.md", "docs/architecture/solid-model/tactics.md", "docs/tech_debt/INDEX.md", "docs/tech_debt/active/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md", "src/spur/calc.py", "src/spur/model.py", "tests/regression/capture.py", "tests/regression/corpus.py", "tests/regression/pre_v0_2.json", "tests/regression/test_pre_v0_2.py", "tests/test_calc.py", "tests/test_model.py"]
covered_digest: "v1:sha256:9163c7f693c8aff9ceac27eafd7d87313b10fe29a155c48bbd0596b91de273f5"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 7: Foundation — Generalized Edge Selection + Regression Fixture Verification Report

**Phase Goal:** The bore-rim edge selector works correctly for any bore shape, and a
regression fixture proves every pre-v0.2 parameter set is unchanged — the foundation
every later phase extends.
**Verified:** 2026-09-26T13:10:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth (ROADMAP Success Criterion) | Status | Evidence |
|---|---|---|---|
| 1 | `bore_rim_limit(p)` computes the correct edge-selection bound per bore shape (round and D-flat today; shaped to extend to hex/keyway); a test asserts non-empty, exact selection whenever the feature is on, for every bore shape that exists | ✓ VERIFIED | `src/spur/calc.py:61-74` defines `bore_rim_limit(p) -> float` returning `bore_radius(p)` for round/D-flat, `0.0` with no bore, no kernel import. `tests/test_calc.py:108-116` asserts exact equality with `bore_radius(p)` for `bore_flat=0`, defaults, and `bore_d=0`. `tests/test_model.py:47-110` (`test_each_edge_selector_picks_exactly_its_own_edges`, 10 rows) asserts the *exact* edge count/type per bore shape (round `{CIRCLE:2}`, D-flat `{CIRCLE:2, LINE:2}`), stronger than the ROADMAP's `len(...) > 0` bar, and confirms identity (z on an end face, circle radius = bore_radius) |
| 2 | A selector that finds zero edges while its feature is on raises a build error rather than shipping unchamfered/unfilleted geometry | ✓ VERIFIED | `src/spur/model.py:233-238` (`_groove_floor_edges`) and `:264-269` (`_bore_rim_edges`) both raise `BuildError` with a named message on empty selection. `tests/test_model.py:113-137` provokes both guards through the real build path (`_build_checked` with a monkeypatched `bore_rim_limit`; a bore-less `_groove_floor_edges` call) and asserts the exact message text and that the catch-all's "try smaller" wording is absent |
| 3 | A regression fixture captures `derive()`'s full 19-field output plus `build()`'s solid volume and bounding box for the defaults, every existing test's parameter set, and the README's example links, and passes at HEAD | ✓ VERIFIED | `tests/regression/pre_v0_2.json` holds 44 records (39 built, 5 mate-only) confirmed by direct JSON inspection; provenance header names git HEAD `6f06d77`, `src_clean: true`, kernel versions, capture date. `tests/regression/test_pre_v0_2.py` replays derive (19 fields) and build (volume/bbox/faces/edges) per record. Re-ran the tripwire independently: monkeypatching `_bore_rim_edges` to return `[]` produced exactly `32 failed, 53 passed` (matches SUMMARY's claim), and `git status --porcelain -- src tests` was clean afterward |
| 4 | `make verify` is green with the new fixture and selector tests included | ✓ VERIFIED | Ran `make verify` myself (not trusting the SUMMARY): ruff clean, `mypy --strict` "Success: no issues found in 31 source files", `lint-imports` 5/5 contracts kept (including "The gear maths stays free of the CAD kernel"), pytest **289 passed in 52.17s** — matches the plan's expected count exactly |

**Score:** 4/4 truths verified (0 present-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `src/spur/calc.py::bore_rim_limit` | Exact per-shape rim bound, no kernel import | ✓ VERIFIED | Present, correct signature/body; `grep cadquery\|cq\.` in calc.py returns nothing |
| `src/spur/model.py::BORE_RIM_SLACK` | Named 0.01mm constant with measured-tolerance comment | ✓ VERIFIED | `model.py:50-55`; comment states 1e-7mm measured kernel tolerance and MIN_WALL 0.4mm |
| `src/spur/model.py::_bore_rim_edges` / `_groove_floor_edges` | Both guarded, `_bore_rim_edges` takes `(solid, p)` | ✓ VERIFIED | Signatures and guards match plan exactly; wired into `_cut_bore`/`_cut_face_recesses` |
| `tests/regression/corpus.py`, `capture.py`, `pre_v0_2.json`, `test_pre_v0_2.py` | Corpus/capture/fixture/replay | ✓ VERIFIED | All exist, no `__init__.py`, 44 records confirmed, replay tests pass as part of the 289 |
| `tests/test_calc.py::test_the_bore_rim_limit_is_the_bore_radius_for_round_and_d_flat_bores` | Unit test | ✓ VERIFIED | Present, exact match to plan's assertions |
| `tests/test_model.py::test_each_edge_selector_picks_exactly_its_own_edges` | 10-row matrix | ✓ VERIFIED | Present, 10 `pytest.param` rows exactly matching the plan's table |
| `docs/architecture/decision_log.md` L26 | New append-only entry | ✓ VERIFIED | `## L26 — ...` present after L25; append-only (no earlier lines touched, confirmed by git history) |
| `docs/architecture/solid-model/tactics.md` | Edge re-selection paragraph updated | ✓ VERIFIED | Names `bore_rim_limit`, `BORE_RIM_SLACK`, and L26 |
| `bench/RESULTS.md` | Fixture cost + selector-change cost sections | ✓ VERIFIED | `## Regression fixture cost (Phase 7, D-06)` and `### After the selector change (07-02)` both present with measured numbers, host-state caveats (L08 honesty) |
| `docs/tech_debt/active/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md` | `must`-severity debt item | ✓ VERIFIED | `Severity: must` present; row added to `docs/tech_debt/INDEX.md` |
| `Makefile::fixture.regen` | New target, sole writer of the JSON | ✓ VERIFIED | Target present; `git log --oneline -- tests/regression/pre_v0_2.json` shows only the two 07-01 commits (`6f06d77`, `7cb4eb6`) — no 07-02 commit touched it |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `model.py::_bore_rim_edges` | `calc.py::bore_rim_limit` | `lim = bore_rim_limit(p) + BORE_RIM_SLACK` | ✓ WIRED | Confirmed at `model.py:252` |
| `model.py::_cut_bore` | `model.py::_bore_rim_edges` | `_bore_rim_edges(solid, p)` | ✓ WIRED | Confirmed at `model.py:207` — passes `p`, not a pre-computed radius |
| Both selectors | `build_errors.BuildError` | raise on empty selection | ✓ WIRED | Confirmed at `model.py:233-238`, `:264-269` |
| `tests/regression/capture.py` | `src/spur/model.build` / `spur/calc.derive` | `solid()`/`derived()` helpers | ✓ WIRED | Confirmed by reading `capture.py` interfaces match plan; fixture content is real derive/build output, not static |
| `Makefile::fixture.regen` | `tests/regression/capture.py` | `$(PY) tests/regression/capture.py` | ✓ WIRED | Present in Makefile |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| REQ-defaults-off-regression | 07-01, 07-02 | Regression fixture proves every pre-v0.2 parameter set unchanged | ✓ SATISFIED | 44-record fixture, byte-unchanged across 07-02 (`git log` shows only 07-01 commits touched the JSON), tripwire proven |
| REQ-edge-selection-proven | 07-02 | Selectors never silently select zero/wrong edges; count test per bore profile with/without recess; zero-edge raises build error | ✓ SATISFIED | 10-row exact-count matrix; two zero-edge `BuildError` tests through real build paths |

No orphaned requirements: REQUIREMENTS.md maps exactly these two IDs to Phase 7, and both are marked `[x]` and `Complete` in the traceability table, matching the PLAN frontmatter `requirements:` fields.

### Anti-Patterns Found

None. Scanned all phase-modified files (`calc.py`, `model.py`, both test files, the regression fixture module trio, `Makefile`, `bench/RESULTS.md`, decision log, tactics doc, tech-debt files) for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` and stub-shaped patterns — no matches except the `Makefile`'s own unfinished-work-scan grep pattern (the linter definition itself, not a marker).

### Additional Checks (explicitly requested)

- `git log --oneline -- tests/regression/pre_v0_2.json` → only `7cb4eb6` and `6f06d77` (both 07-01). No 07-02 commit touched the fixture. ✓
- `src/spur/calc.py` imports: `math`, `dataclasses`, `typing.TYPE_CHECKING`, `pydantic`; `GearParams` import is `TYPE_CHECKING`-gated. No `cadquery` import anywhere in the file. ✓
- `make verify` run directly by the verifier (not taken from SUMMARY): ruff clean, mypy strict clean, 5/5 import contracts kept, **289 passed in 52.17s**. ✓
- Tripwire re-run independently by the verifier: `32 failed, 53 passed` — exact match to both SUMMARY files' claims. `git status --porcelain -- src tests` clean afterward. ✓

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| `make verify` passes | `make verify` | 289 passed in 52.17s, ruff/mypy/lint-imports clean | ✓ PASS |
| Fixture tripwire catches a vanished chamfer | monkeypatch `_bore_rim_edges` to `[]`, run `tests/regression` | `32 failed, 53 passed in 13.64s` | ✓ PASS |
| `bore_rim_limit` matches `bore_radius` exactly | ran `pytest tests/test_calc.py -k bore_rim_limit -q` (implicitly covered by full suite) | passed as part of 289 | ✓ PASS |

### Human Verification Required

None. All four ROADMAP success criteria are code-verifiable and were verified directly against the codebase (not from SUMMARY claims), including an independent re-run of `make verify` and the tripwire probe.

### Gaps Summary

No gaps. All four ROADMAP success criteria hold, both requirement IDs are satisfied,
the fixture was proven byte-unchanged across the selector-generalization plan via direct
git history inspection, `calc.py` remains free of the CAD kernel, and `make verify` is
green at 289 passed when run independently by the verifier.

---

_Verified: 2026-09-26T13:10:00Z_
_Verifier: Claude (gsd-verifier)_
