---
phase: "23"
slug: "conditional-form-fields"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-11"
---

# Phase 23 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `/api/schema` → the DOM | schema strings (titles, relation values) become text in the page | model-declared titles and numbers; no user input |
| shared link (URL fragment) → form inputs | untrusted values load into fields, including dimmed ones, and are sent back to the API | query-string numbers, validated by `GearParams` on the server |
| the form's dim state → the user's decision | the page claims a field needs another value; a false claim misleads what the user sets | a boolean per field derived from `enabled_when` |
| a relation on the model → the user's belief about the part | a relation is a claim that a value does nothing (or is refused) in a state | schema metadata, proved against `calc` |
| a `calc` change → the relation set | a new "ignored" rule without its relation leaves a live field the server ignores | warning text ↔ relation map |
| the browser test → the committed golden pin | regen and test share `sweep()`; a careless commit could rewrite the pin | `tests/regression/golden_requests.json` |
| the server's answer → the form's dim state | a 422 or aborted build must not leave a stale dim state | HTTP status → `applyRelations()` |
| a measurement → a recorded figure | a reading becomes a number later phases cite (Phase 25's bar) | timings in `bench/RESULTS.md` |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-23-01 | Tampering | reason text and titles written into the page (`applyRelations`, `need`) | low | mitigate | `reason.textContent = off ?` token present in `app.js`; `app.js` has no `innerHTML`/`insertAdjacentHTML`/`outerHTML` write; `tests/test_api.py` static assertion names them | closed |
| T-23-02 | Spoofing | a dimmed field the server actually uses (a relation `calc` does not back) | medium | mitigate | `hub_d` parity read before declaration (23-01 SUMMARY); `tests/test_relations.py` forward parity for every row (10 tests, commit slice); the value is still sent | closed |
| T-23-03 | Denial of service | a shared link loading a field the user cannot clear | low | mitigate | static guard in `tests/test_api.py` (`.disabled`/`.hidden`/`readOnly` tokens); browser step typed into dimmed `hub_d` and saw the request carry it (`investigation/23-01-browser-green.log`) | closed |
| T-23-04 | Denial of service | an unknown op throws inside `readHash()` | low | mitigate | `when()` types `op` as `Literal["eq", "gt"]` (`src/spur/params.py`), a bad op fails `mypy --strict`; `test_every_relation_is_well_formed_and_emitted_unchanged` pins the vocabulary. Residual: WR-01 fixed in `cea8c54`: the throw is caught per field in `applyRelations()` and surfaced as the field's reason row | closed |
| T-23-05 | Tampering | regression fixture or golden pin moved inside a feature commit | low | mitigate | `git diff c065d6d..HEAD -- src/spur/calc.py tests/regression/pre_v0_2.json tests/regression/golden_requests.json` is empty | closed |
| T-23-06 | Repudiation | a relation `calc` does not back, or an "ignored" rule with no relation | medium | mitigate | forward parity + warning-names check, reverse coverage (`test_every_field_calc_ignores_is_declared`), three meta-red tests; `bore_chamfer` wrong relation seen red once (`investigation/23-02-wrong-relation-red.log`) | closed |
| T-23-07 | Tampering | `calc` or the fixture moved to make a relation true | low | mitigate | same empty diff as T-23-05; feat commit `fb97ba2` touches `params.py`, `test_relations.py`, `test_cli.py` only | closed |
| T-23-08 | Spoofing | a refused field presented as ignored, or vice versa | low | mitigate | `REFUSED` pinned in `tests/test_relations.py` (`test_the_keyway_pair_is_refused_under_a_hex_bore_alone_and_together`); reason wording states only the need; the server's 422/warning stays visible | closed |
| T-23-09 | Tampering | `golden_requests.json` rewritten by the regen inside a feature commit | low | mitigate | regen run as a byte-identity proof (`investigation/23-03-golden-regen.log`, 44 records) with `git diff --exit-code`; file unchanged since Phase 22 | closed |
| T-23-10 | Repudiation | a stale dim state after a 422 flip or Reset | low | mitigate | 422 flips compared with the evaluator; Reset from a flipped and refused state compared with the default set; `readHash` and `#reset` call sites each seen red when `applyRelations()` removed (`investigation/23-03-readhash-red.log`, `23-03-reset-red.log`) | closed |
| T-23-11 | Repudiation | `bench/RESULTS.md` readings from estimates, another host or a dirty tree | low | mitigate | 25 kept logs committed in `f4f9774`; the Task 2 verify script checks every table figure against its log; host state recorded | closed |
| T-23-12 | Tampering | a wait, timeout or bar moved toward a pass | low | mitigate | `f4f9774` holds no `src/` or `tests/` file; `git diff c065d6d..HEAD` shows no `BUILD_WAIT_MS`/debounce value change (new uses of the existing constant only) | closed |
| T-23-SC | Tampering | package installs | low | accept | no package added in any of the four plans; `requirements.txt` and `pyproject.toml` unchanged since Phase 22 (`c065d6d`) | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-23-01 | T-23-SC | No package is installed by this phase (23-RESEARCH Package Legitimacy Audit: none); the pinned closure does not move, so there is nothing to vet | planner, at plan time (all four plans) | 2026-10-11 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-11 | 13 | 13 | 0 | secure-phase orchestrator (grep-depth L1; short-circuit — register authored at plan time, no threat ≥ high, every mitigation found in the tree or a kept log) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-11
