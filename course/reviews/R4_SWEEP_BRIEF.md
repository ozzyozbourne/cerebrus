# Round-4 cross-page sweep brief

Every page has had its round-4 fix pass. Each fix log (reviews/r4-*-fixlog.md) ends with "For other pages" requests;
they are collected in reviews/R4_OTHER_PAGES.md. Many were already handled by the target page's own fixer (who ran
later), so CHECK THE CURRENT FILE before every change and apply only what is still missing or wrong.

Read first: REVIEW_BRIEF.md, CROSS_CHAPTER_NOTES.md items 30–38 (canonical), R4_FIX_BRIEF.md (style/verification rules).

Your job, on the pages assigned to you only:
1. Apply each still-needed request from R4_OTHER_PAGES.md that targets your pages.
2. Bank links: Ch 6 now has the canonical placement table at `06-dsds.html#banks`. Retarget links that point at
   `06-dsds.html#collisions` or `#op-speed` *for the bank/placement rule* to `#banks` (leave links that are really
   about op speed in general). Remove any surviving retired rates/explanations (WSE-2 f16 "2/cycle" as a rate,
   "3.2/cycle", "WSE-3 doubles f16/adds", "memory traffic", "two reads and a write", "@fadds shows no penalty" unscoped).
3. Clock labelling: any "2,000–4,000 tok/s" one-user figure must say it assumes the SDK's 850 MHz, and mention the
   ~3,300–6,600 at the ~1.4 GHz press estimate (link `09-model-to-tokens.html#ceilings`) where a range is shown.
4. Inbound links: add a short "Next in the SDK → Appendix D" link (`appendix-d-sdk-index.html#after-chNN`; ids:
   after-ch03,04,05,06,07,10,11,12,13,14,15, after-beyond for Ch 18) near the end of each assigned chapter that has an
   id; and in Ch 5/6/7/10 "If you know CUDA" callouts, a link to the matching App B row (ids listed in R4_OTHER_PAGES).
5. CS-2 750 × 994 / 743 × 992: wherever stated without it, add the caveat linking `02-the-wafer.html#cs2-dims`.
Labs 11–13: edit src/*.html then `python3 tools/build.py`. Do not touch 14-lab-gemm / src/14, programs/06-summa,
appendix-e-sources.html, CROSS_CHAPTER_NOTES.md, assets/, tools/.
Verify each page you changed in Playwright (1100 px): zero console errors, all links/anchors resolve.
Append your results to reviews/r4-sweep-<your-part>.md: per request, Done / Already done / Skipped (+why). Final reply ≤6 lines.
