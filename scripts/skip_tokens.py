"""Reject a commit message carrying a GitHub Actions skip token (D-02).

GitHub Actions honours six tokens anywhere in a commit message and silently skips every
workflow run for that commit: `[skip ci]`, `[ci skip]`, `[no ci]`, `[skip actions]`,
`[actions skip]`, and the trailer `skip-checks: true`
(<https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/skipping-workflow-runs>).

Why a commit-time hook, and not only the squash-merge setting (D-03): GitHub applies the
token to a PR's *head* commit too, not only to a push -- a token-carrying ship note left
PR #2's head (`20b63e4`) with zero recorded checks, not a red run. And a literal mention
in *prose* is enough: Phase 4's note "No `[ci skip]` on purpose" (`6fce500`) was itself
skipped and needed the empty trigger commit `87d500e`. Blocking at commit time closes both
holes, for every tool that commits here -- human, `gsd-ship`, or anything else.

This module serves two callers: the `no-skip-token` commit-msg hook below (`main`), and,
from Plan 05-02, `make pr.land`'s check of the squash commit's subject and body -- one
pattern, so the two checks cannot drift apart.

The match is deliberately broader than GitHub's own: case-insensitive, anywhere in the
message. GitHub's documentation does not state a case rule -- over-matching costs a
reworded commit message; under-matching costs a run-less commit on `main` (the actual
failure this phase responds to, `538d26f` and `bfc9110`).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

# The five bracketed phrases, exactly as GitHub writes them (a single space inside the
# brackets), plus the `skip-checks:` trailer with optional whitespace before `true` --
# matched as unanchored substrings, case-insensitive (D-02; see module docstring for why
# case-insensitive is the safe direction to over-match in).
SKIP_TOKEN = re.compile(
    r"\[(?:skip ci|ci skip|no ci|skip actions|actions skip)\]"
    r"|skip-checks:\s*true",
    re.IGNORECASE,
)

# `git commit -v` (or `commit.verbose=true`) hands the commit-msg hook the whole editor
# buffer, including the staged diff below git's own cut line -- discarded by git before
# the commit is recorded. Found by a planning probe in a scratch repository: the line is
# exactly a comment character, one space, 24 dashes, one space, `>8`, one space, 24
# dashes (`# ------------------------ >8 ------------------------`, confirmed byte for
# byte against a real `git commit -v` buffer). Without this cut, a whole-file scan
# refuses a commit whose only token is in the diff of an added file -- and this phase's
# own docs and tests name tokens.
_SCISSORS = re.compile(r"^# -{24} >8 -{24}$", re.MULTILINE)


def message_to_check(raw: str) -> str:
    """The text above the first scissors line, or all of `raw` when there is none."""
    match = _SCISSORS.search(raw)
    return raw[: match.start()] if match else raw


def find_skip_tokens(message: str) -> list[str]:
    """Every skip token in `message_to_check(message)`, in order of appearance, as the
    matched text. Pure -- no I/O, so `pr.land` (Plan 05-02) can call it against a squash
    subject and body with no message-file round trip."""
    return [m.group(0) for m in SKIP_TOKEN.finditer(message_to_check(message))]


def main(argv: list[str] | None = None) -> int:
    """The commit-msg hook entry: `python -m scripts.skip_tokens MESSAGE_FILE`."""
    parser = argparse.ArgumentParser(
        prog="scripts.skip_tokens",
        description="Refuse a commit message carrying a GitHub Actions skip token.",
    )
    parser.add_argument("message_file", help="Path git hands a commit-msg hook")
    args = parser.parse_args(argv)

    # Replace, not raise: an invalid-UTF-8 byte in the message must still be checked --
    # refused if it carries a token, accepted if it does not -- never a traceback.
    raw = Path(args.message_file).read_text(encoding="utf-8", errors="replace")
    tokens = find_skip_tokens(raw)
    if not tokens:
        return 0

    print("make: this commit message carries a GitHub Actions skip token:")
    for token in tokens:
        print(f"      {token!r}")
    print("      A skip token here silences CI on this commit, and on a PR head it")
    print("      leaves the PR with zero checks.")
    print('      Describe it in words instead ("a GitHub Actions skip token") -- do not')
    print("      write the literal token.")
    print(
        "      See docs/tech_debt/resolved/"
        "2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
