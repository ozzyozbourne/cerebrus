# ch15 · visuals review

Summary: The chapter has three visuals: the metric bar-chart widget, the programming-model figure and the decision guide. It renders without console errors or horizontal scroll at 1100 px and 390 px, in light and dark. The bar chart is the weak point. It draws log-scale bars from an arbitrary baseline with no axis, so bar lengths misstate the ratios: the 21 PB/s vs 512 GB/s gap is about 41,000×, but the bars differ about 5.6×. It also mixes numbers that cannot be compared (SRAM vs HBM bandwidth, FP16 vs FP4, a 23 kW system vs one card) with no visual cue. It clips a label, promises "tags" it never shows, and does not recolour when the theme toggle is used. The two static figures are tidy but say little: the programming-model figure has no arrows or data flow, and the decision guide's text becomes unreadable on mobile. For a synthesis chapter there is no synthesis visual (ridge points, capacity vs bandwidth, scaling topology), and Ch1's roofline idea is never brought back.

Method: Playwright/Chromium at 1100×900 and 390×900, `colorScheme` light and dark, every metric in `#c-m` selected and screenshotted, both `<figure>`s screenshotted, plus a run that clicks the top-bar theme toggle. Console errors and warnings: none in any run. `scrollWidth == innerWidth` in every run.

## Findings (defects in existing visuals)

### V1 [critical] Log-scale bars from an arbitrary baseline: bar lengths misstate the ratios
- **Location:** `#cmp` widget, `draw()`: `lo = floor(log10(min)) - 0.3`, bars from x=200 to `X(v)`.
- **Problem:** A bar's length on a log axis is set by where the baseline sits, and here the baseline floats with each metric. There is no axis, no ticks and no gridlines, so the reader cannot recover the scale. The bars look like linear ratios, which they are not.
- **Evidence:** "Main memory bandwidth": WSE-3 bar ≈ 401 px vs p150 ≈ 72 px (5.6×), but the true ratio is 21e15 / 0.512e12 ≈ 41,000×. "Main memory capacity": B200 192 GB vs CS-3 44 GB is 4.4× but draws as about 1.7×. "Compute units": 900k vs 120 draws as about 10×. The hint's only warning is the words "Log scale".
- **Concrete fix:** Replace the bars with dots (a Cleveland dot plot) on a labelled log axis. Draw decade gridlines and tick labels (1 G, 10 G, 100 G…), fixed per metric family. Then add a ratio readout, such as "CS-3 / H100 = 6,270×", computed from the values. If bars stay, start every metric's axis at a fixed, labelled decade and draw that axis.

### V2 [major] Incomparable quantities drawn as if comparable
- **Location:** `M` table, metrics "Main memory bandwidth", "Peak low-precision compute", "Power" and "Compute units".
- **Problem:** The caveat appears only in the readout below the chart. The marks themselves look identical:
  - **Bandwidth:** WSE-3 aggregate SRAM bandwidth is plotted beside DRAM/HBM bandwidth.
  - **Compute:** FP16 dense (an analyst estimate) is plotted beside BlockFP8, BF16 and FP4.
  - **Power:** a whole 23 kW system is plotted beside single cards.
  - **Compute units:** a PE is about 0.05 mm², an SM is far larger.
- **Evidence:** In the screenshots for metrics 2, 3, 4 and 5, all four bars use the same solid style. The B200 FP4 9 PF bar sits next to the H100 BF16 bar with no marker.
- **Concrete fix:**
  - Draw a hollow or hatched mark when a value is "not like-for-like", and print the format inline, for example "9 PF (FP4)" and "989 TF (BF16)".
  - Split compute into per-format choices, or normalise to one format where known (H100 BF16 989 T vs B200 BF16 dense ~2.25 P, if that figure is sourced).
  - For power, add the system-level views: one DGX/HGX H100 8-GPU node (~10 kW) and a Galaxy Blackhole (~12 kW, Flopper). Alternatively, rename the hint to "per sold unit" and say that the units differ.
  - Drop "Compute units", or replace it with "SRAM per unit (KB)", which is meaningful.

