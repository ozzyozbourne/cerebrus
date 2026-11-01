# ch01 · accuracy review

Summary: Chapter 1 is accurate on almost every headline number. The H100 ridge (989 TF ÷ 3.35 TB/s ≈ 295), the decode and prefill intensities, the 5.7× Rubin bandwidth growth, the B200, Blackhole and WSE-3 roofline inputs, the 1.4 MiB Tensix L1, the ~512 KB/SM and ~66 MB H100 figures, and the quiz arithmetic all match the research report and notes. There is one real arithmetic error: the "Vector add" roofline preset is 2–3× too high. The other findings are softer. Several numbers have no provenance tag, which breaks the chapter's own rule that "every figure carries a tag". The "7,000×" claim does not match the chapter's own inputs. One caption and the roofline hint overreach slightly. The Part II roadmap leaves out the Host I/O chapter. Verdict: fine to ship once A1 is fixed; the rest are polish.

## Findings

### A1 [major] Vector-add preset intensity is wrong (0.25 FLOP/B)
- Location: Interactive roofline, `#roof-preset`, option `<option value="-0.6">Vector add (0.25 FLOP/B f32)</option>`.
- Problem: An f32 vector add `c = a + b` does 1 FLOP per element. It reads 8 bytes and writes 4. That gives 1/8 = 0.125 FLOP/B counting reads only (the chapter defines intensity as "for each byte it reads", line 27). Counting all DRAM traffic, as the standard roofline does, it is 1/12 ≈ 0.083 FLOP/B. 0.25 FLOP/B (10^-0.6 = 0.251) would mean 1 FLOP per 4 bytes, and no form of vector add has that ratio. The slider minimum is -1 (0.1 FLOP/B), so the read-only value 0.125 is the one that fits on the axis.
- Evidence: The arithmetic itself. Line 27 defines intensity as "how many floating-point operations it performs for each byte it reads". The quiz on line 135 uses the same reads-only convention ("2 FLOPs per 4-byte float it reads … 0.5 FLOP/byte").
- Concrete fix: Replace `<option value="-0.6">Vector add (0.25 FLOP/B f32)</option>` with `<option value="-0.9">Vector add, f32 (~0.125 FLOP/B: 1 add per 8 bytes read)</option>`.

### A2 [minor] Intensity defined on bytes read only; the standard roofline counts all bytes moved
- Location: Section "Two numbers describe every accelerator", paragraph on line 27.
- Problem: "how many floating-point operations it performs for each byte it reads" is narrower than the standard roofline definition, which counts bytes moved to and from memory (reads plus writes). For decode, where reads of the weights dominate, the result is the same. For streaming kernels such as vector add, it overstates intensity.
- Evidence: Report line 15 defines the ridge as "peak FLOP/s divided by memory bandwidth" and uses "bytes of weights read" only for decode. It never says writes are excluded in general.
- Concrete fix: Replace `how many floating-point operations it performs for each byte it reads.` with `how many floating-point operations it performs for each byte it moves to or from memory (for LLM decode that is essentially the weight bytes it reads).`

### A3 [minor] "7,000×" does not match the chapter's own numbers
- Location: Callout "The comparison trap", line 122.
- Problem: The callout quotes 7,000× next to 21 PB/s and 3.35 TB/s. Those two numbers give 21e15 / 3.35e12 ≈ 6,300×. The quote is correctly tagged Vendor, but a reader who checks the division will find a mismatch. 7,000× is what you get from 21 PB/s ÷ ~3 TB/s, which looks like an older GPU baseline. Also beware: `research_notes/.../gpu_and_comparison.md` line 70 says "about 2,600x an H100's HBM bandwidth", which is itself wrong arithmetic and must not be copied.
- Evidence: Report line 19: "Cerebras markets "7,000×" the memory bandwidth … [Vendor] (Cerebras chip page, via search extract)". Report line 17: "WSE-3: 44 GB at 21 PB/s". Report line 235: "80 GB of HBM3 at 3.35 TB/s".
- Concrete fix: After `That compares on-wafer SRAM (21 PB/s) to the GPU's <em>off-chip</em> HBM (3.35 TB/s).` insert ` (Those two figures actually give about 6,300× <span class="tag derived">Derived</span>; the marketing figure appears to use a slightly lower GPU baseline.)`

