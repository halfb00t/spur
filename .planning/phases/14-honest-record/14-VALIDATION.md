---
phase: "14"
slug: "honest-record"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-02"
validated: "2026-10-05"
---

# Phase 14 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

This phase changed two behaviours and a record: `derive()` warns when the root fillet's
straight chord ends above the pitch circle (`calc.py`, pure maths, no kernel), the four
plain cutout rows are asserted against closed-form removed volumes at `abs=1e-9` mm³ with a
tripwire that proves the bar is load-bearing (`tests/test_model.py`), and README, `_outline`'s
docstring, two retired debt files and L33 say what was measured. Every behaviour has a
pytest test that runs in `make verify`; the record rows are commands over the committed
tree. The pre-v0.2 fixture and `GearParams` are untouched (`git diff --quiet 5d9e907 --
tests/regression/pre_v0_2.json src/spur/params.py`).

Audited 2026-10-05 (State A) at `0a8837c` by the validate-phase orchestrator, run on its own
after the phase landed on `main` as `20cd484` (#17, 2026-10-03) — not at the Phase 14
transition, where it was deferred because the auditor may add tests. The Per-Task map is
filled from the four PLAN.md `<automated>` blocks and the SUMMARYs' `coverage:` blocks; the
tests were re-run at `0a8837c` under Phase 15's `-n 8` gate (Phase 14 itself ran the suite
serially, `927 passed in 212.90s`, 14-04-SUMMARY).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (9.1.1 today); serial at the phase's close, `-n 8 --cov` since Phase 15; nothing installed in this phase (`requirements.txt` untouched) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]`; since Phase 15 also `[tool.coverage.report]` (`fail_under = 96`) |
| **Quick run command** | `make test PYTEST_ARGS="tests/test_calc.py -k root_lead_in -q -n0 --no-cov"` → `15 passed, 389 deselected in 0.06s`; `make test PYTEST_ARGS="tests/test_model.py -k 'each_cutout_is_exactly or cutout_proof_fails or every_feature_proof_holds_on_a_tip or proofs_hold_with_a_single_sided' -q --no-cov"` → `23 passed in 11.79s` (both 2026-10-05, `-n 8` for the second) |
| **Full suite command** | `make verify` — `927 passed in 212.90s` serial at the phase's close (14-04-SUMMARY); 929 passed under `-n 8` with coverage today, through the pre-commit hook on every Phase 16 commit |
| **Estimated runtime** | ~3.5 min serial at the time; ~64 s warm through the hook since Phase 15 (L34) |

---

## Sampling Rate

- **After every task commit:** the pre-commit hook runs `make verify` itself (plain `git commit`; `gsd_run query commit`'s 30 s timeout cannot survive the hook); run the two quick commands above while iterating on `calc.py` or the cutout proofs
- **After every plan wave:** `make verify`, state the command and the result line in the reply (CLAUDE.md)
- **Before `/gsd-verify-work`:** `make verify` green; `git diff --quiet 5d9e907 -- tests/regression/pre_v0_2.json src/spur/params.py`; `git diff --name-only 5d9e907 -- src` is `calc.py` and `model.py` only
- **Max feedback latency:** ~64 s (one hook run on the dev host); the two quick commands together under 15 s

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 14-01-T1 (tracer) | 01 | 1 | REQ-root-lead-in-warned | T-14-01, T-14-02 | the height is computed from `spline_start(pr, root_fillet(p)) − pr.r`, never a literal; `GearParams` and the fixture untouched | unit + live CLI + live API + replay | `pytest tests/test_calc.py -k root_lead_in`; `spur info --profile-shift 0.75 --pressure-angle 20` warnings list equals the one sentence; `TestClient` `/api/info` default gear `[]`, `{0.75, 20}` the sentence; `git diff --quiet 5d9e907 -- tests/regression/pre_v0_2.json src/spur/params.py` + the 85-case replay | ✅ `tests/test_calc.py` | ✅ green (`13857e1`; re-run 2026-10-05: `15 passed`; CLI prints `… reaching 0.125 mm above the pitch circle …`; fixture and `params.py` identical) |
| 14-01-T2 (tdd) | 01 | 1 | REQ-root-lead-in-warned | T-14-01 | one field step either side of the crossing proven, silent at an exact touch and under the print resolution | unit (parametrized) | `pytest tests/test_calc.py -k root_lead_in`; python assert that the parametrize table carries the debt configs, three driver pairs, the mid-tooth cap and the zero rows | ✅ `test_the_root_lead_in_warns_when_it_ends_above_the_pitch_circle` | ✅ green (`ac607d7`; re-run: `15 passed, 389 deselected`) |
| 14-01-T3 | 01 | 1 | REQ-readme-root-zone-states-the-limit | T-14-03, T-14-02 | README's numbers a subset of the measured `{1.188, 1.25, 0.125}`, no micron figure; `model.py` AST equal to `5d9e907` with docstrings blanked | structural + AST + debt sha + replay | python asserts over README and the `_outline` docstring; debt file absent from `active/`, `Status: resolved`, `Resolved in:` equal to the INDEX cell and the retiring commit | — | ✅ green (`825095f`, sha recorded in `775ee6f`; re-run: README:225-229 state the condition and cite the warning, `Resolved in: 825095f`) |
| 14-02-T1 | 02 | 2 | REQ-filleted-spoke-closed-form | T-14-05, T-14-04 | the oracle shares no code with `_fillet_corner` (AST: no `_fillet_corner` or `cq` name); the literal `2934.725405` survives once, in a docstring; `src` untouched | unit + AST + diff | `pytest tests/test_model.py -k "each_cutout_is_exactly or cutout_proof_fails"`; AST check on `_filleted_spoke_volume`; `git diff --quiet HEAD -- src tests/regression` | ✅ `_filleted_spoke_volume` (`tests/test_model.py:1153`) | ✅ green (`61e1bea`; re-run: in the 23 passed) |
| 14-02-T2 (checkpoint:decision, D-06) | 02 | 2 | REQ-filleted-spoke-closed-form | T-14-04 | the executor never loosens the bar; a gap above 1e-9 halts for the human | gate (conditional) | python assert `'D-06 not reached' in 14-02-SUMMARY.md` | — | ✅ green (not reached: measured gaps 2.39e-12, 1.36e-12, 2.73e-12, 8.87e-12 mm³) |
| 14-02-T3 (tdd) | 02 | 2 | REQ-filleted-spoke-closed-form | T-14-04, T-14-06 | all four rows at `abs=1e-9`; the rim-corner tripwire goes red on a 1e-6 mm root move that the old `rel=1e-6` would have passed; debt retired in the proving commit | unit + tripwire + debt sha + replay | the same `-k` run; AST assert that every plain row passes `abs=1e-9`; `Resolved in:` equals the INDEX cell; REQUIREMENTS phrase assert; no `14-02` commit touches `src` | ✅ `test_the_cutout_proof_fails_when_a_rim_corner_tangent_root_moves` | ✅ green (`61e1bea`, sha recorded in `b00c44c`; re-run: in the 23 passed; `Resolved in: 61e1bea`) |
| 14-03-T1 | 03 | 3 | all three | T-14-07, T-14-08 | L09, L10, L30 untouched (0 deleted lines); every e-notation figure in L33 present in `tests/test_model.py`; every cited sha resolves | numstat + structural | `git diff --numstat 5d9e907 -- docs/architecture/decision_log.md` deleted column `0`; python `L33 ok` | — | ✅ green (`9fb667d`; re-run 2026-10-05: one `## L33` heading, numstat `111/0` over the whole landed phase including 14-04's in-place edit) |
| 14-03-T2 | 03 | 3 | all three | T-14-SC | fixture and `params.py` byte-identical; `src` diff is `calc.py` and `model.py`; both debts in `resolved/` | full suite + diff + ledger | `make verify`; `git diff --quiet 5d9e907 -- tests/regression/pre_v0_2.json src/spur/params.py`; `git diff --name-only 5d9e907 -- src`; debt ledger check | — | ✅ green (no commit of its own; `927 passed` at the phase's close; re-run: identical, `src/spur/calc.py src/spur/model.py`, both debt files in `resolved/`) |
| 14-04-T1 (tracer, G-14-2) | 04 | 4 | REQ-filleted-spoke-closed-form | T-14-10 | a control call on the unpatched build passes before the monkeypatch, so the `pytest.raises` can only be satisfied by the patch | unit + AST | `pytest tests/test_model.py -k "each_cutout_is_exactly or cutout_proof_fails_when_the_cutout_step"`; AST assert that the holes and cells rows call `_holes_volume` / `_hex_cells_volume`; numeric check of both oracles against `hex_cells`; `git diff --quiet HEAD -- docs/architecture/decision_log.md src tests/regression` | ✅ `_holes_volume` (`:1208`), `_hex_cells_volume` (`:1224`) | ✅ green (`a4347be`; re-run: in the 23 passed) |
| 14-04-T2 (checkpoint:decision, G-14-5) | 04 | 4 | REQ-filleted-spoke-closed-form | T-14-09 | gaps measured on the pinned kernel before any bar moves; nothing written before the answer | gate (human) | python assert on the SUMMARY's record of the answer; `git diff --quiet HEAD -- tests docs` → `nothing changed before the decision` | — | ✅ green (answered 2026-10-03: `noise-multiple 1e-8` — tip rows at `abs=1e-8` over measured 5.85e-10 / 5.94e-10 / 6.55e-10 mm³, single-sided row at `abs=1e-9` over 2.79e-12) |
| 14-04-T3 (tdd, G-14-5) | 04 | 4 | REQ-filleted-spoke-closed-form | T-14-09, T-14-11 | the four hole-through-web rows on the web formula at the decided bar; hex-holes, spokes and cells unchanged at `volume_rel=1e-6`; every "cannot exist" gone; L33 edited in place only, its tripwire sentence verbatim; `src` untouched | unit + claim scan + numstat + full suite | `pytest tests/test_model.py -k "every_feature_proof_holds_on_a_tip or proofs_hold_with_a_single_sided or each_cutout_is_exactly"`; three python scans over the debt file, L33 and the docstrings; numstat deleted `0`; `make verify` | ✅ `test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore`, `test_the_recess_fillet_and_cutout_proofs_hold_with_a_single_sided_recess` | ✅ green (`4892853`; re-run: in the 23 passed; `make verify` green through the hook on every later commit) |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

Requirement classification (validate-phase §3): REQ-root-lead-in-warned COVERED (01-T1/T2 — one parametrized pure-maths test, 15 cases, plus the live CLI and API reads); REQ-readme-root-zone-states-the-limit COVERED (01-T3, 03-T2 — commands over README, the docstring and the debt ledger, with the fixture replay as the "part unchanged" proof); REQ-filleted-spoke-closed-form COVERED (02-T1/T3, 04-T1/T3 — five pytest tests over the built solid, 23 cases, three closed-form oracles). 0 PARTIAL, 0 MISSING. "Automated" for the README requirement means a command that reads the committed text and the ledger, the same meaning 15- and 16-VALIDATION.md give it; the behaviour it describes (`derive()`'s warning) is the first requirement's test.

Requirement → proof map:

| Req ID | Behavior | Test Type | Automated Command |
|--------|----------|-----------|-------------------|
| REQ-root-lead-in-warned | one sentence in `derive().warnings` when the chord ends above the pitch circle, naming the height at 3 dp; silent on the default gear, at an exact touch and under the print resolution; one field step either side | unit | `make test PYTEST_ARGS="tests/test_calc.py -k root_lead_in -q -n0 --no-cov"` → `15 passed` |
| REQ-root-lead-in-warned | the same sentence reaches `spur info` and `/api/info` | live | `.venv/bin/spur info --profile-shift 0.75 --pressure-angle 20` → one warning naming `0.125 mm above the pitch circle` |
| REQ-readme-root-zone-states-the-limit | README states the measured condition and cites the warning; no "non-working root zone" | structural | `grep -nE 'Root fillets are computed analytically' -A4 README.md` reads `1.188 mm below the pitch circle on the default gear, but above it … when the root fillet exceeds half the dedendum` |
| REQ-filleted-spoke-closed-form | the filleted-spoke row and the other three plain rows match their closed forms at `abs=1e-9` mm³ | unit | `make test PYTEST_ARGS="tests/test_model.py -k each_cutout_is_exactly -q --no-cov"` |
| REQ-filleted-spoke-closed-form | the bar is load-bearing: a 1e-6 mm rim-corner root move and a skipped cutout step both go red | tripwire | `… -k cutout_proof_fails …` (two tests; the skip tripwire's control call passes on the unpatched build first) |
| REQ-filleted-spoke-closed-form | the four hole-through-web composed rows on the web formula at the human's bar; eleven composed rows named at `volume_rel=1e-6` | unit | `… -k 'every_feature_proof_holds_on_a_tip or proofs_hold_with_a_single_sided' …` |
| Whole phase | the part unchanged; two `must` debts retired with their shas | diff + ledger | `git diff --quiet 5d9e907 -- tests/regression/pre_v0_2.json src/spur/params.py`; `Resolved in: 825095f` and `61e1bea` in `docs/tech_debt/resolved/` |

All rows re-run green at `0a8837c` on 2026-10-05.

---

## Wave 0 Requirements

- [x] No new test file, fixture or install. The phase's tests live in the existing `tests/test_calc.py` (+90 lines) and `tests/test_model.py` (+281 lines); `make verify` went 910 → 927 across the phase; `requirements.txt` untouched.

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions | Outcome |
|----------|-------------|------------|-------------------|---------|
| Eleven composed-solid rows keep a 6 dp literal at `volume_rel=1e-6` because their closed form is not derived here (14-02's must-have asked for `abs=1e-9` everywhere) | REQ-filleted-spoke-closed-form | an explicit override of a plan truth; the human's call | read `14-VERIFICATION.md` `overrides` and the debt file's row list | accepted — 14-UAT Test 1, 2026-10-03 (`overrides_applied: 1`); tracked as `nice` debt `docs/tech_debt/active/2026-10-03-composed-cutout-volume-literals-pinned-at-six-places.md` with the recess-split integral named as the next step |
| The bar for the three tip-chamfer hole rows after their gaps measured 5.85e-10 / 5.94e-10 / 6.55e-10 mm³ (above 1e-9's headroom, below 1e-8) | REQ-filleted-spoke-closed-form | D-06 reserves a bar change for the human | re-run the four rows and read the docstring's measured gaps | decided — 14-04 Task 2, 2026-10-03: `noise-multiple 1e-8` (tip rows at `abs=1e-8`, the single-sided row at `abs=1e-9`); recorded in L33 and the test docstrings |
| The reworded sentences ("not derived here", never "cannot exist") in the debt file, L33 and three docstrings read true and sufficient (14-04 coverage D3) | REQ-filleted-spoke-closed-form | the claim scan proves the old phrases are gone; only a reader judges the new ones | read the five sites against 14-04-SUMMARY | read by the verifier at re-verification (14-VERIFICATION truth 7, `passed`); UAT was not re-run after 14-04, and `14-UAT.md` still lists G-14-2 and G-14-5 at `status: failed` although 14-04 (`gap_closure: true`) has its SUMMARY — a record inconsistency, not a behaviour gap |

---

## Validation Audit 2026-10-05

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

State A audit by the validate-phase orchestrator at `0a8837c`, run standalone two days after the phase landed (`20cd484`, #17). No `gsd-nyquist-auditor` was spawned: all three requirements classify COVERED by tests already in `make verify` (15 pure-maths cases, 23 built-solid cases, three closed-form oracles) plus commands over the record; a generated test here could only re-pin a literal the phase deliberately demoted or re-assert text the plans' scans already check. Of the three Manual-Only rows, two were settled by the human on 2026-10-03 and one stands on the verifier's read; `14-UAT.md`'s two gap entries were never flipped to `resolved` after 14-04 executed (noted above, left as is — this audit does not edit the UAT file).

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies — 11/11 tasks carry at least one `<automated>` command, the two decision checkpoints included (each has a nothing-changed or outcome-recorded check)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references — none were MISSING
- [x] No watch-mode flags
- [x] Feedback latency < 240s — ~64 s through the hook today; ~3.5 min serial at the phase's close
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-10-05
