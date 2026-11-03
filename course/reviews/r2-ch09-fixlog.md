# R2 fix log · Ch 9 "From model to tokens" (09-model-to-tokens.html)

Only `course/09-model-to-tokens.html` was edited. Inputs: r2-ch09-{accuracy,pedagogy,visuals,depth}.md, build-ch09.md, CROSS_CHAPTER_NOTES 1–26.
Validated with Playwright at 1100 and 390 px, light and dark, plus the ◐ toggle. Every control of kp, pd, cap, lb, sv and sd was driven, including extremes, an empty base and a negative base. Result: 0 page or console errors, and scrollWidth equals the viewport in every case. I inspected screenshots of every widget. Scratch dir deleted.

## Priority items
1. **GEMV rate (A1, A4, D1, P10).**
   - The experiment callout now says that 7.5 B/cycle (~4 f16 MAC/cycle) is this AXPY kernel's limit, not the chip's. HC2024 gives 8-way f16 SIMD (Ch 3).
   - Plausible reason [Derived]: each MAC reads a weight and an accumulator. 16 B/cycle of reads ÷ 4 B = 4 MAC/cycle, and the measured 7.5 is 94% of that. Weights can use only the read bandwidth. A kernel with partial sums out of SRAM could reach ~15 B/cycle [Unverified]. The callout also notes these are simulator figures.
   - The "24 B/cycle HC22 port peak" option is gone. It was replaced by "15 B/cycle · 8-wide f16 SIMD (not demonstrated)".
   - The single-user bound is restated as **~2,000 (measured kernel) to ~4,000 (8-wide)**. The 7,500 headline is flagged as an overstatement, because 21 PB/s counts every port, writes included.
   - Per-layer conclusion: "between about half (8-wide) and all (measured) of the per-layer budget". Quiz Q5 and the 84 PB/s question are qualified to match.
   - The cap widget gains a third wafer row, "8-wide f16 (not shown)" (70B: 7,359 / 2,011 / 4,021 tok/s). The readout says "region's kernel rate (weights use only the read ports)".
2. **"Kernel streaming rate did not change" (A2, D2).** The history closing paragraph is rewritten. Only the clock did not change. The kernel rate is a lever: MatMul was rewritten, and there is up to ~2× to gain. What-if B now uses the 8-wide rate.
3. **Speculative decoding (D3, P4, A8, D9).**
   - New paragraph, "The draft is not cheap on a wafer". A draft's per-layer collectives and hops are latency, so on the wafer c ≈ 0.15–0.4 (likely 0.3–0.4). With c = 0.35, α = 0.8 and k = 4 the speedup is ≈ 1.4×, against 2.7× for a GPU-style c = 0.05 [Derived/Unverified mapping].
   - The formula block now has a separate wafer line. The text states that the formula assumes pipelined verification, and that batching the k + 1 positions inside a region costs ~(k+1)×.
   - The k-wide argument now leads with structure (each weight feeds k + 1 MACs, and there are no idle FLOPs). The measurement is now supporting evidence, with an explanation of why its k = 1 variant (5,648) differs from the table's 5,228.
   - `#sd` has separate draft-cost sliders for the GPU (default 0.05) and the wafer (default 0.35).
   - `#lb` replaces "accepted tokens/pass" with k, α and c. A round = draft (k·c·trip) + trip + k stage-times, and per token = round ÷ E. The bars show "extra positions" and "draft model" segments.
   - Quiz Q7 is rewritten: GPU 2.8×, wafer 1.4×, and why c differs.
4. **Missed occupancy insight (D4).**
   - New paragraph, "What it costs the system, and when it is nearly free". KV limits the deployment to ≤ ~13 users at 8K (~7 after code). That is ≤13/80 slots without speculation, and ≤65/80 (≈35) with k = 4. Speculation therefore uses idle slots and is nearly free system-wide. It costs throughput only when the pipe is full.
   - A draft on the same wafers eats KV SRAM.
   - Aggregate throughput is ≤ ~27,000 tok/s per 4 × CS-3 at 8K, against the 600k ceiling. This figure is also added to the "cheap per token" callout.
   - New quiz question on this.
5. **Placement toy (V1, V2, V6, V7).**
   - Memory-mode L5/L6 figures were lowered (9,792 / 5,760 KB → 17 / 10 columns). Minimum widths are now 38 + 47 columns, so the graph order fits.
   - `balance()` is packing-aware. It shrinks the column whose cut raises Δt least until the packing is legal, then hands spare columns to the slowest kernel that can still grow. If no legal placement exists, it says so ("press Graph order"). Memory mode in graph order: Δt 152, 92% of cores used.
   - While illegal: Δt and throughput show "—", "cores placed" counts only kernels that fit, and no bottleneck highlight is drawn. This also covers the illegal score in compute mode.
   - The overflow tray is squeezed to the fabric width, so L6 is no longer clipped.
   - Labels moved to the top third of each rectangle. Wires run in the lower part, and their vertical leg is offset right of the labels.
   - `.kgrid` uses minmax 250px and nowrap. Slider values are shortened to "N col" (cores are shown in the tooltip).
