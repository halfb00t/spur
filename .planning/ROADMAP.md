# Roadmap: spur

## Milestones

- ✅ **v0.1 Hardening** — Phases 1–6 (shipped 2026-09-25) — full detail in
  `milestones/v0.1-ROADMAP.md`, audit in `milestones/v0.1-MILESTONE-AUDIT.md`
- ✅ **v0.2 Fit to Shaft** — Phases 7–12 (shipped 2026-10-01) — full detail in
  `milestones/v0.2-ROADMAP.md`, audit in `milestones/v0.2-MILESTONE-AUDIT.md`
- ✅ **v0.3 Clean Ledger** — Phases 13–16 (shipped 2026-10-05) — full detail in
  `milestones/v0.3-ROADMAP.md`, audit in `milestones/v0.3-MILESTONE-AUDIT.md`
- ⏳ **v0.4** — not yet defined; `/gsd-new-milestone`. Candidates carried since the v0.1
  kickoff: the gear family (helical first) or precision (the trochoidal root fillet) —
  `milestones/v0.3-REQUIREMENTS.md` "Future Requirements".

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)
- Numbering continues across milestones — the next milestone starts at Phase 17.

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

<details>
<summary>✅ v0.2 Fit to Shaft (Phases 7–12) — SHIPPED 2026-10-01</summary>

**Milestone Goal:** A generated gear mounts on a real shaft and prints light — new bore
profiles, body cutouts and a tooth-tip chamfer, all additive on the shipped spur pipeline,
with tooth measurements untouched.

- [x] Phase 7: Foundation — Generalized Edge Selection + Regression Fixture (2/2 plans) — completed 2026-09-26
- [x] Phase 8: Hex Bore (4/4 plans) — completed 2026-09-26
- [x] Phase 9: Keyway Bore (5/5 plans) — completed 2026-09-27
- [x] Phase 10: Tooth-Tip Chamfer (5/5 plans) — completed 2026-09-28
- [x] Phase 11: Body Cutouts (9/9 plans) — completed 2026-09-29
- [x] Phase 12: Composition Pass (9/9 plans) — completed 2026-09-30 (re-verified 2026-10-01 after the review fixes)

Goals, success criteria and plan lists: `milestones/v0.2-ROADMAP.md`. Phase artifacts:
`milestones/v0.2-phases/`. Decisions: L26–L31 in `docs/architecture/decision_log.md`.
Landed as PRs #7–#13 through `make pr.land`; the close is its own PR.

</details>

<details>
<summary>✅ v0.3 Clean Ledger (Phases 13–16) — SHIPPED 2026-10-05</summary>

**Milestone Goal:** Every `must` debt item retired by measurement or a logged decision,
every false claim in the record made true or warned, and the gate itself measured — no new
user-facing geometry, no new `GearParams` field, the 44-record pre-v0.2 fixture
byte-unchanged throughout.

- [x] Phase 13: Latency Bar (7/7 plans; 13-05 not executed by design — outcome (a)) — completed 2026-10-02
- [x] Phase 14: Honest Record (4/4 plans; 14-04 a gap-closure plan after UAT) — completed 2026-10-03
- [x] Phase 15: The Gate, Measured and Pinned (6/6 plans) — completed 2026-10-04
- [x] Phase 16: Typing & Validation Debt (3/3 plans) — completed 2026-10-05

Goals, success criteria and plan lists: `milestones/v0.3-ROADMAP.md`. Phase artifacts:
`milestones/v0.3-phases/`. Decisions: L32–L35 in `docs/architecture/decision_log.md`.
Landed as PRs #16–#19 through `make pr.land` after the start PR #15; the close is its own
PR. Outcome against PROJECT.md's three success metrics: 2 and 3 met; 1 ("zero `must` rows")
not met as written — the four `must` rows the milestone was scoped on are retired, and the
one `must` Phase 13 itself filed (the same-slot timeout race, D-17) stays active with its
trigger (`milestones/v0.3-MILESTONE-AUDIT.md`).

</details>

## Process Notes (carried forward)

- Phases run on `gsd/phase-NN-*` branches cut from `origin/main` and land only through
  `make pr.land PR=N` (L22/L25); `.planning/` rides the same PR as the code, never a
  separate planning-only commit. The milestone close is itself a PR.
- `make verify` (ruff, mypy `--strict`, import-linter, unfinished-work scan, pytest on 8
  xdist workers under `fail_under = 96`) is the gate for every phase, no exceptions (L13,
  L34). It runs as the pre-commit hook (~64 s warm at 929 tests); `gsd_run query commit`'s
  30 s timeout cannot survive it — commit with plain `git commit` and let the hook finish.
- Every phase that adds a decision logs it as a new `Lxx` in
  `docs/architecture/decision_log.md`, append-only.
- New parameters default to off (L05); the pre-v0.2 regression fixture is the standing
  proof, re-run by every later phase.

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|-----------------|--------|-----------|
| 1–6 | v0.1 | 21/21 | Complete | 2026-09-25 |
| 7–12 | v0.2 | 34/34 | Complete | 2026-10-01 |
| 13–16 | v0.3 | 20/20 | Complete | 2026-10-05 |
