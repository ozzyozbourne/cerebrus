#!/usr/bin/env bash
# Usage: bash commands.sh [N] [HALF] [PAD]     e.g.  bash commands.sh 1024 1 0
set -e
cslc --arch=${ARCH:-wse3} ./layout.csl --fabric-dims=8,3 --fabric-offsets=4,1 \
  --params=N:${1:-64},HALF:${2:-0},PAD:${3:-0} -o out --memcpy --channels 1
cs_python run.py --name out
