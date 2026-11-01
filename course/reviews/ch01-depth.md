# ch01 · depth review

Summary: Chapter 1 has the right single idea (ridge point, decode at about 1 FLOP/B). As a technical treatment it is thin. It is about 16 KB of HTML with one widget, and almost every mechanism is asserted rather than derived. The biggest gaps are these. (1) No roofline per memory level with real numbers, so the learner never sees the wall move to a different level. On the wafer it moves to the fabric and the wafer edge. (2) No bandwidth-to-tokens/s bound that is checked against the measured Cerebras, GPU and Tenstorrent numbers that the research already holds. (3) No mechanism for why batch 64 gives about 50–100 FLOP/B rather than 64: the GEMM intensity formula and the KV cache are missing. (4) The 21 PB/s and about 15.6 PF wafer figures are never built up from per-PE quantities, although the notes and an SDK benchmark make that easy. This review also ran that benchmark (single-tile matvec on the SDK 2.10.1 simulator, WSE-3) to get measured per-PE numbers a fixer can use as they are. The pedagogy review (ch01-pedagogy.md P1, P3, P4, P9, P11, P12) already covers some of the same ground at the level of concepts. The proposals below add the quantitative content and say where they overlap.

## Gaps and additions (prioritised)

### D1 [critical] One roofline per memory level: a table that shows where the wall moves
- **What is missing:** The chapter computes one ridge point (H100 HBM) and plots the WSE-3 against aggregate SRAM. It never lists ridge points for each memory level of each chip, so the central internal fact goes unstated: every architecture has a wall somewhere. On the wafer it sits at the PE-to-PE fabric and at the wafer edge, not at SRAM. Pedagogy P1 asks for a single sentence on this. This item supplies the numbers.
- **Why it matters:** This table connects Chapter 1 to Chapter 4 (fabric), Chapter 7 (host I/O) and Chapter 8 (weight streaming versus pinned inference). Without it, "Cerebras removes the memory wall" reads as literally true.
- **Source:** Report Ch.1 (H100 295, WSE-3 21 PB/s), Ch.14 (H100 L2 ~3.8 TB/s measured by Chips and Cheese [Indep]); `wse_hardware.md` §1 line 25 (fabric 214 Pb/s ≈ 27 PB/s), line 27 (15.6 PF dense analyst estimate), §7 lines 164/167/174 (12 × 100 GbE ≈ 1.2 Tb/s per CS-3; SDK single host link ~16 × 7 Gb/s ≈ 14 GB/s); ch01-accuracy "Not verifiable" (H100 smem ≈ 33 TB/s rough derivation); `tenstorrent.md` §1 line 32 (p150 664 TF BlockFP8, 512 GB/s).
- **Proposed addition:** A new subsection "A roofline for every level" placed straight after the widget, with this table (every ratio tagged Derived):

  | Chip · level | Bandwidth | Peak used | Ridge (FLOP/B) | What lives there |
  |---|---|---|---|---|
  | H100 · HBM3 | 3.35 TB/s [Vendor] | 989 TF BF16 dense | ≈ 295 | 80 GB: weights, KV |
  | H100 · L2 | ≈ 3.8 TB/s read [Indep] | 989 TF | ≈ 260 | 50 MB |
  | H100 · shared mem/L1 (all SMs) | ≈ 33 TB/s [Derived: 132 × 128 B/clk × ~1.98 GHz] | 989 TF | ≈ 30 | ~33 MB (228 KB × 132 usable smem) |
  | Blackhole p150 · GDDR6 | 512 GB/s [Vendor/3rd party] | 664 TF BlockFP8 | ≈ 1,300 | 32 GB |
  | WSE-3 · own-PE SRAM (sum) | 21 PB/s [Vendor] | ≈ 15.6 PF FP16 [Analyst] | ≈ 0.74 | 44 GB, 48 KB per PE |
  | WSE-3 · fabric (sum of all links) | 214 Pb/s ≈ 27 PB/s [Vendor] | ≈ 15.6 PF | ≈ 0.6 | data in flight between PEs |
  | CS-3 · off-wafer Ethernet | 12 × 100 GbE ≈ 150 GB/s [Vendor, forum] | ≈ 15.6 PF | ≈ 100,000 | MemoryX / host |
  | SDK host link (memcpy, 16 ch.) | ≈ 14 GB/s [SDK 2.10.1, Derived] | — | — | loading 44 GB takes ≈ 3 s |

  Follow-up paragraph (draft): "Read the table from top to bottom for each chip. On a GPU the levels close to the math are fast but tiny, and the level that is big enough for a 70B model (HBM) has a ridge of about 300. On the wafer the level that holds the weights is the fast one, so decode can run near the top row. But the wall has not gone away. It has moved. Data a PE does not own arrives over the fabric, whose total bandwidth is about the same as the SRAM's but which only reaches neighbours one hop per cycle. Data that is not on the wafer at all arrives through the wafer edge, which has a ridge of about 100,000 FLOP/B. That is why Cerebras pins inference weights in SRAM across several wafers and streams weights for training only when each weight is reused across a large batch (Chapter 8)."
  Widget change (complements pedagogy P1.3): add a second `<select id="roof-level">` that switches each chip's bandwidth between its levels using the rows above. The readout should name the level.

