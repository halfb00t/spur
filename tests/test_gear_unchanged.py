"""Tests for `scripts/gear_unchanged.py`, the check behind `make gear.unchanged`.

It runs on scratch git repositories: a real git, a real annotated tag called v0.6, no
network and no edit of this repository. Only the schema probe is replaced by a fake that
reads `src/schema.json`, so `git archive` and the tar extraction run for real while no spur
tree is needed; the two tests at the end drive the real probe. What is pinned is each way
the check can lie: a watched path that moved, a schema that moved by one byte or by key
order, a baseline that could not be read, and a probe that compared a tree with itself.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from scripts.gear_unchanged import REPO_ROOT, check, schema_of
from spur.app import app

IDENTITY = ["-c", "user.name=probe", "-c", "user.email=probe@example.invalid"]
SCHEMA = '{"a": 1, "b": 2}'


@pytest.fixture(autouse=True)
def _clean_git_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """The pre-commit hook exports GIT_INDEX_FILE and the script inherits os.environ, so a
    scratch repo's git would aim at this repository's index (same reason as `_clean_git_env`
    in tests/test_no_fake_done.py: three lines beat a cross-test import)."""
    for name in [k for k in os.environ if k.startswith("GIT_")]:
        monkeypatch.delenv(name)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")


def _git(cwd: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", *IDENTITY, *args], cwd=cwd, capture_output=True, text=True, check=True
    )
    return done.stdout.strip()


def _work_repo(tmp_path: Path) -> Path:
    """A repository shaped like this one: the two watched paths, a `src` holding the
    schema the fake probe serves, one commit, annotated tag v0.6."""
    work = tmp_path / "work"
    for name, text in (
        ("tests/regression/corpus.py", "CORPUS = 1\n"),
        (".github/workflows/ci.yml", "name: ci\n"),
        ("src/schema.json", SCHEMA),
    ):
        (work / name).parent.mkdir(parents=True, exist_ok=True)
        (work / name).write_text(text, encoding="utf-8")
    _git(work, "init", "-q", "-b", "main")
    _git(work, "add", ".")
    _git(work, "commit", "-q", "-m", "v0.6")
    _git(work, "tag", "-a", "v0.6", "-m", "v0.6")
    return work


def _schema_json(src: Path) -> bytes:
    return (src / "schema.json").read_bytes()


def _refused(work: Path, pattern: str) -> None:
    with pytest.raises(SystemExit, match=pattern) as refused:
        check(work, _schema_json)
    assert str(refused.value.code).startswith("gear.unchanged: ")


def test_an_unchanged_tree_reads_green_and_names_what_it_compared(tmp_path: Path) -> None:
    work = _work_repo(tmp_path)

    line = check(work, _schema_json)

    assert line.endswith("are byte-equal to v0.6")
    assert f"({len(SCHEMA)} bytes)" in line
    assert "tests/regression/" in line
    assert ".github/workflows/ci.yml" in line
    assert "/api/schema" in line


def test_an_edited_regression_file_is_named(tmp_path: Path) -> None:
    """A moved regression file is a gear that moved: the fixture is the L05 proof."""
    work = _work_repo(tmp_path)
    with (work / "tests/regression/corpus.py").open("a", encoding="utf-8") as f:
        f.write("MORE = 2\n")

    _refused(work, re.escape("differ from v0.6: tests/regression/corpus.py"))


def test_an_untracked_file_in_the_regression_dir_is_named(tmp_path: Path) -> None:
    """`git diff` does not show a new file, so an added fixture would have read green."""
    work = _work_repo(tmp_path)
    (work / "tests/regression/new.json").write_text("{}", encoding="utf-8")

    _refused(work, re.escape("differ from v0.6: tests/regression/new.json"))


def test_an_edited_ci_workflow_is_named(tmp_path: Path) -> None:
    """ci.yml is what runs the gate; an edit there can loosen it without touching a test."""
    work = _work_repo(tmp_path)
    (work / ".github/workflows/ci.yml").write_text("name: ci\n# edited\n", encoding="utf-8")

    _refused(work, re.escape("differ from v0.6: .github/workflows/ci.yml"))


def test_schema_bytes_that_differ_are_refused(tmp_path: Path) -> None:
    """One changed character is a changed contract: equality is bytes and nothing looser."""
    work = _work_repo(tmp_path)
    (work / "src/schema.json").write_text(SCHEMA.replace("2", "3"), encoding="utf-8")

    _refused(work, re.escape("/api/schema bytes differ from v0.6"))


def test_the_same_schema_with_its_keys_reordered_is_refused(tmp_path: Path) -> None:
    """D-03 compares bytes, not dicts: the same mapping in another key order is drift in
    the route layer that a parsed comparison would call equal."""
    work = _work_repo(tmp_path)
    (work / "src/schema.json").write_text('{"b": 2, "a": 1}', encoding="utf-8")

    _refused(work, re.escape("/api/schema bytes differ from v0.6"))


def test_an_empty_schema_is_never_a_pass(tmp_path: Path) -> None:
    """Two empty bodies are equal; they must read as a failed probe, not as a match."""
    work = _work_repo(tmp_path)

    with pytest.raises(SystemExit, match="read empty"):
        check(work, lambda _src: b"")


def test_a_missing_tag_with_an_unreachable_origin_fails_naming_the_cause(
    tmp_path: Path,
) -> None:
    """D-05: no tag and no way to fetch it is a failure with git's own words, never a skip."""
    lone = tmp_path / "lone"
    lone.mkdir()
    _git(lone, "init", "-q", "-b", "main")
    _git(lone, "commit", "-q", "--allow-empty", "-m", "no tag here")
    _git(lone, "remote", "add", "origin", str(tmp_path / "nowhere"))

    with pytest.raises(SystemExit) as refused:
        check(lone, _schema_json)

    message = str(refused.value.code)
    assert "tag v0.6 is not local and could not be fetched from origin" in message
    assert "does not appear to be a git repository" in message


