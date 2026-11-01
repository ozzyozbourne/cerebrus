# ch03 · depth review

Summary: Chapter 3 is short (~14 KB of HTML). It lists the PE's parts correctly but rarely says how they behave. Its one "mechanism" figure (relative vs absolute bandwidth) is mis-explained, a problem the accuracy and pedagogy reviews already cover. The biggest depth gaps are these:
1. There are no throughput numbers for the CE. The f32 rate every lab depends on is missing, and so is what "8-way FP16" buys in practice.
2. There is no real memory map of the 48 KB: code, task table, runtime and data, and the memory-mapped config registers above 48 KB.
3. Microthreads are not explained: what they are, priorities, queue coupling on WSE-2 vs WSE-3, and queue counts.
4. Bank interleaving has no concrete model, and stride costs are never shown.

I ran small simulator experiments (SDK 2.10.1, `cslc` + `cs_python`, both archs) to supply measured numbers for 1, 2 and 4. They are reported below and can be reproduced in `/home/user/cerebras-sdk/tmp/rev-ch03-depth/stm/` (sources kept, build outputs deleted). All are **simulator** cycle counts. Tag them `Measured (simulator, SDK 2.10.1)`, never as hardware.

## Gaps and additions (prioritised)

### D1 [critical] No CE throughput numbers: f32 rate, FP16 rate, and what SIMD width buys
**What is missing.** The chapter gives only the vendor FP16/INT8 SIMD widths. It never says how many f32 FMAs a PE does per cycle, and every lab and the budget widget use f32. The research notes list the FP32 width as a gap (`wse_hardware.md` §3 Gaps).

**Why it matters.** Learners cannot estimate the compute time of any lab kernel. They will also assume "8-way" applies to f32.

**Source.** My experiment with the SDK benchmark `examples/benchmarks/single-tile-matvec/src/pe_matvec.csl`. It times the inner loop on the PE with the `<time>` timestamp counter, so host I/O is excluded. Width = height = 1, `--fabric-dims=8,3 --fabric-offsets=4,1`, `iters:1`, `--verify` passed for f32. For the f16 run I made a copy, `src/pe_f16.csl`, with every f32 changed to f16 and `@fmacs`→`@fmach`. The structure is the same: `@map` over x with explicit DSRs.

Measured cycles for y = A·x, N×N (A padded to a multiple of 16 B):

| N | FMACs | f32 WSE-3 | f32 WSE-2 | f16 WSE-3 | f16 WSE-2 |
|---|---|---|---|---|---|
| 8 | 64 | 126 | 119 | 94 | 88 |
| 25 | 700 (padded 28×25) | 780 | 778 | – | – |
| 64 | 4,096 | 4,214 | 4,216 | 1,335 | 2,165 |
| 96 | 9,216 | 9,366 | 9,372 | – | – |
| 128 | 16,384 | (does not fit) | – | 5,046 | 8,377 |

Derived (tag Derived):
- f32 FMA runs at almost exactly **1 element per cycle on both WSE-2 and WSE-3**. A fit is cycles ≈ 54 + 1·N(columns) + 1·FMAC: a ~54-cycle fixed cost, about 1 cycle per column for loading x and stepping the DSR, and 1 cycle per FMA. So f32 is effectively scalar (1-wide) in the simulator, and WSE-3 is no faster than WSE-2 for f32.
- f16 `@fmach` reaches about **3.2 FMA/cycle on WSE-3 and about 2.0 on WSE-2** at N = 128. That is ~1.65× faster for WSE-3, but well below the nominal 8-way and 4-way. The likely reason is that each FMA also reads and writes y in SRAM, so memory traffic, not lanes, limits the rate. This is an inference; the simulator does not say why.
- Peak arithmetic: 1 f32 FMA = 2 FLOP/cycle per PE. At the SDK's 850 MHz assumption that is 1.7 GFLOP/s per PE, and ×900k ≈ 1.5 PFLOP/s f32 for the wafer (Derived, simulator-rate × vendor core count). Compare this with the 125 PF sparse FP16 headline.

**Proposed addition.**
1. A new subsection "How fast is one PE?" after "Compute", with the table above (trimmed to N = 8, 64, 96/128) and three sentences:
   - "In the simulator, f32 multiply-accumulate runs at one element per cycle on both generations, so treat f32 as 1-wide."
   - "FP16 runs about 3× faster on WSE-3 and 2× on WSE-2. That is less than the 8- and 4-lane widths, because each FMA also reads and writes the accumulator in SRAM."
   - "Every kernel also pays a fixed start-up cost of tens of cycles, and a little more for each new DSD."
