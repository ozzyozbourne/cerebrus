#!/usr/bin/env python3
"""Scan the course for provenance tags and rebuild the generated parts of Appendix E.

Usage (from anywhere):
    python3 course/tools/scan_tags.py            # rewrite appendix-e-sources.html in place
    python3 course/tools/scan_tags.py --check    # print a summary only, change nothing
    python3 course/tools/scan_tags.py --list     # also print every flagged row (for spot checks)

What it does
  1. Reads the chapter order from assets/course.js (CHAPTERS, then APPENDICES). index.html and
     Appendix E are not scanned: their tags are a legend, not claims.
  2. Finds every static <span class="tag CLASS">label</span> in each page (tags drawn by widget
     JavaScript at run time are not counted) and records the class, the label, the claim text
     (the sentence or table row the tag qualifies) and the nearest preceding element id, so the
     flagged list can link to the right section.
  3. Skips legends: a run of four or more tags with nothing but punctuation between them (the
     tag key in Appendices A and B), and a bare class-name tag introduced by "labelled"/"tagged"
     (a sentence that explains the tags rather than making a claim).
  4. Flags every tag of class "unv"; every tag whose label says the figure came second-hand
     ("via ...", "secondary"); and every Indep tag labelled as press ("Press", "The Register",
     "STH"), because those are third-party write-ups, not measurements.
  5. Gives each flagged row a "why" (from its class and label) and a "what would settle it"
     (from what the claim is about, then its section, then the page's subject).
  6. Collects the bibliography: every markdown link in /home/user/cerebrus/reports and
     research_notes, every http(s) link in the course pages, and the EXTRA list below (sources
     verified for the 2026 NVIDIA/Groq update). URLs are de-duplicated (scheme, www., trailing
     slash, fragment and arXiv abs/pdf/html variants are folded together), given readable
     titles (TITLE_OVERRIDES) and grouped by topic.
  7. Writes the results between the <!-- scan:begin --> / <!-- scan:end --> and
     <!-- bib:begin --> / <!-- bib:end --> markers in appendix-e-sources.html.
"""
import datetime
import hashlib
import html
import json
import os
import re
import sys
import urllib.parse
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
COURSE = os.path.dirname(HERE)
ROOT = os.path.dirname(COURSE)
APPX = os.path.join(COURSE, "appendix-e-sources.html")
SELF = "appendix-e-sources.html"

TAG_CLASSES = ["vendor", "indep", "analyst", "sdk", "measured", "derived", "unv"]
VIA_RE = re.compile(r"\bvia\b|secondary", re.I)                 # second-hand, any class
PRESS_RE = re.compile(r"\bpress\b|the register|\bSTH\b", re.I)    # press write-up (Indep only)
BARE_NAMES = {"vendor", "indep", "independent", "analyst", "sdk", "sdk 2.10.1", "measured", "derived", "unverified"}

def is_flagged(cls, label):
    if cls == "unv":
        return True
    if VIA_RE.search(label):
        return True
    return cls == "indep" and bool(PRESS_RE.search(label))

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
ANCHORS = {"h2", "h3", "h4", "section", "figure", "div", "table", "details", "aside", "dl", "p", "li"}
MARK = "⟦%d⟧"                       # placeholder for tag n inside block text
MARK_RE = re.compile("⟦(\\d+)⟧")

