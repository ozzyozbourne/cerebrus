# ch03 · visuals review

Summary: The chapter has three static SVGs (the PE anatomy, the "relative vs absolute" GEMV comparison and the sparse-wavelet bit layout) and one widget (the 48 KB budget bar). I rendered it with Playwright at 1100 px and 390 px, in light and dark. There are no console errors and no horizontal page scroll. The budget widget computes correctly at every edge value I tried. The defects:
- The anatomy diagram has two text collisions, one-way arrows on ports that carry traffic both ways, and a missing West port.
- All three SVGs shrink to 4–6 px text at 390 px.
- JS-coloured elements keep their old colours after the ◐ theme toggle.
- The budget bar's legend is uncoloured, and the bar hides the overflow it is meant to show.
- Two diagrams repeat content errors from the accuracy review: the GEMV figure explains the benchmark wrongly, and the wavelet figure says "f16" where the SDK uses i16.

The chapter explains several mechanisms only in prose that would work better as visuals: bank interleaving, microthread occupancy and the conflict that hung Lab 3, matvec memory traffic, and sparse wavelet encoding.

## Findings (defects in existing visuals)

### V1 [major] Anatomy SVG: "(WEST port omitted for clarity)" overlaps the S arrow, and "RAMP" runs into the router box
Location: first `<figure>`, router group (`<text x="470" y="268">` and `<text x="398" y="190">`).
Problem: The note text spans x = 391–549, y = 257–271 (measured with getBBox). The S arrow runs down x = 470 from y = 250 to 300, so the arrow crosses the words "omitted for". The "RAMP" label spans x = 398–434, but the router rect starts at x = 420, so the last two letters sit on the router's border.
Evidence: screenshots at 1100 px, light and dark: the arrow line visibly cuts through "omitted"; "RAMP" touches the router outline.
Concrete fix: Draw the West port instead of apologising for it (see V2). That makes the note unnecessary, so delete it. Move the RAMP label below its arrow, clear of the router: `<text x="402" y="222" font-size="12" font-weight="600" text-anchor="middle">RAMP</text>`. Alternatively, shorten the arrow to `M420 200 H392` and set `text-anchor="end"` at x = 416.

### V2 [major] Anatomy SVG: the router's ports are drawn as one-way outputs, the West port is missing, and the RAMP is drawn as one-way into the CE
Location: the four `<path … marker-end="url(#a4)">` elements around the router.
Problem: Every fabric link and the RAMP carry wavelets in both directions. Chapter 4 relies on this: data arrives *from* a neighbour and goes *up* the RAMP to the CE. The diagram shows N, S and E as outputs only and the RAMP as router-to-CE only, which reverses half the data flow this chapter describes ("Arriving data activates tasks"). The caption also calls the RAMP the "fifth port", yet only four port arrows are drawn and one is labelled "omitted". A learner counting ports gets four.
Evidence: 1100 px render: only arrowheads pointing away from the router; no W arrow.
Concrete fix: Add `marker-start` with a reversed marker, or draw pairs of thin parallel arrows (in and out) on every port. Add a West port. There is room if the RAMP enters the router from the lower left as a bent path, for example `M420 230 H395 V300 H380`, or if the router moves to x = 440 and W exits leftwards above the RAMP at y = 175. Add `<marker id="a4s" … orient="auto-start-reverse">` and give every port path both `marker-start` and `marker-end`. Label all five: N, E, S, W, RAMP.

### V3 [major] All three SVGs are illegible on a 390 px phone
Location: all `<figure>` SVGs (`width="760"`, scaled down by `max-width:100%`).
Problem: At 390 px the content width is about 330 px, a scale of 0.43. The 11–12 px labels render at about 5 px, which cannot be read: the bank "6K" labels, "activated ∧ unblocked", "bit 31", the GEMV box text.
Evidence: `el0-light-390.png`, `el2-light-390.png`, `el3-light-390.png`. The text is a smudge, while the captions under the figures are fine.
Concrete fix (choose one):
1. Wrap each figure's SVG in a horizontal scroller: CSS `.fig-scroll{overflow-x:auto} .fig-scroll>svg{min-width:600px}` and `<div class="fig-scroll">` around the SVG. This keeps text at about 10 px or larger and matches what ch09 already does with overflow-x.
2. For the anatomy, give a stacked portrait variant below 680 px: a second `<svg viewBox="0 0 380 640">` with the CE on top and the router below, toggled by `@media`.
3. The wavelet and GEMV figures are simple enough to rebuild as HTML (two flex boxes, or two `.card`s), which reflows naturally.

