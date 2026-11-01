---
phase: "34"
slug: "fit-tables-and-tolerance-window"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-31"
---

# Phase 34 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.
> Built from the `<threat_model>` blocks of 34-01..34-17-PLAN.md (register authored at plan time)
> and each SUMMARY's `## Threat Flags` (all "None" or mapped to an existing id). ASVS L1, block_on
> high: gsd-security-auditor confirmed every mitigation present at HEAD `9658ffb` and re-ran the
> threat-bearing tests (113 + 41 + 20 passed). No table value appears here (D-01).

---

## Trust Boundaries

| Boundary | Description | Data Crossing (see the plan's threat model) |
|----------|-------------|---------------|
| the human's licensed copy -> the public repository | any byte rendered or extracted from the PDFs must stay under the ignored `private/` | — |
| a recorded number -> the phase's comparisons | the gate delta rests on the reading taken here | — |
| operator's file -> the process | an operator-supplied JSON document becomes the numbers every client is served; validated once, here | — |
| loader refusal -> logs and stderr | a refusal message may be committed in a red log or pasted into a SUMMARY | — |
| the licensed PDF -> developer-time scripts | text and values extracted from the copy | — |
| script output -> the repository | any file a script writes, any line it prints that a log or SUMMARY may hold | — |
| the loaded tables -> numbers every client is served | a table value becomes a printed dimension someone cuts metal to | — |
| warnings -> every API client | text in `warnings` leaves the host | — |
| operator's environment -> the composition roots | the variable decides which numbers every client is served | — |
| parent process -> spawned build workers | the solid a worker builds must match the numbers the parent printed | — |
| tabulated pin and form-diameter limit -> printed M_Re | a value from the copy decides whether a measurement prints | — |
| printed numbers -> the solid | the downloaded part must be the part the numbers describe | — |
| test harness -> a server child process | a variable passed to one server only | — |
| the licensed copy -> the repository | renders, crops and read values stay under the ignored `private/` | — |
| one read -> another | independence is what makes the zero diff mean anything | — |
| read A -> read B | blindness is what makes the zero diff mean anything | — |
| read B -> read A | blindness is what makes the zero diff mean anything | — |
| the licensed copy -> the repository and the conversation | values live under the ignored `private/` only | — |
| the human's settlement -> both reads | one answer, applied evenly | — |
| the licensed copy -> the public repository | only approved anchors cross, by name | — |
| the real file -> printed numbers | a contradiction found here must reach the human before release | — |
| the real file -> a committed test module | the module reads values from the file, never holds them | — |
| an edge d_B -> a column | the reading decides every fit number for that size | — |
| the phase's work -> the public repository | the last look before the branch is merged | — |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-34-01 | Repudiation | a gate delta taken against a reading with no log | medium | mitigate | Fresh `make verify` on Phase 33's tree (precondition diff against `ddfb3ea`), both logs committed, figures copied not re-rounded; a red run is discarded by name. | closed |
| T-34-02 | Information Disclosure | `git add` or the Docker build context picking up a private file | high | mitigate | `/private/` in .gitignore and `private` in .dockerignore in their own commit before any file exists there; `git check-ignore` proved on three paths. | closed |
| T-34-03 | Information Disclosure | the toolchain log or SUMMARY quoting what the render shows | high | mitigate | The log holds versions, counts, paths and a yes/no only; the render stays in `$MAIN/private/renders/34-01/`; `git status` shows nothing under private/. | closed |
| T-34-04 | Tampering | a mistranscribed cell loading as a number | high | mitigate | Strict schema, `problems()` invariants and the load-time M1 identity, each seen red (Task 2); two reads diffed to zero upstream (34-14). Caveat: 12 refusal lines not each reached by a test (debt `2026-10-31-din5480-tables-loader-refusals-not-reached-by-a-test.md`). | closed |
| T-34-05 | Tampering | NaN or inf making every guard comparison false | high | mitigate | `allow_inf_nan=False` on every float; cases `nan` and `inf` refuse (Task 2; research Pitfall 2 measured strict mode accepting both). | closed |
| T-34-06 | Denial of Service | a wrong path naming a large file | low | mitigate | `MAX_FILE_BYTES` checked before the read; regular files only. | closed |
| T-34-07 | Repudiation | a broken file degrading quietly to null | high | mitigate | `load_file` raises `TablesError`, `active()` caches and re-raises it; the roots turn it into a refusal (34-05). | closed |
| T-34-08 | Information Disclosure | a tracked copy of the table file under any name | high | mitigate | `test_no_tracked_json_file_is_a_table_file` validates every tracked JSON; the ignore test reads both ignore files; both seen red. | closed |
| T-34-09 | Information Disclosure | the fixture or a refusal message carrying a transcribed value | high | mitigate | Fixture: invented or formula values plus named approved anchors only; refusals carry `loc` and `type`, never pydantic's `input_value`. | closed |
| T-34-10 | Information Disclosure | a diff listing or a read-1 log carrying values | high | mitigate | `diff` prints locations unless `--values`; the read-1 log holds counts and keys; the SUMMARY records only `ok` from `check`. | closed |
| T-34-11 | Tampering | the parser silently guessing an ambiguous row (the Table 12 duplicate) | high | mitigate | Keys not printed once on both pages are reported, never joined; tested on invented text; the human settles them (34-14). | closed |
| T-34-12 | Information Disclosure | a read written into a tracked path | high | mitigate | `ensure_ignored` before every write (parser, join, assemble), tested refusing `tests/x.json`. | closed |
| T-34-13 | Tampering | a table file assembled from reads that disagree | high | mitigate | `assemble` refuses unless both diffs have zero lines and `--complete` passes; tested. | closed |
| T-34-14 | Tampering | an off-table size snapped to a nearby row and printed | high | mitigate | Exact float key only (34-02); neighbours test proves off-table numbers equal the no-file document's. | closed |
| T-34-15 | Information Disclosure | the table file's path inside an API warning | medium | mitigate | Warnings name `SPUR_DIN5480_TABLES` only; `test_no_warning_carries_the_table_files_path` over every tier. | closed |
| T-34-16 | Tampering | a fit outside Table 7 printing limits from a neighbouring letter or class | high | mitigate | `Tables.fit` returns None for a missing letter or class; five rows null, solid at nominal, sentence names the file's sets; tested on three fits. | closed |
| T-34-17 | Information Disclosure | Table 7's letters and classes typed as a constant in src/ (transcribed values in code) | medium | mitigate | The fit sentence reads `Tables.letters` and `Tables.tolerance_classes`; the fixture's sets are invented, so the test proves they come from the file. | closed |
| T-34-18 | Repudiation | a set but broken file degrading quietly to null | high | mitigate | `cli.main` and `app.lifespan` refuse with the reason; tested in-process, in a real process and through `TestClient`'s lifespan; seen red. | closed |
| T-34-19 | Tampering | a replaced worker re-reading an edited file and building a different solid from the printed numbers | high | mitigate | `initargs=(self._tables,)` in both constructions; fingerprint test with the variable pointing elsewhere; seen red with `recreate_for`'s initargs removed. | closed |
| T-34-20 | Information Disclosure | the path reaching an API client | low | mitigate | The path appears only in the startup refusal on the operator's stderr; warnings name the variable (34-04's test). | closed |
| T-34-21 | Denial of Service | `uvicorn --workers N` restart-looping on a lifespan failure (research A4, unverified) | low | mitigate | `spur serve` refuses in `main()` before uvicorn starts; the direct-uvicorn path is documented as defence in depth only. | closed |
| T-34-22 | Tampering | a limit measurement printed with its pin touching below the form circle | high | mitigate | Every thickness guarded on its own at the tabulated floor; the per-limit null tested on a variant and seen red; the margin unchanged; 34-15 sweeps the real file. | closed |
| T-34-23 | Tampering | an odd-count M_Re printed where no table confirms it | medium | mitigate | `odd_confirmed=row is not None`; off-table and no-file odd counts tested null with `ODD_Z_UNCONFIRMED`. | closed |
| T-34-24 | Tampering | a solid and its printed thickness naming different shafts | high | mitigate | `build_shaft` reads the printed row; thickness read back from the section on every flank; seen red against the nominal build. | closed |
| T-34-25 | Tampering | a cache serving the other table state's solid or bytes | medium | mitigate | Caches are per process and the tables fixed per process (D-13); tests flip state only through `with_tables`, which clears both caches. | closed |
| T-34-26 | Information Disclosure | the browser step loading the real table file | low | mitigate | The step writes the synthetic fixture to `tmp_path`; `serve()` still strips every inherited `SPUR_*` variable. | closed |
| T-34-27 | Information Disclosure | a value, render or crop reaching a commit, log or SUMMARY | high | mitigate | Renders and the read under `$MAIN/private/`; only the count-only log is committed; the verify checks nothing under private/ is tracked. | closed |
| T-34-28 | Tampering | read 2 copying or recalling read 1, so a shared error diffs to zero | high | mitigate | The plan forbids opening read 1, its log or SUMMARY; the SUMMARY lists every file opened; read 1 is a different method (text layer) that fails differently (D-06). Caveat: one disclosed departure (34-08 opened `34-03-SUMMARY.md`, counts only). | closed |
| T-34-29 | Information Disclosure | a value, render or crop reaching a commit, log or SUMMARY | high | mitigate | Renders and the read under `$MAIN/private/`; only the count-only log is committed; the verify checks nothing under private/ is tracked. | closed |
| T-34-30 | Tampering | read 2 copying or recalling read 1, or guessing the duplicate row, so a shared error diffs to zero | high | mitigate | The plan forbids opening read 1, its log or SUMMARY; the duplicate is left out and listed; the SUMMARY lists every file opened. | closed |
| T-34-31 | Information Disclosure | a value, render or crop reaching a commit, log or SUMMARY | high | mitigate | Renders and the read under `$MAIN/private/`; only the count-only log is committed; the verify checks nothing under private/ is tracked. | closed |
| T-34-32 | Tampering | read 2 copying or recalling read 1, so a shared error diffs to zero | high | mitigate | The plan forbids opening read 1, its log or SUMMARY; the SUMMARY lists every file opened; read 1 is a different method (D-06). | closed |
| T-34-33 | Information Disclosure | a value, render or crop reaching a commit, log or SUMMARY | high | mitigate | Renders and the read under `$MAIN/private/`; only the count-only log is committed; the verify checks nothing under private/ is tracked. | closed |
| T-34-34 | Tampering | read 2 copying or recalling read 1, so a shared error diffs to zero | high | mitigate | The plan forbids opening read 1, its log or SUMMARY; the SUMMARY lists every file opened; read 1 is a different method (D-06). | closed |
| T-34-35 | Information Disclosure | a value, render or crop reaching a commit, log or SUMMARY | high | mitigate | Renders and the read under `$MAIN/private/`; only the count-only log is committed; nothing under private/ is tracked (verify). | closed |
| T-34-36 | Tampering | a nomogram misread (a column, a diagonal) that both reads share or that is edited to pass the example | high | mitigate | Blind reads in separate plans; the page's worked example and the T_G sum as checks against the page, never targets to edit toward; residual mismatches listed for the human (D-08). | closed |
| T-34-37 | Information Disclosure | a value, render or crop reaching a commit, log or SUMMARY | high | mitigate | Renders and the read under `$MAIN/private/`; only the count-only log is committed; nothing under private/ is tracked (verify). | closed |
| T-34-38 | Tampering | a nomogram misread (a column, a diagonal) that both reads share or that is edited to pass the example | high | mitigate | Blind reads in separate plans; the page's worked example and the T_G sum as checks against the page, never targets to edit toward; residual mismatches listed for the human (D-08). Caveat: one disclosed exposure (34-13 git snapshot named a row count). | closed |
| T-34-39 | Information Disclosure | disagreement values in a committed log, the checkpoint message, STATE.md or a SUMMARY | high | mitigate | Values are written to `disagreements.txt` and `settlements.tsv` under the ignored `private/reads/`; the committed log and the checkpoint carry locations and counts; the verify checks nothing under private/ is tracked. | closed |
| T-34-40 | Tampering | a disagreement settled by picking the read that passes a check, or applied to one read only | high | mitigate | The human settles from the page (blocking-human); the script writes the same value into both reads; both diffs must print `0 differences` before assemble. | closed |
| T-34-41 | Tampering | a table file written while a pair differs or incomplete | high | mitigate | Only `make tables.assemble` writes it, and it refuses on any difference or a `--complete` shortfall; the loader's limits stop-and-ask, never edited around. | closed |
| T-34-42 | Information Disclosure | candidate or finding values in the checkpoint message, the sweep log, RESULTS or a SUMMARY | high | mitigate | Values only in `anchor-candidates.txt` and `sweep-findings.txt` under the ignored `private/reads/` (check-ignore in verify); committed files hold counts and locations. | closed |
| T-34-43 | Information Disclosure | a value committed that the human did not approve by name | high | mitigate | blocking-human checkpoint; Task 3 writes only approved names; acceptance cross-checks every committed name against the checkpoint result. | closed |
| T-34-44 | Tampering | a tabulated combination that nulls M_Re where the copy prints M1, or builds a closed tip or overlapping teeth, shipping unnoticed | high | mitigate | Both sweeps over every size and fit or letter, extremes built and read back; every finding answered by the human; 34-16 implements the answers test first. | closed |
| T-34-45 | Information Disclosure | values of the standard typed into the real-file check module | high | mitigate | The module imports the approved anchors and reads all else from the file; acceptance reads it for numeric literals before commit. | closed |
| T-34-46 | Tampering | an edge d_B read into the wrong column, or printed while unconfirmed | high | mitigate | The human's option encoded and pinned both sides on every printed edge of the real file; `edge-unconfirmed` nulls with its own warning (L08). | closed |
| T-34-47 | Information Disclosure | a value of the standard in any file the phase added or changed | high | mitigate | The leak review classifies every number on every added line; any unclassified number is a blocker; nothing under private/ is tracked (checks 1, 2, 15). Caveat: rests on `34-17-close-checks.log`; auditor could not re-run it against `private/`. | closed |
| T-34-48 | Repudiation | a gate cost or a seen-red claim with no log behind it | medium | mitigate | One logged green run, figures copied not re-rounded; every seen-red row names its log; the bar compared as printed. | closed |
| T-34-SC | Tampering | npm/pip/cargo installs | low | accept | Recorded in each of 17 plans (34-01, 34-02, 34-03, 34-04, 34-05, 34-06, 34-07, 34-08, 34-09, 34-10, 34-11, 34-12, 34-13, 34-14, 34-15, 34-16, 34-17); see Accepted Risks Log | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

Per-threat evidence (file:line, test name, log) is in the auditor's verdict for this run; the
mitigation column above is the plan's own text.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-34-01 | T-34-SC (34-01..34-17) | No package installed in this phase; `git diff ddfb3ea HEAD -- requirements.txt pyproject.toml Dockerfile docker` is empty | plan-time threat model, confirmed by gsd-security-auditor | 2026-10-31 |

*Accepted risks do not resurface in future audit runs.*

---

## Tracked Gaps (not counted in threats_open)

- T-34-04: loader refusal lines not each reached by a test — `docs/tech_debt/active/2026-10-31-din5480-tables-loader-refusals-not-reached-by-a-test.md` (Severity: must).

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-31 | 65 | 65 | 0 | gsd-security-auditor (sonnet), ASVS L1 |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-31
