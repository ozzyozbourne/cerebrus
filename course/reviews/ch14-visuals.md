# ch14 · visuals review

Chapter 14 (`course/14-gpu.html`) has only two visuals: a static memory-hierarchy SVG and the occupancy widget. Both render with no console errors at 1100px and 390px, in light and dark. Neither one teaches as much as it should.
- **Hierarchy diagram:** bar width encodes nothing that is stated, the side labels overlap the bars, and the text drops to about 5px on a phone.
- **Occupancy widget:** it never draws the memory wait (the thing it is meant to show), and it prints two utilisation numbers that disagree.
- **Slider range:** it cannot reach "latency hidden" across most of its range, and it suggests impossible warp counts.
- **Theme toggle:** both visuals bake in colours at load, so they keep stale colours after the theme is toggled.

The chapter promises SM anatomy, SIMT, coalescing and grid/block mapping, but it has no picture of any of them. That is the largest gap.

Method: Playwright/Chromium at 1100×900 and 390×900, `colorScheme` light and dark, full-page shots plus element shots of `figure`, `#occ` and `.grid2`. I also clicked the top-bar theme toggle, and drove the sliders through edge cases: (W,C,L) = (1,2,20), (16,2,400), (16,40,20), (4,10,100), (3,10,100), (1,40,400), (11,10,100), (16,2,20). No console errors or page errors appeared in any configuration. The page has no horizontal scroll at 390px (scrollWidth = clientWidth = 390).

## Findings (defects in existing visuals)

### V1 [major] Occupancy timeline never draws the memory-wait phase, so latency hiding is invisible
- **Location:** `#o-svg`, `occ()` lines 137–142.
- **Problem:** The widget draws only the compute bars (accent) and the "SM busy" strip. The L cycles each warp spends waiting are blank, exactly like the time when a warp is simply not scheduled. Idle gaps in the "SM busy" row are also blank rather than marked. So the learner sees scattered orange squares, not "warp 0 waits while warps 1–3 compute."
- **Evidence:** The 1100-light default (W=4, C=10, L=100) shows six diagonal staircases of 4 tiny squares, separated by about 100px of empty space. Nothing is labelled "waiting on memory." The 16/2/400 case shows two thin diagonal hairlines.
- **Concrete fix:** For each `busy` entry `[w,a,b]`, also draw a wait bar from `b` to `min(b+L,T)` in the same row, with `class="amb"` (amber-soft fill, amber stroke) and a label "waiting on HBM". Draw stall gaps in the SM-busy row as `red`-soft rects labelled "idle". Add a three-item legend above the plot: compute, waiting, idle.

### V2 [major] Simulated utilisation and model utilisation disagree (40% vs 36%)
- **Location:** `occ()` lines 131–135 and 143–145.
- **Problem:** All warps start ready at t=0, so the first round adds a cold-start burst, and the 600-cycle window is short compared with C+L (up to 440). The "simulated" figure therefore overstates the steady state, and the readout shows two different numbers side by side with no explanation.
- **Evidence:** Readouts for each (W,C,L), simulated vs model:

  | W | C | L | Simulated | Model |
  |---|---|---|---|---|
  | 4 | 10 | 100 | 40% | 36% |
  | 1 | 40 | 400 | 13% | 9% |
  | 16 | 2 | 400 | 11% | 8% |
  | 3 | 10 | 100 | 30% | 27% |
- **Concrete fix:** Measure only in steady state. Simulate to T=3000, and count `issued` only for t ∈ [T−600, T). Draw that same window, so the plot and the number agree. Alternatively, keep one number: report the model value, and label the drawing "first 600 cycles". Do not show two percentages.

