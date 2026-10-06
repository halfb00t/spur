"""Tests for `make no-fake-done`, the gate's unfinished-work scan, run against a
throwaway git repository that holds a copy of this repo's `Makefile` and one staged
probe file.

Why a Makefile line gets a test: the scan used to anchor its pattern with `\\b`, and
`git grep -E` hands the pattern to the system regex library, which on macOS does not
implement `\\b` -- a staged file holding both the to-do marker and the not-implemented
exception name passed the scan with exit 1 and no output (homebrew git 2.54.0,
2026-10-05). On the dev host, where the pre-commit hook and every agent's `make verify`
run, the check had passed vacuously since it was written; only CI's Linux git enforced
it. `-w` is git's own whole-word match, the same on both, and this file is what keeps
the next edit of the target from reopening the hole
(docs/tech_debt/resolved/2026-10-05-no-fake-done-scan-is-blind-on-macos.md).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Spelled in halves: this file is itself under the scan it tests, and `-w` sees the
# halves as two ordinary words.
TODO_MARKER = "TO" "DO"
NOT_IMPLEMENTED_MARKER = "NotImplemented" "Error"

# The probe that passed the `\b` scan on macOS: both markers, one staged file.
MARKED_PROBE = f"x = 1  # {TODO_MARKER}: later\nraise {NOT_IMPLEMENTED_MARKER}\n"

# Every marker as a substring of a longer word. Whole-word matching must leave these
# alone, or the scan would refuse legitimate identifiers.
NEAR_MISS_PROBE = (
    f"{TODO_MARKER}S = 2\n"
    f"x{TODO_MARKER} = 3\n"
    f"class {NOT_IMPLEMENTED_MARKER}ish:\n    pass\n"
    "HACKy = 1\n"
)


def _clean_git_env() -> dict[str, str]:
    """git in the throwaway repo must not see this repository. The pre-commit hook that
    runs `make verify` inherits `GIT_INDEX_FILE` (measured: `.git/index`, a relative
    path) and `GIT_PREFIX` from git; carried into the probe's `git add`, they could aim
    it at this repository's own index. `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_NOSYSTEM` keep a
    host's `grep.patternType` or `core.hooksPath` from changing what the scan means."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    return env


def _repo_with_staged_probe(
    tmp_path: Path, probe: str, path: str = "probe.py", *, staged: bool = True,
) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    shutil.copy(REPO_ROOT / "Makefile", repo / "Makefile")
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(probe, encoding="utf-8")
    env = _clean_git_env()
    subprocess.run(["git", "init", "-q"], cwd=repo, env=env, check=True)
    if staged:
        subprocess.run(["git", "add", path], cwd=repo, env=env, check=True)
    return repo


def _run_no_fake_done(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["make", "-C", str(repo), "no-fake-done"],
        env=_clean_git_env(),
        capture_output=True,
        text=True,
        check=False,
    )


def test_a_staged_file_with_both_markers_is_refused_with_each_line_named(
    tmp_path: Path,
) -> None:
    result = _run_no_fake_done(_repo_with_staged_probe(tmp_path, MARKED_PROBE))
    assert result.returncode != 0
    assert "probe.py:1:" in result.stdout
    assert "probe.py:2:" in result.stdout
    assert "unfinished-work markers" in result.stdout


def test_markers_inside_longer_words_pass(tmp_path: Path) -> None:
    result = _run_no_fake_done(_repo_with_staged_probe(tmp_path, NEAR_MISS_PROBE))
    assert result.returncode == 0, result.stdout + result.stderr


# --- the second block: the mypy-suppression pin, scoped to src/spur/ (Phase 16, D-05) -----
# 16-REVIEW WR-02: the pin matched the one spelling `type: ignore` in tracked files, while
# mypy also honours `type:ignore` (no space) and the whole-file `mypy: ignore-errors`, and a
# module not yet `git add`ed is invisible to a plain `git grep`.


def test_a_no_space_type_ignore_under_src_spur_is_refused(tmp_path: Path) -> None:
    repo = _repo_with_staged_probe(
        tmp_path, "x = 1  # type:ignore[attr-defined]\n", "src/spur/probe.py",
    )
    result = _run_no_fake_done(repo)
    assert result.returncode != 0
    assert "src/spur/probe.py:1:" in result.stdout
    assert "a mypy suppression in src/spur" in result.stdout


def test_a_whole_file_ignore_errors_in_an_untracked_module_is_refused(tmp_path: Path) -> None:
    repo = _repo_with_staged_probe(
        tmp_path, "# mypy: ignore-errors\n", "src/spur/probe.py", staged=False,
    )
    result = _run_no_fake_done(repo)
    assert result.returncode != 0
    assert "src/spur/probe.py:1:" in result.stdout


def test_a_deliberate_suppression_outside_src_spur_passes(tmp_path: Path) -> None:
    """tests/test_calc.py and tests/test_cli.py each carry one on purpose (D-05)."""
    repo = _repo_with_staged_probe(
        tmp_path, "x = 1  # type: ignore[arg-type]\n", "tests/probe.py",
    )
    result = _run_no_fake_done(repo)
    assert result.returncode == 0, result.stdout + result.stderr
