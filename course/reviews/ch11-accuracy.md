# ch11 · accuracy review

Summary: The code, expected outputs and every number in the measured-cycles table reproduce exactly when I run them (03: 4,394 / 4,496 / 4,748 / 5,260 cycles; M sweep 3,025 / 11,463; 05: 5,456; WSE-2 also works). The generated page matches what `build.py` produces from the src. The serious problem is how the table is read. Those totals do not include any reduction cost. A copy of program 03 whose `reduce()` does nothing gives exactly the same total cycles. So the sentence "the simulator agrees with the model" has no evidence behind it. When I put timestamps around the kernel (TSC instrumentation), the streaming model does hold: about M + 7·P cycles, not the widget's M + 2P. Smaller problems: the prose says "M + P" but the widget says "M + 2P", "teal" should be green, the gemv tutorial range is overstated, the Exercise 1 hint is misleading (`@fmaxs` takes fabric DSDs), and a few numbers have no provenance tag. Verdict: the chapter is correct apart from the measured-evidence paragraph. That paragraph needs to be rewritten.

## Findings

### A1 [critical] The "measured" table does not measure the reduction, so it cannot back up the streaming model
- **Location:** src paragraph "The simulator agrees with the model. With M = 32 ... adds only 866 cycles in total — and part of that is the extra host copies ..." plus the table that follows it.
- **Problem:** The page offers the P sweep as simulator confirmation of streaming (≈ M + P) over store-and-forward (≈ P × M). But the totals come only from host memcpy. Taking the reduction out leaves the cycle count unchanged, so all 866 cycles come from host I/O, not "part of" them. These numbers also cannot tell the two models apart. Store-and-forward would add only about 14 × 34 ≈ 476 cycles between P = 2 and P = 16, which is less than the measured 866.
- **Evidence:** I made a copy of program 03 with `reduce()` replaced by `sys_mod.unblock_cmd_stream();` (no fmovs/fadds) and ran it with commands.sh on WSE-3, M = 32. Totals: P=2 4,394, P=4 4,496, P=8 4,748, P=16 5,260. At P=8: M=8 3,025, M=128 11,463. These are identical to the real program. I then made a second copy with `<time>` TSC stamps at the start of `reduce()` and in `exit_task`, using the same pattern as tutorials/topic-02-libraries. Start spread across PEs was 0. Kernel cycles from the first launch to the last PE finishing:

  | WSE-3, M = 32 | P=2 | P=4 | P=8 | P=16 |
  |---|---|---|---|---|
  | reduction kernel cycles | 58 | 73 | 101 | 158 |

  At P = 8, M = 8 / 32 / 128 took 77 / 101 / 199 cycles (≈ 1 cycle per element). WSE-2 at P = 8, M = 32 took 84 cycles. Each extra PE adds about 7.2 cycles on WSE-3 and about 5 on WSE-2. That fits streaming. Store-and-forward would add at least M = 32 cycles per hop. The kernel is about 2% of the 4,748-cycle total.
- **Concrete fix (src):** Replace the paragraph and table with the kernel-cycle table above, tagged `<span class="tag measured">Measured</span>`. Say these figures came from a TSC-instrumented copy of program 03, or add that instrumentation to program 03 and to expected_output. Then say: "Going from 2 to 16 PEs adds ~100 cycles (~7 per hop); store-and-forward would add ≥ 32 per hop." Keep the end-to-end totals only as a separate remark, for example: "End-to-end totals (4,394 → 5,260) are almost entirely host memcpy; a version with an empty `reduce()` gives identical totals." Delete "and part of that is the extra host copies".

### A2 [major] Per-hop constant: prose says M + P, widget says M + 2P, simulation shows about M + 7P
- **Location:** src "the reduction takes about **M + P** steps" and the widget readout `"≈ M + 2P"` / `"~2-cycle hop+ramp"` (`tp = p * 2 + i`).
- **Problem:** The two formulas on the page disagree with each other. The "~2-cycle hop+ramp" has no source, and it is about 3.5× smaller than what was measured. The widget model also has no provenance tag.
- **Evidence:** The kernel timings in A1 show ≈ 7.2 cycles per PE on WSE-3 (50, 58, 65, 73, 80, 87, 94, 101, ... per-PE completion times) and about 5 on WSE-2.
- **Concrete fix (src):** Change the prose to "about **M + c·P** cycles, where c is a few cycles per hop (≈ 7 on the WSE-3 simulator, router hop + ramp + FPU pipeline), not **M × P**". In the widget, either set the per-hop delay to 7 (`tp = p * 7 + i`, total `(P-1)*7 + M`) or keep 2 but label it as illustrative. Update the readout text to match, and add `<span class="tag derived">Derived</span>` to the widget hint.

### A3 [minor] "Every element must also cross the narrow host link twice" is incorrect
- **Location:** src "Changing M at P = 8 moves the total much more ... because every element must also cross the narrow host link twice."
- **Problem:** run.py copies P×M elements in (`memcpy_h2d(..., P, 1, M)`) and only M elements out (`memcpy_d2h(out, vs, P - 1, 0, 1, 1, M)`). Most elements cross once. The 3,025 and 11,463 figures also have no provenance tag.
- **Evidence:** programs/03-row-reduce/run.py lines 16 and 19. The noop copy in A1 gives the same 3,025 / 11,463, so this difference is entirely I/O.
- **Concrete fix (src):** "... because the host must copy P × M input elements in and M results out, while the on-wafer reduction grows by only ~1 cycle per element (77 → 199 cycles) <span class="tag measured">Measured</span>."

