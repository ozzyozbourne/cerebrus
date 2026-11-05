# R3 gap audit: Ch 18 (Head to head), index.html, README.md

Scope: `18-comparison.html`, `index.html`, `course/README.md`. Read against CROSS_CHAPTER_NOTES 1–29, ch15-fixlog (old numbering = Ch 18), Ch 8/9/13/14/15, App E. Rendered both pages in Playwright at 1100 and 390 px: no errors and no horizontal scroll. Web check done 2026-11-05. cerebras.ai, arxiv.org and tomshardware.com are blocked from this session, so web facts below come from search extracts.

## Gaps, ranked

**G1 · high · Ch 18 "Choosing", widget `#ch` (Will it fit).** The "Per-user ceiling" column for Cerebras is the aggregate ceiling. Rendered for 70B, 16-bit: CS-3 shows **600k** and the CS-4 rack **1,851k** tok/s per user. The decode callout in the same chapter, and notes 25 and 27, say one user sees about 1/80 of that: ~7,500 at headline bandwidth and ~2,000–4,000 at real kernel rates. The readout also blames "pipeline latency" alone, which contradicts note 25's wording ("per-region SRAM reads plus latency"). A learner gets two different per-user ceilings on one page.
*Fix:* for the Cerebras rows, compute the per-user ceiling as aggregate ÷ layer count. Add a layers input, or use L ≈ 80 for 70B, 126 for 405B and 61 for 671B. Show the aggregate in a separate "all users" column, and reuse the callout's wording. *Resolvable:* yes, writing only. *Effort:* S.

**G2 · high · Ch 18 "Cost and energy per token", the `#cost` widget and Open questions.** The page says $0.60/M "implies roughly 60 concurrent streams" and lists stream count as unanswered by the sources. Chapter 9 already derives a cap from KV capacity: a 4 × CS-3 Llama-70B deployment holds **at most ~13 users at 8K (~7 after code)**, or ~27k tok/s in total (note 28). At 13 streams the widget gives ≈ $2.7/M at $10M capex, so the $0.60 price needs capex near $2M, shorter contexts, or KV held off-wafer. The chapter never makes this link, and it is the course's strongest evidence on cost.
*Fix:* add a "KV-limited max streams" readout that reuses Ch 9's 110k-token budget, with a context-length input. Cap or flag streams above it. Rewrite the paragraph and the open question. *Resolvable:* yes, writing only. *Effort:* M.

**G3 · high · Ch 18 "What programming the wafer taught us", "Choosing" (solvers row), "What the evidence shows", Open questions.** The chapter's lessons stop at Lab 3. The only Lab 4 material is the GEMM paragraph, and Lab 5 (CG) is never drawn on. Missing items:
- The utilisation the course measured itself: GEMM 18–32% of the f32 ideal (51% after the rewrite), and CG 1.3% at Z = 5 and ~17% at Z = 100. The Open questions still say "CS-1's ~1/3 of peak is the only data point".
- The finding that the SDK allreduce is linear in W + H (≈ 958 + 100·W + 88·H cycles per iteration) and already takes 60% of an iteration at 16 × 16.
- The CG memory cap of ≈ 1,835 cells per PE.

The web check also closes App E's open item for Ch 15: the SC20 paper (Rocki et al.) reports a scalar AllReduce of **< 1.5 µs on ~380k PEs** for 0.86 PF BiCGStab on a 600 × 595 × 1536 mesh. On a 600 × 595 grid Lab 5's fit gives ≈ 113k cycles per iteration (two calls), roughly 56k per call. A hand-built reduction is therefore about 30× faster than the SDK library at wafer scale. That matters for the solver row of the decision table: "try it, but not with `<collectives_2d>` as shipped". The 1,536-cell column also agrees with Lab 5's ~1,835 cap.
*Fix:* add one lesson bullet each for Lab 4 and Lab 5. Cite the SC20 allreduce (tag it peer-reviewed with Cerebras authors) and remove the "only data point" wording. Change "five programs" to seven. *Resolvable:* yes, web plus writing (confirm against the arXiv PDF once arxiv.org is allowed). *Effort:* M.

**G4 · med · Ch 18 "Many small SRAM chips" callout.** These statements are stale:
- "No independent LPX decode measurement exists yet." Artificial Analysis measured **3,431 output tok/s on Gemma 4 31B at 100K context**, presented by NVIDIA at Hot Chips 2026.
- "256 per rack (some reports say 128)." This is now settled at 256 LPUs, 128 GB and ~40 PB/s, and the rack is in full production (customers named: Nebius, CoreWeave).

Rubin CPX is still not officially cancelled, so its Unverified tag stays. *Fix:* update the wording and tags, and also in Ch 17. *Resolvable:* yes, web. *Effort:* S.

**G5 · med · Ch 18 tables, quiz Q2, chooser, "Other designs".** The NVIDIA side stops at H100/B200: "capacity per device 80–192 GB" and quiz Q2 "2–4× (80–192 GB vs 44 GB)". By late 2026 the shipping parts are **B300 (288 GB HBM3e)** and **Rubin (288 GB HBM4, 19.2 TB/s)**. AMD **MI455X (432 GB HBM4, ~19.6–23 TB/s, Helios shipping Q3 2026)** supersedes the MI355X line. Google's TPU line moved to **TPU 8t/8i** (Apr 2026); the 8i has 288 GB HBM, 8.6 TB/s and 384 MB on-chip SRAM, a relevant SRAM-leaning inference design. Ch 17 has no B300 either.
*Fix:* add B300 and Rubin rows to the chooser. Change the capacity range to 80–288 GB (~2–6.5×). Update the TPU and AMD lines. *Resolvable:* yes, web. *Effort:* M.

