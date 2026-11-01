# ch02 · fix log

File edited: `course/02-the-wafer.html` only.

Verification: Playwright/Chromium at 1100 px and 390 px, light and dark, plus the in-page theme toggle. No page or console errors. No horizontal page overflow (scrollWidth equals innerWidth in all four renders). Every control was exercised: both bandwidth-ladder modes, both generation tabs, the clock slider, both clock presets, both density sliders (checked that they stay in sync), all spare-segment options, both accounting modes, and Re-roll ×5. Key figures were screenshotted and inspected, and the problems found were fixed (clipped labels, the sparse bar label, repair arcs, the inset label, heat arrows, the cramped phone table).

Coordinator note (from the ch08 depth review): **applied and verified.** `/home/user/cerebras-sdk/tmp/ch08depth/hc22.txt` (Sean Lie, HC2022) reads "1.1GHz clock frequency · 30mW peak power" and "228µm x 170µm core area · TSMC N7". The HC24 text has no clock. Changes: the stat tile now reads "1.1 GHz WSE-2 clock [Vendor HC22]; none published for WSE-3; SDK assumes 850 MHz". There is a new "Core clock" row and a new "Core size" row in the table. The sanity check now runs WSE-2 at 1.1 GHz, which gives 7.5 PF, exactly the analyst figure. WSE-3 is shown at 1.1 GHz (≈15.8 PF) and at 850 MHz (≈12.2 PF), tagged unconfirmed. Hop latency is given at both clocks. The calculator has an "HC22 1.1 GHz" preset. A power cross-check was added (850k × 30 mW ≈ 25 kW). The 0.038 mm² figure is now attributed to HC22 (0.039 mm², WSE-2).

## Accuracy
| ID | Status | Note |
|---|---|---|
| A1 | fixed | The 1 GHz-only check is replaced. It now uses the HC22 1.1 GHz WSE-2 clock and the SDK's 850 MHz; the stat tile is rewritten (see the coordinator note). |
| A2 | fixed | "(~814 mm²) Derived" added to the lede. |
| A3 | fixed | Reticle tagged Industry standard; B200 10 TB/s tagged Vendor. |
| A4 | fixed | H100 989 TF tagged Vendor. |
| A5 | fixed | "6% more cores" tagged Derived. |
| A6 | fixed | 0.05 mm² is tagged Vendor; the alternative is now the HC22 0.039 mm² (228 × 170 µm) Vendor figure, with the area-share arithmetic. |
| A7 | fixed | "configured at manufacturing time" becomes "reconfigured … when/how not public". |
| A8 | fixed | "a few dozen" is replaced by the vendor model's 46; density not published. |
| A9 | fixed | "at least 7 columns / 2 rows"; "at most 743 × 992" in text and quiz. (Ch07 has the same wording; not edited.) |
| A10 | fixed | Edge I/O tagged Derived (physical layout not public); north/south row mentioned. |
| A11 | fixed | ~737k tile now tagged SDK and Derived. |
| A12 | fixed | 48 KB tile tagged Vendor. |
| A13 | fixed | WSE-2 "+ 256 B cache"; WSE-3T "same as WSE-3". |
| A14 | fixed | Fabric row now uses a single unit, PB/s with Pb/s in brackets; WSE-3T ~428 Pb/s. |
| A15 | fixed | "higher clock" tagged The Register; "(per press analysis)" added to the sentence. |
| A16 | fixed | WSE-3T power reads "not published (3 wafers per rack; backpacks 2× CS-3 power/cooling)". |
| A17 | fixed | Vertical power, engine block and connector tagged Secondary sources; CS-4 0.5 mm stays Vendor. |
| A18 | fixed | Quiz answer says the 745.5k breakdown is unpublished ("most likely spares and edge infrastructure"). |

## Pedagogy
| ID | Status | Note |
|---|---|---|
| P1 | fixed | New section "What the wafer buys" (no data leaves the silicon, ~30,000× NVLink, 50:50 SRAM area → 44 GB, link back to ch01), plus the bandwidth-ladder widget. |
| P2 | fixed | The I/O paragraph now attributes the frame to memcpy programs on ordinary PEs, rows explained; the quiz is updated and the new "where the cores go" figure shows it. |
| P3 | fixed | Fixed-cost paragraph added (65% of the wafer used, ~24,000 mm² of corners, spare area, no binning); a simulator readout row; corners labelled in figure 1. |
| P4 | fixed | "Worked example: why spares are not optional" callout (e^−0.858 ≈ 42% for a full reticle; e^−46 ≈ 10⁻²⁰). Uses 858 mm² (26 × 33) rather than 832 so it matches the figures. |
| P5 | fixed | Sparse FLOPs explained: zero-skipping, the analysts' 8:1 assumption (10:1 for WSE-2), and 2:4 = exactly 2×. The Q4 answer is extended. |
| P6 | fixed | One clock story across the chapter: HC22 1.1 GHz (WSE-2) and the SDK's 850 MHz; matches Lab 3's use of 850 MHz. |
| P7 | fixed | Objectives rewritten (vendor vs analyst vs measured, now delivered via the SC20 and simulator numbers); the WSE-3 rectangle is stated as unpublished. |
| P8 | fixed | Caption covers spare links, unknown hop cost, and that repair is not Chapter 4 colour routing. |
| P9 | fixed | Fabric, PE/core, scribe line, SM and "fabric position" defined at first use. |
| P10 | fixed | Fabric units unified; footnote on WSE-3T's ~2× implying a clock change, and the unexplained WSE-2 → WSE-3 fabric drop. |
| P11 | fixed | H100 132 SMs (Vendor) of 144 (tagged Industry figure, not re-verified: 144 is not in the course sources). |
| P12 | fixed | Quiz now has 6 items, including yield arithmetic and a FLOPs estimate; the Q3/Q6 answer is hedged. |
| P13 | fixed | ~20,000 A at an assumed 0.8 V (assumption stated) and why edge feeding fails. |
| P14 | fixed | B200 link tagged (same fix as A3). |

