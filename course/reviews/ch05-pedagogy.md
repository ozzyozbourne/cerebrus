# ch05 · pedagogy review

Summary: The chapter's core idea is right: arrival activates a task, the picker runs one task at a time, each to completion, so loops become state machines. The four-task widget and the real-hang callout are its best teaching moments. But it leans on things taught later: async DSD ops and fabric DSDs (ch06), memcpy, RPC and `unblock_cmd_stream` (ch07). It never says that tasks and ordinary `fn`s are different things. Three objectives get no worked example: control tasks, `@block`/`@unblock` and `@activate`. "Activation is a flag" is the lesson the widget depends on, but the text never squares it with data tasks running once per wavelet. The WSE-2/WSE-3 section is a table of facts. It explains neither the consequences nor what a failure looks like. The Check-yourself questions skip the chapter's three key lessons.

## Findings

### P1 [critical] Chapter depends on async DSD ops and fabric DSDs, which are taught only in Chapter 6
Location: Rules list ("a DSD op with `.async = true`", "a fabric DSD can consume them"), task table row "an async DSD op finishing", the widget hint ("four async transfers"), the WSE table rows "fabout DSD", "Fabric inputs per DSD op", and the hang callout ("an async fabric op runs on the microthread...").
Problem: Chapter 3 says only that DSDs are "base address, length, stride (Chapter 6)". The words "async", "fabric DSD", "fabout DSD" and "DSD operation" are never defined before this chapter uses them as the main way to do long work. The learner meets "an operation finishing activates a task" before knowing what kind of operation can finish on its own.
Why it matters: The key idea ("a task cannot wait; start long work asynchronously and let a different task run on completion") rests on a mechanism the learner cannot yet picture. They will memorise it rather than understand it.
Concrete fix: Add a short primer box straight after the "Three kinds of task" table:
> **Preview: async operations (full story in Chapter 6).** A CE can launch a vector instruction, such as "copy 64 words from memory out onto the fabric", and keep going without waiting for it. Such an operation runs on one of the PE's 8 *microthreads* (Chapter 3) while the CE goes back to the picker. You ask for this with `.async = true`, and you name a task to run when it ends with `.activate = some_task`. The operands are *DSDs*, descriptors of a memory array or a fabric stream. A *fabric* DSD (`fabin_dsd` for receiving, `fabout_dsd` for sending) streams many wavelets through one instruction instead of running a data task per wavelet. For this chapter you only need one fact: an async op is "work in flight", and its completion is an event that activates a local task.

Also add a 3-line code example to the "Local task" discussion (see P4).

### P2 [major] Tasks versus functions is never explained, and the state-machine figure blurs them
Location: "Tasks as a state machine" figure (boxes `run(T, α)`, `start_step()`, `4 done tasks`, `update()`), and the widget, which draws `update` as its own run on the CE timeline.
Problem: In Lab 3 (`course/programs/04-heat-stencil/pe_program.csl`) only `t_se/t_sw/t_rw/t_re` are tasks. `run`, `start_step`, `update` and `op_done` are ordinary `fn`s, called synchronously inside whichever task is running. The figure draws all four boxes the same way. The widget gives `update` its own CE slot one cycle after the last done task, which suggests it is scheduled separately. Nowhere does the chapter say that CSL also has normal functions, or which code runs as a task.
Why it matters: A learner told "code is a set of tasks" will think every handler must be a task. They will not see that the state is just globals (`pending`, `step`) with plain function calls between hand-offs. The wrong model leads to over-using task IDs, which are scarce (P8).
Concrete fix: (a) Add after the Rules list:
> Tasks are only the *entry points* the hardware can start. Inside a task you call ordinary CSL `fn`s as on any CPU, synchronously and on the same stack. A function such as `update()` runs *as part of* whichever task called it. Lab 3 has exactly four tasks; `start_step`, `update` and `op_done` are plain functions, and the host-callable `run` is a function that memcpy's own command task calls (Chapter 7).

(b) In the figure, use a different style for `fn` boxes than for task boxes (dashed outline for functions), and add a legend: "solid = task (hardware entry point), dashed = function called inside a task". (c) In the widget, label the update bar "update() inside t_xx" or attach it to the last done-task bar. Do not draw it as a separate pick.

