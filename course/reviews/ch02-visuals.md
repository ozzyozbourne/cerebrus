# ch02 · visuals review

Summary: The chapter has three static SVGs (wafer vs dies, defect-repair schematic, system cross-section) and one widget (defect simulator). The widget is the best visual. Its statistics are correct: over 200 rolls at 0.001/mm², 34.0 of 60 dies were hit, against a Poisson prediction of 33.9, and 46.2 defects fell in the square, matching the vendor's 46. No console errors appeared in any of the 4 renders, and there is no horizontal scroll at 390 px. The main defects: (1) the first diagram is not to scale and contradicts its own text: the "largest square that fits" pokes out of the wafer, the dies are larger than one reticle, and partial dies are drawn; (2) several colours are fixed at draw time with `cssVar()`, so they do not follow the theme toggle; (3) every SVG shrinks to 0.45× at 390 px, which makes the 11–14 px labels illegible; (4) the repair and cross-section schematics leave out the things their captions claim to show. Prose ideas that would gain most from a picture: a yield-vs-area curve, where the 737k usable PEs come from, what the wafer buys in bandwidth, and the FLOPs/clock arithmetic.

Renders checked: 1100 px and 390 px, each in light and dark `colorScheme`, plus the in-page theme toggle (light→dark). I drove the slider at its min (0.0002), its max (0.003) and with 40 ArrowRight key presses, and pressed Re-roll 200 times.

## Findings (defects in existing visuals)

### V1 [major] "Largest square that fits" does not fit, and the drawing is not to scale
- **Location:** Figure 1, right panel (`<rect x="438" y="58" width="214" height="214">` inside a circle of r=140). The same geometry is in the simulator (`half = 107.5` with R=150).
- **Problem:** The square's corners lie 151 px from the centre, outside the 140 px wafer, so the figure visibly contradicts "the largest square that fits in the wafer". The scale is 300 mm / 280 px, so the square is drawn at 229 mm (≈52,600 mm², 14% too large) rather than 215 mm.
- **Evidence:** In the screenshots at both widths and in both themes, all four corners of the orange square sit outside the grey disc. Arithmetic: 107·√2 = 151 > 140.
- **Note for accuracy reviewers:** a true 215 × 215 mm square has a 304 mm diagonal, which is larger than a 300 mm wafer. Either the real die has trimmed corners or 46,225 mm² is a rounded figure. The figure should not draw something that is impossible.
- **Concrete fix:** Draw the square as the inscribed square: side = 2·140/√2 ≈ 198 → `<rect x="446" y="66" width="198" height="198">`. Then update the stitch loop to `438→446, 58→66, 214→198, 272→264, 652→644`. Alternatively, keep 215 mm to scale (`width=200.7`) and clip it with `clip-path="url(#wcl2)"`, which shows the trimmed corners honestly. `#wcl2` is already defined and unused.

### V2 [major] Left wafer shows dies larger than a reticle, partial dies, and ~76 dies under a "~60 GPUs" title
- **Location:** Figure 1, left panel (script: `for x=25..305 step 34, y=25..305 step 30`, rect 31×27, clipped by `#wcl`).
- **Problem:** At the figure's scale the dies are 33 × 29 mm (≈960 mm²). That is landscape, and larger than the 26 × 33 mm reticle and the "≤ ~800 mm²" stated in the label below. The clipPath cuts partial dies at the rim, so the reader sees 44 whole dies and 32 fragments. A fab never sells the fragments, and the count doesn't match "~60". The simulator, two screens further down, draws only whole dies (60), so the two pictures of the same wafer disagree.
- **Evidence:** Counted from the script: 44 whole, 32 partial. A grid of 26×33 mm dies with a 1 mm street, best-aligned in a 300 mm circle, gives 62 whole dies.
- **Concrete fix:** Replace the static loop with the simulator's geometry. Draw only whole dies, at the 26×33 mm reticle size, with the grid aligned to maximise count:
  ```js
  const k = 280/300, W = 26, H = 33;           // mm
  for (let x = -150-10; x < 150; x += W+1) for (let y = -150-18; y < 150; y += H+1) {
    const c = [[x,y],[x+W,y],[x,y+H],[x+W,y+H]];
    if (!c.every(([a,b]) => a*a+b*b < 150*150)) continue;
    el("rect", { x: 165+x*k, y: 165+y*k, width: W*k, height: H*k, class: "blu", "stroke-width": 1 }, dies);
  }   // → 62 whole dies, matches "~60"
  ```
  Remove `clip-path="url(#wcl)"`. Also change the simulator from `dieH = 32` to 33 so the two figures agree, or say why they differ.

