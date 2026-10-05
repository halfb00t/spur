---
phase: "16"
slug: "typing-validation-debt"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-04"
validated: "2026-10-05"
---

# Phase 16 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

This phase ships one behaviour change (`model.py`'s two checked boundaries, proved by two
new pytest tests) and otherwise a record: a scoped mypy override, a `no-fake-done` block,
two Nyquist files for Phases 7 and 8, a debt file, an audit amendment and L35. Most proofs
are therefore commands over the committed tree, not new tests, and 16-02's prohibition
("MUST NOT turn discovery into scope") forbids writing tests for Phase 7 and 8 behaviour
here. Do not add a test that pins a documented figure or a config literal.

Audited 2026-10-05 (State A) at `a35432d` by the validate-phase orchestrator, dispatched as
the `verify:post` nyquist step after UAT (3/3 passed, `16-UAT.md`). The Per-Task map is
filled from the three PLAN.md `<automated>` blocks and the SUMMARYs' `coverage:` blocks;
every command that does not need a cold cache or a timing session was re-run at `a35432d`
and its result is in the Status cell. The cold-cache mypy run and the five-site gear tuple
were re-run the same day by the verifier (`16-VERIFICATION.md`, truths 7 and 8).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (`.venv/bin/python -m pytest --version`), with the `-n 8 --cov` recipe Phase 15 landed; nothing installed in this phase (`requirements.txt` byte-identical to `085e5a6`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]`, `[tool.coverage.report]` (`fail_under = 96`), `[tool.mypy]` (`strict`, `disallow_any_explicit`; the `[[tool.mypy.overrides]]` entry now names `OCP.*` alone, line 117) |
| **Quick run command** | `make test PYTEST_ARGS="tests/test_model.py -k 'non_body or not_a_shape' -q -n0 --no-cov"` → `2 passed, 201 deselected in 1.95s` (2026-10-05) |
| **Full suite command** | `make verify` — recipe `.venv/bin/python -m pytest -n 8 --cov --cov-report=term`; `929 passed in 62.60s`, 97.24 % against the 96 floor (verifier run, 2026-10-05); passed again through the pre-commit hook on `a35432d` |
| **Estimated runtime** | ~64 s warm through the hook on the dev host (15-VALIDATION's 63.555 s mean; this phase's hook runs read 62.60 s and 66.87 s of pytest) |

---

## Sampling Rate

- **After every task commit:** the pre-commit hook runs `make verify` itself (plain `git commit`, not `gsd_run query commit`, whose 30 s timeout cannot survive the ~64 s hook — 16-02's tooling note); run the quick command above while iterating on `model.py`
- **After every plan wave:** `make verify`, state the command and the result line in the reply (CLAUDE.md)
- **Before `/gsd-verify-work`:** `make verify` green; `git grep -nE 'type: ignore' -- 'src/spur/*.py'` prints nothing; `git diff --exit-code 085e5a6 -- tests/regression/pre_v0_2.json requirements.txt`
- **Max feedback latency:** ~64 s (one hook run on the dev host)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 16-01-T1 (tracer) | 01 | 1 | REQ-model-py-no-type-ignore | T-16-01, T-16-02, T-16-03, T-16-04 | the gate seen red at `085e5a6` before green; `isinstance` asserts the type claim on every call (no cast); the part unchanged; the message carries only a vendor class name | unit + gate + replay + AST | `-k 'non_body or not_a_shape'` → `2 passed`; `git grep -nE 'type: ignore' 085e5a6 -- 'src/spur/*.py'` → 5 lines, at HEAD → none; `rm -rf .mypy_cache && make typecheck` → `Success: no issues found in 37 source files`; `make test PYTEST_ARGS="tests/test_model.py tests/regression -q --no-cov"` + `git diff --quiet 085e5a6 -- tests/regression/pre_v0_2.json`; `build(GearParams(tip_chamfer=0.5))` → `('Solid', True, 4446.54642, 210, 604)`; 18 untouched functions AST-identical to `085e5a6` | ✅ `tests/test_model.py:250`, `:264` | ✅ green (`4f7e8fe`; re-run 2026-10-05: `2 passed, 201 deselected in 1.95s`, suppressions 0 now / 5 at `085e5a6`, fixture byte-identical; cold mypy and the tuple per 16-VERIFICATION truths 7-8) |
| 16-01-T2 | 01 | 1 | REQ-model-py-no-type-ignore | T-16-01, T-16-SC | the override narrowed to `OCP.*` only behind a byte-identical mypy gate; nothing installed | cmp + config assert + collect | `cmp` of the before/after cold-cache mypy captures; tomllib assert that only the override changed in `[tool.mypy]`; `implementation.md` bullet assert; debt file moved to `resolved/`; `--collect-only` → `929 tests collected` | — | ✅ green (`4f7e8fe`; re-run: `module = ["OCP.*"]` at `pyproject.toml:117`, `929 tests collected in 2.19s`, active debt copy gone) |
| 16-01-T3 | 01 | 1 | REQ-model-py-no-type-ignore | T-16-SC | the recorded sha is the commit that touched `model.py`; closure unchanged | structural + diff | `Resolved in:` sha resolves to the `refactor(16-01)` commit; REQUIREMENTS.md / ROADMAP.md phrase asserts; `test -z "$(git grep -nE 'type: ignore' -- 'src/spur/*.py')"`; `git diff --quiet 085e5a6 -- tests/regression/pre_v0_2.json requirements.txt` | — | ✅ green (`c11213e`; re-run: `Resolved in: 4f7e8fe`, one INDEX Resolved row, fixture and closure identical) |
| 16-02-T1 (checkpoint:human-action) | 02 | 2 | REQ-nyquist-phases-7-8 | T-16-06, T-16-07, T-16-08 | both values read from committed frontmatter, never asserted; no test written by the skill; no `--no-verify` | yaml read over committed files + git log | python/yaml prints `status` and `nyquist_compliant` of both files; `git log --grep '^test(phase-0?[78])' 085e5a6..HEAD` empty | — | ✅ green (the human's `655583f`, `5ba02d2`, `8ae468e`; re-run: 07 `validated` / `true`, last commit `5ba02d2`; 08 `validated` / `true`, last commit `8ae468e`) |
| 16-02-T2 | 02 | 2 | REQ-nyquist-phases-7-8 | T-16-06 | the gap count recomputed from each file's Manual-Only rows and Status cells, not copied | structural + the named tests | ledger rows equal the files' Manual-Only data rows (3 for 07, 0 for 08); the proofs the ledger names: `tests/regression`, `tests/test_calc.py::test_the_bore_rim_limit_is_the_bore_radius_for_round_and_d_flat_bores`, `tests/test_model.py::test_a_bore_chamfer_that_selects_no_rim_edges_is_a_build_error_not_a_bare_bore` | ✅ | ✅ green (16-02-SUMMARY § Gap ledger, coverage D2 pass; re-read 2026-10-05: 3 Manual-Only rows in `07-VALIDATION.md`, none in 08; the named tests ran inside the hook's `make verify` on `a35432d`) |
| 16-02-T3 (checkpoint:decision) | 02 | 2 | REQ-nyquist-phases-7-8 | T-16-11 | no `must` row filed as `nice` without the human's call | structural | ledger check: zero `must` rows → the D-09 gate is not reached | — | ✅ green (not reached: three rows, all `nice`; the classification judgment is listed under Manual-Only) |
| 16-03-T1 | 03 | 3 | REQ-nyquist-phases-7-8 | T-16-11 | one debt row per ledger row, none dropped, severity carried | structural | python: `gaps filed: 3 ledger rows, 1 debt files`; each gap text present in its file; one INDEX row | ✅ `docs/tech_debt/active/2026-10-05-phase-07-nyquist-gaps.md` | ✅ green (`4035b04`; re-run: file present, INDEX rows 1) |
| 16-03-T2 | 03 | 3 | REQ-nyquist-phases-7-8 | T-16-09, T-16-12 | the six original audit rows and the Overall line byte-identical to `085e5a6`; non-`nyquist` keys unchanged; committed on its own | yaml + regex + diff | `audit amended {07: compliant, 08: compliant} compliant`; `REQ and SC4 ok`; `milestone scope unchanged`; porcelain clean of product files | — | ✅ green (`3b9d977`; re-run: `missing_phases: []`, 07 and 08 in `compliant_phases`, `overall: compliant`, `amended:` dated 2026-10-05) |
| 16-03-T3 | 03 | 3 | REQ-model-py-no-type-ignore, REQ-nyquist-phases-7-8 | T-16-10, T-16-SC | every cited sha resolves; L21 untouched (0 deleted lines); fixture and closure identical | structural + full suite | `L35 ok [true, true] 10 shas resolve`; the PROJECT.md hand-off section present in 16-03-SUMMARY; end-state check (fixture, closure, no suppression, `src`/`tests` diff is two files, 929 collected); `make verify` | — | ✅ green (`71f474d`; re-run: one `## L35` heading and it is last, numstat `80/0` against `085e5a6`, `src`/`tests` diff = `src/spur/model.py tests/test_model.py`, `make verify` passed through the hook on `a35432d`) |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

