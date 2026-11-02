# Build report: Chapter 14, Lab 4: 2-D GEMM with SUMMA

## What was built
- `programs/06-summa/` (layout.csl, pe_program.csl, run.py, commands.sh, expected_output.txt). Adapted from SDK 2.10.1
  `benchmarks/gemm-collectives_2d`, with attribution in the header. Changes from the SDK version:
  - course style and a resource map (colors 0–3, local tasks 8–15, queues 2–5, microthreads 2/3, task 29 = library teardown handler);
  - TSC stamps on every PE: at main, then per step (broadcasts issued, compute start, compute end), then at exit;
  - run.py prints the far-corner PE's split into broadcast, compute and other;
  - knobs P, T (or Mt/Kt/Nt), ARCH and KERNEL. KERNEL=1 is an outer-product variant: Kt × (@fmuls + @fadds) over 2-D zero-stride DSDs.
  - The GEMV warm-up is the same program with `Nt=1` (batched GEMV), so there is still only one program directory.
  - run.py passes `suppress_simfab_trace=True`. Without it, large tiles wrote GBs of simfab traces; the default size behaves the same either way.
- Defaults P=4, T=8: PASS on WSE-3 (36,959 simulated cycles, kernel 14,422 TSC) and on WSE-2 (33,658; kernel 13,514). About 30 s wall time each. The program directory is clean.
- `src/14-lab-gemm.html` → `14-lab-gemm.html` (built with tools/build.py, which also rebuilt 11–13 and 15 unchanged). Sections:
  - SUMMA from the Ch12 GEMV (Nt=1 warm-up);
  - 2-D data layout and host I/O, with a figure;
  - `<collectives_2d>` internals: ownership, run-time `reset_routes`, the FSM, the root's teardown control wavelet, task 29 → lock → callback, and a chain-vs-tree callout;
  - the two-network join;
  - a code walk-through;
  - measurements with a table, a "where the time goes" bank-clash callout and the roofline comparison;
  - a 9-step design/budget procedure applied to the kernel;
  - wafer-scale extrapolation (Derived);
  - 6 exercises with measured or derived answers;
  - a 7-question Check yourself.
- Widgets (3, plus a JS-drawn layout figure and a measured table):
  - a SUMMA step animation (P 2–6, tile size, play/next/reset, click a PE);
  - a measured-vs-model chart (chip, y = cycles/step or cycles/MAC, tile slider, hover points ↔ table rows);
  - a budget calculator (P, Mt, Kt, Nt, kernel, chip, clock → memory bar against the measured link limits, colors/tasks/queues/fabric, predicted cycles, % of ideal, TFLOP/s).
- 18-comparison.html: one sentence added to the GEMM paragraph in "A second workload", with measured numbers tagged Measured, Ch. 14.
- 17-gpu.html: "(Chapter 13)" → link to Chapter 14 in "Tiling a matmul".

## Measured (TSC, far-corner PE, SDK 2.10.1 simulator)
- Per step, WSE-3, kernel 0: T=4/8/16/24/32 → broadcast 578/650/1,033/1,673/2,569 and compute 623/2,903/17,835/50,348/103,724.
  - Broadcast fit: ≈ 520 + 1·(words of A + B tiles) on WSE-3 and ≈ 429 + 1·words on WSE-2.
  - Compute share of the kernel is 80% at T=8 and 97.5% at T=32.
- Flat in P: at T=8 a WSE-3 broadcast step costs 626/650/653/654 cycles for P=2/4/6/8, and compute is 2,903 at every P. Kernels: 7,188/14,422/21,624/28,828. WSE-2 at P=2/4/8: 6,791/13,514/26,967.
- Against the ideal of 1 f32 MAC/cycle (T³ cycles per step):
  - kernel 0 reaches 18% (T=8) to 32% (T=32) on WSE-3 and 18–34% on WSE-2;
  - kernel 1 reaches 51% at T=32 on WSE-3 (63,890 cycles) and 47% on WSE-2 (69,026).
- Cause, shown by ablations:
  - About 29–38 cycles per @fmacs of fixed loop overhead. With no compute at all the task costs 27 cycles per step.
  - The operand bank clash (CCN 23). A Mt sweep gives 2·Mt + 29 for Mt = 8/16/32 and ≈ 1.25·Mt + 31 for Mt = 15/17/33.
  - The fix: put A_tile and A_buf in one array and pad C by 1–3 words. Compute per step becomes 13,739 instead of 17,835 at T=16, exactly 1 cycle per MAC, and 70,956 instead of 103,724 at T=32 (46% of ideal). Padding C alone fixed only the steps that use A_tile; the PEs then waited for each other and the total did not improve.
  - In kernel 1, @fmuls on the zero-stride DSDs costs ≈1.6 (WSE-3) / 1.35 (WSE-2) cycles per element, and @fadds 0.5 / 1.0.
- Memory link limits (square tiles):
  - WSE-3: kernel 0 links T=45 and fails at 46; kernel 1 links 41 and fails at 42.
  - WSE-2: kernel 0 links 46 and fails at 47; kernel 1 links 39 and fails at 40 (".data.hi"; why it is lower is unexplained).
- GEMV warm-up (P=4, Mt=Kt=16, Nt=1):
  - WSE-3: broadcast 717 + compute 1,114 per step, kernel 7,533;
  - WSE-2: 703 + 706, kernel 5,866. This WSE-2 build happened to land on a clash-free alignment.

## Sources
SDK 2.10.1: `benchmarks/gemm-collectives_2d` and `csl-libs/collectives_2d/{pe,params,ctrl_wavelet}.csl` (read from the SIF). CROSS_CHAPTER_NOTES 12, 13, 16, 19, 20, 22–24 (hop costs, op rates, collision rule, library ≈700 cycles, store-and-forward 348 vs 101). HC22 1.1 GHz clock. Derived items are tagged: wafer extrapolation, chain/tree model and fits.

## Open issues
- Not isolated:
  - why the two concurrent broadcasts cost about the sum of their words (partial overlap for non-square tiles);
  - why the fixed per-@fmacs overhead grows from ≈29 to ≈38 with Kt·Nt;
  - why @fmuls on zero-stride DSDs runs below 1 element/cycle;
  - the low WSE-2 kernel-1 memory limit.
- TSC noise: one rerun of the default under load gave 14,431/2,610 instead of 14,422/2,601 (broadcast +9 cycles). The table mixes runs with traces on (most points) and off; compute values were identical.
- The full `run_all.sh` was not run, because other agents' programs were being built at the time. 06-summa was run with its own commands.sh on both chips (PASS).
- Not done: a static-multicast vs library comparison (SDK-coverage proposal item 7), and the course README program table (not in scope: "touch nothing else").
- The page links to 15-lab-cg.html (Ch15) from the chain/tree callout and an exercise.
