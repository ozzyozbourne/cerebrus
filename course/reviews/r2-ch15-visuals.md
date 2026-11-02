# Review round 2: Chapter 15 (Lab 5, CG): visuals

Page: `course/15-lab-cg.html` (generated from `course/src/15-lab-cg.html`; all fixes go in the src template).
Method: Playwright/Chromium at 1100 px and 390 px, light and dark (`colorScheme`), plus the ◐ toggle at 1100 px. I tried every
experiment in the budget widget on both chips, hovered the legend buttons, tried every chip/view pair in the iteration widget,
every cost-model preset and both slider extremes, and took a screenshot of each figure. Screenshots: `/home/user/cerebras-sdk/tmp/r2-ch15-vis/`.

Clean: there were no page or console errors in any of the four configurations or after the toggle. All SVGs follow the theme live. The page does
not scroll sideways at 390 px. Wide figures and widgets scroll inside their boxes, as the shared fix intends. Halo text on the convergence labels
reads well in both themes.

## Findings

**V1 · med · "The allreduce every iteration waits on": the hardest mechanism in the lab has no picture.**
The three-stage allreduce is described only in prose: row reduce with switch-advance control wavelets, then column reduce on the last column, then a multicast broadcast, with teardown and `reset_routes` between stages. It is the lab's second objective, and the scaling argument depends on it ("cost is per value, not per hop"). A learner has to picture router switch positions and the order of wavelet arrivals from text alone.
Fix: add a small 5 × 5 figure or a three-step stepper. Show the stage 1 routes (W→E, last PE delivers to CE), one PE's switch flipping from position 0 to position 1 after its control wavelet, values arriving one at a time at the row end, then stage 2 down the last column and stage 3 as the multicast fan-out. Mark the teardown at each stage boundary. Reuse the Lab 2 route styling.

**V2 · med · Resource-budget widget, "none: the shipped assignment": the text disagrees with the drawing and the code.**
The output reads "no slot is claimed twice, except that on WSE-2 the stencil and the allreduce never send at the same time". The shipped WSE-2 assignment does not share anything: `pe_program.csl:31,38` gives the allreduce queue 2 and the stencil output queue 3, and the drawing shows them separately. The "except" makes a reader hunt for a clash that is not there. It describes the `queue2` experiment instead.
Fix: "The shipped assignment: no slot is claimed twice on either chip. (Pick the WSE-2 queue experiment to see a slot that can be shared safely.)"

**V3 · med · `#z-tab` (column-length table) is clipped at 390 px.**
The table is 383 px wide at x = 17, so its right edge is at 400 px. The axpy column ("35…", "44…", "51…", "89…") is cut off, and nothing scrolls to reveal it (screenshot `z390.png`). The grid table and the other tables fit.
Fix: wrap both scaling tables in a `<div style="overflow-x:auto">`. Alternatively, shorten the header "Z (cells per PE)" to "Z" and explain it in the lead-in sentence.

**V4 · med · Cost-model widget: the bar is always 100% wide, so the scaling the section argues for is invisible.**
Dragging W/H from 5 to 951 changes only the proportions. The bar never gets longer, so "the allreduce grows with the side" shows only as a percentage, and the per-solve growth (iterations × per-iteration cost, the box "The scaling law of this solver") appears only in the text output.
Fix: draw the bar on a fixed scale. A log axis of cycles per iteration from about 3k to 300k works, or a 5 × 5 reference bar drawn beside the current one. Optionally add a second bar or tick for solve time.

**V5 · low-med · Budget widget on phones: the parts that matter are off-screen.**
At 390 px the 700-unit SVG gets 356 px of a min-620 px scroller. The colors row is cut at 9, and the local task IDs row shows only 0–8. Every task-ID claim (12, 14–20) and memcpy's color 22 sit beyond the fold, and nothing hints that the box scrolls. The same applies to the iteration and cost widgets, where the allreduce segment is off-screen by default.
Fix: under 680 px, draw the 24-slot rows as two lines of 12 (the widget redraws anyway), or add a "scroll →" hint to the widgets.

