# ch08 · visuals review

Summary: I rendered the chapter at 1100 and 390 px wide, in light and dark. It has two static SVG figures (weight streaming, the 4-wafer inference pipeline) and one widget (wafers needed). The page shows no console errors and no horizontal scroll at either width, and dark-mode colours resolve correctly. All three SVGs are fixed-width figures (760 / 760 / 680) scaled down to fit. At 390 px they shrink to 0.45×, so the 11–13 px labels render at about 5–6 px and cannot be read. That is the main defect. The widget's maths is correct at every edge value I tried, but its picture shows almost nothing: unlabelled identical rectangles, no GPU comparison, and an overflow label drawn outside the viewBox. Both figures leave out the mechanism the chapter is about: per-layer streaming, the gradient return, and the autoregressive loop in the pipeline. Counts: 0 critical, 4 major, 7 minor. 6 new visuals proposed.

Method: Playwright, `file:///home/user/cerebrus/course/08-systems.html`, viewports 1100×900 and 390×900, `colorScheme` light/dark, full-page shots plus one shot per figure/widget. I drove all three controls (range by value + `input` event, `selectOption`, and keyboard Home/End), measured text bounding boxes with `getBBox`, and listened for console and page errors (none).

## Findings (defects in existing visuals)

### V1 [major] All three SVGs are illegible on a phone (text renders at 5–6 px)
- Location: weight-streaming figure (`viewBox 0 0 760 330`), pipeline figure (`viewBox 0 0 760 210`), widget `#p-svg` (`viewBox 0 0 680 120`).
- Problem: `figure svg { max-width:100%; height:auto }` scales each drawing to the 340 px content width. That is a factor of 0.447 for the two figures and 0.476 for the widget. The 11 px labels ("activations stay here", "~35 GB weights") become ~4.9 px. The 12 px labels ("layers 1–20", the SwarmX subtitle) become ~5.4 px, and the 13 px footnote lines become ~5.8 px. The widget's wafer icons shrink to 12×19 px.
- Evidence: measured rendered sizes at 390 px: 340×148, 340×94 and 324×57. Screenshots el0/el1-390-light show the subtitles and footnote as unreadable smears.
- Concrete fix: give each figure a portrait layout below 680 px rather than relying on scaling.
  - Weight streaming: the 4 CS-3 boxes are built in JS (`#cs`), so build them as a 2×2 grid when `matchMedia('(max-width:680px)')` matches. Use a 400×420 viewBox, MemoryX/SwarmX boxes 300 wide, wafers 170×64 at x = 20/210 and y = 230/310, and move the bottom note into the figcaption.
  - Pipeline: stack the four wafers vertically (viewBox 340×470, boxes 260×80, arrows pointing down).
  - Widget: draw 10 wafers per row instead of 20 at narrow widths.
  - Re-run on `change` of the media query.
  - In every case, move long single-line SVG notes ("Each wafer holds…", "4 × 44 GB = 176 GB…") out of the SVG and into the `figcaption`, where they reflow.
  - The minimum alternative is to wrap each figure SVG in a `div` with `overflow-x:auto` and set `svg{min-width:600px}` there. That still beats unreadable text.

### V2 [major] Weight-streaming figure omits the mechanism its caption claims: no per-layer flow and no gradient path to the wafers
- Location: first figure; JS block `#cs`.
- Problem: the four links from SwarmX to the wafers are single undirected purple lines. Only the MemoryX↔SwarmX pair has arrows (amber down, purple up). So the figure never shows weights arriving at the wafers or gradients leaving them, which is the point of the sentence it illustrates ("broadcast of weights… reduces gradients in the opposite direction"). "One layer at a time" appears only in the footnote, and the picture shows nothing per-layer. The CS-3 boxes say "activations stay here" but carry no hint of which batch slice each holds.
- Evidence: el0-1100-light.png. The fan lines are `class:"s-pur"` with no marker. The amber colour (weights) never reaches the wafers.
- Concrete fix: for each wafer i, draw two offset lines from the SwarmX bottom edge to the wafer top: an amber line with `marker-end=url(#a8)` (weights, down) offset −6 px in x, and a purple line with `marker-end` reversed (gradients, up) offset +6 px. Label the left-most pair once: "W(layer k)" in amber and "∇W(layer k)" in purple. Change the wafer subtitle to `batch slice ${i+1}/4 · activations`. Add a small amber label beside MemoryX→SwarmX: "one layer's weights". New visual N1 adds the animation of layer k advancing.

