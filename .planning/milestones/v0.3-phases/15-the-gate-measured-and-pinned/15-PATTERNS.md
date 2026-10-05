# Phase 15: The Gate, Measured and Pinned - Pattern Map

**Mapped:** 2026-10-03
**Files analyzed:** 16 (all config / prose / record; no `src/`)
**Analogs found:** 15 / 16 (`.gitignore` has no analog, trivial)

All analog paths verified git-tracked (`git ls-files`). No gitignored mirrors named.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `pyproject.toml` (`[dev]`, `[tool.coverage.*]`) | config | n/a | same file, `[tool.coverage.run]` (125-129) and `dev` list (20-27) | exact (in place) |
| `Makefile` (`test` target, `PYTEST_WORKERS`) | config | request-response (CLI) | `Makefile` `PYTEST_ARGS ?=` (6) + `test:` (70-71) | exact (in place) |
| `.github/workflows/ci.yml` (`test` job) | config | batch | same file's `test` job + step-level comments | exact (in place) |
| `.gitignore` | config | n/a | same file (no coverage entry) | none needed |
| `.pre-commit-config.yaml` (comment, lines 6-8) | config | n/a | same comment block | exact (in place) |
| `bench/RESULTS.md` (new Phase 15 section) | measurement record | batch | `## Composition pass test cost (Phase 12, D-10)` (2130-2198) | exact |
| `tests/regression/test_pre_v0_2.py` (one docstring) | test | request-response | same function (80-90) | exact (in place) |
| `docs/architecture/decision_log.md` (L34) | record | append-only | `## L33` (1517-1626), `## L32` (1427) | exact |
| `docs/tech_debt/{active->resolved}/2026-09-21-no-coverage-floor.md` | debt retirement | CRUD (git mv) | `resolved/2026-09-23-concurrent-latency-bar-waived.md` | exact |
| `docs/tech_debt/{active->resolved}/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md` | debt retirement | CRUD (git mv) | same + `6709953` -> `05668ef` two-commit shape | exact |
| `docs/tech_debt/INDEX.md` (rows 21, 26) | index | CRUD | its own Resolved table | exact |
| `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-...md` (update number, not retire) | debt | prose edit | itself (lines 8, 15) | exact |
| `.planning/REQUIREMENTS.md`, `ROADMAP.md`, `PROJECT.md` amendments | planning record | prose edit | 14 D-07 precedent (ROADMAP via gsd tooling only) | role-match |
| `15-CONTEXT.md` D-01 addendum | planning record | append | Phase 12 "### Gate decision" in RESULTS.md | role-match |
| **EXTRA, not in CONTEXT:** `README.md:282`, `docs/HOW_TO_DEVELOP.md:21`, `docs/architecture/packaging.md:41` | prose | n/a | `~11 s` claim sites | exact |

## Pattern Assignments

### `pyproject.toml` (config)

**Analog:** itself. Current `dev` list (lines 20-27):
```toml
dev = [
    "pytest>=8",
    "httpx>=0.27",
    "ruff>=0.14",
    "mypy>=1.18",
    "import-linter>=2.3",
    "pre-commit>=4",
]
```
Append `"pytest-xdist>=3.8"`, `"pytest-cov>=7.1"` (RESEARCH Standard Stack). `$(STAMP)` depends on `pyproject.toml` so the next `make` reinstalls.

