"""A block diagram: blocks on a grid of equal columns, a block that spans columns as wide as they are, nested
blocks drawn around their cells, and straight labelled arrows.

    nests:                     # id: {title, color}; a nested block, a box around the blocks in it
      ledger: {title: ledger/, color: yellow}
    blocks:                    # id: {label, at: [column, row], columns, nest, color, external}
      skill: {label: SKILL.md, at: [0, 0], columns: 4}              # as wide as four columns
      sins: {label: sins.yaml, at: [0, 1], nest: ledger}
      excalidraw: {label: Excalidraw+, at: [2, 3], columns: 2, external: true}   # dashed, with no fill
    edges:                     # [from, to] or [from, to, label]; a nest can be either end
      - [skill, ledger, remite a]

You place each block on the grid, as the source declares it: a space in the
source is a cell with no block. Every block is one height and every column one
width, and the generator sizes the gaps for the nests and the arrow labels in
them. A block takes the color of its nest, blue outside every nest, unless it
names its own; the area a nest covers holds only its own blocks. An arrow runs
straight down the middle of the narrower of its two ends, or level between
blocks that share a row; one that would run over another block stops the drawing.
"""
from typing import NamedTuple

import fonts
from canvas import FONT, arrow, height, piece, tinted
from grid import Cell, Zone, cell, check_path, ends, layout
from palette import OPEN_COLOR, shade
from schema import DataError, choice, entries, fields, listed

SIZE, EDGE_SIZE = 18, 16
MIN_W, MIN_H, PAD_X, PAD_Y = 180, 60, 24, 14
NEST_SIDE, NEST_TOP = 20, 56  # how far a nest's box reaches past its blocks: sides and bottom, and top with the title
EDGE_COLOR = shade("gray", 7)


class Block(NamedTuple):
    label: str
    cell: Cell
    nest: str | None
    color: str
    external: bool


def parsed(data):
    fields(data, "top level", ("blocks",), ("nests", "edges"))
    nests = {}
    for z, nest in entries(data.get("nests"), "nests", optional=True).items():
        fields(nest, f"nests.{z}", ("title",), ("color",))
        nests[z] = str(nest["title"]), choice(nest.get("color", "blue"), f"nests.{z}.color", OPEN_COLOR)
    blocks = {}
    for n, block in entries(data["blocks"], "blocks").items():
        where = f"blocks.{n}"
        fields(block, where, ("label", "at"), ("columns", "nest", "color", "external"))
        if n in nests:
            raise DataError(f"{where}: {n} is also a nest")
        nest = choice(block["nest"], f"{where}.nest", nests) if "nest" in block else None
        color = choice(block.get("color", nests[nest][1] if nest else "blue"), f"{where}.color", OPEN_COLOR)
        blocks[n] = Block(str(block["label"]), cell(block, where, spans=("columns",)), nest, color,
                          bool(block.get("external")))
    for z in nests:
        if not any(block.nest == z for block in blocks.values()):
            raise DataError(f"nests.{z}: no block is in it")
    edges = []
    for i, edge in enumerate(listed(data.get("edges"), "edges")):
        if not isinstance(edge, list) or len(edge) not in (2, 3):
            raise DataError(f"edges[{i}]: expected [from, to] or [from, to, label], got {edge!r}")
        a, b = (choice(end, f"edges[{i}]", {**blocks, **nests}) for end in edge[:2])
        edges.append((a, b, str(edge[2]) if len(edge) == 3 else None))
    return nests, blocks, edges


def span(cells):
    """The cell that covers all of these."""
    c0, r0 = min(c.column for c in cells), min(c.row for c in cells)
    return Cell(c0, r0, max(c.last_column for c in cells) - c0 + 1, max(c.last_row for c in cells) - r0 + 1)


def apart(a, b):
    """How many columns and rows lie between two cells, 0 each way where they overlap."""
    return (max(0, a.column - b.last_column, b.column - a.last_column) +
            max(0, a.row - b.last_row, b.row - a.last_row))


def stand_ins(a, b, cells, members):
    """The blocks that stand for the ends of an arrow when sizing the gap it crosses: a nest's block nearest the
    other end."""
    area = {n: span([cells[m] for m in members[n]]) if n in members else cells[n] for n in (a, b)}
    return tuple(min(members[n], key=lambda m: apart(cells[m], area[other])) if n in members else n
                 for n, other in ((a, b), (b, a)))


def straight(box_a, box_b):
    """The fixed points of an arrow: down the middle of the narrower box when the wider one spans it, as
    grid.ends otherwise."""
    (ax, ay, aw, ah), (bx, by, bw, bh) = box_a, box_b
    narrow, wide = sorted((box_a, box_b), key=lambda box: box[2])
    x = narrow[0] + narrow[2] / 2
    if max(ay, by) < min(ay + ah, by + bh) or not wide[0] < x < wide[0] + wide[2]:
        return ends(box_a, box_b)
    down = by > ay
    return [(x - ax) / aw, int(down)], [(x - bx) / bw, int(not down)]


def build(data):
    nests, blocks, edges = parsed(data)
    cells = {n: block.cell for n, block in blocks.items()}
    members = {z: tuple(n for n, block in blocks.items() if block.nest == z) for z in nests}
    # every block one height and every column one width
    least = (max([MIN_W] + [fonts.width(b.label, FONT, SIZE) + 2 * PAD_X for b in blocks.values()
                            if b.cell.columns == 1]),
             max([MIN_H] + [height(b.label, SIZE) + 2 * PAD_Y for b in blocks.values()]))
    labels = [(*stand_ins(a, b, cells, members), fonts.width(label, FONT, EDGE_SIZE), height(label, EDGE_SIZE))
              for a, b, label in edges if label]
    zones = {z: Zone(members[z], NEST_SIDE, NEST_TOP) for z in nests}
    box, nest_box = layout(cells, {n: least for n in blocks}, zones, labels, least, where="blocks")
    out = []
    for z, (title, color) in nests.items():
        x, y, w, h = nest_box[z]
        drawn = piece("box-with-title", title=title, x=x, y=y, width=w, height=h, border="solid", color=color)
        drawn[0]["tempId"] = z
        out += drawn
    for n, block in blocks.items():
        out.append(tinted(n, box[n], "gray" if block.external else block.color, block.label, SIZE, block.external))
    boxes = {**box, **nest_box}
    for i, (a, b, label) in enumerate(edges):
        start, end = straight(boxes[a], boxes[b])
        style = {"strokeColor": EDGE_COLOR}
        if label:
            style["label"] = {"text": label, "fontSize": EDGE_SIZE, "fontFamily": FONT, "strokeColor": EDGE_COLOR}
        out.append(arrow(a, boxes[a], start, b, boxes[b], end, **style))
        # the blocks of a nest at either end are where the arrow starts or ends
        inside = {*members.get(a, ()), *members.get(b, ())}
        check_path(out[-1], a, b, [(n, box[n]) for n in blocks if n not in inside], f"edges[{i}]")
    return out
