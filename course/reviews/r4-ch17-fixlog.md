# r4 fix log · ch17 (17-gpu.html)

Verified with Playwright at 1100 px. Console errors: 0. Page scrollWidth: 1100. All 74 relative links resolve to existing files and ids. I drove these widgets: the SM highlight, coalescing reshuffle, latency W, tile BM = 256 and the new cooperative / ping-pong toggle. All 24 App E text-fragment anchors into this page still match. Web check (2026-11-05): search found the LPX production reports, CoreWeave's Rubin availability and B300 specs. Raw GitHub served the CUTLASS sources.

## Errors
- **E1 Fixed.** "Three moves" now says the ridge is roughly flat at equal precision (295 → ~281). The headline growth is put down to format, with per-value figures: B200 FP4 ≈ 560 vs H100 BF16 ≈ 590, Rubin NVFP4 ≈ 1,300 (50 PF) and ≈ 910 (35 PF) [Derived].
- **E2 Fixed.** A strided DSD wastes no bytes. Only operand streams that start in the same bank slow it, by up to 2×. Links to 06-dsds.html#banks (note 30).
- **E3 Fixed.** Attention: ~1 FLOP/B for MHA; Llama-70B's 8-way GQA gives ~8 (BF16 KV) or ~16 (FP8), still far below the 295 ridge [Derived].
- **E4 Fixed.** Clock basis stated: 67 TF FP32 is at the 1.98 GHz boost, the Tensor Core figure at 1.83 GHz, and FP32 at 1.83 GHz is ≈ 62 TF. The 67 TF is retagged as Vendor datasheet.
- **E5 Fixed.** "Hits peak" became "approaches peak". I added a second roofline check against L2: 7.7 TB/s is needed vs >5.5 TB/s measured. Cluster/TMA multicast is shown as an effective 256 × 512 tile (171 FLOP/B, 5.8 TB/s), and the SXM part's higher L2 bandwidth is mentioned. "70–80% of peak" is tagged Unverified. The quiz answer and tile-widget readout now match.
- **E6 Fixed.** The worked example is now "one TP = 8 group of a larger 70B job", with the 1.1 TB Adam state vs 640 GB note (FSDP/PP).
- **E7 Fixed.** Blackhole cell: 1.5 MiB (1,536 KiB; Wormhole 1,464).
- **E8 Fixed.** Rubin header: "shipping since Q3 2026", plus CoreWeave availability on 30 Sep 2026 [Vendor]. The BF16 cell says "not published by NVIDIA; ~4 PF in a third-party spec sheet" [Unverified], consistent with 35 PF ÷ 8. I added a B300/GB300 note: 288 GB, ~8 TB/s, ~15 PF dense NVFP4 [Vendor]. LPX: the count is settled at 256 ("the 128 is an error"). A status paragraph covers full production (Hot Chips, 24 Aug 2026), Nebius as first cloud, and NVIDIA's AA-cited ~3,400 tok/s on Gemma 4 31B at 100K context, with a caveat on its Cerebras comparison.
- **E9 Partly.** Retagged: Megatron → Indep (primary papers); setmaxnreg 40/232 → Vendor (CUTLASS sm90 ping-pong and cooperative sources, both 40/232); TMEM 256 KB → Vendor (CUTLASS tmem_capacity_sm100.hpp: 128 rows × 512 cols × 32 bit); 67 TF → Vendor datasheet. Still Unverified: the NVL72 tray layout, single-thread MMA issue, and the L1/HBM cycle ranges (I did not read Luo et al. 2402.13499's tables). Three Unverified tags are new and honest: the Rubin BF16 aggregator figure, the "adaptive compression" mechanism, and GEMM efficiency of 70–80%. Total unv count is still 13.

## Explanation problems
- **X1 Fixed.** Little's-law callout: an added paragraph says which question each model answers.
- **X2 Fixed.** The compression clause moved out of the table and into the number-formats callout. It is explained as NVIDIA's "adaptive compression" in the third-generation Transformer Engine, with the mechanism unpublished [Unverified], so the 50 PF is conditional on it.
- **X3 Fixed.** Now reads "cp.async on Ampere, the TMA engine on Hopper, below", with a link to #hopper.
- **X4 Fixed.** wgmma: B always comes from shared memory; A comes from registers or shared memory.
- **X5 Fixed.** Now reads "which makes 2,314 possible". The sentence links to Ch 9 #budget and covers the ~500 tok/s launch kernel and the optimised GEMV/collectives plus speculation.
- **X6 Fixed.** I softened the claim and gave the reason (the shared weight read), with a pointer to Ch 18.

## Connecting gaps
- **G1 Fixed.** Measured 86 tok/s (HC2024 citing AA), ≈45% of the 190 bound, linked to Ch 9 #budget. Pointers in "One token" now go to Ch 8 #inference and Ch 9 #budget.
- **G2 Fixed.** The hierarchy figure's wafer column now shows 2 cycles/hop on WSE-3 (1 on WSE-2) and ≈9 per PE that adds and forwards. The caption cites Measured, Ch 4. A new paragraph makes the point that a PE ~400 hops away is as far as HBM (~800 cycles), so layout is a locality problem.
- **G3 Fixed.** The concept table row says the rectangle and N are compile-time params. A new "same n on the wafer" worked example: 8 MB, ~5,500 elements/PE, ≥182 PEs, ~5,500 cycles ≈ 6.5 µs at 850 MHz [SDK clock], twice that for program 01's same-bank placement, and host I/O dominates.
- **G4 Fixed.** Lab 4 numbers added: fabric ~2% of each step, 32% / 51% of 1 f32 FMAC per cycle [Measured, Ch 14 #measure].
- **G5 Fixed.** SM ≈ 256 PEs at the vendor width, ≈512 at the measured ≈4 f16 FMAs per cycle (layout-dependent; link to Ch 6 #op-speed).
- **G6 Fixed.** An "Appendix B" link sits under the concept table. The thread-block/shared-memory row now names the neighbour PE at 2.0 cycles as the nearest thing to cluster DSMEM.
- **G7 Fixed.** Control-task IDs 0–63 [Measured]; safe user local IDs 8–20 = 13 on WSE-3 [SDK]; Ch 5 #budget. The contrast is now numeric.
- **G8 Partly.** I added a cooperative vs ping-pong toggle with a consumer / Tensor Core timeline (illustrative durations; 80% vs 100% busy). No portrait SVG layouts: optional per REVIEW_BRIEF.

## Item 38 / notes 30–38
- Glossary links on the Terms box, plus a "full glossary" link (App A G5). First-use links for HBM, BF16, FP8, Transformer Engine, sparsity, grid of thread blocks, warps, divergence, coalescing, occupancy, latency hiding, DSD, microthreads, ridge, SUMMA, TMA, thread-block clusters, command stream, CUDA graphs, KV cache and AFD.
- Every Chapter / Lab / Appendix mention in the prose is now a link to a section anchor where one exists.
- Note 30: the bank rule is stated once and links to 06-dsds.html#banks. Note 33: the wafer timing says 850 MHz [SDK]. Note 34: hop costs are 2.0 / 1.0 and 9.2 / 6.0. Notes 31, 32, 35–37: nothing on this page.

## For other pages
- **Ch 18 #limits / LPX paragraph:** "no independent LPX decode measurement exists yet" is now dated. NVIDIA cites Artificial Analysis at ~3,400 tok/s on Gemma 4 31B at 100K context (Hot Chips, Aug 2026), and LPX is in full production. Ch 18 should also say "Rubin shipping (CoreWeave, 30 Sep 2026)".
- **Ch 18 "Back to the memory wall":** "the ridge still climbs (295 → ~2,600 FLOP/byte from H100 to Rubin)" compares BF16 with NVFP4. At equal precision the ridge is roughly flat (see Ch 17 E1).
- **Ch 9 #moe:** it says "22 TB/s of HBM4 per Rubin GPU". The current spec is 19.2, and Ch 9 also still hedges "one report says 128" (now settled as 256).
- **App E:** retag rows for Megatron (Indep), setmaxnreg 40/232 and TMEM 256 KB (Vendor, CUTLASS source), and 67 TF (Vendor datasheet). Add rows for the Rubin BF16 ~4 PF [Unverified, flopper.io], the B300 specs, LPX full production and the AA ~3,400 tok/s figure, and the 70–80% GEMM efficiency [Unverified].
- **App A:** a "Rubin CPX" entry and a "PTX / CUTLASS" entry are still missing (App A G3). This page links its terms there once those entries exist.
