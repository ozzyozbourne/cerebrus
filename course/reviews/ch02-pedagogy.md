# ch02 · pedagogy review

Summary: The chapter is short and clear, and two parts work well: the reticle-to-wafer framing, and the defect simulator, which shows "small unit of failure" concretely. But it does not keep its own promise. The lede says it will cover "what that buys", and it never does: nothing links the wafer back to Chapter 1's memory wall. The cost side has the same gap. Only power and cooling are covered. The discarded wafer corners, the area spent on spares, and the lack of binning are never mentioned. The I/O paragraph says the physical rim causes the memcpy column reservation. That is the wrong cause, and it plants a model that Chapter 7 then contradicts. Smaller problems: several terms are used before they are defined (fabric, PE/core/tile, scribe line, SM, 2:4 sparsity, sparse FLOPs). The clock assumption (~1 GHz) differs from the SDK's 850 MHz used in Lab 3. There is no worked yield calculation. The quiz only asks for recall.

## Findings

### P1 [critical] The chapter never says what wafer-scale *buys*
- **Location:** Lede ("This chapter covers what that buys, what it costs…"). There is no section between "From reticle to wafer" and "The numbers".
- **Problem:** The chapter shows that a wafer *can* be one chip. It never says why you would *want* that. Chapter 1 ends with "Cerebras's bet is to remove the hierarchy entirely" and "capacity at that speed: 44 GB". Chapter 2 never picks up that thread. Nothing says that cross-die traffic, which on a GPU goes over SerDes, package links or NVLink, stays on short on-wafer wires here. The ~50:50 logic/SRAM area split goes unmentioned. So does the fact that this is how 44 GB of single-cycle SRAM fits on one chip. The B200's 10 TB/s die-to-die link appears only as "glue". It is never contrasted with the 214 Pb/s fabric.
- **Why it matters:** The chapter belongs to Part I, "Why wafer-scale". Without the benefit, the learner reads only a list of engineering obstacles (defects, power, I/O). They come away without knowing why anyone would take those obstacles on. The mental model has no motive.
- **Concrete fix:** Insert a new `<h2>What the wafer buys</h2>` right after the first figure, with roughly this text: "Keeping the wafer whole buys one thing above all: data never has to leave the silicon. On a GPU cluster, every byte that moves between chips crosses a package edge, a SerDes and a cable: NVLink gives an H100 about 0.9 TB/s. On the wafer, neighbouring cores sit less than 1 mm apart <span class="tag vendor">Vendor (Hot Chips 2022)</span>, and the fabric that links all of them carries 214 Pb/s ≈ 27 PB/s <span class="tag vendor">Vendor</span>, about 30,000× one H100's NVLink <span class="tag derived">Derived</span>. Area is the second gain. About half of each core is SRAM, so the wafer holds 44 GB of single-cycle memory: the 'capacity at that speed' from Chapter 1. A GPU cannot get that on one die, because one die stops at one reticle." Close by pointing ahead: "The rest of this chapter is the price of that bet."

### P2 [major] The I/O paragraph gives the wrong cause for the reserved columns and rows
- **Location:** "I/O lives on the rim" paragraph. Check-yourself Q3 answer.
- **Problem:** The paragraph reasons: data enters at the wafer edges, *so* the runtime reserves columns west and east of *your program*. Chapter 7 (and the SDK) say something different. With `--memcpy`, cslc generates extra *PE programs* in ordinary PEs around your rectangle (3 west and 2 east columns at `--channels 1`). The reservation is software infrastructure that runs on normal PEs. It is not hardware I/O circuitry. The paragraph also explains columns but not rows: the "2 rows shorter" is stated and never explained.
- **Why it matters:** A learner who believes this will expect the reserved region to sit fixed at the physical wafer rim. They will then be confused by `--fabric-offsets=4,1` and by the 8 × 3 simulator fabric in Chapter 7, where the "rim" sits next to a 1 × 1 program.
- **Concrete fix:** Replace the second sentence onward with: "That has a software consequence you will meet in Chapter 7. To get data from the edge to your PEs, the SDK's memcpy runtime compiles its own small programs onto ordinary PEs that frame your rectangle: a few columns on the west and east, plus a row above and below. Those PEs are not available to you. On a CS-2, then, your rectangle must be 7 columns narrower and 2 rows shorter than the 750 × 994 fabric: at most about 743 × 992 ≈ 737k PEs, against 850k marketed [SDK 2.10.1] [Derived]." In Q3's answer, replace "the I/O runtime reserves columns around your program" with "the memcpy runtime runs on PEs that frame your program (7 columns and 2 rows on a CS-2)".

