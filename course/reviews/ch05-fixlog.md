# ch05 · fix log

File edited: `course/05-tasks.html` only. Verified with Playwright at 1100px and 390px, light and dark. There were no page or console errors and no horizontal page overflow (scrollWidth equals innerWidth at both widths, after adding `overflow-wrap:anywhere` to inline code). Every widget control was exercised and the key figures were screenshotted and inspected. Scratch files under `/home/user/cerebras-sdk/tmp/fix-ch05/` were deleted.

## Experiments run (simulator / cslc 2.10.1, copies of programs/04-heat-stencil, P=8, n=16, 50 steps)
- Shipped Lab 3 (iq 4/5): SUCCESS on WSE-3 and WSE-2.
- Input queues 2/3 (the first Lab 3): fails on **both** chips. sim.log ends with `FATAL ... trying to term ut_instr[3], but it's not ours` at cycle 2,123 (WSE-3) and 2,125 (WSE-2), and the host hangs. This agrees with the coordinator's ch12 note. "Stalled forever at cycle 1,894" was removed.
- iq 2/3 with `.ut_id` 4/5 on the receives (WSE-3): SUCCESS.
- One shared completion task for all four ops: hangs on both chips. The host reports "the received length (0 bytes) is not expected (576 bytes), could be a kernel stall".
- cslc probes: on WSE-3, `@get_data_task_id(color)` gives "expected 'input_queue' expression, got: 'color'". Local IDs: WSE-3 [8,31), WSE-2 [0,31). Control-task IDs: [0,64) on both. Binding task 29 is refused because memcpy registers a teardown handler.

## Accuracy
- A1 fixed: the single-bit rule now quotes 25-pt-stencil/task.csl, with an sdk tag, in "What the hardware stores".
- A2 fixed: the widget hint says the timings are illustrative and states the model's assumptions. The text cites 25-pt-stencil and the measured shared-task hang.
- A3 fixed: changed to "programs 02–05 all use it".
- A4 fixed: the filename is now "excerpt, simplified" and the elided body is shown with `/* … */`.
- A5 fixed: the callout is rewritten. It now says microthread = queue only by default on WSE-3 (always on WSE-2), gives the measured FATAL cycles on both chips, notes that the `.ut_id` fix was measured, and tags the SDK quote.
- A6 fixed: "must not wait", with the pipeline-01 deadlock mechanism.
- A7 fixed: "more than one", and the source note now includes sdklayout-03.
- A8 fixed: "one 32-bit arg, or two 16-bit halves".

