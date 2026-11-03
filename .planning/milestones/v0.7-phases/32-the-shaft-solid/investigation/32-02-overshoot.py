"""How far floor_mm can exceed its input (the unverified claim 32-01 carried forward).

floor(v*1000 + 1e-9)/1000 lands above v only when v*1000 is within 1e-9 below an integer.
Walks down from each lattice point n/1000 by fixed offsets and by single ulps and prints the
largest excess.
"""

import math


def floor_mm(v: float) -> float:
    return math.floor(v * 1000 + 1e-9) / 1000


worst = 0.0
worst_v = 0.0
count = 0
for n in range(1000, 500001, 7):
    for off in (1e-13, 5e-13, 9e-13, 1e-12, 1.0000001e-12, 1.1e-12, 2e-12, 5e-12):
        v = n / 1000 - off
        r = floor_mm(v)
        if r > v:
            count += 1
            if r - v > worst:
                worst, worst_v = r - v, v
print("rows exceeding v:", count, "max overshoot mm:", worst, "at", repr(worst_v))

worst_ulp = 0.0
for n in range(1000, 500001, 13):
    v = n / 1000
    for _ in range(40):
        v = math.nextafter(v, 0)
        worst_ulp = max(worst_ulp, floor_mm(v) - v)
print("nextafter walk max overshoot:", worst_ulp)
