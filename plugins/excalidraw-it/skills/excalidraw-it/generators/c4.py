"""A C4 diagram: people and systems, containers or components on a grid, the system boundary around its parts,
and dashed arrows labelled with a verb and its protocol.

    boundary: excalidraw-it  [sistema de software]     # the dashed box around the nodes with no role
    nodes:                     # id: {name, kind, text, at: [column, row], columns, role}
      operador: {name: Operador, kind: Persona, text: pide diagramas, at: [1, 0], role: person}
      claude: {name: Claude Code, kind: "Contenedor: agente CLI", text: planifica el diagrama, at: [1, 1]}
      esm: {name: esm.sh, kind: Sistema externo, text: sirve el conversor, at: [3, 1], role: external}
      excalidraw: {name: Excalidraw+, kind: Sistema externo, at: [1, 2], columns: 2, role: external}
    edges:                     # [from, to, verb] or [from, to, verb, protocol]
      - [operador, claude, pide el diagrama, chat]

One level of zoom per diagram: context, containers or components. A node with
no role is a part of the system: blue, and inside the boundary when there is
one. A person is indigo, with a head; an external system is gray and dashed.
`kind` is written in brackets under the name, and `text`, the description,
wraps past 260 px unless it breaks lines of its own. You place each node on the
grid, as in architecture, and the generator sizes it: each gap wide enough for
the labels in it, so a label stays outside the boundary it crosses. An arrow runs
level between nodes that share a row and vertical between nodes that share a
column, and one between two nodes outside the boundary that would cross it runs
around it instead, on the side where it crosses no node. An arrow that would run
over another node stops the drawing: keep its path empty.
"""
from typing import NamedTuple

import fonts
from canvas import FONT, INK, LINE, MUTED, TITLE_FONT, arrow, height, piece, text, tinted, wrapped
from grid import LABEL_CLEAR, Cell, Zone, cell, check_path, crosses, ends, layout
from palette import shade
from schema import DataError, choice, entries, fields, listed

NAME_SIZE, KIND_SIZE, TEXT_SIZE, EDGE_SIZE = 20, 14, 16, 15
MIN_W, MIN_H, PAD_X, PAD_Y, TEXT_W = 230, 124, 24, 16, 260
HEAD, HEAD_IN = 52, 10        # a person's head, and how far it sinks into the box
ZONE_SIDE, ZONE_TOP = 40, 76  # how far the boundary reaches past its nodes: sides and bottom, and top with the title
AIR = 16                      # more room beside a label than architecture leaves, for the arrowhead of a dashed arrow
COLORS = {"person": "indigo", "external": "gray", None: "blue"}
EDGE_COLOR = shade("gray", 7)


class Node(NamedTuple):
    name: str
    kind: str
    text: str
    cell: Cell
    role: str | None


def parsed(data):
    fields(data, "top level", ("nodes",), ("boundary", "edges"))
    nodes = {}
    for n, node in entries(data["nodes"], "nodes").items():
        where = f"nodes.{n}"
        fields(node, where, ("name", "kind", "at"), ("text", "columns", "role"))
        role = choice(node["role"], f"{where}.role", ("person", "external")) if "role" in node else None
        nodes[n] = Node(str(node["name"]), str(node["kind"]), wrapped(str(node.get("text", "")), TEXT_SIZE, TEXT_W),
                        cell(node, where, spans=("columns",)), role)
    boundary = data.get("boundary")
    if boundary is not None and all(node.role for node in nodes.values()):
        raise DataError("boundary: no node is in it; the nodes with no role go in it")
    edges = []
    for i, edge in enumerate(listed(data.get("edges"), "edges")):
        if not isinstance(edge, list) or len(edge) not in (3, 4):
            raise DataError(f"edges[{i}]: expected [from, to, verb] or [from, to, verb, protocol], got {edge!r}")
        a, b = (choice(end, f"edges[{i}]", nodes) for end in edge[:2])
        edges.append((a, b, str(edge[2]) + (f"\n[{edge[3]}]" if len(edge) == 4 else "")))
    return None if boundary is None else str(boundary), nodes, edges


def lines_height(node):
    """The name, the [kind] under it and the description under that."""
    out = NAME_SIZE * LINE + 4 + KIND_SIZE * LINE
    return out + 8 + height(node.text, TEXT_SIZE) if node.text else out


def size(node):
    """The width and height a node's box needs, without the room for a head."""
    return (max(fonts.width(node.name, TITLE_FONT, NAME_SIZE), fonts.width(f"[{node.kind}]", FONT, KIND_SIZE),
                fonts.width(node.text, FONT, TEXT_SIZE)) + 2 * PAD_X,
            max(MIN_H, lines_height(node) + 2 * PAD_Y))


