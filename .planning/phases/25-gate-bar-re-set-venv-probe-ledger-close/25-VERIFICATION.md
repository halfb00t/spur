---
phase: 25-gate-bar-re-set-venv-probe-ledger-close
verified: 2026-10-14T16:20:00Z
status: passed
score: 5/5 must-haves verified
covered_files:
  - ".ai_skills/reverify-phase/SKILL.md"
  - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/25-01-PLAN.md"
  - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/25-01-SUMMARY.md"
  - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/25-02-PLAN.md"
  - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/25-02-SUMMARY.md"
  - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/25-03-PLAN.md"
  - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/25-03-SUMMARY.md"
  - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/25-04-PLAN.md"
  - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/25-04-SUMMARY.md"
  - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/25-05-PLAN.md"
  - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/25-05-SUMMARY.md"
  - ".pre-commit-config.yaml"
  - "Makefile"
  - "README.md"
  - "bench/RESULTS.md"
  - "docs/HOW_TO_DEVELOP.md"
  - "docs/architecture/decision_log.md"
  - "docs/architecture/packaging.md"
  - "docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md"
  - "tests/test_hooks.py"
covered_digest: "v3:sha256:b31c66b68fba2f1e29e5026dc36518993784ea6c880e12c45b5a9c11f1fc4080"
behavior_unverified: 0
overrides_applied: 3
overrides:
  - must_have: "The human sets the bar from the readings; each reading recorded with load, machine and HEAD (min, median and max per arm)"
    reason: "Ten decisive readings were not taken. The human waived the idle wait for the whole session (`I told you not to wait preconditions and ignore the load. RUN ASAP`), cut the session to one reading per arm (`Run each arm once and don't waste any more time`), and set the bar on a `none` candidate (`Let's set 300 s. IMHO it's a reasonable bar`). Per-arm min/median/max are printed as `no decisive run`, as clause 9 of the unedited rule requires. Two non-decisive readings (A1 195.23 s, B1 179.21 s) are recorded with load, machine and HEAD."
    accepted_by: "human (halfb00t), verbatim in bench/RESULTS.md `#### Gate decision`, 25-02-SUMMARY.md, 25-04-SUMMARY.md"
    accepted_at: "2026-10-14 (time of day not recorded)"
  - must_have: "Rule clause 4 idle wait released (IDLE) before each run; clause 5 A1 exception (no run after an expired A1 wait); N >= 5 per arm"
    reason: "Eight waits before A1 gave up or were aborted; the human waived clause 4 for the session and overrode clause 5's A1 exception. Rule not edited; by clause 5 every run started without a released wait is non-decisive, and is classed so. 2 of 10 slots read, 8 missing by the human's decision, not by the 3 h cap or the attempt budget."
    accepted_by: "human (halfb00t)"
    accepted_at: "2026-10-14 (13:17Z for the waiver, after wait 8)"
  - must_have: "Plan verify scripts of 25-02 / 25-04 that presume ten decisive readings or an IDLE/GAVE_UP wait end"
    reason: "Fail as written because of the same human decision; output kept verbatim under `## Deviations` in 25-02-SUMMARY.md and 25-04-SUMMARY.md."
    accepted_by: "human (halfb00t)"
    accepted_at: "2026-10-14"
re_verification:
  previous_status: passed
  previous_score: 5/5
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 25: Gate Bar Re-Set, Venv Probe, Ledger Close - Verification Report

**Phase Goal:** The gate is measured once on the shipped `HEAD` under a rule written before the first reading, the human sets the bar from the readings, L34 is amended once, `make venv` is probed once under `PIP_CONSTRAINT` without touching the main checkout's hooks, and the two small ledger items (the Pi 5 claim, the reverify recipe) are closed.
**Verified:** 2026-10-14
**Status:** passed (with the three human-decision overrides in the frontmatter, carried unchanged)
**Re-verification:** Yes. The prior report (status passed, 5/5, written at `5c0d4a2`) went stale when a code-review fix pass landed 14 commits (`79958f1` .. `11ac61f`) after `bbc7cff`. This pass re-checks the delta; it does not re-derive the readings.

