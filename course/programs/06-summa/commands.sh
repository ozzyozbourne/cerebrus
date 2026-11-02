#!/usr/bin/env bash
# Knobs (environment): P = grid side (P x P PEs); T = tile size (sets Mt = Kt = Nt
# unless you set them); KERNEL = 0 (column @fmacs, as in the SDK) | 1 (outer product);
# ARCH = wse3 | wse2.     e.g.  P=6 T=16 KERNEL=1 ARCH=wse2 bash commands.sh
set -e
P=${P:-4}; T=${T:-8}; Mt=${Mt:-$T}; Kt=${Kt:-$T}; Nt=${Nt:-$T}; KERNEL=${KERNEL:-0}
cslc --arch=${ARCH:-wse3} ./layout.csl --fabric-dims=$((P+7)),$((P+2)) --fabric-offsets=4,1 \
  --params=P:$P,Mt:$Mt,Kt:$Kt,Nt:$Nt,kernel:$KERNEL -o out --memcpy --channels 1
cs_python run.py --name out
