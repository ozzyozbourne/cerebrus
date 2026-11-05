# Round-4 cross-page sweep, part B

Pages covered: 08, 09, 10, 11–13 and 15 (src, rebuilt with tools/build.py), 16, 17, 18, index, App A–D, README.md, programs/01-saxpy/timed comments.
Verified in Playwright at 1100 px: 08, 09, 10, 11, 12, 13, 15, 16, 17, 18, index, App A, B, C, D. All have zero console errors, and every local link and anchor resolves. I also checked the glossary search for the new entries and the Ch 18 widget labels.

## Requests from R4_OTHER_PAGES.md

### App A (from the App A fixlog and other fixlogs)
- Lab glossary links for CSL identifiers: **Done.**
  - Ch 11: `g-sys-mod`, `g-get-color`, `g-initialize-queue`, `g-export-symbol`, `g-many-item-pointer`.
  - Ch 12: `g-initialize-queue`, `g-local-task`.
  - Ch 13: `g-get-queue`, `g-dsd-mutators`, `g-strong-scaling`, `g-ghost-cell`, `g-dirichlet-boundary`.
  - Ch 15: `g-sys-mod`, `g-host-device-loop`.
  - Ch 11 has no host/device-loop passage, so `g-host-device-loop` is linked only in Ch 15. The other identifiers appear only inside code listings on those pages, so they are not linked.
- Ch 17 "Terms used here" box with a "Full glossary" link: **Partly done.** Ch 17 has no such box. I added a one-line "full glossary" pointer under its objectives.
- App D: Teaches column linked to the glossary: **Already done** (the GL list in the page script). `topic-NN` linked to `#g-topic-nn`: **Done** (in the anatomy paragraph).
- App A bank-clash and bank entries, and the fp16 row: **Done.** All three now link `06-dsds.html#banks`. The bank-clash entry also gains the f32 `@fadds` placement figures (CCN 30).
- `g-filter-range-counter`: **Done.** It now says the counter counts up, wraps at its limit and passes the wavelet at 0, matching Ch 7.
- KV-cache entry linked to `09#pipeline`: **Already done.**
- Rubin CPX and PTX/CUTLASS entries: **Already done** (`g-rubin-cpx`, `g-ptx-cutlass`).
- ELF and CTF (r4-ch10): **Done.** Added `g-elf` and `g-ctf-trace`.
  - The CTF expansion ("Common Trace Format") is tagged Unverified, because the SDK never expands the name.
  - Ch 10 now links ELF on first use.
- Ghost cell, Dirichlet boundary, strong scaling (r4-ch13): **Done.** Added `g-ghost-cell` and `g-dirichlet-boundary`. `g-strong-scaling` already existed.
- "Tokens/s" entry: **Done.** The 2,000–4,000 range is now labelled 850 MHz, with ~3,300–6,600 at the ~1.4 GHz press estimate and a link to `09#ceilings`.

### App B
- Ch 10 "If you know CUDA" callout linked to `#r-kernel` / `#r-grid`: **Done.**
- Ch 15 `#bud` linked to `#checker` and `#libs-row`: **Done.**
- Ch 17 linked to `#rosetta`: **Already done.** Ch 17 linked to `#r-cluster`: **Done** (the distributed-shared-memory sentence).
- Ch 18 linked to `#rosetta`: **Already done.** Ch 18 `#r-cluster`: **Skipped.** Ch 18 never mentions clusters.
- App B links to `#collisions` / `#op-speed` that are really about the placement rule: **Done.** Six links now point to `#banks`. The warp, bank, `@fadds`, `@fmacs`, f16 and clash rows plus the intro all state the one rule.
- App B warp/f16 row "memory traffic": **Already done.** The row cites placement.
- App B hop row in the fit form M + c·(P − 1) + fixed: **Already done.**
  - Also fixed the "buffering per hop" row, which said ≈16. Ch 12 now measures ≈18 (6 in the output queue, 4 in the input queue, the rest in the router).

### App C
- `#collisions` → `#banks`: **Done.** It also states "peak needs opposite halves".
- Link to "What happens inside" (`11#inside`): **Already done.**
- PAD addresses (r4-ch06): **Done.** PAD is now described as elements of T: 32-bit words for f32, 2 B each with HALF = 1.

### App D
- Inbound "Next in the SDK → Appendix D" lines:
  - Ch 10, 11, 12, 13, 15 (`#after-chNN`): **Done.**
  - Ch 18 `#next` (`#after-beyond`): **Done.**
- benchmark-libs row filters include Ch 10 (PCG, bicgstab, power-method): **Already done.**
- bicgstab Where cell linked to `13#sdk-stencils`: **Already done.**
- Ch 10 library map linked to `#run`: **Already done** (this item was optional).
- Housekeeping of the gemv-01 run leftovers: **Skipped.** It is coordinator-only and outside the course.

### CS-2 750 × 994 / 743 × 992 caveat (r4-ch02, ch07, ch10)
- Ch 10: **Done.** The `#fabric-size` text links `02#cs2-dims`. Its Q3 already hedges.
- Ch 13 (Scaling up): **Done.** Added the 745,500 alternative reading (Unverified) and the Ch 2 link.
- Ch 15: **Done.** Ch 2 link added.
- Ch 18: **Done.** Ch 2 link added.
- App B: **Done.** Both places now carry the caveat and the link.

### Ch 8
- `#cs4` ">4,400 tok/s" with a `tag unv`: **Already done.**

