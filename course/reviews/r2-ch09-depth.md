# r2 · Ch09 "From model to tokens" · DEPTH review

Scope: what an expert would find missing, shallow or unsupported. I checked the numbers in the prose, quiz, #lb and #cap JS (lines ~560–645) against build-ch09.md, CROSS_CHAPTER_NOTES 13/14/16/22–25 and research_notes/wse_hardware.md (§3, lines 78–94; ch08-depth.md line 176). I re-derived the arithmetic and did not re-run the simulator. The f32/f16 GEMV table is consistent with notes 14/22.

## Findings

**D1 · high · "A decode latency budget" (measured GEMV paragraph, "three ways"), #lb GEMV-rate select, cap widget "region's SRAM rate"**
The page treats 7.5 B/cycle as a *streaming/SRAM* rate and offers "24 B/cycle · HC22 port peak" as the hardware ceiling. Neither is right. HC22's 24 B/cycle is 2 × 64-bit reads + 1 × 64-bit write. Weights can only use the **16 B/cycle of reads**. The measured kernel is an AXPY (`y += A[:,j]·x[j]`). Each f16 FMAC reads a weight (2 B) and an accumulator (2 B) and writes the accumulator, so it is read-port-bound at 16 B ÷ 4 B = **4 FMAC/cycle = 8 B/cycle of weights**. The measured 7.5 is 94% of that. That is why WSE-3 shows exactly 4/cycle in the simulator although HC2024 claims an 8-wide FP16 SIMD (wse_hardware.md l.85). A production kernel that keeps partial sums in registers or on the fabric (dot-product form) reads only weights and could reach ~16 B/cycle (8 FMAC/cycle). That is ~2.1× the measured rate, not 3.2×.
Fix: explain the 4-FMAC AXPY limit in one paragraph. Replace the 24 B/cycle option with "16 B/cycle · read-port limit, weights only (8-wide SIMD, not demonstrated)", tagged Derived/Unverified. Rename the cap widget's "region's SRAM rate" to "region's kernel rate (read-port-bound)". This makes "faster kernels" a concrete ≤2× lever rather than an open-ended one.

**D2 · high · Speed history closing paragraph: "Clock and kernel streaming rate, the hardware-bound terms, did not change."**
The page contradicts itself. The kernel streaming rate is a software choice (D1), and the row directly above quotes the Oct 2024 blog crediting "re-written or optimized MatMul" kernels. The 4.7× may therefore include up to ~2× from the GEMV itself.
Fix: "Clock did not change. The GEMV rate is a kernel choice and can move up to ~2× (D1), and the blog says MatMul kernels were rewritten." Add a GEMV-rate change to the what-if B preset, or note it as an alternative path to 2,100.

