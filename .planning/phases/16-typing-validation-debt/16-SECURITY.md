---
phase: "16"
slug: "typing-validation-debt"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-05"
---

# Phase 16 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Phase 16 adds no endpoint, auth path, schema or package. Its one code change is inside
`src/spur/model.py` (two `isinstance` boundaries replacing five mypy suppressions, proved by
two tests), and `git diff --name-only 085e5a6 HEAD -- src tests` is exactly that file and
`tests/test_model.py`. The attack surface is therefore the type gate (a false claim about
every built part, or a suppression that slips back in), one new error string that reaches
users, and the record: two Nyquist files, a gap ledger, a debt file, an amended closed audit
and L35 — numbers a later reader trusts without re-running anything. Each mitigation below is
a check that was run at HEAD `4a050c9` on 2026-10-05, not taken from a SUMMARY's word.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| cadquery (vendor) → build pipeline | the kernel's wide `Shape` type enters `model.py`; a wrong narrowing would be a false claim about every built part | `cq.Shape` values at three `fillet`/`chamfer` sites and two `.val()` sites |
| `BuildError` → API / CLI user | the new message crosses the existing 422 / exit-1 mapping unchanged (`app.py:430-434`, `cli.py:111`) | one string: a vendor class name inside a fixed sentence |
| working tree → the gate | a suppression under `src/spur/` would leave lines outside the type checker unnoticed | `# type: ignore` markers; `make no-fake-done` is the second block of the gate |
| human-run interactive skill → repository | `/gsd-validate-phase 7` and `8` wrote a file each and committed through the ~64 s hook; the human finished the commits | `07-VALIDATION.md`, `08-VALIDATION.md`, their `nyquist_compliant` values |
| skill-written VALIDATION.md → the project record | those values and gap tables became the audit's, the debt file's and L35's inputs | `status`, `nyquist_compliant`, Manual-Only rows |
| closed milestone record → amendment | an in-place edit of `v0.2-MILESTONE-AUDIT.md` could erase what it said at close | the `nyquist` frontmatter block and its six original rows |
| measurement → decision log | L35 is read as locked fact about where vendor typing stops and what Phases 7 and 8 measured | figures, ten backticked shas, two `nyquist_compliant` values |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-16-01 | Tampering | the gate (`make no-fake-done`, mypy) — a new suppression slips into `src/spur/` | medium | mitigate | `Makefile:74-77` greps `type: ignore` under `src/spur/*.py` and exits 1 on a hit, with the why-comment naming the two `tests/` carriers; `make no-fake-done` exits 0 at HEAD, the same grep at `085e5a6` prints 5 lines (seen red, then green); `strict = true` keeps `warn_unused_ignores`, which refuses a stale one; `4f7e8fe` carries exactly the eight planned paths (16-VERIFICATION truth 12) | closed |
| T-16-02 | Spoofing | `_body` / `_shape_of` — a type claim wrong at runtime (what a cast would allow) | medium | mitigate | `model.py:429` `isinstance(shape, cq.Solid \| cq.Compound)`, `:439` `isinstance(value, cq.Shape)`; `grep -nE 'cast\(\|typing\.cast\|TypeIs\|\bAny\b' src/spur/model.py` prints nothing; the two refusal tests (`tests/test_model.py:250`, `:264`) assert the full message with `==` and read `2 passed` at `a35432d`; the standing enforcement for a future `cast` is mypy strict + review, decided by the human (16-UAT test 2) | closed |
| T-16-03 | Tampering | the built part (`tests/regression/pre_v0_2.json`, selectors, cuts) | medium | mitigate | `git diff --quiet 085e5a6 HEAD -- tests/regression/pre_v0_2.json` exits 0; `src`/`tests` diff against `085e5a6` is two files; `build(GearParams(tip_chamfer=0.5))` reads `('Solid', True, 4446.54642, 210, 604)` before and after and 18 untouched functions are AST-identical (16-VERIFICATION truth 8, re-run 2026-10-05); the 44-record replay runs in every `make verify` | closed |
| T-16-04 | Information disclosure | the new `BuildError` text | low | mitigate | `_NOT_A_BODY` (`model.py:414-416`) is a fixed sentence with one `{}` filled by `type(x).__name__` — no parameter, path or traceback; asserted as the whole string by both tests; `records.build_failed` (`records.py:235`) logs a `BuildError` at WARNING with `exception = type(exc).__name__`, no traceback; the API returns it as `{"type": "build_error", "msg": str(exc)}` at 422 (`app.py:430-434`) | closed |
| T-16-05 | Repudiation | a pipeline defect reported as a 422 user error | low | accept | R-16-01: the same trade-off as the three existing selector guards (16-RESEARCH Finding 14); the sentence says "a modelling defect in the build pipeline, not a parameter problem"; the check asserts the invariant `_build()`'s end check already asserts and cannot fire from any settable field (`model.py:419-427` comment); recorded in L35 | closed |
| T-16-06 | Repudiation | `nyquist_compliant` and the gap count | medium | mitigate | read at HEAD: `07-VALIDATION.md` `status: validated`, `nyquist_compliant: true` (last commit `5ba02d2`); `08-VALIDATION.md` the same (`8ae468e`); gap counts recomputed from the files: 07 has 3 Manual-Only data rows, 08 has 0 — the 16-02 ledger has 3 rows, the debt file 3 rows; audit and L35 carry the same two values | closed |
| T-16-07 | Tampering | scope (tests written by the skill) and the gate (a commit without the hook) | medium | mitigate | `git log --grep '^test(phase-0\?[78])' 085e5a6..HEAD` is empty; no `tests/` or `src/` path beyond 16-01's two in the phase diff; `655583f`, `5ba02d2`, `8ae468e` each carry exactly one `VALIDATION.md`; no `--no-verify` is claimed anywhere (16-02-SUMMARY:129 — the twelve `--no-verify` mentions in the phase artifacts are all prohibitions); every commit in the window passed the `make verify` hook | closed |
| T-16-08 | Tampering | concurrent work in one tree while the hook sets unstaged edits aside | low | mitigate | the executor was halted at a blocking checkpoint while the human ran the skill; the three human commits each carry one file; the post-check (16-02 Task 1 verify) reads committed state only and was re-run at HEAD with the same values | closed |
| T-16-09 | Repudiation | `v0.2-MILESTONE-AUDIT.md` amendment | low | mitigate | `git diff 085e5a6 HEAD` on the audit removes exactly three lines — `compliant_phases: ["09", "10", "11", "12"]`, `missing_phases: ["07", "08"]`, `overall: partial` — and adds the new values plus an `amended:` key naming those prior values and the dated `### Amended 2026-10-05 by Phase 16` section; the six original rows and the original Overall line are byte-identical (16-VERIFICATION truth 15) | closed |
| T-16-10 | Repudiation | L35's numbers and shas | low | mitigate | `git diff --numstat 085e5a6 HEAD -- docs/architecture/decision_log.md` = `80 0` (L21 and every earlier entry untouched); one `## L35` heading and it is last; the eight distinct shas among the ten backticked (`085e5a6`, `4f7e8fe`, `c11213e`, `655583f`, `5ba02d2`, `8ae468e`, `4035b04`, `3b9d977`) all `git cat-file -t` → `commit`; both `nyquist_compliant: true` phrases match the files; every figure traced to its source line a second time in 16-UAT test 1 | closed |
| T-16-11 | Tampering | the debt ledger (a gap silently dropped or a `must` row filed as `nice`) | medium | mitigate | 3 ledger rows (16-02-SUMMARY § Gap ledger) ↔ 3 data rows in `docs/tech_debt/active/2026-10-05-phase-07-nyquist-gaps.md` § Gaps ↔ 3 Manual-Only data rows in `07-VALIDATION.md`; one INDEX row; `Severity: nice` with the closest call (row 2, byte-stable regeneration) argued in the file and a `Revisit when:` trigger; zero `must` rows, so the D-09 carry/fix gate was never reached; Phase 8 has 0 rows and no file | closed |
| T-16-12 | Tampering | unstaged planning edits during a commit's ~65-90 s hook, which pre-commit sets aside and restores | low | mitigate | `3b9d977` carries exactly `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md` and the audit; `71f474d` carries `decision_log.md` alone, after it; `4035b04` the debt file and INDEX; each plan's commit step checked `git diff --quiet` after staging (16-03-SUMMARY threat flags) | closed |
| T-16-SC | Tampering | npm/pip/cargo installs (declared in 16-01, 16-02, 16-03; `accept`, low, in each) | low | accept | R-16-02: no package installed; `git diff --quiet 085e5a6 HEAD -- requirements.txt` exits 0; the whole `pyproject.toml` diff against `085e5a6` is the `[[tool.mypy.overrides]]` comment and `module = ["OCP.*"]` — `[project] dependencies` and the `[dev]` extras untouched | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

