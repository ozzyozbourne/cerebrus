# ch07 · pedagogy review

Summary: The chapter has the right core story. The host link is narrow, memcpy builds a frame of PEs around your program, host commands run one at a time, and a streaming copy can race a later read. The program-02 bug is an excellent worked example. The mental model breaks in a few places, though. "Halo" is promised in the objectives and never defined, and it clashes with the "halo exchange" of ch06 and ch12. The fabric-dims and offsets arithmetic is never explained. Copy mode is never explained well enough to show why it is safe, and streaming mode is never explained well enough to show where its color comes from. The "Lab 3 measures this" claim does not match what Lab 3 measures. Several calls and terms (RPC, `launch`, `nonblock`, `MemcpyOrder`, "context switch") arrive undefined. Two of the three objectives are only partly delivered. The quiz tests recall more than the model.

## Findings

### P1 [major] "Halo" is promised but never defined, and clashes with ch06/ch12
- **Location:** Objectives bullet 1 ("Explain the memcpy 'halo' columns"); the figure's aria-label. The body never uses the word.
- **Problem:** The learner is told they will be able to explain "halo" columns, but the chapter never says what the word means here. In ch06 (DSD preset note) and ch12 ("ghost cells and a halo exchange"), "halo" means stencil ghost cells exchanged between neighbours. Those are two unrelated meanings within six chapters. The SDK's pipeline-03 tutorial uses "artificial halo" in yet a third sense: extra user PEs around a kernel.
- **Why it matters:** A learner arriving at ch12 will wonder whether the halo exchange has something to do with memcpy's columns. One term should mean one thing.
- **Concrete fix:** Rename the concept "memcpy frame" (or "memcpy infrastructure columns"). Replace objective 1 with: "Explain the columns memcpy adds around your rectangle (the *memcpy frame*) and compute the `--fabric-dims`/`--fabric-offsets` your program needs." At first use in the section "What `--memcpy` adds…", add: "We call these the *memcpy frame*. (Do not confuse it with the *halo exchange* of Chapter 12, which is stencil neighbours swapping edge cells.)" Update the aria-label to match.

### P2 [major] The fabric-dims / fabric-offsets arithmetic is never explained
- **Location:** The section "What `--memcpy` adds…" and the figure caption ("a few columns wider … `--fabric-offsets=4,1`"; "7 columns narrower and 2 rows shorter").
- **Problem:** The objective promises "why your rectangle needs `--fabric-offsets`". The chapter shows 3 west and 2 east columns. That adds up to 5, yet the fabric is 7 wider (8 = 1 + 7), and the offset is x = 4, not 3. Column 0, column 7, and rows 0 and 2 are drawn but never explained. The learner cannot get from "3 + 2 columns" to "P + 7, R + 2" or to "4,1". Yet those are exactly the formulas in every `commands.sh` (`--fabric-dims=$((P+7)),3`, `8,$((R+2))`).
- **Why it matters:** This is the one practical rule the chapter exists to teach. Without the arithmetic, the learner will copy `4,1` without knowing why, and will be stuck when they try `--channels 4`.
- **Concrete fix:** Add a short paragraph after the figure: "The rule this course uses: `--fabric-dims = (W + 7), (H + 2)` and `--fabric-offsets = 4,1` for a W × H program. Of the 7 extra columns, 3 west and 2 east are memcpy PEs (measured above); the remaining edge column on each side and the top and bottom rows are the margin the SDK requires around the core [state source, or say 'we have not found which component uses them']. So your (0,0) is fabric (4,1): one margin column plus three memcpy-west columns. Worked example: program 03 with P = 4 compiles with `--fabric-dims=11,3 --fabric-offsets=4,1`." In the SVG, label column 0, column 7 and rows 0 and 2 as "margin" instead of leaving bare coordinates.