2. A small widget: a slider for N (8–104) and a dtype toggle. Plot predicted cycles = 54 + N + N²/r with r = 1 (f32) or r ≈ 3.2/2.0 (f16, WSE-3/WSE-2), plus the measured points as dots. This links directly to the budget widget's M×N.
3. Add a Check-yourself question: "A 64×64 f32 matvec on one PE: about how many cycles?" Answer: ≈ 4,100–4,200; measured 4,214.

### D2 [major] The 48 KB has no real memory map; the "~2 KB code" figure is wrong for WSE-3
**What is missing.** The chapter says code, stack, data and runtime buffers share the 48 KB, but it never shows how. The accuracy review (A5) corrects the code size from `.text` alone. The full section map shows that the overhead on WSE-3 is larger still, because of a 1 KB task table.

**Source.** `llvm-readelf -S` and `cs_readelf -m` on `out/bin/out_0_0.elf` of single-tile-matvec, built with `--memcpy --channels=1` (Measured, cslc 2.10.1):

| Section | WSE-3 (N=8) | WSE-2 (N=8) |
|---|---|---|
| `.data.lo` (DSR init etc.) | 0x0000, 56 B | 0x0000, 712 B |
| `.text` (code: user + memcpy runtime) | 0x0038, 3,192 B | 0x02c8, 2,232 B |
| `.data` + `.bss` (user arrays + runtime vars) | 0x0cb0, 688 B | in `.data.lo`/`.bss` |
| `.task_table` | 0x0f60, **1,024 B** | 0x0b80, ~512 B (5 pieces) |
| total "Memory used" (cs_readelf -m) | **4,960 B** | **3,458 B** |
| user data in that total (A 260 + x 32 + y 32) | 324 B | 324 B |

The non-user overhead of a minimal memcpy program is therefore ≈ **4.6 KB on WSE-3 and ≈ 3.1 KB on WSE-2**.

I also ran a capacity probe on WSE-3 with the same program at f32 N = 104. A (43,268 B) + x + y compiles, and `cs_readelf -m` reports 48,736 B used of 49,152. At N = 106 (A ≈ 45.8 KB) the link fails with `ld.lld: error: ran out of PE memory for data (section .bss)` / `ran out of PE memory for task table`. The real ceiling for user arrays in this program is ≈ **44 KB**, consistent with the SDK's "< 46 KB" assertion (`spmv-hypersparse/run.py`).

In the same ELF, the config sections (`.fabric_routes` 0xf800, `.fabric_switches` 0xf900, `.filters` 0xf680, `.ce_in_q`, `.prng_state`, `.fpcw`, `.active_ival`, `.blocked_ival`, `.blocked_ut_ival` around 0xfc00) sit **above 48 KB, in a 64 KB address space**. `csl-libs/target/wse3.csl` lists these as memory-mapped registers: `COLOR_CONFIG = 0x7c00*2`, `SWITCH_CONFIG = 0x7c80*2`, `INPUT_QUEUE_CONFIG`, `TIMESTAMP_COUNTER = 0x7b30*2`, `TASK_PRIORITY = 0x7e08*2`, and so on, with `word_size = 2`, `reg = u16`. Router tables, task active/blocked bit vectors and queue configs are therefore just addresses the CE reads and writes (`@get_config`/`@set_config`).

**Why it matters.** It gives "48 KB is everything" a concrete layout. It explains why the widget's 2 KB is optimistic. It also shows that the router and task picker are configured through memory-mapped registers, which is the bridge to Ch. 4 and 5.

**Proposed addition.**
1. A horizontal "address map" diagram from 0x0000 to 0xFFFF. Bands: `.data.lo` | `.text` ~3.2 KB | `.data/.bss` (your arrays grow here) | `.task_table` 1 KB | free | **0xC000 = 48 KB end of SRAM** | gap | memory-mapped config 0xF600–0xFC40 (routes, switches, filters, queues, task bits, timestamp). Label it with the WSE-3 values above.
2. In the budget widget, add a WSE-3/WSE-2 toggle that sets overhead to 4.6 KB / 3.1 KB (replacing `code = 2048`). Add a line: "Measured: user arrays above ~44 KB fail to link on WSE-3 ('ran out of PE memory for task table')."
3. One paragraph: "You can see this yourself: `cs_readelf -m out/bin/out_0_0.elf` prints 'Memory used', and `--sym` lists every symbol with its address and the banks it occupies."

