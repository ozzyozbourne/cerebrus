# ch03 · accuracy review

Summary: The chapter's core facts are right: 48 KB per PE, 8 × 6 KB banks, a 256 B / 512 B software cache, 16 GPRs and 48 DSRs, SIMD widths, 8 microthreads, 24 colors and the topic-04 index-in-upper-16-bits trick. They match the research report and notes, and in places the SDK. The defects are a few clear errors and a cluster of provenance problems:
- an arithmetic error in the quiz (48 − 32 = 16 KB, not ~14 KB);
- the "relative/absolute bandwidth" figure misdescribes what the single-tile-matvec benchmark counts;
- the sparse-wavelet diagram labels the data half "f16" where the SDK uses i16;
- the anatomy caption blanket-tags every figure as "Vendor, Hot Chips 2024", although several come from academic papers, HC34 (WSE-2), the SDK or conflicting secondary sources;
- the "~2 KB for code and runtime" budget is an inference that measured ELFs contradict (~2.5–3.4 KB of .text).

## Findings

### A1 [major] Quiz arithmetic: 48 KB − 32 KB is 16 KB, not ~14 KB
Location: "Check yourself", first `<details>` answer.
Problem: The text says two 64×64 f32 matrices (32 KB) leave "~14 KB for code, runtime buffers and everything else". 48 − 32 = 16 KB. The ~14 KB figure only works if ~2 KB of code is subtracted first, but the sentence counts code inside the remainder, so the remainder must be 16 KB.
Evidence: 2 × 64 × 64 × 4 = 32,768 B = 32 KB. 48 × 1024 − 32,768 = 16,384 B = 16 KB.
Concrete fix: replace
`It fits in 48 KB, but leaves ~14 KB for code, runtime buffers and everything else.`
with
`It fits in 48 KB, but leaves only 16 KB for code (about 3 KB in the SDK examples), runtime buffers, stack and every other array.`

### A2 [major] The relative-vs-absolute bandwidth figure misdescribes the benchmark
Location: second figure ("GEMV y = A·x on one PE") and its figcaption.
Problem: The figure says a cached machine "reads x once into cache, reuses it … counts 'relative' bandwidth that never touches DRAM". The caption calls "relative" "what a cache would have to supply". The benchmark defines it differently. "Relative" is the minimum number of memory accesses on a traditional cached architecture: A and x read once, y written once. "Absolute" is the actual SRAM traffic on the WSE, where y is read and written on every column. The difference is about y, not x (x is read once on both), and relative is the smaller count of memory traffic, not cache-supplied traffic. Also, the benchmark targets CS-2 (WSE-2) and converts cycles to time at 850 MHz.
Evidence:
- `examples/benchmarks/single-tile-matvec/README.rst` L54–59: "Relative refers to the bandwidth obtained if we calculate based on the number of memory accesses that would occur … on a more traditional architecture, where caching allows us to write the y vector for example, only once to memory. 'Absolute' refers to the actual number of memory accesses required to run this program on the WSE."
- `single-tile-matvec/run.py` L202–215: "STANDARD read/writes: Read full x, read each column of V stack, write full y … 4*nb*nb + 8*nb" and "ACTUAL read/writes: Read full x; read each col of V stack; read, write full y nb times … 12*nb*nb + 4*nb".
- `run.py` L223–224, L266: `secs = max_cycles / 850000000.0`.
- README L8: "on an actual CS-2".
Concrete fix: replace the left box's three muted lines with
`keeps the y accumulators in registers/cache:` / `reads A and x once, writes y once` / `→ "relative" = 4(N² + 2N) bytes`.
Replace the right box's three lines with
`reads and writes y in SRAM for every column:` / `"absolute" = 4(3N² + N) bytes, ~3× more,` / `and single-cycle SRAM absorbs it`.
Replace the figcaption with:
`<b>The SDK's single-tile matvec benchmark reports both numbers</b> <span class="tag sdk">SDK 2.10.1</span>: "relative" bandwidth counts the memory traffic a cached machine would need (y written once), and "absolute" counts the SRAM accesses the WSE really makes (y read and written once per column). The gap is reuse that no cache absorbs here. The benchmark is written for CS-2 and assumes an 850 MHz clock.`