### V3 [major] Right panel's reticle grid (6×6 fields of ~36 mm) contradicts the 26 × 33 mm reticle limit in the text
- **Location:** Figure 1, `#stitch` loop (`i < 6`, step 214/6).
- **Problem:** The text says one exposure is at most 26 × 33 mm. The figure divides the WSE into 6 × 6 square fields of about 38 × 38 mm, each larger than a reticle. The caption calls the dashed lines "reticle boundaries", so the reader is shown fields that cannot be printed.
- **Evidence:** The screenshot shows 6×6 square cells. 214 px × 300/280 / 6 = 38 mm.
- **Concrete fix:** Use 8 columns × 7 rows (≈26.9 × 30.7 mm per field at 215 mm, which fits a reticle; 215/26 ≈ 8.3, 215/33 ≈ 6.5). Loop `for i in 1..7` vertical lines at `x0 + i*side/8`, and `for j in 1..6` horizontal lines at `y0 + j*side/7`. Add "(field count illustrative)" to the caption, because the sources do not give the real field grid.

### V4 [major] Colours are fixed at draw time with `cssVar()` and do not follow the theme toggle
- **Location:** Script: stitch lines (`stroke: cssVar("--accent")`), the repair arrows (`cssVar("--blue")`), the power arrows (`cssVar("--amber")`) and the simulator's defect dots (`fill: cssVar("--red")`).
- **Problem:** `course.js`'s `toggleTheme()` only sets `data-theme` and fires no event. Inline colour attributes therefore keep the values from the theme the page loaded in. If you switch light→dark with the top-bar button, the dark-mode diagrams keep light-mode colours: dark-red defect dots on a dark background, and burnt-orange power arrows.
- **Evidence:** After the toggle click, `#stitch line` had `stroke="#c2410c"` while the current `--accent` was `#fb923c`. The toggle screenshots showed the dim light-palette dots and arrows on the dark surface. With `colorScheme: dark` set from the start the colours are correct, so the bug only appears after a toggle.
- **Concrete fix:** Use the existing CSS classes instead of inline colours, so the stylesheet resolves them live: stitch lines `class: "s-acc"` (drop `stroke`); repair arrows `class: "s-blu"`; power arrows `class: "s-amb"`; defect dots `class: "f-red"`. Optionally add `document.dispatchEvent(new Event("themechange"))` in `toggleTheme()` for widgets that genuinely need JS colours.

### V5 [major] All four SVGs are unreadable at phone width (rendered at 0.45×)
- **Location:** Every `figure svg` and `#y-svg` (`viewBox` 760 or 700 wide, rendered 340/324 px wide at 390 px).
- **Problem:** Text of 11–16 px in SVG units renders at 5–7 CSS px on a phone. The simulator's "GPU-sized dies: 36 of 60 hit" label and the cross-section's "I/O" labels cannot be read. Meanwhile the figcaption next to them is 14 px, which looks oversized by comparison.
- **Evidence:** Measured scale factors: 0.45, 0.45, 0.46, 0.45. The 390 px screenshots of f0–f3 show sub-legible text.
- **Concrete fix:** (a) Figures 1 and 2 are two side-by-side panels each. Split each into two `<svg>`s inside a `.grid2` (which already stacks on mobile), so each panel renders at about 0.9× on a phone. (b) In the simulator, build a separate `viewBox="0 0 330 330"` SVG per wafer and stack them with CSS `display:flex; flex-wrap:wrap`. Drop the in-SVG count labels, because `#y-out` already gives them. (c) In the cross-section, use `font-size` ≥ 18 for the layer labels so they stay ≥ 8 px. Better still, at narrow widths switch to a portrait `viewBox` (e.g. 360×420) with the layers stacked and labels beside them.

