---
phase: 06-address-tech-debt-merge-gate-solid-cache
plan: 03
subsystem: ci-merge-gate
tags: [pr-land, gh-api, tdd, pytest, tech-debt, docs]

# Dependency graph
requires:
  - phase: 06-address-tech-debt-merge-gate-solid-cache
    provides: "Plan 06-02's commit-msg-hook fix (message_refusals stays unchanged, tested against the same premise)"
provides:
  - "`head_refusals` refuses a completed run whose own `conclusion` is not `success`, naming the conclusion and the run's `html_url`, in addition to the unchanged per-job loop"
  - "The offline unlisted-job case and the live probe against real run 36116930241 (two refusals before, three after)"
  - "`_effective_job_names(ci_yml)`: the drift test compares `required_jobs()` against the names GitHub actually reports (`jobs.<id>.name` when set, else the id), not job ids"
  - "`docs/HOW_TO_DEVELOP.md` §8: the up-to-date-`main` rule, the `conclusion` refusal, and the effective-name line"
  - "Both `must`/`nice` D-04/D-05 debt files retired to `docs/tech_debt/resolved/`, INDEX rows moved"
affects: []

# Actuals (#2632) -- pairs with the plan's `estimate` to calibrate future estimates.
actuals:
  tokens: 6932
  tasks: 3
  commits: 3

# Commit ledger (#3968) -- measured, not narrated: git rev-list --count
# plan_head_before..HEAD at SUMMARY-write time.
commits: 3
plan_head_before: 79380fee2d4aad37bb32b14b2a69e78e542964c3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "head_refusals gains a run-conclusion check right after the status!=completed early return and before the per-job loop -- the run's own verdict and the per-job verdict are independent refusals that can both fire, never one replacing the other"
    - "_effective_job_names(ci_yml) scopes a `^    name:` (four-space) lookup to each job's own block (from the end of its id-line match to the start of the next id-line match, via re.finditer positions) -- the same block-scoping technique needed anywhere a regex must not read a nested key at a deeper, unrelated indent"

key-files:
  created: []
  modified:
    - scripts/pr_land.py
    - tests/test_pr_land.py
    - docs/HOW_TO_DEVELOP.md
    - docs/tech_debt/INDEX.md
    - "docs/tech_debt/active/2026-09-25-pr-land-admits-a-run-with-a-failing-unlisted-job.md -> docs/tech_debt/resolved/2026-09-25-pr-land-admits-a-run-with-a-failing-unlisted-job.md (git mv)"
    - "docs/tech_debt/active/2026-09-25-required-jobs-drift-test-ignores-job-name-overrides.md -> docs/tech_debt/resolved/2026-09-25-required-jobs-drift-test-ignores-job-name-overrides.md (git mv)"

key-decisions:
  - "Task 2's RED phase was produced by temporarily reverting the already-written _effective_job_names to an ids-only stub (a plain `{job_id: job_id for job_id in job_ids}` dict), running the two new tests to watch the override test fail on a real assertion, then restoring the full name-lookup implementation -- the plan's own action text offered this as one of two options ('or run it before adding the name lookup') and it was the more direct way to prove RED once the helper was already drafted from the read_first files' worked examples."
  - "The plan's own `<verify>` block for Task 2 (`make test PYTEST_ARGS=\"tests/test_pr_land.py -q -k 'job_name'\"`, expecting '2 passed') collides with a pre-existing, unrelated test name (`test_head_refusals_one_red_job_names_it_and_its_conclusion`, which also contains the substring `job_names`) -- the literal command prints '3 passed', not '2 passed'. Verified via the task's own acceptance_criteria (the three named `def` lines present, `matches_ci_yml_job_ids` absent, `.github/` untouched) and a narrower `-k` selector naming exactly the two new/renamed tests (2 passed) instead of treating the literal verify text as failing."

patterns-established: []

requirements-completed: [D-01, D-04, D-05]

