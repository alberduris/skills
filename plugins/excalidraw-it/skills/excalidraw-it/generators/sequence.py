"""A sequence diagram: one column per participant with its lifeline, and the messages between them, top to bottom.

    participants:              # id: label, left to right; or id: {label, actor: true} for a stick figure
      operador: {label: Operador, actor: true}
      claude: Claude
      xplus: Excalidraw+
    messages:                  # in order, top to bottom
      - [operador, claude, pide el diagrama, +]   # a call; + starts a bar on the one it goes to
      - async: [xplus, operador, la escena cambia] # blue: the sender does not wait
      - reply: [xplus, claude, ids añadidos]      # dashed
      - [claude, claude, lint]                    # to itself: a loop right of its lifeline
      - note: {right: claude, text: lee los avisos}  # right or left of one, or over: [one, another]
      - loop:                                     # a fragment: loop and opt take one condition
          hasta lint limpio:
            - [claude, xplus, edit_scene_content]
      - alt:                                      # alt and par take one condition per branch
          si falla:
            - reply: [xplus, claude, error]
          si no:
            - reply: [xplus, claude, ok]
      - reply: [claude, operador, diagrama listo, -]  # - ends the bar of the one it comes from

The generator sets each gap between lifelines so the labels of the messages
across it and the notes beside it fit, writes each label centred above its
arrow, and draws each fragment as a dashed box around the lifelines its messages
touch, with its kind and condition at the top left and a dashed line between its
branches. Fragments nest, each box a little wider than the ones inside it. A bar
runs down its lifeline from the arrow that starts it to the one that ends it, or
to the foot when none does; a bar started inside another sits a little to the
right of it, and arrows meet the side of the innermost bar.
"""
import math
from typing import NamedTuple

import fonts
from canvas import FONT, INK, LINE, height, text, wrapped
from palette import shade
from schema import DataError, choice, entries, fields, listed
from stick_figure import HALF, HAND_GAP, height as figure_height, stick_figure

SIZE, TAG_SIZE, NOTE_SIZE = 16, 14, 15
BOX_W, BOX_H, PAD_X, PAD_Y = 150, 50, 24, 12
BOX_GAP = 40                   # between two participant boxes
CLEAR = 48                     # from a message label to the lifelines on each side of it, past the arrowhead
FIRST, LABEL_GAP, AFTER = 40, 6, 30  # under the boxes, under a label, and under a message to the next label
SELF_W, SELF_DROP = 36, 24     # the loop of a message to itself
FRAME_PAD, NEST_PAD = 40, 14   # a fragment past its outer lifelines, and more for each fragment inside it
FRAME_HEAD, FRAME_FOOT = 36, 16  # from a fragment's top to its first label, and from its last arrow to its foot
FRAME_COLOR, LIFELINE = "#f08c00", "#adb5bd"
BAR_W, BAR_STEP, BAR_MIN = 12, 6, 16  # a bar, how far right of it a bar inside it sits, and its shortest
NOTE_WRAP, NOTE_PAD = 220, 10  # a note wider than this goes on two lines or more
NOTE_OFF, NOTE_OVER, NOTE_CLEAR = 16, 28, 16  # from the lifeline, past the lifelines it spans, from the next one
STYLE = {"call": {"strokeColor": INK}, "reply": {"strokeColor": shade("gray", 7), "strokeStyle": "dashed"},
         "async": {"strokeColor": shade("blue", 7)}}
BRANCHES = {"loop": 1, "opt": 1, "alt": None, "par": None}  # how many conditions each fragment takes; None: any


class Message(NamedTuple):
    start: str
    end: str
    label: str
    kind: str
    bar: str | None  # + starts a bar on end, - ends the bar of start


class Note(NamedTuple):
    side: str        # left, right or over
    over: tuple      # the participants it sits beside or over
    text: str


class Fragment(NamedTuple):
    kind: str
    branches: list  # (condition, items)


def message(value, where, kind, participants):
    if not isinstance(value, list) or len(value) not in (3, 4) or value[3:] not in ([], ["+"], ["-"]):
        raise DataError(f"{where}: expected [from, to, label], with + or - after the label to start or end a bar, "
                        f"got {value!r}")
    return Message(choice(value[0], where, participants), choice(value[1], where, participants), str(value[2]), kind,
                   value[3] if len(value) == 4 else None)


