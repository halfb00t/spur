"""Tests for the two git hooks and the Makefile targets they call.

The commit stage must stay a named prefix of the gate, never a second list of checks
(PITFALLS 14, L13, L36): `make verify` and `make verify.fast` share one `verify.static`
prefix and one pytest recipe, and the hook entries name those targets. A hand-copied
check list drifts; this file is what turns the drift into a red test.

The `$(HOOKS)` stamp must also never rewrite the hooks every checkout shares from a
linked worktree. pre-commit 4.6.2 writes into `git rev-parse --git-common-dir` and bakes
the installing venv's python into the shim, so an install from a worktree would point the
main checkout's hooks at a venv `make worktree.land` deletes.
"""

from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

_MAKE_VARIABLES = ("MAKEFLAGS", "MFLAGS", "MAKELEVEL", "PYTEST_ARGS")
# The files the image suite does not run (26-06): the Makefile comment above `test-image`
# gives each one's reason.
IMAGE_IGNORED = {
    "tests/test_browser.py",
    "tests/test_hooks.py",
    "tests/test_no_fake_done.py",
    "tests/test_browser_pins.py",
    "tests/test_pr_land.py",
    "tests/test_bench.py",
    "tests/test_gear_unchanged.py",
}
HEAVY_TEST_FILES = ("test_model", "test_pool", "test_api", "test_cli", "test_browser")
# The browser stamp, the Makefile's `BROWSER := $(VENV)/.browser`. The commit slice never
# builds it, so on a checkout where it is missing or older than `$(STAMP)` a dry run of
# `verify` prints the install lines that `verify.fast` does not, and the two static
# prefixes differ. `-o` makes make treat the file as old and never remake it, which makes
# the dry run byte-identical wherever the stamp stands (21-RESEARCH Pitfall P2, verified).
BROWSER_STAMP = ".venv/.browser"


def _make_env() -> dict[str, str]:
    """The gate runs this test from inside `make`: the parent's flags and jobserver
    must not leak into the `make` this test starts. Nor may a caller's `PYTEST_ARGS`: a
    caller narrowing the gate sets it in its environment or on the make command line (which
    make exports to the recipe), and a dry run would print it into the recipe these pins
    compare."""
    return {k: v for k, v in os.environ.items() if k not in _MAKE_VARIABLES}


def _clean_git_env() -> dict[str, str]:
    """git in the throwaway repo must not see this repository, nor this host's global
    template (it plants a pre-commit shim into every `git init`). Copied from
    tests/test_no_fake_done.py: three lines beat a cross-test import."""
    env = {k: v for k, v in _make_env().items() if not k.startswith("GIT_")}
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    return env


