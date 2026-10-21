---
phase: 23
review: 23-REVIEW.md
titles: json
findings:
  - id: IN-08
    severity: info
    disposition: fixed
    title: "The driver check cannot tell `hex_cell eq 0.05` from `hex_cell gt 0`; only the forward check's incidental `ValidationError` catches it"
  - id: IN-11
    severity: info
    disposition: fixed
    title: "`_js_number` returns a string JavaScript would not write for -0.0 and outside 1e-6 <= |x| < 1e21, and nothing guards the range"
  - id: IN-01
    severity: info
    disposition: fixed
    title: "The reason text is formatted differently in the two \"independent\" evaluators for non-trivial values"
  - id: IN-02
    severity: info
    disposition: fixed
    title: "A dimmed field's accessible name now contains its own reason, which `aria-describedby` repeats"
  - id: IN-03
    severity: info
    disposition: fixed
    title: "A stale line reference in the new tech-debt item"
  - id: IN-04
    severity: info
    disposition: fixed
    title: "A verdict that \"08 D-09 stands\" remains in the ideas index after L41 superseded it"
  - id: IN-05
    severity: info
    disposition: fixed
    title: "The L41 text is in two tenses about what the commit declares"
  - id: IN-06
    severity: info
    disposition: fixed
    title: "The browser oracle resolves a repeated parameter last-wins where the page resolves it first-wins (external: codex)"
  - id: IN-07
    severity: info
    disposition: fixed
    title: "The refused-pair step does not require both keyway fields to be marked invalid (external: codex)"
  - id: IN-09
    severity: info
    disposition: fixed
    title: "L41 and the threat model still describe an unknown op as an uncaught throw"
  - id: IN-10
    severity: info
    disposition: fixed
    title: "The last assertion of the `unknown relation op` step does not check what its comment claims"
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "An unknown `enabled_when` op freezes the UI silently and leaves a stale part, dimensions and download links on screen"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "The \"never disables, hides or clears a field\" guard is narrower than the contract it claims, and has a false-positive hole"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "The calc parity proof cannot tell a right driver from a wrong one for the seven cutout dependents (external: codex)"
open: 0
total: 14
recorded: 2026-10-21T00:00:00Z  # triage by hand; the gate's own stamp was 2026-10-12T03:11:19.882Z
---

# Phase 23: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| IN-08 | info | fixed | c30ebd0 test(27): walk the OpenAPI document for selectors, share the bore-off block, probe the honeycomb gate twice (`honeycomb (4)` joins `CUTOUT_STATES` and the meta-test probes the gate twice; Phase 27 branch, squashed into 1434a47) |
| IN-11 | info | fixed | 4d43b64 test(27): check _js_number's range and -0, refuse a non-scalar fixture param, re-wrap a docstring (`_js_number` asserts the range JavaScript writes positionally and writes `-0` as `0`; Phase 27 branch, squashed into 1434a47) |
| IN-01 | info | fixed | 23-REVIEW-FIX.md (not in the current review) |
| IN-02 | info | fixed | 23-REVIEW-FIX.md (not in the current review) |
| IN-03 | info | fixed | 23-REVIEW-FIX.md (not in the current review) |
| IN-04 | info | fixed | 23-REVIEW-FIX.md (not in the current review) |
| IN-05 | info | fixed | 23-REVIEW-FIX.md (not in the current review) |
| IN-06 | info | fixed | 23-REVIEW-FIX.md (not in the current review) |
| IN-07 | info | fixed | 23-REVIEW-FIX.md (not in the current review) |
| IN-09 | info | fixed | 23-REVIEW-FIX.md (not in the current review) |
| IN-10 | info | fixed | 23-REVIEW-FIX.md (not in the current review) |
| WR-01 | warning | fixed | 23-REVIEW-FIX.md (not in the current review) |
| WR-02 | warning | fixed | 23-REVIEW-FIX.md (not in the current review) |
| WR-03 | warning | fixed | 23-REVIEW-FIX.md (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
