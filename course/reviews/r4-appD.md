# R4 audit: Appendix D (SDK example index), page-id appD

**Verdict: Mostly correct. Explanation quality: good (as a reference), fair (as a learning path).**

How I checked:
- Listed every directory and `commands_wse*.sh` under `extras/…/examples/{tutorials,benchmarks}`, plus `csl-libs/kernels` in the SIF.
- Read the head of every README.rst and compared it with the "What it teaches" column.
- Parsed `D[]` with a script. For every "Where" link I resolved the anchor against the target file's ids and headings, and grepped every chapter's text (scripts excluded) for every example name.
- Checked `sdk_debug_shell` and `env.sh` for the mount claims.

All r2 findings (A1–A3, R1–R7, V1–V4, P1–P7) are fixed. I re-report none of them. The remaining problems are mostly about order and connection, not facts.

## Errors

**E1 · low · Ladder, "Ch 10" rung.** The rung lists `topic-13-simprint` before `topic-12-debug-library`, and the hint says "suggested order, easiest first". The topic-13 README says "This example modifies the previous example". It is the topic-12 program with `<simprint>` swapped in, so it should follow topic-12. **Fix:** swap the two entries, or add the note "a variant of topic-12".

**E2 · low · Chapter lists vs the stated filter policy.** The page says the filter "finds every chapter that names the example". Four misses remain:
- Ch 10's library-map row for benchmark-libs (10-csl-toolchain.html:306) names `preconditioned-conjugate-gradient`, `bicgstab` and `power-method`. None of the three rows includes 10.
- Ch 15 · How it scales (15-lab-cg.html:714) now names "the SDK's preconditioned CG uses Jacobi" (README.rst:11 confirms Jacobi). The PCG row has no Ch 15 in its filter, and only a "concept" link to #modules.
- `bicgstab` has 13 in its filter (the CS-1 BiCGSTAB caveat in 13-lab-stencil.html:471), but its Where cell has no Ch 13 link.

**Fix:** add 10 to the three rows, and add 15 with a `15-lab-cg.html#scaling` link to PCG. Either add a Ch 13 link to bicgstab or drop 13 from its filter.

**E3 · low · Callout code block.** `cp -r …/conjugate-gradient …/benchmark-libs ~/sdk/` fails on a fresh account ("target '~/sdk/' is not a directory"). With several sources, `cp` needs the target directory to exist already. **Fix:** put `mkdir -p ~/sdk` before the `cp` line.

**E4 · low · Callout, "Most examples print `SUCCESS!`".** This is true (50 of the 54 runnable examples), but the four exceptions are not named. `bandwidth-test`, `row-col-broadcast` and `spmv-hypersparse` have no `SUCCESS` in any .py file, and `gemv-00` has no script. Two of the three are on the ladder (Ch 7). A learner running them may think the run failed. **Fix:** add "(bandwidth-test, row-col-broadcast and spmv-hypersparse print measurements instead)".

## Explanation problems

**X1 · "How this index was made", ¶2.** The paragraph says "It extends the Phase 3 SDK coverage audit, with two corrections". That is internal project history the learner cannot see. **Fix:** delete the sentence. The facts it carries (fft-3d and topic-15 are WSE-3 only, gemv-00 has no script) are already in the stats and the Notes section.

**X2 · No "anatomy of an SDK example".** The page tells the learner to `bash commands_wse3.sh`, but never says what is in an example directory, or what that script runs. The directory holds README.rst, layout.csl, pe_program.csl or src/, and run.py. The script runs `cslc … --fabric-dims --fabric-offsets --params --memcpy`, then `cs_python run.py --name out`. Some examples also differ in layout: 25-pt-stencil has no `src/`, and fft-3d ships only layout.csl and run.py because its code lives in the SIF. **Fix:** add two sentences before the callout, linking to `10-csl-toolchain.html#three-files` and Ch 10's flag table. Also say "read README.rst first; each one says which earlier example it extends".

**X3 · The "Labbed" status does not name the course program.** The legend defines Labbed as "a course program does it", but no row says which program. **Fix:** add the program directory to the note or path line of each Labbed row:

| SDK example | Course program |
|---|---|
| gemv-01, gemv-03, topic-02 | `programs/01-saxpy` |
| gemv-09, topic-03 | `02-wavelet-tasks` |
| gemv-06 | `03-row-reduce` |
| gemv-07 | `05-column-broadcast` |
| topic-11, gemm-collectives_2d | `06-summa` |
| conjugate-gradient, both benchmark-libs | `07-cg` |

I checked the gemv-07 README: it multicasts x SOUTH and down its own RAMP, so Program 05 is the right match.

**X4 · Undefined terms with no glossary links.** The Teaches column and the Notes use these terms without defining them: SpMV, pencil decomposition, SUMMA, sentinel, range filter, color swap, queue flush, microthread, TSC, `time_ref`, preconditioner, residual, SdkLayout. The page has zero links to Appendix A, but every one of these terms has an entry there (for example `g-spmv`, `g-pencil-decomposition`, `g-summa`, `g-sentinel`, `g-filter-range-counter`, `g-color-swap`, `g-queue-flush`, `g-microthread`, `g-timestamp-counter-tsc`, `g-preconditioner`, `g-residual`, `g-sdklayout`). **Fix:** have `render()` link the first occurrence of each term to `appendix-a-glossary.html#g-…`, or add a "Terms used" line under the legend.

**X5 · Notes, "Timing idiom".** The note says "its 1-cycle-per-hop correction" but not the caveat that Appendix C gives: WSE-3 measures 2 cycles per hop, so the alignment can be off by up to about w + h cycles. **Fix:** add "(1 cycle per hop is the SDK's assumption; Appendix C measures 2 on WSE-3)".

## Connecting gaps

**G1 · med · Cumulative tutorial series → the ladder's chapter order.** Many tutorials build on the previous one. The gemv READMEs open with "Continuing from the previous example". gemv-09 is "an alternative version of the previous example", which is gemv-08, the multi-PE routes version. topic-13 modifies topic-12, and sdklayout-04 reuses sdklayout-03's `add2vec` region. The ladder spreads the gemv series over five rungs in this order:

| Rung | gemv examples |
|---|---|
| Ch 6 | gemv-02 |
| Ch 7 | gemv-03, gemv-09 |
| Ch 10 | gemv-00, gemv-01, gemv-04 |
| Ch 11 | gemv-05 |
| Ch 12 | gemv-06, gemv-07, gemv-08 |

So a learner who follows the ladder opens gemv-02 before gemv-01, and gemv-09 before the routes it modifies. The index never says the series exist.

**Bridge:** add a "Series" line to the Notes section: gemv-00→09, pipeline-01→03, sdklayout-01→05, topic-12→13 are cumulative. Each step diffs one or two files against the previous one, which makes them good to read as diffs. In the ladder, mark gemv-02/03/09 "read the diff against the previous gemv now; run after gemv-01 (Ch 10)". Effort S.

