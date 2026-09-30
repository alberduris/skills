"""A use case diagram: the system as a box with its use cases inside as ellipses, and its actors outside it.

    system: Excalidraw+
    actors:                    # name: {uses, side, color}, top to bottom on each side
      Operador: {uses: [view, fix, share], color: blue}
      Invitado: {uses: [view], side: right, color: teal}
    cases:                     # id: label
      view: Ver la escena en vivo
      fix: Corregir a mano
      share: Compartir la escena
      link: Crear enlace de invitación
    include:                   # [case, the case it includes]
      - [share, link]
    extend:                    # [case, the case it extends]
      - [fix, view]

side is left by default, and color the next of blue, orange, teal, grape, green
and pink. You say who uses what, and the generator places the cases: the ones an
actor uses in the column facing it, in the order of the actors and their uses,
each followed by the cases of its column that extend it or that it includes; a
case used from both sides in the left column, its row kept clear so the line
from the right reaches it; the cases no actor uses in gray, in an inner column
on the side of the case that includes them or that they extend, stacked around
its row: level with it when alone, half a row above and below it when two, as
close as they fit. Each case takes the tint of the first actor that uses it, and
each actor stands level with the middle of its cases.
"""
import math
from itertools import count

import fonts
from canvas import FONT, LINE, arrow, piece, spare_colors, wrapped
from palette import OPEN_COLOR, shade
from schema import DataError, choice, entries, fields, listed
from stick_figure import ARMS, FEET, HALF, HAND_GAP, hand, height as figure_height, stick_figure

NAME_SIZE, CASE_SIZE, TAG_SIZE = 18, 16, 14
WRAP = 110                    # a case label wider than this goes on two lines or more
ROW_GAP, COLUMN_GAP = 84, 150
INSET, TITLE_BAND = 48, 62    # from the cases to the box, and the title band of box-with-title
ACTOR_GAP, ACTOR_SPACE = 130, 30  # from the box to the hands of an actor, and between two actors on one side
DIAGONAL = math.sqrt(2) / 4   # from the middle of an ellipse to its outline at 45 degrees, in its sizes
COLORS = ["blue", "orange", "teal", "grape", "green", "pink"]


def pairs(value, where, cases):
    out = []
    for i, pair in enumerate(listed(value, where)):
        if not isinstance(pair, list) or len(pair) != 2 or pair[0] == pair[1]:
            raise DataError(f"{where}[{i}]: expected [case, another case], got {pair!r}")
        out.append(tuple(choice(str(c), f"{where}[{i}]", cases) for c in pair))
    return out


def parsed(data):
    fields(data, "top level", ("system", "actors", "cases"), ("include", "extend"))
    cases = {str(c): str(label) for c, label in entries(data["cases"], "cases").items()}
    raw = entries(data["actors"], "actors")
    spare, actors = spare_colors(raw, COLORS), {}
    for name, actor in raw.items():
        where = f"actors.{name}"
        fields(actor, where, ("uses",), ("side", "color"))
        uses = [choice(str(c), f"{where}.uses", cases) for c in listed(actor["uses"], f"{where}.uses")]
        if not uses:
            raise DataError(f"{where}.uses: name one case at least")
        if str(name) in cases:
            raise DataError(f"{where}: a case has this id too")
        color = choice(actor["color"], f"{where}.color", OPEN_COLOR) if "color" in actor else next(spare)
        actors[str(name)] = choice(actor.get("side", "left"), f"{where}.side", ("left", "right")), color, uses
    return str(data["system"]), actors, cases, pairs(data.get("include"), "include", cases), \
        pairs(data.get("extend"), "extend", cases)


def stacked(start, many, cases, lines):
    """`many` rows one apart, from `start` or as near it as they fit, half a row at a time: a row from the other
    cases of the column and half a row from the lines that cross it."""
    reach = int(max([abs(start), *map(abs, cases), *map(abs, lines)])) + many + 2  # past all of them, they fit
    for k in sorted(range(-2 * reach, 2 * reach + 1), key=lambda k: (abs(k), -k)):  # down before up
        rows = [start + k / 2 + i for i in range(many)]
        if all(abs(r - c) >= 1 for r in rows for c in cases) and all(abs(r - line) >= 0.5 for r in rows for line in lines):
            return rows


