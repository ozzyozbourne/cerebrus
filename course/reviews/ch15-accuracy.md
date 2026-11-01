# ch15 · accuracy review

Summary: Chapter 15 mostly matches the research report's Chapter 15 section (`reports/Cerebras architecture course research.md`, lines 250–313) and the four notes files. Most comparison cells and evidence rows trace back correctly. The main problems are these:
- The compute bar chart compares an FP4 figure against BF16, FP16 and BlockFP8, which makes B200 look about 4× stronger than it would at equal precision.
- The MD row's three numbers do not agree with each other (270,097 / 1,530 = 176.5, not 179).
- Three tags are wrong or incomplete: the pricing row, the Scaling paragraph, and the MD row.
- The two architecture tables carry no provenance tags at all, although the brief requires every number to have one.
- The H100/B200 power can now be stated precisely (700 W / 1,000 W maximum TDP, not "typical"). The CS-3 vs card vs GPU power bars still compare a whole system with single cards.

Nothing is fabricated. The fixes are about framing, tags and arithmetic.

## Findings

### A1 [major] "Peak low-precision compute" bars compare FP4 with BF16/FP16
- **Location:** widget `M["Peak low-precision compute (FLOP/s)"]` = `[15.6e15, 664e12, 989e12, 9e15]`.
- **Problem:** B200 is plotted at its FP4 dense figure (9 PF) and H100 at its BF16 dense figure (989 TF). The bar ratio is about 9×, but most of that gap comes from the number format, not the hardware. The note says "formats differ", but the bars still show a misleading gap. At BF16 dense, B200 is 2.25 PF, about 2.3× H100. WSE-3's analyst figure (15.6 PF) is also FP16, so a like-for-like FP16/BF16 row is possible for three of the four devices.
- **Evidence:**
  - gpu_and_comparison.md lines 17 and 37 give H100 at ~989 TF BF16 dense and ~1,979 TF FP8 dense, and B200 at ~9 PF FP4 dense.
  - Web: Spheron B200 guide, SemiAnalysis InferenceX B200 and GPUPoet all list B200 dense at 9,000 TF FP4, 4,500 TF FP8 and 2,250 TF BF16 (https://www.spheron.network/blog/nvidia-b200-complete-guide/ ; https://inferencex.semianalysis.com/chips/b200).
- **Concrete fix:** replace the entry with:
  `"Peak dense compute, ~16-bit (FLOP/s)": [[15.6e15, 664e12, 989e12, 2.25e15], "FP16/BF16 dense: WSE-3 Analyst est. (Cerebras publishes only 125 PF sparse); H100 Vendor; B200 Vendor via secondary (FP4 dense is 9 PF). p150 is BlockFP8 (Vendor) — no BF16 figure compiled here, so its bar is not like-for-like"`

### A2 [major] MD row: 270,097 vs 1,530 is 176.5×, not 179×
- **Location:** evidence table, row "WSE-2 molecular dynamics: 270,097 timesteps/s vs 1,530 on Frontier (179×)".
- **Problem:** the three numbers are inconsistent. 270,097 / 1,530 = 176.5. The 179× figure is the paper's headline. 1,530 × 179 = 273,870, which suggests the Frontier figure is paired with a different WSE rate (a search extract mentions ~274,000 in the paper body). The course states all three as exact.
- **Evidence:** gpu_and_comparison.md line 167 is the origin of all three numbers, so the notes carry the same inconsistency. The press release and LLNL quote "270,000 timesteps per second" and "179x" (https://www.cerebras.ai/press-release/cerebras-wafer-scale-engine-outperforms-worlds-1-supercomputer-achieving-long-timescale-molecular-dynamics-simulations-179x-faster). arxiv.org was not reachable from this session, so I could not read the paper's table.
- **Concrete fix:** `WSE-2 molecular dynamics (tantalum, ~800k atoms): ~270,000 timesteps/s, 179× LAMMPS on Frontier and 55× Quartz (paper's headline figures)`. Restore an exact Frontier number only after checking the arXiv 2405.07898 table.

### A3 [major] The architecture and programming tables carry no provenance tags
- **Location:** "Architecture and memory" table (every cell) and "Strengths and matching weaknesses" table (21 PB/s, 44 GB, ~23 kW, ~512 GB/s, …).
- **Problem:** REVIEW_BRIEF says "Every number should carry one." The report's version of this table tags its cells: [Vendor] on compute units and CS-3 power, [Derived] on the H100 SRAM total. The course drops all of them, including the one [Derived] figure (H100 ~66 MB RF/L1).
- **Evidence:** report lines 254–263 carry the tags; course 15-comparison.html lines 27–35 have none.
- **Concrete fix:** add a tag row under the table header, `<tr><td>Provenance</td><td><span class="tag vendor">Vendor</span> (Hot Chips 2024, press)</td><td><span class="tag vendor">Vendor</span> (tt docs, datasheet)</td><td><span class="tag vendor">Vendor</span> (whitepaper / secondary)</td></tr>`, and change the H100 SRAM cell to `~50 MB L2 + ~66 MB RF/L1 (H100) <span class="tag derived">Derived</span>`. In the strengths table, add `<span class="tag vendor">Vendor</span>` after "21 PB/s local SRAM bandwidth" and after "~23 kW per system".

### A4 [major] Power: GPU figures are maximum TDP, not "typical", and the bars compare a system with cards
- **Location:**
  - widget `"Power (W)": [[23e3, 300, 700, 1000], "... H100/B200 typical board power, not verified ..."]`
  - architecture table cell "~700 W+ per GPU (not verified here)"
- **Problem:**
  - (a) 700 W and 1,000 W are the vendor *maximum* TDPs, not typical draw. "~700 W+" is vague for B200, which is 1,000 W air-cooled HGX and up to 1,200 W in liquid-cooled or GB200 configurations.
  - (b) 23 kW is a whole 15U CS-3 system (power supplies, cooling, I/O). The other bars are a single PCIe card and bare GPU modules with no host, NVSwitch or cooling. The bars therefore overstate the per-device gap, against Cerebras. A system-level GPU reference would be fairer: DGX H100 is ~10.2 kW for 8 GPUs, DGX B200 ~14.3 kW (background knowledge; not in the notes).
- **Evidence:**
  - Report line 263 and gpu_and_comparison.md say GPU power was "not verified in notes".
  - Web: NVIDIA H200/H100 datasheets list "Max TDP up to 700W (configurable)". Dell/TweakTown and Vultr's HGX B200 docs give 1,000 W per B200, with 1,200 W for the liquid-cooled full-spec part (https://www.tweaktown.com/news/96591/nvidias-next-gen-b200-ai-gpu-uses-1000w-of-power-per-drops-in-2025-confirmed-by-dell/index.html ; https://docs.vultr.com/inference-cookbook/cuda/getting-started/hardware-overview).
- **Concrete fix:**
  - Widget note: `"CS-3 = whole 15U system incl. cooling (Vendor); p150 = one PCIe card (Vendor); H100 SXM up to 700 W and B200 up to 1,000 W (1,200 W liquid-cooled) = max TDP of the GPU module alone, Vendor via web search, not in this course's research notes. System vs card: not like-for-like"`
  - Table cell: `H100 SXM up to 700 W; B200 up to 1,000 W (max TDP per GPU module, not system)`

### A5 [minor] Pricing row tag: $0.60 is a vendor price, not an analyst figure; source is a GPU-cloud blog
- **Location:** evidence row "Batched H100 inference ~$0.10–0.25 per M tokens vs Cerebras $0.60 (Llama 70B)", tagged Analyst only.
- **Problem:** the report tags this row "Vendor / Analyst". $0.60/M is Cerebras's list price, which is a vendor number. The $0.10–0.25 figure comes from Spheron, a GPU-rental company writing about a competitor, so calling it a neutral "analyst" source is generous. The model is Llama 3.1 70B, and the GPU figure is for output tokens at large batch. Chapter 8 repeats the same Analyst-only tag.
- **Evidence:** report line 293; gpu_and_comparison.md line 162 ("Llama 3.1 70B … $0.60/M … H100 … ~$0.10–0.25/M output tokens at large batch", source Spheron).
- **Concrete fix:** `<td>Llama 3.1-70B: Cerebras list price $0.60 per M tokens vs batched H100 ~$0.10–0.25 per M output tokens (GPU-cloud estimate)</td><td><span class="tag vendor">Vendor</span> price vs <span class="tag analyst">Analyst</span> (Spheron)</td>`. Make the same change in 08-systems.html.

### A6 [minor] Scaling paragraph: one Vendor tag covers a derived synthesis; "72 GPUs per rack" applies only to NVL72
- **Location:** "Scaling" paragraph.
- **Problem:** the report tags this paragraph "[Derived synthesis; sources in Chapters 9, 13, 14]". Only "2,048 CS-3s" is a plain vendor figure. "Cheaper, lower bandwidth per link" is the notes' own inference (gpu_and_comparison.md §5 Inferences). Also, "72 GPUs per rack" is the GB200 NVL72 domain, while H100 and HGX B200 scale up to 8 GPUs (report line 241 table: "8-GPU HGX").
- **Evidence:** report line 284; gpu_and_comparison.md lines 38–39 and 146.
- **Concrete fix:**
  - Change the NVIDIA clause to `NVLink/NVSwitch scale-up (8 GPUs on HGX H100/B200, 72 in a GB200 NVL72 rack)`.
  - Tag the MemoryX clause as `(to 2,048 CS-3s <span class="tag vendor">Vendor</span>)`.
  - End the paragraph with `<span class="tag derived">Derived</span> synthesis` in place of the single Vendor tag.

### A7 [minor] MD row tagged "Indep" although Cerebras co-authored it
- **Location:** MD evidence row, tag `<span class="tag indep">Peer-reviewed</span> (Sandia/LLNL/LANL + Cerebras)`.
- **Problem:** the paper has Cerebras co-authors, so "Indep" styling overstates its independence. It is peer-reviewed (SC24, Gordon Bell finalist), not independent. The chapter also never says it was a finalist rather than the winner, which the report asks to state.
- **Evidence:** report line 307 ("the paper was a 2024 Gordon Bell finalist, not the winner"); gpu_and_comparison.md lines 167 and 170.
- **Concrete fix:** `<td><span class="tag measured">Measured</span> peer-reviewed, Sandia/LLNL/LANL with Cerebras co-authors; Gordon Bell 2024 finalist</td>`

### A8 [minor] Tenstorrent Galaxy row omits the ~308 tok/s/user launch figure and batch context
- **Location:** evidence row "Tenstorrent Galaxy: 72.5 tok/s/user on Llama 70B (Wormhole), ~350 on DeepSeek-R1 (Blackhole)".
- **Problem:** ~350 is the vendor headline. Reporting at launch put the measured figure nearer 308 tok/s/user, and the notes disagree on the system size (one "Galaxy Blackhole" vs a demo on 16 Galaxies). The 72.5 figure is Llama **3.3** 70B at batch 32 on a release candidate.
- **Evidence:** report line 297; tenstorrent.md (Futurum / Munich Startup: "about 350 … batch 8–64 … closer to 308 at launch"); gpu_and_comparison.md lines 174–175.
- **Concrete fix:** `Tenstorrent Galaxy: 72.5 tok/s/user on Llama 3.3-70B at batch 32 (Wormhole); ~350 tok/s/user claimed (~308 reported at launch) on DeepSeek-R1 671B (Blackhole)`

### A9 [minor] PE area stated without its uncertainty
- **Location:** architecture table "~900k tiny PEs (~0.05 mm²)".
- **Problem:** the notes give two conflicting figures, ~38,000 µm² (0.038 mm²) and ~0.05 mm², and say "No definitive figure found". Chapter 2 also uses 0.05 mm² without a caveat.
- **Evidence:** wse_hardware.md, per-core area bullet (hyper-accel blog, Cerebras yield blog).
- **Concrete fix:** `~900k tiny PEs (~0.04–0.05 mm², sources differ), 8-wide FP16 SIMD`

### A10 [minor] Tenstorrent "Caches: none" omits the optional write-through cache; GPU "crossbar to L2" is unverified
- **Location:** architecture table, rows "Caches" and "On-chip network".
- **Problem:** Blackhole has a tiny optional write-through L1 data cache (4 × 16 B lines, off by default), and the report's cell reads "None (tiny optional write-through)". The report marks the GPU "Crossbar to L2" as "(not detailed here)", meaning unverified.
- **Evidence:** tenstorrent.md lines 29 and 80; report line 262.
- **Concrete fix:** Tenstorrent cell `none (tiny optional write-through cache, off by default)`; GPU cell `crossbar to L2 (not verified here)`.

### A11 [minor] "Fits in a few wafers" contradicts the chapter's own headline evidence
- **Location:** decision guide row 1, "Lowest latency per user on a model that fits in a few wafers"; quiz answer "a single GPU holds far more memory than one wafer".
- **Problem:**
  - The flagship independent result (Kimi K2.6, ~1T params) needs on the order of a dozen or more CS-3s even at 4–8-bit weights (1T × 0.5–1 B ÷ 44 GB ≈ 12–23 wafers) [Derived]. "A few" undersells the deployments that produced the evidence.
  - "Far more" holds for B200 (192 GB ≈ 4.4×) but is weak for H100 (80 GB ≈ 1.8×).
- **Evidence:** gpu_and_comparison.md line 159 (Kimi K2.6 ~1T); line 79 (70B FP16 ≈ 140 GB needs ~4 CS-3s).
- **Concrete fix:**
  - Decision row: `Lowest latency per user, if you can hold the model's weights in the SRAM of enough wafers`.
  - Quiz: `and a single GPU holds 2–4× more memory than one wafer (80–192 GB vs 44 GB).`

### A12 [minor] "Main memory capacity" note says "All Vendor" but B200 usable is ~180 GB
- **Location:** widget note for "Main memory capacity (bytes)".
- **Problem:** this is a minor fairness point. Clouds expose ~180 GB, and InferenceX lists 180–186 GB usable. Also, Cerebras's 44 GB must hold KV cache and activations as well as weights.
- **Evidence:** gpu_and_comparison.md line 22; Chapter 8 ("with a slice reserved for KV cache and activations").
- **Concrete fix:** append `; B200 nominal 192 GB (~180 GB usable in clouds)` to the note.

## Not verifiable
- The exact Frontier timesteps/s and WSE-2 rate in arXiv 2405.07898. arxiv.org is blocked in this session (DNS failure), so only press figures (~270,000 and 179×) were confirmed.
- Kimi K2.6 at 981 tok/s and 6.7×, and the ~1,700 tok/s AA figure for gpt-oss-120B. The live AA leaderboard was not checked; the notes say to re-check it.
- Llama 3.3-70B at 2,314 tok/s with 170 ms TTFT. This is AA via an interview; the primary benchmark was not checked (notes say so).
- WSE-3 dense 15.6 PF, which is an analyst estimate only; Cerebras publishes no dense figure.
- The CS-3 power of ~23 kW. Most sources agree, but one says 15 kW; Chapter 2's 15–20 kW conflict is for CS-2.
- Whether Cerebras or Tenstorrent has ever submitted to MLPerf. The notes say none were found, which is unverified.
- The H100 "crossbar to L2" interconnect description.
- The lab claims ("~88 cycles fixed", "8 vs 16 PEs same per step", "varied by at most 2 cycles") match Chapters 9 and 12. I did not re-run the simulator.
