# Gap audit brief (round 3)

Goal: find GAPS in the finished course that we can still RESOLVE — not a style review. A gap is: something a learner
needs but the page does not give (missing explanation, missing worked example, missing measurement, missing answer,
missing visual for a hard idea), a claim left Unverified/Derived that could now be measured or sourced, an internal
inconsistency between pages, an exercise without an answer, a widget that cannot be used as intended, or a stale fact.

Course: /home/user/cerebrus/course — 18 chapters + appendices A–E (order in assets/course.js). Labs 11–15 are generated
from src/*.html (programs in programs/01..07). Read REVIEW_BRIEF.md (layout, tags, SDK paths, rules) and
CROSS_CHAPTER_NOTES.md (canonical shared facts, items 1–29). Earlier review/fix logs exist (chNN-*, r2-*, *fixlog.md)
— read the relevant fix logs' "open issues"/"partial"/"skipped" items: those are prime gap candidates. Old chNN-* files
use OLD chapter numbers (9→10, 10→11, 11→12, 12→13, 13→16, 14→17, 15→18).

Rules: READ-ONLY on course files. You may run small experiments to test whether a gap is resolvable (copy programs to
/home/user/cerebras-sdk/tmp/<your-id>/, traces OFF, < 1 GB, delete after; `source /home/user/cerebras-sdk/env.sh`;
never run cs_python under /tmp). Web search is allowed for stale/unverified facts. Don't re-report things already fixed.

For each gap give: ID, severity (high/med/low), page + section, what is missing and why it matters, evidence,
how to resolve (concrete), resolvable here? (yes: simulator / yes: web / yes: writing only / no: needs hardware or
unavailable source — say which), effort (S/M/L). Rank by value to the learner. Also list "not gaps" you checked and
rejected, in one line each. Write course/reviews/r3-gaps-<scope>.md (under ~1,200 words). Final reply: 6-line summary
with counts by severity and the top 3 gaps.