### V3 [major] Hint promises provenance tags; none are rendered
- **Location:** `.hint` says "Tags show provenance". The `#c-out` readout is plain monospace text.
- **Problem:** The course rule is that every number carries a `.tag`. The widget's twenty or so numbers carry none. Provenance appears only as words inside a run-on string ("WSE-3 Vendor; p150 Vendor; H100 … Derived").
- **Evidence:** All cmp-*.png screenshots: no coloured tag chips anywhere in the widget.
- **Concrete fix:** Store provenance per value (for example `{v:21e15, tag:"vendor"}`). Render a small tag chip after each value label, either as an HTML overlay or with SVG rect+text using the `.tag` colours. Turn the readout into a short HTML list, one line per device.

### V4 [major] Value label clipped: "900 k" shows as "900 l"
- **Location:** `#cmp`, metric "Compute units". The label sits at `X(max)+6 = 656` inside a 680-wide viewBox.
- **Problem:** The longest bar plus its label overflows the viewBox. "Compute units" has no unit, so the label is a bare "900 k". "15.6 PFLOP/s" also comes within a few px of the edge.
- **Evidence:** In cmp-1100-light-4.png the label reads "900 l", with its right side cut off.
- **Concrete fix:** Make the plot area 200→600 and the viewBox 700 wide, or put the label inside the bar (right-aligned, white) when `X(v) > 560`. Format counts as "900,000 PEs" rather than an SI suffix.

### V5 [major] Charts do not recolour when the theme toggle is used
- **Location:** `#cmp` bars (`fill: cssVar(...)`), `#dg` answer pills (`fill: cssVar(c)`), and the CSL links in `#pm` (`stroke: cssVar("--blue")`).
- **Problem:** Colours are resolved once at draw time. After the ◐ toggle, the page switches to the dark tokens but these marks keep the light palette until reload. The reverse happens too.
- **Evidence:** toggle-cmp.png and toggle-dg.png were taken after clicking the toggle from a light start. The bars and pills are dark orange #c2410c, blue #1d4ed8 and green #15803d on a #1b1e25 surface, and differ from the OS-dark render in fig1-1100-dark.png.
- **Concrete fix:** Use the existing CSS classes (`f-acc`, `f-grn`, `f-blu`, `f-pur`, `s-blu`) instead of `cssVar()` fills, so CSS handles the theme. Alternatively, watch `data-theme` with a MutationObserver and call `draw()` again.

### V6 [major] Mobile (390 px): SVG text shrinks to about 5–6 px
- **Location:** All three SVGs. The widget's viewBox is 680, scaled to 324 px (×0.48). The figures use viewBox 760, scaled to 340 px (×0.45).
- **Problem:**
  - Bar labels (12 px) render at about 5.7 px, and the decision-guide questions (13 px) at about 5.8 px.
  - The programming-model sub-labels (10 px) render at about 4.5 px.
  - Meanwhile the readout below the chart stays at 14 px, so the chart is the least legible thing in the widget.
- **Evidence:** cmp-390-light-3.png, fig0-390-dark.png, fig1-390-light.png: the device names and the "CB_in/CB_out" and "private 48 KB · colors" captions cannot be read.
- **Concrete fix:**
  - **Decision guide:** build it in HTML (a CSS grid of rows with a coloured pill) instead of SVG, so the text wraps.
  - **Bar chart:** below 600 px, switch to a narrow layout with labels above the bars (viewBox ~360 wide), or render it as HTML rows.
  - **Programming-model figure:** stack the three panels vertically on mobile, either as three separate SVGs in a `.grid2`-style grid or with a 260-wide viewBox per panel.

### V7 [minor] n/a handling looks like a zero bar and hides the reason
- **Location:** `#cmp`, "On-chip SRAM" and "Compute units" for B200.
- **Problem:** "n/a" is drawn in small muted text exactly where a bar would start, so it reads as "tiny value". The reason ("not compiled here") appears only in the readout. Also, `vals.filter(v => v)` would silently drop a legitimate 0.
- **Evidence:** cmp-1100-light-0.png.
- **Concrete fix:** Draw a dashed empty track across the plot width with "not verified in course research" in italics. Use `v != null` for filtering.

### V8 [minor] Programming-model figure shows boxes but no data movement
- **Location:** `figure` with `<g id="pm">`.
- **Problem:** The caption contrasts *how data moves*, but the figure has no arrows:
  - **CUDA:** the warps are not connected to HBM, the L2/L1 caches (the defining "bring data to compute" path) are missing, and "warp 0 … (thousands)" is an odd label.
  - **TT-Metalium:** CB_in/CB_out are floating text rather than buffers. GDDR6 is not linked to the reader or writer, and only one core is shown, so the "core ↔ core over NoC" path is invisible.
  - **CSL:** only horizontal links are drawn (the mesh is 2-D), and there is no host/memcpy edge or edge I/O. Neither "colors" nor the fact that each PE has its own SRAM is shown.
