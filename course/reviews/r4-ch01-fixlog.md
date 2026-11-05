# Round-4 fix log: ch01 (01-memory-wall.html)

Verified in Playwright at 1100 px. I drove the calculator (CS-3, B200, H100; batch 1/64/256; 8B/70B/405B), the roofline (WSE-3 SRAM, H100 smem, "Show on roofline") and both map modes. Result: 0 console errors, no horizontal overflow, and all 67 links resolve (file and `id`). `scan_tags.py --check` now counts the Ch 1 legend (legend=7).

## r4-ch01.md
- **E1** Fixed. Replaced the 450,000 tok/s sentence with the per-region compute cap: 62.4 PF ÷ 80 ≈ 780 TF ≈ 5,600 tok/s on the analyst peak, and ≈ 2,200 at the measured f16 rate (~4 MAC/cycle, ≈ 6.1 PF/wafer at 850 MHz). Added that read and math limits coincide at ≈ 1 FLOP/B. The bold conclusion now names "per-region multiply-accumulate rate (≈ SRAM read rate) plus latency and communication". The table cell gives 7,500 and 5,600 as non-ceilings (item 32).
- **E2** Fixed. The calculator models CS-3 as layer-pipelined: per token = L × (one region step), for both memory and math, with b = max(1, B/L) users per region. New readout lines give per-user at the measured f16 kernel rate and the "pipeline full" aggregate. Removed "memory bound only" and "divide by chip count". 70B FP16 B=1 now reads 5,571 (analyst) / 2,186 (measured) tok/s. The note quotes 2,314 only for 70B.
- **E3** Fixed. "What this course covers" now has `id="course"`, includes Ch 9, says "five labs (Ch 11–15) built on seven original programs" and links every chapter.
- **E4** Fixed. Changed to "≈ 36 GB on paper, ≈ 20 GB after each PE's ~4.2 KB code/task table (≈ 3.8 GB/wafer)", linked to Ch 3 #memory-map.
- **E5** Fixed. Galaxy ceiling ≈ 124 (≈ 74 GB with BlockFP8 exponents), linked to Ch 16 #70b.
- **E6** Fixed. RF+smem bar lo = 3.3e13 (matches the 33 TB/s smem). Ratio restated as 50–650× everywhere (text, arrow, info, quiz).
- **E7** Fixed. "50–100 FLOP/byte" is retagged Indep (research notes). Changed to ≈ 67 MB and ≈ 650× in the callout, map and quiz.
- **E8** Fixed. B200 calculator peak follows the format (2.25 / 4.5 / 9 PF, Vendor, Ch 17). The hint says so and the note prints the peak used.
- **X1** Fixed. Added a sentence in the callout and a table row "Ridge (fp32, measured peak) ≈ 2 ÷ 32 ≈ 0.06".
- **X2** Fixed. Added the asymptote 2P ÷ (ctx × KV/token): ≈ 213 at 2k and ≈ 53 at 8k, so no batch reaches 295.
- **X3** Fixed. Added the rule "FLOPs ≈ 2 × parameters → 140 GFLOP/token" to the #decode worked example.
- **X4** Fixed. Added a GQA half-sentence (8 K/V heads shared by 64 query heads, 8× smaller cache).
- **X5** Fixed. 0 → 67 links: glossary links on first use of key terms, every Chapter mention linked, "Full glossary" link in the Terms box. Added ids `headline`, `course`, `bound`, `regions`, `sram-area`.
- **X6** Fixed. Q6 now asks for three assumptions; the third is that the 15.6 PF peak is reachable (measured ≈ 6 PF roof).
- **G1** Fixed. New paragraph "Why not just add SRAM to a GPU?" plus a to-scale bar figure `#sram-area`: 0.021 µm² N5 bitcell [Indep, IEDM 2019 via WikiChip] → ≈ 7,400 mm² of cells, ≈ 10,500 mm² as macros (~32 Mib/mm², Unverified WikiChip estimate) ≈ 12 reticles. Hands off to Ch 2 #reticle.
- **G2** Fixed. New figure `#regions`: 4 wafers × 20 layer bands, user A in one band, users B–F in others, with a caption on the 1/80 bandwidth and FLOPs. Region/layer-pipelined and tensor-parallel/pipeline split are added to Terms. Linked to Ch 9 #pipeline and Ch 8 #inference.
- **G3** Fixed. Added a per-token budget paragraph: 432 µs → 5.4 µs/layer → ≈ 4,600 cycles at 850 MHz / ≈ 7,600 at ~1.4 GHz (item 33), against ~5,200 (measured) / ~2,600 (8-wide) GEMV cycles. The rest is reductions, hops and 3 wafer crossings. Links Ch 9 #budget.
- **G4** Fixed. Dashed "measured f16 kernel ≈ 6.1 PF" roof on the WSE-3 SRAM level (with a readout line and level note), plus a matching row in the one-PE table. The one-line bank-placement rule links to Ch 6 #op-speed (item 30; Ch 6 #banks did not exist yet).
- **G5** Fixed. Little's law: 23 GB/s × 1.2 ns ≈ 27 B ≈ 7 f32 words vs 1.7 MB.

