#!/usr/bin/env bash
set -e
cslc --arch=wse3 ./layout.csl --fabric-dims=8,3 --fabric-offsets=4,1 \
  --params=N:100 --params=MEMCPYH2D_DATA_1_ID:0 -o out --memcpy --channels 1
cs_python run.py --name out
