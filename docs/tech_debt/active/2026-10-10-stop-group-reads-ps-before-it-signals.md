# `stop_group` reads `ps` before it signals, so a failed `ps` leaves the server group alive

Severity: must
Status: active
Date: 2026-10-10
Source: phase 21 code review, finding WR-01 (`.planning/phases/21-browser-test-of-the-viewer/21-REVIEW.md`)
Related files:
- tests/browser_session.py:91 (`group_members` runs `ps` with `check=True`)
- tests/browser_session.py:116 (first `survivors` read, before any signal; overwritten before use)
- tests/browser_session.py:120 (read after each signal; a failure here skips `SIGKILL`)

## Context
`group_members` runs `ps -A -o pgid=,stat=,pid=` with `check=True`, so a non-zero `ps`
raises `CalledProcessError`. `stop_group` calls it once before the signal loop (that value is
overwritten before it is used) and once after each signal. A `ps` failure before the first
call sends no `SIGTERM`; the same failure after `SIGTERM` sends no `SIGKILL`. In both cases
the uvicorn group outlives the run — the orphan T-21-02 was mitigated against — and the
teardown reports the `ps` error, not survivors. `ps` is procps on the runner and BSD `ps` on
macOS; neither has failed in any recorded run, so this is a latent path, not an observed one.

## Why it matters
The teardown's one job is that no server outlives the test. A failure in the reader must
not stop the signals from being sent; today it does, and the failure reads as a tooling error
rather than as "a server is still running".

## Next step
Send `SIGTERM` and, after the bound, `SIGKILL` unconditionally; read the group only to decide
how long to wait and for the final assertion; treat a failed `ps` as "survivors unknown" and
fail with that wording; drop the dead first assignment. Re-run the leader-only red from
`bench/RESULTS.md` (21-01, "Seen red once") to confirm the survivor check still fires.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
