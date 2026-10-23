---
phase: "27"
slug: "ledger-tests-and-harness"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-20"
---

# Phase 27 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.
> Register authored at plan time in 27-01..27-06 `<threat_model>`; verified at ASVS L1 (grep depth) during execute-phase 27.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| local spike branch -> shared remote and GitHub Actions | throwaway branch runs the workflow on `pull_request` in the repo's own runners | test-step command, `ps` listing print |
| CI log -> committed record | whole job logs committed under `.planning/` | CI logs, `ps` argv lines (no environment) |
| a test's verdict -> the gate's green | a guard that passes on nothing reads as proof | test outcomes |
| temporary breaks -> a commit | deliberate mutations exist only between a red run and its revert | source under test |
| test harness -> OS process groups | teardown sends SIGTERM/SIGKILL to a group it spawned | signals |
| `ps` output -> teardown verdict | an external reader decides wait and report | process listing |
| `src/spur/model.py` -> the part a user downloads | the one product file this phase touches | built solid, printed numbers |
| bench output -> `bench/RESULTS.md` readers | a host block names the code it measured | git HEAD, timings |
| harness failure text -> person fixing a red gate | advice someone follows on their machine | shell commands |
| AST pins -> the gate's meaning | pins make a green browser gate mean the browser ran | source text |
| measurement -> comment and record | readers trust comment and record as observed (L08) | counts, run ids |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-27-01 | Tampering | spike PR merged by mistake | medium | mitigate | `gh pr view 43` reads `CLOSED`, `mergedAt: null` | closed |
| T-27-02 | Tampering | temporary print / workflow edit on the phase branch | medium | mitigate | `git diff --exit-code v0.5 -- .github/workflows/ci.yml` exits 0; `git grep spur-group-listing -- tests .github` empty | closed |
| T-27-03 | Repudiation | member set read from a partial log | low | mitigate | three whole job logs kept: `investigation/27-01-run-39428298442-{test,image,vendor-bundle}.log` | closed |
| T-27-04 | Information Disclosure | CI logs and `ps` command lines committed | low | accept | see Accepted Risks AR-27-01 | closed |
| T-27-05 | Elevation of Privilege | workflow change on a same-repo `pull_request` | low | accept | see Accepted Risks AR-27-02 | closed |
| T-27-06 | Repudiation | totality test passing on empty buckets | medium | mitigate | `tests/test_trochoid.py -k slug_is_total` green; red twice (`investigation/27-02-red-slug-{junction,root-curve}.log`) | closed |
| T-27-07 | Tampering | temporary `calc.py` mutation committed | medium | mitigate | `git diff --exit-code v0.5 -- src/spur/calc.py src/spur/params.py` exits 0 | closed |
| T-27-08 | Tampering | temporary pre-seed test or broken `_has_key` committed | low | mitigate | `git grep tmp_preseed -- tests` empty; walker test green | closed |
| T-27-09 | Denial of Service | commit slice crossing L36's 30 s | low | mitigate | `make verify.fast` 932 passed, real 11.32 s (27-06) | closed |
| T-27-10 | Denial of Service | orphaned uvicorn group surviving a failed `ps` | medium | mitigate | `tests/process_group.py:67` `os.killpg(pgid, sig)` before any read; `tests/test_process_group.py` 6 passed (re-run after WR-03, 2026-10-20) | closed |
| T-27-11 | Tampering | signalling a reused pid's group after reaping | medium | mitigate | signal-first test asserts no wait/poll precedes SIGTERM; green | closed |
| T-27-12 | Denial of Service | unit test or leader-only re-run leaking processes | low | mitigate | `pgrep -fl uvicorn` empty after the phase | closed |
| T-27-13 | Tampering | leader-only mutation committed | low | mitigate | `os.killpg(pgid, sig)` present, no leader-only `os.kill(` in `tests/process_group.py` | closed |
| T-27-14 | Tampering | D-03 moving a built part or printed number | medium | mitigate | `git diff --exit-code v0.5 -- tests/regression/` exits 0; `src/` diff is `model.py` only; regression + chamfer 141 passed | closed |
| T-27-15 | Repudiation | bench host block naming an unreadable HEAD | low | mitigate | `tests/test_bench.py -k host_state` 2 passed; red first (`investigation/27-04-red-host-state.log`) | closed |
| T-27-16 | Tampering | launch change opening a browser-less pass path | medium | mitigate | `tests/test_browser_pins.py` 9 passed (re-run after WR-01/WR-02, 2026-10-20); fail-closed run logged (`investigation/27-05-launch-fail-closed.log`) | closed |
| T-27-17 | Tampering | statement-scoped allowance letting an environ read slip | low | mitigate | synthetic sources red against the line rule (`investigation/27-05-red-environ-rule.log`); pins green | closed |
| T-27-18 | Denial of Service | advice deleting the browser cache | low | mitigate | `.venv/ms-playwright` and `.venv/.browser` still present; advice removes only the stamp | closed |
| T-27-19 | Repudiation | a RESULTS reading or L40 sentence rewritten | medium | mitigate | `git diff --numstat v0.5`: `bench/RESULTS.md` 676/0, `docs/architecture/decision_log.md` 2/0 | closed |
| T-27-20 | Repudiation | comment naming an unobserved Linux member set | medium | mitigate | `tests/browser_session.py:64` cites run 39428298442, `ubuntu-24.04` 20261012.334.1, 2026-10-20 | closed |
| T-27-21 | Repudiation | triage row citing a sha not on the branch | low | mitigate | every hex id in `27-TRIAGE.md` resolves via `git cat-file -e`; the two non-ancestors are named beside their squash commits | closed |
| T-27-SC | Tampering | npm/pip/cargo installs | low | accept | see Accepted Risks AR-27-03 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-27-01 | T-27-04 | `ps -o command=` prints argv, not the environment; the workflow prints no secret; the committed logs are the ones GitHub already shows on PR #43 | plan 27-01 threat model | 2026-10-20 |
| AR-27-02 | T-27-05 | no new secret, job, action or permission; only the test step's command differs, on a throwaway branch closed unmerged | plan 27-01 threat model | 2026-10-20 |
| AR-27-03 | T-27-SC | Phase 27 adds no package; the throwaway CI run installs only what the shipped workflow installs | plans 27-01..27-06 threat models | 2026-10-20 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-20 | 22 | 22 | 0 | secure-phase (orchestrator, ASVS L1 grep depth) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-20

## Security Audit 2026-10-20

| Metric | Count |
|---|---|
| Threats found | 22 |
| Closed | 22 |
| Open | 0 |
