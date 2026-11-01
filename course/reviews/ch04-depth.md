# ch04 · depth review

Summary: The chapter gives a correct and compact surface model: a 5-port router, 32-bit wavelets, 24 colors, static rx→tx routes, the three route shapes and the checkerboard. It stays at the "what" level wherever the SDK shows the "how". The SDK's own target and tile_config libraries contain the actual router register encoding: on WSE-3 rx is a single direction and tx is a multicast bitmask. The `<control>` library gives the bit layout of a control wavelet. The memcpy and collectives_2d libraries show how counter filters, switches and teardown-mode reconfiguration are really used. The chapter uses none of these. Switches and filters each get one paragraph with no worked trace, though topic-06 and topic-08 are small, fully checkable examples. The claim that routes are "configured once, at load time" leaves out runtime reconfiguration (teardown, `@set_local_color_config`). Nothing explains how arbitrary point-to-point traffic is done without dynamic routing (game-of-life diagonals, histogram-torus). The proposals below are ordered by how much they deepen the learner's model of the mechanism. Items that overlap the pedagogy review (P2, P3, P6, P8) are marked and are kept to content the pedagogy review does not supply.

## Gaps and additions (prioritised)

### D1 [critical] The router's real configuration word: rx is ONE direction on WSE-3, tx is a multicast bitmask
**What is missing.** The chapter says a route is "the set of ports a wavelet of that color is accepted from (rx) and the set it is sent to (tx)". On WSE-3 that is false for rx. The SDK library encodes rx as a 3-bit field holding a single direction, and the compiler rejects more than one. Tx is a 5-bit one-hot mask on both chips, and that mask is what makes multicast possible. On WSE-2 rx is also a one-hot mask, so several inputs can feed one color there. The chapter never shows what a route *is* in hardware: one 16-bit register per color per PE.
**Why it matters.** This is the internal mechanism behind everything else in the chapter: multicast (several tx bits set), the checkerboard (one register per color, so one rule), and why a merging reduction tree cannot be built on one WSE-3 color. A learner who writes `.rx = .{WEST, NORTH}` for `--arch=wse3` gets a compile error the chapter does not prepare them for.
**Source.**
- `csl-libs/tile_config/color_config.csl`, `reset_routes()`: `if (@is_arch("wse3") and count > 0) { @comptime_assert(false, "wse3 supports only one input direction"); }`.
- `csl-libs/target/wse2.csl` `fabric_io`: TX_WEST 0x1, TX_EAST 0x2, TX_SOUTH 0x4, TX_NORTH 0x8, TX_RAMP 0x10; RX_WEST 0x20, RX_EAST 0x40, RX_SOUTH 0x80, RX_NORTH 0x100, RX_RAMP 0x200 (a one-hot rx mask).
- `csl-libs/target/wse3.csl` `fabric_io`: the same TX bits; RX_WEST 0x0, RX_EAST 0x20, RX_SOUTH 0x40, RX_NORTH 0x60, RX_RAMP 0x80, RX_DISABLE 0xa0, RX_MASK 0xe0 (an encoded 3-bit field).
- `common.csl`: `NUM_COLORS = 24`, `REGS_PER_COLOR = 1`, registers are u16. Base addresses: `COLOR_CONFIG` 0x7f20 on WSE-2 and 0x7c00 on WSE-3.
**Proposed addition.**
(a) A paragraph after "Routes are static": "Under the hood, each color's route is one 16-bit register in the router: five tx bits (W, E, S, N, RAMP), any number of which may be set, plus an rx field. On WSE-2 the rx field is also five one-hot bits, so a color may accept from several ports. On WSE-3 it is a 3-bit code naming exactly one port (or 'disabled'). `cslc --arch=wse3` rejects a second rx direction with 'wse3 supports only one input direction'. Multicast is therefore free (set more tx bits), but merging two inbound streams onto one color is impossible on WSE-3." <span class="tag sdk">.
(b) A small register-bit diagram (SVG): a 16-bit row with bits 0–4 labelled TX W/E/S/N/R, then bits 5–9 for WSE-2 (RX W/E/S/N/R one-hot) shown against WSE-3 bits 5–7 (RX code 0=W, 1=E, 2=S, 3=N, 4=RAMP, 5=off). Worked encoding: the Lab 2 multicast route `rx NORTH, tx {RAMP, SOUTH}` is TX 0x10|0x04 = 0x14, plus RX 0x100 on WSE-2 (=0x114) or RX 0x60 on WSE-3 (=0x74).
(c) Fix the wording "the set of ports … accepted from" to "the port(s)". Add a quiz item: "Why does `.rx = .{WEST, NORTH}` compile for wse2 but not wse3?"

