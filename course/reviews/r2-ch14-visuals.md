# r2 · ch14 (14-lab-gemm.html) · visuals review

**Method.** I opened the page in Playwright/Chromium at 1100×900 and 390×900, in light and dark, and clicked ◐ once at 1100 px. I drove every control:
- **Stepper:** P = 2/4/5/6, T = 4–32, Play/Pause, Next phase, Reset, and clicking a PE.
- **Chart:** chip, y-axis, the T slider, and hovering a point.
- **Budget:** P = 4/743; Mt, Kt, Nt = 8/45/64/100; both kernels, both chips.

I inspected the element screenshots.

**Result.** There were no page or console errors and no horizontal page overflow at any size. The ◐ toggle re-themes all four drawings live. The host-layout figure is correct (PE (0,0) gets 0 4 1 5, then PE (1,0) gets 2 6 3 7, and so on) and legible in both themes.

## Findings

### V1 [high] The budget calculator says "fits" when the timestamp array overflows memory, which undercuts the wafer-scale section
- **Location:** `#bud`, `budDraw()`: `fit = tiles <= okB ? …`. The same assumption appears in the "Scaling up" section.
- **Problem:** The fit test compares only the tile bytes against the link limits and ignores the timestamps. The timestamp array really scales with P: `var stamp = @zeros([3 * (3 * P + 2)]u16)` (pe_program.csl:43).
- **Evidence:** At P = 743 with T = 45 on WSE-2, the readout says `40,500 B of tiles + 13386 B timestamps → fits (at or below a size that linked)`. The bar itself shows 53.9 KB, running past both limit markers and the 48 KB box (screenshot `bud-743-45-0-wse2`). So the "Kernel 0, T = 45 at P = 743" and "Kernel 1, T = 39" extrapolations use a configuration that this program could not link as written. The tiles use 40.5 KB, and the 0.3 KB of timestamps measured at P = 4 grows to 13 KB at P = 743.
- **Fix, calculator:** Test `tiles + ts - 84` against the limits (84 B is what was linked at P = 4). Add a line such as "timestamps grow as 6·(3P+2) B; drop or cap them for big grids".
- **Fix, Scaling section:** Either state the assumption ("with the per-step stamps removed, keep only start/end: 12 B") or use the largest T that fits with the stamps included. Hand this to the accuracy/depth fixer as well.

### V2 [med] The memory bar overflows its SVG and clips the labels
- **Location:** `#bud-mem`. The scale is fixed at `W / 49152`, and segments are drawn without any cap.
- **Evidence:**
  - At Mt = Kt = Nt = 64 (98 KB), only "A tile | A buffer | B tile" are visible. The C tile, the product tile and the timestamps are drawn beyond x = 670 and clipped. The viewer cannot see how far over budget the design is.
  - The marker label "smallest that failed 41.4 KB" is cut to "smallest that fa…" or "…failed 4" whenever the failed limit sits near the right edge. This happens with WSE-3 kernel 1 and at P = 743.
  - The green and red marker lines are drawn over the "B tile" label.
- **Fix:**
  - Scale the bar to `max(49152, arr) * 1.05`.
  - Draw a red hatched "over 48 KB" zone past the 48 KB tick.
  - Anchor marker labels with `text-anchor:end` when x > 560.
  - Draw the markers before the segment labels, or put the segment labels in a halo (`.halo-txt`).

### V3 [med] The chart's per-multiply-add view silently clamps the broadcast line to the floor
- **Location:** `#ch`, `ly()`, which clamps with `Math.max(ylo, …)` where `ylo = 0.5`.
- **Problem:** Broadcast per MAC is (b0 + 2T²)/T³, which falls below 0.5 at about T ≥ 11.
- **Evidence:** In the WSE-2 and WSE-3 "cycles per multiply-add" views, the purple line drops to the axis and then runs flat at 0.5. The measured points at T = 16 and 32 sit on the floor too (screenshot `ch-wse2mac`). This suggests broadcast costs a constant 0.5 cycle per MAC, when the true values are 0.25 and 0.08.
- **Fix:** Set `ylo = 0.05` in per-MAC mode and add ticks at 0.1 and 0.2. Alternatively, in that mode plot only the compute series and the ideal, and print the broadcast share in the readout.

### V4 [med] The stepper's C matrix overlaps the legend and does not show progress
- **Location:** `#st-svg`, the call `mat(M0 + 60, 200, …)` and the legend at y = 318.
- **Problem 1:** The C matrix spans y = 200–320, which runs over the legend row. "C done (fraction)" is struck through by the bottom row of C blocks at every P (screenshots `st`, `st-P5`, `st-P6`).
- **Problem 2:** The hint says "Right: the same step on the whole matrices". Yet every C block is fully green from step 0, while the left grid fills progressively. The two halves contradict each other.
- **Fix:**
  - Move C to y = 190 with `MS = 110`, or move the legend to y = 340 and raise the viewBox height to 345.
  - Give the C blocks a partial-fill bar like the left grid's (`(s+ph)/P`), or use `class: "box"` until the final step.
  - Remove the no-op `(r === sy ? "acc" : "acc")` in the A matrix, or give the selected row a distinct class.

