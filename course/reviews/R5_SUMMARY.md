# Round-5 verification summary

Workflow `course-r5-verify` (brief: R5_BRIEF.md). For each page: an auditor, then an adversarial verifier, then a page
fixer. After that, cross-page fixers grouped by target page. 80 agents ran with 0 errors. Per-page logs are in
r5-<page>.md.

| Page | Found | Confirmed | High | Fixed | Auditor verdict (first sentence) |
|---|---|---|---|---|---|
| ch01 | 13 | 13 | 0 | 13 | Ch 1 is mostly sound |
| ch02 | 11 | 9 | 0 | 9 | Ch02 is mostly correct after round 4 |
| ch03 | 9 | 9 | 0 | 8 | Ch 3 is in good shape after round 4 |
| ch04 | 10 | 9 | 0 | 8 | Ch 4 is in good shape after round 4 |
| ch05 | 7 | 7 | 1 | 7 | Ch 5 is mostly correct |
| ch06 | 12 | 11 | 0 | 11 | Ch 6 holds up well after round 4 |
| ch07 | 6 | 6 | 0 | 6 | Ch 7 holds up well |
| ch08 | 7 | 6 | 0 | 6 | Ch08 is in good shape after round 4 |
| ch09 | 7 | 7 | 0 | 6 | Ch 9 is mostly correct after round 4 |
| ch10 | 11 | 11 | 0 | 11 | Chapter 10 mostly holds up |
| ch11 | 7 | 7 | 0 | 6 | Ch11 is mostly correct and well tagged after round 4 |
| ch12 | 5 | 5 | 0 | 3 | Ch12 is in good shape |
| ch13 | 6 | 5 | 0 | 5 | Ch13 is in good shape |
| ch14 | 9 | 9 | 0 | 8 | The Ch 14 page is in good shape |
| ch15 | 7 | 7 | 0 | 5 | Ch 15 is in good shape |
| ch16 | 8 | 8 | 1 | 8 | Ch 16 is mostly sound |
| ch17 | 8 | 8 | 0 | 8 | Ch 17 mostly holds up after round 4 |
| ch18 | 13 | 13 | 0 | 11 | Ch18 mostly holds up |
| appA | 7 | 7 | 0 | 7 | The page is mostly correct |
| appB | 9 | 8 | 0 | 8 | Appendix B is mostly correct after round 4 |
| appC | 6 | 6 | 0 | 6 | Appendix C is in good shape |
| appD | 10 | 10 | 1 | 8 | Appendix D is mostly correct |
| appE | 6 | 6 | 1 | 5 | Appendix E is mostly correct after round 4 |
| index | 9 | 9 | 0 | 7 | index.html is mostly correct |

Totals: 203 found. The verifier confirmed 196 and refuted 7. 4 were high severity. Page fixers fixed 180 on their own
pages, and the cross-page pass made 12 more fixes. A further 4 cross-page items needed no edit because the target
page's own fixer had already fixed them. The rest of the confirmed findings were edits to other pages; they were
handled by the cross-page pass or in the follow-ups below.

## Coordinator follow-ups (after the workflow)

- 06-dsds.html #index-offset: the `.index` unit now cites App E issue 5's simulator measurement (Measured).
- src/13-lab-stencil.html: `id="scaling-up"` added to the "Scaling up" heading (App D, D3).
- App C: a long SDK tag split so it wraps at 390 px (the only overflow found).
- scan_tags.py rerun: the generated rows in App E now carry the round-5 tags. The SC20 rows no longer say "via search
  extract", and the NVIDIA–Cerebras comparison row is Unverified.

## Still unverifiable (marked Unverified on the pages)

These items are still unconfirmed:
- the source of the 2,314 tok/s figure (reached through an interview quote);
- the WSE-3 clock (press estimate ~1.4 GHz);
- the WSE-3 fabric size;
- the Groq deal price;
- HC22's "wires under 1 mm" (slides unreachable, so it is tagged Press);
- the 32 B/cycle bank width;
- the register-file bandwidth estimate;
- what silicon does with an odd f32 `.index`.

## Final checks

- build.py and scan_tags.py rerun.
- Playwright on all 24 pages at 1100 and 390 px: 0 console errors, 0 overflow, 0 broken links or anchors.
- All 7 programs PASS on WSE-3: 7740, 7021, 6862, 11667, 7639, 36955 and 144987 cycles.
- All 7 programs PASS on WSE-2: 6826, 5424, 6152, 11288, 6278, 33656 and 129326 cycles.