def note(value, where, participants):
    fields(value, where, ("text",), ("left", "right", "over"))
    sides = [side for side in ("left", "right", "over") if side in value]
    if len(sides) != 1:
        raise DataError(f"{where}: expected one of left, right or over, got {', '.join(sides) or 'none'}")
    side = sides[0]
    over = value[side] if isinstance(value[side], list) else [value[side]]
    if not over or (side != "over" and len(over) != 1):
        raise DataError(f"{where}.{side}: expected {'one participant' if side != 'over' else 'participants'}, "
                        f"got {value[side]!r}")
    return Note(side, tuple(choice(p, f"{where}.{side}", participants) for p in over), str(value["text"]))


def items(value, where, participants):
    out = []
    for i, item in enumerate(listed(value, where)):
        at = f"{where}[{i}]"
        if isinstance(item, list):
            out.append(message(item, at, "call", participants))
            continue
        if not isinstance(item, dict) or len(item) != 1:
            raise DataError(f"{at}: expected [from, to, label], reply, async, note or a fragment, got {item!r}")
        (kind, value), = item.items()
        choice(kind, at, ["reply", "async", "note", *BRANCHES])
        at = f"{at}.{kind}"
        if kind in STYLE:
            out.append(message(value, at, kind, participants))
            continue
        if kind == "note":
            out.append(note(value, at, participants))
            continue
        branches = entries(value, at)
        if BRANCHES[kind] and len(branches) != BRANCHES[kind]:
            raise DataError(f"{at}: {kind} takes one condition, got {len(branches)}")
        fragment = Fragment(kind, [(str(c), items(v, f"{at}.{c}", participants)) for c, v in branches.items()])
        if not leaves([fragment]):
            raise DataError(f"{at}: it holds nothing")
        out.append(fragment)
    return out


def parsed(data):
    fields(data, "top level", ("participants", "messages"))
    participants = {}
    for p, value in entries(data["participants"], "participants").items():
        if isinstance(value, dict):
            fields(value, f"participants.{p}", ("label",), ("actor",))
            participants[p] = str(value["label"]), bool(value.get("actor"))
        else:
            participants[p] = str(value), False
    return participants, items(data["messages"], "messages", participants)


def leaves(items):
    """Every message and note in the items, fragments opened."""
    out = []
    for item in items:
        out += [m for _, inner in item.branches for m in leaves(inner)] if isinstance(item, Fragment) else [item]
    return out


def width(label, size=SIZE):
    return max(fonts.width(line, FONT, size) for line in label.split("\n"))


def note_size(n):
    """The label of a note, broken into lines, and the width and height of its box."""
    label = wrapped(n.text, NOTE_SIZE, NOTE_WRAP)
    return label, width(label, NOTE_SIZE) + 2 * NOTE_PAD, height(label, NOTE_SIZE) + 2 * NOTE_PAD


def note_span(n, x):
    """The left and right edge of a note."""
    _, w, _ = note_size(n)
    xs = [x[p] for p in n.over]
    if n.side == "right":
        return xs[0] + NOTE_OFF, xs[0] + NOTE_OFF + w
    if n.side == "left":
        return xs[0] - NOTE_OFF - w, xs[0] - NOTE_OFF
    middle, half = (min(xs) + max(xs)) / 2, max(w, max(xs) - min(xs) + 2 * NOTE_OVER) / 2
    return middle - half, middle + half


def needs(leaf, order):
    """The gaps a message or a note needs, as (first lifeline, last lifeline, the room between them)."""
    if isinstance(leaf, Note):
        _, w, _ = note_size(leaf)
        i, j = min(order.index(p) for p in leaf.over), max(order.index(p) for p in leaf.over)
        if leaf.side == "right":
            return [(i, i + 1, NOTE_OFF + w + NOTE_CLEAR)]
        if leaf.side == "left":
            return [(i - 1, i, NOTE_OFF + w + NOTE_CLEAR)]
        if i < j:
            return [(i, j, w - 2 * NOTE_OVER)]
        return [(i - 1, i, w / 2 + NOTE_CLEAR), (i, i + 1, w / 2 + NOTE_CLEAR)]
    i, j = sorted((order.index(leaf.start), order.index(leaf.end)))
    if i == j:
        return [(i, i + 1, SELF_W + BAR_W + 8 + width(leaf.label) + CLEAR)]
    return [(i, j, width(leaf.label) + 2 * CLEAR)]


