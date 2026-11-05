=== r4-appA-fixlog.md
- **All chapters (G5 / note 38):** link the first forward use of these terms to the glossary:
  - cslc, cs_python, cs_readelf, Simulator: Ch 3, used before Ch 10.
  - DSD (`#g-dsd-data-structure-descriptor`) and `@get_dsd` (`#g-get-dsd`): Ch 3, Ch 5.
  - memcpy: Ch 2–5.
  - Tensix, Blackhole, MemoryX: Ch 1.
  - `.ut_id`: Ch 3.
  - TSC (`#g-timestamp-counter-tsc`): Ch 3, Ch 11.
  - SpMV: Ch 5.
- **Labs 11–15 code walkthroughs:** link the CSL identifiers to the new entries: `g-sys-mod`, `g-memcpy-params`, `g-get-color`, `g-get-local-task-id`, `g-get-queue`, `g-get-dsd`, `g-dsd-mutators`, `g-many-item-pointer`, `g-export-symbol`, `g-host-device-loop` (Ch 11, 15), `g-strong-scaling` (Ch 13, 14), `g-fsm-task-lock-task` and `g-ce-ignore` (Ch 14).
- **Ch 1 and Ch 17 "Terms used here" boxes:** add a "Full glossary" link to `appendix-a-glossary.html`.
- **App D:** link the Teaches column to existing entries, and link `topic-NN` to `#g-topic-nn` (r4-appD X4).
- **App E:** link TSC, DSR, input queue, microthread and bank on first use (r4-appE X3). The cb16 row can now move from Unverified to Vendor in App E's list.
- **Ch 6:** when `#banks` is created, App A's bank-clash entry can point there instead of `#collisions`.
=== r4-appB-fixlog.md
- Ch 5, 6, 7, 10 "If you know CUDA" callouts: end each with a link to the matching App B row, e.g. `appendix-b-cuda-to-csl.html#r-wait` / `#r-syncthreads` (Ch 5), `#r-warp` / `#r-loop` / `#r-banks` (Ch 6), `#r-launch` / `#r-memcpy` / `#r-streams` (Ch 7), `#r-kernel` / `#r-grid` (Ch 10).
- Ch 14 #design and Ch 15 #bud: link `appendix-b-cuda-to-csl.html#checker` (now has a program 06 preset) and `#libs-row`.
- Ch 17 (r4-ch17 G6) and Ch 18 (r4-ch18 X5): link `appendix-b-cuda-to-csl.html#rosetta`; for thread-block clusters, `#r-cluster`.
- Ch 14 exercise 3: "Chapter 3's smaller WSE-2 overhead (3.1 vs 4.6 KB)" are matvec figures; SAXPY's are 2.85 / 4.24 KB.
- Ch 6: if `#banks` is created per item 30, App B's links to `06-dsds.html#collisions` can be retargeted to `#banks`.
=== r4-appC-fixlog.md
- **Ch 6 fixer / coordinator:** item 30 names `06-dsds.html#banks` as the canonical home of the bank table, but it does not exist yet. App C links `#collisions` for now. Retarget it to `#banks` once that anchor exists.
- **Ch 11:** the E4 anchor `#inside` and the E5 wording are both already in place. No action.
=== r4-appD-fixlog.md
- **G3 inbound links** (for the fixers of those pages): add a one-line "Next in the SDK → [Appendix D](appendix-d-sdk-index.html#after-chNN)" near the end of Ch 3, 4, 5, 6, 7, 10, 11, 12, 13, 14 and 15, using the ids in the table above. Ch 18 `#next` lists six SDK benchmarks; link it to `appendix-d-sdk-index.html#after-beyond`, or to `#index`.
- Ch 10 (src not applicable; 10 is a top-level page): its library-map row for benchmark-libs could link to `appendix-d-sdk-index.html#run` for the import fix. It already links to `#run` elsewhere, so this is optional.
- Housekeeping, not a page issue: the installed SDK example `tutorials/gemv-01-complete-program/` contains run leftovers (`out/`, `sim.log`, `sim_stats.json`, `simconfig.json`, `simfab_traces`). Someone ran it in place. The coordinator may want to clean it.
=== r4-ch01-fixlog.md
- Ch 2: the WSE-2 "~7.5 PF dense" tag should be Vendor (HC22), per r4-ch08 E4. Ch 1 is now Vendor.
- Ch 6: once `#banks` exists, Ch 1's two "Chapter 6" links (#op-speed) could point there.
- Ch 18: r4-ch18 E4 (Rubin ridge 2,600 without format caveat). Ch 1 now uses the 35 PF dense ridge ≈ 1,800, so Ch 18 should match.
- Roofline widget (cosmetic, Ch 1 only): with WSE-3 selected, the "B200 (FP4)" end label sits close to the new dashed measured roof. It is readable, so I left it.
=== r4-ch02-fixlog.md
- **Ch 6:** note 30 names `#banks` as the canonical anchor for the placement table. It did not exist when I checked, so ch02 links `06-dsds.html#op-speed`. If the Ch 6 fixer adds `#banks`, the link could be retargeted.
- **Ch 7 / Ch 10 / Ch 13 / Ch 18:** these should use the same 750 × 994 caveat (ch02 `#cs2-dims`), per r4-ch10 E3 and r4-ch18 E5.
- **Ch 1:** Ch 1 should use the same CS-3 1.2 Tb/s system-I/O Vendor tag and the measured f16 ≈ 6 PF roof (r4-ch01 G4), so the two pages stay consistent with ch02.
=== r4-ch03-fixlog.md
- **Ch 6:** CCN 30 names `06-dsds.html#banks` as the canonical home of the placement table. That id does not exist yet, so Ch 3 links `#collisions` and `#op-speed` instead. Retarget once it exists. Ch 6 #collisions still says "@fadds showed no penalty, WSE-2 and WSE-3" and gives the f16 explanation as "memory traffic". Both conflict with CCN 30, since WSE-2 fadds runs at 1,038 at 0 or 4 B and 526 at 8 B.
- **App B:** the warp/f16 row copied Ch 3's old "memory traffic" inference (r3 G2). It should now cite the placement rule.
- **Ch 11:** the explanation "two reads and a write" for f16 is retired by CCN 30.
=== r4-ch04-fixlog.md
- **Ch 3 (#wavelets), r4-ch04 G8 / r4-ch03 E3:** change "hop one router per cycle" to "about one cycle per hop on hardware, per papers; the WSE-3 simulator models 2 (Ch 4 #latency)".
- **Ch 12 #broadcast:** can link `04-fabric.html#multicast-stall`. The broadcast runs at the pace of its slowest receiver (measured, see G3).
- **Ch 7 / Ch 11 (r4-ch07 G5, r4-ch11 G7):** for memcpy's RAMP→RAMP route, link `04-fabric.html#ce-half` (router half / CE half) and `#routes`.
- **Ch 2, Ch 12, Ch 17:** new Ch 4 anchors available: `#ce-hop` (9.2/6.0 vs 2.0/1.0), `#try-hops`, `#many-to-one`, `#chk2d-fig`, `#try-switches`.
=== r4-ch05-fixlog.md
- Ch 4 (04-fabric.html #filters, r4-ch04 E4) still says Chapter 5 uses the index field for sparse data. Ch 5 has no such material.
- Ch 12 G5: if Ch 12 maps its measured 16–18 buffer capacity, it should use the per-queue depths 6/4/2 (queue 2 = 4) rather than "~14", which is I/O-path buffering (CCN 35).
=== r4-ch06-fixlog.md
- Ch 3 (#bank-model, #pe-speed), Ch 11, Ch 13 (#numbers-say "we have not isolated why"), Ch 14, Ch 15 (G3 Z table), Ch 17 (E2 strided DSD), App B, App C (G-item on PAD addresses), App E (issues 2/3): state the one-line rule and link `06-dsds.html#banks` (canonical table).
- App E #iss-clash still cites "Ch. 6 … @fadds shows no penalty". That sentence is now scoped: no penalty on WSE-3, and WSE-2 adds need 8 B placement.
- Ch 13 line ~431 says "Chapter 6 measured about 17 cycles to start an isolated op … We have not isolated why". Ch 6 now states both figures. Ch 13 could link `06-dsds.html#op-speed`.
- Gaps worth one experiment by whoever owns App E: fadds and fmach at 12 B, and fmach at the odd-bank offsets (2/6/10/14 B). These cells read "not measured" in the #banks table and widget.
=== r4-ch07-fixlog.md

- **Ch 13 (src/13-lab-stencil.html)**, step card and quiz: "launch(..., nonblock=False) keeps waiting" / "returns only after the last step" are wrong (notes 31). Say "the host's next command waits", and link `07-host-io.html#what-blocks`.
- **Ch 14 / programs/06-summa/pe_program.csl:123**: "only now does the host's launch() return" → "the host's next command can now run" (Ch 14 fixer only).
- **Ch 15 / programs/07-cg/pe_program.csl:115, 217 and the prose** "each launch returns only when its phase has finished" → "each phase's wait sits in the following launch or copy" (Ch 15 fixer only). Link `07-host-io.html#what-blocks`.
- **Ch 12**, step 6: use the same wording and link to `#what-blocks`.
- **Ch 11**: r4-ch11 suggests a line under its call table; link `07-host-io.html#what-blocks`.
- **Ch 2 (lines ~190, 219, 234, 268) and Ch 10 (#source-to-sim, #fabric-size, calculator CS-2 mode, Q3)**: the "743 × 992 at most" bound. The single-tile-matvec README contradicts itself: line 38 says "fabric-dims must be 750,994", but its `sweep.py --dims 750,994` treats 750 × 994 as the rectangle (fabric 757,996). Tag it Unverified there too, as Ch 7 now does.
- **Glossary (App A)**: `g-filter-range-counter` could add "counts up and wraps; passes at 0" so it matches Ch 4/Ch 7.
=== r4-ch08-fixlog.md
- **Ch01** (01-memory-wall.html) roofline table: WSE-2 FP16 dense 7.5 PF -> tag Vendor (HC22), item 36 / r4-ch08 E4.
- **Ch02** (02-the-wafer.html): spec table "~7.5 PF dense Analyst" -> Vendor (HC22); #flops-area text: the 10:1 WSE-2 ratio is vendor-stated, only WSE-3's 8:1 is an analyst assumption (E4). Spec note on WSE-3T clock: Cerebras does attribute it to clock ("twice as much power to the WSE-3 Turbo, enabling higher operating frequencies"; cite Ch08 #cs4) (E5).
- **Ch09**: #budget "Chapter 8 ended with 'the sources do not break this down'" and the experiment box "reproduces Chapter 8's benchmark run (10,160 cycles)" are dangling; reword as self-contained (G6).
- **Ch17**: "(Chapter 8)" pointers for the wafer decode budget should be "Chapters 8–9" (r4-ch17 G1); Ch16 quiz likewise (r4-ch16 G11).
=== r4-ch09-fixlog.md

- **CROSS_CHAPTER_NOTES 2:** still says "No WSE-3 clock is published". Note 33 supersedes it, but item 2 itself should point to 33.
- **Ch 1, Ch 2, Ch 18:** wherever they give the single-user bound or per-second figures from cycles, add the clock: ~2,000–4,000 tok/s at 850 MHz, ~3,300–6,600 at the ~1.4 GHz press estimate (Ch 9 `#ceilings`).
- **Ch 18 (r4-ch18 G2):** Ch 9 now states the context dependence: ~13 users at 8K versus ~50–100 at 1–2K. Ch 18's KV-cap widget could link `09-model-to-tokens.html#ceilings` or `#pipeline`.
- **Ch 8 (r4-ch08 E6):** the CS-4 ">4,400 tok/s on gpt-oss-120B" claim is used by Ch 9 #history (Vendor, "not independently measured"). Ch 8 #cs4 should carry it too, with a `tag unv`.
- **Ch 12 (r4-ch12 G1):** link back to `09-model-to-tokens.html#budget`. Ch 9 now links Ch 12 `#composing` as the 2-D GEMV the region model uses.
- **App A (r4-appA G6):** the KV-cache entry can link `09-model-to-tokens.html#pipeline` for the 13 / 7 user limit.
=== r4-ch10-fixlog.md
- **Ch 2** (lines ~190, 219, 234, 268) and **Ch 7** (frame calculator and ~line 106): the CS-2 "750 × 994 fabric / ≤ 743 × 992" needs the same caveat. The README calls 750,994 the fabric, but its sweep.py treats it as the program rectangle (fabric 757,996). Tag it Unverified or footnote it (r4-ch02 E4 and r4-ch10 E3). Ch 13 and Ch 18 reuse 743 × 992.
- **Appendix D** E2: the benchmark-libs row filter should include Ch 10 for preconditioned-conjugate-gradient, bicgstab and power-method.
- **Ch 11** X6: link the "exported symbol mutability mismatch" row with `10-csl-toolchain.html#errors`. New anchors on this page that other pages can link to: `#task-syntax`, `#tsc`, `#sdklayout-03`.
- **Glossary**: there are no ids for ELF or CTF, so consider adding them.
=== r4-ch11-fixlog.md
- Ch 6 (06-dsds.html): once the `#banks` anchor exists, Ch 11's two links to `06-dsds.html#collisions` could point there. Ch 6 also has the "interleaved by 32-bit word [Vendor]" mis-tag (r4 E4).
- App C: link "What happens inside" to `11-lab-first-programs.html#inside` (the anchor now exists).
- Program comments in `programs/01-saxpy/timed/{layout,pe_program}.csl` say "PAD extra words"; PAD is in elements of T. Comment-only fix; no fixer owns 01-saxpy, so the coordinator should decide.
=== r4-ch12-fixlog.md
- Ch 14 (#next aside): it quotes "Chapter 12 measured store-and-forward at >3×". Still true. That page could link to `12-lab-neighbours.html#streaming`, which now shows the store-and-forward code.
- Ch 4 (#back-pressure hint): "real depths are not published" contradicts CCN 35. It should cite the memcpy.csl depths (iq 6/4/2, oq 2/6/2), as this page now does.
- Ch 5 (quiz at "stalls past 14"): it has no anchor, so this page links only to the top of 05-tasks.html. An id there would let it deep-link.
- App B (hop row): could use this page's fit form M + c·(P − 1) + fixed, per r4-appB.
=== r4-ch13-fixlog.md
- **05-tasks.html** (§When several tasks are ready): "Lab 3's measured ~88 fixed cycles per step" should be ~90 (90.2 + 2.5·n). Point to `13-lab-stencil.html#fixed-cost` for the 14.6-per-transfer split. My new text links to `05-tasks.html#priority` and says Ch 5 uses the ≈90.
- **06-dsds.html**: line ~204 still credits "WSE-3 doubled … adds" as the reason Lab 3 is a wash. Per CCN 30 it should cite placement. This page links `06-dsds.html#collisions` for the bank rule. If the Ch 6 fixer adds `#banks`, these links could be retargeted (they work as they are).
- **appendix-a-glossary.html**: consider entries for "ghost cell" (alias of g-halo), "Dirichlet boundary" and "strong scaling" (r4-appA also asks for strong scaling).
- **appendix-d-sdk-index.html**: the bicgstab row has 13 in its filter. The Where cell could link `13-lab-stencil.html#sdk-stencils` (the CS-1 BiCGSTAB caveat is in "Scaling up").
=== r4-ch15-fixlog.md
- appendix-e-sources.html: the Ch 15 Unverified row ("Chapter 18 cites the SC20 BiCGStab … could not check that paper's allreduce latency") is stale. The sentence is gone and the claim is now tagged Indep, so the row and its text-fragment link need updating or removing.
- appendix-b-cuda-to-csl.html: once #checker exists, Ch 15's budget widget could link to it.
- 06-dsds.html: if the Ch 6 fixer adds #banks (item 30), Ch 15's two links to #collisions could point there.
- 18-comparison.html: its SC20 lesson can now cite Ch 15's comparison (#scaling, about 1,300–1,400 vs about 90,000 cycles per call).
=== r4-ch16-fixlog.md
- **Ch 1 (01-memory-wall.html), bound table, Wormhole Galaxy row:** change "≈ 130" to "≈ 124" (74 GB in BFP8 incl. shared exponents, 8.1 ms per pass) to match Ch 16 and Ch 18 (= r4-ch01 E5). Ch 1 quiz Q2 also says "1.4 MiB-per-core"; it should be 1.5 MiB (1,536 KiB).
- **Ch 3 (#pe-speed)** still says "f16 reaches about 3.2 per cycle on WSE-3 and 2.0 on WSE-2", with the "memory traffic" explanation that CCN 30 retires. Ch 16 now quotes ≈ 4/cycle with well-placed operands and links Ch 3 #pe-speed and Ch 6 #op-speed. If Ch 6 creates `#banks`, the Ch 16 link could point there.
- **App E row for the Ch 16 DeepSeek-R1 figure:** upgrade it from "press extracts" to the TT-Deploy post (r3 G3).
=== r4-ch17-fixlog.md
- **Ch 18 #limits / LPX paragraph:** "no independent LPX decode measurement exists yet" is now dated. NVIDIA cites Artificial Analysis at ~3,400 tok/s on Gemma 4 31B at 100K context (Hot Chips, Aug 2026), and LPX is in full production. Ch 18 should also say "Rubin shipping (CoreWeave, 30 Sep 2026)".
- **Ch 18 "Back to the memory wall":** "the ridge still climbs (295 → ~2,600 FLOP/byte from H100 to Rubin)" compares BF16 with NVFP4. At equal precision the ridge is roughly flat (see Ch 17 E1).
- **Ch 9 #moe:** it says "22 TB/s of HBM4 per Rubin GPU". The current spec is 19.2, and Ch 9 also still hedges "one report says 128" (now settled as 256).
- **App E:** retag rows for Megatron (Indep), setmaxnreg 40/232 and TMEM 256 KB (Vendor, CUTLASS source), and 67 TF (Vendor datasheet). Add rows for the Rubin BF16 ~4 PF [Unverified, flopper.io], the B300 specs, LPX full production and the AA ~3,400 tok/s figure, and the 70–80% GEMM efficiency [Unverified].
- **App A:** a "Rubin CPX" entry and a "PTX / CUTLASS" entry are still missing (App A G3). This page links its terms there once those entries exist.
=== r4-ch18-fixlog.md
- **Ch 15** (`15-lab-cg.html#scaling`): it says "we could not check that paper's allreduce latency". The SC20 figure (<1.5 µs on ~380k PEs, search extract) is now quoted in Ch 18; Ch 15 could cite it the same way. Ch 15 also uses 950 × 950 ≈ 900k as "whole wafer" while Ch 13/18 use CS-2's 737k. One convention ("CS-2 737k SDK-visible; CS-3 unpublished, ~900k") would help.
- **Ch 17**: B300 (288 GB) is still missing (r3 G5). The LPX "256 … 128 … not settled" hedge should match Ch 18 (256, ~128 GB, ~40 PB/s, in production).
- **Ch 1**: it compares H100 BF16 with Rubin NVFP4 ridge. That page already has the caveat; no change needed.
- **README.md**: r3 G11 (cycle table vs expected_output, noise caveat, Unverified tag, App E pointer) is still open.
- **Rubin status**: Ch 18's compare and chooser widgets label Rubin "(announced)", following Ch 17. r3 says Rubin ships in late 2026. If Ch 17 changes this, Ch 18's labels should follow.
