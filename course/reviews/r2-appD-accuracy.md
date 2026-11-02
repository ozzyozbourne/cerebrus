# Review r2 · Appendix D (SDK example index) · accuracy + reference

Scope: `appendix-d-sdk-index.html` (59 rows, ladder, import callout, notes) and the new library-map rows plus import paragraph in `10-csl-toolchain.html` (lines 304–309). Checked against `extras/csl-extras-202604101435-6-d2f7d96e/examples`, `csl-libs/kernels` in the SIF, the `cslc`/`sdk_debug_shell` wrappers, and the headings of every linked chapter. Experiment: copied `7pt-stencil-spmv`, `conjugate-gradient` and `benchmark-libs` to `/home/user/cerebras-sdk/tmp/r2appD/` and ran the WSE-3 `cslc` lines, then deleted the copies.

## Verified correct
- Counts: 34 tutorials, 21 benchmarks, 2 benchmark-libs, 2 kernels = 59. 48 of 55 with both scripts, 4 WSE-2-only (topic-14, 25-pt-stencil, histogram-torus, spmv-hypersparse), 2 WSE-3-only (topic-15, fft-3d), and gemv-00 with no script (README: "not a complete program"). Every script's `--arch` matches its file name. Every chip badge in D[] matches.
- Quotes and facts: the topic-14 README quote, the fft3d defaults (`@get_ut_id(2), @get_ut_id(3)`, `@get_input_queue(2), (4)`), the tally quote "every PE must signal completion at least once", 850 MHz in run.py, the pipeline-03 "artificial halo" with west.csl and east.csl, mandelbrot 4×4 with left.csl and middle.csl, wide-multiplication 128-bit × 128-bit → 256-bit, residual row then column reduction, Cholesky "right-looking", topic-03's input queue on WSE-3 (`@get_input_queue(2)` under `@is_arch("wse3")`), `device_run.py` present in all four CG-family benchmarks, and `CSL_IMPORT_PATH` bind-mounting by the wrapper (`sdk_debug_shell` lines 38–58).
- Every section name in the "Where" column exists as a heading in its chapter. Two are paraphrases: "Roles are compile-time params" (heading: "Reading the code: roles are compile-time params") and "Ch 11 · Aside" (not a heading).

## Findings

**A1 · high · Import callout, 7pt-stencil-spmv row, Ch 13 ladder.** The page says that "the four solver benchmarks" need the import fix. A fifth benchmark, `7pt-stencil-spmv`, also needs it: `src/layout.csl:44,51` and `src/kernel.csl:21,31` import `"../../benchmark-libs/…"`. The row has no "Needs the benchmark-libs import fix" note. The Ch 13 ladder recommends it with no warning, so a learner who follows the ladder hits the error first here. Ch 10's row (line 306) already lists 7pt-stencil-spmv as an importer, so the two pages disagree. Fix: change the callout to "five benchmarks (the four solvers and 7pt-stencil-spmv)". Add the note to the row and "(with the import fix)" to the Ch 13 ladder entry.

**A2 · med · Callout "a container that sees only the current directory", and the Ch 10 paragraph (line 309).** This is incomplete. `sdk_debug_shell:58` binds `${TMPDIR}`, `/tmp`, `${PWD}`, `${IMPORT_PATH}` and every `CSL_IMPORT_PATH` entry. `env.sh` sets `TMPDIR=/home/user/cerebras-sdk/tmp`. Measured: sibling copies of `benchmark-libs` + `7pt-stencil-spmv` and of `benchmark-libs` + `conjugate-gradient` under `$TMPDIR` both compiled ("Compilation successful") with `CSL_IMPORT_PATH` unset. The same CG compile in place in extras failed with `failed to parse program requested here` at `layout.csl:55`. This agrees with build-appendix-cd ("sibling copy outside $TMPDIR" fails), but the page does not say it. Fix: "sees only the current directory, `$TMPDIR` and any `CSL_IMPORT_PATH` entries". Add that a sibling copy under `$TMPDIR` works with no extra step, and keep the `CSL_IMPORT_PATH` recipe for copies elsewhere (`~/sdk`).

**A3 · med · Notes, "Timing idiom".** The note says "Every solver and stencil benchmark times itself with the TSC plus an allreduce-based sync and a reference stamp". That is false for two of them. `25-pt-stencil` uses `<time>` with no sync or `time_ref` (grep: 0 files), and Ch 13's own table says "TSC in the kernel". `game-of-life` has no TSC at all. The idiom (sync + `time_ref`) appears in 7pt-stencil-spmv, the four CG-family solvers, bandwidth-test and row-col-broadcast. spmv-hypersparse uses its own `f_sync`. Fix: list those benchmarks by name instead of saying "every".

