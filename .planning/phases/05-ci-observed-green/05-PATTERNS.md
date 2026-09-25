# Phase 5: CI Observed Green - Pattern Map

**Mapped:** 2026-09-25
**Files analyzed:** 16
**Analogs found:** 16 / 16

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|-----------------|---------------|
| `scripts/reject-skip-tokens.sh` (new) | utility (commit-msg hook) | transform (validate text, exit code) | `Makefile`'s `no-fake-done` target | role-match (grep-and-refuse idiom, different host: script vs. Make target) |
| `.pre-commit-config.yaml` (modify) | config | request-response (git hook stage) | itself (existing `verify` hook entry) | exact |
| `tests/test_no_skip_tokens.py` (new) | test | transform | `tests/test_bench.py` | exact (pure-function/no-network test over a small pure predicate, inline literals) |
| `scripts/pr_land.py` (new) | service (pure decision core) | transform (JSON in, bool out) | `bench/memory.py` (`_is_capped`, `_write_mem_limit_override`) | exact (pure predicate over recorded/live JSON-ish data, separated from its I/O shell) |
| `tests/test_pr_land.py` (new) | test | transform | `tests/test_bench.py` | exact |
| `Makefile` (modify: `pr.land` target) | utility (CLI orchestration) | request-response (shell to `gh` API, exit code) | `worktree.land` target | exact (verify-before-land, lock/trap, refuse-and-echo shape) |
| `Makefile` (modify: `PYTHON` loop, `$(STAMP)` error text) | config | — | itself (existing `PYTHON ?=` / `$(STAMP)` block) | exact |
| `.github/workflows/ci.yml` (modify: matrix) | config | — | itself (existing `test.strategy.matrix`) | exact |
| `pyproject.toml` (modify: `requires-python`, ruff `target-version`, mypy comment) | config | — | itself (existing `[tool.ruff]`/`[tool.mypy]` blocks) | exact |
| `README.md` (modify: Python version + CI wording) | config/docs | — | itself (existing L95/L200-212 prose) | exact |
| `docs/HOW_TO_DEVELOP.md` (modify §6, §8) | docs | — | itself (existing §6 "PR", §8 "Влить") | exact |
| `docs/architecture/decision_log.md` (append L22, L23) | docs (append-only log) | event-driven (append) | `L17`/`L18`/`L21` entries (each `supersedes Lxx` heading + Reason paragraph) | exact |
| `docs/tech_debt/INDEX.md` (modify: move row Active→Resolved) | docs | CRUD (row move) | itself (existing Resolved table + the row this file adds/removes) | exact |
| `docs/tech_debt/active/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md` (git mv → `resolved/`) | docs (debt record) | CRUD (status transition) | `docs/tech_debt/resolved/2026-09-21-no-structured-logging.md` | exact |
| `.planning/codebase/CONCERNS.md`, `INTEGRATIONS.md`, `STACK.md` (modify stale CI/Python lines) | docs | — | themselves (existing prose being corrected) | exact |
| `.planning/REQUIREMENTS.md` (modify REQ-ci-verified wording) | docs | — | itself (existing REQ-ci-verified block) | exact |

## Pattern Assignments

### `scripts/reject-skip-tokens.sh` (utility, transform)

**Analog:** `Makefile` lines 61-66 (`no-fake-done` target) — same repo, same refusal tone;
this is the pattern to imitate even though the new file is a standalone script, not a
Make target (D-02 needs it invoked as `entry:` from `.pre-commit-config.yaml` with the
message-file path as `$1`, which a Make target cannot receive).

**Reference shape** (`Makefile:61-66`):
```makefile
no-fake-done: ## refuse unfinished work dressed up as finished
	@if git grep -nE '\b(TODO|FIXME|XXX|HACK|NotImplementedError)\b' \
	     -- '*.py' '*.js' '*.sh' ':!src/spur/static/vendor'; then \
	  echo "make: unfinished-work markers above. Finish it, or file it in docs/tech_debt/."; \
	  exit 1; \
	fi
```

**Pattern to copy:** `grep -E` with the pattern-and-refuse shape — print what matched,
then one or more `echo` lines naming *why* it's rejected and what to do instead, then
`exit 1`. RESEARCH.md's own Code Examples section already has the ported version
(`## Code Examples` → "Skip-token grep") — use it verbatim as the starting point:

```bash
#!/usr/bin/env bash
set -euo pipefail
MSG_FILE="$1"
if grep -iE '\[(skip ci|ci skip|no ci|skip actions|actions skip)\]|skip-checks: ?true' \
     "$MSG_FILE"; then
  echo "make: this commit message carries a GitHub Actions skip token (shown above)."
  echo "      A skip token here silences CI on this commit AND rides into the next"
  echo "      squash-merge message -- see docs/tech_debt/resolved/"
  echo "      2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md."
  exit 1
fi
```

