"""An agentflow: who does each step, with which tool and what it consults; failures and fixes on the left, tools and
documents on the right.

    nodes:                     # down the main column, in order; kind: task (default), input, action, decision,
      ask: {label: Petición del operador, kind: input}          #   tool or document
      recipe: Leer la receta del tipo
      write: {label: Escribir en la escena, kind: action}
      warn: {label: Avisar al operador, beside: write}          # a failure or fix, left of write, on its row
      types: {label: types.yaml, kind: document, beside: recipe}  # consulted by recipe: right of it, on its row
    edges:                     # [from, to] or [from, to, label]: a step after another
      - [ask, recipe]
      - [recipe, write]
    failures:                  # [from, to] or [from, to, label]: in red
      - [write, warn, si falla]
    flows:                     # name: {from, to, color}: a dashed box around those steps of the main column
      Dibujar: {from: recipe, to: write, color: blue}             #   and their branches; color cycles by default
    words: {task: tarea}       # the legend's words, in Spanish by default

words takes input, task, tool, decision, document, action, seq, ref and fail.
You write the main column in order and put each branch, tool and document
beside a step of it: a tool or document on the right, bound to that step by a
dashed line with no head, and anything else on the left. An edge to a tool or
document is one more such line. The generator shapes each kind, sizes it for
its label, a diamond twice as wide as its label, and binds each arrow by its
two ends only, so the server routes the elbow: down the column, level to a
node on the same row, from a branch into the side of the step it returns to. One back up the main column, or skipping down it, runs along its left side,
clear of what it passes. The legend in the free corner at the bottom left
shows only the kinds the diagram uses.
"""
import math

import fonts
from canvas import FONT, INK, LINE, MUTED, arrow, piece, text
from flow import DOWN, LEVEL, corridors, edges as parsed_edges, elbow, exit_label, node, size
from palette import OPEN_COLOR, shade
from schema import DataError, choice, entries, fields

SIZE, EDGE_SIZE, LEGEND_SIZE = 16, 14, 14
ROW_GAP, LABELED_GAP, SIDE_GAP, FLOW_PAD, FLOW_GAP, SLANT = 50, 90, 140, 40, 36, 18
COLORS = {"task": "blue", "input": "teal", "action": "orange", "decision": "yellow", "tool": "grape",
          "document": "gray"}
ASIDE = ("tool", "document")  # the kinds that sit on the right, consulted
FLOW_COLORS = ("blue", "violet", "teal", "grape", "orange")
WORDS = {"input": "entrada", "task": "tarea", "tool": "herramienta", "decision": "decisión", "document": "documento",
         "action": "acción con efecto", "seq": "después", "ref": "consulta o usa", "fail": "si falla"}
ALONG_LEFT = ([0, 0.5], [0, 0.5])
RED = shade("red", 7)


def parsed(data):
    fields(data, "top level", ("nodes",), ("edges", "failures", "flows", "words"))
    nodes = {n: node(value, f"nodes.{n}", tuple(COLORS), ("beside",))
             for n, value in entries(data["nodes"], "nodes").items()}
    main = [n for n, value in nodes.items() if "beside" not in value]
    for n in main:
        if nodes[n]["kind"] in ASIDE:
            raise DataError(f"nodes.{n}: a {nodes[n]['kind']} sits beside the step that consults it")
    left, right = {}, {}
    for n, value in nodes.items():
        if "beside" in value:
            step = choice(value["beside"], f"nodes.{n}.beside", main)
            side = right if value["kind"] in ASIDE else left
            if step in side.values():
                raise DataError(f"nodes.{n}.beside: {step} already has a node on that side")
            side[n] = step
    edges = parsed_edges(data.get("edges"), "edges", nodes)
    failures = parsed_edges(data.get("failures"), "failures", nodes)
    colors = iter(FLOW_COLORS * 4)
    flows = {}
    for name, flow in entries(data.get("flows"), "flows", optional=True).items():
        where = f"flows.{name}"
        fields(flow, where, ("from", "to"), ("color",))
        first, last = (main.index(choice(flow[end], f"{where}.{end}", main)) for end in ("from", "to"))
        if first > last:
            raise DataError(f"{where}: {flow['from']} comes after {flow['to']} in the main column")
        if any(first <= other_last and other_first <= last for other_first, other_last, _ in flows.values()):
            raise DataError(f"{where}: it shares steps with another flow")
        flows[str(name)] = first, last, choice(flow.get("color", next(colors)), f"{where}.color", OPEN_COLOR)
    words = {**WORDS, **fields(data.get("words") or {}, "words", (), tuple(WORDS))}
    return nodes, main, left, right, edges, failures, flows, words


