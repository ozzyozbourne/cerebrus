# Review 2: Appendix C (Measuring and observing), visuals + pedagogy

Page: `course/appendix-c-measuring.html`. Rendered in Playwright (Chromium) at 1100 and 390 px, light and dark, with the ◐ toggle; every flow chip and SVG question box, the noise checkbox, and all 12 trace-line fields were clicked. **Zero page or console errors, no page-level horizontal overflow**, and the theme toggle restyles all three widgets live. Screenshots: `/home/user/cerebras-sdk/tmp/r2appC/`.

## Pedagogy (P)

**P1 (high). The page says Lab 3 uses `cycle_count` differencing, but Lab 3 does the opposite.**
Locations: the "Three instruments" table, row 1, "Use it for" ("Lab 3's slope method"); §1, paragraph after the noise widget ("Lab 3 times a timestep by running 100 and 200 steps and dividing the difference by 100, which cancels the fixed I/O (Chapter 13)"); the flow recipe `R[0]` ("Lab 3: 200 steps minus 100 steps"); and quiz Q1's answer ("compare differences between two problem sizes").
Evidence: `13-lab-stencil.html` l.374–393 takes the slope of the **TSC** between **10 and 100** steps. Its callout "Why not difference the simulator's total cycles?" (l.384) says that differencing `cycle_count` is noisy: the same build gave 5,260 vs 8,905 cycles. So this appendix teaches the method the lab warns against, and it cites the wrong step counts.
Fix: give row 1 "end-to-end cost of a host program" only. Rewrite the §1 sentence: "For a per-step cost, take the slope of the **TSC** between two step counts (Lab 3: 10 and 100 steps, [Chapter 13](13-lab-stencil.html#tsc)). Differencing `cycle_count` inherits its noise ([Ch 13 callout])." Move the slope idea into `R[1]` (TSC) and remove it from `R[0]`. Change Q1's answer to "difference two TSC readings, or run the two versions alone and accept a few percent of noise."

**P2 (med). The page repeats the trace tutorial in Chapter 11 and never says so.**
`11-lab-first-programs.html#trace` ("Look inside: the instruction trace") already introduces `SIMFABRIC_DEBUG=inst_trace` and `trace_tasks.py` (l.304–322). A learner who reaches §3 here is not told that they have seen this before, or where.
Fix: in §3's first paragraph, add "First met in [Chapter 11, 'Look inside'](11-lab-first-programs.html#trace); this section is the reference."

**P3 (med). Cross-references point at internal notes, or at whole chapters when the target section has an anchor.**
- "cross-chapter note 19", "notes 22–23" and "notes 7, 21" (same-PE callout, worked example, pitfall 9) refer to `reviews/CROSS_CHAPTER_NOTES.md`. That is a reviewer file the learner never sees.
- These anchors exist but are not used: `10-csl-toolchain.html#sim-outputs`, `11-lab-first-programs.html#kernel-time`, `12-lab-neighbours.html#hop-cost`, `06-dsds.html#collisions`.
- "Chapter 13", "Chapter 12" (in §1), "Chapter 18" and "Chapter 11's streaming race" have no links at all.

Fix: replace each "note N" with a link to the chapter section that states it (note 19 → `13-lab-stencil.html#tsc` or `12-lab-neighbours.html#hop-cost`; notes 22–23 → `06-dsds.html#collisions`; notes 7 and 21 → `10-csl-toolchain.html#sim-outputs`). Add the `#anchors` above.

**P4 (med). The most useful visual is missing: how the three instruments nest.**
The core idea of the page is that the three instruments measure nested spans. Today the reader has to assemble that from four separate numbers. The page already has every value: the whole run (~21,700 cycles), the RPC run T01 @3353–4113 (761 cycles), the TSC window @3619–3890 (271), and the FMACS @3630–3885 (256).
Fix: add a horizontal timeline figure for the WSE-3 PAD 1 run, with a zoom inset on the RPC. Show three nested brackets labelled `cycle_count` / `trace_tasks` run / TSC / FMACS. That figure also answers pitfall 1 and the "15 cycles of overhead" question at a glance.

**P5 (low). `PAD` and the `commands.sh` arguments are undefined here.**
The noise widget hint says "PAD 1", the table has a PAD column, and the worked example says `bash commands.sh 256 0 PAD`. None of these says that PAD is the padding words between x and y, or that the middle argument is HALF.
Fix: add one clause at first use: "PAD = padding words between x and y (`commands.sh N HALF PAD`, Ch 11)".

