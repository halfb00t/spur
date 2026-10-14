---
phase: 25-gate-bar-re-set-venv-probe-ledger-close
fixed_at: 2026-10-14T00:00:00Z
review_path: .planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/25-REVIEW.md
iteration: 1
findings_in_scope: 8
fixed: 8
skipped: 0
status: all_fixed
---

# Phase 25: Code Review Fix Report

**Fixed at:** 2026-10-14
**Source review:** `.planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/25-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 8 (WR-01, WR-02, WR-03 in the first pass; IN-01..IN-05 in the second pass, `fix_scope: all`)
- Fixed: 8
- Skipped: 0

**Where it ran:** `workflow.use_worktrees` is `false` in `.planning/config.json`, so no worktree was created. Every edit, `make verify` run and commit was in the main checkout, on branch `gsd/phase-25-gate-bar-re-set-venv-probe-ledger-close`. The gate numbers below are reproducible from this tree.

**Verification (whole set):**
- `make verify`, run once on the combined working tree before the commits were split: exit 0, `1318 passed in 188.62s (0:03:08)`, `TOTAL 1358 22 386 13 97.99%`, `Required test coverage of 96.0% reached`, `real 189.22`.
- `make verify`, run again on the final committed tree (HEAD `f7ce3ab`, after the docs text was re-wrapped while splitting commits): exit 0, `1318 passed in 207.89s (0:03:27)`, coverage `Total coverage: 97.99%`. Neither run is a gate reading and neither enters L43's bar.
- `1318` is Phase 25's `1317` plus the one new test.
- Each commit also ran the pre-commit `make verify.fast` hook and `no-skip-token`: both `Passed`.
- Orchestrator follow-up `a9cf1d8`: the WR-02 and WR-03 edits had joined sentences onto existing L43 lines, leaving three at 153, 186 and 206 columns in a file that wraps near 120. Re-wrapped only; wording unchanged. Pre-commit `make verify.fast`: `Passed`.

**Verification (Info pass, IN-01 to IN-05):**
- `make verify` on the final tree (HEAD `4d61923`, after all five Info commits): exit 0, `1318 passed in 186.51s (0:03:06)`, `TOTAL 1358 22 386 13 97.99%`, `Required test coverage of 96.0% reached`, `make verify 629.26s user 559.87s system 636% cpu 3:06.96 total`. Main checkout, so reproducible from this tree. Not a gate reading and not entered into L43's bar. The count is unchanged from the first pass (`1318`): the Info edits touch comments and prose only.
- Each of the five commits ran the pre-commit `make verify.fast` hook and `no-skip-token`: both `Passed`.
- Width: no line I wrote exceeds 100 columns in the Makefile or 90 in the README paragraph; `decision_log.md` and the SKILL.md edits are short lines. The Makefile has other pre-existing lines over 100 (e.g. 36, 80, 85, 112); I did not touch them.

## Fixed Issues

### WR-01: No test covers the shipped `-c requirements.txt` or the new stamp prerequisite

**Files modified:** `tests/test_hooks.py` (new test inserted at lines 162-179, before `test_the_image_suite_ignores_the_browser_test`)
**Commit:** `79958f1`
**Applied fix:** Added `test_the_dev_venv_installs_under_the_closure_and_reinstalls_when_it_moves`. The existing `_dry_run(target)` helper takes one target and bakes in `-o .venv/.browser`, so the review's snippet did not fit it. The test runs its own `make -n --no-print-directory -W requirements.txt .venv/.installed`, in the style of the neighbouring `dry_run_forcing_the_install`. `-W requirements.txt` pretends the file just changed, so the stamp recipe is printed only if the file is a prerequisite of `$(STAMP)`. It then asserts the printed `pip install -e` line carries `-c requirements.txt` exactly once. This covers both halves of the finding (the flag and the prerequisite) in one test.
**Verification:**
- `.venv/bin/python -m pytest tests/test_hooks.py -q --no-cov` on the edited file: `7 passed in 0.67s`.
- Mutation check, Makefile restored afterwards with `git checkout -- Makefile` (`git status` clean for it): with `requirements.txt` removed from the `$(STAMP)` prerequisites the new test failed, `1 failed in 0.02s` (assertion at `tests/test_hooks.py:176`); with `-c requirements.txt` removed from the install line it failed, `1 failed in 0.02s` (`:177`).
- `make verify`: exit 0, `1318 passed in 188.62s (0:03:08)` (see above).

### WR-02: L43 and RESULTS word the adoption proof and the build-constraint caveat as observed when they are inferred

**Files modified:** `docs/architecture/decision_log.md` (L43, "The venv probe" paragraph, about lines 2899-2910), `bench/RESULTS.md` ("The venv probe (25-03)", `#### Outcome`, last paragraph, about line 5932)
**Commit:** `31d0f81`
**Applied fix:** Took the reword option. Nothing was rebuilt: no `make clean`, no `make venv`, `.venv` untouched.
- L43 no longer says the probe "proves the adoption". It now says the probe set `PIP_CONSTRAINT` to an absolute path on the pre-change Makefile, the shipped recipe passes `-c` with a relative path, pip merges the two, so the shipped line is expected to behave as the probe did, and that this is an inference (no probe ran `make venv` with `-c` as shipped).
- L43 and RESULTS no longer say `hatchling` "builds / built unconstrained" as an observation. They cite pip's 2026-07-29 news, as cached in `.planning/research/PITFALLS.md` (line 389, checked), say `hatchling` is expected to build unconstrained, and say the 25-03 logs hold no `hatchling` or build-isolation line.
- The L43 decision itself (300 s bar, `-c requirements.txt`, stamp prerequisite) is unchanged.
**Verification:**
- Re-read of both edited passages after the edit: text present, surrounding paragraphs intact.
- `make verify`: exit 0, `1318 passed in 188.62s (0:03:08)` on the combined tree, and `1318 passed in 207.89s (0:03:27)` on the final tree.
- Not run: any fresh `make venv`; the review's dry-run result that the shipped line resolves is the reviewer's, and I did not repeat it.

