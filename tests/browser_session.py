"""The browser test's shared machinery: one real server, one headless shell, typed
`page.evaluate` wrappers, a named step.

Not collected: no `test_` prefix (`tests/composition.py`'s precedent for a shared module
under `tests/`). It is shared by the scenario module and, from 21-05, the script that
regenerates the golden request pin, so there is one server start, one launch and one sweep
rather than two copies drifting apart.

The server is a subprocess, not a thread: `spur.app.app` is a singleton whose lifespan and
`dependency_overrides` every `TestClient` test on the same xdist worker shares
(tests/test_api.py, tests/test_pool.py), and the serving process must run the pool the
product ships (D-11). Nothing here imports `cadquery` or `spur`.
"""

from __future__ import annotations

import contextlib
import json
import os
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Iterator
from typing import IO

import pytest
from playwright.sync_api import Browser, Error, Page, Playwright

# SPUR_BUILD_TIMEOUT is 30 s (app.py), so a build-bound wait must outlast it. The first
# preview build read 2.7-3.7 s at host load 8 (21-RESEARCH); if the slowest build-bound step
# on either host reads over 15 s, PD-04 makes this three times that, rounded up to 5 s.
BUILD_WAIT_MS = 45_000

# uvicorn plus the shipped pool of 2 workers (D-11, 21-RESEARCH Pattern 1). Seen before the
# kill so that the zero seen after it is a real zero and not a reader that matches nothing.
MIN_GROUP_MEMBERS = 3

# The lower of the hosts' drawn/blank PNG byte ratios divided by 2, rounded down to one
# decimal place (PD-03, written before the reading it is applied to). 21-01's reading:
# blank 3,917 B, drawn 38,908 B, ratio 9.93 (Apple M5 Max, macOS arm64, Chrome Headless
# Shell 153.0.8010.12 on SwiftShader LLVM, 1-minute load 3.3, 2026-10-10, HEAD a310cd3) ->
# 9.93 / 2 = 4.96, rounded down to 4.9. A blank canvas reads a ratio near 1.0. 21-02 re-sets
# this from the lower of the macOS and ubuntu-latest readings.
PNG_RATIO_BAR = 4.9

