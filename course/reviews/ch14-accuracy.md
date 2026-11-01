# ch14 · accuracy review

Summary: The chapter's core numbers are accurate and match the research notes and the report: H100 132 SMs, 256 KB RF, 256 KB L1/smem (228 KB shared), 50 MB L2, 80 GB HBM3 at 3.35 TB/s, 989/1,979 TF; B200 192 GB, ~8 TB/s, 9/18 PF FP4, 10 TB/s NV-HBI; NVL72 72×1.8 ≈ 130 TB/s; Rubin 288 GB, 19.2/22 TB/s, 3/3.6 TB/s, 216/260 TB/s. The CUDA and CSL SAXPY code is correct, and the CSL matches `programs/01-saxpy/pe_program.csl`. The occupancy widget's simulation agrees with its formula. The problems are mainly provenance and framing. The one independent number (L2 ~3.8 TB/s) comes from an H100 *PCIe* test whose headline figure is >5.5 TB/s. The Rubin "NVIDIA says…" quote is presented as fact, but it is unverified and other coverage contradicts it. The "21 warps per scheduler" quiz answer exceeds H100's hardware limit without saying so. There are also several smaller tag and wording issues. Verdict: sound, needs a handful of targeted edits. Nothing is critical.

## Findings

### A1 [major] L2 "~3.8 TB/s measured" is attributed to the wrong H100 variant and is not the article's headline figure
- **Location:** line 33 (table footnote: "Chips and Cheese measured ~3.8 TB/s aggregate L2 read bandwidth on H100 Indep") and line 120 (hierarchy SVG label "50 MB / chip · ~3.8 TB/s measured"). The whole figure is captioned as H100 SXM-centric.
- **Problem:** Chips and Cheese tested the **H100 PCIe** card (114 SMs, HBM2e, 350 W) on Lambda Cloud, not the SXM part the table describes. The search extract of that article says "Starting at the L2 cache, we see **over 5.5 TB/s** of read bandwidth". Other secondary sources (the JAX scaling book) also quote ~5.5 TB/s. The 3.8 TB/s figure appears only in our research notes ("about 3.8 TB/s … from the full 50 MB L2"). I could not find it in any search result, and the article could not be fetched (the host is blocked). It may be the full-50 MB / far-partition figure, but that is unconfirmed. Either way, presenting it as an SXM number is wrong.
- **Evidence:** WebSearch extract of chipsandcheese.com/p/nvidias-h100-funny-l2-and-tons-of-bandwidth: "tested the PCIe version of H100 on Lambda Cloud … 114 SMs, 50 MB of L2 … over 5.5 TB/s of read bandwidth". Notes line 15. A search for `"H100" L2 "3.8 TB/s"` returned no source.
- **Concrete fix:**
  - Line 33: replace "Chips and Cheese measured ~3.8 TB/s aggregate L2 read bandwidth on H100 <span class="tag indep">Indep</span>." with "Chips and Cheese measured over 5.5 TB/s of L2 read bandwidth on an H100 <em>PCIe</em> card (114 SMs), falling for data spread across both L2 partitions <span class="tag indep">Indep</span>."
  - Line 120 label: "50 MB / chip · ~5.5 TB/s measured (PCIe card)".
  - If the coordinator can confirm 3.8 TB/s from the article as the full-50 MB figure, keep it and add "(PCIe card, full 50 MB)" instead.

### A2 [major] Rubin quote "reflect what the system sustains at quality, volume production" is stated as fact but is unverified and contradicted
- **Location:** line 36 (callout "Specs are targets").
- **Problem:** The notes hedge this ("NVIDIA **reportedly** says"). The chapter drops the hedge and quotes it as NVIDIA's own words with no tag. A search found the spec cut itself (19.2/3/216 TB/s), but several reports say NVIDIA changed the page **without explanation**. The pasqualepillitteri.it Chinese edition says "Nvidia did not offer any explanation", and TweakTown says the change was made "quietly … without any announcement". The Wccftech "official statement" source could not be fetched. "At launch" is also imprecise. The 22 TB/s figure was the CES/GTC 2026 announcement figure, listed on the page in February under a "subject to change" caveat. It was not a launch spec, and an even earlier target was 13 TB/s (notes line 28).
- **Evidence:** Notes line 28. WebSearch results: tweaktown.com/news/114304, pasqualepillitteri.it/en/news/27546 and its zh edition, xenospectrum.com.
- **Concrete fix:** Replace the first two sentences with: "NVIDIA's Vera Rubin NVL72 page now lists 19.2 TB/s HBM4 and 3 TB/s NVLink 6 per GPU, down from the 22 and 3.6 it showed at announcement (an even earlier target was 13 TB/s) <span class="tag vendor">Vendor, via secondary reporting, autumn 2026</span>. One report quotes NVIDIA as saying the new figures "reflect what the system sustains at quality, volume production"; others say the change was made without explanation." Also change the table's "launch spec" to "announced" in three cells (lines 28, 30, 31).

