# ch13 · depth review

Summary. Chapter 13 is about 12 KB of text. It covers the product table, the five-RISC-V anatomy, a prose description of reader/compute/writer, a comparison table and two vendor tok/s figures. That is enough to name the parts, but it never shows how anything behaves. There is no matmul mapping, no NoC routing or multicast, no sharding, no kernel code, nothing on TT-Fabric beyond the word "mesh", and no account of how a 70B model is laid out on a Galaxy. Every one of these is documented in primary sources on raw.githubusercontent.com: METALIUM_GUIDE.md, the tech_reports, the programming_examples and tt-isa-documentation. All of them were fetched for this review. The research notes do not cover them, apart from one-line mentions. Several findings also fix the chapter's own claims. The "conflicting" Blackhole peaks of 664, 745 and 774 TF all follow exactly from cores × 4096 FLOP/cycle × clock. The chapter has no code, although the guide contains copyable, verified kernels.

Source shorthand used below (all fetched 2026-11-01 from `https://raw.githubusercontent.com/tenstorrent/`):
- **GUIDE** = `tt-metal/main/METALIUM_GUIDE.md`
- **MATENG** = `tt-metal/main/tech_reports/matrix_engine/matrix_engine.md`
- **GEMM** = `tt-metal/main/tech_reports/GEMM_FLOPS/GEMM_FLOPS.md`
- **LAYOUT** = `tt-metal/main/tech_reports/tensor_layouts/tensor_layouts.md`
- **SHARD** = `tt-metal/main/tech_reports/tensor_sharding/tensor_sharding.md`
- **DRAMBW** = `tt-metal/main/tech_reports/Saturating_DRAM_bandwidth/Saturating_DRAM_bandwidth.md`
- **LLM** = `tt-metal/main/tech_reports/LLMs/llms.md`
- **MESH** = `tt-metal/main/tech_reports/Programming_Mesh_of_Devices/Programming_Mesh_of_Devices_with_TT-NN.md`
- **FABRIC** = `tt-metal/main/tech_reports/TT-Fabric/TT-Fabric-Architecture.md`
- **CCL** = `tt-metal/main/tech_reports/CCLs/CCL_bandwidth.md` (updated Sept 2026)
- **FA** = `tt-metal/main/tech_reports/FlashAttention/FlashAttention.md`
- **DFMT** = `tt-metal/main/tech_reports/data_formats/data_formats.md`
- **MMEX** = `tt-metal/main/tt_metal/programming_examples/matmul/` (`matmul_single_core/kernels/compute/mm.cpp`, `matmul_multicore_reuse_mcast/matmul_multicore_reuse_mcast.cpp`, `matmul_common/kernels/dataflow/reader_bmm_tile_layout_in0_{sender_in1_sender,receiver_in1_receiver}.cpp`)
- **ISA-NOC** = `tt-isa-documentation/main/WormholeB0/NoC/{README,RoutingPaths}.md` and `BlackholeA0/NoC/README.md`
- **ISA-TC** = `tt-isa-documentation/main/WormholeB0/TensixTile/TensixCoprocessor/{README,MatrixUnit,SrcASrcB,Dst}.md`
- **README** = `tt-metal/main/README.md` (model performance tables)

All tt-metal numbers are vendor-authored, so they take `tag vendor`. Where the vendor ran the measurement, write "vendor-measured" in the prose. Arithmetic in this review takes `tag derived`.

## Gaps and additions (prioritised)

### D1 [critical] How a matmul is mapped onto the Tensix grid
**What is missing.** The chapter says the FPU does "tile matmuls" and stops there. It does not explain what the matrix engine does per cycle, how an (M×K)·(K×N) problem is cut across the core grid, how operands reach each core, or why the peak numbers are what they are.

**Why it matters.** Matmul is the workload, and this is the clearest place to show what "explicit, software-scheduled data movement" means in practice. It is also the closest Tenstorrent analogue to the Cerebras SUMMA/GEMV patterns in chapters 11 and 12, so without it the comparison chapter has nothing concrete to compare.