### V4 [minor] The anatomy's CE caption text runs into the CE box border
Location: `<text x="56" y="182" font-size="12">single-cycle · interleaved by 32-bit word · code AND data</text>`.
Problem: The text ends at x = 381; the CE box's right edge is x = 380. "data" touches or crosses the border, depending on the font.
Evidence: getBBox reports x 56–381. Visible in the 1100 px screenshots.
Concrete fix: Use `font-size="11"`, or split it into two lines ("single-cycle · interleaved by 32-bit word" / "holds code AND data") at y = 180 and y = 193, nudging the row of three boxes down by 6 px. Alternatively, shorten it to "1 cycle · word-interleaved · code + data".

### V5 [minor] JS-drawn colours go stale when the reader uses the ◐ theme toggle
Location: inline script, `fill: cssVar("--green")` for `#lanes`, `fill: cssVar("--amber")` for `#uts`, and `cssVar(c)` / `cssVar("--red")` in `budget()`.
Problem: `cssVar` reads the computed value once, at draw time. After clicking ◐ the page switches theme, but the SIMD lanes, the microthread dots and the budget bar keep the previous theme's hex values. In dark mode you get dark orange and saturated purple segments on a dark surface, which are noticeably lower contrast than the dark tokens.
Evidence: loaded light, clicked the toggle (`data-theme="dark"`), took screenshots (`tog-fig.png`, `tog-w.png`). The microthread dots are brownish orange (light `--amber` #b45309) and the bar is light `--accent` #c2410c and `--purple` #7c3aed. Compare the fresh dark load, where they are #fbbf24, #fb923c and #b79cff.
Concrete fix: Use the existing classes instead of resolved colours. For the lanes, `el("rect", {…, class:"f-grn", opacity:.75})`; for the dots, `class:"f-amb"`. In `budget()`, map parts to classes, e.g. `["matrix A", A, "f-acc"]` → `el("rect", {…, class: c})`, and the 48 KB line → `class:"s-red"`. These go through `var(--…)` and follow the theme live.

### V6 [major] Budget widget: the legend has no colours, so it identifies nothing
Location: `el("text", …).textContent = "■ A   ■ vectors   ■ code/runtime"`.
Problem: The three squares are glyphs inside one `class="muted"` text node, so all three are grey. The reader cannot tell which segment is vectors and which is code. The vectors segment is a few pixels wide and the two are adjacent.
Evidence: every widget screenshot shows three grey squares.
Concrete fix: Draw separate `rect` swatches with `class="f-acc|f-blu|f-pur"` (10×10 at y = 68) followed by separate `<text>` labels. Alternatively, use `<tspan class="…">■</tspan>` with a fill class per tspan.

### V7 [major] Budget widget: overflow is hidden exactly when it matters
Location: `budget()`, `const w = Math.min(sz * s, x0 + Wd - x)`.
Problem: When the total exceeds 48 KB, each segment is clamped at the 48 KB line. At M = N = 128 (f32) the bar is solid orange. The vectors and code segments disappear entirely, and nothing shows that the demand is 67.5 KB, 41% over. The "DOES NOT FIT" text is plain monospace with no colour.
Evidence: `w-over.png` at 128×128 f32: one full orange bar; the readout says total 67.5 KB.
Concrete fix: Scale the bar to `max(total, used)` and keep the 48 KB marker where it falls. Alternatively, keep the 48 KB scale and draw the overflow past the red line as a hatched or red-outlined segment, which needs `viewBox` widened to about 0 0 900 90 so the bar can extend 1.5×. Add an "over by X KB" label. Colour the verdict: wrap it in `<b style="color:var(--red)">` or `var(--green)` (switch `#b-out` to `innerHTML`, or use two spans).

### V8 [minor] Budget widget: the hint does not match the controls, and the question it asks is never answered
Location: `.hint` "…plus a few vectors in f32. How big can the block be?" and `#b-out`.
Problem:
- The hint fixes f32, but the dtype select also offers f16.
- The widget never states the answer: the largest square block that fits, which is 104 at f32 with this model and 144 at f16. The f16 answer is beyond the slider maximum of 128, so f16 can never show "DOES NOT FIT" for a square block. The largest f16 total is 34.8 KB, which means half the dtype option is uninteresting.
- The ~2 KB code constant is contradicted by the accuracy review (A-series: measured .text is about 2.5–3.4 KB).
Evidence: slider sweeps: 104×104×4 → 45.5 KB fits, 108×108×4 → 48.8 KB does not fit, 128×128×2 → 34.8 KB fits.
Concrete fix:
- Change the hint to "…plus vectors x, y, b".
- Raise `max` on both sliders to 160 so f16 can overflow.
- Add a readout line computed from the current dtype: `largest square block: floor(sqrt((48K − code − 3·N·t)/t))`, solved numerically by a loop.
- Make the code size a third slider (2–6 KB, default 3 KB) labelled "code + runtime (measured 2.5–3.4 KB in the SDK labs)".

### V9 [minor] Budget readout wraps mid-token on mobile and is not announced
Location: `#b-out` (`white-space: pre-wrap`).
Problem: At 390 px the first line wraps as "vectors:" / "0.56 KB" and "(36.4" / "KB free)". The readout has no `aria-live`, so screen-reader users get no feedback when they move a slider.
Evidence: `el1-light-390.png`.
Concrete fix: Put one fact per line: A, vectors, code, total, verdict. Add `aria-live="polite"` to `#b-out` and an `aria-describedby="b-out"` on the sliders.

### V10 [major] The GEMV "relative vs absolute" figure diagrams the wrong mechanism (content)
Location: second `<figure>` (`aria-label="Relative versus absolute bandwidth"`).
Problem: The figure says the cached machine "reads x once into cache, reuses it". The benchmark's actual distinction is about **y**: a cached architecture writes y once, while the WSE kernel reads and writes y on every column. `x` is read once in both counts. This is also a text-only box pair that does not visualise traffic at all. See accuracy review A2.
Evidence: `single-tile-matvec/run.py` L202–215 counts relative = 4·nb² + 8·nb bytes and absolute = 12·nb² + 4·nb bytes. README L54–59 says "caching allows us to write the y vector for example, only once".
Concrete fix: Replace it with the interactive traffic stepper in proposal P2. At minimum, change the left box text to "reads A and x once, keeps y in cache, writes y once: 4nb²+8nb B" and the right to "reads A and x once, but reads and writes y every column: 12nb²+4nb B".

### V11 [minor] Wavelet figure labels the data half "f16"; the SDK example uses i16 (content)
Location: third `<figure>`, `<text …>lower 16 bits: f16 value</text>`.
Problem: The caption beneath it says `wavelet_data: i16`, so the figure and the caption contradict each other. The topic-04 README says only "lower 16 bits to contain data".
Concrete fix: Change the label to "lower 16 bits: data (i16 in topic-04)". Optionally add tick marks at bits 15 and 16 at the split (x = 380) so the boundary is labelled. This is the same issue as accuracy review A-series item "f16 vs i16".

### V12 [minor] The anatomy says "✕ OS / threads" right beside "8 microthreads"
Location: "Not here:" list, `<text x="580" y="152">✕ OS / threads</text>`.
Problem: A newcomer reads this as a contradiction: no threads, yet 8 microthreads in the same diagram.
Concrete fix: Change it to "✕ OS / software threads", or "✕ OS, scheduler, preemption".

### V13 [minor] The SIMD datapath shows 8 lanes with no width label
Location: `#lanes` (8 rects), "SIMD datapath" box.
Problem: The prose says 8-way for FP16/BF16 and 16-way for INT8. The drawing shows 8 unlabelled lanes, so a reader cannot tell which dtype they represent.
Concrete fix: Add `<text x="210" y="298" text-anchor="middle" font-size="10" class="muted">8 × FP16 · 16 × INT8 (WSE-3)</text>` under the lanes. Shrink the lanes to height 10 at y = 278 to make room, or extend the box to height 56.

## Proposed new visuals (prioritised)

### P1. Interactive "budget → anatomy" link (low cost, high payoff)
Purpose: tie the 48 KB widget to the diagram, so the bank strip in the anatomy is the memory being budgeted.
Content: Re-use the 8-bank strip. The widget fills the banks proportionally: matrix A in accent, vectors in blue, code in purple. Overflow beyond bank 8 spills into a ghost "9th bank" drawn dashed in red. Because memory is word-interleaved, a contiguous array actually stripes across all 8 banks. Show this with a toggle, "address view" vs "bank view": the address view is a linear bar, and the bank view shows each bank filled to the same height.
Interaction: driven by the existing M/N/dtype controls; the view toggle is a two-button segmented control.
Placement: replace the current single bar inside `#budget`.

### P2. Matvec memory-traffic stepper (replaces the GEMV figure; fixes V10)
Purpose: show *why* the WSE's absolute traffic is about 3× the cached-machine count, and that the SRAM absorbs it.
Content: A small nb×nb grid for A (nb from 4 to 12), a column vector x and a column vector y. The kernel goes column by column: y += A[:,j]·x[j]. Each step highlights column j of A (read), x[j] (read) and the whole of y (read and then written). Two running counters:
- relative bytes = 4·(nb·nb + 2·nb), shown as reaching its final value only at the end (y written once);
- absolute bytes = 4·(nb + nb·nb + 2·nb·nb) = 12nb² + 4nb.

At the end, show the ratio (≈3× for large nb). Formulas from `single-tile-matvec/run.py` L202–215 <span class="tag sdk">SDK 2.10.1</span>.
Interaction: an nb slider (4–12), Step / Play / Reset buttons, and a speed control. Optionally show the per-cycle cost: 2 reads and 1 write of y elements per FMAC, against the "few 32-bit accesses per cycle" the chapter derives.
Placement: section "Why no caches?", replacing the current second figure.

### P3. Microthread occupancy timeline (the Lab 3 hang)
Purpose: make "two operations must never share a microthread at the same time" concrete. Today it is one sentence plus a reference to a hang.
Content: 8 horizontal swim lanes labelled ut0–ut7 on a time axis of 0–40 "steps". Preset ops come from topic-15: `@fmovs y → out_dsd` (output queue 2, microthread 4) and `@fmovs in_dsd → y` (input queue 2, microthread 5). On WSE-2 the microthread equals the queue ID. Show that default ("if not specified, they default to the respective queue IDs") as a toggle that collapses both ops onto lane 2 → red overlap → "conflict: undefined / hang".
Interaction: the user adds an async op with a dropdown for microthread ID (0–7 or "default = queue"), a queue ID, a start time and a length. Bars that overlap on a lane turn red and the readout explains why. A preset button reproduces the Lab 3 configuration; take the exact queue and ID pair from `course/programs/03-*/pe_program.csl`.
Placement: after "Compute: SIMD lanes driven by descriptors". Alternatively, cross-link it from the "8 microthreads" block in the anatomy.

### P4. Sparse wavelet encoder / stream (upgrades the static wavelet figure)
Purpose: show *why* sparsity is "free" (fewer wavelets mean fewer task activations) and how the 32-bit packing works.
Content: a 16-element vector with a sparsity slider (0–90%) that zeroes random elements. Two streams animate side by side:
- dense: 16 wavelets, 16 receiver task activations;
- sparse: nnz wavelets, each shown as `0xIIIIDDDD` with the upper half as the index and the lower half as the i16 data. Data bits are green, index bits purple, matching the current figure.

The receiver PE shows a counter of task activations and reconstructs the vector from (index, value) pairs. Click a wavelet to expand its 32 bits as a bit ruler with labels at bits 31, 16, 15 and 0. Source: topic-04 README <span class="tag sdk">SDK 2.10.1</span>.
Interaction: the sparsity slider, a re-randomise button, and click-to-inspect on each wavelet.
Placement: "Sparsity comes free with dataflow", replacing the third figure.

### P5. Bank-interleaving illustration
Purpose: the prose claims interleaving lets vector ops touch "several consecutive words per cycle without bank conflicts". Show the address→bank mapping.
Content: 32 word addresses laid out as a grid, coloured by bank = (word address mod 8), next to the 8 banks. A DSD with base, length and stride highlights the words it touches; each bank's hit count is shown.
- Stride 1: hits spread evenly across the banks.
- Stride 8: every access lands on one bank.
- Stride 2 or 4: half or a quarter of the banks.

Present it as an illustrative model, because the per-cycle port count is not in the sources. Tag it <span class="tag derived">Derived</span>, and do not claim cycle counts.
Interaction: stride slider (1–16), base slider (0–7), length slider (1–32).
Placement: "Memory: 48 KB, one cycle, nothing else", right after the first paragraph.

### P6. Bandwidth derivation chain (small static figure)
Purpose: make the "21 PB/s ÷ 900,000 PEs" sanity check visible.
Content: a left-to-right chain of four boxes: "21 PB/s wafer" → "÷ 900,000 PEs" → "≈ 23 GB/s per PE" → "÷ ~1 GHz ≈ 23 B/cycle ≈ 6 × 32-bit words/cycle". Each box carries its provenance tag: vendor, vendor, derived, derived. Build it in HTML flex so it wraps on mobile.
Interaction: none.
Placement: inline after the paragraph that ends with the derivation.

### P7. Anatomy hover and focus tooltips
Purpose: turn the anatomy into a navigational map.
Content: each block (banks, SW cache, GPRs, DSRs, SIMD, task picker, microthreads, router) gets a `<title>` and `tabindex="0"`. On hover or focus, a side panel shows a one-line definition, the number with its provenance tag, and the chapter where it is covered: DSRs → Ch. 6, task picker → Ch. 5, router → Ch. 4.
Interaction: hover or keyboard focus. On mobile, tap.
Placement: the existing first figure.
