# R4 audit: Appendix B (CUDA to CSL, budgets and constants), page-id appB

**Verdict: Mostly correct. Explanation quality: good.**
Everything the round-2 fixlog lists as fixed (A1–A16, C1–C2, P1–P9) is still in place. I re-checked the page against Ch 3–7, 10–15, CROSS 1–29, the SDK (`target/wse3.csl`, `memcpy/wse3/memcpy.csl`, `collectives_2d/pe.csl`, `malloc.csl`) and programs 01–05. I ran one compile-only experiment, SAXPY at N = 5,610 / 5,612 / 5,615 / 5,616 with cslc 2.10.1 on WSE-3. The directory was deleted afterwards.

The remaining errors are small. The main weakness is coverage. The page stops at Lab 3, so Labs 4 and 5 (Ch 14, 15) and their library-owned resources and loop costs are missing.

## Errors

**E1 (low): `#budget` "usable for arrays" row, the p01 preset note, and the checker.**
- Quoted text: "SAXPY links at N = 5,610 (49,120 B used) and fails at 5,620".
- What is right: the true limit is **N = 5,615**, which uses exactly 49,152 B. N = 5,616 fails with "ran out of PE memory for task table". Measured now with `cs_readelf -m`: 5,610 uses 49,120 B, 5,612 uses 49,136 B, 5,615 uses 49,152 B.
- This matches Ch 11 ("largest N that links is 5,615") and CROSS 13. The appendix and Ch 10 give only a bracket.
- Knock-on effect: the checker computes 11,230 f32 + 4,240 B = 49,160 B for N = 5,615 and reports "fails", but that build links. At the very edge the overhead is 4,232 B, not 4,240 B, because of alignment.
- Fix:
  - Write "largest that links: N = 5,615 (49,152 B, exactly full); 5,616 fails (task table)".
  - Either soften the over-48 KB verdict to "check" within about 16 B of the limit, or say in the hint that the overhead can be about 8 B smaller.

**E2 (low): `#constants` chain-reduce row.**
- Quoted text: "≈ M + 7P (WSE-3) / M + 5P (WSE-2)".
- This drops the fixed term. At P = 2 it predicts 46 against a measured 58, and at P = 8 it predicts 88 against 101.
- Ch 12's own model is "M + c·(P − 1) plus a fixed few tens". The measured data fit **M + 19 + 7.2(P − 1)** on WSE-3 (58, 101 and 274 against 58, 101 and 273) and **M + 17 + 5(P − 1)** on WSE-2.
- The WSE-2 cell also omits P = 32 = 204 cycles, which Ch 12 reports.
- Fix: use those fits and add 204.

**E3 (low): `#budget` stat tile.**
- Quoted text: "≈ 43.5 KB (≈ 44,500 B) … ± 0.7 KB with code size".
- That reads as 43,800–45,200 B, but the measured range in the table directly below is 43,600–44,920 B.
- Fix: write "≈ 43,600–44,900 B (42.6–43.9 KB), depending on code size". You can keep 44,500 as "typical (matvec probe)".

**E4 (low): Rosetta, "latency hiding by many warps" row.**
- Quoted text: "up to 8 async ops (one per microthread)".
- The budget card on the same page says memcpy moves its data with microthread 0, and the checker counts memcpy's microthread 0. So a user kernel gets at most 7 concurrent ops, and fewer for each FIFO, which takes 2.
- Fix: "up to 7 of your own (microthread 0 is memcpy's)".

**E5 (low): `#constants` bank/operand row.**
- The rule "half speed when its two sources start at addresses equal mod 4 words; adds unaffected" is stated for f32 only.
- CROSS 29 (App E) measured a different f16 behaviour. On WSE-2, @fmach is fast only when the sources are 4 banks apart (526 / 526 / 270 cycles). On WSE-3 it is 272 in all three cases.
- Fix: add "f16 behaves differently (App E): WSE-3 no clash; WSE-2 fast only 4 banks apart".

## Explanation problems

**X1: `#constants` memcpy rows mix inverse units.**
"H2D 1.0 cycle/wavelet … D2H 8.0" sits next to "a real channel is ≈ 0.26 wavelets/cycle". The reader has to invert one figure to compare them.
Fix: say "≈ 3.8 cycles per wavelet on hardware, about 4× slower than the simulator's H2D".

