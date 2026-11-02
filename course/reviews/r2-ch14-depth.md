# Review round 2: Ch14 (14-lab-gemm, src/14-lab-gemm.html, programs/06-summa), depth angle

I read the page source, the program, build-ch14.md, CROSS_CHAPTER_NOTES 1–25 and the SDK README. I ran three new
measurements on a scratch copy (`/home/user/cerebras-sdk/tmp/r2-ch14-depth/`, now deleted) with traces suppressed and
scratch under 1 MB. All are SDK 2.10.1 simulator runs, TSC on the far-corner PE, P = 2:

| chip | kernel | T | compute/step | broadcast/step | page's fit predicts |
|---|---|---|---|---|---|
| WSE-3 | 0 | 45 | **189,224** (93.4 cyc/@fmacs) | 4,545 | 271,350 |
| WSE-2 | 0 | 45 | **276,575** (136.6 cyc/@fmacs) | 4,485 | 248,265 (page text: ≈ 248,000) |
| WSE-2 | 1 | 39 | **97,004** | 3,476 | 123,006 (page text: ≈ 123,000) |

The broadcast fit holds well. The compute fits do not hold at odd T.

## Findings

**D1 (high). The compute fits come only from tiles that are multiples of 4, but the "Scaling up" section, the calculator and the chart apply them to odd tiles.**
- Location: "Scaling up" (kernel 0 at T = 45, kernel 1 at T = 39), the budget calculator, the chart's T slider (up to 45), and `FIT` in the script.
- What is wrong: every measured square tile (4, 8, 16, 24, 32) is a multiple of 4, so the fits describe the "all instructions clash" case only. The page's own Mt sweep says odd Mt clashes on only about a quarter of instructions, yet the extrapolation uses the clash fit at T = 45 and 39. The table above shows the error goes in different directions on different chips:
  - WSE-3: T = 45 is 30% faster than the fit (93.4 ≈ 1.25·45 + 37 per instruction, matching the odd-Mt sweep).
  - WSE-2: T = 45 is 11% slower than the fit (≈ 2.2·45 + 37, so it clashes anyway). This agrees with note 22: the clash rule differs by chip.
  - WSE-2 kernel 1 at T = 39 is 21% faster than its fit.
- Corrected wafer extrapolation (P = 743, 1.1 GHz, measured per-step costs):
  - Kernel 0: 743 × (4,485 + 276,575) ≈ 2.09 × 10⁸ cycles ≈ 0.19 s, 0.39 PFLOP/s, 32% of peak (page says 0.17 s, 0.44 PFLOP/s, 36%).
  - Kernel 1: 743 × (3,476 + 97,004) ≈ 7.5 × 10⁷ cycles ≈ 68 ms, 0.72 PFLOP/s, 59% of peak (page says 85 ms, 0.57 PFLOP/s, 47%).
- Fix:
  - Use these measured per-step values in "Scaling up" (tag Measured, P = 2) and state that the fits hold only for T ≡ 0 mod 4.
  - In the calculator and chart, add a warning whenever Mt % 4 ≠ 0 ("alignment-dependent and chip-dependent; measured T = 45: WSE-3 189k, WSE-2 277k").
  - Better still, add the T = 45 and 39 points to `RUNS`.

**D2 (high). The lab never discusses overlapping communication with compute. This is the main design lever for SUMMA and the obvious next step on a wafer.**
- Location: "What the numbers say", "A design method", exercises.
- What is wrong: `start_step()` is called only after `compute` finishes, so broadcast and compute run strictly one after the other. At the default T = 8, broadcast is 18% of the kernel (2,601 of 14,422 cycles), and the page treats that share as fixed. Pipelined / double-buffered SUMMA issues the step s+1 broadcasts into a second buffer pair while step s computes, which hides the broadcast almost entirely once compute is longer than it (true from T ≈ 9).
- The costs are concrete and teachable:
  - two more tiles, so 7·4·T² bytes and a maximum tile of about T ≈ 39 instead of 45;
  - a third join bit, because the buffers must be free before they are overwritten;
  - the lockstep and back-pressure behaviour the page already describes.
- Two other designs an expert would expect to see named:
  - Cannon's algorithm: nearest-neighbour shifts, static routes and no run-time route rewriting. It is a natural fit for a 2-D mesh with cheap hops, which makes it worth saying why the SDK chose SUMMA.
  - Computing straight from a `fabin_dsd` as wavelets arrive. This is the Cerebras idiom, covered in Ch5/6/11. It would remove A_buf, but `<collectives_2d>` always lands data in memory.
