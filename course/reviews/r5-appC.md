# Round 5 fix log: appendix-c-measuring.html

Verdict: all six verified findings fixed. Playwright at 1100 px: zero console errors, 53 links (all local files and anchors resolve), no horizontal scroll. The page has no widgets touched by these edits.

| ID | Kind | Sev | Finding | Outcome |
|---|---|---|---|---|
| appC-r5-1 | error | med | Bank rule said peak needs opposite halves, contradicting the page's own 4 B PAD 1 example at peak | Fixed: f32 @fmacs (both chips) reaches 1/cycle at any non-same-bank start (4, 8, 12 B); opposite halves needed only for WSE-2 @fadds/@fmach; same bank halves the rate for @fmacs and those WSE-2 ops. Ch 6 link kept. Checked against 06-dsds.html #banks table. |
| appC-r5-2 | error | med | ncu said to lock to base clock by default; "none" described as boost clocks | Fixed: default locks clocks (boost in current versions, falling back to base); `none` leaves clocks unchanged. Re-checked against the NsightComputeCli page, 2026-11-05. |
| appC-r5-3 | error | low | Tenstorrent profiler/Tracy rows required `--enable-profiler` | Fixed: a normal `./build_metal.sh` build (profiling and Tracy on by default; `-DENABLE_TRACY=ON` noted). Added the DPRINT/watcher/profiler conflict, confirmed on the device profiler page (2026-11-05). |
| appC-r5-4 | unmarked | low | Intro said details came from search extracts, tagged only Vendor docs | Fixed: reworded to "checked against the linked vendor pages in 2026-11", tag "Vendor docs, checked 2026-11". All flags in the table were re-checked or come from pages the verifier fetched in full, so no Unverified tag added. |
| appC-r5-5 | gap | low | Four-step sync presented as the method of every App D benchmark | Fixed: added that bandwidth-test and row-col-broadcast use the mirror image (signal from PE (0,0), host subtracts px + py, their own src/sync/ module), tagged SDK 2.10.1 (run.py:453 / :277, sync/pe.csl). |
| appC-r5-6 | tag | low | 9.2 / 6.0 compute-hop costs tagged Measured | Fixed: now "Derived, Ch 12" (measured round-trip slope minus one router hop). |

Note: running `python3 tools/scan_tags.py` as a tag check rewrote the generated scan/bib sections of appendix-e-sources.html in place (the script ignores its argument). The change is limited to the generated marker regions and reflects current page state; it was not reverted, and the coordinator should be aware of it.
