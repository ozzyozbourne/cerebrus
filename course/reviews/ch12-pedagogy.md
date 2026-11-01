# ch12 · pedagogy review

Summary: The lab has a good capstone problem: a real 1-D heat stencil, validated against numpy, with a well-chosen hang story and a measured performance table. As a learn-by-doing lab it falls short. "The code" section is three listings (layout, pe_program, run.py) with **zero prose**, so the halo exchange, the `pending` counter, the one-task-per-op rule and the step loop are all left for the learner to decode from comments. The measurement section never says how to produce its numbers (no `commands.sh`, no `STEPS=` variable, no `cycle_count` field). Its 0-step baseline takes a different code path, so the table's 128 cycles/step disagrees with the chapter's own "~130" marginal figure. The exercises have no hints. Exercise 2's expected result is wrong at the default size, and Exercise 1 has a correctness trap nobody mentions. The performance interpretation itself ("fixed + per-cell", surface-to-volume) is clear and well pitched.

## Findings

### P1 [critical] The program is shown but never walked through
Location: `<h2>The code</h2>` (src lines 40–45): three `{{code:...}}` listings, then one sentence about validation.
Problem: Nothing in the prose explains how one timestep actually runs: `run()` → `start_step()` issues four async `@fmovs` → each completion activates its own task → `op_done()` decrements `pending` → the last one calls `update()` → `update()` either calls `start_step()` again or `unblock_cmd_stream()`. The learner has to piece this together from code. The objective "Drive an iterative algorithm entirely from tasks" is therefore never taught. Other points also go unexplained: there is no loop anywhere, the host's `rt.launch(..., nonblock=False)` returns only when the *last* step calls `unblock_cmd_stream()` (Chapter 7's rule, applied here across many tasks), `steps == 0` takes a separate path, and the fixed end temperatures come from the host-written ghosts that the edge PEs never overwrite because `has_w`/`has_e` is false.
Why it matters: This is the capstone. Chapters 5–7 taught the pieces separately, and this lab is where the learner should see them joined. Without a walkthrough it is a reading exercise, not a lab.
Concrete fix: Insert after `{{code:programs/04-heat-stencil/pe_program.csl}}` (or between the listings):
```html
<h3>One timestep, step by step</h3>
<p>There is no loop in <code>pe_program.csl</code>. The iteration is a chain of tasks:</p>
<ol>
<li><strong>Host → <code>run(T, α)</code>.</strong> memcpy's command task calls this RPC (Chapter 7). It stores <code>T</code> and <code>α</code> and calls <code>start_step()</code>. Then it <em>returns without unblocking the command stream</em>, so the host's <code>launch(..., nonblock=False)</code> keeps waiting.</li>
<li><strong><code>start_step()</code></strong> sets <code>pending = ops_per_step</code> (4 for an interior PE, 2 for an end PE). It then launches up to four async <code>@fmovs</code>: send <code>u[n]</code> east, receive into <code>u[n+1]</code>, send <code>u[1]</code> west, receive into <code>u[0]</code>. Each one is a single wavelet (<code>.extent = 1</code>) and each names its own completion task. The function returns at once, and the CE goes back to the task picker.</li>
<li><strong>Completions.</strong> As each transfer finishes, its task (<code>t_se</code>, <code>t_sw</code>, <code>t_rw</code>, <code>t_re</code>) runs and calls <code>op_done()</code>, which decrements <code>pending</code>. These four are the only tasks in the program. <code>start_step</code>, <code>update</code> and <code>op_done</code> are ordinary functions running inside whichever task called them.</li>
<li><strong>Last completion → <code>update()</code>.</strong> When <code>pending</code> reaches 0 both ghosts hold fresh neighbour values and both sends have left. The three DSD instructions compute <code>lap</code> and update <code>u[1..n]</code>.</li>
<li><strong>Next step or finish.</strong> <code>update()</code> calls <code>start_step()</code> again (back to 2), or after the last step calls <code>unblock_cmd_stream()</code>. Only then does the host's <code>launch</code> return and the D2H copy run.</li>
</ol>
<p>The ends of the rod: PE 0 has <code>has_w = false</code>, so it never receives into <code>u[0]</code>. The 1.0 the host wrote there stays put, and that is the fixed (Dirichlet) boundary. The same holds for the last PE's <code>u[n+1] = 0.0</code>.</p>
```
Also add a small sequence/timeline figure (CE row and four microthread rows over one step), in the style of the ch05 widget.

