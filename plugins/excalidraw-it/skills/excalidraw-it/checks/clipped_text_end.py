"""A standalone Cascadia text stored narrower than it renders.

The MCP measures new text with metrics 15-20% narrower than Cascadia
(fontFamily 3), and the browser cuts the text at the stored width, while
take_screenshot draws it whole. An update of the width is kept as written.
Cascadia is monospace: every character advances 1200/2048 of the font size.
"""
import math

CASCADIA = 3
ADVANCE = 1200 / 2048


def run(elements):
    for text in elements.values():
        if text["type"] != "text" or text.get("fontFamily") != CASCADIA or text.get("containerId"):
            continue
        longest = max(len(line) for line in text["text"].split("\n"))
        width = math.ceil(longest * ADVANCE * text["fontSize"])
        if text["width"] < width - 1:
            yield {
                "id": text["id"],
                "problem": f'"{text["text"][:40]}" is stored {text["width"]:.0f} px wide and renders {width} px wide',
                "fix": {"update": [{"id": text["id"], "width": width}]},
            }
