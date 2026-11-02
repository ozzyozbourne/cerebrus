#!/usr/bin/env python3
"""Scan the course for provenance tags and rebuild the generated parts of Appendix E.

Usage (from anywhere):
    python3 course/tools/scan_tags.py            # rewrite appendix-e-sources.html in place
    python3 course/tools/scan_tags.py --check    # print a summary only, change nothing

What it does
  1. Reads the chapter order from assets/course.js (CHAPTERS, then APPENDICES). index.html is
     skipped: its tags are the legend, not claims.
  2. Finds every static <span class="tag CLASS">label</span> in each page (tags drawn by widget
     JavaScript at run time are not counted) and records the class, the label and the claim text:
     the sentence (or table row) that the tag follows.
  3. Flags every tag of class "unv", and every tag whose label says the figure came "via"
     secondary reporting (press, forum, search extract, reprint, secondary).
  4. Collects the bibliography: every markdown link in /home/user/cerebrus/reports and
     research_notes, every http(s) link in the course pages, and the EXTRA list below (sources
     verified for the 2026 NVIDIA/Groq update). URLs are de-duplicated (scheme, www., trailing
     slash, fragment and arXiv abs/pdf/html variants are folded together) and grouped by topic.
  5. Writes the results between the <!-- scan:begin --> / <!-- scan:end --> and
     <!-- bib:begin --> / <!-- bib:end --> markers in appendix-e-sources.html.

Appendix E itself is not scanned (it would count its own legend).
"""
import datetime
import html
import json
import os
import re
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
COURSE = os.path.dirname(HERE)
ROOT = os.path.dirname(COURSE)
APPX = os.path.join(COURSE, "appendix-e-sources.html")
SELF = "appendix-e-sources.html"

TAG_CLASSES = ["vendor", "indep", "analyst", "sdk", "measured", "derived", "unv"]
VIA_RE = re.compile(r"secondary|via (?:press|forum|search|reprint|review)", re.I)

# ---------------------------------------------------------------- chapter list
def chapter_list():
    js = open(os.path.join(COURSE, "assets", "course.js"), encoding="utf-8").read()
    out = []
    m = re.search(r"const CHAPTERS = \[(.*?)\];", js, re.S)
    for i, (href, title) in enumerate(re.findall(r'\["([^"]+)",\s*"([^"]+)"', m.group(1))):
        out.append((href, f"Ch {i + 1}", title))
    m = re.search(r"const APPENDICES = \[(.*?)\];", js, re.S)
    for href, title, letter in re.findall(r'\["([^"]+)",\s*"([^"]+)",\s*"([^"]+)"\]', m.group(1)):
        out.append((href, f"App {letter}", title))
    return out

# ---------------------------------------------------------------- tag scanner
BLOCKS = {"p", "li", "td", "th", "figcaption", "dd", "dt", "summary", "h1", "h2", "h3", "h4", "div", "caption", "blockquote"}
SKIP = {"script", "style", "svg", "title", "desc"}

