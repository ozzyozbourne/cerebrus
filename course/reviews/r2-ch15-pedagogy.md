# Review 2, Chapter 15 (Lab 5: conjugate gradient), pedagogy

Reviewed: `course/src/15-lab-cg.html` (built `15-lab-cg.html`), `programs/07-cg/{layout.csl,pe_program.csl,expected_output.txt}`, `reviews/build-ch15-cg.md`, CROSS_CHAPTER_NOTES, and the chapters it links to (5, 7, 12, 13, 14). Overall: well ordered (problem, CG, mapping, composition, allreduce, code, profile, scaling). Prerequisites are mostly introduced earlier: teardown, switches, `reset_routes`, microthreads, DSRs, `fabout_dsd`, multicast and RPC are all used in Ch 4–14. The serious problems are a scaling claim that the page's own widget contradicts, and exercises that do not test what they say they test.

## Findings

**P1 (high). The scaling law is wrong when the column is fixed, and the cost widget contradicts it.** Location: callout "The scaling law of this solver"; quiz Q6; first paragraph of "Iterations grow too".
- What is wrong: the callout says "Grow the box in x and y with a fixed column … the number of iterations grows like N". With u = 0 on the top and bottom faces, λ_min = Σ_i (2 − 2cos(π/(n_i+1))). As W and H grow, λ_min tends to 2 − 2cos(π/(Z+1)), which is fixed, so κ and the iteration count level off.
- Evidence: I ran the page's own `bound()` formula with Z = 5. It gives bounds of 23, 29, 34, 36, 39, 40 and 41 iterations for N = 5, 8, 12, 16, 32, 100 and 950 (κ levels off at about 44). For a cube (Z = N) the bound grows like N: 23, 35, 51, 66, 129, 393. The "Predict a solve" widget with W = H = 950 and Z = 5 shows about 41 iterations, which contradicts the callout beside it. The measured 5³/8³/12³ runs are cubes, so they do not test the fixed-column claim. Quiz Q6 ("double W and H, keeping Z … the condition number grows too") repeats the error.
- Fix: say that with a fixed column the iteration count levels off at about 40 for Z = 5, so the time per solve grows like N, driven by the allreduce alone. Iterations grow like N only when the box grows in all three dimensions (Z grows too, which also raises the stencil cost). Rewrite Q6's answer to match. A one-line note in the widget would help: "with Z fixed, the bound stops growing once W, H ≫ Z".

**P2 (high). Exercise 1 is circular.** Location: Exercises, item 1, "Read the profile".
- What is wrong: the learner is asked to predict the allreduce cost for 12 × 12 and 16 × 4 "from the fit". Both grids are among the seven points the fit was built from, and both appear in the grid table above. The "expected result" (3,214 and 2,910, fit equals measurement) only proves the learner can read the table.
- Fix: pick grids that were not used for the fit, e.g. 10 × 6 and 6 × 14 (fit: 2,486 and 2,790). Give the measured values with a tolerance, and add a second part: "predict the WSE-2 cost from 82 cycles per PE of W + H".

**P3 (med). A false comparison in the Z/BLOCK paragraph.** Location: "How it scales", Column length: "at Z = 100 it costs more than the whole stencil with one block".
- What is wrong: the page's own table gives local dot 1,115 cycles and stencil with BLOCK = 100 1,957 cycles, so the dot costs less. A careful learner who checks the table will stop trusting the paragraph.
- Fix: "at Z = 100 the local dot (1,115) costs more than half the whole one-block stencil (1,957), and more than the three axpys". Or point out that the two dot phases together cost 2 × 1,115.

**P4 (med). Exercise 3 is too big a jump, uses clashing notation and gives no expected result.** Location: Exercises, item 3.
- What is wrong:
  - The exercise says Chronopoulos–Gear computes "⟨r, r⟩ and ⟨w, r⟩", but on this page w = A p. In that variant w = A r, and the learner will compute the wrong product.
  - "From a test RPC" means adding an exported function, an `@export_name` in layout.csl, a buffer and changes to run.py. None of this is scaffolded. This is the only lab exercise of that size.
  - There is no expected number to check against.
- Fix: define the variant's w explicitly (w = A r, a new vector). List the four edits (pe function plus `@export_symbol`, layout `@export_name`, a `launch` call in run.py, reading the time back from `t_hist` or `prof`). Give a measured or estimated answer, e.g. "a 2-value call costs X vs 2 × 949". Otherwise move this exercise to a "going further" box.

