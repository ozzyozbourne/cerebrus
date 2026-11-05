# Round 4 audit · Appendix E (sources and unverified figures) · appE

**Verdict: Mostly correct. Explanation quality: good.**
The generated parts match the chapters: `scan_tags.py --check` today gives 22 pages, 1,365 tags, 85 flagged and 298 sources, which is the page stamp exactly. Two kinds of problem remain:
- The page's own open issue 2 measured a result that contradicts its worked example and three chapters.
- About ten flagged items can now be closed. Two open issues are settled by evidence: issue 3 by a new run, issue 7 by SDK library code.

Simulator runs this round (Program 01 `timed/` harness, N = 1,024, TSC; scratch dir `/home/user/cerebras-sdk/tmp/r4-appE/`, deleted):

| Run | PAD | Cycles |
|---|---|---|
| WSE-2 f16 `@fmach` (re-check of issue 2) | 0 / 4 | **526 / 270** |
| WSE-2 f32 `@fadds(y, y, x)` | 0, 1 / 2, 6 | **1,038 / 526** |
| WSE-3 f32 `@fadds(y, y, x)` | 2 | 527 |

## Errors

**E1 · high · Worked example, step 5 ("Re-run").**
- Quoted: "f16 multiply-accumulate runs at ~2 elements per cycle on WSE-2 (Chapter 3), half the 4 lanes assumed, so the 7.5 PF is a peak the simulator's DSD ops do not reach."
- This page's own issue 2 (`#iss-clash`) measures WSE-2 `@fmach` at 270 cycles for 1,024 elements when the sources start 4 banks apart. That is about 3.8 elements/cycle, essentially the full 4 lanes. I re-ran it: 526 cycles at PAD 0, 270 at PAD 4.
- What is right: on WSE-2 a well-placed f16 FMAC reaches ~4/cycle. The "~2" is a placement artefact. So the simulator *does* nearly reach the 4-lane peak.
- This also corroborates the Secondary "4 lanes" input that step 4 calls the weakest link: an op that sustains 4 f16 elements per cycle needs at least 4 lanes.
- Fix: rewrite steps 4–5. The lane count is now supported by a Measured rate, and the 7.5 PF peak is consistent with the simulator.

**E2 · high (cross-chapter; App E is where it surfaces) · WSE-2 f16 rate in Ch 3, Ch 6, Ch 11 and CCN 14/22.**
- Ch 3 `#pe-speed` says "f16 reaches about 3.2 per cycle on WSE-3 and 2.0 on WSE-2". Ch 6 `#op-speed` gives `@fmach` WSE-2 527 ("2"). Ch 11 says "f16: 4 per cycle on WSE-3, 2 on WSE-2 … half the quoted 8-wide f16 SIMD, because each element of an in-place op needs two reads and a write".
- CCN 29 (the r2 App E fix) contradicts CCN 22, and nobody propagated it.
- Ch 6's operands sit 1,025 words apart. That is 2,050 f16 elements, 2 banks apart, which is a slow case under issue 2. Ch 11's run is unpadded (0 banks apart), also slow.
- Ch 11's "two reads and a write" explanation fails on WSE-2: the same in-place op runs at 4/cycle with PAD 4.
- Fix: issue 2 should state the consequence in one line ("WSE-2 f16 FMAC: 2/cycle as laid out in Ch 6/11, ~4/cycle with sources 8 bytes apart"). The coordinator should add a CCN item retiring "2/cycle WSE-2 f16" as a rate.

**E3 · med · Open issue 3, `@fadds` on WSE-2. Now settled.**
- Quoted: "Unknown: Why the same op runs twice as fast in Lab 3 … no mechanism is known."
- New measurement: WSE-2 `@fadds(y, y, x)`, 1,024 f32, runs at 1,038 cycles with PAD 0 or 1 and **526 with PAD 2 or 6**. In those cases the start banks are 4 apart, which is the man page's "same bank modulo 4". WSE-3 gives 527 at PAD 2, the same as Ch 6's 528.
- Lab 3's operands are `left = u[i]` and `right = u[i + 2]` (`programs/04-heat-stencil/pe_program.csl:27–29`), exactly 8 bytes, or 4 banks, apart. Ch 6's 1,025-word spacing puts them 2 banks apart.
- So issues 2 and 3 are one rule: a WSE-2 op that reads 2 elements per cycle per stream (f32 add, f16 FMAC) runs at full rate only when the two source streams start in opposite halves of the 8 banks.
- Fix: merge issue 3 into issue 2 as Measured. Update Ch 13's "(…we have not isolated why)" and Ch 6's "1 / 2" footnote.

