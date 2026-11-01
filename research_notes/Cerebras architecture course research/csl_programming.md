# CSL Programming Model and Cerebras SDK 2.10.1 Toolchain

Scope note. Nearly everything below comes from primary material in the installed SDK 2.10.1 (`/home/user/cerebras-sdk`): the tutorial and benchmark sources in the extras tarball, the CSL standard library that ships inside the container image, the `--help` output of the tools, and my own compile-and-simulate runs. The online docs at sdk.cerebras.net could not be reached: DNS resolution failed from this cloud session, so that host has to be allowed in the session's network settings. Anything that only exists in the online docs is therefore listed under Gaps.

Source abbreviations used in links:
- `EX` = `/home/user/cerebras-sdk/extras/csl-extras-202604101435-6-d2f7d96e/examples` (tutorials in `EX/tutorials`, benchmarks in `EX/benchmarks`).
- `LIB` = `/cb/toolchains/cslang/rel-sdk-2.10.0/202604012315-1813-1394a6ea/csl-libs`. This path is inside the SIF image `/home/user/cerebras-sdk/sdk-cbcore-2.10.1-sdk-202606181328-8faf87a26e.sif`; read it with `singularity exec <sif> cat ...`. The compiler toolchain directory inside the 2.10.1 image is labelled `rel-sdk-2.10.0`.
- "Local experiment" = runs I made under `/home/user/cerebras-sdk/tmp/claude-work/` (copies of the examples) on 2026-11-01.

---

## 1. CSL language basics (syntax, comptime, types, arrays, pointers, modules, params)

### Takeaway
CSL looks like Zig: `const`/`var` declarations, `fn`, `@builtins`, `for (@range(...)) |i|`, `while (c) : (i += 1)`, anonymous structs `.{ .a = 1 }`, and `comptime` blocks. It has 16/32-bit integer and float scalar types plus arrays and pointers. Its distinctive features are `param` (compile-time parameters supplied by the layout or the `cslc --params` flag), `@import_module` with `<lib>` names, and DSD/task/color types for hardware resources.

