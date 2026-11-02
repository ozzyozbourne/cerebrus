# Review round 2: Appendix A (Glossary and number formats), visuals + pedagogy/usability

Method: Playwright at 1100 and 390 px, light and dark (colorScheme) plus a live ◐ toggle. I drove every control: all 9 explorer formats × 8 preset buttons, bit flips, bad input, `inf`; all 6 quantiser formats with and without the outlier, plus "New random block"; 11 searches; all 6 chips; the A–Z jumps; and `#g-wavelet`. I also checked all 183 internal links. There were no JS errors, and every link resolves. There is no horizontal page scroll at 390 px. Screenshots are in `/home/user/cerebras-sdk/tmp/r2appA/`.

## Findings

**P1 (high). The glossary stops at the old course and has no terms or links from Ch 9, 14, 15, 18 or Appendix C/D.**
- *Location:* `#gl-list`, all 131 "See" links.
- *Problem:* The "See" links go only to Ch 1–8, 10–13, 16 and 17. Not one points to `09-model-to-tokens`, `14-lab-gemm`, `15-lab-cg`, `18-comparison` or `appendix-c-measuring`. Searching for terms those pages teach gives 0 results: SUMMA, allreduce, conjugate gradient/CG, pencil, speculative decoding, MoE/mixture-of-experts, disaggregation. The lede says "Every … term the course uses", so this is false. Existing entries also miss the newer, deeper treatments:
  - `<collectives_2d>` links only Ch 12, not `14-lab-gemm.html#collectives`.
  - Join links only Ch 5, not `14-lab-gemm.html#join`.
  - TSC and Instruction trace don't link `appendix-c-measuring.html#tsc` / `#trace`.
  - Decode/prefill doesn't link `09-model-to-tokens.html#budget`.
  - Dense/sparse FLOPS doesn't link `09-…#sparsity`.
- *Fix:*
  - Add about 12 entries: SUMMA, allreduce, CG, pencil decomposition, module composition, speculative decoding, MoE, disaggregated prefill/decode, compile path/target, one-user vs pipe-full ceiling, TSC overhead/sync.
  - Add second "See" links on the entries named above.
  - Update the category counts.

**V1 (med). The "largest" button gives the wrong fp32 bit pattern, and "next value up" stalls or skips in fp32.**
- *Location:* `#bx` explorer, `fmtNum` plus the `data-v="max"` and `"next"` handlers.
- *Problem:* Both buttons write the value back into the text box with `fmtNum`. That function uses `toExponential(6)` (7 significant digits) for |v| ≥ 1e6 or < 1e-4. Re-parsing that text loses precision:
  - fp32 "largest" shows `0x7F7FFFFD` with "error 6.07e+30" (the true maximum is `0x7F7FFFFF`).
  - fp32 "next value up" from 1e-6 stays at `0x358637BD`.
  - From 12345678 it jumps `…4E → …50`, skipping one value.
  - bf16 and cb16 "largest" also show a non-zero error (3.9e31, −8), which confuses a learner on the one button that should show the exact maximum.
- *Evidence:* the drive log (`fp32 max :: 0x7F7FFFFD`, `fp32 next 1e-6 0x358637BD -> 0x358637BD`).
- *Fix:* For max and next, set `code` directly (`encode(f, target)[1]`, or the code from `positives()`), call `render()`, and only display the value in the box. Alternatively, format with `toPrecision(17)` / `toExponential(16)` when writing back into the input.

**P2 (med). Searching the glossary misses the formats this same page defines.**
- *Location:* glossary search, followed by `#formats`.
- *Problem:* Searching for NVFP4, BlockFP8, subnormal or E4M3 gives "No term matches". Those formats are taught on this page, but only in the formats section, which the search does not index. A learner who meets "NVFP4" in Ch 17 and searches here concludes it is missing.
- *Fix:* Add short entries (bf16, fp16, FP8 E4M3/E5M2, FP4/NVFP4, MXFP4, BlockFP8/bfloat8_b, cb16, subnormal, mantissa/exponent/bias), each linking to `#formats` or `#blocks`. Alternatively, have the `#gl-none` message link to "Number formats".

**V2 (med). The bit-layout figure: field labels straddle cell borders, and the "to scale" caption is false for block scales.**
- *Location:* `#fmt-svg`.
- *Problems:*
  - Each field label ("E 8", "M 23", "M 10", "E 5", "2") is centred on the field, which usually lands on the gap between two cells, so the 1-px cell strokes cut through the glyphs (`fmt-zoom.png`). Two-bit fields drop their letter, so E5M2's mantissa reads just "2" and E2M1's exponent just "2". These look like bit values, not field widths.
  - The caption says "One cell per bit, to scale within each group". However, the 8-bit amber scale box is drawn `8*cw*1.6` = 55 px wide, while an 8-bit BlockFP8 value is 34 px. This visually overstates the scale's cost by 1.6×.
  - NVFP4's per-tensor FP32 scale is in the note but not drawn.
- *Fix:*
  - Put the field labels above or below the row, or paint a background behind them.
  - Always print the letter: "E2", "M2".
  - Draw the scale at `8*cw`, or change the caption to "scale box not to scale".
  - Add a faint, separate "+ FP32 per tensor" chip on the NVFP4 row.

