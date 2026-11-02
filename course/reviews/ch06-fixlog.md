# ch06 · fix log

Chapter rewritten in place: `course/06-dsds.html` (only file edited). The sections now run: one instruction / scalar vs DSD widget → two spellings and moving a DSD (GEMV widget, DSD-editing builtins, visualizer, mem4d) → builtins (family matrix from dsd_ops.csl) → how fast is one instruction (measured rates, charts, Lab 3 cross-check, worked bytes/FLOPs) → layout and operand collisions (bank widget) → DSRs/@load_to_dsr/@map (loop vs map) → fabric DSDs (declarations, routes not DSDs, one consumer per queue, WSE-3 one fabric input, wavelet_index_offset) → async (sync vs async example, completion meaning, the stall, .unblock throttle, timeline widget, microthread table) → FIFOs (code, ring figure, ways to absorb a burst) → Lab 3 → 10-question quiz. Objectives were rewritten to match (5 bullets).

## Measurements (re-run by the fixer)
Simulator, SDK 2.10.1, a modified copy of `benchmarks/single-tile-matvec`: 1×1 rectangle, TSC around compute(). The scratch copy in `/home/user/cerebras-sdk/tmp/fix-ch06/` has been deleted.
- 1,024 f32 elements, operands 1,025 words apart, WSE-2/WSE-3: fmovs 526/271, fadds 1039/528, fmacs 1039/1041, fmuls scalar 1038/1040, fmuls with two DSD sources 1039/1040. All of these match the depth review.
- f16 with zero data: fmovh 270/162, faddh 527/310, fmach 527/310 (271 when done in place).
- Start-up on WSE-3: fmacs at extents 1/16/64/256/1024 took 18/33/81/273/1041 cycles; fadds took 17/24/48/144/528.
- Matvec: with @map + DSR, WSE-3 126/1110/4214 and WSE-2 119/1108/4216 for N = 8/32/64. With a scalar loop, WSE-3 252/2160/6352 and WSE-2 229/2034/6354. Without the +1 offset, WSE-3 190/2134/8310.
- Collision rule (new): in-place `@fmacs(dA, dA, dC)` with dC at 2048+k doubles (2064 vs 1040) only for k ≡ 0 mod 4. A test with three distinct arrays doubled when src0 and src1 were ≡ 0 mod 4 apart, and not when only dst and src1 were. The in-place fadds at offset 2048 showed no penalty. The page states this as "the two source streams start at addresses equal mod 4", tagged Measured and empirical.
- Compile-only checks (cslc 2.10.1, WSE-3): `.stride = -1`, a mem4d_dsd reduction onto `acc[k]`, `@import_module("<dsd_ops>")` with `ops.fmac(...)`, and `@set_dsd_stride` / `@set_dsd_length`.

## Accuracy
- A1 fixed: the `@fmuls(dst, a, b)` row is now element-wise, with a scalar b allowed. The two-DSD form was also measured.
- A2 fixed: the text says 48 DSRs is WSE-3 only, tagged Vendor, and that no WSE-2 count is published.
- A3 fixed: "arithmetic unit" replaces "SIMD lanes", tagged Derived.
- A4 fixed: the naming pattern now includes `hs`, tagged sdk with the dsd_ops.csl source.
- A5 fixed: the operand-type sentence is now scoped per builtin and points to the reference.
- A6 fixed: "the same source runs on both chips", tagged Measured.
- A7 fixed: the pipeline-01 warning is scoped to a blocking @add16 on a memcpy stream, with the README quote. The topic-04 nuance is noted.
- A8 fixed: the 14-wavelet limit is placed in context as an I/O-path capacity that depends on the architecture.
- A9 fixed: the preset is now base 1, labelled "next column, after @increment_dsd_offset(A_dsd, 1, f32)".
- A10 fixed: the stencil comments use the DSD index (`lap[i] = u[i] + u[i+2]` …).

## Pedagogy
- P1 fixed: the real fabin/fabout declarations and @initialize_queue lines from program 03 are shown, with a paragraph on queue vs colour.
- P2 fixed: the figure labels name queues, and the figure plus caption say that direction comes from the layout.csl routes.
- P3 fixed: new section "Two spellings, and moving a DSD", with the gemv-02 loop and a table of 4 DSD-editing builtins.
- P4 fixed: same as A9.
- P5 fixed: sync-vs-async example from program 04; what completion means; why blocking stalls; the .unblock throttle (topic-09 code); the microthread table; links to Ch5; plus the timeline widget.
- P6 fixed: "One consumer per queue" callout.
- P7 fixed: the FIFO paragraph is rewritten with topic-09 code. The WSE-3 callout now says "(explained below)".
- P8 fixed: the scalar vs DSD widget shows the instruction count (tagged Derived) and the measured cycle estimate.
- P9 fixed: merged with A5.
- P10 fixed: the label now reads "v_dsd → v[0..M-1] in local SRAM".
- P11 fixed: the index meaning and the reason the in-place update is safe are explained after the stencil code.
- P12 fixed: unblock_cmd_stream gets a Ch7 gloss; Lab N (Chapter X) appears on first use; topic-10-map-builtin is named in full.
- P13 fixed: added a "Reading CSL" aside.
- P14 fixed: the tag is now sdk (dsd_ops.csl).
- P15 fixed: Q1 now has the `[8,8]f32` caveat, plus all 4 suggested questions and 3 more (cycle estimate, half-speed matvec, data task vs fabin), for 10 in total.