### P2 [major] The `pending` counter and the one-task-per-op design are never justified in prose
Location: same section; the reasoning exists only as a code comment (pe_program.csl "Activating one task several times before it runs would collapse into a single run").
Problem: A learner will ask three questions the page does not answer. (a) Why four tasks instead of one `done` task activated four times? Activation is a flag (ch05), so four completions could collapse into one run and `pending` would never reach 0. (b) Why wait for the *sends* to complete, not just the receives? `update()` overwrites `u[1]` and `u[n]`; if the async send has not read them yet, the neighbour gets the new value. (c) Why is there no race on the ghosts? A neighbour that runs ahead sends its step s+1 edge cell early, but the wavelet waits in this PE's input queue until the matching receive is issued in this PE's next `start_step()`. The fabric is lossless with back-pressure (ch05), and that is what keeps neighbours in lock-step. Also note that `pending` is set *before* any op is issued, so a completion cannot run against a stale counter.
Why it matters: These are the "what happens inside" ideas that make the program correct. Without them the learner copies the pattern without being able to adapt it, for example in Exercise 1.
Concrete fix: Add after the walkthrough in P1:
```html
<div class="callout">
<strong>Why the counter looks like this</strong>
<ul>
<li><em>One task per operation.</em> Activation is a single bit (Chapter 5). Four completions that activate the same task before it runs would give one run, and <code>pending</code> would stay at 3 forever. Four tasks, one per op, cannot collapse.</li>
<li><em>Sends are counted too.</em> An async send reads <code>u[n]</code> some time after it is issued. If <code>update()</code> ran as soon as the ghosts arrived, it could overwrite <code>u[n]</code> before the send read it, and the neighbour would get next step's value.</li>
<li><em>No ghost race.</em> If a neighbour finishes its step first and sends its next edge cell early, that wavelet waits in this PE's input queue until this PE issues its next receive. Back-pressure keeps neighbours at most one step apart, with no barrier needed.</li>
<li><em>Counter first.</em> <code>pending</code> is set before any op is launched. No completion task can run while <code>start_step()</code> is still running (one task at a time), but setting it first keeps the code correct even if that changes.</li>
</ul>
</div>
```

### P3 [major] The measurement method cannot be reproduced from the page, and its baseline is biased
Location: "Measuring a timestep" (src lines 66–77).
Problem: (1) The page never says how to run with 0 or 100 steps, or how to change P and n. `commands.sh` is not included among the listings, and it is what reads `P`, `n`, `STEPS`, `ARCH` from the environment. (2) It never names the field to read: `cycle_count` in `out/sim_stats.json`, as used by `run_all.sh`. (3) The 0-step run takes a different path (`run()` unblocks at once and never calls `start_step()`), so "the host transfers are identical, so the difference is pure device work" is not quite true. The chapter's own numbers show this. (16,791 − 3,991)/100 = 128, but the marginal cost from the page's 10/50/100-step points is (16,791 − 5,071)/90 ≈ 130.2, and from 0 to 10 steps it is only 108/step. The text then says "~130 cycles each" right under a table that says 128, without reconciling the two. (4) Nothing mentions run-to-run noise: ch09 says totals repeat to within 2 cycles, which is what makes differencing valid.
Why it matters: Objective 3 is "measure kernel cost by differencing runs". A learner cannot repeat the measurement, and an attentive one will spot the 128 vs 130 mismatch and lose trust in the 88 + 2.5·n fit.
Concrete fix: (a) Add `{{code:programs/04-heat-stencil/commands.sh}}` to the code section. (b) Replace the paragraph at src line 67 with:
```html
<p>Every run writes <code>out/sim_stats.json</code>. Its <code>cycle_count</code> is the total for the whole simulation, host transfers included. To isolate the kernel, run the same configuration at two step counts and subtract. Host traffic is identical, so the difference is device work for the extra steps:</p>
<pre><code>cd course/programs/04-heat-stencil
STEPS=10  bash commands.sh &amp;&amp; python3 -c "import json;print(json.load(open('out/sim_stats.json'))['cycle_count'])"
STEPS=100 bash commands.sh &amp;&amp; python3 -c "import json;print(json.load(open('out/sim_stats.json'))['cycle_count'])"
P=16 n=64 ARCH=wse2 STEPS=100 bash commands.sh   # other configs: set P, n, ARCH</code></pre>
<p>This works because the simulator is deterministic to within about 2 cycles (Chapter 9). Use two <em>non-zero</em> step counts. With <code>STEPS=0</code>, <code>run()</code> skips the step machinery entirely, so a 0-step baseline folds start-up effects into the per-step figure.</p>
```
(c) Either re-measure the table with 10 and 100 steps (and refit the model) or add, below the table: "Differencing against 0 steps slightly under-counts. At P = 8, n = 16 the marginal cost between 10 and 100 steps is 130 cycles, not 128, because the first few steps are cheaper. The fit below uses the 0/100 numbers; the conclusions do not change."

### P4 [major] Exercise 2's expected outcome is false at the default size
Location: Exercises, item 2 ("Run 1,000 steps and confirm the profile approaches the straight line between the two boundary temperatures").
Problem: At the default P = 8, n = 16 (L = 128 cells) with α = 0.25, diffusion needs on the order of L²/(π²α) ≈ 6,600 steps. I ran the course's own f32 recurrence: after 1,000 steps the largest deviation from the straight line is 0.48. After 20,000 steps it is still 0.017. At P = 4, n = 4 (L = 16) it is 3e-4 after 1,000 steps. The browser widget also stops at 2,000 steps, so it cannot show this at defaults either. There is also no hint on *how* to confirm: run.py prints only every 8th cell and asserts against numpy, not against the line.
Why it matters: The learner will do exactly what is asked, see a profile that is clearly not linear, and conclude they broke something.
Concrete fix: Replace item 2 with:
```html
<li>Steady state. With <code>P=4 n=4 STEPS=1000 bash commands.sh</code>, check that the profile approaches the straight line from 1.0 to 0.0. Add <code>print(np.abs(device - (1 - np.arange(1, L+1)/(L+1))).max())</code> to <code>run.py</code>; it should be about 3e-4. <em>Hint:</em> heat spreads about √(2αt) cells in t steps, so a rod of L cells needs roughly L²/(π²α) steps to settle. Predict how many steps the default 128-cell rod needs before you try it (it is several thousand).</li>
```
Also raise the widget's stop condition (`step >= 2000` in the script) to 20000 or add a "run to steady state" button.

