# ch10 · visuals review

Summary: I rendered the page with Playwright at 1100px and 390px, in light and dark, and also flipped the theme with the ◐ button after load. The page has two static figures: the SAXPY sequence diagram (drawn by JS) and the program 02 streaming path. It has no interactive element, although the other chapters use `.widget`. The labels in both figures match the sources: N=64, a=2.5, 100 floats, stats[4]/count[1], queue 2, and RXCOMMAND = color 22 (checked in `csl-libs/memcpy/sys_params.csl:48`). The real problems are these. Both SVGs become unreadable at phone width. The sequence diagram does not follow a theme toggle. The output blocks hide the device-vs-numpy digits that the prose talks about, even on desktop. And the streaming figure leaves out the `wait_done` barrier, which is the main lesson of the lab.

## Findings (defects in existing visuals)

### V1 [major] Both SVG figures shrink to illegible text on mobile
- Location: `src/10-lab-first-programs.html`, both `<figure>` blocks (`viewBox="0 0 760 330"` and `viewBox="0 0 760 180"`).
- Problem: At 390px the SVGs render at 340px wide, a scale of 0.45. The 12px labels in `.seq text` come out at about 5.4px, and the 11px muted sub-labels in the streaming figure (`color MEMCPYH2D_1`, `@initialize_queue`, `runs 100 times`) at about 5px. Nobody can read them.
- Evidence: Measured `svg.getBoundingClientRect().width` = 340 at 390px. Zoomed screenshots of fig0/fig1 at 390 in both themes show blurry labels you cannot read.
- Concrete fix: (a) Sequence diagram: wrap the SVG in `<div style="overflow-x:auto">` and give the svg `style="min-width:600px"`, so it scrolls instead of shrinking. Or rebuild it in JS with the four lifelines at x = 60/230/400/560 in a 620-wide viewBox, which gives scale 0.55 at the minimum. (b) Streaming path: add a vertical variant. In the page script, if `innerWidth < 600`, set `viewBox="0 0 300 470"` and place the five boxes in a column at y = 10, 100, 190, 280, 370 (each 260×64), with arrows `M150 y+64 V y+90`. The simplest way is to build both layouts in JS from one array `[[label, sub, cls], ...]`.

### V2 [major] Sequence-diagram arrows ignore the theme toggle
- Location: page script, `el("path", { ..., stroke: cssVar("--blue"), ... })`.
- Problem: The stroke colour is read once, at load. If you load in light mode and then press ◐, the page goes dark but the arrows keep the light-mode `--blue`, a darker blue, so contrast against the dark surface drops. Arrowheads use `class="f-blu"` and do switch, so line and head end up different colours. The same thing happens going from dark to light.
- Evidence: Screenshot after `click('header.topbar button')` from light: the background is dark and the arrows are saturated #2b5bd7-style blue. Compare the native dark render, where the arrows are light periwinkle.
- Concrete fix: Replace `stroke: cssVar("--blue")` with `class: "s-blu"` (already defined in `course.css`). Then CSS handles the theme.

### V3 [major] Output blocks hide exactly the digits the prose discusses
- Location: `{{out:programs/01-saxpy/expected_output.txt}}` and `{{out:programs/02-wavelet-tasks/expected_output.txt}}`, plus the paragraph "The last digit of element 2 differs (…295 vs …293)".
- Problem: The output lines are 996px and 1126px wide inside an 826px box at desktop, and inside 356px at mobile. At 1100px the visible text stops at `expected: [ 0.64329517 -0.5888347   3.18`, so the reader cannot see the `…293` the text points to. For program 02, the `expected:` half, which carries the 26.13794 / 3302.5327 comparison, is entirely off-screen. On mobile only `tasks fired: 100  stats: [  26.137941 3302` is visible.
- Evidence: `pre.scrollWidth` vs `clientWidth`: [996, 826] and [1126, 826] at 1100px; [996, 356] and [1126, 356] at 390px. Screenshots pre3-1100 and pre7-390.
- Concrete fix: Keep the raw output block. Directly below each one, add a small comparison table in the src, so it does not depend on scroll:
  - Program 01: columns `i | device | numpy (a*x+y)`, rows i=0..3: `0.64329517 | 0.64329517`, `-0.5888347 | -0.5888347`, `3.1845295 | 3.1845293` (the last digit highlighted with `<mark>`, plus the note "FMA, 1 ulp"), `1.5826113 | 1.5826113`.
  - Program 02: columns `stat | device | numpy`: sum `26.137941 | 26.13794`, sum sq `3302.5337 | 3302.5327`, max `9.614744 | 9.614744`, min `-9.883508 | -9.883508`, and a caption "count = 100, rtol 1e-4".
  - Optional, as a course.css change that is out of scope here: `pre.output { white-space: pre-wrap; }`. The outputs are short logs, so wrapping is harmless.

