---
phase: 19-the-trochoid-in-the-part
plan: 10
subsystem: docs
tags: [decision-log, L38, trochoid, hob-root, root_shape, gate-cost, strategy-docs]

requires:
  - phase: 19-the-trochoid-in-the-part
    provides: the numbers, bars, shas and three human decisions of 19-01 to 19-09 (SUMMARYs and bench/RESULTS.md "Trochoid in the part (Phase 19)")
provides:
  - "docs/architecture/decision_log.md ## L38 (supersedes L10, amends L09 and L33): the hob root is opt-in through root_shape, the default does not move in v0.4, Phase 20 is skipped"
  - "the regen rules a future flip must follow and its trigger (D-09), the three reversibility ratings, every measured figure cited to a SUMMARY sha or a RESULTS subsection"
  - "the gear-maths and solid-model strategy docs pointing at L38"
affects: [19-11, 20, next-milestone-planning]

# Actuals (#2632): chars/4 over the added lines of the three docs files, 2e2482f..e19ba45.
actuals:
  tokens: 4850
  tasks: 1
  commits: 1

tech-stack:
  added: []
  patterns:
    - "an append-only decision entry whose every figure carries its source (SUMMARY sha or RESULTS subsection) and whose host difference is stated, not scaled"

key-files:
  created: []
  modified:
    - docs/architecture/decision_log.md
    - docs/architecture/gear-maths/strategy.md
    - docs/architecture/solid-model/strategy.md

key-decisions:
  - "L38 records the three human decisions of the phase with their dates and words: 19-02 take the recommendations (kernel bar, waist floor, field name root_waist, D-02 confirmed, area guard), 19-07 exit-documented (SC5's exit 2 reads as the parameter refusals; a root guard's BuildError exits 1 under D-14), 19-09 accept-A (the gate's measured cost accepted, L34's 66 s bar and the 401-position count untouched)"
  - "L34's 66 s bar is not re-set by L38; the entry says the gate reads about 193 s on the 18-CPU M5 Max against a bar set on a 12-CPU M2 Max and names the re-set as a separate decision"
  - "The strategy docs name L38 as superseding L10 (gear-maths) and amending L09 (solid-model); L10 and L09 stay named, as written in the log"

requirements-completed: [REQ-root-mode-decided, REQ-undercut-warning-restated]  # see Issues Encountered: REQ-trochoid-composes-and-is-priced is also declared by 19-11, left to its last declaring plan

coverage:
  - id: D1
    description: "L38 appended after L37 with no line of L01-L37 changed; it names L09, L10, L33 and L37, root_shape, D-09's trigger, the make fixture.regen rule, the three reversibility ratings, Reason: and Machine:, and cites bench/RESULTS.md Trochoid in the part (Phase 19)"
    requirement: REQ-root-mode-decided
    verification:
      - kind: other
        ref: "the plan's decision-log check (prints 'L38 appended, nothing earlier edited'; git diff against the merge-base df4749e shows 0 removed lines)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The gear-maths and solid-model strategy docs name L38"
    requirement: REQ-root-mode-decided
    verification:
      - kind: other
        ref: "the plan's strategy-docs check (prints 'strategy docs point at L38')"
        status: pass
    human_judgment: false
  - id: D3
    description: "The undercut warning's restatement under the trochoid (supersedes L10) and its unchanged radial wording are recorded with the rounding rules and the captured rows"
    requirement: REQ-undercut-warning-restated
    verification:
      - kind: other
        ref: "docs/architecture/decision_log.md ## L38 'What it supersedes and amends' (figures from 19-06 fe8fed9)"
        status: pass
    human_judgment: true
    rationale: "Whether the entry reads true and complete against the code is a reviewer's judgment; the check proves the named terms are present and nothing earlier moved"
  - id: D4
    description: "The gate: make verify after the edits"
    verification:
      - kind: other
        ref: "make verify (1210 passed in 166.32s, coverage 97.90 %, exit 0)"
        status: pass
    human_judgment: false

duration: "about 12 min (start approximate; the SUMMARY reads at 07:40Z to 07:52Z)"
completed: 2026-10-09
status: complete
plan_head_before: 2e2482f33cee8bb8c03bdb99e36f514754f8da36
plan_head_after: e19ba45a5f4a47bf216875189010f6f2670bfd99
commits: 1
---

# Phase 19 Plan 10: L38, the hob root opt-in and what it cost Summary

