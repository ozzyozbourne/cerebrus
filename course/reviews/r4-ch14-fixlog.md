# R4 fix log: Chapter 14, Lab 4 (SUMMA GEMM)

Edited `src/14-lab-gemm.html` (regenerated `14-lab-gemm.html` with `tools/build.py`) and one comment in
`programs/06-summa/pe_program.csl` (exit task). No other files changed.

## Experiment (needed for G1)
Scratch copy of program 06 in `/home/user/cerebras-sdk/tmp/r4fix-ch14/` (deleted afterwards), traces off, P = 2.
Added a kernel 0 variant using Chapter 6's `@map` over DSRs (DSR set 0; j outer, `@map` over column j of B,
A in src1 with `.save_address = true`), with and without C padded by one word (C declared after both A arrays,
DSDs at `C_mem[i + 1]`). All runs passed the numpy check. Compute cycles per step:

| chip, T | SDK loop | @map | @map + pad | ideal |
|---|---|---|---|---|
| WSE-3, 8 | 2,903 | 1,427 | 915 (56%) | 512 |
| WSE-3, 16 | 17,835 | 9,060 | 4,964 (83%) | 4,096 |
| WSE-3, 32 | 103,724 | 67,733 | 34,965 (94%) | 32,768 |
| WSE-2, 8 | 2,768 | 1,398 | — | 512 |
| WSE-2, 16 | 16,086 | 9,007 | 4,896 (84%) | 4,096 |
| WSE-2, 46 | 315,978 | 149,586 | 100,896 (96%) | 97,336 |

Per op: @map = 2·Mt + 6.3 / 3.4 / 2.1 (Mt = 8/16/32), padded = Mt + the same. cs_readelf (T = 16, pad):
A_tile 0x170c, A_buf 0x1f0c, C_mem 0x270c (C_mem[1] at 0x2710).
Also the half-fix per-step stamps (G4): P = 2, T = 16, WSE-3, PE (0,0): compute [13,739, 17,835], wait
[1,014, 4,822], total 37,539 vs 37,814 unfixed (all steps 17,835, waits ≈ 1,000).

## Items from r4-ch14.md
- E1 Fixed. Q7 now says 94.4 vs 101.3 cycles per instruction, ≈ 30 vs 37 fixed on top of the 64 for the clash.
- E2 Fixed. Callout and kernel-1 bullet explain 1.87 + 77/(Mt·Nt) (2.17 / 1.95 vs 2.18 / 1.95 measured; 1,574 vs 1,594 at T = 8); "only approximate" dropped.
- E3 Fixed. Cites Ch 13's "Fewer messages" exercise and Ch 6 #banks for the chip dependence.
- E4 Fixed. Row relabelled "T = 42 (links at P = 4; P = 743 not checked)".
- E5 Fixed. "0 (and 1 on WSE-3) are memcpy's"; "the program's IDs are the same on both chips".
- X1 Fixed. Lede: 18% at the default tile, about a third at T = 32 (plus 94% with @map + padding).
- X2 Fixed. "each PE's own timestamp counter (TSC)", glossary-linked.
- X3 Fixed. Chart hint states the mechanism model (2·Mt + c, c 29 → 37) is the explanation and the least-squares lines are for drawing only; intercepts are not per-instruction costs.
- X4 Fixed. The 209 explained as the run's "other" (set-up, gaps, exit) in #next and exercise 7(c).
- X5 Fixed. Three-row claim / key number / where table opens "What the numbers say".
- X6 Fixed. Table now has broadcast and compute both as "sum of P steps" and per step.
- G1 Fixed (measured). Callout bullets link Ch 6 #dsrs (N + 2 vs N + 35) and the matvec's one-word shift; "Kernel 0's fixed cost" (#fixed-cost) now has the @map sketch, the measured table above, and the padding placement; lesson paragraph, design step 9, X5 summary and a new scaling row (WSE-2 T = 46: 1.12 PFLOP/s, 92%, P = 743 link not checked) use it; exercise 8 now builds it with hints and measured expected results.
- G2 Fixed. New #k1-walk: stride-0 rule, 2 × 2 × 2 address walk table, increments Mt / 1, why @fmacs (scalar multiplier) cannot do it in one op, note on the rereading operand.
- G3 Fixed. New #ridge paragraph: intensity T/2, ridge T = 2, ideal passes broadcast at T ≈ 9, measured crossover T ≈ 4, 3–10 cycles per MAC; links Ch 1 roofline and glossary.
- G4 Fixed (measured). Callout now explains pacing without a barrier and quotes the half-fix per-step stamps.
- G5 Fixed with E3.