### V6 [minor] Repair schematic: the spare used in the repaired row is still drawn as an unused spare, and the arrows are ambiguous
- **Location:** Figure 2 (`#phys`).
- **Problem:** After the shift, the spare in row 2 does real work, but it is still drawn as a dashed grey box like the idle spares. The two small blue arcs sit in the 6 px gutter between rows 2 and 3, and their heads touch row 3's top edge. They read as "row 3 moves" or as decoration, not as "logical column 3 is now physical column 4". The right panel gives no correspondence (no coordinates and no highlighted row), so the reader cannot see the mapping.
- **Evidence:** Screenshot f1-1100-light: arrowheads on the row-3 boundary, and the row-2 spare still grey and dashed.
- **Concrete fix:** In the loop, render `spare && r === bad[0]` as `class:"blu"` (solid). Render the shifted cores `c > bad[1] && r === bad[0]` as `class:"blu"` too. Draw the logical row 2 in the right panel `class:"blu"` as well, so the colours carry the mapping. Write small mono labels (`font-size 10`) of the logical x inside each core of row 2 on both sides: physical cells read `0 1 2 ✕ 3 4`, logical cells read `0 1 2 3 4`. Move the arcs above the row (`y = 40 + bad[0]*(S+6) - 4`, curve `q … -10 …`) so they do not touch row 3. Add a legend line: "solid green = core in use · dashed = idle spare · blue = remapped".

### V7 [minor] Cross-section: power arrows have blue heads, and "heat out below / data out the sides" is not drawn
- **Location:** Figure 3.
- **Problem:** (a) The power arrows reuse marker `#ar3`, whose head is `class="f-blu"`, so amber shafts end in blue heads. (b) The caption promises "heat out below" and "data out the sides", but there are no heat arrows and no arrows from the wafer to the I/O blocks. (c) The custom thermal-expansion connector named in the text is missing. (d) About 40 px of the 260 px viewBox below the note is empty.
- **Evidence:** Screenshots f3 (both themes): orange shafts with blue arrowheads, and nothing below the cold plate.
- **Concrete fix:** Add `<marker id="ar-amb" …><path … class="f-amb"/></marker>` and use it for `#pwr`. Add a thin `class="box"` layer between power and wafer, labelled "compliant connector (lets the wafer expand)". Below the cold plate add 3 downward `s-blu` wavy arrows labelled "heat → water loop". Add short horizontal `s-grn` arrows from the wafer ends to each I/O box. Change the viewBox height to 250 and place the note at y=240. Keep "Schematic only".

### V8 [minor] Simulator: dragging the slider re-randomises everything, so density changes are not comparable
- **Location:** `$("#y-d").oninput = roll`.
- **Problem:** Every slider tick draws a new random field. Moving from 0.0010 to 0.0011 can *lower* the hit count, which defeats "move the slider and watch losses grow".
- **Evidence:** Driven with Playwright: consecutive ticks produced non-monotonic die-hit counts. The visible pattern jumps completely on each tick.
- **Concrete fix:** Pre-generate a fixed pool of 250 uniformly placed points (enough for 0.003 × 70,686 mm² = 212) when the page loads and on Re-roll. Then `draw()` uses `defects = pool.slice(0, n)`. Bind `oninput = draw` and keep `onclick = roll` for the button. Losses then grow smoothly as the slider moves right.

### V9 [minor] Simulator readout contradicts the vendor number the next paragraph quotes, and doesn't say why
- **Location:** `#y-out`, and the paragraph after the widget ("The simulator above makes the same point with your own numbers").
- **Problem:** At 0.001/mm² the simulator reports about 30,000 mm² of GPU dies discarded against about 2.3 mm² on the WSE, a ratio of about 13,000×. The paragraph quotes the vendor's 164×. The difference is in the accounting: 2.2 mm² × 164 ≈ 361 mm², or about 7.8 mm² per defect, which looks like "disable one SM" (binning) rather than "discard the die" (this is my inference). A reader who compares the two numbers is left confused.
- **Concrete fix:** Add a two-way toggle `GPU accounting: [discard whole die] [disable hit SM ≈ 7.8 mm², vendor-style]`, and print the ratio line `dead silicon ratio GPU : WSE = N×`. Tag the 7.8 mm² as `<span class="tag derived">Derived from vendor 164×</span>`.