### P5 [major] Exercises 1 and 3 have no hints and hide real traps
Location: Exercises, items 1 and 3.
Problem: Exercise 1 (overlap): if the learner updates `u[2..n-1]` in place first, the edge cells' later update reads an already-updated `u[2]` and `u[n-1]`. The numpy assertion then fails, and nothing warns about it. The learner also has to see where the overlap can live: interior compute inside `start_step()` after launching the async ops, edges in `update()`. They also need a way to judge the result: per-step cost should drop toward max(compute, ~88). Exercise 3 (f16) is much more than "switch the builtins". It needs `f16` arrays and DSDs, `@faddh`/`@fmach`, a 16-bit memcpy (`MEMCPY_16BIT`, where each f16 travels in the low half of a 32-bit word, ch03), host arrays in `np.float16`, and a looser `rtol`. The f16 range also matters, since the profile drops to 1e-25.
Why it matters: Brief requirement: exercises need hints. These two are the deepest exercises in the course, and without hints they turn into debugging sessions.
Concrete fix: Replace items 1 and 3 with:
```html
<li>Overlap communication with compute. In <code>start_step()</code>, after launching the four transfers, compute the interior right away. Leave the two edge cells for <code>update()</code>, once <code>pending</code> hits 0. <em>Hints:</em> (1) compute <code>lap</code> for <em>all</em> cells that can be done now before writing any <code>u</code>. If you update <code>u[2..n-1]</code> in place first, the edge cells will read new neighbours and the numpy check will fail. (2) You need new DSDs of length <code>n-2</code> for the interior and of length 1 for each edge. (3) The completion tasks cannot run while <code>start_step()</code> is computing (one task at a time), so the transfers proceed on their microthreads while the CE computes. Predict before you measure: cycles/step should move from 88 + 2.5·n toward max(≈88, 2.5·n) plus a small edge cost.</li>
<li>Half precision. Change <code>u</code>, <code>lap</code> and <code>alpha</code> to <code>f16</code>, and the builtins to <code>@faddh</code>/<code>@fmach</code> (Chapter 6 naming). <em>Hints:</em> memcpy moves 32-bit words, so use <code>MemcpyDataType.MEMCPY_16BIT</code> and pass the host data as <code>np.float16</code> values packed into the low 16 bits of <code>uint32</code> (Chapter 3). Loosen <code>rtol</code> to about 1e-2. Expect tiny values in the profile to flush to zero. Then compare cycles/step on WSE-2 and WSE-3 using the method above. Does the 2.5 cycles/cell slope change, and does the fixed part change?</li>
```

### P6 [minor] "Under one cycle per element" is stated without explaining how
Location: "What the numbers say", first bullet ("2.5 cycles per cell covers three vector instructions, under one cycle per element per instruction").
Problem: Chapter 3 told the learner that WSE-3 SIMD widening is for FP16/BF16. A learner would expect f32 at one element per cycle per instruction, so 3 cycles/cell, and the page offers no mechanism for 0.83. The fixed 88 is also asserted as "the halo exchange" with no breakdown, even though P = 2 gives a usable second data point.
Why it matters: "What happens inside" is the point of a performance section. An unexplained number teaches the learner to accept numbers.
Concrete fix: Change the sentence to: "The 2.5 cycles per cell covers three vector instructions, about 0.83 cycles per element per instruction. That is slightly better than one element per cycle, which suggests the datapath overlaps consecutive instructions or moves more than one f32 per cycle on some operands. We have not isolated which, and Exercise 3 is one way to probe it." Then add to the P = 2 bullet: "At P = 2 the fixed part is 99 − 40 = 59 cycles with two transfers, against 88 with four, so each extra send/receive pair costs roughly 30 cycles. Ops on different microthreads overlap, but their completion tasks still run one at a time on the CE."

### P7 [minor] Why P = 8's end PEs don't make it cheaper is not explained
Location: "P = 2 is cheaper" bullet.
Problem: In P = 8 the two end PEs also do only two transfers, yet the step costs as much as at P = 16. The missing idea is that neighbours are coupled through back-pressure (P2), so the whole row advances at the pace of its slowest PEs, the interior ones. Only when *every* PE is an edge PE (P = 2) does the cost drop.
Concrete fix: Append to that bullet: "With P ≥ 3 the end PEs are also cheaper, but it does not matter. Each PE waits for its neighbours' wavelets, so the row moves at the speed of its interior PEs."

### P8 [minor] Memory limit numbers disagree between prose, widget and slider
Location: src line 96 ("memory allows about 5,000 f32 cells plus the scratch array"), the model widget (`maxN = 46*1024/8 − 2` = 5,886; readout says "of 48 KB" but warns at "~46 KB"), slider `max="5000"`, plot `nmax = 128`.
Problem: The prose says ~5,000, the widget says 5,886, and the slider stops at 5,000, so the warning never shows. The plot's x-axis ends at 128, so the red marker disappears for most of the slider range.
Concrete fix: Prose: "memory allows about 5,800 f32 cells, since <code>u</code> and <code>lap</code> take 8 bytes per cell out of the ~46 KB left for data (Chapter 3)". Widget: set the slider `max="6000"`, change the readout to "of ~46 KB usable", and either make `nmax` follow the slider (log-scale x axis) or print "(off-chart)" when `nn > nmax`.

