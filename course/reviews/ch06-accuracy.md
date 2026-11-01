# ch06 · accuracy review

Summary: The chapter is accurate on the main points. The code excerpts match `course/programs/0{1,3,4}` exactly. The `@fmacs(dst, a, b, s)` = `a + b*s` and `@fadds(dst, a, b)` = `a + b` operand orders are confirmed by the SDK (CG benchmark comments, gemv-02 README, the `dsd_ops.csl` library). The WSE-3 single-fabric-input quote, the FIFO and pipeline-01 claims, `tensor_access` forms and `@map` usage all check out against the SDK. The real problems: the `@fmuls` row describes the op too narrowly (it is a general element-wise multiply; scalar scaling is just one operand choice). The "48 DSRs" figure is a WSE-3-only vendor number with no tag and no architecture qualifier. A few smaller claims are overclaimed or carry a weaker tag than they need. I re-ran program 03 on WSE-2 in a scratch copy and it passes, so the "runs unchanged on both chips" claim holds and can carry a Measured tag.

## Findings

### A1 [major] `@fmuls` described as vector × scalar only
- Location: "Builtins: the vector instruction set" table, row `@fmuls(dst, a, s)`.
- Problem: `@fmuls` is the f32 element-wise multiply of two sources: `dst[i] = a[i] × b[i]`, and either source may be a scalar. The signature `(dst, a, s)` and the meaning `a[i] × s` suggest the third operand must be a scalar. The SDK has a separate scale op, `@fscales`.
- Evidence:
  - CSL library `csl-libs/dsd_ops.csl` (in the SIF): `inline fn mul(T: type, dst: anytype, src0: anytype, src1: anytype, ...) { ... if (T == f32) { return @fmuls(dst, src0, src1, config); }`, next to a separate `inline fn scale(...)` that returns `@fscales(dst, src0, src1, config)`.
  - `examples/benchmarks/25-pt-stencil/task.csl:388`: `@fmuls(accDsd, accDsd, vpDsd);` multiplies by the velocity field DSD `vpDsd` (a `mem1d_dsd`, line 294), commented "vp[IDX3(i,j,k)]*lap".
  - Program 05 uses the scalar form: `@fmuls(y_dsd, x_dsd, s[0]);`.
- Concrete fix: replace the row with
  `<tr><td><code>@fmuls(dst, a, b)</code></td><td>dst[i] = a[i] × b[i] (b may be a DSD or a scalar)</td><td>05 (broadcast + scale, scalar b)</td></tr>`

### A2 [major] "48 data-structure registers" is WSE-3-only and untagged
- Location: paragraph after the SAXPY snippet: "The descriptor lives in one of the PE's 48 data-structure registers (DSRs)."
- Problem: The 48 DSR count is a vendor figure for the WSE-3 core only. The WSE-2 DSR count was not found. The sentence gives the number as universal and carries no provenance tag, which breaks the brief's rule that every number carries a tag.
- Evidence:
  - `research_notes/.../wse_hardware.md:83`: "**WSE-3 core (HC2024).** 16 general-purpose registers, 48 data structure registers ... (vendor) ... (via search extract)".
  - `wse_hardware.md:95`: "WSE-2 GPR/DSR counts ... were not found."
  - Report, Ch.4 paragraph: "WSE-2 GPR and DSR counts and the FP32 SIMD width were not found."
- Concrete fix: replace with `The descriptor lives in a data-structure register (DSR); a WSE-3 core has 48 of them <span class="tag vendor">Vendor, WSE-3</span>.`

### A3 [minor] "streaming operands through the SIMD lanes" and "no per-element instruction fetch" are untagged inferences
- Location: same paragraph: "The datapath walks it, generating addresses and streaming operands through the SIMD lanes, with no per-element instruction fetch or loop counter."
- Problem: The known SIMD widths are FP16/BF16 (8-wide) and INT8 (16-wide) on WSE-3. The FP32 SIMD width is unknown, and the notes guess it is 1-wide. So "SIMD lanes" for an f32 `@fmacs` is unsupported. The mechanism description is an inference and has no tag.
- Evidence: `wse_hardware.md:95`: "the exact FP32 SIMD width (probably 1-wide for fp32 FMAC, but no source) were not found." `csl_programming.md:253` (Inferences): "A DSD is a hardware loop descriptor held in a DSR register."
- Concrete fix: replace with `The datapath walks it, generating addresses and streaming operands through the arithmetic unit, with no per-element instruction fetch or loop counter <span class="tag derived">Derived from SDK and vendor descriptions</span>.`

