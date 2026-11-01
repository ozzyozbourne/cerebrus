# ch09 · pedagogy review

Summary: The chapter gives a good map: three files in three places, a line-by-line tour of SAXPY, the compile-to-simulate pipeline and the debugging tools. It works as an orientation chapter. It does not yet work as the chapter where a learner learns to write a program. Four things are missing:
- The tour leaves out the host boilerplate (imports, the `kw` dict, reading params from `out.json`).
- There is no "names must match across files" checklist.
- The `--fabric-dims`/`--fabric-offsets` values are given as magic numbers.
- The "Set up the SDK" objective assumes the SDK tarball and a repo-internal script are already there.

The resource types are listed but never mapped to the chapters that define them, and two "Check yourself" questions rely on things the chapter never introduces. After this chapter a learner could copy SAXPY and change it. They could not write a new program from scratch until Lab 1 (ch10).

## Findings

### P1 [major] The run.py tour leaves out lines a learner needs to write a host script
Location: Guided tour, `run.py` tab (the `files["run.py"]` array in the inline script).
Problem: The tour starts at `rt = SdkRuntime(...)`. It leaves out four things from `course/programs/01-saxpy/run.py`:
- the import line (`from cerebras.sdk.runtime.sdkruntimepybind import SdkRuntime, MemcpyDataType, MemcpyOrder`);
- the `--name/--cmaddr` argparse;
- `N = int(json.load(open(f"{args.name}/out.json"))['params']['N'])`;
- the `kw = dict(streaming=False, order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)` line.

The memcpy lines then use `**kw`, which is never defined. The objective "Read every line of a complete CSL program" is therefore not met for the host file.
Why it matters: The host script is the part a learner is most likely to write from memory, since it is Python. If they copy from the tour, it will not run.
Concrete fix: Add these lines to the top of the run.py tour, each with a note:
- `from cerebras.sdk.runtime.sdkruntimepybind import SdkRuntime, MemcpyDataType, MemcpyOrder` → "The host API. Run the script with `cs_python`, not plain `python`: the module only exists inside the SDK container."
- `N = int(json.load(open(f"{args.name}/out.json"))['params']['N'])` → "cslc writes the params it was given into `out/out.json`. Reading them back keeps host and device in agreement about N."
- `kw = dict(streaming=False, order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)` → "`streaming=False` = copy mode (write into an exported array; see ch07). `ROW_MAJOR` = how the host array maps onto the PE rectangle. `MEMCPY_32BIT` = element size. `nonblock=False` = the call returns only when the copy is done."

Also extend the note on `memcpy_h2d` with the argument order: "(symbol, host array, x0, y0, width, height, elements per PE, …)".

### P2 [major] No checklist for writing a first program: names must match across three files
Location: After the guided tour, before "The language in one screen".
Problem: The tour shows that `"x"` appears in `@export_name` (layout), `@export_symbol` (device) and `rt.get_id('x')` (host). It also shows that every RPC must call `unblock_cmd_stream()`. But these facts are scattered across click-to-reveal notes, and the chapter never pulls them together.
Why it matters: This is exactly what a learner needs before they write program #2. It is also where the chapter's own "most bugs are resource bugs" callout says the mistakes happen.
Concrete fix: Add a short callout headed "Writing your own: the contract between the three files", containing this list:
1. Every array the host touches: `@export_name("name", [*]T, mutable)` in layout.csl; a `[*]T` pointer (`var` if mutable is `true`, `const` if `false`) and `@export_symbol(ptr, "name")` in pe_program.csl; `rt.get_id('name')` in run.py.
2. Every host-callable function: `@export_name("f", fn(args)void)` in layout.csl; `fn f(...)` plus `@export_symbol(f)` in pe_program.csl; `rt.launch('f', ...)` in run.py.
3. Every RPC must end, directly or through a task it starts, with `sys_mod.unblock_cmd_stream()`.
4. Every `param` declared in pe_program.csl must be passed in `@set_tile_code`'s struct. Every `param` declared in layout.csl must be given with `--params`.
5. Keep your own colors, queues and task IDs away from what memcpy reserves (ch07 table).

