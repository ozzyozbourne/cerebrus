# ch05 · visuals review

Summary: I rendered the chapter with Playwright at 1100px and 390px, in light and dark. It has three visuals: the "wire to code" pipeline SVG, the task-picker widget and the Lab 3 state-machine SVG. The console showed no errors or warnings in any of the four renders, and the page never scrolls sideways (scrollWidth equals clientWidth at both widths). Dark-mode contrast is fine everywhere because every colour comes from tokens.
The main defects:
- At 390px all three SVGs shrink to about 45% of their size, so their text is 5–7px tall and unreadable.
- The "task table" in the first figure has columns that do not line up, because SVG collapses runs of spaces.
- The widget draws `update()` as a separate CE run that overlaps the `t_re` bar. In the real program `update()` is a function called inside the last done task.
- The widget is deterministic: "Run one timestep" draws the same picture every time, and the timeline never marks the activation that was lost.
- The state machine always shows 4 ops (edge PEs have 2), and its exit path has no arrowhead and no end state.

The best additions would be a microthread-collision widget for the WSE-3 hang, a timing control on the picker so the collapse shows up as timing-dependent, and a "buffered vs collapsed activation" visual.

## Findings (defects in existing visuals)

### V1 [major] All three SVGs are unreadable at phone width
- Location: figure 1 ("From wavelet arrival to task execution", viewBox 760×250), widget `#t-svg` (680×230), figure 2 ("Stencil state machine", 760×210).
- Problem: `img, svg { max-width: 100% }` with `height: auto` scales each diagram to about 340px wide at a 390px viewport, a factor of 0.45–0.48. The 11–13px labels end up 5–7px tall. You cannot read "route says RAMP", "WSE-3: bound to c", the task-table rows, the cycle axis numbers or "pending -= 1".
- Evidence: at viewport 390 the rendered SVG sizes are 340×112, 324×110 and 340×94. The bounding-box heights of the first SVG text elements are 7.0, 6.0 and 7.0 px. The full-page 390 screenshot shows the boxes and labels as specks.
- Concrete fix: give each SVG a vertical (portrait) layout for narrow screens, or wrap it in a horizontal scroller with a minimum width. The cheapest fix in course.css: `figure .hscroll{overflow-x:auto} figure .hscroll>svg{min-width:640px}`, then wrap all three SVGs in `<div class="hscroll">`. A better fix for figure 1 and figure 2: add a second `<svg class="narrow">` with the five stages stacked top to bottom (viewBox about 340×520), and toggle between the two with `@media (max-width:680px)`. For `#t-svg`, have the script read `svg.clientWidth` and use a shorter axis (0–12 at 22px per tick, labels 12px) when it is under 500px.

### V2 [major] Task-table columns in figure 1 are misaligned
- Location: figure 1, the amber "task table" box, lines `id  activated blocked`, `2   ●         ○`, `10  ○         ○`.
- Problem: SVG `<text>` collapses repeated spaces by default. The ● and ○ marks therefore sit right next to the ID, under "activated", and the blocked-column ○ ends up under the "c" of "activated". The reader cannot tell which column a mark belongs to. Since the figure's whole point is that a task must be activated and not blocked, this matters.
- Evidence: the 1100px light and dark screenshots show "2 ● ○" and "10 ○ ○" packed against the left edge of the box.
- Concrete fix: place each cell with its own `x`. Header `<text x="420">id</text><text x="458">act.</text><text x="510">blk.</text>`; rows `<text x="420">2</text><text x="466">●</text><text x="518">○</text>` and the same for 10. Alternatively add `style="white-space:pre"` to the three text elements. Also add a fourth line under the table, `9px muted: "2 = data task (input queue 2), 10 = local task"`, so the IDs tie back to the code snippet (`@get_input_queue(2)`) and to Lab 3 (`@get_local_task_id(10)`).

### V3 [major] The widget draws `update()` as its own CE run, and it overlaps `t_re`
- Location: widget `#tsk`, "four tasks" mode, JS `runs.push([t + 1, "update"])` with bars `width: 86` and `busyUntil = t + 2`.
- Problem: `t_re` occupies cycles 9 to about 10.9. The green "update" bar starts at cycle 10 and is drawn on top of it, so the t_re label is half covered. It also teaches the wrong model. In `programs/04-heat-stencil/pe_program.csl`, `update()` is a plain `fn` called from `op_done()` inside the task that brings `pending` to 0. It is not a separate pick, and the CE cannot run two things at once. The log line "cycle 10: pending hit 0 → update() runs" repeats the same error.
- Evidence: screenshot at 1100 light, four-task mode: the update bar covers the right half of t_re. Source: `fn op_done() void { pending -= 1; if (pending == 0) update(); }` and `task t_re() void { op_done(); }`.
- Concrete fix: draw the final done task as a longer bar (`busyUntil = t + 2 + 3` for the 3 vector ops). Show its last segment as a green inset rect labelled `update() inside t_re`. Change the log line to `cycle ${t}: t_re: pending = 0 → calls update() (same task)`. Drop the separate `runs.push([t+1,"update"])`.

### V4 [major] The lost activation is invisible on the timeline, and the run button does nothing new
- Location: widget `#tsk`, "one shared task" mode.
- Problem: the chapter's lesson is that two completions landing before `done` runs merge into one run. The SVG shows four purple dots and three amber bars, with nothing tying a dot to the run it caused, so the reader has to count. The merge appears only in the text log. The event times are hard-coded (`[[3,"se"],[4,"sw"],[4,"rw"],[6,"re"]]`), so "Run one timestep" redraws the same picture on every click. The design toggle also implies the shared task *always* hangs. The SDK's actual point is that the outcome depends on timing ("depending on the sequence of task activations and executions", benchmarks/25-pt-stencil/task.csl).
- Evidence: clicking `#t-run` three times leaves 47 identical SVG children. The dark one-task screenshot shows no marker on the `rw` dot.
- Concrete fix: (a) draw a thin connector from each dot to the bar it activated. For a merged activation, draw the dot as a hollow red ring with a red "×" and the label "merged: bit already set". (b) Add an "activation bit" row between the two existing rows: a step trace (0/1) per task, so the reader sees the bit set at cycle 4 while it is already 1. (c) Make the button useful: add a "Jitter completion times" checkbox. When it is on, each click draws completion times uniformly from 1–8. Keep a running tally in the readout: `shared task: 7 of 12 steps hung; four tasks: 0 of 12`. This is Proposal N2 below; it could replace this fix.

### V5 [minor] Widget timeline labels are hard to use
- Location: `#t-svg`.
- Problem: there is no axis title (the ticks are cycles, but nothing says so). The op labels `se/sw/rw/re` are cryptic without the hint text. The four-task bar names are `t_se…` but the real IDs (10–13) are never shown. The readout has no `aria-live`, so a screen-reader user who changes the select gets no announcement.
- Evidence: 1100 screenshots; `#t-out` has no `aria-live` attribute.
- Concrete fix: add `el("text",{x:350,y:230,"text-anchor":"middle","font-size":11,class:"muted"}).textContent="cycle (illustrative)"`. Expand the dot labels to `send E`, `send W`, `recv W`, `recv E`. Label the bars `t_se (10)` and so on. Add `aria-live="polite"` to `#t-out`. Keep the illustrative-timing note that the accuracy review (A2) asks for.

### V6 [minor] State-machine figure: fixed "4", unterminated exit, `fn` and task drawn alike
- Location: figure 2 ("Stencil state machine").
- Problem:
  - (a) "launch 4 async ops" and "4 done tasks" are wrong for the two edge PEs. In the source, `ops_per_step = (has_e?2:0)+(has_w?2:0)`, and with P == 1 (no neighbours) `start_step` calls `update()` directly.
  - (b) The `step == T` path is a bare line ending at a text label: no arrowhead and no end state.
  - (c) "=0" next to an arrow is ambiguous; it means `pending == 0`.
  - (d) There is no self-loop on "done tasks" for `pending > 0`, which is the case the widget is about.
  - (e) `run`, `start_step` and `update` are functions and only the four done boxes are tasks, but every box looks the same (pedagogy review P2).
