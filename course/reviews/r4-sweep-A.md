# Round-4 cross-page sweep, part A (Ch 1–7)

Verified: all seven pages load in Playwright at 1100 px with zero console errors; every relative link and anchor resolves.

## Ch 1 (01-memory-wall.html)
- App A G5: Tensix glossary link: Already done. Blackhole (`g-blackhole-wormhole-grayskull`) and MemoryX (`g-memoryx`): Done (first uses, bandwidth table).
- App A: "Full glossary" link in Terms box: Already done.
- r4-ch01 / item 30: two "Chapter 6" `#op-speed` links (bank-placement rule) → `06-dsds.html#banks`: Done.
- r4-ch08 / item 36: WSE-2 7.5 PF tagged Vendor (HC22): Already done.
- r4-ch02: CS-3 1.2 Tb/s Vendor tag, measured f16 ≈ 6 PF roof: Already done.
- r4-ch09 / item 33: 2,000–4,000 tok/s now says SDK 850 MHz and gives ≈ 3,300–6,600 at the ~1.4 GHz press estimate with a link to `09-model-to-tokens.html#ceilings` (bound table and prose): Done.
- r4-ch16: Wormhole Galaxy ≈ 124; quiz 1.5 MiB: Already done.
- Sweep item 5: the measured-callout "750 × 994 rectangle (the CS-2 fabric size)" now links the `#cs2-dims` caveat: Done.
- r4-ch18 (Rubin ridge caveat): Already done (no change needed).

## Ch 2 (02-the-wafer.html)
- r4-ch01/ch08 / item 36: WSE-2 7.5 PF Vendor (HC22); 10:1 vendor-stated, only WSE-3 8:1 analyst; WSE-3T clock quote cites Ch 8 #cs4: Already done.
- r4-ch02 / item 30: `#op-speed` link for the placement rule → `#banks`: Done.
- r4-ch07/ch10: 743 × 992 caveat: Already done (this page hosts `#cs2-dims`; table, prose, figure and quiz all carry it).
- App A G5: memcpy glossary link: Already done.
- Clock labelling: no tok/s figures on this page; per-second figures already name 850 MHz / 1.1 GHz: Already done.
- r4-ch04: optional new Ch 4 anchors (`#ce-hop` etc.): Skipped (optional; existing `#latency` link covers it).

## Ch 3 (03-processing-element.html)
- r4-ch04 G8 / item 34: hop wording ("about one router per cycle on hardware … simulator models 2"): Already done.
- r4-ch06/ch16 / item 30: #pe-speed "3.2 per cycle on WSE-3 / 2.0 on WSE-2" reworded as a whole-kernel average (start-ups included), not an op rate; op rate stated by placement (≈4 WSE-3; ≈4 or ≈2 WSE-2) with link to `06-dsds.html#banks`; WSE-2/3 comparison row changed from "≈ 2–3.8 / ≈ 3.2–4" to "≈ 4 placed 8 B apart, ≈ 2 otherwise / ≈ 4": Done. "memory traffic" explanation: Already gone.
- `#collisions` links (placement explorer, comparison table) → `#banks`: Done. The `#op-speed` links that are about the op-rate table itself: left.
- #bank-model one-line rule: Already done (stream-start box).
- App A G5 glossary links: memcpy, simulator, cs_readelf, timestamp counter (TSC), `.ut_id`, and cslc / cs_python (in the Try-it box, with a pointer to Ch 10): Done. DSD: Already done. `@get_dsd`: Skipped (not used on this page).
- App D G3: "Next in the SDK → Appendix D" (`#after-ch03`) before the quiz: Done.

## Ch 4 (04-fabric.html)
- r4-ch05: #filters "Chapter 5 uses the index field for sparse data": Already done (now points to Ch 3 #sparsity / Ch 6 #index-offset).
- r4-ch12 / item 35: #back-pressure depths cite memcpy.csl 6/4/2: Already done.
- App A G5: memcpy glossary link: Done (back-pressure hint).
- Sweep item 5: CS-2 750 × 994 (mesh intro, numbers table, aggregate-bandwidth sentence) now link `02-the-wafer.html#cs2-dims`: Done.
- App D G3: `#after-ch04` line: Done.

## Ch 5 (05-tasks.html)
- r4-ch13 / item 37: ~88 → ≈90 with link to `13-lab-stencil.html#fixed-cost`: Already done.
- App A G5: DSD, memcpy: Already done. `@get_dsd` and SpMV: Done.
- App B: CUDA callout now links `#r-wait` and `#r-syncthreads`: Done.
- r4-ch12: anchor for the "stalls past 14" passage: Done, `05-tasks.html#blocking` (the Blocking rule). Ch 12 (src/12-lab-neighbours.html line ~152) can deep-link it; not my page, left for sweeper B.
- App D G3: `#after-ch05` line: Done.

## Ch 6 (06-dsds.html)
- Item 30: `#banks` with canonical table exists; "@fadds no penalty" scoped; "memory traffic"/"two reads and a write" gone; line ~204 "WSE-3 doubled adds" now cites placement; "interleaved by 32-bit word" tagged Indep: Already done.
- App B: CUDA callout now links `#r-warp`, `#r-loop`, `#r-banks` (and the in-page `#banks`): Done.
- App D G3: `#after-ch06` line: Done.

## Ch 7 (07-host-io.html)
- r4-ch10 / item 5: CS-2 750 × 994 / 743 × 992 caveat: Already done (Unverified, widget text); added link to `02-the-wafer.html#cs2-dims`: Done.
- r4-ch04: memcpy RAMP → RAMP route links `04-fabric.html#routes` and `#ce-half` (streaming H2D paragraph and streaming D2H bullet): Done.
- App B: CUDA callout now links `#r-launch`, `#r-memcpy`, `#r-streams`: Done.
- App A G5: memcpy glossary: Already done.
- App D G3: `#after-ch07` line: Done.
