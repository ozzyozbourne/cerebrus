# ch08 · pedagogy review

Summary. The chapter's central idea is strong and correct: training streams weights through the wafer, and inference pins weights onto several wafers. The lede states it in one sentence and the capacity widget makes it concrete. Below that, the mental model is thin. The *why* behind weight streaming (it works because a training step reuses each weight across a huge batch) appears only in a quiz answer. The MemoryX→wafer path is never reconciled with Chapter 7's "narrow door". The four-wafer inference pipeline is shown without saying what each wafer does while the others work. There is no worked bandwidth example linking back to Chapter 1, even though the chapter claims that link. "KV cache" is used three times and never defined anywhere in the course. Objective 3 (a timeline) is not delivered, and the quiz is mostly recall. No critical errors: 6 major, 8 minor.

## Findings

### P1 [major] The reason weight streaming works is only given in the quiz
Location: "Training: weight streaming", paragraph 1; Check yourself Q1.
Problem: The body says weights live off-wafer and stream in one layer at a time, but never says why that is not ruinously slow. The key fact, that each streamed weight is reused across every token in the training batch, first appears in the Q1 answer ("Training processes a large batch per weight load … amortised"). So the learner is tested on reasoning the chapter never taught.
Why it matters: Chapter 7 just told the learner that off-wafer data is slow and "data that matters must stay on the wafer". Without the amortisation argument, weight streaming reads as a contradiction of Chapter 7, not as an application of Chapter 1's arithmetic-intensity idea.
Concrete fix: After the first paragraph of the training section, add:
"Why is streaming affordable? Chapter 1's arithmetic intensity answers it. In training, one layer's weights are used for every token in the batch. With, say, 1,000 sequences of 2,048 tokens, each 2-byte weight takes part in about 2 million multiply-adds per pass, about 2 million FLOP per byte <span class="tag derived">Derived</span> (illustrative batch). That is far right of any ridge point. So the weights need to arrive only once per layer per step, and the link from MemoryX can be orders of magnitude slower than on-wafer SRAM without starving the PEs. Decode at batch 1 has about 1 FLOP per byte, which is why the same trick fails for inference."

### P2 [major] MemoryX bandwidth and the "narrow door" from Chapter 7 are never reconciled
Location: Training section; MemoryX row of the table.
Problem: Chapter 7 ends with "or arrive through dedicated hardware (MemoryX in training, Chapter 8)", and its Q3 says data must "come through MemoryX". Chapter 8 never says how weights physically get onto the wafer, how fast that link is, or whether it is the same 100 GbE path as the SDK's host I/O. The table gives MemoryX capacity but no bandwidth.
Why it matters: The learner was promised an answer to "how do terabytes of weights get past a 14 GB/s door?" and doesn't get one. Bandwidth, not capacity, is the number that decides whether streaming works.
Concrete fix: Add a short paragraph, or a row "MemoryX → system bandwidth" in the table, that gives the figure if the sources have it, or says plainly: "The sources do not give MemoryX-to-wafer bandwidth. The system's external Ethernet (12 × 100 GbE on CS-3 per one forum source <span class="tag analyst">Analyst</span>, ≈150 GB/s) is an upper bound that is at least 10× the SDK's host path in Chapter 7. P1 explains why training needs far less than that." Then cross-link: "This is the 'dedicated hardware' Chapter 7 pointed to."

### P3 [major] The inference pipeline invites the wrong mental model of what the four wafers do
Location: "Inference: pin the weights, stream the tokens" and the "A pipeline of wafers" figure.
Problem: The text says tokens flow "wafer to wafer like a pipeline", but never says that, for one user, a token must pass through wafer 1, then 2, then 3, then 4 before the next token can start (decode is autoregressive). So for one sequence only one wafer is busy at a time. The other wafers are kept busy only by other users' tokens in flight. The term "pipeline parallelism", which Chapter 15 uses, is not introduced.
Why it matters: A learner will assume the four wafers parallelise one user's token, roughly 4× the speed. That is wrong, and it also hides why per-user speed and cost per token diverge (the callout's point).
Concrete fix: Add to the figure caption: "This is <em>pipeline parallelism</em>. For a single sequence, each new token visits the wafers in order, so at any moment only one of the four is working on it. The other three are kept busy only when several sequences are in flight at once. At 2,100 tok/s, one token's full trip through all four wafers takes about 476 µs <span class="tag derived">Derived</span>." Add a quiz question (see P11).

