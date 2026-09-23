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

D-10 adds a per-build timeout: a wedged worker is fatal to 1/N of the parameter space
under D-07's affinity until something kills it, so `export()` terminates the OS process
running an overrunning build rather than merely abandoning the `Future` waiting on it,
then replaces that hash slot's executor (`recreate_for`). The same replacement handles a
worker that dies on its own (`BrokenProcessPool`, D-12).
"""

from __future__ import annotations

import asyncio
import importlib
import multiprocessing as mp
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from typing import cast

from .build_errors import BuildTimeout
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

    def __init__(self, workers: int, timeout: int) -> None:
        self.workers = workers
        self.timeout = timeout  # D-10: per-build ceiling in seconds; see app.py's
        # lifespan for where the number itself comes from -- this class only enforces it.
        self.replaced = 0  # D-13: workers replaced since start, reported at /api/health
        # D-11: max_tasks_per_child deliberately absent (stays None -- no recycling).
        # bench/memory.py's sweep (bench/RESULTS.md, Memory section) split each N's
        # samples into an early/late half to check for drift malloc_trim doesn't
        # flatten: N=1 showed no growth (late peak *below* early peak); N=2 and N=4
        # both grew late vs early, but bench/corpus.py's corpus is strictly ascending
        # tooth count (160 -> 199), so the "late" half is inherently the biggest gears
        # -- a bounded, per-worker 4-entry solid cache holding increasingly large
        # solids as the corpus advances grows resident memory for that reason alone,
        # with no leak required. No sweep run showed unbounded growth or a failure
        # from it. Recycling anyway would cost a respawn plus a cadquery import and
        # wipe the warm solid cache D-07 exists to keep, for a drift signal this sweep
        # did not actually find. Re-run the sweep and revisit if a future corpus or
        # workload shows growth the ascending-corpus explanation can't account for.
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

    async def _run_with_timeout(
        self, p: GearParams, func: Callable[..., bytes], *args: object,
    ) -> bytes:
        """Route `func(*args)` to `p`'s worker, enforcing the per-build timeout (D-10)
        and replacing the worker if it wedges or dies (D-12).

        A private seam behind `export()` rather than inlined there, so
        tests/test_pool.py can drive the timeout/replacement path with a trivial
        sleeping function instead of a real (and therefore slow) CAD build -- the
        mechanics under test (timeout -> terminate -> recreate, and broken-pool ->
        recreate) don't depend on what `func` actually builds.
        """
        executor = self.executor_for(p)
        loop = asyncio.get_running_loop()
        # run_in_executor(executor, func, *args) is positional-only -- no **kwargs --
        # so every func crossing this boundary must stay all-positional (verified
        # against the installed asyncio.AbstractEventLoop.run_in_executor signature,
        # 02-RESEARCH.md).
        future = loop.run_in_executor(executor, func, *args)
        try:
            return await asyncio.wait_for(future, timeout=self.timeout)
        except asyncio.TimeoutError:
            # asyncio.TimeoutError by its qualified name, not the builtin: they are
            # distinct classes on the 3.10 floor CI also runs (see build_errors.py's
            # BuildTimeout docstring) -- and asyncio.wait_for always raises this one.
            #
            # Executor.shutdown(cancel_futures=True) is not a substitute for this: it
            # only cancels futures that have not started running yet [VERIFIED:
            # inspect.signature(ProcessPoolExecutor.shutdown), 02-RESEARCH.md Pattern 2
            # -- `(self, wait=True, *, cancel_futures=False)`]. A future already
            # executing OCCT code is untouched by it: the wait would end while the work
            # continued, and under D-07's affinity every later request for this hash
            # slot would queue up behind a build nobody is waiting for. Terminating the
            # OS process is the only way found to actually stop it.
            #
            # `_processes` is private, undocumented CPython -- confirmed present on
            # 3.12.13 this session (02-RESEARCH.md Assumption A3). If a future
            # interpreter removes or renames it,
            # tests/test_pool.py::test_executor_processes_attribute_still_exists fails
            # `make verify` loudly, rather than this path silently degrading into an
            # abandoned future that never gets killed.
            for proc in executor._processes.values():
                proc.terminate()
            self.recreate_for(p)
            raise BuildTimeout(
                f"Build exceeded the {self.timeout}s per-build timeout. Try a coarser "
                "quality or fewer teeth."
            ) from None
        except BrokenProcessPool:
            # The worker died on its own (crash, OOM-kill, ...) rather than being
            # terminated by us -- concurrent.futures raises this from the awaited call
            # automatically [VERIFIED: BrokenProcessPool.__mro__, 02-RESEARCH.md "Don't
            # Hand-Roll"]. Same remedy as the timeout case: the dead slot is replaced
            # rather than staying dead. Re-raised so app.py maps it to its own status
            # code (D-12) instead of this module deciding HTTP semantics.
            self.recreate_for(p)
            raise

    async def export(self, p: GearParams, fmt: str, quality: str) -> bytes:
        return await self._run_with_timeout(p, build_export, p, fmt, quality)

    def shutdown(self) -> None:
        for executor in self._executors:
            executor.shutdown(wait=False)
