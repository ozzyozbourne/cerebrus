# ch04 · pedagogy review

Summary: The chapter is short and well paced, and it introduces the right objects in the right order: the router, the wavelet, the color, static rx/tx routes, the three route shapes, the checkerboard, switches and filters, and the color budget. The simulator and the color-budget strip are good visuals. The mental model still has gaps, though. The chapter never says that the fabric is lossless and back-pressured (Chapter 5 relies on this), or that colors share one physical link. The key "why" of the checkerboard is explained with a fuzzy "one rule" argument and mixed up with an unrelated collision claim. "The color picks the task" contradicts Chapter 5's WSE-3 queue model. The switch-register sentence will make learners think WSE-2 cannot switch. Objective 2 (write multicast routes) and objective 3 (why alternate) get no worked example or practice question that would show the learner they have understood.

## Findings

### P1 [major] The checkerboard "why" uses vague reasoning and mixes in the collision claim
Location: "Why programs alternate colors", first paragraph; the third Check-yourself question and its answer.
Problem: The text says a router's configuration for one color "is a single rule". It then says the PE would need two rules, and that an incoming wavelet "could not be told apart from an outgoing one". The real mechanism follows from the `@set_color_config` semantics the chapter has just taught: a color has one rx *set* and one tx *set*, and every wavelet arriving on any rx port is copied to every tx port. The text never draws that conclusion. Then, without a break, it cites "two same-colored wavelets meeting at a router in the same cycle is undefined behaviour". That is a separate hazard (two inputs merging on one color), not the reason for alternation. The quiz answer repeats the same blend of the two ideas.
Why it matters to the learner: Objective 3 is "explain why programs alternate colors". The learner leaves able to recite "ambiguity", but cannot work out for themselves what the router would actually do. Without that, they cannot design color assignments for new patterns.
Concrete fix: Replace the paragraph with:
> A color's route at one router is one rx set and one tx set, and the rule is "every wavelet arriving on any rx port goes to every tx port". Now take a middle PE in a reduction chain. It must deliver the partial sum from the west to its CE, and send its own result east. On one color the only way to say both is `rx = {WEST, RAMP}, tx = {RAMP, EAST}`. That route does the wrong thing twice. The partial sum from the west is copied east *as well as* down the ramp, so it skips this PE's addition. The PE's own result is copied back down its own ramp as well as east. The router has no notion of "this wavelet is mine, that one is passing through". Only the color separates traffic. The fix is to give the two roles different colors, alternating by column parity: even columns send on c0 and receive on c1, odd columns the reverse. Now each color has a simple one-in, one-out rule at every PE.

Then move the collision fact into a separate one-line note: "A separate hazard: if two wavelets of the same color arrive at one router in the same cycle from different rx ports, the behaviour is undefined <span class="tag indep">Indep</span>. That is another reason not to merge streams on one color." Change the quiz answer to: "Because a color's rule is 'any rx port → all tx ports'. With rx = {WEST, RAMP} and tx = {RAMP, EAST}, the incoming partial sum would also be forwarded east un-added, and the PE's own output would loop back to its own CE."

### P2 [major] Flow control, back-pressure and losslessness are never introduced
Location: The whole chapter. The only hint is the figure caption: "Each color has its own input buffers at each router, so traffic on one color cannot block another."
Problem: The chapter does not say what happens when a receiver is busy. Chapter 5's Check-yourself answer depends on it ("the fabric is lossless, so the sender eventually stalls. That is back-pressure"), and so does Chapter 5's `@block` discussion. The caption's claim that "one color cannot block another" is also left unexplained, and on its own it could suggest infinite buffering.
Why it matters to the learner: A strong learner coming from packet networks will assume wavelets can be dropped or retried. Without the lossless and back-pressure model, they cannot reason about stalls, hangs or deadlock in Labs 2 and 3.
Concrete fix: Add a short subsection after "Routes are static":
> **Nothing is dropped: back-pressure.** Each router keeps a small buffer per color on each input. If the next hop's buffer for that color is full (for example, because the receiving CE is busy and not draining its queue), the wavelet waits where it is. The stall then propagates upstream, hop by hop, until the sender's CE stops sending. The fabric is lossless: a slow receiver slows the sender, it never loses data <span class="tag indep">Indep (arXiv:2209.15040)</span>. Because buffers are per color, a stalled color does not stop wavelets of other colors from using the same link. Chapter 5 shows how tasks use this deliberately.

