# ch01 · visuals review

Summary: I rendered the chapter with Playwright at 1100 px and 390 px, in light and dark, and drove every control of the roofline widget: each chip at intensity 10^-1 and 10^4, each preset, keyboard input, and the theme toggle. The console showed no errors, the page never scrolls sideways, and the widget redraws correctly when the theme changes. The main defect is on phones. All three SVGs shrink to 0.45–0.51 of their viewBox width, so 10–13 px labels render at about 5–6 px and cannot be read. The roofline has no legend for its four lines. One preset value is wrong, and the preset menu falls out of step with the slider. Some labels collide or use raw `e+3` notation. The two static figures are tidy at desktop width and correct in dark mode, but they carry pedagogy and labelling problems (package edge, missing bandwidths, read once versus used once). The chapter's two central quantitative ideas, tokens/s from bandwidth and the capacity-vs-bandwidth trade-off, are explained only in prose. Both would gain the most from a new visual.

## Findings (defects in existing visuals)

### V1 [critical] All three SVGs are unreadable at phone width
- **Location:** `#roof-svg` (viewBox 640×330), the decode/prefill figure (720×230), and the "Three answers" figure (760×300). All three have a fixed `width` and rely on `img, svg { max-width:100% }`.
- **Problem:** At 390 px the content box is about 340 px, so each SVG scales uniformly. The measured scales are 0.51, 0.47 and 0.45. The 10–11 px muted labels ("~512 KB/SM", "80 GB · 3.35 TB/s", "1 cycle", "package edge", tick labels) render at about 4.5–5.5 px, and the 13–14 px body labels at about 6 px.
- **Evidence:** The `390-*-fig*.png` screenshots showed tick labels, the ridge label, the axis titles and every sub-label as illegible smudges. The roofline plot area is only 324×167 px.
- **Concrete fix:**
  1. **Roofline:** size the chart from the real width instead of a fixed viewBox. In `draw()`, set `const W = Math.max(320, svg.clientWidth || 640), H = W < 500 ? 260 : 330;` and `svg.setAttribute("viewBox", `0 0 ${W} ${H}`)`. Drop the `width="640"` attribute and give the SVG `width:100%`. Add a `ResizeObserver(draw).observe(svg)`. On narrow widths, label only every other decade on the y-axis (`1G, 100G, 10T, 1P, 100P`) and set `L = 44`.
  2. **Static figures:** give each one a stacked portrait variant and switch between them in CSS: `<svg class="fig-wide" …>` plus `<svg class="fig-narrow" viewBox="0 0 360 …">`, with `@media (max-width:680px){ .fig-wide{display:none} } @media (min-width:681px){ .fig-narrow{display:none} }`.
     - Decode/prefill: put decode above prefill, viewBox about 360×420.
     - Three answers: one row per architecture, with the right-hand comment moved below its row, viewBox about 360×520.
  3. **Cheapest fallback:** add a `figure.scroll` class with `overflow-x:auto` and `figure.scroll svg{min-width:640px}`, plus a "scroll →" hint. This keeps the text at its real size.

### V2 [major] Roofline lines have no legend or direct labels
- **Location:** `#roof-svg`, the polylines drawn in `chips.forEach`.
- **Problem:** Four coloured roofs are drawn, but only the colour of the active one is explained, and only indirectly through the dropdown. A reader cannot tell which faint line is the B200 or the WSE-3. Comparing chips is the main reason to draw all four lines.
- **Evidence:** In the 1100-light screenshot the orange, purple and green lines carry no text.
- **Concrete fix:** add a direct label at the right end of each roof, drawn in that chip's colour:
  ```js
  el("text",{x:W-R-4, y:Y(Math.log10(peak))-5, "text-anchor":"end","font-size":11, fill:cssVar(colors[i]), opacity: active?1:.8}, svg).textContent = ["H100","B200 (FP4)","Blackhole","WSE-3 SRAM"][i];
  ```
  The WSE-3 and B200 ceilings are only about 0.24 decades apart, so offset one label below its line. Also make each polyline clickable: `onclick = () => { sel.value = i; draw(); }`, with `style="cursor:pointer"` and a wider transparent hit stroke.