**Security note (V5, RESEARCH.md):** read the message file's content only via `grep
"$MSG_FILE"` (quoted path argument) — never interpolate the message's *content* into a
shell string or `eval` it. The reference shape above already does this correctly.

**Executable bit:** new shell scripts elsewhere in the repo — check
`docker/refresh-requirements.sh` (referenced by `Makefile`'s `lock` target as a bare
invocation) is `chmod +x`; match that (`git ls-files -s docker/refresh-requirements.sh`
shows mode `100755`) so `entry: scripts/reject-skip-tokens.sh` is directly executable
under `language: system`.

---

### `.pre-commit-config.yaml` (config)

**Analog:** itself — the existing single `verify` hook entry.

**Current full file** (`.pre-commit-config.yaml:1-20`):
```yaml
# The gate, at the commit boundary. `make verify` is the same command CI runs and the
# same one `make worktree.land` runs before a merge -- one definition of "passing",
# three places that enforce it.
#
# Install once per clone:  .venv/bin/pre-commit install
# A warm run is ~11 s (the CAD tests dominate). The first run after `make clean` pages
# in ~1.4 GB of OpenCascade and takes a couple of minutes; that is the page cache, not
# the tests.
#
# There is deliberately no formatter hook: see L16 in docs/architecture/decision_log.md.
repos:
  - repo: local
    hooks:
      - id: verify
        name: make verify (ruff, mypy, import boundaries, unfinished-work scan, pytest)
        entry: make verify
        language: system
        pass_filenames: false
        always_run: true
```

**Additions needed (D-02, Claude's Discretion):**
1. A `default_install_hook_types: [pre-commit, commit-msg]` top-level key so the
   documented `pre-commit install` (comment line 5) installs both stages with no change
   to that documented command.
2. A second hook entry under the same `repo: local`, `stages: [commit-msg]`, **no**
   `pass_filenames: false` (the message-file path is the one argument this hook needs —
   RESEARCH.md Pattern 1 states this explicitly), `language: system`, `entry:
   scripts/reject-skip-tokens.sh`.

RESEARCH.md's own Pattern 1 gives the exact merged shape to copy — use it directly
instead of re-deriving the YAML.

---

### `tests/test_no_skip_tokens.py` (test, transform)

**Analog:** `tests/test_bench.py` — full file (44 lines), read in full, exact shape to
copy: module docstring naming the invocation command, `from __future__ import
annotations`, one `test_*` function per case with a one-line docstring naming *which*
real incident/case it pins, inline literal fixtures (no `tests/fixtures/` directory —
RESEARCH.md's Wave-0-gaps note explicitly says not to introduce one).

**Reference shape** (`tests/test_bench.py:1-33`):
```python
"""Pure tests for `bench.memory`'s capping predicate (CR-02 review) -- no Docker daemon
needed; `_is_capped` is a plain function over two byte counts.

Run as `.venv/bin/python -m pytest tests/test_bench.py -q` **from the repo root** -- the
`-m` form is what puts the repo root on `sys.path`...
"""

from __future__ import annotations

import math

from bench.memory import _CAP_TOLERANCE_FRACTION, _SWEEP_MEM_LIMIT_BYTES, _is_capped


def test_a_peak_equal_to_the_ceiling_is_capped() -> None:
    """A sampled peak that reads the ceiling exactly -- what the two capped rows on
    file (bench/RESULTS.md's first sweep attempt) actually read -- is capped."""
    assert _is_capped(_SWEEP_MEM_LIMIT_BYTES, _SWEEP_MEM_LIMIT_BYTES)
```

**What to test (Pitfall 2, Pitfall 3 in RESEARCH.md — hard requirements, not
nice-to-haves):**
- A message with the token in the subject line only.
- A message with the token buried in a later paragraph of the *body* (mirrors `6fce500`'s
  actual shape — a subject-only test would miss the real incident).
- Each of the six token forms individually (`[skip ci]`, `[ci skip]`, `[no ci]`, `[skip
  actions]`, `[actions skip]`, `skip-checks: true`), case-varied on at least one.
- A clean message (no token) passes.

If the hook stays pure bash (per RESEARCH.md's Alternatives Considered recommendation),
this test file drives the script as a subprocess (`subprocess.run(["scripts/reject-skip-tokens.sh",
tmp_msg_path])`, asserting `returncode` and the printed reason) rather than importing
Python — `tests/test_bench.py`'s direct-import shape is the model for a *Python*
hook/module; a bash hook's test instead follows the subprocess-invocation shape already
used for git/gh calls elsewhere in this research (no existing repo analog for
subprocess-testing a script — this is the one file in this phase without a full local
precedent; RESEARCH.md's own Code Examples are the fallback).

---

### `scripts/pr_land.py` (service, transform — pure decision core)

**Analog:** `bench/memory.py` lines 73-79 (`_is_capped`) and lines 272-279
(`_write_mem_limit_override`) — the "pure predicate vs. I/O-heavy orchestrator" split
this repo already uses for exactly the same reason (Claude's Discretion note: "keep the
decision logic ... a pure function tested against recorded `gh` JSON, and the network
shell thin").

**Reference shape** (`bench/memory.py:73-79`):
```python
def _is_capped(peak_bytes: int, ceiling_bytes: int) -> bool:
    """Whether a sampled peak is the sweep's own container ceiling showing up as if it
    were a measurement (CR-02), not a real footprint -- see `_CAP_TOLERANCE_FRACTION`'s
    comment for the record this tolerance is read from. Pure and Docker-free so
    tests/test_bench.py can pin every case without a daemon.
    """
    return peak_bytes >= ceiling_bytes * (1 - _CAP_TOLERANCE_FRACTION)
