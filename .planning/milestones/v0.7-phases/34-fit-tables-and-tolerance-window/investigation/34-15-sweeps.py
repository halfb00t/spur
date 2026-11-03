# ruff: noqa -- probe over the real table file, kept as Phase 34 evidence; prints counts and locations, never a value
"""34-15: the real table file swept through the loader, the maths and the kernel.

Run with SPUR_DIN5480_TABLES set to the ignored private/din5480-tables.json:
  1. the guard sweep: every tabulated size x every fit Table 7 lists, counting per measurement
     (nominal, max, min) printed / null at the guard / null for another reason;
  2. the tip-land and overlap sweep (pure maths): every size x every Table 7 letter, at the
     printed s_vmax written as build_shaft writes it;
  3. the two extreme combinations built through build_shaft in their own subprocess (120 s);
  4. the page's own worked example, W 120x3x38x8f, through derive_shaft.

The committed log holds counts, locations (module, d_B, z, fit or letter), pass/fail and
timings. Every cell and every computed number goes to the ignored private/reads/
sweep-findings.txt and anchor-candidates.txt, which the human reads beside the PDF pages.
"""
import json
import math
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src"))
PY = str(ROOT / ".venv" / "bin" / "python")
PRIVATE = ROOT / "private" / "reads"
VOLUME_REL = 1e-4  # tests/test_shaft_model.py VOLUME_REL
BUILD_WALL_CLOCK = 120

if not os.environ.get("SPUR_DIN5480_TABLES"):
    sys.exit("SPUR_DIN5480_TABLES is not set")

from pydantic import ValidationError  # noqa: E402

from spur import din5480, din5480_tables  # noqa: E402
from spur.shaft_calc import derive_shaft, pin_contact_window  # noqa: E402
from spur.shaft_params import ShaftParams  # noqa: E402

tables = din5480_tables.active()
assert tables is not None
findings: list[str] = []


def loc(row) -> str:
    return f"m={row.module:g} d_B={row.reference_d:g} z={row.teeth}"


def section(title: str) -> None:
    print(f"\n== {title}")


def reason(warnings: tuple[str, ...], prefix: str) -> str:
    for w in warnings:
        if w.startswith(prefix):
            return "guard" if "outside the window" in w else "other"
    return "other"