- Fix: add a short "What this program leaves on the table" subsection with a derived estimate (kernel ≈ P·max(bcast, compute) + one bcast, about 11,800 vs 14,422 cycles at T = 8), plus an exercise to implement double buffering.

**D3 (med). Host I/O and problem size are understated in "Scaling up". This is also not how Cerebras runs large GEMMs.**
- What is wrong: the caveat "loading ≈ 13 GB … is left out" hides a cost of the same order as the kernel.
  - At the 1.2 Tb/s system I/O (150 GB/s, Ch 8, Vendor), 13.4 GB in plus 4.5 GB of C out takes ≥ 0.12 s.
  - Compute is 0.07–0.19 s.
  - So end-to-end throughput is at most about half the quoted PFLOP/s, before any memcpy-frame overhead.
- Also, a 33k² f32 GEMM is the largest that fits resident in SRAM. Production training uses weight streaming (Ch 8/9: weights from MemoryX, one layer at a time), not resident SUMMA.
- Fix: put the I/O time next to the compute time (tag Derived), and add one sentence with links to 08-systems.html and 09-model-to-tokens.html explaining that resident SUMMA is a teaching kernel and that the production matmul path streams one operand.

**D4 (med). Kernel 0's per-instruction overhead is diagnosed but no fix is tried, although it is the larger cost at small tiles.**
- Location: the "Where the other two-thirds go" callout.
- What is wrong: at Mt = 8 the ≈ 30-cycle fixed part is about 80% of each instruction. The page's only answer is to change the algorithm (kernel 1). Cheaper levers exist:
  - hoist `j*Kt + k` (swap loops so the B column is contiguous and use a pointer increment);
  - unroll the j loop at comptime;
  - issue the @fmacs as `.async` on alternating microthreads so start-up overlaps execution (Ch 6 covers async ops). Its gain is unmeasured.
- Kernel 1's @fmuls rate of 1.6/elem is "not isolated", and my T = 39 run (1.6 cycles per element for the whole pair on WSE-2, against 2.0 at even T) suggests it is alignment-sensitive too.
- Fix: list these levers explicitly as unmeasured, and turn one of them into an exercise. Note that kernel 1's per-element cost also depends on alignment.

**D5 (med). Strong scaling is missing.**
- Location: "The step time does not depend on P".
- What is wrong: the page covers only weak scaling (fixed T). A user with a fixed matrix shrinks T as P grows, and then the fixed costs (520-cycle broadcast, ~30 cycles per instruction) take over.
- Derived from the page's own table, for N = 256:
  - P = 8, T = 32: 8 × (2,569 + 103,724) ≈ 850k cycles;
  - P = 32, T = 8: 32 × (650 + 2,903) ≈ 114k cycles;
  - that is 7.5× faster on 16× the PEs, about 47% efficiency.
- Fix: add this as a bullet or a quiz item. Point to the calculator.

**D6 (low). The "roofline" lesson uses an f32 ceiling and does not say how far that is from the wafer's peak.**
- What is wrong: the 51% (kernel 1) is measured against 1 f32 MAC per cycle. The 16-bit path is 3.2–4 MACs per cycle on WSE-3 (notes 14/22), so this kernel reaches roughly 13–16% of the wafer's 16-bit peak. The scaling caveat mentions f16, but the measurement section's "compute-bound" framing does not.
- Fix: one sentence in "The lesson for the roofline", tagged Derived.

**D7 (low). The cause of the broadcast "sum of words" is left open with no hypothesis.**
- Location: "A broadcast step costs …".
- What is wrong: the two fabric→memory moves run at an aggregate of about 1 word/cycle, which suggests the per-PE receive path (ramp or memory-write port) is shared. That would be a per-PE communication ceiling of about 1 word/cycle, the input to a real per-PE roofline: T/2 MACs per word.
- Fix: state it as a hypothesis (Unverified) and add the experiment that would test it: one broadcast alone against both, at equal word count.

**D8 (low). Measurement caveats are scattered.**
- What is wrong: the measurements section never says that all cycles are simulator cycles, that the operand-collision rule is an empirical simulator behaviour (hardware unverified), or that the table mixes runs with traces on and off (build-ch14.md).
- Fix: add one caveat line under the table.
