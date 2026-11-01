# ch10 · depth review

Summary: The lab runs two correct programs but stays close to the surface. Its one "what happens inside" paragraph guesses at the cost split, and the guess is wrong. In program 01 the `@fmacs` takes about 130 cycles, not "tens". The D2H copy takes about 4,400 of the 7,740 cycles (≈60 cycles per element), and the two H2D copies about 1,350 cycles each. I measured this with the simulator's text instruction trace (`SINGULARITYENV_SIMFABRIC_DEBUG=inst_trace`). No chapter of the course mentions that trace, yet it shows each task ID cycle by cycle. With it, plus the `<time>` timestamp counter (SDK topic-02, bandwidth-test), I collected real numbers for cycles vs N, f32 vs f16 and WSE-2 vs WSE-3, a measured task schedule for program 02, and a faster fabric-DSD variant of program 02. All numbers below are from SDK 2.10.1 runs in `/home/user/cerebras-sdk/tmp/rev-ch10-depth/`. The pedagogy review (ch10-pedagogy.md) already covers exercise answers and troubleshooting. This review does not repeat them, except where depth adds something.

## Gaps and additions (prioritised)

### D1 [critical] "What happens inside" is a guess. Replace it with the measured timeline of program 01
What is missing: The chapter says "Almost all of it is host I/O … The @fmacs itself processes 64 elements in on the order of tens of cycles". It gives no breakdown, does not say which transfer dominates, and does not explain how the host's scalar argument reaches `saxpy(a)`.
Why it matters: This chapter is the course's first look inside a run. Learners will later reason about cost from the claim that I/O dominates, so they need to see what each phase costs. They also need to see that D2H is far slower than H2D.
Measured evidence (WSE-3, N=64, PE at fabric (4,1), instruction trace, task IDs from the trace's `Tnn` column):

| cycles | task on the PE | what it is |
|---|---|---|
| 112–937 | T01 (cmd queue IQ1, color 22) | H2D(x) command: 15 parameter pushes (`SYS_CMD_PUSH` → `stack_push`), about 51 cycles apart |
| 1014–1124 | T01 | decode, set the counter filter, block, `OQFLUSH` |
| 1128–1469 | T29 (teardown) | 64 values land via color 23 → IQ0 → SRAM (`FMOV16` pairs), then `ACTVT` |
| 1470 | T27 (`SYS_UBLK_C22`) | `UBLK`: command stream released, H2D(x) "done" |
| 1489–2780 | same pattern | H2D(y) |
| 2796–3086 | T01 | RPC: 6 pushes (wavelet count, `a` as two u16, function ID 3 from `out/bin/out_rpc.json`), then `f_rpc` executes `BLK` on the command task |
| 3120–3250 | T01 | `FMACS` with 64 elements: 2 cycles per element |
| 3247 | T01 | `UBLK` = your `unblock_cmd_stream()` |
| 3265–3776 | T01/T29 | D2H command decode, switch setup |
| 3777–7645 | T21 ↔ T30 ×64 | D2H: per element, one data send (T21, 35 cyc) and one control wavelet that advances the switch (T30, 21 cyc), ≈60 cycles/element |
| 7687–7689 | T28 (`SYS_EXIT`) | final `UBLK` |
| 7690–7740 | – | the simulator's 50-cycle idle window before it stops |

Totals: H2D ≈ 1,360 cycles each (≈21/element, mostly fixed command cost), RPC ≈ 450 (of which FMACS 130), D2H ≈ 4,400 (57%). Sources for the mechanism: `csl-libs/memcpy/wse3/memcpy.csl` (comment "step 1: RXCOMMAND(=C22) broadcasts memcpyH2D … step 2: decodes (px, py, w, h, addr) and sets up a counter filter … " and the RPC protocol: "# of wvlts | param 1 … | ID of the function"), `wse3/sys.csl` (`f_push`, a 32-entry u16 stack, `block_cmd_stream() = @block(task_id_cmd)`), `wse3/memcpyd2h.csl` ("Each PE sends out x, then triggers a switch advance command"), `memcpy/sys_params.csl` (task IDs 27/28/29/30, control tasks 33–37).
Proposed addition: Replace the two "What happens inside" paragraphs with this table, or with a horizontal timeline bar coloured by task (H2D x | H2D y | RPC/FMACS | D2H | idle), tagged Measured. Then add three sentences:
1. "Blocked" is literal. `f_rpc` executes `@block` on the task bound to the command queue, so later command wavelets wait in input queue 1 until your `@unblock`.
2. The scalar `a` travels as two 16-bit control-wavelet pushes onto memcpy's stack, and `rpc_server` dispatches on the function ID listed in `out_rpc.json`.
3. D2H in copy mode sends one element at a time and a control wavelet after each one (memcpy uses this to take turns among the PEs of a row), so D2H costs ~60 cycles per element against ~3 for H2D data.
Fix the existing sequence diagram to match: `memcpy_d2h` should be the longest arrow, and the RPC row should show the `BLK`/`UBLK` pair.

### D2 [critical] Teach the instruction trace: the one tool that shows "what happens internally"
What is missing: No chapter mentions that the simulator can write a readable per-cycle instruction trace. Ch09 lists `sim.log`, `sim_stats.json`, csdb and `<simprint>`. `sdk_debug_shell instr-trace` refuses to read the default CTF trace ("does not support ctf trace debug, please use csdb"), and csdb only has commands to select a trace, so a learner has no obvious way in.
Why it matters: The chapter's stated angle is behaviour inside the run. This trace shows tasks, `BLK`/`UBLK`, DSD ops element by element (`Seq: 0..63`) and every memcpy phase. It is how every number in D1 and D5 was produced.
Measured evidence: `SINGULARITYENV_SIMFABRIC_DEBUG=inst_trace cs_python run.py --name out` writes about 107k lines to `sim.log` for program 01. Line format: `@3124 P4.1: … [EX OP] | 0x013a: T01  FMACS  Dest:3f24aefe Src0:… Src2:40200000`. Here `P4.1` is the fabric coordinate of your PE (offset 4,1), `T01` is the task ID, and the operands are hex values (0x40200000 = 2.5). In my runs the trace did not change cycle counts beyond normal run-to-run noise (program 02: 7,236 with trace vs 7,020–7,037 without).
Proposed addition: A short "Look inside: the instruction trace" section with the command, a five-line excerpt (FMACS issue, first and last `Seq`, UBLK), and a 20-line Python helper that groups consecutive `[EX OP]` lines by task. I used `/home/user/cerebras-sdk/tmp/rev-ch10-depth/tools/tasks.py`; ship it as `course/tools/trace_tasks.py`, or inline it. Add a legend for the task IDs a learner will see: T01 command queue, T02 your data task (WSE-3 IQ2), T21/T30 D2H data/ctrl, T27 H2D unblock, T28 SYS_EXIT, T29 teardown. Exercise: "Find the cycle at which your `@fmacs` starts and ends. How many cycles per element?"

### D3 [major] Add a measured cycles-vs-N table for program 01 (WSE-3 and WSE-2)
What is missing: Exercise 1 asks the learner to try N=4096, and the text says Lab 3 will "separate the two by measuring at two problem sizes". No data is given, and the slope is never interpreted.
Why it matters: Fitting a line to cycles vs N is the basic method behind Lab 3. Doing it here, on one PE, shows that host I/O is linear in N and gives the cost per element.
Measured evidence (unmodified program 01, `sim_stats.json` cycle_count):

| N | WSE-3 | WSE-2 |
|---|---|---|
| 16 | 4,669 | 4,008 |
| 64 | 7,740 | 6,826 |
| 256 | 20,018 | 18,364 |
| 1024 | 69,307 | 64,107 |
| 4096 | 266,295 | 245,355 |

Fit: WSE-3 ≈ 3,640 + 64.1·N, WSE-2 ≈ 3,060 + 59.0·N. That is ≈64 cycles per element for three transfers of one element each, which matches D1's ~3 + ~3 + ~60 split, against 2 cycles per element of compute. Compute is about 3% of the run at any N.
Proposed addition: A table plus a small log-log or linear plot widget (5 points, two series), and the sentence: "The slope is the cost of moving one element in, in, and out; the compute is 2 of those 64 cycles." Use this as the answer to exercise 1. Link forward to Lab 3's subtraction method.

### D4 [major] Measure the kernel itself with the timestamp counter: f32 vs f16, WSE-2 vs WSE-3
What is missing: The lab never measures device compute directly. The course states SIMD widths (4-wide f16 on WSE-2, 8-wide on WSE-3, ch01–03), but no lab checks them. The only f16 content is the exercise that ch10-pedagogy P5 found to be wrong.
Why it matters: Learners can then check a vendor claim with their own measurement. They also learn the standard SDK timing idiom (`<time>`: `enable_tsc`, `get_timestamp` into `[3]u16`, a 48-bit counter). The SDK bandwidth-test README explains why kernel-side timing beats host timing: "the runtime may not send the command right after the user issues it".
Measured evidence (variant at `/home/user/cerebras-sdk/tmp/rev-ch10-depth/saxpy-tsc/`, timestamps taken around the single DSD op inside the RPC; the back-to-back timestamp overhead of 10 cycles is subtracted; f16 data sent with `MEMCPY_16BIT` + `input_array_to_u32` + `memcpy_view`):

| N | f32 `@fmacs` WSE-3 | f32 WSE-2 | f16 `@fmach` WSE-3 | f16 WSE-2 |
|---|---|---|---|---|
| 64 | 133 | 68 | 22 | 36 |
| 256 | 517 | 516 | 70 | 132 |
| 1024 | 2,053 | 2,052 | 262 | 516 |
| 4096 | 8,197 | 8,196 | 1,030 | 2,052 |
| 8192 | – | – | 2,054 | 4,100 |

Asymptotes: f32 = 2.0 cycles per element on both chips. f16 = 0.5 cycles per element on WSE-2 (2 elements per cycle) and 0.25 on WSE-3 (4 elements per cycle). So WSE-3 doubles f16 throughput and leaves f32 unchanged, which agrees with "FP16 SIMD doubled" (wse_hardware.md §1). For this in-place y = y + a·x op, the measured f16 rate is half the quoted SIMD width (4 per cycle, not 8). Tag that Measured and do not present it as the hardware peak; an in-place op reads two operands and writes one per element. Odd point: f32 at N=64 on WSE-2 takes 68 cycles against 133 on WSE-3, repeatable. I cannot explain it; leave it out or mark it as an observation.
Proposed addition: A "Measure the kernel" subsection with the 10-line TSC pattern (from topic-02: `tsc.enable_tsc(); tsc.get_timestamp(&t0); … ; tsc.get_timestamp(&t1);`, export as `[*]u16`, read 3 words with `MEMCPY_16BIT`, `make_u48`). Add the table (or a bar chart: cycles per element by dtype × arch) and an exercise: "Predict f16 cycles at N=2048 on WSE-3, then measure." Replace the broken f16-streaming exercise with this copy-mode f16 experiment, or keep P5's corrected packing version as a stretch.

### D5 [major] Program 02: show the measured task schedule and the memcpy relay path behind the race
What is missing: The bug callout gives the symptom (the sum after 95 values) but not where those values are inside the device, or how long each task runs.
Why it matters: The lesson "H2D completes when wavelets are injected, not consumed" is only convincing with numbers: how far ahead the host gets, and why.
Measured evidence (WSE-3, N=100, trace):
- Path: host → color 23 → IQ0 → memcpy microthread (`fabin` → `fabout`) → OQ0 → your color 0 → IQ2 → data task T02. From `wse3/memcpyh2d.csl`: "streaming mode: C23 (fabin) --> streaming H2D_x (fabout)". Your values make two queue hops inside one PE, and wavelets wait in those queues and in the router.
- `on_value` runs back to back from cycle 1,329, at a median of 40 cycles per wavelet (min 36). Its body has about 20 instructions; the rest is task entry and exit.
- Cycle 4,709: memcpy's `UBLK` marks the streaming H2D as complete. Only **84 of 100** tasks have run at that point; 16 values are still in queues.
- Cycles ~4,985–5,030: the `wait_done` RPC arrives and blocks the stream with 89 done. The 100th `on_value` starts at 5,419 and executes `UBLK` at 5,460.
- Without the barrier, the D2H's own command setup (~250 cycles, D1) lets about 6 more tasks run before `stats` is read. That is why the host saw N−5 at every N (pedagogy P7).
Proposed addition: Add a second sequence or timeline diagram with these cycle stamps (the pedagogy review P4 asks for the diagram; this gives it real numbers). Add one sentence on why the data task is ~40 cycles while memcpy delivers faster: the backlog builds because the CE does one task at a time.

### D6 [major] Add a program-02 variant that receives with a fabric DSD instead of one task per wavelet
What is missing: The lab shows only wavelet-triggered tasks. SDK pipeline-01 ("fabric input DSDs … receive a tensor comprised of multiple wavelets using one instruction") and gemv-09 show the other half of the dataflow style, which Labs 2–3 rely on.
Why it matters: It quantifies the cost of a task per wavelet. It also teaches `fabin_dsd`, async ops with `.activate`, and how long tasks hold up memcpy.
Measured evidence (variant at `/home/user/cerebras-sdk/tmp/rev-ch10-depth/02b-fabin/`, WSE-3): a local task activated at boot runs `@fmovs(buf_dsd, in_dsd, .{ .async = true, .activate = done_id })` with `in_dsd = fabin_dsd{extent=N, input_queue=IQ2}`. Then `done()` computes the stats in a scalar loop and unblocks as in the original. All 100 values are in SRAM by cycle ~1,500 (≈1.7 cycles per wavelet). The task-per-wavelet version finishes receiving at 5,419. Totals: N=100 6,289 vs 7,020; N=500 19,148 vs 24,960; N=2000 67,317 vs 85,290. Second lesson from the trace: the scalar `done()` loop (≈30 cycles per element) ran 1,533–4,556, and memcpy's H2D-complete `UBLK` (T27) could not run until it finished at 4,557. A long task delays the command stream because tasks run to completion. Faster still: compute the sum with DSD ops (`@fadds` over the buffer).
Caveat: my WSE-2 port of this variant compiled with a note ("on 'wse2', 'color' must be specified on the input queue") and then stalled; it needs work before it is published. Use topic-03 / pipeline-01's WSE-2 branches as the model.
Proposed addition: Present it as a "Variant 02b" box: the 15 changed lines, the three-row comparison table, and the questions "Why can't 02b process values as they arrive?" and "What would you change to overlap receive and compute?" (answer: a FIFO, pipeline-02 / topic-09, which points ahead).

### D7 [major] Warn that sim_stats cycle totals depend on host load; prefer TSC for measurements
What is missing: Ch09 says "cycle totals varied by at most 2 cycles across our reruns". On a busy machine that is not true.
Why it matters: Learners who follow D3/D4 on a laptop doing other work, or who run `run_all.sh` in parallel, will see numbers that disagree with the page and blame their code.
Measured evidence: with 3 runs in parallel, plus other users' simulations on the host, the unchanged program 01 gave 7,850 (vs 7,740), 20,363 (vs 20,018) and 70,908 (vs 69,307). The TSC variant at N=16 reported totals of 41,561 and 32,624, against 9,295 on WSE-2. Five of 32 parallel runs aborted with `the received length (0 bytes) is not expected …, could be a kernel stall`, a stall error from correct programs. In-kernel TSC deltas did not change (46 / 47 cycles across all runs). The simulator keeps counting cycles while it waits for slow host commands.
Proposed addition: A callout next to the measurements: "`cycle_count` includes time the device spent waiting for the host. Run one simulation at a time when you compare totals, and time device code with `<time>` (D4). A 'could be a kernel stall' abort on a heavily loaded machine can be a host-side timeout, not a bug; rerun alone before debugging." Also qualify ch09's ±2-cycle claim ("on an otherwise idle machine").

### D8 [minor] Compare WSE-2 and WSE-3 for both programs, and convert cycles to time
What is missing: Objectives say both chips were validated, but only WSE-3 numbers appear (ch09 mentions WSE-2's 6,825 once).
Measured evidence: program 01, N=64: WSE-3 7,740, WSE-2 6,826. Program 02, N=100: WSE-3 7,037, WSE-2 5,533. Per D3, the difference is mostly memcpy's fixed cost (≈3,640 vs ≈3,060) and per-element I/O (64 vs 59), not compute (f32 is identical). The SDK's bandwidth-test converts with `time = cycles / 0.85 … µs`, i.e. an assumed 850 MHz. So 7,740 cycles ≈ 9.1 µs of device time, while the host script takes ~13 s of wall time in the simulator.
Proposed addition: A two-row arch table and one sentence: "WSE-3 is not faster here: these runs are memcpy-bound and f32-bound; the WSE-3 gains are in f16 (D4)." Add the 850 MHz conversion with the SDK provenance tag. Ch12 already uses it.

### D9 [minor] Explain the memcpy call arguments and artefacts the learner can inspect
What is missing: `MemcpyOrder`, `MEMCPY_32BIT`/`16BIT`, `nonblock`, and the meaning of `(0, 0, 1, 1, N)` are pasted, not explained. `out/bin/out_rpc.json` is never opened.
Source: gemv-03 README, topic-02 run.py (16-bit copies fill only the low half of each u32; the host reads them with `memcpy_view`), and `out_rpc.json` for program 01 (`saxpy` is id 3 with input `a: f32`; `x`, `y` are ids 1, 2 with `immutable: 0`).
Proposed addition: A 5-row "memcpy arguments" table, plus a `cat out/bin/out_rpc.json` excerpt tied to D1's "function ID" push. Say that ROW_MAJOR vs COL_MAJOR only matters for rectangles larger than 1×1 (Lab 2).

### D10 [minor] Queue capacity and back-pressure experiment
What is missing: The chapter never says what limits how far the host can run ahead of the device.
Source: SDK pipeline-01 README: "The hardware has some internal queues to hold the data for I/O … The program stalls when size exceeds 14". Measured: 16 values were still queued when the streaming H2D completed (D5).
Proposed addition: An exercise: add a delay loop (e.g. 200 iterations) to `on_value` and observe in the trace that H2D completion moves later, because memcpy cannot inject once the queues are full. The question "Is the number still in flight at H2D completion the same?" leads to back-pressure, which Lab 2 needs.

### D11 [minor] Small SDK-parallel variants missing from program 01
What is missing: The gemv-01/02/03 tutorials, which this lab parallels, cover strided `tensor_access` DSDs, `@increment_dsd_offset`, and device-side initialisation (gemv-01 `init_and_compute`). The lab uses only a contiguous 1-D DSD.
Proposed addition (an exercise each, all single-PE): (a) `y[0::2] += a·x[0::2]` with `tensor_access = |i|{N/2} -> y[2*i]`; time it with D4 and see that a strided walk costs the same per element. (b) An RPC with two scalars, `fn(f32, f32)void` (`axpby`); find the extra pushes in the trace. (c) A 4×6 GEMV on one PE following gemv-02, as a bridge to Lab 2.

## Out of scope for this chapter (new-chapter or cross-chapter ideas)
- **ch07 (host I/O):** use D1's measured per-phase costs and the D2H mechanism (one element at a time, a control wavelet advancing a switch along the row, from `memcpyd2h.csl`) to explain why D2H is ~20× slower per element than H2D on one PE. Point to the SDK `benchmarks/bandwidth-test` (TSC-based, `--channels` up to 16) for real bandwidth figures. Ch07's "the host hangs" should also say what the simulator actually does (pedagogy P6) and mention the load-induced stall false positive (D7).
- **ch09 (toolchain):** add the instruction trace (`SINGULARITYENV_SIMFABRIC_DEBUG=inst_trace`) to the debugging-tools table, explain that `sdk_debug_shell instr-trace` does not read the default CTF traces, and qualify the "±2 cycles" claim (D7).
- **ch03 / ch01 (PE and SIMD):** cite D4's measured f16 vs f32 throughput (WSE-2 2/cycle, WSE-3 4/cycle for `@fmach`; f32 0.5/cycle on both) next to the vendor SIMD-width claims. That replaces the "no source for fp32 width" gap in wse_hardware.md §3 with a measured number for this op.
- **ch05 (tasks):** use D5's ~40-cycle cost per data task and D6's "long task delays memcpy" trace as concrete evidence for run-to-completion scheduling.
- **ch11/ch12 labs:** reuse the trace-task helper and the TSC idiom, so Lab 3's subtraction method can be checked against direct kernel timing.
- **Possible new appendix, "Measuring on the simulator":** sim_stats vs TSC vs instruction trace, what each includes, the 50-cycle idle tail, host-load sensitivity, and cycles → µs at the SDK's 850 MHz assumption.

Experiment sources for implementers: `/home/user/cerebras-sdk/tmp/rev-ch10-depth/saxpy-tsc/` (TSC + f16 variant), `/home/user/cerebras-sdk/tmp/rev-ch10-depth/02b-fabin/` (fabric-DSD variant, WSE-3 only), `/home/user/cerebras-sdk/tmp/rev-ch10-depth/tools/tasks.py` (trace grouper). They are kept after cleanup; bulky run outputs are removed.
