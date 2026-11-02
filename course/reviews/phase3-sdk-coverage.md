# Phase 3: CSL language and SDK coverage audit

Scope: does the course need more chapters, judged against what SDK 2.10.1 ships (`extras/csl-extras-202604101435-6-d2f7d96e/examples`, 34 tutorials and 22 benchmarks, plus `csl-libs/` in the SIF). Method: I grepped every chapter for each example and module name, read the relevant sections, and compiled and ran two candidate lab programs on WSE-3 in a scratch directory, which I deleted afterwards.

## Coverage table

| SDK item | Where the course covers it | Status |
|---|---|---|
| gemv-00..05 (syntax, DSDs, memcpy, params, multi-PE) | Ch 9 "Three files" and "Language in one screen"; Ch 6; Ch 10 | Covered |
| gemv-06..08 (routes, multicast, checkerboard reduce) | Ch 11 programs 03/05, "Composing the two: a distributed GEMV" | Covered, labbed |
| gemv-09, topic-03 (streaming) | Ch 7 "Copy mode vs streaming mode"; Ch 10 program 02 | Covered |
| pipeline-01..03, topic-09 (FIFOs) | Ch 6 "FIFOs extend the tiny hardware queues"; Ch 5 | Covered |
| sdklayout-01..05 | Ch 9 "The other way to lay out: SdkLayout" (measured sdklayout-02) | Covered as a section |
| topic-01, 02, 10 (pointers, libraries, @map) | Ch 9 language table; Ch 6 builtins | Covered |
| topic-04 (sparse tensors), spmv-hypersparse | Ch 3 "Sparsity: skipping zeros"; Ch 5 | Concept covered; hypersparse is WSE-2 only |
| topic-05 (sentinels), 16 (queue flush), 15 (microthreads) | Ch 5 "Control tasks and sentinels", "Reusing a queue on WSE-3"; Ch 3/6 microthreads | Covered |
| topic-06/07/08/14 (switches, filters, color swap) | Ch 4 "Runtime flexibility" | Covered (color swap only named; it is WSE-2 only) |
| topic-11, `<collectives_2d>` | Ch 11 "The library version"; Ch 9 library map | **Explained, never run in 2-D** |
| topic-12/13, `<debug>`, `<simprint>`, inst_trace, csdb | Ch 9 "Debugging", error decoder, hang procedure; Ch 10 trace | Covered (csdb: help screens only) |
| `<time>`, kernel timing | Ch 10 "Measure the kernel itself"; Ch 11; Ch 12 | Covered, measured |
| `<memcpy>` internals, bandwidth-test | Ch 7 throughout | Covered |
| `<math>`, `<random>`, `<tile_config>`, `<layout>` | Ch 9 library map | Covered (table level) |
| `<message_passing>`, `<malloc>`, `<control>`, `<complex>`, `<dsd_ops>` | Ch 9 "also" row | Named only. Fine. |
| 7pt-stencil-spmv, 25-pt-stencil, benchmark-libs/stencil_3d_7pts | Ch 12 "How the SDK's stencils differ" | Covered as comparison |
| gemv-checkerboard-pattern, gemv-collectives_2d, row-col-broadcast | Ch 6 code excerpt; Ch 11; Ch 7 | Covered |
| single-tile-matvec | Ch 3, Ch 6, Ch 15 | Covered (memory/throughput numbers) |
| **gemm-collectives_2d (SUMMA)** | Ch 15 "A second workload", one sentence; "Where to go next" | **Uncovered as a program** |
| **conjugate-gradient, preconditioned CG, BiCGStab, power-method, benchmark-libs/allreduce** | Ch 15 "Choosing" row (names only); Ch 11 exercise cites allreduce's @fmaxs | **Uncovered** |
| fft-1d-2d, fft-3d, `kernels/fft` | Ch 6 DSD-arithmetic example (one line of fft.csl) | Mostly uncovered |
| cholesky, mandelbrot, wide-multiplication, residual, game-of-life, histogram-torus, `kernels/tally` | Ch 4 names game-of-life and histogram-torus; the rest absent | Uncovered (niche) |

