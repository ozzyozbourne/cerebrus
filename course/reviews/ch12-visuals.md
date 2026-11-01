# ch12 · visuals review

Summary: I rendered `12-lab-stencil.html` with Playwright at 1100px and 390px, in light and dark, and also switched the theme with the top-bar toggle. There are no console errors and no horizontal scroll at either width. The heat-rod simulation is numerically correct: at the defaults, its step-50 state matches all 16 cells sampled in `expected_output.txt` to every printed digit (checked in Node). The model widget's three plotted points match the measured table (98, 128 and 248). The main defects:
- **Theme toggle:** all three visuals take some colors from `cssVar()` once, at draw time. After the user clicks the toggle, the bands, arrows and lines keep the old theme's colors.
- **Model widget:** the n slider goes up to 5000, but the chart's x-axis stops at 128. For 97% of the slider's travel the chart does not change.
- **Mobile:** both SVG diagrams scale down to about 4–5px text at 390px.
- **α = 0.5:** at this edge value the rod widget draws an odd/even staircase. The page never explains it, and the readout calls the run "stable".
- **Unplotted data:** half of the measured table (P sweep, WSE-2, and the step-count sweep) is not plotted anywhere.

## Findings (defects in existing visuals)

### V1 [major] Theme toggle leaves the diagram and both widgets in the old theme
- **Location:** src lines 119–120 (decomposition arrows), 144 (heat bands), 147 (heat polyline), 172–176 (model lines, dots and cursor).
- **Problem:** `cssVar("--blue-soft")`, `cssVar("--accent")` and the others are resolved once and written into `fill`/`stroke` attributes. `toggleTheme()` in `course.js` changes only `data-theme` and fires no event, so nothing redraws.
- **Evidence:** I loaded the page in light mode and clicked "Toggle dark mode". The heat widget then showed near-white `#f2f0ea`/`#dbe6ff` bands on a dark card. The muted axis labels sit on those white bands with very low contrast. The model line stayed light-mode `--blue` and the arrows stayed light-mode `--accent`. The reverse also happens: dark OS, toggle to light, and you get navy bands on a light page.
- **Concrete fix:** use CSS-variable styles instead of resolved values.
  - Heat bands: `el("rect", {..., style: \`fill:var(${k % 2 ? "--blue-soft" : "--surface-2"})\`})`.
  - Polyline: `class: "s-acc"` plus `fill: "none"`.
  - Decomposition arrows: `class: "s-acc"` / `class: "s-pur"`.
  - Model fit line: `class: "s-blu"`. Fixed-cost line: `class: "s-pur"`. Dots: `class: "f-acc"`. Cursor: `class: "s-red"`.
  - All of these classes already exist in `course.css` lines 120–123. Do not pass a `stroke` attribute alongside the class.

### V2 [major] Model widget: the slider goes to n = 5000 but the chart stops at n = 128
- **Location:** src lines 91 (`max="5000"`), 166 (`nmax = 128`), 176 (`if (nn <= nmax)` hides the cursor).
- **Problem:** above n = 128 the red cursor disappears and the chart never changes. Only the readout text moves. The slider is 160px wide (120px on mobile), so each pixel is about 31 cells. The user cannot land on the measured points n = 4, 16 or 64, or even on 1–30, by dragging.
- **Evidence:** the screenshots at n = 16, 129 and 5000 show identical charts apart from the cursor, which is absent at 129 and 5000. `ArrowRight` steps by 1, so keyboard users need about 5000 presses to cross the range.
- **Concrete fix:**
  - Use a log x-axis from 1 to 5000, with ticks at 1, 4, 16, 64, 256, 1024 and 4096.
  - Map the slider to log2(n): `<input type="range" min="0" max="12.29" step="0.01">` and `nn = Math.round(2 ** v)`, or a fixed list of stops.
  - Always draw the cursor.
  - Draw the model as a curve on a log–log or log–linear plot, so it bends from "flat at 88" to "slope 2.5".
  - Add a second panel, or shade the area under the curve, to show compute share. That makes the surface-to-volume lesson visible rather than only printed in the readout.