### Cited Findings
- "CSL's syntax is like that of Zig. Despite the similarity, both the purpose and the implementation of the CSL compiler are different from that of the Zig compiler." — [gemv-00 README](file://EX/tutorials/gemv-00-basic-syntax/README.rst)
- Basic types: `bool`, `i16`, `i32`, `u16`, `u32`, `f16`, `f32` (IEEE-754). Array and pointer types also exist. Functions are declared with `fn`. Builtins start with `@` and are implemented by the compiler. — [gemv-00 README](file://EX/tutorials/gemv-00-basic-syntax/README.rst)
- Every variable must be declared `const` (immutable) or `var`. Loops come in two forms: `for (@range(i16, M*N)) |idx| {...}` and `while (i < M) : (i += 1) {...}`. Casts use `@as(f32, idx)`. — [gemv-00 code.csl](file://EX/tutorials/gemv-00-basic-syntax/code.csl)
  ```csl
  const M: i16 = 4;
  var A: [M*N]f32;               // array type [len]T
  for (@range(i16, M*N)) |idx| { A[idx] = @as(f32, idx); }
  var i: i16 = 0;
  while (i < M) : (i += 1) { b[i] = 2.0; }
  ```
- Array initialisers and builtins: `@constants([N]f32, 1.0)`, `@zeros([M]f32)`, literal `[3]i16 { 1, 2, 3 }`. Multi-dimensional arrays are allowed, e.g. `@constants([size, size]f32, 42.0)` indexed as `A[i, i]`. — [gemv-02 pe_program.csl](file://EX/tutorials/gemv-02-memory-dsds/pe_program.csl), [topic-10 pe_program.csl](file://EX/tutorials/topic-10-map-builtin/pe_program.csl)
- Pointers: "Arrays can only be passed to or returned from functions used at compile-time. For functions used at runtime, pointers should be used instead." A pointer to an array must carry the array size in its type (`*[3]i16`). "CSL does not have a null pointer." Dereference with `.*`, e.g. `(data_ptr.*)[0] += 1`. Many-item pointers `[*]f32` are used for exported host-visible symbols. `@ptrcast([*]u32, &buf)` reinterprets a pointer. — [topic-01 README](file://EX/tutorials/topic-01-arrays-and-pointers/README.rst), [topic-01 pe_program.csl](file://EX/tutorials/topic-01-arrays-and-pointers/pe_program.csl), [topic-11 pe_program.csl](file://EX/tutorials/topic-11-collectives/pe_program.csl)
- Params: "Parameter values are compile-time constants, which implies that the compiler is fully aware of their precise value. This enables the programmer to not just change the program's behavior at runtime, but it also enables the programmer to change the program's compilation." They are declared `param M: i16;`. In the layout file they are set via `--params=M:4,N:6`; in PE files they are set by the `@set_tile_code` struct. — [gemv-04 README](file://EX/tutorials/gemv-04-params/README.rst), [gemv-04 layout.csl](file://EX/tutorials/gemv-04-params/layout.csl)
- Params may be untyped (`param memcpy_params;`, which receives a struct) or have defaults (`param enable: bool = true;`). Types such as `comptime_string`, `comptime_int`, `color`, `local_task_id` and function types (`param f_callback : fn ()void = sys_nop;`) are valid param types. — [LIB/debug.csl, LIB/simprint.csl, LIB/memcpy/memcpy.csl](file://LIB) (read inside the SIF)
- Modules: `const m = @import_module("<lib/name>", .{ .param = value });`. Angle brackets name compiler-bundled libraries. Each import with different params is a separate instance; topic-12 imports `<debug>` twice with different `.key`s. `--import-path` / `CSL_IMPORT_PATH` add search directories for `<...>` paths. — [topic-02 README](file://EX/tutorials/topic-02-libraries/README.rst), [topic-12 receiver.csl](file://EX/tutorials/topic-12-debug-library/receiver.csl), `cslc --help` (local experiment)
- Compile-time control: `comptime { ... }` blocks hold bindings and exports. `@comptime_assert(M % kernel_y_dim == 0)` checks layout invariants. `@is_arch("wse3")` selects code per architecture, and is widely used inside `if` expressions that pick struct literals: `@get_dsd(fabout_dsd, if (@is_arch("wse3")) .{...} else .{...})`. — [gemv-08 layout.csl](file://EX/tutorials/gemv-08-routes-3/layout.csl), [gemv-06 pe_program.csl](file://EX/tutorials/gemv-06-routes-1/pe_program.csl)
- Other syntax seen in the sources:
  - enums `const mode = enum(u16) {send = 0, receive = 1};`
  - `switch (x) { 0 => {...}, else => {...} }`
  - `inline fn`
  - `export var gv: i16;` (exports the variable directly, used with SdkLayout and `read_symbol`)
  - `@bitcast(u16, x)`, `@get_int(color)`
  - `anytype` parameters (`fn trace(x: anytype)`)

  — [sdklayout-02 send_receive.csl](file://EX/tutorials/sdklayout-02-routing/send_receive.csl), [topic-11 pe_program.csl](file://EX/tutorials/topic-11-collectives/pe_program.csl), [LIB/debug.csl](file://LIB)
- FP16 format is chosen at compile time: `cslc-driver --fp16-format=f16|cb16|bf16` ("Default=f16"; cb16 = "Cerebras float16"). The library code also writes the half type as `@fp16()`. — cslc-driver `--help` (local experiment), [LIB/malloc.csl](file://LIB)
- Wavelet payloads are 32 bits. A data task can take one `u32`/`f32` argument, or two 16-bit arguments for the lower and upper halves. In topic-04 the upper 16 bits carry an index for sparse data: `task main_task(wavelet_data: i16, index: i16)`. — [topic-04 README](file://EX/tutorials/topic-04-sparse-tensors/README.rst)

### Inferences
- For teaching: present CSL as "Zig syntax + a hardware-resource type system" (`color`, `input_queue`/`output_queue`, `data_task_id`/`local_task_id`/`control_task_id`, `mem1d_dsd`/`fabin_dsd`/...). Most bugs come from misusing those resource types, not from the scalar language.
- Params that differ per PE produce more unique PE programs and longer compiles. That is why gemv-07 replaces a per-PE `pe_id` param with runtime `<layout>` coordinates (see section 2).

### Gaps
- The full language reference (complete builtin list, `comptime_float`, struct/union semantics, `linksection`, `export` rules) is online only (sdk.cerebras.net could not be reached). Builtins named above are only those confirmed in source.

---

## 2. Program structure: layout.csl vs pe_program.csl, memcpy infrastructure, exported symbols, RPC

### Takeaway
A program is (a) a top-level **layout file**, compiled by `cslc`, whose `layout { }` block sets the PE rectangle, assigns a code file plus params to each PE (`@set_tile_code`), configures routes (`@set_color_config`) and declares host-visible names (`@export_name`); (b) one or more **PE programs** that import `<memcpy/memcpy>` with the per-column params from `<memcpy/get_params>`, then export symbols and functions with `@export_symbol`; and (c) a host Python script. Host-callable functions are RPCs. Each one must end by calling `sys_mod.unblock_cmd_stream()` (directly or from a completion task), or the host's next command hangs.

### Cited Findings
- "A complete program consists of a host program (a Python script...) and at least two CSL code files, one of which defines the layout ... and one or more of which define the programs running on the individual PEs." Execution can run on a CS system or on the "Cerebras Fabric Simulator". — [gemv-01 README](file://EX/tutorials/gemv-01-complete-program/README.rst)
- Minimal layout (gemv-01):
  ```csl
  const memcpy = @import_module("<memcpy/get_params>", .{ .width = 1, .height = 1 });
  layout {
    @set_rectangle(1, 1);                       // width (cols), height (rows)
    @set_tile_code(0, 0, "pe_program.csl", .{ .memcpy_params = memcpy.get_params(0) });
    @export_name("y", [*]f32, false);           // false = host may read, not write
    @export_name("init_and_compute", fn()void); // host-callable
  }
  ```
  — [gemv-01 layout.csl](file://EX/tutorials/gemv-01-complete-program/layout.csl)
- Matching PE program:
  ```csl
  param memcpy_params;
  const sys_mod = @import_module("<memcpy/memcpy>", memcpy_params);
  var y: [M]f32;
  const y_ptr: [*]f32 = &y;
  fn init_and_compute() void { initialize(); gemv(); sys_mod.unblock_cmd_stream(); }
  comptime {
    @export_symbol(y_ptr, "y");
    @export_symbol(init_and_compute);
  }
  ```
  "After this function finishes, memcpy's cmd_stream must be unblocked on all PEs for further memcpy commands to execute." — [gemv-01 pe_program.csl](file://EX/tutorials/gemv-01-complete-program/pe_program.csl)
- Grid coordinates: "The dimensions of a grid of PEs is always specified as width by height (or ... columns by rows), and individual PEs are indexed by (x, y), or ... (column number, row number)." — [gemv-05 README](file://EX/tutorials/gemv-05-multiple-pes/README.rst)
- `memcpy.get_params(px)` takes the PE's **column** number. Internally it computes `first_pe = (0 == px)` and `last_pe = (width-1 == px)`, which "is used in H2D and D2H to set up counter filter and switch". It also passes through the optional streaming color IDs `MEMCPYH2D_1..4`, `MEMCPYD2H_1..4` and `LAUNCH` (all default to `MEMCPY_UNDEF`). — [LIB/memcpy/get_params.csl, LIB/memcpy/memcpy.csl](file://LIB)
- `<memcpy/memcpy>` is a wrapper. It imports `<memcpy/wse3/memcpy>` when `--arch=wse3` and `<memcpy/wse2/memcpy>` otherwise. Its public functions are `unblock_cmd_stream()`, `block_cmd_stream()` and `get_streaming_fabout_dsd(color, extent, oq)`, plus a `param f_callback` that runs "When D2H finishes". Library comment: "All commands are running sequential on command color which can be blocked by block_cmd_stream() or unblocked by unblock_cmd_stream(). The user must call unblock_cmd_stream() at the end of a RPC." — [LIB/memcpy/memcpy.csl](file://LIB)
- Resources memcpy reserves (from `<memcpy/sys_params>`):

  | Kind | Reserved IDs and names |
  |---|---|
  | Routable colors | `MEMCPYD2H_DATA = 21`, `RXCOMMAND = 22`, `MEMCPYH2D_DATA = 23`; `SYS_RXCTX = 20` for context switch |
  | Local tasks | 24 (`SYS_EN_MAIN`), 27 (`SYS_UBLK_C22`), 28 (`SYS_EXIT`), 30 (`SYS_SEND_CTRL`); 29 = teardown; 31 = NOP |
  | Control tasks | 33–37 (`SYS_CMD_PUSH`, `SYS_CMD_MEMCPYH2D`, `SYS_CMD_MEMCPYD2H`, `SYS_RPC`, `SYS_CHECK_AND_IGNORE`), 40 (`SYS_CTXCFG`) |
  | Queues | Input queue 0 and output queue 0 |

  The library also notes that "switching-capable colors are 0–9, 12, 13, 16, 17, 20, and 21". — [LIB/memcpy/sys_params.csl](file://LIB)
- On WSE-3, memcpy "reuses input queue 0 and output queue 0 for streaming H2D/D2H ... However the user must not use input queue 1, otherwise compilation fails." The tutorial task maps mark WSE-3 task IDs 0 and 1 as "reserved (memcpy)", and the queue_flush example says "memcpy reserves input/output queue 0 and 1". User code in the tutorials therefore starts its queues at ID 2. — [LIB/memcpy/memcpy.csl](file://LIB), [topic-05 pe_program.csl](file://EX/tutorials/topic-05-sentinels/pe_program.csl), [topic-16 queue_flush_sender.csl](file://EX/tutorials/topic-16-queue-flush/queue_flush_sender.csl)
- The 25-pt stencil README states that "SdkRuntime reserves 6 colors". — [25-pt-stencil README](file://EX/benchmarks/25-pt-stencil/README.rst)
- RPC with arguments: the layout declares `@export_name("f_activate_comp", fn(u32)void);`, the device defines `fn f_activate_comp(iter_cnt: u32) void { iterations = iter_cnt; @activate(COMP); }`, and the host calls `runner.launch("f_activate_comp", cast_uint32(iterations), nonblock=False)`. — [25-pt-stencil layout.csl / task.csl / run.py](file://EX/benchmarks/25-pt-stencil/)
- Runtime coordinates instead of params: `const layout_mod = @import_module("<layout>"); layout_mod.get_x_coord()` / `get_y_coord()`. "This can reduce compilation time by reducing the number of unique PE programs that need to be compiled." `<layout>` implements these as fabric coordinate minus `@get_rectangle().offsets`. — [gemv-07 README](file://EX/tutorials/gemv-07-routes-2/README.rst), [LIB/layout.csl](file://LIB)
- `@get_rectangle().width/.height` gives the program rectangle size at compile time. — [topic-11 pe_program.csl](file://EX/tutorials/topic-11-collectives/pe_program.csl)
- What the memcpy infrastructure adds around the user rectangle (local experiment, gemv-01 on WSE-3 with `--fabric-dims=8,3 --fabric-offsets=4,1`):
  - `out/` contains `bin/out_0_0.elf` (the user PE), `west/bin/out_{0,1,2}_0.elf`, `east/bin/out_{0,1}_0.elf`, `generated/{default,coord,MEMCPY_XY_ROUTES}.elf`, `out.json` and `bin/out_rpc.json`.
  - `west/out.json` has params such as `FABRIC_CMD_ID`, `FABRIC_H2D_DATA_ID_0`, `num_demux`, `width_west_buf`.
  - `out_rpc.json` lists the exported symbols: `{"id":2,"kind":"Func","name":"init_and_compute"}` and `{"id":1,"immutable":1,"kind":"Var","name":"y","sym_name":"y_ptr","type":"[*]f32"}`.
- The library directory `LIB/runtime/` contains demux/mux/cmd_fan/buffer kernels (`demux.csl`, `mux.csl`, `cmd_fan.csl`, `layout_west_demux_cmdfan_multi.csl`, `layout_east_mux_multi.csl`, ...). These match the west (H2D/command) and east (D2H) halo columns. — [LIB/runtime listing](file://LIB/runtime)

### Inferences
- The `--fabric-offsets=4,1` used throughout the tutorials places the user rectangle at fabric (4,1). That leaves room for the memcpy west columns and the edge I/O. The `<debug>` reader's coordinates are relative to the fabric's northwest corner, not the rectangle's (section 7).
- An effective mental model: the host sends a command sequence on `RXCOMMAND` (color 22). memcpy blocks that command stream while an RPC runs. `unblock_cmd_stream()` lets the next queued H2D/D2H/launch command proceed. If even one PE forgets to unblock, everything stalls.

### Gaps
- The exact number of west/east columns memcpy adds per `--channels` value and `--width-west-buf` setting is not documented in the local sources. The 3 west and 2 east ELFs were observed only for `--channels 1`.

---

## 3. Tasks: data, local, control; binding, activation, blocking; WSE-2 vs WSE-3

### Takeaway
Device code is event-driven. **Data tasks** (wavelet-triggered tasks, WTTs) run once per arriving wavelet and receive its payload as an argument. **Local tasks** are activated by software (`@activate`) or by DSD-operation completion. **Control tasks** are activated by control wavelets carrying a task ID (e.g. sentinels). The key WSE-3 change is that data task IDs come from **input queues** (IDs 0–7), not colors (0–23 on WSE-2). WSE-3 also requires every queue to be explicitly bound to a color with `@initialize_queue`.

### Cited Findings
- Task-ID ranges: "On WSE-2, task IDs which can receive data wavelets are in the range 0 through 23, corresponding to the IDs of the colors. On WSE-3, task IDs which can receive data wavelets are in the range 0 through 7, corresponding to input queues which are bound to a routable color. ... local tasks ... on WSE-2 can be associated with any task ID from 0 to 30, and on WSE-3 can be associated with any task ID from 8 to 30." — [topic-05 README](file://EX/tutorials/topic-05-sentinels/README.rst)
- Declaring and binding each task kind:
  ```csl
  const exit_task_id: local_task_id = @get_local_task_id(9);
  const recv_x_task_id: data_task_id =
    if      (@is_arch("wse2")) @get_data_task_id(x_color)     // color
    else if (@is_arch("wse3")) @get_data_task_id(x_color_iq); // input queue
  const send_result_task_id: control_task_id = @get_control_task_id(43);

  task recv_x(x_val: f32) void { ... }   // payload is the argument
  task exit_task() void { sys_mod.unblock_cmd_stream(); }

  comptime {
    @bind_local_task(exit_task, exit_task_id);
    @bind_data_task(recv_x, recv_x_task_id);
    @bind_control_task(send_result, send_result_task_id);
    @initialize_queue(x_color_iq, .{ .color = x_color });
  }
  ```
  — [gemv-07 pe_program.csl](file://EX/tutorials/gemv-07-routes-2/pe_program.csl), [topic-05 pe_program.csl](file://EX/tutorials/topic-05-sentinels/pe_program.csl)
- Activation: `@activate(reduce_task_id)` is called from a task once a counter reaches N (gemv-07 `recv_x`). `@activate(main_task_id)` inside `comptime { }` schedules a task to run at program start (pipeline-01, topic-09, sdklayout gv.csl). — [gemv-07](file://EX/tutorials/gemv-07-routes-2/pe_program.csl), [sdklayout-01 gv.csl](file://EX/tutorials/sdklayout-01-introduction/gv.csl)
- Block/unblock for back-pressure:
  ```csl
  task memcpy_recv_x(data : f32) void {
    @block(memcpy_recv_x_task_id);
    buf[0] = data;
    @fmovs(memcpy_x_dsd, mem_buf_dsd, .{.async = true, .unblock = memcpy_recv_x_task_id });
  }
  ```
  This blocks the WTT so it cannot fire again until the async send that uses `buf` finishes. topic-09 does the same with `.unblock = process_task`. — [gemv-09 pe_program.csl](file://EX/tutorials/gemv-09-streaming/pe_program.csl), [topic-09 buffer.csl](file://EX/tutorials/topic-09-fifos/buffer.csl)
- Pipeline-01: "when using a fabric input DSD, it is important that the programmer blocks the wavelet's color ... Otherwise, wavelets of that color will attempt to activate the (empty) task associated with the color, which in turn will consume the wavelet before it can be consumed by the fabric input DSD." — [pipeline-01 README](file://EX/tutorials/pipeline-01-basic/README.rst)
- Control tasks and sentinels: "a non-routable control task ID to signal the end of an input tensor. We call this use ... a sentinel ... Since sentinel control task IDs are not routable colors, the programmer does not specify a route, but does need to bind the control task ID to a control task." topic-05 uses ID 43. topic-07 encodes a control-task ID (40) into a control wavelet with `ctrl.encode_single_payload(ctrl.opcode.SWITCH_ADV, false, recv_ctrl_id, data16)`. "The lower 16 bits of the control wavelet can be used to store an optional data payload for that control task." — [topic-05 README](file://EX/tutorials/topic-05-sentinels/README.rst), [topic-07 README / send.csl](file://EX/tutorials/topic-07-switches-entrypt/)
- memcpy library warnings: "`.activate` field only accepts color 0~30 because there is only 5-bit 'ACT/UB color' field in fabin/fabout DSD"; "`@activate(color)` can only activate a color less than 31"; "control wavelet indeed can trigger entrypoints bigger than 31". — [LIB/memcpy/sys_params.csl](file://LIB)
- Queues per architecture: WSE-2 `NUM_INPUT_QUEUES = 8`, `NUM_OUTPUT_QUEUES = 6`; WSE-3 `NUM_INPUT_QUEUES = 8`, `NUM_OUTPUT_QUEUES = 8`. Both have `NUM_COLORS = 24`. — [LIB/target/wse2.csl, wse3.csl, common.csl](file://LIB/target)
- Queue binding differences: on WSE-2, output queues are not bound to a color, because the fabout DSD's `.fabric_color` selects the color; `@initialize_queue(oq, .{})` is used. On WSE-3, each output queue binds to a single color, `@initialize_queue(oq, .{ .color = c })`, and the fabout DSD omits `.fabric_color`. The repeated idiom:
  ```csl
  @initialize_queue(send_color_oq, if (@is_arch("wse3")) .{ .color = send_color } else .{});
  @initialize_queue(send_color_iq, .{ .color = send_color });
  ```
  — [gemv-06 pe_program.csl](file://EX/tutorials/gemv-06-routes-1/pe_program.csl), [topic-16 README](file://EX/tutorials/topic-16-queue-flush/README.rst)
- Microthreads: "Unlike WSE-2, the WSE-3 architecture exposes microthread IDs. ... On WSE-2, the queue ID of an input or output fabric DSD corresponds to the ID of the microthread in which that operation executes. On WSE-3, queue IDs and microthreads can be decoupled, so that any microthread ID 0 to 7 can be used with any of queues 0 to 7." Usage: `const ut = @get_ut_id(4); @fmovs(out_dsd, y_dsd, .{ .async = true, .ut_id = ut, .activate = exit_task_id });`. "two operations cannot concurrently use the same microthread". The `cslc-driver` flag `--disable-auto-microthread-id` exists. — [topic-15 README / left_pe.csl](file://EX/tutorials/topic-15-wse3-microthreads/), cslc-driver `--help`
- Reusing a WSE-3 output queue for a new color requires `@queue_flush(oq)` after the send. When the queue drains, "WSE-3 will trigger the special teardown task 29". The handler is registered with `@set_empty_queue_handler(foo, oq)`. It reconfigures the queue with `tile_config.output_queue_config.encode_output_queue(id, color)` and must call `queue_flush.exit(oq)`. "Be careful not to issue `@queue_flush(oq)` before `@mov32`". WSE-2 doesn't need any of this. — [topic-16 README](file://EX/tutorials/topic-16-queue-flush/README.rst)
- Color swap (`swap_color_x`) is WSE-2-only: "CSL currently does not support color swap on WSE-3, and support is in development." That tutorial ships only `commands_wse2.sh`. — [topic-14 README](file://EX/tutorials/topic-14-color-swap/README.rst)

### Inferences
- A useful teaching table, derived from the findings above:

  | | WSE-2 | WSE-3 |
  |---|---|---|
  | Data task ID source | Color (0–23) | Input queue (0–7) |
  | Local task IDs | 0–30 | 8–30 |
  | Output queue binding | Fabout DSD names the color; one queue can carry several colors | Queue bound to one color at init; reuse needs `@queue_flush` |
  | Microthread ID | Same as queue ID | Explicit `.ut_id` allowed |
  | Color swap | Supported | Not supported |

- Tasks are not preemptive functions. A task runs to completion and async DSD operations proceed in microthreads, so "callbacks" are expressed as `.activate` / `.unblock` task IDs on the async op.

### Gaps
- Task priority and the scheduler policy (`<tile_config/task_priority>`, `main_thread_priority.csl` exist in LIB) are not explained in the tutorials. The online docs were unreachable.
- The exact WSE-2 data-task-ID boundary is slightly inconsistent: the README says 0–23, while the task-map comment in the topic sources says "IDs 0 through 24".

---

## 4. DSDs (mem1d/mem4d/fabin/fabout), DSD builtins, async ops, tensor_access, FIFOs, @map

### Takeaway
Data Structure Descriptors describe a whole loop over memory or over a fabric queue. One DSD builtin (`@fmacs`, `@fadds`, `@fmovs`, `@mov16/32`, `@add16`, `@fnegs`, ...) then runs the whole vector operation in hardware. An operand can be a memory DSD, a fabric DSD, a FIFO or a scalar. With `.async = true`, the op runs in a microthread and can `.activate` or `.unblock` a task on completion.

### Cited Findings
- Memory DSDs: "an efficient mechanism for performing operations on entire tensors". There are two equivalent ways to define one:
  ```csl
  var y_dsd = @get_dsd(mem1d_dsd, .{ .base_address = &y, .extent = M });
  var b_dsd = @get_dsd(mem1d_dsd, .{ .tensor_access = |i|{M} -> b[i] });
  var A_dsd = @get_dsd(mem1d_dsd, .{ .tensor_access = |i|{M} -> A[i*N] }); // stride N
  // == @get_dsd(mem1d_dsd, .{ .base_address = &A, .extent = M, .stride = N });
  ```
  "The tensor_access field specifies an induction variable, a loop bound, and an affine expression". — [gemv-02 README / pe_program.csl](file://EX/tutorials/gemv-02-memory-dsds/)
- GEMV column loop with DSD offset update:
  ```csl
  for (@range(u16, N)) |i| {
    @fmacs(y_dsd, y_dsd, A_dsd, x[i]);            // y += A[:,i] * x[i]
    A_dsd = @increment_dsd_offset(A_dsd, 1, f32); // next column
  }
  @fadds(y_dsd, y_dsd, b_dsd);                     // y += b
  ```
  — [gemv-02 pe_program.csl](file://EX/tutorials/gemv-02-memory-dsds/pe_program.csl)
- Other tensor_access forms:
  - diagonal: `|i|{size} -> A[i, i]`
  - broadcast a scalar from memory: `|i|{size} -> buf[0]` (extent `size`, always element 0), used as the "+1" operand in `@add16(out, in, one_dsd)`
  - `@set_dsd_base_addr(memDSD, data2)` re-points a DSD at another array

  — [topic-10](file://EX/tutorials/topic-10-map-builtin/pe_program.csl), [pipeline-01](file://EX/tutorials/pipeline-01-basic/pe_program.csl), [topic-16 sender](file://EX/tutorials/topic-16-queue-flush/queue_flush_sender.csl)
- Fabric DSDs:
  ```csl
  const out_dsd = @get_dsd(fabout_dsd, if (@is_arch("wse3"))
      .{ .extent = M, .output_queue = send_color_oq }
    else
      .{ .fabric_color = send_color, .extent = M, .output_queue = send_color_oq });
  @fmovs(out_dsd, y_dsd, .{ .async = true, .activate = exit_task_id }); // send M wavelets

  const in_dsd = @get_dsd(fabin_dsd, .{ .extent = M, .input_queue = send_color_iq });
  @fadds(y_dsd, y_dsd, in_dsd, .{ .async = true, .activate = exit_task_id }); // y += recv
  ```
  "The @fmovs and @fadds operations are performed asynchronously; when these operations are done, the color exit_color is activated". — [gemv-06 README / pe_program.csl](file://EX/tutorials/gemv-06-routes-1/)
- Fabric-to-fabric ops are allowed. In gemv-08, a middle column runs `@fadds(out_dsd, y_dsd, in_dsd, ...)`: it receives the partial sum from the west, adds its local y, and forwards it east, all in one op. — [gemv-08 pe_program.csl](file://EX/tutorials/gemv-08-routes-3/pe_program.csl)
- Control wavelets are sent with `.control = true` in a fabout DSD plus `@mov32(tx_ctrl_dsd, payload)`. — [topic-06 send.csl](file://EX/tutorials/topic-06-switches/send.csl)
- Synchronous scalar send: `@mov16(out_dsd, wavelet_data)`, with the comment "The non-async operation works here because only two wavelet are sent. It would be better to use async operation". — [topic-04 pe_program.csl](file://EX/tutorials/topic-04-sparse-tensors/pe_program.csl)
- Blocking vs async (pipeline-01): "The microthread is necessary because the CE (compute engine) must have some resources to run memcpy kernel. The kernel stalls if a blocking instruction `@add16(outDsd, inDsd, 1)` is used." — [pipeline-01 README](file://EX/tutorials/pipeline-01-basic/README.rst)
- FIFOs: `var fifo_buffer = @zeros([1024]f32); const fifo = @allocate_fifo(fifo_buffer);` A FIFO is filled by one async op and drained by another:
  ```csl
  @fadds(fifo, in_dsd, ten_dsd, .{ .async = true });     // fabric -> FIFO (+10)
  @fnegs(loopback_dsd, fifo, .{ .async = true });        // FIFO -> fabric (negate)
  ```
  "extend the small hardware queues". "The FIFO requires two microthreads and a scratch buffer." Effectively infinite extents use `0x7fff`. — [topic-09](file://EX/tutorials/topic-09-fifos/), [pipeline-02](file://EX/tutorials/pipeline-02-fifo/)
- "WSE3 does not allow multiple fabric inputs per DSD operation. Therefore, we introduce a FIFO for portability between WSE2 and WSE3." — [sdklayout-03 add2vec.csl](file://EX/tutorials/sdklayout-03-ports-and-connections/add2vec.csl)
- Queue capacity matters. pipeline-01's single-PE H2D→D2H redirect "stalls when size exceeds 14" because "H2D and D2H are serialized". — [pipeline-01 README](file://EX/tutorials/pipeline-01-basic/README.rst)
- 16-bit fabric data: with SdkLayout streaming, "Each operand is 16-bits while 'size' specifies the number of 32-bit wavelets. Each wavelet packs 2 16-bit operands", so fabin/fabout extents are `size * 2`. — [sdklayout-04 add2vec.csl](file://EX/tutorials/sdklayout-04-h2d-d2h/add2vec.csl)
- `@map` is "a customizable DSD operation" applying a user function element-wise:
  ```csl
  @map(math_lib.sqrt_f32, dsdA, dsd_sqrt_diag_A);
  @map(transformation, dsdA, 2.0, 6.0, dsd_weight, dsdA);   // mix DSDs and scalars
  @map(reduction, dsdB, &sum[0], &sum[0]);                   // reduction via pointer
  ```
  "Since DSDs are supported natively by the hardware, using @map can lead to significant performance gains compared to writing explicit loops." — [topic-10 README / pe_program.csl](file://EX/tutorials/topic-10-map-builtin/)
- DSD builtins confirmed in the tutorial sources: `@fmacs`, `@fadds`, `@fmovs`, `@fnegs`, `@mov16`, `@mov32`, `@add16`, `@map`, `@increment_dsd_offset`, `@set_dsd_base_addr`. The collectives library also uses explicit DSRs (`@get_dsr(dsr_dest, id)`, `dsr_src0`, `dsr_src1`) and accepts `dest_dsr_ids/src0_dsr_ids/src1_dsr_ids` params. — sources above, [LIB/collectives_2d/pe.csl](file://LIB/collectives_2d)

### Inferences
- Builtin naming follows a pattern: `f`=float, a trailing `s` = single (f32) and `h` = half (f16), `16/32` = integer width. So `@fmacs` = f32 multiply-accumulate, `@faddh` = f16 add (the topic-11 symbol name "faddh_result" hints at this). This is my reading of the pattern; verify against the builtin reference before teaching it as a rule.
- A DSD is a hardware loop descriptor held in a DSR register. The DSR allocator mentioned in topic-15 maps DSD values to DSRs, so DSDs that are not known at compile time cost DSRs.

### Gaps
- `mem4d_dsd` is not used in any tutorial I read, so its fields (multi-dimensional `tensor_access` with up to 4 induction variables) could not be confirmed locally. The complete DSD-op table (e.g. `@fmuls`, `@fsubs`, `@fmaxs`, `@xp162fs`) and operand-type rules are online-only.

---

## 5. Routing: colors, rx/tx, RAMP, switches, filters

### Takeaway
Each PE's router has 24 colors (virtual channels). For each color, `@set_color_config(x, y, color, .{ .routes = .{ .rx = .{...}, .tx = .{...} } })` statically says which links (`NORTH/SOUTH/EAST/WEST/RAMP`) the color receives from and transmits to. RAMP is the link between the router and that PE's own CE. Runtime flexibility comes from **switches** (up to 4 route positions, advanced by control wavelets) and **filters** (accept only some wavelets to the CE).

### Cited Findings
- "To send data from the left PE to the right PE, we must specify a route, known as a color. ... on the left PE, color 0 will receive data, or wavelets, from the compute element (CE) up the RAMP, and transmit them to the EAST. On the right PE, color 0 will receive wavelets from the WEST, and then transmit them down the RAMP to the CE." — [gemv-06 README](file://EX/tutorials/gemv-06-routes-1/README.rst)
  ```csl
  const send_color: color = @get_color(0);
  @set_color_config(0, 0, send_color, .{.routes = .{ .rx = .{RAMP}, .tx = .{EAST} }});
  @set_color_config(1, 0, send_color, .{.routes = .{ .rx = .{WEST}, .tx = .{RAMP} }});
  ```
- Multicast: `.tx = .{RAMP, SOUTH}` delivers to the local CE and forwards south in one route. This is the column broadcast of x in gemv-07/08. — [gemv-08 layout.csl](file://EX/tutorials/gemv-08-routes-3/layout.csl)
- The checkerboard pattern is needed because "we cannot safely send and receive multiple wavelets on the same color with a fixed routing." gemv-08 alternates `ax_color_1`/`ax_color_2` by column parity. game-of-life uses 8 colors (east/west/north/south × 2 parities). — [gemv-08 README](file://EX/tutorials/gemv-08-routes-3/README.rst), [game-of-life layout.csl](file://EX/benchmarks/game-of-life/layout.csl)
- Switches:
  ```csl
  @set_color_config(1, 1, channel, .{
    .routes = .{ .rx = .{ RAMP }, .tx = .{ NORTH } },
    .switches = .{ .pos1 = .{ .tx = WEST }, .pos2 = .{ .tx = EAST }, .pos3 = .{ .tx = SOUTH },
                   .current_switch_pos = 1, .ring_mode = true } });
  ```
  The sender emits `ctrl.encode_single_payload(ctrl.opcode.SWITCH_ADV, true, {}, 0)` on a `.control = true` fabout DSD. "Switches can be helpful ... to save the number of colors used". — [topic-06 README / layout.csl / send.csl](file://EX/tutorials/topic-06-switches/)
- Switch timing: "a PE router will move to a new switch position only after the control wavelet carrying the switch command passes through that PE ... the data payload of a control wavelet is received by the PE connected by the current switch position, not the new position." — [topic-07 README](file://EX/tutorials/topic-07-switches-entrypt/README.rst)
- Range filters: `.filter = .{ .kind = .{ .range = true }, .min_idx = pe_id*3, .max_idx = pe_id*3+2 }` in `@set_color_config`. Filters accept "wavelets to allow to be forwarded to the CE based on the upper 16 bits of the wavelet contents". WSE-3 filter registers include `DROP_COUNT`, `MAX_PASS`, `COUNTER`; WSE-2 has `MAX_COUNTER`, `COUNTER`. WSE-2 has two filter banks, WSE-3 one. — [topic-08 README / layout.csl](file://EX/tutorials/topic-08-filters/), [LIB/target/wse2.csl, wse3.csl](file://LIB/target)
- Switch hardware detail: `SWITCH_REGS_PER_COLOR` is 1 on WSE-2 and 4 on WSE-3. — [LIB/target](file://LIB/target)
- Within a PE program, `@set_local_color_config(color, .{.routes = ...})` sets routes for the current PE. — [topic-16 sender](file://EX/tutorials/topic-16-queue-flush/queue_flush_sender.csl)
- Do not route memcpy colors yourself: "The routing of the color MEMCPYH2D_DATA_1 must not be defined. The memcpy module will figure out the routing". — [topic-03 README](file://EX/tutorials/topic-03-streaming-wavelet-data/README.rst)
- Loopback trick: "a PE starts a wavelet-triggered task using its own wavelets, by sending them to the router which immediately sends them back to the compute element" (route RAMP→RAMP). — [topic-09 README](file://EX/tutorials/topic-09-fifos/README.rst), [pipeline-02 README](file://EX/tutorials/pipeline-02-fifo/README.rst)
- `cslc-driver --out-routes` will "Show per-PE color and routing information". `cs_readelf` has `--routing` and `--switching` options. — tool `--help` (local experiment)

### Inferences
- The routing model to teach: a wavelet = 32-bit payload + color. Per PE and per color, the router has a static "rx set → tx set" table, and RAMP is just a fifth port. Colors are a scarce shared resource: 24 total, with memcpy taking 21–23 (plus 20 for context switch). Hence the use of switches, filters and SdkLayout's automatic color allocation.

### Gaps
- Wavelet-level details (wavelet size in bits including color/control bits, link bandwidth per cycle, router buffer depths) are not stated in the local sources.

---

## 6. Host side: SdkRuntime, memcpy, launch, streaming vs copy; SdkLayout

### Takeaway
The host imports `SdkRuntime, MemcpyDataType, MemcpyOrder` from `cerebras.sdk.runtime.sdkruntimepybind`. The sequence is: construct with the compile dir, `get_id(symbol)`, `load()`, `run()`, then any mix of `memcpy_h2d` / `launch` / `memcpy_d2h`, then `stop()`. Commands are serialized. **Copy mode** writes into exported arrays on a PE rectangle. **Streaming mode** pushes wavelets on the `MEMCPYH2D_*`/`MEMCPYD2H_*` colors into WTTs or fabric DSDs. `SdkLayout` is a newer Python-side layout API that replaces `layout.csl` with code regions, symbolic colors, ports and automatic routing.

### Cited Findings
- Canonical host script (gemv-03):
  ```python
  from cerebras.sdk.runtime.sdkruntimepybind import SdkRuntime, MemcpyDataType, MemcpyOrder
  runner = SdkRuntime(args.name, cmaddr=args.cmaddr)   # cmaddr None -> simulator
  A_symbol = runner.get_id('A')
  runner.load(); runner.run()
  runner.memcpy_h2d(A_symbol, A, 0, 0, 1, 1, M*N, streaming=False,
    order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
  runner.launch('init_and_compute', nonblock=False)
  y_result = np.zeros([M], dtype=np.float32)
  runner.memcpy_d2h(y_result, y_symbol, 0, 0, 1, 1, M, streaming=False,
    order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
  runner.stop()
  ```
  Arguments: "(starting x-coord, starting y-coord, width, height) of rectangle of PEs ... M is number of elements to be copied from each PE". — [gemv-01 run.py](file://EX/tutorials/gemv-01-complete-program/run.py), [gemv-03 run.py](file://EX/tutorials/gemv-03-memcpy/run.py)
- Multi-PE data layout is the host's job. gemv-08 reshapes A so each PE gets a contiguous column-major block: `A.reshape(kernel_y_dim, M_per_PE, kernel_x_dim, N_per_PE).transpose(0, 2, 3, 1).ravel()`, then calls `memcpy_h2d(A_symbol, A_prepared, 0, 0, kx, ky, M_per_PE*N_per_PE, ...)`. Compile-time params are read back from `out/out.json` (`compile_data['params']['M']`). — [gemv-08 run.py](file://EX/tutorials/gemv-08-routes-3/run.py)
- Streaming mode: the color IDs are params (`--params=MEMCPYH2D_DATA_1_ID:0`, ...) passed into `<memcpy/get_params>` as `.MEMCPYH2D_1 = ...`. The host passes the color ID instead of a symbol: `runner.memcpy_h2d(MEMCPYH2D_DATA_1, x, 0, 0, kernel_x_dim, 1, N_per_PE, streaming=True, ...)`. On WSE-2 the device gets the color as `@get_color(@bitcast(u16, sys_mod.MEMCPYH2D_1))`. "because memcpy commands are serialized, the order of these streaming mode memcpy_h2d calls ... is important. If the b values were streamed in before x, the program would hang." There is no explicit launch: "computation is started by the wavelet-triggered tasks". — [gemv-09 README / run.py / pe_program.csl](file://EX/tutorials/gemv-09-streaming/)
- D2H streaming on the device uses `sys_mod.get_streaming_fabout_dsd(@get_color(@bitcast(u16, sys_mod.MEMCPYD2H_1)), size, d2h_1_oq)` or a hand-built fabout DSD on that color. — [pipeline-01 pe_program.csl](file://EX/tutorials/pipeline-01-basic/pe_program.csl)
- Python API surface (introspected in the container, local experiment):
  - `SdkRuntime` methods: `call(name, np.uint32 array)`, `coord_logical_to_physical`, `dump_core`, `dump_elf_core`, `get_id`, `get_port_id`, `is_task_done(task)`, `launch(name, *args, **kwargs)`, `load`, `memcpy_d2h`, `memcpy_h2d`, `memcpy_h2d_colbcast`, `memcpy_h2d_rowbcast`, `memcpy_h2d_stride`, `read_symbol(x, y, symbol_name, dtype='uint8')`, `receive`, `receive_tofile`, `report_port_infos`, `run`, `send`, `stop`, `task_wait(task)`.
  - Enums: `MemcpyDataType ∈ {MEMCPY_32BIT, MEMCPY_16BIT}`, `MemcpyOrder ∈ {ROW_MAJOR, COL_MAJOR}`.
  - Module also exports `SdkLayout, CodeRegion, Color, Route, RoutingPosition, Edge, SdkTarget(WSE2/WSE3), SimfabConfig, get_platform, get_simulator, get_system, get_edge_routing`.
  - The memcpy calls return a `Task` handle, so `nonblock=True` plus `task_wait` is the async pattern.
- 16-bit memcpy example: `data_type=MemcpyDataType.MEMCPY_16BIT, order=MemcpyOrder.COL_MAJOR` reading `u16` timestamps into a `np.uint32` host array. — [conjugate-gradient run.py](file://EX/benchmarks/conjugate-gradient/run.py)
- Broadcast H2D: `memcpy_h2d_rowbcast()` streams one column of data to every PE in each row (and `colbcast` the reverse), avoiding "wastes host bandwidth by 3x". "The new broadcasting scheme only supports H2D, not D2H." — [row-col-broadcast README](file://EX/benchmarks/row-col-broadcast/README.rst)
- Host-bandwidth measurement relies on device TSC counters, not host timers, because "the runtime can aggregate multiple nonblocking commands together to reduce TCP overhead". The benchmark converts cycles with `time = cycles/0.85 * 1e-3 us` and supports `--channels` "no bigger than 16". — [bandwidth-test README](file://EX/benchmarks/bandwidth-test/README.rst)
- SdkLayout (tutorials sdklayout-01..05). Features: "Creation of CSL code regions", "Routing and switching", "Automatic color allocation", "Automatic routing between code regions" via ports, and "Host-to-device and device-to-host connections".
  ```python
  platform = get_platform(args.cmaddr, SimfabConfig(dump_core=True), SdkTarget.WSE3)
  layout = SdkLayout(platform)
  code = layout.create_code_region('./send_receive.csl', 'send_receive', 2, 1)
  c = Color('c')                                  # symbolic color
  code.paint(IntVector(0,0), c, [RoutingPosition().set_input([Route.RAMP]).set_output([Route.EAST])])
  code.paint(IntVector(1,0), c, [RoutingPosition().set_input([Route.WEST]).set_output([Route.RAMP])])
  code.set_param_all(c)                           # physical color id passed as u16 param
  artifacts = layout.compile(out_prefix='out')
  rt = SdkRuntime(artifacts, platform, memcpy_required=False)
  rt.load(); rt.run(); rt.stop()
  rt.read_symbol(1, 0, 'buffer', dtype='uint16')
  ```
  - The compiler emits `colors.json` with the allocated physical colors.
  - Ports: `create_output_port(color, Edge.RIGHT, [routes], size)` / `create_input_port(...)`, then `layout.connect(tx_port, rx_port)` "will automatically find and encode a path".
  - Streams: `layout.create_input_stream(port)` / `create_output_stream(port)` with `runtime.send(stream, data, nonblock=True)` / `runtime.receive(stream, out, size, nonblock=True)`. Streams are only for single-PE ports, so multi-PE ports need explicit demux/mux adaptor regions (sdklayout-05 GEMV).
  - `CodeRegion` also has `place(x,y)`, `set_param(coord,...)`, `set_param_range`, `paint_all`, `paint_range`, `set_symbol_all('A', A, ...)`. `SdkLayout` also has `hstack`/`vstack`.

  — [sdklayout-01..05 READMEs and run.py](file://EX/tutorials/)

### Inferences
- The copy-vs-streaming distinction to teach: copy mode = host writes or reads a named symbol's memory on a rectangle of PEs; device code isn't involved beyond exporting the symbol and unblocking after RPCs. Streaming mode = host injects wavelets that device tasks must consume (or that device code must produce, for D2H). It is more flexible, but ordering mistakes cause hangs.
- SdkLayout programs in these tutorials use `memcpy_required=False`. They communicate through streams/ports or `read_symbol` rather than the memcpy command stream, and their PE code does not import `<memcpy/memcpy>`.

### Gaps
- Semantics of `MemcpyOrder.COL_MAJOR` for multi-PE copies (how host array dimensions map to (px, py, element)) are only implied by benchmark helper names (`oned_to_hwl_colmajor`). No authoritative description is available locally.
- `call()` vs `launch()`, and `memcpy_h2d_stride`, are not covered in the tutorials.

---

## 7. Toolchain: cslc flags, artifacts, cs_python, simulator outputs, csdb, cs_readelf, debug libraries

### Takeaway
`cslc` (a wrapper around a containerised `cslc-driver`) compiles a layout file into `out/` (per-PE ELFs plus memcpy halo ELFs plus JSON metadata). `cs_python run.py --name out` runs the host script against the simulator, which writes `sim.log`, `sim_stats.json`, `simconfig.json` and CTF traces in `simfab_traces/` to the current directory. The trace tools are `csdb`, `sdk_debug_shell visualize`, `cs_readelf`, and the device libraries `<debug>` (trace buffers read by the host) and `<simprint>` (prints to sim.log).

### Cited Findings
- Standard compile and run (gemv-01 `commands_wse3.sh`):
  ```bash
  cslc --arch=wse3 ./layout.csl --fabric-dims=8,3 --fabric-offsets=4,1 -o out --memcpy --channels 1
  cs_python run.py --name out
  ```
  gemv-04 adds `--params=M:4,N:6`. gemv-08 uses `--fabric-dims=11,5 --params=kernel_x_dim:4,kernel_y_dim:3,M:6,N:8`. — [gemv-01/04/08 commands_wse3.sh](file://EX/tutorials/)
- `cslc` wrapper options: `-o OUTPUT_NAME` (default `out`), `--params`, `--colors`, `--memcpy` ("Add memcpy support"), `--channels` ("Number of memcpy I/O channels ... If ... 0, then the previous single-I/O channel version is compiled"), `--import-path`, `--width-west-buf`/`--width-east-buf` ("buffer to mitigate slow input/output"), `--verbose`. Unrecognised options are forwarded to `cslc-driver`. — `cslc --help` (local experiment)
- `cslc-driver` options: `--arch=wse2|wse3` ("Default=wse2"; wse1 retired), `--fabric-dims`, `--fabric-offsets`, `--fp16-format`, `--out-routes`, `--output-json`, `--single-pe`, `--max-inlined-iterations`, `--comptime-func-depth-limit`, `--disable-auto-microthread-id`, `--dump-dsr-alloc-graph`, `--lomem-reservation-end`, `--warnings-as-errors`, `--g0` ("Turn off debug information"), and experimental `--separate-compilation`. — cslc-driver `--help` (local experiment)
- Artifacts observed (local experiment, gemv-01, WSE-3): `out/out.json` = `{"params":{},"colors":{}}` (gemv-08: `{"params":{"kernel_x_dim":"4","kernel_y_dim":"3","M":"6","N":"8"},...}`); `out/bin/out_0_0.elf`; `out/bin/out_rpc.json`; `out/west/bin/out_{0..2}_0.elf`; `out/east/bin/out_{0,1}_0.elf`; `out/generated/{default,coord,MEMCPY_XY_ROUTES}.elf`.
- Simulator outputs (local experiment): `sim.log`, `sim_stats.json`, `simconfig.json`, `simfab_traces/{global_simdata.json, metadata, stream0}`.
  - `sim.log` records ELF loading, `dimX=8, dimY=3`, the per-tile trace flags (`inst_trace,landing,stalls`), the architecture name, and the stop reason.
  - The architecture name printed is `FYN` for `--arch=wse2` and `SDR` for `--arch=wse3`. These read as internal codenames; the memcpy library comment "memcpy reserves queue 1 on SDR" is consistent with SDR = WSE-3.
  - Stop reason example: `No data movement in the last 50 cycles; stopping.` CTF stats include `num_wavelets=164`, `num_inst_dispatch=1274`.
  - `sim_stats.json` example: `"cycle_count": 1374, "fabric_x": 8, "fabric_y": 3, "hwtile_count": 10, "iotile_count": 4, "nultile_count": 32, "sim_stop_cause": "Stopped due to idleness", "threads": 5`.
- Measured cycle counts (local experiment):

  | Example | WSE-2 cycles | WSE-3 cycles |
  |---|---|---|
  | gemv-01 | — | 1374 |
  | gemv-08 (4×3 PEs, 11×5 fabric) | 4023 | 4539 |
  | topic-13 | — | 2966 |

  The simulation took about 2 s of wall time for gemv-01. The cycle counts include memcpy overhead, not just the kernel.
- Environment gotcha (local experiment): `cs_python` runs `singularity exec -C --bind=$PWD --bind=$TMPDIR:/tmp`. Running from a directory under `/tmp` fails with "destination ... doesn't exist in container", because `/tmp` is replaced by the bind. I ran the copied examples from `/home/user/cerebras-sdk/tmp/claude-work/` instead. Compilation under `/tmp` did succeed.
- Debug tools:
  - `sdk_debug_shell` has subcommands `instr-trace` (tasks/trace/uthreads for `--x --y`), `wavelet-trace` (`--color 0..23`, `--fmt i16|f16|f32|hex`, `--backpressure`), `visualize` ("Visualize routing between PEs, post-simulation run results ... in a web browser") and `smoke`.
  - In 2.10.1, `instr-trace` and `wavelet-trace` print "sdk_debug_shell does not support ctf trace debug, please use csdb" because the simulator emits CTF traces.
  - `csdb [WORKDIR] COMMAND` has subcommands `context, image (info/list/lookup), memory (read/write), rectangle, register, settings, target ("Connect to CM for interactive debugging or examine a core file"), trace (list/select/show), wavelet, workdir`.

  — tool `--help` and runs (local experiment)
- `cs_readelf` is a "GNU Readelf analog for inspecting Cerebras ELFs". Options: `-s/--fs` (fabric size), `--sym/--symbols`, `-m/--msize`, `--routing`, `--switching`, `--tile X,Y`, `--minr/--maxr`, `--mbase/--mlen`, `--xp`, `--visualize`, `-t/--arch`. Example: `cs_readelf --syms out/bin/out_0_0.elf` lists `y` at 0xb60, size 16 bytes, and memcpy internals (`sys_mod.sys_mod.memcpyH2D_px`, ...). — local experiment
- `<debug>` library: `@import_module("<debug>", .{ .key = "trace", .buffer_size = 100 })`. API: `trace_string(comptime str)`, `trace_u16/i16/u32/i32/f16/f32/bool/u8/i8`, `trace_timestamp()`, `put_u16/u32`, `tagged_put_u8`. The host side is `from cerebras.sdk.debug.debug_util import debug_util; debug_mod = debug_util(dirname, cmaddr=...); debug_mod.read_trace(x, y, 'trace')`, and "the PE coordinates passed to read_trace start from the northwest corner of the fabric, not from the northwest corner of the program rectangle" (hence `core_offset_x = 4`). — [topic-12 README / receiver.csl / run.py](file://EX/tutorials/topic-12-debug-library/), [LIB/debug.csl](file://LIB)
- `<simprint>` library: `print_string`, `print_u16_decimal/hex/binary`, `print_u32_*`, `print_f16`, `print_f32`, `fmt(fstr, args)`, `fmt_no_nl`, `fmt_with_coords`; `param enable: bool = true`. "The output is flushed to sim.log whenever a newline is encountered", and each line is prefixed with the cycle. It is "particularly useful for debugging stalling programs", because `<debug>` "requires a program to complete". Observed output (local run): `@1475 PE(0,0): sender beginning main_fn`, `@1606 PE(1,0): recv_task: in_data = 0, global = 0`. — [topic-13 README](file://EX/tutorials/topic-13-simprint/README.rst), [LIB/simprint.csl](file://LIB), local experiment

### Inferences
- The "what happens internally" story for a course, assembled from the artifacts above:
  1. `cslc` evaluates `layout.csl` at compile time, instantiating each `@set_tile_code` with its params.
  2. It compiles each unique PE program to an ELF.
  3. With `--memcpy`, it adds west and east halo kernels (command fan, H2D demux, D2H mux) plus generated routing ELFs, and writes `out_rpc.json` mapping exported names to IDs.
  4. `SdkRuntime.load()` loads all ELFs into the simulator (or the CS system).
  5. `run()` starts the fabric.
  6. Each `memcpy`/`launch` becomes a command on the RXCOMMAND color, which memcpy's control tasks (IDs 33–36) decode.
  7. The simulator stops after 50 idle cycles once the host stops.

### Gaps
- csdb's interactive trace-inspection workflow (exact `csdb trace select` / instruction-trace commands in the CTF era) was not exercised end to end. Only the help screens were verified.
- The "SDK GUI/visualizer": `sdk_debug_shell visualize` exists and the container has `/cbcore/web/csviz` and `csviz` binaries, but I did not launch the browser UI. The `sdk-gui-LICENSE.txt` in the SDK root suggests a GUI component.
- How to enable or disable specific simulator traces (`SimfabConfig` fields other than `dump_core`, and environment variables) was not found locally.

---

## 8. Library modules

### Takeaway
The standard libraries (inside the image at `LIB`) include `<memcpy/*>`, `<layout>`, `<math>`, `<random>`, `<time>`, `<timer>`, `<debug>`, `<simprint>`, `<collectives_2d/*>`, `<control>`, `<tile_config>`, `<message_passing>`, `<malloc>`, `<complex>`, `<string>`, `<dsd_ops>`, `<directions>`, `<types>`, `<data_utils>`, plus kernels (`kernels/fft`, `kernels/tally`).

### Cited Findings
- Library directory listing (local experiment): `collectives_2d/{params,pe,ctrl_wavelet}.csl, complex.csl, control.csl, data_utils.csl, debug.csl, directions.csl, dsd_ops.csl, layout.csl, malloc.csl, math.csl, memcpy/{get_params,memcpy,memcpy_switches,sys_params}.csl (+wse2/, wse3/), message_passing.csl, random.csl, simprint.csl, string.csl, target/{common,wse2,wse3}.csl, tile_config.csl (+color_config, switch_config, input/output_queue_config, queue_flush, teardown, exceptions, task_priority, filters/...), time.csl, timer.csl, types.csl, kernels/fft, kernels/tally, runtime/*`. — [LIB](file://LIB)
- `<math>` functions (each with `_f16`/`_f32` variants plus a generic form): `abs, ceil, floor, cos, sin, exp, log, pow, sqrt, invsqrt, inv, tanh, sig, sign, signbit, min, max, fscale, subsat`. — [LIB/math.csl](file://LIB)
- `<random>`: `set_global_prng_seed, set_global_seed_for_prng_id, random_f16, random_f32, random_pow_u32, random_normal_f32`. The hardware has `prng_count = 4`. — [LIB/random.csl, LIB/target/common.csl](file://LIB)
- `<time>`: `tsc_size_words`, `enable_tsc()`, `disable_tsc()`, `get_timestamp(*[3]u16)`, `reset_tsc_counter()`, `get_perf_cntr(*[3]u16, id)`. topic-02 uses it to time a Monte-Carlo π loop and exports the start/finish buffers. — [LIB/time.csl](file://LIB), [topic-02 pe_program.csl](file://EX/tutorials/topic-02-libraries/pe_program.csl)
- `<collectives_2d>`: in the layout, `c2d.get_params(Px, Py, .{ .x_colors = .{c0, c1}, .x_entrypoints = .{t0, t1}, .y_colors = ..., .y_entrypoints = ... })` (2 colors + 2 local task IDs per dimension). In the PE, `@import_module("<collectives_2d/pe>", .{ .dim_params = c2d_params.x, .queues = [2]u16{2,4}, .dest_dsr_ids = [1]u16{1}, ... })`. API: `init()`, `broadcast(root, buf, n, callback_task)`, `scatter(root, send, recv, chunk, cb)`, `gather(root, send, recv, chunk, cb)`, `reduce_fadds(root, send, recv, n, cb)`, and `pe_id`. The library "mimics ... MPI collective operations". Calls are asynchronous and chained through a state machine in a callback task. — [topic-11 README / layout.csl / pe_program.csl](file://EX/tutorials/topic-11-collectives/), [LIB/collectives_2d/pe.csl](file://LIB/collectives_2d)
- `<control>`: `opcode` enum (e.g. `SWITCH_ADV`), `encode_single_payload(cmd, ce_ignore, entrypoint, data)`, `encode_payload(N, cmds, ce_ignore, ...)`, `encode_control_task_payload(entrypoint)`; `MAX_CMDS = 8`. — [LIB/control.csl](file://LIB)
- `<message_passing>` params: `enable_asserts`, `bank_id: u16 = 14` ("Default is A (base=14), note that B (base=19) clashes with memcpy"), `input_queue_id`, `output_queue_id`. — [LIB/message_passing.csl](file://LIB)
- `<malloc>` is an arena allocator over a static buffer (`param buffer_num_words`): `malloc_` functions for i16/u16/fp16/i32/u32/f32, free-all, `has_enough_*`. — [LIB/malloc.csl](file://LIB)
- `<tile_config>` gives low-level access to the queue/color/switch/filter registers, used e.g. for `queue_flush` and `output_queue_config` in topic-16. — [topic-16](file://EX/tutorials/topic-16-queue-flush/)

### Inferences
- For a course, the libraries worth teaching in depth are `<memcpy>`, `<layout>`, `<time>`, `<simprint>`/`<debug>` and `<collectives_2d>`. The rest (`tile_config`, `control`) are "escape hatches" for advanced routing.

### Gaps
- `<kernels/fft>`, `<kernels/tally>`, `<timer>`, `<complex>`, `<dsd_ops>` APIs were not examined in detail.

---

## 9. Common patterns (GEMV, broadcast, systolic/streaming, reductions, halo-exchange stencils) and the tutorial/benchmark map

### Takeaway
The gemv-00..09 series is the canonical course spine: syntax → single-PE program → memory DSDs → memcpy → params → multi-PE replication → routes and fabric DSDs → 2×2 broadcast and reduce → general k×k with checkerboard colors → streaming mode. The pipeline-*, topic-* and sdklayout-* tutorials each isolate one mechanism. The benchmarks show production-scale patterns (stencils, CG/BiCGSTAB, FFT, GEMM, SpMV, histogram).

### Cited Findings
- Tutorial map (what each teaches):
  - **gemv-00**: types, `fn`, loops; not a full program.
  - **gemv-01**: complete program with layout, memcpy, export and `unblock_cmd_stream`.
  - **gemv-02**: `mem1d_dsd`, `tensor_access`, `@fmacs`/`@fadds`, `@increment_dsd_offset`.
  - **gemv-03**: `memcpy_h2d`.
  - **gemv-04**: `param` + `--params`.
  - **gemv-05**: multiple PEs with replicated work; `np.tile` on the host.
  - **gemv-06**: first route/color, fabin/fabout, async ops with `.activate`, local task.
  - **gemv-07**: 2×2, x broadcast down columns via WTT, `reduce` local task, `<layout>` coordinates.
  - **gemv-08**: arbitrary kernel_x×kernel_y with checkerboard colors for the west→east reduction chain.
  - **gemv-09**: memcpy streaming mode with no launch.

  — [gemv READMEs](file://EX/tutorials/)
- Pipelines and SdkLayout:
  - **pipeline-01**: fabin→fabout redirect; stalls above 14 wavelets.
  - **pipeline-02**: a FIFO decouples H2D from compute.
  - **pipeline-03**: an "artificial halo" of west/east PEs holds the FIFOs instead of the kernel.
  - **sdklayout-01..05**: SdkLayout intro, symbolic routing, ports/connections, host streams, full GEMV with demux/mux adaptors.

  — [pipeline-*, sdklayout-* READMEs](file://EX/tutorials/)
- Topic tutorials:
  - **topic-01**: arrays/pointers. **topic-02**: `<random>`, `<time>`, `<math>`. **topic-03**: streaming WTT.
  - **topic-04**: index in the upper 16 bits for sparse data. **topic-05**: sentinel control tasks.
  - **topic-06**: switches. **topic-07**: switches with control entrypoints. **topic-08**: range filters.
  - **topic-09**: FIFOs and loopback. **topic-10**: `@map`. **topic-11**: `<collectives_2d>`.
  - **topic-12**: `<debug>`. **topic-13**: `<simprint>`.
  - **topic-14**: color swap (WSE-2 only). **topic-15**: WSE-3 microthread IDs. **topic-16**: WSE-3 `@queue_flush` for output-queue reuse.

  — [topic READMEs](file://EX/tutorials/)
- Broadcast pattern: the source PE sends on a color whose route is `rx RAMP, tx {RAMP, SOUTH}`, middle rows use `rx NORTH, tx {RAMP, SOUTH}`, and the last row uses `rx NORTH, tx RAMP`. Every PE's WTT fires per element (gemv-08). The host-side alternative is `memcpy_h2d_rowbcast/colbcast`. — [gemv-08 layout.csl](file://EX/tutorials/gemv-08-routes-3/layout.csl), [row-col-broadcast README](file://EX/benchmarks/row-col-broadcast/README.rst)
- Systolic reduction chain: the leftmost column sends `y`, middle columns `@fadds(out_dsd, y_dsd, in_dsd)` (receive, add, forward in one op), and the rightmost column `@fadds(y_dsd, y_dsd, in_dsd)`. Colors alternate by column parity. — [gemv-08 pe_program.csl](file://EX/tutorials/gemv-08-routes-3/pe_program.csl)
- Reductions via the library: `reduce_fadds` in `<collectives_2d>`; GEMV built from scatter/broadcast/reduce in `benchmarks/gemv-collectives_2d`. — [topic-11](file://EX/tutorials/topic-11-collectives/), [gemv-collectives_2d README](file://EX/benchmarks/gemv-collectives_2d/README.rst)
- Halo exchange:
  - game-of-life, one cell per PE: "each PE sends its state to its four N, S, E, and W neighbors ... and also forwards the received state from its N and S neighbors to its E and W neighbors. Thus, each PE receives from its E and W links both the state of its E and W adjacent neighbors, as well as its four diagonal neighbors." It uses 8 colors (4 directions × 2 parities).
  - 25-pt-stencil (with `oned_exch.csl`, `switches.csl`, `routes.csl`): "uses 21 colors and task IDs for communication patterns, and SdkRuntime reserves 6 colors, so only 4 colors are left". It is launched with an RPC argument (`iterations`).

  — [game-of-life README / layout.csl](file://EX/benchmarks/game-of-life/), [25-pt-stencil README](file://EX/benchmarks/25-pt-stencil/README.rst)
- Benchmarks present in 2.10.1: 25-pt-stencil, 7pt-stencil-spmv, bandwidth-test, benchmark-libs, bicgstab, cholesky, conjugate-gradient, fft-1d-2d, fft-3d, game-of-life, gemm-collectives_2d, gemv-checkerboard-pattern (FP16), gemv-collectives_2d, histogram-torus, mandelbrot, power-method, preconditioned-conjugate-gradient, residual, row-col-broadcast, single-tile-matvec, spmv-hypersparse, wide-multiplication. — [benchmarks listing](file://EX/benchmarks)

### Inferences
- Suggested course ordering: gemv-01 → 02 → 04 → 06 → 07 → 08 (core concepts), then topic-03/05/09 (event-driven streaming), topic-12/13 (debugging), topic-06/08/11 (advanced routing and collectives), and topic-15/16 plus WSE-3 queue rules as an "architecture differences" module. SdkLayout can be taught last as the higher-level alternative.
- Each tutorial ships both `commands_wse2.sh` and `commands_wse3.sh`, except topic-14 (WSE-2 only) and topic-15 (WSE-3 only). Running the same program on both and diffing cycle counts (e.g. gemv-08: 4023 vs 4539 cycles) is a concrete lab exercise.

### Gaps
- Papers that describe CSL programs (e.g. stencil/CFD or MD work on the WSE) and the Cerebras GitHub `csl-examples` repo were not consulted, because external fetches to sdk.cerebras.net failed and time was spent on the authoritative local sources. The local extras tarball (`csl-extras-202604101435`) appears to be the same content as the GitHub repo's examples, but I did not verify this.
- The per-PE memory size is stated only in a recurring code comment, "48 kB of global memory contain A, x, b, y" ([gemv-01 pe_program.csl](file://EX/tutorials/gemv-01-complete-program/pe_program.csl)). I found no separate official statement locally, nor a WSE-3 specific figure.