**P6 (low). The quiz has three items and none tests trace reading or stamp decoding,** although both are stated objectives.
Fix: add one item. Example: "A stamp's words arrive as [0x0114, 0, 0, …] in a u32 buffer viewed as u16. What went wrong?" Or: "Given two FMACS lines @3630 Seq 0 and @3632 Seq 1, what is the rate?"

**P7 (low). Terms are not linked to the glossary.**
TSC, RPC, H2D/D2H, DSD and "fabric coordinates" are used without definition. That is fine for an appendix, but Appendix B links Appendix A and this page does not.
Fix: add "Terms: [Appendix A](appendix-a-glossary.html)" to the lede.

## Visuals (V)

**V1 (med). Flow chart on phones: the answer column is off-screen.**
At 390 px the 760-wide SVG scrolls inside its box (the global min-width rule). The visible part shows the question boxes cut at the right edge, and the method boxes cannot be seen without scrolling sideways (screenshot `flow-390-light.png`). The chips above already give the full interaction, so on a phone the SVG is about 330 px of dead, clipped space.
Fix: hide `#flow-svg` at ≤680 px and rely on the chips and the readout. Alternative: lay the chart out vertically (questions above methods).

**V2 (med). Flow chart: text overflows a question box.**
"How long does a multi-PE phase or hop take?" runs 16.6 px past its 262-px rect. The overflow was measured with getBBox, and the screenshot `flow-q2.png` shows "take?" crossing the border.
Fix: shorten it to "How long does a multi-PE phase take?" (hops are covered by the recipe), or set `qw` to 284 and move `mx` right.

**V3 (med). Noise widget: points collide and the baseline is the outlier.**
- Runs 2 and 3 (21,773 and 21,755) draw as one blob.
- The five TSC dots stack into a single dot, so "five runs" cannot be seen in that row.
- Labels exist only as `<title>` hover tooltips, which do not work on touch.
- The baseline is run 1 (22,844), the high value among the untraced runs, so every other run reads "−5 %". That suggests the runs got faster.
- The axis floor of −8 % is an arbitrary pad, shown with no data near it.

Fix: plot absolute `cycle_count` on the x-axis, or use the median as the baseline. Jitter dots vertically, or label each with its run number. Annotate the TSC row "5 runs, all 271". Show only data-driven ticks.

**V4 (low). Kernel share disagrees inside the page.**
The widget readout says "1.3 % of the smallest total" (271/21,631). The table and pitfall 1 say 1.2 % (271/22,844).
Fix: state the denominator in both places, or use one figure ("1.2–1.3 %").

**V5 (low). `<mark>` on 527 and 526 uses the browser's default yellow (#ff0) with black text,** which glares in dark mode (`num-dark.png`). The highlight is also never explained.
Fix: add `mark{background:var(--accent-soft);color:var(--text)}` and the caption "highlighted: unpadded layout, operand collision".

**V6 (low). The phone tables are hard to read.**
At 390 px, the "Three instruments" table puts its long text in narrow columns. Rows grow to about 350 px tall and most columns are off to the right. In the worked-example table, "WSE-3" breaks as "WSE-/3" and the "kernel share" column is hidden.
Fix: give the first column `white-space:nowrap`. Stack the instruments table as cards, as Appendix D's table does, or set `min-width` on the text columns.

**V7 (low). Trace excerpt alignment.**
The lines @3630, @3631 and @3885 keep extra spaces after `Seq: 0,`, while the other lines were collapsed, so the columns jump. The `.hl` background (`inline-block; width:100%`) also covers only the visible width when the `<pre>` scrolls on a phone.
Fix: normalise the spacing, and use `display:block` or `min-width:max-content` on `.hl`.

**V8 (low). Flow chart details.**
- When a question is selected, the root box "What do I want to know?" fades to 45 % opacity even though its edge is lit. Fix: exempt `.root`.
- `#flow-svg` has `role="img"`, which hides its focusable `role="button"` children from assistive tech. Fix: use `role="group"`.

**V9 (low). The trace-line widget shows `Id: 12, Instr: 1255,` and `Pipe: 6,`, but the excerpt below says these fields were removed.** That is consistent but easy to misread.
Fix: add to the widget hint: "the excerpt below drops the Id/Instr/Pipe fields".

## What works
- The trace-line widget is excellent. The hex operands decode correctly (0xbf2aed8e = −0.6677, 0x3e00bf6c = 0.1257, 0xbeb4ebd5 = −0.3534, 0x40200000 = 2.5), and the arithmetic checks out.
- The annotated trace excerpt, with the TSC read in context, is the best teaching moment on the page.
- All three widgets follow the ◐ toggle with no stale colours.

## Counts
High 1 (P1) · Med 6 (P2, P3, P4, V1, V2, V3) · Low 9 (P5, P6, P7, V4–V9).
