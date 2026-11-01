# ch06 · visuals review

Summary: Chapter 6 has two visuals: the interactive "DSD visualizer" and one static SVG figure of `@fadds(out_dsd, in_dsd, v_dsd)`. Both render without console errors at 1100 px and 390 px in light and dark, and the page never scrolls sideways. The visualizer computes the right word sequences for every preset. Its problems are in presentation and robustness: one preset is mislabelled, stride 0 draws overlapping labels, the stencil preset leaves the controls showing stale values, colors stay in the old theme after a toggle, inputs have no limits, and everything is unreadable on a phone. The static figure is correct in outline but has a wrong label ("my 48 KB"), a cramped arrow, and 5 px text on mobile. Most of the chapter's mechanisms (DSR and address generator, systolic chain, async microthreads, FIFOs, the WSE-3 single-fabric-input rule) are explained only in prose, so this review proposes seven new visuals.

Method: Playwright/Chromium, viewports 1100×900 and 390×900, `colorScheme` light and dark. I selected every preset, typed edge values into all three number inputs, toggled the theme from the top-bar button and recorded console and page errors (there were none). I checked the visuals against `course/programs/{01-saxpy,03-row-reduce,04-heat-stencil}/pe_program.csl` and the SDK tutorials `gemv-02-memory-dsds`, `pipeline-01-basic` and `sdklayout-03-ports-and-connections`.

## Findings (defects in existing visuals)

### V1 [major] "next column" preset actually shows column 3
- **Location:** DSD visualizer, preset `3,6,8` labelled "next column via @increment_dsd_offset: |i|{6} -> A[3 + i*8]".
- **Problem:** The preset after "matrix column" claims to be the *next* column, but it uses base 3, which is column 3 (three increments later). In the SDK, `gemv-02-memory-dsds` walks columns with `A_dsd = @increment_dsd_offset(A_dsd, 1, f32);`, so the next column starts at base 1. The label teaches the wrong offset.
- **Evidence:** The readout reads `base=3 extent=6 stride=8 → words [3, 11, 19, 27, 35, 43]`. See `gemv-02-memory-dsds/pe_program.csl` lines 49–53.
- **Concrete fix:** Change the option to `value="1,6,8"` and the label to `next column: @increment_dsd_offset(A_dsd, 1, f32) → A[1 + i*8]`. Alternatively, keep base 3 and relabel it "column 3 (after 3 × @increment_dsd_offset(…, 1, f32))". Better still, build the button described in proposal P2.

### V2 [major] Visualizer is illegible at phone width
- **Location:** `#d-svg` (viewBox 680×200, `width="680"`) at a 390 px viewport.
- **Problem:** The SVG shrinks to about 320 px (scale about 0.47). The 9 px word indices render at about 4 px and the 10 px order numbers at about 5 px, which nobody can read. The widget's main teaching content, the visit order, is lost on mobile.
- **Evidence:** widget-390-light/dark screenshots: two rows of 24 tiny cells with unreadable labels.
- **Concrete fix:** Make `PER` depend on the space available. In `draw()`, set `PER = svg.clientWidth < 500 ? 8 : 24` and set the viewBox height from `Math.ceil(48/PER)` rows. Eight words per row also makes the 6×8 matrix presets look like a matrix (see V8). Keep text at 11 px or larger at that size.

### V3 [major] Fabric figure is illegible on mobile and has a wrong label
- **Location:** The figure after the row-reduce snippet (viewBox 760×200).
- **Problem:**
  1. At 390 px the figure is scaled to about 0.45, so the 11–12 px labels ("fabin: from WEST", "one instruction, M elements", "v_dsd …") render at about 5 px.
  2. The memory box says "v_dsd (my 48 KB)". `v` is an `[M]f32` array inside the PE's 48 KB SRAM, not 48 KB itself. The label suggests the DSD covers all of SRAM.
  3. The v_dsd→@fadds arrow is drawn from y=170 to y=162, a path of 8 px. Its 12 px arrowhead (markerWidth 6 × stroke-width 2) is longer than the path, so the arrow reads as a bare triangle stuck to the box.
- **Evidence:** fig-390-dark screenshot; the SVG source (`<path d="M380 170 V162" …>`, `<text …>v_dsd (my 48 KB)</text>`).
- **Concrete fix:**
  - Relabel the box `v_dsd → v[0..M-1] in local SRAM`.
  - Move the memory box down (y=200, viewBox height 240) so the arrow is at least 30 px long.
  - For mobile, redraw the figure as a narrower layout: in_dsd above, @fadds in the middle, out_dsd below, with v_dsd to the side, in a viewBox about 360 wide. Swap between the two layouts with a `<picture>`-style pair of SVGs toggled by `@media (max-width: 600px)`. Or simply raise the font sizes to 22–24 user units so they stay at least 10 px after scaling.

### V4 [major] Stencil preset leaves stale controls and is hard to read
- **Location:** Visualizer preset "Lab 3 stencil".
- **Problem:**
  1. Selecting it does not update the base, extent and stride inputs. After the broadcast preset they still show `0 / 16 / 0`, which contradicts the three DSDs drawn.
  2. If the user then edits any input, the drawing jumps to a single-DSD view, but the select still says "Lab 3 stencil".
  3. The three DSDs are drawn as nested, inset squares at opacity 0.75. The innermost square is only 12 px, the colors blend, there is no legend, and the order numbers are switched off when more than one DSD is shown.
  4. The array `u` has n+2 = 10 words, but the widget still draws 48 words, and the ghost cells u[0] and u[9] are not marked.
- **Evidence:** pre4-light screenshot (inputs show stride 0; cells 1–8 are muddy red-green nests). Edge test: after the stencil preset, filling stride=2 gives a single-DSD readout while `#d-pre` keeps the value "stencil".
- **Concrete fix:** In stencil mode, draw a dedicated layout: one strip of 10 cells for `u` with ghost cells hatched and labelled "ghost (halo)", and under it three aligned rows (left, mid, right), each a run of 8 colored cells offset by 0, 1 and 2. Add a color legend on the left of each row. Disable the number inputs in this mode, or set them to show the mid DSD. Reset the select to a "custom" option whenever an input is edited by hand.

### V5 [minor] Stride 0 draws 16 labels on top of each other
- **Location:** Preset "broadcast one value" (or any stride 0).
- **Problem:** All 16 order labels (0…15) and 16 translucent rects are drawn on word 0. Only "15" shows, which suggests the word is visited once, as element 15.
- **Evidence:** pre3-dark screenshot shows a single cell labelled "15".
- **Concrete fix:** Group the addresses that repeat. Draw the rect once and label it with the visit count (for example "×16") or the visit list ("0–15"). Optionally show a small numbered stack of visits next to the cell.

### V6 [minor] Highlight colors go stale after a theme toggle
- **Location:** `draw()` uses `fill: cssVar(color)`, which writes a resolved hex value into the attribute.
- **Problem:** After the top-bar ◐ toggle, the highlighted cells keep the old theme's accent until the user touches a control. Light→dark leaves `#c2410c` on a dark background.
- **Evidence:** Edge test: the fill was `#c2410c` both before and after the toggle (toggled.png).
- **Concrete fix:** Use CSS classes instead of resolved colors. For example `class: "f-acc"`, `"f-blu"` and `"f-grn"` already exist in course.css. Or set `style: "fill: var(--accent)"`.

### V7 [minor] Inputs have no limits: negative or fractional addresses and freeze risk
- **Location:** The `#d-b`, `#d-e` and `#d-s` `oninput` handlers.
- **Problem:** The HTML `min` and `max` are not enforced on typed values.
  - Base −5 or stride −2 produces negative addresses. These rects are drawn outside the viewBox, and no warning appears because the check is only `a > 47`.
  - Fractional values (2.5 / 1.5) give "words [2.5, 4, 5.5]".
  - An extent of 5,000,000 takes about 350 ms per keystroke and builds a 5-million-element array. A larger value would hang the tab.
- **Evidence:** Edge-test readouts: `base=-5 … words [-5, -4, -3, -2]` with no warning; `base=2.5 extent=3 stride=1.5 → words [2.5, 4, 5.5]`; extent 5e6 took 349 ms.
- **Concrete fix:** Clamp and round in `fromInputs()`: `b = clamp(Math.round(b), 0, 47)`, `e = clamp(Math.round(e), 0, 48)`, `s = clamp(Math.round(s), -16, 16)`, and generate at most `e` addresses. Change the warning to `a < 0 || a > 47`. If negative strides are kept, add a preset for them (reverse walk, base 15, stride −1). Confirm against the CSL reference first; otherwise set min=0.

### V8 [minor] Matrix presets are not drawn as a matrix
- **Location:** Presets "matrix column (6×8 row-major)" and "next column".
- **Problem:** Memory is drawn 24 words per row. A column with stride 8 therefore appears as three scattered cells per row instead of a vertical line. The point the widget should make (a stride of N walks down a column of a row-major matrix) is hidden.
- **Evidence:** pre1 and pre2 screenshots.
- **Concrete fix:** Add a "row width" control (default 24; set to 8 by the matrix presets) so the 48 words wrap as a 6×8 grid. Combined with V2, mobile can default to 8.

