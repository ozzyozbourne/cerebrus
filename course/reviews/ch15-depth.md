# ch15 · depth review

Summary. Chapter 15 faithfully reproduces the research report's "Chapter 15" section: the architecture table, the programming-model table, the scaling paragraph, the evidence table and the strengths and weaknesses table. It is shallow exactly where a head-to-head synthesis should be deepest. It never runs one workload through all three machines with numbers. It has no cost-per-token or energy-per-token model, even though the inputs are in the sources. Its account of scale-out is one paragraph with no bandwidth figures. Training versus inference gets one clause, and software maturity and programming effort get one table row each. It does not teach the reader how to judge the next claim. Most of this can be fixed from the existing sources with arithmetic tagged `derived`. Every proposed number below cites its source, and the arithmetic was checked in this review.

## Gaps and additions (prioritised)

### D1 [critical] One workload, three machines: 70B decode worked through with numbers
**What is missing.** The chapter says decode is bandwidth-bound and that Cerebras is fast, but it never computes anything. Nothing shows the reader a bandwidth ceiling for each machine and how far measured results sit from it.
**Why it matters.** This is the single most useful synthesis the course can offer. It also gives a surprising result the chapter currently misses: on Cerebras, 70B decode is *not* bandwidth-bound. Its ceiling is about 250× above what is measured, so the limit is the serial pipeline through 80 layers spread over 4 wafers. On GPUs and Tenstorrent, measured results do sit near the bandwidth ceiling.
**Source.** Report ch1 (≈1 FLOP/B at batch 1), ch9 (140 GB FP16, 80 layers over 4 CS-3s, 2,314 tok/s Indep), ch13 (Galaxy Blackhole 1 TB GDDR6 at 16 TB/s, Wormhole Galaxy 72.5 tok/s/user at batch 32), ch14 (H100 3.35 TB/s 80 GB, B200 ~8 TB/s ~180 GB usable); gpu_and_comparison.md §3, §6.
**Proposed addition.** A new section, "One workload, three machines: Llama-70B decode", with a table and a small bar chart on a log axis showing the ceiling against measured. The ceiling formula is per-user tok/s ≤ aggregate weight bandwidth ÷ weight bytes. All values `derived` unless stated:

| Config | Weight bytes | BW used | Ceiling tok/s/user | Measured |
|---|---|---|---|---|
| 1× H100, FP8 (70 GB just fits in 80) | 70 GB | 3.35 TB/s | ≈48 | — |
| 1× B200, FP16 | 140 GB | 8 TB/s | ≈57 (FP8: ≈114) | — |
| 8× B200 TP, FP16 (ignoring comms) | 140 GB | 64 TB/s | ≈457 | — |
| Galaxy Blackhole, FP16 / BFP8 | 140 / ~70 GB | 16 TB/s | ≈114 / ≈229 | Wormhole Galaxy 72.5 `vendor` |
| 4× CS-3 pinned in SRAM | 140 GB | 4×21 PB/s | ≈600,000 | 2,314 `indep` |

Follow it with the key derivation. 1/2,314 tok/s ≈ 432 µs per token ≈ 5.4 µs per layer ≈ 4,600 cycles per layer at the SDK's 850 MHz assumption. The wafer is therefore limited by per-layer latency and the hops between wafers, not by memory. Add a batch slider: GPU per-user speed falls slowly while aggregate throughput rises roughly linearly up to the ridge (≈295 FLOP/B on H100). This links back to ch01's roofline. Caveats to state: the ceilings ignore KV-cache reads, communication and quantisation overhead; the Wormhole measurement is batch 32 on a different chip generation; no H100/B200 per-user measurement exists in the sources.