### P3 [major] The `--fabric-dims` and `--fabric-offsets` values are magic numbers
Location: "From source to simulation" command block and the flag table.
Problem: A 1 × 1 program is compiled with `--fabric-dims=8,3 --fabric-offsets=4,1`, and the table only says "including memcpy's columns". The rule is never stated here. Ch07 explains the halo, and the SDK's single-tile-matvec README states the rule: width ≤ fabric x − 7, height ≤ fabric y − 2.
Why it matters: The first change a learner makes is a bigger rectangle. Without the rule they will guess and get a compile error.
Concrete fix: Replace the two table rows with:
- `--fabric-dims=W,H` → "size of the simulated fabric. With `--memcpy`, use at least (your width + 7, your height + 2): memcpy adds columns west and east of your rectangle, plus one row above and below (ch07). On a real CS system it must be the full fabric size."
- `--fabric-offsets=X,Y` → "where your rectangle's (0,0) sits. With `--memcpy`, always `4,1`."

Add one worked line under the command: "For an 8 × 4 rectangle: `--fabric-dims=15,6 --fabric-offsets=4,1`."

### P4 [major] The "Set up the SDK in a fresh Linux environment" objective is not delivered
Location: "Setting up the SDK" section; objective 3.
Problem: The section assumes the tarball is already there. It never says where the SDK comes from, which version or filename to expect, or what to unpack it into. It then sends the learner to `.claude/skills/cerebras-sdk/scripts/setup.sh`, an internal file of this repository that a course reader will not have. It also leaves out two steps that script performs:
- It writes an `env.sh` that adds the SDK directory to `PATH`.
- It sets `TMPDIR` to a directory outside `/tmp`, because cs_python fails under `/tmp` (the course's own brief notes this).

`env.sh` is used but its contents are never shown.
Why it matters: A learner on their own machine cannot follow the section, so the objective fails.
Concrete fix: Replace the two-item list with a numbered recipe:
1. "Obtain the SDK 2.10.1 tarball from Cerebras (it is distributed by Cerebras, not via a package manager) and unpack it into a directory, e.g. `~/cerebras-sdk`. It contains the wrapper scripts `cslc`, `cs_python`, `csdb`, `cs_readelf` and the `.sif` image. Unpack the `csl-extras-*.tar.gz` inside it to get the tutorials."
2. "Install a Singularity runtime (Ubuntu: `apt-get install singularity-container`)."
3. "Create `env.sh`:" followed by a code block:
```
export PATH=$HOME/cerebras-sdk:$PATH
export TMPDIR=$HOME/cerebras-sdk/tmp   # cs_python fails under /tmp
mkdir -p "$TMPDIR"
export SINGULARITY_DROP_CAPS=CAP_SYS_RESOURCE   # only if running as root without CAP_SYS_RESOURCE
```
4. "Smoke test: `cslc --help` and the SAXPY `commands.sh`."

Keep the note about the course's setup.sh, labelled "If you are using this course's repository".

### P5 [major] The resource types are listed without definitions or pointers back to earlier chapters
Location: "The language in one screen" → "Hardware parts", the resource-types bullet.
Problem: The bullet lists nine type names: `color`, `input_queue`, `output_queue`, `data_task_id`, `local_task_id`, `control_task_id`, `mem1d_dsd`, `fabin_dsd`, `fabout_dsd`. None is defined here, and the SAXPY tour uses only `mem1d_dsd`. Ch04–06 introduce most of them. Some never appear in a worked example before this chapter, for example `local_task_id` and `control_task_id` (grep of ch05 finds only `data_task_id`).
Why it matters: This chapter's summary claims that "its real content is a type system for hardware resources", but it shows only a list of names. A learner cannot tell which ones a first program needs.
Concrete fix: Replace the bullet with a three-column table: Type · What it names · First used.

| Type | What it names | First used |
|---|---|---|
| `color` | a virtual channel on the fabric | ch04, program 03 |
| `input_queue` / `output_queue` | the hardware FIFO between router and core (WSE-3 binds tasks and DSDs to these) | ch05, program 02 |
| `data_task_id` | a task woken by an arriving wavelet | ch05, program 02 |
| `local_task_id` | a task you activate yourself with `@activate` | ch05 |
| `control_task_id` | a task woken by a control wavelet (memcpy uses these) | ch07 |
| `mem1d_dsd` | a loop over SRAM | ch06, program 01 |
| `fabin_dsd` / `fabout_dsd` | a loop over wavelets from/to a queue | ch06, program 03 |

Then add: "For a first single-PE program you need only `mem1d_dsd`."

### P6 [major] "Check yourself" Q2 has an ambiguous premise and depends on something never taught
Location: Check yourself, question 2 ("You change a param from 8 to 16 PEs and compilation gets slower").
Problem: The question has three faults:
- Compile time grows only if the extra PEs get different params. If all 16 PEs share one param set, there is still one PE program. The premise as written ("change a param from 8 to 16 PEs") does not establish that, so the answer is not implied.
- The fix in the answer, "runtime coordinates from `<layout>`", refers to a library module that is not introduced in this chapter or in any lab. Only ch09 and ch15 mention it.
- It contradicts the course's own program 03, which uses per-PE `role` and color params on purpose.

Why it matters: A learner who answers correctly by reasoning ("same params → same ELF → no slowdown") is told they are wrong. The remedy points at something they cannot look up in the course.
Concrete fix: Replace the question with: "Program 03 passes each PE a `role` (first / middle / last) and a send/receive color chosen by column parity. For P = 16, how many distinct PE programs does cslc build, and why not 16?" Answer: "One per unique parameter combination: first, last, and middle-even/middle-odd (because the colors alternate), so about four, not 16. Compile time grows with the number of unique combinations, not with the PE count. If you passed `.x = x` to every PE you would get 16. To avoid that, a PE can read its coordinates at run time with the `<layout>` module (`layout_mod.get_x_coord()`)." Add one sentence about `<layout>` in "Hardware parts" so the answer has a source.

### P7 [minor] Check yourself Q1's answer is only accurate for WSE-3, and the chapter never shows a route
Location: Check yourself Q1, and the "Three files" box ("routes for every color").
Problem: The answer says "Device code only sees queues bound to that color". On WSE-2, device code binds tasks and DSDs to the color directly, as ch10's program 02 shows with `@is_arch("wse2")`. The chapter also states that layout holds routes, but its only example (SAXPY) has none, so `@set_color_config` first appears in an answer.
Why it matters: It plants a WSE-3-only mental model just before Lab 1 teaches the difference. The learner also never sees the syntax of the most important layout call in the chapter that teaches layout.
Concrete fix: Change the answer's last sentence to "Device code then uses that color: on WSE-2 directly, on WSE-3 through an input/output queue bound to it." Below the tour, add a 4-line snippet from `programs/03-row-reduce/layout.csl` (the two `@set_color_config` calls with `.rx = .{RAMP}, .tx = .{EAST}` and `.rx = .{WEST}, .tx = .{RAMP}`), captioned "What a route looks like (program 03, ch11)".

### P8 [minor] "Why" is missing from several tour notes
Location: Tour notes for `var x_ptr: [*]f32 = &x;`, `@export_name("x", [*]f32, true)` and `@fmacs`.
Problem:
- "Host-visible symbols are exported as many-item pointers" states a rule without a reason.
- The mutability note says it "must match var vs const" but not what goes wrong if it does not.
- The `@fmacs` note does not explain the name or how to find the sibling operations.

Why it matters: A learner who writes a second program needs to pick the right builtin (`@fmuls`, `@fadds`, the f16 variants), and will hit the mutability mismatch that the chapter itself admits caused a bug.
Concrete fix:
- `x_ptr` note: append "The host addresses memory by symbol, not by type, so exports are untyped-length `[*]` pointers. The length comes from the memcpy call."
- `@export_name` note: append "If the flag and the declaration disagree, cslc rejects the program." (Use whichever behaviour program 02's bug actually showed.)
- `@fmacs` note: append "Name = f(loat) + mac + s (32-bit). Siblings: `@fadds`, `@fmuls`, `@fsubs`, and `…h` for f16 (ch06 lists them). Each operand can be a DSD or a scalar."

### P9 [minor] The "most bugs are resource bugs" callout and the debugging trick refer to bugs the learner has not seen
Location: The "Most bugs are resource bugs" callout, and the "cheap trick … program 02's race" paragraph.
Problem: "two operations sharing a microthread" and "program 02's race" are given without a pointer. Program 02 is in ch10, after this chapter. The race is explained in ch07, but no link is given. The microthread bug is not identified at all.
Why it matters: Without a pointer, these read as war stories with no lesson the learner can use.
Concrete fix: Make each item a link with a one-clause explanation:
- "an export's mutability flag (`true` in layout but `const` on the device, program 02)";
- "a race where the host read results before the last data task ran (ch07, 'The race')";
- "two asynchronous DSD operations on the same microthread (ch05/06), which serialise or stall".

In the trick paragraph, change "program 02's race" to "the streaming race described in ch07 (program 02, Lab 1)".

### P10 [minor] The `out_X_Y.elf` label suggests one ELF per PE coordinate
Location: The "From source to simulation" diagram, `bin/out_X_Y.elf`.
Problem: The ELF names are indices of unique PE programs, not PE coordinates. A 1 × 6 column compiled for ch11 produced `out_0_0.elf`, `out_1_0.elf`, `out_1_1.elf`: three files for six PEs, with indices that are not their (x, y). The same chapter says "one ELF per unique param set", so the diagram contradicts the text.
Why it matters: A learner looking in `out/bin/` for "their PE (3,0)" will be confused, and it undercuts the param/ELF lesson in Q2.
Concrete fix: Relabel the box `bin/out_*.elf (one per unique PE program)`. Add to the caption: "File names number the distinct programs. They are not PE coordinates."

### P11 [minor] The compile pipeline and output locations do not say where things are written
Location: "From source to simulation" diagram and caption (objective 2, "find the outputs").
Problem: The diagram separates `out/` from the simulator's files but never says that `sim.log`, `sim_stats.json` and `simfab_traces/` land in the current working directory, nor that the host's `print` output goes to stdout. "Stopped due to idleness" and "50 cycles" are explained, but not whether idleness means success or failure.
Why it matters: A hung program and a finished program both end in "Stopped due to idleness". The learner needs to know that the only real signal of success is the run.py assertion.
Concrete fix: Add to the caption: "`out/` holds compiler output. `sim.log`, `sim_stats.json` and `simfab_traces/` are written to the directory you ran `cs_python` from. A correct run and a deadlocked run both stop 'due to idleness', so success is your host-side check, not the stop cause."

### P12 [minor] "The language in one screen" has unclear one-liners
Location: "Ordinary parts" bullets.
Problem: "if / else (with braces when used as statements)" and "Runtime functions take pointers, not arrays" are compressed to the point of being unclear. A learner does not know what an "expression if" looks like or what a "runtime function" is, as opposed to a comptime one.
Why it matters: These are the rules a Zig newcomer actually trips on.
Concrete fix: Replace with:
- "`if` is also an expression: `const c = if (x % 2 == 0) c0 else c1;`. As a statement it needs braces: `if (v > m) { m = v; }`."
- "Functions that run on the PE cannot take arrays by value. Pass `*[N]f32` or `[*]f32`."

Also add one line on `[*]f32` vs `*[N]f32`: "`*[N]f32` knows its length; `[*]f32` does not (used for exports)."

### P13 [minor] No exercise or "try it" step for the objectives
Location: End of chapter (only three recall questions).
Problem: The chapter sets out to teach compiling, simulating and finding outputs, but asks the learner to do none of it. All three questions are recall.
Why it matters: The fastest test of "can I run a program" is running one with a change. Ch10 has exercises, but they test CSL, not the toolchain.
Concrete fix: Add a fourth question with a hands-on part: "Rebuild SAXPY for WSE-2 (`ARCH=wse2 bash commands.sh`), then open `sim_stats.json`. What is `cycle_count`, and why is it different from WSE-3's 7,740?" Answer: "6,825 cycles. Same source, different chip: `@is_arch` and the memcpy library pick different code paths and timings." Optionally add a fifth: "Which file would you open to confirm that cslc kept the route you asked for?" Answer: "`cs_readelf` on the ELF, or the `--out-routes` dump."

### P14 [minor] csdb and the `<debug>` library are named but not shown
Location: The "Debugging tools" table.
Problem: The table gives no invocation for csdb and no example for `<simprint>`/`<debug>`. The "when" column for `<debug>` ("program must complete") is a constraint, not a use case.
Why it matters: When the learner's first program hangs, they need the one-line `simprint` pattern, not a list of tool names.
Concrete fix: Under the table, add a 3-line snippet: `const prt = @import_module("<simprint>");` then `prt.print_string("reached A\n");` inside a task. Then add: "Output appears in `sim.log` with cycle and PE." Change the `<debug>` "When" cell to "record values over time when the program finishes normally; read with `rt` after `stop()`." Verify the exact simprint API against the SDK library before publishing.
