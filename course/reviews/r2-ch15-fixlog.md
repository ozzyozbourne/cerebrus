# Round-2 fix log: Chapter 15 (Lab 5, CG)

Edited: `course/src/15-lab-cg.html` only, then `python3 course/tools/build.py`. `course/programs/07-cg/` unchanged (no
finding needed a program change), so `expected_output.txt` stands.

New measurements (SDK 2.10.1 simulator, traces off, scratch copies, TSC on the centre PE):
- WSE-3, Z=5, 6 iterations: 10x6 allreduce 2,486 (fit 2,486), 5,170 cyc/iter; 6x14 allreduce 2,790 (fit 2,790), 5,474.
- WSE-2 10x6: allreduce 2,065 (82/PE slope predicts ~2,053), 4,699 cyc/iter.
- 2-value allreduce (`eta` as [2]f32, `allreduce(2, ...)`): allreduce bucket 1,900 vs 1,898; stencil 1,876 vs 1,866.
- Z=100 BLOCK=100: allreduce over all PEs 1,951-2,438 (centre 2,292); Z=100 BLOCK=2: 1,898-2,236.
- Max column (compile only, 5x5, MAX_ITE 30): WSE-3 BLOCK=2 Z ~1,835-1,842 links, BLOCK=100 ~1,757-1,764, WSE-2 BLOCK=2 ~1,978-1,983;
  above that `ld.lld: error: ran out of PE memory for data (section .bss)`.
- Exercise 4's move (allreduce color 9, tasks 8-11, state task 13): compiles on WSE-3 and WSE-2 (and see open issues on the run).
- numpy f32 copy of run.py's recurrence: Z=5 iterations 15/24/30/35/39/39 for 5,10,16,32,64,128 PEs a side (kappa 13.9 ... 43.6,
  cap 43.8); cubes 5^3...48^3: 15/24/34/45/65/83/123 iterations, true residual 5.7e-6 ... 2.0e-5 (24^3), 8.9e-5 (48^3).
  Note: the accuracy review's "kappa 19.3 for 10x10x5" is wrong; it is 26.9.