def shape_size(label, kind):
    w, h = size(label, "decision" if kind == "decision" else "task", SIZE, least=200)
    return w + (2 * SLANT if kind in ("input", "action") else 0), h


def outline(kind, x, y, w, h):
    """The points of a shape Excalidraw has no element for, as a closed line."""
    if kind == "input":
        return [(x + SLANT, y), (x + w, y), (x + w - SLANT, y + h), (x, y + h)]
    if kind == "action":
        return [(x + SLANT, y), (x + w - SLANT, y), (x + w, y + h / 2), (x + w - SLANT, y + h), (x + SLANT, y + h),
                (x, y + h / 2)]
    # a document: a wavy foot, sampled every 8 px
    foot = [(x + w - i, y + h - 6 + 6 * math.sin(2 * math.pi * i / w)) for i in range(0, int(w) + 1, 8)]
    return [(x, y), (x + w, y), *foot, (x, y + h - 6)]


def shape(n, kind, label, x, y, w, h):
    """The elements of a node; a shape Excalidraw has no element for is a closed line under a see-through box,
    which holds the label and the arrow ends."""
    color = COLORS[kind]
    style = {"strokeColor": shade(color, 7), "backgroundColor": "#ffffff" if kind == "document" else shade(color, 1),
             "fillStyle": "solid", "strokeWidth": 2, "roughness": 0}
    labelled = {"label": {"text": label, "fontSize": SIZE, "fontFamily": FONT, "strokeColor": shade(color, 9)}} \
        if label else {}
    box = {"x": x, "y": y, "width": w, "height": h, **({"tempId": n} if n else {})}
    if kind in ("task", "tool", "decision"):
        out = [{"type": "diamond" if kind == "decision" else "rectangle", **box, **style, **labelled,
                **({"roundness": {"type": 3}} if kind == "task" else {})}]
        if kind == "tool":  # a subroutine: a bar inside each end
            out += [{"type": "line", "x": x + dx, "y": y, "points": [[0, 0], [0, h]], **style} for dx in (10, w - 10)]
        return out
    points = outline(kind, x, y, w, h)
    out = [{"type": "line", "x": x, "y": y, "points": [[px - x, py - y] for px, py in points + [points[0]]], **style}]
    if kind == "document":  # a bar inside its left edge
        out.append({"type": "line", "x": x + 10, "y": y, "points": [[0, 0], [0, h - 6]], **style})
    return out + [{"type": "rectangle", **box, "strokeColor": "transparent", "backgroundColor": "transparent",
                   **labelled}]


def layout(nodes, main, left, right, edges, flows):
    """The box of each node: the main column centred, with room above each flow for its title; the branches
    right-aligned on the left and the tools and documents on the right, each level with its step."""
    sizes = {n: shape_size(value["label"], value["kind"]) for n, value in nodes.items()}
    main_w = max(sizes[n][0] for n in main)
    centre = FLOW_PAD + max([sizes[n][0] for n in left], default=0) + SIDE_GAP + main_w / 2
    labelled = {a for a, b, label in edges if label and a in main and b in main and main.index(b) == main.index(a) + 1}
    flow_of = {i: name for name, (first, last, _) in flows.items() for i in range(first, last + 1)}
    box, y = {}, 0
    for i, n in enumerate(main):
        w, h = sizes[n]
        if i and flow_of.get(i) != flow_of.get(i - 1):
            y += FLOW_GAP + (FLOW_PAD + 10 if i in flow_of else 0)  # room for the title of the flow it opens
        box[n] = (centre - w / 2, y, w, h)
        y += h + (LABELED_GAP if n in labelled else ROW_GAP)
    for side, x in ((left, centre - main_w / 2 - SIDE_GAP), (right, centre + main_w / 2 + SIDE_GAP + FLOW_PAD)):
        for n, step in side.items():
            (w, h), (_, sy, _, sh) = sizes[n], box[step]
            box[n] = (x - w if side is left else x, sy + sh / 2 - h / 2, w, h)
    return box


def ends(a, b, box, main):
    """Fixed points: level to a node on the same row, along the left side back up or down the main column, from
    the head or foot of a branch into the side of the step it returns to, and down otherwise."""
    (ax, ay, aw, ah), (bx, by, bw, bh) = box[a], box[b]
    if abs((ay + ah / 2) - (by + bh / 2)) < 1:
        return LEVEL if bx > ax else (LEVEL[1], LEVEL[0])
    if a in main and b in main and main.index(b) != main.index(a) + 1:
        return ALONG_LEFT
    if by < ay or a not in main:  # a branch returns into the side that faces it
        return [0.5, 0 if by < ay else 1], [0, 0.5] if bx > ax else [1, 0.5]
    return DOWN


