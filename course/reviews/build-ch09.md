# Build · Chapter 9 "From model to tokens: compiling and serving on wafers" + Ch8 slim

## What was built
- **course/09-model-to-tokens.html** (new, Part II). Sections: compile path; two compile targets; inference pipeline (moved from Ch8); decode latency budget; speculative decoding; MoE / precision / disaggregation; sparsity in practice (E4); speed history with an explanation for each jump; where the SDK fits (mapping table + optional toy-pipeline exercise); 9-question quiz.
- **Widgets (5 + 1 figure):**
  1. `#cp` compile-path figure (extract → match → size/place/route → link).
  2. `#kp` placement toy: 6 kernels on a 48×24 fabric, width sliders, serpentine shelf packing, Δt = work/cores, slowest kernel highlighted, wire length, illegal-overflow strip. Modes: compute-sized vs memory-sized (pinned inference). Buttons: Balance Δt / Equal widths / Shuffle / Graph order.
  3. `#pd` pipeline-decode animation (moved unchanged from Ch8).
  4. `#cap` wafer-count + decode-bound widget (moved from Ch8, **corrected**; see below).
  5. `#lb` per-token latency budget: stacked bars (GEMV / collectives / attention-KV / wafer hops) for one pass and per output token. Sliders: clock, GEMV rate, context, collectives/layer, hops/collective, cycles/hop, wafer hop µs, accepted tokens/pass. Presets "what-if A/B". Dashed lines at 450 / 2,100 / 2,314 tok/s.
  6. `#sd` speculative-decoding calculator: α, k, c, stages S, base tok/s. GPU vs wafer-pipeline speedup curves, plus the slot-efficiency E/(k+1) curve.
- **course/08-systems.html slimmed** (4,600 → ~3,300 words of prose):
  - Removed: "Inside the pipeline", the pd widget, the inter-wafer budget, KV arithmetic, the cap widget, the speed table, the decode-limit callout, the GEMV experiment and the cost callout, plus their JS (moved to Ch9).
  - Added: a short "Inference" section with a training-vs-inference table and a pointer to Ch9.
  - Updated: objectives; CS-4 paragraph references ("Chapter 9's inter-wafer budget / wafer-count widget"); quiz (3 inference items moved; 1 new item added).
  - Rewrote the "Where this sits for a CSL programmer" box: ISPD compile steps, pointer to Ch9, labs 11–15.
  - Timeline, weight-streaming animation, tokens-per-weight widget, layer figure and CS-4 table untouched and working.
- No changes to course.js/course.css or any other chapter.

## Measured this session (SDK 2.10.1 simulator, 1×1 rectangle, TSC on one PE)
Kernel adapted from `benchmarks/single-tile-matvec`: y += A[:,j]·x[j] via `@map` + `@fmacs`/`@fmach`. A/y offset by one word (bank clash, note 22).

| kernel | bytes | WSE-3 cycles (B/cyc) | WSE-2 cycles (B/cyc) |
|---|---|---|---|
| f32 N=100 | 40,000 | 10,147 (3.94) | 10,153 (3.94) |
| f32 N=50 | 10,000 | 2,698 (3.71) | 2,700 (3.70) |
| f16 N=140 | 39,200 | **5,228 (7.50)** | 10,271 (3.82) |
| f16 N=70 | 9,800 | 1,394 (7.03) | 2,637 (3.72) |

The f32 result reproduces Ch8's 10,160. The f16 rate doubles on WSE-3 only, consistent with note 22.

Naive k-wide f16 (N=140, extra `@fmach` per token re-reading the column via `@increment_dsd_offset`), WSE-3: k=1 5,648, k=2 15,028, k=4 32,110 cycles. This is used only as an upper bound: per-op set-up dominates.

Scratch dirs deleted.

