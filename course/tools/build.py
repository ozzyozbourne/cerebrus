#!/usr/bin/env python3
"""Build lab chapters from course/src/*.html templates.

Placeholders:
  {{code:programs/01-saxpy/pe_program.csl}}  -> escaped, syntax-highlighted <pre> block of that file
  {{out:programs/01-saxpy/expected_output.txt}} -> escaped <pre> block of a real simulator run
This keeps the code shown in the course identical to the code that was validated.
Usage: python3 course/tools/build.py
"""
import html, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
KW = r"\b(const|var|fn|task|comptime|param|if|else|for|while|return|layout|import|from|def|True|False|None)\b"
TYPES = r"\b(f32|f16|i16|i32|u16|u32|bool|void|color|input_queue|output_queue|data_task_id|local_task_id|control_task_id|mem1d_dsd|fabin_dsd|fabout_dsd)\b"

def highlight(src: str) -> str:
    out = []
    for line in src.splitlines():
        code, comment = line, ""
        m = re.search(r"(//|#(?!!)).*$", line)
        if m and line.count('"', 0, m.start()) % 2 == 0:
            code, comment = line[: m.start()], line[m.start():]
        code = html.escape(code)
        code = re.sub(r"(&quot;.*?&quot;|'[^']*')", r'<span class="s">\1</span>', code)
        code = re.sub(r"(@\w+)", r'<span class="b">\1</span>', code)
        code = re.sub(KW, r'<span class="k">\1</span>', code)
        code = re.sub(TYPES, r'<span class="n">\1</span>', code)
        out.append(code + (f'<span class="c">{html.escape(comment)}</span>' if comment else ""))
    return "\n".join(out)

def render(m):
    kind, rel = m.group(1), m.group(2)
    p = ROOT / rel
    text = p.read_text()
    label = f'<div class="filename">course/{rel}</div>'
    if kind == "code":
        return f'{label}\n<pre><code>{highlight(text.rstrip())}</code></pre>'
    return f'{label}\n<pre class="output"><code>{html.escape(text.rstrip())}</code></pre>'

for src in sorted((ROOT / "src").glob("*.html")):
    out = re.sub(r"\{\{(code|out):([^}]+)\}\}", render, src.read_text())
    (ROOT / src.name).write_text(out)
    print("built", src.name)