### A3 [major] Quiz answer "21 warps per scheduler" exceeds the H100 limit; widget calls one scheduler "the SM's scheduler"
- **Location:** line 111 (quiz 2), line 56 (widget hint), lines 58 and 143–145 (widget).
- **Problem:** The arithmetic (400+20)/20 = 21 is correct, and so is the model ⌈(C+L)/C⌉ (Little's law for one in-order issuer). However, an H100 SM has **four** warp schedulers and at most **64 resident warps** (2,048 threads), which is **16 warps per scheduler**. So 21 per scheduler (84 per SM) cannot be reached. Real kernels close the gap with instruction-level and memory-level parallelism: several independent loads in flight per warp. Separately, the widget hint says "The SM's scheduler issues from any ready warp", which models the SM as one issuer, while the quiz says "per scheduler". The widget slider stops at 16, which happens to equal the real per-scheduler limit, but this is not explained, and the quiz scenario cannot be reproduced in the widget.
- **Evidence:** Notes line 46 (64 warps / 2,048 threads per SM, 4 sub-partitions each with 1 scheduler, flagged as from the whitepaper). WebSearch: CUDA compute capability 9.0 has 64 resident warps per SM (docs.rs optirs-gpu occupancy table, Wikipedia Hopper table), and the Modular handbook says an H100 SM has four schedulers. The chapter itself says "up to 2,048 threads" on line 65.
- **Concrete fix:**
  - Line 56 hint: "Each warp computes for C cycles, then waits L cycles for memory. One warp scheduler (an H100 SM has four, each holding at most 16 warps) issues from any ready warp. How many warps does it take to keep the math busy?"
  - Line 111 answer: "About (C + L) / C = 420 / 20 = 21 warps per scheduler. That is more than the 16 an H100 scheduler can hold (64 per SM), so real kernels also issue several independent loads per warp before waiting (instruction-level parallelism), which divides the warps needed."

### A4 [minor] Quiz 3's "1,979 TF" is ambiguous because it is also H100's dense FP8 figure
- **Location:** line 112.
- **Problem:** 1,979 TF is BF16 *with 2:4 sparsity*, but it is also the *dense FP8* peak of H100 SXM. The notes' own summary table lists "~1,979 TF FP8 dense" (line 37). The question as written ("the H100's 1,979 TF figure") has two correct readings.
- **Evidence:** Notes lines 17 and 37. Report line 235.
- **Concrete fix:** Summary: "Why does the H100's 1,979 TF <em>BF16</em> figure need care?" Answer: "It assumes 2:4 structured sparsity. Dense BF16 is ~989 TF (1,979 TF is also the dense <em>FP8</em> peak, so always check format and sparsity). The same trap applies to Cerebras's sparse 125 PF."

### A5 [minor] Rubin "Dies" cell is blank although the notes give two compute dies
- **Location:** line 27, Rubin column ("—").
- **Problem:** The notes say "Each Rubin GPU package has two compute dies", and secondary sources describe two reticle-sized compute dies plus I/O dies. This is also the reason for the NVL144/NVL72 naming. A dash suggests the information is unknown.
- **Evidence:** Notes line 27. WebSearch (cyfuture, cudocompute, vrlatech): "Dual reticle-sized compute dies + I/O dies (CoWoS-L)".
- **Concrete fix:** Replace "—" with "2 reticle-size compute dies + I/O dies (hence "NVL144" counting dies = NVL72 counting packages)".

### A6 [minor] Lede says "tens of thousands of threads"; an H100 holds hundreds of thousands
- **Location:** line 13.
- **Problem:** 132 SMs × 2,048 resident threads = 270,336 threads in flight on H100 SXM. "Tens of thousands" understates this by an order of magnitude.
- **Evidence:** Line 65 of the chapter ("up to 2,048 threads" per SM), the 132 SMs in the table, and the CC 9.0 limits (see A3).
- **Concrete fix:** "…with caches and with hundreds of thousands of threads (up to ~270,000 resident on an H100) that take turns."

### A7 [minor] Derived numbers carry Vendor tags or no tag
- **Location:** line 44 ("Total register + L1 ≈ 66 MB", inside a caption tagged Vendor, Hopper whitepaper). Line 106 ("~130–216 TB/s" untagged; "a 70B FP16 model fits on one B200" untagged). Line 65 ("up to 2,048 threads" untagged). Line 33 footnote ("All Vendor") covers "~180 usable", which comes from cloud providers and SemiAnalysis InferenceX, not from NVIDIA.
- **Problem:** The brief requires every number to carry a tag. 66 MB is computed as 132 × (256+256) KB = 66 MiB ≈ 69 MB, and the report tags it [Derived] (report line 259). The 70B-fits claim is derived: 140 GB of weights in ~180 GB usable, leaving ~40 GB for KV cache.
- **Evidence:** Notes lines 22 and 85. Report lines 259 and 265.
- **Concrete fix:**
  - Line 44: "Total register + L1 ≈ 66 MiB <span class="tag derived">Derived</span> — compare with 44 GB of SRAM on a WSE-3 <span class="tag vendor">Vendor</span>."
  - Line 33: append "The ~180 GB usable B200 figure is what clouds expose <span class="tag analyst">Analyst</span>."
  - Line 106: "…(NVLink/NVSwitch, 72 GPUs at ~130 TB/s on GB200 and ~216 TB/s on Rubin <span class="tag vendor">Vendor</span>)…" and "…a 70B FP16 model (~140 GB) fits on one B200 with ~40 GB left for KV cache <span class="tag derived">Derived</span>…".
  - Line 65: add `<span class="tag vendor">Vendor</span>` after "2,048 threads in flight".

### A8 [minor] Rubin "50 PF NVFP4 inference" mixes metrics with the dense H100/B200 cells
- **Location:** line 29.
- **Problem:** The H100 and B200 cells are labelled dense. Rubin's 50 PF is NVIDIA's *inference* figure. Several secondary sources describe it as "effective" FP4 via Transformer Engine adaptive compression, and the training figure is 35 PF (notes line 27). Without a qualifier, readers will compare 50 against 9 as like for like.
- **Evidence:** Notes line 27 ("50 PF NVFP4 for inference and 35 PF NVFP4 for training"). WebSearch (cyfuture / vrlatech): "35 PFLOPS … up to 50 PFLOPS effective FP4 for inference via Transformer Engine".
- **Concrete fix:** "50 PF NVFP4 inference / 35 PF training (inference figure relies on Transformer Engine compression)".

### A9 [minor] Overstated SIMT and communication wording
- **Location:** line 48 ("Threads execute in warps of 32 in lockstep"; "can share that SM's shared memory") and line 103 ("threads in different blocks share data through HBM and kernel boundaries").
- **Problem:**
  - Since Volta, threads have independent program counters (independent thread scheduling), so "in lockstep" is a simplification.
  - A block shares *its own allocation* of shared memory, not the SM's whole pool.
  - On Hopper, blocks in a thread-block cluster can share data through distributed shared memory (DSMEM). Blocks can also communicate within a kernel through global-memory atomics and the L2, not only across kernel boundaries. The notes themselves list "DSMEM in clusters" under Communication (line 124).
- **Evidence:** Notes lines 46, 65 and 124. Report line 280 (TMA, clusters).
- **Concrete fix:**
  - Line 48: "Each block is assigned to one SM and gets a slice of that SM's shared memory. Threads are issued in <strong>warps of 32</strong> that normally run in lockstep;…"
  - Line 103: "…on a GPU, threads in different blocks share data mainly through L2/HBM (atomics, or kernel boundaries), plus distributed shared memory within a Hopper thread-block cluster;…"

### A10 [minor] "Nothing to hide" on the wafer and "a handful of tasks" overclaim
- **Location:** line 65.
- **Problem:** Local SRAM is single-cycle, but fabric latency still exists. CSL hides it with async DSD operations on microthreads and with pipelining, as the notes' own comparison table says: "Pipelining through the fabric; microthreads" (report line 274). Also, a PE has dozens of task IDs (WSE-2 data tasks 0–23 and local tasks up to 30, report line 93), not "a handful".
- **Evidence:** Report lines 56, 93 and 274.
- **Concrete fix:** "The wafer needs much less of this: a PE's own memory answers in one cycle, so only fabric latency remains, and that is hidden by async operations and pipelining rather than by thread count. That is why a Cerebras PE gets by with a few dozen task IDs and 8 microthreads, while an H100 SM keeps up to 2,048 threads in flight."

### A11 [minor] Callout equates Tenstorrent's firmware de-rate with a pre-production spec revision
- **Location:** line 36 ("Tenstorrent's firmware de-rating (Chapter 13) is the same story").
- **Problem:** Tenstorrent cut the spec of cards already shipped (140→120 cores via firmware, notes line 199). Rubin's figures were revised before volume shipment. Both support "vendor numbers are targets", but they are not the same story.
- **Evidence:** Notes lines 28 and 199.
- **Concrete fix:** "Tenstorrent's firmware de-rating of already-shipped Blackhole cards (Chapter 13) is a cousin of the same story."

## Not verifiable
- The exact Chips and Cheese numbers (5.5 vs 3.8 TB/s, near vs far partition). chipsandcheese.com is outside the session's allowed network domains, so only search extracts were available.
- The NVIDIA quote "reflect what the system sustains at quality, volume production". The Wccftech source is outside the allowed network domains, and the NVIDIA Rubin page was not fetched.
- The Rubin current-spec figures (19.2 TB/s, 3 TB/s, 216 TB/s) are confirmed only through secondary reporting (pasqualepillitteri.it, TweakTown, Hashrate Index), not on nvidia.com directly.
- B200 9/18 PF FP4 and the 10 TB/s NV-HBI link are consistent with secondary sources and with DGX B200 totals (144 PF FP4 sparse ÷ 8 = 18), but the primary datasheet was not fetched.
- GB200 NVL72's 13.4 TB / 576 TB/s is vendor via secondary. It matches 72 × ~186 GB and 72 × 8 TB/s.
- The hierarchy latencies ("~1 cycle", "tens of cycles", "hundreds of cycles") are qualitative and plausible, but no measured source is cited.
- Quiz 1 (stride-2 halves effective bandwidth) is correct by sector arithmetic: 256 B touched for 128 B used. This assumes no later reuse from cache.
