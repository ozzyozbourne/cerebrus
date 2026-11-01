# ch10 · accuracy review

Summary: The chapter is accurate on its main points. Both programs compile and pass on WSE-3 and WSE-2 under SDK 2.10.1, and the generated page matches a fresh build of the src template byte for byte. The FMA explanation, the "sum after 95 values" bug story and the N:4096 / N:6000 exercise premise all reproduce exactly. The problems are: one quantitative overclaim (how long `@fmacs` takes), no provenance tags anywhere in the chapter, a cross-reference to Lab 3 that describes a method Lab 3 does not use, an exercise question that the data cannot answer cleanly, and a few small imprecisions in code comments and captions. There are no critical errors.

Verification done in a scratch copy (`/home/user/cerebras-sdk/tmp/rev-ch10-acc/`, now deleted). Nothing was run inside `course/programs/`.
- 01-saxpy: WSE-3 gives 7,738–7,740 cycles and SUCCESS. WSE-2 gives 6,826 cycles and SUCCESS. N:4096 gives SUCCESS (266,295 cycles). N:5000 gives SUCCESS. N:6000 fails at link time with `ld.lld: error: ran out of PE memory for data (section .bss)`. Without `unblock_cmd_stream()`, the host aborts with `the received length (0 bytes) is not expected (256 bytes), could be a kernel stall`.
- The device output matches a single-rounding FMA (`float32(float64(x)*2.5 + float64(y))`) on all 64 elements. Plain numpy `a*x+y` matches on only 47 of them.
- 02-wavelet-tasks: N=100 and N=500 give SUCCESS on both WSE-3 and WSE-2. Without `launch('wait_done')`, the sum is 30.818176, which is exactly `cumsum[94]` (95 values).
- Generated `course/10-lab-first-programs.html` is identical to the output of `tools/build.py` logic run against the current src and programs.

## Findings

### A1 [major] `@fmacs` cost "tens of cycles" is an underestimate by roughly 3–10x
Location: section "What happens inside, in order", the paragraph after the sequence figure: "The `@fmacs` itself processes 64 elements in on the order of tens of cycles."
Problem: In the simulator, one 64-element `@fmacs` costs about 130–140 cycles, roughly 2 cycles per element. The sentence also carries no provenance tag. The main point of the paragraph still holds: host I/O dominates.
Evidence: A copy of 01-saxpy with the `@fmacs` inside `while (k < K)` measured 7,740 cycles at K=1 and 21,724 cycles at K=101. That is (21,724 − 7,740)/100 ≈ 140 cycles per iteration. The same loop with 1-element DSDs measured 8,912 cycles at K=101, so loop overhead plus one element is ≈ 11.7 cycles per iteration. That leaves ≈ 128 cycles for the extra 63 elements. A single 64-element call and a single 1-element call both give 7,740 total cycles, which confirms that the kernel is invisible next to the I/O.
Concrete fix: replace the sentence with:
`The <code>@fmacs</code> itself is about 140 cycles for 64 elements (roughly 2 cycles per element; measured by running it 101 times in a loop and subtracting) <span class="tag measured">Measured</span>, under 2% of the total: swapping it for a 1-element <code>@fmacs</code> leaves the total unchanged.`

### A2 [major] The chapter has no provenance tags
Location: the whole chapter. The src template contains no `<span class="tag …">`.
Problem: The brief requires every number to carry a tag. Untagged numbers include: 7,740 simulated cycles; 48 KB SRAM; "two 16 KB arrays"; 1e-6 tolerance; 30.818 vs 26.138; "after 95 values"; validated at N = 100 and N = 500; "color 22"; queue 2.
Evidence: `grep -c 'class="tag' course/10-lab-first-programs.html` returns 0. The other labs use tags, for example `src/12-lab-stencil.html:67` uses `<span class="tag measured">Measured</span>`.
Concrete fix (src template):
- Line 45: `Where do the 7,740 simulated cycles <span class="tag measured">Measured</span> go?`
- Line 49: `…does it still fit in 48 KB <span class="tag sdk">SDK 2.10.1</span>?`
- Line 43 (figcaption): `Every host call becomes a command on color 22 <span class="tag sdk">SDK 2.10.1</span>.` The source is the `RXCOMMAND(=C22)` comments in `csl-libs/memcpy/wse3/memcpy.csl`.
- Line 78: `…but the sum was 30.818 instead of 26.138 <span class="tag measured">Measured</span>.`
- Line 84: `Validated afterwards at N = 100 and N = 500, on WSE-3 and WSE-2 <span class="tag measured">Measured</span>.`