### D2 [critical] Decode-speed bound calculator, checked against measured tokens/s
- **What is missing:** The figure caption says single-user tok/s "is set by memory bandwidth", but the chapter never computes the bound or compares it with real numbers. Pedagogy P4 proposes one 8B/H100 sentence. The deeper lesson is missing: on GPUs and Tenstorrent the bound roughly predicts measured speed, while on Cerebras the memory bound is about 300× above the measured speed. So once memory is fixed, something else limits decode (layer-to-layer latency, the pipeline across wafers, inter-wafer links).
- **Why it matters:** This explains the one independently confirmed Cerebras advantage (per-user tok/s) mechanistically. It also shows that the next bottleneck is latency and communication, which is the subject of Part II.
- **Source:** Report Ch.9 (Llama 3.1-70B ≈ 140 GB, 4 × CS-3 over Ethernet, 450 → 2,100 tok/s [Vendor]; 2,314 tok/s and 170 ms TTFT [Indep, AA]); report Ch.15 performance table (Wormhole Galaxy 72.5 tok/s/user at batch 32 [Vendor]; Kimi K2.6 981 tok/s, 6.7× fastest GPU cloud [Indep]); `gpu_and_comparison.md` §5 lines 159–164; `tenstorrent.md` line 163 (Wormhole decode "bound by time to read model weights from DRAM").
- **Proposed addition:**
  1. A worked table (Derived). Bound = aggregate weight bandwidth ÷ weight bytes, for one user (batch 1), 70B model:

     | System | Weights fit? | Bandwidth that holds weights | Bound (tok/s) | Measured or claimed |
     |---|---|---|---|---|
     | 2 × H100, FP16 (tensor parallel) | 140 GB in 160 GB | 6.7 TB/s | ≈ 48 | — (sources give GPU-cloud speeds only as ratios) |
     | 1 × B200, FP8 | 70 GB in ~180 GB | 8 TB/s | ≈ 114 | — |
     | Wormhole Galaxy (32 chips), BFP8 | yes | 32 × 288 GB/s ≈ 9.2 TB/s | ≈ 130 | 72.5 tok/s/user at batch 32 [Vendor] |
     | 4 × CS-3, FP16 | 140 GB in 176 GB | 4 × 21 PB/s = 84 PB/s | ≈ 600,000 | 2,100 [Vendor] / 2,314 [Indep] |

     (Wormhole per-chip bandwidth = n300 576 GB/s ÷ 2 chips, `tenstorrent.md` line 20. Note that the Galaxy figure is at batch 32, so the comparison is approximate.)
  2. A paragraph (draft): "For the GPU and Tenstorrent rows the bound lands within a factor of about 2 of real speeds, so bandwidth really is the limit. For the wafer the bound is about 300× above the measured speed. Compute is not the limit either: 140 GFLOP per token against 4 × 15.6 PF gives about 450,000 tok/s. With weights in SRAM, decode is limited by something the roofline does not model. Each token must pass through 80 layers in sequence, spread over four wafers joined by Ethernet, and each layer's partial sums must be reduced across many PEs over the fabric. Single-stream decode on the wafer is a latency problem, not a bandwidth problem. Chapters 4 and 5 show what that latency is made of." Add a sentence saying the sources do not break down Cerebras's per-token latency, so this explanation is a Derived inference.
  3. A widget, "Decode speed bounds". Inputs: parameters (B), bytes/weight (2, 1, 0.5), batch, context length, chip (H100, B200, p150, n300, CS-3) and count. Outputs: weight bytes, whether it fits (capacity × count, minus KV), intensity (see D3), memory-bound tok/s per user, compute-bound tok/s, and which one binds. Each output carries a Derived tag. Use the existing `.widget` and `.readout` patterns from the roofline widget.

