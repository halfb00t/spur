---
phase: 05-ci-observed-green
reviewed: 2026-09-25T00:00:00Z
depth: standard
files_reviewed: 23
files_reviewed_list:
  - .github/workflows/ci.yml
  - .github/workflows/required-jobs.txt
  - .pre-commit-config.yaml
  - AGENTS.md
  - docs/architecture/decision_log.md
  - docs/architecture/overview.md
  - docs/architecture/packaging.md
  - docs/CODING_VALUES.md
  - docs/HOW_TO_DEVELOP.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/resolved/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md
  - Makefile
  - pyproject.toml
  - README.md
  - scripts/__init__.py
  - scripts/pr_land.py
  - scripts/skip_tokens.py
  - src/spur/build_errors.py
  - src/spur/params.py
  - src/spur/pool.py
  - src/spur/records.py
  - tests/test_pool.py
  - tests/test_pr_land.py
  - tests/test_skip_tokens.py
findings:
  critical: 1
  warning: 3
  info: 1
  total: 5
status: issues_found
---

# Phase 05: Code Review Report

**Reviewed:** 2026-09-25T00:00:00Z
**Depth:** standard
**Files Reviewed:** 23
**Status:** issues_found

## Summary

Reviewed the CI merge-gate implementation (`scripts/skip_tokens.py`, `scripts/pr_land.py`
and their tests), the CI/pre-commit config, the Python-3.12-only collapse, and the docs
that describe them. `pr_land.py`'s argv discipline is genuinely good — every `gh`/`git`
call travels as a list, never through a shell, so PR-supplied title/body text cannot
reach argument or shell injection; the refusal ordering matches the module's own
docstring exactly; the `--match-head-commit` binding closes the check→merge TOCTOU on the
head sha; and the `required-jobs.txt`/`ci.yml`/ruleset triangle is kept honest by a test
that derives one from the other.

The one finding that matters: `find_skip_tokens`' "scissors" cut — the mechanism both the
commit-msg hook and `pr_land.py`'s squash-message check share by design ("so the two
checks cannot drift apart") — trusts a content-pattern match as proof that everything
below it is git-discarded diff text. That assumption only holds for `git commit -v`'s
auto-activated `cleanup=scissors` mode; it does not hold for a plain `-m`/`-F` commit
(default `cleanup=strip`, which only strips `#`-prefixed lines) and it has **no
applicability at all** to a GitHub PR title/body, which never passes through git's editor
or cleanup machinery. Anyone who reproduces that exact 51-character line in a PR body or
a non-verbose commit defeats the whole check this phase exists to add. Three further
warnings and one info item cover a poll-loop diagnostic that can misattribute a
transient API failure to "a skip token reached main," an unvalidated merge-commit sha,
and a TOCTOU window between the dirty-tree check and the later branch switch/delete.

## Critical Issues

### CR-01: The "scissors" cut lets a skip token survive in the exact text `pr.land` is checking

**File:** `scripts/skip_tokens.py:41-62`, reused unmodified by `scripts/pr_land.py:238-249,402`