### A3 [major] The anatomy caption blanket-tags mixed-source figures as "Vendor, Hot Chips 2024"
Location: anatomy figure figcaption: "Figures are WSE-3 <span class="tag vendor">Vendor, Hot Chips 2024</span> unless noted."
Problem: Nothing in the SVG is "noted", so every number inherits the HC2024 vendor tag. Many do not come from HC2024:
- 8 banks × 6 KB and 32-bit interleaving: academic papers. HC34, a WSE-2 talk, gives only "8 single-port banks".
- "single-cycle": HC34 (WSE-2).
- 24 colors: the SDK.
- 8 microthreads: the WSE-2 Cerebras blog plus the SDK.
- "activated ∧ unblocked": the SDK.
- "≈ ½ logic, ½ SRAM": HC34 (WSE-2).
- "~0.05 mm²": the yield blog and secondary sources, with conflicting values (see A4).
Only 48 KB, 512 B, 16 GPRs, 48 DSRs and the SIMD widths are HC2024.
Evidence:
- `research_notes/.../wse_hardware.md` L79: HC34 "8 single-port banks" … "single-cycle access".
- L81: "8 banks × 6 KB … successive 32-bit words in successive banks — [arXiv:2605.07954] … (via search extract)".
- L83: HC2024 "16 general-purpose registers, 48 data structure registers … 8-way … 16-way".
- L86: microthreads from the "Cerebras architecture deep dive" (WSE-2).
- L59: "HC34 slides give a 50:50 logic-to-SRAM area ratio".
- SIF `csl-libs/target/common.csl` L18: `const NUM_COLORS = 24;`.
Concrete fix: replace the figcaption with:
`<b>A 48 KB computer with a router attached.</b> 48 KB, the 512 B cache, 16 GPRs, 48 DSRs and the SIMD widths are WSE-3 figures <span class="tag vendor">Vendor, Hot Chips 2024</span>. The 8 single-ported banks, single-cycle access and the ½ : ½ logic/SRAM split come from the WSE-2 talk <span class="tag vendor">Vendor, Hot Chips 2022</span>. The 6 KB bank size and 32-bit interleaving come from academic papers <span class="tag indep">Independent</span>. The 24 colors, 8 microthreads and the task picker rule come from the SDK <span class="tag sdk">SDK 2.10.1</span>. The RAMP is the router's fifth port, connecting it to its own CE, and all five links are bidirectional. WSE-2 register counts were not found.`

### A4 [major] "~0.05 mm² per PE" is stated as fact, but the sources conflict
Location: anatomy SVG, "Size" note: `~0.05 mm² per PE`.
Problem: The notes and report say no definitive figure exists. One source gives ~38,000 µm² (0.038 mm²), another ~0.05 mm². Dividing the wafer by 900k cores gives ≈0.051 mm², but that includes spares, I/O and edge area, so it is an upper bound. Under the caption's blanket vendor tag (A3), the figure reads as an HC2024 number, which it is not.
Evidence: `wse_hardware.md` L29: "one source cites about 38,000 µm² from a WSE-3 whitepaper, another says about 0.05 mm². No definitive figure found". The report L46 says the same. 46,225 mm² / 900,000 = 0.0514 mm².
Concrete fix: change the SVG text `~0.05 mm² per PE` to `~0.04–0.05 mm² per PE`, and add a third line under the "Size" group, e.g. `<text x="580" y="380" font-size="11" class="muted">(sources differ)</text>`. The A3 caption fix already tags the ½ : ½ split as Hot Chips 2022.

