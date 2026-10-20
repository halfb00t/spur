"""The browser test's server process-group teardown.

Not collected: no `test_` prefix (the same convention as `tests/browser_session.py` and
`tests/composition.py`). Its own module because `tests/test_process_group.py` must import it
at commit and in `make test-image`, while `browser_session` imports the browser driver at the
top and the image installs only pytest, httpx, pytest-cov and pytest-xdist and holds no `ps`.
The precedent is `tests/test_selector.py`'s `_page_string`, a copy kept off the driver module;
here it is a move instead of a copy, so there is one definition. Nothing here imports the
driver, `cadquery` or `spur`.
"""

from __future__ import annotations

import contextlib
import os
import signal
import subprocess
import time
from typing import IO

import pytest

# How long the server gets to stop after SIGTERM and then after SIGKILL. Measured on the dev
# host: killpg took 0.22 s (21-RESEARCH Pattern 1). The bounds are generous: crossing one
# means a bug.
TERM_BOUND_S = 10.0
KILL_BOUND_S = 5.0


def _log_tail(log: IO[bytes], lines: int = 40) -> str:
    # pread, not seek: the child writes through a descriptor that shares this file's
    # offset, and a seek here would make it overwrite the start of its own log.
    fd = log.fileno()
    data = os.pread(fd, os.fstat(fd).st_size, 0)
    return "\n".join(data.decode(errors="replace").splitlines()[-lines:])


def group_members(pgid: int) -> list[int]:
    """Live pids of one process group: `ps -A -o pgid=,stat=,pid=`, zombies left out.

    A scan of the group and not of the host: this machine holds unrelated orphaned
    `multiprocessing` children, and `os.killpg(pgid, 0)` answers EPERM for a group that
    holds only zombies on macOS, so neither says what the fixture needs to know.
    """
    out = subprocess.run(
        ["ps", "-A", "-o", "pgid=,stat=,pid="], capture_output=True, text=True, check=True
    ).stdout
    live: list[int] = []
    for row in out.splitlines():
        fields = row.split()
        if len(fields) == 3 and int(fields[0]) == pgid and not fields[1].startswith("Z"):
            live.append(int(fields[2]))
    return live


def _signal_group(pgid: int, sig: signal.Signals) -> None:
    # Gone already (ProcessLookupError) is the goal; EPERM is macOS's answer for a group of
    # zombies, which group_members then reads as empty.
    with contextlib.suppress(ProcessLookupError, PermissionError):
        os.killpg(pgid, sig)


def stop_group(proc: subprocess.Popen[bytes], log: IO[bytes]) -> None:
    """SIGTERM the server's whole group, SIGKILL what outlasts the bound, fail on survivors.

    Signal first, then read: `ps` decides only how long to wait and what to report. A reader
    that fails must not stop the signals (the orphan T-21-02), and the leader is not reaped
    before the group is signalled, because a reaped leader's pid can be reused and the group
    signal would then reach an unrelated process group. A failed `ps` cannot observe the
    group, so it skips the grace and goes on to SIGKILL, then fails as "survivors unknown".

    The group, not the leader: killing only uvicorn left both pool workers alive 10 s later
    (21-RESEARCH Pitfall P3), and they would outlive the test run.
    """
    pgid = proc.pid  # start_new_session makes the leader's pid the group id
    survivors: list[int] | None = []
    for sig, bound in ((signal.SIGTERM, TERM_BOUND_S), (signal.SIGKILL, KILL_BOUND_S)):
        _signal_group(pgid, sig)
        try:
            deadline = time.monotonic() + bound
            survivors = group_members(pgid)
            while survivors and time.monotonic() < deadline:
                time.sleep(0.05)  # a poll interval; the condition is the group, not the clock
                survivors = group_members(pgid)
        except (subprocess.CalledProcessError, OSError):  # ps failed, or there is no ps
            survivors = None
            continue
        if not survivors:
            break
    with contextlib.suppress(subprocess.TimeoutExpired):
        proc.wait(timeout=KILL_BOUND_S)  # reap the leader so it is not left a zombie
    if survivors is None:
        pytest.fail(
            f"server process group {pgid}: survivors unknown, ps failed after SIGTERM and "
            f"SIGKILL were sent; server log tail:\n{_log_tail(log)}"
        )
    if survivors:
        pytest.fail(
            f"server process group {pgid} still has live pids {survivors} after "
            f"SIGTERM ({TERM_BOUND_S:.0f} s) and SIGKILL ({KILL_BOUND_S:.0f} s); "
            f"server log tail:\n{_log_tail(log)}"
        )