class TagScanner(HTMLParser):
    """Walks a page. Each tag becomes a record pointing at its innermost block; the claim is
    worked out after the parse, when the block text and the table row are complete."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # dicts: tag, text, recs
        self.skip = 0
        self.in_tag = None       # [class, label-parts]
        self.recs = []
        self.tables = []         # header row (list of cell texts) per open table
        self.row = None          # {"cells": [...], "has_td": bool}
        self.section = ""
        self.in_h2 = False
        self.anchor = ""
        self.anchor_name = ""
        self.in_anchor_heading = None

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
            return
        if self.skip:
            return
        a = dict(attrs)
        if a.get("id") and tag in ANCHORS:
            self.anchor = a["id"]
            if tag in ("h2", "h3", "h4"):
                self.anchor_name = ""
                self.in_anchor_heading = tag
        if tag == "table":
            self.tables.append([])
        if tag == "tr":
            self.row = {"cells": [], "has_td": False, "header": self.tables[-1] if self.tables else []}
        if tag == "td" and self.row is not None:
            self.row["has_td"] = True
        if tag == "h2":
            self.in_h2 = True
            self.section = ""
        if tag == "span" and "tag" in (a.get("class") or "").split():
            cls = [c for c in a["class"].split() if c != "tag"]
            self.in_tag = [cls[0] if cls else "", []]
            return
        if tag in BLOCKS:
            blk = {"tag": tag, "text": "", "recs": []}
            if tag in ("td", "th") and self.row is not None:
                blk["row"] = self.row
                blk["col"] = len(self.row["cells"])
            self.stack.append(blk)
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
            n = len(self.recs)
            blk = self.stack[-1] if self.stack else None
            rec = {"n": n, "cls": cls, "label": label, "section": " ".join(self.section.split()),
                   "anchor": self.anchor, "anchor_name": " ".join(self.anchor_name.split()), "blk": blk}
            self.recs.append(rec)
            if blk is not None:
                blk["recs"].append(rec)
            self._add(" " + MARK % n + " ")
            return
        if tag == self.in_anchor_heading:
            self.in_anchor_heading = None
        if tag == "h2":
            self.in_h2 = False
        if tag in BLOCKS:
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i]["tag"] == tag:
                    blk = self.stack[i]
                    del self.stack[i:]
                    blk["text"] = " ".join(blk["text"].split())
                    if tag in ("td", "th") and "row" in blk:
                        blk["row"]["cells"].append(blk["text"])
                    if self.stack:
                        self.stack[-1]["text"] += " " + blk["text"] + " "
                    break
        if tag == "tr" and self.row is not None:
            if not self.row["has_td"] and self.tables:      # a header row: every cell is a <th>
                self.tables[-1][:] = [strip_marks(c, self.recs) for c in self.row["cells"]]
            self.row = None
        if tag == "table" and self.tables:
            self.tables.pop()

    def handle_data(self, data):
        if self.skip:
            return
        if self.in_tag is not None:
            self.in_tag[1].append(data)
            return
        if self.in_h2:
            self.section += data
        if self.in_anchor_heading:
            self.anchor_name += data
        self._add(data)

    def _add(self, s):
        if self.stack:
            self.stack[-1]["text"] += s

def show_marks(t, recs):
    """Replace placeholders by [label]."""
    return MARK_RE.sub(lambda m: "[" + recs[int(m.group(1))]["label"] + "]", t)

def strip_marks(t, recs):
    return " ".join(MARK_RE.sub(" ", t).split())

SENT_END = re.compile(r"(?<!\bal)(?<!e\.g)(?<!i\.e)(?<!\bvs)(?<!\bCh)(?<!\bNo)(?<!\bet)(?<!\bcf)(?<!\bSec)[.!?] (?=\S)")
DANGLING = re.compile(r"\b(is|are|was|were|be|as|of|by|from|and|or|the|a|an|to|remains?|labelled|tagged)$", re.I)
LEGEND_INTRO = re.compile(r"\b(labell?ed|tagged|marked)\b", re.I)

def sentence_start(t, end):
    ends = [m.end() for m in SENT_END.finditer(t, 0, end)]
    return ends[-1] if ends else 0

def tidy(c):
    c = " ".join(c.split())
    c = re.sub(r" ([,;.)])", r"\1", c)
    c = c.lstrip(" ,;:).–—-")
    return c.rstrip(" ,;:(–—-")

def legend_marks(text):
    """Tag numbers that sit in a run of >= 4 tags with only punctuation between them."""
    out = set()
    run = []
    pos = 0
    for m in MARK_RE.finditer(text):
        gap = text[pos:m.start()]
        if run and re.fullmatch(r"[\s,;/·|]*", gap):
            run.append(int(m.group(1)))
        else:
            if len(run) >= 4:
                out.update(run)
            run = [int(m.group(1))]
        pos = m.end()
    if len(run) >= 4:
        out.update(run)
    return out

def claim_of(rec, recs):
    """Return (claim, fragment-text) for one tag record, or (None, None) for a legend tag."""
    blk = rec["blk"]
    if blk is None:
        return "", ""
    raw = blk["text"]
    if rec["n"] in blk.setdefault("_legend", legend_marks(raw)):
        return None, None
    mk = MARK % rec["n"]
    p = raw.find(mk)
    before = raw[:p]
    st = sentence_start(before, len(before))
    if rec["label"].lower() in BARE_NAMES and LEGEND_INTRO.search(strip_marks(before[st:], recs)[-60:] if before[st:] else ""):
        return None, None
    claim = before[st:]
    if len(claim) > 240:
        k = claim.rfind("⟧ ")                       # end of an earlier tag in the same sentence
        if k > 0 and len(claim) - k > 50:
            claim = claim[k + 2:]
        else:
            k = claim.rfind("; ")
            if k > 0 and len(claim) - k > 40:
                claim = claim[k + 2:]
            else:
                claim = "… " + claim[-230:].split(" ", 1)[-1]
    if len(strip_marks(claim, recs)) < 20 and st > 0:  # too short: include the sentence before it
        st2 = sentence_start(before, st - 1)
        claim = before[st2:]
        if len(claim) > 240:
            claim = "… " + claim[-230:].split(" ", 1)[-1]
    body = tidy(strip_marks(claim, recs))
    lead = tidy(MARK_RE.split(claim)[0]).lstrip("… ")  # text before the first tag: safe for a text fragment
    claim = tidy(show_marks(claim, recs))
    if DANGLING.search(strip_marks(claim, recs)):          # the tag is the predicate ("... layout is [Unverified]")
        tail = raw[p + len(mk):]
        e = re.search(r"[.!?](\s|$)", tail)
        tail = tail[: e.start()] if e and e.start() < 80 else ""
        claim = claim + " [" + rec["label"] + "]" + tidy(" " + show_marks(tail, recs))
    if "row" in blk:                                     # table cell: add the row and column names
        row, col = blk["row"], blk["col"]
        hdr = row["header"]
        cells = row["cells"]
        def h(i):
            return hdr[i] if i < len(hdr) else ""
        if len(body.split()) < 3:                        # the cell holds little more than tags: use the row
            parts = []
            for i, c in enumerate(cells):
                c = tidy(strip_marks(c, recs))
                if i == col:
                    c = body
                if not c:
                    continue
                parts.append(c if i == 0 or not h(i) else f"{h(i)}: {c}")
            claim = " · ".join(parts)
            lead = tidy(MARK_RE.split(cells[0])[0]) if cells and col > 0 else ""
        else:
            ctx = []
            if col > 0 and cells:
                ctx.append(tidy(strip_marks(cells[0], recs)))
            if col > 0 and h(col):
                ctx.append(h(col))
            ctx = [c for c in ctx if c]
            if ctx:
                claim = " · ".join(ctx) + ": " + claim
    frag = []
    for w in lead.split():
        if "·" in w or len(frag) >= 6:
            break
        frag.append(w)
    frag = " ".join(frag).rstrip(",;:")
    return claim[-420:], (frag if len(frag.split()) >= 3 else "")

def scan_pages():
    pages = []
    for href, short, title in chapter_list():
        if href == SELF:
            continue
        path = os.path.join(COURSE, href)
        if not os.path.exists(path):
            pages.append({"href": href, "short": short, "title": title, "missing": True, "tags": [], "legend": 0})
            continue
        p = TagScanner()
        p.feed(open(path, encoding="utf-8").read())
        p.close()
        tags, legend = [], 0
        for r in p.recs:
            claim, frag = claim_of(r, p.recs)
            if claim is None:
                legend += 1
                continue
            tags.append({"cls": r["cls"], "label": r["label"], "claim": claim, "frag": frag,
                         "section": r["section"], "anchor": r["anchor"], "anchor_name": r["anchor_name"]})
        pages.append({"href": href, "short": short, "title": title, "missing": False, "tags": tags, "legend": legend})
    return pages

# ---------------------------------------------------------------- why / what would settle it
def reason(t):
    lab = t["label"].lower()
    cls = t["cls"]
    if cls == "unv":
        if "background" in lab:
            return "Background fact repeated from tutorials or secondary write-ups; not checked against a primary document in this course."
        if "press" in lab:
            return "Only press reports; the companies did not confirm."
        if "mapping" in lab:
            return "A mapping or model this course built from public talks; no Cerebras document confirms it."
        if "not independently measured" in lab:
            return "Only the vendor has published it; no independent measurement was found."
        if "not in course sources" in lab:
            return "None of the sources this course reached covers it."
        if re.search(r"not re-read|not re-checked|not verified|ptx isa", lab):
            return "A standard or primary reference exists, but it was not re-read or re-checked during the build."
        return "No reachable primary source confirmed it."
    route = ("press coverage" if "press" in lab else "a forum post" if "forum" in lab else
             "a search-engine extract" if "search" in lab else "a reprint" if "reprint" in lab else
             "an interview" if "interview" in lab else "secondary reporting")
    if cls == "indep":
        if re.search(r"via (press release|interview)", lab):
            return f"An independent measurement, but reached through {'a press release' if 'press release' in lab else 'an interview'} that quotes it, not the measurer's own results page."
        if "secondary" in lab:
            return "Described by a third party (a summary, survey or secondary write-up); no primary document was reached."
        extra = ", seen only as a search-engine extract" if "search" in lab else ""
        return f"A press write-up of a talk or announcement{extra}; the primary slides or document were not reached."
    if "sdk docs" in lab:
        return "The SDK documentation page could not be fetched; the wording comes from a search-engine extract of it."
    return f"The vendor's figure reached the course through {route}, not the vendor's own page."

S_CEREBRAS = "A Cerebras primary document (Hot Chips deck, sdk.cerebras.ai, press release) or, for programming facts, a simulator measurement."
S_NVIDIA = "NVIDIA's own datasheet, architecture whitepaper or docs.nvidia.com (CUDA/PTX guides); for software patterns, the cited paper or library source."
S_TT = "Tenstorrent's own documents (tt-isa-documentation, docs.tenstorrent.com spec pages, tt-metal README tables and tech reports) or an independent benchmark."
S_SDK = "The SDK documentation (sdk.cerebras.ai), or a small test with the installed SDK's compiler and simulator."
SETTLE_RULES = [  # first match wins; tested on claim + label, then on the section title, then the page default
    (r"\$\s?\d+(\.\d+)?\s?(billion|bn)\b|\bdeal\b|acqui", "A filing or statement by the companies involved; the press figure cites unnamed sources."),
    (r"\$\s?\d", "The seller's own store page or price list, with its date."),
    (r"mlperf", "The MLCommons results tables (mlcommons.org): a submission would be listed there."),
    (r"artificial analysis|\baa\b", "Artificial Analysis's own public leaderboard (artificialanalysis.ai), with model, date and settings."),
    (r"\bup to \d+\s?×|×\s(the )?throughput per|projection", "An independent measurement on shipping hardware; until then it is a vendor projection."),
    (r"config\.json|model card|active per token|experts must be resident|\d+ kv heads", "The model's published config.json or model card."),
    (r"\btpu|ironwood", "Google Cloud's TPU documentation (cloud.google.com/tpu/docs, the TPU7x page)."),
    (r"sambanova|sn40l", "The SN40L paper (Prabhakar et al., arXiv 2405.07518) or SambaNova's datasheet."),
    (r"\bamd\b|mi355|instinct", "AMD's MI355X product page (amd.com)."),
    (r"groqcloud|still independent", "Groq's own documentation (groq.com), or an independent GroqCloud benchmark."),
    (r"groq|\blpx\b|\blpus?\b|lp30|attention-ffn|\bcpx\b", "NVIDIA's LPX product page and GTC 2026 keynote, or an NVIDIA/Groq press release; an independent decode benchmark for performance claims."),
    (r"nvfp4", S_NVIDIA),
    (r"\bcb16\b", "A Cerebras document on the cb16 format, or a cslc/simulator test that round-trips known values."),
    (r"\bocp\b|mxfp4|ieee|bfloat16|\bfp8\b", "The OCP Microscaling (MX) specification v1.0 and IEEE 754; the course's own cslc check covers f16."),
    (r"csdb|sdk docs|builtin|picks the next task|scale differs from mul|cslc|@f[a-z]+s\b", S_SDK),
    (r"tensix|blackhole|wormhole|grayskull|galaxy|p150|p100|quietbox|tenstorrent|\btt-", S_TT),
    (r"tok/s|tokens per second|ttft", "The vendor's dated announcement with its configuration, cross-checked against an independent benchmark (e.g. Artificial Analysis)."),
    (r"cerebras|\bwse|\bcs-\d|wafer|memoryx|swarmx|condor|\bper pe\b|\bpes?\b|gbe|hot chips|\bhc\d{2,4}\b|microthread|datapath", S_CEREBRAS),
    (r"nvidia|h100|b200|gb200|rubin|nvlink|nvl72|hopper|blackwell|\bwarps?\b|tensor core|\btma\b|tmem|cuda|ptx|wgmma|nvswitch|megatron|cutlass|\bsms?\b|shared memory|\bsmem\b|hbm", S_NVIDIA),
]
PAGE_DEFAULT = {"16-tenstorrent.html": S_TT, "17-gpu.html": S_NVIDIA}
PAGE_DEFAULT.update({h: S_CEREBRAS for h in ("02-the-wafer.html", "03-processing-element.html", "04-fabric.html", "05-tasks.html",
    "06-dsds.html", "07-host-io.html", "08-systems.html", "09-model-to-tokens.html", "10-csl-toolchain.html",
    "11-lab-first-programs.html", "12-lab-neighbours.html", "13-lab-stencil.html", "14-lab-gemm.html", "15-lab-cg.html")})

def settle(t, page):
    for s in ((t["claim"] + " " + t["label"]).lower(), t.get("section", "").lower()):
        for pat, txt in SETTLE_RULES:
            if re.search(pat, s):
                return txt
    return PAGE_DEFAULT.get(page, "The primary document named in the chapter, or a measurement.")

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

# URL substring -> readable title, for links whose anchor text identifies nothing out of context
# (titles are built from the page's URL slug and the sentence that cites it; dates only where the URL has one).
TITLE_OVERRIDES = {
    "aminer.org/pub/62d16af05aee126c0fd027f0": "CU-Poker: placing DNNs on WSE with optimal kernel sizing and efficient protocol optimization (paper abstract, AMiner)",
    "cerebras.ai/blog/mistral-le-chat": "Cerebras blog: Cerebras powers Mistral Le Chat (Feb 2025)",
    "cerebras.net/chip/": "Cerebras: chip product page (WSE)",
    "clarigital.com/hardware/ai-chips/cerebras/cs3": "Clarigital: Cerebras CS-3 hardware profile",
    "datacenterdynamics.com/en/news/cerebras-unveils-four-trillion-transistor-giant-chip": "DCD: Cerebras unveils four-trillion-transistor giant chip, targets generative AI (WSE-3)",
    "datacenterdynamics.com/en/news/cerebras-unveils-cs-4-rack-scale-solution": "DCD: Cerebras unveils CS-4 rack-scale solution powered by four-trillion-transistor WSE-3T chip",
    "datacenterdynamics.com/en/news/nvidia-announces-vera-rubin-superchip": "DCD: NVIDIA announces Vera Rubin superchip for late 2026",
    "futurumgroup.com/insights/cerebras-cs-3-bring-on-the-nvidia-blackwell": "Futurum: Cerebras CS-3, bring on the NVIDIA Blackwell competition",
    "futurumgroup.com/insights/tenstorrents-galaxy-blackhole": "Futurum: Tenstorrent's Galaxy Blackhole, can RISC-V processors expand fast inference globally?",
    "gpusmith.com/articles/en/cerebras-wafer-scale-engine-explained": "GPUsmith: Cerebras Wafer-Scale Engine explained",
    "hyper-accel.github.io/en/posts/cerebras-wse": "HyperAccel blog: Cerebras WSE (architecture overview)",
    "insidedeeptech.com/cerebras-wafer-scale-engine": "Inside Deep Tech: Cerebras Wafer-Scale Engine (WSE, CS-3) full guide",
    "introl.com/blog/cerebras-wafer-scale-engine-cs3": "Introl blog: Cerebras Wafer-Scale Engine CS-3, alternative AI architecture guide (2025)",
    "blog.kowatek.com/?p=33381": "Kowatek blog: Tenstorrent Quasar chiplet on Samsung SF4X (2026 report)",
    "linuxpro.com.br/en/2026/09/cerebras-cs-4": "Linux Pro (BR): Cerebras CS-4 inference, video summary (Sep 2026)",
    "servethehome.com/?p=79969": "ServeTheHome: Tenstorrent Blackhole at Hot Chips 2024",
    "servethehome.com/cerebras-talks-going-rack-scale-with-their-wses-at-hot-chips-2026/cerebras-cs-4": "ServeTheHome: Cerebras CS-4 at Hot Chips 2026, power delivery (slide page)",
    "servethehome.com/cerebras-talks-going-rack-scale-with-their-wses-at-hot-chips-2026": "ServeTheHome: Cerebras talks going rack-scale with their WSEs at Hot Chips 2026",
    "servethehome.com/cerebras-wafer-scale-engine-wse-2-and-cs-2-at-hot-chips-34": "ServeTheHome: Cerebras Wafer Scale Engine WSE-2 and CS-2 at Hot Chips 34",
    "servethehome.com/decoding-the-future-of-inference-at-nvidia-groq-lpus": "ServeTheHome: Decoding the future of inference at NVIDIA, Groq LPUs join Vera Rubin platform",
    "servethehome.com/tenstorrent-blackhole-and-metalium": "ServeTheHome: Tenstorrent Blackhole and Metalium for standalone AI processing",
    "theregister.com/systems/2026/08/19/cerebras-cs-4": "The Register: Cerebras CS-4 rack systems juice chips for every last drop of AI performance (19 Aug 2026)",
    "theregister.com/2024/08/27/cerebras_ai_inference": "The Register: Cerebras AI inference launch (27 Aug 2024)",
    "tomshardware.com/news/cerebras-wafer-scale-engine-2": "Tom's Hardware: Cerebras Wafer Scale Engine 2, world's largest chip, 7 nm, 850,000 cores",
    "tomshardware.com/tech-industry/artificial-intelligence/cerebras-launches-900000-core": "Tom's Hardware: Cerebras launches 900,000-core, 125-petaflops wafer-scale processor for AI",
    "wccftech.com/cerebras-cs-4-30x-uplift": "Wccftech: Cerebras CS-4 30× uplift, CS-5 and CS-6 roadmap (2026)",
    "wccftech.com/jim-keller-cerebras-ipo": "Wccftech: Jim Keller says Cerebras IPO was helpful, Tenstorrent to beat them on everything",
    "aiweekly.co/alerts/cerebras-cs-4-posts-4400": "AI Weekly: Cerebras CS-4 posts 4,400 tokens/s, up to 30× vs GPUs",
    "benchlm.ai/blog/posts/cerebras-won-speed": "BenchLM blog: Cerebras won speed, not the shortlist",
    "businesswire.com/news/home/20241118595546": "BusinessWire: Cerebras press release (18 Nov 2024)",
    "cerebras.ai/blog/cerebras-inference-3x-faster": "Cerebras blog: Cerebras Inference, now 3× faster",
    "cerebras.ai/blog/which-is-faster-gemini-3-5-flash-or-kimi-k2-6": "Cerebras blog: Which is faster, Gemini 3.5 Flash or Kimi K2.6 on Cerebras?",
    "hpcwire.com/off-the-wire/cerebras-powers-openais-gpt-5-6-sol": "HPCwire: Cerebras powers OpenAI's GPT-5.6 Sol ultrafast mode",
    "businesswire.com/news/home/20250528123694": "BusinessWire: Cerebras beats NVIDIA Blackwell in Llama 4 Maverick inference (28 May 2025)",
    "cerebras.ai/blog/cerebras-kimi-k2-enterprise": "Cerebras blog: Kimi K2 on Cerebras for enterprise (May 2026)",
    "news.syncflo.xyz/2026-08-28-cerebras": "SyncFlo news: Cerebras CS-3 wafer-scale engine fast inference (28 Aug 2026; low-reliability site)",
    "thedataexchange.media/cerebras-inference": "The Data Exchange: Cerebras inference (interview)",
    "venturebeat.com/ai/cerebras-says-its-chips-run-a-trillion-parameter": "VentureBeat: Cerebras says its chips run a trillion-parameter AI model nearly 7× faster than GPU clouds",
    "x.com/cerebras/status/1878926975571763571": "Cerebras on X: post on defect tolerance and yield (status 1878926975571763571)",
    "cudocompute.com/products/nvidia-gb200-nvl72": "CUDO Compute: NVIDIA GB200 NVL72 product page",
    "cyfuture.ai/nvidia-gb200-gpu-server": "Cyfuture AI: NVIDIA GB200 GPU server page",
    "cudacourseh100.github.io": "H100 course slides: 1. Introduction to H100",
    "hothardware.com/news/nvidia-announce-vera-rubin-nvl576": "HotHardware: NVIDIA announces Vera Rubin NVL576 (roadmap)",
    "hyper.ai/en/stories/3422d6a72152beb34a564461208438ff": "hyper.ai: summary of NVIDIA's Rubin CPX announcement",
    "jarvislabs.ai/ai-faqs/nvidia-b200-specs": "Jarvislabs FAQ: NVIDIA B200 specs",
    "runpod.io/gpu-models/b200": "RunPod: NVIDIA B200 GPU model page",
    "spheron.network/gpu-rental/gb200": "Spheron: GB200 rental page",
    "tech-insider.org/nvidia-gtc-2026-rubin": "Tech Insider: NVIDIA GTC 2026 Rubin GPU analysis",
    "arxiv:2211.17192": "Leviathan, Kalman and Matias, Fast inference from transformers via speculative decoding (ICML 2023, arXiv 2211.17192)",
    "arxiv:2405.07898": "Molecular dynamics on the Cerebras wafer (Sandia, LLNL, LANL and Cerebras; arXiv 2405.07898)",
    "arxiv:2503.11698": "Wafer-scale vs GPU comparison paper (arXiv 2503.11698)",
    "computerhistory.org/collections/catalog/102752088": "Computer History Museum catalog: Cerebras wafer-scale engine (object 102752088)",
    "llnl.gov/article/52081": "LLNL news: NNSA researchers break molecular dynamics timescale barrier with world's largest chip",
    "ornl.gov/news/calculations-frontier-earns-gordon-bell-prize": "ORNL news: calculations on Frontier earn Gordon Bell Prize, ORNL at SC24",
    "anandtech.com/show/16006": "AnandTech: Hot Chips 2020 live blog, Cerebras WSE programming (show/16006)",
    "anandtech.com/show/21482": "AnandTech: Tenstorrent launches Wormhole AI processors, 466 FP8 TFLOPS at 300 W",
    "ispd.cc/ispd2026/slides/2020/ISPD_Contest_Closing_Session": "ISPD 2020 contest closing session: wafer-scale deep-learning accelerator placement (Cerebras)",
    "aiproductivity.ai/news/tenstorrent-quietbox-2": "AI Productivity: Tenstorrent QuietBox 2 RISC-V AI workstation",
    "counterpointresearch.com/en/insights/tenstorrent-at-the-open-frontier": "Counterpoint Research: Tenstorrent at the open frontier",
    "design-reuse.com/news/202530698-qualcomm": "Design & Reuse: Qualcomm reportedly considering a Tenstorrent acquisition for up to $10 billion",
    "gigazine.net/gsc_news/en/20250404-tenstorrent-blackhole": "Gigazine: Tenstorrent Blackhole (4 Apr 2025)",
    "hackster.io/news/tenstorrent-launches-its-risc-v-powered": "Hackster: Tenstorrent launches its RISC-V-powered Grayskull e75 and e150 boards",
    "hothardware.com/news/tenstorrent-wormhole-developer-kits": "HotHardware: Tenstorrent Wormhole developer kits and workstations",
    "insights.munich-startup.de/news/feed/tenstorrent-launches-110k-galaxy": "Munich Startup: Tenstorrent launches $110k Galaxy Blackhole AI server with 32 accelerators",
    "insights.munich-startup.de/news/feed/tenstorrent-launches-galaxy-blackhole-ai-system-with-10x": "Munich Startup: Tenstorrent Galaxy Blackhole, 10× faster video generation and 350 tokens/s LLM inference",
    "finance.technews.tw/2026/07/10/qualcomm": "TechNews (TW): Qualcomm reportedly acquires Tenstorrent for $10 billion (10 Jul 2026)",
    "thelogic.co/briefing/intel-qualcomm-interested": "The Logic: Intel and Qualcomm interested in acquiring Tenstorrent (report)",
    "videocardz.com/newz/tenstorrent-downgrades-blackhole-p150": "VideoCardz: Tenstorrent downgrades Blackhole p150 PCIe cards from 140 to 120 cores",
    "whatpsu.com/articles/2460": "WhatPSU: Tenstorrent removes 20 cores from already-shipped Blackhole p150 cards",
    "sdk.cerebras.ai/csl/language/builtins": "Cerebras SDK docs: CSL builtins reference",
    "sdk.cerebras.ai/sdk-release-notes/sdk-rel-notes-cumulative": "Cerebras SDK docs: cumulative release notes",
}
URL_OVERRIDES = {  # URL substring -> (url, title): a link that should point somewhere else
    "github.com/mgajewskitt/tt-metal": ("https://github.com/tenstorrent/tt-metal",
        "tt-metal README performance tables (Tenstorrent; the research note cited a contributor's fork, github.com/mgajewskiTT/tt-metal)"),
}
DROP = {"file:LIB"}          # bare library root: not a source
NAMED_IDS = {"hc34.hotchips.org": "src-hc34"}
SRC_NAMES = {"wse_hardware": "note: WSE hardware", "csl_programming": "note: CSL programming",
             "tenstorrent": "note: Tenstorrent", "gpu_and_comparison": "note: GPUs and comparison",
             "Ch 17/18 update": "Ch 17–18 update"}

TOPICS = [
    ("nvidia-groq", "NVIDIA, Groq and the 2026 SRAM decode tier"),
    ("cerebras-hw", "Cerebras hardware, systems and compiler talks"),
    ("cerebras-inf", "Cerebras inference, benchmarks and business"),
    ("sdk", "Cerebras SDK and CSL programming"),
    ("papers", "Academic papers and lab reports on wafer-scale computing"),
    ("tt", "Tenstorrent"),
    ("nvidia", "NVIDIA GPUs"),
    ("roofline", "Roofline, GPU programming and inference methods (tutorials, papers and analysis)"),
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
    "arxiv.org/abs/2211.17192": "roofline",
    "anandtech.com/show/16006": "cerebras-hw",
    "ispd.cc/ispd2026/slides/2020": "cerebras-hw",
    "blog.kowatek.com": "tt",
    "servethehome.com/?p=79969": "tt",
}
TOPIC_RULES = [  # first match wins; tested against "title url" lowercased
    ("local", r"^file://|^\s*file://"),
    ("nvidia-groq", r"groq|lpx|\blpu\b"),
    ("other", r"tpu|ironwood|sambanova|sn40l|\bamd\b|mi355"),
    ("tt", r"tenstorrent|tt-metal|tt-isa|metalium|ttnn|tt-forge|tt-buda|blackhole|wormhole|grayskull|tensix|quietbox|keller|flopper|whatpsu|videocardz"),
    ("sdk", r"sdk\.cerebras|sdk technical|sdk docs|sdk builtins|sdk release|training-api\.cerebras"),
    ("papers", r"arxiv|uspto|patent|llnl|ornl|nextplatform.*molecular|micro54|computerhistory"),
    ("cerebras-inf", r"artificialanalysis|inference|tokens|gpt-5|kimi|pricing|price|ipo|raised|benchlm|thedataexchange|bear-case|syncflo|venturebeat|hpcwire.*cerebras|morphllm|aiweekly|x\.com"),
    ("cerebras-hw", r"cerebras|wafer|wse|hotchips|hc34|hc31|hc2024|servethehome|semiwiki|gpusmith|hyper-accel|clarigital|damnang|insidedeeptech|mirrorfrog|introl|semianalysis.*cerebras|futurum.*cerebras|ucdavis|slideshare"),
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
        for k, (u2, t2) in URL_OVERRIDES.items():
            if k in url.lower():
                url, title = u2, t2
        if url.startswith("file://"):
            path = url[len("file://"):]
            path = path.replace("/home/user/cerebras-sdk/extras/csl-extras-202604101435-6-d2f7d96e/examples/", "EX/")
            key = "file:" + path
            title = path
        else:
            key = norm_url(url)
        if key in DROP:
            return
        e = entries.get(key)
        if e is None:
            e = entries[key] = {"key": key, "title": title, "url": url, "srcs": set(), "topic": topic or topic_of(title, url)}
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
            add(html.unescape(re.sub("<[^>]+>", "", text)).strip() or url, html.unescape(url), short)
    for title, url, topic in EXTRA:
        add(title, url, "Ch 17/18 update", topic)
    for e in entries.values():                    # readable titles win over scraped link text
        k = e["key"]
        for sub, t in TITLE_OVERRIDES.items():
            if sub.lower() in k or sub.lower() in e["url"].lower():
                e["title"] = t
                break
    return entries

# ---------------------------------------------------------------- render
def esc(s):
    return html.escape(s, quote=True)

def page_link(f):
    href = f["page"]
    if f.get("anchor"):
        href += "#" + f["anchor"]
        if f.get("frag"):
            href += ":~:text=" + urllib.parse.quote(f["frag"], safe="")
    elif f.get("frag"):
        href += "#:~:text=" + urllib.parse.quote(f["frag"], safe="")
    return href

def src_order(s):
    m = re.match(r"(Ch|App) (\w+)", s)
    if s == "report":
        return (0, 0, s)
    if s.startswith("note"):
        return (1, 0, s)
    if m:
        return (2 if m.group(1) == "Ch" else 3, int(m.group(2)) if m.group(2).isdigit() else ord(m.group(2)[0]), s)
    return (4, 0, s)

def render_scan(pages, today):
    flagged = []
    counts = []
    seen = set()
    for p in pages:
        c = {k: 0 for k in TAG_CLASSES}
        c["via"] = 0
        via_by = {}
        for t in p["tags"]:
            c[t["cls"]] = c.get(t["cls"], 0) + 1
            if not is_flagged(t["cls"], t["label"]):
                continue
            if t["cls"] != "unv":
                c["via"] += 1
                via_by[t["cls"]] = via_by.get(t["cls"], 0) + 1
            key = (p["href"], t["cls"], t["label"], t["claim"])
            if key in seen:                       # same tag on the same claim twice: list it once
                continue
            seen.add(key)
            flagged.append({"page": p["href"], "short": p["short"], "cls": t["cls"], "label": t["label"],
                            "claim": t["claim"], "section": t["section"], "anchor": t["anchor"],
                            "anchor_name": t["anchor_name"], "frag": t["frag"],
                            "why": reason(t), "settle": settle(t, p["href"])})
        counts.append({"href": p["href"], "short": p["short"], "title": p["title"], "missing": p["missing"],
                       "c": c, "via_by": via_by, "legend": p.get("legend", 0)})
    total = sum(len(p["tags"]) for p in pages)
    n_unv = sum(1 for f in flagged if f["cls"] == "unv")
    n_leg = sum(p.get("legend", 0) for p in pages)
    missing = [p["short"] for p in pages if p["missing"]]
    data = {"generated": today, "classes": TAG_CLASSES,
            "pages": counts, "flagged": [{"page": f["page"], "cls": f["cls"]} for f in flagged]}
    out = []
    out.append(f'<p class="small" id="scan-stamp">Generated on <b>{today}</b> by <code>python3 course/tools/scan_tags.py</code> from '
               f'{sum(1 for p in pages if not p["missing"])} pages: <b>{total}</b> static provenance tags (not counting {n_leg} tags in legends that '
               f'explain the tags). The list below has <b>{len(flagged)}</b> rows: <b>{n_unv}</b> Unverified and <b>{len(flagged) - n_unv}</b> '
               f'second-hand (a vendor or third-party figure reached via press, a forum, a search extract, a reprint or a secondary write-up).'
               + (f' Pages in the navigation but not yet written, hatched in the chart: {", ".join(missing)}.' if missing else "") + '</p>')
    out.append('<script type="application/json" id="scan-data">' + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + "</script>")
    out.append('<div class="table-wrap flag-wrap"><table class="mini flag-table" id="flag-static"><thead><tr><th>Page</th><th>Claim (the text the tag qualifies)</th><th>Tag</th><th>Why it is not verified</th><th>What would settle it</th></tr></thead><tbody>')
    for f in flagged:
        sec = f["anchor_name"] or f["section"]
        out.append(f'<tr data-page="{esc(f["page"])}" data-cls="{esc(f["cls"])}">'
                   f'<td data-label="Page"><a href="{esc(page_link(f))}">{esc(f["short"])}</a>'
                   + (f'<span class="sec">{esc(sec)}</span>' if sec else "") + '</td>'
                   f'<td data-label="Claim">{esc(f["claim"])}</td><td data-label="Tag"><span class="tag {esc(f["cls"])}">{esc(f["label"])}</span></td>'
                   f'<td data-label="Why">{esc(f["why"])}</td><td data-label="Would settle it">{esc(f["settle"])}</td></tr>')
    out.append('<tr class="flag-empty" hidden><td colspan="5">No flagged figures match these filters. <button type="button" class="btn secondary" data-clear>Clear filters</button></td></tr>')
    out.append("</tbody></table></div>")
    return "\n".join(out), data, flagged

def entry_id(e):
    for k, v in NAMED_IDS.items():
        if k in e["key"]:
            return v
    return "src-" + hashlib.md5(e["key"].encode()).hexdigest()[:8]

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
        out.append(f'<details class="bib-group" id="bib-{tid}"><summary>{esc(tname)} <span class="small">({len(items)})</span></summary>')
        out.append('<ul class="bib">')
        for e in items:
            n += 1
            srcs = ", ".join(SRC_NAMES.get(s, s) for s in sorted(e["srcs"], key=src_order))
            if tid == "local":
                out.append(f'<li id="{entry_id(e)}"><code>{esc(e["title"])}</code> <span class="src">{esc(srcs)}</span></li>')
            else:
                out.append(f'<li id="{entry_id(e)}"><a href="{esc(e["url"])}" rel="noopener">{esc(e["title"])}</a> <span class="src">{esc(srcs)}</span></li>')
        out.append("</ul></details>")
    out.insert(0, f'<p class="small">{n} distinct sources after de-duplication, in {len([t for t, _ in TOPICS if by.get(t)])} groups. '
                  'Grey text after each entry says where it is cited: <i>report</i> = the research report, <i>note: …</i> = one of the four '
                  'research notes behind it, <i>Ch N</i> or <i>App X</i> = a course page.</p>')
    return "\n".join(out), n

def splice(doc, begin, end, body):
    a, b = doc.index(begin) + len(begin), doc.index(end)
    return doc[:a] + "\n" + body + "\n" + doc[b:]

def main():
    today = datetime.date.today().isoformat()
    pages = scan_pages()
    scan_html, data, flagged = render_scan(pages, today)
    bib_html, nbib = render_bib(collect_bib())
    n_leg = sum(p.get("legend", 0) for p in pages)
    print(f"{len(pages)} pages, {sum(len(p['tags']) for p in pages)} tags (+{n_leg} legend tags skipped), {len(flagged)} flagged, {nbib} sources")
    for p in data["pages"]:
        print(f"  {p['short']:7s} {'(missing)' if p['missing'] else ''} " + " ".join(f"{k}={v}" for k, v in p["c"].items() if v)
              + (f" legend={p['legend']}" if p["legend"] else ""))
    if "--list" in sys.argv:
        for i, f in enumerate(flagged, 1):
            print(f"{i:3d} {f['short']:6s} {f['cls']:7s} [{f['label']}] {f['claim']}\n      -> {page_link(f)}\n      why: {f['why']}\n      settle: {f['settle']}")
    if "--check" in sys.argv or "--list" in sys.argv:
        return
    doc = open(APPX, encoding="utf-8").read()
    doc = splice(doc, "<!-- scan:begin -->", "<!-- scan:end -->", scan_html)
    doc = splice(doc, "<!-- bib:begin -->", "<!-- bib:end -->", bib_html)
    open(APPX, "w", encoding="utf-8").write(doc)
    print("wrote", APPX)

if __name__ == "__main__":
    main()
