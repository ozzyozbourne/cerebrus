# Round 3 gap audit: ch01-02 (01-memory-wall.html, 02-the-wafer.html)

Method: I read both pages in full, both fix logs (open items) and CROSS_CHAPTER_NOTES 1–29, and grepped ch03/04/06/09/16/17/18 and App E for shared facts. I loaded both pages in Playwright at 1100 and 390 px and drove every button, select and range: no JS errors, no NaN/undefined, no page overflow. I web-checked the open "unverified" items and read the single-tile-matvec `run.py`. Nothing in the course was edited.

## Gaps, ranked

**G1 · high · ch01 "Decode speed bounds" calculator, WSE-3 note (JS around line 477)**
- **Missing:** The calculator still uses the old framing. Chip = CS-3 prints a per-user bound of about 600k tok/s. The note says measured 2,314 is "far below it" and tells the reader to divide by the chip count (about 150k). The "Bound versus reality" table on the same page was updated per notes 25/27. It gives about 2,000–4,000 tok/s for one user (layer-pipelined, each layer read only by its own region) and says the measured speed sits inside that range.
- **Why it matters:** The chapter's central claim contradicts itself, and the widget is where learners try the numbers.
- **Resolve:** For WSE-3, print two lines: "aggregate, all users ≈ N × 21 PB/s" and "one user ≈ 1/80 of that: ~7,500 at headline bandwidth, ~2,000–4,000 at kernel read rates (Ch 9)". Rewrite the note to match the table: per-region SRAM reads plus latency/communication. Remove the "divide by chip count" advice.
- **Resolvable here?** Yes, writing only. **Effort:** S–M.

**G2 · med · ch01 "The wall is getting taller" (text + generations table)**
- **Missing:** The text says the sources do not say whether Rubin's 50 PF NVFP4 is dense. The table then uses 50 PF, giving a ridge of about 2,600 and a gap of about 650×. Ch17 already says "50 PF inference / 35 PF training (inference figure relies on Transformer Engine compression)". Web sources (Guru3D, PCGH, CUDO) call the 50 PF figure sparse/effective and 35 PF dense.
- **Why it matters:** The B200 row uses dense FP4 (9 PF) and the Rubin row does not, so the "Rubin gap ≈ 2× H100's" conclusion is inflated. It also contradicts ch17.
- **Resolve:** Use 35 PF dense: ridge 35e15 ÷ 19.2e12 ≈ 1,820, gap ≈ 455×. Quote 50 PF as the compression-assisted inference figure. Update the sentence "for Rubin and Blackhole the gap is about twice the H100's".
- **Resolvable here?** Yes, web + writing. **Effort:** S.

**G3 · med · ch01 quiz Q2 answer and "Three answers" SVG (Tenstorrent box)**
- **Missing:** Both say "1.4 MiB per core" in a Blackhole p150 context. Ch16, ch18 and note 15 give 1,536 KiB on Blackhole (1,464 KiB is Wormhole). The SVG's own "120 cores · 180 MB" works out to 1.5 MB per core.
- **Resolve:** Change both to "1.5 MiB (1,536 KiB)".
- **Resolvable here?** Yes, writing only. **Effort:** S.

**G4 · med · ch02 "One wafer, 900,000 small machines" and "Read the FLOPs carefully"**
- **Missing:** The per-PE budget, the first-principles check and quiz Q5 all assume the full vendor f16 SIMD width: 4 on WSE-2, 8 on WSE-3. The "What a real kernel gets" callout measures only fp32. Elsewhere the course has already measured f16 @fmach at about 2/cycle on WSE-2 and about 3.3–4/cycle on WSE-3 (ch06 op table, notes 14/22). That is half the vendor width, and ch09 says the 8-wide path is "not demonstrated".
- **Why it matters:** A learner leaves ch02 believing 12–16 PF dense is attainable per PE. The "measured vs vendor vs analyst" objective is only half delivered.
- **Resolve:** Add one sentence plus a calculator/table row: "simulator f16 FMAC: ~2/cycle WSE-2, ~4/cycle WSE-3 [Measured, Ch 6] ⇒ ≈ 6 PF at 850 MHz on WSE-3, so the analyst dense figure is not demonstrated in the SDK". Link to ch06 #op-speed.
- **Resolvable here?** Yes, writing only (data exists). Optionally re-run single-tile-matvec in f16 in the simulator. **Effort:** S.

**G5 · med · ch01 roofline-per-level table + capacity-map caption (also App E row)**
- **Missing:** CS-3 "12 × 100 GbE ≈ 150 GB/s" is still tagged "Vendor, via forum" and is listed as an open item.
- **Evidence:** The Cerebras system page and PSC Neocortex "CS-3 system specifications" list System I/O 1.2 Tb/s (12 × 100 GbE). The Aug 2026 CS-4 press release lists CS-3 at 1.2 Tb/s against CS-4 at 2.4 Tb/s, which matches ch02's CS-4 figure.
- **Resolve:** Retag as Vendor with those citations. Drop "only from a forum post" in ch01 and App E.
- **Resolvable here?** Yes, web. **Effort:** S.

