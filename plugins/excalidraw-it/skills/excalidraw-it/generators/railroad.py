"""A railroad diagram: one track per grammar rule, under its name, from a small dot to another.

    rules:                     # name: expression, one track each, top to bottom
      diagrama: [packet, {more: <campo>}]
      campo:
        - choice:              # the first on the track, the others below it
            - [<número>, {opt: ["-", <número>]}]
            - ["+", <número>]
        - ":"
        - <texto>

An expression is a terminal, written as it is typed ("packet", ":"), drawn in a
rounded teal box in Cascadia; a rule in angle brackets (<campo>), in a sharp
white box; a list, for a sequence; {choice: [...]}, for alternatives; {opt: x},
for an optional part; {more: x}, for one or more; {opt: {more: x}} is zero or
more. {t: <x>} writes a terminal that looks like a rule. Quote a terminal YAML
would read as something else: "true", "null", "1.0".
"""
import functools
import math

import fonts
from canvas import FONT, INK, LINE, TITLE_FONT, path, text
from palette import shade
from schema import DataError, entries, fields

CODE, RULE_SIZE, SIZE = 3, 20, 15   # Cascadia for terminals
R, H, GAP, VS, LOOP, PAD, DOT = 12, 34, 20, 14, 22, 12, 10
RULE_GAP = 44                       # between the lowest point of a track and the name of the next rule
TRACK = "#495057"
SKIP = ("seq", ())


def parsed(value, where):
    """An expression as a tuple: ("t", text), ("n", name), ("seq", items), ("choice", items), ("opt", x), ("more", x)."""
    if isinstance(value, bool) or value is None:
        raise DataError(f"{where}: {value!r} is not text; quote it")
    if isinstance(value, (int, float)):
        return "t", str(value)
    if isinstance(value, str):
        if len(value) > 2 and value.startswith("<") and value.endswith(">"):
            return "n", value[1:-1]
        if not value:
            raise DataError(f"{where}: an empty terminal")
        return "t", value
    if isinstance(value, list):
        return "seq", tuple(parsed(item, f"{where}[{i}]") for i, item in enumerate(value))
    if isinstance(value, dict) and len(value) == 1:
        (kind, body), = value.items()
        if kind == "t":
            return "t", str(body)
        if kind == "choice":
            if not isinstance(body, list) or len(body) < 2:
                raise DataError(f"{where}.choice: expected a list of two or more alternatives")
            return "choice", tuple(parsed(item, f"{where}.choice[{i}]") for i, item in enumerate(body))
        if kind in ("opt", "more"):
            return kind, parsed(body, f"{where}.{kind}")
    raise DataError(f"{where}: expected a terminal, a <rule>, a list, or one of choice, opt, more and t; got {value!r}")


@functools.cache
def measure(node):
    """(width, up, down): how far the node reaches along its track and above and below it."""
    kind, body = node
    if kind in ("t", "n"):
        return max(H, fonts.width(body, CODE if kind == "t" else FONT, SIZE) * 1.2 + 2 * PAD), H / 2, H / 2
    if kind == "seq":
        sizes = [measure(item) for item in body]
        return (sum(s[0] for s in sizes) + GAP * max(len(sizes) - 1, 0),
                max((s[1] for s in sizes), default=0), max((s[2] for s in sizes), default=0))
    if kind == "opt":
        return measure(("choice", (SKIP, body)))
    if kind == "more":
        w, up, down = measure(body)
        return w + 2 * R, up, max(down + LOOP, 2 * R)
    offsets = drops(body)
    sizes = [measure(item) for item in body]
    return max(s[0] for s in sizes) + 4 * R, sizes[0][1], offsets[-1] + sizes[-1][2]


@functools.cache
def drops(branches):
    """How far below the track each branch of a choice runs."""
    offsets, below = [0], measure(branches[0])[2]
    for item in branches[1:]:
        _, up, down = measure(item)
        offsets.append(max(offsets[-1] + below + VS + up, offsets[-1] + 2 * R))
        below = down
    return tuple(offsets)


