# ch12 fix log (Lab 3: heat stencil)

Files changed: `course/src/12-lab-stencil.html` (rebuilt into `course/12-lab-stencil.html` with `tools/build.py`), and `course/programs/04-heat-stencil/{layout.csl, pe_program.csl, run.py, commands.sh, expected_output.txt}`.
Experiments ran in `/home/user/cerebras-sdk/tmp/fix-ch12/`. The variant sources and scripts are kept there; the simulator outputs were deleted. All new numbers are TSC cycles on one PE (PE 1, or PE 0 at P = 2): the slope between 10 and 100 steps, SDK 2.10.1.

## Findings

### Accuracy
| ID | Status | Note |
|---|---|---|
| A1 | Fixed | Re-based on TSC in-kernel timing. Table uses 10/100-step TSC slopes: 100.2 / 130.2 / 250.2, P=2 101.0, P=16 130.8, WSE-2 104.1 / 134.1 / 255.4. Model is 90.2 + 2.5·n. 88 removed everywhere. |
| A2 | Fixed | Hang callout rewritten: fails on both chips, FATAL "trying to term ut_instr[3], but it's not ours", host hangs. Re-measured: 2,367 (WSE-3) and 2,148 (WSE-2) with the TSC build; the coordinator's 2,123/2,125 is quoted for the original build. `.ut_id` 4/5 on the receives fixes it on WSE-3 (re-measured SUCCESS). pe_program comment corrected to "always on WSE-2; default on WSE-3". |
| A3 | Fixed | Re-measured with the new program: WSE-3 links at n=5,450 and fails at 5,480 ("task table"); it is 5,500 without the timing code. WSE-2 links at 5,650 and fails at 5,750. Widget MAXN is 5450, and the slider (log) reaches ~5,800, so the warning can now show. |
| A4 | Fixed | Covered by A1 (single consistent 130.2). |
| A5 | Fixed | "Bit-identical at α = 0.25; other α differ in last bit; rtol 1e-5/atol 1e-6". |
| A6 | Fixed | Widget hint says it is bit-identical at α = 0.25 only. |
| A7 | Fixed | New "How the SDK's stencils differ" section: both are 3-D pencils. 7-pt does not overlap (source TODO quoted). 25-pt overlaps by async fabric `@fmuls`. |
| A8 | Fixed | "Scale to the whole wafer, hundreds of thousands of PEs". 900k is tagged Vendor; 737k CS-2 rectangle is tagged SDK. |

### Pedagogy
| ID | Status | Note |
|---|---|---|
| P1 | Fixed | New "One timestep, step by step" walkthrough: run → start_step → 4 async ops → completion tasks → op_done → update → next/finish. Also covers no-recursion, why launch() waits, fixed ends, and STEPS=0. Timeline widget N1 added. |
| P2 | Fixed | "Why the step logic looks like this" callout covers one task per op (activation bit), counted sends, no ghost race (back-pressure) and counter first. |
| P3 | Fixed | commands.sh listed, with documented knobs (P, n, STEPS, ALPHA, ARCH). Exact commands shown. The method is now TSC; a callout explains why total-cycle differencing (and a 0-step baseline) is noisy, with own measured evidence (5,260 vs 8,905 total for an identical build; TSC 1,029 both times). |
| P4 | Fixed | Exercise 2 now uses P=4 n=4. Expected result: 3e-4 at L=16; at L=128, 0.48/0.16/0.07/0.017 after 1k/5k/10k/20k steps (Derived, f32 recurrence). Rod widget has a speed control and runs to 20,000 steps. |
| P5 | Fixed | All exercises have `<details>` hints. Exercise 1 also gives an expected result (178 vs 130) and a fused-receive stretch goal. Exercise 3 has f16 memcpy hints and says to compare slopes. Exercise 4 (wide halo) is new. |
| P6 | Fixed | 2.5/cell is explained as 0.5 + 1 + 1 from DSD rates, linked to Ch 6. Re-measured per op on both chips (fadds-only slope 0.5, one-fmacs slope 1.0). Fixed part is decomposed (D1). |
| P7 | Fixed | P = 2 bullet explains that the row moves at the pace of its interior PEs. |
| P8 | Fixed | One memory figure (see A3), "≈43 KB for arrays". |
| P9 | Fixed | Caption explains one route per color and parity. Arrows are labelled E0/E1/W1/W0. Queues 0–1 (memcpy) and task IDs 10–13 (8–20 range) are explained in prose. |
| P10 | Partly | Callout now says "Chapters 3 and 5 described this hang" and includes a try-it step. The ch10 forward reference is not edited (not owned). |
| P11 | Fixed | Device samples are overlaid as dots at step 50 (defaults). Check-yourself quiz added (6 questions). |

### Visuals
| ID | Status | Note |
|---|---|---|
| V1 | Fixed | All colours are now classes or `cssVar` (live vars). Theme toggle verified by screenshot. |
| V2 | Fixed | Log slider (2^0…2^12.6), log–log curve, cursor always drawn, plus a stacked breakdown bar. |
| V3 | Partly | Decomposition has a tighter viewBox, 13–14px text, and sentences moved into the caption. Widgets rely on the shared ≤680px min-width/scroll fix; there is no per-widget mobile redesign. |
| V4 | Fixed | α slider goes to 0.6. Readout shows three regimes. Drawing is clamped, and "blew up at step k" stops playback. |
| V5 | Fixed | Play/Pause label. Auto-pause at 50 only for the validated config, with a message. Step +1 button added. |
| V6 | Fixed | Axis titles, PE labels (when ≥30px), PE boundary lines, amber boundary ghosts, autoscale toggle, device overlay and steady-state dashed line. |
| V7 | Fixed | Colour labels, amber "1.0 fixed"/"0.0 fixed" ghosts, "(first)"/"(last)". |
| V8 | Fixed | Halo-text labels placed above-left, consistent memory text, µs formatting. |
| V9 | Fixed | New measured comparison chart (N2) plots the n sweep for both chips and the P/arch/ablation/overlap bars, with hover-to-row highlight. |
| N1 | Done | "Inside one timestep" widget (see below). |
| N2 | Done | Measured comparison chart. |
| N3 | Not done | Total-vs-steps chart dropped: the method moved to TSC, so the warm-up story is told in the noise callout instead. |
| N4 | Partly | Covered by the labelled decomposition figure; no separate interactive routing map. |
| N5 | Mostly | Device overlay, α regimes, Step +1 and boundary ghosts are done. There is no per-PE "ghost inspector". |

### Depth
| ID | Status | Note |
|---|---|---|
| D1 | Fixed | "Where the 90 cycles go": 4×14.6 transfers+tasks, ≈13 bookkeeping, ≈19 start-up (≈6/instr), 2.5·n streaming. Re-measured base, P=2 and compute-off (71.2 WSE-3 / 80.1 WSE-2), plus single-op variants. Stacked bar in the model widget. The WSE-2 split is explained. |
| D2 | Fixed | "Does overlapping communication help?" section: re-measured 178.0 vs 130.2 with explanation. Exercise 1 expected result. 25-pt fused `@fmuls` described. |
| D3 | Fixed | TSC added to program 04 (enable_tsc/get_timestamp in run(), finish(), separate pack() RPC, 16-bit D2H). Per coordinator note 19, only one PE is reported and the page warns not to compare PEs. Inlining trap re-measured: 130.2 → 167.0, tasks 176 → 212 B. |
| D4 | Fixed | Shortened comparison table plus bullets with the SDK source facts and the review's measured SDK numbers (tagged as review runs). |
| D5 | Fixed (brief) | 2-D/3-D paragraph with message/colour/microthread counts and the D1 constants. No new 2-D exercise. |
| D6 | Fixed | Whole-wafer readout in the model widget and a prose section (Derived) with caveats (simulator, clock, unpublished WSE-3 dims, snake layout, host I/O, toy problem) and the Rocki et al. 0.86 PF reference. |
| D7 | Fixed | Strong-scaling table for L = 4,096 (64/256/1,024 PEs → 250/130/100, 2.5×). |
| D8 | Fixed | WSE-2/3 bullet rewritten. Exercise 3 says to compare slopes. |

### Coordinator notes applied
- Notes 1, 11: hang wording.
- Note 4: 90 + 2.5·n.
- Note 12: task IDs 8–20.
- Note 13: memory, re-measured.
- Notes 14, 16, 22, 23: rates, Ch 6 link, startup ≈17 when isolated.
- Note 17: noise and TSC.
- Note 19: same-PE timing.
- Note 20 and the ch11 hop note (24): hop costs cited.
- **Bank clash (note 23) measured in this lab.** Both `@fmacs` read `u[1]` and `lap[0]`, which are n+1 words apart. At n = 15 a step costs 158.2 (WSE-3) / 162.1 (WSE-2) instead of ~128/131. Padding `lap` by one word gives 128.2 / 132.1. n = 16/17 are unaffected. This is in a callout, and the model widget warns when (n+1) % 4 == 0.

## New visuals
1. **Inside one timestep** (N1): an animated Gantt chart.
   - Lanes: a CE lane plus four microthread lanes, with a `pending` counter.
   - Each transfer bar shows the transfer and then its wait for the CE (dashed).
   - CE lane runs the completion tasks t_se/t_sw/t_rw/t_re in measured order, then @fadds/@fmacs/@fmacs and the loop step.
   - Controls: n = 4/16/64, interior vs end PE, Play/Pause, Next event, Reset.
   - "Input queues 2/3" replays the clash: the two clashing lanes turn red and a FATAL stamp appears.
   - The split is tagged Derived; the totals match the measured values.
2. **Measured comparison chart** (N2): cycles/step vs n for WSE-3 and WSE-2 with fit lines, plus bars at n=16 (P=2/8/16, WSE-2, compute-off, naive overlap). Hover highlights the table row.
3. **Fixed-cost breakdown bar plus log–log model**, in the "Use the model" widget. It also gives a whole-wafer readout (Derived), a memory warning and a bank-clash warning.

## Program changes (programs/04-heat-stencil)
- pe_program.csl:
  - `<time>` TSC: t0 in run(), t1 in a tiny `finish()`.
  - `pack()` RPC copies the timestamps to an exported `tsc` [6]u16.
  - STEPS=0 path goes through finish().
  - Microthread comment corrected.
- layout.csl: exports `tsc` and `pack`.
- run.py:
  - Launches `pack`, does a 16-bit D2H and reassembles the 48-bit timestamps.
  - Prints "kernel time on PE 1 (TSC): … cycles per step".
  - Validation is unchanged.
- commands.sh: documents the knobs and adds `ALPHA`.
- expected_output.txt: regenerated. The profile is unchanged (the widget overlay still matches all 16 values). New lines: TSC "6549 cycles for 50 steps = 131.0", "[11666 simulated cycles, WSE-3]".

## Validation
- `ARCH=wse3 bash commands.sh`: SUCCESS. `ARCH=wse2 bash commands.sh`: SUCCESS (TSC 134.8/step over 50 steps). Profile is identical on both.
- run_all.sh logic for 04 (same command, with grep SUCCESS and cycle_count): PASS, 11,666 cycles. The full run_all.sh was not run because it would write into programs 01–03 and 05, which I don't own.
- Program dir cleaned: out/, sim*.json, sim.log, simfab_traces, wio_flows_tmpdir.*, run.log and simconfig.json all removed.
- Playwright, 1100px and 390px, light and dark:
  - No page or console errors; horizontal overflow 0.
  - Exercised: timeline (play, clash replay, edge, step), rod (play → auto-pause at 50 with device overlay, Step +1, α=0.6 blow-up at step 28, α=0.5 regime, autoscale, speed), model slider (n = 1/16/64/5,793 with warning), chart hover and theme toggle.
  - Screenshots reviewed, then deleted.

## Open issues
- On WSE-2, `@fadds` streams 0.5 cycles/cell in this kernel. Cross-note 16 says 1/cycle on WSE-2 (isolated). The operand pattern probably differs; ch06 may want to reconcile this.
- The ch10 forward reference ("two problem sizes" vs step counts) is still unedited (not owned).
- The per-hop/through-PE latency is only cited, not used: the halo is one hop.
- The SDK benchmark numbers (7-pt 4,206/8,078, 25-pt 123.6) come from the depth review's runs. I did not re-run them.
