# r4 fix log: ch03 (03-processing-element.html)

Sources: r4-ch03.md, r3-gaps-ch03-04.md (Ch 3 items), cross-page mentions in r4-*.md, CCN 30–38. No simulator runs. All new numbers come from CCN 29/30/35, Ch 6 #op-speed/#collisions, App E #iss-clash, SDK csl-libs (main_thread_priority.csl, memcpy/wse{2,3}/memcpy.csl) and single-tile-matvec/run.py.

## r4-ch03 items
- **E1** Fixed. #pe-speed bullet 2 now says the 3.2/2.0 figures are the f16 matvec's own layout. A well-placed @fmach runs at about 4/cycle on both chips, so read the rate as ≈3.2–4 (WSE-3) and ≈2–3.8 (WSE-2), set by bank placement. The "memory traffic" inference is gone. The WSE-2/3 table row now gives the ranges and links #stream-start, Ch 6 and App E.
- **E2** Fixed. Added an op-rate table (#op-rates): fmacs/fmuls 1/1, fadds 2/2 (WSE-2 1 unless 8 B apart), fmovs 2/4, fmach ≈4/≈4, plus ≈15–17 cycles of start-up per op. Bullet 1 now says it covers multiply-add only. Also added an add/copy row to the WSE-2/3 table.
- **E3** Fixed. #wavelets: "about one router per cycle on hardware per papers; the WSE-3 simulator models 2 and WSE-2 1 (Ch 4 #latency)" (CCN 34).
- **E4** Fixed. #memory-map explains 324 = 320 + 4: run.py allocates A as `nb*padded_nb + 1` and writes from index 1, which is the bank-avoiding shift. The capacity probe now reads "43,268 = (104² + 1) × 4".
- **E5** Fixed. The clock row has a footnote: the WSE-3T/CS-4 has the same PE, with press estimates of about 1.4 / 2.8 GHz [Analyst][Unverified]. It links Ch 2 #generations, Ch 8 #cs4 and the glossary (CCN 33). #feed adds the ≈17 B/cycle that a 1.4 GHz clock would give, with a caveat.
- **X1** Fixed. A 4-term key (DSR, microthread, queue, task) sits above the stepper. Each term links to App A and to the section that defines it, and `.async`/`.activate` link to Ch 6 #async. Steps 3 and 5 now name the queues and highlight the new queue block.
- **X2** Fixed. 85 links on the page now, up from 2. Every chapter, lab and appendix mention in the prose points to its section anchor, and first uses of PE, CE, wavelet, color, router, RAMP, queues, DSR/DSD/GPR, bank, bank clash, microthread, task, picker, task ID, software-managed cache, roofline, dataflow sparsity, HBM and WSE-3T link to App A. SVG `<title>`/label text was left as plain text.
- **X3** Fixed. #bank-model now opens with the effect: half-speed @fmacs and Lab 1's 2 cycles/element. Then come the SDK rule, the explorer and the placement box, with the academic-vs-SDK dispute moved to a "Sources differ" callout. Retitled "Which bank does an address land in, and why it matters" (id kept). The "pad to 16 bytes" advice now says what it buys and adds "move one source by 8 B and measure".
- **X4** Fixed. A hint paragraph glosses .text, .data, .bss and .data.lo, including what DSR images are (`__dsr_lowmeminit_*`), and the task table (task ID → handler address, 1 KB on WSE-3, link to Ch 5 #rules).
- **X5** Fixed. "Microthreads have low/medium/high priority levels; CSL exposes only the main thread's level (MEDIUM_LOW 'between low- and medium-priority microthreads' … HIGH)". Verified in main_thread_priority.csl.
- **X6** Fixed by G2: the 1.5 PF vs 125 PF bullet now says the two aren't comparable as they stand and points to the chain.

## Connecting gaps
- **G1** Fixed. Added a "Where two operand streams start matters" box (#stream-start) under #bank-model: same bank / 4 B / 8 B × f32 fmacs, f32 fadds, f16 fmach × both chips (CCN 29/30, Ch 6). It states the one-line rule and says the matvec was timed with the SDK's padded +1 layout; without the shift it takes 8,310 instead of 4,214 cycles (Ch 6, measured). It links Ch 6 #collisions, App E #iss-clash and Ch 11 #kernel-time. Also added a quiz question on placement, and the 4,214 quiz answer notes the layout dependence.
- **G2** Fixed. Lanes → headline chain in #pe-speed: 8 × 2 × 900k × 1.1 GHz ≈ 15.8 PF (≈ the analyst 15.6), measured 4 MAC/cycle × 850 MHz ≈ 6.1 PF, f32 ≈ 1.5 PF, × ~8 sparsity = 125 PF. It links Ch 2, 8, 9 and 18.
- **G3** Fixed. The anatomy SVG now draws a "queues 8 in / 6–8 out" block between the RAMP and the CE (viewBox widened to 790, router and notes moved 30 px). A new paragraph in #wavelets defines queues: hardware FIFOs bound to a color, with counts, depths (CCN 35, from memcpy.csl comments; input 6/4/2, output 2/6/2) and the WSE-3 task/microthread naming. Depth rows added to the queue table.
- **G4** Fixed. #no-caches: 900k × 44.5 KB ≈ 40 GB usable of the 44 GB headline [Derived]. Explains why weights are streamed (Ch 8 #memoryx) or pinned across wafers with KV in the leftover (Ch 8 #inference, Ch 9 #pipeline).
- **G5** Partly. The sharing claim is softened to "reported, not measured". The quiz answer now says it is a secondary-source claim, and "not 8× FLOPs" is conditioned on it. The 3-way timing experiment was not run; it is effort M, and the earlier attempt stalled.
- **G6** Fixed. #feed: memory is not the f32 FMA limit, since adds and copies go 2–4× faster on the same SRAM, so the limit is the datapath or an undocumented FMA issue rate. What memory *can* do is clash (link to box).
- **G7** Skipped. The start-offset test (effort M, simulator) was not run. The wording now says start placement "may account for it, but that was not tested", and the report accepts this.
- **G8** Fixed. The Try-it box points to Ch 7 #frame and Ch 10 #fabric-size for the 4,1 offset, the +7/+2 fabric, `--memcpy` and `--channels`.

## r3-gaps still open → status
G2 → E1 (fixed). G3 → G1 (fixed). G5 → G5 (partly). G9 → G7 (skipped). G11 → E3 (fixed). G12 → E5 (fixed).

## Cross-page items about Ch 3
- r4-appE E2 (Ch 3 "f16 2.0 on WSE-2"): fixed with E1.
- r4-ch06 (6 KB / 32-bit interleave are Independent, the SDK uses a 16-bit rule): Ch 3 already tags it that way and offers both models. No change needed.
- r4-ch09, r4-ch13, r4-appB mentions are about those pages' own references to Ch 3, which are still valid. Nothing to change here.
- CCN 30 (one rule, retired rates and explanations), 33 (clock), 34 (hop), 35 (queue depth) and 38 (links) applied. 31, 32, 36 and 37 do not touch this page.

## Verification
Playwright at 1100 and 390 px: all widgets driven (journey, bank model toggle, memory map, microthread presets, matvec stepper, sparse encoder). Zero console or page errors, no horizontal overflow. All 85 in-page and cross-page hrefs resolve to existing ids. Screenshots were checked and the scratch was deleted.

## For other pages
- **Ch 6:** CCN 30 names `06-dsds.html#banks` as the canonical home of the placement table. That id does not exist yet, so Ch 3 links `#collisions` and `#op-speed` instead. Retarget once it exists. Ch 6 #collisions still says "@fadds showed no penalty, WSE-2 and WSE-3" and gives the f16 explanation as "memory traffic". Both conflict with CCN 30, since WSE-2 fadds runs at 1,038 at 0 or 4 B and 526 at 8 B.
- **App B:** the warp/f16 row copied Ch 3's old "memory traffic" inference (r3 G2). It should now cite the placement rule.
- **Ch 11:** the explanation "two reads and a write" for f16 is retired by CCN 30.
