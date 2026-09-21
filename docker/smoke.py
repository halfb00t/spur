"""Build-time smoke test: prove the trimmed image can still do the job.

The Dockerfile installs a pinned closure with --no-deps and drops the transitive
packages cadquery pulls in but spur never uses (VTK viewers, DXF export, the assembly
solver, matplotlib). That is only safe if the build fails loudly when the closure is
wrong, so this exercises both halves of the product -- the CAD kernel and the HTTP app,
including the ASGI stack under it -- using nothing that isn't already in the image.
"""

from __future__ import annotations

import anyio

from spur.app import app


async def get(path: str, query: bytes = b"") -> tuple[int, bytes]:
    """One GET straight through the ASGI app; the image has no HTTP test client."""
    status: int | None = None
    body = bytearray()
    pending = [{"type": "http.request", "body": b"", "more_body": False}]

    async def receive() -> dict:
        return pending.pop(0) if pending else {"type": "http.disconnect"}

    async def send(message: dict) -> None:
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
    for path in ("/", "/api/health", "/api/schema", "/api/info"):
        status, _ = await get(path)
        assert status == 200, f"{path} -> {status}"

    status, stl = await get("/api/model.stl", b"quality=preview")
    assert status == 200 and len(stl) > 1000, f"stl -> {status}, {len(stl)} bytes"

    status, step = await get("/api/model.step")
    assert status == 200 and step.startswith(b"ISO-10303-21;"), f"step -> {status}"

    status, _ = await get("/api/info", b"bore_flat=3")
    assert status == 422, f"invalid parameters -> {status}, expected 422"

    print("smoke: kernel, exports, ASGI stack and validation all live")


anyio.run(main)
