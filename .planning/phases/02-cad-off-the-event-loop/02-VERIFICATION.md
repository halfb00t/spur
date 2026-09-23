---
phase: 02-cad-off-the-event-loop
verified: 2026-09-23T15:18:49Z
status: human_needed
score: 5/5 must-haves verified
behavior_unverified: 0
covered_files: [".planning/REQUIREMENTS.md", ".planning/phases/02-cad-off-the-event-loop/02-01-PLAN.md", ".planning/phases/02-cad-off-the-event-loop/02-01-SUMMARY.md", ".planning/phases/02-cad-off-the-event-loop/02-02-PLAN.md", ".planning/phases/02-cad-off-the-event-loop/02-02-SUMMARY.md", ".planning/phases/02-cad-off-the-event-loop/02-03-PLAN.md", ".planning/phases/02-cad-off-the-event-loop/02-03-SUMMARY.md", ".planning/phases/02-cad-off-the-event-loop/02-04-PLAN.md", ".planning/phases/02-cad-off-the-event-loop/02-04-SUMMARY.md", ".planning/phases/02-cad-off-the-event-loop/02-05-PLAN.md", ".planning/phases/02-cad-off-the-event-loop/02-05-SUMMARY.md", "Dockerfile", "Makefile", "README.md", "bench/README.md", "bench/RESULTS.md", "bench/__init__.py", "bench/corpus.py", "bench/latency.py", "bench/memory.py", "compose.yaml", "docker/smoke.py", "docs/architecture/decision_log.md", "docs/architecture/http-api.md", "docs/architecture/overview.md", "docs/architecture/packaging.md", "docs/tech_debt/INDEX.md", "docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md", "docs/tech_debt/resolved/2026-09-21-cad-builds-block-the-event-loop.md", "pyproject.toml", "src/spur/app.py", "src/spur/build_errors.py", "src/spur/cli.py", "src/spur/model.py", "src/spur/pool.py", "tests/test_api.py", "tests/test_pool.py"]
covered_digest: "v1:sha256:d5e21b3d498faed1c28bcc892fa7ec166bb5c80a437d70ee8cb0753ff2639e82"
overrides_applied: 1
overrides:
  - must_have: "the debt file's two load scenarios show /api/health p95 within 2x of idle p95, concurrent scenario"
    reason: "Eight runs across four sessions (bench/RESULTS.md) never demonstrated the concurrent scenario's <=2.00x ratio on both runs of one session (pre-fix 2.02x/2.45x, 2.32x/2.35x; post-fix 1.31x/2.10x, 1.86x/2.02x, the last pair on a host a watcher held under the file's own 1.5 idle-load bar). The human explicitly waived broken-windows ledger item 1 on this evidence rather than requiring a further re-run or fix, and filed the caveat plus two unexplained observations as must-severity tech debt (docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md). L18 (decision_log.md) records this as 'accepted with caveat, not demonstrated' verbatim. The single-build scenario (the debt file's own headline numbers) clears the bar on every run recorded."
    accepted_by: "human (via .planning/WINDOWS.md item 1, waived)"
    accepted_at: "2026-09-23T14:17:18.148Z"
