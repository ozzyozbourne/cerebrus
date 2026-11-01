# ch14 · depth review

Summary. Chapter 14 is a short survey (about 10 KB): a generation table, a four-level memory hierarchy, a SIMT paragraph, an occupancy widget, SAXPY in CUDA and CSL, and one paragraph on scaling. It covers none of the internal mechanisms in this review's brief. There is no SM anatomy and no Tensor Core, so the source of the headline FLOPs is never explained. There is no tiled matmul, so the reader never sees how a GPU gets above the HBM roofline. Per-scheduler warp issue, TMA, warp specialisation and Blackwell TMEM are all absent. There is no walk-through of an LLM decode step, which is the course's central comparison. NVLink, NVSwitch, tensor parallelism and pipeline parallelism get one sentence and no numbers. The notes (`gpu_and_comparison.md` §1 Gaps, §2 Gaps) already list most of these items as unverified background. The priority is to add them with derived numbers that a learner can check, carrying provenance tags.

Source caveat. In this session `developer.nvidia.com` and `docs.nvidia.com` did not resolve. Both hosts must be allowed in the session's network settings before anyone can fetch them. Everything below comes from search extracts and the author's background knowledge of the Hopper whitepaper, the CUDA Programming Guide and the PTX ISA. Items marked **verify** must be checked against the named primary document before they ship. Numbers marked **derived** are arithmetic from those inputs and should carry the `derived` tag.

## Gaps and additions (prioritised)

### D1 [critical] SM anatomy and how a Tensor Core produces the headline FLOPs
**What is missing.** The chapter never opens the SM. Missing items:
- the four SM sub-partitions (SMSPs);
- per-SMSP resources: warp scheduler, 64 KB register file slice, 32 FP32 lanes, 16 INT32, 16 FP64, one 4th-gen Tensor Core, LD/ST and SFU units;
- the shared L1/shared-memory pool and the TMA unit;
- the fact that roughly 94% of H100 BF16 throughput comes from Tensor Cores, not from the FP32 lanes.

"Tensor Core" does not appear anywhere on the page. The pedagogy review raises the same problem (P1).

**Why it matters.** The generation table quotes 989 TF, 9 PF and 50 PF, but the learner has no model of where those numbers come from. Without the Tensor Core, the comparison with a Cerebras PE (FMAC datapath, SIMD on DSDs) and a Tensix core (FPU matrix engine) has no anchor.

