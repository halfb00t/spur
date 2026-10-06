# Stack Research — Milestone v0.4 True Root

**Domain:** parametric involute spur gear generator (shipped); this file covers only what the three v0.4 features need
**Researched:** 2026-10-06
**Overall confidence:** HIGH for (a) and (c) (reproduced on this machine against the pinned tree); MEDIUM for (b) (no free published point table was found, so the reference is built, not downloaded)

Confidence tags used below: **[HIGH]** = run or read locally this session (installed source, a measurement, a scratch repo); **[MEDIUM]** = a web source cross-checked against a local result; **[LOW]** = one web source or an absence-of-evidence claim; **ASSUMPTION** = not verified, surface before acting (L08, CLAUDE.md).
The scratch prototypes behind every number live outside the repo and are not committed; the implementation phase re-derives them as tests.

---

## Verdict

**Add nothing at runtime. Add nothing at dev time.** The trochoidal root is ~60 lines of stdlib `math` in `calc.py`; its proof is ~40 lines of stdlib in `tests/`; the hook decision is a Makefile target plus a `.pre-commit-config.yaml` edit. The 31-package closure stays at 31 (four milestones, zero runtime dependencies added).

| Question | Answer | Evidence |
|---|---|---|
| (a) `math` vs numpy/scipy | `math` suffices. numpy: no measured reason. scipy: **not in the shipped closure** and pruned from the image on purpose | 7,296-case sweep, 0 failures, slowest solve 0.19 ms; see (a) |
| (b) known-good reference | No free published point table or openly licensed true-trochoid generator was found. Build the reference from a closed form + an independent swept-cutter oracle (stdlib) + a one-off cross-check against freecad.gears (GPL-3.0, sharp corner only), none of it vendored | see (b) |
| (c) hook | Facts priced; recommendation: a sub-30 s pre-commit subset (measured 11–12 s warm, ~21 s with a cold mypy cache) **plus** the full `make verify` at pre-push. No dependence on an upstream knob (none exists, no open request) | see (c) |

### Corrections to the milestone brief (found while verifying)

1. **scipy is not in the pinned closure.** The brief says numpy and scipy are "present transitively via cadquery". True of the dev venv (scipy 1.18.1, `Required-by: cadquery`), false of the shipped system: `requirements.txt` has `numpy==2.5.3` and no scipy, and `docker/refresh-requirements.sh` lists `scipy` in `PRUNE` (~440 MB of `trame*`, `matplotlib`, `scipy`, `numba`... uninstalled in the image layer, `docs/architecture/packaging.md`). A `calc.py` that imported scipy would crash the image. [HIGH]
2. **The debt file's line reference is stale.** `COMMIT_TIMEOUT_MS = 30_000` is at `~/.claude/gsd-core/bin/lib/commands.cjs:3794` in gsd-core 1.16.0 (the debt file says `:3655`). 1.16.0 is also the npm `latest` (`npm view @opengsd/gsd-core version`, modified 2026-10-05). [HIGH]
3. **The shipped undercut warning is exact only for one cutter.** `calc.derive` uses `z_min = 2(1 − x)/sin²α`, a sharp rack with addendum 1.0·m. The project's own rack has dedendum 1.25·m (`rf = r − m(1.25 − x)`). With a tip radius ρ the onset is `z_min = 2(hf* − x − ρ*(1 − sin α))/sin²α` (derived below). The two agree to 6e-4 teeth at α = 20°, ρ* = 0.38 (17.0967 vs 17.0973), and differ elsewhere (table in (a)). [HIGH]
4. **The shipped default pressure angle is 25°, not 20°** (`params.py:38`, range 14.5–35). At 25° the standard 0.38·m cutter tip radius does not fit the rack (see Pitfalls feeding the roadmap). [HIGH]

---

## Recommended Stack

### Core Technologies (all already in the tree; nothing new)

| Technology | Version | Purpose in v0.4 | Why |
|---|---|---|---|
| Python stdlib `math` | 3.12 | trochoid sampling, form-radius bisection, closed-form undercut predicate, in `calc.py` | Same tool as `inv()`, `_involute_angle()` (60-step bisection, the precedent for "bisection not Newton", L08) and `_fillet_corner`. Keeps `calc.py` kernel-free and import-linter-clean. Solve cost 0.1–0.24 ms |
| cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1 | pinned (L34) | `model.py` turns the 2D point list into an `Edge.makeSpline`, as it does the involute flank | Unchanged; the kernel never sees the root-finding |
| pytest 9.1.1 + pytest-xdist 3.8.0 + pytest-cov 7.1.0 | installed | the trochoid proofs; the fast-subset hook | Already measured (L34). Nothing to add |
| pre-commit 4.6.2 | pinned by `pyproject` `>=4`, installed 4.6.2 | adds a `pre-push` stage | `stages: [pre-push]` is supported; behaviour verified in a scratch repo (see (c)) |