### V3 [major] Slider ranges and recommendations ignore hardware limits; quiz contradicts H100 limits
- **Location:** `#o-w` max=16, readout line 145, quiz question 2 (line 111).
- **Problem:** "Warps needed" reaches 201 (C=2, L=400) and the widget says "add 185 more warps," which is physically impossible. An H100 SM holds at most 64 warps (2,048 threads), which is 16 per warp scheduler. The widget also says "the SM's scheduler," but an H100 SM has four schedulers. The model is per-scheduler, which is the right model, but the label is wrong.
  - The quiz answer "21 warps per scheduler" is above the 16-per-scheduler cap. That is a teachable moment, but the page never makes it.
  - With the default C=10 and L=100, the full slider range never shows "✓ latency hidden" unless C is also raised. For most settings the widget can only show failure.
- **Evidence:** Case (16,2,400) gives "warps needed … = 201 — add 185 more warps". Case (4,10,100) needs 11.
- **Concrete fix:**
  1. Relabel the hint to "one of the SM's four warp schedulers."
  2. Keep max=16, and when `need > 16` print: "needs N warps; one H100 scheduler holds at most 16 (64/SM). Real kernels close the gap with several independent loads in flight per warp (ILP) or async copies (cp.async/TMA)."
  3. Optionally add a "loads in flight per warp" control k (1–4), which turns the requirement into ⌈(C+L)/(k·C)⌉ approximately.
  4. Change the default to W=6, C=20, L=100 (need = 6), so the first view shows the success state.
  5. Edit the quiz answer to note that 21 > 16, so this needs ILP.

### V4 [major] Both visuals shrink below legibility at phone width
- **Location:** Hierarchy SVG (viewBox 760, font 12 muted) and `#o-svg` (viewBox 680, labels font 9/10).
- **Problem:**
  - The hierarchy SVG scales to 324/760 = 0.43, so its 12px detail lines render at about 5px and the 15px titles at about 6.5px. The "fast, small" and "slow, big" labels are roughly 4px.
  - The occupancy SVG scales by 324/680 = 0.48, so the "warp k" labels (9px) render at about 4.3px and "SM busy" at about 4.8px.
  - At 1100px the 9px warp labels are already small.
- **Evidence:** In `hier-390-light.png` the bar text is unreadable. In `occ-390-dark.png` the warp labels are unreadable smudges.
- **Concrete fix:**
  - **Hierarchy:** Add a narrow layout. When `innerWidth<680`, rebuild with viewBox 380×420, stacked full-width bars with two text lines each, and side labels above and below rather than at the left. Or draw it as an HTML `<div>` stack, which reflows naturally.
  - **Occupancy:** Use viewBox 680 with 13px labels on desktop. On mobile set the viewBox to 400 wide and label rows "w0…w15" at 12px.

### V5 [major] Hierarchy bar widths encode nothing stated; the metaphor is inverted
- **Location:** `levels` widths 680/560/400/260, line 119; caption "wide at the top, narrow at the bottom."
- **Problem:**
  - Width falls from registers to HBM while capacity rises from 256 KB to 80 GB, and the left labels say "fast, small" and "slow, big." A reader naturally reads width as size, so the shape says registers are the biggest.
  - Presumably width means bandwidth, but no bandwidth is given for registers or L1, and the units are mixed (per-SM for registers and L1, per-chip for L2 and HBM).
  - Latencies are qualitative ("tens of cycles", "hundreds of cycles"), which is weak for a chapter about hiding latency.
- **Evidence:** In the screenshot, the widest bar ("registers") is labelled 256 KB and the narrowest ("HBM3") is labelled 80 GB.
- **Concrete fix:** State the encoding: "width ∝ log(aggregate bandwidth)". Show chip-wide aggregates on every row:
  - Registers: 132 × 256 KB ≈ 33 MB chip-wide, about 1 cycle.
  - L1/shared: 33 MB chip-wide, about 30 cycles.
  - L2: 50 MB, about 200–270 cycles, about 3.8 TB/s (Indep).
  - HBM3: 80 GB, about 450–600 cycles, 3.35 TB/s (Vendor).

  Tag each latency, citing the Chips and Cheese H100 measurements (Indep), and confirm the exact cycle counts against `research_notes/.../gpu_and_comparison.md` before use.

  Then add a right-hand column "capacity" with a bar ∝ log(bytes), so the two opposing trends are both explicit. Change the caption to "Fast storage is tiny; big storage is far away". The interesting fact that chip-wide RF + L1 ≈ 66 MB is larger than L2 can then be called out.