Requirement classification (validate-phase §3): REQ-model-py-no-type-ignore COVERED (01-T1/T2/T3, 03-T3 — two pytest tests that run in every `make verify`, the `no-fake-done` gate, the fixture replay); REQ-nyquist-phases-7-8 COVERED (02-T1/T2/T3, 03-T1/T2/T3 — commands over the committed record). 0 PARTIAL, 0 MISSING. "Automated" for the second requirement means a command that reads the committed files and recomputes the count, the same meaning 15-VALIDATION.md gave it; the requirement is a record ("Phases 7 and 8 have a `VALIDATION.md` produced by `/gsd-validate-phase`; discovery only"), and the only product behaviour in the phase has its tests.

Requirement → proof map:

| Req ID | Behavior | Test Type | Automated Command |
|--------|----------|-----------|-------------------|
| REQ-model-py-no-type-ignore | no mypy suppression under `src/spur/`, and a new one is refused | gate | `make no-fake-done` (exit 0 today; its grep prints the five lines when run at `085e5a6`) |
| REQ-model-py-no-type-ignore | a non-body after `fillet`/`chamfer` input, or a non-`Shape` from `.val()`, raises `BuildError` with the full message | unit | `make test PYTEST_ARGS="tests/test_model.py -k 'non_body or not_a_shape' -q -n0 --no-cov"` → `2 passed` |
| REQ-model-py-no-type-ignore | mypy strict + `disallow_any_explicit` clean with no cache | typecheck | `rm -rf .mypy_cache && make typecheck` → `Success: no issues found in 37 source files` |
| REQ-model-py-no-type-ignore | the part is unchanged | replay + diff | `make test PYTEST_ARGS="tests/regression -q --no-cov"`; `git diff --exit-code 085e5a6 -- tests/regression/pre_v0_2.json` |
| REQ-nyquist-phases-7-8 | both files `status: validated`, `nyquist_compliant` as read | read | `grep -E '^(status\|nyquist_compliant):'` on `07-VALIDATION.md` and `08-VALIDATION.md` under `.planning/milestones/v0.2-phases/` |
| REQ-nyquist-phases-7-8 | every Manual-Only row is a debt row | structural | count the data rows of each file's `## Manual-Only Verifications` table against the debt file's `## Gaps` table (3 / 3; Phase 8 none / no file) |
| REQ-nyquist-phases-7-8 | the closed audit's history intact | diff | the six original `nyquist` rows and the Overall line byte-identical to `085e5a6` |
| Whole phase | fixture and runtime closure byte-unchanged | diff | `git diff --exit-code 085e5a6 -- tests/regression/pre_v0_2.json requirements.txt` |

