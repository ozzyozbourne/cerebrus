# ch06 · depth review

Summary: The chapter gets the main idea across (a DSD is a hardware loop, and a fabric DSD makes communication an operand), but it never says how fast a DSD op runs, what slows one down, or how the descriptor is held and changed at run time. There are no throughput figures. Bank conflicts are not mentioned. The DSR / `@load_to_dsr` / `@map` fast path, `mem4d_dsd`, `wavelet_index_offset` and the 16-bit packing in fabric DSDs are all missing. The full builtin family from `dsd_ops.csl` is not listed. The FIFO and async parts state rules but give no mechanism. I ran simulator microbenchmarks (single-tile-matvec plus variants, SDK 2.10.1, WSE-2 and WSE-3) to supply the missing numbers. They are below and can be used directly with a `measured` tag. Pedagogy review P1/P3/P5/P6/P7 already cover fabric-DSD declarations, `@increment_dsd_offset`, an async example, the one-consumer-per-queue rule and FIFO code. This review does not repeat those. It adds mechanism and numbers on top of them.

## Gaps and additions (prioritised)

### D1 [critical] No throughput numbers: how many elements per cycle does a DSD op process?
- **What is missing:** The chapter says a DSD removes "per-element instruction fetch", but it never says what one op costs. A learner cannot estimate any kernel's runtime.
- **Why it matters:** This is the core "how it behaves internally" fact of the chapter. It also explains Lab 3's measured "2.5 cycles per cell" (Ch.12), which the course currently leaves unexplained.
- **Source:** I measured these myself, by timing the `compute()` call of `benchmarks/single-tile-matvec` (the `<time>` TSC) with one memory DSD op over 1024 f32 elements in a 1×1 rectangle. Separate regions of `A_array` were offset by 1025 and 2050 words. Simulator, SDK 2.10.1.

  | op (1024 f32 elements, memory DSDs) | WSE-2 cycles | WSE-3 cycles | ≈ elements / cycle (W2 / W3) |
  |---|---|---|---|
  | `@fmovs(dA, dB)` | 526 | 271 | 2 / 4 |
  | `@fadds(dA, dB, dC)` | 1039 | 528 | 1 / 2 |
  | `@fmacs(dA, dB, dC, 2.0)` | 1039 | 1041 | 1 / 1 |
  | `@fmuls(dA, dB, 2.0)` | 1038 | 1040 | 1 / 1 |
  | two `@fmacs` back to back | 2066 | 2069 | 1 / 1 |

  Fixed cost per op ≈ 15 cycles (this includes the timestamp reads).
  Check against Ch.12: one fadds plus two fmacs per cell on WSE-3 = 0.5 + 1 + 1 = **2.5 cycles/cell**, which matches Lab 3's measured `88 + 2.5·n` exactly.
- **Proposed addition:** Add a section "How fast is one instruction?" after the builtins table. It has this table (tag `measured`, "simulator, SDK 2.10.1"), one paragraph, and the Lab 3 cross-check. The paragraph: a DSD op streams at a fixed rate per element after roughly 15 cycles of start-up. f32 multiply ops (fmacs, fmuls) run at one element per cycle on both chips. Moves and adds run 2× faster on WSE-3, so WSE-3 doubled throughput for simple ops but not for f32 FMAC. That fits Lab 3's finding that WSE-2 vs WSE-3 is "a wash" for f32. Do not claim a lane count for f32. The chapter only knows the rate, not the hardware cause.

### D2 [critical] Precision changes throughput: f16 versus f32
- **What is missing:** The chapter lists `h` variants but never says that half precision is where the SIMD width pays off (Ch.3 states 4-wide / 8-wide FP16).
- **Why it matters:** It links Ch.3's SIMD numbers to code the learner writes. It also corrects the naive expectation of an "8× speedup" on WSE-3.
- **Source:** I measured single-tile-matvec (`@map` + DSRs, y += A·x, N×N) with f32 `@fmacs` and with an f16 copy using `@fmach`. Simulator cycles:

  | N | f32 WSE-2 | f32 WSE-3 | f16 WSE-2 | f16 WSE-3 |
  |---|---|---|---|---|
  | 8 | 119 | 126 | 88 | 94 |
  | 32 | 1108 | 1110 | 597 | 406 |
  | 64 | 4216 | 4214 | 2165 | 1335 |

  The fits are: f32 ≈ N² + N + 54 (exact on WSE-3, i.e. **1 FMAC/cycle**); f16 WSE-2 ≈ 0.50·N² (**2 FMAC/cycle**); f16 WSE-3 ≈ 0.29·N² (**≈3.5 FMAC/cycle**). (The f16 timing used zeroed data. The f32 cycle counts were identical with real and zeroed data, so timing appears to be data-independent.)
  Vendor: WSE-3 FP16 SIMD is 8-way and WSE-1/2 is 4-wide (`wse_hardware.md` §3; report Ch.4 para).
