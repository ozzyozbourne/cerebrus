# ch08 · fix log

Chapter rewritten in place (`course/08-systems.html` only). New order: timeline + systems table → training: weight streaming (animated step, 6-step list, tokens-per-weight worked example + widget, a layer on the wafer, MemoryX, SwarmX, layer-pipelined mode) → inference (KV cache defined, inside the pipeline, pipeline-decode animation, inter-wafer budget, KV arithmetic, capacity + decode-ceiling widget) → speed table with configurations, decode worked example, SDK GEMV experiment, cost callout → CS-4 and roadmap → CSL-programmer bridge → 6-question quiz. Objectives rewritten to match (including the timeline objective).

Primary sources used: weight-streaming white paper (wsc.txt), training docs (wsdoc.md), PLDOC (pl.html), HC22, HC24, CS-4 blog, HC2026 blog, STH HC2026, Cerebras Oct/Nov 2024 and GPT-5.6 Sol blogs (all in `/home/user/cerebras-sdk/tmp/ch08depth/`), plus a fresh curl of the Cerebras CS-3 blog (MemoryX SKUs) and a web search for the Kimi K2.6 configuration.

Verification: Playwright at 1100 and 390 px, light and dark. No page or console errors, `scrollWidth == innerWidth` at both widths. Every control exercised: ws Play/Pause/Step/Reset and the 1/2/4 selector; tpw slider and wafer select; pd Play/Step/Reset and the 1/2/4/10/20 selector; cap presets, log slider (min and max), precision, context, users; every timeline milestone. Screenshots inspected, then deleted.

## Accuracy
| ID | Status | Note |
|---|---|---|
| A1 | fixed | $0.60 is now tagged Vendor (launch list price, also on the HC24 slide), split from the Analyst H100 range. ch15 line 64 still has the old combined tag, for the coordinator. |
| A2 | fixed | Q1 answer uses the reviewer's wording plus the 50k-token knee. |
| A3 | fixed | CS-4 "max cluster" is now —; RoCE v2 + DWL moved into the System cell. |
| A4 | fixed | "(sources conflict)" added. |
| A5 | fixed | Lede 44 GB tagged Vendor; 140 GB Derived; the four-CS-3 / 20-layer layout now cited to HC24 (primary) rather than The Register. |
| A6 | fixed | The HC24 slide shows layers 1–20/21–40/41–60/61–80, so the split is now cited as Vendor; ~35 GB/wafer is Derived, with the embedding/output caveat. |
| A7 | fixed | Widget rebuilt with a dynamic viewBox; above 40 devices it groups boxes ("1 box = k devices"). |
| A8 | fixed | Analyst tag added, plus the KV-cache mechanism. |
| A9 | fixed | The [Derived] tspan is gone (the static figure was replaced by an animation; notes now use .tag). |
| A10 | fixed | CG-1/2 4 EF; CG-3 108 TB. |

## Pedagogy
| ID | Status | Note |
|---|---|---|
| P1 | fixed | "Why streaming does not starve the wafer" subsection, worked example and widget, placed before the quiz. |
| P2 | fixed | 1.2 Tb/s = 150 GB/s link (WP for WSE-2, HC24 for CS-3), ~10× the Ch07 host path, explicitly tied to Ch07's "dedicated hardware". |
| P3 | fixed | "Pipeline parallelism" introduced, with the decode animation, Gantt and 476 µs figure. |
| P4 | fixed | Decode speed-limit worked example (24 / 190 / 86 / 600k tok/s, 480,000× vs 42×). |
| P5 | fixed | KV cache defined at first use, cross-referenced to Ch01 (which now defines it); widget models KV explicitly. |
| P6 | fixed | "Where this sits for a CSL programmer" callout before the quiz. |
| P7 | fixed | Backward-pass order and the activation-storage limit on batch, in the 6-step list and the paragraph after it. |
| P8 | fixed | SwarmX section explains data parallelism and why only one layer must fit; the animation has directional arrows on every link. |
| P9 | fixed | Years in the headers, an "Execution mode" row, and the interactive CS-1 → CS-5/6 timeline. |
| P10 | fixed | Gloss paragraph (CS-n vs WSE-n, WSE-3T) and table note (EF/PF, sparse, RoCE v2, MemoryX ranges). |
| P11 | fixed | Q1 rewritten; Q2 replaced by the pipeline question; CS-4 rack question added; also added MemoryX-traffic and KV questions. |
| P12 | fixed (superseded) | The reserve slider is gone (KV is now modelled explicitly). The Q3 answer was recomputed for the new widget: 19 wafers with one 8K user, 20 with ten. |
| P13 | fixed | Kimi row now gives its configuration (~20 CS-3, 4-bit, MoE ~32B active), with a "capability claim" note. |
| P14 | fixed | `<title>` matches the h1 topics; lede disambiguates the SDK streaming mode; "passes tokens" used for inference; overflow label fixed. |

