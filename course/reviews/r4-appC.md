# R4 audit: Appendix C, Measuring and observing (appC)

**Verdict: Mostly correct. Explanation quality: good.**

The worked example reproduces to the cycle. I reran `01-saxpy/timed` (WSE-3, N = 256, PAD 1, trace on) in `/home/user/cerebras-sdk/tmp/r4-appC/` and have since deleted the directory. Results:
- TSC 271.
- FMACS @3630→@3885, all 256 element lines carrying `Instr: 1255`, and the `[IS OP]` line at @3627 with Pipe 3.
- Stamps 5 → 0x0114 at @3619/@3890, and `UBLK` at @3902.
- `T01 3353-4113 (761 cyc, 510 instr)`.
- `cycle_count` 23,038 and 254,939 trace lines. Both fall inside the page's ranges.
- A plain `grep FMACS` gives 257 lines; grepping `EX OP` gives 256.

The r2 fixes (A1–A9, P1–P7, V1–V9, R1–R3) are all in place. The problems left are one mis-described span, a few imprecise trace details and some missing bridges.

## Errors

**E1 (med) · §Worked example, paragraph after the `trace_tasks` output, and the `#nest-svg` figure.**
- Quoted: "That 761-cycle run is the whole RPC as memcpy's command task executes it (argument handling, your function, unblock)." The figure also labels the 761-cycle bar "RPC run T01".
- What is right: the run neither starts at the RPC's start nor ends at its end.
  - It ends about 210 cycles after `UBLK` (@3902). From @3903 to @4113, T01 runs the same stack-push loop (0x0184–0x019a: `MOVRI 0x20`, `LT16`, `ADD16` into 0x1494+) that it ran at @3355. In other words, it is already taking in the wavelets of the *next* command, the D2H of y. The D2H tasks T29, then T21/T30, follow at once (@4119, @4321…).
  - The RPC's earlier parameter pushes run separately (`T01 3285-3305`).
  - `trace_tasks.py` merges anything from one task with gaps under 40 cycles, which is why the two commands look like one run.
- Fix: "The run starts while memcpy pushes the RPC's arguments (an earlier push is a separate run, 3285–3305), contains your function (3608–3902), and continues 211 cycles past `UBLK` while the same task decodes the next command (the D2H). The tool merges them because the gap is under 40 cycles." In the figure, end the RPC bracket at @3902 and shade 3903–4113 as "next command".

**E2 (low) · §3 trace-line widget, the "Msg" part.** Quoted: "The | becomes v or ^ when control enters or leaves a task."
- Measured on P4.1: all 601 `v` lines sit on a terminating instruction (opcode suffix `.T`, e.g. `ST16.T`, `NOP.T`), and every `.T` instruction carries `v`.
- `^` marks the first instruction of a task activation: 539 of 601 change task, and the rest re-activate the same task (e.g. T01 at @3905).
- Fix: "`^` = first instruction of a task activation; `v` = the task's last instruction (its opcode ends in `.T`)."

**E3 (low) · §3 widget hint and §Worked example lead-in.** Both say "the trailing `[ x ] U0` marker". The full sim.log contains **no** `[ x ]` at all. The lines end `[ ] U0`. Write the marker as it appears, or as "`[ ] U0`".

**E4 (low) · §1, second paragraph.** Quoted: "In program 01 each H2D costs about 1,360 cycles and the D2H about 4,400 of 7,740, against about 130 for the `@fmacs` (Chapter 11)".
- The phase table these numbers come from is in Ch 11's "What happens inside, in order", which has no anchor. The link goes to `#kernel-time`, a later section.
- That table gives H2D(x) 1,355 and H2D(y) 1,291 cycles.
- "of 7,740" reads as if 7,740 were the D2H total.
- The run is N = 64, while every example on this page is N = 256, and the page never says so.
- Fix: "In program 01 at N = 64 (WSE-3, 7,740 cycles in all), each H2D costs about 1,300 cycles, the D2H about 4,400 and the `@fmacs` about 130." Ask the Ch 11 fixer to add an anchor to that section.

**E5 (low, cross-page) · contradiction with Ch 11.**
- This page says "never read a kernel cost off the difference of two totals" (pitfall 2; R[0]).
- `11-lab-first-programs.html` line 218 (src line ~142) says "Subtracting whole-run totals for two step counts also works, but it is noisier".
- Ch 13's callout sides with this page. Route to the Ch 11 fixer: "…is unreliable (Chapter 13 shows 5,260 vs 8,905 for one build)".

## Explanation problems

**X1 · §Worked example, "How much of the 15 is the instrument?"**
- The page itemises the 15 cycles as 5 + 2 + 3 + 4 + 1 and then says the 10-cycle empty region leaves "5 (the DSD loads and the pipeline fill)". That makes the 4 NOPs part of the instrument, but the reader is never told so.
- The page itself says the compiler placed those NOPs "after it", meaning after the FMACS.
- Fix: say the arithmetic explicitly: "instrument ≈ stamp t0 (5) + NOPs (4) + t1 read (1) = 10; op = DSD loads (2) + fill (3) = 5". Add that the NOP attribution is inferred from the empty-region total, not seen directly.

**X2 · §2 "Synchronise, then correct".**
- One long sentence carries an allreduce, a signal, `time_ref`, a correction formula and a max/min.
- `(width + height − 2) − (px + py)` is not explained. It is the Manhattan hop count from the bottom-right PE to (px, py).
- Fix: split the bullet into numbered steps and add a 3 × 3 worked line: "PE (0,0) is 4 hops from (2,2), so the signal reaches it 4 cycles later than the sender's own `time_ref`; the host adds 4."

