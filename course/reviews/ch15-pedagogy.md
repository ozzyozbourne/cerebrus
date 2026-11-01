# ch15 · pedagogy review

Summary: As a capstone, the chapter is honest and well sourced in spirit. The "fair reading" callout and the evidence table are its best parts. As synthesis it is weak. The two big tables mostly restate chapters 13 and 14 (the Tensix-vs-PE table in ch13 is nearly the same as column 1 and 2 here). The chapter never names its comparison axes or ties them back to the course's core idea, the ridge point and memory wall from ch01. The decision guide is a static list of four assertions with no link to the evidence rows. Two of the "what programming the wafer taught us" lessons claim more than the labs show. The final check has three recall questions and nothing that makes the learner apply the course. Every gap below can be fixed in this one file, without new research.

## Findings

### P1 [major] Comparison axes are never named or justified
- **Location:** lede ("compares them on the axes that matter"), widget `#cmp`, the "Architecture and memory" table.
- **Problem:** the chapter promises "the axes that matter" but never says what they are or why they matter. The widget offers six metrics with no framing. One of them, "Compute units", the note itself calls "not comparable". The learner has to work out alone why on-chip SRAM, main-memory bandwidth and peak FLOP/s are the right axes. The ch01 ideas that make them meaningful (ridge point = FLOP/s ÷ bytes/s, decode at ~1 FLOP/B) never appear in the chapter body. The only trace is the phrase "below the ridge point" buried in the NVIDIA weakness cell.
- **Why it matters:** a learner finishing the course should come away with a method for comparing accelerators, not a pile of numbers. Without named axes, the widget is a trivia browser and the tables read as a repeat.
- **Concrete fix:** add a short "How to compare" section before the widget, with three axes, each tied to an earlier chapter:
  1. **Where the weights live, and how fast you can read them.** Capacity × bandwidth (ch01, ch02).
  2. **How much compute per byte.** The ridge point (ch01).
  3. **How work and data are placed.** The programming model (ch09–ch14).
  4. Then name **cost and power** as the axes the evidence covers least well.

  Add a derived widget metric, "Ridge point (FLOP per byte of main memory)", computed from the existing rows (e.g. H100 989e12/3.35e12 ≈ 295). Tag it Derived, and add a readout sentence comparing each value with decode's ~1 FLOP/B. Drop "Compute units", or move it to a footnote.

### P2 [major] Tables repeat chapters 13/14 instead of synthesising
- **Location:** "Architecture and memory" table and "Programming model" table.
- **Problem:** most cells copy earlier tables. The Cerebras and Tenstorrent columns match ch13's "Tensix vs the Cerebras PE" table almost row for row (48 KB vs 1,464 KiB, 32 GB GDDR6, 2-D mesh vs two tori, openness). No row states a conclusion, and no row says "so what". The one real synthesis idea is at the very end, in the quiz answer to Q3 ("both use explicit, software-scheduled data movement ... CSL is finer-grained"). It belongs in the body.
- **Why it matters:** at the capstone, re-reading the same facts in a new layout adds little. What a learner needs is the cross-cutting pattern: two designs answer the memory wall by moving data explicitly between private SRAMs, and one hides latency with threads and caches. Those choices explain the evidence that follows.
- **Concrete fix:** add a final "Consequence" row to each table, e.g. Architecture: "weights must fit in SRAM across many wafers / weights stream from slow DRAM every token / weights stream from fast HBM, batching amortises". Programming: "you place data and routes / you schedule DMA around tiles / the hardware hides latency if you give it enough threads". Lift the Q3 grain comparison into a paragraph under the programming figure. Link each column header to its source chapter (ch02/03, ch13, ch14), so the tables work as a recap index rather than new content.

### P3 [major] Decision guide does not follow from the evidence shown
- **Location:** "Choosing" figure `#dg`, rows 1–4.
- **Problem:**
  - None of the four rows cites the evidence table or the strengths/weaknesses table above it.
  - Row 4 ("Low cost, open stack") picks Tenstorrent on cost, yet the evidence table has no cost figure for Tenstorrent, and the fair reading admits "no independent benchmark".
  - Row 3 ("Highest throughput per dollar") rests on one analyst/GPU-vendor pricing row, which the accuracy review (A5) flags.
  - Row 1 says "a model that fits in a few wafers" but never makes concrete the weakness listed just above: 70B at FP16 needs 4+ systems at ~23 kW each.
  - Training is not covered, although MemoryX/SwarmX is discussed under Scaling.
  - Energy, which the lede frames as part of the memory-wall story, is absent. The caption mentions power only as an aside.