# How long the server gets to start, and to stop after SIGTERM and then after SIGKILL.
# Measured on the dev host: /api/health reported a pool 0.18-0.24 s after spawn, killpg
# took 0.22 s (21-RESEARCH Pattern 1). The bounds are generous: crossing one means a bug.
READY_BOUND_S = 120.0
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

    The group, not the leader: killing only uvicorn left both pool workers alive 10 s later
    (21-RESEARCH Pitfall P3), and they would outlive the test run.
    """
    pgid = proc.pid  # start_new_session makes the leader's pid the group id
    survivors = group_members(pgid)
    bound = TERM_BOUND_S
    for sig, bound in ((signal.SIGTERM, TERM_BOUND_S), (signal.SIGKILL, KILL_BOUND_S)):
        _signal_group(pgid, sig)
        deadline = time.monotonic() + bound
        survivors = group_members(pgid)
        while survivors and time.monotonic() < deadline:
            time.sleep(0.05)  # a poll interval; the condition is the group, not the clock
            survivors = group_members(pgid)
        if not survivors:
            break
    with contextlib.suppress(subprocess.TimeoutExpired):
        proc.wait(timeout=KILL_BOUND_S)  # reap the leader so it is not left a zombie
    if survivors:
        pytest.fail(
            f"server process group {pgid} still has live pids {survivors} after "
            f"SIGTERM, SIGKILL and {bound:.0f} s; server log tail:\n{_log_tail(log)}"
        )


def _wait_for_pool(base: str, proc: subprocess.Popen[bytes], log: IO[bytes]) -> None:
    """Ready means /api/health reports a pool: the lifespan has started its workers."""
    deadline = time.monotonic() + READY_BOUND_S
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            pytest.fail(f"server exited {proc.returncode} before it was ready:\n{_log_tail(log)}")
        with contextlib.suppress(urllib.error.URLError, ConnectionError, TimeoutError):
            with urllib.request.urlopen(f"{base}/api/health", timeout=5) as response:
                health: object = json.load(response)
            if isinstance(health, dict) and health.get("pool") is not None:
                return
        # wait() is the poll interval and also wakes at once if the server dies
        with contextlib.suppress(subprocess.TimeoutExpired):
            proc.wait(timeout=0.1)
    pytest.fail(f"no pool in /api/health within {READY_BOUND_S:.0f} s:\n{_log_tail(log)}")


@contextlib.contextmanager
def serve(floor_applies: Callable[[], bool] = lambda: True) -> Iterator[str]:
    """Run the shipped app in its own uvicorn process and yield its base URL.

    The listening socket is bound here, to port 0 on 127.0.0.1, and handed down by
    descriptor (`--fd`): the kernel assigns the port, so two xdist workers can never be
    given one, and nothing off the host can reach it. The child gets no `SPUR_*`
    variable, so the pool is the shipped two workers and the shipped timeouts (D-11).

    `floor_applies` is asked at teardown whether the group must still show its
    `MIN_GROUP_MEMBERS`. Pool workers start on first use: the group read 2 members after
    /api/health reported a pool and 3 after one preview build (macOS, 2026-10-10). A test
    that failed before it built anything must not add a second, misleading error here, so
    the caller says when the floor is meaningful.
    """
    sock = socket.socket()
    try:
        sock.bind(("127.0.0.1", 0))
        sock.listen(128)
        fd = sock.fileno()
        base = f"http://127.0.0.1:{sock.getsockname()[1]}"
        env = {k: v for k, v in os.environ.items() if not k.startswith("SPUR_")}
        # A file and not a PIPE: a pipe nobody reads deadlocks the server once it fills.
        with tempfile.TemporaryFile() as log:
            proc = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "spur.app:app", "--fd", str(fd)],
                pass_fds=(fd,),
                start_new_session=True,
                stdout=log,
                stderr=log,
                env=env,
            )
            body_finished = False
            try:
                _wait_for_pool(base, proc, log)
                yield base
                body_finished = True
            finally:
                try:
                    if body_finished and floor_applies():
                        members = group_members(proc.pid)
                        print(f"server group members before the kill: {len(members)}")
                        assert len(members) >= MIN_GROUP_MEMBERS, (
                            f"saw {members} in the server's group, expected uvicorn plus its "
                            f"pool workers (>= {MIN_GROUP_MEMBERS}): the survivor check "
                            "below would read an empty group as proof"
                        )
                finally:
                    stop_group(proc, log)
    finally:
        sock.close()


def launch(pw: Playwright) -> Browser:
    """Start the default Chrome Headless Shell, or fail the test naming how to install it.

    Called from the test body, not a fixture: `pytest.fail` in a fixture reports ERROR, in
    the body FAILED. No channel, no flags: the default shell renders on SwiftShader on both
    hosts, while the full Chromium channel would draw on the host GPU (D-03).
    """
    try:
        return pw.chromium.launch()
    except Error as error:
        path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "<unset: Playwright's default cache>")
        pytest.fail(
            "the headless shell is not installed: run `playwright install --only-shell "
            f"chromium` (PLAYWRIGHT_BROWSERS_PATH={path}); `make test` runs the install "
            f"stamp for you.\nPlaywright said: {error}"
        )


# page.evaluate returns Any. Assigning it to `object` and narrowing is what mypy --strict
# accepts; `return page.evaluate(...)` is `no-any-return` (21-RESEARCH Pattern 4).


def eval_int(page: Page, expression: str, arg: object = None) -> int:
    value: object = page.evaluate(expression, arg)
    assert isinstance(value, int), f"{expression!r} gave {value!r}, not an int"
    return value


def eval_str(page: Page, expression: str, arg: object = None) -> str:
    value: object = page.evaluate(expression, arg)
    assert isinstance(value, str), f"{expression!r} gave {value!r}, not a str"
    return value


def eval_opt_str(page: Page, expression: str, arg: object = None) -> str | None:
    value: object = page.evaluate(expression, arg)
    assert value is None or isinstance(value, str), f"{expression!r} gave {value!r}"
    return value


def eval_bool(page: Page, expression: str, arg: object = None) -> bool:
    value: object = page.evaluate(expression, arg)
    assert isinstance(value, bool), f"{expression!r} gave {value!r}, not a bool"
    return value


def eval_str_list(page: Page, expression: str, arg: object = None) -> list[str]:
    value: object = page.evaluate(expression, arg)
    assert isinstance(value, list), f"{expression!r} gave {value!r}, not a list"
    items: list[str] = []
    for item in value:
        assert isinstance(item, str), f"{expression!r} held {item!r}, not a str"
        items.append(item)
    return items


def stl_triangles(stl: bytes) -> int:
    """The triangle count a binary STL declares: a little-endian uint32 after 80 header bytes."""
    assert len(stl) >= 84, f"{len(stl)} bytes cannot hold an STL header"
    count: int = struct.unpack_from("<I", stl, 80)[0]
    return count


@contextlib.contextmanager
def step(name: str) -> Iterator[None]:
    """Time one scenario step, print its line, and name it on any failure (D-10)."""
    started = time.monotonic()
    try:
        yield
    except BaseException as error:
        error.add_note(f"step: {name}")
        raise
    finally:
        print(f"step {name}: {time.monotonic() - started:.2f} s")
