"""Build-failure exception types, kept free of the CAD kernel on purpose.

`app.py` has to name a build failure (to map it to a 422) without importing `cadquery` --
the serving process is not allowed to reach the kernel by any path (D-02). Splitting these
two exceptions out of `model.py` is what makes that possible: `model.py` still defines and
raises them, but the import that matters -- `from .build_errors import BuildError` in
`app.py` -- never drags OpenCascade in behind it.

`BuildTimeout` was originally defined here, not reused from a builtin, because
`asyncio.TimeoutError` and the builtin `TimeoutError` were distinct classes on the
retired 3.10 floor and only became aliases in 3.11 -- a gap L23 retired by dropping that
floor. It stays because it is the one timeout `app.py` turns into a 503 with its own
error `type` ("timeout"), distinct from `BrokenProcessPool`'s 503 -- a client can tell
"come back in a moment" from "the worker died" by this class alone.
"""

from __future__ import annotations


class BuildError(RuntimeError):
    """The CAD kernel could not produce a valid solid for these parameters."""


class BuildTimeout(Exception):  # noqa: N818 -- named after asyncio.TimeoutError on purpose
    """A build did not finish within its allotted time; the worker was terminated."""
