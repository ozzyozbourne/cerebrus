# ch11 · visuals review

Summary: I rendered the page with Playwright at 1100 px and 390 px, in light and dark. Nothing overflows horizontally and the console logs no errors. The reduction-roles diagram is correct against `programs/03-row-reduce`. The wavefront widget has two real bugs, though, and one design flaw that cancels out its main lesson:
- Moving a slider while the animation plays updates the label but leaves the old run animating.
- Toggling the theme leaves cells and arrows in the old palette.
- Both modes are scaled to the same ~2.4 s, so store-and-forward does not *look* slower.

The multicast figure does not match program 05: it draws 5 PEs where the program uses R = 6, the root's own `y` is missing, and the caption says "R receivers" where there are R−1. The GEMV figure promises arrows and teal, but it draws plain lines and green, its labels are off by 15 px, and its colour encoding conflicts with the first figure. At 390 px every SVG is scaled to 0.45, so the 11–12 px labels render at about 5 px and cannot be read.

## Findings (defects in existing visuals)

### V1 [major] Wavefront widget: moving a slider or changing mode during playback does not stop the running animation
Location: `src/11-lab-neighbours.html`, the script at the end, the `["#w-p", "#w-m", "#w-mode"].forEach(... oninput ...)` handler.
Problem: the handler calls `frame(0, newP, newM, mode)` but never calls `clearInterval(timer)`. The old interval keeps calling `frame(t, oldP, oldM, oldMode)` and overwrites the new grid on the next tick. The labels show the new values while the grid and readout still show the old run.
Evidence: I started Play in store-and-forward mode at P = 8, M = 12, then set P = 3. 50 ms and 200 ms later `#w-pv` read "3", but the SVG still held 96 rects (8 × 12) and the readout went on counting "cycle 64 / 110" → "cycle 74 / 110". Pressing ArrowLeft on the slider during a run did the same: the grid was redrawn at P = 11 and then overwritten by the old run.
Concrete fix: add a `stop()` helper and call it from every input handler.
```js
function stop() { if (timer) { clearInterval(timer); timer = null; } $("#w-go").textContent = "Play"; }
["#w-p", "#w-m", "#w-mode"].forEach(s => $(s).oninput = () => { stop(); /* existing body */ });
```

### V2 [major] The widget plays both modes in the same wall-clock time, which hides the speed difference
Location: `play()`, `setInterval(..., Math.max(20, 2400 / total))`.
Problem: the tick period is `2400/total`, so a 26-cycle streaming run and a 110-cycle store-and-forward run both take about 2.4 s. The learner sees the same duration and has to read the small counter to notice any difference. The only exception is the extreme (P = 12, M = 24, store-and-forward, 310 cycles), where the 20 ms floor makes it take 6.1 s.
Evidence: measured wall times were 2.3 s (2/4 streaming), 2.3 s (2/4 store-and-forward), 2.3 s (12/24 streaming) and 6.1 s (12/24 store-and-forward).
Concrete fix: use a fixed time per cycle, for example `const MS_PER_CYCLE = 60;` and `setInterval(tick, MS_PER_CYCLE)`. Then 26 cycles take 1.6 s and 110 cycles take 6.6 s. A better fix is New-visual N1: run both modes side by side on one clock.

### V3 [major] Hard-coded colours do not follow the theme toggle (reduction figure, GEMV figure, widget)
Location: every `cssVar(...)` call. In the reduction figure that is the arrow `stroke`. In the GEMV figure it is the line `stroke`. In the widget it is the cell `fill`.
Problem: `cssVar()` reads the token once, when the SVG is drawn, and `course.js` `toggleTheme()` only flips `data-theme`. After a toggle the SVGs keep the old palette.
Evidence: I loaded the page in light mode and set `data-theme="dark"`. The widget then showed bright `#f2f0ea` light-mode cells on the dark `#1b1e25` panel, and the "now" cell stayed the dark-orange light-mode `#c2410c`.
Concrete fix: let CSS resolve the colours instead of baking them in.
- Arrows: use `class: "s-acc"` / `"s-blu"` / `"s-grn"`, which already exist in course.css, instead of `stroke: cssVar(...)`.
- Widget cells: use `style: "fill:var(--accent)"` / `"fill:var(--green)"` / `"fill:var(--surface-2)"`, or add `.f-s2{fill:var(--surface-2)}` to course.css.
- Both work because `var()` resolves at paint time.

