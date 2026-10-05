---
phase: 15-the-gate-measured-and-pinned
plan: 05
subsystem: ci
tags: [ci, pip-constraints, requirements-txt, kernel-pin, draft-pr, tech-debt]

requires:
  - phase: 15-the-gate-measured-and-pinned
    provides: "15-04's Makefile PYTEST_WORKERS (8 clamped to the host's CPUs) and --cov gate, so the same CI run also shows xdist's worker count and the coverage total on a 4-vCPU runner"
provides:
  - ".github/workflows/ci.yml: PIP_CONSTRAINT=requirements.txt on the make verify step, the always-run step that prints the resolved kernel pair, the where-the-pin-lives comment"
  - "tests/regression/test_pre_v0_2.py: the tripwire's docstring names requirements.txt, PIP_CONSTRAINT, docker/refresh-requirements.sh and make fixture.regen; body unchanged"
  - "Draft PR #18 for the phase branch; CI run 37181871926, green, pair cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1"
  - "bench/RESULTS.md ### CI run; the 2026-09-26 CI-kernel debt retired; D-13's mechanism in REQ-ci-installs-the-pinned-kernel and ROADMAP SC4"
affects: [15-06]

actuals:
  tokens: 2565
  tasks: 3
  commits: 2
plan_head_before: a5c9365ae8594318c68bf62d494b346c981c37b2
plan_head_after: 454af540179061754e32e08108bdc30ff4b525b7

tech-stack:
  added: []
  patterns:
    - "pip constraints through the PIP_CONSTRAINT env var on the one CI step that installs: a relative path works because make runs in the repo root, and the same variable reaches the pip self-upgrade and the editable install inside the venv recipe"
    - "a print step with if: always() after the step that creates .venv states the resolved pair in the log of a red run too"

key-files:
  created:
    - docs/tech_debt/resolved/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md
  modified:
    - .github/workflows/ci.yml
    - tests/regression/test_pre_v0_2.py
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md

key-decisions:
  - "The pin is PIP_CONSTRAINT: requirements.txt as step-level env on make verify (D-13): no separate pip step, no job-level name, matrix and required-jobs.txt unchanged"
  - "The print step sits after make verify with if: always() (D-16 left placement to the planner): .venv exists only once make verify has made it"
  - "The draft PR is updated at ship, not re-created: gh pr edit and gh pr ready, because /gsd-ship's gh pr create would refuse a second PR for the branch"

requirements-completed: [REQ-ci-installs-the-pinned-kernel]

coverage:
  - id: D1
    description: "CI's make verify installs under the L12 closure: PIP_CONSTRAINT: requirements.txt on the step, the pair printed by the always-run step after it, the pin's whereabouts written in the ci.yml comment and the tripwire's docstring"
    requirement: REQ-ci-installs-the-pinned-kernel
    verification:
      - kind: other
        ref: "Task 1 automated checks -> 'ci.yml ok', 'docstring only', 'pin scope ok'; tests/test_pr_land.py and the tripwire test: 59 passed"
        status: pass
      - kind: other
        ref: "dry run PIP_CONSTRAINT=requirements.txt pip install --dry-run -e '.[dev]' -> 'pair resolves under the constraint'; scratch constraint cadquery-ocp==8.0.1.0.0 -> 'fails closed' (ResolutionImpossible)"
        status: pass
    human_judgment: false
  - id: D2
    description: "One green CI run on the pin's head whose log shows the pair, 4 xdist workers and a clean pytest line (SC4's proof, SC5's run)"
    requirement: REQ-ci-installs-the-pinned-kernel
    verification:
      - kind: integration
        ref: "gh run view 37181871926 -> conclusion success, headSha 839dfea, test (3.12)/image/vendor-bundle success; log: 'cadquery 2.8.0 cadquery-ocp 7.9.3.1.1', 'created: 4/4 workers', '927 passed in 203.16s'"
        status: pass
    human_judgment: false
  - id: D3
    description: "The CI-kernel debt retired with the pin's sha and the run URL; INDEX row moved; D-13's sentences in the REQ and SC4; ROADMAP milestone scope identical before and after"
    requirement: REQ-ci-installs-the-pinned-kernel
    verification:
      - kind: other
        ref: "Task 3 automated checks -> 'debt ok 839dfea', 'D-13 sentences ok', 'D-20 ok'; cmp of roadmap milestone-scope before/after -> identical"
        status: pass
    human_judgment: false
  - id: D4
    description: "Whether one run shows the constraint, rather than cadquery 2.8.0's own cadquery-ocp<8.0 cap, holding the pair"
    requirement: REQ-ci-installs-the-pinned-kernel
    verification: []
    human_judgment: true
    rationale: "Both give 7.9.3.1.1 today, so the green run cannot tell them apart; the evidence that the constraint fails closed is the local dry run with a conflicting scratch constraint, which no CI assertion repeats"

