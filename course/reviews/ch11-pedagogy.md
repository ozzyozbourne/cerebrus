# ch11 · pedagogy review

Summary: The chapter has the right two programs, good diagrams, and the streaming widget makes the main idea (wavefront, about M + P rather than M × P) easy to see. As a lab, though, it is mostly "read this code". It has no "Run it yourself" box, and unlike Chapter 10 it has no "What happens inside, in order" walk-through. Program 05's `run.py` is never shown. Most of the CSL that is new in this chapter goes unexplained: per-PE `role` and colour params, the `role != 2` / `role != 0` conditionals on routes and queues, queue numbering (2 vs 4) set against Chapter 5's microthread hang, the WSE-2/WSE-3 conditionals, and how one `launch()` reaches every PE. The exercises have weak or missing hints, there is no troubleshooting guidance at all, and the braces callout seems to contradict the braceless `if` the learner has just read in program 03.

## Findings

### P1 [critical] No "what happens inside" walk-through for either program
Location: after `{{out:programs/03-row-reduce/expected_output.txt}}` and after `{{out:programs/05-column-broadcast/expected_output.txt}}`.
Problem: Chapter 10 sets the pattern with a sequence diagram and a "What happens inside, in order" section. Chapter 11 drops it, although these are the first multi-PE programs. The learner is never told that (a) one `memcpy_h2d` with width P scatters row x of V to PE x; (b) `launch('reduce')` calls the RPC on **every** PE in the rectangle, and the host call returns only when **every** PE has called `unblock_cmd_stream()`; (c) the PEs start `reduce()` at slightly different times, and this does no harm, because a `fabin_dsd` operand stalls until wavelets arrive and back-pressure holds the sender; (d) `exit_task` on the first PE fires when its M wavelets have left, not when they have been summed; (e) the answer is read back only from PE P-1.
Why it matters: (b) and (c) answer the question every learner asks: "isn't there a race between the PEs starting?". Without them the program looks correct only by luck, and the core dataflow idea (arrival orders the computation, not the host) is never stated.
Concrete fix: insert after the program 03 output block:
```html
<h3>What happens inside, in order</h3>
<ol>
<li><code>memcpy_h2d(vs, V.ravel(), 0, 0, P, 1, M)</code> writes a P × 1 rectangle, M floats per PE: PE x gets row x of <code>V</code>.</li>
<li><code>launch('reduce')</code> is delivered to <em>every</em> PE in the rectangle. Each PE starts one async DSD op and returns at once, so the command stream stays blocked.</li>
<li>The PEs do not start at exactly the same moment, and they don't need to. A middle PE's <code>@fadds</code> takes <code>in_dsd</code> as an operand, so it waits for each wavelet to arrive. If a PE downstream has not started yet, its input queue fills and back-pressure stalls the PE upstream. Nothing is lost (Chapter 5).</li>
<li>Each PE's op ends after its M-th wavelet. That activates <code>exit_task</code>, which calls <code>unblock_cmd_stream()</code>. PE 0 finishes first, as soon as it has <em>sent</em> v. PE P-1 finishes last, when the total is in its <code>v</code>.</li>
<li><code>launch</code> returns on the host only after every PE has unblocked. Then <code>memcpy_d2h</code> reads <code>v</code> from PE P-1 alone.</li>
</ol>
```
Add the equivalent 4-step list for program 05: x goes to the root only; s goes to all R PEs (width 1, height R, 1 element each); `go()` runs everywhere; the root's `@fmovs` sends while each other PE's `@fmovs(x_dsd, in_dsd)` fills `x`; `t_recv`/`t_send` compute `y` and unblock.