### P3 [major] The learner is never told that colors share one physical link
Location: The "Wavelet + router" figure and the "Colors are the scarcest resource" section.
Problem: The chapter says a link carries one 32-bit word per cycle, and that colors have separate buffers. It never connects the two: colors are *virtual channels* multiplexed over the same wires, so two colors crossing the same link split its 4 GB/s. The term "virtual channel" (used in the research notes) and any analogy are missing.
Why it matters to the learner: Without this, a learner may think more colors means more bandwidth, or that the halo exchange's four colors use four sets of wires. That leads to wrong performance estimates.
Concrete fix: Add after the first paragraph of "A mesh of five-port routers":
> A color is a *virtual channel*. Think of it as a lane label painted on the wavelet, not a separate wire. All colors crossing one link share that link's one word per cycle, and the router interleaves them. What each color gets is its own route rule and its own small buffer, so colors can be steered and stalled independently. (Analogy: one railway track carrying trains of different liveries, with points at every junction set in advance for each livery.)

### P4 [major] "The color picks the task" contradicts Chapter 5's WSE-3 model
Location: Wavelet figure text: "The color picks the route at every router AND the task at the receiver."
Problem: That is true on WSE-2 only. On WSE-3, a wavelet that reaches the RAMP enters an input queue bound to the color, and the data task is chosen by the queue (Chapter 5's figure and table). This chapter never mentions input or output queues, so the next chapter appears to contradict it.
Why it matters to the learner: This is the course's own "biggest portability hazard" (Chapter 5). Planting the WSE-2-only model first makes it harder to unlearn.
Concrete fix: Replace with: "The color picks the route at every router. At the destination it also decides what the CE does with the wavelet: on WSE-2 it selects the data task directly; on WSE-3 it lands in an input queue bound to that color, and the queue selects the task (Chapter 5)." Optionally add "→ input queue (WSE-3)" to the RAMP label in the router drawing.

### P5 [major] The switch sentence suggests WSE-2 has only one switch position
Location: "Switches": "A color can hold up to four route positions (WSE-3 has 4 switch registers per color; WSE-2 has 1)".
Problem: The SDK's `SWITCH_REGS_PER_COLOR` is 1 on WSE-2 and 4 on WSE-3. That counts configuration *registers*, not positions. The topic-06 switches tutorial uses positions 0–3 and targets both chips. A learner will read the parenthesis as "WSE-2 can't really switch".
Why it matters to the learner: It is a wrong conclusion about capability, and it is stated with an SDK tag, so the learner will trust it.
Concrete fix: Replace with: "A color can hold up to four route *positions*: the default route (position 0) plus positions 1–3 <span class="tag sdk">SDK 2.10.1</span>. Both WSE-2 and WSE-3 support this; the hardware just stores the switch state differently (one config register per color on WSE-2, four on WSE-3)." Also define the term before using it: "A *control wavelet* is a wavelet with its control bit set; instead of data, it carries a command for the routers it passes or a task ID for the receiver." Add the control bit to the wavelet diagram as a third small field.

### P6 [major] No worked example of the failure the checkerboard prevents, and the simulator cannot show it
Location: Fabric simulator patterns; the "Why programs alternate colors" section.
Problem: The simulator only offers correct patterns. The most instructive worked example for objective 3 is missing: a one-color chain, and what it does wrong.
Why it matters to the learner: Watching the broken version is what turns "alternate colors" from a rule into an understanding. It is also the obvious use for the simulator's existing "dropped" counter and route-table inspector.
Concrete fix: Add a pattern "Broken: row reduce on ONE color". Middle PEs get `rx {WEST, RAMP} → tx {RAMP, EAST}`, and the readout shows each PE receiving its own wavelet and un-added partials arriving east. Add a sentence under the widget: "Try 'Broken' first, then 'Lab 2: row reduce' and compare the recv counts." Also fix the hint text: it says "the ramp costs an extra tick", but the prose says ~2 cycles, and the code charges 2 ticks on the sending ramp and 0 on the receiving ramp. Make the hint match: "sending up the ramp costs 2 ticks; delivery down the ramp is shown immediately".

### P7 [major] The chapter never explains why routing is static
Location: "Routes are static".
Problem: The section states the fact ("configured once, at load time; the router does no address lookup at run time") but not the trade-off. The benefit: no packet headers, so all 32 bits are payload; deterministic one-cycle hops; tiny routers, which matters when there are 900k of them. The cost: every communication pattern must be known at compile time, and each one spends a color. The second half is the real reason "colors are the scarcest resource".
Why it matters to the learner: The learner is "technically strong" and will compare this with packet-switched NoCs (Tenstorrent, Chapter 13) and NVLink (Chapter 14). Without the why, the colour budget section reads as an arbitrary limitation, not a design consequence.
Concrete fix: Add a paragraph:
> Why static? A packet-switched network puts a destination address in every message, and every router decodes it. Here the wavelet carries only a 5-bit color, and the route is already in a table. That keeps all 32 bits for payload, keeps each hop at about one cycle, and keeps 900,000 routers tiny. The price is that every communication pattern must be planned at compile time, and every distinct pattern at a PE costs a color. Hold on to that: it is why colors become the scarcest resource at the end of this chapter.

### P8 [minor] Latency is taught, throughput and pipelining are not
Location: The second Check-yourself question ("How many cycles does it take a wavelet to cross 100 PEs?").
Problem: The answer covers a single wavelet. Real programs stream vectors. The learner is never shown that wavelets pipeline, so a 1,000-element vector over 100 hops costs about 1,000 + 100 cycles, not 100,000.
Why it matters to the learner: Getting this wrong makes nearest-neighbour versus distant communication look far worse, or far better, than it is. It also misses the link to the 4 GB/s per-link figure.
Concrete fix: Add a worked example after the router paragraph: "Sending a 1,000-element f32 vector 100 PEs east: the first wavelet arrives after ~2 (ramp) + 100 (hops) + ~2 (ramp) ≈ 104 cycles. The rest follow one per cycle behind it, so the whole vector lands after ≈ 1,100 cycles, about 1.1 µs at ~1 GHz <span class="tag derived">Derived</span>. Distance adds latency once; length costs one cycle per word." Change the quiz question to: "How long does a 1,000-wavelet stream take to cross 100 PEs, and what dominates?"

### P9 [minor] The objective-2 multicast skill is not practised; the quiz is thin
Location: Check yourself.
Problem: Two of the three questions test single-wavelet facts. Nothing asks the learner to write a multicast route, design a checkerboard, or count colors. Corner turns (for example `rx WEST → tx SOUTH`) are never shown, so a learner may think routes only go straight.
Why it matters to the learner: Objectives 2 and 3 are claimed but not checked.
Concrete fix: Add these questions:
1. "Write the routes for the bottom PE and for a middle PE of a column multicast on color 3, where the root is at the top." Answer: middle `rx {NORTH}, tx {RAMP, SOUTH}`; bottom `rx {NORTH}, tx {RAMP}`.
2. "A wavelet must go east along row 0, then turn south down column 5. What is the route at PE (5,0)?" Answer: `rx {WEST}, tx {SOUTH}` (or `tx {RAMP, SOUTH}` if (5,0) also needs it).
3. "A 2-D stencil exchanges with all four neighbours. Why does it need 8 colors, and how many are left for anything else?" Answer: 4 directions × 2 parities = 8; 24 − 4 (memcpy) − 8 = 12.
Also add "corner turn" as a fourth bullet under "Three shapes cover most programs", and rename the heading to "Four shapes".

### P10 [minor] Jargon is used without definition, plus forward references
Location: Throughout. The terms are memcpy, "context switch" (color 20), "command stream", "SdkLayout API", "filter banks", "control wavelet", and "Lab 2" / "Lab 3" before the labs exist.
Problem: memcpy is Chapter 7, SdkLayout is never explained, the "context switch" color is unexplained, and "filter banks" adds a hardware detail with no use to the learner.
Why it matters to the learner: Each undefined term is a small stall, and "context switch" will make a systems-minded learner think of an OS, which this machine explicitly lacks (Chapters 3 and 5).
Concrete fix: In the figcaption, write "memcpy, the SDK's host-I/O runtime (Chapter 7), reserves…". Give 20 a short gloss: "20 (runtime-internal switching)". Write "the SdkLayout API (a Python layout layer that allocates colors for you; Chapter 9)", or drop it. Replace "WSE-2 has two filter banks, WSE-3 one" with "WSE-3 has fewer filters than WSE-2", or cut it. On first mention write "Lab 2 (Chapter 11)" and "Lab 3 (Chapter 12)".

### P11 [minor] "Reserved" means two different things
Location: Wavelet figure ("5-bit color tag: 24 routable colors (0–23), 8 reserved") and the color-budget caption ("24 colors, 4 taken by the runtime").
Problem: A learner may conclude 24 − 8 = 16, or wonder whether the 8 and the 4 overlap.
Concrete fix: In the figure, write "5-bit tag → 32 IDs: 0–23 are routable colors; 24–31 are not routable (used for control and task IDs)." In the budget caption, write "Of the 24 routable colors, memcpy takes 4, leaving 20 for your program." Put a "20 usable" label on the budget strip.

### P12 [minor] The aggregate-bandwidth arithmetic has an unexplained ×2 and an unexplained chip switch
Location: The paragraph before Check yourself.
Problem: The formula "32 bits × 4 directions × 2 × ~850k PEs" gives no reason for the ×2. Each PE's 4 output ports already cover every link once per direction, so the ×2 is in effect counting each link from both ends. The lede says 900,000 PEs, but here the figure is ~850k (WSE-2) with no flag that the chip has changed. "~4 GB/s" per link carries no tag or derivation.
Why it matters to the learner: A careful learner will spot the double count and lose trust in the number, or carry it forward as "real" bandwidth.
Concrete fix: Replace the formula sentence with: "32 bits × 4 output ports × ~850k PEs (WSE-2) × ~1 GHz ≈ 1.1 × 10<sup>17</sup> bit/s; counting every port's input as well as its output doubles that to ≈ 2.2 × 10<sup>17</sup>, the vendor's 220 Pb/s <span class="tag derived">Derived</span>." Then: "Each link is 32 bits × ~1 GHz ≈ 4 GB/s per direction <span class="tag derived">Derived</span>, a fifth of the ~23 GB/s a PE gets from its own SRAM (Chapter 3). Moving a word to a neighbour is cheap, but not as cheap as keeping it local."

### P13 [minor] Missed links to the neighbouring chapters (color swap, filters, sparse index)
Location: "Filters" box.
Problem: Color swap (WSE-2) is in effect a hardware checkerboard: a wavelet flips c0 and c1 at each hop. The chapter treats it as trivia and does not connect it to the section above. Range filters act on the upper 16 bits, the same field Chapter 3 used for the sparse index, and that link is not made either.
Concrete fix: Add: "Color swap is the checkerboard done in hardware: one route rule, and the color flips c0 ↔ c1 at every hop. On WSE-3 you write the alternation yourself, as in Lab 2." In Filters, add: "These are the same upper 16 bits that Chapter 3 used to carry a sparse index."

### P14 [minor] "Checkerboard" names a 1-D alternation
Location: The section heading, the figure title, and the simulator pattern name.
Problem: Lab 2's chain and the figure alternate by column only, which is a stripe pattern. "Checkerboard" suggests 2-D parity (x+y), which this chapter never uses. The term matches Chapter 11 and the program comments, so keep it, but say what it means.
Concrete fix: The first time the word appears, write: "…alternate colors by column parity (the SDK and this course call this a 'checkerboard'; in 2-D it alternates by row as well)."
