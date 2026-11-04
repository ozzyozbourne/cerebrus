# Fix log: Appendix A (glossary and number formats), round 2

Only `course/appendix-a-glossary.html` was edited. The glossary now has 176 entries (up from 131). All 325 internal links resolve: a script checked every file and id. Link labels now match the titles of the headings they point to.

## Accuracy (r2-appA-accuracy.md)

**A1 (smallest CSL integer type): fixed.**
- Compiled in `/home/user/cerebras-sdk/tmp/fix2-appA` (since deleted) with cslc 2.10.1, `--arch=wse2` and `wse3`:
  - A live task using `var a: [4]i8`, `var b: u8` and `var c: i64` compiles on both chips. `cs_readelf --sym` shows `a` as 4 bytes and `c` as 8 bytes.
  - A `mem1d_dsd` over an `i8` array fails with `error: type 'i8' is not ABI-sized`, whether the op is `@mov16`, `@add16` or `@mov32`.
- Support-table int8 row: "CSL has i8/u8 scalars and arrays, but its DSD (vector) builtins start at 16 bits ... [Measured]; no CSL route to the INT8 SIMD is documented [SDK]". The WSE-2 cell now reads "i8/u8 scalars only".
- Format table: the int8 row now names CSL i8/u8 … i64/u64.
- Explorer option renamed "int8 (CSL i8)".
- New entry: int8 / i8, u8.

**A2 (`--fp16-format` wording): fixed.** The entry quotes the cslc-driver help text and adds the measured result: with bf16/cb16, run-time f16 fails to compile and constants stay IEEE half. It links to #cslc-f16.

**A3 (microthreads attribution): fixed.** The CE entry now says that the GPR/DSR/SIMD figures are WSE-3's and that "8 microthreads" is a WSE-2 vendor statement.

**A4 (B200 BF16 tag): fixed.**
- New text: "≈ 2.25 PF dense (4.5 PF with 2:4 sparsity) [Vendor, HGX B200 spec via search extract]".
- Sources: NVIDIA's HGX table gives 36 PF sparse for 8 GPUs, and Lenovo's B200 guide gives 2.25 / 4.5 PF.

**A5 (NVFP4 scale never rounds): fixed.**
- The per-tensor FP32 scale now comes from a notional tensor whose maximum is 3× the block's, or the outlier if that is larger.
- Without the outlier, the E4M3 block scale is now visibly rounded (for example 149.3 → 144), and the readout prints it.

**A6 (BlockFP8 clamp): explained.** The note now says that a block maximum just under a power of two rounds up to 128 steps and is clamped to 127, and that real packers may bump the exponent instead.

**R1 / P1 (Ch 9, 14, 15, 18, App C/D missing): fixed.**
- New entries:
  - Ch 14: SUMMA, outer product.
  - Ch 15: allreduce, SpMV, CG, residual, preconditioner (PCG), pencil decomposition, module composition.
  - Ch 9: speculative decoding, draft/target model, acceptance rate α, draft cost c, MoE, TTFT, tokens/s per user vs aggregate (with the one-user and pipe-full ceilings), disaggregated inference, AFD, compile path, LAIR.
  - Ch 18: cost per million tokens, Groq LPU/LPX, TPU.
  - App C: sim.log / sim_stats.json.
- New second links on existing entries:
  - Join → 14#join
  - `<collectives_2d>` → 14#collectives (text updated: per-call route rewrite)
  - Pinned-weight → 09#pipeline, #targets
  - Layer-pipelined → 09#targets
  - KV cache → 09#pipeline (the 327,680 B arithmetic is in that section, not #budget; text updated)
  - Decode/prefill → 09#budget, #moe
  - Dataflow sparsity and Dense/sparse → 09#sparsity
  - Weak scaling → 15#scaling
  - TSC → App C #tsc (text: enable_tsc zeroes the counter; an empty region reads 10 cycles)
  - Instruction trace → App C #trace
  - Simulator → App C #three
  - GEMV/GEMM → 14#summa, 09#budget
  - TP/PP/DP → 09#pipeline
  - Stencil → 15#problem
  - Teardown and Switch → 15#allreduce
  - Multicast → 14#collectives
  - Bank clash → 14#measure
- The lede no longer says "Every … term".
- Category counts are computed live, so they need no edit.

**R2 / P2 (format names not searchable): fixed.**
- New entries: fp32, fp16, bf16, cb16, FP8 (E4M3, E5M2), FP4 (E2M1) / NVFP4, MXFP4, BlockFP8 (bfloat8_b) / bfloat4_b, Subnormal, and "Exponent, mantissa, bias".
- Each links to #formats, #bx, #blocks, #cslc-f16 or #support.
- The "No term matches" message now links to Number formats and to App D.

**R3 (other missing terms): fixed.**
- New entries: Corner turn, Spare cores and redundancy, Yield (cross-reference), tile_config, sim.log / sim_stats.json, .ut_id, @set_color_config, @initialize_queue, WSE-1 / CS-1, TT-Fabric / CCL.
- `fabin_dsd`/`fabout_dsd` were already found by search through the Fabric DSD entry, so I left them as aliases.

**R4 (link labels): fixed.**
- Ch 5 #rules links now use the full heading title.
- Dense/sparse → "Ch. 17, Three generations".
- Microthread → "WSE-2 versus WSE-3: the biggest portability hazard", plus "Budget check (the Lab 3 hang)".
- Task picker also links 05#picker.
- A label-vs-heading script reports no mismatches, apart from App C's "1 ·/2 ·/3 ·" numbering prefixes, which the labels omit on purpose.

**R5 (A–Z bar): fixed.** Added "Virtual channel" (V) and "Yield" (Y). The letter bar is generated from the entries, so only X and Z are now off.

