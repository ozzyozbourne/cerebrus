# Phase 3 review: the learner's path

Reviewer angle: a motivated engineer who knows GPUs and CUDA, reading Ch1 to Ch15 in order and running the programs.

## Verdict

**Yes: add one new chapter.** It should be a fourth lab that builds a 2-D distributed GEMV (with a small GEMM as the stretch goal). Close everything else with edits and one reference appendix. The architecture path (Ch3 to Ch7) and the toolchain-to-lab handoff (Ch9 to Ch10) are strong. Ch9 already tours SAXPY line by line, and it has the three-file "contract", an error decoder, a hang procedure and "Break it on purpose", so Lab 1 is not a cliff. The real cliff is after Lab 3.

## Where the learner gets stuck

1. **The course never practises matrix multiply on Cerebras, though it is the central ML kernel.** Ch13 has "Anatomy of a matmul" (Tenstorrent) and Ch14 has "Tiling a matmul" (GPU). For Cerebras there is only Ch6's single-PE gemv-02 column sweep, Ch8's single-tile-matvec bandwidth box and Ch11's "Composing the two: a distributed GEMV". That last one is a diagram plus "Try it: open gemv-08", with no program, no run and no measurement. So the comparison in Part IV is lopsided: two machines get a matmul mapping and the wafer gets a stencil. Ch14 even says that A and B tiles are "moved neighbour to neighbour by wavelets (Chapter 12)", but Ch12 is the heat rod.
2. **No program is truly 2-D.** Programs 01 to 04 are one PE or one row. Program 05 is one column, and its C × R extension is an exercise (Ch11, "Going 2-D"). Several 2-D skills are only described: memcpy with h > 1 (the Ch7 widget is tagged Derived), routes in both axes on one PE, more than four PE-program groups, `<layout>` coordinates, and 2-D colour budgeting (the Ch4 planner). Lab 3's 2-D and 3-D paragraph is Derived only.
3. **"Write my own real kernel" has no design method.** Each lab hands over a finished program. Nothing walks from a maths problem to a placement, then a colour and queue/microthread budget, then a cost model, then the code, then validation, then the measurement. The pieces exist across Ch4 (colour planner), Ch5 (task-ID budget), Ch9 (memory budget) and Ch12 (90 + 2.5·n model). They are never put together into one procedure.
4. **CUDA intuition goes unused for 13 chapters.** "CUDA" appears zero times in Ch1 to Ch12. The first mapping is Ch14 "SAXPY, twice" and the Ch15 programming-model table. A GPU engineer has to build their own Rosetta stone, for example kernel launch vs RPC, `__syncthreads` vs task activation, shared memory vs 48 KB SRAM, and cudaMemcpy vs memcpy.
5. **The course has no glossary or reference page.** Wavelet, color, ramp, CE, microthread, input queue, DSD, memcpy frame and halo are each defined once, in their own chapter. Ch13 has its own glossary for Tenstorrent, but the Cerebras side has none.

## Proposed new chapters (ranked)

### 1. Lab 4: matrix-vector on a 2-D grid (and a first GEMM)

- **Why it is needed.** It closes gaps 1 to 3 at once. It is the workload that Ch8 (pinned-weight decode is a GEMV per layer) and Ch15 ("One workload: Llama-70B decode") argue about. It turns Ch11's diagram into a validated program, and it gives Part IV a like-for-like kernel next to Ch13's TT matmul and Ch14's tiled GEMM. It is too large to be a section of Lab 2. It needs a new program, 2-D host I/O, three to five colours and its own performance model.
- **Where it goes.** After Lab 3, as the new Ch13. Tenstorrent, GPU and Comparison become Ch14 to Ch16. Lab chapters are generated from `course/src/` by `tools/build.py`, so add `src/13-lab-gemv.html` and update the cross-references that say "Ch13/14/15".
- **Estimated effort.** About 1.5 to 2 days of work, equivalent to Lab 2: one new program, one stretch program, two widgets, and review on both chips.
- **Outline:**
  1. *Design before code.* Turn y = A·x + b into a placement. Each PE holds a block of A (Kb × Nb), and x is broadcast down the columns while partial y values are reduced along the rows. Then write budget sheets for memory (≤ 44 KB, Ch9), colours (Ch4 planner), queues and microthreads (Ch5) and task IDs 8 to 20. Close the section with a reusable checklist for designing a kernel.
  2. *2-D host I/O.* Scatter A in ROW_MAJOR over a W × H block with one memcpy_h2d, load x into the top row and b into the left column, and read y back from the rightmost column. This is the first real use of the Ch7 h > 1 wire order, which is so far Derived.
  3. *Routes in both axes.* One PE carries a SOUTH multicast (from program 05) and an EAST checkerboard (from program 03) at once. Show the PE-program groups, `--out-routes` and `<layout>` coordinates.
  4. *Compute.* A column sweep with `@fmacs` and a moving DSD (Ch6), plus the bank-clash padding rule (Ch6, note 22).
  5. *Streaming vs store-and-forward reduce.* This section compares the course's streaming reduce with gemv-08's store-into-memory step, measured on the TSC.
  6. *Measure and model.* Time compute and reduce separately (in the form a·Kb·Nb + c·W + d) on both chips, from 2 × 2 to 8 × 8. Compare the useful bytes per cycle per PE with the single-tile-matvec figure in Ch8 (≈4.0 B/cycle).
  7. *From GEMV to GEMM (stretch).* Batch several x vectors at once (GEMV with B > 1, which is decode with batching). Optionally add a SUMMA-style loop in which A blocks multicast along rows and B blocks multicast down columns. Show that this is the same dataflow as Ch13's TT matmul, with wavelets in place of 32 × 32 tiles.
  8. *Scale to the wafer and compare.* Extrapolate to one Llama-70B layer region (Ch8). Then compare with the H100 roofline (Ch1/Ch14) and the TT grid matmul (Ch13). Add exercises with expected answers and a Check-yourself section.
