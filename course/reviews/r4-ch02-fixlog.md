# R4 fix log · ch02 (02-the-wafer.html)

Sources for this pass: r4-ch02.md; the still-open r3-gaps-ch01-02 items G4, G8, G10; cross-page items r4-ch08 E4/E5 and r4-ch10 E3; CROSS_CHAPTER_NOTES 30–38.

## r4-ch02 items
- **E1 · Fixed.** The per-PE paragraph now says "at the SDK's 850 MHz on WSE-3" and gives the 1.1 GHz figures (21 B memory, 29 B fabric). It now says the fabric check only brackets a clock (WSE-3 fits 32–40 B only between about 740 and 930 MHz) and does not confirm one. The callout gives ~40% at 850 MHz and ~56% at 1.1 GHz.
- **E2 · Fixed.** Replaced the "because the vendor peak assumes 16-bit SIMD" clause with arithmetic: f16 @fmach at ~4/cycle gives 3 × 4 × 2 B = 24 B ≈ 6 words, which matches the vendor per-PE memory figure. An 8-wide path would need 48 B/cycle.
- **E3 · Fixed.** "I/O lives on the rim" now separates system I/O (CS-2/CS-3 12 × 100 GbE = 1.2 Tb/s Vendor; CS-4 2.4 Tb/s) from the SDK memcpy path (~112 Gb/s, quoting the bandwidth-test docstring). Refill times are 0.3 s and 3 s. Added a "CS-3 system I/O" bar to the bandwidth ladder and readout, and the NVLink reference is now looked up by name.
- **E4 · Fixed.** Added the `#cs2-dims` note after the overhead table. It quotes the README "must be 750,994" sentence, gives the competing sweep.py/run.py reading (program rectangle, fabric ≥ 757 × 996) and tags it Unverified. The stat tile, table, repair caption, memcpy paragraph, matvec callout and quiz Q6 now link to the note or mention it. The numbers are unchanged.
- **E5 · Fixed.** Retagged as Vendor: NVLink 4 (H100 datasheet, 900 GB/s bidirectional), GH100 144 SMs (Hopper whitepaper), H100 die ~814 mm², H100 SXM 700 W max TDP. Removed every "not re-verified" and "Industry figure" tag. Applied in the text, yield-curve note and ladder tooltips.
- **E6 · Fixed.** "HC34" now appears only in a one-time gloss (HC22 = Hot Chips 2022, the 34th Hot Chips). Everything else says HC22.
- **X1 · Fixed.** Added the derivation of 12N² + 4N: read A[i,j], read y[i], write y[i] (3 × 4 B per multiply-add); x is read once per column. Linked the derivation to the "12 B = 3 words" lesson.
- **X2 · Fixed.** Added a sentence saying vendor fabric totals sum router ports, so each link is counted at both ends (a 2× over-count against traffic). Added the same note to the calculator's fabric row.
- **X3 · Fixed.** Quoted the paper's own phrase ("about one third of the machine's peak performance", arXiv:2010.03660). Noted that it implies a peak near 2.6 PF (Derived) and that the page has no independent CS-1 peak.
- **X4 · Fixed.** The reticle section now says each PE pairs a compute core plus 48 KB with a five-port router (4 neighbours + ramp), with links to Ch 3 #anatomy and Ch 4 #mesh. The repair caption now reads "each a PE slot: a compute core plus its router".
- **X5 · Fixed.** Glossed `--fabric-offsets=4,1` and `--channels 1` inline, with a link to Ch 10 #flags.
- **X6 · Fixed.** Every "Chapter N" in prose is now a link, to a section anchor where one exists (Ch 1 #three-answers/#trap, Ch 3 #anatomy/#bank-model/#sparsity/#no-caches, Ch 4 #mesh/#routes/#latency, Ch 6 #op-speed, Ch 7 #door/#frame, Ch 8 #cs4/#inference/#memoryx, Ch 10 #flags, Ch 17). First uses of these terms link to the glossary: reticle, fabric, wavelet, colour, PE, router, hop, SM, spare cores, memcpy, memcpy frame. A Playwright check confirmed all 44 hrefs resolve to existing ids. Short "Ch N" mentions inside JS-generated widget text stay plain.
- **G1 · Fixed.** The reticle section now defines a wavelet: a 32-bit packet tagged with a colour that picks its route, with links to the glossary and Ch 4.
- **G2 · Fixed.** Added a paragraph after the first-principles check giving the measured f16 @fmach rate of ~4/cycle on both chips (best placement; WSE-2 drops to ~2 when badly placed, per note 30). So WSE-2 reaches its 4-wide vendor width, while WSE-3's 8-wide path is not demonstrated: ≈ 6.1 PF at 850 MHz. The calculator gained a green "measured f16 rate (Ch 6)" bar (N × 4 × 2 × f). Quiz Q5 now names SIMD width as the second weak input.
- **G3 · Fixed.** The hop text now says the "one hop per cycle" figure comes from the hardware paper, and that the simulator models 1.0 (WSE-2) and 2.0 (WSE-3) cycles per hop, so WSE-3 times double. It links Ch 4 #latency (notes 20/34).
- **G4 · Fixed.** In the "Means later" column, the SRAM row now says "≈ 44 KB is yours on WSE-3 (Ch 3, Ch 10)" and the FLOP row says "one f32 @fmacs ≈ 1 elem/cycle, f16 @fmach ≈ 4 (Ch 6)". The section intro points readers to that column.
- **G5 · Fixed.** Added a forward pointer: models larger than 44 GB stream weights layer by layer from MemoryX (Ch 8 #memoryx) during training.

## r3-gaps-ch01-02 items still open for ch02
- **G4 · Fixed** (see G2 above). **G8 · Fixed** (see G3 above). **G10 · Fixed** (see E5 above).
- WSE-3 fabric size and the spare scheme · Skipped: no public source (as r3 says).

## Cross-page items about ch02
- **r4-ch08 E4 / note 36 · Fixed.** WSE-2 7.5 PF dense is now tagged Vendor (HC22) in the spec table and calculator. "Read the FLOPs" says the 10:1 ratio is Cerebras's own, quoting the slide, and that only WSE-3's 8:1 is an analyst assumption. The first-principles check and Q5 now say "matches HC22's dense figure".
- **r4-ch08 E5 / note 33 · Fixed.** The generations intro and the table note quote Cerebras: "twice as much power to the WSE-3 Turbo, enabling higher operating frequencies" [Vendor, linked to Ch 8 #cs4]. The Next Platform estimate of ~1.4 / ~2.8 GHz is tagged Analyst + Unverified in the WSE-3T clock cell and the note. The page now says "WSE-3 Turbo" is the vendor's name for WSE-3T.
- **r4-ch10 E3 · Fixed.** Covered by E4: the CS-2 fabric reading is now caveated with an Unverified tag. The 743 × 992 bound is kept but marked as dependent on that reading.
- Notes 30–38: note 30 (one placement rule, linked to Ch 6) is applied to the f16 text. Note 34 (hop) is applied. Note 38 (links) is applied. Notes 31, 32, 35 and 37 do not touch this page.

## Verification
I ran Playwright at 1100 and 390 px and drove the ladder toggle and the calculator's generation buttons and clock buttons. There were 0 console or page errors, no NaN or undefined values, and no horizontal overflow (scrollWidth equals viewport). Every in-page and cross-page anchor resolves. I checked screenshots of #pe and #bw. No simulator runs.

## For other pages
- **Ch 6:** note 30 names `#banks` as the canonical anchor for the placement table. It did not exist when I checked, so ch02 links `06-dsds.html#op-speed`. If the Ch 6 fixer adds `#banks`, the link could be retargeted.
- **Ch 7 / Ch 10 / Ch 13 / Ch 18:** these should use the same 750 × 994 caveat (ch02 `#cs2-dims`), per r4-ch10 E3 and r4-ch18 E5.
- **Ch 1:** Ch 1 should use the same CS-3 1.2 Tb/s system-I/O Vendor tag and the measured f16 ≈ 6 PF roof (r4-ch01 G4), so the two pages stay consistent with ch02.
