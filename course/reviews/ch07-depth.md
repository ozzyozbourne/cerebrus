# ch07 · depth review

Summary: The chapter covers the right topics: the narrow door, the halo, reserved resources, the six host calls, the command stream, copy vs streaming, and the program-02 race. Almost all of it is at the "what" level, though. The SIF memcpy sources (`memcpy/wse3/*.csl`, `runtime/layout_west_demux_cmdfan_multi.csl`, `runtime/demux.csl`) and the bandwidth-test benchmark explain HOW data actually moves: a two-stage demux, round-robin counter filters, row-wide participation, teardown-based completion, the RPC wire format, and buffer columns. They also give the exact halo arithmetic, which the chapter says is "not documented locally". The chapter has no worked example of the TCP-overhead cost, no explanation of ROW_MAJOR/COL_MAJOR, nonblocking calls, 16-bit transfers or buffer columns, and no mechanism for the gemv-09 "wrong order hangs" rule. I ran the bandwidth-test benchmark in the simulator (four configurations). Its numbers are below for an experiment box.

## Gaps and additions (prioritised)

### D1 [critical] How a copy-mode H2D actually travels: two-stage demux plus counter filters
- **What is missing:** The chapter says only that the west columns do "command fan-out and H2D demultiplexing". It never shows the path a wavelet takes or how a PE knows which wavelets are its own.
- **Why it matters:** This is the core internal mechanism of the chapter's topic. It explains why the host must split data, why every PE in a row takes part, and why ordering on the wire differs from the host array.
- **Source:** SIF `csl-libs/runtime/layout_west_demux_cmdfan_multi.csl` (header diagram, lines 1–103). `csl-libs/runtime/demux.csl` (header, lines 1–60). `csl-libs/memcpy/wse3/memcpyh2d.csl` (header, lines 17–80). `csl-libs/memcpy/wse3/memcpy.csl` (lines 13–38, 319–334). Read the SIF with `singularity exec <sif> cat /cb/toolchains/cslang/rel-sdk-2.10.0/202604012315-1813-1394a6ea/csl-libs/...`.
- **Proposed addition (paragraph plus animated SVG):**
  - The path is LVDS link (one "channel") → **demux adaptor** (1 column) → **demux** (1 column) → **cmd fan** (1 column) → core row.
  - The demux broadcasts the channel's stream north→south down its column. Each demux PE runs a **counter filter** that keeps every h-th wavelet ("round-robin a wavelet along a column", order x[l][h]) and turns it east into its row.
  - In the row, the cmd fan sends the data east on MEMCPYH2D_DATA (color 23). Every core PE's counter filter keeps every w-th wavelet: `limit = width-1`, `init_count = (limit+1-pid) % (limit+1)`.
  - Use the source's own worked example. With l = 4 and w = 4, the wire order is `x0 x4 x8 x12 x1 x5 x9 x13 x2 x6 x10 x14 x3 x7 x11 x15`. The counter values show that P0 keeps the wavelets where its counter is 0: x0, x1, x2, x3. P1 keeps x4…x7, and so on.
  - Widget: a 4-PE row with a step button. Each wavelet moves east, each PE's counter ticks, and the PE whose counter reads 0 shows the wavelet dropping into its SRAM (RAMP).
  - Tag: SDK 2.10.1 (library source).

### D2 [critical] Exact halo arithmetic and what each halo column is
- **What is missing:** The chapter says "3 west and 2 east" were measured, that the CS-2 rectangle must be "7 narrower, 2 shorter", and that "exact column roles … not documented locally". The roles and the arithmetic are in fact documented.
- **Why it matters:** It turns "--fabric-offsets=4,1 is magic" into derivable arithmetic. It also explains the buffer flags.
- **Source:**
  - SIF `runtime/layout_west_demux_cmdfan_multi.csl`, placement example lines 37–74. The 4×3 core drawing has columns: halo h | demux adaptor | demux | cmd | core… | mux | mux adaptor (or mux td, or nop) | h, with halo rows on top and bottom.
  - `benchmarks/bandwidth-test/run.py` lines ~238–247: `core_fabric_offset_x = fabric_offset_x(1) + 3 + width_west_buf`, `min_fabric_width = core_offset_x + width + 2 + 1 + width_east_buf`, `min_fabric_height = 1 + height + 1`.