### A4 [minor] Decode and prefill intensities have no provenance tags
- Location: Section "Why LLM decode lives on the slanted part", paragraph on line 49. Also the SVG captions "≈ 1 FLOP / byte" and "≈ thousands of FLOP / byte", and "140 GB (70B, fp16)".
- Problem: "about 1 FLOP per byte", "about 50–100 FLOP/byte" and "thousands of FLOP/byte" carry no tag. The how-to-read callout on line 130 promises "Every figure carries a tag." These figures come from third-party analysis plus simple arithmetic, so Derived is the right tag.
- Evidence: Notes `gpu_and_comparison.md` line 74: "Decode at batch 1 has about 1 FLOP/byte … Batch 64 on a 70B model reaches about 50–100 FLOP/byte … Prefill … can reach thousands of FLOP/byte" (sources: dev.to, Zartis, ZeroEntropy blogs).
- Concrete fix: In line 49, after `<strong>about 1 FLOP per byte of weights</strong>` insert ` <span class="tag derived">Derived</span>`. After `about 50–100 FLOP/byte` insert ` <span class="tag derived">Derived</span>`. After `reaching thousands of FLOP/byte` insert ` <span class="tag derived">Derived</span>`.

### A5 [minor] Comparison-trap capacity numbers have no tags
- Location: Callout "The comparison trap", last sentence: "44 GB on a wafer versus ~66 MB of registers and L1 on an H100."
- Problem: Neither number is tagged. 44 GB is a vendor figure. ~66 MB is derived (132 SMs × (256 KB RF + 256 KB L1/smem) ≈ 67.6 MB, or 66 MiB).
- Evidence: Report line 30: "On-chip SRAM … 44 GB [Vendor]". Report line 259: "~50 MB L2 + ~66 MB RF/L1 (H100) [Derived]". Report line 235: "132 SMs … each with a 256 KB register file and 256 KB of combined L1/shared memory".
- Concrete fix: Replace `44 GB on a wafer versus ~66 MB of registers and L1 on an H100.` with `44 GB on a wafer <span class="tag vendor">Vendor</span> versus ~66 MB of registers and L1 on an H100 (132 SMs × 512 KB) <span class="tag derived">Derived</span>.`

### A6 [minor] "Three answers" figure numbers are untagged; the only tag is a non-standard SVG tspan
- Location: Figure "Where does the working set live?" (SVG, lines 85–116).
- Problem: Several figures carry no provenance: ~512 KB/SM, 50 MB L2, 80 GB · 3.35 TB/s, 1.4 MiB/core, 32 GB · ~0.5 TB/s, 48 KB, × 900,000, 44 GB. The only tag is `[Vendor]` on 21 PB/s. All of these are correct.
- Evidence: Report line 235 (H100: 256 KB RF + 256 KB L1, 50 MB L2, 80 GB HBM3 at 3.35 TB/s [Vendor]). `tenstorrent.md` line 55 ("1464 KiB (about 1.43 MiB)"). Report line 213 ("32 GB GDDR6 at about 512 GB/s" [Vendor]). Report line 3 (48 KB, 900,000 cores, 44 GB).
- Concrete fix: Keep the SVG as it is and add tags to the figcaption. Append to the end of the `<figcaption>` on line 117: ` Capacities and bandwidths: <span class="tag vendor">Vendor</span>; ~512 KB/SM is 256 KB RF + 256 KB L1/smem <span class="tag derived">Derived</span>.`

### A7 [minor] Caption overclaims that "every byte is one cycle from the core that uses it"
- Location: Figcaption on line 117: "Cerebras's bet is to remove the hierarchy entirely: every byte is one cycle from the core that uses it."
- Problem: Each byte is one cycle only from the PE that owns it. Data on any other PE must cross the fabric at roughly one hop per cycle plus about 2 cycles of ramp. The callout below and quiz Q3 say this correctly. Also, WSE-3 still has a small software-managed 512 B cache per PE, so "entirely" overstates.
- Evidence: Report line 54: "a small software-managed cache … 256 B on WSE-2, 512 B on WSE-3 [Vendor]". Report line 62: "a hop takes about one cycle. The ramp takes about 2 cycles". Chapter line 137: "Each PE can only reach its own 48 KB at that speed".
- Concrete fix: Replace `Cerebras's bet is to remove the hierarchy entirely: every byte is one cycle from the core that uses it.` with `Cerebras's bet is to remove the DRAM-and-cache hierarchy: every byte is one cycle from the core that owns it, and anything else arrives over the fabric.`

