"""A flowchart: the happy path straight down one column, side branches in a column on its right, loops back up beside it.

    nodes:                     # down the happy path, in order; kind: step (default), decision or terminal
      start: {label: Petición del operador, kind: terminal}
      lint: lint.py --fix
      findings: {label: '¿Quedan findings?', kind: decision}
      hand: {label: Arreglar a mano, beside: findings}   # a side branch, right of findings, on its row
      end: {label: Hecho, kind: terminal}
    edges:                     # [from, to] or [from, to, label]
      - [start, lint]
      - [lint, findings]
      - [findings, hand, sí]
      - [hand, lint]
      - [findings, end, no]

You write the happy path in order and put each side branch beside a node of it;
the generator sizes each shape for its label, a diamond twice as wide as its
label, and binds each arrow by its two ends only, so the server routes the elbow.
An arrow runs down to the next node, out to the right into a branch, and back
from a branch into the right side of the node it returns to. One that goes back
up the happy path runs up its left side, or up its right when it would cross
another on the left and no branch or other arrow sits right of the nodes it
passes, and one that skips down it runs down its right side, or its left when a
branch sits beside either end; each clear of
the widest shape it passes, further out than another along that side over the
same rows, with its label beside where it leaves, under the line when it goes up. An arrow on a loop is orange,
and the one from a decision into the end is green.
"""
from canvas import FONT, INK
from flow import DOWN, LEVEL, corridors, crossing, edges as parsed_edges, elbow, exit_label, label_width, node, on_loops, size
from palette import shade
from schema import DataError, choice, entries, fields

SIZE = 16
ROW_GAP, LABELED_GAP, COLUMN_GAP = 50, 90, 90
LOOP, DONE = shade("yellow", 9), shade("green", 9)
STYLE = {  # kind: element type, border, fill, label
    "step": ("rectangle", shade("gray", 7), shade("gray", 1), INK),
    "decision": ("diamond", shade("yellow", 7), shade("yellow", 1), shade("yellow", 9)),
    "terminal": ("ellipse", shade("violet", 7), shade("violet", 1), shade("violet", 9)),
}
ALONG_LEFT = ([0, 0.5], [0, 0.5])    # along the left side of the happy path
ALONG_RIGHT = ([1, 0.5], [1, 0.5])   # along the right side of the happy path, and of the branches


def parsed(data):
    fields(data, "top level", ("nodes",), ("edges",))
    nodes = {n: node(value, f"nodes.{n}", tuple(STYLE), ("beside",))
             for n, value in entries(data["nodes"], "nodes").items()}
    main = [n for n, value in nodes.items() if "beside" not in value]
    beside = {}
    for n, value in nodes.items():
        if "beside" in value:
            row = choice(value["beside"], f"nodes.{n}.beside", main)
            if row in beside.values():
                raise DataError(f"nodes.{n}.beside: {row} already has a branch beside it")
            beside[n] = row
    return nodes, main, beside, parsed_edges(data.get("edges"), "edges", nodes)


def ends(a, b, place):
    """The fixed points of an arrow, from where a and b sit: (column, row), column 0 the happy path."""
    (ca, ra), (cb, rb) = place[a], place[b]
    branched = {r for c, r in place.values() if c == 1}
    if ca == cb == 0:
        if rb == ra + 1:
            return DOWN
        return ALONG_RIGHT if rb > ra and not {ra, rb} & branched else ALONG_LEFT
    if ca == 0:
        return LEVEL
    between = any(min(ra, rb) < r < max(ra, rb) for r in branched)
    if cb == 1:
        return ALONG_RIGHT if between else DOWN if rb > ra else (DOWN[1], DOWN[0])
    if rb == ra:
        return LEVEL[1], LEVEL[0]
    return ALONG_RIGHT if between else ([0.5, 0] if rb < ra else [0.5, 1], [1, 0.5])


def untangled(ends_of, place):
    """Moves an arrow along the left side that would cross another there over to the right side, when the right is
    clear over all its rows: no branch there, and no other arrow at the right side of a node there."""
    def rows(edge):
        return tuple(sorted((place[edge[0]][1], place[edge[1]][1])))

    def clear(edge):
        low, high = rows(edge)
        if any(column == 1 and low <= row <= high for column, row in place.values()):
            return False
        return not any(point[0] == 1 and place[n][0] == 0 and low <= place[n][1] <= high
                       for other, fixed in ends_of.items() if other != edge for n, point in zip(other, fixed))

    while True:
        left = [edge for edge, fixed in ends_of.items() if fixed == ALONG_LEFT]
        crossed = {edge: sum(crossing(rows(edge), rows(other)) for other in left) for edge in left}
        movable = [edge for edge in left if crossed[edge] and clear(edge)]
        if not movable:
            return ends_of
        ends_of[max(movable, key=lambda edge: crossed[edge])] = ALONG_RIGHT


def layout(nodes, main, beside, edges, place):
    """The box of each node: the happy path centred down its column, each gap tall enough for the label of the
    arrow down it, and the branches centred on their column, each level with the node it sits beside."""
    sizes = {n: size(value["label"], value["kind"], SIZE, least=220) for n, value in nodes.items()}
    labelled = {a for a, b, label in edges if label and ends(a, b, place) == DOWN}
    main_w = max(sizes[n][0] for n in main)
    branch_w = max([sizes[n][0] for n in beside], default=0)
    out_labels = [label_width(label, SIZE) + 60 for a, b, label in edges if label and place[a][0] == 0 != place[b][0]]
    branch_x = main_w + max([COLUMN_GAP] + out_labels) + branch_w / 2
    box, y = {}, 0
    for n in main:
        w, h = sizes[n]
        box[n] = (main_w / 2 - w / 2, y, w, h)
        y += h + (LABELED_GAP if n in labelled else ROW_GAP)
    for n, m in beside.items():
        (w, h), (_, my, _, mh) = sizes[n], box[m]
        box[n] = (branch_x - w / 2, my + mh / 2 - h / 2, w, h)
    return box


def lanes(edges, place, box, ends_of):
    """The x of each arrow along a side, clear of the widest shape in the rows it passes."""
    sides = []
    for a, b, _ in edges:
        side = -1 if ends_of[a, b] == ALONG_LEFT else 1 if ends_of[a, b] == ALONG_RIGHT else 0
        if side:
            low, high = sorted((place[a][1], place[b][1]))
            passed = [box[n] for n, (column, row) in place.items() if low <= row <= high and (column == 0 or side > 0)]
            edge = min(x for x, _, _, _ in passed) if side < 0 else max(x + w for x, _, w, _ in passed)
            sides.append(((a, b), side, low, high, edge, place[a][1]))
    return corridors(sides)


def build(data):
    nodes, main, beside, edges = parsed(data)
    place = {**{n: (0, row) for row, n in enumerate(main)}, **{n: (1, main.index(m)) for n, m in beside.items()}}
    box = layout(nodes, main, beside, edges, place)
    out = []
    for n, value in nodes.items():
        kind, border, fill, ink = STYLE[value["kind"]]
        x, y, w, h = box[n]
        out.append({"type": kind, "tempId": n, "x": x, "y": y, "width": w, "height": h, "strokeColor": border,
                    "backgroundColor": fill, "fillStyle": "solid", "strokeWidth": 2, "roughness": 0,
                    **({"roundness": {"type": 3}} if kind == "rectangle" else {}),
                    "label": {"text": value["label"], "fontSize": SIZE, "fontFamily": FONT, "strokeColor": ink}})
    looping, leaves = on_loops(edges), {a for a, _, _ in edges}
    ends_of = untangled({(a, b): ends(a, b, place) for a, b, _ in edges}, place)
    lane = lanes(edges, place, box, ends_of)
    for a, b, label in edges:
        start, end = ends_of[a, b]
        color = INK
        if (a, b) in looping and (start, end) != DOWN:
            color = LOOP
        elif nodes[a]["kind"] == "decision" and nodes[b]["kind"] == "terminal" and b not in leaves:
            color = DONE
        if (a, b) not in lane:
            out.append(elbow(a, box[a], start, b, box[b], end, color, label, SIZE))
            continue
        (ax, ay, aw, ah), (_, by, _, bh) = box[a], box[b]
        out.append(elbow(a, box[a], start, b, box[b], end, color, via=[(lane[a, b], ay + ah / 2),
                                                                       (lane[a, b], by + bh / 2)]))
        if label:
            out.append(exit_label(label, (ax + start[0] * aw, ay + ah / 2), start, color, SIZE, below=by < ay))
    return out
