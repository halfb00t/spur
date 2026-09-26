"""The closed pre-v0.2 corpus behind L05 and REQ-defaults-off-regression.

Every hand-written GearParams set from `tests/` and `README.md` as it existed at the end
of v0.1 (commit b3ca789) -- the shareable links that must still build the same part after
every v0.2 feature. This corpus never tracks later test edits: a source line that changes
after v0.2 lands does not change its entry here, because the whole point is proving v0.2
did not move the pre-v0.2 part. Do not narrow, shorten or re-pick it -- a record that
disappears is a guarantee that disappears (`bench/corpus.py`'s own rule, D-05).

Sources are `tests/` and `README.md` only (D-08); `docker/smoke.py` and `bench/corpus.py`
stay out on purpose. Only hand-written literal parameter sets enter -- parametrize lists,
inline `GearParams(...)` calls, `TestClient` `params=` dicts, `cli.main([...])` argument
lists, and the README's own examples (D-09). Machine-generated grids (the centre-distance
solver's cross-check) and sets that fail validation cannot enter by construction.
"""

from __future__ import annotations

from typing import NamedTuple

from spur.params import GearParams


class Entry(NamedTuple):
    """One hand-written parameter set as its source wrote it, tagged by where it lives."""

    tag: str
    params: dict[str, object]
    mate: int | None = None


ENTRIES: tuple[Entry, ...] = (
    Entry("README:export-defaults", {}),
)


class Case(NamedTuple):
    """A deduplicated corpus entry: one GearParams (or one (GearParams, mate) pair),
    plus every source tag that produced it."""

    params: dict[str, object]
    mate: int | None
    sources: list[str]


def cases() -> dict[str, Case]:
    """Deduplicate ENTRIES by GearParams equality (and by (GearParams, mate) for mated
    sets), in listing order.

    The first entry whose GearParams is new opens a base case keyed by its own tag; a
    later entry with an equal GearParams only appends its tag to that case's sources. An
    entry that also names a mate opens or extends a second, mate-keyed case the same way,
    for the (GearParams, mate) pair. Insertion order in the returned dict is the order
    each case first appeared in ENTRIES.
    """
    result: dict[str, Case] = {}
    seen_tags: set[str] = set()
    base_keys: dict[GearParams, str] = {}
    mate_keys: dict[tuple[GearParams, int], str] = {}

    for entry in ENTRIES:
        if entry.tag in seen_tags:
            raise ValueError(f"duplicate corpus tag: {entry.tag}")
        seen_tags.add(entry.tag)

        p = GearParams.model_validate(entry.params)
        base_key = base_keys.get(p)
        if base_key is None:
            base_keys[p] = entry.tag
            result[entry.tag] = Case(params=entry.params, mate=None, sources=[entry.tag])
        else:
            result[base_key].sources.append(entry.tag)

        if entry.mate is not None:
            mate_key = mate_keys.get((p, entry.mate))
            if mate_key is None:
                case_key = f"{entry.tag}+mate={entry.mate}"
                mate_keys[(p, entry.mate)] = case_key
                result[case_key] = Case(params=entry.params, mate=entry.mate,
                                        sources=[entry.tag])
            else:
                result[mate_key].sources.append(entry.tag)

    return result
