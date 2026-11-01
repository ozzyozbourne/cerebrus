#!/usr/bin/env bash
set -e
R=${R:-6}; M=${M:-32}
cslc --arch=${ARCH:-wse3} ./layout.csl --fabric-dims=8,$((R+2)) --fabric-offsets=4,1 \
  --params=R:$R,M:$M -o out --memcpy --channels 1
cs_python run.py --name out