- **Proposed addition:** Add a small grouped bar chart or table, "FMAC elements per cycle: f32 vs f16, WSE-2 vs WSE-3" (tag `measured`). Then one sentence: "The SIMD width is a ceiling, not a rate. In a memory-to-memory FMAC each element needs a read of y, a read of A and a write of y, so on WSE-3 we see about 3.5 rather than 8 f16 FMACs per cycle." Mark the memory-bound explanation `derived`.

### D3 [critical] Bank conflicts: data placement can double an op's cost
- **What is missing:** The chapter never mentions the 8 single-ported, word-interleaved SRAM banks (Ch.3 introduces them). It also does not say that operands which collide on a bank slow a DSD op down. The SDK benchmark pads and offsets arrays explicitly "to avoid bank conflicts", and the chapter never explains why.
- **Why it matters:** This is the one performance rule a DSD programmer controls directly, through array layout. Without it, `A_array[i+1]` and `padded_nb` in the SDK look like magic.
- **Source:** `benchmarks/single-tile-matvec/run.py`: "Calculate alignment and padding to avoid bank conflicts" (`align = 16`, `padded_nb = ceil(nb/4)*4`). `src/pe_matvec.csl`: `A_array: [nb*padded_nb+1]f32 align(16)` with `A_dsd ... -> A_array[i+1]`. Report Ch.4: "8 single-ported 6 KB banks, single-cycle, interleaved by 32-bit word". My simulator runs (WSE-3, f32):
  - matvec N=32: with the +1 offset, 1110 cycles; with `A_array[i]` (no offset), **2134**. N=64: 4214 → **8310**. That is about 2×.
  - Column padding: N=31 padded to 32 → 1078; unpadded (stride 31) → 1294 (+20%). N=33 padded to 36 → 1276; unpadded → 1440. N=30 unpadded → 984, which needs no padding.
  - In-place `@fmacs(dA, dA, dC, 2.0)` over 1024 elements: dC offset by 2050 words → 1040 cycles; offset 2048 or 2052 → **2064**. `@fadds(dA, dA, dC)` with offset 2048 → 527 (no penalty). `@fadds(dA, dB, dC)` with offsets 1024/2048 → 528 (no penalty).
- **Proposed addition:** Add a content paragraph and a small diagram. Diagram: 8 bank columns (words mod 8). Colour y[0..7] and A[0..7]. With no offset, element i of A and element i of y fall in the same bank, so each FMAC step needs that bank twice. With +1, they never collide. Text: "SRAM is 8 single-ported banks interleaved by word Vendor. An FMAC that updates y in place needs y and A every cycle. If the two streams hit the same bank, the op runs at half speed Measured: 2134 vs 1110 cycles for a 32×32 matvec. The SDK's matvec shifts A by one word and pads columns to a multiple of 4 words for this reason." Keep the exact conflict rule hedged ("in our runs, offsets of 0 or 4 words mod 8 between the in-place destination and the FMAC operand doubled the time; adds were unaffected"). It is empirical, not documented. Optional experiment for the widget: add a "bank view" toggle to the existing DSD visualizer that colours words by `addr % 8`, so a stride-8 column visibly sits in one bank.

