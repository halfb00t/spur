---
phase: "25"
slug: "gate-bar-re-set-venv-probe-ledger-close"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-14"
---

# Phase 25 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

The register was authored at plan time (every PLAN carries a `<threat_model>` block). ASVS level 1, block on `high`. Classification is grep-depth against the committed record (`bench/RESULTS.md`, the SUMMARYs, the phase commits); no auditor was spawned (short-circuit rule: `threats_open: 0`, register authored at plan time, level 1).

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| rule commit → readings | the pre-registered rule (`1d5ce8a`) is history before any reading; the executed recipe is extracted from that commit | the rule text, the two shell blocks |
| host → kept logs → record | untracked `investigation/` logs become the committed record in `bench/RESULTS.md`; figures are copied, never typed | `run-record` trailers, `real`, loads, UTC windows |
| main checkout `.git/hooks` ↔ linked worktree | the venv probe installs only inside `.claude/worktrees/venv-probe`; the three hook shims of the main checkout must not move | pip installs, hook shim bytes |
| record → decision log | `#### Gate decision` (the human's verbatim answer) feeds L43; the bar is a human call, never computed | the bar, the `none` candidate, the host line |
| human checkpoints → git | branch deletion and the rule's one-way commit are human decisions, recorded verbatim | `git branch -d`, `commit` |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-25-01 | Repudiation | the rule's place in history | high | mitigate | `1d5ce8a` touches only `bench/RESULTS.md`; `git log -S'### The rule (25-01)'` names it; no reading log existed at commit time (25-01 Task 3 verify) | closed |
| T-25-02 | Tampering | the rule text after the first reading | high | mitigate | `### The rule (25-01)` at HEAD is byte-identical to `1d5ce8a` (checked by 25-03 and 25-04); the human's override of the A1 clause is recorded in the readings sections, not in the rule | closed |
| T-25-03 | Denial of service | a recipe with a broken kill or a lost exit status | medium | mitigate | rehearsal logs `25-01-rehearsal-{ok,cap,armA,armB}.log` (cap exit 124, exit-status line) committed in `1f7ce01` | closed |
| T-25-SC (25-01) | Tampering | npm/pip/cargo installs | high | accept | the plan installs nothing (accepted risk AR-1) | closed |
| T-25-04 | Tampering | the recipe actually executed | high | mitigate | `25-02-wait.sh` / `25-02-run.sh` extracted from the rule commit and compared byte for byte (25-02 Task 1) | closed |
| T-25-05 | Repudiation | a red attempt dropped or replaced | high | mitigate | every attempt has its own stem and log: A1, B1 green; A2 aborted by the human, logged, no retry; no red run | closed |
| T-25-06 | Tampering | a commit or a gate-shaped command during the session | medium | mitigate | measured HEAD `9b68f6d` committed 10:45:05Z; readings 13:17:34Z–13:26:04Z; next commit `861e2cc` at 13:28:02Z; tracked tree clean after the last run | closed |
| T-25-07 | Denial of service | a hung run or a never-quiet host wedging the session | medium | mitigate | the 900 s wait cap fired 7 times (A1), the run cap was armed (`timeout -k 30 900`), the session was cut by the human after two readings; both caffeinate facts logged | closed |
| T-25-SC (25-02) | Tampering | npm/pip/cargo installs | high | accept | `make -n verify` printed no install before A1 (stamp check in `25-02-host-go.log`); accepted risk AR-2 | closed |
| T-25-08 | Repudiation | `#### Runs` and `#### Per arm` figures | high | mitigate | the three rows carry `real` 195.23 / 179.21 / 115.20 equal to their logs' `/usr/bin/time` lines and `run-record` trailers (re-checked by the orchestrator at verification); both arms print `no decisive run`, candidate `none` | closed |
| T-25-09 | Tampering | `.git/hooks/{pre-commit,commit-msg,pre-push}` | high | mitigate | probe ran only in `.claude/worktrees/venv-probe`; sha256 of the three shims equal before and after; line 6 names the main `.venv/bin/python` (`25-03-shims-*.log`, commit `dbc50d9`) | closed |
| T-25-10 | Tampering | dependency drift recorded as green | medium | mitigate | GREEN recomputed by the 25-03 Task 2 verify from the logs: 31/31 pins, `pip check` clean, `make verify` exit 0, the four predicted moves in the freeze diff | closed |
| T-25-11 | Denial of service | `git worktree remove --force`, `git branch -D` | medium | mitigate | plain `git worktree remove` succeeded; `git branch -d agent/venv-probe` at the human's `delete` (`8bb1a24`) | closed |
| T-25-12 | Information disclosure | a venv or worktree files committed by a broad `git add` | low | mitigate | `1f7ce01` = 20 named paths, `dbc50d9` = `bench/RESULTS.md` + 10 named probe logs (file sets checked by the plan verifies); `.claude/worktrees/` is gitignored | closed |
| T-25-SC (25-03) | Tampering | npm/pip/cargo installs | high | mitigate | the probe installed only `pyproject.toml`'s existing `[dev]` extras under the 31 pins of `requirements.txt`; `pip check` and the per-pin check are recorded | closed |
| T-25-13 | Repudiation | `#### Gate decision` and L43's bar | high | mitigate | the human's sentence is recorded verbatim under `#### Gate decision` with `Candidate bar (D-05): none` and `Bar: 300 s`; L43 quotes the `none` line and the bar | closed |
| T-25-14 | Tampering | L43's figures | medium | mitigate | L43 carries the host line and `no decisive run` for both arms, citing the RESULTS.md sections by name (`34270c8`) | closed |
| T-25-15 | Tampering | `$(STAMP)` constraint (GREEN) | medium | mitigate | `25-04-hooks-red.log` (`2 failed, 4 passed`) then `25-04-hooks.log` (`6 passed`); `make -n -W requirements.txt .venv/.installed` shows the constrained install; `requirements.txt` untouched | closed |
| T-25-16 | Denial of service | the main checkout's hook shims after `.pre-commit-config.yaml` changes | low | accept | `make verify` re-ran `pre-commit install`; line 6 of `.git/hooks/pre-commit` recorded afterwards (25-04 SUMMARY); accepted risk AR-3 | closed |
| T-25-SC (25-04) | Tampering | npm/pip/cargo installs | high | accept | the plan installs nothing; existing venvs left alone (D-13); accepted risk AR-4 | closed |
| T-25-17 | Repudiation | README's hardware claim | low | mitigate | the Pi 5 clause removed, `12-CPU Apple M2 Max` and `18-CPU Apple M5 Max` named (25-05 Task 1 verify, `92953bb`) | closed |
| T-25-18 | Tampering | `VERIFICATION.md` digests via the skill | medium | mitigate | `.ai_skills/reverify-phase/SKILL.md` names `covered_digest` as the verifier's to write and routes through `/gsd-execute-phase` (25-05 Task 2 verify, `ac129dc`) | closed |
| T-25-SC (25-05) | Tampering | npm/pip/cargo installs | high | accept | the plan installs nothing; accepted risk AR-5 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-1 | T-25-SC (25-01) | the plan installs no package; RESEARCH's Package Legitimacy Audit lists none for the phase | planner (plan-time disposition `accept`) | 2026-10-14 |
| AR-2 | T-25-SC (25-02) | the plan installs no package; `make -n verify` named no install before A1 | planner (plan-time disposition `accept`) | 2026-10-14 |
| AR-3 | T-25-16 | the hook re-install uses the same `.venv/bin/python`; line 6 verified after the change | planner (plan-time disposition `accept`) | 2026-10-14 |
| AR-4 | T-25-SC (25-04) | the plan installs no package; on GREEN existing venvs are left alone (D-13) | planner (plan-time disposition `accept`) | 2026-10-14 |
| AR-5 | T-25-SC (25-05) | the plan installs no package | planner (plan-time disposition `accept`) | 2026-10-14 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-14 | 23 | 23 | 0 | execute-phase orchestrator (verify:post secure-phase step, L1 grep-depth) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-14