### D3 [major] Why batching raises intensity, and why it stops: GEMM intensity and the KV cache
- **What is missing:** "Intensity rises roughly in proportion to batch" and "batch 64 only reaches 50–100" are both asserted. The chapter does not give the formula, and it does not say why the result is not 64. The KV cache is never mentioned.
- **Why it matters:** This is the internal mechanism of the whole GPU strategy (batching). It also explains why GPU per-user speed drops at large batch and long context, which is exactly where the wafer's capacity is the constraint.
- **Source:** `gpu_and_comparison.md` §3 line 74 ("for a linear layer, intensity is roughly M, the number of concurrent sequences"; batch 64 → 50–100). Model shape for the worked example: Llama-3-70B public config (80 layers, 8 KV heads, head dim 128, hidden 8192). This is not in the research files, so the fixer should tag the result Derived and say "assumes Llama-3-70B shapes".
- **Proposed addition:** A boxed derivation after the decode paragraph:
  "A linear layer multiplies a *d* × *d* weight matrix by *B* input vectors. FLOPs = 2·B·d². Bytes moved at FP16 = 2·d² (weights) + 2·2·B·d (inputs and outputs). Intensity = B·d² / (d² + 2B·d) ≈ B when B ≪ d. For d = 8192 and B = 64 that is 63.0, so the weight matrix alone gives almost exactly 64. Attention adds the KV cache, which every sequence reads in full on every step and which batching does not share. For a Llama-3-70B-shaped model the cache is 80 layers × 8 heads × 128 × 2 (K and V) × 2 B ≈ 0.33 MB per token per sequence. At a 2,000-token context that is ≈ 0.65 GB per sequence, or ≈ 42 GB for batch 64. Step intensity ≈ (64 × 140 GFLOP) ÷ (140 GB + 42 GB) ≈ 49 FLOP/B. At 8k context it drops to ≈ 30. Batching helps until the KV cache is as large as the weights. After that, extra batch buys almost nothing." Optionally add a small inline chart of intensity against batch (1–256) for contexts of 2k, 8k and 32k, drawn with the existing `el()` SVG helper.

