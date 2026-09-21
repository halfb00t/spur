# Roadmap: spur

## Overview

`spur` already ships. This roadmap records one completed baseline milestone — v0, the
working parametric involute spur gear generator currently in the tree, with all 11
ingested requirements satisfied and `make verify` passing. It then stops: **forward scope
is undefined**, and no forward phases are invented here. See "Forward Scope" below for the
two candidate pools the human may draw the next milestone from, and `PROJECT.md`
("Success Metric") for the one field this roadmap explicitly cannot set.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: v0 Baseline (Shipped)** - The generator, its three interfaces, and its
  error/measurement/export contract, as already built and verified.

## Phase Details

### Phase 1: v0 Baseline (Shipped)
**Goal**: Users can generate a correct, print/CNC-ready involute spur gear — with numbers
they can trust — from a web UI, an HTTP API, or a CLI, all driven by one parameter model.
**Depends on**: Nothing (first phase)
**Requirements**: REQ-involute-geometry, REQ-bore-and-fillets, REQ-face-recesses,
REQ-measurement-aids, REQ-three-interfaces, REQ-cli-parity, REQ-shareable-links,
REQ-stl-step-export, REQ-error-contract, REQ-no-auth-default, REQ-docker-multiarch
**Success Criteria** (what is observably TRUE today):
  1. The same gear and the same derived numbers are reachable from the web UI, the HTTP
     API, and the CLI, all built from one `GearParams` model; the CLI's numbers, warnings,
     and exit codes match the API's. *(REQ-three-interfaces, REQ-cli-parity)*
  2. Every gear configuration lives in the URL, so it can be shared and reopened as a
     link. *(REQ-shareable-links)*
  3. The generated solid reflects involute tooth geometry (module, teeth, pressure angle,
     profile shift), backlash, root fillets, a D-flat or round bore with clearance and
     chamfer, and optional filleted-floor face recesses on one or both sides.
     *(REQ-involute-geometry, REQ-bore-and-fillets, REQ-face-recesses)*
  4. Users can download the generated gear as STL (for slicing) or STEP (for CAD) from
     any of the three interfaces. *(REQ-stl-step-export)*
  5. Users get caliper, span (Wildhaber), and centre-distance measurements for matching an
     existing physical gear, with a warning — never a fabricated number — when no working
     centre distance exists. *(REQ-measurement-aids)*
  6. A direct conflict between two explicit parameters is refused (422 / exit 2) naming the
     offending fields; a trimmable dimension is capped and the trim is reported in
     `warnings`; the service deploys via Docker/compose on `linux/amd64` and `linux/arm64`,
     bound to `127.0.0.1` with no built-in authentication by default.
     *(REQ-error-contract, REQ-no-auth-default, REQ-docker-multiarch)*
**Plans**: N/A — this baseline predates GSD planning and was built and verified directly
against `make verify`; there is no PLAN.md history to point to.

## Forward Scope — UNDEFINED

**No forward phases are defined past Phase 1, and none should be invented.** Nothing in
the ingested README, SPECs, or decision log (`docs/architecture/decision_log.md`) states
what ships next; `PROJECT.md`'s "Active" requirements section is empty for the same
reason. This is the correct, honest state of this roadmap right now — not a gap for a
future run of this workflow to quietly fill.

To start the next milestone, the human runs `/gsd-new-milestone` (or equivalent) and
picks requirements — optionally, but not necessarily, from these two pools. Neither pool
is a phase; both are candidates only:

**Ideas pool** — `docs/ideas/` (2 items):
- Trochoidal (vs. radial) root fillet below the base circle — see PROJECT.md, L10.
- A browser-driven test for the 3D viewer.

**Tech debt pool** — `docs/tech_debt/active/` (8 items; excluded from this ingest by user
decision, tracked under its own lifecycle per `CLAUDE.md`):
- `must` (3): CAD builds block the event loop; no structured logging; untyped
  `/api/info` contract.
- `nice` (5): CadQuery `Shape` typing bypasses mypy; no coverage floor in the gate; no
  server-side cancellation on client abort; authentication intentionally absent; Enji
  Guard / CVE alerting not connected.

Full detail on each item: `.planning/codebase/CONCERNS.md`.

## Progress

**Execution Order:**
Phase 1 only. No further phases exist until the human defines the next milestone.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. v0 Baseline (Shipped) | N/A | Complete | Shipped (pre-dates this roadmap) |
