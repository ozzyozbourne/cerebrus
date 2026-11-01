# ch02 · accuracy review

Summary: The chapter is broadly accurate. Every headline spec in the generation table (transistors, cores, SRAM, bandwidths, 125 PF sparse / ~15.6 PF dense, 23 kW, CS-4 figures, 750×994, 7/2 margin, 46 defects / 2.2 mm² / 164×) matches the research notes and the SDK. I found no critical errors. The main problems: (1) the dense-FLOPs sanity check rests on an unsourced ~1 GHz clock and ignores the SDK's own 850 MHz assumption; (2) several numbers have no provenance tag (57×, reticle size, B200 link, H100 TF, 0.05 mm² core, the 48 KB stat); (3) a few small overclaims ("configured at manufacturing time", "must be 7 columns narrower", I/O "at the wafer edges" stated as fact); (4) a few table cells that are inconsistent with ch03 or the notes.

## Findings

### A1 [major] Dense-FLOPs sanity check uses an unsourced 1 GHz clock and ignores the SDK's 850 MHz
- Location: callout "Read the FLOPs carefully", sentence "900k cores × 8 FP16 FMAs (16 FLOPs) × ~1 GHz ≈ 14–15 PF dense"; the stat tile "none / official clock frequency published".
- Problem: No source gives ~1 GHz. The only clock number in the sources is the SDK benchmarks' assumption of 850 MHz. At 850 MHz the same arithmetic gives 900k × 16 × 0.85 GHz ≈ 12.2 PF, not 14–15 PF. The chapter says no clock is published but leaves out the 850 MHz figure that the course could cite.
- Evidence: `research_notes/.../wse_hardware.md` line 21: "The SDK benchmarks convert cycles to time assuming 'a PE runs with clock speed 850MHz'"; line 45: "No official clock frequency for WSE-2 or WSE-3 was found in any source. The only number is the SDK's 850 MHz assumption." SDK `benchmarks/conjugate-gradient/run.py:82`: "where a PE runs with clock speed 850MHz". Line 92 of the notes labels the 1 GHz version "my arithmetic; the clock is unconfirmed."
- Concrete fix: Replace "A sanity check agrees with the analyst estimate: 900k cores × 8 FP16 FMAs (16 FLOPs) × ~1 GHz ≈ 14–15 PF dense <span class="tag derived">Derived; clock unconfirmed</span>." with: "A sanity check lands in the same range as the analyst estimate: 900k cores × 8 FP16 FMAs (16 FLOPs) × clock gives ≈ 12 PF at the 850 MHz the SDK benchmarks assume <span class="tag sdk">SDK 2.10.1</span>, or ≈ 14 PF at 1 GHz <span class="tag derived">Derived; clock unconfirmed</span>." Change the stat tile label to: "official clock published (SDK benchmarks assume 850 MHz <span class="tag sdk">SDK 2.10.1</span>)".

### A2 [minor] "about 57× the area of an H100 die" has no tag and no stated die area
- Location: lede paragraph.
- Problem: The H100 die area (~814 mm²) does not appear anywhere in the notes or the report, so 57× is an unstated derivation (46,225 / 814 ≈ 56.8). The vendor's own framing is "about 50× a GPU".
- Evidence: `wse_hardware.md` line 57: "Total chip area is about 50× a GPU". A grep for "814" across the notes and the report finds nothing.
- Concrete fix: Replace "about 57× the area of an H100 die." with "about 57× the area of an H100 die (~814 mm²) <span class="tag derived">Derived</span>."

### A3 [minor] Reticle size, "~800 mm²" and the B200 10 TB/s link are untagged
- Location: "From reticle to wafer", first paragraph.
- Problem: 26 × 33 mm and ~800 mm² do not appear in the sources (not verifiable; they are standard industry figures). The B200 two-die / 10 TB/s claim is in the sources as vendor-via-secondary but carries no tag.
- Evidence: `gpu_and_comparison.md` line 21: "The B200 is two reticle-limited dies joined by a 10 TB/s NV-HBI die-to-die link" under the heading "[VENDOR via SECONDARY]".
- Concrete fix: After "with a 10 TB/s link" insert ` <span class="tag vendor">Vendor</span>`. After "at most about 26 × 33 mm" insert ` <span class="tag indep">Industry standard</span>`.