### D4 [major] DSRs, `@load_to_dsr` and `@map`: the per-column overhead of a scalar loop
- **What is missing:** The chapter says a DSD "lives in a DSR" and stops there. It never shows that a DSD is a value the compiler loads into a DSR before each op. It also skips the SDK's explicit-DSR fast path (`@get_dsr`, `@load_to_dsr(..., .{.save_address = true})`, then `@map` over x), where the DSR's address advances by itself from column to column. Nor does it give the cost of the ordinary loop.
- **Why it matters:** This shows the next level of the mechanism: the address generator keeps state between ops. It also gives a real number for "the scalar loop around a DSD op is not free".
- **Source:** `benchmarks/single-tile-matvec/src/pe_matvec.csl` (excerpt below). `csl_programming.md` §4 Inferences ("The DSR allocator mentioned in topic-15 maps DSD values to DSRs, so DSDs that are not known at compile time cost DSRs"). `topic-15` README ("allow CSL's DSR allocator to use fewer DSRs"). Report Ch.9 toolchain paragraph (`--dump-dsr-alloc-graph`). My measurements (WSE-3, f32 matvec): the gemv-02-style loop `for j: @fmacs(y, y, col, x[j]); col = @increment_dsd_offset(col, padded_nb, f32);` → 252 / 2160 / 6352 cycles for N = 8/32/64, against 126 / 1110 / 4214 for the `@map` + DSR version. That is **≈ 33–35 cycles of overhead per column** for the loop against ≈ 1 for `@map` + `save_address`. WSE-2: 229 / 2034 / 6354.
  ```
  const y_dest_dsr = @get_dsr(dsr_dest, 0);
  const y_src0_dsr = @get_dsr(dsr_src0, 0);
  const A_src1_dsr = @get_dsr(dsr_src1, 0);
  fn step(curX: f32) void { @fmacs(y_dest_dsr, y_src0_dsr, A_src1_dsr, curX); }
  ...
  @load_to_dsr(y_dest_dsr, y_dsd, .{ .save_address = false });
  @load_to_dsr(y_src0_dsr, y_dsd, .{ .save_address = false });
  @load_to_dsr(A_src1_dsr, A_dsd, .{ .save_address = true });  // A keeps advancing
  @map(step, x_dsd);                                            // one step per x[j]
  ```
- **Proposed addition:** Add an advanced subsection, "Where the descriptor lives". Its contents:
  - DSRs come in destination / src0 / src1 roles.
  - The compiler normally loads them for you, and runtime-variable DSDs consume DSRs (`--dump-dsr-alloc-graph` shows the allocation).
  - With `save_address = true` the register keeps its end address, so the next op continues where the last one stopped. Since A is stored column-major with padded columns, the next op starts on the next column.

  Then add a two-row table with the measured cycles (loop vs `@map`+DSR) and the takeaway: "for short vectors the scalar loop around the instruction costs more than the instruction" (N=8: half the time is loop overhead). Tag all numbers `measured`. Mark the "48 DSRs" figure `vendor, WSE-3` (see accuracy A2).

### D5 [major] Worked memory-traffic and FLOP accounting for one DSD kernel
- **What is missing:** There is no worked example that turns a DSD op into bytes moved and FLOPs. The SDK benchmark has exactly this.
- **Why it matters:** It connects the chapter to Ch.1/Ch.2's bandwidth claims ("21 PB/s"). It also shows the WSE trade-off of re-reading and re-writing y from SRAM on every column instead of keeping it in a register.
- **Source:** `benchmarks/single-tile-matvec/run.py` comments: "STANDARD read/writes ... = nb*nb + 2*nb" (relative, cache-style) against "ACTUAL ... read, write full y nb times = 3*nb*nb + nb" (absolute); `total_flop = 2*nb*nb - nb`; `secs = max_cycles / 850000000.0`. README: "Relative ... where caching allows us to write the y vector only once ... Absolute refers to the actual number of memory accesses".
- **Proposed addition:** Add a worked example box for N = 64 on one PE, using the measured 4214 cycles. FLOPs = 2·64² − 64 = 8128. Actual SRAM traffic = 4·(3·64² + 64) = 49,408 B. At the SDK's 850 MHz assumption, 4214 cycles = 4.96 µs, so ≈ 10 GB/s actual SRAM traffic and ≈ 1.6 GFLOP/s per PE. Scaled to 900k PEs that is ≈ 9 PB/s and ≈ 1.5 PFLOP/s f32. Tag the result `derived`, and say that 850 MHz is the SDK's assumption. Point out the 12 bytes per FMAC (y read, A read, y write, 4 B each), which is why f32 FMAC is 1/cycle.