def legend(used, words, x, y):
    out = []
    for i, kind in enumerate(k for k in WORDS if k in used):
        row = y + i * 38
        if kind in COLORS:
            out += shape(None, kind, None, x, row, 64, 28)
        else:
            out.append({"type": "arrow", "x": x, "y": row + 14, "points": [[0, 0], [64, 0]], "roughness": 0,
                        "strokeWidth": 2, "strokeColor": {"seq": INK, "ref": MUTED, "fail": RED}[kind],
                        "strokeStyle": "dashed" if kind == "ref" else "solid",
                        "endArrowhead": None if kind == "ref" else "triangle"})
        out.append(text(x + 78, row + 14 - LEGEND_SIZE * LINE / 2, words[kind], LEGEND_SIZE, MUTED))
    return out


def build(data):
    nodes, main, left, right, edges, failures, flows, words = parsed(data)
    box = layout(nodes, main, left, right, edges, flows)
    out, frames = [], []
    for name, (first, last, color) in flows.items():
        members = [box[n] for n in main[first:last + 1]] + [box[n] for n, step in left.items()
                                                             if first <= main.index(step) <= last]
        x0, y0 = min(b[0] for b in members) - FLOW_PAD, min(b[1] for b in members) - FLOW_PAD - 10
        x1, y1 = max(b[0] + b[2] for b in members) + FLOW_PAD, max(b[1] + b[3] for b in members) + FLOW_PAD
        frames.append((x0, y0, x1 - x0, y1 - y0))
        out += piece("box-with-title", title=f"flow {name}", x=x0, y=y0, width=x1 - x0, height=y1 - y0,
                     border="dashed", color=color)
    for n, value in nodes.items():
        out += shape(n, value["kind"], value["label"], *box[n])
    references = [(step, n, None) for n, step in right.items()]
    references += [edge for edge in edges if {nodes[edge[0]]["kind"], nodes[edge[1]]["kind"]} & set(ASIDE)]
    steps = [edge for edge in edges if edge not in references]
    for a, b, label in references:
        start, end = LEVEL if box[b][0] > box[a][0] else (LEVEL[1], LEVEL[0])
        style = {"label": {"text": label, "fontSize": EDGE_SIZE, "fontFamily": FONT, "strokeColor": MUTED}} \
            if label else {}
        out.append(arrow(a, box[a], start, b, box[b], end, strokeColor=MUTED, strokeStyle="dashed",
                         endArrowhead=None, **style))
    loops = []
    for a, b, _ in steps + failures:
        if ends(a, b, box, main) == ALONG_LEFT:
            low, high = sorted((main.index(a), main.index(b)))
            loops.append(((a, b), -1, low, high, min(box[n][0] for n in main[low:high + 1]), main.index(a)))
    lane = corridors(loops)
    spans = []  # the room each arrow may take, between its ends and out to its corridor, kept clear of the legend
    for kind, arrows in (("seq", steps), ("fail", failures)):
        color = RED if kind == "fail" else INK
        for a, b, label in arrows:
            start, end = ends(a, b, box, main)
            (ax, ay, aw, ah), (bx, by, bw, bh) = box[a], box[b]
            first, last = (ax + start[0] * aw, ay + start[1] * ah), (bx + end[0] * bw, by + end[1] * bh)
            if (a, b) not in lane:
                out.append(elbow(a, box[a], start, b, box[b], end, color, label, EDGE_SIZE, endArrowhead="triangle"))
                spans.append((min(first[0], last[0]), min(first[1], last[1]), abs(last[0] - first[0]),
                              abs(last[1] - first[1])))
                continue
            out.append(elbow(a, box[a], start, b, box[b], end, color, via=[(lane[a, b], first[1]), (lane[a, b], last[1])],
                             endArrowhead="triangle"))
            spans.append((lane[a, b], min(first[1], last[1]), first[0] - lane[a, b], abs(last[1] - first[1])))
            if label:
                out.append(exit_label(label, first, start, color, EDGE_SIZE, below=last[1] < first[1]))
    used = {value["kind"] for value in nodes.values()}
    used |= {kind for kind, arrows in (("seq", steps), ("ref", references), ("fail", failures)) if arrows}
    legend_w = 78 + max(fonts.width(words[k], FONT, LEGEND_SIZE) for k in used)
    taken = list(box.values()) + frames + spans
    x = min(b[0] for b in taken)
    y = max(b[1] + b[3] for b in taken if b[0] < x + legend_w) + 40
    return out + legend(used, words, x, y)
