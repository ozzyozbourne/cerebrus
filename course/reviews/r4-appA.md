# Round-4 audit: Appendix A (glossary and number formats), page-id appA

**Verdict: Mostly correct. Explanation quality: good** (each entry is clear, but the glossary leaves out much of the vocabulary needed to read CSL code).

Method:
- Extracted all 176 entries and checked every number against its linked chapter and CROSS_CHAPTER_NOTES 1–29.
- Resolved all 325 internal links with a script and compared each label with its target heading. All resolve, and no label is wrong.
- Counted how often every `@builtin`, `<library>`, acronym and bold or `<dfn>` term appears in chapters 01–18 and Appendices B–E, then checked which of them the glossary search finds.
- Rendered the page at 390 px with Playwright: no JS errors and no horizontal overflow. Ran 10 test searches.
- Re-read the formats section, the support table and programs/07-cg/run.py (for the residual entry).
- Ran no simulator jobs. The scratch dir has been deleted.

r2 items A1–A6, R1–R5 and V1–V7 are all fixed. r2's P5 (chapters do not link into the glossary) is **partly fixed**: course.js now puts a "Glossary" link in the top bar, but no chapter 01–18 links to any `#g-` entry.

## Errors

**E1 (med): the "Tokens/s: per user vs aggregate" entry quotes the ceiling Ch 9 itself calls an overstatement.**
- Location: `#g-tokens-per-second`.
- The entry reads: "On four CS-3s the pipe-full ceiling is ~600,000 tok/s in total at the headline bandwidth, but one user's token is in one of 80 regions at a time and sees ~1/80 of it, ~7,500 tok/s."
- Ch 9 (#budget) says ~7,500 is "an overstatement for the same reason", because the 21 PB/s figure counts write ports. At a region's GEMV rate the one-user bound is "~2,000–4,000 tok/s" (~2,000 at the measured f16 matvec rate), and the measured 2,314 tok/s falls inside that range. CROSS_CHAPTER_NOTES 25 and 27 say the same.
- A learner who reads only the glossary takes away 7,500 as the real limit.
- Fix: "…~7,500 tok/s at the headline 21 PB/s (an overstatement: weights use only the read ports). At a region's GEMV kernel rate the bound is ~2,000–4,000 tok/s; the measured 2,314 sits in that range. The limit is a chain of 80 layer reads plus latency, not raw bandwidth."

**E2 (low): the `sim.log / sim_stats.json` entry understates the noise and fixes the idle tail at 50 cycles.**
- The entry says cycle_count runs "from load to a 50-cycle idle tail, noisy by a few percent under host load."
- Ch 10 (#sim-outputs) shows 7,786–11,004 cycles for the same WSE-3 program, and 8,885 on WSE-2 with a **2,109-cycle** idle tail. App C saw cycle_count move by 36 %. Note 26 records −3 % to +41 %.
- Fix: "usually a 50-cycle idle tail and a few percent of noise, but up to ~40 % (and a longer tail) on a loaded host; time kernels with the TSC."

**E3 (low): the lede's tag legend is incomplete.**
- The lede lists Vendor / Independent / SDK / Measured / Derived / Unverified. It leaves out **Analyst**, which Ch 1, 2, 9 and 18 use.
- The page's own support table uses a "Secondary" label in the `indep` class (WSE-2 fp16 4-wide), which the legend does not explain.
- Fix: add Analyst, say that "Secondary" (and "Vendor via secondary") means a second-hand report, and link to App E's tag table.

## Explanation problems

**X1 (Residual entry).** The entry says CG "stops when ⟨r, r⟩ falls below tol²". It does not say that tol = EPS·|b| (programs/07-cg/run.py line 31; Ch 15 #problem), so a learner who sees `--eps` in run.py cannot connect the two. Add "(tol = EPS·|b|, a relative tolerance)".

**X2 (Task ID entry).** The entry reads: "Activatable IDs are below 31; WSE-3 local IDs run 8–30; control IDs 0–63". It reads as if 0–63 contradicts "below 31". Say that data and local tasks bind to IDs 0–30, while control-task IDs are a separate 0–63 space named in the control wavelet's payload. Ch 5 shows this with `@get_control_task_id(43) // > 31 is fine for control tasks`.

**X3 (WSE-2 gaps in WSE-3-only figures).** cslc defaults to `--arch=wse2`, as the glossary's own cslc entry says, yet several entries give only the WSE-3 figure:
- Local task: WSE-2 is 0–30, minus the IDs of colors you receive on (Ch 5 table).
- TSC: the 10-cycle empty region is a WSE-3 measurement.
- Task ID.

Add the WSE-2 value, or write "WSE-3:" explicitly.

**X4 (bare link labels).** "Ch. 4" (Wavelet), "Ch. 1" (HBM) and "Ch. 8" (TP/PP/DP) are the only links without a section name. Name the section, as the other 320 links do.

**X5 (Bank clash entry).** The entry states the f32 @fmacs rule only. App E (open issue 2) and note 29 measured f16 @fmach on WSE-2: it is slow at 0 or 2 banks apart and fast only at 4 banks apart, while WSE-3 shows no penalty. Add one sentence on this and a link to App E.

## Connecting gaps

**G1 (high, S–M): the glossary cannot help a learner read CSL code.**
- Ideas that fail to connect: the concept entries (DSD, color, task ID, queue) → the code identifiers that create them in every lab.
- These identifiers have no entry, and searching for them returns "No term matches" (checked live):
  - `@get_dsd`: 56 uses on 9 pages
  - `sys_mod`: 40
  - `@get_color`: 29
  - `@get_local_task_id`: 27
  - `memcpy_params`: 24
  - `@increment_dsd_offset`: 17, plus `@set_dsd_length` / `@set_dsd_base_addr`
  - `@get_input_queue` / `@get_output_queue`
  - `mem4d_dsd`
  - many-item pointers `[*]f32`: 69
  - `i16` / `u16` as types
  - memcpy's `order=` / `MEMCPY_16BIT` / row-major flags
- `mem1d_dsd` and `tensor_access` exist only as hidden aliases of the DSD entry, whose definition never shows the syntax.
- Bridge, four short entries:
  1. "@get_dsd / mem1d_dsd / tensor_access", with the one-line example `@get_dsd(mem1d_dsd, .{ .tensor_access = |i|{N} -> x[i] })` and a link to 06#one-instruction.
  2. "Handle builtins: @get_color, @get_local_task_id, @get_data_task_id, @get_input_queue / @get_output_queue, @get_ut_id". Explain that they turn a number into a typed handle and that the numbers come from the layout. Link to 05#activates and 10#hardware-parts.
  3. "sys_mod / memcpy_params": the memcpy module instance imported with the params the layout passes in, and the object you call `unblock_cmd_stream()` on. Link to 07#command-stream and 10.
  4. "DSD mutators (@increment_dsd_offset, @set_dsd_length, @set_dsd_base_addr)", with the ~33–35 cycles per step cost (note 16). Link to 06 and 13.

**G2 (med, S): source shorthands and SDK example names are undefined.**
- Ideas that fail to connect: a provenance tag's label → what the label refers to.
- "topic-NN" appears 114 times and "HC22" / "HC2024" / "SC20" about 60 times, inside tags such as "SDK 2.10.1, topic-15" and "Vendor (HC22)". None of them is in the glossary.
- Bridge:
  - Entry "topic-NN, benchmark names": an SDK tutorial or benchmark directory, linked to App D #index.
  - Entry "HC22 / HC2024 / SC20": Hot Chips 2022 / 2024 decks and the SC20 paper, linked to App E's bibliography.
  - Entry "Provenance tags", linked to App E's tag table. This one also covers E3.

**G3 (med, S): course concepts that have no entry.**
- **Host-driven vs device-driven loop** (Ch 11, Ch 15; 19 uses). This is Lab 5's main host-overhead lesson.
- **Strong scaling** (bold-headed in Ch 13 and 14, used in 18). Weak scaling has an entry, but the contrast does not.
- **FSM task / lock task** (Ch 14 #collectives), the internals of `<collectives_2d>`.
- **CE-ignore bit** (Ch 4, 14).
- **Rubin CPX** (Ch 9, 17, 18).
- **Artificial Analysis** (16 uses: the "Indep" source behind the 2,314 tok/s figure).
- **PTX / CUTLASS** (Ch 17, 29 uses).
- The alias **matvec** for GEMV (45 uses; searching "matvec" returns nothing).

Each needs one or two lines plus a link.

**G4 (med, S): entries are not cross-linked into the chains a learner must follow.**
- Only about 12 entries link to another entry.
- Ideas that fail to connect:
  - **Bank (SRAM bank) → Bank clash.** Neither entry explains *why* "equal mod 4 words" collides. Under the SDK rule (bits [3:1] pick the bank), an f32 at word address w occupies banks 2w mod 8 and 2w+1 mod 8. So two words share both banks exactly when w₁ ≡ w₂ (mod 4) [Derived; the physical width is unpublished]. Put this one line in the Bank-clash entry and link the two entries both ways. The Bank entry should also link to 06#collisions.
  - **Task → Activate / Block → Join → Task picker.**
  - **Input queue → Microthread → .ut_id** (the Lab 3 hang chain).
  - **Control wavelet → Switch / Teardown → @queue_flush.**
  - **launch / RPC → Command stream → unblock_cmd_stream() → Kernel stall.**
- Bridge: a "Related:" line of `#g-` links on each entry in these five chains.

**G5 (med, M, outside this file): no chapter links into the glossary, and many terms are used before the chapter that teaches them.**
- The glossary is the natural bridge for these forward uses, but nothing links to it:
  - cslc / cs_python / cs_readelf / the simulator: used with measurements from Ch 3, taught in Ch 10
  - DSD: Ch 3 and 5, taught in Ch 6
  - memcpy: Ch 2–5, taught in Ch 7
  - Tensix / Blackhole / MemoryX: Ch 1, taught in Ch 16 / 8
  - `.ut_id`: Ch 3, taught in Ch 5
  - TSC: Ch 3 and 11, taught in Ch 12 and 13
  - SpMV: Ch 5, taught in Ch 15
- Ch 1 and Ch 17 have their own "Terms used here" boxes that do not link to App A.
- Bridge, for the coordinator: link the first forward use of each of these ~20 terms to `appendix-a-glossary.html#g-…`, and add a "Full glossary" link to both boxes. The ids are stable.
- Still open (from r2-appA-visuals.md, P5).

**G6 (low, S): KV cache → how many users fit.** The KV-cache entry stops at "must fit in the SRAM the weights leave free". It does not give the course's result: at 8K context at most ~13 users (~7 after code overhead) per 4 × CS-3 (note 28, Ch 9). That result is what links KV size to the per-user vs aggregate distinction in the tokens/s entry. Add one clause.

## Checked and fine
- All 325 internal links resolve, and their labels match the target headings.
- Allreduce fit 958 + 100·W + 88·H, and the two calls per iteration (Ch 15).
- TSC: enable_tsc() zeroes the counter, an empty region reads 10 cycles, and counters on different PEs are not aligned (App C, notes 19 and 26).
- Hop 2.0 / 1.0 and 9.2 / 6.0. Store-and-forward 348 vs 101. `<collectives_2d>` ≈ 700 cycles.
- Task IDs: local 8–30 on WSE-3, user IDs 8–20, control IDs 0–63, memcpy 33–37 and 40, teardown task 29, the priority vector covers 0–31 (Ch 5, Ch 4).
- memcpy colors 20–23 with the command stream on 22; queues 8/6 and 8/8; memcpy owns queues 0 and 1; frame layout (Ch 7, note 8).
- Color swap is WSE-2 only; WSE-3 allows one fabric input per operation and one rx per route; the 24 colors and 6 filters.
- Software cache 256 / 512 B; CE register counts and their attribution; banks and bits [3:1].
- WSE-1 400k / ~380k; WSE-2 850k at 1.1 GHz; CS-3 ~23 kW, 15U; CS-4 is three WSE-3T.
- Spec-decoding formulas: 3.36 at α = 0.8, k = 4; ≈ 1.4× on the wafer; c ≈ 0.3–0.4.
- MoE (Kimi K2.6, 1T / 32B). TTFT 240 ms (405B, Nov 2024). KV cache 327,680 B.
- Tenstorrent: flit and packet sizes, CB counts, 9-cycle hop, 711 / 515 ns CCL hop, fidelity cycles, Blackhole 120 cores, TSMC 6 nm.
- GPU: H100 SM numbers, 256 / 228 KB, NVLink, Groq LP30 (~500 MB, ~150 TB/s), TPU Ironwood, the cost-per-million-tokens formula (Ch 18).
- Format table ranges; f16 encoding test; int8 / i8 DSD limit (Ch 10 now lists i8 / u8 / i64 / u64); support-table SIMD widths and tags match Ch 2 and 3.
- Page renders at 390 px with no errors or overflow; all 176 entries present.
