---
phase: "26"
slug: "gate-fails-with-a-cause"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-15"
---

# Phase 26 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

The register was authored at plan time (all seven PLAN.md files carry a `<threat_model>`). With ASVS level 1,
`block_on: high` and no threat at or above `high`, verification is grep-depth (L1) against the final tree; no
auditor agent was spawned.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| caller's shell environment -> `make -n` child of a test | whatever the caller exported reached the dry run the pin compares | environment variables (no secrets) |
| local spike branch -> shared remote and GitHub Actions | a throwaway branch runs the full workflow on `pull_request` in the repo's own runners | repo tree, CI logs |
| phase branch -> shared remote and CI | the human pushes the phase's tree; CI runs it on a draft PR | repo tree, CI logs |
| CI log -> committed record | whole logs are committed under `.planning/` | CI output (no secrets printed) |
| test page -> local uvicorn | the browser test drives the shipped app on localhost; routes intercept only the test's own page | HTTP on localhost |
| gate test -> child Python process | the test starts an interpreter with a fixed script and fixed test ids | argv, filtered env |
| xdist worker -> other tests on the same worker | a monkeypatch of a stdlib class could leak into unrelated tests | in-process state |
| test process -> log (local and CI) | faulthandler writes every thread's stack to stderr | stack frames, paths |
| working tree -> commit hook | an untracked test file is collected by `make verify.fast` at commit | test files |
| host checkout -> container running as root | the recipe mounts host directories into a root container | source, tests, bench, scripts (read-only) |
| container -> package index | the recipe installs unpinned test packages at run time | PyPI packages |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-26-01 | Tampering | `tests/test_hooks.py::_make_env` | low | mitigate | `PYTEST_ARGS` is in `_MAKE_VARIABLES` (`tests/test_hooks.py:27`), filtered at `:53`; both caller forms pinned by tests seen red first (26-01) | closed |
| T-26-02 | Tampering | spike PR merged by mistake | medium | mitigate | PR #40 was a draft titled `-- DO NOT MERGE`; `gh pr view 40` reads `CLOSED` (unmerged) | closed |
| T-26-03 | Elevation of Privilege | workflow on a same-repo `pull_request` | low | accept | see Accepted Risks AR-26-01 | closed |
| T-26-04 | Repudiation | classification from a partial log | low | mitigate | three whole job logs kept as `investigation/26-02-run-38724011970-*.log` | closed |
| T-26-05 | Information Disclosure | CI logs committed under `.planning/` | low | accept | see AR-26-02 | closed |
| T-26-06 | Tampering | route interception leaking to other steps | low | mitigate | routes registered on `twins_page`, own context, closed in `finally`; throwaway arms reverted, tree clean (26-03 SUMMARY) | closed |
| T-26-07 | Repudiation | a fix landed on an unproved mechanism | medium | mitigate | real-app arms recorded before the step was edited (26-03, `bench/RESULTS.md`) | closed |
| T-26-08 | Tampering | `subprocess.run` in the gate test | low | mitigate | fixed argv, no `shell=True` in `tests/test_pool.py`; env drops `PYTEST_ADDOPTS` and `PYTEST_ARGS` (`tests/test_pool.py:758`) | closed |
| T-26-09 | Tampering | `ResourceTracker._check_alive` patch leaking to other tests | medium | mitigate | the patch exists only in the `python -c` child (`_FORCED_GC`); the parent never patches | closed |
| T-26-10 | Repudiation | retiring the item on a quiet run or a symptom filter | medium | mitigate | forced-GC test red 3/3 then green on record; rule commit `957539c` precedes fix `21b46f8`; `src/spur/pool.py` unchanged vs `v0.5` | closed |
| T-26-11 | Information Disclosure | stack dumps in CI logs | low | accept | see AR-26-03 | closed |
| T-26-12 | Denial of Service | the stall probe left on disk stalls the commit hook | medium | mitigate | `tests/test_zz_stall_probe.py` absent from the tree and from every commit (`git log --all` empty) | closed |
| T-26-13 | Denial of Service | `-v` output and durations lengthen the gate | low | mitigate | measured 3 + 3 interleaved: -0.51 %, max 218.94 s against the 300 s bar (26-05) | closed |
| T-26-14 | Tampering | new `bench/` and `scripts/` mounts into a `--user root` container | medium | mitigate | all five mounts are `:ro` (`Makefile:252-254`); the pin asserts the mode set | closed |
| T-26-15 | Tampering | unpinned `pip install` inside the container | low | accept | see AR-26-04 (widened by human decision in 26-06) | closed |
| T-26-16 | Repudiation | ignoring a file to hide a real red | medium | mitigate | every ignore traces to `investigation/26-06-redset.md`; the one `other` red stopped for the human (D-11), resolved by option B, not an ignore | closed |
| T-26-17 | Tampering | draft phase PR merged before ship | medium | mitigate | `gh pr view 41` reads `OPEN draft=true` | closed |
| T-26-18 | Repudiation | `faulthandler_timeout` changed on an unrecorded reading | low | mitigate | changed 120 -> 170 in its own commit `faf376b`, from run 38750065494's recorded durations (S_ci 83.55 s) | closed |
| T-26-19 | Information Disclosure | CI logs committed under `.planning/` | low | accept | see AR-26-02 | closed |
| T-26-SC | Tampering | npm/pip/cargo installs | low | accept | see AR-26-05 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-26-01 | T-26-03 | no new secret, job or permission; only `runs-on` differed from the shipped workflow | plan 26-02 (planner) | 2026-10-15 |
| AR-26-02 | T-26-05, T-26-19 | the workflow prints no secret; committed logs are the same ones GitHub shows on the PR | plans 26-02, 26-07 (planner) | 2026-10-15 |
| AR-26-03 | T-26-11 | frames show repo-relative/venv paths and function names only; the suite holds no secret | plan 26-05 (planner) | 2026-10-15 |
| AR-26-04 | T-26-15 | the `make test-image` container's unpinned `pip install` runs only in a throwaway `--rm` container, never in CI. 26-06 widened the line from `pytest httpx` to add `pytest-cov pytest-xdist` (option B), so the forced-GC gate test runs in the image; the human chose option B at the 26-06 checkpoint. A compromised or drifted package affects only a local test run. | human (26-06 checkpoint) | 2026-10-15 |
| AR-26-05 | T-26-SC | no package added to the project's dependency closure (`requirements.txt`, `pyproject.toml` deps unchanged); only the container line in AR-26-04 changed | plans 26-01..26-07 (planner) | 2026-10-15 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-15 | 20 | 20 | 0 | execute-phase orchestrator (L1 grep check, no auditor: register authored at plan time, ASVS 1) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-15