### V4 [major] Streaming-path figure leaves out the barrier and readback (the lab's central bug)
- Location: the second `<figure>` (host → memcpy west → input queue 2 → on_value → stats).
- Problem: The figure shows only data flowing in. The lab's key point, set out in the callout and the third objective, is that `memcpy_h2d(streaming=True)` returns once the wavelets are *injected*, and `wait_done` keeps the command stream blocked until `count == N`. None of that appears in the figure, so it suggests the host can read `stats` as soon as the stream "arrives".
- Evidence: The SVG contains no element for `wait_done`, `host_waiting`, `unblock_cmd_stream` or `memcpy_d2h`. The caption says only "Dataflow on one PE".
- Concrete fix: Extend the viewBox to `0 0 760 260` and add a second, return lane below the data lane:
  - A dashed amber arrow from host down to a box `wait_done()` (RPC on color 22), labelled "launch('wait_done')".
  - From `wait_done()`, a branch labelled "count==N? unblock : host_waiting=true".
  - A dashed arrow from `on_value(v)` to `wait_done` labelled "100th task: unblock_cmd_stream()".
  - A final arrow from `stats[4]` back to host labelled "memcpy_d2h(stats), memcpy_d2h(count)".
  - Replace the footer text with "Arrival triggers the work; the barrier decides when the host may read it."

### V5 [minor] The stream colour is shown as a symbol name, not the colour actually used
- Location: streaming figure, sub-label `color MEMCPYH2D_1`.
- Problem: `commands.sh` passes `--params=MEMCPYH2D_DATA_1_ID:0`, so the stream runs on color 0. The figure shows only the memcpy parameter name. The sequence-diagram caption, by contrast, gives a concrete number (22), so the two figures are inconsistent.
- Evidence: `02-wavelet-tasks/commands.sh` and `layout.csl` (`.MEMCPYH2D_1 = MEMCPYH2D_DATA_1_ID`).
- Concrete fix: Change the sub-label to `color 0 (MEMCPYH2D_1)`. Widen the memcpy box to 150 if needed and shift the following boxes by 10.

### V6 [minor] The WSE-2 binding is described only in the caption
- Location: streaming figure caption, "On WSE-2 the same code binds the task directly to the color".
- Problem: The architecture difference is the reason for the `@is_arch` ternary in `pe_program.csl`, but the figure shows only the WSE-3 path.
- Concrete fix: Add a thin muted bypass arc from the memcpy box over the "input queue 2" box to `on_value(v)`, labelled `WSE-2: data_task_id = color`. Label the straight path through the queue box `WSE-3: data_task_id = iq 2`.

### V7 [minor] The "memcpy runtime" lifeline mixes the host runtime with the on-PE memcpy module
- Location: sequence diagram, `cols` array (`"memcpy runtime"` at x=300).
- Problem: The caption says "memcpy's control tasks on the PE decode it", so the actor that writes SRAM is the memcpy *module compiled into your PE* (`sys_mod`). The lifeline name suggests a host-side runtime. A learner cannot tell where the color-22 hop happens.
- Concrete fix: Rename the lifeline to `memcpy (fabric + sys_mod on PE)`. Alternatively, split it into two lifelines, `SdkRuntime` (x≈210) and `memcpy module (on PE)` (x≈360), and label the hops between them `cmd · color 22`, `data · color 23` for h2d and `data · color 21` for d2h. Those three colour values come from `sys_params.csl`: RXCOMMAND=22, MEMCPYH2D_DATA=23, MEMCPYD2H_DATA=21.

### V8 [minor] The "stream blocked" interval is only a label, not a visible span
- Location: sequence diagram, steps at y=170 to 220.
- Problem: The caption's key idea is that the command stream stays blocked between `call saxpy` and `unblock_cmd_stream()`. In the drawing that is just text on one arrow. The `@fmacs` label (bbox x 531–679) also runs right up to the SRAM lifeline and arrowhead at 686–690.
- Concrete fix: Add `el("rect", {x: 294, y: 160, width: 12, height: 62, class: "amb", rx: 2}, g)` as an activation bar on the memcpy lifeline, plus a muted text label "cmd stream blocked" at x 250 (right-anchored). Shorten the arrow text to `call saxpy(2.5)`. Change the fmacs label to `@fmacs ×64` so it clears the lifeline.

### V9 [minor] The sequence diagram leaves out load/run and the host blocking on launch
- Location: sequence diagram `steps`.
- Problem: `run.py` calls `rt.load(); rt.run()` before any memcpy. `launch(..., nonblock=False)` also does not return until the RPC unblocks. Without that, the next `memcpy_d2h` seems to follow at once, when it actually waits on the unblock.
- Concrete fix: Add a first step `[90, 300, "load() · run()", 40]` and shift the others down by 15 (viewBox height 345). Add a dashed return arrow `[300, 90, "launch returns", 232]`, drawn with `stroke-dasharray: "4 3"`.

