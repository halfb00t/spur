"""Pins on the browser test's shape, light enough to run at commit.

A green `make verify` has to mean the browser ran (D-02): the browser test must have no
path that passes, or is skipped, without it. These tests read the browser test's source as
a syntax tree, so they import neither playwright nor the CAD kernel and cost milliseconds
in the commit-time slice, where the browser test itself never runs (D-01).

These pins are a tripwire, not a proof: they see the listed spellings and an `environ` read
whose own expression names neither marker. `getattr(pytest, "skip")`, an empty `parametrize` or
a conditional `return` before the first step are not seen (21-REVIEW IN-03).

What each turns red:

- a skip spelling (`importorskip`, `skip`, `skipif`, `xfail`, `pytestmark`, `getenv`), or an
  environment read whose expression holds neither `SPUR_` nor `PLAYWRIGHT_BROWSERS_PATH`,
  appearing anywhere in the browser test's modules (`_scan_set`: the `*browser*` files,
  `capture_requests.py` and the teardown in `process_group.py`) -- each is a way for a green
  gate to lie;
  `launch` no longer failing with the literal install command, and the `make` command that
  reinstalls with the stamp present, when the shell is missing;
- `playwright` no longer pinned with `==` in `[dev]`, or appearing in the runtime closure
  (`[project].dependencies`, `requirements.txt`, the `Dockerfile`,
  `docker/refresh-requirements.sh`): L11 keeps the closure the image installs free of it, and
  an exact pin is what ties the headless-shell revision, and so the canvas bar, to one release;
- `pytest-playwright` declared or importable, or a `channel=` argument anywhere: the plugin
  brings its own fixtures and skip behaviour, and a channel would draw on the host GPU
  where the default shell draws on SwiftShader (D-03).
"""

from __future__ import annotations

import ast
import importlib.util
import re
import sys
import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

TEST_NAME = "test_the_shipped_viewer_in_a_real_browser"
INSTALL_COMMAND = "playwright install --only-shell chromium"
# The stamp `.venv/.browser` re-runs the install only when `pyproject.toml` or
# `requirements.txt` change, so with the stamp present and the shell gone a bare `make test`
# skips the install; removing the stamp is what makes it install (21-REVIEW WR-03).
REINSTALL_COMMAND = "rm -f .venv/.browser && make test"

# Every way a test passes or is skipped without having run, and the two environment reads
# that can change which part is tested.
SKIP_SPELLINGS = frozenset({"importorskip", "skip", "skipif", "xfail", "pytestmark", "getenv"})
ALLOWED_ENVIRON_MARKERS = ("SPUR_", "PLAYWRIGHT_BROWSERS_PATH")
WATCHED = SKIP_SPELLINGS | {"environ"}


def _scan_set() -> list[Path]:
    """The browser test's modules: every `tests/*browser*.py` but this file, the script that
    regenerates the golden pin, which launches the same browser, and the server teardown
    `stop_group`, which the browser test's fixture runs and no `*browser*` glob matches."""
    found = {p for p in REPO_ROOT.glob("tests/*browser*.py") if p.name != Path(__file__).name}
    found.add(REPO_ROOT / "tests" / "capture_requests.py")
    found.add(REPO_ROOT / "tests" / "process_group.py")
    return sorted(found)


def _scan_problems() -> list[str]:
    return [
        problem
        for path in _scan_set()
        for problem in _problems(path.name, path.read_text(encoding="utf-8"))
    ]


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _requirement_name(requirement: str) -> str:
    match = re.match(r"[A-Za-z0-9][A-Za-z0-9._-]*", requirement)
    assert match, f"cannot read a package name from {requirement!r}"
    return match.group().lower().replace("_", "-")


def _pyproject_lists() -> tuple[list[str], list[str]]:
    document = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = document["project"]
    runtime: list[str] = project["dependencies"]
    dev: list[str] = project["optional-dependencies"]["dev"]
    return runtime, dev