**G6 · med · ch01 per-level table note and "The comparison trap"**
- **Missing:** The H100 shared-memory bandwidth uses about 128 B/clk/SM at "~1.8 GHz", flagged as an unsourced assumption (fix-log open item).
- **Evidence:** The SXM boost clock is 1,980 MHz [Vendor]. 132 × 128 B × 1.98 GHz ≈ 33.4 TB/s, which matches the ~33 TB/s aggregate quoted by secondary sources. 128 B/clk is 32 banks × 4 B (CUDA programming guide).
- **Resolve:** Cite the Hopper whitepaper/CUDA guide for 32 × 4 B banks and the 1.98 GHz boost clock. Restate as ≈ 33 TB/s, ridge ≈ 30 (Derived from Vendor inputs). Keep "RF faster again".
- **Resolvable here?** Yes, web (confirm against the primary whitepaper). **Effort:** S.

**G7 · low · ch01 quiz Q5 answer**
- **Missing:** The answer says "a kernel at 50 FLOP/byte that was bandwidth-bound on HBM can become compute-bound once it is tiled into shared memory". That treats intensity as fixed across levels. The page itself says a roofline belongs to one memory level, and intensity is measured against that level too: tiling raises HBM-level intensity, and smem-level intensity is a different number.
- **Resolve:** Reword it. Tiling into shared memory cuts HBM traffic and raises the kernel's HBM intensity. The kernel must then also clear the smem ridge (~30) on its smem traffic.
- **Resolvable here?** Yes, writing only. **Effort:** S.

**G8 · low · ch01 "Latency is not bandwidth" and ch02 "What the wafer buys" (hop time)**
- **Missing:** Both say "about one hop per cycle". Ch04 and note 20 give 1 cycle/hop on hardware [Indep] but 2.0 cycles/hop on the WSE-3 simulator (1.0 on WSE-2). Ch02's crossing times at 850 MHz (0.9 / 2 µs) use 1 cycle/hop with no simulator caveat.
- **Why it matters:** Learners meet 2 cycles/hop in the labs.
- **Resolve:** Add a half-sentence to each: "(the WSE-3 simulator models 2 cycles/hop, Ch 4)".
- **Resolvable here?** Yes, writing only. **Effort:** S.

**G9 · low · ch01 "Measured: one PE's roofline" vs ch02 "What a real kernel gets"**
- **Missing:** ch01 says the N = 100 matrix "takes ≈ 42 KB". ch02 says 40 KB, which is correct: `run.py` pads nb up to a multiple of 4, so padded_nb = 100 and A = 40,000 B. Ch01 also says the benchmark scales to "a 750 × 994 rectangle" without noting that this is the CS-2 size applied to a WSE-3 run (ch02 notes it).
- **Resolve:** Change "42 KB" to "40 KB". Add "(the CS-2 fabric size; WSE-3's is unpublished)".
- **Resolvable here?** Yes, writing only. **Effort:** S.

**G10 · low · ch02 yield/NVLink/power cells**
- **Missing:** GH100 144 SMs, H100 die ~814 mm², H100 ~700 W and NVLink 4 0.9 TB/s are still tagged "Industry figure / not re-verified". Ch17 and ch18 already carry 900 GB/s and 700 W as Vendor.
- **Resolve:** Retag them Vendor (Hopper whitepaper / H100 datasheet), consistent with ch17/18. Remove the "not re-verified" wording.
- **Resolvable here?** Yes, web. **Effort:** S.

**G11 · low · ch01 Little's-law paragraph**
- **Missing:** The 600 ns HBM latency is "illustrative, not from our sources".
- **Resolve:** Cite a measured H100 HBM load latency (e.g. the Chips and Cheese H100 article) and recompute bytes in flight.
- **Resolvable here?** Yes, web. **Effort:** S.

## Not resolvable here
- The WSE-3 user-visible fabric size (ch02, both "where the cores go" and quiz Q6) is still unpublished. The SDK only hard-codes 750 × 994, and the web search found nothing. No: unavailable source.
- The real CS-1/2/3 spare scheme and defect density are not public. No: unavailable source.

## Not gaps (checked and rejected)
- Widgets: all controls on both pages work at 1100/390 px with no errors or NaN.
- Every quiz item on both pages has an answer (7 + 6).
- Clock story (note 2/10): applied consistently on both pages.
- Halo/memcpy frame (notes 8/9): "at least 7 columns / 2 rows", 4 + 3 split and the measured 3 W / 2 E columns all agree with ch07.
- Cache sizes 256 B / 512 B match ch03.
- The 8 banks × 4 B ≈ 32 B/cycle ceiling matches ch03.
- $0.60/M tokens matches ch08, ch09 and ch18.
- Groq 3 LPX reference matches ch17/ch18.
- p150 120 cores / 664 TF matches ch16 and note 15.
- ch08's 450 tok/s vs ch01's 2,100 tok/s: these are launch-era and later measurements, not a conflict.
- Matvec byte/FLOP counts (12N² + 4N; 2N² − N) match `run.py`.
- Three different SM areas in ch02 (6.2 / 7.8 / ~5 mm²) are each derived and explained.
- Unbuilt N4–N6 (ch01) and N5/N7/N8 (ch02) visuals: their content is covered by tables, so they are not learner gaps.
