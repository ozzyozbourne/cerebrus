# ch15 fix log

Edited file: `course/15-comparison.html`. It was rewritten, growing from 166 to about 820 lines. Nothing else was edited: `course.css` and `course.js` are unchanged, and `12-*` and `src/*` were not touched.

New page-local CSS covers:
- `.chart` and `.tri` containers. SVGs placed inside them are not direct children of `figure` or `.widget`, so the 620px phone min-width rule does not apply to them.
- Pills and swatches.
- The calculator grid.

All drawings use `el()`, `cssVar()` and the shared `f-*`, `s-*` and box classes, so they follow the theme toggle live.

## Verification

Playwright/Chromium was run at 1100px and 390px, in light and dark.
- **Result:** 0 page errors, 0 console errors or warnings, and `scrollWidth == innerWidth` on load and after the theme toggle.
- **Clipping check:** no SVG text is clipped outside its chart.
- **Controls exercised:**
  - every metric in both modes of the compare widget
  - all batch steps and both formats of the ridge widget
  - every point in both modes of the map
  - all three scaling toggles
  - both cost presets, with edits
  - the Lab-3 slider at its ends
  - chooser combinations
- **Screenshots:** reviewed, then deleted. The scratch directory has been removed.

## Mandatory corrections

| Item | Status | Note |
|---|---|---|
| Blackhole L1 / NoC / Ethernet | fixed | Values are now 1,536 KiB (WH 1,464), 64 B flits / ≤16 KiB packets / 1.35 GHz, and "4 × 800 GbE (8 of 14 × 400 GbE tiles wired; none on p100)", matching ch13. |
| $0.60 tagging | fixed | Price and source are tagged separately everywhere: the $0.60 list price as Vendor, the H100 $0.10–0.25 as Analyst (Spheron). This matches ch08's tagging. ch13 has no $0.60 figure. |
| CS-6 wording | fixed | The text now reads: integrates "wafer-scale SRAM and compute with 3D-stacked DRAM" [Vendor]. This matches ch08 and note 3. |
| ±2 cycles | fixed | Removed. Replaced with note 17 (whole-run counts vary +1–4% with host load; can abort with "kernel stall"; TSC is stable) and note 19 (TSC values are not comparable across PEs). |
| Decode on Cerebras | fixed | Matches note 6 and ch08: the ceiling is about 600,000 tok/s (≈18,000 from the SDK GEMV rate) against 2,314 measured, so the limit is pipeline latency and communication. This appears in the ridge widget, the decode section, and quiz Q1. |
| Lab 2/3 numbers | fixed | Lab 2: kernel is 1–3% of the run; TSC 58/73/101/158 (≈M+7P); router hop 2.0/1.0; through-PE hop ≈9.2/6.0; streaming vs store-and-forward 101 vs 348. Lab 3: 90 + 2.5·n with 2.5 = 0.5 + 1 + 1; 100/130/250 measured; P=2 101; P=16 ~130.6; break-even n = 36. |
| Microthread wording | fixed | Uses the note 1/11 wording: FATAL "trying to term ut_instr[3], but it's not ours" at 2,123 (WSE-3) / 2,125 (WSE-2); the host waits forever; queue = microthread is the WSE-2 rule and the WSE-3 default. |
| DSD rates | fixed | @fadds runs at 2/cycle on WSE-3. The @fmacs operand-collision rule (mod 4 words) is described as "pad and measure", per notes 16, 22 and 23. |
| Clock | fixed | WSE-2 1.1 GHz [Vendor, HC22] vs the SDK's 850 MHz assumption; no WSE-3 clock is published. |
| SRAM per PE | fixed | ~44,500 B (~44.5 KB) usable on WSE-3 [Measured]; Lab 3 fits about 5,450 cells. Replaces "~46 KB". |

## Accuracy (A)

| ID | Status | Note |
|---|---|---|
| A1 | fixed | Compute is split into two metrics: a "~16-bit dense" metric (B200 2.25 PF BF16, Vendor via secondary; p150 drawn hollow as BlockFP8) and a "lowest precision" metric (all hollow, with format labels). |
| A2 | fixed | Uses the paper's headline figures: ~270,000 timesteps/s, 179× Frontier, 55× Quartz. |
| A3 | fixed | Every cell in both architecture tables and in the strengths table carries a tag. The H100 RF/L1 figure is tagged Derived. |
| A4 | fixed | Power is now given as max TDP per module (700 / 1,000 / 1,200 W liquid-cooled), and CS-3 as a whole system. The figure is hollow in the widget, with a "not like-for-like" note. |
| A5 | fixed | Vendor price vs Analyst (Spheron, a GPU-cloud company), stated as Llama 3.1-70B output tokens. |
| A6 | fixed | Changed to "8 GPUs on HGX, 72 in GB200 NVL72". "2,048 CS-3s" is tagged Vendor. The comparison is tagged as a Derived synthesis. |
| A7 | fixed | Tagged Measured: peer-reviewed with Cerebras co-authors; a Gordon Bell 2024 finalist, not winner. |
| A8 | fixed | Llama 3.3-70B at batch 32 (v0.65 rc); ~350 claimed, ~308 at launch, on DeepSeek-R1 671B. |
| A9 | fixed | Gives WSE-3 ~0.05 mm² and WSE-2 0.039 mm² (HC22), with "sources differ". |
| A10 | fixed | Adds the optional write-through cache (off by default). GPU crossbar is tagged Unverified. |
| A11 | fixed | Decision row reworded to "if you can hold the weights in the SRAM of enough wafers". Quiz now says "2–4× (80–192 GB vs 44 GB)". |
| A12 | fixed | B200 192 GB nominal, ~180 GB usable [Analyst], in the widget and the chooser. |

