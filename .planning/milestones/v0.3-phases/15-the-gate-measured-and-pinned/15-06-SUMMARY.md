---
phase: 15-the-gate-measured-and-pinned
plan: 06
subsystem: docs
tags: [decision-log, L34, gate-wall-time, end-state, amends-L12-L13]
requires:
  - phase: 15-the-gate-measured-and-pinned
    provides: "15-04's mean(B) 63.555 s against the 66 s bar; 15-05's pin, run 37181871926 and the D-16 correction; 15-01 to 15-03's profile, sweep, floor and the human's D-01 answer"
provides:
  - "mean(B) 63.555 s, written as ~64 s where a site says ~, at .pre-commit-config.yaml, README.md, docs/HOW_TO_DEVELOP.md, docs/architecture/packaging.md and the commit-timeout debt file; no eleven-second claim left outside the decision log and .planning/"
  - "docs/architecture/decision_log.md L34 (amends L12 and L13), appended after L33: the measured gate, the floor, the pin, Reversibility, Reason, Machine"
  - "the phase's end state confirmed: make verify green under its own floor and workers, fixture/src/closure byte-identical to 20cd484, both Phase 15 debts in resolved/, 927 tests collected"
affects: [phase-15-transition, gsd-ship]

actuals:
  tokens: 3225
  tasks: 3
  commits: 2
plan_head_before: 2e85bdbd5e67674732a41c00a7e8672bb050b7d6
plan_head_after: 298677ae8ecd35e39fb058d737701ebaf9288b38

tech-stack:
  added: []
  patterns:
    - "a figure written into prose carries its configuration (-n 8 with coverage, 12-core dev host) and its RESULTS section; the whole-commit hook figure is labelled as the whole commit"
    - "an amending decision-log entry is verified append-only by numstat against the phase's base commit (0 deleted lines)"

key-files:
  created: []
  modified:
    - .pre-commit-config.yaml
    - README.md
    - docs/HOW_TO_DEVELOP.md
    - docs/architecture/packaging.md
    - docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md
    - docs/architecture/decision_log.md

key-decisions:
  - "The one headline figure is mean(B) 63.555 s (the gate as committed, -n 8 with coverage, 12-core M2 Max), written as ~64 s where a site says ~ and as 63.555 s with its section in the hook comment"
  - "L34 is one entry in L31-L33's shape; every seconds figure in it appears in bench/RESULTS.md's Phase 15 section; D-16's 'absent on a cache hit' is corrected in it"
  - "The commit-timeout debt stays active (upstream gsd's 30 s timeout is unchanged); its numbers are corrected and one sentence says a warm commit is itself past the limit now"

requirements-completed: [REQ-verify-at-the-bar, REQ-verify-profiled, REQ-coverage-floor, REQ-ci-installs-the-pinned-kernel]

coverage:
  - id: D1
    description: "Every site that said ~11 s now states the measured gate time with its configuration: .pre-commit-config.yaml carries 63.555 s and names the Before and after section and date; README, HOW_TO_DEVELOP (Russian) and packaging.md carry ~64; the debt file carries ~64 s warm twice and stays active"
    requirement: REQ-verify-at-the-bar
    verification:
      - kind: other
        ref: "Task 1 automated checks -> 'no eleven-second claim left', 'measured figure at every site: 63.555', one commit ad99df9 touching exactly the five files"
        status: pass
    human_judgment: false
  - id: D2
    description: "L34 appended after L33, amending L12 and L13, 0 deleted lines against 20cd484, every seconds figure traceable to RESULTS, the run URL, the shas and the bar cited"
    requirement: REQ-verify-profiled
    verification:
      - kind: other
        ref: "Task 2 automated checks -> numstat deleted column 0; 'L34 ok'; grep -c '^## L34 ' = 1"
        status: pass
    human_judgment: false
  - id: D3
    description: "The phase's end state: make verify green under its floor and 8 workers; pre_v0_2.json, src/ and requirements.txt unchanged since 20cd484; both Phase 15 debts in resolved/ and once in INDEX Resolved; 927 tests collected"
    requirement: REQ-coverage-floor
    verification:
      - kind: other
        ref: "make verify -> exit 0, '927 passed in 61.08s', 'Required test coverage of 96.0% reached. Total coverage: 97.21%'; git diff --exit-code 20cd484 -- tests/regression/pre_v0_2.json src requirements.txt -> clean; 'ledger ok'; pytest --collect-only -> '927 tests collected'"
        status: pass
    human_judgment: false
  - id: D4
    description: "Whether L34's prose is a fair and complete account of what the phase measured and decided, including how it words the unproven (the constraint-versus-cap reading, the lost worker flush)"
    requirement: REQ-ci-installs-the-pinned-kernel
    verification: []
    human_judgment: true
    rationale: "The decision log is what later phases read as locked fact; the verify checks that figures, shas and the URL match their sources, not that the paragraphs weigh the evidence fairly"