**R1 · med · "Where in the course" links (render(), line 210).** Every link goes to the top of the chapter (`FILES[c]`), although the cell names a section and nearly all sections have ids (for example 15 `#allreduce`, `#profile`, 10 `#stdlib`, 13 `#tsc`). The reference angle asks for links to the right section. A learner who lands on Ch 4 has to hunt for "Filters: one stream, many slices". Fix: add an anchor per entry, e.g. `[4, "#filters"]`, and add ids to the headings that lack them (Ch 11 has 5 of 14, Ch 13 has 5 of 13).

**R2 · med · Rows bicgstab, preconditioned-conjugate-gradient, power-method (status "Named", chapter 15).** Ch 15 never mentions any of them (grep: no match). All three are named in Ch 18 ("the SDK ships CG, preconditioned CG, BiCGStab, Cholesky, …, power-method benchmarks"). bicgstab also appears in Ch 2 and Ch 13 (the CS-1 BiCGSTAB result). Cholesky is marked "Not covered" but is named in Ch 18. Fix: point these rows at Ch 18, or keep Ch 15 as a "concept" link without the "Named" status. Then either mark Cholesky "Named" or define "Not covered" as "not explained".

**R3 · low-med · topic-13-simprint status "Labbed".** The legend defines Labbed as "a course program does it", but no file under `course/programs/` uses `<simprint>` (grep: empty). Ch 10 only explains it, in "When it hangs". Fix: change the status to "Explained".

**R4 · low · Chapter mapping misses and misfires (chapter filter).** Some rows cite chapters that never mention the example:
- gemv-06 and gemv-07 cite Ch 4, which does not name them.
- game-of-life cites Ch 13.
- gemv-checkerboard cites Ch 12.
- gemv-03 cites Ch 7.

Other chapters that name an example are missing from its row, so "Chapter N" filters under-report:
- gemv-07 and gemv-08 are in Ch 10.
- topic-11 and topic-16 are in Ch 4 and Ch 10.
- topic-04 is in Ch 5, 6 and 11.
- topic-09 is in Ch 5 and 7.
- spmv-hypersparse is in Ch 5.
- bandwidth-test is in Ch 1, 2, 11 and 12.
- fft-3d and histogram-torus are in Ch 10.
- 25-pt-stencil is in Ch 5 and 6.

Fix: add these chapters to `d[5]`, or state that the column lists only the main explanation.

**R5 · low · Notes, `device_run.py`.** The quote "to remove I/O pressure" is not verbatim. The source reads "device_run.py removes this IO pressure" (`conjugate-gradient/run.py:73`). Also, "Chapter 15 compares the two" is loose. Ch 15 ("Host loop or device loop") compares its own program's two loops and the SDK's host-driven and device-driven kernels, but never names `device_run.py`. Fix: quote exactly, and say "Chapter 15 builds the same two loops in its own program".

**R6 · low · Chip badges on csl-libs/kernels/fft (WSE-3) and kernels/tally (WSE-2).** Both libraries have both-chip code paths: `tally/pe.csl:46,49,90,105,209` and `fft/fft_internal/transpose.csl:89–111` branch on `@is_arch("wse3")`. The badge describes the consumer's script, not the library, and the "WSE-3 only" filter returns 3 rows, one of which is a library. Fix: badge them "no own script" (or "via fft-3d / histogram-torus") and keep the note.

**R7 · low · Ch 10 library map, kernels/fft row (line 304).** "Key calls: module params: colors, queues, microthreads, task IDs" mixes two modules. The layout module `fft3d_layout` takes `width` and `memcpy` and exposes `FFT_kernel(width, n, type)`. The queue and microthread params (`ut_ids`, `iq_ids`, `oq_ids`) belong to the PE module `fft3d.csl`. Fix: "layout: `FFT_kernel(width, n, T)`; PE params: queues, microthreads". The tally row (`get_params(i, j)`, params `colors`, `output_color`, `phase2_tally`) and the benchmark-libs row are correct.

## Ladder
The order is sensible, and every entry exists with the right chip badge. The only error is A1 (Ch 13 → 7pt-stencil-spmv with no import note). Optional: the Ch 15 rung could say "copy benchmark-libs next to it" instead of only "with the import fix".
