# ch03 · pedagogy review

Summary: The chapter has the right shape: anatomy figure, memory, compute, control, why no caches, sparsity. The memory-budget widget is a good hands-on hook. But the chapter names parts more than it explains how they work together, so a learner ends up with a parts list rather than a working mental model. Three explanations are wrong or misleading:
- what "eight microthreads" means for throughput;
- what the matvec "relative vs absolute" bandwidth actually measures;
- why sparsity is "free".

Two terms the chapter relies on, wavelet and color, are only defined in Chapter 4. The f32 throughput question that every lab depends on is never raised. The Check-yourself questions test only recall and leave the sparsity objective untested. Nothing is critical; most fixes are a paragraph or a corrected figure.

## Findings

### P1 [major] "Eight operations at once" suggests eight datapaths; microthreads are never defined
**Location:** "Compute: SIMD lanes driven by descriptors", 3rd–4th sentences ("It can run up to eight such operations at once, one per microthread"). Anatomy figure: "8 microthreads" box next to "Not here: ✕ OS / threads". Quiz Q3.

**Problem:** The chapter never says what a microthread is. Its parts, sources (vendor: "eight simultaneous tensor operations, which we call micro-threads"; secondary: the scheduler switches among them every cycle based on operand availability) and the figure leave out that the eight contexts share one SIMD datapath. A strong learner will read "eight operations at once" as up to 8× throughput. The same figure also says "no threads" right beside "8 microthreads", which contradicts itself on first reading.

**Why it matters to the learner:** This sets their performance intuition for the rest of the course. Microthreads overlap communication with compute (a receive, a send and an add in flight together). They do not multiply FLOPs. Without this point, the Chapter 5 and 6 material on async ops and the Lab 3 microthread hang reads as arbitrary rules rather than the consequence of a shared resource.

**Concrete fix:** Replace the sentence "It can run up to eight such operations at once, one per microthread." with:
> "A **microthread** is a hardware context that holds one in-flight vector operation: its DSDs, its progress, and what to activate when it finishes. A PE has eight of them <span class="tag vendor">Vendor</span>, so up to eight vector operations can be *in flight* at once, for example receiving from the west, sending east and adding locally. They share the single SIMD datapath, and the hardware interleaves them according to which one has operands ready <span class="tag indep">secondary source</span>. The gain is overlap, not 8× the FLOPs. Microthreads are not software threads: there is no scheduler, stack or OS behind them."

In the figure, change "✕ OS / threads" to "✕ OS / software threads".

### P2 [major] The GEMV relative/absolute bandwidth figure misstates what is reused, and gives no numbers
**Location:** "Why no caches?" figure and its caption.

**Problem:** The figure says the cached machine "reads x once into cache, reuses it for every row → counts 'relative' bandwidth that never touches DRAM". The benchmark source says something different (`benchmarks/single-tile-matvec/run.appliance.py`, comments above `total_relative_accesses`). STANDARD = read x once, read A once, write y once = 4·nb² + 8·nb bytes. ACTUAL on WSE = the same, plus *read and write the whole y vector nb times* = 12·nb² + 4·nb bytes. What a cached machine absorbs is the **y accumulator** (kept in registers or cache and written once), not x. The caption's phrase "what a cache would have to supply" is also backwards. "Relative" is the traffic a conventional memory system would see, with the cache absorbing the rest. The sentence "bandwidth that never touches DRAM" does not parse as a definition.

**Why it matters to the learner:** This is the chapter's only worked case for "why no caches". As written it teaches the wrong reuse pattern. It also misses the striking result: the WSE does about 3× more memory traffic than a cached machine and is still fast, because each PE's SRAM bandwidth is private.

