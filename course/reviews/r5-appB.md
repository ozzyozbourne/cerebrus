# Round 5 — Appendix B (appendix-b-cuda-to-csl.html) fix report

**Verdict:** all 8 verified findings fixed. Checked with Playwright at 1100 px: zero console errors, every relative link and anchor resolves, and the budget checker's p06 preset and local-task checks work on both chips.

| id | kind | sev | finding | status |
|---|---|---|---|---|
| B5-1 | error | med | The "isolated 15–17 start-ups" figure ≈ 108 was left over from round 2; it is now ≈ 116–122 (58.4 + 13 + 3 × 15–17) instead of 90, tagged Derived | Fixed |
| B5-2 | error | med | memcpy's local tasks are now listed as 24, 27, 28, 30; 21–23 are now described as reserved in the WSE-3 task map / data tasks of memcpy's colors 21–23 on WSE-2. Checker: memL = [27, 28, 30], and 21 is now handled like 22 and 23 (an issue on WSE-2, a warning on WSE-3) | Fixed |
| B5-3 | error | low | The p06 preset note now gives both chips: WSE-3 T = 45 (10,126) links and 46 fails; WSE-2 T = 46 (10,581, exactly 49,152 B) links and 47 fails | Fixed |
| B5-5 | error | low | memcpy channel: ≈ 3.8 changed to ≈ 3.9 cycles per wavelet | Fixed |
| B5-6 | error | low | Lab 3 overhead changed to ≈ 5,520 B (≈ 5.4 KB) on WSE-3 and ≈ 3.8 KB on WSE-2, in the row, caption, figure labels and checker hint; grow values 5520 / 3920 kept | Fixed |
| B5-7 | unmarked | low | The fabric row now says the "SDK README gives" 750 × 994 and adds the other reading (750 × 994 allowed), tagged Unverified, with the size-caveat link | Fixed |
| B5-8 | error | low | #libs-row: Lab 5 stencil queues are now input 4–7 and output 4–7 (WSE-3) / 3 (WSE-2) | Fixed |
| B5-9 | tag | low | The TT-Metalium column header now carries a "Vendor / ISA docs" tag linking to Ch. 16 #tensix; 900,000 PEs and 44 GB are tagged Vendor on first use | Fixed |