def _problems(name: str, source: str) -> list[str]:
    """Each skip spelling, or `environ` read outside the allowance, in one module's source."""
    lines = source.splitlines()
    tree = ast.parse(source, filename=name)
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    problems: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute | ast.Name | ast.ImportFrom):
            continue
        if isinstance(node, ast.Attribute):
            spoken = [node.attr]
        elif isinstance(node, ast.Name):
            spoken = [node.id]
        else:
            spoken = [a.name for a in node.names]
        spelled = next((s for s in spoken if s in WATCHED), "")
        if not spelled:
            continue
        line = lines[node.lineno - 1]
        if spelled == "environ":
            # Equality with a whole string constant in the read's own statement: the `SPUR_`
            # scrub's `k.startswith("SPUR_")` and the launch message's `.get("PLAYWRIGHT_...")`
            # both carry a marker that way, and a marker in a comment or a longer word does not.
            # The climb stops under the statement (or `except` / `case` clause), not at it: a
            # compound statement's node holds its whole body, so a marker anywhere inside an
            # `if` would have allowed a read in its header (27-REVIEW WR-01). A node that is
            # already a statement (`from os import environ`) is its own unit: climbing past it
            # reaches the `Module`, which has no parent, and the scan dies on a `KeyError`
            # instead of reporting the import (27-REVIEW WR-04). It also stops under an
            # `arguments` node, which holds every default of a function: one default's marker
            # must not allow another default's read (27-REVIEW IN-07). A `lambda` is one
            # expression whose parameter list and body are siblings, so it stops there too: a
            # marker in a lambda's defaults must not allow a read in its body (27-REVIEW IN-08).
            expression: ast.AST = node
            clause = ast.stmt | ast.ExceptHandler | ast.match_case | ast.arguments | ast.Lambda
            while not (isinstance(expression, ast.stmt) or isinstance(parents[expression], clause)):
                expression = parents[expression]
            if any(
                isinstance(c, ast.Constant) and c.value in ALLOWED_ENVIRON_MARKERS
                for c in ast.walk(expression)
            ):
                continue
        problems.append(f"{name}:{node.lineno}: `{spelled}` in `{line.strip()}`")
    return problems


def test_an_environ_read_is_allowed_by_its_statement_not_its_line() -> None:
    """21-REVIEW IN-03: the allowance is a marker constant in the read's own expression. A
    marker in a comment on the line must not pass, and a read wrapped over two lines, its
    marker on the second, must."""
    assert len(_problems("a.py", 'import os\nos.environ["X"]  # SPUR_\n')) == 1
    wrapped = 'import os\npath = os.environ.get(\n    "PLAYWRIGHT_BROWSERS_PATH")\n'
    assert _problems("b.py", wrapped) == []


@pytest.mark.parametrize(
    "source",
    [
        pytest.param(
            'import os\nif os.environ.get("CI_NO_BROWSER"):\n    x = "SPUR_"\n',
            id="if-header-marker-in-body",
        ),
        pytest.param(
            'import os\ndef f(a=os.environ.get("SKIP")):\n    return "PLAYWRIGHT_BROWSERS_PATH"\n',
            id="default-argument-marker-in-body",
        ),
        pytest.param(
            'import os\ntry:\n    pass\nexcept os.environ.get("X"):\n    y = "SPUR_"\n',
            id="except-header-marker-in-handler-body",
        ),
        pytest.param(
            'import os\ndef f(a=os.environ.get("SKIP"), b="SPUR_"):\n    pass\n',
            id="default-argument-marker-in-another-default",
        ),
        pytest.param(
            'import os\ng = lambda a=os.environ["SKIP"], b="SPUR_": 0\n',
            id="lambda-default-marker-in-another-default",
        ),
        pytest.param(
            'import os\ng = lambda a="SPUR_": os.environ["SKIP"]\n',
            id="lambda-default-marker-in-the-body-read",
        ),
        pytest.param(
            'import os\ndef f(a=lambda b="SPUR_": os.environ["SKIP"]):\n    pass\n',
            id="nested-lambda-default-marker-in-the-body-read",
        ),
    ],
)
def test_a_marker_outside_the_reads_own_expression_does_not_allow_it(source: str) -> None:
    """27-REVIEW WR-01, IN-07, IN-08: the allowance looks at the read's own expression, never at
    the body of the `if`, `def` or `except` whose header holds the read, nor at a sibling default,
    nor at a lambda's parameter list when the read is in its body."""
    assert len(_problems("c.py", source)) == 1


@pytest.mark.parametrize(
    "source",
    [
        pytest.param("from os import environ\n", id="module-level"),
        pytest.param("def f():\n    from os import environ\n", id="in-a-function"),
    ],
)
def test_an_import_of_environ_is_reported_not_a_crash(source: str) -> None:
    """27-REVIEW WR-04: an `ImportFrom` is a statement and holds no marker constant, so it is
    always one problem. The module-level form used to climb past the statement to the `Module`
    and raise `KeyError`, hiding every other problem in the scan set."""
    assert len(_problems("e.py", source)) == 1


