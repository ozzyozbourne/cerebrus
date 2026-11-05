# R4 fix log: ch05, 05-tasks.html

Sources: r4-ch05.md, CROSS_CHAPTER_NOTES 30–38, plus the cross-page items in r4-ch13.md (stale ~88) and r4-appB.md (callouts do not link App B). I ran no experiments. Every new number comes from SDK files or from measurements the course already has.

## Errors
- **E1 Fixed.** The Blocking rule now gives the published depths: input queues 0–1 / 2–3 / 4–7 hold 6 / 4 / 2 wavelets. The source is memcpy/wse3 and wse2/memcpy.csl [SDK], linked to Ch 7's table. Queue 2 holds 4. pipeline-01's "14" is now described as I/O-path buffering. In the widget, CAP is 4 and the queue is labelled "input queue 2 (depth 4)". The hint and quiz Q1 are updated, and the text no longer says "not published" anywhere (CCN 35).
- **E2 Fixed.** The rule is now conditional: block the data task only if one is bound to the color/queue that a fabric DSD reads. Added "Lab 3 binds no data task to its receive queues 4 and 5, has no @block, and passes on both chips". The comment in the sketch is reworded.
- **E3 Fixed.** Changed ~88 to ≈90 [Measured, Ch 13]. Added Ch 13's split (≈14.6 per transfer + ≈13 bookkeeping) with a link to 13-lab-stencil.html#fixed-cost. This also covers the r4-ch13 cross-page item (CCN 37).
- **E4 Fixed.** The excerpt keeps `if (@is_arch("wse3")) @initialize_queue(...)`.
- **E5 Fixed.** `fillQueues` and the memcpy message use `i < (arch==="wse3" ? 2 : 1)`. On WSE-2, queue 1 is no longer marked memcpy. Checked in Playwright.

## Explanation problems
- **X1 Fixed.** The opener now reads "Chapter 4 previewed it … here it is in detail", with a link to 04-fabric.html#mesh.
- **X2 Fixed.** The snippet now follows topic-05 sentinel.csl. It defines `tx_ctrl_dsd` with `.control = true` and uses `ctrl.encode_control_task_payload(done_id)`, and the receiver is `send_result()` with no argument, as in the SDK. `SWITCH_ADV` now appears only in the switch sentence.
- **X3 Fixed.** The page uses one safe count, 15: 8–20 (Ch 7's rule) plus 25 and 26. The 25-pt squeeze compares against 15 and notes that IDs 2 and 3 would have to move to ≥ 8 on WSE-3. The 18 remains only as the "all non-memcpy" count in the table and Q8, which already explained both counts.
- **X4 Fixed.** The intro now says tasks are never preempted, and that memcpy's "context switch" swaps host-I/O kernels.
- **X5 Fixed.** Added an event → activated/blocked mapping table at the top of #rules. The "task start clears activated" row is tagged as assumed.
- **X6 Fixed.** Changed to "Readiness is not the only input to the picker".

## Connecting gaps
- **G1 Fixed.** Added a "Lab 3 in one box" callout at the top of #picker. It covers the rod over P PEs, n cells plus 2 ghosts, the send/receive pattern and the update formula, with a small two-PE ghost-cell SVG. Linked to 13-lab-stencil.html#problem.
- **G2 Fixed.** Added join step 5: L re-blocks itself to re-arm the join. Quoted programs/06-summa's `@block(COMPUTE); // re-arm the join…` and linked 14-lab-gemm.html#join.
- **G3 Fixed.** Added a "Why four tasks are enough" paragraph. It states the invariant (the next step's ops start only after pending == 0) and the general rule [Derived].
- **G4 Fixed.** Added a "Why the sentinel arrives last" paragraph [Derived]: same output queue, color/route and input queue, all FIFO and lossless. Added a short sequence/FIFO SVG (closes the old N6).
- **G5 Fixed.** Added the gemv-09 self-blocking data-task snippet (verbatim body), with its explanation and a mention of topic-14.
- **G6 Fixed.** Added one sentence: control IDs 0–63 come from the 6-bit entrypoint field, bits 16–21 (`ENTRYPOINT_BIT_POSN = 16`, opcode at 22), linked to 04-fabric.html#control-wavelets. It contrasts this with the 5-bit ACT/UB field and links to the ID map.
- **G7 Fixed.** Added a two-lane schematic timeline (CE plus UT2–UT5) for one Lab 3 step. It names the shared resource (datapath, memory and fabric ports, linked to Ch 3 #microthreads) and cites Ch 13's ≈14.6/transfer and ≈90/step [Measured, Ch 13]. The bars are tagged schematic. This closes the old N4.
- **G8 Fixed.** Every Chapter/Lab mention that points at an idea is now a link. Links added: Ch 3, 4 (mesh, back-pressure, control-wavelets, switches, teardown), 6 #async, 7 (#reserves, #command-stream, #modes), 10 (#hardware-parts, #hangs), 11 #wavelet-tasks, 13 (#problem, #fixed-cost), 14 #join, App B #rosetta. Glossary links added: task, input-queue, data/local/control task, teardown, microthread, DSD, fabric-dsd, sentinel, control-wavelet, block-unblock, back-pressure, run-to-completion, comptime, join, task-picker, ut-id, memcpy, queue-flush. All 61 hrefs resolve to an existing file and anchor (Playwright check).

## Cross-page items about this page
- **r4-ch13 (stale ~88) Fixed:** see E3.
- **r4-appB (Ch 5 callouts do not link App B) Fixed:** the CUDA callout now links appendix-b-cuda-to-csl.html#rosetta.
- **r4-appA X2 / r4-ch15 / r4-ch17:** no change needed here. Those items concern other pages. Ch 5's own wording on IDs 24, 0–63 and 8–20 is consistent with them.

## Verification
Playwright, 1100 px. I drove the buffered widget (N = 3 and 8), the join, the explorer (WSE-2 q0/q1, WSE-3 presets), the picker presets and the 500-run tally. There were zero console or page errors. At 390 px, scrollWidth is 390. I checked screenshots of the new SVGs in light and dark mode.

## For other pages
- Ch 4 (04-fabric.html #filters, r4-ch04 E4) still says Chapter 5 uses the index field for sparse data. Ch 5 has no such material.
- Ch 12 G5: if Ch 12 maps its measured 16–18 buffer capacity, it should use the per-queue depths 6/4/2 (queue 2 = 4) rather than "~14", which is I/O-path buffering (CCN 35).
