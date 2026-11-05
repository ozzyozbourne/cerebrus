# R5 fix log: appendix-a-glossary.html

Verdict: all 7 findings fixed on the page. Playwright at 1100 px showed 0 console errors and no horizontal scroll (scrollWidth 1100). The glossary search works ("shelved" finds Rubin CPX). The new or changed links resolve: 06-dsds.html#banks, 18-comparison.html#limits, #g-bank-clash-operand-collision and 09-model-to-tokens.html#ceilings.

- A5-1 (error, med): the fp16 support cells now give the @fmach rates from note 30. WSE-2 is ~4/cycle when the sources start 8 B apart mod 16 B and ~2 otherwise, with a link to Ch 6. WSE-3 is ~4/cycle in every placement tested. The fp32 cells now mention the 2 cycles/element same-bank case and link to Bank clash. **Fixed**
- A5-2 (unmarked, med): in Tokens/s, the 3,300-6,600 range is now tagged Derived + "Unverified clock" (it was Analyst). The WSE entry's ~1.4 GHz clock now carries Analyst + Unverified. **Fixed**
- A5-3 (unmarked, med): Strong scaling now reads "would run about 7.5x faster ... projected from measured per-step costs [Derived] (P = 32 not run)". **Fixed**
- A5-4 (link, low): in Strong scaling, the See link now goes to 18-comparison.html#limits, "What actually limits a kernel on the wafer". **Fixed**
- A5-5 (error, low): Rubin CPX now reads "supply-chain reports describe it as shelved; NVIDIA has not confirmed a cancellation [Unverified]". **Fixed** on App A. I did not hand-edit App E, because this fixer may only edit its own page. App E's generated scan list does now show the new wording (see the note below).
- A5-6 (tag, low): the cb16 bias of 31 is now tagged "Unverified, assumed IEEE-like" in both the entry and the format-table cell. The computed range and step columns are unchanged. **Fixed**
- A5-7 (error, low): the WSE-2 int8 cell now reads "i8/u8 scalars and arrays, but no 8-bit DSD ops ("type 'i8' is not ABI-sized") [Measured, cslc 2.10.1]". **Fixed**

Note: I ran tools/scan_tags.py to count tags. It also rewrote the generated scan:begin/end and bib regions of appendix-e-sources.html in place, so they now reflect App A's new tags. The script did this as a side effect. I made no hand edits to App E.