### P3 [major] The cost side is incomplete: discarded corners and spare overhead are never mentioned
- **Location:** "Surviving defects" section, the simulator readout, and the "164×" paragraph.
- **Problem:** The "largest square" (46,225 mm²) uses only about 65% of a 300 mm wafer (70,686 mm²). Some 24,000 mm² of corner silicon is thrown away on *every* wafer, defect or not. Spare cores and links also cost area whether or not a defect ever uses them. The simulator compares "GPU mm² discarded" with "wafer-scale mm² replaced", which ignores both costs. It also makes the "164× less dead silicon" claim look like a free win. A third cost: every wafer must work, so there is no binning into cheaper SKUs.
- **Why it matters:** The lede promises "what it costs". A technically strong learner who works out the square-vs-circle area will feel misled. The honest trade (fixed, predictable overhead in exchange for no defect lottery) is the actual insight.
- **Concrete fix:** (a) After the "164×" paragraph, add: "The comparison leaves out two fixed costs. The square uses only about 65% of the round wafer, so about 24,000 mm² of corner silicon is never used [Derived]. And the spare cores and links take up area on every wafer, defective or not. Cerebras trades a small, predictable overhead for having no yield lottery at all." (b) Add a line to the simulator readout: `wafer-scale:  ~24,460 mm² of wafer outside the square is unused regardless of defects`, computed as `Math.PI*150*150 - 215*215`.

### P4 [major] No worked yield calculation: the "why" of redundancy is stated, never shown
- **Location:** "Surviving defects", first paragraph.
- **Problem:** "A wafer-scale chip cannot throw itself away" is asserted. The learner never sees the one-line arithmetic that makes it obvious. With randomly placed point defects, the probability that an area A has no defect is e^(−D·A).
- **Why it matters:** This is the decisive quantitative argument, and the learner can reuse it. Without it, "small cores + spares" reads as a design choice, not a necessity.
- **Concrete fix:** Add a `.callout` worked example before the simulator. "**Worked example: why spares are not optional.** Take Cerebras's own 0.001 defects/mm². A 26 × 32 mm GPU die (832 mm²) is defect-free with probability e^(−0.832) ≈ 44%. A 46,225 mm² wafer chip with *no* redundancy is defect-free with probability e^(−46) ≈ 10⁻²⁰: you would never ship one. With 0.05 mm² cores, the same 46 defects disable about 46 cores out of 900,000 (0.005%), and a modest pool of spares absorbs them [Derived, simple Poisson model]."

### P5 [major] "Sparse FLOPs" is never explained, only flagged
- **Location:** The "Read the FLOPs carefully" callout. Table row "Peak AI compute". Quiz Q2.
- **Problem:** The learner is told that 125 PF is "sparse", and is told to ask "sparse or dense?". The chapter never says what a sparse FLOP figure *means*: an effective rate that counts zero operations the hardware skips as if they were performed. The sparsity level it assumes is not stated either. "2:4-sparsity" for H100 is used without definition. The mechanism appears only in Chapter 3 ("Sparsity comes free with dataflow").
- **Why it matters:** Objective 1 is "quote the specs with the right caveats". The learner can say the word "sparse" but cannot judge the claim. For example, they cannot tell that 125 / 15.6 ≈ 8× implies the vendor counts about 8× the work actually done.
- **Concrete fix:** Add to the callout: "A *sparse* figure counts the multiply-adds the chip skips because an operand is zero, as if they had been done. Cerebras's dataflow cores skip zeros that are never sent (Chapter 3). The ratio 125 / ~15.6 ≈ 8 [Derived] means the headline assumes roughly 7 of every 8 operations are skipped. NVIDIA's '2:4 sparsity' is a fixed pattern of 2 zeros in every 4 weights, which is worth exactly 2×." Extend the Q2 answer with "…and the 8× ratio tells you how much zero-skipping the headline assumes."