def placed(actors, cases, include, extend):
    """The column and row of each case; a row may be a half, and the first is 0."""
    kind = {}
    for want in ("left", "right"):  # a case used from both sides goes left
        for side, _, uses in actors.values():
            for c in uses:
                if side == want:
                    kind.setdefault(c, side)
    row, blocked = {}, set()
    for side in ("left", "right"):
        taken = set(blocked)
        # on the right, an actor that also uses a case on the left first, its cases around that case's row
        mine = [uses for s, _, uses in actors.values() if s == side]
        for uses in sorted(mine, key=lambda uses: side == "right" and all(kind[c] == "right" for c in uses)):
            order = []

            def visit(c):
                """c, then the cases of its column that extend it or that it includes."""
                if c not in row and c not in order and kind.get(c) == side:
                    order.append(c)
                    for follower in [a for a, b in extend if b == c] + [b for a, b in include if a == c]:
                        visit(follower)
            for c in uses:
                visit(c)
            shared = [row[c] for c in uses if side == "right" and kind[c] == "left"]
            start = max(0, round(sum(shared) / len(shared) - (len(order) - 1) / 2)) if shared else 0
            free = (r for r in count(start) if r not in taken)
            for c in order:
                row[c] = next(free)
                taken.add(row[c])
        if side == "left":  # the line from the right to a case on the left crosses the columns right of it
            blocked = {row[c] for s, _, uses in actors.values() if s == "right" for c in uses if kind[c] == "left"}
    # a case no actor uses hangs from the case that includes it or that it extends, in the inner column on its side,
    # with the other cases hanging from that one stacked around its row
    anchor = {}
    for a, b in include:
        anchor.setdefault(b, a)
    for a, b in extend:
        anchor.setdefault(a, b)
    pending = [c for c in cases if c not in kind]
    while pending:  # the ones hanging from the highest case placed first
        parent = min({anchor.get(c) for c in pending}, key=lambda a: (a not in row, row.get(a, 0)))
        hanging = [c for c in pending if anchor.get(c) == parent]
        side = kind.get(parent, "left").removesuffix("-inner")
        inner = [row[c] for c in row if kind.get(c) == f"{side}-inner"]
        start = row.get(parent, 0) - (len(hanging) - 1) / 2
        for c, r in zip(hanging, stacked(start, len(hanging), inner, blocked)):
            kind[c], row[c] = f"{side}-inner", r
            pending.remove(c)
    kinds = [k for k in ("left", "left-inner", "right-inner", "right") if k in kind.values()]
    top = min(row.values())
    return {c: kinds.index(kind[c]) for c in cases}, {c: r - top for c, r in row.items()}


def ends(a, b, column, row):
    """Fixed points on the outline of two cases: side to side on one row, top to bottom in one column, and
    otherwise at the corner of each that faces the other, so it leaves the middle of the sides to the level ones."""
    right, down = column[b] > column[a], row[b] > row[a]
    if row[a] == row[b]:
        return [int(right), 0.5], [int(not right), 0.5]
    if column[a] == column[b]:
        return [0.5, int(down)], [0.5, int(not down)]
    x, y = (DIAGONAL if right else -DIAGONAL), (DIAGONAL if down else -DIAGONAL)
    return [0.5 + x, 0.5 + y], [0.5 - x, 0.5 - y]


def build(data):
    system, actors, cases, include, extend = parsed(data)
    labels = {c: wrapped(label, CASE_SIZE, WRAP) for c, label in cases.items()}
    text_w = max(fonts.width(line, FONT, CASE_SIZE) for label in labels.values() for line in label.split("\n"))
    lines = max(label.count("\n") + 1 for label in labels.values())
    # the label of an ellipse fits in width / 2 * sqrt(2) - 10
    case_w = math.ceil((text_w * 1.2 + 10) * math.sqrt(2)) + 10
    case_h = math.ceil((lines * CASE_SIZE * LINE + 10) * math.sqrt(2)) + 6
    column, row = placed(actors, cases, include, extend)
    columns, rows = max(column.values()) + 1, max(row.values()) + 1
    box_w = 2 * INSET + columns * case_w + (columns - 1) * COLUMN_GAP
    box_h = TITLE_BAND + rows * case_h + (rows - 1) * ROW_GAP + INSET
    box = {c: (INSET + column[c] * (case_w + COLUMN_GAP), TITLE_BAND + row[c] * (case_h + ROW_GAP), case_w, case_h)
           for c in cases}
    out = piece("box-with-title", title=system, x=0, y=0, width=box_w, height=box_h, border="solid", color="gray")
    for c, label in labels.items():
        color = next((color for _, color, uses in actors.values() if c in uses), "gray")
        x, y, w, h = box[c]
        out.append({"type": "ellipse", "tempId": c, "x": x, "y": y, "width": w, "height": h, "roughness": 0,
                    "strokeWidth": 2, "strokeColor": shade(color, 7), "backgroundColor": shade(color, 1),
                    "fillStyle": "solid", "label": {"text": label, "fontSize": CASE_SIZE, "fontFamily": FONT,
                                                    "strokeColor": shade(color, 9)}})
    lines_out = []
    for side in ("left", "right"):
        mine = []
        for name, (s, color, uses) in actors.items():
            if s == side:
                arms = sum(box[c][1] + case_h / 2 for c in uses) / len(uses)
                if len(uses) == 1:  # half a row lower, or its only line runs on into its arms
                    arms += (case_h + ROW_GAP) / 2
                mine.append((arms, name))
        floor = -math.inf
        for arms, name in sorted(mine):  # each clear of the one above it
            arms, floor = max(arms, floor), max(arms, floor) + figure_height(NAME_SIZE) + ACTOR_SPACE
            _, color, uses = actors[name]
            cx = -ACTOR_GAP - HALF if side == "left" else box_w + ACTOR_GAP + HALF
            out += stick_figure(name, name, cx, arms - ARMS, shade(color, 7), NAME_SIZE)
            figure = (cx - HALF - HAND_GAP, arms - ARMS, 2 * (HALF + HAND_GAP), FEET)
            for c in uses:
                lines_out.append(arrow(name, figure, hand(side == "left"), c, box[c], [int(side == "right"), 0.5],
                                       strokeColor=shade(color, 7), endArrowhead=None))
    for kind, links in (("include", include), ("extend", extend)):
        for a, b in links:  # the arrow points at the case included or extended
            start, end = ends(a, b, column, row)
            lines_out.append(arrow(a, box[a], start, b, box[b], end, strokeColor=shade("gray", 7),
                                   strokeStyle="dashed", label={"text": f"«{kind}»", "fontSize": TAG_SIZE,
                                                                "fontFamily": FONT, "strokeColor": shade("gray", 7)}))
    return out + lines_out