6. **lb presets / text (V3, V4, V5).**
   - Both presets set ctx = 8K plus all speculation inputs.
   - Text: A ≈ 1,986 µs (~500 tok/s). B ≈ 428 µs ≈ 2,335 tok/s, "just above the published 2,100–2,314". Without the 8-wide kernel B gives 609 µs (~1,600 tok/s); without speculation, 588 µs (~1,700 tok/s). These match the widget readouts in Playwright.
   - Value labels moved into the left label column, so they no longer collide with the dashed lines. Published-speed labels sit in a strip above the bars. The legend wraps, and the viewBox height adapts.

## Medium/low items
- **SRAM budget (P2, A7, D5):**
  - Weights are 38.9 KB per PE: 81% of 48 KB and 88% of the ~44 KB usable. That leaves ~9 KB raw, or ~5 KB after code (88% → 89% after the note-13 update to ~4.2 KB).
  - KV section: ≤ ~13 users is an upper bound. After ~4.2 KB/PE (note 13 updated: SAXPY 4,240 B) × 3.6 M PEs ≈ 15 GB of code, ~21 GB remains: ~63k tokens, or ~7 users at 8K. Quiz Q3 matches. The Ch 10 #memory link has been added.
- **"~18,000" sentence (A5, P3):** deleted.
- **"note 22/19" references (P1):** replaced with links to Ch 6 #collisions and #op-speed, Ch 12 #hop-cost, and Appendix C #tsc.
- **Terms (P10):** Δt is defined in prose before convperf. LAIR/XLA, WSE-3T (with a Ch 2 reference) and AFD are now glossed.
- **405B halving (A3):** the KV read adds only ~6% per layer (0.41 GB vs ~6.4 GB). The cause is unpublished. Candidates are listed [Derived/Unverified].
- **Collectives (A6, D6):** "at least 8" collectives, with norm, softmax and hand-off counted as ~12–14 realistic. 212 hops is one dimension or a centred root; corner-to-corner is ~424. The default is marked optimistic. Each cycles-per-hop value now has its provenance and a forward link (P5).
- **4-bit (D7):** described as a capacity gain, not a speed gain, in the precision paragraph and in a new quiz question.
- **Sequential dependency (D8):** a new bullet in "Two ceilings".
- **Sparsity (A10, D10):**
  - Relabelled as the streamed-weight packet format of Ch 8.
  - 50% is the break-even only with 16-bit indices. With a bitmap it is ~6%.
  - Gather cost is ~33–35 cycles per DSD step (Ch 6).
  - The quiz answer is qualified to match.
- **KV transfer (D11):** 2.7 GB at 300 GB/s takes ~9 ms (≈19 tokens at 2,100 tok/s). The reviewer's "several hundred tokens" was wrong. Added to the prose and to a new disaggregation quiz question (P8).
- **Provenance (A11):**
  - Kimi "~20 CS-3" is now tagged Press + Unverified, in both the precision paragraph and the history table.
  - LPX now reads: 256 per most reports and NVIDIA pages, one report 128, which looks like an error (Ch 17), tagged Vendor via secondary.
  - CS-4 row: the Unverified tag now covers only the >4,400 tok/s claim, and the quote is tagged Vendor.
- **476 µs (A12, P7):** now "per output token" and "implied by the published 2,100 tok/s". Note that one trip may take longer under speculation.
- **A9:** the four-hop interpretation now reads "Presumably …" and is tagged Derived.
- **A13:** "~1,600 cycles", described as about half of router-speed collectives.
- **Quiz (P8):**
  - Added: compile path "match", the occupancy question, 4-bit, and disaggregation.
  - Q3, Q5, Q7 and the 84 PB/s and sparsity answers are updated.
  - There are now 13 questions.