### D4 [major] Build the wafer's headline numbers up from one PE
- **What is missing:** 21 PB/s, 44 GB and the ~15.6 PF estimate appear as wafer totals with no per-PE breakdown. The chapter never shows that the WSE-3's ridge (~0.6–0.74) is the ridge of one PE, repeated 900,000 times.
- **Why it matters:** It makes "aggregate" concrete and introduces the PE's real limits (8 banks, 8-wide FP16) that Chapter 3 then explains. It also shows the learner that the dense FLOP number depends on an unconfirmed clock.
- **Source:** `wse_hardware.md` §1 Inferences line 40 (21 PB/s ÷ 900k ≈ 23 GB/s per core ≈ 6 × 32-bit accesses per cycle at ~1 GHz); §3 Takeaway (8 single-ported 6 KB banks, 32-bit interleave; 8-wide FP16 on WSE-3) and Inferences line 92 (900k × 16 FLOP/cycle × ~1 GHz ≈ 14–15 PF); §1 line 21 and Gaps line 45 (the SDK assumes 850 MHz; no official clock).
- **Proposed addition:** A short table, "One PE, then 900,000 of them" (Derived unless marked):

  | Quantity | One WSE-3 PE | × 900,000 |
  |---|---|---|
  | SRAM | 48 KB [Vendor] | 44 GB [Vendor] |
  | SRAM ports | 8 banks × 4 B = 32 B/cycle max | — |
  | SRAM bandwidth (vendor total ÷ cores) | ≈ 23 GB/s ≈ 27 B/cycle at 850 MHz | 21 PB/s [Vendor] |
  | FP16 FMA | 8 per cycle = 16 FLOP/cycle [Vendor SIMD width] | ≈ 12–15 PF at 0.85–1 GHz (cf. 15.6 PF [Analyst]) |
  | Ridge | 16 ÷ 27 ≈ 0.6 FLOP/B | same |

  Add one sentence: "No clock speed has been published. The SDK's own benchmarks assume 850 MHz <span class="tag sdk">SDK 2.10.1</span>, so every dense-FLOP figure for the wafer is an estimate." Cross-reference Chapter 3 for the banks.

### D5 [major] Experiment: measure one PE's roofline on the simulator (single-tile matvec)
- **What is missing:** No figure in Chapter 1 is Measured, yet the SDK ships a benchmark that reports FLOPs and memory bandwidth per PE. Chapter 3 mentions this benchmark in one sentence but gives no numbers.
- **Why it matters:** It turns the chapter's central claim (every byte is one cycle from the math, so even ~0.2 FLOP/B kernels run at peak) into an observation the learner can reproduce.
- **Source:** `benchmarks/single-tile-matvec/` (README.rst; `run.py` lines ~196–225 define "relative" bytes as 4N²+8N and "absolute" bytes as 12N²+4N, with FLOPs = 2N²−N; `src/pe_matvec.csl` does one `@fmacs` per x element via `@map`). This reviewer ran it on 2026-11-01 with `cslc ./src/layout_matvec.csl --arch wse3 --fabric-dims=8,3 --fabric-offsets=4,1 --params=width:1,height:1,tile_size:N,iters:1 -o outN --memcpy --channels=1` followed by `cs_python ./run.py --name outN --verify` (SUCCESS for N=25 and N=50). Results [Measured, SDK 2.10.1 simulator, WSE-3, fp32]:

  | N | cycles | FLOP | absolute bytes | FLOP/cycle | bytes/cycle | absolute intensity |
  |---|---|---|---|---|---|---|
  | 25 | 780 | 1,225 | 7,600 | 1.57 | 9.7 | 0.16 |
  | 50 | 2,705 | 4,950 | 30,200 | 1.83 | 11.2 | 0.16 |
  | 100 | 10,154 | 19,900 | 120,400 | 1.96 | 11.9 | 0.17 |

  The benchmark's own scaling to a 750 × 994 rectangle at 850 MHz (N=100) printed 7.5 PB/s absolute, 2.5 PB/s relative and 1.24 PFLOP/s fp32. Note that the N=100 tile uses ≈ 42 KB of the 48 KB SRAM (A is 100 × 104 floats, padded), so this kernel also shows the capacity limit.