**X2: `#constants` "hop through a PE's program" notes.**
The note "own-clock step per PE reads 7.2 / 5.0" is cryptic on its own.
Fix: add Ch 12's explanation in a clause: "each PE's TSC starts one router hop later than its neighbour's, so own-clock readings are one hop (2.0 / 1.0) lower".

**X3: "Putting the constants to work" callout.**
- "≈ 6 for each further op in the same task" does not say when it holds. It needs compile-time DSDs, no scalar code between the ops, and no loop.
- A learner applying it to Lab 4's loop of 64 @fmacs (T = 8) would predict about 64 × (6 + 16) ≈ 1,400 cycles. Ch 14 measured 2,903 = 64 × (2·8 + 29).
- Fix: state the condition, and add a fourth bullet: "≈ 30 cycles per op when a scalar loop moves the DSD (Ch 6: 33–35; Ch 14: 2·Mt + 29 / 1.25·Mt + 31)". See G2.

**X4: `#saxpy` trimmed CSL hides the host-to-device naming.**
- The snippet drops `@export_name("x", …)`, the memcpy import and the `comptime { @export_symbol(...) }` block.
- `run.py` is shown without `xs, ys = rt.get_id('x'), rt.get_id('y')`.
- `xs` and `ys` therefore appear from nowhere, and the CUDA `dx` / `dy` device pointers have no visible counterpart.
- Fix: keep the `get_id` line. Add one Rosetta-style sentence: "the device pointer `dx` becomes an exported symbol name that the host resolves with `rt.get_id('x')`".

**X5: `#budget` "switch-capable colors" row.**
"4 route positions per color" is not explained and not linked.
Fix: link Ch 4 #switches and the glossary, or add "(a color can cycle through up to 4 route settings)".

## Connecting gaps

**G1 (med): CUDA `blockIdx`/`threadIdx` → "which PE owns which data" in a multi-PE program. Effort S–M.**
- The only worked example is SAXPY on a 1 × 1 rectangle. So the page never shows the two steps a CUDA programmer needs most:
  - how a PE learns its index: the layout loop passes `x` or `role` as a param, as program 03 does with `for x … @set_tile_code(x, 0, …, .{ .role = … })`;
  - how `memcpy_h2d(…, 0, 0, W, H, n_per_PE, ROW_MAJOR)` deals a flat array across PEs.
- The thread row asserts both points but shows neither.
- Bridge: a second small side-by-side. CUDA `i = blockIdx.x*blockDim.x + threadIdx.x` next to:
  - the layout loop of a 4 × 1 SAXPY;
  - `memcpy_h2d(xs, x, 0, 0, 4, 1, N/4, …)`;
  - a 4-cell diagram of which slice lands on which PE.
- Alternatively, point at program 03's layout with a two-line annotation.

**G2 (med): budget card and constants (Labs 1–3) → Labs 4–5 (Ch 14, 15), which the page never mentions. Effort M.**
- The appendix has no links to Ch 14 or 15, no presets for programs 06 and 07, and no constants from them.
- Ch 14's objectives include "Budget a kernel before writing it: memory, colors, task IDs, queues and microthreads, and a cycle model". That is exactly this page's checker, yet neither page links the other.
- The checker also cannot model library-owned resources. Ch 14 #collectives says each `<collectives_2d>` instance owns 2 colors, 2 local task IDs, 2 queue pairs and a DSR set. Ch 15 has a whole "resource budget of one PE, by owner" widget.
- Bridge:
  - (a) a budget-card row "libraries take their share too: `<collectives_2d>` per instance …, `<stencil_3d_7pts>`/allreduce … (Ch 14, Ch 15 budget map)";
  - (b) a preset for program 06 (SUMMA: two collective instances plus your tasks);
  - (c) constants rows from Ch 14 and 15: broadcast step ≈ 520 + 2T² cycles (WSE-3); per-@fmacs in an SDK loop 2·Mt + 29 (clashed) or 1.25·Mt + 31; CG allreduce ≈ 958 + 94(W + H) cycles per iteration (WSE-3), about 82 per PE of W + H on WSE-2; 4,574 cycles per CG iteration at 5 × 5 × 5;
  - (d) Rosetta rows "tiled GEMM with shared-memory tiles → SUMMA: owned tiles plus row and column broadcasts (Lab 4)" and "grid-wide sync / global reduction → allreduce, linear in W + H (Lab 5)".