### Supporting Libraries — none added

| Library | Version | Purpose | When to Use |
|---|---|---|---|
| (none) | — | — | The "no new runtime dependency without a measured reason" rule is met by *not having a reason*: see the cost table in (a) |

### Development Tools

| Tool | Purpose | Notes |
|---|---|---|
| `make verify-fast` (new target, ~5 lines) | the sub-30 s commit subset | Reuses the existing recipes (`lint typecheck lint-imports no-fake-done`) and `make test PYTEST_ARGS="… --no-cov"`; no second definition of "passing" |
| `.pre-commit-config.yaml` edit | `default_install_hook_types: [pre-commit, commit-msg, pre-push]`; one new hook pinned `stages: [pre-push]` | Existing clones must re-run `.venv/bin/pre-commit install` once (as D-02 did for commit-msg); this clone's `.git/hooks` has `pre-commit` and `commit-msg` only [HIGH] |

## Installation

```bash
# Runtime / dev dependencies: none.
# Per clone, once, only if the pre-push stage is adopted:
.venv/bin/pre-commit install            # reads default_install_hook_types
```

---

## (a) The trochoidal root inside a pure-Python 2D outline

### What is being computed (derived here, not copied from a standard)

ISO 21771:2024 was not readable (paywalled; the iTeh sample is 14 pages without the root clauses) so no standard's equations are quoted. The construction below is the textbook rack-generation geometry, derived from first principles and then **checked three independent ways** (closed form, swept-cutter oracle, freecad.gears at ρ = 0). **ASSUMPTION:** its form radius equals ISO 21771's form diameter `d_Ff / 2` for a basic-rack-generated gear; confirm before the number is printed as "form diameter".

Setup, with the project's own conventions (`Profile` in `calc.py`; `s` = tooth thickness at the pitch circle, backlash included; θ measured from the space centre, tooth centre at π/z):

- Rolling line tangent to the pitch circle `r`. Cutter tip at depth `(hf* − x)·m` below it, `hf* = 1.25` (this is what `rf = r − m(1.25 − x)` already encodes). Tip corner radius `ρ`.
- Space width on the rolling line `e = πm − s`, `s = m(π/2 + 2x·tanα) − backlash` (identical to `calc.profile`).
- Corner centre in rack coordinates: `wC = −(hf* − x)·m + ρ`, `a = e/2 + wC·tanα − ρ/cosα`. (`a` does not depend on `x`: the corner sits where the rack puts it.)
- Rolling angle φ, `n(φ) = (sin φ, cos φ)`, `t(φ) = (cos φ, −sin φ)`, pitch point `I = r·n`.
  `C(φ) = (r + wC)·n + (a − rφ)·t` (corner-centre path, a prolate involute).
  **Root-curve point `E(φ) = C + ρ·(C − I)/|C − I|`** (the cutter-circle envelope: the point on the corner circle on the line from `I` through `C`).
