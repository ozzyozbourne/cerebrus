# R5 fix log: appendix-d-sdk-index.html

Verdict: 6 fixed, 2 partly fixed (the other-page parts were left out because this fixer may edit only this page). Playwright check at 1100 px: zero console errors, Ch 6 ladder and index rows render the new text, all 111 links/anchors resolve.

- D1 (error, high): Fixed. The vendoring recipe now also rewrites the two `get_stencil_module()` paths in `stencil_3d_7pts/pe.csl` (lines 63/65). It also says that 07-cg's copy changes those two paths (checked by diff against programs/07-cg/lib).
- D2 (unmarked, med): Fixed. The recipe is tagged Unverified: it was not run on an SDK example, and programs/07-cg is the tested instance.
- D3 (link, med): Fixed with the alternative. I dropped "(CS-1 BiCGSTAB for comparison)" from the #sdk-stencils label. For other pages: adding id="scaling-up" to the h3 in src/13-lab-stencil.html would let this link point at the BiCGSTAB comparison.
- D4 (link, low): Partly fixed. The hint now names the "Try it yourself: time one PE and read its memory map" callout and links 03-processing-element.html#wse2-wse3, the section that holds it, instead of #feed. For other pages: Ch 3 could give the callout an id (e.g. try-stm) so the link can point at the callout itself.
- D5 (error, low): Fixed. fft-3d now reads "no PE code of its own (only layout.csl and run.py besides its README and script)", and gemv-00-basic-syntax is added to the exceptions as a single code.csl.
- D6 (tag, low): Partly fixed. This page now uses separate tags: Analyst (The Next Platform, 2026-08-19) and Unverified. For other pages: src/13-lab-stencil.html Caveats needs the same change.
- D7 (unmarked, low): Fixed. Added after the code block: "Output above: Measured, WSE-3 simulator, 5 × 5 PEs, zDim 5, 2 iterations" (matches commands_wse3.sh).
- D8 (error, low): Fixed. The Ch 6 ladder note now says to run it after gemv-01 (Ch 10 rung) and raise size past 14 wavelets. Teaches now reads "stalls once size exceeds the I/O path's buffering (14 wavelets per its README)". A row note carries the SDK tag and the CROSS_CHAPTER_NOTES 35 point that 14 is the whole I/O path's buffering, with a link to Ch 6 · FIFOs.
