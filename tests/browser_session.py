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
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterator, Mapping
from pathlib import Path
from typing import IO, NamedTuple

import pytest
from playwright.sync_api import Browser, Error, Page, Playwright

# Matches the page's own STL request, whatever its query string.
STL_ROUTE = "**/api/model.stl*"

# SPUR_BUILD_TIMEOUT is 30 s (app.py), so a build-bound wait must outlast it. The first
# preview build read 2.7-3.7 s at host load 8 (21-RESEARCH); if the slowest build-bound step
# on either host reads over 15 s, PD-04 makes this three times that, rounded up to 5 s.
# Slowest build-bound step (`first build drawn`), 2026-10-10: 2.53 s on macOS (21-01, M5 Max,
# load 3-5) and 4.75 s on ubuntu-latest (21-02, run 38044109910, 4 vCPU, the tracer running
# inside `make verify` beside three other xdist workers). Neither is over 15 s, so PD-04 leaves
# the 45 s it started from.
# Phase 22 added the `download name` step (one hob-root build on its own page, then a fine
# re-mesh): 3.56, 3.20 and 1.13 s on macOS (22-02, Apple M2 Max, 1-minute load 6.5-7.0,
# 2026-10-11, `bench/RESULTS.md` "Download name carries the root (Phase 22)"), the slowest
# build-bound step in two of the three runs, `first build drawn` (2.91-2.98 s) in the third.
# Each is under 15 s, so PD-04 still leaves 45 s. Not read on ubuntu-latest here.
BUILD_WAIT_MS = 45_000

# uvicorn plus the shipped pool of 2 workers (D-11, 21-RESEARCH Pattern 1). Seen before the
# kill so that the zero seen after it is a real zero and not a reader that matches nothing.
MIN_GROUP_MEMBERS = 3

# The lower of the hosts' drawn/blank PNG byte ratios divided by 2, rounded down to one
# decimal place (PD-03, written before the reading it is applied to). 21-01's reading:
# blank 3,917 B, drawn 38,908 B, ratio 9.93 (Apple M5 Max, macOS arm64, Chrome Headless
# Shell 153.0.8010.12 on SwiftShader LLVM, 1-minute load 3.3, 2026-10-10, HEAD a310cd3).
# 21-02's reading on ubuntu-latest (ubuntu-24.04 image 20261004.327.1, run 38044109910, the
# same shell on SwiftShader Subzero, 2026-10-10, spike head a6a4fc5): blank 3,654 B, drawn
# 38,168 B, ratio 10.45. The lower of the two is macOS's 9.933; 9.933 / 2 = 4.966, rounded down
# to 4.9, so the bar did not move. A blank canvas reads a ratio near 1.0, a scene with the
# mesh deleted 4.24 (macOS).
PNG_RATIO_BAR = 4.9

# The L05/L26 fixture the sweep reads (never writes) and the pin it is compared with.
FIXTURE_PATH = Path(__file__).with_name("regression") / "pre_v0_2.json"
GOLDEN_PATH = Path(__file__).with_name("regression") / "golden_requests.json"

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


FORM_PAIRS = (
    "() => [...document.querySelectorAll('form#params [name]')].map(e => [e.name, e.value])"
)

# Each dimmed field as [name, the text of its reason], in DOM order (L41).
INACTIVE_PAIRS = (
    "() => [...document.querySelectorAll('form#params label.field.inactive')]"
    ".map(l => [l.querySelector('[name]').name, l.querySelector('.reason').textContent])"
)


def eval_pairs(page: Page, expression: str = FORM_PAIRS) -> list[tuple[str, str]]:
    """The form's (name, value) pairs in DOM order, each value the control's own string.

    `expression` returns a list of two-string lists; the default is the form's controls, and
    `eval_inactive` reads the dimmed fields through the same narrowing.
    """
    value: object = page.evaluate(expression)
    assert isinstance(value, list), f"the form's pairs came back as {value!r}, not a list"
    pairs: list[tuple[str, str]] = []
    for item in value:
        assert isinstance(item, list), f"a form pair that is not a list: {item!r}"
        assert len(item) == 2, f"a form pair that is not a pair: {item!r}"
        name, field_value = item
        assert isinstance(name, str), f"a form pair whose name is not a str: {item!r}"
        assert isinstance(field_value, str), f"a form pair whose value is not a str: {item!r}"
        pairs.append((name, field_value))
    return pairs


def eval_inactive(page: Page) -> dict[str, str]:
    """The fields the page dims right now, name -> the reason text it shows (L41)."""
    return dict(eval_pairs(page, INACTIVE_PAIRS))