# 1. The guard sweep ------------------------------------------------------------------------
def guard_sweep() -> None:
    section("1. guard sweep: every tabulated size x every fit Table 7 lists")
    fits = [f"{c}{l}" for c in tables.tolerance_classes for l in tables.letters]
    print(f"fits per size: {len(fits)} ({len(tables.tolerance_classes)} classes x "
          f"{len(tables.letters)} letters)")
    counts: dict[str, Counter] = {k: Counter() for k in ("nominal", "max", "min")}
    no_tolerance = 0
    refused: Counter = Counter()
    refused_sizes: set = set()
    nominal_null: dict = {}
    max_guard: dict = defaultdict(list)
    min_guard: dict = defaultdict(list)
    max_other: dict = defaultdict(list)
    min_other: dict = defaultdict(list)
    combos = 0
    t0 = time.perf_counter()
    for row in tables.sizes:
        for fit in fits:
            if tables.fit(row.module, row.reference_d, fit) is None:
                no_tolerance += 1
                continue
            try:
                p = ShaftParams(reference_d=row.reference_d, module=row.module,
                                teeth=row.teeth, fit=fit, shank_length=0)
            except ValidationError as exc:
                e = exc.errors()[0]
                refused[f"{e['type']} {'/'.join(map(str, e['loc'])) or 'model'}"] += 1
                refused_sizes.add(row.key)
                continue
            combos += 1
            d = derive_shaft(p)
            w = d.warnings
            if d.measure_over_pins is not None:
                counts["nominal"]["printed"] += 1
            else:
                r = reason(w, "M_Re and D_Re not given")
                counts["nominal"][r] += 1
                nominal_null.setdefault(row.key, r)
            for which, value, store_g, store_o in (
                    ("max", d.measure_over_pins_max, max_guard, max_other),
                    ("min", d.measure_over_pins_min, min_guard, min_other)):
                if value is not None:
                    counts[which]["printed"] += 1
                else:
                    r = reason(w, f"M_Re {which} is not given")
                    counts[which][r] += 1
                    (store_g if r == "guard" else store_o)[row.key].append(fit)
    elapsed = time.perf_counter() - t0
    print(f"sizes: {len(tables.sizes)}; fit combinations with a Table 7 tolerance and a valid "
          f"ShaftParams: {combos}; no Table 7 tolerance: {no_tolerance}; "
          f"ShaftParams refused: {sum(refused.values())}")
    for k, v in refused.items():
        print(f"  refusal reason: {k}: {v}")
    if refused_sizes:
        print(f"  sizes refused by ShaftParams: {len(refused_sizes)}")
        for key in sorted(refused_sizes):
            print(f"    REFUSED m={key[0]:g} d_B={key[1]:g} z={key[2]}")
    print("measurement | printed | null at the guard | null for another reason")
    for k in ("nominal", "max", "min"):
        c = counts[k]
        print(f"M_Re {k} | {c['printed']} | {c['guard']} | {c['other']}")
    print(f"sizes whose nominal M_Re is null although the copy prints its M1: "
          f"{len(nominal_null)}")
    for key in sorted(nominal_null):
        print(f"  NOMINAL-NULL m={key[0]:g} d_B={key[1]:g} z={key[2]} ({nominal_null[key]})")
        r = tables.size(*key)
        findings.append(f"NOMINAL-NULL m={key[0]:g} d_B={key[1]:g} z={key[2]}: pin_d={r.pin_d_mm} "
                        f"m1={r.m1_mm} form_d_max={r.form_d_max_mm}")
    for label, store in (("M_Re max null at the guard", max_guard),
                         ("M_Re min null at the guard", min_guard),
                         ("M_Re max null for another reason", max_other),
                         ("M_Re min null for another reason", min_other)):
        print(f"sizes with {label} for at least one fit: {len(store)}")
        for key in sorted(store):
            fs = store[key]
            print(f"  {label.upper().replace(' ', '-')} m={key[0]:g} d_B={key[1]:g} z={key[2]}: "
                  f"{len(fs)} fits ({fs[0]}..{fs[-1]})")
            r = tables.size(*key)
            p = ShaftParams(reference_d=key[1], module=key[0], teeth=key[2], fit=fs[0],
                            shank_length=0)
            xm = din5480.profile_shift(p.reference_d, p.module, p.teeth) * p.module
            tol = tables.fit(key[0], key[1], fs[0])
            s_vmax, s_max, s_min = din5480.thickness_limits(
                din5480.tooth_thickness(p.module, xm), tol.a_s_um, tol.t_g_um, tol.t_eff_um)
            s = s_max if "max" in label else s_min
            res = din5480.measure_over_pins(p.module, p.teeth, s, r.pin_d_mm)
            low, high = pin_contact_window(p, r.form_d_max_mm)
            findings.append(
                f"{label.upper()} m={key[0]:g} d_B={key[1]:g} z={key[2]} first fit {fs[0]} "
                f"(of {len(fs)}): A_s,T_G,T_act,T_eff={tuple(tol)} s_used={s:.4f} "
                f"pin={r.pin_d_mm} contact={'none' if res is None else f'{res[1]:.4f}'} "
                f"window={low:.4f}..{high:.4f} form_d_max={r.form_d_max_mm}")
    print(f"guard sweep wall clock: {elapsed:.1f} s")


# 1b. The same question asked without derive_shaft ---------------------------------------------
def guard_crosscheck() -> None:
    """Every size (the ones ShaftParams refuses too, through model_construct) x every fit x the
    three thicknesses, straight against pin_contact_window: if the sweep above were blind to a
    null (a classification slip), this one would still count it."""
    section("1b. cross-check without derive_shaft: contact against the window, every size x fit")
    fits = [f"{c}{l}" for c in tables.tolerance_classes for l in tables.letters]
    checked = outside = no_contact = 0
    t0 = time.perf_counter()
    for row in tables.sizes:
        p = ShaftParams.model_construct(reference_d=row.reference_d, module=row.module,
                                        teeth=row.teeth, fit="8f", shank_length=0,
                                        splined_length=30.0, end_chamfer=1.0, shank_d=25.0)
        xm = din5480.profile_shift(row.reference_d, row.module, row.teeth) * row.module
        s1 = din5480.tooth_thickness(row.module, xm)
        low, high = pin_contact_window(p, row.form_d_max_mm)
        for fit in fits:
            tol = tables.fit(row.module, row.reference_d, fit)
            _, s_max, s_min = din5480.thickness_limits(s1, tol.a_s_um, tol.t_g_um, tol.t_eff_um)
            for s in (s1, s_max, s_min):
                checked += 1
                res = din5480.measure_over_pins(row.module, row.teeth, s, row.pin_d_mm)
                if res is None:
                    no_contact += 1
                elif not low <= res[1] <= high:
                    outside += 1
                    print(f"  OUTSIDE m={row.module:g} d_B={row.reference_d:g} z={row.teeth} "
                          f"fit {fit}")
    print(f"readings checked: {checked}; contact outside the window: {outside}; "
          f"pin touches no flank: {no_contact}; wall clock {time.perf_counter() - t0:.1f} s")


