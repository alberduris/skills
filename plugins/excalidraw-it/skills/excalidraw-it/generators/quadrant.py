"""A quadrant chart: points placed on two axes, over a square cut into four named quadrants.

    axes: {x: esfuerzo, y: valor para la skill}   # the generator adds -> for the direction
    quadrants:               # top left, top right, bottom left, bottom right: name, or {name, color}
      - {name: Victorias rápidas, color: teal}
      - Proyectos grandes
      - Relleno
      - Dudosos
    points:                  # name: [x, y], each from 0 to 1
      generadores: [0.85, 0.93]
      packet: [0.28, 0.13]

The quadrant colors default to teal, blue, gray and orange. Each point is a dot
in the color of its quadrant, its name at the first spot right, left, above or
below that stays inside the chart and clear of the other names and dots. Say in
the note where the positions come from.
"""
import math

import fonts
from canvas import FONT, INK, LINE, TITLE_FONT, text
from palette import OPEN_COLOR, shade
from schema import DataError, choice, entries, fields, pair

QUADRANT_SIZE, POINT_SIZE, AXIS_SIZE = 18, 14, 16
SIDE, DOT, INSET = 640, 12, 14
AXIS, FRAME = "#495057", "#adb5bd"
COLORS = ["teal", "blue", "gray", "orange"]


def parsed_quadrants(quadrants):
    if not isinstance(quadrants, list) or len(quadrants) != 4:
        raise DataError(f"quadrants: expected four, top left to bottom right, got {quadrants!r}")
    out = []
    for i, quadrant in enumerate(quadrants):
        where, color = f"quadrants[{i}]", COLORS[i]
        if isinstance(quadrant, dict):
            fields(quadrant, where, ("name",), ("color",))
            color = choice(quadrant.get("color", color), f"{where}.color", OPEN_COLOR)
            quadrant = quadrant["name"]
        out.append((str(quadrant), color))
    return out


def text_box(x, y, content, size, font=FONT):
    return x, y, x + fonts.width(content, font, size) * 1.1, y + size * LINE


def overlaps(a, b, margin=4):
    return a[0] < b[2] + margin and b[0] < a[2] + margin and a[1] < b[3] + margin and b[1] < a[3] + margin


def label_spot(x, y, w, h, taken):
    """Right of the dot, else left, above or below: the first spot inside the chart that clears what is taken,
    or else the one that hits the fewest. Above and below slide sideways to stay inside the chart."""
    centred = min(max(x - w / 2, 4), SIDE - 4 - w)
    spots = [(x + DOT / 2 + 6, y - h / 2), (x - DOT / 2 - 6 - w, y - h / 2), (centred, y - DOT / 2 - 4 - h),
             (centred, y + DOT / 2 + 4)]
    inside = [s for s in spots if 0 <= s[0] and s[0] + w <= SIDE and 0 <= s[1] and s[1] + h <= SIDE] or spots

    def hits(spot):
        return sum(overlaps((spot[0], spot[1], spot[0] + w, spot[1] + h), box) for box in taken)
    return min(inside, key=hits)


def build(data):
    fields(data, "top level", ("axes", "quadrants", "points"))
    axes = fields(data["axes"], "axes", ("x", "y"))
    quadrants = parsed_quadrants(data["quadrants"])
    points = {str(n): pair(at, f"points.{n}", low=0, high=1) for n, at in entries(data["points"], "points").items()}
    half = SIDE / 2
    out, taken = [], []  # taken: the boxes the point names keep clear of
    for i, (name, color) in enumerate(quadrants):
        x, y = (i % 2) * half, (i // 2) * half
        out.append({"type": "rectangle", "x": x, "y": y, "width": half, "height": half, "roughness": 0,
                    "strokeColor": "#ffffff", "strokeWidth": 2, "backgroundColor": shade(color, 1),
                    "fillStyle": "solid", "roundness": None})
        out.append(text(x + INSET, y + INSET, name, QUADRANT_SIZE, shade(color, 7), TITLE_FONT))
        taken.append(text_box(x + INSET, y + INSET, name, QUADRANT_SIZE, TITLE_FONT))
    out.append({"type": "rectangle", "x": 0, "y": 0, "width": SIDE, "height": SIDE, "roughness": 0,
                "strokeColor": FRAME, "strokeWidth": 2, "backgroundColor": "transparent", "roundness": None})
    at = {n: (px * SIDE, (1 - py) * SIDE) for n, (px, py) in points.items()}
    taken += [(x - DOT / 2, y - DOT / 2, x + DOT / 2, y + DOT / 2) for x, y in at.values()]
    dots, names = [], []
    for n, (px, py) in points.items():
        x, y = at[n]
        color = shade(quadrants[(py < 0.5) * 2 + (px >= 0.5)][1], 7)
        dots.append({"type": "ellipse", "x": x - DOT / 2, "y": y - DOT / 2, "width": DOT, "height": DOT,
                     "strokeColor": color, "backgroundColor": color, "fillStyle": "solid", "roughness": 0})
        w, h = fonts.width(n, FONT, POINT_SIZE) * 1.1, POINT_SIZE * LINE
        lx, ly = label_spot(x, y, w, h, taken)
        taken.append((lx, ly, lx + w, ly + h))
        names.append(text(lx, ly, n, POINT_SIZE, INK))
    x_name, y_name = f"{axes['x']}  ->", f"{axes['y']}  ->"
    out.append(text(half, SIDE + 12, x_name, AXIS_SIZE, AXIS, align="center"))
    # turned a quarter to the left about its centre, which sits left of the chart, halfway down
    y_w = fonts.width(y_name, FONT, AXIS_SIZE)
    out.append(text(-12 - AXIS_SIZE * LINE / 2 - y_w / 2, half - AXIS_SIZE * LINE / 2, y_name, AXIS_SIZE, AXIS,
                    angle=3 * math.pi / 2))
    return out + dots + names
