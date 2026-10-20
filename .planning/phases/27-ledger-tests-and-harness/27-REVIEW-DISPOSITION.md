---
phase: 27
review: 27-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "`_problems` environ allowance walks a compound statement's whole body, so the new \"own statement\" rule is bypassable"
  - id: WR-02
    severity: warning
    disposition: open
    title: "Moving the teardown to `tests/process_group.py` took it out of the pin's scan set"
  - id: WR-03
    severity: warning
    disposition: open
    title: "`stop_group` still lets a failure in the reader skip SIGKILL and the reap"
  - id: IN-01
    severity: info
    disposition: open
    title: "`_sleeper` sends `killpg` to a pid its own test already reaped"
  - id: IN-02
    severity: info
    disposition: open
    title: "`_instrument` records `poll` events that `stop_group` never produces, and test 1 asserts only `events[0]`"
  - id: IN-03
    severity: info
    disposition: open
    title: "`_page_string` in `test_selector.py` is a second copy of `_js_number`, and the copy's new guard and `-0` rule are untested"
  - id: IN-04
    severity: info
    disposition: open
    title: "Nothing pins that `_build` passes its own `rm` to `_chamfer_tips`"
  - id: IN-05
    severity: info
    disposition: open
    title: "`test_the_host_state_reads_unknown_where_git_cannot_name_head` patches the process-wide `subprocess.run`"
  - id: IN-06
    severity: info
    disposition: open
    title: "The `Resolved in:` fields of the five resolved debt items hold commit subjects, not shas"
open: 9
total: 9
recorded: 2026-10-20T14:26:56.245Z
---

# Phase 27: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |
| IN-06 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