**L38 (supersedes L10, amends L09 and L33) is appended to the decision log: `root_shape` makes the hob root opt-in, the default does not move in v0.4, the flip's regen rules and trigger are named, and every bar, floor, timing and gate figure of Phase 19 is cited to its SUMMARY sha or `bench/RESULTS.md` subsection with the 18-CPU versus 12-CPU host difference stated.**

## Performance

- **Duration:** about 12 min (approximate; the first reads were at about 07:40Z and the last commit at 07:51Z), of which the one `make verify` is 2 min 47 s
- **Tasks:** 1
- **Files modified:** 3 (`docs/architecture/decision_log.md` +203, `gear-maths/strategy.md` +5/-2, `solid-model/strategy.md` +7/-3)

## Accomplishments

- **L38 title:** `## L38 — The hob-cut root is opt-in through root_shape, every number beside it is proved or warned, and the default does not move in v0.4 (supersedes L10, amends L09 and L33)`, dated 2026-10-09, in L37's shape: bold-led paragraphs (The choice; What a future flip must do; What it supersedes and amends; The part; The numbers; The interfaces; The price; Reversibility), then `Reason:` and `Machine:`. The append-only check against the merge-base `df4749e` shows 0 removed lines in the decision log.
- **The flip:** one commit carrying the predicate change, `make fixture.regen` output and an `Lxx` listing the moving records first (L26 D-03, 18 D-01); trigger a real fit report or a mating-pair request below `z_min` (D-09), owned by REQUIREMENTS.md "Trochoid follow-ups".
- **Figures cited and where from (none re-estimated):**
  - Chamfer law, 14 rows, law holds, 8 on the law, 6 conservative, worst on-law -3.06e-06 mm: 19-01 `7a0268f`, re-run on the shipped build in 19-09 `4b08aa8` with identical rows.
  - `ROOT_ARC_MIN` 2e-6 mm (10.0x the last failing chord 2.0e-7 mm, 15.8x below the smallest real chord 3.1644e-5 mm), the four guard bars (1e-11 rad at 40.9x, 1000 at 75.0x, `TOL` 1e-6 mm at 8.8e6x, 5e-2 on the arc-midpoint polygon at 13.6x), `KERNEL_BAR_PER_MODULE` 2e-3 (10.9x, tripwire 5.5x over at 1.1039e-2 mm), the 401-position count (41 reads 28 % low): 19-02 `d8abb23` / `bench/RESULTS.md` "Bars adopted (19-02)", written into code by 19-04 `ad8c51a` and 19-05 `4b2b03a` `356682b`.
  - The waist floor 0.4 mm absolute, the walk (1,098 gears, 1,061 built, thinnest 3.2325e-3 mm), 294 of 1,061 and 771 of 10,326 firing, the small-module caveat (595 of 616 at module 0.2 against 176 of 9,710): 19-02 "Waist walk (19-02, D-07)", 19-06 `6032926`.
  - Heaviest corner row: 14.64 s of 30 s trochoid (build 14.28 s plus the 0.36 s fine STL), 9.50 s radial twin, 1.54x, margin 15.36 s, 16.61 s in 19-01's spike, 34 requests inside 30 s; L37's 29.42 s row is 200-tooth, a trochoid request ignored there, so it stands: 19-09 `4b08aa8`, "Composed build time on the real build (19-09)".
  - The gate: 52.89 s mean at the phase base (19-01 `7a0268f`) against 208.52 / 161.71 / 208.60 s, mean 192.94 s, 2.92x L34's 66 s, +140.05 s on the same Apple M5 Max (18 CPUs), with L34's bar set on a 12-CPU M2 Max; `make verify.fast` 11.39 to 11.54 s inside L36's 30 s; `derive()` 10.3 usec default and 30 usec trochoid: 19-09 `f810fb6`, "The gate, priced (19-09)".
- **The human's three decisions are in L38 with dates and words:** `take the recommendations` (19-02, ids mapped by the orchestrator, 2026-10-09), `exit-documented` (19-07, quoted from its SUMMARY, 2026-10-09), `accept-A` (19-09, 2026-10-09, Phase 12 D-10's precedent via L31).
- **Strategy docs:** `gear-maths/strategy.md`'s L10 bullet is now an L38 bullet that names L10 as superseded and still describing the default; `solid-model/strategy.md`'s L09 line gains the trochoid branch under L38 and the key-decisions list adds L38.
- **Gate:** `make verify` exit 0, `1210 passed in 166.32s (0:02:46)`, coverage 97.90 % (floor 96); ruff, mypy `--strict`, import contracts and the unfinished-work scan green; 0 `ReentrantCallError` in the log. The commit hook ran `make verify.fast` (Passed).
- **ISO wording (D-04):** `root_form_d` is called the cutter-envelope junction in L38 and is stated not to be a form diameter in ISO 21771's sense; no sentence in L38 calls it one.

