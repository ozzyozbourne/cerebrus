# Review 2: Appendix D (SDK example index), visuals + pedagogy/usability

Method: Playwright at 1100 and 390 px, light and dark, ◐ toggled. Drove every ladder chip followed by "Show in table", every
option of all four selects, 12 search terms, the empty state and Reset. Checked every "Where in the course" claim against the
headings and text of the target chapter (script `sec.py`). Screenshots are in `/home/user/cerebras-sdk/tmp/r2appDv/`.
Zero page or console errors and no page-level horizontal overflow at any size. Theme toggling recolours the badges live.
Every chapter link resolves to an existing file.

## Findings

**V1 (med) — Index table at 1100 px: the Coverage column is clipped.** `.table-wrap` is 821 px of content in a 792 px box, so the
last column shows "Covera" and "Explaine" until the reader scrolls inside the table (`crop-top.png`). Most desktop
readers will not notice that the table scrolls. The cause is `td.nm { white-space: nowrap }`: long names such as
`preconditioned-conjugate-gradient` and `sdklayout-03-ports-and-connections` force the first column to about 290 px, which squeezes
"What it teaches" and "Where" to about 150 px each. That makes every row 4–6 lines tall, and the full table is about 8,300 px long.
*Fix:* allow names to break at hyphens. Use `white-space: normal; overflow-wrap: anywhere`, or insert `<wbr>` after each `-`
in `esc(d[0])`. Also give the Coverage column `width: 1%; white-space: nowrap`. The table then fits at 792 px and rows get
shorter.

**P1 (med) — "Where in the course" says Chapter 15 covers three solvers that Chapter 15 never mentions.** `bicgstab`,
`preconditioned-conjugate-gradient` and `power-method` list "Ch 15 (same module structure as CG)", "Ch 15 (variant of CG)"
and "Ch 15 (same structure as CG)", and they appear under the Ch 15 filter. `grep -i "bicg|precondition|power" 15-lab-cg.html` finds
nothing. Their status is "Named", which by the legend means "mentioned only", and that is also false.
`single-tile-matvec` lists Ch 8 (as chapter tag 8 and in the Where text), but `08-systems.html` never mentions it or a matvec, and Ch 8 is the only
reason that chapter appears in the Course chapter dropdown (1 result). `sdklayout-05-gemv` says "compare Ch 14's layout.csl
version". Ch 14 does build SUMMA with layout.csl, but SUMMA is a GEMM, not a GEMV, so the comparison is loose.
*Fix:* for the three solvers, change status to `no` (or add one sentence to Ch 15 naming them, which is the better pedagogical
fix, since the ladder sends Ch 15 graduates to them). Drop the Ch 8 tag from `single-tile-matvec`. Reword the sdklayout-05 note
to "compare the layout.csl GEMV of Ch 12".

**P2 (med) — The headline stats disagree with the filter counts the reader gets.** The stat row says "48 / 55 both chips" and
"4 + 2 WSE-2 only / WSE-3 only". The Chip filter gives 50 (both), 5 (WSE-2 only) and 3 (WSE-3 only), because it also counts the 4
libraries, while the stats count only the 55 examples. A reader who checks the claim with the widget sees a mismatch. In the
same way, `residual` has chapter tag 12 but status "Not covered", so it shows under "Chapter 12" while also counting as one of the
"4 examples no chapter explains".
*Fix:* either label the stats "of 55 examples (libraries excluded)" and note in the hint that the Chip filter includes
libraries, or add the libraries to the stats (50/59, 5 + 3). Remove `12` from residual's chapter list, or mark it "Named"
and say "concept only" in the Where column.

**V2 (low) — Phone layout: the stacked cards have no field labels.** At 390 px (`ix-390-ch15.png`), each card shows the name,
description, a chip badge, a Where line, links and a coloured word ("Named"), all without labels. "Named" and "Labbed" in amber
or green with no heading are hard to read until the reader finds the legend at the bottom of a list that can be 59 cards
long. *Fix:* add `td::before { content: attr(data-l) }` with `data-l="Coverage"` and similar on each `td` in the ≤680 px
media query, or prefix the coverage cell with "Coverage:".

**V3 (low) — The legend sits below the table.** At desktop it is about 8,000 px below the badges it explains. *Fix:* move the
`<p class="legend">` above `#ix-count`, or into the hint line.

**P3 (low) — Ladder selection and the filters work against each other.** After "Show in table", the select boxes read "any" but
a hidden set restricts the rows. Changing Kind to "benchmark" after the Ch 6 ladder (5 items) still showed "5 of 59" because
the selection still applies, and only Reset clears it. The count text says "(ladder selection; Reset filters to clear)", which
helps, but there is no visible chip or close button for the selection. *Fix:* show a removable pill such as "Ladder: after
Ch 6 ✕" next to the count, or clear `only` whenever a select or the search changes.

**P4 (low) — The ladder has no rows for Ch 8, 9 and 16–18, and its items are not links.** Each ladder entry is plain `<code>`. To act on it
the reader must press "Show in table", then follow a chapter link. Neither the ladder nor the table gives the example's path in the
SDK tree or its README, which is the thing the reader actually needs to open. *Fix:* in the table name cell, add a muted
second line `examples/tutorials/<name>/` or `benchmarks/<name>/`. Make each ladder name scroll to and highlight its table row.
Optionally add a "Beyond: Ch 16–18" note saying no SDK example applies.

**P5 (low) — The Where text cites section names that differ from the real headings, and the links go only to the chapter.**
Examples: "Ch 3 · Is memory fast enough?" (the real heading is "Is memory fast enough to feed the math?"), "Ch 14 · Lab 4: 2-D GEMM with
SUMMA" (a chapter title, not a section), "Ch 11 · Aside" (the heading is "Aside: receive the whole stream with one
instruction") and "Ch 12 · Program 03/05". All the links go to the top of the chapter, so the reader has to hunt for the named
section. Every target heading checked does exist. *Fix:* link to section ids (`06-dsds.html#…`) and copy the
heading text exactly. The target chapters already carry ids on their h2s.

**V4 (low) — The search box at 1100 px.** The auto-fit grid puts Search alone on a second row, at about 190 px wide, so the
placeholder "e.g. switch, FIFO, allreduce" is truncated to "allredu". *Fix:* `.filters label:last-child { grid-column: 1 / -1 }` or
`span 2`.

**P6 (low) — Search uses US spelling only.** "colour" returns 0 results, while "color" works. British readers will expect
"colour", and the course text uses "colors". *Fix:* normalise `colour→color` (and `behaviour`) in the query before matching.

**P7 (low) — Missing visual.** For a learner new to the SDK, the most useful addition would be a small heat-map grid: chapters
across, topics down, cells coloured by the best coverage status. It would show at a glance which topics are labbed and which are
only named, for example that Linear algebra and Other algorithms are mostly Named or Not covered. Optional.

## What works
- The colours of the chip badges and the coverage words pass contrast in both themes (light: green #15803d on #dcf3e3; dark:
  #4ade80 on #15301f). Toggling ◐ recolours them correctly.
- All ladder chips produce the stated item count, and "Show in table" matches it (2/4/3/5/4/8/4/8/3/3/4/5).
- The empty state ("No example matches these filters.") renders cleanly. Reset restores 59/59.
- The import-fix callout is clear and ordered for action (copy, export, run), with the measured result.
