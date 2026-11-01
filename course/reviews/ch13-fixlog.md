# ch13 fix log

Edited file: `course/13-tenstorrent.html`. Nothing else was edited apart from this log. The page grew from about 12 KB to about 75 KB.

Primary sources re-checked this session:
- tt-isa-documentation: BlackholeA0 README, BlackholeA0 NoC, WormholeB0 RoutingPaths, SrcA/SrcB, Dst, Coprocessor README.
- tt-metal: `blackhole_140_arch.yaml` (fetched; 17×12 grid, tile coordinates, `worker_l1_size` 1572864).
- tt-metal guides and reports: METALIUM_GUIDE, matrix_engine, GEMM_FLOPS, data_formats, tensor_layouts, Saturating_DRAM_bandwidth, LLM report, Programming Mesh of Devices, TT-Fabric, CCL bandwidth.
- tt-metal code and model docs: matmul `mm.cpp`, the in0 sender and receiver readers, the llama3_70b_galaxy README, and the tt-metal README perf table.

## Accuracy (A)

| ID | Status | Note |
|---|---|---|
| A1 | fixed | L1 is now 1536 KiB on BH and 1464 KiB on WH in the lede, figure, product table (new per-core row) and comparison table. Also confirmed by `worker_l1_size` in the SoC yaml. |
| A2 | fixed | 64 B flits, 16 KiB packets and a 1.35 GHz NoC clock on BH, with the WH values (32 B / 8 KiB) in brackets. Per-link rate of about 86 GB/s is tagged derived. |
| A3 | fixed | p150 now reads "4 × 800 GbE QSFP-DD (8 of the die's 14 × 400 GbE tiles wired)". |
| A4 | fixed | Slots are now freed at consumer end. CB size 1/2/4 gives 50/29/29, and 56/40/36 with the jitter pattern. Verified in Playwright. |
| A5 | fixed | CB limit is 32 on WH and 64 on BH (glossary), plus a note that tt-metal plans to replace CBs with dataflow buffers. |
| A6 | fixed | The lede and table both say "not on p100". |
| A7 | fixed | n300 SRAM is now ~192 MB (derived). Per-core values moved to their own row. |
| A8 | fixed | "16 × 100 GbE tiles per die; 2 × QSFP-DD on the card". |
| A9 | fixed | ~12 kW is tagged analyst (Flopper). ~4,000 is replaced by 3,840–4,480 (derived). 512 GB/s now cites the tt-metal CCL report (8 ch × 64 GB/s, device spec), so it is tagged vendor. Galaxy topology is reworded. The caption now reads "Vendor unless tagged otherwise". |
| A10 | fixed | DST capacity is attributed to Wormhole (LLM report / matrix_engine) and explained as half-sync. |
| A11 | fixed | Label is now "RV32IM+". The caption names the BH extensions and 1.35 GHz. |
| A12 | fixed | Tags added to the bullets, both tables, the derived arithmetic and the quiz numbers. |
| A13 | fixed | Perf bullet and the new table now give TP=32, 128-token input, target 80 and v0.65.0-rc7. |

## Pedagogy (P)

| ID | Status | Note |
|---|---|---|
| P1 | fixed | Same fix as A4. Added stage-time sliders, a speedup readout for all three sizes, CB_in/CB_out occupancy strips and red idle bars. |
| P2 | fixed | Real reader/compute/writer code from METALIUM_GUIDE, with each compute line annotated by the core that runs it. Added a "One tile through the core" stepper (BRISC→…→NCRISC with API calls) and byte/flit counts. A CSL side-by-side is given as a concept-mapping table rather than code. |
| P3 | fixed | Glossary callout, a callout on the double meaning of "tile", SrcA/SrcB/Dst/ThCon in the figure, BFP explained (shared 8-bit exponent per 16 values, 1,088 B per tile), fidelity explained, and a software-stack line (Metalium/TT-NN/Forge). |
| P4 | fixed | New section "The chip: a grid on two tori" with an interactive Blackhole floorplan: routing, multicast, congestion presets. Harvesting and the firmware core cut are explained. |
| P5 | fixed | Added a CSL ↔ Metalium mapping table, total-SRAM and off-chip rows (MemoryX mentioned), and a "Same GEMV, two grains" widget. |
| P6 | fixed | Quiz rewritten as 7 reasoning questions: CB deadlock, padding, NoC choice, multicast reuse, Galaxy ceiling (Ch. 8 nuance: four CS-3 systems), and translating CSL to Metalium. |
| P7 | fixed | Units made consistent, p150 column highlighted as "used in the rest of this chapter", separate rows for Ethernet ports and topology, BlockFP8 ≠ FP8 note. |
| P8 | fixed | "Decode ceiling" callout: about 74 GB BFP8 → ~124 tok/s/u on WH Galaxy (measured 72.5 = 58%), and ~220 on BH Galaxy (derived). |
| P9 | fixed | Paragraph explaining why there are three TRISCs (one FPU issue per cycle, pipelining, one source compiled three times, MOP/replay expanders). ThCon added to the figure. |

## Visuals (V)

| ID | Status | Note |
|---|---|---|
| V1 | fixed | Used the reviewer's corrected model with the reviewer's jitter pattern. The axis scales to the slowest CB size so runs are comparable. Tick marks added. |
| V2 | partially | Relies on the shared phone rule (SVG min-width 620px inside a scrolling box). No portrait redesign. No page overflow at 390px, checked in both themes. |
| V3 | fixed | Bars use the blu/acc/grn classes and the text uses default fill, so the timeline follows the theme toggle live. No `#fff` labels remain. Hue-coloured shard tiles use dark `.on-fill` text. |
| V4 | fixed | Anatomy redrawn: router ports on the core boundary, double-headed NoC links, dashed control lines from each RISC-V, data path L1→unpack→SrcA/B→FPU→Dst→pack→L1, SFPU↔Dst, ThCon, legend. |
| V5 | fixed | Removed the redundant Run button. Added an axis, and moved the "done" label above the plot. |
| V6 | fixed | The NoC direction notes now sit beside each router box, and the torus note is in the prose and caption. |

