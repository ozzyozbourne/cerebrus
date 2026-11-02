# Review round 2: Chapter 15 (Lab 5, conjugate gradient), accuracy

Scope: `src/15-lab-cg.html` / built `15-lab-cg.html`, `programs/07-cg` (layout.csl, pe_program.csl, run.py, lib/),
`expected_output.txt`, `run.log`, build-ch15-cg.md, CROSS_CHAPTER_NOTES 1–25, SDK 2.10.1 CG benchmark.
Checks I ran myself:
- A numpy copy of run.py's own CG recurrence (same b, A and f32 arithmetic) for several box sizes, plus the page's bound formula.
- One simulator run in a scratch copy, W=6 H=3 Z=5, 6 iterations, WSE-3, traces off. The scratch copy has been deleted.

Most numbers check out. These match the output or the arithmetic:
- 4,574 / 5,798 cycles, the +1,224 and 27% gap, allreduce 41% and SpMV 41%, the 1,898–2,126 allreduce spread (228 cycles).
- κ = 13.9 / 32.2 / 67.8 and the bounds 23 / 35 / 51.
- The 958 + 100W + 88H fit. On a grid it was not fitted to, W=6 H=3, it predicts 1,822 and the run measured 1,841 (+19). So the fit holds.
- 60% at 16×16, the ~180k-cycle extrapolation, 532 / 503 cycles per block saved, 10 cycles per cell for the dot.
- The 99.5% host-wait figure and the compile-error line numbers (wse3/pe.csl:741/753/629, allreduce/pe.csl:1097).
- The SDK's "21–30 reserved (memcpy)" comment and the allreduce algorithm (pos0 rx WEST, pos1 rx RAMP, farthest value first, teardown between stages).

## Findings