def _holds(owner: str, op: object, have: float, wanted: float) -> bool:
    """One relation condition's truth, the grammar's only two ops (D-02), shared by both users."""
    if op == "eq":
        return have == wanted
    if op == "gt":
        return have > wanted
    raise AssertionError(f"{owner}: the op {op!r} is neither 'eq' nor 'gt' (D-02)")


def expected_inactive(properties: Mapping[str, Mapping[str, object]], link: str) -> dict[str, str]:
    """The fields a link must leave dimmed, name -> reason, from the schema alone (D-14).

    The deliberate second implementation of `applyRelations()` in app.js, and it names no
    field: every property's `enabled_when` is read off `/api/schema`, so a relation declared
    later is expected here with no edit. Two evaluators that share no code agreeing over every
    state is the proof. The Phase 21 D-09 rejection of a Python predictor does not apply:
    that was a predictor of what the SERVER answers, where the grammar (D-01..D-03) is the
    spec of this one.

    A field the link omits, or leaves blank, reads as its schema default (D-18: the value the
    page sends). Every condition of a relation is evaluated (PD-05), `eq` and `gt` are the
    only ops, and any other op raises naming it (D-02), as the page's `holds()` does.
    """
    # parse_qsl drops blank values, so an emptied box reads as the default (D-18).
    given = dict(urllib.parse.parse_qsl(link))

    def number(name: str) -> float:
        raw: object = given.get(name, properties[name].get("default"))
        assert isinstance(raw, str | int | float), f"{name}: {raw!r} is not a number"
        assert not isinstance(raw, bool), f"{name}: {raw!r} is a bool, not a number"
        return float(raw)

    def title(name: str) -> str:
        # app.js buildForm(): `prop.title ?? name`.
        found = properties[name].get("title")
        return name if found is None else str(found)

    inactive: dict[str, str] = {}
    for name, prop in properties.items():
        conditions = prop.get("enabled_when")
        if not isinstance(conditions, list) or not conditions:
            continue
        holds: list[bool] = []
        needs: list[str] = []
        for condition in conditions:
            assert isinstance(condition, dict), f"{name}: condition {condition!r} is not an object"
            gate, op, wanted = condition["field"], condition["op"], condition["value"]
            assert isinstance(gate, str), f"{name}: condition field {gate!r} is not a str"
            assert isinstance(wanted, int | float), f"{name}: condition value {wanted!r}"
            assert not isinstance(wanted, bool), f"{name}: condition value {wanted!r} is a bool"
            holds.append(_holds(name, op, number(gate), float(wanted)))
            needs.append(f"{title(gate)} {'=' if op == 'eq' else 'above'} {wanted:g}")
        if False in holds:
            inactive[name] = "Needs " + " and ".join(needs)
    return inactive


def flip_links(properties: Mapping[str, Mapping[str, object]]) -> list[str]:
    """One link per distinct gate condition that makes it differ from the default, from the schema.

    Names no field: for each distinct (field, op, value) across every property's
    `enabled_when`, in order of first appearance, the gate's `minimum + step` and `maximum`
    are tried and the first whose truth differs from the truth at the gate's default is the
    link `field=value`. A fifth relation therefore adds its own link with no test edit (D-15).
    """
    links: list[str] = []
    seen: set[tuple[str, object, float]] = set()
    for owner, prop in properties.items():
        conditions = prop.get("enabled_when")
        if not isinstance(conditions, list):
            continue
        for condition in conditions:
            assert isinstance(condition, dict), f"{owner}: condition {condition!r} is not an object"
            gate, op, wanted = condition["field"], condition["op"], condition["value"]
            assert isinstance(gate, str), f"{owner}: condition field {gate!r} is not a str"
            assert isinstance(wanted, int | float), f"{owner}: condition value {wanted!r}"
            if (gate, op, float(wanted)) in seen:
                continue
            seen.add((gate, op, float(wanted)))
            bounds: dict[str, float] = {}
            for key in ("minimum", "maximum", "step", "default"):
                raw = properties[gate].get(key)
                assert isinstance(raw, int | float), f"{gate}: {key} {raw!r} is not a number"
                bounds[key] = float(raw)
            at_default = _holds(owner, op, bounds["default"], float(wanted))
            flips = [
                candidate
                for candidate in (bounds["minimum"] + bounds["step"], bounds["maximum"])
                if _holds(owner, op, candidate, float(wanted)) != at_default
            ]
            assert flips, f"{gate}: neither minimum + step nor maximum flips {op} {wanted}"
            links.append(f"{gate}={flips[0]:g}")
    return links