### A4 [minor] H100 1,979 / 989 TF numbers are untagged
- Location: end of the "Read the FLOPs carefully" callout.
- Evidence: report line 235: "Dense BF16 is about 989 TFLOPS, and the often-quoted 1,979 TF is a 2:4-sparsity figure"; `gpu_and_comparison.md` line 17.
- Concrete fix: Replace "dense is ~989 TF." with "dense is ~989 TF <span class="tag vendor">Vendor</span>."

### A5 [minor] The "SIMD width plus 6% more cores" claim is untagged
- Location: same callout, "The WSE-2 → WSE-3 jump is mostly SIMD width (4 → 8) plus 6% more cores."
- Problem: This is arithmetic (900/850 = 1.059) from the notes' Inferences section, not a vendor statement.
- Evidence: `wse_hardware.md` line 41, under "### Inferences".
- Concrete fix: Append ` <span class="tag derived">Derived</span>` after "6% more cores".

### A6 [minor] The 0.05 mm² core size is stated as fact, untagged, and the conflicting figure is left out
- Location: "Surviving defects", "a core is about 0.05 mm², roughly 1/100th of an H100 SM."
- Evidence: report line 46: "Per-core area is uncertain: one source cites about 38,000 µm² from a WSE-3 whitepaper and another about 0.05 mm²". `wse_hardware.md` line 29: "No definitive figure found".
- Concrete fix: Replace with "a core is about 0.05 mm², roughly 1/100th of an H100 SM <span class="tag vendor">Vendor</span> (another source says ~0.038 mm²; either way, tiny)."

### A7 [minor] "configured at manufacturing time" overclaims
- Location: "Surviving defects", "the fabric is configured at manufacturing time to route around bad cores."
- Problem: The sources say the fabric is reconfigured to route around defective cores using spares. None says when this happens.
- Evidence: `wse_hardware.md` line 55: "The fabric is reconfigured to route around defective cores using spare cores (vendor)"; line 71: "I found no primary numbers for spare-core ratio …".
- Concrete fix: Replace "and the fabric is configured at manufacturing time to route around bad cores." with "and the fabric is reconfigured to route around bad cores <span class="tag vendor">Vendor</span> (when and how that configuration is done is not public)."

### A8 [minor] "a few dozen point flaws is normal" is unsourced and conflicts with the report
- Location: "Surviving defects", first sentence.
- Problem: The report says "a wafer-sized chip must expect hundreds of flaws". The only number in the sources is the vendor model's 46 defects at an assumed 0.001/mm².
- Evidence: report line 46: "Every wafer has defects, so a wafer-sized chip must expect hundreds of flaws." `wse_hardware.md` line 57: "With 0.001 defects/mm², the WSE 'sees 46 defects'".
- Concrete fix: Replace "Every wafer has defects — a few dozen point flaws is normal." with "Every wafer has defects: Cerebras's own model assumes about 46 on the wafer-scale square <span class="tag vendor">Vendor modelling</span>, and real defect densities are not published."

### A9 [minor] The CS-2 rectangle constraint is a maximum, but the text says "must be 7 columns narrower"
- Location: "I/O lives on the rim" paragraph; "Check yourself" item 3 ("your rectangle must be 7 columns and 2 rows smaller").
- Evidence: SDK `benchmarks/single-tile-matvec/README.rst` lines 34–36: "the width must be no bigger than 7 less than the x-dimension of the fabric, and the height must be no bigger than 2 less than the y-dimension of the fabric."
- Concrete fix: In the paragraph, replace "your rectangle of PEs must be 7 columns narrower and 2 rows shorter than" with "your rectangle of PEs must be at least 7 columns narrower and 2 rows shorter than". In Check yourself, replace "your rectangle must be 7 columns and 2 rows smaller." with "your rectangle must be at least 7 columns and 2 rows smaller (at most 743 × 992)." (Ch07 has the same wording, "must be 7 columns narrower and 2 rows shorter"; flag it to the ch07 owner.)

