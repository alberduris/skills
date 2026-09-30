"""What the flow generators share (flowchart, swimlanes and agentflow): their nodes and edges as the YAML writes
them, the size of a node for its label, which edges run on a loop, an elbow arrow, the corridors of the arrows
that run along a side, and the label beside where an arrow leaves."""
import functools
import math

import fonts
from canvas import FONT, LINE, arrow, height, text
from schema import DataError, choice, fields, listed

LEVEL = ([1, 0.5], [0, 0.5])  # from the right side of one box to the left side of the next
DOWN = ([0.5, 1], [0.5, 0])   # from the foot of one box to the head of the next


def node(value, where, kinds, optional=()):
    """A node written as its label, or as {label, kind, …} with the keys in `optional`; its kind is kinds[0] by
    default."""
    if not isinstance(value, dict):
        value = {"label": value}
    fields(value, where, ("label",), ("kind", *optional))
    return {**value, "label": str(value["label"]), "kind": choice(value.get("kind", kinds[0]), f"{where}.kind", kinds)}


def edges(value, where, nodes):
    """[from, to] or [from, to, label], as (from, to, label or None)."""
    out = []
    for i, edge in enumerate(listed(value, where)):
        if not isinstance(edge, list) or len(edge) not in (2, 3):
            raise DataError(f"{where}[{i}]: expected [from, to] or [from, to, label], got {edge!r}")
        a, b = (choice(end, f"{where}[{i}]", nodes) for end in edge[:2])
        out.append((a, b, str(edge[2]) if len(edge) == 3 else None))
    return out


def label_width(label, size):
    """The width the server gives a bound label: up to 19% wider than the font measures it."""
    return fonts.width(label, FONT, size) * 1.2


def size(label, kind, font_size, least=200):
    """The smallest shape that holds the label: a diamond twice as wide and tall as its label, since it fits the
    label in half of each; an ellipse √2 as wide; a box 20 px wider on each side, `least` wide at least."""
    w = label_width(label, font_size) + 20
    h = height(label, font_size) + 20
    if kind == "decision":
        return max(220, 2 * w + 40), max(96, 2 * h)
    if kind == "terminal":
        return max(160, w * math.sqrt(2) + 20), max(60, h * math.sqrt(2))
    return max(least, w + 20), max(60, h)


def on_loops(edges):
    """The edges (from, to) that run on a loop: those whose end leads back to their start."""
    after = {}
    for a, b, _ in edges:
        after.setdefault(a, []).append(b)

    def reaches(start, goal):
        seen, todo = set(), [start]
        while todo:
            n = todo.pop()
            if n == goal:
                return True
            if n not in seen:
                seen.add(n)
                todo += after.get(n, [])
        return False
    return {(a, b) for a, b, _ in edges if reaches(b, a)}


def elbow(a, box_a, start, b, box_b, end, color, label=None, label_size=16, via=(), **style):
    """An elbow arrow bound by its two ends. The server routes it, or it turns at the corners in `via`."""
    if label:
        style["label"] = {"text": label, "fontSize": label_size, "fontFamily": FONT, "strokeColor": color}
    out = arrow(a, box_a, start, b, box_b, end, elbowed=True, strokeColor=color, **style)
    if via:
        out["points"] = [[0, 0], *([x - out["x"], y - out["y"]] for x, y in via), out["points"][-1]]
    return out


def crossing(rows, other):
    """Whether two arrows along one side, each as (first row, last row), have to cross: their rows overlap and
    neither holds the other's."""
    return rows[0] < other[0] < rows[1] < other[1] or other[0] < rows[0] < other[1] < rows[1]


def corridors(loops, clear=42, step=24):
    """The x of each arrow that runs along a side, from (id, side, first row, last row, edge, start): side is -1 on
    the left and 1 on the right, edge the outermost x on that side of what it passes, and start the row it leaves
    from. Each runs `clear` past its edge and `step` further out than those on its side whose rows it shares and
    that run inside it: those whose rows it holds, the shorter first, and of two that have to cross, the one that
    leaves from within the other's rows, so that they cross where the other one ends, away from its label."""
    def order(one, other):
        rows, other_rows = one[2:4], other[2:4]
        if crossing(rows, other_rows):
            within = other_rows[0] < one[5] < other_rows[1], rows[0] < other[5] < rows[1]
            if within[0] != within[1]:
                return -1 if within[0] else 1
        return (rows[1] - rows[0]) - (other_rows[1] - other_rows[0])

    out, placed = {}, []
    for n, side, low, high, edge, _ in sorted(loops, key=functools.cmp_to_key(order)):
        x = edge + side * clear
        for other_side, other_low, other_high, other_x in placed:
            if other_side == side and low <= other_high and other_low <= high:
                x = min(x, other_x - step) if side < 0 else max(x, other_x + step)
        placed.append((side, low, high, x))
        out[n] = x
    return out


def exit_label(content, point, start, color, font_size, below=False):
    """A label beside where an arrow leaves its box at `point`: right of the line on the way down out of a foot,
    and above the line on the way out a side, or below it when `below`."""
    x, y = point
    width = fonts.width(content, FONT, font_size)
    if start[1] == 1:
        x, y = x + 8, y + 4
    else:
        x = x - 8 - width if start[0] == 0 else x + 8
        y = y + 4 if below else y - 6 - font_size * LINE
    return text(x, y, content, font_size, color)
