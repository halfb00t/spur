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
pattern, so the two checks cannot drift apart. Both call one function, `find_skip_tokens`,
on the text each hands in: the hook's `main` removes what git discards below its cut line
first; `make pr.land` hands in the PR title and body whole, because GitHub records them
verbatim with no git cleanup step at all (CR-01, 05-VERIFICATION.md, Plan 05-06).

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

# git truncates a commit message at this line only in `commit -v`/`commit.verbose` mode
# or with an explicit `--cleanup=scissors` -- never for a plain `-m`/`-F` commit, and
# never for text (like a GitHub PR body) that has no git cleanup step at all. Found by a
# planning probe in a scratch repository: the line is exactly a comment character, one
# space, 24 dashes, one space, `>8`, one space, 24 dashes
# (`# ------------------------ >8 ------------------------`, confirmed byte for byte
# against a real `git commit -v` buffer). The cut is applied by `main` alone, below --
# never inside `find_skip_tokens` -- so a caller whose text never went through git's
# editor is never cut by default (CR-01, 05-VERIFICATION.md, Plan 05-06 Decision (a)).
_SCISSORS = re.compile(r"^# -{24} >8 -{24}$", re.MULTILINE)


def message_to_check(raw: str) -> str:
    """The text above the first scissors line, or all of `raw` when there is none."""
    match = _SCISSORS.search(raw)
    return raw[: match.start()] if match else raw


def find_skip_tokens(message: str) -> list[str]:
    """Every skip token in the whole of `message`, in order of appearance, as the matched
    text -- no cut. Pure -- no I/O, so `pr.land` (Plan 05-02) can call it against a squash
    subject and body with no message-file round trip. The cut is the hook's own step
    (`main`, below), applied only to the editor buffer git hands a commit-msg hook -- a
    body that hid a token below a forged cut line passed the check that used to cut here
    (CR-01, 05-VERIFICATION.md)."""
    return [m.group(0) for m in SKIP_TOKEN.finditer(message)]


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
    # The buffer git hands a commit-msg hook can carry `git commit -v`'s staged diff
    # below the cut line -- cut here, the hook's own step (see `_SCISSORS` above).
    tokens = find_skip_tokens(message_to_check(raw))
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
