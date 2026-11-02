# ch11 · fix log

Template: `course/src/11-lab-neighbours.html` (rebuilt with `tools/build.py`). Programs: `course/programs/03-row-reduce/`, `course/programs/05-column-broadcast/`. Experiments: `/home/user/cerebras-sdk/tmp/fix-ch11/` (`rt` CE round trip, `rtr` router-only round trip, `saf` store-and-forward variant, `b2d` 2-D broadcast, `col` collectives_2d reduce, `merge` exercise 4, `sweep.sh`). All numbers come from the SDK 2.10.1 simulator.

## Coordinator notes applied
- **TSC cross-PE comparison.** Every kernel time on the page and in run.py now uses start and end stamps from the SAME PE. The per-hop cost was re-measured as a round trip on PE 0's own clock:
  - Router-only hop: 2.0 cycles on WSE-3, 1.0 on WSE-2. This matches ch04.
  - CE-forwarded hop (@fadds): 9.2 cycles on WSE-3, 6.0 on WSE-2.
  - The old "7 per hop" own-clock step is the CE hop minus one router hop, which fits each PE's clock starting one hop later. That reading is tagged Derived.
  - Widget and text use c ≈ 9 / 6. The page explains the difference between the two hop costs.
- **Notes 22/23 (@fmacs bank clash).** The page's "1 cycle per element" is a fabric-fed @fadds with one memory stream, limited by the link rate. A sentence now says the mod-4 bank clash cannot occur here.
- **Notes 5, 12, 13, 14, 16.** Applied. Totals are host I/O; the kernel is timed with TSC. Task IDs are 9/10/11, inside 8–20. Notes 13/14/16 matter only through the 1 cycle per element statement, which is consistent with them.