duration: 10min
completed: 2026-10-04
status: complete
---

# Phase 15 Plan 05: Pin CI to the Fixture's Kernel, Draft PR and One Green Run Summary

**CI's `make verify` now installs under `PIP_CONSTRAINT: requirements.txt` (the L12 closure) and prints the resolved pair; run 37181871926 on draft PR #18 printed `cadquery 2.8.0 cadquery-ocp 7.9.3.1.1`, created 4/4 xdist workers and passed 927 tests, and the CI-kernel debt retired citing `839dfea` and that run.**

## Performance

- **Duration:** 10 min (most of it the CI run: the `test (3.12)` job took 267 s)
- **Started:** 2026-10-04T06:05:01Z
- **Completed:** 2026-10-04T06:15:00Z (approximate; the closing commit follows this file)
- **Tasks:** 3
- **Files modified:** 8 (and one `git mv` of the debt file)

## The answer Task 2 acted on

15-CONTEXT.md D-16 addendum (2026-10-03, the human's answer at plan-phase): "Mechanism: **`draft-pr`** -- 15-05 opens the phase PR as a draft at its push (`gh pr create --draft`) and reads the run URL from that PR's checks; at ship, `/gsd-ship`'s `gh pr create` would refuse a second PR, so the draft is updated with `gh pr edit` and marked ready with `gh pr ready` instead." No checkpoint was presented.

## The pull request and the run

- **PR:** #18, https://github.com/halfb00t/spur/pull/18, a draft against `main`, titled "Phase 15: The Gate, Measured and Pinned", body with no CI skip token (checked through `scripts.skip_tokens.find_skip_tokens`) and ending with the Claude Code attribution line. One PR exists for the branch.
- **Push:** one plain `git push -u origin gsd/phase-15-the-gate-measured-and-pinned` of HEAD `839dfea` (the branch was not on origin and had no PR; checked read-only first). No force, nothing pushed to `main`. The closing commits are pushed after this SUMMARY so the draft's head matches local HEAD.
- **Run:** https://github.com/halfb00t/spur/actions/runs/37181871926, event `pull_request`, head `839dfeaa33d60c1c996c9d7c111190a1dcca4cbc`, conclusion `success`; `test (3.12)`, `image` and `vendor-bundle` all `success`. Not re-run.
- **What the log printed:** the step `kernel pair this run resolved` -> `cadquery 2.8.0 cadquery-ocp 7.9.3.1.1`; pip's install line in the `make verify` step -> `cadquery-2.8.0 cadquery-ocp-7.9.3.1.1 cadquery-ocp-proxy-7.9.3.1.1`, `pytest-cov-7.1.0`, `pytest-xdist-3.8.0`, with setup-python's pip cache a hit (RESEARCH Pitfall 14 again: pip's output named the pair on a cache hit); `created: 4/4 workers` and `4 workers [927 items]` (the `-n 8` clamp read 4 online CPUs); `927 passed in 203.16s (0:03:23)`; `TOTAL 1069 22 294 15 97.29%` against `fail_under = 96`, no lost worker flush this time.
- **CI `test (3.12)` job wall time:** 06:07:19Z to 06:11:46Z = 267 s, context on a 4-vCPU runner and never the bar (D-02).

## Task Commits

1. **Task 1: constrain CI's install to requirements.txt, the kernel pair the fixture pins** - `839dfea` (ci)
2. **Task 2: push the branch, open the draft PR, wait for the run** - no commit (push of `839dfea`; PR #18; run 37181871926)
3. **Task 3: record the run, retire the CI-kernel debt** - `454af54` (docs)

**Plan metadata:** the closing `docs(15-05): name D-13's mechanism in REQ-ci-installs-the-pinned-kernel and SC4` commit (this SUMMARY, REQUIREMENTS.md, ROADMAP.md, STATE.md). Frontmatter `commits: 2` is measured from the plan ledger (`a5c9365..454af54`) and counts the two task commits, not the closing commit.

## Dry-run results (Task 1, before anything was pushed)

- Under `PIP_CONSTRAINT=requirements.txt`, `pip install --dry-run --ignore-installed --report -e '.[dev]'` resolved 87 packages: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1, pytest-xdist 3.8.0, pytest-cov 7.1.0. The dev extras do not conflict with the constraint file.
- The same dry run against a scratch copy of requirements.txt with `cadquery-ocp==8.0.1.0.0` failed with `ResolutionImpossible` ("conflicting dependencies"): the constraint fails closed.
- `tests/test_pr_land.py` and the tripwire test: 59 passed. The pre-commit hook then ran `make verify` green on the pin commit.
- `tests/regression/pre_v0_2.json`, `requirements.txt`, `required-jobs.txt`, the `cadquery>=2.5` range, `$(STAMP)` and `src/` are byte-identical to `20cd484`.

## Accomplishments

- `.github/workflows/ci.yml`: `env: PIP_CONSTRAINT: requirements.txt` on the `make verify PYTHON=python` step, a comment above it naming `requirements.txt`, `docker/refresh-requirements.sh`, `make fixture.regen` and the tripwire (L34), and a step `kernel pair this run resolved` (`if: always()`) that prints the pair from `.venv`.
- `tests/regression/test_pre_v0_2.py`: the tripwire's docstring says where the pin lives; assertion and message unchanged.
- `bench/RESULTS.md ### CI run`; `docs/tech_debt/resolved/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md` (Status resolved, `Resolved in: 839dfea -- proven by CI run ...`, a Resolution), INDEX row moved to Resolved.
- `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md` SC4 name D-13's mechanism; one Roadmap Evolution line added; `roadmap milestone-scope` identical before and after (complete, phases 13 to 16).

## Files Created/Modified

- `.github/workflows/ci.yml`, `tests/regression/test_pre_v0_2.py` - the pin and its documentation
- `bench/RESULTS.md` - `### CI run`; one cross-reference reworded in 15-04's last paragraph (see Deviations)
- `docs/tech_debt/resolved/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md`, `docs/tech_debt/INDEX.md` - debt retired
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md` - D-13's sentences, position, metrics

## Decisions Made

- PIP_CONSTRAINT as step-level env rather than `-c` on a separate install step (D-13's choice of form was the planner's): a separate pip step would install into the runner's Python, not `.venv` (RESEARCH Pitfall 8), and the env var reaches both pip calls inside `$(STAMP)`.
- The pair line is read from `.venv` after `make verify`, with `if: always()`, so a red gate still states the pair.
- At ship, PR #18 is updated, not re-created (see below).

## Deviations from Plan

**1. [Rule 3 - Blocking] A plan verify command tripped on 15-04's prose mention of the heading**
- **Found during:** Task 3
- **Issue:** Task 3's first automated check splits the Phase 15 section on the text `### CI run` and takes `[1]`. 15-04's last paragraph in `### Before and after` named "15-05's `### CI run`" inline, so `[1]` was the text after that mention, which holds no run URL and made the check raise.
- **Fix:** reworded that one phrase to "15-05's CI-run subsection, below". The two verify commands then read the real section.
- **Files modified:** bench/RESULTS.md
- **Committed in:** `454af54`

**2. [Process] The PR body went in through `--body-file`, not `--body`**
- **Found during:** Task 2
- **Issue:** the plan's text says the body sits in a double-quoted shell argument; the orchestrator also asked for the attribution line to end the body, and a file keeps the line and the emoji out of shell quoting.
- **Fix:** body written to the session scratchpad and passed with `--body-file`; same words as the plan, plus the attribution line.
- **Files modified:** none in the repo

---

**Total deviations:** 2 (1 Rule 3 wording fix, 1 process note)
**Impact on plan:** none on the outcome.

## Issues Encountered

None. The run was green on the first and only run; nothing was re-run.

## Known Stubs

None (config, tests' docstring and records only).

## Threat Flags

None. The only new surface is the `PIP_CONSTRAINT` env var and a print step in CI; no new endpoint, auth path or file access. T-15-12 (a constraints file without hashes) stands as accepted: the closure carries no hashes, the same as the image's install (L12).

## User Setup Required

None.

## Next Phase Readiness

For 15-06 and for `/gsd-ship`:

- **L34 cites run 37181871926** (https://github.com/halfb00t/spur/actions/runs/37181871926) and the pin commit `839dfea`. L34 should also say what D-16 got wrong: pip's install output is not "absent on a cache hit" in this workflow (run 37116412012 and this run both hit the cache and printed the pair), so the print step is the cheaper proof, not the only one. It logs the choice against L12's "why floors and ranges" rationale and names the idea file for the unconstrained local `make venv` (`docs/ideas/2026-10-03-constrain-make-venv-to-the-closure.md`, D-14).
- **For /gsd-ship:** PR #18 exists as a draft -- update its title and body with `gh pr edit` and mark it ready with `gh pr ready` instead of `gh pr create`, which would refuse a second PR for this branch (15-CONTEXT.md D-16 addendum). Landing is the human's `make pr.land PR=18`. The "~11 s" sites and the measured number (mean(B) 63.555 s) are 15-04's note for 15-06; CI's 203.16 s `-n 4` pytest time is context only.
- 15-06's prose must not claim the CI run measured the bar: it ran on 4 vCPUs at `-n 4`.
- The debt file `2026-10-04-worker-coverage-flush-is-sometimes-lost.md` can take one more datum: this CI run at `-n 4 --cov` read `TOTAL ... 97.29%` (22 statements missed, vs 23 at `-n 8` on the dev host); the platform differs, so it is a row, not a cause.

## Self-Check: PASSED

- Files FOUND: `.github/workflows/ci.yml`, `tests/regression/test_pre_v0_2.py`, `bench/RESULTS.md`, `docs/tech_debt/resolved/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md`, this SUMMARY; the active/ copy is gone
- Commits FOUND: `839dfea`, `454af54` (`git rev-list --count a5c9365..HEAD` was 2 before this SUMMARY)
- Re-run: Task 1 checks -> `ci.yml ok`, `docstring only`, `pair resolves under the constraint`, `fails closed`, `pin scope ok`; Task 2 checks -> `one draft PR at HEAD 18`, `the run on HEAD has ended`; Task 3 checks -> run conclusion success and the pair line count 1, the clean pytest line count 1, `debt ok 839dfea`, `D-13 sentences ok`, `D-20 ok`
- Run 37181871926 re-read from GitHub with `gh run view`: conclusion `success`, head `839dfea`
- `git diff --quiet 20cd484 -- src tests/regression/pre_v0_2.json requirements.txt .github/workflows/required-jobs.txt` exits 0

---
*Phase: 15-the-gate-measured-and-pinned*
*Completed: 2026-10-04*
