"""A dashed element too small to read as one outline.

Excalidraw draws a dashed stroke as dashes of 8 px with gaps of 8 px plus the
stroke width, so a side shorter than 32 px holds one or two dashes: a small
dashed square reads as four corner brackets, a small dashed circle as "( )".
A shape counts by its longest side, a line or an arrow by its length. There is
no fix: make it larger, or draw it solid and tell it apart by color or fill.
"""
import math

LEAST = 32


def run(elements):
    for element in elements.values():
        if element.get("strokeStyle") != "dashed" or element["type"] == "text":
            continue
        if element.get("strokeColor") == "transparent":
            continue
        if "points" in element:
            size = sum(math.dist(a, b) for a, b in zip(element["points"], element["points"][1:]))
            what = "long"
        else:
            size = max(abs(element["width"]), abs(element["height"]))
            what = "across its longest side"
        if size < LEAST:
            yield {"id": element["id"],
                   "problem": f"dashed {element['type']} only {size:.0f} px {what}: its dashes read as loose strokes"}
