# ch01 · fix log

File edited: `course/01-memory-wall.html` only. Verified with Playwright at 1100 px and 390 px, light and dark: no page or console errors, no horizontal page overflow. Every widget control was exercised (4 chips × all memory levels × 3 formats × 4 presets, slider extremes and keyboard, calculator 3 models × 4 chips × 3 formats × 2 contexts × 3 batches, "Show on roofline", map modes and hover, theme toggle). I checked the screenshots by eye, then deleted them.

Re-measured: single-tile-matvec on SDK 2.10.1, WSE-3 simulator, N=25 (780 cycles) and N=100 (10,154 cycles, 1.24 PF / 7.5 PB/s scaled). Both match D5 exactly.

## Accuracy
- A1 fixed: vector-add preset is now 1 FLOP / 12 B ≈ 0.083. The slider and axis were extended to 10^-1.5.
- A2 fixed: intensity is now defined as bytes moved, reads plus writes. For decode that is essentially the weight bytes read.
- A3 fixed: the comparison trap now notes that the two figures give ≈ 6,300× (Derived).
- A4 fixed: the decode, batch and prefill intensities carry Derived tags and are now worked out in full.
- A5 fixed: 44 GB is tagged Vendor; ~66 MB (132 × 512 KB) is tagged Derived.
- A6 fixed: the figure's tspan tag was removed; the figcaption now holds the per-number provenance.
- A7 fixed: the caption now says "every byte a PE owns"; other bytes cross the fabric; the 512 B cache is mentioned.
- A8 fixed: the widget hint explains the different memory levels and says ridges are Derived.
- A9 fixed: the roadmap now includes Chapter 2 (Part I) and Chapter 7 (host I/O).
- A10 fixed: Rubin's 19.2 TB/s is labelled as the revised spec (launch spec 22).

## Pedagogy
- P1 fixed: added a paragraph saying a roofline belongs to one memory level. The widget gained a "Memory level" selector (H100 HBM/L2/smem; WSE-3 SRAM/fabric/off-wafer), a hint and a WSE-3 caveat note. Memory levels replace the proposed 5th "H100 smem" chip.
- P2 fixed: the caption is rewritten, and a "placement and communication problem" paragraph follows the trap.
- P3 fixed: a "Capacity cuts both ways" paragraph gives devices per 70B model, the 36 GB KV headroom and MemoryX. The SVG now says "no DRAM on the wafer".
- P4 fixed: added the worked 1 FLOP/B derivation, the tokens/s ≤ BW ÷ bytes rule and the 8B/H100 ≈ 210 tok/s example.
- P5 fixed: same as A1/A2.
- P6 fixed: added a "Terms used here" callout.
- P7 fixed: the quiz now has 7 questions: ridge (p150), tokens/s bound, KV/batch, per-level, WSE-3 assumptions, trap. Q1 was reworded for bytes moved.
- P8 fixed: a "Weights" format selector rescales the LLM presets. The B200 FP4 note appears when the format does not match.
- P9 fixed: the shared-memory ≈ 30 TB/s derivation is shown, with its assumptions flagged as unsourced; the like-for-like gap is given as ≈ 50–700×.
- P10 fixed: same as A3.
- P11 fixed: Rubin 50 PF ⇒ ridge ≈ 2,600, plus a generations table.
- P12 fixed: added a "Latency is not bandwidth" paragraph.
- P13 fixed: the marker now reads "die edge" (also added to the Tenstorrent row; HBM labelled "in package").
- P14 fixed: the roadmap wording now uses "replaces a main loop" and "DSDs turn whole loops into single instructions".
- P15 fixed: three strategy bullets were added before the figure.

