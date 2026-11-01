# ch01 · pedagogy review

Summary: The chapter starts in the right place. The memory wall is the correct motivation for wafer-scale, the roofline is well chosen, and the "comparison trap" callout is the most valuable idea on the page. However, the mental model it builds is inconsistent. The interactive roofline plots WSE-3 using its summed per-PE SRAM bandwidth, so decode at batch 1 reads as "100% of peak, compute-bound". Two sections later the callout says that number is not comparable. The chapter also never says that a roofline belongs to one memory level. It skips the capacity problem: a 70B model fits neither one H100 nor one WSE-3. And it never says that Cerebras swaps a bandwidth problem for a data-placement and communication problem, which is the bridge into Part II. Smaller issues: a wrong preset value, several undefined terms (PE, fabric, Tensix, dense, BlockFP8), no tokens/s worked example, and recall-level quiz questions.

## Findings

### P1 [critical] The roofline widget and the "comparison trap" teach opposite things, and "roofline per memory level" is never stated
- **Location:** "Two numbers describe every accelerator" (ridge-point definition), the Interactive roofline widget (chips array, WSE-3 entry `15.6e15, 21e15`), and the "The comparison trap" callout.
- **Problem:** The ridge point is defined against "memory bandwidth" without saying *which* memory. The widget then mixes levels. GPU and Tenstorrent use off-chip DRAM (HBM, GDDR6), but WSE-3 uses the sum of 900,000 private 48 KB SRAMs. The WSE-3 ridge comes out at 0.74 FLOP/B, so choosing WSE-3 with the "LLM decode, batch 1" preset reports "100% of peak → COMPUTE-bound". The callout then tells the learner that exactly this comparison is apples to oranges. The chapter never reconciles the two, and the widget hint ("using that chip's main working memory") is the only clue.
- **Why it matters to the learner:** The widget is the part people play with and remember. A learner leaves believing "WSE-3 makes decode compute-bound with no conditions", when that only holds if every weight already sits in the SRAM of the PE that uses it. The real lesson (a roofline exists per memory level, and the trick is which level your working set fits in) is the key to the rest of the course, and the chapter leaves it implicit.
- **Concrete fix:**
  1. After the roofline paragraph, add: "A roofline is always drawn for one level of memory. A GPU has several (registers, shared memory/L1, L2, HBM), each with its own bandwidth and so its own ridge point. The roofline that matters is the one for the level where your working set actually lives. For a 140 GB model on a GPU, that is HBM. The Cerebras bet, which this course examines, is to make the working set live in the level that is one cycle from the math."
  2. Change the widget hint to: "Each line uses the memory the chip's *working set* normally lives in: HBM or GDDR6 for the GPU and Tenstorrent, on-wafer SRAM for WSE-3. These are different memory levels. The WSE-3 line assumes every byte is already in the SRAM of the PE that uses it (see 'The comparison trap' below)."
  3. Add a fifth chip entry, "NVIDIA H100 · BF16 dense · shared memory/L1 (aggregate)", using a Derived bandwidth (for example ~33 TB/s; see P9). The learner can then see that a GPU's on-chip level also has a low ridge, but only for ~33 MB of data.
  4. When WSE-3 is selected, add to the readout: "(only if the data is resident in the using PE's 48 KB; see the comparison trap)".

### P2 [major] "Every byte is one cycle from the core that uses it" overstates the model and hides the real trade-off
- **Location:** Caption of the "Where does the working set live?" figure, and the last sentence of the comparison-trap callout.
- **Problem:** The caption says Cerebras "removes the hierarchy entirely: every byte is one cycle from the core that uses it." That holds only for bytes a PE owns. A byte needed by a different PE is fabric hops away, and Chapter 4 shows that moving it is the main cost. Also, Ch03 introduces a 512 B software cache on WSE-3, and Ch08 introduces off-wafer MemoryX, so "no hierarchy, no DRAM" will soon look contradicted. The chapter never states the trade-off that motivates Part II: Cerebras turns the memory-bandwidth problem into a data-placement and communication problem.
- **Why it matters to the learner:** This is the core mental model for programming the wafer (place data, then route wavelets). Without it, Chapters 3–6 look like a set of quirks rather than consequences of one design decision.
- **Concrete fix:** Replace the caption's second sentence with: "Cerebras's bet is to flatten the hierarchy on the wafer: every byte a PE *owns* is one cycle away. A byte owned by another PE is not. It must travel over the on-wafer network (the *fabric*, Chapter 4). So the hard problem moves from 'feed the math from DRAM' to 'put each piece of data on the PE that needs it, and move the rest between neighbours'." Then add one sentence under the callout: "Keep this trade-off in mind. Chapters 3–6 are mostly about how the wafer makes placement and neighbour-to-neighbour movement cheap."

