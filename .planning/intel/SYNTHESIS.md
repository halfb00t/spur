# Synthesis summary

Entry point for `gsd-roadmapper`. Produced by `gsd-doc-synthesizer` from 22 classified
documents in `CLASSIFICATIONS_DIR = .planning/intel/classifications/`. Mode: `new` (no
prior `.planning/` files existed to merge against).

## Doc counts by type

| Type | Count |
|---|---|
| ADR | 1 (holds 16 individually locked decisions, L01–L16) |
| SPEC | 15 |
| PRD | 0 |
| DOC | 6 |
| **Total** | **22** |

All 22 classified at high confidence; none `UNKNOWN`.

## Decisions locked

16 (`L01`–`L16`), all from `docs/architecture/decision_log.md`, all `locked: true` (basis
recorded as INFO in `INGEST-CONFLICTS.md` — the file has no `Status: Accepted`
frontmatter; lock status comes from the file's own declaration and `AGENTS.md`'s
attribution). No LOCKED-vs-LOCKED contradictions found. See `decisions.md`.

## Requirements extracted

11, all derived from the root `README.md` and the 15 SPECs — there is no PRD in this
ingest set, so none were manufactured. IDs: `REQ-involute-geometry`,
`REQ-bore-and-fillets`, `REQ-face-recesses`, `REQ-measurement-aids`,
`REQ-shareable-links`, `REQ-stl-step-export`, `REQ-three-interfaces`,
`REQ-error-contract`, `REQ-no-auth-default`, `REQ-docker-multiarch`, `REQ-cli-parity`.
Acceptance is marked absent on 4 of the 11 where no test or explicit criterion was cited
in the ingested SPECs. See `requirements.md`.

## Constraints

36, from all 15 SPECs. Type breakdown: `api-contract` 9, `schema` 6, `nfr` 15,
`protocol` 6. Covers the CLI, HTTP API, web UI, packaging/Docker, the gear-maths
(`calc.py`) module, and the solid-model (`model.py`) module. See `constraints.md`.

## Context topics

6, one per ingested DOC: product summary (README.md), development workflow
(HOW_TO_DEVELOP.md), coding values and standards (CODING_VALUES.md), requirements
taxonomy — intended, not populated (docs/requirements/README.md), and two historical
records — the 2026-09-21 review (superseded findings) and its remediation plan/outcome.
See `context.md`.

## Conflicts

0 blockers, 0 competing variants, 5 info entries. No gate applies — safe to route.

The 5 INFO entries (full detail in `../INGEST-CONFLICTS.md`):
1. Decision log's LOCKED status set by manifest override, not frontmatter.
2. Historical review findings (`docs/review-2026-09-21.md`, F1–F8) superseded by the live
   SPECs and the remediation record (`docs/plan-2026-09-21.md`) — treated as history, not
   extracted as live requirements or constraints.
3. Tech-debt cross-references from SPECs preserved as provenance only — `docs/tech_debt/`
   itself was excluded from this ingest by user decision.
4. `docs/requirements/README.md` is an intended-taxonomy placeholder, not a requirements
   source.
5. No PRD in the ingest set — `requirements.md` derived from README + SPECs instead.

## Files in this directory

- `decisions.md` — 16 locked ADR entries (L01–L16)
- `requirements.md` — 11 requirements derived from README + SPECs
- `constraints.md` — 36 technical constraints from the 15 SPECs
- `context.md` — 6 topic-keyed notes from the 6 DOCs
- `../INGEST-CONFLICTS.md` — the full conflict detection report (3 buckets)