### D2 [major] Worked switch trace (topic-06): which neighbour receives which value, and why
**What is missing.** Switches get two sentences. The "payload follows the old route" subtlety is stated but never shown with an example, and the reader cannot see what `current_switch_pos`, `ring_mode` or a CE-ignored control wavelet do.
**Why it matters.** The timing rule only makes sense when traced. Topic-06 is a 9-PE example whose expected outputs are asserted in its `run.py`, so a trace can be checked exactly.
**Source.** `tutorials/topic-06-switches/layout.csl` (the center PE (1,1) has default route `rx RAMP, tx NORTH`; `pos1 tx WEST`, `pos2 tx EAST`, `pos3 tx SOUTH`; `current_switch_pos = 1`; `ring_mode = true`). `send.csl` sends four times: `ctrl(SWITCH_ADV, ce_ignore=true)` then data 0; ctrl, data 2; ctrl, data 4; ctrl, data 6. `run.py` asserts East=0, South=2, North=4, West=6. `topic-07 README` gives the timing rule. `target/wse2.csl` comment: switch config bits 14:13 = current position, bit 12 = ring mode, three 3-bit position fields (direction codes 0=W 1=E 2=S 3=N 4=CE 5=invalid).
**Proposed addition.** A 5-row trace table under "Switches":

| step | position before | wavelet | goes to | position after |
|---|---|---|---|---|
| 1 | pos1 (W) | ctrl SWITCH_ADV (CE ignores it) | West PE's router, dropped before its CE | pos2 (E) |
| 2 | pos2 (E) | data 0 | East PE → result 0 | pos2 |
| 3 | pos2 (E) | ctrl | East | pos3 (S) |
| 4 | pos3 (S) | data 2 | South → 2 | pos3 |
| 5 | pos3 (S) | ctrl | South | pos0 (N), wraps because ring_mode |
| 6 | pos0 (N) | data 4 | North → 4 | pos0 |
| 7 | pos0 (N) | ctrl | North | pos1 (W) |
| 8 | pos1 (W) | data 6 | West → 6 | pos1 |

Caption: "Each control wavelet leaves on the *old* position and flips the switch behind it. That is why the program starts at pos1 and not pos0. One color replaces four." Also add the code snippet of `.switches = .{ .pos1 = .{ .tx = WEST }, … .current_switch_pos = 1, .ring_mode = true }`. Without ring_mode the switch would stick at pos3 (inference; state it as such). Also note that the switches tutorial ships both `commands_wse2.sh` and `commands_wse3.sh` (this matches accuracy A1).

### D3 [major] Anatomy of a control wavelet: entrypoint, up to 8 commands, CE-ignore bits
**What is missing.** The figure only says "Control wavelets carry commands (e.g. advance a switch, trigger a task)". The format is fully specified in the SDK library and explains switches, control tasks and teardown in one picture.
**Why it matters.** A learner who knows the format understands why one control wavelet can both reconfigure routers along its path and start a task at the destination. It also shows why `encode_single_payload(SWITCH_ADV, true, {}, 0)` takes those four arguments, and how collectives_2d steers multi-hop reconfiguration.
**Source.** `csl-libs/control.csl`: opcodes `NOP=0, SWITCH_ADV=1, SWITCH_RST=2, TEARDOWN=3`; `MAX_CMDS = 8`; bit positions: entrypoint at 16 (6 bits, so 16–21; "null" entrypoint 31 when none), cmd0 opcode at 22–23 with its CE-filter bit at 24, cmd1 at 25–26/27, cmd2 at 28–29 and filter bit 0, cmd3 at 1–2/3 … cmd7 at 13–14/15. In single-payload form the low 16 bits carry the data. `target/wse2.csl` `pop_mode`: NO_POP, ALWAYS_POP, POP_ON_ADVANCE (WSE-3 adds POP_ON_ADVANCE_OR_NOP). `collectives_2d/pe.csl` gather-teardown comment: "PE root+1 pops cmd0 and let cmd1 flip the root PE's switch". `topic-07 README`: the lower 16 bits are an optional payload for the control task.
**Proposed addition.** A 32-bit field diagram (SVG) with two variants. Single-command form: [31..25 unused/cmd1+] [24 CE-ignore][23:22 opcode][21:16 entrypoint][15:0 data]. Multi-command form: up to 8 (opcode, CE-ignore) slots packed through the word. Then a paragraph: "A router that sees a control wavelet on a color executes its command (advance or reset the switch, or enter teardown). If the CE-ignore bit is clear and the route reaches RAMP, the CE also gets it and the entrypoint's control task runs with the 16-bit data. Routers can be configured to *pop* the head command, so a multi-command wavelet hands a different command to each successive hop (the collectives library relies on this)." Tag sdk for the field layout. Mark "each hop pops one command" as derived from the pop_mode registers and the collectives comment.

