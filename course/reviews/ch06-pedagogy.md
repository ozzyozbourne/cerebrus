# ch06 · pedagogy review

Summary: The chapter's core idea is right and well chosen: a DSD is a hardware loop, so one builtin processes a whole vector, and fabric DSDs make communication an operand. The DSD visualizer and the stencil example work well. The chapter gets thin after that. Two of its three objectives are only half delivered. It never shows how a fabric DSD is declared, never shows the raw base/extent/stride form or how to change a DSD at run time, and states the async rules without an example. One widget preset is mislabelled, and the figure suggests a fabric DSD names a direction, which builds a wrong mental model. The quiz only tests memory-DSD addressing. Findings: 0 critical, 6 major, 9 minor.

## Findings

### P1 [major] Fabric DSDs are used but never declared (objective 2 not delivered)
Location: "Fabric DSDs: communication is an operand". The code block shows only the `@fadds(out_dsd, in_dsd, v_dsd, ...)` call.
Problem: The learner never sees how `in_dsd` and `out_dsd` are built: `.extent`, `.input_queue`, `.output_queue`, and the WSE-2-only `.fabric_color`. The objective says "Use fabric DSDs", but the learner cannot write one after reading the chapter. The queue/colour binding from Chapter 5 is not connected to the DSD either.
Why it matters: A fabric DSD is the point where the queue, colour, router and datapath meet. Without its declaration the learner cannot see that a fabric DSD names a *queue*, and that the queue is bound to a colour.
Concrete fix: Put the real declarations from `programs/03-row-reduce/pe_program.csl` before the `@fadds` line:
```
const oq: output_queue = @get_output_queue(2);
const iq: input_queue  = @get_input_queue(2);
const out_dsd = @get_dsd(fabout_dsd, if (@is_arch("wse3")) .{ .extent = M, .output_queue = oq }
                                     else .{ .extent = M, .output_queue = oq, .fabric_color = send_color });
const in_dsd  = @get_dsd(fabin_dsd, .{ .extent = M, .input_queue = iq });
// comptime: @initialize_queue(iq, .{ .color = recv_color }); and, on WSE-3, @initialize_queue(oq, .{ .color = send_color });
```
Follow it with: "A fabric DSD has no base address or stride. Its extent counts wavelets, not words. It names a hardware queue, and the queue is bound to a colour (Chapter 5). On WSE-2 the outgoing colour is a field of the fabout DSD. On WSE-3 it is fixed when the queue is initialised."

### P2 [major] The figure implies a fabric DSD knows its direction
Location: Fabric figure labels "fabin: from WEST" and "fabout: to EAST", and the comment "receive the running sum from the WEST ... send the result EAST".
Problem: Nothing in a fabin or fabout DSD names a direction. Direction comes from the colour's route in the router (Chapter 4), and the layout sets that route. The learner will think the DSD picks the link.
Why it matters: This separation is central to how the architecture works internally. The PE program speaks in queues and colours, and the router config decides where those colours go. Learners who miss it will look for direction bugs in the wrong file.
Concrete fix: Change the box labels to "fabin: input queue 2 (recv_color)" and "fabout: output queue 2 (send_color)". Add to the caption: "The DSD names only a queue. That recv_color arrives from the west and send_color leaves to the east is set by the routes in layout.csl (Chapter 4), not by this code."

### P3 [major] Objective 1 promises base/extent/stride, but only `tensor_access` is shown, and run-time DSD updates are missing
Location: Objectives, first bullet, and the paragraph after the SAXPY code. The widget preset "next column via @increment_dsd_offset" is the only mention of updating a DSD.
Problem: The explicit form `.{ .base_address = &A, .extent = M, .stride = N }` never appears, although the widget's controls are labelled base/extent/stride. `@increment_dsd_offset`, `@set_dsd_base_addr` and `@set_dsd_length` are not explained. The learner does not learn that a DSD is a value you can change at run time, and that this is how a 2-D algorithm (GEMV over columns) is built from 1-D DSDs.
Why it matters: Without this, the learner cannot write the most common pattern: an outer loop over columns, with one vector instruction per column.
Concrete fix: Add a subsection "Two spellings, and moving a DSD" after the tensor_access paragraph:
```
// these two are the same descriptor (SDK gemv-02)
var A_dsd = @get_dsd(mem1d_dsd, .{ .tensor_access = |i|{M} -> A[i*N] });
//        = @get_dsd(mem1d_dsd, .{ .base_address = &A, .extent = M, .stride = N });
for (@range(i16, N)) |j| {
  @fmacs(y_dsd, y_dsd, A_dsd, x[j]);              // y += A[:, j] * x[j]
  A_dsd = @increment_dsd_offset(A_dsd, 1, f32);   // slide to column j+1
}
```
Follow it with one sentence: "A DSD is a small run-time value. `@increment_dsd_offset`, `@set_dsd_base_addr` and `@set_dsd_length` edit it, so the scalar loop runs N times while the inner loop over M stays in hardware."