### D2 [critical] Cost-per-token model with explicit assumptions
**What is missing.** One analyst price row ($0.10–0.25 vs $0.60 per M tokens) and nothing else. The reader cannot see *why* the prices differ or what would change them.
**Why it matters.** "GPUs win on throughput per dollar" is the chapter's main counterweight, but the chapter asserts it without showing it. A transparent model also reveals the biggest open question: how many concurrent streams a Cerebras pipeline serves.
**Source.** gpu_and_comparison.md §7 ($8–12M per 70B instance, unverified Medium; 23 kW per CS-3); tenstorrent.md §6 (Galaxy Blackhole $110k–160k, Wormhole Galaxy $70k JP, QuietBox 2 $9,999); report ch13 (Galaxy ~12 kW); report ch15 ($0.60/M Cerebras price, H100 $0.10–0.25 Analyst).
**Proposed addition.** An interactive calculator: $/M tokens = (capex ÷ amortisation hours + kW × $/kWh) ÷ (aggregate tok/s × 3600 ÷ 10⁶). Inputs have defaults and editable fields, and each carries a tag. Worked examples (`derived`, 4-year amortisation, $0.10/kWh):
- 4× CS-3 at $10M: $285/h capex + $9/h power. At **one** stream of 2,314 tok/s that is ≈ **$35/M tokens**. The published $0.60/M therefore implies roughly 60 concurrent streams per instance, or far lower capex. State plainly that this is an inference about concurrency the sources do not report.
- Wormhole Galaxy at $70k, ~12 kW (power assumed from the Blackhole Galaxy figure), 2,269 tok/s aggregate at batch 32: ≈ $2/h + $1.2/h → ≈ **$0.39/M**.
- H100: use the Analyst $0.10–0.25/M directly. The sources give no H100 capex, so say so.
Close with: "No independent TCO study covers all three (report ch15 gaps)."

### D3 [major] Energy: per token, per FLOP, and the data-movement argument
**What is missing.** The power row lists 23 kW, 300 W and 700 W with no normalisation. Energy per token is mentioned only as "no study exists". Two sourced energy claims are left out: the MD paper's "one to two orders of magnitude better energy efficiency" and CS-4's "up to 10× throughput per watt" (vendor). Also missing is the physical reason, under-1 mm wires between cores.
**Why it matters.** Raw watts mislead, because 23 kW is a whole system with cooling while 700 W is one board. A compute-bound normalisation reverses the intuitive story. Per peak FLOP, the wafer is *less* efficient than GPUs. Its energy advantage, where it exists, comes from avoiding data movement on bandwidth-bound work.
**Source.** gpu_and_comparison.md §6 (MD energy claim), wse_hardware.md §1 and §2 (CS-4 10×/W vendor; <1 mm wires, STH HC34); report ch2 (15.6 PF dense Analyst); ch14 (989 TF BF16 dense, 9 PF FP4 dense).
**Proposed addition.** A short section with two tables, both `derived`:
1. Peak dense TFLOP/s per watt, stating "formats differ; system vs board power": WSE-3 ≈0.68 (FP16, 23 kW system); H100 ≈1.4 (BF16, 700 W board); p150 ≈2.2 (BlockFP8, 300 W card); B200 ≈9 (FP4, ~1 kW).
2. Joules per token for 70B decode: 4× CS-3 at 92 kW ÷ 2,314 tok/s ≈ 40 J/token if there is one stream, divided by N for N concurrent streams; Galaxy ≈ 5 J/token at 12 kW and 2,269 tok/s aggregate (mixing generations, flagged). This shows that concurrency, which is unknown, dominates the answer.
Finish with a one-line takeaway: on compute-bound work, GPUs do more FLOPs per watt; on bandwidth-bound work with resident data, the wafer can win on energy (the MD claim). Neither has been independently measured as tokens per joule.

