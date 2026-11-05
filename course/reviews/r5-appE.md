# Round 5 fix: appendix-e-sources.html

Verdict: all five verified findings fixed. Playwright at 1100 px: zero console errors; #iss-index, #iss-clash, #used-by render; all 15 links in the edited sections resolve (incl. 03-processing-element.html#bank-model, 06-dsds.html#op-speed).

| id | kind | severity | finding | status |
|---|---|---|---|---|
| E-R5-1 | error | high | Issue 5 .index recipe could not give the stated result; simulator fault shows .index counts 16-bit words | Fixed: added Measured result (MEM[0611] not 32-bit aligned, x at 0xc20 = word 0x610), conclusion, Unknown narrowed to silicon behaviour, recipe now says run ends in fatal error in sim.log and run.py must be killed |
| E-R5-2 | error | med | WSE-3 "never slowed" overstated; with a separate destination f16 @fmach 272 -> 310, @faddh 310 | Fixed: both sentences scoped to in place; separate-destination numbers added with Measured tag and Ch. 6 link |
| E-R5-3 | error | low | Used-by row: "f16 ops ≈4 per cycle" too broad (@fmovh ≈7) | Fixed: now FMAC and add ≈4, copy ≈7 (Ch. 6 link), GEMV is FMAC-bound |
| E-R5-5 | error | low | "word" ambiguous in PAD wording | Fixed: "PAD = 0 or 4 f32 elements (0 or 16 B)", "PAD 2 for f32", "1,025 f32 elements" |
| E-R5-6 | link | low | Stride 4 vs 8 claim had no numbers/tag/link | Fixed: added 546 vs 799 cycles, Measured tag, link to Ch. 3 stride table |

## For other pages
- 06-dsds.html #index-offset still calls the 16-bit unit "Derived from the two SDK uses"; it can now cite the App E issue 5 simulator measurement (Measured).