### A5 [major] The ~2 KB code-and-runtime budget is an inference that measured ELFs contradict
Location: "Memory: 48 KB…" paragraph ("implying ~2 KB for code and runtime in those configurations"), and the budget widget (`code = 2048`, label "code + runtime (~2 KB)", readout "code≈2 KB").
Problem: The SDK never says code takes 2 KB. One benchmark asserts data stays under 46 KB, and another sizes a buffer FIFO at 46 KB. Compiled user-PE ELFs from the SDK tutorials and this course's labs, built in the reviewers' scratch directories, have 2.5–3.4 KB of `.text`, plus 0.3–0.8 KB of `.data`/`.bss`. So "~2 KB" understates the real overhead, and the widget's verdicts are slightly optimistic.
Evidence:
- `benchmarks/spmv-hypersparse/run.py` L564: `assert (mem_use_per_pe < 46 * 1024), "exceed maximum memory capacity, increase the core rectangle"`.
- `benchmarks/bandwidth-test/run.py` L26: "Each PE in the buffer has 46KB fifo".
- `readelf -S` on user-PE ELFs:
  - `tmp/claude-work/gemv-01-complete-program/out/bin/out_0_0.elf`: `.text` 0xb00 (2,816 B), `.bss` 0x110.
  - `tmp/claude-work/gemv-08-routes-3/out/bin/out_0_0.elf`: `.text` 0xcc8 (3,272 B).
  - `tmp/rev-ch12-acc/b/out/bin/out_0_0.elf`: `.text` 0xd38 (3,384 B).
  - `tmp/rev-ch12-acc/f/...`: `.text` 0x9b0 (2,480 B).
Concrete fix: replace
`The SDK's own benchmarks keep data under about 46 KB, implying ~2 KB for code and runtime in those configurations <span class="tag sdk">SDK 2.10.1</span>.`
with
`The SDK's own benchmarks keep data under about 46 KB <span class="tag sdk">SDK 2.10.1</span>, and compiled tutorial and lab programs carry about 2.5–3.4 KB of code each <span class="tag measured">Measured, cslc 2.10.1 ELFs</span>, so budget roughly 3 KB for code and runtime.`
In the script, set `code = 3072`, change the label to `"code + runtime (~3 KB)"`, and change the readout text `code≈2 KB` to `code≈3 KB`.

### A6 [major] "Up from 4-wide FP16" is tagged Vendor, but the source is secondary
Location: "Compute: SIMD lanes…" paragraph, first sentence, `<span class="tag vendor">Vendor</span>`.
Problem: The 8-way and 16-way WSE-3 figures are vendor (HC2024). The WSE-1/2 4-wide figure comes only from a secondary blog, and the notes say it was not confirmed in HC34. Chapter 02 already marks it as secondary, so ch03 contradicts ch02.
Evidence: `wse_hardware.md` L84: "A secondary analysis says WSE-1 and WSE-2 used a 4-wide FP16 SIMD … (secondary; I did not confirm a 4-wide figure in the HC34 extract)". Report L34: "4-wide (secondary)". `02-the-wafer.html`: "*4-wide FP16 on WSE-1/2 comes from a secondary source."
Concrete fix: replace
`The WSE-3 datapath is <strong>8-way SIMD for FP16/BF16 and 16-way for INT8</strong>, up from 4-wide FP16 on earlier generations <span class="tag vendor">Vendor</span>.`
with
`The WSE-3 datapath is <strong>8-way SIMD for FP16/BF16 and 16-way for INT8</strong> <span class="tag vendor">Vendor, HC2024</span>, reportedly up from 4-wide FP16 on WSE-1/2 <span class="tag indep">Secondary source</span>.`

### A7 [major] The sparse-wavelet diagram says "f16 value", but the SDK example uses i16
Location: third figure (32-bit wavelet), right-hand label `lower 16 bits: f16 value`.
Problem: topic-04 receives `wavelet_data: i16`, and its README just says "data". The figcaption itself quotes the i16 signature, so the figure contradicts its own caption.
Evidence: `tutorials/topic-04-sparse-tensors/pe_program.csl` L28: `task main_task(wavelet_data: i16, index: i16) void {`. README: "use the lower 16 bits to contain data as usual … the upper 16 bits to contain the index of the value."
Concrete fix: change the SVG text `lower 16 bits: f16 value` to `lower 16 bits: 16-bit value`. Optionally append to the figcaption: `(topic-04 uses i16 data; any 16-bit type fits)`.