human_verification:
  - test: "Bring the service up (`make up`) and watch it reach healthy with the Dockerfile's new HEALTHCHECK --timeout=2s; read the rewritten HEALTHCHECK comment and confirm it cites a number in bench/RESULTS.md and describes the shipped service rather than the one this phase replaced. Confirm the debt file's two shas (`daeb284` fixed it, `becedc0`/the 02-05 commit recorded the resolution) are distinguishable."
    expected: "Container reaches `healthy` well inside the new 2s/30s/3-retries window; comment text matches bench/RESULTS.md's measured p95 (0.7-2.3ms); the two shas are named and distinguished in docs/tech_debt/resolved/2026-09-21-cad-builds-block-the-event-loop.md."
    why_human: "02-05-PLAN.md Task 3's own <human-check> block; deferred to end-of-phase per workflow.human_verify_mode=end-of-phase (02-05-SUMMARY.md coverage D4, human_judgment: true). Automated evidence already collected this session: `docker inspect` on the running `spur-spur-1` container shows Timeout=2000000000ns (2s) and status healthy; this is presence/config evidence, not the qualitative 'watch it happen' check the plan asks a human to perform."
  - test: "Read docs/architecture/overview.md, docs/architecture/http-api.md and docs/architecture/packaging.md back to back as someone arriving at this repository for the first time. Confirm they tell one consistent story about where a build happens, what stops the serving process reaching the kernel, and where the memory ceiling comes from."
    expected: "No sentence in any of the three documents still describes the pre-phase (single-process, one-lock) architecture; all three agree on the pool/app/model split, the fourth import-linter contract, and the L17-derived mem_limit story."
    why_human: "02-05-PLAN.md Task 4's own <human-check> block; deferred to end-of-phase per workflow.human_verify_mode=end-of-phase (02-05-SUMMARY.md coverage D6, human_judgment: true). This verifier read all three documents this session (see Goal Achievement below) and found them consistent by inspection, but the plan explicitly assigns the final read to a human, not the executor or verifier."
---

# Phase 2: CAD Off the Event Loop Verification Report

**Phase Goal:** CAD kernel work runs in worker processes outside the request-serving
event loop, and the resulting multi-process memory ceiling is a measured number — not an
assumption carried forward from the single-process design L07 measured.
**Verified:** 2026-09-23T15:18:49Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

Five truths, one per ROADMAP.md success criterion. Truth 1 is asserted per-scenario
because the debt file's acceptance clause names two distinct scenarios with independent
outcomes; both halves are recorded rather than merged into a single averaged verdict.

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1a | `single` scenario: under-load p95 <= 2x idle p95, numbers recorded beside baseline | ✓ VERIFIED | `bench/RESULTS.md` § Latency: met on every run recorded across 3 sessions — Runs 1-2 (1.12x, 1.18x), Runs 3-4 (1.68x, 1.17x), Run 5 (1.10x). Debt file's baseline (0.22s→0.76s→2.00s, 12-core machine) quoted verbatim beside the new figures, labelled as a different machine (D-17). |
| 1b | `concurrent` scenario: under-load p95 <= 2x idle p95, numbers recorded beside baseline | PASSED (override) | Not demonstrated on both runs of any of 4 sessions (8 runs: 2.02x/2.45x, 2.32x/2.35x, 1.31x/2.10x, 1.86x/2.02x). Human waived `.planning/WINDOWS.md` item 1 on this evidence 2026-09-23T14:17:18Z; caveat filed as must-severity debt (`docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`); L18 records "accepted with caveat, not demonstrated" verbatim. See `overrides` in frontmatter. |
| 2 | Memory sweep of real N-worker topology produces a measured ceiling; `compose.yaml`'s `mem_limit` set from it | ✓ VERIFIED | `bench/RESULTS.md` § Memory: N=1/2/4 sweep (peaks 2052.1/2878.5/4731.9 MiB), `mem_limit: 4g` = 2878.5 MiB × 1.3 headroom, rounded up, confirmed 0/40 failures. `compose.yaml` ships `mem_limit: 4g` with the comment naming peak, factor and confirm result. L17 carries the same numbers. |
| 3 | `decision_log.md` gains entries superseding, and saying they supersede, L07 and L06 — dated, citing measurement, neither edited in place | ✓ VERIFIED | L17 ("supersedes L07") and L18 ("supersedes L06") present, both dated 2026-09-23, both citing `bench/RESULTS.md` numbers inline. `git show 163a84b --numstat -- docs/architecture/decision_log.md` = 151 added / 0 deleted — L06/L07 byte-identical (confirmed by direct read, both unchanged from the pre-phase text). |
| 4 | Debt file `Status: resolved`, sha recorded, `git mv`'d to `resolved/`, INDEX row moved — same commit as fix | ✓ VERIFIED | `docs/tech_debt/resolved/2026-09-21-cad-builds-block-the-event-loop.md` exists, reads `Status: resolved`, `Resolved in: daeb284` (with the distinguishing sentence naming `becedc0` as the commit that resolved it). `docs/tech_debt/active/...` no longer exists. `git show becedc0 -M --summary` records a 63%-similarity rename (not delete+add). `docs/tech_debt/INDEX.md`'s Active table no longer lists the item; its Resolved table does. |
| 5 | `make verify` passes with new topology; admission control stays in web layer; CLI never queues | ✓ VERIFIED | `make verify` run this session: ruff clean, `mypy --strict` "no issues found in 19 source files", 4 import-linter contracts kept/0 broken, 71 passed in 24.71s. `BUILD_QUEUE`/`_build_slot` live in `src/spur/app.py` (web layer). `src/spur/cli.py::cmd_export` imports `export` from `.model` directly — no pool, no queue import. |