## Visuals and usability (r2-appA-visuals.md)

**V1 (fp32 max/next round-trip): fixed.**
- "largest" and "next value up" now set the bit code directly.
- The text box shows the shortest decimal that encodes back to exactly that code, so the box never moves the bits. Bit flips use the same path.
- Verified:
  - fp32 max = 0x7F7FFFFF, "stored exactly".
  - 1e-6: 0x358637BD → BE → BF.
  - 12345678: …4E → 4F → 50.
  - bf16, cb16 and fp16 max: exact.

**V2 (bit-layout figure): fixed.**
- Field labels now sit above each field and always give letter plus width (S, E8, M23, E2, M1, "8 integer bits").
- Block scales are drawn at 8 × cw (to scale).
- NVFP4 has a dashed "+ FP32 per tensor" chip.
- Each block note is split onto two lines.
- The caption now states what is to scale.

**P3 (outlier result not explained): fixed.**
- The readout explains each case with the outlier on: bf16 is unaffected, E4M3 keeps a per-value exponent, and block formats share the exponent.
- The #blocks prose now says why per-tensor E4M3 beats the block formats here, and that real block formats confine the damage to one block.

**V3 (chart hides the small values): fixed.**
- New "zoom to the 15 ordinary values" switch (on by default; enabled only with the outlier).
- When zoomed, the outlier bar is clipped and marked with an amber arrow and "x → stored (off scale)".

**P4 (phone scrolling and tap targets): fixed.**
- At ≤680 px the inner scroll box is removed and the page scrolls.
- The search box and letter bar form a sticky header under the top bar. Its offset is measured from `.topbar`.
- The letter bar is a single horizontally scrollable row with 28 × 28 px targets.
- `.widget#gl` overrides course.css's phone `overflow-x:auto`, which otherwise stops the header from sticking.
- Letter, hash and in-entry `#g-…` links scroll with that offset.

**V4 (Inf/NaN broke the explorer): fixed.**
- The input accepts inf, infinity, -inf and nan.
- NaN in a format without NaN (E2M1, ints) resets to 0, with a message.

**V5 (edge messages): fixed.**
- Integers: "integers have no fraction: it rounds to the nearest integer, 0".
- inf in E4M3/E2M1: saturation line. inf in ints: clamp line. inf in IEEE formats: explanation of the encoding.
- "next value up" at the maximum: "already the largest finite value", in all 9 formats.

**V6 (chip contrast): fixed.**
- In light mode, Cerebras chips now use #9a3412 and Tenstorrent chips #14532d, both above 6:1 on their soft backgrounds.
- Dark mode is unchanged.
- Chips are now 11 px.

**V7 (smaller issues): fixed except one.**
- Added `dd code { overflow-wrap:anywhere }`.
- Shorter placeholder.
- Added `#gl` scroll-margin, and the hash link scrolls below the top bar.
- Search matches the start of words, and when the only match is a hidden keyword the entry shows "Matched keyword: …".
- Outlier label is now "≈ 40× the typical value" (0.8 against σ = 0.02).
- Not fixed: the wide `#fmt-svg` still scrolls inside its figure at 390 px, as the coordinator's phone policy allows.

**P5 (no chapter links into the glossary):** I cannot do this from this file. See below.

## Coordinator's extra request
- Added LAIR, AFD and "Draft cost c" from the current 09-model-to-tokens.html.
- Updated the Speculative decoding entry to Ch 9's current figures: about 1.4× per user at c ≈ 0.35, and speculation costs the system throughput only when the pipe is full.

## Validation
- Playwright at 1100 and 390 px, light and dark, plus the ◐ toggle: no page or console errors, and no horizontal page overflow.
- Driven:
  - 20 searches, all chips and letters, hash and in-entry links.
  - All 9 explorer formats × 8 presets, plus bit flips, inf/nan, bad input, and next-at-max.
  - All 6 quantiser formats with the outlier and zoom on and off, plus "New random block".
- Screenshots were inspected. One overlap (the off-scale label on the legend) was found and fixed.
- The scratch directory has been deleted.

## For the coordinator
1. **Ch 10 #language type list** (10-csl-toolchain.html) lists only i16/i32/u16/u32. Add `i8`/`u8` and `i64`/`u64`, and note that DSD ops need 16- or 32-bit element types (an `i8` DSD fails with "type 'i8' is not ABI-sized", cslc 2.10.1, both chips). Grep other chapters for "smallest CSL integer" wording.
2. **B200 BF16 tag in Ch 17 (#generations table) and Ch 18** (callout, roofline data): both still say "Derived from 9 PF FP4". NVIDIA's HGX B200 table (36 PF sparse BF16 per 8 GPUs) and Lenovo's B200 guide (2.25 / 4.5 PF) make this a Vendor figure. Retag both pages to match App A.
3. **P5, links into the glossary:** link the first use of key terms (wavelet, color, DSD, microthread, task ID, CB, Tensix, SUMMA, allreduce) to `appendix-a-glossary.html#g-…`, or add a "Glossary" link to the course.js top bar. The ids are stable: `g-` plus the slugged term, for example `g-wavelet`, `g-summa`, `g-allreduce`, `g-ut-id`.
4. The new links into 09, 14, 15, 18 and App C/D use ids that existed when I checked. If those pages' fixers rename `#spec`, `#moe`, `#budget`, `#pipeline`, `#summa`, `#join`, `#collectives`, `#measure`, `#problem`, `#mapping`, `#modules`, `#allreduce`, `#scaling`, `#profile`, `#dc`, `#sram-chips`, `#other-designs`, `#cost`, `#three`, `#whole`, `#tsc`, `#trace` or appendix-d `#index`, re-run a link check on App A.