### V10 [minor] SVG accessibility
- Location: both `<svg role="img">`.
- Problem: The aria-labels ("SAXPY sequence", "Streaming path for program 02") are labels only. A screen-reader user does not get the call sequence.
- Concrete fix: Add `<desc>` listing the steps in order, for example "Host copies x then y into SRAM, launches saxpy(2.5), memcpy blocks the command stream until the PE calls unblock_cmd_stream, host reads y back."

## Proposed new visuals (prioritised)

### P1 Step-through of the SAXPY run sequence (high)
- Purpose: Turn the static sequence diagram into a stepper, so the learner sees what each host call does on the PE and when the command stream is blocked.
- Content and data: The 11 steps of V7/V9 (`load/run`, `h2d x`, write x, `h2d y`, write y, `launch saxpy(2.5)`, call saxpy (stream blocked), `@fmacs` ×64, `unblock_cmd_stream`, `d2h y`, read y → 64 floats). Each step highlights the active arrow and the matching line in `run.py` or `pe_program.csl`, given as line references in a JS array. Beside the diagram, a mini SRAM panel shows the first 4 elements of x and y. The values come from `rng(0)`, and the y panel ends at `[0.64329517, -0.5888347, 3.1845295, 1.5826113]` after the `@fmacs` step. A "cmd stream" pill turns red while blocked.
- Interaction: Prev / Next / Play buttons (`.btn`, `.btn.secondary`) and arrow keys. A readout (`.readout`) explains the current step in one sentence, for example "color 22 command decoded by sys_mod: write 64 words at &x".
- Placement: Replaces the existing "What happens inside, in order" figure, reusing its `#seq1` drawing code inside a `.widget`.

### P2 Race-condition timeline: injection vs consumption (high)
- Purpose: Make the bug in the callout visible: the host read `stats` after 95 of 100 tasks.
- Content and data: Two horizontal tracks over time. The top track, "wavelets injected", shows 100 ticks ending at time T_inj, where `memcpy_h2d` returns. The bottom track, "on_value() ran", shows 100 ticks, each a little later, ending at T_done. A vertical "host reads stats" marker sits at T_inj without the barrier and at T_done with it. A counter readout shows "tasks run: 95 / 100 · sum = 30.818176 (expected 26.137941)". The partial sums come from `np.cumsum(rng(1).uniform(-10,10,100).astype(f32))`; precompute the 100 values in build.py, or inline them as a JS array, so that index 95 shows 30.818176 exactly.
- Interaction: A toggle "with wait_done() / without". A slider for queue lag (0–10 wavelets) moves the read marker and updates the partial-sum readout. Make the lag illustrative and label it "illustrative lag" with a `derived` tag, because the simulator's actual gap of 5 was measured only at N=100.
- Placement: Directly above the "The bug, and the debugging method" callout.

### P3 Animated wavelets triggering tasks (medium)
- Purpose: Show "arrival is the trigger" in motion, and the WSE-2 vs WSE-3 binding difference.
- Content and data: The extended streaming figure (V4/V6). Dots (wavelets) carrying values from the real data array travel host → memcpy → input queue 2 → on_value. Each arrival flashes the on_value box and updates live `stats` (sum, sumsq, max, min) and `count`. An arch switch, WSE-3 or WSE-2, reroutes the dots through the queue or straight to the task (`data_task_id = iq 2` vs `= color 0`).
- Interaction: Play/pause, speed, an arch radio button, and "step one wavelet". Respect `prefers-reduced-motion` by defaulting to step mode.
- Placement: Replaces or sits directly under the streaming-path figure, before the bug callout, and connects to P2.

### P4 SRAM budget calculator for exercise 1 (medium)
- Purpose: Help the learner answer "does N:4096 / N:6000 still fit in 48 KB?" visually.
- Content and data: A 48 KB bar split into x (4·N bytes), y (4·N bytes), and "code + memcpy + stack (unknown, measure)". Use `--params=N:<n>` values 64, 4096 and 6000, plus a slider. Mark the point where 8·N alone exceeds 48 KB (N > 6144), tagged `derived`. Do not invent a code size. Show it as a hatched "measure with cslc" segment, or fill it only if someone measures the real figure from the compiled ELF.
- Interaction: A slider for N from 64 to 8192 with a readout of bytes used and bytes free.
- Placement: Inline with Exercises (Program 01), next to item 1.

### P5 Device-vs-numpy diff tables (low effort, high clarity)
- Already specified in V3's fix. Highlight the differing digit with `<mark>` and add a `measured` tag next to "7,740 simulated cycles" and "7,020 simulated cycles".
