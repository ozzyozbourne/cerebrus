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
  ["09-csl-toolchain.html", "CSL and the toolchain", "Part III · Programming"],
  ["10-lab-first-programs.html", "Lab 1: SAXPY and wavelet tasks", "Part III · Programming"],
  ["11-lab-neighbours.html", "Lab 2: reduce and broadcast", "Part III · Programming"],
  ["12-lab-stencil.html", "Lab 3: a heat stencil, measured", "Part III · Programming"],
  ["13-tenstorrent.html", "Tenstorrent, the middle path", "Part IV · Comparison"],
  ["14-gpu.html", "NVIDIA GPUs, the incumbent", "Part IV · Comparison"],
  ["15-comparison.html", "Head to head", "Part IV · Comparison"],
];

(function () {
  const here = location.pathname.split("/").pop() || "index.html";
  const idx = CHAPTERS.findIndex(c => c[0] === here);

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
    <div class="crumb">${idx >= 0 ? `Chapter ${idx + 1} of ${CHAPTERS.length} · ${CHAPTERS[idx][1]}` : "Course home"}</div>
    <button type="button" aria-label="Toggle dark mode">◐</button></div>`;
  bar.querySelector("button").onclick = toggleTheme;
  document.body.prepend(bar);

  // pager
  const main = document.querySelector("main");
  if (idx >= 0 && main) {
    const pager = document.createElement("nav");
    pager.className = "pager";
    const prev = idx > 0 ? CHAPTERS[idx - 1] : null;
    const next = idx < CHAPTERS.length - 1 ? CHAPTERS[idx + 1] : null;
    pager.innerHTML =
      (prev ? `<a class="prev" href="${prev[0]}"><small>← Chapter ${idx}</small>${prev[1]}</a>` : `<a class="prev" href="index.html"><small>←</small>Course home</a>`) +
      (next ? `<a class="next" href="${next[0]}"><small>Chapter ${idx + 2} →</small>${next[1]}</a>` : `<a class="next" href="index.html"><small>→</small>Course home</a>`);
    main.appendChild(pager);
  }
})();

// Small helpers used by chapter widgets
const $ = (s, r = document) => r.querySelector(s);
const svgNS = "http://www.w3.org/2000/svg";
function el(tag, attrs = {}, parent) {
  const e = document.createElementNS(svgNS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}
function cssVar(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }
