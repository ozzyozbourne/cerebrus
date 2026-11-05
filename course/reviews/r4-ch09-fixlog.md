# R4 fix log · Ch 9 "From model to tokens" (09-model-to-tokens.html)

Edited only `09-model-to-tokens.html`. I made no simulator runs. I did one web search, for the 2,314 tok/s source. Playwright at 1,100 and 390 px, light and dark: zero console or page errors and no horizontal overflow. I drove the lb presets at 0.85, 1.4 and 2.8 GHz, the cap clock, per-wafer and users controls, and the pd, sv and kp controls. All 83 local links and anchors resolve, including the new `06-dsds.html#banks` and `#ceilings`.

## r4-ch09 items

| ID | Status | What changed |
|---|---|---|
| E1 | Fixed | The experiment box now has a "Which clock?" note: SDK 850 MHz [SDK]; WSE-2 1.1 GHz [Vendor]; ~1.4 GHz WSE-3 and ~2.8 GHz WSE-3T [Analyst, press estimate][Unverified], linked to The Next Platform. The budget paragraph gives 5,060 / ~8,330 cycles and 31–62%. A new callout, "What the ~1.4 GHz estimate changes", covers A ≈ 1.2 ms / ~820 tok/s against the 450 launch (a teaching point), B ≈ 270 µs with slack, and a one-user bound of 3,300–6,600. The `#lb-clk` slider now goes up to 2.8 GHz. Two ceilings, quiz Q6/Q7 and the cap widget (new Clock select) state the bound as a range by clock. The propagation to other pages is listed below. |
| E2 | Fixed | The dangling "Chapter 8's benchmark run (10,160)" now cites Ch 3 `#pe-speed`'s fit, 54 + N + N² = 10,154. |
| E3 | Fixed | 9.2 is now tagged "Derived from measurements" (difference of two Lab 2 slopes); the 2.0 router hop stays Measured. |
| E4 | Fixed | Removed the quote marks from the AXPY phrase and attributed it to HC2022 "as Chapter 8 describes it". The mechanism now links Ch 5 `#activates`, Ch 6 `#fabric-dsds` and Ch 8's weight-streaming figure. |
| E5 | Fixed | The cap JS wafer rows and pipe-full now use `wGB + kvGB/users`; the GPU rows keep `tot`. The caption is rewritten to match. Check: 70B at 8K, 1 or 10 users → 2,011 tok/s either way. |
| E6 | Fixed | Weights per PE now uses one unit: 48 KiB = 49,152 B, 4,240 B of code, ~44,900 B of data, 79% / ~87%, leaving ~10 KB raw or ~6 KB after code. The cap widget has a "Per wafer: 44 GB raw / ~40 GB after code" select (405B: 19 raw, 21 after code; 10 users: 20 / 22). The quiz answer reads "19 raw, ~20–21 after code". The 405B history row adds "~21 once code is counted". |
| E7 | Fixed | The SDK table now says "at most ~14 GB/s, only if channels scale linearly … ≥ ~3 s, Derived, extrapolated (Ch 7); production weight loading is not public". |
| E8 | Fixed | gpt-oss row is now dated: ~3,000 claimed (Aug 2025), AA 2,700 (Aug 2025) → ~1,870 (late 2026), with links. Llama 3.3 row: 2,314 is labelled as an AA figure quoted in an interview whose original was not found [Unverified source]. The row adds AA's providers page (~2,270, undated) and Cerebras's Apr 2025 claim of 2,500, giving a range of ~2,270–2,500. |
| X1 | Fixed | The SDK table "M + 7P" becomes "M + 9.2·P". It explains that the ~7 own-clock step hides one router hop (cross-note 34). |
| X2 | Fixed | §pipeline now defines stage = one layer region and stage-time ≈ one layer's time (~6 µs), with S = 80 counting these. The pd hint says it lumps 4 layers per stage for drawing only. |
| X3 | Fixed (reframed per note 30) | The read-port argument is now labelled "a hypothesis, not an explanation". Under note 30, WSE-2 f16 reaches ~4/cycle when its operands are in opposite bank halves. So the paragraph says the placement data fit the hypothesis but do not test it. It ties the argument to Ch 3 `#bank-model` (bits [3:1]; 16 B of reads with no room for the write; ≥19 B/cycle measured) and says the 8-per-cycle upper end is unanchored. The experiment text now explains WSE-2's slow f16 as placement, not the chip. The collision rule is restated as note 30's one-line rule with a link to Ch 6 `#banks`. |
| X4 | Fixed | One added passage: c ≈ 0.23–0.40 under B's 8-wide kernel; draft regions sized by weights per PE are ~12,800 PEs (~113 hops), so ~1,800 cycles of collectives and an upper end of ~0.33; B's 0.35 stays in range. This also covers r3 G8. |
| X5 | Fixed | "On a GPU, decode is bandwidth-bound (Ch 1; on the wafer … see Two ceilings below)", with the new `#ceilings` anchor. |
| X6 | Fixed | Glossary links added for AXPY, tensor/pipeline parallelism, KV cache, TSC, operand collision, hop, multicast, corner turn, speculative decoding, draft, acceptance rate, c, MoE, NVLink, TTFT, disaggregation, AFD, LAIR, compile path, layer-pipelined, weight streaming and pinned-weight inference. RMSNorm and softmax are glossed inline (there is no glossary entry for either). |
| G1 | Fixed | New 2-panel inline SVG after the model list. It shows x multicast down columns, local FMACs, the row reduce and a dashed corner turn, so one product = 2 one-dimensional collectives of ~212 hops, which justifies both "at least 8" and the 212 default. A per-PE block table follows (Q/O 39×39, K/V 5×39, gate/up 135×39, down 39×135), using the fit N²/4.0 + 2.5·N. That gives ~5,730 cycles per layer (~10% above 5,228); K and V run at 33% of peak. All Derived/Unverified. Links Ch 8 `#layer` and Lab 2 `#composing`. |
| G2 | Fixed | The history closing paragraph and the CS-4 row tie the clock (~1.4 → ~2.8 GHz) to >4,400 tok/s ≈ 1.5–2.4× the CS-3 gpt-oss figures. It is flagged as a consistency check across different software dates. |
| G3 | Fixed | The "Fast per user" callout now says that at 1–2K context the same space holds ~50–100 sequences (~30–60 after code), so Ch 18's ~60 streams imply short contexts. Links Ch 18 `#cost`. |
| G4 | Fixed | Disaggregation section: a worked TTFT estimate of (1,000 + 80) × ~6 µs ≈ 6.5 ms against the published 170 / 240 ms. It says the gap must come from queueing, host/network, or a costlier prefill per position, and that the cause is unknown. |
| G5 | Fixed | The right panel of the new figure shows a context-sliced KV with a partial softmax, a max reduce and a sum reduce, plus the q broadcast. One sentence was added to the Attention step [Unverified layout]. |
| G6 | Fixed | Handled together with X3 (Ch 3 bank-model link and argument). |

