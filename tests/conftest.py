"""Shared fixtures for the whole suite.

Autouse root-logger reset (Phase 3): `records.configure()` installs a handler bound to
whatever `sys.stderr` was at construction time. Without this fixture, any test that
calls `configure()` directly, or drives the app's `lifespan()` (which also calls it),
would leave that handler -- and the stream object it captured -- installed on the root
logger for every test that runs afterwards, including tests with no interest in logging
at all. Snapshotting the handler list and level before each test and restoring them
after is also what lets each `configure()`-touching test in tests/test_records.py start
from a genuinely unconfigured root logger, rather than depending on test execution order.
"""

from __future__ import annotations

import logging
import sys
from collections.abc import Iterator

import din5480_tables_fixture
import pytest

from spur import din5480_tables
from spur.din5480_tables import Tables


@pytest.fixture(autouse=True)
def _no_table_file(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Every test starts with no table file named and the loader empty (34-RESEARCH Pitfall 4).

    A developer who exported SPUR_DIN5480_TABLES would otherwise turn every "no file"
    assertion red, and the loader's module state would leak from one test to the next on
    the same xdist worker. Real-file tests read the variable at collection, before this
    runs.
    """
    monkeypatch.delenv(din5480_tables.ENV_VAR, raising=False)
    din5480_tables.reset()
    yield
    din5480_tables.reset()


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


def _forget_built_solids(monkeypatch: pytest.MonkeyPatch) -> None:
    # Only modules that are already imported: importing spur.model here would load the
    # kernel into every light run.
    model = sys.modules.get("spur.model")
    if model is not None:
        model._build_cached.cache_clear()
    app = sys.modules.get("spur.app")
    if app is not None:
        monkeypatch.setattr(app, "_EXPORTS", app._BlobCache(1 << 20))


@pytest.fixture
def with_tables(monkeypatch: pytest.MonkeyPatch) -> Iterator[Tables]:
    """The synthetic tables installed for one test, with the solid and export caches emptied.

    Both caches are keyed by the parameters only, which is correct in production because the
    tables are fixed per process (D-13), and wrong inside one test process that flips them:
    the second build would return the first build's solid (34-RESEARCH Pattern 3). A test
    that builds a shaft with tables requests this fixture.
    """
    tables = din5480_tables_fixture.build()
    din5480_tables.install(tables)
    _forget_built_solids(monkeypatch)
    yield tables
    _forget_built_solids(monkeypatch)
