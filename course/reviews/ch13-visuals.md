# ch13 · visuals review

Summary: The chapter has one static SVG (Tensix core anatomy) and one widget (circular-buffer timeline). The page itself works: it renders cleanly at 1100 px and 390 px, in light and dark, with no console errors and no horizontal page scroll. The widget's teaching claim is wrong, though. Because of an off-by-one in its event model, CB size 1, 2 and 4 all finish at **t = 29**, so the control does nothing. That contradicts the widget's own text, which says size 1 makes the stages serialise. Other problems: on a phone both graphics shrink to unreadable text (labels end up about 5 px tall). The timeline colours are captured once at render time, so they go stale when the theme is toggled, and in dark mode the bar labels fail contrast. The anatomy figure shows boxes but no data flow. The chapter has no chip-level or tile-flow visual at all, and the Tensix-vs-PE comparison is only a table.

Method: Playwright/Chromium at 1100×900 and 390×900, colorScheme light and dark. Full-page and per-element screenshots. Each CB option was selected and the readout captured. The ◐ theme toggle was clicked and the widget re-captured. Contrast was computed with the WCAG formula from course.css tokens. The simulator was re-run in Node to check the corrected model. Screenshots were deleted afterwards.

## Findings (defects in existing visuals)

### V1 [critical] Circular-buffer size has no effect on the timeline
- **Location:** `13-tenstorrent.html`, inline script, `sim()`: the lines computing `rStart` and `cStart`.
- **Problem:** A slot is freed at the moment the consumer *starts* (`cp[k-cap][0]`, `wr[k-cap][0]`). In TT-Metalium a slot is freed only when the consumer calls `cb_pop_front`, after it has *finished* with the tile. For the writer, that is after `noc_async_write_barrier`. Freeing at start gives even a 1-slot buffer full overlap. Because all stage durations are also constant (3/3/2), sizes 2 and 4 cannot differ either. The readout text for size 1 ("stages serialise") is contradicted by the bars directly above it.
- **Evidence:** I captured the readout in Playwright for each option:
  - `CB size 1: 8 tiles finish at t = 29`
  - `CB size 2: … t = 29`
  - `CB size 4: … t = 29`

  The screenshot for size 1 shows the same perfectly pipelined bars as size 2.
