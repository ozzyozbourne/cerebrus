# R4 fix log: Appendix C, Measuring and observing (appC)

Page edited: `appendix-c-measuring.html` only. One check run: I compiled `01-saxpy/timed` (WSE-3, N = 256, PAD 0 and PAD 1) in `/home/user/cerebras-sdk/tmp/r4fix-appC/` and ran `cs_readelf --symbols`. No simulation was run, and the directory has been deleted.
- PAD 0: x at byte 0x0c20, y at 0x1020.
- PAD 1: y at 0x1024.

## Errors
- **E1** Fixed.
  - The paragraph now says the 761-cycle T01 run is three things in turn. It starts during the argument pushes (an earlier push is the separate run 3285–3305). It contains the function, from @3608 to `UBLK` at @3902. It then runs 211 cycles into the next command (the D2H), whose tasks start at @4119. The paragraph also gives the cause: `trace_tasks.py` merges same-task gaps of under 40 cycles.
  - In `#nest-svg`, the bar is solid up to `UBLK` @3902 and has a divider there. The span from 3903 to 4113 is pale and labelled "next command (D2H of y)". The row title, caption and aria-label are updated.
- **E2** Fixed. The Msg widget now says: `^` marks the first instruction of a task activation, and `v` marks the task's last instruction (opcode ending in `.T`).
- **E3** Fixed. The marker is now written as `[ ] U0`, both in the widget hint and in the lead-in to the trace excerpt.
- **E4** Fixed.
  - The sentence now reads "program 01 at N = 64 on WSE-3 (7,740 in all; examples below use N = 256)". It gives H2D 1,355 / 1,291, D2H ≈4,440 and `@fmacs` ≈130, tagged Measured, Ch 11.
  - The link now points to Ch 11 `#inside` ("What happens inside, in order"), which already exists.
- **E5** Already fixed on the Ch 11 side. Ch 11 l.220 now says "unreliable" and cites 5,260 vs 8,905. No change was needed here.

## Explanation problems
- **X1** Fixed. The arithmetic is now written out: instrument = 5 + 4 NOPs + 1 = 10, and op = 2 DSD loads + 3 fill = 5. The page adds that the NOP attribution is inferred from the 10-cycle total, not seen directly.
- **X2** Fixed.
  - The "Synchronise, then correct" bullet is now four numbered steps: sync, signal, correction, max/min.
  - It names `(w + h − 2) − (px + py)` as the Manhattan hop count from the bottom-right PE.
  - It adds a 3 × 3 worked line. PE (0,0) is 4 hops away, so the host takes 4 off its `time_ref`. On WSE-3 the true delay is 8, which leaves a 4-cycle residual.
  - Correction to the report: the SDK `run.py` *subtracts* the delay from `time_ref`, which I checked. The page says this rather than "adds 4".
- **X3** Fixed. The `trace_tasks.py` paragraph now states the rule. A new run starts when the task changes or the gap is ≥ 40 cycles. Gaps under 40 are merged, IDLE included, and the paragraph points to the worked example as a case.
- **X4** Fixed. The page uses "bank clash" everywhere: the table legend, the TSC bullet, quiz Q3 and the Seq widget text. The first use links to `g-bank-clash-operand-collision`.

## Connecting gaps
- **G1** Fixed.
  - The TSC bullet now gives the measured `cs_readelf --symbols` addresses: x 0x0c20 and y 0x1020, which are 1,024 B apart, ≡ 0 mod 16 B, so the same bank. With PAD 1, y is at 0x1024, 4 B off.
  - It then states the one-line rule from item 30 (16-byte, 8-bank cycle; same bank halves the rate) and links Ch 6.
- **G2** Fixed. A new paragraph, "Kernels made of tasks", covers the case.
  - The start is stamped in the function that issues the async op or arms the receive.
  - The end is stamped in the task that runs after the last wavelet, on the same PE.
  - Program 03 is the concrete example: `start_timer` / `reduce` / `exit_task`.
  - It links Ch 5 `#activates` and Ch 12 `#measuring`.
- **G3** Fixed.
  - The Lab 5 sentence now says "eleven `mark()` calls, 30–35 cycles each, 7–10 %". The old text said "eight", but Ch 15 says eleven.
  - It explains why `mark()` costs more than a bare stamp: it joins the counter words into 32 bits, subtracts the previous stamp and accumulates into a bucket. The code uses u32, not 48-bit as the report said.
- **G4** Fixed.
  - A new sentence under the trace commands gives the mapping `P(px+4).(py+1)` and why: 3 memcpy columns + 1 halo column on the west, 1 halo row on the north. It gives the Lab 2 example (3,0) → P7.1 and links Ch 7 `#frame` and the glossary `g-fabric-dims-fabric-offsets`.
  - The P4.1 widget text and the decision-chart recipe say the same.
- **G5** Fixed. The `enable_tsc` bullet and pitfall 4 now say that re-enabling at the start of each launched function is fine, as long as both stamps come after it. Program 03's `start_timer` and Lab 5's `f_init` are given as examples.

## Coordinator items 30–38
- **30** Applied: a one-line bank rule plus the measured addresses (see G1). The Ch 6 link goes to `#collisions`, because `#banks` does not exist yet in 06-dsds.html (see below).
- **31** Applied. Pitfall 9 now says `launch()` returns at once and that the next memcpy is what waits and aborts.
- **33** Applied. The page now says "no official WSE-3 clock". It adds the CS-4 press estimate of ~1.4 GHz [Analyst][Unverified] and the derived 0.19 µs, and pitfall 10 is updated to match.
- **34** Already consistent: 2.0/1.0 router hop, 9.2/6.0 through a PE.
- **32, 35, 36, 37** Not touched on this page.
- **38** Applied.
  - Glossary links added for TSC, RPC, H2D/D2H, DSD, sim_stats.json, hop, allreduce, instruction trace, memcpy, fabric offsets, bank clash, task, simprint, cs_readelf, csdb and launch().
  - Lab 5 mention linked.

## Cross-page items about appC
- r4-appA, r4-appD (X5/G3), r4-ch06 (X2), r4-ch10 (X1/G2), r4-ch12 (G7), r4-ch18 (X6): all ask other pages to link to or cite App C. Nothing to change here. The anchors they need (`#tsc`, `#trace`, `#worked`) exist.

## Verification
I tested with Playwright at 1100 px (light) and 390 px (dark).
- Clicked all 7 flow chips and all 12 trace-line parts, and toggled the noise checkbox.
- Zero console or page errors and no horizontal overflow.
- All 48 local links and anchors resolve.
- Checked the `#nest-svg` screenshot: no label overlaps.

## For other pages
- **Ch 6 fixer / coordinator:** item 30 names `06-dsds.html#banks` as the canonical home of the bank table, but it does not exist yet. App C links `#collisions` for now. Retarget it to `#banks` once that anchor exists.
- **Ch 11:** the E4 anchor `#inside` and the E5 wording are both already in place. No action.