**Concrete fix:**
- Left box text: "A cached machine: reads A and x once, keeps the running y in registers/cache, writes y once → 4·nb² + 8·nb bytes ('relative')".
- Right box text: "The WSE: column-by-column @fmacs reads and writes the whole y for every column → 12·nb² + 4·nb bytes ('absolute'). Every one is a real SRAM access."
- Replace the caption with: "**The SDK's single-tile matvec benchmark counts memory traffic both ways** <span class="tag sdk">SDK 2.10.1</span>. 'Relative' is the bytes a cached machine would move; 'absolute' is the bytes the WSE's SRAM actually serves. For nb = 64: 16,896 B vs 49,408 B, about 2.9× <span class="tag derived">Derived</span>. Nothing absorbs the accumulator's reuse here. The design bets that single-cycle local SRAM can serve the extra traffic. The 512 B software-managed cache exists for exactly this kind of hot accumulator."

### P3 [major] "Sparsity is free" is overclaimed; its costs and the hardware/software split are missing
**Location:** Objective 3; section "Sparsity comes free with dataflow"; wavelet figure and caption.

**Problem:**
1. The section never states the costs:
   - the sender must still detect zeros;
   - packing an index halves the payload to 16 bits, so a value of the f32 type that every lab uses cannot travel this way;
   - a 16-bit index addresses at most 65,536 positions;
   - each non-zero arrives as a separate data-task activation, with scatter work on the receiver;
   - uneven non-zeros across PEs cause load imbalance.
2. It mixes the hardware feature (HC34/MICRO-54: dataflow triggering, zeros filtered at the sender) with an SDK tutorial convention (topic-04 index-in-upper-16-bits) without saying which is which.
3. "This mechanism is what Cerebras's sparse-FLOPS headline numbers assume" is misleading. The headline peaks count skipped zero multiplies as if they were performed, at an assumed sparsity ratio (analysts assume 8:1 or 10:1; see Chapter 2).
4. The figure labels the low half "f16 value", but the caption's task signature is `wavelet_data: i16`. That is the SDK tutorial's actual type; an f16 would need a bitcast.

**Why it matters to the learner:** "Free" is a marketing word. The course's own standard, set in Chapter 2's "Read the FLOPs carefully", is to separate peak claims from mechanism. A learner should leave able to say when sparsity pays off and when it does not.

**Concrete fix:**
- Rename the objective to "Explain why the WSE has no caches, and how dataflow lets it skip zeros (and what that costs)". Retitle the section "Sparsity: skipping zeros with dataflow".
- Replace the last sentence of the paragraph with: "The filtering of zeros at the sender is a hardware feature <span class="tag vendor">Vendor, HC34</span>. Packing an index into the upper half is a software convention from the SDK tutorial. Cerebras's sparse-FLOPS peaks count the skipped multiplies as if they were done, at an assumed sparsity ratio (Chapter 2)."
- Add a short "What it costs" list after the figure:
  - the sender still checks every value;
  - index + value means 16-bit data only, so f32 values do not fit;
  - indices stop at 65,535;
  - each non-zero is one task activation on the receiver;
  - PEs with more non-zeros finish last.

  End the list with: "Skipping zeros pays off when sparsity is high and unstructured enough that a dense SIMD op would mostly multiply zeros."
- Change the figure label to "lower 16 bits: 16-bit value (i16 in the SDK example; f16 via @bitcast)".

### P4 [major] Wavelet, color and router are used before they are defined
**Location:** Anatomy figure ("Router · 24 colors"); lede ("five-port router"); sparsity section ("a wavelet is 32 bits").

**Problem:** Chapter 4 is the first to define wavelets and colors. In ch03, "24 colors" is unexplained, and the sparsity argument depends on the learner knowing that a wavelet is the unit of fabric traffic and that its arrival triggers a task.

**Why it matters to the learner:** The "why sparsity is cheap" argument cannot land if the learner does not know what is being sent or why its arrival causes work.

