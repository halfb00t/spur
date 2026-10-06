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
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

_MAKE_VARIABLES = ("MAKEFLAGS", "MFLAGS", "MAKELEVEL")
HEAVY_TEST_FILES = ("test_model", "test_pool", "test_api", "test_cli")


def _make_env() -> dict[str, str]:
    """The gate runs this test from inside `make`: the parent's flags and jobserver
    must not leak into the `make` this test starts."""
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
        ["make", "-n", "--no-print-directory", target],
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
    assert "--ignore=" not in whole_pytest
    assert "--no-cov" in fast_pytest
    # The whole set, not membership: a fifth `--ignore` would quietly stop the commit
    # stage running that file, and L36 sells the exclusion form because a new test file
    # runs at commit until someone names it heavy.
    ignored = {
        w.removeprefix("--ignore=") for w in fast_pytest.split() if w.startswith("--ignore=")
    }
    assert ignored == {f"tests/{n}.py" for n in HEAVY_TEST_FILES}


def test_the_hook_stamp_installs_from_the_main_checkout_and_never_from_a_linked_worktree(
    tmp_path: Path,
) -> None:
    env = _clean_git_env()
    main = tmp_path / "main"
    main.mkdir()
    shutil.copy(REPO_ROOT / "Makefile", main / "Makefile")
    (main / "pyproject.toml").write_text("", encoding="utf-8")
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