- **Proposed addition:** A callout, "Measured: one PE's roofline". Draft: "A matrix-vector product in fp32 does 2 FLOPs per 12 bytes of SRAM traffic (read A, read y, write y). That is about 0.17 FLOP/byte, 1,700× below an H100's HBM ridge. On one simulated WSE-3 PE it still reaches about 2 FLOP/cycle, which is one fp32 multiply-add per cycle and the PE's fp32 peak, while moving about 12 bytes/cycle out of a possible 32. On a GPU the same kernel run from HBM would reach about 0.17 × 3.35 TB/s ≈ 0.56 TFLOP/s. The benchmark reports two bandwidths. 'Relative' counts the bytes a cached machine would move. 'Absolute' counts what the SRAM really served, about 3× more, because y is re-read and re-written for every column. There is no cache to absorb that reuse, and the SRAM does not need one." Optionally add a "Measured" preset to the roofline widget that places this kernel at 0.17 FLOP/B. Tag the per-PE fp32 peak of ~2 FLOP/cycle as Measured/Derived. The notes say the fp32 SIMD width is unconfirmed (`wse_hardware.md` §3 Gaps).

### D6 [major] The wall over generations, with the format effect separated out
- **What is missing:** "FLOPs grow much faster" is not quantified (pedagogy P11 covers Rubin only). There is no table across vendors and generations, and the chapter never separates the two ways vendors raise intensity: smaller number formats and more bandwidth.
- **Why it matters:** It shows that the problem is structural and getting worse, and that lower precision is a genuine bandwidth mechanism. Tenstorrent's BFP8/BFP4 weights and Cerebras's on-wafer capacity limit both depend on bytes per weight.
- **Source:** Report Ch.14 table (H100 989 TF/3.35 TB/s; B200 9 PF FP4 dense/8 TB/s; Rubin 50 PF NVFP4/19.2 TB/s); `tenstorrent.md` lines 20, 32 (n300 466 TF FP8/576 GB/s; p150 664 TF/512 GB/s), line 163 (decode bound by DRAM, "why BFP8/BFP4 weights matter"); `wse_hardware.md` lines 19, 27, 34 (WSE-2 ~7.5 PF dense analyst, 20 PB/s; WSE-3 15.6 PF, 21 PB/s; WSE-3T ~25 PF dense disputed, 43.2 PB/s).
- **Proposed addition:** A table, "Ridge points by generation" (Derived ratios), with columns chip, format, peak, bandwidth, ridge, and decode intensity at that format for batch 1:
  - H100: BF16, 989 TF, 3.35 TB/s → 295, decode 1
  - B200: FP4 dense, 9 PF, 8 TB/s → 1,125, decode 4
  - Rubin: NVFP4, 50 PF (dense or sparse not stated), 19.2 TB/s → ~2,600, decode 4
  - n300: FP8, 466 TF, 576 GB/s → ~810, decode 2
  - p150: BlockFP8, 664 TF, 512 GB/s → ~1,300, decode ~2
  - WSE-2: FP16, ~7.5 PF [Analyst], 20 PB/s → ~0.4, decode 1
  - WSE-3: FP16, ~15.6 PF [Analyst], 21 PB/s → ~0.74, decode 1
  - WSE-3T: FP16, ~25 PF [Analyst, disputed], 43.2 PB/s → ~0.6, decode 1

  Follow with one sentence: "Halving bytes per weight doubles decode intensity, which is why every vendor pushes FP8 and FP4. But each generation's ridge rises faster than that, so the gap between decode and the ridge keeps widening on HBM and GDDR machines." The roofline widget should also gain a "bytes per weight" control that shifts the presets (pedagogy P8).

### D7 [minor] Capacity at speed: how many devices a 70B model needs, and what it costs to fill them
- **What is missing:** Pedagogy P3 names the capacity problem. The numbers are still missing: devices needed per architecture, and how long the host takes to fill the wafer.
- **Source:** Report Ch.15 Architecture ("70B FP16 fits on one B200 or two H100s, but needs four CS-3"; Galaxy Blackhole 6.2 GB SRAM + 1 TB GDDR6); report Ch.9 (176 GB − 140 GB ≈ 36 GB left for KV and activations; 405B needs ≥ 19 wafers at 16-bit); `wse_hardware.md` line 174 (filling 44 GB over the SDK host link takes ≈ 3 s).
- **Proposed addition:** A small bar figure or table, "Devices to hold 140 GB of weights": H100 2, B200 1, p150 5 (GDDR) or ~1,000 cores' worth of SRAM, Galaxy Blackhole 1 (GDDR), CS-3 4 (SRAM). Add: "Loading one wafer's 44 GB through the SDK host path at ~14 GB/s takes about 3 seconds, which is why inference keeps weights resident rather than reloading them."

