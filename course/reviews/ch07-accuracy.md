# ch07 · accuracy review

Summary: Chapter 7 is accurate on almost everything that matters. The bandwidth quote, the 14 GB/s and 3 s derivations, the reserved colors 20–23, the local and control task IDs, the queue rule, the gemv-09 quote, the unblock_cmd_stream quote, the 3 west + 2 east halo ELFs (I re-checked these by compiling program 01 with `--channels 1`), and the program-02 race numbers (I recomputed 30.818176 as the float32 running sum after 95 values and 26.137941 after 100) all match the SDK files and the course programs. There are no critical errors. The fixes needed are one wrong piece of advice about which local task IDs are free (21 is used by memcpy), a few numbers with no provenance tag, a slight misreading of the CS-2 rectangle limit, two small overclaims (rowbcast mechanism, streaming "no launch"), and some small fidelity problems in the code excerpt and the quiz.

## Findings

### A1 [major] Suggested local-task range 9–23 includes an ID memcpy uses
Location: "memcpy also claims a fixed set of on-chip resources" table, row "Local tasks", column "Consequence for you".
Problem: The table recommends "use e.g. 9–23 for your local tasks". memcpy's D2H module binds local task ID 21 (it takes the ID from the D2H data color, 21) on both architectures. Also, on WSE-3, local task IDs only start at 8. On WSE-2, IDs 0–23 are also the data-task IDs of the colors, so 22 and 23 collide with memcpy's colors there.
Evidence: SIF `csl-libs/memcpy/wse3/memcpyd2h.csl:161` and `wse2/memcpyd2h.csl:119`: `const LOCAL_MEMCPYD2H_DATA: local_task_id = @get_local_task_id(@get_int(MEMCPYD2H_DATA));` with `sys_params.csl:46` `param MEMCPYD2H_DATA : color = @get_color(21);`. Notes `csl_programming.md:125` (topic-05 README): "local tasks ... on WSE-3 can be associated with any task ID from 8 to 30". The course programs use 9–13 (`programs/03-row-reduce/pe_program.csl:21`, `04-heat-stencil/pe_program.csl:49-52`).
Concrete fix: Replace the cell text `use e.g. 9–23 for your local tasks` with `use e.g. 8–19 for your local tasks (WSE-3 local IDs start at 8; memcpy also uses 21 for D2H; the course uses 9–13)`.

### A2 [minor] Several numbers carry no provenance tag
Location: "The narrow door" stat tiles and the paragraph after them.
Problem: The brief requires every number to carry a tag. The "≤ 16 channels" and "~200 µs TCP overhead" tiles have none, even though their two neighbouring tiles do. "44 GB of SRAM" and "21 PB/s" in the paragraph are also untagged; they are vendor figures.
Evidence: bandwidth-test `README.rst:26`: "``--channels=<int>`` specifies the number of I/O channels, no bigger than 16." `bandwidth-test/run.py:5-7`: "...the overhead of TCP is about 200 us". Notes `gpu_and_comparison.md:70`: "44 GB of on-wafer SRAM (vendor figure: 21 PB/s ...)".
Concrete fix: Add `<span class="tag sdk">SDK 2.10.1</span>` to the "≤ 16" and "~200 µs" tiles, in the same position the "100 GbE" and "~7 Gb/s" tiles use. In the paragraph, change `filling 44 GB of SRAM` to `filling 44 GB <span class="tag vendor">Vendor</span> of SRAM` and `read at 21 PB/s.` to `read at 21 PB/s <span class="tag vendor">Vendor</span>.`

### A3 [minor] The 14 GB/s figure assumes channels scale linearly, and it exceeds one 100 GbE link
Location: "The narrow door" paragraph, "Sixteen channels give roughly 14 GB/s".
Problem: The SDK gives a per-channel figure and a 16-channel cap. It never says that 16 channels deliver 16× the bandwidth. Also, 112 Gb/s is more than one 100 GbE link can carry (12.5 GB/s). The source says "ethernets", plural, so this is only possible across several links. The derived number is an upper bound and should be worded as one.
Evidence: `bandwidth-test/run.py:5`: "The host connects the device via 100Gbps ethernets. The data is distributed from/to couple of I/O channels." Report line 114 calls it "roughly 112 Gb/s, or 14 GB/s ... [Derived]".
Concrete fix: Replace `Sixteen channels give roughly 14 GB/s, so` with `Sixteen channels give at most about 14 GB/s, if channels scale linearly (more than one 100 GbE link can carry), so`.

