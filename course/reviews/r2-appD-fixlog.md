# Fix log: Appendix D (SDK example index), round 2

Inputs: r2-appD-accuracy.md (A1–A3, R1–R7) and r2-appD-visuals.md (V1–V4, P1–P7). Every finding is fixed. One is fixed
differently from the reviewer's suggestion (R4/P1 mapping policy, see below). Note: the coordinator's WIP commits
(714ac59, 3f27cfd) already picked up most of this work part-way through. Only the last ladder-hint wording is uncommitted.

## Files touched
- `course/appendix-d-sdk-index.html`: rewritten (data, widgets, callout, notes).
- `course/10-csl-toolchain.html`:
  - library-map rows for kernels/fft and benchmark-libs;
  - the import paragraph;
  - `id="ordinary"` on h3 "Ordinary parts".
- Harmless ids added so that links reach sections:
  - `course/12-lab-neighbours.html` and `src/12-lab-neighbours.html`: `id="roles"`;
  - `course/13-lab-stencil.html` and `src/13-lab-stencil.html`: `id="sdk-stencils"`;
  - `course/18-comparison.html`: `id="choosing"` and `id="next"`.
- Ch 12 and 13 were changed in src and generated output identically. I checked that `build.py`, run on a scratch copy, reproduces the
  edited generated files byte for byte. I did not run build.py in place, because src/15 was mid-edit by another fixer.

## Verification of the container mount (A2)
- `sdk_debug_shell` binds `CSL_IMPORT_PATH` entries, `$TMPDIR`, `$TMPDIR` over `/tmp`, `$PWD` and `$IMPORT_PATH`.
- Measured this session, WSE-3, with `CSL_IMPORT_PATH` unset:
  - `7pt-stencil-spmv` + `benchmark-libs` copied as siblings under `$TMPDIR` (`tmp/fix2-appD`): the full `commands_wse3.sh` ran to
    `SUCCESS!` (`|y_ref - y_wes| = 0.0`).
  - The same pair copied outside `$TMPDIR` (`/home/user/cerebras-sdk/fix2-appD-outside`): `Unable to open ./src/../../benchmark-libs/...`.
  - The outside copy with `CSL_IMPORT_PATH=$(realpath ../benchmark-libs)` set: "Compilation successful".
- Both scratch dirs are deleted.