coverage:
  - id: D1
    description: "head_refusals refuses a completed run whose own conclusion is not success, naming the conclusion and the run's html_url, in addition to the unchanged per-job loop"
    requirement: D-04
    verification:
      - kind: unit
        ref: "tests/test_pr_land.py#test_head_refusals_a_failed_run_is_refused_even_when_every_listed_job_is_green"
        status: pass
      - kind: unit
        ref: "tests/test_pr_land.py#test_head_refusals_one_red_job_names_it_and_its_conclusion"
        status: pass
      - kind: unit
        ref: "tests/test_pr_land.py#test_head_refusals_matches_the_recorded_red_run_verbatim"
        status: pass
      - kind: unit
        ref: "tests/test_pr_land.py#test_head_refusals_a_required_job_cancelled_or_skipped_is_refused"
        status: pass
      - kind: unit
        ref: "tests/test_pr_land.py#test_head_refusals_several_problems_at_once_prints_every_line"
        status: pass
    human_judgment: false
  - id: D2
    description: "check_head on the real, recorded failed run 36116930241 returns three refusals through the real gh (two before this plan): the run's own conclusion with its URL, and the one listed job that failed"
    requirement: D-04
    verification:
      - kind: unit
        ref: "tests/test_pr_land.py#test_check_head_names_the_run_conclusion_of_recorded_run_36116930241"
        status: pass
      - kind: other
        ref: "live probe: check_head('73535a24ce57258f23049d72e8c99eb1d5c0ba90', ...) through the real gh -- recorded verbatim in this file's Task 1 Live Probe section"
        status: pass
    human_judgment: false
  - id: D3
    description: "The drift test compares required_jobs() against the effective job names GitHub reports (jobs.<id>.name when set, else the id), not job ids; a name: override under image: moves the derived set and step-level name: keys are never read"
    requirement: D-05
    verification:
      - kind: unit
        ref: "tests/test_pr_land.py#test_required_jobs_file_matches_ci_yml_job_names"
        status: pass
      - kind: unit
        ref: "tests/test_pr_land.py#test_a_job_name_override_moves_the_derived_required_set"
        status: pass
    human_judgment: false
  - id: D4
    description: "docs/HOW_TO_DEVELOP.md Section 8 documents the up-to-date-main rule, the conclusion refusal, and the effective-name line; both D-04 and D-05 debt files are resolved, moved, and indexed in the commit that carries Section 8's text"
    requirement: D-01
    verification:
      - kind: other
        ref: "shell probe (this plan's own <verify> block): grep for the three literal additions confined to Section 8 by an awk section scan; per-file Status/Resolved-in/ancestor/ls-files/INDEX-link checks for both debt files -- recorded verbatim in this file's Task 3 verification section"
        status: pass
    human_judgment: false

duration: 10min
completed: 2026-09-25
status: complete
---

# Phase 6 Plan 3: `pr.land`'s head check trusts the run's own verdict and the job names GitHub reports Summary

