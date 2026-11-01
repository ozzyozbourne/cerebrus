# ch04 · visuals review

Summary: I rendered the page with Playwright at 1100 px and 390 px in light and dark. There are no console errors and no horizontal scroll. The fabric simulator routes correctly for all five patterns, and every route table it shows matches the real Lab layouts (`programs/03-row-reduce`, `04-heat-stencil`, `05-column-broadcast`). The main defects:
- On phones every SVG is scaled to 0.45–0.52×, so its text renders at about 5–6 px.
- In the wavelet figure, a text line collides with the router's WEST port and label.
- The simulator's timing contradicts the prose. Its "in flight" counter counts wavelets still in the CE. Opposite-direction wavelets render as overlapping dots with no direction shown. It has no keyboard access, and its cycle counter keeps advancing after the run ends.
- The color-budget legend has the wrong swatch color and says "Lab 1 = 0".

The largest gap is pedagogical: no visual shows the one-color failure that the checkerboard prevents, back-pressure or shared link bandwidth, switches, or filters.

## Findings (defects in existing visuals)

### V1 [major] All four SVGs are unreadable at phone width
Location: The wavelet+router figure (viewBox 760), the fabric simulator (620), the checkerboard (760) and the color budget (760).
Problem: Each SVG uses `max-width:100%` with a fixed viewBox, so at 390 px the whole drawing shrinks uniformly.
Evidence: The measured rendered widths at 390 px are 340/324/340/340 px, scale factors 0.45/0.52/0.45/0.45. The 13 px labels render at ≈5.9 px, and the 11 px labels (simulator PE coordinates, color-budget numbers, "per-color table") at ≈4.9–5.7 px. The screenshots show the legend line "Colors used in this course…" and the checkerboard key as an unreadable smear. Simulator PEs are 29 × 25 px tap targets.
Concrete fix:
- Simulator: add a narrow-layout branch in JS. When `svg.getBoundingClientRect().width < 500`, use `COLS = 4` (patterns then need ≤4 columns; pass-through and row reduce would use x 0..3), CS = 70 and a viewBox of `0 0 400 340`, and redraw on `resize`. Alternatively, transpose the grid to 4 columns × 6 rows on mobile.
- Static figures: give each a second, stacked layout. Example for the wavelet figure: put the router group below the wavelet text with `<g class="m-stack">` and two viewBoxes switched by a `matchMedia('(max-width:680px)')` listener. The cheaper option is to raise every font-size to ≥18 user units, so they render at ≥8 px, and cut the color-budget legend into two lines (`y=100` and `y=118`, viewBox height 130).
- Checkerboard: draw 4 PEs instead of 6 on mobile (viewBox 0 0 520 170).

### V2 [major] Wavelet figure: a text line runs into the WEST port and label
Location: First figure. `<text x="20" y="124">The color picks the route at every router AND the task at the receiver.</text>` against the router group `translate(560 125)`, whose WEST line runs x = 430→505 and whose WEST label sits at x = −128.
Problem: The text's bbox spans x 20–446, y 111–127. The WEST port line at y = 125 starts at x = 430, and the "WEST" label occupies x 432–467, y 105–120. The word "receiver." is struck through by the port line, and "WEST" sits on top of it.
Evidence: getBBox measurements as above. The overlap is visible in the 1100 px light and dark screenshots.
Concrete fix: Move the router group to `translate(600 125)` and shorten the WEST stub to `x2="-110"`, with the label at `x="-108"`. Or wrap the sentence onto two lines (`…at every router` / `AND the task at the receiver.`) so it ends before x ≈ 400. Also see P4 in the pedagogy review: on WSE-3 the receiving task is chosen by the queue bound to the color, so the sentence should become "…and, via its input queue, the task at the receiver".

### V3 [major] Simulator timing does not match the text or its own hint
Location: The `reset()` and `step()` code (lines 187, 198–203) and the hint "the ramp costs an extra tick".
Problem:
- The ramp-up costs 2 ticks (`t: s.t0 + k + 2`).
- The ramp-down costs 0 ticks: delivery is counted on the same tick the wavelet arrives.
- A relay costs 3 ticks.

