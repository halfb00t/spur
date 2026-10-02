"""Quiet-gated session driver (D-05, D-06): preflight, the quiet wait, server
lifecycle, the runs themselves, and a status.json rewritten atomically at every change.

Launched detached, never run in the foreground: D-05's quiet wait can take up to
`QUIET_CAP_S` (15 minutes) before the runs even start, well past any interactive
command's budget. Nothing here busy-waits a caller -- every wait is bounded and polled.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

# This file sits at <repo>/.planning/phases/13-latency-bar/investigation/session.py --
# four directories below the repository root (same depth as run_experiment.py).
REPO_ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RUN_EXPERIMENT = HERE / "run_experiment.py"
LOCK_PATH = HERE / ".session.lock"
SPUR_BIN = REPO_ROOT / ".venv" / "bin" / "spur"
PYTHON_BIN = REPO_ROOT / ".venv" / "bin" / "python"

sys.path.insert(0, str(REPO_ROOT))

from bench import machine_facts  # noqa: E402

# 8000 is spur-spur-1's port (this repo's own container, left running throughout every
# recorded session); the test server always serves on 8001 (RESEARCH.md Pitfall 1).
BASE_URL = "http://127.0.0.1:8001"
QUIET_BAR = 1.5
SAMPLE_INTERVAL_S = 30
QUIET_RUN = 3
# D-05: bounded the way 12-03's 5-minute cap was, scaled to D-05's own 15 minutes -- a
# session that never reaches three quiet samples still runs, marked non-decisive.
QUIET_CAP_S = 900.0


class _RunFailedError(Exception):
    """A run, a server start, or a server-identity check failed -- the session aborts
    rather than continuing on an unverified server (D-06)."""


def _now_utc() -> str:
    return datetime.now(UTC).isoformat()


def _atomic_write_json(path: Path, data: dict[str, object]) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    tmp.replace(path)


def _append_log(log_path: Path, line: str) -> None:
    with log_path.open("a") as f:
        f.write(f"{_now_utc()} {line}\n")


def _label(text: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9-]+", text):
        raise argparse.ArgumentTypeError(
            f"--label must be letters, digits and hyphens only (got {text!r})")
    return text


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="session",
        description="One quiet-gated session: preflight, D-05's wait, server "
                     "lifecycle, the runs.")
    parser.add_argument("--mode", required=True, choices=["pair", "bar", "composed"])
    parser.add_argument("--label", required=True, type=_label)
    parser.add_argument("--pair", choices=["A", "B", "C"])
    parser.add_argument(
        "--order", default="concurrent,single",
        help="Passed through to run_experiment.py (--mode pair only).")
    parser.add_argument("--quiet-cap", type=float, default=QUIET_CAP_S)
    return parser


def _one_minute_load() -> float:
    out = subprocess.run(["sysctl", "-n", "vm.loadavg"], capture_output=True,
                          text=True, check=True).stdout
    # "{ 1.11 1.85 2.38 }\n" -- the first of the three is the 1-minute figure D-05 gates on.
    return float(out.strip().strip("{}").split()[0])


def _git_head_short() -> str:
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT,
                           capture_output=True, text=True, check=True).stdout.strip()


def _listener_pid(port: int) -> int | None:
    out = subprocess.run(["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"],
                          capture_output=True, text=True).stdout.strip()
    if not out:
        return None
    return int(out.splitlines()[0])


def _docker_state() -> tuple[int, list[str]]:
    info = subprocess.run(["docker", "info"], capture_output=True, text=True)
    docker_ps: list[str] = []
    if info.returncode == 0:
        ps = subprocess.run(["docker", "ps", "-a", "--format", "{{.Names}} {{.Status}}"],
                             capture_output=True, text=True, check=True)
        docker_ps = [line for line in ps.stdout.splitlines()
                     if line.startswith(("spur-spur-1 ", "fleet-user "))]
    return info.returncode, docker_ps


def _fleet_user_busy(docker_info_exit: int) -> bool:
    """D-06: a `docker info` failure means there is no daemon to ask, and fleet-user
    cannot be running without one -- recorded as "docker unavailable", not a block."""
    if docker_info_exit != 0:
        return False
    out = subprocess.run(
        ["docker", "ps", "-a", "--filter", "name=^fleet-user$", "--format", "{{.Status}}"],
        capture_output=True, text=True, check=True).stdout.strip()
    return out.startswith(("Up", "Restarting"))


def _top_cpu() -> list[str]:
    out = subprocess.run(["ps", "-Ao", "%cpu,comm", "-r"], capture_output=True,
                          text=True, check=True).stdout
    return out.splitlines()[:6]


def _start_server(label: str, server_count: int) -> tuple[subprocess.Popen[bytes], int, Path]:
    """Start `.venv/bin/spur serve` detached (its own process group), shipping-default
    `SPUR_*` env (every inherited `SPUR_*` removed first, D-06's env-change precedent),
    wait for a healthy `/api/health`, then confirm the 8001 listener really is this
    child -- never trust that *something* answered on 8001 (T-13-01)."""
    server_count += 1
    log_file = HERE / f"{label}.server{server_count}.log"
    env = {k: v for k, v in os.environ.items() if not k.startswith("SPUR_")}
    env["SPUR_PORT"] = "8001"
    with log_file.open("wb") as log_fh:
        proc = subprocess.Popen(
            [str(SPUR_BIN), "serve"], env=env, stdout=log_fh, stderr=log_fh,
            start_new_session=True, cwd=REPO_ROOT)
    # log_fh is closed here in the parent; the child already holds its own dup'd
    # descriptor from Popen, so this does not truncate or disturb its output.

    deadline = time.monotonic() + 60.0
    healthy = False
    with httpx.Client() as client:
        while time.monotonic() < deadline:
            try:
                response = client.get(f"{BASE_URL}/api/health", timeout=2.0)
                if response.status_code == 200 and response.json().get("pool") is not None:
                    healthy = True
                    break
            except httpx.HTTPError:
                pass
            time.sleep(1.0)

    listener = _listener_pid(8001)
    if not healthy or listener != proc.pid:
        raise _RunFailedError(
            f"server{server_count} did not come up as the expected child "
            f"(listener={listener}, child={proc.pid}, healthy={healthy})")
    return proc, server_count, log_file


def _stop_server(proc: subprocess.Popen[bytes], label: str, server_count: int,
                  log_file: Path) -> int:
    """SIGTERM the process group, SIGKILL on a 30s timeout, wait for the 8001 listener
    to clear, then collapse the full log into spur's own records (every line whose
    `logger` is not `uvicorn.access` -- that line is one per /api/health request, tens
    of thousands per run and a duplicate of the poller's own count)."""
    os.killpg(proc.pid, signal.SIGTERM)
    try:
        proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()

    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline and _listener_pid(8001) is not None:
        time.sleep(0.2)

    kept: list[str] = []
    dropped = 0
    for line in log_file.read_text(errors="replace").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            kept.append(line)  # uvicorn's own startup/shutdown lines are plain text
            continue
        if record.get("logger") == "uvicorn.access":
            dropped += 1
        else:
            kept.append(line)
    records_path = HERE / f"{label}.server{server_count}.records.jsonl"
    records_path.write_text("\n".join(kept) + ("\n" if kept else ""))
    log_file.unlink()
    return dropped


def _run_experiment_leg(label_run: str, order: str, teeth_start: int) -> int:
    stdout_path = HERE / f"{label_run}.stdout.txt"
    stderr_path = HERE / f"{label_run}.stderr.txt"
    with stdout_path.open("wb") as out_f, stderr_path.open("wb") as err_f:
        result = subprocess.run(
            [str(PYTHON_BIN), str(RUN_EXPERIMENT), "--label", label_run,
             "--base-url", BASE_URL, "--order", order, "--teeth-start", str(teeth_start)],
            stdout=out_f, stderr=err_f, check=False)
    return result.returncode


def _run_bar_leg(label_run: str) -> tuple[int, str]:
    """The unmodified harness, no scenario argument, no poller (13-04, D-07) --
    `python -m bench.latency` run exactly as its own `main()` runs it."""
    out_path = HERE / f"{label_run}.txt"
    result = subprocess.run(
        [str(PYTHON_BIN), "-m", "bench.latency", "--base-url", BASE_URL],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    combined = result.stdout + result.stderr
    out_path.write_text(combined)
    return result.returncode, combined


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.mode == "pair" and not args.pair:
        print("error: --pair is required for --mode pair", file=sys.stderr)
        return 2

    label = args.label
    status_path = HERE / f"{label}.status.json"
    log_path = HERE / f"{label}.session.log"

    status: dict[str, object] = {
        "label": label, "mode": args.mode, "pair": args.pair, "order": args.order,
        "state": "preflight", "reason": None, "decisive": None,
        "started_utc": _now_utc(), "finished_utc": None,
        "quiet": {"bar": QUIET_BAR, "cap_s": args.quiet_cap, "samples": [], "released": None},
        "host": {"head": None, "machine": None, "docker_info_exit": None, "docker_ps": None,
                  "top_cpu": None, "server_env": None},
        "runs": [], "load_after": None,
    }

    def abort(reason: str) -> int:
        status["state"] = "aborted"
        status["reason"] = reason
        status["finished_utc"] = _now_utc()
        _atomic_write_json(status_path, status)
        _append_log(log_path, f"aborted: {reason}")
        return 1

    # Checked, and refused, before anything is written for this label -- including
    # status_path itself. `abort()` below writes status_path unconditionally, which
    # would destroy a prior completed run's own status.json the moment this check found
    # it; that is exactly the overwrite E7 forbids. No file for this label is touched
    # when this check fires.
    existing = sorted(p.name for p in HERE.glob(f"{label}.*")) + \
        sorted(p.name for p in HERE.glob(f"{label}-run*"))
    if existing:
        print(f"error: refusing to start -- existing files for this label: {existing}",
              file=sys.stderr)
        return 2

    try:
        LOCK_PATH.touch(exist_ok=False)
    except FileExistsError:
        return abort(f"session lock already exists: {LOCK_PATH}")

    try:
        porcelain = subprocess.run(
            ["git", "status", "--porcelain", "--", "src", "bench"], cwd=REPO_ROOT,
            capture_output=True, text=True, check=True).stdout
        if porcelain.strip():
            return abort(f"src or bench is not at HEAD: {porcelain.strip()}")

        if _listener_pid(8001) is not None:
            return abort("port 8001 already has a listener")

        docker_info_exit, docker_ps = _docker_state()
        if _fleet_user_busy(docker_info_exit):
            return abort("fleet-user is Up or Restarting")

        status["host"]["head"] = _git_head_short()
        status["host"]["machine"] = machine_facts()
        status["host"]["docker_info_exit"] = docker_info_exit
        status["host"]["docker_ps"] = docker_ps
        _atomic_write_json(status_path, status)
        _append_log(log_path, "preflight passed")

        status["state"] = "waiting_quiet"
        _atomic_write_json(status_path, status)
        samples: list[dict[str, object]] = []
        deadline = time.monotonic() + args.quiet_cap
        while True:
            load1 = _one_minute_load()
            samples.append({"utc": _now_utc(), "load1": load1})
            status["quiet"]["samples"] = samples
            _atomic_write_json(status_path, status)
            _append_log(log_path, f"quiet sample load1={load1}")
            recent = samples[-QUIET_RUN:]
            if len(recent) >= QUIET_RUN and all(s["load1"] < QUIET_BAR for s in recent):
                status["decisive"] = True
                status["quiet"]["released"] = True
                break
            if time.monotonic() >= deadline:
                status["decisive"] = False
                status["quiet"]["released"] = False
                break
            time.sleep(SAMPLE_INTERVAL_S)
        status["host"]["top_cpu"] = _top_cpu()
        _atomic_write_json(status_path, status)
        _append_log(log_path, f"quiet wait ended, decisive={status['decisive']}")

        status["state"] = "running"
        _atomic_write_json(status_path, status)

        server_proc: subprocess.Popen[bytes] | None = None
        server_count = 0
        log_file: Path | None = None
        try:
            if args.mode == "pair":
                server_proc, server_count, log_file = _start_server(label, server_count)
                status["host"]["server_env"] = {"SPUR_PORT": "8001"}
                _atomic_write_json(status_path, status)

                run1_label = f"{label}-run1"
                load_before_1 = _one_minute_load()
                exit1 = _run_experiment_leg(run1_label, args.order, 190)
                status["runs"].append(
                    {"label": run1_label, "exit_code": exit1, "load_before": load_before_1})
                _atomic_write_json(status_path, status)
                if exit1 != 0:
                    raise _RunFailedError(f"{run1_label} exited {exit1}")

                if args.pair == "C":
                    dropped = _stop_server(server_proc, label, server_count, log_file)
                    _append_log(log_path, f"server{server_count} stopped, "
                                           f"{dropped} access lines dropped")
                    server_proc, server_count, log_file = _start_server(label, server_count)
                    status["host"]["server_env"] = {"SPUR_PORT": "8001"}
                    _atomic_write_json(status_path, status)

                teeth_start_2 = 180 if args.pair == "B" else 190
                run2_label = f"{label}-run2"
                load_before_2 = _one_minute_load()
                exit2 = _run_experiment_leg(run2_label, args.order, teeth_start_2)
                status["runs"].append(
                    {"label": run2_label, "exit_code": exit2, "load_before": load_before_2})
                _atomic_write_json(status_path, status)
                if exit2 != 0:
                    raise _RunFailedError(f"{run2_label} exited {exit2}")
            elif args.mode == "bar":
                server_proc, server_count, log_file = _start_server(label, server_count)
                status["host"]["server_env"] = {"SPUR_PORT": "8001"}
                _atomic_write_json(status_path, status)

                for n in (1, 2):
                    run_label = f"{label}-run{n}"
                    load_before = _one_minute_load()
                    exit_code, output = _run_bar_leg(run_label)
                    status["runs"].append(
                        {"label": run_label, "exit_code": exit_code, "load_before": load_before})
                    _atomic_write_json(status_path, status)
                    if "Traceback (most recent call last)" in output:
                        raise _RunFailedError(f"{run_label} raised -- see {run_label}.txt")
            else:  # composed (SC3, D-16): one fresh server, one run, no second leg --
                # SC3 is measured once, never retried in search of a different reading.
                server_proc, server_count, log_file = _start_server(label, server_count)
                status["host"]["server_env"] = {"SPUR_PORT": "8001"}
                _atomic_write_json(status_path, status)

                run1_label = f"{label}-run1"
                load_before_1 = _one_minute_load()
                exit1 = _run_experiment_leg(run1_label, "composed", 190)
                status["runs"].append(
                    {"label": run1_label, "exit_code": exit1, "load_before": load_before_1})
                _atomic_write_json(status_path, status)
                if exit1 != 0:
                    raise _RunFailedError(f"{run1_label} exited {exit1}")
        finally:
            if server_proc is not None and log_file is not None:
                dropped = _stop_server(server_proc, label, server_count, log_file)
                _append_log(log_path, f"server{server_count} stopped, "
                                       f"{dropped} access lines dropped")
            status["load_after"] = _one_minute_load()
            _atomic_write_json(status_path, status)
    except _RunFailedError as exc:
        status["state"] = "aborted"
        status["reason"] = str(exc)
        status["finished_utc"] = _now_utc()
        _atomic_write_json(status_path, status)
        _append_log(log_path, f"aborted: {exc}")
        return 1
    finally:
        LOCK_PATH.unlink(missing_ok=True)

    status["state"] = "done"
    status["finished_utc"] = _now_utc()
    _atomic_write_json(status_path, status)
    _append_log(log_path, "done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
