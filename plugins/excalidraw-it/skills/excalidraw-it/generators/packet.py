"""A packet diagram: the fields of a header, in rows of a fixed number of bits.

    bits: 32                 # bits per row: 8, 16, 32 or 64; 32 by default
    fields:                  # [bits, name] or [bits, name, group], in order from bit 0
      - [16, Puerto de origen, extremos]
      - [1, SYN, control]
      - [32, "Opciones, de 0 a 40 bytes", opcional]
    groups:                  # group: color, or group: {color, dashed}; dashed marks a field of variable length
      extremos: blue
      control: orange
      opcional: {color: gray, dashed: true}
    words: {bit: bit}        # the word over the ruler

A field that crosses the end of a row goes on in the next one. Its name is
written across it, or turned a quarter to the left when it does not fit; the rows
grow tall enough for the longest turned name. The numbers left of the rows are
the byte where each row starts. The legend lists the groups, and a field with no
group is blue and stays out of it.
"""
import math

import fonts
from canvas import FONT, LINE, MUTED, text
from palette import OPEN_COLOR, shade
from schema import DataError, choice, entries, fields, listed, number

SIZE, SMALL, RULER = 15, 13, 11
BIT, MIN_ROW, PAD, SWATCH = 30, 56, 8, 32
BORDER, COLOR = "#495057", "blue"
WORDS = {"bit": "bit"}


def parsed(data):
    fields(data, "top level", ("fields",), ("bits", "groups", "words"))
    wide = choice(data.get("bits", 32), "bits", (8, 16, 32, 64))
    groups = {}
    for g, value in entries(data.get("groups"), "groups", optional=True).items():
        where, dashed = f"groups.{g}", False
        if isinstance(value, dict):
            fields(value, where, ("color",), ("dashed",))
            dashed = bool(value.get("dashed"))
            value = value["color"]
        groups[str(g)] = choice(value, where, OPEN_COLOR), dashed
    out = []
    for i, field in enumerate(listed(data["fields"], "fields")):
        where = f"fields[{i}]"
        if not isinstance(field, list) or len(field) not in (2, 3):
            raise DataError(f"{where}: expected [bits, name] or [bits, name, group], got {field!r}")
        group = choice(str(field[2]), f"{where}.group", groups) if len(field) == 3 else None
        out.append((number(field[0], f"{where}.bits", low=1, whole=True), str(field[1]), group))
    if not out:
        raise DataError("fields: expected at least one")
    words = {**WORDS, **fields(data.get("words") or {}, "words", (), tuple(WORDS))}
    return wide, out, groups, words


def segments(packet, wide):
    """(row, first bit, last bit, name, group) for each row a field covers."""
    start = 0
    for bits, name, group in packet:
        end = start + bits - 1
        for row in range(start // wide, end // wide + 1):
            yield row, max(start, row * wide) % wide, min(end, row * wide + wide - 1) % wide, name, group
        start = end + 1


def across(name, width):
    return fonts.width(name, FONT, SIZE) * 1.2 + 2 * PAD <= width


def build(data):
    wide, packet, groups, words = parsed(data)
    parts = list(segments(packet, wide))
    turned = [fonts.width(name, FONT, SMALL) * 1.1 for _, first, last, name, _ in parts
              if not across(name, (last - first + 1) * BIT)]
    row_h = max([MIN_ROW] + [w + 2 * PAD for w in turned])
    left = fonts.width(words["bit"], FONT, SMALL) + 16
    rows_top = RULER * LINE + 6
    # add reads the x of a right-aligned or centred text as its right edge or its centre
    out = [text(left - 10, -(SMALL - RULER) * LINE / 2, words["bit"], SMALL, MUTED, align="right")]
    out += [text(left + b * BIT + BIT / 2, 0, str(b), RULER, MUTED, align="center") for b in range(wide)]
    rows = 0
    for row, first, last, name, group in parts:
        rows = max(rows, row + 1)
        x, y, w = left + first * BIT, rows_top + row * row_h, (last - first + 1) * BIT
        color, dashed = groups[group] if group else (COLOR, False)
        field = {"type": "rectangle", "x": x, "y": y, "width": w, "height": row_h, "strokeColor": BORDER,
                 "backgroundColor": shade(color, 1), "fillStyle": "solid", "roughness": 0,
                 "strokeStyle": "dashed" if dashed else "solid"}
        ink = shade(color, 9)
        if across(name, w):
            out.append({**field, "label": {"text": name, "fontSize": SIZE, "fontFamily": FONT, "strokeColor": ink}})
        else:  # too narrow to write across: turned a quarter to the left, centred on the field
            out += [field, text(x + w / 2, y + row_h / 2 - SMALL * LINE / 2, name, SMALL, ink, align="center",
                                angle=3 * math.pi / 2)]
    for row in range(rows):
        out.append(text(left - 10, rows_top + row * row_h + row_h / 2 - SMALL * LINE / 2, str(row * wide // 8),
                        SMALL, MUTED, align="right"))
    # the legend under the rows, one swatch per group
    x, y = left, rows_top + rows * row_h + 40
    for g, (color, dashed) in groups.items():
        out += [{"type": "rectangle", "x": x, "y": y, "width": SWATCH, "height": 16, "strokeColor": BORDER,
                 "backgroundColor": shade(color, 1), "fillStyle": "solid", "roughness": 0,
                 "strokeStyle": "dashed" if dashed else "solid"},
                text(x + SWATCH + 8, y + 8 - SMALL * LINE / 2, g, SMALL, MUTED)]
        x += SWATCH + 8 + fonts.width(g, FONT, SMALL) + 32
    return out