### A4 [minor] CS-2 rectangle limit stated as an exact size rather than a maximum
Location: "What --memcpy adds" paragraph: "On a real CS-2 the user rectangle must be 7 columns narrower and 2 rows shorter than the 750 × 994 fabric".
Problem: The SDK states an upper bound on the rectangle, not an exact size.
Evidence: `benchmarks/single-tile-matvec/README.rst:35-39`: "the width must be no bigger than 7 less than the x-dimension of the fabric, and the height must be no bigger than 2 less than the y-dimension of the fabric. Additionally, if you are running on a real CS-2, ``fabric-dims`` must be ``750,994``."
Concrete fix: Replace `the user rectangle must be 7 columns narrower and 2 rows shorter than the 750 × 994 fabric` with `--fabric-dims must be 750,994 and the user rectangle can be at most 7 columns narrower and 2 rows shorter than that, i.e. at most 743 × 992`.

### A5 [minor] "3 west and 2 east" is right, but the measurement source is not stated
Location: same section, "For our programs with --channels 1 the compiler emitted 3 west and 2 east columns [Measured from out/]".
Problem: The research notes recorded this on the SDK tutorial gemv-01, not on the course programs. I re-ran program 01's compile line and got the same result: `out/west/bin/out_{0,1,2}_0.elf` and `out/east/bin/out_{0,1}_0.elf`. The claim holds. The fix makes it say exactly what was observed: ELF files.
Evidence: Notes `csl_programming.md:115`: "The 3 west and 2 east ELFs were observed only for `--channels 1`." My local compile of `programs/01-saxpy` with its `commands.sh` flags produced 3 west and 2 east ELFs.
Concrete fix: Replace `the compiler emitted 3 west and 2 east columns` with `the compiler emitted 3 west and 2 east halo programs (out/west/bin/*.elf, out/east/bin/*.elf)`. Keep the Measured tag. The figure places these programs at x = 1–3 and x = 5–6, but the exact placement is not documented. Add to the figcaption: `Exact halo positions are schematic.`

### A6 [minor] The code excerpt is labelled with a file path but is not verbatim
Location: "Six calls on the host", code block titled `course/programs/01-saxpy/run.py`.
Problem: The excerpt calls `rt.memcpy_d2h(out, ...)` but never defines `out`. The real file has `out = np.zeros(N, dtype=np.float32)` on the line before. The comments `# cmaddr=None → simulator`, `# exported symbol IDs` and `# RPC with an f32 argument` are not in the file. A reader who copies the snippet gets a NameError.
Evidence: `course/programs/01-saxpy/run.py:21-23`: `rt.launch('saxpy', a, nonblock=False)` / `out = np.zeros(N, dtype=np.float32)` / `rt.memcpy_d2h(out, ys, 0, 0, 1, 1, N, **kw)`.
Concrete fix: Insert the line `out = np.zeros(N, dtype=np.float32)` between the `rt.launch(...)` line and the `rt.memcpy_d2h(...)` line. Change the block title to `course/programs/01-saxpy/run.py (excerpt, comments added)`.

### A7 [minor] "No launch needed" conflicts with program 02, which does launch
Location: "Copy mode vs streaming mode", Streaming card: "No launch needed — arrival starts the computation. Program 02."
Problem: The general statement is from gemv-09 and is correct. But the chapter cites Program 02 as the example, and Program 02 calls `rt.launch('wait_done')`, which is the fix the chapter itself presents next. As written, the card contradicts the timeline section.
Evidence: gemv-09 `README.rst`: "The host code no longer includes an explicit kernel launch." `programs/02-wavelet-tasks/run.py:18`: `rt.launch('wait_done', nonblock=False)   # barrier`.
Concrete fix: Replace `No launch needed — arrival starts the computation. Program 02.` with `No launch is needed to start: arrival starts the computation (gemv-09). Program 02, which still launches a wait_done barrier before reading results (see below).`

