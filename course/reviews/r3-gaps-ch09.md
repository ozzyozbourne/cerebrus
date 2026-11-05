# R3 gap audit · Ch 9 "From model to tokens" (09-model-to-tokens.html)

Inputs: GAP_AUDIT_BRIEF, REVIEW_BRIEF, CROSS_CHAPTER_NOTES 1–29, build-ch09.md (open issues), r2-ch09-fixlog.md ("Not done"), the page text and the cap/lb widget JS. Cross-checked Ch 1, Ch 7, Ch 18, App A/B/E. All page arithmetic re-done (GEMV 5,190 cyc, KV 0.33 MB/token, 110k/63k tokens, 13/7 users, what-if A ≈ 1.99 ms, 405B 19 wafers / 0.41 vs 6.4 GB, 9 ms KV transfer, spec 1.4×/2.8×). It is all correct. No simulator runs were made. Web searches were made (Next Platform could not be fetched: the host is blocked in this session).

## Gaps, ranked by value to the learner

**G1 · high · §A decode latency budget, #lb clock slider, "Two ceilings", history closing para.**
- **What is missing.** The chapter's central conclusion assumes an 850 MHz clock and states "No WSE-3 clock is published". It says the measured GEMV is "about all of the per-layer budget", that the model fits 2,100 tok/s only with a higher clock, faster kernels or speculation, and that the single-user bound is 2,000–4,000 tok/s. Since Aug 2026, press coverage of CS-4 gives an estimated WSE-3 clock of **~1.4 GHz**, with WSE-3T (Turbo) at ~2.8 GHz.
- **Evidence.** Next Platform, 19 Aug 2026, "Cerebras overclocks WSE-3…", says 2.8 GHz has "doubled from the 1.4 GHz used in the plain vanilla WSE-3", and calls it a likely figure. ServeTheHome and diariobitcoin repeat it as an estimate. No course page mentions 1.4 or 2.8 GHz (grep). The `#lb-clk` slider is capped at 1.3 GHz, so a learner cannot even try the estimate.
- **Why it matters.** At 1.4 GHz the per-layer budget is ~8,330 cycles, and the measured GEMV uses ~62% of it, not ~100%. The single-user bound becomes ~3,300–6,600 tok/s. What-if A drops to ~1.2 ms (~830 tok/s), which overshoots the 450 tok/s launch speed. That gap is itself a teaching point: the launch kernels were worse than this model, or the clock was lower.
- **How to resolve.**
  - Add the estimate with tags Press + Unverified, and keep 850 MHz as the SDK assumption.
  - Extend the slider to 1.5 GHz (and mention 2.8 GHz for CS-4).
  - Restate the conclusions as a clock range: "at 850 MHz… at an estimated 1.4 GHz…".
  - Flag the same issue for Ch 1, Ch 2 and Ch 18, and add it to CROSS_CHAPTER_NOTES 2/27.
- **Resolvable:** yes, via web (fetch the Next Platform article from a session that allows the host) and writing. **Effort:** M.

**G2 · med · §A decode latency budget ("This is the kernel's limit, not the chip's"), cap widget "8-wide" row, quiz Q6.**
- **What is missing.** The 2× upper end of every bound (4,000 tok/s, ~2,600 cycles per layer, what-if B) rests on the untested read-port hypothesis: an AXPY reads both A and y, so a weights-only form could reach 8 f16 MAC/cycle. The r2 fix log lists it as "not re-measured". It also does not explain WSE-2's 2/cycle.
- **How to resolve.** Use the simulator, in a 1×1 copy of `single-tile-matvec`:
  - Time single-read-stream f16 ops (`@fmulh` or `@fmovh`, mem→mem, 1,024 elements, TSC).
  - Time an f16 FMAC whose accumulator is a fabric or scalar operand rather than a memory stream (the `gemv-checkerboard-pattern` `@fmach(…, wlet_data)` form is a starting point).
  - If a single-stream op reaches ~8/cycle on WSE-3, the hypothesis gains real support. If it does not, retag 15 B/cycle as speculative and narrow the range.
- **Resolvable:** yes, via the simulator. **Effort:** M.

**G3 · med · Optional exercise "toy inference pipeline" (Where the SDK fits).**
- **What is missing.** The exercise has no reference solution, and its "Expected" result (one token ≈ the sum of GEMV times plus a few cycles per hop; a second user changes it by less than ~1%) was never measured. That makes it the chapter's only unchecked prediction, and a learner who gets something else cannot tell whether they or the text is wrong.
- **How to resolve.** Build the 2–3 region pipeline from `single-tile-matvec` plus Lab 2's color hand-off on a 3×1 rectangle. Measure one-user and two-user round trips with TSC on PE 0. Then either add `programs/08-toy-pipeline/` with the program and its expected output, or at least put the measured numbers in a collapsible answer.
- **Resolvable:** yes, via the simulator. **Effort:** M–L.

