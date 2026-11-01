# ch12 · accuracy review

Summary: The program, its expected output and the browser simulation all check out. I recompiled and re-simulated copies, and every cell of the cycles table reproduces exactly when run again. The JS widget matches the device result bit for bit at the defaults. Three things are wrong. (1) The measurement method says "0 vs 100 steps = pure device work". That is not true: the 0-step baseline hides about 200 cycles, and it varies from run to run. The real marginal cost is about 2 cycles per step higher, so the model should be 90 + 2.5·n, not 88 + 2.5·n. (2) The hang story pins the problem on WSE-3. In fact the identical failure happens on WSE-2, the simulator dies with a fatal error rather than stalling silently, and the conflict is on microthread 3 as well as 2. (3) The memory limit is stated three different ways, and none of them matches what the compiler accepts. None of these is critical. The page's teaching points survive all three.

All re-measurements: SDK 2.10.1, `commands.sh` flags, copies in /home/user/cerebras-sdk/tmp/rev-ch12-acc/ (now deleted). "cycles" means `sim_stats.json` `cycle_count`.

## Findings

### A1 [major] "Difference = pure device work" is wrong; the true per-step cost is ~2 cycles higher and the baseline is noisy
- **Location:** src/12-lab-stencil.html, "Measuring a timestep": the paragraph before the table ("the host transfers are identical, so the difference is 100 timesteps of pure device work"), the table's "Cycles per step" column, and the paragraph after it ("~130 cycles each").
- **Problem:** The 0-step run does not give a clean zero-work baseline. Adding the first steps costs almost nothing, so differencing against 0 steps underestimates the per-step cost. The page shows this itself: it says 128 in the table and "~130 each" one line later. The 0-step and 1-step baselines also vary between identical runs. A single 0/100 difference can be off by tens of cycles per step.
- **Evidence (WSE-3, P=8, n=16 unless noted):**
  - 0 steps 3,991; 1 step 4,004 (+13); 2 steps 4,050 (+59). The first steps cost far less than 88 each.
  - Marginal slopes, each deterministic across repeats:
    - n=4: 50→100→200 steps = 7,905 / 12,905 / 22,906, so **100.0** per step (table: 98).
    - n=16: 10/50/100/200 = 5,071 / 10,291 / 16,791 / 29,791, so **130.0** (table: 128).
    - n=64: 19,664 / 32,164 / 57,164, so **250.0** (table: 248).
    - P=2, n=16: 8,535 / 13,585 / 23,685, so **101.0** (table: 99).
    - P=16, n=16: 50→100 = 10,691 → 17,219, so **130.6** (table: 128.5).
    - WSE-2, P=8, n=16: 100→200 = 16,103 → 28,703, so **126.0** (table: 125).
  - The marginal points fit **90 + 2.5·n** exactly (100 / 130 / 250).
  - Baseline variance from identical commands:
    - WSE-3 P=16 0 steps: 4,694 the first time, 4,371 on two later runs.
    - WSE-2 0 steps: 6,617, then 3,628, then 4,113.
    - WSE-2 1 step: 3,628, which is lower than one of the 0-step runs.
    - With the 6,617 baseline, WSE-2 would come out at 95 cycles/step instead of 125.
  - The 100- and 200-step totals were stable to ±1 cycle.
- **Concrete fix:** Replace the method sentence with: "To isolate the kernel, difference two runs that both do work, e.g. 100 and 200 steps; the slope is the per-step cost. (Differencing against 0 steps under-counts by ~2 cycles/step: the first couple of steps hide under the fixed launch/readback latency, and the 0-step total itself varies by hundreds of cycles between identical runs.)"
  - Change the table columns to 100 / 200 steps and cycles per step:
    - P=8 n=4: 12,905 / 22,906 / **100**
    - P=8 n=16: 16,791 / 29,791 / **130**
    - P=8 n=64: 32,164 / 57,164 / **250**
    - P=2 n=16: 13,585 / 23,685 / **101**
    - P=16 n=16: 17,219 / (re-measure 200) / **~130.6**
    - WSE-2 P=8 n=16: 16,103 / 28,703 / **126**
  - Change "88" to "90" everywhere: the bullet text, the model widget hint, the `88` constants and the `meas` array in the script (`[[4,100],[16,130],[64,250]]`), the label "fixed ≈ 90", the readout string, and Exercise 1 ("does the fixed 90 shrink?").
  - Change "WSE-2 vs WSE-3 … (125 vs 128)" to "(126 vs 130)".
  - Change the 10/50-step sentence to: "the slope between 10, 50, 100 and 200 steps is a constant 130 cycles."