### A8 [minor] Streaming H2D colors are left out of the resource table
Location: resource table, row "Colors".
Problem: The table lists only 20–23 as memcpy colors. Streaming mode also uses user-chosen MEMCPYH2D_DATA_n / MEMCPYD2H_DATA_n colors, and those come out of the 0–19 range. Program 02 gives color 0 to memcpy (`--params=MEMCPYH2D_DATA_1_ID:0`). This is why the SDK's 25-pt-stencil README says "SdkRuntime reserves 6 colors". The research report says "minus 4–6 for runtime".
Evidence: `programs/02-wavelet-tasks/commands.sh`: `--params=N:100 --params=MEMCPYH2D_DATA_1_ID:0`. `benchmarks/25-pt-stencil/README.rst:17`: "``SdkRuntime`` reserves 6 colors". Report line 309: "only 24 colors, minus 4–6 for runtime".
Concrete fix: Change the "Consequence for you" cell to `use colors 0–19; each streaming H2D/D2H channel also takes one of these (program 02 gives color 0 to MEMCPYH2D_DATA_1)`.

### A9 [minor] The rowbcast/colbcast mechanism is overclaimed
Location: "Ordering matters too": "memcpy_h2d_rowbcast/colbcast send one copy and let the fabric replicate it".
Problem: The SDK says only that the host sends one column or row instead of the replicated tensor. Where the replication happens is not stated.
Evidence: `benchmarks/row-col-broadcast/README.rst:16-24`: "This operation wastes host bandwidth by 3x. Now the user can use the new API, ``memcpy_h2d_rowbcast()``, to stream 4 elements only. ... The new broadcasting scheme only supports H2D, not D2H."
Concrete fix: Replace `send one copy and let the fabric replicate it, saving host bandwidth (host→device only).` with `let the host send one column (or row) of data instead of a replicated tensor, saving host bandwidth (3× in the SDK example; host→device only) <span class="tag sdk">SDK 2.10.1</span>.`

### A10 [minor] Quiz question says "colors ≤ 4", but the programs use 0–3, and the answer does not explain the bound
Location: Check yourself, question 2.
Problem: The course programs use colors 0–3 (program 04 uses `@get_color(0..3)`; program 02 streams on color 0). The real constraint is colors below 20. The question's "≤ 4" is both inaccurate and not the rule.
Evidence: `programs/04-heat-stencil/layout.csl:10-13` (colors 0–3). Sys_params: `MEMCPYD2H_DATA` 21, `RXCOMMAND` 22, `MEMCPYH2D_DATA` 23, `SYS_RXCTX` 20.
Concrete fix: Change the summary to `Why does every course program use queues ≥ 2 and colors below 20 (in practice 0–3)?`. Change the answer to `memcpy owns colors 20–23 on both architectures, and input/output queues 0 and 1 on WSE-3 (input queue 1 carries the command stream). Everything below those is free; the course simply starts at color 0 and queue 2.`

### A11 [minor] The race explanation is an inference but reads as a documented SDK fact
Location: "What actually happened": "A streaming memcpy_h2d completes when the host has injected its wavelets, not when the device has processed them".
Problem: No SDK document found states this completion semantics. It is inferred from the measured partial sum, which strongly supports it. The chapter should label it as an inference.
Evidence: No match for any such statement in the bandwidth-test, gemv-09 or row-col-broadcast READMEs or in the research notes. The measurement itself is confirmed: the float32 cumulative sum of `default_rng(1).uniform(-10,10,100)` at k = 95 is 30.818176, and at k = 100 it is 26.137941 (expected_output.txt).
Concrete fix: Replace `A streaming memcpy_h2d completes when` with `The evidence shows that a streaming memcpy_h2d completes when`, and append `<span class="tag derived">Derived</span>` after `raced the last few data tasks.`

## Not verifiable
- The exact physical placement of the halo programs within the 8 × 3 fabric (figure shows x = 1–3 west, x = 5–6 east, and x = 0 and x = 7 plain). The ELF counts are confirmed; the positions are not documented. The direction is supported: SIF `wse3/sys.csl:105` routes the command color `rx WEST`, and `wse3/memcpy.csl:594-595` says the mux is "to the EAST of the core PEs".
- "Forget it on even one PE and the host hangs on its next call." This follows from serialized commands (`memcpy.csl:94-97`), but the per-PE hang was not tested.
- The widget output text "validated at N=100 and N=500" and "count read later shows 100" for the no-barrier run. Only the N = 100 barrier output is in `expected_output.txt`.
- Whether `100 GbE` applies to CS-3 as well as CS-2. The SDK text is CS-2-era; CS-3 "12x100GbE" comes only from a forum post (notes `wse_hardware.md:170`).
