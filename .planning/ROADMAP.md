# Roadmap: spur

## Milestones

- ✅ **v0.1 Hardening** — Phases 1–6 (shipped 2026-09-25) — full detail in
  `milestones/v0.1-ROADMAP.md`, audit in `milestones/v0.1-MILESTONE-AUDIT.md`
- ✅ **v0.2 Fit to Shaft** — Phases 7–12 (shipped 2026-10-01) — full detail in
  `milestones/v0.2-ROADMAP.md`, audit in `milestones/v0.2-MILESTONE-AUDIT.md`
- ✅ **v0.3 Clean Ledger** — Phases 13–16 (shipped 2026-10-05) — full detail in
  `milestones/v0.3-ROADMAP.md`, audit in `milestones/v0.3-MILESTONE-AUDIT.md`
- ✅ **v0.4 True Root** — Phases 17–20 (shipped 2026-10-09; Phase 20 skipped under L38) — full
  detail in `milestones/v0.4-ROADMAP.md`, audit in `milestones/v0.4-MILESTONE-AUDIT.md`

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)
- Numbering continues across milestones — the next milestone starts at Phase 21 (Phase 20
  keeps its number although it was skipped).

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

<details>
<summary>✅ v0.4 True Root (Phases 17–20) — SHIPPED 2026-10-09</summary>

**Milestone Goal:** Retire the last two `must` items — the same-slot timeout race by a
measured reproduction and a narrow fix, the commit-timeout gap by a logged decision — then
replace the radial root below the base circle with the trochoid a hob cuts, proven against
an independent oracle, with the fixture rule (L26) honoured under its own `Lxx`, never
bypassed.

- [x] Phase 17: Debt First — Commit Gate and Pool Race (5/5 plans) — completed 2026-10-06
- [x] Phase 18: Trochoid Maths, Proved (6/6 plans; 18-06 a gap-closure plan after UAT) — completed 2026-10-08
- [x] Phase 19: The Trochoid in the Part (11/11 plans; review CR-01/WR-01 fixed before verification) — completed 2026-10-09
- [x] Phase 20: The Flip (conditional) — skipped under L38 (O4, flip deferred to D-09's trigger: a real fit report or a mating-pair request below z_min); criteria not applicable; the flip owned by `milestones/v0.4-REQUIREMENTS.md` "Trochoid follow-ups"

Goals, success criteria and plan lists: `milestones/v0.4-ROADMAP.md`. Phase artifacts:
`milestones/v0.4-phases/`. Decisions: L36–L38 in `docs/architecture/decision_log.md`.
Landed as PRs #27–#29 through `make pr.land` after the start PR #26; the close is its own
PR. Outcome against the milestone goal's three clauses: all met (the two scoped `must` rows
retired; the hob root in the part proven against the swept-cutter oracle; the fixture
byte-identical to `v0.3`); one `must` the milestone itself filed (the resource-tracker flake,
17-04) stays active with its trigger, and L34's 66 s gate bar sits against a gate that reads
~193 s after the kernel-tier proofs — accepted (`accept-A`), its re-set an open decision
(`milestones/v0.4-MILESTONE-AUDIT.md`, status `tech_debt`).

</details>

## Process Notes (carried forward)

- Phases run on `gsd/phase-NN-*` branches cut from `origin/main` and land only through
  `make pr.land PR=N` (L22/L25); `.planning/` rides the same PR as the code, never a
  separate planning-only commit. The milestone close is itself a PR.
- `make verify` (ruff, mypy `--strict`, import-linter, unfinished-work scan, pytest on 8
  xdist workers under `fail_under = 96`) is the gate for every phase, no exceptions (L13,
  L34). Since Phase 17 (L36) it runs as the pre-push hook; the pre-commit hook runs
  `make verify.fast` (~11 s warm, under `gsd_run query commit`'s 30 s timeout — proved by SDK
  commit `5a3332f`). Since Phase 19 the whole gate reads 162–240 s on the 18-CPU M5 Max
  (192.94 s mean, 19-09) against L34's 66 s bar, a cost the human accepted (`accept-A`, L38);
  the bar's re-set is an open decision. A killed SDK commit still leaves the hook running as
  an orphan: wait for it, then one plain `git commit`, never a blind retry (D-07).
- Every phase that adds a decision logs it as a new `Lxx` in
  `docs/architecture/decision_log.md`, append-only.
- New parameters default to off (L05); the pre-v0.2 regression fixture is the standing
  proof, re-run by every later phase. It changes only through `make fixture.regen`, in its
  own commit, under its own `Lxx` that says what moved and why (L26 D-03) — a feature commit
  never touches it. The hob-root default flip, if it ever comes, is that one commit (L38).
- A debt item is retired only in the commit that fixes it: `Status: resolved`, the sha,
  `git mv` into `resolved/`, the INDEX row moved (CLAUDE.md).

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1–6 | v0.1 | 21/21 | Complete | 2026-09-25 |
| 7–12 | v0.2 | 34/34 | Complete | 2026-10-01 |
| 13–16 | v0.3 | 20/20 | Complete | 2026-10-05 |
| 17–20 | v0.4 | 22/22 (Phase 20 skipped under L38) | Complete | 2026-10-09 |