def lifelines(participants, box_widths, all_leaves):
    """The x of each lifeline: neighbouring boxes BOX_GAP apart, and each gap widened until the labels across it
    and the notes beside it fit."""
    order = list(participants)
    widths = [box_widths[p] for p in order]
    gaps = [(widths[i] + widths[i + 1]) / 2 + BOX_GAP for i in range(len(order) - 1)]
    spans = [(i, j, need) for leaf in all_leaves for i, j, need in needs(leaf, order) if 0 <= i < j < len(order)]
    for i, j, need in sorted(spans, key=lambda n: n[1] - n[0]):  # the short spans first, spread over the long
        short = need - sum(gaps[i:j])
        for k in range(i, j):
            gaps[k] += max(0, short) / (j - i)
    xs = [widths[0] / 2]
    for g in gaps:
        xs.append(xs[-1] + g)
    return dict(zip(order, xs))


def reach(items, x):
    """The leftmost and rightmost x the messages in the items reach, and how deep the fragments in them nest."""
    left, right, depth = math.inf, -math.inf, 0
    for item in items:
        if isinstance(item, Fragment):
            l, r, d = reach([i for _, inner in item.branches for i in inner], x)
            left, right, depth = min(left, l), max(right, r), max(depth, d + 1)
            continue
        if isinstance(item, Note):
            l, r = note_span(item, x)
            left, right = min(left, l), max(right, r)
            continue
        left, right = min(left, x[item.start], x[item.end]), max(right, x[item.start], x[item.end])
        if item.start == item.end:
            right = max(right, x[item.start] + SELF_W + BAR_W + 8 + width(item.label))
    return left, right, depth


class Drawing:
    """Lays the messages, notes and fragments out from the top down: the arrows, notes and texts over the fragment
    tags, those over the bars, and those over the fragment boxes."""

    def __init__(self, x):
        self.x, self.front, self.tags, self.bars, self.back = x, [], [], [], []
        self.open = {p: [] for p in x}  # the top of each bar still running down a lifeline, outermost first

    def items(self, items, y):
        """Draws the items from y down; the lowest y they reach, y itself when there are none."""
        bottom = y
        for item in items:
            draw = self.fragment if isinstance(item, Fragment) else self.note if isinstance(item, Note) else self.message
            bottom = draw(item, y)
            y = bottom + AFTER
        return bottom

    def edge(self, p, right):
        """Where an arrow meets p: its lifeline, or the side of its innermost bar that faces the other end."""
        depth = len(self.open[p])
        if not depth:
            return self.x[p]
        return self.x[p] + (depth - 1) * BAR_STEP + (BAR_W / 2 if right else -BAR_W / 2)

    def close(self, p, y):
        """Ends the innermost bar of p at y."""
        if not self.open[p]:
            raise DataError(f"messages: {p} ends a bar with - but has none running; start one with + on a message to it")
        top = self.open[p].pop()
        depth = len(self.open[p])
        self.bars.append((depth, {"type": "rectangle", "x": self.x[p] + depth * BAR_STEP - BAR_W / 2, "y": top,
                                  "width": BAR_W, "height": max(y - top, BAR_MIN), "strokeColor": shade("gray", 7),
                                  "backgroundColor": "#ffffff", "fillStyle": "solid", "strokeWidth": 1,
                                  "roughness": 0}))

    def message(self, m, y):
        style, h = STYLE[m.kind], height(m.label, SIZE)
        arrow = {"type": "arrow", "strokeWidth": 2, "roughness": 0, "roundness": None, "endArrowhead": "arrow", **style}
        if m.start == m.end:  # a loop right of the lifeline, its label beside it
            drop = max(SELF_DROP, h)
            x0 = self.edge(m.start, True)
            if m.bar == "+":
                self.open[m.start].append(y + drop)
            x1 = self.edge(m.start, True)
            self.front += [{**arrow, "x": x0, "y": y, "points": [[0, 0], [SELF_W, 0], [SELF_W, drop], [x1 - x0, drop]]},
                           text(x0 + SELF_W + 8, y + drop / 2 - h / 2, m.label, SIZE, style["strokeColor"])]
            if m.bar == "-":
                self.close(m.start, y + drop)
            return y + drop
        arrow_y = y + h + LABEL_GAP
        if m.bar == "+":
            self.open[m.end].append(arrow_y)
        right = self.x[m.end] > self.x[m.start]
        x0, x1 = self.edge(m.start, right), self.edge(m.end, not right)
        self.front += [{**arrow, "x": x0, "y": arrow_y, "points": [[0, 0], [x1 - x0, 0]]},
                       text((x0 + x1) / 2, y, m.label, SIZE, style["strokeColor"], align="center")]
        if m.bar == "-":
            self.close(m.start, arrow_y)
        return arrow_y

    def note(self, n, y):
        label, _, h = note_size(n)
        left, right = note_span(n, self.x)
        self.front.append({"type": "rectangle", "x": left, "y": y, "width": right - left, "height": h,
                           "strokeColor": shade("yellow", 7), "backgroundColor": shade("yellow", 1),
                           "fillStyle": "solid", "strokeWidth": 1, "roughness": 0,
                           "label": {"text": label, "fontSize": NOTE_SIZE, "fontFamily": FONT, "strokeColor": INK}})
        return y + h

    def fragment(self, f, y):
        left, right, depth = reach([f], self.x)
        pad = FRAME_PAD + NEST_PAD * (depth - 1)
        tags = [f"{f.kind}: {f.branches[0][0]}"] + [c for c, _ in f.branches[1:]]
        x0 = left - pad
        x1 = max(right + pad, x0 + max(fonts.width(t, FONT, TAG_SIZE) for t in tags) + 24)
        line = {"type": "line", "strokeColor": FRAME_COLOR, "strokeStyle": "dashed", "strokeWidth": 1, "roughness": 0}
        top, bottom = y, y
        for i, ((_, inner), tag) in enumerate(zip(f.branches, tags)):
            if i:  # a dashed line between two branches, with the condition of the next under it
                y = bottom + FRAME_FOOT
                self.back.append({**line, "x": x0, "y": y, "points": [[0, 0], [x1 - x0, 0]]})
            # on a white patch that hides the lifelines and bars under it
            self.tags += [{"type": "rectangle", "x": x0 + 8, "y": y + 6, "width": fonts.width(tag, FONT, TAG_SIZE) + 8,
                           "height": TAG_SIZE * LINE + 4, "strokeColor": "transparent", "backgroundColor": "#ffffff",
                           "fillStyle": "solid", "roughness": 0},
                          text(x0 + 12, y + 8, tag, TAG_SIZE, FRAME_COLOR)]
            bottom = self.items(inner, y + FRAME_HEAD)
        bottom += FRAME_FOOT
        self.back.append({"type": "rectangle", "x": x0, "y": top, "width": x1 - x0, "height": bottom - top,
                          "strokeColor": FRAME_COLOR, "backgroundColor": "transparent", "strokeStyle": "dashed",
                          "strokeWidth": 1, "roughness": 0})
        return bottom


