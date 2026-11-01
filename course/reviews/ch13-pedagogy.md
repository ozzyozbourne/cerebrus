# ch13 · pedagogy review

Summary: The chapter is short (about 100 lines of prose) and covers the right topics: product line, Tensix anatomy, reader/compute/writer, a comparison table and caveats. As teaching material it is thin. Most core terms (tile, NoC, NIU, flit, CB, DST, SrcA/SrcB, unpack/pack, BFP, fidelity, sharded/interleaved, multicast, TT-NN/Forge) appear only as labels or not at all. Nothing traces a single op end to end, and the comparison with Cerebras stays at the level of table rows. The one interactive widget is broken: every CB size gives the same timeline (t = 29), while the readout text says one slot serialises the stages. This teaches the wrong lesson on the chapter's main mechanism. The quiz checks recall, not reasoning.

## Findings

### P1 [critical] Double-buffering widget shows no difference between 1, 2 and 4 tiles
- **Location:** `#cb` widget, `sim()` in the inline script (lines 124–148).
- **Problem:** The model frees an input-CB slot when compute *starts* a tile (`cp[k-cap][0]`) and frees an output slot when the writer *starts* (`wr[k-cap][0]`). In Metalium, `cb_pop_front` runs after the consumer is done with the tile. Because of this, a 1-slot CB behaves like a deep queue. I ran `sim()` under node and got the same result for every size: CB 1 → t = 29, CB 2 → t = 29, CB 4 → t = 29, with identical reader start times. The readout still says "With one slot … stages serialise."
- **Why it matters:** Double buffering is the chapter's only hands-on mechanism, and the learner sees text that contradicts the picture. Anyone who looks closely learns either nothing or the wrong thing. It also weakens Quiz Q2.
- **Concrete fix:** Release slots at the consumer's end time: `rStart = max(rd[k-1][1], cp[k-cap][1])` and `cStart = max(rd[k][1], cp[k-1][1], wr[k-cap][1])`. With 3/3/2 durations, CB 1 should then come out clearly slower than CB 2, and CB 4 about the same as CB 2. Add sliders for reader/compute/writer time so the learner can see that the slowest stage sets throughput, and that deeper buffers only help when stage times jitter. Print the speedup in the readout (e.g. "CB 1: 8 tiles in 48; CB 2: 29 → 1.66×"), and show slot occupancy as small boxes above each CB.

### P2 [major] No end-to-end worked example of one op
- **Location:** "Programming: reader, compute, writer" section (line 67).
- **Problem:** The kernel model is described in a single paragraph. No code or pseudocode appears, and the CB handshake calls are missing (`cb_reserve_back` / `noc_async_read` / `noc_async_read_barrier` / `cb_push_back` / `cb_wait_front` / `cb_pop_front`), even though the research notes (tenstorrent.md §4) give the canonical triplet. The learner never follows a tile from DRAM to L1, through the unpack → FPU → DST → pack path, back to L1 and out to DRAM.
- **Why it matters:** The Cerebras chapters teach through real programs (Labs 10–12). Without a matching trace, the learner cannot really compare the two programming models, and the second objective ("Explain the reader / compute / writer kernel model") is only half supported.
- **Concrete fix:** Add a section titled "One tile, end to end: element-wise add C = A + B". Include (a) three short side-by-side pseudocode panels for reader, compute and writer with the CB calls above, labelled with which RISC-V runs each (BRISC/NCRISC/TRISC0-2). (b) A numbered step diagram, ideally a stepper widget: host `SetRuntimeArgs` → reader `noc_async_read` from an interleaved DRAM bank over NoC 0 → `cb_push_back(c_0)` → TRISC0 unpacks into SrcA/SrcB → TRISC1 FPU add into DST → TRISC2 packs to `c_16` → writer `noc_async_write` over NoC 1. (c) Byte counts: a 2,048 B BF16 tile fits in one 8 KiB packet, which is 64 data flits of 32 B, about 64 cycles of link time plus ~9 cycles per hop <span class="tag derived">derived</span>. (d) A CSL version of the same add beside it (wavelets arriving on a color trigger a task, then a DSD add), so the difference is concrete.

