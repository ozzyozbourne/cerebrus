# ch13 · accuracy review

Summary: The chapter follows the research notes and report closely, and most product-line numbers match the vendor snippets: p150 firmware cut, Galaxy 23 PF / 6.2 GB / 1 TB / 16 TB/s, n300 466 TF / 24 GB / 576 GB/s, and the tt-metal README table (72.5 t/s/u, 2268.8 t/s). The problems come from attaching Wormhole-generation facts to Blackhole. The column headed "Tensix core (Blackhole)" uses Wormhole's L1 size (1464 KiB; Blackhole has 1536 KiB), Wormhole's NoC flit and packet sizes (32 B / 8 KiB; Blackhole is 64 B / 16 KiB) and Wormhole's circular-buffer limit (32; Blackhole has 64). The p150 Ethernet entry overstates connectivity: the ASIC has 14 tiles, but only 8 are wired to ports on a p150. The double-buffering widget's model is also wrong, so 1-, 2- and 4-tile CBs all give the same time (t=29), which contradicts the text printed under it. A few provenance tags are too coarse: third-party and derived values are labelled "All Vendor", and several numbers have no tag. Verdict: sound overall, with 4 major fixes needed before publication.

## Findings

### A1 [major] Blackhole Tensix L1 is 1536 KiB, not 1464 KiB
- **Location:** Lede ("each with 1.4 MiB of SRAM"). SVG figure label "L1 SRAM · 1464 KiB". Comparison table, column "Tensix core (Blackhole)", row "Local memory": "1,464 KiB L1".
- **Problem:** 1464 KiB is the Wormhole value. The Tenstorrent ISA docs and the tt-metal device memory map give Blackhole 1536 KiB (1.5 MiB). That also matches the vendor's "180 MB / 120 cores = 1.5 MB" marketing. The tt-metal Blackhole Bring-Up guide (the notes' source) still says "1464 KB", but it is stale. The same error is in the research notes (§2) and the report (Ch13, Ch15 table).
- **Evidence:**
  - https://raw.githubusercontent.com/tenstorrent/tt-isa-documentation/main/WormholeB0/TensixTile/L1.md: "Each Tensix tile has 1464 KiB (Wormhole) or 1536 KiB (Blackhole) of scratchpad RAM … `TENSIX_SRAM_SIZE` = `1464*1024` (Wormhole) or `1536*1024` (Blackhole)".
  - https://raw.githubusercontent.com/tenstorrent/tt-isa-documentation/main/BlackholeA0/TensixTile/README.md: "Each Tensix tile contains: 1536 KiB of RAM called L1".
  - https://raw.githubusercontent.com/tenstorrent/tt-metal/main/tt_metal/hw/inc/internal/tt-1xx/blackhole/dev_mem_map.h line 33: `#define MEM_L1_SIZE (1536 * 1024)`. The Wormhole file has `(1464 * 1024)`.
- **Concrete fix:**
  - Lede: "each with about 1.5 MiB of SRAM (1464 KiB on Wormhole, 1536 KiB on Blackhole)".
  - SVG label: "L1 SRAM · 1464 KiB (WH) / 1536 KiB (BH) · software-managed, no caches".
  - Table cell: "1,536 KiB L1 (Wormhole: 1,464 KiB) <span class="tag vendor">tt-isa-documentation</span>".