**G6 · med · Ch 18 evidence table, cost widget, decision table.** The "$0.60 list price, Llama 3.1-70B" is a 2024 figure. Price aggregators now list Llama 3.3-70B on Cerebras at **$0.85 in / $1.20 out per M**, with some saying it is dedicated-endpoint only. The sources conflict. *Fix:* re-check cerebras.ai/pricing, date the price, and carry the change into the widget target and Q2. *Resolvable:* yes, web (needs cerebras.ai allowed). *Effort:* S.

**G7 · low · Ch 18 "Training, prefill and decode", Prefill × Cerebras.** The cell omits that CS-4 advertises disaggregated inference, with prefill on another platform (AMD Helios or Trainium) and decode on CS-4. Ch 8 states this. *Fix:* one sentence with a link to Ch 8. Also note Tenstorrent's counter-pitch, "no disaggregation needed" (Galaxy Blackhole, TTFT < 4 s, Vendor). *Resolvable:* yes, writing only. *Effort:* S.

**G8 · low · Ch 18 evidence table and the cost widget's capex tag.** Two items can now be upgraded:
- "MLPerf: none found" can become sourced: coverage of MLPerf Inference v6.0 (Apr 2026) reports Cerebras absent again, and Tenstorrent is not listed.
- The Unverified $8–12M capex has analyst support. NextPlatform puts Condor Galaxy-1 at $100M for 32 nodes ≈ $3.1M per CS-3, so 4 nodes ≈ $12.5M including MemoryX/SwarmX; other analysts say $2–3M per system.

*Resolvable:* yes, web. *Effort:* S.

**G9 · low · Ch 18 decoder item 6 ("Quantised?").** The only evidence is from October 2024. Cerebras's 2026 GPT-5.6 Sol post says the model is "not … quantized to lower precision", which is a newer data point. *Resolvable:* yes, web. *Effort:* S.

**G10 · low · index.html.** Three issues:
- There are no prerequisites, no time estimate and no alternative routes for readers with a single goal, for example a buyer/architect (1, 2, 8, 9, 16–18) or a programmer (3–7, 10–15, App B/C). The only advice is "read in order".
- The lede says "seven **original** programs", but the README says 06 and 07 are adapted from SDK benchmarks.
- The stat "4 real problems … explained" has no link to where they are (Ch 18 "What programming taught us").

*Resolvable:* yes, writing only. *Effort:* S.

**G11 · low · README.md.** Four issues:
- The cycle table disagrees with `expected_output.txt`: 6,860 vs 6,861, 11,665 vs 11,666, 36,971 vs 36,959 and 145,003 vs 145,166.
- There is no note that whole-run counts vary by +1–4% (note 17).
- The tag list omits Unverified.
- There is no pointer to Appendix E for checking sources.

*Fix:* copy the numbers from the expected outputs and add a noise caveat. *Resolvable:* yes, writing only. *Effort:* S.

**G12 · low · Ch 18 "Back to the memory wall" / Lab 3 widget.** The page says "memory was never the bottleneck", but Lab 5 shows the memory cap (≈ 1,835 cells per PE) and BLOCK buffers trading memory for speed. Qualify it to "bandwidth was never the bottleneck; capacity was". *Resolvable:* yes, writing only. *Effort:* S.

## Not gaps (checked, rejected)

- Stencil extrapolation arithmetic (7.7 × 10¹³, 2.5 × 10¹⁴, 4.2 × 10¹¹, 180–600×): recomputed, correct.
- Decode callout (432 µs, 5.4 µs, ~4,600 cycles, 1.75 GB at ~1 PB/s): correct and matches notes 25 and 27.
- Cost widget, 1 stream ≈ $35/M at $10M / 4 yr / 92 kW: correct.
- Lab 3 numbers (130.2 / 130.8, 134.1, 5,450, 14.6, 178) match Ch 13.
- GEMM numbers (2,569 / 103,724 / 32% / 51% / ≈37) match Ch 14.
- 16 × 16 Lab 5 claim and the `#scaling` anchor exist; `17-gpu.html#groq-lpx` exists.
- CS-4 rack 132 GB / 129.6 PB/s matches Ch 8.
- Rubin HBM4 22 → 19.2 TB/s is confirmed as current. (Also new: NVLink 6 went from 3.6 to 3 TB/s; optional.)
- Kimi K2.6 981 tok/s (AA, measured 6 May 2026): correct date.
- GPT-5.6 Sol 750 tok/s, limited preview: confirmed (Aug 2026).
- CS-4 "4,400 tok/s": still vendor-only; the Unverified tag is right.
- Galaxy Blackhole $110k, 350 tok/s/user at batch 32 on 16 Galaxies; QuietBox 2 $9,999; p150 140 → 120 cores: confirmed.
- Index stats: 90 widgets (counted 90); 7 / 7 programs and `setup.sh` exist; the kicker says 18 chapters and 5 appendices.
- No console errors or overflow on either page at 390 / 1100 px.
- Index map white text on coloured bars: style issue, not a gap.