### P6 [major] Clock assumption differs from the SDK's 850 MHz and from later chapters
- **Location:** Callout ("× ~1 GHz ≈ 14–15 PF"). Stat tile "none · official clock frequency published".
- **Problem:** The research report records that the SDK's own benchmarks assume 850 MHz, and Lab 3 (Chapter 12) converts cycles at 850 MHz. Chapter 2 uses ~1 GHz and the tile implies there is no number at all. The learner meets two different clocks with no link between them.
- **Why it matters:** This is a terminology and number mismatch with later chapters, and it undercuts the sanity check: at 850 MHz the estimate is 12.2 PF, not 14–15.
- **Concrete fix:** Change the tile label to "official clock published (SDK benchmarks assume 850 MHz)" with an SDK tag. In the callout, replace "× ~1 GHz ≈ 14–15 PF dense" with "× 0.85–1 GHz ≈ 12–14 PF dense (850 MHz is the SDK benchmarks' own assumption <span class="tag sdk">SDK 2.10.1</span>; no official clock is published)".

### P7 [major] Objectives 1 and 3 are only partly delivered
- **Location:** Objectives list.
- **Problem:** Objective 1 promises caveats for "vendor vs measured", but the chapter has no measured or independent numbers, only Vendor/Analyst/Derived. Objective 3 promises "how big that rectangle is", but the chapter gives only CS-2. It never says that the WSE-3 equivalent is not public.
- **Why it matters:** The learner cannot check off either objective, and may assume 750 × 994 holds for CS-3 too.
- **Concrete fix:** Reword objective 1 to "…(sparse vs dense FLOPs, vendor vs analyst estimates)". After the repair-figure caption or in the I/O paragraph, add: "The WSE-3 equivalent of 750 × 994 is not published in the SDK or anywhere we could find; expect the same kind of gap below 900k."

### P8 [major] The repair mechanism leaves an obvious question unanswered: are logical neighbours still physical neighbours?
- **Location:** The repair figure and caption. "…the fabric is configured at manufacturing time to route around bad cores."
- **Problem:** The figure shifts a row east into the spare column. The learner, who will soon read in Chapter 4 that "a hop takes about one cycle", will ask whether the shifted cores now sit two physical hops from their logical neighbours. The chapter also says the fabric is "configured", the same word Chapter 4 uses for the programmer's color routes (`@set_color_config`). Two very different configuration layers end up blurred together.
- **Why it matters:** These are the key internal-behaviour questions for this learner. Leaving them open lets them build a wrong timing model or confuse repair with routing.
- **Concrete fix:** Add to the caption: "Spare *links* exist so that a shifted core still reaches its logical neighbour; Cerebras says the result behaves as a uniform mesh, but the exact hop cost around a repair is not public. This repair mapping is fixed in hardware and invisible to software. It is not the per-color routing you will program in Chapter 4."

### P9 [minor] Jargon used before it is defined: fabric, PE/core/tile, scribe line, SM
- **Location:** Objectives ("rectangle of PEs"). First section ("on-chip network", "scribe lines", "fabric"). Table "Cores (PEs)". "1/100th of an H100 SM". "fabric positions".
- **Problem:** "Fabric" first appears in the figure caption and is defined only in Chapter 4. "PE" appears in the objectives before the table equates it with "core". Chapter 3 adds a third term, "tile". "Scribe line", "SM" and "fabric position" are never defined.
- **Why it matters:** These are small gaps, but they pile up for a learner new to both semiconductor manufacturing and Cerebras terms.
- **Concrete fix:** In "From reticle to wafer", change "the on-chip network" to "the on-chip network (Cerebras calls it the *fabric*: a 2-D mesh linking every core to its four neighbours, Chapter 4)". Change "across the scribe lines" to "across the *scribe lines* (the narrow strips between fields where a saw would normally cut)". At the first mention of cores, add: "Cerebras calls each core a *processing element* (PE); the course uses the two words interchangeably." Change "H100 SM" to "H100 SM (streaming multiprocessor, the GPU's core unit)". In the caption, change "750 × 994 fabric positions" to "750 × 994 fabric positions (PE slots with a router)".

