# ch09 · depth review

Summary: Ch09 gives a correct overview of the three files, a SAXPY tour, the two commands and a list of tool names. It is too thin for a learner who has to write and debug CSL on their own. Four gaps matter most:
1. **The compile model.** The chapter does not explain what makes a "unique PE program". Measured: both params and routes do. It also does not explain what the ELF names mean, or what the cslc wrapper checks and generates before the compiler runs.
2. **SdkLayout.** The whole Python layout API is missing, although the SDK has five tutorials on it.
3. **Debugging.** There is no symptom-to-cause workflow. The chapter does not show what the common mistakes actually print, and several of them print something misleading.
4. **The language.** About half of the language features the SDK examples use are absent: structs, enums/switch, comptime asserts, module instancing, param types, `@get_rectangle`, `export var`.

I ran nine small experiments on SDK 2.10.1 (dir `/home/user/cerebras-sdk/tmp/ch09-depth/`, since deleted) so that the proposals can quote real outputs. Each one is tagged `Measured` below. Unless noted, all were WSE-3, `--memcpy --channels 1`, on 2026-11-01.

Overlap with the existing reviews: pedagogy P1–P5 and P14 and visuals P5 touch some of the same areas. This review assumes they are applied, and it adds the depth they lack: the real rules, real messages and real numbers.

## Gaps and additions (prioritised)

### D1 [critical] The compile model: what becomes a separate PE program, what the ELF names mean, and what the wrapper does

**What is missing.**
- The chapter says "one ELF per unique param set" and draws `bin/out_X_Y.elf`. Both are incomplete.
- It does not say that routes also split PE programs, or that memcpy's own per-column params force at least three programs for any rectangle three or more columns wide.
- It does not say what the ELF file names encode, or that one ELF can cover a whole rectangle of identical PEs.
- It does not say that `cslc` is a Python wrapper that generates the memcpy halo and checks the fabric before `cslc-driver` runs, or that linking (`ld.lld`) is a separate stage with its own errors.

**Why it matters.**
- This is "the compile model and its internals" that the chapter promises.
- Without it, the learner cannot predict compile time or read `out/`.
- The SDK's advice in gemv-07 ("use `<layout>` coordinates instead of params to reduce unique programs") then looks like it fails: gemv-07 itself still compiles to 4 ELFs for 4 PEs. Routes are why.

**Source.**
- `cslc --help`: "Frontend for cslc-driver. Creates a directory and then calls cslc-driver …".
- The cslc wrapper's own error messages (below).
- `cs_readelf --help` (`-r/--rect`: "what rectangular PE regions are covered by data contained in the target ELF").
- gemv-07 README.
- `LIB/memcpy/get_params.csl` (`first_pe`/`last_pe` from the column).
- Experiments, all Measured:

| Program (WSE-3) | PEs | ELFs in `out/bin/` | Why |
|---|---|---|---|
| SAXPY pe_program on a 6×2 rectangle, identical params | 12 | 3 (`out_0_0`, `out_1_0`, `out_2_0`) | memcpy params differ for first, middle and last column only |
| same, plus color 3 routed `RAMP→EAST` on row 0 and `WEST→RAMP` on row 1 | 12 | 6 (`out_{0,1,2}_{0,1}`) | the router configuration is part of the ELF |
| course program 04, `P=8` | 8 | 4 | first/last plus per-PE send/recv color params |
| SDK gemv-07 (2×2, uses `<layout>` coords) | 4 | 4 | every PE has different `x_color`/`ax_color` routes |