### P3 [major] The capacity problem is shown but never named: 140 GB fits neither one H100 nor one WSE-3
- **Location:** Decode-versus-prefill figure ("140 GB (70B, fp16)"), the GPU row of the three-architectures figure ("80 GB"), the Cerebras row ("= 44 GB, no DRAM"), and the comparison-trap callout ("capacity at that speed").
- **Problem:** The example model is 140 GB. One H100 holds 80 GB and one WSE-3 holds 44 GB. A careful learner will notice that the running example fits on neither chip, and the chapter says nothing. The callout ends on "capacity at that speed" but never runs the numbers. "No DRAM" also conflicts with Ch08's MemoryX (DRAM plus flash outside the wafer).
- **Why it matters to the learner:** Capacity is the main weakness of SRAM-only designs and the reason Ch08 (multi-wafer, weight streaming) exists. Leaving it out makes the chapter read as marketing and breaks the "why" chain into Ch08.
- **Concrete fix:** Add a short paragraph after the comparison-trap callout: "Capacity cuts both ways. A 70B model in FP16 is ~140 GB of weights <span class=\"tag derived\">Derived</span>. That is more than one H100 (80 GB) and more than three times one WSE-3 (44 GB). GPUs split the model across several GPUs and still read it from HBM. Cerebras either spreads the weights across several wafers so they stay in SRAM (for fast inference), or keeps weights off-wafer and streams them in layer by layer (for training, Chapter 8). On-wafer means no DRAM *on the wafer*. It does not mean no DRAM in the system." Change "44 GB, no DRAM" in the SVG to "44 GB, no DRAM on-wafer".

### P4 [major] No worked example links bandwidth to tokens per second; the 1 FLOP/byte figure is asserted, not derived
- **Location:** "Why LLM decode lives on the slanted part", first paragraph.
- **Problem:** Objective 2 depends on this section, but (a) "about 1 FLOP per byte" is stated without the two-line derivation (2 FLOPs per multiply-add ÷ 2 bytes per FP16 weight). (b) "proportional to batch size" plus "batch 64 → 50–100 FLOP/B" leaves the learner wondering why it is not simply 64, since KV-cache reads are never mentioned. (c) The caption claims tokens/s "is set by memory bandwidth", but there is no calculation showing it.
- **Why it matters to the learner:** A strong technical learner wants to *compute* the bound. The tokens/s ceiling is the most transferable result in the chapter, and it explains why Cerebras is fast at single-stream decode.
- **Concrete fix:** Insert after the first paragraph:
  "**Worked example.** One multiply-add is 2 FLOPs, and an FP16 weight is 2 bytes, so batch-1 decode does 2 FLOP / 2 B = **1 FLOP/byte**. At batch *B* each weight serves *B* sequences, so intensity ≈ *B* FLOP/byte. In practice it is a bit lower, because each sequence also reads its own attention KV cache, which batching does not share. That is why batch 64 lands at ~50–100 rather than exactly 64. Because each token must stream every weight once, single-stream speed is capped at *bandwidth ÷ model bytes*. An 8B model in FP16 (16 GB) on one H100 gives 3.35 TB/s ÷ 16 GB ≈ **210 tokens/s at most** <span class=\"tag derived\">Derived</span>, whatever the FLOP count. Make the bandwidth 1,000× larger and the cap rises 1,000×, until compute or communication becomes the limit."

### P5 [major] Wrong vector-add preset, and intensity defined as bytes "read" only
- **Location:** Arithmetic intensity definition ("for each byte it reads") and widget preset `<option value="-0.6">Vector add (0.25 FLOP/B f32)</option>`.
- **Problem:** Element-wise `c = a + b` in f32 does 1 FLOP, reads 8 bytes, and writes 4. Its intensity is 1/12 ≈ **0.083 FLOP/B** (0.125 if writes are ignored). It is never 0.25. The definition also counts only reads, which is non-standard: roofline traffic counts bytes moved to *and* from the memory level.
- **Why it matters to the learner:** The preset is wrong by 3×, and a learner who checks it will lose trust in the other numbers. Counting reads only is also a habit that breaks on write-heavy kernels such as stencils (Lab 3).
- **Concrete fix:** Change the definition to "how many floating-point operations it performs for each byte it moves between the math units and the memory in question (reads plus writes)." Change the preset to `<option value="-1.08">Vector add c=a+b (1 FLOP / 12 B ≈ 0.083 FLOP/B, f32)</option>`. Also note that this value is below the slider minimum of −1, so either set `min="-1.2"` and `xmin = -1.2`, or use `value="-1"` with the label "~0.1 FLOP/B".

