"""Measures the honeycomb cutout before any honeycomb field exists (11-CONTEXT.md D-24,
ROADMAP Phase 11 SC3's research flag).

Three parts: (1) build, fine-STL and STEP export time versus whole-cell count at D-11's
configuration (200 teeth, module 10, both recesses); (2) the cut spelling (research
PITFALLS.md Pitfall 2 -- `cut(*cutters)` versus fuse-then-cut versus a compound); (3) the
candidate `HEX_CELL_CAP` (D-11, D-12) -- the largest whole-cell count whose row stays
inside a 7.5 s quarter of `SPUR_BUILD_TIMEOUT`. It is not part of `make verify`: it takes
about 5 minutes, and a timing assertion on shared hardware would flap (`build_time.py`'s
stance).

Run it as `.venv/bin/python -m bench.honeycomb_spike` from the repo root. It prints
Markdown and exits 1 when the verdict fails.
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
import time
import timeit
from dataclasses import dataclass
from importlib import metadata

import cadquery as cq

from bench import machine_facts
from spur import int_env, model
from spur.calc import (  # noqa: F401 -- cell_count_floor/whole_cells re-exported below
    bore_mouth_limit,
    cell_count_floor,
    cells_within,
    profile,
    whole_cells,
)
from spur.params import GearParams

# A quarter of the 30 s SPUR_BUILD_TIMEOUT (D-11): the tip chamfer alone already reads
# 14.87 s at 200 teeth (bench/RESULTS.md "Tooth-tip chamfer build and export time"), so
# the honeycomb's own share must leave room beside it rather than claim half.
BUDGET_S = 7.5

# whole_cells and cell_count_floor moved into spur.calc unchanged by 11-05
# (D-07...D-09, D-13's raise-to-fit); this spike no longer calls them directly
# (cells_within does), but re-imports both so
# bench.honeycomb_spike.whole_cells is spur.calc.whole_cells still holds -- one
# definition of the lattice and the raise, measured and shipped (L08).


def hex_prisms(cell: float, face_width: float,
                centres: tuple[tuple[float, float], ...]) -> list[cq.Solid]:
    """One hexagonal prism prototype -- flats on +-X, vertices on +-Y, the same
    `polygon(6, ..., circumscribed=True)` call `model._cut_bore`'s hex branch uses --
    translated to every cell centre. `Workplane.val()` is a typed union; narrowed with
    isinstance rather than a suppression (per the interfaces note)."""
    proto = cq.Workplane("XY").polygon(6, cell, circumscribed=True).extrude(face_width).val()
    if not isinstance(proto, cq.Solid):
        raise TypeError(f"hex prototype is not a Solid: {type(proto)}")
    return [proto.translate(cq.Vector(x, y, 0)) for x, y in centres]


def cut_with(solid: cq.Solid, prisms: list[cq.Solid], spelling: str) -> cq.Shape:
    """The three spellings research PITFALLS.md Pitfall 2 names for subtracting many
    cutters in a single call -- always exactly one `cut()` (D-24). The spike times all
    three at the cap's target and 11-03 through 11-05 use whichever this run's
    `### Cut spelling` section names."""
    if spelling == "star":
        return solid.cut(*prisms)
    if spelling == "compound":
        return solid.cut(cq.Compound.makeCompound(prisms))
    if spelling == "fuse":
        return solid.cut(prisms[0].fuse(*prisms[1:]))
    raise ValueError(f"unknown cut spelling: {spelling!r}")


@dataclass(frozen=True)
class CostRow:
    label: str
    target: int
    cell: float
    cells: int
    bare_s: float
    cut_s: float
    stl_s: float
    step_s: float
    d_faces: int
    why: str

    @property
    def request_s(self) -> float:
        """The cold request `SPUR_BUILD_TIMEOUT` wraps: one build, one cut, then the
        slower of the two exports -- `Timing.worst_request`'s reasoning in
        `bench/build_time.py`, extended with the cut step this phase adds."""
        return self.bare_s + self.cut_s + max(self.stl_s, self.step_s)

    def ok(self) -> bool:
        return self.why == "" and self.cells <= self.target

    def line(self) -> str:
        return (f"| {self.label} | {self.cell:g} | {self.cells} | {self.bare_s:.2f} | "
                f"{self.cut_s:.2f} | {self.stl_s:.2f} | {self.step_s:.2f} | "
                f"{self.request_s:.2f} | {self.d_faces} | {self.why or 'ok'} |")


def cost_row(kw: dict[str, object], target: int, *, wall: float = 1.0,
             start: float = 3.0, spelling: str = "star") -> CostRow:
    """Build, cut and export one (parameter set, target cell count) row.

    `inner`/`outer` are D-09's honeycomb annulus, read exactly the way 11-05's field
    will: `bore_mouth_limit(p) + wall` to `profile(p).rf - wall`. `target` 0 means no
    cells and no cut -- the bare-build baseline every heavier row is measured against,
    with no export (there is nothing new to export). A failed cut returns a row with
    `why` set and zero export times, never dropped (must_haves prohibition: no
    re-picking to green a bad row).
    """
    label = " ".join(f"{k}={v}" for k, v in kw.items()) + f" target={target}"
    p = GearParams.model_validate(kw)
    inner = bore_mouth_limit(p) + wall
    outer = profile(p).rf - wall

    cell: float
    cells: tuple[tuple[float, float], ...]
    if target == 0:
        cell, cells = start, ()
    else:
        cell, cells = cells_within(target, start, wall, inner, outer)

    t0 = time.perf_counter()
    bare = model._build_checked(p)
    bare_s = time.perf_counter() - t0

    if not cells:
        return CostRow(label, target, cell, 0, bare_s, 0.0, 0.0, 0.0, 0, "")

    prisms = hex_prisms(cell, p.face_width, cells)
    faces_before = len(bare.Faces())

    t0 = time.perf_counter()
    try:
        result: cq.Shape = cut_with(bare, prisms, spelling)
    except Exception as exc:  # mirrors _build_checked's own catch-all breadth: OCCT
        # raises assorted Standard_Failure subclasses this module has no name for.
        cut_s = time.perf_counter() - t0
        return CostRow(label, target, cell, len(cells), bare_s, cut_s, 0.0, 0.0, 0,
                       type(exc).__name__)
    cut_s = time.perf_counter() - t0

    solids = result.Solids()
    if len(solids) != 1:
        return CostRow(label, target, cell, len(cells), bare_s, cut_s, 0.0, 0.0, 0,
                       f"solids={len(solids)}")
    solid = solids[0]
    if not solid.isValid():
        return CostRow(label, target, cell, len(cells), bare_s, cut_s, 0.0, 0.0, 0, "invalid")

    d_faces = len(solid.Faces()) - faces_before

    t0 = time.perf_counter()
    model._write_export(solid, p, "stl", "fine")
    stl_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    model._write_export(solid, p, "step", "fine")
    step_s = time.perf_counter() - t0

    return CostRow(label, target, cell, len(cells), bare_s, cut_s, stl_s, step_s, d_faces, "")


def slower(a: CostRow, b: CostRow) -> CostRow:
    """The row with the larger `request_s`: each row is timed twice, the slower kept --
    conservative against one lucky run understating the cost (T-11-03's mitigation:
    a slow row must never be dropped or re-run away).

    A failed trial (`why` set) always wins over a successful one, regardless of
    `request_s`: a failed cut/build never pays export time, so its `request_s` is
    almost always *smaller* than a successful trial's -- comparing `request_s` alone
    would let a real, reproducible failure lose to a lucky success and vanish before
    the verdict ever sees it (11-REVIEW.md WR-01, external: codex)."""
    if bool(a.why) != bool(b.why):
        return a if a.why else b
    return a if a.request_s >= b.request_s else b


TARGETS: tuple[int, ...] = (0, 25, 50, 75, 100, 125, 150, 175, 200, 250, 300)
# D-11: 200 teeth, module 10 is the largest web, so the cap always binds there; the
# default recess is both sides (GearParams.recess_sides's own default).
HEAVIEST: dict[str, object] = {"teeth": 200, "module": 10}
# D-11's flagged confirmation (A2): the planning probe read module 1.75 heavier than
# module 10 at the same cell count -- the smaller gear's cells cross the recess groove
# and its fillets more often.
CONFIRM: dict[str, object] = {"teeth": 200, "module": 1.75}


def main() -> int:
    timeout = int_env("SPUR_BUILD_TIMEOUT", 30)
    versions = ", ".join(f"{dist} {metadata.version(dist)}"
                         for dist in ("cadquery", "cadquery-ocp"))
    head = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    load1, load5, load15 = os.getloadavg()

    # Time and print everything before deciding (bench/latency.py's rule): every cost
    # row, the spelling rows, the confirmation row and the enumeration timing are all
    # computed here, before the verdict at the end reads any of them.
    cost_rows: list[tuple[CostRow, CostRow, CostRow]] = []
    for target in TARGETS:
        r1 = cost_row(HEAVIEST, target)
        r2 = cost_row(HEAVIEST, target)
        cost_rows.append((slower(r1, r2), r1, r2))

    # The cap: the last row before the first row whose request exceeds BUDGET_S -- a
    # row at or under budget after an over-budget row does not extend it (D-12).
    cap_row: CostRow | None = None
    over_row: CostRow | None = None
    for row, _, _ in cost_rows:
        if row.request_s > BUDGET_S:
            over_row = row
            break
        cap_row = row
    cap_target = cap_row.target if cap_row is not None else 0

    spelling_rows: dict[str, CostRow] = {}
    for name in ("star", "compound", "fuse"):
        r1 = cost_row(HEAVIEST, cap_target, spelling=name)
        r2 = cost_row(HEAVIEST, cap_target, spelling=name)
        spelling_rows[name] = slower(r1, r2)
    star_cut = spelling_rows["star"].cut_s
    spelling = "star"
    for name, row in spelling_rows.items():
        if name != "star" and row.cut_s < star_cut * 0.9:
            spelling = name

    confirm_r1 = cost_row(CONFIRM, cap_target)
    confirm_r2 = cost_row(CONFIRM, cap_target)
    confirm_row = slower(confirm_r1, confirm_r2)

    # The enumeration cost at hex_wall 0.4 (derive()'s heaviest input, 11-05's
    # docstring): the smallest allowed wall gives the most candidate cells to search.
    p_heaviest = GearParams.model_validate(HEAVIEST)
    enum_wall = 0.4
    enum_inner = bore_mouth_limit(p_heaviest) + enum_wall
    enum_outer = profile(p_heaviest).rf - enum_wall
    cap_for_enum = cap_row.cells if cap_row is not None else 0
    enum_s = min(timeit.repeat(
        lambda: cells_within(cap_for_enum, 3.0, enum_wall, enum_inner, enum_outer),
        number=1, repeat=5))

    print("### Host state")
    print(f"- Machine: {machine_facts()}")
    print(f"- Python: {platform.python_version()}")
    print(f"- Kernel: {versions}")
    print(f"- HEAD: `{head}`")
    print(f"- Load averages at start (script's own os.getloadavg()): "
         f"{load1:.2f}, {load5:.2f}, {load15:.2f}")
    print(f"- SPUR_BUILD_TIMEOUT: {timeout} s")
    print(f"- BUDGET_S: {BUDGET_S} s (a quarter of SPUR_BUILD_TIMEOUT, D-11)")
    print()

    print("### Cost by cell count")
    print("| Set | Cell (mm) | Cells | Bare (s) | Cut (s) | STL (s) | STEP (s) | "
         "Request (s) | dFaces | Why | Run 1 / Run 2 request (s) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for row, r1, r2 in cost_rows:
        print(f"{row.line()} {r1.request_s:.2f} / {r2.request_s:.2f} |")
    print()

    print("### Cut spelling")
    print("| Set | Cell (mm) | Cells | Bare (s) | Cut (s) | STL (s) | STEP (s) | "
         "Request (s) | dFaces | Why | Spelling |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for name in ("star", "compound", "fuse"):
        print(f"{spelling_rows[name].line()} {name} |")
    print(f"**Spelling:** {spelling}")
    print()

    print("### Cap")
    if cap_row is not None:
        if over_row is not None:
            next_txt = (f" the next row ({over_row.cells} cells) reads "
                       f"{over_row.request_s:.2f} s.")
        else:
            next_txt = " every row stayed inside budget."
        print(f"**Cap:** HEX_CELL_CAP = {cap_row.cells} -- {cap_row.label} reads "
             f"{cap_row.request_s:.2f} s of {BUDGET_S} s;{next_txt}")
    else:
        assert over_row is not None  # TARGETS is non-empty, so one of the two is set
        print(f"**Cap:** HEX_CELL_CAP = 0 -- even the bare build and export at "
             f"{over_row.label} reads {over_row.request_s:.2f} s of {BUDGET_S} s.")
    print()

    print("### Confirmation at module 1.75")
    print("| Set | Cell (mm) | Cells | Bare (s) | Cut (s) | STL (s) | STEP (s) | "
         "Request (s) | dFaces | Why |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    print(confirm_row.line())
    print()

    print("### Enumeration cost")
    print(f"`cells_within({cap_for_enum}, 3.0, {enum_wall:g}, inner, outer)` at "
         f"teeth=200 module=10: {enum_s * 1000:.3f} ms (best of 5).")
    print()

    reasons: list[str] = []
    if not all(row.ok() for row, _, _ in cost_rows):
        reasons.append("a cost row is not ok()")
    if cap_row is None or cap_row.cells < 50:
        reasons.append("the cap is under 50 cells")
    if confirm_row.request_s > BUDGET_S:
        reasons.append("the module-1.75 confirmation row exceeds the budget")
    # WR-01 (11-REVIEW.md, external: codex): request_s alone never proved the
    # confirmation or spelling rows actually succeeded -- only `ok()` (why == "")
    # does, and slower() could hide a failure under a faster successful run, so a
    # real build/cut failure in either row set could reach "Verdict: held" unseen.
    if not confirm_row.ok():
        reasons.append("the module-1.75 confirmation row failed")
    if not all(row.ok() for row in spelling_rows.values()):
        reasons.append("a cut-spelling row failed")

    print("### Verdict")
    if not reasons:
        assert cap_row is not None  # else "the cap is under 50 cells" would have fired
        print(f"**Verdict:** held -- HEX_CELL_CAP = {cap_row.cells} cells "
             f"({cap_row.request_s:.2f} s of {BUDGET_S} s), spelling {spelling}, "
             f"confirmation {confirm_row.request_s:.2f} s of {BUDGET_S} s.")
        return 0
    print(f"**Verdict:** FAILED -- {'; '.join(reasons)}.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
