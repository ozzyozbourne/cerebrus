# ch05 · accuracy review

Summary: Chapter 5 is accurate overall. The task-ID ranges, queue counts, microthread rules, control-task payload, builtin names and Lab 3 details all match the SDK 2.10.1 tutorials, the CSL target library and `course/programs/04-heat-stencil`. The key claim that activating an already-activated task does not queue a second run **is confirmed** by SDK source: `benchmarks/25-pt-stencil/task.csl` says the hardware "uses a single bit to track task activations". That source is not cited anywhere in the course or in the research notes. The fixes below are mostly provenance gaps, two overclaims ("used in every program", "stalled forever"), one wording point on microthread defaults, and labelling an abbreviated snippet. There are no critical errors.

## Findings

### A1 [major] The activation-is-a-flag rule is correct but its real source is never cited
- Location: "Three kinds of task" section, the bullet list under "Rules that follow from the hardware", bullet 2 ("Tasks do not call tasks…"). The widget `#tsk` hint also depends on it.
- Problem: The claim is true. It is the whole premise of the widget, but its only provenance is the blanket `SDK 2.10.1` tag on the paragraph above the list. The research report and notes never state this rule; they only say tasks "cannot call each other, only activate one another". A reader or fixer cannot trace it. The SDK wording is also more careful than the chapter's: two activations collapse into one only if both land before the task runs.
- Evidence: `/home/user/cerebras-sdk/extras/csl-extras-202604101435-6-d2f7d96e/examples/benchmarks/25-pt-stencil/task.csl`, lines ~495–502: "While it may _seem_ better to activate just one task instead of four, we cannot do so since the hardware does not queue activations (instead, the hardware uses a single bit to track task activations). Thus, depending on the sequence of task activations and executions, activating a task multiple times does not guarantee that the said will execute multiple times." The course's own `course/programs/04-heat-stencil/pe_program.csl` lines 46–48 say the same: "Activating one task several times before it runs would collapse into a single run, so we use one task per op and count." Grepping `reports/` and `research_notes/` for "single bit" or "queue activations" finds nothing.
- Concrete fix: Replace bullet 2 with:
  `<li><strong>Tasks do not call tasks.</strong> They activate them. Activation is a single bit, not a counter: activating a task again before it has run does not queue a second run. The SDK's 25-point stencil uses four completion tasks for exactly this reason: "the hardware does not queue activations (instead, the hardware uses a single bit to track task activations)" <span class="tag sdk">SDK 2.10.1, benchmarks/25-pt-stencil/task.csl</span>.</li>`

### A2 [minor] Widget hint gives no source for the one-task failure
- Location: widget `#tsk`, `<p class="hint">`.
- Problem: The widget shows a hang that follows from A1, but nothing tells the reader that this is a documented SDK design rule rather than the course's own conjecture. Its cycle numbers (3, 4, 6; 2-cycle task runs) are invented for illustration and are not labelled as such.
- Evidence: The JS `const events = [[3, "se"], [4, "sw"], [4, "rw"], [6, "re"]];` and `busyUntil = t + 2` are made-up values. The real run is 10,291 cycles for 50 steps (`course/programs/04-heat-stencil/expected_output.txt`: "[10291 simulated cycles, WSE-3]").
- Concrete fix: Add this sentence to the end of the hint: ` Cycle numbers are illustrative, not measured. The SDK's own 25-point stencil uses one completion task per transfer for the same reason (benchmarks/25-pt-stencil/task.csl).`

### A3 [minor] "used in every program in this course" is false
- Location: the paragraph after the WSE-2/WSE-3 table, "The idiom that makes one source file serve both chips — used in every program in this course:".
- Problem: Program 01 (SAXPY) contains no `@is_arch` at all. The data-task-ID form of the idiom shown here (`@get_data_task_id(color)` vs `(queue)`) appears only in program 02.
- Evidence: `grep -c is_arch course/programs/*/pe_program.csl` gives 01-saxpy: 0, 02: 1, 03: 2, 04: 3, 05: 2. `grep -l get_data_task_id course/programs/*/*.csl` returns only `02-wavelet-tasks/pe_program.csl`.
- Concrete fix: Replace the sentence with `The idiom that makes one source file serve both chips (<code>@is_arch</code> selects the per-chip form; programs 02–05 all use it):`

