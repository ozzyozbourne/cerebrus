# ch05 · depth review

Summary: The chapter states the task model correctly, but it stays at the level of rules. It never shows the hardware state behind them, even though the SDK exposes most of it. That state is an activation bit and a block bit per task ID, a task-ID space with hard 5-bit limits, a task-priority bit-vector register, a main-thread priority set relative to microthread priorities, a teardown task (29) driven by per-color teardown-pending bits, and queue status registers. The research notes list priority and arbitration as "gaps". In fact the CSL library inside the SIF (`tile_config/task_priority*.csl`, `main_thread_priority.csl`, `teardown.csl`, `target/*.csl`) and two benchmarks (`25-pt-stencil`, `spmv-hypersparse`) answer much of it. The largest missing ideas are these: activated ∧ unblocked works as a hardware *join*; the ID budget is a real design constraint, worked through on a real benchmark; priorities exist; and "run to completion" sits alongside 8 microthreads that keep running. Several items overlap the pedagogy (P3, P4, P5) and visuals (N5, N6) reviews. Below I give the extra mechanism and numbers those reviews lack, so one fix can satisfy both.

## Gaps and additions (prioritised)

### D1 [critical] The per-task hardware state and the task-ID space are never shown
**What is missing.** The chapter says "activation is a flag" and that the picker chooses "activated and unblocked" tasks. It never says this is literally one activation bit and one block bit per task ID, and it never shows the ID space those bits are indexed by. It also omits the hard limits that follow:
- `.activate`/`.unblock` on an async DSD op can only name IDs 0–30, because the fabin/fabout DSD has "only 5-bit 'ACT/UB color' field".
- `@activate(id)` "can only activate a color less than 31".
- ID 31 is NOP.
- "control wavelet indeed can trigger entrypoints bigger than 31", which is why memcpy's control tasks sit at 33–37 and 40, and topic-05's sentinel at 43.
- Task 29 is the teardown task.

The 25-pt-stencil comment that proves the one-bit model is not quoted. Accuracy review A1 flags the missing citation. This item is about adding the mechanism.

**Why it matters.** This is the machine-level model the whole chapter rests on. Without it, the reader cannot see three things: why the four-completion-task design is required, why sentinel IDs are above 31, and why there are only so many tasks.

**Source.**
- `benchmarks/25-pt-stencil/task.csl` lines 495–502: "the hardware does not queue activations (instead, the hardware uses a single bit to track task activations). Thus ... activating a task multiple times does not guarantee that the said will execute multiple times."
- SIF `csl-libs/memcpy/sys_params.csl` header, WARNING 1–3 and the ID list (24 SYS_EN_MAIN, 27 SYS_UBLK_C22, 28 SYS_EXIT, 29 teardown, 30 SYS_SEND_CTRL, 31 NOP, 33–37 and 40 control).
- `tile_config/teardown.csl` `get_task_id()` returns `@get_local_task_id(29)`.
- topic-05 README (data 0–23 / 0–7, local 0–30 / 8–30).
- Task-ID map comments in `tutorials/topic-09-fifos/layout.csl` lines 1–27, with separate WSE-2 and WSE-3 tables.

**Proposed addition.**
1. A paragraph titled "What the hardware actually stores". For each task ID the CE keeps an *activated* bit and a *blocked* bit. The picker considers only IDs with activated = 1 and blocked = 0. Running a task clears its activated bit. Setting a bit that is already set does nothing, which is the single-bit sentence quoted from 25-pt-stencil, tagged `sdk`.
2. A table, "The task-ID space", with columns ID | WSE-2 meaning | WSE-3 meaning | Reachable by. Rows:
   - 0–7: WSE-2 color/data task or local; WSE-3 input-queue data tasks (0, 1 memcpy).
   - 8–20: WSE-2 color/data or local; WSE-3 local.
   - 21–23: memcpy colors on WSE-2 (MEMCPYD2H 21, RXCOMMAND 22, MEMCPYH2D 23). The WSE-3 map in topic-09 also marks them "reserved (memcpy)".
   - 24, 27, 28, 30: memcpy local tasks.
   - 29: teardown.
   - 31: NOP.
   - 32+: control-wavelet entrypoints only (memcpy 33–37, 40; topic-05 sentinel 43).

   The "Reachable by" column records the rule: `@activate`/`.activate`/`.unblock` reach only IDs < 31 (5-bit field); control wavelets reach any ID. Tag `sdk`.
