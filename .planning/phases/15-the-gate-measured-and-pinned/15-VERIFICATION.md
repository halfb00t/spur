---
phase: 15-the-gate-measured-and-pinned
verified: 2026-10-04T12:00:00Z
status: passed
score: 15/16 must-haves verified
covered_files:
  - .github/workflows/ci.yml
  - .gitignore
  - .planning/phases/15-the-gate-measured-and-pinned/15-01-PLAN.md
  - .planning/phases/15-the-gate-measured-and-pinned/15-01-SUMMARY.md
  - .planning/phases/15-the-gate-measured-and-pinned/15-02-PLAN.md
  - .planning/phases/15-the-gate-measured-and-pinned/15-02-SUMMARY.md
  - .planning/phases/15-the-gate-measured-and-pinned/15-03-PLAN.md
  - .planning/phases/15-the-gate-measured-and-pinned/15-03-SUMMARY.md
  - .planning/phases/15-the-gate-measured-and-pinned/15-04-PLAN.md
  - .planning/phases/15-the-gate-measured-and-pinned/15-04-SUMMARY.md
  - .planning/phases/15-the-gate-measured-and-pinned/15-05-PLAN.md
  - .planning/phases/15-the-gate-measured-and-pinned/15-05-SUMMARY.md
  - .planning/phases/15-the-gate-measured-and-pinned/15-06-PLAN.md
  - .planning/phases/15-the-gate-measured-and-pinned/15-06-SUMMARY.md
  - .pre-commit-config.yaml
  - Makefile
  - bench/RESULTS.md
  - docs/architecture/decision_log.md
  - pyproject.toml
  - tests/regression/test_pre_v0_2.py

covered_digest: "v2:sha256:71f9dd5b365c7ced5bd8e78d146f6e07e476bfc78be31cca04d08836f99243d9"
behavior_unverified: 0
overrides_applied: 0
gaps: []
deferred: []
coincidental_reliance_items: []
human_verification:
  - test: "Accept or refuse the one non-inferable (`verification: backstop`) truth from 15-02: 'the combined coverage total does not depend on the order in which the per-process data files are written or combined'"
    expected: "Either accept the recorded observation as sufficient (three -n 8 --cov totals identical at 97.21 % with 23 missed statements each, a fourth identical set in 15-04's B1/B2, and CI's -n 4 run at 97.29 %), or ask for a held-out/property test. Note the one observed divergence: serial C0 and 15-04's A1/A2 read 96.99 % because worker lines 63-67 and 222 of pool.py were lost (the flush-loss debt, `docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md`) -- a different cause than combine order, but the order was never varied on purpose."
    why_human: "The plan itself tags this truth `backstop`; presence, wiring and equal totals on runs whose file-write order was not controlled do not prove order-independence. The verifier abstains (insufficient_spec) rather than mark it VERIFIED."
  - test: "Confirm the 14 `must_haves.prohibitions` (9 `verification: test`, 5 `judgment`; see the Prohibitions table) hold -- the verifier observed each negative at HEAD by its own commands, but no standing wired enforcement exists for any of them"
    expected: "Each negative is true at HEAD 1eab497 (evidence column below). Accept the flagged `unverified-prohibition` items as 'complete with N flagged prohibitions', or ask for a wired check on any you want kept."
    why_human: "ADR-550 D4/D5d: a test-tier prohibition with no wired enforcement fails closed to flagged-unverified, and a judgment-tier prohibition is never a silent green. The fail-closed default, not an observed violation, is what holds `passed` back."
---

# Phase 15: The Gate, Measured and Pinned -- Verification Report