## Still open from r3-gaps-ch01-02.md
- **G1** Fixed (as E2).
- **G2** Fixed. Rubin uses 35 PF dense (50 PF with compression): ridge ≈ 1,800, gap ≈ 455×. Added the same-precision clause (B200 BF16 ≈ 281, per r4-ch17 E1 and r4-ch18 E4). The sentence now reads "Rubin ≈ 1.5×, Blackhole ≈ 2× the H100's gap".
- **G3** Fixed. 1.5 MiB (1,536 KiB) in Q2 and the SVG.
- **G5** Fixed. Changed to "Vendor, CS-3 system spec 1.2 Tb/s" in the table, note, figure caption, SVG box and widget tag. The "forum" wording is gone.
- **G6** Fixed. smem = 132 × 32 banks × 4 B × 1.98 GHz ≈ 33 TB/s, ridge ≈ 30, in the table, note, trap callout and widget level.
- **G7** Fixed. Q5 reworded: intensity is per level, tiling raises HBM intensity, and the kernel must also clear the smem ridge (~30).
- **G8** Fixed. The "(WSE-3 simulator models 2 cycles/hop, Ch 4)" caveat is in the level-table intro, the Little's-law paragraph and the widget fabric note (item 34).
- **G9** Fixed. 40 KB (100 × 100 × 4 B); 750 × 994 marked as the CS-2 fabric size.
- **G11** Partly. No published measured H100 HBM latency was found (web search 2026-11-05). Now "~500 ns, Unverified ballpark" (1.7 MB in flight), which matches Ch 17's figure.

## Cross-page items about Ch 1
- r4-appE E8 (legend not detected): Fixed. The legend is rewritten as "marked <tag>, …", adds Unverified and links App E #tags. The scanner now reports legend=7.
- r4-ch08 E4 (WSE-2 7.5 PF tagged Analyst): Fixed in the generations table → "Vendor, Hot Chips 2022" (item 36).
- r4-ch08 G4 (off-wafer ridge = Ch 8 knee): Fixed (Ch 1 side). One sentence in the level-table note links Ch 8 #weight-streaming.
- r4-ch16 E4 (130 → 124): Fixed (as E5).
- r4-appA G5 (Terms box doesn't link App A): Fixed.
- r4-ch09 E1 (propagate ~1.4 GHz to Ch 1): Fixed in the G3 budget paragraph and the measured-rate wording (850 MHz stated).
- r4-ch09 X5 (in Ch 9): nothing to do here. Ch 1's decode figure caption now says "on a GPU" and links #bound.

## For other pages
- Ch 2: the WSE-2 "~7.5 PF dense" tag should be Vendor (HC22), per r4-ch08 E4. Ch 1 is now Vendor.
- Ch 6: once `#banks` exists, Ch 1's two "Chapter 6" links (#op-speed) could point there.
- Ch 18: r4-ch18 E4 (Rubin ridge 2,600 without format caveat). Ch 1 now uses the 35 PF dense ridge ≈ 1,800, so Ch 18 should match.
- Roofline widget (cosmetic, Ch 1 only): with WSE-3 selected, the "B200 (FP4)" end label sits close to the new dashed measured roof. It is readable, so I left it.
