---
phase: 21
review: 21-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "`stop_group` can leak the whole server group if `ps` fails"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "`MIN_GROUP_MEMBERS` is documented as \"uvicorn plus 2 workers\"; the 3 members are uvicorn, the resource tracker and ONE worker"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "A missing-shell failure tells the reader `make test` will fix it, but a current `$(BROWSER)` stamp makes `make test` do nothing"
  - id: IN-01
    severity: info
    disposition: fixed
    title: "Dead assignment and misleading bound in the survivor failure message"
  - id: IN-02
    severity: info
    disposition: fixed
    title: "`fixture_hash` accepts non-string scalars it would encode wrongly"
  - id: IN-03
    severity: info
    disposition: fixed
    title: "The \"no path that passes without the browser\" scan is line-based and spelling-based"
  - id: IN-04
    severity: info
    disposition: fixed
    title: "Inconsistent waits and a hot loop in `test_browser.py`"
open: 0
total: 7
recorded: 2026-10-21T00:00:00Z  # triage by hand; the gate's own stamp was 2026-10-10T15:02:32.792Z
---

# Phase 21: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | a7c5f78 fix(tests): stop_group signals the server group before it reads ps (the group teardown was first moved to a playwright-free module in 675cf68; Phase 27 branch, squashed into 1434a47); docs/tech_debt/resolved/2026-10-10-stop-group-reads-ps-before-it-signals.md |
| WR-02 | warning | fixed | 99e2b7d docs(27): name the server group's members as ps lists them, with dated corrections (Phase 27 branch, squashed into 1434a47); docs/tech_debt/resolved/2026-10-10-group-floor-of-3-is-not-two-pool-workers.md |
| WR-03 | warning | fixed | a393e50 fix(tests): name the reinstall that works when the browser stamp is current (Phase 27 branch, squashed into 1434a47); docs/tech_debt/resolved/2026-10-10-launch-failure-message-names-a-stamp-that-skips-the-install.md |
| IN-01 | info | fixed | a7c5f78 fix(tests): stop_group signals the server group before it reads ps (the dead assignment and the misleading bound are gone with the reorder; Phase 27 branch, squashed into 1434a47) |
| IN-02 | info | fixed | 4d43b64 test(27): check _js_number's range and -0, refuse a non-scalar fixture param, re-wrap a docstring (`fixture_hash` refuses a non-scalar param; Phase 27 branch, squashed into 1434a47) |
| IN-03 | info | fixed | 0ed2057 test(27): read the browser pins' environ allowance from the statement, not the line (the environ allowance is read from the statement, not the line; Phase 27 branch, squashed into 1434a47) |
| IN-04 | info | fixed | 1981d93 Phase 26: Gate Fails With a Cause (#41), branch commit 6ff1269 fix(26): take the twin-selectors baseline after the link's own STL request and settle past the debounce, for 04a (the waits). 04b (the hot loop) is deferred to docs/tech_debt/active/2026-10-15-wait-until-parked-spins-without-a-pause.md (D-16) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