All rows re-run green at `a35432d` on 2026-10-05 except the cold-cache mypy row, which stands on the verifier's run the same day (16-VERIFICATION, behavioral spot-check 2).

---

## Wave 0 Requirements

- [x] No new test file, fixture or install. The two refusal tests live in the existing `tests/test_model.py` (927 → 929 collected, 16-01), `requirements.txt` and the `[dev]` extras are byte-identical to `085e5a6`, and `git diff --name-only 085e5a6 HEAD -- src tests` is exactly `src/spur/model.py` and `tests/test_model.py`.

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions | Outcome |
|----------|-------------|------------|-------------------|---------|
| Every figure in L35 matches 16-01-SUMMARY, 16-02-SUMMARY or 16-CONTEXT (16-03 coverage D4; 16-03 judgment-tier prohibition) | both | "not estimated" is a judgment; the automated check only proves the shas resolve and the required facts are present | trace each figure to a source line; `git cat-file -t` each backticked sha | done — 16-UAT test 1, 2026-10-05: second trace recorded in the UAT (source lines per figure, ten shas / eight distinct all `commit`) |
| The cast clause of 16-01's prohibition has a standing gate or an accepted substitute (16-VERIFICATION human item 2) | REQ-model-py-no-type-ignore | a policy choice: a one-time AST check proved it, nothing keeps refusing a future `typing.cast` | decide: pin `cast(` in `no-fake-done`, file debt, or accept mypy strict + review | decided — 16-UAT test 2, 2026-10-05: mypy strict + `disallow_any_explicit` and review of `[tool.mypy]` are the standing enforcement; no pin, no debt item (`git grep` for `cast(` / `typing.cast` / `Any` under `src/spur/` prints nothing at `a35432d`) |
| Phase 7's record rests on the committed `07-VALIDATION.md`, not on the human's resume message (16-02 truths 2 and 4; 16-VERIFICATION human item 3) | REQ-nyquist-phases-7-8 | a disclosed deviation from a must-have truth; the human's call to accept | read 16-02-SUMMARY § Validation runs against the file's two `## Validation Audit` sections | accepted — 16-UAT test 3, 2026-10-05: both audit sections read `Gaps found 0` (file lines 105, 113); no third run requested |
| The corrected REQ-model-py-no-type-ignore, SC1, SC2, REQ-nyquist-phases-7-8 and SC4 sentences read true (16-01 coverage D4, 16-03 coverage D3) | both | the plans' checks assert key phrases, not meaning | read `REQUIREMENTS.md:152-166` and ROADMAP Phase 16 SC1/SC2/SC4 against 16-01-SUMMARY and 16-03-SUMMARY | read by the verifier 2026-10-05 (16-VERIFICATION truths 13 and 16); no separate human read recorded |
| The regeneration byte-stability row is a tool property with a named command (`nice`), not a behaviour without a test (`must`) (16-02 coverage D3) | REQ-nyquist-phases-7-8 | D-09's classification is a judgment the executor made and explained | read ledger row 2's "Proved today by" in 16-02-SUMMARY and the debt file's `Revisit when:` | stands as filed (`nice`, 16-VERIFICATION truth 15); no separate human ruling — the debt file's trigger is where it is revisited |

---

## Validation Audit 2026-10-05

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

State A audit by the validate-phase orchestrator at `a35432d`, dispatched from `/gsd-verify-work 16` as the `verify:post` nyquist step after UAT (3/3). No `gsd-nyquist-auditor` was spawned: both requirements classify COVERED, the one behaviour the phase added already has its two tests, and a generated test here would either pin a documented figure or a config literal (what this file's header forbids) or test Phase 7 and 8 behaviour, which 16-02's prohibition rules out. The five Manual-Only rows are judgments and policy decisions by nature; three were settled in the UAT the same day, two stand on the verifier's read and the filed debt trigger.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies — 9/9 tasks carry at least one `<automated>` command, the two checkpoints included (each reads the committed state after the human's action)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references — none were MISSING
- [x] No watch-mode flags
- [x] Feedback latency < 240s — ~64 s through the hook
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-10-05