## Pedagogy (P)

| ID | Status | Note |
|---|---|---|
| P1 | fixed | New "How to compare: the axes" section (four axes tied to Ch. 1, 2, 9–14), plus an interactive ridge/decode-intensity widget. "Compute units" is replaced by "Local memory per compute unit", and a Ridge metric is added. |
| P2 | fixed | Adds a Consequence row to both tables, chapter links in the column headers, and a "cross-cutting pattern" paragraph (lifted from the old Q3). |
| P3 | fixed | The decision guide is now an HTML table with "Because" and "What is missing" columns. Rows added for training, HPC solvers, capacity/KV and learning. |
| P4 | fixed | Bugs are split into runtime bugs (host-copy race in program 02; microthread clash in Lab 3) and compile-time ones (mutability; if/else braces). Each links to its chapter. |
| P5 | fixed | Measured tag, the TSC vs whole-run noise distinction, "≤ 16 PEs simulated", and a reworded GPU-profiler contrast. |
| P6 | fixed | Defines weak vs strong scaling; explains P=2 (101); states break-even n = 36. |
| P7 | fixed | The quiz now has 8 questions: the 400B sizing, n = 36 with how to lower the 90, the least-trusted row, ridge points, and the bandwidth cliff. |
| P8 | fixed | TTFT expanded. "Spec slippage" becomes "announced specs revised (Rubin 22 → 19.2 TB/s)". The de-rating is explained. Weakness cells link to their chapters. Strong scaling is defined. |
| P9 | fixed | Adds an objectives block, a "Back to the memory wall" section, and "Where to go next" (SDK tutorials, benchmarks, report, a Lab 3 extension). |
| P10 | fixed | Three-panel scaling figure with scale-up / scale-out highlight, plus a bandwidth-cliff table. |
| P11 | fixed | The CSL panel now has a full 2-D mesh, two highlighted routes with wavelets, and host memcpy. |

## Visuals (V)

| ID | Status | Note |
|---|---|---|
| V1 | fixed | Cleveland dot plot on a labelled log axis with decade gridlines; ratio readout of Cerebras ÷ each. |
| V2 | fixed | Hollow dots mark non-comparable values, with the format given in the label. Compute is split by format; power is labelled system vs card vs module. Compute units dropped. A per-rack toggle is added. |
| V3 | fixed | The readout is an HTML list with a real `.tag` per value. |
| V4 | fixed | Labels flip side near the right edge; the narrow layout puts values on the label line. The clipping test passes. |
| V5 | fixed | Uses classes and `cssVar` only, so colours follow the toggle live. |
| V6 | fixed | Charts redraw at the container's pixel width (ResizeObserver), giving 1:1 text size on phones. Static panels stack to one column below 760px. The decision guide is HTML. |
| V7 | fixed | Dashed track with italic "n/a: reason"; filtering uses `v != null`. |
| V8 | fixed | CUDA: HBM→L2→SM→warps. TT: GDDR6→reader→CB_in→compute→CB_out→writer→GDDR6, plus a ghost core over the NoC. CSL: mesh, routes, memcpy. A common footer row spans all three. |
| V9 | fixed | HTML decision table plus the interactive chooser (N3). |
| V10 | fixed | Metric renamed "Memory that holds the weights", with a MemoryX note. |
| N1 | fixed | Ridge widget with batch slider, a format toggle (16-bit vs lowest), a prefill band, and per-device attainable fraction. A Lab 3 stencil marker was not added: there is no sourced intensity figure. |
| N2 | fixed | Capacity-vs-bandwidth map with time-to-read diagonals, model-size lines, device/rack toggle, and focusable points. |
| N3 | fixed | "Will it fit" chooser with units, per-user ceiling, and a verdict by goal stating the missing evidence. |
| N4 | fixed | Three-panel scaling figure with highlight toggle. Line thickness is not mapped to bandwidth; figures are in the caption and the cliff table instead. |
| N5 | skipped | The quadrant/radar would duplicate N2. N2 already plots the reviewer's preferred axes (capacity vs bandwidth per byte). |
| N6 | fixed | Lab 3 chart: log–log model with measured points and the n = 36 marker, plus a stacked step bar (fixed 90 + 0.5n + n + n) and a whole-wafer extrapolation readout. |
| Index kicker colour | skipped | Trivial, and it concerns the index page, which is not in scope. |