### V4 [major] Every diagram becomes unreadable at phone width
Location: all three `<figure><svg viewBox="0 0 760 …" width="760">` and `#w-svg` (680).
Problem: at 390 px the SVGs render at 340/324 px, a scale of 0.45–0.48. The 11 px labels (`@fadds(out,in,v)`, the route text, "middle", "PE 3" in the widget) become about 5 px. The route annotations in the multicast figure cannot be read at all.
Evidence: computed scale factors at 390 px were 0.45 (all three figures) and 0.48 (the widget). I confirmed by eye in the 390 px screenshots.
Concrete fix:
- **Multicast figure:** the content only spans x ≈ 150–620, so crop it with `viewBox="140 8 490 290"`, which gives a scale of 0.69. Raise the route text to 13 px.
- **Reduction-roles figure:** at narrow widths (`matchMedia("(max-width:600px)")`), draw PEs 0–5 in two rows of three, or wrap the SVG in `<div style="overflow-x:auto"><svg style="min-width:600px">`.
- **Widget:** set `cw = Math.min(24, 600/M)` → `cw = 600/M`, and size the viewBox to the content: `viewBox="0 0 ${44+M*cw+8} ${20+P*ch+10}"`. The grid then fills the width.
- **GEMV figure:** crop it to `viewBox="170 0 500 250"`.

### V5 [major] The multicast figure does not match program 05 (PE count, root result, "R receivers")
Location: the `#bc` drawing loop and the figcaption "One send, R receivers".
Problem:
1. The loop draws 5 PEs (`r < 5`), but the program output right below it says "reached all 6 PEs" (R = 6 in `commands.sh`).
2. The root also computes `y = 1·x` (`t_send` runs `@fmuls(y_dsd, x_dsd, s[0])`, and the output row 0 is `[-1, …]`), yet the figure labels the root only "sends x once".
3. The root's route is `rx RAMP → tx SOUTH`, with no RAMP in its tx, so the root does not receive its own broadcast. There are R−1 fabric receivers and R results. "R receivers" is wrong.
4. The arrows are 11 px stubs where the arrowhead is the whole arrow, so the "flows south" reading is weak.
5. Nothing shows that the host copies `x` to the root only and `s` to all R PEs, and that contrast is the point of the program.
Evidence: `programs/05-column-broadcast/{layout.csl,pe_program.csl,run.py,expected_output.txt}`.
Concrete fix:
- Draw 6 rows: `for (let r = 0; r < 6; r++)`, with `y = 16 + r*46` and boxes 36 px high. Set `viewBox` height to 300.
- Change the root's left label to `sends x · y = 1·x`.
- Change the caption to `<b>One send, R − 1 fabric receivers, R results.</b> The root's route has no RAMP in tx, so it computes y from its own copy of x…`.
- Add a small "host" box above the root with an arrow labelled `memcpy_h2d: x → root only` and a side bracket `s → all R PEs`.
- Lengthen the arrows by using 18 px gaps.

