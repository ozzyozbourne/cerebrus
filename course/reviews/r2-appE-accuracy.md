# Review 2 · Appendix E (sources) · accuracy + reference

Scope: `appendix-e-sources.html`, `tools/scan_tags.py`, the Errata table in `reports/Cerebras architecture course research.md`.

## How I checked it
- I ran `python3 course/tools/scan_tags.py --check` (rc 0): 22 pages, **1289** tags, 71 flagged, 299 sources.
- I compared the scanner against a plain regex count of `class="tag …"` on every page, outside script, style and svg. The counts match on all 22 pages.
- I compared a fresh scan with the JSON embedded in the page. The flagged list is identical, row for row. Only the Ch 13 counts differ (see A7).
- I regenerated the page in a scratch copy (`scratchpad/regen`). It works from any working directory and rewrites only the two marked regions. Run again with no chapter edits, it changes only the date.
- I fetched 14 cited arXiv IDs. All exist and their titles match. Rocki et al. SC20 is 2010.03660, and Prabhakar et al. SN40L is 2405.07518.
- I checked the `dsd_ops.csl` mapping for scale/norm inside the SIF, and the `cs_readelf` man-page quotes. Both are correct.
- The numbers in open issues 1, 3 and 7 match Ch 6, 11 and 13. Each row of the Errata table quotes a claim that really appears in the report body.

## Findings

**A1 · high · Report Errata, row "Decode on Cerebras framed by SRAM bandwidth".**
- What is wrong: the row says decode "is **not** memory-bandwidth bound … the limit is pipeline latency and communication". It cites only CCN 6, and CCN 25 replaces that part of CCN 6.
- Evidence: per CCN 25, ~600k tok/s is the aggregate over all users. The single-user bound is ~1/80 of that: ~7,500 tok/s at headline bandwidth, ~2,000 at the measured f16 matvec rate. The measured 2,314 tok/s is about 30% of the headline bound. CCN 25 says to write "per-region SRAM reads plus latency/communication". The Errata says "the course wins", yet this row states the claim the course has since withdrawn.
- Fix: rewrite the row from CCN 25 and cite "CCN 6, 25".

**R1 · med · `scan_tags.py` `SETTLE_RULES`, "What would settle it" column.**
- What is wrong: the NVIDIA rule comes before the TPU/SambaNova/AMD rule. Its pattern contains `hbm`, `cuda`, `b200` and others, so any claim that mentions HBM matches it first.
- Evidence: Ch 18's TPU (Ironwood), SambaNova SN40L and AMD MI355X rows get "NVIDIA's own datasheet, architecture whitepaper…". So does Ch 9's Artificial Analysis Cerebras-vs-DGX-B200 row.
- Fix: move the `other` rule above the NVIDIA rule, and put word boundaries around `hbm`.

**R2 · med · `scan_tags.py` `reason()` and `VIA_RE`, flagged list.**
- What is wrong, case 1: 11 flagged rows are class `indep`. The reason text for all of them says "The vendor number reached the course through …". Ten have labels "Secondary", "Secondary source" or "Secondary sources" (Ch 2, 3, 18, App A). Their text is a third-party description, not a vendor number, so the reason is wrong. The eleventh, "Indep, Artificial Analysis via press release", is a third-party measurement, so "vendor number" is wrong for it too.
- What is wrong, case 2: flagging is uneven. Indep "Secondary" tags are flagged, but `indep` tags labelled "Press", "Press, The Register" and "The Register" (4 tags) are not.
- Fix: give `indep` tags their own reason ("third-party summary, not a primary document"). Add `press|the register` to the rule, or document in the page's intro paragraph that these labels are left out on purpose.

**R3 · med · `scan_tags.py` counts legend tags as claims.**
- What is wrong: the script skips `index.html` and Appendix E because their tags are a legend. It does not skip the legend sentences in other pages: `appendix-a-glossary.html:66` and `appendix-b-cuda-to-csl.html:54` each hold a row of 6 tags.
- Evidence: this adds 12 tags that are not claims. It also adds 2 Unverified rows whose claim text is just "[Measured] [Derived]", so the stated 32 Unverified is really 30.
- Fix: skip any block with ≥4 tags and no other text, or mark legends with `data-legend` and skip those.

**A2 · med · Open issue 2, "Unknown" and "Would settle it".**
- What is wrong: the issue calls the clash rule undocumented and asks for "a vendor statement of the rule". Part of one exists. The `cs_readelf` man page, which issue 1 already quotes, says: "Bank conflicts where concurrent reads and writes target the same bank **or the same bank modulo 4** may result in cycle delays." I checked this with `cs_readelf --help`.
- Evidence: with bank = bits [3:1], "same bank mod 4" means byte addresses equal mod 8, which is 2 words. The measured rule is "equal mod 4 words". So the man page predicts conflicts at 2-word offsets as well. That is a direct, testable prediction.
- Fix: quote the man page here. Change "why mod 4 words when there are 8 banks" to the man-page rule, and add "test 2-word offsets" to "Would settle it".