- `cs_readelf -r` / `-m` on the 6×2 build: `out_1_0.elf` holds blocks for fabric tiles (5,1),(6,1),(7,1),(8,1). It is one file for the four middle-column PEs of row 0. `out_0_1.elf` is fabric (4,2) only.
- `cs_readelf --routing out/bin/out_0_1.elf` shows `@(4,2): [3] (WEST) → (RAMP)` plus memcpy's colors 21–23. The routes really are inside the ELF.
- Wrapper checks: `--fabric-dims=7,3` for a 1×1 program gives `RuntimeError: Fabric dimension must be at least 8-by-3`. `--fabric-offsets=3,1` gives `RuntimeError: The core must have --fabric-offsets=4+width_west_buf,1`. Both come from `_generate_memcpy` in the wrapper, before the CSL compiler runs.
- Link stage: an oversized array gives `ld.lld: error: ran out of PE memory for data (section .bss)` followed by `Failed to link`.
- The halo: `out/west/bin/out_{0,1,2}_0.elf` and `out/east/bin/out_{0,1}_0.elf`, each with its own `out.json` (program 04 build). Notes §2 also record the `generated/` directory.

**Proposed addition.** A new section "What cslc actually builds", placed after "From source to simulation". It has four parts.
1. A five-stage paragraph or ordered list:
   1. The `cslc` wrapper (Python) checks the fabric against memcpy's needs (width + 7, height + 2, offsets `4+width_west_buf,1`) and generates the west and east halo programs.
   2. `cslc-driver` evaluates `layout {}` at compile time. Every `@set_tile_code` and `@set_color_config` is now a concrete value.
   3. PEs with identical code, params and router configuration are grouped into one PE program.
   4. Each group is compiled and then linked with `ld.lld`, which is where "ran out of PE memory" comes from.
   5. The wrapper writes `out.json` (params) and `bin/out_rpc.json` (export IDs).
   Each stage gets the error it can raise. Tag the stages `Derived` and the messages `Measured`.
2. The table above, verbatim, captioned "What splits a PE program", tagged `Measured`.
3. A diagram: a 6×2 grid of PEs coloured by ELF. First the 3-colour version, then a toggle "add a per-row route" that splits it into 6 colours. Label each region with its file name (`out_1_0.elf` covers four PEs). This can be the real-rule version of visuals-review P5 (the "Unique params → ELFs" counter). The counting rule is: classes = distinct (column role ∈ {first, middle, last}) × distinct per-PE params × distinct route sets.
4. One sentence that corrects the ELF naming: "`out_i_j` numbers a group of identical PEs. Use `cs_readelf -r` to see which fabric tiles a file covers." Then give the practical consequence: "`<layout>`'s `get_x_coord()` removes coordinate params, but it does not remove route differences. A program whose PEs all route differently still compiles one program per PE."

### D2 [critical] SdkLayout, the Python alternative to layout.csl, is absent

**What is missing.** SdkLayout gets one mention, in ch04, and none here. The SDK ships five tutorials on it (sdklayout-01 to -05). It is a different compile and run model:
- There is no `cslc` command. `layout.compile()` is called from `run.py` under `cs_python`.
- Colors are symbolic and allocated automatically (`colors.json`).
- Routes are "painted" from Python.
- Ports are joined with `layout.connect()`, which "will automatically find and encode a path".
- Host I/O uses streams, not memcpy (`memcpy_required=False`).
- Code regions are placed anywhere on the fabric (`place(x, y)`).

**Why it matters.** The chapter is titled "CSL and the toolchain", and the brief asks for the SdkLayout API. A learner who opens the SDK will find two layout styles and not know which to use. It also clarifies by contrast that memcpy is an optional library, not part of the language.

**Source.** `EX/tutorials/sdklayout-01-introduction/{README.rst,gv.csl,run.py}`, `sdklayout-02-routing/{send_receive.csl,run.py}`, `sdklayout-03-ports-and-connections/run.py`, `sdklayout-04-h2d-d2h/{README.rst,run.py}`, `sdklayout-05-gemv/{README.rst,run.py,gemv.py,demux.py}`, notes §6, report ch11 ("SdkLayout is the newer Python-side alternative …").

