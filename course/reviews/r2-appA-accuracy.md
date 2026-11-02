# Review round 2: Appendix A (glossary and number formats), accuracy + reference

Reviewer scope: every definition (131 entries), the format table, the bit-layout SVG, the explorer and quantiser code, the support table, and all internal links.
Method:
- Resolved all 196 internal links with a script and printed each target heading.
- Cross-checked each entry against the chapter it links to, CROSS_CHAPTER_NOTES 1–25, `cs_readelf --help` and `cslc-driver --help`.
- Recomputed every row of the range table.
- Read the `encode`/`decode`/`blockExp`/NVFP4/MXFP4 code.
- Compiled two small CSL tests with cslc 2.10.1 on both arches in a scratch dir, since deleted.

Overall: the content is strong. Every link resolves, and every numeric claim I checked matches its chapter and the notes (KV 327,680 B, hops 2.0/1.0 and 9.2/6.0, queues 8/6 and 8/8, colors 20–23, control IDs 33–37 and 40, Blackhole at 120 cores after the Feb 2026 firmware update, flits, fidelity, and others). The format arithmetic is correct. The issues are one false SDK claim, a gap for the three new chapters, and some imprecise links and wording.

## Findings

**A1 (high): "the smallest CSL integer type is 16-bit [SDK]" is false.** Location: #support table, int8 row, WSE-3 cell (line 345).
- Evidence: the CSL stdlib `types.csl` handles `i8`/`u8` (`byte_size_of` returns 1) and also `i64`/`u64`.
- Measured: a PE program with `var a: [4]i8`, `var b: u8` and `var c: i64` compiles under cslc 2.10.1 for both `--arch=wse2` and `--arch=wse3`. `cs_readelf --sym` shows `b` as a 1-byte object.
- What is true: the stdlib word helpers note "currently only support ≥16-bit primitive types", and the DSD builtins have 16-bit and 32-bit forms (@add16, @mov16, @mov32), with no 8-bit vector op found.
- Fix: "CSL has i8/u8 scalars, but its DSD (vector) builtins start at 16-bit; no CSL route to the INT8 SIMD is documented [SDK]".
- Also check the explorer label "int8" and the format-table row "int8 / i16 / i32", which cite Ch. 10's type list. Add i8/u8 (and i64/u64) wherever Ch. 10 lists CSL types.

**R1 (high): Chapters 9, 14 and 15 are missing from the glossary.**
- No entry links to 09-model-to-tokens, 14-lab-gemm or 15-lab-cg.
- Undefined terms, with how often the chapters use them: SUMMA (28), allreduce (85), SpMV (51), conjugate gradient / CG, residual, speculative decoding (16), mixture-of-experts / MoE (12), TTFT (5), tokens/s, and outer product.
- Fix: add entries that link to 14#summa, 14#join, 15#problem, 15#allreduce, 15#mapping, 09#spec, 09#moe, 09#budget and 09#pipeline.
- Also add the new chapters as second links on existing entries:
  - Join: 14#join
  - `<collectives_2d>`: 14#collectives
  - Pinned-weight inference and Layer-pipelined: 09#pipeline, 09#compile
  - KV cache: 09#budget, which holds the 327,680 B arithmetic
  - Dataflow sparsity: 09#sparsity
  - Weak scaling: 15#scaling

**R2 (med): The format names in the number-formats section cannot be found with the glossary search.**
- Typing NVFP4, bfloat16, bf16, FP8, E4M3, MXFP4, BlockFP8, bfloat8_b, cb16 or "subnormal" returns "No term matches".
- The search only covers `#gl-list`, and none of these has an entry, even though the page defines all of them below.
- Fix: add short entries (General / GPU / Tenstorrent categories) that link to `#formats`, `#blocks` and `#bx`.