3. Optional diagram: a 0–43 strip of cells coloured by kind, with a bracket showing "5-bit field reaches here" ending at 30. Visuals N5 proposes a similar map; merge them.

### D2 [major] "Activated ∧ unblocked" is a two-input join, and the chapter never uses it that way
**What is missing.** The chapter presents `@block` only as back-pressure. In real SDK code, block plus activate is the standard way to make a task run only after two independent events. The pattern: the operation blocks task L at its start; a different event activates L; the operation's completion unblocks L. L runs only when both have happened, in either order. Three SDK uses:
- gemv-09 `memcpy_recv_x`: the data task blocks itself, then launches `@fmovs(..., .{.async=true, .unblock=memcpy_recv_x_task_id})`. The next wavelet is already pending as an activation, but it cannot fire until the buffer is free.
- memcpy's `SYS_UBLK_C22`: "H2D blocks SYS_UBLK_C22 in the beginning, H2D unblocks SYS_UBLK_C22 when operation is done, teardown handler of H2D activates SYS_UBLK_C22".
- spmv-hypersparse `allreduce2R1E/pe.csl` LOCK: "row_reduce blocks LOCK / T29 activates LOCK / row_reduce unblocks LOCK when it finishes / LOCK goes to next state", repeated for col_reduce and bcast. The comment says it directly: "LOCK runs only if teardown is received and the operation is done".

**Why it matters.** This is the deepest "how" in the execution model. It explains why `.unblock` exists alongside `.activate`. It also gives the learner a second synchronisation tool besides counting, as Lab 3's `pending` does.

**Source.** `tutorials/gemv-09-streaming/pe_program.csl` (quoted in csl_programming.md §3); SIF `memcpy/sys_params.csl` header lines 13–17; `benchmarks/spmv-hypersparse/src/allreduce2R1E/pe.csl` lines 55–92.

**Proposed addition.**
1. A paragraph titled "Block + activate = join", with the three-row truth table (activated, blocked) → runs?:
   - (1, 0) → yes
   - (1, 1) → waits
   - (0, 0) or (0, 1) → no
2. The memcpy SYS_UBLK_C22 sequence as a 4-step numbered list.
3. Optional widget: two buttons, "event A: activate L" and "event B: unblock L". Press them in either order. The L cell lights up and "runs" only after both. A third button, "press A twice", shows that a second activation adds nothing. It can reuse the existing widget's SVG helpers.

### D3 [major] Task priority and main-thread priority exist and are undocumented in the course
**What is missing.** The chapter implies the picker treats all ready tasks equally. The CSL library has a task-priority register and a main-thread priority:
- `tile_config.task_priority.set_task_priority(id)` / `clear_task_priority(id)` / `update_task_priority(id, level)`, with `level = enum { LOW = 0, HIGH = 1 }`. The function reads and writes two 16-bit config registers at `TASK_PRIORITY = 0x7e08` (lo) and `0x7e09` (hi). Together they form a 32-bit vector with one bit per task ID, so only IDs 0–31 can be prioritised (derived). "Updates ... made at runtime may take a few clock cycles to take effect." It can be called at comptime or at runtime.
- Accepted ID types: `data_task_id` or `local_task_id`. For wavelet-activated tasks, including control tasks, the priority is set "using the color on wse2, or the input_queue on wse3, that carries the wavelets" (`task_priority/target/wse2.csl`, `wse3.csl`).
- `tile_config.main_thread_priority.update_main_thread_priority(level)` writes 2 bits at offset 5 of `MISC_CFG` (0x7e1f). The levels are MEDIUM_LOW (between low- and medium-priority microthreads), MEDIUM (same as medium), MEDIUM_HIGH (between medium and high) and HIGH (same as high-priority microthreads). So task code and async microthreads compete for the CE under a priority scheme.
- Async DSD ops take `.priority = .{ .high = true }` or `.{ .medium = true }` (spmv-hypersparse `hypersparse_spmv/pe.csl` lines 688, 709, 985–1070).
- A worked mask in a comment, spmv-hypersparse `pe.csl` lines 146–148: `task_pri_cfg = 0x7E09*2; COMP_LO_PRI = 0x73FD; // all comp tasks at 17, 26, 27 at task_pri=0, else at 1`. Decoding: 0x73FD = 0111 0011 1111 1101b on the hi register (IDs 16–31). Bits 1, 10, 11 and 15 are 0, which gives IDs 17, 26, 27 (and 31) LOW and everything else HIGH. This matches the comment.