## Findings
| ID | Status | Note |
|---|---|---|
| A1 | Fixed | Totals table replaced. New kernel-vs-total table and chart; the empty-reduce() fact is stated; program 03 now times its own kernel. |
| A2 | Fixed | Text and widget both use M + c·(P−1); c measured as 9.2 / 6.0 (round trip); tagged. |
| A3 | Fixed | "Twice" removed. Text says P × M in and M out; kernel 77 → 199 → 588 vs totals. |
| A4 | Fixed | Lede says "one color and multicast routes"; middle vs bottom router stated; caption says R − 1 fabric receivers. |
| A5 | Fixed | gemv-06 to gemv-08, with the wavelet-task and store-and-forward caveats; SDK tag. |
| A6 | Fixed | Caption rewritten (orange/blue/purple/green); no "teal". |
| A7 | Fixed | Exercise 1 hint rewritten; answer says @fmaxs is a drop-in. |
| A8 | Fixed | Every new number tagged; run-to-run variation noted (totals and 05's ±1). |
| P1 | Fixed | "What happens inside, in order" added for both programs. |
| P2 | Fixed | "Reading the code: roles are compile-time params" section. |
| P3 | Fixed | Queue callout (oq 2 / iq 2 safe; one op per PE). A code comment was also added in 03. |
| P4 | Fixed | 05 run.py shown, plus a paragraph on host-side asymmetry, fabin→mem and t_send/t_recv. |
| P5 | Fixed | "When it goes wrong" bug callout (stall abort message, parity, P ≥ 2, wrong PE, bisect). |
| P6 | Fixed | Exercises rewritten, each with hints and an expected result in `<details>`. |
| P7 | Fixed | "Run it yourself" box with P/M/R/ARCH knobs; commands.sh shown. |
| P8 | Fixed | Braces callout corrected: braces are needed only with else. |
| P9 | Fixed | "Two chips, one source" paragraph. |
| P10 | Fixed | One formula throughout (M + c·(P−1)). |
| P11 | Fixed | Bottom router only delivers; the reason is stated. |
| P12 | Fixed | "Try it" pointer to gemv-08 layout.csl. |
| P13 | Fixed | The figure says P = 6 is shown and the program defaults to P = 8. |
| V1 | Fixed | Every input calls reset(), which stops the timer (checked with Playwright: P changed mid-run → 74 rects, Play state). |
| V2 | Fixed | Fixed 30 ms per cycle; both modes on one clock (race). |
| V3 | Fixed | All colours are classes or var() styles; checked live with the theme toggle. |
| V4 | Partial | Uses the shared ≥620 px scroll fix; multicast and GEMV viewBoxes cropped. No phone-specific redesign. |
| V5 | Fixed | 6 rows; host box ("x → root only"); s bracket; root "sends x · y = 1·x"; longer arrows; new caption. |
| V6 | Fixed | Marker arrows; x lines centred; purple x, orange/blue reduction matching fig 1, green b/y; caption. |
| V7 | Fixed | Readout prints the exact formulas with numbers. |
| V8 | Fixed | Colour legend; Play/Pause/Resume, Step, Reset; buffered cells shaded blue in store-and-forward. Role tags were replaced by grid titles. |
| V9 | Fixed | Labels centred on rows (dominant-baseline middle) and thinned at large P. |
| V10 | Fixed | Empty cells have a border stroke; the .btn contrast was already fixed course-wide. |
| V11 | Fixed | recv_c/send_c names, "(P = 6 shown)", coloured c0/c1 labels, green first/last boxes. |
| D1 | Fixed | TSC added to program 03 (and 05); "Measuring the kernel, not the host" section, table and chart. |
| D2 | Fixed | Constant corrected (and re-measured on one clock); the widget has a chip selector (c = 9 / 6). |
| D3 | Fixed | "When a PE is late: back-pressure" paragraph using the depth review's numbers (~16 wavelets/hop, flagged ±2 own-clock). |
| D4 | Fixed | "Timing the broadcast, and a trap" callout. Program 05 itself prints the skew (start_timer → go: 2,610 vs 2,248) and the receivers' 431–439 wait. |
| D5 | Fixed | `<collectives_2d>` section: excerpt, internals, re-measured table (754/818/1,002/1,538 on the root's clock), 1-D gotcha re-verified by compiling. |
| D6 | Fixed | "Going 2-D" worked example: diff, one colour, measured C = 1/4/16 (~78 cycles after root start, every column). |
| D7 | Fixed | Exercise 3 compares kernel spans on both chips; answer includes WSE-2 54/64/84/124. |
| D8 | Fixed | Store-and-forward variant measured (58/154/348/733 at M = 32; 1,024 vs 199 at M = 128); gemv tutorials named as store-and-forward. |
| D9 | Fixed | Walk-through step 5: "left the CE", queued; M ≤ ~16. |

Counts: 40 findings. 39 Fixed, 1 Partial (V4).

## New visuals
1. **N1 race widget** (replaces `#pipe`): streaming and store-and-forward grids on one 30 ms/cycle clock, with chip selector, Play/Pause/Step/Reset, legend, and a done-at badge. Below it, a cycles-vs-P chart: model lines plus measured dots (shown at M = 32), a current-P marker and the ratio.
2. **N2 kernel vs whole-run chart** (`#io`): bars for P = 2/4/8/16 with the kernel segment and its percentage, plus hover titles.
3. **N3 router stepper** (`#rtw`): 4 PEs with routers, stepping through the checkerboard. In one-colour mode it shows the `{WEST,RAMP}→{RAMP,EAST}` route copying raw v0 east and looping the CE's output back.
4. The multicast and GEMV figures were redrawn (V5, V6).

## Program changes
- **03:**
  - `<time>` TSC stamps (`t_start` at reduce(), `t_end` in exit_task) and a `start_timer` RPC; layout exports.
  - run.py launches start_timer, reads both stamps with MEMCPY_16BIT and prints per-PE `t_end − t_start` (same PE) and the last-PE kernel time.
  - Comment explaining queue numbering.
  - expected_output: kernel 101 cycles, `[6861 simulated cycles, WSE-3]` (was 4,748: one more launch and two small reads).
- **05:**
  - Same TSC instrumentation. start_timer is the first command, so all PEs reset at the same point in their command streams.
  - run.py prints start_timer→go and go→done per PE. That exposes the 362-cycle command-stream skew.
  - expected_output ends `[7620 simulated cycles, WSE-3]`.
- commands.sh unchanged in both. Programs 01, 02 and 04 untouched.

## Validation
- `ARCH=wse3` and `ARCH=wse2 bash commands.sh` in both dirs: SUCCESS! on all four runs. The run_all.sh loop body was run for 03 and 05 (PASS on wse3 and wse2: 6,862 / 7,620 / 6,152 / 6,276 cycles).
- 03 output matches expected exactly. 05 differs by ±1 cycle in two TSC numbers between runs (host-timing dependent skew); this is noted on the page.
- Sim outputs cleaned from both program dirs.
- Playwright, 1100 px and 390 px, light and dark: no page or console errors, 0 px horizontal overflow (after wrapping one long inline command). Widgets exercised: stepper both modes, race play, slider change mid-run, run to completion, live theme toggle. Screenshots inspected, then deleted.
- `build.py` also rewrites ch10 and ch12 from their own src (unchanged by me).

## Open issues
- WSE-2 round trips have a ~90-cycle floor for P ≤ 8, so the WSE-2 hop cost is fitted from P ≥ 12 only.
- "Each PE's clock starts one router hop later" is an inference that fits the numbers (Derived), not a direct measurement.
- The back-pressure numbers (D3) are the depth reviewer's per-PE own-clock readings; I did not re-run them.
- The widget models leave out the fixed ~20 cycles, and store-and-forward is modelled as M + 2c per hop (≈ 5% above measured).
- V4: on phones, figures rely on the shared horizontal-scroll fix.