Measured, running sdklayout-02 with `cs_python run.py --arch=wse3`:
- It prints `SUCCESS!`.
- `sim_stats.json` shows `fabric_x: 2, fabric_y: 1, iotile_count: 0, cycle_count: 81`. Compare 8×3 and thousands of cycles with memcpy.
- It writes these files into the current directory:
  - `executables/send_receive-1.elf` and `send_receive-2.elf`: two ELFs, because `select` is 0 or 1;
  - `colors.json` (`{"color_id": 0, "color_name": "/send_receive:c"}`);
  - `plan.json`;
  - `out.elf`, `out.map`, `out.symbols`, `out.params`, `out.core`, `out.lst`, `out.viz`;
  - `generated/{coord,default}.elf`.

**Proposed addition.** A new section "The other way to lay out: SdkLayout", placed after the toolchain section. It has five parts.
1. A paragraph built on the facts above.
2. A side-by-side code block. Left: SAXPY-style `layout.csl` with `@set_rectangle`, `@set_tile_code` and `@set_color_config`. Right: the sdklayout-02 equivalent:
   ```python
   platform = get_platform(args.cmaddr, SimfabConfig(dump_core=True), SdkTarget.WSE3)
   layout = SdkLayout(platform)
   code = layout.create_code_region('./send_receive.csl', 'send_receive', 2, 1)
   code.set_param(IntVector(0,0), 'select', 0); code.set_param(IntVector(1,0), 'select', 1)
   c = Color('c')
   code.paint(IntVector(0,0), c, [RoutingPosition().set_input([Route.RAMP]).set_output([Route.EAST])])
   code.paint(IntVector(1,0), c, [RoutingPosition().set_input([Route.WEST]).set_output([Route.RAMP])])
   code.set_param_all(c)            # device receives the physical id as `param c: u16`
   artifacts = layout.compile(out_prefix='out')
   rt = SdkRuntime(artifacts, platform, memcpy_required=False)
   rt.load(); rt.run(); rt.stop()
   rt.read_symbol(1, 0, 'buffer', dtype='uint16')
   ```
   Device side: `param c: u16;` … `@get_color(c)`, `export var buffer: [size]u16;`. There is no `@export_symbol`, no memcpy import and no `unblock_cmd_stream`.
3. A table "layout.csl + memcpy vs SdkLayout" with these rows:
   - who compiles (`cslc` vs `layout.compile()` inside `cs_python`);
   - colors (numbers you pick vs symbolic `Color('c')` or `region.color('tx')`, ids in `colors.json`);
   - routes (`@set_color_config` vs `paint`, `paint_all`, `paint_range`, `get_edge_routing`);
   - inter-region routing (by hand vs `create_output_port` / `create_input_port` + `layout.connect`);
   - host I/O (memcpy copy/stream + RPC vs `create_input_stream`/`create_output_stream` + `runtime.send`/`receive`, or `read_symbol` after `stop()`);
   - placement (fixed offset `4,1` vs `region.place(x, y)`, plus `hstack`/`vstack`);
   - exports (`@export_name` + `@export_symbol` vs `export var`);
   - fabric (the user rectangle plus the halo vs exactly the regions you place).
4. A limitation callout, quoting sdklayout-04: "it is only possible to create input/output streams to/from single-PE ports. If a port consists of more than one PE then an adaptor layer must be created explicitly". Then: "sdklayout-05 builds demux/mux regions in Python for a 4×4 GEMV."
5. A diagram of the sdklayout-03 placement: sender1 at (2,2), sender2 at (4,7), add2vec at (7,4), receiver at (3,3). Draw ports as edge markers and `connect` arcs as auto-routed paths. Caption: "You place regions and name ports; the compiler finds the paths and the colors."

Tag the code and API `SDK 2.10.1`, and the cycle and fabric facts `Measured`.

### D3 [critical] The debugging workflow: what each common mistake actually prints

**What is missing.** The tools table names five tools, but there is no workflow from symptom to cause. Several common mistakes give misleading or delayed errors that the learner cannot decode:
- A missing `@export_symbol` compiles silently.
- A missing `--params` value reports an "uninitialized variable" error.
- A forgotten `unblock_cmd_stream()` surfaces as a host-side length error.

