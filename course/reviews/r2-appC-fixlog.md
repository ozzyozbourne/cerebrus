# Fix log r2: Appendix C (Measuring and observing)

Files edited: `course/appendix-c-measuring.html`, plus one sentence in `course/18-comparison.html` (A3).
Inputs: r2-appC-accuracy.md, r2-appC-visuals.md, build-appendix-cd.md.

## Re-runs this round (SDK 2.10.1 simulator, scratch /home/user/cerebras-sdk/tmp/fix2-appC, now deleted)
Course `01-saxpy/timed`, 1 PE, N = 256 f32, PAD 1:
- WSE-3 traced: TSC 271, cycle_count 21,515, 239,709 lines / 17.6 MB. Every quoted trace line reproduced at the same cycle (FMACS @3630→@3885, stamps @3619/@3890, `T01 3353-4113 (761 cyc, 510 instr)`).
- WSE-2 traced: TSC 270, cycle_count 31,645, 342,988 lines / 21.4 MB. Stamps 4 and 0x112 as before, but the whole kernel came **one cycle later** (FMACS @4157→@4412), so absolute stamps are not fully repeatable. Differences are.
- `[IS OP]` lines: Pipe 3 (WSE-3) / 2 (WSE-2); `[EX OP]` lines: Pipe 6 / 4. EX follows IS by 3 / 2 cycles, and the same `Instr` number ties them together. Lines read `... Pipe: 6, Msg: [EX OP] | ...`. The widget now shows the `Msg:` field.
- Empty TSC region (the `@fmacs` deleted): **10 cycles** on WSE-3, PAD 0 and 1.

## Findings
| ID | Sev | Action |
|---|---|---|
| P1 | high | Fixed in all four places. Instruments row 1 is now "end-to-end cost of a host program, nothing finer". Row 2 now carries the slope method. The §1 paragraph now says Lab 3 takes the TSC slope between 10 and 100 steps and divides by 90, links 13-lab-stencil.html#tsc, and quotes the 5,260 vs 8,905 cycle_count counter-example. Chart R[0] drops the differencing and warns against it with a link to the Ch 13 callout; R[1] now carries the slope. The Q1 answer now says to compare the TSC. Method box subtitle is "whole run only". |
| P2 | med | §3 now opens by linking 11-lab-first-programs.html#trace and calling this section the reference. |
| P3 | med | Every "note N" was removed. Links now carry anchors: 10#sim-outputs, #hangs, #stdlib, #builds, #debugging; 11#kernel-time, #noise, #trace, #wavelet-tasks; 12#measuring, #hop-cost; 13#tsc; 06#collisions; 15#profile, #scaling. Ch 18 is no longer cited. Recipes in the readout are HTML, so they hold links. |
| P4 | med | Added the `#nest-svg` figure. Top: the whole run (0 to 21,515, with a faded continuation to 29,368). A zoom of the RPC shows three tracks: T01 761, TSC 271 and FMACS 256, with ticks for enable_tsc, t0, t1 and UBLK and the 15-cycle split. It is drawn with cssVar, so both themes and ◐ work. |
| P5 | low | Defined at first use in the noise hint ("one padding word between x and y") and in the worked-example intro (`N HALF PAD`, HALF = 0 is f32, PAD shifts y). |
| P6 | low | Added quiz Q4, on stamp decoding: 1,163,936,137,216 = 271 × 2^32 means the words were joined in the wrong order. Q3 already tests Seq spacing. |
| P7 | low | The lede now links Appendix A for TSC, RPC, H2D/D2H and DSD. |
| V1 | med | `#flow-svg` is hidden at ≤680 px; the chips and readout carry the interaction (checked at 390 px). |
| V2 | med | Q2 is now "How long does a multi-PE phase take?" with the subtitle "Across PEs, or one hop". getBBox overflow check: none. |
| V3 | med | Rebuilt the chart with 8 runs: builder 1–5, reviewer 6–7 (24,763; 25,258 traced), revision 8 (21,515 traced). The baseline is now the median. Each dot is labelled with its run number, overlapping dots stack vertically, and traced runs are drawn pale and dashed. The TSC row is annotated "N runs, all 271 cycles". Ticks are data-driven (min, median, max, with absolute values). The readout lists every run. |
| V4 | low | One figure everywhere now. Untraced kernel share is 1.1–1.3 % (table, pitfall 1, widget readout computed from the runs shown). |
| V5 | low | Added a `mark` style (accent-soft, text colour) and a legend: "Highlighted: the unpadded layout…". |
| V6 | low | The instruments table becomes stacked cards at ≤680 px, with `data-l` labels. The worked table now has a nowrap first column and a min-width of 780 px, so it scrolls inside `.table-wrap` instead of crushing. |
| V7 | low | Excerpt spacing normalised (`Seq:   0,` padded, opcodes padded to one column). `.hl` is `display:block` inside a `min-width:max-content` code block, and the newline sits inside the span, so there are no blank lines. |
| V8 | low | `.root` is exempt from fading. The SVG role is now `group`. |
| V9 | low | The widget hint says the excerpt drops Id/Instr/Pipe/Msg and that the trailing `[ x ] U0` marker is left out. |
| A1 | med | Same-PE callout rewritten: each counter is zeroed when that PE calls `enable_tsc()` (random before that on hardware), so the offset is when each PE enabled, on simulator and hardware alike. That is also why `time_ref` exists. Pitfall 3 and quiz Q2 remain correct. |
| A2 | med | Instruments row now reads "a few percent to about 40 %". R[0] says the same and drops "Expect a few percent". The worked table now gives every run, labelled with run counts, in untraced and traced columns. Data: 21,515–29,368 (WSE-3 PAD 1); 22,126 vs 31,193 (WSE-3 PAD 0, +41 %). |
| A3 | med | Appendix C now says "largest grid … 16 × 16 = 256 PEs (Lab 5, Chapter 15 #scaling)". In 18-comparison.html, "(we simulated at most 16 PEs)" became "(the largest grid we simulated was 16 × 16 = 256 PEs, in Lab 5)", with a link. Nothing else in Ch 18 was touched. |
| A4 | low-med | Now "230,000–345,000 lines (17–21 MB) on either chip". It also says that size scales with total simulated cycles × PEs, IDLE lines included. Updated in §3, R[3] and pitfall 8. |
| A5 | low | New §3 paragraph on IS/EX lines, Pipe values, the IS→EX latency, the Instr pairing, DSD loads printing two lines, and "grep `EX OP`" (257 vs 256). The widget's Pipe and Instr explanations now give the observed pattern. |
| A6 | low | Worked-example bullet lists the 15 cycles: 5 + 2 + 3 + 4 + 1. **Partly disagrees with the reviewer:** the measured empty region is 10 cycles, not 5–6, so subtracting it leaves 261 = 256 + 5 (DSD loads and fill, which belong to the op). Pitfall 6, R[1] and instruments row 2 updated to match. |
| A7 | low | The excerpt now says lines and fields were omitted. Added the interleaved t0 stores, a note that each DSD load prints two lines, and comment lines for IDLE @3627–3629, the NOPs @3886–3889 and the copy @3893–3901. |
| A8 | low | Replaced "about 21,700". The traced runs ran the RPC at identical cycles yet ended at 21,515 vs 29,368, so the noise arose after the kernel. Untraced runs: 21,631–24,763. |
| A9 | low | The ncu row now says it locks to base clock by default and that `--clock-control none` gives boost clocks. |
| R1 | low | Two bullets added: `disable_tsc`, `reset_tsc_counter`, `get_perf_cntr(&t, 0|1)` (what the counters count is undocumented); and `<timer>` (start/stop/elapsed, on-device `subtract_timestamps`). Neither is used by any SDK example. |
| R2 | low | Lab 5's per-phase PROFILE is linked from §2 (including its 7–10 % cost) and from the multi-PE recipe. The conjugate-gradient/run.py SDK tag was added; I verified the same time_ref correction there. |
| R3 | low | Done (see P3). |

## Validation
Playwright at 1100 and 390 px, light and dark, ◐ toggled at each, clicking every chip, every SVG question box (plus Enter on a focused box), the noise checkbox both ways, all 12 trace-line fields and all quiz items. Results: 0 page and 0 console errors; no horizontal overflow (a long two-file SDK tag caused 27 px at 390, so I split it); no SVG text outside its viewBox; no question text past its box. I inspected screenshots of the flow chart, noise chart (both states), nested figure, trace excerpt, both tables and the trace widget.

## Open issues
- CROSS_CHAPTER_NOTES 19, and the Ch 13 / Ch 18 / Appendix A wording "each PE's counter starts when the launch reaches it", should get A1's nuance (zeroed at that PE's `enable_tsc()`). These are outside my scope and were not edited.
- BUILD_BRIEF's "Whole-run cycles are noisy (+1–4%)" understates the noise: this page now documents up to ~40 %.
- WSE-2 trace stamps shifted by one cycle in one rerun. Any page that quotes absolute WSE-2 `@` cycles should treat them as ±1.
- What `get_perf_cntr` counters 0/1 count is not documented in csl-libs (left undocumented on the page).
