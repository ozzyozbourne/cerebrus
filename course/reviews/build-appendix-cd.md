# Build: Appendix C (Measuring and observing) and Appendix D (SDK example index)

## Built
- `course/appendix-c-measuring.html` (new). Sections: three instruments compared; a decision-chart widget (7 questions to 6 methods, clickable chips or SVG boxes, recipe readout); 1 whole-run `cycle_count` with a five-run noise widget; 2 TSC via `<time>` (device and host snippets, what `enable_tsc()` does from `csl-libs/time/internal.csl`, the same-PE rule, round trip, SDK sync + `time_ref` method); 3 instruction trace with a clickable trace-line widget and `trace_tasks.py`; a measured worked example on both chips with an annotated trace excerpt; other tools (simprint, debug, exported arrays, cs_readelf, csdb); profiling on Tenstorrent and NVIDIA; 10 pitfalls; a 3-question quiz.
- `course/appendix-d-sdk-index.html` (new). 59 items: 34 tutorials, 21 benchmarks, 2 benchmark-libs and 2 csl-libs kernels. A filterable table widget (topic, chapter, chip, kind, free text; phone layout stacks rows), a per-chapter ladder widget with "Show in table", a callout with the benchmark-libs import fix, and notes.
- `course/10-csl-toolchain.html`, library map: replaced the bare `kernels/fft` in the "also" row with rows for `kernels/fft`, `kernels/tally` and `benchmark-libs/{allreduce,stencil_3d_7pts}`; linked Appendix D; added one paragraph on the relative-import failure and its fix. No other chapters touched. course.js and course.css untouched.

## Measured this session (SDK 2.10.1 simulator, course `01-saxpy/timed` copied to scratch, 1 PE, N = 256 f32)
| chip | PAD | TSC | cycle_count |
|---|---|---|---|
| WSE-3 | 0 | 527 | 22,126 |
| WSE-3 | 1 | 271 (×5 runs) | 22,844; 21,773; 21,755; 21,631; 29,368 (traced) |
| WSE-2 | 0 | 526 | 20,405 |
| WSE-2 | 1 | 270 (×2) | 19,720; 20,421 (traced) |

- Trace: FMACS Seq 0→255 at @3630→@3885 (WSE-3) and @4156→@4411 (WSE-2), so 1 element/cycle. The TSC reads appear in the trace: WSE-3 counter at 0x7b30–0x7b32 (control 0x7b34), reads 5 then 0x114 = 276, so 271; WSE-2 at 0x318–0x31a (control 0x31e), reads 4 then 274, so 270. The trace matches the TSC to the cycle.
- The trace is 318,240 lines / 20.7 MB (WSE-3) and 230,747 / 17.1 MB (WSE-2).
- The RPC runs inside memcpy task **T01 on WSE-3 but T22 on WSE-2**. Ch 11's task table lists only the WSE-3 IDs; consider adding a note there.
- Padding made `cycle_count` go up in one pair (22,126 → 22,844) while the kernel got 256 cycles faster. Used as the noise example.
- csdb: the interactive shell `csdb <workdir>` with commands on stdin works. `context select out`, `image info` ("8 x 3") and `image lookup --name ts` (PE (4,1), 0x4, size 12) were verified. `memory read` fails: "Invalid cgz coredump: no cgz files found" (needs a core file or a device). Separate CLI invocations do not persist context. Halted-sim debugging stays Unverified.
- Import fix: the CG benchmark fails **even in place** in the extras tree (`Unable to open ./src/../../benchmark-libs/...`), because the wrapper container mounts only the cwd. `cslc --import-path` alone does NOT fix it, and neither does a sibling copy outside $TMPDIR. A sibling `benchmark-libs/` plus `CSL_IMPORT_PATH=$(realpath ../benchmark-libs)` (which the wrapper bind-mounts) compiles, and the run printed SUCCESS with `|xf_ref - xf_wse| = 3.05e-05` (WSE-3, 5×5, 2 iterations). The library's own comment says "--import-path"; the page states the measured truth. **This deviates from the brief's "(--import-path)" wording on purpose.**

## Verified from SDK files
- Chip support comes from the shipped scripts. Every script's `--arch` matches its name. WSE-2 only: topic-14, 25-pt-stencil, histogram-torus, spmv-hypersparse. WSE-3 only: **topic-15, fft-3d** (the coverage report missed both). **gemv-00 has no script at all**: the coverage report called it WSE-2 only, but it is a syntax fragment with no script for either chip.
- `<time>` internals: `enable_tsc()` sets control to 7 and resets the counter (hardware starts it at a random value).
- SDK cross-PE timing: allreduce sync, `time_ref`, and a propagation correction `(width+height-2)-(px+py)` (1 cycle/hop). Against CCN 20 (2.0 cycles/hop on WSE-3) the correction is off by up to ~w+h cycles. That is Derived.
- The kernels/tally and kernels/fft roles were read from the csl-libs sources.

## Sources for "other machines"
docs.tenstorrent.com and docs.nvidia.com do not resolve from this session (not in the allowed network domains). The facts come from WebSearch extracts of the tt-metalium Device Program Profiler and Tracy pages, the Nsight Systems User Guide and the Nsight Compute Profiling Guide. They are tagged Vendor docs, and the page says so and asks readers to check flags against their installed version.

## Validation
Playwright at 1100 and 390 px, light and dark, plus ◐ toggling, on both appendices and ch10. Zero page or console errors, zero horizontal overflow. Every widget control was driven: all flow chips and boxes, the noise checkbox, every trace field, every ladder chip plus "Show in table", each filter (filtered counts checked: WSE-3-only 3, WSE-2-only 5, no script 1, not covered 4, ch14 3), search, and reset. Widget screenshots were inspected. The phone table needed a stacked-card layout (fixed).

## Open issues
- Links to `14-lab-gemm.html` and `15-lab-cg.html` (and any section names for Ch 14/15) point at chapters not yet built. They are chapter-level links only, so check them when those labs land, especially the claim "Ch 15 compares host loop vs device_run.py".
- `index.html` still says "A 15-chapter visual course" (not edited, out of scope).
- Disk: `/home/user/cerebras-sdk/tmp/ch14` held ~26 GB (another task) and filled the disk mid-run. My scratch (`tmp/appcd`, `appcd-lab`) is deleted. No SDK extras files were modified (only `-o` into scratch).
- The `[ x ]` marker and `Pipe` field in trace lines are undocumented; the page says so.