### V3 [major] Both SVGs are illegible at phone width
- **Location:** the decomposition `<svg viewBox="0 0 760 210">` (font-size 10–12) and the heat `<svg viewBox="0 0 680 260">` (font-size 10–11). The model SVG (680×230) has the same problem.
- **Problem:** at 390px the figure renders about 342px wide, a scale of 0.45. Cell labels `u0…u5` come out at about 4.5px, and the two explanatory lines under the decomposition at about 5.4px. The heat axis labels (`hot end (1.0)`, `step 0`) are unreadable, as are the model's "measured 98" labels.
- **Evidence:** screenshots `390-light-figure.png`, `390-light-heat.png` and `390-dark-model.png`.
- **Concrete fix:**
  - Decomposition: the two grey sentences at y = 170 and 192 carry real content. Move them into the `<figcaption>` as HTML text and shrink the viewBox to about `0 0 760 150`. Remaining text is then only `PE k` and `u0…u5`; raise those to font-size 13–14.
  - Heat and model widgets: under `@media (max-width: 600px)`, redraw with a narrower viewBox (for example W = 340) and larger fonts. Alternatively, raise the base font-size to 14 and cut the tick count. Both widgets already rebuild their SVG in `draw()`/`model()`, so reading `svg.clientWidth` at draw time and choosing a layout is cheap.

### V4 [major] At α = 0.5 the rod widget draws a staircase, and the page calls it "stable"
- **Location:** src line 58 (`max="0.5"`), line 152 (`stable while α ≤ 0.5`).
- **Problem:** at α = 0.5 the update becomes u'[i] = (u[i−1] + u[i+1])/2. Even and odd cells then decouple, so the profile turns into flat pairs: a non-physical staircase.
- **Evidence:** the polyline y-values near the peak at step 50 come in pairs: `193.7 193.7 186.8 186.8 181.3 181.3 178.2 178.2 …`. The jagged hump is visible in `1100-light-heat-a05.png`.
- **Concrete fix:**
  - Extend the slider to `max="0.6"`.
  - In the readout, colour-code three regimes, each with a one-line explanation:
    - α < 0.5: smooth.
    - α = 0.5: marginal, odd and even cells decouple.
    - α > 0.5: unstable, the checkerboard grows.
  - Clamp the drawing to the axis range and show "blew up at step k" once max |u| exceeds 1e3, so learners can see why α ≤ 0.5 matters.
  - At minimum, change the readout to "stable for α ≤ 0.5 (smooth only below 0.5)".

### V5 [minor] Heat widget: Play stops at step 50 without saying so, and the button never changes to "Pause"
- **Location:** src lines 154–155.
- **Problem:** Play always stops at step 50, even for non-default P, n and α where step 50 has no special meaning. A second click continues to step 2000. The button label stays "Play" while the simulation runs, and the hard stop at 2000 is never shown.
- **Concrete fix:**
  - Set `$("#h-go").textContent = timer ? "Pause" : "Play"`.
  - Stop at 50 only for the validated configuration, and show "paused at the validated step; press Play to continue".
  - Add a "Step +1" button. Single-stepping is exactly what you want when relating the picture to one halo exchange plus update.

### V6 [minor] Heat chart: no axis titles, no PE labels, and the boundary values and validation evidence are not drawn
- **Location:** `draw()`, src lines 141–153.
- **Problem:**
  - The y-axis has no "temperature" title and the x-axis has no "cell index" title.
  - The bands are not labelled PE 0…P−1, so a learner cannot see that the default hot spot (global cells 62–65) straddles the PE 3 / PE 4 boundary. This is the most instructive fact in the picture: the heat must cross a halo.
  - The fixed ghost values 1.0 and 0.0 appear only as text. At step 50 the profile peaks at about 1.5 against a y-axis of 0–5, so 70% of the plot is empty.
  - The "validated" claim is text only.
