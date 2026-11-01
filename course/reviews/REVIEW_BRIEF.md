# Brief for course reviewers and fixers

## What this is
`/home/user/cerebrus/course/` is a 15-chapter static-HTML visual course on the Cerebras Wafer-Scale Engine (WSE-2/WSE-3), CSL programming with SDK 2.10.1, and a comparison with Tenstorrent and NVIDIA GPUs. Audience: a technically strong learner who is new to Cerebras. It must explain the architecture, how programs are written and run, and how things behave internally, with lots of visuals.

Files:
- Chapters: `course/01-memory-wall.html` … `course/15-comparison.html`, home page `course/index.html`.
- Chapters 10, 11, 12 are GENERATED from `course/src/10-*.html`, `src/11-*.html`, `src/12-*.html` by `python3 course/tools/build.py`. `{{code:...}}` and `{{out:...}}` placeholders pull in program sources and real outputs. Edit the src template, never the generated file.
- Shared chrome: `course/assets/course.css` (design tokens, light/dark, components such as .callout, .tag, .widget, figure) and `course/assets/course.js` (CHAPTERS list, top bar, pager; helpers `$`, `el(tag, attrs, parent)` for SVG, `cssVar`).
- Programs: `course/programs/0{1..5}-*/` each with layout.csl, pe_program.csl, run.py, commands.sh, expected_output.txt; `course/programs/run_all.sh`.
- Sources of truth:
  - Research report: `/home/user/cerebrus/reports/Cerebras architecture course research.md`.
  - Notes: `/home/user/cerebrus/research_notes/Cerebras architecture course research/{wse_hardware,csl_programming,tenstorrent,gpu_and_comparison}.md`.
  - Installed SDK: `/home/user/cerebras-sdk`. Tutorials and benchmarks with README.rst are in `/home/user/cerebras-sdk/extras/csl-extras-202604101435-6-d2f7d96e/examples/{tutorials,benchmarks}`. The CSL standard library is inside the SIF; read it with `singularity exec /home/user/cerebras-sdk/sdk-cbcore-2.10.1-sdk-202606181328-8faf87a26e.sif ls /cb/toolchains/cslang/rel-sdk-2.10.0/202604012315-1813-1394a6ea/csl-libs`, after `source /home/user/cerebras-sdk/env.sh`.
- Provenance tags used in the course: `<span class="tag vendor|indep|analyst|sdk|measured|derived">`. Every number should carry one.

## Known caveat
Most vendor documentation sites were unreachable during research, so many web facts came from search extracts. Prefer the SDK files for Cerebras programming facts. You may use WebSearch/WebFetch, but fetching may be blocked.

## Running things (only if your task needs it)
- `source /home/user/cerebras-sdk/env.sh` before cslc / cs_python.
- Never run the simulator inside `course/programs/` unless your task explicitly owns that program directory. For experiments, copy into your own dir under `/home/user/cerebras-sdk/tmp/<your-id>/`. cs_python fails under /tmp, so do not use /tmp. Clean up afterwards.
- Rendering pages: Playwright and Chromium are preinstalled, so `require('playwright')` works from any directory and `chromium.launch()` needs no options. Use `file:///home/user/cerebrus/course/<page>.html`. Save screenshots under `/home/user/cerebras-sdk/tmp/<your-id>/`.

## Rules for everyone
- Do NOT run git commands that change state (no commit, push, checkout, reset, stash). The coordinator commits.
- Reviewers: read-only. Write only your report file.
- Fixers: edit only the files your prompt assigns you.
