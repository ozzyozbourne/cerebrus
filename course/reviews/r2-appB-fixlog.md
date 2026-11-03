# Fix log: Appendix B (CUDA to CSL, budgets, constants), round 2

Inputs: r2-appB-accuracy.md (A1–A16, C1–C2) and r2-appB-visuals.md (V1–V6, P1–P9).
Files edited: appendix-b-cuda-to-csl.html; one sentence each in 06-dsds.html (C1) and 07-host-io.html (C2).
Not touched: course.css, course.js, other chapters.

## Accuracy
- **A1 fixed overhead and usable memory.**
  - The budget card's overhead row now gives the smallest measured overhead: SAXPY, 4,240 B on WSE-3 (incl. 1 KB task table) and about 2,850 B on WSE-2 (Ch 10). It labels 4,636 / 3,134 B as "matvec benchmark (N = 8)" and says the overhead grows with code: Lab 3 reaches about 5.5 KB on WSE-3 and about 3.9 KB on WSE-2 (Derived from its link limits).
  - The "usable" row now gives measured ranges with their sources:
    - WSE-3: 43,600–44,900 B. SAXPY 5,610 links at 49,120 B; 5,620 fails; Lab 3 links at n ≈ 5,450.
    - WSE-2: 45,200–46,300 B. SAXPY 5,784; Lab 3 at about 5,650.
  - Checker: the overhead defaults to 4,240 / 2,850, and `USABLE` is removed.
    - SRAM status: "fails" only above 49,152 B, and "check: within 512 B of 48 KB … bisect with cs_readelf -m" inside the last 0.5 KB.
    - Verified: WSE-3 N = 5,610 → 49,120 B "check"; 5,620 → 49,200 B "fails". WSE-2 N = 5,784 → 49,122 B "check"; 5,800 → "fails".
  - The phrase "more code raises it (SAXPY …)" is gone.
- **A2 units.** I removed every "44.5 KB". It now reads "about 44,500 B (≈ 43.5 KB)" in the stat tile, the `__shared__` row and the occupancy row. The budget intro states "KB = 1,024 B". The WSE-2 row reads "≈ 44–45 KB" for 45,200–46,300 B.
- **A3 / P1 25-pt preset.**
  - Colors set to `4-7`.
  - The preset is renamed "25-point stencil (WSE-2 SDK benchmark) ported to WSE-3". A note explains IDs 2 and 3 < 8, 24 = memcpy, and 25–26 outside 8–20.
  - It now reports only the local-task-ID failure.
- **A4 WSE-2 IDs 22/23.** Now "fails: taken by memcpy on WSE-2, the data task of memcpy's color 22/23". The budget-card row says the same. On WSE-2, ID 20 warns ("memcpy's context-switch color").
- **A5 streaming colors.**
  - p02 now has `col: ""`, so it counts 1 color.
  - The hint and the result message say not to list streaming colors under "colors you route".
