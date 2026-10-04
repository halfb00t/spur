---
status: complete
phase: 15-the-gate-measured-and-pinned
source: [15-VERIFICATION.md, 15-01-SUMMARY.md, 15-02-SUMMARY.md, 15-03-SUMMARY.md, 15-04-SUMMARY.md, 15-05-SUMMARY.md, 15-06-SUMMARY.md]
started: 2026-10-04T12:20:00Z
updated: 2026-10-04T13:20:00Z
---

## Current Test

[testing complete]

## Tests

### 1. The `backstop` truth: coverage total independent of combine order
expected: Either accept the recorded observation as sufficient (three `-n 8 --cov` totals identical at 97.21 % with 23 missed statements each, a fourth identical pair in 15-04's B1/B2, and CI's `-n 4` run at 97.29 %), or ask for a held-out/property test. The one observed divergence (serial runs at 96.99 %) is the flush-loss debt, not combine order; the order was never varied on purpose. Why human: the plan itself tags this truth `backstop`; equal totals on runs whose file-write order was not controlled do not prove order-independence, so the verifier abstained (insufficient_spec).
result: pass

### 2. The 14 flagged prohibitions (9 `verification: test`, 5 `judgment`)
expected: Each negative is true at HEAD 1eab497 — the verifier observed every one by its own commands (the Prohibitions table in 15-VERIFICATION.md carries the command behind each row) — but no standing wired enforcement exists for any of them. Accept the flagged `unverified-prohibition` items as "complete with 14 flagged prohibitions", or name any you want kept by a wired check. Why human: ADR-550 D4/D5d — a test-tier prohibition with no wired enforcement fails closed to flagged-unverified, and a judgment-tier prohibition is never a silent green; the fail-closed default, not an observed violation, holds `passed` back.
result: pass

### 3. Package legitimacy of pytest-xdist and pytest-cov (15-01 D5)
expected: The trust decision to install `pytest-xdist>=3.8` and `pytest-cov>=7.1` as `[dev]` extras was yours, recorded in 15-01-SUMMARY.md before the install, and still stands: both are the packages you meant (pytest-dev org on PyPI), and nothing else landed in `[dev]`, `requirements.txt` (byte-identical to 20cd484) or `[project] dependencies`. Why human: a PyPI trust call automation cannot establish; the checkpoint was blocking-human by design.
coverage_id: 15-01/D5
reason: human_judgment
result: pass

### 4. Makefile `test` recipe spells `--cov --cov-report=term` instead of the plan's literal text (15-02 D6)
expected: `make -n test` prints `.venv/bin/python -m pytest -n 8 --cov --cov-report=term $(PYTEST_ARGS)`; the explicit `--cov-report=term` exists so a leading path in `PYTEST_ARGS` is not swallowed as `--cov`'s optional argument. You accept that guard as the right one over the alternatives (`--cov=src/spur`, or moving `--cov` after `PYTEST_ARGS`), knowing 15-04's readings were taken on this recipe. Why human: a Rule 1 deviation from a plan-specified recipe; which guard is the maintainable one is a judgment no assertion covers.
coverage_id: 15-02/D6
reason: human_judgment
result: pass

### 5. Heaviest contributors and priced cuts in bench/RESULTS.md (15-03 D1)
expected: `bench/RESULTS.md` `### Heaviest contributors` names four files at 5 % or more of pytest's seconds, each with seconds, share, item count and a "what it proves" cell; every proposed cut (15 rows) is priced from the measured P1/P2 serial seconds and carries its proof-value cost. Each "what it proves" cell and each cost reads as accurate and fair to the test it describes. Why human: a reading of test bodies against Lxx records; the automated check only recomputed the shares from the duration columns.
coverage_id: 15-03/D1
reason: human_judgment
result: pass

