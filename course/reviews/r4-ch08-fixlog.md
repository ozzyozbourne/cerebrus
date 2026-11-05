# R4 fix log: Chapter 8 (08-systems.html)

## Items from reviews/r4-ch08.md
- **E1** Fixed. Quiz Q1 now says "~150 GB/s per CS-3 wafer, about 1/20 of one H100's 3.35 TB/s HBM".
- **E2** Fixed. False quotation removed; Ch07's point paraphrased without quote marks and linked to 07#copy-path.
- **E3** Fixed. Callout: "extracts the model graph (TensorFlow via XLA in the 2020 slides, PyTorch today), lowers it to LAIR".
- **E4** Fixed here already (Vendor, HC22); the Ch01/Ch02 retag is for other pages (below).
- **E5** Partly (Ch08 half). Added: "WSE-3 Turbo" is the vendor's name for WSE-3T, so Cerebras itself attributes the speed-up to clock; added the item-33 clock range (~1.4 / ~2.8 GHz press estimate, Analyst + Unverified, vs SDK 850 MHz). Ch02 half is below.
- **E6** Fixed. Claims row now carries ">4,400 tok/s per user on gpt-oss-120B (AI Weekly)" with Vendor + `tag unv` spans and links to Ch9 #budget and Ch18; plain-text "Unverified." replaced.
- **X1** Fixed. Sentence added after the 140,000× paragraph: the reuse is physical (column multicast over every token's activations), with a link to #layer.
- **X2** Fixed. Defined loss delta, user node (host CPU server running the training script), why transposed (dX = dY·Wᵀ, dW = Xᵀ·dY), and why the last layer is retained.
- **X3** Fixed. New paragraph in #memoryx on mixed precision, FP32 masters and Adam's two moments.
- **X4** Fixed. TP/PP parenthetical, glossary g-tp-pp-dp and link to Ch17 #scaling.
- **X5** Fixed. Links to Ch1 #two-numbers, Ch2 #generations, Ch3, Ch4 #routes/#control-wavelets, Ch5 #activates, Ch6 #fabric-dsds, Ch7 #modes/#copy-path, Ch9 #pipeline/#cap/#budget/#moe/#compile, Ch11–15, Ch14, Ch17, Ch18; 17 glossary links (weight-streaming, memoryx, swarmx, multicast, data-task, arithmetic-intensity, ridge-point-roofline, tp-pp-dp, layer-pipelined-mode, pinned-weight-inference, dense-sparse-flops, wse-2-wse-3-wse-3t, dataflow-sparsity, hgx-nvl72, disaggregation, decode-prefill, lair). All ids checked.
- **X6** Fixed. NVL72 Rubin, AMD Helios, "expert" (MoE) glossed with glossary/Ch9/Ch17 pointers.
- **G1** Fixed (with caveat). New warn callout: GPT-3 XL at 250k tokens -> ~1 GB per layer output, ~25 GB for 24 layers (Derived); full intermediates would not fit; recompute / smaller shards named as usual ML answers; explicit "sources do not say which Cerebras uses" (Unverified). No source found in research notes.
- **G2** Fixed. "Which bytes cross the link?" paragraph: dense 2 B per crossing (vendor 32 bits each way); fabric packet value+index; sparse non-zero likely 4 B, so sparsity cuts link bytes only above 50% zeros (Derived); where the dense index is attached is Unverified.
- **G3** Fixed. New paragraph "Why a row reduction?" plus a 4-step widget (#mm) computing Y = X·W for X=[[1,2],[3,4]], W=[[5,6],[7,8]] on 4 cores (multicast/FMAC -> PSUM -> FSUM, twice); plus a CSL-terms paragraph mapping multicast route (Ch4), data task / @fmach with fabric DSD (Ch5/6), PSUM/FSUM as control wavelets (Ch4), Lab 4.
- **G4** Fixed. Worked example bullet: the knee is Ch1's off-wafer ridge point (~100,000 FLOP/B vs widget's 104k for WSE-3).
- **G5** Fixed. "about 25 sequences of 2,048 tokens per wafer".
- **G6** Not this page (Ch09 text); listed below.
- **G7** Fixed. New SwarmX tree figure (#sx): MemoryX root, 1 + 4 B-R 1:4 nodes, 16 CS-3 leaves; caption explains linear node count / log depth.
- **G8** Fixed. "A training step in one paragraph" callout before the weight-streaming text.

## Items 30–38
Page has no DSD rates, launch(), hop-cycle or queue-depth text. Item 33 (clock) applied in #cs4; item 36 already correct; item 38 applied (see X5).

## Cross-page items about Ch08 from other r4 reports
- r4-ch01 G2, r4-ch02 G5, r4-ch09, r4-ch16 G11, r4-ch17 G1: all fixes live on those pages; nothing to change in Ch08.

## Verification
Playwright, 1100 px light and 390 px dark: zero console/page errors, no horizontal overflow; drove #mm (all 5 states), #ws Step, #tpw wafer select (knee 104k), #sx rendered. All new anchors (in-page and cross-page) checked against existing ids.

## For other pages
- **Ch01** (01-memory-wall.html) roofline table: WSE-2 FP16 dense 7.5 PF -> tag Vendor (HC22), item 36 / r4-ch08 E4.
- **Ch02** (02-the-wafer.html): spec table "~7.5 PF dense Analyst" -> Vendor (HC22); #flops-area text: the 10:1 WSE-2 ratio is vendor-stated, only WSE-3's 8:1 is an analyst assumption (E4). Spec note on WSE-3T clock: Cerebras does attribute it to clock ("twice as much power to the WSE-3 Turbo, enabling higher operating frequencies"; cite Ch08 #cs4) (E5).
- **Ch09**: #budget "Chapter 8 ended with 'the sources do not break this down'" and the experiment box "reproduces Chapter 8's benchmark run (10,160 cycles)" are dangling; reword as self-contained (G6).
- **Ch17**: "(Chapter 8)" pointers for the wafer decode budget should be "Chapters 8–9" (r4-ch17 G1); Ch16 quiz likewise (r4-ch16 G11).