**V6 · low · Budget widget, "allreduce queue 2 → 4 (WSE-3)": the allreduce's output-queue claim disappears.**
The code clears both `S.in[2]` and `S.out[2]` but re-adds the allreduce only to input queue 4. In the drawing the allreduce no longer owns any output queue, but in the real experiment it would claim output queue 4 too, a second clash with the stencil.
Fix: in `draw()`, for `queue` also run `S.out[4] = S.out[4].concat(["allreduce"])`.

**V7 · low · Budget widget is missing DSRs and memcpy's other colors.**
The `layout.csl` ledger lists explicit DSRs (stencil 2,3/2/2,3; allreduce 1/1/1), the module graph's `pe_program.csl` box says "queues, UTs, DSRs", and objective 2 says "give each its … DSRs, and check the budget". The widget has no DSR row. memcpy is also drawn on color 22 only, while the text says 21–30 are reserved for it.
Fix: add a DSR row (dest/src0/src1 grouped), and draw 21 and 23–30 with a hatched "reserved for memcpy" style so 22 stays the one known use.

**V8 · low · Cost-model labels overflow their segments.**
With the "≈ whole wafer" preset, the label "stencil SpMV 13%" is 110 px wide in a 93 px segment. It starts at x = 4, left of the bar (x = 10), and runs into the next segment, rendering as "stencil SpMV 13" with clipped glyphs. The rule `wd > 60` is too permissive.
Fix: measure the label with `getBBox()` and drop the name if it does not fit, keeping just "13%".

**V9 · low · Cost model does not reproduce its own anchor.**
The default 5 × 5 × 5 view prints 4,586 cycles per iteration against the measured 4,574 in the stat row. The model uses axpy 341 and control 316, but the text says it uses "the measured value at that Z" (measured: 352 and 295). The preset "≈ whole wafer" shows 951 × 951, not 950 × 950, because the log slider quantizes values.
Fix: use the measured 5 × 5 phase values at Z = 5 so the default matches 4,574. Let the preset set w/h directly and display those numbers rather than `toV(fromV(950))`.

**V10 · low · Iteration widget, "real system" view.**
(a) The device bar is 2 px wide, so it is invisible next to 1,005 µs. Add a callout or a ×200 annotation, or use a log axis.
(b) The host bar is coloured `acc` (the allreduce colour in the simulated view) and the device bar `grn` (stencil), which reuses legend colours for a different meaning. Use neutral or `--muted` plus `--accent`.
(c) The host bar's on-device part uses `noprof` (device-loop 4,261 cyc). The host loop's own PROFILE=0 figure, 5,488 cyc (6.5 µs), would be the consistent choice. The total barely changes.
(d) In the simulated view the bars are scaled by the sum of the phases (5,806), but the end label shows the total (5,798). The difference is invisible; normalise the phases to the total or ignore it.

**V11 · low · Convergence figure.**
The figure has no y-axis title (|r_k|/|b|) and no line marking the 1e-5 stopping threshold that all three curves end at. Solid versus dashed is explained only in the caption. The label "12³: 34 it." sits on the green dashed 8³ bound line.
Fix: add a dotted horizontal line at 1e-5 labelled "EPS", a short in-plot legend ("— measured, - - bound"), and a y-axis title.

**V12 · low · Pencil figure.**
The left panel is a top view only, so the "z-column" (the pencil itself) never appears. In the memory panel, p and w are green and b, x and r are grey without explanation.
Fix: add a small oblique 3-D box with one highlighted column. Say in the caption that green marks the vectors the SpMV reads and writes, p sent to neighbours and w = A p.

**V13 · low · Module graph omits memcpy's layout half.**
`layout.csl` imports `<memcpy/get_params>` (layout.csl line 40) and passes `memcpyParams`, but the compile-time row shows only the stencil and allreduce layout halves.
Fix: add a small blue `<memcpy/get_params>` box beside them with a dashed arrow to `pe_program.csl`.

**V14 · low · Missing visual for the grid-scaling claim.**
The allreduce fit (958 + 100·W + 88·H, within 30 cycles over 7 grids) is shown only as a table. A small scatter of measured allreduce cycles against W + H, or against the fit, with the plane drawn as a line would make "linear in the side, serial" visible at a glance. Add it next to `#grid-tab`, optionally with the WSE-2 points.