Overall, the language, the runtime mechanisms (tasks, DSDs, queues, routes, switches, filters, teardown), host I/O and the toolchain are covered deeply. Most of it was measured on the simulator, and the depth matches or exceeds the SDK tutorials. Two things are missing. First, **every lab is 1-D**: a row, a column, or a rod. Second, **no lab composes several modules into a multi-phase algorithm**.

## Verdict

**Yes, one new chapter is clearly justified (2-D GEMM / SUMMA). A second (iterative solver) is justified but optional.** Nothing else meets the bar. Debugging, performance tuning, SdkLayout and the streaming topics are already sections with measurements. Promoting them to chapters would repeat Chapters 9 to 12.

## Ranked new-chapter proposals

### 1. Lab 4: A 2-D GEMM (SUMMA) with `<collectives_2d>` (strongly recommended)

**Why.** GEMM is the workload Chapters 1, 8, 13, 14 and 15 keep returning to, and Ch 15 compares the wafer on it with one sentence and no measurement. It is the only place the course would show:
- a genuinely 2-D decomposition (P × P tiles);
- runtime-rerouted collectives in action (Ch 4's switches, filters and teardown are explained but never exercised by a lab);
- a task join over two independent networks (`x_done` and `y_done`, Ch 5's "block + activate = join" in real code);
- the compute-bound regime, where `@fmacs` over tiles finally dominates. This is the opposite of Lab 3's message-bound result, and it lets the course test its own "messages, not memory, were the bottleneck" claim (Ch 15).

**Feasibility (measured).** `benchmarks/gemm-collectives_2d` compiles and runs unchanged: `cslc --arch=wse3 --fabric-dims=11,6 --params=P:4,Mt:14,Kt:14,Nt:14`, then `cs_python run.py` prints `SUCCESS` with `cycle_count: 91158`, in 58 s wall time. The device code is small (pe.csl 137 lines, layout.csl 56 lines), so it can be copied in as `programs/06-summa` in course style. Additions needed:
- `<time>` stamps around `main` to separate kernel from host I/O, as in Ch 10/12;
- a P and tile-size sweep;
- optionally, a variant with hand-written static multicast (program 05) instead of the library, to price the library's teardown and reroute overhead.

**Outline.**
1. The algorithm: P steps, broadcast an A column across rows and a B row down columns, then a local multiply-accumulate.
2. The code: `<collectives_2d>` params per PE, 2 colors and 2 entrypoints per dimension, home tile versus received buffer pointers.
3. One step inside: route rewrites, teardown, the double completion join.
4. The local kernel: `@fmacs` with a scalar from B over a column of A, and the DSD shapes.
5. Measurements: kernel cycles against tile size (communication ∝ tile², compute ∝ tile³), and the crossover point.
6. Memory budget: five tiles per PE in 48 KB, and the largest tile that fits.
7. Library versus static multicast: what runtime rerouting costs.
8. Scale to the wafer and set it against Ch 14's tiled GPU matmul and Ch 13's multicast matmul.

**Widgets:**
- a SUMMA step-through on a 4 × 4 grid, showing which tiles move at step i;
- a slider from tile size to compute/communication cycles, using measured points;
- a 48 KB memory-map bar for the chosen tile sizes.

**Slot.** After Ch 12 (stencil), as the fourth lab, before the Tenstorrent and GPU chapters, so Ch 13–15 can cite it. Renumber 13→14, 14→15, 15→16.

**Effort.** Medium: about 2–3 days, including the sweep runs at ~1 min each, plus Ch 15 table updates.

### 2. Lab 5: Composing modules: a conjugate-gradient solver (recommended if a fifth lab is wanted)

**Why.** Real CSL programs are built from several modules, each holding colors, queues and task IDs. CG is the SDK's canonical example. It combines `benchmark-libs/stencil_3d_7pts` (SpMV), `benchmark-libs/allreduce` (dot products) and a BLAS file. The colors are passed in as `C0_ID..C8_ID` params. The host drives the iteration with one RPC per phase (`f_spmv_Ap`, `f_eta`, `f_update_x_r_rho`…). The SDK also ships `device_run.py`, which moves the loop onto the device "to remove I/O pressure". Three things here are new to the course:
- budgeting colors and queues across libraries;
- a global allreduce on the critical path of every iteration;
- the cost of host-driven versus device-driven control. Ch 7 prices one RPC but never a loop of them.

**Feasibility (measured).** Copied as-is it fails: `Unable to open ./src/../../benchmark-libs/stencil_3d_7pts/layout.csl`. It needs `benchmark-libs/` as a sibling directory. With that, `commands_wse3.sh` (5 × 5 PEs, zDim 5, 2 iterations) prints `SUCCESS!`, `|xf_ref - xf_wse| = 3.05e-05`, `cycles_send = 14971`, in 24 s wall time. power-method and BiCGStab share the same structure.

**Outline:**
1. CG in ten lines of numpy.
2. The module graph and the color/queue ledger.
3. SpMV recap (link Ch 12).
4. The allreduce: a row reduce, then a column reduce, then a broadcast back.
5. Host loop versus device loop: cycles per iteration.
6. Where an iteration's time goes.
7. Scaling: allreduce latency ∝ width + height, compute ∝ zDim.

**Widgets:**
- a per-iteration timeline (SpMV / reduce / axpy);
- a color-ledger table that highlights clashes.

**Slot.** After the GEMM lab. **Effort.** Medium–high: 3–4 days. The sources are larger (kernel.csl plus two libraries), so the chapter must abridge heavily.

## Smaller edits (no new chapter)

- **Ch 9, library map:** add `kernels/fft` and `kernels/tally`, and add `benchmark-libs/` (allreduce, stencil_3d_7pts) as reusable user-level modules. Note that relative `@import_module` paths break when a benchmark is copied alone; this is the CG failure above. Fix with `--import-path` / `CSL_IMPORT_PATH`.
- **Ch 11, "The library version":** one paragraph on 2-D use (gemv-collectives_2d, and the gemm lab if it is added), plus `benchmark-libs/allreduce` as the row+column composition.
- **Ch 12, exercises/scaling:** point to CG as "what a stencil is for". If proposal 2 is rejected, use a short boxed section with the measured run above.
- **Ch 15, "A second workload":** replace the single GEMM sentence with measured numbers once proposal 1 exists.
- **Ch 6 or an appendix:** half a page on FFT as a transpose-dominated workload (fft-3d uses `kernels/fft` with reshape and transpose). It is the clearest SDK example of all-to-all traffic on a mesh. A section is enough; a chapter is not warranted.
- **Ch 4:** state that topic-14 (color swap), histogram-torus and spmv-hypersparse are WSE-2 only in 2.10.1 (they ship no `commands_wse3.sh`). The same is true of 25-pt-stencil and gemv-00. This is useful for a reader who tries them.
- **Appendix (optional):** a one-page "SDK example index" mapping all 56 examples to chapters, built from the table above.

## Rejected ideas

- **Debugging chapter.** Ch 9 already has an error decoder (measured), a four-step hang procedure, `<simprint>`, `<debug>` and the instruction trace, and Ch 10 uses the trace on SAXPY. The only gap is that csdb was verified at help-screen depth. Extend that in Ch 9 if it can be run; it is not a chapter.
- **Performance-tuning chapter.** Ch 6 (operand collisions, instruction cost), Ch 10 (f16 vs f32, WSE-2 vs WSE-3), Ch 11 (hop cost, back-pressure) and Ch 12 ("Where the 90 cycles go", overlap measured slower) already form a measured tuning thread. A separate chapter would re-run the same measurements. The GEMM lab adds the compute-bound side.
- **ML-workload chapter.** Ch 8 covers weight streaming, inference pipelines and KV-cache arithmetic. The SDK has no ML examples beyond GEMV/GEMM, so on the CSL side the GEMM lab is the ML kernel.
- **SdkLayout chapter.** Ch 9 has a measured section with a comparison table. Most SDK examples use layout.csl, and SdkLayout's single-PE-port limit makes it a niche path for now.
- **FFT, Cholesky, Mandelbrot, wide-multiplication, game-of-life chapters.** Each is a fine example, but none teaches a mechanism the course lacks beyond what the GEMM and CG labs would add. Mandelbrot (load imbalance) and wide-multiplication (multi-word integer carry chains) could be lab exercises.
- **Sparse/hypersparse chapter.** Ch 3 covers the concept. spmv-hypersparse has no WSE-3 script and needs preprocessing data.
