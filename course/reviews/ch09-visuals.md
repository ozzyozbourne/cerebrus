# ch09 · visuals review

Chapter 9 has two static SVG figures (the "three files" boxes and the compile/simulate pipeline) and one interactive widget, a tabbed code tour of program 01. The content is accurate: all 25 tour lines match `course/programs/01-saxpy/*` exactly, and there are no console errors at any size or theme. Two problems carry most of the weight. First, at 390 px both SVGs shrink to 45 % and their 11–12 px text renders at about 5 px, which is unreadable. Second, the "every line" tour leaves out the lines that hold the program together: `kw` (which sets copy mode), `@export_symbol(saxpy)` and the y-side twins. It also cannot be used from the keyboard, and in dark mode the white-on-orange pins are low contrast. The chapter's main idea, how names and IDs cross the three files and the host↔device command stream, is explained only in prose and in single tour notes. That is where new visuals would help most.

Method: Playwright, 1100 px and 390 px (DPR 2), light and dark. I clicked all 3 tabs and all 25 numbered lines (7 + 10 + 8), re-clicked tabs, checked scroll overflow, focusability, ARIA and computed colour contrast. Console: 0 errors and 0 warnings in all 4 configurations. Page has no horizontal overflow (scrollWidth = clientWidth at both widths).

## Findings (defects in existing visuals)

### V1 [major] Both SVG figures are illegible on phones
- **Location:** Figure "Three files, three places" (`viewBox 0 0 760 230`) and figure "From source to simulation" (`viewBox 0 0 760 260`).
- **Problem:** `width="760"` together with `max-width:100%` scales both figures to 340 px at 390 px viewport (scale 0.447). Body text at font-size 12 becomes about 5.4 CSS px, mono 11 becomes about 4.9 px, and titles become about 7 px. The second figure is worse because it puts a 5-line paragraph (sim_stats.json excerpt, the 50-cycle note, the FYN/SDR note) inside the SVG. That paragraph could simply be HTML.
- **Evidence:** Rendered SVG sizes at 390 px are 340×103 and 340×116. In the screenshots fig1-390 and fig2-390, the box bullet lines can only be read at 2× zoom.
- **Concrete fix:**
  - Figure 1: add a narrow variant that stacks the three boxes vertically (`viewBox 0 0 300 520`), and switch with `<picture>`-style twin SVGs plus `@media (max-width:680px)`. A simpler option is to remove the four muted bullet lines from the SVG and render them as an HTML `.grid3` under each box title.
  - Figure 2: move the "Program 01's sim_stats.json" block and the two muted notes out of the SVG into a `<pre class="output">` and a `<p>` under the figure. Then lay the 4-stage pipeline out as a 2×2 grid on narrow screens (cslc → out/ on row 1; cs_python → simulator on row 2), or as a vertical stack. The goal is at least 11 px effective text.

### V2 [major] Code tour is not usable from the keyboard and has no tab semantics
- **Location:** `#tour-tabs` buttons and `#tour-code div[data-n]`.
- **Problem:** The numbered lines are `<div>`s with `onclick`. None has `tabindex`, `role="button"` or key handling, so the core interaction of the widget cannot be reached by keyboard. The tab buttons have no `role="tab"` or `aria-selected`. The readout has no `aria-live`, so screen readers never announce the explanation.
- **Evidence:** `focusable = 0` for all `#tour-code div`. `role/aria-selected = null/null` for all 3 tab buttons.
- **Concrete fix:**
  - Render numbered lines as `<button class="ln">` (or add `tabindex="0" role="button"` plus a key handler for Enter/Space).
  - Add ↑/↓ (or j/k) to move between numbered lines.
  - Give `#tour-tabs` `role="tablist"`, give each button `role="tab"` with `aria-selected` toggled in `show()`, and give `#tour-note` `aria-live="polite"`.

### V3 [major] "Every line" tour skips lines that matter, including `kw`, which defines copy mode
- **Location:** Widget title "Guided tour: program 01 (SAXPY), every line"; the `files` object in the inline script.
- **Problem:** Only 25 of 44 lines carry a pin, and the run.py tab is abridged. These parts are missing:
  - **run.py:** the `N = …out.json['params']['N']` line (how the host learns a compile-time param). The data generation. Above all, the `kw = dict(streaming=False, order=ROW_MAJOR, data_type=MEMCPY_32BIT, nonblock=False)` line. Note 4 says "Copy mode", but the setting that makes it copy mode (`streaming=False`) is hidden behind an unexplained `**kw`.
  - **pe_program.csl:** `@export_symbol(saxpy)` has no note, yet it is the only export without a name string. Readers will wonder why. The answer is that the function's own name is used, and it matches `@export_name("saxpy", …)`.
  - **Twin lines:** `@export_name("y"…)`, `var y`, `y_ptr`, `y_dsd` and `param N` in pe_program.csl are unpinned and greyed by implication. That is fine for twins, but nothing tells the reader "same as above".