def test_a_missing_tag_is_fetched_without_making_a_full_clone_shallow(tmp_path: Path) -> None:
    """A depth-1 fetch into a full clone wrote .git/shallow and hid its history (plan-time
    reproduction); the depth is for shallow clones only."""
    work = _work_repo(tmp_path)
    clone = tmp_path / "clone"
    _git(tmp_path, "clone", "-q", "--no-tags", str(work), str(clone))
    assert _git(clone, "tag") == ""

    line = check(clone, _schema_json)

    assert line.endswith("are byte-equal to v0.6")
    assert _git(clone, "rev-parse", "--verify", "v0.6^{commit}")
    assert _git(clone, "rev-parse", "--is-shallow-repository") == "false"


def test_a_shallow_clone_fetches_the_tag_at_depth_one(tmp_path: Path) -> None:
    """CI's checkout is shallow and tagless: the tag arrives at depth 1 and `git archive`
    works there, with the clone still shallow."""
    work = _work_repo(tmp_path)
    clone = tmp_path / "clone"
    _git(tmp_path, "clone", "-q", "--depth=1", "--no-tags", f"file://{work}", str(clone))
    assert _git(clone, "rev-parse", "--is-shallow-repository") == "true"

    line = check(clone, _schema_json)

    assert line.endswith("are byte-equal to v0.6")
    assert _git(clone, "rev-parse", "--is-shallow-repository") == "true"


def test_the_check_leaves_the_repository_as_it_found_it(tmp_path: Path) -> None:
    """The check runs inside the pre-commit hook: a git write there empties the commit in
    progress (30-RESEARCH Pitfall 1). No index change, no worktree, no status change."""
    work = _work_repo(tmp_path)
    (work / "notes.txt").write_text("untracked\n", encoding="utf-8")
    index_before = (work / ".git/index").read_bytes()
    status_before = _git(work, "status", "--porcelain")

    check(work, _schema_json)

    assert (work / ".git/index").read_bytes() == index_before
    assert _git(work, "status", "--porcelain") == status_before
    assert not (work / ".git/worktrees").exists()


def test_the_probe_refuses_a_tree_it_did_not_import(tmp_path: Path) -> None:
    """The editable install satisfies `import spur` from this repository whatever the tree
    asked for; without the location check both probes read the same tree (T-30-02)."""
    empty = tmp_path / "src"
    empty.mkdir()

    with pytest.raises(SystemExit, match="imported spur from"):
        schema_of(empty)


def test_the_probe_reads_the_bytes_the_app_serves() -> None:
    """The probe must carry the identity-encoded response body, not a re-serialisation."""
    served = TestClient(app).get("/api/schema", headers={"Accept-Encoding": "identity"})

    probed = schema_of(REPO_ROOT / "src")

    assert probed
    assert probed == served.content