**G2 · med · Concept chapters (3–7) → runnable CSL (Ch 10).**
- The Ch 4–7 rungs send the learner to run CSL programs before Ch 10 has taught layout.csl, `@set_rectangle`, comptime params or the cslc flags. Ch 3 is the exception: it walks through running single-tile-matvec itself.
- Two items sit before their own prerequisite. topic-07 is on the Ch 4 rung, but it activates *control tasks*, a Ch 5 idea (its own row cites Ch 5 #sentinels). topic-04 is on the Ch 3 rung, but it needs a data task with two arguments (Ch 5 #activates) and index offsets (Ch 6).

**Bridge:**
- Tag each ladder item "read" or "run", with a one-line rule in the hint: before Ch 10, read the README and the pe_program; run once you have done gemv-01.
- Move topic-07 to the Ch 5 rung and topic-04 to the Ch 6 rung. A per-row "earliest chapter" field (the maximum prerequisite) would make this checkable.

Effort S.

**G3 · med · Chapters → this index (no inbound links).** The lede says "Use it to pick your next example after each chapter", but only Ch 10 (lines 308–309) and App C (line 139) link to the page. Chapters 3–7, the labs 11–15 and Ch 18 · Where to go next have no link. Ch 18's #next even lists six benchmarks, but does not link here. The ladder cannot be deep-linked to a rung either. **Bridge:** read `location.hash` (for example `#ladder-ch6`) to preselect a rung. Then add one "Next in the SDK → Appendix D" line to the end of each chapter that has a rung, plus Ch 18 #next. That last part is outside this page and needs a fixer for those chapters. Effort M.

**G4 · low · The import-fix callout → how the course itself solved it.** `programs/07-cg` vendors both libraries in `lib/` and imports `"lib/stencil_3d_7pts/layout.csl"` (layout.csl:23,31; commands.sh: "Self-contained: lib/ holds the two SDK benchmark libraries"). That is a third fix and the one the course's own Lab 5 uses, but the callout does not mention it. **Bridge:** add a third bullet: "or vendor the libraries as Lab 5 does: copy `benchmark-libs/*` into `lib/` inside the example and change the two import paths". Link to `15-lab-cg.html#modules`. Effort S.

**G5 · low · `device_run.py` note → Ch 15's actual explanation.** Ch 15 now says outright that the host-driven loop "is the SDK's run.py with kernel.csl" and the device-driven one "the SDK's device_run.py with kernel_cg.csl". That text is in the #code section under the h3 "Two loops, one program" (15-lab-cg.html:473–477, no id). The note links to #profile instead, which holds only the cost comparison. **Bridge:** link to the "Two loops" text. Add an id there; if one cannot be added, link to `#code` and keep #profile for the cost. Add the same link to the conjugate-gradient row. Effort S.

**G6 · low · WSE-2-only rows → what porting would take.** The method paragraph says a missing script means "not necessarily that the code cannot be ported". The course already explains the blockers for three of the four WSE-2-only examples:
- 25-pt-stencil binds 18 local tasks, more than WSE-3's 13 safe IDs (Ch 5 #budget, "could not be ported without sharing tasks").
- topic-14 needs color swap, which CSL lacks on WSE-3 (Ch 4 router table).
- The queue rules are in Ch 5 #portability.

**Bridge:** add one clause to each WSE-2-only note, with a link to the chapter that names its blocker. Effort S.

## Checked and fine
- Inventory: 34 tutorials, 21 benchmarks, 2 benchmark-libs, 2 csl-libs kernels (`fft`, `tally` in the SIF). That gives 59 items, and the computed stats are right: 48/55, 4 + 2, 1 with no script, 3 not covered.
- Chip badges match the shipped scripts for all 55 examples. WSE-2 only: topic-14, 25-pt-stencil, histogram-torus, spmv-hypersparse. WSE-3 only: topic-15, fft-3d. gemv-00 has no script.
- All 120-odd "Where" links resolve to existing ids, and every label matches or shortens the real heading.
- The Teaches column agrees with each README in all 59 rows that have one. I spot-checked these against source:
  - topic-02 imports `<random>`, `<time>`, `<math>`;
  - row-col-broadcast uses `memcpy_h2d_rowbcast`/`colbcast`;
  - Cholesky works on the lower triangle;
  - histogram-torus uses rings and a tally row;
  - mandelbrot runs on 4 × 4 PEs with left/middle roles;
  - PCG uses Jacobi;
  - gemv-07 multicasts x.
- Callout mount facts: `sdk_debug_shell` binds `CSL_IMPORT_PATH` entries, `$TMPDIR`, `$TMPDIR`→`/tmp` and `$PWD`; `env.sh` sets `TMPDIR=/home/user/cerebras-sdk/tmp`. The measured results come from build-appendix-cd and r2-appD-fixlog.
- Timing-idiom note: 25-pt-stencil (`task.csl`) and single-tile-matvec use `<time>` with no sync; game-of-life uses no TSC.
- "Measured in Ch 10" for sdklayout-02 is real: Ch 10 reports fabric 2 × 1 and cycle_count 81.
- Lab titles in the ladder match course.js CHAPTERS (Ch 11 is Lab 1 … Ch 15 is Lab 5).
