"""An architecture: nodes on a grid of columns and rows, zones around their nodes, and straight labelled arrows.

    zones:                     # id: {title, color}
      maquina: {title: Tu máquina, color: blue}
    nodes:                     # id: {label, at: [column, row], rows, zone, external}
      operador: {label: Operador, at: [0, 0], rows: 2}        # spans rows 0 and 1
      claude: {label: Claude Code, at: [1, 1], zone: maquina}
      esm: {label: esm.sh, at: [1, 4], external: true}        # dashed, with no fill
    edges:                     # [from, to] or [from, to, label]
      - [operador, claude, pide el diagrama]

You place each node on the grid, and the generator sizes the grid: each column
as wide as its widest node, each gap wide enough for the zone borders and the
arrow labels in it. An arrow runs level between nodes that share a row, vertical
between nodes in one column, and straight across otherwise; a node that spans two
rows takes level arrows from both. An arrow that skips a column or a row runs
over it, so keep its path empty: an arrow over another node stops the drawing. A node takes the color of its zone, blue by
default, and is gray outside every zone. The area a zone covers on the grid holds
only its own nodes.
"""
from typing import NamedTuple

import fonts
from canvas import FONT, INK, arrow, height, piece, tinted
from grid import Cell, Zone, cell, check_path, ends, layout
from palette import OPEN_COLOR
from schema import DataError, choice, entries, fields, listed

SIZE, EDGE_SIZE = 18, 16
MIN_W, H, PAD_X, PAD_Y = 180, 70, 24, 14
ZONE_SIDE, ZONE_TOP = 40, 70  # how far a zone's box reaches past its nodes: sides and bottom, and top with the title
EDGE_COLOR = "#495057"


class Node(NamedTuple):
    label: str
    cell: Cell
    zone: str | None
    external: bool


def parsed(data):
    fields(data, "top level", ("nodes",), ("zones", "edges"))
    zones = {}
    for z, zone in entries(data.get("zones"), "zones", optional=True).items():
        fields(zone, f"zones.{z}", ("title",), ("color",))
        zones[z] = str(zone["title"]), choice(zone.get("color", "blue"), f"zones.{z}.color", OPEN_COLOR)
    nodes = {}
    for n, node in entries(data["nodes"], "nodes").items():
        where = f"nodes.{n}"
        fields(node, where, ("label", "at"), ("rows", "zone", "external"))
        zone = choice(node["zone"], f"{where}.zone", zones) if "zone" in node else None
        nodes[n] = Node(str(node["label"]), cell(node, where), zone, bool(node.get("external")))
    for z in zones:
        if not any(node.zone == z for node in nodes.values()):
            raise DataError(f"zones.{z}: no node is in it")
    edges = []
    for i, edge in enumerate(listed(data.get("edges"), "edges")):
        if not isinstance(edge, list) or len(edge) not in (2, 3):
            raise DataError(f"edges[{i}]: expected [from, to] or [from, to, label], got {edge!r}")
        a, b = (choice(end, f"edges[{i}]", nodes) for end in edge[:2])
        edges.append((a, b, str(edge[2]) if len(edge) == 3 else None))
    return zones, nodes, edges


def build(data):
    zones, nodes, edges = parsed(data)
    sizes = {n: (fonts.width(node.label, FONT, SIZE) + 2 * PAD_X,
                 height(node.label, SIZE) + 2 * PAD_Y) for n, node in nodes.items()}
    labels = [(a, b, fonts.width(label, FONT, EDGE_SIZE), height(label, EDGE_SIZE))
              for a, b, label in edges if label]
    members = {z: tuple(n for n, node in nodes.items() if node.zone == z) for z in zones}
    box, zone_box = layout({n: node.cell for n, node in nodes.items()}, sizes, labels=labels, least=(MIN_W, H),
                           zones={z: Zone(members[z], ZONE_SIDE, ZONE_TOP) for z in zones})
    out = []
    for z, (title, color) in zones.items():
        x, y, w, h = zone_box[z]
        out += piece("box-with-title", title=title, x=x, y=y, width=w, height=h, border="dashed", color=color)
    for n, node in nodes.items():
        color = zones[node.zone][1] if node.zone else "gray"
        out.append(tinted(n, box[n], color, node.label, SIZE, node.external))
    for i, (a, b, label) in enumerate(edges):
        start, end = ends(box[a], box[b])
        style = {"strokeColor": EDGE_COLOR}
        if label:
            style["label"] = {"text": label, "fontSize": EDGE_SIZE, "fontFamily": FONT, "strokeColor": INK}
        out.append(arrow(a, box[a], start, b, box[b], end, **style))
        check_path(out[-1], a, b, box.items(), f"edges[{i}]")
    return out
