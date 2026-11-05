# Round-4 fix log: Appendix E (sources and unverified figures), page-id appE

File edited: `appendix-e-sources.html` only. Hand-written parts edited by hand; generated parts rebuilt with `python3 tools/scan_tags.py` as the last step (22 pages, 1,792 tags, 137 flagged, 302 sources at the time of the run; Ch 14's fixes were already on disk). Verified with Playwright (Chromium) at 1100 px and 390 px. There were zero console errors and no horizontal overflow. Every relative href and anchor on the page resolves (checked by script against the target files). The tag chart's chips, search, page filter and clear all work.

Experiments: Program 01 `timed/` harness, N = 1,024, in `/home/user/cerebras-sdk/tmp/r4fix-appE/` (deleted afterwards). Start gaps were read with `cs_readelf --sym`, because cslc places each array on a 4-byte boundary.
- `@fadds` at 12 B: WSE-2 1,038, WSE-3 527.
- `@fmach` at 12 B: WSE-2 526, WSE-3 272.
- `@fmach` at PAD = 1/3/5/7 f16 on WSE-2: gaps 4/8/12/0 B, 526/270/526/526 cycles. WSE-3 at 4/8/12 B: 272 each.
- Odd-bank offsets (2/6/10/14 B) cannot be reached with separate arrays.

## Items from r4-appE

| ID | Status | Note |
|---|---|---|
| E1 | Fixed | Worked example steps 4–6 rewritten. The Ch 2 quote is updated to the current wording ("HC22 dense figure", CCN 36). The Vendor numbers back-solve to 4.0 lanes. WSE-2 `@fmach` reaches ≈4/cycle when well placed (270), so the "~2/cycle, half the lanes" reading is called a placement artefact. |
| E2 | Fixed (App E part) | The "What this means" box says "WSE-2 f16 = 2/cycle" is a layout, not a rate, and links Ch 3/6/11. CCN 30 already retires the rate; the other chapters were fixed by their own fixers. |
| E3 | Fixed | Issues 2 and 3 merged into one Measured issue, "Operand placement sets DSD op rates", per CCN 30. It links `06-dsds.html#banks`, keeps `#iss-clash`, and keeps `#iss-fadds` as an inner anchor. Lab 3's `u[i]`/`u[i+2]` is the worked instance. The objectives now say six issues, renumbered. |
| E4 | Fixed | Issue 6 (was 7): scale is ldexp f·2^s with an i16 exponent [SDK, math.csl, checked in the SIF]. norm returns the significand in [1, 2) [Derived from SDK code]. Only the edge cases stay Unknown. |
| E5 | Fixed (by Ch 18) | Verified: no `measured` class remains on the peer-reviewed MD and SC20 rows in Ch 18. |
| E6 | Fixed | The Vendor row is now "maker of the product, model or library", with Meta/Google/AMD/Groq named. |
| E7 | Fixed | "Two limits" now says "during the build", and that cerebras.ai's 405B post and the Cerebras training docs were later fetched directly. |
| E8 | Fixed (by Ch 1) | Ch 1's legend now reads "marked …" and the scanner counts legend = 7. No tools change needed. |
| X1 | Skipped | Cutting a multi-tag table cell at the tagged clause, and merging duplicate rows, need changes to `tools/scan_tags.py`, which I may not edit. See "For other pages". |
| X2 | Fixed | The 170-word paragraph is replaced by a 6-row table: op × chip by 0/4/8/12 B, with the `@fadds` rows and the new 12 B cells. |
| X3 | Fixed | Glossary links on first use: bank (issue 1), TSC (issue 2), microthread, DSR and input queue (issue 4). Also linked: bank-clash glossary entry, and Chapter mentions per CCN 38. |
| G1 | Fixed | A "What this means" box (callout key) with 3 points under the merged issue 2. |
| G2 | Fixed | New hand-written section `#used-by` after the generated list, with 6 rows: WSE-2 lanes → 7.5 PF; WSE-3 clock → per-second bounds; 8-wide f16 → Ch 9 ceiling; layer-per-region → 1/80 and spec-decode c; LPX 256/rack → 128 GB / 40 PB/s; H100 32 banks → 31 TB/s. Linked from the TOC. |
| G3 | Fixed | Harness and command lines added to issue 2 (fmacs/fmach/fadds, plus the readelf step), issue 5 (`.index` via `@fmovs` with `.wavelet_index_offset`) and issue 4 (no ready harness; start points named). Step 5 of "How to check" names the harness. |
| G4 | Fixed (by Ch 15) / n/a | Ch 15 now tags SC20 as Indep, so the stale Unverified row is gone after the rescan. 2010.03660 is already in the bibliography (`#src-fa9b63aa`). |
| G5 | Fixed | Via E6. |
| Flagged-table rows (78/79, 40, 42, 46, 25/74, 21/54/66, 49, …) | Partly | The list is generated from chapter tags, so retags happen in the chapters. After the rescan, cb16 and the CS-4 rows follow their pages' new tags. Ch 17's TMEM (row "Unverified background, Colfax") and NVL72 trays rows are still Unverified in Ch 17. |

## Cross-page items aimed at App E

| Source | Status | Note |
|---|---|---|
| r4-ch15 fixlog: stale SC20 row | Fixed | Gone after the rescan. |
| r4-ch16 fixlog: DeepSeek-R1 → TT-Deploy | Fixed | Ch 16 now cites TT-Deploy under a Vendor tag, so the row no longer appears in the flagged list. |
| r4-ch17 fixlog: retags/additions | Partly | The new Ch 17 tags (Rubin BF16 flopper.io, B300, LPX full production, AA ~3,400, 70–80 %) appear in the generated list automatically. Retags that Ch 17 did not make on its own page (TMEM, NVL72 layout) cannot be made from App E. |
| r4-ch18 fixlog: E5, CS-4 row | Fixed | Ch 18 made both changes. Verified. |
| r4-ch06 fixlog: #iss-clash "fadds shows no penalty"; experiment request (12 B, odd banks) | Fixed | The sentence is removed. 12 B was measured (above). Odd-bank offsets are unreachable with separate arrays (cslc 4-byte alignment); this is recorded in issue 2 as Unknown, with a suggested single-array test. |
| r4-appA fixlog: link TSC/DSR/input queue/microthread/bank; cb16 | Fixed | Links added. The cb16 row follows App A's tags after the rescan. |
| r4-ch13 fixlog | n/a | Issue 3's "we have not isolated why" is retired by the merge. |
| r4-ch14 fixlog | n/a | Nothing aimed at App E. |

## For other pages
- **Ch 6 `#banks` table and widget:** fill the 12 B cells: `@fadds` WSE-3 527 (2), WSE-2 1,038 (1); `@fmach` WSE-3 272 (≈4), WSE-2 526 (2) [Measured, TSC, cs_readelf-checked, App E #iss-clash]. Both fit the WSE-2 window hypothesis. Odd-bank f16 offsets cannot be reached with two separately declared arrays (cslc aligns them to 4 B), so mark them "not reachable with separate arrays" instead of "not measured".
- **tools/scan_tags.py (coordinator), r4-appE X1:** cut a multi-tag table cell's claim at the clause the tag follows (Ch 9's 405B row shows 969 tok/s as Unverified), and merge rows that share a claim (Ch 9 Kimi rows, CS-4 rows, Ch 1 WikiChip rows), showing both tags.
- **Ch 17:** the TMEM 256 KB sentence still carries "Unverified background, Colfax" ahead of its Vendor CUTLASS tag, and the NVL72 "18 compute trays × 4 GPUs, 9 NVSwitch trays" is still Unverified. r4-appE found the NVIDIA GB200 SuperPOD reference architecture (via search) for the second, so it could be "Vendor via secondary".