def build(data):
    participants, content = parsed(data)
    heads = {p: max(width(label) + 2 * PAD_X, 2 * (HALF + HAND_GAP)) if actor else max(BOX_W, width(label) + 2 * PAD_X)
             for p, (label, actor) in participants.items()}
    x = lifelines(participants, heads, leaves(content))
    tall = {p: figure_height(SIZE) if actor else max(BOX_H, height(label, SIZE) + 2 * PAD_Y)
            for p, (label, actor) in participants.items()}
    header = max(tall.values())
    drawing = Drawing(x)
    end = drawing.items(content, header + FIRST) + AFTER
    for p, running in drawing.open.items():  # a bar no arrow ends runs to the foot
        for _ in list(running):
            drawing.close(p, end - AFTER / 2)
    out = []
    for p, (label, actor) in participants.items():
        top = header - tall[p]  # each participant stands on the line its lifeline starts from
        if actor:
            out += stick_figure(p, label, x[p], top, shade("gray", 7), SIZE, FONT)
        else:
            out.append({"type": "rectangle", "x": x[p] - heads[p] / 2, "y": top, "width": heads[p], "height": tall[p],
                        "strokeColor": shade("gray", 7), "backgroundColor": "#f8f9fa", "fillStyle": "solid",
                        "strokeWidth": 2, "roughness": 0, "roundness": {"type": 3},
                        "label": {"text": label, "fontSize": SIZE, "fontFamily": FONT, "strokeColor": INK}})
        out.append({"type": "line", "x": x[p], "y": header, "points": [[0, 0], [0, end - header]],
                    "strokeColor": LIFELINE, "strokeStyle": "dashed", "strokeWidth": 1, "roughness": 0})
    bars = [bar for _, bar in sorted(drawing.bars, key=lambda b: b[0])]  # a bar inside another over it
    return out + drawing.back + bars + drawing.tags + drawing.front
