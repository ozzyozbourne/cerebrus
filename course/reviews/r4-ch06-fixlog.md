# R4 fix log · ch06 (06-dsds.html)

Only `06-dsds.html` was edited. No experiments were run: every new number comes from the page, Ch 11, Ch 13, Ch 15, App E or CCN 29/30/35, and the memcpy queue depths were read from the SIF (`csl-libs/memcpy/wse2/memcpy.csl` comments). Playwright at 1100 and 390 px, light and dark: 0 console errors and no horizontal overflow. I drove every option of the new collision widget, plus bank view, presets, the sv/gv/tl widgets. All 45 distinct hrefs resolve to existing ids.

## Canonical placement table (CCN 30)
- New `<h3 id="banks">` "Which bank does an operand start in? The placement rule", inside #collisions. It contains:
  - the cs_readelf man-page quote and the 16-bit bank rule;
  - why "equal mod 4 words" means "same bank";
  - the redesigned collision widget;
  - the canonical 6-row table: f32 fmacs / f32 fadds / f16 fmach × WSE-3/WSE-2 × start offsets of 0/4/8/12 B mod 16, with "not measured" where no run exists;
  - a "One rule for placement" callout in CCN 30's wording, which also says that the rule differs by chip.
- Other pages can link to `06-dsds.html#banks`.

## Items
- **E1** Fixed. 8 single-ported banks tagged Vendor (HC22); 6 KB and the 32-bit interleave tagged Independent, linked to Ch 3 #bank-model and App E #iss-bank. SDK 16-bit rule stated at #banks. The DSD visualizer's bank view now uses the SDK rule (word w → banks 2(w mod 4), 2(w mod 4)+1), and its readout names the academic model.
- **E2** Fixed. @fmach row: "2, or ≈4 with sources 8 B apart (App E)". The f16 bullet is rewritten in placement terms. The "memory traffic" explanation is retired. The rate-table intro says that its 1,025-word spacing is 4 B mod 16, a slow placement for WSE-2. The f32 collision rule is now scoped by the table.
- **E3** Fixed. "40 cycles of streaming + ≈19 start-up ≈ 59 (Chapter 13)".
- **E4** Fixed. Start-up is qualified as "isolated op bracketed by timestamp reads"; consecutive ops start in ≈6 (WSE-3) / 5 (WSE-2), Ch 13.
- **E5** Fixed. The table intro no longer gives a count. Added an @fsubs row. "Used in" now covers programs 06 (fmacs, two-DSD fmuls, fadds) and 07 (fmacs, fmovs, fsubs, scalar @map). Program use was added to the @set_dsd_base_addr / @set_dsd_length rows.
- **E6** Fixed. Footnote under the sv widget, and the widget's final readout gives ≈17+2N for program 01 as shipped.
- **E7** Fixed. Changed to "no hardware caches (only a tiny software-managed cache, Ch 3)".
- **X1** Fixed. Column header: "after subtracting ~17 cycles of start-up".
- **X2** Fixed. One-line TSC gloss plus glossary, Ch 11 #kernel-time and App C #tsc links.
- **X3** Fixed. The README mechanism is paraphrased: serialized H2D/D2H → internal queues fill → back-pressure (link to Ch 4) → H2D stalls. Per CCN 35, the memcpy input-queue depths 6/4/2 are cited [SDK]; "not a published depth" was removed.
- **X4** Fixed by E1 + G1. Both pictures now use the SDK 16-bit banks.
- **X5** Fixed. Glosses for H2D/D2H (with a Ch 7 link), for the memcpy kernel (G5 sentence and the timeline hint), and for the "halo" PE (pipeline-03's artificial halo vs memcpy's halo, Ch 7).
- **X6** Fixed. About 25 new cross-chapter links to section anchors, and glossary links: DSD, DSR, builtin, TSC, bank, fabric DSD, wavelet, input queue, microthread, FIFO.
- **G1** Fixed. Mechanism paragraph, man-page quote including the "modulo 4" clause and App E's finding, and an interactive 16-bit bank-ruler strip (the #bk widget redesign). The widget shows the two streams on the bank ruler, the start banks and the measured cycles on both chips. Its red marks come from a WSE-2 read-window hypothesis, tagged Derived. That hypothesis fits all WSE-2 cells of the table but not WSE-3.
- **G2** Fixed. "Lab 1 hits this case" bullet (2,063 → 1,039, Ch 11). Quiz Q5 now asks about program 01.
- **G3** Fixed. A paragraph on the @map signature and per-element call, plus a two-row table: vector-op body (≈N+2 per call) vs CG's scalar dot body (≈10 cycles per cell for the two dots, Ch 15 #scaling).
- **G4** Fixed. Opening paragraph of #fabric-dsds: a fabric op waits per element on its microthread under back-pressure (link to Ch 4); this is tied to the sync deadlock, to send completion, and to the 14-wavelet stall.
- **G5** Fixed. "memcpy is not a DMA engine: its receive handler runs as tasks on this PE's CE (Ch 7)", plus the timeline hint.
- **G6** Fixed. Forward sentence after the GEMV widget to program 06's `@fmacs` + `@increment_dsd_offset` loop (Ch 14 #code).
- **G7** Partly. Added a static mem4d folding diagram (4 buffer slices → acc[0..3], colour = k), with a pointer to SUMMA kernel 1's zero-stride `A_tile[i]`. Skipped as optional and low priority: the wavelet_index_offset mini diagram, the 16-bit packing diagram, an animated systolic reduction, and a numeric stencil step-through. ".index unit" stays Derived, because no SDK source states it.

## Cross-page items about Ch 6
- r4-ch11 (Ch 6 mis-tag of the 32-bit interleave): Fixed (E1).
- r4-ch14 E3 ("Ch 6 never says the clash rule differs by chip"): Fixed. The #banks callout says it explicitly, and the table shows it.
- r4-appE E2/E3 (Ch 6 f16 row and the "1 / 2" fadds footnote): Fixed. The fmach and fadds rows and the Lab 3 callout now explain the WSE-2 add through placement (u[i]/u[i+2] are 8 B apart).
- CCN 33 (clock): the worked example adds the ~1.4 GHz press estimate [Analyst, Unverified] and says per-second figures scale by ≈1.6×.
- CCN 30 retired phrases: removed "memory traffic … sets f16 speed" and the "3.2" f16 rate. Placement is the stated cause.
- CCN 31/32/34/37: not present on this page.

## For other pages
- Ch 3 (#bank-model, #pe-speed), Ch 11, Ch 13 (#numbers-say "we have not isolated why"), Ch 14, Ch 15 (G3 Z table), Ch 17 (E2 strided DSD), App B, App C (G-item on PAD addresses), App E (issues 2/3): state the one-line rule and link `06-dsds.html#banks` (canonical table).
- App E #iss-clash still cites "Ch. 6 … @fadds shows no penalty". That sentence is now scoped: no penalty on WSE-3, and WSE-2 adds need 8 B placement.
- Ch 13 line ~431 says "Chapter 6 measured about 17 cycles to start an isolated op … We have not isolated why". Ch 6 now states both figures. Ch 13 could link `06-dsds.html#op-speed`.
- Gaps worth one experiment by whoever owns App E: fadds and fmach at 12 B, and fmach at the odd-bank offsets (2/6/10/14 B). These cells read "not measured" in the #banks table and widget.
