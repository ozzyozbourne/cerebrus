# Fix log · Appendix E (sources and unverified figures), round 2

Files edited: `course/tools/scan_tags.py`, `course/appendix-e-sources.html` (hand-written and generated parts), and the Errata table in `reports/Cerebras architecture course research.md`. No chapter, course.css or course.js was touched. No git operations.

## Scanner (`tools/scan_tags.py`)
- **Claims are built after the parse.** Each tag is now a placeholder in its block's text, so the claim is cut from the finished sentence. The rules: start at the sentence start, not after the last tag, which fixes claims that began with ")" (Ch 9 Maverick). Keep the clause after an earlier tag only when the sentence is longer than 240 characters. When the tag is the predicate ("… layout is [Unverified background]"), append the tag and the rest of the sentence. Tidy the punctuation left behind by tags.
- **Tables (R7).** A row counts as a header only if all its cells are `<th>`, so row-header tables no longer overwrite the column names. When the tag's cell holds fewer than three words besides tags, the claim is built from the row's other cells with their column names. This fixes "FP16 SIMD lanes · Source:" and the Ch 18 "Tag: [Vendor]" rows. For example, row 73 now reads `CS-4: "4,400 tok/s, up to 30× vs GPUs" · Metric: tok/s`.
- **Legends (R3, V3).** Two kinds of tag are skipped. The first is a run of four or more tags with only punctuation between them; these are the keys in Appendix A and Appendix B. The second is a bare class-name tag introduced by "labelled", "tagged" or "marked" in the same sentence: the Ch 9 "is labelled [Derived] … or [Unverified]" sentence, Ch 2's "All cells Vendor unless tagged" note and Ch 18's "every output is Derived". That is 16 tags in all. The stamp reports them, and the two phantom App A/B Unverified rows and the Ch 9 legend row are gone.
- **De-duplication**: by (page, class, label, claim).
- **Flag rule (R2).** A tag is flagged if it is Unverified, if its label contains "via" or "secondary" (any class), or if it is an Indep tag labelled as press ("Press", "The Register", "STH"). The page's intro paragraph states this rule. "Indep, AA via interview" is now flagged too, consistent with "via press release".
- **Why column (R2, V4).** Indep tags now get their own reasons:
  - Secondary: "described by a third party … no primary document".
  - Press: "a press write-up …; the primary slides … not reached".
  - via press release or interview: "an independent measurement, but reached through …".
  - The "SDK docs, via search extract" tag and the Unverified sub-labels (mapping, not independently measured, not re-read or re-checked, not in course sources) also have specific text.
- **Settle column (R1, V1).** The rules now match the claim and label first, then the section title, then the page's subject (Cerebras for Ch 2–15, NVIDIA for Ch 17, Tenstorrent for Ch 16).
  - Order: deal price, list price, MLPerf, Artificial Analysis, vendor projection ("up to N×"), model config/card, TPU, SambaNova, AMD, GroqCloud, LPX, NVFP4, cb16, OCP/IEEE formats, SDK/csdb/builtins, Tenstorrent, tok/s claims, Cerebras, NVIDIA.
  - `hbm` and `$` no longer trigger the NVIDIA rule, and `sm` needs word boundaries.
  - I spot-checked all 85 rows with `--list`. Results include: the TPU, SambaNova and AMD rows go to Google, the SN40L paper and amd.com; the AA row to its leaderboard; the deal price to a company filing; MLPerf to mlcommons.org; QuietBox's $9,999 to the seller's price list; and the Ch 1 Ethernet row to Cerebras.
- **Section links (P2).** Each row links to the nearest preceding element id in its chapter (h2/h3/figure/widget). Where there are 3 or more words before the first tag, the link also carries a text fragment (`#id:~:text=…`, hyphens encoded). All 85 links were checked in Chromium: every anchor exists, and 84 of 85 scroll. The one that does not, a Ch 17 "Three generations" row, scrolls 0 px because Chromium does not match its text fragment; the anchor still exists. The row also shows the section name.
- **Counts.** `via_by` per class is exported, so the "2nd-hand" column follows the class toggles (V8). Per-flagged-row data is no longer duplicated in the JSON.
- **New option `--list`** prints every flagged row with its link, why and settle text.

