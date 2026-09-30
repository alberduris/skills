"""Boxes in compartments, for the types drawn as tables on a grid: class, ER and requirement diagrams. A box is a
header band with its name, then sections of lines, each under a rule, all in one group; every box is as wide as
the widest and as tall as it needs, at the top of its row."""
import fonts
from canvas import FONT, INK, MUTED, arrow, height, text
from grid import ends, layout
from palette import shade

SIZE, HEAD_SIZE, EDGE_SIZE = 16, 18, 16
PAD, GUTTER, EMPTY, MIN_W = 12, 32, 16, 200  # GUTTER: before a right-hand column; EMPTY: an empty section
MIN_GAP = 100                                # room for an arrow head at each end
HEAD_ROOM = 24  # beside a label, for the arrow head that may sit between it and the box
EDGE_COLOR = "#495057"


def rows(section):
    """The lines of a section as (left, right) pairs: a line is a text, or [text, right-aligned text]."""
    return [(line, "") if isinstance(line, str) else tuple(line) for line in section]


def head_height(title):
    return height(title, HEAD_SIZE) + 2 * PAD


def section_height(section):
    return height("\n".join(left for left, _ in rows(section)), SIZE) + 2 * PAD if section else EMPTY


def size(title, sections):
    """The (width, height) a box needs for its title and its sections."""
    widths = [fonts.width(line, FONT, HEAD_SIZE) for line in title.split("\n")]
    for section in sections:
        for left, right in rows(section):
            widths += [fonts.width(line, FONT, SIZE) for line in left.split("\n")]
            if right:
                widths[-1] += GUTTER + fonts.width(right, FONT, SIZE)
    return max(MIN_W, max(widths) + 2 * PAD), head_height(title) + sum(section_height(s) for s in sections)


def boxes(cells, sizes, labels=(), min_gap=MIN_GAP, where="nodes"):
    """The box (x, y, width, height) of each cell: as wide as the widest box and centred in the columns it spans,
    as tall as `sizes` says, at the top of its row. `labels` are (id, id, text) of each labelled arrow."""
    widest = max(w for w, _ in sizes.values())
    label_sizes = [(a, b, fonts.width(t, FONT, EDGE_SIZE) + 2 * HEAD_ROOM, height(t, EDGE_SIZE) + 2 * HEAD_ROOM)
                   for a, b, t in labels]
    placed, _ = layout(cells, sizes, labels=label_sizes, least=(widest, 0), min_gap=min_gap, where=where)
    return {n: (x + (w - widest) / 2, y, widest, sizes[n][1]) for n, (x, y, w, _) in placed.items()}


def drawn(n, box, title, sections, color, group):
    """The elements of a box in compartments: an outline that arrows bind to, the header band with its title,
    and each section, left lines in ink and right lines right-aligned in gray."""
    x, y, w, h = box
    style = {"strokeColor": shade(color, 7), "strokeWidth": 2, "roughness": 0, "fillStyle": "solid",
             "groupIds": [group]}
    head = head_height(title)
    out = [{"type": "rectangle", "tempId": n, "x": x, "y": y, "width": w, "height": h, "backgroundColor": "#ffffff",
            **style},
           {"type": "rectangle", "x": x, "y": y, "width": w, "height": head, "backgroundColor": shade(color, 1),
            **style, "label": {"text": title, "fontSize": HEAD_SIZE, "fontFamily": FONT,
                               "strokeColor": shade(color, 9)}}]
    top = y + head
    for i, section in enumerate(sections):
        if i:
            out.append({"type": "line", "x": x, "y": top, "points": [[0, 0], [w, 0]], **style})
        lines = rows(section)
        if lines:
            out.append(text(x + PAD, top + PAD, "\n".join(left for left, _ in lines), SIZE, INK, groupIds=[group]))
        if any(right for _, right in lines):
            out.append(text(x + w - PAD, top + PAD, "\n".join(right for _, right in lines), SIZE, MUTED,
                            align="right", groupIds=[group]))
        top += section_height(section)
    return out


def level_or_straight(box_a, head_a, box_b, head_b):
    """The fixed points of a straight arrow: level at the height of the lower header's middle between boxes on one
    row, and as grid.ends places it otherwise."""
    (ax, ay, aw, ah), (bx, by, bw, bh) = box_a, box_b
    if ay != by:
        return ends(box_a, box_b)
    middle, right = min(head_a, head_b) / 2, bx > ax
    return [int(right), middle / ah], [int(not right), middle / bh]


def joined(a, box_a, start, b, box_b, end, label=None, **style):
    """A straight arrow in the edge color, with its label in the edge size."""
    if label:
        style["label"] = {"text": label, "fontSize": EDGE_SIZE, "fontFamily": FONT, "strokeColor": INK}
    return arrow(a, box_a, start, b, box_b, end, **{"strokeColor": EDGE_COLOR, **style})


def up_to_feet(pairs, box):
    """Where each (child, parent) arrow meets its parent's foot: spread along it, in the order of the children."""
    spots = {}
    for parent in {p for _, p in pairs}:
        children = sorted((c for c, p in pairs if p == parent), key=lambda c: box[c][0])
        spots.update({(c, parent): (i + 1) / (len(children) + 1) for i, c in enumerate(children)})
    return spots
