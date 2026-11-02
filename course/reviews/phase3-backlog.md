# Phase 3: review backlog and new-chapter decision

Inputs: the out-of-scope sections of the 15 depth reviews, notes in the other reviews, the open sections of the 15 fix logs, and CROSS_CHAPTER_NOTES.md (CCN). Coverage was checked by grepping the built HTML. "Sources" counts independent files.

## 1. Cluster table

| # | Theme | Sources | Covered now? | Recommendation |
|---|---|---|---|---|
| 1 | **Collectives on a mesh**: `<collectives_2d>` in depth, a switch lab (one color, dynamic switches), 2-D allreduce, tree vs chain, root placement, 25-pt switch multicast | ch04-depth, ch09-depth, ch11-depth, ch12-depth, ch04-fixlog (5) | **Partly.** ch04 has "Runtime flexibility: switches, filters and teardown". ch11 has a `<collectives_2d>` library box (≈700 fixed cycles, CCN 24). Not covered: an allreduce, tree vs chain, a switch-based program, the teardown FSM, the 25-pt `switches.csl` | **New lab chapter** (proposal A) |
| 2 | **Same workload on three machines**: 70B decode traced end to end, stencil/GEMM, code effort, TP scaling | ch14-depth (#1, #2), ch15-depth, ch13-depth, ch08-depth, ch01-depth (5) | **Mostly.** ch15 has "One workload, three machines: Llama-70B decode", "A second workload: a stencil, and a GEMM", and a code-effort row (246 lines, Measured). Not covered: a per-token count of bytes, hops and syncs; the producer/consumer "same kernel" table; HC24 TP-scaling data | **Section edits in ch15** (a new chapter only if ch15 gets split) |
| 3 | **Measurement methodology**: sim_stats vs TSC vs inst_trace, host-load noise, cross-PE TSC skew, a kernel-timer snippet, cycles→µs | ch09-, ch10-, ch11-, ch12-depth, ch12-pedagogy P3, CCN 17/19/21 (5 + 3 CCN) | **Spread out.** ch09 debugging (inst_trace, no sim_stats on FATAL), ch10 TSC idiom, ch11/ch12 TSC method. No single page | **Appendix A** |
| 4 | **Profiling on each machine** (Nsight, Tracy, simulator traces, csdb/CTF) | ch14-depth #5, ch09-depth, ch11-depth, ch09-fixlog (4) | **No.** Nsight and Tracy: 0 hits. csdb verified only from help screens | Fold into Appendix A; csdb is a follow-up experiment |
| 5 | **Glossary** (course-wide terms; GPU terms undefined) | ch13-pedagogy, ch14-pedagogy (2), and implied by ch05/ch09 | **ch13 only** ("Glossary for reading Tenstorrent material"). ch14 and the Cerebras chapters have none | **Appendix B** |
| 6 | **Number formats** (BF16, FP8, MXFP4/NVFP4, CB16, BlockFP8; one quantisation widget) | ch14-depth #6, ch13-pedagogy (2) | **Scattered.** ch14 defines NVFP4, ch13 BlockFP8, ch15 "Which number format?" | Merge into Appendix B |
| 7 | **Roofline arithmetic cheat sheet** (GEMM/GEMV intensity, KV bytes/token, Little's law, tok/s bounds) | ch01-depth, ch15-depth (2) | **Partly.** ch01 hierarchical roofline, ch14 bytes-in-flight, ch15 ridge row | **Appendix C** |
| 8 | **CSL/SDK reference**: tutorial map, PE config space (`@get_config`, address maps), SdkRuntime surface, compiler flags, `cs_readelf` | ch05-depth, ch09-depth (×2), ch03-depth, ch07-depth (4) | **Partly.** ch05 covers TASK_PRIORITY and priorities; ch09 covers cs_readelf, flags and per-module tutorials; ch07 covers nonblock/rowbcast. `@get_config`/`@set_config`: 0 hits | **Appendix D** |
| 9 | **Sources, provenance, reading a benchmark claim** | ch15-depth D9, ch01-accuracy A4/A5, all fixlogs' unverified lists (≥8) | **Partly.** The index has a tag legend; ch15 has a claim checklist. There is no page of sources and no list of unverified figures | **Appendix E** |
| 10 | **Single-PE performance lab** (single-tile-matvec, pad/bank clash, scalar-loop cost, f16) | ch01-, ch02-, ch06-, ch10-depth (4) | **Yes, mostly.** ch10 has the bank-clash padding (CCN 22); ch12 has an f16 exercise; single-tile-matvec is cited in 8 chapters | Small edit: one optional ch10 exercise |
| 11 | **Capstone: 3-D 7-pt stencil + CG**; temporal blocking | ch12-depth (×2), ch15-depth (ch12 extrapolation) (2) | **Partly.** ch12 has a 2-D/3-D paragraph, a 7-pt/25-pt benchmark comparison and a whole-wafer extrapolation | Optional exercise or appendix. Not a chapter |
| 12 | **Toy inference pipeline in CSL** (GEMV layer regions, activation passed east) | ch08-depth (1) | **No** | Optional final section of proposal A, or proposal C |
| 13 | **SdkLayout lab** / streams host path | ch09-depth, ch07-depth (2) | **Partly** (ch09: 13 SdkLayout mentions, "when it is better") | Small: an exercise in ch09 or ch11 |
| 14 | **MoE / expert parallelism** (all-to-all vs wafer routing) | ch14-depth #7 (1) | **Barely** (ch08: the Kimi K2.6 MoE note) | Small sidebar in ch15 |
| 15 | **Economics and energy** | ch15-depth (1) | **Yes** (ch15 cost/energy calculator with Derived labels) | Done |
| 16 | **Tenstorrent ttsim lab** | ch13-depth, ch13-fixlog (2) | **No** (ttsim is named in ch13/ch15). Feasibility not checked | Defer. Check install feasibility first |
| 17 | **Cross-machine links** (TMA≈CB, SwarmX vs SHARP, NVL72 vs multi-CS-3, reliability at scale) | ch08-, ch13-, ch14-depth (3) | **Partly** (ch14 has TMA pipeline and SwarmX/ring text) | Small edits |
| 18 | **Unbuilt widgets / animations** | fixlogs ch01, 02, 04, 05, 06, 07, 08, 09, 13, 14 (10) | Not built; the fixers judged the prose sufficient | Visual backlog. Not chapters |
| 19 | **Phone layouts and course CSS** (portrait SVGs, `.btn` contrast, `pre.output` wrap, move `.tag.unv` into course.css) | fixlogs ch01, 04, 05, 07, 08, 11, 13, 14; ch10-, ch11-visuals (10) | Only the shared horizontal-scroll fix | One course-wide CSS pass. **Most-raised item overall** |
| 20 | **Research report and notes are stale** (layer-pipelined "not found", 1464 KB/32 B BH, "no official clock") | ch08-depth, ch08-fixlog, ch13-depth, ch13-fixlog (4) | Outside the course | Fix `reports/` and `research_notes/` |

## 2. Verdict

**The course is complete without new chapters, but one new chapter is clearly justified.** Only cluster 1 (collectives) is raised often (5 reviews), is substantial (it does not fit as a box in ch04 or ch11), is central to the "programming the wafer" part, and can be measured with the SDK simulator already in use. Cluster 2 (three machines) also has 5 sources, but ch15 has since absorbed most of it, so a chapter 16 would now mostly repeat ch15. The other repeated clusters (3, 5–9) are reference material that several chapters would link to. These should become appendices, not chapters. The largest single backlog item (cluster 19, phones and CSS) is engineering work, not content.

## 3. Ranked new-chapter proposals

**A. (Recommended) "Lab 4 · Collectives on the wafer"** (after ch11, or as ch13 with Part IV renumbered)
1. Recap: chain reduce and broadcast from Lab 2, with the measured hop costs (2.0/1.0 router hop, 9.2/6.0 through a PE; CCN 20/24).
2. Saving colors with switches: port topic-06. Rewrite Lab 2's checkerboard reduce with one color and SWITCH_ADV control wavelets, which the gemv-08 README promises.
3. `<collectives_2d>` inside: 2 colors per axis, the teardown FSM, root placement. Measure the ≈700-cycle fixed cost.
4. A 2-D allreduce (`benchmark-libs/allreduce`): chain vs tree, with a prediction from c ≈ 9 that the learner then measures.
5. Host-side alternative: `memcpy_h2d_rowbcast/colbcast` (`benchmarks/row-col-broadcast`).
6. Optional finale (cluster 12): two GEMV "layer regions" passing an activation east, timed in cycles per token.
Widget: a chain/tree/2-D reduce cost model with measured points on it. All programs must pass on WSE-3 and WSE-2, as the existing five do.

**B. (Only if ch15 is split) "16 · One token, three machines."** Move ch15's 70B-decode and stencil/GEMM sections here. Add the per-token count of bytes, hops and syncs (HGX TP=8, 4 × CS-3 pinned, Galaxy), the TP=32 vs 4×TP=8 table, HC24 TP-scaling data, and the producer/consumer "same kernel" table. ch15 then keeps only the verdict.

**C. (Low priority) "Lab 5 · Capstone: 3-D stencil and CG."** Based on `stencil_3d_7pts`: pencil decomposition, 8 parity colors, allreduce sync, then `conjugate-gradient`. It depends on A. Only 2 sources.

## 4. Appendix proposals

- **A. Measuring and observing.** sim_stats vs TSC vs inst_trace: what each includes, the 50-cycle idle tail, host-load noise (CCN 17), cross-PE TSC skew (CCN 19), launch/no-stats behaviour (CCN 21), the reusable `<time>`/`make_u48` snippet, and cycles→µs at 850 MHz vs 1.1 GHz (CCN 2). Add one table on "how to see inside" each machine: Nsight Compute, Tracy/device profiler, simulator traces and csdb (marked unverified).
- **B. Glossary and number formats.** Course-wide terms (PE, CE, wavelet, color, DSD, microthread, SM, warp, Tensix, CB, NoC, TP/PP/DP, …) with the chapter that introduces each. Add a single format table (BF16, FP8 E4M3/E5M2, MXFP4/NVFP4, CB16, BlockFP8 with a block size of 16), plus an optional quantisation-error widget. ch13's glossary moves here and ch13 links to it.
- **C. Roofline cheat sheet.** GEMM/GEMV intensity, KV-cache bytes per token, Little's law, the tok/s ≤ BW ÷ weight-bytes bound, each with one worked number taken from ch01, ch14 or ch15.
- **D. CSL and SDK reference.** A tutorial map (gemv-00…09, pipeline, topic-xx, sdklayout-01…05, each mapped to a chapter), task-ID and memory budgets (CCN 12/13), DSD op rates (CCN 14/16/22/23), PE config registers (`@get_config`, 0x7e08…), cslc flags, the SdkRuntime surface, and WSE-2 vs WSE-3 differences.
- **E. Sources and provenance.** What each tag means, the primary documents (HC22, HC24, the WP, the SDK 2.10.1 docs, tt-isa-documentation, …), the ch15 claim checklist as a general method, and a live list of every Unverified figure (section 5).

## 5. Open issues that need follow-up regardless

**Factual or measurement issues not yet resolved**
1. **Bank model disagreement.** The SDK uses 16-bit address units (`word_size = 2`, a 16-byte FIFO stripe). Academic sources say 32-bit words go to successive banks. ch03 presents both. The physical bank width is unpublished (ch03-depth, ch03-fixlog).
2. **Bank and operand clash rule is empirical.** It differs between the chips at N = 64 (ch10-fixlog, CCN 22/23). Strides 4 and 8 cost differently even though they hit the same banks (ch03-fixlog).
3. **WSE-2 `@fadds` rate.** It is 1/cycle when measured in isolation (CCN 16) but 0.5 cycles/cell in Lab 3, where both sources are offset views of one array (ch12-fixlog). ch06 states the caveat, but no mechanism is known.
4. **WSE-2 hop timing oddities.** About 2 cycles/wavelet streaming in the round trip (ch04-fixlog). A ~90-cycle floor for P ≤ 8 (ch11-fixlog). "Each PE's clock starts one hop later" is only Derived.
5. **Shared microthread datapath.** No measurement; the claim stays tagged Secondary (ch03-fixlog).
6. **Undocumented semantics.** Whether a range filter drops before forwarding (ch04). The DSD `.index` unit and scale/norm (ch06). The east mux adaptor placement for 1-row rectangles (ch07). The task-picker tie rule and when the activated bit clears (ch05).
7. **Not re-run or not measured.** Per-wavelet task cost E3 (ch05). D10 back-pressure (ch10). D3 back-pressure figures (ch11). SDK 7-pt/25-pt benchmark numbers (ch12). csdb CTF workflow (ch09, ch11).
8. **ch08 sanity check** still uses "~1 GHz" (24 B × 850k PEs). It should use 1.1 GHz per CCN 2/10.

**Unverified external figures (move them into Appendix E)**
9. NVIDIA: H100 shared-memory/RF bandwidth (ch01). H100 die ~814 mm², 144 SMs, ~700 W, NVLink 0.9 TB/s (ch02). INT32/FP64 lanes, 128 B/clk smem, L1/HBM cycle counts, cluster sizes, TMEM, ping-pong register counts, NVL72 tray (ch14: 9 `.tag.unv`). These need re-checking against docs.nvidia.com.
10. Cerebras: CS-3 12×100 GbE (forum post only). WSE-3 user-visible fabric size (unpublished). Kimi K2.6 config (press only). $8–12M capex. CS-4 power (n/a).
11. Tenstorrent: Grayskull figures, p150 300 W, the 1–2% derating, DeepSeek-R1 tok/s, The Register quote, Galaxy mesh shape (inferred), Wormhole Galaxy power (borrowed), which 20 cores are disabled.
12. ch15: MLPerf absence and the GPU max-TDP figures (from a reviewer web search only).

**Checked as fixed** (keep on a regression list): the Blackhole values in ch15, the B200 tags, the 1,894/88 + 2.5·n text, "at least 7 columns", and ch15 matching ch12's Lab 3 numbers.