### P6 [major] Core terms used before they are defined
- **Location:** Throughout: "PE math" and "PE" (three-architectures figure, callout, quiz), "Tensix", "the fabric (Chapter 4)" (quiz answer), "dense BF16" and "FP16 dense", "BlockFP8", "FP4", "RF+L1/smem", "SM", "SXM", "Rubin", "decode" (prefill gets a parenthetical, decode does not).
- **Problem:** The learner is new to Cerebras and Tenstorrent. PE, Tensix, and fabric are the three most important nouns in the course, and here they appear with no gloss. "Dense" only makes sense once sparse marketing figures are explained, and that happens in Ch02.
- **Why it matters to the learner:** Each undefined noun is a speed bump in a chapter meant to set up the vocabulary for the next fourteen.
- **Concrete fix:** Add a compact "Terms used here" box (a `.callout`) after the objectives:
  "**Decode / prefill:** generating one new token per step / processing the whole prompt at once. **Dense FLOP/s:** peak with no assumed zero-skipping. Vendors often quote 2:4 "sparse" figures that are 2× higher (Chapter 2). **BF16, FP8, FP4, BlockFP8:** 2-, 1-, ½-byte number formats. BlockFP8 is Tenstorrent's FP8 variant with a shared exponent per block. **SM:** an NVIDIA streaming multiprocessor, the GPU's core (132 on H100). **RF / smem:** register file / shared memory inside an SM. **HBM / GDDR6:** DRAM stacked beside the GPU die / ordinary graphics DRAM on the board. **Tensix:** a Tenstorrent core. **PE (processing element):** one of the ~900,000 tiny cores on a Cerebras wafer, each with 48 KB of SRAM (Chapter 3). **Fabric:** the on-wafer network linking each PE to its four neighbours (Chapter 4)."

### P7 [major] "Check yourself" tests recall, not the objectives; nothing on capacity, other chips, or the tokens/s bound
- **Location:** The `.quiz` block.
- **Problem:** Q1 is a good computation. Q2 and Q3 restate sentences from the page. No question asks the learner to compute a ridge point (objective 1 says "compute a chip's ridge point"), compare two chips, apply the bandwidth bound, or reason about whether a model fits. Q1 is also ambiguous about whether output writes count (see P5).
- **Why it matters to the learner:** The quiz should confirm that the learner can use the model, especially the per-level and capacity reasoning that the later chapters assume.
- **Concrete fix:** Change Q1's stem to "…per 4-byte float it reads (ignore writes)…". Add:
  - "Compute the ridge point of a Tenstorrent Blackhole p150 (664 TFLOP/s BlockFP8, 512 GB/s GDDR6). Is batch-64 decode (~70 FLOP/B) compute-bound there?" Answer: "664e12 / 512e9 ≈ 1,300 FLOP/B. No, 70 is far below it, so the kernel is even more bandwidth-bound than on an H100 (ridge ≈ 295). This is why Tenstorrent relies on keeping data in its 1.4 MiB-per-core SRAM."
  - "What is the most tokens/s one H100 can generate for a single user on a 16 GB model, and what limits it?" Answer: "≈ 3.35 TB/s ÷ 16 GB ≈ 210 tokens/s. HBM bandwidth limits it, because every weight is streamed once per token."
  - "The widget shows WSE-3 decode at 100% of peak. What two assumptions make that true?" Answer: "(1) The whole model fits in on-wafer SRAM (44 GB, so a 70B FP16 model needs several wafers). (2) Each weight sits in the 48 KB of the PE that uses it, so no fabric transfer is needed. Breaking either assumption moves you off that roofline."

### P8 [minor] Intensity depends on number format, but the presets assume FP16 on every chip
- **Location:** Widget presets and the B200 "FP4" and Blackhole "BlockFP8" entries.
- **Problem:** "Decode, batch 1 (~1 FLOP/B)" is true for FP16 weights. With the B200 FP4 line selected, the same kernel is ~4 FLOP/B (½-byte weights), and ~2 FLOP/B at FP8. The widget implies the same x-position for every chip.
- **Why it matters to the learner:** It hides one of the two ways vendors close the gap, which is shrinking bytes per weight. The Rubin paragraph relies on exactly this point.
- **Concrete fix:** Add to the widget hint: "Presets assume FP16 weights. At FP8 an intensity doubles, at FP4 it quadruples, because each byte holds more weights." Optionally scale the preset by `2 / bytesPerWeight[chip]` on chip change.

