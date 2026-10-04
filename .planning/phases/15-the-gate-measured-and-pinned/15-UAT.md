---
status: testing
phase: 15-the-gate-measured-and-pinned
source: [15-VERIFICATION.md]
started: 2026-10-04T12:20:00Z
updated: 2026-10-04T12:20:00Z
---

## Current Test

number: 1
name: Accept or refuse the one non-inferable (`verification: backstop`) truth from 15-02 — the combined coverage total does not depend on the order in which the per-process data files are written or combined
expected: |
  Either accept the recorded observation as sufficient (three `-n 8 --cov` totals identical at
  97.21 % with 23 missed statements each, a fourth identical pair in 15-04's B1/B2, and CI's
  `-n 4` run at 97.29 %), or ask for a held-out/property test. Note the one observed
  divergence: serial C0 and 15-04's A1/A2 read 96.99 % because worker lines 63-67 and 222 of
  `pool.py` were lost (the flush-loss debt,
  `docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md`) -- a
  different cause than combine order, but the order was never varied on purpose.
awaiting: user response

## Tests

### 1. The `backstop` truth: coverage total independent of combine order
expected: Either accept the recorded observation as sufficient (three `-n 8 --cov` totals identical at 97.21 % with 23 missed statements each, a fourth identical pair in 15-04's B1/B2, and CI's `-n 4` run at 97.29 %), or ask for a held-out/property test. The one observed divergence (serial runs at 96.99 %) is the flush-loss debt, not combine order; the order was never varied on purpose. Why human: the plan itself tags this truth `backstop`; equal totals on runs whose file-write order was not controlled do not prove order-independence, so the verifier abstained (insufficient_spec).
result: [pending]

### 2. The 14 flagged prohibitions (9 `verification: test`, 5 `judgment`)
expected: Each negative is true at HEAD 1eab497 — the verifier observed every one by its own commands (the Prohibitions table in 15-VERIFICATION.md carries the command behind each row) — but no standing wired enforcement exists for any of them. Accept the flagged `unverified-prohibition` items as "complete with 14 flagged prohibitions", or name any you want kept by a wired check. Why human: ADR-550 D4/D5d — a test-tier prohibition with no wired enforcement fails closed to flagged-unverified, and a judgment-tier prohibition is never a silent green; the fail-closed default, not an observed violation, holds `passed` back.
result: [pending]

## Summary

total: 2
passed: 0
issues: 0
pending: 2
skipped: 0
blocked: 0

## Gaps
