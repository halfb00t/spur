"""The seam between the gear and the shaft, pinned before any shaft code exists (L46,
D-12 to D-15).

Each belt below is the regex half of an import-linter contract in pyproject.toml, the
pairing tests/test_records.py started: the contract is the suspenders, the belt reads the
source text. The existence guard closes a hole in import-linter itself: it rejects a
contract whose source module is missing, but accepts a missing forbidden module without a
word (measured: `9 kept` with shaft_model.py deleted, 30-RESEARCH Resolved Unknown 1), so
a mistyped forbidden name would never go red. The route pin follows ARCHITECTURE F1: a gear
route ignores query keys it does not know, so a part chosen by a query key would build the
default gear silently, and the shaft gets its own /api/shaft/ prefix instead.

The file only reads app.routes, app.openapi() and source files. It never adds a route, so
it is safe under xdist.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import cast

from fastapi.routing import APIRoute
from starlette.routing import Mount, Route

from spur.app import app
from spur.params import GearParams

SRC = Path(__file__).resolve().parents[1] / "src" / "spur"

# D-13: costly to reverse, since a rename edits every contract and every plan naming it.
FROZEN_LAYOUT = ("parts", "shaft_params", "shaft_calc", "din5480", "din5480_tables",
                 "shaft_model")
SHAFT_MATHS = ("shaft_params", "shaft_calc", "din5480", "din5480_tables")

V06_API = frozenset({
    ("/api/health", frozenset({"GET"})),
    ("/api/schema", frozenset({"GET"})),
    ("/api/info", frozenset({"GET"})),
    ("/api/model.{fmt}", frozenset({"GET"})),
})
NON_API_PATHS = frozenset({"/", "/openapi.json", "/docs", "/docs/oauth2-redirect",
                           "/redoc", "/static"})


def _import_lines(source: str, names: tuple[str, ...]) -> list[str]:
    """The import statements in `source` that name any of `names`, at any indentation
    (params.py imports inside functions). Matches `import x`, `import x.y`, `import
    spur.x`, `from x import`, `from .x import`, `from spur.x import`, `from . import a, x`
    and `from spur import x`. `\\b` after the name keeps `model` from matching
    `shaft_model`. A parenthesised multi-line `from . import (` list is the one shape a
    line-based regex cannot see; the contract catches it.
    """
    alt = "|".join(re.escape(n) for n in names)
    pattern = re.compile(
        rf"^[ \t]*(?:import[ \t]+(?:spur\.)?(?:{alt})\b"
        rf"|from[ \t]+(?:spur\.|\.)?(?:{alt})\b"
        rf"|from[ \t]+(?:spur|\.)[ \t]+import[ \t]+[^#\n]*\b(?:{alt})\b)[^\n]*",
        re.MULTILINE)
    return [m.group(0).strip() for m in pattern.finditer(source)]


def _read(name: str) -> str:
    return (SRC / f"{name}.py").read_text(encoding="utf-8")


def test_every_module_a_contract_names_exists_and_the_layout_is_frozen() -> None:
    """D-13, T-30-10: every `spur.*` name in any import-linter contract has a file under
    src/spur, and the six frozen names are among them and exist flat, not in a package."""
    config = tomllib.loads((SRC.parents[1] / "pyproject.toml").read_text(encoding="utf-8"))
    contracts = config["tool"]["importlinter"]["contracts"]
    named = {m for c in contracts for key in ("source_modules", "forbidden_modules")
             for m in c.get(key, []) if m.startswith("spur.")}
    missing = [m for m in sorted(named) if not (SRC / f"{m.removeprefix('spur.')}.py").exists()]
    assert not missing, f"contracts name modules with no file: {missing}"
    frozen = {f"spur.{n}" for n in FROZEN_LAYOUT}
    assert frozen <= named, f"frozen names no contract mentions: {sorted(frozen - named)}"
    absent = [n for n in FROZEN_LAYOUT if not (SRC / f"{n}.py").is_file()]
    assert not absent, f"frozen modules missing: {absent}"
    assert not (SRC / "shaft").exists(), "the shaft modules are flat, never a package (D-13)"


def test_the_shaft_maths_imports_no_kernel_no_solid_no_logger_and_no_gear_maths() -> None:
    """Belt for 'The shaft maths stays free of the CAD kernel and the solid', '... of the
    logger' and 'The shaft maths copies the gear maths, never imports it'. It first proves
    the helper sees each way to write an import of `model` and lets `shaft_model` and
    `params` through, so a belt over docstring-only files cannot pass for the wrong reason."""
    for line in ("import model", "import spur.model", "from model import x",
                 "from .model import x", "from spur.model import x", "from . import model",
                 "from . import params, model", "from spur import model",
                 "    from . import model  # inside a function"):
        assert _import_lines(line, ("model",)), line
    for line in ("import shaft_model", "from .shaft_model import x", "from . import shaft_model",
                 "from .params import GearParams", "from . import params  # model",
                 "import models"):
        assert not _import_lines(line, ("model",)), line
    forbidden = ("cadquery", "OCP", "model", "shaft_model", "records", "logging", "calc")
    found = {n: _import_lines(_read(n), forbidden) for n in SHAFT_MATHS}
    assert not any(found.values()), found


def test_only_model_may_import_the_shaft_solid() -> None:
    """Belt for 'The kernel doorways are model and shaft_model': nothing that serves,
    logs or lists parts names the shaft's solid."""
    found = {n: _import_lines(_read(n), ("shaft_model",))
             for n in ("app", "cli", "pool", "records", "parts")}
    assert not any(found.values()), found


