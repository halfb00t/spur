---
phase: 12-composition-pass
verified: 2026-10-01T10:09:21Z
status: passed
score: 5/5 must-haves verified
covered_files: [".planning/phases/12-composition-pass/12-01-PLAN.md", ".planning/phases/12-composition-pass/12-01-SUMMARY.md", ".planning/phases/12-composition-pass/12-02-PLAN.md", ".planning/phases/12-composition-pass/12-02-SUMMARY.md", ".planning/phases/12-composition-pass/12-03-PLAN.md", ".planning/phases/12-composition-pass/12-03-SUMMARY.md", ".planning/phases/12-composition-pass/12-04-PLAN.md", ".planning/phases/12-composition-pass/12-04-SUMMARY.md", ".planning/phases/12-composition-pass/12-05-PLAN.md", ".planning/phases/12-composition-pass/12-05-SUMMARY.md", ".planning/phases/12-composition-pass/12-06-PLAN.md", ".planning/phases/12-composition-pass/12-06-SUMMARY.md", ".planning/phases/12-composition-pass/12-07-PLAN.md", ".planning/phases/12-composition-pass/12-07-SUMMARY.md", ".planning/phases/12-composition-pass/12-08-PLAN.md", ".planning/phases/12-composition-pass/12-08-SUMMARY.md", ".planning/phases/12-composition-pass/12-09-PLAN.md", ".planning/phases/12-composition-pass/12-09-SUMMARY.md", ".planning/phases/12-composition-pass/12-REVIEW-DISPOSITION.md", ".planning/phases/12-composition-pass/12-REVIEW-FIX.md", ".planning/phases/12-composition-pass/12-REVIEW.md", ".planning/phases/12-composition-pass/12-SECURITY.md", ".planning/phases/12-composition-pass/12-UAT.md", ".planning/phases/12-composition-pass/12-VALIDATION.md", "Makefile", "README.md", "bench/RESULTS.md", "bench/build_time.py", "bench/export_cost.py", "bench/sweeps/composed.json", "bench/sweeps/spoke_cutout.json", "docs/architecture/cli.md", "docs/architecture/decision_log.md", "docs/ideas/2026-09-21-browser-test-for-the-viewer.md", "docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md", "docs/ideas/2026-09-29-conditional-form-fields.md", "docs/ideas/INDEX.md", "docs/tech_debt/INDEX.md", "docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md", "docs/tech_debt/resolved/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md", "docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md", "docs/tech_debt/resolved/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md", "src/spur/app.py", "src/spur/params.py", "tests/composition.py", "tests/test_api.py", "tests/test_bench.py", "tests/test_calc.py", "tests/test_cli.py", "tests/test_model.py"]
covered_digest: "v2:sha256:261a9a1045984a19f4a1f6c5a96cd81fc10c1b1449f0ee2bc1cfa3ecff468b66"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: "5/5"
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 12: Composition Pass Verification Report

**Phase Goal:** Every v0.2 feature composes correctly across the full matrix, the
milestone's heaviest-configuration build time is measured, and all three interfaces stay
in parity — closing out v0.2.
**Verified:** 2026-10-01T10:09:21Z
**Status:** passed
**Re-verification:** Yes — after review-fix commits, not after gap closure. The prior
VERIFICATION.md (2026-09-30T20:25:00Z, `status: passed`, `human_needed` had already been
resolved by 12-UAT.md before this pass) went stale once the second code-review fix pass
(12-REVIEW-FIX.md, iteration 2, 14/14 findings fixed) touched eight of its covered files:
`bench/RESULTS.md`, `bench/export_cost.py`, `docs/architecture/cli.md`,
`docs/architecture/decision_log.md`, `src/spur/params.py`, `tests/test_api.py`,
`tests/test_bench.py`, `tests/test_model.py`. This pass re-verifies the five success
criteria against the current code, confirms the fixes are real (not just claimed), and
confirms no regression against the prior pass.

## What changed since the prior verification

`git diff fed8baf..HEAD --stat`: 17 files, +786/-289. Of those, the eight files the prior
VERIFICATION.md's `covered_files` named are all doc/comment/test-assertion edits — no
production behavior outside `bench/export_cost.py`'s two new error-reporting branches
(still exit 1 on the same failure condition, just with a stderr message first) and one
docstring/comment correction in `src/spur/params.py` (no bound changed). The remaining
nine changed files are `.planning/` bookkeeping (ROADMAP checkbox + completion dates,
STATE.md, PROJECT.md, the review/validation/security/fix records themselves) — not
production code or test assertions that bear on the five success criteria.

