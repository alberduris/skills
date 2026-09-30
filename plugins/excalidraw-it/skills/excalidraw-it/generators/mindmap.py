"""A mindmap: the root in the middle, its branches stacked on both sides, and their leaves in a column further out.

    root: Tipos de diagrama
    branches:                  # branch: [leaves], or branch: {color, leaves}; right side first, top to bottom
      Cajas y flechas: {color: blue, leaves: [flowchart (a mano), architecture (a mano)]}
      Interacción: [sequence (a mano), {text: use case, muted: true}]   # a muted leaf is gray

The branches fill the right side top to bottom, then the left side top to bottom,
split where the two sides come out closest in height. The branches of a side share
the width of the widest, so break a long name with \n. A branch with no color
takes the next of blue, violet, teal, orange, grape, cyan, green and pink that no
branch chose. A leaf
is a text, or {text, muted: true} to gray it out, as for what is still pending;
say in the note what the gray means.
"""
import math

import fonts
from canvas import FONT, INK, LINE, MUTED, spare_colors, text
from palette import OPEN_COLOR, shade
from schema import DataError, choice, entries, fields, listed

ROOT_SIZE, BRANCH_SIZE, LEAF_SIZE = 28, 20, 18
BRANCH_H, LEAF_H, LEAF_GAP, SLOT_GAP = 56, 32, 8, 48
ROOT_H, ROOT_TO_BRANCH, BRANCH_TO_LEAF = 130, 150, 90
COLORS = ["blue", "violet", "teal", "orange", "grape", "cyan", "green", "pink"]
STROKE = {"strokeWidth": 2, "roughness": 0}


def lines(content):
    return content.count("\n") + 1


def parsed(data):
    fields(data, "top level", ("root", "branches"))
    branches, spare = [], spare_colors(entries(data["branches"], "branches"), COLORS)
    for name, value in data["branches"].items():
        where, color = f"branches.{name}", None
        if isinstance(value, dict):
            fields(value, where, (), ("color", "leaves"))
            color = choice(value["color"], f"{where}.color", OPEN_COLOR) if "color" in value else None
            value = value.get("leaves")
        leaves = []
        for j, leaf in enumerate(listed(value, where)):
            muted = False
            if isinstance(leaf, dict):
                fields(leaf, f"{where}[{j}]", ("text",), ("muted",))
                leaf, muted = leaf["text"], bool(leaf.get("muted"))
            if leaf is None:
                raise DataError(f"{where}[{j}]: a leaf needs a text")
            leaves.append((str(leaf), muted))
        branches.append((str(name), color or next(spare), leaves))
    return str(data["root"]), branches


def leaf_height(leaf):
    return max(LEAF_H, lines(leaf) * LEAF_SIZE * LINE + 8)


def branch_height(name):
    return max(BRANCH_H, lines(name) * BRANCH_SIZE * LINE + 20)


def slot(branch):
    """The height a branch takes on its side: its box, or the column of its leaves."""
    name, _, leaves = branch
    return max(branch_height(name), sum(leaf_height(leaf) + LEAF_GAP for leaf, _ in leaves))


def split(branches):
    """How many branches go right: the split, in order, where both sides come out closest in height."""
    def height(side):
        return sum(slot(b) for b in side) + SLOT_GAP * max(len(side) - 1, 0)
    return min(range(1, len(branches) + 1),
               key=lambda k: (abs(height(branches[:k]) - height(branches[k:])), abs(k - len(branches) / 2)))


def connector(start, end, start_id, end_id, start_point, end_point, stroke):
    """A curved arrow with no heads, leaving start level and bending into end's row halfway."""
    (sx, sy), (ex, ey) = start, end
    return {"type": "arrow", "x": sx, "y": sy, "points": [[0, 0], [(ex - sx) / 2, ey - sy], [ex - sx, ey - sy]],
            "roundness": {"type": 2}, "startArrowhead": None, "endArrowhead": None, "strokeColor": stroke, **STROKE,
            "startBinding": {"elementId": start_id, "fixedPoint": start_point, "mode": "inside"},
            "endBinding": {"elementId": end_id, "fixedPoint": end_point, "mode": "inside"}}