### A3 [minor] The Lab 3 cross-reference describes the wrong method
Location: same paragraph as A1: "Lab 3 shows how to separate the two by measuring at two problem sizes and subtracting."
Problem: Lab 3 separates kernel time from host I/O by running 0 and 100 timesteps at the same size and subtracting. Problem size is varied separately, to fit a per-cell model.
Evidence: `src/12-lab-stencil.html:67`: "run the same program with 0 and 100 timesteps and subtract; the host transfers are identical".
Concrete fix: `Lab 3 shows how to separate the two: run the same program with 0 and 100 iterations of the kernel and subtract, so the host transfers cancel.`

### A4 [minor] Exercise "Does the error grow or shrink?" cannot be answered from the error
Location: Program 02, Exercises, item 2.
Problem: Without the barrier, the number of values missing from the sum is constant: exactly 5 at every N tested. Relative error in the sum is not a clean signal, because the sum of uniform(−10, 10) values is close to zero and noisy. Measured relative sum errors were 17.9% at N=100, 21.7% at N=500 and 3.8% at N=2000. The answer is non-monotonic, so a learner who compares relative errors gets a misleading result.
Evidence: Scratch copy with the `launch('wait_done')` line deleted. Matching the device sum against `np.cumsum` gives 95/100, 495/500 and 1995/2000 values included. The sum of squares includes 96, 496 and 1996, which shows that the readback overlaps the still-running tasks. Results were identical on repeated runs.
Concrete fix: `Delete the <code>launch('wait_done')</code> line in <code>run.py</code> and try N = 100, 500 and 2000. Use <code>numpy.cumsum</code> to find how many values made it into <code>stats[0]</code>. Does the number of missing values change with N? Why might <code>stats[1]</code> include one more value than <code>stats[0]</code>?` Our measurement: 5 missing at every N; <code>stats[1]</code> includes one more.

### A5 [minor] The `@export_name(…, false)` comment misstates the SDK meaning
Location: Program 02 `layout.csl`, shown via `{{code:programs/02-wavelet-tasks/layout.csl}}`, line 13: `// false = pointer is immutable (const)`.
Problem: The third argument is host-side mutability: whether the host may write the symbol. It does not mean the pointer is `const`. Program 01's comment ("host may write and read") gets this right, so the two programs contradict each other.
Evidence: SDK `tutorials/gemv-01-complete-program/layout.csl:16`: "Last argument is mutability: host can read y, but not write to it". The research report (line 156) says the same: "host may read, not write".
Concrete fix: The text comes from the program source, not the template. In `course/programs/02-wavelet-tasks/layout.csl` line 13, change the comment to `// false = host may read, not write`, then rerun `tools/build.py`. This is a comment-only change and does not affect the validated code.

### A6 [minor] Cycle counts are presented as exact but vary between runs
Location: line 45 "the 7,740 simulated cycles", and the `[7020 simulated cycles, WSE-3]` line in the 02 output.
Problem: Simulated cycle counts vary from run to run, especially for program 02. Learners using `run_all.sh` will see different numbers and may think something is wrong.
Evidence: 01-saxpy on WSE-3 over 3 runs: 7,740, 7,738, 7,740. 02-wavelet-tasks on WSE-3 at N=100 over 4 runs: 7,023, 7,163, 7,543, 7,022.
Concrete fix: At line 45: `Where do the ~7,740 simulated cycles <span class="tag measured">Measured</span> go? (Counts vary by a few cycles between runs, and by a few hundred for program 02.)`

### A7 [minor] The tolerance description is incomplete
Location: line 35: "The test tolerates 1e-6 relative error."
Problem: The test uses `rtol=1e-6, atol=1e-6`, which is a combined absolute plus relative tolerance. For elements near 0, the absolute term dominates.
Evidence: `programs/01-saxpy/run.py:26`.
Concrete fix: `The test tolerates this: <code>assert_allclose</code> with <code>rtol=1e-6, atol=1e-6</code>. (17 of the 64 elements differ in the last bit; all 64 match a single-rounding FMA exactly.)`