**Why it matters.** The learner will ask what happens when several tasks are ready at once. The SDK gives a partial answer (two priority classes, plus main thread versus microthread levels), and the course currently says nothing. Arbitration *within* a priority class is still undocumented, and the chapter should say so honestly (research notes §5 "Gaps").

**Source.** SIF `csl-libs/tile_config/task_priority.csl`, `task_priority/target/{wse2,wse3}.csl`, `main_thread_priority.csl`, `target/common.csl` (`main_thread_priority_level`, offset 5), `target/{wse2,wse3}.csl` (`TASK_PRIORITY = 0x7e08`, `MISC_CFG = 0x7e1f`); `benchmarks/spmv-hypersparse/src/hypersparse_spmv/pe.csl`.

**Proposed addition.**
1. A subsection, "When several tasks are ready", of about 120 words covering the points above, tagged `sdk`. Include the 0x73FD decode as a small bit-row figure: 16 cells labelled 16–31, with cells 17, 26, 27 and 31 shaded "LOW".
2. Name what is unknown: order among equal-priority ready tasks, and the cycle cost of a task switch. Tag the statement `derived`.
3. A 4-row table of main-thread levels against microthread levels.

### D4 [major] What "run to completion" means while microthreads keep running, and how a task *can* wait and deadlock
**What is missing.** The chapter says "A task cannot wait". In fact a task can issue a *synchronous* DSD op on a fabric DSD, and the CE then sits in that instruction. pipeline-01 documents the resulting deadlock with a mechanism: with a blocking `@add16(outDsd, inDsd, 1)` "the instruction trace shows @add16 repeatedly querying data from input queue 1, which is still empty. The router receives the H2D command much later ... The CE has no resource to run the H2D command ..., so it stalls." The chapter also never pictures the CE as one main thread, which runs the current task, plus up to 8 microthreads, which run async ops, sharing the datapath under the priorities in D3. A secondary source says the WSE-3 scheduler switches among the 8 microthreads every cycle based on operand availability (analyst tag).

**Why it matters.** It replaces a slogan with a mechanism. It explains *why* async is mandatory for fabric ops: the main thread must stay free to run the memcpy control tasks that feed the data. Accuracy review A6 flags the overclaim; this item supplies the replacement content.

**Source.** `tutorials/pipeline-01-basic/README.rst` (last two paragraphs); wse_hardware.md §3 (microthreads, hyper-accel claim); SIF `main_thread_priority.csl`.

**Proposed addition.**
1. Rewrite the rule as: "A task should not wait. A synchronous fabric op *does* wait, inside the task, and if the data it waits for needs another task to run first, which is memcpy's H2D command in pipeline-01, the PE deadlocks."
2. A two-lane diagram, "main thread" and "microthreads 0–7". The main thread lane shows task A → picker → task B. The microthread lane shows an async op bar spanning across both tasks, with its completion arrow going to the activated bit of task C. Visuals N4 proposes the same; merge them.

### D5 [major] Task-ID budget: a worked example, and WSE-2's shared color/task namespace
**What is missing.** The chapter never says that on WSE-2 a data task ID *is* a color ID. Colors and local tasks therefore share one 0–30 namespace, and every color a PE receives on uses up a possible local-task ID. The 25-pt-stencil (WSE-2 only, ships just `commands_wse2.sh`) shows the squeeze:
- It binds **18 local tasks**: COMP 2, send 3, 4×DataFin 8–11, 4×CtrlFin 12–15, 4×CtrlFin2 16–19, and 4×Fin on 20, 24, 25, 26.
- It skips 4–7, because those are its channel colors 4–7.
- It skips 21–23, with the comment "WARNING: ID 21/22/23: reserved (memcpy)".

On WSE-3 the user local range is 8–30, which is 23 IDs. Minus 24, 27, 28, 30 (memcpy) and 29 (teardown), that leaves **18** (8–23, 25, 26). If 21–23 are also reserved, as the topic-09 WSE-3 map marks them, it leaves **15**. User data tasks: 8 input queues minus memcpy's queues 0 and 1 = **6** (queues 2–7).

**Why it matters.** It turns the WSE-2/WSE-3 table into a design constraint the learner can compute. It also explains why the 25-pt-stencil benchmark is WSE-2-only: its 18 local tasks would use the whole WSE-3 budget or overflow it. It shows too why the stencil's per-direction "Fin" tasks cannot be merged (D1).