**G4 · med · cap widget, quiz "405B wafers", §A model "Weights per PE".**
- **What is missing.** The page subtracts ~4.2 KB/PE of code from the KV budget (13 → 7 users), but the wafer-count widget and quiz still use the full 44 GB per wafer. With ~3.8 GB of code per wafer, 405B at 16-bit needs ~21 wafers, not 19.
- **Evidence.** In the `cap()` JS, `cnt = ceil(tot / 44)`. The quiz says "810 ÷ 44 ≈ 19". 70B still needs 4 wafers either way.
- **How to resolve.** Add a "usable per wafer: 44 / ~40 GB (after code)" toggle or line, and amend the quiz answer to "19 raw, ~20–21 with code".
- **Resolvable:** yes, writing and JS only. **Effort:** S.

**G5 · low · Speed history table, gpt-oss-120B row ("~3,000 claimed vs ~1,700 measured").**
- **What is missing.** The row has no date and is stale. Artificial Analysis now shows Cerebras gpt-oss-120B at ~1,840–1,900 tok/s, and Cerebras's Aug 2025 blog cited 2,700 from Artificial Analysis. The measured figure has varied over time.
- **How to resolve.** Give a dated range, e.g. "AA: 2,700 (Aug 2025) → ~1,850 (Nov 2026)". Also note that AA has not measured CS-4 (the >4,400 claim is still vendor-only, which confirms the current tag).
- **Resolvable:** yes, via web. **Effort:** S.

**G6 · low · Speed history, Llama 3.3-70B 2,314 tok/s row.**
- **What is missing.** The source is given only as "reported in an interview", so a learner cannot check it.
- **How to resolve.** Cite the Artificial Analysis provider page or press release directly, with a date.
- **Resolvable:** yes, via web. **Effort:** S.

**G7 · low · SDK table, "Loading weights… host memcpy ~14 GB/s, so ~3 s per 44 GB".**
- **What is missing.** Ch 7 frames 14 GB/s as an *at most* extrapolation from 16 simulated channels, "only if channels scale linearly". Ch 9 drops that hedge and implies production loads weights through host memcpy, which is unsourced.
- **How to resolve.** Add "at most, extrapolated (Ch 7)" and tag it Derived.
- **Resolvable:** yes, writing only. **Effort:** S.

**G8 · low · "The draft is not cheap on a wafer", c range.**
- **What is missing.** The ~0.4 upper end combines target-sized collectives (3,400 cycles, 212 hops) with draft regions "sized like the target's" in weights per PE. But such regions hold ~12,800 PEs (~113 hops), so their collectives would be ~1,800 cycles. Recomputed, c ≈ 0.32, which is still inside the stated 0.3–0.4, but the derivation is internally inconsistent.
- **How to resolve.** Add one sentence giving the region-size/hop scaling, or quote 0.15–0.35.
- **Resolvable:** yes, writing only. **Effort:** S.

**G9 · low · Unit mixing in "Weights per PE".**
- **What is missing.** The section uses 48 KB = 48,000 B, giving 81% and 89%. With 48 KiB (49,152 B) the figures are 79% and ~87%, and note 13's usable figure is 44,500 B ≈ 43.5 KiB.
- **How to resolve.** State the unit, or use KiB throughout to match Ch 3 and Ch 10.
- **Resolvable:** writing only. **Effort:** S.

**G10 · low · Missing visuals (r2 "Not done"): speed-history chart and sparsity break-even plot.**
- **What is missing.** A small log-scale timeline of tok/s per model, colour-coded by lever, would carry the "every row is a different model" lesson better than the 10-row table.
- **Resolvable:** writing/JS. **Effort:** M.

## Not gaps (checked and rejected)
- Ch 1 and Ch 18 single-user bound wording now matches the 2,000–4,000 range (r2 coordinator items 2 and 3 are done).
- Glossary entries for LAIR, AFD and draft cost c, and the App B/E 8-wide caveat, exist.
- All 7 cross-page anchors resolve (10#memory, 04#latency, 12#hop-cost, 06#collisions, 06#op-speed, 03#simd, C#tsc).
- KV, GEMV, attention (~100 / ~1,600 cycles), inter-wafer (34 MB/s, 4%), KV transfer (9 ms, 19 tokens) and the 405B 6% arithmetic all re-derive correctly.
- The spec-decoding formulas and quiz numbers (3.36, 2.8×, 1.4×, 67%, 65 slots) are consistent with notes 27/28 and the glossary.
- The pd widget offering 20 users is not a contradiction: context is unspecified and the readout names the KV limit.
- The kp side panel off-screen at 390 px was optional per the brief, and the readout names the bottleneck.
- The CS-4 >4,400 tok/s claim is still vendor-only (no AA measurement found), so the current tag is right.
- The 405B 969 → 539 cause and the Kimi "~20 CS-3" are still unpublished or press-only, as tagged. Not resolvable.
- The region mapping and collective count are unverifiable without Cerebras kernels (needs an unavailable source), and are already tagged.

Sources: nextplatform.com/compute/2026/08/19/cerebras-overclocks-wse-3-waferscale-engine-to-boost-inference-oomph-in-nexus-cs-4/5289400 (search extract); servethehome.com/cerebras-intros-faster-wse-3-turbo-processor-and-first-rack-scale-cs-4-system/; artificialanalysis.ai/providers/cerebras; cerebras.ai/blog/openai-gpt-oss-120b-runs-fastest-on-cerebras.