- **Proposed addition:**
  - Relabel the existing 8×3 halo SVG. x=0 and x=7, and rows 0 and 2, are the **outer halo**. x=1 is the demux adaptor, x=2 the demux, x=3 the cmd fan, x=5 the mux, x=6 the mux adaptor. The demux-adaptor column has "nop" PEs in rows the LVDS does not enter.
  - Add a one-line derivation: west = 1 halo + 3 memcpy = 4 → offset x = 4. East = 2 memcpy + 1 halo = 3. 4 + 3 = 7 columns. 1 + 1 = 2 rows. This gives the CS-2 rule of 750−7 = 743 × 994−2 = 992.
  - Add a small calculator widget. Inputs: rectangle w×h, `--width-west-buf`, `--width-east-buf`. Outputs: minimum `--fabric-dims` and `--fabric-offsets`.
  - Measured note from my run (SDK 2.10.1, WSE-3, 5×5 core): ELF counts grow with `--channels`, from west/bin 8 and east/bin 6 ELFs at `--channels=1` to 11 and 8 at `--channels=4`. More channels means more demux and mux kernels, while the column count stays the same. These are ELF counts, not column counts. Tag Measured.
  - Delete the sentence "Exact column roles per --channels are not documented locally". Replace it with: "Each channel is one LVDS link feeding a demux that serves a band of rows (`height_demux_<j>`, up to 16 channels)".

### D3 [major] Worked example: when the 200 µs TCP overhead dominates, and nonblocking aggregation
- **What is missing:** The 200 µs and 7 Gb/s figures are quoted but never combined. Nothing explains `nonblock=True`, the returned `Task`, `task_wait`/`is_task_done`, or that the runtime "can aggregate multiple nonblocking commands together to reduce TCP overhead".
- **Why it matters:** It gives the reader a quantitative rule of thumb for batching transfers, and it is the main practical performance lever on the host side.
- **Source:** `benchmarks/bandwidth-test/run.py`, docstring factors (1)–(3) and the loop that uses `nonblock=True` for H2D, then `call("f_toc", [], nonblock=False)`. SdkRuntime introspection (SDK 2.10.1): `memcpy_* -> Task`, `task_wait(Task)`, `is_task_done(Task)`.
- **Proposed addition:**
  - Arithmetic, tagged Derived: at 7 Gb/s, 200 µs is the time to move about 175 KB. So a single-channel transfer smaller than about 175 KB spends more time on TCP overhead than on data.
  - Interactive "transfer time" calculator: `t = n_cmds × 200 µs + bytes / (channels × 7 Gb/s)`. Toggle "nonblocking (aggregated)", which sets n_cmds = 1 per batch, as an idealised assumption labelled as such. Show example cases of 1 KB, 100 KB and 44 GB.
  - Code snippet: `t = rt.memcpy_h2d(..., nonblock=True); …; rt.task_wait(t)`.
  - Caveat: nonblocking does not reorder commands. They are still serialised on color 22.

### D4 [major] Simulator experiment: host-transfer cycles from bandwidth-test
- **What is missing:** The chapter has no measured transfer numbers ("Lab 3 measures this" points away from it).
- **Why it matters:** It gives readers a reproducible experiment, real numbers, and a lesson in the difference between simulator and hardware.
- **Source:** `benchmarks/bandwidth-test` (README, run.py, commands_wse3.sh). My local runs, SDK 2.10.1, `--arch wse3`, `--fabric-dims=12,7 --fabric-offsets=4,1`, 5×5 PEs, loop_count=1:

  | Direction | channels | elems/PE | wavelets | cycles_send | reported MB/s |
  |---|---|---|---|---|---|
  | H2D | 1 | 5 | 125 | 1,471 | 289 |
  | H2D | 1 | 1000 | 25,000 | 24,954 | 3,406 |
  | H2D | 4 | 1000 | 25,000 | 10,059 | 8,450 |
  | D2H | 1 | 1000 | 25,000 | 199,124 | 427 |
  | D2H | 4 | 1000 | 25,000 | 199,072 | 427 |