# 2. The tip-land and overlap sweep -----------------------------------------------------------
def tip_sweep() -> dict:
    section("2. tip-land and overlap sweep: every tabulated size x every Table 7 letter")
    tolerance_class = tables.tolerance_classes[0]
    tip_fail: list = []
    root_fail: list = []
    no_column: set = set()
    combos = 0
    worst_tip = (math.inf, None)
    worst_root = (-math.inf, None)
    t0 = time.perf_counter()
    for row in tables.sizes:
        m, z, d_b = row.module, row.teeth, row.reference_d
        xm = din5480.profile_shift(d_b, m, z) * m
        s1 = din5480.tooth_thickness(m, xm)
        tip_d = round(din5480.tip_diameter(d_b, m), 3)
        root_d = round(din5480.root_diameter(m, z, xm, din5480.H_FP), 3)
        for letter in tables.letters:
            tol = tables.fit(m, d_b, f"{tolerance_class}{letter}")
            if tol is None:
                no_column.add(row.key)
                continue
            combos += 1
            s_vmax = round(s1 + tol.a_s_um / 1000, 3)
            xm_flank = (s_vmax - math.pi * m / 2) / (2 * math.tan(din5480.ALPHA))
            h_tip = din5480.flank_half_angle(m, z, xm_flank, tip_d / 2)
            h_root = din5480.flank_half_angle(m, z, xm_flank, root_d / 2)
            land = h_tip * tip_d / 2
            fraction = h_root / (math.pi / z)
            key = (row.key, letter)
            if h_tip <= 0:
                tip_fail.append((key, land))
            if h_root >= math.pi / z:
                root_fail.append((key, fraction))
            if land < worst_tip[0]:
                worst_tip = (land, key)
            if fraction > worst_root[0]:
                worst_root = (fraction, key)
    print(f"size x letter combinations: {combos} (class {tolerance_class} stands for all: A_s "
          f"depends on the letter and the column only); sizes without a column: {len(no_column)}")
    print(f"tip land closed (half angle at the tip radius <= 0): {len(tip_fail)}")
    for (k, letter), land in tip_fail:
        print(f"  TIP-CLOSED m={k[0]:g} d_B={k[1]:g} z={k[2]} letter {letter}")
        findings.append(f"TIP-CLOSED m={k[0]:g} d_B={k[1]:g} z={k[2]} letter {letter}: "
                        f"tip half width={land:.5f} mm")
    print(f"space closed (half angle at the root radius >= pi/z): {len(root_fail)}")
    for (k, letter), fr in root_fail:
        print(f"  TEETH-OVERLAP m={k[0]:g} d_B={k[1]:g} z={k[2]} letter {letter}")
        findings.append(f"TEETH-OVERLAP m={k[0]:g} d_B={k[1]:g} z={k[2]} letter {letter}: "
                        f"root half angle / (pi/z)={fr:.5f}")
    (wt_k, wt_l), (wr_k, wr_l) = worst_tip[1], worst_root[1]
    print(f"thinnest tip land: m={wt_k[0]:g} d_B={wt_k[1]:g} z={wt_k[2]} letter {wt_l} "
          f"(its width is in private/reads/sweep-findings.txt)")
    print(f"thickest tooth at the root: m={wr_k[0]:g} d_B={wr_k[1]:g} z={wr_k[2]} letter {wr_l} "
          f"(its fraction of the space is in private/reads/sweep-findings.txt)")
    findings.append(f"THINNEST-TIP m={wt_k[0]:g} d_B={wt_k[1]:g} z={wt_k[2]} letter {wt_l}: "
                    f"tip half width={worst_tip[0]:.5f} mm")
    findings.append(f"THICKEST-ROOT m={wr_k[0]:g} d_B={wr_k[1]:g} z={wr_k[2]} letter {wr_l}: "
                    f"root half angle / (pi/z)={worst_root[0]:.5f}")
    print(f"tip sweep wall clock: {time.perf_counter() - t0:.1f} s")
    return {"tip": (wt_k, wt_l), "root": (wr_k, wr_l), "class": tolerance_class}