- Range: `φ_tip = a/r` (E tangent to the root circle) down to `φ_flank = (a + wC·cotα)/r` (E meets the straight flank's foot point, tangent-continuous with the involute).
- Roll of that join along the line of action, `ξ_join = (m/sinα)·[ (z/2)·sin²α − (hf* − x − ρ*(1 − sinα)) ]`. **Undercut ⇔ ξ_join < 0 ⇔ `z < 2(hf* − x − ρ*(1 − sinα))/sin²α`** (ρ* = ρ/m).
- If undercut, the root curve is `E` from the root circle to the **form point** `φ_c`: the intersection of `E` with the true involute (roll ≥ 0). Solve `g(φ) = θ_E(φ) − (π/z − ψ(R_E(φ))) = 0`, `ψ(R)` = `Profile.half_angle(R)`, on `[φ_flank, φ_b]` where `R_E(φ_b) = r_b`; `g(φ_flank) < 0 < g(φ_b)`. If not undercut there is no root-find: the root curve ends at the join and the involute continues.

Corroboration of the rack geometry: it gives a maximum tip radius with a flat of zero width, `ρ*_max = (π/4 − 1.25·tanα)/(1/cosα − tanα)` = **0.4719 at 20°**, which matches the "ρ* = 0.471, the full-fillet hob" stated on standardsapplied.com [MEDIUM, commercial page]. The "17 teeth" folklore also falls out: ρ* = 0.38 (ISO 53's `ρ_fP = 0.38·m` with `c_P = 0.25·m`, quoted by engineersedge.com [MEDIUM]) gives `hf* − ρ*(1 − sin20°) = 0.99997` and `z_min = 17.0967` (the shipped sharp-rack formula reads 17.0973). [HIGH for the arithmetic]

### Does stdlib `math` suffice? Yes. What numpy/scipy would cost

| Option | Cost, measured on this host (2026-10-06, load 3–9 from sibling agents, so upper bounds) | Verdict |
|---|---|---|
| stdlib `math`, hand bisection | per-flank form-radius solve 0.09–0.24 ms; sampling 16 points negligible; import cost 0 (already imported) | **Use** |
| `import numpy` in `calc.py` | +33 ms import, +11 MiB RSS per process (13.0 → 24.1 MiB maxrss). `calc.py` is imported by the serving parent (`import spur.app`: 44.3 MiB) that L17's memory ceiling and the fourth import-linter contract keep kernel-free. numpy is in the closure (`numpy==2.5.3`, requires Python ≥ 3.12, PyPI 2026-09-06), so *no* new package, but a new import in the hottest module. Last-ulp differences between numpy and libm transcendentals are **ASSUMPTION** (not measured here); the fixture's byte-identity rule argues against finding out | Do not add |
| `import scipy.optimize` in `calc.py` | **not installable in the image** (pruned). In the dev venv: 250–270 ms warm import (8.5 s cold), 68 MiB RSS. Adding it means un-pruning ~hundreds of MB of the image and repinning (L12, `make lock`). `brentq` does not remove the need for a bracket, which is the hard part | Do not add |
| casadi / nlopt (in closure, for cadquery) | imported eagerly by cadquery, not by `calc.py` | Do not use as root-finders |

### Root-finding: how it behaves (the numbers behind "bisection, closed-form first")

A 7,296-case sweep at m = 1 (z 6–40, 60, 100, 200; x ∈ {−1, −0.5, −0.2, 0, 0.2, 0.5, 1}; α ∈ {14.5, 20, 25}; ρ* ∈ {0, 0.1, 0.25, 0.38, 0.5}; backlash ∈ {0, 0.1}) [HIGH]:

- 3,150 cases undercut by the closed form: the bracket `g(φ_flank) < 0 < g(φ_b)` held in **all 3,150**; 0 spurious cusps in the 4,146 not undercut; `R_E(φ)` strictly monotone on `[φ_flank, φ_tip]` in **all** 7,296; no cusp below the root circle; slowest solve **0.19 ms**.
- Why the closed form decides first: the radius-based bracket collapses as ξ_join → 0⁻. At z = 17, α = 20°, ρ* = 0.38 with x tuned so ξ_join = −2.9e-3 mm the solver found the cusp (R − r_b = 1.3e-7 mm); at ξ_join = −2.9e-5 mm the join sits 5e-11 mm above the base circle and the bisection returns "no bracket". Double precision cannot separate R from r_b below ~1e-15·R, which is a roll resolution of ~1e-7 mm, **the same order as the 1e-7 mm kernel tolerance L26 already measured**. So: decide undercut from the sign of `ξ_join` (exact algebra), run the bisection only when it is negative, and when the bracket degenerates treat the form point as the join (a ≤ 1e-7 mm effect). The threshold itself is to be set from a measurement in the phase, not from this file (L08): the two measured points above are the bracket for it.
- Numerical stability near the base circle: `acos(min(1, r_b/R))` (as in `Profile.half_angle`) has a square-root singularity at R = r_b. That is why bisection (sign-only) and not Newton, exactly L08's reasoning for `_involute_angle`. Nested bisection: one for `φ_b` (monotone `R_E`), one for `φ_c`; 60 halvings each.
- Degenerate rack: `a < 0` means the two corner centres cross (tip flat gone). Count in the sweep: 0 of 21 combos at ρ* ≤ 0.25, 7 of 21 at ρ* = 0.38, 14 of 21 at ρ* = 0.5. At ρ* = 0.38 every α = 25° case is degenerate (a = −0.0395·m) and no α = 20° or 14.5° case is. The formulas above assume `a ≥ 0`.

### Sampling density for the spline

Measured with the real `cq.Edge.makeSpline` (OCCT interpolation), maximum distance from the spline to a 20,001-point dense curve, root circle → form point, uniform in φ, m = 1 (deviation scales linearly with m) [HIGH]:

| Points N | 8 | 12 | **16** | 24 |
|---|---|---|---|---|
| z = 8 / 10 / 14, ρ* = 0.38 | 4.7–5.0e-4 mm | 1.1–1.2e-4 mm | **3.6–4.0e-5 mm** | 7.0–7.9e-6 mm |

The shipped involute flank (16 points, `i^1.5` spacing, `FLANK_POINTS`) measures **6.0e-5 mm (z=12, m=1)** and **1.0e-4 mm (z=19, m=1.75, the default gear)** by the same method. **Use N = 16 uniform in φ**: it is better than what the project already ships on its flank, and "match the existing flank's measured deviation" is a defensible rule that needs no new tolerance. One root curve serves every tooth (rotate by `2π/z`) and the other flank by mirror, so cost is one solve per build.

### Integration with the module boundaries

- **`calc.py`** gains pure functions returning plain `tuple[tuple[float, float], ...]` (never `cq` types): the cutter parameters, the closed-form undercut predicate, the form radius, the root-curve points. It still imports only `math`. `derive()` can print the form radius (that is a number someone cuts to, so it needs the proofs in (b)).
- **`model.py`** consumes the points exactly as `_outline` consumes the flank points. No new vendor type crosses its boundary (L35).
- **Coupled constants to revisit** (integration risk, not stack): `spline_start()` and `tip_chamfer_limit()` read where the involute spline starts; for an undercut gear that start becomes the form radius, and the tip chamfer's kernel limit `ra − spline_start` (L29, bisected to ~2 µm) must follow it. The existing warning `z_min = 2(1−x)/sin²α` should be re-stated from `ξ_join`, or retired once the trochoid is on.

| α | shipped `2/sin²α` | rack model hf* = 1.25, ρ* = 0.38 | ρ* = 0 | ρ* = 0.25 |
|---|---|---|---|---|
| 14.5° | 31.903 | 30.791 | 39.879 | 33.900 |
| 20° | 17.097 | 17.097 | 21.372 | 18.559 |
| 25° | 11.198 | 11.540 | 13.997 | 12.381 |

(x = 0. Computed from the closed form; the shipped formula under-warns at 25° and over-warns at 14.5° against the 0.38·m rack.)

---

## (b) A known-good reference for the test

Search result [LOW for the absence claim]: no freely downloadable published coordinate table of a rack-generated trochoidal root was found (searches 2026-10-06: academic hits are paywalled or abstract-only; ISO 21771, DIN 3960 and KISSsoft material are paywalled). So the reference is constructed from independent things, each justified without an external file.

| Candidate | Availability | Licence | Fit | Tolerance justification | Verdict |
|---|---|---|---|---|---|
| **Closed form: undercut onset** `ξ_join` / `z_min` | none needed | n/a | exact; agrees with the DIN/ISO-form `z_min` and with the 17-teeth rule | float algebra; assert the sign flip one tooth either side and at a tuned `x` one field step either side (the L33 pattern, 15-row style) | **Use (T1)** |
| **Swept-cutter "no-gouge" oracle** (stdlib, ~40 lines) | write it | project's own | independent of the envelope derivation: a point is on the cut boundary iff it lies on the cutter at its own rolling angle and strictly inside the cutter at no other. Two-sided, so it can fail | measured: root → form point, 41 points × 2,001 rolling angles: max penetration **−1.6e-11 mm**; points moved past the form point toward the join: min penetration **+3.9e-3 mm**. Eight orders of separation, so a bar anywhere between (e.g. 1e-9 mm) is not tuned to a pass. 0.07 s in pure Python. Its cusp equals the bisection's: at z = 10, θ_E = θ_involute(R) = 0.142588 rad to six decimals (R = 4.72560, r_b = 4.69846) | **Use (T2), primary** |
| **freecad.gears** `pygears/involute_tooth.py` | GitHub, pushed 2026-09-15 | **GPL-3.0** | a true trochoid, but the **sharp** cutter corner (ρ = 0) only; intersection with the involute by discrete polyline trimming, not a solve | at ρ = 0 my `E(φ)` equals its parametrisation to **1.8e-15 mm** in R and **1.1e-16 rad** in angle (z = 8, 10, 14; x = 0, 0.3) | **One-off cross-check (T3)**: run once, record the numbers with provenance in the test; do not import or vendor GPL code |
| A DXF from FreeCAD Gears workbench | needs FreeCAD to regenerate | GPL tool, output unencumbered | ρ = 0 only; polyline/B-spline sampled, so its own sampling error is the tolerance and is not documented | cannot be justified beyond "their sampling" | Reject. (`ezdxf` 1.4.4 is already in the closure and could read it, which is the only point in its favour) |
| `heartworm/py_gear_gen` | GitHub, last push 2020-07-30 | none declared (GitHub licence field empty) | circular root fillet, no trochoid | — | Reject |
| BOSL2 `gears.scad` (OpenSCAD) | GitHub, pushed 2026-10-02 | BSD-2-Clause | `_root_radius_basic`: simplified root, no rack-tip path | — | Reject as a trochoid reference |
| `CodiPixelPL/Gear-Gen` (MIT), `marmakoide/gear-profile-generator` (MIT) | GitHub | MIT | no trochoid evidence found; **not examined in depth** | — | Unverified, not needed |
| standardsapplied.com calculator | web | © All Rights Reserved | states z_min and ρ* = 0.471 | consulted only to corroborate two numbers (above); data not copied | Corroboration only |

**Recommendation: three tiers, no new files.**

1. **T1 closed form** pins *when* the root is a trochoid (exact).
2. **T2 swept-cutter oracle** pins *where* the root curve is. Run it on the **points the kernel will actually get** from `calc`, and again on the built solid's root edge (`Edge.positionAt`), so the proof is about the part and not only the maths. This is the same shape as L33's `_filleted_spoke_volume` ("a closed form that shares no code with the thing it checks").
3. **T3 cross-check** against freecad.gears at ρ = 0, numbers recorded once with the source file, commit and licence named.

L08 note: what no tier proves is parity with ISO 21771's printed form diameter; if `derive()` is to print "form diameter", say what it is (cutter-envelope intersection for a basic rack with tip radius ρ) or keep the warning and no number.

---

## (c) The hook decision: facts and pricing

### gsd side [HIGH unless noted]

- `COMMIT_TIMEOUT_MS = 30_000` at `commands.cjs:3794` (gsd-core 1.16.0, also npm `latest`); used by all three commit sites (lines 2441, 2631, 2787). No environment variable, no `.planning/config.json` key reads it (`grep` across `~/.claude/gsd-core` finds it only in `commands.cjs`).
- Upstream: issue open-gsd/gsd-core #3886 (closed) introduced the 30 s band ("the same band the push call uses"). `gh search issues` for "commit timeout" and "COMMIT_TIMEOUT_MS" returns only #3886. **No open upstream request for a knob exists** (2026-10-06): option (a) means filing one, and committing by hand until it lands and is released.
- gsd's only `git push` (`commands.cjs:2814`, the multi-repo branch-and-PR path) has a 60 s timeout; `.planning/config.json` has only `git.branching_strategy: phase`. **ASSUMPTION:** that path is not used here. Pushes in this repo are made by hand or by `gsd-ship` through the shell tool (HOW_TO_DEVELOP.md §6), where the tool's own default timeout (120 s foreground, 600 s max) applies: a warm 64 s pre-push fits, a cold "couple of minutes" run may not without an explicit timeout.
- gsd's own guidance is "hooks run by default; do NOT pass `--no-verify`" (`workflows/execute-phase.md:674, :757`, `references/git-integration.md:65`). A policy of `--no-verify` is not an option.

### pre-commit 4.6.2 `pre-push` semantics [HIGH: installed source + scratch repo]

- Valid stages include `pre-push`; since 3.2.0 stage names match git hook names (docs).
- `default_install_hook_types` defaults to `[pre-commit]`; `default_stages` defaults to **all** stages, so a hook without `stages:` runs in every installed stage. Both existing hooks are already pinned (`verify` → `pre-commit`, `no-skip-token` → `commit-msg`); the new one must be pinned `[pre-push]` too.
- `pre-push` runs **only when there is something to push** (`hook_impl._pre_push_ns` returns `None` otherwise). Scratch repo, two stages installed, local hooks writing a log: 2 commits → fast hook ×2, full hook ×0; first push → full ×1; a second push with nothing new → still ×1 ("Everything up-to-date"); new commit + push → fast ×3, full ×2; `git push --no-verify` → full unchanged; pushing a tag on an already-pushed commit → full unchanged.
- Filenames are irrelevant for `always_run: true` + `pass_filenames: false`. For pre-push pre-commit still `stash`es unstaged changes (`run.py`: `stash = not args.all_files and not args.files`), so the gate runs on the index plus untracked files, as the commit stage already does.
- Bypass: `git push --no-verify`, `SKIP=<hook-id>`. The wall is CI plus `make pr.land` (L22/L25), exactly as for commits.

### Pricing a sub-30 s pre-commit subset [HIGH, measured 2026-10-06, host load 5–9]

| Piece | Wall time | Notes |
|---|---|---|
| `ruff check .` | 0.06–0.10 s | |
| `mypy src tests docker bench scripts` | 0.23 s warm; **9.1 s with a cold cache** (`--cache-dir` fresh) | a fresh clone or a cleared `.mypy_cache` pays the 9 s once |
| `lint-imports` | 0.14 s | 5 contracts kept |
| `make no-fake-done` | 0.06 s | |
| the four static steps together | **0.59 s warm** | |
| pytest, all files **except** `test_model.py`, `test_pool.py`, `test_api.py`, `test_cli.py`, `-n 8 --no-cov` via `make test PYTEST_ARGS=…` | **11.0–11.1 s**, 617 tests (twice) | includes all of `test_calc.py` (where the trochoid maths will be tested) and `tests/regression` (the L26 fixture) |
| same slice, include-by-path (calc, records, bench, skip_tokens, pr_land, regression): `-n 8` / `-n 4` / `-n 0` | 8.0–8.7 s / 9.2 s / 21.6 s, 612 tests | xdist startup eats most of the gain on a small slice; `-n 8` is still right here |
| `tests/test_calc.py` + 4 other cheap files alone, `-n 0` | 3.9 s, 527 tests | the floor for a "maths only" subset |
| full `make verify` (L34) | 63.555 s warm, `-n 8` with coverage; ~224 s serial | the number the hook is up against |

**Subset ≈ 12 s warm, ≈ 21 s with a cold mypy cache**, so ≥ 9 s of headroom under 30 s even on a loaded host.

What it **loses**: `test_model.py` (201 items, ~74 % of pytest seconds: every kernel proof, so the new kernel-level trochoid tests would run only at pre-push/CI unless a small dedicated file is kept inside the subset), `test_pool.py` (the process-boundary tests, relevant to feature 2 of this milestone), `test_api.py`, `test_cli.py`; and **coverage gating**: `fail_under = 96` reads a partial run as a failure, which is why the Makefile's own comment says to pass `--no-cov` for a subset. Gate semantics stay "the full `make verify`": the subset is the same recipes with different arguments, not a second definition.

Selection mechanism: `--ignore=` paths cost **no file changes**; `-m` would need a registered marker (`--strict-markers` is on, none is registered) plus decorating tests, so it costs pyproject and test edits for no extra precision. Exclusion (not inclusion) is the safer default: a new test file runs at commit until someone names it heavy.

### Recommendation for the Lxx (human's call; amends L13)

Sub-30 s pre-commit subset **and** full `make verify` at pre-push. Why this and not the others: (a) alone changes nothing today and there is no upstream request to wait on; (b) alone removes every check from the commit boundary, which is the one the fixture rule (L26) most needs during the trochoid phase (the regression slice is inside the 11 s); (c) alone leaves the full gate unenforced locally until CI. Together, "one definition of passing" survives as `make verify`; the commit hook runs a named subset of its recipes. File upstream for the knob in parallel; do not block on it. Patching `~/.claude/gsd-core` is not an option (outside the repo, overwritten by `gsd-update`, `HOW_TO_DEVELOP.md` §6 already makes the same call for `ship.md`).

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|---|---|---|
| stdlib `math` bisection | `scipy.optimize.brentq` | Never here: scipy is pruned from the image; the bracket is the hard part, not the iteration |
| stdlib `math` | numpy vectorised sampling | If a profile of `derive()` ever shows the root curve dominating (it is 0.1–0.24 ms; keystroke path budget is far above that) |
| Built reference (T1+T2+T3) | A published point table / DXF | If one with a stated licence and tolerance turns up (ISO 21771 annex, a textbook table); add it as T4, do not replace T2 |
| Subset at commit + full at push | Pre-push only | If the human values zero commit latency over commit-time fixture checking |
| Subset at commit + full at push | Upstream `COMMIT_TIMEOUT_MS` knob | If gsd ships one and the full 64 s hook is acceptable per commit |

## What NOT to Use

| Avoid | Why | Use Instead |
|---|---|---|
| scipy anywhere under `src/spur/` | not in `requirements.txt`, pruned by `refresh-requirements.sh`, 250 ms / +55 MiB to import, un-pruning costs the image ~hundreds of MB | stdlib `math` bisection |
| numpy in `calc.py` | +33 ms and +11 MiB into the kernel-free serving parent for no measured gain; float-path divergence risk against the byte-identical fixture (ASSUMPTION, unmeasured) | stdlib `math` |
| vendoring or importing freecad.gears code | GPL-3.0 | run once, record numbers and provenance |
| `py_gear_gen` | no licence declared, circular fillet only | — |
| shapely / pyclipper / any polygon-boolean library for the oracle | a dependency for 40 lines of distance-to-trapezoid arithmetic | stdlib oracle in `tests/` |
| a DXF golden file | ρ = 0 only, polyline-sampled, tolerance unjustifiable | T1+T2 |
| pytest markers + `-m` for the subset | `--strict-markers` on; edits pyproject and test files for no gain over `--ignore` | `make verify-fast` with `--ignore=` |
| `pytest-timeout`, `pytest-testmon`, `pytest-picked` | not needed for a measured 12 s subset; each is a new dev dependency | — |
| lefthook / husky / a hand-written `.git/hooks/pre-push` | pre-commit already owns the hook chain, and a hand-written hook is invisible to `default_install_hook_types` | `pre-commit` stage `pre-push` |
| `--no-verify` as the workaround | contradicts gsd's own rule and L22's spirit | the subset |
| patching `COMMIT_TIMEOUT_MS` in `~/.claude/gsd-core` | outside the repo; overwritten at update; invisible to reviewers | upstream issue |
| ISO 21771's "d_Ff" as a printed label | clause unread (paywalled); parity unproven (L08) | say what the number is, or print none |

## Stack Patterns by Variant

**If the human picks "always-on for undercut gears":** pure `calc.py` + `model.py` change, no stack difference. Priced from the fixture: **5 of the 44 records (3 distinct gear sets: z=6, 14.5°, x=−0.6; z=6, 14.5°, x=−0.5; z=8, 25°, x=0)** are below the rack-model `z_min` for ρ* = 0.38 and also for ρ = their own `root_fillet`; the same three the shipped warning already flags. `make fixture.regen` in its own commit under its own `Lxx` (L26 D-03).

**If the human picks "default-off `GearParams` field":** one new field through the one-model walk (UI, API, CLI, schema); the fixture and every shared link stay byte-identical (L05). Again no stack change.

**If the cutter tip radius is the user's `root_fillet`:** the trochoid generalises the existing field (0 = sharp cutter, deepest cusp) and the default 0.5 mm at the default 1.75 mm module is ρ* = 0.286, which fits the 25° rack (`ρ*_max` = 0.318). **If it is a fixed 0.38·m:** it does not fit at 25° (`a = −0.0395·m`). Decide at discuss-phase; both are `calc.py`-only.

## Version Compatibility (checked against PyPI JSON 2026-10-06; installed in `.venv`)

| Package | Latest on PyPI (upload) | Installed | Notes |
|---|---|---|---|
| pre-commit | 4.6.2 (2026-08-10), Python ≥ 3.10 | 4.6.2 | `pre-push` stage in 4.x; stage names = hook names since 3.2.0 |
| pytest-xdist | 3.8.0 (2025-07-01) | 3.8.0 | `-n 8` knee measured in L34 |
| pytest-cov | 7.1.0 (2026-03-21) | 7.1.0 | `--no-cov` disables the report and the floor; `fail_under` applies only when `--cov` is active |
| pytest | — | 9.1.1 | |
| numpy | 2.5.3 (2026-09-06), Python ≥ 3.12 | 2.5.3 | in `requirements.txt`; imported by nothing in `src/spur` |
| scipy | 1.18.1 (2026-08-21), Python ≥ 3.12 | 1.18.1 | **dev venv only**; not in `requirements.txt`; pruned from the image |
| ezdxf | 1.4.4 (2026-05-14) | 1.4.4 | in the closure (cadquery imports it); would read a DXF golden at no dependency cost, not recommended |
| cadquery / cadquery-ocp | pinned (L34) | 2.8.0 / 7.9.3.1.1 | unchanged |
| gsd-core | 1.16.0 (npm `latest`, 2026-10-05) | 1.16.0 | `COMMIT_TIMEOUT_MS` still hard-coded |

---

## Findings that belong to FEATURES / PITFALLS but were found here

1. **Pressure-angle range vs the rack.** `ρ*_max(α)` at zero backlash: 0.597 (14.5°), 0.472 (20°), 0.318 (25°, the default), 0.110 (30°); at α ≈ 32.1° (`tanα = π/(4·1.25)`) even a sharp rack of dedendum 1.25·m has no flat, and the range runs to 35°. The trochoid must cap ρ (L03: capped and warned, never guessed) or fall back to the shipped radial root and say so; `a ≥ 0` is a precondition of the formulas, not an edge case. Backlash adds `backlash/2` to `a`.
2. **The shipped warning's z_min** is off against the 1.25·m rack except at 20°/0.38 (table in (a)); any re-statement must be proved, or the sentence stays.
3. **Two-flank interaction** at very low z or large ρ: the left and right trochoids can meet before the root circle; not exercised by the 7,296 cases (only one flank was solved). Needs an explicit test.
4. **Sample once per build, rotate per tooth**: keeps the `make bench.build` timings (heaviest composed row 29.42 s of 30 s, the margin finding in feature 2) unaffected by this feature in principle; **ASSUMPTION** until measured, since the spline is a new edge type in the boolean.

## Open questions (ASSUMPTIONs to surface)

- Whether the cutter tip radius is `root_fillet` or a constant fraction of the module (decides fixture price in practice and the 25° fit).
- Whether `E` below the base circle should stop at the form point for **non**-undercut gears with a root fillet larger than the analytic L09 one (L09 stays for the normal case per the milestone).
- ISO 21771 form-diameter parity (above).
- Whether a dedicated small kernel test file should sit inside the commit subset so the first trochoid build proof runs at commit time.
- gsd path assumption: spur never uses the multi-repo `git push` path.

## Sources

- Local, installed pre-commit 4.6.2 source: `pre_commit/commands/hook_impl.py` (`_pre_push_ns`), `pre_commit/commands/run.py` (`stash`, `from_ref`/`to_ref`), `pre_commit/clientlib.py` (stage names) [HIGH]
- pre-commit docs: https://pre-commit.com/ (stages, `default_install_hook_types`, `default_stages`, `--hook-type`, `SKIP`) [HIGH, cross-checked against the source above]
- Scratch-repo pre-push experiment, this session [HIGH]
- gsd-core 1.16.0 `~/.claude/gsd-core/bin/lib/commands.cjs` (lines 2441, 2631, 2787, 2814, 3794), `agents/gsd-executor.md:842`, `workflows/execute-phase.md:674,757`, `references/git-integration.md:65`; `npm view @opengsd/gsd-core version` [HIGH]
- https://github.com/open-gsd/gsd-core/issues/3886 (closed; introduced the commit timeout detection); `gh search issues` on "commit timeout" and "COMMIT_TIMEOUT_MS" [HIGH for presence, LOW for "no other request exists"]
- PyPI JSON: https://pypi.org/pypi/pre-commit/json, /numpy/json, /scipy/json, /pytest-xdist/json, /pytest-cov/json, /ezdxf/json (queried 2026-10-06) [HIGH]
- Repo: `requirements.txt`, `docker/refresh-requirements.sh` (`PRUNE`), `docs/architecture/packaging.md`, `pyproject.toml`, `Makefile`, `bench/RESULTS.md` (Phase 15 profile), `src/spur/calc.py`, `src/spur/model.py`, `src/spur/params.py`, `tests/regression/corpus.py` [HIGH]
- freecad.gears `pygears/involute_tooth.py` (GPL-3.0; undercut functions at the file's `undercut_function_x/y`): https://github.com/looooo/freecad.gears/blob/master/pygears/involute_tooth.py [HIGH for what the file computes, read directly; the web-summary quote of it was not trusted]
- https://www.standardsapplied.com/involute-gear-design.html (z_min with ρ*, "ρ* = 0.471 full-fillet hob"; © All Rights Reserved) [MEDIUM: commercial page, corroborated by the local derivation]
- https://www.engineersedge.com/gears/basic_rack_tooth_gear_profiles_din_867_13217.htm ("c_P = 0.25 m and ρ_fP = 0.38 m … specified in ISO 53") [MEDIUM: secondary quote of ISO 53, the ISO text itself was not readable]
- https://www-mdp.eng.cam.ac.uk/web/library/enginfo/textbooks_dvd_only/DAN/gears/generation/generation.html (trochoidal fillet exists; equations deferred to a PDF appendix not read) [LOW]
- https://www.sciencedirect.com/science/article/abs/pii/S0094114X25003179 ("Is the root fillet curve in involute gears trochoidal? A geometric reassessment", Mech. Mach. Theory): 403 on fetch, known only from a search snippet claiming a rack cutter's root is a prolate involute rather than a trochoid. Same curve, different name; no effect on the maths here [LOW]
- ISO 21771:2024 sample (https://cdn.standards.iteh.ai/samples/84949/f235930bfa0e4457a07b8a787a067045/ISO-21771-1-2024.pdf): does not contain the trochoid or form-diameter clauses [HIGH for that statement]
- BOSL2 https://github.com/BelfrySCAD/BOSL2 (BSD-2-Clause per GitHub API), py_gear_gen https://github.com/heartworm/py_gear_gen (no licence per GitHub API) [MEDIUM]
