# ch04 · fix log

Only `course/04-fabric.html` was edited. The page has a small `<style>` block and one inline script. Coordinator notes applied: clock figures are now 1.1 GHz WSE-2 [Vendor, HC22] and 850 MHz [SDK assumption], with no "~1 GHz" left. "Color picks the task" is now WSE-2 only; on WSE-3 the color is bound to an input queue and the queue picks the task (Ch. 5).

## New measurements (this fix)
- **Hop latency** (`Measured, SDK 2.10.1 simulator`). A row of P PEs, pass-through east on c0. The far PE does an async `@fmovs` relay back west on c1, and PE 0 times the round trip with `<time>`, so only one PE's clock is used.
  - WSE-3, M=1: 44 / 68 / 164 / 292 cycles at P = 2 / 8 / 32 / 64, so 2.0 cycles/hop.
  - WSE-2, M=1: 36 / 48 / 96 / 160, so 1.0 cycle/hop.
  - WSE-3, M=64: +63–64 cycles over M=1, so 1 cycle per extra wavelet.
  - WSE-2, M=64: ~160 cycles flat up to P=32, so about 2 cycles per wavelet. This is a CE-side limit I did not investigate.
  - An earlier attempt that compared TSCs across PEs was discarded. Each PE's TSC is enabled by a broadcast launch, so the propagation delay cancels and cross-PE differences are invalid. The ch11 "start spread 0" result may have the same caveat.
- **WSE-3 single-rx rule** (`Measured, cslc 2.10.1`). Lab 2's layout with `.rx = .{WEST, NORTH}` (and also the one-color `{WEST, RAMP}` → `{RAMP, EAST}` rule) compiles for wse2. For wse3 it fails with `error: expected at most 1 input direction(s) on 'wse3', got: 2`.

## Accuracy
- A1 fixed: positions vs registers corrected; switching-capable colors listed (memcpy/sys_params.csl).
- A2 fixed: Lab 1 = 1 (H2D stream on color 0), in the prose and the planner.
- A3 fixed: the 25-pt stencil sentence now quotes "reserves 6 colors, so only 4 colors are left" and notes that the library names 4.
- A4 fixed: the per-color buffer sentence is tagged Indep (arXiv:2209.15040) and says links share bandwidth.
- A5 fixed: both chips have 6 filters (4+2 vs 6).
- A6 fixed: the 900,000 is tagged Vendor. "Over a thousand hops" is now 1,742 hops on CS-2's 750×994 (SDK + Derived). The 5-bit tag and the 8 reserved IDs are tagged Indep. The per-link GB/s is derived at both clocks.
- A7 fixed: the formula now reads "4 ports × 2 (in + out) × ~850k routers × 1.1 GHz" and gives the range 2.1–2.4×10^17 b/s (745,500 positions vs 850k).
- A8 fixed: the hint now matches the code (hop 1, ramp up 2, ramp down 2, relay +1). The simulator models ramp-down explicitly.

## Pedagogy
- P1 fixed: the checkerboard "why" is rewritten around "any rx → all tx". Collisions are a separate warn callout. The quiz answer is updated.
- P2 fixed: new h3 "Nothing is dropped: back-pressure", plus the back-pressure widget.
- P3 fixed: a "virtual channel" paragraph with a railway analogy; the widget shows the shared link.
- P4 fixed: wavelet figure text and RAMP label ("WSE-3: input queue"), pointing to Ch. 5.
- P5 fixed: switch sentence corrected; control wavelet defined; ctrl flag drawn in the wavelet figure (as a schematic, since the header layout is unpublished).
- P6 fixed: "Broken: row reduce on ONE color" simulator pattern with a "Fix it →" button; prose points to it.
- P7 fixed: "Why static?" paragraph, with a link to Ch. 13.
- P8 fixed: pipelining worked example, the measured table, the stream-time calculator and a quiz question.
- P9 fixed: corner turn added ("Four shapes", plus a simulator pattern); quiz adds multicast, corner-turn and 8-color questions.
- P10 fixed: memcpy, SdkLayout and color 20 glossed; Lab chapter numbers given. The filter-bank detail is kept but quantified (A5).
- P11 fixed: "5-bit tag → 32 IDs; 0–23 routable; 24–31 not". The planner shows "20 usable".
- P12 fixed: ×2 explained; chip and clock stated; per-link GB/s compared with ~23 GB/s SRAM (Ch. 3).
- P13 fixed: color swap described as the hardware checkerboard; the filter index is linked to sparse data. The review said Ch. 3, but the sparse index lives in Ch. 5, so the link points to Ch. 5.
- P14 fixed: "checkerboard" defined at first use (column parity; 2-D adds rows).

