"""Build-time smoke test: prove the trimmed image can still do the job.

The Dockerfile installs a pinned closure with --no-deps and drops the transitive
packages cadquery pulls in but spur never uses (VTK viewers, DXF export, the assembly
solver, matplotlib). That is only safe if the build fails loudly when the closure is
wrong, so this exercises both halves of the product -- the CAD kernel and the HTTP app,
including the ASGI stack under it -- using nothing that isn't already in the image.
"""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any

import anyio

from spur.app import app


async def get(path: str, query: bytes = b"") -> tuple[int, bytes]:
    """One GET straight through the ASGI app; the image has no HTTP test client."""
    status: int | None = None
    body = bytearray()
    pending = [{"type": "http.request", "body": b"", "more_body": False}]

    async def receive() -> MutableMapping[str, Any]:
        return pending.pop(0) if pending else {"type": "http.disconnect"}

    async def send(message: MutableMapping[str, Any]) -> None:
        nonlocal status
        if message["type"] == "http.response.start":
            status = message["status"]
        elif message["type"] == "http.response.body":
            body.extend(message.get("body", b""))

    await app({
        "type": "http", "asgi": {"version": "3.0", "spec_version": "2.1"},
        "http_version": "1.1", "method": "GET", "scheme": "http",
        "path": path, "raw_path": path.encode(), "query_string": query,
        "root_path": "", "headers": [(b"host", b"smoke")],
        "client": ("127.0.0.1", 0), "server": ("smoke", 80),
    }, receive, send)
    assert status is not None, f"{path}: the app never responded"
    return status, bytes(body)


async def main() -> None:
    # The build pool (Phase 2, D-04) starts in app.py's `lifespan`, which only runs
    # under a real ASGI server or a lifespan-aware client -- calling `app(...)` raw, as
    # this script does, never triggers it on its own. `/api/model.{stl,step}` now needs
    # a started pool (build_backend() hard-fails otherwise, by design -- 02-01-SUMMARY.md
    # "resolves Open Question 1: injection is for tests only, production never goes
    # inline"), so this smoke test drives the lifespan itself via Starlette's own
    # `router.lifespan_context`, the same callable a real ASGI server invokes.
    async with app.router.lifespan_context(app):
        for path in ("/", "/api/health", "/api/schema", "/api/info"):
            status, _ = await get(path)
            assert status == 200, f"{path} -> {status}"

        status, stl = await get("/api/model.stl", b"quality=preview")
        assert status == 200, f"stl -> {status}"
        assert len(stl) > 1000, f"stl -> only {len(stl)} bytes"

        status, step = await get("/api/model.step")
        assert status == 200, f"step -> {status}"
        assert step.startswith(b"ISO-10303-21;"), "step -> not an ISO-10303-21 file"

        status, _ = await get("/api/info", b"bore_flat=3")
        assert status == 422, f"invalid parameters -> {status}, expected 422"

    print("smoke: kernel, exports, ASGI stack and validation all live")


if __name__ == "__main__":
    # Required now that /api/model.{stl,step} spawns a worker process (Phase 2,
    # mp_context="spawn", pool.py): spawn re-imports this module as __main__ in the
    # child to bootstrap it, and an unguarded module-level anyio.run(main) call would
    # re-run this entire script inside that child -- the exact recursive-relaunch
    # multiprocessing's own "Safe importing of main module" guidance (and its
    # RuntimeError when violated) warns against.
    anyio.run(main)