**E4 · med · Open issue 7, `@fscales` / `@fnorms`. Mostly settled from the SDK.** The Unknown says it is not known whether scale differs from `@fmuls` with a scalar.
- `LIB/math.csl:1327–1333` defines `fscale_f32(f: f32, s: i16)`. At compile time it returns `f * internal.pow2i_f32(s)`; at run time it calls `@fscales(&r, f, s)`. So `@fscales` is ldexp, f · 2^s with an **i16** exponent [SDK]. It is not a general multiply.
- `@fnorms` is used as `internal.fnorm(f32, x) - 1.0` before a log polynomial (`math.csl:1385`). In sqrt, the exponent comes separately and the comment "so x_norm in [1,4)" follows one doubling (`math.csl:1147–1153`, `1286–1291`). It returns the significand normalised into [1, 2), like frexp's mantissa [Derived from SDK code].
- Fix: move this to Known, keep only the edge cases (zero, denormals) as Unknown, and update Ch 6 `#builtins`, flagged row 10.

**E5 · med · Ch 18:282 and :284 still use class `measured` for peer-reviewed third-party results** (WSE-2 MD "Measured peer-reviewed…", SC20 BiCGStab "Measured Cerebras/NETL authors").
- This contradicts this page's definition ("Run during this course's build") and inflates Ch 18's Measured count in the widget.
- The r2 fixlog says A8 was already fixed on disk; it is not. **Still open (from r2-appE-accuracy A8).** The fix belongs to Ch 18: use class `indep`.

**E6 · low · Tag table, "Vendor" row.** It says "Published or presented by Cerebras, NVIDIA or Tenstorrent". The course also tags Meta, Google, AMD and Groq figures as Vendor (for example "[Vendor, Meta]" in flagged row 16). Fix: "published by the maker of the product or model".

**E7 · low · "Two limits" paragraph.** It says cerebras.ai and the Cerebras docs could not be fetched. This round both `cerebras.ai/blog/llama-405b-inference` and `training-api.cerebras.ai/en/1.7.0/...data-formats` were fetched directly. Fix: write "could not be fetched during the build (some became reachable later)", and upgrade the items below.

**E8 · low · Scanner misses Ch 1's legend** (`01-memory-wall.html:282`, "Every figure carries a tag: Vendor published by …"). That sentence has six tags with prose between them, so the "≥4 tags, punctuation only" rule skips it. Ch 1 shows legend = 0, and its counts include 6 non-claims. Fix: extend the "labelled/tagged" rule to "carries a tag:", or add `data-legend`.

## Flagged items that can now be verified (web, 2026-11-05)

| # | Item | Result | Suggested tag |
|---|---|---|---|
| 78, 79 | App A cb16 "1 / 6 / 9" | Cerebras docs: "CB16 is a floating-point format with 6-bit exponent and 9-bit explicit mantissa" (training-api.cerebras.ai 1.7.0, fetched directly). The bias is still unstated. | Vendor (Cerebras ML docs); keep "bias 31 if IEEE-like" as Derived |
| 40 | CUTLASS ping-pong 40 / 232 registers | `sm90_gemm_tma_warpspecialized_pingpong.hpp`: `LoadRegisterRequirement = !HeavyRegisterPressure ? 40 : 24`, `MmaRegisterRequirement = … ? 232 : 240` (raw GitHub, fetched). | Vendor (CUTLASS source); mention the 24/240 variant |
| 42 | Blackwell TMEM 256 KB | 128 lanes × 512 columns × 32 bit = 256 KiB per SM (NVIDIA tilus docs, mlc.ai, via search) | Vendor via secondary |
| 46 | NVL72: 18 compute trays × 4 GPUs, 9 NVSwitch trays | NVIDIA DGX SuperPOD GB200 reference architecture (via search) | Vendor via secondary |
| 29 | Ch 15: SC20 allreduce latency "could not check" | arXiv 2010.03660, fetched: scalar AllReduce "under 1.5 microseconds for … about 380,000 … processors"; "cycle count only about 10% greater than the diameter"; iteration 28.1 µs with 4 dots per iteration (so ≤ ~6 µs of it); two receiving cores per row because "a core can add two 32-bit quantities per cycle but can receive only one from the fabric". | Indep (peer-reviewed); Ch 15 can now compare its ~180,000 cycles per iteration with ~1,300 |
| 25, 74 | CS-4 ">4,400 tok/s per user on gpt-oss-120B" | Confirmed as Cerebras's own claim (press release, 18 Aug 2026, via search). There is no Artificial Analysis CS-4 measurement; AA lists the hosted service at ~1,869 tok/s. | Ch 18 row: Vendor (press release), "not independently measured" (as Ch 9 already says) |
| 22 | 405B row | 969 tok/s (1,000-token prompt), 539 at 100K, 240 ms TTFT: all three confirmed on cerebras.ai/blog/llama-405b-inference (fetched). The Unverified tag is on the explanation, not the numbers; see X1. | no change |
| 21, 54, 66 | Rubin CPX | Still no formal cancellation. New: NVIDIA VP Ian Buck at GTC 2026 said CPX was pulled from the immediate roadmap and may return "in the next generation" (LAVX, Wccftech: secondary). | add a "Vendor via secondary: deferred, not cancelled" clause |
| 49 | ~$20B deal price | Still unconfirmed. CNBC's source is Alex Davis (Disruptive, Groq investor), not either company. | unchanged; name the source |
| 75 | MLPerf, Cerebras/Tenstorrent | None found | unchanged |
| 38 | H100 32 banks × 4 B | This is the CUDA Programming Guide rule, but the guide (docs.nvidia.com) still could not be fetched; extracts confirm it only for cc 5.x/6.x. | unchanged, settle text OK |