The prose says the ramp takes about 2 cycles, and the quiz says "plus ~2 cycles on each ramp". A learner who counts cycles in Point to point sees delivery at cycle 3 for a 1-hop transfer, which does not equal 2 + 1 + 2.
Evidence: Stepping Point to point gives `cycle 3 … (1,0):recv 1`. Pass-through over 5 hops first delivers at cycle 7 (2 + 5 + 0).
Concrete fix: Model ramp-down explicitly. In `step()`, when `d === "RAMP"`, push `{…f, stage:"down", t: tick + 2}` and count the delivery only when that entry matures. Change the hint to "each hop costs 1 tick; going up or down the ramp costs ~2 ticks each; a relaying CE adds 1 tick". Then Point to point delivers at cycle 5 and pass-through at cycle 9, both consistent with the quiz.

### V4 [major] Opposite-direction wavelets on the same link overlap, and direction is never shown
Location: Simulator `draw()`. Dots are drawn at `px + (f.c-1.5)*4, py-14`, and route lines have no arrowheads.
Problem: In the halo pattern at cycle 2, the eastbound c1 wavelet (x ≈ 227) and the westbound c2 wavelet (x ≈ 231) between (1,2) and (2,2) are r = 6 circles 4 px apart, so the blue one is almost hidden by the green one. Nothing shows which way any wavelet or route goes, which is the whole point of a halo exchange. Every dot sits at the link midpoint the whole time it is in transit, so motion is only implied.
Evidence: The halo screenshot at cycle 2 (light and dark) shows two half-hidden dots on the middle link. Route lines are plain 2 px lines at 0.45 opacity.
Concrete fix:
- Draw each route line with `marker-end` arrowheads, one marker per palette color, defined once in a `<defs>`.
- Offset eastbound traffic above the link centre and westbound traffic below it: `const lane = (d==="EAST"||d==="SOUTH") ? -1 : 1; offset = lane*6`. For vertical links, apply the offset to x, not y. The current code adds `(c-1.5)*3` to y1/y2 for vertical lines too, so vertical routes of different colors would draw on top of each other.
- Put flits on the link line (`py`, not `py-14`) and animate them with `requestAnimationFrame` between ticks: interpolate `prog` from 0 to 1 over the 420 ms interval instead of the fixed 0.5.

### V5 [minor] The "in flight" counter includes wavelets still sitting in the CE
Location: `#f-tick` text, `cycle ${tick} · in flight ${flits.length}`.
Problem: At cycle 0 it reads "in flight 4" (point to point) or "in flight 6" (halo) while no dot is visible. In row reduce it reads "in flight 3" while only one dot is on screen.
Evidence: Step logs show "cycle 0 · in flight 4" with no circles drawn.
Concrete fix: Show `queued ${flits.filter(f=>f.t>tick+1).length} · on fabric ${flits.filter(f=>f.t<=tick+1).length} · delivered ${sum(delivered)}`.

### V6 [minor] Step and Run keep advancing the cycle after the run ends; the "dropped" counter is never shown
Location: The `#f-run` and `#f-step` handlers and `delivered.dropped`.
Problem: After completion, each Step adds a cycle (cycle 10, 11, … with nothing in flight). Run starts the timer again for one more empty tick. Mis-routed wavelets are counted in `delivered.dropped`, but nothing displays the count. The count is also mixed into the per-PE `delivered` map; no existing pattern drops anything, so this is latent.
Evidence: "after full run cycle 9" → Step → "cycle 10 · in flight 0" → Run → "cycle 11".
Concrete fix: In `step()`, `if (!flits.length) return;` at the top. In the Run handler, `if (!flits.length) reset();` before starting. Keep the drop count in a separate variable and show it in `#f-tick` in red when it is above 0. This is needed for the proposed "broken one-color" pattern (N1).