The chapter also says `<simprint>` output is "prefixed with cycle and PE". The library prefixes only the cycle. PE coordinates come from `fmt_with_coords` or a helper that the user writes.

**Why it matters.**
- The chapter's own callout says "most bugs are resource bugs", and these are exactly those bugs.
- The objective "find the outputs" includes knowing that a deadlock and a success both stop "due to idleness".

**Source.** Measured, each by modifying course program 01 (SAXPY, WSE-3):

| Mistake | When it shows | Exact message |
|---|---|---|
| `const y_ptr` but `@export_name("y", …, true)` | compile | `pe_program.csl:25:18: error: exported symbol mutability mismatch` / `note: expected name to be mutable` / `note: symbol declared here` |
| omit `--params=N:64` (layout declares `param N: i16;`) | compile | `layout.csl:3:1: error: only 'var' and 'extern const' variables may be uninitialized` then `error: failed to evaluate layout block` |
| `--fabric-dims=7,3` for a 1×1 program | compile (wrapper) | `RuntimeError: Fabric dimension must be at least 8-by-3` |
| `--fabric-offsets=3,1` | compile (wrapper) | `RuntimeError: The core must have --fabric-offsets=4+width_west_buf,1` |
| `N=5620` (two f32 arrays) | link | `ld.lld: error: ran out of PE memory for data (section .bss)` … `Failed to link` |
| delete `@export_symbol(saxpy)` | **runtime**, compiles cleanly (`saxpy` simply missing from `out_rpc.json`) | `FATAL: Error: the function saxpy does not exist` (from `SdkRuntime::check_rpc_api`) |
| delete `sys_mod.unblock_cmd_stream()` | runtime, at the next memcpy | `the received length (0 bytes) is not expected (256 bytes), could be a kernel stall`; `sim.log` ends `@23829 Stopping due to fatal error`; no `sim_stats.json` written; about 9 s of wall time |

Library facts, from `LIB/simprint.csl` and `LIB/debug.csl` (read in the SIF), topic-12 and topic-13:
- `<simprint>`: `print_string`, `print_u16_decimal`/`_hex`/`_binary`, `print_u32_*`, `print_f16`, `print_f32`, `fmt(fstr, args)`, `fmt_no_nl`, and `fmt_with_coords`. The last prints `"PE({d},{d}): "` using `<layout>`. There is also `param enable: bool = true`.
- topic-13: "The output is flushed to sim.log whenever a newline is encountered, so you must explicitly print "\n"". Also: "each line printed to sim.log is prepended with the cycle".
- `<debug>`: `@import_module("<debug>", .{ .key = "trace", .buffer_size = 100 })`, with `trace_string`, `trace_u16/i16/u32/i32/f16/f32/bool/u8/i8`, `trace_timestamp`, `put_u16/u32`, `tagged_put_u8`.
- `<debug>` host side: `from cerebras.sdk.debug.debug_util import debug_util; d = debug_util(dirname, cmaddr=…); d.read_trace(4 + x, 1 + y, 'trace')`. These are fabric coordinates, not rectangle coordinates, which is why topic-12 uses `core_offset_x = 4`.

**Proposed addition.** Replace the "Debugging tools" table and the paragraph after it with three parts.
1. **"Error decoder"**: the table above, tagged `Measured`. Add a fourth column, "Fix".
2. **"When it hangs: a four-step procedure"**:
   1. Read the run.py traceback. A "received length … kernel stall" error means some RPC never unblocked, or a task never ran.
   2. Add `const prt = @import_module("<simprint>");` and `prt.fmt_with_coords("reached {d}", .{step});` at task entry and exit. Rerun, then `grep PE sim.log` to find the last line each PE printed.
   3. Check the routes you believe you set: `cslc … --out-routes` (see D7), or `cs_readelf --routing --tile X,Y out/bin/out_i_j.elf`.
   4. Only then open `csdb` (`csdb out trace list`, `csdb out memory read …`, `csdb out wavelet …`; notes §7). Keep csdb at "help screens verified": notes §7 lists its interactive CTF workflow as a gap.
