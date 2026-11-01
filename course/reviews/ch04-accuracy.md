# ch04 · accuracy review

Summary: The chapter is mostly accurate. The router model, `@set_color_config` syntax, the multicast/pass-through shapes, the memcpy color numbers (20–23), the game-of-life 8-color count, the filter and color-swap quotes, and the 220 Pb/s derivation arithmetic all check out against the notes, the report and the SDK. The simulator's route tables match the real Lab programs. There is one major error: the chapter turns `SWITCH_REGS_PER_COLOR` (a register count) into "WSE-2 has 1 switch position", which the SDK's own WSE-2 switches tutorial contradicts. The color-budget figure has two problems. It says Lab 1 uses 0 colors, but Lab 1's streaming program uses color 0. It also cites the 25-pt stencil while leaving out that the same README says the runtime reserves 6 colors, not 4. The rest are provenance and wording fixes.

## Findings

### A1 [major] Switch "positions" confused with switch registers; WSE-2 does support 4 positions
Location: "Runtime flexibility: switches and filters" → Switches paragraph.
Problem: "A color can hold up to four route positions (WSE-3 has 4 switch registers per color; WSE-2 has 1)" makes it sound as if WSE-2 has only one position. `SWITCH_REGS_PER_COLOR` counts registers. On WSE-2, a single register encodes all positions. The SDK switches tutorial uses pos1–pos3 and ships a WSE-2 build.
Evidence: `tutorials/topic-06-switches/commands_wse2.sh`: `cslc --arch=wse2 ./layout.csl ...`; `topic-06-switches/layout.csl` lines 51–57: `.pos1 = .{ .tx = WEST }`, `.pos2 = .{ .tx = EAST }`, `.pos3 = .{ .tx = SOUTH }`. `csl-libs/target/wse2.csl:79 const SWITCH_REGS_PER_COLOR = 1;` vs `wse3.csl:94 ... = 4;`. The report (line 72) states only the register count and never equates it with positions.
Concrete fix: Replace `A color can hold up to four route positions (WSE-3 has 4 switch registers per color; WSE-2 has 1) <span class="tag sdk">SDK 2.10.1</span>.` with `A color can hold up to four route positions: the default (position 0) plus pos1–pos3, on both WSE-2 and WSE-3. The SDK switches tutorial builds for both. (The hardware stores them differently: <code>SWITCH_REGS_PER_COLOR</code> is 1 on WSE-2 and 4 on WSE-3.) Not every color can switch: memcpy's source lists 0–9, 12, 13, 16, 17, 20 and 21 as switching-capable <span class="tag sdk">SDK 2.10.1</span>.`
(Evidence for the last sentence: `csl-libs/memcpy/sys_params.csl`: `// WARNING 4: switching-capable colors are //   0, 1,2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 16, 17, 20, and 21`.)

### A2 [major] "Lab 1 = 0" colors is wrong
Location: Color-budget SVG, text element `Colors used in this course: Lab 1 = 0, Lab 2 = 2, Lab 3 = 4`.
Problem: Lab 1's second program streams host data on user color 0, so Lab 1 spends one routable color.
Evidence: `course/programs/02-wavelet-tasks/commands.sh`: `--params=N:100 --params=MEMCPYH2D_DATA_1_ID:0`. `02-wavelet-tasks/pe_program.csl:13`: `const h2d_color: color = @get_color(@bitcast(u16, sys_mod.MEMCPYH2D_1));`. Lab 2 (`03-row-reduce`: c0,c1; `05-column-broadcast`: color 0) = 2 is correct, and Lab 3 (`04-heat-stencil`: E0,E1,W0,W1) = 4 is correct.
Concrete fix: Change the text to `Colors used in this course: Lab 1 = 1 (H2D stream), Lab 2 = 2, Lab 3 = 4`.

### A3 [major] 25-pt stencil citation contradicts "4 taken by the runtime"
Location: Color-budget figcaption ("24 colors, 4 taken by the runtime … The SDK's 25-point stencil benchmark notes it is left with only 4 spare colors.").
Problem: The README the caption cites says SdkRuntime reserves 6 colors, and the stencil itself uses 21 colors and task IDs. Quoting only "4 spare" next to "4 taken by the runtime" makes a reader compute 24 − 4 − 4 = 16 for the stencil. The research report quotes the "reserves 6" part, so the chapter dropped it.
Evidence: `benchmarks/25-pt-stencil/README.rst` lines 16–18: "The stencil code uses 21 colors and task IDs for communication patterns, and ``SdkRuntime`` reserves 6 colors, so only 4 colors are left for ``streaming`` H2D/D2H transfers". Report line 74 quotes the same. `memcpy/sys_params.csl` defines only colors 20, 21, 22 and 23 as routable system colors.
Concrete fix: Replace `The SDK's 25-point stencil benchmark notes it is left with only 4 spare colors.` with `The SDK's 25-point stencil benchmark spends 21 colors and task IDs on its communication; its README says SdkRuntime "reserves 6 colors, so only 4 colors are left" for streaming transfers. (The library source names 4 routable system colors; the README's count of 6 is not broken down.)`