- **Programs.** Add `programs/06-gemv-2d` (required, validated on WSE-2 and WSE-3, with knobs W, H, Kb, Nb). Optionally add `programs/07-gemm-summa`, or ship batched GEMV as an exercise variant if time is short. Add both to `run_all.sh` and the README table.
- **Widgets.** A 2-D dataflow stepper (broadcast, then FMACs, then the reduce wave, cycle by cycle from measured TSC). A block-size and grid planner that checks memory, colours and microthreads and predicts cycles from the fitted model.

### 2. No second new chapter

The other gaps fit as edits or an appendix (see below).

## Smaller edits

- **New appendix A: reference card and glossary (`16-reference.html` or `appendix.html`, linked from the index).** It needs four parts:
  - a glossary of about 40 Cerebras terms, each linking to the chapter that defines it;
  - a CUDA to CSL Rosetta table (thread/block/grid → PE/rectangle, kernel launch → RPC, `__syncthreads` → task activation and barrier RPC, shared memory → PE SRAM, cudaMemcpy → memcpy, warp occupancy → microthreads and async ops);
  - a one-page resource budget (48 KB / ~44 KB usable, 24 colours with 20–23 reserved, task IDs 8–20, queues, the 8 microthreads and their WSE-2/WSE-3 rules, and fabric dims of width + 7 by height + 2);
  - the measured cost constants from CROSS_CHAPTER_NOTES 14, 16, 20, 22–24 (hop costs, DSD op rates, startup ≈ 15–17 cycles, per-message ≈ 14.6).
  
  Effort is about half a day.
- **"If you know CUDA" callouts** of two or three lines each:
  - Ch3: PE vs SM and thread; no caches vs L1/L2.
  - Ch5: task vs thread and kernel; run-to-completion vs warp scheduling.
  - Ch6: DSD vs a vectorised loop.
  - Ch7: memcpy and RPC vs cudaMemcpy and `<<<>>>`, and why "launch returned" means nothing.
  - Ch9: three files vs `.cu` + host.
- **Ch14 "Tiling a matmul":** fix the "(Chapter 12)" reference. Point to the new Lab 4, or to Ch11 "Composing the two" if Lab 4 is not written.
- **Ch11 "Composing the two":** if Lab 4 is not built, at minimum make gemv-08 a run exercise with commands, expected output and a TSC measurement. Then point forward to Lab 4.
- **Ch12 exercises:** "Fewer messages" (the k-wide halo) and "Half precision" have hints but no measured expected result. Every other lab exercise has one, so add the numbers. Also add a 2-D stencil tile exercise (8 colours) with a measured answer, or mark it explicitly as unmeasured, as Ch10's stretch does.
- **Ch12 end, or Lab 4 §1:** add a short "From here to your own kernel" checklist that links the Ch4/5/9 budget widgets in order.
- **Ch15 "Where to go next":** turn the tutorial list into a ladder that maps each SDK tutorial or benchmark to the chapter that prepares for it (gemv-00…09 → Ch9–11, topic-11 → Ch11, 7pt-stencil-spmv/25-pt → Ch12, gemm-collectives_2d → Lab 4).
- **Ch8 line "Weight streaming … not by programs you write with the SDK":** promote it to a visible callout early in Part III (the Ch9 intro), so that learners know CSL is the custom-kernel path and not how PyTorch users program the machine.

## Considered and rejected

- **A chapter on the Cerebras PyTorch/ML stack.** It is closed, and it cannot be run or validated here. Ch8 ("Weight streaming", the ML-stack paragraph) and the Ch15 software-stack table cover what is knowable.
- **A Tenstorrent or CUDA coding lab.** There is no hardware for it, and it would dilute the Cerebras goal. Ch14 "SAXPY, twice", Ch13 "Programming: reader, compute, writer" and the Ch15 programming-model table cover the comparison well enough.
- **A separate debugging chapter.** Ch9 already has the error decoder, the four-step hang procedure, the instruction trace and `<debug>`/`<simprint>`, and each lab has an "If it fails" or "When it goes wrong" section.
- **A sparsity chapter.** Ch3 "Sparsity: skipping zeros with dataflow" and Ch6's dataflow-sparsity note are enough for the stated goal.
- **An SdkLayout chapter.** Ch9 "The other way to lay out" covers when to use it. The labs deliberately use layout.csl + memcpy, as most SDK examples do.
- **Splitting Ch9 because it is long.** It is long (about 5,100 words), but well sequenced, and Lab 1 picks up exactly where it stops. Splitting it would add page-turning without filling a gap.
- **An attention or softmax kernel lab.** It is attractive, but it needs `<math>` exp and an allreduce on top of the GEMV skills. Better to offer it as a Lab 4 stretch exercise once the GEMV exists.
- **A "real hardware" chapter.** Nothing in the course can run on a CS system. Ch9 already says what changes (`--cmaddr`, fabric 750 × 994).