def _hook_blocks() -> dict[str, str]:
    text = (REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    blocks: dict[str, str] = {}
    for block in text.split("- id: ")[1:]:
        blocks[block.split("\n", 1)[0].strip()] = block
    return blocks


def _dry_run(target: str) -> list[str]:
    result = subprocess.run(
        ["make", "-n", "-o", BROWSER_STAMP, "--no-print-directory", target],
        cwd=REPO_ROOT,
        env=_make_env(),
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.splitlines()


def test_the_commit_hook_runs_the_fast_prefix_and_the_push_hook_runs_the_whole_gate() -> None:
    text = (REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "default_install_hook_types: [pre-commit, commit-msg, pre-push]" in text
    blocks = _hook_blocks()
    assert set(blocks) == {"verify-fast", "verify", "no-skip-token"}

    fast = blocks["verify-fast"].splitlines()
    assert any(line.strip() == "entry: make verify.fast" for line in fast)
    assert any(line.strip() == "stages: [pre-commit]" for line in fast)

    whole = blocks["verify"].splitlines()
    assert any(line.strip() == "entry: make verify" for line in whole)
    assert any(line.strip() == "stages: [pre-push]" for line in whole)

    assert any(
        line.strip() == "stages: [commit-msg]" for line in blocks["no-skip-token"].splitlines()
    )
    for hook_id, block in blocks.items():
        # An unpinned hook gets every installed stage and runs more than once per commit.
        stage_lines = [ln for ln in block.splitlines() if ln.strip().startswith("stages:")]
        assert len(stage_lines) == 1, hook_id


def test_verify_and_verify_fast_share_one_static_prefix_and_one_pytest_recipe() -> None:
    whole = _dry_run("verify")
    fast = _dry_run("verify.fast")

    def split(lines: list[str]) -> tuple[list[str], str]:
        pytest_lines = [ln for ln in lines if " -m pytest " in ln]
        assert len(pytest_lines) == 1, pytest_lines
        at = lines.index(pytest_lines[0])
        # `make -n` prints a backslash-continued recipe as several lines: rejoin it.
        end = at
        while lines[end].endswith("\\"):
            end += 1
        return lines[:at], " ".join(ln.rstrip("\\").strip() for ln in lines[at : end + 1])

    whole_static, whole_pytest = split(whole)
    fast_static, fast_pytest = split(fast)
    assert whole_static == fast_static
    static = "\n".join(whole_static)
    for needle in ("-m ruff check", "-m mypy", "lint-imports", "git grep"):
        assert needle in static, needle

    def through_worker_count(line: str) -> str:
        words = line.split()
        return " ".join(words[: words.index("-n") + 2])

    assert through_worker_count(whole_pytest) == through_worker_count(fast_pytest)
    assert "--cov" in whole_pytest
    # D-06 (26-05): every whole gate prints each test id at start and finish and the 25
    # slowest durations, so a stalled run names its test; the commit slice stays lean.
    assert "-v" in whole_pytest.split()
    assert any(w.startswith("--durations=") for w in whole_pytest.split())
    assert "-v" not in fast_pytest.split()
    assert not any(w.startswith("--durations=") for w in fast_pytest.split())
    assert "--ignore=" not in whole_pytest
    assert "--no-cov" in fast_pytest
    # The whole set, not membership: a fifth `--ignore` would quietly stop the commit
    # stage running that file, and L36 sells the exclusion form because a new test file
    # runs at commit until someone names it heavy.
    ignored = {
        w.removeprefix("--ignore=") for w in fast_pytest.split() if w.startswith("--ignore=")
    }
    assert ignored == {f"tests/{n}.py" for n in HEAVY_TEST_FILES}


def test_both_gates_run_the_gear_safety_check() -> None:
    """D-04 puts `gear.unchanged` in `verify.static`, so a dry run of `verify` and of
    `verify.fast` each print its recipe before the pytest line. Dropping the prerequisite
    would leave `make gear.unchanged` working by hand while no gate ran it, and the shared
    static prefix would still match itself, so the test above cannot see it."""
    for target in ("verify", "verify.fast"):
        lines = _dry_run(target)
        check = [i for i, ln in enumerate(lines) if "-m scripts.gear_unchanged" in ln]
        pytest_at = next(i for i, ln in enumerate(lines) if " -m pytest " in ln)
        assert len(check) == 1, (target, check)
        assert check[0] < pytest_at, target


def test_the_pin_ignores_pytest_args_set_in_the_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A narrowed gate must not turn this pin red (debt item
    2026-10-10-hook-pin-reads-the-callers-pytest-args). `PYTEST_ARGS` in the caller's
    environment reaches the dry run through the Makefile's `PYTEST_ARGS ?=`, so the pin
    compared the caller's flags instead of the recipe; it cost 21-07 one 165 s run."""
    monkeypatch.setenv("PYTEST_ARGS", "--ignore=tests/test_browser.py")
    test_verify_and_verify_fast_share_one_static_prefix_and_one_pytest_recipe()


def test_the_pin_ignores_pytest_args_handed_down_from_the_make_command_line(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`make verify PYTEST_ARGS="--ignore=..."` exports the variable to the recipe, so the
    pin runs with it set. These four are exactly what GNU Make 4.4.1 hands a recipe for a
    command-line variable (measured, 26-RESEARCH Item 1). `_make_env` already strips the
    MAKEFLAGS trio, so this case documents the shape make hands down; `PYTEST_ARGS` is the
    carrier that turns the pin red."""
    monkeypatch.setenv("PYTEST_ARGS", "--ignore=tests/test_browser.py")
    monkeypatch.setenv("MAKEFLAGS", " -- PYTEST_ARGS=--ignore=tests/test_browser.py")
    monkeypatch.setenv("MAKELEVEL", "1")
    monkeypatch.setenv("MFLAGS", "")
    test_verify_and_verify_fast_share_one_static_prefix_and_one_pytest_recipe()


def test_the_whole_gate_installs_the_browser_and_the_commit_slice_never_does() -> None:
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "BROWSER := $(VENV)/.browser" in makefile
    # BROWSER_STAMP above is these two spelled out; if either moves, this fails with it.
    assert re.search(r"^VENV\s+\?= \.venv$", makefile, re.MULTILINE)
    assert BROWSER_STAMP == ".venv/.browser"

    def dry_run_forcing_the_install(target: str) -> list[str]:
        # No `-o` here: `-W` pretends `$(STAMP)` just changed, as a pyproject.toml edit
        # would, so everything that hangs off it is remade, the browser install included.
        return subprocess.run(
            ["make", "-n", "--no-print-directory", "-W", ".venv/.installed", target],
            cwd=REPO_ROOT,
            env=_make_env(),
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()

    whole = dry_run_forcing_the_install("test")
    installs = [i for i, ln in enumerate(whole) if " -m playwright install " in ln]
    assert len(installs) == 1, installs
    assert "--only-shell chromium" in whole[installs[0]]
    pytest_at = next(i for i, ln in enumerate(whole) if " -m pytest " in ln)
    assert installs[0] < pytest_at, "the shell must be installed before the tests run"

    for commit_stage in ("test.fast", "verify.static"):
        lines = dry_run_forcing_the_install(commit_stage)
        assert [ln for ln in lines if "playwright" in ln] == [], commit_stage


def test_the_dev_venv_installs_under_the_closure_and_reinstalls_when_it_moves() -> None:
    """L43: `-c requirements.txt` keeps `make venv` on the pins CI resolves, and the stamp
    depending on that file is what carries a `make lock` to a clone's venv. Drop either and
    the dev venv quietly goes back to an unconstrained resolve (the L34 gap). `-W` pretends
    requirements.txt just changed: the stamp recipe is printed only if it is a prerequisite."""
    lines = subprocess.run(
        ["make", "-n", "--no-print-directory", "-W", "requirements.txt", ".venv/.installed"],
        cwd=REPO_ROOT,
        env=_make_env(),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    install = next((ln for ln in lines if " -m pip install -e " in ln), None)
    assert install is not None, "a changed requirements.txt must re-install the venv stamp"
    assert install.split().count("-c") == 1
    assert "-c requirements.txt" in install, install


def test_the_image_suite_ignores_the_browser_test() -> None:
    """Pins the `test-image` recipe as exact sets (D-13): the read-only mounts, `PYTHONPATH`,
    the pip-installed test tools and the ignored files. The image installs only what the
    runtime needs, so the browser test could not even import there, and the host-only files
    read `make`, git, the Dockerfile or `.github`, none of which the image holds (26-06).
    Sets, not lists: the order of the flags is not the contract. A dry run builds and runs
    nothing; it prints the recipe."""
    lines = _dry_run("test-image")
    at = next(i for i, ln in enumerate(lines) if "docker run" in ln)
    end = at
    while lines[end].endswith("\\"):
        end += 1
    words = shlex.split(" ".join(ln.rstrip("\\").strip() for ln in lines[at : end + 1]))

    mounts = set()
    for host, target, mode in (w.rsplit(":", 2) for w in words if w.startswith(str(REPO_ROOT))):
        mounts.add((Path(host).relative_to(REPO_ROOT).as_posix(), target, mode))
    assert mounts == {
        ("src", "/app/src", "ro"),
        ("tests", "/app/tests", "ro"),
        ("pyproject.toml", "/app/pyproject.toml", "ro"),
        ("bench", "/app/bench", "ro"),
        ("scripts", "/app/scripts", "ro"),
    }, words
    assert words[words.index("-e") + 1] == "PYTHONPATH=/app/src:/app", words

    # pytest-cov and pytest-xdist are here for one test: the forced-GC test in test_pool.py
    # launches `pytest --no-cov -n0` in a subprocess, which fails "unrecognized arguments"
    # without them (26-06, option B).
    script = words[words.index("-c") + 1].split()
    pip = script[script.index("install") + 1 : script.index("&&")]
    tools = {w for w in pip if not w.startswith("-")}
    assert tools == {"pytest", "httpx", "pytest-cov", "pytest-xdist"}, script
    ignored = {w.removeprefix("--ignore=") for w in script if w.startswith("--ignore=")}
    assert ignored == IMAGE_IGNORED, script


def test_the_hook_stamp_installs_from_the_main_checkout_and_never_from_a_linked_worktree(
    tmp_path: Path,
) -> None:
    env = _clean_git_env()
    main = tmp_path / "main"
    main.mkdir()
    shutil.copy(REPO_ROOT / "Makefile", main / "Makefile")
    (main / "pyproject.toml").write_text("", encoding="utf-8")
    (main / "requirements.txt").write_text("", encoding="utf-8")
    (main / ".pre-commit-config.yaml").write_text("repos: []\n", encoding="utf-8")
    git = ["git", "-c", "user.name=probe", "-c", "user.email=probe@example.invalid"]
    subprocess.run(["git", "init", "-q"], cwd=main, env=env, check=True)
    subprocess.run(["git", "add", "."], cwd=main, env=env, check=True)
    subprocess.run([*git, "commit", "-q", "-m", "probe"], cwd=main, env=env, check=True)
    worktree = tmp_path / "wt"
    subprocess.run(["git", "worktree", "add", "-q", str(worktree)], cwd=main, env=env, check=True)

    marker = tmp_path / "installs.txt"
    for checkout in (main, worktree):
        # `$(STAMP)` up to date, so only `$(HOOKS)` has work to do.
        os.utime(checkout / "pyproject.toml", (1_000_000_000, 1_000_000_000))
        os.utime(checkout / "requirements.txt", (1_000_000_000, 1_000_000_000))
        venv = checkout / ".venv"
        (venv / "bin").mkdir(parents=True)
        (venv / ".installed").write_text("", encoding="utf-8")
        shim = venv / "bin" / "pre-commit"
        shim.write_text(f'#!/bin/sh\necho "install $(pwd)" >> "{marker}"\n', encoding="utf-8")
        shim.chmod(0o755)

    main_run = subprocess.run(
        ["make", "-C", str(main), ".venv/.hooks-installed"],
        env=env, capture_output=True, text=True, check=True,
    )
    worktree_run = subprocess.run(
        ["make", "-C", str(worktree), ".venv/.hooks-installed"],
        env=env, capture_output=True, text=True, check=True,
    )

    installs = marker.read_text(encoding="utf-8").splitlines()
    assert len(installs) == 1, installs
    assert os.path.realpath(installs[0].removeprefix("install ")) == os.path.realpath(main)
    assert "linked worktree" not in main_run.stdout
    assert "linked worktree" in worktree_run.stdout
    assert (main / ".venv" / ".hooks-installed").exists()
    assert (worktree / ".venv" / ".hooks-installed").exists()


def test_the_hook_stamp_skips_loudly_when_core_hooks_path_is_set(tmp_path: Path) -> None:
    """pre-commit refuses to install under `core.hooksPath`, which would turn the gate red
    for a reason no code change fixes. The stamp is left untouched so the message repeats."""
    env = _clean_git_env()
    main = tmp_path / "main"
    main.mkdir()
    shutil.copy(REPO_ROOT / "Makefile", main / "Makefile")
    (main / "pyproject.toml").write_text("", encoding="utf-8")
    (main / "requirements.txt").write_text("", encoding="utf-8")
    (main / ".pre-commit-config.yaml").write_text("repos: []\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=main, env=env, check=True)
    subprocess.run(["git", "config", "core.hooksPath", "elsewhere"], cwd=main, env=env, check=True)
    os.utime(main / "pyproject.toml", (1_000_000_000, 1_000_000_000))
    os.utime(main / "requirements.txt", (1_000_000_000, 1_000_000_000))
    venv = main / ".venv"
    (venv / "bin").mkdir(parents=True)
    (venv / ".installed").write_text("", encoding="utf-8")
    marker = tmp_path / "installs.txt"
    shim = venv / "bin" / "pre-commit"
    shim.write_text(f'#!/bin/sh\necho "install" >> "{marker}"\n', encoding="utf-8")
    shim.chmod(0o755)

    run = subprocess.run(
        ["make", "-C", str(main), ".venv/.hooks-installed"],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    assert "core.hooksPath is set" in run.stdout
    assert not marker.exists()
    assert not (venv / ".hooks-installed").exists()