### V3 [major] "Vector add" preset is wrong (0.25 FLOP/B)
- **Location:** `<option value="-0.6">Vector add (0.25 FLOP/B f32)</option>`.
- **Problem:** `c = a + b` in f32 does 1 FLOP per 12 bytes moved (8 read, 4 written), which is 0.083 FLOP/B. Counting reads only gives 0.125 FLOP/B. Neither is 0.25. The accuracy review (A1) and the pedagogy review (P5) report the same error. Here it also misplaces the dot.
- **Evidence:** Choosing the preset sets the slider to 10^-0.6 = 0.251 FLOP/B.
- **Concrete fix:** use `<option value="-1.08">Vector add, f32 (1 FLOP / 12 B ≈ 0.083)</option>`. The slider's `min="-1"` must become `min="-1.5"`, and `xmin` must become `-1.5` (or `-2`) so the point stays on the chart. Update the tick loop to start at `Math.ceil(xmin)`.

### V4 [major] Preset menu goes out of step with the slider, and a preset cannot be re-selected
- **Location:** `#roof-preset` and its `onchange` handler. `ai.oninput` never touches the preset menu.
- **Problem:** After the slider moves, the menu still shows the old preset label, for example "LLM decode, batch 1 (~1 FLOP/B)" while the slider reads 1.00e+3. Choosing that same option again fires no `change` event, so the reader cannot snap back to it.
- **Evidence:** I set the slider to 3. The preset text stayed "LLM decode, batch 1 (~1 FLOP/B)" and the value label read "1.00e+3 FLOP/B".
- **Concrete fix:** add `<option value="" selected>Custom…</option>` as the first option. In the slider handler, add `ai.oninput = () => { const m=[...$("#roof-preset").options].find(o=>o.value!=="" && Math.abs(o.value-ai.value)<0.005); $("#roof-preset").value = m? m.value : ""; draw(); };`. In the preset handler, ignore the empty value. A cleaner alternative is to replace the `<select>` with a row of buttons (`.btn` chips). Buttons always fire, show all four presets at once, and let you mark the active one with `aria-pressed`.