**A1 (high): "The scaling law of this solver" callout and quiz Q6 are wrong for a fixed column.**
- **Location:** the callout says "Grow the box in x and y with a fixed column, and the time per solve grows like the square of the side: the number of iterations grows like N". Quiz Q6 says "The condition number grows too, so the solve needs more iterations as well … grows roughly like the square of the side".
- **Problem:** with u = 0 on every face (run.py's A), λ_min = Σ_d 2(1 − cos(π/(n_d+1))). The z term stays fixed, so with Z fixed κ is bounded: it tends to 12/0.268 ≈ 43.8 for Z = 5. Iterations level off. They do not grow like N.
- **Evidence:** numpy runs of run.py's recurrence to 1e-5 (b from rng 15) at Z = 5:

  | W×H | iterations | κ |
  |---|---|---|
  | 5×5 | 15 | 13.9 |
  | 16×16 | 30 | 34.7 |
  | 32×32 | 35 | 40.9 |
  | 64×64 | 39 | 43.0 |
  | 128×128 | 39 | 43.6 |

  At 950×950×5 the bound is 41 (κ 43.8). The page's own cost widget gets this right, because `bound()` uses the real W, H, Z. So the widget contradicts the callout.
- **Fix:** split the two cases.
  - Cube growth (N×N PEs, N cells each): iterations grow like N, and the per-iteration allreduce also grows like N. That is about N² per solve, and the SpMV grows with Z too.
  - Fixed column: iterations level off at about 40 (Z = 5), so solve time grows like N, through the allreduce alone.

  Rewrite Q6's answer to match: doubling W and H at fixed Z raises κ only slightly (13.9 → 19.3 for 10×10×5), and by at most about 3×.

**A2 (med): "over 100 times its 7 multiply-adds per cell" (Scaling, column-length paragraph).**
- **Problem:** at ~1 f32 FMAC per cycle (note 16), 7 multiply-adds take ~7 cycles. 276 / 7 ≈ 40×, not >100×.
- **Fix:** say "about 40 times".

**A3 (med): "at Z = 100 it [local dot] costs more than the whole stencil with one block".**
- **Problem:** the Z table says local dot 1,115 versus stencil 1,957 at BLOCK = 100. The dot is cheaper.
- **Fix:** "more than half the stencil with one block", or compare it with the axpys (898) instead.

**A4 (med): "the eight `mark()` calls cost about 310–400 cycles" (profile list item 4).**
- **Problem:** pe_program.csl makes 11 `mark()` calls per iteration:

  | Phase | `mark()` calls |
  |---|---|
  | update_p | 1 |
  | spmv_Ap | 1 |
  | eta_dot | 2 |
  | update_x_r_rho | 3 |
  | phase_done × 4 | 4 |

  `record()`'s `now()` also stays in with PROFILE = 0.
- **Fix:** "the eleven `mark()` calls (about 30–35 cycles each)".

**A5 (med): The whole-wafer callout's "about 2,700 of other work" disagrees with the widget preset it points to.**
- **Location:** the callout, and the cost-widget preset "≈ whole wafer, Z = 100".
- **Problem:** 2,700 is the Z = 5 figure (4,574 − 1,898 = 2,676). At Z = 100 and BLOCK = 2 the other work is ~30,100 cycles.
- **Fix:** write "at Z = 5" in the callout, or quote both numbers. Either way, the allreduce still dominates at Z = 5 (180k vs 2.7k) and at Z = 100 (180k vs 30k).

**A6 (low): "instruction start-up ≈ 15 cycles each", attributed to Lab 3 (profile item 1).**
- **Problem:** Lab 3 (13-lab-stencil, "Where the 90 cycles go") measured ≈14.6 cycles per async transfer, but only ≈6 cycles of start-up per vector instruction inside a task. Chapter 6's isolated op is ~17 cycles.
- **Fix:** "one message ≈ 15 cycles, plus ≈ 6 cycles to start each vector instruction (17 for an isolated op, Chapter 6)".

**A7 (low): Line counts in "Composing modules".**
- **Problem:** "writes about 200 lines and imports about 2,700" does not match either count:
  - Own CSL is 315 lines (layout 74 + pe_program 241).
  - lib/ is 2,929 lines in total.
  - A single-chip build uses ~2,180 of those (allreduce 1,174, plus stencil dispatch, layout and one arch file: 1,005).
- **Fix:** "about 300 lines, importing about 2,200 (2,900 counting both chip variants)".

**A8 (low): "CG usually beats its bound because the right-hand side does not excite the worst eigenvectors equally".**
- **Problem:** the main reason is that the κ-only bound ignores how the eigenvalues are spread out: once the extreme eigenvalues are resolved, convergence speeds up (superlinear convergence). The caption already notes that the bound is on the A-norm error.
- **Fix:** "because the bound uses only κ; CG adapts to the actual eigenvalue distribution (and to which components b contains)".

**A9 (low): The cost widget's Z = 5 constants differ from the measured default.**
- **Problem:** the widget uses axpy 341 and a fixed control of 316, which come from the 6-iteration grid sweep. The default 5×5×5 run measured 352 / 295. At the default preset the widget therefore shows 4,586 cycles, while the stat, table and text show 4,574.
- **Fix:** use [352, 1866, 165] and 295 for Z = 5, or note in the hint that the constants come from 6-iteration runs.

**A10 (low): "all of it in the control bucket" (Host loop or device loop).**
- **Problem:** control rises by 1,262 (295 → 1,557) while axpy falls by 29 and allreduce by 3. The control increase is slightly larger than the 1,224 total.
- **Fix:** "essentially all of it (+1,262 in control, small changes elsewhere)".

**A11 (low): The resource-widget error texts give "pe.csl:753 / 741 / 629" for the stencil.**
- **Problem:** these lines are in `lib/stencil_3d_7pts/wse3/pe.csl`, not the stencil's dispatch `pe.csl` (111 lines).
- **Fix:** name `wse3/pe.csl`.

**A12 (low): WSE-2 host-loop figures differ slightly between places.**
- **Problem:** the widget uses 5,333 (control 1,439, which gives +1,147). The committed run.log shows 5,326 (control 1,433, which gives +1,140).
- **Fix:** none needed, since this is within note 17's noise. Optionally say "≈1,140–1,150".

## Provenance tags

- The tags are generally right.
  - Measured: only simulator/TSC values.
  - Derived: the fit, κ, the real-system bar and the extrapolation.
  - SDK: the 200 µs figure, BLOCK_SIZE:2 and the reserved colours.
- Add a Derived tag to "about 50 cycles per call per PE along a row and 44 along a column" (it is half the fit coefficients).
- "Chapter 12's review measured … about 700 cycles" is tagged Measured, but the learner cannot see that review. Point to the Chapter 12 section that states it, or say "measured during this course's review (note 24)".

## Summary
High 1 (A1), med 4 (A2–A5), low 7 (A6–A12). The measured numbers are sound and reproduce. On a grid outside the sweep (6×3) the fit predicts within 19 cycles. The main error is conceptual: with the column fixed, CG's iteration count levels off (κ ≤ ~44 for Z = 5), so the "square of the side" scaling law holds only for cubes.