### V7 [minor] The simulator has no keyboard or screen-reader access to the PEs
Location: The PE `<g>` elements built in `draw()`.
Problem: PEs respond to clicks only. They have no tabindex, role or key handler, and `#f-out` is not a live region.
Evidence: The count of focusable PE groups is 0.
Concrete fix: `el("g", {tabindex: 0, role: "button", "aria-label": \`PE (${x},${y})\`, …})`, plus `g.onkeydown = e => { if (e.key==="Enter"||e.key===" ") { e.preventDefault(); g.onclick(); } }`, plus `aria-live="polite"` on `#f-out`. Because `draw()` rebuilds the SVG every tick, focus is lost. Restore it after drawing with `svg.querySelector(\`[aria-label="PE (${sx},${sy})"]\`)?.focus()` when the previously focused element was a PE.

### V8 [minor] Color-budget legend: wrong swatch color and a wrong Lab 1 count
Location: The color-budget SVG, lines 113–115.
Problem:
- The "■ yours" swatch has no class, so it renders in the text color (black in light mode, white in dark), while the user colors are drawn green.
- "Lab 1 = 0" is wrong: `programs/02-wavelet-tasks/commands.sh` passes `MEMCPYH2D_DATA_1_ID:0`, so Lab 1 spends color 0 (accuracy review A2).
- The bar is labelled as 24 colors, but the wavelet figure says the tag is 5-bit with 8 more reserved IDs. The two figures never connect.

Evidence: In the dark 1100 px screenshot the legend square is white next to green boxes.
Concrete fix: Use `<text … class="f-grn">■</text><text …> yours</text>` (two tspans or two text elements), and change the course text to `Lab 1 = 1 (H2D stream), Lab 2 = 2, Lab 3 = 4`. Better still, mark the lab usage on the bar: thin underline ticks under colors 0–3 labelled "Lab 3 uses 0–3". Optionally add 8 dashed grey boxes for IDs 24–31 labelled "not routable (reserved IDs)". This needs viewBox width 760 → about 1000, or two rows.

### V9 [minor] The checkerboard figure shows only the fix, never the failure, and it is 1-D
Location: The `#chk` figure.
Problem: The six-PE chain with c0/c1 arrows is correct. It matches the row-reduce layout and reads well in both themes. But it shows only send arrows, and nothing shows the receive side or the per-PE rule pair the caption describes. The end PEs (PE 0 sends only, PE 5 receives only) are drawn like the middle ones. The top 40 units of the viewBox are empty. The name "checkerboard" suggests 2-D, but only a 1-D alternation is drawn (pedagogy P14).
Evidence: Screenshots at 1100 px, light and dark.
Concrete fix: Under each PE box, add two small mono lines with its actual rules, e.g. for PE 2: `c1: WEST→RAMP`, `c0: RAMP→EAST`. PE 0 gets only `c0: RAMP→EAST` and PE 5 only `c1: WEST→RAMP`. Use `font-size` 12 and y = 118/134, with the viewBox height raised to 200. Reduce the top padding (`y: 40` → `y: 20`). The 2-D version and the failure demo are proposed below (N1, N7).

### V10 [minor] Route-line color offset and dot offset collide for four colors
Location: Simulator `draw()`, route lines offset by `(c - 1.5) * 3`.
Problem: In the halo pattern four route lines (c0–c3) share each link within a 9 px band at 0.45 opacity. In dark mode the c0 orange and c3 purple lines are hard to tell apart (screenshot), and no legend maps colors to c0–c3.
Concrete fix: Add a small legend under the SVG generated from `palette` (`c0 ● c1 ● c2 ● c3 ●`, showing only the colors the current pattern uses). Raise the opacity to 0.7 and use the lane separation from V4 (eastbound above, westbound below) so that at most two lines share a band.

### Checked and correct
- Simulator routing. Every pattern delivers all wavelets with 0 drops:
  - Point to point: 4/4 to (1,0).
  - Pass-through: 3/3 to (5,1).
  - Row reduce: 3 to each of PEs 1..5, alternating c0/c1, with relays emitting on the opposite color.
  - Column multicast: 3 each to (0,1), (0,2) and (0,3), with each copy delivered and forwarded in the same hop.
  - Halo: interior PEs get 2, edge PEs get 1.
