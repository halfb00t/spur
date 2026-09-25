---
phase: 02-cad-off-the-event-loop
plan: 02
subsystem: testing
tags: [argparse, httpx, statistics, docker, make]

# Dependency graph
requires:
  - phase: 02-cad-off-the-event-loop
    provides: "Plan 02-01's process-pool topology (SPUR_BUILD_WORKERS, /api/health) --
      not consumed by this plan's code, but the reason the harness exists."
provides:
  - "A committed, rerunnable `make bench` (bench.latency + bench.memory) that can
    produce every number Phase 2's two success criteria depend on."
  - "bench/corpus.py: L07's own 40 distinct 160-199 tooth gears, generated
    deterministically -- the fixed workload Plan 02-04's memory sweep must reuse."
  - "bench/latency.py: the debt file's single/concurrent load scenarios against
    /api/health, p95 via statistics.quantiles(n=20) only, refusing <20-sample reports."
  - "bench/memory.py: the N=1,2,4 container memory sweep and the confirm-at-a-candidate-
    limit run, driving docker compose directly."
affects: [02-04]

# Actuals (#2632)
actuals:
  tokens: 7057    # chars/4 over the realized diff (ec457d3..HEAD, .planning excluded)
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []   # stdlib + httpx (already a dev dependency) only
  patterns:
    - "Argparse CLI mirroring docker/smoke.py's script shape and the Makefile's
      docker-driven target shape (Makefile's smoke/up/down), for a tool that lives
      outside src/ and is therefore allowed to print (unlike src/'s no-print rule)."
    - "Container memory peak read via `docker stats --no-stream` polling every 0.5s,
      not by exec'ing into the container to read /sys/fs/cgroup/memory.peak -- the
      image runs as a non-root `nologin` user and cgroup v1 vs v2 layout was never
      verified this session (02-02-PLAN.md flagged assumption 1)."
    - "A one-line generated docker-compose override YAML file is the only way `confirm`
      mode sets mem_limit per invocation, since `docker compose run` (unlike plain
      `docker run`) has no --memory flag."
    - "A tiny shared bench/__init__.py (machine_facts()) instead of duplicating the
      CPU/arch/RAM block in both bench/latency.py and bench/memory.py."

key-files:
  created:
    - bench/__init__.py
    - bench/corpus.py
    - bench/latency.py
    - bench/memory.py
    - bench/README.md
  modified:
    - Makefile

key-decisions:
  - "Container memory peak is sampled via `docker stats --no-stream` polling rather
    than reading a cgroup peak file inside the container -- resolved rather than
    deferred, since the image's non-root/nologin user makes `docker exec ... cat
    /sys/fs/cgroup/...` unreliable without also verifying a shell and cgroup layout
    that were never checked this session."
  - "`bench.memory confirm`'s mem_limit override goes through a generated one-line
    compose override file merged via `-f compose.yaml -f <override>`, not a CLI flag
    (none exists on `docker compose run`) and not an edit to compose.yaml itself
    (that stays Plan 02-04's job, per files_modified)."
  - "The concurrent latency scenario uses ten fixed tooth counts (190-199) of its own,
    not bench/corpus.py's 40-gear corpus -- keeps the memory-sweep corpus, which D-18
    pins and forbids changing, decoupled from the latency scenario's own workload
    choice."

requirements-completed: [REQ-cad-off-event-loop, REQ-measured-memory-ceiling]

coverage:
  - id: D1
    description: "bench/corpus.py generates L07's own 40 distinct 160-199 tooth gears,
      deterministically from the tooth count alone."
    requirement: "REQ-measured-memory-ceiling"
    verification:
      - kind: other
        ref: "python -c 'from bench.corpus import corpus; ...' (40 entries, 40 distinct
          teeth, all 160<=teeth<=199) -- run this session"
        status: pass
    human_judgment: false
  - id: D2
    description: "bench/latency.py's CLI names both the `single` and `concurrent`
      scenarios and exits 0 on --help."
    requirement: "REQ-cad-off-event-loop"
    verification:
      - kind: other
        ref: ".venv/bin/python -m bench.latency --help -- run this session"
        status: pass
    human_judgment: false
  - id: D3
    description: "bench/latency.py's runtime behavior against a live service: idle vs.
      under-load p95 via statistics.quantiles(n=20), the <20-sample refusal, and the
      recorded-baseline comparison."
    requirement: "REQ-cad-off-event-loop"
    verification: []
    human_judgment: true
    rationale: "Deliberately not run against a live service this session -- the plan's
      own objective is that Wave 1 authors the harness only and runs nothing against
      the service (the topology it measures lands in parallel via Plan 02-01). Plan
      02-04 executes it for real and records the numbers in bench/RESULTS.md."
  - id: D4
    description: "bench/memory.py's CLI names both the `sweep` and `confirm` modes and
      exits 0 on --help."
    requirement: "REQ-measured-memory-ceiling"
    verification:
      - kind: other
        ref: ".venv/bin/python -m bench.memory --help -- run this session"
        status: pass
    human_judgment: false
  - id: D5
    description: "bench/memory.py's runtime behavior: the N=1,2,4 sweep against a real
      Docker daemon, peak tracking, cold-start teardown between values of N, the
      confirm run, and the empty-row-on-failure / non-zero-exit contract."
    requirement: "REQ-measured-memory-ceiling"
    verification: []
    human_judgment: true
    rationale: "Deliberately not run against Docker this session, for the same reason
      as D3 -- Plan 02-04 runs the real sweep and records the per-N table."
  - id: D6
    description: "make bench / bench.latency / bench.memory exist, are listed by make
      help, are not prerequisites of verify or check, and bench/ is inside the
      typecheck target's mypy --strict scope."
    requirement: "REQ-cad-off-event-loop"
    verification:
      - kind: other
        ref: "make -n bench.latency bench.memory bench; make help; make verify with
          mypy's file count rising from 15 to 19 source files -- all run this session"
        status: pass
    human_judgment: false

duration: 19min
completed: 2026-09-23
status: complete
---

# Phase 2 Plan 2: Bench Harness (Latency + Memory-Sweep Instrument) Summary

A committed `make bench` -- `bench/corpus.py`, `bench/latency.py`, `bench/memory.py` --
that can reproduce the debt file's two load scenarios and the N=1,2,4 container memory
sweep over L07's own 40-gear corpus, held to `mypy --strict` and deliberately outside
`make verify`/`make check`.

## Performance

- **Duration:** ~19 min
- **Started:** 2026-09-23T08:49 (local, +06:00) -- immediately after Plan 02-01's `docs`
  commit
- **Completed:** 2026-09-23T09:08 (local, +06:00)
- **Tasks:** 3 completed
- **Files changed:** 6 (5 created, 1 modified)

## Accomplishments

- `bench/corpus.py` reproduces L07's own memory-sweep workload exactly: 40 distinct
  160-199 tooth gears, generated deterministically from the tooth count so two runs on
  two machines drive the identical corpus -- verified this session (`corpus ok 40`).
- `bench/latency.py` implements both of the debt file's load scenarios (`single`: one
  200-tooth fine build in flight; `concurrent`: ten concurrent builds), sampling
  `/api/health` throughout each. p95 is computed by exactly one named stdlib call
  (`statistics.quantiles(samples, n=20)[-1]`), and a scenario with fewer than 20 health
  samples is refused with a named warning rather than given a plausible number (L08).
  Every report carries CPU count, architecture and total RAM (D-17), plus the debt
  file's own recorded baseline printed alongside for reference, explicitly labelled as
  a different machine.
- `bench/memory.py` drives `docker compose` itself. `sweep` cold-starts the service at
  `SPUR_BUILD_WORKERS`=1, 2 and 4 in turn, drives the 40-gear corpus through
  `/api/model.stl?quality=fine`, and records the peak container memory (sampled from
  `docker stats --no-stream`, polled every 0.5s -- documented as a sampled peak, not
  the cgroup accounting's exact one) alongside request/failure counts and elapsed time.
  A value of N that never comes up, or that produces no memory samples, gets a named
  warning and an empty peak rather than a guessed one, and the process exits non-zero
  when any row is incomplete. `confirm` re-runs the corpus at a candidate `mem_limit`
  (via a generated one-line compose override file, since `docker compose run` has no
  `--memory` flag) and reports the failure count.
- Three new `make` targets (`bench`, `bench.latency`, `bench.memory`), modelled on the
  existing `smoke`/`up`/`down` shape, listed by `make help`, and deliberately **not** a
  prerequisite of `verify` or `check` (D-16). `bench/` is now inside the `typecheck`
  target's `mypy --strict` scope (confirmed: file count rose from 15 to 19).
- `bench/README.md` documents what each half measures, which environment each must run
  in and why, how to run them, and the corpus-stability rule that outranks convenience.

## Task Commits

Each task was committed atomically:

1. **Task 1: The corpus, and the latency scenarios the debt file already ran** -
   `ca06141` (feat)
2. **Task 2: The container memory sweep, earned the way 2g was earned** - `80f25b5`
   (feat)
3. **Task 3: Wire `make bench`, and hold the harness to the same gate as `src/`** -
   `af1bd45` (chore)

## Files Created/Modified

- `bench/__init__.py` (new) - package marker plus a shared `machine_facts()` helper
  (CPU count, architecture, total RAM via `os.sysconf`), used by both `latency.py` and
  `memory.py` so the D-17 machine block isn't duplicated.
- `bench/corpus.py` (new) - `corpus()`: L07's own 40 distinct 160-199 tooth gears.
- `bench/latency.py` (new) - `single`/`concurrent` scenarios, `statistics.quantiles`
  p95, the <20-sample refusal, the machine-facts + recorded-baseline report.
- `bench/memory.py` (new) - `sweep` (N=1,2,4 peak table) and `confirm` (candidate
  `mem_limit`, failure count) modes, both driving `docker compose` via argument lists
  (never a shell string -- T-02-05).
- `bench/README.md` (new) - what/where/how/why for both halves, and the corpus rule.
- `Makefile` - `bench`, `bench.latency`, `bench.memory` targets and `.PHONY` entries;
  `typecheck`'s mypy invocation extended to include `bench`.

## Decisions Made

See `key-decisions` in the frontmatter. The most consequential: reading container
memory via `docker stats --no-stream` polling rather than the cgroup peak file --
02-02-PLAN.md's flagged assumption 1 left this open, and it was resolved here (not
deferred) because the alternative (`docker exec ... cat /sys/fs/cgroup/...`) needs a
shell inside a non-root, `nologin` image and a cgroup version this session had no way
to verify. The choice is documented as a sampled, not exact, peak in both the code
comment and `bench/README.md`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking issue] mypy rejected `corpus()`'s `dict[str, object]` values
passed straight into httpx's `params`**
- **Found during:** Task 2, first `make verify` run for `bench/memory.py`.
- **Issue:** `bench.corpus.corpus()`'s plan-mandated signature is
  `list[dict[str, object]]`; unpacking one of those dicts straight into
  `httpx.Client.get(params=...)` fails `mypy --strict` because `object` isn't one of
  httpx's accepted primitive query-param types.
- **Fix:** In `bench/memory.py`'s `_drive_corpus`, stringify every corpus value
  (`{k: str(v) for k, v in gear.items()}`) before building the params dict -- a query
  string is text either way, and this doesn't touch `bench/corpus.py`'s own signature.
- **Files modified:** `bench/memory.py`.
- **Verification:** `make verify` green (`mypy --strict`: "Success: no issues found in
  19 source files").
- **Committed in:** `80f25b5`

---

**Total deviations:** 1 auto-fixed (Rule 3: blocking type-check issue). **Impact:**
none on behavior or scope -- a type-compatibility fix at the harness's own boundary,
not a change to the corpus contract or the memory-figure logic.

## Issues Encountered

None beyond the deviation documented above.

## User Setup Required

None - no external service configuration required. No new dependency (stdlib plus
`httpx`, already a dev dependency).

## Next Phase Readiness

The harness is committed, typechecked and its structural/CLI-surface checks all pass
this session (`--help` for both modules, the corpus assertion, `make -n`/`make help`,
`make verify` with `bench/` in the typecheck scope). Its actual runtime behavior against
a live service and a running Docker daemon was **deliberately not exercised** this
session -- that is Plan 02-04's job, per this plan's own objective ("this plan authors
the harness only ... runs nothing against the service"). Ready for Plan 02-03; Plan
02-04 depends on this plan and should budget time for the harness's first real run to
surface anything the corpus-and-CLI-level checks here couldn't catch (e.g. the docker
stats output format on the executor's actual Docker version, per flagged assumption 1).
No blockers.

## Self-Check: PASSED

All 6 created/modified files confirmed present on disk; all 3 task commits (`ca06141`,
`80f25b5`, `af1bd45`) confirmed present in `git log --oneline --all`.

---
*Phase: 02-cad-off-the-event-loop*
*Completed: 2026-09-23*