class TagScanner(HTMLParser):
    """Walks a page; keeps a stack of block texts so each tag can see the text before it."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # [tagname, text-so-far]
        self.skip = 0
        self.in_tag = None       # [class, label-parts]
        self.found = []
        self.row = None          # first cell text of the current table row
        self.cell_idx = 0
        self.header = []         # header row of the current table
        self.is_header_row = False
        self.row_cells = []
        self.section = ""
        self.in_h2 = False

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
            return
        if self.skip:
            return
        a = dict(attrs)
        if tag == "table":
            self.header = []
        if tag == "tr":
            self.row_cells = []
            self.is_header_row = False
        if tag == "th":
            self.is_header_row = True
        if tag == "h2":
            self.in_h2 = True
            self.section = ""
        if tag == "span" and "tag" in (a.get("class") or "").split():
            cls = [c for c in a["class"].split() if c != "tag"]
            self.in_tag = [cls[0] if cls else "", []]
            return
        if tag in BLOCKS:
            self.stack.append([tag, ""])
        if tag == "br":
            self._add(" ")

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag == "span" and self.in_tag is not None:
            cls, parts = self.in_tag
            self.in_tag = None
            label = " ".join("".join(parts).split())
            self._record(cls, label)
            self._add(" [" + label + "] ")
            return
        if tag == "h2":
            self.in_h2 = False
        if tag in BLOCKS:
            # pop to the matching block
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    txt = self.stack[i][1]
                    del self.stack[i:]
                    if tag in ("td", "th"):
                        self.row_cells.append(" ".join(txt.split()))
                    if self.stack:
                        self.stack[-1][1] += " " + txt + " "
                    break
        if tag == "tr":
            if self.is_header_row:
                self.header = self.row_cells[:]
            self.row_cells = []

    def handle_data(self, data):
        if self.skip:
            return
        if self.in_tag is not None:
            self.in_tag[1].append(data)
            return
        if self.in_h2:
            self.section += data
        self._add(data)

    def _add(self, s):
        if self.stack:
            self.stack[-1][1] += s

    def _record(self, cls, label):
        block = self.stack[-1] if self.stack else ["", ""]
        text = " ".join(block[1].split())
        # claim = the sentence the tag follows: text after the previous tag/sentence end
        def sentence_start(t, end):
            # last "] " (end of an earlier tag) or full stop before `end`, ignoring "et al. ", "e.g. ", "vs. ", "Ch. "
            ends = [m.start() for m in re.finditer(r"(?<!\bal)(?<!e\.g)(?<!i\.e)(?<!\bvs)(?<!\bCh)(?<!\bNo)\. ", t[:end])]
            return max(t.rfind("] ", 0, end), ends[-1] if ends else -1)
        cut = sentence_start(text, len(text))
        claim = text[cut + 2:] if cut >= 0 else text
        if len(claim) > 220 and "; " in claim:    # long sentence: keep the clause the tag follows
            claim = claim[claim.rfind("; ") + 2:]
        if len(claim) < 60 and cut > 0:           # too short: include the sentence before it
            cut2 = sentence_start(text, cut)
            claim = text[cut2 + 2:] if cut2 >= 0 else text
        claim = claim.strip(" ,;:(")
        if block[0] in ("td", "th"):
            ctx = []
            if self.row_cells:
                ctx.append(self.row_cells[0])
            col = len(self.row_cells)
            if self.header and col < len(self.header) and self.header[col]:
                ctx.append(self.header[col])
            if ctx:
                claim = " · ".join(c for c in ctx if c) + ": " + claim
        self.found.append({"cls": cls, "label": label, "claim": claim[-400:],
                           "section": " ".join(self.section.split())})

def scan_pages():
    pages = []
    for href, short, title in chapter_list():
        if href == SELF:
            continue
        path = os.path.join(COURSE, href)
        if not os.path.exists(path):
            pages.append({"href": href, "short": short, "title": title, "missing": True, "tags": []})
            continue
        p = TagScanner()
        p.feed(open(path, encoding="utf-8").read())
        pages.append({"href": href, "short": short, "title": title, "missing": False, "tags": p.found})
    return pages

# ---------------------------------------------------------------- why / what would settle it
def reason(t):
    lab = t["label"].lower()
    if t["cls"] == "unv":
        if "background" in lab:
            why = "Background fact repeated from tutorials or secondary write-ups; not checked against a primary document in this course."
        elif "press" in lab:
            why = "Only press reports; the companies did not confirm."
        elif "not re-checked" in lab or "not verified" in lab:
            why = "Reviewer could not reach the primary source."
        else:
            why = "No reachable primary source confirmed it."
    else:
        why = "The vendor number reached the course through " + (
            "press coverage" if "press" in lab else "a forum post" if "forum" in lab else
            "a search-engine extract" if "search" in lab else "a reprint" if "reprint" in lab else
            "secondary reporting") + ", not the vendor's own page."
    return why

SETTLE_RULES = [
    (r"groq|lpx|lpu|lp30|attention-ffn|cpx", "NVIDIA's LPX product page and GTC 2026 keynote, or an NVIDIA/Groq press release; an independent decode benchmark for the claims."),
    (r"tensix|blackhole|wormhole|grayskull|galaxy|p150|p100|tenstorrent|tt-", "tt-isa-documentation, docs.tenstorrent.com spec pages, or a tt-metal tech report."),
    (r"h100|b200|gb200|rubin|nvlink|nvl72|hopper|blackwell|sm\b|warp|tensor core|tma|tmem|cuda|ptx|hbm|nvswitch|megatron|smem|shared memory", "NVIDIA's own datasheet, architecture whitepaper or docs.nvidia.com (CUDA/PTX guides); for software patterns the cited paper."),
    (r"tpu|ironwood|sambanova|sn40l|amd|mi355|instinct", "The vendor's product page or documentation (cloud.google.com/tpu, sambanova.ai, amd.com)."),
    (r"cs-3|cs-4|cs-6|wse|cerebras|wafer|memoryx|swarmx|kimi|condor", "A Cerebras primary document (Hot Chips deck, sdk.cerebras.ai, press release) or, for programming facts, a simulator measurement."),
    (r"mlperf|tdp|price|\$", "The benchmark organisation's results page or the vendor's price list."),
]
def settle(t):
    s = (t["claim"] + " " + t["label"] + " " + t.get("section", "")).lower()
    for pat, txt in SETTLE_RULES:
        if re.search(pat, s):
            return txt
    return "The primary document named in the chapter, or a measurement."

# ---------------------------------------------------------------- bibliography
EXTRA = [  # sources verified (via web search) for the 2026 NVIDIA/Groq update in Ch 17 and Ch 18
    ("Groq newsroom: Groq and Nvidia enter non-exclusive inference technology licensing agreement (24 Dec 2025)", "https://groq.com/newsroom/groq-and-nvidia-enter-non-exclusive-inference-technology-licensing-agreement-to-accelerate-ai-inference-at-global-scale", "nvidia-groq"),
    ("Groq blog: Groq among the first to bring NVIDIA Groq 3 LPX and Vera Rubin NVL72 to market", "https://groq.com/blog/groq-among-the-first-to-bring-nvidia-groq-3-lpx-and-vera-rubin-nvl72-to-market", "nvidia-groq"),
    ("NVIDIA Groq 3 LPX product page (localised editions reached via search)", "https://www.nvidia.com/ja-jp/data-center/lpx/", "nvidia-groq"),
    ("Tom's Hardware: Nvidia's $20 billion Groq deal produces its first chip", "https://www.tomshardware.com/tech-industry/semiconductors/nvidias-20-billion-groq-deal-produces-its-first-chip", "nvidia-groq"),
    ("HPCwire: Nvidia boasts 7 chips in production for Vera Rubin platform, including Groq 3 LPU (16 Mar 2026)", "https://www.hpcwire.com/2026/03/16/nvidia-boasts-7-chips-in-production-for-vera-rubin-platform-including-groq-3-lpu/", "nvidia-groq"),
    ("StorageReview: NVIDIA Groq 3 LPX, everything we know", "https://www.storagereview.com/news/nvidia-groq-3-lpx-everything-we-know", "nvidia-groq"),
    ("Hashrate Index: NVIDIA Vera Rubin reference architecture (AFD, CPX shelved)", "https://hashrateindex.com/blog/nvidia-vera-rubin-reference-architecture/", "nvidia-groq"),
    ("Counterpoint Research: GTC 2026, NVIDIA's LPU strategy", "https://www.counterpointresearch.com/en/insights/GTC-2026-NVIDIA%E2%80%99s-LPU-Strategy-and-the-Rise-of-Agentic-AI-Infrastructure", "nvidia-groq"),
    ("ABI Research: Inference is disaggregating (32 trays × 8 LP30)", "https://www.abiresearch.com/market-research/insight/7787784-inference-is-disaggregating-to-balance-per", "nvidia-groq"),
    ("Tom's Hardware (via 3dtested): Nvidia removes Rubin CPX accelerators from its roadmap", "https://www.3dtested.com/pc-components/gpus/nvidia-removes-rubin-cpx-accelerators-from-its-roadmap-groq-3-lpus-take-center-stage-as-cpx-is-removed", "nvidia-groq"),
    ("The Register: Groq–NVIDIA analysis (31 Dec 2025)", "https://www.theregister.com/2025/12/31/groq_nvidia_analysis", "nvidia-groq"),
    ("Computer Weekly: NVIDIA and Groq", "https://www.computerweekly.com/news/366640398", "nvidia-groq"),
    ("Constellation Research: Nvidia's Groq deal, acquisition, acquihire or licensing deal?", "https://www.constellationr.com/insights/news/nvidias-groq-deal-acquisition-acquihire-or-creative-licensing-deal", "nvidia-groq"),
    ("Google Cloud: TPU7x (Ironwood) documentation", "https://docs.cloud.google.com/tpu/docs/tpu7x", "other"),
    ("The Register: Google's Ironwood TPUs (6 Nov 2025)", "https://www.theregister.com/2025/11/06/googles_ironwood_tpus_ai/", "other"),
    ("Prabhakar et al., SambaNova SN40L: scaling the AI memory wall (arXiv 2405.07518)", "https://arxiv.org/abs/2405.07518", "other"),
    ("SambaNova at Hot Chips 2024 (Prabhakar)", "https://www.hc2024.hotchips.org/assets/program/conference/day1/48_HC2024.Sambanova.Prabhakar.final-withoutvideo.pdf", "other"),
    ("AMD Instinct MI355X platform page", "https://www.amd.com/en/products/accelerators/instinct/mi350/mi355x/platform.html", "other"),
    ("Tom's Hardware: AMD announces MI350X and MI355X", "https://www.tomshardware.com/pc-components/gpus/amd-announces-mi350x-and-mi355x-ai-gpus-claims-up-to-4x-generational-gain-up-to-35x-faster-inference-performance", "other"),
]

TOPICS = [
    ("nvidia-groq", "NVIDIA, Groq and the 2026 SRAM decode tier"),
    ("cerebras-hw", "Cerebras hardware and systems"),
    ("cerebras-inf", "Cerebras inference, benchmarks and business"),
    ("sdk", "Cerebras SDK and CSL programming"),
    ("papers", "Academic papers on wafer-scale computing"),
    ("tt", "Tenstorrent"),
    ("nvidia", "NVIDIA GPUs"),
    ("roofline", "Roofline, GPU programming and inference economics (tutorials and analysis)"),
    ("other", "Other accelerators (TPU, SambaNova, AMD)"),
    ("local", "Installed SDK 2.10.1 files cited by the research notes"),
]
TOPIC_OVERRIDES = {  # URL substring -> topic, for links whose title and URL do not say enough
    "businesswire.com/news/home/20241118595546": "cerebras-inf",
    "blog.gpu.net/posts/2026/june/new-blog-june13": "tt",
    "technews.tw/2026/07/10/qualcomm": "tt",
    "hyper.ai/en/stories/3422d6a72152beb34a564461208438ff": "nvidia",
    "hashrateindex.com/blog/nvidia-vera-rubin-nvl72": "nvidia",
    "inferencex.semianalysis.com": "nvidia",
    "modal.com/blog/nvidia-b200": "nvidia",
    "the-roofline-model-for-llm-inference": "roofline",
}
TOPIC_RULES = [  # first match wins; tested against "title url" lowercased
    ("local", r"^file://|^\s*file://"),
    ("nvidia-groq", r"groq|lpx|\blpu\b"),
    ("other", r"tpu|ironwood|sambanova|sn40l|\bamd\b|mi355"),
    ("tt", r"tenstorrent|tt-metal|tt-isa|metalium|ttnn|tt-forge|tt-buda|blackhole|wormhole|grayskull|tensix|quietbox|keller|flopper|whatpsu|videocardz"),
    ("sdk", r"sdk\.cerebras|sdk technical|sdk docs|sdk builtins|sdk release|training-api\.cerebras"),
    ("papers", r"arxiv|uspto|patent|llnl|ornl|nextplatform.*molecular|micro54|computerhistory"),
    ("cerebras-inf", r"artificialanalysis|inference|tokens|gpt-5|kimi|pricing|price|ipo|raised|benchlm|thedataexchange|bear-case|syncflo|venturebeat|hpcwire.*cerebras|morphllm|aiweekly|x\.com"),
    ("cerebras-hw", r"cerebras|wafer|wse|hotchips|hc34|hc31|hc2024|servethehome|semiwiki|gpusmith|hyper-accel|clarigital|damnang|insidedeeptech|mirrorfrog|introl|semianalysis.*cerebras|futurum.*cerebras|ucdavis|slideshare|kowatek"),
    ("nvidia", r"nvidia|h100|b200|gb200|rubin|hopper|blackwell|nvl72|chipsandcheese|cudo|spheron.*gb200|runpod|modal|jarvislabs|cyfuture|nextpcb|inferencex|datacenterdynamics.*nvidia|tech-insider|pasqualepillitteri|wccftech.*rubin|hothardware.*nvidia|theregister.*rubin"),
    ("roofline", r"."),
]

def norm_url(u):
    u = u.strip().rstrip(".,;")
    u = re.sub(r"#.*$", "", u)
    m = re.search(r"arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d{4,5})", u)
    if m:
        return "arxiv:" + m.group(1)
    k = re.sub(r"^https?://", "", u)
    k = re.sub(r"^www\.", "", k).rstrip("/")
    return k.lower()

def topic_of(title, url):
    for k, t in TOPIC_OVERRIDES.items():
        if k in url:
            return t
    s = (title + " " + url).lower()
    for t, pat in TOPIC_RULES:
        if re.search(pat, s if t != "local" else url):
            return t
    return "roofline"

LINK_RE = re.compile(r"\[([^\]\n]{2,160})\]\(((?:https?|file)://[^)\s]+)\)")

def collect_bib():
    entries = {}
    def add(title, url, src, topic=None):
        url = url.strip().rstrip(".,;")
        if url.count("(") > url.count(")"):      # markdown link regex stops at the first ")"
            url += ")"
        if url.startswith("file://"):
            path = url[len("file://"):]
            path = path.replace("/home/user/cerebras-sdk/extras/csl-extras-202604101435-6-d2f7d96e/examples/", "EX/")
            key = "file:" + path
            title = path
        else:
            key = norm_url(url)
        e = entries.get(key)
        if e is None:
            e = entries[key] = {"title": title, "url": url, "srcs": set(), "topic": topic or topic_of(title, url)}
        e["srcs"].add(src)
        # keep the most descriptive title (longest, but not a bare domain)
        if len(title) > len(e["title"]) and not title.startswith("http"):
            e["title"] = title
        if topic:
            e["topic"] = topic
    srcdirs = [(os.path.join(ROOT, "reports"), "report"), (os.path.join(ROOT, "research_notes"), "notes")]
    for d, tag in srcdirs:
        for dp, _, files in os.walk(d):
            for f in sorted(files):
                if not f.endswith(".md"):
                    continue
                txt = open(os.path.join(dp, f), encoding="utf-8").read()
                name = "report" if tag == "report" else os.path.splitext(f)[0]
                for title, url in LINK_RE.findall(txt):
                    add(title.strip(), url, name)
    for href, short, title in chapter_list():
        path = os.path.join(COURSE, href)
        if href == SELF or not os.path.exists(path):
            continue
        for url, text in re.findall(r'<a [^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', open(path, encoding="utf-8").read(), re.S):
            add(re.sub("<[^>]+>", "", text).strip() or url, url, short)
    for title, url, topic in EXTRA:
        add(title, url, "Ch 17/18 update", topic)
    return entries

# ---------------------------------------------------------------- render
def esc(s):
    return html.escape(s, quote=True)

def render_scan(pages, today):
    flagged = []
    counts = []
    for p in pages:
        c = {k: 0 for k in TAG_CLASSES}
        c["via"] = 0
        for t in p["tags"]:
            c[t["cls"]] = c.get(t["cls"], 0) + 1
            via = t["cls"] != "unv" and bool(VIA_RE.search(t["label"]))
            if via:
                c["via"] += 1
            if t["cls"] == "unv" or via:
                flagged.append({"page": p["href"], "short": p["short"], "cls": t["cls"], "label": t["label"],
                                "claim": t["claim"], "section": t["section"], "why": reason(t), "settle": settle(t)})
        counts.append({"href": p["href"], "short": p["short"], "title": p["title"], "missing": p["missing"], "c": c})
    total = sum(len(p["tags"]) for p in pages)
    n_unv = sum(1 for f in flagged if f["cls"] == "unv")
    data = {"generated": today, "classes": TAG_CLASSES, "pages": counts, "flagged": flagged}
    out = []
    out.append(f'<p class="small" id="scan-stamp">Generated on <b>{today}</b> by <code>python3 course/tools/scan_tags.py</code> from '
               f'{sum(1 for p in pages if not p["missing"])} pages: <b>{total}</b> static provenance tags, of which <b>{n_unv}</b> are '
               f'Unverified and <b>{len(flagged) - n_unv}</b> are vendor or other figures reached via secondary reporting. '
               f'Pages listed in the course but not yet written: {", ".join(p["short"] for p in pages if p["missing"]) or "none"}.</p>')
    out.append('<script type="application/json" id="scan-data">' + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + "</script>")
    out.append('<div class="table-wrap"><table class="mini flag-table" id="flag-static"><thead><tr><th>Page</th><th>Claim (text before the tag)</th><th>Tag</th><th>Why it is not verified</th><th>What would settle it</th></tr></thead><tbody>')
    for f in flagged:
        cls = "unv" if f["cls"] == "unv" else f["cls"]
        out.append(f'<tr data-page="{esc(f["page"])}" data-cls="{esc(f["cls"])}"><td><a href="{esc(f["page"])}">{esc(f["short"])}</a></td>'
                   f'<td>{esc(f["claim"])}</td><td><span class="tag {cls}">{esc(f["label"])}</span></td>'
                   f'<td>{esc(f["why"])}</td><td>{esc(f["settle"])}</td></tr>')
    out.append("</tbody></table></div>")
    return "\n".join(out), data

def render_bib(entries):
    out = []
    by = {}
    for k, e in entries.items():
        by.setdefault(e["topic"], []).append(e)
    n = 0
    for tid, tname in TOPICS:
        items = sorted(by.get(tid, []), key=lambda e: e["title"].lower())
        if not items:
            continue
        out.append(f'<h3 id="bib-{tid}">{esc(tname)} <span class="small">({len(items)})</span></h3>')
        out.append('<ul class="bib">')
        for e in items:
            n += 1
            srcs = ", ".join(sorted(e["srcs"]))
            if tid == "local":
                out.append(f'<li><code>{esc(e["title"])}</code> <span class="src">{esc(srcs)}</span></li>')
            else:
                out.append(f'<li><a href="{esc(e["url"])}" rel="noopener">{esc(e["title"])}</a> <span class="src">{esc(srcs)}</span></li>')
        out.append("</ul>")
    out.insert(0, f'<p class="small">{n} distinct sources after de-duplication. Grey text after each entry says where it is cited: '
                  '<i>report</i> = the research report, a note name = that research note, <i>Ch N</i> = a course page.</p>')
    return "\n".join(out), n

def splice(doc, begin, end, body):
    a, b = doc.index(begin) + len(begin), doc.index(end)
    return doc[:a] + "\n" + body + "\n" + doc[b:]

def main():
    today = datetime.date.today().isoformat()
    pages = scan_pages()
    scan_html, data = render_scan(pages, today)
    bib_html, nbib = render_bib(collect_bib())
    print(f"{len(pages)} pages, {sum(len(p['tags']) for p in pages)} tags, {len(data['flagged'])} flagged, {nbib} sources")
    for p in data["pages"]:
        print(f"  {p['short']:7s} {'(missing)' if p['missing'] else ''} " + " ".join(f"{k}={v}" for k, v in p["c"].items() if v))
    if "--check" in sys.argv:
        return
    doc = open(APPX, encoding="utf-8").read()
    doc = splice(doc, "<!-- scan:begin -->", "<!-- scan:end -->", scan_html)
    doc = splice(doc, "<!-- bib:begin -->", "<!-- bib:end -->", bib_html)
    open(APPX, "w", encoding="utf-8").write(doc)
    print("wrote", APPX)

if __name__ == "__main__":
    main()
