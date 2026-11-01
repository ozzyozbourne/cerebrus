#!/usr/bin/env bash
set -e
P=${P:-8}; M=${M:-32}
cslc --arch=${ARCH:-wse3} ./layout.csl --fabric-dims=$((P+7)),3 --fabric-offsets=4,1 \
  --params=P:$P,M:$M -o out --memcpy --channels 1
cs_python run.py --name out