**`head_refusals` now refuses a completed run whose own `conclusion` is not `success` (naming it and the run's URL) alongside the existing per-job loop, proven against the real failed run 36116930241 through the live `gh`; the drift test compares `required_jobs()` against the effective job names GitHub actually reports instead of raw job ids; both D-04/D-05 debt records are retired in the commit that documents the fix in `docs/HOW_TO_DEVELOP.md` §8.**

## Performance

- **Duration:** 10 min
- **Started:** 2026-09-25T12:41:38Z
- **Completed:** 2026-09-25T12:52:04Z
- **Tasks:** 3
- **Files modified:** 6 (two via `git mv`)

## Accomplishments

- `head_refusals` refuses a completed run whose own `conclusion` is not `success`,
  naming the conclusion's `repr` and the run's `html_url` -- right after the
  `status != "completed"` early return, before the unchanged per-job loop that still
  names a *missing* job (which a green run conclusion cannot).
- The debt file's own unlisted-job case is refused offline
  (`test_head_refusals_a_failed_run_is_refused_even_when_every_listed_job_is_green`),
  and the real, recorded failed run 36116930241 is refused through both `check_head`
  offline (`test_check_head_names_the_run_conclusion_of_recorded_run_36116930241`) and
  the real `gh` live: two refusals before this fix, three after.
- Four existing `head_refusals` cases whose run concluded `failure` were updated, never
  loosened, to expect the extra `concluded` line: `test_head_refusals_one_red_job_...`,
  `test_head_refusals_matches_the_recorded_red_run_verbatim`,
  `test_head_refusals_a_required_job_cancelled_or_skipped_is_refused`, and
  `test_head_refusals_several_problems_at_once_prints_every_line` (renamed from
  `..._prints_both_lines`, now three lines).
- `_effective_job_names(ci_yml)` derives the job name GitHub actually reports
  (`jobs.<id>.name` when a job sets one, else the id), scoped to each job's own block
  so the two step-level `name:` keys `ci.yml` already has are never read.
  `test_required_jobs_file_matches_ci_yml_job_ids` renamed
  `test_required_jobs_file_matches_ci_yml_job_names`; its body now compares against
  the effective names, not ids.
- `test_a_job_name_override_moves_the_derived_required_set` reproduces the debt
  file's own `image` -> `renamed-image` rename (plain and quoted), asserting the
  derived set moves and neither step name leaks in.
- `docs/HOW_TO_DEVELOP.md` §8 gained three additions (Russian): the up-to-date-`main`
  rule (`git switch main && git pull --ff-only`), the `conclusion` refusal in the "По
  порядку оно:" paragraph, and the effective-name sentence in the
  `required-jobs.txt`-drift paragraph.
- Both debt files are retired (`Status: resolved`, `Resolved in:` naming each fix's
  own commit, not the moving commit), `git mv`'d to `resolved/`, and
  `docs/tech_debt/INDEX.md`'s rows moved -- in the commit that carries §8's text, per
  D-01.

## Task Commits

Each task was committed atomically:

1. **Task 1: End to end -- `make pr.land`'s head check refuses a run whose own
   conclusion is not `success`, proven offline and against the real run 36116930241
   (D-04)** - `9ca8320` (fix, tracer -- RED and GREEN folded into one commit; the
   pre-commit hook runs the full `make verify` with no bypass, so a RED-only commit
   whose tests fail cannot land)
2. **Task 2: The drift test holds `required-jobs.txt` equal to the job names GitHub
   reports, `jobs.<id>.name` included (D-05)** - `0573319` (test -- RED and GREEN in
   one commit, same reason as Task 1)
3. **Task 3: §8 says where `make pr.land` runs from, that the run's own verdict
   counts, and that the list holds effective names -- both debt files retired in
   that commit (D-04, D-05, D-01)** - `ff7441a` (docs)

**Plan metadata:** committed below, alongside this SUMMARY.

_Note: Task 1 is `type="tracer" tdd="true"` and Task 2 is `type="auto" tdd="true"` --
each folds RED and GREEN into one commit, not two, because the repository's own
pre-commit hook runs the full `make verify` on every commit with no bypass (same
pattern as 06-01 and 06-02)._

## RED Evidence

**Task 1** -- before the `head_refusals` change,
`make test PYTEST_ARGS="tests/test_pr_land.py -q"` failed 6 of 54 tests, on real
assertions against the unchanged function (not import errors, fixture crashes, or
unrelated failures):

```
FAILED tests/test_pr_land.py::test_head_refusals_one_red_job_names_it_and_its_conclusion
FAILED tests/test_pr_land.py::test_head_refusals_a_failed_run_is_refused_even_when_every_listed_job_is_green
FAILED tests/test_pr_land.py::test_head_refusals_matches_the_recorded_red_run_verbatim
FAILED tests/test_pr_land.py::test_check_head_names_the_run_conclusion_of_recorded_run_36116930241
FAILED tests/test_pr_land.py::test_head_refusals_a_required_job_cancelled_or_skipped_is_refused
FAILED tests/test_pr_land.py::test_head_refusals_several_problems_at_once_prints_every_line
6 failed, 48 passed in 0.10s
```

Representative failure: `test_check_head_names_the_run_conclusion_of_recorded_run_36116930241`
asserted `len(refusals) == 2` and got `1 == 2` (`["pr.land: required job 'test (3.12)'
is failure, not success."]`) -- the target assertion failing on real behavior of the
unchanged `head_refusals`, valid RED per `gsd-core/references/tdd.md`.

**Task 2** -- `_effective_job_names` was written directly to its final, correct form
from the plan's own worked block-scoping description (block positions via
`re.finditer`, a `^    name:` lookup). To still observe a genuine RED before GREEN
(rather than commit a helper that was already green), the implementation was
temporarily reverted to an ids-only stub (`effective = {job_id: job_id for job_id in
job_ids}`, no `name:` lookup) and `make test PYTEST_ARGS="tests/test_pr_land.py -q -k
'job_name'"` run against it:

```
.F.                                                                      [100%]
_____________ test_a_job_name_override_moves_the_derived_required_set ____________
    assert names == {"test (3.12)", "vendor-bundle", "renamed-image"}
E   AssertionError: assert {'image', 'te...endor-bundle'} == {'renamed-ima...endor-bundle'}
E     Extra items in the left set: 'image'
E     Extra items in the right set: 'renamed-image'
1 failed, 2 passed, 52 deselected in 0.06s
```

The override test failed on its target assertion (the stub's derived set still says
`image`, not `renamed-image`) -- valid RED. The full name-lookup implementation was
then restored (byte-identical to what stood before the stub swap, confirmed with
`diff`) and the same command passed all 3.

After both GREEN implementations, `make test PYTEST_ARGS="tests/test_pr_land.py -q"`
passed all 55 tests (later confirmed at 188/188 under the full `make verify`).

## Live Probe (Task 1)

Before the code change (this plan's own execution, `check_head` against the real
head `73535a24ce57258f23049d72e8c99eb1d5c0ba90`, run 36116930241):

```
['pr.land: head 73535a24ce57258f23049d72e8c99eb1d5c0ba90 is 1 commit(s) behind main. Rebase onto main, push, let CI run on the real tree, retry.', "pr.land: required job 'test (3.12)' is failure, not success."]
```

Two refusals, matching the plan's own recorded pre-fix result.

After the GREEN implementation, the plan's own live `<verify>` command:

```
['pr.land: head 73535a24ce57258f23049d72e8c99eb1d5c0ba90 is 1 commit(s) behind main. Rebase onto main, push, let CI run on the real tree, retry.',
 "pr.land: the newest run for 73535a24ce57258f23049d72e8c99eb1d5c0ba90 concluded 'failure', not success: https://github.com/halfb00t/spur/actions/runs/36116930241",
 "pr.land: required job 'test (3.12)' is failure, not success."]
```

Three refusals, exit 0 -- the run's own `concluded 'failure'` line, naming the
conclusion and `actions/runs/36116930241`, is the new third line.

## Verification (Task 3)

The plan's own two `<verify>` shell probes, run against the committed state (`ff7441a`):

1. `grep -qF 'git switch main && git pull --ff-only' docs/HOW_TO_DEVELOP.md &&
   grep -qF '`conclusion`' docs/HOW_TO_DEVELOP.md && grep -qF 'jobs.<id>.name'
   docs/HOW_TO_DEVELOP.md && awk '/^## 8\. /{s=1} /^## Параллельные/{s=0} s'
   docs/HOW_TO_DEVELOP.md | grep -qF 'git switch main && git pull --ff-only'` --
   exit 0 (all four checks passed; the first attempt failed because the
   `--ff-only` clause was word-wrapped across a line break inside the markdown
   source, which `grep -F` does not span -- fixed by keeping the literal command on
   one unbroken line, see Deviations).
2. The per-file `Status`/`Resolved in`/ancestor/`ls-files`/INDEX-link probe for both
   debt files -- exit 0, no `FAILED:` line; `S1 != S2` confirmed
   (`9ca8320` != `0573319`).

`make verify` (ruff, mypy `--strict`, import boundaries, unfinished-work scan,
pytest): 188 passed in 32.20s.

## Files Created/Modified

- `scripts/pr_land.py` - `head_refusals` gained the run-conclusion refusal; docstring
  extended; `check_head`, `land`, and the parsers unchanged
- `tests/test_pr_land.py` - two new recorded constants
  (`RUN_36116930241_HEAD_SHA`/`_RUNS_JSON`/`_JOBS_JSON`), two new tests, four updated
  tests (one renamed), `_effective_job_names` helper, one renamed drift test, one new
  regression test
- `docs/HOW_TO_DEVELOP.md` - §8 gained three additions (Russian), nothing else in
  the file touched
- `docs/tech_debt/active/2026-09-25-pr-land-admits-a-run-with-a-failing-unlisted-job.md`
  -> `docs/tech_debt/resolved/...` - `git mv`'d, `Status: resolved`,
  `Resolved in: 9ca8320`, `## Resolution (2026-09-25)` appended, the trailing
  on-resolve comment removed
- `docs/tech_debt/active/2026-09-25-required-jobs-drift-test-ignores-job-name-overrides.md`
  -> `docs/tech_debt/resolved/...` - same shape, `Resolved in: 0573319`
