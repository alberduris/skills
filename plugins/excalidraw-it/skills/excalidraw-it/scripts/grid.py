"""Boxes on a grid of columns and rows that the agent chose: each column as wide as its widest box, each row as tall
as its tallest, and each gap as wide as the zone borders and the arrow labels in it. The generators that place
boxes share it: architecture and the types drawn on its recipe."""
from typing import NamedTuple

from schema import DataError, number, pair

BETWEEN = 24      # from a zone border to the next border or box
MIN_GAP = 60      # between two boxes with no border between them
LABEL_CLEAR = 28  # from an arrow label to the boxes and borders on each side of it


class Cell(NamedTuple):
    """Where a box sits: its first column and row, and how many of each it spans."""
    column: int
    row: int
    columns: int = 1
    rows: int = 1

    @property
    def last_column(self):
        return self.column + self.columns - 1

    @property
    def last_row(self):
        return self.row + self.rows - 1

    def spots(self):
        return [(c, r) for c in range(self.column, self.last_column + 1) for r in range(self.row, self.last_row + 1)]


class Zone(NamedTuple):
    """A box drawn around some boxes, `side` past them on the sides and at the bottom, and `top` past them at the top."""
    members: tuple
    side: float
    top: float


def cell(node, where, spans=("rows",)):
    """The cell of a node written as {at: [column, row]}, with `rows` or `columns` when `spans` lets it span them."""
    column, row = pair(node["at"], f"{where}.at", low=0, whole=True)
    span = {s: number(node.get(s, 1), f"{where}.{s}", low=1, whole=True) for s in spans}
    return Cell(column, row, span.get("columns", 1), span.get("rows", 1))


def areas(cells, zones, where):
    """The area each zone covers, (first column, last column, first row, last row), once no two boxes share a cell
    and each area holds only the boxes of its zone. Each zone has one member at least."""
    taken = {}
    for n, c in cells.items():
        for spot in c.spots():
            if spot in taken:
                raise DataError(f"{where}.{n}: cell {list(spot)} is taken by {taken[spot]}")
            taken[spot] = n
    out = {}
    for z, zone in zones.items():
        members = [cells[m] for m in zone.members]
        out[z] = c0, c1, r0, r1 = (min(m.column for m in members), max(m.last_column for m in members),
                                   min(m.row for m in members), max(m.last_row for m in members))
        for (column, row), n in taken.items():
            if n not in zone.members and c0 <= column <= c1 and r0 <= row <= r1:
                raise DataError(f"{where}.{n} sits in the area of {z}, columns {c0}-{c1} and rows {r0}-{r1}: "
                                "move it out, or into it")
    return out


def gap(before, after, need, min_gap):
    """Space between two columns or rows: the zone padding on each side, 0 with no border there, and the
    room an arrow label needs, 0 with no label. The label sits in the middle, so it takes the larger padding twice.
    A gap with a border is never narrower than one without."""
    base = max(min_gap, before + after + BETWEEN) if before or after else min_gap
    return max(base, 2 * max(before, after) + need) if need else base


def starts(sizes, gaps):
    out = [0]
    for size, space in zip(sizes, gaps):
        out.append(out[-1] + size + space)
    return out


def label_needs(cells, labels, columns, rows):
    """The room the arrow labels need in each column gap and each row gap: an arrow between boxes that share a
    column crosses the row gap between them, one between neighbouring columns crosses the column gap, and one
    that also joins neighbouring rows crosses a row gap as well, the third list."""
    column_needs, row_needs, across_needs = [0] * columns, [0] * rows, [0] * rows
    for a, b, width, height in labels:
        a, b = cells[a], cells[b]
        if a.column <= b.last_column and b.column <= a.last_column:
            upper, lower = sorted((a, b), key=lambda c: c.row)
            if lower.row - upper.last_row == 1:
                row_needs[upper.last_row] = max(row_needs[upper.last_row], height + 2 * LABEL_CLEAR)
        else:
            left, right = sorted((a, b), key=lambda c: c.column)
            if right.column - left.last_column == 1:
                column_needs[left.last_column] = max(column_needs[left.last_column], width + 2 * LABEL_CLEAR)
                upper, lower = sorted((a, b), key=lambda c: c.row)
                if lower.row - upper.last_row == 1:
                    across_needs[upper.last_row] = max(across_needs[upper.last_row], height + 2 * LABEL_CLEAR)
    return column_needs, row_needs, across_needs