- **Proposed addition (experiment callout plus table, tag Measured, simulator):**
  - Lessons: (a) small transfers are dominated by fixed cost even in the simulator (about 12 cycles per wavelet at 125 wavelets, about 1 cycle per wavelet at 25k). (b) More channels speed up H2D (2.5× with 4). (c) D2H is about 8× slower per wavelet here and did not scale with channels. D2H sends a {data, ctrl} pair per wavelet, round-robin through a switch (wse3/memcpy.csl lines 19–24, 345–347), which plausibly explains part of this. State it as a hypothesis.
  - Contrast with hardware: 7 Gb/s ÷ 32 bits ÷ 850 MHz ≈ 0.26 wavelets per PE cycle per channel (Derived). The simulator's roughly 1 wavelet per cycle therefore overstates real host bandwidth by about 4×, and the 200 µs TCP cost is not modelled at all.
  - Commands: `bash commands_wse3.sh`. For variants, recompile with `--params=...,pe_length:1000 --channels=4` and run `run.py ... -k=1000 --channels=4 [--d2h]`.

### D5 [major] Mechanism for "wrong stream order hangs" (gemv-09): back-pressure plus serialised commands
- **What is missing:** The chapter quotes the hang but does not explain it. It also says a streaming H2D "completes when the host has injected its wavelets" without adding that injection itself stalls when the device does not consume them.
- **Why it matters:** This is the deepest "how it behaves" fact about streaming mode. It connects the program-02 race (completion is too early) and the gemv-09 hang (completion never happens) to one model: small hardware queues plus back-pressure.
- **Source:** `tutorials/gemv-09-streaming/pe_program.csl` (memcpy_recv_b forwards b onto recv_west_color, which is consumed only by `reduce()`; reduce is activated only after all x has arrived in `recv_x`) and README. `memcpy/wse3/memcpy.csl` lines 372–389 (streaming path C23 → IQ0 → UT0 → OQ0 → user WTT queue), and line 429 ("When UT0 is done, all data in IQ0 is drained, but OQ0 may not be empty").
- **Proposed addition:**
  - A step diagram. If b streams first, the b wavelets fill column 0's queues because reduce is not running. Back-pressure travels up C23 to the demux and the LVDS. The b H2D cannot finish, so the x command (next on color 22) never starts, and that is a deadlock.
  - A sentence uniting the two cases: "A streaming H2D finishes when memcpy's microthread has handed the last wavelet to your queue: not before the device has room, and not after your task has run."
  - Optional: let the existing timeline widget take a third toggle, "stream b before x", which shows a stall bar.

### D6 [major] Explain the 95-of-100 number quantitatively using queue depths
- **What is missing:** The chapter says 95 values were seen but not why the gap is about 5.
- **Why it matters:** It turns the anecdote into a mechanism, and the hardware queue depths are a fact readers will reuse.
- **Source:** `memcpy/wse3/memcpy.csl` lines 205–211 and `memcpyh2d.csl` lines 174–180: "Queues 0,1: input depth 6; 2,3: input depth 4; 4–7: input depth 2; output 0,1: depth 2; 2,3: depth 6; 4,5: depth 2". Program 02 binds its data task to input queue 2 (`course/programs/02-wavelet-tasks/pe_program.csl`). The streaming path ends in OQ0 → user IQ2 (memcpy.csl lines 372–389).
- **Proposed addition:**
  - A small table of WSE-3 queue depths.
  - A sentence: when the H2D reports done, up to 2 wavelets can sit in OQ0 and up to 4 in IQ2, so about 5–6 values can still be pending. That is consistent with reading the sum after 95. Tag Derived, and say it is consistent with the measurement rather than proven.

