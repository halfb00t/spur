---
phase: "33"
slug: "interfaces-and-parity"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: false
wave_0_complete: true
created: "2026-10-27"
---

# Phase 33 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `33-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-xdist (8 workers) + pytest-cov (floor 96); Playwright 1.63.0 for the browser test |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (`--strict-markers --strict-config`, `filterwarnings = error`) |
| **Quick run command** | `.venv/bin/python -m pytest tests/test_seam.py tests/test_shaft_params.py tests/test_shaft_interfaces.py --no-cov -n0 -q` |
| **Heavy per-file runs** | `make test PYTEST_ARGS="tests/test_api.py tests/test_cli.py --no-cov -n0 -q"`; browser: `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"` |
| **Full suite command** | `make verify` |
| **Estimated runtime** | quick: seconds; full: ~235 s at Phase 32 close (`2644 passed in 233.83s`); take a fresh baseline before the first code commit |

---

## Sampling Rate

- **After every task commit:** Run the quick command plus the touched test file; `make verify.fast` must stay under L36's 30 s.
- **After every plan wave:** Run `make verify.fast`, plus the browser file when `app.js` or `tests/test_browser.py` moved.
- **Before `/gsd-verify-work`:** `make verify` green with the result line recorded in `bench/RESULTS.md` against the phase-start baseline; `make gear.unchanged` green; `git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml` empty.
- **Max feedback latency:** 30 seconds (commit slice).

---

## Per-Task Verification Map

Filled by the planner per task. Requirement-level map (from research):

| Requirement | Behavior | Test Type | Automated Command | File Exists |
|-------------|----------|-----------|-------------------|-------------|
| REQ-shaft-api | schema/info/stl/step answer; `dims` key; gear `/api/schema` byte-equal; route table additions only; invalid shaft 422 naming the field | unit + integration | `pytest tests/test_shaft_interfaces.py tests/test_seam.py tests/test_api.py -k shaft` | ✅ |
| REQ-shaft-cli | `spur shaft` numbers equal the API; exit 2 on refusal; README commands run | integration | `pytest tests/test_cli.py -k shaft` | ✅ |
| REQ-designation-input | designation alone builds; + spline field = 422 naming both; + solid field fine; bad token named; infeasible designation 422 not 500 | unit | `pytest tests/test_shaft_interfaces.py -k designation` | ✅ (repeated `designation` key: manual-only, see below) |
| REQ-shaft-web | switch both ways, preview, rows from schema, designation row, STL+STEP, `part=shaft` round trip, gear link no `part`, bad `part` refused and the form dimmed while it stands (33-10); under 820 px the switch above the canvas (33-10); `.btn.primary` text ≥ 4.5:1 in both themes (33-10) | browser + static | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"` (steps `bad part refused`, `narrow layout`, `primary button contrast`); `pytest tests/test_api.py -k "shareable or every_key"` | ✅ |
| REQ-shaft-parity | web = API = CLI per number and download name over the fixed set; red once on a perturbed number | browser + integration | browser step `parity: web and API` + `pytest tests/test_shaft_parity.py` | ✅ |
| REQ-wr02-fixed | no token blank-in-box and 200-at-API; Chromium re-probe equals the table; 37-input browser sweep; golden sweep still sends the 44 pinned queries | unit + browser | `pytest tests/test_number_as_written.py tests/test_shaft_interfaces.py -k as_written`; browser steps `number box tokens`, `as-written sweep`, `shaft as-written sweep` | ⚠️ partial — `0-0` gap, manual-only + debt |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `tests/shaft_parity.py` — fixed shaft set (default; `reference_d=30 module=2 teeth=14`; an odd-count shaft such as `26x1.25x19`; `shank_length=0`) and the three readers
- [x] `tests/test_shaft_interfaces.py` — light TestClient tests
- [x] perturbation test, recorded under "Seen red once (Phase 33)" in `bench/RESULTS.md`
- [x] committed Chromium token table and its two walkers
- [x] `tests/test_api.py` amendment for the `hashchange` token (new Lxx) and the `dims` test
- [x] `tests/test_cli.py` amendment for the `shaft` help partition and README commands

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Viewer framing for a long shaft along Z | REQ-shaft-web | Visual judgement (Claude's Discretion in CONTEXT) | Open `#part=shaft&shank_length=<max>`, confirm the whole part is framed |
| An int field refuses `0-0` / `00-0` (blank in the box) | REQ-wr02-fixed | Deferred by the human 2026-10-28: closing it changes L49's rule; harmless today because `spoke_count` and `hole_count` default to 0 (33-REVIEW IN-01) | `curl '…/api/info?spoke_count=0-0'` answers 200 today; tracked in `docs/tech_debt/active/2026-10-28-int-fields-accept-a-blanked-zero-minus-zero-token.md` |
| A repeated `designation` key builds the last value | REQ-designation-input | Deferred by the human 2026-10-28 (33-REVIEW IN-06); checked by hand in 33-04, no test pins it | `/api/shaft/info?designation=nonsense&designation=W%2030x2x14x8f` answers 200 with the last value; the reverse order is a 422 at `designation` |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** partial — validated 2026-10-28 by /gsd-validate-phase 33; `nyquist_compliant` stays false while the two manual-only rows above stand

## Validation Audit 2026-10-28

| Metric | Count |
|---|---|
| Gaps found | 2 |
| Resolved | 0 |
| Escalated | 2 |

## Validation Audit 2026-10-29

| Metric | Count |
|---|---|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
