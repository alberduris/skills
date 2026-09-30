"""A radar chart: one axis per measure, clockwise from 12 o'clock, one ring per level, and one outline per series.

    axes: [calidad visual, editable, tipos que cubre, poco código, control del layout, sin sorpresas]
    levels: 5                # rings, one per point of the scale; the scores run from 0 to it
    series:                  # name: scores, one per axis, or name: {scores, color}
      create_diagram: {scores: [2, 5, 2, 5, 1, 2], color: violet}
      a mano: [5, 5, 5, 1, 5, 3]

A series takes the next color of violet, teal, orange, blue, pink and green unless
it has its own. Each fills see-through under its outline, with a dot on each
score; every other outline is dashed, so one that runs over another lets it show
through. The rings carry no numbers: say the scale in the note.
"""
import math

import fonts
from canvas import FONT, INK, height, text
from palette import OPEN_COLOR, shade
from schema import DataError, choice, entries, fields, listed, number

AXIS_SIZE, LEGEND_SIZE = 16, 16
R, DOT, SWATCH, ROW, LABEL_OUT = 190, 8, 16, 30, 14
GRID, AXIS_INK = "#dee2e6", "#495057"
COLORS = ["violet", "teal", "orange", "blue", "pink", "green"]


def parsed(data):
    fields(data, "top level", ("axes", "series"), ("levels",))
    axes = [str(axis) for axis in listed(data["axes"], "axes")]
    if len(axes) < 3:
        raise DataError(f"axes: a radar needs 3 axes or more, got {len(axes)}")
    levels = number(data.get("levels", 5), "levels", low=1, whole=True)
    series = []
    for i, (name, value) in enumerate(entries(data["series"], "series").items()):
        where, color = f"series.{name}", COLORS[i % len(COLORS)]
        if isinstance(value, dict):
            fields(value, where, ("scores",), ("color",))
            color = choice(value.get("color", color), f"{where}.color", OPEN_COLOR)
            value = value["scores"]
        scores = [number(s, f"{where}[{j}]", low=0, high=levels) for j, s in enumerate(listed(value, where))]
        if len(scores) != len(axes):
            raise DataError(f"{where}: {len(scores)} scores for {len(axes)} axes")
        series.append((str(name), color, scores))
    return axes, levels, series


def corner(i, count, radius, cx, cy):
    angle = 2 * math.pi * i / count  # clockwise from 12 o'clock
    return cx + radius * math.sin(angle), cy - radius * math.cos(angle)


def polygon(points, cx, cy, **style):
    closed = points + points[:1]
    return {"type": "line", "x": cx, "y": cy, "points": [[x - cx, y - cy] for x, y in closed], "roundness": None,
            "roughness": 0, **style}


def axis_name(i, count, name, cx, cy):
    """The name outside the end of its axis: left-aligned on the right, right-aligned on the left, centred
    at the top and bottom, where it sits above or below the end."""
    x, y = corner(i, count, R + LABEL_OUT, cx, cy)
    h = height(name, AXIS_SIZE)
    side, rise = x - cx, cy - y
    if abs(side) < 1:
        return text(x, y - h if rise > 0 else y, name, AXIS_SIZE, AXIS_INK, align="center")
    return text(x, y - h / 2, name, AXIS_SIZE, AXIS_INK, align="left" if side > 0 else "right")


def build(data):
    axes, levels, series = parsed(data)
    count = len(axes)
    label_w = max(fonts.width(axis, FONT, AXIS_SIZE) for axis in axes)
    cx, cy = label_w + 24 + R, R
    out = []
    for level in range(1, levels + 1):
        ring = [corner(i, count, R * level / levels, cx, cy) for i in range(count)]
        out.append(polygon(ring, cx, cy, strokeColor=GRID, strokeWidth=1))
    for i, axis in enumerate(axes):
        x, y = corner(i, count, R, cx, cy)
        out += [{"type": "line", "x": cx, "y": cy, "points": [[0, 0], [x - cx, y - cy]], "strokeColor": GRID,
                 "strokeWidth": 1, "roughness": 0},
                axis_name(i, count, axis, cx, cy)]
    for k, (_, color, scores) in enumerate(series):
        shape = [corner(i, count, R * s / levels, cx, cy) for i, s in enumerate(scores)]
        # the fill and the outline apart, so the fill can be see-through and the outline not
        out.append(polygon(shape, cx, cy, strokeColor="transparent", backgroundColor=shade(color, 6),
                           fillStyle="solid", opacity=18))
        out.append(polygon(shape, cx, cy, strokeColor=shade(color, 7), strokeWidth=2,
                           strokeStyle="dashed" if k % 2 else "solid"))
        out += [{"type": "ellipse", "x": x - DOT / 2, "y": y - DOT / 2, "width": DOT, "height": DOT,
                 "strokeColor": shade(color, 7), "backgroundColor": shade(color, 7), "fillStyle": "solid",
                 "roughness": 0} for x, y in shape]
    lx, ly = cx + R + label_w + 60, cy - len(series) * ROW / 2
    for j, (name, color, _) in enumerate(series):
        out += [{"type": "rectangle", "x": lx, "y": ly + j * ROW + 2, "width": SWATCH, "height": SWATCH,
                 "strokeColor": shade(color, 7), "backgroundColor": shade(color, 6), "fillStyle": "solid",
                 "roughness": 0, "roundness": {"type": 3}},
                text(lx + SWATCH + 10, ly + j * ROW, name, LEGEND_SIZE, INK)]
    return out