**Score:** 5/5 truths verified (1 via override, `overrides_applied: 1`); 0 present-but-behavior-unverified.

### Advisory (New Scope, Unevidenced)

Not applicable — this is an initial verification, not a re-verification.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/build_errors.py` | Kernel-free `BuildError`/`BuildTimeout` | ✓ VERIFIED | Present, contains both classes, no reference to `cadquery`/`OCP`/`spur.model`. |
| `src/spur/pool.py` | `BuildPool`: N single-worker executors, affinity routing, timeout, termination/replacement | ✓ VERIFIED | Present; `BuildPool.__init__`, `executor_for`, `recreate_for`, `_run_with_timeout`, `export`, `shutdown` all implemented and match the described mechanics (terminates `_processes`, calls `recreate_for`, catches `asyncio.TimeoutError` by qualified name, catches `BrokenProcessPool`). |
| `src/spur/app.py` | Async model endpoint, lifespan-managed pool, byte cache, admission control derived from `SPUR_BUILD_WORKERS`, `/api/health` pool fields | ✓ VERIFIED | `lifespan` builds `BuildPool` eagerly; `model()` is `async def`; `_BlobCache`/`_EXPORTS` live here; `_max_queued_builds()` derives from `SPUR_BUILD_WORKERS`; `health()` returns nested `pool` object from parent-local counters only, synchronous `def`, no await/lock/worker call. |
| `pyproject.toml` | Import-linter contract forbidding `spur.app` → kernel, indirect included | ✓ VERIFIED | "The serving process never imports the CAD kernel" contract present, `allow_indirect_imports = false`, `source_modules = ["spur.app"]`. `lint-imports` (via `make verify`) reports 4 contracts kept, 0 broken. |
| `bench/latency.py`, `bench/memory.py`, `bench/corpus.py` | Rerunnable harness producing both scenarios and the N=1,2,4 sweep | ✓ VERIFIED | All present, exercised for real (not just `--help`) — `bench/RESULTS.md` is the produced output, 8 latency runs + 3 memory sweeps + a confirm run, all cross-checked against the harness's own emitted numbers. |
| `bench/RESULTS.md` | Committed measurement record | ✓ VERIFIED | 362 lines; Machine/Latency/Memory sections; every number in L17/L18/`compose.yaml`/`Dockerfile`/README traced back to a line here. |
| `docs/architecture/decision_log.md` | L17, L18 (+ L19) | ✓ VERIFIED | Present, dated, cite `bench/RESULTS.md`, L06/L07 untouched. |
| `docs/tech_debt/resolved/2026-09-21-cad-builds-block-the-event-loop.md` | Resolved debt item | ✓ VERIFIED | Present, `Status: resolved`, `Resolved in: daeb284`, original Context/Why-it-matters sections intact, new Resolution section added. |
| `Dockerfile` | HEALTHCHECK timeout from measured p95 | ✓ VERIFIED | `--timeout=2s` (was 10s), inner `urlopen timeout=1`, comment cites the measured 0.7-2.3ms p95 and points at `bench/RESULTS.md`. Live container confirmed at `Timeout: 2000000000ns`, status `healthy`. |
| `docs/architecture/overview.md` | System map redrawn for kernel-free server + N workers | ✓ VERIFIED | New `pool.py` row, updated `app.py`/`model.py` rows, fourth contract named, caches bullet points at L17. One page (matches `http-api.md`/`packaging.md` consistently — see Human Verification). |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `src/spur/app.py` | `src/spur/pool.py` | `app.state.pool` created in lifespan; `model()` awaits injected `build_backend` → `pool.export` | ✓ WIRED | Confirmed by reading `app.py`; `build_backend()` hard-fails (no silent inline fallback) if `app.state.pool` is `None`. |
| `src/spur/pool.py` | `src/spur/model.py` | Dynamic `importlib.import_module("spur.model")` inside the worker entry point | ✓ WIRED | Confirmed in `_warm()` and `build_export()`; static analysis (`lint-imports`) confirms this stays invisible to the forbidden-import contract while still resolving at runtime (contract kept, 0 broken). |
| `src/spur/app.py` | `src/spur/build_errors.py` | `BuildError`/`BuildTimeout` imported from the kernel-free module | ✓ WIRED | `from .build_errors import BuildError, BuildTimeout` present in `app.py`; both mapped to their own status codes in `model()`. |
| `docs/architecture/decision_log.md` (L17/L18) | `bench/RESULTS.md` | Numbers cited inline, traceable to the results file | ✓ WIRED | Cross-checked every figure in L17 (peaks, mem_limit, headroom, confirm result) and L18 (ratios) against `bench/RESULTS.md`'s own tables — all match. |
| `compose.yaml` `mem_limit` | `bench/RESULTS.md` | Comment cites the sweep row and headroom factor | ✓ WIRED | `mem_limit: 4g` comment names 2878.5 MiB peak, ×1.3 headroom, 0/40 confirm failures — all present verbatim in `bench/RESULTS.md`. |
| `docs/tech_debt/INDEX.md` | `docs/tech_debt/resolved/...` | Resolved-section link | ✓ WIRED | Row present under `## Resolved`, links to the moved file, which exists at that path. |