### D4 [major] Same kernel, three machines: the stencil and a GEMM
**What is missing.** The chapter's "what programming taught us" box quotes the course's own stencil cost (88 fixed cycles) but never sets it against a GPU or Tenstorrent. It also has no compute-bound counterexample.
**Why it matters.** The course's own measurement, extrapolated, reproduces the order of magnitude of the peer-reviewed 179× MD result. That is a strong teaching moment, and it uses the course's own data. A GEMM shows the opposite regime, where the advantage collapses to the ratio of peak FLOPs.
**Source.** src/12 lab: cycles/step ≈ 88 + 2.5·n (`measured` in the simulator, WSE-3); 850 MHz SDK assumption; ch01's 0.5 FLOP/B stencil example; ~46 KB usable per PE (wse_hardware.md §3); report ch2 dense estimates; SDK `benchmarks/gemm-collectives_2d` (P×P SUMMA-style GEMM) and `benchmarks/single-tile-matvec` ("relative vs absolute" bandwidth).
**Proposed addition.**
- Stencil (`derived`): a WSE-3 extrapolation of 900k PEs × n cells ÷ ((88+2.5n)/850 MHz) gives ≈9.6×10¹³ cell-updates/s at n = 16 and ≈3×10¹⁴ for large n. The H100 streaming roofline (8 B per cell-update, no temporal blocking) gives ≈4.2×10¹¹. The ratio is several hundred times, consistent in order with 179× MD. Capacity check: the wafer holds at most ≈900k × 5,750 ≈ 5×10⁹ cells (two f32 arrays in 46 KB); one H100 holds ≈10¹⁰ in 80 GB. Caveats: 1-D vs real 3-D; GPU temporal blocking in the 50 MB L2 narrows the gap; the simulator extrapolation is not a hardware measurement.
- GEMM: compute-bound, so the ceiling is peak dense FLOPs, ≈15.6 PF (WSE-3, Analyst) vs 0.99 PF (H100 BF16) vs ~9 PF (B200 FP4). That is ~16× an H100 at ~33× the power, which ties into D3. Mention that gemm-collectives_2d is the SDK pattern (P steps on a P×P grid with row and column broadcasts), the same structure as Tenstorrent multicast matmul and GPU tiled GEMM.
- Optional: a table of "what limits this kernel on each machine" (stencil: halo latency / NoC+DRAM / HBM; GEMM: SIMD width & 48 KB tile size / FPU & L1 / Tensor Cores).

### D5 [major] Scale-out topologies compared with numbers, and the "bandwidth cliff" ratio
**What is missing.** The Scaling section is prose only, with no link or domain bandwidths, no topology picture and no mapping of parallelism strategies.
**Why it matters.** The most clarifying single number for scale-out is how much bandwidth drops when data leaves the device. That ratio predicts each design's scaling behaviour, and the chapter has all the inputs.
**Source.** report ch13 (14×400 GbE per Blackhole, Galaxy 8×4 mesh, AllGather using 4 and 3 links per axis from the tt-metal LLMs report), ch14 (NVLink 5 1.8 TB/s per GPU, NVL72 ~130 TB/s; Rubin 3 TB/s, ~216 TB/s), ch8 and wse_hardware.md §7 (CS-3 12×100 GbE forum-sourced; WSE-3T 2.4 Tb/s per wafer; on-wafer fabric 214 Pb/s ≈ 27 PB/s), ch9 (SwarmX broadcast and reduce tree, 2,048 CS-3).
**Proposed addition.** A table and a three-panel topology SVG (on-wafer mesh then Ethernet/SwarmX tree; per-die torus then switchless 8×4 Ethernet mesh; NVLink switch domain then IB fat tree):

| | On-device | Off-device per device | Cliff (on ÷ off) |
|---|---|---|---|
| CS-3 | ~27 PB/s fabric | ~150 GB/s (12×100 GbE, forum) | ≈180,000× |
| B200 | ~8 TB/s HBM | 1.8 TB/s NVLink 5 | ≈4.4× |
| Blackhole p150 | ~512 GB/s GDDR6 | ~400 GB/s (4×800G ports; 700 GB/s raw from 14×400G tiles; sources conflict) | ≈1× |

All `derived` from `vendor` inputs. Teaching point: Tenstorrent scale-out costs almost no bandwidth compared with its own DRAM, so it is designed around many chips. The GPU loses ~4× at the NVLink boundary. The wafer has an enormous cliff at its edge, which is why inference pipelines layers across wafers (only activations cross) and training streams weights layer by layer. Add a row listing how each machine applies TP/PP/DP.

### D6 [major] Training vs inference (and prefill vs decode) across the three
**What is missing.** Training appears only as "MemoryX/SwarmX for training (to 2,048 CS-3s)". Nothing compares how each architecture trains, and the prefill/TTFT caveat from the report is dropped.
**Why it matters.** The chapter's verdict is almost entirely about inference decode. A reader could leave thinking it covers training too. The sources say clearly that the evidence is asymmetric: there are no independent multi-system training benchmarks for Cerebras, and Tenstorrent is "inference-first in practice".
**Source.** report ch9 (weight streaming vs pinned inference, inverse placements), gpu_and_comparison.md §5 gaps, §6 (benchlm "won speed, not the shortlist"; fast decode does not shorten TTFT); tenstorrent.md §6 (TT-Blacksmith, no credible training benchmarks); gpu_and_comparison.md §1 (Rubin CPX, a GDDR7 prefill accelerator).
**Proposed addition.** A 3×3 table (rows Training / Prefill / Decode; columns the three vendors) covering where weights and activations live, the limiting resource, and the evidence available. Include: Cerebras training = activations resident, weights streamed, SwarmX reduce, "linear scaling" claimed by the vendor with no independent check. GPU = one hardware for all phases, with NVIDIA now splitting prefill onto Rubin CPX (an interesting convergence on phase-specialised hardware). Tenstorrent = training recipes exist, no benchmarks. Add the sentence the report has and the chapter lacks: "Fast decode does not shorten prefill or time to first token."

