# ch03 · fix log

File edited: `course/03-processing-element.html` (only). The chapter was rewritten around the four reviews; it grew from ~14 KB to ~50 KB.

New measurements for this fix (simulator, SDK 2.10.1; scratch dir `tmp/fix-ch03/` since deleted):
- Reran single-tile-matvec: f32 N=64 → 4,214 cycles (WSE-3), 4,216 (WSE-2); f16 copy N=128 → 5,046 (WSE-3), 8,377 (WSE-2). These match the depth review exactly.
- Reran the stride probe on WSE-3: @fadds over 256 f32 → 162 / 290 / 546 / 799 cycles for stride 1 / 2 / 4 / 8. These match the depth review.
- `cs_readelf -m`: 4,960 B (WSE-3) and 3,458 B (WSE-2) for N=8. `llvm-readelf -S` gives the section map shown in the new memory-map widget. Capacity probe: N=104 links (48,736 B); N=106 fails with "ran out of PE memory for data (section .bss)" and "... for task table".
- **New source on banking:** the `cs_readelf(1)` man page says "The bank a memory access lies in is determined by bits [3:1] of the address … a 32-bit read … is broken into two 16-bit reads … Bank conflicts where concurrent reads and writes target the same bank or the same bank modulo 4 may result in cycle delays." This is now quoted in the chapter.
- An attempt to measure two concurrent async memory-only ops failed. cslc rejects them: "'async' requires at least one fabric or DSR operand" (quoted, tagged Measured). The DSR-operand variant stalled in the simulator, so the chapter makes no measured claim about concurrency throughput.

## Accuracy
| ID | Status | Note |
|---|---|---|
| A1 | fixed | Quiz Q1 now says 16 KB remain, minus ~4.5 KB of measured overhead. |
| A2 | fixed | GEMV figure replaced by the matvec traffic stepper. Relative = 4(N²+2N), absolute = 4(3N²+N); the difference is y, not x. Says it targets CS-2 at 850 MHz. |
| A3 | fixed | Anatomy caption tags each source separately (HC2024, HC22, academic, SDK, Measured). |
| A4 | fixed | Size now reads "WSE-2: 0.039 mm² (HC22)" and "WSE-3: ~0.05 mm² (blog)", matching ch02. The caption notes that sources differ. |
| A5 | fixed (superseded by D2) | The "~2 KB" figure is gone. The widget uses the measured 4,636 B (WSE-3) and 3,134 B (WSE-2). |
| A6 | fixed | 8/16-way tagged Vendor HC2024; 4-wide on WSE-1/2 tagged Secondary source. |
| A7 | fixed | The bit ruler reads "16-bit value (i16 in topic-04)". |
| A8 | fixed | Sparsity paragraph rewritten. Hardware zero-filtering (Vendor HC22/MICRO-54) is separated from the SDK convention. Says headline peaks count skipped multiplies. |
| A9 | fixed | The software-managed cache no longer says "the compiler decides". |
| A10 | fixed | Banks: single-port and single-cycle tagged HC22, 6 KB tagged academic. The interleaving claim is replaced by the two-model section (see item 2 of the brief). |
| A11 | fixed | The sanity check is now a derivation chain giving 21–27 B/cycle, about 5–7 f32 words, at 1.1 GHz (HC22) to 850 MHz (SDK). |
| A12 | fixed | "Eight microthreads" tagged Vendor; the queue-ID default is stated. |
| A13 | fixed | Control paragraph covers data, local and finishing-op activation. |
| A14 | fixed | "OS / software threads"; "instruction cache (none documented)"; the lede says "WSE-3 … about 900,000 [Vendor]". |
| A15 | fixed | The A3 caption tags 24 colors as SDK. |

