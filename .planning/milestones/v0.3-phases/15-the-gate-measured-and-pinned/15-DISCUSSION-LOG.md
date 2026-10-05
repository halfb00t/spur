# Phase 15: The Gate, Measured and Pinned - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-03
**Phase:** 15-the-gate-measured-and-pinned
**Areas discussed:** The bar — shape and timing, pytest-xdist policy, Coverage floor, CI kernel pin mechanism

**Opening finding surfaced before the area pick:** ROADMAP SC2 / REQ-verify-profiled say
the bar is set "at this phase's discuss-phase from the profile", but the profile is this
phase's own first deliverable and does not exist. Last recorded gate: 907 passed in
216.73 s, 217.83 s wall at host load 9 (Phase 12 B2); today 927 tests, no `--durations`
on record, host load 4.37. Neither `pytest-xdist` nor `pytest-cov` is installed.

---

## The bar — shape and timing

### When does the bar get its number?

| Option | Description | Selected |
|--------|-------------|----------|
| Shape now, number at a checkpoint | Decide shape and cut policy here; plan 15-01 produces the profile; executor halts with table + proposed cuts; human sets the number; written back into 15-CONTEXT.md; ROADMAP/REQ "at discuss-phase" corrected in the same PR (14 D-07 precedent) | ✓ |
| Run one profile now | One `make verify --durations` on this host (load 4.37, ~4 min, single non-alternating sample) | |
| Set a number now from the record | Pick a figure from Phase 12's 217.83 s; contradicts REQUIREMENTS "Out of Scope" | |

**User's choice:** Shape now, number at a checkpoint (Recommended)

### What shape is the bar?

| Option | Description | Selected |
|--------|-------------|----------|
| Absolute wall seconds, dev host | `make verify` end-to-end wall on this machine, D-10's way; what the hook costs; CI job time as context only | ✓ |
| Ratio to the measured baseline | Travels across hosts; hides the absolute; every later phase re-measures the baseline | |
| pytest seconds only | Excludes ruff/mypy/import-linter/no-fake-done | |

**User's choice:** Absolute wall seconds, dev host (Recommended)

### What may change the gate's cost without being named?

| Option | Description | Selected |
|--------|-------------|----------|
| Parallelism + dedup free; any skip/removal by name | xdist and non-proof changes need no approval; any test removed/skipped/marked/sampled is listed at the checkpoint with its proof-value cost and accepted by name or stays; L13 untouched | ✓ |
| Nothing is cut, period | The bar is whatever parallelism and free wins deliver | |
| Allow a slow tier skipped in the hook, run in CI | Fastest local commits; hook and CI no longer run the same gate — trades against L13 | |

**User's choice:** Parallelism + dedup free; any skip/removal by name (Recommended)

### What load rule governs the profile and before/after runs?

| Option | Description | Selected |
|--------|-------------|----------|
| D-10 as is: alternate, record load, no quiet gate | Alternating A/B in one session, load read before each, delta = mean(B) − mean(A); profile = two runs with load recorded | ✓ |
| D-05 quiet gate | Three 30 s samples under 1.5, 15-min cap; this host met it in 2 of 5 sessions | |
| D-10 locally plus CI job wall time | As the first, plus the Actions job duration as a load-independent second reading | |

**User's choice:** D-10 as is (Recommended)
**Notes:** User moved to the next area without further questions.

---

## pytest-xdist policy

### What measurement makes xdist adoptable?

| Option | Description | Selected |
|--------|-------------|----------|
| 3 green runs, same pass set, peak RSS recorded | Three consecutive full runs at the chosen `-n`, each the full count, zero flakes/reruns, peak RSS in the header; one failure = not adopted this phase | ✓ |
| 1 green run is enough | Cheapest; a 1-in-5 pool flake would not show | |
| Measure only, do not adopt this phase | Record serial vs `-n`; `make verify` stays serial | |

**User's choice:** 3 green runs, same pass set, peak RSS recorded (Recommended)

### How is the worker count chosen?

| Option | Description | Selected |
|--------|-------------|----------|
| Sweep N, pick the knee at the checkpoint | N ∈ {2, 4, 8, 12}, one run each, load and peak RSS; human picks N at the bar checkpoint; N written as a literal citing the table | ✓ |
| `-n auto`, record peak RSS | Every logical CPU (12 here, 4 on CI); memory decides after the fact | |
| Fixed conservative N = 4 | Mirrors CI's vCPU count; leaves 8 cores idle on the bar's host | |

**User's choice:** Sweep N, pick the knee at the checkpoint (Recommended)

### Where does the `-n` flag live?

| Option | Description | Selected |
|--------|-------------|----------|
| Makefile `test` target only | `make test`/`make verify`/CI go parallel; bare pytest stays serial; `make test-image` (installs only `pytest httpx`) unaffected | ✓ |
| `addopts` in pyproject.toml | Every invocation parallel; debugging flags fight xdist; `make test-image` breaks unless xdist added | |
| Makefile, and `make test-image` gets xdist too | Same shape in the image; one more place to keep in step | |

**User's choice:** Makefile `test` target only (Recommended)

### How are tests distributed across workers?

| Option | Description | Selected |
|--------|-------------|----------|
| `--dist load` (default), isolate only if measured | Individual tests spread; module fixtures per worker; `xdist_group`/`loadgroup` for pool tests only if a tolerance run flakes, reason recorded | ✓ |
| `--dist loadfile` | Safe by construction; `test_model.py` serialises on one worker | |
| `--dist loadgroup` with pool tests grouped from day one | Pre-emptive isolation before measuring | |

**User's choice:** `--dist load`, isolate only if measured (Recommended)
**Notes:** User moved to the next area without further questions.

---

## Coverage floor