### V10 [minor] Simulator polish: label collisions, a11y, mobile readout
- **Location:** `#y-svg` labels at y=325, `#y-out`.
- **Problem:** At high density, defect dots near the wafer bottom (y up to 315) collide with the count labels (seen at 0.003). The GPU die grid is anchored at (−150,−150), not centred, so the layout is lopsided: one lone die at the bottom and one at the right. `#y-out` has no `aria-live`. At 390 px the space-aligned `pre` readout wraps mid-line ("29,952 mm² discarded" breaks), which spoils the alignment.
- **Concrete fix:** Change the viewBox height to 345 and the labels to y=338. Offset the grid with the best-aligned offsets (x −160, y −168 for 26×33). Add `aria-live="polite"` to `#y-out`. Replace the readout with a 3-row `<table class="mono">` (defects / GPU / wafer-scale) that wraps cleanly.

## Proposed new visuals (prioritised)

### N1 Yield vs area curve (the core argument in one plot). Priority 1
- **Purpose:** The "Surviving defects" section argues in prose that a small unit of failure saves the wafer. A plot of the yield curve shows why a monolithic wafer is hopeless and a tiny core is safe.
- **Content/data:** Log-x axis of die area, 0.01 → 100,000 mm². Y axis: probability that a unit is defect-free, `Y = exp(−D·A)` (Poisson) <span class="tag derived">Derived</span>. Marked points: WSE core 0.05 mm² (Y≈0.99995), H100 SM ≈ 6 mm², H100 die 814 mm² (Y≈0.44 at D=0.001), one B200 die about 800 mm², and the whole WSE treated as monolithic 46,225 mm² (Y ≈ 8×10⁻²¹; label it "≈ 0 — needs redundancy"). A secondary readout gives the expected dead area per wafer for each unit size (D·A_wafer·A_unit).
- **Interaction:** A density slider shared with the simulator (move `#y-d` and the curve redraws), and hover on a point to see its numbers. Implement it as `figure.widget` with one SVG of 700×300 and a log axis built by hand with `el()`.
- **Placement:** Right after the "Surviving defects" paragraph, before the repair schematic.

### N2 Where the 850k cores go: marketed → fabric → your rectangle. Priority 2
- **Purpose:** The stat tile "~737k" and the I/O paragraph explain a three-step loss in prose. The reader never sees the geometry of 750×994 or the 7-column/2-row margin.
- **Content/data:** A to-scale nested rectangle of the 750 × 994 fabric (745,500 positions) <span class="tag sdk">SDK 2.10.1</span>, inside a ghost outline for the 850,000 marketed cores (the area difference is labelled "spares + not exposed, breakdown unpublished"). Within the fabric: west memcpy columns (4, from `--fabric-offsets=4,1`) and east columns (3), plus 1 row at the top and 1 at the bottom, with the remaining user rectangle of ≈743 × 992 ≈ 737k <span class="tag derived">Derived</span>. Waterfall bars beside it: 850,000 → 745,500 → ≈737,000. The margins are a few pixels wide at scale, so add a zoomed callout of the north-west corner where the 4 west columns and the offset row are drawn as individual PEs.
- **Interaction:** Hover each region for its count and source. A toggle "show memcpy west/east roles" labels the columns cmd-fan / demux (west) and mux (east), linking ahead to Chapter 7.
- **Placement:** Replace or sit under the "I/O lives on the rim" paragraph. This also fixes the pedagogy concern that the rim causes the margin: the picture attributes the margin to memcpy.

### N3 What the wafer buys: a link-bandwidth ladder. Priority 3
- **Purpose:** The chapter never shows the benefit (pedagogy P1). A log-scale ladder compares on-wafer bandwidth with the links a GPU system has to cross.
- **Content/data:** Horizontal log bars (TB/s): H100 NVLink ≈ 0.9; B200 die-to-die NV-HBI 10 <span class="tag vendor">Vendor</span>; WSE-3 fabric 214 Pb/s ≈ 27,000 TB/s <span class="tag vendor">Vendor</span>; WSE-3 memory 21 PB/s = 21,000 TB/s <span class="tag vendor">Vendor</span>; H100 HBM 3.35 TB/s <span class="tag vendor">Vendor</span>. Annotate the bars with the multiplier relative to NVLink.
- **Interaction:** Toggle "per chip" / "per mm² of silicon", dividing by die area (814 vs 46,225 mm²), so the learner can see how much of the gain is just size. Use the dataviz palette, with tags on hover.
- **Placement:** In a new "What the wafer buys" section after Figure 1.

