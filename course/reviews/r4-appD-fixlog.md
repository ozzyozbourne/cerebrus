# R4 fix log: Appendix D (SDK example index), page-id appD

Page: `course/appendix-d-sdk-index.html` (only file edited). Verified with Playwright at 1100 px (and 390 px overflow check):
zero console/page errors, every chip and "Show all in table", filters, search and a heat-map cell driven; all 174 in-page
and cross-page hrefs (static plus every ladder rung and index row) resolve to existing ids; no horizontal overflow at 1100 or 390 px.
Loading `#after-ch05` selects and scrolls to that rung; a same-document `hashchange` also switches the rung.

## Ladder anchors (for chapters to link to)

Each rung has a static, linkable id (a hidden `<span>` above the chips, so the browser scrolls there natively, offset for the
top bar). Loading or switching to the hash selects that rung, and clicking a chip writes its hash with `history.replaceState`.

| Rung | Link |
|---|---|
| After Ch 3 | `appendix-d-sdk-index.html#after-ch03` |
| After Ch 4 | `appendix-d-sdk-index.html#after-ch04` |
| After Ch 5 | `appendix-d-sdk-index.html#after-ch05` |
| After Ch 6 | `appendix-d-sdk-index.html#after-ch06` |
| After Ch 7 | `appendix-d-sdk-index.html#after-ch07` |
| After Ch 10 | `appendix-d-sdk-index.html#after-ch10` |
| After Ch 11 (Lab 1) | `appendix-d-sdk-index.html#after-ch11` |
| After Ch 12 (Lab 2) | `appendix-d-sdk-index.html#after-ch12` |
| After Ch 13 (Lab 3) | `appendix-d-sdk-index.html#after-ch13` |
| After Ch 14 (Lab 4) | `appendix-d-sdk-index.html#after-ch14` |
| After Ch 15 (Lab 5) | `appendix-d-sdk-index.html#after-ch15` |
| Beyond the course (for Ch 18 #next) | `appendix-d-sdk-index.html#after-beyond` |

Chapters 1, 2, 8, 9, 16 and 17 have no rung. Other new ids: `#anatomy` (what is in an example directory) and `#series` (the cumulative tutorial series note). Existing `#run`, `#ladder`, `#index`, `#notes` are unchanged.

## Items

- **E1** Fixed. Ch 10 rung now lists topic-12 before topic-13, and topic-13 is marked "a variant of topic-12". Its row note says so too, quoting its README.
- **E2** Fixed. Added 10 (with a link to Ch 10 #stdlib) to the PCG, bicgstab and power-method rows. Added 15 to PCG with a `15-lab-cg.html#scaling` link ("the SDK's PCG uses Jacobi"); its Teaches text now says "(Jacobi)". Added a Ch 13 `#sdk-stencils` link to bicgstab, which is where the CS-1 BiCGSTAB comparison sits. Checked: filters for Ch 10 and Ch 15 now return these rows.
- **E3** Fixed. Added `mkdir -p ~/sdk` (with a comment) before the `cp` line.
- **E4** Fixed. The callout names bandwidth-test, row-col-broadcast and spmv-hypersparse as printing measurements, and gemv-00 as having no script. The three rows and their ladder entries say "prints measurements".
- **X1** Fixed. Deleted the "Phase 3 coverage audit" sentence. Its facts are already in the stats and the Notes.
- **X2** Fixed. New h3 `#anatomy` before the callout covers: README.rst, layout.csl, pe_program.csl or `src/`, run.py, and the two scripts. It gives the typical two-line script (cslc with flags, then `cs_python run.py --name out`) tagged SDK, and links Ch 10 #three-files and #flags. It lists the exceptions: sdklayout-* run only `cs_python run.py` (checked), 25-pt-stencil keeps its .csl files at top level, and fft-3d ships only layout.csl and run.py. It ends with "Read README.rst first" and links the series note.
- **X3** Fixed. Each Labbed row now has a green "course: programs/NN-…/" line under its path, using the auditor's mapping (12 rows). Search also matches the program name (for example "07-cg"). The legend explains the green line.
- **X4** Fixed. Added a "Terms used (glossary)" line under the legend, with 18 links to `appendix-a-glossary.html#g-…`, all checked to exist. `render()` also links the first use of each term in every row's Teaches text (23 term patterns). The Notes link microthread, TSC, color swap and allreduce.
- **X5** Fixed. The timing-idiom note now says the correction assumes 1 cycle per hop, while the WSE-3 simulator takes 2 (WSE-2: 1) [Measured], so the alignment can be off by up to about width + height cycles [Derived]. It links App C #tsc.
- **G1** Fixed. New Notes item `#series` covers the four cumulative series with README quotes, sdklayout-04 reusing add2vec, and "read as a diff" with a `diff -r` example. In the ladder, gemv-02/03 are marked "a diff against …; run after gemv-01". gemv-09 is marked "a streaming rewrite of gemv-08 (Ch 12 rung); run it after that one", and gemv-08 points forward to it. I moved gemv-09 to last on the Ch 7 rung.
- **G2** Partly. Every ladder item now has a READ or RUN badge. Rungs before Ch 10 default to READ, except single-tile-matvec, which is RUN (Ch 3 walks through running it). A new hint states the rule and links Ch 10 and Ch 3 #feed, and the gemv-01 entry says "run this first; then go back and run the Ch 3–7 rungs". topic-07 moved to the Ch 5 rung and topic-04 to the Ch 6 rung, each with a one-line reason. I skipped the optional per-row "earliest chapter" field: the report offers it only as a way to make the order checkable.
- **G3** Partly (this page's half done). The rungs are deep-linkable (`#after-chNN`, table above), with hash preselect and hashchange handling, and the hint advertises them. The inbound "Next in the SDK" links belong to other pages and are listed below.
- **G4** Fixed. Third callout bullet "Or vendor the libraries": Lab 5's `programs/07-cg` keeps both libraries in `lib/` and imports `"lib/…/layout.csl"`, linked to 15-lab-cg #modules. For an SDK example that means copying them into `src/lib/` and rewriting the `"../../benchmark-libs/` imports; four files in conjugate-gradient/src have them [SDK, grep]. I did not run this variant; the bullet describes what Lab 5 does.
- **G5** Fixed. Ch 15 already has `id="two-loops"` on that h3. The device_run.py note links it, maps host loop = run.py + kernel.csl and device loop = device_run.py + kernel_cg.csl, and keeps #profile for the cost. The conjugate-gradient row gained a "Two loops, one program" link.
- **G6** Fixed. The WSE-2-only Notes bullet now gives each example's porting blocker. Color swap → Ch 4 #router-numbers (the "color swap: no (in CSL)" row). 25-pt-stencil's 18 local tasks → Ch 5 #budget. histogram-torus and spmv-hypersparse → "no specific blocker named; start from Ch 5 #portability". The same clause, with links, is in each of the four rows' notes; row notes are now trusted HTML, and the `<simprint>` note is escaped.

### Coordinator items 30–38
- 33 (clock): the timing note now tags 850 MHz as the SDK assumption, says no WSE-3 clock is published, and adds the ~1.4 GHz press estimate [Analyst, unverified].
- 34 (hop cost): 2.0 / 1.0 cycles per hop, in the X5 note.
- 38 (linking): the Chapter 14/15/10/3 mentions, rung titles (each links its chapter), App C and Ch 15 sections are now links, and glossary links were added as described under X4.
- 30, 31, 32, 35, 36, 37: the page makes no rate, launch(), tok/s, queue-depth, FP16 or Lab 3 fixed-cost claims, so nothing to change. pipeline-01's "stalls past the queue size" makes no depth claim.

### Cross-page items about this page
- r4-appA.md:78 says App A links SDK names to App D `#index`. The id exists and is unchanged. Nothing else in other r4 reports concerns App D.

## For other pages
- **G3 inbound links** (for the fixers of those pages): add a one-line "Next in the SDK → [Appendix D](appendix-d-sdk-index.html#after-chNN)" near the end of Ch 3, 4, 5, 6, 7, 10, 11, 12, 13, 14 and 15, using the ids in the table above. Ch 18 `#next` lists six SDK benchmarks; link it to `appendix-d-sdk-index.html#after-beyond`, or to `#index`.
- Ch 10 (src not applicable; 10 is a top-level page): its library-map row for benchmark-libs could link to `appendix-d-sdk-index.html#run` for the import fix. It already links to `#run` elsewhere, so this is optional.
- Housekeeping, not a page issue: the installed SDK example `tutorials/gemv-01-complete-program/` contains run leftovers (`out/`, `sim.log`, `sim_stats.json`, `simconfig.json`, `simfab_traces`). Someone ran it in place. The coordinator may want to clean it.
