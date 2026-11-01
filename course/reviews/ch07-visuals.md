# ch07 · visuals review

Summary: Chapter 7 has two visuals: a static halo-columns figure, drawn by JS, and an animated command-stream timeline widget about the program-02 race. Both render without console errors at 1100 px and 390 px, in light and dark. Neither causes horizontal page scroll. The timeline is the chapter's best teaching device, but it contradicts itself at the key moment. When the dashed "read" line appears, its own counter shows about 73–79 data tasks done, while the label says the read saw 95. Its bar labels are low-contrast in both themes: the intended white text is overridden by CSS, giving 2.1–2.9:1 in dark mode. Its labels overlap in barrier mode, and both SVGs shrink to 5–6 px text on phones. The halo figure is correct in outline. It does not explain the two plain columns, the two plain rows or the data directions, and it labels only the west side "host I/O". The chapter explains the bandwidth gap, the resource reservations, the host rectangle/element mapping and the RPC unblock rule only in prose; each would gain from a visual.

Screenshots: `/home/user/cerebras-sdk/tmp/rev-ch07-vis/` (deleted after review). Driven: Play button, barrier checkbox on/off, toggling during playback, rapid re-Play, keyboard Enter on Play. Console: 0 errors, 0 warnings in all 4 renders.

## Findings (defects in existing visuals)

### V1 [major] Timeline: the on_value() counter at the read moment contradicts the "95 values" label
Location: `#cmd` widget, no-barrier mode, `play()` in the inline script.
Problem: The read line is drawn at t = readAt = 40. At that moment the data-task bar label is `on_value() × round((40-2)*100/52)` = 73 (the screenshot sampled 77–79 because of timer jitter). The red label next to it says "reads sum after 95 values". The widget exists to show that the read caught exactly 95 tasks, but its own numbers disagree. The disagreement is visible for about 0.5 s and is captured in any mid-animation screenshot. After the animation ends the bar says `× 100` with the line crossing it at about 73 % of its length, so the reader never sees "95".
Evidence: Playwright snapshot ~1.6 s after uncheck at 1100/light: SVG texts `["memcpy_h2d stream ×100","on_value() × 77","reads sum after 95 values = 30.818 ✕"]`. Code: `tasksEnd = 54`, `readAt = 40`, `done = (min(t,tasksEnd)-2)*100/(tasksEnd-2)`.
Concrete fix: Make the timing consistent with 95/100. Set `tasksEnd` so that 95 % of the task bar falls at the read time: with the bar starting at 2 and the read at 40, use `tasksEnd = 2 + (40-2)/0.95 ≈ 42`. In barrier mode, end `wait_done` at the same `tasksEnd` (42) and start the D2H at 42. Once `t >= readAt`, freeze a second label on the read line: `"D2H snapshot: on_value() × 95"`. Keep the bar counter running to 100 after the line, and grey out the part of the amber bar past the line with a hatched "too late" fill. The reader then sees 95 at the line and 5 tasks finishing after it.

### V2 [major] Timeline bar labels: wrong text colour, low contrast (dark mode 2.1–2.9:1)
Location: `#c-svg`, labels drawn with `fill: "#fff"` on the coloured bars.
Problem: `course.css` has `svg text { fill: var(--text) }`. A CSS rule beats an SVG presentation attribute, so the intended white text renders as `--text`. In light mode that puts near-black on saturated blue at opacity .8 (3.8:1). In dark mode it puts light grey on light pastel bars: blue 2.87, purple 2.66, green 2.09, amber 2.48:1. All of these fail WCAG AA for 11 px text. "memcpy_d2h stats" also spills past the end of its 14-unit bar onto the card background.
Evidence: Computed contrast with the course tokens (bar colour blended at its opacity over `--surface`): L blue 3.81, L purple 4.25, D blue 2.87, D purple 2.66, D green 2.09, D amber 2.48. Visible in `cmd-nobar-1100-dark.png` and `cmd-bar-1100-light.png`.
Concrete fix: Draw the bars with the soft/stroke classes (`class:"blu"`, `"pur"`, `"grn"`, `"amb"`) instead of `fill: cssVar(...)` with opacity, and leave the label as default `--text`. That pairing is already themed and passes AA in both modes. Alternatively, set the label colour with `style="fill:#fff"`, which beats the stylesheet, and drop the opacity, but white on dark-mode `#4ade80` would still fail. Put labels longer than their bar (such as "memcpy_d2h stats") above the bar at y = 20 instead of inside it.

### V3 [major] Timeline barrier mode: "launch wait_done" and "memcpy_d2h stats" labels overlap
Location: `#c-svg`, barrier mode, host-commands lane.
Problem: The `wait_done` bar is 14 units (70 px) wide, but its label at 11 px is about 90 px long, so it runs under the "memcpy_d2h stats" label that starts at the next bar. The result reads as "launch wait_memcpy_d2h stats".
Evidence: `cmd-bar-1100-light.png`, `cmd-bar-1100-dark.png`.
Concrete fix: Shorten the labels to `"H2D stream ×100"`, `"wait_done()"` and `"D2H stats"`. Also stagger them: put command labels above the bars (y = 20) with `text-anchor:start`. Or widen the time scale: `X = t => 150 + t*6.5` with `viewBox 0 0 680 220` still fits, since t ≤ 68.

### V4 [major] Both SVGs become unreadable at phone width (text renders at about 5 px)
Location: halo figure (viewBox 760 wide) and `#c-svg` (680 wide) at 390 px.
Problem: Both SVGs scale down to fit about 340 px (×0.45) or 324 px (×0.48). The 11–12 px labels become 5.0–5.7 px. The PE coordinates, "west/east", the two caption lines inside the halo SVG and every timeline label are illegible. The timeline also leaves three quarters of its height empty.
Evidence: `halo-390-dark.png`, `cmd-bar-390-dark.png`. Measured rendered sizes: halo 340×134, timeline 324×105.
Concrete fix: (a) Halo: move the two caption lines out of the SVG into the `<figcaption>`. Crop the viewBox to the grid (`viewBox="20 20 600 220"`), and drop the coordinate text in plain cells below 500 px with a `@media (max-width:500px){ #halo text.muted{display:none} }` rule. (b) Timeline: give the SVG a mobile layout. Below 500 px, rebuild it with `viewBox 0 0 360 260`, the lane names above each lane instead of in a 150 px left gutter, and 13 px text. Or wrap it in `overflow-x:auto` with a `min-width:560px` (the course already uses `.table-wrap` for this).

### V5 [minor] Halo figure: unexplained plain columns and rows, and a one-sided "host I/O" arrow
Location: halo figure (`#halo`).
Problem: (1) Columns x = 0 and x = 7 and rows 0 and 2 are plain with no explanation. These are exactly what the "7 columns narrower, 2 rows shorter" rule in the caption refers to (3 west + 2 east + 2 edge columns = 7). The figure is the natural place to show that sum and it does not. (2) "host I/O ←" sits only on the west side. The caption says D2H is multiplexed on the east, so a reader infers that results also leave westward, or does not know where they leave. (3) Nothing shows the direction of data. (4) The positions are schematic: the accuracy review A5 confirms the ELF counts but not the placement, and the figure does not say so.
Evidence: `halo-1100-light.png`; the caption says "must be 7 columns narrower and 2 rows shorter"; the accuracy review notes `wse3/memcpy.csl:594` "to the EAST of the core PEs" and `sys.csl:105` command color `rx WEST`.
Concrete fix: Shade x = 0, x = 7 and rows 0 and 2 with a hatched "reserved / edge" pattern, and add a bracket under the grid: "3 west + 1 you + 2 east + 2 edge = 8 = 1 + 7". Draw arrows: purple H2D/commands west → you; green D2H you → east. Label both ends "to/from host". Add "(positions schematic; counts measured from out/west, out/east ELFs)" to the caption.

### V6 [minor] Timeline: overlapping animations when Play or the checkbox is used during playback
Location: `play()`; `const anim = setInterval(...)` is never cleared on re-entry.
Problem: Each Play click or checkbox change starts a new 3 s interval while the previous one keeps running. Each tick of each interval deletes all `.dyn` elements and redraws its own state, so two timelines flicker over each other. In a test, toggling the barrier 400 ms after Play gave alternating frames from both runs (`on_value() × 58` and `× 63` within one sampling window). The final frame is correct only because the older run finishes first.
Evidence: Playwright `race.js`: click Play, wait 400 ms, check the barrier, sample `.dyn` texts.
Concrete fix: Keep `let anim` outside `play()` and call `clearInterval(anim)` at the start of `play()`. Better still, drive the animation with `requestAnimationFrame` and a start timestamp.

