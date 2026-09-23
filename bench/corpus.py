"""L07's own memory-sweep corpus: 40 distinct 160-199 tooth gears.

This is the exact workload `docs/plan-2026-09-21.md`'s F2 measured against -- the run
that took anon RSS from ~3.0 GiB (still climbing) to a flat 358 MiB, the number
`compose.yaml`'s `mem_limit: 2g` was earned against. `bench/memory.py` reuses it
verbatim for the N = 1, 2, 4 sweep (D-18) so the new multi-process ceiling is comparable
with the one already on record.

Do not narrow, shorten or re-pick this corpus to make a ceiling look better: a different
workload produces a number that cannot be compared with the one on record, which
defeats the entire point of measuring (02-02-PLAN.md prohibitions).
"""

from __future__ import annotations


def corpus() -> list[dict[str, object]]:
    """40 distinct gears, tooth counts 160 through 199 inclusive, one per tooth count.

    Generated deterministically from the tooth count alone -- two runs on two machines
    drive the identical workload. Query-parameter dictionaries, ready to hand to an HTTP
    client against `/api/model.{stl,step}`. Every other `GearParams` field is left at
    its default on purpose: L07's own corpus varied only teeth, and comparing this
    phase's ceiling to that one means holding everything else fixed too.
    """
    return [{"teeth": teeth} for teeth in range(160, 200)]
