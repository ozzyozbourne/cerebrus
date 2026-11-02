# Build: NVIDIA/industry update (Ch 17, 18) + Appendix E

## Task 1: NVIDIA, Groq and other designs

### Verification (web search, 2026-11-02; WebFetch blocked for nvidia.com and tomshardware.com, so these are search extracts)
| Claim (phase3-architecture E1) | Result | Tag used | Sources |
|---|---|---|---|
| ~$20B NVIDIA–Groq deal, Dec 2025 | Non-exclusive licence + hires (Ross, Madra), announced 24 Dec 2025 by Groq; Groq stays independent, GroqCloud continues. **$20B is a CNBC figure, not confirmed by either company.** | Vendor, Groq newsroom; price Unverified, press report | groq.com/newsroom/groq-and-nvidia-enter-non-exclusive-inference-technology-licensing-agreement-…; constellationr.com; theregister.com/2025/12/31/groq_nvidia_analysis |
| Groq 3 LPU / LPX at GTC 2026 as SRAM decode co-processor beside Vera Rubin | Confirmed: GTC 16 Mar 2026, chip LP30 (Samsung 4 nm). NVIDIA term "Attention-FFN Disaggregation": Rubin = prefill + attention/KV, LPU = decode FFN/MoE, Dynamo routes. 35×/MW vs Blackwell NVL72 is a vendor projection. | Vendor via secondary | hpcwire.com/2026/03/16/…; tomshardware.com/…/nvidias-20-billion-groq-deal-produces-its-first-chip; hashrateindex.com/blog/nvidia-vera-rubin-reference-architecture; counterpointresearch.com GTC 2026 note; groq.com/blog/groq-among-the-first-… |
| 512 MB SRAM/die, ~150 TB/s | 150 TB/s consistent; SRAM given as 500 MB (NVIDIA pages, StorageReview, KGI) or 512 MB (Tom's, Counterpoint). Course says "about 500 MB (512 MB in some reports)". ~2.5 TB/s scale-up per chip. | Vendor via secondary | storagereview.com/news/nvidia-groq-3-lpx-everything-we-know |
| Rack 128 or 256 LPUs | Most sources and NVIDIA's localised LPX pages: 256 (ABI: 32 trays × 8), ~128 GB, ~40 PB/s, 640 TB/s scale-up. One (ServeTheHome via Ground News) says 128. Course states 256 with the dissent noted. | Vendor via secondary | nvidia.com/ja-jp/data-center/lpx (via search); abiresearch.com |
| Rubin CPX dropped | Absent from GTC 2026 slides/roadmap; Korean/Taiwanese supply-chain reports call it shelved. NVIDIA has not confirmed. | Unverified | 3dtested.com (Tom's reprint); hashrateindex |
| TPU / SambaNova / AMD lines | Ironwood: 192 GiB HBM ~7.37 TB/s, ICI 3-D torus to 9,216 chips (Google docs). SN40L: 520 MB SRAM, 64 GB HBM, 1.5 TB DDR (datasheet says 768 GB). MI355X: 288 GB HBM3E, 8 TB/s. | Secondary (tag indep, as in ch02/ch03) | docs.cloud.google.com/tpu/docs/tpu7x; arXiv 2405.07518, HC2024 SambaNova; amd.com MI355X page |

### Edits
- **17-gpu.html**: new callout `#groq-lpx` "2026: the incumbent adds an SRAM decode chip" at the end of "Scaling out" (deal, LPX specs, AFD, Derived per-chip comparison: ~8× Rubin bandwidth for 1/576 capacity; 256-LPU rack's 128 GB can't hold Llama-70B FP16, FP8 needs ~140 LPUs; CPX note Unverified; sources + link to Appendix E). One new quiz question. The Ch 13 pointer sentence (line ~209) was not touched.
- **18-comparison.html**: Prefill row (CPX → Unverified, shelved); Decode row (AFD + LPX); bandwidth-cliff table gets a Groq 3 LPU row (~60× cliff, Derived); new callout `#sram-chips` "Many small SRAM chips, or one 44 GB wafer" with a Derived table (88 LPUs ≈ one wafer's SRAM; rack ≈ 2.9 wafers capacity, 1.8 wafers bandwidth; rack scale-up ~1/42 of one wafer's fabric; Llama-70B counts) and the reticle argument; new callout `#other-designs` with TPU, Groq, SambaNova, AMD lines (Secondary); NVIDIA strengths row and "Back to the memory wall" get one clause each. GEMM sentence untouched; no widget code changed.

## Task 2: Appendix E (`course/appendix-e-sources.html`)
- §1 tag table (8 tag kinds incl. "Vendor via secondary") and a 6-step "how to check a figure".
- §2 bibliography: generated, 286 distinct sources in 10 topic groups (incl. 85 local SDK files, shown as paths), each with where it is cited (report / note / chapter / "Ch 17/18 update").
- §3 widget `#tc`: tag-class toggle chips, sort (course order / most tags / most flagged), claim search, clickable HTML stacked bars per page (hatched for unwritten pages), counts table with totals and a "via sec." column; filters the generated flagged list (54 rows: 18 Unverified, 36 via-secondary) with chapter, claim, tag, why, what would settle it.
- §4 seven open issues (bank model, clash rule, WSE-2 @fadds, WSE-2 hop floor, microthread datapath, .index units, @fscales/@fnorms) with Measured / Unknown / Would settle it, numbers taken from CCN and fix logs (no new measurements this session).
- **Generator**: `course/tools/scan_tags.py` (`--check` for counts only). Splices between `<!-- scan:begin/end -->` and `<!-- bib:begin/end -->`. Generated 2026-11-02: 15 written pages, 992 static tags. Re-run after the parallel agents add Ch 9, 14, 15 and Appendices A–D (they show as "not written yet" now). Limits: JS-drawn tags are not counted; "why/settle" are keyword rules; claim text is a sentence heuristic.

## reports/ and research_notes/
- Report: new "Errata / superseded by course measurements" table at the top (12 rows: clock, bank units, usable SRAM, "at least 7 columns", hop cost, DSD rates/bank clash, unblock_cmd_stream abort, queue/microthread collision, decode not BW-bound, CS-6 wording, Blackhole vs Wormhole L1/NoC, Rubin CPX → Groq LPX, TSC timing).
- Each of the 4 research notes got a one-paragraph errata pointer at the top naming the affected items.

## Validation
Playwright, appendix-e / 17 / 18 at 1100 and 390 px, light and dark, plus ◐ toggle: 0 page/console errors, 0 px overflow. Widget driven: chips, sort, search, bar click, table-row click, keyboard Enter, clear. Screenshots inspected, then deleted.

## Open issues
- nvidia.com, tomshardware.com could not be fetched; all LPX numbers are from search extracts → tagged Vendor via secondary. Rack size 128 vs 256 is not fully settled.
- Ch 1's "Three answers" sentence (phase3 E1) is outside this task's files and was not edited.
- course.js / course.css unchanged. No git operations.
