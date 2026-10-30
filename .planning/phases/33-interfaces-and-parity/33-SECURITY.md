---
phase: "33"
slug: "interfaces-and-parity"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-28"
---

# Phase 33 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.
> Built from the `<threat_model>` blocks of 33-01..33-09-PLAN.md (register authored at plan time)
> and each SUMMARY's `## Threat Flags` (all "None" beyond the register). ASVS L1: mitigations
> confirmed present by grep at HEAD `ccac029`; `make verify` at HEAD passed (2778 tests).

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| URL query → API | `/api/info`, `/api/model.*`, `/api/shaft/*` read untrusted query tokens | numbers, `fit`, `designation` (no secrets) |
| URL hash → page | `app.js` reads `part` and field values from a shared link | part name, field values, echoed into refusal text |
| argv → CLI | `spur shaft info/export` flags | same parameter set as the API |
| CAD kernel → printed numbers | `build_shaft` result checked before any number or file is served | geometry the user cuts metal to (L08) |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-33-01 | Repudiation | gate delta with no log | medium | mitigate | baseline logs committed (33-01-verify.log) | closed |
| T-33-02 | Tampering | server rule from HTML spec, not the browser | high | mitigate | 37-input Chromium probe, human-picked rule (A1), table re-probed in the gate | closed |
| T-33-03 | Tampering | chamfer printed but not cut | high | mitigate | end-face read-back in `_guard_volume` (shaft_model.py), test seen red | closed |
| T-33-04 | Denial of Service | face scan cost on the heaviest shaft | low | mitigate | build time logged (2.86 s); 33-09 contention run | closed |
| T-33-05 | Tampering | blanked link token builds a non-default gear | high | mitigate | `_numbers_as_written` on gear routes (app.py); walker + browser sweep. Residual: `0-0` on int fields reaches 200 but builds the default part — tracked as debt `2026-10-28-int-fields-accept-a-blanked-zero-minus-zero-token.md` | closed |
| T-33-06 | Information Disclosure / XSS | reflected token in 422 | medium | mitigate | `json.dumps` quoting (app.py); `textContent` only; 0 `innerHTML`/`insertAdjacentHTML` in app.js | closed |
| T-33-07 | Denial of Service | very long token echoed | low | accept | see Accepted Risks Log | closed |
| T-33-08 | Tampering | designation beside a spline field picks a winner | high | mitigate | conflict on key presence (`designation_clash`), `resolve_shaft` refuses; tests per key | closed |
| T-33-09 | Denial of Service | regex cost on long designation | low | mitigate | `DESIGNATION_MAX_LENGTH` (64) before any regex; tested at and above cap | closed |
| T-33-10 | Denial of Service | heavy shaft builds fill the queue | medium | mitigate | shared `BUILD_QUEUE` via `_serve_model`; `503 busy` test; 33-09: 4×200, 6×`503 busy`, no timeout | closed |
| T-33-11 | Information Disclosure | infeasible designation escapes as 500 | medium | mitigate | `_shaft` maps `ValidationError`/`DesignationError` to 422; fuzzed (1809 strings, 200/422 only) | closed |
| T-33-12 | Tampering | gear contract drift | high | mitigate | `make gear.unchanged`, seam pins, route-prefix pin — all green at HEAD | closed |
| T-33-13 | Tampering | CLI prints/writes what the API refuses | high | mitigate | one validation path (`resolve_shaft`, `ShaftParams`); parity test; exit 2, no file | closed |
| T-33-14 | Elevation of Privilege | CLI imports web policy | low | mitigate | import contracts (`Contracts: 10 kept, 0 broken.`) | closed |
| T-33-15 | Tampering | hash `part` indexes `PARTS` prototype keys | medium | mitigate | `partOf` compares literals; browser case per prototype key | closed |
| T-33-16 | Information Disclosure / XSS | schema labels/rows into DOM | medium | mitigate | `textContent`/`setAttribute` only; guard green | closed |
| T-33-17 | Tampering | one part's values sent with the other | high | mitigate | `buildForm(which)` clears maps and mate box; `no_foreign_key` recorder | closed |
| T-33-18 | Tampering | page shows a shaft number other than the API's | high | mitigate | browser `parity: web and API` step, `fmt` pin, two recorded reds | closed |
| T-33-19 | Information Disclosure / XSS | labels/designation into the table | low | mitigate | `textContent` only; guard green | closed |
| T-33-20 | Tampering | blanked shaft link token builds a non-default shaft | high | mitigate | shaft routes carry the as-written pre-check; `shaft as-written sweep`; table re-read on shaft inputs | closed |
| T-33-21 | Denial of Service | heavy shafts under contention exceed 30 s | medium | mitigate | measured at shipping defaults: slowest 200 at 10.16 s, no `503 timeout`/`pool_broken`/500 | closed |
| T-33-22 | Repudiation | figure with no log | medium | mitigate | every figure copied from a committed log; close checks logged | closed |
| T-33-23 | Information Disclosure / XSS | echoed `part` in refusal | medium | mitigate | `JSON.stringify` + `textContent` via `showMessages` | closed |
| T-33-24 | Tampering | edit/Reset under unknown `part` builds | medium | mitigate | `update()` returns while `refused`; `bad part refused` step counts requests | closed |
| T-33-25 | Repudiation | criterion wording rewritten to match shipped | medium | mitigate | one `Reading (C1…)` sentence beside ROADMAP criterion 4 and `REQ-wr02-fixed`; approved words unchanged | closed |
| T-33-26 | Tampering | `body[data-refused]` outlives the refusal | medium | mitigate | 33-10: attribute written beside each of the 3 `refused` assignments only (app.js:199, 262, 278); `bad part refused` asserts the live look after a radio click and after a valid link; `writes_a_field_shut` green | closed |
| T-33-SC | Tampering | package installs | low | accept | see Accepted Risks Log | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-33-01 | T-33-07 | request line bounded by uvicorn/h11; pydantic's own 422 already echoes `input`; nothing stored | plan 33-03 threat model | 2026-10-27 |
| AR-33-02 | T-33-SC | no package installed this phase; `requirements.txt` byte-equal to `6800769` | plan threat models 33-01..33-09 | 2026-10-27 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-28 | 26 | 26 | 0 | /gsd-secure-phase 33 (orchestrator, ASVS L1 grep) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-28

## Security Audit 2026-10-29

| Metric | Count |
|---|---|
| Threats found | 1 |
| Closed | 1 |
| Open | 0 |
