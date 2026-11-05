# r3 gap audit · ch16-17 (16-tenstorrent.html, 17-gpu.html)

Inputs: both pages (text plus widget code), ch13-fixlog and ch14-fixlog (old numbering), CROSS_CHAPTER_NOTES 1–29, App E rows for Ch 16/17, ch18 and App A/B/C for cross-checks. A Playwright run at 1100 px and 390 px clicked every button and swept every select and range: 0 errors, no page overflow. Web check done on 2026-11-05. docs.nvidia.com does not resolve from this session. GitHub raw and search do work.

## Gaps, ranked

**G1 · high · Ch 17 "Inside an SM", SM/PE/Tensix table.** The Blackhole Tensix cell says "~1.43 MiB SRAM (1,464 KiB)". That is the Wormhole value. Ch 16, Ch 18, App A and App B all give Blackhole 1,536 KiB. The ch13 fix log already corrected this course-wide, but Ch 17 was missed. Learners compare these tables side by side. *Resolve:* change it to "1.5 MiB (1,536 KiB; Wormhole 1,464)". Writing only, S.

**G2 · high · Ch 16 "Same GEMV, two grains", comparison table, Network row.** It says "24 static colors, ~1 cycle/hop [sdk]". Note 20, Ch 12 and App C give measured costs of 2.0 cycles/hop on WSE-3 and 1.0 on WSE-2. Through a PE's compute (note 24) the cost is about 9.2 / 6.0. Ch 4 also says users get 20 of the 24 colors. The row sits next to Tenstorrent's "9 cycles router-to-router", so a learner would conclude that a Cerebras hop is 9× cheaper, when it is about 4.5× cheaper. *Resolve:* "24 colors (20 for user code), 2.0 cycles/hop WSE-3 / 1.0 WSE-2 [measured], ~9 through a PE's compute". Writing only, S.

**G3 · high · Ch 16 "Performance and caveats" (and App E row).** "Galaxy Blackhole, DeepSeek-R1 671B: ~350 tok/s per user" gives no configuration. Tenstorrent's TT-Deploy post (May 2026) now gives it as **16 Galaxies (512 Blackhole chips), batch 32, ~4 s TTFT**. Galaxy Blackhole reached GA on 28 Apr 2026, and The Register reported ~300, rising to 350 with software. Without the 512-chip context, the number reads like one box and invites a false comparison with Cerebras. *Resolve:* add the configuration and cite tenstorrent.com/newsroom/tt-deploy as the vendor primary. Upgrade the App E row from "press extracts" to that source. Resolvable via web, S.

**G4 · med · Ch 16 "Same GEMV, two grains" widget.** The Tensix side gives a time bound (≥ µs per token from 512 GB/s). The WSE-3 side gives no time, only "nothing comes from off-chip". So the widget cannot answer the question it sets up ("which grain is faster for this layer?"). *Resolve:* add a WSE-3 estimate from measured course constants: the f16 matvec rate of ~7.5 B/cycle/PE (note 27), the chain reduce at c ≈ 9 cycles/hop over √PEs (note 24), at 850 MHz/1.1 GHz [derived]. A short GEMV run in the simulator could confirm it (Lab 4 or gemv-08 copy). The caption also says "the pattern from Labs 2 and 3", but Lab 3 is the heat stencil. It should say Labs 2 and 4. Resolvable in writing (constants already measured), with an optional simulator check. M.

**G5 · med · Ch 16 "Anatomy of a matmul" and "CSL ↔ Metalium".** The page calls matmul 2D "a systolic array built in software", which is the SUMMA dataflow of Lab 4 (row multicast of A, column multicast of B). Yet Ch 16 never links to Lab 4, although Lab 4 links back to `16-tenstorrent.html#matmul`. The mapping table also says "In CSL (Chapters 4–13)"; it should say 4–15. The learner misses the one like-for-like kernel the course measured on both sides (phase3-learner-path asked for exactly this). *Resolve:* add one sentence plus a table row (`<collectives_2d>` broadcast ↔ `noc_async_write_multicast` + semaphores) and quote Lab 4's measured fabric share (1.5–3% of each step). Writing only, S.

**G6 · med · Ch 17 "Three generations", Rubin column (stale).** The BF16 dense cell says "not published in our sources". NVIDIA's preliminary 2026-1H partner deck (Gigabyte PDF) and Flopper now list ~4 PF dense BF16 per GPU. Rubin is also in full production and shipping since Q3 2026 (first NVL72 racks to CoreWeave and others), so "(2026)" should say so. HBM is still contested: Meta's San Miguel spec gives 19.2 TB/s, while others repeat 22, so keep the "specs are targets" callout. *Resolve:* fill the cell, tagged vendor (preliminary), and add the shipping status. Resolvable via web, S.

