---
schema_version: 1
open_count: 1
waived_count: 0
fixed_count: 0
total_count: 1
last_updated: 2026-09-23T10:47:42.245Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 02 | unmet-truth | bench/RESULTS.md |  | Concurrent latency scenario's under-load/idle p95 ratio not demonstrated <=2x on this measurement session (2.02x, 2.45x); needs re-run on idle host or explicit accept decision before REQ-cad-off-event-loop closes | open |  | 2026-09-23T10:47:42.245Z |  |

````json
[
  {
    "id": 1,
    "kind": "unmet-truth",
    "phase": "02",
    "file": "bench/RESULTS.md",
    "line": null,
    "description": "Concurrent latency scenario's under-load/idle p95 ratio not demonstrated <=2x on this measurement session (2.02x, 2.45x); needs re-run on idle host or explicit accept decision before REQ-cad-off-event-loop closes",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-23T10:47:42.245Z",
    "resolved_at": null,
    "milestone": "v0.1"
  }
]
````
