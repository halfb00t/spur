---
phase: "24"
slug: "bore-shape-selector"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-12"
---

# Phase 24 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `/api/schema` → the DOM | the selector's title, option labels and the pending note become text in the page | model-declared strings; no user input |
| the select → the form's fields | a pick writes into flat fields that the page then sends and puts in the shareable hash | the string `0`, or a stashed string the user typed |
| shared link (URL fragment) → form | untrusted values load into the fields the select derives from, including negatives | query-string numbers, validated by `GearParams` on the server |
| the model's selector list → what the form claims | the page shows a bore shape the model says the fields make; a wrong option makes the form claim a shape the part does not have | schema metadata, proved against `derive()` |
| every page the scenario opens → `/api/*` | the form's requests leave the page; a key the API does not define is parameter pollution the server would ignore silently | request parameter names |
| the browser proof → the committed pin | the golden request pin is the record of what each shared link sends; regenerating it to green would erase the proof | `tests/regression/golden_requests.json`, `tests/regression/pre_v0_2.json` |
| a measurement → a recorded figure | a reading becomes a number Phase 25 cites when it re-sets the bar; a mis-copied or estimated one is a false claim (L08) | timings in `bench/RESULTS.md` |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-24-01 | Tampering | the selector's title, labels and the pending note written into the page (`buildSelectors`, `pend`, `deriveSelectors`) | low | mitigate | `app.js` has no `innerHTML`/`insertAdjacentHTML`/`outerHTML` write (0 matches); the selectors (L42) section uses `textContent` (8 uses) and `new Option(` (2 uses) only; `writes_a_field_shut` in `tests/test_api.py` still pins the absence of markup writes | closed |
| T-24-02 | Tampering | the selector's own state reaching a request or the hash (parameter pollution; L05) | medium | mitigate | `fields.set(` occurs once in `app.js`; the selectors section sets no `name` on the select; `tests/test_api.py` asserts the emitted `selectors` and that `/openapi.json` carries none; 24-03's recorder on all seven pages (T-24-09) saw no foreign key after any of the 14 steps | closed |
| T-24-03 | Tampering | a pick writing a field the user did not choose or a value nobody typed (the keyway, an inert bore field, a starter flat) | medium | mitigate | plan then write, `String(value)` only, in `app.js`; `tests/test_selector.py::test_each_pick_from_each_state_writes_the_minimum_and_matches_the_typed_path` checks the changed-field set against `GearParams`; the browser step's 16 picks from 4 states match the mirror (24-03 SUMMARY); the restore and stop breaks seen red (`investigation/24-01-restore-red.log`, `24-01-stop-red.log`) | closed |
| T-24-04 | Denial of service | an option the page cannot read, or a negative value, throwing out of `readHash()` and skipping `update()` (the WR-01 class) | low | mitigate | three `catch` sites in the selectors section; the catch removed was seen red (`investigation/24-01-catch-red.log`); the twin selector loads blank (`24-01-twin-red.log` for the first-match regression); the `unknown relation op` browser step tampers the selector's op and the part still builds | closed |
| T-24-05 | Information disclosure | the stash holding values the user typed | low | accept | memory only: `app.js` has no `localStorage`/`sessionStorage`/`indexedDB`/`document.cookie` use (0 matches); `stash.clear();` runs on Reset; never in the URL or a request (T-24-02, T-24-09); a local single-user page — see R-24-01 | closed |
| T-24-06 | Tampering | a regression fixture or the golden request pin moved inside a feature commit | low | mitigate | `git diff --exit-code 07cba05..HEAD -- tests/regression/pre_v0_2.json tests/regression/golden_requests.json` is empty across the whole phase | closed |
| T-24-07 | Spoofing | a selector option whose label disagrees with the part `derive()` describes, or two options claiming one triple | medium | mitigate | `tests/test_selector.py::test_exactly_one_option_holds_on_every_valid_cell_and_the_default_is_d_flat` (35 cells) and the round trip's `derive()` class per label, both in the commit slice; a wrong field, a wrong op and an overlap on the real model each seen red (`investigation/24-02-wrong-field-red.log`, `24-02-wrong-op-red.log`, `24-02-overlap-red.log`) | closed |
| T-24-08 | Tampering | a deliberately wrong option left in `src/spur/params.py` after the evidence runs | low | mitigate | `git diff --exit-code 470b78a HEAD -- src/spur/params.py` is empty; commit `505999e` adds `tests/test_selector.py` and nothing else | closed |
| T-24-09 | Tampering | a selector or other non-`GearParams` key sent from a page the assertion does not watch | medium | mitigate | `record_api(browser.new_page(), seen)` at all 7 `browser.new_page()` sites in `tests/test_browser.py`; `no_foreign_key` attached to all 14 steps and run once at the end; the recorder saw 260 `/api` requests, 140 `api/info`, more than the sweep's 44 (24-03 SUMMARY) | closed |
| T-24-10 | Tampering | `tests/regression/golden_requests.json` regenerated to absorb a moved query | low | mitigate | `make golden.regen` run as a byte-identity proof (`investigation/24-03-golden-regen.log`); the same empty diff as T-24-06 across both 24-03 commits | closed |
| T-24-11 | Repudiation | `bench/RESULTS.md` readings recorded from estimates, another host or a dirty tree | low | mitigate | 31 kept logs committed in `c0675b9`; the `## Bore-shape selector (Phase 24)` section and its `### Seen red once (Phase 24)` table present; every table figure checked against its log by the plan's script (24-04 SUMMARY); host state recorded | closed |
| T-24-12 | Tampering | a wait, timeout or bar moved toward a pass | low | mitigate | `c0675b9` holds no `src/` or `tests/` file; no reading was over its limit, so the plan's `checkpoint:decision` never fired (24-04 SUMMARY) | closed |
| T-24-SC | Tampering | package installs | low | accept | no package added in any of the four plans; `requirements.txt`, `pyproject.toml` and `docker/` unchanged since `07cba05` — see R-24-02 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-24-01 | T-24-05 | The stash lives only in page memory, is cleared by Reset and by a reload, and never reaches the URL or a request; the page is a local single-user tool with no other reader (24-01 plan register, disposition `accept`) | planner, at plan time (24-01) | 2026-10-12 |
| R-24-02 | T-24-SC | No package is installed by this phase; the pinned closure does not move, so there is nothing to vet (Phase 23 precedent R-23-01) | secure-phase orchestrator | 2026-10-12 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-12 | 13 | 13 | 0 | secure-phase orchestrator (grep-depth L1; short-circuit — register authored at plan time in all four plans, no threat ≥ high, every mitigation found in the tree, a commit or a kept log) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-12