### A8 [major] "This mechanism" ties the sparse-FLOPS headline to the SDK index trick
Location: "Sparsity comes free with dataflow" paragraph, last sentence: "This mechanism is what Cerebras's sparse-FLOPS headline numbers assume."
Problem: In context, "this mechanism" points at the topic-04 index-in-upper-16-bits encoding. The report ties the sparse-FLOPS numbers to hardware zero-filtering at the sender and dataflow triggering, not to a CSL encoding trick. "Senders filter zeros" also carries no tag; it is vendor (HC34, MICRO-54).
Evidence: Report L58: "zeros are filtered at the sender, so no compute is spent on them ([HC34]; [Lie MICRO-54 keynote]). This mechanism underlies the sparse-FLOPS headline numbers. The SDK shows the software side: …". `wse_hardware.md` L85.
Concrete fix: rewrite the paragraph as:
`Because computation is triggered by arriving data, a zero that is never sent never triggers work. Senders filter zeros and receivers only compute on what arrives <span class="tag vendor">Vendor, HC34 / MICRO-54</span>. This dataflow zero-skipping is what Cerebras's sparse-FLOPS headline numbers rely on. The SDK shows the software side: a wavelet is 32 bits, so a sparse value can travel as 16 bits of data plus a 16-bit index in the upper half <span class="tag sdk">SDK 2.10.1, topic-04</span>.`

### A9 [minor] "Software-managed" is glossed as "the compiler decides", which is unsourced
Location: paragraph on the software-managed cache: `"software-managed" meaning the compiler decides what goes there`.
Problem: No source says who manages it. HC34 says only "256B software-managed cache for high-frequency data such as accumulators". The CSL standard library and the tutorials never mention a cache.
Evidence: `wse_hardware.md` L79. `grep -rni cache` over the SIF `csl-libs` returns nothing.
Concrete fix: replace `— "software-managed" meaning the compiler decides what goes there; nothing is cached automatically.` with `<span class="tag vendor">Vendor</span>. "Software-managed" means nothing is cached automatically; the public sources do not say how CSL exposes it, and the CSL standard library never mentions it.`

### A10 [minor] Memory-organisation sentence: no provenance, and an inference stated as fact
Location: first sentence of "Memory: 48 KB…" and the next sentence: "Interleaving lets a vector instruction read and write several consecutive words per cycle without bank conflicts."
Problem: There is no tag. The bank size and interleaving come from academic papers, and single-ported banks with single-cycle access come from HC34. The claim that interleaving avoids conflicts is the author's inference and holds only for unit-stride access.
Evidence: `wse_hardware.md` L79, L81.
Concrete fix: replace the first two sentences with:
`The SRAM is 8 single-ported banks with single-cycle access <span class="tag vendor">Vendor, HC34</span>, each 6 KB and interleaved by 32-bit word <span class="tag indep">Academic papers</span>. Interleaving means consecutive words sit in different banks, so a unit-stride vector access can touch several words per cycle without bank conflicts <span class="tag derived">Derived</span>.`

### A11 [minor] The per-PE bandwidth check assumes ~1 GHz, and "a few" understates the result
Location: "A quick sanity check: 21 PB/s ÷ 900,000 PEs ≈ 23 GB/s per PE, a few 32-bit accesses per cycle at ~1 GHz".
Problem: The arithmetic is right: 23.3 GB/s works out to ≈5.8 words per cycle at 1 GHz. But no clock is published, and the SDK itself assumes 850 MHz, which gives ≈6.9 words per cycle. "A few" undersells a figure close to the 8-bank limit, which is the point of the check.
Evidence: `wse_hardware.md` L40 ("roughly … 6 × 32-bit accesses per cycle"), L45 ("No official clock … The only number is the SDK's 850 MHz assumption").
Concrete fix: replace `a few 32-bit accesses per cycle at ~1 GHz` with `about 6–7 32-bit accesses per cycle at the SDK's assumed 850 MHz to 1 GHz (no clock is published), close to what 8 single-cycle banks can deliver`.

