---
phase: "21"
slug: "browser-test-of-the-viewer"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-10"
---

# Phase 21 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| PyPI / cdn.playwright.dev → developer host and CI | a new third-party driver (`playwright==1.63.0`, `pyee`, `greenlet`) and a browser download enter the dev toolchain only | wheels and a headless-shell archive; dev extra only, never the runtime closure (L11, L12) |
| test process → uvicorn subprocess | a long-lived server and its `BuildPool` started by a test; must not be reachable off-host or outlive the test | HTTP on a kernel-assigned port bound to 127.0.0.1, passed by descriptor |
| this repo's gate → the host's shared Playwright cache | another project's browser lives in `~/Library/Caches/ms-playwright` | the shell installs only under `.venv/ms-playwright` |
| a throwaway branch → GitHub (CI, PRs) | `spike/21-linux-runner` with gate wiring sat beside the real work on the remote | a do-not-merge draft PR (#32, closed unmerged) |
| GitHub-hosted runner → apt via sudo | `--with-deps` installs system libraries on the ephemeral runner | CI only; local default empty |
| browser page → test assertions | DOM text built from server responses | expectations read from `/api/schema`, `/api/info` at test time |
| a shareable link (user fragment) → form → API | untrusted hash; validation stays at the `GearParams` boundary | the browser test observes, never validates |
| regen script → committed pin | `tests/regression/golden_requests.json` is what later phases trust | 44 queries; only `make golden.regen` writes it |
| the gate's definition of passing → pre-push, CI, `worktree.land` | a test that can pass without running makes "green" lie | the admission commit and its pins |
| the agent → the remote repository | pushes, PRs and branch deletion are the human's | `gh` reads only; pushes made by the orchestrator at the human's explicit instruction |
| a measured figure → a locked decision | L39 cites what the phase measured (L08) | run ids, shas, subsection names |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-21-01 | Information disclosure | `serve()` listening socket | medium | mitigate | `tests/browser_session.py`: bound to `127.0.0.1`, port 0, handed to uvicorn with `--fd` | closed |
| T-21-02 | Denial of service | orphaned uvicorn / pool workers | medium | mitigate | `start_new_session=True`, `killpg` SIGTERM then SIGKILL in a `finally`, survivor check with a floor of 3 members; leader-only kill seen red (21-01) | closed |
| T-21-03 | Tampering | developer `SPUR_*` leaking into the server under test | low | mitigate | child environment drops every `SPUR_*` key (D-11) | closed |
| T-21-04 | Tampering | `ps` and uvicorn invocations | low | mitigate | fixed argument lists; no `shell=True` in `tests/browser_session.py` | closed |
| T-21-05 | Tampering | driver and shell drift between hosts | medium | mitigate | exact `"playwright==1.63.0"` in `[dev]`; `$(BROWSER): $(STAMP)` re-installs on a pin change | closed |
| T-21-06 | Tampering | the host's shared browser cache | medium | mitigate | `export PLAYWRIGHT_BROWSERS_PATH := $(abspath $(VENV))/ms-playwright` in the Makefile; host cache listed before/after and unchanged (21-01, 21-06) | closed |
| T-21-07 | Tampering | integrity of the shell archive from cdn.playwright.dev | low | accept | RESEARCH A5 assumes Playwright verifies its download; the exact wheel pin is the project's control — see Accepted Risks | closed |
| T-21-SC | Tampering | pip install of `playwright`, `pyee`, `greenlet` (SUS by the legitimacy audit) | high | mitigate | 21-01 Task 1 blocking-human legitimacy gate answered `approved` (dry-run list and PyPI metadata recorded in 21-01-SUMMARY); none of the three in `requirements.txt`, `Dockerfile` or `docker/refresh-requirements.sh` | closed |
| T-21-08 | Tampering | `spike/21-linux-runner` merged or landed by mistake | medium | mitigate | draft PR #32 titled DO NOT MERGE, closed unmerged; `git merge-base --is-ancestor spike/21-linux-runner HEAD` exits non-zero | closed |
| T-21-09 | Elevation of privilege | `playwright install --with-deps` via sudo on the runner | low | accept | CI only on GitHub's ephemeral runner (`BROWSER_INSTALL_ARGS: --with-deps` in `ci.yml`); Makefile default empty — see Accepted Risks | closed |
| T-21-10 | Repudiation | a step passing on a stale DOM state | medium | mitigate | content waits on expected text/href for the query sent (`tests/test_browser.py`), never element counts; fragment-change guard | closed |
| T-21-11 | Tampering | a deliberate break left in `app.js` / `style.css` | medium | mitigate | `style.css` byte-identical to `592506f`; `app.js` differs by the one `data-triangles` line and its comment (L39) | closed |
| T-21-12 | Tampering | an invalid enum in a link silently becomes the default | low | transfer | pinned as today's behaviour (`root_shape=bogus as today`) and filed as `must` debt `docs/tech_debt/active/2026-10-10-root-shape-bogus-loads-a-blank-select.md`; server validation unchanged | closed |
| T-21-13 | Repudiation | a round-trip step passing on a no-op hash assignment | low | mitigate | fragment asserted to differ before each assignment; the captured request is the signal | closed |
| T-21-14 | Tampering | `golden_requests.json` rewritten to match a regression | medium | mitigate | only `tests/capture_requests.py` (`make golden.regen`) writes it; `tests/test_browser.py` reads it; regen on unchanged code byte-identical (verified 2026-10-10 at `d4371cb`) | closed |
| T-21-15 | Tampering | `tests/regression/pre_v0_2.json` (L05/L26 fixture) | high | mitigate | `git diff --quiet 592506f -- tests/regression/pre_v0_2.json` exits 0 at `d4371cb` | closed |
| T-21-16 | Repudiation | a skip path or env opt-out making a green gate lie | high | mitigate | `tests/test_browser_pins.py` AST pins (no skip spelling, no `os.environ` read, exact dev-only pin, no plugin, no `channel=`), run at commit; `3 passed` at `d4371cb`; each seen red (21-06) | closed |
| T-21-17 | Denial of service | the browser test entering the commit slice past the 30 s kill | medium | mitigate | `--ignore=tests/test_browser.py` in `test.fast`; `HEAVY_TEST_FILES` set equality in `tests/test_hooks.py`; `verify.fast` 10.14–10.41 s | closed |
| T-21-18 | Tampering | the exclusion silently lapsing in `test-image` | low | mitigate | `test_the_image_suite_ignores_the_browser_test` reads the dry run; seen red | closed |
| T-21-19 | Elevation of privilege | `BROWSER_INSTALL_ARGS` as an injection point into a sudo-run install | low | accept | literal in `ci.yml` on an ephemeral runner; no user input reaches it — see Accepted Risks | closed |
| T-21-20 | Repudiation | a red run dropped so the price reads cleaner | medium | mitigate | seven logs kept under `investigation/21-07-*.log`, the red run classified under `#### Red runs` | closed |
| T-21-21 | Tampering | a price compared with another host's bar as if one | low | mitigate | L34's 66 s quoted with its host (M2 Max) and never rescaled; the delta is between two arms on one host, interleaved | closed |
| T-21-22 | Elevation of privilege | the agent pushing, merging or deleting branches on its own | high | mitigate | both pushes (spike, phase) went through `blocking-human` gates; the human explicitly instructed the orchestrator to perform them; executors never pushed; no branch deleted; the spike never merged | closed |
| T-21-23 | Repudiation | SC5 recorded from a stale or other-branch run | medium | mitigate | run `38059369744` `headSha` = pushed `88df5cf` (checked with `gh run view`); `1226 passed` matches the local B arm; log kept | closed |
| T-21-24 | Tampering | L39 citing a figure the record does not hold | low | mitigate | L39 names run `38059369744` and cites subsections and shas | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-21-01 | T-21-07 | Playwright's own download verification is assumed (RESEARCH A5); the exact wheel pin and the `.venv`-only install path are the project's controls; recorded as an assumption, not a measurement | the plan (21-01), accepted at planning | 2026-10-10 |
| R-21-02 | T-21-09 | `--with-deps` escalates to apt only on GitHub's ephemeral `ubuntu-latest` runner; local hosts never pass it (`BROWSER_INSTALL_ARGS` empty by default) | the plan (21-02), accepted at planning | 2026-10-10 |
| R-21-03 | T-21-19 | `BROWSER_INSTALL_ARGS` is a literal in `ci.yml`; no user input reaches the sudo-run install | the plan (21-06), accepted at planning | 2026-10-10 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-10 | 25 | 25 | 0 | /gsd-secure-phase 21 (orchestrator, L1 grep-depth short-circuit: register authored at plan time, ASVS 1) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-10
