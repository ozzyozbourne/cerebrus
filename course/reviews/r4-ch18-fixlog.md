# R4 fix log: Ch 18 (18-comparison.html) + index.html

Inputs: r4-ch18.md, the still-open items of r3-gaps-ch18-index.md, CROSS_CHAPTER_NOTES 30–38, and cross-page items about Ch 18 in r4-appD, r4-appE, r4-ch09, r4-ch17. Verified with Playwright at 1100 and 390 px on both pages: zero console or page errors, no horizontal overflow. Every widget was driven (ridge batch, cost presets/streams/context, chooser for all models and both goals, Lab 3 slider). All 109 links on Ch 18 and 59 on index resolve, including anchors. No experiments were needed.

## Errors
- **E1 Fixed.** The `#rf` WSE-3 readout no longer mentions the tick or "the rest is pipeline latency". It now reads: whole-wafer bandwidth; one user sees ~1/80; measured 2,314 sits in the 2,000–4,000 kernel-rate range (Ch 9). The ridge paragraph also links to the new `#limits` section.
- **E2 Fixed (r3 G1).** The `#ch` chooser has two columns for the Cerebras rows. "Per-user ceiling" is aggregate ÷ layers (LAYERS: 32/80/126/61/61, model configs), shown at real kernel rates (×2,000/7,500 to ×4,000/7,500): 70B 16-bit gives ~2.0k–4.0k. "All users (aggregate)" gives 600k. GPU and TT rows show "grows with batch". The readout's "pipeline latency" wording is replaced with note 32's wording plus the KV cap.
- **E3 Fixed.** Now "~24–60 ms per full read (H100/B200 ~24, p150 ~62)", with which device holds 70B at which precision.
- **E4 Fixed.** Added the clause on format growth (BF16 vs NVFP4, decode intensity ×4) with a link to Ch 1 #taller.
- **E5 Fixed.** The stencil callout and the `#lab` readout say "CS-2's 737k SDK-visible PEs; CS-3 unpublished, ~900k would add ~22%". Ch 15's 950 × 950 convention is listed under "For other pages".
- **E6 Fixed.** Changed to "≈ M + 7P + 13" (59/73/101/157 against measured 58/73/101/158).
- **E7 Fixed.**
  - G4: LPX is 256/rack, ~128 GB, ~40 PB/s, in production. Added the AA 3,431 tok/s Gemma 4 31B figure (Vendor citing AA + Unverified, flagged not comparable).
  - G5: The decision table reads 80–288 GB with B300/Rubin and Rubin NVL72 20.7 TB. Quiz Q2 reads 2–6.5×. The CUDA panel HBM label reads 80–288 GB. B300 and Rubin rows were added to the chooser. MI455X and TPU 8i lines were added (Secondary + Unverified).
  - G6: The price is now dated "2024 list price, Llama 3.1-70B" everywhere. The 2026 aggregator $0.85 in / $1.20 out was added (Unverified), and the preset label says the price target is from 2024. I could not re-check cerebras.ai/pricing because the site is blocked.
  - G12: Now "bandwidth was never the bottleneck; capacity was (5,450 / 1,835 cells)".
- **E8 Fixed.** Changed to "seven programs (five written from scratch, two adapted)". The "only data point" wording is gone from the open questions and the evidence table, which now has a row for the course's own utilisation (GEMM 18–51%, CG 1.3–17%).

## Explanation problems
- **X1 Fixed.** HC22/HC2024 are expanded at first use (architecture table). The decode intro defines AA = Artificial Analysis and HC2024.
- **X2 Fixed.** The Lab 2 bullet now says the ~7.2 slope is the own-clock reading (9.2 CE hop minus one router hop) and links Ch 12 #hop-cost.
- **X3 Fixed.** Added a clause saying the match with 179× is a coincidence of framing (one H100 roofline vs all of Frontier under strong scaling).
- **X4 Fixed.** `#dc` draws a shaded 2,000–4,000 "one user" band. The 600k dot is labelled "all users ≤ 600k" and the hint explains band, tick and dot. The readout gives 2,314 = 31% of 7,500, inside the band, and warns against dividing by 600k.
- **X5 Fixed.** Added a sentence pointing to Ch 17 #saxpy-twice and App B #rosetta / #budget.
- **X6 Fixed.** "Where to go next" now links App D #ladder (also closes r4-appD G3's Ch 18 part), App B, App C and App E #unverified. The redundant Lab 3 extension is replaced with a 2-D stencil / wide-halo extension, and a Lab 5 streaming-allreduce extension was added.