### V6 [minor] "fast, small" / "slow, big" labels collide with the bars
- **Location:** Lines 125–126, text at x=20; the register bar starts at x=40.
- **Problem:** "fast, small" runs about 35px into the registers rectangle, and "slow, big" sits beside the HBM bar at a different height than intended (y=250 vs bar centre 244).
- **Evidence:** `hier-1100-light.png`: "fast, small" overlaps the left edge of the registers bar.
- **Concrete fix:** Replace the two labels with a vertical arrow at x≈24 running from y=20 to y=270, labelled "latency ↑" (rotated text), or place them at x=20, y=12 and y=294, above and below the stack. If V5 is done, use explicit column headers instead.

### V7 [minor] Theme toggle leaves stale colours in both SVGs
- **Location:** `cssVar()` calls at lines 122, 140, 141. The toggle in `course.js` lines 26–31 dispatches no event.
- **Problem:** Fills and strokes are read from CSS variables once, at render time. After clicking ◐ (light → dark), the hierarchy keeps light-mode `#15803d`/`#1d4ed8`/`#b45309` at 0.22 opacity on a dark surface: duller, with low-contrast strokes. The occupancy bars stay `#c2410c` on dark until a slider moves. The hierarchy never recovers.
- **Evidence:** In `hier-toggled.png` and `occ-toggled.png`, the colours visibly differ from the `colorScheme: dark` render (`hier-1100-dark.png`).
- **Concrete fix:** Use the existing CSS classes instead of `cssVar`: `class:"grn"`/`"blu"`/`"amb"` for the hierarchy rects (these use the soft fills and strong strokes from course.css lines 115–119), and `class:"f-acc"` / `"f-grn"` for the occupancy bars. Then no re-render is needed. This also fixes dark-mode stroke contrast.

### V8 [minor] Occupancy plot wastes most of its height and has no time axis
- **Location:** `#o-svg` viewBox 680×260; rows use `rh=min(13,200/rows)`; the busy row is fixed at y=230.
- **Problem:** With 4 warps, the rows occupy y=20–72 and then about 150px is empty before "SM busy". There is no time axis, tick marks or "cycles" label, so C and L cannot be read off the picture.
- **Evidence:** `occ-1100-light.png`.
- **Concrete fix:**
  - Set `rh = 180/W` (capped at 28) so the rows fill the space.
  - Put "SM busy" directly below the last row.
  - Add an x-axis with ticks every 100 cycles, labelled "cycles".
  - Add a bracket annotating C and L on warp 0's first cycle.
  - Resize the SVG height to the content.

### V9 [minor] The CUDA code clips at desktop width and is hard to compare on mobile
- **Location:** `.grid2` SAXPY block.
- **Problem:** At 1100px the CUDA `<pre>` has scrollWidth 429 against clientWidth 404, so `threadIdx.x;` and `float *y)` are cut and need horizontal scrolling. At 390px the columns stack, which is correct, but the reader then loses the line-for-line correspondence the section is about. The CUDA block scrolls (429 vs 356) and the CSL block is about 650px further down.
- **Evidence:** `saxpy-1100-light.png` shows the trailing `;` cut. `saxpy-390-dark.png` shows "const float *x, floa" truncated.
- **Concrete fix:**
  - Re-wrap the CUDA signature to ≤ 48 columns: `int i = blockIdx.x * blockDim.x` / `      + threadIdx.x;`.
  - Add a small "concept map" table under the two blocks that survives stacking:

    | CUDA | CSL |
    |---|---|
    | thread / `threadIdx` | PE / layout coordinates |
    | `y[i]` in HBM | `y` in 48 KB PE SRAM |
    | `<<<grid, block>>>` | layout.csl `@set_rectangle` + memcpy launch |
    | the hardware schedules warps | `@fmacs` DSD loop, one instruction |
  - Optionally, on mobile, use a tab switcher (CUDA | CSL) so the two stay adjacent.

