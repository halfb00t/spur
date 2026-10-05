---
phase: "15"
slug: "the-gate-measured-and-pinned"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-03"
validated: "2026-10-04"
---

# Phase 15 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

Source: `15-RESEARCH.md` § Validation Architecture. This phase ships configuration and a
measurement record, not product behaviour, so most proofs are commands whose output is
checked, not new pytest tests. Do not add a test that pins the `fail_under` literal — it
would restate the config and fail on every legitimate re-pin.

Audited 2026-10-04 (State A): the Per-Task map below is filled from the six PLAN.md
`<verify>` blocks and the SUMMARYs' recorded results, and every command that can be re-run
without a timing session was re-run at `fc4bc7b` — the measurement rows stand on the
committed record and its recompute checks.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1; `pytest-xdist` 3.8.0 and `pytest-cov` 7.1.0 as `[dev]` extras (15-01) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (untouched: `addopts = "--strict-markers --strict-config"`) and `[tool.coverage.run]` / `[tool.coverage.report]` (`fail_under = 96`, `precision = 2`) |
| **Quick run command** | `make test PYTEST_ARGS="tests/test_pr_land.py tests/test_bench.py -q --no-cov -n0"` (`PYTEST_ARGS` comes last, so `-n0`/`--no-cov` override the recipe) |
| **Full suite command** | `make verify` — `pytest -n 8 --cov --cov-report=term`, 927 passed, 97.21 % against the 96 floor |
| **Estimated runtime** | 63.555 s warm on the 12-core dev host (mean(B), `bench/RESULTS.md` § Before and after); ~64 s through the pre-commit hook; 203.16 s of pytest at `-n 4` on CI (run 37181871926) |

---

## Sampling Rate

