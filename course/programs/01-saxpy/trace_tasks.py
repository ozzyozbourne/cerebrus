#!/usr/bin/env python3
"""Group the simulator's instruction trace into runs of one task on one PE.

Run the program with the trace on:
    SINGULARITYENV_SIMFABRIC_DEBUG=inst_trace cs_python run.py --name out
then:
    python3 trace_tasks.py sim.log P4.1        # P4.1 = your PE at fabric offset (4,1)
Each output line is one run of consecutive instructions from one task:
    task  first-last cycle  (length, instructions)  notable opcodes
"""
import re, sys

NOTABLE = ("FMAC", "FMUL", "FADD", "FMOV", "MOV32", "BLK", "UBLK", "ACTVT", "OQ")
log, pe = sys.argv[1], sys.argv[2]
pat = re.compile(r"^@(\d+) " + re.escape(pe) + r": .*\[EX OP\] . 0x[0-9a-f]+: (T\d+)\s+(?:\S+\?\s+)?(\S+)")
runs = []                                   # [task, first, last, count, opcodes]
for line in open(log, errors="replace"):
    m = pat.match(line)
    if not m:
        continue
    cyc, task, op = int(m.group(1)), m.group(2), m.group(3)
    if runs and runs[-1][0] == task and cyc - runs[-1][2] < 40:
        r = runs[-1]; r[2] = cyc; r[3] += 1; r[4].add(op)
    else:
        runs.append([task, cyc, cyc, 1, {op}])
for task, a, b, n, ops in runs:
    key = " ".join(sorted(o for o in ops if o.startswith(NOTABLE)))
    print(f"{task:4} {a:6}-{b:<6} ({b - a + 1:5} cyc, {n:4} instr) {key}")
