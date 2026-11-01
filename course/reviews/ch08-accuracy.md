# ch08 · accuracy review

Summary: Chapter 8 matches the research report closely (report "Chapter 9" section, lines ~127–141, and wse_hardware.md §8). I checked every number against the sources: CS-4 rack totals (3 × 250 PF = 750 PF, 3 × 43.2 = 129.6 PB/s, 3 × 2.4 = 7.2 Tb/s), 2,048 × 125 PF = 256 EF, CG-3 64 × 125 PF = 8 EF, 4 × 44 = 176 GB, 405B at 16-bit is 810 GB / 44 GB ≈ 19, and at 4-bit 202.5 / 44 ≈ 5. All of them are consistent. Web search confirms the launch figures: 450 tok/s, $0.60/M and 16-bit weights. The text has no outright factual errors. The problems are provenance and precision: one mis-tag (a vendor price filed as Analyst), several untagged numbers, a table cell in the wrong row, a quiz answer that understates the bandwidth gap, an even-split diagram presented as fact, and a widget label that is clipped off-screen. Verdict: accurate overall; apply the minor and major fixes below.

## Findings

### A1 [major] $0.60/M is a Cerebras list price, not an analyst figure
- Location: `.callout.warn`, "Fast per user is not the same as cheap per token" (line 93).
- Problem: The sentence puts the H100 analyst estimate and Cerebras's own list price under a single `Analyst` tag. The $0.60 per million tokens is the vendor's launch price for Llama 3.1-70B (Aug 2024). Chapter 15 line 64 has the same mis-tag.
- Evidence: gpu_and_comparison.md:162 "**[VENDOR]** Llama 3.1 70B at about 2,100 tok/s at batch 1, priced at $0.60/M tokens. A GPU comparison puts H100 ... $0.10–0.25/M"; report Performance table: "Vendor / Analyst". Launch coverage: "60 cents per million tokens for Llama 3.1 70B" (https://siliconangle.com/?p=668501, https://www.businesswire.com/news/home/20240827815278/en).
- Fix: Replace `Analysts put batched H100 serving at ~$0.10–0.25 per million tokens against Cerebras's $0.60 for Llama 70B <span class="tag analyst">Analyst</span>.` with `Analysts put batched H100 serving at ~$0.10–0.25 per million tokens <span class="tag analyst">Analyst</span>, against Cerebras's launch list price of $0.60 for Llama 3.1-70B <span class="tag vendor">Vendor</span>.` (Tell the coordinator that ch15 line 64 needs the same split.)

### A2 [major] Quiz answer understates the cost of streaming weights for decode
- Location: Quiz 1, "Why does weight streaming suit training but not low-latency inference?" (line 98).
- Problem: "streaming weights would make it as bandwidth-bound as a GPU" implies parity with HBM. Weights would come from MemoryX over the off-wafer links. Those links are far narrower than a GPU's HBM: WSE-3T has 2.4 Tb/s ≈ 300 GB/s off-wafer per wafer, while H100 HBM gives 3.35 TB/s. Decode would therefore be bound by the link and would be slower than on a GPU, not equal to it.
- Evidence: wse_hardware.md:34 "2.4 Tb/s off-wafer I/O per wafer (vendor)"; report line 235 "80 GB of HBM3 at 3.35 TB/s"; ch07 line 110 says host I/O is "orders of magnitude below on-wafer bandwidth".
- Fix: Replace `Decode uses each weight for one token per sequence; streaming weights would make it as bandwidth-bound as a GPU.` with `Decode uses each weight for only one token per sequence, so every token would wait on weights arriving over the off-wafer links (a few hundred GB/s per wafer, less than one GPU's HBM) <span class="tag derived">Derived</span>. Pinning weights in 21 PB/s SRAM avoids that.`

### A3 [minor] CS-4 interconnect cell sits in the "Max cluster via SwarmX" row
- Location: Systems table, row "Max cluster via SwarmX", CS-4 column (line 30).
- Problem: "Direct Wafer Links + RoCE v2" is a link technology, not a maximum cluster size, and no source ties it to SwarmX. In the report it belongs to the Rack row. As placed, it suggests that SwarmX scales CS-4 over DWL.
- Evidence: report line 134 lists CS-4 as "—" for max cluster; report line 136 puts "RoCE v2 + Direct Wafer Links" in the Rack row; wse_hardware.md:36 "Uses RoCE v2 Ethernet plus 'Direct Wafer Links' (switchless wafer-to-wafer)".
- Fix: Change the CS-4 cell in that row to `—`. Then change the CS-4 System cell to `3 wafers per rack: 750 PF sparse, 129.6 PB/s memory, 7.2 Tb/s I/O; RoCE v2 + Direct Wafer Links (switchless wafer-to-wafer)`.

### A4 [minor] CS-2 power range drops the "sources conflict" note
- Location: Systems table, System row, CS-2 cell "one wafer, 15–20 kW" (line 28).
- Problem: The cell reads as a range of configurations. In fact two sources give two different single figures (15 kW from Tom's Hardware, ~20 kW from the Computer History Museum). Ch02 line 59 says "15–20 kW (sources conflict)".
- Evidence: report line 36 "15 kW vs ~20 kW (conflict)"; report line 38 sources.
- Fix: `one wafer, 15–20 kW (sources conflict)`.

### A5 [minor] Untagged numbers in the lede and the inference paragraph
- Location: Lede (line 13), "A wafer has 44 GB of memory"; inference paragraph (line 59), "Llama 3.1-70B needs about 140 GB at 16-bit ... 80 layers ... four CS-3 systems".
- Problem: The brief requires a tag on every number. 44 GB applies to WSE-3 only (WSE-2 has 40 GB). The 140 GB figure is derived (70.6B × 2 B). The four-CS-3 / 80-layer layout is a vendor-sourced report (The Register).
- Evidence: report line 140 (source The Register 2024-08-27); wse_hardware.md:189. Launch coverage confirms 16-bit weights (https://www.businesswire.com/news/home/20240827815278/en).
- Fix: Lede: `A WSE-3 wafer has 44 GB of on-chip SRAM <span class="tag vendor">Vendor</span>.` Inference paragraph: after `about 140 GB at 16-bit` insert ` <span class="tag derived">Derived</span>`. After `like a pipeline.` insert ` <span class="tag vendor">Vendor</span> (as reported by The Register).`

### A6 [minor] Pipeline diagram presents an even 20-layer split as fact
- Location: `#pipe` script (lines 119–120), labels `layers 1–20` … `61–80` and "~35 GB weights".
- Problem: No source gives the per-wafer split. The sources only say the 80 layers were spread over four CS-3s. The embedding and LM head (~2 GB each at 16-bit for a 128k × 8192 vocab matrix) also make the split uneven. The figure should be labelled as illustrative.
- Evidence: wse_hardware.md:189 gives only "80 layers are distributed across four CS-3 systems"; report line 140 notes "the per-model inference precision were not verified".
- Fix: In the figcaption, after `the weights never move.` append ` The even 20-layer, ~35 GB split is illustrative <span class="tag derived">Derived</span>; the actual partition was not published.`

### A7 [minor] Widget's "… N wafers total" label is outside the SVG viewBox
- Location: `cap()` function (line 135), together with `#p-svg` `viewBox="0 0 680 120"` (line 78).
- Problem: The text is drawn at `y: 140`, but the viewBox is 120 tall, so the label is clipped. Above 40 wafers (for example 1000B at 16-bit = 57 wafers at 20% reserve), the graphic shows only 40 wafers and nothing marks the truncation. A learner who reads the picture rather than the readout gets an undercount.
- Fix: Change `viewBox="0 0 680 120"` to `viewBox="0 0 680 150"` on `#p-svg` (and change `width`/height accordingly if needed).

### A8 [minor] "Few concurrent sequences" claim has no tag
- Location: Callout, "a wafer serves relatively few concurrent sequences compared with a GPU running large batches" (line 93).
- Problem: This is a reasoned inference with no source. The notes carry no measured concurrency figure for Cerebras.
- Evidence: gpu_and_comparison.md:162–164 cover price and batch only for GPUs; no Cerebras concurrency number appears.
- Fix: Append ` <span class="tag analyst">Analyst</span>` immediately after `running large batches`.

### A9 [minor] "[Derived]" in the pipeline SVG is not a real provenance tag
- Location: Line 65, `<tspan class="f-amb">[Derived]</tspan>`.
- Problem: It looks different from the `.tag derived` spans used everywhere else, and it is coloured amber, which may clash with the derived tag's colour token. Accuracy is fine; the problem is consistency of provenance.
- Fix: Remove the tspan from the SVG text and append ` <span class="tag derived">Derived</span> 4 × 44 GB = 176 GB; ~36 GB left for KV cache and activations.` to the figcaption. Alternatively, keep it in the SVG and give the tspan the same colour class the `.tag.derived` style uses.

### A10 [minor] Condor Galaxy row omits the CG-1/CG-2 exaflop figure, so the eras are compared unevenly
- Location: Systems table, Flagship cluster row (line 31).
- Problem: CG-3 is given "8 EF" but CG-1/2 get no EF figure. The report gives "4 EF, 82 TB" for each. Readers cannot see the 2× per-system jump.
- Evidence: report line 135 "CG-1/CG-2: 64 CS-2 each, 4 EF, 82 TB [Vendor] | CG-3: 64 CS-3, 8 EF, 58M cores, 108 TB".
- Fix: CS-2 cell: `Condor Galaxy 1 & 2: 64 CS-2 each, 4 EF`. CS-3 cell: `Condor Galaxy 3: 64 CS-3, 8 EF, 108 TB parameter memory`.

## Not verifiable
- The Register's statement of four CS-3s, 80 layers, over Ethernet (2024-08-27). Web search did not surface the article; only the notes and report cite it. Analytics India Magazine confirms layer-boundary splitting across multiple CS-3s, but gives no count.
- The 2,314 tok/s / 170 ms TTFT for Llama 3.3-70B. It is attributed to Artificial Analysis but is second-hand, via a Data Exchange interview.
- Kimi K2.6 at 981 tok/s, 6.7×. The source is VentureBeat ("Cerebras says…") citing AA; I could not check the AA provider page directly.
- gpt-oss-120B ~3,000 claimed vs ~1,700 measured (single secondary source, morphllm).
- CS-4 "2× CS-3 speed, up to 10× throughput per watt", and all CS-4 rack figures (investor release, STH HC2026). Not re-fetched.
- MemoryX "1.5 PB in some sources" and CS-3-era "up to 1.2 PB" (Cerebras CS-3 blog). Not re-fetched.
- The 2,100 tok/s figure for Oct 2024. Search results show the Cerebras blog title "Llama3.1-70B breaks 2,100 tokens/s", which is consistent with the chapter.
- The current status of the Condor Galaxy clusters (the chapter already flags this).