### P3 [major] "Lab 3 measures this" is not what Lab 3 shows, and the simulator does not model the 7 Gb/s link
- **Location:** End of "The narrow door" paragraph: "In this course's labs, host transfers dominate total runtime — Lab 3 measures this."
- **Problem:** Lab 3 (ch12) subtracts a 0-step baseline of about 3–7 k cycles from runs of 13–32 k cycles. In most of its configurations the timesteps dominate, not the host transfers. The cycle-level simulator also does not simulate 100 GbE or 200 µs of TCP overhead, so no lab measures the narrow door this section describes.
- **Why it matters:** The learner gets a wrong expectation of what they will see in Lab 3, and blurs the simulator's cycle counts with real-system wall-clock time.
- **Concrete fix:** Replace the sentence with: "The simulator does not model the Ethernet/TCP path, so the labs cannot measure it. In simulation, memcpy still costs cycles on the device: Lab 3 isolates them by running with 0 timesteps (about 3–7 k cycles of setup and transfer) and subtracting that from the total."

### P4 [major] Why copy mode is safe and streaming mode is not: the missing "why"
- **Location:** The "Copy mode vs streaming mode" callouts and the "What actually happened" bug callout.
- **Problem:** The bug explanation says a streaming H2D "completes when the host has *injected* its wavelets". It never says why copy-mode H2D does not race in the same way, so the learner cannot generalise. The claim that copy mode involves no device code "beyond exporting the symbol" also misleads. memcpy's own tasks run on your PE's CE to write the array. That is the very reason ch06 and ch05 warn that the CE must stay free to service memcpy.
- **Why it matters:** The learner needs one rule they can reuse: "a command is complete when memcpy's own code says so; in streaming mode, memcpy's part ends at injection and *your* task finishes the job."
- **Concrete fix:** Change the copy-mode callout to: "…memcpy's own device tasks (running on your PE's CE, on colors 21–23) write or read it. The command does not complete until memcpy has finished on every PE, so the next command always sees the data. Your code only exports the symbol." Add to the streaming callout: "memcpy's job ends when the wavelets are delivered to your color. Processing them is your data task's job, and memcpy cannot know when that is done. Hence the barrier." (If the per-PE completion semantics of copy mode cannot be sourced, tag it Derived.)

### P5 [major] Where the streaming color comes from, and what it costs
- **Location:** Streaming-mode callout ("The host passes a color ID instead of a symbol"); the reserved-resources table.
- **Problem:** The learner is never told how the device and host agree on that color. Program 02 compiles with `--params=MEMCPYH2D_DATA_1_ID:0`, and the device reads `sys_mod.MEMCPYH2D_1`. The SDK (topic-03) says the user must *not* route that color, because memcpy routes it. The table says 21/23 are "H2D/D2H data", so the learner will assume streaming arrives on color 23, when program 02 actually streams on user color 0.
- **Why it matters:** The streaming color is a hidden cost against the "use colors 0–19" budget, and a hidden rule ("do not route it"). A learner who writes their own streaming program will trip on both.
- **Concrete fix:** Add after the callouts: "In streaming mode you pick the color at compile time: program 02 passes `--params=MEMCPYH2D_DATA_1_ID:0`, and the device code gets it as `sys_mod.MEMCPYH2D_1`. memcpy routes that color from the west frame to your PEs, so you must not write a `@set_color_config` for it (SDK topic-03). It comes out of your 0–19 budget. Colors 21 and 23 in the table are memcpy's internal copy-mode channels." Show the two relevant lines of program 02 (the `commands.sh` param and `const h2d_color = @get_color(... sys_mod.MEMCPYH2D_1)`).

### P6 [major] Objective 2 ("choose between copy and streaming mode") has no decision criteria
- **Location:** The "Copy mode vs streaming mode" section.
- **Problem:** The two modes are described but never compared. No criteria are given for choosing streaming.
- **Why it matters:** The learner cannot do what the objective promises.
- **Concrete fix:** Add a three-row table under the callouts. Columns: "Use copy mode when…" / "Use streaming mode when…". Rows:
  1. Data must sit in SRAM before compute starts (most kernels) / each element can be consumed on arrival (reductions, pipelines).
  2. Input fits in the PE's 48 KB / the input is larger than SRAM, or you want to avoid buffering it.
  3. Order of arrival does not matter / you can accept the obligations: a data task or fabric DSD per color, a barrier before reading, and sending streams in the order the device consumes them.