## Visuals
| ID | Status | Note |
|---|---|---|
| V1 | partially | Relies on the shared ≤680px min-width scroll fix. All new SVGs use ≥11 px text, and long notes moved to captions or readouts. No portrait relayouts. |
| V2 | fixed | Replaced by the animated widget: amber weights down and purple gradients up on every wafer link, "batch shard i/N", per-layer slabs. |
| V3 | fixed | Rebuilt: per-device fill (weights amber, KV purple), H100/B200 rows, row labels, computed readout, decode-ceiling bar chart. |
| V4 | fixed | Pipeline animation has the return arc, per-region "weights + KV", and the sourced split. |
| V5 | fixed | SwarmX box widened; subtitle shortened to "broadcast ↓ W · sum ↑ ∇W". |
| V6 | fixed | As A9. |
| V7 | fixed | Log-scale parameter slider plus 8B/70B/120B/405B/1T presets. |
| V8 | fixed | B200 at nominal 192 GB, tagged Vendor. |
| V9 | fixed | One decimal place below 10 GB. |
| V10 | fixed | aria-live on all readouts; dynamic aria-label on the capacity SVG; timeline points are focusable role=button. |
| V11 | fixed | Short labels ("Users", "Context", "Weights"); values inside the labels. |

## Depth
| ID | Status | Note |
|---|---|---|
| D1 | fixed | 6-step list with WP/WSDOC quotes, plus the 32-bits-each-way traffic budget. |
| D2 | fixed | Worked example (75 G weights/s, 50k-token knee, 0.002% for decode) plus the link/compute widget (WSE-3 dense tagged Analyst). |
| D3 | fixed | "A layer on the wafer" paragraph and SVG (packet format, column multicast, PSUM/FSUM, sparsity), linked to Ch03–06. |
| D4 | fixed | 20 B/param table, derivations (3.5 TB, 2.4 PB, 50 B/param for CS-3), mechanism paragraph. Added shipped SKU sizes from the CS-3 blog (1.5/12 TB CS-2; 24/36/120/1,200 TB CS-3). Dropped "1.5 PB in some sources": no primary support, and it is likely a confusion with the 1.5 TB SKU. |
| D5 | fixed | SwarmX tree paragraph with WP quotes and the Andromeda 15.87× caveat (cited from the reviewer's source, not re-fetched). No tree diagram. |
| D6 | fixed | "Not found" sentence replaced with the PLDOC description (<1B params; regions; on-wafer updates; steady state). The reviewer's "does not support multiple CS-2s" was left out because it is not in the fetched doc text. |
| D7 | fixed | "Inside the pipeline" bullets from HC24, plus the animation. |
| D8 | fixed | Inter-wafer budget callout (16 KB, 0.9% / 4%, 100 Gb/s of 1.2 Tb/s, 2 µs on CS-4). The Databricks TP-scaling point is left out (it belongs in Ch14/15). |
| D9 | fixed | Decode worked example plus SDK GEMV experiment box. Cycle counts are the depth reviewer's simulator run (tagged Measured); I checked the extrapolation against run.py's formula (4·nb²+8·nb bytes, 850 MHz, 750×994) but did not re-run it. |
| D10 | fixed | Speed table now has a configuration column; 405B and GPT-5.6 Sol rows added; 4.7× software-only note. |
| D11 | fixed | KV arithmetic (327,680 B/token, ~110k tokens, ~13 users at 8K) plus context/users controls in the widget. |
| D12 | fixed | CS-4/Nexus table from CS4B/HC26B/STH. MoE placement uses the HC26B quote instead of the paywalled SemiAnalysis. ">4,400 tok/s gpt-oss" left out (not found in the fetched pages). |
| D13 | fixed | CS-5 targets added; CS-6 corrected to "wafer-scale SRAM and compute with 3D-stacked DRAM" (HC26B), with the STH "DRAM for the first time" quote. |
| D14 | fixed | CG 3–5 / 6–9 planned (HC24 2024 plan) in the table, keeping the status caveat. |
| D15 | fixed | Merged into the CSL-programmer callout. |

## New visuals added
1. **Systems timeline** (`#tl`): four lanes (systems, training mode, inference, clusters), 2019–2027, clickable/keyboard milestones with tagged detail cards, mode spans, hollow roadmap dots (N4).
2. **Animated weight-streaming step** (`#ws`): MemoryX layer slabs, SwarmX, 1/2/4 wafers with activation stacks that fill and drain, weight packets down and summed gradient packets up (Σ), per-parameter traffic counter (N1).
3. **Link-bound vs compute-bound** (`#tpw`): utilisation vs tokens per shard on a log axis, knee marker, WSE-2/WSE-3 toggle (D2 mini-widget).
4. **A layer on the wafer** (`#lw`): static PE-grid schematic of column multicast and PSUM/FSUM ring reduction (D3).
5. **Pipeline-decode animation** (`#pd`): 4 wafers × 5 regions, return arc, users in flight 1–20, a 20-stage occupancy Gantt (busy-wafer timeline), utilisation readout (N2/D7).
6. **Capacity + decode-ceiling calculator** (`#cap`): weights + KV fill per device for WSE-3/H100/B200, a log-scale per-user tok/s ceiling (headline and SDK-GEMV rates) with published speeds overlaid (V3/N3/N5/D9c/D11).

All animations respect `prefers-reduced-motion`.

## Left for later
- Per-figure portrait layouts for phones (V1); the shared scroll fix is in place.
- SwarmX tree diagram (D5), cost-vs-speed scatter (N6).
- ch15 line 64 needs the same Vendor/Analyst split as A1 (not my file).
- Research report "Chapter 9" section still says layer-pipelined and inference mapping details were "not found", and CS-6 is "3D wafer-scale SRAM". Both should be updated (D6/D13).
- Kimi K2.6 configuration (~20 CS-3, 4-bit) rests on press reports; VentureBeat returned 429 and there is no Cerebras primary.
- Out-of-scope depth notes (HC22's official 1.1 GHz WSE-2 clock vs the report's "no official clock"; the toy inference-pipeline lab idea) are for other chapters.
