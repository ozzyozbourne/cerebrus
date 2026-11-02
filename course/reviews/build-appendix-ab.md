# Build: Appendix A, Appendix B, "If you know CUDA" callouts

Chapter numbers below are the NEW numbering.

## Built
- **appendix-a-glossary.html — Glossary and number formats.**
  - 131 glossary terms (Cerebras 33, CSL & SDK 46, Tenstorrent 20, GPU 20, General 12). Each links to the section that teaches it and has its own `#g-…` anchor. The page supports search with highlighting, machine filter chips and an A–Z jump bar; opening a `#g-…` link highlights that entry.
  - Number-format section: an SVG bit-layout figure (fp32, bf16, fp16, cb16, FP8 E5M2/E4M3, FP4 E2M1, int8, BlockFP8, NVFP4, MXFP4) and a range and precision table.
  - Bit explorer widget (round-to-nearest-even encoding, click a bit to flip it, next value up).
  - Block quantiser widget (bf16, per-tensor E4M3, bfloat8_b, bfloat4_b, NVFP4, MXFP4, with an outlier switch).
  - Table of which machine runs which format.
  - The glossary HTML was generated from a scratch Python list that has now been deleted. From now on, edit the `<dl id="gl-list">` entries in the page directly.
- **appendix-b-cuda-to-csl.html — CUDA to CSL, budgets and constants.**
  - CUDA → CSL/WSE → TT-Metalium map: 33 rows in 6 groups, with a filter and a switch for the TT column. "No equivalent" rows are marked.
  - Per-PE budget card for WSE-3 and WSE-2.
  - Budget checker widget covering memory, colors, rx ports and fabric inputs, local and control task IDs, queues, data tasks, microthreads, fabric dims and channels. It has presets for programs 01–05, the Lab 3 queue bug, the `.ut_id` fix, and the 25-point stencil's task IDs. It also prints the cslc command line.
  - Measured cost-constant table.
- **"If you know CUDA" callouts** (`div.callout.cuda`, which renders as the standard blue callout; no CSS change):
  - Ch 3 (#no-caches): PE vs SM and thread; 48 KB vs `__shared__`/L1/L2.
  - Ch 5 (before #buf): task vs thread and kernel; run to completion vs warp scheduling.
  - Ch 6 (before #moving-dsd): a DSD vs a grid-stride loop; about 35 cycles per scalar loop step.
  - Ch 7 (before #command-stream): memcpy and RPC vs cudaMemcpy and `<<<>>>`; why "launch returned" means nothing.
  - Ch 10 (before #tour): three files vs a `.cu` file plus host code.
- **Anchor fixes:**
  - Added heading ids to 17-gpu.html (13, including `inside-sm`) and 18-comparison.html (`programming-model`, `budget`, `stack`).
  - Ch 8's "KV-cache arithmetic" heading no longer exists in the working tree, so the glossary links to `08-systems.html#inference` instead.
  - All internal links in A and B resolve.

## Numbers
- Nothing new was measured in the simulator for this task.
- The f16 encoding check (1.0 = 0x3C00 etc.; `--fp16-format=bf16/cb16` leaves comptime constants unchanged, and run-time f16 arrays then fail to compile on both chips) was measured earlier in this task with cslc and the simulator from SDK 2.10.1.
- All other figures are copied from the chapters and CROSS_CHAPTER_NOTES, with the chapter tags kept. Format ranges are derived from the layouts.

## Validation
- Playwright at 1100 and 390 px, light and dark, plus the ◐ toggle, on A, B, Ch 3/5/6/7/10/17/18: no page or console errors and no horizontal overflow.
- Every widget control was driven: search, chips, letters, hash link, every explorer format with every preset and a bit flip, every quantiser format with the outlier on and off, Rosetta filters and TT toggle, every budget preset on both chips, and a stress input.
- Screenshots inspected. A duplicated warning in the checker's microthread row was found and fixed.

## Open issues
- cb16's 1/6/9 layout is unverified; the page tags it that way. The documentation for `--fp16-format` was not available.
- MXFP4 is not in any course source and is listed for comparison only, tagged Unverified.
- The budget checker's WSE-2 "usable ≈ 45.2 KB" comes from Lab 3's link limit, not from a minimal program.
- On WSE-2 the checker cannot tell which microthread an op that uses both an input and an output queue takes, so it warns about it.
