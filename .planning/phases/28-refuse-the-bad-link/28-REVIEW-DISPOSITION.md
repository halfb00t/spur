---
phase: 28
review: 28-REVIEW.md
titles: json
findings:
  - id: WR-02
    severity: warning
    disposition: deferred
    title: "A token the box blanks but the API accepts builds a non-default part under a blank box"
  - id: IN-03
    severity: info
    disposition: fixed
    title: "The old `input.value = to;` pin is now a substring of the new one and can never fail on its own"
  - id: IN-04
    severity: info
    disposition: fixed
    title: "L45's \"only a request under 0.0005 mm prints differently\" and the field description both miss the capped-to-zero case"
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "A selector pick that writes a rejected field leaves the page sending the old token"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "A printed value the project's own rule forbids is filed `must` with no trigger other than a decision"
  - id: IN-01
    severity: info
    disposition: fixed
    title: "`readHash()` assigns the mate box twice only to keep an old test pin adjacent"
  - id: IN-02
    severity: info
    disposition: fixed
    title: "`web-ui.md` has a 190-character line inserted mid-paragraph"
open: 0
total: 7
recorded: 2026-10-22T01:12:18.210Z
---

# Phase 28: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-02 | warning | deferred | docs/tech_debt/active/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md (D-20) |
| IN-03 | info | fixed | 28-REVIEW-FIX.md |
| IN-04 | info | fixed | 28-REVIEW-FIX.md |
| WR-01 | warning | fixed | 3224ec7 fix(28): a selector pick that writes a field ends its rejected link token (28-REVIEW WR-01) (gsd/phase-28-refuse-the-bad-link) (not in the current review) |
| WR-03 | warning | fixed | 6497c28 fix(28): print no tip chamfer when none is cut -- log L45 (gsd/phase-28-refuse-the-bad-link); L45; G-28-2; docs/tech_debt/resolved/2026-10-21-tip-chamfer-effective-gate-reads-the-request.md (not in the current review) |
| IN-01 | info | fixed | aede0fd refactor(28): assign the mate box once in readHash, its pin tightened through the read-back (28-REVIEW IN-01) (gsd/phase-28-refuse-the-bad-link) (not in the current review) |
| IN-02 | info | fixed | 2368718 docs(28): re-wrap web-ui.md's Shape paragraph (28-REVIEW IN-02) (gsd/phase-28-refuse-the-bad-link) (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
