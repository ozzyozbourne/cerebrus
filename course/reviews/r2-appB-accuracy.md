# Review r2: Appendix B (CUDA to CSL, budgets, constants): accuracy + reference

Scope: appendix-b-cuda-to-csl.html (Rosetta table, budget card, budget checker, constants table, closing callout) plus the five `callout cuda` boxes in Ch 3, 5, 6, 7, 10. I checked them against SDK 2.10.1 (`csl-libs/memcpy/sys_params.csl`, `memcpy/wse2|wse3/*.csl`, `target/wse2|wse3.csl`, `benchmarks/25-pt-stencil/layout.csl`), the chapter text, the program sources, and CROSS_CHAPTER_NOTES 1–25. I also drove every checker preset on both chips in Playwright: no page errors. Every internal `href="…#id"` resolves.

## Findings

**A1 — high — Budget card "fixed overhead" and "usable" rows, plus the checker's SRAM row (`OVH`, `USABLE`).**
The page calls 4,636 B (WSE-3) and 3,134 B (WSE-2) the overhead of a "minimal memcpy program", and it says "more code and tasks raise it (SAXPY: 4,240 B on WSE-3)". That contradicts itself, because SAXPY is *smaller* than the so-called minimum. The 4,636 B figure is the single-tile-matvec benchmark at N = 8 (Ch 3 memory map). Ch 10 measures SAXPY's fixed part at 4,240 B on WSE-3 and "about 2.85 KB" on WSE-2, and says "even an empty program uses about 4.2 KB". As a result, the checker fails programs that the course measured as linking:
- WSE-3, SAXPY N = 5,610: Ch 10 shows it linking at 49,120 B. Entering f32 = 11,220 in the checker gives 44,880 + 4,636 = 49,516 B, reported as "fails".
- WSE-2, SAXPY N = 5,784: Ch 11 says it links (46,272 B of arrays). The checker gives 49,406 B, also "fails". `USABLE.wse2 = 45,200` comes from Lab 3, which carries more code.
- Lab 3 on WSE-3 links only to n ≈ 5,450, about 43.6 KB of arrays (Ch 13). So the real "usable" figure spans about 43.6–44.9 KB, depending on the code.

Fix: relabel the overhead as "matvec benchmark (N = 8)". Give the measured range: about 4.2–4.6 KB on WSE-3 and about 2.9–3.1 KB on WSE-2. Default the checker to the low end, or add an overhead preset per program. Turn the "fails" verdict near the limit into "check: within ~0.5 KB of the measured link limits, bisect with cs_readelf -m". Drop the phrase "more code raises it (SAXPY …)".

**A2 — med — "≈ 44.5 KB" appears in four places: the stat tile, the Rosetta `__shared__` row, the occupancy row, and the lede of the budget card.**
On this page 48 KB = 49,152 B, so KB means KiB here. 44,500 B is about 43.5 KB, and Ch 3 says so explicitly ("≈ 43.5 KB, '~44 KB'"). CROSS note 13 says "~44 KB". The WSE-2 row has the same problem: "≈ 45 KB (… 45.2 KB of arrays)" for 45,200 B, which is 44.1 KB. Ch 18 repeats "~44.5 KB" (lines with 44,500 B).
Fix: write "≈ 44,500 B (≈ 43.5 KB)" and "≈ 45,200 B (≈ 44 KB)". Tell the Ch 18 owner.

**A3 — med — Checker preset "25-point stencil's task IDs on WSE-3".**
The preset sets colors to `0-20`, so the checker reports "color 20 belongs to memcpy" and counts 21 colors. The SDK stencil routes only colors 4–7 (`layout.csl`: east/west/north/south channel = 4,5,6,7). Ch 5 says the same: "skips 4–7 because those are its channel colors". The failure is spurious and hides the real lesson, which is about task IDs. Fix: `col: "4-7"`.

**A4 — med — Checker, WSE-2 local task IDs 22 and 23.**
On WSE-2 these get only "check" ("outside the safe 8–20"). But on WSE-2 a data-task ID is its color, and memcpy binds data tasks to color 22 (`PSEUDO_WTT_RXACT_CMD = @get_data_task_id(RXACT_CMD)`, wse2/memcpyh2d.csl) and to color 23 (the H2D data color). Ch 7's reserves table says the same ("IDs 0–23 are also the data-task IDs of the colors"). Fix: on WSE-2, treat 22 and 23 like 21: "taken by memcpy (data task of color 22/23)", status bad.

**A5 — low/med — Checker colors row with streaming.**
`nC = new Set(cols).size + str` counts the streaming color twice when the user also lists it, and preset p02 does exactly that (`col: "0", str: 1` gives "colors 2"). Program 02 uses one color: Ch 7 says "program 02 gives color 0 to its stream". Fix: set p02 to `col: ""`. Also add to the hint: "do not list streaming colors under colors you route".

**A6 — low — Checker microthread message.**
For every shared microthread *u*, the message says "measured in Lab 3 as FATAL 'trying to term ut_instr[u] …'". The p04bad preset therefore prints a "measured" `ut_instr[2]` message, but only `ut_instr[3]` was ever observed (CROSS notes 1 and 11; Ch 5). Fix: use "Lab 3's version of this failed at run time with FATAL 'trying to term ut_instr[3], but it's not ours' on both chips", without substituting *u*.

**A7 — low — Budget card, routable colors: "20 (internal switching)".**
sys_params.csl defines color 20 as `SYS_RXCTX`, "the routing from context buffer", for context switching. Ch 7 also says "20 context switch". Fix: "20 (context switch)".

