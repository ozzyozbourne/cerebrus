# NVIDIA GPU Architecture and Cross-Architecture Comparison (GPU vs Cerebras WSE vs Tenstorrent)

> **Errata (2026-11-02).** Some figures below have been superseded by measurements in the course. See the "Errata / superseded by course measurements" table at the top of `reports/Cerebras architecture course research.md` and `course/reviews/CROSS_CHAPTER_NOTES.md`. Affected here: Rubin CPX is reported shelved (unconfirmed); NVIDIA now pairs Vera Rubin with the Groq 3 LPX SRAM decode rack (course Ch 17).

*Research date: 2026-11-01. Method note: in this session WebFetch was blocked for every host tried (resources.nvidia.com, developer.nvidia.com, tomshardware.com, cerebras.ai, arxiv.org, chipsandcheese.com). All findings below come from WebSearch result summaries and snippets. Figures should be checked against the primary documents linked before they go into course material. Labels: **[VENDOR]** = vendor-published or vendor-claimed; **[INDEP]** = independent measurement or third-party analysis; **[SECONDARY]** = aggregator/blog that repeats specs.*

## 1. GPU internals: H100, B200/GB200, Rubin (2026). SM structure, memory hierarchy, NVLink, key numbers

### Takeaway
A modern NVIDIA datacenter GPU is a large array of Streaming Multiprocessors (132 on H100 SXM5). Each SM has 256 KB of registers and 256 KB of L1/shared memory. They share a 50 MB L2 cache, which in turn is fed by HBM: 3.35 TB/s on H100, about 8 TB/s on B200, and 19.2 to 22 TB/s on Rubin depending on which spec revision you use. Each generation roughly doubles or triples HBM bandwidth and low-precision FLOPs, and NVLink grows from 900 GB/s to 1.8 TB/s and then 3 to 3.6 TB/s per GPU. The NVL72 rack, with 72 GPUs in one NVLink domain, is NVIDIA's unit of scale-up.

