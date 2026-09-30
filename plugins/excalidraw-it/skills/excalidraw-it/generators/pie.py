"""A pie chart: one slice per part, clockwise from 12 o'clock, sorted from the largest, with a legend.

    slices:                  # name: value, or name: {value, color}
      textos: 412
      rectángulos: {value: 230, color: teal}
    sort: false              # keeps the order given; true by default
    thousands: ","           # the thousands separator, "." by default; the decimal one is the other

A slice takes the next color of blue, teal, violet, orange, yellow, pink, grape,
cyan, lime, red, indigo and green unless it has its own. Its percentage sits in
white inside it when it is 4 % or more; the legend on the right gives each value.
Say the total in the note.
"""
import math

import fonts
from canvas import FONT, INK, LINE, MUTED, shown, text
from palette import OPEN_COLOR, shade
from schema import DataError, choice, entries, fields, number

LABEL_SIZE, LEGEND_SIZE = 16, 16
R, ARC_STEP = 170, 3     # the radius, and the degrees between two samples of an arc
INSIDE, LEAST = 0.64, 4  # where a percentage sits, in radii, and the least share that shows one
SWATCH, ROW, LEGEND_GAP = 16, 30, 60
COLORS = ["blue", "teal", "violet", "orange", "yellow", "pink", "grape", "cyan", "lime", "red", "indigo", "green"]


def parsed_slices(slices):
    out = []
    for i, (name, value) in enumerate(entries(slices, "slices").items()):
        where, color = f"slices.{name}", COLORS[i % len(COLORS)]
        if isinstance(value, dict):
            fields(value, where, ("value",), ("color",))
            color = choice(value.get("color", color), f"{where}.color", OPEN_COLOR)
            value = value["value"]
        out.append((str(name), number(value, where, low=0), color))
    if not sum(value for _, value, _ in out):
        raise DataError("slices: every value is 0")
    return out


def wedge(start, sweep):
    """A slice as a closed line: the centre, then its arc every ARC_STEP degrees, clockwise from 12 o'clock."""
    steps = max(2, math.ceil(sweep / ARC_STEP))
    arc = [start + sweep * i / steps for i in range(steps + 1)]
    return [[0, 0]] + [[R * math.sin(math.radians(a)), -R * math.cos(math.radians(a))] for a in arc] + [[0, 0]]


def build(data):
    fields(data, "top level", ("slices",), ("sort", "thousands"))
    thousands = choice(data.get("thousands", "."), "thousands", (".", ","))
    slices = parsed_slices(data["slices"])
    if data.get("sort", True):
        slices.sort(key=lambda s: -s[1])
    total = sum(value for _, value, _ in slices)
    cx, cy = R, R
    out, labels, start = [], [], 0
    for name, value, color in slices:
        sweep = 360 * value / total
        if sweep:
            out.append({"type": "line", "x": cx, "y": cy, "points": wedge(start, sweep), "roundness": None,
                        "strokeColor": "#ffffff", "strokeWidth": 2, "roughness": 0,
                        "backgroundColor": shade(color, 6), "fillStyle": "solid"})
        share = 100 * value / total
        if share >= LEAST:
            middle = math.radians(start + sweep / 2)
            x, y = cx + INSIDE * R * math.sin(middle), cy - INSIDE * R * math.cos(middle)
            labels.append(text(x, y - LABEL_SIZE * LINE / 2, f"{share:.0f} %", LABEL_SIZE, "#ffffff", align="center"))
        start += sweep
    legend_x, legend_y = 2 * R + LEGEND_GAP, cy - len(slices) * ROW / 2
    name_w = max(fonts.width(name, FONT, LEGEND_SIZE) for name, _, _ in slices)
    value_w = max(fonts.width(shown(value, thousands), FONT, LEGEND_SIZE) for _, value, _ in slices)
    for i, (name, value, color) in enumerate(slices):
        y = legend_y + i * ROW
        out += [{"type": "rectangle", "x": legend_x, "y": y + 2, "width": SWATCH, "height": SWATCH,
                 "strokeColor": shade(color, 6), "backgroundColor": shade(color, 6), "fillStyle": "solid",
                 "roughness": 0, "roundness": {"type": 3}},
                text(legend_x + SWATCH + 10, y, name, LEGEND_SIZE, INK),
                text(legend_x + SWATCH + 10 + name_w + 24 + value_w, y, shown(value, thousands), LEGEND_SIZE, MUTED,
                     align="right")]
    return out + labels