### D6 [major] `mem4d_dsd`: multi-dimensional walks and reduction by index omission
- **What is missing:** Only `mem1d_dsd` appears. The chapter never shows that a DSD can nest up to several induction variables, or that leaving an index out of the right-hand side makes a reduction or broadcast inside one instruction.
- **Why it matters:** It shows how far "loops as hardware" goes: a triple loop with a reduction becomes one `@fadds`. The notes list `mem4d_dsd` as a gap, but the SDK benchmarks contain a real use.
- **Source:** `benchmarks/25-pt-stencil/task.csl` lines 607–622:
  ```
  var buffer = @zeros([directionCount, pattern, chunkSize]f32);   // line 203
  const bufferDsd = @get_dsd(mem4d_dsd, .{
    .tensor_access = |i,j,k|{directionCount, pattern, chunkSize} -> buffer[i, j, k] });
  const accumulatorDsd = @get_dsd(mem4d_dsd, .{
    .tensor_access = |i,j,k|{directionCount, pattern, chunkSize} -> accumulator[k] });
  const dstDsd = @increment_dsd_offset(accumulatorDsd, offset, f32);
  @fadds(dstDsd, dstDsd, bufferDsd);   // sums all directions × pattern chunks into accumulator
  ```
  The comment there: "buffer contains data received from each neighbor in all 4 cardinal directions".
- **Proposed addition:** Add a short paragraph with the excerpt above, and a widget preset or small static diagram. The diagram shows a 4×2×3 buffer walked in i,j,k order, with arrows folding every (i,j) slice onto the same 3-word accumulator. Text: "The destination ignores i and j, so it revisits accumulator[0..k) once per (i,j). That turns a triple loop with a reduction into a single instruction." Tag `sdk`.

