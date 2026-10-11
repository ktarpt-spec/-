#!/bin/sh
# usage: render_bl.sh <outdir> <samples> <w> <h> view...
PY=${BPY:-/tmp/claude-0/-home-user--/e4171e91-f2e5-5ba4-a09a-54a6d4c5711f/scratchpad/bl/venv/bin/python}
out=$1; smp=$2; w=$3; h=$4; shift 4
for v in "$@"; do
  t0=$(date +%s)
  "$PY" "$(dirname "$0")/scene_blender.py" "$v" "$out/$v.png" "$smp" "$w" "$h" > "$out/$v.log" 2>&1 && echo "$v ok $(( $(date +%s) - t0 ))s" || { echo "$v FAIL"; tail -5 "$out/$v.log"; }
done
