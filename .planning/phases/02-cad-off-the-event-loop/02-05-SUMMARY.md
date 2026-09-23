---
phase: 02-cad-off-the-event-loop
plan: 05
subsystem: infra
tags: [decision-log, dockerfile, healthcheck, tech-debt, architecture-docs]

# Dependency graph
requires:
  - phase: 02-cad-off-the-event-loop
    provides: "02-04's bench/RESULTS.md (all latency and memory measurements) and quick
      task 260923-qwr's gzip fix (2d47994, 7a61fad) plus the human's waiver decision --
      this plan's L17/L18/L19 and the HEALTHCHECK timeout are transcribed from that
      evidence, not re-measured."
provides:
  - "L17, L18, L19 appended to docs/architecture/decision_log.md (supersede L07, supersede
    L06, and a new gzip-admission decision), every number transcribed from
    bench/RESULTS.md and the quick-task SUMMARY, L06/L07 byte-identical"
  - "Dockerfile HEALTHCHECK --timeout lowered from 10s to 2s (inner urlopen 8s -> 1s), set
    from the measured under-load p95 (0.7-1.3ms across all eight bench/RESULTS.md latency
    runs), comment rewritten"
  - "docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md resolved
    (Status: resolved, Resolved in: daeb284), git mv'd to resolved/, INDEX.md row moved --
    this repository's first completed tech-debt lifecycle"
  - "docs/architecture/overview.md redrawn for the kernel-free server plus N build
    workers: a new pool.py row, updated app.py/model.py rows, the fourth import-linter
    contract named, the caches bullet pointed at L17"
affects: []

# Actuals (#2632)
actuals:
  tokens: 4442      # chars/4 over 81486f2..HEAD, .planning excluded (17767 chars)
  tasks: 3           # Task 1 was the pre-resolved decision checkpoint (no code); Tasks 2-4 committed
  commits: 3
  plan_head_before: 81486f2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A resolved tech-debt file's closing note must stay proportionate to the original
      file's size, or the in-commit content growth pushes git's default 50%
      rename-similarity threshold below detection -- a `git mv` into a bloated file then
      commits as a recorded delete+add, not a rename. Check with `git diff -M --summary`
      before committing a resolve-and-move."

key-files:
  created: []
  modified:
    - docs/architecture/decision_log.md
    - Dockerfile
    - docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md (renamed to docs/tech_debt/resolved/)
    - docs/tech_debt/INDEX.md
    - docs/architecture/overview.md

key-decisions:
  - "L17 supersedes L07 with a swept (not derived) memory formula (parent byte budget +
    N x per-worker solid cache); L18 supersedes L06, retiring only the throughput
    consequence and keeping the RLock; L19 records the gzip admission-bound decision as a
    new entry -- Option A per the human's Task 1 checkpoint decision (append both, plus
    L19, numbers inline)."
  - "HEALTHCHECK --timeout: 2s (inner urlopen 1s), chosen with margin over the worst
    measured p95 (1.3ms) for the probe's own Python interpreter startup inside the
    container, not for the request itself -- the old 10s existed to tolerate a stall this
    phase removed."
  - "The debt file's Resolved in: field cites daeb284 (the Plan 02-01 commit that actually
    fixed the debt), not this plan's own commit that records the resolution -- the file
    says which is which so the two shas are never confused."
  - "L18's concurrent-scenario claim is recorded as accepted with caveat, not
    demonstrated, per the human's 2026-09-23 waiver -- no throughput number is invented;
    'concurrency now buys throughput too' is stated as a structural property of N
    independent kernels, not a measured requests/second figure."

patterns-established:
  - "A resolved tech-debt file's closing note stays proportionate to the original file's
    size so git's default rename-similarity threshold still detects the git mv as a
    rename, not a delete+add."

