"""`make gear.unchanged`: prove no gear link builds a different part than at v0.6 (D-01).

What it proves (REQUIREMENTS.md rule "Same gear, same links"): `tests/regression/`,
`.github/workflows/ci.yml` and the bytes `GET /api/schema` serves are the same as at the
`v0.6` tag. The regression directory holds the L05 fixture and the golden requests, so a
byte of drift there is a gear that moved; the schema is the contract every shareable link
is built against. It runs in every gate (`verify.static`, D-04), so each later phase's
edit of a gear-side file is proved by this check, never by reading the diff.

Why each choice is what it is:

- The baseline is the tag, read at run time; nothing is committed (D-02). A committed
  snapshot would be a second source of truth that someone could regenerate by mistake. For
  the same reason there is no pinned sha: the annotated tag is the one name for v0.6.
- The v0.6 tree is extracted with `git archive`, not checked out as a git worktree. This
  check runs in the pre-commit hook, where git exports GIT_INDEX_FILE, and a worktree added
  there emptied the commit in progress (30-RESEARCH Pitfall 1, scratch repo, 2026-10-23;
  the human chose `git archive`). Every git call here is read-only (`rev-parse`, `diff`,
  `ls-files`, `archive`, and a fetch of the one tag), with `--no-optional-locks`, so the
  index is never written and no worktree is registered.
- Each tree is probed in its own interpreter with PYTHONPATH pointing at its `src` and
  `-P`, and the probe's `spur.__file__` is asserted. The editable install appends this
  repository's src to sys.path; a shadowed import would compare the tree with itself and
  read green forever (Pitfall 2). Two trees cannot share one process either: sys.modules
  would hand the second import the first tree's modules.
- The schema is compared as raw response bytes (D-03), with `Accept-Encoding: identity`:
  GZipMiddleware(minimum_size=1024) compresses the 8.7 KB schema, and a gzip header
  carries an mtime. Bytes also catch key-order and serialisation drift that comparing
  parsed dicts would call equal.
- An untracked file in a watched path counts as a change: `git diff` does not show one
  (Pitfall 6).
- CI checks out shallow, with no tags, and ci.yml may not be edited, so a missing tag is
  fetched from origin (D-05). The fetch is depth 1 only in a shallow clone: a depth-1 fetch
  into a full clone wrote .git/shallow and `git log` went from 3 commits to 2 (reproduced
  at plan time). A failed fetch fails the check naming git's message. It never skips and
  never passes without comparing (L08).
- requirements.txt is not watched; the human chose the two paths at plan time.

Every failure is a SystemExit whose message starts `gear.unchanged: ` and names the cause.
"""

from __future__ import annotations

import argparse
import io
import os
import subprocess
import sys
import tarfile
import tempfile
from collections.abc import Callable
from pathlib import Path

TAG = "v0.6"
WATCHED = ("tests/regression/", ".github/workflows/ci.yml")
REPO_ROOT = Path(__file__).resolve().parents[1]

# Run by the child interpreter, once per tree. stdout carries where spur came from, the
# status and the raw body, in that order, so the parent can check all three.
PROBE = """
import sys
import spur
from fastapi.testclient import TestClient
from spur.app import app

r = TestClient(app).get("/api/schema", headers={"Accept-Encoding": "identity"})
sys.stdout.buffer.write(
    spur.__file__.encode() + b"\\n" + str(r.status_code).encode() + b"\\n" + r.content
)
"""


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "--no-optional-locks", *args],
        cwd=root, capture_output=True, check=False,
    )


def _stderr(done: subprocess.CompletedProcess[bytes]) -> str:
    return done.stderr.decode(errors="replace").strip()


def ensure_tag(root: Path) -> None:
    if _git(root, "rev-parse", "-q", "--verify", f"{TAG}^{{commit}}").returncode == 0:
        return
    shallow = _git(root, "rev-parse", "--is-shallow-repository").stdout.strip() == b"true"
    depth = ["--depth=1"] if shallow else []
    fetched = _git(root, "fetch", *depth, "origin", "tag", TAG)
    if fetched.returncode != 0:
        raise SystemExit(
            f"gear.unchanged: tag {TAG} is not local and could not be fetched from origin: "
            f"{_stderr(fetched)}"
        )


def changed_paths(root: Path) -> list[str]:
    paths: set[str] = set()
    for args in (
        ("diff", "--name-only", TAG, "--", *WATCHED),
        ("ls-files", "--others", "--exclude-standard", "--", *WATCHED),
    ):
        done = _git(root, *args)
        if done.returncode != 0:
            raise SystemExit(f"gear.unchanged: git {' '.join(args)} failed: {_stderr(done)}")
        paths.update(done.stdout.decode().splitlines())
    return sorted(paths)


def schema_of(src: Path) -> bytes:
    done = subprocess.run(
        [sys.executable, "-P", "-c", PROBE],
        env={**os.environ, "PYTHONPATH": str(src)},
        capture_output=True, check=False,
    )
    if done.returncode != 0:
        tail = "\n".join(done.stderr.decode(errors="replace").strip().splitlines()[-5:])
        raise SystemExit(f"gear.unchanged: the probe for {src} failed:\n{tail}")
    where, status, body = done.stdout.split(b"\n", 2)
    if status != b"200":
        raise SystemExit(
            f"gear.unchanged: GET /api/schema answered {status.decode()} for {src}, not 200"
        )
    imported = where.decode()
    if not Path(imported).resolve().is_relative_to(src.resolve()):
        raise SystemExit(
            f"gear.unchanged: the probe for {src} imported spur from {imported}; "
            "refusing to compare a tree with itself"
        )
    return body


def baseline_src(root: Path, dest: Path) -> Path:
    archived = _git(root, "archive", "--format=tar", TAG, "src")
    if archived.returncode != 0:
        raise SystemExit(f"gear.unchanged: git archive {TAG} src failed: {_stderr(archived)}")
    with tarfile.open(fileobj=io.BytesIO(archived.stdout)) as tar:
        # filter="data": a hostile member cannot leave dest.
        tar.extractall(dest, filter="data")
    return dest / "src"


def check(root: Path, probe: Callable[[Path], bytes] = schema_of) -> str:
    ensure_tag(root)
    changed = changed_paths(root)
    if changed:
        raise SystemExit(
            f"gear.unchanged: these watched paths differ from {TAG}: {', '.join(changed)}"
        )
    with tempfile.TemporaryDirectory() as tmp:
        old = probe(baseline_src(root, Path(tmp)))
        new = probe(root / "src")
    if not old or not new:
        # Two empty bodies compare equal; that must never read as a pass.
        raise SystemExit(
            f"gear.unchanged: /api/schema read empty ({len(new)} bytes now, {len(old)} at "
            f"{TAG}); nothing was compared"
        )
    if old != new:
        raise SystemExit(
            f"gear.unchanged: /api/schema bytes differ from {TAG} "
            f"({len(new)} bytes now, {len(old)} at {TAG})"
        )
    return (
        "gear.unchanged: tests/regression/, .github/workflows/ci.yml and /api/schema "
        f"({len(new)} bytes) are byte-equal to {TAG}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scripts.gear_unchanged",
        description=f"Prove the gear regression files and /api/schema bytes equal {TAG}.",
    )
    parser.parse_args(argv)
    print(check(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
