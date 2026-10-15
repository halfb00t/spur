---
phase: 25-gate-bar-re-set-venv-probe-ledger-close
plan: 04
subsystem: testing
tags: [gate, bar, decision-log, L43, venv, pip-constraint, debt]

requires:
  - phase: 25
    provides: "25-03's readings record, the GREEN venv probe and `Candidate bar (D-05): none`; 25-01's rule commit 1d5ce8a"
provides:
  - "bench/RESULTS.md `#### Gate decision`: the human's verbatim answer, `Candidate bar (D-05): none`, `Bar: 300 s`"
  - "docs/architecture/decision_log.md L43 (amends L34): the bar, the method, the readings, the knee, the probe, the widened CI sentence"
  - "Makefile `$(STAMP): pyproject.toml requirements.txt` with `pip install -e '.[dev]' -c requirements.txt`"
  - "The stale 63.555 s / ~64 s gate figures rewritten to cite L43 in five files; IN-03 closed by subject"
affects: [phase-25-close, gate, make-venv]

actuals:
  tokens: 12722      # chars/4 over `git diff 8bb1a24 HEAD` (50888 chars, kept logs included)
  tasks: 3           # Task 1 answered at the checkpoint; Tasks 2 and 3 produced the one commit
  commits: 1         # measured: git rev-list --count 8bb1a24..HEAD at SUMMARY write (the metadata commit comes after)
plan_head_before: 8bb1a24d5a4b228191cee78033a827894e51ce1e
plan_head_after: 34270c8946f0bedb90920de6c79fd051ac326fdb

tech-stack:
  added: []
  patterns:
    - "A bar the rule could not compute is the human's number, recorded verbatim beside the rule's own `none`"

key-files:
  created:
    - "docs/ideas/retired/2026-10-03-constrain-make-venv-to-the-closure.md (git mv from docs/ideas/)"
    - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/investigation/25-04-hooks-red.log"
    - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/investigation/25-04-hooks.log"
    - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/investigation/25-04-readme.log"
    - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/investigation/25-04-verify.log"
  modified:
    - "docs/architecture/decision_log.md"
    - "bench/RESULTS.md"
    - "Makefile"
    - ".pre-commit-config.yaml"
    - "docs/HOW_TO_DEVELOP.md"
    - "README.md"
    - "docs/architecture/packaging.md"
    - "docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md"
    - "docs/tech_debt/INDEX.md"
    - "docs/ideas/INDEX.md"
    - "tests/test_hooks.py"

key-decisions:
  - "The gate bar is 300 s on the 18-CPU Apple M5 Max, set by the human; the rule's candidate is `none`; no check enforces it (L43)"
  - "L34's CI sentence widens to every environment that claims to run the gate, with the pip 26.2 caveat that hatchling builds unconstrained (L43)"

patterns-established:
  - "One Lxx carries the bar, the probe outcome and the stale-figure rewrite, so L34 is amended once"

requirements-completed: [REQ-gate-bar-reset, REQ-venv-constraint-probe]

duration: 2h
completed: 2026-10-14
status: complete
---

# Phase 25 Plan 04: The gate bar and L43 Summary