| ID | Status | What was done |
|---|---|---|
| A1 / P1 / D1 | fixed | "How many iterations?" now says the cube law holds only when all three sides grow and that kappa is capped (~44) at fixed Z. "Iterations grow too" became "Iterations: it depends on which sides grow" with a numpy table (kappa, iterations, bound) at Z=5 up to 950x950. Scaling-law callout split into weak scaling (linear in the side, through the allreduce) and growing cube (N^2 asymptotically). Quiz Q6 rewritten. Cost widget gained a fixed-column whole-wafer preset and a "levelled off" readout line. |
| A2 | fixed | "about 40 times its 7 multiply-adds" (≈7 cycles at 1 FMAC/cycle). |
| A3 / P3 | fixed | Dots (1,115) "more than half the one-block stencil (1,957) and more than the three axpys (898)"; also says the 1,115 covers both dots. |
| A4 / P7b | fixed | "eleven mark() calls (seven in phases, four in phase_done), ~30-35 cycles each"; notes record()'s timestamp stays with PROFILE=0. |
| A5 | fixed | Callout gives other work ~2,700 at Z=5 and ~30,000 at Z=100. |
| A6 / P6b | fixed | Lab 3 split quoted from Ch13 #fixed-cost: 90-cycle floor, ≈15 per transfer+task, ≈6 start-up per vector instruction in a task, ≈17 isolated (Ch6). |
| A7 | fixed | "about 300 lines ... imports about 2,200 (2,900 counting both chips' stencil variants)". |
| A8 | fixed | Bound uses only kappa; CG adapts to the eigenvalue distribution and to b's components. |
| A9 / V9 | fixed | Cost model uses measured 352/1866/165 and control 295 at Z=5 (control per Z = remainder of measured totals); readout shows the measured total where one exists; presets set W/H exactly (950, not 951). Default model still sums to 4,576 vs measured 4,574 (bucket rounding), shown side by side. |
| A10 | fixed | "essentially all of it ... control +1,262 while axpy/allreduce fall slightly". |
| A11 | fixed | Widget errors cite `wse3/pe.csl:…` and `allreduce/pe.csl:1097`; sentence below the table explains the file. |
| A12 | fixed | WSE-2 host-loop gap given as "about 1,140-1,150 (run to run)". Widget keeps 5,333. |
| A-tags | fixed | Derived tag on the per-call per-PE coefficients; "Chapter 12 measured" with link to #collectives instead of "Chapter 12's review". |
| P2 | fixed | Exercise 1 uses 10x6 and 6x14 (not in the fit) plus a WSE-2 10x6 prediction; measured answers given (above). |
| P4 | fixed | Exercise 3 defines Chronopoulos-Gear's w = A r, reduces the experiment to a two-line change (2-element eta), gives the measured answer (1,900 vs 1,898: priced per call, not per value) and the saving; mentions pipelined CG. |
| P5 | fixed | Exercise 4 hint covers 21-24 (21 D2H task, 21-23 topic-09 reserved, 24 SYS_EN_MAIN, Ch5 link) and why colour 9 is safe (memcpy 20-23, Ch7 table link). Verified the move compiles on both chips. |
| P6a | fixed | TSC cross-PE pointer now links Chapter 13 (Lab 3). |
| P6c | fixed | see A-tags. |
| P7a | fixed | "The four phases of an iteration ... plus three set-up phases". The program's header comment ("five phases", listing four plus the check) left unchanged to avoid touching the program. |
| P8 | fixed | Paragraph after the numpy block defines A(v), x0, tol, eta; new table maps numpy lines to the four device phases. |
| P9 | fixed | Q5 now carries the arithmetic (5 × 200 µs vs 4,261/850 MHz) and the non-blocking caveat; new quiz items on the import-path trap and BLOCK at Z=100. |
| P10 | fixed | Callout says "asymptotically, once the allreduce dominates". |
| V1 | fixed | New figure `#ar-svg`: three 4x3 panels (row reduce, column reduce, multicast broadcast) with teardown + reset between stages, and a step-by-step strip of one row showing switch positions (sw 0/1), control wavelets, farthest-first arrival and the final teardown. |
| V2 | fixed | Text: "no slot is claimed twice, on either chip"; points to the WSE-2 experiment. Prose below the table also says the shipped program keeps slots separate. |
| V3 | fixed | z-tab headers shortened (Z, cycles / iter., SpMV, dot, axpy) and explained in the lead-in; fits at 390 px (screenshot checked). Tables were already in .table-wrap. |
| V4 | fixed | Cost bars now have logarithmic length on fixed axes (1k-1M cycles per iteration, 10k-1G per solve), with a dashed outline of the 5x5x5 default; second bar shows per-solve cycles. |
| V5 | partial | Added a phone-only hint above the budget map that it scrolls and where the hidden IDs are. Did not redraw the rows in two lines of 12; iteration/cost widgets not changed (their bars start at the left edge, so the key part is visible). |
| V6 | fixed | queue experiment also adds the allreduce to output queue 4. |
| V7 | fixed | DSR row (dest/src0/src1, 0-3) with the ledger's assignments; memcpy colours drawn 20-23 per Ch7 (sys_params); WSE-3 tasks 21-23 drawn hatched "reserved". The SDK CG comment's "21-30" is quoted in the hint. |
| V8 | fixed | Labels measured with getBBox; fall back to the percentage, or nothing. |
| V10 | fixed | (a) "device × 200" magnified bar; (b) neutral grey for host waiting, accent for device time; (c) host bar uses the host loop's own PROFILE=0 5,488 cycles; (d) simulated bars scaled so each ends at the measured total. |
| V11 | fixed | y-axis title, dotted EPS=1e-5 line with label, in-plot legend (solid measured, dashed bound), 12³ label moved off the 8³ bound. |
| V12 | fixed | Left panel is now an oblique 3-D box with the centre PE's pencil drawn through it; caption explains the green vectors. |
| V13 | fixed | `<memcpy/get_params>` box with arrows in the module graph; caption mentions it. |
| V14 | fixed | New scatter `#fit-svg`: measured allreduce vs W+H (WSE-3 seven grids, WSE-2 two grids) with the square-grid fit line. Exercise grids deliberately not plotted. |
| D2 | fixed | Callout: 180k describes this library (≈50 cycles/PE/call); table of per-PE costs for one 950-PE row stage (library ≈47,500; CE-forwarded chain 9.2/PE ≈8,700, Ch12; hop floor 2/PE ≈1,900, Ch4), per iteration ≈40k / ≈15k vs 180k, all Derived; SC20 BiCGStab ~1/3 of peak via Ch18, Unverified for allreduce latency. |
| D3 | fixed | New "f32 at scale" callout with the numpy true-residual drift and remedies (true residual check, residual replacement, higher-precision dot accumulation, sum order). |
| D4 | fixed | 16·BLOCK bytes (1.6 KB at 100) buys 4.9×; measured max Z per PE (WSE-3 ≈1,835 / 1,757, WSE-2 ≈1,978); ≈1.6e9 unknowns on a wafer (Derived). Says we have no measurement of what BLOCK=2 buys. |
| D5 | fixed | "How far from peak": 23 flops/cell/iteration, 1.3% at the default, ≈17% at Z=100 BLOCK=100 (Derived). |
| D6 | fixed | Paragraph on nonblock=True: ≈200 µs-1 ms per iteration (Derived), still 40-200×. |
| D7 | fixed | Pipelined CG (Ghysels-Vanroose) in the callout and in exercise 3; overlap needs disjoint slots on both chips (the WSE-2 shared-queue experiment would break) and a phase_done that waits for both. Note: the reviewer's premise that the shipped WSE-2 build shares queue 3 is wrong (stencil out 3, allreduce 2); only the experiment shares it. |
| D8 | fixed | Jacobi (SDK PCG, README) with constant diagonal 6 only rescales A; stronger preconditioners meet the same communication cost. |
| D9 | fixed | Reported the all-PE range at BLOCK=100 (1,951-2,438) vs BLOCK=2 (1,898-2,236): extra on the centre PE is mostly barrier waiting. |
| D10 | fixed | "(profiling on)" on the 41%/41% cards. |
| D11 | fixed | Barrier callout now argues from the 228-cycle spread; equal iteration times are called what any barrier loop shows. |

Also changed: the grid paragraph now says the allreduce cost is per contributing PE, not per "value" (the 2-value experiment
shows a second value costs ~1 cycle per PE).

Validation: Playwright, 1100 and 390 px, light and dark, plus the ◐ toggle; every budget experiment on both chips, legend
hover, all chip/view pairs of the iteration widget, all cost presets and slider extremes. Zero page/console errors, no page
overflow, no clipped elements outside scrollers; screenshots inspected.

## Open issues
- The cost model at 5x5x5 sums to 4,576 vs the measured 4,574 (bucket averages are rounded); both are shown.
- V5 only partly done (hint, no two-line redraw).
- What BLOCK_SIZE:2 buys the SDK is still unmeasured; the SC20 allreduce latency is unverified.
- `pe_program.csl` header comment still says "five phases" (four plus the check); left to avoid touching the program.
