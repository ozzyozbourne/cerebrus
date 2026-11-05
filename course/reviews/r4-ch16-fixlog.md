# r4 fix log · ch16 (16-tenstorrent.html)

Inputs: r4-ch16.md, r3-gaps-ch16-17.md (items still open), CCN 30–38, grep of all r4-*.md (only Ch 1 E5 also touches the Ch 16 numbers; handled under "For other pages"). Web: tt-metal `tech_reports/LLMs/llms.md` and `AdvancedPerformanceOptimizationsForModels.md` fetched (for X5). No simulator runs.

## Errors
- **E1 Fixed.** #scale-out: per-chip ratios (BH 1.7× NoC link / 10× DRAM; WH 2.6× / 23×) plus the latency ratio (515–711 ns vs a 7–9 ns NoC hop ≈ 80×), all [Derived].
- **E2 Fixed.** Peak bullet now gives ~640 TF BFP4/LoFi (5120×6656×6656) ≈ 89% of 719 TF [vendor-measured], with 581/81% noted as the report's prose figure. The #matmul closing paragraph says utilisation is measured at the run's own fidelity (the ~95% runs are HiFi4 at ~160 TF).
- **E3 Fixed.** Both 13 × 10 mentions say "run before the 2026 core cut".
- **E4 Fixed (this page).** Footnote under the 70B table: 72.5 × 32 = 2,320, and 2,269 implies ~70.9. The #performance bullet points to it. The Ch 1 alignment is listed under "For other pages".
- **E5 Fixed.** "selects a route that is configured at compile time (and can be switched at runtime by control wavelets)", linked to Ch 4 #runtime.
- **E6 Fixed.** The matmul widget divides ideal cycles by used_x × used_y. The hint and the readout say so (M = 256 on 13 × 10 → 104 busy cores).

## Explanation problems
- **X1 Fixed.** Forward links to #tensix from the formula callout and the table caption, plus a glossary link for fidelity.
- **X2 Fixed.** The caption links App A #g-blockfp8, and the on-page glossary box has a new BFP8/BFP4 entry.
- **X3 Fixed.** Linked VC (with a one-clause definition and the analogy to a Cerebras color), all-reduce, TP, TTFT, replica (→ g-tp-pp-dp) and TT-Fabric. App A has no entries for Go-Back-N or bubble flow control, so both are defined inline.
- **X4 Fixed.** Worked fidelity example: 8 significant bits; LoFi uses 5 × 7; a 2 × 2 slice split gives 4 partial products, so HiFi4 = 4 × 16 cycles [Derived].
- **X5 Partly.** Added the LLM report's own figure ("about 10 ms per decode pass with microsecond-length ops", [vendor]) and a derived ratio of ~1,000 ops → ~10 µs/op. The op count per layer is labelled as our assumption. No vendor number for host dispatch time per op was found, so none is quoted. Linked g-trace-replay.

## Connecting gaps
- **G1 Fixed.** The page went from 0 to 65 links: every chapter/lab mention, App A terms on first use, a "See also" line in #matmul (Lab 4, Ch 17 #tiling) and in #70b (Ch 9, Lab 5 #allreduce). All anchors were checked and resolve.
- **G2 Fixed.** New table row "Peak math per unit per cycle": PE 16 FLOP [vendor] or ≈ 8 measured; Tensix 4,096 LoFi. A paragraph after it gives ≈ 256 PEs (≈ 512 measured) in math against ≈ 32 PEs in memory [Derived].
- **G3 Fixed.** "Does SRAM remove the limit?" adds a two-row table: Galaxy 124 → 72.5 (bandwidth) against 4 × CS-3 ~2,000–4,000 → 2,100/2,314 (per-region reads plus an 80-layer latency chain). It links Ch 1 #calc and Ch 9 #budget. The quiz answer says the same.
- **G4 Fixed.** New paragraph in #vs-pe: 4 B over 5 hops on BH = 57 cycles; a 2 KiB tile = 88 cycles (23 B/cycle); on the wafer ~10 cycles at 2.0/hop with no header [Derived/Measured]. It notes that the two clocks differ.
- **G5 Fixed.** Two new rows in the CSL↔Metalium table (input queue + back-pressure / @allocate_fifo ↔ CB; collectives_2d ↔ multicast + semaphores). After the CB paragraph, a sentence covers queue depths 6/4/2 [SDK] (CCN 35) and links Ch 4 #back-pressure and Ch 6 #fifos.
- **G6 Fixed.** Paragraph after the 70B table: Galaxy FF1 all-reduce ≈ 5 µs + 0.7 µs/hop, against a wafer hop of 2.0 cycles ≈ 2.4 ns (≈ 250×). Using Lab 5's fit, a 16 × 16 allreduce is ≈ 2,000 cycles ≈ 2.3 µs at 850 MHz [Derived]. It notes that per-PE software steps, not wires, set the wafer's cost.
- **G7 Fixed.** Note under the CB widget: the compute bar hides the TRISC0/1/2 pipeline, which uses Dst half-sync instead of a CB.

