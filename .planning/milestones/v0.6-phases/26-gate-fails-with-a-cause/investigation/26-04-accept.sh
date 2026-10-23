#!/bin/bash
# 26-04 acceptance: implements `#### The rule (26-04)` in bench/RESULTS.md, committed in 957539c.
# Run from the repo root. Interleaved A1 B1 ... A10 B10, one at a time, no retry, no early stop.
set -u
D=.planning/phases/26-gate-fails-with-a-cause/investigation
HASH_A=d88ba80e08cfcaf0c522ca0d688d246e02eda31dc3c234eb4cab90eaa3ab8b3b
HASH_B=b56df86990cb4a5547bc776b0979355b4b3e5927c522a5a11f43e03c1dc01ba5
FILE_A=$D/26-04-arm-before.test_pool.py.txt
FILE_B=$D/26-04-arm-after.test_pool.py.txt
sum() { shasum -a 256 < tests/test_pool.py | cut -d' ' -f1; }
load() { sysctl -n vm.loadavg | awk '{print $2}'; }
.venv/bin/pip freeze 2>/dev/null | grep -iE '^(pytest|pytest-xdist|pytest-cov|coverage)==' > $D/26-04-accept-tools.log
for k in 1 2 3 4 5 6 7 8 9 10; do
  for arm in A B; do
    if [ $arm = A ]; then src=$FILE_A; want=$HASH_A; else src=$FILE_B; want=$HASH_B; fi
    cp "$src" tests/test_pool.py
    [ "$(sum)" = "$want" ] || { echo "HASH MISMATCH before $arm$k" >&2; exit 2; }
    log=$D/26-04-accept-$arm-$k.log
    lb=$(load); t0=$(date -u +%FT%TZ); s0=$(date +%s)
    timeout 600 make test PYTEST_ARGS="tests/test_pool.py tests/test_api.py -k 'not forced_gc' --cov-fail-under=0" > "$log" 2>&1
    rc=$?
    s1=$(date +%s); t1=$(date -u +%FT%TZ); la=$(load)
    echo "exit $rc" >> "$log"
    status=ok; [ $rc -eq 124 ] && status=killed
    [ $rc -ne 0 ] && [ $rc -ne 124 ] && status=red
    after=$(sum)
    printf 'run-record\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$arm" "$k" "$status" "$t0" "$t1" "$((s1-s0))" "$lb" "$la" "$after" >> "$log"
    [ "$after" = "$want" ] || { echo "HASH MISMATCH after $arm$k" >&2; exit 2; }
  done
done
cp "$FILE_B" tests/test_pool.py
[ "$(sum)" = "$HASH_B" ] && echo "done; after-arm restored" > $D/26-04-accept-done.log
