## Conflict Detection Report

### BLOCKERS (0)

None. No LOCKED-vs-LOCKED ADR contradictions were found (the single ADR in this ingest,
`docs/architecture/decision_log.md`, holds 16 individually locked decisions, L01–L16, none
of which contradict one another). Mode is `new`, so there is no existing locked
`CONTEXT.md` decision to contradict. No `UNKNOWN`/low-confidence classification exists in
the set (22 of 22 docs classified high confidence). Cycle detection over the `cross_refs`
graph restricted to these 22 docs found 0 cycles (run by the orchestrator before spawning
this synthesis; re-verified against the classification set here).

### WARNINGS (0)

None. There are 0 PRDs in this ingest set, so there is no competing-acceptance-variant
case to raise.

### INFO (5)

[INFO] Decision log's LOCKED status set by manifest override, not frontmatter
  Note: `docs/architecture/decision_log.md` carries no `Status: Accepted` frontmatter per
  entry. `locked: true` was applied via `manifest_override` on orchestrator instruction,
  based on the file's own opening declaration ("Locked decisions... Agents must not
  re-litigate a logged decision") and `AGENTS.md` naming it "the single source of locked
  decisions." Recorded here for audit trail — this is a non-standard basis for the LOCKED
  flag compared to a typical `Status: Accepted` ADR, and all 16 sub-decisions (L01–L16)
  inherit it uniformly.

[INFO] Historical review findings superseded by live specs and remediation record
  Note: `docs/review-2026-09-21.md` documents eight findings (F1–F8) against the initial
  commit — an unguarded Newton `centre_distance` solver returning wrong (sometimes
  negative) numbers, entry-count-bounded caches with unbounded RSS growth, absolute-mm
  bore/recess defaults infeasible on 17% of the standard grid, no admission control,
  6-of-56 pinned dependencies, a `root_thickness` measured at the wrong radius, ~440 MB of
  unused image weight, and assorted structure/test/CI gaps. `docs/plan-2026-09-21.md`
  records all seven remediation steps landed and measured (each F-number improved,
  including F1's 138→0 wrong values and F5's 6/56→31/31 pinned packages), and the live
  SPECs synthesized here (`docs/architecture/gear-maths/*`, `docs/architecture/solid-model/*`,
  `docs/architecture/http-api.md`, `docs/architecture/packaging.md`) together with ADR
  entries L03, L04, L07, L08 and L12 describe the fixed behavior already in the tree. The
  review is preserved verbatim in `context.md` as a historical record; none of its F1–F8
  findings were extracted into `requirements.md` or `constraints.md` as live, open items.

[INFO] Tech-debt cross-references preserved as provenance only, not synthesized
  Note: Several ingested SPECs cross-reference `docs/tech_debt/active/` items —
  no-structured-logging (cited by http-api.md, both errors_and_logging.md files, and
  CODING_VALUES.md), no-authentication (http-api.md), cadquery-shape-typing and
  cad-builds-block-the-event-loop (solid-model/implementation.md), no-server-side-cancellation
  (web-ui.md), no-coverage-floor (gear-maths/tests.md). Per orchestrator instruction,
  `docs/tech_debt/active/` (8 items) was deliberately excluded from this ingest — it is
  already summarized in `.planning/codebase/CONCERNS.md` and tracked under its own
  lifecycle. These cross-references are recorded inline in `constraints.md` and
  `context.md` where the citing SPEC mentions them, but no tech-debt item was pulled in as
  a requirement or constraint in its own right.

[INFO] Requirements taxonomy placeholder, not a requirements source
  Note: `docs/requirements/README.md` describes an intended structure (`functional.md`,
  `nfr.md`, `errors.md`, `security.md`) — none of those four files exist; the directory
  holds only the placeholder README, which states explicitly "Nothing is written here yet,
  and nothing should be invented to fill it." `requirements.md` in this synthesis was
  instead derived directly from the root `README.md` and the 15 SPEC documents, per
  orchestrator instruction, since no PRD exists in this ingest set. The taxonomy itself is
  preserved in `context.md` as a pointer for whoever authors `REQUIREMENTS.md` downstream.

[INFO] No PRD in ingest set — requirements.md derived from README + SPECs, not PRDs
  Note: 0 of 22 ingested docs classified PRD. `requirements.md` was populated by reading
  functional/product statements out of the root `README.md` (feature list, parameter
  table, matching-gear workflow, error/warning behavior) and the 15 SPEC documents, rather
  than from acceptance criteria in a product requirements document, because none exists.
  Acceptance fields in `requirements.md` are marked absent wherever no test or explicit
  criterion was cited in the source SPECs — no acceptance criteria were fabricated to fill
  a gap.