**Concrete fix:** Add a short paragraph "The router, in one paragraph" after the "Control" subsection:
> "Each PE's router has five ports: N, S, E, W to the neighbours, and the RAMP down to its own CE. PEs share no memory. They exchange **wavelets**, 32-bit messages that hop one router per cycle. Each wavelet carries a **color**, one of 24 tags that select a pre-configured route at every router, and a task at the receiver. Chapter 4 covers routing in full. For now, the key fact is that a wavelet coming down the RAMP is what wakes the CE."

In the figure, change "24 colors" to "24 colors (route tags, Ch. 4)".

### P5 [major] No step-by-step trace that ties the parts together
**Location:** Whole chapter, between "The anatomy" and "Why no caches?".

**Problem:** The parts are described one at a time: SRAM, cache, GPRs, DSRs, SIMD, picker, microthreads, router. The chapter never shows them working together. Objective 1 ("Draw a PE and name its parts") is met only as naming. The learner never sees how the parts interact.

**Why it matters to the learner:** A technically strong reader builds a model by following one event through the machine. Without that trace, Chapters 5 and 6 arrive as new concepts rather than as zoom-ins on a picture the learner already has.

**Concrete fix:** Add a subsection "One wavelet's journey through a PE" with a numbered list (or a 5-step animated highlight on the anatomy SVG). Use Lab 2's row reduction, `@fadds(out_dsd, in_dsd, v_dsd, .{.async=true, ...})`:
1. A wavelet of color c arrives at the router's WEST port. The route table says RAMP, so it goes down to the CE's input queue.
2. Earlier, a task issued the `@fadds`. Its three DSDs (fabric-in, memory v, fabric-out) are in DSRs, and the op is parked on a microthread.
3. The microthread has an operand ready, so the datapath adds the wavelet to `v[i]`, read from an SRAM bank in one cycle.
4. The result goes back up the RAMP and out EAST.
5. After the last element, the microthread finishes and activates a completion task. The task picker runs it when it is activated and unblocked.

Add one closing line: "Every later chapter zooms into one of these steps: routing (Ch. 4), tasks (Ch. 5), DSDs (Ch. 6)."

### P6 [major] The bandwidth "sanity check" is not connected to compute, so the "why" of the design is missing
**Location:** "Memory: 48 KB, one cycle, nothing else", last sentence.

**Problem:** "≈ 23 GB/s per PE, a few 32-bit accesses per cycle" is left hanging. The interesting question for this learner is whether memory keeps up with the SIMD unit. That is the per-PE version of Chapter 1's roofline, and the chapter never asks it.

**Why it matters to the learner:** Chapter 1 sets up the memory wall and arithmetic intensity. Chapter 3 is where the course should show, with numbers, that the WSE's answer is bandwidth matched to the core. Without that, "single-cycle SRAM" is an assertion, not an explanation.

**Concrete fix:** Expand into a short worked example, marked Derived:
> "23 GB/s at ~1 GHz is about 24 bytes per cycle per PE: three 64-bit accesses <span class="tag derived">Derived</span>. That is what a vector FMA needs every cycle at 4-wide FP16 (two 64-bit operand reads, one 64-bit result write). So on the WSE-2-class datapath, memory can feed the math at full rate with arithmetic intensity well under 1 FLOP/byte. Compare the ~295 FLOP/byte an H100 needs from HBM (Chapter 1). WSE-3 doubled SIMD width while per-PE bandwidth grew only ~5%. Full 8-wide rate therefore probably depends on operands from registers, the cache or the fabric. That is an inference; the clock is also unpublished."

If the fixer prefers not to make the WSE-3 inference, keep only the WSE-2 balance and the Chapter 1 comparison.

### P7 [major] f32 throughput is never addressed, though every lab uses f32
**Location:** "Compute: SIMD lanes driven by descriptors"; anatomy figure (8 lanes drawn, unlabelled).

**Problem:** The chapter gives FP16/BF16 and INT8 widths only. The budget widget, the quiz and all labs use f32. The figure draws 8 lanes without saying which precision they are for. The research notes record the f32 width as an explicit gap.