## Visuals
- V1 fixed: same as A9.
- V2 fixed (partly by the shared CSS): a row-width control (8/12/16/24) and labels of at least 11 px. On phones the shared 620 px minimum-width scroll applies.
- V3 fixed: relabelled; the arrow is now 42 px; fonts are 12–16; route notes added. Mobile uses the shared scroll rather than a second layout.
- V4 fixed: the stencil preset has its own layout (hatched ghost cells, three aligned rows). Its inputs show the mid DSD and are locked. Editing any input switches the select to "custom".
- V5 fixed: repeated visits are grouped and labelled "×16", and the readout states the broadcast.
- V6 fixed: only classes and cssVar are used; the toggle was tested.
- V7 fixed: values are clamped and rounded (base 0–47, extent 1–48, stride −16..16). There is a negative-address warning and a reverse-walk preset (stride −1 compiles).
- V8 fixed: the matrix presets set row width to 8, so the matrix is drawn as 6×8.
- V9 fixed: the readout shows the tensor_access and base/extent/stride forms and up to 48 words; the viewBox is fitted; dark text on soft fills; aria-live.
- V-P1 (animated systolic reduction) skipped: left for later. The static figure was fixed instead.
- V-P2 (GEMV column sweep) added, with the gemv-02 data (y = 17, 53, 89, 125) and an "increment by N" bug toggle.
- V-P3 (scalar loop vs DSD with DSRs and the address generator) added.
- V-P4 (async timeline) added: async vs blocking (deadlock), .activate vs .unblock (join).
- V-P5 (FIFO) partly done: a static ring figure plus the "ways to absorb a burst" table. No animation and no rate slider.
- V-P6 (stencil with numbers) partly done: the visualizer preset was redrawn, but there is no numeric step-through.
- V-P7 (name decoder) partly done: replaced by the static family matrix table.

## Depth
- D1 fixed: rate table, two charts (elements/cycle; cycles vs extent), the Lab 3 2.5 = 0.5+1+1 callout using the coordinator's 90 + 2.5·n.
- D2 fixed: f16 single-op rates measured by the fixer. Matvec f16 1335/2165 is quoted from the depth review (not re-run). The text says "SIMD width is a ceiling" and is tagged Derived.
- D3 fixed: new section with measured matvec numbers and the mod-4 rule (re-measured, which refines the reviewer's "0 or 4 mod 8"), plus the collision widget and a bank view in the visualizer. The N=31 padding number is quoted from the depth review.
- D4 fixed: new "Where the descriptor lives" subsection with the matvec code and the loop-vs-@map table. Overhead is about N+35 per column against N+2.
- D5 fixed: worked bytes/FLOPs callout, tagged Derived, with 850 MHz marked as the SDK's assumption.
- D6 fixed: mem4d_dsd subsection with the 25-pt-stencil excerpt. There is no diagram.
- D7 fixed: wavelet_index_offset subsection. The index unit is inferred to be 16-bit from the f32 `.index = 2*idx` use, tagged Derived. There is no mini diagram.
- D8 fixed: full family matrix from dsd_ops.csl, plus an import example (the compile was measured). The semantics of scale and norm are tagged Unverified.
- D9 fixed: FIFO mechanism, the two-microthread cost, the ring figure, a burst table including pipeline-03 and sdklayout-03, and 0x7fff in the fabric section. The pipeline-01 14 vs 15 experiment was not run.
- D10 fixed: microthread mapping table (topic-15) and the block/unblock throttle. The "memory-only async ut_id" row was omitted as unverified.
- D11 fixed: the 16-bit packing sentence with the sdklayout-04 quote. There is no diagram.
- D12 fixed: table of 4 builtins with the FFT one-liner and an "every second word" preset.
- D13 fixed: start-up chart and text ("below ~16 elements start-up dominates"), plus a quiz question.

## New visuals added
1. Scalar loop vs one DSD instruction (interactive: N slider, Step/Play/Reset).
2. GEMV column sweep (interactive: Step/Play/Reset, bug toggle).
3. Async timeline (interactive: async/blocking, activate/unblock, time slider, Play).
4. Operand collision widget (offset and op selectors, with measured readout).
5. Elements-per-cycle bar chart and cycles-vs-extent chart (static, measured).
6. FIFO ring figure (static).
7. Rebuilt DSD visualizer: presets, row width, bank view, stencil layout.

## Verification
Playwright/Chromium at 1100 and 390 px, in light and dark: no page or console errors and no horizontal page overflow. One overflow, caused by a long tag, was found and fixed. Every widget control was exercised, including edge inputs (−5, 2.5, 5e6) and the theme toggle. Screenshots of the key figures were inspected, and label overlaps in the timeline, GEMV and collision widgets were fixed.

## Left for later
- Animated systolic row reduction (V-P1); stencil numeric step-through (V-P6); FIFO animation.
- Diagrams for mem4d folding, wavelet_index_offset and 16-bit packing.
- Confirm the `.index` unit and the scale/norm semantics against the online builtin reference.
- Ch12 still says 88 + 2.5·n and "stalled at cycle 1,894"; that is the ch12 fixer's job (cross-chapter notes 1 and 4).
