# Round 5: index.html fix log

**Verdict:** all 7 verified findings fixed. Playwright check at 1100 px: zero console errors, 23 cards render, no horizontal scroll, and the new link to appendix-e-sources.html#tags resolves.

| ID | Kind | Sev | Finding | Status |
|---|---|---|---|---|
| IDX-1 | error | med | The widget stat said 90. The real count is 91, because round 4 added #mm to Ch 8. | Fixed: now 91 (grep count = 91) |
| IDX-2 | error | low | "each with diagrams" was false for App. D and E. | Fixed: "chapters and appendices; every chapter has diagrams" |
| IDX-3 | error | low | The page said every chapter ends with "Check yourself". Ch 11, 12 and 18 do not. | Fixed: wording now covers Labs 1–2 (exercises) and the Ch 18 final check |
| IDX-4 | unmarked | low | The Ch 15 blurb stated the wafer-scale allreduce dominance as a result. It is an extrapolation. | Fixed: now "60% of an iteration at 16 × 16 [Measured]; its measured fit predicts (an extrapolation, not a run) it dominates at wafer scale" |
| IDX-5 | gap | low | The run command covered WSE-3 only, and its paths were relative with no root given. | Fixed: both ARCH=wse3 and ARCH=wse2 commands, "from the repository root", with a note that WSE-3 is the default |
| IDX-6 | error | low | The App. D blurb said every example is mapped to an explaining chapter. 3 are not covered. | Fixed: "(59 items), with the chapter that covers it or a note that none does" |
| IDX-7 | tag | low | The tags had no definitions link, and the index's own figures were untagged with no pointer. | Fixed: "provenance tag" links to appendix-e-sources.html#tags, with a sentence saying lede and summary figures are tagged in their chapters |