### D4 [major] Routes are not only load-time: teardown mode and runtime reconfiguration
**What is missing.** The chapter says routes are "configured once, at load time". The SDK exposes `@set_local_color_config` (runtime, from the PE's own program), a per-color `.teardown = true` option, a TEARDOWN control command, a TEARDOWN_PENDING register with one bit per color, and teardown task 29. The collectives library uses these to rebuild broadcast/scatter/gather/reduce networks rooted at any PE on only 2 colors per dimension.
**Why it matters.** This is the real answer to "how do libraries do MPI-style collectives with only ~20 colors?". It also qualifies the "static" claim correctly: there is no per-packet lookup, but a PE can rewrite its own router between phases. (This complements pedagogy P7, "why static".)
**Source.**
- `csl-libs/tile_config/teardown.csl`: `get_task_id()` returns local task 29; "teardown-pending … has 1 bit per routable color indicating the ones that are currently in teardown state".
- `csl-libs/collectives_2d/pe.csl`: `clear_filter_and_switch()` then `configure_reduce_network(DATA_COLOR_0/1)`; `initiate_teardowns()`: "The root should send out teardown wavelets to all others PEs to turn C0 and C1 back to teardown mode". There is also an ASCII diagram of the gather teardown sequence, and the alternating C0/C1 reduce-network diagram for 5 PEs.
- `csl-libs/memcpy/wse2/memcpyh2d.csl`: `.teardown = true` in the color config, and "the teardown wavelet ignores the filter, and triggers task 29".
- `tutorials/topic-16-queue-flush/queue_flush_receiver.csl` line 97: `@set_local_color_config(in_color1, .{.routes = .{.rx = .{WEST}, .tx = .{RAMP}}})`.
- `tutorials/topic-11-collectives/README.rst`.
**Proposed addition.** A new h3 under "Runtime flexibility": "Teardown: rewriting routes between phases". Content: (1) a color marked `.teardown = true` can be put into teardown state by a TEARDOWN control wavelet; (2) the router sets that color's bit in TEARDOWN_PENDING and the CE runs task 29; (3) the handler rewrites routes, filters and switches (`@set_local_color_config`, `tile_config.color_config.reset_routes`) and then releases the color. Then a 3-panel diagram from the collectives_2d comment: the gather network (arrows converging on the root, switch positions pos0/pos1 labelled), the teardown wavelets from both ends, and the final all-teardown state. Closing sentence: "This is how `<collectives_2d>` offers broadcast, scatter, gather and reduce rooted anywhere using just two colors per axis (X uses queues 2 and 4, Y uses 3 and 5)." Change "configured once, at load time" to "configured at load time; the router never looks anything up per packet, though a PE can rewrite its own routes between phases".

### D5 [major] Filters in depth: a range-filter trace and the counter filter memcpy uses on every H2D
**What is missing.** One paragraph on range filters. Counter filters are not mentioned, though memcpy's H2D path uses one on every row to deal wavelets round-robin. Filter counts are given as "two banks vs one" with no numbers.
**Why it matters.** It shows a concrete internal mechanism the learner relies on unknowingly every time they call `memcpy_h2d`. It also shows how one broadcast stream becomes per-PE slices without extra colors.
**Source.**
- `tutorials/topic-08-filters/layout.csl` and `send.csl`: PE 0 sends 12 wavelets `pack(i, 10.0+i)` = `(i << 16) | f16 bits`. Receivers pe_id 1..3 have `.filter = .{ .kind = .{ .range = true }, .min_idx = pe_id*3, .max_idx = pe_id*3+2 }`. Routes are `rx WEST, tx {RAMP, EAST}` (the last PE uses `tx RAMP`). So PE1 keeps indices 3–5, PE2 keeps 6–8 and PE3 keeps 9–11, while the stream still passes east. Indices 0–2 are kept by no one.
- `csl-libs/memcpy/wse2/memcpyh2d.csl` header comment ("Example 2: round-robin a wavelet along row PEs", `limit = width - 1`, `init_count = (limit+1 - pid) % (limit+1)`, with the 4×4 counter table) and the base config at ~line 576: `.kind = .{ .counter = true }, .count_data = true, .count_control = false, .limit1 = width-1`.
- `target/wse2.csl`: `filter_bank_1_size = 4`, `filter_bank_2_size = 2` (6 filters, fields CONFIG0/ACTIVE_LIMIT/MAX_COUNTER/COUNTER). `target/wse3.csl`: `filter_bank_1_size = 6` (fields CONFIG0/1, DROP_COUNT, MAX_PASS, COUNTER, STATE). `tile_config/filters/wse3.csl` comments: WSE-3 counters are in "half-wavelets", and WSE-2 "limit" semantics are emulated through MAX_PASS/DROP_COUNT.
**Proposed addition.** (a) A 12-column strip diagram: wavelets 0–11 flow left to right past PE1, PE2 and PE3, with each PE's accepted range shaded and the upper-16 index / lower-16 f16 split drawn on one wavelet. (b) A paragraph plus a small table on the counter filter: "A counter filter counts wavelets on the color and passes one to the CE only when its counter hits zero, then wraps at `limit`. memcpy starts PE *p* at `(w − p) mod w`, so on a row of w = 4 the stream x0 x4 x8 x12 x1 … is dealt PE0: x0, x1, x2, x3; PE1: x4…" Reproduce the 4×4 counter table from memcpyh2d.csl. (c) Replace "WSE-2 has two filter banks, WSE-3 one" with "both have 6 filters per PE: 4+2 in two banks on WSE-2 and 6 in one bank on WSE-3. WSE-3's counter filter is reworked (pass/drop counts in half-wavelets)" <span class="tag sdk">.

### D6 [major] How arbitrary traffic works without dynamic routing: forwarding in software
**What is missing.** The chapter teaches nearest-neighbour and line patterns only. It never says what you do when PE A must reach an arbitrary PE B, or need diagonal neighbours.
**Why it matters.** Static routes plus a 24-color budget mean that general traffic must be relayed by CEs. That is a key internal consequence of the design and a big difference from Tenstorrent's addressed NoC packets (ch13/ch15).
**Source.**
- `benchmarks/game-of-life/README.rst`: "each PE … also forwards the received state from its N and S neighbors to its E and W neighbors. Thus, each PE receives from its E and W links both the state of its E and W adjacent neighbors, as well as its four diagonal neighbors". `game-of-life/layout.csl`: 8 colors with even/odd parameter sets, and route constants `RX_R_TX_E`, `RX_W_TX_R`, …
- `benchmarks/histogram-torus/README.rst`: a two-hop scheme (north/south first, then "actively reroute" east/west). Each axis is a ring made of 4 colors with even and odd PEs passing in opposite directions, and the ring turns around at the end PEs. "Each wavelet is processed by each PE along the route": the PE decodes the target from the wavelet and decides whether to forward or count it.
**Proposed addition.** A short h2 "Reaching PEs you have no route to" with two diagrams. (1) Game of life: a 3×3 neighbourhood with arrows N→centre→E/W, showing that the NE diagonal value arrives in 2 hops via the north neighbour's CE. (2) The histogram folded ring: a 1-D row of 6 PEs, an outbound lane on even PEs and a return lane on odd PEs, and the end PEs turning around. This shows how a torus is made on a mesh by folding. One paragraph: "The router never inspects destinations. If the destination is not on a configured path, a CE must receive the wavelet, decide and re-send it. Each software hop costs ramp latency plus task time instead of one cycle, so these patterns are saved for irregular data."

### D7 [minor] Throughput and pipelining worked numbers (supports pedagogy P8)
**What is missing.** The only timing worked example is "100 PEs ≈ 100 cycles". Nothing says that a stream of n wavelets costs about hops + ramps + (n − 1) cycles. Nothing says that a CE relay (Lab 2's task-based relay) costs more than a fabric-to-fabric DSD op.
**Why it matters.** Learners need to estimate costs and to see why gemv-08 uses `@fadds(out_dsd, y_dsd, in_dsd)` (receive, add and forward in one streaming op) instead of a task per element.
**Source.** Notes `wse_hardware.md` §4: 1 word/cycle per link, about 1 cycle per hop, about 2-cycle ramp (arXiv:2209.15040, arXiv:2605.07954); "T_R cycles from entering the router until an instruction can be issued on it" (arXiv:2404.15888). `csl_programming.md` line 229 (gemv-08 fabric-to-fabric `@fadds`). Report line 42: the SDK's 850 MHz assumption.
**Proposed addition.** A worked example box. "gemv-08 broadcast of x down a column: kx×ky = 4×4, N = 64, so each top PE sends N/kx = 16 wavelets. The last row sees the first wavelet after ~2 (ramp up) + 3 (hops) + 2 (ramp down) ≈ 7 cycles and the last after ≈ 7 + 15 = 22 cycles. Time grows with *n + distance*, not *n × distance*." Second line: "A west-to-east reduction of M/ky-element vectors over kx columns with streaming `@fadds` is pipelined (≈ M/ky + kx·(hop + ramps + T_R)). A task-per-element relay serialises on each CE." Tag the per-cycle figures indep and the sums derived. State that T_R is unpublished.

### D8 [minor] "Router by the numbers" table (gathers SDK constants now scattered or missing)
**What is missing.** Several hard numbers that bound the fabric appear nowhere in the chapter.
**Source.** `target/common.csl`, `wse2.csl`, `wse3.csl`; notes `wse_hardware.md` line 20 (CS-2 fabric 750×994); `csl_programming.md` line 158 (queues); report line 42 (850 MHz).
**Proposed addition.** A table with WSE-2 and WSE-3 columns:

| | WSE-2 | WSE-3 |
|---|---|---|
| routable colors | 24 | 24 |
| route register per color | 1 × 16-bit | 1 × 16-bit |
| rx directions per color | several (one-hot) | exactly one |
| switch positions | 4 (pos0–pos3), 1 register | 4, 4 registers |
| filters per PE | 6 (4 + 2 banks) | 6 (1 bank) |
| input / output queues | 8 / 6 | 8 / 8 |
| fabric coordinate field | 10 bits (`fabric_coord_mask 0x03ff`) | 11 bits (`0x07ff`) |
| SDK-visible fabric | 750 × 994 (CS-2) | not published |
| color swap | yes | no |

Add a derived row: CS-2 corner-to-corner distance is 749 + 993 = 1,742 hops, about 2 µs at the SDK's 850 MHz assumption (derived). This makes "over a thousand hops" precise. Per-link bandwidth: 32 b × 0.85 GHz ≈ 3.4 GB/s (derived). Use this in place of the unqualified "~4 GB/s" or alongside it.

### D9 [minor] Color swap explained as hardware checkerboarding (WSE-2)
**What is missing.** Color swap gets one clause about which chips support it. Its mechanism, and its relation to the checkerboard just taught, are not explained.
**Source.** `tutorials/topic-14-color-swap/README.rst`: 4 PEs, red = color 0 and blue = color 1. All PEs use `rx WEST → tx {RAMP, EAST}` plus `swap_color_x = true`, so a red wavelet leaves east as blue and vice versa. `red_task` adds `in_data` and `blue_task` adds `2*in_data`.
**Proposed addition.** Two sentences and a tiny 4-PE strip in alternating red and blue. "Color swap does the checkerboard in the router: flip the lowest color bit on every east/west hop, and adjacent PEs automatically see alternating colors with *one identical route* on every PE. The layout needs no parity logic. CSL does not support it on WSE-3, so WSE-3 code alternates colors by hand." Optional quiz: "Which PEs run blue_task?"

### D10 [minor] Experiments: dump the real router table and measure hop latency
**What is missing.** Every number in the chapter is quoted. None is measured or inspected.
**Source.** Notes `csl_programming.md` §5: `cslc-driver --out-routes` will "Show per-PE color and routing information"; `cs_readelf --routing/--switching`. The simulator writes `sim_stats.json` with `cycle_count` (report line 197).
**Proposed addition.** (a) A short "Try it" callout: compile `course/programs/03-row-reduce` with `--out-routes` (a copy, outside course/programs) and show the per-PE color table next to the layout source, so the learner sees that the compiler output matches the `@set_color_config` calls. (b) An experiment a fixer can run and then tag "measured": build a pass-through row like the widget's "Pass-through across a row" pattern of width W = 2, 8, 32 (fabric dims W+7 × 3). Send 1 wavelet from the west PE and record the receive cycle with `<simprint>` or the `<time>` TSC at sender and receiver. Fit cycles = a + b·W, where b should be about 1 cycle/hop and a includes the two ramps. Report the fitted b and a in a small table. Run it under `/home/user/cerebras-sdk/tmp/<id>/` per the brief.

### D11 [minor] Widget: add the switch and filter patterns (and expose WSE-3 single-rx)
**What is missing.** The simulator has 5 static patterns. Switches, filters and the single-rx rule (D1–D5) cannot be seen in motion. (Pedagogy P6 separately asks for a collision demo.)
**Source.** The current widget code in `04-fabric.html` (`patterns` object, `step()`, route entries `{rx, tx}`), plus topic-06 and topic-08 as above.
**Proposed addition.** (1) Pattern "topic-06: one color, four neighbours (switch)": on a 3×3 subgrid, give the center router a `sw: [ ["NORTH"], ["WEST"], ["EAST"], ["SOUTH"] ]` with `pos: 1` and `ring: true`. Sources alternate a ctrl flit and a data flit (draw ctrl flits hollow). In `step()`, when a ctrl flit leaves a router that has `sw`, advance `pos` after forwarding. The inspector shows the current position, and the final delivered values must read E=0, S=2, N=4, W=6. (2) Pattern "topic-08: range filter": a 1×4 row with 12 flits labelled by index. Routes carry `filter: [min, max]`; on RAMP delivery, count the flit only when its index is in range, and otherwise draw it fading at that PE while the EAST copy continues. (3) In the route-table inspector, print a "WSE-3: ok / not allowed (rx > 1)" note for each route.

## Out of scope for this chapter (new-chapter or cross-chapter ideas)
- **ch05 (tasks):** The WSE-3 input/output queue binding (`@initialize_queue`, one color per output queue, `@queue_flush` and teardown task 29 for rebinding) is the CE-side half of D1/D4. Ch05 should own it, and ch04 should link to it. Also link to the pipeline-01 warning about blocking a color that a fabin DSD consumes.
- **ch07 (host I/O):** The memcpy H2D row demux with counter filters (D5) could be shown in full there: the west demux columns, the round-robin counter, and why `memcpy_h2d_rowbcast` exists. Ch04 should give only the filter mechanism.
- **ch11/ch12 labs:** Two possible labs. One is a "switch lab" porting topic-06, which reuses one color for a 4-neighbour send and then rewrites Lab 2's checkerboard reduction with switches (gemv-08 README promises this: "In a future example, we will demonstrate the use of dynamic switching … to use a single color"). The other is a `<collectives_2d>` lab based on topic-11 or `benchmarks/gemv-collectives_2d`.
- **ch13/ch15 comparison:** Contrast static colors plus CE relays (D6) with Tenstorrent's addressed NoC packets (32 B flits, ~9-cycle router latency, rectangular multicast, from the report line 229). That is a crisp row for the comparison table: "route chosen per program (Cerebras) vs per packet (Tenstorrent)".
- **Possible new short chapter or appendix "Collectives on a mesh":** broadcast, scatter, gather and reduce on 2 colors per axis via teardown (collectives_2d), the near-optimal wafer-scale reduce (arXiv:2404.15888), and the histogram-torus folded ring. Ch04 alone cannot hold all of this.