### P2 [major] Per-PE params and role logic are shown but not explained
Location: paragraph after the program 03 figure, and `{{code:programs/03-row-reduce/layout.csl}}`.
Problem: "Write a multi-PE layout with per-PE roles and colors" is the first objective. The only explanation is the figure caption. The text never says that `role`, `send_color` and `recv_color` are compile-time **params**, so each PE gets its own specialised binary and `if (role == 0)` inside `reduce()` is resolved at compile time. It also never explains why the route calls and `@initialize_queue` are guarded: the last PE never sends, so it has no send route and no output queue; the first PE never receives. Chapter 9 says "one ELF per unique param set", but this lab never ties that to P = 8 producing 3 roles × 2 parities, or what the learner should do with it.
Why it matters: This is the reusable skill of the lab. Learners copy the guards without knowing which rule they come from, and then break it when they change the shape (P1/P6 exercises).
Concrete fix: after the `{{code:programs/03-row-reduce/pe_program.csl}}` line, add:
```html
<h3>Reading the code: roles are compile-time params</h3>
<p>The layout loop runs at compile time. For each column x it computes three values, <code>role</code> (0 first, 1 middle, 2 last), <code>send_color</code> and <code>recv_color</code>, and passes them to <code>@set_tile_code</code>. Inside <code>pe_program.csl</code> they are <code>param</code>s, so the compiler knows them. <code>if (role == 0)</code> in <code>reduce()</code> is folded away, and each PE's binary holds only its own branch. P = 8 gives at most 4 distinct binaries (first, last, and two middles with swapped colours). Chapter 9: one ELF per unique param set.</p>
<p>The guards follow one rule: <em>configure only what this PE uses</em>. Every PE except the last sends, so it gets a <code>send_c</code> route (RAMP → EAST) and an output queue bound to <code>send_c</code>. Every PE except the first receives, so it gets a <code>recv_c</code> route (WEST → RAMP) and an input queue bound to <code>recv_c</code>. A middle PE has both, on two different colours: this is the checkerboard of Chapter 4.</p>
```

### P3 [major] Queue numbers look like they break Chapter 5's microthread rule, and nothing says why they don't
Location: `pe_program.csl` of 03 (`@get_output_queue(2)`, `@get_input_queue(2)`) and of 05 (`@get_output_queue(2)`, `@get_input_queue(4)`).
Problem: Chapter 5's "real hang" callout teaches that output queue 2 and input queue 2 share microthread 2 and caused a hang. Program 03's middle PE then uses exactly oq 2 + iq 2, and the chapter is silent about it. Program 05 does use iq 4, yet no PE there has both queues, so the choice looks arbitrary. Chapter 5 also says queues 0 and 1 belong to memcpy, which is why both programs start at 2; this chapter does not repeat that.
Why it matters: A learner who took Chapter 5 seriously will think program 03 is buggy, or that the rule is wrong. A learner who skipped it will copy "2 and 2" into a program with two concurrent ops and hang.
Concrete fix: add a callout after the 03 code:
```html
<div class="callout">
<strong>Why oq 2 and iq 2 are safe here, but were not in Lab 3</strong>
Queues 0 and 1 belong to memcpy on WSE-3, so user queues start at 2. Chapter 5's rule is that two <em>concurrent</em> operations must not share a microthread. A middle PE runs <em>one</em> operation, <code>@fadds(out, in, v)</code>, which uses both queues on one microthread, so there is no clash. Lab 3 runs four ops at once, which is why it needs input queues 4 and 5. Program 05 uses input queue 4 only out of habit; no PE there has both queues.
</div>
```

### P4 [major] Program 05's run.py is missing, and its pe_program is not explained
Location: program 05 section; there is `{{code:...layout.csl}}` and `{{code:...pe_program.csl}}`, but no `run.py`.
Problem: The host side is where the lesson "only the root gets x from the host" shows up (`memcpy_h2d(xs, x, 0, 0, 1, 1, M)`), along with the per-PE scale (`memcpy_h2d(ss, s, 0, 0, 1, R, 1)`). Neither is shown. In the device code, `t_recv` and `t_send` have identical bodies and nothing says why there are two. The non-root `@fmovs(x_dsd, in_dsd)` (fabric→memory, the "fabin→mem op" named in the layout header) is never pointed out as the opposite of program 03's fabric→fabric op.
Why it matters: Without run.py the learner cannot see that the broadcast replaces R−1 host copies, which is the whole point. The duplicated task looks like a mistake.
Concrete fix: add `{{code:programs/05-column-broadcast/run.py}}` before the output block, then:
```html
<p>Look at the host: <code>x</code> is copied to the root only (a 1 × 1 rectangle). Every other PE's <code>x</code> is filled by the fabric. <code>s</code> is copied to all R PEs, one float each. On the device, non-root PEs run <code>@fmovs(x_dsd, in_dsd)</code>: fabric in, memory out. That is the opposite of program 03, where the incoming stream never touches memory. The receivers need <code>x</code> stored before <code>@fmuls</code> can read it. <code>t_send</code> and <code>t_recv</code> do the same work. They are separate only to show that the root's completion means "sent" and a receiver's means "received". Exercise 4 merges them.</p>
```

