---
phase: 25-gate-bar-re-set-venv-probe-ledger-close
reviewed: 2026-10-14T00:00:00Z
depth: standard
files_reviewed: 15
files_reviewed_list:
  - .ai_skills/reverify-phase/SKILL.md
  - .pre-commit-config.yaml
  - Makefile
  - README.md
  - bench/RESULTS.md
  - docs/HOW_TO_DEVELOP.md
  - docs/architecture/decision_log.md
  - docs/architecture/packaging.md
  - docs/ideas/INDEX.md
  - docs/ideas/retired/2026-09-22-measure-or-soften-the-pi5-claim.md
  - docs/ideas/retired/2026-09-28-reverify-after-post-verification-fixes.md
  - docs/ideas/retired/2026-10-03-constrain-make-venv-to-the-closure.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md
  - tests/test_hooks.py
findings:
  critical: 0
  warning: 3
  info: 5
  total: 8
status: issues_found
---

# Phase 25: Code Review Report

**Reviewed:** 2026-10-14
**Depth:** standard (phase diff `1864bcd..HEAD`; `bench/RESULTS.md` and `decision_log.md` reviewed as diff only)
**Files Reviewed:** 15
**Status:** issues_found

## Summary

The executable change is small and correct. Checks I ran:

- `$(STAMP): pyproject.toml requirements.txt` and `-c requirements.txt` are both relative to make's cwd, as is the neighbouring `-e '.[dev]'`. In a linked worktree `requirements.txt` is a tracked file, so it exists there; in the main checkout it is the same. Neither case has a path or ordering bug.
- `.venv/bin/python -m pip install --dry-run -e '.[dev]' -c requirements.txt` on this host (macOS arm64) resolved. It would move only fastapi, fonttools, starlette and uvicorn, which are the four moves the probe predicted.
- `tests/test_hooks.py`: both throwaway-repo fixtures now supply `requirements.txt` and `os.utime` it, and the venv stamp is written after the utime, so `$(STAMP)` stays up to date and only `$(HOOKS)` has work. `25-04-hooks-red.log` shows the failure without the file (`No rule to make target 'requirements.txt'`) and `25-04-hooks.log` shows `6 passed`. The worktree copy gets the file from the committed fixture. The fixtures still exercise what they claim.
- Numbers trace to `bench/RESULTS.md` and the investigation logs: 195.23 s (A1) and 179.21 s (B1), 270.35 s (probe), `1315`/`1317 passed`, 97.99 % coverage, 18 vs 12 CPUs, the 31 pins (`grep -c '==' requirements.txt` gives 31), and the 300 s bar quoted verbatim from the human.
- No live 66 s / 64 s / 63.555 s gate figure survives outside historical records. The remaining hits are `decision_log.md` L34/L36 and L39 history, resolved debt files, and `Makefile:190`, which is the `verify.fast` re-pricing and not the gate.
- The `reverify-phase` skill's mechanics hold up on this host. GSD is 1.16.0, `gsd_run query verification.status <dir>` returns `status` and `next_command`, `resolve-model gsd-verifier` works, #4682 is cited in the installed `execute-phase.md`, and Phase 24's report reads `Re-verification: Yes ... (#4682)`.

The findings below are about missing proof for the shipped Makefile line and about what the docs leave out of the 300 s bar. None is a defect in a printed number.

## Warnings

### WR-01: No test covers the shipped `-c requirements.txt` or the new stamp prerequisite

**File:** `Makefile:49`, `Makefile:57`; `tests/test_hooks.py:179-240`
**Issue:** The only test change makes two fixtures survive the new prerequisite. Nothing asserts that `$(STAMP)` depends on `requirements.txt` or that the install line carries `-c requirements.txt`. A later edit that drops either one would pass `make verify`, and `make venv` would silently go back to an unconstrained resolve. That would undo L43 and reopen the L34 gap between CI and developer hosts with no signal. CLAUDE.md says new behavior ships with its tests. `tests/test_hooks.py:139-142` already has the pattern: a dry run with `-W .venv/.installed` whose recipe lines are inspected.
**Fix:** Add a dry-run test next to the existing ones:
```python
def test_the_venv_stamp_installs_under_the_closure() -> None:
    lines = _dry_run("-W", "requirements.txt", ".venv/.installed")  # adapt to the helper's signature
    install = next(ln for ln in lines if " -m pip install -e " in ln)
    assert "-c requirements.txt" in install, install
```
A second dry run could assert that `touch requirements.txt` makes `.venv/.installed` stale, for example with `make -n -q`.

### WR-02: L43 and RESULTS word the adoption proof and the build-constraint caveat as observed when they are inferred

**File:** `docs/architecture/decision_log.md` L43 ("The venv probe", about line 2899-2907); `bench/RESULTS.md` "The venv probe (25-03)", "Readings" and "Outcome"
**Issue:** Two claims read stronger than the evidence behind them (CLAUDE.md L08: no claim of a measurement that was not taken).
1. The probe ran `make venv` with `PIP_CONSTRAINT=<absolute path>/requirements.txt` in the environment, on the pre-change Makefile. The shipped recipe is `-c requirements.txt`, a relative path. It was never run by a probe. L43 says "`PIP_CONSTRAINT` and `-c` reach the same pip call, which is why the probe proves the adoption". That is a reasoned equivalence, not a reading. I confirmed with a dry-run that the shipped line resolves on this host, but no fresh `make venv` was run with it.
2. The Outcome section says "`hatchling` built unconstrained here". The 25-03 logs contain no hatchling or build-isolation line (`grep -i hatchling 25-03-*.log` is empty). The statement comes from pip's 2026-07-29 news, cached in `.planning/research/PITFALLS.md` at MEDIUM confidence. It is a documented behavior of pip 26.2, not something the probe saw.
**Fix:** Reword both as inference with the source named. For example: "The probe set `PIP_CONSTRAINT`; the shipped recipe passes `-c`. pip merges the two, so this is expected to behave the same (not run as shipped)." And: "pip 26.2 documents that constraints no longer reach isolated build environments (pip news 2026-07-29), so `hatchling` is expected to build unconstrained (not observed in the probe logs)." Alternatively run `make clean && make venv` once on the final tree and cite that log.

