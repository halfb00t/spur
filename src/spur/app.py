"""HTTP API and web UI.

    GET /                    web UI
    GET /api/health          liveness
    GET /api/schema          JSON schema of the parameters (drives the UI form)
    GET /api/info?...        derived dimensions, measurement aids, warnings
    GET /api/model.stl?...   binary STL   (quality=preview|fine)
    GET /api/model.step?...  STEP AP214 solid

Every gear parameter is a query string field, so a model URL is shareable and
curl-able. Unset fields take their defaults.
"""

from __future__ import annotations

import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated, Any, Iterator, Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import Field

from . import __version__, int_env
from .calc import derive, with_mate
from .model import BuildError, export
from .params import GearParams

STATIC = Path(__file__).parent / "static"
MEDIA_TYPES = {"stl": "model/stl", "step": "model/step"}

# Every build serialises on the kernel lock in model.py, so requests waiting behind it
# buy latency and memory but no throughput. Past a short queue, 503 is the honest answer.
MAX_QUEUED_BUILDS = int_env("SPUR_MAX_QUEUED_BUILDS", 4)
BUILD_QUEUE = threading.BoundedSemaphore(MAX_QUEUED_BUILDS)

app = FastAPI(
    title="spur",
    version=__version__,
    summary="Parametric involute spur gear generator with STL/STEP export.",
)
app.add_middleware(GZipMiddleware, minimum_size=1024)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


class InfoQuery(GearParams):
    mate_teeth: int | None = Field(None, ge=6, le=1000, title="Mating gear teeth",
                                   description="Also report the centre distance to this gear.")


class ModelQuery(GearParams):
    quality: Literal["preview", "fine"] = Field(
        "fine", description="STL tessellation: preview (coarse, small) or fine.")


def _gear(q: GearParams) -> GearParams:
    """Strip the per-endpoint extras back to a plain GearParams.

    The build caches are keyed on the parameter object, and pydantic equality includes
    the class, so a ModelQuery and an InfoQuery describing the same gear would otherwise
    never hit each other's cache entries.
    """
    return GearParams(**q.model_dump(include=set(GearParams.model_fields)))


@contextmanager
def _build_slot() -> Iterator[None]:
    """Admission control: refuse work we cannot start soon rather than queue it."""
    if not BUILD_QUEUE.acquire(blocking=False):
        raise HTTPException(
            503,
            detail=[{"loc": ["query"], "type": "busy",
                     "msg": f"Busy: {MAX_QUEUED_BUILDS} gears are already being built. "
                            "Try again in a moment."}],
            headers={"Retry-After": "5"},
        )
    try:
        yield
    finally:
        BUILD_QUEUE.release()


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/api/schema")
def schema() -> dict[str, Any]:
    return GearParams.model_json_schema()


@app.get("/api/info")
def info(q: Annotated[InfoQuery, Query()]) -> dict[str, Any]:
    """Derived dimensions. With `mate_teeth`, also the centre distance to that gear."""
    params = _gear(q)
    out = derive(params)
    return with_mate(out, params, q.mate_teeth) if q.mate_teeth else out


@app.get("/api/model.{fmt}", response_class=Response,
         responses={200: {"content": {t: {} for t in MEDIA_TYPES.values()}}})
def model(fmt: Literal["stl", "step"], q: Annotated[ModelQuery, Query()]) -> Response:
    params = _gear(q)
    try:
        with _build_slot():
            data = export(params, fmt, q.quality)
    except BuildError as exc:
        raise HTTPException(422, detail=[{"loc": ["query"], "msg": str(exc),
                                          "type": "build_error"}]) from exc
    return Response(
        data,
        media_type=MEDIA_TYPES[fmt],
        headers={"Content-Disposition": f'attachment; filename="{params.slug()}.{fmt}"'},
    )