## Bibliography (R4, R6, P3, P4)
- **Titles.** `TITLE_OVERRIDES` gives readable "Publisher: headline (date)" titles to about 75 entries whose link text identified nothing: "abstract", "blog, Feb 2025", "May 2025", "May 2026", the DCD, ServeTheHome, Tom's Hardware, The Register and Futurum duplicates, "arXiv:2211.17192", "anandtech.com/show/16006", "Cerebras blog" ×2 and others. Headlines come from the URL slug and the citing sentence; dates are given only where the URL has one.
- **Misfiled entries.**
  - Leviathan et al. (2211.17192, speculative decoding) moved to the roofline/inference-methods group, renamed "Roofline, GPU programming and inference methods".
  - The AnandTech HC2020 live blog and the ISPD 2020 contest moved to "Cerebras hardware, systems and compiler talks".
  - Kowatek and STH `?p=79969` moved to Tenstorrent.
- **Fork link.** The `mgajewskiTT/tt-metal` link now points to `github.com/tenstorrent/tt-metal`, and the title says the note cited a contributor's fork.
- **LIB entries.** The bare "LIB" entry was dropped, and the intro defines `EX/` and `LIB/` (csl-libs inside the SDK image).
- **"Cited in" labels.** These are now readable ("note: WSE hardware"), sorted report → notes → chapters.
- **Layout.** Each topic group is a collapsed `<details>` with its count, and an "Open all groups" button opens them. A link to an entry (`#src-…`) opens its group and centres the entry. Every entry has a stable id.

## Page (hand-written parts)
- **Order and navigation (P1).** Added an "On this page" jump list. The new order is tags → how to check (with worked example) → widget and flagged list → open issues → bibliography (moved to the end and collapsed). At 1100 px the widget now starts about 2,000 px down instead of 11,400.
- **Worked example (missing visual).** It follows Ch 2's "1.1 GHz [Vendor (HC22)] … ≈ 7.5 PF [Derived]" sentence through all six steps:
  - the HC34 bibliography entry (linked, `#src-hc34`);
  - matching conditions: WSE-2 only, dense vs the 75 PF sparse figure;
  - the arithmetic (7.48 PF);
  - the finding that the "4 lanes" input is tagged Secondary in Ch 3 and sits in the flagged list, so the analyst match is not independent;
  - the simulator's ~2 f16 elements/cycle on WSE-2;
  - the errata history.
- **Step 6 (A5, P3)** no longer names CROSS_CHAPTER_NOTES or an item range. It points to "Open factual issues" and says that a measurement or primary document wins.
- **Internal references removed.** I dropped the reference to `reviews/phase3-backlog.md §5` and the "older numbering" sentence. The script's path is kept in one small-print line.
- **Widget colours.** The colours now use the same tokens as the `.tag` classes: Measured `--teal`, Indep `--green`, Derived `--muted`, and the rest unchanged. The invented 45% green tint is gone (V2 widget part).
- **Widget behaviour.**
  - Clicking a bar or a count-table row filters the list, smooth-scrolls to it (with scroll-margin under the top bar), and updates the `aria-live` readout, for example "24 of 85 rows for Ch 17 … (click its bar again to show all pages)" (V5).
  - Bars carry `aria-pressed`, and their labels include the flagged count.
- **Count table.** It is folded into `<details>` so the list sits right under the bars. "via sec." became "2nd-hand", moved after Total, recomputed from the class toggles, and explained in a hint (V8).
- **Empty state (V9).** A "No flagged figures match these filters" row with its own Clear button.
- **Phone layout (V6).** At ≤ 680 px every flagged row is a card with captions taken from `data-label`, and the §1 tag table stacks its third column under the second. Page overflow is 0 px at 390.
- **Two-line tags (V10).** `line-height: 1.25` on tags in the flagged table.
- **Hatched-page note (V11).** The note is now generated, and printed only when the navigation lists unwritten pages.