duration: 8min
completed: 2026-10-04
status: complete
---

# Phase 15 Plan 06: The Record, L34 and the Corrected Sites Summary

**Every place the tree said the gate takes ~11 s now says what Phase 15 measured (mean(B) 63.555 s at `-n 8` with coverage, ~64 s), L34 amends L12 and L13 with the profile, the bar read, the floor and the CI pin, and the phase ends green: `make verify` under its 96 % floor on 8 workers, fixture, `src/` and closure untouched since `20cd484`.**

## Performance

- **Duration:** 8 min (the two prose commits each ran the ~64 s hook)
- **Started:** 2026-10-04T06:19:00Z (approximate)
- **Completed:** 2026-10-04T06:28:00Z (approximate; the closing commit follows this file)
- **Tasks:** 3
- **Files modified:** 6 (and this SUMMARY)

## The headline number

mean(B) = **63.555 s**: 15-04's two `-n 8 --cov` runs (B1 64.19 s, B2 62.92 s) of the gate as committed, on the 12-core M2 Max dev host, against a serial `--cov` mean(A) of 228.99 s and the human's 66 s bar (`bench/RESULTS.md` § "Before and after", `b8b4dd1`). It replaces "~11 s warm". Written as `63.555 s` with section and date in the hook comment, and as `~64 s` at the other sites (the plan's rounding rule: nearest whole second where a site says "~"). The no-coverage serial 224.28 s is the pre-phase profile and appears only in L34's account of the start. The 63-64 s per commit that `date` read around 15-04's commits is the whole commit (hook plus commit-msg) and is labelled so; it is context, not the bar.

## Task Commits

1. **Task 1: state the gate's measured wall time where the tree said eleven seconds** - `ad99df9` (docs)
2. **Task 2: log L34 -- the gate measured, floored and pinned** - `298677a` (docs)
3. **Task 3: confirm the end state** - no commit (checks only, recorded below)

**Plan metadata:** the closing `docs(15-06): record Phase 15's end state` commit (this SUMMARY, STATE.md, ROADMAP.md, REQUIREMENTS.md). `commits: 2` is measured from the plan ledger (`2e85bdb..298677a`) and counts the two task commits, not the closing commit.

## Figure written at each site

| Site | Now says |
|---|---|
| `.pre-commit-config.yaml` (comment) | `A warm run measured 63.555 s (`-n 8` with coverage, mean of two runs) on the 12-core M2 Max dev host: bench/RESULTS.md, "The gate, measured and pinned (Phase 15)", section "Before and after", 2026-10-04.` then "The CAD tests dominate it (tests/test_model.py is about three quarters of pytest's seconds, section "Per-file share")"; the cold-run sentence, both hooks and `stages: [pre-commit]` unchanged |
| `README.md` (sh block) | `(~64 s warm on a 12-core dev host, no Docker)` |
| `docs/HOW_TO_DEVELOP.md` section 0 (Russian) | `~64 с на прогретом кеше (12-ядерный dev-хост, `bench/RESULTS.md`, фаза 15).` |
| `docs/architecture/packaging.md` gate table | `(~64 s warm, no Docker)`, column alignment kept (same width as `~11 s`) |
| commit-timeout debt, "Related files" line | `~64 s warm` |
| commit-timeout debt, Context | `~64 s warm (`-n 8` with coverage, bench/RESULTS.md, Phase 15)`; `Status: active` unchanged |

## End-state checks (Task 3), each with what it printed

- `make verify` (Bash timeout 600000 ms, HEAD `298677a`): exit 0; ruff `All checks passed!`; `created: 8/8 workers`; **result line `======================== 927 passed in 61.08s (0:01:01) ========================`**; `TOTAL 1069 23 294 15 97.21%`; `Required test coverage of 96.0% reached. Total coverage: 97.21%`; `make verify  366.23s user 272.95s system 1033% cpu 1:01.86 total`. One run, load not recorded, context for the figure above and not a bar reading. The same gate also ran as the pre-commit hook on both task commits (`Passed`).
- `git diff --exit-code 20cd484 -- tests/regression/pre_v0_2.json src requirements.txt` -> clean, `part, code and closure unchanged since 20cd484`. `requirements.txt` still has 31 `==` pins.
- `git diff --stat 20cd484 -- tests` -> one file, `tests/regression/test_pre_v0_2.py` (7 insertions, 1 deletion): the 15-05 docstring edit naming the pin. Nothing else in `tests/` differs from `20cd484`.
- Debt ledger: `ledger ok` (neither Phase 15 debt in `active/`; `2026-09-21-no-coverage-floor.md` and `2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md` once each in INDEX's Resolved table, zero times above it).
- `.venv/bin/python -m pytest --collect-only -q | tail -1` -> `927 tests collected in 2.12s`. The count is 927, as 15-04 says no cut changed it; the plan's `fails_when` quotes the line as "927 tests collected" without pytest's timing suffix, which pytest always prints, so the check was read for the count.
- Eleven-second grep outside the decision log and `.planning/`: `no eleven-second claim left`.
- Decision log numstat against `20cd484`: 133 added, **0 deleted**; `grep -c "^## L34 "` = 1; L33 is the entry before it.
- Tree: clean except GSD's untracked `.planning/milestone.lock`, left alone.

Everything the plan asked for held. Nothing failed.

## Accomplishments

- Five prose sites corrected to the measured figure, in their own languages and layouts (D-19).
- L34, `## L34 -- The gate is measured, runs on eight workers under a coverage floor, and CI installs the pinned kernel (amends L12 and L13)`: the profile (P1 230.20 s / P2 218.36 s, mean 224.28 s, pytest 99.8 % of it, `tests/test_model.py` 74 % of pytest), the sweep and the pre-registered knee rule (K = 8), D-05's verdict (6 of 6 green), the human's answer verbatim and the bar and N, all 15 cuts refused by name, the reading (mean(B) 63.555 s, bar met by 2.445 s) with L13's claim corrected, Open Questions 3 and 4; the floor (C0 96.99 %, 1,069 statements and 294 branches, `fail_under = 96`, `precision = 2`, worker lines through multiprocessing plus thread, parallel and sigterm and why, the red run at 90.24 %, config-only floor, the filed lost-flush debt); the pin (`PIP_CONSTRAINT`, why neither named option, the run URL and its printed pair, what one run cannot show, the tripwire kept, D-16's cache-hit claim corrected with run 37116412012); Reversibility, Reason, Machine.

## Files Created/Modified

- `.pre-commit-config.yaml`, `README.md`, `docs/HOW_TO_DEVELOP.md`, `docs/architecture/packaging.md`, `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md` - the measured figure
- `docs/architecture/decision_log.md` - L34

## Decisions Made

- One headline figure, mean(B) 63.555 s; rounded to ~64 only where the site says "~".
- The debt file got one sentence beyond a figure swap (see Deviations); L34 says the debt stays active because the hook is ~64 s and gsd's 30 s timeout still kills it.
- L34 does not carry a number the phase did not record: the ~550 MB figure D-13 quotes for the pruned dependencies is left out, and the Machine line reads the dev host's macOS version again (27.0.1 now; L32 and L33 read 27.0).

## Deviations from Plan

**1. [Rule 2 - Missing critical] One sentence added to the commit-timeout debt's Context**
- **Found during:** Task 1
- **Issue:** the plan changes only the figure, but the debt's "Why it matters" says the executor's warm retry works because a retry runs warm. With the hook at ~64 s and the timeout 30 s, a warm run is itself past the limit; leaving the figure alone would print `~64 s warm` beside a claim that a warm retry escapes a 30 s timeout.
- **Fix:** after "each passed the hook.", one sentence citing 15-04-SUMMARY.md's 63-64 s per whole commit by `date`. `Status: active`, Severity, trigger and Next step unchanged; the debt is not retired.
- **Files modified:** docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md
- **Committed in:** `ad99df9`

**2. [Process] Commit trailer**
- The dispatch asked for `Co-Authored-By: Claude Fable 5.1`; the harness's attribution note for this session names `Claude Sonnet 5.5`, the model that wrote these commits. `ad99df9` carries the Fable trailer (written before I compared the two), `298677a` and the closing commit carry the Sonnet one. History already mixes both (`a5c9365`, `ba53d17` Sonnet; `839dfea` to `2e85bdb` Fable).

---

**Total deviations:** 2 (1 Rule 2, 1 process note)
**Impact on plan:** none on the outcome.

## Issues Encountered

None. Both prose commits ran the pre-commit hook (`make verify`, about 64 s each) with plain `git commit`; neither needed a retry.

A discrepancy in an earlier summary, not fixed here: 15-03-SUMMARY.md says "6 `remove` rows in `tests/test_api.py`"; `### Proposed cuts` lists seven (`api-honeycomb-link` to `api-repeat-download`), which with 3 samples, 3 skips and 2 dedups makes the 15 rows. L34 says seven.

## Known Stubs

None (prose and decision-log only).

## Threat Flags

None. No code, endpoint, auth path or schema changed. T-15-15: the decision log's deleted-line count against `20cd484` is 0. T-15-16: every two-decimal seconds figure in L34 is in RESULTS' Phase 15 section; the run URL, the three shas and the bar match their sources.

## User Setup Required

None.

## Notes for the transition (not this plan)

- `.planning/PROJECT.md` "Constraints -> Gate" gets the measured figure (63.555 s, `-n 8` with coverage, 12-core dev host), and its L12 and L13 Key Decisions rows get their Outcome column (D-17, D-19).
- `/gsd-map-codebase` refreshes `.planning/codebase/TESTING.md`, which still carries the old gate claim (a map, not hand-edited, D-19).
- The draft PR #18 is updated at ship with `gh pr edit` and marked ready with `gh pr ready`, not re-created: `/gsd-ship`'s `gh pr create` would refuse a second PR for the branch (D-16 addendum).
- The phase lands through `make pr.land PR=18` and is reviewed by the other CLI (D-21, CLAUDE.md): this diff was written by Claude, so Codex reviews it.
- RESEARCH Open Question 6 is raised to the human, not acted on: PyPI lists cp313 and cp314 wheels for `cadquery-ocp` 7.9.3.1.1, against L23's and AGENTS.md's "nothing newer than 3.12".
- Standing debts that still apply: `docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md` (nice; 15-05 noted one more datum for it, CI's `-n 4 --cov` run read 97.29 % with 22 statements missed, not yet added) and the commit-timeout debt (active, numbers corrected).

## Next Phase Readiness

Phase 15 has six of six plans summarised; the phase is ready for verification and the transition.

## Self-Check: PASSED

- Files FOUND: `.pre-commit-config.yaml`, `README.md`, `docs/HOW_TO_DEVELOP.md`, `docs/architecture/packaging.md`, the commit-timeout debt file, `docs/architecture/decision_log.md`, this SUMMARY
- Commits FOUND: `ad99df9`, `298677a`; `git rev-list --count 2e85bdb..HEAD` was 2 before this SUMMARY
- Re-run: Task 1 -> `no eleven-second claim left`, `measured figure at every site: 63.555`; Task 2 -> numstat deleted `0`, `L34 ok`; Task 3 -> `make verify` exit 0 with `927 passed in 61.08s` and 97.21 % against the floor, `part, code and closure unchanged since 20cd484`, `ledger ok`, `927 tests collected`

---
*Phase: 15-the-gate-measured-and-pinned*
*Completed: 2026-10-04*