## Pedagogy
| ID | Status | Note |
|---|---|---|
| P1 | fixed | New subsection "Microthreads: overlap, not more FLOPs" with a definition, the shared datapath (secondary) and main-thread priority (SDK). The occupancy timeline widget shows it. |
| P2 | fixed | Traffic stepper plus text: N=64 is 16,896 vs 49,408 B, 2.9×, measured. |
| P3 | fixed | Objective and section retitled. Hardware and software split. "What it costs" list, with a corrected index-range point (the i16 index covers 0–32,767; enough for one PE's array). |
| P4 | fixed | New "Wavelets, colors and the router, in one paragraph". The figure reads "24 colors (route tags, Ch. 4)". |
| P5 | fixed | "One wavelet's journey" stepper (6 steps, from Lab 2's @fadds) highlights the anatomy parts. |
| P6 | fixed | "Is memory fast enough to feed the math?": 0.17 FLOP/B, versus the H100 ridge from Ch1; measured 11.7 B/cycle. The suggested WSE-3 8-wide inference was not added. |
| P7 | fixed | Measured f32 ≈ 1/cycle and f16 3.2/2.0 per cycle (from D1) replace the "unknown" note. The lanes are labelled. |
| P8 | fixed | Quiz rewritten: 6 applied questions covering budget, cycles, microthreads, matvec traffic, stride/banks and sparsity. |
| P9 | fixed | Covered by the bank explorer and the measured stride table (SDK 16-bit rule rather than word mod 8). |
| P10 | fixed | Same text as A9. |
| P11 | fixed | The hint defines x, y, b. "FITS, barely" appears under 1 KB spare. Uses the measured overhead instead of a 46 KB line. |
| P12 | fixed | GPR/DSR expanded in the text; "activated AND not blocked"; Lab 3 references now name Chapters 5 and 12. |
| P13 | fixed | Lede states PE = core = tile. 4-wide is secondary. Size sourced. |
| P14 | fixed | W port drawn. All five ports have arrows at both ends. The "omitted" note is removed. |
| P15 | fixed | Clock is WSE-2 1.1 GHz (HC22) and SDK 850 MHz, per cross-notes 2 and 10. |

## Visuals
| ID | Status | Note |
|---|---|---|
| V1 | fixed | Note deleted. RAMP label sits below its arrow, clear of the router. |
| V2 | fixed | Five bidirectional ports via `orient="auto-start-reverse"`. W is routed over the CE, which the label says. |
| V3 | fixed | Uses the coordinator's shared phone rule (620 px min-width, scroll in box). Page has no horizontal overflow at 390 px. Long tags wrap on phones (local style). |
| V4 | fixed | Line shortened to font 11, "single-cycle · banked (see Memory) · code AND data". |
| V5 | fixed | All JS colours use classes (f-*, soft classes) or `cssVar`. Survives the theme toggle (checked). |
| V6 | fixed | Legend uses real coloured swatches. |
| V7 | fixed | Bar scales to max(total, used). Overflow has a dashed red outline and an "over by X KB" label. Verdict is coloured. |
| V8 | fixed | Sliders go to 160 in steps of 2. Shows the largest square block (104 at f32/WSE-3, which matches the measured link limit). The chip selector replaces the code slider. |
| V9 | fixed | One fact per line; `aria-live` and `aria-describedby` added. |
| V10 | fixed | Replaced by the traffic stepper. |
| V11 | fixed | Same as A7. |
| V12 | fixed | "✕ OS / software threads". |
| V13 | fixed | Lane label: "8 × FP16 lanes, 16 × INT8 (WSE-3) · f32 ≈ 1 FMA/cycle". |

## Depth
| ID | Status | Note |
|---|---|---|
| D1 | fixed (partially) | "How fast is one PE?" has the table, the fit 54 + N + N², and derived peak FLOPs. Quiz question added. The cycle model sits in the matvec stepper readout; no separate plot widget. |
| D2 | fixed | Memory-map widget (WSE-3/WSE-2 toggle, zoom on the first 5 KB, config block above 48 KB). Capacity probe text. Budget uses the measured overhead. |
| D3 | fixed | Microthread mechanism, priorities and a generation table (queues 8/6 vs 8/8 from csl-libs). The timeline widget covers the optional diagram. |
| D4 | fixed | Both bank models are presented with sources, plus the explorer widget with a model toggle and the stride table. States which model the SDK shows, and notes a derived inconsistency (19 B/cycle > 8 × 16-bit). |
| D5 | fixed | DSR paragraph and the 5-line `save_address` snippet. |
| D6 | fixed | 11.7 B/cycle measured is stated in the bandwidth and no-caches sections. |
| D7 | fixed | Table "What changed per PE, WSE-2 → WSE-3", each row tagged. Fabric-coordinate mask, filter counts and PRNG rows omitted for focus. |
| D8 | fixed | 16-bit word sentence (word_size = 2, u16 registers). |
| D9 | fixed | Collapsible "Try it yourself" box, including `cs_readelf --sym`. |

## Brief-specific items
- Speeds, budget (4,636 B ≈ 4.5 KiB; cross-note 13's "4.6 KB" is the same number in decimal kB, and the text says so; ~44,500 B usable), matvec y-correction, microthread overlap, sparsity costs, clock, W port and two-way ports: all done.
- Microthread hang (cross-note 1/11): uses "FATAL … trying to term ut_instr[3], but it's not ours" at ~2,123 (WSE-3) / ~2,125 (WSE-2), and the host hangs. No "cycle 1,894" claim.
- Bank interleaving conflict: both models are shown with sources. The chapter says plainly that the SDK (cs_readelf man page and `--sym` Banks column) is the observable one.

## New visuals / widgets
1. Wavelet-journey stepper, linked to the anatomy SVG (highlights parts).
2. Address → bank explorer (SDK rule vs academic model, dtype, stride, start; per-bank histogram; measured cycles).
3. PE memory map (WSE-3/WSE-2, measured sections).
4. Budget widget rebuilt with a bank view (8 banks filled evenly, overflow shown above).
5. Microthread occupancy timeline (serial vs async vs collision; illustrative, tagged Derived).
6. Matvec memory-traffic stepper (step/play/reset, N 4–12, relative vs absolute counters).
7. Sparse wavelet encoder (sparsity slider, clickable wavelets, 32-bit ruler).
8. Static: bandwidth derivation chain (HTML flex); `<title>` hover text on anatomy blocks.

Verified with Playwright at 1100 and 390 px, light and dark, and with the ◐ toggle. Every control was exercised. No page or console errors, and no horizontal page overflow.

## Left for later
- A measured demonstration that concurrent microthreads share one datapath. The attempt stalled; the claim stays tagged Secondary.
- Why strides 4 and 8 cost differently although they hit the same banks (possibly the "same bank modulo 4" rule); not investigated.
- Physical bank width: not published. The SDK numbering versus the academic "32-bit word" description stays unresolved.
- ch02 still says "8 single-cycle 32-bit banks … 32 B/cycle ceiling". Its fixer or the coordinator may want to point to ch03's two-model note.
- Ch09 could teach `cs_readelf -m/--sym` (depth review's out-of-scope note).