### A4 [minor] Per-color buffer claim tagged as SDK; it comes from an arXiv paper
Location: First figcaption: "Each color has its own input buffers at each router, so traffic on one color cannot block another."
Problem: The sentence follows the SDK tag, but its source is arXiv:2209.15040 (Indep). "Cannot block another" also overclaims: colors still share the physical link bandwidth. The source says the buffers make the fabric lossless and deadlock-free.
Evidence: wse_hardware.md §4: "dedicated input buffers for each color at each router … no wavelet is dropped and … communication remains deadlock-free — [arXiv:2209.15040]". Report line 62 cites the same arXiv paper.
Concrete fix: Replace with `Each color has dedicated input buffers at each router, so the fabric is lossless and deadlock-free and a stalled color does not stall the others' buffers, though all colors share each link's bandwidth <span class="tag indep">Indep (arXiv:2209.15040)</span>.`

### A5 [minor] Filter banks: both chips have 6 filters
Location: Filters paragraph: "WSE-2 has two filter banks, WSE-3 one."
Problem: The sentence is literally true, but it suggests WSE-3 has less filtering. Both chips have 6 filters in total.
Evidence: `target/wse2.csl:36–38`: `filter_bank_1_size = 4; filter_bank_2_size = 2; num_filters = filter_bank_1_size + filter_bank_2_size;`. `target/wse3.csl:38–39`: `filter_bank_1_size = 6; num_filters = filter_bank_1_size;`.
Concrete fix: Replace `WSE-2 has two filter banks, WSE-3 one.` with `Both chips have 6 filters: WSE-2 splits them into two banks (4 + 2), WSE-3 has one bank of 6 <span class="tag sdk">SDK 2.10.1</span>.`

### A6 [minor] Untagged numbers
Location: (a) lede "900,000 PEs"; (b) first section "over a thousand hops"; (c) wavelet SVG text "5-bit color tag: 24 routable colors (0–23), 8 reserved."; (d) final paragraph "~4 GB/s".
Problem: The brief requires every number to carry a tag. "8 reserved" comes from SpaDA (Indep), and "5-bit" comes from an SDK-docs search extract. "~4 GB/s" is 32 bit × ~1 GHz, which is derived. "Over a thousand hops" comes from the ~950×950 grid size (Manhattan distance ≈ 1,900).
Evidence: wse_hardware.md §4: "each wavelet carries a 5-bit color tag … [SDK docs] (via search extract)"; "24 per PE and an additional 8 reserved — [SpaDA arXiv:2511.09447]"; §1: "900k cores (vendor)".
Concrete fix: (a) after `900,000 PEs` add ` <span class="tag vendor">Vendor, WSE-3</span>`. (b) change `takes over a thousand hops.` to `takes well over a thousand hops (about 1,900 on a ~950 × 950 grid) <span class="tag derived">Derived</span>.` (c) add a figcaption sentence: `The 5-bit tag and the "8 reserved" IDs come from SDK docs extracts and the SpaDA paper <span class="tag indep">Indep</span>.` (d) change `is only ~4 GB/s` to `is only ~4 GB/s per direction (32 bits × ~1 GHz) <span class="tag derived">Derived</span>`.

### A7 [minor] Aggregate-bandwidth formula should say what it sums
Location: Paragraph "The aggregate fabric numbers follow from this design: 32 bits × 4 directions × 2 × ~850k PEs × ~1 GHz…".
Problem: The arithmetic is right (256 × 8.5e5 × 1e9 ≈ 2.2e17). The "× 2" counts every router's ingress and egress, so each physical link-direction is counted twice. Vendors apparently count the same way, but the chapter should say so. The ~1 GHz clock is an assumption, not a vendor figure.
Evidence: wse_hardware.md §4 Inferences: "My arithmetic, assuming a ~1 GHz clock."
Concrete fix: Replace `32 bits × 4 directions × 2 × ~850k PEs × ~1 GHz` with `32 bits × 4 ports × 2 (in + out) × ~850k routers × an assumed ~1 GHz clock`.

### A8 [minor] Simulator hint contradicts the stated ramp latency
Location: Widget hint "the ramp costs an extra tick" vs prose "the ramp takes about two".
Problem: The prose says the ramp takes ~2 cycles. The code delays the source ramp-up by 2 ticks (`t: s.t0 + k + 2`), counts ramp-down delivery instantly, and gives relays 3 ticks. "An extra tick" matches none of these.
Evidence: 04-fabric.html line 187 `t: s.t0 + k + 2`; line 201 `t: tick + 3`; line 25 prose.
Concrete fix: Change the hint text `the ramp costs an extra tick` to `going up the ramp costs ~2 ticks (relaying PEs also spend a tick adding)`.

## Not verifiable
- The "8 reserved" color IDs and the 5-bit tag width: only search extracts (SDK docs site) and SpaDA support them, and the local SDK does not state them.
- Whether "24 routable colors" holds identically on WSE-3 hardware. `NUM_COLORS = 24` is a library constant for both chips, but the notes list the WSE-3 route-table color count as a gap.
- The ~1 GHz clock behind the bandwidth derivation and the "~4 GB/s per link" figure (no vendor clock figure in the sources).
- The undefined-behaviour claim for same-color collisions rests on one paper (arXiv:2605.07954). It is correctly tagged Indep but could not be checked against the SDK.
- What the 6 colors SdkRuntime reserves are, per the 25-pt stencil README. The library source shows only 4 routable system colors.