### V7 [minor] Timeline accessibility and motion
Location: `#cmd` widget.
Problem: The SVG has only `aria-label="Command stream timeline"`, and the `#c-out` readout has no `aria-live`, so screen-reader users get no result when they toggle the barrier. The animation ignores `prefers-reduced-motion`. In the barrier (success) case the read line is still red-dashed, which signals an error on the correct path.
Evidence: `getAttribute('aria-live')` returns null. In code, the `stroke: cssVar("--red")` is unconditional.
Concrete fix: Add `aria-live="polite"` to `#c-out`. Update the SVG `aria-label` with the outcome sentence on each play. When `matchMedia('(prefers-reduced-motion: reduce)').matches`, draw the final frame immediately. Use `--green` for the read line when `barrier` is true.

### V8 [minor] Timeline readout states unverified facts
Location: `#c-out` text.
Problem: "validated at N=100 and N=500" and "count read later shows 100" are not backed by `expected_output.txt`, which holds only the N = 100 barrier run (accuracy review, "Not verifiable"). The figure presents them as measured.
Evidence: `programs/02-wavelet-tasks/expected_output.txt`.
Concrete fix: Remove "and N=500" and "count read later shows 100". Or add the no-barrier run's output to the program directory and cite it.

### V9 [minor] Timeline colours are captured once, so a live theme switch leaves stale colours
Location: `fill: cssVar(c)` and `stroke: cssVar("--red")`.
Problem: The colours are resolved to hex when drawn. If the user switches theme (the course supports `data-theme`) after the animation ends, the bars keep the old palette until the next Play. In dark mode, light-theme `#1d4ed8` on a dark card is very low contrast.
Concrete fix: The class-based fills in the V2 fix also solve this. For the line, use `class:"s-red"` or `class:"s-grn"`.

## Proposed new visuals (prioritised)

### N1 (high) "Narrow door" bandwidth ladder plus transfer-time calculator
Purpose: Make the gap between 21 PB/s and 7 Gb/s visible, and show that the 200 µs TCP overhead dominates small transfers. The chapter currently states both only in prose.
Content and data: A horizontal log-scale bar chart (bytes/s, 10^8 to 10^17) with these bars:
- on-wafer SRAM aggregate 21 PB/s [vendor];
- 16 channels × 7 Gb/s ≈ 14 GB/s upper bound [derived];
- 1 channel ≈ 0.875 GB/s [sdk];
- one 100 GbE link 12.5 GB/s [sdk/derived].

Below the chart, a calculator. Inputs: transfer size as a log slider from 4 B to 44 GB, with presets "one f32", "64 KB", "48 KB×PE row of 750", "full 44 GB SRAM"; channels 1–16; transfer count 1–1000. Output: time = n × (200 µs + bytes / (ch × 0.875 GB/s)), shown as a stacked bar split into "TCP overhead" and "wire time". Also show the "% overhead" figure and the equivalent number of SRAM-bandwidth seconds. Edge cases: 4 B gives 99.99 % overhead; 44 GB with 16 channels gives about 3.1 s.
Interaction: sliders update live, and the chart highlights the bar for the selected channel count.
Placement: replace or follow the stat row in "The narrow door". Tag every bar with its provenance.

### N2 (high) Interactive host-call mapper: (x0, y0, w, h, elements per PE) to PEs
Purpose: The paragraph "four integers name a rectangle … element block k lands on PE k" is the core host-programming skill, and it is prose only.
Content and data: On the left, a host array drawn as a strip of N coloured cells. On the right, a user-rectangle grid of up to 8×4 PEs. Inputs: x0, y0, width, height and elements-per-PE (steppers), plus N computed as w × h × l. In ROW_MAJOR order, colour the host array as a [h][w][l] tensor so that block k = (y·w + x) lands on PE (x0+x, y0+y). Each PE shows its received slice indices, for example "PE(2,0): x[8..11]". Presets: program 01 (1,1,64), program 03 (row of P PEs, l = N/P), program 04 (stencil rows). If COL_MAJOR is included, its layout must first be confirmed from the SDK runtime docs (not available locally). Otherwise show ROW_MAJOR only and say so.
Interaction: hover a host cell to highlight its PE and offset. Out-of-rectangle values (x0 + w > rectangle width) show a red "would fail" message. A toggle for `memcpy_h2d_rowbcast` shows one row of host data replicated down the columns, with the host bytes counter dropping by a factor of h (3× in the SDK example).
Placement: right after "Six calls on the host".