### 6. The A row is a fair "Before" for the bar reading (15-04 D3)
expected: In `### Before and after`, A1/A2 (228.23 s, 229.75 s) were run serially with coverage by passing `-n0` over the recipe's `-n 8`, at load 14.15 and 19.17; B1/B2 (64.19 s, 62.92 s) at load 5.91 and 5.31. You accept that `-n0` on the xdist recipe is the same serial gate as C0's plain `pytest --cov` (the A walls sit 15-16 s under C0's 244.59 s) and that the load gap does not flatter the mean(B) 63.555 s against the 66 s bar. Why human: the Before was your choice at the checkpoint and the plan's A was serial without coverage; how the plugin behaves at `-n0` is a reading no assertion covers.
coverage_id: 15-04/D3
reason: human_judgment
result: pass

### 7. Constraint vs cadquery's own cap: what the green CI run proves (15-05 D4)
expected: CI run 37181871926 prints `cadquery 2.8.0 cadquery-ocp 7.9.3.1.1`, but cadquery 2.8.0's own `cadquery-ocp<8.0` cap would pick the same pair today, so the run alone cannot show `PIP_CONSTRAINT: requirements.txt` held it. The fail-closed evidence is the local dry run with a scratch constraint at `cadquery-ocp==8.0.1.0.0` -> `ResolutionImpossible` (recorded in 15-05-SUMMARY.md, reproduced by the verifier). You accept that this split -- CI proves the pair, the local dry run proves the mechanism -- is stated openly in RESULTS and L34 and is sufficient, or ask for a CI assertion that repeats it. Why human: no CI assertion distinguishes the two today.
coverage_id: 15-05/D4
reason: human_judgment
result: pass

### 8. L34 is a fair and complete account (15-06 D4)
expected: `docs/architecture/decision_log.md` L34 (appended after L33, amends L12 and L13, 0 deleted lines) weighs the evidence fairly: it names what was measured, what the bar is and who set it, and words the unproven as unproven -- the constraint-versus-cap reading and the lost worker flush. Figures, shas and the run URL match RESULTS and the SUMMARYs (spot-checked by the verifier). Why human: later phases read L34 as locked fact; the verifier checked the numbers match their sources, not that the paragraphs weigh the evidence fairly.
coverage_id: 15-06/D4
reason: human_judgment
result: pass

### 9. Serial gate profiled per stage, per file and slowest 25 into bench/RESULTS.md
expected: Serial gate profiled per stage, per file and slowest 25 (two runs, P1 and P2, 927 passed each) into bench/RESULTS.md with host state and the reproducible run recipe
result: pass
source: automated
coverage_id: 15-01/D1

### 10. pytest-xdist and pytest-cov installed as [dev] extras only
expected: pytest-xdist>=3.8 and pytest-cov>=7.1 installed as [dev] extras only; requirements.txt byte-identical to 20cd484; addopts unchanged
result: pass
source: automated
coverage_id: 15-01/D2

### 11. xdist sweep recorded with knee rule stated before the table
expected: xdist sweep S2/S4/S8/S12 recorded with load, pytest line, wall, peak tree RSS and exit; knee rule stated before the table; Apparent knee N = 8
result: pass
source: automated
coverage_id: 15-01/D3

### 12. REQ and ROADMAP say the bar is set at the profile checkpoint
expected: REQ-verify-profiled acceptance and ROADMAP Phase 15 Depends-on / SC2 / Research flag say the bar is set at the profile checkpoint; milestone scope identical before and after
result: pass
source: automated
coverage_id: 15-01/D4

### 13. BuildPool's spawned-worker lines are counted
expected: BuildPool's spawned-worker lines are counted: concurrency multiprocessing + thread, parallel, sigterm; tests/test_pool.py reads pool.py at 100.00 % serially and at -n 2
result: pass
source: automated
coverage_id: 15-02/D1

### 14. Baseline, alternating runs, coverage cost and floor line recorded
expected: Baseline C0 (96.99 %), six alternating runs at -n 8 (all 927 passed, B totals 97.21 x3), D-05 verdict adopted, coverage cost 3.51 s, and the floor line recorded in bench/RESULTS.md
result: pass
source: automated
coverage_id: 15-02/D2

### 15. fail_under = 96 read from config; partial run fails, --no-cov exits 0
expected: fail_under = 96 and precision = 2 in [tool.coverage.report]; make test runs --cov with the floor read from config; a test_calc-only run fails the floor and the same with --no-cov exits 0; adjacency probe (96 passes, 95.99 fails)
result: pass
source: automated
coverage_id: 15-02/D3

### 16. Red on the floor recorded, nothing committed
expected: Red on the floor: a full run without tests/test_cli.py read 90.24 % against 96 and failed; recorded in RESULTS, tree untouched, nothing committed
result: pass
source: automated
coverage_id: 15-02/D4

### 17. Coverage-floor debt retired with its sha
expected: The coverage-floor debt retired with its sha (2aadcea), pytest-cov sentence corrected, INDEX row moved; REQ-coverage-floor and ROADMAP SC3 say fail_under is where the floor is read and state the settled worker mechanism
result: pass
source: automated
coverage_id: 15-02/D5

### 18. D-01 checkpoint ran with nothing written before the answer
expected: The D-01 checkpoint ran with the committed record in front of the human; nothing was written or applied before the answer
result: pass
source: automated
coverage_id: 15-03/D2

### 19. The human's answer recorded verbatim in one commit
expected: The human's answer verbatim in 15-CONTEXT.md under D-01 and in RESULTS ### Gate decision, with the bar in seconds, N, every cut ruled on by name and the Before row, in one commit
result: pass
source: automated
coverage_id: 15-03/D3

### 20. src/, tests/, Makefile and pyproject.toml unchanged by 15-03
expected: src/, tests/, Makefile and pyproject.toml unchanged by this plan
result: pass
source: automated
coverage_id: 15-03/D4

### 21. The gate runs on pytest-xdist workers via the Makefile only
expected: The gate runs on pytest-xdist workers: make test passes -n $(PYTEST_WORKERS), 8 clamped to the host's CPUs, with --cov --cov-report=term unseparated; no -n auto, addopts untouched, no rerun plugin
result: pass
source: automated
coverage_id: 15-04/D1

### 22. The 66 s bar is met by alternating A/B runs
expected: The 66 s bar is read by alternating A1 B1 A2 B2 runs: mean(B) 63.555 s against 66 s is met, 927 passed in every row, test count unchanged
result: pass
source: automated
coverage_id: 15-04/D2

### 23. CI's make verify installs under the L12 closure
expected: CI's make verify installs under the L12 closure: PIP_CONSTRAINT: requirements.txt on the step, the pair printed by the always-run step after it, the pin's whereabouts written in the ci.yml comment and the tripwire's docstring
result: pass
source: automated
coverage_id: 15-05/D1

### 24. One green CI run on the pin's head shows the pair
expected: One green CI run on the pin's head whose log shows the pair, 4 xdist workers and a clean pytest line (SC4's proof, SC5's run)
result: pass
source: automated
coverage_id: 15-05/D2

### 25. CI-kernel debt retired with the pin's sha and run URL
expected: The CI-kernel debt retired with the pin's sha and the run URL; INDEX row moved; D-13's sentences in the REQ and SC4; ROADMAP milestone scope identical before and after
result: pass
source: automated
coverage_id: 15-05/D3

### 26. Every ~11 s site now states the measured gate time
expected: Every site that said ~11 s now states the measured gate time with its configuration: .pre-commit-config.yaml carries 63.555 s and names the Before and after section and date; README, HOW_TO_DEVELOP (Russian) and packaging.md carry ~64; the debt file carries ~64 s warm twice and stays active
result: pass
source: automated
coverage_id: 15-06/D1

### 27. L34 appended, amending L12 and L13, every figure traceable
expected: L34 appended after L33, amending L12 and L13, 0 deleted lines against 20cd484, every seconds figure traceable to RESULTS, the run URL, the shas and the bar cited
result: pass
source: automated
coverage_id: 15-06/D2

### 28. Phase end state: gate green under its floor, fixture and src/ unchanged
expected: The phase's end state: make verify green under its floor and 8 workers; pre_v0_2.json, src/ and requirements.txt unchanged since 20cd484; both Phase 15 debts in resolved/ and once in INDEX Resolved; 927 tests collected
result: pass
source: automated
coverage_id: 15-06/D3

## Summary

total: 28
passed: 28
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps
