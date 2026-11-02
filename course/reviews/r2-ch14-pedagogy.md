# Review round 2 — Chapter 14 (Lab 4: 2-D GEMM with SUMMA), pedagogy

Source reviewed: `src/14-lab-gemm.html` (generated `14-lab-gemm.html`), `programs/06-summa/*`. Cross-links checked against
chapters 4, 5, 6, 10–13. Overall: the order works (algorithm → layout → library internals → join → code → measurement →
design method → scale → exercises), the join and teardown explanations are clear, and most quiz answers are right. The
main problems are exercises whose answers are printed in the body first, two thin spots in the quiz coverage, a long
reduction digression in the wrong place, and several wrong chapter pointers.

## Findings

**P1 — med — Exercises 4 and 5 are answered in the body before they are asked.**
The callout "Where the other two-thirds go" gives the whole Mt sweep (45.4/60.9/92.4 vs 49.9/52.4/72.4 cycles per
`@fmacs` for Mt = 8/16/32 vs 15/17/33) and the whole bank-clash fix story (pad C → 13,739 vs 17,835; merge A arrays;
4,096 cycles saved; 70,956 at T = 32). Exercise 5 then asks the learner to run Mt = 15/16/17, and exercise 4 asks them to
"predict before and after" — nothing is left to predict or discover.
Fix: in the callout keep the mechanism and one data point (e.g. Mt = 8 vs 15), and move the sweep and the step-by-step
fix (half-fix, then merged A array) into the exercise answers. Or relabel these two as "reproduce" exercises, not "predict".

**P2 — med — Exercise 5's question ("Which is fastest per multiply-add?") is not answered, and the answer implies the wrong one.**
The answer compares Mt = 16 with Mt = 15 only. Per multiply-add the numbers given are 3,192/(15·64) = 3.33,
3,896/1,024 = 3.80 and 3,352/(17·64) = 3.08 cycles, so **Mt = 17 is fastest**, then 15, then 16.
Fix: state "Mt = 17 (3.08 cycles/MAC), then 15 (3.33), then 16 (3.80)". Also give the full command
(`P=2 T=8 Mt=15 bash commands.sh`) like the other exercises.

**P3 — med — Exercise 4's solution is incomplete for a learner who follows it.**
The expected result shows only the `compute` pointer change for `A_both`. `start_step()` also chooses `&A_tile`/`&A_buf`
as the broadcast source/destination, the `A_dsd` template names `A_tile`, and the exported `A` pointer must now point at
the first half of `A_both`. A learner who changes only `compute` sends from the old arrays and gets a wrong C.
Fix: list all four edits (declaration, `A_ptr` export, `start_step`, `compute`), or ship the fixed variant as a knob
(e.g. `PAD=1`) and let the exercise diff it.

**P4 — med — The quiz does not test two of the five objectives.**
Objective 1 (2-D host I/O: reshape/transpose wire order) and objective 5 (budgeting: memory, colors, task IDs, queues)
have no question. These are exactly the skills a learner reuses in Lab 5.
Fix: add (a) "With ROW_MAJOR order, which PE's tile is the third block of the host array, and why must each tile be
column-major here?" and (b) "Why does the color count stay at 4 for any P, and which task ID must you never bind?"

**P5 — med — "Chain or tree?" callout is a reduction digression placed inside the broadcast section.**
It sits right after the teardown explanation, introduces a new cost model (c ≈ 9/hop, ≈ 15 cycles per store-and-forward
message, tree wire 2·P, a crossover inequality) and three back-references, then ends with "SUMMA itself needs no
reduction". A learner who has just absorbed the library FSM has to switch topics and absorb a model that this lab never
uses. Exercise 6 then re-derives it with slightly different terms (2·(P−1) vs 2·P).
Fix: move the callout after "Scaling up" (or into Ch 15), keep only one sentence in the library section ("broadcasts here
are chains; when a tree wins is a reduction question, see exercise 6 / Ch 15"), and use the same tree formula in both places.

**P6 — med — Wrong chapter pointers.**
- "From GEMV to SUMMA": link to `12-lab-neighbours.html#row-reduce` lands on Program 03 (row reduction). The GEMV is at `#composing` ("Composing the two: a distributed GEMV").
- Exercise 3 hint: "Chapter 10's rule of thumb leaves about 44 KB". The 44 KB figure is in Ch 3 (and confirmed in Ch 11); Ch 10 has no such line.
- `layout.csl` resource-map comment: "colors 20-23 belong to memcpy and the runtime, Chapter 4". The reservation of colors 20–23 is stated in Ch 10 ("Keep clear of memcpy's resources: colors 20–23"), not Ch 4.
- Design section: "using the budgets from Chapters 4, 5, 7 and 10" — the memory budget is Ch 3/11; consider "Chapters 3, 4, 5, 7 and 10".

**P7 — low — "With Mt = 8 that alone is about 80% of the instruction" does not match the numbers beside it.**
At T = 8 an instruction costs 2,903/64 = 45.4 cycles, of which the fixed part ≈ 29 is 64%. 80% is only true against an
unclashed 8-cycle body (29/37). Fix: "about two-thirds of the instruction (29 of 45 cycles)".

**P8 — low — Kernel-1 ablation numbers and its fit do not add up, with no comment.**
The callout gives `@fmuls` ≈ 1.6 and `@fadds` 0.5 cycles/element on WSE-3 (sum 2.1), 1.35 + 1.0 on WSE-2 (2.35), but the
fit above says 1.87 and 2.0 cycles/element for the pair. Quiz 7's answer then explains the WSE-2 gap using only
`@fadds`, although `@fmuls` is faster on WSE-2. A careful learner sees the mismatch and has nothing to resolve it with.
Fix: one sentence saying the ablations were run alone (each op pays its own start-up and runs without the other's
overlap) so they over-estimate the pair, or quote the per-op costs measured inside the pair. In quiz 7 add that
`@fmuls` is slightly faster on WSE-2, which offsets part of the `@fadds` gap.

**P9 — low — Undefined or unexplained terms in the library walk-through.**
"FSM" (never expanded), "CE-ignore bit", "TIP bit" (in a quoted comment), and "DSD-register set" / `dest_dsr_ids`
(the library params in `pe_program.csl`) appear without a definition or a link. Ch 4 covers teardown and task 29, Ch 6
the DSRs, but the page does not point there for these. Fix: expand FSM ("a small state machine task"), gloss the
CE-ignore bit in a clause ("so the PE's own CE does not receive it as data"), drop or gloss TIP, link DSRs to Ch 6.

**P10 — low — Quiz 2 answer says "keeps it to two colors per axis", but broadcast uses one.**
The body says color 1 is only for `reduce_fadds`. Fix: "one color per axis for the broadcast (the library reserves a
second for its reduce)".

**P11 — low — Index-order trap is not flagged.**
"PE (px, py) owns block (py, px)" swaps the order, and the widget readout, figure and code all rely on it. This is the
most likely source of a wrong C in a learner's own 2-D program. Fix: a one-line warning after the ownership sentence
("PE coordinates are (x, y) = (column, row); matrix blocks are (row, column)").

**P12 — low — "Pad and measure" leaves the learner unable to check alignment.**
The half-fix result ("the two A arrays sit at different alignments") cannot be predicted from the declaration order shown
(A_tile, B_tile, C_tile, A_buf are all multiples of 4 words at T = 16). Tell the learner how to see the actual addresses
(e.g. the ELF symbol table of `out/bin/out_*.elf` via the SDK's readelf/`nm`, or reading `&A_buf` at run time into an exported
word) so the clash can be reasoned about, not only measured.

**P13 — low — Exercise 1 broadcast explanation contradicts the measurement section without saying so.**
The findings say the two broadcasts "do not overlap fully" (time grows with the sum of both tiles); exercise 1 explains
717 < 792 by "the small B transfer overlaps the large A transfer". Both are consistent with the partial-overlap
observation, but the learner is not told that. Fix: "(the partial overlap noted in the findings: for very unequal tiles
the small one hides behind the large one)".

## What works well (keep)
- SUMMA derivation from the GEMV and the "rank-K/P update" framing; the Nt = 1 batched-GEMV bridge.
- Four-step "one broadcast, end to end" list and the teardown/back-pressure paragraph.
- The join explanation and "why not count" contrast with Lab 3.
- Nine-step design table tied to this program; the calculator makes it concrete.
- Quiz answers 1, 3, 4, 5, 6 are correct and test the right ideas; exercise 2, 3 and 6 numbers check out
  (e.g. ex 6: chain 208/9,218, tree 310/2,332).

## Counts
High 0 · Medium 6 (P1–P6) · Low 7 (P7–P13).
