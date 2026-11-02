# ch10 · fix log

Files edited: `course/src/10-lab-first-programs.html` (then `python3 course/tools/build.py`), `course/programs/02-wavelet-tasks/{layout.csl,pe_program.csl,expected_output.txt}`. Added `course/programs/01-saxpy/trace_tasks.py` and `course/programs/01-saxpy/timed/{layout.csl,pe_program.csl,run.py,commands.sh,expected_output.txt}`. Program 01's original files are unchanged. All experiments ran in `/home/user/cerebras-sdk/tmp/fix-ch10/`, which was deleted afterwards. Other machines' simulations were running at the same time, so whole-run totals from parallel runs were not used.

## New measurements (SDK 2.10.1 simulator, tagged Measured on the page)
- Program 01 instruction trace (WSE-3, N=64, `SINGULARITYENV_SIMFABRIC_DEBUG=inst_trace`): H2D x 115–1,470, H2D y 1,489–2,780, RPC 2,796–3,251 (BLK 3,089, FMACS Seq 0 at 3,124 to Seq 63 at 3,250 = 127 cycles, UBLK 3,251), D2H 3,252–7,689 (57%), idle until 7,740. This agrees with the depth reviewer and the coordinator's ch09 note.
- Program 02 traces (WSE-3, N=100), with and without the barrier. 100 measured `on_value` start cycles each. H2D "done" (T27 UBLK) at 4,709 with 84/100 run. wait_done BLK at 4,987 with 89 run. The 100th task starts at 5,421 and executes UBLK at 5,460. New finding: without the barrier, the D2H sends `stats[0]` at 5,539 (95 run), `stats[1]` at 5,635 (96 run), and `count` at 7,777 (100). One memcpy_d2h samples its four elements at different moments, which explains the 3207.2998 sum of squares.
- TSC kernel timing (new `01-saxpy/timed`, cycles including ~10 for the timestamp reads). f32 WSE-3 143 / 2,063 / 8,207 at N = 64 / 1,024 / 4,096. With one pad word between x and y, 79 / 1,039 / 4,111. f32 WSE-2 78 / 2,062 / 8,206; padded 78 / 1,038 / 4,110. f16 WSE-3 32 / 272 / 1,040. f16 WSE-2 46 / 526 / 2,062. **The "2 cycles/element" of program 01's @fmacs is a bank conflict**: padding gives 1/element on both chips. This reconciles cross-chapter notes 14/16 (1/cycle) with note 18 (2/elem).
- Largest N that links for program 01: WSE-3 5,615 (5,616 fails: "ran out of PE memory for data (section .data.hi)"), WSE-2 5,784. N=6000 fails with `.bss` / task-table errors. This is consistent with note 13 (~44 KB usable on WSE-3).
- Removing unblock: `launch()` returns (printed a marker after it). memcpy_d2h aborts with "received length (0 bytes) is not expected (256 bytes), could be a kernel stall", exit 134, and no sim_stats.json is written. This matches the coordinator note.
- Exercise solutions verified on both chips: histogram (`[8 11 11 7 10 10 10 10 15 8]`), `scale` RPC, and f16 pairs packed with `data16.view(np.uint32)` + MEMCPY_32BIT (50 tasks, sum 26.157837, rtol 1e-4).
- Noise: program 01 gave 16,940 cycles once under load (7,740 otherwise). 3 of 28 TSC runs made 2–3 at a time aborted with "could be a kernel stall"; each passed on rerun.

## Accuracy
- A1 fixed: "tens of cycles" replaced by measured 127 cycles (3,124–3,250, ≈130, <2%), with a phase table.
- A2 fixed: 46 provenance tags (measured, sdk, derived, vendor) on every number.
- A3 fixed: Lab 3's method is now described as "0 and 100 kernel iterations and subtract".
- A4 fixed: the exercise asks how many values are missing (via cumsum). Answer: N−5 always, and stats[1] includes N−4.
- A5 fixed: the layout comment now reads "false = host may read but not write" (program revalidated).
- A6 fixed: cycle counts are presented as approximate, with a "Cycle totals are approximate" callout and measured ranges.
- A7 fixed: rtol+atol explained; 17/64 differ from numpy, 64/64 match a one-rounding FMA.
- A8 fixed: the figcaption describes the WSE-3 relay hop (color 23 → IQ0 → memcpy microthread → MEMCPYH2D_1) with an sdk tag.
- A9 fixed: the f16 exercise is rewritten (pack on host, MEMCPY_32BIT), and the reason not to use MEMCPY_16BIT is given.
- A10 fixed: the remove-unblock exercise gives the observed abort, and notes that launch() returns.

## Pedagogy
- P1 fixed: a "Set up a working copy" callout (~/lab1 copies, not /tmp). Each exercise block says to work in the copy.
- P2 fixed: commands.sh shown for both programs, with flag explanations. A note under each output says where the cycle line comes from (sim_stats.json one-liner in setup).
- P3 fixed: the intro links to Chapter 9's walkthrough. New "Reading program 02" list covering color, queue, task ID (+ IDs 8–20, never 29), exports (`immutable: 1`), flag, and initial values. `host_waiting` was moved above `on_value` in the program, so order no longer needs explaining.
- P4 fixed: new section "Why the barrier itself is race-free", plus the measured-schedule widget.
- P5 fixed: corrected f16 exercise, verified on both chips.
- P6 fixed: the remove-unblock exercise has prediction + "What we saw" details.
- P7 fixed: every exercise has a Check/Hint `<details>` with measured answers (266k cycles, link limits 5,615/5,784, scale, histogram, N−5, f16 pairs, TSC prediction, trace exercise). The back-pressure stretch exercise is explicitly marked unmeasured.
- P8 fixed: "If it fails" troubleshooting section.
- P9 fixed: "Produce the bug yourself" comes before the bug callout.
- P10 fixed: the rtol=1e-4 / sequential vs pairwise sum is explained; the device matches a sequential f32 sum exactly.
- P11 fixed: the figure says "color 0 (MEMCPYH2D_1)". The program now guards `@initialize_queue` with `if (@is_arch("wse3"))` as SDK topic-03 does (revalidated on both chips), and the text explains why.
- P12 fixed: the callout opens with a cross-link to Chapter 7's widget.

## Visuals
- V1 fixed: the new widgets put their SVGs in a scroll box with min-width 620px. The streaming figure relies on the shared phone rule (figure > svg min-width 620). Verified no page overflow at 390px.
- V2 fixed: the sequence diagram is rebuilt with `class: "s-blu"` and `f-*` classes; the chart uses `cssVar`. It follows the live theme toggle (screenshots after toggling).
- V3 fixed: device-vs-numpy(-vs-FMA / sequential) tables with `<mark>` on the differing digits, for both programs.
- V4 fixed: the streaming figure has a control lane (launch('wait_done') → wait_done() branch; 100th task unblocks; D2H back to host) and the new footer line.
- V5 fixed: "color 0 (MEMCPYH2D_1)".
- V6 fixed: a muted WSE-2 bypass arc ("data_task_id = color 0"), and the queue path labelled "WSE-3: data_task_id = input queue 2".
- V7 fixed: separate lifelines "SdkRuntime + memcpy fabric" and "memcpy module on your PE (sys_mod)". Hops are labelled color 22 / 23 / 21.
- V8 fixed: a red activation bar plus "cmd stream blocked" label on the module lifeline; the label is now "@fmacs ×64".
- V9 fixed: a load()/run() step, and dashed return arrows (H2D done, unblock, results). Per the coordinator note, launch() is described as returning immediately rather than blocking on the unblock.
- V10 fixed: `<title>`/`<desc>` on every SVG; desc lists the steps.

## Depth
- D1 fixed: the measured phase table, plus a timeline bar inside the step-through. Three sentences: BLK is literal; `a` travels as 2×u16 + function id 3; D2H costs ~60 cycles/element. The out_rpc.json excerpt is included.
- D2 fixed: section "Look inside: the instruction trace", with the command, a 5-line real excerpt, the shipped helper `programs/01-saxpy/trace_tasks.py` (shown via {{code}}), a task-ID legend and a trace exercise.
- D3 fixed: cycles-vs-N table (WSE-3 + WSE-2), a log-log chart with fits, and the slope interpretation.
- D4 fixed: a validated `timed/` variant (TSC, f32/f16, PAD), shown via {{code}}/{{out}}, with the measured table, the bank-conflict explanation and a prediction exercise. The WSE-2 N=64 "anomaly" is explained: there is no conflict at that offset on WSE-2.
- D5 fixed: the measured schedule in widget 2 and bullets (84/100 at H2D done, 89 at BLK, 5,421/5,460, two queue hops). It adds the new interleaved-D2H finding.
- D6 partly applied (as instructed): a WSE-3-only measured aside with the depth reviewer's numbers. No program was shipped, because the WSE-2 port stalls.
- D7 fixed: the noise callout uses our measured examples (16,940 under load; stall aborts) and recommends TSC. The ch09 "±2" wording is not in this chapter (ch09's fixer owns it).
- D8 fixed: WSE-2 vs WSE-3 columns and fits, the "WSE-3 not faster here" sentence, and 850 MHz → ~9.1 µs (sdk + derived tags).
- D9 fixed: memcpy-arguments table, plus the out_rpc.json excerpt for both programs (immutable 0/1).
- D10 applied as a stretch exercise with the SDK pipeline-01 hint; explicitly marked "not measured".
- D11 partly applied: (b)-style extra RPC is covered by the `scale` exercise. Strided DSD and GEMV variants were not added (minor; they would lengthen an already long lab).

## New visuals
1. **SAXPY step-through widget** (#st): 14 steps on 5 lifelines. It highlights the active arrow and the causing line of run.py / pe_program.csl (lines are taken from the validated {{code}} blocks in the page, so there is no second copy). It also has a command-stream pill (free / busy / BLOCKED), a red activation bar, a mini SRAM panel (x, y first four values before/after @fmacs), and a measured cycle timeline with a cursor. Controls: Prev/Next/Play and arrow keys.
2. **Program 02 schedule widget** (#rc): three tracks (H2D stream, 100 measured on_value starts, host/cmd stream with BLK span and D2H read markers), a cycle slider, Play, and a with/without wait_done toggle. The readout gives tasks run, running sum (exact cumsum) and the value the host actually read (26.137941 ✓ vs 30.818176 ✗, with the sum of squares at 96 and count at 100).
3. **Device-vs-numpy diff tables** for both programs, with `<mark>`.
4. Also: a cycles-vs-N log-log chart, and the redesigned streaming/barrier figure.

## Program changes and validation
- 02-wavelet-tasks: comment fix; `@initialize_queue` guarded by `@is_arch("wse3")`; `host_waiting` declared before use. `ARCH=wse3 bash commands.sh` → SUCCESS (7,021). `ARCH=wse2` → SUCCESS (5,423). expected_output.txt regenerated: "[7021 simulated cycles, WSE-3]".
- 01-saxpy: original files untouched. Rerun WSE-3 SUCCESS 7,740, WSE-2 SUCCESS 6,826. New `timed/`: WSE-3 SUCCESS (kernel 143, total 11,010; expected_output.txt written in the same format), WSE-3 f16 SUCCESS (32), WSE-2 SUCCESS (78). `trace_tasks.py` was run on a real trace.
- run_all.sh (copy of the script with 01 and 02 only, in scratch, so programs 03–05 were not touched): wse3 PASS 7,740 / 7,020; wse2 PASS 6,826 / 5,436.
- Program dirs cleaned (no out/, sim*.json, sim.log, simfab_traces, wio_flows_tmpdir.*).
- Page: rebuilt with tools/build.py. Playwright at 1100 and 390 px, light and dark: 0 page/console errors; scrollWidth == innerWidth in all four. Both widgets were exercised (Next ×9 → step 10 shows the @fmacs line highlighted and the pill BLOCKED; Prev/arrow key; slider at 6,000 with and without the barrier gives 26.137941 ✓ / 30.818176 ✗; Play/Pause on both), plus the theme toggle after load. Screenshots were inspected; fixes made: label overlap with the activation bar, the WSE-2 arc label, the SRAM panel width, and the timeline gap. Screenshots deleted.

## Open issues
- The fabric-DSD variant (D6) runs on WSE-3 only, so it is shown as a measured aside.
- D10 back-pressure is left as an unmeasured stretch exercise.
- The exact bank-conflict rule is empirical (it differs between the chips at N=64). The page says "pad and measure".
- Building rebuilds chapters 11 and 12 too (tools/build.py builds all src templates); their content comes from their own src files.