### N3 (high) RPC / command-stream sequence diagram with unblock placement
Purpose: The rule "every RPC must call unblock_cmd_stream(), possibly from a completion task" and quiz Q1 are prose only. The existing widget covers only the streaming race.
Content: Three swim lanes (host, command stream on color 22, PE), with the commands `launch('f')` then `memcpy_d2h(y)`. A radio selector picks one of three cases:
(a) unblock at the end of a synchronous RPC: correct;
(b) the RPC starts an async send and unblocks immediately: the D2H overtakes the send and reads stale data (mark it red);
(c) unblock in the send's completion task: correct, and the D2H waits;
(d) no unblock on one of 4 PEs: the stream stays blocked and the host shows a spinning "hang" icon.
Show the stream as a gate icon that closes on RPC entry and opens on `unblock_cmd_stream()`.
Interaction: radio plus a Step button that advances one event at a time, with a caption for each step. For case (d), a PE selector picks which PE forgets.
Placement: in "The command stream", before the copy vs streaming section.

### N4 (medium) memcpy resource reservation map (colors, task IDs, queues), switchable between WSE-2 and WSE-3
Purpose: Turn the reserved-resource table into a visual "what's left for me" map, and fix the 9–23 task-ID confusion visually (accuracy A1).
Content and data:
- Row of colors 0–23: 20–23 memcpy (20 ctx-switch, 21 D2H, 22 cmd, 23 H2D). User-chosen streaming colors are drawn hatched; program 02's color 0 appears when a "program 02" preset is selected.
- Row of local task IDs: WSE-3 local IDs 8–30; memcpy uses 21, 24, 27, 28, 30, 29 (teardown) and 31 (NOP). On WSE-2, IDs 0–23 are shared with the color data-task IDs.
- Row of control-task IDs: 33–37 and 40.
- Queues: 0 and 1 reserved on WSE-3, 0 only on WSE-2.
Colour coding: memcpy (purple), free (green), used by the course programs (orange outline: colors 0–3, tasks 9–13, queues 2+).
Interaction: an arch toggle, a program preset dropdown (01–05), and hover tooltips that cite the `sys_params.csl` line.
Placement: replace the table, or sit directly above it in "What --memcpy adds".

### N5 (medium) Copy mode vs streaming mode side-by-side animation
Purpose: Show why copy mode is safe and streaming is not (pedagogy P4). In copy mode memcpy writes the symbol in memory with no user code involved. In streaming mode, each element is a wavelet on a user color that wakes the user's data task.
Content: Two panels, each showing host → west halo → PE memory. Left panel: 8 words fill the `x[]` array directly, and the "done" tick fires when the last word lands. Right panel: wavelets queue in the PE's input queue, each triggers an `on_value()` box that updates `sum`, and the host "done" tick fires when the last wavelet leaves the host, while the queue still holds wavelets.
Interaction: Play/Step, plus a "device slowness" slider (1–5 cycles per task) that widens the gap between host-done and device-done in streaming mode only. This makes the race mechanism, not just the result, visible.
Placement: replace the two callouts in "Copy mode vs streaming mode", or sit just below them.

### N6 (medium) Fabric-dims and offsets calculator built from the halo figure
Purpose: Explain the `--fabric-dims` / `--fabric-offsets` arithmetic (pedagogy P2) and generalise the static 8×3 figure.
Content: Inputs: program width W (1–12) and height H (1–6). Output: a grid of (W+7) × (H+2) cells with 3 west columns, the W×H user rectangle at (4,1), 2 east columns, edge columns and edge rows, plus the generated `cslc` line: `--fabric-dims=${W+7},${H+2} --fabric-offsets=4,1`. A "real CS-2" toggle sets dims to 750,994 and shows the maximum rectangle 743 × 992. A note says the halo for `--channels 1` is measured and other channel counts are undocumented.
Interaction: steppers, with the copyable command line updating live.
Placement: replace the static halo figure (it would also fix V4 and V5).

### N7 (low) Stream-ordering hang demo (gemv-09)
Purpose: Explain why streaming b before x hangs: commands are serialized, and the device's tasks consume streams in a fixed order.
Content: The host queue holds two streams in a user-chosen order. The device waits on color A (x) first. With the wrong order, the b wavelets fill the input queue, the stream backs up and the command never completes, so a padlock appears.
Interaction: drag to reorder the two host commands, then press Run.
Placement: in "Ordering matters too".
