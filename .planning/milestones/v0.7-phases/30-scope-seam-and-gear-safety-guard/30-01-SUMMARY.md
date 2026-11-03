---
phase: 30-scope-seam-and-gear-safety-guard
plan: 01
subsystem: infra
tags: [git, gate, regression, makefile, fastapi-testclient, pytest]

requires:
  - phase: 29-ubuntu-26-final-reading
    provides: the v0.6 tag and the tests/regression/ fixture the check compares against
provides:
  - "make gear.unchanged: one command proving tests/regression/, ci.yml and the /api/schema bytes equal the v0.6 tag"
  - "gear.unchanged as a verify.static prerequisite, so verify and verify.fast both run it"
  - "scratch-repo tests for the check, pinned dry-run proof that both gates run it"
  - "bench/RESULTS.md Phase 30 section: the check's price and nine reds plus the image red"
affects: [30-03, 30-04, 30-05, 32, 33, 34]

plan_head_before: 54f18422f9df3a971a890c1d1aad4a07a479bdb5
plan_head_after: 42c67afe5b3b976b9a08ef7fa546a15241cd7569

actuals:
  tokens: 13600   # chars/4 over `git diff 54f1842 HEAD` of scripts, tests, Makefile, bench, .planning/phases (54504 chars, logs included)
  tasks: 3
  commits: 2      # MEASURED: git rev-list --count 54f18422f9df3a971a890c1d1aad4a07a479bdb5..HEAD, before this SUMMARY's own commit

tech-stack:
  added: []
  patterns:
    - "baseline read from a git tag at run time via git archive into a TemporaryDirectory, never a worktree, because the pre-commit hook exports GIT_INDEX_FILE"
    - "one child interpreter per tree with PYTHONPATH and -P, and an assertion on spur.__file__, so a shadowed editable install cannot compare a tree with itself"

key-files:
  created:
    - scripts/gear_unchanged.py
    - tests/test_gear_unchanged.py
  modified:
    - Makefile
    - tests/test_hooks.py
    - bench/RESULTS.md

key-decisions:
  - "D-04: gear.unchanged is a prerequisite of verify.static, so verify and verify.fast both run it; measured 0.45-0.46 s, and make verify.fast reads 10.01 s against L36's 30 s budget"
  - "The fetch of a missing tag is depth 1 only when the clone is shallow, because a depth-1 fetch into a full clone writes .git/shallow"
  - "tests/test_gear_unchanged.py joins the test-image ignore set: the image has no git, read red on the unfixed recipe"

patterns-established:
  - "A guard counts after it was seen red: nine reds of the check and its tests, each log kept under the phase's investigation folder"

requirements-completed: [REQ-gear-unchanged-proof]

coverage:
  - id: D1
    description: "make gear.unchanged exits 0 on the tree as it stands and prints one line ending 'are byte-equal to v0.6' naming tests/regression/, ci.yml and /api/schema with the byte count (8723)"
    requirement: REQ-gear-unchanged-proof
    verification:
      - kind: unit
        ref: "tests/test_gear_unchanged.py#test_an_unchanged_tree_reads_green_and_names_what_it_compared"
        status: pass
      - kind: other
        ref: "make gear.unchanged (30-01-green.log)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The check is red on an edited or untracked regression file, an edited ci.yml, one changed or reordered schema byte, an empty schema, and a missing unfetchable tag; a shadowed probe import and a repository mutation are refused"
    requirement: REQ-gear-unchanged-proof
    verification:
      - kind: unit
        ref: "tests/test_gear_unchanged.py (13 tests, 13 passed)"
        status: pass
      - kind: other
        ref: "bench/RESULTS.md ### Seen red once (Phase 30), 10 rows, logs 30-01-red-*.log"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both gates run the check: verify and verify.fast each print its recipe before the pytest line"
    requirement: REQ-gear-unchanged-proof
    verification:
      - kind: unit
        ref: "tests/test_hooks.py#test_both_gates_run_the_gear_safety_check"
        status: pass
    human_judgment: false
  - id: D4
    description: "The check's wall time (three runs) and make verify.fast's wall time after the wiring are recorded with the load"
    requirement: REQ-gear-unchanged-proof
    verification:
      - kind: other
        ref: "bench/RESULTS.md ### The check, priced (30-01), 30-01-price.log"
        status: pass
    human_judgment: false
  - id: D5
    description: "The first CI run of the phase PR fetches the v0.6 tag in a shallow tagless checkout (assumption A1) and imports spur from the PYTHONPATH tree on Linux (assumption A2)"
    verification: []
    human_judgment: true
    rationale: "Not testable from this host; the phase PR's first CI run is the proof, and if it fails the check names the cause (D-05)"

