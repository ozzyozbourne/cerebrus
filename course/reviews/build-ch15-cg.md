# Build: Chapter 15, Lab 5 conjugate gradient (phase 4)

## What was built
- `course/programs/07-cg/`: CG on a 7-point 3-D Laplacian, W x H PEs with a Z-cell column ("pencil") each.
  Adapted from SDK 2.10.1 `benchmarks/conjugate-gradient` (kernel.csl + kernel_cg.csl, attribution in headers).
  Both loops in one program: host-driven (one RPC per phase) and device-driven (state-machine task 12),
  chosen by what `phase_done()` (the libraries' `f_callback`) does. Per-phase TSC profile (`PROFILE`), rho and
  TSC history. `lib/` holds `stencil_3d_7pts` and `allreduce` copied from SDK benchmark-libs; the only edit
  is the two dispatch import paths (`lib/stencil_3d_7pts/wse3|wse2/pe.csl`).
  Knobs: W, H, Z, ITERS, EPS, HOST_ITERS, BLOCK, PROFILE, ARCH. run.py uses `suppress_simfab_trace=True`
  (long runs otherwise write GBs of traces).
- `course/src/15-lab-cg.html` -> built `course/15-lab-cg.html`: problem + CG, pencil mapping (figure),
  module composition (module graph, resource-budget widget with measured clash experiments), import-path trap,
  allreduce mechanism/barrier, code, two loops, profile (iteration widget incl. derived real-system view),
  scaling (grid table, Z/BLOCK table, cost-model widget, measured convergence figure vs CG bound),
  4 exercises, 6-question quiz.

## Measurements (SDK 2.10.1 simulator, TSC on centre PE unless stated)
- Default 5x5x5, WSE-3: 15 iterations; device loop 4,574 cyc/iter (axpy 352, SpMV 1,866, dot 165,
  allreduce 1,898, control 295); host loop 5,790-5,798 (control ~1,550). All 25 PEs 4,574; allreduce share
  1,898-2,126. PROFILE=0: 4,261 / 5,488. Whole run 145,166-147,084 cycles. HOST_ITERS=15: 5,783.
- WSE-2: 15 iterations; device 4,186 (422/1,756/163/1,561/285), host 5,333; PROFILE=0 3,782 / 4,984. 129,365 cycles.
- Grid sweep WSE-3, Z=5, 6 iterations (cyc/iter, allreduce): 3x3 4,235/1,551; 8x8 5,146/2,462;
  12x12 5,898/3,214; 16x16 6,650/3,966; 16x4 5,594/2,910; 4x16 5,450/2,766.
  Fit allreduce = 958 + 100 W + 88 H (exact to <=30 cycles on all 7). WSE-2 12x12: 5,339/2,705.
- Z sweep WSE-3 5x5 (cyc/iter, SpMV, dot, axpy): Z20 8,688/5,722/315/441; Z50 17,282/13,945/615/512;
  Z100 32,004/27,782/1,115/898; Z100 BLOCK10 10,706/6,483; Z100 BLOCK100 6,573/1,957 (allreduce rose to 2,292, unexplained).
- Convergence to 1e-5: 5^3 15 it, 8^3 24 it (5,746 cyc/iter), 12^3 34 it (7,664); CG bounds 23/35/51 (derived).
- Clash experiments (5x5, WSE-3 unless noted): queue 2->4, color 8->7, color 8->22, task 12->14 = compile
  errors (messages quoted on page); stencil UT 3->2 runs (4,595); WSE-2 allreduce queue 2->3 runs (4,180).

## Sources
SDK 2.10.1 CG benchmark (README, commands_wse3.sh BLOCK_SIZE:2, layout comments), benchmark-libs source;
Golub & Van Loan Alg. 10.2.1 / Thm 10.2.6; cross-chapter notes 2 (850 MHz), 16, 17, 19, 20; Ch07 200 us/command.

## Notes / open issues
- Corrected during build: the allreduce library takes NO microthread parameter (compiler-assigned); the ledger
  comment in layout.csl and the page say so. On WSE-2 output queues are not color-bound, so stencil and
  allreduce can share output queue 3 (safe only because they never overlap).
- Real-system host-loop cost (~1 ms/iter, ~99.5% waiting) is derived from the SDK's 200 us/command, not measured.
- Whole-wafer allreduce (~180k cyc/iter) is a 60x extrapolation of the fit; labelled as such.
- The allreduce +394 cycles at BLOCK=100 was not investigated.
- course.js/course.css untouched. build.py rebuilt all lab pages (no content change to others).