- **Concrete fix:** Free each slot at the consumer's end. Add an optional "DRAM jitter" row of reader durations so that deeper buffers visibly absorb latency spikes. Scale the axis to the data. Draw CB occupancy. Use theme classes instead of baked colours. I re-ran this model in Node:

  | Reader durations | Size 1 | Size 2 | Size 4 |
  |---|---|---|---|
  | Constant (3/3/2) | 50 | 29 | 29 |
  | Jitter `[2,2,9,2,2,2,9,2]` | 56 | 40 | 36 |

  Replacement HTML controls (inside `#cb .controls`):
  ```html
  <label>CB size <select id="cb-n"><option value="1">1 tile</option><option value="2" selected>2 tiles</option><option value="4">4 tiles</option></select></label>
  <label><input type="checkbox" id="cb-jit"> DRAM latency spikes</label>
  ```
  (Drop the "Run 8 tiles" button; it only re-runs the same deterministic render. See V5.)

  Replacement for `sim()` and its wiring:
  ```js
  function simulate(cap, R, C, W) {
    const N = R.length, rd = [], cp = [], wr = [];
    for (let k = 0; k < N; k++) {
      // reader: cb_reserve_back(cb_in) waits until compute has cb_pop_front'ed tile k-cap (i.e. FINISHED it)
      const rs = Math.max(k ? rd[k-1][1] : 0, k >= cap ? cp[k-cap][1] : 0);
      rd.push([rs, rs + R[k]]);
      // compute: cb_wait_front(cb_in) + cb_reserve_back(cb_out) — out slot frees when writer finished tile k-cap
      const cs = Math.max(rd[k][1], k ? cp[k-1][1] : 0, k >= cap ? wr[k-cap][1] : 0);
      cp.push([cs, cs + C[k]]);
      const ws = Math.max(cp[k][1], k ? wr[k-1][1] : 0);
      wr.push([ws, ws + W[k]]);
    }
    return { rd, cp, wr, end: wr[N-1][1] };
  }
  function sim() {
    const cap = +$("#cb-n").value, jit = $("#cb-jit").checked;
    const R = jit ? [2,2,9,2,2,2,9,2] : Array(8).fill(3), C = Array(8).fill(3), W = Array(8).fill(2);
    const { rd, cp, wr, end } = simulate(cap, R, C, W);
    const serial = R.concat(C, W).reduce((a, b) => a + b, 0);
    const svg = $("#cb-svg"); svg.innerHTML = "";
    const T = 60, X = v => 80 + v * 580 / T;            // fixed 0..60 axis so runs are comparable
    [["reader", rd, "blu", 20], ["compute", cp, "acc", 70], ["writer", wr, "grn", 120]].forEach(([n, arr, c, y]) => {
      el("text", { x: 4, y: y + 22, "font-size": 13 }, svg).textContent = n;
      arr.forEach(([a, b], k) => {
        el("rect", { x: X(a), y, width: Math.max(1, X(b) - X(a) - 1), height: 34, rx: 3, class: c, "stroke-width": 1.2 }, svg);
        el("text", { x: (X(a) + X(b)) / 2, y: y + 22, "text-anchor": "middle", "font-size": 12, "font-weight": 600 }, svg).textContent = k;
      });
    });
    // CB_in occupancy strip: tiles produced but not yet consumed
    for (let t = 0; t < end; t++) {
      const occ = rd.filter(([, e], k) => e <= t && cp[k][1] > t).length;
      el("rect", { x: X(t), y: 166, width: X(t + 1) - X(t), height: 10, class: occ >= cap ? "acc" : "box", opacity: occ ? 1 : .35 }, svg);
    }
    el("text", { x: 4, y: 175, "font-size": 11, class: "muted" }, svg).textContent = "CB_in full";
    for (let t = 0; t <= T; t += 10) {
      el("text", { x: X(t), y: 196, "font-size": 11, "text-anchor": "middle", class: "muted" }, svg).textContent = t;
    }
    el("line", { x1: X(end), x2: X(end), y1: 14, y2: 182, class: "s-red", "stroke-dasharray": "4 3", "stroke-width": 1.5 }, svg);
    el("text", { x: Math.min(X(end) + 4, 600), y: 12, "font-size": 12 }, svg).textContent = `done t=${end}`;
    $("#cb-out").textContent =
      `CB size ${cap}: 8 tiles finish at t = ${end} (fully serial would be ${serial}).\n` +
      (cap === 1 ? "One slot: the reader cannot reserve tile k+1 until compute pops tile k, so read and compute alternate."
       : jit && cap === 2 ? "Two slots hide steady latency, but a DRAM spike still stalls compute. Try 4."
       : "Enough slots: compute (the slowest stage) never waits, so it sets the finish time.");
  }
  $("#cb-n").onchange = sim; $("#cb-jit").onchange = sim; sim();
  ```
  Also update the hint text to say "a slot is freed only when the consumer pops it".

