# Roadmap: spur

## Milestones

- ✅ **v0.1 Hardening** — Phases 1–6 (shipped 2026-09-25) — full detail in
  `milestones/v0.1-ROADMAP.md`, audit in `milestones/v0.1-MILESTONE-AUDIT.md`
- ⏳ **Next milestone** — not yet defined. Run `/gsd-new-milestone`; the candidates
  (helical/internal/rack/bevel gears, tooth chamfers, keyway/hex bores, spoke/hex cutouts,
  the trochoidal root fillet, a browser-driven viewer test) are gathered, not scoped, under
  "Future Requirements" in `milestones/v0.1-REQUIREMENTS.md`.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)
- Numbering continues across milestones — the next milestone starts at Phase 7.

<details>
<summary>✅ v0.1 Hardening (Phases 1–6) — SHIPPED 2026-09-25</summary>

- [x] Phase 1: v0 Baseline (Shipped) (no plans — built and verified directly against `make verify` before GSD)
- [x] Phase 2: CAD Off the Event Loop (5/5 plans) — completed 2026-09-24
- [x] Phase 3: Structured Logging at the Composition Boundary (3/3 plans) — completed 2026-09-24
- [x] Phase 4: Typed Derived-Dimensions Contract (3/3 plans) — completed 2026-09-24
- [x] Phase 5: CI Observed Green (6/6 plans) — completed 2026-09-25
- [x] Phase 6: Address tech debt: merge gate + solid cache (4/4 plans) — completed 2026-09-25 (added 2026-09-25 after the Phase 5 review and the first milestone audit)

Goals, success criteria and plan lists: `milestones/v0.1-ROADMAP.md`. Phase artifacts:
`milestones/v0.1-phases/`. Quick tasks: `milestones/v0.1-quick/`.

</details>

## Forward Scope

v0.1 was hardening only — no new gear geometry shipped. The six items still in
`docs/tech_debt/active/` (one `must`: the waived ten-concurrent latency bar, L18; five
`nice`: coverage floor, CadQuery `Shape` typing, server-side cancellation, no
authentication, Enji Guard/CVE alerting) keep their own lifecycle and triggers; they are
not roadmap phases unless a trigger fires.

## Progress

| Milestone | Phases | Plans | Status | Shipped |
|-----------|--------|-------|--------|---------|
| v0.1 Hardening | 1–6 | 21 | Complete | 2026-09-25 |