### P3 [major] Core jargon used without definition
- **Location:** Throughout, especially the figure and the bullets after it (lines 40–64), plus the comparison table.
- **Problem:** Several terms appear without explanation:
  - **NoC**: never expanded or explained. "NoC 0 reads (convention)" and "two 2-D torus networks, opposite directions" appear without saying what a torus is (wrap-around edges) or why there are two networks.
  - **Tile**: used for the 32×32 data unit. The Tenstorrent ISA docs and the research notes also use "Tensix tile", "DRAM tile" and "Ethernet tile" for grid locations. The chapter neither defines the term nor warns about the double meaning.
  - **Circular buffer / CB**: never defined as an L1 FIFO of fixed-size pages with producer/consumer counters. "Up to 32 per core" and IDs such as c_0/c_16 are left unexplained.
  - **Unpack / pack**: the learner is not told that unpackers move tiles from L1 into the FPU's source registers (SrcA/SrcB), converting format on the way, or that packers write results from DST back to L1.
  - **DST**: "destination register holds 8 BF16 tiles" is given without saying why that matters. It caps how many output tiles a compute kernel can accumulate before packing.
  - **Block floating point**: block size, exponent width and the bytes-per-element saving (≈1 B for bfp8_b vs 2 B for BF16) are not given. The link to DRAM-bound decode is not made.
  - **LoFi/HiFi2/HiFi4**: "fidelity knobs" does not explain that these are FPU passes over mantissa bits.
  - **SFPU, RV32IM, flit, NIU, GDDR6, BlockFP8, "switchless meshes", "dynamic packets"**: none explained.
  - **TT-Metalium vs TT-NN / TT-Forge**: only Metalium is named. The learner does not learn that most users never write kernels.
- **Why it matters:** The audience is strong but new to Tenstorrent. These terms are what you need to read any Tenstorrent material, and the chapter does not define them.
- **Concrete fix:** Add a compact glossary callout after the anatomy figure, one line per term with the definitions above. Draw SrcA/SrcB/DST inside the coprocessor box with arrows L1 → unpack → SrcA/B → FPU/SFPU → DST → pack → L1. Add a callout: "‘Tile’ means two things: a 32×32 block of data, and a grid location on the chip (Tensix tile, DRAM tile). This chapter uses ‘core’ for the second." Add a short stack diagram: TT-Forge/TT-XLA → TT-MLIR → TT-NN → TT-Metalium → LLK.

### P4 [major] No picture of the whole chip; the NoC's behaviour is not shown
- **Location:** Between "The product line" and "Inside a Tensix core".
- **Problem:** The learner sees one core but never the chip: the 14×10 Tensix grid, the DRAM tiles along the edges, Ethernet tiles, PCIe and ARC, all on two tori. The chapter never shows how a read reaches DRAM, what "interleaved across DRAM banks" vs "sharded in L1" means, or what multicast looks like (rectangular, with strided and L-shaped on Blackhole). Harvesting (140 → 130 → 120 cores) is mentioned in the table footnote but not explained.
- **Why it matters:** Chapter 4 (fabric) gave the learner a detailed mental model of the Cerebras mesh. Without a chip-level view, they cannot compare networks. The table row "~1 cycle/hop vs ~9 cycles router-to-router" then has no context: Tensix moves 32 B/flit in large packets, and the wafer moves 4 B wavelets.
- **Concrete fix:** Add an SVG chip floorplan (schematic, labelled as such) with an animated or toggleable packet path: a NoC 0 read from a DRAM tile into core (3,2), a NoC 1 write back, and a rectangular multicast of one weight tile to a 4×4 block. Annotate with link bandwidth: 32 B/cycle ≈ 32 GB/s per link per direction at ~1 GHz <span class="tag derived">derived</span>. Add one sentence each on interleaved vs sharded tensors and on harvesting.

### P5 [major] Cerebras comparison is a list of rows, not an explanation
- **Location:** "Tensix vs the Cerebras PE" table and the paragraph after it (lines 81–92).
- **Problem:** The table lists numbers side by side, but they are not comparable as given. ~900,000 vs 120 compares units roughly 30× different in SRAM and of very different area. The paragraph's single takeaway ("difference is grain") is stated but never worked through. Several contrasts are missing:
  - total SRAM per device (WSE-3 44 GB vs p150 180 MB vs Galaxy 6.2 GB);
  - aggregate on-chip bandwidth;
  - how a matmul is mapped on each (systolic wavelet streams across PEs vs tiles DMA'd into a core's L1 and multicast);
  - the different synchronisation styles (data-triggered tasks vs CB counters polled by kernels);
  - static routes vs dynamic addressed packets, and what each costs the programmer.

  "Off-chip memory: none on the wafer" also skips MemoryX, which Chapter 8 introduced and Chapter 15 mentions.
- **Why it matters:** Comparing Tenstorrent with Cerebras is the reason this chapter exists in the course. A learner who has just finished CSL needs an explicit map along the lines of "X in CSL corresponds to Y in Metalium".
- **Concrete fix:**
  - Add a "CSL ↔ Metalium" concept-mapping table: color/route ↔ NoC address + packet; wavelet ↔ flit/tile; task activated by data ↔ kernel loop blocking on `cb_wait_front`; DSD ↔ unpack/pack + tile ops; `memcpy` host streams ↔ `EnqueueWriteMeshBuffer`; layout.csl `@set_rectangle` ↔ core-range + `SetRuntimeArgs`.
  - Add a "same matmul, two machines" diagram for one 1024×1024 BF16 layer: count PEs vs cores used, where the weights sit, and how many bytes cross the network.
  - Add per-device total-SRAM and memory-bandwidth rows, with tags.
  - Change the off-chip row to "none on the wafer; MemoryX for training weight streaming (Ch. 8)".