### A4 [minor] Code snippet is abbreviated without saying so
- Location: `<div class="filename">pe_program.csl (Lab 1, program 02)</div>` and the `<pre>` that follows it.
- Problem: The `on_value` body shown (`stats[0] += v; count[0] += 1;`) is not what the file contains. The real task also updates sum of squares, max and min, and calls `sys_mod.unblock_cmd_stream()`. The `comptime` block also leaves out the three `@export_symbol` lines. The filename label suggests a verbatim copy.
- Evidence: `course/programs/02-wavelet-tasks/pe_program.csl` lines 22–30 (`stats[1] += v * v; … if (count[0] == @as(u32, N) and host_waiting) sys_mod.unblock_cmd_stream();`) and lines 47–49 (exports).
- Concrete fix: Change the filename div text to `pe_program.csl (Lab 1, program 02), excerpt, simplified`. Replace the task line with `task on_value(v: f32) void { stats[0] += v; /* … */ count[0] += 1; }`.

### A5 [minor] Bug callout overstates the hang and leaves out that microthread = queue ID is only the default
- Location: `.callout.bug` "A real hang from this course".
- Problem: (a) "stalled forever" is not something anyone observed. Chapter 12, the primary account, says it stalled "with no progress at cycle 1,894 and had to be killed". (b) "On WSE-3 an async fabric op runs on the microthread matching its queue ID" is true only when no `.ut_id` is given. The table in this same chapter says WSE-3 has an "explicit `.ut_id` (0–7)", so as written the callout contradicts the table. (c) The SDK quote has no provenance tag.
- Evidence: `course/12-lab-stencil.html:248`: "stalled with no progress at cycle 1,894 and had to be killed". `EX/tutorials/topic-15-wse3-microthreads/README.rst` lines 37–38: "(if they are not explicitly specified, they default to the respective queue IDs)", and line 41: "Note, however, that two operations cannot concurrently use the same microthread."
- Concrete fix: Replace the callout body with:
  `The first version of Lab 3 used output queues 2, 3 and input queues 2, 3. It compiled cleanly, then the simulator stopped making progress at cycle 1,894 and had to be killed. On WSE-3, an async fabric op with no explicit <code>.ut_id</code> runs on the microthread whose ID matches its queue, so "send east" (output queue 2) and "receive from west" (input queue 2) both wanted microthread 2. Renumbering the input queues to 4 and 5 fixed it <span class="tag measured">Measured</span>. (Giving each op its own <code>.ut_id</code> would also work.) The SDK states the rule: "two operations cannot concurrently use the same microthread" <span class="tag sdk">SDK 2.10.1, topic-15</span>.`

### A6 [minor] "A task cannot wait" overclaims
- Location: the "Rules" list, bullet 1, "Run to completion".
- Problem: A task can execute a synchronous (blocking) fabric DSD op. The hardware allows it. What goes wrong is that the CE is then tied up, which can deadlock, for example by starving memcpy. "Cannot" should be "must not". The quiz answer in the same chapter ("Why must a task not 'wait for' a transfer?") already frames it as "must not".
- Evidence: `EX/tutorials/pipeline-01-basic/README.rst` lines 33–39: "The microthread is necessary because the CE (compute engine) must have some resources to run memcpy kernel. The kernel stalls if a blocking instruction `@add16(outDsd, inDsd, 1)` is used … The CE has no resource to run the H2D command received by the router, so it stalls."
- Concrete fix: Replace `A task cannot wait.` with `A task must not wait: a blocking fabric op inside a task ties up the CE and can stall the whole PE (SDK pipeline-01: "The kernel stalls if a blocking instruction … is used").`

