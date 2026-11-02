# Round 2 review: Ch9 "From model to tokens", visuals angle

Method: Playwright (Chromium) at 1100 and 390 px, emulated light and dark, plus the ◐ toggle from light to dark. Every
widget control was driven, including extremes: all 6 kp sliders, both modes, every button; pd at 1/2/4/10/20 users
with 25–45 steps; cap with every preset, the params slider at its minimum, 4-bit, 128K context and 64 users; lb with
both presets and every slider and select at min and max; sd at α/k/c/S extremes, with an empty and a negative base.
Screenshots: `/home/user/cerebras-sdk/tmp/r2ch09v/`. Result: 0 page or console errors in every configuration, and
no page-level horizontal overflow (scrollWidth = viewport). At 390 px, only `pre.formula` code and the SVGs scroll
inside their own boxes. The theme toggle re-colours every drawing live. Dark-mode contrast is fine everywhere.

## Findings

**V1 — high — `#kp` placement toy, "memory (pinned inference)" mode is always ILLEGAL in graph order**
- What is wrong: clicking "memory (pinned inference)" runs `balance()` and immediately draws "L6 head: no room" under
  the fabric. The readout says "ILLEGAL: kernels overflow the fabric. Narrow some kernels (or balance)". The same
  readout also says "cores used 1152 of 1152 (100%)", a legal-looking Δt of 133, and "relative throughput 0.75".
  Following the advice cannot fix it.
- Evidence (screenshot `d-kp-mem.png`): the minimum widths in that mode are ceil(memKB/48/12) = 4, 22, 12, 20, 18 and
  14 columns, which sum to 90 of 96. Packed in graph order, shelf 1 takes at most L1–L3 (38 columns). That leaves
  L4–L6 = 52 columns for a 48-column shelf. No slider setting is legal; only some shuffled orders fit. The prose
  promises that "minimum widths then use most of the wafer, and little freedom is left to balance". The widget
  shows a broken placement instead, which is the opposite lesson.
- Fix:
  - Lower one memory figure so the graph order fits. For example, set L6's memory-mode figure to 5,760 KB, which
    gives 10 columns, so L4–L6 = 48 columns. Check that both shelves are ≤ 48 at the minimum widths.
  - Better: make `balance()` packing-aware. Try the trim loop until no `pos[i].ill` remains.
  - When the placement is illegal, compute "cores used" only from the kernels that were placed, and replace Δt and
    throughput with "—".

**V2 — med — `#kp`, an illegal compute-mode layout still reports a full throughput score**
- What is wrong: with L1 = L2 = 40 columns the readout says "ILLEGAL … cores used 1728 of 1152 (150%) … relative
  throughput 1.00". That is the best possible score, given to a layout that does not exist.
- Fix: the same as the last part of V1. While illegal, suppress or strike out the Δt and throughput lines.

**V3 — med — `#lb` presets are path-dependent and do not reset Context**
- What is wrong: `presets.a` and `presets.b` set clk, rate, nc, hops, cph, wh and e, but not `ctx`. After changing
  Context, "B" shows as pressed but gives 414 µs instead of the 418 µs the prose describes. Pressed preset buttons
  are cleared on any input, but the preset itself never restores 8K.
- Fix: add `ctx: "8192"` to both presets.

**V4 — low — `#lb` output disagrees with the text right after it**
- What is wrong: the prose says what-if B "lands at ~420 µs per token, in the range of the measured 2,100–2,314
  tok/s". The widget says 418 µs ≈ 2,391 tok/s. Its "per output token" bar ends left of both the 2,314 line
  (432 µs) and the 2,100 line (476 µs), so it is faster than either published speed, not inside that range.
- Fix: reword to "~420 µs (~2,400 tok/s), just above the published 2,100–2,314 tok/s".

**V5 — low — `#lb` labels collide with the published-speed lines**
- What is wrong: at the default state, the "418 µs" end label sits on the dashed 2,314 and 2,100 lines. These lines
  run from y = 22 to 126 across both bars. At extreme settings the "8053 µs" label is drawn end-anchored on top of
  the attention segment.
- Fix: end the dashed lines above the bars (y2 ≈ 28), or draw them only in a thin strip above the bars with a tick
  at the axis. Alternatively, move the value labels to the right of x1 in a fixed column.