### V3 [major] The widget's graphic carries almost no information, and its overflow label is invisible
- Location: `#cap` widget, `cap()` and `#p-svg`.
- Problem:
  - (a) Every wafer is the same unlabelled rectangle. Nothing shows how full each wafer is, how much is reserved, or that the count is per WSE-3.
  - (b) The GPU comparison exists only in text, though the hint says "Compare with GPUs' HBM capacity".
  - (c) For fewer than 21 wafers, the bottom ~60 % of the SVG is empty (the default view at 1100 px shows four 26×40 boxes and a blank band).
  - (d) Above 40 wafers the drawing stops at 40, and the "… N wafers total" text is placed at y=140 in a 120-tall viewBox, so it is clipped. This was also reported as A7/P14.
  - (e) The readout's last line is a static slogan that never changes with the controls.
- Evidence: at 1000B / 16-bit / 50 % the readout says 91 wafers, but the SVG shows exactly 40 boxes and no label (w-max.png). `getBBox` of the SVG content reaches y=143, beyond the viewBox height of 120.
- Concrete fix: redraw `#p-svg` with a dynamic height (`viewBox 0 0 680 ${rows*50+70}`), using three rows of marks.
  - Row 1, "WSE-3 × N": each wafer box is filled bottom-up in amber in proportion to its weight load (the last wafer only partly), with the reserve slice as a hatched band at the top. Up to 60 boxes at 20 per row; beyond that, one box stands for 5 wafers and a legend says so.
  - Row 2, "H100 × M" and row 3, "B200 × K": boxes whose widths are drawn to the same GB scale (80 GB and 192 GB devices), so the reader sees that 4 wafers ≈ 2 H100 ≈ 1 B200 in capacity.
  - Put a text label at the left of every row.
  - Replace the static last line of the readout with a computed one: `aggregate weight bandwidth: N × 21 PB/s = X PB/s vs M × 3.35 TB/s = Y TB/s (≈ Z× ) [Derived]` (see N3).

### V4 [major] Pipeline figure shows a one-shot left-to-right flow with no decode loop, and its even split is presented as fact
- Location: second figure, `#pipe`.
- Problem: the figure has a "token activations →" label and three arrows, but no input and no output. Decode is autoregressive: the token produced after wafer 4 must re-enter wafer 1. Without that return path the reader cannot see why a single sequence keeps only one wafer busy at a time (pedagogy P3). The labels "layers 1–20 … 61–80" and "~35 GB weights" are drawn as facts, though the split is illustrative (A6). The band between y=130 and y=175 is empty.
- Evidence: el1-1100-dark.png.
- Concrete fix:
  - Add a "prompt / token t" pill at the left before wafer #1 and a "token t+1" pill after wafer #4.
  - Draw a dashed blue return arc under the boxes (y≈150) from wafer #4 back to wafer #1, labelled "next decode step: token t+1 re-enters wafer 1".
  - Change the per-box subtitle to "≈20 layers · ≈35 GB" and add "(illustrative split)" to the bottom note.
  - New visual N2 animates this loop.

### V5 [minor] SwarmX subtitle overflows its box
- Location: first figure, text "broadcast ↓ weights · reduce ↑ gradients".
- Problem: the text spans x=261–499, but the box spans x=270–490, so it overruns by 9 px on each side. The MemoryX subtitle (274–486) has only 4 px of margin.
- Evidence: `getBBox` measurement; visible in el0-1100-light.png where "broadcast" and "gradients" cross the purple stroke.
- Concrete fix: widen both boxes to `x="250" width="260"` and shift the arrows to x=370/390. Alternatively, shorten the subtitle to "broadcast ↓ W · sum ↑ ∇W".

### V6 [minor] The "[Derived]" marker in the pipeline SVG does not match the course's provenance tag
- Location: `<tspan class="f-amb">[Derived]</tspan>` in the pipeline figure.
- Problem: it renders amber (rgb 180,83,9 light; 251,191,36 dark), while `.tag.derived` is grey on a light chip (rgb 93,98,112 on 242,240,234). It reads as a warning colour, not as a provenance tag. A9 raises the same point.
- Concrete fix: move the whole note into the figcaption and use `<span class="tag derived">Derived</span>`. This also helps V1.

### V7 [minor] Parameter slider is linear from 1 to 1000; small and mid-size models are hard to hit, especially on mobile
- Location: `#p-n` (min 1, max 1000, step 1). On mobile `.controls input[type=range]{width:120px}`.
- Problem: 70B sits at 7 % of the track. On a 120 px slider each pixel is ≈8B, so 7B/8B/13B cannot be selected reliably, and the slider does not land on 405 exactly.
- Concrete fix: use a log-scale slider (`min=0 max=3 step=0.01`, n = round(10^v)) and add preset buttons: `8B` `70B` `120B` `405B` `1T`. Each button sets the value and calls `cap()`.

