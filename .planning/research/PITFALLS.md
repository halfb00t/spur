# Pitfalls Research

**Domain:** Adding a rack-cut trochoidal root, a same-slot timeout-cleanup fix and a commit-hook decision to an existing, shipped parametric spur-gear generator (`spur`, milestone v0.4 True Root)
**Researched:** 2026-10-06
**Confidence:** HIGH for everything measured in this repo (each such claim names its date and kernel; scratch scripts were not committed, so a plan that leans on a number must re-create the measurement inside the repo); MEDIUM for gear-geometry theory (derived and numerically cross-checked, literature only partly retrievable); LOW for anything marked ASSUMPTION.

How to read this file: phases are named by role, not number (the roadmap numbers from 17):

- **Phase A** — the debt phase: the same-slot race fix and the commit-hook decision (runs first, so every later commit lives under the hook decision).
- **Phase B** — trochoid maths in `calc.py`: pure `math`, no kernel, proven against an independent oracle.
- **Phase C** — outline and kernel integration (`model._outline`), landed dark.
- **Phase D** — the root-mode decision's consequences: flip, fixture regeneration under its own `Lxx`, warning text, README, records.

One correction to the brief before the pitfalls: `BuildPool` has **no lock**. `recreate_for` is a plain synchronous method and `_run_with_timeout`'s `except TimeoutError` branch never awaits, so the identity check is atomic only because everything runs on one event-loop thread. The race-fix pitfalls below are written against that fact, not against a lock that does not exist.

---

## Critical Pitfalls

### Pitfall 1: "Undercut", "root below the base circle" and "the cutter's form circle" are three different predicates, and the fixture straddles them

**What goes wrong:**
The milestone says "trochoid below the base circle, analytic fillet for the normal case" and "always-on for undercut gears". The repo already holds two non-equivalent predicates: `derive()`'s warning uses `z < z_min = 2(1-x)/sin²α`, while the radial/lead-in segment in `_outline` exists whenever `rf < rb`, i.e. `z < 2(1.25-x)/(1-cos α)`. They select very different sets. Measured on the committed fixture (2026-10-06, `tests/regression/pre_v0_2.json`, 44 records, 39 built): **3 built records are undercut by the warning's definition** (z=6 at 14.5° x=-0.6, z=6 at 14.5° x=-0.5, z=8 at 25°; 5 records carry the warning text counting the two mate-only copies), but **23 of the 39 built records have `rf < rb`**, including the README default gear (19 teeth, m 1.75, 25°: `rf` 14.4375 mm, `rb` 15.0674 mm) that nearly every shared link without a `teeth` override builds. A plan that keys the trochoid on "rf < rb" rewrites the default part; one that keys it on the warning's `z_min` touches 3 built rows. A third reading (use the trochoid wherever the cutter's form circle lies at or below where the analytic chord currently starts) selects yet another set.

**Why it happens:**
L10 and the warning text say "undercut" while the code's radial segment is a base-circle property. The word is used for both. `z_min` also silently assumes a cutter whose straight flank reaches 1.0 m below the pitch line.

**How to avoid:**
- Decide the predicate first, as a pure function in `calc.py` derived from the *same cutter constants the geometry uses* (rack addendum 1.0 m, dedendum 1.25 m, tip radius, shift, backlash), never from a second hand-typed formula. Check both sides of the boundary one tooth step either side (the L33 "one step either side of the crossing" pattern).
- Re-derive `z_min` from the cutter. ISO 53:1998 gives hfP 1.25 m, haP 1.0 m and a root-fillet radius of 0.38 m (LOW, web summary of the standard); with 0.38 m the straight flank ends at depth `1.25 m - ρ(1 - sin α)`, which is exactly 1.0 m only at α = 20° (0.38 × (1 - 0.342) = 0.25). The repo's `z_min` is therefore exact at 20° and an approximation at the project default 25° and across its 14.5° to 35° range. Either state that, or compute the boundary from the actual cutter.
- Expect a discontinuity at the switch (measured, ρ = 0.38 m, 20°): the analytic-fillet root gap printed for z=17 is 2.052 mm against about 0.28 mm for the cutter-generated gap — a cliff in root shape between adjacent tooth counts. The predicate's boundary is a visible step in the product; the human should see that number at discuss-phase.

**Warning signs:**
Fixture rows that move that the plan did not list; the default gear's face/edge counts (172 faces / 490 edges with the bore chamfer, L26) changing; a phase summary that says "undercut" without a formula.

**Phase to address:** Phase B (the predicate) with the human's root-mode decision made before it; Phase D (what the fixture regen moves).

---

### Pitfall 2: Always-on silently changes shared links (L05) and is structurally incompatible with a green pre-commit hook plus L26's one-commit rule

**What goes wrong:**
Two separate collisions:
1. CLAUDE.md standing rule 2: a parameter the user did not set must never silently change the part. Always-on for undercut gears rebuilds every old low-tooth-count link as a different solid. L33 already refused an outline re-cut for exactly this reason ("changes the part of every shared link that sets a large profile shift or root fillet (L05)").
2. L26 D-03: the fixture changes only via `make fixture.regen`, in its own commit, never in a feature commit; and the pre-commit hook runs the full `make verify` with no bypass, so "a failing commit cannot exist" (v0.1 retrospective). A feature commit that changes the outline turns the affected fixture rows red, so the hook refuses it; a fixture-regen commit made first is red against the old code. There is no ordering of two plain commits that satisfies both rules.

**Why it happens:**
L26 was written for kernel bumps and small contract changes where the regen could precede or follow trivially; nobody has yet shipped a deliberate geometry change under it.

