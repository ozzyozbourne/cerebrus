# Review brief, round 2 (new pages)

Read REVIEW_BRIEF.md (rules, file layout, tags, SDK paths) and BUILD_BRIEF.md (page contract). The course now has 18
chapters + appendices A–E (see assets/course.js). Old review files chNN-* use the OLD numbering (9→10, 10→11, 11→12,
12→13, 13→16, 14→17, 15→18). Canonical shared facts: CROSS_CHAPTER_NOTES.md items 1–25. Each page's builder wrote
reviews/build-*.md — read it, but verify rather than trust it.

Pages under review: 09-model-to-tokens.html, 14-lab-gemm.html (src/14-lab-gemm.html, programs/06-summa),
15-lab-cg.html (src/15-lab-cg.html, programs/07-cg), appendix-a-glossary, appendix-b-cuda-to-csl, appendix-c-measuring,
appendix-d-sdk-index, appendix-e-sources.

## Angles
- accuracy: every factual and numeric claim. Check against SDK files, the programs' real output, research notes,
  CROSS_CHAPTER_NOTES and other chapters (consistency), and the web where useful. Check provenance tags are right
  (e.g. "Measured" only if really measured). Re-run a program or a small experiment in your own scratch dir when a key
  number looks doubtful (copy the program; never run inside course/programs/).
- pedagogy: does a strong learner new to Cerebras follow it? Order, prerequisites, jumps, undefined terms, whether the
  exercises/quiz test the right things and their answers are right, links to earlier chapters.
- visuals: open the page in Playwright at 1100 and 390 px, light and dark, toggle ◐; drive every widget control; inspect
  screenshots. Report: errors, clipped/overlapping text, wrong or misleading drawings, unreadable contrast, widgets whose
  output disagrees with the text, missing visuals that would help most.
- depth: what an expert would find missing or shallow; important caveats; whether measurements support the claims made.
- (appendices) reference: completeness and correctness of the reference content (terms, tables, links resolve to the right
  section, index entries match the SDK examples), plus usability of search/filter widgets.

## Output
Write reviews/r2-<page>-<angle>.md (page = ch09, ch14, ch15, appA … appE). Numbered findings with IDs (A1…, P1…, V1…,
D1…, R1…), each: severity (high/med/low), location (section/heading or line), what is wrong, evidence, concrete fix.
Most severe first. Be specific; no padding; under ~1,200 words. Read-only except your report and scratch dirs. Final
reply: 5-line summary with counts by severity.
