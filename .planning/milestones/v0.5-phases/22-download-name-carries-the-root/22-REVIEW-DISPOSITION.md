---
phase: 22
review: 22-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "`slug()` totality is unguarded in CI and the function now runs inside failure-record paths"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "`test_a_failed_build_records_the_name_of_the_part_it_would_have_been` depends on no other test requesting the same gear"
  - id: IN-01
    severity: info
    disposition: fixed
    title: "The bore-off field block is duplicated in two test files"
  - id: IN-02
    severity: info
    disposition: fixed
    title: "Ragged docstring reflow in `serve_stl_from`"
  - id: IN-03
    severity: info
    disposition: fixed
    title: "L40 quotes the best-case reading of the new step as its cost"
open: 0
total: 5
recorded: 2026-10-21T00:00:00Z  # triage by hand; the gate's own stamp was 2026-10-11T06:51:09.210Z
---

# Phase 22: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | 345ee08 test(27): guard slug() totality with a seeded, stratified test in the commit slice (a seeded, stratified `slug()` totality test; Phase 27 branch, squashed into 1434a47); docs/tech_debt/resolved/2026-10-15-slug-totality-is-not-guarded-in-the-gate.md |
| WR-02 | warning | fixed | c47bfc4 test(27): give the failed-build name test its own export cache (the failed-build name test has its own export cache; Phase 27 branch, squashed into 1434a47); docs/tech_debt/resolved/2026-10-15-failed-build-name-test-depends-on-cache-order.md |
| IN-01 | info | fixed | c30ebd0 test(27): walk the OpenAPI document for selectors, share the bore-off block, probe the honeycomb gate twice (one `BORE_OFF` in `tests/composition.py` for the finding's two files; Phase 27 branch, squashed into 1434a47). Inline copies outside them are left: `tests/test_cli.py` `_BORE_OFF`, and bore-off field blocks in `tests/test_calc.py`, `tests/test_bench.py` and `tests/test_model.py` |
| IN-02 | info | fixed | 4d43b64 test(27): check _js_number's range and -0, refuse a non-scalar fixture param, re-wrap a docstring (`serve_stl_from`'s docstring re-wrapped; Phase 27 branch, squashed into 1434a47) |
| IN-03 | info | fixed | d7f069d docs(27): amend L40 with the download step's range and record the phase's red runs (L40's dated amendment; Phase 27 branch, squashed into 1434a47) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
