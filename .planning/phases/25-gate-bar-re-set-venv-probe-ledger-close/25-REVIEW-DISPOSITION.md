---
phase: 25
review: 25-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "No test covers the shipped `-c requirements.txt` or the new stamp prerequisite"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "L43 and RESULTS word the adoption proof and the build-constraint caveat as observed when they are inferred"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "The 300 s bar is stated without the same-host gate readings that exceed it"
  - id: IN-01
    severity: info
    disposition: fixed
    title: "Two Makefile comments still describe the stamp as depending on `pyproject.toml` only"
  - id: IN-02
    severity: info
    disposition: fixed
    title: "Over-long comment line in `Makefile`"
  - id: IN-03
    severity: info
    disposition: fixed
    title: "README says Apple silicon is \"not measured on\", then says the numbers were read on Apple silicon"
  - id: IN-04
    severity: info
    disposition: fixed
    title: "`reverify-phase` hard-codes a Claude-specific tool path in a tool-neutral directory"
  - id: IN-05
    severity: info
    disposition: fixed
    title: "Debt item carries a commit subject where convention asks for a sha; L34 has no forward pointer to L43"
open: 0
total: 8
recorded: 2026-10-14T15:24:06.542Z
---

# Phase 25: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | 25-REVIEW-FIX.md |
| WR-02 | warning | fixed | 25-REVIEW-FIX.md |
| WR-03 | warning | fixed | 25-REVIEW-FIX.md |
| IN-01 | info | fixed | 25-REVIEW-FIX.md |
| IN-02 | info | fixed | 25-REVIEW-FIX.md |
| IN-03 | info | fixed | 25-REVIEW-FIX.md |
| IN-04 | info | fixed | 25-REVIEW-FIX.md |
| IN-05 | info | fixed | 25-REVIEW-FIX.md |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