## Task Commits

1. **Task 1: L38 and the two strategy docs** - `e19ba45` (docs)

**Plan metadata:** the docs commit that carries this SUMMARY, then the commit for STATE.md, ROADMAP.md and `.planning/state.json`.

`commits: 1` is measured from the ledger: `git rev-list --count 2e2482f..HEAD` read 1 at SUMMARY write.

## Files Created/Modified

- `docs/architecture/decision_log.md` - `## L38` appended after `## L37`; no earlier line changed
- `docs/architecture/gear-maths/strategy.md` - the L10 bullet becomes an L38 bullet naming L10 as superseded
- `docs/architecture/solid-model/strategy.md` - the L09 design-secret line gains the trochoid branch; the key-decisions list adds L38

## Decisions Made

See `key-decisions`. The entry quotes the human's words where the plan asked for them and leaves L34's 66 s bar alone: re-setting it from an idle-host reading is named as a separate decision, which is the orchestrator's caveat at 19-09 kept in the record.

## Deviations from Plan

None - plan executed exactly as written. Two small items inside the plan's latitude: the plan's "the L10 bullet becomes an L38 bullet" was written so the bullet also says L10 "still describes the default" (L10 is not deleted, only superseded); and the entry lists the 19-03 resource-tracker re-deferral in one sentence under The price because the gate's cost and its flake are read together.

## Issues Encountered

- **Commit attribution line.** The commit ends with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`, the line the session's attribution reminder gives. The dispatch text named `Claude Fable 5.1`; `CLAUDE.md` names neither, so the reminder was followed, as 19-05 to 19-08 did.
- **`gsd_run` was not defined in the executor's shell** for the protected-branch probe (`git.base-branch`); the five-name fallback of the pre-commit assertion was used (branch `gsd/phase-19-the-trochoid-in-the-part`, not protected).
- **Shared requirement ID.** `REQ-trochoid-composes-and-is-priced` is also declared by 19-11, which has no SUMMARY yet; it is left for 19-11 under the #2388 gate.
- **L34's bar against the measured gate.** L38 records the cost and the human's acceptance; the 66 s bar now sits against a gate that reads about 193 s on this host (about 167 s on the quietest reading). Nothing was filed (see below); a debt item or a new `Lxx` that re-sets the bar is the human's call.

## Known Stubs

None. No code was written; no placeholder, skipped test or unrun `<verify>` was left behind, so nothing was appended to `.planning/WINDOWS.md`.

## Threat Flags

None. A record only: no network, auth, file-access or trust-boundary surface. T-19-20 (a claim the code does not back, an ISO form-diameter label, or a re-estimated figure) is mitigated: every figure is cited to a SUMMARY sha or a RESULTS subsection, the decision log diff has no removed line, and the cutter-envelope-junction wording is asserted by the plan's check.

## User Setup Required

None - no external service configuration required.

## Debt and Ideas Filed

None filed. The candidate for the human is above (L34's 66 s bar against a gate near 193 s on this host). The download-name idea is 19-11's.

## Next Phase Readiness

- 19-11 cites `L38` by id only (README, the ideas, ROADMAP's Phase 20 row, REQUIREMENTS); nothing it writes depends on L38's text.
- Phase 20 is recorded skipped by 19-11; L38 names the flip's rules and trigger for whoever picks it up.

## Self-Check: PASSED

- FOUND: `docs/architecture/decision_log.md`, `docs/architecture/gear-maths/strategy.md`, `docs/architecture/solid-model/strategy.md`; `## L38` appears once, after `## L37`.
- FOUND: commit `e19ba45` is an ancestor of HEAD; `git rev-list --count 2e2482f..HEAD` read 1 before this SUMMARY.
- The plan's two automated checks printed `L38 appended, nothing earlier edited` and `strategy docs point at L38`; the merge-base diff of the decision log has 0 removed lines; `make verify` exit 0, `1210 passed`.

---
*Phase: 19-the-trochoid-in-the-part*
*Completed: 2026-10-09*