### P4 [major] No worked bandwidth example, though the chapter rests on Chapter 1's argument
Location: Inference section, paragraph 1, and the "What the speed looks like" table.
Problem: "Decode is bandwidth-bound (Chapter 1)" is asserted, then the tok/s results are listed with nothing linking them to bandwidth. The widget's closing line, "bandwidth per byte held is its strength", is never quantified.
Why it matters: This is the moment the learner could see, with numbers, why the architecture wins at decode. Without it, the speed table reads as marketing.
Concrete fix: Add a worked-example box after the table:
"Worked example. At batch 1, every token reads all 140 GB of weights. 2,100 tok/s therefore needs about 140 GB × 2,100 ≈ 294 TB/s of weight bandwidth <span class="tag derived">Derived</span>. One H100 (3.35 TB/s) caps out near 3.35 TB/s ÷ 140 GB ≈ 24 tok/s, and it cannot even hold the model, so it would need two GPUs, about 48 tok/s. Four WSE-3s have about 4 × 21 PB/s = 84 PB/s of SRAM bandwidth, a ceiling of hundreds of thousands of tok/s. So on Cerebras, weight bandwidth is no longer the limit. Inter-wafer hops and compute set the speed (the sources do not break this down). Per byte held, WSE-3 can read all of its memory about 21 PB/s ÷ 44 GB ≈ 480,000 times per second, against about 42 for an H100 <span class="tag derived">Derived</span>." Then the widget's last line has an anchor.

### P5 [major] "KV cache" is used but never defined anywhere in the course
Location: Pipeline figure text, widget hint, widget slider label "Reserve for KV/activations", Q3 answer.
Problem: Chapter 1 covers decode and prefill but never introduces the KV cache (grep of chapters 01–07 finds none). Here it drives a widget control.
Why it matters: The learner cannot set the reserve slider sensibly, and misses the actual reason a wafer "serves relatively few concurrent sequences": every concurrent sequence needs its own KV cache, which competes with weights for the same 44 GB.
Concrete fix: At first use (inference paragraph), add: "Besides weights, decode keeps a <strong>KV cache</strong>: the attention keys and values of every earlier token, one copy per sequence, growing with context length. On a GPU it lives in HBM. On Cerebras it must fit in whatever SRAM the weights leave free, which is what the widget's reserve slider models." In the warn callout, change "a wafer serves relatively few concurrent sequences" to "a wafer serves relatively few concurrent sequences, because each one's KV cache must fit in the SRAM left after the weights".

### P6 [major] The chapter never says how this relates to what the learner will program next
Location: End of chapter (missing bridge to Chapter 9).
Problem: Part II ends here and Part III (CSL) begins. The learner is not told that MemoryX, SwarmX and multi-wafer inference are not things they will touch from CSL/SDK 2.10.1. The labs run on one simulated wafer with memcpy host I/O. Nor does the chapter say whether the on-wafer mapping of "one layer at a time" is documented.
Why it matters: A learner who wants internal behaviour will expect Chapter 9 onward to show how weight streaming is coded, and will be confused or disappointed.
Concrete fix: Add a closing callout before the quiz: "<strong>Where this sits for a CSL programmer.</strong> Weight streaming and multi-wafer inference are run by Cerebras's machine-learning software stack, not by programs you write with the SDK. The SDK targets one wafer (or the simulator), and its host path is the memcpy runtime of Chapter 7. How a layer is mapped onto the PE grid during weight streaming is not documented in the sources used for this course. The labs in Chapters 10–12 show the building blocks (broadcast, neighbour exchange, reduction) such a mapping would need."

### P7 [minor] Training: the backward pass and activation memory are skipped
Location: Training section and figure.
Problem: The paragraph and figure describe a forward stream (weights in) and gradients out, but not the order: forward layer 1…N, then backward N…1, with weights streamed again. Nor do they say that activations from every layer must be kept (or recomputed) for backward, which is what actually bounds per-wafer batch under "activations stay on the wafer".
Why it matters: "Activations stay on the wafer" sounds free. A strong learner will immediately ask where the activations of all layers fit.
Concrete fix: Add: "A step runs forward through layers 1…N, then backward N…1. Each layer's weights are streamed in again for its backward step, and that layer's gradients flow out through SwarmX at the same time. The activations needed for backward must stay on the wafer (or be recomputed), so wafer SRAM still limits batch per wafer. It just no longer limits model size. The sources do not describe how Cerebras manages this."

### P8 [minor] Why linear scaling follows, and why a separate SwarmX exists, is left implicit
Location: Figure caption "adding systems is pure data parallelism".
Problem: "Data parallelism" is not defined, and the caption doesn't say *why* weight streaming removes the need for model (tensor/pipeline) parallelism: only one layer must fit at a time, and any layer fits on any wafer. It also doesn't say why broadcast and reduce get their own box rather than MemoryX talking to each system.
Concrete fix: Replace the caption's first sentence with: "<b>Weights in, gradients out.</b> Only one layer must fit on a wafer at a time, so no system ever needs a <em>part</em> of the model. Each system runs the same layer on its own slice of the batch (<em>data parallelism</em>). The only cross-system work is sending each layer's weights to everyone and summing everyone's gradients, which SwarmX does as a broadcast/reduce tree between MemoryX and the systems. Cerebras frames the result as 'linear scaling' <span class="tag vendor">Vendor</span>." Also add arrowheads (or a "↕" label) to the SwarmX→CS-3 lines in the SVG, which currently have no direction.

