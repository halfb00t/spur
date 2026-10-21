---
phase: "28"
slug: "refuse-the-bad-link"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-21"
---

# Phase 28 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `28-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (+ xdist 3.8.0, cov 7.1.0); Playwright sync API for the browser file |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `.venv/bin/python -m pytest --no-cov -n0 -q -p no:cacheprovider tests/test_api.py -k "shareable_link or every_key_the_ui or root_form_d_is_never or root_shape"` |
| **Browser run command** | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"` |
| **Full suite command** | `make verify` |
| **Estimated runtime** | quick ~2 s; browser ~23 s; full under the 300 s bar (L43) |

---

## Sampling Rate

- **After every task commit:** quick `test_api.py` command; plus the browser command whenever `app.js` or `test_browser.py` moved.
- **After every plan wave:** `make verify`.
- **Before `/gsd-verify-work`:** `make verify` green, `git diff --exit-code v0.5 -- tests/regression/` empty, triage grep empty.
- **Max feedback latency:** 30 seconds (browser run).

---

## Per-Task Verification Map

Filled by the planner per task; requirement-level map below.

| Requirement | Behavior | Test Type | Automated Command | File Exists | Status |
|-------------|----------|-----------|-------------------|-------------|--------|
| REQ-bad-link-refused | four bad links: token kept and sent, server text, field marked (mate: message only), no STL, no new triangles; edit/Reset clear | browser | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"` | step rewrite | ⬜ pending |
| REQ-bad-link-refused | generic over the schema; pinned `app.js` tokens hold | static | quick command (`-k shareable_link`) | extend existing tuple | ⬜ pending |
| REQ-bad-link-refused | valid links unchanged | browser + diff | golden sweep step; `git diff --exit-code v0.5 -- tests/regression/` | ✅ | ⬜ pending |
| REQ-bad-link-decision-logged | old pin red vs fix; new pin red with fix reverted; L44; debt retired; web-ui.md true | manual-with-record + grep | logs in `investigation/`; `grep -n '^## L44' docs/architecture/decision_log.md` | n/a | ⬜ pending |
| REQ-root-fillet-label-follows-root | hob → "Hob tip radius used"; radial/fallback → "Root fillet used" | browser | browser command | new assertions | ⬜ pending |
| REQ-info-findings-triaged / REQ-old-info-findings-triaged | no `\| info \| open \|` rows in scope | grep | `grep -rn '\| info \| open \|'` over the in-scope `*-REVIEW-DISPOSITION.md` prints nothing | n/a | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements (framework, harness and browser all ran green during research).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Red-first record: old pin red against the fix, new pin red with the fix reverted | REQ-bad-link-decision-logged | The red runs are a one-time evidence record, not a standing test | Run the browser command in each state; save logs under `.planning/phases/28-refuse-the-bad-link/investigation/` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
