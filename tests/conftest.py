"""Shared fixtures for the whole suite.

Autouse root-logger reset (Phase 3): `records.configure()` installs a handler bound to
whatever `sys.stderr` was at construction time. Without this fixture, any test that
calls `configure()` directly, or drives the app's `lifespan()` (which also calls it),
would leave that handler -- and the stream object it captured -- installed on the root
logger for every test that runs afterwards, including tests with no interest in logging
at all. Snapshotting the handler list and level before each test and restoring them
after is also what lets each `configure()`-touching test in tests/test_records.py start
from a genuinely unconfigured root logger, rather than depending on test execution order.

Autouse solid-cache reset (Phase 3, discovered while adding this file): `model.py`'s
`_build_cached` is a process-global `lru_cache` returning the *same* `cq.Solid` object
for identical parameters, and `Shape.exportStl()` has a side effect on that shared
object (attaching a coarser mesh) that skews a *later* `.BoundingBox()` call on it --
even one made by a wholly unrelated test. tests/test_api.py's new all-default-gear
logging test and tests/test_model.py's own all-default `kw={}` case both build the
literal same `GearParams()`; without this reset, whichever ran second silently measured
the first one's leftover mesh instead of exact geometry. See
docs/tech_debt/active/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md for
the underlying defect (no production code calls `.BoundingBox()` today, so this is a
test-isolation fix, not a shipped-behavior one). Clearing before each test matches the
unique-parameter-per-test discipline the rest of the suite already follows for the
app-level byte cache.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator

import pytest

from spur.model import _build_cached


@pytest.fixture(autouse=True)
def _reset_root_logger() -> Iterator[None]:
    root = logging.getLogger()
    handlers_before = list(root.handlers)
    level_before = root.level
    yield
    for handler in list(root.handlers):
        if handler not in handlers_before:
            root.removeHandler(handler)
    root.setLevel(level_before)


@pytest.fixture(autouse=True)
def _reset_solid_cache() -> None:
    _build_cached.cache_clear()
