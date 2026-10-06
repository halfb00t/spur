---
phase: 15
review: 15-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "The one CI datapoint is recorded without the baseline that shows `-n 4` bought nothing on the runner"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "Two retirements left a false statement and two dangling links"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "The commit-timeout debt now contradicts its own recovery argument and trigger"
  - id: WR-04
    severity: warning
    disposition: fixed
    title: "\"None of the five `-n 8 --cov` runs\" undercounts the record it cites"
  - id: IN-01
    severity: info
    disposition: fixed
    title: "`requirements.txt` and `packaging.md` do not say the closure is now also CI's constraint file"
  - id: IN-02
    severity: info
    disposition: fixed
    title: "`PYTEST_WORKERS` clamp trusts `getconf` blindly"
  - id: IN-03
    severity: info
    disposition: fixed
    title: "L34 names two different \"Before\" numbers"
  - id: IN-04
    severity: info
    disposition: fixed
    title: "`make clean` leaves coverage data, and two concurrent gates in one tree share it"
open: 0
total: 8
recorded: 2026-10-06T00:00:00Z  # triage by hand; the gate's own stamp was 2026-10-04T06:43:27.364Z
---

# Phase 15: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | 47a118d RESULTS.md CI run beside its baseline; dated amendment to L34 (fix/review-findings-v0.3) |
| WR-02 | warning | fixed | 47a118d (fix/review-findings-v0.3) |
| WR-03 | warning | fixed | 38d6390 docs(tech_debt): warm or cold, raised to must (fix/review-findings-v0.3) |
| WR-04 | warning | fixed | 47a118d (fix/review-findings-v0.3) |
| IN-01 | info | fixed | 47a118d (fix/review-findings-v0.3) |
| IN-02 | info | fixed | build(make) commit on fix/review-findings-v0.3 |
| IN-03 | info | fixed | 47a118d dated amendment to L34 (fix/review-findings-v0.3) |
| IN-04 | info | fixed | build(make) commit on fix/review-findings-v0.3: clean removes .coverage*; concurrent gates in one tree stay unsupported (R1) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