### WR-03: The 300 s bar is stated without the same-host gate readings that exceed it

**File:** `docs/architecture/decision_log.md` L43 "The bar" (about line 2889-2894); `README.md:310`; `docs/HOW_TO_DEVELOP.md` section 0 and section 6; `docs/architecture/packaging.md` gate block; `.pre-commit-config.yaml:10-12`; `Makefile:109-111`
**Issue:** L43 justifies 300 s as sitting "above both non-decisive readings (195.23 s, 179.21 s) and above the venv probe's 270.35 s". `bench/RESULTS.md` (end of the Phase 24 material, about line 5540) already records green `make verify` pytest times on the same M5 host at 294.40 s (24-02) and 336.15 s (24-03). The 24-01 runs were 296.91 s and 272.91 s. The 336.15 s reading alone exceeds the bar, and L43 does not mention it. That is selective support. Every doc that now quotes "bar 300 s on an 18-CPU Apple M5 Max" lets a reader take 300 s as the gate's ceiling, but the same host has read above it under load. Idle-ish readings of 179-195 s against 336 s under load is nearly a twofold spread, and the new text does not say so. Related wording in `.pre-commit-config.yaml:10-12`: "L43 sets its bar at 300 s ... read on 2026-10-14". The 300 s was set by the human; the readings were 179-195 s. "Read" attaches to the wrong figure.
**Fix:** In L43 "The bar", add the Phase 24 readings (`296.91 s`, `294.40 s`, `336.15 s`, at the loads recorded there) and say the bar is a human-set figure the gate has been read above under load. In `.pre-commit-config.yaml`, drop "read on 2026-10-14", or split it: "bar 300 s (human-set, L43); readings 179.21-195.23 s on 2026-10-14".

## Info

### IN-01: Two Makefile comments still describe the stamp as depending on `pyproject.toml` only

**File:** `Makefile:62-63`, `Makefile:91-92`
**Issue:** Line 62-63 reads "$(STAMP) alone (pyproject.toml only) never would". Line 91 reads "It depends on $(STAMP), which depends on pyproject.toml". Since this phase `$(STAMP)` also depends on `requirements.txt`. The comment at line 91 explains why a playwright bump re-installs the shell, so a `make lock` that moves requirements now triggers that too.
**Fix:** Say "pyproject.toml and requirements.txt" in both places.

### IN-02: Over-long comment line in `Makefile`

**File:** `Makefile:179`
**Issue:** The rewritten comment line is 111 columns, against the 100 used everywhere else in the file. It also merges two sentences at an odd point.
**Fix:** Rewrap: "# The commit-time slice (D-02, D-04): gsd's SDK kills `git commit` at 30 000 ms, and the whole gate's bar is 300 s (L43)." Put "Every test file but the five heavy ones ..." on the next line.

### IN-03: README says Apple silicon is "not measured on", then says the numbers were read on Apple silicon

**File:** `README.md:37-43`
**Issue:** The list "Apple silicon, Graviton and a Raspberry Pi 5 are the targets, built for and not measured on" is followed by "every performance number ... was read on ... a 12-CPU Apple M2 Max and an 18-CPU Apple M5 Max". Both Apple hosts are Apple silicon, and "another arm64 board" is ambiguous for the same reason. The intent (no linux/arm64 image run on Graviton or a Pi) is right, but as written the two clauses contradict each other.
**Fix:** "Graviton and a Raspberry Pi 5 are targets the image is built for and not measured on: every performance number ... was read on a 12-CPU Apple M2 Max and an 18-CPU Apple M5 Max, and none on a Raspberry Pi, Graviton or another arm64 server or board."

### IN-04: `reverify-phase` hard-codes a Claude-specific tool path in a tool-neutral directory

**File:** `.ai_skills/reverify-phase/SKILL.md:20`
**Issue:** `.ai_skills/README.md` says this directory is tool-neutral and read by any CLI. The skill pins `gsd_run` to `node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs"`, which does not exist for a Codex or other runtime install.
**Fix:** "`gsd_run` is the gsd-tools shim your runtime installed (for Claude Code, `node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs"`)."

### IN-05: Debt item carries a commit subject where convention asks for a sha; L34 has no forward pointer to L43

**File:** `docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md:17`; `docs/architecture/decision_log.md` L34
**Issue:** The IN-03 line says "Resolved in: docs(25): log L43 -- ...", but the template's `Resolved in:` field wants a commit sha, as the retired idea files do not. Separately, L43 "amends L34", but L34's entry still reads as current ("The bar is 66 s ...") with no "Amended by L43" line. A reader who lands on L34 through its id will not learn the bar moved. The log's rule is "add a new entry that supersedes it", so a forward link is the minimum.
**Fix:** After the commit lands, replace the subject with the sha. Add one line under L34's heading: "Bar amended by L43 (2026-10-14)."

---

_Reviewed: 2026-10-14_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