**Source.** MATENG, GEMM, LLM §4.3.2, MMEX, ISA-TC (MatrixUnit, SrcASrcB, Dst).

**Proposed addition.** Add a new section, "Anatomy of a matmul", with three layers.
1. **Inside one core.**
   - One FPU `MVMUL` computes 8×16 · 16×16 → 8×16 per cycle. That is 2048 MACs, or 4096 FLOP/cycle. It works out to about 4 TFLOPS per core at 1 GHz (Wormhole) and about 5.4 TFLOPS at 1.35 GHz (Blackhole) (MATENG, GEMM).
   - A 32×32 tile is stored as four 16×16 "faces", because the engine natively multiplies 16×16 faces (LAYOUT §3.2.2).
   - Operands are unpacked from L1 into SrcA and SrcB. Each holds 2 banks × 64 rows × 16 columns of 19-bit data and is double-buffered between the unpacker and the FPU (ISA-TC SrcASrcB). Results accumulate in Dst.
   - If the in0 operand has fewer than 8 rows, throughput drops proportionally. A 1×16 input runs at 1/8 rate (MATENG). This explains why decode batches are padded to tile height.
2. **Across the grid (matmul 2D, `MatmulMultiCoreReuseMultiCastProgramConfig`).**
   - M is split over `cores_y` and N over `cores_x`. Each core owns `per_core_M = ceil(M/32/cores_y)` × `per_core_N = ceil(N/32/cores_x)` output tiles.
   - K is streamed in blocks of `in0_block_w` tiles.
   - Outputs are produced in `out_subblock_h × out_subblock_w` sub-blocks, whose product must be ≤ DST capacity: 8 tiles in BF16, 4 in FP32 on Wormhole (LLM §4.3.2.1).
   - Draw a 4×4 grid with A row-blocks entering on the left column and B column-blocks entering on the top row.
3. **Operand reuse by multicast.**
   - In `matmul_multicore_reuse_mcast`, the host creates four reader-kernel variants: in0 sender/receiver × in1 sender/receiver. It also creates four semaphores (MMEX).
   - The left-column core reads an A block from DRAM and multicasts it to the rest of its row.
   - The top-row core reads a B block and multicasts it down its column.
   - Each operand therefore crosses DRAM once per row or column instead of once per core. This is a software-built systolic array.
   - The guide calls this the MPMD case: "specialized kernels on specific Tensix cores to broadcast data to other cores, reducing NoC bandwidth consumption" (GUIDE, SPMD in Metalium).
4. **Variant choice.** Give one sentence each on the three LLM matmuls (LLM §4.3.2):
   - **2D**: prefill, compute-bound, DRAM-interleaved inputs.
   - **1D**: N-parallel only, width-sharded activations, `mcast_in0=True`.
   - **DRAM-sharded**: decode, weight-bandwidth-bound (see D4).
5. **Measured.** Wormhole n150 reaches about 190 TFLOPS and Blackhole p150 about 580 TFLOPS on tuned matmuls. Peak utilisation is about 93% on WH and 96% on BH. BFP8/HiFi2 runs 1.5–1.8× faster than BF16/HiFi4 (GEMM, vendor-measured). The utilisation formula is ideal cycles = M·K·N / 32³ × cycles_per_tile / cores, with cycles_per_tile = 16, 32, 48 or 64 for LoFi, HiFi2, HiFi3 or HiFi4 (GEMM). One worked example using this formula would tie the section together.

Visual: an interactive grid. Let the learner choose M, N and K and a grid size. Highlight each core's output block, and animate one K-step with in0 sweeping across rows and in1 sweeping down columns. Show the DRAM bytes read with and without multicast.