### P5 [major] No troubleshooting guidance
Location: the chapter has none. Chapter 10 at least shows a debugging method.
Problem: Multi-PE programs fail in new ways, and the learner gets no help reading them. A wrong route or colour parity gives a simulator that runs until timeout with no error. A missing guard (for example, an output queue on the last PE) or P = 1 (the first PE is also the last and sends into nothing) does the same. A `tx` with SOUTH on the bottom PE sends wavelets into the memcpy halo. A wrong `memcpy_d2h` coordinate reads zeros.
Why it matters: The exercises ask the learner to change routes and shapes, so they will hit these failures, and the course gives them no way to tell "hung" from "slow".
Concrete fix: add before "Composing the two":
```html
<div class="callout bug">
<strong>When it goes wrong</strong>
<ul>
<li><b>The simulator never finishes.</b> A wavelet has nowhere to go, or nothing consumes it. Check every sender for a matching receiver route on the <em>same</em> colour (parity!), and check that the last PE has no EAST route and the bottom PE no SOUTH route. P must be at least 2.</li>
<li><b>Hangs only once you add a second async op.</b> Two concurrent ops on one microthread (Chapter 5). Renumber the queues.</li>
<li><b>Result is all zeros.</b> You read the wrong PE: the sum lives on PE P-1, not PE 0.</li>
<li><b>Bisect like Lab 1.</b> Set P = 2 (first + last, no middle), then P = 3, and print <code>v</code> from every PE with one <code>memcpy_d2h(..., 0, 0, P, 1, M)</code> to see how far the sum got.</li>
</ul>
</div>
```

### P6 [major] Exercises are thin and two of them can't be done from the chapter
Location: `<h3>Exercises</h3>`.
Problem: (1) The max exercise's hint suggests there may be no fabric-capable max. The SDK has `@fmaxs` (used with DSD operands in `benchmarks/benchmark-libs/allreduce/pe.csl` and `25-pt-stencil/task.csl`), so the hint sends the learner the wrong way. (2) The 2-D broadcast exercise gives no hint about what changes: rectangle width, a loop over x, `memcpy.get_params(x)`, and whether colours can be reused across columns. (3) "Compare cycles": the chapter never says how to run with `ARCH=wse2`, and the `run.py` output contains no cycle count (it comes from `sim_stats.json`, read only by `run_all.sh`). No exercise asks the learner to reproduce the measured table.
Why it matters: Exercises are where a lab "teaches by doing". At the moment one misleads, one is open-ended, and one cannot be checked.
Concrete fix: replace the `<ol>` with:
```html
<ol>
<li>Make program 03 compute an element-wise <em>maximum</em> instead of a sum. Hint: <code>@fmaxs(dst, a, b)</code> exists and takes DSD operands, like <code>@fadds</code>. Try the drop-in change first. If the compiler rejects a fabric operand, receive into a buffer with <code>@fmovs</code> and then compare in memory. Update the check in <code>run.py</code> to <code>V.max(axis=0)</code>.</li>
<li>Extend program 05 to a C × R rectangle where row 0 multicasts its own x down every column. Hint: loop over x as well as y, pass <code>memcpy.get_params(x)</code>, and widen <code>--fabric-dims</code>. Columns never exchange wavelets, so ask whether the same colour can be reused in every column. (Answer: yes, one colour. Routes are per PE.)</li>
<li>Reproduce the table: <code>for P in 2 4 8 16; do P=$P bash commands.sh; python3 -c "import json;print(json.load(open('sim_stats.json'))['cycle_count'])"; done</code>. Then repeat with <code>ARCH=wse2</code>. Which changes more, P or M?</li>
<li>Merge <code>t_send</code> and <code>t_recv</code> in program 05 into one task. What else do you have to change?</li>
</ol>
```

### P7 [major] No "Run it yourself" box
Location: after the objectives box.
Problem: Chapter 10 opens with how to run the programs. Chapter 11 never says where the programs live, that `commands.sh` takes `P`, `M`, `R` and `ARCH` from the environment, or what `--fabric-dims=$((P+7)),3` means. `commands.sh` is not shown, though Chapter 7 explains the +7 columns.
Why it matters: A learner doing the lab needs the command line before anything else, and the knobs (P, M, R) are what make the widget and table something they can try.
Concrete fix:
```html
<div class="callout ok">
<strong>Run it yourself</strong>
<code>source /home/user/cerebras-sdk/env.sh</code>, then in <code>course/programs/03-row-reduce</code> run <code>bash commands.sh</code>. Change the size with <code>P=16 M=64 bash commands.sh</code> and the chip with <code>ARCH=wse2</code>. Program 05 takes <code>R</code> and <code>M</code>. <code>commands.sh</code> sizes the fabric to your rectangle plus memcpy's frame (<code>--fabric-dims=$((P+7)),3</code>, Chapter 7). The cycle count is in <code>sim_stats.json</code>.
</div>
```
and add `{{code:programs/03-row-reduce/commands.sh}}` before the layout block.

