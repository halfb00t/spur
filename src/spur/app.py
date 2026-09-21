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

from pathlib import Path
from typing import Annotated, Any, Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import Field

from . import __version__
from .calc import centre_distance, derive
from .model import BuildError, export
from .params import GearParams

STATIC = Path(__file__).parent / "static"
MEDIA_TYPES = {"stl": "model/stl", "step": "model/step"}

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
    return GearParams(**q.model_dump(include=set(GearParams.model_fields)))


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
    if q.mate_teeth:
        out["mate_teeth"] = q.mate_teeth
        out["centre_distance"] = round(centre_distance(params, q.mate_teeth), 3)
    return out


@app.get("/api/model.{fmt}", response_class=Response,
         responses={200: {"content": {t: {} for t in MEDIA_TYPES.values()}}})
def model(fmt: Literal["stl", "step"], q: Annotated[ModelQuery, Query()]) -> Response:
    params = _gear(q)
    try:
        data = export(params, fmt, q.quality)
    except BuildError as exc:
        raise HTTPException(422, detail=[{"loc": ["query"], "msg": str(exc),
                                          "type": "build_error"}]) from exc
    return Response(
        data,
        media_type=MEDIA_TYPES[fmt],
        headers={"Content-Disposition": f'attachment; filename="{params.slug()}.{fmt}"'},
    )