3. **Two snippets**, each 4–6 lines: the simprint snippet above, and the `<debug>` device and host pair with the fabric-coordinate warning.

Fix the "prefixed with cycle and PE" cell to "prefixed with `@cycle`; use `fmt_with_coords` for the PE". Add one sentence: "A deadlock and a success can both end 'Stopped due to idleness'. Only your host-side check tells you which."

### D4 [major] Language coverage: about half of the features the SDK examples use are missing

**What is missing.** "The language in one screen" lists scalars, loops, `param`, `comptime`, resource types and `@is_arch`. It leaves out things the learner meets on the first page of any multi-PE example:
- anonymous struct literals `.{ .a = 1 }` (used on every `@set_tile_code` and `@get_dsd` line, but never explained);
- `enum(u16)` plus `switch` (sdklayout-02);
- `@comptime_assert` (gemv-08);
- `@get_rectangle().width/.height/.offsets` (topic-11, `LIB/layout.csl`);
- arrays as comptime-only function arguments, versus pointers at run time;
- dereference `ptr.*` and `@ptrcast` (topic-01, topic-11);
- param types beyond integers (`color`, `local_task_id`, `comptime_string`, `fn()void`) and default values (`param enable: bool = true`);
- module instancing: each `@import_module` with different params is a separate instance (topic-12 imports `<debug>` twice);
- `--import-path` / `CSL_IMPORT_PATH`;
- `inline fn` and `anytype` (`LIB/debug.csl`);
- `export var` (sdklayout);
- `@get_color(id)` and `@get_int`;
- multi-dimensional arrays `A[i, j]` (topic-10).

It also leaves out one rule that bites: `--params` values must be unsigned integers. The `cslc --help` text says "value is an unsigned integer", so floats and negatives cannot be passed on the command line.

**Why it matters.** A learner reading gemv-07/08 or the course's programs 03–05 meets these on the first page. The `--params` rule decides how a learner passes a float coefficient: it has to go through memcpy or an RPC argument, as SAXPY's `a` does.

**Source.** gemv-00, gemv-04, gemv-08 `layout.csl`; topic-01 README ("Arrays can only be passed to or returned from functions used at compile-time"; "CSL does not have a null pointer"); topic-02 README; topic-10; topic-11 `pe_program.csl`; topic-12 `receiver.csl`; sdklayout-02 `send_receive.csl`; `LIB/{debug,simprint,layout}.csl`; `cslc --help`; `cslc-driver --help` (`--import-path`: "searched _before_ the compiler's built-in library directory"); notes §1.

**Proposed addition.** Keep the two-column "one screen" summary. Add a collapsible "Language reference card" table with columns Feature · One-line example · Where you'll meet it, and about 14 rows:
- `.{ .N = N }` anonymous struct;
- `enum(u16) { send = 0, receive = 1 }` + `switch (@as(mode, select)) { mode.send => …, mode.receive => … }`;
- `@comptime_assert(M % kernel_y_dim == 0)`;
- `@get_rectangle().width`;
- `param c: color;` / `param enable: bool = true;` / `param f: fn()void = nop;`;
- `const t1 = @import_module("<debug>", .{ .key = "a", .buffer_size = 100 });` twice = two buffers;
- `(p.*)[0] += 1`;
- `@ptrcast([*]u32, &buf)`;
- `inline fn`;
- `fn trace(x: anytype)`;
- `export var gv: i16;`;
- `@get_color(c)` from a `u16` param;
- `const A = @constants([4, 4]f32, 0.0); A[i, j]`;
- `@is_arch("wse3")` in an expression: `@get_dsd(fabout_dsd, if (@is_arch("wse3")) .{…} else .{…})`.

Add a callout: "`--params` takes unsigned integers only (cslc --help). Pass floats at run time."

### D5 [major] The 48 KB budget is never made concrete: how much memcpy and code cost, and how to measure it

**What is missing.** The chapter says "arrays in the 48 KB" but never shows how to measure what a program uses, how much the runtime takes, or where the limit shows up (at link time).