## Connecting gaps
- **G1 Fixed.** New `<h3 id="limits">What actually limits a kernel on the wafer</h3>` after the decode callout. It is a paragraph joining ridge, decode-kernel rate and GEMM efficiency, plus a decode/stencil/GEMM/CG × GPU/wafer table with tags and links (Ch 9, 13, 14, 15, 17, Ch 6 #op-speed). This also covers the ch15-fixlog D4 table.
- **G2 Fixed (r3 G2; also r4-ch09 G3).**
  - The cost widget has a "Context per stream" input (cb preset only). It shows the KV-limited max streams: 36 GB, or ~21 GB after code (4.2 KB × ~900k × 4), ÷ 0.33 MB per token. It also shows the best $/M at that cap, flags streams that do not fit, and gives the capex needed for $0.60.
  - At 8K: 13 streams (~7) → $2.72 ($5.05). $0.60 needs capex ≤ $2.0M or contexts under ~1.9K.
  - The paragraph, the open question, the decision-table price row and quiz Q2 were rewritten to match. Analyst capex support was added (r3 G8: $2–3M per system; CG-1 ≈ $3.1M per CS-3).
- **G3 Fixed (r3 G3).**
  - New Lab 4 and Lab 5 lesson bullets. The Lab 5 bullet covers the allreduce fit, 60% at 16 × 16, the SC20 <1.5 µs on ~380k PEs against ≈57k cycles per call on 600 × 595 (≈35–45× at 0.85–1.1 GHz, Derived), and the 1,835-cell cap.
  - The solver row is qualified: "not with `<collectives_2d>` as shipped".
  - The SC20 allreduce figure is tagged Unverified (search extract, PDF not checked).
- **G4 Fixed (r3 G7).** The Prefill row links the 170 ms TTFT and CS-4 disaggregation (Ch 8 #cs4, Ch 9 #moe). Tenstorrent's "no disaggregation needed" counter-pitch was added (Vendor).
- **G5 Fixed (r3 G10).** index.html:
  - Added prerequisites and three short reader routes (hardware chooser, programmer, from CUDA).
  - The lede now says "five written for the course, two adapted from SDK benchmarks".
  - The "4 real problems" stat links to 18-comparison.html#lessons (new id).
  - Blurbs for Ch 12 (GEMV composition), 15 (allreduce dominates), 16 (scale-out, 70B on 32 chips) and 18 (decode case study, cost model) were extended.
  - Skipped: a time estimate, because no source exists for one.

## Other r3 items (not in the r4 list, done because cheap)
- r3 G8: MLPerf row is now "none in v6.0 (Apr 2026) coverage", tagged Press + Unverified. The capex analyst figures are under G2.
- r3 G9: Decoder item 6 now has the 2026 GPT-5.6 Sol "not … quantized" vendor quote.
- r3 G11 (README): Skipped. It is not my page.

## Cross-page items about Ch 18
- **r4-appE E5 Fixed.** The MD and SC20 rows are now class `indep` ("Peer-reviewed"), not `measured`.
- **r4-appE CS-4 row Fixed.** It now reads ">4,400 tok/s per user on gpt-oss-120B" (press release, 18 Aug 2026), not independently measured, with AA listing the hosted service at ~1,869. Tagged Vendor + Unverified.
- **r4-appD G3 Fixed** (the Ch 18 part): #next links App D #ladder.
- **r4-ch09 G3 Fixed** via G2.
- **r4-ch17 (LPX hedge repeated in Ch 18) Fixed** via E7/G4.

## Notes 30–38 applied
- 30: The lessons bullet uses the one rule (opposite halves of the 16-byte bank cycle; same bank halves the rate) and links Ch 6 #banks. The @fadds 2/cycle is explained by u[i]/u[i+2] being 8 B apart (no longer "on WSE-3"). The old "mod 4 words, differs by chip" wording is gone.
- 31: The Lab 3 hang now says launch() has returned and the next memcpy waits forever.
- 32: 7,500 is no longer presented as the one-user ceiling (#dc, #rf, chooser, quiz Q1 says "overstates").
- 33: The decode callout shows 850 MHz [SDK] and ~1.4 GHz [Analyst/Unverified] (4,600 vs 7,600 cycles per layer; the kernel-rate read is about the whole budget vs ~70%).
- 34: The 7P slope is explained as own-clock.
- 35, 36: Not on this page.
- 37: Already 90.
- 38: Linked the plain chapter mentions (Ch 1, 2, 8, 13, 16, 17; Lab 3), fixed a wrong link (`Chapters 10–14` pointed "14" at 17-gpu.html), and added glossary links at first use: memory wall, HBM, ridge point, PE, Tensix, SIMT, wavelet, color, fabric DSD, memcpy, microthread, circular buffer, KV cache, Groq LPX, SUMMA, prefill/decode, TTFT, disaggregation, cost per million tokens, hop, bank clash, weak scaling, TSC, allreduce.

## For other pages
- **Ch 15** (`15-lab-cg.html#scaling`): it says "we could not check that paper's allreduce latency". The SC20 figure (<1.5 µs on ~380k PEs, search extract) is now quoted in Ch 18; Ch 15 could cite it the same way. Ch 15 also uses 950 × 950 ≈ 900k as "whole wafer" while Ch 13/18 use CS-2's 737k. One convention ("CS-2 737k SDK-visible; CS-3 unpublished, ~900k") would help.
- **Ch 17**: B300 (288 GB) is still missing (r3 G5). The LPX "256 … 128 … not settled" hedge should match Ch 18 (256, ~128 GB, ~40 PB/s, in production).
- **Ch 1**: it compares H100 BF16 with Rubin NVFP4 ridge. That page already has the caveat; no change needed.
- **README.md**: r3 G11 (cycle table vs expected_output, noise caveat, Unverified tag, App E pointer) is still open.
- **Rubin status**: Ch 18's compare and chooser widgets label Rubin "(announced)", following Ch 17. r3 says Rubin ships in late 2026. If Ch 17 changes this, Ch 18's labels should follow.
