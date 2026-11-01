# ch08 · depth review

Summary: Chapter 8 gets the two-mode story right (stream weights for training, pin weights for inference), but it is a summary, not an explanation. The research report treats the internals as unknown ("primary details of the older layer-pipelined mode were not found"). In fact three primary sources cover nearly all of them: the Cerebras weight-streaming white paper (Hall, Schreiber, Lie), Sean Lie's Hot Chips 2022 and Hot Chips 2024 decks, and the Cerebras training docs. I downloaded and read all three. They give the step-by-step weight-streaming schedule, the on-wafer GEMM mechanism, MemoryX's bytes-per-parameter budget, SwarmX's tree topology, the layer-pipelined mode, and the on-wafer inference pipeline (regions, KV cache placement, multi-user filling, inter-wafer latency budget). The chapter has no worked numbers for any of these. I also ran the SDK `single-tile-matvec` benchmark in the simulator to get a measured per-PE SRAM bandwidth for a decode-like kernel. The highest-value additions are D1, D2, D7, D9 and D11.

Network note: WebFetch could not resolve cerebras.ai, servethehome.com, training-api.cerebras.ai or venturebeat.com. `curl` through the proxy did work for all of them except VentureBeat, which returned 429. The local copies I read are in `/home/user/cerebras-sdk/tmp/ch08depth/` (hc22.txt, hc24.txt, wsc.txt = white paper, wsdoc.md, hc26.txt, cs4.txt, sol.txt, x3.txt, l405.txt, sth.txt).

