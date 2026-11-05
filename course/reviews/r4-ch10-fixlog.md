# R4 fix log · Ch 10 "CSL and the toolchain" (10-csl-toolchain.html)

Edited only 10-csl-toolchain.html (not a generated page). No experiments were run; all new numbers come from the R4 audit's measurements (r4-ch10, r4-appB) or the SDK files. Verified with Playwright at 1100 px (light) and 390 px (dark): no console or page errors, no horizontal overflow, all 70 in-page and cross-page links resolve. Memory, wrapper (CS-2 mode), tour (pe_program 13/18/24) and run-stepper widgets were driven.

## Errors
- **E1 Fixed.** #builds: the wrapper checks and frame are now stage 5, run only after cslc-driver succeeds. The page says a fabric-size RuntimeError arrives after your program compiles (~24 s) and that out/bin/ already holds your ELFs. Updated the legend (main() → driver → _generate_memcpy), the pipeline-figure box text and its aria-label, and the #fabric-size intro.
- **E2 Fixed.** Rewrote the contract summary: a mismatched name or flag and a missing param are compile errors; a missing @export_symbol (array or function), a missing unblock and a get_id typo fail at run time. Added two error-decoder rows, (A) missing x export → TypeError at memcpy_h2d and (B) "xx" → "not declared during layout evaluation", and changed "three" to "four" that compile cleanly. Also added a "Break it" item and extended the tour note for pe_program:24.
- **E3 Fixed.** #fabric-size quotes the README's "must be 750,994" and its "Dims here refers to the dimensions of the program rectangle", plus sweep.py's width+7/height+2 (= 757,996). The CS-2 fabric is tagged Unverified, and 743 × 992 is kept only as Derived from the README reading. Updated the figure caption, flags row, wrapper widget option and readout, and Q3.
- **E4 Fixed.** The memory widget's threshold is now soft: an amber band of ±16 B around 49,152 B, labelled "at the edge … build and check". The readout gives "largest N ≈ 5,614–5,615 (Derived; Measured 5,615 links at exactly 49,152 B; 5,616 and 5,620 fail)", plus 5,784/5,790 for WSE-2. Added a table row for N = 5,615 (fixed part 4,232 B by alignment, per r4-appB). "Even an empty program" is now "SAXPY minus its two arrays".
- **E5 Fixed.** Rule 4 now reads "every param without a default"; color params may come from --colors.

## Explanation problems
- **X1 Fixed.** Removed every "Chapter 11 review" and "course reviews" reference. They now read "our parallel runs for Lab 1" (linked to 11#noise), with links to Appendix C (#noise) and Lab 2.
- **X2 Fixed.** Explained sw-1 / rx=R as a second router position that memcpy switches to with a control wavelet, so the PE's own D2H data joins the eastbound stream. Linked to 04-fabric.html#switches.
- **X3 Fixed.** Added a parenthetical defining width_west_buf/width_east_buf (0 by default), linked to #flags.
- **X4 Fixed.** Added definitions of port, adaptor and demux/mux, linked to Ch 7 #frame. Closed the still-open ch09-fixlog item with a new inline-SVG placement figure for sdklayout-03 (four regions, ports and connections copied from run.py, SDK tag, quoted comment).
- **X5 Fixed.** The tour hint now points to #language for the syntax.

## Connecting gaps
- **G1 Fixed.** The tour note for pe_program:18 and stepper step 5 now explain the 2 cycles/element: x and y share an SRAM bank, and one pad word gives 1/element. Uses the item-30 one-line rule and links 06-dsds.html#banks and Lab 1 #kernel-time.
- **G2 Fixed.** New #tsc subsection: verbatim excerpts from program 03 (pe_program enable_tsc/get_timestamp, run.py read_tsc 48-bit join), the same-PE-only caution (note 26), and links to Appendix C #tsc and Lab 3 #tsc.
- **G3 Fixed.** New #task-syntax block (full width, after "Hardware parts") with verbatim lines from program 02 (data task, ID, bind, WSE-3 queue) and program 03 (local task, .async/.activate, @bind_local_task), plus a note on @activate. Linked to Ch 5, Ch 6 #async and Lab 1.
- **G4 Fixed.** Replaced the 4-line route excerpt with program 03 layout.csl lines 16–31 verbatim (checked by diff) and 3 pins: compile-time loop, parity (quoting the file's comment, linked to Ch 4 #checkerboard), and role × parity → 4 ELFs.
- **G5 Fixed.** The pe_program card says there is no main and that code runs only on an RPC or a woken task. Stepper step 1 explains the same.
- **G6 Fixed.** Added to the --params callout that the unsigned value is converted to the declared type (N: i16) and that defaulted params need no entry.
- **G7 Fixed.** The memory text now explains the task table and why the linker's first error names it. The approximate split (~3.2 KB code + ~1 KB task table, Derived from note 13) is in the widget readout and the bar label.
- **G8 Fixed** (with E3). The page says no CS-3 fabric size is in the SDK files and that you get it from your system.
- **G9 Fixed.** Added glossary links for CSL, RPC, SdkRuntime, param, comptime, DSR, command stream, memcpy frame, halo, router, color, TSC, task ID, sim.log/sim_stats.json, instruction trace, kernel stall and SdkLayout. There is no glossary id for ELF or CTF, so those are not linked.
- **Forward refs Fixed.** "Lab 3 rebuild" now links 13-lab-stencil.html, "difference two runs as Lab 3 does" links 13#measurements, and the remaining plain "Chapter 4", "Ch 7", "Ch 15" and the "Chapter 7" tour notes are links (item 38).

## Cross-page items about this page
- r4-appB E1 (Ch 10 gives only a bracket for the N limit): **Fixed** via E4.
- r4-appA E2 and r4-ch12 X1 are about other pages and only cite Ch 10; nothing to change here.
- Items 30–38: applied item 30 (one-line rule plus a link to #banks) and item 38 (links). The page has no clock, hop, queue-depth or tok/s claims, and its launch() text already matches note 31.

## For other pages
- **Ch 2** (lines ~190, 219, 234, 268) and **Ch 7** (frame calculator and ~line 106): the CS-2 "750 × 994 fabric / ≤ 743 × 992" needs the same caveat. The README calls 750,994 the fabric, but its sweep.py treats it as the program rectangle (fabric 757,996). Tag it Unverified or footnote it (r4-ch02 E4 and r4-ch10 E3). Ch 13 and Ch 18 reuse 743 × 992.
- **Appendix D** E2: the benchmark-libs row filter should include Ch 10 for preconditioned-conjugate-gradient, bicgstab and power-method.
- **Ch 11** X6: link the "exported symbol mutability mismatch" row with `10-csl-toolchain.html#errors`. New anchors on this page that other pages can link to: `#task-syntax`, `#tsc`, `#sdklayout-03`.
- **Glossary**: there are no ids for ELF or CTF, so consider adding them.