```

**Module docstring convention to copy** (`bench/memory.py:1-14`): explain *why* the
module exists, cite the decision(s) driving it, and state what it is NOT part of
(`bench/memory.py` states "Not part of `make verify` (D-16)"; `pr_land.py`'s docstring
should equally state it needs network/`gh` auth and is invoked only via `make pr.land`,
never from `make verify`/`make check`).

**Core pattern — RESEARCH.md's own `## Architecture Patterns` → Pattern 2 already gives
the exact functions and literal field shapes to copy** (verified live this session
against the real repo, not invented):
```python
from __future__ import annotations

REQUIRED_JOBS = frozenset({"test (3.12)", "vendor-bundle", "image"})  # D-05, post-D-09

def jobs_are_green(jobs: list[dict[str, str]]) -> bool:
    """`jobs` is the REST `.../actions/runs/<id>/jobs` response's `jobs` array
    (field names `name`, `conclusion` -- confirmed live this session). True only
    when every job in REQUIRED_JOBS is present with conclusion == "success"."""
    by_name = {j["name"]: j["conclusion"] for j in jobs}
    return REQUIRED_JOBS <= by_name.keys() and all(
        by_name[name] == "success" for name in REQUIRED_JOBS
    )

def branch_is_current(compare: dict[str, object]) -> bool:
    """`compare` is `repos/.../compare/main...<sha>`'s response (`behind_by` field).
    D-05 step 2: refuse if behind main."""
    return compare["behind_by"] == 0
```

**Constant-naming convention** (`bench/memory.py:34-37`, `:61`, `:70`): a module-level
`UPPER_SNAKE` constant with a comment citing the decision or measurement that fixed its
value, never a bare magic number — `REQUIRED_JOBS`'s comment above already follows this
(cites D-05, D-09).

**Network shell (thin, around the pure core) — model on `bench/memory.py`'s
`subprocess.run([...], capture_output=True, text=True, check=False)` calls** (e.g.
`_wait_healthy`, lines 90-100): always `check=False` + explicit returncode/stdout
handling, never a bare `check=True` that raises past the caller's own error message.
`pr.land`'s shell must **not** swallow `gh pr merge`'s own exit code (RESEARCH.md Open
Question 2) — propagate it as a refusal.

