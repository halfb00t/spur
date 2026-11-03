---
phase: "30"
slug: "scope-seam-and-gear-safety-guard"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-23"
---

# Phase 30 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| origin remote → `scripts/gear_unchanged.py` | The check fetches tag `v0.6` and archives its tree | git objects from this repository's own remote |
| pre-commit hook → working repository | The check runs inside every commit's hook | read-only git subcommands; must not mutate the index or `.git/shallow` |
| shaft modules → gear modules / serving process | Import contracts keep shaft code from reaching gear maths or the CAD kernel | Python imports (static) |
| HTTP client → `/api/model` | Unchanged route surface; seam moved behind it | query parameters, 503 refusal text |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-30-01 | Tampering | tag `v0.6` moved or deleted on origin | medium | accept | Annotated pushed tag; a deleted tag fails with its cause (D-05) | closed |
| T-30-02 | Repudiation | `schema_of` self-comparison via shadowed import | high | mitigate | `-P` + `spur.__file__` assert (`scripts/gear_unchanged.py:22,68,112`); `test_the_probe_refuses_a_tree_it_did_not_import` | closed |
| T-30-03 | Tampering | `baseline_src` archive path traversal | medium | mitigate | `tar.extractall(dest, filter="data")` (`scripts/gear_unchanged.py:139`) | closed |
| T-30-04 | Tampering | git calls in pre-commit hook corrupting the commit | high | mitigate | `--no-optional-locks`, read-only subcommands (`scripts/gear_unchanged.py:75`); `test_the_check_leaves_the_repository_as_it_found_it` | closed |
| T-30-05 | Information disclosure | git fetch stderr printed on failure | low | accept | Failure-only, names the remote, no credentials read | closed |
| T-30-06 | Tampering | depth-1 fetch making a full clone shallow | high | mitigate | `--is-shallow-repository` gate (`scripts/gear_unchanged.py:87`); `test_a_missing_tag_is_fetched_without_making_a_full_clone_shallow` | closed |
| T-30-07 | Repudiation | missing baseline read as a pass | high | mitigate | SystemExit naming the cause; `test_a_missing_tag_with_an_unreachable_origin_fails_naming_the_cause` | closed |
| T-30-08 | Tampering | subprocess argument injection | low | mitigate | List-form argv, constant tag and paths, no `shell=True` (grep: none) | closed |
| T-30-09 | Repudiation | decision log L02/L05 rewritten instead of amended | low | mitigate | `git diff --numstat v0.6 -- docs/architecture/decision_log.md` reads `41 0` | closed |
| T-30-10 | Tampering | mistyped forbidden module silently kept by import-linter | high | mitigate | `test_every_module_a_contract_names_exists_and_the_layout_is_frozen` (`tests/test_seam.py`) | closed |
| T-30-11 | Denial of service | shaft code pulling CAD kernel into serving process (L17) | medium | mitigate | Contracts C1, C3; `make lint-imports` reads `10 kept, 0 broken` | closed |
| T-30-12 | Tampering | route or query key added to a gear route | high | mitigate | Route-prefix and query-key pins in `tests/test_seam.py` | closed |
| T-30-13 | Repudiation | placeholder with unfinished-work markers | low | mitigate | AST docstring-only check; `make no-fake-done` in `make verify` | closed |
| T-30-14 | Tampering | `_serve_model` move changing cache key / admission / error mapping | high | mitigate | Pure-move check modulo named substitutions (`q.quality`→`quality`, `_gear(q)` kept in caller); unedited suites; `gear.unchanged` green | closed |
| T-30-15 | Denial of service | admission control lost in the move | medium | mitigate | `_build_slot` still wraps the build (`src/spur/app.py:264`); saturated tests incl. `test_a_saturated_service_names_its_queue_in_parts` pass | closed |
| T-30-16 | Information disclosure | 503 message | low | accept | Carries only the queue size, already exposed by `/api/health` | closed |
| T-30-17 | Repudiation | gate reading recorded without load/host/log | low | mitigate | Meta log with load before/after, HEAD, host (`30-05-verify-meta.log`) | closed |
| T-30-SC | Tampering | npm/pip/cargo installs | low | accept | No package installed in any plan; dependency tables untouched | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-30-01 | T-30-01 | Tag is the single source of truth (D-02); a missing tag fails loudly, never passes | plan-phase (30-01 threat model) | 2026-10-23 |
| AR-30-02 | T-30-05 | Stderr printed on failure only; script reads no credentials | plan-phase (30-01 threat model) | 2026-10-23 |
| AR-30-03 | T-30-16 | Queue size already public via `/api/health` `queue_available` | plan-phase (30-04 threat model) | 2026-10-23 |
| AR-30-04 | T-30-SC | No dependency installed or changed in this phase | plan-phase (all plans) | 2026-10-23 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-23 | 18 | 18 | 0 | execute-phase orchestrator (L1 grep-depth, auditor skipped per short-circuit rule) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-23