**How to avoid:**
- Land the trochoid **dark**: the maths and the outline branch exist, are exercised by their own tests through an explicit argument, and are not selected by any default. The flip is a separate commit containing only the one-line switch, the `make fixture.regen` output and the new `Lxx` that says what moved and why — the only commit allowed to touch `tests/regression/pre_v0_2.json`. Verify with `git diff --exit-code tests/regression/pre_v0_2.json` after every other task, as 07-02 did.
- If a default-off `GearParams` field is chosen, the fixture must stay byte-identical (the fixture records carry explicit params only, so a new defaulted field does not appear in them) and the flip commit does not exist. State which scenario applies in the plan, with the count of fixture rows that move (3 built records for the warning's predicate, 23 built for `rf < rb`, per Pitfall 1).
- If always-on is chosen by the human, keep an explicit value that reproduces the old part so a user can still rebuild it, and say in `Lxx` how many shared links change in kind (unknown in the wild; ASSUMPTION that no telemetry exists).

**Warning signs:**
A feature commit whose diff lists `pre_v0_2.json`; a plan task "regenerate fixture" inside a code-change plan; a test that is deselected or `xfail`ed to get a commit through.

**Phase to address:** Phase D (decision and sequencing), with Phase C obliged to land dark.

---

### Pitfall 3: Wrong cutter frame — backlash, shift and rolling direction must reproduce the model's own flank, or the fillet starts off the involute

**What goes wrong:**
The existing flank is `half_angle(rho)` with `psi_p = s/(2r)` and `s = m(π/2 + 2x tan α) - backlash`. A rack generated from "standard" values (m, α, x, 1.25 m) that forgets how backlash enters places the fillet's junction off the model's involute. Measured in a scratch prototype (2026-10-06, default gear, backlash 0.10): a cutter built without backlash leaves a **0.046 mm step** at the junction; the kernel closes a wire only if endpoints agree within about 1e-7 mm (Pitfall 7). A mirrored rolling direction puts the fillet on the opposite flank of the gap: the same junction test fails by a large angle.

**Why it happens:**
The model folds backlash into the tooth angle, not the cutter. The matching cutter is a rack whose tooth thickness on the rolling line is `e0 = π m/2 - 2 x m tan α + backlash`, displaced by `x m`, with rolling point `P = (r - d)·n̂ + (λ - rφ)·t̂`. With this convention the prototype's junction agrees with `half_angle` to **4.9e-17 rad** (z=19, 25°) and 6.9e-18 rad (z=30, 20°), at backlash 0 and 0.10 alike. The sign of `rφ` (and therefore which of `φ_flank`, `φ0` bracket the fillet) is easy to flip.

**How to avoid:**
- Derive the cutter from the model's flank, then **assert the junction against `Profile.half_angle`** for both flanks as the first test of Phase B: position error at the form point below 1e-9 mm and tangent direction agreement (non-undercut z). That one test catches wrong sign, missing backlash and a wrong `x` convention at once.
- Keep the backlash convention in one place (a single `cutter(p)` function returning `e0`, `d_tip`, `ρ`); never recompute it at call sites.

**Warning signs:**
A step of the order `backlash/2` at the form point; the trochoid test passing at backlash 0 only; the outline wire reporting `IsClosed() == False`.

**Phase to address:** Phase B.

---

### Pitfall 4: Treating the junction as tangent for every gear — it is tangent only when the gear is not undercut; for undercut it is a crossing that must be found

**What goes wrong:**
For `z >= z_min` the cutter's tip-arc envelope joins the straight-flank involute tangentially at the form circle (measured: z=19, 30 above). For undercut gears the envelope crosses the involute at a shallow angle (a real cusp). Using the arc's flank-side end `φ_flank` as the junction for an undercut gear lands off the involute: measured angle gap −2.4e-3 rad (−0.024 mm) at z=12/20°, −5.7e-3 rad (−0.037 mm) at z=8/25°, and −0.50 rad (−3.7 mm) at z=6/14.5°. Worse, the arc-envelope parameter range `[φ_flank, φ0]` runs far past the crossing: for z=6, 14.5°, x=-0.5 the curve reaches r = 10.27 mm while the tip circle is `ra` = 6.125 mm — a spike outside the gear if sampled whole.

Where the crossing actually sits (ρ = 0.38 m, same session): r_cross − rb = 23 µm (z=12, 20°), 27 µm (z=8, 25°), 48 µm (z=10, 20°), 234 µm (z=6, 14.5°), about 0.5 mm (z=6, 14.5°, x=-0.6). At exactly `z_min` (z=17, 20°) the curves touch and a sign-change search finds **no crossing** (a double root).

**Why it happens:**
"Trochoid below the base circle" is shorthand. The envelope trims the involute from above, not at `rb`, and the trim point depends on the cutter.

**How to avoid:**
- Find the crossing of the fillet curve with the involute by bracketing and bisection on the rolling angle (the repo's L08 precedent: `centre_distance` and `_involute_angle` use bisection because it has no failure mode that returns a plausible wrong answer — scipy is installed in the venv but is not a declared runtime dependency and `calc.py` is stdlib-only). Treat the near-tangent case explicitly: at or within a stated epsilon of `z_min` the junction is the tangent point, not "no root".
- Where no honest junction can be computed, follow L08: warn and keep the old radial root; never return a plausible number.
- Tests: tangency (position and direction) asserted only for `z >= z_min`; for undercut rows assert the crossing radius against the brute-force oracle of Pitfall 5, and assert that no fillet point lies above `ra` or beyond the crossing.
- `spline_start` (and so `tip_chamfer_limit`'s third limit, `TIP_CHAMFER_MARGIN`) must read the new start radius from the same function the outline uses; re-measure the chamfer cap for undercut rows (L29).

**Warning signs:**
A fillet sampled over its whole parameter range; r_max above `ra`; a test that asserts G1 continuity on an undercut row; an empty root-find result near `z_min`.

**Phase to address:** Phase B (maths and tests), Phase C (spline start).

---

### Pitfall 5: Using the cutter-tip-centre path instead of the tip-surface envelope, and having no independent oracle

**What goes wrong:**
The path of the tip-arc centre is a prolate involute (the centre sits `d_c` below the rolling line). The part's boundary is the envelope of the arc, not that path: a point at distance ρ from the centre along the line through the instantaneous pole `M` (the rolling-line contact point). Using the path itself leaves the root ρ too deep and misplaced; offsetting it perpendicularly by ρ is not the envelope either and, where ρ exceeds the path's radius of curvature, produces swallow-tail loops. Literature wording is itself inconsistent ("trochoid" versus "prolate involute"; a 2025 paper asks "Is the root fillet curve in involute gears trochoidal?", abstract not retrievable, 403), so a plan that cites "the trochoid" without fixing the construction invites the wrong curve.

**Why it happens:**
Both curves are loosely called "the trochoid", and a hob with a transition edge (a "secondary involute at a lower pressure angle", Gear Solutions form-diameter article, MEDIUM) is a different cutter again.

**How to avoid:**
- Fix the construction in the plan: envelope `F(φ) = C(φ) + ρ·(M - C)/|M - C|` taken on the side away from the cutter, with `φ` between the root-circle tangency `φ0 = λ_c/r` and the flank-tangent end `φ_flank = (λ_c - d_c/tan α)/r`.
- Write the oracle so it shares no code with production (the v0.3 pattern: `_filleted_spoke_volume` sharing nothing with `_fillet_corner`): for sampled fillet points, `min over φ' |C(φ') - F|` must equal ρ to the bar and never fall below `ρ - bar`. This clearance test also catches a swapped side and any loop, and it is independent of how the production curve is parametrised.
- Cross-check one case against a closed form where one exists. ISO 6336-3 defines the critical-section radius `ρ_F` and chord `s_Fn` for rack-generated roots at the 30° tangent point (LOW: formula text could not be retrieved — the public PDF previews are unreadable here — so the plan must obtain it from a licensed copy or a documented implementation before relying on it).

**Warning signs:**
A fillet whose lowest point sits at `rf - ρ` or at `rf + ρ`; an "offset by ρ" helper in the production code; an oracle that calls the production helper.

**Phase to address:** Phase B.

---

### Pitfall 6: The printed numbers drift from the cut part (L08) — root thickness, root gap, the root diameter and the cutter's own feasibility

**What goes wrong:**
`_tooth()` prints `root_thickness` and `root_gap` "measured on the root circle" under a radial-flank idealisation. A rack-cut root has a very different tooth at that circle. Measured (prototype, ρ = `root_fillet` 0.5 mm unless noted): default gear printed gap 1.609 mm against 0.149 mm between the cutter's fillet tangent points; thickness 3.166 mm against 4.625 mm. z=12/20°: gap 2.008 against 0.440, thickness 2.345 against 3.912. z=8/25°: gap 1.670 against 0.118. Anything that prints `root_thickness`/`root_gap` for a trochoid root without recomputing it from the geometry the kernel cuts breaks L08 ("a number someone will cut metal to").

A second drift: the cutter must be feasible. The tip-land half-width is `λ_c = e0/2 - d_tip·tan α - ρ(1 - sin α)/cos α`; when `λ_c < 0` the two corner arcs overlap, the cutter has no flat tip, and the deepest point is shallower than `rf`, so printed `root_d = 2·rf` overstates the depth. Measured at the project default 25° (m 1.75): ρ = 0.38 m = 0.665 mm gives `λ_c = -0.019 mm`; the largest feasible ρ is 0.635 mm (0.363 m); z=8/25° is also negative at 0.665 mm. `root_fillet` is allowed 0 to 3 mm over modules 0.2 to 10 (up to 15 m at m 0.2), so an unchecked mapping of that field to the cutter radius makes cutters that cannot exist.

**Why it happens:**
The fillet field was a circle radius in a 2D outline, not a cutter dimension. Mapping it to ρ gives it a new meaning; keeping a constant ρ ignores a field the user set.

**How to avoid:**
- Decide what `root_fillet` means in trochoid mode and say so in a warning when it is ignored or capped (L03: cap and warn when no explicit conflict, a `422` only for a direct conflict; the repo's "X is ignored" sentence pattern exists for hex bore, spokes and holes).
- Compute `root_thickness`/`root_gap` (and any new root figure) from the same function the outline uses, at a stated radius; if no honest measurement radius exists, report `null` plus a warning for trochoid mode rather than the radial-flank number.
- Cap ρ so `λ_c >= 0` and warn with the capped value, using the print-resolution rule already in `derive()` (compare at the 3 dp printed).
- `root_fillet = 0` is legal today and builds a sharp-root part; the trochoid mode must keep that case valid (the corner path meets the root circle at a kink), not crash on `ρ = 0`.
- Re-measure `derive()`'s cost: a 60-step bisection of the junction condition measured 73 µs per call against `derive(default)` at 20.4 µs on 2026-10-06 (host load about 6.8, so the docstring's 11.5 µs is already stale). That is acceptable per keystroke but the docstring must carry the new measured figure (CLAUDE.md: measured, not estimated).

**Warning signs:**
`root_gap` identical for trochoid and analytic mode; a test that pins `root_thickness` from the old formula; negative `λ_c` anywhere in a parameter sweep.

**Phase to address:** Phase B (feasibility and caps), Phase D (printed fields, README, warning text).

---

### Pitfall 7: Sampling and kernel handling — the spline blows up, the wire opens, and `isValid()` is not enough

**What goes wrong:**
Measured on cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1 (2026-10-06):
- **Junction gaps.** `Wire.assembleEdges` plus `Face.makeFromWires` plus `Solid.extrudeLinear` raise nothing for an endpoint gap of 1e-6 mm or more; the wire is simply open (`IsClosed() False`) and the solid invalid. Gaps up to 1e-7 mm close and stay valid.
- **Duplicate or near-duplicate spline points** (1e-9 apart) raise `Standard_Failure` with an empty message; `_build_checked` relabels any kernel exception "try smaller fillets or chamfers", a wrong remedy here.
- **Uneven spacing.** A cubic interpolation through points spaced 1e-3 mm beside 2.0 mm swung to a 538 mm excursion yet produced a face that passed `isValid()` with volume 347.9 against 21.4 for the clean curve. A self-crossing wire (a loop) gives `isValid() False` and a negative volume (-7.1), which the existing check does catch.
- The existing involute flank is accurate: 16 samples at `(i/15)**1.5` radial spacing deviate at most 0.13 µm from the exact involute (z=8/25°), 0.004 µm on the default gear. That is the floor to beat.

**Why it happens:**
A trochoid parametrised uniformly in `φ` bunches points where its speed collapses (near cusps and where the envelope turns), and radius-based sampling like the flank's fails because the fillet's radius is not monotone near the crossing.

**How to avoid:**
- Sample by arc length with a bounded spacing ratio; reject (BuildError or fall back with a warning) any outline with a spacing ratio above a measured limit.
- Compute the junction point once and use the **same `Vector` objects** for the end of one edge and the start of the next; never recompute it per edge.
- Add structural guards that do not depend on `isValid()`: every edge's bounding box lies inside the annulus `[rf - tol, ra + tol]`, each tooth's outline has no self-intersection (the cheap segment test used in the prototype is enough for a pure-maths check), and the pre-existing `Volume()` check against the closed-form tooth area.
- Measure the new spline's midpoint deviation from the analytic curve per tooth count class and assert it, the way the flank's 0.13 µm was measured; do not assume it.
- Keep `FLANK_POINTS` semantics: the 1.5 exponent exists because the involute angle behaves like `(r - rb)^1.5` at the base circle; the new start radius (the crossing, tens of µm above `rb`) must keep that clustering near `r0`, and curvature radius of the involute is `sqrt(r² - rb²)` (zero at `rb`), so do not sample the involute flank itself at `rb`.

**Warning signs:**
`BuildError: Geometry kernel failed (Standard_Failure)`; a valid solid whose volume disagrees with the closed form; per-edge bounding boxes outside the annulus; slow builds on low-tooth gears.

**Phase to address:** Phase C.

---

### Pitfall 8: A tolerance picked to make the reference comparison pass, instead of one the reference actually supports

**What goes wrong:**
The ticket says "proven against a known-good undercut profile". No such reference is in the repo, and the candidates have unequal precision. Form-diameter methods in the literature quote relative errors under 0.1 % (0.05 % for common gears) for their own approximations (Gear Solutions article, MEDIUM): on a 20 mm form circle that is up to 20 µm, so an oracle built on published form diameters cannot support a bar of 1 µm. A DXF from another generator carries its own point density and its own cutter assumptions (tip radius, any transition edge or protuberance, backlash placement); a mismatch in those assumptions looks like a tolerance problem and gets "fixed" by loosening the bar. ASSUMPTION: no suitable known-good DXF has been identified yet.

**Why it happens:**
L33's lesson already applies: a bar is set from a measured gap with the gap recorded, never tuned toward a pass; and "tolerance carries the number that set it" (L26).

**How to avoid:**
- Pin the reference's cutter (ρ, haP, hfP, α, backlash, shift) in the test before comparing a single point; if the reference states none, it is not a reference.
- Set the bar from two recorded numbers: the floor (the model's own spline error, the kernel tolerance 1e-7 mm, Pitfall 7) and the reference's own stated resolution; write both beside the assertion. If the floor is above the reference's resolution the test proves less than it claims, and the plan must say so.
- Add a tripwire like L33's: move the cutter radius by a small stated amount and prove the assertion goes red; a bar that cannot discriminate is not a bar.
- Prefer two independent oracles: the brute-force clearance oracle (Pitfall 5, high precision, shares no code) for geometry, and a published or standard closed form for at least one scalar (Pitfall 5, `ρ_F`) so the tool is anchored outside its own derivation.

**Warning signs:**
A tolerance written without a measured gap beside it; a reference with no stated cutter; a test that passes at 1e-2 mm and "needs" 1e-1.

**Phase to address:** Phase B (oracle and bars), Phase D (the `Lxx` records them).

---

### Pitfall 9: The identity check is atomic only while the block stays synchronous, and it misses the shutdown path

**What goes wrong:**
Reproduced on 2026-10-06 against the committed `BuildPool` (scratch script, one worker, timeout 1.0 s, a sleeping task as the build, worker pre-warmed): two same-slot requests launched `gap` seconds apart gave, over 4 runs each:

| gap between requests | first | second |
|---|---|---|
| 0 s, 0.5 ms, 2 ms, 5 ms | `BuildTimeout` | `AttributeError: 'NoneType' object has no attribute 'values'` in 4/4 |
| 20 ms | `BuildTimeout` | `AttributeError` in 3/4, `BrokenProcessPool` in 1/4 |
| 100 ms | `BuildTimeout` | `BrokenProcessPool` in 4/4 |

This confirms the debt file's diagnosis (the second branch reads `executor._processes` after the first's `recreate_for` shut the executor down) and bounds the window: it is the few milliseconds before the executor manager thread flags the pool broken. Beyond it the sibling arrives as the documented `503 pool_broken`. A second route to the identical `AttributeError` exists: `BuildPool.shutdown()` (called from the lifespan `finally`) runs `shutdown(wait=False)` on every executor **without replacing it**, which sets `_processes = None`; an in-flight request that then times out reproduces the crash while `self._executors[i] is executor` still holds. Measured the same session: `_processes = None`, slot identity unchanged, request ends in `AttributeError`. Reachability through uvicorn's graceful shutdown is ASSUMPTION; the direct call is measured.

An identity-only guard (the fix the debt file suggests) closes the first route and leaves the second; and after `shutdown()` `recreate_for` would still build a fresh executor that nobody shuts down, which leaks the multiprocessing semaphores the resource-tracker debt (below) already concerns.

**Why it happens:**
There is no lock; atomicity comes from "no `await` between the check and the act". A reasonable-looking improvement — awaiting the process's death before replacing the executor, to avoid an orphan — introduces the await and reopens the window.

**How to avoid:**
- Guard on both facts: the executor is still the live one for its slot, **and** its `_processes` is not `None`. Add a `_closed` flag set by `shutdown()` so `recreate_for` refuses to build a replacement after shutdown.
- Keep the terminate-and-replace block synchronous and say so in a comment that names this failure; add a test that fails if an `await` is inserted (two tasks, same slot, gap 0).
- Do **not** swallow the error with a broad `except`; narrow the guard so a genuine third defect still surfaces.
- `_processes` is typed non-optional in typeshed and `make no-fake-done` refuses new suppressions under `src/spur/` (L35), so the guard must be typed honestly (an explicit local `procs = executor._processes` check), not silenced.

**Warning signs:**
`AttributeError` or `RuntimeError: dictionary changed size` near `_processes`; `workers_replaced` rising by 2 for one incident; a `worker.replaced` record count different from the incident count.

**Phase to address:** Phase A.

---

### Pitfall 10: Tests for the race that depend on the window flake on a loaded 4-vCPU runner, and the new tests land on a file with known flakes

**What goes wrong:**
The window above is a thread-scheduling property of this idle-ish M2 Max (load average about 6.8 at measurement). On GitHub's 4-vCPU `ubuntu-latest` with `pytest -n 4 --cov` the manager thread competes with every other xdist worker; the window can be wider or narrower (ASSUMPTION, not measured). `tests/test_pool.py` already documents one CI-only failure class: `proc.join(); assert not proc.is_alive()` failed on 4 of 5 GitHub runner attempts (runs 36116930241, 36117030280, 36118554588) because the manager thread and the test race `os.waitpid`, and the fix is to join the manager thread and assert `proc.exitcode == -signal.SIGTERM`. Separately, the active nice debt `2026-10-06-resource-tracker-flake-fails-the-gate.md` (one occurrence, cause unmeasured) lists this very file's shutdown path under "revisit when ... is next touched", so editing it triggers that item. The coverage-flush debt (`pool.py` lines lost in serial `--cov` runs) can also misread new coverage.

**How to avoid:**
- Make the decisive test **deterministic**: inject a stale executor (replace `pool.executor_for`, or call the branch with an executor already shut down) and assert `BuildTimeout`, with no sleep-based ordering. Keep one timing test at gap 0 that asserts "never `AttributeError`; the sibling is `BuildTimeout` or `BrokenProcessPool`" — both are documented `503` types — not one exact type.
- Pre-warm the worker (`executor.submit(os.getpid).result()`) before arming a short injected timeout, as the existing tests do, so spawn plus the `_warm` kernel import never counts against it.
- Never assert process death with `proc.join()`/`is_alive()`; reuse the manager-thread join plus exit-code pattern.
- Do not change the existing `test_four_same_slot_requests_all_refuse_without_cancellation` expectations (its 0.5 s gap is outside the window by design).
- Before calling the tests stable, run the new tests repeatedly under the gate's own invocation (`-n 8 --cov`, then `-n 4`) and record the count and the outcome; the repo's precedent is 0/18 locally in the test comment. If the resource-tracker warning recurs, capture the whole log as that file asks; add no blanket `ignore::pytest.PytestUnraisableExceptionWarning`.

**Warning signs:**
A test that passes locally and fails only in CI; a `ResourceTracker called reentrantly` warning; `sleep()` used for ordering.

**Phase to address:** Phase A.

---

### Pitfall 11: Orphaned workers and the memory ceiling

**What goes wrong:**
Skipping `terminate()` for a stale executor is safe only because each executor owns exactly one process and the replacer already terminated it. Cases that break that: the first handler was the `BrokenProcessPool` branch (process already dead, fine), a worker that is slow to honour SIGTERM (the code sends SIGTERM only, never `kill()`, and a worker's death is not awaited), or a replacement built after `shutdown()` (Pitfall 9). An orphaned worker is a live OCC solid: L17 measured about 810 to 870 MiB baseline per extra worker, and `mem_limit: 4g` is N=2's 2878.5 MiB peak × 1.3 = 3742 MiB rounded up, so one orphan consumes nearly all of the headroom (arithmetic on L17's own numbers; not measured as an orphan).

**How to avoid:**
- After the fix, a test asserts the worker PID count returns to N after a same-slot double timeout (psutil is not a runtime dependency; use the `_processes` handle and exit codes the existing tests already read).
- Do not add `kill()` escalation or a wait in this change; if SIGTERM proves insufficient that is a separate, measured item.

**Warning signs:**
`/api/health` `workers_replaced` correct but resident memory above the sweep's N=2 peak; stray `multiprocessing.spawn` processes after a test run.

**Phase to address:** Phase A.

---

### Pitfall 12: Changing the timeout clock, or masking the margin finding behind the fix

**What goes wrong:**
`asyncio.wait_for(future, timeout)` starts its clock when the request is submitted, so queue wait on a shared slot counts against the 30 s (SC3: both requests on a slot recorded `duration_ms` 30002 to 30004). That is current behaviour, flagged as an ASSUMPTION in the debt file and measured by SC3. A "fix" that restarts the clock at execution would let a request wait several budgets (four admitted builds on one slot) and silently redefine `SPUR_BUILD_TIMEOUT`. Separately, once the crash is fixed the worst composed row (29.42 s alone, 0.58 s of margin, timed out at 30004 ms under contention) becomes a clean `503 timeout`: client dashboards show an ordinary documented failure and the margin problem disappears from view while remaining true.

**How to avoid:**
- Keep the fix narrow: no change to when the clock starts, to `SPUR_BUILD_TIMEOUT`, or to `MAX_QUEUED_BUILDS`. A test pins that a request queued behind a slow sibling still times out at its own submission-relative deadline.
- Record the margin decision in its own `Lxx` (raise the timeout, cap the row, or record the limit), with the measurement behind it, and do not retire the debt file on the race fix alone: the debt names both findings.
- The cheap reproduction above (milliseconds, no kernel) is enough to prove the fix; the ten-identical-worst-row bench is a confirmation that needs the quiet-host gate the retrospective says was reached in 2 of 5 Phase 13 sessions. Surface that to the human rather than blocking the fix on it.

**Phase to address:** Phase A.

---

### Pitfall 13: A pre-push hook removes the guarantee the repo's workflow relies on, and pre-push does not verify what you think

**What goes wrong:**
Moving `make verify` from pre-commit to pre-push (option b) means commits made in the meantime are unverified; the retrospective's pattern "TDD RED and GREEN land in one commit: the pre-commit hook runs the full `make verify` with no bypass, so a failing commit cannot exist" no longer holds, `git bisect` can land on a red commit, and a red gate at push surfaces after many task commits. Read from the installed pre-commit 4.6.2 source (`pre_commit/commands/hook_impl.py`, `_pre_push_ns`): the pre-push hook runs **once per `git push`**, not once per ref; it builds its from/to refs from the **first** stdin line that is not a delete; a delete-only push, or one with nothing new, runs no hook; and with the `verify` hook's `pass_filenames: false`/`always_run: true` the ref range is irrelevant, so it verifies whatever is checked out (pre-commit stashes unstaged changes first, `run.py` `staged_files_only`), not the commit being pushed. `git push origin <sha>:refs/heads/x` from a different checkout is verified against the wrong tree. `pre-commit install` is also per clone and per hook type: the current `.git/hooks` holds only `pre-commit` and `commit-msg`, so a clone that did not re-run the install gets no pre-push gate at all, silently.

**How to avoid:**
- If chosen, add `pre-push` to `default_install_hook_types`, pin the hook's `stages: [pre-push]` (the config already records that an unpinned hook runs once per installed stage), add a one-line "re-run `pre-commit install`" check to the how-to, and keep CI and `make pr.land` as the wall.
- Amend L13's "one definition of passing in three places" explicitly; state which commits can now be red.
- Compare with the cheaper option (Pitfall 14) before deciding.

**Phase to address:** Phase A.

---

### Pitfall 14: A sub-30 s pre-commit subset that drifts from CI's definition of passing

**What goes wrong:**
A hand-maintained second list (lint, types, boundaries, scan) beside `make verify` will drift: the next gate stage added to one is not added to the other, and "one definition of passing" (L13, amended by L34) becomes two. Priced from the repo (2026-10-06, load average about 6.8): ruff 0.03 s, `lint-imports` 0.10 s, `mypy --cache-dir <empty> src tests docker bench scripts` 9.12 s cold-cache and 0.20 s warm, the unfinished-work scan 0.02 s (P1 profile). About 9.5 s cold, comfortably under 30 s; an OS-cold page cache (the "couple of minutes" the hook file mentions applies to loading OpenCascade for pytest, not to mypy) is not measured here (ASSUMPTION).

**How to avoid:**
- Make the subset a **prefix by construction**: a `verify.fast` target (`lint typecheck lint-imports no-fake-done`) and `verify: verify.fast test`. The pre-commit entry names the target; CI still runs `make verify`. Add a drift test of the style already used for the hook files (the config's entry equals the Makefile target, and `verify` depends on it).
- Price it again at decision time and record the number with its load figure, labelled by when it was taken (the 12-02/12-03 lesson).
- Accept and write down what the subset does not run: pytest, the coverage floor and the fixture replay, so a commit can still turn the gate red; the pre-push or `make pr.land` stage is where those run.

**Phase to address:** Phase A.

---

### Pitfall 15: The "upstream knob" does not exist, and a local patch of the tool is not durable

**What goes wrong:**
The debt file cites `commands.cjs:3655`; on the installed gsd-core 1.16.0 the constant is at `COMMIT_TIMEOUT_MS = 30_000` (line 3794 of `~/.claude/gsd-core/bin/lib/commands.cjs`), shared by all three commit sites, with no config key (`planning-config.md` lists none). The line number has already drifted, so cite the symbol. The same file has a `noVerify` argument to the SDK commit (`--no-verify` is appended when set), but every gsd workflow (`execute-phase`, `execute-plan`, `manager`) instructs "Do NOT pass `--no-verify`", and CLAUDE.md treats the gate as non-bypassable. Depending on upstream (option a) leaves the repo waiting on a release it does not control; editing the installed file is outside the repo and is lost on update (ASSUMPTION about update behaviour).

**Measured, resolving the debt file's "Unverified" line** (2026-10-06, git 2.54.0, Node `spawnSync` with a 2 s timeout against a 6 s `pre-commit` hook in a scratch repo): the child was killed with `SIGTERM` (`ETIMEDOUT`), nothing was committed, no `index.lock` remained, and the hook process **kept running to completion as an orphan (parent PID 1)**. So a killed gsd commit leaves a real `make verify` running; a retry then overlaps it (two gates, each with 8 xdist workers, sharing `.coverage` files and the stash), and the retry is itself killed at 30 s because the warm hook is about 64 s.

**How to avoid:**
- If the knob is chosen, treat it as "commit by hand until it ships" and keep the decision's date and the upstream issue in the `Lxx`; do not build the milestone on it.
- Whatever is chosen, the executor's documented recovery (remove the lock and retry once) must be re-read against the hook's new runtime; a retry that can only be a second kill is not a recovery.
- A file-filtered variant is cheaper than it looks but needs care: most SDK commits touch only `.planning/`. `always_run: false` plus a `files:` pattern would skip the hook for them, but `tests/test_cli.py` reads `README.md` and the gate scans tracked files, so the pattern must include at least `README.md` and every directory `make verify` reads. A wrong pattern skips the gate silently.

**Phase to address:** Phase A.

---

## Moderate Pitfalls

### Pitfall 16: The undercut warning keeps saying something false, or is retired without evidence

**What goes wrong:**
`derive()` appends "Below {z_min:.1f} teeth a cut gear would be undercut; this model uses a radial root instead." The sentence is pinned verbatim in five fixture records (lines 582, 632, 948, 996, 1588 of `pre_v0_2.json`: 51.0, 47.9 and 11.2 teeth). In trochoid mode "this model uses a radial root" is false; if the mode is off by default, the warning must still fire and should say how to get the trochoid. Changing the meaning without re-measuring the predicate (Pitfall 1) just moves the error.

**How to avoid:**
Re-state the warning from the same predicate function the geometry uses; capture the new strings from `derive()` (never typed, the L33 rule); retire it only with the evidence that the model no longer approximates anything for those rows; README lines 222 to 223 ("Below the base circle the flank is radial ...") change in the same plan. Remember `check()` and the pinned `warnings` tuple move only in the regen commit.

**Phase to address:** Phase D.

### Pitfall 17: The `root_fillet` field's meaning changes silently, and a new field reaches three interfaces at once

**What goes wrong:**
If trochoid mode ignores `root_fillet` (or reinterprets it as the cutter radius) a user-set parameter changes the part without a word. If a new `GearParams` field is added (mode, or a cutter radius), the form, schema and CLI pick it up automatically from field metadata, and v0.2's three-interface parity proof (L31) and the README parameter tables must include it.

**How to avoid:**
Use the "ignored/capped" warning sentence shapes already in `derive()`; add the field to the parity and README-example tests in the same change; keep any new field defaulted so omitted links are unchanged (L05) and prove it with the fixture, not by assertion.

**Phase to address:** Phase D.

### Pitfall 18: Cost to `make verify` (66 s bar, 2.445 s headroom) and to the 30 s build budget

**What goes wrong:**
L34 set the gate bar at 66 s and read 63.555 s, a 2.445 s headroom on a 12-core host; at 8 xdist workers that is roughly 20 s of serial test time. L26's measured cost for the 39 fixture builds was 16.27 s, about 0.4 s a row serially. A trochoid test matrix built mostly on kernel rows exhausts the headroom. Build cost is a second budget: the trochoid applies only where `rf < rb`, at most 116 teeth (extreme case 14.5°, x = -0.6), so the 200-tooth composed worst rows (29.42 s, `SPUR_BUILD_TIMEOUT` 30 s) are untouched by construction; but the 249-row composed sweep includes lower tooth counts, and added edges per tooth cost in tip-chamfer and cutout booleans (the chamfer alone is about 12 s at 200 teeth / 400 edges, L29). That cost is ASSUMPTION until the sweep is re-run for `rf < rb` rows.

**How to avoid:**
Do the proof in pure-maths tests (the oracle needs no kernel, like the v0.3 volume oracles) and keep kernel rows to a priced handful: set a row budget before writing them, measure with `--durations`, and take a human checkpoint if the gate bar is crossed (the D-06/D-10 precedent). Spike-before-field: measure the build cost of a trochoid outline at the heaviest allowed row (low-z, tip chamfer, recess, cutout) before any schema change. Re-run only the composed rows that have `rf < rb`.

**Phase to address:** Phase C (cost), Phase D (bar).

### Pitfall 19: Fixture, tripwire and topology assertions that now disagree for the right reason

**What goes wrong:**
The fixture pins face and edge counts exactly (the "sharpest cheap tripwire"). New per-tooth edges change them for every affected row, so a red fixture on affected rows is expected after the flip and a bug before it (L26: "a red fixture ... is, by definition, a bug in that phase"). A `Volume()` bar of `rel=1e-6` and bounding-box `abs=1e-6` will also move. Do not widen those bars to absorb the change.

**How to avoid:**
Name, before the flip, exactly which records must move and by roughly what (count, volume sign), and have the regen commit's message and `Lxx` list them; any other record moving is a bug. Keep `test_the_fixture_was_captured_on_the_kernel_this_run_uses` untouched.

**Phase to address:** Phase D.

### Pitfall 20: Self-intersecting loops are handled by hiding them

**What goes wrong:**
Where the cutter's tip radius exceeds the path's radius of curvature the offset curve grows a swallow-tail. Clipping the loop away by dropping points, or by relying on the kernel to "heal" it, produces a profile that is close but not the cut part, and the kernel verdict (`isValid()`) is not a proof (Pitfall 7).

**How to avoid:**
Trim analytically at the self-intersection or at the crossing with the involute (Pitfall 4); a clearance oracle (Pitfall 5) proves the surviving curve is the true envelope; refuse or fall back (L08) when a clean trim cannot be computed.

**Phase to address:** Phase B.

---

## Minor Pitfalls

### Pitfall 21: `derive()` stays pure and stdlib-only

`calc.py` must never import `cadquery` (import-linter contract) and, by the same discipline, no `numpy`/`scipy` (installed in the venv, not declared dependencies of this module). The crossing search is bisection in `math`.

### Pitfall 22: Cutter constants hard-coded in two places

The root circle is `rf = r - m(1.25 - x)`; the trochoid's `d_tip = (1.25 - x) m` must come from that expression, not a copy, or `root_d` and the cut part drift.

### Pitfall 23: Stale line references in debt and decision records

Cite symbols, not lines (the commit-timeout debt's `commands.cjs:3655` is now 3794). Record the kernel pair and date beside every measured number, as every `Lxx` already does.

### Pitfall 24: Retiring debt outside the fixing commit

CLAUDE.md: `Status: resolved`, the commit sha, `git mv` to `resolved/`, the INDEX row, all in the same commit as the fix. The race debt retires on the race fix and its margin decision together (Pitfall 12), not on the first commit that touches `pool.py`; the commit-timeout debt retires on the commit that makes the hook decision true.

---

## Phase-Specific Warnings

| Phase | Topic | Likely Pitfall | Mitigation |
|-------|-------|----------------|------------|
| A | Same-slot race fix | Identity-only guard; shutdown route missed; await inserted into the block; clock changed | Guard live-slot and `_processes is not None`; `_closed` flag; synchronous block with a comment and a test; pin the deadline semantics (Pitfalls 9, 12) |
| A | Race tests | Window-dependent assertions flake on 4 vCPUs; `proc.join` ECHILD; resource-tracker warning | Deterministic stale-executor injection; manager-thread join plus exit code; pre-warm; repeat runs under `-n 8 --cov` and `-n 4` (Pitfall 10) |
| A | Margin finding | Hidden by the fix | Separate `Lxx` on `SPUR_BUILD_TIMEOUT`, cap or recorded limit (Pitfall 12) |
| A | Hook decision | Pre-push loses "no red commit"; verifies the checked-out tree; install is per clone; subset drifts; upstream knob absent | Prefer a prefix-by-construction `verify.fast` at commit plus the full gate at push or `make pr.land`; amend L13/L34 in an `Lxx` (Pitfalls 13 to 15) |
| B | Predicate and mode | Three meanings of "undercut"; always-on vs L05 | Human decides with both priced; one predicate function from the cutter constants (Pitfalls 1, 2) |
| B | Cutter frame | Backlash, shift, sign; junction off the model's involute | Junction asserted against `half_angle` first (Pitfall 3) |
| B | Geometry | Tangent assumed everywhere; whole fillet range sampled; centre path used | Crossing by bisection; envelope formula; independent clearance oracle (Pitfalls 4, 5, 20) |
| B | Reference | Unsupported tolerance | Pin the cutter, two recorded numbers per bar, a tripwire (Pitfall 8) |
| B | Printed numbers | `root_thickness`/`root_gap`/`root_d` stay radial-flank figures; ρ infeasible | Recompute from the same geometry or `null` plus warning; cap ρ so `λ_c >= 0` (Pitfall 6) |
| C | Outline and kernel | Open wire, spline blow-up, valid-but-wrong solid | Shared junction points, arc-length sampling, annulus and area guards (Pitfall 7) |
| C | Cost | Rows over budget; heavy composed rows slower | Pure-maths proof, priced kernel rows, spike first, re-run `rf < rb` composed rows (Pitfall 18) |
| D | Flip | Feature commit touches the fixture; hook rejects a red commit | Land dark, flip plus regen plus `Lxx` in one commit (Pitfalls 2, 19) |
| D | Records | Warning text false; README stale; field meaning changed | Capture strings from `derive()`; README and parity tests in the same change (Pitfalls 16, 17) |

## Confidence Notes and What Was Not Verified

- **Measured in this session (HIGH):** the race window table and the shutdown route (scratch scripts against the committed `pool.py`, Python 3.12.13); the kernel facts (cadquery 2.8.0, cadquery-ocp 7.9.3.1.1); the fixture counts; the flank spline error; the gate-subset timings; the git/Node orphaned-hook behaviour (git 2.54.0); pre-commit 4.6.2's pre-push logic (read from installed source); gsd 1.16.0's `COMMIT_TIMEOUT_MS` and `noVerify`.
- **Derived and cross-checked numerically (MEDIUM):** the rack-cutter envelope construction, its agreement with `half_angle` to about 1e-17 rad for non-undercut gears, and the crossing radii. It was checked against the repo's own flank, not against an external reference.
- **Not retrieved (LOW):** ISO 6336-3's `ρ_F`/`s_Fn` formula text and the 2025 "is the fillet a trochoid" abstract (PDF previews unreadable, one 403); ISO 53's 0.38 m value comes from a search summary. The plan must obtain the formulas from a licensed or documented source before using them as an oracle.
- **ASSUMPTION:** behaviour of the race window on a 4-vCPU runner; the build-cost increase of extra per-tooth edges; reachability of the shutdown route through uvicorn; durability of local edits to `~/.claude/gsd-core`; OS-cold mypy timing; that no usable known-good DXF is in hand.

## Sources

- Repository records: `docs/architecture/decision_log.md` (L05, L08, L09, L10, L17, L18, L26, L32, L33, L34); `docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md`; `.../2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`; `.../2026-10-06-resource-tracker-flake-fails-the-gate.md`; `.../2026-10-04-worker-coverage-flush-is-sometimes-lost.md`; `src/spur/pool.py`, `src/spur/calc.py`, `src/spur/model.py`; `tests/test_pool.py`; `tests/regression/pre_v0_2.json`; `.planning/RETROSPECTIVE.md`; `.pre-commit-config.yaml`; `Makefile`.
- Installed tools read directly: `pre_commit/commands/hook_impl.py` and `run.py` (pre-commit 4.6.2); `~/.claude/gsd-core/bin/lib/commands.cjs` (gsd-core 1.16.0).
- ISO 53:1998 standard basic rack profile (haP 1 m, hfP 1.25 m, 0.38 m root-fillet radius; LOW, search summary): https://www.sis.se/api/document/preview/611411/ and https://www.iso.org/obp/ui/es/#!iso:std:22643:en
- ISO 6336-3:2019 existence of `ρ_F`, `s_Fn`, the 30° tangent critical section (LOW, formula text not retrieved): https://www.iso.org/obp/ui/#iso:std:iso:6336:-3:en
- Methods to Determine Form Diameter on Hobbed External Involute Gears, Gear Solutions (trochoid plus secondary involute; relative errors under 0.1 %; MEDIUM): https://gearsolutions.com/features/methods-to-determine-form-diameter-on-hobbed-external-involute-gears/
- Is the root fillet curve in involute gears trochoidal? A geometric reassessment, Mechanism and Machine Theory (title only; abstract 403): https://www.sciencedirect.com/science/article/abs/pii/S0094114X25003179
- Investigation of rack cutter geometry and trochoid curves (J-STAGE, JAMDSM 18(8); title via search only): https://www.jstage.jst.go.jp/article/jamdsm/18/8/18_2024jamdsm0098/_pdf/-char/ja
- pre-commit documentation, pre-push stage and environment variables: https://pre-commit.com/
