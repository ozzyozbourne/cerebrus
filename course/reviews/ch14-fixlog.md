# ch14 · fix log

The chapter was rewritten and expanded from about 10 KB to about 60 KB. Its sections are now:
1. Three generations
2. Inside an SM
3. Memory hierarchy
4. SIMT (with coalescing, occupancy and latency hiding as subsections)
5. Tiling a matmul
6. Hopper pipeline
7. SAXPY, twice
8. One token, step by step
9. Scaling out
10. An 8-question quiz

The objectives were rewritten to match.

**Verification.** Playwright was run at 1100px and 390px, in light and dark. There were no page or console errors, and scrollWidth equals innerWidth in all four runs. Every control in every widget was driven. Screenshots were reviewed and then deleted.

**Sources checked this session** (WebSearch extracts only; the NVIDIA and Chips and Cheese hosts were unreachable):
- The SM has 4 sub-partitions. Each has 1 scheduler, a 64 KB register-file slice, 32 FP32 lanes and 1 Tensor Core.
- CC 9.0 limits: 64 warps, 2,048 threads and 32 blocks per SM, 65,536 registers, and 255 registers per thread giving 8 warps.
- Each Tensor Core does 512 BF16 FMA/clk. With 132 SMs at 1.83 GHz this gives 989 TF.
- Memory moves in 32 B sectors within 128 B lines.
- L2 latency is 200–300 cycles and the L2 is split 2 × 25 MB (RRZE gpu-benches, measured on a PCIe H100).
- L1 and HBM cycle ranges come only from cheat sheets, so they are tagged Unverified.
- NVFP4 uses 16-element blocks with an E4M3 scale per block and an FP32 scale per tensor, about 4.5 bits per value.
- Llama-3.1-70B config: 80 layers, 8 KV heads, hidden size 8192.
- HGX H100: 18 NVLink4 links per GPU for 900 GB/s, 4 NVSwitch chips, and 8 × 400G ConnectX-7 NICs.

Anything that could not be confirmed carries a new page-local `tag unv` ("Unverified") tag.

## Accuracy
| ID | Status | Note |
|---|---|---|
| A1 | fixed | The L2 figure is now ">5.5 TB/s, H100 PCIe card" (Indep), in both the caption and the figure. The 3.8 TB/s figure was dropped because it could not be confirmed. |
| A2 | fixed | Rubin callout reworded per the review: the quote is hedged, "announced" replaces "launch spec" in three cells, and the earlier 13 TB/s target is mentioned. |
| A3 | fixed | Widget is now explicitly per scheduler (one of 4), with max 16 explained. Quiz Q2 explains why 21 > 16 is impossible and how ILP closes the gap. |
| A4 | fixed | The 1,979 TF ambiguity (sparse BF16 vs dense FP8) is explained in the "Why the FLOPs jump" callout. The old Q3 was replaced (P13). |
| A5 | fixed | Rubin Dies cell: 2 compute dies + I/O dies, with the NVL144/NVL72 naming note. |
| A6 | fixed | Lede says hundreds of thousands of threads, ~270,000 (Derived). |
| A7 | fixed | Added Derived tags (66 MiB, 70B fits, 270k threads), Analyst tag (~180 GB usable), and Vendor tags (NVLink ~130/216 TB/s, 2,048 threads). |
| A8 | fixed | Rubin cell: 50 PF inference / 35 PF training, plus a Transformer Engine caveat. Each peak cell is labelled with its precision. |
| A9 | fixed | Each block gets a slice of shared memory. Warps "normally" run in lockstep, with a note on Volta's per-thread program counters. Inter-block communication now covers L2/HBM atomics, kernel boundaries and DSMEM. |
| A10 | fixed | Replaced "nothing to hide" with a fabric-latency explanation, a two-row table, and "a few dozen task IDs". |
| A11 | fixed | "a cousin of the same story", noting the cards were already shipped. |