- **Evidence:** The pins/total counts per tab are layout 7/12, pe_program 10/23 and run.py 8/9. The run.py tab has 9 lines while the real `run.py` has 26.
- **Concrete fix:**
  - Retitle the widget to "…line by line", or show the full run.py.
  - Add pinned notes for `N = int(json.load(...))` ("reads the param cslc recorded in out/out.json"), for `kw = dict(...)` ("streaming=False → copy mode; ROW_MAJOR order; 32-bit elements; blocking"), and for `@export_symbol(saxpy)` ("no name string: exported under the function's own name, matching the layout's @export_name").
  - Give twin lines a muted "same as line n" note instead of no pin.

### V4 [minor] Pin numbers look like line numbers but are not
- **Location:** The readout text `"<file> · <n>: …"`.
- **Problem:** The readout shows, for example, "layout.csl · 6: Declares a host-visible name". Readers take 6 as a source line number, but it is line 9 of the file. Pin numbering also restarts per tab, so "pe_program.csl · 8" cannot be cross-referenced to the file on disk or to the Lab chapters.
- **Concrete fix:** Show real file line numbers in a gutter (all lines, muted) and keep the pins as the clickable markers. In the readout, print `layout.csl:9`.

### V5 [minor] Dark mode: white on accent orange is 2.26:1
- **Location:** `.code-tour .pin` (white text on `--accent`) and `.tabs button.on` (white on `--accent`).
- **Problem:** In dark mode `--accent` is `#fb923c`. White text on it gives 2.26:1, which fails WCAG AA for both the 11 px pin numbers and the 13 px tab label. Light mode passes at 5.18:1 on `#c2410c`.
- **Evidence:** The contrast values were computed from the resolved CSS variables. Screenshot tour-1-390-dark shows faint white digits on the orange pins.
- **Concrete fix:** Use `color: var(--bg)` or `#1b1e25` for `.pin` and `.tabs button.on` in dark mode, which gives about 7.9:1. Alternatively, use a dark-mode-specific `--accent-strong`.

### V6 [minor] Pipeline figure misplaces `out_rpc.json` and omits `generated/`; outputs location is ambiguous
- **Location:** Figure 2, `out/` box: lines "bin/out_X_Y.elf", "west/ east/ (memcpy)", "out.json  out_rpc.json".
- **Problem:**
  - `out_rpc.json` is drawn at the top level of `out/`, but it is written to `out/bin/out_rpc.json`. The chapter's own tour note (run.py line 2) gives the correct path.
  - `out/generated/{default,coord,MEMCPY_XY_ROUTES}.elf` is missing.
  - The simulator box lists `sim.log`, `sim_stats.json` and `simfab_traces/` with no hint that these land in the working directory, not in `out/`. That matters for the objective "find the outputs".
- **Evidence:** A real compile tree (`tmp/rev-ch11-acc/cb/`) contains `out/bin/out_rpc.json`, `out/generated/*.elf`, and `sim.log`, `sim_stats.json` and `simfab_traces/` at the top level, next to `layout.csl`. `csl_programming.md` §memcpy records the same layout.
- **Concrete fix:** Change the `out/` box to: `bin/out_X_Y.elf, bin/out_rpc.json` / `west/ east/ generated/ (memcpy)` / `out.json (params)`. Label the simulator box's file list "written to ./ (cwd)".

### V7 [minor] Figure 1 has an unused arrow marker and shows no relationships between the files
- **Location:** Figure 1, `<marker id="a11">` is defined but never referenced.
- **Problem:**
  - The figure presents three isolated boxes. The figure itself shows none of the links the chapter teaches: `@set_tile_code` → pe_program.csl, `@export_name` ↔ `@export_symbol` ↔ `rt.get_id`, and `param N` from `--params`. The unused marker suggests the arrows were planned and dropped.
  - The footer line "grid coordinates are always (x = column, y = row)" is unrelated to the boxes and appears with no visual anchor.
- **Concrete fix:** Either add the arrows (see proposal P1, which replaces this figure), or delete the dead `<defs>` and move the coordinate convention into the caption.

