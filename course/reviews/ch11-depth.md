# ch11 · depth review

Summary: The chapter gets the two collective shapes right, but it describes their internal behaviour only through a toy model, and it never measures the kernel. Its only numbers are whole-run simulator totals, and I measured that host I/O makes up about 98% of them. The kernel-only measurements below come from instrumenting copies of programs 03 and 05 with the `<time>` TSC module. Program 03's reduction takes about **M + 7.2·(P−1) + 18 cycles** on WSE-3 (101 cycles at P = 8, M = 32, against 4,748 total). That puts the widget's per-hop constant (2) off by about 3.5×, and the 866-cycle growth the chapter gives for P = 2 → 16 is mostly host copies (the kernel grows by 100 cycles). Back-pressure can be measured cleanly: each stalled hop holds about 16 wavelets. Program 05's kernel time hides a big effect. When only the root gets an H2D, its command stream runs about 375 cycles behind the receivers', and the receivers sit idle for that long. The chapter has no 2-D variant and does not mention `<collectives_2d>`. That library's `reduce_fadds` gives the same sum about 8× slower at M = 32, and it has a 1-D gotcha that blocks compilation.

All numbers are from SDK 2.10.1 simulator runs of instrumented copies, with sources kept in `/home/user/cerebras-sdk/tmp/rev-ch11-depth/{rr,cba,col}` and `sweep.sh`. Kernel spans come from TSC and are bit-identical across repeat runs. Whole-run `cycle_count` varies by about ±40 between identical runs (12,817 / 12,831 / 12,852 for P = 8, M = 128).

## Gaps and additions (prioritised)

### D1 [critical] No kernel-only measurement; the chapter's table measures host I/O, not the reduction
**What is missing.** The only numbers are `sim_stats.json` totals (4,394 / 4,496 / 4,748 / 5,260 cycles for P = 2/4/8/16; 3,025 → 11,463 for M = 8 → 128). The text calls them "end-to-end, not kernel times", but it never shows the kernel time. It also says the P growth is "only 866 cycles … and part of that is the extra host copies". In fact almost all of the 866 is host copies.
**Why it matters.** The chapter's main claim is about the wavefront (≈ M + c·P). Its evidence is a number that is about 98% memcpy, so the learner cannot check the claim. Separating kernel time from I/O is also the main measurement skill for every later lab (ch12 stencil, ch15 comparisons).
**Measured evidence** (WSE-3, program 03 + TSC: `tsc.enable_tsc()` in a preceding `f_init` launch, `get_timestamp` at entry to `reduce()` and in `exit_task`, 6 u16 per PE read with `MEMCPY_16BIT`). The table shows the end time of each PE, measured from its own `reduce()` start:

| P | M | PE ends (cycles) | kernel span | total sim cycles |
|---|---|---|---|---|
| 2 | 32 | 50, 58 | 58 | 5,805 |
| 4 | 32 | 50, 58, 65, 73 | 73 | 5,950 |
| 8 | 32 | 50, 58, 65, 73, 80, 87, 94, 101 | **101** | 6,103 (4,748 uninstrumented) |
| 16 | 32 | … 158 | 158 | 6,691 |
| 32 | 32 | … 273 | 273 | 8,773 |
| 8 | 8 | 21, 34, 41 … 77 | 77 | 5,121 |
| 8 | 128 | 146, 156 … 199 | 199 | 12,828 |
| 8 | 512 | 535, 546 … 588 | 588 | 39,389 |