def element(n, node, bounds):
    """A box with its name, its [kind] and its description, each centred; a person also has a head."""
    x, y, w, h = bounds
    color, group = COLORS[node.role], [f"c4-{n}"]
    out = [tinted(n, bounds, color, external=node.role == "external", groupIds=group)]
    if node.role == "person":
        out.append({"type": "ellipse", "tempId": f"{n}-head", "x": x + w / 2 - HEAD / 2, "y": y - HEAD + HEAD_IN,
                    "width": HEAD, "height": HEAD, "strokeColor": shade(color, 7), "strokeWidth": 2, "roughness": 0,
                    "backgroundColor": shade(color, 1), "fillStyle": "solid", "groupIds": group})
    top = y + (h - lines_height(node)) / 2 + (HEAD_IN / 2 if node.role == "person" else 0)
    kind_top = top + NAME_SIZE * LINE + 4
    centred = {"align": "center", "groupIds": group}
    out += [text(x + w / 2, top, node.name, NAME_SIZE, shade(color, 9), TITLE_FONT, **centred),
            text(x + w / 2, kind_top, f"[{node.kind}]", KIND_SIZE, MUTED, **centred)]
    if node.text:
        out.append(text(x + w / 2, kind_top + KIND_SIZE * LINE + 8, node.text, TEXT_SIZE, INK, **centred))
    return out


def around(a, b, body, frame, label):
    """The points of an arrow from a to b around the boundary, left or right of the whole drawing, on the side
    whose level runs from a and b cross no box; its label sits on the long vertical run."""
    reach = fonts.width(label, FONT, EDGE_SIZE) / 2 + LABEL_CLEAR
    everything = [*body.values(), frame]
    (ax, ay, aw, ah), (bx, by, bw, bh) = body[a], body[b]
    others = [box for n, box in body.items() if n not in (a, b)] + [frame]
    routes = []
    for side in (0, 1):
        run = (max(x + w for x, _, w, _ in everything) + reach) if side else (min(x for x, *_ in everything) - reach)
        points = [(ax + side * aw, ay + ah / 2), (run, ay + ah / 2), (run, by + bh / 2), (bx + side * bw, by + bh / 2)]
        hits = sum(crosses(p, q, box) for p, q in (points[:2], points[2:]) for box in others)
        routes.append((hits, abs(run - ax) + abs(run - bx), side, points))
    _, _, side, points = min(routes)
    return points, [side, 0.5], [side, 0.5]


def above(upper, lower):
    """Whether one cell sits above the other in a column they share."""
    return upper.last_row < lower.row and upper.column <= lower.last_column and lower.column <= upper.last_column


def ends_at(line):
    (px, py), (qx, qy) = line["points"]
    return (line["x"] + px, line["y"] + py), (line["x"] + qx, line["y"] + qy)


def build(data):
    boundary, nodes, edges = parsed(data)
    headroom = {node.cell.row: HEAD - HEAD_IN for node in nodes.values() if node.role == "person"}
    sizes = {n: (size(node)[0], size(node)[1] + headroom.get(node.cell.row, 0)) for n, node in nodes.items()}
    labels = [(a, b, fonts.width(label, FONT, EDGE_SIZE) + 2 * AIR, height(label, EDGE_SIZE) + 2 * AIR)
              for a, b, label in edges]
    zones = {"boundary": Zone(tuple(n for n, node in nodes.items() if node.role is None), ZONE_SIDE, ZONE_TOP)}
    cells, frames = layout({n: node.cell for n, node in nodes.items()}, sizes, zones if boundary else None, labels,
                           least=(MIN_W, 0))
    frame = frames.get("boundary")
    # a box sits under the headroom of its row, where a person's head goes
    body = {n: (x, y + headroom.get(nodes[n].cell.row, 0), w, h - headroom.get(nodes[n].cell.row, 0))
            for n, (x, y, w, h) in cells.items()}
    heads = {f"{n}-head": (x + w / 2 - HEAD / 2, y - HEAD + HEAD_IN, HEAD, HEAD) for n, (x, y, w, h) in body.items()
             if nodes[n].role == "person"}
    box = {**body, **heads}
    out = []
    if boundary:
        x, y, w, h = frame
        out += piece("box-with-title", title=boundary, x=x, y=y, width=w, height=h, border="dashed", color="blue")
    for n, node in nodes.items():
        out += element(n, node, body[n])
    owned = [*body.items(), *((n.removesuffix("-head"), head) for n, head in heads.items())]
    for i, (a, b, label) in enumerate(edges):
        style = {"strokeColor": EDGE_COLOR, "strokeStyle": "dashed",
                 "label": {"text": label, "fontSize": EDGE_SIZE, "fontFamily": FONT, "strokeColor": EDGE_COLOR}}
        # an arrow that comes down to a person, or leaves one upwards, ends at its head
        ta = f"{a}-head" if f"{a}-head" in heads and above(nodes[b].cell, nodes[a].cell) else a
        tb = f"{b}-head" if f"{b}-head" in heads and above(nodes[a].cell, nodes[b].cell) else b
        start, end = ends(box[ta], box[tb])
        line = arrow(ta, box[ta], start, tb, box[tb], end, **style)
        if frame and nodes[a].role and nodes[b].role and crosses(*ends_at(line), frame):
            points, start, end = around(a, b, body, frame, label)
            line = {**arrow(a, body[a], start, b, body[b], end, **style), "x": points[0][0], "y": points[0][1],
                    "points": [[px - points[0][0], py - points[0][1]] for px, py in points]}
        check_path(line, a, b, owned, f"edges[{i}]")
        out.append(line)
    return out