### P7 [major] Undefined host-API vocabulary: RPC, launch, nonblock, order, get_id, cmaddr, load/run
- **Location:** "Six calls on the host" code and the paragraph below it.
- **Problem:** "RPC" is used throughout but never expanded or defined here (ch09 uses it only in passing). `nonblock`, `MemcpyOrder.ROW_MAJOR`, `MemcpyDataType.MEMCPY_32BIT`, `load()` vs `run()`, and "exported symbol IDs" are all unexplained. Every course program passes `nonblock=False`, but the learner never learns what `True` would do, which is directly relevant to the command-stream model. The section heading says "Six calls", but the code makes eight distinct kinds of call (constructor, get_id, load, run, memcpy_h2d, launch, memcpy_d2h, stop).
- **Why it matters:** These are the knobs of the command stream, the chapter's central mechanism.
- **Concrete fix:** Add a compact table after the code. Columns: Call / What it does / Device side.
  - `SdkRuntime(name, cmaddr)`: open the compiled `out/` directory. `cmaddr` is the CS system's address; `None` runs the simulator.
  - `get_id(name)`: look up a name exported in `layout.csl`.
  - `load()` / `run()`: load the ELFs and start the PEs, including memcpy's.
  - `memcpy_h2d/d2h`: one copy command.
  - `launch(fn, args…)`: an RPC (remote procedure call), meaning "run exported device function `fn` on every PE". It returns only after the device calls `unblock_cmd_stream()`.
  - `stop()`: tear down.

  Then add: "`nonblock=True` returns to Python immediately and lets later commands queue up; they still execute one at a time on the device. `order` says how a multi-PE array is flattened (ROW_MAJOR: PE-major blocks, as described below). `MEMCPY_32BIT` moves 32-bit words; 16-bit data is packed [check SDK]." Rename the heading to "The host side in eight lines".

### P8 [minor] The bug explanation omits why the wait_done check is race-free and why "95"
- **Location:** The `wait_done()` snippet in the bug callout.
- **Problem:** The snippet shows only half the handshake; the matching line in `on_value()` (`if (count[0] == N and host_waiting) unblock_cmd_stream()`) is mentioned only in a comment. A strong learner will immediately ask: "What if the last data task runs between the `if` and `host_waiting = true`?" The answer is that tasks run to completion on one CE and never interleave (ch05), but the chapter does not say so. It also presents "95" as if it were meaningful. That number reflects how many wavelets were still queued at that instant, which depends on timing.
- **Why it matters:** This is the best "internal behaviour" moment in the chapter. Closing these two gaps turns a recipe into an understood mechanism.
- **Concrete fix:** Show both functions side by side (the `on_value` tail from `programs/02-wavelet-tasks/pe_program.csl` lines 27–29). Add: "There is no race between the check and the flag: tasks on a PE run to completion one at a time (Chapter 5), so `on_value` cannot run in the middle of `wait_done`. The missing 5 values were wavelets still in the input queue and router buffers when the D2H began. The number depends on timing, not on a hardware constant."

### P9 [minor] The ordering hang is quoted but not explained
- **Location:** "Ordering matters too".
- **Problem:** The gemv-09 quote says the program "would hang", but the chapter never says why. The mechanism is back-pressure (ch05) plus serialization. The device is waiting for x, so b's wavelets are not consumed. The b stream backs up and never completes, and because commands are serialized, the x command is never issued. That is a deadlock.
- **Why it matters:** It is a direct, satisfying application of ch05's back-pressure model, and the chapter leaves it unused.
- **Concrete fix:** After the quote, add: "Why: the device's tasks are waiting for x, so b's wavelets are not consumed. They fill the input queue and back up the fabric (Chapter 5's back-pressure). The b command never completes, and because commands are serialized, the x command is never sent. Each side waits for the other."