- **A6 microthread message.** It now lists the shared pairs, then states once: "Lab 3's version of this failed at run time with FATAL "trying to term ut_instr[3], but it's not ours" on both chips". The microthread number is no longer substituted.
- **A7.** Color 20 is now "context switch" (card and checker).
- **A8 task 24.** The message now reads "memcpy's SYS_EN_MAIN (first task after a context switch); the SDK stencil reuses it on WSE-2, so avoid it unless you know your memcpy mode". Status is bad on WSE-3 and check on WSE-2.
- **A9 / P4 Lab 3 arithmetic.** The closing callout now lists its terms: about 15–17 start-up for an isolated op, about 6 for later ops in the same task, 14.6 per transfer, 13 bookkeeping, and 9 / 6 per pass-through PE. It works the sum: 4 × 14.6 + 13 + 3 × ≈ 6 (19, measured) ≈ 90, and 2.5 = 0.5 + 1 + 1. It notes that using 15–17 for every op would give about 108.
- **A10.** The WSE-2 chain-reduce cell now reads 54 / 64 / 84 / 124 for P = 2 / 4 / 8 / 16 (Ch 12), and the note reads "≈ M + 7P (WSE-3) / M + 5P (WSE-2)".
- **A11.** Stale CROSS note 4: see the coordinator list below.
- **A12.** The TT wording in the Rosetta intro and in the global-memory row is now "GDDR6 beside the chip, reachable from every core over the NoC". The intro now also links Ch 16.
- **A13.** p04, p04bad and p04ut now have other bytes = 24 (t0, t1, tsc). p02 has other = 4 (count).
- **A14.** The grid row now says "must be at least W + 7 by H + 2", with a link to the new figure.
- **A15.** The cache row and card row now say "we found no CSL API for it; the CSL standard library never mentions it".
- **A16.** The FIFO row now reads "allocate FIFO buffers on a 16 B / 8 B boundary (FIFO_MIN_ALIGNMENT)". The padding note moved to a new "SRAM banks" row (16-byte stripe; matvec pads rows to 16 B).
- **C1 (Ch 6).** "about 35" is now "about 33–35 cycles per step". The appendix grid-stride row changed the same way.
- **C2 (Ch 7).** Added: "where a CUDA cudaMemcpy would block forever, here the copy errors after about 4 s".

## Visuals and pedagogy
- **V1 constants table.** I removed the `.consts td:nth-child(2/3)` nowrap rule, which caught the Notes cells of colspan rows. The page-local style now gives Notes `min-width: 14em`. At 1100 px the table measures 826/826 (it was 2,148 px).
- **V2 Rosetta.** Dropped the nowrap on the first column. Columns are now about 21% / 50%. Page height at 1100 px is about 15,200 px including the new sections; it was 14,300 without them.
- **V3 figures.** Both figures are inline SVG drawn with the course.css classes and `cssVar`, and the ◐ toggle was checked on them.
  - (a) `#mem-fig`: 48 KB bars for WSE-3 and WSE-2, to scale. They show code + runtime, the task table, a hatched "grows with code" band (up to Lab 3) and the arrays, with a legend.
  - (b) `#fabric-fig`: a 5 × 3 rectangle in a 12 × 5 fabric. It shows the halo ring, 3 memcpy columns west and 2 east, the offset 4,1 arrow to PE (0,0), and the `--fabric-dims` line.
  - The checker also has a live memory bar (`#bu-mem`) that fills from the SRAM inputs.
  - The optional (c) ladder figure was not added; the SAXPY side-by-side covers that mapping.
- **V4 compile line.** The command now appears in its own `<pre id="bu-cmd">` with `white-space: pre`. It wraps once with a `\` and adds `cs_python run.py --name out`.
- **V5 green pill contrast.** `.pill.ok` text is now `color-mix(--green 78%, --text)`. The Measured-tag contrast comes from course.css: see the coordinator list.
- **V6 meters.** No meter for rx ports or fabric inputs, and none for I/O channels when the limit is 1.
- **P2 preset notes and chip switch.**
  - New `#bu-note` explains every preset.
  - p04ut and p25 append "Chip switched to WSE-3." when they switch.
  - Switching back to WSE-2 adds "this preset is meant for WSE-3".
  - The p04bad note gives the FATAL cycles (2,123 / 2,125), links the cause to Ch 5, and points to both fixes.
- **P3.** New `#saxpy` section: CUDA kernel + host side by side with program 01's layout.csl, pe_program.csl and run.py, trimmed. Lines are ≤ 54 characters, so the code fits two columns at 1100 px and stacks below 680 px. A paragraph maps each line to its Rosetta row and explains `unblock_cmd_stream()`.
- **P5 checker limits now match the table.**
  - WSE-2 local IDs: "23 (0–20, 25, 26), minus receive colors". The table says the same.
  - WSE-2 queue 1 now gets "check: free on WSE-2 but memcpy's on WSE-3: start at 2 so the code ports".
  - The WSE-2 data-tasks row is OK, with the binding rule given as its explanation. Program 02 on WSE-2 now "fits every documented limit".