### D2 [critical] How the NoC actually moves tiles, including multicast and its handshake
**What is missing.** The chapter has a single sentence: "two 2-D tori, opposite directions", plus "~9 cycles router to router". It gives no routing rule, no multicast mechanics, no explanation of how a receiver learns that data has arrived, no congestion behaviour and no per-link bandwidth.

**Why it matters.** The NoC is Tenstorrent's counterpart to the Cerebras fabric, which chapter 4 covers in depth. Without routing rules a learner cannot reason about DRAM reader placement (D4) or multicast cost (D1). This also answers pedagogy finding P4 ("the NoC's behaviour is not shown").

**Source.** ISA-NOC (README, RoutingPaths, BlackholeA0 README), MMEX reader kernels, DRAMBW, GUIDE.

**Proposed addition.** Add a section, "Moving a tile across the chip".
- **Routing is static dimension-order** (ISA-NOC RoutingPaths).
  - NoC 0 flows only rightward and downward: a packet goes right, turns at most once, then goes down.
  - NoC 1 flows only upward and leftward: up first, then left.
  - Edges wrap, so the network is a torus.
  - Routers are cut-through ("wormhole switching").
  - Congestion occurs only when two packets want the same link. Crossing inside a router is free. Packets on different virtual channels interleave.
- **Packets** have one header flit plus up to 256 data flits.
  - Wormhole flits are 32 B, giving up to 8 KiB per packet.
  - Blackhole flits are 64 B, giving up to 16 KiB per packet, and the NoC clock rises from 1 GHz to 1.35 GHz (ISA-NOC BlackholeA0). This overlaps with accuracy finding A2.
  - Derived per-link rate: 32 GB/s per direction per NoC on WH, and about 86 GB/s on BH (`tag derived`).
- **Multicast.** A write or atomic can target a *rectangle* of receivers, and only Tensix tiles accept it. The route is a tree: major axis, then minor axis, then major axis again. Broadcast requests use their own VC class (`0b10`) (ISA-NOC).
- **Handshake (real code, from MMEX).** Show about 12 lines.
  - Receiver: `noc_semaphore_set(my_sem, INVALID)`, then `noc_semaphore_inc(sender_sem_noc_addr, 1)` ("I have space"), then `noc_semaphore_wait(my_sem, VALID)`, then `cb_push_back`.
  - Sender: `noc_async_read_page`… `noc_async_read_barrier()`, then `noc_semaphore_wait(sender_sem, num_dests)`, then `noc_async_write_multicast(src, get_noc_multicast_addr(x0,y0,x1,y1,addr), bytes, num_dests)`, then `noc_semaphore_set_multicast(receiver_sem, ..., num_dests)`.
  - Note the Blackhole-only `noc_async_writes_flushed()` between the data multicast and the flag multicast. It is a nice concrete example of the "Blackhole needs explicit flushes" note in the research notes.
- **Contrast with Cerebras.** Cerebras routes are configured per colour at compile time and data triggers tasks. On Tenstorrent, each packet carries its destination, and synchronisation is a semaphore in L1 updated by NoC atomics.

Visual: a 10×12 grid widget. Click a source and a destination, or a destination rectangle, and toggle NoC 0 or NoC 1. The widget draws the route or multicast tree and highlights any link that two chosen transfers share. A preset reproduces the DRAMBW congestion example: 12 readers in the top rows with overlapping routes, compared with readers placed next to their banks.

### D3 [major] Real kernel code for reader, compute and writer, and the host side
**What is missing.** The chapter describes the kernel triplet only in prose. The research notes give unverified pseudocode and flag the CB API names as unconfirmed. The guide contains the full verified code.

**Why it matters.** Learning objective 2 promises that learners can "explain the reader / compute / writer kernel model". Chapters 10–12 teach CSL through real code, so chapter 13 should give the same level of code to make the comparison fair. This also addresses pedagogy finding P2.

**Source.** GUIDE (vector-add kernels, "Register control" section, SPMD section); MMEX `mm.cpp`.

