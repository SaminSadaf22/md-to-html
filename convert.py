#!/usr/bin/env python3
"""Convert a small subset of Markdown to HTML.

Supports headings, bold/italic, inline code, unordered lists and paragraphs. No dependencies.
"""

import html
import re
import sys
from pathlib import Path


def inline(text):
    text = html.escape(text)

    # Protect inline code spans so their contents are not touched by bold/italic rules.
    code_spans = []

    def stash(match):
        code_spans.append(match.group(1))
        return f"\x00CODE{len(code_spans) - 1}\x00"

    text = re.sub(r"`(.+?)`", stash, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)

    for i, code in enumerate(code_spans):
        text = text.replace(f"\x00CODE{i}\x00", f"<code>{code}</code>")
    return text


def convert(markdown):
    lines = markdown.splitlines()
    out = []
    in_list = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                out.append("</ul>")
                in_list = False
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            if in_list:
                out.append("</ul>")
                in_list = False
            level = len(heading.group(1))
            out.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
            continue

        if stripped.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline(stripped[2:])}</li>")
            continue

        if in_list:
            out.append("</ul>")
            in_list = False
        out.append(f"<p>{inline(stripped)}</p>")

    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def main():
    if len(sys.argv) != 3:
        print("usage: convert.py input.md output.html")
        return 1
    source = Path(sys.argv[1]).read_text(encoding="utf-8")
    Path(sys.argv[2]).write_text(convert(source), encoding="utf-8")
    print(f"wrote {sys.argv[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
