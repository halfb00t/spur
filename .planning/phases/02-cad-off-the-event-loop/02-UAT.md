---
status: testing
phase: 02-cad-off-the-event-loop
source: [02-VERIFICATION.md]
started: 2026-09-23T15:23:51Z
updated: 2026-09-23T15:23:51Z
---

## Current Test

number: 1
name: The container reaches healthy under the new 2 s HEALTHCHECK timeout, and the rewritten comment describes the shipped service
expected: |
  `make up` (or the already-running `spur-spur-1`, rebuilt from becedc0) reaches `healthy` well
  inside the 2s timeout / 30s interval / 3 retries window. The HEALTHCHECK comment in the
  Dockerfile cites the measured under-load p95 range from bench/RESULTS.md (0.7-2.3 ms across
  the eight runs; worst 2.3 ms, Run 3 concurrent, pre-L19) and describes a kernel-free serving
  process, not the GIL-holding one this phase replaced. In
  docs/tech_debt/resolved/2026-09-21-cad-builds-block-the-event-loop.md the two shas are
  distinguishable: daeb284 fixed it (02-01, build moved into a worker), becedc0 recorded the
  resolution and removed the last accommodation.
awaiting: user response

## Tests

### 1. The container reaches healthy under the new 2 s HEALTHCHECK timeout, and the rewritten comment describes the shipped service
expected: `make up` reaches `healthy` inside 2s/30s/3 retries; the Dockerfile HEALTHCHECK comment cites bench/RESULTS.md's measured under-load p95 (0.7-2.3 ms across the eight runs) and describes the shipped service; the resolved debt file names and distinguishes daeb284 (the fix) from becedc0 (the resolution).
result: [pending]

### 2. overview.md, http-api.md and packaging.md tell one consistent story
expected: Read docs/architecture/overview.md, docs/architecture/http-api.md and docs/architecture/packaging.md back to back as a first-time reader. No sentence still describes the pre-phase single-process, one-lock architecture; all three agree on where a build happens (a pool worker), what stops the serving process reaching the kernel (the fourth import-linter contract), and where the memory ceiling comes from (L17's sweep).
result: [pending]

## Summary

total: 2
passed: 0
issues: 0
pending: 2
skipped: 0
blocked: 0

## Gaps