## Visuals
| ID | Status | Note |
|---|---|---|
| V1 | fixed | Figure 1 redrawn to scale (1 px = 1 mm); the 215 mm square is clipped by the wafer circle and the 304 mm diagonal is explained in the text. |
| V2 | fixed | Only whole dies, 26 × 33 mm, best-aligned (62 whole dies, count printed); the simulator uses the same geometry. |
| V3 | fixed | Field grid is 9 × 7 (each field ≤ a reticle), labelled "count illustrative". |
| V4 | fixed | All JS colours use CSS classes (s-acc, s-blu, s-amb, f-red); verified after the theme toggle. |
| V5 | fixed | Figure 1, the repair figure and the simulator are each split into two SVGs in a `.panels` grid that stacks on phones; the other wide SVGs use the shared min-width scroll. |
| V6 | fixed | Remapped cores and the used spare are blue; logical-x labels on both sides; arcs above the row with extra spacing; legend added. |
| V7 | fixed | Amber arrowheads, a compliant-connector layer, heat arrows, I/O arrows, tightened viewBox. |
| V8 | fixed | Fixed pool of 260 random points; the slider takes a prefix (monotonic), Re-roll redraws. |
| V9 | fixed | Accounting selector (whole die vs one SM ≈ 7.8 mm², Derived from 164×) and a dead-silicon ratio row; the text explains why 164× needs SM-level accounting. |
| V10 | fixed | Labels moved below the wafers, grid centred, readout is an aria-live table that wraps cleanly. |

## Depth
| ID | Status | Note |
|---|---|---|
| D1 | fixed | New section "One wafer, 900,000 small machines" with a per-PE budget widget (WSE-2/WSE-3 toggle, clock slider, presets); clock-dependent cells highlighted; consistency paragraph. |
| D2 | fixed | "What a real kernel gets" callout. I re-ran `single-tile-matvec` myself (wse3, N = 100): 10,154 cycles, 120,400 B, scaled 7.51 PB/s and 1.24 PF. Tagged Measured, with the method stated; the reviewer's WSE-2 count (10,160) is cited. |
| D3 | fixed | Marketed vs visible table (CS-1 380k Measured on hardware, SC20; CS-2 SDK; CS-3 unpublished), the 70k claim judged, BiCGStab 0.86 PF. |
| D4 | fixed | "How many spares" paragraph (65% / 12% birthday arithmetic) plus a spare-segments selector in the simulator with the analytic P(fail). |
| D5 | fixed | Hop latency (1,744 hops, 1.6–2 µs) in "What the wafer buys"; perimeter vs area, 112 Gb/s, ~3 s to refill, CS-4 2.4 Tb/s in "I/O lives on the rim". |
| D6 | fixed | ~0.5 W/mm² vs H100 ~0.9 W/mm² (700 W / 814 mm² tagged Industry figures); per-PE power row; HC22 30 mW cross-check. |
| D7 | fixed | Table of the three ways past the reticle, with the Theseus caveat; no Dojo numbers. |
| D8 | fixed | Field count stated as schematic; 84 (12 × 7) not used because it is unverified. |
| D9 | fixed | The simulator shows the expected good-die fraction e^(−D·858) and the D·46,225 model, which reproduces 46 → 2.2 mm². |

Counts: 50 findings — 50 fixed, 0 partial, 0 skipped.

## New visuals added
1. **Bandwidth ladder** (N3): a log bar chart with a per-chip / per-mm² toggle and hover sources. It shows that size explains only ~57× of the ~30,000× gap.
2. **Per-PE budget and dense-FLOPs calculator** (D1 + N4): generation tabs, clock slider with SDK and HC22 presets, a derived table, and bars comparing the estimate with the analyst dense and vendor sparse figures, plus the clock needed to match the analyst figure.
3. **Yield vs unit size curve** (N1): Poisson curve on a log-area axis with five marked units; its density slider is synced with the simulator.
4. **Where the 850k cores go** (N2): to-scale fabric and program rectangles inside an 850k outline, a zoomed north-west corner showing the memcpy frame, and waterfall bars (850,000 → 745,500 → 737,056).
5. The defect simulator was extended with the spare-segment repair model (N6-lite / D4) and the accounting toggle (V9).
6. Figure 1, the repair schematic and the cross-section were redrawn (V1–V3, V6, V7).

## Left for later
- Not built: N5 (powers-of-ten zoom), N7 (generation small multiples), N8 (stitching close-up), and the clustering parameter of N6.
- Cross-chapter: ch07 says "must be 7 columns narrower" (should be "at least"). ch03 and ch04 still use "~1 GHz" in their sanity checks; they should adopt HC22 1.1 GHz for WSE-2 and the SDK's 850 MHz.
- Unverified figures used with honest tags: H100 die ~814 mm², GH100 144 SMs, H100 ~700 W, NVLink 4 0.9 TB/s.
- The WSE-3 user-visible fabric size is still unpublished.
