#!/usr/bin/env bash
# Knobs (environment): P = PEs in the row, n = cells per PE, STEPS = timesteps,
# ALPHA = diffusion number, ARCH = wse3 | wse2.   e.g.  P=16 n=64 STEPS=100 bash commands.sh
set -e
P=${P:-8}; n=${n:-16}; STEPS=${STEPS:-50}; ALPHA=${ALPHA:-0.25}
cslc --arch=${ARCH:-wse3} ./layout.csl --fabric-dims=$((P+7)),3 --fabric-offsets=4,1 \
  --params=P:$P,n:$n -o out --memcpy --channels 1
cs_python run.py --name out --steps $STEPS --alpha $ALPHA
