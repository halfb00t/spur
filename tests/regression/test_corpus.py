"""`corpus.cases()`'s collision guard (WR-01): a synthesized mate-case key must never
silently overwrite an existing `result` entry -- the exact failure mode `seen_tags`
already guards for literal tags."""

from __future__ import annotations

import corpus
import pytest
from corpus import Entry, cases


def test_a_synthesized_mate_key_colliding_with_an_existing_entry_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An earlier entry's literal tag ("a+mate=40") happens to equal the mate key a
    later entry ("a", mate=40) would synthesize -- `cases()` must raise naming the
    colliding key, not drop the earlier case."""
    monkeypatch.setattr(corpus, "ENTRIES", (
        Entry("a+mate=40", {"teeth": 20}),
        Entry("a", {"teeth": 19}, 40),
    ))
    with pytest.raises(ValueError, match=r"corpus key collision: a\+mate=40"):
        cases()
