# Round-4 audit summary (correctness, explanation, connecting gaps)

23 auditors, one per page, brief in R4_AUDIT_BRIEF.md. Per-page reports: r4-<page>.md.

## Verdicts

| Page | Verdict | Top item |
|---|---|---|
| ch01 | **Has errors** | "Compute is not the limit" uses the all-user total; per user, compute is the tighter limit. Decode calculator contradicts its own note and table. |
| ch02 | Mostly correct | "Wavelet" used before Ch 4 defines it; FLOPs math assumes an unmeasured 8-wide f16 rate. |
| ch03 | Mostly correct | Stale f16 rates (3.2/2.0) with wrong "memory traffic" reason; queues used before defined. |
| ch04 | Mostly correct | Never shows the PE-code half of a route (fabin/fabout DSD + queue); stale ~7-cycle relay cost (should be ≈9.2/6.0). |
| ch05 | Mostly correct | Says queue depth "not published"; memcpy.csl gives 6/4/2. Lab 3 used as example without introduction. |
| ch06 | Mostly correct | Bank model (word mod 8, tagged Vendor) conflicts with Ch 3 / SDK 16-bit-bank rule; own SAXPY example is the half-speed clashing layout. |
| ch07 | Mostly correct | Correct about `launch()` returning at once, but Ch 12–15 and programs 06/07 comments contradict it (re-measured: launch 0.00 s, next memcpy 5.06 s). |
| ch08 | Mostly correct | "All activations stay on wafer" doesn't fit 44 GB at the stated token counts; no mechanism given. |
| ch09 | Mostly correct | No r3 fixes applied; conclusions assume a clock (press now estimates ~1.4 GHz); GEMV split across a region never shown. |
| ch10 | Mostly correct | cslc stage order wrong; missing `@export_symbol` is a runtime TypeError, not a compile error; no task syntax before Lab 1. |
| ch11 | Mostly correct | "WSE-3 doubles f16" is a bank-placement artefact (WSE-2 PAD 4: 270 vs 526 cycles); queue capacity never tied to the missing-values bug. |
| ch12 | Mostly correct | gemv-08 misdescribed as store-and-forward; launch() claim wrong; 16×7≠128 back-pressure; tree/chain crossover contradicts Ch 14. |
| ch13 | Mostly correct | Re-run matches exactly. Formula never mapped to the shifted DSDs or stability limit; "the capstone" is stale. |
| ch14 | Mostly correct | Doesn't point to Ch 6's measured `@map` fix for its main overhead; quiz Q7 numbers wrong; 2-D zero-stride DSDs unexplained. |
| ch15 | Mostly correct | Presents composition as new, ignoring Lab 4; 65 vs 14.6 cycles/message unexplained; column reduce scope wrong. |
| ch16 | Mostly correct | Zero hyperlinks; Ethernet "7× slower" ratio wrong (real gap is latency ~70–100×); no compute-per-cycle bridge to PEs. |
| ch17 | Mostly correct | FLOP/B "rises every generation" only across precisions; contradicts Ch 6 on strided DSDs; measured 86 tok/s never given. |
| ch18 | Mostly correct | Chooser still uses aggregate as per-user ceiling; three findings (compute-bound, read rate, per-PE efficiency) never joined. |
| appA | Mostly correct | No entries for core CSL builtins (`@get_dsd`, `sys_mod`, `@get_color`, …); Tokens/s entry says ~7,500 (should be 2,000–4,000). |
| appB | Mostly correct | Never covers Labs 4–5; memory checker off by a few bytes (5,615 links, checker says fails). |
| appC | Mostly correct | "761-cycle whole RPC" includes the next D2H; no pattern for timing wavelet-triggered kernels. |
| appD | Mostly correct | All 59 examples verified; gemv series split out of order; ladder sends learners to run CSL before Ch 10. |
| appE | Mostly correct | Its own measurements refute "WSE-2 f16 ≈2/cycle"; several Unverified items now verifiable from web. |

## Cross-course themes (fix once, many pages)

1. **Bank placement rule.** f16/f32 rates on Ch 2, 3, 6, 11, 14, 15, App B, App E, CCN 22 must be restated as layout-dependent (same bank / mod 4 → half speed). One canonical table, linked everywhere.
2. **`launch()` semantics.** Fix Ch 12, 13, 14, 15 and comments in programs/06-summa/pe_program.csl:123, programs/07-cg/pe_program.csl:115,217.
3. **Per-user vs aggregate tok/s.** Ch 1, Ch 18 chooser, App A glossary.
4. **Links.** Almost no chapter links to other chapters or to the glossary (Ch 3, 4, 5, 8, 12, 13, 16 worst; none link `#g-` entries).
5. **Concepts used before taught.** wavelet (Ch 2), queues/DSRs/microthreads (Ch 3), route PE-side code (Ch 4), CSL constructs (Ch 4–7 before Ch 10), task syntax (Ch 10 → Lab 1).
6. **Stale cross-refs.** ~7 vs 9.2 cycles/hop relay, "~88" vs ~90 fixed cycles, Ch 9's pointers into Ch 8, "capstone", r3 items never applied (Ch 1, 3, 9, 16, 18).