duration: 35min
completed: 2026-10-23
status: complete
---

# Phase 30 Plan 01: Gear-safety check Summary

**`make gear.unchanged`: tag-baselined byte check of tests/regression/, ci.yml and the raw /api/schema response, read-only git plus `git archive`, wired into both gates at 0.46 s, seen red nine times**

## Performance

- **Duration:** about 35 min (start about 2026-10-23T15:28Z, end 2026-10-23T16:03Z); about 19 of those went to a stalled image build, see Deviations
- **Tasks:** 3
- **Files modified:** 5 source/doc files plus 12 logs

## Accomplishments

- `scripts/gear_unchanged.py` compares the two watched paths (an untracked file counts) and the `/api/schema` bytes of the working tree against `v0.6`. The baseline is read from the tag at run time and nothing is committed. `make gear.unchanged` prints `gear.unchanged: tests/regression/, .github/workflows/ci.yml and /api/schema (8723 bytes) are byte-equal to v0.6`.
- It is a prerequisite of `verify.static`, so `make verify` and `make verify.fast` both run it, and the pre-commit hook proved it at both commits of this plan.
- 13 scratch-repo tests pin green and every red (edited and untracked regression file, edited ci.yml, one changed byte, reordered keys, empty schema, missing tag with an unreachable origin, the two fetch modes, repository state, the shadow guard, the probe's bytes); `test_both_gates_run_the_gear_safety_check` pins the wiring.
- Seen red once per watched item on the real tree, plus a missing tag on a real clone, four subtle-test reds and the unfixed `test-image` recipe. Each first failure line is in `bench/RESULTS.md` `### Seen red once (Phase 30)`; whole logs are in the phase's `investigation/` folder.
- Priced: `make gear.unchanged` 0.45, 0.46, 0.46 s real; `make verify.fast` 10.01 s real, `961 passed in 9.13s`, 1-minute load 4.09 before and 5.04 after (not an idle host).

## Task Commits

1. **Tasks 1 and 2: the script, Makefile wiring, both test files, the image ignore** - `67177da` (feat). Task 1 was not committed alone, as the plan directs; the stat lists Makefile, scripts/gear_unchanged.py, tests/test_gear_unchanged.py and tests/test_hooks.py.
2. **Task 3: reds, price, Phase 30 RESULTS section, 12 logs** - `42c67af` (docs)

**Plan metadata:** the `docs(30-01)` commit that adds this file, STATE.md, ROADMAP.md and REQUIREMENTS.md.

## Files Created/Modified

- `scripts/gear_unchanged.py` - the check: `ensure_tag`, `changed_paths`, `schema_of`, `baseline_src`, `check`, `main`
- `tests/test_gear_unchanged.py` - 13 tests on scratch git repos
- `Makefile` - `gear.unchanged` target with its why-comment, `.PHONY`, `verify.static` prerequisite, `test-image` ignore
- `tests/test_hooks.py` - `test_both_gates_run_the_gear_safety_check`; `IMAGE_IGNORED` gains the new file
- `bench/RESULTS.md` - `## Scope, seam and gear-safety guard (Phase 30)`, `### The check, priced (30-01)`, `### Seen red once (Phase 30)` (append only, 0 lines deleted)

## Decisions Made

- D-04: the check sits in `verify.static`. Its cost is 0.46 s, 1.5 % of L36's 30 s commit budget, and `make verify.fast` reads 10.01 s after the wiring, so no stop-and-ask was needed.
- The Makefile comment for the new `test-image` ignore is worded `tests/test_gear_unchanged.py (also ignored): ...` instead of `--ignore=...: ...`, so the literal flag appears once in the file as the plan's acceptance count requires.

## Deviations from Plan

**1. [Rule 3 - Blocking] The `make test-image` red ran with the image build skipped**
- **Found during:** Task 2 (the unfixed-recipe red)
- **Issue:** `make test-image` depends on `image`, and `docker build` re-ran the apt layer under amd64 emulation; after about 19 minutes it was still downloading packages.
- **Fix:** stopped that build and ran the same unfixed recipe as `make -o image test-image PYTEST_ARGS="tests/test_gear_unchanged.py -q"` against the existing `spur:latest` (created 2026-10-20). The red is `FileNotFoundError: [Errno 2] No such file or directory: 'git'`, which does not depend on the image's build date. The log opens with a note saying so; the RESULTS row says the same.
- **Files modified:** `.planning/phases/30-scope-seam-and-gear-safety-guard/investigation/30-01-red-image.log`
- **Committed in:** `42c67af`

**2. [Instruction conflict] Commit trailer**
- The dispatch asked for `Co-Authored-By: Claude Opus 5.5`; the session's attribution reminder, which governs commits from here on, names `Claude Sonnet 5.5`, the model that made them. Both commits carry the Sonnet line.

**Total deviations:** 1 auto-fixed (Rule 3), 1 instruction conflict. **Impact:** none on the check or its proofs.

## Issues Encountered

- `gsd_run check evaluation-scope --plan 30-01 --commits-only` returned `no-matching-commits` for the two production commits: it matches the `{type}(30-01):` subject form, and the plan's own suggested subjects (`feat(gate): ...`, `docs(bench): ... (30-01)`) do not use it. The commits are real and measured from the ledger (`commits: 2` above). The `docs(30-01)` metadata commit matches the resolver.
- R8 (`check` registering a worktree) turned red only on the `.git/worktrees` assertion. The index-bytes and `status` assertions stayed green because the scratch repo has no `GIT_INDEX_FILE`, the variable that makes a worktree add dangerous inside the hook. The wall is the read-only git calls plus the `.git/worktrees` pin; the hook case itself is not emulated by a test.
- The plan's verification flags still open: A1 (CI's persisted credentials let the shallow, tagless checkout run `git fetch --depth=1 origin tag v0.6`) and A2 (the Linux CI venv also puts PYTHONPATH ahead of the editable src). Neither can be tested from this host; the phase PR's first CI run is the proof. If A1 fails the check fails naming git's message (D-05) and the human decides, since ci.yml may not be edited; if A2 fails the shadow guard fails the run loudly. Also accepted: a SIGKILL'd run can leave its TemporaryDirectory in the OS temp dir and nothing in the repository.
- No debt or idea item was filed.