**Proposed addition.** Add three tabbed code blocks, each trimmed to about 15 lines, with these API names (now confirmed):
- **Reader.** `get_arg_val<uint32_t>(i)`, `TensorAccessor(args, addr, tile_bytes)`, then a loop: `cb_reserve_back(cb_in0,1)`, `get_write_ptr`, `noc_async_read_page(i, a, addr)`, `noc_async_read_barrier()`, `cb_push_back(cb_in0,1)`.
- **Compute.** Annotate each line with the core that executes it, exactly as the guide does.
  - Setup: `compute_kernel_hw_startup` (U/M/P), `add_init`.
  - Loop: `cb_wait_front` (Unpack), `tile_regs_acquire` (Math), `add_tiles(cb0,cb1,0,0,dst)` (Unpack+Math), `tile_regs_commit` (Math), `cb_pop_front` (Unpack), `cb_reserve_back` (Pack), `tile_regs_wait` (Pack), `pack_tile` (Pack), `tile_regs_release` (Pack), `cb_push_back` (Pack).
  - Explain that the single source file is compiled three times, and each binary keeps only its own core's sections.
- **Writer.** `cb_wait_front`, `get_read_ptr`, `noc_async_write_page`, `noc_async_write_barrier`, `cb_pop_front`.
- **Matmul compute.** Add a fourth block taken from `mm.cpp`: `for mt, for nt { tile_regs_acquire(); for kt { cb_wait_front×2; matmul_tiles(cb0,cb1,0,0,0); cb_pop_front×2 } tile_regs_commit(); tile_regs_wait(); cb_reserve_back; pack_tile; cb_push_back; tile_regs_release(); }`. This links directly to D1.
- **SFPU pattern.** One line: `copy_tile(cb,0,dst); sin_tile(dst); pack_tile(dst,cb_out,0)`. FPU ops read circular buffers directly, whereas SFPU ops need the data in Dst first (GUIDE).
- **Host.** Give a 10-line sketch of `split_work_to_cores(grid, n_tiles)`. It returns two core groups with different tile counts, then a per-core `SetRuntimeArgs` loop passes each core its start ID. Include the warning that a core with a kernel but no args causes undefined behaviour (GUIDE).

Then add a two-column table that maps these calls to CSL equivalents: `cb_wait_front` ↔ a task activated by wavelet arrival, `noc_async_read_page` ↔ a fabric DSD with `@fmovs`, and runtime args ↔ `memcpy`/`SdkRuntime` parameters.

### D4 [major] Interleaved and sharded layouts, and why decode uses DRAM-sharded weights
**What is missing.** The chapter does not mention interleaved or sharded layouts at all.

**Why it matters.** Layout is the main performance tool in TT-NN. It is the mechanism behind the "decode is bound by DRAM" quote the chapter already uses. It also replaces kernel fusion: the FlashAttention report says L1 sharding gives a "form of op fusion specific to our framework".

**Source.** LAYOUT, SHARD, DRAMBW, LLM §3.3.4 and §4.3.2.2, FA §1, GUIDE ("SRAM, interleaved and shared buffers").

**Proposed addition.**
- **Vocabulary.** A tensor is a 2D buffer of *pages*. A page is one row in row-major layout or one 32×32 tile in tiled layout. Storage is L1 or DRAM. Memory layout is interleaved or sharded (LAYOUT).
- **Interleaved.** Pages are dealt round-robin across banks: 12 DRAM banks on Wormhole, 8 on Blackhole, one L1 bank per core. Every allocation starts at bank 0. Show the four-pages-over-three-banks picture.
- **Sharded.** The tensor is split into height, width or block shards, mapped one-to-one onto a core grid (SHARD). Example: shape (1,256,256) block-sharded on 4×4 cores gives 64×64 per core.
- **Why it matters.**
  - Sharded activations stay in L1 between ops, so no DRAM round trip is needed (FA).
  - In decode, weights are *width-sharded across the DRAM banks*. Each DRAM reader core sits next to its own bank, so every route is one hop, and readers in the same row use different NoC VCs. This reaches 92% of peak on a microbenchmark and 82–90% in Llama-3-70B and Mixtral decode matmuls, measured on Wormhole: 239–260 GB/s of 288 at 12 Gbps (DRAMBW, vendor-measured).
  - Tie this back to D2's routing rule: interleaved reads from every core cross the whole NoC and congest it.