def side(branches, sign, root):
    """Branches stacked beside the root, each with its leaves in a column further out; sign 1 right, -1 left."""
    if not branches:
        return []
    rx, ry, rw, rh = root
    cx, cy = rx + rw / 2, ry + rh / 2
    width = max(fonts.width(name, FONT, BRANCH_SIZE) for name, _, _ in branches) + 48
    slots = [slot(b) for b in branches]
    top = cy - (sum(slots) + SLOT_GAP * (len(slots) - 1)) / 2
    inner = cx + sign * (rw / 2 + ROOT_TO_BRANCH)
    bx = inner if sign > 0 else inner - width
    outer = bx + width if sign > 0 else bx
    out = []
    for (name, color, leaves), height in zip(branches, slots):
        stroke, middle, h = shade(color, 7), top + height / 2, branch_height(name)
        branch_id = f"branch:{name}"
        out.append({"type": "rectangle", "tempId": branch_id, "x": bx, "y": middle - h / 2, "width": width,
                    "height": h, "strokeColor": stroke, "backgroundColor": shade(color, 1), "fillStyle": "solid",
                    "roundness": {"type": 3}, **STROKE,
                    "label": {"text": name, "fontSize": BRANCH_SIZE, "fontFamily": FONT,
                              "strokeColor": shade(color, 9)}})
        # leave the root's outline on the way to the branch
        angle = math.atan2((middle - cy) / (rh / 2), (inner - cx) / (rw / 2))
        start = cx + rw / 2 * math.cos(angle), cy + rh / 2 * math.sin(angle)
        out.append(connector(start, (inner, middle), "root", branch_id,
                             [0.5 + 0.5 * math.cos(angle), 0.5 + 0.5 * math.sin(angle)],
                             [0 if sign > 0 else 1, 0.5], stroke))
        y = middle - sum(leaf_height(leaf) + LEAF_GAP for leaf, _ in leaves) / 2
        for i, (leaf, muted) in enumerate(leaves):
            # a transparent box for the connector to bind to, and the text against the connector end: an add
            # ignores textAlign in a label, so the text stands alone, grouped with its box
            lh = leaf_height(leaf)
            leaf_w, leaf_middle = fonts.width(leaf, FONT, LEAF_SIZE) * 1.2 + 16, y + (lh + LEAF_GAP) / 2
            near = outer + sign * BRANCH_TO_LEAF
            lx, leaf_id = near if sign > 0 else near - leaf_w, f"leaf:{name}/{i}"
            group = [f"mindmap-{name}-{i}"]
            out += [{"type": "rectangle", "tempId": leaf_id, "x": lx, "y": leaf_middle - lh / 2, "width": leaf_w,
                     "height": lh, "strokeColor": "transparent", "backgroundColor": "transparent", "groupIds": group},
                    text(lx + 5 if sign > 0 else lx + leaf_w - 5, leaf_middle - lines(leaf) * LEAF_SIZE * LINE / 2,
                         leaf, LEAF_SIZE, MUTED if muted else INK, align="left" if sign > 0 else "right",
                         groupIds=group),
                    connector((outer, middle), (near, leaf_middle), branch_id, leaf_id,
                              [1 if sign > 0 else 0, 0.5], [0 if sign > 0 else 1, 0.5], stroke)]
            y += lh + LEAF_GAP
        top += height + SLOT_GAP
    return out


def build(data):
    root, branches = parsed(data)
    # an ellipse fits a label up to width / 2 * sqrt(2) - 10
    rw = (fonts.width(root, FONT, ROOT_SIZE) * 1.2 + 10) * math.sqrt(2) + 20
    rh = max(ROOT_H, (lines(root) * ROOT_SIZE * LINE + 10) * math.sqrt(2) + 20)
    box = (-rw / 2, -rh / 2, rw, rh)
    out = [{"type": "ellipse", "tempId": "root", "x": box[0], "y": box[1], "width": rw, "height": rh,
            "strokeColor": INK, "backgroundColor": shade("yellow", 1), "fillStyle": "solid", **STROKE,
            "label": {"text": root, "fontSize": ROOT_SIZE, "fontFamily": FONT, "strokeColor": INK}}]
    k = split(branches)
    return out + side(branches[:k], 1, box) + side(branches[k:], -1, box)