### V10 [minor] Hierarchy SVG has a fixed `width="760"` attribute and an empty accessible description
- **Location:** Line 41.
- **Problem:** `aria-label="GPU memory hierarchy"` gives none of the numbers. The `width` attribute is overridden by CSS `max-width`, which is harmless, but the occupancy SVG has no text alternative for its result at all.
- **Concrete fix:** Add a `<title>`/`<desc>` listing the four levels with sizes. Add `aria-live="polite"` to `#o-out`.

## Proposed new visuals (prioritised)

### P1. SM anatomy diagram (static SVG, hover details)
- **Purpose:** The first objective is "Describe an SM", and there is no picture of one. Everything else in the chapter (warps, schedulers, occupancy, shared memory) hangs off it.
- **Content:** H100 SM, with numbers from the Hopper whitepaper (tag Vendor):
  - **Four sub-partitions in a 2×2 grid.** Each contains:
    - an L0 instruction cache;
    - 1 warp scheduler plus dispatch (32 threads/clk);
    - a 64 KB register file (16,384 × 32-bit);
    - 32 FP32 lanes;
    - 16 INT32 and 16 FP64 lanes;
    - 1 fourth-generation Tensor Core;
    - LD/ST units and an SFU.
  - **Shared across the SM:**
    - L1 instruction cache;
    - 256 KB combined L1 data cache / shared memory (up to 228 KB shared);
    - Tensor Memory Accelerator (TMA);
    - texture units.
  - **Callout row beneath:** "×132 SMs on H100 SXM · 2,048 threads (64 warps) max per SM · 16 warps per scheduler". Add a mini inset: "a Cerebras PE: 1 core, 48 KB SRAM, 8 microthreads" (link to Chapter 3).
- **Interaction:** Hover or tap a block to show a one-line tooltip in a readout below (for example, "Tensor Core: one MMA per warp instruction; most of the FLOPs in the spec table"). A toggle highlights "what one warp uses": one scheduler, its RF slice, and its lanes.
- **Placement:** New section "Inside an SM" between "Three generations" and "The memory hierarchy". Re-key the hierarchy colours to match the SM blocks (RF green, L1 green, L2 blue, HBM amber).

### P2. Grid → block → warp → SM mapping and occupancy calculator
- **Purpose:** Connect the SAXPY launch `<<<(n+255)/256, 256>>>` to hardware residency, and show where the "resident warps" number in the occupancy widget actually comes from.
- **Content:** Left: the grid as squares (blocks), with one block expanded into 8 warps of 32 threads. Right: 8 SMs drawn (labelled "8 of 132"), each with 64 warp slots. Blocks fill SMs round-robin. Leftover blocks wait in a queue labelled "next wave".
- **Controls:**
  - n (1K–1M, log);
  - threads/block (32–1024, step 32);
  - registers/thread (16–255);
  - shared memory/block (0–228 KB).
- **Readout:** Blocks per SM = min(32, ⌊64 / warpsPerBlock⌋, ⌊65,536 / (regs·threadsPerBlock)⌋ (approximate; ignores allocation granularity, which should be stated), ⌊228 KB / smem⌋). Also show the limiting factor (highlighted), occupancy = residentWarps/64, and waves = ⌈blocks / (132·blocksPerSM)⌉.
- **Interaction:** Changing a slider animates the slots filling. The limiting resource bar turns red.
- **Placement:** In "SIMT: one program, many threads", right after the first paragraph and before the occupancy widget. The occupancy widget's W slider can default to residentWarps/4 from this calculator.

### P3. Coalescing visualizer
- **Purpose:** The coalescing bullet and quiz question 1 have no picture. This is the most important GPU performance rule after occupancy.
- **Content:**
  - A row of 32 lanes (warp).
  - Below it, the memory address line divided into 32-byte sectors grouped into 128-byte lines.
  - Arrows from each lane to its address. Touched sectors are filled.
