# R4 fix log · ch07 Host I/O and memcpy (07-host-io.html)

I edited only `07-host-io.html`. I ran no simulator experiments. The new SDK facts come from the library sources in the SIF: `memcpy/wse3/memcpyh2d.csl`, `memcpyd2h.csl`, `memcpy.csl`, `sys_params.csl`, `runtime/demux_adaptor.csl` and `layout_*_multi.csl`. The README facts come from `single-tile-matvec/README.rst` and `sweep.py`, and the frame formula from `bandwidth-test/run.py`. I checked the page with Playwright: 1100 px light and dark, 390 px, every widget driven. Zero console errors, no horizontal overflow, and all in-page and cross-page anchors resolve.

## Report items

| ID | Status | What changed |
|---|---|---|
| E1 | Fixed | Warn callout now says Lab 3 times the kernel with the TSC (link `13-lab-stencil.html#tsc`) because whole-run totals include memcpy and host idle time. |
| E2 | Fixed (this page's part) | The new `#what-blocks` box states the rule prominently. The wrong text is on Ch 13/14/15 and in the programs 06/07 comments (see "For other pages"). |
| E3 | Fixed | Quotes bandwidth-test/run.py:239–248 verbatim (`core_fabric_offset_x = fabric_offset_x + 3 + width_west_buf`, `min_fabric_width…`, `min_fabric_height…`) and states that `fabric_offset_x = 1`. |
| E4 | Fixed | Local-task rows now say: WSE-3 8–20; programs 01–05 use 9–13; Labs 4–5 go up to 20. |
| E5 | Fixed | General form `$((W+7)),$((H+2))` with `4,1`, listing the 1-D (programs 03–05) and 2-D (Labs 4–5) instances. |
| E6 | Fixed | CUDA callout says "in the simulator … how hardware reports it we have not measured". Q7 now asks about one copy (~200 µs) and the whole program (4 commands ≈ 0.8 ms). |
| X1 | Fixed | States that the counter counts up and wraps, and gives a worked PE 1 example showing why the direction matters. Adds the library's 4-row counter table (memcpyh2d.csl:57–62) and links Ch 4 `#filters`. |
| X2 | Fixed | UT0/IQ0/OQ0 glossed as memcpy's microthread 0, input queue 0 and output queue 0, pointing to the new streaming figure. |
| X3 | Fixed | The ordering paragraph and quiz Q5 now say the host is still inside the blocking `memcpy_h2d(b)`, that x's wavelets would need the path where b's stalled wavelets sit, and that each PE decodes x only after b. |
| X4 | Fixed | The Local tasks cell is split into three rows (both chips / WSE-3 / WSE-2), with a link to Ch 5 `#budget`. |
| X5 | Fixed | Chapters 4, 5, 8, 10, 11, 13 and 15 are now linked to section anchors. About 25 glossary links on first use (memcpy, memcpy frame, halo, H2D/D2H, channel, counter filter, command stream, RPC, unblock_cmd_stream, kernel stall, microthread, data task, task picker, run-to-completion, back-pressure, param, export, SdkRuntime, TSC, MemoryX, fabric-dims, color, three files). |
| G1 | Fixed | New `<div class="callout key" id="what-blocks">` after the call table. It covers what `nonblock=False` means per call and the three consequences. It has a two-lane SVG timeline (launch returns at 0.00 s, the next memcpy_d2h waits 5.06 s until `unblock_cmd_stream()`), the measurement (Measured, round-4 audit run), and a link to Lab 5's host loop. The call table's launch row links to it. |
| G2 | Fixed | New "How the host finds your arrays" box after the host excerpt. It shows `@export_name` in the layout, `@export_symbol` in the PE program and `get_id` on the host (from program 01), plus the memcpy params import → `sys_mod` line, with forward links to Ch 10 `#three-files` and the glossary. |
| G3 | Fixed | New `#d2h-path` subsection with a figure. Each row has one sender at a time on switch-capable color 21: a data wavelet, then a switch-advance control wavelet that passes the turn east. Output is element-interleaved. The mux column merges rows into the mux adaptor, and a teardown ends the copy. Streaming D2H goes RAMP→RAMP into IQ0. The experiment's lessons now explain the 8× from this mechanism (Derived). The no-channel-scaling result is still stated as unexplained. |
| G4 | Fixed | New numbered sequence in `#copy-path`: command on FABRIC_CMD → cmd fan → color 22; header `{enable_receiver[N], pes_per_receiver, pe_length}` to the demux adaptor; teardown/config/teardown to the demux; per-PE filter setup from the decoded command (and the inactive-row unblock); data, then a teardown that frees each row. |
| G5 | Fixed | The streaming paragraph now explains the extra router trip (UT0 → OQ0 bound to your color → router RAMP→RAMP set by memcpy → your IQ → your data task). New figure drawn from memcpy.csl:372–380. Both rules (do not route the color; it costs one of your 0–19) now follow from the figure. |
| G6 | Fixed | New paragraph (Derived): run-to-completion does not fix the order, the D2H control task becomes ready on color 22, and the picker need not drain IQ2 first (link Ch 5 `#priority`). Adds the library's QFLUSH(OQ0) quote (memcpy.csl:402–404). The race widget now draws a purple "picker chooses memcpy's D2H task (color 22)" tick and a readout line in the no-barrier case. |
| G7 | Fixed | Adds a sentence after "the whole row takes part": PEs can be at different commands, and the per-PE ordering guarantee is stated. |

## Cross-page items about this page

| Source | Status | What changed |
|---|---|---|
| r4-ch10 E3 (CS-2 750,994 / 743 × 992 also on Ch 7) | Fixed | The `#frame` paragraph quotes both README statements: "fabric-dims must be 750,994", and the sweep example treating 750 × 994 as the program rectangle (`--fabric-dims=757,996`). The CS-2 maximum is now tagged Unverified. The calculator's "real CS-2 limits" readout says the same. |
| Notes 31 (launch) | Already correct; reinforced by `#what-blocks`. |
| Notes 33 (clock) | Fixed | The 0.26 wavelets/cycle derivation now says 850 MHz is the SDK benchmarks' assumed clock and that there is no official WSE-3 clock. |
| Notes 35 (queue depths) | Already correct (6/4/2 in, 2/6/2 out table, tagged SDK). |
| Notes 38 (links) | Fixed (see X5). |
| r4-ch08 E2, r4-ch13 E2, r4-ch11, r4-ch12 | Not this page | They quote or link Ch 7. Ch 13 and Ch 12 can now link `07-host-io.html#what-blocks`, and Ch 13's 16-bit reference can link `07-host-io.html#host-side`. |

## For other pages

- **Ch 13 (src/13-lab-stencil.html)**, step card and quiz: "launch(..., nonblock=False) keeps waiting" / "returns only after the last step" are wrong (notes 31). Say "the host's next command waits", and link `07-host-io.html#what-blocks`.
- **Ch 14 / programs/06-summa/pe_program.csl:123**: "only now does the host's launch() return" → "the host's next command can now run" (Ch 14 fixer only).
- **Ch 15 / programs/07-cg/pe_program.csl:115, 217 and the prose** "each launch returns only when its phase has finished" → "each phase's wait sits in the following launch or copy" (Ch 15 fixer only). Link `07-host-io.html#what-blocks`.
- **Ch 12**, step 6: use the same wording and link to `#what-blocks`.
- **Ch 11**: r4-ch11 suggests a line under its call table; link `07-host-io.html#what-blocks`.
- **Ch 2 (lines ~190, 219, 234, 268) and Ch 10 (#source-to-sim, #fabric-size, calculator CS-2 mode, Q3)**: the "743 × 992 at most" bound. The single-tile-matvec README contradicts itself: line 38 says "fabric-dims must be 750,994", but its `sweep.py --dims 750,994` treats 750 × 994 as the rectangle (fabric 757,996). Tag it Unverified there too, as Ch 7 now does.
- **Glossary (App A)**: `g-filter-range-counter` could add "counts up and wraps; passes at 0" so it matches Ch 4/Ch 7.