- **MoE presets (P9, V9):** buttons are now "120B dense" and "1T dense". The hint says these are dense Llama-3-shape models and not gpt-oss or Kimi, that layer counts above 405B are extrapolated, and points to the MoE section.
- **Optional exercise (P6):** now labelled "come back after Lab 3 (Ch 13)". It names what it needs, explains the round-trip TSC hint with links, gives an expected result (≈ sum of GEMV times + hop cycles, second user within ~1%) and names the starting files.
- **Recaps (P11):** "Where we are" notes added at the top of the budget and history sections. The GPU comparison is moved into its own callout.
- **SDK table (P5):** glosses added for chain reduce (M, P), ghost exchange, SUMMA and `<collectives_2d>`. The f16 rate is now "~4 elements/cycle (WSE-3)".
- **sd (V10, V11):** an empty or out-of-range base is clamped to 10–10,000, written back on change, and noted in the readout. The slot-share curve is drawn thinner, and the readout notes when it coincides with the wafer curve.
- **New visual (V "missing 1"):** `#sv`, "Verification through the pipeline". It is a 16-stage Gantt with k ∈ {0, 2, 4} and users ∈ {1, 2, 3}, showing k + 1 positions entering one stage apart, the +k stage-time marker, and idle slots. The readout gives occupancy, pass length, E, and the 80-stage/13-user figures.

## Not done / why
- **V8 (kp side panel off-screen at 390):** optional per the brief. The readout already names the bottleneck.
- **Missing visuals 2 and 3 (speed-history chart, sparsity break-even plot):** not added. The table and prose carry them, and the page is already long.
- **P11 length:** the page grew (about 9,100 words in main, widget text included) because the priority content was added. The recaps and the split callout help, but a future pass could trim the history table or move the SDK mapping elsewhere.
- **The read-port explanation** of the 4/cycle f16 rate is a hypothesis, tagged Derived/Unverified. It uses HC2022's WSE-2 port widths for WSE-3. It does not explain why WSE-2 reaches only 2 f16 MAC/cycle. It was not re-measured this session.

## For the coordinator
1. **CROSS_CHAPTER_NOTES 25:** restate the single-user bound as a range.
   - It is **~2,000 tok/s at the measured f16 kernel rate** (7.5 B/cycle/PE ≈ 4 f16 MAC/cycle, an AXPY read-port limit of this kernel form, simulator) **to ~4,000 at WSE-3's 8-wide f16 SIMD** (15 B/cycle, not demonstrated).
   - The ~7,500 headline figure overstates, because 21 PB/s counts every SRAM port, writes included, and weights can use only the reads.
   - Per layer, GEMV is half to all of the 5,060-cycle budget.
2. **Ch 18:**
   - l.197: "~2,000 at the measured SDK matrix-vector rate" → "~2,000–4,000 at a region's GEMV kernel rate (measured vs 8-wide SIMD)", plus the headline-overstatement caveat.
   - l.380 (quiz): add the same range.
   - l.78 and the remaining "not bandwidth-bound" / "pipeline latency, not bandwidth" wording (reviewer P3 cites l.216/380/498): align to "per-region SRAM reads at the kernel rate (a sequential-dependency bound) plus latency/communication".
3. **Ch 1, l.173:** "~7,500 … about 3× the measured speed" → add that at a region's kernel rate it is ~2,000–4,000. Check what follows "At the rate a r…" for the same range.
4. **New cross-chapter note (speculation on a wafer):**
   - The draft is latency-bound, so on the wafer c ≈ 0.3–0.4 (range 0.15–0.4). With α = 0.8 and k = 4 the speedup is ≈ 1.4×, against 2.8× on a GPU (c = 0.05).
   - Verification is pipelined (+k/S), not batched in a region (~(k+1)×).
   - At 8K, KV limits a 4 × CS-3 Llama-70B deployment to ≤ ~13 users (~7 after the ~4.2 KB/PE code overhead), so ≤13 of 80 pipe slots are busy and speculation is nearly free system-wide.
   - Aggregate throughput is ≤ ~27,000 tok/s per 4 × CS-3 at 8K.
   - Ch 18's cost discussion could use the last two points.
5. **New note (KV capacity):** 4 × CS-3 Llama-70B leaves 36 GB raw, which is ≤ ~110k tokens (~13 users at 8K). After ~15 GB of code and task tables (4,240 B/PE) it is ~21 GB, ~63k tokens, or ~7 users. Any chapter that quotes "13 users" should say "at most".
6. **New note (precision):** native 4-bit with 16-bit compute is a capacity gain (wafers, KV), not a per-token speed gain.
7. **New note (405B):** the 969 → 539 tok/s drop at 100K context is not explained by KV reads in the budget model (+~6% per layer). Ch 8 and Ch 18 should not attribute it to attention bandwidth.
8. **Appendix A glossary:** consider entries for LAIR, AFD (Attention-FFN disaggregation), and "draft cost c". **Appendix B/E:** the f16 GEMV constants (7.5 B/cycle WSE-3, 3.8 WSE-2) and the 8-wide option.
9. **Ch 17:** consistent with Ch 9 now (LPX 256, 128 likely an error). No change needed.