- Evidence: the 1100 screenshots; `course/programs/04-heat-stencil/pe_program.csl` lines `ops_per_step`, `start_step`, `update`, `op_done`.
- Concrete fix:
  - Relabel the boxes to "launch 2–4 async ops (4 inside, 2 at edges)" and "done tasks t_se…t_re".
  - Add a self-loop arc on the purple box labelled `pending > 0: back to picker`.
  - Change "=0" to `pending == 0`.
  - Turn the top exit into an arrow into a new rounded box, `host unblocked (memcpy)`, at x≈580–760, y≈10.
  - Draw `fn` boxes with `stroke-dasharray="5 3"` and add a legend: `solid = task, dashed = fn called inside a task`.
  - Grow the viewBox height to about 230 to fit the legend.

### V7 [minor] Figure 1 leaves out the blocked path and the WSE-2 branch
- Location: figure 1.
- Problem: the caption quotes "activated and unblocked", but the diagram shows no blocked state, and the "input queue" box says only "WSE-3: bound to c". The bottom note explains WSE-2, but the boxes are drawn for WSE-3 only. Readers who see one pipeline will not see that the task ID is taken at a different stage on each chip.
- Evidence: the 1100 screenshot; the box text at line 31 of the HTML.
- Concrete fix: under the input-queue box, add two small tags pointing at the task table: `WSE-2: task ID = color c` (from the router arrow) and `WSE-3: task ID = queue q` (from the queue arrow). Add a dashed red branch from the task table, `blocked → stays in queue (a fabric DSD may drain it)`, ending at the queue box. This also gives the "Back-pressure" bullet a picture.

## Proposed new visuals (prioritised)

### N1 (highest) WSE-3 microthread collision explorer: the real hang from Lab 3
- Purpose: make the `.callout.bug` story concrete. The reader picks queue IDs and sees microthread conflicts before running anything.
- Content and data: four rows, one per async op of Lab 3: `send E (fabout, oq_e)`, `send W (oq_w)`, `recv W (fabin, iq_w)` and `recv E (iq_e)`. Each row has a queue-ID dropdown (0–7) and a `.ut_id` dropdown ("default = queue ID" or 0–7). On the right, 8 microthread lanes (UT0–UT7) show which op lands on each. Queues 0 and 1 are greyed out and tagged "memcpy on WSE-3" (as the code comment in this chapter says). Presets:
  - "first Lab 3 (hangs)": oq 2, 3 and iq 2, 3. Lanes UT2 and UT3 turn red. Readout: `UT2: send E + recv W concurrently → simulator stalled at cycle 1,894 [Measured]`.
  - "fixed Lab 3": oq 2, 3 and iq 4, 5. All lanes green.
  - "fixed via .ut_id": iq 2, 3 with `.ut_id` 4 and 5.
- Rule source: topic-15 README ("default to the respective queue IDs", "two operations cannot concurrently use the same microthread"). Add an "Architecture: WSE-2 / WSE-3" toggle. Under WSE-2 the microthread equals the queue ID and outputs are limited to 6 queues, so the dropdowns allow 0–5 and the same conflict rule applies.
- Interaction: the dropdowns update the lanes live; a conflict also shows a red flash on the bug callout.
- Placement: right after the "A real hang from this course" callout.

### N2 Timing-dependent collapse (upgrade of the existing picker widget)
- Purpose: show that one shared completion task fails *sometimes*, which is why the SDK's 25-pt stencil uses four tasks.
- Content and data: keep the current two lanes and add an "activation bit" lane per task. Four sliders set the completion cycle of se/sw/rw/re (0–10), plus a slider for task run length (1–4 cycles). Add a "Randomise × 20" button. It runs 20 random timesteps under both designs and plots two small bars: hung steps out of 20 for shared, and the same for four tasks (always 0).
- Interaction: when the sliders are spread apart (each completion arrives after the previous `done` run has finished), the shared design succeeds; the reader sees this and learns it is a race, not a guaranteed failure. Merged activations are drawn as a red ring (see V4).
- Placement: replaces the current `#tsk`.

