#!/usr/bin/env bash
# Knobs (environment): W x H PEs, Z cells per PE (z-column), ITERS = max CG iterations,
# HOST_ITERS = iterations of the (slow-to-simulate) host-driven loop,
# EPS = stop when |r| <= EPS*|b|, PROFILE = 1|0 (per-phase timers), ARCH = wse3 | wse2.
#   e.g.  W=8 H=8 Z=20 ITERS=40 bash commands.sh
# Self-contained: lib/ holds the two SDK benchmark libraries this program imports.
set -e
W=${W:-5}; H=${H:-5}; Z=${Z:-5}; ITERS=${ITERS:-30}; EPS=${EPS:-1e-5}; PROFILE=${PROFILE:-1}
cslc --arch=${ARCH:-wse3} ./layout.csl --fabric-dims=$((W+7)),$((H+2)) --fabric-offsets=4,1 \
  --params=width:$W,height:$H,MAX_ZDIM:$Z,MAX_ITE:$ITERS,BLOCK_SIZE:${BLOCK:-2},PROFILE:$PROFILE \
  -o out --memcpy --channels 1
cs_python run.py --name out --zdim $Z --max-ite $ITERS --eps $EPS --host-ite ${HOST_ITERS:-3}
