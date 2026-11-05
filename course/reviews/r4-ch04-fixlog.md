# R4 fix log: Chapter 4, The fabric (04-fabric.html)

Experiments (scratch /home/user/cerebras-sdk/tmp/r4fix-ch04/, now deleted). I rebuilt the hop round-trip program. WSE-3 M=1 gave 44 / 164 at P=2/32, M=64 gave 137 at P=8. WSE-2 M=1 gave 48 / 96 at P=8/32. These match the page table within a few cycles. Multicast stall test, 3-PE column with program 05's routes, middle PE's CE busy before it receives: see G3. I ran topic-06 and topic-08 with `commands_wse3.sh` and both print SUCCESS.
Verification: Playwright at 1100 px (light and dark) and 390 px. 0 console or page errors, 0 horizontal overflow. All 75 hrefs resolve (files and #ids). I drove the latency calc, planner, back-pressure widget and fabric simulator (topic-06 pattern still "match"), and opened both try-it boxes.

## Errors
- **E1 Fixed.** The "~7 cycles per PE" claim is gone. The new #ce-hop paragraph gives 9.2 (WSE-3) / 6.0 (WSE-2) per PE versus 2.0 / 1.0 for a router hop, links Ch 12 #hop-cost, and explains why the old number was an artefact.
- **E2 Fixed.** The planner items are relabelled "one PE sends to its 4 neighbours, no switches (4) / with switches (topic-06) (1)". A new hint says switches save colors at one sender but do not remove the checkerboard (the 2-D exchange stays at 8).
- **E3 Fixed.** Color 20 is now described as "context-switch routing, SYS_RXCTX in memcpy/sys_params.csl".
- **E4 Fixed.** The index-field reference now points to Ch 3 #sparsity and Ch 6 #index-offset.
- **E5 Fixed.** The first figcaption now says "lossless, and a stalled color does not block other colors". It adds that programs can still deadlock themselves, with a link to Ch 5 #rules.
- **E6 Fixed.** It now reads "On WSE-2 it compiles [Measured, cslc] and then hangs or gives wrong sums", citing the auditor's hung run [Measured].
- **E7 Fixed.** The parenthetical is replaced by the 21 + 6 + 4 = 31 reconciliation: the 5-bit `.activate` ID space ("color 0~30", sys_params). The "6" counts IDs, not routable colors [SDK]/[Derived].

## Explanation problems
- **X1 Fixed.** The checkerboard caption now says color swap still uses two colors and only saves the parity-dependent routes. It notes that topic-14's route is a pure forward. I also corrected the field name: `.color_swap_x` (topic-14 layout), not `swap_color_x`.
- **X2 Fixed.** The table row is renamed "PE coordinate register (not a wavelet field)". A note below it covers `tile_config.get_fabric_coord`/`fabric_coord_mask` and says 11 bits allow a dimension above 1,023.
- **X3 Fixed.** The control-wavelets section now explains what a fabric DSD is in one line, with links to #ce-half and Ch 6 #fabric-dsds. The #ce-half code pairing also covers the @fmovs relay mention.
- **X4 Fixed.** The latency calculator has a new "op start-up ≈ 17" checkbox, on by default [Measured, Ch 6 #op-speed]. The bar has a new start-up segment, and the hint explains when to leave the term on.
- **X5 Fixed.** New figure #chk2d-fig: a 4×4 grid with E c0/c1, W c2/c3, S c4/c5 and N c6/c7. The outlined interior PE uses all 8 colors. The caption explains the parity rule and that the count of 8 matches game-of-life.
- **X6 Fixed.** New 3-panel teardown figure: phase-1 route, then TEARDOWN arrives (pending bit set, task 29 runs), then the handler calls `@set_local_color_config` + `teardown.exit(c)`. The claim that the color is held between panels 2 and 3 is tagged Unverified.

## Connecting gaps
- **G1 Fixed.** New #ce-half block in #routes puts the layout route (router half) and the program-03 `fabout_dsd`/`fabin_dsd`/`@initialize_queue`/`@fadds` lines (CE half) side by side. It notes the WSE-2/WSE-3 differences and links Ch 6 and Ch 5.
- **G2 Fixed.** New #many-to-one paragraph lists three ways to merge: (a) a CE chain (~9 cycles/PE), (b) one color per source, (c) switches or teardown over time. It links Ch 12, 13, 14 #collectives and 15 #allreduce.
- **G3 Fixed (measured).** New #multicast-stall paragraph: a multicast waits for its slowest branch. Measured on WSE-3 with M=64: the middle PE was busy ~1,050 cycles, and the bottom PE finished at 1,136 instead of 96 (root send 1,119 instead of 82). With M=8 the bottom PE still finished at 1,080. WSE-2 behaves the same (2,154). The multicast bullet links back to this paragraph. I did not claim anything about memcpy's row fan, which I did not test.
- **G4 Fixed.** The page now has 75 links: every specific "Chapter N"/"Lab N" mention, Appendix C #tsc, and first uses of fabric, router, wavelet, ramp, CE, color, virtual channel, back-pressure, route, set_color_config, multicast, corner turn, hop, TSC, checkerboard, color swap, control wavelet, control task, switch positions, filter, teardown, collectives_2d, memcpy, SdkLayout and initialize_queue.
- **G5 Fixed.** The #ce-hop paragraph includes a worked sum: router hop 2 + ramps ≈ 2 + 2 + CE queue→add→queue ≈ 3 ≈ 9 [Derived; only the total is measured]. It ties this to "keep traffic in the router". #relay now quotes 9/6 versus 2/1.
- **G6 Fixed.** New collapsible #try-hops box holds the full layout.csl and pe_program.csl (rebuilt and re-run this round), the core of run.py, and the commands. It lists the rerun results [Measured].
- **G7 Fixed.** New #try-switches box runs topic-06 and topic-08 with `commands_wse3.sh` and gives their outputs (rerun) mapped to the trace table and filter slices. It flags topic-14, histogram-torus and 25-pt-stencil as WSE-2-only in SDK 2.10.1. #relay also marks histogram-torus as WSE-2 only.
- **G8 Skipped (other page).** This is Ch 3's text; see below.

## Coordinator items 30–38
- **33 / r3 G12 Fixed.** The WSE-3 clock row now reads "not published; ~1.4 GHz estimated" [Analyst][Unverified]. The note mentions WSE-3T at ~2.8 GHz and links Ch 2 #generations.
- **34 Fixed.** The lede and #mesh now qualify "one hop per cycle" as a hardware-paper figure and say the WSE-3 simulator models 2. The ~7 figure is replaced (E1).
- **35 Fixed.** The back-pressure hint no longer says depths are "not published". It gives the memcpy.csl input-queue depths 6/4/2 [SDK], says router buffer depths are unpublished, and links Ch 12 #late-pe for the ~16 per hop.
- **38 Fixed** (G4).
- 30, 31, 32, 36, 37: not applicable to this page.

## Cross-page items about Ch 4 from other r4 reports
- **r4-ch07 X1 (counter-filter wording) Fixed here.** The text now says the counter "counts up from its start value to limit and back to 0, passes when it reads 0". It links Ch 7 #copy-path.
- **r4-ch06 G4** (back-pressure → fabric DSD ops): the Ch 4 back-pressure paragraph now links Ch 6 #fabric-dsds. The bridge itself belongs on Ch 6.

## For other pages
- **Ch 3 (#wavelets), r4-ch04 G8 / r4-ch03 E3:** change "hop one router per cycle" to "about one cycle per hop on hardware, per papers; the WSE-3 simulator models 2 (Ch 4 #latency)".
- **Ch 12 #broadcast:** can link `04-fabric.html#multicast-stall`. The broadcast runs at the pace of its slowest receiver (measured, see G3).
- **Ch 7 / Ch 11 (r4-ch07 G5, r4-ch11 G7):** for memcpy's RAMP→RAMP route, link `04-fabric.html#ce-half` (router half / CE half) and `#routes`.
- **Ch 2, Ch 12, Ch 17:** new Ch 4 anchors available: `#ce-hop` (9.2/6.0 vs 2.0/1.0), `#try-hops`, `#many-to-one`, `#chk2d-fig`, `#try-switches`.