- **Why it matters:** the chapter says it "states plainly what the evidence does and does not show". The decision guide then gives verdicts the evidence cannot support. A careful learner will notice the gap, and that weakens the honest tone the chapter worked to build.
- **Concrete fix:** give each row a third column, "because", that cites the evidence:
  - Row 1: "981 tok/s Kimi, 2,314 tok/s Llama 70B (Indep); capacity ≈ 44 GB per wafer".
  - Row 2: "MD 179× (Peer-reviewed), but the authors' caveat".
  - Row 3: "$0.10–0.25 vs $0.60 per M tokens (GPU-cloud estimate)".
  - Row 4: "list price and open source; no independent performance data".
  - Add a fifth row, "Large-scale training: no independent comparison found; GPU by default, Cerebras via MemoryX/SwarmX is vendor-reported only". Alternatively, make it a small interactive: the learner picks workload, batch size and model size, and the figure highlights the evidence rows that apply.

### P4 [major] Lesson 1 overclaims: "Every bug was ... None was a wrong formula"
- **Location:** "What programming the wafer taught us", bullet 1.
- **Problem:** the labs support only two of the three named bugs.
  - The command-stream race is fully documented (ch10 bug callout, program 02).
  - The microthread clash is fully documented (ch12 bug callout, stall at cycle 1,894).
  - The "mutability flag" bug appears only as a one-line code annotation in ch09 ("We got this wrong once in program 02"). No lab explains its symptom or fix.
  - ch11 documents a compile error from un-braced `if/else`, which is a language/syntax issue, not a resource issue. "Every bug" is therefore contradicted inside the course.
- **Why it matters:** this section is the course's first-hand evidence, the part learners will trust most. An absolute claim that the labs partly contradict undercuts it.
- **Concrete fix:** reword to "Every runtime bug we hit was about resources: a race on the command stream (Lab 1, ch10), two fabric operations sharing a microthread (Lab 3, ch12), and an export declared with the wrong mutability (ch09). The arithmetic was never wrong." Link each item to its chapter. Optionally add the mutability symptom and fix to the ch10 bug callout, so the claim has a lab behind it.

### P5 [minor] Lesson 4: the 2-cycle repeatability is not in the labs, and the GPU contrast is unsupported
- **Location:** bullet 4 ("totals varied by at most 2 cycles between reruns ... That is harder to get on a GPU").
- **Problem:** no lab page reports rerun variance; only ch09 mentions it, in passing. The labs' measurement method (0 vs 100 steps, ch12) supports "pin per-step cost to within a cycle" (128 vs 128.5). The rerun figure, however, has no table or Measured tag. "Harder to get on a GPU" is asserted with no comparison. Also, the programming-model table gives CUDA "—" for simulator, and the learner has not been told why that matters.
- **Why it matters:** the lesson is about evidence quality. It should model that quality itself.
- **Concrete fix:** add `<span class="tag measured">Measured</span>` and a pointer to ch12's measurement table. Replace the GPU sentence with something the course supports, e.g. "A GPU profiler measures real hardware, with run-to-run variance from clocks and scheduling. The simulator trades speed and scale (we simulated ≤ 16 PEs) for exact repeatability." That also names the simulator's limit, which this section omits.

### P6 [minor] Lesson 3 cherry-picks 8→16 PEs; the 2-PE point (99 cycles) goes unexplained
- **Location:** bullet 3 ("Going from 8 to 16 PEs cost nothing per step").
- **Problem:** ch12's table shows P = 2 at 99 cycles/step, against 128 at P = 8 and 128.5 at P = 16. A learner who goes back to the lab will see that per-step cost is not flat from 2 to 8. The likely reason is that with P = 2 both PEs are edge PEs with one neighbour each. Neither ch12 nor ch15 explains it.
- **Why it matters:** "weak scaling is effortless" is a headline lesson. Leaving out the data point that seems to contradict it invites doubt, and it misses a good teaching moment: cost becomes flat once interior PEs exist.
- **Concrete fix:** "Once every interior PE has two neighbours (P ≥ 3), per-step cost is flat: 128 cycles at 8 PEs, 128.5 at 16 (ch12). At P = 2 there are only edge PEs, so each step is cheaper (99)." Also state the break-even point for bullet 2: 88 / 2.5 ≈ 35 cells per PE, where compute starts to outweigh communication. That replaces the vague "dozens".

### P7 [major] Final check is three recall questions; nothing makes the learner apply the course
- **Location:** `.quiz` "Final check".
- **Problem:**
  - Q1 is answered almost word for word by ch01 and by the chapter's own lede.
  - Q2 repeats the fair-reading callout.
  - Q3's answer holds the chapter's best synthesis idea (see P2).
  - No question uses the labs, the evidence-quality theme, or the decision guide. Three questions is the same count as an ordinary chapter, although this is the course's last chapter.