### V5 [major] Red intensity dot is lost on the WSE-3 roof
- **Location:** the `circle` with `fill: cssVar("--red")`, drawn on the active line in `--accent` when the WSE-3 is selected.
- **Problem:** Accent and red are nearly the same hue. Their contrast is 1.25:1 in light mode (#c2410c vs #b91c1c) and 1.22:1 in dark mode. When the WSE-3 is selected, the "you are here" dot merges into its line, and that line is the one the comparison trap is about.
- **Evidence:** In `drive-chip3.png` the dot at 10^4 is hard to tell apart from the thick orange roof.
- **Concrete fix:** draw the marker as a hollow ring that contrasts with every series: `fill: cssVar("--surface"), stroke: cssVar("--text"), "stroke-width": 2.5, r: 6`. Draw the guide line in `--text` at opacity .5 instead of `--red`. Alternatively, give the WSE-3 series `--amber` and keep the red marker.

### V6 [minor] Ridge labels collide with other roofs and hit the plot edge
- **Location:** the ridge label `text` at `X(ridge)+6, Y(peak)-6`.
- **Problem:** The Blackhole label "ridge 1297 FLOP/B" sits on top of the H100 roof at 1 PFLOP/s. Its bounding box runs from x 527 to 623, past the plot's right edge at 620. The B200 label ends at 614, right against the edge.
- **Evidence:** `drive-chip2.png` shows the H100 blue line running through the label text. The measured getBBox is `[526.6, 622.7]`.
- **Concrete fix:** when `X(ridge) > W-R-110`, anchor the label to the left of the point: `"text-anchor":"end", x: X(ridge)-6`. Place it below the roof (`y: Y(peak)+14`) whenever another roof's y lies within 12 px. Also give the label a halo: `paint-order:stroke; stroke: var(--surface); stroke-width:3px`.

### V7 [minor] Raw exponent notation and lost precision in labels
- **Location:** `$("#roof-ai-v").textContent = Math.pow(10,a).toPrecision(3)`, the `toPrecision(3)` call in the readout, `fmt()`, and the tick labels `"10^" + x`.
- **Problem:**
  - The value label shows "1.00e+3 FLOP/B" and "1.00e+4 FLOP/B".
  - The readout says "ridge point: 1.13e+3 FLOP/byte", while the chart label for the same chip says "ridge 1125 FLOP/B".
  - `fmt()` rounds 15.6 PFLOP/s to "16 PFLOP/s" and 51.2 GFLOP/s to "51 GFLOP/s".
  - The x ticks read "10^-1", "10^0" as literal text.
- **Evidence:** These strings came from the driver output for chips 1, 2 and 3 at 10^4.
- **Concrete fix:**
  - Add a helper: `const nice = v => v >= 100 ? Math.round(v).toLocaleString("en") : v.toPrecision(3);`. Use it for both the value label and the ridge readout.
  - In `fmt`, use `toPrecision(3)` instead of `toFixed(...)`.
  - Label the x ticks `["0.1","1","10","100","1k","10k"]`, or build a superscript with `el("tspan",{dy:-5,"font-size":9})`.

### V8 [minor] Inactive roofs and gridlines fall below 3:1 contrast
- **Location:** the polylines with `opacity: .45`, and the gridlines with class `line` (`--border`).
- **Problem:** Inactive series reach only about 1.9–2.2:1 against the surface in light mode and about 2.4–3.0:1 in dark mode. Gridlines are about 1.4:1. Readers need the inactive roofs to compare chips.
- **Evidence:** Computed contrast ratios, for example light green at .45 is 1.92:1 and dark blue at .45 is 2.45:1. In the dark screenshot the purple and green roofs are faint.
- **Concrete fix:** use `opacity: .7` and `stroke-dasharray: "5 3"` for inactive roofs, so they stay readable and still clearly secondary. Gridline contrast is acceptable for a grid. Optionally draw the decade lines in `--muted` at opacity .35.

### V9 [minor] Roofline slider exposes the log exponent to assistive technology
- **Location:** `<input type="range" id="roof-ai" min="-1" max="4">`.
- **Problem:** A screen reader announces "0" for 1 FLOP/B and "1.85" for decode at batch 64. The step is 0.01 in log space, so the arrow keys barely move the slider.
- **Evidence:** One ArrowRight moved the value from 3 to 3.01. The input has no `aria-valuetext`.
- **Concrete fix:** in `draw()`, add `ai.setAttribute("aria-valuetext", nice(Math.pow(10,a)) + " FLOP per byte, " + bound)`. Also add `<datalist>` tick marks at the integer decades.

### V10 [minor] WSE-3 roof shown with no caveat in the widget
- **Location:** the WSE-3 chip entry and the readout.
- **Problem:** With the WSE-3 selected, the widget shows decode at 1 FLOP/B as compute-bound on 21 PB/s of SRAM. That is the comparison the warning callout below calls a trap. The pedagogy review (P1) and the accuracy review (A8) say the same; here it is a matter of what the visual shows.
- **Evidence:** The readout for the WSE-3 at 1 FLOP/B shows about 100% of peak with no qualification.
- **Concrete fix:** when `sel.value == 3`, append a line to the readout: `"note: 21 PB/s is 900,000 private 48 KB SRAMs; only weights that fit in 44 GB stay on this roof. See 'The comparison trap' below."`. Also draw a second, dashed WSE-3 roof labelled "if weights stream from MemoryX" (see N3), or at least a dashed "fabric/off-wafer" roof once later chapters supply that number.

### V11 [minor] Decode/prefill figure: "read once" vs "used once" asymmetry; arrow semantics
- **Location:** the second figure, the text at (95,112), (465,112), (20,190) and (390,190).
- **Problem:**
  - The decode side labels W "140 GB (70B, fp16)", while the prefill side labels it "read once". Both sides read W once. The real contrast is how many times each byte is used (1 vs 2,000), and the figure does not show that as a quantity.
  - The arrow runs from W into x, which suggests the weights flow into the activation.
  - The output y is not drawn.
  - The KV cache, which decode also streams, is absent.
- **Evidence:** This is what the 1100-light-fig1 screenshot shows.
- **Concrete fix:**
  - Label both W boxes "140 GB · read once".
  - Under each arrow, add a counter in `--accent`: "used ×1" and "used ×2,000".
  - Change the activation labels to "x (1×8192)" and "X (2000×8192)".
  - Add a small output box "y" after a "→ W·x →" glyph.
  - Optionally add a thin amber strip under the decode W labelled "+ KV cache (grows with context)".

### V12 [minor] "Three answers" figure: wrong edge marker, unlabeled divider, no bandwidths per level
- **Location:** the third figure.
- **Problem:**
  1. The "package edge" line is drawn between L2 and HBM, but H100 HBM3 sits on the same CoWoS package. The boundary there is the die edge (see pedagogy P13).
  2. The Tenstorrent dashed divider has no label.
  3. The caption claims bandwidth falls with distance, but only HBM and GDDR6 carry a bandwidth. RF/smem and L2 show only capacity, and the WSE-3 row gives an aggregate figure.
  4. The `[Vendor]` amber tspan is not a course tag (see A6).
  5. There is a dead element: `<path d="M415 56 H440" stroke="none"/>`.
  6. The PE math box and the 48 KB box are 2 px apart, while every other gap is 15 px. The tight gap is presumably meant as "adjacent", but nothing says so.
- **Evidence:** This is what the 1100-light-fig2 and 1100-dark-fig2 screenshots show.
- **Concrete fix:**
  - Rename the label to "die edge" and add the same label under the Tenstorrent divider.
  - Add a small `font-size=10` bandwidth line under each box: H100 L2 "~3.8 TB/s [Indep, Chips and Cheese]". For RF/smem, either "~30+ TB/s aggregate [Derived]" or "tens of TB/s". For Blackhole L1, leave it unlabelled or mark "[to verify]".
  - Encode distance with connector line weight, thicker for higher bandwidth.
  - Replace the tspan with a footnote marker and put the tag in the figcaption: `<span class="tag vendor">Vendor</span>`.
  - Delete the dead path.
  - Add a tiny "wire, 1 cycle" label between the PE and SRAM boxes.

## Proposed new visuals (prioritised)

### N1 (highest) Decode speed calculator: bandwidth sets tokens per second
- **Purpose:** turn "decode is bandwidth-bound" (objective 2) into numbers, and show the capacity problem (pedagogy P3/P4) that the prose only implies.
- **Content and data:**
  - Inputs:
    - model size: 8B, 70B or 405B parameters;
    - weight format: FP16 = 2 B, FP8 = 1 B, FP4 = 0.5 B;
    - batch size: 1–256, log slider;
    - chip: H100 80 GB/3.35 TB/s, B200 192 GB/8 TB/s, Blackhole p150 32 GB/0.512 TB/s, WSE-3 44 GB/21 PB/s.
  - Computed values (all tagged Derived):
    - weight bytes = params × bytes;
    - chips needed to hold the weights = ceil(bytes / capacity);
    - time per decode step ≥ weight bytes / (chips × bandwidth);
    - upper bound on tokens/s per user = 1 / step time;
    - aggregate tokens/s = batch × that;
    - intensity ≈ 2·batch / bytes-per-param FLOP/B, compared with the ridge.
  - Example: 70B FP16 on H100 needs 2 GPUs. 140 GB / 6.7 TB/s ≈ 21 ms, so at most about 48 tok/s per user.
- **Interaction:** sliders and selects update a horizontal bar of "ms per token" split into "weight streaming" and "math" segments, so the reader sees the math segment is tiny at batch 1. A row of chip icons shows how many chips are needed. A "show on roofline" link sets the roofline widget's intensity.
- **Placement:** right after the decode/prefill figure in "Why LLM decode lives on the slanted part".

### N2 Capacity vs bandwidth map ("where can the working set live?")
- **Purpose:** show the real trade-off behind the comparison trap. Fast memory is normally small, and Cerebras is the outlier with large capacity at high bandwidth.
- **Content and data:** a log-log scatter, x = capacity in bytes, y = bandwidth in B/s. Points:
  - H100 RF+L1/smem: about 66 MB, bandwidth "tens of TB/s" [Derived, show as range bar];
  - H100 L2: 50 MB, about 3.8 TB/s [Indep];
  - H100 HBM3: 80 GB, 3.35 TB/s [Vendor];
  - B200 HBM3e: 192 GB, 8 TB/s;
  - Rubin HBM4: 288 GB, 19.2 TB/s (revised);
  - Blackhole GDDR6: 32 GB, 0.512 TB/s;
  - Blackhole L1 total: about 120 × 1.4 MiB [verify count];
  - WSE-3 SRAM: 44 GB, 21 PB/s [Vendor].
  - Vertical reference lines for working sets: 70B FP16 = 140 GB, 8B FP16 = 16 GB.
- **Interaction:** hovering a point shows its provenance tag. A toggle labelled "Marketing comparison / Fair comparison" draws an arrow from WSE-3 SRAM to either H100 HBM (labelled 6,300×) or H100 RF+smem, and changes the ratio label.
- **Placement:** replace or follow "Three answers", directly before "The comparison trap" callout.

### N3 Roofline per memory level (extend the existing widget)
- **Purpose:** state the idea that the bandwidth term depends on which memory level feeds the kernel (pedagogy P1).
- **Content and data:** add a "memory level" control next to the chip select.
  - H100: HBM 3.35 TB/s, L2 about 3.8 TB/s, smem/RF tens of TB/s (dashed, labelled "estimate").
  - WSE-3: local SRAM 21 PB/s. Also offer a weights-streamed roof using MemoryX/fabric bandwidth from chapter 8 sources, or leave it disabled with "see Ch 8".
  - Draw every level of the selected chip as a stacked set of slanted roofs under one flat ceiling.
- **Interaction:** radio buttons choose the level that drives the dot. The readout names the level.
- **Placement:** inside the existing `#roof` widget.

### N4 "The wall is getting taller" ridge-point bar chart
- **Purpose:** quantify the sentence "FLOPs grow much faster" (pedagogy P11).
- **Content and data:** paired bars per generation, on a log axis or as normalised growth, with a ridge-point line overlaid:
  - H100: 989 TF BF16 / 3.35 TB/s → 295 FLOP/B;
  - B200: 9 PF FP4 dense / 8 TB/s → 1,125;
  - Rubin: 50 PF NVFP4 inference / 19.2 TB/s → about 2,600 [Derived; Rubin numbers are revised and secondary].
- **Interaction:** a toggle labelled "same format (BF16) / headline format" shows how much of the growth comes from shrinking the number format. Where BF16 figures for B200 and Rubin are not in the notes, grey those bars out with "not sourced".
- **Placement:** right after the paragraph "And the wall is getting taller".

### N5 Animated decode step
- **Purpose:** make "reads everything to do very little" felt rather than read.
- **Content and data:** a schematic chip with a compute block and a memory block. During one decode step, weight tiles stream across a bus whose width is proportional to the selected chip's bandwidth. A utilisation meter shows ALU busy % ≈ min(1, intensity / ridge): 0.34% for H100 at batch 1, 22% at batch 64.
- **Interaction:** play/pause, and a batch slider shared with N1. The bus animation speed and the meter update together. Honour `prefers-reduced-motion` by showing a static end state.
- **Placement:** optional. Combine with N1 if space allows.

### N6 Quiz helper: intensity counter for small kernels
- **Purpose:** support the first quiz question and the corrected vector-add preset.
- **Content and data:** pick a kernel: vector add, SAXPY, dot product, GEMV, or GEMM with N = 64/1024/8192. Show FLOPs, bytes read and bytes written, each as a coloured block bar, then the resulting intensity. For example, SAXPY f32 does 2 FLOP per 12 B, so 0.167 FLOP/B. GEMM N×N f32 does 2N³ FLOP over 12N² B, so N/6 FLOP/B.
- **Interaction:** selecting a kernel puts its marker on the roofline.
- **Placement:** under the roofline widget, or inside the quiz.