### N3 Buffered vs collapsed: why data tasks never lose wavelets
- Purpose: resolve the apparent conflict between "activation is one bit" and "a data task runs per wavelet" (pedagogy P3).
- Content: two side-by-side lanes, animated. Left: a data task with an input queue (8 slots drawn as cells). Three wavelets arrive in the cycles before the task runs. They fill the queue, the bit stays 1 while the queue is not empty, and the task runs 3 times. Right: a local task getting three `@activate` calls or async completions in the same window. The bit goes 1, the second and third are absorbed, and the task runs once. Caption rule: "events that carry data are buffered; events that carry none collapse".
- Interaction: a "step" button and a "play" button, plus an arrivals slider (1–8). Past 8 arrivals the left queue fills, and the extra wavelets are drawn backing up into the router as a back-pressure stall. This also answers Check-yourself Q1.
- Placement: right after the "Rules" list, before the picker widget.

### N4 CE vs microthread lanes: what "run to completion + async" looks like
- Purpose: show why a task must not wait. The CE launches an async op and returns to the picker while a microthread moves the data.
- Content: a Gantt chart over about 30 illustrative cycles with lanes `CE`, `UT2`, `UT3`, `UT4`, `UT5` and `memcpy cmd`. In the async version, `start_step` runs briefly on the CE, four bars appear on the UT lanes, the CE is idle or serving memcpy, and then the done tasks appear as short CE bars, each fired by its UT bar ending (arrows). Toggle "blocking op instead": the CE bar stretches over the whole transfer and the memcpy command waits (red), matching pipeline-01 ("The kernel stalls if a blocking instruction … is used").
- Interaction: a single toggle, async ↔ blocking, plus hover on a bar to show its `@fmovs(...)` line from Lab 3.
- Placement: in "Three kinds of task", next to the "Run to completion" rule (if the async primer from pedagogy P1 is added, put it beside that).

### N5 Task-ID space map, WSE-2 vs WSE-3
- Purpose: turn the first three rows of the comparison table into a picture of the ID space.
- Content: two horizontal strips of 31 cells (IDs 0–30).
  - WSE-2: 0–23 shaded blue, "data task = color 0–23 (if routed to RAMP)"; 0–30 hatched amber, "local tasks may use any 0–30"; a note that each ID is bound once.
  - WSE-3: 0–7 blue, "data task = input queue 0–7", with 0–1 marked "memcpy"; 8–30 amber, "local"; 31 grey.
  - A separate small strip, "control task IDs: not colors, no route needed" (topic-05). Check the exact legal range in csl-libs before drawing it; Chapter 7 says memcpy reserves IDs 33–37 and 40.
  - Highlight Lab 1's ID 2 (data) and Lab 3's IDs 10–13 (local).
- Interaction: hover a cell to show "what can be bound here on this chip". An architecture toggle animates the blue band shrinking from 24 to 8.
- Placement: directly above the "WSE-2 versus WSE-3" table.

### N6 Sentinel / control-task sequence diagram
- Purpose: give control tasks (objective 1) a picture; at present they appear only in one table row.
- Content: a static sequence diagram with lanes host → PE A → PE B. The host sends N; data wavelets d1…dN flow on color c, each with a small "data task: sum += v" tick on B. Then one control wavelet labelled `ctrl, task ID S (not a color, no route)` reaches B and activates `send_result`, which sends the sum back. Data from topic-05-sentinels README.
- Interaction: none needed; optionally, step-through numbering.
- Placement: right after the "Three kinds of task" table.

### N7 `@block` / fabric-DSD handover animation
- Purpose: illustrate the back-pressure bullet. While a data task is blocked, wavelets stay in the queue so that a `fabin_dsd` op can drain them.
- Content: an input queue with arriving wavelets, a data task box with a lock icon (blocked), and an async `@fmovs(mem, fabin)` bar draining the queue into a memory array (16 cells filling). On completion, `.unblock = task_id` removes the lock. Source: pipeline-01 README.
- Interaction: a toggle `@block` on/off. When off, the data task fires once per wavelet and competes with the DSD, shown as a conflict warning.
- Placement: after N3, or merged with V7's blocked branch if space is short.