## Visuals
- V1 partially fixed: relies on the shared phone fix (min-width 620 with an inner scroll). New SVGs keep text ≥ 10–11 user units in viewBoxes ≤ 760. There is no separate narrow layout.
- V2 fixed: the router moved right, the WEST stub shortened and the text wrapped. No overlaps at 1100 px in light or dark.
- V3 fixed: explicit ramp-down (2 ticks). Point to point now delivers at cycle 5, pass-through at cycle 9.
- V4 fixed: direction lanes (eastbound above, westbound below; S/N offset in x), arrowheads per color, and flits animated along the link with requestAnimationFrame.
- V5 fixed: the counter now reads "on links · on ramps · waiting in CE · delivered".
- V6 fixed: step is a no-op when done; Run resets a finished run; dropped and collision counts shown in red.
- V7 fixed: PEs are tabbable buttons with Enter/Space; the readouts are aria-live. The static layer is no longer rebuilt each tick, so focus is kept.
- V8 fixed: replaced by the planner (green "20 usable" bar, red memcpy, Lab counts corrected).
- V9 fixed: per-PE rule lines under each PE; end PEs show one rule; padding tightened.
- V10 fixed: per-pattern color legend, opacity 0.75, lanes.

## Depth
- D1 fixed: the "one 16-bit register" subsection, the register-bit SVG with worked 0x114 / 0x74, the measured cslc error, an inspector note "WSE-3: NOT ALLOWED" and a quiz item.
- D2 fixed: topic-06 code, the 8-step trace table, and a simulator pattern that reproduces E=0 S=2 N=4 W=6.
- D3 fixed: control wavelet subsection and bit-field SVG (single-command form), pop_mode note (tagged Derived), 0x015F0000 example.
- D4 fixed: teardown h3 (task 29, teardown-pending, `@set_local_color_config`, collectives_2d with 2 colors per axis). "Configured once" is qualified. The 3-panel collectives diagram was skipped.
- D5 fixed: range-filter trace (prose + simulator pattern), counter-filter round-robin paragraph, 6-filter counts. The 4×4 counter table is summarised, not reproduced.
- D6 fixed: new h2 "Reaching PEs you have no route to" with a diagonal-relay SVG (game of life) and a histogram-torus mention. The folded-ring diagram was skipped.
- D7 fixed: pipelining numbers plus measured simulator slopes; the ~7 cycles/PE for an add-and-relay is cited from Ch. 11. The gemv-08 example was not added (the 100-PE example covers the same point).
- D8 fixed: "router by the numbers" table, with simulator cycles/hop and clock rows added.
- D9 fixed: color swap mechanism in the checkerboard caption. The quiz item was skipped, because which PEs run blue_task depends on WTT details not verified here.
- D10 partially fixed: (b) hop latency measured and tabled. (a) `--out-routes` was skipped: cslc 2.10.1 `--help` does not list it and I could not verify it.
- D11 fixed: switch and range-filter patterns plus the WSE-3 rx note in the inspector.

Counts: 43 findings. 41 fixed (D4, D5, D6 and D7 with some sub-items trimmed, as noted), 2 partially fixed (V1, D10), 0 skipped.

## New visuals / widgets
1. Simulator patterns: Broken one-color reduce (with collision and extra-receipt detection, plus "Fix it →"), Corner turn, Switch (topic-06), Range filter (topic-08). The simulator was rebuilt with explicit ramps, lanes, arrows, animation, keyboard access and verdicts.
2. "One link, two colors" back-pressure / shared-bandwidth widget (stall toggle, c1 rate slider).
3. Stream-time calculator (distance, length, hop cost 1 [Indep] / 2 [Measured], clock 1.1 GHz / 850 MHz).
4. Route-register bit diagram (WSE-2 vs WSE-3).
5. Control-wavelet bit-field diagram.
6. Checkerboard figure with per-PE rules.
7. Diagonal-relay figure.
8. Color-budget planner (replaces the static strip).
9. Measured hop-latency table and the router-by-numbers table.

Verified with Playwright at 1100 and 390 px, light and dark: no page or console errors, and scrollWidth equals innerWidth. All 9 simulator patterns run to completion with the expected deliveries; Broken correctly reports wrong sums, extra receipts and collisions. Screenshots were deleted.

## Left for later
- A real narrow (phone) layout for the simulator and figures, instead of the inner horizontal scroll.
- A 2-D checkerboard figure (N7) and the collectives_2d teardown 3-panel diagram (D4).
- The WSE-2 streaming result of ~2 cycles/wavelet in the round-trip test is unexplained.
- Whether a range filter drops before forwarding or only before the CE. The page describes the observable topic-08 behaviour (the stream continues east).
