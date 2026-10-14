# one run (25-01)
LOG="$S/$L.log"
l_before=$(sysctl -n vm.loadavg | awk '{print $2}')
t_start=$(date -u +%FT%TZ)
if [ "$ARM" = A ]; then
  PYTEST_ADDOPTS=--ignore=tests/test_browser.py /usr/bin/time -p timeout -k 30 900 make verify > "$LOG" 2>&1
else
  /usr/bin/time -p timeout -k 30 900 make verify > "$LOG" 2>&1
fi
status=$?
echo "make verify exit $status" >> "$LOG"
t_end=$(date -u +%FT%TZ)
l_after=$(sysctl -n vm.loadavg | awk '{print $2}')
rev=$(git rev-parse --short HEAD)
machine=$(.venv/bin/python -c 'import bench; print(bench.machine_facts())')
printf 'run-record\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$L" "$ARM" "$status" "$t_start" "$t_end" "$l_before" "$l_after" "$rev" "$machine" >> "$LOG"
exit 0
