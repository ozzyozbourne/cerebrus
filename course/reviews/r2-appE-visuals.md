# Review r2 — Appendix E (sources), visuals + pedagogy/usability

Method: Playwright at 1100 and 390 px, light and dark, ◐ toggle; drove every chip, all three sorts, search (hit and no-hit), bar click/re-click, Enter on a focused bar, count-table row click, Clear. Measured element overflow, section offsets and tag contrast; read every row of the generated flagged list (71 rows). `scan_tags.py --check` matches the page (not stale). 0 page or console errors, 0 px page-level horizontal overflow at either width. Readout counts agree with the visible rows in every state tested (e.g. Ch 17 → 23 = 13 Unv + 10 via-secondary).

## High

**V1 (high) — §3 flagged list, "What would settle it" column: wrong advice on at least 13 of 71 rows.** The keyword rules in `tools/scan_tags.py` (lines ~205–212) fire on words, not on what the claim is about. Examples: row 2 (Ch 1, Cerebras "~23 GB/s per PE (21 PB/s ÷ 900,000)") → "NVIDIA's own datasheet…"; row 12 (Ch 9, HC2024 "fraction of a chip…") → NVIDIA datasheet; row 13 (Ch 9, Artificial Analysis 2,522 vs 1,038 tok/s) → NVIDIA datasheet; rows 55, 57, 58 (Ch 18 TPU Ironwood, SambaNova SN40L, AMD MI355X) → NVIDIA datasheet; row 56 (Groq GroqCloud) → "NVIDIA's LPX product page"; row 37 (the ~$20B Groq deal price) → "The benchmark organisation's results page"; row 60 (MLPerf for Cerebras/Tenstorrent) → "tt-isa-documentation…". The page sells this list as the place to find "what would settle it", so wrong answers mislead.
Fix: order rules so the page/claim subject wins (Cerebras/WSE/CS-n first, then TPU/SambaNova/AMD/Groq/MLPerf/Artificial Analysis/price rules), remove `hbm`, `\$`, `sm\b` as triggers, and add rules: TPU → Google Cloud TPU docs; SambaNova → SN40L paper/datasheet; AMD → amd.com MI355X page; Artificial Analysis → its public leaderboard; deal price → a company filing or statement; MLPerf → mlcommons.org results. Re-generate and spot-check every row.

**V2 (high) — §1 tag table and the widget legend: Measured and Indep/Secondary tags look identical.** `course.css` gives `.tag.indep` and `.tag.measured` the same colours (`--green` on `--green-soft`); computed values are identical in both themes. On the page whose first table says "the tag's colour gives the class", the strongest class (Measured) and a second-hand class (Secondary) cannot be told apart (visible side by side in "Open factual issues" #1/#2: "Secondary" next to "Measured, TSC"). The widget then invents a third green (45 % tint) for Indep, so the chart legend matches no tag in the course. "Vendor via secondary" also renders exactly like Vendor.
Fix (course.css, coordinator): give `.tag.indep` its own hue (e.g. teal) or an outlined style, and reuse that hue for `.c-indep`; optionally a dashed border for any label containing "via" so second-hand vendor figures are visible inline.

## Medium

**V3 (med) — §3 flagged list: non-claims and mangled claims.** Rows 62 and 70 have claim "[Measured] [Derived]" (the tag legends of App A/B, flagged as Unverified); row 10 is Ch 9's legend sentence ("Everything below… is labelled [Derived] … or"); row 7 is "FP16 SIMD lanes · Source: " (empty); row 13 begins with ")"; row 15 begins "Tom's Hardware; ServeTheHome)." and duplicates row 16; row 34 ends mid-sentence ("…NVSwitch trays layout is"); rows 18 and 59 contain "Tag: [Vendor]" while the row's tag is Unverified, with no explanation. That is ~10 % noise in a list meant to be a to-do list.
Fix: in the scanner, skip tags inside legend/`.objectives`/key paragraphs (or a `data-noscan` attribute), drop claims shorter than ~4 words or made only of tag text, trim leading punctuation to the sentence start, de-duplicate by (page, tag position), and strip the "Tag: […]" column text from table-row claims.

**V4 (med) — §3 "Why it is not verified" says "The vendor number reached the course through secondary reporting" for all Indep-class "Secondary" rows** (rows 3–7, 55–58, 69), which are third-party descriptions (connector design, SIMD width, TPU/SambaNova specs), not vendor numbers. Fix: separate "why" text for `cls=indep`: "Described by a third party; no primary document was reached."