def test_the_shaft_solid_never_imports_the_gear_doorway() -> None:
    """model imports shaft_model statically, so the reverse edge is a cycle (32-RESEARCH
    Anti-Patterns). A module-level cycle would also fail at import, a function-local one
    would not; `_import_lines` reads both."""
    assert _import_lines(_read("shaft_model"), ("model",)) == []


def test_the_gear_maths_imports_no_shaft_module() -> None:
    """Belt for 'The gear maths does not know the shaft': gear numbers must not move
    because shaft code did (L46)."""
    forbidden = (*SHAFT_MATHS, "shaft_model", "parts")
    found = {n: _import_lines(_read(n), forbidden) for n in ("calc", "params")}
    assert not any(found.values()), found


def test_every_route_beyond_v0_6_lives_under_the_shaft_prefix() -> None:
    """D-15: the /api/ routes contain the v0.6 four exactly as (path, methods), every
    other /api/ route starts with /api/shaft/, and nothing outside /api/ is added."""
    api: set[tuple[str, frozenset[str]]] = set()
    other: set[str] = set()
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path.startswith("/api/"):
            api.add((route.path, frozenset(route.methods or ())))
        elif isinstance(route, Route | Mount):
            other.add(route.path)
        else:
            raise AssertionError(f"route of an unexpected type: {type(route).__name__}")
    assert api >= V06_API, f"v0.6 routes missing or changed: {sorted(V06_API - api)}"
    stray = sorted(p for p, _ in api - V06_API if not p.startswith("/api/shaft/"))
    assert not stray, f"/api/ routes outside /api/shaft/: {stray}"
    outside = sorted(other - NON_API_PATHS)
    assert not outside, f"routes outside /api/ that v0.6 did not have: {outside}"


def _query_keys(path: str) -> set[str]:
    paths = cast("dict[str, dict[str, dict[str, list[dict[str, object]]]]]",
                 app.openapi()["paths"])
    return {str(p["name"]) for p in paths[path]["get"].get("parameters", [])
            if p["in"] == "query"}


def test_the_gear_routes_take_the_v0_6_query_keys() -> None:
    """D-15: a gear route ignores a query key it does not know, so a key added to one
    would change what an old link builds without any error. The keys are the gear's
    fields plus each endpoint's own extra, and the two bare routes take none."""
    fields = set(GearParams.model_fields)
    assert _query_keys("/api/info") == fields | {"mate_teeth"}
    assert _query_keys("/api/model.{fmt}") == fields | {"quality"}
    assert _query_keys("/api/schema") == set()
    assert _query_keys("/api/health") == set()
