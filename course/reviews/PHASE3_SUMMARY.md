# Phase 3 — do we need more chapters?

Four independent audits: learner path, SDK coverage, architecture/systems, review backlog.
Reports: phase3-learner-path.md, phase3-sdk-coverage.md, phase3-architecture.md, phase3-backlog.md.

## Verdict: yes — two new chapters, plus appendices

1. **Lab 4 · 2-D GEMM (SUMMA) with `<collectives_2d>`** — new Ch 13 (Tenstorrent/GPU/Comparison become 14–16).
   Raised by 3 of 4 audits (learner path: "no matmul, no 2-D program"; SDK coverage: strongly recommended;
   backlog: "collectives on the wafer", 5 reviews). Every current lab is 1-D. Evidence: SDK
   `benchmarks/gemm-collectives_2d` runs unchanged on WSE-3 (P=4, 14×14 tiles, SUCCESS, 91,158 cycles).
   Teaches run-time route switching/teardown, a task joined on two networks, the compute-bound regime,
   and gives Ch 13–15's matmul comparisons a Cerebras counterpart. Fold in a 2-D GEMV warm-up and
   chain-vs-tree allreduce. Effort ~2–3 days.
2. **From model to tokens: compiling and serving on wafers** — after Ch 8. Raised by the architecture
   audit: the PyTorch→wafer compile path, speculative decoding, MoE and a per-token latency budget are
   each a paragraph or less today. Effort medium-high; parts rest on secondary sources (ISPD 2020 slides unreachable).

Optional: Lab 5 · CG solver (SDK benchmark runs: SUCCESS, err 3.05e-05). Rejected as chapters by
all audits: debugging/tuning, SdkLayout, sparsity, ML-on-CSL, other accelerators, FFT/Cholesky etc.

## Appendices (agreed by 3 audits)
A Glossary + number formats · B CUDA→CSL map + resource budget card + measured cost constants ·
C Measuring and observing (sim_stats vs TSC vs trace) · D SDK example index by chapter · E Sources and Unverified list.

## Edits regardless of new chapters
- Ch 14/15: NVIDIA update — Groq licensing deal (Dec 2025), Groq 3 LPX SRAM decode rack (GTC 2026); Rubin CPX reportedly dropped (verify).
- Ch 14: wrong "Chapter 12 for matmul tiles" pointer.
- Ch 9: library map (fft, tally, benchmark-libs) and `--import-path` fix; move the "CSL is the custom-kernel path" note up.
- Ch 3/5/6/7/9: short "if you know CUDA" callouts.
- Ch 12 exercises: measured answers for "Fewer messages" and "Half precision".
- Engineering pass: phone layouts, shared CSS (button contrast, pre.output wrap, .tag.unv into course.css), unbuilt widgets from fix logs.
- reports/ and research_notes/ are stale relative to the measured findings.
- Done in this pass: ch08 "~1 GHz" → 1.1 GHz.

## Open factual issues (no chapter can settle yet)
Bank model (16-bit SDK units vs 32-bit academic); empirical bank-clash rule; WSE-2 @fadds 1/cycle isolated vs 2/cycle in Lab 3;
WSE-2 hop ~90-cycle floor for P≤8; microthread shared-datapath claim unmeasured; `.index` units, @fscales/@fnorms semantics.