**Issue:** `message_to_check()` truncates the text it scans at the *first* line that
matches `^# -{24} >8 -{24}$`, on the stated assumption that git has already discarded
everything past that point ("the staged diff below git's own cut line -- discarded by
git before the commit is recorded", `skip_tokens.py:41-48`). That assumption is only true
for `git commit -v`'s auto-selected `cleanup=scissors` mode. It is false in two ways that
both defeat the check:

1. **Commit-msg hook, non-verbose commits.** `git commit -m "..."` / `-F file` default to
   `cleanup=strip`, which removes only lines that themselves start with `#` — it does
   **not** discard everything after a scissors-shaped line. A message such as:
   ```
   safe subject

   # ------------------------ >8 ------------------------
   [skip ci]
   ```
   committed with a plain `-m`/`-F` (no `-v`, no explicit `--cleanup=scissors`) keeps the
   `[skip ci]` line in the final commit object (it isn't `#`-prefixed, so `strip` leaves
   it alone), while the hook's `message_to_check()` stops scanning at the fake scissors
   line and reports zero tokens, letting the commit through. This string is not obscure —
   it appears verbatim in this module's own docstring (`skip_tokens.py:47`) and in
   `tests/test_skip_tokens.py`, so an agent or human quoting either while writing a commit
   message reproduces it by accident.
2. **`pr_land.py`'s squash-message check.** `message_refusals()` runs the exact same
   `find_skip_tokens()` over `subject + "\n\n" + body` where `body` is `pr.body` — a
   GitHub PR body, which never passes through git's editor, `commit -v`, or any cleanup
   mode at all (`scripts/pr_land.py:238-249,402`). The scissors convention has zero
   meaning there. A PR author who puts the same fake scissors line in the PR description,
   followed by a skip token, produces a squash commit (`gh pr merge --subject ... --body
   ...`, `pr_land.py:409-423`) whose real message on `main` contains the token verbatim —
   while `message_refusals()` silently ignores everything after the decoy line and reports
   no refusal. This is the exact failure mode L22/D-02/D-03 were written to close (a skip
   token reaching `main`'s commit message), reopened through the one checker meant to
   catch it at the last gate before merge.

The existing test `tests/test_skip_tokens.py::test_token_only_below_the_scissors_line_gives_no_tokens`
encodes the vulnerable behavior as the intended one — it is a design assumption, not an
accidental gap, and it is shared by both call sites by construction.

**Fix:** Two independent fixes, either sufficient on its own for `pr_land.py`, both
recommended:

- `pr_land.py`'s `message_refusals()` should never apply the scissors cut at all — a PR
  title/body has no git scissors semantics to respect. Call the token search directly on
  the raw text instead of through `message_to_check()`:
  ```python
  def message_refusals(subject: str, body: str) -> list[str]:
      tokens = [m.group(0) for m in SKIP_TOKEN.finditer(subject + "\n\n" + body)]
      ...
  ```
  (or add a `find_skip_tokens_raw()` / a `cut: bool` parameter to `find_skip_tokens` that
  `pr_land.py` calls with `cut=False`.)
- The commit-msg hook's cut is inherently unsafe against a forged marker in a non-`-v`
  commit. Either drop the truncation and accept the over-match (this project's own stated
  preference: "over-matching costs a reworded commit message; under-matching costs a
  run-less commit on main", `skip_tokens.py:19-22`), or verify `git config --get
  commit.cleanup` actually resolves to `scissors` before trusting the cut, since content
  alone cannot prove which cleanup mode produced it.

This is a stop-and-ask per `CLAUDE.md` ("A library/API behavior is unverified after a
real check"): the docstring's claim about git's own behavior is conditionally true, not
universally true, and the module was built on the universal reading.

## Warnings

### WR-01: The post-merge poll loop reports "a skip token reached main" for API failures too

**File:** `scripts/pr_land.py:440-461`

**Issue:** The polling loop that waits for the squash commit's CI run distinguishes
"the API call itself failed" (`poll_result.returncode != 0`) and "the JSON didn't parse"
(`except ValueError: found_run = None`) from "zero runs exist for this sha" — but treats
all three identically: silently continue to the next attempt, with no stderr surfaced (unlike
`check_head`, which prints `stderr` on every failed read at `pr_land.py:305-349`). If
every poll attempt hits a transient failure (rate limiting, a network blip), the loop
exhausts and prints:
```
pr.land: PR #{pr_number} IS merged as {squash_sha}, but no ci.yml run appeared within
{attempts * interval_s:.0f} s -- a skip token reached main (L22)
```
(`pr_land.py:500-505`) — a specific, actionable-sounding diagnosis that may be entirely
wrong; the actual cause was never "no run", it was "couldn't ask." This is the kind of
plausible-but-unverified claim the project's own standing rule warns against for numbers
("a warning and no number — never a plausible one", `CLAUDE.md`); the same principle
applies to a diagnosis a human will act on.

**Fix:** Track *why* `found_run` stayed `None` and report it distinctly, e.g.:
```python
last_error: str | None = None
for attempt in range(attempts):
    poll_result = run([...])
    if poll_result.returncode != 0:
        last_error = poll_result.stderr.strip()
    else:
        try:
            found_run = newest_run(parse_runs(poll_result.stdout))
        except ValueError as exc:
            last_error = str(exc)
        else:
            if found_run is not None:
                print(found_run.html_url)
                break
    ...
# at timeout:
if last_error is not None:
    print(f"pr.land: the last poll attempt failed: {last_error}")
```

### WR-02: The squash commit sha is used unvalidated, unlike every other parsed value in this module

**File:** `scripts/pr_land.py:429-438`

**Issue:** `squash_sha = squash_sha_result.stdout.strip()` is used directly, with no
check that it is non-empty or shaped like a sha — every other API response in this file
goes through a strict `_as_str`/`_as_int`/`_as_object` boundary check that raises on a
type mismatch (`pr_land.py:104-127`, "A mismatch is always a refusal, never a default").
`gh api ... --jq '.mergeCommit.oid'` prints the literal string `"null"` if `mergeCommit`
is not yet populated on the read immediately following `gh pr merge` (jq's raw output for
a JSON `null`). That value then feeds directly into the poll query's `head_sha=null`
(`pr_land.py:446`), which will find no runs, and the loop times out with the same
misleading "a skip token reached main" message from WR-01 — a plausible-looking, wrong
diagnosis for what is actually a read-after-write timing gap.

**Fix:** Validate `squash_sha` the same way every other parsed value in this module is
validated, and refuse explicitly rather than let an empty/`"null"` value flow into the
poll query:
```python
squash_sha = squash_sha_result.stdout.strip()
if not squash_sha or squash_sha == "null":
    print(f"pr.land: PR #{pr_number} IS merged, but the squash commit sha "
          f"came back empty: {squash_sha_result.stdout!r}")
    return 1
```

### WR-03: A TOCTOU window between the clean-tree check and the branch switch/delete

**File:** `scripts/pr_land.py:393-398` vs `scripts/pr_land.py:464-496`

**Issue:** Step 2 checks the working tree is clean (`git diff --quiet`, `git diff
--cached --quiet`) before `check_head`/merge/poll run — a sequence that can take up to
~60 s (`POLL_ATTEMPTS * POLL_INTERVAL_S`, `pr_land.py:67-68`). Step 6 then runs `git
switch {pr.base}` and, if the local branch's tip matches the merged head, `git branch -D`
— trusting the step-2 clean check, which is now up to a minute stale. If the working tree
picks up new changes during that window (a concurrent edit, another process, a slow
finger), `git switch` may carry them onto `pr.base` silently (when compatible) rather than
refusing, since git's own protection only triggers on an actual conflict. The module
docstring's own reasoning for checking cleanliness at all is "the local follow-up switches
branches" (`pr_land.py:20`) — but the check that justifies doesn't cover the branch this
follow-up actually happens on the far side of a merge and a ~60 s poll.

**Fix:** Re-check the tree is still clean immediately before `git switch` in step 6, or
narrow the window by moving the poll before the clean-tree check (poll first, merge
happens either way once checks pass, then check-clean-and-switch right before switching).
At minimum, note the gap so a future reader doesn't assume step 2's check covers step 6.

## Info

### IN-01: No test coverage for a PR with a null `body`

**File:** `scripts/pr_land.py:130-146`, `tests/test_pr_land.py`

**Issue:** `parse_pull_request` requires `data["body"]` to be a JSON string
(`_as_str(data["body"], "body")`, `pr_land.py:142`) and raises (refuses the whole PR) if
it is `null`. GitHub's PR `body` field can come back `null` for a PR with no description
filled in, depending on API path — this is plausible enough to be worth a fixture, and
the current behavior (refuse the PR entirely rather than treat `null` as `""`) is a
real, user-facing choice: it blocks landing a legitimately empty-description PR with a
"does not parse" error rather than a clear "PR has no description" message. This may be
the intentional fail-closed direction this module already takes everywhere else
(`pr_land.py:98-101`), but it is untested and unremarked, so a future reader can't tell
whether it was chosen or missed.

**Fix:** Add a `PR3_VIEW_JSON`-style fixture with `"body": null` and a test asserting the
refusal, or normalize `null` to `""` in `parse_pull_request` if an empty description
should be landable — either is defensible, but pick one deliberately.

---

_Reviewed: 2026-09-25T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