### V8 [minor] B200 capacity is discounted twice and labelled inconsistently
- Location: `cap()`, `b200 = Math.ceil(gb / (180 * (1 - r)))`, readout "~180 GB usable HBM".
- Problem: 180 GB is already a "usable" figure (192 GB nominal, report line 239), and the KV reserve is then subtracted again. The H100 uses the nominal 80 GB. The two GPUs are therefore treated differently.
- Concrete fix: use the nominal capacity for both (`192` for B200) and label it "192 GB HBM3e" <span class="tag vendor">Vendor</span>, so the reserve slider is the only discount.

### V9 [minor] Readout rounding hides small models
- Location: `gb.toFixed(0)`.
- Problem: 1B at 4-bit shows "weights: 1 GB" (actually 0.5 GB), and 405B at 4-bit shows "203 GB" (202.5).
- Concrete fix: `gb < 10 ? gb.toFixed(1) : gb.toFixed(0)`.

### V10 [minor] Widget is not announced to assistive tech
- Location: `#p-out`, `#p-svg`.
- Problem: the readout has no `aria-live`, and the SVG's `aria-label` is a static "Wafers needed".
- Concrete fix: add `aria-live="polite"` to `#p-out`, and in `cap()` call `svg.setAttribute('aria-label', `${w} WSE-3 wafers needed`)`.

### V11 [minor] Mobile control layout: the reserve value wraps onto its own line
- Location: `#cap .controls` at 390 px.
- Problem: "Reserve for KV/activations" plus the slider fills the line, so "20%" drops alone onto the next line (el2-390-dark.png).
- Concrete fix: shorten the label to "KV reserve" (the hint already explains it), or put the value span inside the label text: `KV reserve <span id="p-rv">`.

Note for the fixer: pedagogy P12 proposes the text "With the widget's default 20% reserve … it is 23". The widget actually prints **24** (810 / 35.2 = 23.01, rounded up by `ceil`). Use 24.

## Proposed new visuals (prioritised)

### N1 (high) Animated weight-streaming step: layers flowing down, gradients flowing up
- Purpose: show what P1 says the chapter currently states only in a quiz answer. Each layer's weights are fetched once per step and reused across the whole batch, and the gradients come back reduced. This replaces the static first figure, or sits directly under it.
- Content: MemoryX (left column, a stack of L=8 layer slabs W1…W8 plus an "optimizer state" slab), SwarmX, and four CS-3 boxes, each showing a batch slice (e.g. "sequences 1–256", "257–512", …) and an activation stack that grows during the forward pass.
- Animation, one training step:
  1. Forward: for k=1..8, slab Wk lights up and an amber packet travels MemoryX → SwarmX, splits into 4, and reaches every wafer. Each wafer's activation stack gains a layer. Show a counter "weight bytes moved: k × |W|/8".
  2. Backward: for k=8..1, Wk is sent again, and each wafer emits a purple ∇Wk packet. The 4 packets merge at SwarmX (a "Σ" badge) and one packet reaches MemoryX, where slab Wk flashes "update".
  3. A final counter: "each weight used by 4 × B sequences per fetch".
- Interaction: Play/Pause/Step buttons. A "batch size per wafer" slider (1, 8, 64, 512) updates a readout of reuse per fetched byte (`2 × 4 × B` FLOPs per weight byte fetched, labelled Derived). A "wafers" selector (1/2/4/8) adds or removes wafer boxes and shows that MemoryX traffic stays the same while throughput scales (the "linear scaling" claim, Vendor).
- Data: none beyond structure. Label any numbers as illustrative.

### N2 (high) Pipeline-decode animation: one sequence vs many in flight
- Purpose: fix the wrong mental model in P3, that all four wafers work on a token together. Show that one sequence keeps one wafer busy at a time, and that filling the pipeline needs several sequences in flight. Place it after the pipeline figure, replacing or extending it.
- Content: the 4 wafers as in the current figure, plus a time strip underneath (a Gantt chart: 4 lanes for wafers 1–4, time on x).
- Animation: a coloured token dot moves through wafers 1→4 and then returns along the arc (V4) as the next token. Each wafer's lane gets a coloured block while the dot is inside it.
- Interaction: a "sequences in flight" control (1, 2, 4) adds differently coloured dots staggered by one stage. At 1 the Gantt is 25 % filled; at 4 it is 100 %. Readout: "wafer utilisation: s/4; per-sequence tokens per step unchanged" [Derived]. An optional "hop latency" slider (inter-wafer Ethernet hop, labelled illustrative since sources do not give it) shows the share of time spent in transit.

