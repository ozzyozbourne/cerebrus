# ch12 · depth review

Summary: The lab's measured table and its "88 + 2.5·n" model are real and reproducible, but the chapter stops at the fit. It never opens up the fixed ~88 cycles. It does not test the overlap it recommends. It does not show how the SDK's 7-point and 25-point benchmarks actually build their stencils (the one-line claim that they "do both" 2-D/3-D and overlap is only half right). Its whole-wafer story is one sentence. I instrumented copies of program 04 with on-device `<time>` timestamps and ran ablations. The fixed part splits cleanly into about **4 × 14.6 cycles per async transfer (issue + completion task) + about 13 cycles of loop bookkeeping + about 19 cycles of DSD start-up (≈6 per vector instruction)**. Measured overlap makes things *slower*, not faster. Halo width costs about 1 cycle per extra word against about 15 per extra message. I also found that the chapter's measurement method (differencing `sim_stats.json` totals) is not robust under host load, and that per-step cost can jump by 30 % from an unrelated code change. The SDK benchmarks avoid both problems by timing with the TSC.

All new numbers below are WSE-3, P = 8, n = 16 unless stated. They come from copies in `/home/user/cerebras-sdk/tmp/rev-ch12-depth/` (variant sources and scripts are kept there; simulator outputs were deleted). The per-step figure is (TSC cycles at 100 steps − TSC cycles at 10 steps) / 90, read on interior PE 1. TSC values repeat to the cycle across reruns.

## Gaps and additions (prioritised)

### D1 [critical] The fixed ~88 cycles is never decomposed, though it can be, with real numbers
**What is missing.** The page asserts that the fixed part is "the halo exchange — four single-wavelet async transfers, their completion tasks, and task scheduling" and stops there. Nothing tells the learner how much is transfer and how much is CE overhead. Nothing says that part of the "fixed" 88 is really per-instruction compute start-up, or why P = 2 saves exactly what it saves.

**Why it matters.** This is the chapter's main "how it behaves inside" moment. The answer is surprising and teachable: almost none of the fixed cost is wire time. It is CE instruction overhead per message and per vector instruction. That lesson also explains why the overlap exercise fails (D2) and why the SDK sends a few large messages (D4).

**Measured evidence** (TSC-timed, cycles per step, WSE-3):

| Variant (source dir in scratch) | n | cycles/step |
|---|---|---|
| base (program 04 unchanged + TSC) | 4 | 100.2 |
| base | 16 | 130.2 |
| base | 64 | 250.2 |
| base, P = 16 | 16 | 130.2 (flat weak scaling confirmed) |
| base, P = 2 (2 ops/step instead of 4) | 16 | 101.0 |
| `nocomp`: exchange + tasks, the three DSD ops removed | 16 | 71.2 |
| `compute_only`: three DSD ops, no exchange, loop via one `@activate`d task | 16 | 73.0 |
| `taskloop`: neither exchange nor compute, one activate per step (simcycle differencing) | – | ≈12.5 |
| WSE-2 base / WSE-2 nocomp | 16 | 134.1 / 80.1 |