### A10 [minor] Physical edge I/O is stated as fact, and the reserved rows are not mentioned
- Location: "I/O lives on the rim", "Data enters and leaves at the wafer edges … the runtime reserves columns on the west and east sides".
- Problem: The notes list the physical location of wafer I/O as a gap. The SDK only states the 7/2 margin. West/east comes from `--fabric-offsets=4,1` and the memcpy layout (4 columns west + 3 east, 1 row north + 1 south). The link from physical edge I/O to the margin is an inference.
- Evidence: `wse_hardware.md` line 177: "The physical location and count of the wafer-edge I/O and SerDes were not found." Ch07 line 41: `--fabric-offsets=4,1`; ch07 figure: "Purple = memcpy west … green = memcpy east".
- Concrete fix: Replace "Data enters and leaves at the wafer edges. That has a software consequence you will meet in Chapter 7: the runtime reserves columns on the west and east sides of your program for host I/O," with "Data enters and leaves through I/O channels at the edge of the fabric <span class="tag derived">Derived; physical layout not public</span>. You will meet the software consequence in Chapter 7: the memcpy runtime reserves columns on the west and east sides of your program (and a row above and below) for host I/O,".

### A11 [minor] The ~737k stat tile is tagged SDK only, but the number is derived
- Location: stat tile "~737k / PEs a CS-2 program can use".
- Problem: The SDK gives 750×994 and the 7/2 margin. 743 × 992 = 737,056 is arithmetic. The body text has both tags; the tile has only one.
- Evidence: `wse_hardware.md` line 20; `single-tile-matvec/README.rst` lines 34–39.
- Concrete fix: Change `<span class="tag sdk">SDK 2.10.1</span>` in that tile to `<span class="tag sdk">SDK 2.10.1</span> <span class="tag derived">Derived</span>`.

### A12 [minor] The 48 KB stat tile has no tag
- Location: stat tile "48 KB / SRAM per PE, every generation".
- Evidence: HC34 / HC2024 vendor slides and the SC20 paper for CS-1 (`wse_hardware.md` lines 13, 79–80).
- Concrete fix: Append ` <span class="tag vendor">Vendor</span>` inside that tile's `.l` div.

### A13 [minor] The SRAM-per-PE row leaves out the WSE-2 256 B cache (inconsistent with ch03) and leaves WSE-3T blank
- Location: generation table, "SRAM per PE" row.
- Problem: WSE-3 shows "+ 512 B cache" but WSE-2 shows plain "48 KB", although WSE-2 has a 256 B software-managed cache. Ch03 line 90 says "256 B on WSE-2, 512 B on WSE-3". WSE-3T is the same silicon as WSE-3, so "—" undersells what is known.
- Evidence: `wse_hardware.md` line 79: "plus a '256B software-managed cache'"; line 34: WSE-3T "44 GB SRAM (same as WSE-3)".
- Concrete fix: Change the row to `<tr><td>SRAM per PE</td><td>48 KB</td><td>48 KB + 256 B cache</td><td>48 KB + 512 B cache</td><td>same as WSE-3</td></tr>`.

### A14 [minor] The WSE-3T fabric cell uses different units from the rest of the row
- Location: generation table, "Fabric bandwidth" row, WSE-3T cell "53.5 PB/s".
- Problem: The rest of the row is in Pb/s. 53.5 PB/s ≈ 428 Pb/s, and the cell should say so to avoid misreading.
- Evidence: `wse_hardware.md` line 113: "WSE-3T 53.5 PB/s (≈428 Pb/s)".
- Concrete fix: Replace `<td>53.5 PB/s</td>` (fabric row) with `<td>53.5 PB/s (~428 Pb/s)</td>`.