requirements-completed: [REQ-cad-off-event-loop, REQ-measured-memory-ceiling]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "L17 appended to decision_log.md, supersedes L07, carrying the per-N
      peak table, the confirmed mem_limit and headroom factor, and the
      max_tasks_per_child outcome with drift numbers, all inline."
    requirement: "REQ-measured-memory-ceiling"
    verification:
      - kind: other
        ref: "grep -nE '^## L1[78] ' docs/architecture/decision_log.md (2 headings);
          grep -n 'supersedes L07'; git diff --stat 81486f2..HEAD -- decision_log.md
          (151 insertions, 0 deletions); make verify"
        status: pass
    human_judgment: false
  - id: D2
    description: "L18 appended, supersedes L06, keeps the RLock, retires only the
      'concurrency buys latency not throughput' consequence, cites the measured latency
      ratios and carries the waiver caveat verbatim."
    requirement: "REQ-cad-off-event-loop"
    verification:
      - kind: other
        ref: "grep -n 'supersedes L06' docs/architecture/decision_log.md; diff-stat
          adds-only check above; make verify"
        status: pass
    human_judgment: false
  - id: D3
    description: "L19 (new entry) records the gzip level/admission-bound decision from
      quick task 260923-qwr, citing the measured 1/6/9 table, the E2c 4.33x/5.52x
      finding, and commits 2d47994/7a61fad."
    verification:
      - kind: other
        ref: "grep -cE '^## L1[789] ' docs/architecture/decision_log.md (3); make
          verify"
        status: pass
    human_judgment: false
  - id: D4
    description: "Dockerfile HEALTHCHECK --timeout lowered from 10s to 2s, set from the
      measured under-load p95, comment rewritten to cite bench/RESULTS.md; make up
      observed reaching healthy under the new timeout."
    requirement: "REQ-cad-off-event-loop"
    verification:
      - kind: other
        ref: "make check (image build + docker/smoke.py); docker inspect --format
          '{{json .Config.Healthcheck}}' spur-spur-1 -- Timeout=2000000000ns; docker
          compose up -d --build -> healthy in ~1s this session"
        status: pass
    human_judgment: true
    rationale: "Task 3's own <human-check> asks a human to bring the service up, watch it
      reach healthy, and read the rewritten comment for whether it describes the shipped
      service rather than the one this phase replaced -- deferred to end-of-phase UAT per
      workflow.human_verify_mode=end-of-phase."
  - id: D5
    description: "docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md is
      Status: resolved with Resolved in: daeb284, git mv'd to resolved/, and
      INDEX.md's row moved from Active to Resolved -- in the same commit as the
      HEALTHCHECK fix."
    requirement: "REQ-cad-off-event-loop"
    verification:
      - kind: other
        ref: "git status --porcelain docs/tech_debt/; test -f resolved/... && test
          ! -f active/...; grep -nE '^Status:|^Resolved in:' resolved/...; grep -n
          'cad-builds-block-the-event-loop' INDEX.md; git diff -M --summary shows a
          63%-similarity rename, not a delete+add; make check"
        status: pass
    human_judgment: false
  - id: D6
    description: "docs/architecture/overview.md redrawn: a build-pool row, updated
      app.py/model.py rows, the fourth import-linter contract named, the caches bullet
      pointed at L17 -- still one page."
    verification:
      - kind: other
        ref: "grep -nE 'pool\\.py|build pool|worker process' overview.md; grep -n L17
          overview.md; wc -l overview.md (60 lines); make verify"
        status: pass
    human_judgment: true
    rationale: "Task 4's own <human-check> asks a human to read overview.md, http-api.md
      and packaging.md back to back for one consistent story -- deferred to end-of-phase
      UAT per workflow.human_verify_mode=end-of-phase."

duration: ~35min (continuation from Task 2; Task 1's decision checkpoint was already
  resolved by the human before this continuation began)
completed: 2026-09-23
status: complete
---

# Phase 2 Plan 5: Close the Loop -- Supersede, Retire, Redraw Summary

**L17/L18/L19 appended to the decision log with every number transcribed from
bench/RESULTS.md, the Docker HEALTHCHECK timeout dropped from 10s to 2s on the measured
p95, the CAD-builds-block-the-event-loop debt resolved and moved -- this repository's
first completed tech-debt lifecycle -- and the system map redrawn for the kernel-free
server plus N build workers.**

## Performance

- **Duration:** ~35 min this continuation (Task 1's decision checkpoint was already
  resolved by the human before it started)
