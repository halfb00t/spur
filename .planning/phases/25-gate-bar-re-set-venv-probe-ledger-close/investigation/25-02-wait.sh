# the wait (25-01)
X=1.5
CAP=900
NEED=3
EVERY=30
ok=0
t0=$(date +%s)
while :; do
  l1=$(sysctl -n vm.loadavg | awk '{print $2}')
  busy=$(pgrep -fl '[p]ytest|[p]re_commit|[m]ake verify' | wc -l | tr -d ' ')
  if awk -v l="$l1" -v x="$X" 'BEGIN{exit !(l<x)}' && [ "$busy" = 0 ]; then ok=$((ok+1)); else ok=0; fi
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$l1" "$busy" "$ok" >> "$S/$L.wait.tsv"
  if [ "$ok" -ge "$NEED" ]; then
    printf 'IDLE\t%s\n' "$(date -u +%FT%TZ)" >> "$S/$L.wait.tsv"
    exit 0
  fi
  if [ $(( $(date +%s) - t0 )) -ge "$CAP" ]; then
    printf 'GAVE_UP\t%s\n' "$(date -u +%FT%TZ)" >> "$S/$L.wait.tsv"
    exit 3
  fi
  sleep "$EVERY"
done