- **Concrete fix:**
  - Add `PE k` labels at the top of each band, shown only when the band is at least 30px wide.
  - Add axis titles.
  - Draw the two boundary ghosts as hollow squares at x = X0 − ε and X0 + W + ε.
  - Add a "y-axis: fixed 0–5 / autoscale" toggle.
  - At P = 8, n = 16, α = 0.25 and step 50, overlay the 16 device samples from `expected_output.txt` (every 8th cell) as dots with the legend "device (simulator)". I confirmed they match the JS curve exactly.
  - Draw thin vertical lines at PE boundaries in the `--border` colour.

### V7 [minor] Decomposition diagram: the four colours and the fixed end ghosts are not shown
- **Location:** src lines 109–124 and the figure caption (line 37).
- **Problem:**
  - The caption names E0/E1/W0/W1 and the parity alternation, but no arrow is labelled. Both east arrows look the same, so the alternation the caption explains is invisible.
  - PE 0's `u0` and PE 2's `u5` are the rod-end Dirichlet ghosts (1.0 and 0.0), yet they are drawn exactly like the exchanged ghosts. PE 2 is the last PE only implicitly.
  - The canvas has about 30px of dead space below the text.
- **Concrete fix:**
  - Label each arrow with a small tag: "E0" for PE0→PE1, "E1" for PE1→PE2, "W1" for PE1→PE0, "W0" for PE2→PE1. These follow `layout.csl`: even PEs send E0/W0 and odd PEs send E1/W1.
  - Fill PE 0's `u0` and PE 2's `u5` with `amb` and label them "1.0 fixed" and "0.0 fixed".
  - Add "(last PE)" under PE 2.
  - Tighten the viewBox (see V3).

### V8 [minor] Model widget: label overlap and an inconsistent memory figure
- **Location:** src lines 174–181.
- **Problem:**
  - The "measured 98" label sits on top of the dashed 88 line and the fit line (visible at both widths).
  - The readout says "of 48 KB", but the over-capacity check uses 46 KB, giving `maxN = 5885`. The slider stops at 5000, so the warning can never appear.
  - At large n the latency prints as "14809 ns" instead of µs.
- **Concrete fix:**
  - Place the measured labels above-left of each dot, with a background halo (`paint-order: stroke; stroke: var(--surface); stroke-width: 3`).
  - Say "of ~46 KB usable" consistently.
  - Either extend the slider to about 6000 so the warning can fire, or remove the dead branch.
  - Format the time as µs when it exceeds 1000 ns.

### V9 [minor] Most of the measured table is never plotted
- **Location:** the table at src lines 68–76, the sentence at line 77, and the model widget.
- **Problem:** the model chart shows only the n-sweep. The P sweep (99 / 128 / 128.5 for P = 2 / 8 / 16), WSE-2 vs WSE-3 (125 vs 128), and the step-count sweep (0 / 10 / 50 / 100 steps) are text only. The step sweep also hides something: (5071 − 3991)/10 = 108 cycles/step for the first 10 steps, against about 130 marginal per step from step 10 to 100. The prose "linear, ~130 each" glosses over this, and the table's 128 is an average that includes the cheaper start.
- **Concrete fix:** see new visuals N2 and N3.

## Proposed new visuals (prioritised)

### N1 (high) Animated per-step timeline: four transfers, four completion tasks, then the update
- **Purpose:** make the "fixed ~88 cycles" concrete, and show that a step is a join of four asynchronous operations followed by three DSD instructions. This is the core control-flow idea of the lab, and today it lives only in code.
- **Content:** a Gantt chart for one interior PE, with these lanes:
  1. `@fmovs to_e` on oq 2 / microthread 2.
  2. `@fmovs to_w` on oq 3.
  3. `@fmovs from_w` on iq 4.
  4. `@fmovs from_e` on iq 5.
  5. Tasks `t_se`, `t_sw`, `t_rw`, `t_re`.
  6. `pending` counter (4→3→2→1→0).
  7. `update()`: `@fadds`, `@fmacs`, `@fmacs`, each about 2.5·n/3 wide (total 2.5·n).

  The four transfer bars plus tasks fill the fixed 88 cycles, then the update bar takes 2.5·n.
