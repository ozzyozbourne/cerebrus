# Phase 3 · Architecture, systems and comparison coverage: does the course need more chapters?

## Verdict

**The course needs at most one new chapter, and only one is justified: split the inference half of Chapter 8 out into its own chapter.** The hardware story (Ch 1–7) is unusually complete. Yield, repair, power delivery, cooling and I/O are in Ch 2. Sparsity is in Ch 3 and Ch 8. Weight streaming, MemoryX, SwarmX and layer-pipelined mode are in Ch 8. The Tenstorrent and GPU comparison is in Ch 13–15. The one large, central gap is the path **from a model to tokens on wafers**. Today it is half of an already 4,600-word chapter, and its key question ("how does Cerebras get its tok/s?") gets the answer "the sources do not break this down" (Ch 8, decode worked example). Every other candidate fits as a section or an edit.

## Ranked new-chapter proposals

### 1. (Recommended) "From model to tokens: compiling and serving on wafers"

**Slot:** new Chapter 9, right after a slimmed Ch 8 ("Systems: training at scale"). Renumber Ch 9–15 to 10–16. Alternatively, keep the numbering by making it "8b". **Effort:** medium-high, about 4–5k words and 3 widgets. Most of the material already exists in the Ch 8 inference sections and the ch08-depth notes (D5–D11). The new parts are §2, §4, §5 and §6.

**Why.** An informed reader's first question after Ch 1 is how a wafer turns pinned weights into 2,000+ tok/s, and why the same hardware went from 450 to 2,100 tok/s. Here is what the course has now:
- the compiler path: one paragraph ("Where this sits for a CSL programmer", Ch 8);
- speculative decoding: two mentions (the Ch 8 speed table and a caveat);
- MoE: one sentence (Kimi K2.6 row);
- disaggregated prefill: one table cell (CS-4 "Use");
- the per-token latency budget: explicitly left open.

Ch 15's verdicts rest on decode, so the mechanism behind them deserves its own chapter. Moving these sections out also makes Ch 8 a reasonable length again.

**Outline**
1. **The compile path, PyTorch to wafer.** The steps are trace graph → match ops to a hand-written kernel library → choose each kernel's size (area vs time) → place kernels as rectangles on the fabric → route colours → link. Show the placement problem itself: kernels as rectangles with area/time trade-offs, with the goal of balancing the slowest stage against wire length. This is the same rectangle-and-route vocabulary as Ch 4 and Ch 9. Sources: Hot Chips 2020 Cerebras software talk (AnandTech live blog, anandtech.com/show/16006); ISPD 2020 contest "Wafer-scale DL accelerator placement" (Cerebras-sponsored; slides at ispd.cc, which could not be fetched from this session, so verify); Cerebras training docs "Weight Streaming Execution" (already cited in ch08-depth). Tag mostly Vendor/Secondary, and say plainly that the internals are closed.
2. **Two compile targets, one graph.** Streaming compiles one layer onto the whole wafer, for training. Pipelined compiles all layers as regions, for inference. Recap from Ch 8, then contrast how each sizes regions: by compute in training, by weights + KV + compute in inference (HC2024 "sized based on memory and compute requirements").
3. **The inference pipeline.** Move the existing Ch 8 material here: regions, one token per stage, multi-user filling, the inter-wafer budget, KV-cache arithmetic and the wafer-count widget.
4. **A decode latency budget.** A new Derived model: per-token time = Σ stages (GEMV time at measured ~4 B/cycle/PE from the SDK `single-tile-matvec` run already in Ch 8) + row/column reductions (Lab 2 hop costs, Ch 11) + inter-wafer hops (HC2024 <5 µs, CS-4 2 µs) + attention/KV reads. Have the reader reconcile it with the measured 2,100 tok/s (476 µs per token, Ch 8). This turns "sources do not break this down" into a bounded estimate built from the course's own measurements.
5. **Speculative decoding on an SRAM machine.** The mechanism: a draft proposes k tokens and the target verifies them in one k-wide pass. Explain why pinned weights make verification nearly free, because a k-token pass reuses each weight k times while the stages are latency-bound. Show how the acceptance rate maps to the speedup: expected tokens per step = (1−αᵏ⁺¹)/(1−α). Sources: Cerebras Oct 2024 blog (cerebras.ai/blog/cerebras-inference-3x-faster); Mistral Le Chat blog, Feb 2025 (>1,100 tok/s, spec decoding co-developed with Mistral; cerebras.ai/blog/mistral-le-chat); Leviathan et al. 2023 for the formula. Caveat: no Cerebras source quantifies the speedup from spec decoding alone.
6. **MoE, precision and disaggregation.** For MoE, every expert must be resident but only about 32B parameters are read per token (Kimi K2.6, Ch 8); expert placement keeps "tensor and expert communication within each wafer" (CS-4 blog). For precision, show 16-bit originals vs native 4-bit (Kimi). For disaggregation, prefill runs elsewhere (AMD Helios, Trainium) and decode runs on CS-4. Compare NVIDIA's own disaggregation on the GPU side (see edit E1).
7. **The speed history, explained.** Move the Ch 8 table here and attribute each jump: kernels, async I/O, spec decoding, CS-4 clock and hop latency.
8. **Where the SDK fits.** Map each production mechanism to the lab primitive that underlies it: GEMV region → Lab 2 distributed GEMV; reductions → Lab 2; data-triggered FMAC → Ch 5/6. ch08-depth §"toy inference pipeline in CSL" offers an optional exercise.

