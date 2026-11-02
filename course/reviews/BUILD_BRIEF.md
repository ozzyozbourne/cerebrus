# Build brief — new chapters and appendices (phase 4)

Course: /home/user/cerebrus/course, 18 chapters + appendices A–E (see assets/course.js CHAPTERS/APPENDICES — nav, top bar
and pager are automatic; do not edit course.js/course.css unless strictly necessary and backward-compatible, and say so).
The course was just renumbered: old 9→10, 10→11, 11→12, 12→13, 13→16, 14→17, 15→18. Review/fix-log files in reviews/
use the OLD numbers. New: 9 From model to tokens, 14 Lab 4 GEMM/SUMMA, 15 Lab 5 CG, appendices A–E.
Decision record: reviews/PHASE3_SUMMARY.md and reviews/phase3-*.md.

## Page contract
- Copy the skeleton of an existing chapter (e.g. 13-lab-stencil.html or 03-processing-element.html): same <head>, kicker
  ("Chapter N · Part … " / "Appendix X"), objectives, sections, "Check yourself" quiz (chapters), course.js at the end.
- Use course.css components (callout, stat-row, figure, widget, tables, tags) and course.js helpers ($, el, cssVar, cssValue).
  Colours in SVG via cssVar("--x") or CSS classes so both themes and the ◐ toggle work.
- Every number gets a provenance tag: .tag.vendor|indep|analyst|sdk|measured|derived|unv (see REVIEW_BRIEF.md). Do not
  invent numbers. Measured = you ran it in the SDK simulator this session (say chip, size). Cite sources inline.
- Reuse established facts consistently: reviews/CROSS_CHAPTER_NOTES.md (items 1–24) is canonical.
- Mobile: no horizontal page overflow at 390 px (wide SVG/widgets scroll inside figure/.widget).
- Lab chapters are generated: write course/src/NN-*.html with {{code:programs/…}} and {{out:programs/…}} placeholders,
  then run `python3 course/tools/build.py` (it rebuilds all labs; don't hand-edit generated lab HTML).

## Programs
- New programs live in course/programs/0N-name/ with layout.csl, pe_program.csl (or module files), run.py, commands.sh
  (honours $ARCH, default wse3), expected_output.txt (from a real run; last line "[NNNN simulated cycles, WSE-3]" style as
  the others). run_all.sh globs 0*/, so it must PASS (print SUCCESS!) on ARCH=wse3 and ARCH=wse2, or document clearly if
  a chip is unsupported and make commands.sh exit 0 with a SKIP message (prefer supporting both).
- SDK: `source /home/user/cerebras-sdk/env.sh`; see .claude/skills/cerebras-sdk/SKILL.md. Never run cs_python under /tmp.
  Scratch under /home/user/cerebras-sdk/tmp/<your-task>/ and delete it at the end. Clean sim outputs from program dirs.
- Kernel timing: on-tile TSC (<time> module), same-PE start/end (notes 17, 19). Whole-run cycles are noisy (+1–4%).
- Respect licensing: SDK examples may be adapted with attribution in a header comment ("Adapted from Cerebras SDK 2.10.1
  benchmarks/…"); keep the course's own code style and comments.

## Validation (required)
Playwright (require('playwright'); chromium.launch()) at 1100 and 390 px, light and dark, plus toggling ◐: zero page and
console errors, no horizontal overflow, drive every widget control, inspect screenshots. Scratch in
/tmp/claude-0/-home-user-cerebrus/dad2686f-4919-59f3-a15a-5e1f2815e9e2/scratchpad/<task>/ and delete after.
Do not commit. Write reviews/build-<task>.md: what you built, numbers measured, sources, open issues. Final reply concise.