**Why it matters.** Sizing arrays per PE is the first design decision in every distributed program (ch11–12 split arrays across PEs for exactly this reason).

**Source.** Measured with `cs_readelf -m out/bin/out_0_0.elf` on course program 01, two f32 arrays of N each:

| Build | Memory used on PE (4,1) |
|---|---|
| WSE-3, N=1 | 4,240 B |
| WSE-3, N=1024 | 12,432 B (+8,192 = 2×1024×4, as expected) |
| WSE-3, N=5610 | 49,120 B (of 49,152) |
| WSE-3, N=5620 | link fails: `ran out of PE memory for data (section .bss)` |
| WSE-2, N=5600 | 47,674 B (so a fixed footprint of about 2,874 B, against about 4,240 B on WSE-3) |

`cs_readelf --help`: `-m, --msize  Display main memory used per PE`; `--syms` shows each symbol's address and banks.

**Proposed addition.**
- A short subsection "Where did my 48 KB go?" with the table, tagged `Measured`.
- One paragraph: "Even an empty program uses about 4 KB on WSE-3 for code, the memcpy runtime and its buffers. SAXPY's two vectors can hold at most about 5,610 floats each. Overflow is a link error, not a runtime one."
- An experiment box: "Bisect the largest N: `for N in 5000 5600 5620; do cslc … --params=N:$N -o b$N …; cs_readelf -m b$N/bin/out_0_0.elf; done`."
- Optionally, a stacked bar widget: a 48 KB bar split into "runtime + code ≈ 4.2 KB" and "x, y = 8·N bytes", with an N slider that turns red past 5,610.

### D6 [major] A standard-library map: which `<…>` modules exist and which a learner needs

**What is missing.** The chapter names only `<memcpy/…>`, `<simprint>`, `<debug>` and `<layout>`. It gives no list of what the compiler ships, and no guidance on what is a library call versus a builtin.

**Why it matters.** Learners reimplement things the library provides, such as timing with `<time>`, math functions with `<math>`, and MPI-style collectives with `<collectives_2d>`. Some modules also collide with memcpy. For example, `<message_passing>` says "bank B (base=19) clashes with memcpy".

**Source.** Notes §8 (directory listing and APIs); `LIB/` inside the SIF (`singularity exec <sif> ls …/csl-libs`); topic-02 (`<time>`, `<random>`); topic-11 (`<collectives_2d>`); topic-16 (`<tile_config>`); report ch12.

**Proposed addition.** A table with columns Module · What for · Key calls · Tutorial:

| Module | What for | Key calls | Tutorial |
|---|---|---|---|
| `<memcpy/get_params>` (layout), `<memcpy/memcpy>` (PE) | host I/O | `get_params(px)`, `unblock_cmd_stream()`, `get_streaming_fabout_dsd` | gemv-01 |
| `<layout>` | run-time coordinates | `get_x_coord()`, `get_y_coord()` | gemv-07 |
| `<simprint>` | prints to `sim.log` | see D3 | topic-13 |
| `<debug>` | trace buffers read by the host | see D3 | topic-12 |
| `<time>` | timing | `enable_tsc()`, `get_timestamp(*[3]u16)`, `reset_tsc_counter()` | topic-02 |
| `<math>` | math functions | `sqrt_f32`, `exp_f16`, `tanh`, `min`, `max` … | topic-10 |
| `<random>` | random numbers | `random_f32`, `random_normal_f32` | topic-02 |
| `<collectives_2d/params>` / `<collectives_2d/pe>` | MPI-style collectives | `broadcast`, `scatter`, `gather`, `reduce_fadds` | topic-11 |
| `<tile_config>` | escape hatch: queue/color/switch registers | | topic-16 |
| others | | `<control>`, `<malloc>`, `<message_passing>`, `<complex>`, `<string>`, `<dsd_ops>` | |

