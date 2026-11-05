# R4 fix log · ch12 · Lab 2 (src/12-lab-neighbours.html)

Edited only `src/12-lab-neighbours.html`, then ran `tools/build.py`. Verified with Playwright at 1100 px: router stepper (one-color mode, all frames) and race widget (step, chip switch, play/pause) work, 0 console errors, all 51 links (in-page and cross-page anchors) resolve.
One experiment (in `/home/user/cerebras-sdk/tmp/r4fix-ch12/`, since deleted): the store-and-forward diff now shown on the page gives 348 cycles at P = 8, M = 32 with SUCCESS. That matches the table.

## Errors
- **E1** Fixed. #streaming now says gemv-08's middle columns stream `@fadds(out_dsd, y_dsd, in_dsd)` (SDK-tagged) and that gemv-06/07 are 2 PEs wide. #composing says gemv-08 uses program 03's first/middle/last pattern and differs only in the `recv_x` data task and per-scalar `@fmacs`. Both store-and-forward claims are gone.
- **E2** Fixed. Step 6 now says launch has already returned and the next command, `memcpy_d2h`, waits on each PE until it unblocks. Links to Ch 7 #command-stream (CCN 31).
- **E3** Fixed. Changed to ≈18 wavelets per hop: the 16 own-clock reading plus the 2-cycle clock offset agrees with 128/7 ≈ 18. Rule of thumb is now 18·(P − 1).
- **E4** Fixed. Kept "hops dominate past P ≈ M/9". The tree claim is replaced by Ch 14's model with its crossovers (P ≈ 27 at M = 32, ≈ 280 at M = 256: 2,776 vs 2,761), linked to 14-lab-gemm.html#next.
- **E5** Fixed. The stepper hint and its last frame now say that cslc rejects the route on WSE-3 ("expected at most 1 input direction(s)") and that it compiles and gives a wrong answer on WSE-2. Links to Ch 4 #route-register.
- **E6** Fixed. The bank-clash rule now cites Ch 6 #collisions, worded as "same bank, addresses equal mod 16 bytes" (CCN 30).
- **E7** Fixed. Removed the dead `tmp/fix-ch11/...` paths ("not shipped"). Replaced "The depth review delayed" with "We delayed".
- **E8** Fixed. The excerpt uses `P - 1`, declares `v` and `r`, and shows `@set_tile_code(..., .{ .c2d_params = params, ...})` with `param c2d_params`.
- **E9** Fixed. Step 5 now says PE 1 normally consumes about one hop later, and that PE 0 *can* finish without that because ~18 wavelets fit in a hop. Links to #late-pe.

## Explanation problems
- **X1** Fixed. Cross-chapter links added to Ch 4 (#checkerboard, #route-register, #latency, #back-pressure, #switches/#filters/#teardown), Ch 5 (#portability, #picker), Ch 6 (#fabric-dsds, #collisions), Ch 7 (#frame, #command-stream), Ch 9 #budget, Ch 10 (#builds, #hangs), Ch 11 (#kernel-time, #trouble), Ch 13, Ch 14 (#collectives, #next) and App C #tsc. Glossary links added for multicast, TSC, store-and-forward, checkerboard, microthread, back-pressure, hop, bank clash and kernel stall. New in-page anchors: `#same-pe`, `#going-2d`.
- **X2** Fixed. The title is now "...but were not in Lab 3's first version (Chapter 5)", with links, and the body says Lab 3 is Chapter 13.
- **X3** Fixed. Rough split of the ~37: about half is the root's own send (50 = M + 18). The rest (first hop, receiver op start-up, completion) is stated as not separated. Tagged Derived.
- **X4** Fixed. Added a note that the WSE-2 router-only points below P = 12 are irregular (105 → 94), the cause was not tracked down, and they count as noise. Tagged Unverified. No rerun.
- **X5** Fixed. c is split into a 2.0/1.0 router hop (Measured) and ≈7.2/5.0 for ramps plus CE pipeline (Derived, not separated further). c is now tagged "Derived from measurements".
- **X6** Fixed. The 3,025/11,463 totals are now labelled as uninstrumented runs (Measured).
- **X7** Fixed. The exercise 3 answer is now "Probably ... not isolated", tagged Unverified.

## Connecting gaps
- **G1** Fixed. The lede now ties to Ch 9's ~12 collectives per layer (at least 8, ~12–14), with a link.
- **G2** Partly. The brief forbids program edits, so no variants were shipped to `programs/03-row-reduce/variants/` and `run_all` is unchanged. The page now shows the verified 5-line store-and-forward diff (348 cycles measured again) and explains why each hop costs M + 2c. It also describes the round-trip variant's route. The round-trip and 2-D variants are still not shipped.
- **G3** Fixed with E4: forward link plus crossover numbers.
- **G4** Fixed. Step 3 states the per-PE command-queue model (launch returns at once; the next command waits for unblock) and links Ch 7 #command-stream. The skew callout points back to it.
- **G5** Fixed. The ~18 is mapped onto iq 2 = 4 and oq 2 = 6 wavelets (SDK memcpy.csl comments, CCN 35), with ~8 in the router and ramp buffers (Derived). It is tied to Ch 5's "stalls past 14" (described as total I/O-path buffering) and to Ch 4's "nothing is dropped".
- **G6** Fixed. Switches, filters and teardown link to Ch 4. The library walk-through links to Ch 14 #collectives.
- **G7** Fixed. Explains that the three 16-bit words arrive in u32 slots and are joined. Gives the start/end stamp pattern and the ~10-cycle empty-pair cost (glossary). Links Ch 11 #kernel-time and App C #tsc.
- **G8** Fixed. Added a gloss for "systolic" in the objectives, with a link to Ch 6's fabric-DSD figure.

## Cross-page items about this page (from other r4 reports)
- r4-appC G2 links to `12-lab-neighbours.html#measuring`: the anchor still exists, and the stamp pattern is now named there.
- r4-ch09 / r4-ch18 / r4-ch04 (7 vs 9.2 per hop): this page already explains the own-clock artefact, and c is now tagged Derived to match those pages. The fixes themselves belong on those pages.
- CCN 31 (launch) applied in step 6. CCN 34 (hop costs) is consistent. CCN 30 (bank rule) applied. CCN 35 (queue depths) applied. CCN 38 (links) applied.

## For other pages
- Ch 14 (#next aside): it quotes "Chapter 12 measured store-and-forward at >3×". Still true. That page could link to `12-lab-neighbours.html#streaming`, which now shows the store-and-forward code.
- Ch 4 (#back-pressure hint): "real depths are not published" contradicts CCN 35. It should cite the memcpy.csl depths (iq 6/4/2, oq 2/6/2), as this page now does.
- Ch 5 (quiz at "stalls past 14"): it has no anchor, so this page links only to the top of 05-tasks.html. An id there would let it deep-link.
- App B (hop row): could use this page's fit form M + c·(P − 1) + fixed, per r4-appB.
