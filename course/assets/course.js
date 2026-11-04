// Shared course chrome: chapter list, top bar, prev/next pager, theme toggle.
const CHAPTERS = [
  ["01-memory-wall.html", "The memory wall", "Part I · Why wafer-scale"],
  ["02-the-wafer.html", "One chip, one wafer", "Part I · Why wafer-scale"],
  ["03-processing-element.html", "Inside a processing element", "Part II · The machine"],
  ["04-fabric.html", "The fabric: wavelets and colors", "Part II · The machine"],
  ["05-tasks.html", "Tasks: computing on arrival", "Part II · The machine"],
  ["06-dsds.html", "DSDs: loops as hardware", "Part II · The machine"],
  ["07-host-io.html", "Host I/O and memcpy", "Part II · The machine"],
  ["08-systems.html", "Systems: CS-3, MemoryX, SwarmX, CS-4", "Part II · The machine"],
  ["09-model-to-tokens.html", "From model to tokens", "Part II · The machine"],
  ["10-csl-toolchain.html", "CSL and the toolchain", "Part III · Programming"],
  ["11-lab-first-programs.html", "Lab 1: SAXPY and wavelet tasks", "Part III · Programming"],
  ["12-lab-neighbours.html", "Lab 2: reduce and broadcast", "Part III · Programming"],
  ["13-lab-stencil.html", "Lab 3: a heat stencil, measured", "Part III · Programming"],
  ["14-lab-gemm.html", "Lab 4: 2-D GEMM with SUMMA", "Part III · Programming"],
  ["15-lab-cg.html", "Lab 5: a conjugate-gradient solver", "Part III · Programming"],
  ["16-tenstorrent.html", "Tenstorrent, the middle path", "Part IV · Comparison"],
  ["17-gpu.html", "NVIDIA GPUs, the incumbent", "Part IV · Comparison"],
  ["18-comparison.html", "Head to head", "Part IV · Comparison"],
];
const APPENDICES = [
  ["appendix-a-glossary.html", "Glossary and number formats", "A"],
  ["appendix-b-cuda-to-csl.html", "CUDA to CSL, budgets and constants", "B"],
  ["appendix-c-measuring.html", "Measuring and observing", "C"],
  ["appendix-d-sdk-index.html", "SDK example index", "D"],
  ["appendix-e-sources.html", "Sources and unverified figures", "E"],
];

(function () {
  const here = location.pathname.split("/").pop() || "index.html";
  const SEQ = CHAPTERS.map((c, i) => ({ href: c[0], title: c[1], label: `Chapter ${i + 1}` }))
    .concat(APPENDICES.map(a => ({ href: a[0], title: a[1], label: `Appendix ${a[2]}` })));
  const idx = SEQ.findIndex(c => c.href === here);

  // theme
  try { const t = localStorage.getItem("wsc-theme"); if (t) document.documentElement.dataset.theme = t; } catch (e) {}
  function toggleTheme() {
    const cur = document.documentElement.dataset.theme ||
      (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("wsc-theme", next); } catch (e) {}
  }

  // top bar
  const bar = document.createElement("header");
  bar.className = "topbar";
  bar.innerHTML = `<div class="inner"><a class="brand" href="index.html">Wafer-Scale <span>Computing</span></a>
    <div class="crumb">${idx >= 0 ? (idx < CHAPTERS.length ? `Chapter ${idx + 1} of ${CHAPTERS.length}` : SEQ[idx].label) + ` · ${SEQ[idx].title}` : "Course home"}</div>
    <a class="glossary-link" href="appendix-a-glossary.html" title="Glossary">Glossary</a><button type="button" aria-label="Toggle dark mode">◐</button></div>`;
  bar.querySelector("button").onclick = toggleTheme;
  document.body.prepend(bar);

  // pager
  const main = document.querySelector("main");
  if (idx >= 0 && main) {
    const pager = document.createElement("nav");
    pager.className = "pager";
    const prev = idx > 0 ? SEQ[idx - 1] : null;
    const next = idx < SEQ.length - 1 ? SEQ[idx + 1] : null;
    pager.innerHTML =
      (prev ? `<a class="prev" href="${prev.href}"><small>← ${prev.label}</small>${prev.title}</a>` : `<a class="prev" href="index.html"><small>←</small>Course home</a>`) +
      (next ? `<a class="next" href="${next.href}"><small>${next.label} →</small>${next.title}</a>` : `<a class="next" href="index.html"><small>→</small>Course home</a>`);
    main.appendChild(pager);
  }
})();

// Small helpers used by chapter widgets
const $ = (s, r = document) => r.querySelector(s);
const svgNS = "http://www.w3.org/2000/svg";
// Colours passed as cssVar("--x") become live CSS variables (set via inline style),
// so drawings follow the light/dark theme toggle without being redrawn.
const STYLE_ATTRS = new Set(["fill", "stroke", "stop-color", "color"]);
function el(tag, attrs = {}, parent) {
  const e = document.createElementNS(svgNS, tag);
  for (const k in attrs) {
    const v = attrs[k];
    if (STYLE_ATTRS.has(k) && typeof v === "string" && v.startsWith("var(")) e.style.setProperty(k, v);
    else e.setAttribute(k, v);
  }
  if (parent) parent.appendChild(e);
  return e;
}
function cssVar(name) { return `var(${name})`; }
function cssValue(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }
