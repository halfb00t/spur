---
phase: "13"
slug: "latency-bar"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-02"
---

# Phase 13 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.
> Register authored at plan time (every PLAN carries a `<threat_model>`); verified after
> execution at ASVS L1 grep depth by the execute-phase orchestrator's `verify:post`
> secure-phase step. Evidence cites file:line, commit sha, or the SUMMARY that recorded it.

---

## Trust Boundaries

| Boundary | Description | Declared by |
|----------|-------------|-------------|
| harness -> server under test | the harness trusts that whatever answers on its base URL is the server this session started | 13-01 |
| raw samples -> printed figures | every number later quoted must be derivable from committed raw files | 13-01 |
| parent harness -> poller subprocess | a crashed parent can orphan the poller, which keeps writing | 13-01 |
| prediction -> evidence | a prediction edited after the data turns a test into a description | 13-02 |
| agent -> the human's other containers | stopping a container that is not this project's is the human's act | 13-02 |
| one session -> the next | a session's server, poller or lock left behind contaminates the next session's measurement | 13-03 |
| raw data -> ruling | a ruling chosen after seeing the data | 13-03 |
| measurement -> published bar | the decisive session's verdict decides whether L18's caveat is closed or the bar's definition changes | 13-04 |
| captured output -> record | numbers move from a capture file into bench/RESULTS.md by hand | 13-04 |
| decision -> harness code | the bar's definition or protocol changes in the instrument every later run is read with | 13-05 |
| re-measure -> verdict | a changed harness re-read until it passes would be tuning | 13-05 |
| composed scenario -> the bar's no-argument run | a third registered scenario would otherwise ride every future bar run | 13-06 |
| client -> the server's admission control | which four requests are admitted decides whether SC3 measures the worst row at all | 13-06 |
| SC3 server -> later sessions | a worker it times out is replaced and must not pollute a bar session | 13-06 |
| record -> future readers | L32, the Dockerfile comment and the resolved debt are what later phases and the container's maintainers read as fact | 13-07 |
| agent -> the human's containers | restarting fleet-user is the human's act | 13-07 |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation / Evidence | Status |
|-----------|----------|-----------|----------|-------------|-----------------------|--------|
| T-13-01 | Spoofing | session.py / run_experiment.py base URL | high | mitigate | `run_experiment.py:200` `--base-url required=True` (no default); `session.py:146` sets `SPUR_PORT=8001`, `:167-171` aborts unless the 8001 listener PID is its own child | closed |
| T-13-02 | Tampering | poller JSONL | medium | mitigate | `poller.py:43-44` refuses an existing `--out`; `run_experiment.py:281` refuses existing outputs, `:346-349` `finally:` stop-file then kill; `session.py:29` `.session.lock` | closed |
| T-13-03 | Repudiation | summary.json figures | medium | mitigate | `tabulate.py:254` `--check` recomputes every series from JSONL; ran clean on all twelve campaign runs (13-03-SUMMARY) | closed |
| T-13-04 | Denial of service (local) | orphaned server / workers on 8001 | low | mitigate | `session.py:150` `start_new_session=True`, `:181-185` `killpg` SIGTERM then SIGKILL; no listener on 8001 after every session (spot-checked after 13-04, 13-06, 13-07) | closed |
| T-13-05 | Repudiation | `13-LATENCY-INVESTIGATION.md ## Predictions` | medium | mitigate | pre-registered in `67eeefb` (subject `pre-register`) before any campaign run; 13-03's Predictions-diff gate ran clean against it (13-03-SUMMARY Threat Flags) | closed |
| T-13-06 | Elevation of privilege | `docker stop fleet-user` | low | mitigate | human-at-keyboard checkpoint (13-02 Task 3, resume text `approved`); the agent only read `docker ps`; fleet-user was already `Exited` and was never touched | closed |
| T-13-07 | Information disclosure | host-state records committed | low | accept | accepted at plan time — same fields `bench/RESULTS.md` has carried since Runs 3-4; no paths, users or secrets (see Accepted Risks Log) | closed |
| T-13-08 | Tampering | overlapping sessions | medium | mitigate | `.session.lock` + port-8001 preflight; sessions launched one at a time after the prior `status.json` was read; no commit or test run during any session (orchestrator-enforced host discipline) | closed |
| T-13-09 | Repudiation | non-decisive / aborted sessions presented as clean | medium | mitigate | every committed `status.json` carries `state` and `decisive`: A1,B1,C1,A2,B2,C2 `done/true`; bar-1, bar-2 `done/false`; bar-3 `done/true`; sc3 `aborted/false` — all listed in `bench/RESULTS.md` | closed |
| T-13-10 | Repudiation | a ruling written after the data | medium | mitigate | Predictions diff gate against `67eeefb` passed before the Verdict was written; Verdict applies the pre-registered rule by name (13-03-SUMMARY) | closed |
| T-13-11 | Tampering | the bar verdict | high | mitigate | verdict rule E8/E9 and retry rule fixed in 13-04-PLAN before any number; attempts committed in order `83bb448` (bar-1, non-decisive) → `fe17199` (bar-2, non-decisive) → `e15437e` (bar-3, decisive, outcome (a)); the two non-decisive attempts' printed ratios never counted | closed |
| T-13-12 | Spoofing | the server measured | high | mitigate | `session.py` preflight + listener-PID check; `bar-3.status.json` `host.server_env == {"SPUR_PORT": "8001"}`; `--base-url http://127.0.0.1:8001` | closed |
| T-13-13 | Repudiation | RESULTS.md bar tables | medium | mitigate | 13-04 Task 1 verify (every printed ratio in the captures appears in the section) passed; 13-04-SUMMARY `Self-Check: PASSED` | closed |
| T-13-14 | Tampering | `bench/latency.py` pass rule | high | mitigate | not instantiated — 13-05 did not execute (outcome (a), `52ca7b7`); no pass-rule change exists; `scenario_single`/`scenario_concurrent` byte-identical to `9f26052` | closed |
| T-13-15 | Denial of service | the gate formula | medium | mitigate | not instantiated — no formula change (13-05 not executed) | closed |
| T-13-16 | Repudiation | silent second change after a miss | medium | mitigate | not instantiated — no miss, D-11 not reached (13-05-SUMMARY) | closed |
| T-13-17 | Tampering | `bench/latency.py main()` default | high | mitigate | `bench/latency.py:332` `DEFAULT_SCENARIOS = ("concurrent", "single")`; `tests/test_bench.py:591` pins it; the text from `def scenario_single(` to `_SCENARIOS: dict` byte-identical to `9f26052` (13-06 Task 1 verify). Note for review: `_sample_while_building` (a helper on the bar's sampling path, outside the promised byte-range) was generalized with a type parameter in `47613fd`, after bar-3 was measured; tests and `mypy --strict` pass | closed |
| T-13-18 | Repudiation | SC3 reported without the worst row holding a slot | medium | mitigate | `run_composed` raises if the worst row is served without holding a slot or never holds one within 10 s; the RESULTS.md SC3 table names all ten request outcomes from `sc3.server1.records.jsonl` | closed |
| T-13-19 | Denial of service (local) | timed-out / replaced workers | low | accept | accepted at plan time — SC3 ran last on its own fresh 8001 server, torn down by `session.py`; `spur-spur-1` on 8000 never addressed (see Accepted Risks Log). The run surfaced a real server defect (same-slot timeout-cleanup race → undocumented 500), filed as `must` debt `docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md` — a correctness defect in the API contract, not a security exposure beyond this accepted local DoS | closed |
| T-13-20 | Information disclosure | committed server records | low | accept | accepted at plan time — records carry public gear parameters, request ids and timings; access lines dropped (see Accepted Risks Log) | closed |
| T-13-21 | Repudiation | L32 / Dockerfile numbers | medium | mitigate | 13-07 Task 1 verify: every ratio in L32 traces to `bench/RESULTS.md` or the write-up; Dockerfile diff is comment-only | closed |
| T-13-22 | Tampering | L18 and earlier decision-log entries | medium | mitigate | `git diff --numstat 9f26052 -- docs/architecture/decision_log.md` → `90 0`; L32 is the last and only new entry | closed |
| T-13-23 | Repudiation | the debt retired without its evidence | low | mitigate | `docs/tech_debt/resolved/2026-09-23-concurrent-latency-bar-waived.md` `Status: resolved`, `Resolved in: 6709953`; INDEX row cites the same sha | closed |
| T-13-24 | Elevation of privilege | `docker start fleet-user` | low | mitigate | human-at-keyboard checkpoint (13-07 Task 2, resume text `approved`); the agent only read docker state; fleet-user left `Exited`, matching its pre-phase state | closed |
| T-13-SC | Tampering | npm/pip/cargo installs (declared in all seven plans) | low | accept | no package was installed in this phase: `git diff 9f26052 -- pyproject.toml requirements*.txt` is empty; the investigation uses httpx, argparse, statistics, subprocess only (see Accepted Risks Log) | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on (`high`) count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-13-01 | T-13-07 | host-state records (container names, load averages, top-CPU process names) are the same fields `bench/RESULTS.md` has recorded since Runs 3-4; no paths, users or secrets | plan-phase register, human-approved plans (`b524ed2`) | 2026-10-01 |
| R-13-02 | T-13-19 | SC3's timed-out and replaced workers are local to a fresh 8001 server that `session.py` tears down; the production container on 8000 is never addressed | plan-phase register, human-approved plans (`b524ed2`) | 2026-10-01 |
| R-13-03 | T-13-20 | committed server records carry only public gear parameters, request ids and timings; access-log lines are dropped | plan-phase register, human-approved plans (`b524ed2`) | 2026-10-01 |
| R-13-04 | T-13-SC | no package is installed in this phase (verified: no dependency-manifest diff since `9f26052`) | plan-phase register, human-approved plans (`b524ed2`) | 2026-10-01 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-02 | 25 (24 numbered + T-13-SC declared ×7) | 25 | 0 | execute-phase orchestrator — secure-phase `verify:post` step, ASVS L1, short-circuit (register authored at plan time, threats_open 0) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-02