- **Started:** 2026-09-23 (continuation)
- **Completed:** 2026-09-23T15:06:26Z
- **Tasks:** 3 completed this continuation (Tasks 2, 3, 4; Task 1 had no code)
- **Files modified:** 5

## Accomplishments

- `docs/architecture/decision_log.md` gains three entries, L17 (supersedes L07, the
  swept memory formula, the per-N peak table, the confirmed `mem_limit`), L18 (supersedes
  L06, keeps the lock, retires only its throughput consequence, carries the waiver
  caveat), and L19 (new, the gzip-level/admission-bound decision) -- L06 and L07 stand
  untouched (diff adds 151 lines, deletes none).
- The Dockerfile's `HEALTHCHECK --timeout` is down from 10s to 2s (inner `urlopen`
  timeout 8s -> 1s), set from the measured under-load p95 (0.7-1.3ms across all eight
  latency runs) rather than the old comment's now-disproven claim that OpenCascade
  legitimately stalls the event loop for a few seconds.
- `docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md` is resolved
  (`Status: resolved`, `Resolved in: daeb284`), `git mv`'d to `resolved/`, and
  `docs/tech_debt/INDEX.md`'s Active row moved to a new Resolved table -- exercising this
  repository's tech-debt lifecycle for the first time, in the same commit as the
  HEALTHCHECK fix that removed the last accommodation.
- `docs/architecture/overview.md`'s "Main pieces" table gains a `pool.py` row and updated
  `app.py`/`model.py` rows; the enforced-dependency paragraph names the fourth
  import-linter contract (serving process never imports the CAD kernel, indirect
  included); the caches bullet points at L17 instead of the now-superseded L07. Still one
  page (60 lines).
- `make verify` and `make check` (image build, in-image smoke test, vendored-bundle byte
  check) both green throughout; `docker compose up -d --build` reached `healthy` in ~1s
  under the new timeout.

## Task Commits

Each task was committed atomically:

1. **Task 1: Decision -- append L17 and L18 (D-20, one-way)** - resolved by the human
   before this continuation began (Option A + L19); no commit (checkpoint:decision).
2. **Task 2: L17 and L18 -- supersede, never rewrite** - `163a84b` (docs)
3. **Task 3: Bring the healthcheck timeout down, and retire the debt in the same commit**
   - `becedc0` (fix)
4. **Task 4: Redraw the system map** - `4e8b8ac` (docs)

**Plan metadata:** commit follows this summary.

## Files Created/Modified

- `docs/architecture/decision_log.md` - gains L17, L18, L19; L06/L07 byte-identical.
- `Dockerfile` - `HEALTHCHECK --timeout=2s` (was 10s), inner `urlopen timeout=1` (was 8),
  comment rewritten to cite the measured p95 and `bench/RESULTS.md`.
- `docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md` -> `docs/tech_debt/resolved/2026-09-21-cad-builds-block-the-event-loop.md`
  (renamed): `Status: resolved`, `Resolved in: daeb284`, a "Resolution (2026-09-23)"
  section naming what was done and the measured (caveated) result; original Context and
  Why-it-matters sections kept intact.
- `docs/tech_debt/INDEX.md` - the row moved from the Active table into a new Resolved
  table.
- `docs/architecture/overview.md` - new `pool.py` row; `app.py`/`model.py` rows updated
  for their post-phase roles; fourth import-linter contract named; caches bullet points
  at L17.

## Decisions Made

See `key-decisions` in the frontmatter. Most consequential: L18 records the concurrent
latency scenario as **accepted with caveat, not demonstrated** -- the human's waiver, not
a claim that the bar was met -- and states no throughput number that isn't in
`bench/RESULTS.md` (L08).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] A `git mv`'d, content-heavy debt file committed as a delete+add
instead of a detected rename**
- **Found during:** Task 3, immediately after the first commit of the Dockerfile +
  debt-file + INDEX change.
