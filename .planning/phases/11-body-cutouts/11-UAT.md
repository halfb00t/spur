---
status: testing
phase: 11-body-cutouts
source: [11-VERIFICATION.md]
started: 2026-09-29T11:49:44Z
updated: 2026-09-29T11:49:44Z
---

## Current Test

number: 1
name: Confirm the spoke-arm MIN_WALL rule (0 < spoke_width < MIN_WALL refused with a 422) matches what the human actually wanted at the 11-01 checkpoint.
expected: |
  11-01-SUMMARY.md's transcription of the human's 'approved' answer (keep the rule) matches the human's intent; test_a_spoke_rule_refuses_one_step_past_its_wall_and_accepts_it_exactly and the arm sentence in calc.check() implement it.
awaiting: user response

## Tests

### 1. Confirm the spoke-arm MIN_WALL rule (0 < spoke_width < MIN_WALL refused with a 422) matches what the human actually wanted at the 11-01 checkpoint.
expected: 11-01-SUMMARY.md's transcription of the human's 'approved' answer (keep the rule) matches the human's intent; test_a_spoke_rule_refuses_one_step_past_its_wall_and_accepts_it_exactly and the arm sentence in calc.check() implement it.
why_human: A policy decision transcribed from the human's own words at a checkpoint, not a property automation can verify — this project's own 11-VALIDATION.md lists it as manual-only.
result: [pending]

### 2. Confirm HEX_CELL_CAP = 120 and the star cut spelling are acceptable as measured, given (a) both readings were taken under a loaded host (8-9 and 5-10 on a 12-core machine, well above the project's 1.5 'quiet' bar) and (b) 11-REVIEW.md's WR-01 (open, unfixed) found that bench/honeycomb_spike.py's slower()/verdict logic can silently discard a failed build trial in favour of a successful one and never checks the confirmation or spelling rows for validity — a methodology gap in the exact script whose output produced HEX_CELL_CAP.
expected: Either accept 120 as-is (11-06's independent sweep at the cap re-confirms every honeycomb row builds, heaviest 8.65 s, inside the 30 s absolute budget) or require a re-run of the spike with WR-01's fix before trusting the cap further.
why_human: The number is read off one load-affected run on shared hardware, and a known, still-open methodology gap in the measuring script itself is a judgment call about acceptable evidence quality, not something a test can settle (L08).
result: [pending]

### 3. Confirm the honeycomb's 8.65 s cap-row reading is acceptable against D-11's own 7.5 s quarter-share budget (a 1.15x overrun), accepted at 11-06's checkpoint as 'comparable to 11-02's own 7.25 s reading under similar load.'
expected: The human's already-recorded acceptance (11-06-SUMMARY.md key-decisions) stands, or a quieter-host re-measurement is requested.
why_human: Same load-affected-measurement judgment as above; already decided once at an interactive checkpoint (11-06, autonomous: false) but worth a final confirmation since it is the honeycomb's only reading over its own D-11 budget line.
result: [pending]

### 4. Confirm the 33.39 s arithmetic total (heaviest spoke_count le-40 row, 18.52 s, plus Phase 10's 14.87 s tip-chamfer row, both single-feature readings, not a composed build) is acceptable to defer to Phase 12's real composed sweep rather than lowering spoke_count's le further now.
expected: docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md's must-severity filing with Phase 12 as its named trigger is the right call, or the le should be lowered again before Phase 12.
why_human: Whether one loaded-host arithmetic reading (load 32.17, the heaviest anywhere in this project's bench history) warrants revisiting the le now versus waiting for Phase 12's real measurement is a project-priority call, not a test (11-06-SUMMARY.md's own rationale).
result: [pending]

### 5. Triage the five still-open code-review findings from 11-REVIEW.md (WR-01 through WR-05, IN-01; 11-REVIEW-DISPOSITION.md shows all six at disposition 'open', none fixed/skipped/deferred). Two were independently reproduced during this verification: WR-02 (docs/architecture/decision_log.md:1218-1221's L30 entry still says 'the boundary itself builds, one step past it does not', the opposite of what test_the_kernel_cuts_one_valid_solid_past_each_cutout_rule proves and ships) and WR-04 (README.md:151-152 still claims the reverse half-set case — a cutout dimension set with its count at 0 — is 'rejected'; confirmed live that it instead builds nothing and warns: `spur info --hole-d 4 --hole-circle-d 20` returns warnings=['No lightening holes with hole_count 0: ...'], not a 422).
expected: Each finding gets a disposition (fixed/skipped/deferred) rather than sitting at 'open' indefinitely; WR-02 and WR-04 are confirmed real doc/prose inaccuracies (not code defects) and are inexpensive one-sentence fixes.
why_human: Severity/priority triage of a code-review finding is a project decision, and code review disposition is explicitly a human-owned gate (11-REVIEW-DISPOSITION.md), not something the verifier can resolve unilaterally.
result: [pending]

## Summary

total: 5
passed: 0
issues: 0
pending: 5
skipped: 0
blocked: 0

## Gaps