### P4 [major] Widget preset "next column" shows column 3, not the next column
Location: DSD visualizer, option `value="3,6,8"`, label "next column via @increment_dsd_offset: |i|{6} -> A[3 + i*8]".
Problem: Starting from column 0, `@increment_dsd_offset(A_dsd, 1, f32)` gives base 1 (column 1). Base 3 is column 3, which needs three increments or an offset of 3. The label teaches the wrong effect of the builtin.
Why it matters: The learner will conclude that the offset is something other than elements, or that "next" skips columns.
Concrete fix: Change the option to `value="1,6,8"` with the label "next column (after @increment_dsd_offset(A_dsd, 1, f32)): |i|{6} -> A[1 + i*8]". Or keep base 3 and use the label "column 3: offset 3 from column 0".

### P5 [major] Async section states rules without an example or the underlying "why"
Location: "Async operations and completion tasks".
Problem:
(a) There is no code that contrasts a synchronous op (the stencil's `update()` ops) with an async one (the halo `@fmovs` ops).
(b) `.unblock` is introduced as "(lift a block)" with no use case.
(c) The text does not say what "finishes" means for a send. Completion is local to this PE's side of the transfer and says nothing about the receiver.
(d) The stall warning is quoted, but the mechanism is not explained. A blocking fabric op keeps the CE busy while it waits for wavelets that may depend on a command the CE must process.
(e) There is no link to the microthread-sharing rule (Chapter 5) or to the 8-microthread limit (Chapter 3).
Objective 3 ("chain them through tasks") is therefore only asserted.
Why it matters: This is the internal behaviour the learner most needs to model, and it caused the course's real Lab 3 hang.
Concrete fix: Add a short paired example drawn from `programs/04-heat-stencil`:
```
// synchronous: the CE executes this to completion before the next line
@fadds(lap_dsd, left, right);
// asynchronous: queued on a microthread; the CE continues; done_se runs when it finishes
@fmovs(to_e, last_cell, .{ .async = true, .activate = done_se });
```
Then add: "Why fabric ops must be async: a synchronous `@fmovs` from a fabin DSD keeps the CE spinning on an empty queue. If the wavelets it waits for depend on a memcpy command that the CE itself must decode, nothing can make progress (SDK pipeline-01). `.unblock` is for the opposite case: block a data task so that it does not fire again, start an async send from its buffer, and let the send's completion unblock it (SDK gemv-09, topic-09). Each async op occupies one microthread, and two concurrent ops must not share one (Chapter 5, 'A real hang')." Finally, point to Chapter 5's state-machine figure as the worked example of chaining.

### P6 [major] The fabric-DSD/data-task conflict is missing
Location: Fabric DSD section.
Problem: The SDK warns that if a data task is bound to the queue or colour a fabin DSD reads from, the task will consume the wavelets before the DSD can. Chapter 5 hints at this ("A blocked data task leaves wavelets waiting ... which is how a fabric DSD can consume them instead"), but Chapter 6, where the learner actually writes fabin DSDs, never says so.
Why it matters: The two ways to receive wavelets, per-wavelet tasks and whole-vector DSDs, compete for the same queue. A learner who mixes them gets silent data loss into an empty task, or a hang.
Concrete fix: Add a callout: "**One consumer per queue.** If a data task is bound to the queue that a fabin DSD reads, each arriving wavelet activates the task, and the task consumes the wavelet first. Either bind no data task to that queue, as programs 03 and 04 do, or `@block` it while the DSD op runs (SDK pipeline-01)."

### P7 [minor] FIFO paragraph: misleading "14" quote, and no example
Location: "FIFOs extend the tiny hardware queues".
Problem: "stalls when size exceeds 14" comes from pipeline-01, where it refers to the memcpy I/O queues in a deliberately invalid H2D-then-D2H example. It is not a general hardware queue depth. The learner cannot interpret the number. The paragraph also gives no code and no reason why a FIFO helps.
Why it matters: FIFOs are needed for the WSE-3 two-input workaround described in the callout above them, yet that callout refers to FIFOs before they are explained.
Concrete fix: Replace the paragraph with: "Hardware queues hold only a few wavelets. In SDK pipeline-01, an H2D stream of more than 14 wavelets with no consumer stalls. `@allocate_fifo(buf)` turns an SRAM array into a software queue. One async op fills it while another drains it, so a burst from the fabric does not back-pressure the sender. This uses two microthreads (SDK topic-09):
```
var fifo_buffer = @zeros([1024]f32);
const fifo = @allocate_fifo(fifo_buffer);
@fadds(fifo, in_dsd, ten_dsd, .{ .async = true });   // fabric -> FIFO (+10)
@fnegs(out_dsd, fifo, .{ .async = true });           // FIFO -> fabric (negated)
```
" Move the WSE-3 callout below this subsection, or add "(FIFOs: see below)" to it.

### P8 [minor] The "why" of DSD speed is not quantified
Location: The paragraph after the SAXPY code ("no per-element instruction fetch or loop counter").
Problem: The learner is told the hardware loop is cheaper but gets no sense of how much cheaper. There is no comparison with the scalar instruction sequence, and no link to the SIMD width from Chapter 3.
Concrete fix: Add: "A scalar loop body would be roughly load x, load y, multiply-add, store y, increment, compare, branch: about seven instructions per element, each fetched and decoded. With a DSD, one instruction is decoded and the datapath streams operands at SIMD width (Chapter 3: 8-way for FP16 on WSE-3), with the interleaved SRAM banks supplying several words per cycle. The loop overhead disappears, not just the cache misses." Tag the instruction count `derived`.

### P9 [minor] "Any operand can be ... a scalar" overgeneralises
Location: The paragraph after the builtins table.
Problem: A destination cannot be a scalar, and in `@fmacs` the scalar sits in a fixed position. The callout further down then contradicts "any operand can be a fabric DSD" for WSE-3.
Concrete fix: Replace with: "Each operand slot accepts a memory DSD, a fabric DSD or a FIFO. Some source slots, such as the multiplier in `@fmuls` and `@fmacs`, also accept a scalar. On WSE-3, at most one source may be a fabric DSD (see below)."

### P10 [minor] Figure label "v_dsd (my 48 KB)"
Location: Fabric figure, green box.
Problem: It implies `v_dsd` spans the PE's whole memory. It covers M f32 values.
Concrete fix: Use the label "v_dsd: M words of my SRAM".

### P11 [minor] Stencil index notation shifts between code and comments
Location: The Lab 3 code block.
Problem: The DSDs index `u[i]`, `u[i+1]` and `u[i+2]`, but the comments say `u[i-1] + u[i+1]` and `-2 u[i]`. In the comments, "i" means the cell, not the DSD's induction variable. The page also never explains why the in-place update `@fmacs(mid, mid, lap_dsd, alpha)` is safe.
Concrete fix: Add after the block: "In the comments, i is the cell index, so cell i lives at `u[i+1]`. The update can be in place because `lap` is completed for every cell by the first two instructions, before any `u` is overwritten. A single fused pass over `u` would read already-updated left neighbours."

### P12 [minor] Undefined forward references
Location: SAXPY code (`sys_mod.unblock_cmd_stream()`), "memcpy runtime" in the async section, "SDK topic-10" in the table, and "Lab 1/2/3" throughout.
Problem: The command stream is first explained in Chapter 7, the labs are Chapters 10–12, and "topic-10" is an SDK tutorial name the learner does not know.
Concrete fix: After the SAXPY code, add: "(`unblock_cmd_stream()` tells the host that this call is done; Chapter 7.)" On first use, write "Lab 1 (Chapter 10)". Change "SDK topic-10" to "SDK tutorial topic-10-map-builtin".

### P13 [minor] CSL syntax is used before Chapter 9 introduces it
Location: First code block.
Problem: `.{ .field = ... }`, `|i|{N} -> expr`, `@builtin` and `comptime` all appear without a gloss. The `tensor_access` sentence explains only the last of these.
Concrete fix: Add a one-line aside: "Reading CSL: `@name` is a builtin, `.{ .a = 1 }` is an anonymous struct literal, and `|i|{N} -> x[i]` reads 'for i in 0..N, element x[i]'. Chapter 9 covers the language."

### P14 [minor] The naming-pattern tag is a reviewer note, not learner content
Location: "Derived from SDK sources; verify against the builtin reference".
Concrete fix: Verify the pattern against the SIF builtin docs and change the tag to `sdk`, or reword it to "Derived from builtins used in the SDK examples".

### P15 [minor] The quiz only tests memory-DSD addressing
Location: "Check yourself".
Problem: All three questions are about addressing or a single speed claim. Nothing tests fabric DSD semantics, async completion, FIFOs or the WSE-3 limit. Q1's 2-D answer `A[i, i]` also assumes A is declared as `[8, 8]f32`, which the chapter never shows.
Concrete fix: Add "(if A is declared `[8, 8]f32`)" to Q1's 2-D answer, and add these questions:
- "Where in `in_dsd` is the direction 'from the west' encoded?" Answer: "Nowhere. The DSD names an input queue bound to a colour, and the layout's route for that colour makes it arrive from the west."
- "On WSE-3 you want `out = in_west + in_east`, both from the fabric. Why does `@fadds(out, in_w, in_e)` not work, and what do you write instead?" Answer: "WSE-3 allows one fabric input per op. Drain one stream into a FIFO with an async `@fmovs`, then `@fadds(out, fifo, in_e, .{.async = true})`."
- "Your async send activates `done`, and `done` calls `unblock_cmd_stream()`. Does that guarantee the neighbour has received the data?" Answer: "No. Completion is local to the sender's operation. The receiver's own op completion is what tells the receiver."
- "After `A_dsd = @increment_dsd_offset(A_dsd, 1, f32)` on `|i|{6} -> A[i*8]`, which words does it visit?" Answer: "1, 9, 17, 25, 33, 41."
