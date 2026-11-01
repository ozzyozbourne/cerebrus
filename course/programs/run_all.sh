#!/usr/bin/env bash
# Compile + simulate every course program and report PASS/FAIL and simulated cycles.
# Usage: source /home/user/cerebras-sdk/env.sh; ARCH=wse3 bash run_all.sh   (or ARCH=wse2)
cd "$(dirname "$0")"
ARCH=${ARCH:-wse3}; export ARCH
fail=0
for d in 0*/; do
  d=${d%/}
  if (cd "$d" && timeout 600 bash commands.sh > run.log 2>&1 && grep -q 'SUCCESS!' run.log); then
    cyc=$(python3 -c "import json;print(json.load(open('$d/sim_stats.json'))['cycle_count'])")
    printf '%-24s %s  PASS  %8s cycles\n' "$d" "$ARCH" "$cyc"
  else
    printf '%-24s %s  FAIL  (see %s/run.log)\n' "$d" "$ARCH" "$d"; fail=1
  fi
  rm -rf "$d"/wio_flows_tmpdir.*
done
exit $fail