### Ch 9
- `#budget` and the experiment box no longer depend on Ch 8 (r4-ch08 G6): **Already done.**
- `#moe` said "22 TB/s" and "one report says 128": **Done.** It now gives 19.2 TB/s (22 at announcement) and 256 LPUs with ~128 GB SRAM, says the single "128 LPUs" report is an error, and links `17#groq-lpx`.
- Bank links: **Done.** Two `#op-speed` links that are about placement now point to `#banks`.

### Ch 10
- See App B, App D and CS-2 above.
- `#banks`: **Already done.**

### Ch 11
- `#collisions` → `#banks`: **Done.** Also replaced "how addresses map to banks is not vendor-documented" with the SDK's 16-byte rule (the physical width is still unpublished).
- "Two reads and a write": **Already done** (the phrase is gone).
- `04#ce-half` for memcpy's RAMP→RAMP route: **Done.** `#routes` was already linked.
- `07#what-blocks` under the call table: **Done.**
- X6 "mutability mismatch" row linked to `10#errors`: **Already done.**
- The PAD comments in `programs/01-saxpy/timed/{layout,pe_program}.csl` now say "elements of T": **Done.** These are comment-only edits, and I rebuilt the pages.

### Ch 12
- `#broadcast` linked to `04#multicast-stall`: **Done.** Added a sentence that a multicast runs at its slowest receiver's pace.
- G5 per-queue depths: **Already done.** The page uses iq 4 and oq 6, not ~14.
- Step 6 launch wording and `#what-blocks` link: **Done.** The wording was already correct, so only the link was added.
- Link back to `09#budget`: **Already done.**
- `#collisions` → `#banks`: **Done.**
- Coordinator extra: the Ch 5 "stalls past 14" link now points to `05-tasks.html#blocking`: **Done.**

### Ch 13
- Launch wording: **Already done.** Added the `07#what-blocks` link.
- Bank links: **Done.** Four `#collisions` links and the placement-split `#op-speed` link now point to `#banks`.
- "Chapter 6 measured about 17 cycles … We have not isolated why": **Done.** The sentence now gives both Ch 6 figures: 15–17 cycles isolated (including the timestamp reads) and ~6 for consecutive ops.
- Glossary links: see App A.
- 750 × 994 caveat: see the CS-2 section.

### Ch 15
- `#collisions` → `#banks` (2 links): **Done.**
- Launch wording ("each phase's wait sits in the following launch or copy") and the `07#what-blocks` link: **Done.**
- SC20 allreduce latency cited as in Ch 18: **Already done** (`#scaling`, Indep, SC20).
- 950 × 950 convention: **Already done.** The page states that the CS-3 fabric is unpublished (~900k) and that CS-2 has 737k SDK-visible PEs. I added the Ch 2 caveat link.
- App B checker and libs-row links: **Done.**

### Ch 16
- Quiz "(Chapter 8)": **Already done** (it links Ch 8 and Ch 9).
- Clock label on 2,000–4,000: **Done.**
- `#op-speed` → `#banks` for well-placed f16: **Done.**

### Ch 17
- The "(Chapter 8)" pointers for the decode budget: **Already done.** The page links Ch 8 and Ch 9.
- B300 and the LPX hedge: **Already done.**
- E2 strided-DSD bank rule: **Already done** (`#banks`).
- f16 rate link `#op-speed` → `#banks`: **Done.**

### Ch 18
- E4/X ridge "295 → ~2,600" (BF16 vs NVFP4): **Done.** The text now gives 295 → ~1,800 dense NVFP4 and says the ridge is roughly flat at equal precision (B200 BF16 ≈ 281), matching Ch 1.
- LPX "no independent measurement": **Already done** (the AA 3,431 figure is there).
- Rubin shipping: **Done.** Added a CoreWeave 30 Sep 2026 sentence. The compare and chooser widget labels changed from "(announced)" to "(shipping)", following Ch 17.
- Clock labelling: **Done.** The decode prose shows 850 MHz plus the ~3,300–6,600 at ~1.4 GHz range and links `09#ceilings`. The band hint, the limits table, the chooser note, the roofline readout and the quiz now say 850 MHz.
- KV-cap widget link: **Already done** (`09#pipeline`). The chooser note now also links `09#ceilings`.
- SC20 lesson citing Ch 15 `#scaling`: **Already done.**
- `#op-speed` → `#banks` for the per-op rates: **Done.**
- `#next` linked to App D `#after-beyond`: **Done.**

### README.md (r3 G11)
- **Done.** The changes:
  - Cycle table copied from `expected_output.txt` (6,861; 11,666; 36,959; 145,166).
  - Whole-run noise caveat added, pointing to TSC and App C.
  - Unverified added to the tag list.
  - App E pointer added.

### index.html
- No affected content found: no tok/s ranges, no CS-2 dims, no bank links. **No change.**

## Sweep checks (brief items 2–5) on my pages
- Retired rates and explanations: I grepped all my pages for "3.2/cycle", "2.0 on WSE-2", "memory traffic", "two reads and a write", "doubles f16" and an unscoped "no penalty". None remain unscoped.
- Remaining `06-dsds.html#op-speed` links are about op speed in general:
  - start-up cost: Ch 13, Ch 15
  - one f32 MAC per cycle: Ch 15
  - one-source f16 move: Ch 11
  - fmovs and fixed start-up rows: App B