### D7 [major] What a command is: the RPC wire format, and why every PE must unblock
- **What is missing:** The chapter says commands are wavelets on color 22 decoded by control tasks. It does not say what they contain, that they reach every PE in the rectangle (including PEs outside the copy region), or how PEs that are not involved get released.
- **Why it matters:** It explains "forget on one PE → hang" mechanically, and shows that a 1-PE copy still touches every PE.
- **Source:** `memcpy/wse3/memcpy.csl`:
  - Lines 13–24: C22 broadcasts the command to a row of PEs. The PE decodes (px, py, w, h, addr) and sets the filter (H2D) or switch (D2H).
  - Lines 143–156: the H2D parameter list includes `memcpy_optype {DENSE, ROW_BCAST, COL_BCAST, STRIDE}`, row/col stride and is_half.
  - Lines 319–343 and 510–519: inactive rows unblock C22 immediately. Inactive PEs in active rows forward the data and wait for the teardown (TD) wavelet. D2H "routing PEs" are the ROI extended east.
  - Lines 672–705: the RPC format is a count of wavelets, then params, then the function ID, all as u32.
- **Proposed addition:** A paragraph plus a small "anatomy of a command" table: `PUSH color, px, py, w, h, addr, pe_length → MEMCPYH2D ctrl`, and the RPC frame. Add a row-of-PEs diagram coloured by "active PE / forwarding PE / inactive row", showing that the TD wavelet is what frees C22.

### D8 [major] ROW_MAJOR vs COL_MAJOR for multi-PE copies
- **What is missing:** The chapter uses `MemcpyOrder.ROW_MAJOR` without explaining it. The research report flags COL_MAJOR semantics as unexplained.
- **Why it matters:** Getting the host layout wrong silently scrambles data across PEs.
- **Source:** `benchmarks/bandwidth-test/run.py`, `hwl_2_oned_colmajor` (loops l outer, w, h inner, for tensor A[h][w][l]). `benchmarks/row-col-broadcast/run.py` (`B.T.ravel()` for COL_MAJOR, `B.ravel()` for ROW_MAJOR).
- **Proposed addition:**
  - A table and a 2×2-PE, 3-element picture. ROW_MAJOR means the host array is A[h][w][l] in C order, so each PE's block is contiguous. COL_MAJOR means it is A[l][w][h], equivalent to `A_hwl.T.ravel()` (Fortran order), so element j of every PE is contiguous.
  - Show both numpy one-liners.

### D9 [minor] Buffer columns (`--width-west-buf`/`--width-east-buf`) for overlapping I/O with compute
- **What is missing:** These flags are not mentioned at all.
- **Source:** `benchmarks/bandwidth-test/run.py` docstring (2): back-pressure from a busy core stalls the I/O channel. "Each PE in the buffer has 46KB fifo … needs (pe_length*width)*4/46K columns". The flags also enter the offset formula (D2).
- **Proposed addition:**
  - A paragraph with a worked example: 1000 f32 per PE × 100 PEs wide = 400 KB, and 400 KB ÷ 46 KB ≈ 9 buffer columns (Derived).
  - Note that the user offset grows by width_west_buf.

### D10 [minor] Streaming-mode device side: how the color IDs get there, and limits
- **What is missing:** The chapter does not show how the streaming color reaches the device (a layout param → `get_params(.MEMCPYH2D_1 = …)` → `sys_mod.MEMCPYH2D_1`, with the host reading the ID from `out/out.json`). It also omits that WSE-3 binds the data task to a user input queue, that there are at most 4 H2D and 4 D2H streaming colors, that streaming D2H uses a `fabout_dsd` on `MEMCPYD2H_1`, and that users must not route memcpy colors.
- **Source:** `memcpy/memcpy.csl` and `get_params.csl` (MEMCPYH2D_1..4, MEMCPYD2H_1..4, LAUNCH). `memcpyh2d.csl` line 140: copy vs streaming is decided by the color field (`is_streaming == !(c >= 24)`). gemv-09 `layout.csl`, `pe_program.csl` lines 26–52 and 83–88, and `run.py` lines 28–30 and 63–74. Course program 02 `run.py` and `pe_program.csl`.
- **Proposed addition:** A three-column "host / layout / PE program" snippet strip showing the color ID flowing through, plus a one-line note on the 4+4 limit.