### Does BuildPool worker-process code count toward the floor?

| Option | Description | Selected |
|--------|-------------|----------|
| Count it: multiprocessing concurrency + combine | `concurrency = ["multiprocessing"]`, `parallel = true`, `sigterm = true`; pytest-cov subprocess hook + combine; baseline states how | ✓ |
| Declare it uncovered, floor set on that reading | No subprocess tracing; `pool.py` worker lines read uncovered; the number understates | |
| Exclude worker-side lines with `# pragma: no cover` | Hides code the pool tests do run | |

**User's choice:** Count it (Recommended)

### How far under the baseline is `fail_under`?

| Option | Description | Selected |
|--------|-------------|----------|
| Whole percent below, determinism checked | Baseline rounded down to an integer; one more point if slack < 0.25 pt; the three tolerance runs' spread must fit | ✓ |
| Baseline minus 1.0, two decimals | Always exactly one point; odd literal | |
| Baseline minus 0.1 | Tightest; one timing-dependent branch could flip a run red | |

**User's choice:** Whole percent below, determinism checked (Recommended)

### What does the floor cover?

| Option | Description | Selected |
|--------|-------------|----------|
| `src/spur` only | The product; configured intent; debt file's scope | ✓ |
| `src/spur` + `scripts/` | Merge-gate tooling joins the floor | |
| `src/spur` + `scripts/` + `bench/` | Everything mypy checks; `bench/` is hand-run by design | |

**User's choice:** `src/spur` only (Recommended)

### Who accepts the tracing cost on every `make verify`, and when?

| Option | Description | Selected |
|--------|-------------|----------|
| Every run; cost is a row at the bar checkpoint | Delta measured D-10's way against the profiled baseline; one row at the same checkpoint; no separate halt or pre-chosen ceiling | ✓ |
| Every run, but halt if the delta exceeds a ceiling named now | Pre-agreed line forces a second checkpoint; a number chosen before the profile exists | |
| CI only; local `make verify` skips coverage | Breaks L13 and REQ's acceptance text | |

**User's choice:** Every run; cost is a row at the bar checkpoint (Recommended)
**Notes:** User moved to the next area without further questions.

---

## CI kernel pin mechanism

### Which mechanism pins the kernel pair in CI?

| Option | Description | Selected |
|--------|-------------|----------|
| Constraints file: `pip install -c requirements.txt -e '.[dev]'` | L12's 31 `==` lines constrain every CI install; both halves pinned; dev extras and pruned packages free; pyproject untouched; outside REQ's two named options — REQ/SC4 amended in the same PR | ✓ |
| REQ option A: install `requirements.txt --no-deps`, then the dev extras | pip keeps satisfied pins; second install pulls ~550 MB of pruned deps back; CI-only | |
| REQ option B: upper bound on `cadquery` in `pyproject.toml` | Pins every environment; `cadquery-ocp` pinned only through cadquery's own cap; adds a product dependency for a fixture reason | |

**User's choice:** Constraints file (Recommended)

### Does the constraints file also govern `make venv`?

| Option | Description | Selected |
|--------|-------------|----------|
| CI only this phase; local as a filed idea | REQ's scope is CI; tripwire test stays the local remedy; closure resolved on linux/amd64, arm64 unproven; idea filed with that trigger | ✓ |
| CI and `make venv`, proven by a fresh venv here | One install path everywhere; one more ~1.4 GB install; wider L34 | |
| CI only, no idea filed | Loses the thought | |

**User's choice:** CI only this phase; local as a filed idea (Recommended)

### Where is "where the pin lives" written down?

| Option | Description | Selected |
|--------|-------------|----------|
| Tripwire test's docstring + a comment in `ci.yml` | Names `requirements.txt`, `docker/refresh-requirements.sh`, `make fixture.regen`; fixture file untouched | ✓ |
| Test docstring + `docs/HOW_TO_DEVELOP.md` | Misses whoever edits `ci.yml` | |
| Amend the fixture's `regenerate` note as its own commit | Changes fixture bytes for a prose reason | |

**User's choice:** Tripwire test's docstring + a comment in `ci.yml` (Recommended)

### What makes the CI log show the resolved pair?

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit version-print step + tripwire green | One `python -c` line prints both versions; the run URL goes in L34 and the retired debt file | ✓ |
| Explicit step, plus a scratch run proving the tripwire fires | Throwaway branch constrained to `cadquery-ocp==8.0.1.0.0`; recorded, never merged | |
| pip's own "Successfully installed …" line is enough | Buried in ~60 names; absent on a cache hit | |

**User's choice:** Explicit version-print step + tripwire green (Recommended)
**Notes:** User chose "I'm ready for context" at the closing check.

---

## Claude's Discretion

- Plan order (suggested sequence in CONTEXT.md).
- `--durations` count and whether it stays in `make test` after the profile.
- Peak-RSS measurement method for the whole process tree.
- Makefile spelling for N; `[tool.coverage.report]` flags; the scratch run's removed file.
- `PIP_CONSTRAINT` env vs explicit `-c`; placement of the version-print step; pip cache key.
- Checkpoint table layout; L34 title and wording.
- `xdist_group` marker declaration if D-08 triggers.

## Deferred Ideas

- Constrain local `make venv` to the closure — filed `docs/ideas/2026-10-03-constrain-make-venv-to-the-closure.md`.
- `make test-image` in parallel — not taken.
- A `slow` tier — rejected (L13), recorded so it is not re-proposed.
- A scratch CI run manufacturing the tripwire's trigger — not taken.
- `--durations` permanently in `make test` — default no.
- `/gsd-map-codebase --paths bench` and a `TESTING.md` refresh — owed since Phase 13.
- The gsd commit-timeout debt's trigger number — updated, not retired.