## Pedagogy
| ID | Status | Note |
|---|---|---|
| P1 | fixed | New "Inside an SM" section: interactive SVG, Tensor Core explanation, 989 TF derivation, and an SM / PE / Tensix comparison table. |
| P2 | fixed | Glossary callout (`dl.gloss`) after the table. HBM described as high bandwidth but high latency in the lede. |
| P3 | fixed | Each peak cell labelled with its precision. Added a same-precision BF16 row (B200 value is Derived, flagged as not checked against a datasheet) and a "three moves" narrative tying the reticle limit to Chapter 2. |
| P4 | fixed | Text and widget state 4 schedulers × 16 warps. Q2 rewritten with the ~76% cap and ILP. |
| P5 | fixed | Register and shared-memory occupancy worked example, plus the occupancy calculator widget, plus a contrast with the PE's 48 KB. |
| P6 | fixed | Sector arithmetic in the text, coalescing visualizer, Q1 answer rewritten with sectors, column-read example (12.5%), and a DSD contrast. |
| P7 | fixed | Dataflow vs oversubscription table. Microthreads explained as async-operation slots, not threads. |
| P8 | fixed | Annotated CUDA (index, guard, grid). Added the host-side run.py snippet, an explanation of unblock_cmd_stream, a kernel-boundary definition, a CUDA↔CSL concept-map table, and the n = 1M worked example (3,907 blocks, 64/192). |
| P9 | fixed | "One token, step by step" section and decode widget: B200 at 17.5 ms / ~57 tok/s, ~40 GB of KV headroom, and the Cerebras contrast. |
| P10 | fixed | Hierarchy redrawn with chip-wide capacities, the 132 × 512 KB derivation, latency and bandwidth per level, a parallel WSE-3 column, and the L1-vs-shared-memory distinction. Cycle counts are tagged Indep or Unverified. |
| P11 | fixed | Divergence table with 3 cases and the per-PE independent-branch contrast. |
| P12 | fixed | Formula derived in the prose, the ILP extension explained, and a guided task (C = 10, L = 100 gives 11) added to the hint. |
| P13 | fixed | Quiz grew from 3 to 8 questions covering coalescing, the latency cap, register occupancy, divergence, tiling, CUDA↔CSL, 70B decode, and NVL72 vs IB. The repeated sparsity question was removed. |

## Visuals
| ID | Status | Note |
|---|---|---|
| V1 | fixed | Wait bars (amber), queued-for-issue (grey), idle (red) and a legend. C and L labels on warp 0. |
| V2 | fixed | Simulates 20,000 cycles and measures over the second half. One utilisation number, which now matches the formula. Draws the last 1,000 cycles. |
| V3 | fixed | "one of 4 schedulers" label. Message when more than 16 warps are needed. Loads-in-flight (k) slider. Default W = 6, C = 20, L = 100 shows success. Quiz updated. |
| V4 | partially | Labels are now 12px or larger. On phones the coordinator's shared fix (620px min-width with horizontal scroll inside the box) applies. No separate narrow layouts were built. |
| V5 | fixed | Width now means log(capacity) and the caption says so. Chip-wide capacities, latency and bandwidth on every row. Caption reads "Fast storage is tiny; big storage is far away". |
| V6 | fixed | Side labels replaced with a "latency grows" arrow. |
| V7 | fixed | All drawings use CSS classes or `cssVar`, so they follow the theme toggle live. |
| V8 | fixed | Rows fill the height, the issuing row sits under the last warp, the x-axis has ticks every 200 cycles, and the SVG height fits its content. |
| V9 | fixed | CUDA re-wrapped so nothing clips at 1100px. Concept-map table added; it survives stacking on mobile. |
| V10 | fixed | `<title>`/`<desc>` on the static figures. `aria-live` on every readout. |