**X3 · §3 `trace_tasks.py` paragraph.** It says the script groups "consecutive instructions of one task". It actually merges same-task instructions separated by gaps of under 40 cycles, IDLE included. That is why runs contain IDLEs and, per E1, a neighbouring command. State the 40-cycle rule.

**X4 · Terminology drift.** The page says "x/y operand collision" in the table legend, "operand bank collision" in quiz Q3, and "operand streams collide" elsewhere. Appendix A's entry is "bank clash (operand collision)". Use one term and link the glossary entry once.

## Connecting gaps

**G1 (med, S) · "PAD 1 halves the time" → why one word matters.**
- The page states the effect and links Ch 6, but never shows the addresses. The reader is left to accept that 527 vs 271 cycles comes from "a collision".
- Bridge: one sentence using this page's own tools. "With PAD 0, y starts 256 words after x; 256 ≡ 0 (mod 4), so both source streams hit the same bank every cycle (empirical rule, [Ch 6](06-dsds.html#collisions)). PAD 1 makes it 257 ≡ 1." Optionally show `cs_readelf -m` or the csdb `image lookup` for x and y.

**G2 (med, M) · TSC around one function → timing an asynchronous, task-driven kernel.**
- Every snippet here wraps a single RPC body. Most CSL kernels from Ch 5 onward are data tasks triggered by wavelets, so there is no single function to bracket.
- Ch 12 (program 03) does show the pattern: `enable_tsc` and `t_start` in the launch function, `t_end` in the completion path, both on one PE. This page never names that pattern.
- Bridge: add a short "Kernels made of tasks" bullet in §2. "Stamp the start in the function that arms the receive, the end in the task that sees the last wavelet, and export both from that PE ([Ch 12](12-lab-neighbours.html#measuring))."

**G3 (med, S) · "Stamps cost 10 cycles" → Lab 5's "30–35 cycles per mark()".** These look contradictory side by side. Lab 5's `mark()` (programs/07-cg/pe_program.csl l.82) joins the words into an integer, subtracts the last stamp and adds into a bucket on the device. Bridge, in the Lab 5 sentence of §2: "each mark() costs 30–35 cycles, not 5, because it also does a 48-bit subtract-and-accumulate on the device; raw `get_timestamp` is cheap, arithmetic on stamps is not."

**G4 (low, S) · fabric coordinates for grep in a multi-PE program.**
- The widget explains `P4.1` for a 1 × 1 rectangle, and R[3] says "fabric coordinates". A learner tracing Lab 2 or Lab 3 still has to work out the mapping.
- Bridge: "your PE (px, py) prints as `P(px+4).(py+1)` with the course's `--fabric-offsets=4,1` (3 memcpy columns + 1 halo on the west, 1 halo row on the north)." Link Ch 7 or Ch 10.

**G5 (low, S) · `enable_tsc()` zeroes → what about several RPCs?** Pitfall 4 says to enable once, but a host that launches the kernel several times calls `saxpy` (and so `enable_tsc()`) each time. Bridge: one clause saying it is fine to enable at the start of each launched function as long as both stamps of a measurement fall after that call. Ch 12's program 03 and Ch 15 do exactly this.

## Checked and fine

- Every quoted trace line, address (0x7b30–0x7b34, WSE-2 0x318–0x31e) and stamp value reproduced in my rerun, together with the IS→EX 3-cycle gap, the `Instr` pairing and the 257/256 grep counts.
- The page's 271/527/270/526 TSC values agree with r2. All kernel-share percentages recompute correctly (1.7–2.4, 1.1–1.3, 2.6, 1.3–1.4 %), the 36 % and ~41 % spreads are right, and the run counts per row (8, 2, 5, 2) match the logs.
- My `cycle_count` of 23,038 and 254,939 trace lines fall within the stated ranges.
- Quiz Q4: 271 × 2³² = 1,163,936,137,216 is exact, and the explanation of the word order is right.
- Hex decodes and the SAXPY check: −0.6677 + 2.5 × 0.1257 = −0.3534.
- In `<time>` (SIF csl-libs), `enable_tsc` sets the control register to 7 and then calls reset, the random-start comment is there, and `disable_tsc`, `reset_tsc_counter` and `get_perf_cntr` exist. `<timer>` has start/stop/elapsed and `subtract_timestamps`.
- The device and host snippets match `programs/01-saxpy/timed`, and `commands.sh` matches `N HALF PAD`, fabric 8 × 3 and offset 4,1.
- All 15 cross-page anchors resolve. Each was checked against its target:
  - Ch 12: Lab 2 kernel 58–158 of 4,394–5,260, so 1–3 %; hop costs 2.0/1.0 and 9.2/6.0.
  - Ch 13: 10/100-step TSC slope; 5,260 vs 8,905.
  - Ch 15: 7–10 % profile cost; 16 × 16 grid.
  - Ch 10: a fatal stop writes no `sim_stats.json`; "could be a kernel stall".
- The clock statements (850 MHz SDK, 1.1 GHz WSE-2 HC22, no published WSE-3 clock) match CCN 2/10, and the µs conversions are right.
- The same-PE callout matches CCN 26. The noise claims match CCN 17/26.
- The ncu clock-control row is corrected, and the Tenstorrent/NVIDIA rows are correctly tagged as vendor search extracts.
