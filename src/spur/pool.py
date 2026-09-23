"""Process pool that runs CAD builds outside the serving process (D-01--D-08).

`app.py` holds a `BuildPool` instance and calls its async `export()`; it has no static
import path to `cadquery`/`OCP` through this module (D-02) -- the kernel import happens
only at runtime, inside a worker, via `importlib.import_module`. Each of the N
single-worker `ProcessPoolExecutor`s is warmed with the kernel once at startup (D-04) and
then reused for every build routed to it by parameter-hash affinity (D-07): the UI's
preview STL, fine STL and STEP requests for one gear are three byte-cache keys but one
solid, so keeping them on the same worker avoids the same ~280 MiB solid becoming
resident in all N of them. Accepted cost: no work stealing -- a hot gear serialises,
which is what it does today under the single kernel lock (D-08).
"""

from __future__ import annotations

import importlib
import multiprocessing as mp
from asyncio import get_running_loop
from concurrent.futures import ProcessPoolExecutor
from typing import cast

from .params import GearParams

_SPAWN = mp.get_context("spawn")  # portable, and with D-02 the parent has no OCP to fork


def _warm() -> None:
    """`ProcessPoolExecutor`'s initializer: runs once per worker, before its first task.

    Loads the kernel into the worker before it accepts work (D-04), so the first real
    request doesn't pay the cadquery/OCP import cost. This import is the reason the
    contract in Task 3 must be `allow_indirect_imports = false` scoped to `spur.app`
    only -- `spur.pool` importing `spur.model` at runtime, inside a worker, is exactly
    the boundary this phase is drawing, not a violation of it.
    """
    importlib.import_module("spur.model")


def build_export(p: GearParams, fmt: str, quality: str) -> bytes:
    """The function submitted across the process boundary (D-05).

    Deliberately a dynamic import, not `from .model import export` (even nested inside
    this function): a static import would put a `spur.app -> spur.pool -> spur.model ->
    cadquery` edge in the import graph, which is exactly what D-02's
    `allow_indirect_imports = false` contract (Task 3) forbids for `spur.app`. The parent
    process only ever holds this function's *name*, for `spawn` to pickle by reference;
    only a worker process executes its body, where importing the kernel is fine.
    """
    model = importlib.import_module("spur.model")
    # `model` is loaded dynamically, so mypy sees its attributes as Any; `export()`'s
    # real return type is bytes (it's model.py's own export(), unchanged by this phase),
    # so warn_return_any needs this cast rather than a genuine type gap.
    return cast(bytes, model.export(p, fmt, quality))


class BuildPool:
    """N independent single-worker executors, routed to by parameter-hash affinity (D-07)."""

    def __init__(self, workers: int) -> None:
        self.workers = workers
        self.replaced = 0  # D-13: workers replaced since start, reported at /api/health
        self._executors = [
            ProcessPoolExecutor(max_workers=1, mp_context=_SPAWN, initializer=_warm)
            for _ in range(workers)
        ]

    def executor_for(self, p: GearParams) -> ProcessPoolExecutor:
        return self._executors[hash(p) % self.workers]  # D-07: affinity, not load-balance

    def recreate_for(self, p: GearParams) -> None:
        """Discard a broken/wedged single-worker executor and replace it (D-10, D-12)."""
        i = hash(p) % self.workers
        self._executors[i].shutdown(wait=False, cancel_futures=True)
        self._executors[i] = ProcessPoolExecutor(
            max_workers=1, mp_context=_SPAWN, initializer=_warm)
        self.replaced += 1

    async def export(self, p: GearParams, fmt: str, quality: str) -> bytes:
        loop = get_running_loop()
        # run_in_executor(executor, func, *args) is positional-only -- no **kwargs --
        # so build_export's signature must stay all-positional (verified against the
        # installed asyncio.AbstractEventLoop.run_in_executor signature, 02-RESEARCH.md).
        return await loop.run_in_executor(self.executor_for(p), build_export, p, fmt, quality)

    def shutdown(self) -> None:
        for executor in self._executors:
            executor.shutdown(wait=False)