**Why it matters to the learner:** The learner will try to estimate Lab 3's compute rate and has nothing to start from. An honest "unknown" is much better than silence, which invites them to assume 8-wide f32.

**Concrete fix:** Add after the SIMD sentence: "The f32 SIMD width is not published. The labs in this course use f32, so treat FP16 peak numbers as an upper bound for them, and measure (Lab 3 does)." Label the lanes in the figure "8 × FP16 lanes (WSE-3)".

### P8 [major] Check-yourself questions are recall-only, one is imprecise, and two objectives are untested
**Location:** Quiz.

**Problem:**
- Q1 is good.
- Q2 repeats the text almost word for word.
- Q3's answer says "each async DSD operation occupies one". "Async" is never introduced in ch03, and the question's framing ("what limits concurrency") reinforces the 8× misreading from P1.
- Nothing tests sparsity (objective 3b), bank interleaving, or the bandwidth argument.

**Why it matters to the learner:** The quiz is where a learner finds out whether the model built. Recall questions do not expose the misconceptions this chapter is most likely to create.

**Concrete fix:**
- Rewrite Q3 as: "Eight microthreads: does that make a PE eight times faster?" Answer: "No. They share one SIMD datapath. They let up to eight vector operations (usually ones started with `.async = true`, Ch. 6) be in flight together, so sending, receiving and computing overlap. Two in-flight operations may not use the same microthread."
- Replace Q2 with an applied question: "In the matvec benchmark the WSE moves ~3× more bytes than a cached machine. Why is that acceptable?" Answer: "The extra traffic is the y accumulator re-read and re-written every column. It hits single-cycle SRAM private to that PE, and there are ~900k such SRAMs in parallel, so there is no shared slow memory to protect."
- Add: "A layer's activations are 90% zeros and stored as f32. Can you use the topic-04 index trick directly?" Answer: "Not as is. Index + value leaves only 16 bits for the value, so you would send f16/bf16 (losing precision) or spend two wavelets per value. You also pay one task activation per non-zero on the receiver."

### P9 [minor] The interleaving claim is only true for unit stride, and Chapter 6 immediately uses stride 8
**Location:** "Interleaving lets a vector instruction read and write several consecutive words per cycle without bank conflicts."

**Problem:** With 8 banks interleaved by 32-bit word, word k lives in bank k mod 8. A stride-8 walk (the 6×8 matrix-column preset in Chapter 6) therefore lands in one bank every time. Whether the hardware actually stalls is not public, but the chapter's statement implies conflict-freedom in general.

**Why it matters to the learner:** It is a natural question for a systems-minded reader, and Chapter 6 invites it immediately.

**Concrete fix:** Append: "That holds for consecutive words. Word k lives in bank k mod 8, so a stride-8 walk hits the same bank every time <span class="tag derived">Derived</span>. Cerebras does not publish whether such strides cost extra cycles."

### P10 [minor] "The compiler decides" what goes in the software-managed cache is unsupported
**Location:** Paragraph on the software-managed cache.

**Problem:** The sources say only "software-managed cache for high-frequency data such as accumulators" (HC34). No SDK tutorial or CSL feature mentioning the cache was found, so attributing the decision to "the compiler" is a guess presented as fact.

**Why it matters to the learner:** The learner may look for a CSL keyword to control it, or assume the compiler optimises for them.

**Concrete fix:** Replace "'software-managed' meaning the compiler decides what goes there; nothing is cached automatically" with "'software-managed' meaning nothing is cached automatically by hardware. CSL as used in this course exposes no control over it; the toolchain manages it <span class="tag vendor">Vendor, HC34</span>."

### P11 [minor] The "~2 KB for code" figure and the widget's assumptions are presented too firmly
**Location:** Memory paragraph ("implying ~2 KB for code and runtime"); budget widget.