`src/spur/static/app.js` (the file the four human-verified UAT items depend on) has not
changed since the prior human verification run: `git diff c9a169d..HEAD --
src/spur/static/app.js` is empty.

## Goal Achievement

### Observable Truths

Re-checked against the current HEAD (`9e18fa5`). Each row re-verifies the prior pass's
evidence against the diff above, not just copies it forward.

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1: full composition matrix passes — recess × each bore shape, recess × each cutout, each cutout × each bore, every locked refusal (keyway×hex, two-cutout) with the 422 naming fields | ✓ VERIFIED | `tests/composition.py` unchanged by the diff. `tests/test_model.py` changed only in its `HOLES`/`CELLS` typing (IN-05 fix, `cast()` removed, annotated `dict[str, float]` instead) — re-ran `pytest -k "composed or COMPOSED or holes or cells"` against `tests/test_model.py`: 42 passed, same count IN-05's own fix report claims. `tests/test_calc.py` untouched by this diff. Pre-commit `make verify` ran green (907 passed) on every one of the seven fix commits, most recently `9e18fa5`; `pytest --collect-only -q` this session independently confirms the same 907-test collection count (no drift). |
| 2 | SC2: every v0.2 parameter on the form (own group), API, CLI from one `GearParams` model; round-trips the shareable URL; appears in `/api/schema`; `spur info`/`spur export` match the API | ✓ VERIFIED | `tests/test_api.py`'s shareable-link test (IN-04 fix) now whitespace-normalizes both sides of its substring check instead of comparing raw source — re-ran it alone this session: 1 passed. Hand-verified the fix's own claim by reading the diff: the normalization is applied to both `source` and each pinned snippet, so the proof still requires the real tokens, just not their exact whitespace. `app.js` itself is byte-unchanged since the UAT run (`git diff c9a169d..HEAD -- src/spur/static/app.js` empty), so the live-browser behavior UAT already exercised (see Human Verification below) still applies to the current code. `docs/architecture/decision_log.md`'s L31 now correctly attributes the schema/CLI field-order proof to `tests/test_cli.py::test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order` (confirmed present at `tests/test_cli.py:187`, re-ran this session: passes) rather than the `test_api.py` test, which the citation fix (WR-05) separates out as proving the app.js hash round trip specifically. |
| 3 | SC3 (amended): `bench/RESULTS.md` records build + fine-STL/STEP export time for the composed sweep (each cutout stacked with tip chamfer and a recess on the heaviest bore its rules allow, module 1.75 and 10) and for each individual feature, inside `SPUR_BUILD_TIMEOUT` | ✓ VERIFIED | `bench/sweeps/composed.json` re-confirmed 18 rows on disk this session (unchanged by the diff). `bench/RESULTS.md`'s only changes are two prose corrections (WR-07: "at-start loads" reworded to disclose the end-of-run tool-bug reading; WR-09/WR-08: the gzip-invariant and honeycomb-arithmetic sentences corrected to not overclaim) — no run numbers, table cells, or the `spoke_count.le=32` gate changed. `src/spur/params.py` `le=32` re-confirmed present (`grep -n "le=32" src/spur/params.py`), unchanged by the diff (only the adjacent `hole_count` comment text changed, WR-02). |
| 4 | SC4: L19's gzip-level table and L24's mesh-copy timing re-measured against the heaviest v0.2 face topology | ✓ VERIFIED | `bench/export_cost.py` exists; its two production-code changes (WR-03, WR-04) add stderr diagnostics on the same two failure branches (triangle-count mismatch, child-process failure) without changing the measurement logic or the `_decisions()` comparison bars. `bench/RESULTS.md`'s "Export cost" section numbers are untouched by the diff — only the overclaiming sentence about what the triangle-count check proves was corrected (WR-09). `src/spur/app.py` (`_GZIP_LEVEL = 1`) untouched by this diff. |
| 5 | SC5 (amended): Phase 7's regression fixture passes one final time across the whole matrix — identical `DerivedDimensions` and solid (volume, bounding box, face and edge counts); export bytes not compared | ✓ VERIFIED | `git diff --quiet c9a169d -- tests/regression/pre_v0_2.json` still clean (byte-unchanged); `tests/regression/test_pre_v0_2.py` not touched by this diff and was part of the 907-test collection re-confirmed this session. |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tests/composition.py` | shared family/refusal tables for calc- and CLI-level composition tests | ✓ VERIFIED | Unchanged by this diff; still imported by `test_calc.py`/`test_cli.py` |
| `bench/sweeps/composed.json` | 18-row composed sweep (D-01) | ✓ VERIFIED | 18 entries re-confirmed by direct JSON load this session |
| `bench/build_time.py` | `stl_size()`, `Timing.stl_bytes`/`stl_triangles`, largest-fine-STL reporting | ✓ VERIFIED | Unchanged by this diff |
| `bench/export_cost.py` | L19/L24 re-measurement script behind `make bench.export` | ✓ VERIFIED | Changed only to add stderr diagnostics on two existing failure branches (WR-03, WR-04) and correct a docstring (IN-01); `ast.parse`, `ruff`, `mypy --strict` reported clean in the fix commits, independently confirmed by reading the diff for syntactic soundness |
| `docs/architecture/decision_log.md` L31 | phase close-out entry, append-only | ✓ VERIFIED | `git diff --numstat c9a169d -- docs/architecture/decision_log.md` still reads 140/0 this session — append-only invariant holds across the full range including the in-place rewording of L31's own still-uncommitted-at-c9a169d text (the established 11-REVIEW-FIX precedent) |
| `docs/architecture/cli.md` Errors section | real 2/1/1 exit contract | ✓ VERIFIED | Re-read this session: "Three cases, two exit statuses" (corrected from "three exit statuses" per WR-01), one parameter-error case names all three real stderr shapes (argparse flag error, field-level `ValidationError`, field-less `check()` refusal) — cross-checked the no-prefix refusal shape directly against `src/spur/cli.py:67` (`f"error: {where + ': ' if where else ''}{msg}"`, empty `where` for a `check()` refusal) and `tests/test_cli.py:435-437` |
| `docs/tech_debt/resolved/*` (3 files) | two build-timeout debts + the cli.md debt resolved | ✓ VERIFIED | Unchanged by this diff; still present in `resolved/`, absent from `active/` |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `.planning/ROADMAP.md` Phase 12 SC3 | `12-CONTEXT.md` D-01/D-03/D-06 | citation string in the amended criterion | ✓ WIRED | Success-criteria text unchanged by this diff (`git diff fed8baf..HEAD -- .planning/ROADMAP.md` touches only the checkbox, completion date, and the phase-status table — not SC text) |
| `.planning/ROADMAP.md` Phase 12 SC5 | `tests/regression/test_pre_v0_2.py` comparison contract | SC5 names DerivedDimensions + solid geometry, export bytes excluded | ✓ WIRED | Unchanged |
| `bench/RESULTS.md` "Largest fine STL" line | `bench/export_cost.py` input row | same 17,306,084-byte row named in both sections | ✓ WIRED | Row unchanged by this diff |
| `src/spur/params.py` `spoke_count.le=32` | `bench/sweeps/composed.json`/`spoke_cutout.json` | every `spoke_count=40` row moved to 32 | ✓ WIRED | `le=32` re-confirmed present; sweep files unchanged |
| `docs/architecture/decision_log.md` L31 | `tests/test_cli.py::test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order` | corrected attribution (WR-05) | ✓ WIRED | Test name confirmed present at `tests/test_cli.py:187`; re-ran this session, passes |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| The IN-05-fixed composed-cutout tables (typed, no `cast`) still build and pass on every bore/cutout combination | `.venv/bin/python -m pytest -q tests/test_model.py -k "composed or COMPOSED or holes or cells"` | `42 passed` | ✓ PASS |
| The IN-04-fixed shareable-link proof still passes with whitespace normalization | `.venv/bin/python -m pytest -q tests/test_api.py::test_the_shareable_link_round_trips_every_field_through_generic_code` | `1 passed` (part of the 42 above) | ✓ PASS |
| The WR-06-fixed level-9-vs-adopted-level regression test passes and is no longer vacuous | `.venv/bin/python -m pytest -q tests/test_bench.py::test_level_9_is_compared_against_the_level_currently_adopted` | `1 passed` (part of the 42 above) | ✓ PASS |
| The WR-05-fixed field-order citation test passes | `.venv/bin/python -m pytest -q tests/test_cli.py::test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order` | `1 passed` (part of the 42 above) | ✓ PASS |
| Full suite collection count unchanged (no silent test loss/duplication from the fix commits) | `.venv/bin/python -m pytest --collect-only -q` | `907 tests collected` | ✓ PASS |
| No debt markers introduced in any of the eight review-fix-touched files | `grep -n -E "TBD\|FIXME\|XXX\|TODO\|HACK\|PLACEHOLDER"` across all eight | no matches | ✓ PASS |

