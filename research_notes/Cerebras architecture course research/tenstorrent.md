# Tenstorrent AI Accelerator Architecture and Programming Model (for comparison with the Cerebras WSE)

> **Errata (2026-11-02).** Some figures below have been superseded by measurements in the course. See the "Errata / superseded by course measurements" table at the top of `reports/Cerebras architecture course research.md` and `course/reviews/CROSS_CHAPTER_NOTES.md`. Affected here: Blackhole L1 is 1536 KiB with 64 B flits and ≤16 KiB packets (1464 KiB / 32 B / 8 KiB are Wormhole).

> Research note on method (as of 2026-11-01): this session's network sandbox blocked docs.tenstorrent.com, tenstorrent.com, theregister.com, servethehome.com, corsix.org, and blog.gpu.net. Only raw.githubusercontent.com could be fetched. Primary facts below come from fetched GitHub sources: tt-metal METALIUM_GUIDE.md, the tt-metal tech reports, and tt-isa-documentation. Everything else comes from search-result snippets, which are marked "(snippet)". Those should be re-checked against the full page before publication.

## 1. Product line and specs (Grayskull, Wormhole, Blackhole, Galaxy, 2025-2026 products)

### Takeaway
There are three shipping generations. Grayskull (12nm, legacy, discontinued) has 120 Tensix cores and LPDDR4. Wormhole (12nm) has 80 Tensix tiles per die, 12 GiB of GDDR6, and 16x100 GbE. Blackhole (TSMC 6nm, current) has 140 Tensix tiles per die, 32 GiB of GDDR6, 14x400 GbE, and 16 SiFive X280 "big" RISC-V cores. Each is sold as PCIe cards plus 32-chip "Galaxy" servers. Peak-TFLOPS figures are vendor claims and conflict across sources (745 vs 774 vs 664 TFLOPS FP8 for Blackhole). The p150's published core count was cut from 140 to 120 by a firmware change in February 2026.

