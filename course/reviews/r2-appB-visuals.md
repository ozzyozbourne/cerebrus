# Review r2 — Appendix B (CUDA to CSL) — visuals + pedagogy

Method: Playwright 1100/390 px, light/dark, ◐ toggle; every Rosetta chip, TT checkbox, every preset on both chips, a stress input. No page/console errors, no page-level overflow, all internal `#` links resolve. Screenshots: `/home/user/cerebras-sdk/tmp/r2appBvis/`.

## Visuals

**V1 (high): the "Measured cost constants" table is 2,148 px wide, so at desktop width only two of its five columns are visible.**
- Location: `#constants`, `.consts`, CSS line 34.
- At 1100 px the `.table-wrap` has scrollWidth 2148 and clientWidth 826. Only "Constant | WSE-3" are visible. WSE-2, Notes and Source sit off to the right, and the only hint is a scrollbar (screenshot `s-1100-light-8.png`). At 390 px it is the same table at 2148 px.
- Cause: `.consts td:nth-child(2), td:nth-child(3) { white-space: nowrap }`. In rows that use `colspan="2"`, the 3rd child is the long Notes cell, so whole sentences (up to 951 px) never wrap.
- Fix: delete that rule, or limit it to short cells (e.g. a `.num` class on the WSE-3/WSE-2 cells of single-span rows only). Give Notes `min-width: 14em`.

**V2 (med): the Rosetta table is about 7,300 px tall at desktop because its first column cannot wrap.**
- Location: `.rosetta td:first-child { white-space: nowrap }`.
- Long labels such as "thread-block clusters, distributed shared memory" and "thread, threadIdx / blockIdx" make column 1 about 355 px wide. That squeezes the main "CSL equivalent, and why" column to about 230 px, so each row runs 8–10 lines (`s-1100-light-1.png`). The page is 14,300 px at 1100 and 20,000 px at 390.
- Fix: drop the nowrap, set `td:first-child { width: 22% }`, and give column 2 about 50%.

**V3 (med): the page has no figure at all; it is three tables and a form.**
- This is a visual course, and this appendix has the facts that most need a picture. Two drawings would help most:
  - (a) A 48 KB memory bar for WSE-3 and WSE-2: code, memcpy runtime, 1 KB task table, user arrays ≈ 44.5 KB. It could be driven by the checker's SRAM row, so the bar fills as you type.
  - (b) A W × H rectangle inside the (W+7) × (H+2) fabric: 1 halo + 3 memcpy columns west, 2 + 1 east, and the offset 4,1. This turns the checker's `--fabric-dims` line into geometry.
- Optionally, add (c) a small three-level ladder: CUDA grid → block → thread → warp beside rectangle → PE → task → DSD op.
- Fix: add (a) and (b) as SVGs that use `cssVar`, following the chapter figures.

**V4 (low): the compile line in the readout breaks inside `--channels`.**
- Location: `#bu-sum`. At 1100 px it renders as "--memcpy -" then "-channels 1" (`bud-p04bad.png`), which reads as a single-dash flag.
- Fix: put the command in its own `<code style="white-space:pre; overflow-x:auto; display:block">`, or use `overflow-wrap: anywhere` without breaks at hyphens.

**V5 (low): the green "OK" pills and Measured tags reach only 4.29:1 contrast at 11.5 px in light mode.**
- Location: `.pill.ok`. Dark mode is fine (8.2:1).
- Fix: darken `--green` text on `--green-soft` for these pills, or reuse the darker tag green from course.css.

**V6 (low): meters at 1/1 (rx ports, fabric inputs, I/O channels) draw as full bars that read as "maxed out".** Fix: show meters only where the fraction means something.

## Pedagogy and usability

**P1 (med): the "25-point stencil's task IDs on WSE-3" preset reports a failure that the real program does not have.**
- Location: `PRE.p25` sets `col: "0-20"`.
- The benchmark routes colors 4–7 as its channels. Its own layout.csl comment map lists 0–26 as *task IDs*, not routed colors. The checker therefore prints "color 20 belongs to memcpy (20–23)" as one of its two failures.
- The preset also forces the chip to WSE-3 silently. Chapter 5 (#budget) says these 18 tasks are "the entire user local-task budget" on WSE-3. The widget says "2 limits broken", with five task-ID errors. A learner who compares the two will be confused.
- Fix: set `col: "4-7"`. Add a one-line caption saying the preset shows why this WSE-2 program does not port to WSE-3 as written (IDs 2, 3 < 8; 24 = memcpy; 25–26 outside 8–20). Change Ch. 5's wording to "more than" the budget.

**P2 (med): presets give no statement of what they are meant to show, and they can change the Chip control without saying so.**
- Location: `#bu-pre`.
- `p04ut` and `p25` set the chip to WSE-3 even if the user had picked WSE-2. Choosing WSE-2 + "Lab 3 · queues 2,3 / 2,3 with .ut_id" silently shows WSE-3 results.
- `p04bad` reports "1 limit broken" but does not point to the explanation in 05-tasks.html#hang-callout or to the fixed presets.
- Fix: add a `<p class="hint" id="bu-note">` filled per preset. Example: "Lab 3's first version: o2/i2 collide on microthread 2 → FATAL at cycle 2,123. Try the next two presets for both fixes (Ch. 5)." Also: "This preset is WSE-3 only; chip switched."

**P3 (med): there is no worked translation of a whole kernel.**
- A CUDA programmer learns fastest from one kernel side by side. The appendix has 33 single-concept rows but never shows `saxpy<<<…>>>` plus `cudaMemcpy` next to program 01's layout.csl, pe_program.csl and run.py. The course already has all three, and Ch. 10's tour covers them.
- Fix: add a short "#saxpy" section with a two-column code block (≈ 12 lines each). Annotate it with the Rosetta row names (grid → `@set_rectangle`, `<<<>>>` → `rt.launch`, `cudaMemcpy` → `memcpy_h2d`, the grid-stride loop → the `@fmacs` DSD extent).

**P4 (med): "Lab 3 is exactly that sum: 90 + 2.5·n" is asserted, but the sum is never shown.**
- Location: the final callout.
- The callout gives "≈ 15 per async transfer" and "≈ 9 per PE hop". The constants table gives a start-up of 15–17 isolated *or* 6 consecutive, plus 14.6 per transfer and 13 of bookkeeping. A learner cannot rebuild 90 from these, or tell which start-up value to use.
- Fix: show the arithmetic. 4 × 14.6 + 13 + 3 × ≈ 6 (consecutive op start-ups) ≈ 89 ≈ 90, and 2.5·n = 0.5 + 1 + 1. Say "use 6 for ops inside one task, 15–17 for the first".

**P5 (low–med): the checker's limits disagree with the budget table right above it, even though the hint says "every limit comes from the table above".**
- (a) WSE-2 local task IDs: the table says "0–30, minus the IDs of colors you receive on". The checker's limit says "≈ 21 (0–20, minus colors)".
- (b) WSE-2 queues: the table says "queue 0 … belongs to memcpy: start at 2". The checker says "7 / 5 (1–7 / 1–5)" and accepts queue 1 silently.
- (c) The data-tasks row always warns on WSE-2 ("on WSE-2 data tasks bind to colors"). As a result, the course's own program 02 preset shows "fits, with 1 thing to check" on WSE-2, although it runs there.
- Fix: make the limit strings match the table. On WSE-2, mark the data-tasks row "ok" with that message as the explanation, not as a warning.

**P6 (low–med): the compile line printed by the checker cannot be pasted for the course programs.**
- It omits `-o out` (run.py expects `--name out`) and `--params`. For example, program 04's commands.sh passes `--params=P:$P,n:$n`.
- Fix: append `-o out`, and for presets add their `--params` (P:8,n:16 for p04/p04bad/p04ut; matching values for 03 and 05).

**P7 (low): the input checks drop errors without telling the user.**
- With `abc,99,21` in "colors you route", only "color 99 does not exist" is shown. "abc" (unreadable) and 21 (memcpy) are hidden because the message is a first-match chain.
- An H of 0 is silently treated as 1, while the field still shows 0.
- Fix: collect all messages, as the local-task row already does, and clamp the field value itself.

**P8 (low): DSR, TSC, rx, `.ut_id`, counter filter, SFPU and CB are undefined on the page.** Fix: link each first use to its `appendix-a-glossary.html#g-…` entry, especially in the budget table.

**P9 (low): "8-wide FP16 SIMD" [Vendor] in the warp row vs 3.2–4 f16/cycle measured is never reconciled.** Fix: one sentence on why the measured rate is about half the width (memory-to-memory operand bandwidth, Ch. 3/6).

## Counts
High 1 · Med 6 (V2, V3, P1, P2, P3, P4) · Low/low–med 8 (V4, V5, V6, P5, P6, P7, P8, P9).