Derivation [derived]:
- Fit over n = 4/16/64: **90 + 2.5·n** (the chapter's 88 came from 0-step differencing; see D3).
- Exchange plus step loop = 71. Removing two of the four ops (P = 2) saves 29, so **≈14.6 cycles per async op**, covering issue, completion-task dispatch and `op_done()`. Then 4 × 14.6 = 58, and the remaining **≈13 is step bookkeeping/dispatch**, which matches `taskloop` (12.5) and `compute_only` − compute (73 − 60).
- Compute at n = 16 = 130.2 − 71.2 = 59 = 40 (2.5·16) + **19 ≈ 3 × 6.3 cycles start-up per DSD instruction**. So the true "intercept" is 71 + 19 = 90, and about a fifth of the "fixed communication" cost is really compute start-up.
- WSE-2 has a larger fixed part (80 vs 71) and slightly cheaper compute (54 vs 59). That is why the totals nearly cancel (134 vs 130). The current sentence "WSE-2 vs WSE-3 is a wash" hides this.

Timeline evidence: an intrusive per-event timestamp run (`ts2` approach: 8 `get_timestamp` calls per step, about 40 cycles each, so absolute values are inflated) shows the order of events on an interior PE. The four completion tasks run **strictly one after another**, never overlapping. `update()` starts only after the fourth. The order is the same every step (send_e → send_w → recv_w → recv_e).

Code-size evidence: every function is inlined into each completion task. In the ELF symbol table (`readelf -sW out/bin/out_3_0.elf`) `t_se`/`t_sw`/`t_rw`/`t_re` are 136 bytes each in the original and 84 bytes without the DSD ops. No separate `update`/`start_step` symbols exist.

**Proposed addition.** Add an `<h3>Where the 90 cycles go</h3>` after "What the numbers say", containing:
1. The ablation table above (a stacked-bar SVG is ideal: 4 × 14.6 "async op + completion task", 13 "step loop", 19 "DSD start-up (3 × ~6)", 2.5·n "streaming"). Tag the numbers `measured` and the split `derived`.
2. One paragraph: "Almost none of this is wire time. A single wavelet crosses one hop in a cycle or two. The cost is the CE running a task for each transfer that finishes, one at a time, plus a few cycles to start each vector instruction. Fewer, larger messages and fewer, longer instructions are the levers."
3. Update the model widget's labels: the dashed line becomes "messages + tasks ≈ 71", and a second band shows "DSD start-up ≈ 19".
4. Fix the WSE-2 bullet: "the fixed part is ~9 cycles larger on WSE-2 and the per-cell part slightly smaller, so totals land within 3 %."
5. Optional: a sentence noting that P = 2 → 101 agrees with this model to within one cycle, which shows how well the model predicts.

### D2 [critical] Overlap of communication and compute: the chapter recommends it, but measured, it makes this kernel slower
**What is missing.** "Use the model" says that on a real wafer you would "overlap the halo exchange with the interior update — the SDK's 7-point and 25-point stencil benchmarks do both". Exercise 1 asks whether "the fixed 88 shrinks". The page gives no expected answer and no explanation of what overlap can and cannot hide on a WSE PE.

**Why it matters.** Learners coming from GPUs/MPI will assume overlap always helps. On a PE, tasks do not pre-empt each other. A completion task cannot run while the interior compute runs, and the latency to hide here is a few cycles. The measured result teaches the CE execution model better than any prose.

**Measured evidence** (WSE-3, n = 16, TSC):
- `overlap` (interior `u[2..n-1]` with three DSD ops issued right after the four async transfers, then the two edge cells as scalar f32 code in `update()`): **≈273 cycles/step** by simcycle differencing, more than double. Scalar f32 arithmetic on the CE is slow.
- `overlap2` (interior Laplacian `@fadds`/`@fmacs` on n−2 cells during the transfers, the two edge Laplacians with 2-element strided DSDs after arrival, then one final `@fmacs` over n): **178 cycles/step vs 130** for the original, and still bit-correct (`MATCH`).
- Reason [derived from D1]: it adds two more vector instructions (≈6 cycles start-up each) and grows every inlined completion task. Meanwhile there is almost no transfer latency to hide, because the four completions already run back-to-back.

**Source evidence for how the SDK really overlaps.** The 25-pt benchmark does not "compute while waiting" in the sense the exercise means. It **fuses the receive with the arithmetic**: `oned_exch.csl` `recvMode()` issues `@fmuls(buffDsd, fabInDsd, constDsd, .{ .async = true, .activate = callback })`. Incoming wavelets are multiplied by the stencil coefficients on a microthread as they arrive, so no separate receive-then-compute pass exists. The 7-pt library (`benchmark-libs/stencil_3d_7pts/wse3/pe.csl`) does *not* overlap at all. It does all sends and receives for a block, then `laplacian_xy()`, and its own comment says "TODO: to reduce latency, combine laplacian_xy into RECV".

**Proposed addition.**
- Rewrite the "On a real wafer…" sentence: "The SDK's 25-point benchmark hides communication by fusing it with arithmetic. Its receive is an asynchronous `@fmuls` from the fabric, so data is scaled by stencil coefficients as it lands. The 7-point library does not overlap at all yet (its source carries a TODO saying so)."
- Give Exercise 1 an expected outcome in a `<details>` box: "We measured 178 cycles/step (vs 130) for a correct overlapped version. Interior compute cannot hide what is not latency: completion tasks cannot run until the interior instructions finish, and you added two instructions. Overlap pays off only when transfers are long (many wavelets per message, D4) or when the receive itself does the arithmetic (`@fmacs`/`@fmuls` with a `fabin_dsd` source, `.async = true`)."
- Optional stretch exercise: replace the receive `@fmovs(ghost_w, from_w, …)` with a fused async op, and compare.

### D3 [major] The measurement method is fragile; the SDK benchmarks time with the TSC, and the lab should too
**What is missing.** The lab differences the total `cycle_count` from `sim_stats.json` (0 vs 100 steps). It does not mention the `<time>` module or the tic/toc pattern that both SDK stencil benchmarks use, and it never warns about what pollutes the total.

**Why it matters.** (1) The total includes cycles where the fabric sits idle waiting on the host process. It moves by hundreds to thousands of cycles when the host is loaded. (2) The 0-step baseline takes a different code path (the pedagogy review P3 also notes this). (3) The SDK's own method is the "how it is done for real" lesson.

**Measured evidence.**
- Unmodified program 04, P = 8, n = 16, 10 steps, run twice under load: `cycle_count` **5,392** and then **6,559**. The second run had `idle_ce_cycles` 1,538 against the usual 50. Elsewhere, the 100-step totals of identical kernels varied between 21,612 and 23,424 (`idle_ce_cycles` = 50 in both). The chapter's 10-step value is 5,071. So the "within 2 cycles" claim (ch09/ch15) holds only on a quiet machine.
- TSC-timed kernel cycles (start at `run()`, end just before the final `unblock_cmd_stream()`) were **identical to the cycle** across 8 reruns and machine loads: interior PE 13,049 at 100 steps and 1,329 at 10.
- Source: `7pt-stencil-spmv/src/kernel.csl` (`f_tic`/`f_toc` → `timestamp.get_timestamp`, packed by a separate RPC `f_memcpy_timestamps`; README: "`cycles_send = max(time_end) - min(time_start)`", with an allreduce-based `f_sync` to align PE clocks). `25-pt-stencil/task.csl` records `tscStartBuffer` in `f_comp` and `tscEndBuffer` in `f_checkpoint()`, and run.py reports "cycles per element".

**Trap found while instrumenting (worth a callout).** Copying the six timestamp words into the export buffer *inside* the final-step branch, code that runs once, raised the per-step cost from 130 to **167 cycles**. That branch is inlined into every completion task (task size 136 → 200 bytes in the ELF). Moving the copy to a separate RPC (`pack()`, exactly the SDK's `f_memcpy_timestamps` pattern) restored 130. Adding only `import <time>` + `enable_tsc` changed nothing (130.7).

**Proposed addition.**
- Add a short "Measure it like the SDK does" subsection with about 15 lines of CSL: `const timestamp = @import_module("<time>");` `enable_tsc()` + `get_timestamp(&t0)` in `run()`, `get_timestamp(&t1)` before the last `unblock_cmd_stream()`, a separate exported `pack()` RPC that copies `t0`/`t1` into a `[6]u16` export, and on the host `launch('pack')`, then `memcpy_d2h` with `MEMCPY_16BIT`, then `t = w0 | w1<<16 | w2<<32`.
- Re-base the table and model on TSC numbers: 100.2 / 130.2 / 250.2 → **90 + 2.5·n**; P = 2 → 101.0; P = 16 → 130.2; WSE-2 → 134.1.
- Add a callout: "Code you run once can still slow every step. CSL inlines your helper functions into each task, so a bigger task costs more to enter. Keep instrumentation and epilogue code in its own RPC."
- Mention the start-up skew visible in the TSC data: PE 0 starts first and PE 7 last, because the `run` RPC reaches PEs at different times. The SDK's 7-pt `f_sync` exists to remove exactly this.

### D4 [major] How the SDK benchmarks structure their stencils differently is never shown
**What is missing.** The two benchmarks are mentioned only as "do both". A learner finishing the capstone should see what the production-grade versions do differently and why.

**Source evidence and measured numbers.**

| | Lab 3 (program 04) | 7pt-stencil-spmv (`benchmark-libs/stencil_3d_7pts`) | 25-pt-stencil |
|---|---|---|---|
| Decomposition | 1-D rod, n cells/PE | 3-D: x, y over a 2-D PE grid, the **whole z-column in each PE's memory** ("pencil") | same pencil layout; `zDim` per PE, chunked if > 400 (`util.computeChunks`) |
| Neighbours on fabric | 2 (E, W) | 4 (E, W, N, S), one hop | 4 directions × 4 hops (pattern = 5) via **router switches advanced by control wavelets** (`switches.csl`, `routes.csl`): one send reaches 4 downstream PEs |
| Colors | 4 | 8 (4 directions × 2 parities) + 1 for allreduce | 21 colors/task IDs; README: "only 4 colors are left" |
| Concurrency | 4 concurrent async ops, one per queue/microthread | **sequential state machine**: `f_send` sends E, W, N, S one after another on one fixed microthread (`.ut_id = out_ut`, `output_ut_id = 3`); `f_recv` does the same; `count_send_recv` joins them | 4 directions concurrent (queues 0–3 out, 4–7 in), each receive an async `@fmuls` fused with the coefficients |
| Message size | 1 wavelet | `BLOCK_SIZE` wavelets (whole z-column chunks) | `chunkSize` wavelets |
| z-direction | – | in memory: 3 `@fmacs` with shifted DSDs | in memory: 8 `@fmacs` with `@increment_dsd_offset` (manually unrolled) |
| Time stepping | `update()` → `start_step()` call chain | single SpMV per RPC (used inside CG/BiCGSTAB) | leapfrog over `zValues[2, …]`, `epilog()` → `@activate(send)` |
| Timing | sim total cycles | TSC tic/toc + allreduce sync | TSC in kernel |
| Arch | WSE-2 + WSE-3 | both (separate `wse2/` and `wse3/` pe.csl) | **WSE-2 only** (only `commands_wse2.sh`) |

Measured runs of the unmodified SDK benchmarks (copies, simulator):
- 7-pt SpMV, WSE-3, 5×5 PEs, `BLOCK_SIZE` = zDim: zDim 5 → 1,050 cycles; 50 → 1,650; 200 → **4,206** (`cycles_send`, which includes tic/toc RPC overhead). Marginal cost is **≈13–17 cycles per z-cell** per SpMV: 4 sends + 4 receives + 7 FMACs per cell.
- 7-pt, zDim = 200 with `BLOCK_SIZE` 20 instead of 200: **8,078 vs 4,206** cycles. Ten blocks instead of one cost about 430 cycles per extra block, the same "per-message overhead dominates" law as D1.
- 25-pt, WSE-2, 10×10×10, run.py's own TSC: 2,501 cycles for 2 iterations and 12,360 for 10, so **≈1,232 cycles per iteration ≈ 123 cycles per z-cell** ("cycles per element = 123.6"), `SUCCESS`.
- Lab 3 halo-width test (`halo4`/`halo16`: send k wavelets per direction instead of 1): 136.9 and 151.9 cycles/step vs 130.2, so **≈1 cycle per extra word against ≈14.6 per extra message**.

**Why it matters.** It answers "what would I change to scale this up". Use 2-D/3-D pencils, send whole columns, cut the number of messages, and fuse receive with compute. It also shows a second fix for the chapter's own hang: the WSE-3 7-pt library pins sends to an explicit microthread with `.ut_id` and allocates DSRs explicitly (`@get_dsr`, `@load_to_dsr`), instead of relying on queue-ID = microthread-ID.

**Proposed addition.** Add a section `<h2>How the SDK's stencils differ</h2>` with the comparison table (shortened), the three measured SDK numbers tagged `measured`, and a small SVG of the "pencil" decomposition (PE grid in x-y, z-column in SRAM, four arrows). Add one sentence linking to the hang story: "The 7-pt library avoids the microthread clash by putting every send on one microthread chosen explicitly (`.ut_id`) and serialising them in a state machine. That trades concurrency for safety."

### D5 [major] 2-D/3-D extension is a single clause; give the learner the cost model and one concrete step
**What is missing.** The page says "you would also go to 2-D domains" with no model of what changes.

**Why it matters.** Real stencils on the WSE are 3-D pencils (D4). The surface-to-volume lesson changes shape: with a pencil, the "surface" sent per step is the *whole* column in each of 4 directions. Communication then grows with zDim instead of staying fixed. That is a qualitatively different regime from the 1-D lab, and the 7-pt numbers show it.

**Evidence [derived from D1 + D4 measurements].**
- 1-D lab: per step ≈ 90 + 2.5·n. Communication is constant (2 words/PE/step) and compute grows with n.
- 2-D tile (n×m cells per PE, 5-point): 4 messages; the E/W edges are strided columns (extent m, stride n, which a `mem1d_dsd` can express) and N/S are contiguous rows. The D1 constants predict ≈ 4·14.6 + 13 + (4 directions × ~1 cycle/word × edge length) + 4–5 DSD ops × (6 + ~0.8·n·m). 8 colors (4 directions × 2 parities, as in game-of-life; ch04 already says this). On WSE-3, 8 concurrent async ops need 8 distinct microthreads beyond memcpy's, which is why the 7-pt library serialises (D4).
- 3-D pencil: the 7-pt measurement gives ≈15 cycles per z-cell per apply. Memory caps zDim (25-pt: about 400 per chunk; 7-pt keeps x, y plus 4 neighbour buffers).

**Proposed addition.** A short subsection "Going to 2-D and 3-D" containing:
- a 3-panel figure (rod → tile → pencil) with per-step message count and words per message;
- a revised model formula with the D1 constants;
- a new exercise: "Extend program 04 to a P×Q PE grid with one cell per PE in x-y and an n-cell column in z (a 7-point stencil). Predict cycles/step from the constants above, then measure with the TSC method." A hint should point at `benchmark-libs/stencil_3d_7pts/layout.csl` for the 8-color parity scheme.

### D6 [major] Whole-wafer extrapolation is one sentence ("lets a stencil use all ~900k PEs") with no numbers or caveats
**What is missing.** The page gives no cell counts, step rates or FLOP rates. It does not compare with published wafer-scale stencil results, and it does not mention that a 1-D rod cannot lie in a straight line across a 2-D wafer.

**Evidence [derived, flagged as such].**
- SDK-visible CS-2 fabric is 750×994; the user rectangle is ≤ width − 7 and ≤ height − 2 (`single-tile-matvec/README.rst`, research notes), so ≈743×992 ≈ 737k PEs. WSE-3's user-visible dims are not published locally (research notes say so).
- With 90 + 2.5·n at 850 MHz (SDK benchmark assumption, `bandwidth-test/README.rst`) and 5 flops per cell (fadd + 2 FMAs):
  - n = 16: 130 cycles = 0.153 µs/step → 6.5 M steps/s; 11.8 M cells; ≈ 0.39 PFLOP/s f32.
  - n = 5,000 (memory limit claimed on the page): 12,590 cycles = 14.8 µs/step; 3.7 G cells; ≈ 1.25 PFLOP/s. That is the per-PE ceiling of 2 flops/cycle × 737k × 0.85 GHz, so the asymptote is pure DSD throughput.
- A 1-D chain over 737k PEs must snake (boustrophedon). The turn PEs need N/S routes, so neighbours remain one hop apart and the model still holds, but the layout code changes.
- Published reference points (already in the research notes, with tags): CS-1 BiCGSTAB on a 7-point stencil ≈ 0.86 PFLOPS, about 1/3 of peak (Rocki et al., arXiv:2010.03660); WSE-2 EAM MD 270,097 timesteps/s vs 1,530 on Frontier (arXiv:2405.07898). Both are strong-scaling, step-rate stories, which the 0.15 µs/step figure illustrates.

**Proposed addition.** Extend the model widget with a "whole wafer" readout (PEs = 737k, a CS-2 SDK rectangle `derived`): total cells, steps/s and PFLOP/s for the chosen n. Add a paragraph of caveats: simulator cycles, assumed clock, snake layout, host I/O excluded, and a 1-D problem being a toy (real codes are 3-D pencils, D5). Add a sentence placing the Rocki et al. 0.86 PF result beside it, with its tag.

### D7 [minor] Strong scaling is missing; only weak scaling is shown
**What is missing.** "Weak scaling is flat" is shown. The more relevant WSE story (fixed problem, more PEs → shorter steps until the fixed part dominates) is not.

**Evidence [derived from the measured model].** A rod of L = 4,096 cells: P = 64 → n = 64 → 250 cycles; P = 256 → n = 16 → 130; P = 1,024 → n = 4 → 100. Moving from 64 to 1,024 PEs (16×) gives only 2.5× speed-up, and the limit is the 90-cycle floor. This is also the place to say that the floor (messages and tasks), not bandwidth, sets the strong-scaling limit.

**Proposed addition.** Add a second mode or slider ("total cells L") to the model widget that plots step time against P. Add one bullet under "What the numbers say".

### D8 [minor] Exercise 3 (f16) and the WSE-2/WSE-3 claim lack the needed facts
**What is missing.** "f32 work does not benefit from WSE-3's wider FP16 SIMD" is stated without the per-instruction evidence. Exercise 3 gives no hint about what to expect.

**Evidence.** The D1 split shows that the WSE-2/WSE-3 difference is in the fixed part (80 vs 71) and in compute (54 vs 59 at n = 16), not a wash in each component. I did not measure f16.

**Proposed addition.** Reword the bullet as in D1 item 4. In Exercise 3, tell learners to compare the *slope* (cycles per cell from n = 16 vs 64) rather than total per-step cost, because the fixed part will hide any SIMD gain at small n.

## Out of scope for this chapter (new-chapter or cross-chapter ideas)
- **ch09 / ch15 (cross-chapter):** "Totals repeat to within 2 cycles" holds only on an unloaded host. Under load, `cycle_count` varied by 1,000+ cycles and `idle_ce_cycles` rose from 50 to 1,538–6,317. Recommend that ch09 teach `<time>` TSC tic/toc (the SDK benchmark pattern) as the primary kernel timer and treat `sim_stats.json` as whole-run only. ch15's "pin per-step cost to within a cycle" should credit the TSC method.
- **ch05 (tasks) cross-link:** the measured ≈14.6 cycles per async-op completion and ≈13 per task-loop iteration are the first hard numbers for "what a task costs". Add them to ch05's task-model section. The "inlined helpers make every task heavier" effect (130 → 167 cycles) belongs there too.
- **ch06 (DSDs) cross-link:** ≈6 cycles start-up per vector DSD instruction plus about 0.8 cycles/element for f32 `@fadds`/`@fmacs` (measured indirectly here). ch06 could teach "fewer, longer DSD ops" with this number.
- **ch04 / ch11 cross-link:** the 25-pt benchmark's switch-based multicast (control wavelets advancing router switch positions, `switches.csl`) is the most advanced routing technique in the SDK and is not covered anywhere. It deserves a figure in ch04 or a box in ch11.
- **ch08 / ch13 cross-link (microthreads):** the WSE-3 7-pt library's explicit `.ut_id` / `@get_dsr` allocation is the "real" fix behind Lab 3's hang rule and should be referenced from wherever microthreads are explained.
- **New chapter or appendix: "Lab 4: a 3-D 7-point stencil".** Build on `benchmark-libs/stencil_3d_7pts`: a pencil decomposition, 8 parity colors, allreduce-based sync, TSC timing, then a CG solve (the SDK has `conjugate-gradient` and `bicgstab` on top of it). That is the natural capstone after Lab 3 and the bridge to the Rocki et al. result.
- **Communication-avoiding / temporal blocking:** since a message costs about 15× a word, a wider halo exchanged every k steps (k ghost cells, k sub-steps locally) should cut the fixed part by roughly k. This is a good advanced exercise or appendix. Not measured here beyond the halo-width cost (≈1 cycle/word).