- The inspector's `@set_color_config` lines match `programs/03-row-reduce/layout.csl`, `04-heat-stencil/layout.csl` (E0/E1/W0/W1 = c0..c3 parity scheme) and `05-column-broadcast/layout.csl` exactly.
- Changing the pattern while Run is active stops the timer correctly. Double-clicking Run does not start two timers.
- No console errors or warnings at either width or in either scheme. No horizontal page scroll.
- The color budget correctly marks 20–23 as memcpy-reserved (checked by the accuracy review against `memcpy/sys_params.csl`).

## Proposed new visuals (prioritised)

### N1 (high) "Broken" pattern: row reduce on ONE color
Purpose: Show the failure that the checkerboard prevents (pedagogy P1/P6). At present the reader has to take it on trust.
Content and data: Add a sixth simulator pattern, "Row reduce on one color (broken)". Rows y = 0, PEs 0..3, everything on c0:
- PE 0: `rx {RAMP} → tx {EAST}`.
- PEs 1–2: the only single rule that can both receive and send, `rx {WEST, RAMP} → tx {RAMP, EAST}`.
- PE 3: `rx {WEST} → tx {RAMP}`.

A relay at PE 1 and PE 2 emits on c0. When run, the counters show PE 2 receiving both PE 0's raw value (forwarded by PE 1's router before PE 1 adds) and PE 1's partial sum, and its own sends loop back down its ramp. A red "wrong: PE 2 got 2× the wavelets it expected" banner appears. Also flag a "collision" whenever two c0 wavelets enter one router in the same tick (count them, and draw a red ring at that router).
Interaction: Selectable in the existing dropdown, with a "Fix it" button that switches to the checkerboard pattern so the two are seen side by side. The inspector shows the bad rule.
Where: The simulator, plus a sentence in "Why programs alternate colors" pointing to it.

### N2 (high) Router anatomy with back-pressure and shared link bandwidth
Purpose: Introduce per-color input buffers, losslessness and back-pressure (P2), and the fact that all colors share one physical link (P3).
Content: A single router drawn larger, with five ports. Each input port has a small stack of per-color FIFO slots (showing c0 and c1, depth 2). A crossbar sits in the middle, and the output link carries one wavelet per cycle. Two streams (c0 from WEST, c1 from NORTH) both want to go EAST.
Interaction:
- Run/Step controls.
- A toggle "stall c0 receiver downstream": c0's buffer fills, its upstream sender is shown stopping (credit back-pressure), and c1 keeps flowing.
- A slider for c1's injection rate 0–100%, showing that c0's throughput drops to `1 − rate` because the link is shared.
- A readout of per-color wavelets/cycle.

Data: 1 wavelet per link per cycle, 32 bits, ≈4 GB/s per direction at ~1 GHz <span>Derived</span>. Buffer depth is illustrative and must be labelled as such.
Where: New subsection after "A mesh of five-port routers", or right after the first figure.

