# r2 review: Ch 15 (Lab 5, CG), depth angle

Scope: `course/15-lab-cg.html` (src `src/15-lab-cg.html`), `programs/07-cg`, `build-ch15-cg.md`. One experiment: an f32 numpy CG with the same recurrence and seed as run.py (`/tmp/claude-0/-home-user-cerebrus/dad2686f-4919-59f3-a15a-5e1f2815e9e2/scratchpad/cg.py`). I did not run the simulator. arxiv.org could not be reached from this session, so I could not check the SC20 paper's own allreduce numbers.

## Findings

**D1 (high). "The scaling law of this solver" box, plus quiz Q6: with a fixed column, the iteration count does not grow with the side.**
The box says: "Grow the box in x and y with a fixed column, and the time per solve grows like the square of the side: the number of iterations grows like N." That is false. Write λ = Σ_d 2(1 ∓ cos(π/(n_d+1))). With Z fixed, the z term keeps λ_min ≥ 2(1 − cos(π/(Z+1))), which is 0.268 at Z = 5. So κ ≤ about 45 however large W and H get.
- The page's own cost-model widget computes the bound correctly: 23 at 5×5×5, 36 at 16×16×5, 40 at 100×100×5, 41 at 950×950×5. So the widget contradicts the text.
- My f32 CG to 1e-5 needs 15, 30, 35, 39 and 39 iterations for 5², 16², 32², 64² and 128² PEs with Z = 5.
- So at fixed Z the time per solve grows linearly in the side, and all of that growth comes from the allreduce. It grows like N² only when the box grows in all three directions (Z = N, as in the convergence figure).
- Quiz Q6 ("double W and H, keeping Z … the condition number grows too … square of the side") repeats the error. Its answer should be: the iterations rise a little and then level off near 40, so the solve grows about linearly.

Fix: rewrite the box with two cases. (a) Weak scaling with fixed Z: iterations level off, so time per solve is linear in the side. (b) The cube grows (W = H = Z = N): iterations ∝ N, allreduce ∝ N and stencil ∝ Z = N, so time per solve ∝ N². Also qualify the sentence near line 59, "A bigger grid needs more iterations", with "when all three sides grow". Fix Q6 to match.

**D2 (high). Scaling box, whole-wafer extrapolation: the page never says how far this library is from what the hardware can do.**
The 180,000 cycles per iteration come from this library's per-value serial protocol: about 50 cycles per PE per call. That number is not a property of the wafer. The course's own measurements give lower bounds:
- A streaming add-and-forward chain costs about 9.2 cycles per PE on WSE-3 (CROSS_CHAPTER_NOTES item 24).
- A pure router hop costs 2 cycles (item 20).

For a 950-PE row, one stage then costs:
- this library: about 47,500 cycles
- streaming chain: about 8,700 cycles
- hop-bound pipeline: about 1,900 cycles

That is a 5–25× spread, before any tree. The box lists "pipelined or tree-shaped reductions" as remedies but never puts a number on them. A reader is left thinking that CG on a wafer is allreduce-bound by about 65:1, when part of that ratio comes from the library.

Fix: add 2–3 sentences with the per-PE costs above (Derived, from items 20 and 24). Say that the 180k figure describes this library, not the fabric. Cite the SC20 BiCGStab result already used in Ch 18 (about 1/3 of peak on a 600×595 fabric) as evidence that well-built global reductions do not dominate at wafer scale. Mark it Unverified until someone checks that paper's allreduce latency.

**D3 (med). Missing caveat: f32 arithmetic limits CG at scale.**
All the bounds assume exact arithmetic. In my f32 runs:
- The recursive residual reaches 1e-5 for 24³ and 48³.
- The true residual |b − Ax|/|b| does not: it is 1.95e-5 at 24³ and 9.0e-5 at 48³.

At the whole-wafer preset (κ ≈ 12,000), the drift will be worse, and the dot products summed over about 10⁸ cells in f32 lose precision too. The page shows the true residual only for 5³, where the two agree.

Fix: add a short caveat in "Predict a solve". Make three points: the recursive and true residuals separate in f32 as κ grows, so check the true residual or recompute r = b − Ax now and then. The order of the allreduce sum changes the rounding. And the 1e-5 target may not be reachable at wafer-scale κ without residual replacement or higher-precision accumulation.

**D4 (med). "How it scales" › Column length: the memory price of BLOCK is overstated, and the trade-off is never quantified.**
The page says "The price is memory: BLOCK_SIZE sizes the library's temporary communication buffers." The buffers are four arrays of BLOCK f32 values (`lib/stencil_3d_7pts/wse3/pe.csl` lines 93–96), so they take 16·BLOCK bytes. That is 1.6 KB at BLOCK = 100, out of about 44 KB usable (item 13). That 1.6 KB buys a 4.9× speed-up of the iteration at Z = 100 (32,004 → 6,573 cycles).