**Problem:**
- "Benchmarks keep data under 46 KB" shows that those programs leave at least 2 KB. It does not show that code and runtime take 2 KB in general.
- The widget hard-codes 2,048 B and reports "FITS" with 0.1 KB spare.
- The hint never says what x, y and b are; the widget sizes them as 2M + N.

**Why it matters to the learner:** Learners will design layouts against this number and be surprised when a larger program does not fit.

**Concrete fix:**
- Text: "...keep data under about 46 KB, so plan on reserving at least ~2 KB for code, stack and runtime. More code needs more."
- Widget hint: "Suppose each PE computes y = A·x + b on its own M × N block of A (x has N entries; y and b have M)."
- Draw a dashed amber line at 46 KB labelled "SDK benchmarks stay below this". Report "FITS, but tight" when usage is between 46 and 48 KB.

### P12 [minor] Undefined acronyms and symbols, and unexplained forward references
**Location:** Figure ("16 GPRs", "48 DSRs", "activated ∧ unblocked"); "a rule that caused a real hang in Lab 3".

**Problem:**
- GPR is never expanded.
- DSR is expanded only in Chapter 6.
- "∧" is logic notation dropped into a hardware diagram.
- "Lab 3" means nothing yet; the labs are Chapters 10–12.

**Concrete fix:**
- In the text, write "16 general-purpose registers (GPRs) for scalars and addresses, and 48 data-structure registers (DSRs) that each hold one DSD."
- In the figure, use "activated AND not blocked".
- Change "a rule that caused a real hang in Lab 3" to "a rule that hung this course's own heat-stencil program (Chapter 5 tells the story; Chapter 12 measures the fix)."

### P13 [minor] Terminology and provenance inconsistencies with neighbouring chapters
**Location:** Figure title "One PE (one 'tile')"; "up from 4-wide FP16 on earlier generations <span class=tag vendor>"; figure "Size: ~0.05 mm², ≈ ½ logic, ½ SRAM".

**Problem:**
- Chapter 2 says "core", ch03 adds "tile", and Chapters 4–6 say "PE". The chapter never states these are the same thing.
- Chapter 2 marks the 4-wide WSE-1/2 figure as coming from a secondary source, but ch03 tags it Vendor.
- The caption says all figures are from HC2024. In fact 0.05 mm² comes from a Cerebras blog and an arXiv comparison (one other source says ~0.038 mm²), and "½ logic, ½ SRAM" has no source in the notes.

**Concrete fix:**
- Add to the lede: "(Cerebras also calls it a core or a tile; this course says PE.)"
- Retag the 4-wide figure `<span class="tag indep">secondary source</span>` to match Chapter 2.
- In the figure, tag 0.05 mm² as Vendor (blog) and either source "½ logic, ½ SRAM" or delete it.

### P14 [minor] The anatomy figure contradicts "five-port" and shows one-way ports
**Location:** Router in the anatomy SVG.

**Problem:** The lede says five ports, but the figure omits WEST "for clarity" when there is room to draw it. All arrows point outward, including the RAMP, which points only into the CE. Chapter 4 says the ports are bidirectional.

**Concrete fix:** Draw the WEST port (shift the RAMP arrow to come off the router's lower-left corner, or route it below). Use double-headed arrows (marker-start and marker-end) for all five ports. Drop the "(WEST port omitted for clarity)" note.

### P15 [minor] No anchor for "~1 GHz"
**Location:** Memory paragraph, "at ~1 GHz".

**Problem:** Chapter 2 says no clock is published, yet ch03 uses ~1 GHz without comment. The SDK gives a concrete anchor the learner could use: the matvec benchmark converts cycles to seconds at 850 MHz for CS-2 (`secs = max_cycles / 850000000.0`).

**Concrete fix:** Change "at ~1 GHz" to "at a ~0.85–1 GHz clock (no official figure; the SDK's matvec benchmark assumes 850 MHz for CS-2 <span class="tag sdk">SDK 2.10.1</span>)".