**G7 · med · Ch 17 "2026: the incumbent adds an SRAM decode chip" (stale).** It says "256 vs 128 … not settled here" and has no status. Since then, NVIDIA announced Groq 3 LPX in full production on 24 Aug 2026 (Hot Chips 2026), shipping in Q3 with Nebius as the first cloud, and showed a first third-party inference benchmark (Tom's Hardware). Most reports, including NVIDIA's localised pages, give 32 trays × 8 = 256. *Resolve:* update the status, settle on 256, and add the benchmark figure if the article is reachable. The vLLM Rubin preview (Oct 2026, "7.8× GB200") is optional. Resolvable via web, S.

**G8 · med · Ch 17, nine `[unv]` tags.** Several now have citable sources: L1/L2/HBM latency (Luo et al., arXiv 2402.13499); Megatron patterns (the cited papers are primary: tag [indep], not unv); 67 TF FP32 (H100 datasheet). TMEM, setmaxnreg 40/232 and the NVL72 tray layout need PTX/CUTLASS/NVIDIA pages; docs.nvidia.com is blocked here, CUTLASS via raw GitHub may work. *Resolve:* retag where the source is reached, and update App E. Partly resolvable via web, M.

**G9 · low · Ch 16 product table, Galaxy Blackhole column.** "6.2 GB" of on-chip SRAM matches neither 32 × 180 MB = 5.76 GB (after the cut) nor 32 × 210 MB = 6.72 GB. The column has no derivation and no tag. The status should mention GA on 28 Apr 2026, with a 4-Galaxy supercluster from $440k, which is consistent with "from $110k". *Resolve:* use 5.76 GB [derived] (6.72 before the cut). Writing plus web, S.

**G10 · low · Ch 16 caveats, "No independent benchmark or MLPerf submission was found".** This still holds: no Tenstorrent entry appears in the MLPerf Inference v6.0 coverage (Apr 2026). It now needs a date, and two 2026 vendor-side data points:
- QuietBox 2 (4 × Blackhole, $9,999) runs Llama 3.1-70B at 476.5 tok/s in aggregate [vendor], not independently confirmed.
- Moreh's TT-Deploy demo claims DGX-A100-class MoE inference on Wormhole Galaxy, as a partner with no published numbers.

Ch 18 already has QuietBox 2. *Resolve:* add one sentence with the "as of Nov 2026" date. Resolvable via web, S.

**G11 · low · cross-references.** The Ch 16 quiz ("four CS-3 systems … Chapter 8") and Ch 17 (3×: "Chapter 8's layers-across-wafers", "(Chapter 8), which is how Cerebras reaches 2,314") point to Ch 8. The per-user decode explanation (notes 25–27) now lives in Ch 9 "From model to tokens". *Resolve:* point to Ch 9, or to "Ch 8–9". Writing only, S.

**G12 · low · Ch 17 SM/PE footnote.** "One SM = 256 PEs at 8 FP16 FMAs each" uses the vendor SIMD width. The course measured ~4 f16 MAC/cycle on WSE-3 (notes 22 and 27), which makes it ~512 PEs per SM in practice. *Resolve:* add a half-sentence caveat with a link to Ch 6. Writing only, S.

**G13 · low · Ch 17 generations table.** Blackwell Ultra (B300/GB300, 288 GB HBM3e) is missing. It is the volume part in 2026 and the MLPerf v6.0 record holder. *Resolve:* add a footnote, or a column if space allows. Resolvable via web, S.

**G14 · low · carried-over partials** (ch13 D10/V2, ch14 D4/V4): no dispatch/trace timeline (Ch 16), static Hopper pipeline with no ping-pong toggle (Ch 17), no portrait SVG layouts. Writing + JS, M–L.

**G15 · low · Ch 16 GEMV widget text.** It says W "is smaller than the 180 MB of SRAM, but in decode it is streamed from GDDR6 anyway". For small layers, TT-NN can keep weights L1-sharded. *Resolve:* say "for a full model it must be streamed". Writing only, S.

## Not gaps (checked, rejected)
Quizzes all answered (7 + 8). NoC quiz 18 vs 11 hops correct. TP all-reduce example (0.26 ms / 83 ms / 0.75 s) correct. B200 BF16 dense 2.25 PF matches HGX table. GB200 NVL72 13.4 TB / 576 TB/s correct. tt-metal README still 72.5 t/s/u, v0.65.0-rc7 (not stale). p150 140→120 cut confirmed (fw 19.5). Ch 18 Blackhole L1/flit values already fixed. WSE-3 8-way FP16 consistent with Ch 3. Peak formula 774/664/745 correct. Widgets: 0 errors, no overflow, all controls respond. No post-Blackhole TT accelerator launched yet.