**L43 amends L34 with a 300 s bar the human set on the 18-CPU Apple M5 Max (the rule's candidate was `none`), and `make venv` now installs under `requirements.txt` as a constraint after a green probe.**

## Performance

- **Duration:** about 2 h across two executors (the first stopped at the bar checkpoint; this one ran from 2026-10-14T14:08Z)
- **Completed:** 2026-10-14
- **Tasks:** 3 (Task 1 the human's checkpoint, Tasks 2 and 3 as one commit)
- **Files modified:** 16 in the L43 commit (12 outside `.planning/`)

## The human's answer (Task 1)

Verbatim, 2026-10-14 (time of day not recorded; the continuation was spawned about 14:08Z):

`Let's set 300 s. IMHO it's a reasonable bar`

Candidate: `Candidate bar (D-05): none` (neither arm has a decisive green run). Bar: **300 s**, read as the plan's `other 300 <reason>`
with the reason being the human's words. GREEN probe applied. The readings behind it: A1 195.23 s and B1 179.21 s, both
non-decisive (waits waived by the human), and the probe's 270.35 s, which is not a reading.

## Accomplishments

- `bench/RESULTS.md` `#### Gate decision` holds the verbatim answer, the `none` candidate, `Bar: 300 s`, the give-up/short-arm note and the "no check enforces it" sentence; `### The rule (25-01)` is byte-identical to the rule commit.
- L43 is the last entry of `docs/architecture/decision_log.md`: method (D-01..D-06, D-21), readings (n = 0 per arm, the two non-decisive runs quoted as measured), the bar, the unswept knee (`PYTEST_WORKERS` 8, "Form follow-ups"), the probe, the widened CI sentence and the pip 26.2 caveat, `**Reversibility.**`, `Reason:`, `Machine:`.
- `Makefile`: `$(STAMP): pyproject.toml requirements.txt` and `$(PY) -m pip install -e '.[dev]' -c requirements.txt`, with a comment; the `--upgrade pip` line is unchanged. `make -n -W requirements.txt .venv/.installed` prints the constrained install.
- `tests/test_hooks.py`: the two throwaway-repo tests write and `os.utime` a `requirements.txt`; seen `2 failed, 4 passed` first, then `6 passed`.
- Stale gate figures rewritten to cite L43 and the bar with its host in `Makefile` (`verify` and `test.fast` comments), `.pre-commit-config.yaml`, `docs/HOW_TO_DEVELOP.md` (section 0 and section 6), `README.md` line 307 and `docs/architecture/packaging.md`; README line 96 (the 29.42 s composed gear) is untouched.
- IN-03 closed by this commit's subject in the Phase 19 debt file (still `Status: active` for IN-01, IN-02, IN-04); the venv idea retired to `docs/ideas/retired/` with its INDEX row.

## Task Commits

1. **Tasks 2 and 3 (one commit by design, D-14):** `34270c8` -- `docs(25): log L43 -- the gate bar re-set on an idle host amends L34, stale gate figures rewritten, IN-03 closed`

**Plan metadata:** the `docs(25-04): complete ...` commit follows this file.

## Verification

- Stale-figure search `grep -n -E '63\.555|~64 s|about 64 s' Makefile .pre-commit-config.yaml docs/HOW_TO_DEVELOP.md README.md docs/architecture/packaging.md`: empty output, grep rc 1 (the negated plan check exits 0).
- `make verify` on the tree that was committed (kept as `investigation/25-04-verify.log`): `1317 passed in 153.47s (0:02:33)`, `make verify exit 0`, wall 155 s, coverage `TOTAL 1358 22 386 13 97.99%`, "Required test coverage of 96.0% reached". Not a gate reading. `pre-commit install` re-ran first (the config changed); `.git/hooks/pre-commit` line 6 afterwards reads `INSTALL_PYTHON=/Users/half/git/halfb00t/spur/.venv/bin/python`.
- README pins: `make test exit 0` (`2 passed, 118 deselected`).
- Task 3 checks run as written: `one L43 commit 34270c8 : 16 paths; probe GREEN ; IN-03 closed by subject`; the negated grep exits 0; the regression-fixture diff is empty and no tracked file was left modified.
- The commit hook ran `make verify.fast` and the skip-token check: both Passed. `git show --diff-filter=D` listed no deletions (the idea is a rename).
- Moved since the rule commit outside `.planning/`: only `tests/test_hooks.py` among `src docker scripts requirements.txt pyproject.toml tests .github`.

## Decisions Made

- The bar is 300 s, the human's, bound to the 18-CPU Apple M5 Max and `HEAD` `9b68f6d`; the figure is recorded, not enforced.
- The venv adoption (GREEN branch) goes in L43, not a second Lxx, so L34 is amended once.

## Deviations from Plan

### Plan verify scripts that did not pass as written

**1. [Task 2 verify] The `other <N>` pattern cannot read a free-text answer.**
The script matches `re.match(r'\s*other\s+([0-9]+)', answer)` on the quoted verbatim answer. The human wrote `Let's set 300 s. IMHO it's a reasonable bar`, which does not begin with `other`, and the candidate is `none`, so the script stops at its `none`-candidate assertion. Output of the plan's script, run unedited:

```
  File ".../scratchpad/t2.py", line 15, in <module>
    assert cand.group(1) or other, 'the candidate is none: only other <N> <reason> gives a bar (D-04)'
AssertionError: the candidate is none: only other <N> <reason> gives a bar (D-04)
```

The quoted answer was not altered to satisfy the pattern (that would falsify "verbatim"). Everything after that assertion was run in a scratch copy in which only the `other` match was replaced by reading `300` from `set ([0-9]+) s`; it printed `gate decision recorded ( Let's set 300 s. IMHO it's a reasonable bar ); L43 holds 26 items; probe GREEN`. The plan file was not edited.

**2. [Rule 3 - Blocking] The red hook log did not contain make's message.**
The plan's check wants `No rule to make target 'requirements.txt'` in `25-04-hooks-red.log`. Pytest raises `CalledProcessError` naming only exit status 2 and hides make's stderr, so the log had `2 failed, 4 passed` but not the sentence. I appended, labelled as such, the same throwaway repo run by hand without a `requirements.txt` (`make: *** No rule to make target 'requirements.txt', needed by '.venv/.installed'.  Stop.`). The plan's script then passes.

### Other notes

- The attribution line on the commit is `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`, taken from the session's attribution reminder; the continuation brief named `Claude Fable 5.1`. The reminder was followed.
- The `Makefile` `verify` comment keeps "about 11 s of repeated work on L34's gate" as history, as the plan allows, and drops the old gate-wall wording.

**Total deviations:** 2 (one verify script that presumes an `other` answer, one log supplement). **Impact:** none on the recorded bar or L43.

## Issues Encountered

None beyond the two verify points above. The first executor reached the bar checkpoint and stopped; no file had been edited.

## Known Stubs

None.

## Threat Flags

None: the commit changes docs, one Makefile recipe line and two test fixtures; no new endpoint, auth path or trust boundary.

## Tangents raised for the human

- **Four-versus-five heavy files drift (not edited, not filed):** `README.md:315` and `docs/HOW_TO_DEVELOP.md:25-27` still say four heavy files while the slice ignores five (`tests/test_browser.py` was added by L39). `docs/architecture/packaging.md`'s `make verify.fast` row names four files as well. Real drift, outside this phase's brief.
- The linked-worktree `agent/venv-probe` branch was already deleted at the human's word (25-03).

## Filed or moved

No debt or idea was filed. Moved: `docs/ideas/2026-10-03-constrain-make-venv-to-the-closure.md` to `docs/ideas/retired/` (planned, with its INDEX rows). Closed in place: IN-03 in `docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md`.

## Next Phase Readiness

- Phase 25 has its four plans done; phase verification is next. Existing `.venv` directories keep their resolve until `make clean && make venv` (D-13), so the main checkout's venv is still the pre-adoption one.

## Self-Check: PASSED

- FOUND: docs/architecture/decision_log.md (`## L43 — ` is the last heading, no `## L44`), bench/RESULTS.md `#### Gate decision`, docs/ideas/retired/2026-10-03-constrain-make-venv-to-the-closure.md, the four `investigation/25-04-*` logs
- FOUND: commit 34270c8 is an ancestor of HEAD