- **Decode recipe** (LLM §3.3.4). Activations (batch × hidden, seq = 1) are L1 width-sharded, weights are DRAM-sharded, and weights are BFP8 or BFP4.

Visual: a toggle that shows one 256×256 tensor as interleaved over 12 DRAM banks, then height-, width- and block-sharded over a 4×4 core grid, with the pages coloured by owner.

### D5 [major] How LLM inference is laid out on a Galaxy
**What is missing.** The chapter gives one tok/s figure and one quiz answer ("weights mostly in GDDR6"). It says nothing about how 32 chips split a model.

**Why it matters.** The brief names this topic explicitly. It is also the most direct comparison with Cerebras's multi-wafer pipeline placement for inference.

**Source.** LLM §2.5.5–2.5.7 and §3.3, MESH §8, README (Llama 3.3 70B TP=32 table), `models/demos/llama3_70b_galaxy/README.md`, CCL.

**Proposed addition.** Add a section, "70B on 32 chips".
- **Topology.** A Wormhole Galaxy ("TG") is an 8×4 mesh of 32 chips, with four Ethernet links between neighbouring chips (MESH, Fig. 2). Collectives use 4 links along axis 0 and 3 along axis 1 (LLM §3.3.1). Newer Galaxy cabling is a torus, and the demo uses ring collectives by default (llama3_70b_galaxy README).
- **Tensor-parallel schemes** (LLM §3.3.5–3.3.8). Use a small diagram for each:
  - column-parallel (all-gather the input, output is width-fractured);
  - row-parallel (partial sums, then reduce-scatter);
  - column then row for the MLP, which moves the collective after FF2 so it handles [32,8k] instead of [32,28k];
  - 2D weight fracturing on TG: each chip holds a [K/4, N/8] block of every weight, with an all-reduce along `cluster_axis=1` after FF1/FF3 and along axis 0 after FF2.
  - On TG, all five Llama matmuls (QKV, dense-out, FF1, FF2, FF3) use 2D (LLM §3.3.10 table).
- **Collective cost** (LLM §3.3.9, CCL). Bottleneck bytes are (N−1)/N·T for all-gather and reduce-scatter, and 2(N−1)/N·T for all-reduce. Link line rate is 12.5 GB/s per direction on WH and 50 GB/s on BH. Measured per-hop latency is 711 ns on WH and 515 ns on BH for the 1D fabric. Fixed per-call cost is a few microseconds, and at 8 devices about three quarters of it is barriers (CCL, vendor-measured).
- **Two ways to use the same box** (vendor). This makes a good teaching table.
  - One replica, TP=32: Llama 3.3 70B, batch 32, 72.5 tok/s/user, 2,269 tok/s, TTFT 53 ms (README).
  - Four replicas, each TP=8 on a 2×4 submesh: Llama 3.1 70B, batch 128, 14.3 tok/s/user, 1,835 tok/s (MESH §8.2).
  - The point: tensor parallelism buys per-user speed, while data parallelism over submeshes buys throughput.
- **Derived roofline check** (`tag derived`, with assumptions stated):
  - 70B parameters in BFP8 at about 1.06 B/param (8 bits plus one shared exponent per 16 values, from DFMT) is about 74 GB, or about 2.3 GB per chip.
  - At 288 GB/s per Wormhole chip that is about 8 ms per token, so the weight-read ceiling is about 125 tok/s/user.
  - The measured 72.5 tok/s/user is about 58% of that ceiling. The rest goes to KV-cache reads, collectives and op gaps.
  - Note that some MLP weights may be BFP4, which would raise the ceiling.
  - This is the derivation pedagogy finding P8 asked for.