### A4 [minor] Multicast wording: "every router below" forwards south, and "a single multicast route"
- **Location:** src lede ("with a single multicast route") and Program 05 intro ("Every router below delivers each wavelet to its own CE *and* forwards it south"). The figcaption also says "One send, R receivers".
- **Problem:** The bottom router uses `rx NORTH → tx RAMP` and does not forward. The program has one color but three distinct route configurations. Only R−1 PEs receive over the fabric; the root uses its own memory copy. The figure itself draws all of this correctly.
- **Evidence:** programs/05-column-broadcast/layout.csl lines 17–23.
- **Concrete fix (src):** Lede: "with one color and multicast routes". Intro: "Every middle router delivers each wavelet to its own CE *and* forwards it south in the same hop (`.tx = .{RAMP, SOUTH}`); the bottom router only delivers." Caption: "One send, R − 1 fabric receivers (the root scales its own copy)."

### A5 [minor] The GEMV paragraph overstates which tutorials cover this
- **Location:** src "The SDK tutorials gemv-05 through gemv-09 walk through exactly this."
- **Problem:** gemv-05 has no communication between PEs. gemv-06 is a two-PE send, gemv-07 a 2×2 grid, gemv-08 the full broadcast + checkerboard pattern, and gemv-09 is about memcpy streaming mode. Also, gemv-08 does not use a bulk fabric-to-memory copy for the broadcast. Each x element is consumed by a wavelet-triggered task `recv_x` (`@fmacs` per wavelet), and the root also sends x down its own RAMP (`RX_R_TX_RS`). Program 05 does neither.
- **Evidence:** tutorials/gemv-05-multiple-pes/README.rst ("This program involves no communication between PEs"), gemv-08-routes-3/README.rst plus layout.csl line 67 and pe_program.csl lines 102–103, and gemv-09-streaming/README.rst.
- **Concrete fix (src):** "The SDK tutorials gemv-06 to gemv-08 build up to exactly this (gemv-08 is the full pattern; it consumes x with a wavelet-triggered task rather than a bulk copy) <span class="tag sdk">SDK 2.10.1</span>."

### A6 [minor] The figure caption says "teal", but the line is green
- **Location:** src GEMV figcaption "Orange/teal: checkerboard row reduction".
- **Evidence:** The script draws these lines with `cssVar(c % 2 ? "--green" : "--accent")`. `--green` is #15803d in light mode and #4ade80 in dark mode (assets/course.css lines 13 and 32).
- **Concrete fix (src):** "Orange/green: checkerboard row reduction of partial y."

### A7 [minor] The Exercise 1 hint suggests a fabric-capable max might not exist
- **Location:** src Exercise 1 "(Hint: is there a fabric-capable max builtin? If not, receive into memory and compare.)"
- **Problem:** `@fmaxs` accepts fabin/fabout DSDs directly, so the "if not" branch never applies. The hint as written may send learners down the wrong path.
- **Evidence:** I replaced `@fadds` with `@fmaxs` in a copy of program 03 (`@fmaxs(out_dsd, in_dsd, v_dsd, ...)` and `@fmaxs(v_dsd, in_dsd, v_dsd, ...)`) and checked against `V.max(axis=0)`. It compiled and passed (SUCCESS) on WSE-3. The SDK's own allreduce also uses `@fmaxs` with a fabric source (benchmarks/benchmark-libs/allreduce/pe.csl lines 607–613).
- **Concrete fix (src):** "(Hint: look for an `@fadds`-like builtin for max; does it accept fabric DSDs the same way?)"

### A8 [minor] Missing provenance tags and small run-to-run variation
- **Location:** The M sweep sentence (3,025 / 11,463) has no tag. The gemv claim has no SDK tag. The widget model has no derived tag. The "measured" totals are presented as exact.
- **Evidence:** The brief says "Every number should carry one." In repeat runs I once got 11,467 instead of 11,463, and once 5,410 instead of 4,496 for P = 4 (noop variant). The other runs reproduced exactly.
- **Concrete fix (src):** Add the tags as described in A2, A3 and A5. Optionally note "(±a few cycles run to run)".

## Not verifiable
- Whether the simulator's TSC values and cycle counts match real CS-3 hardware timing. All measurements here come from the SDK 2.10.1 simulator.
- The hardware basis for the widget's "one element per cycle per link" assumption. The measured kernel slope of ≈ 1 cycle per element is consistent with it, but I found no SDK document stating it.
- Checked and confirmed, so not findings: the callout's claim that braceless `if (a) s; else ...` fails with "Unexpected character" (I reproduced it with cslc; even `if (a) s; else s;` fails, while braceless `if (a) s;` alone compiles); the expected outputs for 03 and 05; the WSE-2 run for Exercise 3 (P=8, M=32: 4,548 total cycles, SUCCESS); the checkerboard description, which matches gemv-08's README.
