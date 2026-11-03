# Review r2: Chapter 14 (Lab 4: SUMMA GEMM), accuracy

Scope: `14-lab-gemm.html` / `src/14-lab-gemm.html` / `programs/06-summa`. I checked every number on the page against the program's real output, the `collectives_2d` library source (`csl-libs/collectives_2d/{pe,params,ctrl_wavelet}.csl` in the SIF), CROSS_CHAPTER_NOTES and the chapters the page cites. I re-ran things in `/home/user/cerebras-sdk/tmp/r2-ch14-acc/` with simulator traces off:
- 7 simulations: the default on WSE-3 and WSE-2, kernel 1 at T=8 (run twice), the GEMV warm-up, and Mt = 15/16/17;
- the exercise-4 clash fix at P=2, T=16;
- 15 link-only cslc builds.

**What reproduced exactly** (TSC):
- default WSE-3 14,422 = 2,601 + 11,612 + 209, and WSE-2 13,514 / 2,233 / 11,072;
- kernel 1 at T=8: 1,594 per step and 9,186 total (one run gave 9,194, i.e. +8 cycles of broadcast noise);
- GEMV warm-up: 717 / 1,114 / 7,533;
- Mt sweep: 3,192 / 3,896 / 3,352;
- exercise 4's fix: 13,739 on every step and every PE;
- WSE-3 link limits: kernel 0 links at 45 and fails at 46 ("task table"); kernel 1 links at 41 and fails at 42;
- WSE-2 kernel 0: links at 46, fails at 47.

I also recomputed every derived percentage, fit and ratio from the table data (the 80/94/97.5% shares, the 520 + 2T² and 429 + 2T² broadcast fits, the 18/32/34/51/47% of ideal, 1.6×, 2·Mt + 29, 1.25·Mt + 31, 69.7, 23%, 6%, the 37/38/48% GEMV numbers, the chain/tree numbers in exercise 6, and the 13 GB host load). All are correct. The library description matches the source:
- route-rewrite code;
- comptime start state in teardown mode with PE 0 as root;
- `no_ce` TEARDOWN control wavelet sent only by the root;
- T29 handler activates LOCK;
- queues 2/4 and 3/5;
- the TIP warning;
- `pe.csl` is 1,312 lines.

## Findings

**A1 (high). The WSE-2 kernel-1 memory limit is wrong, and so is the "unexplained" mystery built on it.**
- Location: exercise 3 expected result; budget calculator `LIM.wse2["1"] = [36504, 38400]`; "Scaling up" (kernel 1, T = 39).
- The page says kernel 1 links only up to T = 39 and fails at 40 with ".data.hi", and that "We have not found why the WSE-2 kernel-1 limit is lower."
- Evidence: with the shipped program, `cslc --arch=wse2 … kernel:1` links at T = 40, 41 and 42 (rc=0, "Compilation successful"). It fails at 43 and 44 with "ran out of PE memory for data (section .data.hi)". So T = 42 links: 24·42² = 42,336 B, the same budget as WSE-2 kernel 0 at T = 46 (42,320 B). Nothing is anomalous.
- Fix:
  - exercise 3: "kernel 1 links at 42 (42,336 B) and fails at 43 (.data.hi)", and delete the "not found why" sentence;
  - `LIM.wse2["1"] = [42336, 44376]`;
  - redo the kernel-1 wafer line (see A2);
  - remove this item from build-ch14's open issues.

**A2 (high). The wafer-scale extrapolation uses tiles that cannot link at P = 743, and the wrong kernel-0 tile.**
- Location: "Scaling up"; budget calculator memory verdict.
- (a) The program's timestamp array is 6·(3P + 2) bytes. That is 84 B at P = 4, but **13,386 B at P = 743**. The link limits were measured at P = 4. Evidence: WSE-2, kernel 0, T = 45 links at P = 4 and P = 100, but **fails at P = 200** (".data.hi", 3,612 B of stamps).
- (b) The text says "largest tiles that linked on WSE-2", then uses T = 45 for kernel 0. 45 is WSE-3's limit; WSE-2 links 46.
- (c) The calculator compares only the tile bytes (`tiles <= okB`) and leaves out the timestamps it draws. So P = 743, T = 45 reports "fits".
- Fix:
  - State that the extrapolation assumes the per-step stamps are removed, keeping only the 2 stamps (main and exit).
  - Use the corrected tiles. Recomputed with the page's own fits and the 1.1 GHz clock:
    - kernel 0, T = 46: step ≈ 4,661 + 263,900 cycles; 0.18 s for 34,178²; 0.44 PFLOP/s; 36%.
    - kernel 1, T = 42: step ≈ 3,957 + 152,900 cycles; 0.106 s for 31,206²; 0.57 PFLOP/s; 47%.
  - In the calculator, compare `arr` (tiles plus stamps) with the limits, or add the stamps' growth to the warning text.