**Caveat.** sys_params lists 24 as SYS_EN_MAIN ("first task after context switch"), but the 25-pt-stencil binds westFin to 24. So 24 is probably reserved only in some memcpy modes. Say "usually reserved" and tag it `derived`.

**Source.** `benchmarks/25-pt-stencil/layout.csl` lines 25–57; SIF `memcpy/sys_params.csl` lines 54–95 (input_queue_id 0, input_queue_cmd_id 1); `tutorials/topic-09-fifos/layout.csl` task maps.

**Proposed addition.** A "Budget check" table with columns resource | WSE-2 | WSE-3 | used by memcpy | left for you, covering data-task IDs, local-task IDs, input queues, output queues and microthreads. Follow it with one worked sentence: "25-pt-stencil uses 18 local tasks plus 4 receive colors; on WSE-3 that is ≥ 100 % of the local budget." Add a Check-yourself question: "How many independent completion tasks can a WSE-3 PE have alongside memcpy?" Answer: 18 at most (15 if you avoid 21–23).

### D6 [major] Teardown task 29 and the queue-flush mechanism are just a table cell
**What is missing.** The WSE table says "reuse needs @queue_flush", but the mechanism is never explained. The steps:
- The microthread's completion only means the data has been *pushed into* the output queue: "the queue may not be empty yet".
- `@queue_flush(oq)` arms an event. When `oq` drains, "WSE-3 will trigger the special teardown task 29, the same way a teardown wavelet does".
- Task 29 calls the handler registered with `@set_empty_queue_handler(foo, oq)`. That handler re-encodes the queue's color (`output_queue_config.encode_output_queue`), activates the next step, and must call `queue_flush.exit(oq)`, or task 29 will keep calling it.
- The hardware side: `TEARDOWN_PENDING` holds "1 bit per routable color indicating the ones that are currently in teardown state" (`teardown.get_pending()`, `is_pending()`). A per-color "teardown in progress" bit sits in COLOR_CONFIG at bit 14 on WSE-2 and bit 15 on WSE-3; `teardown.exit(c)` clears it.
- The ordering hazard: issuing `@queue_flush` before `@mov32` can fire task 29 immediately.

**Why it matters.** This is the one place where the hardware itself raises a task on a queue condition, which is a fourth activation source beyond wavelet, `@activate`/completion and control wavelet. It is also the thing a WSE-2 port most often needs.

**Source.** `tutorials/topic-16-queue-flush/README.rst` (12-step sender sequence, the warning, the receiver note); SIF `tile_config/teardown.csl`; `target/wse2.csl` / `wse3.csl` (`teardown_in_progress_offset` 14 / 15, `TEARDOWN_PENDING` 0x7f3a / 0x7c42).

**Proposed addition.**
1. Add a fourth row to the "Three kinds of task" table (rename it "What activates a task"): "Teardown task 29: activated by hardware when a teardown wavelet arrives or a flushed queue drains. Gets: nothing; read `teardown.get_pending()`. Use: queue reuse, phase changes (allreduce LOCK in D2)."
2. A 6-step sequence diagram: mov32 → done_transmit1 → queue_flush → oq empty → T29 → foo() rebinds and activates transmit2 → exit().

### D7 [minor] Control-task mechanics: encoding, payload and routing
**What is missing.** Only "optional 16-bit payload" is given. Missing details:
- How a control wavelet is built: `ctrl.encode_single_payload(ctrl.opcode.SWITCH_ADV, false, recv_ctrl_id, data16)` (topic-07).
- The payload is the lower 16 bits.
- The same control wavelet also advances switches, and "the data payload of a control wavelet is received by the PE connected by the current switch position, not the new position".
- Sentinel IDs are non-routable, so no route is declared (topic-05).
- They can be above 31 (D1).

The 25-pt-stencil's `*CtrlFin2` tasks are "entrypoints (send control wavelets for switch)" and show the same mechanism in production code.

**Source.** `tutorials/topic-05-sentinels/README.rst`, `tutorials/topic-07-switches-entrypt/README.rst` and `send.csl`; `benchmarks/25-pt-stencil/layout.csl` lines 44–49. Overlaps pedagogy P5. Give the fixer this detail for the P5 code example.

**Proposed addition.** A 6-line snippet (encode plus `@bind_control_task(send_result, @get_control_task_id(43))`). Add one sentence on switch-position timing, linking to Chapter 4.

### D8 [minor] Data-task details: self-triggering, start-up, queue capacity
**What is missing.**
- A PE can trigger its own data task by sending wavelets to its router on a RAMP→RAMP color, which "immediately sends them back to the compute element" (topic-09; WSE-3 `loopback_iq` at queue 4 in the topic-09 map).
- `@activate(main_task_id)` inside `comptime {}` runs a task at program start (pipeline-01, topic-09, sdklayout-01 gv.csl).
- The check-yourself back-pressure answer has no numbers. pipeline-01 "stalls when size exceeds 14" wavelets, which gives a scale for hardware queue capacity on that path. The 8 input queues each have empty/full bits in `INPUT_QUEUE_STATUS` (`tile_config/input_queue_status.csl`: bits 0–7 empty, 8–15 full), which software can poll.

**Why it matters.** These are concrete, checkable mechanisms. The self-trigger in particular is a non-obvious idiom.

**Proposed addition.** Three bullets under "Rules that follow from the hardware". Add "≈14 wavelets" (tagged `sdk`, pipeline-01) to the back-pressure answer.

### D9 [minor] The microthread-collision callout: evidence that the queue convention also matters on WSE-2
**What is missing.** The callout calls this a WSE-3 trap. Yet on WSE-2, "the queue ID of an input or output fabric DSD corresponds to the ID of the microthread" (topic-15). And Cerebras's own WSE-2 25-pt-stencil deliberately splits queues: "FD uses input_queue = 4,5,6,7 ... .input_queue = 4 + queueId, .output_queue = queueId" (task.csl lines 66–78). That is the same fix Lab 3 used. The chapter should mention this convention and the `cslc-driver --disable-auto-microthread-id` flag. It should also say whether the collision also happens on WSE-2, which is currently unverified.

**Source.** `benchmarks/25-pt-stencil/task.csl` lines 66–78; topic-15 README; csl_programming.md §3 (driver flag).

**Proposed addition.** One sentence plus the quote: "Cerebras's own 25-pt stencil uses the same rule: input queues = 4 + output queue." Run experiment E1 below before claiming WSE-2 behaviour either way.

### D10 [minor] Experiments that would replace schematic numbers with measured ones
The widget uses invented cycle numbers, and the notes record "no cycle cost of task switching". Two cheap simulator experiments, each in its own dir under `/home/user/cerebras-sdk/tmp/<id>/`:
- **E1: Lab 3 queue collision on both architectures.** Copy `course/programs/04-heat-stencil`, set `iq_w`/`iq_e` back to 2/3, and compile with `--arch=wse2` and with `--arch=wse3`. Record whether each hangs and the cycle it stalls at. This settles D9 and gives a `measured` tag for the callout's "1,894".
- **E2: shared completion task.** In the same copy, bind all four async ops' `.activate` to one task, and record the hang (pending stuck at 1–3). This turns the widget's claim into a measured fact.
- **(Optional) E3: per-wavelet task overhead.** Compare program 02's data task (`on_value`, 100 wavelets) with a fabin `@fadds` receiving the same 100 wavelets. Report simulator cycles per wavelet as `measured`. This gives the chapter its first number for "what a task costs".

## Out of scope for this chapter (new-chapter or cross-chapter ideas)
- **Ch03:** add microthread priority classes (low/medium/high, `.priority` on async ops) and the main-thread levels to the PE anatomy. Ch05 would then reference them rather than introduce them.
- **Ch04:** "The color picks the route ... AND the task at the receiver" is true only on WSE-2 (also pedagogy P11). Add "(WSE-3: the input queue bound to the color)".
- **Ch06:** the `.unblock` field is introduced there. Cross-link to D2's join pattern so the two chapters tell one story.
- **Ch07:** the reserved-ID list says "use e.g. 9–23 for your local tasks". That conflicts with the WSE-3 topic-09 map marking 21–23 reserved, and SYS_EN_MAIN = 24 conflicts with 25-pt-stencil binding 24. Reconcile it with the D5 budget table.
- **New appendix or sidebar, "The PE configuration space":** `@get_config`/`@set_config` and the address maps in `target/wse2.csl` and `wse3.csl` (TASK_PRIORITY 0x7e08, MISC_CFG 0x7e1f, COLOR_CONFIG, TEARDOWN_PENDING, INPUT/OUTPUT_QUEUE_STATUS, PERF counters, TIMESTAMP_COUNTER). Many "how it works" answers across chapters 3–6 live there.
- **Ch12 (Lab 3) extension:** an exercise that marks the four completion tasks HIGH with `set_task_priority` and measures whether the step time changes.