### D8 [minor] Prefill is the other half: where the wafer's advantage shrinks
- **What is missing:** The chapter shows that prefill is compute-bound but does not draw the consequence: on the flat part of the roofline the comparison becomes raw FLOPs (and FLOPs per dollar or watt), and fast decode does not shorten time-to-first-token.
- **Source:** `gpu_and_comparison.md` §5 line 164 ("fast decode does not shorten time-to-first-token or prefill"; "won speed, not the shortlist"); line 162 (price at batch: $0.60/M tokens versus $0.10–0.25/M on H100 at large batch); report Ch.9 (170 ms TTFT [Indep]).
- **Proposed addition:** Two sentences after the decode/prefill figure: "On the flat part of the roofline every chip runs at peak, so the comparison is FLOPs per dollar and per watt. Dense WSE-3 is estimated at about 16× an H100 <span class="tag analyst">Analyst</span>, but a CS-3 system draws about 23 kW <span class="tag vendor">Vendor</span>. That is why Cerebras's independently measured advantage is tokens per second for one user, not cost per token at high batch (Chapter 15)."

### D9 [minor] Latency hiding versus bandwidth: Little's law
- **What is missing:** The GPU row says "hides latency with thousands of threads", but the chapter never gives the mechanism. Pedagogy P12 asks for a qualitative sentence. The quantitative form is Little's law: bytes in flight = bandwidth × latency.
- **Source:** Report Ch.14 (occupancy hides HBM latency; 2,048 threads per SM). HBM latency is **not** in the research files, so use a symbolic or clearly hypothetical value.
- **Proposed addition:** A sentence plus a one-line formula: "To keep 3.35 TB/s busy with a memory latency of *L*, the GPU must have 3.35 TB/s × *L* bytes in flight (for example, ≈ 2 MB at a hypothetical 600 ns). That is why it needs thousands of resident threads. On the wafer the SRAM answers in one cycle, so one PE needs only a few bytes in flight, and the latency to hide is fabric latency (about 1 cycle per hop plus about 2 cycles on and off the ramp, Chapter 4)." Mark the 600 ns as illustrative, or find a source for it.

## Out of scope for this chapter (new-chapter or cross-chapter ideas)
- **Chapter 3 (PE):** The measured matvec moves ~12 B/cycle at fp32 1-wide. An 8-wide FP16 `@fmach` with all three operands in SRAM would need 48 B/cycle, which is more than the 32 B/cycle that 8 banks × 4 B can supply. Chapter 3 should explain how full-width FP16 is fed (an operand from the fabric, registers, or the 512 B cache?). The research does not answer this, so it is a candidate SDK experiment: time `@fmach` with memory-only operands against one fabric operand on the simulator.
- **Chapter 3 or 12:** Run single-tile-matvec with `--arch wse2` against `--arch wse3`, and sweep N up to the 48 KB limit, as a Measured lab extension. `sweep.py` already exists in the benchmark.
- **Chapter 4:** The fabric line in the D1 table (27 PB/s summed, but only to neighbours) deserves its own "fabric roofline" for a stencil: bytes exchanged per PE per iteration against local FLOPs.
- **Chapter 8:** Weight-streaming intensity. A training batch reuses each streamed weight across the whole batch, so it can sit above the ~100,000 FLOP/B off-wafer ridge from D1. Make that arithmetic explicit there.
- **Chapter 15:** Reuse the D2 bound-versus-measured table as the head-to-head "who is limited by what" summary.
- **Possible new short appendix:** "Roofline arithmetic cheat sheet": GEMM/GEMV intensity, KV-cache bytes per token, Little's law, and tokens/s bounds, all with worked numbers. Several chapters could link to it.