### A4 [minor] Naming-pattern tag can be upgraded, and the mixed-precision `hs` suffix is missing
- Location: paragraph under the builtin table: "Naming pattern: f = float, trailing s = single (f32), h = half (f16); 16/32 = integer width <span class="tag derived">Derived from SDK sources; verify against the builtin reference</span>."
- Problem: The SIF's CSL library confirms the pattern directly, so the "verify" hedge is no longer needed. It also shows a mixed form, `hs` (f16 sources, f32 destination), which the sentence leaves out.
- Evidence: `csl-libs/dsd_ops.csl`: `if (Tsrc == @fp16()) { if (Tdst == @fp16()) { return @faddh(...) } if (Tdst == f32) { return @faddhs(...) } } if (Tsrc == f32 and Tdst == f32) { return @fadds(...) }`. The same structure holds for `@fmach`/`@fmachs`/`@fmacs`, `@fmulh`/`@fmuls`, `@fnegh`/`@fnegs`, and `@mov16` for i16/u16 vs `@mov32` for i32/u32.
- Concrete fix: replace the sentence with `Naming pattern: <code>f</code> = float, trailing <code>s</code> = single (f32), <code>h</code> = half (f16), <code>hs</code> = f16 inputs with an f32 result (e.g. <code>@fmachs</code>); <code>16/32</code> = integer width <span class="tag sdk">SDK 2.10.1, csl-libs/dsd_ops.csl</span>.`