### V8 [minor] Tour readout sits below a tall code block, out of view on phones
- **Location:** `#tour-note` under `#tour-code`.
- **Problem:** On the pe_program.csl tab at 390 px, the code block is about 480 px tall. Clicking pins 1–5 updates a readout that is off-screen. Each line also needs horizontal scrolling inside the block (scrollWidth/clientWidth = 766/322 on layout.csl and 603/322 on pe_program.csl), so the most important part of long lines (e.g. `.memcpy_params = …, .N = N`) is hidden.
- **Concrete fix:** At ≤680 px, open the note inline directly under the clicked line, as an expanding row. Alternatively, make `#tour-note` `position: sticky; bottom: 0`. Wrap long lines with `white-space: pre-wrap` and a hanging indent at narrow widths.

### V9 [minor] Figure 1 caption leaves an orphaned full stop on mobile
- **Location:** Figure 1 figcaption ends with `</span>.`
- **Problem:** At 390 px the "." wraps alone onto its own line after the tag pill.
- **Concrete fix:** Put the full stop before the tag, or wrap the tag and the stop in a `white-space:nowrap` span.

## Proposed new visuals (prioritised)

### P1 (high) "Follow a name across three files": linked-highlight diagram replacing Figure 1
- **Purpose:** The chapter's core claim is that a CSL program is three files joined by names and params. Today that is only implied. Make the joins visible.
- **Content:** Three columns (layout.csl | pe_program.csl | run.py), each showing the relevant lines of program 01 in mono text. Five coloured "threads" (curved connectors) join them:
  1. **`N`:** `cslc --params=N:64` → `param N: i16` (layout) → `.N = N` in `@set_tile_code` → `param N: i16` (pe_program) → `var x: [N]f32`. The thread also reaches run.py's `json.load(out.json)['params']['N']`.
  2. **`"x"`:** `@export_name("x", [*]f32, true)` ↔ `@export_symbol(x_ptr, "x")` ↔ `rt.get_id('x')`. A small badge reads "mutable = true ↔ `var x_ptr`" (ties to the program-02 bug).
  3. **`"y"`:** same as `"x"`.
  4. **`"saxpy"`:** `@export_name("saxpy", fn(f32)void)` ↔ `fn saxpy(a: f32)` + `@export_symbol(saxpy)` ↔ `rt.launch('saxpy', a)`.
  5. **`memcpy_params`:** `memcpy.get_params(0)` → `param memcpy_params` → `@import_module("<memcpy/memcpy>", memcpy_params)`.
- **Middle of the diagram:** a small "out/bin/out_rpc.json" chip on the connector between pe_program and run.py, showing `{"id":1,"kind":"Var","name":"y","sym_name":"y_ptr","type":"[*]f32"}`. That entry format is from `csl_programming.md`. Show only the fields, not invented IDs for this program, unless it is compiled to read the real ones.
- **Interaction:** Chips along the top read `N`, `x`, `y`, `saxpy`, `memcpy_params`. Clicking or hovering a chip (or any token in the columns) highlights that thread across all three files and dims the rest. A one-line readout gives the rule, e.g. "the third arg of @export_name must match var/const of the exported pointer". Use keyboard arrows to cycle the chips.
- **Mobile:** columns stack, and the threads are drawn as numbered colour badges instead of curves.
- **Where:** replaces the current Figure 1 under "Three files, three places", before the tour.

