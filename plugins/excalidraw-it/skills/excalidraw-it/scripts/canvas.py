"""What the generators share: a text, its lines and its numbers, the title and note of a diagram, a node box, a
bound arrow and a path, the spare colors of a cycle, and the pieces."""
import argparse
import contextlib
import functools
import io
from itertools import cycle

import fonts
from modules import SKILL_DIR, load
from palette import shade

INK, MUTED = "#1e1e1e", "#868e96"
FONT, TITLE_FONT = 5, 7  # Excalifont, Lilita One
LINE = 1.25              # the height of a line of text, in font sizes
TITLE_SIZE, NOTE_SIZE, NOTE_GAP, HEADER_GAP = 30, 17, 6, 48


def text(x, y, content, size, color=INK, font=FONT, align="left", **extra):
    """A standalone text. `add` reads x as its left edge, its centre or its right edge, after textAlign."""
    element = {"type": "text", "x": x, "y": y, "text": content, "fontSize": size, "fontFamily": font,
               "strokeColor": color, **extra}
    if align != "left":
        element["textAlign"] = align
    return element


def height(content, size):
    return (content.count("\n") + 1) * size * LINE


def wrapped(content, size, widest, keep=None, font=FONT):
    """The text in as few lines as keep each within `widest`, split at spaces and balanced so the longest is as
    short as it can be. A text with a \\n of its own stays as written, and so does one within `keep`, which is
    `widest` by default."""
    if "\n" in content or fonts.width(content, font, size) <= (widest if keep is None else keep):
        return content
    words = content.split(" ")

    def filled(limit):
        """Greedy: each line takes words while it stays within the limit."""
        lines = [words[0]]
        for word in words[1:]:
            if fonts.width(f"{lines[-1]} {word}", font, size) <= limit:
                lines[-1] += f" {word}"
            else:
                lines.append(word)
        return lines

    # past `keep` it takes two lines at least; the narrowest limit that needs no more lines balances them
    count = max(2, len(filled(widest)))
    low, high = max(fonts.width(word, font, size) for word in words), max(widest, fonts.width(content, font, size))
    for _ in range(30):
        middle = (low + high) / 2
        low, high = (low, middle) if len(filled(middle)) <= count else (middle, high)
    return "\n".join(filled(high))


def shown(value, thousands, decimals=2, trim=True):
    """The value with its thousands grouped and `decimals` decimals, less their trailing zeros when trim:
    4.100, 2,5. The decimal separator is the other of . and ,."""
    out = f"{value:,.{decimals}f}"
    if trim and decimals:
        out = out.rstrip("0").rstrip(".")
    return out if thousands == "," else out.translate(str.maketrans(",.", ".,"))


def header(title, note, left, top):
    """The title in Lilita One and the note in gray under it, ending HEADER_GAP above `top`."""
    out, y = [], top - HEADER_GAP
    if note:
        y -= height(note, NOTE_SIZE)
        out.append(text(left, y, note, NOTE_SIZE, MUTED))
        y -= NOTE_GAP
    if title:
        y -= height(title, TITLE_SIZE)
        out.append(text(left, y, title, TITLE_SIZE, font=TITLE_FONT))
    return out


def tinted(n, box, color, label=None, size=None, external=False, **extra):
    """A rounded node box (x, y, width, height), bordered in shade 7 of its color, filled with shade 1 and labelled
    in shade 9; an external one dashed, with no fill and its label in ink."""
    x, y, w, h = box
    out = {"type": "rectangle", "tempId": n, "x": x, "y": y, "width": w, "height": h,
           "strokeColor": shade(color, 7), "strokeWidth": 2, "roughness": 0, "roundness": {"type": 3},
           "strokeStyle": "dashed" if external else "solid",
           "backgroundColor": "transparent" if external else shade(color, 1), "fillStyle": "solid", **extra}
    if label is not None:
        out["label"] = {"text": label, "fontSize": size, "fontFamily": FONT,
                        "strokeColor": INK if external else shade(color, 9)}
    return out


def path(kind, points, **style):
    """A line or an arrow through `points`, written where they sit on the canvas."""
    x0, y0 = points[0]
    return {"type": kind, "x": x0, "y": y0, "points": [[x - x0, y - y0] for x, y in points], **style}


def arrow(a, box_a, start, b, box_b, end, **style):
    """A straight arrow bound from the fixed point `start` of a to `end` of b; a box is (x, y, width, height)."""
    (ax, ay, aw, ah), (bx, by, bw, bh) = box_a, box_b
    sx, sy = ax + start[0] * aw, ay + start[1] * ah
    ex, ey = bx + end[0] * bw, by + end[1] * bh
    return {"type": "arrow", "x": sx, "y": sy, "points": [[0, 0], [ex - sx, ey - sy]],
            "strokeWidth": 2, "roughness": 0, "roundness": None, "startArrowhead": None, "endArrowhead": "arrow",
            "startBinding": {"elementId": a, "fixedPoint": list(start), "mode": "inside"},
            "endBinding": {"elementId": b, "fixedPoint": list(end), "mode": "inside"}, **style}


def spare_colors(entries_map, colors):
    """The colors for the entries with none: `colors` in turn, skipping those some entry chose as {color: …}."""
    chosen = {value.get("color") for value in entries_map.values() if isinstance(value, dict)}
    return cycle([c for c in colors if c not in chosen] or colors)


@functools.cache
def _piece_module(piece_id):
    return load(SKILL_DIR / "pieces" / f"{piece_id.replace('-', '_')}.py")


def piece(piece_id, **options):
    """The elements of a piece, from options named as its flags: group_id="x" is --group-id x, True a bare flag."""
    module = _piece_module(piece_id)
    parser = argparse.ArgumentParser(prog=piece_id)
    module.add_arguments(parser)
    argv = []
    for name, value in options.items():
        flag = "--" + name.replace("_", "-")
        if value is True:
            argv.append(flag)
        elif value not in (None, False):
            argv.append(f"{flag}={value}")
    args = parser.parse_args(argv)
    with contextlib.redirect_stderr(io.StringIO()):  # the free area a piece prints serves only a hand drawing
        return module.build(args)