### Data-Flow Trace (Level 4)

Not separately applicable — this phase has no UI-rendered dynamic values; the "data"
that matters is measurement numbers flowing from `bench/RESULTS.md` into `compose.yaml`,
`Dockerfile` and `decision_log.md`, all traced above under Key Link Verification and
cross-checked by direct read (not a static fallback anywhere in the chain).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full test suite passes, including the process-boundary tests | `make verify` (ruff, mypy --strict, lint-imports, no-fake-done, pytest) | ruff clean; mypy "no issues found in 19 source files"; 4 import-linter contracts kept/0 broken; 71 passed in 24.71s (includes `tests/test_pool.py`'s 14 tests: real worker build+download, affinity routing, timeout-terminate-replace, broken-pool-replace, failure-mode mapping, health shape) | ✓ PASS |
| Running container reaches healthy under the new HEALTHCHECK | `docker ps` / `docker inspect --format '{{json .Config.Healthcheck}}' spur-spur-1` | `spur-spur-1 Up 13 minutes (healthy)`; `Timeout: 2000000000` (2s), matching Dockerfile | ✓ PASS |
| No debt-marker regressions in phase-modified files | `git grep -nE '\b(TODO|FIXME|XXX|HACK|NotImplementedError)\b' -- '*.py' '*.js' '*.sh' ':!src/spur/static/vendor'` (the exact `no-fake-done` gate command) | no output (0 matches) | ✓ PASS |
| CLI still calls `model.export` in-process, no pool | Direct read of `src/spur/cli.py::cmd_export` | `from .model import Format, export`; no import of `.pool` or `.app` anywhere in `cli.py` | ✓ PASS |

### Probe Execution

Not applicable — this phase declares no `scripts/*/tests/probe-*.sh` probes; its
measurement harness (`bench/`) is the analogous instrument and is covered above under
Behavioral Spot-Checks and the artifact/key-link tables (its output, `bench/RESULTS.md`,
was cross-checked directly against every downstream number rather than re-run, since a
fresh `make bench` run takes ~15+ minutes and would only reproduce, not contradict, the
already-committed record per D-16/D-17's own design — the harness's job is to make prior
claims falsifiable, not to be re-executed on every verification pass).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-cad-off-event-loop | 02-01, 02-02, 02-03, 02-04, 02-05 | CAD builds run outside the serving process; `/api/health` latency decoupled from build size | ✓ SATISFIED | Truths 1a/1b/4/5 above; `.planning/REQUIREMENTS.md` marks it `[x]` and `Complete` in the coverage table. |
| REQ-measured-memory-ceiling | 02-02, 02-04, 02-05 | Memory ceiling measured (not derived), `mem_limit` set from it, superseding decision-log entry | ✓ SATISFIED | Truths 2/3 above; `.planning/REQUIREMENTS.md` marks it `[x]` and `Complete`. |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s Phase 2 section lists exactly
these two IDs, both claimed across the five plans' frontmatter `requirements:` fields.

### Anti-Patterns Found

None in phase-scoped files. `no-fake-done` gate (part of `make verify`) scans the whole
repository for `TODO`/`FIXME`/`XXX`/`HACK`/`NotImplementedError` and returned clean this
session. No stub returns, empty handlers, or hardcoded-empty data patterns found in
`src/spur/pool.py`, `src/spur/app.py`, or `src/spur/build_errors.py` on direct read.

### Human Verification Required

Two items, both explicitly deferred by the plans themselves to end-of-phase per
`workflow.human_verify_mode=end-of-phase` (02-05-PLAN.md Tasks 3 and 4's own
`<human-check>` blocks). Listed in frontmatter `human_verification`. Automated/read-based
evidence for both was already collected this session (see table below and the Goal
Achievement / artifact sections above), but the plans assign the final qualitative call
to a human, not to an agent.

1. **Watch the container reach healthy under the new 2s HEALTHCHECK timeout, and read the
   rewritten comment against `bench/RESULTS.md`.**
   Expected: reaches `healthy` well inside 2s/30s/3-retries; comment cites the measured
   0.7-2.3ms p95.
   Why human: 02-05-PLAN.md Task 3's own `<human-check>`; this verifier confirmed the
   container is currently `healthy` with `Timeout: 2000000000ns` via `docker inspect`,
   which is config/state evidence, not the "watch it happen" observation the plan asks
   for.

2. **Read `overview.md`, `http-api.md` and `packaging.md` back to back for one
   consistent story.**
   Expected: no sentence in any of the three still describes the pre-phase architecture.
   Why human: 02-05-PLAN.md Task 4's own `<human-check>`; this verifier read all three
   documents this session and found them mutually consistent (kernel-free server + N
   workers, fourth import-linter contract, L17-derived `mem_limit`) by inspection, but
   the plan assigns the final read explicitly to a human.

### Gaps Summary

None. All five roadmap success criteria are met or explicitly, evidentially overridden
by a documented human decision already on record in the codebase (`.planning/WINDOWS.md`,
`docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`, `decision_log.md`
L18) — not a gap introduced or accepted by this verification pass. `make verify` is
green (71 tests, 4 contracts, clean lint/mypy/no-fake-done); the debt-resolution
lifecycle, the decision-log supersession, and the measured knobs (`SPUR_BUILD_TIMEOUT`,
`mem_limit`, `SPUR_BUILD_WORKERS`, the HEALTHCHECK timeout) are all traceable to
`bench/RESULTS.md`. Two items remain for human sign-off per the plans' own deferred
`<human-check>` design, not because anything is unverified in the codebase.

---

_Verified: 2026-09-23T15:18:49Z_
_Verifier: Claude (gsd-verifier)_
