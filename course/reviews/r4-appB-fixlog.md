# R4 fix log: Appendix B (appB)

Page: appendix-b-cuda-to-csl.html (hand-written; no build step). One experiment: the 4 × 1 SAXPY sketch (program 01's pe_program.csl unchanged, new layout + run.py), WSE-3, N_PE = 16: compiled and printed SUCCESS!. Scratch dir deleted.

| ID | Status | What changed |
|---|---|---|
| E1 | Fixed | Usable-arrays row now says largest SAXPY that links is N = 5,615 (49,152 B, exactly full), 5,616 fails (task table). p01 preset note updated. Checker: a total up to 8 B over 48 KB is "check", not "fails" (EDGE = 8, the measured alignment slack 4,232 vs 4,240 B); hint text says so. Verified: N = 5,615 → check, 5,616 → fails. |
| E2 | Fixed | Chain-reduce note: M + 19 + 7.2(P − 1) (WSE-3), M + 17 + 5(P − 1) (WSE-2), tagged Derived fit; WSE-2 P = 32 = 204 added; says the 7.2/5 is the own-clock step, not the hop cost. |
| E3 | Fixed | Stat tile: ≈ 42.6–43.9 KB (43,600–44,900 B) depending on code size; 44,500 B kept as "typical (matvec probe)". |
| E4 | Fixed | Latency-hiding row: up to 7 of your own async ops (microthread 0 is memcpy's, minus 2 per FIFO). Microthread budget row also says "at most 7 are yours". |
| E5 | Fixed | Bank/operand rows (Rosetta and constants) restated as the item-30 single rule, with f16 behaviour (WSE-3 no clash; WSE-2 fast only 8 B apart) and f32 @fadds WSE-2 placement dependence. |
| X1 | Fixed | memcpy row: ≈ 3.8 cycles per wavelet on hardware, ≈ 4× slower than the simulator's single-channel H2D (Derived). |
| X2 | Fixed | Hop-through-PE note explains the own-clock 7.2 / 5.0: each PE's TSC starts one router hop (2.0 / 1.0) later. |
| X3 | Fixed | Callout: the "≈ 6 per further op" condition stated (back-to-back, compile-time DSDs, no scalar code, no loop); fourth bullet "≈ 30 per op in a scalar loop" with the Lab 4 example (2,903 ≈ 64 × (2·8 + 29) vs ≈ 1,400). Links to #checker and Ch 14 #design. |
| X4 | Fixed | SAXPY snippet shows @export_name("x"), x_ptr/y_ptr, the comptime @export_symbol block and `xs, ys = rt.get_id(...)`; one sentence maps dx/dy → exported symbol resolved by rt.get_id. |
| X5 | Fixed | Switch row: "a color can cycle through up to 4 route settings (switch positions), advanced by control wavelets", glossary link; Ch 4 #switches already linked. |
| G1 | Fixed | New section #multi-pe: CUDA index vs 4 × 1 SAXPY layout loop + memcpy_h2d(…, 4, 1, N_PE), inline SVG of which slice lands on which PE (light/dark checked), paragraph on params (program 03's role) vs run-time coordinate (collectives_2d), ELF-count trade-off. Thread row links to it. |
| G2 | Fixed | (a) new budget row #libs-row: collectives_2d per-instance share, program 06 and 07 assignments, library overhead 6,750–8,560 B Derived from SUMMA link limits; links Ch 14 #collectives, Ch 15 #bud. (b) checker preset p06 (SUMMA P = 4, T = 8, overhead 8,564 / 6,744 B per chip, so T = 45 lands exactly at 48 KB). (c) constants section "Lab 4 and Lab 5": broadcast 520 + 2T² / 429 + 2T², scalar-loop @fmacs 2·Mt + 29 / 1.25·Mt + 31 / WSE-2 2.12·Mt + 27, CG allreduce 958 + 100W + 88H / ≈ 82 per PE, CG iteration 4,574. (d) Rosetta rows "tiled GEMM → SUMMA" (#r-gemm) and "grid-wide sync / global reduction → allreduce" (#r-gridsync). |
| G3 | Fixed | Tensor Cores row: Lab 4 reached 18–34% (SDK loop) and 47–60% (outer product) of 1 f32 MAC/cycle, ≈ 0.72 PFLOP/s whole-wafer at T = 41; links Ch 14 #findings and #scale. |
| G4 | Partly | This page's side done: every Rosetta row now has an id (r-kernel, r-grid, r-thread, r-warp, r-wait, r-syncthreads, r-atomics, r-launch, r-memcpy, r-occupancy, r-latency, r-banks, r-gemm, r-gridsync, …) and the checker has id="checker". The links from Ch 5/6/7/10 callouts and Ch 14/15 must be added by those pages (see below). |
| G5 | Fixed | WSE-2 local-ID cell: "Example: receiving on color 10 binds data task 10, so local task 10 is no longer yours". |
| Item 30 | Fixed | Warp row, Tensor row, @fadds/@fmacs/f16 rows, bank rows, f16 matvec row ("this kernel's placement, not the chip's rate"): retired "3.2 f16", "memory traffic" explanation, "reason unknown"; one-line rule in the constants intro; links Ch 6 #collisions (Ch 6 #banks did not exist when I checked; see below). |
| Item 31 | Fixed | SAXPY text: launch returns; the next copy waits and fails after about 4–5 s. |
| Item 33 | Fixed | Clock row and constants intro: 850 MHz (SDK) and ≈ 1.4 GHz press estimate (Unverified); "say which clock". |
| Item 34 | Fixed | Constants intro: "one hop per cycle" is a hardware-paper figure; WSE-3 simulator models 2. Old "M + 7P" removed (E2). |
| Item 38 | Fixed | ~35 new glossary links (CUDA-side terms in the first column, first uses of CSL terms); "Lab 3" in the callout linked. All 197 links resolve. |
| r4-ch03 E1 (App B's f16 copy) | Fixed | via item 30. |
| r4-ch13 G4 (14.6 mechanism) | Fixed (this page's part) | 14.6 row: "best figure for issue + task dispatch + task body; grows with the task's size". |

Verification: Playwright at 1100 px and 390 px, light and dark: 0 console/page errors, no horizontal overflow (scrollWidth 1100 / 390), all 197 hrefs and anchors resolve, all 9 presets load, p06 OK on both chips, filter chips and TT toggle driven.

## For other pages
- Ch 5, 6, 7, 10 "If you know CUDA" callouts: end each with a link to the matching App B row, e.g. `appendix-b-cuda-to-csl.html#r-wait` / `#r-syncthreads` (Ch 5), `#r-warp` / `#r-loop` / `#r-banks` (Ch 6), `#r-launch` / `#r-memcpy` / `#r-streams` (Ch 7), `#r-kernel` / `#r-grid` (Ch 10).
- Ch 14 #design and Ch 15 #bud: link `appendix-b-cuda-to-csl.html#checker` (now has a program 06 preset) and `#libs-row`.
- Ch 17 (r4-ch17 G6) and Ch 18 (r4-ch18 X5): link `appendix-b-cuda-to-csl.html#rosetta`; for thread-block clusters, `#r-cluster`.
- Ch 14 exercise 3: "Chapter 3's smaller WSE-2 overhead (3.1 vs 4.6 KB)" are matvec figures; SAXPY's are 2.85 / 4.24 KB.
- Ch 6: if `#banks` is created per item 30, App B's links to `06-dsds.html#collisions` can be retargeted to `#banks`.