### P3 [major] "Activation is a flag" conflicts with data tasks running once per wavelet, and nothing resolves it
Location: Rule 2 ("Activation is a flag: activating an already-activated task does not queue a second run"), compared with the table row "Data task: activated by each arriving wavelet".
Problem: A careful learner will ask: "If activation is one bit, do I lose wavelets when two arrive before my data task runs?" They don't. Wavelets wait in the input queue, and the task is re-activated while the queue is not empty. Only events with no buffer behind them collapse: `@activate` calls and async-op completions. The chapter never draws this line, and the widget's hang only makes sense once it is drawn.
Why it matters: This is the chapter's deepest point about internal behaviour. Without it the learner either fears data loss on streaming input, or misses why Lab 3 needs four tasks.
Concrete fix: Replace rule 2 with:
> **Tasks do not call tasks; they activate them, and activation is a single bit.** For local tasks this bit is all there is: two `@activate`s, or two async completions, that land before the task runs give **one** run. Data tasks behave differently because the input queue sits behind the bit: each wavelet waits in the queue, and the task is activated again while the queue is not empty, so wavelets are never merged. The rule of thumb: *events that carry data are buffered; events that carry no data collapse.*

Add a Check-yourself question for it (see P10).

### P4 [major] Objective 2 (`@activate`, `@block`/`@unblock`, completion) has no worked code
Location: Objectives list, item 2; the Rules list.
Problem: The only code in the chapter is the data-task binding idiom. There is no snippet with `@activate`, `@block`, `@unblock`, `.activate =` or `.unblock =`, and no `@bind_local_task` example. The learner is told these build control flow but never sees them do it.
Concrete fix: Add a "Control flow in 12 lines" listing after the Rules list, based on Lab 3 and pipeline-01:
```csl
const done_id: local_task_id = @get_local_task_id(10);
task on_done() void { /* runs once the async op has finished */ }

fn start() void {
  @fmovs(out_dsd, buf_dsd, .{ .async = true, .activate = done_id }); // completion -> on_done
}
task kick() void { start(); }   // or: @activate(kick_id) from any task

comptime {
  @bind_local_task(on_done, done_id);
  @block(h2d_task_id);          // let a fabin_dsd, not the data task, consume these wavelets
}
```
Then add one sentence on `.unblock = id`: "use it when the task is already activated, for example by data, and should run only once a transfer has drained". The SDK's pipeline-01 README covers the block-a-data-task case.

### P5 [major] Control tasks: no example, no ID range, no link to sentinels or switches
Location: "Three kinds of task" table, row 3; objective 1.
Problem: The row says only "a control wavelet carrying its ID … optional 16-bit payload … end-of-stream sentinels". The chapter never says that a control task ID is *not a color*, so it needs no route (topic-05-sentinels). It does not say where the ID and payload sit in the wavelet (payload = lower 16 bits, topic-07). It does not say which IDs are legal, while Chapter 7 lists memcpy's reserved control IDs 33–37 and 40, which suggests an ID space above 31. Chapter 4 says "control wavelets … advance a switch, trigger a task" and this chapter never connects to that.
Why it matters: Objective 1 asks the learner to "say what activates each" kind of task. For control tasks they cannot. A sentinel is the standard answer to "how does a streaming receiver know the stream ended?", a question every learner will ask after the data-task section.
Concrete fix: Add a paragraph and a small diagram after the table: "Sentinel pattern: the sender streams N data wavelets on color c, then sends one *control* wavelet whose payload names control task ID S. The receiver's data task handles the N values; the control wavelet activates the task bound with `@bind_control_task(send_result, S)`, which knows the stream is complete (SDK topic-05)." State the legal control-task ID range from the SDK (check it in the CSL libs / `@get_control_task_id`). Add a forward note: "memcpy reserves some of these IDs (Chapter 7)."

### P6 [major] The "why" of run-to-completion is missing, and there is no analogy
Location: Lede and Rules list.
Problem: The chapter says what (no OS, no threads, tasks run to completion) but not why the hardware is built this way. There is no saved context to switch, no stack per thread, only 48 KB of SRAM, and the design is dataflow: work starts when its data arrives. There is also no analogy to a model the learner already has.
Why it matters: A technically strong learner remembers rules much better when they follow from constraints. A familiar analogy gives them the right intuitions for free, such as "never block the event loop".
Concrete fix: Add after the lede:
> **If you know JavaScript or interrupt handlers, you already know this model.** Each task is like a callback on an event loop, or a short interrupt service routine. It runs, returns, and must never spin waiting for something; the picker then chooses the next ready callback. The hardware can afford no more: a PE has 48 KB of memory, no MMU and no context-switch machinery, so there is nothing to save if a task were paused. In exchange, scheduling costs almost nothing, and work starts the cycle its data arrives. That is the dataflow ideal behind the whole wafer.

