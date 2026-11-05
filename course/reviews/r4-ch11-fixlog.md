# R4 fix log · ch11 · Lab 1 (src/11-lab-first-programs.html)

Experiments (in /home/user/cerebras-sdk/tmp/r4fix-ch11/, now deleted):
- `01-saxpy/timed` on WSE-2, f16, PAD 4: N = 64 / 1,024 / 4,096 gives 30 / 270 / 1,038 TSC cycles.
- Program 02 traced on WSE-3 with and without `wait_done`. memcpy's own task runs on P4.1 (T01/T21/T29/T30) were captured for G2. Task and read times match the page's existing data to within ±1–6 cycles up to the stats readback.

| ID | Status | Note |
|---|---|---|
| E1 | Fixed | Added an "f16 WSE-2, PAD 4" column (30 / 270 / 1,038, measured). Reworded the f16 bullet: 4/cycle on both chips when the sources sit 4 banks apart, 2/cycle on WSE-2 otherwise. Dropped "FP16 SIMD doubled". Exercise 4 now says "(unpadded)". Removed "WSE-3's gains are in f16". |
| E2 | Fixed | The slope is now "3 + 3 + 2 + 56 ≈ 64 (out = T21 35 + T30 21)" [Derived], with a note that the in-cost is about 5 at N = 64. Widget step 13 and the D2H bullet now say 56, not 60. |
| E3 | Fixed | Replaced with "about 15 cycles of fixed cost per measurement: op start-up plus the timestamp reads together". Removed the separate 10-cycle claim. |
| E4 | Fixed | Now "8 single-ported banks [Vendor]; how addresses map to banks is not vendor-documented (App E issue 2)". |
| E5 | Fixed | The 48 KB tag is now Vendor. |
| X1 | Fixed | Added a paragraph saying PAD counts elements of T (f32 PAD 1 = 4 B = two 16-bit words; f16 PAD 4 = 8 B). |
| X2 | Fixed | Added a line under the memcpy table: for `launch`, nonblock=False waits only until the command is sent. Links Ch 7 #rpc. |
| X3 | Fixed | Changed to "a variant we built (not shipped with the course)". Added the rule that no data task may be bound to the fabin queue unless it is blocked (Ch 5 #rules, pipeline-01). Removed the process wording and the "WSE-2 port stalled" wording. |
| X4 | Fixed | "Two reads and a write" is gone (CCN 30 retires it). The half-width statement is tagged Derived and links Ch 6 #op-speed (the f16 move is near full width). |
| X5 | Fixed | Exercise 5 now gives `SINGULARITYENV_SIMFABRIC_DEBUG=inst_trace bash commands.sh 64 0 1`. |
| X6 | Fixed | Names the "exported symbol mutability mismatch" row and links Ch 10 #errors. |
| G1 | Fixed | The H2D-done bullet now says "pushed into the buffers, not consumed" (pipeline-01 quote) and gives the depths: IQ0 6, IQ2 4, OQ0 2 [SDK memcpy.csl], with the rest of the 16 in the router/relay [Derived]. The Exercise 2 answer gives the model: 16 buffered − 11 drained in the ~830-cycle D2H start = 5 at any N. The without-barrier bullet now says "11 of the 16 drained". The stretch exercise is reframed as the test of this model and uses the CCN 35 depths in place of the vague "few wavelets". |
| G2 | Fixed | New bullet: memcpy's tasks share the core. Spacing is 38 + 21 (T01) = 59 after H2D, 35 + 21 + 38 ≈ 96 during the D2H, and back to ~39 when the stream is blocked. Says why the 40-cycles-per-task model fails. The widget now draws memcpy's task runs as purple blocks on the middle track, with a legend, and the readout names the memcpy task running at the cursor. |
| G3 | Fixed | The f16 bullet states that the same placement rule reverses the chip comparison and links App E #iss-clash. The f32 bullet states the CCN 30 one-line rule and links Ch 6. |
| G4 | Fixed | "Blocked is literal" bullet now maps `T01 BLK Src1:0001` onto Ch 5's blocked bit (link #rules). |
| G5 | Fixed | Quotes the sys_params.csl line "chunk … only support/test chunk = 1" [SDK]. Forward link to Lab 2 #measuring. |
| G6 | Fixed | Added that enable_tsc() zeroes the counter (reset_tsc_counter) [SDK] and that you subtract stamps only on the same PE. Links Lab 2 #measuring and App C #tsc. |
| G7 | Fixed | The figcaption now says memcpy routes MEMCPYH2D_1 RAMP→RAMP on your PE [SDK memcpy/wse3/memcpyh2d.csl:475, verified] and links Ch 4 #routes. |
| App C E4 (cross) | Fixed | Added `id="inside"` to "What happens inside, in order". The App C fixer can link `11-lab-first-programs.html#inside`. |
| App C E5 (cross) | Fixed | "Subtracting whole-run totals … is unreliable", with Ch 13's 5,260 vs 8,905 and a link to 13 #tsc. |
| Ch 15 G8 / CCN 38 | Fixed | 14 glossary links on first use: wavelet, task, memcpy, command stream, RPC, unblock_cmd_stream, control wavelet, TSC, DSD, bank clash, trace, input queue, data task, microthread, run-to-completion, fabric DSD, kernel stall. About 20 "Chapter N"/"Lab N" mentions are now section links. All 49 in-page and cross-page hrefs resolve. |
| CCN 30 | Applied | Uses the one-rule statement. Retired "WSE-2 f16 = 2/cycle" as a chip rate and "two reads and a write". Links Ch 6 #collisions, because `#banks` does not exist yet in 06-dsds.html. |
| CCN 31 | Checked | Text already says launch() returns at once. |
| CCN 33 | Applied | Now "No WSE-3 clock is published; at the 850 MHz the SDK benchmarks assume …". |
| CCN 35 | Applied | Queue depths 6/4/2 are cited. pipeline-01's 14 is described as total path buffering. |

Verification: Playwright at 1100 px. Zero console errors. Stepped through the step-through to step 14. The race widget was checked in both modes (27 purple memcpy blocks; readout correct). The TSC table fits (826/826 px).

## For other pages
- Ch 6 (06-dsds.html): once the `#banks` anchor exists, Ch 11's two links to `06-dsds.html#collisions` could point there. Ch 6 also has the "interleaved by 32-bit word [Vendor]" mis-tag (r4 E4).
- App C: link "What happens inside" to `11-lab-first-programs.html#inside` (the anchor now exists).
- Program comments in `programs/01-saxpy/timed/{layout,pe_program}.csl` say "PAD extra words"; PAD is in elements of T. Comment-only fix; no fixer owns 01-saxpy, so the coordinator should decide.