### A15 [minor] "Higher clock" for WSE-3T is The Register's interpretation, but the table tags it Vendor
- Location: table "Process" row, WSE-3T cell "same silicon as WSE-3, higher clock", and the sentence "Gains come from … and in 2026 a higher clock."
- Problem: The footnote says "All rows Vendor unless tagged", so this reads as a vendor claim. The source is The Register's interpretation ("squeezing its chips for every hertz").
- Evidence: `wse_hardware.md` line 35: "The Register attributes the doubled figures largely to 'squeezing its chips for every hertz', meaning a higher clock on the same silicon".
- Concrete fix: Change the cell to `same silicon as WSE-3; higher clock <span class="tag indep">The Register</span>`. Change the sentence to "Gains come from process shrinks, wider SIMD, and in 2026 (per press analysis) a higher clock."

### A16 [minor] The "System power" row has a non-power value for WSE-3T
- Location: table "System power" row, WSE-3T cell "3 wafers per rack".
- Evidence: `wse_hardware.md` line 36: "Backpacks have 2× the power and cooling of CS-3"; no per-wafer power figure is given.
- Concrete fix: Replace `<td>3 wafers per rack</td>` with `<td>not published (3 wafers per rack; each backpack has 2× CS-3 power and cooling)</td>`.

### A17 [minor] Power and cooling details from secondary sources are tagged as plain Vendor
- Location: "Power goes in through the face" paragraph.
- Problem: The single trailing Vendor tag covers the whole paragraph. Vertical power delivery, the "engine block" water loop and the thermal-expansion connector come from secondary summaries (gpusmith, Medium). Only the CS-4 0.5 mm / 50 mm figure is vendor (Hot Chips 2026 via STH).
- Evidence: `wse_hardware.md` line 63: "(Secondary sources. The HC31 slides are the primary source for the stitching, connector, and power details, but I could not open them.)"; line 64: engine block "[gpusmith] (secondary)".
- Concrete fix: After "removes the heat." insert ` <span class="tag indep">Secondary sources</span>`. Keep the existing Vendor tag after the CS-4 sentence.

### A18 [minor] The explanation for the 850k vs 745.5k gap is an inference stated as fact
- Location: Check yourself item 3, "Spares are hidden by the repair logic, and the I/O runtime reserves columns".
- Evidence: `wse_hardware.md` line 42: "The gap is consistent with spare or redundant cores and edge I/O not being exposed … This is an inference; Cerebras has not published the breakdown."
- Concrete fix: Replace "Spares are hidden by the repair logic, and the I/O runtime reserves columns around your program." with "The SDK exposes only 750 × 994 = 745,500 positions (the rest are most likely spares and edge infrastructure; Cerebras has not published the breakdown), and the memcpy runtime reserves a frame around your program."

## Not verifiable
- 26 × 33 mm reticle limit, "~800 mm²" largest GPU dies, and H100 die area (~814 mm², used for 57×): not in the notes, report or SDK.
- WSE-1 on TSMC 16nm: not in the notes (the chapter already caveats it).
- "~60 GPUs" per wafer: not sourced, but it matches the chapter's own simulator geometry (26×32 mm dies with 1 mm gaps on a 300 mm wafer gives exactly 60 whole dies; checked by running the same loop in Python).
- HC31 (2019) primary slides for stitching, the connector and power delivery: the notes say they could not be opened. The "Vendor (Hot Chips 2019/2022)" caption tag relies on secondary extracts.
- SDK inconsistency to note: the top of `benchmarks/single-tile-matvec/README.rst` (lines 9–13) runs `--dims 750,994` as the *program rectangle* ("750*994 matvecs, with one matvec occurring on each PE"), while lines 34–39 say 750,994 is the *fabric* size and the program must be 7/2 smaller. The chapter follows the latter reading, which agrees with the notes, but the source is internally ambiguous.