Also state what is not guaranteed: "If several tasks are ready, do not rely on which one the picker chooses first". Check the SDK for a priority rule, and say so if there is one. The widget currently picks in insertion order without saying so.

### P7 [major] The WSE-2 vs WSE-3 section lists facts but not consequences or failure symptoms
Location: "WSE-2 versus WSE-3" table and objective 3 ("Avoid the two WSE-3 traps").
Problem: (a) "an input queue bound to a color (0–7)" reads as if colors 0–7 were the limit. It is the queue ID range, and any routable color can be bound. (b) The main consequence is never stated: on WSE-3 a PE can have at most 8 data tasks, and only 6 when memcpy holds queues 0–1 (stated only in a code comment). That is why local IDs start at 8. (c) The learner is not told how the "queue-bound data task" trap shows up: a compile error, a silent wrong binding, or a hang? (d) "reuse needs `@queue_flush`" and `.ut_id` are not explained. (e) This chapter names only one trap explicitly; the objective promises two.
Concrete fix: Rename the column header to "Data task ID comes from" / "an input queue (ID 0–7) bound to any routable color". Add below the table:
> **What this means in practice.** On WSE-3 the number of data tasks on a PE is limited by queues, not colors: 8 input queues, of which memcpy takes 0 and 1, so at most 6 of yours. That is why local task IDs start at 8, since IDs 0–7 are kept for queue-bound data tasks. **Trap 1:** WSE-2 code that binds a data task straight to a color ID does not port: [state the observed symptom — compile error or hang — after checking with cslc]. **Trap 2:** two concurrent async ops on the same microthread hang with no error (callout below).

Define microthread in one clause on first use here ("one of 8 hardware slots that runs an async op, Chapter 3").

### P8 [minor] Local task ID ranges contradict Chapter 7's reserved IDs
Location: WSE table row "Local task IDs: 0–30 / 8–30".
Problem: Chapter 7 says memcpy reserves local IDs 24, 27, 28, 30 (29 = teardown, 31 = NOP) and advises "use e.g. 9–23". Chapter 5 offers 8–30 with no warning, so a learner who picks 24 or 30 after reading this chapter collides with memcpy.
Concrete fix: Add to the row: "(of which memcpy reserves 24, 27, 28, 30, and 29 for teardown; see Chapter 7. Safe choice: 8–23)". Keep the ranges consistent with Chapter 7's table.

### P9 [minor] Back-pressure rule states fabric-DSD consumption as an option, but the SDK says blocking is required
Location: Rule 3: "A blocked data task leaves wavelets waiting in the queue — which is how a fabric DSD can consume them instead."
Problem: SDK pipeline-01 says you *must* block the color/task when a fabin DSD reads the stream. Otherwise the data task consumes the wavelets first. The phrasing reads like an optional feature. Also, "back-pressure" is used as the name of `@block`. In Check-yourself Q1 it means the lossless fabric stalling the sender, and that is the usual meaning.
Concrete fix: Rename the rule "Blocking" and rewrite it as: "`@block(id)` stops a task from being picked even if activated; `@unblock(id)` releases it. **If a fabric DSD is to read a queue, you must block that queue's data task.** Otherwise the task fires on each wavelet and consumes it first (SDK pipeline-01). Blocked wavelets wait in the queue, and when the queue fills, the lossless fabric pushes *back-pressure* upstream to the sender."

