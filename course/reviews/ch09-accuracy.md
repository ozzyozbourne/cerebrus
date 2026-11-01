# ch09 · accuracy review

Summary: Chapter 9 is mostly accurate. I checked it against `cslc`/`cslc-driver --help`, the memcpy library in the SIF, the tutorials, the research notes, and fresh compile+simulate runs of program 01 (WSE-3 and WSE-2) and program 03 in `/home/user/cerebras-sdk/tmp/rev09/`. The code tour matches `course/programs/01-saxpy/` line for line. The flag table, the quotes from the SDK READMEs, the memcpy reservations, the SingularityCE version, the capability workaround and the setup.sh path are all correct. There is one major error: the caption says the simulator ELFs are reused unchanged on hardware, and it carries a "Measured" tag for that claim. The minor findings are about the simulator's idle/stop window and how repeatable cycle counts are (one of my runs got 8202 cycles, not 7740), a misplaced file in the pipeline figure, imprecise wording in the quiz and the language list, and numbers that have no provenance tag.

## Findings

### A1 [major] "Same ELFs" on hardware is wrong, and "Measured" is not justified
- Location: "From source to simulation" figure, `<figcaption>` ("Two commands. Same host script, same ELFs: on hardware you pass `--cmaddr IP:port` instead of using the simulator" with tags SDK 2.10.1 + Measured).
- Problem: The ELFs are compiled for `--fabric-dims=8,3`. A real system needs a compile against its own fabric size, so the same ELFs do not run on hardware. Only the host script carries over. Nothing in this course was run on hardware, so the "Measured" tag cannot support a hardware claim.
- Evidence: `cslc-driver --help`: "--fabric-dims ... representing the fabric width and the fabric height". `examples/benchmarks/single-tile-matvec/README.rst`: "To compile and run ... on an actual CS-2, use: `./sweep.py --dims 750,994 --cmaddr <CS IP ADDR>`". Its `sweep.py` line 33 is `args.append(f"--fabric-dims={width+7},{height+2}")`, so the compile changes for hardware. The research notes record no hardware runs.
- Fix: Replace the figcaption content with:
  `<b>Two commands.</b> On a real CS system the host script is unchanged apart from passing <code>--cmaddr IP:port</code> (<code>cmaddr=None</code> selects the simulator), but you recompile with <code>--fabric-dims</code> set to that system's fabric <span class="tag sdk">SDK 2.10.1</span>. The cycle and file details shown are from our simulator runs <span class="tag measured">Measured</span>.`

### A2 [minor] The 50-cycle stop rule and the "at most 2 cycles" repeatability claim are stated too strongly
- Location: Pipeline SVG text "The simulator stops once nothing has moved for 50 cycles." Also the paragraph after the Debugging table: "(cycle totals varied by at most 2 cycles across our reruns)".
- Problem: The idle window is not always 50 cycles. My first WSE-3 run of program 01 (compile then simulate, in a fresh directory) stopped after 512 idle cycles and reported 8202 cycles. All later runs reported 7740 cycles with a 50-cycle window. The cycle total includes the idle tail, and the tail apparently depends on host timing. So "at most 2 cycles" holds for warm reruns only. The 50-cycle text is also untagged.
- Evidence: First run, `sim.log`: `@8202 No data movement in the last 512 cycles; stopping.` and `sim_stats.json` `"cycle_count": 8202, "idle_ce_cycles": 512`. Four later runs: `@7740 No data movement in the last 50 cycles; stopping.` WSE-2 run: `@6826 No data movement in the last 50 cycles` (the chapter says 6,825, which is within ±2). `simconfig.json` contains `"sunsetCount": 50`. Notes, csl_programming.md line 409: "The simulator stops after 50 idle cycles once the host stops."
- Fix:
  - SVG line 118: replace `The simulator stops once nothing has moved for 50 cycles.` with `The simulator stops after an idle window (50 cycles in almost all our runs) once the host has stopped.`
  - Paragraph: replace `(cycle totals varied by at most 2 cycles across our reruns)` with `(warm reruns varied by at most 2 cycles; one cold first run added a ~460-cycle idle tail)` and add `<span class="tag measured">Measured</span>` after the parenthesis.