## Cross-chapter items (CCN 30–38 and other auditors)
- CCN 30 Fixed. One-line placement rule with link to 06-dsds.html#banks in the callout; @fadds rates qualified by placement (C and T in the same bank) in the kernel-1 bullet, callout and Q7; retired "3.2–4" f16 → "about 4 on WSE-3 in every placement; 2–4 on WSE-2 by placement" (lesson and caveat paragraphs); 13–16% → about 13% (and 24% for the rewrite).
- CCN 31 Fixed. pe_program.csl:123 comment now "the host's next command (memcpy_d2h of C) can now run; launch() itself returned at once" (now lines 123–124). Code-walk prose: launch returns at once, the next memcpy waits (link Ch 7 #command-stream).
- CCN 33 Fixed. Calculator gains a "1.4 GHz (WSE-3 press estimate)" option; hint states no official WSE-3 clock, 850 MHz SDK [SDK], 1.1 GHz WSE-2 [Vendor], 1.4 GHz [Analyst][Unverified]. Scaling section stays at the WSE-2 1.1 GHz clock (it is a WSE-2 table).
- CCN 34 Checked, already consistent (2.0 / 1.0 router hop, 9.2 / 6.0 CE hop).
- CCN 32, 35, 36, 37 Not applicable to this page.
- CCN 38 Fixed. Every remaining plain "Chapter N"/"Lab N" pointing at an idea is now a link (to section anchors where they exist: 01#two-numbers, 04#routes, 05#join-rule, 06#dsrs/#banks/#moving-dsd/#builtins/#dsd, 07#command-stream, 12#collectives/#broadcast/#two-colors/#streaming/#measuring/#composing, 13#fixed-cost, 15#allreduce, App B #checker). Glossary links on first use: SUMMA, collectives-2d, TSC, multicast, DSR, checkerboard, teardown, back-pressure, join, task picker, bank clash, microthread, ridge point, outer product. All 58 hrefs resolve.
- r4-appB line 119 Fixed. Exercise 3 now quotes SAXPY 2.85 / 4.24 KB (Ch 3 #memory-map), not the matvec 3.1 / 4.6 KB.
- r4-appB G2/#checker Fixed (this page's side): design section links appendix-b-cuda-to-csl.html#checker and says it does not model library-owned resources.
- r4-ch06 G6 Partly (this page's side): code-walk note names the shared "1-D DSD × scalar, move, repeat" pattern and links 06#moving-dsd. (Ch 6 already links forward.)
- r4-ch07 E2 Fixed for program 06 (comment) and the Ch 14 prose.

## Verification
Playwright, 1100 px and 390 px: no console or page errors, no horizontal overflow; drove the stepper (Next, Play/Pause), chart (chip, T slider), calculator (new clock option); dark-mode screenshot of the new sections checked. Built with `python3 tools/build.py`.

## For other pages
- Ch 7 (r4-ch07 E2) cites "programs/06-summa/pe_program.csl:123"; the comment is fixed and now spans lines 123–124.
- Ch 17 G4 and Ch 18 (E8, lessons, "GEMM: 32% of the f32 ideal"): Ch 14 now also measures kernel 0 with @map + one word of padding at 56% / 83% / 94% of the f32 ideal (T = 8 / 16 / 32, WSE-3, P = 2) and 96% on WSE-2 at T = 46; the extrapolated whole-wafer figure is 1.12 PFLOP/s f32, 92% of peak (WSE-2, P = 743, link not checked). "18–32% (SDK loop), 51% (outer product)" remain correct as the shipped kernels' numbers.
- App B constants (r4-appB G2c): an @map kernel 0 costs ≈ 2·Mt + 2–6 per op clashed, Mt + 2–6 padded (Ch 14 #fixed-cost).
- Ch 6 could cite Ch 14 #fixed-cost as a second measured instance of the @map + DSR lever (GEMM, 94% at T = 32).
