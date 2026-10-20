"""The server group teardown signals before it reads, and a failed `ps` fails it.

REQ-stop-group-signals-first, SC3.

`stop_group` used to read the group with `ps` before it sent a signal, so a `ps` that
failed left the uvicorn group alive (the orphan T-21-02 was mitigated against). It now
signals first and lets `ps` decide only how long to wait and what to report.

The tests use a fake `group_members`: the container image has no `ps`, and a fake lets the
second test fail it on purpose. The group itself is real, a `sleep 60` in its own session,
so a signal that never arrives would leave the leader running. The order of events is
recorded from wrapped functions, never raced against a clock. The file name carries no
`browser`, so the commit slice and `make test-image` both run it; `tests/process_group.py`
imports no browser driver.
"""

from __future__ import annotations

import contextlib
import os
import signal
import subprocess
from collections.abc import Callable, Iterator
from pathlib import Path

import process_group
import pytest


@contextlib.contextmanager
def _sleeper() -> Iterator[subprocess.Popen[bytes]]:
    """A leader with a group of its own, killed and reaped on the way out whatever happens.

    An un-waited `Popen` is a `ResourceWarning`, an error under `filterwarnings = ["error"]`.
    The class-level `wait` bypasses the recorders a test puts on the instance.
    """
    proc = subprocess.Popen(["sleep", "60"], start_new_session=True)
    try:
        yield proc
    finally:
        # A leader `stop_group` already reaped has a pid the kernel may hand to someone else,
        # and `killpg` on it could reach an unrelated group: the hazard `stop_group` avoids.
        if proc.returncode is None:
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(proc.pid, signal.SIGKILL)
        subprocess.Popen.wait(proc, timeout=5)


def _instrument(
    monkeypatch: pytest.MonkeyPatch,
    proc: subprocess.Popen[bytes],
    read: Callable[[int], list[int]],
) -> list[str]:
    """Fake the reader with `read`; return the list each signal, read, wait and poll lands in."""
    events: list[str] = []
    real_signal = process_group._signal_group

    def signal_group(pgid: int, sig: signal.Signals) -> None:
        events.append(f"signal {sig.name}")
        real_signal(pgid, sig)

    def record_read(pgid: int) -> list[int]:
        events.append("read")
        return read(pgid)

    def wait(timeout: float | None = None) -> int:
        events.append("wait")
        return subprocess.Popen.wait(proc, timeout)

    def poll() -> int | None:
        events.append("poll")
        return subprocess.Popen.poll(proc)

    monkeypatch.setattr(process_group, "_signal_group", signal_group)
    monkeypatch.setattr(process_group, "group_members", record_read)
    monkeypatch.setattr(proc, "wait", wait)
    monkeypatch.setattr(proc, "poll", poll)
    return events


def test_the_group_is_signalled_before_ps_is_read_or_the_leader_reaped(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    with _sleeper() as proc, (tmp_path / "server.log").open("w+b") as log:
        events = _instrument(monkeypatch, proc, lambda _pgid: [])

        process_group.stop_group(proc, log)

        assert events[0] == "signal SIGTERM", events
        assert [e for e in events if e.startswith("signal")] == ["signal SIGTERM"], events
        assert proc.returncode is not None, "the sleep leader is still running"


@pytest.mark.parametrize(
    "error",
    [
        pytest.param(subprocess.CalledProcessError(1, ["ps"]), id="ps-exits-non-zero"),
        pytest.param(FileNotFoundError(2, "No such file or directory", "ps"), id="ps-is-absent"),
        pytest.param(subprocess.TimeoutExpired(["ps"], 5), id="ps-hangs"),
        pytest.param(ValueError("invalid literal for int()"), id="ps-row-is-not-numbers"),
    ],
)
def test_a_failed_ps_fails_the_teardown_with_the_group_already_signalled(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, error: Exception
) -> None:
    def fail(_pgid: int) -> list[int]:
        raise error

    with _sleeper() as proc, (tmp_path / "server.log").open("w+b") as log:
        events = _instrument(monkeypatch, proc, fail)

        with pytest.raises(pytest.fail.Exception, match="survivors unknown"):
            process_group.stop_group(proc, log)

        signals = [e for e in events if e.startswith("signal")]
        assert signals == ["signal SIGTERM", "signal SIGKILL"], events
        assert proc.returncode is not None, "the sleep leader is still running"


def test_ps_is_run_with_a_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """27-REVIEW WR-03: a `ps` that hangs after SIGTERM must not block the teardown for ever,
    so SIGKILL and the reap are never held up. A fake `run` keeps the test off the host's `ps`."""
    seen: dict[str, object] = {}

    def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        seen.update(kwargs)
        return subprocess.CompletedProcess(command, 0, stdout="")

    # The module object is shared, so this is process-wide for the one call below.
    monkeypatch.setattr(subprocess, "run", run)

    assert process_group.group_members(1) == []
    assert seen.get("timeout") is not None, seen