### A3 [minor] The pipeline figure shows `out_rpc.json` in the wrong directory
- Location: Pipeline SVG, the `out/` box, text `out.json  out_rpc.json` (line 107).
- Problem: `out_rpc.json` is in `out/bin/`, not in `out/`. The code tour itself says "IDs come from out/bin/out_rpc.json", so the figure and the tour disagree. The figure also leaves out `generated/`.
- Evidence: After compiling, `ls out` gives `bin east generated out.json west`, and `ls out/bin` gives `out_0_0.elf out_rpc.json`. The notes agree: "`out/bin/out_rpc.json`; ... `out/generated/{default,coord,MEMCPY_XY_ROUTES}.elf`".
- Fix: Change the three text lines in the `out/` box to `bin/out_X_Y.elf  bin/out_rpc.json`, `west/ east/ (memcpy)`, and `out.json  generated/`.

### A4 [minor] The queue reservation should say it applies to WSE-3, to match ch07 and ch05
- Location: Code tour, pe_program.csl note on `const sys_mod = ...`: "It reserves colors 20–23, some task IDs and queues 0–1."
- Problem: Chapters 05 and 07 say queues 0–1 belong to memcpy "on WSE-3". The library comment ties the queue 1 reservation to SDR (WSE-3). The tour program builds for both chips, so the note should say which chip the queue rule covers.
- Evidence: `csl-libs/memcpy/memcpy.csl`: "memcpy reserves queue 1 on SDR". `sys_params.csl`: colors 20 (SYS_RXCTX), 21, 22 (RXCOMMAND), 23; local task IDs 24, 27, 28, 30; control task IDs 33–37 and 40; `input_queue_id = 0`, `input_queue_cmd_id = 1`. 07-host-io.html: "memcpy owns queues 0–1 on WSE-3 and colors 20–23".
- Fix: Replace the note text with `The device side of the host-I/O runtime. It reserves colors 20–23, task IDs 24–30 and 33–40, and (on WSE-3) queues 0–1.`

### A5 [minor] The quiz 1 answer misdescribes what device code does with the color
- Location: Check yourself, Q1 answer: "layout.csl, through @set_color_config on both PEs. Device code only sees queues bound to that color."
- Problem: The routing is set in the layout, but in the course's own programs the device code binds a queue to the color itself, with `@initialize_queue`. It does not just "see" queues that something else bound.
- Evidence: `programs/03-row-reduce/layout.csl:28,30` uses `@set_color_config(...)`. `programs/03-row-reduce/pe_program.csl:38-39` has `@initialize_queue(oq, ... .{ .color = send_color } ...)` and `@initialize_queue(iq, .{ .color = recv_color })`.
- Fix: Replace the answer with `<code>layout.csl</code>, through <code>@set_color_config</code> on both PEs (tx EAST on (3,0), rx WEST on (4,0)). The device code receives the color as a param and binds its queues to it with <code>@initialize_queue</code>.`

### A6 [minor] The brace rule for if/else is imprecise
- Location: "Ordinary parts" list: "`if`/`else` (with braces when used as statements)".
- Problem: A statement-form `if` without an `else` compiles without braces, and the course's program 02 uses that form. Braces are only required when the statement-form `if` has an `else`.
- Evidence: `programs/02-wavelet-tasks/pe_program.csl` contains `if (v > stats[2]) stats[2] = v;` and the program compiles and passes. My test inserted `if (a > 0.0) t = 1; else t = 2;` into the program 01 kernel, and it gave `error: Unexpected character at this location`. ch11 states the same rule: "if (a) stmt; else if (b) stmt; else stmt; without braces is a compile error".
- Fix: Replace `<code>if</code>/<code>else</code> (with braces when used as statements)` with `<code>if</code>/<code>else</code> (a statement <code>if</code> with an <code>else</code> needs braces)`.

### A7 [minor] Several numbers have no provenance tag
- Location:
  - Debugging/flag table, `--channels`: "(up to 16)".
  - Pipeline SVG: "One SAXPY run takes a few seconds of wall time."
  - Code tour notes, which are plain JS strings and cannot hold tag spans: "48 KB", "colors 20–23", "WSE-3 (7,740 cycles) and WSE-2 (6,825 cycles)".
  - Setup section: "3.4 GB" sits under the paragraph's Measured tag, so it is covered.