### D11 [minor] 16-bit transfers do not save bandwidth
- **What is missing:** `MEMCPY_16BIT` is not explained.
- **Source:** `tutorials/topic-01-arrays-and-pointers/run.py` and `topic-02-libraries/run.py`: the host array is u32 and `memcpy_view(..., np.int16)` "remove[s] upper 16-bit of each u32". memcpy.csl H2D param "is_half (mov16)". Wavelets are 32-bit.
- **Proposed addition:** One sentence and a snippet. A 16-bit value still occupies a full 32-bit wavelet, so halving precision does not halve transfer time (Derived). Use `sdk_utils.memcpy_view`.

### D12 [minor] Full host API surface: call, stride and broadcast variants, read_symbol
- **What is missing:** The chapter shows only 6 calls. `call(name, u32 array)` (used by bandwidth-test for the RPCs `f_sync`, `f_tic` and `f_toc`), `memcpy_h2d_stride(…, row_stride, col_stride)` (2 extra int args), `read_symbol`, `dump_core`, `send`/`receive` and `is_task_done` all exist.
- **Source:** SdkRuntime introspection (`cs_python -c "from cerebras.sdk.runtime.sdkruntimepybind import SdkRuntime; help(SdkRuntime)"`). Research report Ch.11 paragraph.
- **Proposed addition:** A compact reference table: method, signature, what it does, example in the SDK.

### D13 [minor] Worked example for rowbcast/colbcast, and WSE-3 queue reservation reasons
- **rowbcast/colbcast:** Use the README's example. A column [1,2,3,4] sent to a 3×4 region needs 12 elements with `memcpy_h2d` and 4 with `memcpy_h2d_rowbcast`, saving 3× host bandwidth. H2D only. It is implemented as `memcpy_optype ROW_BCAST/COL_BCAST` in the command. Source: `benchmarks/row-col-broadcast/README.rst` and `run.py` lines 77–99.
- **Queue reservation:** Explain *why* queue 1 is reserved on WSE-3. C22 binds to input queue 1 ("cmd color (C22) needs to bind an input queue 1 for wse3"), and IQ0/OQ0 carry H2D/D2H data through microthread UT0. Source: `memcpy/wse3/memcpy.csl` lines 40–46 and 742; `memcpy/memcpy.csl` header.
- **Proposed addition:** Turn the "Queues" row of the reserved-resources table into "queue 0: data via UT0; queue 1 (WSE-3): command color 22".
- **Note for the fixer:** Some header comments in `wse3/memcpy.csl` give stale color numbers ("21: RXCOMMAND, 22: H2D, 23: D2H"). Trust `sys_params.csl`, which matches the chapter's table (21 D2H, 22 command, 23 H2D).

### D14 [minor] Consistency of the "16 channels ≈ 14 GB/s" ceiling
- **What is missing:** 16 × 7 Gb/s = 112 Gb/s, which is more than a single 100 GbE link. The SDK text says "100Gbps ethernets" (plural), and CS-3 is reported as 12×100 GbE (analyst/forum source).
- **Proposed addition:** A footnote saying the 14 GB/s figure assumes the host side can supply more than one 100 GbE link. Tag Derived. Source: research report Ch.8. wse_hardware.md §7 Gaps.

## Out of scope for this chapter (new-chapter or cross-chapter ideas)
- **Ch04/Ch05:** The WSE-3 queue-depth table (D6) and the counter-filter mechanism (D1) are general fabric features. Ch04 could reuse the filter widget, and Ch05 the queue depths for back-pressure.
- **Ch12 (Lab 3):** Add the bandwidth-test experiment as an optional lab step: sweep pe_length and channels, and plot cycles per wavelet. Ch12 already separates host transfer from kernel time by subtraction, and could cite D4's per-wavelet costs.
- **Ch09:** The RPC frame (D7) and `call` vs `launch` belong partly in the toolchain chapter. SdkLayout streams (`create_input_stream`, memcpy_required=False), from research report Ch.11 and sdklayout-01..05, are an alternative host path not covered anywhere. That could be a short section in ch09 or an appendix.
- **Ch08:** Contrast the SDK host path (about 0.26 wavelets per cycle per channel) with the WSE-3T's 2.4 Tb/s per wafer and MemoryX/SwarmX weight streaming. D3's calculator could be reused there with system-level numbers.
