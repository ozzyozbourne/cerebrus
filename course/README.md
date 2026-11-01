# Wafer-Scale Computing — a 15-chapter visual course

Open `course/index.html` in a browser. It is plain static HTML with no build step needed to read it and no external dependencies. Every chapter has SVG diagrams and most have an interactive widget.

| Part | Chapters |
|---|---|
| I · Why wafer-scale | 1 The memory wall · 2 One chip, one wafer |
| II · The machine | 3 Processing element · 4 Fabric · 5 Tasks · 6 DSDs · 7 Host I/O and memcpy · 8 Systems |
| III · Programming | 9 CSL and the toolchain · 10 Lab 1 · 11 Lab 2 · 12 Lab 3 |
| IV · Comparison | 13 Tenstorrent · 14 NVIDIA GPUs · 15 Head to head |

## Programs

`course/programs/` holds five original CSL programs. Each has `layout.csl`, `pe_program.csl`, `run.py`, `commands.sh`, and `expected_output.txt` from a real simulator run.

| Program | Teaches | WSE-3 cycles |
|---|---|---|
| 01-saxpy | layout, memcpy copy mode, RPC, memory DSDs | 7,740 |
| 02-wavelet-tasks | streaming memcpy, input queues, data tasks, barrier RPC | 7,020 |
| 03-row-reduce | colors, routes, checkerboard, fabric-to-fabric DSD op | 4,748 |
| 04-heat-stencil | halo exchange on 4 colors, completion tasks, iteration | 10,291 |
| 05-column-broadcast | multicast routes | 5,456 |

All five pass on both `--arch=wse3` and `--arch=wse2` with the Cerebras SDK 2.10.1 simulator.

```bash
bash .claude/skills/cerebras-sdk/scripts/setup.sh      # one-time SDK install
source /home/user/cerebras-sdk/env.sh
ARCH=wse3 bash course/programs/run_all.sh
ARCH=wse2 bash course/programs/run_all.sh
```

## Editing the lab chapters

Chapters 10–12 are generated from `course/src/*.html`, so their code listings are copied from the validated program files. After editing a program or a template, run:

```bash
python3 course/tools/build.py
```

## Sources

The facts come from the research in `reports/Cerebras architecture course research.md` and `research_notes/`. Every number in the course carries a provenance tag (Vendor, Indep, Analyst, SDK 2.10.1, Measured, Derived). The research sessions could not open most vendor documentation sites directly. Many web figures therefore come from search-engine extracts of the primary sources and should be checked against those documents before you rely on them.