### WR-03: The 300 s bar is stated without the same-host gate readings that exceed it

**Files modified:** `docs/architecture/decision_log.md` (L43 "The bar", about lines 2887-2900), `.pre-commit-config.yaml:9-13`
**Commit:** `f7ce3ab`
**Status note:** fixed, but **the finding's premise is partly wrong and the fix was adapted**; see below. Requires a human glance at the L43 wording.
**Applied fix:**
- I read the four figures from `bench/RESULTS.md` lines 5538-5543 and the logs under `.planning/phases/24-bore-shape-selector/investigation/` before writing them: `1 failed, 1294 passed in 296.91s` (24-01 first run, `24-01-red-1.log`), `1295 passed in 272.91s` (24-01 re-run), `1311 passed in 294.40s` (24-02), `1311 passed in 336.15s` (24-03).
- The review calls these "same M5 host" readings and the 296.91 s run a green one. Both are wrong. `24-01-SUMMARY.md:213` and `24-03-SUMMARY.md:167` record the host as an Apple M2 Max (24-04, same phase, records `12 CPUs, 32.0 GiB`); `24-02-SUMMARY.md` names no host. The 296.91 s run was red (`test_health_reports_pool_state`, the resource-tracker flake). The figures are pytest-reported seconds, not `make verify` `real`. L43 itself says no figure is carried from one host to another (L08), so writing them as M5 readings would have been a wrong number.
- Loads: only two are recorded. 296.91 s read at a host load of 15.6 (`24-01-SUMMARY.md:244`); 336.15 s at load averages `5.36 4.71 6.68` at the start (`24-03-SUMMARY.md:220`). For 272.91 s and 294.40 s no load is recorded anywhere I looked, and L43 says "load not recorded" rather than a figure.
- L43 "The bar" now says the bar is not a ceiling the gate has been read under, that this host has no loaded full-gate reading, quotes the four Phase 24 figures as read with their host, HEAD/test-count and unit caveats, states that 336.15 s is above 300 s, and says 300 s is a human-set figure whose behaviour on the M5 Max under load is unread. I did not write the review's "nearly twofold spread" (it compares readings from two different hosts).
- `.pre-commit-config.yaml`: dropped "read on 2026-10-14". It now says the 300 s is "a figure the human set, not a reading" and names the two non-decisive readings, `179.21 s and 195.23 s`, separately.
- Not changed: `README.md:310`, `docs/HOW_TO_DEVELOP.md` and `docs/architecture/packaging.md` also quote the bar with its host. The finding's Fix names only L43 and `.pre-commit-config.yaml`, so I left them; they already say "bar 300 s on an 18-CPU Apple M5 Max", which remains true.
**Verification:**
- Re-read of both edits: present, surrounding text intact.
- `make verify`: exit 0, `1318 passed in 207.89s (0:03:27)` on the final tree.
- `.pre-commit-config.yaml` is read by `tests/test_hooks.py` (`_hook_blocks`); that file passed (`7 passed`) before and inside the gate runs.

### IN-01: Two Makefile comments still describe the stamp as depending on `pyproject.toml` only