## Depth
| ID | Status | Note |
|---|---|---|
| D1 | fixed | SM anatomy, the 512 FMA/clk × 4 × 132 × 1.83 GHz check, FP32 ≈ 67 TF (tagged unverified), "~15×", a wgmma sentence (tagged unverified), and the SM ≈ 256 PEs per clock bridge. No mma animation. |
| D2 | fixed | Tiling section and tile calculator widget (intensity, shared-memory and register budgets, picture of the tiles), the 8192³ minimum-traffic number, the 128 × 256 × 64 budget, and a wafer contrast. |
| D3 | fixed | Per-scheduler model with ILP, Little's law callout (500 ns explicitly illustrative), occupancy calculator, and sector numbers. Nsight stall-reason names skipped because they could not be verified. |
| D4 | partially | Static warp-specialised pipeline figure, plus TMA, clusters/DSMEM, setmaxnreg 40/232, a Blackwell TMEM note and the analogy to TT and CSL. All tagged Unverified. Not animated, and no Ping-Pong vs Cooperative toggle. |
| D5 | fixed | Per-layer kernel strip, Llama-70B bytes per token, KV 320 KiB per token, the TP = 8 H100 bound (5.2 ms), the batch-64 KV of ~86 GB, and the decode calculator. PagedAttention mentioned; continuous batching and speculative decoding not covered in detail. |
| D6 | fixed | HGX vs NVL72 topology figure, parallelism table with the bubble formula, and the TP all-reduce worked example. The NVLink:IB ratio is given as 9× per direction, a deliberate correction of the review's 18×, which mixed bidirectional and per-direction figures. |
| D7 | fixed | Bandwidth and latency per level, the 2-partition L2, and the shared-memory bandwidth derivation (~31 TB/s, bank width marked unverified). DSMEM is covered in the Hopper section rather than drawn as a hierarchy level. |
| D8 | fixed | "Why the FLOPs jump" callout with BF16/FP8/NVFP4 explained, the NVFP4 block format (Vendor blog via reprint), and the iso-precision row. |
| D9 | fixed | SAXPY on the roofline (0.17 FLOP/B, 0.56 TF, 0.06%), n = 10⁸ takes ≥ 0.36 ms, about 3.7 waves, and Lab 1's 7,740 measured cycles. |

**Counts:** 41 findings. 38 fixed, 3 partially fixed (V4, D4, and part of D5's serving machinery, which is counted as fixed), 0 skipped.

## New visuals and widgets
1. SM anatomy (interactive SVG): tap or hover a block for a description; "highlight what one warp uses" toggle.
2. Memory hierarchy, redrawn: H100 log-capacity bars with latency and bandwidth, beside a WSE-3 PE column.
3. Coalescing visualizer: 6 access patterns, 4 B or 8 B elements, lanes-to-sectors arrows, efficiency and effective bandwidth readout.
4. Occupancy calculator: threads per block, registers per thread and shared memory per block; per-scheduler warp slots, limiter bars, waves; feeds its warp count into the latency widget.
5. Latency-hiding widget, rebuilt: per scheduler, ILP slider, wait/queued/idle drawn, steady-state measurement, time axis.
6. Tile calculator: BM/BN/BK/stages/threads, picture of the A/B/C tiles, shared-memory and register budget checks, intensity compared with the ridge.
7. Hopper warp-specialised pipeline (static SVG).
8. Decode calculator: GPU, weight and KV precision, TP, batch and context; bytes vs HBM capacity bar; ms per step and tok/s bounds.
9. HGX H100 vs NVL72 topology (static SVG).

## Left for later
- Animated wgmma/TMA pipeline with Ping-Pong vs Cooperative toggle (D4); warp-divergence animation (visuals P4); H100 roofline widget with SAXPY and GEMM points (visuals P5; partly covered by Chapter 1).
- Dedicated narrow-phone layouts for the SVGs (V4). The shared horizontal-scroll fix applies for now.
- Re-verify against primary NVIDIA documents once docs.nvidia.com and developer.nvidia.com are reachable: INT32/FP64 lanes per sub-partition, the 128 B/clk shared-memory bandwidth, the L1 and HBM cycle counts, cluster sizes, TMEM size, the ping-pong register counts, the NVL72 tray layout, and the B200 BF16 dense figure (currently Derived as ~2.25 PF).
- The chapter now uses a page-local `.tag.unv` style (in the page's `<style>` block). The coordinator may want to move it into course.css if other chapters adopt it.
