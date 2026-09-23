"""Command line: `spur serve`, `spur info`, `spur export`.

Gear options are generated from GearParams, so they always match the API.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Literal, cast, get_args, get_origin

from pydantic import ValidationError

from . import __version__
from .params import GearParams


def _add_gear_args(ap: argparse.ArgumentParser) -> None:
    g = ap.add_argument_group("gear parameters (defaults in brackets)")
    for name, field in GearParams.model_fields.items():
        kw: dict[str, Any] = {"dest": name, "default": None, "metavar": "V",
                    "help": f"{field.description} [{field.default}]".replace("%", "%%")}
        if get_origin(field.annotation) is Literal:
            kw["choices"] = list(get_args(field.annotation))
            kw.pop("metavar")
        else:
            kw["type"] = field.annotation
        g.add_argument("--" + name.replace("_", "-"), **kw)


def _params(ns: argparse.Namespace) -> GearParams:
    values = {k: v for k in GearParams.model_fields if (v := getattr(ns, k)) is not None}
    try:
        return GearParams(**values)
    except ValidationError as exc:
        for err in exc.errors():
            where = ".".join(str(x) for x in err["loc"])
            msg = err["msg"].removeprefix("Value error, ")
            print(f"error: {where + ': ' if where else ''}{msg}", file=sys.stderr)
        raise SystemExit(2) from None


def cmd_serve(ns: argparse.Namespace) -> None:
    import uvicorn

    uvicorn.run("spur.app:app", host=ns.host, port=ns.port, workers=ns.workers,
                root_path=ns.root_path, proxy_headers=True)


def cmd_info(ns: argparse.Namespace) -> None:
    from .calc import derive, with_mate

    p = _params(ns)
    out = derive(p)
    if ns.mate_teeth:
        out = with_mate(out, p, ns.mate_teeth)
    print(json.dumps(out, indent=2, ensure_ascii=False))


def cmd_export(ns: argparse.Namespace) -> None:
    from .build_errors import BuildError
    from .calc import derive
    from .model import Format, export

    out: Path = ns.output
    fmt = ns.format or out.suffix.lower().lstrip(".").replace("stp", "step")
    if fmt not in ("stl", "step"):
        raise SystemExit("error: output must end in .stl or .step (or pass --format)")
    p = _params(ns)
    try:
        data = export(p, cast("Format", fmt), ns.quality)   # the check above is the proof
    except BuildError as exc:
        raise SystemExit(f"error: {exc}") from None
    out.write_bytes(data)
    print(f"wrote {out} ({len(data) / 1024:.0f} KiB)", file=sys.stderr)
    for warning in derive(p)["warnings"]:
        print(f"warning: {warning}", file=sys.stderr)


def main(argv: list[str] | None = None) -> None:
    env = os.environ.get
    ap = argparse.ArgumentParser(prog="spur", description="Parametric involute spur gears.")
    ap.add_argument("--version", action="version", version=f"spur {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("serve", help="run the web UI and API")
    s.add_argument("--host", default=env("SPUR_HOST", "127.0.0.1"))
    s.add_argument("--port", type=int, default=int(env("SPUR_PORT", "8000")))
    s.add_argument("--workers", type=int, default=int(env("SPUR_WORKERS", "1")))
    s.add_argument("--root-path", default=env("SPUR_ROOT_PATH", ""),
                   help="URL prefix when served behind a reverse proxy, e.g. /spur")
    s.set_defaults(func=cmd_serve)

    i = sub.add_parser("info", help="print derived dimensions as JSON")
    i.add_argument("--mate-teeth", type=int, help="also print centre distance to this gear")
    _add_gear_args(i)
    i.set_defaults(func=cmd_info)

    e = sub.add_parser("export", help="write an STL or STEP file")
    e.add_argument("-o", "--output", type=Path, required=True, help="file.stl or file.step")
    e.add_argument("--format", choices=["stl", "step"], help="override the file extension")
    e.add_argument("--quality", choices=["preview", "fine"], default="fine",
                   help="STL tessellation [fine]")
    _add_gear_args(e)
    e.set_defaults(func=cmd_export)

    ns = ap.parse_args(argv)
    ns.func(ns)


if __name__ == "__main__":
    main()
