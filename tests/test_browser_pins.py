"""Pins on the browser test's shape, light enough to run at commit.

A green `make verify` has to mean the browser ran (D-02): the browser test must have no
path that passes, or is skipped, without it. These tests read the browser test's source as
a syntax tree, so they import neither playwright nor the CAD kernel and cost milliseconds
in the commit-time slice, where the browser test itself never runs (D-01).

What each turns red:

- a skip spelling (`importorskip`, `skip`, `skipif`, `xfail`, `pytestmark`, `getenv`), or an
  environment read other than the `SPUR_` scrub and the `PLAYWRIGHT_BROWSERS_PATH` message,
  appearing anywhere in the browser test's modules -- each is a way for a green gate to lie;
  `launch` no longer failing with the literal install command when the shell is missing;
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
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TEST_NAME = "test_the_shipped_viewer_in_a_real_browser"
INSTALL_COMMAND = "playwright install --only-shell chromium"

# Every way a test passes or is skipped without having run, and the two environment reads
# that can change which part is tested.
SKIP_SPELLINGS = frozenset({"importorskip", "skip", "skipif", "xfail", "pytestmark", "getenv"})
ALLOWED_ENVIRON_MARKERS = ("SPUR_", "PLAYWRIGHT_BROWSERS_PATH")
WATCHED = SKIP_SPELLINGS | {"environ"}


def _scan_set() -> list[Path]:
    """The browser test's modules: every `tests/*browser*.py` but this file, and the script
    that regenerates the golden pin, which launches the same browser."""
    found = {p for p in REPO_ROOT.glob("tests/*browser*.py") if p.name != Path(__file__).name}
    found.add(REPO_ROOT / "tests" / "capture_requests.py")
    return sorted(found)


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


def test_the_browser_test_has_no_path_that_passes_without_the_browser() -> None:
    paths = _scan_set()
    names = {p.name for p in paths}
    assert "browser_session.py" in names, names
    defining = [
        p.name
        for p in paths
        if any(
            isinstance(node, ast.FunctionDef) and node.name == TEST_NAME
            for node in ast.walk(_parse(p))
        )
    ]
    assert len(defining) == 1, f"{TEST_NAME} is defined in {defining}, expected exactly one module"

    problems: list[str] = []
    for path in paths:
        lines = path.read_text(encoding="utf-8").splitlines()
        for node in ast.walk(_parse(path)):
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
            if spelled == "environ" and any(m in line for m in ALLOWED_ENVIRON_MARKERS):
                continue
            problems.append(f"{path.name}:{node.lineno}: `{spelled}` in `{line.strip()}`")
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