**A3 (med). Wrong share of fixed overhead at Mt = 8.**
- Location: "Where the other two-thirds go", first bullet: "With Mt = 8 that alone is about 80% of the instruction."
- Evidence: the page's own numbers give 45.4 cycles per @fmacs at Mt = 8 with a fixed part of ≈29. That is 64%, not 80%. 80% is roughly 29/(29 + 8), i.e. the share if there were no clash.
- Fix: "about two-thirds of the instruction (29 of 45 cycles)".

**A4 (med). Kernel 1's per-element fit and its ablation disagree, and Q7 relies on the fit only.**
- Location: "Kernel 1: fewer, longer instructions"; callout paragraph on kernel 1; Check yourself Q7.
- The fits give 1.87 (WSE-3) and 2.0 (WSE-2) cycles per element for the pair. The ablation gives @fmuls 1.6/1.35 plus @fadds 0.5/1.0, i.e. 2.1/2.35. The measured T = 16 point is 8,914/4,096 = 2.18 per element (incl. overhead) on WSE-3. So the "fit over T = 8–32" hides a T-dependent per-element cost.
- Q7 attributes WSE-2's smaller gain only to @fadds. Its @fmuls is actually faster on WSE-2 (1.35 vs 1.6), which partly offsets that.
- Fix: say the fit is approximate and the per-element cost varies with T (≈2.2 at T = 16, ≈1.95 at T = 32 on WSE-3). In Q7, mention both terms. The real reason is mainly kernel 0 being cheaper on WSE-2 (96,630 vs 103,724 at T = 32).

**A5 (low). Chart/calculator fit for kernel 0 differs from the text's model.**
- Location: JS `FIT.k0 = [2.32, 29.6]` (WSE-3) and `[2.12, 27.2]` (WSE-2), against the text's "2 cycles per element + 29–38".
- At T = 8 the JS fit predicts 3,082 against 2,903 measured (+6%).
- Fix: either say in the chart caption that the line is a least-squares fit (2.32·Mt + 29.6), or use 2·Mt + c(T) as the text does.

**A6 (low). Wrong chapter cited for the ~44 KB rule of thumb.**
- Location: exercise 3 hints: "Chapter 10's rule of thumb leaves about 44 KB".
- Evidence: Chapter 10 (csl-toolchain) does not contain it. The 44 KB figure is in Chapter 3 (measured) and Chapter 11.
- Fix: "Chapter 3's".

**A7 (low). Chain/tree crossover for one word is nearer P ≈ 6 than 8.**
- Location: "Chain or tree?" callout.
- Evidence: 9P = log₂P·16 + 2P gives a crossover between P = 5 (35 vs 37) and P = 6 (42 vs 41). P ≈ 35 for M = 32 is right.
- Fix: "about P ≈ 6".

**A8 (low). The routing text overgeneralises.**
- Location: after the abridged `configure_broadcast_network`: "Every non-root router passes the wavelet both to its own CE (RAMP) and onward."
- Evidence: in `pe.csl` (lines 546–551), non-root PEs at either end of the line (pe_id 0 or NUM_PES−1) use `.tx = RAMP` only.
- Fix: "every non-root router in the middle of the line…; the two end PEs only take it to their CE".

**A9 (low). Exercise 5 asks "Which is fastest per multiply-add?" but never answers it.**
- Evidence: per MAC, Mt = 17 costs 3.08 cycles, Mt = 15 costs 3.33 and Mt = 16 costs 3.80.
- Fix: "Mt = 17 is fastest per multiply-add (3.08 cycles vs 3.33 for 15 and 3.80 for 16)".

**A10 (low). Design-table step 9 is vague and contradicts the measurements.**
- Location: design table step 9: "the model was off by 2× on compute until the operand collision was found."
- Evidence: the ideal model is off by 3–5.5× (18–32% of ideal), and the collision accounts for only part of that (46% of ideal after the fix).
- Fix: "the measurement was 3–5× above the ideal; the operand collision explained 1 cycle per MAC of it, instruction start-up most of the rest".

**A11 (low, provenance/hygiene).**
- The build report says the program directory is clean, but `programs/06-summa/` currently holds `out/`, `run.log`, `sim.log`, `sim_stats.json` and `simconfig.json` from a WSE-2 run.
- The table's WSE-3 kernel-1 values are reproducible but show ±8-cycle broadcast noise (9,186 vs 9,194 on reruns). The page should keep "less than 1%" wording rather than imply exact cycles. It does not claim ±0, so this is fine.

## Counts
High 2 (A1, A2) · Med 2 (A3, A4) · Low 7 (A5–A11).