### A2 [major] Blackhole NoC flits are 64 B and packets carry up to 16 KiB
- **Location:** Comparison table, "Tensix core (Blackhole)" column, row "Data unit": "32×32 tile; 32-byte NoC flits, packets up to 8 KiB".
- **Problem:** 32 B flits and 8 KiB packets are Wormhole figures. Blackhole doubled the flit width, which doubles the maximum packet payload. It also raised the NoC clock from 1 GHz to 1.35 GHz. The research notes listed this as a gap ("Blackhole NoC link width was not confirmed … assumed 32 B but unverified"). It is now verified, and the assumption was wrong. The report's Ch13 paragraph and Ch15 table repeat the error, and its derived "32 GB/s per link at 1 GHz" applies only to Wormhole. The Blackhole figure is 64 B × 1.35 GHz ≈ 86 GB/s.
- **Evidence:** https://raw.githubusercontent.com/tenstorrent/tt-isa-documentation/main/BlackholeA0/NoC/README.md: "Each flit consists of exactly 512 bits (64 bytes)", "very long packets use one header flit and 256 data flits to transport 16384 bytes of data", and "Compared to Wormhole … higher clock speed (1 GHz → 1.35 GHz), doubling of bandwidth per clock cycle (256 bits per flit → 512 bits per flit)". The router-to-router latency of 9 cycles is the same on both, so the "~9 cycles" cell is correct.
- **Concrete fix:** Data-unit cell: "32×32 tile; 64-byte NoC flits, packets up to 16 KiB (Wormhole: 32 B / 8 KiB) <span class="tag vendor">tt-isa-documentation</span>".

### A3 [major] p150 scale-out overstated: 14 Ethernet tiles on the ASIC, but only 8 connected on a p150
- **Location:** Product table, Blackhole p150 column, row "Scale-out": "14 × 400 GbE (paired as 800G)".
- **Problem:** 14 is the full-ASIC tile count. On a p150, 12 tiles are available and 8 are connected to 4 QSFP-DD 800 GbE ports. The remaining 4 cannot send or receive packets. The p100 has 0 Ethernet tiles.
- **Evidence:** https://raw.githubusercontent.com/tenstorrent/tt-isa-documentation/main/BlackholeA0/README.md:
  - "On p150 boards, there are four QSFP-DD ports, meaning that 8 Ethernet tiles are connected; the remaining 4 Ethernet tiles are not connected to anything".
  - Tile table: "Ethernet tile | p100 0 | p150 12 | Full ASIC 14"; "↳ with 400 GbE connected | 0 | 8 | 12".
  - "Each PCI Express 5.0 x16 connection reduces the number of connectable Ethernet tiles by four".
- **Concrete fix:** Cell: "4 × 800 GbE QSFP-DD (8 of the die's 14 × 400 GbE tiles wired)".

