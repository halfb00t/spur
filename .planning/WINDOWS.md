---
schema_version: 1
open_count: 0
waived_count: 1
fixed_count: 0
total_count: 1
last_updated: 2026-09-23T14:17:18.148Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 02 | unmet-truth | bench/RESULTS.md |  | Concurrent latency scenario's under-load/idle p95 ratio not demonstrated <=2x on this measurement session (2.02x, 2.45x); needs re-run on idle host or explicit accept decision before REQ-cad-off-event-loop closes | waived | Accepted with caveat by the human on the Runs 1-8 evidence (bench/RESULTS.md): post-fix (7a61fad) runs read 1.31x, 2.10x, 1.86x, 2.02x against the 2.00x bar vs pre-fix 2.02x-2.45x; every first run of a pair passes, the misses are <=0.10x over on a 0.6 ms idle p95, and Runs 7-8 were on a host waited for below the 1.5 idle bar. The second-run-of-pair effect is uninvestigated; tracked in docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md | 2026-09-23T10:47:42.245Z | 2026-09-23T14:17:18.148Z |

````json
[
  {
    "id": 1,
    "kind": "unmet-truth",
    "phase": "02",
    "file": "bench/RESULTS.md",
    "line": null,
    "description": "Concurrent latency scenario's under-load/idle p95 ratio not demonstrated <=2x on this measurement session (2.02x, 2.45x); needs re-run on idle host or explicit accept decision before REQ-cad-off-event-loop closes",
    "status": "waived",
    "reason": "Accepted with caveat by the human on the Runs 1-8 evidence (bench/RESULTS.md): post-fix (7a61fad) runs read 1.31x, 2.10x, 1.86x, 2.02x against the 2.00x bar vs pre-fix 2.02x-2.45x; every first run of a pair passes, the misses are <=0.10x over on a 0.6 ms idle p95, and Runs 7-8 were on a host waited for below the 1.5 idle bar. The second-run-of-pair effect is uninvestigated; tracked in docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md",
    "recorded_at": "2026-09-23T10:47:42.245Z",
    "resolved_at": "2026-09-23T14:17:18.148Z",
    "milestone": "v0.1"
  }
]
````
