# Review 2 · Chapter 9 "From model to tokens" · Pedagogy

Scope: `course/09-model-to-tokens.html` (about 6,600 words, 9 h2 sections, 5 widgets, 9-question quiz, 1 optional exercise). I checked the arithmetic in every quiz answer and worked example and found all of it correct (5,190 cycles / 6.1 µs / 490 µs; 268 GB vs 36 GB; 19→20 wafers; E = 3.36, 2.8× / 2.7× / 67%; 34 MB/s; what-if A ≈ 2.0 ms, B ≈ 418 µs; 8K/128K attention ≈ 100 / 1,590 cycles). The findings below are about how easily a learner can follow the chapter.

## Findings

**P1 · med · "Experiment: a decode-like GEMV" (lines ~177, ~185) and "Optional exercise" (line ~317): internal reviewer notes are shown to learners.**
The learner-facing text says "the bank clash of note 22", "(note 22)" and "a round trip as in note 19". These refer to `reviews/CROSS_CHAPTER_NOTES.md`, which learners never see.
Fix: replace each one with the course location and a short clause. For example, "the SRAM bank clash between operand streams (Chapter 6 / Lab 1, Chapter 11): padding one word restores 1 element/cycle", "WSE-3 does ~4 f16 MACs per cycle (Chapter 6)", and "TSC counters on different PEs start at different times, so time a round trip on one PE (Lab 2, Chapter 12)".

**P2 · med · "The model" bullet "Weights per PE" vs the "Two compile targets" table: the same page gives two inconsistent SRAM budgets.**
The budget says 38.9 KB of weights is "about 81% of each 48 KB SRAM… leaves ~9 KB per PE for KV cache, code and buffers". The table a few screens earlier says "~44 KB per PE of user data on WSE-3 (Chapter 10)", and note 13 puts fixed overhead at ~4.6 KB. A careful learner computes 44 − 38.9 ≈ 5 KB, not 9, and does not know which number to trust. This also feeds the "~36 GB left for KV" number used in the KV section and in quiz Q3.
Fix: say "~9 KB raw, of which ~4–5 KB remains after code and the task table (Chapter 10)". Then add one sentence noting that the 36 GB KV figure is an upper bound for the same reason. The section already says "even if all of it held KV", so connect the two explicitly.

**P3 · med · "Two ceilings, not one" callout: it corrects a claim the learner never saw, and Chapter 18 still teaches the uncorrected version.**
The callout says "Earlier chapters' '~18,000 tok/s from the GEMV benchmark' is the four-wafer figure…". No chapter 1–8 contains 18,000 any more (grep finds no match in 01, 08 or 18). Meanwhile 18-comparison.html line 216 ("limited by pipeline latency, not bandwidth"), quiz line 380, and widget text line 498 ("pipeline latency, not bandwidth") still state the claim this chapter calls only true in aggregate. A learner who reaches Ch18 gets contradictory messages.
Fix: in Ch9, delete the "Earlier chapters'…" sentence or reword it to "A tempting estimate multiplies the GEMV rate by all four wafers' PEs (~18,000 tok/s); that is a throughput ceiling…". Flag Ch18 lines 216/380/498 to the coordinator so they can be aligned with note 25 ("per-region SRAM reads plus latency/communication").

**P4 · med · Speculative decoding, "On the wafer that argument fails, and a different one works": two models of verification are presented back to back without saying which one the formula uses.**
The paragraph first argues that a k-wide pass in one region costs about k× and backs this with a measured 15,028 / 32,110 cycles. It then says the positions instead trail one stage apart, so the cost is k/S. A learner cannot tell whether the measured k-wide kernel matters to the speedup formula. It doesn't, because the formula assumes the pipelined mode. The budget widget's "Accepted tokens / pass" slider also just divides pass time by tokens, with no k/S or c term, which contradicts the formula introduced in the next section.
Fix: add one bridging sentence: "So the compiler should not batch the k positions inside a region (that costs k×, measured below); it should feed them one stage apart, which costs k stage-times." In the budget hint, state that the slider is net tokens per pass after the k/S and draft overhead, and point to the speculative-decoding widget.