### A4 [major] Double-buffering widget gives identical results for 1, 2 and 4 tiles, contradicting its own text
- **Location:** Widget `#cb`, function `sim()`, lines 129 and 131.
- **Problem:** The model frees a CB slot when the consumer *starts* (`cp[k - cap][0]`, `wr[k - cap][0]`). In tt-metal, a slot is freed only when the consumer calls `cb_pop_front`, after it has finished with the tile. With the current model, a 1-tile CB already overlaps the reader with compute. Re-running the code gives t=29 for CB size 1, 2 and 4. The readout for size 1 still says "With one slot the reader cannot fetch tile k+1 until compute has consumed tile k: stages serialise", so the widget contradicts itself.
- **Evidence:**
  - Re-running the chapter's own `sim()` logic in node gives cap 1 → 29, cap 2 → 29, cap 4 → 29. Freeing at consumer end gives cap 1 → 50, cap 2 → 29, cap 4 → 29.
  - METALIUM_GUIDE.md (https://raw.githubusercontent.com/tenstorrent/tt-metal/main/METALIUM_GUIDE.md) says each CB holds "two or more tiles worth of data, enabling the reader kernel to fetch new data while the compute kernel processes the previous tile". That overlap is impossible with one slot.
- **Concrete fix:**
  - Line 129: `cp[k - cap][0]` → `cp[k - cap][1]`.
  - Line 131: `wr[k - cap][0]` → `wr[k - cap][1]`.
  - This gives 50 / 29 / 29. The fact that 4 tiles is no faster than 2 matches the guide's "diminishing returns" remark. Optionally append to the cap>1 readout: "Beyond two slots there is no further gain here, because every stage is already busy."

### A5 [minor] "Up to 32 circular buffers per core" is the Wormhole limit; Blackhole allows 64
- **Location:** Programming paragraph: "Circular buffers (up to 32 per core) synchronise them".
- **Evidence:** https://raw.githubusercontent.com/tenstorrent/tt-metal/main/tt_metal/hw/inc/api/circular_buffer_constants.h: "Wormhole has fewer CBs due to limited TRISC memory (2KB) - Blackhole supports the full CB count … #if defined(ARCH_WORMHOLE) NUM_CIRCULAR_BUFFERS = 32; #else NUM_CIRCULAR_BUFFERS = 64". The same file says CBs are "TEMPORARY … eventually will be replaced by Dataflow Buffers (DFBs)".
- **Concrete fix:** "Circular buffers (up to 32 per core on Wormhole, 64 on Blackhole) synchronise them".

### A6 [minor] "Ethernet ports on every die" is false for p100 and Grayskull
- **Location:** Lede ("Ethernet ports on every die link chips into meshes"). Comparison table, Scale-out row ("Ethernet on every die, switchless meshes").
- **Evidence:** BlackholeA0 README tile table: p100 "Ethernet tile 0". The chapter's own product table shows Grayskull scale-out as "—".
- **Concrete fix:**
  - Lede: "Ethernet ports built into the die (on Wormhole and on most Blackhole products) link chips into meshes."
  - Table cell: "on-die Ethernet (not on p100), switchless meshes".

### A7 [minor] n300 SRAM cell uses a different unit from its row neighbours
- **Location:** Product table, Wormhole n300 column, row "On-chip SRAM": "~1.43 MiB / core".
- **Problem:** The other cells in the row are per-device totals. The n300 total is 128 × 1464 KiB ≈ 183 MiB ≈ 192 MB. This value is derived; no vendor figure was found.
- **Concrete fix:** "~192 MB (128 × 1464 KiB) <span class="tag derived">Derived</span>".

### A8 [minor] n300 "16 × 100 GbE" is per die, not per card
- **Location:** Product table, n300 column, Scale-out row.
- **Problem:** The n300 has two dies, and some of each die's 16 tiles are unconnected. The card exposes 2 QSFP-DD ports. The docs say 400GbE and Flopper says 200G; the notes record this as unresolved.
- **Evidence:** WormholeB0 README (https://raw.githubusercontent.com/tenstorrent/tt-isa-documentation/main/WormholeB0/README.md): "16x Ethernet tile … Depending on the particular product, some of these tiles will not be connected to anything". Research notes §1: "n300 external Ethernet: docs say 2x QSFP-DD '400GbE'. Flopper lists 2x QSFP-DD 200G. Unresolved."
- **Concrete fix:** "16 × 100 GbE tiles per die; 2 × QSFP-DD on the card".

### A9 [minor] "All Vendor" caption covers third-party and derived values
- **Location:** Caption under the product table.
- **Problem:** Several cells are not vendor figures:
  - Galaxy "~12 kW" comes from Flopper, a third-party aggregator. The vendor page states no power figure.
  - p150 "~512 GB/s" is flagged in the notes as a "third-party figure" (Flopper).
  - Galaxy "~4,000" Tensix is arithmetic (32 × 120–140). No vendor states it.
  - Galaxy "8 × 4 mesh" comes from the tt-metal LLM report's description of the *Wormhole* Galaxy (TG), not Galaxy Blackhole.
- **Evidence:**
  - Research notes §1: "512 GB/s (third-party figure)" and "Flopper lists about 12.0 kW".
  - https://raw.githubusercontent.com/tenstorrent/tt-metal/main/tech_reports/LLMs/llms.md: "TG systems … `(8, 4)` device mesh" (Wormhole).
  - Web search of tenstorrent.com/hardware/galaxy: the official excerpt gives no power figure. Flopper lists "12.0 kW Total".
- **Concrete fix:**
  - Tag "~12 kW" and "~512 GB/s" as <span class="tag analyst">Third-party (Flopper)</span>, and "~4,000" as <span class="tag derived">Derived</span>.
  - Change Galaxy scale-out to "32 chips in a 2-D Ethernet mesh (8 × 4 on Wormhole Galaxy)".
  - Caption: "Vendor figures except where tagged otherwise, mostly from search extracts of spec pages."

### A10 [minor] DST-register capacity is a Wormhole statement
- **Location:** Tensix bullet: "The math engine's destination register holds 8 BF16 tiles or 4 FP32 tiles."
- **Evidence:** llms.md line 1568: "For example, Wormhole DST has eight tiles when accumulating in BF16 and four tiles when accumulating in FP32." No equivalent Blackhole statement was found.
- **Concrete fix:** "On Wormhole, the math engine's destination register holds 8 BF16 tiles or 4 FP32 tiles <span class="tag vendor">tt-metal LLM report</span>."

### A11 [minor] Baby-core ISA label: Blackhole cores are more than RV32IM
- **Location:** SVG: every baby core is labelled "RV32IM".
- **Evidence:** https://raw.githubusercontent.com/tenstorrent/tt-isa-documentation/main/BlackholeA0/TensixTile/BabyRISCV/README.md: "The full RV32IM instruction set is implemented, plus all of 'Zicsr' / 'Zaamo' / 'Zba' / 'Zbb', plus some … of 'Zicntr' / F / 'Zfh'. RISCV T2 additionally implements some … of V … running at a clock speed of 1.35 GHz."
- **Concrete fix:** Change the label to "RV32IM+", or add to the caption: "(RV32IM on Wormhole; Blackhole adds bit-manipulation, atomics and partial F/V extensions, at 1.35 GHz)".

### A12 [minor] Missing provenance tags on numeric claims
- **Location:**
  - The Tensix bullets: 2,048 B; 8/4 tiles; 32-lane.
  - The programming paragraph: 32 CBs.
  - The whole Tensix-vs-PE table.
  - The performance bullet "~512 GB/s per card".
  - The quiz answer "6.2 GB SRAM vs 140 GB of weights" (140 GB = 70B × 2 B is derived).
- **Problem:** The brief says "Every number should carry one."
- **Concrete fix:**
  - Add <span class="tag vendor">METALIUM_GUIDE / tt-isa-documentation</span> to the bullets and table rows.
  - Add <span class="tag derived">Derived</span> after "140 GB of weights" (70B params × 2 bytes, BF16).

### A13 [minor] Wormhole Galaxy benchmark context
- **Location:** Performance bullet 1.
- **Problem:** The numbers are correct. The source is the tt-metal README "Llama 3.3 70B (TP=32)" table, not MODEL_UPDATES as the report cites. That table also records the input length (128), the target (80 t/s/u) and the release (v0.65.0-rc7). These are useful caveats.
- **Evidence:** https://raw.githubusercontent.com/tenstorrent/tt-metal/main/README.md: "| 32 | Galaxy (Wormhole) | 53 | 72.5 | 80 | 2268.8 | v0.65.0-rc7" and "Reported LLM Performance: Based on an input sequence length of 128 tokens".
- **Concrete fix:** "Wormhole Galaxy, Llama 3.3-70B (TP=32, 128-token input): 72.5 tok/s per user, 2,269 tok/s total at batch 32, target 80 <span class="tag vendor">tt-metal README table</span>."

## Not verifiable
These could not be checked because docs.tenstorrent.com, tenstorrent.com, tomshardware.com and theregister.com were blocked or unresolvable from this session. They come from search extracts only:
- Grayskull e150: 332 TF FP8, 200 W, $799, 118 GB/s.
- p150 300 W.
- The "1–2%" impact claim. Search results agree, but the Tom's Hardware article text was not readable.
- The exact firmware version (v19.5.0) and the date.
- DeepSeek-R1 ~350 / ~308 tok/s/user, from Munich Startup and Futurum extracts.
- The Register's "trapped in a software blackhole" quote. Only the headline was confirmed, via the forum URL for the 2025-11-27 article.

Also unresolved:
- Whether Galaxy Blackhole is wired as an 8×4 mesh.
- Galaxy Blackhole's 23 PF, which is above 32 × 664 TF = 21.2 PF. It probably assumes pre-cut 140-core chips, but that is unconfirmed.
- No MLPerf submission exists as of this review. A negative claim like this cannot be fully proven.
