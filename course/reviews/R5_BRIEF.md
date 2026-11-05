# Round-5 verification audit brief

Course: /home/user/cerebrus/course (18 chapters + appendices A–E + index.html; order in assets/course.js). Audience: a
technically strong learner new to Cerebras. Round 4 just fixed every page (reviews/r4-*.md audits, r4-*-fixlog.md fixes,
r4-sweep-*.md). Round 5 VERIFIES the result. Read REVIEW_BRIEF.md (layout, provenance tags, SDK paths) and
CROSS_CHAPTER_NOTES.md — items 30–38 are canonical and override older items.

Labs 11–15 are generated from src/*.html (code pulled from programs/01..07): audit the generated page, fix in src/ and
run `python3 tools/build.py` from /home/user/cerebrus/course.

Three things to check on your page:
1. **Correct.** Every claim, number, code excerpt, quiz/exercise answer, widget formula and readout: right, consistent
   with the SDK (/home/user/cerebras-sdk), the programs and their expected_output.txt, CROSS_CHAPTER_NOTES 30–38, and the
   other pages. Round-4 edits are fresh and unreviewed — check them hardest (new numbers, new figures, new widgets).
2. **No gaps.** Each idea is introduced (or linked) before it is used; nothing a learner needs to connect A → B is
   missing; links and anchors land on the right thing.
3. **Unverifiable things are marked.** Every number carries a provenance tag (Vendor / Indep / Analyst / SDK 2.10.1 /
   Measured / Derived, plus Unverified where it applies). Anything that cannot be confirmed from a reachable source or a
   measurement in this course — hypotheses, estimates, press/search-extract figures, extrapolations not actually run —
   must carry `<span class="tag unv">Unverified</span>` (or be worded as a hypothesis/estimate). "Measured" only if the
   course actually ran it; "Derived" only if the arithmetic from tagged inputs is shown or checkable.

Rules: auditors and verifiers are READ-ONLY. Small simulator checks allowed in /home/user/cerebras-sdk/tmp/r5-<page>/
(`source /home/user/cerebras-sdk/env.sh`, never under /tmp, traces off, delete after). Web search allowed for
vendor/market facts. No git commands that change state. Report only real problems — style preferences are not findings.