### P9 [minor] Objective 3 ("timeline") is not delivered
Location: Objectives list, item 3; the "system around the wafer" table.
Problem: There are no dates in the table except "CS-4 (2026)". CS-1 is absent. There is no timeline visual. The table also mixes units across a row (CS-4's "System" cell gives rack compute, memory bandwidth and I/O, while the others give power).
Concrete fix: Change the column headers to "CS-2 (2021)", "CS-3 (2024)", "CS-4 (Aug 2026)", and add a first row "Execution mode": "layer-pipelined → weight streaming (2021)" / "weight streaming; inference service Aug 2024" / "positioned for frontier inference". Either add a small horizontal SVG timeline (2019 CS-1, 2021 CS-2 and weight streaming, Aug 2024 inference launch with 4 × CS-3, 2026 CS-4), or reword the objective to "Compare the CS-2, CS-3 and CS-4 systems with the right numbers."

### P10 [minor] Undefined or un-linked jargon in the table
Location: The table and its note.
Problem: "WSE-3T", "15U", "EF/PF", "sparse", "RoCE v2" and "Direct Wafer Links" appear with no gloss here. "CS-3" (system) vs "WSE-3" (wafer) is never spelled out in this chapter, though the figures label boxes "CS-3". Also, MemoryX looks like it *shrank* from CS-2 (2.4 PB) to CS-3 (1.2 PB) with no explanation.
Concrete fix: Under the table, add: "A CS-<i>n</i> is the system (cooling, power, I/O) built around one WSE-<i>n</i> wafer. CS-4 is the exception: a rack holding three WSE-3T wafers, the higher-clocked WSE-3 variant from Chapter 2. 'Sparse' FLOPs are the inflated vendor figure explained in Chapter 2. RoCE v2 is RDMA over standard Ethernet. Direct Wafer Links are vendor-described switchless wafer-to-wafer links. MemoryX capacities are the largest configurations quoted in different sources, not a regression."

### P11 [minor] The quiz is mostly recall and misses the chapter's two key ideas
Location: Check yourself.
Problem: Q2 is pure recall. None of the questions tests the pipeline model (P3) or the per-user vs per-token cost trade-off (the callout). Q1's answer leans on reasoning the body lacks (P1), and its "as bandwidth-bound as a GPU" understates the case: per Chapter 7, off-wafer paths are slower than HBM.
Concrete fix: (a) Rewrite the Q1 answer's last clause as "…streaming weights would make every token wait on the off-wafer link, which is far slower than SRAM and, from the SDK figures in Chapter 7, slower than a GPU's HBM." (b) Replace Q2 with: "One user is generating with Llama 70B on four CS-3s. While wafer 3 processes their token, what are wafers 1, 2 and 4 doing?" Answer: "Nothing for that user, because the next token cannot start until this one leaves wafer 4. They stay busy only with other users' tokens in flight. That is why per-user speed and total throughput are separate numbers." (c) Add: "A CS-4 rack has three 44 GB wafers. Can it hold Llama 70B at 16-bit with weights pinned?" Answer: "No: 3 × 44 = 132 GB < 140 GB before any KV cache. At 8-bit (70 GB) it fits with about 62 GB to spare <span class="tag derived">Derived</span>."

### P12 [minor] Q3's answer disagrees with the widget's default
Location: Q3 answer vs widget default reserve of 20%.
Problem: Q3 says "≈ 19 wafers before any KV cache". A learner who checks with the widget at its default gets 23 (810 / 35.2) and may think one of them is wrong.
Concrete fix: Append to the Q3 answer: "With the widget's default 20% reserve for KV cache it is 23. Set the reserve to 0% to reproduce 19."

### P13 [minor] The trillion-parameter result is left unexplained against the capacity widget
Location: Speed table, Kimi K2.6 row.
Problem: The widget tells the learner that a 1,000B model at 16-bit needs about 46+ wafers (at least 57 with the default reserve). The table then reports 981 tok/s for a ~1T model with no word on how it was deployed (precision, number of wafers, MoE). The learner is left with a contradiction.
Concrete fix: Add after the table: "The widget says a dense 1T-parameter model at 16-bit would need dozens of wafers. The sources do not state the precision or wafer count Cerebras uses for Kimi K2.6 (a mixture-of-experts model, so only a fraction of weights are read per token, though all must still be resident), so treat this row as a capability claim, not a recipe."

### P14 [minor] Small inconsistencies: title, the word "stream", and the hidden widget overflow label
Location: `<title>` vs `<h1>`; lede; widget script.
Problem: (a) The `<title>` is "Systems: CS-3, MemoryX, SwarmX", but the `<h1>` adds CS-4. (b) "Stream" means three different things in adjacent chapters: SDK streaming mode (Chapter 7), weight streaming, and "stream tokens" here. (c) In the widget, the "… N wafers total" label is drawn at y=140 inside a `viewBox` 120 tall, so it is never visible when more than 40 wafers are needed.
Concrete fix: (a) Make the `<title>` match: "Systems: CS-3, CS-4, MemoryX". (b) In the lede, add after the first sentence of strategies: "(Neither is the SDK's 'streaming mode' from Chapter 7.)" Alternatively, change "streams tokens through them" to "passes tokens through them". (c) Change the SVG to `viewBox="0 0 680 150"` (or draw the label at y=118 and cap rows at 2), so the overflow label shows.