def arc(cx, cy, start, end, steps=8):
    """A quarter circle as points: a curved line overshoots its corners."""
    return [(cx + R * math.cos(math.radians(start + (end - start) * i / steps)),
             cy + R * math.sin(math.radians(start + (end - start) * i / steps))) for i in range(steps + 1)]


def line(points, head=False):
    return path("arrow" if head else "line", points, strokeColor=TRACK, strokeWidth=2, roughness=0,
                **({"endArrowhead": "triangle"} if head else {}))


def track(node, x, y):
    """The elements of a node whose track starts at (x, y)."""
    kind, body = node
    w, up, down = measure(node)
    if kind in ("t", "n"):
        terminal = kind == "t"
        return [{"type": "rectangle", "x": x, "y": y - H / 2, "width": w, "height": H,
                 "strokeColor": shade("teal", 7) if terminal else TRACK,
                 "backgroundColor": shade("teal", 1) if terminal else "#ffffff", "fillStyle": "solid",
                 "strokeWidth": 2, "roughness": 0, **({"roundness": {"type": 3}} if terminal else {}),
                 "label": {"text": body, "fontSize": SIZE, "fontFamily": CODE if terminal else FONT,
                           "strokeColor": shade("teal", 9) if terminal else INK}}]
    if kind == "seq":
        out = []
        for i, item in enumerate(body):
            if i:
                out.append(line([(x, y), (x + GAP, y)]))
                x += GAP
            out += track(item, x, y)
            x += measure(item)[0]
        return out
    if kind == "opt":
        return track(("choice", (SKIP, body)), x, y)
    if kind == "more":
        item_w = w - 2 * R
        right, left, bottom = x + R + item_w, x + R, y + down
        middle = (left + right) / 2
        # the loop back under the item, with an arrowhead halfway along it
        return [line([(x, y), (left, y)]), *track(body, left, y), line([(right, y), (x + w, y)]),
                line([*arc(right, y + R, -90, 0), *arc(right, bottom - R, 0, 90), (middle, bottom)], head=True),
                line([(middle, bottom), *arc(left, bottom - R, 90, 180), *arc(left, y + R, 180, 270)])]
    out, end = [], x + w
    for item, drop in zip(body, drops(body)):
        item_w = measure(item)[0]
        start = x + 2 * R + (w - 4 * R - item_w) / 2
        if item == SKIP:
            out.append(line([(x, y), (end, y)]))
            continue
        if drop:
            out += [line([*arc(x, y + R, -90, 0), *arc(x + 2 * R, y + drop - R, 180, 90), (start, y + drop)]),
                    line([(start + item_w, y + drop), *arc(end - 2 * R, y + drop - R, 90, 0),
                          *arc(end, y + R, 180, 270)])]
        else:
            out += [line([(x, y), (start, y)]), line([(start + item_w, y), (end, y)])]
        out += track(item, start, y + drop)
    return out


def build(data):
    fields(data, "top level", ("rules",))
    rules = {str(name): parsed(value, f"rules.{name}") for name, value in entries(data["rules"], "rules").items()}
    out, y = [], 0
    for name, node in rules.items():
        w, up, down = measure(node)
        out.append(text(0, y, name, RULE_SIZE, font=TITLE_FONT))
        rail = y + RULE_SIZE * LINE + 16 + up
        x = DOT + GAP
        dot = {"type": "ellipse", "width": DOT, "height": DOT, "y": rail - DOT / 2, "strokeColor": TRACK,
               "backgroundColor": TRACK, "fillStyle": "solid", "roughness": 0}
        out += [{**dot, "x": 0}, line([(DOT, rail), (x, rail)]), *track(node, x, rail),
                line([(x + w, rail), (x + w + GAP, rail)]), {**dot, "x": x + w + GAP}]
        y = rail + down + RULE_GAP
    return out
