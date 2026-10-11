---
phase: "22"
slug: "download-name-carries-the-root"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-11"
---

# Phase 22 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| HTTP query → `GearParams` | untrusted query fields are validated once; the file name is built only after that | `teeth` (int), `module`, `pressure_angle` (bounded floats), `root_shape` (a `Literal`), `root_fillet` |
| `GearParams` → `Content-Disposition` header | the name leaves the server in a response header and becomes a file name on the user's disk | `spur_z{teeth}_m{module:g}_pa{pressure_angle:g}` plus the literal `_trochoid` |
| failure path → structured log records | `slug()` runs inside `build.failed` / `queue.refused`; an exception there would lose the record of a failure | the `slug` field of four record kinds |
| a measurement → a recorded figure | a reading becomes a number later phases cite (Phase 25's bar); a mis-copied or estimated one is a false claim (L08) | three `step download name` readings, host state |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-22-01 | Tampering | `Content-Disposition` filename via `slug()` (`app.py`, built per response after the byte cache) | low | mitigate | `src/spur/params.py:206-210`: the name is `f"spur_z{self.teeth}_m{self.module:g}_pa{self.pressure_angle:g}"` plus the literal `_trochoid` chosen by `root_mode`; `root_shape` is `Literal["radial", "trochoid"]` (`params.py:59`), so no request text reaches the header; whole-value header pins in `test_the_download_name_carries_the_root_the_part_has` (`tests/test_api.py:736`) | closed |
| T-22-02 | Repudiation | the suffix rule in `slug()` — a name claiming a root the part lacks (L08) | medium | mitigate | the effective root: `root_mode(self, profile(self), requested=self.root_shape, rho=self.root_fillet).mode == "trochoid"` (`params.py:209-210`), never the requested root; the ignored (27, 40 teeth), refused (`tip land gone`) and `build.failed` rows were seen red under the requested-root rule — four red rows under `bench/RESULTS.md` `### Seen red once (Phase 22)` (line 5306) | closed |
| T-22-03 | Denial of service | `slug()` on the event loop and in failure records, now calling a solver | low | mitigate | no `try`, totality by construction (L40 "Totality"): six pure rows (`test_the_download_name_follows_the_root_root_mode_builds`, `tests/test_trochoid.py:225`), two `build.failed` rows (`test_a_failed_build_records_the_name_of_the_part_it_would_have_been`, `tests/test_api.py:1124`), the 17,567-case sweep (9,954 `_trochoid`, none raised) and the verifier's own re-run of it; cost 2.3–37.8 µs per call, at most four calls per request (L40 "The cost"). Residual, open in `22-REVIEW-DISPOSITION.md` WR-01: the sweep is a command, not a test | closed |
| T-22-04 | Information disclosure | log greps keyed on `slug` see a new value for hob-root gears | low | accept | documented in L40 ("a grep keyed on a slug"); `params` in every record still carries the full request — see Accepted Risks Log R-22-01 | closed |
| T-22-05 | Tampering | the regression fixture or golden request pin moved inside a feature commit | low | mitigate | `git diff --quiet 0290a07 HEAD -- tests/regression/` exits 0 on `e6122a6` (`tests/regression/pre_v0_2.json` and `golden_requests.json` byte-unchanged since the `main` merge base); the `test_model_download` pin `spur_z21_m1.75_pa25.{fmt}` unedited | closed |
| T-22-06 | Repudiation | `bench/RESULTS.md` readings recorded from estimates, another host or a dirty tree | low | mitigate | three kept logs committed in `f905a25` (`investigation/22-02-reading-{1,2,3}.log`: `step download name: 3.56 s`, `3.20 s`, `1.13 s`) and the table under `### The download step, priced (22-02)` reads 3.56 / 3.20 / 1.13 with host state, HEAD `5c6c025` and the clean-tree check; no figure compared with Phase 21's host; no bar set | closed |
| T-22-07 | Tampering | `BUILD_WAIT_MS` or a wait tuned toward a pass | low | mitigate | `tests/browser_session.py:52` `BUILD_WAIT_MS = 45_000`; the file's AST with docstrings blanked is identical between `0290a07` and HEAD (comment-only edit, 12+/4−); the slowest reading 3.56 s is under 21 PD-04's 15 s, so the plan's decision checkpoint never fired and nothing moved | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-22-01 | T-22-04 | A log grep keyed on a slug sees `spur_z23_m1.75_pa25_trochoid` where it saw `spur_z23_m1.75_pa25`; the `params` object in each record is unchanged and carries the full request, so nothing is lost — only a grep pattern may need the suffix. Recorded in L40. | 22-01 plan (D-10), human-approved plan | 2026-10-11 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-11 | 7 | 7 | 0 | gsd-secure-phase (orchestrator, ASVS L1 grep-depth short-circuit; evidence read on `e6122a6`) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-11
