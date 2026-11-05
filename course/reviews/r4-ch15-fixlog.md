# Round-4 fix log: Ch 15, Lab 5 CG (src/15-lab-cg.html, programs/07-cg comments)

Edited src/15-lab-cg.html (rebuilt with tools/build.py) and comments only in programs/07-cg/pe_program.csl. No simulator runs were needed. The one new measured number (axpy at Z = 22, 408 cycles) comes from the round-4 audit run and is tagged as such. Checked with Playwright at 1100 px (light and dark) and 390 px: no console or page errors, no horizontal overflow, all widget controls driven, all 52 distinct links resolve (files and anchors).

## Report items
- E1 Fixed. Column-reduce item, #ar-svg caption and figure: every column reduces at once, and only the last column's sum is used. Stage 2 of the figure now shows faint arrows in the other columns.
- E2 Fixed. Removed the overlap guess and pointed to the new block anatomy (no send overlaps the @fmacs). Added the queue-depth hypothesis: memcpy gives queues 4–7 a depth of 2 [SDK], tagged Unverified.
- E3 Fixed. Changed to "35 multiply-adds (about 70 flops)".
- E4 Fixed. Stated the assumption: all-streaming ≈ 70,000 cycles; reduce crossings streaming with the broadcast at the hop floor ≈ 42,000; hop floor ≈ 15,000. Ratio changed to 2.6–12×.
- E5 Fixed. The exercise 4 hint now says "avoid 21–24" and notes that 24 (SYS_EN_MAIN) is probably needed only in some memcpy modes (link to Ch 5 #budget).
- E6 Fixed. The pe_program.csl header now says "four phases plus a stopping check" (comment-only change).
- X1 Fixed. Row-reduce item: all PEs push at once and each value waits in its output queue. switch_cmd_11 sets the sender's own router back to 0 and the next router to 1. The figure's switch labels were corrected to match (the sender's router returns to sw 0), and so was the caption.
- X2 Fixed. The text now says "one `phase` variable … where Lab 3 needed a `pending` count of four transfers".
- X3 Fixed. Added ≈ 245 device cycles per command [Derived] and a link to Ch 7's memcpy experiment (#ordering, where the box sits; the box has no id of its own).
- X4 Fixed, with a correction. The tight worst-case relation is ‖r‖/‖b‖ ≤ √κ·‖e‖_A/‖e₀‖_A (x₀ = 0), not κ: ‖r‖² ≤ λmax‖e‖_A² and ‖b‖² ≥ λmin‖e₀‖_A². The caption gives √κ ≈ 3.7 at 5³ and 8.2 at 12³.
- G1 Fixed. #modules now opens from Lab 4: one library used twice, the budget sheet, the five-step method (links to 14 #collectives and #design). The ledger rule says "the same budget sheet Lab 4 kept". The teardown paragraph links Ch 14's sequence (C_LOCK, task 29, the join, Ch 5 #join-rule) and says what is new: one color across three stages, chained by an FSM.
- G2 Fixed. New #block-anatomy: four steps from wse3/pe.csl, about 11 task runs + 8 transfer starts + 4 @fmacs starts per block ≈ 500 cycles [Derived estimate]. It explains why Lab 3 overlapped its transfers and why the library serialises its sends (the microthread hang), and cites Ch 13's 4,206 vs 8,078. The profile bullet 1 links to it.
- G3 Fixed. New #axpy-banks paragraph applies the operand rule (link 06 #collisions). A back-to-back placement model (offsets 4Z and 8Z) predicts per-cell steps of 7 / 2.7 / 8 and −32 cycles from Z = 20 to 22, against the measured 5.9 / 2.4 / 7.7 and −33. Recommendation: an odd MAX_ZDIM, "pad and measure". The paragraph also marks the 898 as the slow case. Note: the report's suggestion (≡ 2 mod 4) still leaves the p update (8Z apart) slow; an odd length makes all three fast.
- G4 Fixed. New #deps paragraph with an inline SVG (#dep-svg) of the chain β → p → SpMV → η (sum 1) → α → x, r → ρ (sum 2) → next β. The caption says how Chronopoulos–Gear merges the two sums.
- G5 Fixed. The device-loop bullet explains why phase_done() activates STATE: the callback runs inside the library's own task. Pipelined CG's "waits for both" now links Ch 14 #join.
- G6 Fixed. The #ar-svg bottom strip has two lines giving the per-contribution chain, labelled as an estimate.
- G7 Fixed. ≈ 44.5 KB usable in a minimal program (Ch 3 #memory-map) − 36.7 KB of vectors ≈ 8 KB for three modules [Derived].
- G8 Fixed. Added glossary links on first use: CG, module composition, stencil, residual, pencil decomposition, SpMV, allreduce, DSR, microthread, switch positions, control wavelet, teardown, unblock_cmd_stream, launch/RPC, TSC, weak scaling, preconditioner. Bare chapter and lab mentions now link to their section anchors.

## Cross-page items about this page
- CROSS_CHAPTER 31 / r4-ch07 E2: Fixed. The prose now says launch() returns at once and the host's next command waits (link Ch 7 #command-stream). Comments at pe_program.csl:116 and :218 (were 115/217) now read "the host's next command … can now run" / "can run".
- r4-appE G4 (SC20): Fixed. New paragraph citing Rocki et al. 2010.03660 [Indep]: < 1.5 µs over ~380k cores, ≈ 10% above the diameter, so ≈ 1,300–1,400 cycles vs ≈ 90,000 per call here; two receiving cores per row (quoted). The old "Unverified" sentence is gone.
- r4-appD G5: Fixed. Added id="two-loops" to the "Two loops, one program" h3.
- r4-appC G3: Fixed here too. Profile bullet 4 explains why mark() costs 30–35 cycles (link App C #tsc).
- r4-ch18 E5: Fixed. The whole-wafer extrapolation now tags 900k as Vendor and notes that the CS-3 SDK-visible fabric is unpublished (CS-2 ≈ 743 × 992 ≈ 737k).
- r4-ch06 G3 / r4-ch13 G5: links added from here to 06 #dsrs (@map) and 13 #sdk-stencils.
- r4-appB: Skipped the link to appendix-b #checker, because that id does not exist yet.
- Items 30–38: rates (30) applied in #axpy-banks; launch (31) fixed; clock (33): 850 MHz [SDK] is stated wherever µs are derived, and no conclusion changes at ~1.4 GHz; hop (34): 2.0 / 9.2 already used; queue depth (35) used in E2; links (38) done.

## For other pages
- appendix-e-sources.html: the Ch 15 Unverified row ("Chapter 18 cites the SC20 BiCGStab … could not check that paper's allreduce latency") is stale. The sentence is gone and the claim is now tagged Indep, so the row and its text-fragment link need updating or removing.
- appendix-b-cuda-to-csl.html: once #checker exists, Ch 15's budget widget could link to it.
- 06-dsds.html: if the Ch 6 fixer adds #banks (item 30), Ch 15's two links to #collisions could point there.
- 18-comparison.html: its SC20 lesson can now cite Ch 15's comparison (#scaling, about 1,300–1,400 vs about 90,000 cycles per call).
