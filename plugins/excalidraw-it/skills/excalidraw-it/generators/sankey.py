"""A sankey diagram: each stage a column of bars, and each flow a band to the next stage, as thick as its value.

    stages:                  # left to right, each {name, nodes}; nodes top to bottom
      - name: ruta
        nodes:               # id: label, gray; or id: {label, color}
          hand: {label: a mano, color: orange}
          later: por mirar
    flows:                   # [from, to, value], from a node to one in the next stage
      - [image, hand, 13]
    color_stage: 1           # the stage whose colors the flows take, the one that carries the meaning; 1 by default
    thousands: ","           # the thousands separator, "." by default

A bar is as tall as the larger of what comes in and what goes out, and the tallest
column takes 430 px. The flows stack on each bar in the order of the bars they
come from or go to, so none cross. A flow takes the color of its end in the color
stage, or of the end nearer to it.
"""
import fonts
from canvas import FONT, INK, LINE, MUTED, TITLE_FONT, path, shown, text
from palette import OPEN_COLOR, shade
from schema import DataError, choice, entries, fields, listed, number

HEADER_SIZE, LABEL_SIZE = 16, 16
TALLEST, BAR, GAP, MIN_COLUMN, SAMPLES = 430, 14, 26, 340, 24


def parsed(data):
    fields(data, "top level", ("stages", "flows"), ("color_stage", "thousands"))
    stages, node_of = [], {}
    for s, stage in enumerate(listed(data["stages"], "stages")):
        fields(stage, f"stages[{s}]", ("name", "nodes"))
        nodes = []
        for n, node in entries(stage["nodes"], f"stages[{s}].nodes").items():
            where, color = f"stages[{s}].nodes.{n}", "gray"
            if isinstance(node, dict):
                fields(node, where, ("label",), ("color",))
                color = choice(node.get("color", color), f"{where}.color", OPEN_COLOR)
                node = node["label"]
            if n in node_of:
                raise DataError(f"{where}: {n} is also a node of stage {node_of[n][0]}")
            node_of[n] = (s, len(nodes))
            nodes.append((n, str(node), color))
        stages.append((str(stage["name"]), nodes))
    if len(stages) < 2:
        raise DataError("stages: a sankey needs 2 stages or more")
    flows = []
    for i, flow in enumerate(listed(data["flows"], "flows")):
        if not isinstance(flow, list) or len(flow) != 3:
            raise DataError(f"flows[{i}]: expected [from, to, value], got {flow!r}")
        a, b = (choice(end, f"flows[{i}]", node_of) for end in flow[:2])
        if node_of[b][0] != node_of[a][0] + 1:
            raise DataError(f"flows[{i}]: {b} is not in the stage after the one of {a}")
        flows.append((a, b, number(flow[2], f"flows[{i}]", low=0)))
    color_stage = number(data.get("color_stage", 1), "color_stage", low=0, high=len(stages) - 1, whole=True)
    return stages, node_of, flows, color_stage, choice(data.get("thousands", "."), "thousands", (".", ","))


def band(x0, y0, x1, y1, thick):
    """A closed line between two bars: an S along a smoothstep on top, the same S back underneath."""
    ts = [i / SAMPLES for i in range(SAMPLES + 1)]
    top = [(x0 + (x1 - x0) * t, y0 + (y1 - y0) * (3 * t * t - 2 * t ** 3)) for t in ts]
    return top + [(x, y + thick) for x, y in reversed(top)] + top[:1]


def build(data):
    stages, node_of, flows, color_stage, thousands = parsed(data)
    size = {n: max(sum(v for a, _, v in flows if a == n), sum(v for _, b, v in flows if b == n)) for n in node_of}
    empty = [n for n in node_of if not size[n]]
    if empty:
        raise DataError(f"nodes {', '.join(empty)}: no flow comes in or goes out")
    color = {n: c for _, nodes in stages for n, _, c in nodes}
    label = {n: f"{name}  {shown(size[n], thousands)}" for _, nodes in stages for n, name, _ in nodes}
    unit = TALLEST / max(sum(size[n] for n, _, _ in nodes) or 1 for _, nodes in stages)
    # the labels of the first column stand left of its bars, so the chart starts where they end
    left = max(fonts.width(label[n], FONT, LABEL_SIZE) for n, _, _ in stages[0][1]) + 10
    # the labels of the other columns stand right of their bars, clear of the next column
    column = max([MIN_COLUMN] + [BAR + 10 + fonts.width(label[n], FONT, LABEL_SIZE) + 60
                                 for _, nodes in stages[1:-1] for n, _, _ in nodes])
    at = {}
    for s, (_, nodes) in enumerate(stages):
        y = 0
        for n, _, _ in nodes:
            at[n] = (left + s * column, y)
            y += size[n] * unit + GAP
    # each bar stacks its flows in the order of the bars at their other end
    out_at, into_at = {}, {}
    for n in node_of:
        y = at[n][1]
        for a, b, v in sorted((f for f in flows if f[0] == n), key=lambda f: node_of[f[1]]):
            out_at[a, b], y = y, y + v * unit
        y = at[n][1]
        for a, b, v in sorted((f for f in flows if f[1] == n), key=lambda f: node_of[f[0]]):
            into_at[a, b], y = y, y + v * unit
    out = []
    for a, b, v in flows:
        if not v:
            continue
        carrier = b if node_of[b][0] <= color_stage else a
        points = band(at[a][0] + BAR, out_at[a, b], at[b][0], into_at[a, b], v * unit)
        out.append(path("line", points, roundness=None, roughness=0, strokeColor="transparent",
                        backgroundColor=shade(color[carrier], 6), fillStyle="solid", opacity=35))
    for s, (_, nodes) in enumerate(stages):
        for n, _, c in nodes:
            x, y = at[n]
            h = size[n] * unit
            out.append({"type": "rectangle", "x": x, "y": y, "width": BAR, "height": h, "roughness": 0,
                        "strokeColor": shade(c, 7), "backgroundColor": shade(c, 7), "fillStyle": "solid"})
            first = s == 0
            out.append(text(x - 10 if first else x + BAR + 10, y + h / 2 - LABEL_SIZE * LINE / 2, label[n],
                            LABEL_SIZE, INK, align="right" if first else "left"))
    for s, (name, _) in enumerate(stages):
        out.append(text(left + s * column + BAR / 2, -HEADER_SIZE * LINE - 16, name, HEADER_SIZE, MUTED,
                        font=TITLE_FONT, align="center"))
    return out