**Where the shell lives (Claude's Discretion, unresolved by research):** either a
`Makefile` recipe (following `worktree.land`'s shell-in-Make idiom, see below) calling
`.venv/bin/python -m scripts.pr_land` for the network calls, or a `main()` in
`scripts/pr_land.py` itself (mirroring `bench/memory.py`'s own `main()` +
`argparse`/subparsers shape, lines 320-351) invoked from a one-line Make target. Either
satisfies "thin shell, pure core"; pick the one that keeps the Makefile target closest to
`worktree.land`'s existing shape (see next section) for consistency.

---

### `tests/test_pr_land.py` (test, transform)

**Analog:** `tests/test_bench.py` (same as `test_no_skip_tokens.py` above) — direct
import of the pure functions, inline literal fixture dicts sourced from real
recorded/observed API responses (never invented shapes) — RESEARCH.md's `## Architecture
Patterns` → Pattern 2 already provides the literal test file to copy verbatim:

```python
from scripts.pr_land import jobs_are_green, branch_is_current

def test_all_three_named_jobs_green_passes() -> None:
    jobs = [
        {"name": "test (3.12)", "conclusion": "success"},
        {"name": "vendor-bundle", "conclusion": "success"},
        {"name": "image", "conclusion": "success"},
    ]
    assert jobs_are_green(jobs)

def test_a_missing_job_refuses() -> None:
    # PR #2's own recorded shape this session: statusCheckRollup == [] --
    # zero jobs at all, not one failing -- must refuse the same as a red job.
    assert not jobs_are_green([])

def test_one_red_job_refuses() -> None:
    jobs = [
        {"name": "test (3.12)", "conclusion": "failure"},  # run 35993984796's shape
        {"name": "vendor-bundle", "conclusion": "success"},
        {"name": "image", "conclusion": "success"},
    ]
    assert not jobs_are_green(jobs)

def test_branch_up_to_date() -> None:
    assert branch_is_current({"ahead_by": 0, "behind_by": 0, "status": "identical"})

def test_branch_behind_refuses() -> None:
    assert not branch_is_current({"ahead_by": 0, "behind_by": 3, "status": "behind"})
```

Note: every literal in these fixtures traces to a real `gh api` call made during
research (05-RESEARCH.md `## Verified Live State`) — keep that traceability (a comment
citing which call) the way `tests/test_bench.py`'s fixtures cite `bench/RESULTS.md`'s
recorded numbers.

**Import mechanics caveat** (`tests/test_bench.py:4-9`): `bench` is importable only
because `pytest -m pytest` (not a bare `pytest` binary) is run from the repo root, with
no `tests/__init__.py`/`conftest.py` doing path setup. If `scripts/` is a plain directory
(no `pyproject.toml` package listing), the same "run as `.venv/bin/python -m pytest`"
constraint applies to `scripts.pr_land` — state this in the new test file's docstring,
copying `tests/test_bench.py`'s own docstring wording almost verbatim.

---

### `Makefile` — `pr.land` target (utility, request-response)

**Analog:** `worktree.land` (`Makefile:148-167`) — the only existing "verify before you
land" target; same shape, same lock/trap/refuse idiom, next to it per Claude's
Discretion note ("shell in the Makefile ... next to `worktree.land`, whose lock/trap
idiom is the local precedent").

**Reference shape** (`Makefile:148-167`):
```makefile
worktree.land:  ## SLUG=<slug> MSG="<commit>" : verify, squash-merge, remove the worktree
	@test -n "$(SLUG)" || { echo "SLUG= required"; exit 1; }
	@test -n "$(MSG)" || { echo 'MSG= required'; exit 1; }
	@WT=$$(git rev-parse --show-toplevel)/.claude/worktrees/$(SLUG); \
	test -d "$$WT" || { echo "No worktree at $$WT"; exit 1; }; \
	...
	LOCK=$$(git rev-parse --git-dir)/worktree-land.lock; \
	until mkdir "$$LOCK" 2>/dev/null; do echo "another land in progress on $$BASE; waiting..."; sleep 1; done; \
	trap 'rmdir "$$LOCK" 2>/dev/null' EXIT; \
	git diff --quiet && git diff --cached --quiet || { echo "Dirty $$BASE; commit or reset first"; exit 1; }; \
	: "reset --hard HEAD is safe here: ..."; \
	git merge --squash agent/$(SLUG) || { git reset --hard HEAD; echo "CONFLICT ..."; exit 1; }; \
	$(MAKE) verify || { git reset --hard HEAD; echo "verify failed ..."; exit 1; }; \
	git commit -m "$(MSG)"; \
	git worktree remove --force $$WT; \
	git branch -D agent/$(SLUG); \
	echo "landed agent/$(SLUG) on $$BASE"
```

**Pattern to copy for `pr.land PR=N`:**
- `@test -n "$(PR)" || { echo "PR= required"; exit 1; }` — same required-var-guard idiom.
- One `echo "..."; exit 1` per named refusal reason (behind-branch, missing/red job,
  no-run-appeared) — mirrors `worktree.land`'s "one echo per refusal" (role instructions'
  own Step 4 table: Error Handling).
- No `mkdir`/`trap` lock needed here (unlike `worktree.land`, `pr.land` does not mutate
  the local `main` branch's working tree before the merge — the squash happens on
  GitHub's side via `gh pr merge`); only fold in the discretion note's local-branch
  cleanup (`git switch main && git pull --ff-only && git branch -D <branch>`) as the
  final step, mirroring `worktree.land`'s own `git worktree remove` + `git branch -D`
  tail.
- Add the new target's name to the `.PHONY:` line (`Makefile:21-24`) and give it a `##`
  help comment (the `help:` target at line 26-27 greps for these) — every existing target
  has one; `pr.land` must too.
- Add a `## Merge gate --------` section comment banner matching the existing
  `# --- <section> ---` banners (`Makefile:29`, `:44`, `:76`, `:108`, `:120`, `:132`,
  `:169`) — place the new section near `worktree.land`'s or as its own between `# ---
  worktrees ---` and `# --- cleanup ---`.

---

### `Makefile` — `PYTHON` interpreter loop + error text (config)

**Analog:** itself — `Makefile:8-12` (the loop) and `:31-36` (the error message it
feeds).

**Current** (`Makefile:8-12`):
```makefile
# cadquery-ocp publishes wheels for CPython 3.10-3.12 only. Choosing the interpreter
# here instead of using a bare `python3` is what stops pip trying to build OpenCascade
# from source against a newer one and failing several minutes in.
PYTHON ?= $(shell for p in python3.12 python3.11 python3.10; do \
            command -v $$p >/dev/null 2>&1 && { echo $$p; break; }; done)
```
And the error text (`Makefile:32-36`):
```makefile
	@test -n "$(PYTHON)" || { \
	  echo "make: no python3.10-3.12 on PATH."; \
	  echo "      cadquery-ocp has no wheels for anything newer and pip cannot build it."; \
	  echo "      Install one (brew install python@3.12), or use 'make test-image'."; \
	  exit 1; }
```

**D-09 change:** narrow the `for p in ...` loop to `python3.12` only (drop
`python3.11`/`python3.10`), update the comment (drop "3.10-3.12", keep the
wheel-availability reasoning since the *ceiling* reasoning is unchanged per D-09), and
narrow the error text's `"no python3.10-3.12 on PATH"` to `"no python3.12 on PATH"`. Keep
the exact `test -n ... || { echo...; exit 1; }` refusal shape — this is the same
"refuse, explain, exit 1" idiom as `no-fake-done` and `worktree.land`, applied a third
time.

---

### `.github/workflows/ci.yml` — matrix (config)

**Analog:** itself — `.github/workflows/ci.yml:13-14`.

**Current:**
```yaml
      matrix:
        python: ["3.10", "3.12"]
```

**D-09 change:** `python: ["3.12"]` — one-entry list (Claude's Discretion note leaves
open whether to widen back to a bare `python: "3.12"` non-matrix job or keep the
one-entry matrix; keep the matrix form so `pr.land`'s `REQUIRED_JOBS` name
`"test (3.12)"` unchanged — a bare `test` job would rename the required job string and
touch `pr_land.py`'s constant too, more surface for one phase). Everything else in the
`test` job (`.github/workflows/ci.yml:9-24`) is unchanged — `make verify PYTHON=python`
already targets whatever interpreter `actions/setup-python` put on `PATH`.

---

### `pyproject.toml` — `requires-python`, ruff `target-version`, mypy comment (config)

**Analog:** itself.

**`requires-python`** (`pyproject.toml:10`, currently `">=3.10"`) → `">=3.12,<3.13"`
per D-09's exact text (the upper bound is new — "makes L01's ceiling checkable").

**Ruff `target-version`** (`pyproject.toml:38`, currently):
```toml
[tool.ruff]
target-version = "py310"   # cadquery-ocp has no wheels past 3.12; CI runs 3.10 and 3.12
```
→ `target-version = "py312"` with the trailing comment updated to describe the new
single-version reality (drop "CI runs 3.10 and 3.12").

**Mypy comment** (`pyproject.toml:80-84`, currently):
```toml
[tool.mypy]
# 3.12, not the 3.10 floor: numpy's bundled stubs use `type` statements and mypy refuses
# to read them below 3.12. Ruff (target-version = py310) is what holds the language
# floor, and CI runs the suite on a real 3.10 -- so the floor is checked by execution,
# not by the type checker's opinion.
python_version = "3.12"
```
D-09: keep the numpy-stub reason, **drop** the "floor checked by execution" paragraph
(no longer true — mypy's version now equals the only runtime). `python_version = "3.12"`
itself is unchanged. This is the model D-09 itself names ("the mypy comment is the model
for the D-09 rewrite" per CONTEXT.md `<code_context>` → Established Patterns) — match the
existing comment's tone: explain *why*, cite the constraint (CODING_VALUES).

---

### `README.md` (docs)

**Analog:** itself — lines 95, 200-212.

**Line 95:** `Python 3.10+:` → `Python 3.12:`.

**Lines 200-212** (`make venv` help comment and the paragraph explaining `PYTHON ?=`):
```
200: make venv        # .venv with the dev extras (needs CPython 3.10-3.12; see below)
...
207: runs in the pre-commit hook, in CI on Python 3.10 and 3.12, and inside
...
212: Python at all. **`cadquery-ocp` only publishes wheels for CPython 3.10-3.12**, so a
213: newer default `python3` will send pip off trying to build OpenCascade from source;
```
Narrow each "3.10-3.12"/"3.10 and 3.12" to "3.12" (D-09's exact wording: "README Python
3.10+ → 3.12"). Line 207's "CI wording" also ties to D-07 (retire the "never executed"
claim elsewhere — see `.planning/codebase/CONCERNS.md` below, not README itself, per
D-07's file list) — README's own CI mention here is only about which Python versions,
not about whether CI has run.

---

### `docs/HOW_TO_DEVELOP.md` §6 "PR" / §8 "Влить" (docs, Russian — keep language)

**Analog:** itself, current §6 and §8 text (already read in full above).

**§6 "PR" addition (D-04):** one line after the existing paragraph, in Russian, matching
the doc's existing terse imperative style (e.g. "Проверяет верификацию... CI
запускается на PR сам..."). Content: after `/gsd-ship N`, commit `.planning/STATE.md` as
`docs(NN): ship phase N — PR #M` **without** a skip token, then push — because D-02's
hook now rejects the ship note's hardcoded `[ci skip]` commit.

**§8 "Влить" replacement (D-05):** replace "Squash-merge PR on GitHub" instruction with
`make pr.land PR=N` as the sanctioned path; keep the existing local follow-up
(`git switch main && git pull --ff-only origin main && git branch -D
gsd/phase-NN-<slug>`) as *folded into* `pr.land` per Claude's Discretion, but the doc
should still say what `pr.land` does under the hood (mirrors how §0 already explains what
`make verify`/`make check` cover, rather than just naming the command) — match the
existing doc's habit of a short paragraph followed by an example command block (see
the existing §6 "PR" section: a one-line intro, an indented `sh` command block with
`/gsd-ship N`, then a short prose paragraph starting "Проверяет верификацию, ...").
**Also add** the `gh api -X PATCH` command for D-03 (repo squash-merge settings), since
CONTEXT.md's D-03 explicitly places it in "docs/HOW_TO_DEVELOP.md §8 because a repo
setting is not in git":
```sh
gh api -X PATCH repos/halfb00t/spur \
  -f squash_merge_commit_title=PR_TITLE \
  -f squash_merge_commit_message=PR_BODY
```
And the "tool, not a wall" wording D-06/`<specifics>` explicitly asks to be kept — the
web merge button still works; branch protection would be the actual wall and needs a
plan visibility/money change, deferred.

**Keep §0's "Что уже гарантировано" bullet** (`docs/HOW_TO_DEVELOP.md:20-22`, mentioning
"CI... Python 3.10 и 3.12") in sync with D-09 — narrow to "Python 3.12" there too, even
though it is not in the canonical_refs file list explicitly (it is the same claim as
README's, and CLAUDE.md's own consistency expectation covers it).

---

### `docs/architecture/decision_log.md` — append L22, L23 (docs, append-only)

**Analog:** `L17` (`docs/architecture/decision_log.md:163`, "supersedes L07") and `L21`
(`:382`, "supersedes L14") — both show the exact heading-and-body shape for a superseding
entry; `L13` (`:118-126`, "make verify is the gate") is the closest shape for L22 (a
*process/gate* entry, not a *code* entry).

**Heading convention:** `## Lxx — <short description> (supersedes Lyy)` — the
"(supersedes Lyy)" suffix appears **in the heading itself**, not just in prose (see L17,
L18, L21 headings above). L22 does not supersede anything (it's new territory — the merge
gate); L23 supersedes L01's floor specifically: `## L23 — Python 3.12 only (supersedes
L01's floor)`.

**Body convention** (from L21, the most recent and most detailed superseding entry):
short lead paragraph stating what changed and why the old reason no longer holds, then
**bolded sub-headers** in prose (not markdown headers) for each distinct sub-decision
(`**The rule is on globally...**`, `**The house rule**`, `**The two plugin settings...**`
in L21), each with its own one-paragraph justification citing evidence
(commit/run/measurement), ending with a "Reason:" paragraph naming the single most likely
future regression this entry forecloses — L21's closing paragraph
("the single most likely future regression is someone re-adding `Any`...") and L20's
closing paragraph (`docs/architecture/decision_log.md` tail, read above: "the
two-call-site correction... is the single most likely future regression") both do this;
match it.

**L22 must cite** (D-08): PR #2's red merge (run `35993984796` failed `test (3.10)`,
merged five minutes later) and the two run-less squash commits `538d26f`, `bfc9110` —
these are the "Trigger" the entry names, same as L17/L18 cite the measured numbers that
drove them.

**L23 must cite** (D-08, D-09): "detected, not chosen" (L01's own wording — direct quote,
not paraphrase, since L01 says exactly this), the ceiling reasoning is unchanged
(`cadquery-ocp` wheel availability), and the concrete incident
(`logging.StreamHandler[TextIO]`, runs `35993984796`/`36028253714`/`36028759311`, fixed
`990d1fe`) — mirrors how L17/L18/L21 all cite the specific commit/run/measurement that
forced the change, never an abstract justification alone.

**Reversibility note:** several recent entries have no explicit "Reversibility" line;
D-08/D-09's own CONTEXT text already states the reversibility for both L22
("append-only... one-way") and L23 ("costly... a one-line matrix change plus a new log
entry, but..."). Include a `**Reversibility:**` sentence at the end of each new entry's
body — this is not an existing convention in L13-L21 but CONTEXT.md's own text for D-08/
D-09 already reads as if written for that slot; carry it over verbatim rather than
dropping it to match the older entries' silence.

---

### `docs/tech_debt/INDEX.md` (docs, CRUD — row move)

**Analog:** itself — the existing `## Resolved` table (`docs/tech_debt/INDEX.md:28-34`)
and the row to remove from `## Active` (`:20`).

**Current Resolved table shape:**
```markdown
## Resolved

| Item | Resolved in |
|---|---|
| [CAD builds block the event loop](resolved/2026-09-21-cad-builds-block-the-event-loop.md) | `daeb284` -- see the file's own `Resolved in:` field |
```

**Action:** remove the row `| must | [The ship-note's CI skip token leaks...` from
`## Active` (`docs/tech_debt/INDEX.md:20`), add a new row to `## Resolved` with the same
`[Item](resolved/<same-filename>.md) | `<sha>` — see the file's own `Resolved in:` field`
shape — the sha is filled in by the fix commit itself (same-commit resolution, D-11).

---

### `docs/tech_debt/active/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md` → `resolved/` (docs, CRUD)

**Analog:** `docs/tech_debt/resolved/2026-09-21-no-structured-logging.md` (full file, 59
lines, read above) — the exact shape for turning an active debt file into a resolved one.

**Header field changes** (mirrors the analog's own header, `:1-6`):
```
Severity: must
Status: resolved
Date: 2026-09-25
Resolved in: <the fix commit's sha>
```
(`Resolved in:` is a **new** field added at resolution time — the analog shows it sits
right after `Status:`/`Date:`, before `Source:`.)

**Body addition:** a new `## Resolution (2026-09-25)` section appended after the
existing `## Next step` section (never edit the existing `## Context`/`## Why it
matters`/`## Next step` sections in place — the analog's resolution section is purely
additive, and per the analog's own footnote pattern ("resolves this file and makes the
documentation... true... a file cannot carry its own commit's sha" — the analog's own
caveat about referencing its own commit) note whether the resolving commit is the same
one that carries `Resolved in:` or a distinguishable one.

**Content to cite in `## Resolution`:** the hook + its test (D-02), the `gh api -X PATCH`
setting change (D-03), and `pr.land`'s post-merge check as "the standing verification the
file's 'Next step' asks for" (D-11's own wording) — mirrors the analog's resolution
section citing the specific commit, the specific mechanism, and a test proving it
(`caplog`-based tests, in the analog's case).

**Move mechanic:** `git mv docs/tech_debt/active/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md docs/tech_debt/resolved/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md` — same filename, only the directory changes (matches every existing resolved file's naming: date stays the *original* filing date, not the resolution date — `2026-09-21-no-structured-logging.md` was resolved 2026-09-24 per its own `Date:`/resolution date split).

---

### `.planning/codebase/CONCERNS.md`, `INTEGRATIONS.md`, `STACK.md` (docs)

**Analog:** themselves — exact lines identified this session:

- `CONCERNS.md:221` — `**CI:** ... **Note:** The workflow has never executed in a GitHub
  Actions environment — it was hand-verified during setup but not yet proven in CI.` →
  replace the "Note" sentence with the retirement text (D-07): cite run `35963114939`
  (main push, `59f02c3`) and `36088409707` (PR #3 head, `2c4b544`), both green on all
  four jobs. Also update `CONCERNS.md:184` (`Full gate runs on Python 3.10 and 3.12 via
  CI`) and `:215` (`pinned to 3.10–3.12 in pyproject.toml`) for D-09.
- `INTEGRATIONS.md:63-78` (`## CI/CD & Deployment` section) — `:67` and `:73` both say
  "Python 3.10 and 3.12"; narrow to "3.12" (D-09). No "never executed" claim exists here
  to retire (unlike CONCERNS.md), but CONTEXT.md's canonical_refs still names this file
  for D-07 — treat it as the Python-version correction only, unless a broader CI-status
  claim is found nearby at execution time.
- `STACK.md:13-15` — `Python 3.10–3.12 ... Ruff targets 3.10 (L01); CI runs both 3.10 and
  3.12` → `Python 3.12 ... Ruff targets 3.12 (L23, superseding L01's floor); CI runs
  3.12`. Also `STACK.md`'s `## Runtime` section, `CPython 3.10–3.12 (server and CLI)` (a
  few lines below the excerpt read this session) needs the same narrowing.

**Pattern:** all three are prose corrections, not structural changes — copy the sentence
shape already there, replace only the version numbers/claim, keep everything else
(headers, surrounding bullets) untouched, per CLAUDE.md's "surgical edits" rule.

---

### `.planning/REQUIREMENTS.md` — REQ-ci-verified (docs)

**Analog:** itself, `.planning/REQUIREMENTS.md:147-152`.

**Current:**
```markdown
- [ ] **REQ-ci-verified**: `.github/workflows/ci.yml` is observed executing green in GitHub
  Actions on both supported Python versions — not hand-verified step-by-step.
  - *Retires*: the "CI workflow unverified" blocker carried in `STATE.md` since the
    2026-09-21 bootstrap (source: `docs/plan-2026-09-21.md`).
  - *Acceptance*: a run URL, on a real push, showing the gate and both container checks
    green. Predicting that it would pass is not the same as watching it pass (L13).
```

**Change (D-07, D-09):** "on both supported Python versions" → "on the supported Python
version" (singular, post-D-09); the `*Acceptance*` line's "both container checks" phrase
is about `vendor-bundle`/`image`, not Python versions — leave that phrase itself
unchanged, only the "both supported Python versions" wording in the main bullet. Keep the
`- [ ]` → `- [x]` checkbox flip for whichever mechanism this repo's `.planning/` tooling
uses to mark a requirement met (check `REQUIREMENTS.md`'s own existing `[x]` rows
elsewhere in the file for the exact marker convention before flipping it).

---

## Shared Patterns

### "Refuse, explain, exit 1" — the one Makefile idiom every new target/check reuses
**Source:** `Makefile` — `no-fake-done` (`:61-66`), `$(STAMP)`'s python guard (`:32-36`),
`worktree.land` (`:148-167`), `worktree.new`'s SLUG guard (`:138-139`)
**Apply to:** `scripts/reject-skip-tokens.sh`, the narrowed `PYTHON` loop's error text,
and every refusal branch inside `pr.land` (behind-branch, missing/red job, no-run-appeared).
```makefile
@test -n "$(REQUIRED_VAR)" || { echo "reason"; exit 1; }
```
or, for a check that runs a command and inspects its output:
```makefile
@if <condition-that-should-not-be-true>; then \
  echo "make: <what's wrong, shown above/below>"; \
  echo "      <why it matters / what to do>"; \
  exit 1; \
fi
```

### Pure-core / thin-shell split for anything touching an external system with no offline test
**Source:** `bench/memory.py` (`_is_capped`, `_write_mem_limit_override` vs. `sweep()`/
`confirm()`), tested by `tests/test_bench.py`
**Apply to:** `scripts/pr_land.py`'s `jobs_are_green`/`branch_is_current` (pure, tested
offline against recorded JSON) vs. the `gh api`/`gh pr merge` calls (untested, thin,
network-dependent) — same shape, same reason ("the live GitHub API has no offline test").

### Decision-log entries are append-only, dated, and named in their own heading when superseding
**Source:** `docs/architecture/decision_log.md` — `## L17 ... (supersedes L07)`, `## L18
... (supersedes L06)`, `## L21 ... (supersedes L14)`
**Apply to:** the new `## L22` and `## L23 — ... (supersedes L01's floor)` entries — never
edit L01/L13 in place, only point at them from the new heading and body.

### Debt resolution: same-commit `Status: resolved` + `git mv` + INDEX row move
**Source:** `docs/tech_debt/resolved/2026-09-21-no-structured-logging.md` (full file) +
`docs/tech_debt/INDEX.md`'s `## Resolved` table
**Apply to:** `docs/tech_debt/active/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md`
— per D-11 and CLAUDE.md's "Capturing ideas and debt" section, all three edits (file
header, `## Resolution` section, `git mv`, INDEX row) land in the same commit as the hook
+ setting fix, never a follow-up commit on `main`.

### Module/constant documentation: cite the decision or measurement that fixed a value
**Source:** `bench/memory.py`'s `_SWEEP_MEM_LIMIT_BYTES`, `SHIPPING_DEFAULT_WORKERS`,
`_CAP_TOLERANCE_FRACTION` (each has a paragraph-length comment citing D-17/D-18/D-19 and
a measured number, never a bare literal)
**Apply to:** `scripts/pr_land.py`'s `REQUIRED_JOBS` (already modeled above, citing
D-05/D-09) and any other constant the plan introduces (e.g. a poll interval/timeout for
step 5's ~60s wait — cite D-05's own "~60 s" figure and the ~3 min full-run measurement
from RESEARCH.md's `## Verified Live State`, not an invented number).

## No Analog Found

None — every file in this phase's scope has a close, git-tracked analog in the existing
codebase (see table above). The one partial exception is `tests/test_no_skip_tokens.py`
if the hook stays pure bash: there is no existing repo precedent for a pytest file that
subprocess-invokes a shell script (every existing test either imports a Python module
directly or drives the ASGI app in-process) — RESEARCH.md's own Code Examples section is
the fallback source for that one file's shape, not a codebase analog.

## Metadata

**Analog search scope:** `Makefile`, `.pre-commit-config.yaml`, `bench/`, `tests/`,
`pyproject.toml`, `.github/workflows/`, `docs/tech_debt/`, `docs/architecture/`,
`docs/HOW_TO_DEVELOP.md`, `README.md`, `.planning/codebase/`, `.planning/REQUIREMENTS.md`,
`docker/smoke.py`
**Files scanned:** 16 (all git-tracked, verified via `git ls-files`)
**Pattern extraction date:** 2026-09-25