**P1 (med) — Page order buries the useful part.** Offsets at 1100 px: §2 bibliography runs from 2,058 to 11,039 px (299 entries); the widget starts at 11,438 and the flagged table at 13,315; the page is 26,500 px tall (38,450 at 390 px). There is no in-page table of contents. A learner arriving from a chapter's "Unverified" tag must scroll past nine screens of links to reach the list.
Fix: add a jump list under the objectives (Tags · Flagged figures · Open issues · Bibliography), move §2 to the end, and wrap each bibliography group in `<details>` (open the NVIDIA/Groq and Cerebras groups by default).

**P2 (med) — Flagged claims cannot be found in their chapter.** The Page column links to the top of the chapter only; Ch 17 has 59 tags and Ch 18 142. Claims are sentence fragments, so the reader needs context.
Fix: emit a text-fragment link per row (`17-gpu.html#:~:text=<first 6–8 words>`), or have the scanner add an `id` to each flagged tag and link to it.

**V5 (med) — Clicking a bar gives no visible result.** The filtered list starts ~1,900 px below the bars at 1100 px (the 23-row count table sits between them); only the small readout changes. Fix: after `pick()`, `scrollIntoView` the first visible flagged row (or the table head), or put the flagged table directly under the bars and fold the count table into `<details>`.

**V6 (med) — Phone (390 px): flagged table is clipped.** The table is 697 px wide in a 356 px box; the Tag column is cut at the right edge ("Vendor, via forum" half visible) and Why/Settle are off-screen, while each row is ~200 px tall because of the hidden columns. The §1 tag table also overflows (386 in 356) and cuts the "weight it bears" column mid-word.
Fix: at ≤680 px render each flagged row as a card (`display:block` per `td`, with `data-label` captions), and drop `min-width` on columns 4–5; for the §1 table, stack the third column under the second.

**V7 (med) — Tag contrast below WCAG AA in light mode** (11 px bold text): Measured/Indep 4.29:1, Vendor 4.45:1. Dark mode is fine (5.6–8.2). Fix (course.css): darken `--green` text in tags to ~#116932 and `--amber` to ~#9a4508, or bump tag size to 12 px.

## Low

**P3 (low) — Internal build files presented to learners.** Step 6 of "How to check a figure" sends readers to `reviews/CROSS_CHAPTER_NOTES.md` "items 1–24" (the file now has 25 items, and it is not linked or published); "Open issues" cites `reviews/phase3-backlog.md §5` and says "the review files … use the older numbering"; bibliography "cited in" labels are internal file stems (`wse_hardware`, `gpu_and_comparison`). Fix: say "the course's cross-chapter corrections list (in the source repository, reviews/CROSS_CHAPTER_NOTES.md)" without an item range; replace note stems with readable names ("research note: WSE hardware") and add one sentence saying the notes live in `research_notes/`; drop the old-numbering sentence.

**P4 (low) — 55 of 214 web entries have labels that identify nothing**: "abstract", "blog, Feb 2025", "May 2025", "May 2026", "DCD" ×3, "ServeTheHome" ×3, "The Register" ×2 etc. (scraped link text). Fix: fall back to "Publisher: page title" (or the URL path) when the anchor text is under ~15 characters or repeats in the group.

**V8 (low) — "via sec." column ignores the chips.** With Vendor and Indep toggled off it still shows 39 in the totals row, and it sits between Unverified and Total although it is a subset, not an addend. Fix: add one sentence to the hint ("via sec. is a subset of Vendor/Indep, not added to Total") and hide or recompute it when those chips are off.

**V9 (low) — No empty state.** Search "zzz" leaves a header-only table; only the readout says "0 of 71". Fix: insert a single "No flagged figures match" row.

**V10 (low) — Two-line tags in the flagged table are cramped.** `.flag-table .tag { white-space: normal }` with the base `line-height: 1` makes "Vendor, via / forum" lines touch. Fix: add `line-height: 1.25` to that rule.

**V11 (low) — Stale hint.** "Pages listed in the navigation but not yet written appear hatched" — none are now. Keep the rule but say "(none at present)", or show the sentence only when `missing` pages exist.

Missing visual that would help most: a small worked example in §1, with one real sentence from a chapter, its tag, and the bibliography entry and check step it maps to, so the six-step procedure is shown once and not only described.