### A5 [minor] "Any operand can be ... a scalar" overclaims
- Location: the same paragraph: "Any operand can be a memory DSD, a fabric DSD, a FIFO, or a scalar."
- Problem: The allowed operand types vary by builtin. A destination is not a plain scalar, and on WSE-3 at most one operand may be a fabric input (the chapter's own callout says so). The SDK points to a per-op operand-type table rather than a blanket rule.
- Evidence: `examples/tutorials/gemv-02-memory-dsds/README.rst:39-40`: "Other DSD operations and their associated operand types are described in :ref:`language-builtins-for-dsd-operations`." `sdklayout-03-ports-and-connections/add2vec.csl:22`: "WSE3 does not allow multiple fabric inputs per DSD operation."
- Concrete fix: replace with `Depending on the builtin, a source operand can be a memory DSD, a fabric DSD, a FIFO, or a scalar, and the destination a memory DSD, fabric DSD or FIFO; each op's allowed operand types are listed in the SDK's builtin reference <span class="tag sdk">SDK 2.10.1</span>.`

### A6 [minor] "Runs unchanged on both chips" can carry evidence
- Location: WSE-3 limit callout: "Lab 2's reduction only ever has one fabric input, so it runs unchanged on both chips."
- Problem: The claim is true but has no tag. The source contains `@is_arch("wse3")` branches for the fabout DSD and the queue init, so "unchanged" means "the same source". I compiled and ran a scratch copy of program 03 with `ARCH=wse2 bash commands.sh` and got `summed 8 vectors of length 32 across the row ... SUCCESS!`. The default run is WSE-3.
- Evidence: `programs/03-row-reduce/pe_program.csl:17-18`: `@get_dsd(fabout_dsd, if (@is_arch("wse3")) .{ .extent = M, .output_queue = oq } else .{ ..., .fabric_color = send_color })`, plus the WSE-2 run above.
- Concrete fix: replace with `Lab 2's reduction only ever has one fabric input, so the same source runs on both chips (only the fabout DSD fields differ, via <code>@is_arch</code>) <span class="tag measured">Measured, simulator, wse2 and wse3</span>.`

### A7 [minor] pipeline-01 warning is broader in the chapter than in the SDK
- Location: "Async operations..." paragraph: "the SDK warns that a blocking fabric op can stall because the CE must stay free to service the memcpy runtime".
- Problem: pipeline-01 describes one specific case: a blocking op reading a memcpy H2D stream on the same PE starves the CE, which then cannot process the H2D command. The chapter turns this into a general rule about any blocking fabric op. The general advice is fine, but the attribution should be scoped. topic-04 even uses a blocking `@mov16` send and only says async "would be better".
- Evidence: `tutorials/pipeline-01-basic/README.rst:33-39`: "The microthread is necessary because the CE (compute engine) must have some resources to run memcpy kernel. The kernel stalls if a blocking instruction @add16(outDsd, inDsd, 1) is used ... The CE has no resource to run the H2D command received by the router, so it stalls." `csl_programming.md` (topic-04): "The non-async operation works here because only two wavelet are sent. It would be better to use async operation".
- Concrete fix: replace with `Fabric operations should almost always be async: in pipeline-01, a blocking <code>@add16</code> that reads a memcpy input stream stalls the program, because the CE then has no resources left to run the memcpy kernel <span class="tag sdk">SDK 2.10.1, pipeline-01</span>.`

### A8 [minor] The "14" stall figure is an I/O-path capacity, not one hardware queue's depth
- Location: "FIFOs extend the tiny hardware queues": "Hardware queues hold only a handful of wavelets — one SDK example "stalls when size exceeds 14"."
- Problem: pipeline-01 attributes the stall to H2D/D2H serialization plus the capacity of "some internal queues to hold the data for I/O". pipeline-02 adds that the size "is architecture-dependent". So 14 is not the depth of a single input queue.
- Evidence: `pipeline-01-basic/README.rst:22-29`: "H2D and D2H are serialized ... The hardware has some internal queues to hold the data for I/O ... The program stalls when size exceeds 14." `pipeline-02-fifo/README.rst:3-5`: "The size of the queue is architecture-dependent."
- Concrete fix: replace with `Hardware queues hold only a handful of wavelets: in one SDK example, where a single PE loops memcpy input straight back out, the program "stalls when size exceeds 14", and the capacity is architecture-dependent <span class="tag sdk">SDK 2.10.1, pipeline-01/02</span>.` Keep the following `@allocate_fifo` sentence as is (it is correct: pipeline-02 says "The FIFO requires two microthreads and a scratch buffer").

### A9 [minor] Widget preset label "next column" shows column 3
- Location: DSD visualizer `<option value="3,6,8">next column via @increment_dsd_offset: |i|{6} -> A[3 + i*8]</option>`.
- Problem: In gemv-02 one `@increment_dsd_offset(A_dsd, 1, f32)` moves to the next column (offset +1). Base 3 is column 3, reached after three increments.
- Evidence: `csl_programming.md` (gemv-02): `A_dsd = @increment_dsd_offset(A_dsd, 1, f32); // next column`.
- Concrete fix: change the option text to `column 3 (after 3× @increment_dsd_offset(A, 1, f32)): |i|{6} -> A[3 + i*8]`.

### A10 [minor] Stencil comment mixes two meanings of `i`
- Location: Lab 3 snippet comment `// lap = u[i-1] + u[i+1]`.
- Problem: In the DSDs directly above, `i` is the induction variable, so `left` is `u[i]` and `right` is `u[i+2]`. The comment silently switches to a cell index `j = i+1`. A reader checking against the DSDs sees an off-by-one.
- Evidence: the same snippet, `left = ... u[i]`, `mid = ... u[i + 1]`, `right = ... u[i + 2]`.
- Concrete fix: change the three comments to `// lap[i] = u[i] + u[i+2]   (left + right neighbour of cell i+1)`, `// lap[i] += -2 * u[i+1]`, `// u[i+1] += alpha * lap[i]`.

## Not verifiable
- 48 DSRs on WSE-3: vendor figure via search extract (HC2024); the slide itself was not reachable. No WSE-2 figure exists.
- Whether `@fmacs`'s fourth operand may be a DSD rather than a scalar. Every SDK use passes a scalar, and the builtin reference is online-only.
- The exact queue depth behind pipeline-01's "14", and whether it differs between WSE-2 and WSE-3. The SDK only says it is "architecture-dependent".
- The claim that a DSD op needs "no per-element instruction fetch": consistent with the vendor and SDK descriptions, but there is no public ISA document.