### V9 [minor] Readout and SVG polish
- **Location:** `#d-out` and `#d-svg`.
- **Problem:**
  - The readout truncates to 16 words even for extent 48.
  - It never shows the CSL text for custom values, so the user has to translate base/extent/stride back into `tensor_access` alone.
  - The SVG has about 40 px of empty space above the cells and about 60 px below the last label (viewBox 200, content ends near y=137).
  - The white order numbers (10 px bold) sit on 75 %-opacity fills at about 3.5:1 contrast (green in dark mode about 2.8:1), below 4.5:1 for small text.
  - `#d-out` is not `aria-live`.
- **Evidence:** widget screenshots; contrast computed from the course.css tokens.
- **Concrete fix:**
  - Add a line `tensor_access: |i|{e} -> v[b + i*s]   ≡   .{ .base_address = &v[b], .extent = e, .stride = s }`. The equivalence is the one used in gemv-02.
  - Show up to 48 words in the readout.
  - Set the viewBox to `0 0 680 150` and `OY = 10`.
  - Use opacity 1 on the order cells, or dark text on the soft fills.
  - Add `aria-live="polite"` to `#d-out`.

## Proposed new visuals (prioritised)

### P1. Systolic row reduction, animated (highest priority)
- **Purpose:** The caption says "A chain of these is a systolic reduction", but the chapter only ever shows one PE. Learners need to see that the wavelets pipeline through the PEs, and that the sum arrives at the last PE without any PE storing the stream.
- **Content and data:** A row of P PEs (default 4; slider 2–8), each holding `v` with M elements (default 4; slider 1–8). Use small integer values, for example PE k holds v = [k+1, k+1, …], so the sums are easy to check. Role labels come from `03-row-reduce/pe_program.csl`:
  - first PE: `@fmovs(out_dsd, v_dsd)`;
  - middle PEs: `@fadds(out_dsd, in_dsd, v_dsd)`;
  - last PE: `@fadds(v_dsd, in_dsd, v_dsd)`.
  - Each PE also shows the `.activate = exit_id` completion.
- **Interaction:** Step, Play and Reset buttons. At each tick, a wavelet (a colored dot carrying its running value) moves one hop east, and the receiving PE adds its own v[j]. A counter shows "tick t". The final tick, about M + P − 1, is marked "derived: illustrative pipeline timing" with a `.tag derived`; it is not a measured cycle count. When an op's last element passes, show its exit_task firing. At the end, the last PE's `v` shows the column sums.
- **Where:** Replace the static figure, or place it directly after it, under "Fabric DSDs: communication is an operand". The static one-PE figure, with V3 fixed, becomes frame 1.

### P2. GEMV column sweep with `@increment_dsd_offset`
- **Purpose:** The chapter shows a matrix column and the next column only as presets. The typical idiom, from SDK gemv-02, is to re-point one DSD on every loop iteration. This is the bridge from "a DSD is a loop" to "a DSD is a loop you can move".
- **Content and data:** A 6×8 row-major `A` drawn as a grid, a vector `x` of 8 elements and an output `y` of 6 elements. The code panel follows gemv-02:
  - `A_dsd = |i|{M} -> A[i*N]`
  - `for i in 0..N: @fmacs(y_dsd, y_dsd, A_dsd, x[i]); A_dsd = @increment_dsd_offset(A_dsd, 1, f32);`
- **Interaction:** A "Next column" button (and Play). Each press highlights the column that A_dsd covers, highlights x[i] as the scalar, and updates y numerically. Use A[idx] = idx as in gemv-02 and x = 1, so the values are checkable. A toggle "increment by N instead of 1" shows a row walk going past the end of the array, which ties in with the "runs past the array" warning.
- **Where:** Directly after the DSD visualizer, in "One instruction, a whole loop". It also fixes the meaning of V1.

### P3. Scalar loop vs DSD instruction: what the CE actually issues
- **Purpose:** The prose claims "no per-element instruction fetch or loop counter" and says the descriptor lives in one of 48 DSRs, but there is no picture of a DSR, the address generator or the datapath.
- **Content and data:** Two lanes, side by side.
  - Left: a C-style loop compiled to scalar steps per element (load x[i], load y[i], fma, store y[i], i++, branch). This instruction stream is illustrative and should carry `.tag derived`.
  - Right: one `@fmacs` instruction loads three DSRs (dst y_dsd, src0 y_dsd, src1 x_dsd) and a scalar register `a`. An "address generator" box ticks base, base+stride, … and streams operands to the FMA unit and back to SRAM.
  - Facts with tags: 48 DSRs per WSE-3 core `vendor` (HC2024); 48 KB SRAM per PE.
- **Interaction:** A slider for N (1–64). Counters show "instructions issued": 6N + small constant on the left (labelled illustrative) versus 1 on the right. A Step button animates the address generator producing each address.
- **Where:** Right after the paragraph "The descriptor lives in one of the PE's 48 data-structure registers…", before the visualizer.

### P4. Async timeline: CE, microthreads and completion tasks
- **Purpose:** `.async`, `.activate` versus `.unblock`, and the claim that a blocking fabric op can stall memcpy (pipeline-01) are prose only. A timeline makes the concurrency and the deadlock visible.
- **Content and data:** Swimlanes: CE (main thread), microthread for queue 2 (or another queue ID), memcpy/router, and the task picker. Scenario A is program 03's middle PE: `reduce()` issues the async `@fadds` and returns, the CE goes idle or serves memcpy, the microthread streams M wavelets, and on completion `exit_task` is activated and calls `unblock_cmd_stream()`. Scenario B is the same op without `.async`. Following pipeline-01's README, the CE sits in `@add16` polling an empty input queue, the H2D command that would fill it cannot be serviced, and the lane shows a red "stall" bar.
- **Interaction:** A toggle "async on/off" and a radio button for completion: `.activate` (a task runs) versus `.unblock` (a blocked task becomes eligible, and runs only once it is also activated). Play animates both lanes. Add a note from program 04: two concurrent async ops must not share a microthread ID (queue IDs 2–5 are all different in 04-heat-stencil).
- **Where:** Under "Async operations and completion tasks".

### P5. FIFO between two microthreads, and the WSE-3 single-fabric-input rule
- **Purpose:** The warning callout and the FIFO paragraph each describe the add2vec pattern in words.
- **Content and data:** Two panels.
  - Panel 1 (✗ WSE-3): `@add16(output, input1, input2)` with two fabin arrows into one op, crossed out, labelled "WSE3 does not allow multiple fabric inputs per DSD operation" `sdk`.
  - Panel 2 (✓): copied from `sdklayout-03-ports-and-connections/add2vec.csl`:
    - `@mov16(fifo, input2, .{.async=true})` fills the FIFO, which is an SRAM `buffer[size]` drawn as a ring with head and tail pointers;
    - `@add16(output, input1, fifo, .{.async=true})` drains it;
    - each op is labelled with its microthread.
- **Interaction:** A Play/step control moves wavelets: input2's wavelets enter the ring and input1's wavelets pair with the FIFO head. A slider sets the input2 arrival rate relative to input1, showing the FIFO filling up and then back-pressure when it is full. A note keeps the "stalls when size exceeds 14" fact in its correct context: it is pipeline-01's limit on the H2D I/O queues, not a general FIFO depth.
- **Where:** Replace the plain warning callout with callout + figure, and put the animated part under "FIFOs extend the tiny hardware queues".

### P6. Lab 3 stencil, step by step with numbers
- **Purpose:** The three-instruction update is shown as code plus a pointer to the visualizer preset, which (see V4) does not explain it well.
- **Content and data:** n = 8. `u` has 10 cells: u[0] is a ghost from the west neighbour, u[9] a ghost from the east neighbour. Example values: u = [100, 0, 0, 0, 0, 0, 0, 0, 0, 0] (hot west boundary), alpha = 0.25. Rows for left, mid and right offset by 0, 1 and 2; a `lap` row of 8 cells below.
- **Interaction:** A Step button runs the three instructions in turn:
  1. `@fadds(lap, left, right)` fills lap.
  2. `@fmacs(lap, lap, mid, -2.0)` updates lap.
  3. `@fmacs(mid, mid, lap, alpha)` writes into u[1..8].
  At each step the operand rows are highlighted and the numbers update. A "halo exchange" step before step 1 animates u[1] being sent west and u[8] east into the neighbours' ghost cells, as in `start_step()` in program 04. A "repeat T steps" slider shows the heat spreading.
- **Where:** Directly under the stencil code in "Lab 3's whole update, in three instructions". The visualizer's stencil preset can then be dropped.

### P7. Builtin name decoder (small)
- **Purpose:** The naming rule (`f`, `s`/`h`, `16`/`32`) and "any operand can be a memory DSD, fabric DSD, FIFO or scalar" are only in prose and a table.
- **Content and data:** The builtins from the table: `@fmovs`, `@fadds`, `@fmuls`, `@fmacs`, `@fnegs`, `@mov16`, `@mov32`, `@add16`.
- **Interaction:** Hover or tap a builtin: its name splits into colored parts (`f` | `mac` | `s`), and a mini operand diagram shows which slots accept which DSD kinds. Fabric-input slots carry the WSE-3 "max one fabric input" badge. Keep the existing "Derived from SDK sources" tag.
- **Where:** Under the "Builtins: the vector instruction set" table.