### D7 [major] Software ecosystem maturity, with concrete evidence
**What is missing.** Maturity appears as "maturing software" and "proprietary, dominant ecosystem". The sourced evidence of immaturity, and the layers each stack offers, are left out.
**Why it matters.** The decision guide itself says "software maturity for your model" decides real purchases. The chapter should give the reader something to weigh.
**Source.** report ch15 programming table "Higher layers" row (dropped from the chapter: PyTorch/cuDNN; Cerebras ML stack plus research compilers MLIR-stencils and SpaDA; TT-NN/TT-MLIR/TT-Forge); tenstorrent.md §4 (TT-XLA via PJRT, TT-Forge-ONNX single-chip only, TT-Lang early preview); §6 and gpu_and_comparison.md §6–7 (Blackhole QuietBox Llama 70B 14.9 tok/s/user vs Wormhole 15.9, newer chip slower and "under active development"; The Register "software blackhole"; vLLM: none vs a TT fork, partly contradicted); csl_programming.md §3 (WSE-2/WSE-3 portability: queues vs colors, microthread IDs, no color swap on WSE-3, one fabric input per op); pricing anchors ($799 e150, $9,999 QuietBox 2) as an access path.
**Proposed addition.** A "stack ladder" figure: three columns from framework down to device ISA, with each layer marked open, closed or research. Add a short evidence list:
- the Blackhole-vs-Wormhole regression;
- the vLLM status;
- the CSL portability traps;
- how a learner gets access: buy a $799–$9,999 TT board, rent any GPU, or for Cerebras use the free SDK simulator, the inference API or an allocation. Verify the last before stating it; it is not in the sources.

### D8 [major] Programming-effort comparison grounded in the course's own programs
**What is missing.** Effort is implied ("low-level CSL") but not compared. The sources confirm that no independent productivity study exists, and the chapter does not say so.
**Why it matters.** Learners want to know what it costs to write the same thing on each platform. The course has its own data: five programs, their line counts and the bug classes it hit.
**Source.** course/programs (04-heat-stencil: layout.csl 43 + pe_program.csl 111 + run.py 39 + commands.sh 6 lines; 01-saxpy: 14 + 27 + 28); report ch8 (memcpy reserves colors 20–23, local tasks 24/27/28/30/29/31, queues 0–1); csl_programming.md §3 (task ID ranges, 8 queues, 8 microthreads); tenstorrent.md §4 (3 kernels + host, ≤32 CBs, runtime args to every core, even idle ones); gpu_and_comparison.md §2 (occupancy limits); report ch15 gap "no independent productivity study".
**Proposed addition.** A table titled "What you must budget by hand":
- CSL: 24 colors minus 4 for memcpy, data-task IDs bound to 8 queues, 8 microthreads, 48 KB for code and data, routes, a separate layout file;
- Metalium: ≤32 CBs, 5 RISC-Vs, 3 kernels plus host, 1,464 KiB L1, 32×32 tile padding, runtime args per core;
- CUDA: registers per thread and shared memory (≤228 KB per SM) to balance against occupancy; nothing to route.
Add a "files and lines for a 1-D heat stencil" row using the course's real counts for CSL (≈200 lines across 4 files). For CUDA and Metalium, label any figure as `derived` illustrative pseudocode, or omit them. State: "No independent productivity study exists."

