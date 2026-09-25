---
phase: "3"
slug: "structured-logging-at-the-composition-boundary"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-24"
---

# Phase 3 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| HTTP client → `app.model()` | Untrusted query parameters, validated once at the `GearParams` boundary (L03); only the validated object reaches a record | Gear dimensions (numbers, four literals) — public, non-personal |
| `app.py`/`cli.py` → stderr stream | Application state leaves the process; readable by anyone with `docker logs` | JSON records: event, request id, slug, params, source, duration, exception class |
| `records.py` → `uvicorn.error`/`uvicorn.access` | uvicorn's own records join the root handler (`log_config=None`, D-02) | uvicorn access/error lines rendered by this phase's formatter |
| HTTP client → `app.model()` `except` clauses | Every failure branch is attacker-triggerable on demand | Exception class name only; validated params |
| Worker subprocess → parent | `_RemoteTraceback` text crosses inside `BuildError`'s message | Kernel traceback text — kept out of records (D-06) |
| `pool.recreate_for` → stderr | The only externally visible timing of a worker replacement | Slot index, cause (`timeout`/`dead`) |
| Planning artefacts → `docs/architecture/decision_log.md` | A claim becomes a locked decision later agents treat as settled | `L20` text |
| `docs/tech_debt/active/` → `resolved/` | A `must` item leaves the watched set | Debt file + `Resolved in:` sha |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-03-01 | Information Disclosure | `records._gear_fields` / per-event helpers | medium | mitigate | `src/spur/records.py` reads no header, client address, user agent or hostname (grep: none); emitted key set pinned by `tests/test_records.py` and the `caplog` tests in `tests/test_api.py` | closed |
| T-03-02 | Tampering | `records._JsonFormatter` | low | mitigate | `json.dumps(payload, default=str)` at `records.py:87`; `test_a_field_with_a_newline_and_non_ascii_stays_one_physical_line` (`tests/test_records.py:101`) | closed |
| T-03-03 | Denial of Service | stderr stream volume | low | accept | Bounded by admission control (`MAX_QUEUED_BUILDS`, L04); shipping/rotation out of scope — see AR-03-01 | closed |
| T-03-04 | Elevation of Privilege | `_JsonFormatter.format` raising inside a log call | medium | mitigate | `default=str` at `records.py:80-87` with the stated reason in the comment | closed |
| T-03-SC (03-01) | Tampering | package-manager installs | low | accept | No install; `pyproject.toml` dependencies unchanged `782730d..HEAD` — see AR-03-02 | closed |
| T-03-05 | Information Disclosure | `records.build_failed` | low | mitigate | `"exception": type(exc).__name__` at `records.py:231`; no `exc_info`/traceback on the record (grep: only the reserved-attribute list and the docstring mention them) | closed |
| T-03-06 | Repudiation | `pool.recreate_for` | medium | mitigate | `worker_replaced(slot=i, cause=cause)` at `pool.py:151`, inside the identity guard immediately after `self.replaced += 1`; exactly one call site; `tests/test_pool.py:490` asserts exactly one `worker.replaced` record for two same-slot deaths | closed |
| T-03-07 | Denial of Service | `_build_slot` refusal branch | low | accept | One WARNING per refused request, bounded by L04 — see AR-03-03 | closed |
| T-03-08 | Tampering | attacker-controlled values in `build.failed` | low | mitigate | Validated `GearParams` fields + closed-set class name, serialized via the same `json.dumps` path as T-03-02 | closed |
| T-03-SC (03-02) | Tampering | package-manager installs | low | accept | No install; dependencies unchanged — see AR-03-02 | closed |
| T-03-09 | Repudiation | `docs/architecture/decision_log.md` | medium | mitigate | `c8b7fc8` diffstat: 1 file, 68 insertions, 0 deletions | closed |
| T-03-10 | Tampering | the debt-file move | medium | mitigate | `013997a` records the move as `R057 active/… → resolved/…`; `Resolved in: 21b8fe4` resolves (`git cat-file -t` → commit) | closed |
| T-03-11 | Information Disclosure | `README.md`, `docs/architecture/http-api.md` | low | accept | Documents field names and an env var already visible in source and in every log line; no secret exists to publish (`REQ-no-auth-default`) — see AR-03-04 | closed |
| T-03-12 | Spoofing | a debt item marked resolved without the work | high | mitigate | `make verify` green at `945219a` (96 tests, 4/4 contracts); plan ran in wave 3 after the code waves; recorded sha is a real code commit, not a placeholder | closed |
| T-03-SC (03-03) | Tampering | package-manager installs | low | accept | Documentation-only plan; no install — see AR-03-02 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-03-01 | T-03-03 | Log volume is bounded by the same admission control that bounds builds; shipping, rotation and retention are explicitly outside this phase (03-CONTEXT.md §Phase Boundary) | plan author (03-01 threat register), confirmed at audit | 2026-09-24 |
| AR-03-02 | T-03-SC (03-01, 03-02, 03-03) | Stdlib-only phase (D-01, L20); `pyproject.toml` dependencies unchanged across the phase, so L12's pinned closure and the supply-chain surface are untouched | plan author, confirmed at audit (`git diff 782730d..HEAD -- pyproject.toml`: no dependency change) | 2026-09-24 |
| AR-03-03 | T-03-07 | The refusal path is the cheapest path through the endpoint and is itself the bounding mechanism (L04); one WARNING per refusal adds no new amplification | plan author (03-02 threat register), confirmed at audit | 2026-09-24 |
| AR-03-04 | T-03-11 | Field names and `SPUR_LOG_LEVEL` are already public in source and on the wire; the application holds no secret (`REQ-no-auth-default`) | plan author (03-03 threat register), confirmed at audit | 2026-09-24 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-24 | 15 | 15 | 0 | execute-phase `verify:post` security hook (L1 grep-depth; register authored at plan time; no auditor spawn per short-circuit rule) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-24