Add the line from `LIB/layout.csl` as a two-line code sample. It shows that libraries are plain CSL that you can read: `fn get_x_coord() u16 { return tile_config.get_fabric_coord(tile_config.fabric_coord.X) - @get_rectangle().offsets.width; }`. Tag the table `SDK 2.10.1`.

### D7 [minor] `--out-routes`: show what memcpy adds to every PE

**What is missing.** The flag table lists `--out-routes` but never shows its output. That output is the clearest evidence that memcpy occupies colors 21–23 on every user PE.

**Why it matters.** It makes ch04 and ch07's "memcpy reserves colors 20–23" visible in the learner's own program. It is also step 3 of the hang procedure (D3).

**Source.** Measured on the 6×2 experiment with the per-row route (`cslc … --out-routes`):
```
|  0,0 | 3  | R | E   |      |
|      | 21 | R | E   | rx=R |
|      | 22 | W | R,E |      |
|      | 23 | W | R,E |      |
|  0,1 | 3  | W | R   |      |
|  1,0 | 21 | W | E   | rx=R | ...
```
In the output, color 21 (D2H) runs `RAMP→EAST` with a switch position on the first column and `WEST→EAST` elsewhere. Colors 22 (command) and 23 (H2D) run `WEST→RAMP,EAST` on every PE.

**Proposed addition.**
- A 10-line excerpt as a figure, captioned "Your color 3, and memcpy's 21/22/23, on every PE", tagged `Measured`.
- One sentence: "Commands and H2D data enter from the west and are passed east along each row; D2H results leave eastward."

### D8 [minor] The flag table leaves out half the flags, and does not separate wrapper from driver

**What is missing.**
- Wrapper-only flags: `--colors name:value`, `--import-path`, `--width-west-buf` / `--width-east-buf` ("buffer to mitigate slow input/output"; it also shifts the required offset to `4+width_west_buf`), and `--verbose`.
- Driver flags: `--single-pe`, `--output-json`, `--warnings-as-errors`, `--g0`, `--max-parallelism=N`, `--disable-auto-microthread-id`, `--dump-dsr-alloc-graph`, `--lomem-reservation-end`, `--link-section-start-address-bytes`, and `--separate-compilation` ("Experimental and unsupported").
- The fact that unknown options are forwarded from the wrapper to the driver.
- The fact that the default arch is wse2. This is a pitfall: omitting `--arch` silently builds for WSE-2.

**Why it matters.** A learner reads `commands.sh` in SDK examples that use these flags (bandwidth-test uses `--channels`, and the width buffers appear in benchmarks). Without them, the help screen is the only reference.

**Source.** `cslc --help` and `cslc-driver --help` (via `singularity exec <sif> cslc-driver --help`). Both were captured for this review.

**Proposed addition.** Split the table into "cslc (wrapper)" and "cslc-driver (forwarded)" and add the rows above. Make "default `--arch` is wse2" its own row, in bold. Leave the less common flags in a `<details>` element.

### D9 [minor] Simulator outputs: no anatomy of `sim_stats.json`, `sim.log` or the trace directory

**What is missing.** Only `cycle_count`, the fabric size, `hwtile_count` and the stop cause are shown. The following are not:
- the other fields: `idle_ce_cycles`, `idle_wavelet_cycles`, `iotile_count`, `nultile_count`, `tile_count`, `sim_time`, `cycles_per_second`, `threads`;
- `simconfig.json`;
- that `cycle_count` includes the memcpy load and copy phases and the idle tail, not just the kernel;
- that a fatal stop writes no `sim_stats.json` at all (Measured, missing-unblock run).

**Why it matters.** Lab 3 uses `cycle_count` to measure cost per step. Learners need to know that it is end-to-end, so that they difference two runs rather than read one.

**Source.** Notes §7 (field list); this review's runs; course program 01 output (7,740 cycles). For contrast: SdkLayout sdklayout-02 runs in 81 cycles with no memcpy (Measured), and gemv-01 takes 1,374 cycles with memcpy (notes).

