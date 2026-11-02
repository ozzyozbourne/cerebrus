# Review r2: Appendix C (Measuring and observing), accuracy + reference

Reviewer scope: timing methods, trace reading, worked-example numbers, profiler facts, pitfalls, reference completeness.

## What I re-ran
I copied `programs/01-saxpy/timed` and `trace_tasks.py` to `/home/user/cerebras-sdk/tmp/r2appC-acc` (now deleted). SDK 2.10.1 simulator, N = 256 f32, `bash commands.sh 256 0 PAD`.

| chip | PAD | TSC | cycle_count (untraced) | traced cycle_count | trace lines / bytes |
|---|---|---|---|---|---|
| WSE-3 | 0 | **527** | 31,193 | – | – |
| WSE-3 | 1 | **271** | 24,763 | 25,258 | 277,138 / 19.1 MB |
| WSE-2 | 0 | **526** | 19,887 | – | – |
| WSE-2 | 1 | **270** | 20,472 | 25,437 | 280,908 / 19.0 MB |

These items match the page **exactly**:
- All four TSC values.
- FMACS Seq 0→255 at @3630→@3885 (WSE-3) and @4156→@4411 (WSE-2).
- Every line of the annotated WSE-3 excerpt: MOVRI 7, ST16 to 0x7b34, three zero stores to 0x7b30–32, LD16 values 5 and 0x0114, and UBLK at @3902.
- The WSE-2 counter at 0x318–0x31a with control 0x31e, reading 4 and then 0x112.
- The `trace_tasks.py` line `T01 3353-4113 (761 cyc, 510 instr) BLK FMACS OQFLUSH UBLK`.
- The hex decodes: beb4ebd5 = −0.35336, bf2aed8e = −0.66769, 3e00bf6c = 0.12573, 40200000 = 2.5. They agree with `default_rng(0)`.
- The µs conversions (0.32 / 0.25) and the kernel-share column.

These SDK facts also check out:
- `enable_tsc()` sets control to 7 and then resets the counter. The "random 48-bit number" quote is in `csl-libs/time/internal.csl`.
- In `7pt-stencil-spmv/run.py`, the bottom-right signal, the `(width+height-2)-(px+py)` correction, `max(time_end)-min(time_start)` and `make_u48` all appear as described.
- 850 MHz is in `conjugate-gradient/run.py`, and the bandwidth-test README quote is correct.
- `sunsetCount: 50` is set.
- `fmt_with_coords` exists in simprint.
- topic-12 uses `trace_string/u32/timestamp` and calls `read_trace` after `runner.stop()`.

## Findings

**A1 (med) · Same-PE rule callout (line 115), and pitfall 3. The page gives the wrong reason why counters differ.**
- The callout says "each PE's counter starts when the launch reaches that PE … On hardware they start as random numbers."
- The page's own bullet (line 89), confirmed in `time/internal.csl`, says `enable_tsc()` zeroes the counter. So after enabling, the offset between two PEs is the moment each PE ran `enable_tsc()`, on the simulator and on hardware alike. The random start value matters only before enabling.
- This is also why the SDK needs `time_ref` at all: each PE is zeroed at a different time.
- Fix: "Each PE's counter is zeroed when *that* PE calls `enable_tsc()` (and runs freely from a random value before that). PEs enable at different cycles, so their counters are offset by an unknown amount." CCN 19 should get the same nuance.

**A2 (med) · `cycle_count` noise is understated (three-instruments table "a few percent"; decision-chart recipe R[0] "Expect a few percent of noise").**
- My four untraced reruns differ from the page's numbers by −3 % to **+41 %**: WSE-3 PAD 0 gave 31,193 against 22,126, and PAD 1 gave 24,763 against the page's 21,631–22,844.
- The page's own five runs span 36 %.
- Fix: "often 5–15 %, sometimes 40 %". Drop "Expect a few percent" from R[0].
- The table's single `cycle_count` values (e.g. WSE-2 PAD 1 = 19,720) should be labelled "one run".

**A3 (med) · Profiling-on-other-machines paragraph (line 202): "the course simulated at most 16 PEs per run (Chapter 18)" is now false.**
- Lab 15 (`15-lab-cg.html` line 666) reports measured runs at **16 × 16 = 256 PEs** and defaults to 5 × 5.
- Lab 14 runs 4 × 4.
- Fix: "at most 256 PEs per run (Lab 15)". Flag Ch 18 line 331 ("at most 16 PEs") to its fixer.

**A4 (low-med) · Trace size presented as a fixed per-chip fact (line 128, R[3], pitfall 8).**
- The page gives 318,240 lines / 20.7 MB on WSE-3 and 230,747 / 17.1 MB on WSE-2. My reruns gave 277,138 and 280,908 lines, about 19 MB each, so the WSE-3 > WSE-2 ordering reversed.
- Every PE prints a line per cycle (IDLE included), so the size scales with the noisy total run length × PEs, not with the kernel.
- Fix: "about 230k–320k lines (17–21 MB) for one PE and N = 256; size grows with total simulated cycles × PEs, IDLE lines included."

**A5 (low) · Trace anatomy: the issue-stage lines are not mentioned (widget "Pipe" and "[EX OP]" fields; line 151 "256 FMACS lines").**
- Every op also has an `[IS OP]` line, e.g. `@3627 … Seq: 0, Pipe: 3, Msg: [IS OP] … FMACS Dest:[S0DS0] … Src2:R1,R0`. It carries Pipe 3 on WSE-3 and 2 on WSE-2, against 6 and 4 on the `[EX OP]` lines.
- So a plain `grep FMACS` counts 257 lines, and "Pipe" is evidently the pipeline stage (issue vs execute), not a mystery.
- Fix: in the widget, say "[IS OP] lines (issue, Pipe 3/2) precede the [EX OP] lines (execute, Pipe 6/4); grep `EX OP`". The "meaning not documented" caveat can stay, but give the observed correlation.

**A6 (low) · Overhead breakdown (line 151 "the other 15 … are the timestamp reads, two DSD loads and the start-up of the op"; pitfall 6; R[1] "~10–15 cycles of overhead").**
- The trace shows how the 15 cycles split:
  - the counter is zeroed at @3614 and read as 5 at @3619;
  - three ST16s that copy t0 are interleaved with the reads (@3620–3624);
  - two LDS*WDS loads take @3625–3626;
  - three idle cycles pass before the first FMACS EX;
  - four compiler NOPs come after the last element (@3886–3889).
- An "empty region" would contain the stores but not the DSD loads, the fill or the NOPs. So "time an empty region and subtract" removes only about 5–6 of the 15.
- Fix: list the parts, and say that the op start-up and drain belong to the op, not to the instrument.

**A7 (low) · Excerpt fidelity (line 154): the page says only "padding removed" from the `Id/Instr/Pipe` fields, but lines were also dropped.**
- Dropped lines: the t0 ST16s at @3620/3622/3624, the second LDS0WDS/LDS1WDS line at @3625/@3626 (each DSD load prints two lines), the NOPs, the t1 copies, and @3893–3901.
- Fix: "some lines omitted". Optionally show that each DSD load prints two words.

**A8 (low) · Line 180 "the whole program took about 21,700 cycles".**
- The `trace_tasks` line quoted just above comes from the *traced* run (29,368).
- Fix: "about 21,600–29,400 cycles depending on the run (29,368 for this traced one)".

**A9 (low) · Nsight Compute row: "`--clock-control base` locks clocks so runs compare".**
- `ncu` already locks to base clocks by default. The flag that matters is `--clock-control none`, which you would use to profile at real boost clocks.
- Fix: "ncu locks clocks to base by default (`--clock-control base`); `none` disables this, so results differ from production clocks."

**R1 (low) · Reference gap: the `<time>` and `<timer>` APIs.**
- `time.csl` also exports `disable_tsc`, `reset_tsc_counter` and `get_perf_cntr(result, 0|1)`, which reads hardware performance counters.
- `csl-libs/timer.csl` (`<timer>`) offers named start/stop buffers and on-device `subtract_timestamps`.
- Neither is mentioned. Add one table row, or a sentence after the `<time>` bullets.

**R2 (low) · Reference gap: Lab 15 is a richer profiling example than any cited.**
- Lab 15 builds a compile-time `PROFILE` per-phase TSC split, with a measured split per iteration on PE (2,2). It is the course's best multi-phase example.
- Fix: link it from section 2 and from the chart's Q3 recipe. Also add the CG benchmark (`conjugate-gradient`, listed in R[2]) to the SDK tag in the "Synchronise, then correct" bullet, which currently cites only 7pt-stencil-spmv.

**R3 (low) · Chapter references.**
- Ch 11 `#kernel-time`, Ch 12 `#hop-cost`, Ch 6 `#collisions` and Ch 10 `#sim-outputs` all exist, but the page links only to chapter tops.
- Fix: add the fragment anchors, since this is a reference page.

## Not re-verified
- The csdb transcript. I accepted the builder's log. The binaries exist at `/home/user/cerebras-sdk/csdb` and `cs_readelf`.
- The tt-metal and Tracy flags. They are plausible and consistent with current docs as I know them, and are correctly tagged as vendor search extracts.
- The PAD 0 "two cycles apart" spacing (quiz Q3). I did not trace it, but 527 ≈ 2 × 256 + 15 supports it.

## Summary
High 0 · Med 3 (A1–A3) · Low 9 (A4–A9, R1–R3). The worked example reproduces to the cycle on both chips, and every trace line, address, hex value and SDK quote checked is correct.
