---
phase: 25-gate-bar-re-set-venv-probe-ledger-close
verified: 2026-10-14T15:30:00Z
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
  - "tests/test_hooks.py"
covered_digest: "v3:sha256:8246fa5bf2d71429d1a6ad0859a8a3c169209598984180eb84dccaa5166cff10"
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
---

# Phase 25: Gate Bar Re-Set, Venv Probe, Ledger Close - Verification Report

**Phase Goal:** The gate is measured once on the shipped `HEAD` under a rule written before the first reading, the human sets the bar from the readings, L34 is amended once, `make venv` is probed once under `PIP_CONSTRAINT` without touching the main checkout's hooks, and the two small ledger items (the Pi 5 claim, the reverify recipe) are closed.
**Verified:** 2026-10-14
**Status:** passed (with three human-decision deltas stated below)
**Re-verification:** No, initial verification

## The delta against the plan, stated first

The phase did **not** produce the measurement the roadmap describes. Read this before the table.

| What the rule / plan presumed | What happened | Who decided |
|---|---|---|
| Idle wait (clause 4): three samples under load 1.5 before every run | 8 waits before A1: 7 `GAVE_UP`, 1 `ABORTED`; lowest 1.60, never held under 1.5 for three samples. Every run started with wait `WAIVED` | Human: `I told you not to wait preconditions and ignore the load. RUN ASAP` |
| A1 exception (clause 5): no run after an expired A1 wait | A1 ran anyway | Human override (the rule did not allow it; the rule was not edited) |
| 10 readings, N = 5 per arm | 2 readings: A1 195.23 s (load 4.18 -> 7.04), B1 179.21 s (6.07 -> 7.33). A2 started and stopped on the human's order (not red, not a reading). 8 slots never ran | Human: `Run each arm once and don't waste any more time` |
| min / median / max per arm, a candidate bar (largest decisive B, ceil) | n = 0 decisive in both arms. Per-arm table says `no decisive run`; `Candidate bar (D-05): none`. Browser file's idle cost: not read | Follows from the above by clause 9 of the unedited rule |
| Human accepts the candidate | Human wrote `Let's set 300 s. IMHO it's a reasonable bar`; recorded as `other 300 <reason>`; no reason beyond that sentence was given or asked | Human |

Consequences, plainly: the 300 s bar is a human number set on a host that was never idle, backed by two non-decisive readings (both below it). It is not derived from a rule and L43 says so. It carries no idle-host statistics and no measured browser-file cost. That is what was decided; it is recorded, not a gap to re-plan. The claim "gate measured on an idle host" in L43's title is the plan's framing; the body of L43 and `bench/RESULTS.md` say the opposite, correctly.

## Goal Achievement

### Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | The rule exists before any reading: idle threshold, cool-down, N >= 5, give-up, A/B interleaved, "new method not L34's" | VERIFIED | `bench/RESULTS.md` `### The rule (25-01)` (line ~5551): clause 4 X = 1.5 strict, cool-down = the wait before every run; clause 6 N = 5, slots A1 B1 ... A5 B5 interleaved, arm A `--ignore=tests/test_browser.py`; clause 5 give-up 900 s; first paragraph says new method vs Phase 15 D-04's loads 5-30. Commit `1d5ce8a` (2026-10-14 16:43 +0600 = 10:43Z) is the only commit that adds it; first reading ran 13:17Z; readings committed in `1f7ce01` later. The section is **byte-identical** to `1d5ce8a` (diffed: IDENTICAL), so nothing was edited after readings. |
| 2 | The human sets the bar from the readings; each reading with load, machine, HEAD (min/median/max per arm); give-up recorded and human decides | VERIFIED (override, delta above) | Runs table has load before -> after, UTC, `HEAD 9b68f6d`, machine line `18 CPUs, arm64, 64.0 GiB RAM` for each reading. Give-ups recorded (`#### Waits that gave up`, 8 rows). Min/median/max: `no decisive run` (override 1). Bar 300 s recorded as the human's verbatim words under `#### Gate decision`, with `Candidate bar (D-05): none`. Not tuned toward a pass: 300 s sits above both readings and the human, not the agent, chose it. |
| 3 | L34 amended once; stale `63.555 s` / `~64 s` sentences rewritten; IN-03 retired in same commit; search prints nothing | VERIFIED | `docs/architecture/decision_log.md` has exactly one `## L43` (line 2858), "amends L34", carries bar, method, venv adoption and the widened CI sentence. `grep -n -E "63\.555\|~ ?64 ?s" Makefile .pre-commit-config.yaml docs/HOW_TO_DEVELOP.md` prints nothing (rc 1). Those files and README/packaging.md cite L43's 300 s with host. IN-03 line in `docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md` reads "Resolved in: docs(25): log L43 ..." and IN-04 is still open; commit `34270c8` touches all of it in one commit. (The debt file carries the commit subject, not the sha, because the sha is not known inside its own commit; project precedent per the repo's "resolved-in-shas" debt item.) |
| 4 | Probe safe and recorded: `make venv` under `PIP_CONSTRAINT` in linked worktree, verify result line, `pip check`, freeze diff, hooks still `.venv/bin/python`, probe after last reading; green -> `$(STAMP)` gains constraint | VERIFIED | `### The venv probe (25-03)`: worktree `.claude/worktrees/venv-probe`, `make venv` exit 0, `make verify` `1317 passed`, `pip check` clean, 31/31 pins, freeze diff recorded (four predicted moves plus 13 others listed as read), `Outcome: GREEN`. Timeline: last run-record end 13:26:04Z, probe start 13:33:03Z. Hook shim sha256 before == after; I re-read `.git/hooks/pre-commit` line 6: `INSTALL_PYTHON=/Users/half/git/halfb00t/spur/.venv/bin/python`. `git worktree list` shows only the main checkout; `agent/venv-probe` branch no longer exists (deleted at the human's word, `8bb1a24`). Green action done: `Makefile` `$(STAMP): pyproject.toml requirements.txt` and `pip install -e '.[dev]' -c requirements.txt` (diff in `34270c8`); `tests/test_hooks.py` updated, `6 passed` logged. The probe's 270.35 s wall is expressly not a reading and is not in the bar. |
| 5 | Small ledger closed: README hardware / no Pi 5 claim; reverify recipe in HOW_TO_DEVELOP section 6 or `.ai_skills/reverify-phase` (count from the record); ideas retired | VERIFIED | `README.md:39-43` "built for and not measured on ... none on a Raspberry Pi or another arm64 board", names the 12-CPU M2 Max and 18-CPU M5 Max. `.ai_skills/reverify-phase/SKILL.md` exists, with a count of five (Phase 9 twice, 17, 23, 24) read from the record; `docs/HOW_TO_DEVELOP.md:150` points at it beside the ship-note workaround. Both ideas are under `docs/ideas/retired/` and their INDEX rows (lines 29-30) carry the closing commit subject. Commits `92953bb` and `ac129dc` hold them. |

**Score:** 5/5 truths verified, 3 with a human-decision override as listed in the frontmatter. 0 behavior-unverified.

Note on SC5's "count from the record": I only spot-checked it (git log lists `0f1209f` re-verify for Phase 17; the other hits live in `.planning/` history). The roadmap's threshold is three; one hit more or fewer does not change the fork.

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|---|---|---|---|
| REQ-gate-rule-pre-registered | 25-01 | SATISFIED | Truth 1. **Bookkeeping warning:** `.planning/REQUIREMENTS.md` still shows `- [ ]` at line 157 and `Pending` in the traceability table (line 261) while the other four are `[x]` / `Complete`. The requirement is met; the file was not updated. |
| REQ-gate-bar-reset | 25-02, 25-04 | SATISFIED (override) | Truths 2, 3. Readings recorded; human set the bar; one L43; stale sentences rewritten; IN-03 retired. Delta above. |
| REQ-venv-constraint-probe | 25-03, 25-04 | SATISFIED | Truth 4. |
| REQ-pi5-claim-softened | 25-05 | SATISFIED | Truth 5. |
| REQ-reverify-recipe | 25-05 | SATISFIED | Truth 5 (skill branch of the fork). |

No orphaned requirement: REQUIREMENTS.md maps exactly these five IDs to Phase 25 and all five appear in plan frontmatter.

### Key Links / Artifacts

| Artifact | Status | Details |
|---|---|---|
| `bench/RESULTS.md` `## The gate re-set (Phase 25)` | VERIFIED | rule, host, runs, per-arm, red runs, waits, gate decision, probe all present; rule untouched since `1d5ce8a` |
| `docs/architecture/decision_log.md` L43 | VERIFIED | single amendment of L34; cites RESULTS sections by name |
| `Makefile` `$(STAMP)` | VERIFIED, WIRED | `-c requirements.txt` on the install line and `requirements.txt` as prerequisite; `$(HOOKS)` still gates on `$(STAMP)` |
| `tests/test_hooks.py` | VERIFIED | fixtures write `requirements.txt`; 6 passed logged in `investigation/25-04-hooks.log` |
| `.ai_skills/reverify-phase/SKILL.md` | VERIFIED | real steps, not a stub |
| Investigation logs under `investigation/` | VERIFIED | kept and committed in `1f7ce01` / `dbc50d9` |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Gate green after the last code-touching commit | `investigation/25-05-verify.log` tail (not re-run: ~185 s, orchestrator states it is current) | `1317 passed in 184.95s`, `make verify exit 0`, on `ac129dc` | PASS (log read) |
| Nothing but `.planning/` changed since that run | `git diff --name-only ac129dc HEAD \| grep -v '^\.planning/'` | empty | PASS |
| Rule untouched | diff of section vs `1d5ce8a` | IDENTICAL | PASS |
| Stale figures absent | grep on the three named files | no output | PASS |
| Hook shim intact | `.git/hooks/pre-commit` line 6 | `.../spur/.venv/bin/python` | PASS |

### Probe Execution

The phase's own probe (`make venv` under `PIP_CONSTRAINT`) was run once, in a worktree, by plan 25-03 and is recorded above; I did not re-run it (it would load the host and install into a throwaway venv; evidence is the kept logs `25-03-*`). No `scripts/*/tests/probe-*.sh` exist.

### Anti-Patterns Found

No `TBD|FIXME|XXX` markers added to the changed non-planning files that I could find in the diff of `34270c8`; the repo's unfinished-work scan is part of the green `make verify`. None blocking.

### Human Verification Required

None open. Every deviation from the plan is a recorded human decision, listed in the override frontmatter.

### Gaps Summary

No gaps. Warnings (non-blocking):

1. **Bookkeeping:** `.planning/REQUIREMENTS.md` line 157 and 261 still mark REQ-gate-rule-pre-registered `[ ]` / `Pending`. Flip to `[x]` / `Complete` at phase close.
2. **The bar's evidential weight is thin and the record says so.** 300 s is a human number over two non-decisive readings (179-195 s at loads 4-7) on a host that never went idle; the browser test file's idle cost was not measured (the 21-07 B mean of 163.96 s is another session's reading). If a future phase needs a defensible gate bar, it needs a new rule and a new session (L43 "Reversibility").
3. **Open observation, not blocking:** the freeze diff in the probe lists 13 non-pin package moves recorded "as read, not explained" (ruff 0.16.10 -> 0.17.0 among them). They did not affect green, but `make venv` now resolves unpinned dev tools differently from the main `.venv`.

---

_Verified: 2026-10-14_
_Verifier: Claude (gsd-verifier)_