### P9 [minor] The four-color / parity scheme is only half explained, and the figure doesn't label colors
Location: the figure caption (src line 37) and the `layout.csl` listing.
Problem: The caption says four colors are needed "because neighbours alternate by parity" but not *why*. A router can hold only one route per color. With one eastward color, PE k's router would need that color as both RAMP→EAST (its own send) and WEST→RAMP (receiving from k−1). The subtle line `recv_w = if (even) E1 else E0` ("my west neighbour's send_e") is never stated in prose. The figure's arrows carry no color names. Queues 2–5 (0/1 are memcpy's, ch05) and task IDs 10–13 go unexplained. Chapter 11 points back to Chapter 4 for parity; this chapter does not.
Concrete fix: Replace the caption with: "<b>Ghost cells and halo exchange.</b> Orange arrows travel east, purple arrows west. A router holds one route per color, so a PE cannot use the same color to send east (RAMP→EAST) and to receive from the west (WEST→RAMP). Even PEs therefore send east on E0 and receive on E1, odd PEs the reverse; westward traffic uses W0/W1 the same way (Chapter 4). Queues 0–1 belong to memcpy, so the program uses 2–5 (Chapter 5)." In the diagram script, add a text label `E${k%2}` above each orange arrow and `W${(k+1)%2}` above each purple one.

### P10 [minor] Inconsistent forward reference from Chapter 10, and duplicated hang story
Location: ch10 src line 45 promises "Lab 3 shows how to separate the two by measuring at two problem sizes and subtracting"; ch12 differences by *step count*. The hang callout (src line 49) repeats ch03/ch05 almost word for word without saying so.
Concrete fix: In `src/10-lab-first-programs.html`, change "at two problem sizes" to "at two step counts". In ch12's callout, start with "You met this hang in Chapter 5; here is the code that caused it." Then add one learner action: "Try it: change <code>iq_w</code>/<code>iq_e</code> back to queues 2/3, rerun, and look at the stop cause in <code>sim_stats.json</code> (Chapter 9)."

### P11 [minor] The widget models the math, not the machine, and there are no check-yourself questions
Location: "Watch the rod" widget; the end of the chapter.
Problem: The widget updates a single global array, so nothing in it shows a halo exchange, a ghost copy or the per-PE task flow. That flow is the lab's actual lesson. The "validated" readout at step 50 cannot be compared with the printed `expected_output.txt` (every 8th cell), because the widget does not print those cells. Earlier theory chapters end with `<details>` check-yourself questions; this chapter has none.
Concrete fix: (a) In `draw()`, when P=8, n=16, α=0.25 and step=50, append the every-8th-cell values to `#h-out` so they can be compared directly with the device output. (b) Add a "Check yourself" block:
```html
<h3>Check yourself</h3>
<details><summary>Why can't the four completions share one task that decrements <code>pending</code>?</summary><p>Activation is a single bit. Two completions that land before the task runs give one run, so <code>pending</code> would never reach 0 and the program would hang.</p></details>
<details><summary>PE 3 finishes step 7 before PE 4. What happens to the edge cell PE 3 sends east for step 8?</summary><p>It waits in PE 4's input queue (and, if needed, the routers behind it) until PE 4 issues its step-8 receive. Back-pressure keeps neighbours in lock-step.</p></details>
<details><summary>At n = 16, about how much of each step is communication and synchronisation, and how would you shrink it?</summary><p>About 88/128 ≈ 70%. Give each PE more cells (surface-to-volume), overlap the exchange with the interior update (Exercise 1), or go 2-D.</p></details>
```