- **Evidence:** fig0-1100-light.png.
- **Concrete fix:**
  - **CUDA:** draw arrows HBM → L2 → SM (L1/shared) → warps, with the label "hardware caches, implicit".
  - **TT-Metalium:** draw GDDR6 → reader → [CB_in rect] → compute → [CB_out rect] → writer → GDDR6/other core, and add a ghosted second core joined by a NoC arrow.
  - **CSL:** add vertical links, two coloured routes (for example a red-colour route east and a blue-colour route south, with wavelet dots), and a host → edge memcpy arrow.
  - Add a common footer row under all three panels: "data → compute (cached)" / "data → compute (explicit DMA)" / "compute at data (messages)".

### V9 [minor] Decision guide is a list drawn as a picture
- **Location:** `figure` with `<g id="dg">`.
- **Problem:** Four fixed-width text rows in SVG add nothing over a table, and they break on mobile (V6). There is no "it depends" path and no conditions (model size vs 44 GB, batch size, budget). It also contradicts nothing and adds nothing to the evidence table above it.
- **Evidence:** fig1-1100-light.png and fig1-390-light.png.
- **Concrete fix:** Replace it with the interactive chooser in proposal N3, or at least build it in HTML and give each row a "because…" link back to the evidence row that supports it.

### V10 [minor] Cerebras bandwidth bar labelled "main memory" invites the wrong reading
- **Location:** The metric names "Main memory capacity" and "Main memory bandwidth".
- **Problem:** For CS-3 the "main memory" is on-wafer SRAM, while MemoryX (TB-scale, for training) exists but is not drawn. A reader comparing 44 GB with 192 GB may conclude that CS-3 cannot hold more. The opposite misreading also happens with the 21 PB/s bar.
- **Concrete fix:** Rename the metric to "Memory the compute reads every step", or draw a secondary hollow mark for CS-3 + MemoryX (training) with its own provenance tag.

## Proposed new visuals (prioritised)

### N1 Ridge-point and decode-intensity chart (highest priority; replaces or complements the bar widget)
- **Purpose:** This is the synthesis. It brings back Ch1's roofline and shows on one axis why each design wins where it does.
- **Content and data:**
  - **Axis:** one horizontal log axis, "FLOP per byte of the memory the weights live in", spanning 0.1 to 10,000.
  - **Device markers** at their ridge points = peak ÷ bandwidth:
    - WSE-3: 15.6 PF ÷ 21 PB/s ≈ **0.74** (Analyst / Vendor → Derived)
    - H100 BF16: 989 T ÷ 3.35 T ≈ **295** (Derived)
    - B200 FP4: 9 P ÷ 8 T ≈ **1,125**. If a BF16 dense figure is sourced, show both, joined by a "format change" bracket.
    - p150 BlockFP8: 664 T ÷ 0.512 T ≈ **1,300** (Derived)
    - p150 with weights in L1 SRAM: tied to the 180 MB SRAM, marked as "if it fits", with the bandwidth flagged as not compiled.
  - **Workload bands** above the axis:
    - decode at batch 1 ≈ 1 FLOP/B
    - decode at batch 64 on 70B ≈ 50–100
    - prefill ≈ thousands
    - the stencil from Lab 3 (derive its FLOP per byte of SRAM from the program, about 0.25–0.5)
- **Interaction:** a batch-size slider (1 to 512) moves the decode marker (intensity ≈ batch). Each device marker lights up "bandwidth-bound" or "compute-bound", and a readout shows the attainable fraction of peak = min(1, I / ridge).
- **Placement:** directly after the lede, as the chapter's opening figure. The current bar widget moves under "Architecture and memory".