**Files modified:** `Makefile` (comment at lines 62-63; comment at lines 91-96)
**Commit:** `fa1468d`
**Applied fix:** Located both by content (the review's lines 62-63 and 91-92 had not moved). The D-06 hooks comment now says `$(STAMP)` alone "(pyproject.toml and requirements.txt) never would". The `$(BROWSER)` comment now says `$(STAMP)` "depends on pyproject.toml and requirements.txt". Both paragraphs were re-wrapped at 100 columns; the browser paragraph grew by one line. Comment text only, no recipe or prerequisite changed.
**Verification:** `git diff` re-read: only the two comment blocks changed. Pre-commit `make verify.fast`: `Passed`. `make verify`: exit 0, `1318 passed` (see above). Not run: any syntax check beyond make parsing the file in `make verify`.

### IN-02: Over-long comment line in `Makefile`

**Files modified:** `Makefile` (comment at lines 179-186)
**Commit:** `1694d73`
**Applied fix:** The review said line 179; the content was still the 111-column line, now line 180 after IN-01's extra line, and measured 111 columns before the edit. Split after "(L43)." as proposed, started "Every test file but the five heavy ones ..." on its own line and re-wrapped the rest of that sentence through "The first three, by share of ..." so the old ragged "The" / "first three" break is gone. No word changed. Longest line I wrote: 89 columns. Committed separately from IN-01 (one concern per commit) by staging IN-01's hunks first.
**Verification:** `git diff` re-read: only the comment block changed. Pre-commit `make verify.fast`: `Passed`. `make verify`: exit 0.

### IN-03: README says Apple silicon is "not measured on", then says the numbers were read on Apple silicon

**Files modified:** `README.md` (lines 39-43)
**Commit:** `de17a2c`
**Applied fix:** Applied the review's wording: "Graviton and a Raspberry Pi 5 are targets the image is built for and not measured on", the two dev hosts kept as read (a 12-CPU Apple M2 Max and an 18-CPU Apple M5 Max), and "none on a Raspberry Pi, Graviton or another arm64 server or board". Apple silicon no longer appears in the unmeasured list. I added a sentence break after "`linux/arm64`." to keep the sentence readable; no host, CPU count or figure was added or changed. Re-wrapped at the paragraph's existing 88 columns.
**Verification:** `git diff` re-read. `grep` over `tests/` for the old phrase and for "Raspberry": no test asserts this text. Pre-commit `make verify.fast`: `Passed`. `make verify`: exit 0.

### IN-04: `reverify-phase` hard-codes a Claude-specific tool path in a tool-neutral directory

**Files modified:** `.ai_skills/reverify-phase/SKILL.md` (lines 20-22)
**Commit:** `4bbe249`
**Applied fix:** Applied the review's wording: `gsd_run` is "the gsd-tools shim your runtime installed (for Claude Code, `node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs"`)". The rest of step 1 is unchanged.
**Verification:** `git diff` re-read. Pre-commit `make verify.fast`: `Passed`. `make verify`: exit 0.

### IN-05: Debt item carries a commit subject where convention asks for a sha; L34 has no forward pointer to L43

**Files modified:** `docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md` (line 17), `docs/architecture/decision_log.md` (new line 1668, under the L34 heading)
**Commit:** `4d61923`
**Applied fix:**
- (a) `git log --oneline --grep='log L43'` returns exactly one commit, `34270c8`, subject identical to the text in the file. Replaced the subject with `Resolved in: 34270c8 (L43 re-set the bar and the Makefile comment now cites it).` The item stays in `active/`: its IN-01, IN-02 and IN-04 are still open, so I did not flip its `Status` or move it.
- (b) Added "Bar amended by L43 (2026-10-14)." under L34's heading, after the `Date:` line, as its own paragraph. Nothing else in L34 changed.
- Correction to the brief: it says `docs/ideas/retired/*.md` cite shas. They do not. Their `Retired in:` fields carry commit subjects (the same L43 subject appears in the retired venv idea). `docs/tech_debt/resolved/*.md` cite shas (`daeb284`, `4f7e8fe`, `2aadcea`, `21b8fe4`), and the tech-debt template asks for a sha, so I used the sha. I did not touch the retired idea files.
**Verification:** `git diff` re-read: two files, 3 changed lines. Pre-commit `make verify.fast`: `Passed`. `make verify`: exit 0.

## Skipped Issues

None. All eight findings were fixed. No finding was skipped as already resolved: IN-01 and IN-02's quoted text was still present after the WR fixes (only the line numbers had moved).

## Filed items

No `docs/ideas/` or `docs/tech_debt/` item was filed. The existing Phase 19 debt item was edited (IN-05) and stays active.

---

_Fixed: 2026-10-14_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
