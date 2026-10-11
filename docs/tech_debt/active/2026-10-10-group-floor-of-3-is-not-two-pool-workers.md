# The group floor of 3 is recorded as "two pool workers"; the live group is uvicorn, the resource tracker and one worker

Severity: must
Status: active
Date: 2026-10-10
Source: phase 21 code review, finding WR-02 (`.planning/phases/21-browser-test-of-the-viewer/21-REVIEW.md`)
Related files:
- tests/browser_session.py:49 (the comment on `MIN_GROUP_MEMBERS = 3`: "uvicorn plus the shipped pool of 2 workers")
- bench/RESULTS.md:4768 ("3 (uvicorn and two pool workers)", macOS)
- bench/RESULTS.md:4902 ("3 (uvicorn and two pool workers)", ubuntu-latest)

## Context
The comment and both `bench/RESULTS.md` rows name the three group members as uvicorn and
two pool workers. The code review listed the live group with `ps` during a run: after one
build it is uvicorn, `multiprocessing.resource_tracker` and one spawned worker, and a second
build on a different gear added no process. That matches CPython: the spawn context starts
one resource tracker when the pool is created, and `ProcessPoolExecutor` spawns workers on
demand, so sequential builds keep one worker. It also explains the recorded "before the first
build the group read 2": uvicorn plus the tracker, not uvicorn plus a worker.

ASSUMPTION: the orchestrator did not re-list the group itself; the member set above is the
reviewer's listing plus the CPython explanation. Listing it is the first step below.

## Why it matters
Comments in this codebase carry the measurement that forced the choice; this one names a
member set nobody observed. A reader trusting it would conclude that both pool workers ran
under the browser test, which the floor of 3 does not show. The floor itself still works as
the non-vacuity check for the kill — three live members before, zero after.

## Next step
List the group once with `ps -o pid=,pgid=,command=` during a run on each host, correct the
comment to the observed members, and add a dated correction under the two `RESULTS.md`
rows (do not rewrite the readings). Then decide whether the floor should name the tracker
explicitly, or whether a second concurrent build should be forced so both workers appear.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