def serve_stl_from(page: Page, stl: bytes) -> None:
    """Answer every later STL request with `stl`, the first build's bytes (PD-06).

    On a page that carries this route, every step after the first real build builds nothing
    on the server, so the pool is not asked again and a step's cost is the page's, not the
    kernel's. The `download name` step (Phase 22) opens its own page without this route,
    because it needs the server's Content-Disposition, and builds one more part. The bytes
    must be served and not the
    request aborted: an aborted STL makes `fail()` replace `#messages` with "Request failed:
    ...", which erases the very warnings a step asserts (21-RESEARCH P7).
    """
    page.unroute(STL_ROUTE)
    page.route(STL_ROUTE, lambda route: route.fulfill(status=200, body=stl))


def stl_triangles(stl: bytes) -> int:
    """The triangle count a binary STL declares: a little-endian uint32 after 80 header bytes."""
    assert len(stl) >= 84, f"{len(stl)} bytes cannot hold an STL header"
    count: int = struct.unpack_from("<I", stl, 80)[0]
    return count


def fixture_hash(params: dict[str, object], mate_teeth: int | None) -> str:
    """The link a person would share for one fixture record: its params, then the mate.

    `str(value)` of the JSON value, so `1.0` stays `1.0` the way a person typing it would
    send it; the page's own `gearQuery()` decides what survives (a default is dropped).
    """
    pairs = [(name, str(value)) for name, value in params.items()]
    if mate_teeth is not None:
        pairs.append(("mate_teeth", str(mate_teeth)))
    return urllib.parse.urlencode(pairs)


def fixture_hashes() -> dict[str, str]:
    """Every record of `pre_v0_2.json` as its shareable link, name -> hash, in file order.

    Parsed straight from the JSON: `tests/regression/capture.py` imports the CAD kernel,
    which a browser test must not.
    """
    document: object = json.loads(FIXTURE_PATH.read_text())
    assert isinstance(document, dict), "pre_v0_2.json is not an object"
    records = document["records"]
    assert isinstance(records, dict), "pre_v0_2.json has no records object"
    hashes: dict[str, str] = {}
    for name, record in records.items():
        assert isinstance(record, dict), f"record {name!r} is not an object"
        params = record["params"]
        assert isinstance(params, dict), f"record {name!r} has no params object"
        mate = record.get("mate_teeth")
        assert mate is None or isinstance(mate, int), f"record {name!r}: mate_teeth {mate!r}"
        hashes[name] = fixture_hash(params, mate)
    return hashes


class Swept(NamedTuple):
    """What the page did for one link: the `api/info` query it sent and the fields it dimmed."""

    query: str
    inactive: dict[str, str]


def sweep(page: Page, base: str, hashes: dict[str, str]) -> dict[str, Swept]:
    """The `api/info` query the page sends for each link and the fields it dims, name -> Swept.

    Builds no part: the STL route is aborted, so a link costs one `hashchange` and one
    info request, not a CAD build. `hashchange` calls `readHash(); update()` directly, no
    debounce (app.js:340), so the request is sent as soon as the fragment is assigned;
    21-RESEARCH read 0.09-0.15 s for each of the 43 hash-driven records. The empty link
    cannot be reached that way (an empty fragment is the fresh load's own), so its query is
    the fresh load's request, which is the empty string today.

    The dimmed set is read right after the link's own request, and that is the link's state:
    `readHash()` ends with `applyRelations()` and `update()` sends the request synchronously
    after it, so the state is set before the request this waits for and no response can have
    changed it (23-RESEARCH Pitfall 7).

    A link equal to the live fragment fires no `hashchange`, and the wait would time out
    with a message that names nothing (21-RESEARCH Pitfall P5), so that case raises naming
    the record. The guard reads the live fragment, not the previous record's raw link:
    `update()` rewrites the fragment to the normalised query with `replaceState`.
    Queries are kept exactly as the page's `URLSearchParams` wrote them.
    """
    page.route(STL_ROUTE, lambda route: route.abort())
    with page.expect_request(
        lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
    ) as fresh:
        page.goto(base + "/")
    swept: dict[str, Swept] = {}
    fresh_query = urllib.parse.urlsplit(fresh.value.url).query
    fresh_inactive = eval_inactive(page)
    for name, link in hashes.items():
        if link == "":
            swept[name] = Swept(fresh_query, fresh_inactive)
            continue
        live = eval_str(page, "() => location.hash.slice(1)")
        if live == link:
            raise AssertionError(
                f"{name}: the link {link!r} equals the page's current fragment, so no "
                "hashchange would fire; reorder or separate the records"
            )
        with page.expect_request(
            lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
        ) as request:
            page.evaluate("link => { location.hash = link; }", link)
        swept[name] = Swept(urllib.parse.urlsplit(request.value.url).query, eval_inactive(page))
    return swept


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