- **Access patterns (select):**

  | Pattern | Sectors touched | Efficiency |
  |---|---|---|
  | `x[i]` | 4 | 100% |
  | `x[i+1]`, misaligned | 5 | 80% |
  | `x[2*i]` | 8 | 50% |
  | `x[32*i]` (column of a row-major 32-wide matrix) | 32 | 12.5% |
  | `x[perm[i]]`, random | up to 32 | |
  | `double x[i]` | 8 | 100% (lines doubled) |

  Element size toggle: 4 B / 8 B.
- **Readout:** sectors requested vs useful bytes, efficiency %, and effective bandwidth = 3.35 TB/s × efficiency.
- **Interaction:** The select and a stride slider (1–32) re-route the arrows. A "step" button animates the request being split into transactions.
- **Placement:** Directly after the "Coalescing" bullet. Update the quiz answer to reference it ("8 sectors instead of 4").

### P4. Warp-divergence animation
- **Purpose:** The text says "a fully divergent warp runs at 1/32 of peak". Show the masking, and show that branching on warp-aligned conditions costs nothing.
- **Content:** 32 lane columns and a code panel with `if (cond) { A; A; } else { B; }`. Condition presets:
  - `threadIdx.x < 16`: 2 passes, 50% lane-efficiency.
  - `threadIdx.x % 2`.
  - `threadIdx.x / 32 == 0`, warp-aligned: 1 pass, 100%.
  - `data[i] > 0` with random data.
  - `switch(threadIdx.x)`: 32 passes, 1/32.
- **Interaction:** Play/step through instruction slots. Active lanes light up (accent) and masked lanes grey out. A cycle counter compares against the no-divergence case. Footnote: Volta+ independent thread scheduling changes forward-progress guarantees, not this cost.
- **Placement:** After the SIMT paragraph, before the coalescing bullet (or as a tab alongside P3 to save space).

### P5. Roofline for H100 with SAXPY marked
- **Purpose:** Explain why the "memory wall" applies to GPUs in numbers, and tie it back to Chapter 1. It also makes the generations table less of a wall of numbers.
- **Content:** Log-log plot, arithmetic intensity (FLOP/byte) against attainable TFLOP/s:
  - **Compute roof:** 989 TF BF16 dense.
  - **Bandwidth slopes:** HBM 3.35 TB/s (ridge ≈ 295 FLOP/B) and L2 about 3.8 TB/s (Indep).
  - **Kernel points:**
    - SAXPY at 2 FLOP / 12 B ≈ 0.17 FLOP/B, giving about 0.56 TF/s, which is 0.06% of peak.
    - A large GEMM at about 500 FLOP/B, which is compute-bound.
  - **Generation toggle (B200 / Rubin):** the HBM slopes move to 8 and 19.2 TB/s. Use a matching-precision compute roof, or mark the precision mismatch explicitly.
  - Faint dashed comparison line for WSE-3 on-wafer SRAM bandwidth, with its tag, linking to Chapter 15.
- **Interaction:** Hover a point to read its values. Generation radio buttons.
- **Placement:** End of "Three generations", or immediately after the memory-hierarchy figure.

### P6. Scale-up vs scale-out topology (NVL72)
- **Purpose:** "Scaling out" is pure text. Show the two networks and where the parallelism dimensions go.
- **Content:**
  - 18 compute trays (each 2 Grace + 4 Blackwell; 72 GPUs) all connected to 9 NVSwitch trays (1.8 TB/s per GPU, ~130 TB/s aggregate). Verify counts against the notes before drawing.
  - A separate InfiniBand/Ethernet spine linking racks.
  - An overlay showing tensor parallelism inside NVLink, pipeline parallelism across racks and data parallelism across everything.
  - Side note: "70B FP16 = 140 GB, which fits in one B200 (192 GB) vs 4 CS-3 wafers (Ch. 8)".
- **Interaction:** Toggle TP, PP and DP to highlight which links carry which traffic.
- **Placement:** In "Scaling out", after the first sentence. Low priority.

Counts: 10 findings (0 critical, 5 major, 5 minor) and 6 proposed visuals.