**Phase Goal:** `make verify`'s wall time, the bar set from it, and a coverage floor are all numbers in `bench/RESULTS.md`, not estimates -- and CI installs the exact kernel pair the regression fixture's provenance header names, so the fixture's exact-value assertions stay honest.
**Verified:** 2026-10-04
**HEAD:** `1eab497` on `gsd/phase-15-the-gate-measured-and-pinned` (head of draft PR #18)
**Status:** human_needed
**Re-verification:** No -- initial verification

## Verdict in one paragraph

The goal is achieved in the codebase. No truth failed, no artifact is a stub, no key link is broken, no blocker anti-pattern was found. Every number the goal names exists in `bench/RESULTS.md`'s Phase 15 section and matches the code that cites it (Makefile, `pyproject.toml`, `.pre-commit-config.yaml`, L34). The kernel pair claim is proven by a green CI run whose log I re-read, and the constraint's fail-closed behaviour I reproduced. The status is `human_needed`, not `passed`, for two reasons only: one non-inferable (`backstop`) truth the verifier must abstain on, and the ADR-550 fail-closed rule for prohibitions that have no wired enforcement. Both are listed under Human Verification; neither is a defect found.

## Goal Achievement

### Observable Truths

ROADMAP success criteria (the contract) first, then the plan-level truths that add detail.

| #  | Truth | Status | Evidence |
|----|-------|--------|----------|
| SC1 | `bench/RESULTS.md` records `make verify`'s wall time per stage, pytest's per-file and top-N `--durations`, the heaviest contributors named with what each proves, and xdist tolerance measured | VERIFIED | `bench/RESULTS.md:2302-2446`. Per-stage table (ruff 0.07/0.03, mypy 0.37/0.20, import-linter 0.11/0.09, scan 0.02/0.01, pytest 229.63/218.03 s; whole gate 230.20/218.36 s), per-file table (11 files, 927 items, sorted P1 desc), slowest 25 verbatim, sweep N=2/4/8/12 all green with RSS. `### Heaviest contributors` (line 2583) names four files at >=5 % with what each proves. Loads recorded per run (6.53, 9.09). Tolerance: six alternating runs at N=8, 6 of 6 green (line 2519). |
| SC2 | The bar the human set at the profile checkpoint (dated addendum under D-01) is read at or under, measured the same way; before/after rows; test count unchanged or named; the hook's "~11 s" comment corrected | VERIFIED | Addendum present at `15-CONTEXT.md:63-79` with the verbatim answer `knee-headroom N=8 bar=66 cuts=none before=244.59`. `### Before and after` (RESULTS:2720): A1 228.23, B1 64.19, A2 229.75, B2 62.92; mean(B) 63.555 s <= 66 s, "met". Every row `927 passed`, exit 0; no cut applied, so no difference to name (`git diff 20cd484 HEAD -- tests` is the tripwire docstring only). `.pre-commit-config.yaml:6-8` now reads "A warm run measured 63.555 s ... Before and after". Arithmetic re-checked: (64.19+62.92)/2 = 63.555. |
| SC3 | `pytest-cov` in `[dev]`; one baseline recorded; `fail_under` just under it; `make verify`'s test target runs `--cov` reading the floor from `fail_under`; a scratch red run recorded; worker coverage settled | VERIFIED | `pyproject.toml:27-28` (`pytest-xdist>=3.8`, `pytest-cov>=7.1` in `dev` only). C0 baseline 96.99 % (RESULTS:2448-2492). `[tool.coverage.report] fail_under = 96`, `precision = 2`; `[tool.coverage.run]` `concurrency = ["multiprocessing", "thread"]`, `parallel = true`, `sigterm = true`. Makefile `test:` = `$(PY) -m pytest -n $(PYTEST_WORKERS) --cov --cov-report=term $(PYTEST_ARGS)`, no `--cov-fail-under` anywhere (grep: only a comment in pyproject). Red run recorded (RESULTS:2550, 90.24 % vs 96, `tests/test_cli.py` left out); `git log -S'--ignore=tests/test_cli.py'` finds no commit. I re-ran `tests/test_pool.py` with `--cov`: `src/spur/pool.py 54 0 6 0 100.00 %` (worker lines counted). |
| SC4 | CI's `make verify PYTHON=python` resolves `cadquery==2.8.0`/`cadquery-ocp==7.9.3.1.1` by D-13's mechanism, proven by a green CI run URL showing the pair, logged as an Lxx against L12; the tripwire stays | VERIFIED | `ci.yml`: `env: PIP_CONSTRAINT: requirements.txt` on the `make verify PYTHON=python` step, plus `kernel pair this run resolved` step with `if: always()`. I re-read run 37181871926 with `gh`: `pull_request` event, head `839dfea`, conclusion success, `test (3.12)`, `image`, `vendor-bundle` all success; log line `cadquery 2.8.0 cadquery-ocp 7.9.3.1.1`, `created: 4/4 workers`, `927 passed in 203.16s`, `97.29 %` vs floor 96. L34 appended (decision_log.md, "amends L12 and L13"). Tripwire test still present, assertion body unchanged, docstring now names the pin. I reproduced fail-closed: `PIP_CONSTRAINT=<requirements.txt with cadquery-ocp==8.0.1.0.0> pip install --dry-run -e '.[dev]'` -> `ResolutionImpossible`; with the real file it resolves `cadquery-2.8.0`, `cadquery-ocp-7.9.3.1.1`. |
| SC5 | Both debt files retire with their sha; any new dev dependency lands only in `[dev]`; `requirements.txt`'s 31 pins unchanged | VERIFIED | `docs/tech_debt/resolved/2026-09-21-no-coverage-floor.md` (`Resolved in: 2aadcea`, which is `test(15-02): gate make verify on a coverage floor`) and `resolved/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md` (`Resolved in: 839dfea` + the run URL); both gone from `active/`; INDEX rows moved (INDEX:49-50). `git diff --quiet 20cd484 -- requirements.txt` exits 0; `grep -c '==' requirements.txt` = 31. |
| 6 | The bar and N were set by the human at a checkpoint with nothing written before the answer (15-03) | VERIFIED | `0a74eed` touches `bench/RESULTS.md` only; `df607f9` (CONTEXT addendum + RESULTS Gate decision) is the commit after the answer; `git diff` of Makefile/pyproject across the 15-03 commits is empty. |
| 7 | `-n` and `--cov` live in the Makefile `test` recipe only, never `addopts`; `PYTEST_WORKERS` is a literal 8 clamped to online CPUs | VERIFIED | `pyproject.toml` `addopts = "--strict-markers --strict-config"` unchanged. Makefile line 85: `w=8; n=$(getconf _NPROCESSORS_ONLN); echo $(( n < w ? n : w ))`. CI printed `4/4 workers` (clamp working). |
| 8 | Probe (empty): a partial run fails on the floor and `--no-cov` exits 0 | VERIFIED | I ran both. `make test PYTEST_ARGS="tests/test_calc.py -q"` -> `404 passed`, `TOTAL 45.93 %`, `FAIL Required test coverage of 96.0% not reached`, exit 2. With `-n0 --no-cov` -> `404 passed in 0.25s`, exit 0. Matches RESULTS:2575-2581 exactly. |
| 9 | Probe (adjacency): a total exactly on the floor passes, one hundredth under fails | VERIFIED | `coverage.results.should_fail_under(96, 96, 2)` -> False; `(95.99, 96, 2)` -> True (run by me). |
| 10 | Probe (concurrency): a lost worker flush (~0.22 pt) cannot turn the gate red with no code change | VERIFIED | Arithmetic on recorded totals: the lowest observed total, C0 at 96.99 %, is the run that already lost the flush, and it sits 0.99 over `fail_under = 96`; a further 0.22 loss on the 97.21 % runs gives 96.99 %, still over. The flush loss is filed as debt (`2026-10-04-worker-coverage-flush-is-sometimes-lost.md`, nice, trigger named, INDEX row 21). |
| 11 | Probe (ordering): the combined coverage total does not depend on data-file write/combine order (`verification: backstop`) | UNCERTAIN (insufficient_spec) | Abstained per the non-inferable rule. Observed behaviour is equal totals across runs (97.21 % x3 at -n 8, x2 more in 15-04, 97.29 % on CI at -n 4), but file-write order was never varied on purpose and presence+wiring never qualifies. See Human Verification 1. |
| 12 | Probe (boundary/adjacency/ordering): the constraint fails closed; CI's print line reads exactly the fixture's strings; every pip call runs under the constraint | VERIFIED | Fail-closed reproduced (above). Print line is `cadquery 2.8.0 cadquery-ocp 7.9.3.1.1`, byte-equal to the provenance strings. `PIP_CONSTRAINT` is an env var on the step, so pip's self-upgrade and the `$(STAMP)` editable install inside `make verify` both read it; `Makefile` `$(STAMP)` recipe untouched (the Makefile diff is a single hunk at lines 67-90). |
| 13 | The tripwire `test_the_fixture_was_captured_on_the_kernel_this_run_uses` stays, assertion unchanged, docstring names where the pin lives (D-15); `pre_v0_2.json` not edited | VERIFIED | `tests/regression/test_pre_v0_2.py:80-96`; the diff is docstring-only (+7/-1). I ran it with `tests/test_pr_land.py`: `59 passed` (so `required-jobs.txt` and `ci.yml` still agree; `required-jobs.txt` is byte-identical to `20cd484`). |
| 14 | L34 is one append-only entry amending L12 and L13, every number cited to RESULTS or a SUMMARY | VERIFIED | `git diff --numstat 20cd484 -- docs/architecture/decision_log.md` = `133 0` (no deletion). L34 figures spot-checked against RESULTS: 224.28, 130.72/84.76/68.93/75.47, 3.51, 63.555, 165.435, 96.40, 203.16, 1,069/294/13.63. |
| 15 | No eleven-second claim about the gate remains outside the decision log and `.planning/`; the measured figure sits at every corrected site | VERIFIED | Grep for `~11`/`11 s`/`11s warm` across the tree (excluding `.git`, `.venv`, `milestones`) finds only `decision_log.md:121` (L13, append-only, corrected by L34) and `.planning/` files. README, HOW_TO_DEVELOP, packaging.md, the commit-timeout debt file and `.pre-commit-config.yaml` carry the figure (~64 s; 63.555 s in the hook comment). |
| 16 | End state: fixture byte-unchanged, `src/` unchanged, 927 tests, planning-record sentences corrected | VERIFIED | `git diff --quiet 20cd484 -- src tests/regression/pre_v0_2.json requirements.txt` exits 0 (run by me). REQUIREMENTS.md REQ-verify-at-the-bar / REQ-coverage-floor / REQ-ci-installs-the-pinned-kernel and ROADMAP SC2/SC3/SC4 read "profile checkpoint", `fail_under`, and D-13's `PIP_CONSTRAINT` mechanism. `make lint typecheck lint-imports no-fake-done` clean at HEAD (5 contracts kept, 0 broken). |

**Score:** 15/16 truths verified; 1 UNCERTAIN (insufficient_spec, routed to human); 0 PRESENT_BEHAVIOR_UNVERIFIED.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `bench/RESULTS.md` Phase 15 section | host state, method, per-stage, per-file, slowest 25, sweep, coverage baseline, tolerance/cost, floor, red run, heaviest, cuts, gate decision, before/after, CI run | VERIFIED | 16 subsections present at lines 2200-2815; no estimate: each row carries load, HEAD, wall, RSS, exit. |
| `pyproject.toml` | two dev extras; coverage run/report config | VERIFIED | Substantive and wired: `make test` consumes it; CI run read `fail_under = 96`. |
| `Makefile` | `PYTEST_WORKERS`, `-n`, `--cov` in `test` | VERIFIED | Wired through `verify`; CI and my partial-run checks used it. |
| `.gitignore` | `.coverage`, `.coverage.*` | VERIFIED | lines 28-29. `git status` shows nothing but `.planning/milestone.lock`. |
| `.github/workflows/ci.yml` | `PIP_CONSTRAINT`, print step, comment | VERIFIED | Ran green on PR #18. |
| `.pre-commit-config.yaml` | measured warm time | VERIFIED | 63.555 s with section and date named. |
| `docs/architecture/decision_log.md` L34 | amends L12, L13 | VERIFIED | Appended after L33, no deletions. |
| Two retired debt files + INDEX | resolved, sha | VERIFIED | See SC5. |
| `docs/ideas/2026-10-03-constrain-make-venv-to-the-closure.md` + INDEX row | D-14's idea | VERIFIED | in the diff stat. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `Makefile` `PYTEST_WORKERS` | RESULTS sweep + Gate decision | comment cites both; literal is the human's N | WIRED | N=8 in Makefile, sweep knee K=8, addendum N=8. |
| `pyproject.toml` `fail_under` | RESULTS Coverage floor | L, S recompute to the literal | WIRED | floor(96.99 - 0.25) = 96. |
| `make test --cov` | `fail_under` | no `--cov-fail-under` on the command line | WIRED | I observed `Required test coverage of 96.0%` in the output with no flag passed. |
| `ci.yml` `PIP_CONSTRAINT` | `$(STAMP)` `pip install -e '.[dev]'` | env var read by every pip call in the step | WIRED | CI log shows the pair; dry-run reproduces. |
| debt file `Resolved in` | CI run + `839dfea` | URL and sha both cited | WIRED | `gh run view` confirms the run's head is `839dfea`. |
| `.pre-commit-config.yaml` comment | RESULTS Before and after | mean(B) | WIRED | 63.555 matches. |
| L34 | RESULTS subsections and the debt run URL | figures | WIRED | spot-checked. |

### Data-Flow Trace (Level 4)

Not applicable: the phase renders no dynamic data. The only "data" is measured numbers, traced in the previous table from raw run rows to every prose site that quotes them.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Partial run goes red on the floor | `make test PYTEST_ARGS="tests/test_calc.py -q"` | 404 passed, 45.93 %, FAIL, exit 2 | PASS |
| `--no-cov` hatch exits 0 | `make test PYTEST_ARGS="tests/test_calc.py -q -n0 --no-cov"` | 404 passed, exit 0 | PASS |
| Worker lines counted | `make test PYTEST_ARGS="tests/test_pool.py -q -n0 --cov-report=term-missing"` | 16 passed; `pool.py 54 0 6 0 100.00 %` (the run's own total is low and fails the floor, as expected for one file) | PASS |
| Floor boundary | `should_fail_under(96,96,2)`, `(95.99,96,2)` | False, True | PASS |
| Kernel pair resolves under the closure | `PIP_CONSTRAINT=requirements.txt pip install --dry-run --ignore-installed -e '.[dev]'` | cadquery 2.8.0, cadquery-ocp 7.9.3.1.1 | PASS |
| Constraint fails closed | same with a scratch copy at `cadquery-ocp==8.0.1.0.0` | `ResolutionImpossible` | PASS |
| Tripwire + merge-gate drift test | `pytest tests/regression/...kernel_this_run_uses tests/test_pr_land.py` | 59 passed | PASS |
| Cheap gate stages | `make lint typecheck lint-imports no-fake-done` | clean; 5 contracts kept | PASS |

I did not re-run the full gate or re-measure any wall time: measured numbers were verified against `bench/RESULTS.md` and the SUMMARYs that cite them, as instructed. The orchestrator's `make test` result at HEAD (927 passed, 8/8 workers, 97.21 % against 96) was relied on, not re-run. `pgrep -fl '[p]ytest|[p]re_commit|[m]ake verify'` printed nothing before every pytest-running command.

### Probe Execution

No `scripts/*/tests/probe-*.sh` is declared by any PLAN, and none is conventional here. Step 7c: SKIPPED (no declared probes).

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|--------------|-------------|--------|----------|
| REQ-verify-profiled | 15-01, 15-02, 15-04, 15-06 | per-stage wall, per-file and top-N durations, heaviest named, xdist tolerance measured, bar set at the checkpoint | SATISFIED | SC1, SC2 rows; REQUIREMENTS.md marks `[x]`, traceability "Complete" |
| REQ-verify-at-the-bar | 15-01, 15-04, 15-06 | mean(B) at or under the human's bar; nothing cut; `[dev]`-only deps; hook comment corrected | SATISFIED | 63.555 s <= 66 s; cuts none; `requirements.txt` byte-identical; hook comment corrected |
| REQ-coverage-floor | 15-01, 15-02, 15-06 | `pytest-cov` in dev, baseline, `fail_under`, `--cov` in make test, red-run recorded, debt retired, worker ASSUMPTION settled | SATISFIED | SC3 row |
| REQ-ci-installs-the-pinned-kernel | 15-05, 15-06 | CI resolves the pair; green run URL; Lxx; tripwire kept; where-the-pin-lives stated; debt retired | SATISFIED | SC4 row; mechanism is D-13's, which REQUIREMENTS.md now names in place of the two originally listed options |

Orphaned requirements: none. REQUIREMENTS.md maps exactly these four IDs to Phase 15 (traceability table lines 222-225), and every one appears in at least one PLAN's `requirements:` frontmatter (15-06 lists all four).

### Prohibitions (ADR-550 D3/D4)

All fourteen are observed to hold at HEAD by the verifier's own commands, but none has wired, standing enforcement, so each is reported as flagged `unverified-prohibition` per the fail-closed default. No violation was found.

| Plan | Prohibition | Tier | Observed at HEAD |
|------|-------------|------|------------------|
| 15-01 | Not re-run a red/slow/loaded run to replace its reading | judgment | No red run exists; C0's lossy reading stayed as measured (RESULTS:2485-2488); runs appear in order run. LLM-judge: holds (non-authoritative). |
| 15-01 | No package in `requirements.txt` / `[project] dependencies` | test | `git diff --quiet 20cd484 -- requirements.txt` exits 0; extras only in `dev`. |
| 15-01 | No `-n`/`--cov`/`--durations` in `addopts` | test | `addopts` unchanged. |
| 15-02 | No `pragma: no cover`, narrowed `source`, or `omit` to lift the total | test | grep over `src` and `pyproject.toml`: none; `source = ["src/spur"]` unchanged. |
| 15-02 | Scratch red-on-the-floor state not committed | test | `git log -S'--ignore=tests/test_cli.py'` empty; working tree clean. |
| 15-02 | No test restating the `fail_under` literal | judgment | `grep -rn fail_under tests` empty. |
| 15-03 | Nothing written before the human's answer | test | `0a74eed` touches RESULTS only; no Makefile/pyproject/tests change in the 15-03 commits. |
| 15-03 | No estimate-priced cuts; no tier the hook skips and CI runs | judgment | Proposed-cuts rows are priced from P1/P2 duration lines; text states no `mark`/tier rows. |
| 15-04 | No test removed, skipped, marked or sampled without by-name acceptance | test | `git diff 20cd484 HEAD -- tests` is one docstring; the human refused all 15 by name. |
| 15-04 | No rerun plugin, no re-run to green, no bar change | judgment | `dev` extras hold no rerun plugin; bar 66 unchanged from the addendum; no run repeated. |
| 15-05 | No edit to fixture, `requirements.txt`, `cadquery>=2.5`, `$(STAMP)` | test | all unchanged (`pyproject.toml:13` still `cadquery>=2.5`). |
| 15-05 | No force-push, no second PR, no re-run of CI | judgment | PR timeline shows only `committed` events; exactly one PR (#18) for the branch; summary and RESULTS say "not re-run". |
| 15-06 | No edit to L12, L13 or earlier entries | test | numstat `133 0`. |
| 15-06 | No number in L34 or at corrected sites that is not in RESULTS or a 15-0x SUMMARY | test | spot-checked (see truth 14). The hook-timing figure "63-64 s by `date`" is from `15-04-SUMMARY.md`, as L34 says. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (phase-modified code files) | - | `TBD`/`FIXME`/`XXX`/`TODO`/`HACK` | none | Scanned the added lines of `Makefile`, `pyproject.toml`, `ci.yml`, `.pre-commit-config.yaml`, `.gitignore`, `test_pre_v0_2.py`: no marker. |

No stubs: the phase has no rendering code. Empty-implementation patterns do not apply to config and prose changes.

### Advisory and informational items (not gaps)

- `.planning/PROJECT.md:403` still says "~11s warm", and its L12/L13 Outcome columns are not updated. D-19 assigns both to the phase transition, and 15-06's own truth exempts `.planning/`. The orchestrator owes these at transition.
- `.planning/ROADMAP.md` still shows the Phase 15 checkbox unticked and the progress row "In Progress" while 6/6 plans are executed. Transition bookkeeping, not a phase defect.
- `.planning/codebase/TESTING.md` is stale ("Warm run ~11 seconds", "Coverage measurement in place"). D-19 and `<deferred>` leave it to `/gsd-map-codebase`.
- The CI proof cannot show whether the constraint or cadquery 2.8.0's own `cadquery-ocp<8.0` cap held the pair on that run; RESULTS says so openly, and my local dry-run is what demonstrates the constraint fails closed. This is not a coincidental-reliance flag: the precondition is declared and the fail-closed behaviour is demonstrated independently of the CI run.
- Locally the serial `--cov` gate can read 96.99 % instead of 97.21 % when BuildPool's worker flush is lost; the floor (96) clears it and the debt file carries a trigger. Eight full `--cov` runs are tallied in RESULTS:2761-2768.

## Human Verification Required

### 1. The `backstop` truth: coverage total independent of combine order

**Test:** Decide whether the recorded observation is enough, or require a deliberate order-varied check (for example combining the same set of `.coverage.*` files in shuffled order and comparing totals).
**Expected:** Identical totals either way. Recorded so far: 97.21 % on five `-n 8 --cov` runs, 97.29 % on CI at `-n 4`; the 96.99 % reads are the separately-tracked flush loss.
**Why human:** The plan tagged this truth `backstop` (non-inferable); the verifier abstains absent a wired held-out test or an experiment that varied the order.

### 2. The flagged prohibitions

**Test:** Skim the Prohibitions table and the commands behind each row (all re-runnable in seconds: `git diff --quiet 20cd484 -- requirements.txt tests/regression/pre_v0_2.json src`, `git diff --numstat 20cd484 -- docs/architecture/decision_log.md`, `grep -rn fail_under tests`, `git diff 20cd484 HEAD --stat -- tests`).
**Expected:** Each negative holds, as observed above. Accept "complete with 14 flagged prohibitions", or ask for a wired check on any you want kept as standing protection.
**Why human:** ADR-550 D4/D5d fail-closed: no wired enforcement means flagged, never silently green.

## Gaps Summary

No gaps. The phase goal is achieved: the gate's wall time (224.28 s serial profile; 63.555 s as committed at `-n 8` with coverage), the bar (66 s, set by the human, met), and the coverage floor (96, from a 96.99 % baseline) are all numbers in `bench/RESULTS.md`, and CI resolves and prints `cadquery 2.8.0 cadquery-ocp 7.9.3.1.1` under a constraint that I confirmed fails closed. The fixture, `src/` and `requirements.txt` are byte-unchanged against `20cd484`. The only open items are the two human-verification entries above.

---

_Verified: 2026-10-04_
_Verifier: Claude (gsd-verifier)_
