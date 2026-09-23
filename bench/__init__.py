"""Measurement harness for this phase's two success criteria (D-16).

A rerunnable `make bench`, committed so its numbers stay falsifiable by whoever doubts
them later -- not a script run once in a session and quoted from memory afterwards.

`bench.latency` measures `/api/health` under load on the host, the same way the debt
file's own baseline was produced (D-17). `bench.memory` sweeps container memory over
L07's own 40-gear corpus (D-18). Neither is part of `make verify`: both need a running
service and minutes, and a latency assertion on shared hardware would flap until someone
stopped believing it (D-16).
"""

from __future__ import annotations

import os
import platform


def machine_facts() -> str:
    """CPU count, architecture and total RAM.

    Every number this harness reports must carry the machine that produced it (D-17) --
    a measurement's meaning changes with the hardware behind it, so this is printed
    alongside every scenario and every sweep row, shared by bench.latency and
    bench.memory rather than computed twice.
    """
    cpu = os.cpu_count()
    ram = _total_ram_gib()
    ram_text = f"{ram:.1f} GiB RAM" if ram is not None else "RAM unknown"
    return f"{cpu if cpu is not None else '?'} CPUs, {platform.machine()}, {ram_text}"


def _total_ram_gib() -> float | None:
    """Total RAM in GiB via `os.sysconf`, or `None` where the platform exposes neither.

    `[VERIFIED this session]`: `os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')`
    on this arm64 macOS dev host agrees exactly with `sysctl hw.memsize` (34359738368
    bytes = 32 GiB). Both sysconf names are also defined on glibc Linux, which is where
    the memory half of this harness actually runs (D-17), so the same call is expected
    to hold there too.
    """
    try:
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / (1024**3)
    except (ValueError, OSError, AttributeError):
        return None
