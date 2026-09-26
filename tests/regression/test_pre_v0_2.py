"""Every pre-v0.2 parameter set still derives and builds the same part (L05, Success
Metric 3 of milestone v0.2: "old links unchanged").

Comparison contract: `DerivedDimensions` compares exactly, warning text included --
`derive()` is Python-computed and rounded to 3 dp at construction, so exact is honest
(D-10). `build().Volume()` compares at `rel=1e-6`: `Volume()` read identical (max diff
0.0) over three independent builds on the pinned kernel, and the default 0.4 mm bore
chamfer is only 1.05e-3 of the volume, so a looser tolerance would let a vanished chamfer
through (D-11). The six bounding-box corners compare at `abs=1e-6`: OCCT pads the box by
about 1e-7 per side, and a translated part must fail too, not only a resized one (D-12).
Face and edge counts compare exactly: 172 faces / 490 edges with the default bore
chamfer, 168 / 482 without (D-13).

A red test here in Phases 8-12 is that phase's bug, never this fixture's (D-03). Fix the
regression, then run `make fixture.regen` in its own commit stating what moved and why --
never as part of a feature commit.
"""

from __future__ import annotations

import json
from importlib import metadata

import pytest
from capture import FIXTURE, Fixture, Record, derived, solid
from corpus import cases

_FIXTURE: Fixture = json.loads(FIXTURE.read_text())
_RECORDS = _FIXTURE["records"]

_ALL_RECORDS = [pytest.param(record, id=record_id) for record_id, record in _RECORDS.items()]
_SOLID_RECORDS = [pytest.param(record, id=record_id)
                  for record_id, record in _RECORDS.items() if "solid" in record]

_CORNERS = ("xmin", "xmax", "ymin", "ymax", "zmin", "zmax")


@pytest.mark.parametrize("record", _ALL_RECORDS)
def test_a_pre_v0_2_parameter_set_derives_the_same_dimensions(record: Record) -> None:
    got = derived(record["params"], record.get("mate_teeth"))
    assert got == record["derived"]


@pytest.mark.parametrize("record", _SOLID_RECORDS)
def test_a_pre_v0_2_parameter_set_builds_the_same_solid(record: Record) -> None:
    expected = record["solid"]
    got = solid(record["params"])
    assert got["faces"] == expected["faces"]
    assert got["edges"] == expected["edges"]
    assert got["volume"] == pytest.approx(expected["volume"], rel=1e-6)
    assert ({k: got[k] for k in _CORNERS}
            == pytest.approx({k: expected[k] for k in _CORNERS}, abs=1e-6))


def test_the_fixture_records_every_corpus_set() -> None:
    """A corpus edit with no regeneration, or a hand-edited JSON, must go red here."""
    fixture_index = {record_id: (record["params"], record.get("mate_teeth"), record["sources"])
                     for record_id, record in _RECORDS.items()}
    corpus_index = {case_id: (case.params, case.mate, case.sources)
                    for case_id, case in cases().items()}
    assert fixture_index == corpus_index


def test_the_fixture_was_captured_on_the_kernel_this_run_uses() -> None:
    """Pitfall 11: an unpinned kernel bump otherwise shows up as dozens of unexplained
    topology mismatches instead of one named test."""
    provenance = _FIXTURE["provenance"]
    running = {"cadquery": metadata.version("cadquery"),
              "cadquery-ocp": metadata.version("cadquery-ocp")}
    captured = {"cadquery": provenance["cadquery"], "cadquery-ocp": provenance["cadquery-ocp"]}
    assert running == captured, (
        f"fixture captured on cadquery/cadquery-ocp {captured}, this run uses {running}; "
        "recreate the venv to match, or regenerate with `make fixture.regen` per D-03 "
        "if the pin moved deliberately")