### P2 (high) Host ↔ device sequence for one SAXPY run (stepper)
- **Purpose:** Show the run.py lines as a timeline across host, memcpy runtime and PE. Make clear why `unblock_cmd_stream()` is mandatory and what "blocks" means.
- **Content:** Three lifelines: **host (run.py)**, **memcpy runtime (west/east halo, color 22 command stream)** and **PE (0,0)**. Seven steps:
  1. `load()` / `run()`: ELFs placed (user `bin/out_0_0.elf`, west ×3, east ×2, generated/*).
  2. `memcpy_h2d(x)`: command on color 22, then N=64 f32 arrive in `x`.
  3. `memcpy_h2d(y)`.
  4. `launch('saxpy', 2.5)`: an RPC command; memcpy calls `saxpy(a)` on the PE, and the command stream is now **blocked**.
  5. `@fmacs`: a 64-element vector op.
  6. `unblock_cmd_stream()`: the stream is released.
  7. `memcpy_d2h(y)`, then `stop()`, after which sim_stats.json shows 7,740 cycles (WSE-3) / 6,825 (WSE-2).
- **Interaction:** Next/Prev buttons and a step slider. The active run.py line is highlighted next to the diagram. A toggle, "forget unblock_cmd_stream()", replays the run: step 7's arrow stops at a red "waiting" bar, the host lifeline shows a hang, and the simulator stops with "Stopped due to idleness". This connects to the quiz question about hangs.
- **Where:** directly after the code tour, before "The language in one screen".

### P3 (medium) Fabric map for `--fabric-dims=8,3 --fabric-offsets=4,1`
- **Purpose:** The flag table says "size of the simulated fabric, including memcpy's columns" and "where your rectangle's (0,0) sits". A picture of the 8×3 grid makes both concrete and explains the numbers in sim_stats.json (`fabric_x 8, fabric_y 3, hwtile_count 10`).
- **Content:** An 8×3 grid of cells. The user PE is at fabric (4,1), labelled "your (0,0)". Mark the halo-kernel ELFs observed for `--channels 1` (west/bin out_{0,1,2}_0, east/bin out_{0,1}_0) as "memcpy west/east". Grey out the edge/null tiles.
- **Caveat:** do not draw exact west/east column positions as fact. `csl_programming.md` §Gaps says the per-channel layout is undocumented, so label those columns "memcpy halo (observed: 3 west, 2 east ELFs)". Reuse chapter 7's frame figure style and link to it.
- **Interaction:**
  - Number inputs for program width/height (1–8) and offsets. The grid recomputes and flags an error when the rectangle plus halo does not fit. Use the SDK rule that the user rectangle must be ≤ dims − (7, 2), from the single-tile-matvec README.
  - The generated `cslc … --fabric-dims=W,H --fabric-offsets=X,Y` line updates live.
  - Edge values to handle: width 0 (reject) and offset < (4,1) (warn).
- **Where:** next to the `commands.sh` block and flag table in "From source to simulation".

### P4 (medium) Clickable output tree: "where did that file come from?"
- **Purpose:** Supports the objective "find the outputs" and fixes V6 properly.
- **Content:** A collapsible tree of a real program-01 working directory:
  - `out/bin/out_0_0.elf` (your PE)
  - `out/bin/out_rpc.json`
  - `out/west/bin/out_{0,1,2}_0.elf`
  - `out/east/bin/out_{0,1}_0.elf`
  - `out/generated/{default,coord,MEMCPY_XY_ROUTES}.elf`
  - `out/out.json`
  - `sim.log`
  - `sim_stats.json`
  - `simfab_traces/`
  - `simconfig.json`

  Each node is tagged with its producer (cslc / simulator) and its consumer (SdkRuntime / you / csdb).
- **Interaction:** Clicking a node shows a short real excerpt and what to use it for. Use real data: sim_stats keys `cycle_count`, `sim_stop_cause`, `idle_ce_cycles: 50`, `idle_wavelet_cycles: 90`; an out_rpc.json entry; the out.json params. A "producer" filter colours the tree by cslc vs simulator.
- **Where:** replaces the text-heavy right half of Figure 2, or sits directly below it.

### P5 (low) "Unique params → ELFs" counter
- **Purpose:** Quiz question 2 ("8 → 16 PEs and compilation gets slower") and the bullet "Different params → different ELF" are prose-only.
- **Content:** A row of P PEs, each coloured by its param tuple. Mode A passes `.pe_id = i` as a param, giving P unique programs and P ELFs. Mode B uses `<layout>` `get_x_coord()` at runtime, giving 1 ELF. A counter reads "unique PE programs to compile: n". Source: the gemv-07 README quote already in `csl_programming.md`.
- **Interaction:** A slider for P from 1 to 16 and a mode toggle. Show ELF counts only, not compile times, since no compile times were measured.
- **Where:** in "The language in one screen", next to the `param` bullet.

### P6 (low) Resource-bug gallery for the callout "Most bugs are resource bugs"
- **Purpose:** The callout names three real bugs in one sentence. Three small side-by-side cards would make them memorable.
- **Content:** Each card has a code snippet (wrong vs right), the symptom and the tool that revealed it:
  1. **Export mutability flag:** `@export_name("x",[*]f32,false)` vs a `var` pointer; compile/runtime error text from program 02.
  2. **Race on the command stream:** the `numpy.cumsum` recording trick described in "Debugging tools".
  3. **Two operations sharing a microthread.**

  Use only error messages actually captured in `course/programs/02-*` or the lab chapters.
- **Interaction:** a wrong/right toggle per card.
- **Where:** replace or extend the callout after "The language in one screen".