### P8 [major] The braces callout seems to contradict program 03
Location: `<div class="callout">` "CSL detail learned the hard way".
Problem: The callout says statement-form `if/else` needs braces. Program 03, shown just above, has braceless statement-form `if (role != 2) @set_color_config(...);` in the layout and `if (role != 0) @initialize_queue(...);` in comptime, and these compile. It also has a braceless chained *expression* `if (x == 0) 0 else if (x == P - 1) 2 else 1`. The callout sits in the program 05 section without saying it explains why 05's layout and comptime use braces.
Why it matters: The learner sees a rule that the shown code appears to break, and stops trusting the callout or the code.
Concrete fix: replace the callout body with:
```html
<strong>CSL detail learned the hard way</strong>
A lone statement <code>if</code> without braces is fine (program 03: <code>if (role != 2) @set_color_config(...);</code>). Add an <code>else</code> and braces become mandatory: <code>if (a) stmt; else stmt;</code> fails with "Unexpected character". That is why program 05's three-way route choice and its queue setup use <code>{ }</code>. Expression-form <code>if</code> chains need no braces: <code>const role = if (x == 0) 0 else if (x == P - 1) 2 else 1;</code>.
```

### P9 [minor] WSE-2/WSE-3 conditionals are not explained
Location: `out_dsd` and the `@initialize_queue(oq, if (@is_arch("wse3")) .{ .color = ... } else .{})` lines in both programs.
Problem: The only comment is "WSE-3: every fabric transfer goes through a hardware queue bound to a color". It is not said that on WSE-2 the colour goes on the fabout DSD instead, and the output queue is initialised with no colour. Chapter 5 has this in a table, but this is where the learner first sees it in code.
Concrete fix: add after the 03 code: `<p><b>Two chips, one source.</b> On WSE-3 an output queue is bound to one colour by <code>@initialize_queue</code>, and the DSD names only the queue. On WSE-2 the colour goes on the <code>fabout_dsd</code> (<code>.fabric_color</code>), and the queue is initialised without one. Input queues are bound to a colour on both chips. The <code>@is_arch</code> expressions select the right form at compile time (Chapter 5, WSE-2 vs WSE-3 table).</p>`

### P10 [minor] The widget's model (M + 2P) disagrees with the text (M + P)
Location: the "Why it is fast" paragraph ("about **M + P** steps") and the widget readout ("model: ≈ M + 2P … ~2-cycle hop+ramp").
Problem: The two formulas differ, and Chapter 4 gives about 1 cycle per hop plus about 2 per ramp. A middle PE crosses ramp-up, the CE, and ramp-down, so the per-PE latency is a small constant, not exactly 1 or 2.
Concrete fix: change the text to "about **M + c·P** steps, where c is a few cycles of hop + ramp + CE latency per PE (the widget uses c = 2)", and say the same in the widget hint.

### P11 [minor] Program 05 prose overstates the multicast
Location: "Every router below delivers each wavelet to its own CE *and* forwards it south".
Problem: The bottom router only delivers (`tx = .{RAMP}`). The learner reading the layout's three cases sees the mismatch, and the reason the bottom PE must not forward (wavelets would leave the rectangle) is never stated.
Concrete fix: "Every middle router delivers each wavelet to its own CE *and* forwards it south in the same hop: `.tx = .{RAMP, SOUTH}`. The bottom router only delivers (`.tx = .{RAMP}`). Forwarding SOUTH there would push wavelets out of your rectangle into memcpy's frame."

### P12 [minor] The GEMV composition is told, not done
Location: "Composing the two: a distributed GEMV".
Problem: The section names SDK tutorials but gives no path and no task, so it stays a passive paragraph at the high point of the lab.
Concrete fix: append `<p>Try it: open <code>/home/user/cerebras-sdk/extras/csl-extras-202604101435-6-d2f7d96e/examples/tutorials/gemv-08-routes-3/</code>. In its <code>layout.csl</code>, find the route that matches program 05's multicast and the colour pair that matches program 03's checkerboard.</p>`

### P13 [minor] The diagram shows 6 PEs but the program runs 8
Location: the reduction figure (`for (let i = 0; i < 6; i++)`) and its text "PE 5 ends with Σ v".
Problem: The default is P = 8, and the expected output says "summed 8 vectors". This is a small mismatch, but it costs a learner tracing PE indices against the code.
Concrete fix: add to the figcaption "Drawn with P = 6; the program defaults to P = 8, where PE 7 holds the result."