### Cited Findings
**H100 (Hopper, 2022) [VENDOR whitepaper, partly independently measured]**
- The H100 SXM5 has 132 SMs and the PCIe version has 114. — [NVIDIA H100 Tensor Core GPU Architecture whitepaper v1.02 (mirror)](https://www.hpctech.co.jp/assets/images/info/catalog/pdf/gtc22-whitepaper-hopper_v1.02.pdf); [Wikipedia: Hopper](https://en.wikipedia.org/wiki/Hopper_(microarchitecture))
- Each SM has 256 KB of combined L1 data cache and shared memory, and shared memory can be configured up to 228 KB per SM. — [Hopper whitepaper](https://www.hpctech.co.jp/assets/images/info/catalog/pdf/gtc22-whitepaper-hopper_v1.02.pdf); [NVIDIA Hopper Architecture In-Depth blog (PDF mirror)](https://lists.riscv.org/g/tech-attached-matrix-extension/attachment/25/0/NVIDIA%20Hopper%20Architecture%20In-Depth%20_%20NVIDIA%20Technical%20Blog.pdf)
- The register file is 256 KB per SM. This is separate from the L1/shared pool. — [Hopper whitepaper](https://www.hpctech.co.jp/assets/images/info/catalog/pdf/gtc22-whitepaper-hopper_v1.02.pdf)
- The L2 is 50 MB, and every SM can reach all of it, though not at the same speed (the L2 is split into two partitions). **[INDEP]** Chips and Cheese measured about 3.8 TB/s aggregate read bandwidth from the full 50 MB L2. — [Chips and Cheese: "Nvidia's H100: Funny L2, and Tons of Bandwidth"](https://chipsandcheese.com/p/nvidias-h100-funny-l2-and-tons-of-bandwidth)
- The SXM part has 80 GB of HBM3 at 3.35 TB/s. — [Hopper whitepaper](https://www.hpctech.co.jp/assets/images/info/catalog/pdf/gtc22-whitepaper-hopper_v1.02.pdf); [H100 course slides](https://cudacourseh100.github.io/H100-Course/slides/1.%20Introduction%20to%20H100.pdf)
- Dense BF16 on H100 SXM is about 989 TFLOPS. The commonly quoted 1,979 TFLOPS is the 2:4-sparsity figure. Using the dense figure, the BF16 ridge point is about 989 / 3.35 ≈ 295 FLOP/byte. — [Spheron: roofline model for LLM inference](https://www.spheron.network/blog/the-roofline-model-for-llm-inference-are-you-compute-bound-o/); [dev.to: prefill vs decode roofline](https://dev.to/ji_ai/why-llm-decoding-is-memory-bound-prefill-vs-decode-roofline-223f)
- Several secondary sources give on-chip bandwidth estimates of "~20 TB/s" or "~12 TB/s" for L1/shared or L2. These conflict with each other and with NVIDIA-derived numbers, so treat them as rough guides only. — [Modular handbook: GPU memory hierarchy](https://handbook.modular.com/kernel-optimization/gpu-architecture-fundamentals/gpu-memory/); [BentoML: GPU architecture fundamentals](https://bentoml.com/llm/kernel-optimization/gpu-architecture-fundamentals); [Spheron: memory hierarchy](https://www.spheron.network/blog/gpu-memory-hierarchy-diagram-registers-to-hbm-explained/)

**B200 / GB200 NVL72 (Blackwell, 2024–25) [VENDOR via SECONDARY]**
- The B200 is two reticle-limited dies joined by a 10 TB/s NV-HBI die-to-die link and packaged as one GPU. It has 208B transistors on TSMC 4NP. — [Spheron B200 guide](https://www.spheron.network/blog/nvidia-b200-complete-guide/); [Jarvislabs B200 specs](https://jarvislabs.ai/ai-faqs/nvidia-b200-specs)
- Memory is 192 GB of HBM3e at about 8 TB/s. Clouds commonly expose about 180 GB, and SemiAnalysis InferenceX lists 180–186 GB as usable. — [SemiAnalysis InferenceX: B200](https://inferencex.semianalysis.com/chips/b200); [Modal B200 pricing](https://modal.com/blog/nvidia-b200-pricing); [Spheron GB200](https://spheron.network/gpu-rental/gb200/)
- FP4 is about 9 PFLOPS dense and 18 PFLOPS sparse. Marketing figures of "20 PF FP4" appear to be sparse numbers, and some may refer to GB200 rather than HGX B200. — [Spheron B200](https://www.spheron.network/blog/nvidia-b200-complete-guide/); [RunPod B200](https://www.runpod.io/gpu-models/b200)
- The GB200 NVL72 rack has 72 Blackwell GPUs and 36 Grace CPUs. NVLink 5 provides 1.8 TB/s bidirectional per GPU, for about 130 TB/s across the rack. The rack holds about 13.4–13.5 TB of HBM3e with 576 TB/s aggregate HBM bandwidth, and delivers about 1,440 PF FP4 and 720 PF FP8 (sparse figures). — [nextpcb: GB200 NVL72 architecture](https://www.nextpcb.com/blog/nvidia-gb200-nvl72-architecture); [CudoCompute GB200 NVL72](https://www.cudocompute.com/products/nvidia-gb200-nvl72); [Spheron NVL72 guide](https://www.spheron.network/blog/nvidia-gb200-nvl72-guide/); [SemiAnalysis InferenceX GB200 NVL72](https://inferencex.semianalysis.com/chips/gb200-nvl72)

**Vera Rubin (2026) [VENDOR, revised; all sources secondary]**
- Each Rubin GPU package has two compute dies and 288 GB of HBM4 in 8 stacks. It is rated at 50 PF NVFP4 for inference and 35 PF NVFP4 for training. A rack is about 3.6 EF NVFP4 for inference. "NVL144" (original GTC 2025 naming, counting dies) and "NVL72" (counting packages) describe the same 72-package rack, which also has 36 Vera CPUs, about 20.7 TB of HBM4 and about 54 TB of LPDDR5X. — [The Register, CES 2026, 2026-01-05](https://www.theregister.com/2026/01/05/ces_rubin_nvidia/); [HotHardware roadmap](https://hothardware.com/news/nvidia-announce-vera-rubin-nvl576); [DCD](https://datacenterdynamics.com/en/news/nvidia-announces-vera-rubin-superchip-for-late-2026)
- **Spec revision (important, late 2026).** The launch and GTC 2026 figures were 22 TB/s HBM4 and 3.6 TB/s NVLink 6 per GPU, with about 260 TB/s NVLink per rack. Recent reporting says NVIDIA's own NVL72 page now lists **19.2 TB/s HBM4, 3 TB/s NVLink 6 per GPU and about 216 TB/s per rack**, with capacity unchanged. NVIDIA reportedly says the new specs "reflect what the system sustains at quality, volume production." An earlier target was 13 TB/s before NVIDIA raised it to 22. — [pasqualepillitteri.it: NVIDIA site confirms Vera Rubin spec cut](https://pasqualepillitteri.it/en/news/27546/nvidia-site-confirms-vera-rubin-spec-cut-hbm4-nvlink-6); [Wccftech: NVIDIA official statement on Vera Rubin spec change](https://wccftech.com/nvidia-official-statement-on-vera-rubin-spec-change/); [Hashrate Index NVL72 breakdown](https://hashrateindex.com/blog/nvidia-vera-rubin-nvl72-specs-breakdown/)
- Rubin CPX is an inference/prefill accelerator with about 30 PF NVFP4 and GDDR7 instead of HBM. The NVL144 CPX rack is about 8 EF NVFP4. — [hyper.ai summary](https://hyper.ai/en/stories/3422d6a72152beb34a564461208438ff); [Tom's Hardware Vera Rubin in depth](https://tomshardware.com/pc-components/gpus/nvidias-vera-rubin-platform-in-depth-inside-nvidias-most-complex-ai-and-hpc-platform-to-date) (not fetched)
- One secondary source cites about 336B transistors for Rubin. — [tech-insider.org](https://tech-insider.org/nvidia-gtc-2026-rubin-gpu-analysis/) (unverified)

**Summary table (dated, mostly vendor numbers)**

| | H100 SXM (2022) | B200 (2024–25) | Rubin (2026, current spec) |
|---|---|---|---|
| HBM | 80 GB HBM3, 3.35 TB/s | 192 GB HBM3e, ~8 TB/s | 288 GB HBM4, 19.2 TB/s (was 22) |
| Low-precision peak | ~989 TF BF16 dense; ~1,979 TF FP8 dense | ~9 PF FP4 dense | 50 PF NVFP4 (inference) |
| NVLink per GPU | 900 GB/s (NVLink 4; not re-verified) | 1.8 TB/s (NVLink 5) | 3 TB/s (NVLink 6; was 3.6) |
| Rack NVLink domain | 8-GPU HGX | NVL72, ~130 TB/s | NVL72, ~216 TB/s (was 260) |

### Inferences
- From H100 to Rubin, HBM bandwidth grows about 5.7x (3.35 to 19.2 TB/s), while low-precision FLOPs grow far more because the format also changes (BF16 to NVFP4). FLOPs per byte keeps rising, so the memory wall gets worse with each generation. This is a key teaching point for comparing against SRAM-centric designs.
- The Rubin spec revision is a good case study for "vendor numbers are targets." Course tables should give the date and source page for each Rubin number.

### Gaps
- I could not re-verify from primary sources the per-SM breakdowns I know from the Hopper whitepaper: 4 SM sub-partitions, each with 1 warp scheduler, 32 FP32 lanes and 1 4th-gen Tensor Core, giving 128 FP32 cores and 4 Tensor Cores per SM; up to 64 warps (2,048 threads) per SM; NVLink 4 at 900 GB/s; FP64 at about 67 TF; and the Hopper features TMA, thread-block clusters and distributed shared memory. Check these in the whitepaper linked above before use.
- Blackwell SM details (Tensor Memory/TMEM of 256 KB per SM, tcgen05 instructions, 5th-gen Tensor Cores, SM count of 148) did not come up in search results and remain unverified. Check the Blackwell whitepaper and PTX ISA docs on docs.nvidia.com.
- I found no primary NVIDIA source for Rubin SM count or per-SM structure.

## 2. The SIMT programming model: grids/blocks/warps, coalescing, occupancy, latency hiding

### Takeaway
A CUDA kernel runs as a grid of thread blocks. Each block runs on one SM and shares its shared memory, and its threads execute in warps of 32 in lockstep (SIMT). Performance depends on coalescing global loads, so that consecutive threads read consecutive addresses, and on keeping enough warps resident (occupancy) so the scheduler can hide the latency of HBM accesses.

### Cited Findings
- A warp is 32 threads executing one instruction together. When threads in a warp branch differently, the paths run one after another with inactive threads masked. A fully divergent warp runs at 1/32 of peak. — [Intro to CUDA: Understanding Warps](https://intro-to-cuda.readthedocs.io/en/latest/tutorial/warps.html); [TheoremPath: CUDA fundamentals](https://theorempath.com/topics/cuda-programming-fundamentals)
- Block sizes should be multiples of 32 (32, 64, …, 512). — [Sergiu Nistor: CUDA Made Simple](https://sergiunistor.substack.com/p/cuda-made-simple-a-short-practical)
- Accesses are coalesced when consecutive threads hit consecutive addresses ("thread i accesses element i"). Strided access is not coalesced. 2D arrays should be padded so the width is a multiple of 32. — [ZeroEntropy: CUDA programming](https://www.zeroentropy.dev/concepts/cuda-programming/); [EPITA GPGPU slides](https://www.lrde.epita.fr/~carlinet/cours/GPGPU/j1-part4-gpu_programming_model.slides.pdf)
- Occupancy = active warps ÷ maximum active warps per SM. It is limited by registers per thread, shared memory per block and block size. When occupancy is too low and one warp stalls on a load, no other warp is ready and the SM sits idle. — [NVIDIA CUDA webinar: Warps and Occupancy](https://developer.download.nvidia.com/CUDA/training/cuda_webinars_WarpsAndOccupancy.pdf); [DigitalOcean: CUDA performance tuning](https://www.digitalocean.com/community/tutorials/cuda-performance-tuning-workflow)

### Inferences
- CUDA is a *bulk-synchronous, time-multiplexed* model. The programmer tiles data from HBM into shared memory and registers, computes, and writes back, and relies on oversubscription (many warps) to hide latency. This is the opposite of the *spatial* approach used by Cerebras and Tenstorrent, where data is placed near compute ahead of time and streamed between cores (see §4).

### Gaps
- Thread-block clusters and distributed shared memory (Hopper+), TMA, and warpgroup MMA (wgmma) and tcgen05 did not come up in search results. Cite the CUDA C++ Programming Guide (docs.nvidia.com/cuda/cuda-c-programming-guide/) directly; I did not verify it this session.

## 3. The memory wall: SRAM vs HBM, arithmetic intensity, roofline, why decode is bandwidth-bound, and how each architecture responds

### Takeaway
At batch 1, LLM decode does about 1 FLOP per byte of weights read. That is far below the H100's ridge point of about 295 FLOP/byte (BF16 dense), so decode speed is set by memory bandwidth, not by FLOPs. GPUs respond by batching and adding more HBM bandwidth with each generation. Cerebras keeps weights in 44 GB of on-wafer SRAM (vendor figure: 21 PB/s, about 2,600x an H100's HBM bandwidth). Tenstorrent takes a middle path: about 1.5 MB of SRAM per core (180 MB per Blackhole chip), modest GDDR6 (512 GB/s), and Ethernet to spread a model across chips.

### Cited Findings
- **Roofline:** the ridge point = peak FLOP/s ÷ memory bandwidth. For H100 SXM BF16 dense this is about 989 TFLOPS ÷ 3.35 TB/s ≈ 295 FLOP/byte. One Spheron post gives about 591, but it uses the sparse 1,979 TF figure. — [Spheron: roofline model for LLM inference](https://www.spheron.network/blog/the-roofline-model-for-llm-inference-are-you-compute-bound-o/); [mlsysbook: Hello Roofline](https://mlsysbook.ai/mlsysim/tutorials/00_hello_roofline.html)
- **Decode** at batch 1 has about 1 FLOP/byte, so it is memory-bound. For a linear layer, intensity is roughly M, the number of concurrent sequences. Batch 32 is still below the ridge but about 30x more throughput per weight read. Batch 64 on a 70B model reaches about 50–100 FLOP/byte, still under the ridge. **Prefill** has intensity roughly equal to the token batch and can reach thousands of FLOP/byte, so it is compute-bound. — [dev.to: why LLM decoding is memory-bound](https://dev.to/ji_ai/why-llm-decoding-is-memory-bound-prefill-vs-decode-roofline-223f); [Zartis: bytes-per-token problem](https://www.zartis.com/you-dont-have-a-compute-problem-you-have-a-bytes-per-token-problem/); [ZeroEntropy: arithmetic intensity](https://www.zeroentropy.dev/concepts/arithmetic-intensity/)
- A 2026 arXiv survey covers accelerator design for LLMs specifically through the memory-wall lens. Its title and abstract appeared in search results, but I did not read the content. — [AI Hardware Accelerators for LLMs: Architectures and the Memory Wall (arXiv 2608.28048)](https://arxiv.org/pdf/2608.28048)
- **Cerebras WSE-3 [VENDOR]:** 900,000 AI cores, 44 GB on-chip SRAM, 21 PB/s memory bandwidth, 46,225 mm² on TSMC 5 nm, and 125 PF peak. The 125 PF is an FP16 figure *with sparsity*. — [Cerebras Hot Chips 2024 deck](https://hc2024.hotchips.org/assets/program/conference/day2/72_HC2024.Cerebras.Sean.v03.final.pdf); [mirrorfrog WSE-3 card](https://mirrorfrog.com/en/docs/cards/cerebras/wse-3/); [insidedeeptech](https://www.insidedeeptech.com/cerebras-wafer-scale-engine-wse-cs3-full-guide/)
- **Cerebras per-PE:** each PE has 48 KB of SRAM in 8 banks of 6 KB, and code and data share it. — [Cerebras SDK docs (llms-full.txt)](https://sdk.cerebras.ai/llms-full.txt); [Cerebras SDK Technical Overview white paper](https://8968533.fs1.hubspotusercontent-na2.net/hubfs/8968533/Cerebras%20SDK%20Technical%20Overview%20White%20Paper.pdf)
- **Tenstorrent Blackhole p150 [VENDOR]:** 120 Tensix cores (cut from 140 by firmware v19.5.0, with a vendor-stated 1–2% performance impact), 180 MB SRAM (about 1.5 MB per core; reportedly down from 210 MB), 32 GB GDDR6 at 512 GB/s, 664 TFLOPS BlockFP8 (down from 774), 4x QSFP-DD 800G Ethernet, 16 "big" RISC-V cores, PCIe 5.0 x16, 300 W. — [Tom's Hardware: Blackhole downgrade](https://www.tomshardware.com/tech-industry/semiconductors/jim-kellers-tenstorrent-is-downgrading-blackhole-p150-cards-from-140-to-120-tensor-cores-via-firmware-update-will-ship-cards-with-120-tensor-cores-going-forward-company-claims-existing-users-should-expect-1-2-percent-performance-drop); [VideoCardz](https://videocardz.com/newz/tenstorrent-downgrades-blackhole-p150-pcie-cards-specs-from-140-to-120-cores); [gpusmith p150 datasheet](https://gpusmith.com/datasheets/tenstorrent-blackhole-p150-datasheet.pdf); [Spheron: Tenstorrent vs NVIDIA 2026](https://www.spheron.network/blog/tenstorrent-vs-nvidia-open-source-ai-hardware/)
- **Capacity critique of SRAM-only designs:** a 70B model at FP16 is about 140 GB of weights, more than three times the 44 GB on one WSE-3. Serving it requires several CS-3 systems, or lower precision (about 70 GB at FP8 is still more than one wafer). — [Spheron: Cerebras vs H100 2026](https://www.spheron.network/blog/cerebras-vs-nvidia-h100-inference-2026/); [Medium: Why Cerebras raised at $56.4B](https://machine-learning-made-simple.medium.com/why-cerebras-raised-at-56-4-billion-usd-to-attack-nvidias-memory-bottleneck-c11bfe81f417); [damnang: WSE-3 physical ceiling](https://www.damnang.com/p/cerebras-wse-3-the-technical-achievement)

**Memory-wall comparison table (vendor figures, dated)**

| | On-chip SRAM | Off-chip memory | Off-chip BW | Notes |
|---|---|---|---|---|
| H100 SXM (2022) | 50 MB L2 + 132 × 256 KB L1/smem (~33 MB) + 132 × 256 KB RF (~33 MB) | 80 GB HBM3 | 3.35 TB/s | L1 and RF totals computed from per-SM figures |
| B200 (2024) | (L2 not verified) | 192 GB HBM3e | ~8 TB/s | |
| Rubin (2026) | n/a | 288 GB HBM4 | 19.2 TB/s (rev.) | |
| Cerebras WSE-3 (2024) | 44 GB SRAM, 21 PB/s | MemoryX (external, for weight streaming) | n/a | 48 KB per PE |
| TT Blackhole p150 (2025) | 180 MB (~1.5 MB/core) | 32 GB GDDR6 | 512 GB/s | 4×800G Ethernet |

### Inferences
- Cerebras's quoted 21 PB/s is *aggregate local SRAM bandwidth* spread across 900k PEs. It is not a shared memory any core can reach at that rate. Comparing it to GPU HBM bandwidth is fair for weights that stay resident, but the fairer GPU comparison is aggregate register-file plus shared-memory bandwidth, which is also in the tens to hundreds of TB/s. The course should state that explicitly.
- The three designs place the "bandwidth vs capacity" knob in different spots. A GPU has large capacity (80–288 GB per device) and medium bandwidth. Cerebras has small capacity (44 GB per wafer) and huge bandwidth. Tenstorrent has small SRAM plus cheap GDDR, and leans on scale-out over Ethernet.

### Gaps
- I found no independent measurement of WSE-3 sustained SRAM or fabric bandwidth. All Cerebras bandwidth numbers are vendor figures.
- B200 L2 size was not verified.

## 4. Programming model comparison: CUDA vs Cerebras CSL vs Tenstorrent TT-Metalium

### Takeaway
CUDA is SIMT with bulk-synchronous kernels over a shared memory hierarchy. CSL is spatial dataflow: each PE runs its own program, and tasks fire when 32-bit "wavelets" arrive on statically routed "colors," with 48 KB of local memory per PE. TT-Metalium sits in between. Each Tensix core runs three cooperating kernels (reader, compute, writer) that pass tiles through circular buffers and move data over two NoCs.

### Cited Findings
**Cerebras CSL [VENDOR docs + academic]**
- Device code is written in CSL, a Zig-like DSL, and host code in Python. Tasks run to completion, after which the hardware picks the next activated task. Tasks cannot call each other, only activate one another. *Local tasks* are activated by the program, while *data tasks* fire automatically when a wavelet arrives. Each PE supports up to 28 task IDs. — [Cerebras SDK docs](https://sdk.cerebras.ai/llms-full.txt); [wafer.ai substack: breaking down the WSE](https://wafer.substack.com/p/breaking-down-the-cerebras-wafer)
- Data moves between PEs as 32-bit wavelets. There are 24 routable colors per PE plus 8 reserved. Concurrent streams need separate colors, and congestion on one color does not block another. Each PE's router table maps colors to directions, and this routing is fixed at compile and load time. — [Cerebras SDK docs](https://sdk.cerebras.ai/llms-full.txt); [SpaDA: Spatial Dataflow Architecture Programming Language (arXiv 2511.09447)](https://arxiv.org/html/2511.09447v2)
- The WSE-2 has 850,000 PEs in a 2D grid, and one academic source cites 730k–900k PEs across generations. — [Cerebras SDK Technical Overview white paper](https://8968533.fs1.hubspotusercontent-na2.net/hubfs/8968533/Cerebras%20SDK%20Technical%20Overview%20White%20Paper.pdf); [SpaDA](https://arxiv.org/pdf/2511.09447)
- Academic work is building higher-level compilers above CSL, including an MLIR lowering pipeline for stencils and the SpaDA language. This suggests that hand-written CSL is seen as low-level. — [MLIR Lowering Pipeline for Stencils at Wafer-Scale (arXiv 2601.17754)](https://arxiv.org/pdf/2601.17754); [Stencil Computations on Cerebras WSE (arXiv 2605.07954)](https://arxiv.org/html/2605.07954v1)

**Tenstorrent TT-Metalium [VENDOR docs]**
- The programming model is cooperative. Each Tensix core typically runs three kernels: a reader (DRAM or NoC into local SRAM), a compute kernel, and a writer (back out). — [TT-Metalium docs: Lab 1 single-core matmul](https://docs.tenstorrent.com/tt-metal/latest/tt-metalium/tt_metal/labs/matmul/lab1/lab1.html); [METALIUM_GUIDE.md](https://github.com/tenstorrent/tt-metal/blob/main/METALIUM_GUIDE.md)
- Circular buffers (CBs) are the channels between kernels, with one producer and one consumer each and up to 32 per Tensix. The host allocates them and kernels refer to them by index (e.g., CB 0/1 for inputs, CB 16 for output in the matmul example). Sizing a CB for two tiles gives double buffering. — [TT-Metalium docs: Eltwise binary](https://docs.tenstorrent.com/tt-metal/latest/tt-metalium/tt_metal/examples/eltwise_binary.html); [Matmul single core](https://docs.tenstorrent.com/tt-metal/latest/tt-metalium/tt_metal/examples/matmul_single_core.html); [FlashAttention tech report](https://github.com/tenstorrent/tt-metal/blob/main/tech_reports/FlashAttention/FlashAttention.md)
- Each Tensix has 5 "baby" RISC-V cores. Two data-movement RISCs run the reader and the writer, and the compute kernel is compiled into three threads (unpack, math/FPU, pack) on the other three. Sources number the cores differently (RISC0 = reader / RISC1 = writer / RISC2–4 = compute in the FlashAttention report, versus a different numbering in an arXiv fusion paper), so treat the exact index mapping as implementation detail. — [FlashAttention tech report](https://github.com/tenstorrent/tt-metal/blob/main/tech_reports/FlashAttention/FlashAttention.md); [Operator Fusion for LLM Inference on Tensix (arXiv 2606.09879)](https://arxiv.org/pdf/2606.09879); [TT-Metalium eltwise docs](https://docs.tenstorrent.com/tt-metal/latest/tt-metalium/tt_metal/examples/eltwise_binary.html)
- Cores talk to DRAM and to each other over two NoCs. — [tensixfuse repo](https://github.com/tanaymihani/tensixfuse)
- TTNN is the higher-level, PyTorch-like op library above Metalium. — [PyPI ttnn](https://pypi.org/project/ttnn/)

**Comparison table (synthesis)**

| | CUDA (GPU) | CSL (Cerebras) | TT-Metalium (Tenstorrent) |
|---|---|---|---|
| Execution model | SIMT; grid of blocks, warps of 32; time-multiplexed | Spatial dataflow; one program per PE (or region); tasks triggered by events or data | Per-core MIMD; 3 cooperating kernels (reader/compute/writer) |
| Local memory | Registers + shared memory (≤228 KB/SM on H100), managed by programmer | 48 KB per PE (code + data) | ~1.5 MB SRAM per Tensix (Blackhole) |
| Communication | Global memory/L2; shuffles; DSMEM in clusters | 32-bit wavelets on statically routed colors to neighbours | NoC reads/writes between cores/DRAM; CBs within a core |
| Synchronization | `__syncthreads`, barriers, kernel boundaries | Task activation, wavelet arrival | CB push/pop (producer–consumer) |
| Latency hiding | Many resident warps (occupancy) | Pipelining through the fabric; data arrives as needed | Double-buffered CBs overlapping data movement and compute |

### Inferences
- In a course diagram, CUDA "brings data to compute" through a cache hierarchy, while CSL and Metalium "place compute next to data" and make data movement explicit. Tenstorrent's reader/compute/writer split resembles a hand-built version of Hopper's TMA + warp-specialized producer/consumer pattern. That is a useful bridge for students who already know CUDA (my analogy, not from a source).

### Gaps
- I found no independent productivity or usability study comparing CSL or Metalium to CUDA.

## 5. Scaling: GPU parallelism over NVLink/IB vs Cerebras weight streaming (MemoryX/SwarmX) vs Tenstorrent Ethernet meshes

### Takeaway
GPUs scale by combining tensor, pipeline and data parallelism. Tensor parallelism stays inside the NVLink domain (8 GPUs on HGX, 72 on NVL72), and InfiniBand or Ethernet connects racks. For training, Cerebras separates storage from compute: weights live in the external MemoryX store and are streamed layer by layer to CS-3s, with SwarmX broadcasting weights and reducing gradients, so the wafer only holds activations. For fast inference, Cerebras instead keeps weights in SRAM spread across several wafers. Tenstorrent puts Ethernet ports on every chip and builds 2D meshes (Galaxy: 32 chips per box), using the same fabric within and between boxes.

### Cited Findings
- NVL72 is a 72-GPU NVLink domain with about 130 TB/s all-to-all (GB200), rising to about 216–260 TB/s on Vera Rubin depending on spec revision. — [cyfuture GB200](https://cyfuture.ai/nvidia-gb200-gpu-server); [nextpcb](https://www.nextpcb.com/blog/nvidia-gb200-nvl72-architecture); [pasqualepillitteri.it](https://pasqualepillitteri.it/en/news/27546/nvidia-site-confirms-vera-rubin-spec-cut-hbm4-nvlink-6)
- **Cerebras [VENDOR]:** MemoryX stores weights and streams them to CS-3s, and SwarmX handles broadcast and reduction across systems. The Hot Chips deck presents this mainly as a *training* architecture. MemoryX capacity is quoted as 1.2 PB or 1.5 PB depending on source. — [Cerebras Hot Chips 2024](https://hc2024.hotchips.org/assets/program/conference/day2/72_HC2024.Cerebras.Sean.v03.final.pdf); [introl](https://introl.com/blog/cerebras-wafer-scale-engine-cs3-alternative-ai-architecture-guide-2025); [clarigital](https://www.clarigital.com/hardware/ai-chips/cerebras/cs3/)
- Defenders argue that Cerebras does not need a whole model on one wafer, because MemoryX streaming and SwarmX multi-wafer setups handle large models. Critics note that low-latency inference still needs weights resident in SRAM, so a 70B FP16 model needs about four CS-3s. — [ustastockman substack (pro-Cerebras)](https://ustastockman.substack.com/p/the-cerebras-bear-case-is-built-on); [Spheron Cerebras vs H100](https://www.spheron.network/blog/cerebras-vs-nvidia-h100-inference-2026/)
- **Tenstorrent:** each Blackhole p150 has 4 × 800G QSFP-DD ports. Other sources give conflicting aggregate Ethernet figures (3.2 Tb/s vs "1 TBps across ten 400 Gb links," the latter likely the on-package chip spec). Galaxy servers combine many chips into one mesh, and a vendor-linked 2026 demo ran DeepSeek R1 on 16 Blackhole Galaxy units. — [Spheron Tenstorrent vs NVIDIA](https://www.spheron.network/blog/tenstorrent-vs-nvidia-open-source-ai-hardware/); [gpu.net: Inside Tenstorrent chips (2026-06)](https://blog.gpu.net/posts/2026/june/new-blog-june11/)

### Inferences
- Interconnect philosophy: NVIDIA uses a proprietary scale-up fabric (NVLink/NVSwitch) plus a separate scale-out network. Tenstorrent uses one commodity-Ethernet fabric for both, which costs less but has lower per-link bandwidth than NVLink 5/6. Cerebras uses on-wafer fabric for "scale-up" (the wafer is effectively a whole rack of chips), with SwarmX and Ethernet between wafers.

### Gaps
- I did not retrieve the Galaxy box's chip count, mesh topology, or per-box bandwidth from a primary source in this session (commonly 32 chips in a 4×8 mesh, which is background knowledge and unverified).
- I found no independent benchmarks of Cerebras multi-system weight-streaming training efficiency versus GPU clusters.

## 6. Evidence: benchmarks and published comparisons

### Takeaway
On single-stream decode speed, independent measurements by Artificial Analysis confirm that Cerebras is much faster than GPU clouds: for example, 981 tok/s on Kimi K2.6 (about 1T parameters), 6.7x the fastest GPU provider (May 2026). Vendor claims tend to run higher than AA's numbers, e.g., about 3,000 tok/s claimed vs about 1,700 measured on gpt-oss-120B. In HPC, peer-reviewed WSE-2 molecular dynamics work showed 179x Frontier on timesteps/s, but only for problems that fit on a single wafer. Tenstorrent's published numbers are vendor-reported repo tables, with moderate per-user speeds (about 70 tok/s/user on Galaxy for Llama 70B).

### Cited Findings
**Cerebras LLM inference**
- **[INDEP, AA]** On 2026-05-06, Artificial Analysis measured Cerebras serving Kimi K2.6 at 981 output tok/s. That was 6.7x the next-fastest GPU cloud and 23x the median provider, and AA's co-founder called it the fastest they had measured on a trillion-parameter model. — [VentureBeat](https://venturebeat.com/ai/cerebras-says-its-chips-run-a-trillion-parameter-ai-model-nearly-7-times-faster-than-gpu-clouds); [Artificial Analysis: Cerebras provider page](https://artificialanalysis.ai/providers/cerebras)
- **[VENDOR citing AA]** OpenAI's GPT-5.6 Sol "Ultrafast" mode on Cerebras runs at up to 750 tok/s, about 14x Standard (limited preview). — [Cerebras blog: GPT-5.6 Sol at 750 tok/s](https://cerebras.ai/blog/how-cerebras-serves-gpt-5-6-sol-at-up-to-750-tokens-per-second); [HPCwire](https://www.hpcwire.com/off-the-wire/cerebras-powers-openais-gpt-5-6-sol-ultrafast-mode/)
- **[INDEP vs VENDOR gap]** gpt-oss-120B: one analysis reports about 1,700 tok/s sustained as measured by AA, versus Cerebras's claim of about 3,000. Cerebras says most GPU vendors serve it at 100–300 tok/s. — [morphllm: Cerebras pricing](https://www.morphllm.com/cerebras-pricing); [Cerebras: Blackwell vs Cerebras](https://www.cerebras.ai/blog/blackwell-vs-cerebras)
- **[VENDOR]** Llama 3.1 70B at about 2,100 tok/s at batch 1, priced at $0.60/M tokens. A GPU comparison puts H100 serving of Llama 70B at about $0.10–0.25/M output tokens at large batch. — [Spheron Cerebras vs H100](https://www.spheron.network/blog/cerebras-vs-nvidia-h100-inference-2026/)
- A CS-4 claim of "4,400 tok/s, up to 30x vs GPUs" appears in news aggregators. It is a vendor claim and I could not verify it. — [aiweekly](https://aiweekly.co/alerts/cerebras-cs-4-posts-4400-tokenssec-up-to-30x-vs-gpus)
- Caveat: fast decode does not shorten time-to-first-token or prefill. AA's end-to-end metric includes input processing. One analysis argues that Cerebras "won speed, not the shortlist" (i.e., speed alone does not win procurement). — [benchlm.ai](https://benchlm.ai/blog/posts/cerebras-won-speed-not-the-shortlist); [Spheron Groq vs Cerebras](https://www.spheron.network/blog/groq-lpu-vs-cerebras-wse-cheapest-inference-2026/)

**Cerebras scientific computing [peer-reviewed / lab-reported]**
- "Breaking the Molecular Dynamics Timescale Barrier Using a Wafer-Scale System" (Sandia/LLNL/LANL + Cerebras, 2024; Gordon Bell 2024 *finalist*, not winner). Running embedded-atom-method (EAM) MD on WSE-2 with one atom per core and about 800k atoms, it reached 270,097 timesteps/s versus 1,530 for LAMMPS on Frontier GPUs: **179x Frontier** and **55x Quartz** for tantalum. The authors also report one to two orders of magnitude better energy efficiency. — [arXiv 2405.07898](https://arxiv.org/pdf/2405.07898); [LLNL news](https://www.llnl.gov/article/52081/nnsa-researchers-break-molecular-dynamics-timescale-barrier-worlds-largest-chip); [The Next Platform, 2024-05-15](https://www.nextplatform.com/2024/05/15/one-cerebras-wafer-beats-an-exascale-super-at-molecular-dynamics/)
- **Lab caveat:** the researchers said this "doesn't mean the chip is faster overall than exascale systems like Frontier." The advantage applies to smaller problems that fit on one chip (strong scaling for long timescales). — [LLNL](https://www.llnl.gov/article/52081/nnsa-researchers-break-molecular-dynamics-timescale-barrier-worlds-largest-chip); [Next Platform](https://www.nextplatform.com/2024/05/15/one-cerebras-wafer-beats-an-exascale-super-at-molecular-dynamics/)
- A later Cerebras release (Nov 2024, also a Gordon Bell finalist) claims more than 1.1M steps/s, 748x Frontier. Other coverage cites 457x. These use different configurations or benchmarks, and the 179x figure is the one from the original paper. — [Cerebras blog: exascale MD record](https://www.cerebras.ai/blog/cerebras-breaks-exascale-record-for-molecular-dynamics-simulations); [BusinessWire 2024-11-18](https://www.businesswire.com/news/home/20241118595546/en)
- The 2024 Gordon Bell Prize itself went to a University of Melbourne-led quantum MD project on Frontier. — [ORNL](https://www.ornl.gov/news/calculations-frontier-earns-gordon-bell-prize-ornl-major-presence-sc24)
- 2026 stencil work on WSE exists. — [Stencil Computations on Cerebras WSE (arXiv 2605.07954)](https://arxiv.org/html/2605.07954v1) (search snippet only; I did not read the results)

**Tenstorrent [VENDOR repo tables]**
- On Wormhole Galaxy, Llama 3.3 70B at batch 32 runs at 72.5 tok/s/user (about 2,269 tok/s total) on a tt-metal v0.65 release candidate, and an earlier table lists 66.7 tok/s/user for Llama 3.1 70B. On Blackhole QuietBox, Llama 3.1 70B runs at about 14.9 tok/s/user versus 15.9 on Wormhole QuietBox, and Blackhole is flagged as "under active development." — [tt-metal MODEL_UPDATES.md](https://github.com/tenstorrent/tt-metal/blob/main/models/docs/MODEL_UPDATES.md); [tt-metal README tables](https://github.com/mgajewskiTT/tt-metal)
- A blog cites Tenstorrent figures of 4,000–5,000 tok/s at batch 32. That does not match the repo tables, so treat it with caution. A 2026 demo ran DeepSeek R1 at 350+ tok/s/user on 16 Blackhole Galaxies. — [gpu.net blog (2026-06)](https://blog.gpu.net/posts/2026/june/new-blog-june11/)

### Inferences
- Fair framing: Cerebras's clearest independently verified advantage is **latency/tokens per second per user** and **strong-scaling HPC on problems that fit on the wafer**. GPUs' advantage is **throughput per dollar at high batch** and capacity per device. For Tenstorrent, I found no independent third-party benchmark showing it beats GPUs on a headline metric. Its pitch is cost and openness.

### Gaps
- I did not retrieve the live AA leaderboard values. Re-check [artificialanalysis.ai/providers/cerebras](https://artificialanalysis.ai/providers/cerebras) before publishing.
- I found no MLPerf submissions from Cerebras or Tenstorrent in search results (I believe neither submits regularly; unverified).

## 7. Limitations and criticism of each architecture

### Takeaway
GPUs face the memory wall, high cost, rising power per rack, and vendor lock-in through CUDA, plus evidence of spec slippage (Rubin). Cerebras faces small SRAM capacity per wafer (44 GB), which forces multi-system deployments for large models, high system power (about 23 kW per CS-3), a niche programming model, and per-token prices that are unfavourable compared with batched GPUs. Tenstorrent faces software immaturity, spec reductions in shipping hardware, and modest memory bandwidth.

### Cited Findings
- **GPU:** Rubin's HBM4 and NVLink specs were cut after launch (22 to 19.2 TB/s; 3.6 to 3 TB/s). — [pasqualepillitteri.it](https://pasqualepillitteri.it/en/news/27546/nvidia-site-confirms-vera-rubin-spec-cut-hbm4-nvlink-6); [Wccftech](https://wccftech.com/nvidia-official-statement-on-vera-rubin-spec-change/)
- **GPU:** decode stays below the ridge point even at batch 64, so much of the peak FLOPs goes unused during decode. — [Zartis](https://www.zartis.com/you-dont-have-a-compute-problem-you-have-a-bytes-per-token-problem/); [Spheron roofline](https://www.spheron.network/blog/the-roofline-model-for-llm-inference-are-you-compute-bound-o/)
- **Cerebras:** a 70B FP16 model needs about four CS-3s. — [Spheron](https://www.spheron.network/blog/cerebras-vs-nvidia-h100-inference-2026/). An unverified estimate puts the cost at $8–12M per 70B instance. — [Medium](https://machine-learning-made-simple.medium.com/why-cerebras-raised-at-56-4-billion-usd-to-attack-nvidias-memory-bottleneck-c11bfe81f417)
- **Cerebras:** CS-3 power is about 23 kW in a 15U chassis according to most sources, though one source says 15 kW. — [introl](https://introl.com/blog/cerebras-wafer-scale-engine-cs3-alternative-ai-architecture-guide-2025); [mirrorfrog](https://mirrorfrog.com/en/docs/cards/cerebras/wse-3/)
- **Cerebras:** dense GPU clusters win on raw cost per unit of compute because they spread hardware cost across many concurrent users. — [damnang: WSE-3 physical ceiling](https://www.damnang.com/p/cerebras-wse-3-the-technical-achievement)
- **Cerebras:** one source argues that WSE-3 is not faster per core than WSE-2 and that its gains come from more cores and memory (snippet only). — [clarigital](https://www.clarigital.com/hardware/ai-chips/cerebras/cs3/)
- **Cerebras:** in CSL, 48 KB per PE must hold both code and data ("your entire world"), which constrains kernel design. — [wafer.ai substack](https://wafer.substack.com/p/breaking-down-the-cerebras-wafer); [Cerebras SDK docs](https://sdk.cerebras.ai/llms-full.txt)
- **Cerebras (MD paper):** the advantage is limited to problems that fit on one wafer. — [LLNL](https://www.llnl.gov/article/52081/nnsa-researchers-break-molecular-dynamics-timescale-barrier-worlds-largest-chip)
- **Tenstorrent:** The Register's review of the Blackhole QuietBox (2025-11-27) is titled "a high-performance RISC-V AI workstation trapped in a software blackhole," a critique of software maturity. — [The Register review](https://www.theregister.com/2025/11/27/tenstorrent_quietbox_review/)
- **Tenstorrent:** firmware cut shipping p150 cards from 140 to 120 cores and peak from 774 to 664 TFLOPS. Tenstorrent's own docs are still inconsistent (140 vs 120). — [Tom's Hardware](https://www.tomshardware.com/tech-industry/semiconductors/jim-kellers-tenstorrent-is-downgrading-blackhole-p150-cards-from-140-to-120-tensor-cores-via-firmware-update-will-ship-cards-with-120-tensor-cores-going-forward-company-claims-existing-users-should-expect-1-2-percent-performance-drop); [VideoCardz](https://videocardz.com/newz/tenstorrent-downgrades-blackhole-p150-pcie-cards-specs-from-140-to-120-cores)
- **Tenstorrent:** a 2026 blog says there is no Tenstorrent equivalent to vLLM with PagedAttention and continuous batching. However, Tenstorrent maintains a vLLM fork for Galaxy Llama models, so this claim is partly contradicted. — [gpu.net](https://blog.gpu.net/posts/2026/june/new-blog-june11/); contradicted in part by [tt-metal MODEL_UPDATES.md](https://github.com/tenstorrent/tt-metal/blob/main/models/docs/MODEL_UPDATES.md)
- **Tenstorrent:** Blackhole is at 512 GB/s GDDR6 per card, against 8 TB/s for B200. — [gpusmith datasheet](https://gpusmith.com/datasheets/tenstorrent-blackhole-p150-datasheet.pdf)

### Inferences
- Each design's strength is also its weakness. SRAM-centric Cerebras gets bandwidth but gives up capacity. HBM-centric GPUs get capacity but give up bandwidth per FLOP. GDDR+Ethernet Tenstorrent gets low cost and openness but gives up bandwidth and software maturity. A three-axis radar or table (bandwidth per device, capacity per device, cost and software maturity) would capture this for the course.

### Gaps
- I found no reliable source on Cerebras wafer yield or redundancy overhead (spare cores and rows), and no independent measurement of WSE utilization. Cerebras's public statements say the WSE uses redundant cores and routes around defects (background knowledge, unverified).
- I found no independent TCO study comparing all three. No SemiAnalysis article on Cerebras or Tenstorrent economics came up in search results (SemiAnalysis's InferenceX pages cover only GPU specs).
- I found no measured power-efficiency comparison (tokens per joule) across the three from an independent source.
