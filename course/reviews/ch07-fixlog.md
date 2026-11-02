# ch07 · fix log

File edited: `course/07-host-io.html` only. Rewritten and restructured. New section order: narrow door (+ calculator) → memcpy frame (+ fabric-dims calculator, reserved resources) → how a copy reaches its PE (+ counter-filter widget) → host side in eight lines → command stream (+ RPC unblock widget) → copy vs streaming (+ decision table, streaming color flow, race timeline, bug callout, queue depths) → ordering → simulator experiment → quiz (7 questions).

New measurements by the fixer (SDK 2.10.1, WSE-3 simulator; scratch dir deleted afterwards):
- Program 02 without the barrier at N=100: sum 30.818176 (= the running sum after 95 values); the `count` read by the next copy is 100. At N=500 without the barrier: the running sum after 495 values. With the barrier, N=500 passes.
- Program 01: 3 west and 2 east ELFs; `out/west/out.json` has num_demux 1.
- bandwidth-test 5×5: H2D 1 ch k=5: 1,473 cycles; H2D 1 ch k=1000: 24,947; H2D 4 ch k=1000: 9,938; D2H 1 ch: 199,327; D2H 4 ch: 199,101. With `--channels=4`: 4 demuxes over row bands 2/1/1/1 and 11 west ELFs instead of 8.
- SdkRuntime introspection: memcpy_*/launch/call return `Task`; `task_wait`, `is_task_done` exist.

## Accuracy
- A1 fixed — Local tasks: "use 8–20 (WSE-3) / 0–20 (WSE-2)", lists 21 (D2H) and topic-09's 21–23, never bind 29 (per coordinator, consistent with ch05).
- A2 fixed — SDK tags on ≤16 and ~200 µs; Vendor tags on 44 GB and 21 PB/s.
- A3 fixed — "at most about 14 GB/s, only if channels scale linearly … assumes several links" [Derived].
- A4 fixed — "at least 7 columns wider and 2 rows taller" and "CS-2 fabric-dims must be 750,994, rectangle at most 743 × 992".
- A5 fixed — "3 west and 2 east frame programs (out/west/bin/*.elf …)" Measured; column roles now come from the library layout files, not schematic guesses.
- A6 fixed — `out = np.zeros(...)` added; title "(excerpt, comments added)".
- A7 fixed — streaming card: no launch needed to start (gemv-09); program 02 still launches wait_done.
- A8 fixed — Colors row: streaming channels take colors from 0–19 (program 02 uses color 0).
- A9 fixed — rowbcast wording per README (3× in SDK example, H2D only).
- A10 fixed — quiz question now says "colors below 20 (in practice 0–3)", answer explains queues 0 and 1.
- A11 fixed — "The evidence shows …" + Derived tag, plus the library comment "OQ0 may not be empty" [SDK].

## Pedagogy
- P1 fixed — term "memcpy frame", defined; distinguished from ch12 halo exchange; objective rewritten.
- P2 fixed — full arithmetic (1 halo + 3 west, 2 east + 1 halo, 2 rows), commands.sh formulas, interactive calculator, quiz Q2 (P=10 → 17,3 / 4,1).
- P3 fixed — "Lab 3 measures this" removed; warn callout says the simulator does not model Ethernet/TCP and points to Lab 3's 0-step subtraction and the new experiment box (no baseline numbers quoted, since the coordinator flagged them as noisy).
- P4 fixed — copy-mode callout explains memcpy tasks on your CE and per-PE completion (sourced from memcpy.csl: unblock after mov32 / TD); streaming callout explains why memcpy cannot know.
- P5 fixed — "Where the streaming color comes from" paragraph plus a 4-file snippet; do-not-route rule (topic-03); 4+4 limit; IDs < 24 mean streaming.
- P6 fixed — copy vs streaming decision table.
- P7 fixed — call table (constructor, get_id, load/run, memcpy, launch = RPC, stop), heading "The host side in eight lines", nonblock/Task/task_wait, order, 16-bit.
- P8 fixed — both halves of the handshake shown; run-to-completion explanation. On "why 95": measurement now shows a gap of 5 at both N=100 and N=500, so it is explained via queue depths (D6) as Derived/consistent, not as "timing only".
- P9 fixed — back-pressure + serialization mechanism paragraph, quiz Q5.
- P10 fixed — 175 KB crossover, program-01 256 B ≈ 200 µs ≈ 1.3 MB/s, and the calculator.
- P11 fixed — H2D/D2H expanded; demux/mux roles concrete; note on context switch/teardown/NOP.
- P12 fixed — quiz rebuilt: fabric dims, counter filter, copy vs streaming race, ordering deadlock, colors/queues, transfer time.
- P13 fixed — Q1 answer generalised (another launch reusing the queue).