## Depth (D)

| ID | Status | Note |
|---|---|---|
| D1 | fixed | New section "Anatomy of a matmul" (per-core engine rate, matmul-2D split, in0/in1 multicast, variants) and a matmul-grid widget showing DRAM bytes with and without multicast, GEMM_FLOPS ideal cycles and an L1 fit check. |
| D2 | fixed | Routing rules, packets, hop costs, multicast tree and VC class. Sender and receiver semaphore code from tt-metal, including the BH `noc_async_writes_flushed`. Contrast with Cerebras colours. Floorplan widget. |
| D3 | fixed | Five code tabs: reader, compute (per-core annotations), writer, `mm.cpp`, and host `split_work_to_cores`/`SetRuntimeArgs` with the undefined-behaviour warning. SFPU `copy_tile/sin_tile` pattern. CSL mapping table. |
| D4 | fixed | Interleaved/sharded section with a 5-mode widget. The DRAM-sharded decode explanation uses vendor-measured 92% and 82–90% figures. Floorplan presets show the congestion. |
| D5 | fixed | "70B on 32 chips": TG 8×4, links per axis, 2-D fracturing (FF1 [K/4,N/8] with all-reduce on axis 1; FF2 [K/8,N/4] on axis 0), Galaxy widget (block per chip, all-reduce partners, torus wrap, TP32 vs 4×TP8), two-layout table, roofline. |
| D6 | fixed | "Scaling out: from NoC to fabric" covers ERISC firmware, remote NoC ops, Go-Back-N, source routing, bubble flow control, routing planes, scale, and link rates and per-hop latency (CCL). Skipped the router slot counts (8/16) and the 4,352 B payload. |
| D7 | fixed | Peak-formula callout replaces "conflict": 774/664/745, HiFi2/HiFi4, 581 TF measured = 81%, Galaxy 23.8–24.8 PF. States that the WH/GS figures don't fit. |
| D8 | fixed | SrcA/SrcB banks, Dst size and half-sync, tile_regs_* roles, frontends and MOP/replay, all in text and figure. |
| D9 | fixed | 5×7-bit multipliers, mantissa slices, 16/32/48/64 cycles per tile, BFP rounding. No bit-slice widget. |
| D10 | partially | Short bullet on fast dispatch, CQ0/CQ1 events and trace. No timeline diagram. |
| D11 | fixed | Faces, padding example, on-device tilize. Quiz covers padding. The smaller hardware tile shapes are not listed. |
| D12 | fixed | Bullet on causal FlashAttention load balancing (1.6×, vendor-measured). |

## Counts
- Fixed: 38 (A1–A13, P1–P9, V1, V3–V6, D1–D9, D11, D12).
- Partially: 2 (V2, D10).
- Skipped: 0.

## New visuals and widgets
1. **Blackhole floorplan + NoC router.** Real coordinates from the tt-metal SoC descriptor. Choose NoC 0 or 1, unicast or rectangle multicast. Shows hops, cycle and ns estimates, and congestion highlighting, with two DRAM-reader placement presets.
2. **One tile through the core.** An 11-step stepper with Step/Back/Play. Shows the active RISC-V core, the API call, and a BF16/bfp8_b byte and flit toggle.
3. **Circular-buffer timeline, rebuilt.** Correct model, sliders, jitter, occupancy strips, idle bars, and a comparison of all three sizes.
4. **Matmul on the grid.** M/K/N, grid, fidelity and K-step controls, a clickable core, multicast lines, and DRAM-byte, ideal-time and L1-fit readouts.
5. **Interleaved vs sharded.** Five layouts of a 256×256 tensor, coloured by owner.
6. **Galaxy 70B layout.** Per-chip weight block, all-reduce partners, torus wrap links, TP=32 vs 4×TP=8, and derived weight-read and all-reduce times.
7. **Same GEMV, two grains.** p150 vs WSE-3 with an n slider, showing off-chip bytes per token, units used and granule.
8. **Redrawn Tensix anatomy figure.**

Verification:
- Playwright at 1100px and 390px, light and dark: 0 page or console errors, `scrollWidth == innerWidth` in all four, including after the theme toggle.
- Every control was exercised.
- Key figures were screenshotted, inspected, then deleted.

## Left for later / open issues
- **Ch15 (not mine to edit) still has the WH-era values in its Blackhole column:** "1,464 KiB L1" and "32 B flits, ≤ 8 KiB packets". They should be 1,536 KiB and 64 B / 16 KiB. The ch15 Scaling paragraph also says "Ethernet on every die", which should become "on-die Ethernet (not on p100)".
- **Research notes and report:** still carry 1464 KB and 32 B for BH. Their gaps on the CB API names, BFP block size 16 and the BH clock of 1.35 GHz are now resolved.
- **Still unverified (search extracts only):** Grayskull figures, the p150 300 W rating, the 1–2% derating claim, the DeepSeek-R1 tok/s figures and The Register quote. The Blackhole Galaxy's physical mesh shape is inferred only from `MESH_DEVICE=TG` in the demo README.
- **Which 20 Tensix cores the firmware disables:** not documented, so not drawn.
- **Possible future additions:** a portrait phone layout for the large SVGs (V2), a dispatch timeline (D10), a fidelity bit-slice widget (D9), TT-Fabric router buffer details (D6), and the optional ttsim lab (depth "out of scope").