Fit: span ≈ 1.01·M + 7.2·(P−1) + ~18 cycles. Going from P = 2 to 16 adds 100 kernel cycles but 886 total cycles. Going from M = 8 to 512 adds 511 kernel cycles (1 per element) but about 34,000 total cycles (about 68 per element, all memcpy). Even at P = 32, M = 512 the kernel is under 2% of the run. Total cycles are also noisy (±40 run to run), while TSC spans repeat exactly.
**Proposed addition.** Add a section "Measuring the kernel, not the host" after the program 03 output:
1. Show a 10-line diff to `pe_program.csl`: `const tsc = @import_module("<time>")`, a `ts: [6]u16` export, a `f_init` RPC that calls `tsc.enable_tsc()`, a timestamp at `reduce()` entry and in `exit_task`. Show the matching `run.py` lines: `memcpy_d2h(..., MEMCPY_16BIT)`, mask `& 0xffff`, then `make_u48` (copied from topic-02's run.py). The SDK pattern is in `tutorials/topic-02-libraries` and `benchmarks/single-tile-matvec`.
2. Replace or extend the existing table with a two-row table (kernel span vs total) for P = 2/4/8/16/32. Tag kernel numbers `measured` and the fit `derived`.
3. Add one sentence: "the simulator's total includes the memcpy frame and host link, and wobbles by about ±40 cycles between identical runs. TSC spans do not."
4. Optional: add a "kernel share" bar (101 of 6,103 cycles).

### D2 [critical] The wavefront model's per-hop constant is wrong, and the widget teaches it
**What is missing.** The text says "about M + P steps". The widget uses `p*2 + i` ("~2-cycle hop+ramp"). The measured per-PE increment for a fabric→CE→fabric `@fadds` hop is **7.2 cycles on WSE-3** and **5.0 cycles on WSE-2** (WSE-2 P = 8: 51, 54, 59 … 84; P = 32 span 204; M = 512 span 564). The first PE's completion is not a wavefront point either. PE 0 finishes when its last wavelet enters its output queue (50 cycles at M = 32, ≈ M + 18), and for small M it finishes early: at M = 8, PE 0 ends at 21 but PE 1 at 34.
**Why it matters.** The widget is the chapter's main internal-behaviour visual. A constant that is 3.5× off changes the crossover the learner would reason about. With c ≈ 7, the P term is as big as the M term once M ≈ 7P: about 40 PEs at M = 256, or a 750-PE row at M = 5,000. That decides when a tree or 2-D decomposition beats a linear chain.
**Measured evidence.** See D1's table. WSE-3: (273 − 58)/30 = 7.17 cycles per PE. M slope: (588 − 77)/504 = 1.01 cycles per element. WSE-2: 5.0 cycles per PE, M slope 0.99.
**Proposed addition.** Change the text to "about M + c·P cycles, where c ≈ 7 on WSE-3 and ≈ 5 on WSE-2: one router hop plus ramp up, the CE's `@fadds` pipeline, and ramp down, measured with TSC". Change the widget's `tp = p*2 + i` to `tp = p*c + i`, with c chosen by an arch selector (7 / 5), and print "measured, SDK 2.10.1 sim" in `#w-out`. This also fixes the M + P vs M + 2P mismatch flagged in pedagogy P10. Add a line: "throughput is one wavelet per cycle per link; the hop constant only shifts the wavefront".

### D3 [major] Back-pressure is asserted, never shown or quantified
**What is missing.** Neither the chapter nor the pedagogy fix (P1) shows what happens when a downstream PE is late, or how much the fabric buffers.
**Why it matters.** Back-pressure is the internal mechanism that makes this dataflow safe without a barrier, and it is the hidden cost of an imbalanced pipeline. The learner should see that a late consumer freezes the whole chain, and that the chain absorbs a bounded number of wavelets.
**Measured evidence.** I delayed only the last PE with a busy loop of mem→mem `@fmovs` before its `@fadds` (`DELAY` param, P = 8 unless noted):
- M = 128, delay ≈ 37 cycles (D = 1): no change at all. The last PE would have idled anyway: its first wavelet arrives about 7·7 = 50 cycles in. A late start is free up to the wavefront arrival time.
- M = 128, delay ≈ 590 cycles (D = 16): PE 0 still ends at 146, because the 7 hops hold all 128 wavelets. PEs 1–7 end at 644, 660, 676 … 737, 16 cycles apart.
- M = 512, delay ≈ 5,500 cycles (D = 40): ends 5,940, 5,956, 5,972, 5,988, 6,004, 6,020, 6,036, 6,049. When the stalled chain drains at one wavelet per cycle, adjacent PEs finish 16 cycles apart (13 for the last hop). So **each hop holds about 16 wavelets**: output queue + router + input queue. This agrees with ch05's "queue stalls past 14" quote from pipeline-01. P = 2, M = 128, D = 4: PE 0's end moves from 146 to 285 (it is fully stalled); P = 2/3/4, M = 512 all end at 6,049.
**Proposed addition.** Add a subsection "When a PE is late: back-pressure, measured" with a small line chart of PE index against end cycle, two series (no delay; last PE delayed), using the D = 40 numbers. Add the rule of thumb: "a chain of P PEs buffers ≈ 16·(P−1) wavelets; if M is less than that, upstream PEs finish even when the consumer is stalled. Otherwise everyone waits for the slowest PE." Optional widget toggle: "delay last PE by N cycles", modelling a 16-wavelet capacity per hop.

### D4 [major] Program 05's timing hides command-stream skew from asymmetric host copies
**What is missing.** The chapter says "one send, R receivers" but does not say how long the broadcast takes. It also misses a trap in program 05 itself.
**Why it matters.** This is an important lesson about how the memcpy command stream interacts with kernels. "Kernel time" on a receiver can be dominated by another PE's host I/O, and naive per-PE TSC readings mislead.
**Measured evidence** (WSE-3, TSC from each PE's `go()` to its receive-complete task):
- As written (x copied to the root only): the root finishes sending in 50 cycles, but receivers report **420–437 cycles** (R = 2/6), 933 at M = 256, and **1,280–1,289 at C = 16 columns**. The receivers' command streams skip the x H2D, so they reach `go()` about 375 cycles before the root (more with more columns or larger M) and sit idle.
- With `x` also copied to every PE (`memcpy_h2d(xs, np.tile(X, R), 0, 0, C, R, M)`), so every PE runs the same command sequence: receivers finish at 57–67 cycles (R = 6–16), the last row of 16 at 94, M = 256 at about 281, and 16 columns × 6 rows at 57. That is **≈ M + 2–3 cycles per row**: the multicast hop costs about 2–3 cycles, against 7 for a CE hop in program 03. WSE-2, R = 16: 51 … 70.
- The TSC resets at `enable_tsc()`, so raw starts are equal on every PE (222 and 123 cycles after `f_init`). Cross-PE comparison is only valid if the commands arrive with equal skew. This is why `benchmarks/bandwidth-test` adds a `sync()` and a reference clock ("the tsc counters of all PEs are not synchronized").
**Proposed addition.** Add a box "Timing the broadcast, and a trap" after program 05: give the two measurements, explain that memcpy commands are queued per PE, and say "if you time a kernel, make every PE's command history identical, or synchronise clocks over the fabric (bandwidth-test's sync/pe.csl)". Compare multicast at about 2–3 cycles/hop with program 03's 7: the router copies without involving the CE. Optionally change program 05 itself to put x on the root only, but time it with a fabric-start (see the D1 instrumentation).

### D5 [major] `<collectives_2d>` is not mentioned; it is the SDK's packaged form of exactly these two programs
**What is missing.** topic-11 and `benchmarks/gemv-collectives_2d` / `gemm-collectives_2d` use `<collectives_2d>`, whose `broadcast` and `reduce_fadds` are programs 05 and 03 in library form. The chapter never names it, and no other chapter covers it (grep of course/*.html).
**Why it matters.** Learners should know the "MPI-like" option exists, what it costs, and how it works inside: it reconfigures routes at runtime and tears them down. It is also the natural answer to "how do I reduce to a PE in the middle?"
**Source evidence** (`csl-libs/collectives_2d/pe.csl`): 2 colours + 2 entrypoints per dimension; `queues = [2]u16{2,4}`; runtime `color_config.reset_routes`, switches and filters; teardown wavelets after every op; the reduce network is the same alternating C0/C1 checkerboard as program 03 (the ASCII diagram at about lines 432–447). Two passes at the root: the root receives into memory (it cannot take two fabin operands on WSE-3, per a comment at line ~1095), then adds its own copy. The library also chooses `pe_id` at runtime to cut the number of ELFs (params.csl `get_params`).
**Measured evidence** (WSE-3, row of P PEs, `reduce_fadds(root = P−1, v, r, M, cb)`, `init()` excluded from timing):

| P, M | hand-written 03 span | collectives `reduce_fadds` span |
|---|---|---|
| 2, 32 | 58 | 754 |
| 8, 32 | 101 | 818 |
| 32, 32 | 273 | 1,002 |
| 8, 512 | 588 | 1,538 |

Same per-hop slope (about 7.5), about 500–700 cycles of fixed cost (reconfiguration, teardown, extra root pass) plus a second M-length pass at the root. **Gotcha found:** using only `x_colors`/`x_entrypoints` fails to compile on WSE-3, with `params.csl:25: expected task ID in the range [8,31), got: 0`. The absent dimension defaults to task ID 0. You must also pass `y_colors`/`y_entrypoints` (unused colours 4/5, IDs 12/13).
**Proposed addition.** Add a section "The library version: `<collectives_2d>`" with a 15-line excerpt of the layout `get_params` call and the PE `reduce_fadds(root, send, recv, n, callback)` call, the table above, and the gotcha. Add one paragraph on what it does internally: runtime route rewrites + teardown, the root anywhere, the same checkerboard. Close with the trade-off: "use the library for flexibility (any root, scatter/gather, chaining via one callback task); hand-write the static-route version on the hot path". Program source: `/home/user/cerebras-sdk/tmp/rev-ch11-depth/col/`.

### D6 [major] No 2-D variant is worked or measured
**What is missing.** gemv-07/08 go to 2 × 2 and k × k. The chapter stays 1-D and leaves 2-D to an exercise and a static diagram.
**Why it matters.** The chapter's claim that these shapes are what "most wafer algorithms are built from" depends on running them in parallel across rows and columns without interference. That is the point of a 2-D fabric.
**Measured evidence.** A C × R broadcast (program 05 looped over x, **one colour reused in every column**, `memcpy.get_params(x)`, `--fabric-dims=$((C+7)),$((R+2))`) verifies correctly. With equalised command streams (D4), C = 16 × R = 6 finishes in 57 cycles, the same as one column. The 16 columns run fully in parallel. Total sim cycles grow from about 7,000 to 28,500, all from H2D/D2H of 16× more data.
**Proposed addition.** Make the 2-D broadcast a worked example, not just an exercise: show the 6-line layout diff, the "one colour serves every column because routes are per PE" point, and the measured 57-vs-57 result. Then set up the gemv-08 composition with a 2-D sketch: row reductions on c0/c1 and column broadcast on c2 can coexist, and gemv-08 uses 3 colours. Point to `tutorials/gemv-08-routes-3/layout.csl` for the full colour map. Source: `/home/user/cerebras-sdk/tmp/rev-ch11-depth/cba/`.

### D7 [minor] The WSE-2 vs WSE-3 exercise has no answer, and the interesting difference is per hop, not total
**What is missing.** Exercise 3 asks the learner to compare totals, which mostly measure memcpy.
**Evidence.** WSE-2 kernel spans: P = 8, M = 32: 84 (WSE-3: 101). P = 32: 204 (273). M = 512: 564 (588). The per-hop cost is 5.0 vs 7.2 cycles, and multicast is about 1–2 vs 2–3 cycles per row. In this microbenchmark WSE-3's queue-based fabric I/O adds hop latency. Totals: 5,670 vs 6,103.
**Proposed addition.** Reword the exercise to "compare the kernel span with TSC (D1) on both architectures; which term changes, M or P?", and put the answer in a `<details>`.

### D8 [minor] Streaming is not contrasted with the tutorials' store-and-forward step
**What is missing.** gemv-06/07/08 do `@fadds(y, in, y)` into memory and then send in a separate step (`reduce` task), which is store-and-forward per PE. Program 03's single fabric→fabric `@fadds(out, in, v)` is the streaming form. The chapter's widget contrasts the two, but it never says that the SDK tutorial pattern is the store-and-forward one, or what the store-and-forward model predicts with the measured constants: P × (M + ~18) gives 8 × 50 = 400 cycles vs 101 at P = 8, M = 32.
**Proposed addition.** Add one paragraph plus an optional measured variant (receive into memory with `@fadds(v, in, v)`, then `@fmovs(out, v)` in the completion task). Present the expected ≈ P·(M + c) result as "derived", or measure it in the same harness.

### D9 [minor] Small-M behaviour and "first PE finishes early" are not explained
**Evidence.** At M = 8, PE 0 ends at 21 but PE 1 at 34. PE 0's async op completes once its wavelets are in its output queue or buffers (up to about 16, D3), not when they are delivered. This matters for the pedagogy P1 step (d) ("PE 0 finishes first, as soon as it has sent v"). That wording is correct, but "sent" means "queued".
**Proposed addition.** One sentence in the walk-through: "PE 0's completion means its M wavelets have left the CE, possibly still sitting in queues; with M ≤ ~16 that happens before PE 1 has consumed anything."

## Out of scope for this chapter (new-chapter or cross-chapter ideas)
- **Cross-chapter (ch07 host I/O / ch10):** a reusable "kernel timer" snippet built on `<time>` plus a `make_u48` helper, introduced once (perhaps in ch10's first program) and reused in ch11/ch12. Include the caveats: the TSC resets at enable, counters are not synchronised across PEs, the `bandwidth-test` sync pattern, and cycles → µs via the benchmark's `/0.85 * 1e-3` (WSE-2/3 clock ≈ 0.85 GHz per the bandwidth-test README).
- **Cross-chapter (ch05 tasks/queues):** the measured ~16 wavelets per hop (D3) is direct evidence for ch05's back-pressure section, and could replace its single "stalls past 14" quote with a measured figure.
- **Cross-chapter (ch04 fabric):** the measured hop costs (multicast router hop ≈ 2–3 cycles; CE-forwarded hop ≈ 7 on WSE-3 / 5 on WSE-2) belong in ch04's latency discussion as `measured` numbers.
- **Cross-chapter (ch07):** the command-stream skew from D4 (per-PE memcpy command queues; asymmetric H2D causes up to about 1,300 cycles of idle time at C = 16) is a host-I/O behaviour lesson.
- **New chapter / lab 2b: "Collectives at scale".** `<collectives_2d>` in depth (broadcast/scatter/gather/reduce, FSM + teardown internals, root placement), `benchmarks/gemv-collectives_2d`, a 2-D allreduce (`benchmarks/benchmark-libs/allreduce`), and a tree vs chain comparison justified by the c ≈ 7 per-hop term. Also cover memcpy's `memcpy_h2d_rowbcast/colbcast` (`benchmarks/row-col-broadcast`) as the host-side alternative to on-wafer broadcast.
- **Debugging/inspection:** `simfab_traces/` (CTF) is written on every run. A csdb walk-through that plots the wavefront from real traces would give the widget a ground truth. The research notes verified csdb only from help screens.
- **Exercise:** make program 03 compute a maximum by swapping in `@fmaxs`. Pedagogy P6 already covers this.