## Pedagogy
- P1 fixed: a "Preview: async operations (full story in Chapter 6)" box defines async, microthread, DSD and fabric DSD.
- P2 fixed: new "Tasks are entry points; functions do the work" section. The state-machine figure now draws fn boxes dashed and tasks solid, with a legend. The widget draws update() inside the last done-task bar.
- P3 fixed: rule 2 is rewritten (buffered vs collapsed, with the measured program-02 count of 100). New widget N3, plus a quiz question.
- P4 fixed: control-flow sketch with `@bind_local_task`, `.activate`, `@activate` in comptime and `@block`, plus a `.unblock` sentence. The join section adds a second pattern.
- P5 fixed: "Control tasks and sentinels" section. It gives the ID range 0–63 (Measured), the memcpy IDs 33–37/40, the topic-05 ID 43, no route needed, the lower-16-bit payload, a code snippet, and the switch-position note.
- P6 fixed: the event-loop / ISR analogy with the reason behind it. The "When several tasks are ready" section says what is and is not guaranteed.
- P7 fixed: the table cell now says "input queue (ID 0–7) bound to any routable color". New budget table, and "What this means in practice" with both traps (Trap 1's symptom is a measured compile error). Microthread is defined in the P1 box.
- P8 fixed: the budget table and ID map show the memcpy-reserved IDs. A safe range of 8–20 is given, and the text notes that Chapter 7's 9–23 is looser.
- P9 fixed: the rule is renamed "Blocking". It says blocking is required for fabric-DSD reads and separates block from back-pressure.
- P10 fixed: Q2 and Q3 answers revised. Added questions on collapse, buffered wavelets, microthread sharing, tasks vs functions, the ID budget and the join.
- P11 fixed: a sentence at the top of "The path from wire to code" reconciles Chapter 4, and figure 1 shows both chips.
- P12 fixed: "Why the compiler cannot help" explains the run-time nature and how to diagnose it (sim.log FATAL, instruction trace). WSE-2 behaviour was measured.
- P13 fixed: (a) the task table is marked schematic and Derived; (b) RAMP labels the router→queue arrow; (c) payload cell; (d) the widget's assumptions are stated.
- P14 fixed: glosses added for memcpy, unblock_cmd_stream(), comptime and CE/picker. The tutorial folder names are given.

## Visuals
- V1 partially fixed: the shared phone rule (SVGs keep a 620px minimum width and scroll inside their box) applies to every new and old SVG. No separate portrait layouts were made.
- V2 fixed: each table cell has its own x, there is a status column, and a legend line ties IDs 2/10/11 to the programs.
- V3 fixed: update() is a green inset inside the last done-task bar, and the log reads "calls update() (same task)".
- V4 fixed: connectors run from each completion to the run it caused, a lost activation shows as a red ring with "×", there is an activation-bit trace lane, the timing sliders, presets and random times are controllable, and a 500-step tally compares both designs.
- V5 fixed: axis title "cycle (illustrative)", op labels "send E" etc., task IDs in the lane labels, and `aria-live` on all readouts.
- V6 fixed: "launch 2–4 async ops (4 inside, 2 at the ends)", a self-loop for `pending > 0`, "pending == 0", an arrowhead to a "host unblocked" end state, dashed fn boxes with a legend, and the P = 1 case in the caption.
- V7 fixed: WSE-2 and WSE-3 task-ID tags, and a dashed red "blocked" branch back to the queue.

## Depth
- D1 fixed: "What the hardware stores" (activated and blocked bits). New ID-space map (SVG, both chips, IDs 0–43, hover tooltips) shows the 5-bit reach (0–30), control-only IDs above 31, memcpy IDs, teardown 29 and NOP 31.
- D2 fixed: the "Block + activate = join" section has the 4-step sequence, the memcpy SYS_UBLK_C22 and spmv LOCK quotes, and a new interactive join widget.
- D3 fixed: "When several tasks are ready" covers the task-priority register (0x7e08/09, HIGH/LOW, wavelet tasks set via color or queue), the 0x73FD bit-row figure (noting that the source line is commented out), the main-thread priority table, `.priority` on async ops, and what is undocumented.
- D4 fixed: the run-to-completion rule is rewritten with the pipeline-01 mechanism. The two-lane CE/microthread diagram (N4) was not drawn (see Left for later).
- D5 fixed: budget table (6 data tasks, 18 or 15 local, 6 output queues), the 25-pt-stencil worked squeeze (18 local tasks), the 24/SYS_EN_MAIN caveat tagged Derived, and a quiz question.
- D6 fixed: a fourth row in the activation table (teardown task 29), and a "Reusing a queue on WSE-3" section with the 5-step flush sequence, the ordering hazard and the measured "cannot bind 29" error. Told as a numbered list, not a diagram.
- D7 fixed: covered by the sentinel section (encode_single_payload, payload in the lower 16 bits, switch timing, IDs above 31).
- D8 fixed: the "Self-start and self-send" bullet, plus the queue-size number (~14, pipeline-01) in the blocking rule and the quiz. INPUT_QUEUE_STATUS polling is not mentioned.
- D9 fixed: the 25-pt-stencil "input_queue = 4 + queueId" quote, and WSE-2 behaviour measured. The `--disable-auto-microthread-id` flag is not mentioned.
- D10 fixed: E1 and E2 were run (plus the `.ut_id` variant and cslc probes), and the results are tagged Measured. E3 (per-wavelet task cost) was not run.

## New visuals added
1. **Buffered vs collapsed widget** (N3): step/play/reset with an N slider; the queue overflows into the router as back-pressure.
2. **Join widget** (D2): activated and blocked bit cells with event A / event B buttons.
3. **Task picker rewrite** (N2 + V3/V4/V5): timing sliders, activation-bit lanes, lost-activation markers, update() inside the task, presets, a random button and a 500-step tally.
4. **Priority-mask bit row** (D3): 0x73FD decoded.
5. **Task-ID space map** (N5 + D1): WSE-2 and WSE-3 strips with tooltips and reach brackets.
6. **Microthread collision explorer** (N1): chip, presets, per-op queue and `.ut_id` controls, UT0–7 lanes. Measured verdicts are shown for the three configurations that were run; all others are labelled Predicted.
Also redrawn: figure 1 (V2/V7/P13) and the state machine (V6/P2).

## Left for later
- N4 (CE vs microthread Gantt, async vs blocking), N6 (sentinel sequence diagram), N7 (@block / fabric-DSD handover animation).
- Portrait layouts for phones (V1). The shared scroll rule covers this for now.
- E3, the per-wavelet task cost measurement.
- Cross-chapter items for other fixers: Chapter 4's "color picks the task" should be qualified for WSE-3. Chapter 7's "use 9–23" should be reconciled with topic-09 marking 21–23 reserved on WSE-3 and with the 25-pt stencil binding ID 24. Chapter 12 should be updated with the measured FATAL at cycle ~2,123/2,125 on both chips.
- The toy picker model assumes the activated bit clears when a task starts and that ties go to the lowest ID first. Both assumptions are stated on the page as undocumented.