def test_an_environ_read_that_holds_its_own_marker_is_allowed() -> None:
    """The legitimate shape: the marker is inside the read's own expression, whether that sits
    in a header, a default or a lambda body."""
    scrub = 'import os\nif any(k.startswith("SPUR_") for k in os.environ):\n    pass\n'
    assert _problems("d.py", scrub) == []
    own_default = 'import os\ndef f(a=os.environ.get("PLAYWRIGHT_BROWSERS_PATH")):\n    pass\n'
    assert _problems("d.py", own_default) == []
    own_body = 'import os\ng = lambda: any(k.startswith("SPUR_") for k in os.environ)\n'
    assert _problems("d.py", own_body) == []


def test_a_skip_spelling_in_the_server_teardown_module_is_caught(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """27-REVIEW WR-02: `stop_group` moved out of `browser_session.py` into
    `tests/process_group.py`, which no `*browser*` glob matches. The teardown runs in the
    browser test's fixture, so a skip there turns that test into a pass without it running."""
    tests = tmp_path / "tests"
    tests.mkdir()
    for name in ("browser_session.py", "capture_requests.py"):
        (tests / name).write_text("", encoding="utf-8")
    (tests / "process_group.py").write_text(
        'import pytest\n\n\ndef stop_group() -> None:\n    pytest.skip("no ps")\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(sys.modules[__name__], "REPO_ROOT", tmp_path)

    problems = _scan_problems()

    assert len(problems) == 1, problems
    assert problems[0].startswith("process_group.py:5:"), problems


def test_the_browser_test_has_no_path_that_passes_without_the_browser() -> None:
    paths = _scan_set()
    names = {p.name for p in paths}
    assert {"browser_session.py", "process_group.py"} <= names, names
    defining = [
        p.name
        for p in paths
        if any(
            isinstance(node, ast.FunctionDef) and node.name == TEST_NAME
            for node in ast.walk(_parse(p))
        )
    ]
    assert len(defining) == 1, f"{TEST_NAME} is defined in {defining}, expected exactly one module"

    problems = _scan_problems()
    assert not problems, "a path that passes without the browser (D-02): " + "; ".join(problems)

    launch = next(
        node
        for node in ast.walk(_parse(REPO_ROOT / "tests" / "browser_session.py"))
        if isinstance(node, ast.FunctionDef) and node.name == "launch"
    )
    fails = [
        node
        for node in ast.walk(launch)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "fail"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "pytest"
    ]
    assert fails, "launch() must call pytest.fail when the shell cannot start"
    named = [
        node
        for node in ast.walk(launch)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and INSTALL_COMMAND in node.value
    ]
    assert named, f"launch() must name `{INSTALL_COMMAND}` when it fails"
    reinstall = [
        node
        for node in ast.walk(launch)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and REINSTALL_COMMAND in node.value
    ]
    assert reinstall, (
        f"launch() must name {REINSTALL_COMMAND} when it fails: the stamp alone skips the install"
    )


def test_playwright_is_pinned_exactly_in_dev_and_never_in_the_runtime_closure() -> None:
    runtime, dev = _pyproject_lists()
    pins = [r for r in dev if _requirement_name(r) == "playwright"]
    assert len(pins) == 1, f"[dev] holds {pins}, expected exactly one playwright entry"
    assert re.fullmatch(r"playwright==\d+\.\d+\.\d+", pins[0]), (
        f"{pins[0]!r} is not an exact pin: the headless-shell revision, and with it the "
        "canvas bar, moves with the release"
    )
    assert [r for r in runtime if _requirement_name(r) == "playwright"] == [], runtime
    for name in ("requirements.txt", "Dockerfile", "docker/refresh-requirements.sh"):
        text = (REPO_ROOT / name).read_text(encoding="utf-8")
        assert "playwright" not in text.lower(), f"{name} mentions playwright (L11)"


def test_the_browser_test_uses_the_default_headless_shell_and_no_pytest_plugin() -> None:
    _, dev = _pyproject_lists()
    assert [r for r in dev if _requirement_name(r) == "pytest-playwright"] == []
    assert importlib.util.find_spec("pytest_playwright") is None, "pytest-playwright is installed"
    channels = [
        f"{path.name}:{node.lineno}"
        for path in _scan_set()
        for node in ast.walk(_parse(path))
        if isinstance(node, ast.Call) and any(k.arg == "channel" for k in node.keywords)
    ]
    assert not channels, f"channel= selects a shell other than the default one (D-03): {channels}"
