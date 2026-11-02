# ch09 fix log

File edited: `course/09-csl-toolchain.html` only. New experiments were run on SDK 2.10.1 in `/home/user/cerebras-sdk/tmp/fix-ch09/`, which has since been deleted. Every result from them is tagged Measured on the page:
- program 01, compiled and simulated on WSE-3 and WSE-2;
- 9 one-line break variants;
- a 6×2 rectangle with and without a per-row route, with `--out-routes`, `cs_readelf -r/-m` and `<simprint>`;
- an `inst_trace` run;
- the sdklayout-02 tutorial;
- the wrapper source (`_generate_memcpy`), read inside the SIF.

## Accuracy
| ID | Status | Note |
|---|---|---|
| A1 | fixed | The caption now says the host script carries over (with `--cmaddr`) but you recompile with that system's `--fabric-dims` (750,994 on a CS-2). Measured is scoped to the simulator runs. |
| A2 | fixed | Idle stop is described with `sunsetCount: 50` and as "most runs". The "±2 cycles" claim is removed and replaced by measured variance (7,786–11,004 cold or loaded vs 7,740 quiet; WSE-2 8,885 vs 6,826) plus the ch10-depth numbers. The page now recommends `<time>` TSC timing. |
| A3 | fixed | The pipeline SVG is redrawn. The file locations live in a new output-tree widget: `bin/out_rpc.json`, `generated/` (which, as Measured, only appears at run time), and files written to the cwd. |
| A4 | fixed | Tour note: colors 20–23, local task IDs 21/24/27/28/30, control task IDs 33–37 and 40, queue 0 plus queue 1 on WSE-3. Wording is aligned with the current ch07 table. |
| A5 | fixed | Q1 answer reworded: the device uses the color as a param, directly on WSE-2 and via `@initialize_queue` on WSE-3. |
| A6 | fixed | Brace rule stated precisely, with the measured error message. |
| A7 | fixed | Tags added for channels ≤16, wall time (moved into the caption as Measured), and all numbers in the code-tour notes (notes now carry inline tags plus a legend). |
| A8 | fixed | Image size changed to 3.5 GB. |
| A9 | fixed | Cards now say "on each PE (one or more files)". |

## Pedagogy
| ID | Status | Note |
|---|---|---|
| P1 | fixed | The tour shows the full verbatim run.py (28 lines) with notes on the import, argparse, `out.json`, `kw`, and the memcpy argument order. |
| P2 | fixed | New "contract between the three files" callout, plus the name-map widget. |
| P3 | fixed | New "fabric-size rule" subsection taken from the wrapper source, worked examples (8×4 → 15,6; 6×2 → 13,4, Measured), a rewritten flag table, and a wrapper-check widget. |
| P4 | fixed | Numbered setup recipe with the `env.sh` contents, the `/tmp` warning and a smoke test. The repo setup.sh is labelled as repo-only. |
| P5 | fixed | Resource-type table with links to the chapters that teach each type. Also states "only `mem1d_dsd` for a first program". |
| P6 | fixed | Q2 replaced with the program-03 P=16 question (answer: 4). A `<layout>` bullet was added so the answer has a source. |
| P7 | fixed | Q1 fixed, and a program-03 `@set_color_config` snippet added after the tour. |
| P8 | fixed | Added "why" notes for `[*]` exports, the mutability mismatch (with the measured error), and the `@fmacs` name and its siblings. |
| P9 | fixed | The resource-bug callout is now a list with links. The microthread bug is named, using cross-note 1's message. The trick paragraph now points to the program 02 streaming race. |
| P10 | fixed | Diagram relabelled. A new section explains that `out_i_j` numbers groups of PEs, not PE coordinates (shown with `cs_readelf -r`). |
| P11 | fixed | The page says where outputs land (cwd vs `out/`), and that "Stopped due to idleness" can mean a deadlock as well as success. |
| P12 | fixed | Clearer one-liners: `if` as an expression, braces, `*[N]` vs `[*]`, and pointers on PE functions. |
| P13 | fixed | New "Break it on purpose" list (6 items, including the WSE-2 rebuild), and the quiz grew from 3 to 7 questions. |
| P14 | fixed | `<simprint>` and `<debug>` snippets were verified against `csl-libs` and run, with real `sim.log` output. The csdb subcommands are listed as help-verified only. |