### P9 [minor] The "fair counterpart" bandwidth for a GPU is asserted without a derivation
- **Location:** The comparison-trap callout: "aggregate register-file + shared-memory bandwidth, which is also tens to hundreds of TB/s Derived".
- **Problem:** The text is tagged Derived, but no derivation is shown, and the range spans 10×.
- **Why it matters to the learner:** The callout's whole point is to teach comparing like with like. Showing the arithmetic models that skill.
- **Concrete fix:** Add one line: "For example, shared memory/L1 delivers about 128 B per clock per SM. 132 SMs × 128 B × ~1.8 GHz ≈ 30 TB/s <span class=\"tag derived\">Derived</span> (verify per-SM figure against the Hopper whitepaper). The register file is faster again. So the like-for-like gap is closer to 21 PB/s vs a few hundred TB/s, about 100×, and the gap in *capacity at that speed* (44 GB vs ~66 MB, ~650×) is the bigger story."

### P10 [minor] The "7,000×" claim does not match the chapter's own numbers
- **Location:** The comparison-trap callout.
- **Problem:** 21 PB/s ÷ 3.35 TB/s ≈ 6,300×, not 7,000×. A learner who checks the arithmetic will be puzzled.
- **Concrete fix:** Append: "(With the H100 SXM's 3.35 TB/s the ratio is ≈ 6,300× <span class=\"tag derived\">Derived</span>. The marketing figure rounds up or uses a lower-bandwidth H100 variant.)"

### P11 [minor] "FLOPs grow much faster" is not quantified
- **Location:** The paragraph beginning "And the wall is getting taller".
- **Problem:** The bandwidth growth (5.7×) is given, but the FLOP growth is not, so the learner cannot work out the new ridge point.
- **Concrete fix:** Add: "Rubin is rated at ~50 PF NVFP4 for inference <span class=\"tag vendor\">Vendor</span>. That is ~50× the H100's 989 TF BF16, against 5.7× more bandwidth, so the ridge point rises from ~295 to ~2,600 FLOP/byte <span class=\"tag derived\">Derived</span>. Part of that is the format: an FP4 weight is a quarter of the bytes, so decode intensity also rises 4×. Even so, the gap widens."

### P12 [minor] The GPU row introduces "latency hiding" without separating latency from bandwidth
- **Location:** GPU row of the three-architectures figure: "Hides latency with thousands of threads."
- **Problem:** The chapter is about bandwidth. Threads hide *latency*, not a *bandwidth* shortfall. Without that distinction the learner may conclude that more threads fix decode.
- **Concrete fix:** Add a sentence to the "Three answers" section: "Note the difference between latency and bandwidth. Thousands of GPU threads hide the *wait* for each HBM access, but they cannot raise the *rate* at which HBM delivers bytes. A bandwidth-bound kernel stays bandwidth-bound however many threads it has."

### P13 [minor] The "package edge" marker is in the wrong place
- **Location:** GPU row of the three-architectures SVG (the dashed line labelled "package edge" between L2 and HBM3).
- **Problem:** HBM stacks sit *inside* the GPU package, on the interposer. What L2 and HBM are separated by is the *die* edge. The callout correctly says "off-chip".
- **Concrete fix:** Change the label text to "die edge".

### P14 [minor] The roadmap wording conflicts with later chapters and leaves out Chapter 7
- **Location:** "What this course covers".
- **Problem:** "The task model that replaces the instruction stream" is inaccurate. Tasks are still instruction streams. Ch03 and Ch05 say they replace the *main loop / program counter marching through main*. "Descriptors that replace loads and stores" also conflicts with Ch06 ("DSDs: loops as hardware"), because DSDs replace explicit loops and address arithmetic. Memory is still accessed. Host I/O (Ch07) is not mentioned.
- **Concrete fix:** Replace with: "…the task model that replaces a main loop (code runs when data arrives), the descriptors (DSDs) that turn whole loops over memory or the fabric into single instructions, how the host gets data on and off the wafer, and the systems that turn wafers into clusters."

### P15 [minor] "Three answers to the same wall" is a figure with no prose
- **Location:** The section "Three answers to the same wall".
- **Problem:** The lede promises that each architecture is "a different answer to that one problem", but the section is a single SVG with seven-word notes. It never states each strategy as a response to the roofline: GPU batches to raise intensity and adds HBM bandwidth; Tenstorrent keeps tiles in a large per-core SRAM and scales out over Ethernet; Cerebras makes the working set on-chip.
- **Concrete fix:** Add a three-bullet paragraph before the figure: "**GPU:** raise intensity (batching, fused kernels) and buy more HBM bandwidth each generation. **Tenstorrent:** keep tiles in a large per-core SRAM, stream from cheap GDDR6, and spread models over on-chip Ethernet. **Cerebras:** make on-chip SRAM big enough to hold the working set, so decode runs on the SRAM roofline, then pay for it in capacity and in moving data between PEs."