### D9 [major] How to evaluate future claims, and open questions
**What is missing.** The chapter shows tags but never teaches the reader how to decode a new headline. Open questions appear only as "no study exists".
**Why it matters.** The numbers will be stale within a year (CS-4, Rubin and Blackhole revisions are already moving). A reusable checklist is the most durable thing the chapter can teach, and the sources are full of concrete traps.
**Source.** report "How to read the numbers" and ch2 (125 PF sparse, never a dense figure); ch14 (1,979 TF is 2:4 sparse; Rubin 22 to 19.2 TB/s revision); ch13 (p150 de-rated 140 to 120 cores, 774 to 664 TF; 745/774 conflict); gpu_and_comparison.md §6 (gpt-oss 3,000 claimed vs ~1,700 measured ≈ 0.57×; MD 179× paper vs 748×/457× later configurations; Gordon Bell finalist, not winner; Tenstorrent "4,000–5,000 tok/s" blog contradicting repo tables); ch2 (SDK-visible 750×994 ≈ 745k positions vs 850k marketed).
**Proposed addition.** A "claim decoder" checklist, which could also be an interactive widget that flags a pasted claim:
- dense or sparse;
- number format;
- chip, board, system or rack;
- per-user or aggregate tok/s;
- batch size and TTFT included;
- quantisation;
- vendor, independent, analyst or peer-reviewed;
- spec date and revision;
- shipping vs announced hardware;
- usable vs marketed units.

Each item gets one worked example from the sources above. Then an "Open questions" list:
- Cerebras concurrency per instance and true cost (from D2);
- independently measured tokens per joule;
- WSE utilisation (the only data point is CS-1 BiCGStab at ~1/3 of peak, which the chapter omits);
- multi-system training efficiency;
- the absence of MLPerf entries;
- CS-4 "4,400 tok/s / 30×" and "10×/W";
- "3D wafer-scale SRAM";
- whether Tenstorrent software closes the gap;
- how many wafers a 1T-parameter model (Kimi K2.6) actually uses. At FP8 that is ≈1 TB ≈ 23 wafers, `derived`, unless MoE or other tricks apply.

### D10 [major] Generation-matched and rack-level comparison
**What is missing.** The comparison pits a 2024 system (CS-3) against a 2022 GPU (H100), with B200 only partly filled (SRAM shown as n/a). There is no rack-to-rack view, and no CS-4 or Rubin, although both are in the sources.
**Why it matters.** Units differ by orders of magnitude (wafer vs card vs GPU). The fair unit for frontier inference is now the rack, and both vendors' 2026 racks are documented.
**Source.** report ch9 (CS-4: 3× WSE-3T, 750 PF sparse, 129.6 PB/s, 7.2 Tb/s I/O, 132 GB SRAM `derived`), ch14 (Rubin NVL72: 288 GB HBM4 per GPU, 19.2 TB/s, ~20.7 TB per rack, 3.6 EF NVFP4), ch13 (Galaxy Blackhole: 32 chips, 6.2 GB SRAM, 1 TB GDDR6, 16 TB/s, 23 PF, ~12 kW).
**Proposed addition.** Add a "Per rack (2026)" toggle to the compare widget, with CS-4, Rubin NVL72 and Galaxy Blackhole. Headline `derived` ratios: CS-4 has ≈94× the memory bandwidth of Rubin NVL72 (129.6 vs ~1.38 PB/s) but ≈1/157 of the capacity (132 GB vs 20.7 TB). That is the capacity-bandwidth trade-off in one sentence, at matched dates.

### D11 [minor] Device-count / capacity calculator
**What is missing.** Only one capacity fact (70B FP16 → 4 CS-3s) appears, in the weaknesses table.
**Why it matters.** Capacity is the wafer's main liability. A calculator makes it tangible across model sizes and precisions, and it feeds D1 and D2.
**Source.** report ch9 and ch15 (70B, 405B arithmetic), ch13 and ch14 (device capacities).
**Proposed addition.** Inputs: parameters (70B, 405B, 1T) × precision (FP16, FP8, FP4) and a KV-cache reserve %. Output: devices needed for WSE-3 (44 GB), p150 (32 GB), Galaxy (1 TB), H100 (80 GB), B200 (~180 GB usable) and NVL72 (13.4 TB). Example: 405B FP16 ≈ 19 wafers vs 5 B200 vs one NVL72 (`derived`). Light overlap with ch08's 405B question; refer back to it.