- **Why batch 32.** One 32-row tile holds 32 users, and smaller batches are padded to it (LAYOUT, MATENG). This explains why "decode supports batches up to 32".

Visual: an 8×4 chip grid in which clicking a weight matrix shows its [K/4, N/8] block on each chip and animates the all-reduce along a row and a column. This ties in with visuals proposal N5.

### D6 [major] Multi-chip mechanics and TT-Fabric
**What is missing.** The chapter has a single row, "Ethernet on every die, switchless meshes", plus the research-note mention of "EDM" and "tt-Fabric".

**Why it matters.** Scale-out is half of Tenstorrent's design argument, and the comparison with SwarmX/MemoryX in chapter 8 needs a mechanism, not a label.

**Source.** FABRIC §1–§6, CCL, GUIDE ("Scaling beyond one chip", "Fast dispatch").

**Proposed addition.** Add a subsection, "From NoC to fabric".
- **Where it runs.** The fabric router is firmware on the Ethernet tiles' RISC-V cores: one core per Ethernet tile on Wormhole, two on Blackhole (FABRIC §3).
- **Programming model.** "NoC operations are packetized, transported to the target chip, and executed remotely". A destination is {MeshId, ChipId} + NoC (x,y) + offset, so a remote write looks like a NoC write with a longer address (FABRIC §4). Commands include unicast and multicast, write, atomic increment, fused write+increment, inline write and scatter write.
- **Layers.**
  - L2 "TT-link" mode adds a 16-byte header with Go-Back-N retransmission, so upper layers never see CRC loss.
  - L3 uses source routing inside a mesh. Each mesh-entry router rewrites the route for the next mesh.
  - Routing is dimension-ordered within a mesh to avoid deadlock, and rings and tori use bubble flow control: a packet is injected only if the next hop has at least 2 free slots.
  - A separate control virtual channel carries control messages.
  - PCIe acts as an out-of-band control plane that can reroute traffic around dead links (FABRIC §1.1, §2, §6).
- **Scale.**
  - Routing planes: 4 Ethernet links per direction on WH and 2 on BH, with each "first port" plane kept separate.
  - Up to 1024 meshes of 256 devices each, about 250k devices in total (FABRIC §2.2).
- **Router buffers.** A 1D router has two sender channels of 8 slots (local and pass-through) and one 16-slot receiver channel (FABRIC §3.1.1). Fabric payload is 4,352 B by default, about 96% wire efficiency (CCL).
- **n300 detail.** The R chip is reached through the L chip over Ethernet. Fast dispatch runs one RISC-V per command queue on a spare Ethernet core (GUIDE), so a remote chip's dispatch traffic uses Ethernet routing planes (CCL, "Links available").

Visual: a three-level zoom from Tensix → chip (NoC, with Ethernet tiles at the edge) → Galaxy 8×4 mesh → multi-Galaxy mesh-of-meshes, with one packet's path drawn at each level.

### D7 [major] Peak-FLOPS derivation that resolves the chapter's "conflicting" figures
**What is missing.** The product-table caption says Blackhole peaks of 745, 774 and 664 "conflict".

**Why it matters.** All three are consistent with a single formula. Showing that teaches more than flagging the conflict, and it lets the course tag these figures `derived` with confidence.

**Source.** GEMM, MATENG (4096 FLOP/cycle per core, LoFi).

**Proposed addition** (`tag derived`):
- 140 cores × 4096 × 1.35 GHz = **774 TF**, the pre-firmware p150 figure.
- 120 cores × 4096 × 1.35 GHz = **664 TF**, the post-February-2026 p150 figure.
- 140 × 4096 × 1.30 GHz = **745 TF**, the Hot Chips 2024 figure, consistent with an earlier clock target.
- These are LoFi, BlockFP8-class peaks. HiFi2 halves them and HiFi4 quarters them, giving 332 and 166 TF on a 120-core p150.
- Vendor-measured tuned matmul reaches about 580 TF on 130 cores (GEMM), which is 81% of 130 × 5.53 TF.