**A3 · med · Open issue 4, "Unknown".**
- What is wrong: the issue says "Each PE's clock starts one hop later" fits the numbers of the WSE-2 floor. In `12-lab-neighbours.html:289` that Derived claim explains something else: the per-PE "own clock" step (7.2 / 5.0 cycles) being one router hop less than the CE-forwarded hop. The same paragraph mentions the ~90-cycle floor separately and offers no cause for it.
- Fix: say no explanation of the floor is proposed. Drop the clock-start sentence, or say what it actually explains.

**A4 · med · Open issue 5, "Would settle it".**
- What is wrong: the issue proposes timing "two async `@fadds` on different microthreads". With memory-only operands this does not compile.
- Evidence: `ch03-fixlog.md` records that cslc rejects it: "'async' requires at least one fabric or DSR operand". The DSR variant stalled. That is the "attempt … stalled" the issue mentions.
- Fix: specify at least one fabric or FIFO operand per op. For example, use two receives from two colors into memory, compared with the same two run back to back. Cite the compile error.

**R4 · med · Bibliography titles and grouping.**
- What is wrong: the script uses the link text as the title, so many entries are useless out of context:
  - "abstract" (the aminer CU-Poker paper)
  - "blog, Feb 2025", "May 2025", "May 2026"
  - "Cerebras blog" (2 entries)
  - "arXiv:2211.17192" and "anandtech.com/show/16006"
  - "DCD" (3 entries), "ServeTheHome" (4), "Tom's Hardware" (2), "The Register" (2), "Futurum" (2)
- What is wrong, misfiled entries:
  - arXiv 2211.17192 is Leviathan et al., speculative decoding, but it is listed under "Academic papers on wafer-scale computing".
  - The AnandTech Hot Chips 2020 Cerebras live blog and the ISPD 2020 placement contest fell through to the catch-all "Roofline" group.
  - Kowatek and `servethehome.com/?p=79969` are both cited by `tenstorrent.md` but are filed under Cerebras hardware.
- What is wrong, attribution: "tt-metal README tables" points to a personal fork (`github.com/mgajewskiTT/tt-metal`), not `tenstorrent/tt-metal`.
- Fix: add a `TITLE_OVERRIDES` dict (URL → "Publisher: headline (date)") and more `TOPIC_OVERRIDES` entries. Point the README entry at the upstream repo, or label it as a fork.

**A5 · low · "How to check a figure", step 6.** The text says "CROSS_CHAPTER_NOTES.md, items 1–24". There are 25 items. Fix: change to 1–25.

**A6 · low · Open issue 6, "Known".**
- What is wrong: the issue says "the SDK's sparse examples pass `.index = 2*idx`". The only such use is `tutorials/sdklayout-05-gemv/gemv.csl:26`, which is a dense GEMV; Ch 6 names it correctly.
- Extra evidence: `benchmarks/gemv-checkerboard-pattern/pe.csl:83` passes `.index = idx` to `@fmach` on f16. That supports 16-bit units.
- Fix: name both files.

**A7 · low · Generated stamp is stale.** The page says 1,285 tags; the scan now finds 1,289. The difference is all Ch 13: Measured went from 19 to 22 and Derived from 5 to 6, after Ch 13 was edited. The flagged list is unaffected. Fix: re-run the script as the coordinator's last step.

**A8 · low · Tag class misuse picked up by the counts (`18-comparison.html:271, 346`).** Two "Peer-reviewed" tags use class `measured`. Appendix E defines Measured as "run during this course's build", so these inflate Ch 18's Measured count. Ch 13:471 handles the same kind of source correctly with `indep`. Fix: change the class in Ch 18 to `indep`.

**R5 · low · Report Errata, bank row.** It cites "Appendix E §1". §1 of Appendix E is the tag table; the bank question is open issue 1 (`#iss-bank`). Fix: change the reference.

**R6 · low · Local SDK bibliography.**
- What is wrong: it lists bare entries "LIB", "LIB/collectives_2d", "LIB/runtime" and "LIB/target". The page explains only the `EX/` prefix, and the bare "LIB" entry is noise.
- Fix: define LIB (csl-libs inside the SIF) in the intro paragraph and drop the bare entry.

**R7 · low · Claim heuristic in tables.**
- What is wrong, case 1: in Ch 3 ("What changed per PE") one flagged row reads only "FP16 SIMD lanes · Source:" because the tag sits alone in a Source column.
- What is wrong, case 2: `is_header_row` is set by any `<th>`, so a table with row headers overwrites `self.header` on every row and attaches the wrong column names.
- Fix: when the claim is empty, use the text of the other cells in the row. Treat a row as a header only if all its cells are `th`.

## Summary
- **Counts:** 1 high, 8 medium, 7 low (16 findings).
- **Scanner:** it finds every static tag. Its flagged list matches the chapters exactly, and regeneration works.
- **Script bugs:** the settle and reason rules give wrong text for 15 rows, and legend tags add 12 phantom tags, 2 of them phantom Unverified rows.
- **Open issues:** issue 2 misses the man page's "same bank modulo 4" rule. Issue 4 borrows an explanation from Ch 12 that is about a different effect. Issue 5's proposed experiment does not compile.
- **Bibliography and Errata:** every arXiv entry checked is real, but about 20 titles are bare link text and 5 entries are misfiled. The report's Errata row on decode predates CCN 25.