**A8 — low — Checker treats task 24 as a hard fail ("taken by memcpy").**
24 is `SYS_EN_MAIN`, "first task after context switch". Ch 5 notes that the WSE-2 25-point stencil binds its own task to 24, so "24 is probably needed only in some memcpy modes". Fix: keep the status bad if you like, but say "SYS_EN_MAIN (context switch); the SDK stencil reuses it on WSE-2, so avoid it unless you know the mode".

**A9 — low — Closing callout "Putting the constants to work".**
The callout says "Lab 3 is exactly that sum". Its recipe uses an isolated start-up of about 15–17 cycles per op and about 15 cycles per transfer. For Lab 3 that gives about 4 × 15 + 3 × 16 = 108 + 2.5·n, not 90 + 2.5·n. Lab 3's 90 is 4 × 14.6 + 13 (bookkeeping) + about 19 (three in-task start-ups of about 6, Ch 13 #fixed-cost). Fix: say "use ≈ 6 cycles per op for consecutive ops inside one task, add ≈ 13 for step bookkeeping. Lab 3's 90 = 58.4 + 13 + 19".

**A10 — low — Constants table, chain-reduce row.** The WSE-2 cell shows "–", but Ch 12 lists WSE-2 values of 54 / 64 / 84 / 124 for P = 2 / 4 / 8 / 16 (Measured). Fill them in.

**A11 — low — CROSS_CHAPTER_NOTES note 4 is stale (for the coordinator, no page change).** The appendix follows Ch 13 correctly: slope from 10 → 100 steps, WSE-2 134.1 at n = 16. Note 4 still says "100 vs 200 steps" and "WSE-2 126". Update the note so later checks don't flag the right number.

**A12 — low — Rosetta intro and global-memory row, TT column.** "DRAM behind every core" and "GDDR6 behind every core" are wrong. Ch 16 describes GDDR6 *beside the chip*, reached through 24 DRAM tiles (8 channels) over the NoC. Fix: "GDDR6 beside the chip, reachable from every core over the NoC (interleaved or sharded)".

**A13 — low — Preset p04 "other bytes" = 12.** Program 04 has `t0`, `t1` (3 u16 each, 12 B) plus `tsc` (6 u16, 12 B), so 24 B in total. Programs 03 and 05 (12 B) are right.

**A14 — low — Rosetta "grid" row.** "the simulated fabric is W + 7 by H + 2". Per CROSS note 9 this is a minimum: write "at least W + 7 by H + 2". The budget card already says "at least".

**A15 — low — Rosetta cache row and budget card.** "CSL does not expose it" is stronger than the source. Ch 3 says only that the public sources don't say how CSL exposes it and that the stdlib never mentions it. Fix: "no CSL API for it that we found".

**A16 — low — Budget card, FIFO alignment row.** The rule cell "pad rows to 16 B to avoid bank conflicts" is the matvec padding note (Ch 3 #bank-model), not a FIFO rule. Move it, or replace it with "allocate FIFO buffers on a 16 B (WSE-3) / 8 B (WSE-2) boundary".

## "If you know CUDA" callouts (Ch 3, 5, 6, 7, 10)
All five are accurate and consistent with their chapters and with Appendix B. Two optional nits:
- **C1 — low — Ch 6.** "about 35 cycles per step Measured". Ch 6's own table gives (6,352 − 4,214)/64 ≈ 33.4, and CROSS note 16 says "~33–35". Prefer "≈ 33–35".
- **C2 — low — Ch 7.** "As with an asynchronous CUDA launch, a kernel that never finishes shows up at the next copy". In CUDA a hung kernel makes the next cudaMemcpy block forever. Here the next copy *errors* after about 4 s. Add "here it errors rather than hangs" to sharpen the contrast.

## Checked and correct (no action)
- memcpy colors 21/22/23; local IDs 21, 24, 27, 28, 30, with 29 teardown and 31 NOP; control IDs 33–37 and 40; queue 0, plus queue 1 for commands on WSE-3; the 5-bit activate field (activatable IDs < 31); switch-capable colors.
- Queue counts 8/8 (WSE-3) and 8/6 (WSE-2) match `target/*.csl` NUM_*_QUEUES. WSE-3 queue depths match the wse3/memcpy.csl comment.
- Control IDs [0,64); task priority; rx and fabric-input rules; filters; caches; DSR/GPR counts; FIFO's 2 microthreads.
- Fabric 750 × 994 → 743 × 992 at offsets 4,1; ≤ 16 channels; 7 Gb/s, 200 µs, 175 KB break-even, 0.26 wavelets/cycle.
- Every row of the vector-op table, the stride table, the matvec fit (54 + N + N² = 4,214), f16 matvec 1,335 / 2,165, and the collision numbers (2,064 vs 1,040; 158.2 vs 127.7; 8,310 vs 4,214).
- Hop 2.0 / 1.0 and CE hop 9.2 / 6.0; chain reduce 58…273; collectives 754 vs 58; about 16 wavelets per hop.
- Lab 3 100.2 / 130.2 / 250.2, P = 2 101.0, 14.6 and 13; program 01 split (7,740 / 6,826 / 3,640 + 64·N); bandwidth-test numbers; 50-cycle idle stop.
- The Program 02 "5 short" barrier result.
- TT facts: 8×16·16×16 FPU, 32-lane SFPU, CB 32/64, CQ0/CQ1, ttsim.
- The `--params` unsigned-only rule and the default `--arch=wse2`.