## What this pass ran, and what it carried

**Ran in this pass (against the tree at HEAD `ffcc40e`):**

- `git diff --stat bbc7cff..HEAD` over the nine named files, then read the full diff of `SKILL.md`, `.pre-commit-config.yaml`, `Makefile`, `README.md`, `bench/RESULTS.md`, `decision_log.md` and `tests/test_hooks.py`. `docs/HOW_TO_DEVELOP.md` and `docs/architecture/packaging.md` have no change in that range.
- The rule section `### The rule (25-01)` in `bench/RESULTS.md` against its content at `1d5ce8a` (the pre-registration commit). The two extractions differ only by one trailing blank line (121 vs 122 lines), which is the separator before the next heading, since the old file ended with that section. The rule text is byte-identical. The rule was not edited after the readings.
- `grep -n -E "63\.555|~ ?64 ?s" Makefile .pre-commit-config.yaml docs/HOW_TO_DEVELOP.md` prints nothing (rc 1).
- `grep -n "^## L43"` finds exactly one L43 (line 2860). L34 carries `Bar amended by L43 (2026-10-14).` (line 1668, the IN-05 pointer).
- `Makefile` `$(STAMP): pyproject.toml requirements.txt` (line 49). `make -n --no-print-directory -W requirements.txt .venv/.installed` prints `.venv/bin/python -m pip install -e '.[dev]' -c requirements.txt`.
- The test file `tests/test_hooks.py` run alone: `7 passed in 0.59s` (6 before, plus the WR-01 test). It was not a whole-suite run.
- L43's new factual claims against their sources (table below).
- The `+` lines of the delta for `TBD|FIXME|XXX|TODO`: none.
- `git worktree list` shows only the main checkout; `agent/venv-probe` does not exist; `.git/hooks/pre-commit` line 6 is `INSTALL_PYTHON=/Users/half/git/halfb00t/spur/.venv/bin/python`.
- `.planning/REQUIREMENTS.md` lines 157, 163, 167, 176, 178 are `[x]` and lines 261-265 read `Complete` for all five IDs.
- Fingerprint through the CLI (`verification.fingerprint`), copied verbatim above.

**Carried from the prior report, not re-run:**

- The five phases' readings and their load, machine and HEAD columns (A1 195.23 s, B1 179.21 s, 8 gave-up waits), per-arm "no decisive run", the three overrides.
- The venv probe's own outcome (`make venv` exit 0, `1317 passed`, `pip check` clean, 31/31 pins, freeze diff, hook shim sha256 equal before and after, probe after the last reading). I did not re-run the probe.
- The README Pi 5 sentence's existence and the skill's count of five from the record (I re-read only the delta of both).
- The gate: not re-run. Evidence supplied by the orchestrator and not independently reproduced here: `make test` on `ffcc40e` read `1318 passed in 217.25s`, coverage 97.99 %, exit 0; the fixer's `make verify` on `4d61923` exited 0 with `1318 passed`. 1318 is the phase's 1317 plus the one new test, which agrees with the `7 passed` I observed in the hooks file (6 + 1).

## The delta against the plan (carried, unchanged)

The phase did not produce the measurement the roadmap describes. The plan presumed ten decisive idle readings; it got two non-decisive ones (A1 195.23 s at load 4.18 -> 7.04, B1 179.21 s at 6.07 -> 7.33, HEAD `9b68f6d`), because the human waived the idle wait and cut the session. The 300 s bar is a human figure (`Let's set 300 s. IMHO it's a reasonable bar`) over those two readings, recorded as `Candidate bar (D-05): none`. L43 says so in its title and body. That is recorded, not a gap to re-plan. The three overrides above carry each waiver with its reason and the human's words; none was re-litigated here.

## Goal Achievement

### Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | The rule exists before any reading: idle threshold, cool-down, N >= 5, give-up, A/B interleaved, "new method not L34's" | VERIFIED (re-checked) | Rule section identical to `1d5ce8a` (diff above), so no post-reading edit. The delta did not touch it. |
| 2 | The human sets the bar from the readings; each reading with load, machine, HEAD (min/median/max per arm); give-up recorded and the human decides | VERIFIED (override 1 and 2; delta touched L43's "The bar" paragraph, re-checked) | The recorded readings are unchanged (carried). L43 "The readings" still states n = 0 per arm and the verbatim human words. The WR-03/WR-04 text now says the bar "is not a ceiling the gate has been read under on an idle host", "a figure the human set; it was not read as a ceiling". That strengthens the honesty of the record and does not alter the decision. The 300 s figure is untouched. |
| 3 | L34 amended once; stale `63.555 s` / `~64 s` sentences rewritten; IN-03 retired in the same commit; search prints nothing | VERIFIED (re-checked) | One `## L43`, L34 gains a forward pointer (IN-05). Stale-figure grep prints nothing. The debt file's IN-03 line now reads `Resolved in: 34270c8 (...)`; `34270c8` is the commit the prior report names as holding L43, the Makefile rewrite and the IN-03 closure together. I did not re-open that commit's diff in this pass; the sha is carried from the prior report. |
| 4 | Probe safe and recorded; green -> `$(STAMP)` gains the constraint | VERIFIED (re-checked where the delta touched it) | Makefile stamp line and the `-c requirements.txt` install line are both present (above). The WR-01 test `test_the_dev_venv_installs_under_the_closure_and_reinstalls_when_it_moves` pins both: it dry-runs `make -n -W requirements.txt .venv/.installed`, asserts exactly one `-c` and the text `-c requirements.txt`, and only prints the recipe if `requirements.txt` is a prerequisite. It passes (`7 passed`). Hook shim, worktree list and branch state re-read and unchanged. |
| 5 | Small ledger closed: README hardware / no Pi 5 claim; reverify recipe; ideas retired | VERIFIED (re-checked) | `README.md` now says the image builds for `linux/amd64` and `linux/arm64`; "Graviton and a Raspberry Pi 5 are targets the image is built for and not measured on"; every number was read on the 12-CPU M2 Max and 18-CPU M5 Max, "and none on a Raspberry Pi, Graviton or another arm64 server or board". The IN-03 self-contradiction (Apple silicon "not measured on" yet measured on) is gone. `.ai_skills/reverify-phase/SKILL.md` step 1 now says `gsd_run` is the gsd-tools shim the runtime installed, giving the Claude Code path as the example; `docs/HOW_TO_DEVELOP.md:150` still points at the skill. |

**Score:** 5/5 truths verified (3 with the human-decision overrides carried). 0 behavior-unverified.

### L43 claim cross-check (the delta's new factual text)

| Claim in L43 / RESULTS | Source checked | Result |
|---|---|---|
| L38: 208.52, 161.71, 208.60 s at loads 4 to 9, 1210 tests, `### The gate, priced (19-09)` | `bench/RESULTS.md` lines 4614-4616: loads 4.03->6.30, 6.30->9.06, 9.06->7.98; machine line at that section is "Apple M5 Max ... 18 CPUs" | holds; and "none above 300 s" holds |
| Phase 24 readings: `1 failed, 1294 passed in 296.91s` (load 15.6), `1295 passed in 272.91s`, `1311 passed in 294.40s`, `1311 passed in 336.15s` (loads 5.36 4.71 6.68) | `bench/RESULTS.md` 5538-5543; 24-01/02/03 SUMMARYs | all four figures and loads match |
| Host of those: 24-01 and 24-03 name a 12-CPU Apple M2 Max; 24-02 names no host | grep: 24-01 "Apple M2 Max, 12 CPUs", 24-03 "Apple M2 Max"; 24-02 has no host line | holds |
| Phase 24 merged 2026-10-13 | `git log main`: `94dfc19 2026-10-13 Phase 24: Bore-Shape Selector (#36)`; ROADMAP "completed 2026-10-13" | holds |
| Probe set `PIP_CONSTRAINT` absolute; shipped line is `-c` relative; no probe ran `make venv` with `-c`; `hatchling` unobserved | Reworded as inference in both L43 and RESULTS; claim "the 25-03 logs hold no hatchling or build-isolation line" is carried from the prior pass and from the review, not re-grepped here | wording is now conservative; the absence-in-logs claim is unconfirmed in this pass |

The one overstatement the review found (WR-04, "no loaded M5 Max reading") is gone from the text: the paragraph now lists the M5 Max loaded readings and puts the readings at or above 300 s on the M2 Max.

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|---|---|---|---|
| REQ-gate-rule-pre-registered | 25-01 | SATISFIED | Truth 1. REQUIREMENTS.md now `[x]` / `Complete` (the prior report's bookkeeping warning is closed). |
| REQ-gate-bar-reset | 25-02, 25-04 | SATISFIED (override) | Truths 2, 3. |
| REQ-venv-constraint-probe | 25-03, 25-04 | SATISFIED | Truth 4. |
| REQ-pi5-claim-softened | 25-05 | SATISFIED | Truth 5. |
| REQ-reverify-recipe | 25-05 | SATISFIED | Truth 5. |

All five IDs from the PLAN frontmatter (`25-01` through `25-05`) are in REQUIREMENTS.md and map to Phase 25. No orphan.

### Key Links / Artifacts

| Artifact | Status | Details |
|---|---|---|
| `bench/RESULTS.md` `## The gate re-set (Phase 25)` | VERIFIED | rule untouched; the probe-outcome paragraph reworded as inference |
| `docs/architecture/decision_log.md` L43 | VERIFIED | single amendment; claims cross-checked above |
| `Makefile` `$(STAMP)` | VERIFIED, WIRED | prerequisite and `-c requirements.txt` present; `$(HOOKS)` and `$(BROWSER)` still hang off `$(STAMP)`; delta otherwise comments |
| `tests/test_hooks.py` | VERIFIED | new test exercises the real Makefile via `make -n`; passes |
| `.ai_skills/reverify-phase/SKILL.md` | VERIFIED | real steps, tool-neutral wording |
| `README.md` hardware sentence | VERIFIED | |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| New venv-stamp test | `.venv/bin/python -m pytest tests/test_hooks.py -q --no-cov` | `7 passed in 0.59s` | PASS |
| Stamp recipe carries the constraint | `make -n -W requirements.txt .venv/.installed` | `pip install -e '.[dev]' -c requirements.txt` | PASS |
| Stale figures absent | grep on three files | no output | PASS |
| Rule unchanged | section diff vs `1d5ce8a` | identical but one separator blank line | PASS |
| Gate on HEAD | not re-run by this pass | orchestrator: `1318 passed in 217.25s`, exit 0 | carried, unverified by me |

### Probe Execution

No `scripts/*/tests/probe-*.sh` exist. The phase's own `make venv` probe was run once by 25-03 and was not re-run here.

### Anti-Patterns Found

None blocking. No `TBD|FIXME|XXX|TODO` on the added lines of the delta.

### Human Verification Required

None open.

### Gaps Summary

No gaps. Non-blocking observations:

1. **Evidential weight of the bar is unchanged and honestly recorded.** 300 s is a human figure over two non-decisive readings. L43 now says plainly that it was not read as a ceiling.
2. **L43 still contains two sentences that were true when written and are now slightly dated.** (a) "IN-03 ... closed by this commit's subject" while the debt file now cites sha `34270c8`; (b) `tests/test_hooks.py`'s "`6 passed`" is the historical log, the file now has 7 tests. Neither is a false claim about the current state. Info only.
3. **Two checks the delta leans on were not re-run in this pass:** the absence of a `hatchling`/build-isolation line in the 25-03 logs, and the identity of `34270c8` as the L43 commit. Both are carried from the prior report and the review.
4. **The 13 unexplained freeze-diff moves in the probe** (e.g. ruff 0.16.10 -> 0.17.0) remain recorded "as read, not explained", as in the prior report.

---

_Verified: 2026-10-14_
_Verifier: Claude (gsd-verifier)_