## Open issues
- **#2 (A2).** Added the cs_readelf man-page sentence, quoted exactly. I read the measured "equal mod 4 words" rule as the man page's "same bank": 16-bit banks, so 8 banks = 4 words. I then **tested the "same bank modulo 4" prediction** in a scratch copy of Program 01's timed kernel, N = 1,024, TSC, with placement checked by `cs_readelf --sym`:

  | Run | Start-bank gap 0 | 2 | 4 | Other offsets |
  |---|---|---|---|---|
  | f32 `@fmacs`, WSE-3 | 2,063 (PAD 0, 4) | — | 1,039 (PAD 2, 6) | 1,039 (PAD 1, 3) |
  | f32 `@fmacs`, WSE-2 | 2,062 (PAD 0, 4) | — | 1,038 (PAD 2, 6) | 1,038 (PAD 1, 3) |
  | f16 `@fmach`, WSE-2 | 526 | 526 | 270 | — |
  | f16 `@fmach`, WSE-3 | 272 | 272 | 272 | — |

  - f32: a 2-word offset (start banks 4 apart, "same bank modulo 4") costs nothing.
  - f16 on WSE-2: the mod-4 offset is the only fast case, the opposite of a conflict. The page gives a guess (4-wide reads of adjacent banks), tagged Derived.
  - The WSE-3 f16 run with PAD = 0 aborted with "could be a kernel stall" (host noise, CCN 17). The gap-0 case is covered by PAD = 8.
  - "Would settle it" now asks for a destination-offset test and traces of the f16 runs.
  - The scratch directory `/home/user/cerebras-sdk/tmp/fix2-appE/` was deleted.
- **#4 (A3).** The issue now says no explanation of the ~90-cycle floor has been proposed. It also notes that Ch 12's clock-start remark explains the per-PE step, not the floor.
- **#5 (A4).** The issue quotes the cslc error ("'async' requires at least one fabric or DSR operand", tagged Measured, cslc). The proposed experiment now uses two async `@fmovs` from two input queues on different microthreads, against the same receives run back to back.
- **#6 (A6).** Names `tutorials/sdklayout-05-gemv/gemv.csl` (dense GEMV, f32, `.index = 2 * idx`) and `benchmarks/gemv-checkerboard-pattern/pe.csl` (`@fmach`, f16, `.index = idx`). Both lines were checked in the SDK.
- **All issues** now link to chapter section anchors (`#bank-model`, `#kernel-time`, `#collisions`, `#op-speed`, `#numbers-say`, `#latency`, `#hop-cost`, `#microthreads`, `#index-offset`, `#builtins`).

## Report Errata
- **Decode row (A1)** rewritten from CCN 25. It separates the ~600k tok/s aggregate from the ~1/80 single-user bound (~7,500 at headline bandwidth, ~2,000 at the measured f16 rate, up to ~4,000 for an undemonstrated 8-wide kernel). It says the measured 2,314 tok/s is ~30% of the headline single-user bound, and that the limit is "per-region SRAM reads plus latency and communication". Citation: "CCN 6, 25; course Ch 9, 18".
- **Bank row (R5).** Now cites "Appendix E open issues 1 and 2 (`#iss-bank`, `#iss-clash`)" and adds the man-page clause and the simulator result. The intro link points to `#open`.

## Not fixed here (other owners)
- **A8.** The two "Peer-reviewed" tags in `18-comparison.html` are already class `indep` on disk (Ch 18's fixer). The regenerated counts reflect this.
- **V7.** Tag contrast in light mode (Vendor 4.45:1) is in course.css, which belongs to the coordinator. Measured now uses teal.

## Validation
- **Playwright.** I tested at 1100 and 390 px, in light and dark, and toggled ◐ in each, with these results:
  - 0 page or console errors, and 0 px horizontal overflow. Before the fix, a hidden empty-state button caused 4 px of overflow at 390; it is now fixed.
  - Every control was driven: all 7 chips (with Vendor and Indep off, the 2nd-hand total is 0), all three sorts, the bar click (scrolls about 2,000 px, 24 Ch 17 rows), Enter on a focused bar (clears it), the count-table row click (22 Ch 18 rows), search for "NVLink" (5) and "zzzz" (empty row shown, and its Clear button works), and Clear filters.
  - The worked-example link opens the bibliography group and highlights the entry, and "Open all groups" works.
- **Screenshots.** I inspected the widget, the flagged cards at 390, the worked example, the bibliography and the toggled theme.
- **Regeneration.** Regenerated last, at **2026-11-04 02:03 UTC**: 22 pages, 1,364 tags (+16 legend tags skipped), 85 flagged (37 Unverified, 48 second-hand), 298 sources. `--check` immediately afterwards gives the same numbers as the page stamp. Other fixers were editing chapters at the same time, so re-run `python3 course/tools/scan_tags.py` after their last edit.

**Coordinator correction (cleanup):** `/home/user/cerebras-sdk/tmp/fix2-appE/` was deleted later than stated above, just before the final regeneration; all scratch is gone.