- Problem: The brief says every number should carry a tag.
- Evidence: Each value checks out. The benchmarks' README.rst says "no bigger than 16". My timing of `cs_python run.py` was 2.9 s. 48 KB is in wse_hardware.md line 8. The colors are in `sys_params.csl`. My reruns gave 7740 (WSE-3) and 6826 (WSE-2).
- Fix:
  - Flag table: change `(up to 16)` to `(up to 16 <span class="tag sdk">SDK 2.10.1</span>)`.
  - Under the tour widget, after `<div class="readout" id="tour-note">…</div>`, add `<p class="hint">Numbers in the notes: 48 KB per PE <span class="tag vendor">Vendor</span>; memcpy colors, task IDs and queues <span class="tag sdk">SDK 2.10.1</span>; cycle counts <span class="tag measured">Measured</span>.</p>`.
  - Move the wall-time sentence out of the SVG and into the figcaption as `One SAXPY simulation takes about 3 s of wall time <span class="tag measured">Measured</span>.`, or keep it in the SVG and add "(measured)" to the text.

### A8 [minor] The SIF size rounds to 3.5 GB, not 3.4 GB
- Location: Setting up the SDK: "a 3.4 GB Singularity image (.sif)".
- Problem: The SIF is 3,455,725,568 bytes, which is 3.46 GB (3.2 GiB). The 3.4 GB figure is the size of the tarball (3,429,958,480 bytes), not the image.
- Evidence: `ls -la` on `sdk-cbcore-2.10.1-...sif` gives `3455725568`. `setup.sh` has `EXPECTED_SIZE=3429958480` for the archive.
- Fix: Replace `a 3.4 GB Singularity image` with `a 3.5 GB Singularity image`.

### A9 [minor] "pe_program.csl runs on every PE" understates the SDK's own description
- Location: The three-files SVG, middle box.
- Problem: The figure quotes gemv-01, but gemv-01 says there are one or more device files. Not every PE has to run the same file. Program 01 also has a 1×1 rectangle, so it has only one PE.
- Evidence: gemv-01 README: "one or more of which define the programs running on the individual PEs."
- Fix: Change the SVG text `runs <tspan font-weight="700">on every PE</tspan>` to `runs <tspan font-weight="700">on each PE</tspan> (1+ files)`.

## Not verifiable
- "We got this wrong once in program 02" (the mutability flag) and the claim that every bug was a resource bug. These are the course's own history. I did confirm the mechanism: changing `var x_ptr` to `const` gives `error: exported symbol mutability mismatch ... note: expected name to be mutable`.
- That 7,740 / 6,825 cycles were the values when the course was written. I reproduce 7740 and 6826 now.
- The quoted capability error text. It matches `.claude/skills/cerebras-sdk/SKILL.md` line 42, but I did not re-trigger it.
- How csdb and `<debug>` behave beyond their help text and the notes. I did not run them end to end.
- Whether `rt.launch(..., nonblock=False)` blocks specifically until `unblock_cmd_stream()`. The SDK docs are not available locally. This is consistent with ch07 and with the program behaving as described.

Verified OK:
- Every cslc flag in the table: `--arch` defaults to wse2, and `--fp16-format` accepts f16/cb16/bf16.
- `--fabric-dims=8,3` and `--fabric-offsets=4,1`.
- The sim_stats keys and values: fabric_x 8, fabric_y 3, hwtile_count 10, "Stopped due to idleness".
- FYN/SDR as the architecture names.
- The gemv-01 and topic-13 quotes, and that `<debug>` "requires a program to complete".
- Null pointers and pointer-only runtime arguments, per topic-01.
- The `for (@range(...))` and `while (...) : (...)` syntax.
- Colors 20–23, color 22 as the command color, and queues 0–1.
- One ELF per unique param set: program 03 has 8 PEs and produces 4 ELFs.
- SingularityCE 4.1.1, `SINGULARITY_DROP_CAPS` in env.sh, and the setup.sh path.