**V6 — low — `#kp` dashed wires run through the kernel labels**
- What is wrong: the L1→L6 wires are drawn at each rectangle's vertical centre, which is exactly where the name and
  Δt text sit. The dashes strike through "L1 conv / Δt 50" and the other labels (`1100-light-kp.png`). The halo
  softens this but does not stop it.
- Fix: route the wires at `r + SH*0.75`, or move the text to the top third of each rectangle.

**V7 — low — `#kp` slider grid is cramped at 1100 px**
- What is wrong: with `.kgrid` at `minmax(230px, 1fr)`, each label wraps to two lines at 1100 px ("L1 / conv" and
  "16 col · 192 / cores"), which looks broken. At 390 px it is actually on one line.
- Fix: use `minmax(300px, 1fr)` or `white-space: nowrap` on the name and value spans. Alternatively shorten the
  value to "16 col".

**V8 — low — `#kp` at 390 px hides the Δt side panel**
- What is wrong: the min-width 620 rule scrolls the SVG, so on a phone the bar panel that says "← slowest" is off
  screen. The point of the widget is invisible until the reader scrolls sideways.
- Fix (optional per the brief): at narrow widths, draw the Δt bars below the fabric (viewBox 760 → 560 wide, panel
  under it). Alternatively, make sure the readout's "bottleneck Lx" line is visible.

**V9 — low — `#cap` presets show plausible but misleading layer counts for MoE models**
- What is wrong: the 120B preset (gpt-oss-120B, the model the page discusses, which has about 36 layers) is drawn
  with 94 interpolated layers. The 1T preset (Kimi-like) gets 150 extrapolated layers and Llama-3 GQA KV of
  0.61 MB/token. Kimi uses MLA, which makes its KV much smaller. With 64 users × 128K at 4-bit, the device chart
  becomes a wall of purple: 5,154 GB of KV against 500 GB of weights. The ÷150 per-user bound also uses an invented
  layer count. The hint does say "illustrative", but the presets carry real model names and sizes.
- Fix: label the 120B and 1T presets "dense, Llama-3 shapes", or cap the interpolation at 405B. Alternatively, add
  per-preset layer counts with a note that the MoE presets are treated as dense.

**V10 — low — `#sd` accepts an empty or negative base silently**
- What is wrong: clearing "Speed without speculation" or typing −50 gives "→ 1 tok/s" for both GPU and wafer, with
  no warning.
- Fix: clamp to the input's min (10) and write the clamped value back into the box.

**V11 — low — `#sd` curves hide each other at S = 1, c = 0**
- What is wrong: at S = 1 and c = 0, the wafer curve and the slot-share curve coincide (both are E/(k+1)), so the
  orange line hides behind the dashed one. This is not wrong, but it is confusing.
- Fix: draw the slot-share curve last with a thinner stroke, or add a note to the readout when they coincide.

## Checked and fine
- `#cp` compile figure: no overlaps, legible in both themes and at 390 px.
- `#pd`:
  - 20 users fill all 80 Gantt cells.
  - With 1 user the single dot circulates, and the readout's "tokens generated" increments every 20 steps.
  - Its numbers agree with the text.
- `#cap`:
  - 70B: 4 WSE-3, 7,359 tok/s headline ÷ 80, 2,011 at the kernel rate. This matches the prose ("~7,500" and
    "~2,000") and the "589k" pipe-full total (prose says "≈600,000").
  - 405B: 19 wafers, and 20 with 10 users. This matches the quiz.
- `#lb`:
  - Preset A: 20,888 cycles per layer and 1,986 µs, which matches "~15,600 cycles of collectives" and "about 2 ms".
  - At 128K, attention is 1,591 cycles per layer, which matches "~1,500".
- `#sd` defaults: E = 3.36, which matches the formula block.

## Missing visuals that would help most
1. **Speculative verification in the pipeline.** A small Gantt-style figure with the k + 1 positions entering one
   stage apart, so a reader can see that "+k/S of a trip" and "k + 1 slots used" are both true. It could reuse the
   pd drawing with a "speculate k" option.
2. **Speed history as a chart.** Plot tok/s against date, coloured by model or with a symbol per model, and annotate
   the 450 → 2,100 jump. Today it is a dense ten-row table. Its lesson, that every row is a different model, would
   show at a glance.
3. **Sparsity break-even.** A one-line bar or plot of bytes per weight against sparsity, dense 2 B versus sparse
   4 B × (1 − s), crossing at 50%. It is cheap to add and makes the claim concrete.