### A12 [minor] "8 microthreads" carries no Vendor tag, and the hang attribution needs precision
Location: Compute paragraph: "It can run up to eight such operations at once, one per microthread. On WSE-3 microthread IDs are exposed … — a rule that caused a real hang in Lab 3."
Problem: The 8-operation figure is vendor (Cerebras blog, WSE-2), but only the SDK tag follows. The Lab 3 reference is accurate: ch05 and ch12 describe both async ops defaulting to microthread 2 from queue IDs. It would read better if the default behaviour were stated.
Evidence: `wse_hardware.md` L86: "The core also supports eight simultaneous tensor operations, which we call micro-threads". topic-15 README L37–41: "(if they are not explicitly specified, they default to the respective queue IDs) … two operations cannot concurrently use the same microthread". `12-lab-stencil.html`: "both claimed microthread 2".
Concrete fix: after `one per microthread</strong>` insert ` <span class="tag vendor">Vendor</span>`. Replace `two operations must never share one at the same time` with `if you do not pick one, an async fabric op uses the microthread matching its queue ID, and two operations must never share one at the same time`.

### A13 [minor] "Arriving data activates tasks" omits local and control tasks
Location: "Control: tasks…" paragraph.
Problem: Data tasks fire on wavelet arrival, but local tasks are activated by software (including by async-op completion), and control tasks fire on control wavelets.
Evidence: `wse_hardware.md` L125: "A local task runs when software activates it. A control task runs when a control wavelet carrying its ID arrives."
Concrete fix: replace `Arriving data activates tasks.` with `Arriving data activates data tasks; other tasks are activated by code or by a finishing vector operation <span class="tag sdk">SDK 2.10.1</span>.`

### A14 [minor] "✕ OS / threads" contradicts the 8 microthreads in the same figure, and the I-cache claim is stronger than the evidence
Location: anatomy SVG "Not here" list.
Problem:
- "threads" sits next to an "8 microthreads" box. The intended meaning is "no software threads".
- "✕ instruction cache" rests on not having found one. The notes say "no separate I-cache was found".
- The lede's "900,000 copies" is a vendor WSE-3 marketing count with no tag. The SDK-visible grid is smaller (750×994 on CS-2).
Evidence: `wse_hardware.md` L96, L68.
Concrete fix:
- Change `✕ OS / threads` to `✕ OS / software threads`.
- Change `✕ instruction cache` to `✕ instruction cache (none documented)`.
- In the lede, change `The wafer is 900,000 copies of one small computer.` to `The WSE-3 wafer is about 900,000 copies of one small computer <span class="tag vendor">Vendor</span>.`

### A15 [minor] The router label "24 colors" needs an SDK tag
Location: anatomy SVG router `24 colors`.
Problem: The number is correct for both architectures in the SDK, but under the current caption it reads as an HC2024 vendor figure. The A3 caption rewrite fixes this. No SVG change is needed if A3 is applied.
Evidence: SIF `csl-libs/target/common.csl` L18 `const NUM_COLORS = 24;`, shared by wse2.csl and wse3.csl (`const NUM_COLORS = common.NUM_COLORS;`).
Concrete fix: covered by A3.

## Not verifiable
- The HC2024 figures (16 GPRs, 48 DSRs, 8-way FP16/BF16, 16-way INT8, 512 B cache) are known only through search extracts of the slides. The slide PDF was not re-fetched.
- Whether the 512 B WSE-3 "local cache" is still software-managed (HC34 says so for the 256 B WSE-2 cache; the HC2024 extract says only "local cache").
- The 6 KB bank size and 32-bit interleaving (academic papers, via search extract), and whether they apply unchanged to WSE-3.
- WSE-1/2 4-wide FP16 SIMD (secondary only).
- Per-PE area (0.038 vs 0.05 mm²) and whether the 50:50 logic/SRAM split still holds on WSE-3.
- The absence of an instruction cache (no positive source either way).
- The architecture targeted by the measured ELFs in A5 (scratch builds by other reviewers; the default `--arch` is wse2). The 2.5–3.4 KB range covers all builds inspected.
