---
phase: "29"
slug: "ubuntu-26-final-reading"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-22"
---

# Phase 29 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

The phase closed on its close condition (outcome `not fired`, the human's `close` at Task 2).
No `ubuntu-latest` run named Ubuntu 26.04, so the green and red paths never ran. Their
mitigations are recorded as not exercised, not as verified in operation. No code under
`src/`, no endpoint and no workflow file changed.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| GitHub Actions run logs → committed record | logs read with the gh CLI's own auth (read calls only), committed under `.planning/` | runner image names and versions, run metadata; public to anyone who can see the runs |
| the agent → `.github/workflows/ci.yml` | a runner-label edit changes the environment of every required check | none crossed: the file is unchanged against `v0.5` |
| the agent → the planning ledger | ROADMAP, REQUIREMENTS, STATE and the debt ledger say what is done and what is deferred | completion and deferral claims |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-29-01 | Repudiation | the first 26.04 run's classification | medium | mitigate | Each read's per-job image token and version are kept in `investigation/29-01-window-<stamp>.tsv`: 30 rows at 13:13Z, all `ubuntu-24.04`. The 29-VERIFICATION.md re-listed the window from gh, and four job logs it re-fetched matched their rows. Keeping whole job logs applies only to a reading set; none existed. | closed |
| T-29-02 | Tampering | `.github/workflows/ci.yml` pinned or edited by the agent | high | mitigate | Task 2 is `gate="blocking-human"` (29-01-PLAN.md:367). `git diff --exit-code v0.5 -- .github/workflows/ci.yml` is clean at HEAD. No L46 was logged and no pin was made. | closed |
| T-29-03 | Spoofing | a pinned-label run or a misread log taken for the first `ubuntu-latest` run on 26.04 | medium | mitigate | The image is the token after `Image: ` in each job log, compared by string equality. No window job read `ubuntu-26.04`, so the head-`ci.yml` check never had a run to test. | closed |
| T-29-04 | Information disclosure | CI logs committed under `.planning/` | low | accept | see Accepted Risks Log | closed |
| T-29-05 | Denial of service | a red 26.04 image turns every PR's required jobs red | medium | mitigate | The red path offers `pin` and `hold` to the human, as planned. That path was not reached, because the outcome was `not fired`. The debt item stays `active` with its trigger restated, so a later red is still routed to the human. | closed |
| T-29-06 | Repudiation | a requirement reported complete, or the item retired, without a reading | medium | mitigate | `29-01-SUMMARY.md` has `requirements-completed: []`. The debt item is still in `docs/tech_debt/active/`. The requirement was moved to Future Requirements with the human's approval (c16daa8). The decision line quotes the human's literal reply (c5f14f6). | closed |
| T-29-SC | Tampering | npm/pip/cargo installs | low | accept | see Accepted Risks Log | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-29-01 | T-29-04 | The workflow prints no secret. The committed tsv files hold only run metadata and image names and versions, the same data GitHub shows on each run (T-26-05 precedent). A grep of `investigation/` for `token`, `secret` and `password` matched nothing. | plan 29-01 threat model | 2026-10-22 |
| AR-29-02 | T-29-SC | No package was installed. The plan read with the installed `gh` and `.venv` only. | plan 29-01 threat model | 2026-10-22 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-22 | 7 | 7 | 0 | gsd-secure-phase orchestrator (ASVS L1 grep depth; auditor skipped per the short-circuit rule) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-22