### A8 [minor] Roofline hint invites the very SRAM-vs-HBM comparison the chapter warns about
- Location: Roofline widget hint (line 33) and the WSE-3 entry in `chips` (line 148).
- Problem: The WSE-3 curve uses aggregate per-PE SRAM bandwidth (ridge ≈ 0.74 FLOP/B), while the GPU and Tenstorrent curves use off-chip DRAM. Plotted together, they show the 21 PB/s vs 3.35 TB/s comparison that the callout calls a trap. There is also no Derived tag on the ridge values the widget computes.
- Evidence: Chapter line 122: "That compares on-wafer SRAM (21 PB/s) to the GPU's off-chip HBM … not apples to apples" (also quiz line 137). Report line 19.
- Concrete fix: Replace the hint text `using that chip's main working memory. Axes are log-scale.` with `using the memory that holds that chip's weights (HBM/GDDR for GPU and Tenstorrent, local SRAM for the wafer; see the comparison trap below). Ridge points are computed here <span class="tag derived">Derived</span>. Axes are log-scale.`

### A9 [minor] Course roadmap leaves out a Part II chapter and misplaces "the wafer"
- Location: Section "What this course covers", line 126.
- Problem: "Part II takes the wafer apart from the bottom up: the single processing element, the fabric …, the task model …, the descriptors …, and the systems …". This skips Chapter 7 (Host I/O and memcpy), which is in Part II. Chapter 2 (the wafer) belongs to Part I and is not mentioned. The rest checks out: Part III has the toolchain chapter plus three labs covering five programs, and all five `programs/0*/expected_output.txt` end in `SUCCESS!` with simulated WSE-3 cycle counts. Part IV is chapters 13–15.
- Evidence: `course/assets/course.js` CHAPTERS lines 4–10: `"02-the-wafer.html" … "Part I"`, `"07-host-io.html", "Host I/O and memcpy", "Part II · The machine"`.
- Concrete fix: Replace `the descriptors that replace loads and stores, and the systems that turn wafers into clusters.` with `the descriptors that replace loads and stores, the host link and memcpy, and the systems that turn wafers into clusters. (Chapter 2 first shows why a whole wafer can be one chip.)`

### A10 [minor] Rubin bandwidth is the revised spec; say so
- Location: Paragraph on line 81: "From H100 to Rubin, HBM bandwidth grows about 5.7× (3.35 → 19.2 TB/s)".
- Problem: 19.2 TB/s is NVIDIA's revised spec; the launch spec was 22 TB/s. Without a note, the reader may run into a contradiction with Chapter 14 or other sources. The tag is fine.
- Evidence: Report line 239: "288 GB HBM4, 19.2 TB/s (launch spec 22)". Report line 246: "NVIDIA's page now lists 19.2 TB/s HBM4 … down from the launch figures of 22".
- Concrete fix: Replace `(3.35 → 19.2 TB/s)` with `(3.35 → 19.2 TB/s, Rubin's revised spec; launch spec was 22)`.

## Not verifiable
- The "7,000×" vendor figure itself. It comes only from a search extract of the cerebras.net chip page (report line 19), and the underlying GPU baseline is unknown.
- "Aggregate register-file + shared-memory bandwidth … tens to hundreds of TB/s". This is a Derived claim in the notes with no worked calculation in the sources. A rough estimate (132 SMs × 4 sub-partitions × 32 lanes × ~12 B operand reads × ~1.98 GHz ≈ 400 TB/s RF; 132 × 128 B/clk × 1.98 GHz ≈ 33 TB/s smem) supports it, but the H100 clock and port widths were not in the sources.
- WSE-3 dense FP16 of 15.6 PF (analyst, sparsity-assumption based) and its ~1 GHz clock, used in the roofline. Cerebras has never published a dense figure (report line 40).
- "Tokens-per-second for a single user is set by memory bandwidth": a qualitative claim from blog sources (dev.to, Zartis). It is consistent with the derived arithmetic but not checked against a primary source.
- Rubin "50 PF NVFP4 inference": whether that is a dense or sparse figure is not stated in the sources. The chapter only says FLOPs grow "much faster", which holds either way.