## r3-gaps-ch09 items still open

- **G1, G2, G4, G5, G6, G7, G8, G9:** Fixed, as E1, X3, E6, E8, E8, E7, X4 and E6 above.
- **G3 (toy-pipeline reference solution):** Skipped. It needs an M–L simulator build plus a new program directory. The brief forbids program edits, and r4 does not re-list it. The exercise still says how to time it.
- **G10 (speed-history chart, sparsity plot):** Skipped. It is optional, and r4 does not re-list it.

## Cross-page items about Ch 9

- **r4-ch08 G6:** Fixed. "Chapter 8 ended with 'the sources do not break this down'" is reworded to a self-contained sentence. The 10,160 reference is fixed under E2.
- **Notes 30–38:**
  - 30: one bank rule; link to Ch 6 `#banks`.
  - 32: 7,500 is now called overstated everywhere on the page (text, quiz, cap bar label and readout).
  - 33: clock range.
  - 34: 9.2 / 2.0, no "~7 per PE".
  - 38: chapter and glossary links.
  - 31, 35, 36, 37: do not touch this page.

## For other pages

- **CROSS_CHAPTER_NOTES 2:** still says "No WSE-3 clock is published". Note 33 supersedes it, but item 2 itself should point to 33.
- **Ch 1, Ch 2, Ch 18:** wherever they give the single-user bound or per-second figures from cycles, add the clock: ~2,000–4,000 tok/s at 850 MHz, ~3,300–6,600 at the ~1.4 GHz press estimate (Ch 9 `#ceilings`).
- **Ch 18 (r4-ch18 G2):** Ch 9 now states the context dependence: ~13 users at 8K versus ~50–100 at 1–2K. Ch 18's KV-cap widget could link `09-model-to-tokens.html#ceilings` or `#pipeline`.
- **Ch 8 (r4-ch08 E6):** the CS-4 ">4,400 tok/s on gpt-oss-120B" claim is used by Ch 9 #history (Vendor, "not independently measured"). Ch 8 #cs4 should carry it too, with a `tag unv`.
- **Ch 12 (r4-ch12 G1):** link back to `09-model-to-tokens.html#budget`. Ch 9 now links Ch 12 `#composing` as the 2-D GEMV the region model uses.
- **App A (r4-appA G6):** the KV-cache entry can link `09-model-to-tokens.html#pipeline` for the 13 / 7 user limit.