### A2 [major] The hang is not WSE-3-specific, and the symptom and microthread are misdescribed
- **Location:** src/12-lab-stencil.html, `.callout.bug` "The hang". The same claim also appears in 05-tasks.html line ~100 and 03-processing-element.html line ~105, for the coordinator.
- **Problem:**
  - (a) "On WSE-3, async fabric operations run on the microthread with their queue's ID" has the architecture backwards. The SDK says the queue-ID = microthread-ID rule is the *WSE-2* rule. On WSE-3 that mapping is only the default, and you can override it.
  - (b) I rebuilt the "first version" (input queues 2/3) and it fails identically on WSE-2.
  - (c) The simulator does not stall with "no progress". It aborts with a FATAL microthread error in `sim.log`, and the host script then hangs waiting forever.
  - (d) With oq 2/3 and iq 2/3 there are two collisions: east send + west receive on 2, and west send + east receive on 3. The fatal error my run hit is on microthread 3.
- **Evidence:**
  - topic-15-wse3-microthreads/README.rst: "On WSE-2, the queue ID of an input or output fabric DSD corresponds to the ID of the microthread in which that operation executes. On WSE-3, queue IDs and microthreads can be decoupled … (if they are not explicitly specified, they default to the respective queue IDs)". The research report (Ch.4 table) says the same: "Microthread ID | Equal to queue ID | Explicit `.ut_id` (0–7)".
  - Reproduction: the current program with `@get_input_queue(4)`→`(2)` and `(5)`→`(3)`, P=8, n=16, 50 steps.
    - WSE-3 sim.log: `@2124 FATAL: P5.1: … Msg: trying to term ut_instr[3], but it's not ours` then `@2125 Stopping due to fatal error`.
    - WSE-2 sim.log: the same message at @2124/2125.
    - On both, cs_python never returned and had to be killed.
  - I could not reproduce the "cycle 1,894" figure.
- **Concrete fix:** Replace the callout body with: "The first version used output queues 2/3 and input queues 2/3. It compiled, then the host script hung; `sim.log` showed the simulator had aborted at cycle ~2,125 with `trying to term ut_instr[3], but it's not ours`. An async fabric op runs on the microthread whose ID equals its queue ID. That is fixed on WSE-2 and is the default on WSE-3, which also lets you choose an explicit microthread ID. So east-send/west-receive both claimed microthread 2 and west-send/east-receive both claimed 3. Moving the input queues to 4/5 fixed it on both architectures. Rule: give every concurrently active fabric operation its own microthread, and when a run hangs, read `sim.log` first." Also edit the pe_program.csl comment "on WSE-3 an async fabric op runs on the microthread with its queue's ID" to say "by default (always on WSE-2)". Make the matching edits in ch05 and ch03.

### A3 [minor] Memory limit stated three inconsistent ways; none matches the compiler
- **Location:** src/12-lab-stencil.html: the prose "memory allows about 5,000 f32 cells plus the scratch array"; the model script `maxN = Math.floor((46 * 1024) / 8) - 2` (= 5,886) and "~46 KB of usable SRAM"; and the slider `max="5000"`.
- **Problem:** The real limit depends on the architecture. The widget's 5,886 is about 7% too high for WSE-3. And because the slider stops at 5,000, the "no longer fit" warning can never appear.
- **Evidence:** cslc compile sweep, P=3:
  - WSE-3: n=5,500 links; n=5,520 fails (`ld.lld: error: ran out of PE memory for task table` at 5,600; `… for data (section .bss)` at 5,700+).
  - WSE-2: n=5,650 links; n=5,750 fails (`… section .data.hi`).
  - So usable data for u + lap is about 8·5,500 B ≈ 43 KB on WSE-3 and about 44 KB on WSE-2, not 46 KB. The 46 KB figure comes from a different benchmark (research report Ch.4).
- **Concrete fix:** Prose: "memory allows about 5,500 f32 cells per PE on WSE-3 (≈5,650 on WSE-2) once the scratch array, code and memcpy runtime are counted <span class="tag measured">Measured</span>". Script: `const maxN = 5500;` and "no longer fit (cslc fails above ~5,500 on WSE-3)". Slider: `max="6000"` so the warning can actually be reached.

### A4 [minor] "~130 cycles each" contradicts the table's 128
- **Location:** the sentence after the table.
- **Problem / Evidence:** The 10→50 and 50→100 slopes are 130.5 and 130.0, which is not the 128 in the table. Fixed by A1; listed separately in case A1 is only partly adopted.
- **Concrete fix:** see A1. At minimum, add "(the 0-step baseline under-counts slightly; see note)".

### A5 [minor] Validation claim understated
- **Location:** "The device result matches a numpy reference … to within 1e-5 relative error".
- **Problem:** run.py asserts `rtol=1e-5, atol=1e-6`, so "relative error" alone is imprecise. The actual result is stronger than the claim.
- **Evidence:** At α = 0.25 the device array equals the numpy reference bit for bit (`np.array_equal` True, max abs diff 0.0, WSE-3, 50 steps). At α = 0.3 it differs by ≤ 3.4e-7 relative (1.5e-8 abs), probably because the hardware `@fmacs` rounds differently.
- **Concrete fix:** "The device result is bit-identical to a numpy reference doing the same f32 arithmetic at α = 0.25 (other α values differ in the last bit or so; run.py checks rtol 1e-5, atol 1e-6), on both WSE-3 and WSE-2."

### A6 [minor] The widget is exact only at α values that are powers of two
- **Location:** widget hint, "This runs the same algorithm in your browser with Float32 arithmetic."
- **Problem:** The JS uses separate roundings (`fround(a*lap)` then the add). That is bit-exact against the device at α = 0.25: I reproduced all 16 printed values of expected_output.txt with node, and the max is 1.5459. At other α the device's multiply-add differs in the last bit (see A5). The text does not overclaim, since it marks only the default state as validated, but a learner might take "same algorithm" to mean identical at any α.
- **Concrete fix (optional):** append "(bit-identical to the device at α = 0.25; other α may differ in the last bit)".

### A7 [minor] The SDK stencil benchmarks are 3-D, and the 7-point one is not a time-marching stencil
- **Location:** "On a real wafer you would also go to 2-D domains and overlap the halo exchange with the interior update — the SDK's 7-point and 25-point stencil benchmarks do both."
- **Problem / Evidence:**
  - benchmarks/7pt-stencil-spmv/README.rst is titled "3D 7-Point Stencil SpMV". It does a single matrix-vector product, not time-stepping, with `zDim` elements per PE (a 3-D domain mapped onto the 2-D PE grid).
  - 25-pt-stencil is a time-marching app with `zdim` per PE.
  - Neither README mentions overlapping communication with compute. "overlap" appears only in 7pt-stencil-spmv/src/kernel.csl, and I did not confirm what it means there.
- **Concrete fix:** "…go to 3-D domains mapped onto the 2-D PE grid (each PE holds a z-column), as the SDK's 25-point stencil (time-marching) and 7-point stencil SpMV benchmarks do, and overlap the halo exchange with the interior update (Exercise 1)."

### A8 [minor] "~900k PEs" is the marketing count, not what a stencil can use
- **Location:** "This is the property that lets a stencil use all ~900k PEs."
- **Evidence:** The research report (Ch.2) gives 900,000 cores as the [Vendor] figure for WSE-3. On CS-2 the user-visible fabric is about 737k usable PEs (750×994 minus the margins), and the WSE-3 figure was not found.
- **Concrete fix:** "…lets a stencil scale to the whole wafer (hundreds of thousands of PEs)", or keep ~900k with a `<span class="tag vendor">Vendor</span>` tag.

## Not verifiable
- "stalled … at cycle 1,894": my reproduction aborted at cycle 2,124/2,125 instead. The original "first version" may have differed in ways the page does not record.
- How the fixed ~90 cycles splits among the halo transfers, completion tasks and task scheduling. This is plausible, but separating it would need instrumentation (another reviewer's rev-ch12-depth seems to be doing that).
- "f32 work does not benefit from WSE-3's wider FP16 SIMD": consistent with WSE-2 ≈ WSE-3 here (126 vs 130), but the f32 SIMD width is undocumented (research report: "FP32 SIMD width were not found").
- Exercise 3's claims about f16 builtins and how WSE-2 vs WSE-3 would compare were not run.
- The 850 MHz clock is accurately described as the SDK benchmarks' own assumption (bandwidth-test, conjugate-gradient, etc.). No official clock exists, as the research report also says. Checked; no problem found.