### N4 Dense-FLOPs calculator. Priority 4
- **Purpose:** The callout's arithmetic (cores × SIMD × 2 × clock) is prose, and the clock is the disputed input. A calculator shows how much the conclusion depends on it.
- **Content/data:** Generation selector: WSE-2 (850k, 4-wide FP16), WSE-3 (900k, 8-wide). Clock slider 0.6–1.2 GHz, with a tick at 850 MHz labelled "SDK benchmark assumption <span class="tag sdk">SDK 2.10.1</span>". Output: dense PF = cores × width × 2 × f. Reference lines on a small bar: analyst 7.5 PF (WSE-2) or 15.6 PF (WSE-3), and the vendor's 125 PF sparse as a hatched bar labelled "sparse, not comparable". At 850 MHz WSE-3 gives ≈12.2 PF; at 1 GHz, 14.4 PF.
- **Interaction:** Slider plus radio buttons, live readout, no randomness.
- **Placement:** Directly under the "Read the FLOPs carefully" callout.

### N5 Powers-of-ten zoom: wafer → reticle field → core. Priority 5
- **Purpose:** "0.05 mm², 1/100 of an SM" and "57× an H100" are hard to picture. A to-scale zoom makes the size ratios physical.
- **Content/data:** Four stops, each a to-scale square: WSE 215 mm with an H100 die (≈28.5 mm side, 814 mm²) overlaid, and 57 of them tiled ghosted; one reticle field 26×33 mm; one H100 SM ≈ 2.4 mm side; one WSE core ≈ 0.22 mm side (0.05 mm²; note the alternative 38,000 µm² figure). Scale bar on each stop.
- **Interaction:** Four buttons or a scroll-scrubbed slider that animates `viewBox` between the stops (CSS transition on a `<g transform>`), respecting `prefers-reduced-motion`.
- **Placement:** In the lede area or right after the reticle paragraph, before Figure 1.

### N6 Spare-budget extension to the defect simulator. Priority 6
- **Purpose:** The prose implies redundancy always works. The real constraint is that spares are finite and local, and clustered defects can exhaust them. This also makes the "spare ratio is unpublished" caveat concrete.
- **Content/data:** A zoomed panel of a 40×40 core patch with one spare column per K rows (a hypothetical scheme, labelled as such). Defects are drawn from the same density, with an optional clustering parameter (negative-binomial α). Show repaired rows in blue and unrepairable rows in red. Count "wafer unusable if any row needs > s spares".
- **Interaction:** Sliders for spares per row (0–3) and for clustering. A Re-roll button. A readout of P(repairable) over 500 trials.
- **Placement:** As a second tab of the existing `#yield` widget, or immediately after it.

### N7 Generation small multiples. Priority 7
- **Purpose:** The spec table hides the trend: the same area every generation, with growth in other columns.
- **Content/data:** Four mini bar charts over WSE-1/2/3/3T: transistors (1.2/2.6/4/4 T), cores (400k/850k/900k/900k), SRAM (18/40/44/44 GB), memory BW (–/20/21/43.2 PB/s). A constant-area strip of 46,225 mm² across the top. Missing values are shown as hollow bars with "not published".
- **Interaction:** Hover a generation to highlight its column in the table (`tr td:nth-child`).
- **Placement:** Directly above the spec table.

### N8 Stitching close-up. Priority 8
- **Purpose:** "Wires across the scribe lines" is abstract. A close-up shows what is different from a normal wafer.
- **Content/data:** Two adjacent reticle fields with a scribe line between them. Normal wafer: the fabric links stop at the field edge, and a saw path runs through the line. WSE: links continue across. A toggle switches between "diced" and "stitched". All dimensions are labelled illustrative, because the sources give no wire pitch or count.
- **Interaction:** One toggle, with an animated wavelet dot crossing (or stopping at) the boundary.
- **Placement:** Inset beside Figure 1, or replacing its right-panel caption text.