# 3. The extreme builds ------------------------------------------------------------------------
BUILD = '''
import json, math, sys, time
sys.path.insert(0, %r)
import shaft_oracle
from spur import din5480
from spur.shaft_calc import derive_shaft
from spur.shaft_model import build_shaft
from spur.shaft_params import ShaftParams
a = json.loads(sys.argv[1])
p = ShaftParams(reference_d=a["d"], module=a["m"], teeth=a["z"], fit=a["fit"],
                splined_length=10.0, shank_length=0)
t = time.perf_counter()
solid = build_shaft(p)
dims = derive_shaft(p)
printed = dims.max_effective_thickness
x = (printed - math.pi * p.module / 2) / (2 * p.module * math.tan(din5480.ALPHA))
ref = shaft_oracle.shaft_volume(p.module, p.teeth, x, dims.root_d / 2, dims.tip_d / 2,
                                p.splined_length, dims.end_chamfer_effective or 0.0,
                                p.shank_d, p.shank_length)
print(json.dumps(dict(valid=solid.isValid(), n=len(solid.Solids()),
                      rel=abs(solid.Volume() / ref - 1), t=time.perf_counter() - t)))
''' % str(ROOT / "tests")


def extreme_builds(extremes: dict) -> None:
    section(f"3. extreme builds through build_shaft ({BUILD_WALL_CLOCK} s wall clock each)")
    for label, (k, letter) in (("thinnest tip land", extremes["tip"]),
                               ("thickest tooth", extremes["root"])):
        arg = json.dumps(dict(d=k[1], m=k[0], z=k[2], fit=f"{extremes['class']}{letter}"))
        t0 = time.perf_counter()
        try:
            r = subprocess.run([PY, "-c", BUILD, arg], capture_output=True, text=True,
                               timeout=BUILD_WALL_CLOCK)
            out = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else None
            err = r.stderr.strip().splitlines()[-1][:120] if r.stderr.strip() else ""
        except subprocess.TimeoutExpired:
            out, err = None, "timeout"
        wall = time.perf_counter() - t0
        where = f"m={k[0]:g} d_B={k[1]:g} z={k[2]} letter {letter}"
        if out is None:
            print(f"  {label}: {where}: FAIL (no result; {err}) after {wall:.1f} s")
            continue
        ok = out["valid"] and out["n"] == 1 and out["rel"] <= VOLUME_REL
        print(f"  {label}: {where}: {'PASS' if ok else 'FAIL'} valid={out['valid']} "
              f"solids={out['n']} volume rel error {out['rel']:.2e} (bar {VOLUME_REL:g}) "
              f"build {out['t']:.2f} s, wall {wall:.1f} s")


# 4. The page's worked example -----------------------------------------------------------------
def page_example() -> None:
    section("4. the page's example W 120x3x38x8f through derive_shaft")
    d = derive_shaft(ShaftParams(reference_d=120, module=3, teeth=38, fit="8f"))
    # CONTEXT D-05 and Phase 31's approved anchor give these four; they are already in the
    # repository (34-CONTEXT.md, tests/test_din5480_anchors.py).
    want = {"max_effective_thickness": 6.243, "max_actual_thickness": 6.22,
            "min_actual_thickness": 6.18, "measure_over_pins_min": 125.956}
    for name, value in want.items():
        got = getattr(d, name)
        print(f"  {name}: {'PASS' if got == value else 'FAIL'}")
    print(f"  M_Re (nominal) printed: {d.measure_over_pins is not None}; "
          f"M_Re max printed: {d.measure_over_pins_max is not None}")