## Visuals
| ID | Status | Note |
|---|---|---|
| V1 | fixed | Figure 1 is now HTML cards. The pipeline SVG keeps only 4 short boxes, and the paragraph inside it moved to HTML. Remaining SVGs use the shared ≤680px scroll rule. |
| V2 | fixed | Tabs use `role=tab`/`aria-selected` with roving tabindex and ←/→ keys. Lines use `role=button` and `tabindex=0`, with Enter/Space and ↑/↓. The note is `aria-live`. |
| V3 | fixed | All three files are shown verbatim. Pins were added for `N`, `kw`, `@export_symbol(saxpy)` and others. Twin lines get grey pins whose note reads "Same as line n". Retitled "line by line". |
| V4 | fixed | A gutter shows the real line numbers, and notes print `file:line`. |
| V5 | fixed | Uses the shared `--on-accent`. The local `color:#fff` was removed. |
| V6 | fixed | Handled by the output-tree widget and the cwd label in the pipeline. |
| V7 | fixed | The dead marker is gone (Figure 1 replaced). The coordinate convention moved into the prose. |
| V8 | fixed | The note opens inline under the clicked line. Lines wrap with a hanging indent, so there is no horizontal scroll. |
| V9 | fixed | The caption is rewritten, so there is no orphaned full stop. |

## Depth
| ID | Status | Note |
|---|---|---|
| D1 | fixed | New "What cslc actually builds" section with 5 stages, a table of what splits a PE program (6×2: 3 ELFs, 6 with routes, re-measured), and an ELF-grid widget. One correction to the review: the link error for N=5620 is `.data.hi` plus "task table", not `.bss`. |
| D2 | fixed | New SdkLayout section: re-ran sdklayout-02 (81 cycles, 2×1 fabric, outputs listed), side-by-side code, an 8-row comparison table, and the sdklayout-04 limitation quote. The placement diagram for sdklayout-03 was skipped. |
| D3 | fixed | Error decoder with 9 measured rows and a Fix column. Two new rows: `set_color_config` before `set_tile_code`, and if/else without braces. Also added a 4-step hang procedure, simprint and debug snippets, and the `inst_trace` paragraph (coordinator note, verified). Correction: in our run `launch()` returned, and the stall surfaced at the next memcpy. |
| D4 | fixed | Collapsible reference card with 14 rows, every example copied from the SDK, plus a `--params`-unsigned callout. |
| D5 | fixed | Measured table (re-measured 4,752 B at N=64, 49,120 B at 5,610, link failure at 5,620, WSE-2 3,362 B) and a memory-bar widget. |
| D6 | fixed | Library table. Function names were checked in `csl-libs` (sqrt_f32 and tanh_f32 exist). `get_x_coord` source is quoted. |
| D7 | fixed | Measured `--out-routes` excerpt with an explanation. |
| D8 | fixed | Flag table split into wrapper and driver. The default `--arch=wse2` is in bold. Rarer flags are in a `<details>` block. |
| D9 | fixed | Annotated real `sim_stats.json`. Notes that `cycle_count` is end-to-end, that a fatal stop writes no `sim_stats.json`, and that kernels should be timed with TSC. |
| D10 | fixed | "Writing for both chips": 3 idioms (sdklayout-02, topic-12, program 03), with a link to ch05. |
| D11 | fixed | Merged into "Break it on purpose". |

Totals: 43 findings. 43 fixed, 0 partial, 0 skipped. One sub-item is deferred: the sdklayout-03 placement diagram (part of D2).

## New visuals and widgets
1. **Follow a name across the three files.** Threads for N, x, y, saxpy, memcpy_params and unblock. The matching lines are highlighted in commands.sh, layout.csl, pe_program.csl and run.py, and a rule readout explains each one. The widget can be driven from the keyboard.
2. **Host ↔ memcpy ↔ PE run stepper.** Eight steps, with the matching run.py line highlighted and a command-stream state bar. A "forget unblock" toggle shows the measured failure: `launch` returns, the D2H copy fails, and the run aborts with "kernel stall".
3. **"What will the cslc wrapper say?"** A W/H/offsets/channels/buffers/fabric calculator that applies the real wrapper checks in order and prints the exact RuntimeError, or the predicted number of PE programs. Includes a CS-2 mode.
4. **"Where did that file come from?"** A clickable tree of the output files, with who writes each file and a real excerpt.
5. **ELF grid.** The 6×2 rectangle coloured by ELF, with a route toggle (3 → 6 files).
6. **Memory bar.** A 48 KB bar with an N slider and a WSE-3/WSE-2 switch.

Verification: Playwright at 1100 and 390 px, light and dark. No page or console errors. No horizontal overflow (an earlier overflow at 390 px from long inline code was fixed). Every control was exercised, including keyboard navigation in the tour. Screenshots were reviewed and then deleted.

## Left for later
- sdklayout-03 placement diagram (regions, ports and auto-routed connections).
- The ch07 calculator and this chapter's wrapper widget overlap partly. Consider cross-linking them from ch07 as well.
- ch07 still says "7 columns narrower" without "at least" (cross-note 9). ch10 still says the `@fmacs` takes "tens of cycles"; measured is about 127. Both belong to other fixers.
- csdb's interactive CTF workflow is still unverified.