Replace the caption's "conflict" sentence with this short derivation. Wormhole and Grayskull marketing figures do not fit the formula cleanly. Say so, and do not force them.

### D8 [minor] Inside the compute pipeline: SrcA/SrcB, Dst halves, and why "8 tiles"
**What is missing.** The chapter states that "DST holds 8 BF16 tiles or 4 FP32 tiles" without explaining why, or what `tile_regs_*` does.

**Why it matters.** This is the in-core analogue of the circular-buffer double buffering the widget teaches. It is where unpack, math and pack actually overlap.

**Source.** ISA-TC README/SrcASrcB/Dst, MATENG ("DstSync::Half"), GUIDE.

**Proposed addition.**
- Dst is 1024 rows × 16 columns of 16-bit data, which is 16 BF16 tiles' worth, or 512 × 16 in 32-bit mode.
- In the default `DstSync::Half` mode, Math fills one half (8 BF16 or 4 FP32 tiles) while Pack drains the other.
- `tile_regs_acquire`/`commit` are the Math side of that handshake, and `tile_regs_wait`/`release` are the Pack side.
- SrcA and SrcB each have two banks, so the unpackers fill one bank while the FPU consumes the other.
- The RISC-V cores do not fetch Tensix instructions for the coprocessor. They *push* 32-bit custom instructions into three in-order frontends (T0/T1/T2), and a MOP/Replay expander turns one push into many instructions so the backend sees about one instruction per thread per cycle (ISA-TC README).

Diagram: L1 → Unpack0 → SrcA[2], L1 → Unpack1 → SrcB[2], then FPU → Dst[half A | half B] → Packers → L1, with the SFPU reading and writing Dst through LRegs.

### D9 [minor] Math fidelity and block floating point mechanics
**What is missing.** The chapter says only that LoFi, HiFi2 and HiFi4 "trade accuracy for throughput".

**Why it matters.** This is a concrete, unusual hardware trade-off, and it explains the 2× and 4× performance steps in D7.

**Source.** MATENG, DFMT, GEMM.

**Proposed addition.**
- The multipliers are 5-bit × 7-bit, using the hidden bit plus 4 mantissa MSBs of SrcA and the hidden bit plus 6 MSBs of SrcB.
- Each fidelity phase is one more pass over a different slice of the mantissa bits. LoFi is 1 pass, HiFi2 is 2, HiFi3 is 3 and HiFi4 is 4, so cycles per tile are 16, 32, 48 and 64.
- BFP8, BFP4 and BFP2 share one exponent across 16 values, rounding to nearest-even after normalising to the shared exponent (DFMT). The research notes had this as unverified; it is now confirmed.
- `packer_l1_acc` lets the packer accumulate into L1 at higher precision, and `fp32_dest_acc_en` halves Dst capacity (MATENG).
- A small widget could show one bf16 value split into its LoFi/HiFi bit slices.

### D10 [minor] Dispatch, command queues, tracing and op-to-op gaps
**What is missing.** The chapter does not say how the host launches work.

**Why it matters.** At microsecond-scale op times, dispatch overhead determines decode latency. This is the counterpart to the Cerebras host-I/O chapter (07).

**Source.** GUIDE (Fast dispatch), LLM §4.1–4.2 and §4.5.5, GEMM (trace on/off).

**Proposed addition.** Add a short paragraph and a timeline diagram.
- Fast dispatch uses one RISC-V per command queue on a spare Ethernet core.
- There are two in-order CQs, CQ0 for compute and CQ1 for I/O, synchronised by `enqueue_record_event` / `enqueue_wait_for_event`.
- Trace capture and replay removes host overhead.
- A full decode pass takes about 10 ms, built from ops that each take microseconds (LLM), so gaps between ops matter.