The page never explains why the SDK still ships BLOCK = 2. One possible reason is that small blocks pipeline the sends with the @fmacs, though at Z = 5 that is moot. The page also never says what limits Z: about (44 KB − buffers) / 20 B ≈ 2,000 cells per PE, which is about 1.8 × 10⁹ unknowns on a whole wafer. That figure is a nice counterpoint to the intro's "with a billion you cannot even store it".

Fix: state the 16·BLOCK bytes cost and the maximum Z (Derived). Present BLOCK as a latency knob that is almost free in memory.

**D5 (med). "Where an iteration's cycles go": no utilisation figure.**
The page never puts the measurements against peak. One iteration costs about 23 flops per cell (SpMV 13, two dots 4, three axpys 6).
- Default run: 5 cells × 23 = 115 flops in 4,574 cycles. That is 0.025 flop/cycle/PE, about 1.3% of the 2 flop/cycle f32 fmac peak (item 16).
- Z = 100, BLOCK = 100: about 2,300 flops in 6,573 cycles, about 17%.

This is the clearest way to show that the lab's default sits deep in the latency-bound regime. It also lines up with the one hardware data point, SC20's BiCGStab at about 1/3 of peak, which used deep columns.

Fix: add a stat card or one paragraph with both utilisation numbers (Derived), and say that real stencil codes put thousands of cells on each PE.

**D6 (med). "Host loop or device loop": the 5 × 200 µs model assumes synchronous launches.**
The 99.5% waiting figure assumes every one of the five commands is a full round trip. With `nonblock=True` the host can queue the four phase launches and block only on the ρ copy. That leaves about one round trip per iteration, if the SDK's 200 µs figure is latency rather than throughput per command. The conclusion stands, since even one round trip is about 40× the iteration. The page should still name this as the obvious first fix and the real assumption behind the number.

Fix: one sentence plus a Derived range: about 200 µs to 1 ms per iteration, depending on how much of each command's overhead overlaps.

**D7 (med). Scaling box and exercise 3: the page is missing pipelined CG, and the WSE-2 queue sharing blocks it.**
The page offers Chronopoulos–Gear, which merges the two dot products into one allreduce. It leaves out the variant that matters most when the allreduce costs as much as everything else: pipelined CG (Ghysels–Vanroose), which overlaps the reduction with the SpMV. On this program that overlap is impossible as written. The WSE-2 build shares output queue 3 between the stencil and the allreduce, which the page itself says "works here only because the program never runs [them] at the same time." That connection would teach the ledger lesson far better than a generic warning.

Fix: add a sentence to the scaling box and a hint in exercise 3: overlapping needs disjoint queues and microthreads on both chips. Point back to the WSE-2 shared queue.

**D8 (low). Missing: why preconditioning does not help here.**
The SDK's preconditioned-conjugate-gradient benchmark uses a Jacobi preconditioner. For this A the diagonal is a constant 6, so Jacobi only rescales the problem and leaves κ and the iteration count unchanged. A reader who meets PCG in the "after Ch 15" list of Appendix D will expect a speed-up.

Fix: one sentence. Effective preconditioners (multigrid, incomplete factorisations) need more global or recursive communication, which runs into the same allreduce cost.

**D9 (low). Column-length paragraph: the BLOCK = 100 allreduce rise is left unexplained, though a likely cause is close at hand.**
The allreduce bucket on the centre PE includes waiting at the barrier. If another PE's stencil phase ran longer at BLOCK = 100, the extra time lands in the centre PE's allreduce bucket. run.py already prints the min and max allreduce over all PEs.

Fix: report that line for the BLOCK = 100 run. If the maximum rises less than the centre PE's value, say the extra time is barrier waiting. Otherwise keep "not tracked down".

**D10 (low). Stat cards "41% / 41%".**
These shares come from PROFILE = 1, and the eight mark() calls (about 310–400 cycles, 7–10%) are spread through the buckets. The page warns about this four paragraphs later, but the cards come first.

Fix: add "(profiling on)" to the card captions.

**D11 (low). "Why the allreduce is a barrier".**
Every PE showing exactly 4,574 cycles per iteration is what any loop with a global barrier in steady state must show. It is not separate evidence of the barrier. The real evidence is the 228-cycle spread in the allreduce share.

Fix: reword so the spread carries the argument.

## Verified, no action
- The fit 958 + 100W + 88H reproduces 3,966 at 16×16 and 179,558 at 950×950.
- The widget's bound() uses the full 3-D eigenvalues.
- The κ values 13.9, 32.2 and 67.8 are correct.
- The 15, 24 and 34 iterations match my f32 numpy runs.
- The two CG dot products per iteration and the barrier argument are sound.

## Counts
High 2 (D1, D2) · Med 5 (D3–D7) · Low 4 (D8–D11) · Total 11.