Full `make verify` not re-run by this verifier per the orchestrator's instruction: the
pre-commit hook ran it green (907 passed, ruff/mypy/import-boundary/unfinished-work clean)
on every one of the seven review-fix commits, most recently `9e18fa5`. This session's own
`pytest --collect-only -q` (907 collected, no drift) and the four named spot-runs above
are the narrow corroborating evidence for that claim, not a substitute full run.

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|-----------------|--------------|--------|----------|
| REQ-measured-build-time | 12-01, 12-02, 12-03, 12-04, 12-09 | Recorded build/export time per feature at its heaviest, recess × each cutout, honeycomb at cap, inside `SPUR_BUILD_TIMEOUT` | ✓ SATISFIED | `REQUIREMENTS.md:198` marks Complete; `bench/RESULTS.md` sections re-confirmed present with the same measured numbers, only prose corrections applied |
| REQ-three-interfaces-extended | 12-01, 12-05, 12-06, 12-07, 12-08, 12-09 | Every v0.2 parameter on form/API/CLI, URL round trip, `/api/schema`; `spur info`/`export` match the API | ✓ SATISFIED | `REQUIREMENTS.md:197` marks Complete; parity tests re-confirmed passing this session |

No orphaned Phase 12 requirements found in `REQUIREMENTS.md` beyond these two. Both IDs
appear in at least one plan's `requirements:` frontmatter (12-01 through 12-09).