## Findings
| ID | Fix |
|---|---|
| A1 | The callout, objectives and Ch 10 paragraph now say "five benchmarks (7pt-stencil-spmv + the four CG-family solvers)". Ch 10's benchmark-libs row lists all five. 7pt-stencil-spmv's row has the import-fix note. The Ch 13 ladder entry says "needs the import fix: copy benchmark-libs next to it". The Ch 15 rungs say "copy benchmark-libs next to it" / "same import fix". |
| A2 | The callout and Ch 10 say the container sees only cwd, `$TMPDIR` and `CSL_IMPORT_PATH` entries, and that `$TMPDIR` is mounted over `/tmp`. Two cases are given: "both copies under `$TMPDIR`: nothing else to do" (Measured) and "anywhere else: export CSL_IMPORT_PATH" (the recipe is kept). |
| A3 | The timing note lists the benchmarks by name and mechanism: 7pt + CG family use benchmark-libs/allreduce; bandwidth-test and row-col-broadcast use their own `sync/`; spmv-hypersparse uses its own allreduce + `f_sync`. 25-pt-stencil and single-tile-matvec use `<time>` alone, and game-of-life uses no TSC. 850 MHz is attributed to the run.py scripts. |
| R1/P5 | Every "Where" entry is now a link to a section anchor (`file#id`), with the label copied from the real heading (or shortened from it). All anchors were checked by script to exist. Ch 11's aside is a callout, not a heading, so it links to `#wavelet-tasks`. Ch 15 "Host loop or device loop" has no id and src/15 is being edited, so it links to the parent `#profile`. |
| R2/P1 | bicgstab, PCG and power-method now point to Ch 18 · Choosing, where they are named (status Named). bicgstab also points to Ch 2 · Surviving defects (the CS-1 result). Each keeps a "concept" link to Ch 15 · Composing modules, which does not count for the filter. Cholesky is now Named (Ch 18). "Not covered" is defined as "not mentioned". |
| R3 | topic-13-simprint is now Explained, with a note that no course program uses `<simprint>`. |
| R4 | Every chapter list was rebuilt by a script that greps each chapter's text (outside scripts) for the full name and short name (e.g. `topic-04`) and reports the enclosing section. Added: gemv-07/08 Ch 10; topic-11 Ch 4 and 10; topic-16 Ch 4 and 10; topic-04 Ch 5 and 11; topic-09 Ch 5 and 7; spmv-hypersparse Ch 5; bandwidth-test Ch 1, 11, 12; fft-3d and histogram-torus Ch 10; 25-pt-stencil Ch 4, 5, 6, 18; and others. Removed: single-tile-matvec Ch 8; fft-3d Ch 6; residual Ch 12; 7pt-stencil-spmv Ch 15; game-of-life Ch 13 (now a "concept" link); sdklayout-05 Ch 14. **Different from the suggestion:** the filter counts chapters that *name the example or explain its central idea*. So gemv-03 → Ch 7 (memcpy), gemv-06/07 → Ch 4 (routes) and gemv-checkerboard → Ch 12 (the two-colour checkerboard) stay. The page states this policy. |
| R5 | The quote is exact ("I/O pressure is high, not good for performance. device_run.py removes this IO pressure"). Text now reads "Chapter 15 builds the same two loops in its own program", with a link. |
| R6 | The four libraries get a "library" chip badge (dashed, neutral) with arch `lib` and a Chip filter option "library (no own script)". The kernels/fft and tally notes say each library has both-chip code paths and that only its one consumer's script is chip-specific. |
| R7 | Ch 10 kernels/fft row: layout module (`width`, `memcpy`) `FFT_kernel(width, n, T)`; PE module params `colors`, `ut_ids`, `iq_ids`, `oq_ids`, `local_task_ids`; `csfftExec*` calls (read from fft3d_layout.csl / fft3d.csl in the SIF). |
| V1 | Names break after `-`, `_` and `/` (`<wbr>` + `overflow-wrap:anywhere`). The Coverage column is `width:1%; nowrap`. The table is 792/792 px at 1100 (no inner scroll). |
| P2 | Stats are computed in JS from the same rows the filters use (static fallbacks are the same values): 59 = 55 examples + 4 libraries; 48/55 both; 4 + 2; 3 not covered. Chip filter: both 48, WSE-2 only 4, WSE-3 only 2, no script 1, library 4. "not covered" gives 3. residual no longer carries chapter 12. |
| V2 | Phone cards label each field with `td[data-l]::before` (Teaches, Chips, Where, Coverage). |
| V3 | The legend moved above the filters. |
| P3 | "Show all in table" now shows a removable pill, "Ladder: after Ch N ✕". Changing any select or the search clears the ladder selection. |
| P4 | Ladder names are links that scroll to and highlight their table row, clearing filters if the row is hidden. Each row shows its SDK path (`tutorials/…/`, `benchmarks/…/`, `SDK image: csl-libs/…`), and the method paragraph gives the absolute examples path. The hint explains the missing rungs (Ch 1, 2, 8, 9, 16–18 → "Beyond"). |
| V4 | Search spans the full filter width at desktop (4-column grid). On phones the grid has 2 columns. |
| P6 | Query and haystack are normalised (colour/behaviour/neighbour → US spellings, -ise → -ize for common stems). "colour" = "color" = 8 rows. |
| P7 | Added "Coverage at a glance": a topics × chapters heat map (cell = count, colour = best status, last column = not covered). Clicking a cell filters the index; every cell's count equals the filtered count (66 cells checked). |
| Also | sdklayout-05's comparison now points to Ch 12's GEMV (concept link), not Ch 14. |

## Validation
- Playwright at 1100 and 390 px, in light and dark, plus the ◐ toggle in each. Zero page/console errors and zero horizontal overflow.
  The table fits at 1100.
- Every control was driven:
  - all 7 + 1 chip options, every chapter and topic option, all 3 kinds, 8 search terms (including the empty result) and Reset;
  - all 12 ladder chips with "Show all in table" (2/4/3/5/4/8/4/8/3/3/4/5);
  - the pill, filter-clears-ladder, and a ladder link to a row hidden by a filter (it scrolls and highlights);
  - all 66 heat-map cells.
- Ch 10 renders at 1100/390 with no errors or overflow. Screenshots were inspected, then deleted with the scratch dir.

## Open issues (outside my files)
- `appendix-c-measuring.html` line ~135 ("Synchronise, then correct") repeats the generalisation "The SDK's solver and stencil
  benchmarks run an allreduce…". It should be scoped the same way as A3 (not 25-pt-stencil; bandwidth-test and row-col-broadcast use their own sync module).
- `15-lab-cg.html` "Host loop or device loop" (h3) has no id. If one is added to src/15, change the two links that point to `#profile`.
