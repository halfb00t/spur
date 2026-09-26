"""Regenerates `tests/regression/pre_v0_2.json`: `make fixture.regen`, never anything else.

Trigger and mechanism: this script made the first capture in Phase 7, on unmodified
pre-v0.2 code. It rebuilds every corpus set (`tests/regression/corpus.py`) on the working
tree's code and rewrites the JSON. During v0.2 the file changes only in its own commit
whose message states what moved and why -- a cadquery/cadquery-ocp pin bump under L12, or
a deliberate contract change carrying a new Lxx. A feature commit never touches it, and a
red fixture in Phases 8-12 is, by definition, a bug in that phase, not this file's (D-03).
"""

from __future__ import annotations

import json
import subprocess
from datetime import date
from importlib import metadata
from pathlib import Path
from typing import NotRequired, TypedDict

from corpus import cases

from spur.calc import derive
from spur.model import build
from spur.params import GearParams

FIXTURE = Path(__file__).with_name("pre_v0_2.json")

_REPO_ROOT = Path(__file__).resolve().parents[2]


def derived(params: dict[str, object], mate: int | None) -> dict[str, object]:
    """derive()'s 19 fields, JSON-ready (the warnings tuple becomes a list, D-10)."""
    return derive(GearParams.model_validate(params), mate_teeth=mate).model_dump(mode="json")


def solid(params: dict[str, object]) -> dict[str, float]:
    """build()'s content: volume, six bounding-box corners, face and edge counts
    (D-11, D-12, D-13)."""
    s = build(GearParams.model_validate(params))
    bb = s.BoundingBox()
    return {
        "volume": s.Volume(),
        "xmin": bb.xmin, "xmax": bb.xmax,
        "ymin": bb.ymin, "ymax": bb.ymax,
        "zmin": bb.zmin, "zmax": bb.zmax,
        "faces": len(s.Faces()),
        "edges": len(s.Edges()),
    }


class Record(TypedDict):
    """A record stores only the fields its source set (D-04), plus what was measured."""

    params: dict[str, object]
    sources: list[str]
    derived: dict[str, object]
    solid: NotRequired[dict[str, float]]
    mate_teeth: NotRequired[int]


class Fixture(TypedDict):
    """Typed so nothing here ever writes `Any` (L21)."""

    provenance: dict[str, object]
    records: dict[str, Record]


def provenance() -> dict[str, object]:
    """Which kernel and which working tree produced these numbers (Pitfall 11)."""

    def git(*args: str) -> str:
        # Fixed argument list, no shell (T-07-03): nothing here is attacker-controlled,
        # but the pattern is the one to copy if that ever changes.
        return subprocess.run(
            ["git", *args], cwd=_REPO_ROOT, check=True, capture_output=True, text=True,
        ).stdout.strip()

    return {
        "git_head": git("rev-parse", "HEAD"),
        "src_clean": git("status", "--porcelain", "--", "src") == "",
        "cadquery": metadata.version("cadquery"),
        "cadquery-ocp": metadata.version("cadquery-ocp"),
        "captured": date.today().isoformat(),
        "regenerate": ("Rewrite only with `make fixture.regen`, in its own commit stating "
                       "what moved and why (D-03) -- never as part of a feature commit."),
    }


def main() -> int:
    records: dict[str, Record] = {}
    built = 0
    mate_only = 0
    for case_id, case in cases().items():
        if case.mate is None:
            records[case_id] = {
                "params": case.params,
                "sources": case.sources,
                "derived": derived(case.params, None),
                "solid": solid(case.params),
            }
            built += 1
        else:
            # The solid is the base record's -- mated sets share a GearParams with one,
            # so no extra build() (D-07).
            records[case_id] = {
                "params": case.params,
                "sources": case.sources,
                "derived": derived(case.params, case.mate),
                "mate_teeth": case.mate,
            }
            mate_only += 1

    fixture: Fixture = {"provenance": provenance(), "records": records}
    FIXTURE.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n")
    print(f"wrote {len(records)} records ({built} built, {mate_only} mate-only) to {FIXTURE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
