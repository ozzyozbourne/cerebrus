# R4 fix log: ch13 (Lab 3: a heat stencil, measured)

Edited `src/13-lab-stencil.html` only, then ran `python3 tools/build.py`. No simulator runs were needed: every new number comes from the r4 report, CROSS_CHAPTER_NOTES 30–38 or the SDK sources.
Verified with Playwright at 1100 px and 390 px. Results: zero console or page errors, no horizontal overflow at 390 px, and all 52 in-page and cross-page links resolve to existing files and ids.
Widgets driven: the timeline (n 4/16/64, interior and end PE, buggy queues, Play and Next event), the model slider and the rod widget (Play to step 50).

## Errors
- **E1** Fixed. The lede now reads "The third lab, and the first full application, simulates…".
- **E2** Fixed. Both 16-bit memcpy references (#tsc and the Half-precision hint) now point to Chapter 7 (`07-host-io.html#host-side`, the MEMCPY_16BIT text).
- **E3** Fixed. The 176→212 B figures are now labelled as an end-PE ELF. Added that cslc writes one ELF per code variant, and that the interior variant (`out_1_0.elf`, the code timed PE 1 runs) has 200-byte tasks before the change.
- **E4** Fixed. In the timeline widget, the 14.6 per transfer is now split into a 1.6 issue slot and a 13.0 completion task, with 12.9 bookkeeping. Interior totals are unchanged (100.2/130.2/250.2). The end-PE preset now gives 101.4 against the measured 101.0; the remaining 0.4 is a drawn wait before the first task. The hint and the readout state the split.
- **E5** Fixed. The text now says that on both chips only microthreads 2–7 are free, so at most six fabric ops can be in flight (link to Ch 5's budget table). It also says the limit is at least as tight on WSE-2.
- **E6** Fixed. Added "(WSE-3 build)" in the table and the text, and quoted wse2/pe.csl's "output_ut_id is NOT used in WSE2".
- **E7** Fixed. The CS-1 BiCGSTAB tag is now `vendor` ("Cerebras/NETL paper").
- **Cross-page (05-tasks ~88)**: not my file. Listed under For other pages below.

## Explanation problems
- **X1** Fixed.
  - Every "Chapter N" mention now links to a section anchor: Ch 3 #microthreads; Ch 4 #checkerboard and #latency; Ch 5 #budget, #activates, #picker, #hang-callout, #portability and #priority; Ch 6 #builtins, #op-speed, #collisions, #lab3-update and #dsd; Ch 7 #command-stream and #host-side; Ch 11 #kernel-time; Ch 12 #roles, #measuring and #hop-cost; Ch 14 #summa and #measure; Ch 15 #modules and #profile; App C #tsc.
  - Glossary links added for: stencil, halo/ghost cells, microthread, activate, unblock_cmd_stream, back-pressure, ut_id, sim.log, is_arch, TSC, weak scaling, bank clash, hop, SpMV and pencil.
  - Two glossary entries the report named do not exist yet: Dirichlet and strong scaling. Both are explained inline instead.
- **X2** Fixed. The hint now separates the diffusion time, L²/(2α), from the e-fold time of the slowest mode, L²/(π²α) ≈ 6,640 at L = 128. It says to allow 3–5× the e-fold time.
- **X3** Fixed. The model readout now says "CS-2's 737k SDK-visible PEs … 5 flops/cell".
- **X4** Fixed. The text now says "≈2.5 on both (exactly 2.5 on WSE-3; 2.50 for n = 4→16 and 2.53 for n = 16→64 on WSE-2)".
- **X5** Fixed. The text now says what the 25-pt run.py prints: the TSC time on PE (width−1, 0) divided by iterations × zDim, i.e. cycles per timestep per z-cell. That reading was checked against the SDK run.py source.

## Connecting gaps
- **G1** Fixed. Added a paragraph saying:
  - α = DΔt/Δx²;
  - the scheme is stable only for α ≤ 0.5 (von Neumann; a growing checkerboard above that);
  - 0.25 is a power of two, so the products are exact and the fused ops round once, which is why the result is bit-identical;
  - the rod widget shows the three stability regimes.
- **G2** Fixed. Added a three-row mapping table (u[j−1]/u[j]/u[j+1] to left/mid/right, j = i + 1). Spelled out `@fmacs(dst,a,b,s)` as dst = a + b·s and wrote all three instructions out in that form. Linked Ch 6's #lab3-update section and its DSD visualizer's "Lab 3 stencil" preset.
- **G3** Fixed. Added a sentence on `fabout()` and `@initialize_queue` with `@is_arch`: it is the same split as Lab 2's send. Linked Ch 12 #roles and Ch 5 #portability.
- **G4** Fixed. Added a sentence on what the 14.6 covers: issue, picker, task entry and exit, and the inlined body. It is the course's best measurement, not a constant, and it grows with task size (inlining-trap evidence). The fixed cost is stated as ≈90 (CCN 37); Ch 5's stale 88 is routed below.
- **G5** Fixed. Added a forward pointer: Lab 5 uses `stencil_3d_7pts` as its SpMV (links to Ch 15 #modules and #profile).
- **G6** Fixed. Added a "Next: Lab 4" paragraph: Lab 4 moves to a 2-D grid with row and column broadcasts and is compute-dominated (links to Ch 14).
- **G7** Fixed. The text now says "As in Labs 1 and 2 (Ch 11, Ch 12) …", and that what is new here is pack() and the slope method. Linked App C #tsc.
- **G8** Fixed. "No race on the ghosts" (new anchor `#no-race`) now has the two-step argument: finishing step s+1 needs the neighbours' step-s+1 edges, which they send only after finishing step s. It also says the early wavelet waits in the queue until after `update()` has read the old ghost.
- **G9** Fixed. Weak and strong scaling are defined in the "Weak scaling is flat" bullet, with a glossary link.

## Cross-page items about this page
- **r4-ch07 E1 / CCN 31 (launch)** Fixed. Step 1, step 5 and the quiz now say that `launch()` returns at once and that the next command (memcpy_d2h) is what waits. run.py has no comment claiming otherwise.
- **r4-appE (CCN 30): "we have not isolated why" for WSE-2 @fadds** Fixed. Replaced with the one-line layout rule: u[i] and u[i+2] are 8 B apart, opposite halves of the 16-byte bank cycle. Also:
  - Retired the "f16 3.2/cycle WSE-3, 2.0 WSE-2" rates in the half-precision hint and answer, and replaced them with the CCN 30 placement rule.
  - Reworded "f32 gains nothing from WSE-3's wider FP16 SIMD".
  - The k = 4 re-alignment note now cites the placement rule, not "clash rule differs".
- **CCN 33 (clock)** Fixed. The caveats name 850 MHz [SDK] and the ~1.4 GHz CS-4 press estimate [Analyst, unverified], which would scale the per-second figures by about 1.6×.
- **CCN 34, 37** Already consistent (2.0/1.0 hop, 9.2/6.0 through-PE, 90 + 2.5·n).
- **r4-ch18 E5 (CS-2 fabric)** This page already said CS-2. The model readout now says "CS-2's 737k" too.
- **r4-appD (bicgstab filter)** Skipped: that is App D's change.

## For other pages
- **05-tasks.html** (§When several tasks are ready): "Lab 3's measured ~88 fixed cycles per step" should be ~90 (90.2 + 2.5·n). Point to `13-lab-stencil.html#fixed-cost` for the 14.6-per-transfer split. My new text links to `05-tasks.html#priority` and says Ch 5 uses the ≈90.
- **06-dsds.html**: line ~204 still credits "WSE-3 doubled … adds" as the reason Lab 3 is a wash. Per CCN 30 it should cite placement. This page links `06-dsds.html#collisions` for the bank rule. If the Ch 6 fixer adds `#banks`, these links could be retargeted (they work as they are).
- **appendix-a-glossary.html**: consider entries for "ghost cell" (alias of g-halo), "Dirichlet boundary" and "strong scaling" (r4-appA also asks for strong scaling).
- **appendix-d-sdk-index.html**: the bicgstab row has 13 in its filter. The Where cell could link `13-lab-stencil.html#sdk-stencils` (the CS-1 BiCGSTAB caveat is in "Scaling up").