### V5 [med] The stepper's "arrows" are stubs that show no direction and no root fan-out
- **Location:** `#st-svg`, the routes loop.
- **Problem:** Each non-root cell gets a short line from its edge facing the root toward its centre. The lines have no arrowheads, do not connect between cells, and nothing leaves the root, even though the hint says "the root's router sends both ways".
- **Evidence:** In the P = 4, step 0 screenshot the stubs look like dashes. It is impossible to tell that data flows away from column 0 or that each router forwards onward.
- **Fix:**
  - Draw one continuous polyline per row, from the root cell outward in both directions, with an SVG `<marker>` arrowhead at each hop. Use one polyline per column for B in the same way.
  - Add a small "RAMP" tick into each receiving PE.
  - Optional: animate a dash offset during the broadcast phase to show streaming.

### V6 [low] The stepper's green "C done" fill is nearly invisible in dark mode
- **Location:** `#st-svg`, the fill drawn with `class: "grn", opacity: .55` over `.box`.
- **Evidence:** In the dark P = 2 compute screenshot, the fully done cells are hard to tell apart from empty ones, because green-soft at 0.55 opacity sits on surface-2.
- **Fix:** Use `opacity: .85`, or fill with `var(--green)` at about 0.35 opacity, and keep the stroke.
- **Also at P = 6:** G = 46.7 < 50 hides the PE labels. Lower the label threshold to 40 and use a font size of 10.

### V7 [low] The budget inputs clamp silently
- **Location:** `#bud`, `clampI`.
- **Evidence:** Typing Mt = 100 leaves "100" in the field, but the readout computes with 64 (`6,656 B … C 256 × 32`). The `max` attributes do not stop typed values.
- **Fix:** Write the clamped value back to the field (`$(id).value = v`), or show "Mt capped at 64".
- **Also:** The `P > 743 ? " (too big)"` branch can never fire, because P is clamped to 743 first. Remove it, or clamp to a higher value and keep the warning.

### V8 [low] Small inconsistencies in the chart readout and legend
- **Readout label:** The readout prints "WSE3" and "WSE2" (`chip.toUpperCase()`), while the rest of the page says WSE-3 and WSE-2.
- **Legend:** It shows only an orange dot for "measured (P = 4)". The purple (broadcast) and blue (kernel 1) measured dots are not explained. Use the label "measured (P = 4; colour = series)" or show three dots.
- **Hover state:** It is never cleared. The highlighted table row and the "measured point:" line stay after the mouse leaves. Add `mouseleave` to restore `chBase` and clear the row background.
- **Touch and keyboard:** Hover is the only way to read a point. Add `click` and `tabindex=0` with focus handlers for touch and keyboard users.

### V9 [low] The stepper readout's cycle estimate differs from the measured value without saying so
- **Evidence:** At P = 4, T = 8 the readout shows compute ≈ 3,082 and kernel ≈ 14,921. The measured values are 2,903 and 14,422 (table row `wse3|0|4|8`).
- **Fix:** When the (P, T) pair has a measured run in `RUNS`, append "(measured: 14,422)".

### V10 [low] Phone layout
- At 390 px both widget SVGs scroll inside their boxes, as designed. For the stepper this means the matrix half, which carries the "whole matrices" story, starts entirely off-screen.
- The budget bar at the defaults (1.3 KB of 48 KB) is a sliver a few pixels wide.
- This is optional: at ≤ 680 px, stack the matrices under the grid (viewBox 360 × 560). For the budget bar, label the free space ("46.7 KB not used by tiles").

## Missing visuals that would help most

### M1 [med] A sequence diagram for one `<collectives_2d>` broadcast
- **Where:** "One broadcast, end to end".
- **What:** Lanes for the root, a middle PE and the end PE, each with router and CE. Steps:
  1. `reset_routes`, then exit teardown
  2. the data stream
  3. the TEARDOWN control wavelet following the data
  4. task 29 → lock (activate)
  5. the FSM → lock (unblock)
  6. the callback
- **Why:** This is the densest section of the chapter, and it is prose only today. A second panel could show the next step's root waiting behind a router that is still in teardown (the back-pressure case).

### M2 [low] A two-bit join diagram for `compute`
- **Where:** "The task that waits on two networks".
- **What:** Activated/blocked bits, with `x_done` and `y_done` arriving in either order, and `@block` re-arming the join. Chapter 5 likely has a reusable drawing.

### M3 [low] A bank-clash picture
- **Where:** The callout.
- **What:** Four memory banks (address mod 4). Draw the column of C and the column of A as two streams starting in the same bank (clash, 2 cycles per element) against offset banks (1 cycle per element).
- **Why:** The 4,096-cycle "exactly one per MAC" result is the chapter's key insight, and it currently has no drawing.

Summary counts: high 1 · med 5 (V2–V5, M1) · low 7 (V6–V10, M2, M3).