- **Honesty:** only the totals are measured. Mark the internal split as illustrative (`<span class="tag derived">`) and draw the 88 as one bracket labelled "halo + tasks + scheduling (measured total)".
- **Interaction:**
  - Play / step buttons that advance a time cursor, lighting each bar as it starts and decrementing `pending` as each task fires.
  - n stops at 4, 16 and 64, which redraw the update bar and the total (98 / 128 / 248).
  - An "edge PE" toggle that removes two lanes (P = 2 case: 99).
  - A "buggy queues (in 2/3)" toggle: lanes 1 and 4 collide on microthread 2, the cursor freezes with a red "no progress at cycle 1,894" stamp. This connects directly to "The hang" callout.
- **Placement:** right after "The hang" callout (src line 50), before the rod widget.

### N2 (high) Measured comparison chart for the cycles-per-step table
- **Purpose:** turn the six-row table into the three findings the text claims: linear in n, flat in P, and WSE-2 ≈ WSE-3.
- **Content:** a three-panel dot chart with a shared y-axis "cycles/step":
  - n sweep (P = 8): 4 → 98, 16 → 128, 64 → 248, with the fit 88 + 2.5n overlaid.
  - P sweep (n = 16): 2 → 99, 8 → 128, 16 → 128.5. Annotate P = 2 as "both PEs are edges: 2 transfers".
  - Architecture (P = 8, n = 16): WSE-3 128, WSE-2 125.
- **Styling:** every dot carries the `measured` tag colour, with direct value labels and no legend.
- **Interaction:** hovering a dot highlights the matching table row, and the reverse.
- **Placement:** directly under the table (after src line 76), replacing the need to read the numbers row by row.

### N3 (medium) Total cycles vs timesteps (the differencing method, drawn)
- **Purpose:** show why subtracting the 0-step run isolates the kernel, and expose the warm-up effect.
- **Content:** points (0, 3991), (10, 5071), (50, 10291), (100, 16791) for P = 8, n = 16, WSE-3.
  - A shaded band for the 0–3,991 intercept, labelled "host memcpy + launch (identical in every run)".
  - Segment slopes labelled 108, 130.5 and 130 cycles/step.
- **Interaction:** a toggle between "average from 0" (128) and "marginal" (130), plus a one-line explanation.
- **Placement:** replace the sentence at src line 77 with this small chart and a caption. Coordinate with the accuracy reviewer on wording.

### N4 (medium) Four-colour routing map for P = 4–6
- **Purpose:** the caption's "neighbours alternate by parity" is hard to picture.
- **Content:** a row of PEs. On each link, draw two arrows labelled with their colour: east E0 or E1, west W0 or W1, chosen by the sender's parity as in `layout.csl`.
  - Inside each PE, list its `send_e / recv_w / send_w / recv_e` and the `rx/tx` route for each colour (RAMP→EAST, and so on).
  - Edge PEs grey out the missing directions (`has_w` / `has_e` false).
- **Interaction:** click a PE to highlight its four colour configs and the matching lines of `layout.csl`.
- **Placement:** either extend the existing decomposition figure (V7 fix) or add it directly after `{{code:programs/04-heat-stencil/layout.csl}}`.

### N5 (low) Upgrades to the rod widget
- **Device overlay:** add the device-sample overlay at step 50 (V6).
- **Ghost inspector:** a "show ghosts" mode that, at each step, draws each PE's `u[0]` and `u[n+1]` as small hollow markers at the band edges, with the value just received.
- **Instability regime:** α up to 0.6 with the regime readout (V4).
- **Step +1 button:** (V5).
- **Placement:** in place, in the existing `#heat` widget.