## Still open from r3
- **r3 G2 Fixed.** Network row: 24 colors (20 user, Ch 4 #color-budget), 2.0/1.0 cycles/hop [Measured], ≈ 9 per PE through compute (CCN 34).
- **r3 G3 Fixed.** DeepSeek-R1: 16 Galaxies / 512 chips, batch 32, ~4 s TTFT, ~350 (~300–308 at launch), with the TT-Deploy source named, and a warning not to compare it with one CS-3. These facts are taken from the r3 web check and were not re-fetched.
- **r3 G4 Fixed.** The GEMV widget now gives a WSE-3 time (24 KiB/PE at 7.5 B/cycle + 9·side reduce + 2·side broadcast) at 850 MHz and at ~1.4 GHz (CCN 33), shown both in the SVG and in the readout. The caption now says Lab 2 #composing and Lab 4. No simulator check was run, since the constants were already measured.
- **r3 G5 Fixed.** Names SUMMA, links Lab 4 #summa and quotes the 1.5–3% fabric share; "Chapters 4–15".
- **r3 G9 Fixed.** 5.76 GB [Derived] (6.72 before the cut) in the product table, the comparison table and the quiz. GA date 28 Apr 2026 added; the "from $110k" price is tagged.
- **r3 G10 Fixed.** "As of November 2026", no MLPerf entry (v6.0). Adds QuietBox 2 at 476.5 tok/s [Vendor] and the Moreh demo with no published numbers.
- **r3 G11 Fixed.** The quiz links Ch 8 #inference for the four CS-3s and Ch 9 #budget for the per-user bound.
- **r3 G15 Fixed.** The GEMV readout now says that a full model must be streamed and that small layers can stay L1-sharded.

## CCN 30–38 on this page
- 33 (clock): new per-second wafer numbers state 850 MHz [SDK], and the GEMV widget also shows ~1.4 GHz [analyst].
- 34 (hop costs) and 35 (queue depths) were applied as above.
- 38 (links) was applied.
- 30, 31, 32, 36 and 37 do not touch this page, apart from the 2,000–4,000 per-user range used in G3 (consistent with 32).

## Verification
Playwright at 1100 px and 390 px: zero console/page errors and no horizontal overflow. Drove the matmul selects, the GEMV slider (n = 1024/4096/16384), the CB size and jitter controls, the pipe stepper, the floorplan preset and the Galaxy selects. All 65 hrefs resolve to existing files and ids.

## For other pages
- **Ch 1 (01-memory-wall.html), bound table, Wormhole Galaxy row:** change "≈ 130" to "≈ 124" (74 GB in BFP8 incl. shared exponents, 8.1 ms per pass) to match Ch 16 and Ch 18 (= r4-ch01 E5). Ch 1 quiz Q2 also says "1.4 MiB-per-core"; it should be 1.5 MiB (1,536 KiB).
- **Ch 3 (#pe-speed)** still says "f16 reaches about 3.2 per cycle on WSE-3 and 2.0 on WSE-2", with the "memory traffic" explanation that CCN 30 retires. Ch 16 now quotes ≈ 4/cycle with well-placed operands and links Ch 3 #pe-speed and Ch 6 #op-speed. If Ch 6 creates `#banks`, the Ch 16 link could point there.
- **App E row for the Ch 16 DeepSeek-R1 figure:** upgrade it from "press extracts" to the TT-Deploy post (r3 G3).