## Visuals
- V1 fixed: covered by the shared phone CSS (SVGs keep ≥ 620 px and scroll inside their box); I checked legibility at 390 px. No responsive redraw was added.
- V2 fixed: added direct coloured labels at the right end of each roof, placed to avoid collisions. Lines are clickable to select a chip.
- V3 fixed: same as A1.
- V4 fixed: the preset `<select>` became buttons with aria-pressed. They deselect when the slider moves off a preset and can always be re-clicked.
- V5 fixed: the marker is a hollow ring in --text on --surface; the guide line is --text at 0.5 opacity.
- V6 fixed: the ridge label is placed at the candidate position with the fewest line collisions, and has a halo.
- V7 fixed: added `nice()` formatting; there is no e-notation; x ticks read 0.1…100k; fmtF uses 3 significant figures.
- V8 fixed: inactive roofs are dashed at 0.75 opacity.
- V9 fixed: added aria-valuetext and a datalist of decade ticks.
- V10 fixed: the readout lists every level of the chip; a note under the widget gives the WSE-3 caveat per level. A dashed "off-wafer" roof is drawn for WSE-3.
- V11 fixed: both sides say read once; "used ×1 / ×2,000" counters; an output y/Y; a KV-cache strip; prefill intensity corrected to ≈ 1,300.
- V12 fixed: "die edge" ×2, per-level bandwidth sublabels, the tspan and dead path removed, a thick PE↔SRAM connector with "1 cycle away", a "wafer edge" with an off-wafer box (~150 GB/s, Ch 8). Line-weight encoding of bandwidth was skipped.

## Depth
- D1 fixed: added a "roofline for every level" table (H100 HBM/L2/smem, p150, WSE-3 SRAM/fabric/off-wafer, SDK host link) plus a paragraph saying the wall moves rather than disappears. It is also built into the widget.
- D2 fixed: added the "Decode speed bounds" calculator widget, a "Bound versus reality" table and the latency paragraph. The wafer bound is given as a range, 150k (pipeline) to 600k (parallel), so measured speed is 65–260× below it. The review's single 600k figure assumed parallel reads.
- D3 fixed: added a derivation callout (linear-layer intensity formula, KV cache 0.33 MB/token, ≈ 49 at 2k, ≈ 30 at 8k). The calculator plots the effect. A separate intensity-vs-batch chart was not added, because the calculator covers it.
- D4 fixed: added a "One PE, then 900,000" table and the note that the 850 MHz clock is an SDK assumption.
- D5 fixed: added a measured matvec callout with the cycle table. I re-ran N=25 and N=100 myself; the N=50 row is the reviewer's run.
- D6 fixed: added a ridge-by-generation table with the format effect. Finding: B200's FP4 gap (~280×) roughly matches H100's; Rubin and p150 are ~650×.
- D7 fixed: devices per 70B model and the 3 s wafer fill time are in the capacity paragraph and the calculator.
- D8 fixed: added a prefill paragraph (≈ 16× dense FLOPs, 23 kW, TTFT, price per token).
- D9 fixed: added Little's law with a 600 ns latency marked as illustrative.

## New visuals / widgets added
1. Roofline per memory level: the existing widget was extended with a level selector, a weight-format selector, preset buttons, direct labels and an off-wafer roof (N3/D1).
2. "Decode speed bounds" calculator: model/format/batch/context/chip; chips needed; a memory-vs-math step-time bar split into weights, KV and math; tok/s bounds; a link to the roofline (N1/D2/D7).
3. "Capacity versus bandwidth" log-log map: 8 memory levels plus the H100 RF+smem range bar and the 8B/70B working-set lines; a toggle between the marketing (6,300×) and like-for-like (50–700×, 670× capacity) comparisons; hover/tap shows provenance (N2).
4. Tables: roofline per level, bound versus measured, ridge by generation, one PE ×900,000, measured matvec.
5. Redrawn decode/prefill and "three answers" figures.

## Left for later / open
- H100 shared-memory (~30 TB/s) and RF bandwidth are rough estimates; per-SM bytes per clock and the clock speed are not in our sources. Check against the Hopper whitepaper.
- CS-3 12×100 GbE (~150 GB/s) comes only from a forum post.
- Llama-3 layer shapes (layers, KV heads) come from the public model configs, not the research files; they are tagged as an assumption.
- N4 (animated generation bars), N5 (animated decode) and N6 (kernel intensity counter) were not built; the D6 table covers N4's content.
- No responsive redraw for phones; this relies on the shared horizontal-scroll CSS.