### P10 [minor] The spec table mixes units and hides the cause of the WSE-3T doubling
- **Location:** Rows "Fabric bandwidth" and "Memory bandwidth". The WSE-3T column.
- **Problem:** Fabric bandwidth reads 220 Pb/s → 214 Pb/s (~27 PB/s) → 53.5 PB/s. That mixes bits and bytes, and the small *drop* from WSE-2 to WSE-3 is not explained. WSE-3T doubles memory bandwidth, fabric bandwidth and sparse FLOPs on "same silicon, higher clock". The learner is not told that this implies roughly a 2× clock, or that the figure is a press attribution (The Register).
- **Why it matters:** A careful learner will spend time converting units and may think the fabric got slower or that WSE-3T has new hardware.
- **Concrete fix:** Use one unit across the row: "27.5 PB/s (220 Pb/s) | 26.8 PB/s (214 Pb/s) | 53.5 PB/s". Add to the footnote: "WSE-3T's figures are almost exactly 2× WSE-3's on identical silicon, which implies a roughly doubled clock; the press attributes it to clock [Analyst], Cerebras has not said. The slight WSE-2 → WSE-3 fabric drop is as published and unexplained."

### P11 [minor] Missing analogy: GPUs harvest defects too, just at coarser grain
- **Location:** "Surviving defects", first paragraph ("a defect landing in a die usually kills or downgrades that die").
- **Problem:** The chapter presents redundancy as a Cerebras idea. An H100 SXM ships with 132 of the full GH100's 144 SMs enabled (Chapter 14 also gives 132 SMs). That is the same trick with ~6 mm² units instead of 0.05 mm² ones.
- **Why it matters:** Tying the idea to something the learner already knows makes the mental model stronger. "Same idea, 100× finer grain" is easier to remember than "new idea".
- **Concrete fix:** After "…the more silicon goes with it", add: "GPUs already soften this with spares: an H100 SXM enables 132 of its die's 144 SMs [Vendor], so a defect in an SM costs one SM. Cerebras pushes the same idea about 100× finer."

### P12 [minor] Quiz is recall-only and Q3's answer overstates certainty
- **Location:** "Check yourself".
- **Problem:** All three questions repeat sentences from the text. None asks the learner to compute or apply anything. The chapter has numbers for both (yield, FLOP sanity check), and Chapter 1's quiz does ask for arithmetic. Q3's answer says spares "are hidden by the repair logic" as fact. The research notes mark the 850k → 745.5k gap as an inference.
- **Why it matters:** Recall questions do not test the mental model. Stating an inference as fact contradicts the course's provenance rule.
- **Concrete fix:** Add Q4: "<summary>At 0.001 defects/mm², what fraction of 832 mm² GPU dies are defect-free, and what is the chance a 46,225 mm² chip with no spares is?</summary><p>e^(−0.832) ≈ 44%; e^(−46) ≈ 10⁻²⁰. Without fine-grained spares a wafer-scale chip would never yield.</p>". Add Q5: "<summary>Estimate WSE-3 dense FP16 peak from first principles. Which input is weakest?</summary><p>900k PEs × 8 FMAs × 2 FLOPs × 0.85–1 GHz ≈ 12–14 PF. The clock: none is published; 850 MHz is only the SDK benchmarks' assumption.</p>". Change Q3's answer to: "Part of the gap is consistent with spare cores hidden by repair (Cerebras does not publish the breakdown), so the SDK sees a 750 × 994 fabric. The memcpy runtime then occupies PEs framing your program, so your rectangle must be 7 columns and 2 rows smaller: ≈ 743 × 992 ≈ 737k."

### P13 [minor] The power section states "what" with no "why"
- **Location:** "Power goes in through the face".
- **Problem:** "A ~23 kW system cannot feed a wafer from its edges" has no reason attached. The learner gets no picture of the current involved, and no explanation of why moving AC/DC conversion closer (0.5 mm vs 50 mm) matters.
- **Why it matters:** A short derived number would turn an assertion into understanding for a technically strong reader.
- **Concrete fix:** Add: "At core voltages below 1 V, ~15–20 kW into the wafer means on the order of 20,000 amperes [Derived, assuming ~0.8 V]. Pushed in from the edge across 215 mm of thin metal, that current would lose much of its voltage on the way, so it is fed in vertically all over the face. Shortening the last stage of conversion (CS-4) cuts the distance that huge current has to travel."

### P14 [minor] The B200 die-to-die figure has no provenance tag
- **Location:** "…NVIDIA's B200 glues two such dies together with a 10 TB/s link."
- **Problem:** Untagged number. The brief says every number carries a tag.
- **Why it matters:** The learner is trained to trust tags. An untagged number weakens that habit.
- **Concrete fix:** Append `<span class="tag vendor">Vendor</span>` after "10 TB/s link".