### A8 [minor] The streaming figure omits the WSE-3 memcpy forwarding hop
Location: Figure "Streaming path for program 02": host → "memcpy west / color MEMCPYH2D_1" → "input queue 2".
Problem: On WSE-3, H2D data does not arrive directly on MEMCPYH2D_1. It arrives on C23 into IQ0. memcpy's kernel microthread (UT0), running on this same PE, then forwards it to OQ0, which is recoloured to MEMCPYH2D_1 and lands in the user's input queue. That hop explains why the user must avoid queues 0 and 1. It also explains why H2D "completion", which is triggered by the teardown arriving, can come before the user tasks drain. "memcpy west" makes it look as if memcpy is only an external block.
Evidence: `csl-libs/memcpy/wse3/memcpy.csl`, comment block "H2D data flow: reuse OQ0 from D2H … router --IQ0 (UT0)--> CE --OQ0 (H2D_1)--> WTT_1 --> user_input_queue_1 … C23". The same file also says: "we can only unblock the cmd stream (C22) when TD arrives because TD indicates all data of this H2D has been sent".
Concrete fix: Append to the figcaption: ` On WSE-3 the data actually reaches the PE on memcpy's own color into input queue 0; memcpy's kernel microthread on the same PE re-emits each wavelet on <code>MEMCPYH2D_1</code>, which is why queues 0 and 1 are off-limits <span class="tag sdk">SDK 2.10.1</span>.`

### A9 [minor] Exercise 3 (f16 pairs) gives the wrong hint
Location: Program 02, Exercises, item 3: "…and send `MEMCPY_16BIT` data."
Problem: The phrasing suggests that `MEMCPY_16BIT` is what makes two halves arrive per wavelet. In streaming mode, the host must pack the pairs into 32-bit words itself. The data-type flag made no difference.
Evidence: Scratch copy with `task on_value(lo: f16, hi: f16)`, streaming `h.view(np.uint32)`. It passed identically with `MEMCPY_16BIT` and with `MEMCPY_32BIT`. SDK `tutorials/topic-04-sparse-tensors/run.py` packs `(idx << 16) + val` into an int32 array on the host before streaming.
Concrete fix: `Stream f16 pairs instead: give the data task two 16-bit arguments (<code>lo: f16, hi: f16</code>) and pack pairs on the host with <code>h.astype(np.float16).view(np.uint32)</code>, as in SDK topic-04. Does the <code>data_type</code> flag matter?`

### A10 [minor] Exercise 3 (remove `unblock_cmd_stream`): the observed behaviour is a crash, not a hang
Location: Program 01, Exercises, item 3. This is not wrong as written. The finding is that the chapter gives no expected observation, and the course elsewhere (research notes, ch09) says "hangs".
Problem: On the simulator, the host does not hang. The simulator stops on idleness, and `cs_python` aborts.
Evidence: Scratch run printed `terminate called after throwing an instance of 'std::runtime_error' what(): the received length (0 bytes) is not expected (256 bytes), could be a kernel stall`, with exit code 134.
Concrete fix: `Remove <code>sys_mod.unblock_cmd_stream()</code> and run again. On the simulator the next command (<code>memcpy_d2h</code>) never gets through: the simulator stops when idle and the host aborts with “could be a kernel stall”; on hardware it would hang. (Put it back.)`

## Not verifiable
- "The first version had no `wait_done`": this is a development-history claim. The symptom it describes (sum 30.818 = sum after 95 values, max and min correct, count = 100) reproduces exactly when the barrier is removed. The intermediate debugging steps (exported `seen[N]`, running partial sums) were not re-performed, but they are consistent with the observed behaviour.
- The N:4096 and N:6000 premise was checked only on WSE-3. WSE-2 was not compiled at those sizes, though both have 48 KB per PE.
- The WSE-2 streaming data path inside memcpy (`memcpy/wse2`) was not traced. The WSE-2 binding claim (task ID == color) is confirmed by SDK topic-03 and by a successful WSE-2 run.