## Key derived results (all tagged Derived in the page)
- Llama-70B on 4×CS-3: 38.9 KB weights per PE; region ≈ 45,000 PEs (~212²). One layer's GEMV at 7.5 B/cycle ≈ 5,190 cycles ≈ 6.1 µs at 850 MHz. The 476 µs/token budget is 5,060 cycles per layer at 850 MHz. **So under the region mapping, weight streaming is the largest term, about the whole per-layer budget.** The model fits 2,100 tok/s only with a clock above 850 MHz, faster kernels, or more than one accepted token per pass.
- What-if A (collectives through PE compute, 9.2 cyc/hop, no speculation) ≈ 2.0 ms/token (~500 tok/s, near the 450 launch speed). What-if B (2.0 cyc/hop, 2 tokens/pass) ≈ 418 µs. Both are presented as consistent with the vendor's "rewritten reduce/broadcast + spec decoding", not as proof.
- **Correction worth propagating (cross-chapter, not edited by me):** the "84 PB/s → ~600,000 tok/s" ceiling and the "~18,000 tok/s from the SDK GEMV" figure are *pipe-full aggregates*. One user's token is in one of 80 layer regions at a time (HC2024: "single user is using only a fraction of the total memory bandwidth"), so the per-user bound is ÷80: ~7,500 tok/s at the headline rate, ~2,000 tok/s at the measured f16 kernel rate (850 MHz).
  - Ch1 table row ("≈150,000 … 600,000") and the "65–260× above" text are affected.
  - Ch18 lines ~197–198 and the quiz at ~380 are affected. "Reading that layer's ~1.75 GB … 83 ns at 21 PB/s" assumes the whole wafer serves one layer; with regions it is ~1.7 µs at the headline rate and ~6 µs at the kernel rate. Ch18's widget tick at "~18,000 (Ch. 8)" is also affected.
  - CROSS_CHAPTER_NOTES item 6 should be refined: "not bandwidth-bound in aggregate; per user, a region's SRAM rate is within a small factor of the published speed".
  - The Ch9 cap widget now uses the ÷L per-user bound and reports the pipe-full total separately.
- Speculative decoding on the wafer: the PE datapath is balanced to its SRAM ports, so a k-wide pass in one region costs ~k× (measured naive kernel). The pipeline makes verification cheap per user: k positions trail one stage each, so the trip grows by k/S (≈5% for k=4, S=80). The system pays E/(k+1) slot efficiency when the pipe is full. Formula from Leviathan et al. 2023.
- Sparsity: a 16-bit value + 16-bit index saves SRAM only above 50% sparsity. Production serving is dense 16-bit or native 4-bit.

## Sources (new or newly fetched this session)
- **ISPD 2020 contest closing-session slides — fetched and read (now primary, tagged Vendor):** https://ispd.cc/ispd2026/slides/2020/ISPD_Contest_Closing_Session.pdf. They cover the Extract/Match/Place&Route/Link definitions, the size-place-route objective, the `convperf` cost model, "overall Δt is the max", adapters, the contest objective, and the winners (RippleWafer 1st, Gigaplacer 2nd, CUPID 3rd), plus the RippleWafer comparison numbers.
- Hot Chips 2020 AnandTech live blog (anandtech.com/show/16006): blocked (browser check). Used via search extract only, tagged "Press, via search extract".
- Cerebras blogs (fetched): Mistral Le Chat, Feb 2025 (https://www.cerebras.ai/blog/mistral-le-chat); Kimi K2.6, May 2026, with 4-bit weights / 16-bit compute, on-wafer all-to-all, custom kernels + spec decoding (https://www.cerebras.ai/blog/cerebras-kimi-k2-Enterprise); Kimi 32B active (https://cerebras.ai/blog/which-is-faster-gemini-3-5-flash-or-kimi-k2-6-on-cerebras); CS-4 press release, >4,400 tok/s/user on gpt-oss-120B.
- Llama 4 Maverick 2,522 vs 1,038 tok/s (AA via BusinessWire, May 2025).
- Leviathan et al., arXiv:2211.17192.
- NVIDIA–Groq LPX / AFD (Tom's Hardware, ServeTheHome, via search): rack size 128 vs 256 and the CPX status are tagged Unverified.
- Reused local copies of HC2024, the Oct 2024 blog, the Sol blog and the HC2026 blog in /home/user/cerebras-sdk/tmp/ch08depth/.
- No Oct 2026 Cerebras speed news was found. The latest items are CS-4 (Aug 2026) and Sol (Aug 2026).

## Validation
Playwright, Ch8 and Ch9, at 1100 and 390 px, light and dark, plus the ◐ toggle: 0 page and console errors and no horizontal overflow (scrollWidth = viewport) in every case. Every range, select, number input and button was driven (107 controls on Ch9, 25 on Ch8). I inspected element screenshots of every Ch9 widget in both themes and fixed overlaps in the compile figure, the placement side panel and overflow drawing, and the spec-decoding legend.

## Open issues
- The region mapping (every PE of a layer region joins each matvec), 8 collectives per layer at ~212 hops, and the clock are assumptions, marked Unverified/Derived. Cerebras has not published its kernels or the WSE-3 clock.
- No source quantifies spec-decoding gain, α, k or draft placement. The Kimi wafer count (~20 CS-3) is press-only.
- The cross-chapter bandwidth-ceiling correction above (Ch1, Ch18, note 6) needs a coordinator decision. Appendix E / B may want the f16 GEMV constant (7.5 B/cycle WSE-3, 3.8 WSE-2).
- Ch14/15 links in the SDK table point to pages being built by others.
