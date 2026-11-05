# Round-4 fix brief

You fix ONE page of the course at /home/user/cerebrus/course using the round-4 audit report for it.

Read first: REVIEW_BRIEF.md (layout, tags, SDK paths, rules), BUILD_BRIEF.md (page contract), CROSS_CHAPTER_NOTES.md
(ESPECIALLY items 30–38, the round-4 coordinator decisions — they override anything older), and your report
reviews/r4-<page>.md. Then grep ALL reviews/r4-*.md for items other auditors raised about YOUR page
(search for e.g. "Ch 5", "ch05", "Chapter 5", "05-tasks") and treat those as part of your list.

What to do:
- Fix every Error (E), Explanation problem (X) and Connecting gap (G) in your report, plus "still open" items and the
  cross-page items about your page, unless the fix would need hardware/unavailable sources or the report itself marks it
  optional; then skip it and say why. Bridging gaps is the priority: add the missing explanation, worked example,
  2-D/step-through figure (inline SVG, same style as the page), or link that connects idea A to idea B.
- Apply items 30–38 wherever they touch your page (rates, launch(), per-user tok/s, clock, hop cost, queue depth, tags,
  links). Add cross-chapter links and glossary links (item 38).
- Keep the page's voice, structure, CSS classes and widget style. Every new number carries a provenance tag. Keep
  changes proportionate: fix what is reported; don't rewrite sections that are fine.
- Labs 11–15: edit src/<page>.html, NEVER the generated top-level file; then run `python3 tools/build.py` from
  /home/user/cerebrus/course to regenerate (other fixers may run it too; that is fine). Only the Ch 14 fixer may edit
  comments in programs/06-summa/, and only the Ch 15 fixer comments in programs/07-cg/ (comment-only changes; then
  rerun build.py). No other program edits.
- Experiments (only if a fix needs a number): copy into /home/user/cerebras-sdk/tmp/r4fix-<page>/, `source
  /home/user/cerebras-sdk/env.sh`, never run cs_python under /tmp, traces off, delete afterwards. Keep runs few.
- Verify: load your page with Playwright (`file:///home/user/cerebrus/course/<page>.html`) at 1100 px, drive changed
  widgets, confirm zero console errors and that new in-page and cross-page anchors resolve.

Edit ONLY your page (or its src template), plus the program comments named above. Never edit CROSS_CHAPTER_NOTES,
other pages, assets/, or tools/. If another page needs a change, put it in your fix log under "For other pages".
No git commands that change state.

Write reviews/r4-<page>-fixlog.md: for each item ID, Fixed / Partly / Skipped + one line. Then "For other pages".
Final reply: ≤6 lines: counts fixed/partly/skipped, the most important changes, anything left open.