### D11 [minor] Tilize, faces, padding and supported tile shapes
**What is missing.** The chapter covers only the "32×32 tile, 2,048 B" fact.

**Why it matters.** Padding cost is a real inefficiency, for example a 48×1024 tensor becomes 64×1024. Faces explain the memory order inside a tile.

**Source.** LAYOUT §3.2, GUIDE ("Native tile based computing"), DRAMBW (Future Work).

**Proposed addition.**
- The hardware supports 32×32, 16×32, 4×32, 2×32 and 1×32 tiles. Metalium mostly uses 32×32.
- A tile's memory order is face0 → face1 → face2 → face3, each face 16×16 row-major.
- Tilize and untilize run on the device.
- Uneven sharding across 12 banks wastes bandwidth, which is the reason smaller tiles are being considered (DRAMBW).

### D12 [minor] One worked example of explicit scheduling: causal FlashAttention load balancing
**What is missing.** The chapter has no example of a scheduling decision that the programmer, rather than the hardware, makes.

**Why it matters.** This shows the "no hardware scheduler" philosophy paying off, using a well-known kernel.

**Source.** FA §3.1.2, LLM §2.4.

**Proposed addition.** Give three sentences and a small picture.
- Q is chunked across cores. With causal masking, later chunks do more work.
- Each core takes one "low" and one "high" chunk (Q0 with Qn−1, Q1 with Qn−2, and so on), which balances the work perfectly and gave a 1.6× speedup (FA, vendor-measured).
- Flash-decode gains nothing beyond 16 cores per head batch (LLM).

## Out of scope for this chapter (new-chapter or cross-chapter ideas)
- **Chapter 4 (fabric) cross-link.** Put the Tenstorrent rectangle-multicast-with-semaphores pattern (D2) beside Cerebras colour broadcast and multicast routes, as a side-by-side "one-to-many" figure that both chapters reference.
- **Chapters 11/12 cross-link.** Compare the SUMMA/GEMV mapping on the wafer with the 2D multicast matmul on Tensix (D1): the same systolic idea at a different grain (a 32-bit wavelet compared with a 2–16 KiB packet).
- **Chapter 1 roofline.** Add a p150 point at 664 TF LoFi over 512 GB/s, giving a ridge at about 1,300 FLOP/B (`derived`), and a Wormhole Galaxy point. Reuse D5's weight-read ceiling as a second worked example of the memory wall.
- **Chapter 14 (GPU) cross-link.** Tensix reader/writer with CB handshakes is close to Hopper TMA plus warp-specialised producer/consumer with mbarriers, and Tensix multicast is close to TMA multicast within a thread-block cluster. Both chapters could share one table.
- **Chapter 15 (comparison).** Add a collective-cost row using CCL figures (12.5 or 50 GB/s per link, 0.5–0.9 µs per hop) beside NVLink and Cerebras inter-wafer numbers. Also add the "TP=32 vs 4×TP=8" table (D5) as the general latency-versus-throughput trade-off.
- **Possible new optional chapter, "Lab: Tenstorrent kernels in ttsim".** tt-isa-documentation names `ttsim` as the official ISA simulator. A lab could run the vector-add triplet and the single-core matmul, mirroring chapter 10, if ttsim can be installed in the container. Feasibility has not been checked.
- **Chapter 8 (systems).** TT-Fabric's PCIe control plane with automatic rerouting is a direct contrast with Cerebras system-level fault handling and could go in a "reliability at scale" sidebar.
- **Research notes update.** The notes should record that the CB API names are now confirmed (GUIDE), that the BFP shared-exponent block size of 16 is confirmed (DFMT), and that the Blackhole clock is 1.35 GHz (GEMM, ISA-NOC). These were all listed as gaps.