**R3 (med): Several often-used terms have no entry.**
- Corner turn (Ch. 4 #routes).
- Spare cores and redundancy / yield (Ch. 2, 33 uses of "spare").
- `@set_color_config`, `@initialize_queue` and `fabin_dsd`/`fabout_dsd` are mentioned only inside other entries. Searching finds them, but they are not entries of their own.
- `tile_config` (Ch. 5 #priority, 11 uses).
- `sim.log` / `sim_stats.json`, which the Simulator entry mentions but does not define.
- `.ut_id` (WSE-3 microthread choice), which is only inside the Microthread entry.
- WSE-1 / CS-1 (Ch. 2, Ch. 8).
- TT-Fabric / CCL (Ch. 16).
- Fix: add entries, or add these as aliases in the matching entries' `data-q`.

**A2 (med): The `--fp16-format` entry overstates what the flag does.** Location: g-fp16-format.
- The entry says the flag "chooses what CSL's f16 type means".
- The page's own measurement, which I re-ran on both arches, shows that with bf16 or cb16 every run-time f16 variable fails to compile ("variable of type '[16]f16' must be comptime-known"). Comptime constants are unchanged.
- `cslc-driver --help` words it as "Choose the runtime FP16 format. Default=f16 … =cb16 Cerebras float16 … =bf16 Brain float16".
- Fix: quote the help text, and add "in SDK 2.10.1, choosing bf16/cb16 makes run-time f16 arrays fail to compile (measured, see #cslc-f16)".

**A3 (low): The CE entry tags "8 microthreads" as a WSE-3 figure.**
- The entry says "16 GPRs, 48 DSRs, … 8 microthreads (WSE-3 figures)".
- Ch. 3 says "eight microthreads" is a WSE-2 vendor statement. GPRs, DSRs and SIMD are the HC2024 WSE-3 figures.
- Fix: "(GPR/DSR counts: WSE-3; 8 microthreads: WSE-2 vendor statement, same count used on WSE-3)".

**A4 (low): Wrong tag on B200 BF16 in the support table.**
- The table says "B200 ≈ 2.25 PF [Derived from FP4]". NVIDIA publishes about 2.25 PF dense BF16 per B200 (HGX B200), so this is a vendor figure.
- The tag copies Ch. 17, so it is consistent, but both pages could switch to Vendor (Unverified if the datasheet cannot be fetched).
- Severity is low because the derivation happens to give the right number.

**A5 (low): The NVFP4 quantiser model hides the effect of rounding the E4M3 scale.** Location: #bq code, `nvfp4`.
- The per-tensor scale is computed from the same 16-value block (t = amax/(6·448)), so the block scale is always exactly 448 and E4M3 rounding of the scale never shows.
- This is acceptable as a model, but the readout claims "an E4M3 scale per 16".
- Fix: compute t from a fixed notional tensor amax (for example 4× the block amax, or the no-outlier block). Alternatively, say in the note that block = tensor here, so the scale is exact.

**A6 (low): The BlockFP8 model clamps the top value.** Location: `blockExp`.
- step = 2^(floor(log2 a) − 6) and top = 127. A block maximum just under 2^(k+1) rounds to 128 and is clamped to 127, which looks like a small error in the largest value.
- Real TT packing has the same edge case or bumps the exponent, so this is acceptable. One sentence in the note would stop learners from thinking it is a bug.

**R4 (low): Some link labels do not match their targets.**
- "Ch. 5, Blocking" and "Ch. 5, Run to completion" go to #rules ("What the hardware stores, and the rules that follow"). The text is there, but the label suggests a heading that does not exist.
- "Ch. 17, number formats" goes to #generations ("Three generations").
- Microthread's "Ch. 5, A real hang" goes to #portability ("WSE-2 versus WSE-3: the biggest portability hazard").
- Task picker should also link 05#picker.
- Fix: use the target headings' real titles.

**R5 (low): A–Z bar.** V, X, Y and Z have no entries. That is fine, but adding "Virtual channel → see Color" would give V a target and help CUDA/NoC readers who search for that phrase.

## Verified correct (no action)
- Range table, all rows recomputed:
  - fp16: 65,504 / 6.10e-5 / 9.77e-4
  - bf16: 3.39e38 / 7.81e-3
  - cb16 under the stated assumption: 4.29e9 / 9.31e-10 / 1.95e-3
  - E5M2 57,344; E4M3 448 / 2^-6 with only S.1111.111 as NaN; E2M1 6 / 1 / 0.5
  - NVFP4 4.5, MXFP4 4.25 (E8M0 per 32), BlockFP8 1,088 B / 1,024 = 8.5, bfp4/bfp2 4.5 / 2.5
  - "1 + 2^-6 = 0x3C10"
- Explorer: RNE with ties to even, the IEEE overflow threshold (max + ulp/2 rounds to infinity), subnormal decode, E4M3/E2M1 saturation (stated), and the MXFP4 scale 2^(floor(log2 amax) − 2) per the OCP spec.
- `cs_readelf` -m / --sym (banks) / --routing, and the bank rule bits [3:1] (man page).
- `--arch` defaults to wse2.
- `--params` takes unsigned only.
- 24 colors on both chips.
- 6 filters per PE.
- Memcpy channels: ≤16 channels at ~7 Gb/s.
- Ch. 16 Tenstorrent table: 332 / 466 / 664 TF, CBs 32/64, 9-cycle hop, two CQs.
- H100: 989 / 1,979 / 67 TF, 228 KB, 50 MB, 132 SMs, 512 FMA/clk per Tensor Core.
- WSE-3 125 PF sparse.
- CS-4 is 3 × WSE-3T.
