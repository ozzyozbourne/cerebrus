# Fix log, round 2: Chapter 14 (Lab 4: SUMMA GEMM)

Files edited: `course/src/14-lab-gemm.html` (then `python3 course/tools/build.py`), `course/programs/06-summa/layout.csl` (comment only: colors 20–23 → Chapter 10). The program logic is unchanged, so `expected_output.txt` was kept. Defaults re-run from a scratch copy: WSE-3 PASS (14,424 TSC, 36,968 cycles; within noise of the shipped 14,422 / 36,959), WSE-2 PASS (13,514, 33,655). `18-comparison.html` was not touched: its GEMM sentence uses the P = 4, T = 32 numbers, which did not change.

## New measurements (SDK 2.10.1 simulator, traces off, P = 2, TSC far-corner PE, per step; all steps and PEs equal)
| chip | kernel | T | broadcast | compute | fit | 
|---|---|---|---|---|---|
| WSE-3 | 0 | 44 | 4,367 | 242,396 | 254,932 (−5%) |
| WSE-3 | 0 | 45 | 4,545 | 189,224 | 271,350 (−30%, confirms depth review) |
| WSE-3 | 1 | 41 | 3,857 | 128,438 | 132,315 (−3%) |
| WSE-2 | 0 | 40 | 3,633 | 182,854 | 179,200 (+2%) |
| WSE-2 | 0 | 44 | 4,306 | 325,914 | 233,249 (+40%, unexplained) |
| WSE-2 | 0 | 46 | 4,666 | 315,978 | 263,908 (+20%) |
| WSE-2 | 1 | 40 | 3,634 | 132,418 | on fit |
| WSE-2 | 1 | 41 | 3,796 | 112,028 | −21% |
| WSE-2 | 1 | 42 | 3,962 | 152,872 | on fit |
Also used from the depth review: WSE-2 k0 T=45 276,575; WSE-2 k1 T=39 97,004.
Link tests (no-per-step-stamps variant, 12 B of stamps): WSE-2 kernel 0 T = 46 and kernel 1 T = 41 link at **P = 743**; at P = 4 kernel 0 T = 47 also links without the stamps; kernel 1 T = 43 still fails. `cs_readelf --syms` on the T = 16 build: A_tile 0x1708, B_tile 0x1b08, C_tile 0x1f08, A_buf 0x2308, B_buf 0x2708 (declaration order, all ≡ 8 mod 16 B), which explains the exercise-4 half-fix (A_buf is declared after C and moves with it).

## Findings
Accuracy
- A1 fixed: WSE-2 kernel 1 links at 42, fails at 43; mystery sentence removed; `LIM.wse2["1"] = [42336, 44376]`.
- A2 fixed: "Scaling up" now states the per-step stamps are dropped (13,386 B at P = 743; T=46 link at P=743 verified), uses WSE-2 tiles 46 (k0) and 42 (k1), plus the fastest measured tiles 40 and 41, all with measured P = 2 step costs. Calculator compares tiles + stamps with limits (+84 B measured at P = 4) and has a "stamps: per step / start and end only" selector.
- A3/P7: "about two-thirds (29 of 45 cycles)".
- A4/P8: kernel-1 fit called approximate; ablation (2.1 at T=16) matches the T=16 measurement (2.18), fit lower because cost falls with T; Q7 now mentions both @fmuls/@fadds and kernel 0's cheaper WSE-2 baseline.
- A5: chart hint names the least-squares fits and the 6% offset at T=8.
- A6/P6: Ch 3 (and Ch 11) for 44 KB; GEMV link → `12-lab-neighbours.html#composing`; layout comment → Ch 10; design section lists Chapters 3, 4, 5, 7, 10 with links.
- A7: unified chain/tree formula (chain 9P + M, tree log₂P(15+M) + 2(P−1), same as exercise 6); crossover ≈ 5–6 for one word, ≈ 27 for M = 32 (the old "35" used a different formula).
- A8: end PEs only send to their CE.
- A9/P2: Mt = 17 fastest (3.08 vs 3.33 vs 3.80), full command given.
- A10: design step 9 reworded (3–5.5× off; collision = 1 cycle/MAC, start-up most of the rest).
- A11: program dir cleaned (out/, run.log, sim.log, sim_stats.json, simconfig.json removed).

