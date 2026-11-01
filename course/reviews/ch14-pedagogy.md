# ch14 · pedagogy review

Summary: The chapter is short (about 150 lines) and assumes more GPU knowledge than the target learner has. Core terms (SM, HBM, SIMT, NVLink/NVSwitch, NVL72, HGX, SXM, InfiniBand, FP4/NVFP4, Tensor Core, the kinds of parallelism) are used but never defined. The first objective ("Describe an SM") is not supported by any content or figure: Tensor Cores, warp schedulers and the occupancy limits never appear. The occupancy widget is good, but the matching quiz answer (21 warps per scheduler) is more than an H100 can hold, and the chapter never says so. Several Cerebras comparisons are loose (8 microthreads vs 2,048 threads, "nothing to hide", 66 MB vs 44 GB). The chapter needs one SM anatomy figure, a glossary pass, three or four worked examples and a stronger quiz.

## Findings

### P1 [critical] No SM anatomy; Tensor Cores never mentioned, so objective 1 is not met
- Location: objectives (line 18); "The memory hierarchy" and "SIMT" sections (lines 39–52).
- Problem: The first objective asks the learner to "Describe an SM", but the chapter never says what is inside one. The only per-SM facts are register and L1 sizes in a caption. Tensor Cores, the units that produce the 989 TF figure in the table and in Chapter 1, appear nowhere. The chapter also never says that an SM has 4 sub-partitions, each with its own warp scheduler, that it has FP32 lanes, or that it holds at most 64 resident warps.
- Why it matters: The learner cannot connect "132 SMs" to "989 TF". They also cannot compare an SM with a Cerebras PE (8-wide SIMD, Chapter 3) or a Tensix core (Chapter 13), and that comparison is the point of Part IV. Chapter 15's table says "132 SMs with Tensor Cores" without this chapter ever introducing them.
- Concrete fix: Add an "Inside an SM" section with an SVG showing the SM as 4 sub-partitions. Give each sub-partition a warp scheduler, a register-file slice, 32 FP32 lanes and 1 Tensor Core, and draw a shared L1/shared-memory block underneath. Tag the per-SM breakdown as Vendor (Hopper whitepaper). The research notes (gpu_and_comparison.md line 46) flag it as not yet re-verified, so check it before use. Add one sentence explaining that a Tensor Core is a matrix-multiply unit doing a small tile MMA per instruction, which is where nearly all of the AI FLOPs come from. Add a three-column comparison with a WSE-3 PE and a Tensix core, covering unit count, local memory, math engine and threads in flight.

### P2 [major] Core jargon used without definition
- Location: lede (HBM), line 18 (SM), line 26 (SXM), line 27 ("reticle-size die"), lines 29–31 (FP4, NVFP4, NVLink, "scale-up domain", HGX, NVL72), line 47 (SIMT), line 106 (NVSwitch, InfiniBand, tensor/pipeline/data parallelism), line 112 ("2:4 structured sparsity").
- Problem: None of these terms is expanded or explained where it first appears. "SIMT" appears only in a heading. HBM is described as "relatively slow", which is confusing for a technology whose name is "High Bandwidth Memory". It is slow in *latency*, not in bandwidth.
- Why it matters: A learner with limited GPU knowledge will stall on the table in the first section. The "slow HBM" wording may also undo Chapter 1's bandwidth framing.
- Concrete fix: Expand each term at first use. Suggested wording:
  - SM: "Streaming Multiprocessor, the GPU's core; H100 has 132".
  - HBM: "High Bandwidth Memory: stacks of DRAM dies on the same package, beside the GPU die. High bandwidth, but hundreds of cycles of latency". Change the lede to "big, high-bandwidth but high-latency memory".
  - SIMT: "Single Instruction, Multiple Threads. You write scalar code per thread and the hardware groups 32 threads into a SIMD-like warp. Contrast: on a PE you issue the vector op yourself via a DSD".
  - NVLink/NVSwitch: "NVIDIA's GPU-to-GPU link and the switch chip that connects many GPUs at NVLink speed".
  - Scale-up vs scale-out: "scale-up = GPUs sharing a memory-semantic NVLink domain; scale-out = a normal network between such domains".
  - HGX / NVL72: "an 8-GPU board / a 72-GPU rack in one NVLink domain".
  - SXM: "socketed module form factor, as opposed to a PCIe card".
  - Reticle: point to Chapter 2's reticle limit.
  - FP4/NVFP4.
  - Tensor, pipeline and data parallelism: one line each, mapped to Chapter 8's "layers across wafers" (pipeline).
  - 2:4 sparsity: "2 of every 4 weights are zero".

  A small `<dl>` glossary callout after the table would also work.

### P3 [major] Generation table mixes precisions and gives no narrative, which invites a false "50x" reading
- Location: lines 24–33, "Low-precision peak" row.
- Problem: The row compares BF16 dense (H100), FP4 dense (B200) and NVFP4 inference (Rubin). The learner sees 989 TF to 9 PF to 50 PF and reads it as a 10–50x compute gain, when most of that gain comes from halving the precision twice. The objective promises "the H100 → B200 → Rubin progression", but the chapter never says what changed or why. Examples: two dies because a single die cannot exceed the reticle limit (the problem Cerebras solves by stitching across the wafer, Chapter 2), and HBM bandwidth growing faster than capacity. The Rubin "Dies" cell is an unexplained "—", although the notes say 2 compute dies.
- Why it matters: This is the same marketing trap Q3 warns about, but here the chapter sets it itself. The missing narrative also leaves objective 1 unmet.
- Concrete fix: Add a same-precision row, e.g. BF16 or FP8 dense for all three (tagged Vendor/derived), or annotate each cell with its precision in bold. Fill Rubin "Dies" with "2 compute dies" from the research notes. Add 3–4 sentences of narrative: each generation buys more FLOPs mainly through lower precision and more silicon; more silicon means multiple dies because of the reticle; HBM bandwidth roughly doubles per generation; NVLink grows so that the rack behaves like one big GPU. Then tie it to Cerebras: the wafer is the extreme answer to the same reticle limit.

### P4 [major] Quiz Q2 answer is impossible on real hardware, and the limit is never taught
- Location: quiz Q2 (line 111); widget hint (line 56) says "the SM's scheduler"; line 65 says "up to 2,048 threads".
- Problem: The answer "21 warps per scheduler" is not achievable. An H100 SM holds at most 64 warps (2,048 threads), which is 16 per scheduler. The widget slider also stops at 16 without saying why. The widget talks about "the SM's scheduler", singular, while the quiz says "per scheduler", and the chapter never says there are 4 per SM.
- Why it matters: This is the key insight of the occupancy model. When the required warps exceed what fits, occupancy alone cannot hide the latency, and GPU programmers turn to ILP, prefetching into shared memory, or async copies (TMA). Leaving it out teaches that the GPU can always hide latency. The singular/plural mismatch also confuses the mental model.
- Concrete fix: State in the SIMT section: "4 warp schedulers per SM, at most 16 resident warps each (64 per SM, 2,048 threads)". Label the widget slider max "(H100 limit per scheduler)". Rewrite the Q2 answer: "(C+L)/C = 21 warps per scheduler, but H100 allows at most 16, so utilisation tops out near 16·20/420 ≈ 76%. To go further you need more independent loads per warp (ILP) or software prefetch into shared memory." This also makes the question non-trivial.

### P5 [major] What limits occupancy is never explained (registers and shared memory)
- Location: "Occupancy" bullet (line 51) and hierarchy caption (line 44).
- Problem: The chapter says "keep enough warps resident", but never says what stops you. The 256 KB register file and the 228 KB of shared memory are shared among resident threads. The learner gets the sizes in the caption and the occupancy idea in the bullet, but nothing joins them.
- Why it matters: This is the main internal behaviour a CUDA programmer reasons about, and it is a direct parallel to Cerebras's 48 KB-per-PE budget for code and data. Without it, "occupancy" is a slogan.
- Concrete fix: Add a worked example. 256 KB / 4 B = 65,536 registers per SM. At 32 registers/thread that is 2,048 threads (full occupancy). At 64 registers/thread it is 1,024 threads (50%). At 128 registers/thread it is 512 threads (25%), so latency hiding halves each time. Do the same for shared memory: a block using 100 KB of shared memory leaves room for only 2 blocks per SM. Follow it with a one-line contrast: on a PE, code + data + buffers compete for 48 KB, but no memory latency has to be hidden in exchange.