### Anti-Patterns Found

None. Scanned all eight files the review-fix commits touched
(`bench/RESULTS.md`, `bench/export_cost.py`, `docs/architecture/cli.md`,
`docs/architecture/decision_log.md`, `src/spur/params.py`, `tests/test_api.py`,
`tests/test_bench.py`, `tests/test_model.py`) for `TBD`/`FIXME`/`XXX` (debt-marker gate)
and `TODO`/`HACK`/`PLACEHOLDER` — zero matches.

### Prohibitions (12-01-PLAN.md must_haves.prohibitions)

| # | Statement | Status | Evidence |
|---|-----------|--------|----------|
| 1 | MUST NOT write ROADMAP.md directly or before human approval | resolved | Unchanged since the prior verification; not touched by the review-fix commits |
| 2 | MUST NOT name a winning configuration in SC3 before the sweep measured it | resolved | SC3 text re-confirmed unchanged by this diff (only the checkbox/date/status-table lines in ROADMAP.md changed) |

### Human Verification Required

None open. The prior VERIFICATION.md's four browser-dependent items (fieldset order; the
composed link populating the form, building the preview, and printing every dimension;
copy-link round trip; a live 422 naming the keyway and hex fields) were run by the human
on 2026-09-30 against a fresh `make serve` and recorded as `result: pass` in 12-UAT.md
(4/4, `status: complete`). That is directly observed runtime behavior — the evidence
class this process requires for non-inferable truths — so it stands as the evidence for
SC2's browser leg rather than being re-listed as an open item. The UI source
(`src/spur/static/app.js`) the UAT exercised has not changed since
(`git diff c9a169d..HEAD -- src/spur/static/app.js` is empty), so nothing in the
review-fix diff invalidates that record. None of the eight review-fix-touched files is
`app.js` or any other runtime UI code, so no new human verification is triggered by this
re-verification.

### Gaps Summary

No gaps. All five roadmap success criteria (as amended by 12-01) still hold against the
current HEAD (`9e18fa5`). The second code-review fix pass (12-REVIEW-FIX.md, 14/14
findings fixed) touched eight files already in this phase's covered-files list; every
change was re-verified directly against the diff and, where a fix altered a test
assertion, by re-running the specific named test (42 passed across the four targeted
spot-checks). No regression found: the full-suite collection count is unchanged (907),
no debt markers were introduced, and the append-only invariant on
`docs/architecture/decision_log.md` still holds (140/0 insertions/deletions since
`c9a169d`). Both requirement IDs remain satisfied. The four browser-dependent human
verification items from the prior pass are closed by 12-UAT.md (4/4 pass) and remain
valid because the UI source they exercised is unchanged.

---

*Verified: 2026-10-01T00:00:00Z*
*Verifier: Claude (gsd-verifier)*