- `docs/tech_debt/INDEX.md` - both rows moved from `## Active` to `## Resolved`

## Decisions Made

- Task 2's RED phase used a temporary stub-then-restore of `_effective_job_names`
  rather than writing an intermediate ids-only helper as a separate commit step --
  the plan's own action text explicitly offered this as an alternative ("or run it
  before adding the name lookup"). See key-decisions in the frontmatter for the full
  rationale.
- The plan's Task 2 `<verify>` command (`-k 'job_name'`, expecting "2 passed")
  collides with a pre-existing test name and prints "3 passed" instead -- verified
  correctness via the task's own `acceptance_criteria` and a narrower `-k` selector
  instead of treating the literal command's output as a failure signal. See
  key-decisions in the frontmatter.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] §8's `git switch main && git pull --ff-only` literal was
word-wrapped across a markdown line break, failing the plan's own `grep -F` check**
- **Found during:** Task 3 (writing §8's second addition)
- **Issue:** The first draft wrapped the sentence containing the literal command
  across two source lines (`git pull` on one line, `--ff-only` on the next), which
  is fine for markdown rendering but means `grep -qF 'git switch main && git pull
  --ff-only'` (a single-line literal match) does not find it -- confirmed by running
  the plan's own verify command and observing `FAIL1`.
- **Fix:** Rewrote the sentence so the literal command sits on one unbroken source
  line; the surrounding prose still wraps normally around it.
- **Files modified:** docs/HOW_TO_DEVELOP.md
- **Verification:** `grep -qF 'git switch main && git pull --ff-only'
  docs/HOW_TO_DEVELOP.md` -- exit 0 (`OK1`)
- **Committed in:** ff7441a (Task 3 commit -- caught and fixed before commit, not a
  follow-up)

---

**Total deviations:** 1 auto-fixed (1 bug -- a markdown line-wrap breaking a
single-line literal grep check, caught and fixed before the commit landed)
**Impact on plan:** No scope creep; the fix makes §8's text match the plan's own
stated acceptance check exactly.

## Issues Encountered

- The plan's own Task 2 `<verify>` command's `-k 'job_name'` filter also matches a
  pre-existing, unrelated test (`test_head_refusals_one_red_job_names_it_and_its_conclusion`,
  from Task 1, whose name contains the substring `job_names`), so the literal command
  prints "3 passed, 52 deselected" rather than the plan's expected "2 passed". This
  is not a code defect -- the task's `acceptance_criteria` (the three named `def`
  lines present, `matches_ci_yml_job_ids` absent, `.github/` untouched, `make verify`
  green) and a narrower `-k` selector naming exactly
  `test_required_jobs_file_matches_ci_yml_job_names` and
  `test_a_job_name_override_moves_the_derived_required_set` (2 passed) both confirm
  the task's `<done>` criteria are met. Documented here rather than "fixed" because
  the plan text is a historical record of what was specified, not something this
  execution edits.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- D-01, D-04, and D-05 are complete; `docs/tech_debt/INDEX.md`'s `## Active` table
  now lists only the waived-latency-bar `must` item and two unrelated `nice` items
  (`CadQuery Shape typing`, `no server-side cancellation`, `no coverage floor`, `no
  authentication`, `Enji Guard`, and `pr.land blames a skip token for any missed
  post-merge run` -- none in this plan's scope).
- `make verify` passes (188 tests) at HEAD (`ff7441a`).
- This was the last plan in Phase 6 per `06-CONTEXT.md`'s wave structure (waves 1-3,
  plans 06-01 through 06-03) -- ready for phase-level verification
  (`/gsd-verify-work 6`) and, if that passes, `/gsd-ship`.

---
*Phase: 06-address-tech-debt-merge-gate-solid-cache*
*Completed: 2026-09-25*

## Self-Check: PASSED

- `.planning/phases/06-address-tech-debt-merge-gate-solid-cache/06-03-SUMMARY.md` exists on disk (this file).
- Commits `9ca8320`, `0573319`, and `ff7441a` found in `git log --oneline --all`.
- All three task commits' post-commit acceptance-criteria checks re-run and passed (documented above and in-session).
- `make verify` exits 0 at HEAD (`ff7441a`), 188 tests passing.