# The private candidates file -------------------------------------------------------------------
def candidates() -> None:
    lines = ["ANCHOR CANDIDATES (private; never commit, never paste into a message)", ""]
    for name, (d_b, m, z, fit) in {
            "W 120x3x38x8f": (120, 3, 38, "8f"),
            "W 25x1.25x18x8f": (25, 1.25, 18, "8f"),
            "W 26x1.25x19x8f": (26, 1.25, 19, "8f")}.items():
        row = tables.size(m, d_b, z)
        lines.append(f"=== {name}")
        if row is None:
            lines.append("  size not in the file")
            continue
        lines.append(f"  Part 2 (cl. {row.provenance.clause}, Tables {row.provenance.table}, "
                     f"pages {row.provenance.pages}): d_Ff1 max={row.form_d_max_mm}  "
                     f"D_M={row.pin_d_mm}  M1={row.m1_mm}")
        covering = sorted((c for c in tables.columns if c.module_min_mm <= m <= c.module_max_mm),
                          key=lambda c: (c.d_b_over_mm is not None, c.d_b_over_mm or 0))
        selected = tables.column_for(m, d_b)
        on_edge = [c for c in covering if d_b in (c.d_b_over_mm, c.d_b_upto_mm)]
        lines.append(f"  module group columns (over..upto -> column), A1 selects column "
                     f"{selected}:")
        for c in covering:
            mark = "  <- on the edge" if c in on_edge else ""
            lines.append(f"    {c.d_b_over_mm}..{c.d_b_upto_mm} -> column {c.column}{mark}")
        shown = on_edge or [c for c in covering if c.column == selected]
        cls = next(c for c in tables.classes if c.tolerance_class == int(fit[:-1]))
        dev = next(x for x in tables.deviations if x.letter == fit[-1])
        xm = din5480.profile_shift(d_b, m, z) * m
        s1 = din5480.tooth_thickness(m, xm)
        for c in shown:
            trow = next(t for t in tables.tolerances if t.row == cls.row_by_column[c.column - 1])
            a_s = dev.a_s_um[c.column - 1]
            lim = din5480.thickness_limits(s1, a_s, trow.t_g_um, trow.t_eff_um)
            lines.append(
                f"  Table 7 (page {dev.provenance.pages}) column {c.column}: A_s of "
                f"'{fit[-1]}'={a_s}  class {fit[:-1]} -> tolerance row {trow.row}: "
                f"T_G={trow.t_g_um} T_act={trow.t_act_um} T_eff={trow.t_eff_um}  "
                f"[s1={s1:.4f} -> s_vmax,s_max,s_min={tuple(round(v, 4) for v in lim)}]")
        dims = derive_shaft(ShaftParams(reference_d=d_b, module=m, teeth=z, fit=fit))
        lines.append(f"  the five printed rows (tool): s_vmax={dims.max_effective_thickness} "
                     f"s_max={dims.max_actual_thickness} s_min={dims.min_actual_thickness} "
                     f"M_Re max={dims.measure_over_pins_max} M_Re min={dims.measure_over_pins_min} "
                     f"(M_Re nominal={dims.measure_over_pins}, pin={dims.pin_d})")
        lines.append("")
    (PRIVATE / "anchor-candidates.txt").write_text("\n".join(lines) + "\n")


def main() -> None:
    t0 = time.perf_counter()
    print(f"table file loaded: {len(tables.sizes)} sizes, {len(tables.deviations)} letters, "
          f"{len(tables.classes)} classes, {len(tables.tolerances)} tolerance rows, "
          f"{len(tables.columns)} columns")
    guard_sweep()
    guard_crosscheck()
    extremes = tip_sweep()
    extreme_builds(extremes)
    page_example()
    PRIVATE.mkdir(parents=True, exist_ok=True)
    candidates()
    (PRIVATE / "sweep-findings.txt").write_text(
        "SWEEP FINDINGS (private; never commit, never paste into a message)\n"
        + "\n".join(findings) + "\n")
    print(f"\nprivate files written: sweep-findings.txt ({len(findings)} lines), "
          f"anchor-candidates.txt")
    print(f"total probe time: {time.perf_counter() - t0:.1f} s")


if __name__ == "__main__":
    main()
