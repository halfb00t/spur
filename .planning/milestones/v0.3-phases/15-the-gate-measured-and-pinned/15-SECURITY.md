---
phase: "15"
slug: "the-gate-measured-and-pinned"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-04"
---

# Phase 15 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Phase 15 adds no endpoint, auth path, schema or `src/` change (`src/` and the pre-v0.2
fixture are byte-identical to `20cd484`). Its attack surface is the supply chain and the
record: two packages pulled from PyPI into every test session, CI's install of ~85 packages
on every run, and the numbers in `bench/RESULTS.md` that the bar (66 s), the worker count
(8), the coverage floor (96) and L34 are set from. The threats below are therefore about
what gets installed and whether a recorded number can be moved without the record showing
it. Each mitigation is a check that was run at HEAD `49dcdaf` (the phase's last code commit
is `1eab497`; everything after is `.planning/`), not a promise.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| PyPI → `.venv` | `pytest-xdist` and `pytest-cov` are downloaded and imported in every local test session | two wheels, vetted by the human before install (15-01 Task 2, answer `approved`) |
| PyPI → CI runner | every CI run resolves and installs the closure afresh under `PIP_CONSTRAINT: requirements.txt` | 31 exact runtime pins plus the `[dev]` extras; no hashes (L12, unchanged) |
| measurement → record | `bench/RESULTS.md` rows are what the bar, N, the floor and L34 are set from | wall seconds, loads, coverage totals, HEAD shas per run |
| record → human → config | the human's checkpoint answer becomes `PYTEST_WORKERS = 8` and the 66 s bar; the floor rule becomes `fail_under = 96` | one verbatim answer in two places; two literals in `Makefile` and `pyproject.toml` |
| spawned worker → coverage data | `BuildPool` workers write their own `.coverage.*` files, combined by the controller | per-process data files; a lost flush lowers the total (debt filed, floor clears it) |
| repo → GitHub | the push and draft PR #18 make the branch public and start CI | branch content, already public at ship |
| decision log → later phases | L34 is read as locked fact about the gate's cost, floor and CI kernel | figures, shas, the run URL, the bar |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-15-01 | Repudiation | `bench/RESULTS.md` profile and sweep rows | medium | mitigate | `### Method` (RESULTS:2232) quotes the run recipe; every row carries load, HEAD, wall, RSS and exit; the knee rule precedes the sweep table and the verifier recomputed the knee (N = 8) from it (15-VERIFICATION SC1) | closed |
| T-15-02 | Tampering | `requirements.txt`, the runtime closure | medium | mitigate | `git diff --quiet 20cd484 -- requirements.txt` exits 0, 31 pins; `pytest-xdist>=3.8` and `pytest-cov>=7.1` sit in `[project.optional-dependencies] dev` only; `[project] dependencies` is the same four names | closed |
| T-15-03 | Tampering | coverage total (pragma, narrowed `source`, `omit`, dropped thread tracing) | medium | mitigate | `grep -rn 'no cover' src pyproject.toml` finds nothing (the only `pragma` hits in `src/` are the vendored three.js bundle's `unroll_loop` directives); `[tool.coverage.run]` keeps `source = ["src/spur"]`, no `omit`, `concurrency = ["multiprocessing", "thread"]`; `src/` byte-identical to `20cd484` | closed |
| T-15-04 | Repudiation | `fail_under` literal and the red-run record | medium | mitigate | `fail_under = 96`, `precision = 2` with the rule and its inputs (L = 96.99, S = 0.00) in the comment, citing RESULTS `### Coverage floor` (2532); `### Red on the floor` (2550) records 90.24 % against 96; `git log -S'--ignore=tests/test_cli.py'` empty and `tests/` diff vs `20cd484` is the tripwire docstring only; no `--cov-fail-under` on any command line (the one grep hit is the `pyproject.toml` comment) | closed |
| T-15-05 | Elevation of privilege | coverage's `a1_coverage.pth` auto-start in every interpreter | low | accept | present in `.venv` as shipped by the coverage wheel; its body runs `coverage.process_startup` only when `COVERAGE_PROCESS_START` or `COVERAGE_PROCESS_CONFIG` is set, and neither appears in `Makefile`, `pyproject.toml`, `.github/` or `.pre-commit-config.yaml`; worker coverage rides `concurrency = ["multiprocessing", ...]` instead | closed |
| T-15-06 | Repudiation | the bar, N and cuts | medium | mitigate | the D-01 checkpoint was `blocking-human` with no `auto_select`; `0a74eed` touches RESULTS only and the Makefile/pyproject diff across the 15-03 commits is empty (nothing written before the answer, 15-VERIFICATION truth 6); the verbatim answer `knee-headroom N=8 bar=66 cuts=none before=244.59` sits in 15-CONTEXT.md:64 and RESULTS `### Gate decision` (2696) | closed |
| T-15-07 | Tampering | proposed-cut savings | low | mitigate | `### Proposed cuts` (2601) prices every row from the recorded P1/P2 serial seconds; the human refused all 15 by name, so no saving was applied or claimed at N | closed |
| T-15-08 | Tampering | `tests/` (cuts) | medium | mitigate | no cut applied; `git diff 20cd484 HEAD --stat -- tests` is one file, +7/−1 (the tripwire docstring); `src/`, the fixture and `requirements.txt` byte-identical to `20cd484`; no rerun/retry/flaky plugin in `[dev]` | closed |
| T-15-09 | Repudiation | the before/after verdict | medium | mitigate | `### Before and after` (2720) carries A1 B1 A2 B2 in the fixed order with loads; mean(B) = (64.19 + 62.92) / 2 = 63.555 s ≤ 66 s recomputed by the verifier; every row `927 passed`, exit 0; the miss checkpoint never fired because the bar was met | closed |
| T-15-10 | Denial of service | CI's 4-vCPU runner oversubscribed by N workers | medium | mitigate | `Makefile:85` clamps `PYTEST_WORKERS` to `getconf _NPROCESSORS_ONLN` (`n < w ? n : w`); CI run 37181871926's log reads `created: 4/4 workers` and `927 passed` | closed |
| T-15-11 | Tampering | CI's kernel resolution (an unpinned transitive upgrade under the fixture) | high | mitigate | `ci.yml:37` sets `PIP_CONSTRAINT: requirements.txt` on the `make verify PYTHON=python` step; the always-run step after it prints `cadquery 2.8.0 cadquery-ocp 7.9.3.1.1` (log line re-read 2026-10-04); a scratch constraint at `cadquery-ocp==8.0.1.0.0` fails closed with `ResolutionImpossible` (15-05-SUMMARY, reproduced by the verifier); `test_the_fixture_was_captured_on_the_kernel_this_run_uses` present at `test_pre_v0_2.py:80` with no assertion line changed since `20cd484` | closed |
| T-15-12 | Tampering | constraints without hashes | low | accept | the closure carries no hashes, the same as the image's `--no-deps` install (L12); this phase does not widen that; a hashed closure is a separate decision | closed |
| T-15-13 | Information disclosure | the draft PR opened before ship | low | accept | the repository is `PUBLIC` (`gh repo view`); exactly one PR for the branch (#18, draft), opened once after 15-05 Task 1's local proof per the human's `draft-pr` answer | closed |
| T-15-14 | Repudiation | the debt retired without run evidence | medium | mitigate | `docs/tech_debt/resolved/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md:6` cites `839dfea` and the run URL; `gh run view 37181871926` reads `success`, head `839dfea`, event `pull_request` (re-read 2026-10-04) | closed |
| T-15-15 | Tampering | L12, L13 and earlier decision-log entries | medium | mitigate | `git diff --numstat 20cd484 -- docs/architecture/decision_log.md` = `133 0`; exactly one `## L34 ` heading and it is the last entry | closed |
| T-15-16 | Repudiation | L34's figures and the corrected sites | medium | mitigate | 63.555 appears twice in L34, twice in RESULTS and once in `.pre-commit-config.yaml`; the run URL appears in L34; the verifier spot-checked 224.28, 130.72/84.76/68.93/75.47, 3.51, 165.435, 96.40, 203.16 against RESULTS (truth 14); no `~11 s` claim remains outside the decision log and `.planning/` (truth 15) | closed |
| T-15-SC | Tampering | pip install of `pytest-xdist` and `pytest-cov` (15-01, high); pip installs on the CI runner (15-05, high); no install (15-02/03/04/06, low, accept) | high | mitigate | 15-01 Task 2 was a `blocking-human` package-legitimacy checkpoint before any install, answer `approved` (15-01-SUMMARY:131; UAT test 3 passed 2026-10-04); on CI every pip call in the step runs under `PIP_CONSTRAINT: requirements.txt`, so the runtime set resolves to the L12 closure's exact versions; no other plan installs anything (R-15-01) | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

Residual, stated, not a threat in this register: the green CI run cannot show whether the
constraint or cadquery 2.8.0's own `cadquery-ocp<8.0` cap held the pair, because both pick
7.9.3.1.1 today; the fail-closed property rests on the local dry run, which no CI assertion
repeats. RESULTS and L34 say so openly (UAT test 7, accepted 2026-10-04). A `BuildPool`
worker's coverage flush is sometimes lost (~0.22 pt); the floor (96) clears the lowest
observed total (96.99 %) and the trigger is named in
`docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md`.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-15-01 | T-15-SC (declared ×6, once per plan; accept in 15-02, 15-03, 15-04, 15-06) | No package is installed in those four plans; `requirements.txt` byte-identical to `20cd484`, `[dev]` gained only the two packages vetted at 15-01 Task 2 | verify-work orchestrator, from the six PLAN.md threat models | 2026-10-04 |
| R-15-02 | T-15-05 | coverage's `.pth` auto-start is inert without `COVERAGE_PROCESS_START`/`COVERAGE_PROCESS_CONFIG`, which nothing in the repo sets; ships in the official wheel | 15-02 PLAN threat model (RESEARCH Security Domain) | 2026-10-04 |
| R-15-03 | T-15-12 | A constraints file without hashes is the same trust the image's `--no-deps` install already extends to the closure (L12); not widened here | 15-05 PLAN threat model | 2026-10-04 |
| R-15-04 | T-15-13 | The repository is public; the branch becomes public at ship regardless; one draft PR, opened once per the human's `draft-pr` answer (D-16 addendum) | the human (D-16 addendum), 15-05 PLAN threat model | 2026-10-04 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-04 | 22 (16 numbered + T-15-SC declared ×6) | 22 | 0 | verify-work orchestrator — secure-phase (State B, from the six PLAN.md threat models and five SUMMARY threat-flag sections; 15-03-SUMMARY.md has no `## Threat Flags` section, so T-15-06/T-15-07 are classified from the plan's verifies and 15-VERIFICATION truth 6), ASVS L1, short-circuit (register authored at plan time, threats_open 0); every grep, `git diff` and `gh` read above re-run at `49dcdaf` on 2026-10-04, not taken from the SUMMARYs' word |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-04