### P6 [major] Coalescing explained without numbers; the strided-access answer is unsupported
- Location: "Coalescing" bullet (line 50); quiz Q1 (line 110).
- Problem: "Merge into a few wide memory transactions" has no unit. The learner does not know a transaction is a 32-byte sector (128-byte line), so they cannot derive "bandwidth roughly halves" in Q1. The answer is given, not reasoned.
- Why it matters: Coalescing is one of the two rules said to "dominate performance". Without a worked example it cannot be applied to a new access pattern, e.g. stride 32 or a column read of a row-major matrix.
- Concrete fix: Add a small diagram or worked example. A warp reads 32 consecutive floats = 128 B = 4 sectors (100% useful). With `x[2*i]` it spans 256 B = 8 sectors, half of which is wasted (50%). With `x[32*i]` every thread hits its own sector: 32 sectors for 128 useful bytes, 12.5%. Rewrite the Q1 answer with this arithmetic. Optionally add Q: "a warp reads a column of a row-major 1024×1024 float matrix — efficiency?" Answer: 1 useful float per 32-byte sector, so 12.5%. Contrast with Cerebras: DSD strides on a PE cost nothing extra because the SRAM is single-cycle and accessed per element (Chapter 6).

### P7 [major] "Nothing to hide" and "8 microthreads vs 2,048 threads" are misleading comparisons
- Location: line 65.
- Problem: (a) A PE does have latency to hide: fabric wavelets from neighbours arrive over many cycles. Cerebras hides it with dataflow tasks triggered by arrival and with async DSD ops on microthreads (Chapters 4–5), not with many threads. Saying "the wafer needs none of this" is too strong. (b) Microthreads are slots for concurrent async vector operations (Chapter 3), not threads of control like CUDA threads. Putting "8" next to "2,048" implies they are the same kind of thing.
- Why it matters: The chapter's stated purpose is to sharpen understanding of Cerebras by contrast. An inaccurate contrast undoes Chapters 3–5.
- Concrete fix: Reword along these lines: "A PE's own SRAM answers in one cycle, so local loads need no hiding. Latency still exists on the fabric, but the wafer hides it differently: a task runs when its data arrives (Chapter 5), and up to 8 async DSD operations, one per microthread, overlap send, receive and compute. A GPU hides latency by oversubscription (many warps waiting); the wafer hides it by dataflow (work starts when data shows up)." Add a 2-row table: latency source / hiding mechanism / what the programmer controls.