**D3 · high · Speculative decoding (wafer argument, quiz Q7, #sd default c = 0.05, #lb "accepted tokens/pass")**
c = 0.05 is a GPU number: draft cost there scales with bytes read. On the wafer, a draft model's per-token latency is also a pipeline trip. Its collectives, hops and handoffs per layer do not shrink with parameter count. An 8B draft (32 layers) on the page's own budget is ~0.3–0.4 of a 70B pass, not 0.05. With c = 0.35, α = 0.8, k = 4: 3.36/(1 + 0.05 + 1.4) ≈ **1.37×**, not 2.7×. The #lb widget also divides the pass time by "accepted tokens/pass" with no draft cost and no k/S term. So what-if B's "~2 tokens/pass → 420 µs" is free speculation and is optimistic.
Fix: give a wafer-specific c estimate (draft layers × per-layer fixed cost ÷ target), set the #sd default to ~0.3 or show both values, and rework Q7. In #lb, add the draft cost and k/S to the per-pass time, or label the E slider "net speedup from speculation".

**D4 · high · "Speculative decoding on an SRAM machine" ("The price moves to the system") and the "Fast per user is not cheap per token" callout**
The page never combines its own two numbers: ~13 users fit at 8K context (KV section), and the pipe has 80 slots. Without speculation a 4-wafer Llama-70B deployment at 8K is therefore at most ~16% occupied (13/80). Speculation with k = 4 fills ~65 slots. In the KV-limited regime the "E/(k+1) system cost" is close to zero, and speculation mostly uses slots that would otherwise sit idle. That is a strong, non-obvious reason why it fits the wafer. Aggregate throughput is ~13 × 2,100 ≈ 27k tok/s, far below the 600k "pipe-full ceiling". That is the real cost story behind the callout.
Fix: add a short worked example, "occupancy = users × positions per pass ÷ S". State when speculation costs throughput (pipe full, short contexts) and when it does not (KV-limited). Quote ~27k tok/s per 4 × CS-3 at 8K as Derived in the cost callout.

**D5 · med · KV-cache arithmetic and budget "Weights per PE" ("~9 KB per PE … matching the ~36 GB above")**
The 36 GB / 110,000-token / 13-user figures ignore per-PE fixed overhead. Note 13 gives ~4.6 KB on WSE-3 for a minimal program. Real kernels with several matmul/collective routines need more, plus activation, x-slice and partial-sum buffers. 48 − 38.9 − 4.6 ≈ 4.5 KB/PE × 3.6 M PEs ≈ 16 GB, so ~49k tokens or ~6 users at 8K, and less once buffers are counted. The page states "even if … none held activations or code", but the "matching" sentence in the budget treats 9 KB as if it were all KV.
Fix: give a second line, "with ~4.6 KB/PE of code and task tables (note 13): ≤16 GB, ~6 users at 8K". Update quiz Q3's "about 13" to a range, and soften "matching".

**D6 · med · Budget model, "Collectives per layer: about 8"**
The model counts only the four GEMV broadcast/reduce pairs. A decode layer also needs two RMSNorm reductions (sum of squares → broadcast), the softmax max and sum across the region's KV slices, and the handoff of the 16 KB activation into the next region. Each is latency-bound (~212–424 hops in 2-D) and not bandwidth-bound, so the realistic count is ~12–14, and that matters most in what-if A. In 2-D, a broadcast or reduce from an edge or corner spans ~212 hops per dimension, so ~424 for row plus column, unless both run concurrently.
Fix: list the extra reductions, raise the default range or note "≥8". Say that hops/collective = 212 assumes a centred or 1-D traversal.

**D7 · med · Precision section: "In the budget it halves the bytes each PE streams per token."**
With 16-bit compute the GEMV is bounded by FMACs per cycle (D1), not bytes. 4-bit weights spread over the same PEs give the same FMAC count and the same time, plus the unpack cost. Packed onto half the wafers, each PE does 2× the FMACs and is slower. 4-bit buys capacity (fewer wafers, more KV room), not per-token speed, unless the unpack runs alongside the multiply-accumulate. MoE's benefit is real because it cuts FMACs, not bytes.
Fix: reword to "halves SRAM per weight. Per-token GEMV time is set by multiply-accumulates at 16-bit, so the gain is capacity (KV, wafers), not speed."

**D8 · med · "Two ceilings" box and quiz Q6**
The one-user ceiling is presented as an SRAM/bandwidth bound. Underneath it is a **sequential-dependency bound**: layer l+1 cannot start before layer l finishes, so per-token time ≥ Σ (layer FMACs ÷ PEs in that layer's region × FMAC rate). It holds whatever the bandwidth. Saying so makes clear why only speculation or prefill-style multi-position passes, a higher clock, or a faster FMAC rate can push past it.
Fix: one sentence naming it as a dependency/latency bound per region.

**D9 · low · Speculative "k-wide costs ~k×", supported by the naive k-wide measurement**
The measurement is set-up-dominated (the page admits this), so it is weak evidence. The better argument is structural: each weight feeds (k+1) FMACs, and the FMAC rate (4–8/cycle) is no higher than the weight read rate, so even an ideal kernel pays ~(k+1)×.
Fix: lead with the structural argument and keep the measurement as a footnote.

**D10 · low · Sparsity: "Below 50% sparsity it costs SRAM"**
This holds only for a 16-bit index per non-zero. A bitmap (1 bit per weight) breaks even at ~6% sparsity, and block formats lower it further. The stronger reason inference avoids sparsity is that skipping zeros on a pinned, memory-resident tile needs index-driven gathers with per-op set-up costs (note 16: ~33 cycles per DSD step). Accuracy is another reason.
Fix: qualify with "with 16-bit indices" and mention bitmaps and gather cost.

**D11 · low · Disaggregation**
The ~2.7 GB KV payload is given without a transfer time. At 2.4 Tb/s (300 GB/s) it is ~9 ms per 8K request, which is comparable to several hundred decode tokens' worth of time at 4,400 tok/s and needs overlapping with decode.
Fix: add the transfer time as Derived.

## Summary counts
High 4 (D1–D4), Med 4 (D5–D8), Low 3 (D9–D11). Total 11.