### P10 [minor] Link-rate stats are not reconciled, and the 200 µs overhead gets no worked example
- **Location:** The stat row and the paragraph in "The narrow door".
- **Problem:** "100 GbE" sits beside "~7 Gb/s × ≤16 = 112 Gb/s", and the learner is not told how these relate. Does 16 channels saturate the link? The 200 µs TCP overhead is stated but never applied. For this course's tiny transfers (64 f32 = 256 B), overhead dominates completely: about 1 MB/s effective. The stat also lacks a provenance tag, and the "≤ 16" stat has no tag either.
- **Why it matters:** The learner should leave with two regimes in mind: bulk transfers are bandwidth-bound, small ones are latency-bound. That is the actual reason to batch host calls.
- **Concrete fix:** Add a sentence: "Sixteen channels at about 7 Gb/s (112 Gb/s) roughly fill one 100 GbE link. For small transfers the 200 µs overhead dominates: copying program 01's 256 bytes costs about 200 µs, an effective 1.3 MB/s [Derived]. Batch data into few large copies." Add an SDK tag to the "≤ 16" and "~200 µs" stats.

### P11 [minor] Reserved-resource table: unexplained terms ("context switch", teardown, NOP, H2D/D2H)
- **Location:** The reserved-resources table.
- **Problem:** "Context switch" (color 20), "teardown" (task 29) and "NOP" (31) are never explained. "H2D/D2H" are first used in the section before, without expansion. "Demultiplexing" and "multiplexing" in the frame paragraph are not tied to anything concrete.
- **Why it matters:** These are minor, but they read as noise to someone new to Cerebras.
- **Concrete fix:** Expand H2D/D2H at first use: "host-to-device (H2D) and device-to-host (D2H)". Add a footnote row: "Context switch, teardown and NOP are internal memcpy mechanisms; you only need to avoid their IDs." In the frame paragraph, write: "west columns split one host stream into per-row streams (demultiplex); east columns merge per-row results into one stream back to the host (multiplex)".

### P12 [minor] Check-yourself Q2 tests a coincidence; quiz misses the key models
- **Location:** The quiz.
- **Problem:** Q2 asks why programs use "colors ≤ 4". Nothing requires ≤ 4; the real constraint is 0–19, and ch04 says the labs use 0, 2 and 4 colors (counts, not maximum IDs). The answer also says "memcpy owns queues 0–1 on WSE-3" without noting that on WSE-2 only queue 0 is reserved. Q3 duplicates the lede. No question tests the frame arithmetic (P2), the copy/streaming choice (P6), or the ordering deadlock (P9).
- **Why it matters:** The quiz should check the mental model the objectives promise.
- **Concrete fix:** Replace Q2 with: "Your program 03 variant has P = 10 PEs in one row. What `--fabric-dims` and `--fabric-offsets` do you pass, and why?" Answer: "`17,3` and `4,1`. That is 7 extra columns (3 memcpy-west, 2 memcpy-east, plus a margin column each side) and 2 extra rows; your (0,0) sits after one margin column and three west columns." Replace Q3 with: "You stream b, then x, but the device consumes x first. What happens and why?" Answer: "Deadlock. b's wavelets are not consumed, back-pressure keeps the b command from completing, and serialization means x is never sent." Optionally add: "Why does a copy-mode `memcpy_h2d` followed by `launch` never race?" Answer: "The copy command completes only after memcpy's own tasks have written the array on every PE."

### P13 [minor] Q1 answer slightly misstates the hazard
- **Location:** Quiz Q1 answer.
- **Problem:** "Otherwise the host could issue a D2H copy before the data has moved." True, but the more general point is that the *next command of any kind* proceeds. That could be another `launch` that reuses the same output queue or microthread while the send is still in flight, which is the ch05 microthread trap.
- **Why it matters:** It ties the chapter back to ch05 and generalises the rule.
- **Concrete fix:** Change the answer to: "In the completion task the send activates (as in programs 03–05). Unblocking at the end of the RPC would let the next command run, whether a D2H copy or another `launch` reusing the same queue, while the send is still in flight."