### V6 [major] The GEMV figure has no arrows, the wrong colour name, misaligned labels, and colour codes that conflict with the reduction figure
Location: the `#gemv` drawing loop and its figcaption.
Problem:
1. The caption says "Blue arrows" and "Orange/teal". The code draws `line` elements with no `marker-end`, and `--green` is green (#15803d / #4ade80), not teal.
2. The `x[c] ↓` labels sit at `x+35` (the box centre), while the blue broadcast lines sit at `x+20`, so labels and lines are 15 units apart. No line connects a label to the top row.
3. In the reduction-roles figure, c1 is **blue**. Here c1 is **green** and blue means the x broadcast, so the same colour encodes two different things on one page.
4. The `→ y[r]` labels float 30 px to the right of column 3, with no connector.
5. The figure leaves out `b`, which gemv-08 loads into the left column (README: "copies b into the y tensor of the left column"). It also leaves out that x starts *in* the top-row PEs, copied there by the host.
Evidence: SDK `tutorials/gemv-08-routes-3/README.rst` and `layout.csl` lines 61–79.
Concrete fix:
- Add `<marker>` defs (`g0` orange, `g1` blue, `g2` blue) and draw `path`s with `marker-end`.
- Put the broadcast lines at `x+35`.
- Colour the row-reduction links with the reduction figure's palette: even column sends c0 = orange, odd column sends c1 = blue. Draw the x broadcast in a third colour (`--purple`, class `s-pur` / `f-pur`, which needs adding to course.css) and say so in the caption.
- Add `b[r]` labels on the left feeding column 0, and draw a line from column 3 to `y[r]`.
- New caption: `Purple: x multicast down each column (x_color). Orange/blue: checkerboard row reduction of partial y (ax_color_1/ax_color_2), west to east; y is read from the rightmost column.`

### V7 [minor] The widget's formula disagrees with the text, and the readout labels are loose
Location: the paragraph before the widget ("about **M + P** steps, not **M × P**") and `frame()` (`≈ M + 2P` / `≈ P × M`).
Problem: the text says M + P and the widget says M + 2P. The totals actually computed are `(P−1)·2 + M` and `(P−1)(M+2) + M`. A learner who checks the counter (26 at P = 8, M = 12) against either label gets a different number.
Concrete fix: change the text to "about **M + 2P** cycles (one cycle per element, roughly two per hop)", and print the exact formula in the readout: `streaming: M + 2(P−1) = 26` / `store-and-forward: P·M + 2(P−1) = 110`.

### V8 [minor] The widget has no legend, no step or pause control, and cannot be replayed cleanly
Location: the `#pipe` widget.
Problem:
- Nothing says what orange or green means. The code uses orange for "processing now" and green for "done".
- Play has no Pause, Step or Replay state, and a second click silently restarts.
- Rows are not labelled with roles (`@fmovs`, `@fadds`, last PE into memory).
- In store-and-forward mode the "receiving into buffer" phase is not drawn, so row p looks idle while it is actually busy receiving.
Concrete fix:
- Add a legend line under the SVG: `■ element being processed  ■ done  □ not yet arrived`.
- Make the button a toggle (Play/Pause) and add a "Step" button that moves `t` by 1.
- Add role tags after the PE labels: "PE 0 send", "PE k add+fwd", "PE P−1 add→mem".
- In store-and-forward mode, shade the cells of row p in `--blue-soft` while row p−1 sends: from time `(p−1)(M+2)+i` to `p(M+2)`, showing it is receiving into a buffer.

### V9 [minor] Widget row labels drift below their rows at large P
Location: `frame()`. The text is at `y: 20 + p*ch + ch/2 + 4` and the rect at `y: 14 + p*ch`.
Problem: the label baseline sits about 11 units below the row centre. At P = 12 (ch ≈ 18), "PE 11" renders below the last row.
Concrete fix: set the label to `y: 14 + p*ch + (ch-3)/2`, with `"dominant-baseline": "middle"`.

### V10 [minor] Low contrast in dark mode (empty cells, Play button)
Location: widget cells (`--surface-2` #232731 on `--surface` #1b1e25) and `.btn` (white on #fb923c in dark mode).
Problem: in dark mode the empty grid cells are barely distinguishable from the panel. The white "Play" label on light orange is about 2.2:1, which fails WCAG AA for text. `.btn` is defined in course.css, so this is a course-wide issue.
Concrete fix:
- Give the empty cells a stroke: `stroke: var(--border)`.
- In course.css, under both dark selectors, add `.btn { color: #1b1e25; }`, which gives about 8:1.

### V11 [minor] Small naming and labelling mismatches in the reduction-roles figure
Location: the `#red` bottom line "middle PE routes: c_recv rx WEST → tx RAMP · c_send rx RAMP → tx EAST".
Problem: the code names are `recv_c`/`send_c` (layout) and `recv_color`/`send_color` (PE params), never `c_recv`/`c_send`. The figure also draws 6 PEs without saying so, while the program default is P = 8. The `c0`/`c1` labels are plain text sitting on the arrows. Finally, c0 is drawn in the same orange as the first/last box fill, so "orange" means both "end role" and "colour 0".
Concrete fix:
- Rename the text to `recv_c: rx WEST → tx RAMP · send_c: rx RAMP → tx EAST`.
- Add "(P = 6 shown)" to the top title.
- Colour the `c0`/`c1` labels with `f-acc`/`f-blu`.
- Give the first and last boxes the `.grn` class, or a dashed outline, instead of `.acc`.

## Proposed new visuals (prioritised)

### N1 (high) Side-by-side "race" for the wavefront widget, plus a cost-versus-P plot
Purpose: make "streaming is about M + 2P, store-and-forward about P·M" visible at a glance, which V2 currently prevents.
Content: replace the Mode select with two stacked grids, labelled "streaming (`@fadds` fabric→fabric)" and "store-and-forward (receive to memory, add, send)", driven by one shared clock (fixed 60 ms per cycle). The streaming grid finishes, turns its border green and shows "done at cycle 26", while the store-and-forward grid keeps going until 110. Below them, a small line chart has x = P (2..12) and y = cycles, with two lines, `M + 2(P−1)` and `P·M + 2(P−1)`, at the current M. A dot marks the current P, and the gap is labelled "×4.2".
Interaction: P and M sliders (which stop and reset the run, per V1), Play/Pause, Step, Replay.
Where: replaces the current `#pipe` widget.

### N2 (high) Measured versus model: where the cycles go
Purpose: the paragraph after the widget says "the simulator agrees with the model", but it shows a table in which kernel time is invisible. A chart makes clear that host I/O dominates and that the reduction itself barely grows with P.
Content: stacked bars for P = 2, 4, 8, 16 at M = 32. The total heights are the measured 4,394 / 4,496 / 4,748 / 5,260 cycles (tag: Measured). A thin top segment shows the model kernel cost `M + 2(P−1)` (34 / 38 / 46 / 62, tag: Derived), and the rest is labelled "host I/O + launch". A second, small panel at P = 8 plots M = 8, 32, 128 against 3,025, 4,748, 11,463, with a fitted slope of about 70 cycles per element. Each element crosses the host link twice.
Interaction: hover each bar for its numbers, and a toggle switches between absolute values and "difference from P = 2".
Where: replaces or sits beside the measured table under "Why it is fast".

### N3 (medium) Router-level checkerboard stepper: why one colour per link is not enough
Purpose: the chapter claims two colours are needed (layout.csl comment), but nothing shows why. Learners copy the parity trick without understanding it.
Content: 4 PEs, each drawn as a CE box plus a router box with 5 ports (RAMP, N, S, E, W). Each colour's route is drawn as port-to-port lines inside the router, with c0 in orange and c1 in blue, exactly as `@set_color_config` sets them for P = 4. Wavelets are small dots carrying the element index.
Interaction: Step, Play, and a toggle "use one colour for all PEs". In one-colour mode a middle router needs both `rx WEST → tx RAMP` and `rx RAMP → tx EAST` on the same colour. The stepper highlights that conflict in red ("one route per colour per router: the router cannot tell incoming from outgoing") and refuses to advance.
Where: directly after the reduction-roles figure, before the layout.csl code.

### N4 (medium) Host-to-device data mapping for both programs
Purpose: the memcpy rectangles (`memcpy_h2d(vs, V.ravel(), 0, 0, P, 1, M)`, d2h from `(P−1, 0)`, `x` to `(0, 0)` only, `s` to a `1 × R` rectangle) are where most learner bugs come from, and the chapter never draws them.
Content: on the left, the host array V (P × M) with coloured rows. Arrows go from row x to PE x in a 1 × P strip, and a return arrow goes from PE P−1 to `out[M]`. A second panel shows `x[M]` going to the root only and `s[R]` split one float per PE, with `y` (R × M) returning from all R PEs.
Interaction: hover a host row to highlight its destination PE and the matching `memcpy_*` argument tuple.
Where: just before `{{code:.../run.py}}` for program 03. The second panel goes in the program 05 section (it pairs with pedagogy finding P4, which adds run.py).

### N5 (medium) Multicast timeline compared with relay-by-CE and host copies
Purpose: show what `.tx = {RAMP, SOUTH}` buys.
Content: three swimlane timelines for R = 6, M = 32.
- (a) Host copies x to every PE: R−1 extra host transfers.
- (b) Each PE receives into memory and then re-sends with `@fmovs`: store-and-forward, about R·M.
- (c) Router multicast: wavelet i reaches row r at about i + r, so the total is about M + R.
Lane (c) is labelled "no CE instructions on PEs 1..R−1 until data lands".
Interaction: R and M sliders, and hover to read the cycle count for each lane.
Where: after the corrected multicast figure (V5).

### N6 (low) Animated GEMV phases
Purpose: turn the static composition figure into the three phases the text names.
Content: the corrected 3 × 4 grid from V6, with three phases:
- Phase 1: x wavelets flow down the purple columns.
- Phase 2: each PE's tile flashes "partial y += A_blk · x_blk".
- Phase 3: partial y flows west to east on alternating orange and blue links and accumulates into column 3.
Interaction: three phase buttons plus Play. A "pipelined" toggle shows that phase 3 in column c can start while column c+1 is still in phase 2.
Where: replaces the static `#gemv` figure.