## Explanation problems

**X1 · med · Flagged list, Ch 9 rows 17/18, 22, 23/24.**
- Row 22 quotes the whole 405B table row, so 969 tok/s reads as Unverified when the tag covers only the "what made the jump" reasoning.
- Rows 17/18 and 23/24 are the same claim listed twice, under two tags.
- Fix: for a table cell with several tags, cut the claim at the clause the tag follows. Merge rows that share a claim and show both tags.

**X2 · low · Issue 2, "Reading it".** This is one 170-word paragraph that carries eight PAD values. Use the 4-row table from `r2-appE-fixlog.md`: gap 0 / 2 / 4 by op and chip, with E3's `@fadds` row added.

**X3 · low · Open issues.** Terms used without links to App A: TSC, DSR, input queue, microthread, bank. Link them on first use.

## Connecting gaps

**G1 · high · "Bank placement" (issues 1–3) → "per-PE speed" (worked example; Ch 3/6/11). Effort S.**
- The page measures a placement rule, but never says what it changes for a learner: the quoted WSE-2 rates, and which lane-count claims the simulator supports.
- Bridge: a 3-line "What this means" box under issue 2:
  1. On WSE-2, put two source streams 8 bytes apart and f32 adds and f16 FMACs double.
  2. On WSE-3 they don't move.
  3. That is why Lab 3 is fast.
- Point to Lab 3's `u[i]`/`u[i+2]` as the worked instance.

**G2 · med · "Flagged input" → "Derived figures built on it". Effort M.**
- The worked example shows that 7.5 PF inherits the Secondary "4 lanes". The flagged list never shows a figure's dependents, so a reader cannot see which Derived numbers weaken when an input is flagged.
- Bridge: a "used by" note on rows whose claim feeds Derived arithmetic (lanes → peak PF; 21 PB/s → decode bounds; 256-LPU rack → rack SRAM). Doing it by hand for the five or so biggest is enough.

**G3 · med · Open issues → "how do I run the test myself". Effort S.**
- Each "Would settle it" describes an experiment but not the harness. Issues 2, 3 and 6 can all be run with `programs/01-saxpy/timed`, `bash commands.sh N HALF PAD`, after swapping the one op line.
- Bridge: one sentence per issue naming the harness and command. Step 5 of "How to check a figure" could say the same.

**G4 · low · SC20 reduction (now verified, see table) → Ch 15's 180,000-cycle collective. Effort S.**
- The SC20 paper explains why a hand-routed allreduce costs about the diameter: a streaming chain into two centre cores, one datum per cycle per core.
- That is the mechanism Ch 12's chain and Ch 15's library differ on. Cite it in Ch 15 and add it to the bibliography's Cerebras-papers group, which already lists 2010.03660.

**G5 · low · "Vendor" tag → products from other makers.** See E6. Without the wider definition, a learner can't tell whether "[Vendor, Meta]" belongs to the Vendor class.

## Checked and fine
- The page stamp and the embedded JSON equal a fresh `scan_tags.py --check` (1,365 / 85 / 298). All 85 flagged rows still exist in their chapters.
- Every chapter anchor the open issues link to exists: `#bank-model`, `#kernel-time`, `#collisions`, `#op-speed`, `#numbers-say`, `#latency`, `#hop-cost`, `#microthreads`, `#index-offset`, `#builtins`. So do `02#generations`, `03#pe-speed`, `03#wse2-wse3`, `appendix-c#tsc` and `#src-hc34`.
- Worked example steps 1–4: the quoted Ch 2 sentence is verbatim (line 127), the arithmetic (7.48 PF) is right, the HC22 = HC34 deck is in the bibliography, the 75 PF sparse vs 7.5 PF dense distinction holds, and the Ch 3 "4 lanes" tag is Secondary.
- Issue 1: the bank rule agrees with Ch 3:150–154 (bits [3:1], 16-byte stripe, 8 × 6 KB).
- Issue 2: the numbers equal Ch 11's table (143/79/78, 2,063/1,039, 2,062/1,038) and Ch 6. My re-run reproduced 526 / 270.
- Issue 4: the numbers equal Ch 4's table (36/48/96/160; 44/68/164/292; WSE-2 M = 64 ≈ 160) and Ch 12's ~90-cycle floor.
- Issues 5 and 6: the cslc error quote and the two SDK file references are as in the r2 fixlog.
- The deal-price, CPX and LPX wording in the flagged list still matches the current state of reporting, apart from the CPX nuance above.