**Source.**
- NVIDIA H100 Tensor Core GPU Architecture whitepaper v1.02, SM and Tensor Core sections ([mirror](https://www.hpctech.co.jp/assets/images/info/catalog/pdf/gtc22-whitepaper-hopper_v1.02.pdf)).
- "NVIDIA Hopper Architecture In-Depth" blog (developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/; fetch blocked, search extract confirms "2x the MMA rates of A100 per SM").
- PTX ISA, sections "wgmma" and "mma".
- Secondary corroboration: [cudacourseh100 lesson 1](https://cudacourseh100.github.io/pages/lesson-1.html), [ANU COMP4300 lecture 18](https://comp.anu.edu.au/courses/comp4300/assets/lectures/Lecture_18_Week_10_JAT.pdf).

**Proposed addition.** Add a new section, "Inside one SM", between "Three generations" and "The memory hierarchy".
1. **Static SVG of the SM.** Draw four SMSP quadrants. Label each with: warp scheduler + dispatch (1 warp-instruction/clk); 16,384 × 32-bit registers (64 KB); 32 FP32, 16 INT32 and 16 FP64 lanes; 1 Tensor Core; LD/ST; SFU. Below the quadrants, draw a shared 256 KB L1/shared block (up to 228 KB shared) with the TMA unit beside it. Per-SM limits: 64 warps, 2,048 threads, 32 blocks, 65,536 registers, at most 255 registers per thread. Tag: `vendor` (whitepaper / CUDA Guide compute-capability 9.0 table). **Verify.**
2. **Where 989 TF comes from.** Each H100 SM does 2,048 dense BF16 FMAs per clock: 4 Tensor Cores × 512. That is 4,096 FLOP/clk/SM, 2× A100's 1,024 FMA/clk/SM (**verify** in the whitepaper's per-SM table). Show the check:
   `989 TF ÷ (132 SM × 2,048 FMA × 2 FLOP) ≈ 1.83 GHz` (derived). This is consistent with the Tensor Core figure being quoted at a lower sustained clock than the FP32 figure.
   For comparison, the FP32 lanes give 132 × 128 × 2 × ~1.98 GHz ≈ 67 TF (vendor). Tensor Cores therefore supply about 15× the FP32-lane rate. FP8 doubles the per-clock rate again (1,979 TF dense). Teach the sentence "the FLOPs live in the Tensor Cores; everything else in the SM exists to keep them fed."
3. **What a Tensor Core instruction is.** Two generations:
   - Ampere `mma.sync.m16n8k16`: one warp, operands in registers, synchronous.
   - Hopper `wgmma.mma_async.m64nNk16`: one *warpgroup* (4 warps, 128 threads), N from 8 to 256, A from registers or shared memory, B from shared memory via a matrix descriptor, FP32 accumulator in registers, asynchronous (`wgmma.fence` / `commit_group` / `wait_group`).
   A small animation could show one m64n256k16 step: 64×16 times 16×256 accumulating into a 64×256 FP32 tile held in the registers of 128 threads (128 floats per thread). PTX ISA, **verify** shapes.
4. **Bridge sentence.** "One H100 SM (2,048 BF16 FMA/clk) does the per-clock work of N Cerebras PEs." Compute N as 2,048 divided by Chapter 3's per-PE FP16 FMAs per cycle, labelled derived. This makes the "few fat cores vs many thin cores" contrast quantitative.

### D2 [critical] Shared-memory tiling of a matmul: how a GPU climbs above the HBM roofline
**What is missing.** The chapter's only kernel is SAXPY. SAXPY does 2 FLOP per 12 bytes and is HBM-bound on every architecture, so it shows nothing about how GPUs reach their peak. The chapter never covers:
- tiling;
- data reuse in shared memory and registers;
- the intensity of a tile;
- multi-stage buffering.

**Why it matters.** Chapter 1 teaches that decode sits at about 1 FLOP/B, below H100's ridge of about 295. The natural question is how GEMM ever reaches the flat part of the roofline. The answer is the tile hierarchy: HBM → L2 → shared memory → registers → Tensor Core. Each level multiplies reuse. This hierarchy is the GPU counterpart of the 2D-decomposed GEMM on the wafer (Cannon/SUMMA-style across PEs) and of Tenstorrent's reader/compute/writer tiles. A comparison chapter cannot be complete without it.

**Source.**
- CUDA C++ Programming Guide, "Shared Memory" matrix-multiply example (docs.nvidia.com; blocked here, **verify**).
- CUTLASS docs, "Efficient GEMM in CUDA" (github.com/NVIDIA/cutlass/blob/main/media/docs/efficient_gemm.md).
- Colfax, [CUTLASS tutorial: design of a GEMM kernel](https://research.colfax-intl.com/cutlass-tutorial-design-of-a-gemm-kernel/).

**Proposed addition.** Add a new section, "Tiling a matmul", after SIMT.
1. **Figure.** C (M×N) split into block tiles BM×BN, one per thread block / SM. The K loop marches BK-wide slabs of A (BM×BK) and B (BK×BN) into shared memory. Each warp/warpgroup owns a sub-tile of C in registers.
2. **Intensity of one tile step (derived).**
   - FLOP = 2·BM·BN·BK.
   - Bytes from global memory = (BM + BN)·BK·2 (BF16).
   - Intensity = BM·BN / (BM + BN).
   - BM = BN = 128 → 64 FLOP/B. 128×256 → 85 FLOP/B. 256×256 → 128 FLOP/B.
   - Point out that all of these are *below* 295. GEMM still reaches peak because neighbouring blocks re-read the same A/B slabs from the 50 MB L2, not from HBM. The whole-matrix minimum traffic for M = N = K = 8192 is 3 × 8192² × 2 B = 403 MB against 1.1 TFLOP, about 2,700 FLOP/B. That is far above the ridge.
   - Add a slider widget: choose BM, BN, BK and stages. Show smem bytes, register bytes per thread, and intensity. Flag configurations that exceed 227 KB smem per block or 255 registers per thread.
3. **Budget example (derived).** BM = 128, BN = 256, BK = 64, BF16:
   - A slab 16 KB + B slab 32 KB = 48 KB per stage;
   - 4 stages = 192 KB, which fits in 227 KB;
   - FP32 accumulator 128×256 = 128 KB of registers, i.e. 128 registers per thread across 256 consumer threads.
   This shows why registers, shared memory and Tensor Cores are sized together.
4. **Contrast box.** On the wafer, A/B tiles never pass through a shared cache. They are pre-placed in PE SRAM and moved by wavelets (Chapter 12's stencil pattern). The GPU re-fetches from L2/HBM, and the wafer forwards neighbour to neighbour. Tie this to the "brings data to compute vs places compute next to data" line in notes §4.

### D3 [major] Warp scheduling at the level of one scheduler, and what limits occupancy
**What is missing.**
- The widget and the text talk about "the SM's scheduler". There are four, each owning up to 16 warps. Accuracy A3 and pedagogy P4 flag the resulting 21-warp quiz answer as impossible.
- Warp states (stalled, eligible, selected) and stall reasons (long scoreboard = waiting on global memory, barrier, MIO throttle, math pipe throttle) are absent.
- Occupancy limiters (registers per thread, smem per block, blocks per SM) are not quantified.
- The chapter never covers instruction-level parallelism and memory-level parallelism (Little's law). This is the real reason one warp per scheduler is not enough, and why modern kernels hide latency with *bytes in flight* rather than *warps*.

**Why it matters.** "Occupancy hides latency" is half true. Little's law gives the full statement. HBM bandwidth × latency = bytes that must be in flight. That amount can be reached with fewer warps if each issues more independent loads, via vector loads, unrolling or TMA bulk copies. This is also the cleanest contrast with the wafer: a PE's memory is one cycle away, but the fabric still needs wavelets in flight.

**Source.**
- CUDA C++ Programming Guide, compute-capability table for 9.0 (**verify**: 64 warps, 32 blocks, 64K registers per SM).
- [NVIDIA webinar: Warps and Occupancy](https://developer.download.nvidia.com/CUDA/training/cuda_webinars_WarpsAndOccupancy.pdf).
- Nsight Compute Kernel Profiling Guide, "Warp State Statistics" (docs.nvidia.com/nsight-compute; **verify** stall names).
- Volkov, "Better performance at lower occupancy" (GTC 2010).
- HBM latency: [Chips and Cheese H100](https://chipsandcheese.com/p/nvidias-h100-funny-l2-and-tons-of-bandwidth) (fetch blocked, **verify** the measured latency).

**Proposed addition.**
1. Change the widget model to per-SMSP: cap warps at 16 and label the plot "one scheduler (of 4 per SM)". Add a stall-reason legend. Fixing the quiz is the job of the accuracy and pedagogy fixes; here, add an ILP slider (independent loads per warp before the first use) so that W·ILP replaces W in the model.
2. **Little's law box (derived).** Assume HBM latency of about 600 ns (illustrative; replace with the measured value).
   - Bytes in flight = 3.35 TB/s × 600 ns ≈ 2 MB chip-wide ≈ 15 KB per SM.
   - One coalesced 4-byte warp load moves 128 B, so this needs ~120 outstanding warp loads per SM. That is more than the 64 resident warps.
   - With 16-byte vector loads (512 B per warp instruction) it needs ~30.
   - Conclusion: occupancy alone cannot saturate HBM; ILP, vector loads or TMA must do the rest.
3. **Occupancy calculator table (derived).** Registers per thread 32 → 64 warps (100%); 64 → 32 warps (50%); 128 → 16 (25%); 255 → 8. Shared memory per block 100 KB → at most 2 blocks per SM. This overlaps pedagogy P5; one implementation should satisfy both.
4. **Coalescing in numbers.** L1/L2 transfer in 32-byte sectors within 128-byte lines. A warp reading 32 consecutive floats touches 4 sectors (100% efficiency). Stride 2 touches 8 (50%). A random gather touches up to 32 (12.5%). This gives the existing quiz answer its support (pedagogy P6). **Verify** sector size in the CUDA Best Practices Guide.

### D4 [major] Hopper TMA, thread-block clusters and warp specialisation (with a Blackwell note)
**What is missing.** The chapter never mentions any of:
- TMA;
- mbarrier transaction counts;
- clusters and distributed shared memory (DSMEM);
- TMA multicast;
- producer/consumer warpgroups;
- `setmaxnreg`;
- Blackwell's Tensor Memory (TMEM) and `tcgen05`.

These features define how a modern GPU kernel is written. They are also the closest GPU analogue to Cerebras's asynchronous DSD operations and microthreads, and to Tenstorrent's reader/compute/writer split.

**Why it matters.** The chapter's "SIMT: one program, many threads" model describes 2012-era CUDA. A state-of-the-art Hopper GEMM or FlashAttention-3 kernel is explicitly spatial within an SM. One warp moves data and the others compute, synchronised through barriers on a ring of buffers. This narrows the conceptual gap with dataflow machines. A comparison course that hides it overstates how different CUDA is from CSL.

**Source.**
- Hopper whitepaper (TMA, clusters, DSMEM, async transaction barrier).
- CUDA Hopper Tuning Guide (TMA "1D–5D tensors between global and shared memory"; DSMEM; search extract confirmed).
- [PyTorch blog: CUTLASS Ping-Pong GEMM](https://pytorch.org/blog/cutlass-ping-pong-gemm-kernel/) (producer 40 regs / consumers 232 regs; kernel `sm90_gemm_tma_warpspecialized_pingpong`).
- [Colfax CUTLASS tutorials](https://research.colfax-intl.com/cutlass-tutorial/).
- FlashAttention-3 paper (Shah et al. 2024, arXiv 2407.08608). Its headline is about 740 TFLOPS FP16, ~75% of H100 peak; **verify**.
- Blackwell: [Colfax TMEM tutorial](https://research.colfax-intl.com/cutlass-tutorial-writing-gemm-kernels-using-tensor-memory-for-nvidia-blackwell-gpus/) (256 KB per SM, 512 columns × 128 lanes of 32-bit), [Modular Blackwell matmul part 3](https://modular.com/blog/matrix-multiplication-on-nvidias-blackwell-part-3-the-optimizations-behind-85-of-sota-performance) (`tcgen05.mma.cta_group::2`, a CTA pair shares one MMA), [arXiv 2512.02189 microbenchmarks](https://arxiv.org/pdf/2512.02189). PTX ISA for semantics.

**Proposed addition.** Add a section "Hopper: a GPU kernel becomes a pipeline".
1. **TMA.** A single thread issues `cp.async.bulk.tensor` with a tensor map created on the host (`cuTensorMapEncodeTiled`, up to 5D, with swizzle). The TMA engine generates the addresses and writes the tile into shared memory. Completion arrives on an mbarrier that was told how many bytes to expect (`expect_tx`). No registers are spent on address arithmetic. Multicast writes the same tile into the shared memory of several SMs in a cluster: up to 8 blocks portable, 16 non-portable on H100 (**verify**).
2. **Warp-specialised GEMM, animated (core visual).** Show one producer warpgroup and two consumer warpgroups, plus a ring of S shared-memory stages, each with a `full` and an `empty` barrier.
   - The producer waits on `empty[s]`, issues TMA into stage s, and TMA arrives on `full[s]`.
   - A consumer waits on `full[s]`, issues `wgmma`, and when it retires, arrives on `empty[s]`.
   - Register rebalancing: `setmaxnreg` drops the producer to 40 registers and raises consumers to 232.
   - Toggle between Ping-Pong (consumers alternate whole tiles, so one does its epilogue while the other runs MMA) and Cooperative (both consumers split one tile).
   This is a direct visual rhyme with Tenstorrent's circular buffers (Chapter 13) and with CSL's async DSD + task activation (Chapters 5–6). Say so explicitly. It is an analogy, labelled as the course's own.
3. **Blackwell note (two paragraphs).** The accumulator moves out of registers into a 256 KB-per-SM Tensor Memory (TMEM). A *single thread* issues `tcgen05.mma`. A CTA pair on two SMs can execute one MMA with M = 256 (`cta_group::2`). Consumer Blackwell (compute capability 12.x) lacks TMEM. Trend line: each generation moves more of the kernel into asynchronous, explicitly scheduled hardware engines. Tag `vendor` / `indep` per source; **verify** against the PTX ISA.

### D5 [major] How one LLM decode step runs on a GPU: kernels, KV cache, batching, numbers
**What is missing.** The chapter never walks through a token being generated. It does not cover:
- the per-layer kernel sequence;
- KV cache size and layout;
- why attention does not benefit from batching while the GEMMs do;
- continuous batching and PagedAttention;
- CUDA graphs and launch overhead;
- how tensor parallelism spreads one token across GPUs.

Chapter 1 has the roofline and Chapter 8 has Cerebras weight pinning, but nobody shows the GPU side mechanically.

**Why it matters.** Decode speed is the course's headline independent evidence for Cerebras (981 tok/s, 6.7×; Chapter 15). The learner needs to see, in kernels and bytes, why a GPU is slower per user and faster per dollar at batch. This is the single most important bridge between Chapters 1, 8, 14 and 15.

**Source.**
- Llama 3 model card / config (80 layers, d_model 8192, 64 query heads, 8 KV heads (GQA), head dim 128, FFN 28,672, vocab 128,256). **Verify** against the HF `config.json` for Llama-3.1-70B.
- vLLM paper (Kwon et al., SOSP 2023, "Efficient Memory Management for LLM Serving with PagedAttention").
- vLLM docs on CUDA graphs (capture per batch size, pad to the nearest size; search extract).
- Flash-Decoding (Dao et al., Oct 2023, Together/Stanford blog, split-KV).
- Orca (Yu et al., OSDI 2022) for iteration-level ("continuous") batching.
- Megatron-LM (Shoeybi et al. 2019) for the two all-reduces per layer.

**Proposed addition.** Add a section "One token, step by step" with a figure and a calculator widget.
1. **Kernel strip for one layer** (drawn as a timeline of boxes): RMSNorm → fused QKV GEMM → RoPE + KV-cache append → paged decode attention (split-KV across thread blocks, then reduce) → O-proj GEMM → [TP all-reduce] → residual + RMSNorm → gate/up GEMM → SiLU·mul → down GEMM → [TP all-reduce] → residual. That is about 10–14 kernels per layer, about 1,000 per token for 80 layers. Launch overhead (a few µs each) would cost milliseconds, hence CUDA graphs and fusion.
2. **Bytes per token (derived; Llama-3.1-70B, BF16).**
   - Weights: ~141 GB.
   - KV cache per token: 2 × 80 × 8 × 128 × 2 B = 327,680 B ≈ 320 KB.
   - Batch 1, TP = 8 on HGX H100: 17.6 GB per GPU ÷ 3.35 TB/s ≈ 5.3 ms, i.e. an upper bound of ~190 tok/s per user before attention, all-reduce and launch overhead. Compare with Cerebras's figures in Chapter 15.
   - Batch 64 at 4k context: KV = 64 × 4096 × 320 KB ≈ 86 GB to read per step, on top of 141 GB of weights. Weight bytes are shared across the batch, so GEMM intensity grows about ×B. Every sequence reads only its own KV, so attention stays near 1 FLOP/B regardless of batch. This explains why long-context, high-batch serving becomes KV-bandwidth-bound and why GQA, FP8 KV and MLA exist.
3. **Calculator widget.** Inputs: model (70B / 8B / 405B), precision (BF16 / FP8 / FP4), TP degree, batch, context, GPU (H100 / B200 / Rubin from the generation table). Outputs: per-GPU bytes per step, step time from HBM bandwidth, tok/s per user, aggregate tok/s, whether the weights + KV fit in HBM. Use the same model numbers as Chapter 8's Cerebras capacity widget so the two can be compared directly.
4. **Serving machinery.**
   - Continuous batching: the scheduler re-forms the batch every step, so requests join and leave.
   - PagedAttention: the KV cache sits in fixed-size blocks (16 tokens by default in vLLM; **verify**) addressed through a block table, like OS pages, which removes fragmentation.
   - Prefill and decode are batched together (chunked prefill) or split onto separate GPUs (disaggregation).
   - Speculative decoding briefly mentioned.
   - One sentence per item, each with a source.

### D6 [major] NVLink/NVSwitch topology and tensor/pipeline/data parallelism, with numbers
**What is missing.** Scale-out is one paragraph with no topology and no link counts. It also lacks:
- the NVLink-to-InfiniBand bandwidth ratio;
- the all-reduce cost model;
- a statement of which parallelism maps onto which fabric;
- the pipeline bubble.

**Why it matters.** The NVLink domain is NVIDIA's answer to "the model doesn't fit". It is the direct counterpart of Cerebras's multi-wafer inference and MemoryX/SwarmX (Chapter 8) and of Tenstorrent's Ethernet mesh (Chapter 13). Without numbers, Chapter 15's comparison of scale-up domains cannot be quantified.

**Source.**
- Hopper whitepaper / HGX H100 blog: 18 NVLink4 links × 50 GB/s/dir = 900 GB/s bidirectional per GPU; HGX H100 with 4 NVSwitch3 chips; 3.6 TB/s bisection ([NVIDIA HGX H100 blog](https://developer.nvidia.com/blog/introducing-nvidia-hgx-h100-an-accelerated-server-platform-for-ai-and-high-performance-computing), search extract; [Glenn Lockwood NVLink notes](https://glennklockwood.com/garden/NVLink)).
- NVSwitch3: 64 NVLink4 ports (Hot Chips 34).
- GB200 NVL72: 18 NVLink5 links × 100 GB/s bidirectional = 1.8 TB/s per GPU; 9 switch trays × 2 NVSwitch chips = 18 chips with 72 ports each, so every GPU has one link to every switch chip (single hop, all-to-all); 72 × 1.8 ≈ 130 TB/s ([SemiAnalysis GB200 hardware architecture](https://newsletter.semianalysis.com/p/gb200-hardware-architecture-and-component), [naddod GB200 interconnect](https://naddod.com/blog/nvidia-gb200-interconnect-architecture-analysis-nvlink-infiniband-and-future-trends); **verify** against NVIDIA's NVL72 page).
- Megatron-LM: Shoeybi et al. 2019 (two all-reduces per layer forward); Narayanan et al., [SC21, arXiv 2104.04473](https://arxiv.org/pdf/2104.04473) (TP within node, PP across nodes; bubble (p−1)/m relative to ideal compute; 502 PFLOP/s on 3,072 A100s, 52% of peak, **verify**).

**Proposed addition.** Replace the "Scaling out" section with three parts.
1. **Two topology diagrams side by side.**
   - HGX H100: 8 GPUs, 4 NVSwitch chips, each GPU's 18 links split across the switches (5/4/4/5, **verify**), 900 GB/s per GPU, plus one 400 Gb/s (50 GB/s) NIC per GPU to the InfiniBand fabric.
   - NVL72: 72 GPUs, 18 switch chips, one link from every GPU to every chip.
   - Annotate the ratio: NVLink 900 GB/s vs IB 50 GB/s per GPU, about 18× (derived). This ratio is the reason for the rule "tensor parallel inside NVLink, pipeline/data parallel across IB".
2. **Parallelism table with a cost model.** Columns: what is split, what is communicated, how often, which fabric.
   - **TP:** weight matrices split by column/row; 2 all-reduces per layer forward (4 with backward); size = batch × seq × d_model × bytes.
   - **PP:** layers split; only boundary activations are sent; bubble = (p−1)/m.
   - **DP / FSDP:** a full gradient all-reduce or reduce-scatter once per step.
   - **EP (MoE):** all-to-all of tokens.
   - Ring all-reduce time ≈ 2(N−1)/N × S / BW.
3. **Worked example (derived; TP = 8 on H100, 70B training, microbatch 1 × 4096 tokens).**
   - S = 4096 × 8192 × 2 B = 64 MB per all-reduce.
   - Each all-reduce takes ≈ 2 × 7/8 × 64 MB ÷ 450 GB/s ≈ 0.25 ms.
   - Per microbatch: 80 layers × 4 all-reduces ≈ 80 ms.
   - Compute: 6 × 70e9 × 4096 ≈ 1.7 PFLOP ÷ (8 × 989 TF × 50% MFU) ≈ 0.43 s. Communication is about 19% of compute over NVLink.
   - The same all-reduces over 50 GB/s IB would take ~0.7 s, more than the compute. That is why TP never crosses the NVLink domain.
   - Decode variant: at batch 1 the all-reduce is only 16 KB, but there are 160 per token, so they are latency-bound (a few µs each, **verify** with NCCL numbers) and can cost a meaningful fraction of the 5.3 ms step from D5.
   - Make the numbers sliders: TP degree, link bandwidth, microbatch.

### D7 [minor] Memory hierarchy figure lacks bandwidths and latencies per level, and omits L1 sectors, the L2 partition split and DSMEM
**What is missing.** Only HBM and the measured L2 bandwidth carry numbers. Missing:
- register/shared-memory bandwidth per SM (derived: 128 B/clk/SM shared-memory bandwidth × 132 × ~1.8 GHz ≈ 30 TB/s; **verify** the 128 B/clk figure);
- latencies in cycles (register ~1, smem ~20–30, L2 ~200+, HBM ~500+; **verify** with Chips and Cheese or arXiv microbenchmark papers);
- the two-partition L2;
- DSMEM as a new level between smem and L2.

**Why it matters.** Notes §3 Inferences says the fair comparison for Cerebras's 21 PB/s is aggregate register + shared-memory bandwidth, not HBM. The chapter cannot make that point without numbers.

**Source.** Hopper whitepaper; Chips and Cheese H100 article; [arXiv 2512.02189](https://arxiv.org/pdf/2512.02189) (Blackwell microbenchmarks, latency tables).

**Proposed addition.** Add a bandwidth column and a latency column to the hierarchy figure. Add a callout that computes aggregate on-chip bandwidth (derived) and puts it next to the WSE-3's 21 PB/s and Blackhole's per-core SRAM bandwidth, with honest caveats.

### D8 [minor] Low-precision formats behind the generation table (FP8, NVFP4, microscaling) are unexplained
**What is missing.** The table jumps from BF16 to FP4 to NVFP4 without saying:
- what these formats are;
- that the Transformer Engine on Hopper chooses FP8 scaling per tensor;
- that NVFP4 uses block scaling (16-element blocks with an FP8 E4M3 scale plus a per-tensor FP32 scale; **verify** against NVIDIA's NVFP4 blog / PTX `mxf4nvf4`).

**Why it matters.** Most of the 50× growth in "FLOPs" from H100 to Rubin comes from format, not silicon (notes §1 Inferences: HBM grows only 5.7×). Without this, the learner misreads the table. Pedagogy P3 raises the same concern.

**Source.** Hopper whitepaper (Transformer Engine); NVIDIA technical blog "Introducing NVFP4" (developer.nvidia.com, **verify**); OCP Microscaling (MX) spec v1.0.

**Proposed addition.** Add a short box, "Why the FLOPs jump". It should contain:
- a table of bits per value per format;
- the Tensor Core rate per clock per SM for each format;
- an iso-precision comparison row (BF16 dense: 989 TF → B200 ≈ 2.25 PF (**verify**) → Rubin n/a).

### D9 [minor] SAXPY comparison stops before data distribution and the host side on the GPU
**What is missing.** It does not show what SAXPY costs on an H100. At 12 B/element and 2 FLOP (about 0.17 FLOP/B), it takes about n × 12 B ÷ 3.35 TB/s. It also skips:
- the kernel-launch latency (~µs);
- the `cudaMemcpy` over PCIe/NVLink-C2C;
- that the whole kernel is one wave of 132 × 2,048 threads.

**Why it matters.** It would close the loop with Chapter 1's roofline and with Lab 1's measured cycle counts, which come from the simulator.

**Source.** Derived from the chapter's own numbers; CUDA Programming Guide for launch semantics.

**Proposed addition.** Add a two-line "SAXPY on the roofline" note: point marked on the H100 roofline, time for n = 10⁸ ≈ 0.36 ms (derived). Contrast with the time per element on the wafer from Lab 1 (`measured`).

## Out of scope for this chapter (new-chapter or cross-chapter ideas)

1. **Cross-chapter "same kernel, three machines" table (Chapter 15).** Put warp-specialised TMA/wgmma pipelines (GPU), reader/compute/writer with circular buffers (Tenstorrent), and async DSD ops + task activation/microthreads (Cerebras) side by side. Columns: producer, consumer, buffer, synchronisation primitive, who decides placement. D4 gives the GPU row.
2. **New chapter: "One token on three architectures".** A sequel to Chapter 8 and D5. Trace a Llama-70B decode step on (a) HGX H100 with TP = 8, (b) four CS-3 wafers with weights pinned and layer-pipelined, (c) a Tenstorrent Galaxy mesh. Count bytes moved, hops, synchronisations and the predicted versus independently measured tok/s per user. One shared calculator widget.
3. **Chapter 1 roofline extension.** Add L2 and shared-memory ceilings (hierarchical roofline) and mark the D2 tile intensities. Chapter 1 then explains why GEMM tiles still reach peak.
4. **Chapter 8 cross-link.** Compare the NVL72 scale-up domain (~130–216 TB/s, ~13.4–20.7 TB HBM) against multi-CS-3 inference and MemoryX/SwarmX, side by side in one figure with matching axes (bandwidth per byte of capacity).
5. **New appendix: "Profiling and seeing inside".** Nsight Compute warp-state stalls and the memory chart on GPU, the Cerebras simulator's cycle traces and debug library, and Tenstorrent's Tracy/device profiler. This teaches the learner how to *observe* internal behaviour on each machine.
6. **New short chapter or appendix: number formats.** BF16 → FP8 → MXFP4/NVFP4 → Cerebras's FP16/CB16 and Tenstorrent's BlockFP8. One table and one quantisation-error widget. It would deduplicate precision caveats across Chapters 2, 13, 14 and 15.
7. **Mixture-of-experts and expert parallelism.** All-to-all over NVLink compared with routing on the wafer. This could be a future extension of Chapter 15, since current frontier models (Kimi K2.6 in Chapter 15's evidence) are MoE.