### D3 [major] Microthreads: mechanism, priorities and WSE-2 vs WSE-3 coupling are missing
**What is missing.** The chapter says "up to eight such operations at once, one per microthread", and that IDs are exposed on WSE-3. It does not say what a microthread holds, how it competes with the main (task) thread, or how the queue coupling differs between generations. The pedagogy review (P1) adds a definition. This proposal adds the mechanism and the numbers.

**Source.**
- `tutorials/topic-15-wse3-microthreads/README.rst` and `left_pe.csl`: "On WSE-2, the queue ID of an input or output fabric DSD corresponds to the ID of the microthread in which that operation executes. On WSE-3 … any microthread ID 0 to 7 can be used with any of queues 0 to 7." Code: `const send_color_oq = @get_output_queue(2); const send_color_ut = @get_ut_id(4); @fmovs(out_dsd, y_dsd, .{ .async = true, .ut_id = send_color_ut, .activate = exit_task_id });`. The README also says: "By using explicit microthread IDs, we allow CSL's DSR allocator to use fewer DSRs", and that "two operations cannot concurrently use the same microthread". On WSE-3, output queues "cannot be re-used with a different color if they have not yet been drained", so programs tend to use up queues, and therefore microthreads, unless the IDs are decoupled.
- `csl-libs/target/wse2.csl`: `NUM_INPUT_QUEUES = 8`, `NUM_OUTPUT_QUEUES = 6`. `wse3.csl`: `NUM_INPUT_QUEUES = 8`, `NUM_OUTPUT_QUEUES = 8`, `REGS_PER_INPUT_QUEUE = 2` (vs 1 on WSE-2).
- `csl-libs/tile_config/main_thread_priority.csl`: "The meanings of main thread priority levels are relative to microthread priorities: MEDIUM_LOW: Between low- and medium-priority microthreads. MEDIUM … MEDIUM_HIGH … HIGH: Same priority as high-priority microthreads". It is set through the MISC_CFG register, bits 5–6 (`main_thread_priority_offset = 5`). Microthreads therefore have priority classes, and the main thread (the running task's instructions) is arbitrated against them.
- `tutorials/pipeline-01-basic/README.rst`: "The microthread is necessary because the CE must have some resources to run memcpy kernel. The kernel stalls if a blocking instruction `@add16(outDsd, inDsd, 1)` is used."
- cslc-driver flag `--disable-auto-microthread-id` (`csl_programming.md` L165).

**Why it matters.** It turns the WSE-3 "trap" covered in Ch. 5 into a consequence of a shared, finite resource. It also explains why a blocking fabric op can starve the memcpy runtime on the same CE.

**Proposed addition.**
1. A table "Microthreads and queues by generation":

| | WSE-2 | WSE-3 |
|---|---|---|
| microthreads | 8 | 8 (IDs 0–7) |
| input queues / output queues | 8 / 6 | 8 / 8 |
| which microthread runs a fabric op | = its queue ID (fixed) | any, via `.ut_id` (defaults to queue ID) |
| data-task IDs | colors 0–23 | input queues 0–7 |

2. A paragraph explaining the CE as "one main thread (the current task) plus eight microthreads, sharing one datapath. A hardware arbiter interleaves them by priority. The main thread's priority can be set from MEDIUM_LOW to HIGH relative to the microthreads." Tag it SDK 2.10.1. Do not claim cycle-level switching; the hyper-accel claim is secondary.
3. Optional diagram: 8 microthread slots, each holding (op, DSR operands, completion `.activate`/`.unblock` task), feeding one SIMD datapath through an arbiter, with the main thread as a ninth input.

### D4 [major] Bank interleaving has no concrete model and no cost of breaking it
**What is missing.** The chapter asserts "interleaved by 32-bit word … lets a vector instruction read and write several consecutive words per cycle". It gives no address→bank rule, no evidence, and no cost of strided access.

**Source.**
- `cs_readelf --sym` on the matvec ELFs prints a "Banks" column for every symbol. On both archs it shows **16-bit granularity**: a 2-byte variable at 0xcb0 → bank 0, at 0xcb4 → bank 2, at 0xcb8 → bank 4, at 0xcbc → bank 6. A 4-byte one at 0xcc0 → banks 0–1, and a 260-byte array → banks 0–7. That is bank = (byte address / 2) mod 8, a 16-byte stripe. This **conflicts with the "interleaved by 32-bit word" claim** (an arXiv source via a search extract, in `wse_hardware.md` §3), which would give a 32-byte stripe. The benchmark pads rows to 16 B "to avoid bank conflicts" (`single-tile-matvec/run.py`: "Calculate alignment and padding to avoid bank conflicts", `align = 16`), and `target/wse3.csl` has `FIFO_MIN_ALIGNMENT = 16` (WSE-2: 8). Both are consistent with a 16-byte stripe on WSE-3. Flag this to the accuracy fixer: the chapter should say "interleaved in 16-bit units (as the SDK's cs_readelf shows)" or present both views.
- My stride experiment (`src/pe_stride.csl`). One synchronous DSD op over 256 f32 elements, `tensor_access = |i|{256} -> a[i*s]`, both operands with the same stride; cycles from `<time>` (Measured, simulator):

| op (256 × f32) | stride 1 | 2 | 4 | 8 |
|---|---|---|---|---|
| `@fadds` a=a+b, WSE-3 | 162 | 290 | 546 | 799 |
| `@fadds` a=a+b, WSE-2 | 294 | – | 550 | 804 |
| `@fmovs` a=b, WSE-3 | 92 | – | 284 | – |

  Derived: contiguous f32 add is ~0.63 cycles/element on WSE-3, ~1.8× faster than WSE-2's ~1.15. With stride 4 or more, both generations fall to ~2.1 and then ~3.1 cycles/element and become **equal**. WSE-3's gain needs contiguous (bank-spread) access. (Caveat: `@fmacs` with an immediate scalar on stride-1 vectors measured 546 cycles, slower than in the matvec form. The cost depends on operand form, so present only the `@fadds`/`@fmovs` rows.)

**Why it matters.** This is the internal reason why layout and padding matter on a cache-less machine. It also gives the "single-cycle SRAM" claim a measured shape.

**Proposed addition.**
1. Replace the interleaving sentence with the 16-bit-unit rule plus the table above.
2. Build the visuals review's P5 bank-interleaving widget with bank = (byte addr / 2) mod 8 rather than (word mod 8), and show the measured cycles/element for the stride selected (1, 2, 4, 8) next to the hit counts.

### D5 [major] Explicit DSRs: a real example of descriptors living in registers
**What is missing.** "48 DSRs hold DSDs" is stated, but the chapter never shows that DSRs are named, finite registers the program can load directly. Ch. 6 teaches DSDs as values; the register side belongs in this chapter.

**Source.** `benchmarks/single-tile-matvec/src/pe_matvec.csl`:

```
const y_dest_dsr = @get_dsr(dsr_dest, 0);
const y_src0_dsr = @get_dsr(dsr_src0, 0);
const A_src1_dsr = @get_dsr(dsr_src1, 0);
@load_to_dsr(A_src1_dsr, local_A_dsd, .{ .save_address = true });
@map(gemv_static_step_A, x_dsd);   // calls @fmacs(y_dest_dsr, y_src0_dsr, A_src1_dsr, curX)
```

`.save_address = true` makes the A descriptor's address persist, so each `@fmacs` continues where the last one stopped. A walks column by column with no `@increment_dsd_offset`. Also relevant: DSR classes `dsr_dest`/`dsr_src0`/`dsr_src1` (also used in `collectives_2d/pe.csl`), the topic-15 note on the DSR allocator, the cslc flag `--dump-dsr-alloc-graph`, and the `.data.lo` `__dsr_lowmeminit_*` 8-byte objects in the ELF, which are DSR initial images.

**Proposed addition.** A short paragraph plus the 5-line snippet under "Compute": "A DSR comes in three roles: destination, source 0 and source 1. An instruction names its operands by DSR. Loading a descriptor once and letting it advance (`save_address`) is how the benchmark streams A through `@fmacs` at one element per cycle (D1)." Link to Ch. 6.

### D6 [minor] Show the memory-traffic numbers that the "no caches" figure is about
**What is missing.** Once the figure is corrected (accuracy A2, pedagogy P2), the measured cycles let it make the real point: the WSE moves ~3× the bytes and still runs at ~1 FMA/cycle.

**Source.** single-tile-matvec, N = 64, WSE-3: relative 16,896 B, absolute 49,408 B, 4,214 cycles (my run; run.py prints these). 49,408 / 4,214 ≈ **11.7 B/cycle ≈ 3 × 32-bit accesses per cycle** (read y, read A, write y), against relative 4.0 B/cycle. At 850 MHz: ~10 GB/s per PE, ×900k ≈ 9 PB/s of the 21 PB/s vendor peak (Derived).

**Proposed addition.** Add a caption line: "Measured for N = 64: 4,214 cycles, so the PE's SRAM served 11.7 bytes every cycle, about three f32 accesses: read A, read y, write y." Connect it to the chapter's existing "23 GB/s per PE" sanity check. A plain f32 matvec uses about half of it.

### D7 [minor] Generation-difference table for PE-level resources
**What is missing.** WSE-2 vs WSE-3 differences are scattered (cache size, SIMD, microthread IDs).

**Source.**
- `csl-libs/target/wse2.csl` ("Tile map for WSE2 (Feynman)") and `wse3.csl` ("WSE3 (Schrödinger)").
- Fabric coordinate mask: 0x03ff (10 bits) vs 0x07ff (11 bits).
- Filters: 4 + 2 in two banks vs 6 in one bank.
- Output queues: 6 vs 8. FIFO_MIN_ALIGNMENT: 8 vs 16 B.
- `NUM_COLORS = 24` in common.csl for both.
- `prng_count = 4`, a 48-bit timestamp counter (`tsc_size_words = 3`).
- Cache 256 vs 512 B (HC34/HC2024).
- SIMD FP16 4 vs 8 (secondary for WSE-2).
- Measured f32 FMA rate the same on both, f16 ~2.0 vs ~3.2/cycle (D1).

**Proposed addition.** A compact two-column table at the end of "The anatomy", titled "What changed per PE, WSE-2 → WSE-3", tagging each row with its source.

### D8 [minor] Native word is 16 bits; registers are u16
**What is missing.** The chapter implies a 32-bit machine (32-bit words, 32-bit wavelets). `target/common.csl` has `word_size = 2; reg = u16; double_reg = u32`, and CSL addresses and config registers are 16-bit. That is why `memcpy` has a `MEMCPY_16BIT` mode and timestamps are three u16 words.

**Source.** `csl-libs/target/common.csl` L1–3. `cs_readelf -m` reports "4960 bytes (2480 words)".

**Proposed addition.** One sentence under Memory: "Internally the PE addresses memory in 16-bit words. The 48 KB is 24,576 words, and an f32 is two of them." This also supports D4's 16-bit bank rule.

### D9 [minor] A small "measure it yourself" experiment box
**Proposed addition.** A collapsible "Try it" box (no new program directory needed):

```
cp -r $EX/benchmarks/single-tile-matvec ~/stm && cd ~/stm
cslc src/layout_matvec.csl --arch wse3 --fabric-dims=8,3 --fabric-offsets=4,1 \
  --params=width:1,height:1,tile_size:64,iters:1 -o out --memcpy --channels=1
cs_python run.py --name out --verify      # → Max cycles ≈ 4214
cs_readelf -m out/bin/out_0_0.elf          # → Memory used
```

Suggested variations: `--arch wse2`, `tile_size:104` (fits) vs `106` (link error).

## Out of scope for this chapter (new-chapter or cross-chapter ideas)
- **Ch. 5 (tasks):** task and main-thread priority (`tile_config/task_priority.csl`: HIGH/LOW per task ID, via color on WSE-2 or input queue on WSE-3, in the TASK_PRIORITY register at 0x7e08). The 1 KB WSE-3 task table and the active/blocked bit vectors (`.active_ival`, `.blocked_ival`, `.blocked_ut_ival` in the ELF) would make the "activated ∧ unblocked" picker concrete.
- **Ch. 6 (DSDs):** the stride-cost table (D4) and the `save_address` DSR pattern (D5) could be reused or extended there. Note also that `@fmacs` cost depends on operand form (immediate scalar vs `@map` over x), which needs its own measurement before it is taught.
- **Ch. 9 (toolchain):** teach `cs_readelf -m`, `--sym` (with the Banks column) and `llvm-readelf -S` on the PE ELF. Neither is shown anywhere in the course.
- **Ch. 12 (stencil lab):** the lab's "~46 KB usable SRAM" assumption should become ~44 KB on WSE-3 (D2 probe).
- **Accuracy follow-up, course-wide:** the "interleaved by 32-bit word" claim (report Ch. 4, `wse_hardware.md` §3, chapter 3) conflicts with the SDK's cs_readelf bank model of 16-bit units (D4). The coordinator should decide which to teach, or present both.
- **Ch. 15 comparison:** use the measured per-PE f32 rate (2 FLOP/cycle/PE) and the derived ~1.5 PF f32 wafer figure next to the FP16 headline numbers.