def layout(cells, sizes, zones=None, labels=(), least=(0, 0), min_gap=MIN_GAP, where="nodes"):
    """The boxes (x, y, width, height) of the cells, each filling the columns and rows it spans, and of the zones.

    sizes: the (width, height) each box needs; a box that spans columns or rows sizes none of them.
    zones: {id: Zone}, each drawn around its members.
    labels: (id, id, width, height) of each arrow label, which widens the gap its arrow crosses.
    least: the narrowest column and the shortest row."""
    zones = zones or {}
    covered = areas(cells, zones, where)
    columns = max(c.last_column for c in cells.values()) + 1
    rows = max(c.last_row for c in cells.values()) + 1
    widths = [max([least[0]] + [sizes[n][0] for n, c in cells.items() if c.column == i and c.columns == 1])
              for i in range(columns)]
    heights = [max([least[1]] + [sizes[n][1] for n, c in cells.items() if c.row == i and c.rows == 1])
               for i in range(rows)]
    column_needs, row_needs, across_needs = label_needs(cells, labels, columns, rows)

    def reach(edge, pad, count):
        """How far past each column or row the zones whose area ends there at `edge` reach."""
        return [max([getattr(zones[z], pad) for z, area in covered.items() if area[edge] == i], default=0)
                for i in range(count)]
    left, right, top, bottom = reach(0, "side", columns), reach(1, "side", columns), reach(2, "top", rows), \
        reach(3, "side", rows)
    xs = starts(widths, [gap(right[i], left[i + 1], column_needs[i], min_gap) for i in range(columns - 1)])

    def row_need(i):
        """The label of a diagonal sits in the row gap too, where only a zone border running along it can meet it."""
        return max(row_needs[i], across_needs[i] if bottom[i] or top[i + 1] else 0)
    ys = starts(heights, [gap(bottom[i], top[i + 1], row_need(i), min_gap) for i in range(rows - 1)])
    boxes = {n: (xs[c.column], ys[c.row], xs[c.last_column] + widths[c.last_column] - xs[c.column],
                 ys[c.last_row] + heights[c.last_row] - ys[c.row]) for n, c in cells.items()}
    zone_boxes = {}
    for z, (c0, c1, r0, r1) in covered.items():
        side, head = zones[z].side, zones[z].top
        x0, y0 = xs[c0] - side, ys[r0] - head
        x1, y1 = xs[c1] + widths[c1] + side, ys[r1] + heights[r1] + side
        zone_boxes[z] = (x0, y0, x1 - x0, y1 - y0)
    return boxes, zone_boxes


def ends(box_a, box_b):
    """The fixed points of a straight arrow between two boxes: vertical where their columns overlap, level where
    their rows overlap, each at the middle of what both span, and across from a quarter of each side otherwise."""
    (ax, ay, aw, ah), (bx, by, bw, bh) = box_a, box_b
    left, right = max(ax, bx), min(ax + aw, bx + bw)
    if left < right:
        x, down = (left + right) / 2, by > ay
        return [(x - ax) / aw, int(down)], [(x - bx) / bw, int(not down)]
    top, bottom = max(ay, by), min(ay + ah, by + bh)
    to_right = bx > ax
    if top < bottom:
        y = (top + bottom) / 2
        return [int(to_right), (y - ay) / ah], [int(not to_right), (y - by) / bh]
    # off the middle, where a level arrow may already sit: low on the higher box, high on the lower one
    down = by > ay
    return [int(to_right), 0.75 if down else 0.25], [int(not to_right), 0.25 if down else 0.75]


def crosses(start, end, box):
    """Whether the segment from start to end runs through the inside of the box (x, y, width, height); along its
    edge or through a corner is outside."""
    (sx, sy), (ex, ey), (x, y, w, h) = start, end, box
    low, high = 0, 1
    for step, room in ((sx - ex, sx - x), (ex - sx, x + w - sx), (sy - ey, sy - y), (ey - sy, y + h - sy)):
        if step == 0:
            if room <= 0:
                return False
        elif step < 0:
            low = max(low, room / step)
        else:
            high = min(high, room / step)
    return low < high


def check_path(line, a, b, boxes, where):
    """Stop when the arrow from a to b runs through a box of neither. `boxes` are (owner, box) pairs, so a node
    may own more than one box."""
    points = [(line["x"] + px, line["y"] + py) for px, py in line["points"]]
    for n, box in boxes:
        if n not in (a, b) and any(crosses(p, q, box) for p, q in zip(points, points[1:])):
            raise DataError(f"{where}: the arrow from {a} to {b} runs over {n}; keep its path empty: "
                            f"move {n}, or {a} or {b}, to another cell")
