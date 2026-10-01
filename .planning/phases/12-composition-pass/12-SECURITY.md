---
phase: "12"
slug: "composition-pass"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-30"
verified: "2026-09-30"
audited_at_head: "90c1150"
---

# Phase 12 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.
> Register authored at plan time (18 threats across 12-01 … 12-09, every disposition
> `mitigate` except T-12-14 `accept`, plus one `T-12-SC` package-install row per plan, all
> `accept`); verified at L1 grep depth after execution — every mitigation is present in the
> implementation or its record, so `threats_open: 0` and no auditor was spawned
> (secure-phase § 3 short-circuit).

---

## Trust Boundaries

Phase 12 adds no code path a user reaches; it composes, measures and records what Phases
7–11 shipped. The boundaries it touches:

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| query string / CLI flags / URL hash → `GearParams` | Untrusted numbers become geometry; the one bound this phase moved is `spoke_count` `le` 40 → 32 (`src/spur/params.py:118`), from a measured probe; the form's `readHash()` only reads names already in `fields` (`src/spur/static/app.js:94`) | floats/ints, mm |
| `GearParams` → kernel | Only `check()`-accepted sets build, inside a worker under `SPUR_BUILD_TIMEOUT` (`src/spur/app.py:146`); this phase measured the heaviest composed sets against that timeout | validated parameter sets |
| `calc` → user, on both interfaces | The composed document is byte-identical on `spur info` and `/api/info` (`tests/test_cli.py:161`); every refusal reads the same as a 422 and as exit 2 (`tests/test_cli.py:405`) | numbers someone cuts metal to (L08); refusal sentences |
| kernel → printed part | Each composed solid is read back — face, edge, volume and TORUS counts pinned (`tests/test_model.py:1474`, `tests/test_model.py:1528`) | topology counts, volumes |
| sweep files → runner → record | `bench/sweeps/composed.json` (18 rows) and `bench/sweeps/spoke_cutout.json` are hard-coded developer-host sets; `bench/build_time.py` times every row and reads each fine STL's size from its own header | parameter sets; bytes and triangle counts |
| measurement → published bound | The probe's number became `spoke_count` `le` 32; the export-cost table kept `_GZIP_LEVEL = 1` (`src/spur/app.py:205`) | measured seconds → one bound, one constant |
| records → the next reader | L31, three `bench/RESULTS.md` sections, `docs/architecture/cli.md`'s exit contract, the README's composed example and three resolved debt files are what v0.3 plans from | static prose, executed CLI examples |
| planning docs → phase verifier | The verifier grades against ROADMAP SC1–SC5 as amended by 12-01 | requirement text |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-12-01 | Tampering | ROADMAP.md written outside the tooling | low | mitigate | 12-01 Task 3's commit `ed8910b` touches exactly `.planning/ROADMAP.md`, `.planning/STATE.md` and the plan's SUMMARY (`git show --name-only ed8910b`); written through edit-phase's write step with the milestone-scope check; Task 1 built the diff without writing (`git diff --quiet -- .planning/ROADMAP.md` in the plan's own verify) | closed |
| T-12-02 | Repudiation | An unrecorded criteria change or conflict answer | low | mitigate | One Roadmap Evolution line in STATE.md (`.planning/STATE.md:345`, "per 12-CONTEXT.md D-06/D-15"); the human's SC3/SC5 wording and both evidence-conflict answers recorded verbatim in 12-01-SUMMARY.md | closed |
| T-12-03 | Denial of service | A composed link the schema accepts builds past 30 s and is killed: a 503 for a link the tool called valid | high | mitigate | Every cutout's heaviest row composed with the tip chamfer, recess and heaviest bore at both modules was measured (18 rows, RESULTS § "Composed build and export time (Phase 12)"); over-budget rows went to 12-03's D-03 checkpoint; after `lower-le: spoke_count 32` the full re-run has every row inside 30 s, heaviest 29.42 s (§ "Re-run after the gate"); the sweep pins the design (`tests/test_bench.py:385`) | closed |
| T-12-04 | Tampering | An over-budget or loaded row dropped or re-run until green, hiding the risk | high | mitigate | Four runs stand in the record with their load readings (§ "Run 1" … "Run 4", `bench/RESULTS.md:56`–`210`), each appended, none overwritten; the runner times every row before deciding its exit code (`bench/build_time.py`); the over-budget rows and the decision sit beneath them in "### Gate", "### Gate probe", "### Gate decision" | closed |
| T-12-05 | Tampering | A truncated or ASCII STL yields a plausible triangle count and picks the wrong row for 12-04 | medium | mitigate | `stl_size()` raises when the length is not `84 + 50 * n` for the header's own count (`bench/build_time.py:89`–`95`); `tests/test_bench.py:114` (`test_an_stl_whose_length_disagrees_with_its_header_is_refused`) and `:106` pin it | closed |
| T-12-06 | Denial of service | A limit changed without re-measuring leaves a composed link over the timeout, or a `le` lowered past what was measured refuses links that built | high | mitigate | The probe measured `spoke_count` 30–35 on a quiet host: 32 inside (29.41 s), 33 over (30.11 s) (§ "Gate probe"); `le` set to the largest measured-inside count (`src/spur/params.py:118`, comment cites the section); the change re-run across all 18 rows (§ "Re-run after the gate"); `tests/test_calc.py:1073` and the sweep pins (`tests/test_bench.py:309`, `:385`) hold the bound | closed |
| T-12-07 | Repudiation | A debt closed without the number or the decision, so nobody can tell later why the margin was accepted | low | mitigate | Both build-timeout debts carry `Resolved in: 89304e2` and a Resolution section citing the composed number and the decision (`docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md:6`, `docs/tech_debt/resolved/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md:6`); INDEX rows moved in the same commit | closed |
| T-12-08 | Denial of service | A higher gzip level adopted on bytes alone raises CPU per download under concurrency | medium | mitigate | L19's rule carries the ten-concurrent wall clause (≤ 1.5×, `bench/export_cost.py:21`); the rule is tested at both bars (`tests/test_bench.py:493`, `:505`, `:526`); on the heaviest topology it kept level 1 (`src/spur/app.py:205`, RESULTS § "Export cost on the heaviest v0.2 topology (Phase 12)") | closed |
| T-12-09 | Tampering | The wrong row re-measured (by inspection), so "the heaviest topology" is a guess | medium | mitigate | The label comes from the runner's `**Largest fine STL:**` line — a number (`tests/test_bench.py:123`); `--set` must match a sweep label exactly or `_find_set` raises `SystemExit(2)` (`bench/export_cost.py:155`–`163`); the same 17,306,084-byte row is named in both RESULTS sections | closed |
| T-12-10 | Tampering | A refusal's sentence or fields drift when another family is on, misleading the user about what to change | medium | mitigate | 138 calc rows pin every refusal's `check()` field tuple and sentence with each other family on; the 18 two-refusal rows and 6 datum-shift rows are explained and pinned (`tests/test_calc.py:1432`) | closed |
| T-12-11 | Tampering | A valid composition silently prints a missing or extra number (L08) | medium | mitigate | 96 tier-1 rows pin the exact non-null `DerivedDimensions` field set and warnings per combination against written-out expectations in `tests/composition.py`, never computed from `derive()` (`tests/test_calc.py:1331`) | closed |
| T-12-12 | Tampering | A feature silently vanishes or changes on a composed solid while `derive()` still prints its number | high | mitigate | Each of 12 composed rows re-runs 10-03's tip proof and 11-08's cutout proof unchanged on the one solid, plus 3 single-sided-recess rows with the fillet-survival proof; face, edge, volume and TORUS deltas measured on the pinned kernel and pinned as literals (`tests/test_model.py:1474`, `:1528`; D-09) | closed |
| T-12-13 | Tampering | The API and the CLI print different numbers or errors for one link, or a field is reachable on one interface only | medium | mitigate | One model-driven walk of `GearParams.model_fields` across `/api/schema`, the form groups and `spur info --help` (`tests/test_cli.py:187`); the composed document byte-identical on both interfaces (`tests/test_cli.py:161`); 23 refusals routed identically to 422 and exit 2 (`tests/test_cli.py:405`) | closed |
| T-12-14 | Tampering | A crafted hash sets names the form does not know | low | accept | `readHash()` iterates `fields` (the schema's properties) and reads the hash by those names only (`src/spur/static/app.js:94`–`98`); the API validates every value; the static test pins that loop (`tests/test_api.py:142`) — see R-12-02 | closed |
| T-12-15 | Tampering | A script branching on `$? == 2` for a bad extension, as the doc told it, takes the wrong branch | medium | mitigate | `docs/architecture/cli.md` "Errors" now states 2 / 1 / 1 (2× "exit 2", 2× "exit 1"; the false single-status claim gone); every status asserted in `tests/test_cli.py`, one by the real process (`tests/test_cli.py:450`); the doc debt resolved in `0deb25a` | closed |
| T-12-16 | Tampering | The gate's cost drifts past D-10's line with nobody deciding it | medium | mitigate | Same-host alternating A1 B1 A2 B2 `make verify` runs against the phase's own start `c9a169d`, load read before each (RESULTS § "Composition pass test cost (Phase 12, D-10)"): delta 28.28 s against the 30.0 s line; the human decided "accept" at 12-09 Task 2, recorded verbatim under "### Gate decision" | closed |
| T-12-17 | Repudiation | L31 carries a number nobody measured | low | mitigate | L31 present once; every number cites a RESULTS section or a SUMMARY sha — the three Phase 12 section titles all appear in the entry (3 grep hits); appended, never edited: `git diff --numstat c9a169d -- docs/architecture/decision_log.md` → 134 added, 0 deleted | closed |
| T-12-18 | Tampering | The A runs rebuild the main venv against the worktree, so later B runs test the old code | medium | mitigate | `make -o "$MAIN/.venv/.installed"` with `PYTHONPATH="$WT/src"`; the import path proven under the worktree before timing; `_editable_impl_spur.pth`'s content identical before and after all four runs (RESULTS § "Host state", `bench/RESULTS.md:1815`–`1818`) | closed |
| T-12-SC | Tampering | npm/pip/cargo installs (one row per plan, 12-01 … 12-09) | low | accept | `git diff c9a169d..HEAD -- pyproject.toml requirements.txt` → empty; `bench/export_cost.py` uses stdlib `gzip`, `resource`, `statistics`, `concurrent.futures` only — see R-12-01 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

Register notes: every row's mitigation is as planned; T-12-03/T-12-06 executed through the
D-02 → D-03 path (four loaded runs, a probe, one bound lowered, one full re-run) rather than
the single-run path the plans sketched. No SUMMARY carries a `## Threat Flags` section — no
executor surfaced a new threat during execution.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-12-01 | T-12-SC | No dependency or lockfile changed in this phase and the one new script imports only the standard library; nothing to verify beyond the diff | orchestrator (audit) | 2026-09-30 |
| R-12-02 | T-12-14 | A hash name the form does not know is ignored by construction (`readHash()` reads by the schema's field names, not by iterating the hash), and every value still passes the API's validation; a crafted hash can at most set known fields to values the server then refuses with a 422 | orchestrator (audit), as planned in 12-07 | 2026-09-30 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-30 | 19 (18 planned + T-12-SC) | 19 | 0 | verify-work orchestrator (secure-phase § 3 short-circuit: register authored at plan time, ASVS L1, grep-depth evidence per row; `make verify` 907 passed at `fed8baf` in the pre-commit hook) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-30
