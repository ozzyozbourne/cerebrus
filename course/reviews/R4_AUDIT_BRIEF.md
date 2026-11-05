# Round-4 audit brief: correctness, explanation quality, connecting gaps

You audit ONE page of the course at /home/user/cerebrus/course (18 chapters + appendices A–E; reading order is the
CHAPTERS list in assets/course.js). Audience: a technically strong learner who is new to Cerebras. Read
REVIEW_BRIEF.md (layout, provenance tags, SDK paths, rules) and CROSS_CHAPTER_NOTES.md (canonical shared facts) first.
Labs 11–15 are generated from src/*.html and pull code from programs/01..07, so check the code there too.

Answer three questions about your page:

1. **Is it correct?** Check every technical claim, number, code snippet, quiz/exercise answer and widget formula against
   the SDK (installed at /home/user/cerebras-sdk: README.rst files, CSL libs inside the SIF, man pages), the programs
   and their expected_output.txt, the research report/notes, CROSS_CHAPTER_NOTES, and the other chapters (internal
   consistency). Flag claims that are wrong, stale, overstated, mis-tagged (e.g. Measured with no measurement), or that
   contradict another page. Quote the exact text and say what is right instead, with evidence.
2. **Does it explain well?** Is each idea introduced before it is used? Are hard ideas given an example, a visual, or
   a worked number? Are terms defined (or linked to the glossary) on first use? Point at the specific passages that
   are confusing, too terse, out of order or hand-wavy, and say how to fix them.
3. **What connecting pieces are missing?** This is the main focus. Find the concepts, steps or bridges a learner needs
   to get from idea A to idea B that the page (and the earlier pages it relies on) never supplies. Examples: a term
   used as if known but defined nowhere earlier; a result stated without the mechanism that links it to the previous
   chapter; a lab step that assumes a concept not yet taught; a jump from "what the hardware does" to "what the code
   says" with the mapping left out; a missing "why" behind a design choice. For each one, say which two ideas fail to
   connect and what explanation, example or figure would bridge them. Also check the page's links back and forward:
   does it rely on something a later chapter introduces?

Prior work: older reviews exist in reviews/ (chNN-*, r2-*, r3-gaps-*; old chNN-* files use OLD numbering: 9→10,
10→11, 11→12, 12→13, 13→16, 14→17, 15→18). Skim the ones for your page so you don't re-report items already fixed. If
an earlier report flagged something that is STILL unfixed, you may re-list it briefly, marked "still open (from <file>)".

Rules:
- READ-ONLY on course files. Write only your report file. No git commands that change state.
- Small simulator experiments are allowed if they settle a correctness question: copy into
  /home/user/cerebras-sdk/tmp/r4-<page-id>/, `source /home/user/cerebras-sdk/env.sh`, never run cs_python under /tmp,
  keep traces off, delete your dir afterwards. Many auditors run at once, so keep runs few and short.
- Web search is allowed for vendor/market facts (Ch 1, 2, 8, 9, 16–18, App E).

Report: write course/reviews/r4-<page-id>.md (page-id such as ch07 or appC), under ~1,500 words:
- Verdict line: Correct / Mostly correct / Has errors, plus Explanation quality: good / fair / poor.
- **Errors** (ID E1…, severity high/med/low, location by section id/heading, quoted text, what is right, evidence).
- **Explanation problems** (ID X1…, location, problem, concrete fix).
- **Connecting gaps** (ID G1…, severity, "A → B" ideas that fail to connect, what is missing, concrete bridge, effort S/M/L).
- **Checked and fine**: one line each for the main things you verified.
Final reply to the coordinator: ≤8 lines with the verdict, counts by type and severity, and the top 3 items.
