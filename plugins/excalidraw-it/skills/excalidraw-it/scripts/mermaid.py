#!/usr/bin/env python3
"""Convert Mermaid into the add payload of the MCP, through mermaid-to-excalidraw.

Reads Mermaid on stdin and prints the add payload, to pipe into write.py:

    mermaid.py --x 0 --y 0 < state.mmd | write.py <sceneId>

mermaid-to-excalidraw draws flowchart, sequence, class, ER and state diagrams as
native elements, and any other diagram, or one it fails on, as an image of the
whole diagram; this script exits with the converter's error instead. It runs in
headless Google Chrome through playwright-core, which the first run installs.
The converter drops the transitions of a state to itself; this script draws them.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import fonts

CONVERTER = Path(__file__).with_name("mermaid")
REACH = 10  # an arrow end this close to a shape is bound to it
SELF_LOOP = re.compile(r"^\s*([\w.]+)\s*-->\s*\1\s*(?::\s*(.*?))?\s*$", re.M)
LOOP_CLEAR, LOOP_OVER = 16, 24  # a self-loop's room past its label, and how far it runs above and below its state


def skeleton(source):
    if not (CONVERTER / "node_modules").exists():
        subprocess.run(["npm", "install", "--silent"], cwd=CONVERTER, check=True)
    result = subprocess.run(["node", "convert.mjs"], cwd=CONVERTER, input=source,
                            capture_output=True, text=True, timeout=120)
    if result.returncode:
        sys.exit(f"mermaid-to-excalidraw failed: {result.stderr[-500:]}")
    elements = json.loads(result.stdout)
    if any(element["type"] == "image" for element in elements):
        sys.exit("mermaid-to-excalidraw drew the diagram as an image: "
                 + (result.stderr.strip()[:300] or "the diagram type has no native conversion"))
    return elements


def extent(element):
    if "points" in element:
        xs = [element["x"] + x for x, _ in element["points"]]
        ys = [element["y"] + y for _, y in element["points"]]
        return min(xs), min(ys), max(xs), max(ys)
    return element["x"], element["y"], element["x"] + element["width"], element["y"] + element["height"]


def binding(point, shape):
    x0, y0, x1, y1 = extent(shape)
    fx = min(max((point[0] - x0) / (x1 - x0), 0), 1)
    fy = min(max((point[1] - y0) / (y1 - y0), 0), 1)
    return {"elementId": shape["id"], "fixedPoint": [fx, fy], "mode": "inside"}


def touches(point, shape):
    x0, y0, x1, y1 = extent(shape)
    return x0 - REACH <= point[0] <= x1 + REACH and y0 - REACH <= point[1] <= y1 + REACH


def add_payload(elements, left, top):
    """Ids become tempIds; an arrow end is bound to the shape it names only when it touches it:
    sequence arrows name their actors but run between lifelines, far from the actor boxes."""
    shapes = {e["id"]: e for e in elements if e["type"] != "arrow" and e.get("id")}
    boxes = [extent(e) for e in elements]
    dx, dy = left - min(b[0] for b in boxes), top - min(b[1] for b in boxes)
    payload = []
    for element in elements:
        new = {k: v for k, v in element.items() if k not in ("id", "start", "end", "link")}
        new.update(x=element["x"] + dx, y=element["y"] + dy)
        if element["type"] != "arrow" and element.get("id"):
            new["tempId"] = element["id"]
        for field, key, index in (("startBinding", "start", 0), ("endBinding", "end", -1)):
            shape = shapes.get((element.get(key) or {}).get("id"))
            if shape and "points" in element:
                point = element["x"] + element["points"][index][0], element["y"] + element["points"][index][1]
                if touches(point, shape):
                    new[field] = binding(point, shape)
        payload.append(new)
    return payload


def self_loops(source, payload):
    """The transitions of a state to itself, as a curved loop off its right side. The middle of the loop runs past
    the top and the bottom of the state, so the line shows around the label, and far enough out to clear it."""
    if not source.lstrip().startswith("stateDiagram"):
        return []
    shapes = {e["tempId"]: e for e in payload if e.get("tempId")}
    arrows = [e for e in payload if e["type"] == "arrow"]
    drawn = {(e.get("startBinding") or {}).get("elementId") for e in arrows
             if (e.get("startBinding") or {}).get("elementId") == (e.get("endBinding") or {}).get("elementId")}
    style = {k: v for k, v in (arrows[0] if arrows else {}).items()
             if k in ("strokeColor", "strokeWidth", "strokeStyle", "endArrowhead", "roundness")}
    size = (arrows[0].get("label") or {}).get("fontSize", 16) if arrows else 16
    loops = []
    for state, label in SELF_LOOP.findall(source):
        shape = shapes.get(state)
        if state in drawn or not shape:
            print(f"self-loop of {state} not drawn: " + ("already there" if shape else "no shape with that id"),
                  file=sys.stderr)
            continue
        x, y, h = shape["x"] + shape["width"], shape["y"], shape["height"]
        out = (fonts.width(label, 5, size) * 1.2 / 2 if label else 0) + LOOP_CLEAR
        loop = {"type": "arrow", "x": x, "y": y + h / 4, **style,
                "points": [[0, 0], [out, -h / 4 - LOOP_OVER], [out, h * 3 / 4 + LOOP_OVER], [0, h / 2]],
                "startBinding": {"elementId": state, "fixedPoint": [1, 0.25], "mode": "inside"},
                "endBinding": {"elementId": state, "fixedPoint": [1, 0.75], "mode": "inside"}}
        if label:
            loop["label"] = {"text": label, "fontSize": size}
        loops.append(loop)
    return loops


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--x", type=float, default=0, help="left edge of the diagram")
    parser.add_argument("--y", type=float, default=0, help="top edge of the diagram")
    args = parser.parse_args()
    source = sys.stdin.read()
    payload = add_payload(skeleton(source), args.x, args.y)
    print(json.dumps(payload + self_loops(source, payload), ensure_ascii=False))


if __name__ == "__main__":
    main()