- **Issue:** The debt file's closing "Resolution" section and `Resolved in:` explanation
  nearly doubled the original 37-line file to 70 lines, dropping git's rename-similarity
  score to 42% -- below the default 50% threshold `git status`/`git diff -M` uses to
  detect a rename. The commit (`398355c`) recorded the move as a plain delete + add, which
  fails Task 3's own acceptance criterion ("git records a rename rather than a delete
  plus an add") and the threat register's T-02-17 mitigation (the debt lifecycle must be
  provably a move, not an erase-and-recreate).
- **Fix:** `git reset --soft HEAD~1` (local, unshared, non-destructive -- the commit had
  not been pushed or seen by anyone) to un-commit without losing any staged content, then
  trimmed the closing note to a single compact paragraph (51 lines total, well within the
  proportion that keeps similarity above 50%), then re-staged and re-committed.
- **Files modified:** `docs/tech_debt/resolved/2026-09-21-cad-builds-block-the-event-loop.md`
- **Verification:** `git diff -M --summary` on the re-committed state shows `rename
  docs/tech_debt/{active => resolved}/... (63%)`; `git status --porcelain docs/tech_debt/`
  shows `R`, not `D`+`A`; `make check` green.
- **Committed in:** `becedc0` (the corrected commit; `398355c` never existed in final
  history)

---

**Total deviations:** 1 auto-fixed (1 Rule 1). **Impact on plan:** Self-corrected before
any commit was shared; the final history satisfies every acceptance criterion the plan
states for the rename. No scope creep.

## Issues Encountered

None beyond the deviation above, which was caught and fixed before being reported.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Both of Phase 2's requirements (`REQ-cad-off-event-loop`, `REQ-measured-memory-ceiling`)
are structurally ready to mark `Complete` in `.planning/REQUIREMENTS.md`
(`requirements.ready-ids` reports 2/2 ready -- this was the last plan declaring either
ID). The decision record, the runtime timeout, and the debt lifecycle are all closed out
consistently with the evidence: the `single` latency scenario is met on every run; the
`concurrent` scenario is accepted with caveat, not demonstrated, per the human's
2026-09-23 waiver.

One `must`-severity debt item stays open and untouched by this plan, as intended:
`docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` (the caveat itself),
with its own named triggers (harness or machine change, any run above 2.45x). This plan's
L17/L18/L19 carry that caveat verbatim rather than resolving it -- nothing in this plan's
scope was meant to close it.

Phase 2 is otherwise complete: all five plans have summaries, both requirements are
ready, and the three architecture documents (`overview.md`, `http-api.md`,
`packaging.md`) describe the shipped kernel-free-server-plus-N-workers topology
consistently (cross-checked by reading all three during Task 4; formal human sign-off on
that consistency and on the HEALTHCHECK comment/behaviour deferred to end-of-phase UAT
per `workflow.human_verify_mode=end-of-phase`, coverage IDs D4 and D6 above).

## Self-Check: PASSED

- FOUND: `docs/architecture/decision_log.md` (contains `## L17`, `## L18`, `## L19`)
- FOUND: `Dockerfile` (`HEALTHCHECK --timeout=2s`)
- FOUND: `docs/tech_debt/resolved/2026-09-21-cad-builds-block-the-event-loop.md`
  (`Status: resolved`, `Resolved in: daeb284`)
- CONFIRMED: `docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md` no
  longer exists
- FOUND: `docs/architecture/overview.md` (contains `pool.py`, `L17`)
- FOUND commits `163a84b`, `becedc0`, `4e8b8ac` (`git log --oneline --all | grep`)
- CONFIRMED: `git rev-list --count 81486f2..HEAD` = 3, matching `actuals.commits` above
  (`plan_head_before: 81486f2`)
- CONFIRMED: `make verify` green (ruff, mypy --strict, lint-imports, no-fake-done, 71
  passed) at the final state
- CONFIRMED: `make check` green (image build, `docker/smoke.py`, vendor-check) at the
  final state
- CONFIRMED: `docker compose up -d --build` reached `healthy` (`docker inspect
  --format '{{json .Config.Healthcheck}}' spur-spur-1` shows `Timeout: 2000000000`ns,
  matching the Dockerfile)

---
*Phase: 02-cad-off-the-event-loop*
*Completed: 2026-09-23*