## Depth (D)

| ID | Status | Note |
|---|---|---|
| D1 | fixed | New section "One workload, three machines": ceiling-vs-measured dot chart for 7 configs, the 432 µs → 5.4 µs → ~4,600-cycle derivation, and an ~83 ns weight-read check. Batch effects are handled in the ridge widget rather than here. |
| D2 | fixed | Editable cost/energy calculator with tagged inputs. The $10M capex is tagged Unverified. Shows implied ~59 streams for $0.60/M. No H100 capex, which is stated. |
| D3 | fixed | TFLOP/s-per-W table (system vs module flagged), J/token in the calculator, the MD energy claim, and the <1 mm wires. The CS-4 "10×/W" claim is skipped: it is not in the research notes. |
| D4 | partial | Stencil extrapolation (≈180–600× an H100 streaming roofline) and a GEMM paragraph. The optional "what limits this kernel" table is not added. |
| D5 | fixed | Cliff table (≈140,000× / 3.7× / 4.4× / 1.3×) with a note on bidirectional NVLink, a parallelism mapping in prose, and the topology figure. |
| D6 | fixed | Training / prefill / decode × vendor table, including Rubin CPX and "fast decode does not shorten prefill". |
| D7 | fixed | Software-stack table: layers, serving, maturity evidence (BH vs WH QuietBox, The Register, vLLM dispute, portability traps), and access paths. |
| D8 | fixed | "What you must budget by hand" table, with the program 04 line count (246 lines, 4 files, measured with `wc -l`). Says no productivity study exists. CUDA and Metalium line counts are omitted. |
| D9 | fixed | 11-item claim decoder with course examples, plus an open-questions list. |
| D10 | fixed | Per-rack (2026) mode in the compare widget and the map: CS-4, Galaxy Blackhole, GB200 NVL72, Rubin NVL72. Readout gives the 94× bandwidth and 1/157 capacity ratios. |
| D11 | fixed | Merged into the chooser: 8B–1T × 16/8/4-bit × KV reserve, across 7 platforms. |
| D12 | fixed | Metric column added. New rows: CS-1 BiCGStab, GPT-5.6 Sol, CS-4 4,400 (Unverified), MD 748×/457×, DGX-H100 86 tok/s, the excluded Tenstorrent blog, and MLPerf none-found (Unverified). The H100 L2 row uses ch14's ">5.5 TB/s" because ch14 dropped 3.8 TB/s as unconfirmed. The TTFT sentence is in the fair reading. |
| D13 | fixed | Decision row for solvers and FFTs, tagged SDK (patterns exist, no performance claim). |
| D14 | fixed | Rows added for training, long context/KV and learning. Rows are linked to evidence through the "Because" column, not tooltips. |
| Out of scope (new ch16, appendices) | skipped | These need coordinator decisions. D1 and D4 were folded into ch15 as the reviewer's fallback. |

## Cross-chapter notes applied
Notes 1, 2, 3, 4, 5, 6, 11, 13 (as ~44.5 KB, per the brief), 15, 16, 17, 19, 20, 22, 23 and 24. Note 21 (`launch()` returning) is not mentioned, as it is not needed here.

## Counts
- Accuracy: 12 of 12 fixed.
- Pedagogy: 11 of 11 fixed.
- Visuals: 10 of 10 fixed. Of the proposals, N1–N4 and N6 are fixed and N5 is skipped.
- Depth: 13 fixed and 1 partial (D4) of 14.

Total: 51 findings and proposals. 49 fixed, 1 partial, 1 skipped, plus the out-of-scope items and the index kicker, also skipped.

## Open issues
- ch12 is still being revised. ch15 quotes these values from it: 90 + 2.5·n; 100/130/250; P=2 101; P=16 ~130.6; ~5,450 cells; the 737k-PE extrapolation; overlap 178 vs 130; ≈14.6 cycles per transfer. If ch12's final numbers change, update the lessons list, the stencil box, the Lab-3 widget and quiz Q5.
- B200 BF16 dense (~2.25 PF) is "Vendor via secondary" here but Derived in ch14. GPU max-TDP figures come from the accuracy reviewer's web search, not the research notes.
- Unverified inputs: the $8–12M capex, the Wormhole Galaxy power (the Blackhole Galaxy 12 kW figure is borrowed), and the MLPerf absence.
- Rack mode has n/a for CS-4 and NVL72 power; the sources give no figure.