### D12 [minor] Evidence table and fair reading omit sourced items
**What is missing.** Several items from the report's evidence table are absent:
- CS-1 BiCGStab ≈0.86 PF, ~1/3 of peak, the only utilisation data point;
- GPT-5.6 Sol 750 tok/s (vendor citing AA);
- CS-4 4,400 tok/s (unverified);
- the later MD 748×/457× claims, set against the 179× peer-reviewed figure;
- "Gordon Bell finalist, not winner";
- H100 L2 3.8 TB/s measured by Chips and Cheese, the one independent microbenchmark;
- the instruction to exclude the Tenstorrent "4,000–5,000 tok/s" blog.
**Why it matters.** These are exactly the examples D9 needs, and the utilisation number is the only check on peak FLOPs.
**Source.** report ch15 "Performance evidence".
**Proposed addition.** Add a "Metric" column (per-user tok/s, aggregate, timesteps/s, FLOPS) and these rows to the table, and add the TTFT/prefill sentence to "The fair reading".

### D13 [minor] HPC breadth beyond stencils and MD
**What is missing.** The decision guide mentions only "stencil / particle science".
**Why it matters.** The SDK ships solver and transform benchmarks that show which HPC patterns map onto the fabric. That helps the reader generalise beyond one MD paper.
**Source.** csl_programming.md §9 (benchmarks: conjugate-gradient, preconditioned-CG, bicgstab, cholesky, fft-1d-2d, fft-3d, spmv-hypersparse, power-method, 7pt/25pt stencils); report ch15 (CS-1 BiCGStab); gpu_and_comparison.md §6 (arXiv 2605.07954 stencil work).
**Proposed addition.** One paragraph plus a decision-guide row: "Iterative sparse solvers and FFTs on grids that fit on the wafer: Cerebras (SDK patterns exist); large-memory or irregular HPC: GPU." Tag it `sdk` for the existence of the patterns, not for performance.

### D14 [minor] Decision guide is too coarse
**What is missing.** Four rows; no training row; no rows for availability and procurement ("won speed, not the shortlist"), long context or KV-heavy workloads (capacity), or learning and research access.
**Why it matters.** It is the chapter's practical takeaway.
**Source.** gpu_and_comparison.md §6 (benchlm), tenstorrent.md §6 (price anchors), D6 and D11 above.
**Proposed addition.** Add rows for training at scale (GPU; Cerebras via weight streaming, vendor evidence only), long-context or large-KV serving (GPU, on capacity), and learning a spatial architecture cheaply (Tenstorrent board, or the Cerebras simulator). Add a "why" tooltip per row that links to the D-section with the numbers.

## Out of scope for this chapter (new-chapter or cross-chapter ideas)

- **New chapter recommended: "16 · Same workload, three machines".** D1 (70B decode), D4 (stencil and GEMM) and the D8 code-effort comparison together are too big for ch15, which is already a dense table-driven synthesis. Each needs a widget (batch slider, ceiling-vs-measured bars, stencil per-PE size slider) and side-by-side pseudocode. A dedicated chapter would keep ch15 as the verdict and make chapter 16 the worked proof. If only one new chapter is added, it should be this one. If no new chapter is allowed, put D1 into ch15 as a full section and fold D4 into a shorter "second workload" box.
- **Possible short chapter or appendix: "Economics and energy" (D2 and D3).** This is justified only if the course wants an editable cost/energy calculator with a sensitivity view. The sources are thin (no independent TCO, unverified capex), so a section in ch15 with clear `derived` labels is probably enough. Do not make it a full chapter unless better cost data is found.
- **Appendix: "Reading a benchmark claim" (D9).** Could be a course-wide appendix linked from every chapter's evidence tables, since ch08, ch13 and ch14 all quote vendor numbers.
- **Cross-chapter (ch01).** The report's visual idea of a roofline with H100, B200, Rubin, p150 and WSE-3 ridge points belongs in ch01. ch15's D1 should link back to it rather than redraw it.
- **Cross-chapter (ch08).** The cost-per-token paragraph in ch08 should link forward to D2's model. The concurrency question (D2) belongs in ch08's inference section as an open question.
- **Cross-chapter (ch13 / ch14).** Each should state its own off-device bandwidth number so that D5's cliff table is a recap, not new material.
- **Cross-chapter (ch12).** Lab 3 could add an "extrapolate to the full wafer and compare with an H100 roofline" exercise that matches D4's stencil numbers.