**P3 (med). The quantiser's outlier result contradicts the prose and is not explained.**
- *Location:* `#bq` and the `#blocks` paragraph.
- *Problem:* The prose says one large value "squeezes the small ones". With the outlier on, though, *per-tensor* FP8 E4M3 does best on the 15 ordinary values (3.1% error, 0 flushed). bfloat4_b flushes all 15 (100%), and NVFP4 and MXFP4 flush 13. The widget doesn't say why. A learner can reasonably conclude that per-tensor FP8 beats block formats. The reason is that E4M3 keeps a per-value exponent, while the block formats share one exponent across the block.
- *Fix:*
  - Add a readout line, for example: "E4M3 keeps an exponent per value, so its range absorbs the outlier; block formats share one exponent, so small neighbours lose all their bits."
  - Add a sentence to the prose.
  - Note that real NVFP4 kernels limit the damage to one 16-block, while a per-tensor scale spreads it to the whole tensor.

**V3 (med). With the outlier on, the quantiser chart hides what happened to the 15 small values.**
- *Location:* `#bq-svg`.
- *Problem:* The y-axis rescales to ±0.8, so the ordinary values become 1–3 px slivers, and the only cue left is the red "0" labels (`bq-outlier-toggled.png`). The learner can't see the reduced precision when a value is rounded but not flushed (for example BlockFP8: 12.9% error with only 2 flushed).
- *Fix:* Add a "zoom to ordinary values" toggle, or a second strip under the main chart scaled to the non-outlier maximum, with the outlier bar clipped and marked with an arrow.

**P4 (med). The glossary list scrolls inside its own box, which is hard to use on a phone.**
- *Location:* `.gl-scroll` (80vh at ≤680 px).
- *Problem:* At 390 px the box is 673 px tall with 28,965 px of content, inside a page that also scrolls. Swipes get trapped, and the page below (the formats section) is hard to reach. The letter bar helps, but its 13.5 px letters with a 2–6 px gap are small tap targets.
- *Fix:*
  - At ≤680 px, drop the `max-height` and let the page scroll.
  - Make the letter bar and the search box sticky instead.
  - Give the letters at least 28 px tap targets.

**P5 (low). No chapter links into the glossary.**
- *Location:* course-wide.
- *Problem:* No page links to `appendix-a-glossary.html#g-…`, even though every entry has an anchor and the page supports `#g-` links.
- *Fix:* Have the coordinator link the first use of key terms (wavelet, color, DSD, microthread, task ID, CB, Tensix) in each chapter, or add a "Glossary" link to the top bar.

**V4 (low). After a bit flip produces Inf or NaN, the explorer breaks on the next format change.**
- *Location:* `#bx`.
- *Problem:* Flipping a bit writes "Infinity" or "NaN" into the input. `fromValue` lower-cases this to "infinity", which `Number()` rejects. Changing the format then shows "Type a number such as 0.1…", and the old bits are still drawn.
- *Fix:* Accept `infinity`/`-infinity`/`nan` in `fromValue`, or keep the current `code` when the text is not numeric.

**V5 (low). Some explorer messages are wrong or missing for edge cases.**
- *Location:* the `#bx` readout.
- *Problems:*
  - For int8 and i16, entering 0.1 prints "underflow: below half the smallest subnormal". Integers have no subnormals, so this should say "rounds to 0".
  - Typing `inf` in E4M3 or E2M1 silently gives 448 or 6, with no saturation line, because `orig` is not finite.
  - "next value up" at the maximum does nothing and gives no feedback.
- *Fix:* Change the message for the integer branch, handle a non-finite `orig` in the saturate branch, and make the button print "already the largest finite value".

**V6 (low). Two category chips fall below 4.5:1 contrast in light mode.**
- *Location:* `.cat-wse` (4.34:1) and `.cat-tt` (4.29:1), at 10.5 px. Dark mode is 5.7–8.2:1.
- *Fix:* Darken `--accent`/`--green` text on these chips, or raise them to 11.5 px bold.

**V7 (low). Several smaller layout and labelling issues.**
- *Location:* various.
- *Problems:*
  - At 390 px, the `#fmt-svg` fp32 row and the block notes run past the 620 px min-width crop. "32 bits" and "→ 8.5 bits per value" are cut until the user scrolls sideways.
  - `SINGULARITYENV_SIMFABRIC_DEBUG=inst_trace` overflows its `dd`, creating a horizontal scrollbar inside the glossary box.
  - At 1100 px the search placeholder is clipped ("CB, t…").
  - Opening `#g-…` scrolls `#gl` under the sticky top bar, which hides the widget heading.
  - Substring search (for example "sm", 18 hits) matches hidden aliases and words like "smallest", leaving entries with no visible highlight.
  - The "one outlier (×40)" label is a fixed 0.8 = 40σ, not 40× any value shown.
- *Fix:*
  - Shorten the SVG notes, or wrap them onto two lines.
  - Add `overflow-wrap:anywhere` to `dd code`.
  - Shorten the placeholder.
  - Add `scroll-margin-top` to `#gl`.
  - Match on word starts.
  - Relabel the switch "one outlier (≈40× the typical value)".

## What works
- The theme toggle recolours the SVGs live.
- The filter chips and letter dimming are correct: V, X, Y and Z are off for All, and the right letters go off per machine.
- The hash links flash the right entry, and the search highlights matches.
- Rounding to nearest-even matches IEEE for fp16, bf16 and fp32: 0.1 gives `0x2E66` in fp16 and `0x3DCD` in bf16, and 3.14159 gives `0x4248` in fp16.
- E4M3 saturates at 448 and E5M2 at 57,344.
- The format table and the support table read well, and the "Three rules" callout is a good close.
