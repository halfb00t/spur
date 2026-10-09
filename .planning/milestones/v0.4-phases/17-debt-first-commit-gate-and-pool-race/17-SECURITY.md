---
phase: "17"
slug: "debt-first-commit-gate-and-pool-race"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-06"
verified: "2026-10-06"
---

# Phase 17 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.
> Register authored at plan time (all five plans carry a `<threat_model>`); verified at L1 grep depth by secure-phase after execution, 2026-10-06.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| developer workstation → commit | the commit stage runs `make verify.fast`, a subset; a red heavy-tier change can be committed locally | source and test changes |
| developer workstation → remote | the pre-push hook runs the whole `make verify`, the last local check before CI and the `main` ruleset (L22) | pushed commits |
| shared `.git/hooks` ← any checkout's gate run | every linked worktree shares one hooks dir; whichever venv installs last owns the shim | hook shims, venv path |
| this repository → a public issue tracker | the upstream request is posted under the user's account, readable by anyone | issue text |
| gsd SDK (`execGit`, 30 s) → git → repo hooks | a killed commit leaves a hook process running outside any tool's control | commit, hook stash |
| bench client → a live HTTP server on the host | the `identical` scenario drives builds past their timeout and replaces workers | gear params, 500/503 bodies |
| committed investigation files → the repository | raw server logs (tracebacks with local paths) enter `.planning/` | uvicorn logs |
| HTTP client → `app.py` → `BuildPool` | an unhandled exception in the pool becomes a raw 500 with a server-side traceback | error bodies |
| event-loop thread ↔ executor manager threads | the cleanup's atomicity rests on nothing yielding the loop thread | executor state |
| shared links (query strings) → `GearParams` defaults and caps | a moved default or `le` would silently change or refuse a link that builds today | gear params |
| the decision log and README → users and later phases | a margin figure there is read as a property of the service | documented limits |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-17-01 | Tampering | commit stage (`make verify.fast`) — a red `test_model`/`test_pool`/`test_api`/`test_cli` change commits | medium | mitigate | `verify.fast: verify.static test.fast` (Makefile); `verify` at `stages: [pre-push]`; CI + `main` ruleset + `make pr.land` (L22/L25); L36 states which commits can be red; `make verify` ran green before the hook commit `c06749d` | closed |
| T-17-02 | Denial of service | `$(HOOKS)` stamp run from a linked worktree repoints the shared hooks at a venv `make worktree.land` deletes | medium | mitigate | main-checkout guard (`--absolute-git-dir` vs `--git-common-dir`) in the Makefile; `tests/test_hooks.py::test_the_hook_stamp_installs_from_the_main_checkout_and_never_from_a_linked_worktree` | closed |
| T-17-03 | Tampering | drift between the hook entry and the gate (two lists of checks) | medium | mitigate | `verify.static` shared by `verify` and `verify.fast`; `tests/test_hooks.py::test_verify_and_verify_fast_share_one_static_prefix_and_one_pytest_recipe` | closed |
| T-17-04 | Repudiation | `--no-verify` / `SKIP=` bypass at commit or push | low | accept | out of scope (REQUIREMENTS); L36's scratch table records both bypasses exist (rows 7, 8); CI + ruleset + pr.land are the wall — see Accepted Risks | closed |
| T-17-05 | Information disclosure | the upstream issue text (local paths, user name, tokens, private repo details) | medium | mitigate | 17-02 Task 1 verify refused `/Users/`, `/home/`, the user name, `commands.cjs:<n>` and token prefixes; blocking-human checkpoint on the exact text; posted unchanged as open-gsd/gsd-core#5231; re-checked here | closed |
| T-17-06 | Tampering | a killed SDK commit retried blind, two gates sharing pre-commit's stash | medium | mitigate | D-07 in docs/HOW_TO_DEVELOP.md §4 and L36: wait until `pgrep` prints nothing, one plain commit, never a blind SDK retry; not triggered — every SDK commit of the phase returned `committed: true` | closed |
| T-17-07 | Spoofing | the SC1 proof faked by a hand commit | low | mitigate | `17-02-sdk-commit.json` carries `"committed": true` and hash `5a3332f`, the commit that carries exactly the three paths | closed |
| T-17-08 | Denial of service | the long-lived `spur-spur-1` container on :8000 disturbed by the bench | medium | mitigate | every attempt targeted a fresh server on :8001; `lsof` preflight; `docker ps` recorded before and after (no container existed); port free after each run | closed |
| T-17-09 | Repudiation | a reproduction recorded that nobody saw (or a miss dropped) | medium | mitigate | 17-03 Task 2 check ties every `500` row to the server's own `AttributeError` record; verdict `Reproduced in attempt 1.` in `bench/RESULTS.md`; raw logs committed under `investigation/` | closed |
| T-17-10 | Information disclosure | committed server logs carry uvicorn tracebacks with local filesystem paths | low | accept | same kind of record SC3 committed; no secret, token or user data in a gear-build log; `build.failed` records carry no traceback (records.py T-03-05) — see Accepted Risks | closed |
| T-17-11 | Denial of service | an orphaned wedged worker (~810–870 MiB, L17) or an unowned executor after a mishandled cleanup | medium | mitigate | the two-fact guard keeps the first caller's terminate-and-replace; `_closed` in `src/spur/pool.py` stops replacements after shutdown; `tests/test_pool.py::test_three_same_tick_same_slot_timeouts_each_end_in_a_documented_refusal` reaps the terminated worker and proves a fresh one serves | closed |
| T-17-12 | Information disclosure | an unhandled `AttributeError` reaching the client as a raw 500 | medium | mitigate | the second caller raises `BuildTimeout` → documented `503` `timeout`; `tests/test_pool.py::test_a_stale_executor_timeout_is_a_build_timeout_not_an_attribute_error`; after-fix bench: four `503 timeout`, zero `500` (17-05) | closed |
| T-17-13 | Tampering | a later edit inserting an `await` into the terminate-and-replace block, reopening the race | low | mitigate | `tests/test_pool.py::test_the_timeout_branch_never_awaits_before_it_raises` (ast tripwire with a seeded `await`) | closed |
| T-17-14 | Repudiation | a broad handler masking a third defect | low | mitigate | the same ast test pins the handler types to `TimeoutError` and `BrokenProcessPool` | closed |
| T-17-15 | Tampering | `SPUR_BUILD_TIMEOUT` default or `spoke_count`'s `le` moved by the margin decision (L05) | medium | mitigate | `src/spur/params.py` byte-identical to `e64d764`; `app.py` diff comment-only with `int_env("SPUR_BUILD_TIMEOUT", 30)` intact (17-05 Tasks 2 and 3; re-checked here); `tests/test_api.py` pins `spoke_count` maximum 32 | closed |
| T-17-16 | Repudiation | a margin number stated without its source or load, or tuned toward a pass (L08) | low | mitigate | L37 carries 29.42, 0.58, 30004, `51e80f35`, 29.41/30.11 and "at this load", each with its section; dated notes in `bench/RESULTS.md` and the tip-chamfer debt cite them | closed |
| T-17-17 | Repudiation | the stability claim behind the race fix asserted but not re-readable | low | mitigate | `investigation/17-04-stability.md` committed with one row per run and the blob ids (`2e2a9b6a…`, `322107c7…`) of the code the 43 runs ran; run 2's failing log committed beside it as `17-04-verify-2.log` | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on (high) count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

Per-plan `T-17-SC` supply-chain rows: no package was added in any plan (pre-commit is an existing dev extra; `gh`, gsd-core, httpx, `ast`, `pathlib` already on the host or stdlib); `requirements.txt` untouched. Reserved rows, not register entries.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-17-01 | T-17-04 | `--no-verify` / `SKIP=` are out of scope (REQUIREMENTS); the scratch table in L36 records that both bypasses exist; CI, the `main` ruleset and `make pr.land` are the wall (L22/L25) | 17-01 plan (human-approved plan), executed 2026-10-06 | 2026-10-06 |
| R-17-02 | T-17-10 | committed uvicorn logs carry local filesystem paths in tracebacks — the same kind of record SC3 committed; no secret, token or user data in a gear-build log; `build.failed` records carry no traceback by design | 17-03 plan (human-approved plan), executed 2026-10-06 | 2026-10-06 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-06 | 17 | 17 | 0 | secure-phase (orchestrator, L1 grep-depth; register authored at plan time, ASVS 1 — auditor not spawned per the short-circuit rule) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-06

## Security Audit 2026-10-06

| Metric | Count |
|---|---|
| Threats found | 17 |
| Closed | 17 |
| Open | 0 |