- **P6.** The compile line now includes `-o out`, and each preset adds its `--params`, copied from its commands.sh:
  - p01 `N:64`
  - p02 `N:100 --params=MEMCPYH2D_DATA_1_ID:0`
  - p03 `P:8,M:32`
  - p04 `P:8,n:16`
  - p05 `R:6,M:32`

  Custom input prints "(add your own --params)".
- **P7 all errors shown.**
  - Colors, local IDs, control IDs, queues and data tasks now collect every message. Example: `abc,99,21,3,3` gives "cannot read abc; 99 does not exist; 21 belongs to memcpy; listed twice: 3".
  - Number fields are clamped in place: H = 0 becomes 1 in the field itself. The rx and fabric-input fields are clamped to their max.
- **P8 glossary links.** Links to Appendix A anchors added at first use: DSD, DSR, GPR, TSC, rx, counter filter, data task, local/control task, microthread (also covers `.ut_id`), FIFO, software-managed cache, FPU/SFPU, CB.
- **P9.** The warp row now explains that the 8 FP16 lanes are a ceiling. Measured f16 FMAC runs at 3.2–4 per cycle because each element also reads y and A and writes y in SRAM, so memory traffic appears to set the rate. This is labelled an inference and links Ch 3 and Ch 6.

## Validation
- Playwright at 1100 and 390 px, light and dark, plus the ◐ toggle: zero page or console errors.
- No page-level horizontal overflow (scrollWidth equals the viewport). At 390 px the wide tables and SVGs scroll inside their boxes.
- I drove every preset on both chips, along with the Rosetta filters and TT toggle, the link-limit cases and a stress input.
- All 129 in-page links resolve.
- Screenshots were inspected for the memory and fabric figures, SAXPY, the checker (incl. WSE-2 p04bad) and constants, in both themes.

## For the coordinator
1. **Ch 18:** "~44.5 KB" / "about 44.5 KB" appears at lines ~108, 143 and 329. Change it to "about 44,500 B (≈ 43.5 KB)", and note that Lab 3 itself fits only about 43,600 B.
2. **CROSS_CHAPTER_NOTES note 4 is stale.** It should read: slope from 10 → 100 steps; WSE-2 134.1 at n = 16 (not "100 vs 200 steps", "WSE-2 126").
3. **CROSS note 13** calls 4.6 KB / 3.1 KB "the fixed overhead of a minimal program". The smallest measured program is SAXPY, at 4,240 B (WSE-3) and about 2,850 B (WSE-2); 4,636 / 3,134 is the matvec benchmark. **Ch 3 #memory-map** (line ~197) uses the same "minimal memcpy program" label for 4,636 / 3,134 and should say "matvec benchmark".
4. **Ch 10 vs Ch 11 SAXPY link limit.**
   - Ch 10 says N = 5,610 links at 49,120 B and 5,620 fails.
   - Ch 11's exercise says the largest that links is 5,615 (44,920 B of arrays). With a constant 4,240 B overhead that would be 49,160 B > 49,152 B.
   - Either the overhead is not constant (alignment) or one number is off. Worth a quick cs_readelf check.
5. **Ch 5 #budget** calls the 25-pt stencil's 18 tasks "the entire user local-task budget" on WSE-3. They exceed it (13 safe IDs), so write "more than".
6. **course.css:** `.tag.measured` and `.tag.indep` green text on green-soft reaches only about 4.3:1 at 11.5 px in light mode (V5). I fixed the page-local `.pill.ok`, but the tag colours belong to you.

## Open issues
- The 512 B "near the limit" margin is a judgement call. It is based on the 4,240 → 4,636 B spread between SAXPY and matvec. Lab 3's larger overhead (about 5.5 KB) means a Lab 3-sized program can still fail with the default overhead. The hint says so, but the checker cannot know your code size.
- The optional CUDA grid/block/thread ladder figure (V3c) was not drawn.
- At 390 px the Rosetta, budget and checker tables still scroll horizontally inside `.table-wrap`. There is no page overflow.
