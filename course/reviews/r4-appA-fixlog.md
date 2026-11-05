# Round-4 fix log: Appendix A (glossary), page-id appA

File edited: `appendix-a-glossary.html` only. Entries: 176 → 195. Verified with Playwright (Chrome, 1100 px and 390 px). There were zero console errors and no horizontal overflow at 390 px. All in-page and cross-page hrefs resolve: the one script reports is the literal `#g-…` inside a JS comment. Ran 16 test searches. Opened every new id by hash and checked that the entry flashes in the scroll box. Clicked a "Related:" link (Task → Join). Selected cb16 in both format explorers.

## Priority ids (CROSS_CHAPTER_NOTES 38)
All nine now exist, each with syntax, a one-line example from programs/, and "See" links to where it is taught:
`g-get-dsd`, `g-dsd-mutators`, `g-sys-mod`, `g-get-color`, `g-get-local-task-id`, `g-get-queue`, `g-memcpy-params`, `g-many-item-pointer`, `g-export-symbol`.
- `g-export-symbol` is now the `<dt>` id of the existing "@export_name / @export_symbol" entry, which I rewrote with syntax and examples. The old id `g-export-name-export-symbol` moved to the entry's wrapper `<div>`, so both ids land on the same entry.

## Items
| ID | Status | Note |
|---|---|---|
| E1 | Fixed | Tokens/s now gives ~7,500 as an overstated headline bound (read ports only), the ~2,000–4,000 one-user bound [Derived], and 2,314 inside it [Indep]. It frames the limit as a chain of 80 layer reads plus latency (note 32). |
| E2 | Fixed | sim_stats.json: the idle tail is "usually 50" and noise "a few percent", but up to ~40 % with a 2,109-cycle tail on a loaded host [Measured]. Says to time kernels with the TSC, and links the TSC entry. |
| E3 | Fixed | The lede legend adds Analyst, explains "Secondary" / "Vendor via secondary", and links App E #tags and the new Provenance tags entry. |
| X1 | Fixed | Residual: tol = EPS·\|b\| (relative; `--eps`, default 1e-5). |
| X2 | Fixed | Task ID: describes two separate ID spaces (data/local 0–30, activatable below 31; control 0–63, named in the payload) and gives the `@get_control_task_id(43)` example. |
| X3 | Fixed | Local task and Task ID give the WSE-2 rule (0–30 minus the colors you receive on). The TSC entry says "WSE-3:" for the 10-cycle empty region and notes that WSE-2 was not measured. |
| X4 | Fixed | Wavelet → "Ch. 4, A mesh of five-port routers"; HBM → "Ch. 1, Two numbers"; TP/PP/DP → "Ch. 8, Inference". |
| X5 | Fixed | Bank clash: adds the WSE-2 f16 @fmach rule (fast only 4 banks apart; WSE-3 no penalty) [Measured], states the single "opposite halves of the 16-byte bank cycle" rule (note 30), and links App E #iss-clash. |
| G1 | Fixed | Nine new code-vocabulary entries (above) plus "Integer types: i16, u16, i32, u32". DSD entry now shows `@get_dsd` syntax and links to the new entries. memcpy_h2d entry now explains `order=MemcpyOrder.ROW_MAJOR/COL_MAJOR`, `MEMCPY_32BIT/16BIT`, `streaming`, `nonblock`. mem4d_dsd / fabin_dsd / fabout_dsd covered in g-get-dsd. Mutator cost ~33–35 cycles/step [Measured]. |
| G2 | Fixed | New entries "topic-NN, gemv-NN, benchmark names" (→ App D #index, #ladder), "HC22 / HC2024 / SC20" (→ App E #bib) and "Provenance tags" (→ App E #tags, #unverified). |
| G3 | Fixed | New entries: Host-driven vs device-driven loop (5,798 vs 4,574 cycles/iter [Measured]; ~99.5 % host wait on real system [Derived]), Strong scaling, FSM task / lock task, CE-ignore bit, Rubin CPX ("deferred, not cancelled" [Unverified], per r4-appE), Artificial Analysis, PTX / CUTLASS. GEMV entry gains alias "matvec" (search finds it). |
| G4 | Fixed | Bank-clash entry gives the derivation: an f32 word w occupies banks 2w and 2w+1 mod 8, so two words collide iff w₁ ≡ w₂ (mod 4) [Derived]. Bank ↔ Bank clash are linked both ways, and Bank links to 06#collisions. New "Related:" line (`.rel`, same style as `.see`) on all five chains: Task/Activate/Block/Join/Picker; Input queue/Microthread/.ut_id; Control wavelet/Switch/Teardown/@queue_flush; launch/Command stream/unblock_cmd_stream/Kernel stall (+ sys_mod, host vs device loop). Related text is kept out of the search index so searches stay precise. |
| G5 | Skipped (outside this file) | See "For other pages". |
| G6 | Fixed | KV cache: at 8K context at most ~13 users (~7 after code overhead) per 4 × CS-3 [Derived], linked to Tokens/s; added link to Ch 9 #spec. |
| Note 30 | Applied | Bank-clash wording. Note 30 asks for a link to Ch 6 `#banks`, but that anchor does not exist yet, so I linked `#collisions` instead. |
| Note 33 | Applied | WSE entry: SDK benchmarks assume 850 MHz [SDK]; CS-4 press estimates ~1.4 GHz [Analyst]. |
| Note 35 | Applied | Input queue: depths 6/4/2 for queues 0–1/2–3/4–7 [SDK]. |
| Notes 31, 32, 34, 36, 37 | Checked | 32 is applied in E1. Launch entry already said "returns without waiting". Hop entry already said 2.0/1.0 and 9.2/6.0. No 88-cycle or 7.5 PF figure on the page. Fabric entry now says routes are set at load time and can be changed at run time by switches and teardown (cf. r4-ch16 E5). |
| r4-appE 78/79 (cb16) | Fixed | The 1/6/9 split is now Vendor (Cerebras ML docs) and the bias 31 is Derived (assumed). Changed in the entry, format table row, figure caption, explorer option labels and explorer note. |
| Extra (found while verifying) | Fixed | Duplicate id `gl-q`: the search input and the letter-Q heading both had it, so the "Q" jump link scrolled to the search box. Renamed the input to `gl-search` and updated the JS. |
| r4-ch13 (Dirichlet boundary entry), r4-ch08 G8 (training basics) | Skipped | Optional asks from other auditors. Not in this page's report. |

## For other pages
- **All chapters (G5 / note 38):** link the first forward use of these terms to the glossary:
  - cslc, cs_python, cs_readelf, Simulator: Ch 3, used before Ch 10.
  - DSD (`#g-dsd-data-structure-descriptor`) and `@get_dsd` (`#g-get-dsd`): Ch 3, Ch 5.
  - memcpy: Ch 2–5.
  - Tensix, Blackhole, MemoryX: Ch 1.
  - `.ut_id`: Ch 3.
  - TSC (`#g-timestamp-counter-tsc`): Ch 3, Ch 11.
  - SpMV: Ch 5.
- **Labs 11–15 code walkthroughs:** link the CSL identifiers to the new entries: `g-sys-mod`, `g-memcpy-params`, `g-get-color`, `g-get-local-task-id`, `g-get-queue`, `g-get-dsd`, `g-dsd-mutators`, `g-many-item-pointer`, `g-export-symbol`, `g-host-device-loop` (Ch 11, 15), `g-strong-scaling` (Ch 13, 14), `g-fsm-task-lock-task` and `g-ce-ignore` (Ch 14).
- **Ch 1 and Ch 17 "Terms used here" boxes:** add a "Full glossary" link to `appendix-a-glossary.html`.
- **App D:** link the Teaches column to existing entries, and link `topic-NN` to `#g-topic-nn` (r4-appD X4).
- **App E:** link TSC, DSR, input queue, microthread and bank on first use (r4-appE X3). The cb16 row can now move from Unverified to Vendor in App E's list.
- **Ch 6:** when `#banks` is created, App A's bank-clash entry can point there instead of `#collisions`.