### V2 [major] Both graphics are illegible at phone width
- **Location:** `figure svg` (viewBox 760×380) and `#cb-svg` (680×200).
- **Problem:** At 390 px, the anatomy SVG renders 340×170 (scale 0.45) and the timeline renders 324×95 (scale 0.48). The 11–12 px labels ("RV32IM", "data movement", "reads (convention)", tile numbers, "done at t=29") come out at about 5 px.
- **Evidence:** Element screenshots `el0-390-light` and `el1-390-dark`: the text is a blur, and the timeline is a thin strip.
- **Concrete fix:**
  - **Timeline:** wrap it in `<div style="overflow-x:auto">` and give the SVG `style="min-width:560px"`. Alternatively, after V1's fixed axis, render a narrow viewBox (`0 0 360 260`) when `innerWidth < 600`, with lanes stacked taller and labels at 13 px.
  - **Anatomy figure:** provide a portrait layout for small screens via `<picture>`-style swapping: two `<svg>` elements, one shown with `@media (max-width:600px)`. The portrait version should be a 2-column grid of RISC-V boxes, NoC boxes below the core, and viewBox around 380×620. A cheaper fix is `min-width:600px` inside an `overflow-x:auto` wrapper.

### V3 [major] Timeline colours freeze at first render and fail contrast in dark mode
- **Location:** `sim()` uses `fill: cssVar(c)` with `opacity: .8` and `fill: "#fff"` labels.
- **Problem:**
  - The colours are resolved once. After the ◐ toggle (which only changes `data-theme`), the bars keep the other theme's palette. After toggling dark to light, the bars stay pastel dark-mode colours on a white card.
  - White 10 px labels on the bars fail WCAG AA in every case. In dark mode, white on `--green` #4ade80 at 0.8 is **2.54:1**, `--accent` is 3.23:1 and `--blue` is 3.49:1. In light mode, `--green` is 3.49:1 and `--accent` is 3.73:1.
- **Evidence:** Screenshot `cb-toggled.png`: the page is in light theme with dark-palette bars. Contrast was computed from the course.css tokens.
- **Concrete fix:** Use the existing SVG classes `blu`, `acc` and `grn` (soft fill plus strong stroke, as in the anatomy figure). Use default `svg text` fill (`var(--text)`) for the labels, as in the V1 code. CSS then handles theme switches with no re-render. Raise the label size to 12 px. If solid fills are kept, use a `#111` label: 5.4–7.4:1 on all six fills. Also redraw on theme change, via a `MutationObserver` on `documentElement[data-theme]`.

### V4 [major] Anatomy figure shows parts but no flow, and the NoC arrows mislead
- **Location:** The "Inside a Tensix core" figure.
- **Problem:**
  - The five RISC-V boxes are not connected to anything. There is no arrow showing that BRISC/NCRISC drive the NoC, or that TRISC0/1/2 issue instructions to the unpackers, FPU/SFPU and packers.
  - L1 → unpack → FPU/SFPU → Dst → pack → L1 is not drawn. The Dst register, which the bullet list mentions (8 BF16 / 4 FP32 tiles), is absent.
  - Both NoC arrows point one way, out of L1. NoC 0 is labelled "reads", yet its arrow points *out* of L1.
  - The NoC boxes sit outside the dashed core boundary, although each core has its own two router ports.
- **Evidence:** Screenshots `el0-1100-light` and `el0-1100-dark`. The figure's own caption says "TRISC0/1/2 drive the unpack → math → pack pipeline", but nothing in the drawing shows it.
- **Concrete fix:**
  - Add thin control arrows: each TRISC down to its stage (TRISC0 → unpackers, TRISC1 → FPU+SFPU, TRISC2 → packers). Add BRISC and NCRISC → their NoC router.
  - Add a thick data path. L1 feeds down to the unpackers. Between the FPU/SFPU and the packers, insert a "Dst regs (8×BF16 / 4×FP32 tiles)" box. The packers feed back up to L1, drawn as an arrow along the right edge of the coprocessor.
  - Make both NoC links double-headed (`marker-start` too). Change the sub-labels to "BRISC reads in (conv.)" and "NCRISC writes out (conv.)".
  - Move the two router boxes onto the dashed boundary so they read as ports of this core. Extend the viewBox width to about 780 if needed.
  - Colour-code control (dashed, muted) versus data (solid, accent), with a two-item legend.

