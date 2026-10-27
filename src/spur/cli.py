"""Command line: `spur serve`, `spur info`, `spur export`, `spur shaft info`, `spur shaft export`.

Gear options are generated from GearParams and shaft options from ShaftParams, so they
always match the API. The shaft also takes a DIN 5480 designation in place of its four
spline fields (REQ-designation-input).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Literal, cast, get_args, get_origin

from pydantic import ValidationError

from . import __version__
from .din5480 import DesignationError
from .params import GearParams
from .records import configure
from .shaft_calc import derive_shaft
from .shaft_params import SPLINE_KEYS, DesignationConflict, ShaftParams, resolve_shaft

# Mirrors InfoQuery.mate_teeth's ge=/le= in app.py, so the CLI refuses what the API
# refuses (REQ-cli-parity). A tooth count outside this range would produce a centre
# distance for a gear that cannot exist (L08). cli.py may not import spur.app (the
# import-linter contract "The CLI does not inherit web-serving policy"), so the bound
# is copied rather than shared; tests/test_cli.py::test_info_rejects_a_mate_the_api_
# would_reject reads InfoQuery's own JSON schema and pins the two copies together.
_MATE_TEETH_MIN = 6
_MATE_TEETH_MAX = 1000


def _mate_teeth(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not an integer") from None
    if not (_MATE_TEETH_MIN <= value <= _MATE_TEETH_MAX):
        raise argparse.ArgumentTypeError(
            f"--mate-teeth must be between {_MATE_TEETH_MIN} and {_MATE_TEETH_MAX} "
            f"(got {value})")
    return value


def _add_gear_args(ap: argparse.ArgumentParser) -> None:
    g = ap.add_argument_group("gear parameters (defaults in brackets)")
    for name, field in GearParams.model_fields.items():
        flag = "--" + name.replace("_", "-")
        help_text = f"{field.description} [{field.default}]".replace("%", "%%")
        if get_origin(field.annotation) is Literal:
            g.add_argument(flag, dest=name, default=None, help=help_text,
                            choices=list(get_args(field.annotation)))
        else:
            # pydantic gives every declared field an annotation; this check exists
            # only to narrow `field.annotation`'s `type | None` to a real type for
            # argparse's `type=`, not because a field can actually lack one.
            assert field.annotation is not None
            g.add_argument(flag, dest=name, default=None, help=help_text,
                            metavar="V", type=field.annotation)


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


def _add_shaft_args(ap: argparse.ArgumentParser) -> None:
    # The gear's loop again, not a shared generator: the two groups' titles differ and the
    # gear's help text is pinned byte for byte (33-RESEARCH Pattern 5).
    g = ap.add_argument_group("shaft parameters (defaults in brackets)")
    for name, field in ShaftParams.model_fields.items():
        flag = "--" + name.replace("_", "-")
        help_text = f"{field.description} [{field.default}]".replace("%", "%%")
        assert field.annotation is not None  # as in _add_gear_args: narrows for type=
        g.add_argument(flag, dest=name, default=None, help=help_text,
                       metavar="V", type=field.annotation)
    g.add_argument("--designation", default=None, metavar="TEXT",
                   help="a DIN 5480 designation such as 'W 25x1.25x18x8f'. It replaces "
                        "--reference-d, --module, --teeth and --fit and may not be given "
                        "with any of them; the solid's flags combine with it")


def _shaft_params(ns: argparse.Namespace) -> ShaftParams:
    values = {k: v for k in ShaftParams.model_fields if (v := getattr(ns, k)) is not None}
    try:
        if ns.designation is None:
            return ShaftParams(**values)
        return resolve_shaft(ns.designation, values)
    except (DesignationConflict, DesignationError) as exc:
        print(f"error: designation: {exc}", file=sys.stderr)
    except ValidationError as exc:
        for err in exc.errors():
            loc = [str(x) for x in err["loc"]]
            # Read the way the API reads it: a refusal of what the designation spelled, or
            # of the shaft as a whole, is the designation's; a solid's field keeps its own.
            if ns.designation is not None and (not loc or loc[0] in SPLINE_KEYS):
                loc = ["designation"]
            where = ".".join(loc)
            msg = err["msg"].removeprefix("Value error, ")
            print(f"error: {where + ': ' if where else ''}{msg}", file=sys.stderr)
    raise SystemExit(2)


def cmd_serve(ns: argparse.Namespace) -> None:
    import uvicorn

    # The composition root (D-05): every production start is `spur serve`. configure()
    # installs the one stderr JSON handler for the SPUR_WORKERS=1 default; app.py's
    # lifespan() calls it again, idempotently, because this call alone would silently
    # miss every record once a deployer raises SPUR_WORKERS (see records.py's docstring).
    configure()
    # log_config=None: verified this session by reading the installed uvicorn's
    # Config.configure_logging(), whose entire body is gated behind
    # `if self.log_config is not None`. Passing None skips uvicorn's own dictConfig
    # entirely, and since no log_level is passed either, uvicorn never touches
    # `uvicorn.error`/`uvicorn.access`'s levels or handlers -- they keep propagate=True
    # and land on the one root handler above, so the whole stream shares one format
    # (D-02).
    uvicorn.run("spur.app:app", host=ns.host, port=ns.port, workers=ns.workers,
                root_path=ns.root_path, proxy_headers=True, log_config=None)


def cmd_info(ns: argparse.Namespace) -> None:
    from .calc import derive

    # ns.mate_teeth is None (flag omitted) or already range-checked by _mate_teeth
    # (argparse's type=); --mate-teeth 0 is refused at the argument, matching the
    # API's 422 for the same value (R-2) instead of meaning "no mate" as it used to.
    print(derive(_params(ns), mate_teeth=ns.mate_teeth).model_dump_json(indent=2))


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
    for warning in derive(p).warnings:
        print(f"warning: {warning}", file=sys.stderr)


def cmd_shaft_info(ns: argparse.Namespace) -> None:
    print(derive_shaft(_shaft_params(ns)).model_dump_json(indent=2))


def cmd_shaft_export(ns: argparse.Namespace) -> None:
    from .build_errors import BuildError
    from .model import Format, export

    out: Path = ns.output
    fmt = ns.format or out.suffix.lower().lstrip(".").replace("stp", "step")
    if fmt not in ("stl", "step"):
        raise SystemExit("error: output must end in .stl or .step (or pass --format)")
    p = _shaft_params(ns)
    try:
        data = export(p, cast("Format", fmt), ns.quality)   # the check above is the proof
    except BuildError as exc:
        raise SystemExit(f"error: {exc}") from None
    out.write_bytes(data)   # only after the build returned: a refused run leaves no file
    print(f"wrote {out} ({len(data) / 1024:.0f} KiB)", file=sys.stderr)
    for warning in derive_shaft(p).warnings:
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
    i.add_argument("--mate-teeth", type=_mate_teeth,
                   help="also print centre distance to this gear "
                        f"[{_MATE_TEETH_MIN}-{_MATE_TEETH_MAX}]")
    _add_gear_args(i)
    i.set_defaults(func=cmd_info)

    e = sub.add_parser("export", help="write an STL or STEP file")
    e.add_argument("-o", "--output", type=Path, required=True, help="file.stl or file.step")
    e.add_argument("--format", choices=["stl", "step"], help="override the file extension")
    e.add_argument("--quality", choices=["preview", "fine"], default="fine",
                   help="STL tessellation [fine]")
    _add_gear_args(e)
    e.set_defaults(func=cmd_export)

    sh = sub.add_parser("shaft", help="the DIN 5480 splined shaft")
    shaft_sub = sh.add_subparsers(dest="shaft_cmd", required=True)

    si = shaft_sub.add_parser("info", help="print the shaft's derived dimensions as JSON")
    _add_shaft_args(si)
    si.set_defaults(func=cmd_shaft_info)

    se = shaft_sub.add_parser("export", help="write the shaft as an STL or STEP file")
    se.add_argument("-o", "--output", type=Path, required=True, help="file.stl or file.step")
    se.add_argument("--format", choices=["stl", "step"], help="override the file extension")
    se.add_argument("--quality", choices=["preview", "fine"], default="fine",
                    help="STL tessellation [fine]")
    _add_shaft_args(se)
    se.set_defaults(func=cmd_shaft_export)

    ns = ap.parse_args(argv)
    ns.func(ns)


if __name__ == "__main__":
    main()