### P10 [major] Check-yourself questions miss the chapter's three key lessons; Q2 relies on untaught memcpy
Location: Quiz.
Problem: Q1 (back-pressure) and Q3 (port a binding) are fine, but Q3's answer should mention avoiding queues 0/1. Q2's answer leans on "the memcpy runtime", which has not been taught. No question tests collapsing activation (the widget's lesson), microthread sharing (the callout), or tasks versus functions/state machines.
Concrete fix: Change Q2's answer to: "Tasks run to completion and there is only one CE. While one task spins, no other task, including the one that would deliver the data, can run, so the PE deadlocks. Start the transfer async and let its completion activate another task. (The host runtime, memcpy, also needs the CE; Chapter 7.)" In Q3's answer add "(not 0 or 1, which memcpy uses on WSE-3)". Add:
- "Two async receives both use `.activate = done` and finish one cycle apart, before `done` runs. How many times does `done` run, and how do you fix it?" Answer: "Once, because activation is a flag. Give each op its own local task, as Lab 3 does, or count completions some other way."
- "On WSE-3 you send on output queue 3 and receive on input queue 3 at the same time, with no `.ut_id`. What happens?" Answer: "Both default to microthread 3. Two ops cannot use one microthread at once, so the program hangs. Renumber a queue or set `.ut_id`."
- "Convert `for (s = 0; s < T; s++) { exchange(); update(); }` into tasks. Which pieces are tasks and which are functions?" Answer: "Only the completion handlers need to be tasks. `start_step` and `update` are functions, and the loop counter is a global checked at the end of `update`."

### P11 [minor] Chapter 4 says the color picks the task, which is WSE-2-only, and Chapter 5 never reconciles it
Location: Chapter 4 wavelet figure ("The color picks the route at every router AND the task at the receiver"), compared with this chapter's figure caption.
Problem: Read alone, the Chapter 4 sentence is wrong for WSE-3. Chapter 5 gives the correct rule but does not point out that it revises the earlier statement.
Concrete fix: In the "path from wire to code" section, add: "Chapter 4 said that the color picks the task at the receiver. That is exactly true on WSE-2. On WSE-3 one more step sits in between: the color is bound to an input queue, and the *queue* picks the task." (Alternatively, ask the ch04 fixer to qualify the sentence there.)

### P12 [minor] The hang callout does not explain why the hang is silent, or how it was found
Location: "A real hang from this course" callout.
Problem: The learner learns the rule but not the diagnostic skill. Why didn't the compiler catch it? (Queue-to-microthread defaults are resolved per op, and concurrency happens at run time.) How did the authors find microthread 2? (Instruction trace or sim logs.) It is also unclear whether the same pairing is safe on WSE-2, where microthread = queue ID as well.
Concrete fix: Add two sentences: "The compiler cannot see that the two ops overlap in time, so the program builds cleanly and the second op simply never starts. The tell is a simulator that stops advancing with an async op still pending; the instruction trace (Chapter 9) shows which microthread is stuck." Check whether the WSE-2 build of the same code also hung, and say so, since the table says WSE-2 microthread = queue ID.

### P13 [minor] Figure and widget details that can mislead
Location: "Path from wire to code" figure; widget.
Problem: (a) The "task table" with "activated/blocked" columns is a schematic model, but it carries no tag, so it may be read as a documented hardware structure. (b) The router box says "route says RAMP", but the RAMP hop is not drawn, though Chapter 4 makes a point of its ~2-cycle cost. (c) The data task "Gets: the 32-bit payload", while Chapter 3 shows the `(i16, i16)` two-argument form. (d) The widget's 2-cycle task duration and its pick order are invented and not labelled as such.
Concrete fix: (a) Add a `<span class="tag derived">` and "schematic" to the caption. (b) Relabel the arrow router → input queue as "RAMP". (c) Table cell: "the 32-bit payload (as one f32/u32/i32, or two 16-bit args)". (d) Add to the widget hint: "Timings are schematic: each task takes 2 cycles, and ready tasks are picked in a fixed order."

### P14 [minor] Undefined jargon on first use
Location: Throughout.
Problem: These terms are used without definition or a pointer: "memcpy" (code comment, Q2), "host RPC" and `unblock_cmd_stream()` (state figure), "target library", "topic-05, topic-15, topic-16 tutorials" (provenance line), `comptime`, `@queue_flush`, `.ut_id`, and "CE" in "picker → CE" (defined in ch03, but worth re-expanding).
Concrete fix: Add a one-line gloss or chapter pointer at first use. "memcpy, the SDK's host-to-device runtime, which owns some colors, queues and task IDs (Chapter 7)". "`unblock_cmd_stream()`: tells the host runtime that this PE has finished the current host call (Chapter 7)". "`comptime` block: code run by the compiler to set up bindings (Chapter 9)". For the provenance line, name the SDK tutorial folders (`examples/tutorials/topic-05-sentinels`, etc.).