## Known Stubs

None.

## Threat Flags

None. The check adds no endpoint, auth path or schema; it reads git objects and calls the app in-process.

## User Setup Required

None - no external service configuration required.

## Verification

- `make verify`: exit 0, `1362 passed in 238.84s (0:03:58)`, coverage `Required test coverage of 96.0% reached. Total coverage: 97.99%` (load 16.39 at start, a busy host).
- `make gear.unchanged` green after every revert; `git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml requirements.txt` empty; `git diff --exit-code HEAD -- src scripts Makefile tests` empty.
- Plan acceptance for Tasks 1 to 3 re-run: 13 tests, `13 passed`; `tests/test_hooks.py -k "gear_safety or image_suite"` `2 passed`; 10 rows start `| 30-01 |`; the RESULTS commit deleted 0 lines.

## Next Phase Readiness

Plans 30-03 and 30-04 edit gear-side files and prove each edit with `make gear.unchanged`; every commit's hook runs it. Plan 30-05 reads it at the phase close and records the gate delta (REQ-gate-cost-recorded). Phase 32 inherits the contract handoff in 30-RESEARCH Pitfall 4 (`ignore_imports` in the same commit as the `model -> shaft_model` edge), which belongs to 30-03.

## Self-Check: PASSED

Files found: `scripts/gear_unchanged.py`, `tests/test_gear_unchanged.py`, `bench/RESULTS.md`, and the twelve logs under `investigation/`. Commits found in HEAD: `67177da`, `42c67af`.

---
*Phase: 30-scope-seam-and-gear-safety-guard*
*Completed: 2026-10-23*