### A7 [minor] Source note for the WSE-2/WSE-3 table leaves out the source of the "Fabric inputs per DSD op" row, and "several" is vague
- Location: the paragraph below the WSE-2 vs WSE-3 table ("All rows SDK 2.10.1 (topic-05, topic-15, topic-16 tutorials and the target library)") and the last table row.
- Problem: The one-fabric-input rule comes from `sdklayout-03 add2vec.csl`, which is not one of the listed sources. The SDK only says that WSE-3 does not allow *multiple* fabric inputs, so "several" for WSE-2 claims more than the source supports.
- Evidence: `EX/tutorials/sdklayout-03-ports-and-connections/add2vec.csl`: "WSE3 does not allow multiple fabric inputs per DSD operation. Therefore, we introduce a FIFO for portability" (quoted in the report, line 110).
- Concrete fix: Change the WSE-2 cell from `several` to `more than one`. Change the note to `All rows <span class="tag sdk">SDK 2.10.1</span> (topic-05, topic-15, topic-16 and sdklayout-03 tutorials and the target library).`

### A8 [minor] Data-task payload is not limited to one 32-bit argument
- Location: the "Three kinds of task" table, Data task row, "Gets" column: "the 32-bit payload".
- Problem: This is correct but incomplete. A data task can instead take two 16-bit arguments (the lower and upper halves). Chapter 4 and the sparse tutorial rely on this, and the chapter does not mention it.
- Evidence: `research_notes/.../csl_programming.md:44`: "A data task can take one `u32`/`f32` argument, or two 16-bit arguments for the lower and upper halves … `task main_task(wavelet_data: i16, index: i16)`" (topic-04 README).
- Concrete fix: Change the cell to `the 32-bit payload (one 32-bit arg, or two 16-bit halves)`.

## Verified (no change needed)
- WSE-2 data task IDs 0–23 = colors; WSE-3 0–7 = input queues; local tasks 0–30 / 8–30: topic-05 README lines 6–11.
- Input/output queues 8/6 (WSE-2) and 8/8 (WSE-3): csl-libs `target/wse2.csl:109,114` and `target/wse3.csl:299,304` (`NUM_INPUT_QUEUES = 8`, `NUM_OUTPUT_QUEUES = 6/8`).
- WSE-3 output queue bound to one color, reuse via `@queue_flush`: topic-16 README lines 4–9.
- WSE-2 microthread = queue ID; WSE-3 `.ut_id` 0–7 that defaults to the queue ID: topic-15 README lines 8–11 and 37–38.
- Control task with an optional 16-bit payload in the lower bits: topic-07 README lines 4–10. `@bind_control_task` exists (topic-05 `pe_program.csl:78`).
- Fabric DSD needs its color's task blocked: pipeline-01 README lines 14–19.
- Queues 0 and 1 are reserved by memcpy on WSE-3: notes `csl_programming.md:99`.
- Lab 3 details: task names `t_se/t_sw/t_rw/t_re`, `pending`, `start_step()`, `update()` with 3 vector ops (`@fadds`, `@fmacs`, `@fmacs`), `run(T, a)`, `unblock_cmd_stream()` on `step == T`, output queues 2/3 and input queues 4/5: `course/programs/04-heat-stencil/pe_program.csl` lines 32–35 and 49–93.
- The picker quote and its "via search extract" vendor tag match `wse_hardware.md:128` and report line 78.
- The widget logic is correct: in one-task mode, the second activation at tick 4 is dropped, `pending` sticks at 1, and the program hangs.

## Not verifiable
- The cycle-1,894 stall and the claim that renumbering the input queues was what fixed it. No log or archived version of the earlier program exists. The only other record is the matching prose in `course/src/12-lab-stencil.html:49`.
- Whether a task that is *currently running* when it is activated again will run once more afterwards. The SDK comment only says that activations are a single bit and that repeated activation "does not guarantee" repeated execution. The exact semantics depend on when the bit is cleared, which is not documented locally. The chapter's wording ("already-activated", meaning pending) stays safe as long as it does not say anything about a running task.
- The scheduler's priority and arbitration order between several ready tasks are not documented locally (report line 93). The chapter makes no claim here, and it should not add one.