Residual, stated, not a threat in this register: nothing mechanical refuses a future
`typing.cast` in `model.py` — the human chose mypy strict + review over a grep pin
(16-UAT test 2, 2026-10-05). The verifier's observation that `_cell_cutters`
(`model.py:355-357`) raises a bare `TypeError` on a non-`Solid` prototype, which
`_build_checked` would relabel with the catch-all remedy, predates this phase and is
unchanged by it; the human has not yet said whether it gets a debt file.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-16-01 | T-16-05 | A `_body` / `_shape_of` refusal surfaces as a 422 `build_error` like the three selector guards already do; the sentence names a modelling defect, not the user's parameters, and no settable field can make it fire. A new status code or exception class for a path no user can reach was judged not worth it (16-RESEARCH Finding 14, recorded in L35) | 16-01 PLAN threat model; L35 | 2026-10-05 |
| R-16-02 | T-16-SC (declared ×3, once per plan) | No package is installed in any of the three plans; `requirements.txt` byte-identical to `085e5a6`; `pyproject.toml` changed only in the mypy override | 16-01 / 16-02 / 16-03 PLAN threat models | 2026-10-05 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-05 | 15 (12 numbered + T-16-SC declared ×3) | 15 | 0 | verify-work orchestrator — secure-phase (State B, from the three PLAN.md threat models and the three SUMMARY `## Threat Flags` sections, each reading "None"), ASVS L1, short-circuit (register authored at plan time, threats_open 0); every grep, `git diff`, `git show --stat` and file read above re-run at `4a050c9` on 2026-10-05 |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-05