## Visuals
- V1 fixed — tasksEnd = 42 so the counter reads 95 at the read line; "D2H snapshot: on_value() × 95" label; grey "5 tasks too late" segment.
- V2 fixed — bars use themed soft classes (blu/pur/grn/amb) with default text colour; no #fff text.
- V3 fixed — shorter labels; D2H label placed below the bar in barrier mode; wider time scale.
- V4 partially — shared CSS keeps widget SVGs at 620 px with in-box scrolling on phones (text stays legible); halo caption text moved out of SVG; no separate phone layout.
- V5 fixed — static halo figure replaced by the fabric-dims calculator: halo cells labelled, every frame column named, H2D-in (west) and D2H-out (east) arrows, schematic caveat for the east adaptor position.
- V6 fixed — requestAnimationFrame with cancel on re-entry; Play/toggle during playback restarts cleanly.
- V7 fixed — aria-live readouts, aria-label updated with the outcome, prefers-reduced-motion draws the final frame, read line green with the barrier.
- V8 fixed — both claims now Measured by the fixer (count=100 read after the race; N=500 passes) and cited in the bug callout.
- V9 fixed — class-based colours follow live theme changes.

## Depth
- D1 fixed — "How a copy reaches its PE" section (demux column + row counter filters, limit/init_count, library example) and the counter-filter step-through widget.
- D2 fixed — column roles and arithmetic from layout_west_demux_cmdfan_multi.csl and bandwidth-test run.py; calculator with buffer inputs; channels/demux bands Measured.
- D3 fixed — 175 KB crossover, transfer-time calculator with idealised aggregation toggle, nonblock/Task/task_wait, "never reorders".
- D4 fixed — experiment callout with fixer's own bandwidth-test measurements, cycles/wavelet, 0.26 wavelets/cycle hardware comparison, reproduce instructions.
- D5 fixed — ordering mechanism paragraph and the unifying sentence.
- D6 fixed — WSE-3 queue-depth table; 2 + 4 = up to 6 pending, consistent with the measured 5 (Derived).
- D7 fixed — command contents (STACK_POS fields), RPC frame, whole-row participation, inactive rows, TD-based completion; RPC unblock widget.
- D8 fixed — ROW_MAJOR vs COL_MAJOR explained and toggled in the counter-filter widget (COL_MAJOR = wire order, Derived).
- D9 fixed — buffer-columns bullet with 400 KB ≈ 9 columns example; buffers in the calculator.
- D10 fixed — streaming color flow, 4+4 limit, data task on user input queue, do-not-route. (Streaming D2H via fabout DSD not detailed.)
- D11 fixed — MEMCPY_16BIT sentence (memcpy_view, 32-bit wavelets).
- D12 partially — call, rowbcast/colbcast, stride, task_wait/is_task_done mentioned; no full reference table (read_symbol, dump_core, send/receive omitted as unverified here).
- D13 fixed — rowbcast example (4 vs 12 elements), queue row explains IQ0/UT0 data and IQ1 = C22 on WSE-3; note that sys_params.csl is authoritative over stale header comments.
- D14 fixed — ceiling worded as an upper bound needing several links.

## Coordinator notes applied
- "At least 7 columns / 2 rows"; CS-2 max 743 × 992.
- Missing unblock: launch() returns, the next memcpy fails after ~4 s with "could be a kernel stall", no sim_stats.json (Measured, ch09/ch10 reviews) — in prose and RPC widget case (d).
- Halo layout 1 + 3 west, 2 + 1 east.
- Local task IDs 8–20 (WSE-3) / 0–20 (WSE-2).

## New visuals added
1. Transfer-time calculator with a log-scale bandwidth ladder and overhead-vs-wire bar (N1, D3).
2. Fabric-dims calculator replacing the static halo figure (N6, D2, V4, V5).
3. Counter-filter step-through with ROW/COL_MAJOR toggle, wire order and per-PE slots (D1, D8, partly N2).
4. RPC unblock-placement selector with four cases (N3).
5. Rebuilt race timeline (V1–V9).

## Verification
Playwright at 1100 and 390 px, light and dark: 0 page/console errors; no horizontal page overflow (fixed a 1-px overflow from long nowrap tags by moving file names out of tags and allowing long tokens to wrap in prose). Every control exercised (presets, sliders, aggregation, buffers, CS-2 toggle, Step/Play/Pause/Reset, order switch, all four RPC cases, barrier toggle during playback). Screenshots inspected, then the scratch dir was deleted.

## Left for later
- `05-tasks.html` still says "(Chapter 7 gives the looser "9–23")"; ch07 now says 8–20, so that parenthesis is stale (not my file).
- N4 (resource map widget), N5 (copy vs streaming animation), N7 (drag-to-reorder hang demo) not built; the prose and the RPC widget cover the points.
- Dedicated phone layouts for the SVG widgets (they rely on the shared in-box scroll).
- Exact placement of the east mux adaptor / td for 1-row rectangles is not documented; shown as schematic.