### Cited Findings
**Grayskull (first generation, LEGACY / now "currently unavailable")**
- Grayskull e150: 120 Tensix cores, 1.2 GHz AI clock, 120 MB SRAM, 8 GB LPDDR4 at 118.4 GB/s, 200 W total board power (TBP), $799 at launch. The e75 has 96 cores, 1 GHz, and 75 W. (snippet) — [Tenstorrent Grayskull spec page](https://docs.tenstorrent.com/aibs/grayskull/specifications.html); [Hackster](https://hackster.io/news/tenstorrent-launches-its-risc-v-powered-ai-inference-acceleration-boards-the-grayskull-e75-and-e150-e5b07d9e7274)
- Grayskull: 12nm, 120 Tensix cores, 8 channels of LPDDR4, "332 TFLOPS (FP8) / 83 TFLOPS (BLOCKFP8)". The FP8 figure is a vendor number. (snippet) — [Tenstorrent slides, EPCC HPC Asia 2025](https://riscv.epcc.ed.ac.uk/assets/files/hpcasia25/Tenstorrent.pdf)
- Grayskull's vector unit is 19-bit FP with 64-element vectors. Wormhole and Blackhole use 32-bit FP with 32-element vectors. — [tt-metal METALIUM_GUIDE.md](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/METALIUM_GUIDE.md)

**Wormhole (second generation, 12nm; still sold, but superseded by Blackhole)**
- Per ASIC: 80 Tensix tiles, of which 64, 72 or 80 are active depending on product (the rest are fused off). Also 18 DRAM tiles exposing 12 GiB of GDDR6, 16 Ethernet tiles each with bidirectional 100 GbE, 1 PCIe 4.0 x16 tile, 1 ARC management tile, and 2 NoCs in a 2D torus. — [tt-isa-documentation WormholeB0 README](https://raw.githubusercontent.com/tenstorrent/tt-isa-documentation/main/WormholeB0/README.md)
- Wormhole n150 Tensix grid is 8x10 (80 total), with 64 (8x8) available for compute in tt-metal. It has 16 Ethernet cores (1 RISC-V and 256 KB L1 each) and 12 DRAM banks of 1 GB. — [tt-metal Blackhole Bring-Up Programming Guide](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/tech_reports/Blackhole/BlackholeBringUpProgrammingGuide.md)
- n300 = two Wormhole chips on one card: an "L" (local, PCIe-attached) chip and an "R" (remote) chip linked by on-card Ethernet. — [METALIUM_GUIDE.md](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/METALIUM_GUIDE.md)
- n300: 128 Tensix cores across 2 chips, 24 GB GDDR6, 576 GB/s, "up to 466 TFLOPS (FP8)" (233 BF16) at 300 W TBP, PCIe Gen4 x16, 1 GHz AI clock. Vendor claim. HotHardware reported 488 TFLOPS, which conflicts. (snippet) — [Tenstorrent Wormhole one-pager](https://tenstorrent.com/assets/one-pagers/08.01.24_Wormhole.pdf); [AnandTech](https://www.anandtech.com/show/21482/tenstorrent-launches-wormhole-ai-processors-466-fp8-tflops-at-300w); [HotHardware](https://hothardware.com/news/tenstorrent-wormhole-developer-kits-workstations)
- n300 external Ethernet: docs say 2x QSFP-DD "400GbE". Flopper lists 2x QSFP-DD 200G. Unresolved. (snippet) — [Tenstorrent Wormhole specs](https://docs.tenstorrent.com/aibs/wormhole/specifications.html); [Flopper n300s](https://flopper.io/gpu/tenstorrent-wormhole-n300s)
- Wormhole is 12nm. (snippet) — [AIWiki Blackhole](https://www.aiwiki.ai/wiki/blackhole_tenstorrent)
- Wormhole Galaxy: 32 Wormhole modules in a 4U server, priced from $70,000 (JP page). The product page snippet listed "292 TFLOPS (FP8)" for the full server. This is very likely a per-module or erroneous number (see Inferences). (snippet) — [Tenstorrent Galaxy page](https://tenstorrent.com/hardware/galaxy); [Tenstorrent JP Galaxy](https://tenstorrent.com/ja/hardware/galaxy)
- tt-metal's LLM report calls the Wormhole Galaxy "TG, a 2D mesh of 8x4 devices". T3000 (T3K) is the 8-chip (4x n300) box. — [tt-metal LLMs tech report](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/tech_reports/LLMs/llms.md)

**Blackhole (third generation, TSMC 6nm, CURRENT)**
- Full ASIC / p150 / p100 tile counts: Tensix 140 / 140 / 120. DRAM tiles 24 / 24 / 21. L2CPU tiles 4 / 4 / 4. Ethernet tiles 14 / 12 / 0, of which 12 / 8 / 0 have 400 GbE connected. PCIe tiles 2 / 1 / 1. 1 ARC, 1 security tile, 2 NoCs. — [tt-isa-documentation BlackholeA0 README](https://raw.githubusercontent.com/tenstorrent/tt-isa-documentation/main/BlackholeA0/README.md)
- GDDR6: 32 GiB on the full ASIC (28 or 32 GiB enabled by product), each 4 GiB exposed across 3 DRAM tiles. 16 SiFive X280 cores in 4 coherent clusters of 4. Each core has 32 KiB L1-D, 32 KiB L1-I and 128 KiB L2, and each cluster has 2 MiB shared L3. Ethernet is 400 GbE per tile, paired into 800 GbE QSFP-DD ports, and the p150 has 4 QSFP-DD ports. PCIe 5.0 x16. — [BlackholeA0 README](https://raw.githubusercontent.com/tenstorrent/tt-isa-documentation/main/BlackholeA0/README.md)
- Blackhole grid is 14x10 = 140 Tensix, with 130 (13x10) available for compute in tt-metal at the time of writing. L1 is 1464 KB per Tensix (unchanged from Wormhole), plus a tiny optional write-through data cache (4 x 16B lines, off by default). 14 Ethernet cores (2 RISC-V, 512 KB L1 each). 8 DRAM banks of about 4 GB. DRAM tiles carry a RISC-V with 128 KB L1 that the runtime doesn't yet expose. — [tt-metal Blackhole Bring-Up Guide](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/tech_reports/Blackhole/BlackholeBringUpProgrammingGuide.md)
- Hot Chips 2024: TSMC 6nm, 745 TFLOPS FP8 (372 FP16), 32 GB GDDR6, "768 RISC-V cores" in total (counting the baby cores). Vendor claim. (snippet) — [The Register via RISC-V Intl.](https://riscv.org/blog/tenstorrents-blackhole-chips-boast-768-risc-v-cores-and-almost-as-many-flops/); [AIWiki Blackhole](https://www.aiwiki.ai/wiki/blackhole_tenstorrent)
- The 774 TFLOPS (FP8) figure in a Tenstorrent university deck conflicts with 745. (snippet) — [EPCC Tenstorrent slides](https://riscv.epcc.ed.ac.uk/assets/files/hpcasia25/Tenstorrent.pdf)
- Current official card specs (post-firmware v19.5.0, February 2026): 120 Tensix + 16 big RISC-V, 180 MB SRAM (1.5 MB/core), up to 32 GB GDDR6 on a 256-bit bus, 512 GB/s (third-party figure), 300 W, PCIe 5.0 x16, 664 TFLOPS BLOCKFP8 (was 774). The firmware cut p150 from 140 to 120 Tensix cores and from 210 MB to 180 MB SRAM. (snippet) — [Tenstorrent Blackhole specs](https://docs.tenstorrent.com/aibs/blackhole/specifications.html); [WhatPSU](https://de.whatpsu.com/articles/2460-Tenstorrent-Removes-20-Cores-From-Already-Shipped-Blackhole-P150-Cards); [Flopper p150a](https://flopper.io/gpu/tenstorrent-blackhole-p150a)
- Blackhole dev products went on sale at Tenstorrent Dev Day, April 3, 2025. Unlike Grayskull and Wormhole, Blackhole is pitched as a "standalone AI computer" because of its on-die Linux-capable X280s. (snippet) — [Gigazine](https://gigazine.net/gsc_news/en/20250404-tenstorrent-blackhole); [ServeTheHome](https://servethehome.com/tenstorrent-blackhole-and-metalium-for-standalone-ai-processing)
- Galaxy Blackhole: 32 Blackhole ASICs, 23 PFLOPS Block FP8, 6.2 GB accelerator SRAM, 1 TB GDDR6 at 16 TB/s. Flopper lists about 12.0 kW. Priced from $110,000 (US page) or $160,000 (JP page). Hot Chips 2024 had projected "nearly 24 PFLOPS". (snippet) — [Tenstorrent Galaxy](https://tenstorrent.com/hardware/galaxy); [Flopper Galaxy Blackhole](https://flopper.io/system/tenstorrent-galaxy-blackhole); [Munich Startup](https://insights.munich-startup.de/news/feed/tenstorrent-launches-110k-galaxy-blackhole-ai-server-with-32-accelerators-and-23-petaflops)
- QuietBox: 8 Wormhole or 4 Blackhole processors in a mesh. Galaxy-style systems have up to 32 chips per host. — [METALIUM_GUIDE.md](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/METALIUM_GUIDE.md)
- TT-QuietBox 2: 4x Blackhole, "480 RISC-V cores", $9,999. (snippet) — [AIProductivity](https://aiproductivity.ai/news/tenstorrent-quietbox-2-risc-v-ai-workstation/)

**2025-2026 products and roadmap (Quasar, Ascalon, Aegis)**
- Quasar is a low-power ML chiplet on Samsung SF4X (4nm-class), designed to work in groups and pair with Tenstorrent CPU chiplets. 2026 reports say the Samsung-made Quasar "is not based on RISC-V". (snippet; older reporting plus a 2026 job post) — [Kowatek](https://blog.kowatek.com/?p=33381); [Counterpoint](https://www.counterpointresearch.com/en/insights/tenstorrent-at-the-open-frontier)
- TT-Ascalon is a high-performance RISC-V CPU IP, announced as available for licensing. The newsroom lists TT-Ascalon S (July 30, 2026). Counterpoint describes a 2026 portfolio of chiplets (Aegis, Quasar), subsystems, and "Ascalon Arsenal". (snippet) — [Tenstorrent newsroom](https://tenstorrent.com/newsroom/tenstorrent-announces-availability-of-tt-ascalon); [Counterpoint](https://www.counterpointresearch.com/en/insights/tenstorrent-at-the-open-frontier)
- Corporate context: in June 2026 The Information/Reuters reported Qualcomm in talks to acquire Tenstorrent for $8-10B. Bloomberg (May 2026) said Intel was also interested. A July 10, 2026 technews.tw report quotes Jim Keller denying negotiations with Qualcomm. — [Design & Reuse](https://www.design-reuse.com/news/202530698-qualcomm-is-reportedly-considering-a-tenstorrent-acquisition-for-up-to-10-billion-dollars-jim-keller-s-ai-and-risc-v-company-in-focus/); [TechNews TW](https://finance.technews.tw/2026/07/10/qualcomm-reportedly-acquires-tensorrent-for-10-billion/); [The Logic](https://thelogic.co/briefing/intel-qualcomm-interested-in-acquiring-tenstorrent-report/)

### Inferences
- Use these numbers for a per-chip comparison table. All TFLOPS figures are vendor peaks.

  | | Grayskull e150 | Wormhole n150 | Wormhole n300 | Blackhole p150 |
  |---|---|---|---|---|
  | Status | legacy | older | older | current |
  | Process | 12nm | 12nm | 12nm | 6nm |
  | Tensix cores | 120 | 64-72 (one die) | 128 (two dies) | 120 (140 before Feb 2026) |
  | Off-chip memory | 8 GB LPDDR4, 118 GB/s | 12 GB GDDR6 | 24 GB GDDR6, 576 GB/s | 32 GB GDDR6, ~512 GB/s |
  | Peak FP8 | 332 TFLOPS | n/a | 466 TFLOPS | 664-774 TFLOPS |
  | Power | 200 W | n/a | 300 W | 300 W |

- Per-core L1 is about 1 MB on Grayskull (120 MB / 120 cores). On Wormhole and Blackhole it is 1464 KiB (about 1.43 MiB, marketed as "1.5 MB").
- Galaxy Blackhole's 6.2 GB of SRAM works out to about 1.5 MB x ~4,000 Tensix cores (32 x ~120-130). Compare this with Cerebras WSE-3's 44 GB of on-wafer SRAM (figure from Cerebras public specs; check against the Cerebras notes). That is about 7x more SRAM on one wafer than in a whole 32-chip Galaxy. Galaxy instead adds 1 TB of GDDR6.
- The "292 TFLOPS FP8" Wormhole Galaxy number is inconsistent with 32 chips at about 230+ TFLOPS each, which would give roughly 7-9 PFLOPS. Treat it as a scraping or page error.
- The 140 vs 130 vs 120 Tensix discrepancy for Blackhole probably reflects different layers. 140 is physical tiles. 130 was the usable grid in early tt-metal, with one column likely reserved for dispatch or harvesting. 120 is the published spec after the firmware change.

### Gaps
- Could not fetch docs.tenstorrent.com spec tables directly (network blocked). Exact per-datatype TFLOPS (FP16/BF16/BFP8/BFP4/TF32) for n150/n300/p100/p150 and Wormhole power for n150 are unverified.
- Wormhole n150 official Tensix count (72 vs 64 usable) was not confirmed from a spec table.
- No confirmed 2026 tape-out or availability details for Quasar or Aegis chiplets. No confirmed specs for any "Blackhole successor" accelerator.
- Clock frequencies for Wormhole and Blackhole Tensix are stated only as "1 GHz" in a snippet (n300). Blackhole clock was not found.

## 2. Tensix core internals

### Takeaway
A Tensix tile has 5 tiny RV32IM "baby" RISC-V cores, 1464 KiB of software-managed L1 SRAM (no caches), 2 NoC interfaces, and a Tensix coprocessor (2 unpackers, an FPU matrix unit, a 32-lane FP32 SFPU vector unit, a scalar unit, and 4 packers). The RISC-V cores don't compute. They issue instructions to these engines. Two cores move data over the NoC, and three (TRISC0/1/2 = unpack/math/pack) drive the compute pipeline. All compute works on 32x32 tiles that flow through L1 circular buffers.

### Cited Findings
- Each Tensix core has five "baby" RISC-V CPUs: Data Movement 0 (BRISC), Data Movement 1 (NCRISC), Unpack, Math, and Pack (TRISC0/1/2). They are RV32IM, single-threaded, with no hardware multithreading or task switching. They dispatch instructions to the hardware engines rather than doing heavy computation themselves. — [METALIUM_GUIDE.md](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/METALIUM_GUIDE.md)
- The Wormhole Tensix tile has 1464 KiB of L1, 5 RV32IM baby cores, 2 NoC connections, and a "NoC overlay" coprocessor. The Tensix coprocessor contains 2 unpackers (L1 to coprocessor), 1 Matrix Unit (FPU, low-precision matmul-accumulate), 1 Vector Unit (SFPU, "32-wide SIMD operations on 32-bit lanes"), 1 scalar unit (ThCon, integer scalar ops and 128-bit L1 memory ops), and 4 packers (coprocessor to L1). The suggested split is 2 RISC-Vs overseeing the NoC and 3 overseeing the coprocessor. — [tt-isa-documentation WormholeB0 TensixTile](https://raw.githubusercontent.com/tenstorrent/tt-isa-documentation/main/WormholeB0/TensixTile/README.md)
- There is no cache hierarchy. SRAM is directly addressable chip-wide, and all data movement is explicit. The guide compares the design to the IBM CELL processor (per-core SRAM plus explicit DMA). — [METALIUM_GUIDE.md](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/METALIUM_GUIDE.md)
- The native tile is 32x32 elements, used by both matrix and vector units. Tensors are padded to that size (for example, 48x1024 becomes 64x1024). A bfloat16 tile is 1024 x 2 B = 2048 B. — [METALIUM_GUIDE.md](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/METALIUM_GUIDE.md)
- The compute kernel is one source file that the compiler builds into three binaries, one each for the Unpack, Math, and Pack cores. — [METALIUM_GUIDE.md](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/METALIUM_GUIDE.md)
- The Wormhole DST (accumulator/destination) register holds 8 tiles when accumulating in BF16 and 4 tiles in FP32. — [tt-metal LLMs tech report](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/tech_reports/LLMs/llms.md)
- Data formats used in practice include bfloat16, bfloat8_b (BFP8, block floating point with a shared exponent) and bfloat4_b (BFP4). Llama uses bfloat8_b for the MLP and LM-head outputs, and SDPA accepts bf16, bfp8_b, or bfp4_b. Math fidelity knobs (LoFi/HiFi2/HiFi4) trade accuracy for FPU passes: HiFi2 for the MLP, while HiFi4 "would mean that this matmul would become compute bound". — [tt-metal LLMs tech report](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/tech_reports/LLMs/llms.md)
- Circular buffers (CBs) live in L1 and act as producer-consumer queues with hardware-assisted metadata synchronization. Example IDs are c_0 and c_1 for inputs and c_16 for output. Size each CB for at least 2 tiles (double-buffering) so data movement overlaps compute. — [METALIUM_GUIDE.md](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/METALIUM_GUIDE.md)
- Blackhole's L1 is still 1464 KB. Blackhole adds a 4 x 16 B write-through L1 data cache for the baby cores, off by default. — [Blackhole Bring-Up Guide](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/tech_reports/Blackhole/BlackholeBringUpProgrammingGuide.md)

### Inferences
- In a diagram, a Tensix core is: L1 (1.43 MiB) at the center. Two NoC routers sit at its edges, driven by BRISC and NCRISC. An unpack, math (FPU/SFPU on SrcA/SrcB to DST), pack pipeline is driven by the 3 TRISCs.
- A Cerebras WSE PE is similar in that both have private SRAM and no cache. The PE has much smaller SRAM (48 KB on WSE-2/3, per the Cerebras notes) and one core with a router. A Tensix core is about 30x larger in SRAM and coarse-grained (tile-level matmul engine), while a WSE PE is fine-grained (scalar/SIMD on wavelets).
- A GPU SM is similar in that both have a tensor or matrix engine plus a vector unit. The GPU hides latency with threads and caches, while Tensix uses explicit software pipelining across 5 cooperating in-order cores.

### Gaps
- FPU throughput per cycle (for example, the matmul shape per instruction) and SrcA/SrcB register sizes were not in the fetched pages. They are likely in TensixTile sub-pages not fetched.
- The exact BFP8/BFP4 encoding (block size of 16 elements with a shared 8-bit exponent) was not verified from a fetched source in this session.

## 3. Network-on-Chip and Ethernet scale-out

### Takeaway
Each chip has two physically separate 2D-torus NoCs running in opposite directions (NoC0 is typically used for reads, NoC1 for writes). Links are 32 B/flit, one flit per cycle. Packets are up to 8 KiB, and rectangular multicast is supported (Blackhole adds strided and L-shaped). Scale-out uses native on-die Ethernet: 16x100 GbE on Wormhole, 14x400 GbE on Blackhole. Chips are wired directly into 2D meshes or tori (n300 to T3K/QuietBox to 32-chip Galaxy to multi-host via TT-Fabric) without switches or NVLink-style fabrics.

### Cited Findings
- NoC flit = 256 bits (32 B). Links carry one flit per cycle per NoC. A packet is 1 header flit plus up to 256 data flits, so the maximum payload is 8192 B. 16 B atomics are supported. — [tt-isa-documentation WormholeB0 NoC](https://raw.githubusercontent.com/tenstorrent/tt-isa-documentation/main/WormholeB0/NoC/README.md)
- The topology is a 2D torus with edges wrapped. NoC#0 and NoC#1 connect the same tiles but are physically separate and flow in opposite directions. Latency is about 5 cycles NIU to router, 9 cycles router to router, and about 5 cycles router to NIU. — [WormholeB0 NoC](https://raw.githubusercontent.com/tenstorrent/tt-isa-documentation/main/WormholeB0/NoC/README.md)
- Multicast (broadcast writes and atomics) targets a rectangle of receivers, and only Tensix tiles can receive. Each 2 GiB GDDR6 DRAM tile on Wormhole has 6 NIUs, 3 per NoC. — [WormholeB0 NoC](https://raw.githubusercontent.com/tenstorrent/tt-isa-documentation/main/WormholeB0/NoC/README.md)
- Blackhole multicast adds strided and L-shaped patterns. NoC read alignment to DRAM/PCIe grows from 32 B to 64 B. Blackhole needs explicit NoC flushes where Wormhole often did not. — [Blackhole Bring-Up Guide](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/tech_reports/Blackhole/BlackholeBringUpProgrammingGuide.md)
- By convention, NoC0 handles reads (DRAM or other cores to local L1) and NoC1 handles writes. Using both NoCs for one transfer can double effective bandwidth. DRAM sits outside the Tensix address space and needs explicit DMA. Tensors are "interleaved" across DRAM banks by default or "sharded" across cores' L1. — [METALIUM_GUIDE.md](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/METALIUM_GUIDE.md)
- Chips use standard Ethernet "up to 800G" (the guide contrasts this with NVLink 5.0 at 400G). Ethernet traffic is handled by Ethernet Data Movers (EDM). Multi-host meshes of 32-chip boxes are linked through tt-Fabric. — [METALIUM_GUIDE.md](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/METALIUM_GUIDE.md)
- Wormhole has 16 Ethernet tiles at bidirectional 100 GbE. Blackhole has 14 tiles at 400 GbE, paired into 800 GbE QSFP-DD ports. On Blackhole, a PCIe x16 connection costs 4 Ethernet tiles. — [WormholeB0 README](https://raw.githubusercontent.com/tenstorrent/tt-isa-documentation/main/WormholeB0/README.md); [BlackholeA0 README](https://raw.githubusercontent.com/tenstorrent/tt-isa-documentation/main/BlackholeA0/README.md)
- In LLM collectives, N300 and T3000 use 1 Ethernet link per AllGather. TG (Galaxy, 8x4 mesh) uses 4 links along one cluster axis and 3 along the other. — [tt-metal LLMs tech report](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/tech_reports/LLMs/llms.md)
- Because Ethernet is on-die, an n300's two chips can be programmed like a continuous Tensix grid. (snippet; third-party) — [Flopper n300s](https://flopper.io/gpu/tenstorrent-wormhole-n300s)

### Inferences
- Per-link NoC bandwidth is 32 B/cycle. At about 1 GHz (the n300 clock), that is roughly 32 GB/s per link, per direction, per NoC. This is computed, not vendor-stated.
- Contrast for diagrams:
  - Cerebras uses a single 2D mesh fabric of PEs across the wafer, with wavelets (32-bit) routed by color. There is no off-wafer DRAM in the compute path; weights stream in via MemoryX/SwarmX.
  - Tenstorrent has a 2D torus on each die, then "the same mesh idea extended" across chips via Ethernet. The mesh crosses die boundaries at Ethernet speeds, not on-wafer speeds.
  - GPUs use a hierarchical crossbar/L2, with NVLink and NVSwitch for scale-up.
- Tenstorrent's philosophy is "no special interconnect": Ethernet ports on every chip make chip-to-chip and box-to-box links the same technology.

### Gaps
- Aggregate on-chip NoC bisection bandwidth (GB/s) is not vendor-stated in fetched sources.
- Blackhole NoC link width was not confirmed to be the same as Wormhole's (assumed 32 B but unverified).
- Galaxy internal wiring (which ports form the 8x4 torus and which go external) was not verified.

## 4. Programming model: TT-Metalium, TT-NN, TT-Forge/TT-MLIR; contrast with Cerebras CSL

### Takeaway
TT-Metalium is an open-source C++ host API (OpenCL-like) plus C++ device kernels. A typical op runs three kernels per core: a reader on NoC0, a compute kernel split across the TRISCs, and a writer on NoC1. They talk through L1 circular buffers using a reserve/push/wait/pop handshake. Work is divided across cores by explicit runtime arguments, not thread IDs. TT-NN (PyTorch-like op library) sits above it, and TT-Forge (TT-XLA/PJRT for PyTorch/JAX into TT-MLIR) is the compiler stack. All of it is open source on GitHub.

### Cited Findings
- TT-Metalium is a C++ API modeled on OpenCL. TTNN, tt-MLIR, and tt-Forge build on it. Everything is a mesh (a single chip is a 1x1 mesh). Key host calls include `MeshDevice::create_unit_mesh`, `MeshBuffer::create`, `EnqueueWriteMeshBuffer`, `CreateCircularBuffer`, `CreateKernel`, `SetRuntimeArgs`, `EnqueueMeshWorkload`, `EnqueueReadMeshBuffer`, and `split_work_to_cores`. — [METALIUM_GUIDE.md](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/METALIUM_GUIDE.md)
- There are three kernel types per Tensix: reader (input, usually NoC0), compute (Unpack/Math/Pack cores), and writer (output, usually NoC1). There is no built-in `get_global_id()`. Work is partitioned with runtime args, and every core in the grid must get runtime args, even idle ones. — [METALIUM_GUIDE.md](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/METALIUM_GUIDE.md)
- Fast dispatch uses one RISC-V core per command queue, usually on an unused Ethernet tile. Each device has 2 command queues (CQ0 for compute, CQ1 for data transfer), executed strictly in order. Slow dispatch (`TT_METAL_SLOW_DISPATCH_MODE=1`) is for debugging. — [METALIUM_GUIDE.md](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/METALIUM_GUIDE.md)
- GPUs rely on SIMT, latency hiding, and caches. Tensix avoids all three in favor of asynchronous I/O, software pipelining, and cooperation among the baby cores, which makes memory access deterministic. — [METALIUM_GUIDE.md](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/METALIUM_GUIDE.md)
- The stack from top to bottom is TT-Forge, TT-NN, TT-Metalium, TT-LLK (low-level kernels). ttsim is the official ISA simulator and golden reference. — [tt-isa-documentation README](https://raw.githubusercontent.com/tenstorrent/tt-isa-documentation/main/README.md)
- The TT-Forge README covers four pieces (snippet):
  - TT-XLA is the primary PyTorch and JAX frontend, using PJRT to produce StableHLO for TT-MLIR. TT-Forge-ONNX is a TVM-based frontend for ONNX, TF, and PaddlePaddle (single-chip only).
  - TT-MLIR defines TTIR, TTNN, and TTKernel dialects, runs fusion, sharding, and layout passes, and lowers to TT-Metalium.
  - TT-Lang is a Python kernel DSL (early preview).
  - TT-Blacksmith provides training recipes.

  Older pages name tt-torch and tt-forge-fe as frontends, and the earlier stack was TT-Buda. — [tt-forge GitHub](https://github.com/tenstorrent/tt-forge); [Tenstorrent TT-Forge page](https://tenstorrent.com/software/tt-forge); [TT-Buda page](https://tenstorrent.com/software/tt-buda)
- LLM ops in TT-NN are tuned per op. Examples: flash attention over an 8x8 grid (64 cores), with "more than 16 cores per head batch" giving no benefit in flash decode. Decode supports batches up to 32 and prefill sequences up to 128k. A full-model decode pass takes about 10 ms "with microsecond-length OP times". — [tt-metal LLMs tech report](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/tech_reports/LLMs/llms.md)

### Inferences
- The canonical Metalium kernel triplet (pseudocode) runs as three cooperating loops:
  - Reader loop: `cb_reserve_back(cb_in)`, then `noc_async_read(dram_addr to cb write ptr)`, then `noc_async_read_barrier()`, then `cb_push_back(cb_in)`.
  - Compute loop: `cb_wait_front(cb_in)`, then unpack, math, and pack into `cb_out`, then `cb_pop_front(cb_in)` and `cb_push_back(cb_out)`.
  - Writer loop: `cb_wait_front(cb_out)`, then `noc_async_write`, then `cb_pop_front(cb_out)`.

  The CB API names come from the tt-metal codebase and should be verified against the guide's code samples before quoting.
- Contrast with Cerebras CSL: in CSL, the program is per-PE dataflow. Tasks are triggered by arriving wavelets on colors, routes are configured statically, and there are no explicit DRAM reads (data streams in over the fabric). In Metalium, the programmer explicitly issues DMA-like NoC reads and writes between DRAM and L1 and between cores, and synchronizes through CB counters. It is closer to "CELL SPE plus DMA" or "CUDA with manual cp.async pipelines" than to pure dataflow.
- Both vendors expose the low-level layer openly (CSL SDK; tt-metal on GitHub). Tenstorrent is fully open source (Apache-2.0 repos, public ISA docs, and a simulator), which is a sharper open stance than Cerebras's closed compiler with a public SDK.

### Gaps
- The exact CB API function names were not confirmed from the fetched text (the guide summary mentioned CBs but not function names).
- No verification of the license (Apache 2.0) from a fetched page in this session.

## 5. Memory hierarchy philosophy (SRAM + DRAM vs Cerebras SRAM-only vs GPU HBM + caches)

### Takeaway
Tenstorrent uses a two-level, software-managed hierarchy. A large distributed L1 SRAM (about 1.5 MB per core, 120-210 MB per chip) holds the working set and activations, and relatively cheap GDDR6 (not HBM) holds weights and KV cache. There are no hardware caches, and all moves are explicit NoC DMA. It sits between Cerebras (44 GB on-wafer SRAM, weights streamed from external MemoryX) and GPUs (HBM plus hardware L1/L2 caches).

### Cited Findings
- There is no cache hierarchy, and DRAM is accessed only via explicit DMA. Tensor placement is interleaved in DRAM or sharded across L1. — [METALIUM_GUIDE.md](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/METALIUM_GUIDE.md)
- Blackhole p150: 180 MB SRAM (post-February 2026) plus 32 GB GDDR6 on a 256-bit bus (about 512 GB/s). (snippet) — [Tenstorrent Blackhole specs](https://docs.tenstorrent.com/aibs/blackhole/specifications.html); [Flopper p150a](https://flopper.io/gpu/tenstorrent-blackhole-p150a)
- Galaxy Blackhole: 6.2 GB SRAM plus 1 TB GDDR6 at 16 TB/s across 32 chips. (snippet) — [Tenstorrent Galaxy](https://tenstorrent.com/hardware/galaxy)
- LLM decode on Wormhole "is bound by time to read model weights from DRAM rather than time to compute". This is why BFP8/BFP4 weights matter. — [tt-metal LLMs tech report](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/tech_reports/LLMs/llms.md)
- Wormhole uses 12 DRAM banks of 1 GB, and Blackhole uses 8 banks of about 4 GB. Weights are padded to fit evenly across banks. — [Blackhole Bring-Up Guide](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/tech_reports/Blackhole/BlackholeBringUpProgrammingGuide.md); [LLMs tech report](https://raw.githubusercontent.com/tenstorrent/tt-metal/main/tech_reports/LLMs/llms.md)

### Inferences
- A single p150 has about 512 GB/s of GDDR6, roughly 6x less bandwidth than one H100's HBM3 (about 3.35 TB/s; the H100 figure comes from NVIDIA's public spec, not fetched here). Tenstorrent compensates by scaling out many cheap chips (Galaxy reaches 16 TB/s aggregate) and with block-float weight compression. This is a cost-per-bandwidth design point rather than a peak-bandwidth one.
- Diagram suggestion: three columns.
  - Cerebras: SRAM-only on the wafer (44 GB, about 21 PB/s), weights streamed in.
  - Tenstorrent: per-core SRAM (about 180 MB per chip) plus GDDR6 (32 GB at about 0.5 TB/s per chip), explicit NoC DMA, no caches.
  - GPU: registers, then shared memory/L1 (software or hardware), then L2 (hardware cache, about 50 MB), then HBM (80-192 GB at 3-8 TB/s).

  Take the Cerebras and GPU figures from the other researchers' notes.

### Gaps
- Per-chip GDDR6 bandwidth for Wormhole n150 (single die) was not directly confirmed (n300's 576 GB/s covers two dies, implying about 288 GB/s per die).

## 6. Performance positioning and benchmarks

### Takeaway
Tenstorrent positions itself as the low-cost, open, Ethernet-scaled alternative for inference, with a cost per FLOP or per token pitch rather than peak performance. Nearly all published LLM numbers are vendor-run (tt-metal model READMEs, launch PR). The headline claim is about 350 tok/s/user on DeepSeek-R1 671B on Galaxy Blackhole, with one report of about 308 tok/s/user measured at launch. Independent MLPerf-style audited results were not found.

### Cited Findings
- Galaxy Blackhole: Tenstorrent reports decode up to about 350 tokens/s/user on DeepSeek-R1 671B across batch 8-64. Other reporting put the measured figure at launch closer to 308 tok/s/user. Vendor claims. (snippet) — [Munich Startup](https://insights.munich-startup.de/news/feed/tenstorrent-launches-galaxy-blackhole-ai-system-with-10x-faster-video-generation-and-350-tokens-second-llm-inference); [Futurum](https://futurumgroup.com/insights/tenstorrents-galaxy-blackhole-can-risc-v-processors-expand-fast-inference-globally/)
- Llama 70B at batch 32 on Galaxy: 4,000-5,000 tok/s aggregate, from Tenstorrent's own benchmarking and not independently verified. (snippet) — [blog.gpu.net benchmarks post](https://blog.gpu.net/posts/2026/june/new-blog-june13/)
- TT-QuietBox 2 (4x Blackhole): Llama 3.1 70B at 476.5 tok/s aggregate, vendor figure. (snippet) — [blog.gpu.net benchmarks post](https://blog.gpu.net/posts/2026/june/new-blog-june13/)
- At Hot Chips 2024, Tenstorrent claimed Blackhole can outperform an NVIDIA A100 in raw compute and scalability. Vendor claim. (snippet) — [ServeTheHome](https://www.servethehome.com/?p=79969)
- Pricing anchors are $799 for Grayskull e150, $110k-$160k for Galaxy Blackhole, $70k for Wormhole Galaxy (JP), and $9,999 for QuietBox 2. (snippets) — [Hackster](https://hackster.io/news/tenstorrent-launches-its-risc-v-powered-ai-inference-acceleration-boards-the-grayskull-e75-and-e150-e5b07d9e7274); [Tenstorrent Galaxy](https://tenstorrent.com/hardware/galaxy); [AIProductivity](https://aiproductivity.ai/news/tenstorrent-quietbox-2-risc-v-ai-workstation/)
- Jim Keller said the Cerebras IPO was "helpful" and that Tenstorrent aims to "beat them on everything". This is positioning rhetoric. (snippet; headline only) — [Wccftech](https://wccftech.com/jim-keller-cerebras-ipo-was-helpful-tenstorrent-to-beat-them-on-everything/)

### Inferences
- Positioning versus Cerebras: Cerebras sells peak single-stream speed (thousands of tok/s/user on SRAM-resident or streamed models) at high system cost. Tenstorrent sells moderate per-user speed (hundreds of tok/s/user) on commodity-ish GDDR6 and Ethernet at much lower entry price. Versus GPUs, the pitch is openness (no CUDA lock-in, open ISA docs) and cost, not absolute performance.
- Training: no credible published training benchmarks were found. TT-Blacksmith training recipes exist, but the platform is inference-first in practice.

### Gaps
- No independently audited (MLPerf) Tenstorrent results found.
- No fetched primary source for Hot Chips 2025 Tenstorrent talk content.
- No Chips and Cheese or SemiAnalysis measured microbenchmarks retrieved (sites blocked or not surfaced).
- tt-metal's model-performance table (the README "LLMs" table with tok/s/user per model per system) could not be fetched in this session. It is the best primary source for vendor-measured numbers and should be checked: https://github.com/tenstorrent/tt-metal (README "Featured models" table).