### P6 [minor] Quiz is recall-only and Q3 oversimplifies Cerebras
- **Location:** "Check yourself" (lines 102–107).
- **Problem:** Q1 and Q2 repeat sentences from the text. None of the questions makes the learner reason about a mechanism: deadlock if the reader and compute CB sizes don't match, what happens with a 48×1024 tensor, or why there are two NoCs. Q3's answer says Cerebras "pins weights in SRAM". That holds for Cerebras inference (Ch. 8), but a 70B model needs multiple wafers, and training streams weights. The quiz states neither.
- **Why it matters:** Recall questions give false confidence. Q3 also hides a nuance that Chapter 8 teaches.
- **Concrete fix:** Replace or add the following:
  - "A 48×1000 BF16 tensor: how many tiles, and how many bytes after padding?" (pads to 64×1024 → 2 × 32 = 64 tiles × 2,048 B = 128 KiB).
  - "Your reader pushes 1 tile per iteration but compute waits for 2 on a CB sized for 1. What happens?" (deadlock).
  - "Estimate Llama-70B decode tok/s for one Blackhole Galaxy from 16 TB/s and bfp8 weights" (~70 GB/token → ~230 tok/s upper bound for batch 1 if perfectly parallel; compare with the vendor figure).
  - "Translate this CSL fragment's control flow into Metalium terms."
  - Edit Q3's answer to say "…unlike Cerebras inference, which spreads a 70B model's weights across the SRAM of several wafers (Ch. 8)".

### P7 [minor] Product table is hard to read and mixes units
- **Location:** Product line table (lines 25–36).
- **Problem:**
  - The On-chip SRAM row mixes totals (120 MB, 180 MB) with a per-core value for Wormhole ("~1.43 MiB / core").
  - The Wormhole "128 (2 dies)" has no note that each die has 80 grid slots, of which 64 are active.
  - The Scale-out row mixes port counts with topology ("8 × 4 mesh").
  - FP8, BlockFP8 and BF16 peaks are compared directly with no note.
  - Nothing tells the learner which column to focus on. Every later section uses Blackhole p150.
- **Why it matters:** The learner gets numbers without knowing which ones to keep in mind.
- **Concrete fix:**
  - Put the n300 SRAM total in the same units as the other columns, and add a separate per-core row.
  - Highlight the p150 column as "the chip used for the rest of this chapter".
  - Add a one-line note that BlockFP8 is a block-floating-point format (see glossary) and is not the same as FP8 E4M3.
  - Move the topology into its own row.

### P8 [minor] Performance section has no derivation tying it back to the memory wall
- **Location:** "Performance and caveats" (lines 94–100).
- **Problem:** The memory-wall quote appears, but no back-of-envelope calculation follows. For example: 70B params × ~1 B (bfp8) ≈ 70 GB per token at batch 1. At 16 TB/s aggregate that gives an upper bound of ~230 tok/s per user, against the vendor's 72.5 on Wormhole Galaxy. The Chapter 1 roofline method is not reused.
- **Why it matters:** The learner can't tell whether the vendor numbers are plausible, and can't see where BFP pays off. Chapter 1's tools go unused.
- **Concrete fix:** Add a small calculation callout, or reuse the Chapter 1 roofline widget with presets for p150 and Galaxy (bandwidth, peak). Tag the result <span class="tag derived">derived</span>, and say why measured results fall below the bound (Ethernet hops, KV-cache reads, op overheads).

### P9 [minor] Objectives and figure caption overpromise "what each RISC-V does"
- **Location:** Objectives (line 18), figure caption (line 58).
- **Problem:** The chapter only names the cores' roles. It never explains:
  - why a math operation needs three separate in-order cores: they are pipelined, and each one issues to a different hardware engine;
  - how the cores synchronise with each other (semaphores, CB counters in L1);
  - that one C++ compute source is compiled three times.

  The Tensix coprocessor's scalar unit (ThCon) is also missing from the figure.
- **Why it matters:** "Draw a Tensix core and explain what each does" is the first objective. Right now the learner can label the core but can't explain why it is built this way.
- **Concrete fix:**
  - Add 2–3 sentences: the cores are in-order RV32IM, single-threaded and do no heavy math; the unpack/math/pack split lets the three stages overlap like a hardware pipeline; the compiler splits one compute source into three binaries using `#ifdef`-style sections.
  - Add ThCon to the coprocessor row.
  - Connect the figure to the P2 worked example with matching colours.