### N2 Capacity vs bandwidth scatter (the trade-off map)
- **Purpose:** This shows the central trade-off in one picture: fast-but-small vs big-but-slow.
- **Content and data:**
  - **Axes:** log-log. X is memory capacity per unit (bytes), Y is bandwidth to that memory (B/s).
  - **Points, one per memory tier**, so each device draws a short path from SRAM to DRAM:
    - **WSE-3:** SRAM 44 GB @ 21 PB/s, plus a hollow point for MemoryX (capacity from Ch8, bandwidth = SwarmX/MemoryX link if sourced, otherwise n/a).
    - **p150:** SRAM 180 MB (bandwidth n/a, or derived if available) → GDDR6 32 GB @ 512 GB/s.
    - **H100:** L2 50 MB → HBM 80 GB @ 3.35 TB/s.
    - **B200:** HBM 192 GB @ 8 TB/s.
  - **Overlays:**
    - Iso-lines of "time to read all of it once" = capacity ÷ bandwidth (1 µs, 1 ms, 10 ms, 100 ms) as diagonals. This equals the lower bound on per-token decode time if the weights fill that memory.
    - Model-size verticals: 8B, 70B and 1T at FP16 (16 GB, 140 GB, 2 TB).
- **Interaction:** hover a point for its value, tag and source. A toggle switches between per device and per rack/system (CS-3, NVL72 13.5 TB @ 576 TB/s, Galaxy Blackhole 1 TB @ 16 TB/s).
- **Placement:** start of "Architecture and memory", before the table.

### N3 Interactive "will it fit / what limits it" chooser (replaces the static decision guide)
- **Purpose:** This turns the decision guide into reasoning instead of verdicts.
- **Content and data:**
  - **Inputs:** model size in parameters (1B–2T), precision (FP16/FP8/FP4), batch size, and whether you optimise for latency or $/token.
  - **Outputs per device:**
    - the number of units needed to hold the weights: ceil(bytes ÷ 44 GB, 32 GB, 80 GB, 192 GB);
    - the lower bound on per-token decode time = bytes per unit ÷ bandwidth;
    - whether batch-size decode is under or over the ridge (reusing N1);
    - which column in the "evidence" table supports or contradicts the choice.
  - **Rendering:** HTML rows with tags, so it is mobile-safe. Every derived number gets a `derived` tag.
- **Placement:** replaces the `#dg` figure in "Choosing".

### N4 Scaling-topology diagram (three small panels)
- **Purpose:** "Scaling" is currently a single paragraph.
- **Content and data:** three panels with the same grid style:
  - **NVIDIA:** an NVL72 rack (72 GPUs on NVSwitch, ~130 TB/s, 1.8 TB/s per GPU), with InfiniBand/Ethernet links to other racks.
  - **Tenstorrent:** a Galaxy of 32 chips in a switchless 2-D mesh of Ethernet links (14×400 GbE per Blackhole), extending to more Galaxies over the same Ethernet.
  - **Cerebras:** one wafer drawn as a mesh "rack on silicon" (214 Pb/s fabric), plus MemoryX → SwarmX → up to 2,048 CS-3 for training, a pipelined chain of wafers over Ethernet for inference, and a dashed CS-4 Direct Wafer Link.
  - Each link is labelled with its bandwidth and provenance tag. A common legend maps line thickness to log bandwidth.
- **Interaction:** a toggle highlights the "scale-up domain" (NVLink domain / Galaxy mesh / one wafer) vs "scale-out".
- **Placement:** inside "Scaling", replacing or illustrating the paragraph.

### N5 Strengths/weaknesses as a quadrant or radar (low priority)
- **Purpose:** a one-glance profile to recap the chapter.
- **Content:** six axes, each scored only from tagged numbers already in the chapter, with the raw value shown on hover: per-user decode speed, capacity per unit, throughput per dollar at batch, power per unit, software maturity (qualitative, marked "editorial"), and openness. To stay honest, prefer a 2×2 quadrant over a radar: x = capacity per unit (log), y = bandwidth per byte of capacity (1 / time-to-read), with one bubble per device. The axes are derived, so there is no fake scoring.
- **Placement:** just before "The fair reading" callout.

### N6 Lessons-learned cycle breakdown (small)
- **Purpose:** The "What programming the wafer taught us" section quotes measured cycles (the ~88-cycle fixed cost per stencil step) but shows nothing.
- **Content:** a stacked bar or line of cycles per step vs cells per PE, from the Lab 3 measured outputs (`course/programs/05-*/expected_output.txt`). It shows the fixed communication cost against the growing compute cost and the crossover point. Tag: `measured`.
- **Placement:** next to the "Communication is cheap but not free" bullet.

Index page (glanced): it renders cleanly in both themes. The Part IV map segment is green, but the ch15 kicker uses the accent colour, a trivial inconsistency. No other issues.