**P5 · med · Placement in Part II: forward references to constants the learner has not met yet.**
The budget is built on "Chapter 4's and Lab 2's measured cycles per hop". The 9.2 cycles/hop-through-compute value appears only in Chapter 12 (Lab 2), three chapters later. The SDK mapping table also cites "chain reduce ≈ M + 7P", SUMMA and `<collectives_2d>` (Ch12/Ch14), and "ghost exchange" (Ch13) without definitions. The objectives promise that the learner will "build a per-token decode latency budget from this course's measured constants", but at this point in the course they cannot have seen several of those constants.
Fix: in the budget section, give each constant a one-line provenance and preview, for example "9.2 cycles: a hop that passes through a PE's receive-add-send, measured in Lab 2 (Chapter 12); for now, take it as given". In the SDK table, add a short gloss per primitive (SUMMA = broadcast A row-wise and B column-wise, multiply-accumulate locally; ghost exchange = halo cells copied from the neighbour).

**P6 · med · "Optional exercise: a toy inference pipeline in CSL": it is not doable at this point and has no checkpoint.**
It needs layout.csl, colors, routes, the TSC and memcpy. The learner has seen these only in passing and writes them first in Chapters 10–13. The exercise has no expected result beyond "time per token does not change", and no hint about how two stages share one PE's timer.
Fix: label it "Return after Lab 3 (Chapter 13)", or move it to the end of Ch13/14 and link it from here. Add a target ("expect ≈ 2 × GEMV + hop cycles per token; a second user should leave this unchanged within ~1%") and a hint naming the starting files.

**P7 · low · Objective 3: "check it against the published 476 µs per token".**
476 µs is derived from the published 2,100 tok/s; it is not itself published.
Fix: "…against the 476 µs per token implied by the published 2,100 tok/s".

**P8 · low · Quiz coverage.**
The nine questions cover placement, pipelining, KV, wafer count, the GEMV budget, ceilings, speculation, MoE and sparsity. None covers the compile-path stages (objective 1, first half) or disaggregation and precision (objective 5).
Fix: add one question, such as "Why does a CS-4 disaggregated deployment need fast wafer I/O? (~2.7 GB of KV per 8K-context Llama-70B request)". Optionally add a matching question on what "match" does in the compile path.

**P9 · low · "How many wafers" widget: the model presets imply dense models.**
The 120B and 1T presets (gpt-oss-120B and Kimi are both MoE) are interpolated as dense models with Llama-3 shapes. The caption says that MoE is ignored, but the MoE section later tells the learner that only ~32B is streamed per token. A learner comparing the 1T bound with Kimi's 981 tok/s will be misled.
Fix: add to the caption "120B and 1T are treated as dense; for MoE models the per-user bound would use active parameters (see the MoE section)". Alternatively, label those presets "dense 120B / dense 1T".

**P10 · low · Undefined or late-defined terms.**
- Δt is first defined inside the convperf code block ("cycles per sample"). Add it to the prose before the block.
- "LAIR" and "XLA" appear in the figure caption without a gloss.
- "WSE-3T" and "AFD" in the history and disaggregation sections are used once without explanation.
- The 24 B/cycle "HC22 port peak" option in the budget widget is not explained anywhere in the text.

Fix: add a short gloss for each at first use.

**P11 · low · Length and pacing.**
The chapter runs to about 6,600 words. The budget section alone stacks a model, an experiment table, a widget, a callout and a GPU comparison. That is heavy for the last chapter of Part II.
Fix: put a 3-line "where we are" recap at the top of "A decode latency budget" and at the top of "The speed history". The GPU comparison paragraph at the end of the "Two ceilings" callout could be a separate short callout.

## Strengths (keep)
- Clear tagging of what is Vendor, Derived and Unverified, plus the up-front "What is public" callout.
- The quiz answers are correct and test reasoning rather than recall.
- What-if A/B presets reproduce the 450 → 2,100 story numerically and match the "Things to try" text.

## Counts
High 0 · Med 6 (P1–P6) · Low 5 (P7–P11)