### N3 (high) Bandwidth-bound decode ceiling calculator (extends the capacity widget)
- Purpose: deliver pedagogy P4's worked example interactively and give "bandwidth per byte held" a number.
- Content: from the same controls (params, precision), compute bytes per token = params × bytes/param (batch 1, dense). Plot a horizontal log-scale bar chart of the upper bound on tok/s = aggregate weight bandwidth ÷ bytes per token for:
  - N × WSE-3 at 21 PB/s each [Vendor];
  - M × H100 at 3.35 TB/s each [Vendor];
  - K × B200 at ~8 TB/s each [Vendor].
  N, M and K come from the capacity calculation. Overlay measured points as markers: Llama 3.1-70B 450 tok/s (Aug 2024) and 2,100 tok/s (Oct 2024) [Vendor]; Llama 3.3-70B 2,314 tok/s [Indep].
- Readout: "70B @16-bit: 140 GB/token → H100×2 ceiling ≈ 48 tok/s; WSE-3×4 ceiling ≈ 600,000 tok/s; measured 2,100 → on Cerebras something other than weight bandwidth (hops, compute) is the limit" [Derived].
- Interaction: shares the widget's controls. Add a "times per second each device can read its whole memory" stat tile (WSE-3 ≈ 480,000/s vs H100 ≈ 42/s).

### N4 (medium) Systems timeline (delivers objective 3, pedagogy P9)
- Purpose: objective 3 promises a timeline, and none exists.
- Content: a horizontal SVG timeline, 2019–2026, with lanes for "wafer", "system", "cluster" and "mode":
  - WSE-1 / CS-1 (2019);
  - WSE-2 / CS-2 (2021, 40 GB, 15–20 kW (sources conflict));
  - weight streaming + MemoryX/SwarmX (2021);
  - CG-1 / CG-2 (2023, 64 CS-2, 4 EF);
  - WSE-3 / CS-3 (2024, 44 GB, ~23 kW, max 2,048 CS-3);
  - CG-3 (64 CS-3, 8 EF);
  - inference service launch (Aug 2024, Llama 3.1-70B on 4 CS-3);
  - CS-4 (2026, 3 × WSE-3T per rack, 750 PF sparse, Direct Wafer Links).
  Every label carries its tag colour. Training-mode spans are shaded "layer-pipelined" until 2021 and "weight streaming" after; inference "pinned weights" runs from 2024.
- Interaction: hover or tap a milestone to show its table row in a side card. On mobile, rotate to a vertical timeline.

### N5 (medium) SRAM budget bar for one inference wafer (defines the KV cache visually)
- Purpose: back up P5's KV-cache definition, and show why "fast per user" means "few concurrent sequences" (the warn callout).
- Content: one stacked horizontal bar of 44 GB: weights (35 GB in the illustrative 70B split), and the remainder divided into activations plus KV cache. Below it, the KV-cache size per sequence = 2 × layers_on_wafer × kv_heads × head_dim × bytes × context. Llama 3.1-70B: 80 layers, 8 KV heads, head_dim 128 (from the model config, to be tagged as such), so 20 layers per wafer at 16-bit gives 2×20×8×128×2 = 81,920 B ≈ 80 KB per token per wafer [Derived].
- Interaction:
  - a context-length slider (1k–128k);
  - a "concurrent sequences" slider;
  - the bar fills with KV, turns red when it exceeds the free SRAM, and the readout shows the maximum number of concurrent sequences at that context length. For example, ~9 GB free ÷ (80 KB × 8k tokens ≈ 0.66 GB) ≈ 13 sequences [Derived, illustrative].
  - a GPU toggle switches to an H100 pair (160 GB HBM, 140 GB weights) for contrast.
- Caveat to state: Cerebras's actual KV placement is not documented in the sources, so the visual is a model, not a description.

### N6 (low) Cost vs speed scatter for the warn callout
- Purpose: make "fast per user ≠ cheap per token" visible.
- Content: x = per-user tok/s (log scale), y = $ per million tokens. Points:
  - Cerebras Llama 3.1-70B at (2,100, $0.60) [Vendor];
  - batched H100 as a range box at x ≈ 30–100 tok/s per user (to be sourced or marked illustrative), y $0.10–0.25 [Analyst].
  Each point's colour follows its provenance tag.
- Interaction: hover tooltips with the sources. No controls. Place it inside or directly after the warn callout. Mark any x-range lacking a source as "illustrative" or omit it.