**Current coverage block to replace** (lines ~125-129):
```toml
[tool.coverage.run]
branch = true
source = ["src/spur"]
# No fail_under yet: a floor picked without measuring is a number, not a guarantee.
# See docs/tech_debt/active/2026-09-21-no-coverage-floor.md.
```
**Target shape** (RESEARCH Code Example 5; supersedes D-09's text, `"thread"` must be listed, `precision = 2`):
```toml
[tool.coverage.run]
branch = true
source = ["src/spur"]
# BuildPool's spawned workers (pool.py:35) are separate processes: "multiprocessing" makes
# coverage instrument them, "thread" must be listed too or setting this key drops the
# default and the lifespan thread's lines vanish, "parallel" writes one data file per
# process for pytest-cov to combine, "sigterm" saves a worker that pool.py:205 terminates.
concurrency = ["multiprocessing", "thread"]
parallel = true
sigterm = true

[tool.coverage.report]
# <baseline>% read on <date> (bench/RESULTS.md "<section>"), minus the D-10 slack. precision 2 so
# the number printed and the number compared are the same one (the default rounds to 0 dp).
fail_under = <D-10 number>
precision = 2
```
Style: comments carry the measurement and date and cite the RESULTS table (house pattern, `HEX_CELL_CAP = 120`). No formatter (L16): hand-align. `[tool.pytest.ini_options]` (`addopts = "--strict-markers --strict-config"`) stays untouched; `xdist_group` needs no `markers` entry (RESEARCH Pitfall 10).

---

### `Makefile` (config)

**Analog:** itself. Existing vars (lines 4-8) and `test` (70-71):
```make
PYTEST_ARGS ?=
SWEEP       ?=
SET         ?=
...
test: $(STAMP)  ## run the test suite (a cold first run is page cache, not the tests)
	$(PY) -m pytest $(PYTEST_ARGS)
```
**Target** (RESEARCH Code Example 4; add `PYTEST_WORKERS ?= N` beside the other `?=` vars, aligned to the column; keep the `##` help text because `help` greps `^[a-z][a-z.-]*:.*##`):
```make
# N is the knee of bench/RESULTS.md's xdist sweep (12-CPU M2 Max); -n0 runs serially, and
# --no-cov skips the coverage floor for a partial run:
#   make test PYTEST_ARGS="tests/regression -q --no-cov -n0"
PYTEST_WORKERS ?= <N from the sweep>

test: $(STAMP)  ## run the test suite (a cold first run is page cache, not the tests)
	$(PY) -m pytest -n $(PYTEST_WORKERS) --cov $(PYTEST_ARGS)
```
`PYTEST_ARGS` lands last so `-n0` / `--no-cov` override. Do NOT touch `test-image` (83-89, installs only `pytest httpx`) or `$(STAMP)` (33-42). Floor comes from `[tool.coverage.report]`, so no `--cov-fail-under` literal (REQUIREMENTS sentence amended instead).

---

### `.github/workflows/ci.yml` (config, batch)

**Analog:** itself, `test` job (lines 12-27). Comment style above a step explains why (lines 24-26):
```yaml
      # The same gate a developer runs locally and `make worktree.land` runs before a
      # merge: ruff, mypy --strict, the import-boundary contracts, the unfinished-work
      # scan and the tests. One definition of "passing", enforced in three places.
      - run: make verify PYTHON=python
```
**Target** (RESEARCH Code Example 6): add `env: PIP_CONSTRAINT: requirements.txt` on the `make verify` step (the install happens inside `$(STAMP)`, so a separate `pip install -c` step installs nothing into `.venv`), the "where the pin lives" comment (D-15), and a version-print step after it using `.venv/bin/python` with `if: always()`.

**Constraint:** `tests/test_pr_land.py::_effective_job_names` is a regex parser: job ids are two-space keys, job `name:` only at exactly 4 spaces. Step-level `env:` (8 spaces) is invisible to it. Do not add a 4-space `name:` under `test:`. `required-jobs.txt` unchanged (`test (3.12)`, `vendor-bundle`, `image`). Run `tests/test_pr_land.py` after the edit. Matrix stays `["3.12"]` (L23).

---

### `.gitignore` (config)

No analog needed. Existing style is one pattern per line with a `#` comment above groups (e.g. `# generated models` / `*.stl`). Add `.coverage*` (and `htmlcov/` only if an HTML report is ever produced) with a one-line why comment. Not in D-20's list; required before the first `--cov` run lands on a commit (RESEARCH Pitfall 6).

---

### `.pre-commit-config.yaml` (config, comment lines 6-8)

**Analog:** itself:
```yaml
# Install once per clone:  .venv/bin/pre-commit install
# A warm run is ~11 s (the CAD tests dominate). The first run after `make clean` pages
# in ~1.4 GB of OpenCascade and takes a couple of minutes; that is the page cache, not
# the tests.
```
Replace "~11 s" with the measured number from the new RESULTS section (cite the section name and date, comment style carries the measurement). Keep the rest of the comment block and the `stages: [pre-commit]` pin untouched.

---

### `bench/RESULTS.md` (measurement record, batch)

**Analog:** `## Composition pass test cost (Phase 12, D-10)` (lines 2130-2198), the last section; the new Phase 15 section goes after it (and after any Phase 13/14 material). Section skeleton:

```markdown
## <Title> (Phase 15, D-xx)

<one paragraph: what is measured, the method (alternating A/B, load before each,
delta = mean(B) - mean(A)), the bar>

### Host state

- CPU: Apple M2 Max, 12 cores
- RAM: 32.0 GiB
- Python: 3.12.13 (`.venv`)
- Date: 2026-10-03
- Phase-start HEAD ...: `<sha>`
- Load averages (1-minute, `sysctl -n vm.loadavg`), read immediately before each run
  started building: A1 2.87, B1 8.07, A2 8.51, B2 9.07 -- <why no quiet bar (D-04)>
```
Phase 15 additions to the header (CONTEXT D-04/D-05): peak-RSS method ("sum of per-process RSS from a 1 s `ps -axo pid=,ppid=,rss=` tree sampler", RESEARCH Code Example 3, state it overstates shared pages), and `SPUR_*` values. Use `bench/__init__.py::machine_facts()` for the machine line.

**A/B table shape** (lines ~2158-2166):
```markdown
| Run | Code | Load | pytest | Wall (s) |
|---|---|---|---|---|
| A1 | `c9a169d` | 2.87 | 621 passed in 183.67s | 193.30 |
| B1 | `480da30` | 8.07 | 907 passed in 216.90s | 217.90 |
| A2 | `c9a169d` | 8.51 | 621 passed in 184.89s | 185.88 |
| B2 | `480da30` | 9.07 | 907 passed in 216.73s | 217.83 |

mean(A) = 189.59s, mean(B) = 217.87s -> **delta = 28.28s**, against D-10's 30.0s line
```
Phase 15 row columns per CONTEXT: sweep `N | passed/failed | pytest s | wall s | load | peak RSS`; tolerance rows the same plus coverage total (spread across the three = D-10 determinism reading).

**Subsections to mirror:** `### make verify wall time` (`/usr/bin/time -p`, "includes lint/typecheck/import-lint/no-fake-done"), `### Regression fixture share` (opens with `git diff --exit-code <sha> -- tests/regression/pre_v0_2.json` clean), and closing `### Gate decision` carrying the human's verbatim checkpoint answer ("accept (Recommended)" shape). Record red rows as measured, never re-run to green. Per-file shares: put the exact awk command in the method note (RESEARCH Code Example 2; no new script, Open Question 3). Profile runs use `--no-cov -n0`. Partial runs now need `--no-cov -n0` in `PYTEST_ARGS` (old `make test PYTEST_ARGS="tests/regression -q"` fails the floor).

---

### `tests/regression/test_pre_v0_2.py` (test, docstring only)

**Analog:** itself, lines 80-90:
```python
def test_the_fixture_was_captured_on_the_kernel_this_run_uses() -> None:
    """Pitfall 11: an unpinned kernel bump otherwise shows up as dozens of unexplained
    topology mismatches instead of one named test."""
    ...
    assert running == captured, (
        f"fixture captured on cadquery/cadquery-ocp {captured}, this run uses {running}; "
        "recreate the venv to match, or regenerate with `make fixture.regen` per D-03 "
        "if the pin moved deliberately")
```
Extend the docstring only (D-15): name `requirements.txt` as the pin (CI via `PIP_CONSTRAINT`), `docker/refresh-requirements.sh` as what moves it, `make fixture.regen` as the fixture's own move. Keep the `-> None` annotation and no `Any` (L21). `pre_v0_2.json` is never edited.

---

### `docs/architecture/decision_log.md` (L34, append-only)

**Analog:** `## L33 — ... (amends L09, L10 and L30)` (line 1517 to EOF, 1626 lines). Shape, in order:
```markdown
## L33 — <title naming the thing> (amends L09, L10 and L30)

Date: 2026-10-03.

L09, L10 and L30 stay as written; this entry amends <the specific claim> with what Phase 14 measured and proved.

**<Topic 1>** (D-01 to D-04, ...). <what, numbers cited to RESULTS section / SUMMARY sha> ... Commits: `13857e1` (...), ...

**<Topic 2>** (D-05 to D-10). ...

**Reversibility.** Reversible on every axis ... The path not taken stays costly and untouched: ...

Reason: <one paragraph>
Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1 (`importlib.metadata.version`), Python
3.12.13 (`sys.version.split()[0]`), read 2026-10-03; ...
```
For L34 "(amends L12 and L13)": three bold topics (the measured gate; the floor; the pin) per D-17. Required content from RESEARCH: use 1,069 statements / 294 branches (not D-10's ~3,100); say `concurrency` includes `"thread"` and pytest-cov 7 dropped subprocess hooks; D-16's "absent on a cache hit" justification is false (Pitfall 14); L13's "~11 s warm" correction lives here since L13 text (line 118-121) is untouched. Cite each number to a `bench/RESULTS.md` section or a SUMMARY sha. No mirror paths.

---

### Debt retirements (`git mv` active -> resolved + INDEX row)

**Analog:** `docs/tech_debt/resolved/2026-09-23-concurrent-latency-bar-waived.md`. Header block (lines 1-7):
```markdown
# The concurrent latency bar was waived, not demonstrated

Severity: must
Status: resolved
Date: 2026-09-23
Resolved in: 6709953
Source: ...
```
Body keeps original sections and appends a dated resolution section:
```markdown
## Resolution (2026-10-02)

Phase 13 ran ... (`bench/RESULTS.md` § "..."). ... All three findings are logged in
`docs/architecture/decision_log.md` L32 (amends L18), append-only.
```
Also delete the trailing `<!-- On resolve: ... -->` comment if present (the template keeps it in some files; the analog shows it left in, harmless either way).

Apply to:
- `no-coverage-floor.md` (Severity nice, currently `Status: active`): flip Status, add `Resolved in: <coverage commit sha>`, correct the false sentence "`pytest-cov` is installed." (currently in `## Context`), add `## Resolution (date)` citing the RESULTS baseline and L34. Retired in the coverage commit.
- `ci-resolves-the-kernel-the-fixture-pins.md` (Severity must): `Resolved in:` cites the pin commit sha AND the green run URL; follow-up commit shape from Phase 13 (`6709953` -> `05668ef`, file cannot carry its own sha).

**INDEX.md row shapes.** Active table (3 columns) row to delete:
```markdown
| nice | [No coverage floor in the gate](active/2026-09-21-no-coverage-floor.md) | after one measured baseline run |
```
Resolved table (2 columns) row to add, same commit:
```markdown
| [The concurrent latency bar was waived, not demonstrated](resolved/2026-09-23-concurrent-latency-bar-waived.md) | `6709953` — see the file's own `Resolved in:` field |
```
Link target changes `active/` -> `resolved/`. Do not retire `2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`; only update its "~11 s warm" numbers (lines 8 and 15).

---

### `~11 s` prose sites (D-19)

CONTEXT names `.pre-commit-config.yaml`, L13 (via L34), `PROJECT.md`, `TESTING.md`. A tree grep finds additional live claims:

| Site | Action |
|---|---|
| `.pre-commit-config.yaml:6` | measured number (REQ) |
| `docs/architecture/decision_log.md:121` (L13) | untouched, L34 corrects |
| `.planning/PROJECT.md:403` | number at transition |
| `README.md:282` "(~11 s, no Docker)" | **not in CONTEXT**; edit (README is not append-only) |
| `docs/HOW_TO_DEVELOP.md:21` "~11 с на прогретом кеше" (Russian text, keep language) | **not in CONTEXT**; edit |
| `docs/architecture/packaging.md:41` | **not in CONTEXT**; edit |
| `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-...md:8,15` | update number |
| `.planning/REQUIREMENTS.md:129`, `ROADMAP.md:206` | quote the claim being corrected; leave or reword via gsd tooling |
| `.planning/codebase/TESTING.md`, `.planning/intel/*` | maps, not hand-edited |
| `.planning/STATE.md:116`, `RETROSPECTIVE.md`, `MILESTONES.md`, `*-SUMMARY.md` | false positives ("~11min", "~11 h") |

Planner should ask the human whether the three extra doc sites are in scope (CLAUDE.md "stop and ask": evidence conflicts with CONTEXT's list).

---

### `.planning/` amendments

**Analog:** 14 D-07 (correct the planning record's own false sentence in the PR). Edit sites: `REQUIREMENTS.md` ("at this phase's discuss-phase" in REQ-verify-profiled / REQ-verify-at-the-bar -> "at the profile checkpoint"; the "one of two mechanisms" sentence in REQ-ci-installs-the-pinned-kernel; the `--cov --cov-fail-under` sentence per RESEARCH Open Question 2), `ROADMAP.md` SC2 / SC4 / "Depends on" **only through gsd roadmap tooling**, never a whole-file Write; `PROJECT.md` Outcome columns for L12/L13 and Constraints "Gate" at transition.

---

## Shared Patterns

### Measurement, then cite
**Source:** `bench/RESULTS.md` 2130-2198; CONTEXT "Established Patterns".
**Apply to:** every number written to config comments, L34, debt files, `.pre-commit-config.yaml`. A literal in config cites the RESULTS section and date. No re-estimates.

### Partial-run escape hatch
**Source:** RESEARCH Pitfall 5, Code Example 4.
**Apply to:** Makefile comment, RESULTS method note, every profile run. `PYTEST_ARGS="... --no-cov -n0"`.

### Append-only record
**Source:** `decision_log.md` L32/L33 ("Lxx stay as written; this entry amends ...").
**Apply to:** L34, and never edit L12/L13 text.

### No formatter, hand-aligned
**Source:** L16. **Apply to:** `Makefile`, `pyproject.toml`, `ci.yml`.

### Byte-unchanged guards (final pass, D-20)
```
git diff --exit-code 20cd484 -- tests/regression/pre_v0_2.json src
git diff --exit-code 20cd484 -- requirements.txt
```

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `.gitignore` `.coverage*` entry | config | n/a | trivial one-liner; no prior coverage artefact handling |
| Version-print CI step | config | batch | no existing step prints installed versions; use RESEARCH Code Example 6 |
| xdist / coverage config | config | n/a | no existing parallel or coverage-gating config; use RESEARCH Code Examples 4-5 |

## Metadata

**Analog search scope:** `Makefile`, `pyproject.toml`, `.github/workflows/`, `.pre-commit-config.yaml`, `.gitignore`, `bench/RESULTS.md`, `tests/regression/`, `docs/architecture/decision_log.md`, `docs/tech_debt/`, tree-wide grep for `~11`.
**Pattern extraction date:** 2026-10-03

**Research corrections the planner must carry (from RESEARCH, supersede CONTEXT text):** D-09 (pytest-cov 7 has no subprocess hook; `"thread"` required), D-10 (1,069 statements + 294 branches; `precision = 2`), D-13 (`PIP_CONSTRAINT` on the `make verify` step, not a separate install), D-16 (print step still good, "absent on cache hit" false).