- **After every task commit:** the pre-commit hook runs `make verify` itself (plain `git commit`, D-21 — `gsd_run query commit`'s 30 s timeout cannot survive the ~64 s hook); run the quick command above while iterating
- **After every plan wave:** `make verify`, state the command and the result line in the reply (CLAUDE.md)
- **Before `/gsd-verify-work`:** `make verify` green; the three D-05 tolerance runs; the CI run URL; `git diff --exit-code 20cd484 -- tests/regression/pre_v0_2.json src`
- **Max feedback latency:** ~64 s (one hook run on the dev host after 15-04 landed `-n 8`; ~240 s before it)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 15-01-T1 (tracer) | 01 | 1 | REQ-verify-profiled | T-15-01 | run recipe quoted in § Method; every run recorded as it ran | structural (python assert over the RESULTS section) | python: headings `Host state … Slowest 25`, P1/P2 rows `927 passed`, 11 per-file rows summing to 927, 25 duration lines, host state → `profile ok`; `git diff --quiet 20cd484 -- src tests Makefile pyproject.toml requirements.txt` | — | ✅ green (`39eb062`; re-run 2026-10-04: 16 subsections, 0 full-run rows without `927 passed`) |
| 15-01-T2 | 01 | 1 | REQ-verify-at-the-bar | T-15-SC | nothing installed before the human's answer | checkpoint:human-verify (package legitimacy) | `git diff --quiet HEAD -- pyproject.toml && test -z "$(pip show pytest-xdist pytest-cov)"` → `nothing installed before the answer` | — | ✅ green (answer `approved`, 15-01-SUMMARY:131) |
| 15-01-T3 | 01 | 1 | REQ-verify-profiled, REQ-verify-at-the-bar | T-15-02 | the two packages in `[dev]` only; closure untouched | config assert + recompute + diff | tomllib assert over `[dev]` and `[project] dependencies` → `extras ok`; knee recomputed from the sweep table by the pre-registered rule → `sweep ok, knee 8`; `git diff --quiet 20cd484 -- requirements.txt` | — | ✅ green (`65ef9db`; re-run: `pyproject.toml:27-28`, closure byte-identical, 31 pins) |
| 15-02-T1 | 02 | 2 | REQ-coverage-floor | T-15-03 | `source` unchanged, no `omit`, the `thread` entry kept | config assert + run | tomllib assert over `[tool.coverage.run]`; `make test PYTEST_ARGS="tests/test_pool.py --cov-report=term-missing -q"` → `pool.py` row `54 0 6 0 100.00%` (serial and `-n 2`) | — | ✅ green (`f771c5e`; re-run 2026-10-04 `-n0`: `src/spur/pool.py 54 0 6 0 100.00%`, 16 passed in 27.01 s) |
| 15-02-T2 | 02 | 2 | REQ-coverage-floor, REQ-verify-profiled | T-15-04 | F recomputed from the table's own totals | recompute | python recomputes L = 96.99, S = 0.00, F = 96 from the RESULTS tables → `floor ok 96`; `git diff --quiet 20cd484 -- src tests/regression requirements.txt`; commit touches RESULTS only | — | ✅ green (`6599677`) |
| 15-02-T3 | 02 | 2 | REQ-coverage-floor | T-15-04 | the literal tied to the RESULTS line; `tests/` untouched by the red run | config assert + boundary + recipe | `should_fail_under(96, 96, 2)` False / `(95.99, 96, 2)` True → `floor wired 96`; `make -n test \| grep -c -e '-m pytest --cov'` = 1; red run recorded in § Red on the floor, tree untouched | — | ✅ green (`2aadcea`; re-run: `make -n test` prints `-n 8 --cov --cov-report=term`; `git check-ignore .coverage .coverage.host.1.x` prints both) |
| 15-03-T1 | 03 | 3 | REQ-verify-profiled | T-15-07 | savings priced from the recorded serial run only | recompute (plan regex fixed — 15-03 deviation 2) | mean share from the P1/P2 seconds columns → `contributors and cuts ok`, 15 rows; commit touches RESULTS only | — | ✅ green (`0a74eed`) |
| 15-03-T2 | 03 | 3 | REQ-verify-at-the-bar | T-15-06 | nothing written or applied before the answer | checkpoint:decision (the bar, N, cuts) | `'(profile checkpoint, 15-03' not in 15-CONTEXT.md`; `git diff --quiet HEAD -- Makefile pyproject.toml tests src` exit 0 | — | ✅ green (answer verbatim: `knee-headroom N=8 bar=66 cuts=none before=244.59`) |
| 15-03-T3 | 03 | 3 | REQ-verify-at-the-bar | T-15-06 | the two copies of the answer match | structural | CONTEXT D-01 addendum vs RESULTS § Gate decision → `decision recorded: …`; one commit touching exactly the two files → `decision committed` | — | ✅ green (`df607f9`) |
| 15-04-T1 | 04 | 4 | REQ-verify-at-the-bar | T-15-08, T-15-10 | no cut applied; fixture/`src`/closure unchanged; CPU clamp present, `-n` out of `addopts` | structural + diff | Makefile/addendum assert → `make test runs -n 8`; `git diff --quiet 20cd484 -- src tests/regression/pre_v0_2.json requirements.txt` → `D-20 ok`; `git diff --quiet 20cd484 -- tests` | — | ✅ green (`5797199`; re-run: recipe `-n 8 --cov --cov-report=term`, byte-identical to `20cd484`) |
| 15-04-T2 | 04 | 4 | REQ-verify-at-the-bar, REQ-verify-profiled | T-15-09 | verdict recomputed from the rows and the addendum's bar | recompute | mean(B) from the A/B rows against the bar → `verdict met 63.55 bar 66.0`; commit touches RESULTS only → `reading committed` | — | ✅ green (`b8b4dd1`) |
| 15-04-T3 | 04 | 4 | REQ-verify-at-the-bar | T-15-09 | — | checkpoint:decision (on a miss only — not reached, bar met) | `git diff --quiet HEAD -- Makefile tests pyproject.toml` → `nothing changed after the reading` | — | ✅ green (check ran; no miss, no decision needed) |
| 15-05-T1 | 05 | 5 | REQ-ci-installs-the-pinned-kernel | T-15-11, T-15-SC | the constraint on the installing step; a conflicting pin fails closed | yaml assert + unit + dry run | ci.yml assert → `ci.yml ok`, `pin scope ok`; `pytest tests/test_pr_land.py + tripwire` → 59 passed; `PIP_CONSTRAINT=requirements.txt pip install --dry-run -e '.[dev]'` resolves the pair / scratch `cadquery-ocp==8.0.1.0.0` → `ResolutionImpossible` | — | ✅ green (`839dfea`; re-run 2026-10-04: `59 passed in 3.11s`) |
| 15-05-T2 | 05 | 5 | REQ-ci-installs-the-pinned-kernel | T-15-13 | one draft PR, opened once, after the local proof | remote state | `git ls-remote` head equals HEAD; `gh run list --event pull_request` → one run on HEAD, ended → `one draft PR at HEAD 18`, `the run on HEAD has ended` | — | ✅ green (PR #18, run 37181871926) |
| 15-05-T3 | 05 | 5 | REQ-ci-installs-the-pinned-kernel | T-15-14 | the run's conclusion and pair line re-read from GitHub | CI log + structural | `gh run view <id from RESULTS>` → success + `cadquery 2.8.0 cadquery-ocp 7.9.3.1.1`; debt file and INDEX → `debt ok 839dfea`, `D-13 sentences ok` | — | ✅ green (`454af54`; re-read 2026-10-04: success, head `839dfea`, `created: 4/4 workers`, `97.29%`) |
| 15-06-T1 | 06 | 6 | REQ-verify-at-the-bar | T-15-16 | every corrected site carries mean(B) | grep | `git grep -E '~11 ?s'` outside the decision log and `.planning` exits 1 → `no eleven-second claim left`; `63.555` at every site → `measured figure at every site` | — | ✅ green (`ad99df9`; re-run: no hit) |
| 15-06-T2 | 06 | 6 | REQ-verify-profiled (cites all four) | T-15-15, T-15-16 | append-only; every figure traceable to RESULTS or a SUMMARY | numstat + structural | `git diff --numstat 20cd484 -- docs/architecture/decision_log.md` deleted column = 0; L34 last and unique, figures/shas/URL/bar matched → `L34 ok` | — | ✅ green (`298677a`; re-run: `133 0`, one `## L34 ` heading, last entry) |
| 15-06-T3 | 06 | 6 | all four | — | — | full suite + diff + collect | `make verify` → `927 passed`, `97.21%` against 96; `git diff --exit-code 20cd484 -- tests/regression/pre_v0_2.json src requirements.txt`; `pytest --collect-only -q` → 927; both debts in `resolved/` and once in INDEX Resolved | — | ✅ green (no commit; `make verify` passed through the hook on `49dcdaf`, `20f33c4`, `9a773b0`, `fc4bc7b`) |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

Requirement classification (validate-phase §3): REQ-verify-profiled COVERED (T1, T3, 02-T2, 03-T1, 04-T2, 06-T2); REQ-verify-at-the-bar COVERED (01-T2/T3, 03-T2/T3, 04-T1/T2/T3, 06-T1); REQ-coverage-floor COVERED (02-T1/T2/T3, 06-T3); REQ-ci-installs-the-pinned-kernel COVERED (05-T1/T2/T3). 0 PARTIAL, 0 MISSING. "Automated" here means a command over the committed record, the config or the remote run plus the three existing pytest files the phase leans on (`tests/test_pr_land.py`, the tripwire in `tests/regression/test_pre_v0_2.py`, `tests/test_pool.py`); no pytest test was added, by design (Wave 0, third item), and the test count is 927 before and after.

Requirement → proof map (from research):

| Req ID | Behavior | Test Type | Automated Command |
|--------|----------|-----------|-------------------|
| REQ-verify-profiled | RESULTS section has the per-stage, per-file, top-N, sweep {2,4,8,12}, three tolerance rows, cost rows, host-state header | structural | `grep -nE '^(##|###) ' bench/RESULTS.md \| tail -20`; every full-run row says `927 passed` |
| REQ-verify-profiled | xdist tolerance is measured | measurement | three consecutive `make verify` runs at the chosen N, each `927 passed`, exit 0, zero reruns |
| REQ-verify-at-the-bar | wall time at or under the bar, same method | measurement | `/usr/bin/time -p make verify` alternating A/B, `sysctl -n vm.loadavg` before each; `mean(B) <= bar` |
| REQ-verify-at-the-bar | runtime closure untouched | diff | `git diff --exit-code 20cd484 -- requirements.txt` |
| REQ-verify-at-the-bar | hook comment corrected | grep | `git grep -n '~11' -- ':!bench/RESULTS.md' ':!docs/architecture/decision_log.md' ':!.planning/codebase'` returns only D-19 sites |
| REQ-coverage-floor | `pytest-cov` in `[dev]`; floor in config | grep | `grep -n 'pytest-cov\|fail_under\|precision' pyproject.toml` |
| REQ-coverage-floor | worker lines counted | run | `make test PYTEST_ARGS="tests/test_pool.py --cov-report=term-missing:skip-covered -q"` — `pool.py` absent from skip-covered list or without 50, 63-67 |
| REQ-coverage-floor | gate goes red below the floor | run | `make verify PYTEST_ARGS="--ignore=tests/test_cli.py"` exits non-zero with `Coverage failure` (recorded, not committed) |
| REQ-coverage-floor | `.coverage*` ignored | grep | `git check-ignore .coverage .coverage.host.1.x` prints both |
| REQ-ci-installs-the-pinned-kernel | the pair on CI | CI log | `gh run view <id> --log \| grep -E 'cadquery 2.8.0 cadquery-ocp 7.9.3.1.1'` |
| REQ-ci-installs-the-pinned-kernel | tripwire stays | unit | `.venv/bin/python -m pytest -n0 --no-cov tests/regression/test_pre_v0_2.py::test_the_fixture_was_captured_on_the_kernel_this_run_uses -q` |
| REQ-ci-installs-the-pinned-kernel | ci.yml edit keeps required jobs | unit | `.venv/bin/python -m pytest -n0 --no-cov tests/test_pr_land.py -q` |
| SC5 / D-18 | both debt files retired | grep | `grep -c 'active/2026-09-21-no-coverage-floor\|active/2026-09-26-ci-resolves' docs/tech_debt/INDEX.md` equals 0 |
| Whole phase | fixture and `src/` byte-unchanged (D-20) | diff | `git diff --exit-code 20cd484 -- tests/regression/pre_v0_2.json src` |

All fourteen rows re-run green at `fc4bc7b` on 2026-10-04 except the two measurement rows (tolerance, A/B timing), which stand on the recorded runs in `bench/RESULTS.md` § Tolerance and coverage cost and § Before and after and on 15-04-T2's recompute check.

---

## Wave 0 Requirements

- [x] `pyproject.toml` `[dev]` gains `pytest-xdist>=3.8`, `pytest-cov>=7.1`, then one `make` to install them — done in 15-01 Task 3 (`65ef9db`) after the Task 2 legitimacy checkpoint
- [x] `.gitignore` gains `.coverage*` — done in 15-02 Task 1 (`f771c5e`), before the first `--cov` run landed on a commit
- [x] No new test files or fixtures. Existing tests cover the touched seams: `tests/test_pr_land.py` (ci.yml parser), `tests/regression/test_pre_v0_2.py` (the tripwire, docstring-only edit in 15-05), `tests/test_pool.py` (worker-coverage proof) — held: `git diff 20cd484 HEAD --stat -- tests` is one file, +7/−1

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions | Outcome |
|----------|-------------|------------|-------------------|---------|
| CI resolves `cadquery==2.8.0` / `cadquery-ocp==7.9.3.1.1` on the Linux runner | REQ-ci-installs-the-pinned-kernel | the run exists only after a push; the local dry-run is a simulation of linux/x86_64 | push the branch; `gh run view <id> --log`; record the URL in L34 and the retired debt file (D-16) | done — run 37181871926 (`839dfea`, success) printed the pair; URL in L34 and the resolved debt file; re-read 2026-10-04 |
| The bar is read at or under on the dev host | REQ-verify-at-the-bar | load-dependent timing; the human sets the number at the D-01 checkpoint | alternate A/B `make verify` runs in one session with load recorded (D-04); before/after rows in `bench/RESULTS.md` | done — bar 66 s set at 15-03; A1 228.23 / B1 64.19 / A2 229.75 / B2 62.92 s, loads recorded; mean(B) 63.555 s, met (`b8b4dd1`); the human accepted the Before row as fair (15-UAT test 6) |

---

## Validation Audit 2026-10-04

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

State A audit by the validate-phase orchestrator at `fc4bc7b`, after UAT (28/28), security (22/22 closed) and the phase transition. No `gsd-nyquist-auditor` was spawned: the gap analysis found no MISSING or PARTIAL requirement, and the phase's own design (research § Validation Architecture; Wave 0, third item; L34's "no test removed, skipped, sampled or marked" and the 927 count) rules out adding tests here — a generated test would have to pin a measured literal or a config value, the exact thing this file's header forbids. The two Manual-Only rows are measurement and CI by nature; both were completed and recorded.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies — 18/18 tasks carry at least one `<automated>` command, the three checkpoints included (each has a nothing-written-before check)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references — none were MISSING
- [x] No watch-mode flags
- [x] Feedback latency < 240s — ~64 s through the hook since 15-04
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-10-04