- **Why it matters:** a capstone quiz is where a learner checks they can transfer what they learned. These questions only check that they read this page.
- **Concrete fix:** keep Q1, and add 3–4 application questions with worked answers:
  - (a) "A 400B-parameter model at FP16 must serve 50 tok/s/user to 10,000 users. Roughly how many wafers hold the weights, and which platform does the evidence favour? What evidence is missing?" (≈ 800 GB / 44 GB ≈ 19 wafers; the decision depends on throughput per dollar, where only analyst data exists.)
  - (b) "Using 88 + 2.5n, how many cells per PE before compute takes more than half of each step? What would you change in the program to lower the 88?" (n ≈ 35; overlap the halo exchange with the interior update.)
  - (c) "Which row of the evidence table would you trust least, and why?" (The gpt-oss vendor claim against the independent measurement.)
  - (d) "Compute the ridge point for H100 and B200 and say what it means for decode."

### P8 [minor] Jargon in the strengths/weaknesses table is used without definition or a back-link
- **Location:** "Strengths and matching weaknesses" table, plus the evidence and scaling text.
- **Problem:** several terms appear in ch15 only:
  - "spec slippage", "strong scaling" and "TTFT" (170 ms TTFT) are used nowhere else in the course.
  - "WSE-2/3 portability traps" is a compressed reference to ch05.
  - "de-rated shipping hardware" is defined only in ch13's prose ("firmware de-rating").
- **Why it matters:** a learner finishing the course should be able to read every cell. Undefined shorthand in the summary table makes it look as if they missed a chapter.
- **Concrete fix:**
  - Define strong vs weak scaling in one sentence, ideally in lesson 3: "strong = fixed problem, more PEs; weak = problem grows with PEs".
  - Expand TTFT to "time to first token".
  - Replace "spec slippage" with what happened (e.g. "announced specs revised before shipping"), or delete it.
  - Make each weakness cell link to its source chapter: "24 colors minus 4" → ch04/ch07, "portability traps" → ch05, "narrow host I/O" → ch07, "de-rated" → ch13.

### P9 [minor] No objectives block, no course recap and no "where next"
- **Location:** top and bottom of the chapter.
- **Problem:** chapters 01, 13 and 14 open with an `.objectives` block; ch15 has none. The chapter also ends abruptly after the quiz. It never revisits the memory-wall question the course opened with, and gives no pointers on (SDK tutorials/benchmarks, the 7-point/25-point stencil benchmarks mentioned in ch12, the research report).
- **Why it matters:** a capstone should tell the learner what they can now do and where to go next. Without that the course just stops.
- **Concrete fix:** add `.objectives`, e.g.:
  - "compare three accelerators on capacity, bandwidth, ridge point and programming model"
  - "say which claims are independently confirmed"
  - "pick a platform for a workload and justify it"

  End with a short "Back to the memory wall" closing paragraph: one sentence per vendor on how it answers ch01's question, and how the labs confirmed the Cerebras answer. Follow it with a "Where to go next" list (SDK tutorials directory, benchmarks, research report).

### P10 [minor] The Scaling section is a dense paragraph with no visual
- **Location:** "Scaling" `<p>`.
- **Problem:** one paragraph holds three scale-up/scale-out hierarchies and five product names (NVLink/NVSwitch, InfiniBand, MemoryX, SwarmX, Direct Wafer Links/CS-4). This in a course built around visuals, and in the chapter where a side-by-side picture would help most.
- **Why it matters:** "scale-up happens on the wafer itself" is one of the chapter's sharpest synthesis points, and here it is hard to pick out.
- **Concrete fix:** replace the paragraph with a three-column figure or table that has rows "inside one chip/wafer", "scale-up domain" and "scale-out". Example cells: Cerebras "900k PEs on-wafer mesh / — / MemoryX+SwarmX (training), Ethernet pipeline (inference)"; NVIDIA "SMs via L2 / NVLink, 8 (HGX) or 72 (NVL72) / InfiniBand-Ethernet"; Tenstorrent "Tensix NoC / Ethernet mesh / same Ethernet". Bold the on-wafer cell, and link MemoryX/SwarmX to ch08.

### P11 [minor] The CSL panel of the programming-model figure shows only east-west links
- **Location:** `#pm` drawing loop (only horizontal `line` elements between PEs).
- **Problem:** the 4×4 PE grid draws only horizontal links. A learner could read it as rows of 1-D chains, which contradicts "2-D mesh" in the table above and the north-south broadcast in Lab 2 (ch11).
- **Why it matters:** this is a small visual inconsistency, but it is the last picture of the fabric the learner sees.
- **Concrete fix:** add vertical links (`if (r < 3) el("line", {x1: 559 + c*50, x2: 559 + c*50, y1: 70 + r*48, y2: 82 + r*48, ...})`), and give one route a highlight colour to suggest "routes you declared".
