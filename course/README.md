# Wafer-Scale Computing — an 18-chapter visual course with five appendices

Open `course/index.html` in a browser. It is plain static HTML with no build step needed to read it and no external dependencies. Every chapter has SVG diagrams and most have an interactive widget.

| Part | Chapters |
|---|---|
| I · Why wafer-scale | 1 The memory wall · 2 One chip, one wafer |
| II · The machine | 3 Processing element · 4 Fabric · 5 Tasks · 6 DSDs · 7 Host I/O and memcpy · 8 Systems · 9 From model to tokens |
| III · Programming | 10 CSL and the toolchain · 11 Lab 1 · 12 Lab 2 · 13 Lab 3 · 14 Lab 4 (SUMMA GEMM) · 15 Lab 5 (CG solver) |
| IV · Comparison | 16 Tenstorrent · 17 NVIDIA GPUs · 18 Head to head |
| Appendices | A Glossary and number formats · B CUDA to CSL, budgets and constants · C Measuring and observing · D SDK example index · E Sources and unverified figures |

## Programs

`course/programs/` holds seven CSL programs (06 and 07 adapted from SDK benchmarks, with attribution). Each has `layout.csl`, `pe_program.csl`, `run.py`, `commands.sh`, and `expected_output.txt` from a real simulator run.

| Program | Teaches | WSE-3 cycles |
|---|---|---|
| 01-saxpy | layout, memcpy copy mode, RPC, memory DSDs | 7,740 |
| 02-wavelet-tasks | streaming memcpy, input queues, data tasks, barrier RPC | 7,021 |
| 03-row-reduce | colors, routes, checkerboard, fabric-to-fabric DSD op | 6,860 |
| 04-heat-stencil | halo exchange on 4 colors, completion tasks, iteration | 11,665 |
| 05-column-broadcast | multicast routes | 7,620 |
| 06-summa | 2-D SUMMA GEMM with `<collectives_2d>`, TSC broadcast/compute split (adapted from SDK) | 36,971 |
| 07-cg | conjugate-gradient solver: stencil + allreduce modules, host vs device loop (adapted from SDK) | 145,003 |

All seven pass on both `--arch=wse3` and `--arch=wse2` with the Cerebras SDK 2.10.1 simulator.

```bash
bash .claude/skills/cerebras-sdk/scripts/setup.sh      # one-time SDK install
source /home/user/cerebras-sdk/env.sh
ARCH=wse3 bash course/programs/run_all.sh
ARCH=wse2 bash course/programs/run_all.sh
```

## Editing the lab chapters

Chapters 11–15 are generated from `course/src/*.html`, so their code listings are copied from the validated program files. After editing a program or a template, run:

```bash
python3 course/tools/build.py
```

## Sources

The facts come from the research in `reports/Cerebras architecture course research.md` and `research_notes/`. Every number in the course carries a provenance tag (Vendor, Indep, Analyst, SDK 2.10.1, Measured, Derived). The research sessions could not open most vendor documentation sites directly. Many web figures therefore come from search-engine extracts of the primary sources and should be checked against those documents before you rely on them.