### N3 (high) Switch-position animation (from SDK tutorial topic-06)
Purpose: The switches paragraph is prose only, and its subtle point (a control wavelet's own payload follows the old route) is hard to picture.
Content: A 3×3 grid with centre PE (1,1) as the sender on one color. The routes are `rx RAMP`, with pos0 tx NORTH, pos1 WEST, pos2 EAST, pos3 SOUTH, `current_switch_pos = 1` and `ring_mode = true`, exactly as in `tutorials/topic-06-switches/layout.csl`. The receivers are (1,0) rx SOUTH, (0,1) rx EAST, (2,1) rx WEST and (1,2) rx NORTH. A position dial at the centre router highlights the active position.
Interaction: Two buttons, "send data wavelet" and "send control wavelet". A control wavelet travels along the current route and the dial advances one position *after* it leaves. The dial then wraps 3 → 0. A caption counter shows "colors used: 1 (vs 4 without switches)".
Where: Replace the prose-only "Switches" column, keeping the grid2 layout with the figure below both columns.

### N4 (medium) Range-filter demo (from SDK tutorial topic-08)
Purpose: Show how one broadcast stream can feed different slices to different PEs.
Content: A 4×1 row on one color. PE 0 sends 12 wavelets with index field 0..11 in the upper 16 bits (show the 16|16 split). PE k (1..3) has `min_idx = 3k`, `max_idx = 3k+2`. PEs 1–2 have `tx {RAMP, EAST}` and PE 3 has `tx {RAMP}`, as in `tutorials/topic-08-filters/layout.csl`. Accepted wavelets drop down the ramp in green, and rejected ones pass by greyed out. Indices 0–2 are accepted by no one, which is worth pointing out.
Interaction: Run/Step, plus number inputs for each PE's min/max, with edge checks (min > max gives an "accepts nothing" warning). A WSE-2/WSE-3 toggle shows the filter counts: 4 + 2 banks versus 6 in one bank, from `target/wse2.csl` and `wse3.csl`.
Where: Under the "Filters" column.

### N5 (medium) Latency vs throughput calculator
Purpose: Make "latency grows linearly with distance" and pipelining concrete (P8), and make "over a thousand hops" tangible.
Content: Inputs are hop distance d (slider 1–1,900, with markers at 1 for "neighbour", 100, 950 for "half wafer" and ~1,900 for "corner to corner") and message length M wavelets (1–4,096). Outputs:
- first-wavelet latency ≈ 2 + d + 2 cycles;
- last-wavelet arrival ≈ 2 + d + 2 + (M−1) cycles;
- a bar split into ramp, hops and stream;
- the time at an assumed 1 GHz;
- effective bandwidth M·4 B / time.

Every assumption carries a Derived tag. Optionally overlay "d-step relay chain" (store-and-forward through CEs, as in row reduce) against "pass-through" to show why pass-through routes exist.
Where: After the aggregate-bandwidth paragraph, or replacing the second quiz question.

### N6 (medium) Interactive color-budget planner
Purpose: Turn "colors are the scarcest resource" from a statement into an exercise.
Content: Checkboxes for communication patterns, each with its cost:
- 1-D reduce chain (2);
- 1-D halo (4);
- 2-D halo/game of life (8, from the SDK benchmark);
- column broadcast (1);
- each streaming H2D/D2H channel (1);
- the 25-pt stencil (21 colors and task IDs, from its README).

The 24-box bar from the existing figure fills from 0 upward. Boxes 20–23 stay red, so the planner turns red when the total passes 20. Switching-capable colors (0–9, 12, 13, 16, 17, 20, 21, from `memcpy/sys_params.csl`) get a small ⇄ marker, so a learner who ticks "uses switches" sees which IDs qualify.
Where: Replace the static color-budget figure (fixing V8 at the same time).

### N7 (low) 2-D checkerboard for a 4-neighbour exchange
Purpose: Explain the "4 directions × 2 parities = 8 colors" figure in the caption, and justify the word "checkerboard".
Content: A 4×4 PE grid colored by (x+y) parity, or by x and y parity separately, with arrows from one highlighted PE to its four neighbours, each arrow labelled with its color (e.g. E0/E1, W0/W1, N0/N1, S0/S1). A side table lists the 8 rules that the highlighted PE's router holds.
Interaction: Hover or click any PE to see its 8 `@set_color_config` lines, as in the simulator inspector.
Where: Directly after the existing 1-D checkerboard figure.

### N8 (low) Wavelet bit layout with the index field
Purpose: Connect the wavelet figure to filters and sparse data (pedagogy P13).
Content: Redraw the payload as two 16-bit halves labelled "index (upper 16, used by range filters / sparse tensors)" and "data". Show the 5-bit color field with a scale mark "0–23 routable, 24–31 reserved IDs" (Indep, SpaDA). Draw field widths proportional to bit count (5 : 32), not 70 : 250 px.
Where: Replace the left half of the first figure (fixing V2 by giving the router its own column).
