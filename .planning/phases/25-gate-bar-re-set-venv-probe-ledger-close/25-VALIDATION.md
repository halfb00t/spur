---
phase: "25"
slug: "gate-bar-re-set-venv-probe-ledger-close"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-14"
---

# Phase 25 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 + pytest-xdist 3.8.0 + pytest-cov 7.1.0, driven by `make`; most of this phase's checks are stdlib Python heredocs over kept logs, `git log` / `git show` and `bench/RESULTS.md` |
| **Config file** | `pyproject.toml` (`[tool.coverage.report] fail_under = 96`, `--strict-markers`); no new config |
| **Quick run command** | `make verify.fast` (the pre-commit hook on every commit; ~16 s on record, L36 kills at 30 s) |
| **Full suite command** | `make verify` (`1317 passed` on this HEAD; arm B of the readings) |
| **Estimated runtime** | per-task verify scripts under 5 s; `make verify` 160-340 s on record; 25-02 Task 3 is itself the ten readings, ~75-90 min under the 3 h cap |

---

## Sampling Rate

- **After every task commit:** the hook runs `make verify.fast`; then the task's own `<automated>` checks; then the standing invariants: `git diff --exit-code -- tests/regression/pre_v0_2.json tests/regression/golden_requests.json`; nothing under `src/`, `docker/`, `scripts/`, `requirements.txt`, `pyproject.toml` moved since the rule commit; under `tests/` only `tests/test_hooks.py`, and only on a GREEN probe; the rule section at HEAD equals the rule commit's.
- **Never during the readings:** no commit, no `make`, no pytest, no probe from the first wait to the last run's end (25-02 Task 3). The commit hook is a gate-shaped load and moves HEAD.
- **After every plan wave:** waves 1-2 run no full `make verify` beyond the readings themselves; wave 3's probe runs `make verify` in the worktree (not a gate reading); wave 4 (25-04 Task 3) and wave 5 (25-05 Task 2) each run `make verify` on the main checkout and keep the log.
- **Before `/gsd-verify-work`:** `investigation/25-05-verify.log` ends `make verify exit 0`; the stale-figure search over the five files prints nothing; every per-task check below passes.
- **Max feedback latency:** under 10 minutes for every task except 25-02 Task 3, whose feedback is per attempt (one wait plus one run, at most ~31 minutes under the rule's two 15-minute caps).

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 25-01-01 | 01 | 1 | REQ-gate-rule-pre-registered | T-25-03 | the recipe is rehearsed on `sleep`/`printenv` stand-ins; no gate runs before the rule commit | structural + rehearsal | 25-01 Task 1 heredoc: rule pins, both blocks, host line, the rehearsal logs (wait exit 3, cap 124, arm A spelling) | ❌ W0 (the task creates the section and `investigation/`) | ⬜ pending |
| 25-01-02 | 01 | 1 | REQ-gate-rule-pre-registered | T-25-02 | the human sees every clause before the one-way commit | checkpoint:decision | human answer recorded verbatim | n/a | ⬜ pending |
| 25-01-03 | 01 | 1 | REQ-gate-rule-pre-registered | T-25-01 | the rule lands alone, before any reading | git | 25-01 Task 3 heredoc: one commit by subject, only `bench/RESULTS.md`, the `git log -S'### The rule (25-01)'` anchor; no `25-02-*` log exists | ✅ | ⬜ pending |
| 25-02-01 | 02 | 2 | REQ-gate-rule-pre-registered | T-25-04 | the executed recipe is the committed one | structural | 25-02 Task 1 heredoc: extracted scripts equal the rule commit's blocks; stamps fresh; only `.planning/` changed since the rule | ✅ | ⬜ pending |
| 25-02-02 | 02 | 2 | REQ-gate-bar-reset | — | the host is quieted by the human, not by the agent | checkpoint:human-action | `go` recorded in `25-02-host-go.log` | n/a | ⬜ pending |
| 25-02-03 | 02 | 2 | REQ-gate-bar-reset, REQ-gate-rule-pre-registered | T-25-05, T-25-06, T-25-07 | no reading dropped, no commit during the session, caps enforced | log protocol | 25-02 Task 3 heredoc: every log's run-record, idle releases, one HEAD, one host, order, no overlap, budgets, 3 h cap | ✅ | ⬜ pending |
| 25-03-01 | 03 | 3 | REQ-gate-bar-reset | T-25-08 | every recorded figure is recomputed from its log | record recompute + git | 25-03 Task 1 heredocs: Runs rows vs run-records, per-arm cells and candidate recomputed; commit file set | ✅ | ⬜ pending |
| 25-03-02 | 03 | 3 | REQ-venv-constraint-probe | T-25-09, T-25-10, T-25-12, T-25-SC | hook shims untouched; outcome from evidence | hash + record | 25-03 Task 2 heredoc: linked-worktree line, shim sha256 before = after, probe after the last reading, GREEN/RED recomputed, commit file set, no code moved | ✅ | ⬜ pending |
| 25-03-03 | 03 | 3 | REQ-venv-constraint-probe | T-25-11 | no destructive git step without the human | checkpoint:decision | human answer recorded; branch state matches it | n/a | ⬜ pending |
| 25-04-01 | 04 | 4 | REQ-gate-bar-reset | T-25-13 | the bar is the human's verbatim call | checkpoint:decision | human answer recorded before any edit | n/a | ⬜ pending |
| 25-04-02 | 04 | 4 | REQ-gate-bar-reset, REQ-venv-constraint-probe | T-25-13, T-25-14, T-25-15 | L43's figures come from RESULTS.md; GREEN stamp seen red then green | record + make dry run + pytest | 25-04 Task 2 heredoc: Gate decision verbatim, one L43 with its items, GREEN `make -n -W requirements.txt .venv/.installed`, `25-04-hooks-red.log` / `25-04-hooks.log` | ✅ | ⬜ pending |
| 25-04-03 | 04 | 4 | REQ-gate-bar-reset | T-25-16 | no stale gate figure; IN-03 closed by subject | grep + git + gate | the negated stale-figure `grep -n -E` over the five files (25-04 Task 3, first verify); 25-04 Task 3 heredoc: L43 cited, IN-03, commit file set per fork, `25-04-verify.log` green | ✅ | ⬜ pending |
| 25-05-01 | 05 | 5 | REQ-pi5-claim-softened | T-25-17 | no unmeasured hardware claim | doc + README pins | 25-05 Task 1 heredoc: hardware sentence, claim gone, README:96 unchanged, `25-05-readme.log` green, idea retired | ✅ | ⬜ pending |
| 25-05-02 | 05 | 5 | REQ-reverify-recipe | T-25-18 | the skill never tells a reader to hand-write a digest | dry read + gate | 25-05 Task 2 heredoc: skill via `.claude/skills`, steps and order, §6 pointer, idea retired with the count, `25-05-verify.log` green | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No test stub, fixture or framework install is needed:

- [ ] `bench/RESULTS.md` `## The gate re-set (Phase 25)` does not exist yet -- 25-01 Task 1 creates it (the tracer).
- [ ] `.planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/investigation/` does not exist yet -- 25-01 Task 1 creates it; its logs are committed by 25-03.
- [ ] On a GREEN probe only, `tests/test_hooks.py`'s two throwaway-repo fixtures need a `requirements.txt` (D-20) -- 25-04 Task 2 sees them red first, then fixes them.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The host is quiet before run 1 | REQ-gate-bar-reset | only the human may close other sessions on a shared host (D-09) | 25-02 Task 2: read the snapshot, quiet the host, reply `go`; A1's wait then checks it |
| The rule's wording before the one-way commit | REQ-gate-rule-pre-registered | the clauses are the human's decisions plus the planner's gap-fills | 25-01 Task 2: read the drafted section, answer `commit`, `amend: ...` or `stop` |
| The bar | REQ-gate-bar-reset | the bar is a human call from the readings, never computed (SC2, L08, L34) | 25-04 Task 1: answer `accept`, `other <N> <reason>` or `no-bar <reason>`; recorded verbatim and checked by 25-04 Task 2's verify |
| Deleting `agent/venv-probe` | REQ-venv-constraint-probe | destructive git step (CLAUDE.md) | 25-03 Task 3: answer `delete`, `force-remove-and-delete` or `keep` |
| The reverify skill fires when a review finds something | REQ-reverify-recipe | not plannable in this phase (D-18) | proved by a dry read in 25-05 Task 2; exercised the next time ship refuses on a stale report |

---

## Edge Probe Coverage

The spec-less edge probe handed the planner 15 edges. Each is either a must-have truth, labelled `(edge probe E<n>, <requirement>)` in its plan, or a flagged assumption under 25-05's `## Flagged assumptions`, labelled `E<n>`. None is dropped: 10 truths (E4 a backstop) and 5 flagged assumptions.

| Edge | Requirement | Category | Disposition | Where | Proved by |
|------|-------------|----------|-------------|-------|-----------|
| E1 | REQ-gate-rule-pre-registered | boundary | truth | 25-01, `Boundary (edge probe E1, ...)` | 25-01 Task 1 pins `1\.5`, `900` and `math\.ceil` in the rule, and its `CAP=0` rehearsal gives up on the first sample (exit 3), so a wait gives up when elapsed reaches the cap; 25-02 Task 3 requires the three rows before every `IDLE` to read strictly under 1.5; 25-03 Task 1 recomputes the candidate with `math.ceil` |
| E2 | REQ-gate-rule-pre-registered | precision | truth | 25-01, `Precision (edge probe E2, ...)` | 25-03 Task 1 copies each `real` from its log as printed, recomputes every per-arm cell with `format(x, '.2f')` and `statistics.median` (an even n takes the mean of the two middle values), and the candidate with `math.ceil`, the only rounding |
| E3 | REQ-gate-bar-reset | adjacency | truth | 25-03, `Adjacency (edge probe E3, ...)` | 25-02 Task 3 (`overlapping runs`) and 25-03 Task 1 (`overlap`): each run's UTC end is at or before the next run's UTC start |
| E4 | REQ-gate-bar-reset | empty | truth, `verification: backstop` | 25-03, `Empty (edge probe E4, ...)` | 25-03 Task 1: n = 0 must print `no decisive run` and `Candidate bar (D-05): none`; the branch runs only if an arm ends with no decisive run, so a normal session does not exercise it |
| E5 | REQ-gate-bar-reset | ordering | truth | 25-03, `Ordering (edge probe E5, ...)` | 25-03 Task 1 matches the `#### Runs` rows one to one against the attempts sorted by UTC start; 25-02 Task 3 checks slot order (`out of slot order`) |
| E6 | REQ-venv-constraint-probe | adjacency | truth | 25-03, `Adjacency (edge probe E6, ...)` | 25-03 Task 2: the probe transcript's first UTC stamp is later than every `run-record`'s UTC end |
| E7 | REQ-venv-constraint-probe | empty | truth | 25-03, `Empty diff (edge probe E7, ...)` | 25-03 Task 2: GREEN needs a non-empty freeze diff holding all four predicted `> name==pin` lines, and the recorded `Outcome:` must equal that recomputation |
| E8 | REQ-venv-constraint-probe | encoding | truth | 25-03, `Encoding (edge probe E8, ...)` | 25-03 Task 2 step 8 writes `25-03-pins.log` in PEP 503 normal form; the verify requires its `pins:` line and no `MISMATCH` for GREEN, so a wrong normalisation can only read RED, never a false GREEN |
| E9 | REQ-venv-constraint-probe | ordering | truth | 25-03, `Ordering (edge probe E9, ...)` | 25-03 Task 2 step 7 drops `-e ` and `#` lines and sorts each side under `LC_ALL=C`; the verify finds each predicted move as a `> ` line |
| E10 | REQ-pi5-claim-softened | boundary | flagged assumption | 25-05, `## Flagged assumptions` | not applicable: one prose sentence with no threshold |
| E11 | REQ-pi5-claim-softened | adjacency | flagged assumption | 25-05, `## Flagged assumptions` | not applicable: no two compared things |
| E12 | REQ-pi5-claim-softened | empty | flagged assumption | 25-05, `## Flagged assumptions` | not applicable: the sentence takes no input |
| E13 | REQ-pi5-claim-softened | ordering | flagged assumption | 25-05, `## Flagged assumptions` | not applicable: two hosts named in the order the record first used them; no ordering contract |
| E14 | REQ-pi5-claim-softened | precision | truth | 25-05, `Precision (edge probe E14, ...)` | 25-05 Task 1 requires `12-CPU Apple M2 Max` and `18-CPU Apple M5 Max` in the Docker paragraph |
| E15 | REQ-reverify-recipe | unclassified | flagged assumption, manual | 25-05, `## Flagged assumptions`; the Manual-Only row above | the skill fires only when a review finds something; proved by the dry read in 25-05 Task 2 (D-18) |

Check, from the repo root: the first command prints E1 to E9 and E14, each once; the second prints E10 to E13 and E15.

```
grep -ohE 'edge probe E[0-9]+' .planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/25-0[1-5]-PLAN.md | sort -V | uniq -c
sed -n '/^## Flagged assumptions/,/^<threat_model>/p' .planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/25-05-PLAN.md | grep -oE '^- E[0-9]+'
```

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies (the four checkpoint tasks are human gates; each auto task has its own)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify (the longest run of checkpoints is two: 25-03 Task 3, 25-04 Task 1)
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Every edge the spec-less probe handed the planner (15) is a truth or a flagged assumption (`## Edge Probe Coverage`)
- [ ] Feedback latency < 600 s (holds for every task but 25-02 Task 3, the readings themselves)
- [ ] `nyquist_compliant: true` set in frontmatter (left for validate-phase)

**Approval:** {pending / approved YYYY-MM-DD}