Key primary sources used below (short names):
- **WP**: Hall, Schreiber, Lie, "Training Giant Neural Networks Using Weight Streaming on Cerebras Wafer-Scale Systems", Cerebras white paper (mirror: https://www.kisacoresearch.com/sites/default/files/documents/cs_weight_streaming_white_paper_-_cerebras.pdf), 29 pp.
- **HC22**: Sean Lie, "Cerebras Architecture Deep Dive", Hot Chips 34 (https://hc34.hotchips.org/assets/program/conference/day2/Machine%20Learning/HC2022_Cerebras_Final_v02.pdf).
- **HC24**: Sean Lie, "Wafer-Scale AI: GPU Impossible Performance", Hot Chips 2024 (https://hc2024.hotchips.org/assets/program/conference/day2/72_HC2024.Cerebras.Sean.v03.final.pdf).
- **WSDOC**: Cerebras training docs, "Weight Streaming Execution" (https://training-docs.cerebras.ai/rel-2.10.0/concepts/weight-streaming-execution.md).
- **PLDOC**: Cerebras docs R2.0.3, "Pipelined Execution" (https://training-api.cerebras.ai/en/2.0.3/original/cerebras-basics/cerebras-execution-modes.html).
- **HC26B**: Cerebras blog, "Ultrafast Frontier Inference: Cerebras Deep Dive at Hot Chips 2026" (https://www.cerebras.ai/blog/ultrafast-frontier-inference-cerebras-deep-dive-at-hot-chips-2026).
- **CS4B**: Cerebras blog, "Introducing Cerebras CS-4" (https://cerebras.ai/blog/introducing-cerebras-cs-4).
- **STH26**: ServeTheHome, "Cerebras Talks Going Rack-Scale with Their WSEs at Hot Chips 2026" (https://www.servethehome.com/cerebras-talks-going-rack-scale-with-their-wses-at-hot-chips-2026/).

## Gaps and additions (prioritised)

### D1 [critical] The weight-streaming schedule, step by step
**What is missing.** The chapter says "weights in, gradients out" in one sentence. It never says that each layer's weights are streamed **twice** per step (once forward, once backward), that gradients leave the wafer in FP32, what stays on the wafer, or how off-wafer latency is hidden.

**Why it matters.** This is the mechanism the chapter is named for. Pedagogy P1/P7 and visuals V2/N1 point at the same hole, and none of them has the actual sequence to work from.

**Source.** WSDOC (forward and backward bullets); WP pp. 13, 17, 19, 28 [Vendor].

**Proposed addition.** A numbered list, "One training step on a weight-streaming cluster", placed right after the current figure:
1. Each CS-X receives its own shard of the batch from the input workers. That shard is the layer-1 input activation. WP: "a unique shard of the training batch is downloaded from the data service to each CS-2."
2. **Forward pass.** MemoryX streams layer 1's weights, and SwarmX broadcasts one copy to every wafer. Each wafer computes layer-1 activations and **keeps them in SRAM**. Then layer 2's weights arrive, and so on. MemoryX starts sending layer k+1 before layer k finishes, so the stream is pipelined (WP p. 28).
3. At the loss layer the wafer computes the loss delta. SwarmX also reduces the loss values and sends them to the user node (WSDOC).
4. **Backward pass, last layer to first.** The weights are streamed **again**, this time in transposed order. MemoryX keeps both a forward view and a transposed view of the same data (WP p. 27). The wafer uses the stored activations to compute activation gradients and weight gradients. The weight gradients stream out in FP32. SwarmX sums them across wafers. MemoryX applies the optimizer update as the gradients arrive. WSDOC notes that the last layer's weights "can be retained to save time".
5. **Critical path.** Layer 1's weights are the last to get gradients and the first needed in the next step. To shorten that wait, the wafer computes gradients in the same order the forward weights were sent, so updated layer-1 weights can start streaming before the layer-1 gradients are complete. WP: "The round-trip latency … can be completely hidden when the compute time of the first layer is greater than the round-trip latency."
6. Checkpoints are pulled from MemoryX at intervals (WSDOC).

Add a one-line traffic budget: "Per step, each parameter crosses the link 2 × 16 bits inward (FP16 weights, forward and backward) and 32 bits outward (FP32 gradient)" [Vendor, WP p. 13]. A fixer can build the animation proposed in visuals N1 directly from these six steps.

### D2 [critical] Worked example: why streaming weights does not starve the wafer in training
**What is missing.** The chapter asserts that streaming suits training. The quiz answer says it is "amortised", with no numbers. Chapter 7 tells the learner the host link is a narrow door (~14 GB/s), so the learner will ask how 1.2 Tb/s can possibly keep 900k cores busy.

**Why it matters.** This is the single most important "how does it behave" calculation in the chapter, and it reconciles Chapter 7 (pedagogy P2, P4).

**Source.** WP p. 14: "The WSE-2's 1.2Tb/s of I/O bandwidth is used for receiving weights from and transmitting gradients back to the MemoryX service." WP p. 21: "batch shards typically contain hundreds of thousands of tokens." HC22: 7.5 PF FP16 dense [Vendor]. The arithmetic below is [Derived].

**Proposed addition.** A callout box "Worked example: tokens per weight":
- Link: 1.2 Tb/s = 150 GB/s. At 2 bytes per FP16 weight that is **75 G weights/s** into the wafer.
- Each arriving weight does one multiply-add (2 FLOP) per token in the wafer's shard. With T tokens per shard, the wafer does 2·T FLOP per weight.
- To keep a WSE-2 at 7.5 PF dense: 7.5e15 / (2 × 75e9) ≈ **50,000 tokens per shard**. Below that, the link is the bottleneck. Above it, compute is.
- This explains why WP says shards hold "hundreds of thousands of tokens", and why the same trick fails for decode, where T = 1 per sequence: 75 G weights/s at T = 1 is only 150 GFLOP/s, about 0.002% of the wafer.
- The comparison point is the Chapter 1 roofline: training intensity is ≈ T FLOP per byte, decode ≈ 1.

Optional mini-widget: a slider for tokens per shard (1 to 10⁶, log scale) and a WSE-2/WSE-3 toggle that outputs "link-bound or compute-bound, and utilisation = min(1, 2·T·75e9 / peak)". Rewrite quiz Q1's answer to use these numbers. This also fixes accuracy A2.

### D3 [major] How one layer actually runs on the wafer in weight-streaming mode
**What is missing.** The chapter never explains what "the whole wafer computes one layer at a time" means at the PE level, even though Chapters 4–6 have already taught wavelets, colours, multicast and tasks. Those chapters set this up and nothing here pays it off.

**Why it matters.** This is where the architecture chapters meet the system. It also explains native sparsity and why there is no matrix size limit ("up to 100k × 100k MatMul").

**Source.** HC22 slides "Mapping Neural Networks to WSE-2", "Dataflow Execution", "GEMM with Sparse Input", "Partial Sum Reduce". WP pp. 19–25 ("Data Layout on the Wafer", "One Sparse Input", "Sparse Output") [Vendor].

**Proposed addition.** A paragraph plus a diagram titled "A layer on the wafer":
- **Layout.** The activation tensor [B][S][H] is spread across the whole wafer. H (features) is split across the wafer's x axis. B and S are split across y, with consecutive tokens of a sequence on adjacent cores. Because GPT-3's H = 12k is much smaller than the token count, B is also split over x so each core gets a roughly square tile (WP Figs. 10–11).
- **Weights as messages.** Weight rows enter at one edge. Each 32-bit fabric packet carries a 16-bit weight and a 16-bit index (HC22). The packet is multicast down the column of cores that holds the matching features. On arrival, each weight triggers an FMAC against that core's local activations. This is an AXPY, and it is the Chapter 5 "data-triggered task" in production.
- **Reduction.** After a row has been processed, a PSUM command makes the cores in a row ring-reduce their partial sums. An FSUM command sends the final sum to the column that should own that output feature. Reductions overlap with the next row's weights (HC22).
- **Control.** The commands come from MemoryX's coordinator (WP p. 24, Fig. 14).
- **Sparsity for free.** Zero weights are never sent, so they cost no compute and no memory. Weights are never stored on the wafer at all: "No memory used for weights, not even stored temporarily" (HC22).
- **Backward pass.** Weight gradients use a second kernel flavour ("sparse output"): MemoryX sends a sparsity mask, and each masked position triggers a dot product, reduced in a chain along columns (WP pp. 24–26).

Diagram: a grid of PEs with H across and B·S down, a weight row entering from the top edge, a blue multicast down one column, an orange ring reduction along a row, and the result landing in one column. Cross-link to Ch04 (multicast/colours), Ch05 (tasks) and Ch06 (DSDs/FMAC).

### D4 [major] MemoryX: what it stores per parameter, and where its capacity numbers come from
**What is missing.** The table gives "4 TB – 2.4 PB" and "1.2 PB" without saying what is stored, so the numbers mean nothing. Nor does the chapter say what MemoryX computes, or why its compute never becomes the bottleneck.

**Why it matters.** With the bytes-per-parameter figure, the learner can derive the vendor capacity range and sanity-check the "120T"/"24T" claims.

**Source.** WP pp. 12, 16–17, 26–27 [Vendor]. The CS-3 "24 trillion parameters with 1.2 PB" figure appears in Cerebras CS-3 launch coverage (https://www.nextplatform.com/2024/03/14/cerebras-goes-hyperscale-with-third-gen-waferscale-supercomputers/, https://www.cerebras.ai/blog/cerebras-cs3) [Vendor].

**Proposed addition.** A small table, "MemoryX bytes per parameter (WP)":

| Item | Bytes |
|---|---|
| FP32 master weight | 4 |
| FP32 gradient | 4 |
| Adam moment 1 + moment 2 (FP32) | 8 |
| Sparse working copy: FP16 value + 16-bit delta-encoded column index (CSR) | 4 |
| **Total** | **20** |

Follow it with this text:
- "GPT-3 175B × 20 B = 3.5 TB, which is why the smallest MemoryX is 4 TB. 120T × 20 B = 2.4 PB, the top of the range" [Derived; matches vendor endpoints].
- "The CS-3 figure, 1.2 PB for '24T parameters', implies about 50 B/param, so the vendor's assumptions differ between eras" [Derived].

Then a mechanism paragraph:
- MemoryX is DRAM plus flash "in a hybrid fashion". Its storage and I/O "match or exceed the I/O bandwidth of a CS-2".
- It runs any optimizer. Its compute is "three orders of magnitude greater than its I/O bandwidth" in FLOP/s.
- Update cost is O(P) while wafer compute is O(B·S·P), so a single MemoryX can serve a cluster of any size.
- It keeps a dense FP32 copy, so sparsity masks can change (weights can regrow), and it streams the sparse FP16 copy.

### D5 [major] SwarmX internals: a broadcast–reduce tree
**What is missing.** SwarmX is currently a box with a quote. The chapter does not say what hardware it is, how it scales, or why reducing inside the network matters.

**Why it matters.** It explains why scaling is "linear" (pedagogy P8). It is also a concrete contrast with GPU all-reduce, which Chapter 14 can reuse.

**Source.** WP pp. 17–18 [Vendor]. Andromeda result: Cerebras announcement as reposted (https://www.businesswire.com/news/home/20221114005138/en, TechPowerUp) [Vendor].

**Proposed addition.** A paragraph plus a tree diagram for 8 systems, mirroring WP Fig. 9:
- SwarmX is built from **broadcast–reduce nodes**, each with a set of 100 Gb/s interfaces. A node does either one 1:4 broadcast–reduce or a pair of 1:2 operations, and it sums FP gradients **at line rate**.
- The nodes form a bidirectional **tree**. Node count grows linearly with N systems, latency grows with log N, and the reduction is work-efficient (one add per element per CS-2).
- Reducing on the way back makes weight and gradient traffic symmetric: one copy of the gradient tensor crosses each link.
- The abstraction: "From the perspective of the MemoryX service, the SwarmX fabric looks just like a single CS-2 and from the perspective of the CS-2, the SwarmX looks just like the MemoryX service." This is why one compiled mapping runs unchanged on 1 or N systems (WSDOC: "the same mapping is used for every layer across all systems").
- Why only data parallelism: WP p. 10 explains that combining streaming with tensor or pipeline parallelism adds activation traffic, so Cerebras sets Nm = Np = 1.
- Evidence: Andromeda's 16 CS-2 delivered 15.87× the throughput of one CS-2 (GPT-3 XL, 10K sequence length, genomics workload) [Vendor]. Say plainly that this is one vendor workload at 16 systems.

### D6 [major] Layer-pipelined mode: the primary description exists, so replace "not found"
**What is missing.** The chapter says "Primary details of the older layer-pipelined mode were not found." They are in the Cerebras docs.

**Why it matters.** It removes a false gap. It also sets up the inference section: 2024 inference is layer-pipelining brought back for decode (HC24 "Pipeline mapping of model").

**Source.** PLDOC (Cerebras docs R2.0.3, "Pipelined Execution") [Vendor].

**Proposed addition.** Replace the sentence with this:
- "In layer-pipelined mode (CS-1 and the 'Original Cerebras Installation' of CS-2), **all layers are loaded onto the wafer at once**. The compiler maps each layer to a rectangular region and connects the regions with on-wafer data paths. It sizes and places the regions 'to optimize the throughput, which is the number of training samples that the wafer can accept per unit time'."
- "Activations flow forward region to region, activation gradients flow back, and weights stay in their region and are updated on the wafer at the end of each backward step. After an initial fill latency, every region is busy in steady state."
- "It was meant for models under ~1B parameters and does not support multiple CS-2s" [Vendor].

Add a one-line forward pointer: "Inference (below) uses the same spatial idea."

### D7 [critical] What actually happens inside an inference wafer (HC2024)
**What is missing.** The pipeline figure shows four boxes and an arrow. It does not show how layers are laid out on a wafer, where the KV cache lives, what each stage does per token, how the loop closes, or how other users and prefill fill the idle stages (pedagogy P3, visuals V4/N2).

**Why it matters.** This is the core mechanism of Cerebras's main 2024–26 product, and the primary source describes it directly.

**Source.** HC24 slides "Pipeline execution on a single chip", "Pipeline mapping of model", "A low latency pipeline", "Cerebras enables low latency and high throughput", "High performance prompt processing", "Naturally scales to multiple wafers" [Vendor].

**Proposed addition.** A subsection "Inside the pipeline", with these points paraphrased and quoted:
- **Opposite of a GPU.** "GPU: multiple chips to run a single layer. Cerebras: fraction of a chip to run a single layer."
- **Mapping.** "Model layers are mapped to wafer regions." Each region's size is "determined based on memory and compute requirements". "Model weights **and KV cache** stored locally in the region memory close to the compute."
- **Per token.** "Each wafer region processes 1 token". The work is matrix × vector at local batch 1. Adjacent regions are physically next to each other, so there is "virtually no latency between pipe stages". The "last region output [is] cycled back to generate next token". This is the autoregressive loop the current figure lacks.
- **Many users.** "Single user is using only a fraction of the total memory bandwidth". Additional users occupy the other pipe stages at the same moment, and "every user gets full performance". This turns pipeline depth into concurrency.
- **Prefill.** Prompt tokens are known in advance, so several of one user's prompt tokens can share a stage or occupy several stages at once, using empty stages when few users are active.
- **Fits on one wafer.** Llama 3.1-8B is 16 GB at FP16 and maps onto a single WSE-3.
- **Across wafers.** Llama 3.1-70B is 140 GB and goes onto 4 × WSE-3 (176 GB). The HC24 slide shows layers 1–20, 21–40, 41–60 and 61–80 on the four wafers, which supports the current figure's even split. Cite it, and that resolves accuracy A6. "Keep almost all high communication on wafer … Transfer only activations between wafers."

Diagram or animation, which merges visuals N2: one wafer drawn as a serpentine chain of rectangular regions labelled L1…L20, each region coloured as "weights + KV". A token dot walks the chain, crosses to the next wafer, and returns from L80 to L1 as the next token. A toggle adds users 2, 3 and 4 as dots in other stages.

### D8 [major] Worked example: why the Ethernet hop between wafers barely matters
**What is missing.** The chapter does not say what crosses between wafers, how big it is, or why latency does not dominate.

**Why it matters.** Without it, "four systems over Ethernet" sounds as if it should be slow. The numbers show why it is not, and they set up the CS-4 Direct Wafer Links.

**Source.** HC24 "Naturally scales to multiple wafers": "CS-3 IO is <5us; 4 hops required; <1% impact to latency" and "CS-3 IO is 1.2Tbps; 100Gbps required; <10% of available"; "Using CS-3 low latency RDMA over Ethernet interconnect" [Vendor]. CS4B: Direct Wafer Links "as low as 2 microseconds" [Vendor]. Llama-3-70B hidden size 8192 comes from Meta's public model config [Vendor]. The arithmetic is [Derived].

**Proposed addition.** A callout "Worked example: the inter-wafer budget":
- Per token, the data crossing each wafer boundary is one activation vector: 8192 × 2 B ≈ **16 KB**.
- At 450 tok/s (launch), one token takes 2.2 ms, and four hops at under 5 µs each add 20 µs, about **0.9%**. That matches HC24's "<1%".
- At 2,100 tok/s, 0.48 ms per token, the same 20 µs is about 4%. That is one reason CS-4 cuts the hop to 2 µs.
- Bandwidth: HC24 budgets 100 Gb/s of the 1.2 Tb/s per system, under 10%, because many users and prefill tokens share the link.
- Contrast with GPUs (HC24, citing Databricks): tensor-parallel memory-bandwidth utilisation on Llama-70B batch 1 falls from 60% on 2 H100s to 25% on 8, so 4× the bandwidth buys 1.7× the speed (42% scaling efficiency). Tag this [Vendor citing Indep].

### D9 [major] Worked decode-bandwidth example, plus an SDK experiment that measures it
**What is missing.** The chapter says decode is bandwidth-bound (Ch1) but never does the arithmetic for Cerebras or a GPU. The capacity widget computes capacity only (pedagogy P4, visuals N3).

**Why it matters.** The result is surprising and teaches something: at the published speeds Cerebras uses well under 1% of its headline SRAM bandwidth, so its decode is limited by something other than SRAM bandwidth. HC24 says exactly this ("single user is using only a fraction of the total memory bandwidth").

**Source.** HC24 (21 PB/s; 8×H100 aggregate 26.8 TB/s; DGX-H100 measured <30% bandwidth utilisation, 86 tok/s best on Llama-3.1-70B per Artificial Analysis). Cerebras Oct 2024 blog (2,100 tok/s, 16-bit weights, speculative decoding). SDK `benchmarks/single-tile-matvec` (README + run.py; time = cycles / 850 MHz) [SDK 2.10.1]. My simulator run results are below [Measured].

**Proposed addition.**
(a) A worked paragraph [Derived]:
- Llama-70B at 16-bit reads 140 GB of weights per token.
- One H100 at 3.35 TB/s therefore tops out at about 24 tok/s. Eight H100s (26.8 TB/s) top out at about 190 tok/s, and the best measured is about 86 (HC24).
- Four WSE-3s give 84 PB/s, a ceiling of about 600,000 tok/s. At 2,100 tok/s the wafers are reading weights at only about 0.3 PB/s, roughly 0.35% of the headline. Caveat: speculative decoding changes the bytes read per accepted token.

(b) A short "experiment" box reproducing a measured number with the SDK:
- I ran `single-tile-matvec` (y = A·x, fp32, one N×N tile per PE) on a 2×2 rectangle in the simulator for both `--arch wse2` and `--arch wse3`. Max cycles: N=25 → 778/780; N=50 → 2,707/2,705; N=100 → 10,160/10,154.
- At N=100 each PE reads its 40 KB matrix plus vectors (40,800 B of "relative" traffic) in about 10,160 cycles, so ≈ 4.0 B/cycle/PE of useful weight bytes, and ≈ 11.9 B/cycle/PE of actual SRAM accesses.
- The benchmark's own extrapolation to 750×994 PEs at 850 MHz is **2.5 PB/s relative (weight bytes) and 7.5 PB/s absolute**, with 1.24 PF for fp32 GEMV. This is the same on WSE-2 and WSE-3 because the benchmark is fp32 and gets no benefit from the wider FP16 SIMD.
- Commands: `cslc ./src/layout_matvec.csl --arch wse3 --fabric-dims=9,4 --fabric-offsets=4,1 --params=width:2,height:2,tile_size:100,iters:1 -o out --memcpy --channels=1` then `cs_python ./run.py --name out` (copied to a scratch dir, as the brief requires).
- Lesson for the box: a real GEMV kernel gets roughly 12% of the headline as useful weight bandwidth. Even so, 35 GB per wafer ÷ 2.5 PB/s ≈ 14 µs per wafer per token, or about 56 µs for four wafers, an upper bound near 18,000 tok/s [Derived]. The measured 2,100 tok/s is therefore set by reductions, pipeline synchronisation, attention and KV reads, not by raw SRAM bandwidth.
- Also cross-check the headline: HC22 gives 2 × 64-bit reads + 1 × 64-bit write per cycle per PE = 24 B/cycle, and 850k PEs × 24 B × ~1 GHz ≈ 20 PB/s, which is the WSE-2 headline [Derived].

(c) Extend the capacity widget (visuals N3) with a "decode ceiling" readout, bytes per token ÷ aggregate bandwidth, for WSE-3 at both headline and measured-kernel bandwidth, and for H100/B200.

### D10 [major] Speed results: say *why* each number changed and what configuration produced it
**What is missing.** The speed table lists results with no mechanism or configuration: 450 → 2,100 tok/s, 405B, Kimi. The 405B result (969 tok/s), the most important data point between 70B and 1T, is missing entirely, as are precision and wafer counts.

**Why it matters.** It ties the capacity widget to deployments the learner can check, and it shows that software (kernels, speculative decoding) moved speed 4.7× on the same hardware. That is a key lesson about the system.

**Sources.**
- Cerebras blog, Oct 24 2024 (https://www.cerebras.ai/blog/cerebras-inference-3x-faster) [Vendor]: "We've re-written or optimized the most critical kernels such as MatMul, reduce/broadcast, element wise ops, and activations. Wafer IO has been streamlined to run asynchronously from compute. This release also implements speculative decoding … 20% higher or lower than the 2,100 tokens/sec average is normal. … all models continue to use 16-bit original weights."
- Cerebras blog, Nov 18 2024 (https://www.cerebras.ai/blog/llama-405b-inference) [Vendor citing AA]: Llama 3.1-405B at 969 tok/s with a 1,000-token prompt, 539 tok/s with a 100,000-token prompt, 240 ms TTFT, 128K context, 16-bit weights, $6/$12 per M input/output tokens.
- VentureBeat (May 2026, via search extract; the page returned 429) [Vendor/press]: Kimi K2.6 runs across "approximately 20 CS-3 systems", stored in the model's original 4-bit weights with 16-bit compute; 32B of 1T parameters active per token (MoE).
- Cerebras blog, Aug 27 2026 (https://cerebras.ai/blog/how-cerebras-serves-gpt-5-6-sol-at-up-to-750-tokens-per-second) [Vendor]: GPT-5.6 Sol "partitions it at layer boundaries across multiple CS-3 systems … only activations move between stages", same weights and precision as the standard endpoint.

**Proposed addition.** Add a column, "What made it possible / configuration", and these rows:
- Aug 2024, 70B, 450 tok/s: 4 × CS-3, 16-bit, first implementation "utilized only a fraction of its peak bandwidth, compute, and IO".
- Oct 2024, 70B, 2,100 tok/s: rewritten kernels, async wafer I/O, speculative decoding, still 16-bit.
- Nov 2024, 405B, 969 tok/s: 16-bit, so ≥ 19 wafers from the widget [Derived].
- May 2026, Kimi K2.6: ~20 CS-3, 4-bit weights. Show the widget check: 1T × 0.5 B = 500 GB → ≥ 12 wafers for weights alone, so the ~20 actually used leave room for KV cache and stage balance [Derived].
- Aug 2026, GPT-5.6 Sol: layer-boundary pipelining, as in D7.

This also answers pedagogy P13 (the trillion-parameter result left unexplained against the capacity widget).

### D11 [major] KV-cache arithmetic: what limits users and context on a wafer
**What is missing.** "~36 GB left for KV cache" is never turned into users or tokens. The KV cache is never defined (pedagogy P5), and the "few concurrent sequences" claim (accuracy A8) has no mechanism behind it.

**Why it matters.** This is the real capacity constraint on serving, and it explains the cost-per-token callout.

**Source.** HC24 (KV cache stored in region memory). Llama-3-70B config from Meta's public model card/config [Vendor]: 80 layers, 8 KV heads (GQA), head dim 128. Arithmetic [Derived].

**Proposed addition.**
- A definition sentence: "The KV cache holds each layer's key and value vectors for every earlier token of every active sequence, so attention need not recompute them. It grows with tokens × users."
- Worked example: per token, 80 layers × 8 heads × 128 × 2 (K and V) × 2 B = **327,680 B ≈ 0.31 MiB**. 36 GB ÷ 0.31 MiB ≈ **110,000 tokens of context in total across all users** on the 4-wafer system. That is about 13 users at 8K context, or less than one 128K-context user [Derived].
- Conclusions: this is why Cerebras ran 405B at 128K on a large system, why HC24 lists "KV cache optimizations" among its next techniques, and why CS-4 adds disaggregated prefill (D12).
- Add a fourth slider to the widget, "context tokens × users", that subtracts KV bytes from the reserve. This merges visuals N5's SRAM budget bar.
- Cite HC24's own projection as context: Cerebras expects "20–40x higher throughput" than DGX-H100 at batch up to 32 [Vendor projection].

### D12 [major] CS-4 is in the title but has only one table cell; add how it works
**What is missing.** The only CS-4 detail is "3 × WSE-3T", "750 PF" and "DWL + RoCE". There is nothing on backpacks, power, the mechanism behind the 2× claim, the I/O module, or disaggregated inference.

**Why it matters.** Objective 3 places CS-4 on the timeline. The interesting part is the mechanism: more power → higher clock → faster tokens, plus lower hop latency.

**Sources.** CS4B; HC26B; STH26 [Vendor/press]. MoE expert placement: SemiAnalysis "Cerebras's next-generation CS-4" (paywalled excerpt via search) [Analyst].

**Proposed addition.** A table, "CS-4 / Nexus at a glance", with each row tagged Vendor:

| Topic | Detail |
|---|---|
| Rack | Nexus platform: power at the front, three rear "compute backpacks", each with one WSE-3T, its power conversion, direct liquid cooling, I/O and control. 50% fewer components and 60% more automated manufacturing than CS-3. |
| Power | Up to 30 air-cooled AC/DC PSUs per backpack, up to 277 V AC in and 54.5 V DC out, a 30 A breaker per PSU, 5+1/4+1/3+1/4+2 redundancy, up to six AC feeds from the top of the rack. Conversion about 0.5 mm from the wafer (vs ~50 mm on GPUs). "Twice as much power to the WSE-3 Turbo, enabling higher operating frequencies". Cooling: per-backpack water conditioning, energy meter, dry quick-disconnects, leak sensors. |
| I/O | A new Wafer I/O Module "extends the fabric from the edges of the wafer". 2.4 Tb/s per wafer (double CS-3). RoCE v2 RDMA for heterogeneous connections and Direct Wafer Links for switch-free links "within and across racks". Wafer-to-wafer latency "as low as 2 microseconds" (vs <5 µs on CS-3, HC24). |
| Fabric | 53.5 PB/s on-wafer fabric per WSE-3T. Cerebras compares this with NVL72 Rubin's 260 TB/s NVLink spine of about 5,000 cables. |
| Use | "Native support for disaggregated inference": prefill on AMD Helios or AWS Trainium, then the model state goes to CS-4 for decode. STH: pairing with AMD MI455X. MoE: each expert is kept within one wafer [Analyst, SemiAnalysis]. |
| Claims | 2× CS-3 token speed, 10× tokens/s/W, >4,400 tok/s on gpt-oss-120B, "more than 1,000 tokens per second on models exceeding 10 trillion parameters" ("extrapolation from internal benchmarking"). |

Then one sentence linking back to D8: the drop from 5 µs to 2 µs matters more as tok/s rises.

### D13 [minor] Roadmap: CS-5 numbers, and a correction to CS-6
**What is missing / wrong.** The research report and the CS-4 sentence describe CS-6 as "3D wafer-scale SRAM". Cerebras's own HC2026 blog says CS-6 integrates "wafer-scale SRAM and compute with **3D-stacked DRAM**". STH26 adds: "Cerebras will be employing DRAM for the first time." CS-5 is not mentioned in the chapter at all.

**Source.** HC26B; STH26 [Vendor].

**Proposed addition.** Two timeline entries for objective 3 (pedagogy P9, visuals N4):
- **CS-5 (target 2027):** Nexus plus the next-generation WSE. Up to 10,000 output tok/s/user on gpt-oss-120b and Gemma 4 31B, up to 5,000 tok/s/user and 3M tok/s/MW on multi-trillion-parameter models, "designed to support models with more than 50 trillion parameters".
- **CS-6:** wafer-scale SRAM plus 3D-stacked DRAM, aimed at "an order-of-magnitude smaller system footprint". This is a direct attack on the capacity limit the chapter's widget illustrates.

### D14 [minor] Condor Galaxy build-out beyond CG-3
**What is missing.** The table stops at CG-3.

**Source.** HC24 slide [Vendor, 2024 plan]: "Condor Galaxy 3-5 - 20 Exaflops, Dallas, Texas" and "Condor Galaxy 6-9 - 32 Exaflops, Minneapolis, MN".

**Proposed addition.** Add a "planned (2024)" note to the flagship-cluster row, keeping the existing "status not verified" caveat. It shows that the training-cluster design was meant to replicate in 64-system blocks.

### D15 [minor] What the learner would actually touch for each mode
**What is missing.** The chapter does not say that weight streaming is driven by the Cerebras PyTorch/Model Zoo compiler, not CSL, or that the compiler maps one kernel per layer onto the entire WSE (pedagogy P6).

**Source.** WSDOC ("The compiler maps one kernel (layer) at a time onto the entire WSE, first for the forward pass and then for the backward pass"; `--validate_only`, `--compile_only`). WP p. 19 (Cerebras Graph Compiler) [Vendor].

**Proposed addition.** Two sentences at the end of the training section:
- The cluster stack compiles a PyTorch graph into per-layer kernels and runs the same mapping on every system.
- The CSL SDK the course teaches next is a separate, lower-level path for custom kernels on one wafer. Forward pointer to Ch09.

## Out of scope for this chapter (new-chapter or cross-chapter ideas)

- **Ch02/Ch03 (accuracy, high value): an official clock frequency exists.** HC22's "Core Design" slide gives the WSE-2 core as "1.1GHz clock frequency, 30mW peak power", "228µm x 170µm core area", "110,000 logic standard cells", "48kB high density SRAM". The report says "No official clock frequency exists for any generation", so Ch02/Ch03 should be checked. The same deck also gives:
  - die and wafer: 66 × 154 = 10,156 cores per die, 12 × 7 = 84 dies;
  - SRAM: 8 banks × 6 KB, 32 bits wide, single port, "2 full reads + 1 full write per cycle", 256 B software cache;
  - registers and pipeline: 44 DSRs, 16 GPRs, 6-stage pipeline;
  - fabric: 4.3 TB/s at 0.15 pJ/bit in A100-equivalent area.

  HC24 gives the WSE-3 values: 10.7k cores per die, 84 dies, 512 B cache, 48 DSRs, 16-way 8-bit SIMD, and inter-die I/O at 0.05 pJ/bit vs NVLink serdes 5 pJ/bit.
- **Ch01 / Ch15:** the HC24 GPU tensor-parallel scaling data (60% → 25% bandwidth utilisation from 2 to 8 H100s; 42% scaling efficiency; DGX-H100 <30% utilisation on Llama-70B) and the HC24 throughput-versus-latency chart (GPU batch 1–8 against Cerebras batch 1–32) fit the comparison chapter. The same goes for disaggregated prefill/decode as a heterogeneous design pattern.
- **Ch06:** HC22's "Sparse GEMM is one AXPY per non-zero weight" and its BLAS bytes/FLOP ladder (GEMM 0.005 → AXPY 3 B/FLOP) are a strong DSD/FMAC motivation figure.
- **Ch14:** SwarmX's in-network tree reduction (D5) is a clean contrast with ring all-reduce and NVLink SHARP. Worth a sidebar there.
- **New lab chapter idea, "A toy inference pipeline in CSL":** extend the existing gemv tutorials. Place two or three GEMV "layer regions" side by side on a small rectangle, keep each region's weights resident, pass a 1×H activation vector east between regions on a colour, and loop the last region's output back to the first. Measure cycles per "token" in the simulator. It would make D7 concrete with the same SDK the course already uses. Base it on `benchmarks/single-tile-matvec` and `tutorials/gemv-*`.
- **Research report fix:** update the report's "Chapter 9" section to cite WP, HC22, HC24 and PLDOC, and drop the "not found" statements about layer-pipelined mechanics and inference mapping.