Depth
- D1: new findings bullet with all measured large/odd tiles; RUNS2 rows in the table, squares in the chart, shaded "extrapolated" band beyond T=32, readout warning, calculator uses measured values when available and warns otherwise. Corrected wafer numbers: k0 0.37–0.42 PFLOP/s (30–34%), k1 0.57–0.72 PFLOP/s (47–60%).
- D2: new section "What this program leaves on the table": double-buffered SUMMA (derived −14% at T=8, −2% at T=32, < 3% on wafer; memory 28T² → T≈38, kernel 1 35–36; third join condition; caveat that the library's FSM task cannot run during a long compute task, so real overlap needs split compute or own async moves), Cannon (wrap-around on a mesh, skew), fabin_dsd. New exercise 7 (design + build; answer Derived, not measured).
- D3: host I/O 11–14 GB: ≥ 74–93 ms at 150 GB/s, 0.8–1.0 s via SDK host path; resident SUMMA vs weight streaming (links Ch 8 #weight-streaming, Ch 9). Calculator prints I/O time.
- D4: kernel-0 overhead levers listed (unmeasured); exercise 8 (open); kernel-1 alignment sensitivity noted.
- D5: strong-scaling bullet (N = 256: 7.5× on 16× PEs, 47%).
- D6: 16-bit roofline sentence (13–16% of 16-bit capability).
- D7: shared receive-path hypothesis tagged Unverified, with the experiment.
- D8: consolidated caveats paragraph under the table.

Pedagogy
- P1: callout keeps mechanism + the multiple-of-4 data; Mt sweep moved into exercise 5's answer; fix story moved into exercise 4's answer (body says only what the test predicts and how to see addresses).
- P3: exercise 4 answer lists all five edits (declarations, exports, start_step + compute pointer, DSD templates, run.py), taken from the accuracy reviewer's working variant (13,739 measured).
- P4: two new quiz items (ROW_MAJOR wire order / column-major; 4 colors for any P, never task 29).
- P5: chain/tree callout moved to an aside after "Scaling up"; one sentence left in the library section.
- P9: FSM, DSRs (link Ch 6 #dsrs), control wavelet/CE-ignore (link Ch 4), TIP (teardown-in-progress, from library comment) defined.
- P10: quiz 2 says one color per axis for broadcast.
- P11: index-order warning callout.
- P12: `cs_readelf --syms` addresses in the callout and exercise 4 hints.
- P13: exercise 1 wording ties to the partial-overlap finding.

Visuals
- V1: see A2. V2: bar scales to max(48 KB, total), hatched over-48 KB zone, "x KB over" label, marker labels anchored to stay inside, segment labels drawn last with halo, free-space label. V3: per-MAC axis floor 0.03 with ticks to 0.05. V4: legend moved below C; C blocks fill progressively; no-op removed; selected blocks outlined. V5: per-hop arrows with arrowheads from the root outward on rows and columns. V6: done fill uses `--green` at 0.35 (visible in dark); labels shown down to G > 40. V7: out-of-range inputs reported in the readout and written back on change; dead "(too big)" removed. V8: WSE-3/WSE-2 labels; legend shows three-colour dots, hollow circle and squares; mouseleave/blur restores; points are focusable and clickable. V9: stepper readout adds the measured run when (P, T) was measured. V10: at ≤ 680 px the stepper stacks the matrices under the grid (360-wide viewBox, min-width overridden); budget bar labels free space.
- M1: added the broadcast sequence diagram (route rewrite, data + RAMP copies, TEARDOWN wavelet, task 29 → lock, FSM unblock, lock → callback, back-pressure panel).
- M2 (join diagram), M3 (bank-clash picture): not done (low priority); the join is drawn in Ch 5 and the clash is now explained with real addresses.

Validation: Playwright 1100/390, light/dark, ◐ toggle, every control (stepper P/T/play/next/reset/PE click, chart chip/y/slider/hover, budget all inputs incl. out-of-range, stamps, kernel, chip, clock): 0 page/console errors, 0 horizontal overflow; screenshots inspected.

## Open issues
- Why WSE-2 kernel 0 at T = 44 runs at ~3 cycles per element (worse than a full clash) is unexplained.
- Double buffering and the kernel-0 overhead levers are derived/unmeasured (exercises 7 and 8 have no measured answers).
- The extrapolation assumes per-step cost is flat to P = 743 (measured P ≤ 8) and code size independent of P; only the k0 T = 46 and k1 T = 41 links at P = 743 were verified (k1 T = 42 at P = 743 not linked).