### P8 [major] SAXPY comparison: CUDA indexing, launch syntax and CSL data distribution unexplained
- Location: lines 67–103.
- Problem: `blockIdx.x * blockDim.x + threadIdx.x`, the `<<<(n + 255) / 256, 256>>>` launch and the `if (i < n)` guard are not explained. The CSL side does not say that `N` is the *per-PE* slice length (it is `param N` in program 01), or how x and y get onto PEs: the host-side memcpy to a PE rectangle that corresponds to `cudaMemcpy`. `sys_mod.unblock_cmd_stream()` appears without a cross-reference. "One instruction per PE over its local slice" is unclear without knowing that the slices come from the host's split. "Kernel boundaries" (line 103) as a synchronisation mechanism is undefined.
- Why it matters: Objective 3 is to translate SAXPY between CUDA and CSL, and the learner cannot do that without understanding both halves. Because the CSL side hides the distribution step, the comparison makes the wafer look simpler than it is.
- Concrete fix:
  - Annotate the CUDA code: the grid is ⌈n/256⌉ blocks of 256 threads, `i` is the thread's global index, and the guard handles the last partial block. Worked example: n = 1,000,000 gives 3,907 blocks; the last block has 64 active threads and 192 masked.
  - Add a short host-side CSL snippet or comment (e.g. `runner.memcpy_h2d(x_symbol, x, ... width, height ...)` from program 01's run.py) and say: "the host splits x and y into N-element slices, one per PE; `unblock_cmd_stream` hands control back to the host command stream (Chapter 7)".
  - Define "kernel boundary": a kernel launch ends only when all its blocks finish, so the next kernel can safely read what they wrote to HBM. It acts as a global barrier.
  - Add an aligned "who does what" mapping (thread ↔ PE-slice, block ↔ no equivalent, HBM ↔ per-PE SRAM, cudaMemcpy ↔ memcpy_h2d, kernel launch ↔ host-called function).

### P9 [major] No worked example linking GPU capacity vs bandwidth to Chapters 1 and 8
- Location: "Scaling out" (line 106).
- Problem: "A 70B FP16 model fits on one B200; on Cerebras it needs four wafers" gives the capacity side only. It shows no arithmetic (140 GB vs ~180 GB usable, with KV cache eating the rest) and leaves out the consequence for decode speed, the reason Cerebras accepts four wafers.
- Why it matters: Without the bandwidth half, a learner may conclude GPUs simply win. The trade-off (capacity vs bandwidth per token) is the main lesson of the comparison, and Chapter 1 already set it up.
- Concrete fix: Add a worked example with Derived tags. Batch-1 decode on one B200 has to read all 140 GB of weights per token: 140 GB ÷ ~8 TB/s ≈ 17.5 ms, so at most ~57 tokens/s per sequence. Batching raises throughput but not per-sequence speed. On four wafers the weights stay in SRAM, so the token rate is set by the pipeline, not by HBM. Add one line on KV cache: 180 − 140 = ~40 GB left for KV cache and activations, which limits batch size and context length.

### P10 [minor] Memory hierarchy figure is vague and its Cerebras comparison is one-sided
- Location: figure (lines 40–45) and script levels (lines 119–120).
- Problem: Latencies are "tens of cycles" and "hundreds of cycles", and L1/shared and register bandwidth are missing. The 66 MB total is not derived (132 × 512 KB). "Compare with 44 GB of SRAM" leaves out that per-unit the numbers are 512 KB/SM vs 48 KB/PE, and that the GPU also has 50 MB of L2 plus 80 GB of HBM. L1 (hardware cache) vs shared memory (programmer-managed scratchpad) is never distinguished, although shared memory is the closest analogue to PE SRAM.
- Why it matters: The research notes (line 92) ask the course to state that the fair comparison for 21 PB/s is the GPU's aggregate register + shared bandwidth. The caption invites the opposite, unfair comparison.
- Concrete fix: Show the derivation "132 × (256 + 256) KB ≈ 66 MB". Add a parallel mini-column for WSE-3 (PE registers → 48 KB SRAM, 1 cycle → neighbours via fabric → host/MemoryX), so the two hierarchies sit side by side. Add one sentence: "shared memory is a scratchpad you manage explicitly, like a PE's SRAM; L1 is a hardware cache, which the PE does not have (Chapter 3)". Give approximate cycle counts if a source supports them (tag Indep).

### P11 [minor] Warp divergence stated without an example
- Location: line 48.
- Problem: "A fully divergent warp runs at 1/32 of peak" is stated with no example of how it happens, e.g. `if (threadIdx.x % 2)` costs 2x and a 32-way switch on the lane costs 32x. The Cerebras counterpart, where each PE runs its own control flow freely because PEs are independent (MIMD across PEs), is not given.
- Why it matters: Divergence is a key SIMT internal behaviour, and the contrast with independent PEs is cheap to add and instructive.
- Concrete fix: Add a 3-line example with its cost and one line: "On the wafer each PE has its own instruction stream, so neighbouring PEs can take different branches at no cost; the lockstep penalty applies only within one PE's SIMD vector op."

### P12 [minor] Widget model not derived; formula appears only in the readout
- Location: widget (lines 54–64) and readout (line 144).
- Problem: The readout prints `min(1, W·C/(C+L))` and `⌈(C+L)/C⌉`, but the prose never derives them. The idea is that each warp is busy C out of every C+L cycles, so W warps fill W·C of every C+L cycles. Nor does the prose say that the model assumes one scheduler issuing one warp at a time.
- Why it matters: Learners copy formulas they cannot rederive, and Q2 depends on this one.
- Concrete fix: Add two sentences under the widget deriving the formula. Suggest a guided task, e.g. "Set C=10, L=100: find the W where the SM busy bar becomes solid (11)."

### P13 [major] Check-yourself questions are weak and do not cover the objectives
- Location: quiz (lines 108–113).
- Problem: There are only 3 questions. Q3 repeats Chapter 2's sparsity question almost word for word, and Chapter 2 line 72 already makes the H100 1,979 TF point. Q1 and Q2 are plug-in recall (see P4 and P6 for answer issues). Nothing tests the SM/Tensor Core, divergence, occupancy limits, the CUDA ↔ CSL translation (objective 3) or scale-up vs scale-out.
- Why it matters: The quiz cannot confirm that the objectives were met, and the repeated question wastes a slot.
- Concrete fix: Replace Q3 and add questions such as:
  - (a) "A kernel uses 128 registers/thread. Max resident threads per SM, and what happens to latency hiding?" Answer: 65,536/128 = 512 threads = 16 warps, 4 per scheduler.
  - (b) "Translate: which CSL concept plays the role of blockIdx/threadIdx, and which CUDA concept has no wafer equivalent?" Answer: PE coordinates/slice offsets set by the host layout; thread blocks and HBM have no equivalent.
  - (c) "Why does a 70B model fit on one B200 but still decode slower per sequence than on four wafers?" Answer: per P9.
  - (d) "A warp runs `if (lane < 16) A(); else B();` — cost?" Answer: both paths serially, half the lanes idle in each.
  - (e) "What does NVL72 give that 9 HGX boxes on InfiniBand do not?" Answer: one NVLink domain at ~130 TB/s, enough for tensor parallelism across all 72.