**P5 (med). Exercise 4's answer misses part of its own question.** Location: Exercises, item 4, hint.
- What is wrong: the question asks "Could you use tasks 21–24?", but the answer covers only 21–23. Chapter 5 (lines 242–246) says 24 is `SYS_EN_MAIN`, which memcpy may need.
- Fix: add "and 24 is memcpy's SYS_EN_MAIN on WSE-3 (Chapter 5), so 21–24 is out on every count". Also state that colour 9 is safe because memcpy owns 20–23 and the program uses 0–8 (link the Chapter 7 table), so the learner checks the colour too and not only the tasks.

**P6 (med). Wrong cross-chapter pointers and numbers.**
- Location: "Where an iteration's cycles go", "(Chapter 12 explains why readings from different PEs are not comparable)". That explanation is in Chapter 13, Lab 3 (13-lab-stencil.html, line 374 and quiz line 530). Fix: point to Chapter 13 and link it.
- Location: "Four things stand out", item 1: "Lab 3 measured … one message ≈ 15 cycles, plus instruction start-up ≈ 15 cycles each". Chapter 13 says about 19 cycles of start-up for three instructions, "about 6 per vector instruction", and a 90-cycle floor per step. CROSS_CHAPTER_NOTES 16/23 give about 15–17 per op from Ch 6. Fix: quote Chapter 13's split (a 90-cycle floor per step, of which about 19 is start-up) or cite Chapter 6 for the per-op start-up, and drop "one message ≈ 15 cycles" unless a chapter shows it.
- Location: the `<collectives_2d>` paragraph: "Chapter 12's review measured its fixed overhead at about 700 cycles". Learners cannot see reviews. Chapter 12's page states the same 700 cycles (line 524). Fix: "Chapter 12 measured…" with a link to `#collectives`.

**P7 (med). Small count errors in the code walkthrough.**
- Location: before `pe_program.csl`: "The five CG phases are ordinary functions". The text then names four (`update_p`, `spmv_Ap`, `eta_dot`, `update_x_r_rho`). The program defines seven phase constants: three set-up phases (INIT, SPMV_AX, RESIDUAL) and four per iteration. Fix: "four phases per iteration (plus three set-up phases: init, A x0, residual)".
- Location: profile item 4: "the eight `mark()` calls". Counting `pe_program.csl` gives 7 explicit marks plus one in `phase_done()` for each of the 4 phases, so 11 per iteration. Fix: "eleven `mark()` calls (about 30–37 cycles each)".

**P8 (low). η and a few names in the numpy reference are never defined in the prose.** Location: figure "+ 7 coefficients, ρ, η"; the host-loop list (`f_eta`); the numpy block (`tol`, `x0`, `A`).
- Fix: after the numpy block, add "η = ⟨p, w⟩, the denominator of α; tol = EPS·|b|". A small table mapping numpy lines to the four device phases would help: `update_p`, `spmv_Ap`, `eta_dot` (with the α dot), and `update_x_r_rho` (x, r and the ρ dot). It would also make the five profile buckets easier to read.

**P9 (low). The quiz under-tests the lab's distinctive lessons.** Location: "Check yourself".
- What is wrong: no question covers the import-path trap (paths resolve relative to the top-level layout; the container mounts only the current directory) or BLOCK size. None asks for a number. Q5's "roughly 200 times slower" compares the host loop with 5 commands against the PROFILE = 0 device time. That is right, but the reasoning is not given.
- Fix: add "Why does `cslc` fail with `Unable to open ./wse3/pe.csl`?" and "At Z = 100, what does BLOCK = 10 save, and what does it cost?". In Q5 give the arithmetic: 5 × 200 µs ≈ 1 ms against 4,261 / 850 MHz ≈ 5 µs.

**P10 (low). "The time per solve grows like the square of the side" needs a regime caveat even for cubes.** Location: the same callout.
- What is wrong: at 16 × 16 the non-allreduce work is still 40% of an iteration. For a cube, the stencil and dot also grow with Z = N, so "square" holds only for the allreduce part.
- Fix: after the P1 rewrite, say "asymptotically, once the allreduce dominates".

## Counts
High 2 (P1, P2), med 5 (P3–P7), low 3 (P8–P10).