**G3 (low–med): Tensor Cores row ("FLOPs come from 900,000 thin datapaths") → what a real GEMM achieves. Effort S.**
The row gives a per-cycle FMAC rate but no measured GEMM efficiency. Ch 14 has it: 18–34% of the 1 MAC/cycle ideal for the SDK loop, 47–60% for the outer-product kernel, up to 0.72 PFLOP/s whole-wafer at T = 41.
Bridge: one sentence with a link. This turns the peak into a realistic expectation.

**G4 (low): the chapters' "If you know CUDA" callouts → this appendix. Effort S.**
The callouts in Ch 5, 6, 7 and 10 do not link Appendix B. Only Ch 3 does, along with App A and App E. A CUDA reader meets the map piecemeal and is never told that the full Rosetta exists.
Bridge: end each callout with "Full map: Appendix B, row X" and link that row's anchor. Ch 14 #design and Ch 15's budget widget should link `#checker`.

**G5 (low): budget card "data tasks" (WSE-2: "task ID = color") → local task ID budget. Effort S.**
- The WSE-2 local-ID cell says "minus … the IDs of colors you receive on". The checker only warns on that collision.
- No worked example shows why receiving on color 10 steals local task 10.
- Bridge: one line under the card, e.g. "WSE-2: receiving on color 10 binds data task 10, so local task 10 is no longer yours".

## Checked and fine
- Rosetta facts:
  - memcpy reserves colors 20–23, local IDs 21/24/27/28/30, control IDs 33–37 and 40, queue 0 (plus queue 1 for commands on WSE-3); 29 is teardown and 31 is NOP; activatable IDs are < 31 (5-bit field).
  - `--params` takes unsigned integers only; `--arch` defaults to wse2; `<malloc>` and `<collectives_2d>` `reduce_fadds` exist in the SDK libs.
- Queue counts are 8/8 on WSE-3 (`target/wse3.csl`). WSE-3 queue depths match the comments in `memcpy/wse3/memcpy.csl` lines 205–211 and the Ch 7 table.
- The SAXPY snippet matches programs/01 (layout, pe_program, run.py, `--params=N:64`, fabric 8,3).
- Checker presets match programs 02–05: f32 counts 4/32/65/34, other bytes 4/12/12/24, queues, task IDs 9 and 10–13, colors, and `--params`. The fabric-dims formula matches every commands.sh.
- Memory:
  - SAXPY 4,240 B (4,752 at N = 64; 12,432 at N = 1,024); WSE-2 SAXPY 5,784 → 49,122 B;
  - Lab 3 limits n ≈ 5,450 / 5,650 → 5.5 / 3.9 KB overhead;
  - matvec probe 4,636 / 3,134 B; the to-scale memory figure.
- Vector rates (Ch 6 table): 526/271, 1,039/528, 1,041, f16 162/310 and 270/527; start-up 18/33/81/273/1,041; stride 162/290/546/799 and 294/550/804; matvec 54 + N + N² = 4,214; f16 matvec 1,335 / 2,165; 11.7 B/cycle.
- Fabric and host I/O:
  - hop 2.0 / 1.0; CE hop 9.2 / 6.0; collectives 754 vs 58; 16 wavelets per hop; store-and-forward 348 vs 101;
  - Lab 3 table (100.2 / 130.2 / 250.2, P = 2 101.0, WSE-2 134.1, 14.6, 13, ≈ 19 start-up) and the closing callout's 58.4 + 13 + 19 ≈ 90;
  - bandwidth-test rows (1,473; 1.0; 0.40; 8.0); 0.26 wavelets/cycle and 175 KB derivations; the "5 short" barrier result; the about 4 s stall; 743 × 992.
- All 129 in-page links resolve, including `17-gpu.html#saxpy-twice`.
- Cross-page note for the coordinator: Ch 14 still says "Chapter 3's smaller WSE-2 overhead (3.1 vs 4.6 KB)". Those are the matvec figures; SAXPY's are 2.85 / 4.24 KB.