### D7 [major] Data-driven addressing: `wavelet_index_offset` and `.index`
- **What is missing:** Nothing tells the learner that an arriving wavelet can choose where a DSD op addresses memory. Ch.5's sparse wavelets (value plus index in a 32-bit payload) and this chapter's DSDs are never connected.
- **Why it matters:** This is the internal mechanism behind dataflow sparsity (the report's Ch.4 "sparsity is native" paragraph). A data task receives (x_j, j) and runs a whole column FMAC on column j, so a zero x_j is never sent and its column is never touched.
- **Source:** `benchmarks/gemv-checkerboard-pattern/pe.csl` lines 65–87:
  ```
  const dsd_A = @get_dsd(mem1d_dsd, .{ .tensor_access = |i|{A_local_dim_x} -> A[i, 0],
                                       .wavelet_index_offset = true });
  task fmac_task(wlet_data: f16, idx: u16) void {
    @fmach(dsd_mul_temp, dsd_mul_temp, dsd_A, wlet_data, .{ .index = idx });
    ...
  ```
  Also `tutorials/sdklayout-05-gemv/gemv.csl`. `topic-04` README: "lower 16 bits to contain data … upper 16 bits to contain the index".
- **Proposed addition:** Add a paragraph plus a mini diagram. A wavelet [idx | value] arrives → data task → `@fmach(..., .index = idx)` → the DSD base shifts by idx and the op runs on column idx. Add a callout linking it to sparsity: "the sender filters zeros (Ch.3/5), and the receiver's DSD jumps straight to the right column". Tag `sdk`. Give the exact offset semantics (whether idx scales by row length or by element) only after checking the builtin reference. The code is consistent with the offset selecting column `idx` of an `[A_local_dim_x, …]` array whose rows are contiguous… mark this `derived` until it is confirmed.

### D8 [major] The complete builtin family, from `dsd_ops.csl`
- **What is missing:** The table lists 6 rows and "...". The SIF library enumerates the full set of type-dispatched DSD builtins: conversions, abs, neg, norm, max, sub, scale and the mixed-precision `hs` forms.
- **Why it matters:** The learner needs to know what the hardware can do in one instruction (for example f32↔f16 conversion, max for ReLU/pooling, `@fscales`, integer sub). The library is also a useful CSL pattern: `comptime` type dispatch over builtins.
- **Source:** SIF `csl-libs/dsd_ops.csl` (178 lines): `convert` → `@fh2s, @fh2xp16, @fmovh, @fs2h, @fs2xp16, @fmovs, @xp162fh, @xp162fs, @mov16`; `abs` → `@fabsh/@fabss`; `neg` → `@fnegh/@fnegs`; `norm` → `@fnormh/@fnorms`; `mov` → `@fmovh/@fmovs/@mov16/@mov32`; `add` → `@faddh/@faddhs/@fadds/@add16`; `fmac` → `@fmach/@fmachs/@fmacs`; `max` → `@fmaxh/@fmaxs`; `mul` → `@fmulh/@fmuls`; `scale` → `@fscaleh/@fscales`; `sub` → `@fsubh/@fsubs/@sub16`.
- **Proposed addition:** Expand the table into a compact matrix. Rows are operations (mov, add, sub, mul, scale, fmac, max, abs, neg, norm, convert). Columns are f16 / f16→f32 / f32 / i16·u16 / i32·u32. Each cell holds the builtin name or "—". Tag `sdk, csl-libs/dsd_ops.csl`. Add one line saying the library can be imported as `@import_module("<dsd_ops>")` to write type-generic code (e.g. `dsd_ops.fmac(f32, f16, dst, a, b, s, .{})`). Fold in accuracy fixes A1 and A4.

### D9 [major] FIFO internals: capacity, the two-microthread cost, and the alternatives
- **What is missing:** The chapter does not explain *why* a FIFO works: a push microthread and a pop microthread decouple producer from consumer, and the buffer size is the new capacity. It also leaves out the "infinite extent" idiom `0x7fff`, the resource cost, and pipeline-03's fix of moving the FIFO to a separate "artificial halo" PE.
- **Why it matters:** It turns the FIFO from a magic word into a mechanism with a cost the learner must budget (2 of 8 microthreads plus SRAM).
- **Source:** `pipeline-02-fifo/README.rst` ("binds two microthreads to the FIFO: one pushes data into the FIFO, and the other pops the data out. As long as the parameter size does not exceed the capacity of the FIFO, H2D can always push all data"; "The FIFO requires two microthreads and a scratch buffer"). `pipeline-02-fifo/pe_program.csl` (`var fifo_buffer = @zeros([1024]i16)`, `const INFINITE_DSD_LEN: u16 = 0x7fff;`, `@mov16(fifo, h2d_in_dsd, .{.async=true}); @mov16(C1_out_dsd, fifo, .{.async=true}); @add16(d2h_out_dsd, C1_in_dsd, one_dsd, .{.async=true});`). `pipeline-03-multiple/README.rst` ("move such FIFO outside the kernel … artificial halo … west.csl implements a FIFO"). `sdklayout-03 add2vec.csl` (the FIFO as the WSE-3 two-input workaround: `@mov16(fifo, input2, …); @add16(output, input1, fifo, …)`).
- **Proposed addition:** Add a diagram: H2D queue → [µthread A: push] → SRAM ring buffer (1024 words) → [µthread B: pop] → C1 → router RAMP→RAMP → `@add16` → D2H. Label "capacity: hardware queue ≈ a few wavelets → FIFO = 1024". Follow it with a three-row table, "Ways to absorb a burst": none (pipeline-01: stalls past 14 wavelets in that I/O configuration); FIFO on the same PE (pipeline-02: +2 microthreads, +buffer); FIFO on a neighbour PE (pipeline-03: kernel PE keeps its microthreads). A possible experiment for a lab: build pipeline-01 with `size` = 14 and 15 on both architectures to show the stall boundary (the README states 14; the WSE-3 value is "architecture-dependent").

### D10 [major] Async ops: microthread mapping and what "completion" means
- **What is missing:** Pedagogy P5 asks for an example. The missing mechanism is that each async op occupies a microthread chosen by its queue ID on WSE-2 and by `.ut_id` (or defaulting to the queue ID) on WSE-3. The chapter also omits that `.unblock` with `@block` inside a data task is the standard "one send in flight" throttle.
- **Source:** `topic-15-wse3-microthreads/README.rst` ("On WSE-2, the queue ID of an input or output fabric DSD corresponds to the ID of the microthread … On WSE-3 … any microthread ID 0 to 7 can be used with any of queues 0 to 7"; code `const send_color_ut = @get_ut_id(4); @fmovs(out_dsd, y_dsd, .{ .async = true, .ut_id = send_color_ut, ...})`). `topic-09-fifos/buffer.csl` (`task process_task(element: f32) void { @block(process_task_id); elem[0] = element*element*element; @fmovs(out_dsd, elem_dsd, .{ .async = true, .unblock = process_task }); }`). `gemv-checkerboard-pattern/pe.csl` `wtt_memcpyh2d_x` uses the same pattern.
- **Proposed addition:** Add a small table: "which microthread does this op use?" (WSE-2: = queue ID; WSE-3: `.ut_id` if given, otherwise the queue ID; memory-only async ops: per `.ut_id`). Add a 4-step timeline of the block/unblock throttle: wavelet arrives → task runs, blocks itself, starts the async send → the next wavelets wait in the queue → the send completes and unblocks → the task runs again. Tag `sdk`. Link to Ch.5's "A real hang".

### D11 [minor] Fabric DSD data width: 16-bit operands pack two per wavelet
- **What is missing:** The text says "extent counts wavelets" (or will, after P1), but with 16-bit ops the extent counts 16-bit operands, two per 32-bit wavelet.
- **Source:** `sdklayout-04-h2d-d2h/add2vec.csl` lines 10–13: "Each operand is 16-bits while 'size' specifies the number of 32-bit wavelets. Each wavelet packs 2 16-bit operands." `const input1 = @get_dsd(fabin_dsd, .{.extent = size * 2, …`. The gemv-checkerboard comment "TODO: Enable SIMD on memcpy library" hints that this interacts with SIMD.
- **Proposed addition:** Add one sentence and a mini diagram of a 32-bit wavelet split into two f16 lanes, inside the fabric DSD section. Tag `sdk`.

### D12 [minor] Run-time DSD editing builtins: the full set with real uses
- **What is missing:** Beyond P3's `@increment_dsd_offset`, the chapter should list `@set_dsd_base_addr`, `@set_dsd_length` and `@set_dsd_stride`, with one composed example.
- **Source:** `benchmarks/fft-1d-2d/fft.csl` line 116: `var fDSD = @set_dsd_length(@increment_dsd_offset(@set_dsd_base_addr(Xaux_dsd, f_twiddle), 1, tensor_type), N); fDSD = @set_dsd_stride(fDSD, 2);` (it negates the imaginary parts of interleaved complex twiddles: `@fnegh(fDSD, fDSD)`). `conjugate-gradient/src/blas.csl` uses `@set_dsd_length` (21 files use it).
- **Proposed addition:** Add a 4-row table (builtin, what it changes, SDK example). Add the FFT one-liner as the worked example ("every second word starting at word 1 = the imaginary parts"). The visualizer can show it as base 1, stride 2.

### D13 [minor] Explain the "fixed cost" of an instruction for small extents
- **What is missing:** Short vectors are dominated by start-up. The measured fixed cost of about 15 cycles per op, and about 88 cycles per stencil step in Lab 3, means DSDs only pay off above roughly 16–32 elements.
- **Source:** the D1 measurements (1024-element op = N + ~15). Ch.12 `88 + 2.5·n`. The N=8 matvec rows in D4.
- **Proposed addition:** One sentence and a tiny line chart "cycles vs extent" (a straight line with intercept ~15 and slope 1 for fmacs). Optionally add a widget input "extent" that prints the estimated cycles for each op from the D1 table.

## Out of scope for this chapter (new-chapter or cross-chapter ideas)
- **Ch.3:** Replace the vague "SIMD lanes driven by descriptors" with the measured per-op rates from D1/D2. State that f32 FMAC runs at 1 element/cycle on both chips (measured), so the 8-wide figure applies only to 16-bit types, and even there memory traffic caps it at about 3.5.
- **Ch.12 (Lab 3):** Explain the measured 2.5 cycles/cell as 0.5 (fadds) + 1 (fmacs) + 1 (fmacs). Add an f16 exercise predicting about a 2× (WSE-2) / 3.5× (WSE-3) gain from D2.
- **New lab or Ch.10 extension, "Performance lab: one PE":** single-tile-matvec as a lab. Have the learner measure N²+N+54 and break the +1 offset to see 2× (D3). Then rewrite with a scalar loop to see ~35 cycles/column (D4), and switch to f16 (D2). All four runs take seconds in the simulator. Recipe: copy `benchmarks/single-tile-matvec`, compile with `--fabric-dims=8,3 --fabric-offsets=4,1 --params=width:1,height:1,tile_size:N,iters:1`, and time with the existing `maxmin_time` TSC buffer (`run.py`).
- **Ch.5/Ch.13–15:** The `wavelet_index_offset` sparse-GEMV mechanism (D7) is a concrete point of comparison with GPU sparse kernels and Tenstorrent in Ch.15.
- **Ch.9:** Mention `--dump-dsr-alloc-graph` when explaining compiler output (ties to D4).