**Proposed addition.**
- An annotated JSON block of a real `sim_stats.json` from program 01 (the fixer should rerun it to get the exact fields), with one-line notes per field.
- The sentence: "cycle_count is wall-to-wall: load, every memcpy, your kernel, and the idle tail. To time a kernel, difference two runs (Lab 3) or use `<time>` timestamps (topic-02)."

### D10 [minor] One source for WSE-2 and WSE-3: the idioms are not shown

**What is missing.** `@is_arch("wse3")` gets one bullet. The chapter does not show the concrete pattern every portable program uses:
- queue initialisation only on WSE-3: `if (@is_arch("wse3")) { @initialize_queue(out_q, .{ .color = c }); }` (sdklayout-02);
- task ID selection: `if (@is_arch("wse2")) @get_data_task_id(c) else if (@is_arch("wse3")) @get_data_task_id(iq)` (topic-12 `receiver.csl`);
- DSD struct selection (gemv-06).

It also does not mention that `<memcpy/memcpy>` itself switches to `wse2/` or `wse3/` internally.

**Why it matters.** All the course programs build for both chips. The tour shows a single-PE program that needs none of these idioms.

**Source.** sdklayout-02 `send_receive.csl`, topic-12 `receiver.csl`, gemv-06 `pe_program.csl`, `LIB/memcpy/memcpy.csl`, report ch06 table.

**Proposed addition.** A three-snippet box "Writing for both chips", with one link to ch05's portability table. Do not repeat the table.

### D11 [minor] Experiment: "Break it on purpose"

**What is missing.** The chapter has no hands-on step that ties the toolchain to its errors. Pedagogy P13 asks for one exercise. This proposal supplies a set that is ready to use.

**Why it matters.** Seeing each failure once makes the error decoder (D3) stick.

**Source.** The D3 experiments. Each takes under 15 s.

**Proposed addition.** An `<ol>` of five edits to a copy of program 01. Each item has a hidden "what you'll see" answer that quotes D3's message:
1. Change `var y_ptr` to `const y_ptr`.
2. Drop `--params`.
3. Delete `@export_symbol(saxpy)`.
4. Delete `unblock_cmd_stream()`.
5. Set `N` to 5620.

Add the warning: "Run from a directory outside /tmp. cs_python binds only `$PWD`, so `run.py` must be in the directory you run it from."

## Out of scope for this chapter (new-chapter or cross-chapter ideas)

- **New lab, "SdkLayout lab"**: port program 03 (row reduce) to SdkLayout, with a symbolic color, `paint_range` and `read_symbol`. Then add an input stream with a demux, as in sdklayout-05. This would sit after ch11, with ch09's D2 as the theory.
- **New lab or appendix, "Collectives"**: topic-11's `<collectives_2d>` broadcast, scatter, gather and reduce, compared with the hand-routed program 05.
- **ch07 (host I/O)**: the advanced SdkRuntime surface. This covers:
  - `nonblock=True` with `task_wait` / `is_task_done` (the memcpy calls return a `Task`);
  - `read_symbol(x, y, name, dtype)` after `stop()`;
  - `memcpy_h2d_rowbcast` / `colbcast` (ch07 mentions rowbcast; check depth);
  - `MemcpyDataType.MEMCPY_16BIT` with `COL_MAJOR` (conjugate-gradient run.py);
  - the fact that `nonblock` calls may be aggregated, so host timers are unreliable (bandwidth-test README).
- **ch04/ch07**: link to D7's `--out-routes` excerpt as visible proof of memcpy's color reservations.
- **ch10 to ch12 (labs)**: add a `<simprint>` line to program 02 or 04, and show the real `sim.log` excerpt. Use `cs_readelf -m` in Lab 3 to justify the per-PE tile size.
- **Appendix, "SDK tutorial map"**: the gemv-00→09, pipeline, topic and sdklayout sequence from report ch12, with one line per tutorial and the course chapter it supports.
- **csdb deep dive**: only worth a section once someone runs the CTF trace workflow end to end. It is still a gap in the notes (§7).
