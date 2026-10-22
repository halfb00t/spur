---
phase: "28"
slug: "refuse-the-bad-link"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-22"
---

# Phase 28 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| shared link (URL fragment) -> `app.js` | the fragment is attacker-controllable text that `readHash()` now keeps and forwards instead of dropping | untrusted query tokens |
| `app.js` -> `/api/info` | the server is the only validator (pydantic, unchanged); the client adds no validation | form parameters, percent-encoded |
| 422 body -> the page | the server's `msg` is rendered as text; its `input` echo is never rendered | validation messages |
| `/api/info` document -> the dimensions table | a label that names the wrong root misdescribes a number someone measures (L08) | derived dimensions |
| `/api/schema` -> `buildForm()` | the schema is self-served; a malformed selector is a build-time defect, not user input | form schema |
| `derive()` -> `/api/info`, the CLI, the form | a printed number is read as a dimension someone cuts metal to (L08) | derived dimensions |
| a fixture regen -> `tests/regression/` | the L05 fixture changes only in its own commit stating what moved (D-03, D-13) | regression records |
| a comment or docstring -> the next reader | a wrong contract text steers the next change; comment-only commits must not move behaviour | source text |
| a disposition cell -> the milestone audit | the audit reads the cell as evidence; an unbacked cell hides an open defect | review ledgers |
| the human's answer -> `28-CONTEXT.md` | a disposition the human did not give, written as theirs, would be repudiable | D-19..D-23 |
| `tests/test_api.py` text pins -> `app.js` | a pin loosened to get green would hide a regression of L44's mechanism (SC2) | test pins |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-28-01 | Tampering | `readHash()`/`gearQuery()` carrying a crafted token (DOM XSS) | high | mitigate | no `innerHTML`/`insertAdjacentHTML`/`outerHTML`/`document.write`/`eval`/`new Function` in `src/spur/static/app.js`; token reaches only `input.value`, `URLSearchParams` and `history.replaceState`; messages via `textContent`; `writes_a_field_shut` (`tests/test_api.py:351-393`) passes | closed |
| T-28-02 | Tampering | a link silently rebuilt as the default part | high | mitigate | `refuse()`, `readHash`, `gearQuery` and the mate fallback send the raw token; `bad link refused` / `cleared` / `on a fresh page` steps (`tests/test_browser.py:1873-2059`) pass; red runs kept (`investigation/28-01-red-*.log`) | closed |
| T-28-03 | Information disclosure | the 422 body's `input` echo | low | mitigate | `problems()` renders `d.msg` only; the `_expected_422` oracle builds from `msg`; a 20 KiB token's echo was not rendered | closed |
| T-28-04 | Denial of service | a multi-KiB token sent in the query | low | accept | see AR-28-01 | closed |
| T-28-05 | Repudiation | a pin deleted or allow-listed to get green | medium | mitigate | `cb93d4e` removed no line; later tuple edits `3224ec7`, `aede0fd`, `cced006` add or lengthen pins only; field-name rule and both write guards untouched | closed |
| T-28-06 | Spoofing | a token the API accepts built while its box shows blank | medium | mitigate | fragment written from the same `infoQ` that carries the token; L44 rows; `blank, unknown and accepted tokens` step pins `face_width=5.`; the visibility gap is WR-02, deferred (D-20) to `docs/tech_debt/active/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md` | closed |
| T-28-07 | Spoofing | the `root_fillet` row's label | medium | mitigate | `app.js:30` keys on `d.root_form_d`, set by `calc.py:1292` only when a curve was built; `root_fillet label` step passes; red run `28-02-red-label.log` | closed |
| T-28-08 | Tampering | the reworded stash comment adding a value write | low | mitigate | `282fa63` changes `//` lines only; selectors guard counts exactly one write (`tests/test_api.py:424`) | closed |
| T-28-09 | Repudiation | the new bootstrap wording hiding which stage failed | low | accept | see AR-28-02 | closed |
| T-28-10 | Tampering | a "comment-only" commit that changes code | medium | mitigate | AST recomputed: `87d98ab` identical, `9092802` identical with docstrings stripped, `54f3b53`/`282fa63` diffs are comment lines | closed |
| T-28-11 | Repudiation | a docstring that states a behaviour the code does not have | low | mitigate | `root_mode` probed against the new docstring for radial and trochoid with NaN, -1 and inf | closed |
| T-28-12 | Repudiation | a `fixed` cell whose sha does not exist, or a `deferred` cell whose path does not | medium | mitigate | audit found Phase 10 `IN-02` still `deferred` to a path `6497c28` moved to `resolved/`; fixed in `8b20072`; 28-04 ledger check prints `ledger closed: 41 rows read` | closed |
| T-28-13 | Tampering | a vacuous-pass finding closed as `skipped` | medium | mitigate | 28-04 ledger check requires `24 CX-05`, `23 IN-08`, `23 IN-11`, `21 IN-03`, `21 IN-04` to read `fixed`; passes | closed |
| T-28-14 | Repudiation | a hand triage mistaken for the gate's own write | low | mitigate | ledger check enforces the `# triage by hand; the gate's own stamp was ...` shape; passes | closed |
| T-28-15 | Repudiation | the five dispositions D-19..D-23 | high | mitigate | `28-05-PLAN.md:111` is `gate="blocking-human"` with no `auto_select`; `28-CONTEXT.md` has one line each; the human's words are verbatim in `28-05-SUMMARY.md`; `ad28848` touches `28-CONTEXT.md` only | closed |
| T-28-16 | Tampering | a deferred item's revisit trigger | medium | mitigate | `docs/tech_debt/INDEX.md:33-34` triggers are events (an edit of a named function, or a report) | closed |
| T-28-17 | Tampering | `tip_chamfer_effective` moving a pinned record silently | high | mitigate | `git diff --exit-code v0.5 -- tests/regression/` exits 0; the 44-record derive replay passes inside `make verify` | closed |
| T-28-18 | Repudiation | a regen's output discarded with no evidence | medium | mitigate | `investigation/28-06-fixture-check.log` tracked, its last line quoted in L45 and in `6497c28`; the fixture equals HEAD and `v0.5` (the EXIT trap itself was not re-observed) | closed |
| T-28-19 | Tampering | an Lxx written without the human's pick | high | mitigate | L45 cites D-21 ("WR-03 fix"); D-21 recorded in `ad28848` before `6497c28` wrote L45 | closed |
| T-28-20 | Tampering | `tests/test_api.py`'s `app.js` pins | high | mitigate | tokens only added; `aede0fd`'s replacement contains the old assignment and tail, red run `28-07-red-readhash-pin.log`; D-22 records the reading | closed |
| T-28-21 | Spoofing | the accepted-token notice passing as the server's text | medium | mitigate | D-20 is `defer`, so no page-written notice exists; `problems()`, `fail()` and `showMessages` untouched | closed |
| T-28-22 | Repudiation | a new browser case or pin that passes vacuously | medium | mitigate | `bench/RESULTS.md` "Seen red once (Phase 28)" has a row per new case or pin; all 12 investigation logs tracked | closed |
| T-28-23 | Tampering | a selector pick that leaves the request at odds with the visible box (WR-01) | medium | mitigate | `write()` clears `rejected` (`app.js:425`), as do the input, mate and Reset handlers; `bad link cleared` asserts `bore_d=0` and a green build | closed |
| T-28-24 | Repudiation | a ledger cell not backed by the tree, or not what the human chose | medium | mitigate | each `28-REVIEW-DISPOSITION.md` row matches its D line and leads with a resolving sha (`3224ec7`, `6497c28`, `aede0fd`, `2368718`; IN-03/IN-04 via `cced006`, `6ff2d55`) | closed |
| T-28-25 | Tampering | the IN-02 re-wrap changing a word of `web-ui.md` | low | mitigate | `2368718` touches `docs/architecture/web-ui.md` only; word lists identical (947 each) | closed |
| T-28-26 | Repudiation | a hand triage mistaken for the review gate's own write | low | mitigate | `e33d2f6` keeps the hand stamp shape; later stamps in `2653eb9`, `e6480cb` are gate writes | closed |
| T-28-SC | Tampering | npm/pip/cargo installs | low | accept | see AR-28-03 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-28-01 | T-28-04 | no client length check (L02, RESEARCH Pitfall 9); `problems()` falls to its `catch` (`<status> <text>`) on a non-JSON error; measured locally: 4 KiB and 20 KiB tokens both returned a JSON 422 | plan 28-01 threat model | 2026-10-22 |
| AR-28-02 | T-28-09 | the message still carries `err.message` (status text or the selector's own error); the old prefix named a fetch that had succeeded; `form build error` step pins the wording | plan 28-02 threat model | 2026-10-22 |
| AR-28-03 | T-28-SC | Phase 28 installs no package (RESEARCH: "Installation: none"); `main..HEAD` touches no `Dockerfile`, `pyproject.toml`, `requirements.txt`, `web/package*.json` or vendored bundle | plans 28-01..28-08 threat models | 2026-10-22 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-22 | 27 | 27 | 0 | secure-phase (gsd-security-auditor, ASVS L1; T-28-12 closed by `8b20072` on the human's pick) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-22