### V5 [minor] "Run 8 tiles" button is redundant, and the widget has no axis
- **Location:** `#cb-go`; `#cb-svg`.
- **Problem:**
  - The button re-renders the identical deterministic chart, since the select already triggers `sim` on change. Clicking it appears to do nothing.
  - There is no time axis, and the fixed 0–60 scale leaves the right half of the plot empty (end = 29).
  - The tile label "7" on the writer lane abuts the dashed "done" line.
- **Evidence:** Screenshots `cb-1` and `cb-2`.
- **Concrete fix:** Either remove the button or make it animate: reveal bars progressively with a `requestAnimationFrame` cursor over t. Add ticks every 10 units, as in the V1 code. Put the "done" label above the plot rather than below the last bar.

### V6 [minor] Anatomy figure: low-weight sub-labels in dark mode
- **Location:** The `muted` 11 px texts ("RV32IM", "reads (convention)", "two 2-D torus networks…").
- **Problem:** These are readable at 1100 px in both themes (#a2a7b4 on #1d2a4a is about 5.5:1). They depend on V2's mobile fix, though. The side note "two 2-D torus networks, opposite directions" floats unattached under NoC 1 and reads as if it belongs only to NoC 1.
- **Evidence:** Screenshot `el0-1100-dark`.
- **Concrete fix:** Put the note in a bracket spanning both NoC boxes, or move it into the caption.

No console errors or warnings were seen in any of the 4 renders. There is no horizontal page scroll at 390 px: `scrollWidth` equals `clientWidth`, and the tables scroll inside `.table-wrap` as designed.

## Proposed new visuals (prioritised)

### N1 (high) Blackhole chip floorplan with the two NoC tori, interactive
- **Purpose:** The chapter never shows the *chip*. Learners cannot see where Tensix, DRAM, Ethernet and RISC-V/PCIe tiles sit, or how NoC 0 and NoC 1 wrap. This visual anchors the comparison with the wafer's uniform PE mesh in ch02/ch04.
- **Content:**
  - A grid of the Blackhole tile array, 17 columns × 12 rows of NoC nodes per tt-isa-documentation / tt-metal `blackhole` soc descriptor. The reviewer of the accuracy angle should verify the grid size against the soc descriptor YAML before drawing.
  - Tensix tiles in accent. Of the 140 physical Tensix tiles, 120 are enabled after the Feb 2026 firmware; draw the 20 disabled ones hatched.
  - The DRAM controller columns (8 GDDR6 channels, 32 GB, ~512 GB/s) at the edges in green.
  - A row of 14 Ethernet tiles in blue, and the PCIe, ARC and L2CPU tiles labelled.
  - Every number carries a `vendor` tag.
- **Interaction:**
  - A toggle "NoC 0 / NoC 1 / both": arrows on each row and column show direction (NoC 0 east/south, NoC 1 west/north), with the wrap-around link drawn as a curved edge so the torus is visible.
  - Clicking two tiles draws the dimension-order route on the selected NoC and reports hops × ~9 cycles.
  - Hovering a tile shows its type and coordinates.
- **Placement:** New subsection "The chip" between the product table and "Inside a Tensix core".

### N2 (high) One tile's journey: DRAM → L1 → unpack → FPU → pack → L1 → DRAM
- **Purpose:** Connect the anatomy figure to the reader/compute/writer code model. Make concrete what "the RISC-V cores issue work, not compute it" means.
- **Content:**
  - A horizontal strip of stations. GDDR6 → (NoC 0, BRISC `noc_async_read_tile`) → L1 CB_in (`cb_push_back`) → unpacker (TRISC0, `cb_wait_front`) → SrcA/SrcB → FPU `matmul_tiles` (TRISC1) → Dst register → packer (TRISC2, `pack_tile`) → L1 CB_out → (NoC 1, NCRISC `noc_async_write_tile`) → GDDR6.
  - Show each station's data format: 32×32 BF16 = 2,048 B in L1. Unpack can convert to the FP32/TF32 source format. Show bfp8_b with its shared exponent per 16 values.
- **Interaction:** Step / Play buttons move a single 32×32 tile glyph along the strip. At each step, a side panel highlights which RISC-V core is active and the one-line API call. A "format" select (BF16 / bfp8_b) changes the byte counts shown.
- **Placement:** Directly after the anatomy figure, before "Programming: reader, compute, writer". It then leads into the CB widget.

### N3 (high) Side-by-side: the same op on Tensix vs Cerebras PEs
- **Purpose:** Replace the purely tabular comparison with a visual of *grain*, the section's key message.
- **Content:** Use one GEMV y = W·x with W of 4096×4096 BF16, about 32 MiB.
  - **Left (Blackhole):** W lives in GDDR6 (32 MiB ≪ 180 MB SRAM, but streamed for decode). Each of the 120 Tensix cores gets about 34 row-blocks of 32×4096 tiles. Each core streams its tiles from DRAM via its reader kernel, then partial results are written out. Annotate the bandwidth ceiling: 32 MiB / 512 GB/s ≈ 65 µs, `derived`.
  - **Right (WSE-3):** W is pre-placed across a PE rectangle, e.g. 512×512 PEs with about 128 B of W each, using the same row/column decomposition as ch12/ch15. x is broadcast along rows as wavelets and partials are reduced along columns. There is no DRAM in the path.
  - Below each side, a mini bar compares "bytes moved from off-chip per token", "units in use" and "data granule" (2 KB tile vs 4 B wavelet).
- **Interaction:** A slider for matrix size (1k–16k), updating per-core tile count, per-PE bytes and the DRAM-time estimate.
- **Placement:** Top of "Tensix vs the Cerebras PE", above the table.

### N4 (medium) CB widget: add a stage-occupancy / stall view
- **Purpose:** Make the reason the buffer matters visible, not just the end time.
- **Content:** Below the lanes, two occupancy strips (CB_in and CB_out slots, 0..cap) and red hatching where a stage is *blocked*: reader blocked on `cb_reserve_back`, compute on `cb_wait_front`. A partial version is already in the V1 code (the CB_in strip).
- **Interaction:** Sliders for reader/compute/writer durations, alongside the jitter checkbox, so learners can make the reader the bottleneck and see that a bigger CB does not help.
- **Placement:** Extends the existing `#cb` widget.

### N5 (medium) Galaxy mesh scale-out diagram
- **Purpose:** Show "Ethernet on every die, switchless meshes" against Cerebras' MemoryX/SwarmX picture from ch08.
- **Content:**
  - An 8×4 grid of 32 Blackhole chips with Ethernet links to their neighbours (vendor: 8 × 4 mesh).
  - Totals beside it: 6.2 GB SRAM, 1 TB GDDR6, 16 TB/s, 23 PF BlockFP8, all `vendor`.
  - An overlay showing how a 70B BF16 model (about 140 GB) spreads at about 4.4 GB per chip. That fits in GDDR but not in SRAM, which is the visual answer to quiz question 3.
- **Interaction:** Hover a chip to see its links. A toggle between "weights in SRAM?" and "weights in GDDR6" colours the chips by fit.
- **Placement:** "Performance and caveats", before the Llama/DeepSeek bullets.

### N6 (low) Tile and block-float format glyph
- **Purpose:** The "Everything is a 32×32 tile" and "Block floating point" bullets are abstract.
- **Content:**
  - A 32×32 grid split into its four 16×16 faces (the actual L1 tile layout).
  - A bfp8_b zoom: 16 mantissas sharing one exponent byte. Per tile, BF16 = 2,048 B vs bfp8_b = 1,088 B vs bfp4_b = 576 B (`derived`, include formula).
- **Interaction:** None needed, or a format toggle.
- **Placement:** Beside the bullet list after the anatomy figure.