**Visuals/widgets:**
- (a) a "place the layers" toy: drag kernel rectangles onto a small fabric, with the slowest stage setting throughput;
- (b) a decode latency stacked-bar budget with sliders for hop µs, reduction cycles and clock;
- (c) a speculative-decoding calculator (α, k, draft cost → tok/s);
- reuse the existing pipeline-decode animation and the wafer-count widget.

### 2. (Not recommended as a chapter) "Other SRAM answers: Groq and the GPU's turn"

I considered a chapter on other accelerators and rejected it. It fails the "large, central gap" test, and the user asked for Tenstorrent and GPUs. **Groq is the one exception worth a section** (edit E1), because it now sharpens the GPU comparison directly.

## Smaller edits (by chapter)

- **E1 · Ch 14 + Ch 15 (high priority, factual currency): add NVIDIA–Groq.** Ch 15 says "NVIDIA now splits prefill onto Rubin CPX". Since then:
  - NVIDIA struck a ~$20B non-exclusive licensing-and-talent deal with Groq (Dec 2025).
  - At GTC 2026 it unveiled the Groq 3 LPU / LPX rack as a decode co-processor beside Vera Rubin NVL72. The chip has 512 MB SRAM per die and ~150 TB/s, against ~22 TB/s HBM4 per Rubin GPU. NVIDIA calls the split "Attention-FFN Disaggregation".
  - Rubin CPX is reported dropped, which NVIDIA has not confirmed.

  Sources: Tom's Hardware (tomshardware.com/tech-industry/semiconductors/nvidias-20-billion-groq-deal-produces-its-first-chip); Computer Weekly (computerweekly.com/news/366640398); The Register (theregister.com/2025/12/31/groq_nvidia_analysis). Rack size is reported as both 128 and 256 LPUs, so mark it unverified.

  Add a one-paragraph "The incumbent adopts SRAM decode" box to Ch 14's scaling section. Add a row to Ch 15's training/prefill/decode table and the bandwidth-cliff table. Add a sentence to Ch 1 "Three answers" saying the GPU answer now includes an SRAM chip. The comparison then becomes: many small SRAM chips (Groq, at ~0.5 GB each, needs hundreds per large model) versus one 44 GB wafer. This is a sharper version of Ch 2's reticle argument.
- **E2 · Ch 15:** Add one "other designs, one line each" note so readers can place TPU, Groq, SambaNova and AMD MI-series without a chapter:
  - TPU: systolic MXU + HBM + ICI torus, philosophically between GPU and Tenstorrent.
  - SambaNova: dataflow RDU with SRAM, HBM and DDR tiers.
  - AMD MI-series: HBM-heavy GPU, same class as NVIDIA.

  Tag all of these Secondary.
- **E3 · Ch 15:** Ch 15-depth D13 already plans HPC breadth (SDK FFT, BiCGStab/CG and other solver benchmarks; NETL CFD; seismic). Adopt it as a short section. It needs no chapter: Ch 2 (SC20 BiCGStab 0.86 PF), Ch 12 (stencil lab) and Ch 15 (MD 179×, decision row) already carry HPC.
- **E4 · Ch 8 (or new Ch 9):** Add "Sparsity in practice" (3–4 sentences). The mechanism is in Ch 3 and Ch 8 ("zero weights never sent"). What is missing is that production inference runs dense 16-bit or native-quantised weights, and that unstructured sparsity was a *training* claim. State that sparse-PF headlines (Ch 2) are not achieved on dense LLM serving.
- **E5 · Ch 2 or Ch 8:** Add a short "Reliability in service" note:
  - Ch 2 covers manufacturing yield only.
  - Say that field failure rates, MTBF and wafer-level fault handling are not public.
  - Training survives via MemoryX checkpoints (Ch 8, step 6).
  - CS-4 adds N+1 power redundancy and leak sensors (Ch 8 table).

  Contrast with TT-Fabric's automatic rerouting (ch13-depth note).
- **E6 · Ch 8:** Once proposal 1 moves the PyTorch paragraph, retitle "Where this sits for a CSL programmer" to point to the new chapter. Until then, add the HC2020/ISPD compile-steps list there (two sentences).

## Rejected ideas

- **Power and cooling chapter.** Already covered in Ch 2 ("Power, cooling and the edges", W/mm² vs H100), Ch 8 (CS-3 ~23 kW, CS-4 Nexus power/cooling table) and Ch 15 (cost and energy model). Independent energy data is missing, which no chapter can fix.
- **Yield/redundancy chapter.** Ch 2 has the Poisson model, the defect simulator, spare segments and the marketed-vs-visible core table. This is complete.
- **HPC/scientific chapter.** Ch 12 lab, Ch 15 MD/SC20 evidence and the decision guide cover it. Use E3 instead.
- **TPU / SambaNova / AMD chapter.** None of them sharpens Tenstorrent-vs-GPU-vs-wafer beyond what one line each gives (E2), and they would dilute the user's requested comparison. Groq is the one with real bearing, and it is handled in E1.
- **Training-at-scale deep dive (µP, sparse training recipes, Condor Galaxy results).** Ch 8 already covers the mechanism. The independent evidence is absent (Ch 15: "training: vendor only"), so a chapter would be vendor narration.
- **Quantization chapter** (Ch 1 and Ch 3/13/14 cover formats; the rest fits in proposal 1 §6) and **inference-business chapter** (not architecture; Ch 8's cost box and Ch 15's cost model suffice).
