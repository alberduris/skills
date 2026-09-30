"""A bar chart: one bar per category on a value axis, sorted from the largest.

    bars:                    # category: value, or category: {value, color}
      architecture: 4100
      kanban: {value: 1400, color: teal}     # a bar that stands for something else
    sort: false              # keeps the order given, as for months; true by default
    reference: {label: media, value: mean}   # a red dashed line under the bars; value a number or mean
    thousands: ","           # the thousands separator, "." by default; the decimal one is the other

The axis runs from 0 to a round number at or above the largest value, in 3 to 6
steps, with a dashed grid line at each. A bar is blue unless it has a color. Its
value sits in white inside its top, or above it when the bar is too short.
"""
import math

import fonts
from canvas import FONT, INK, LINE, MUTED, shown, text
from palette import OPEN_COLOR, shade
from schema import choice, entries, fields, number

TICK_SIZE, VALUE_SIZE, CATEGORY_SIZE = 14, 14, 15
HEIGHT = 300                     # of the axis, from 0 to its top
MIN_BAR, BAR_PAD, PITCH_PAD = 44, 12, 24
GRID, AXIS, COLOR = "#dee2e6", "#495057", "blue"
LINE_STYLE = {"strokeWidth": 2, "roughness": 0}


def axis_top(largest, integers):
    """A round top at or above the largest value, and its step: 1, 2, 2.5 or 5 times a power of ten."""
    power = 10 ** math.floor(math.log10(largest / 6))
    for scale in (1, 2, 2.5, 5, 10):
        step = scale * power
        if integers and not float(step).is_integer():
            continue
        if math.ceil(largest / step) <= 6:
            return math.ceil(largest / step) * step, step
    raise AssertionError("a step of 10 times the power always fits")


def parsed_bars(bars):
    out = []
    for name, value in entries(bars, "bars").items():
        where = f"bars.{name}"
        color = COLOR
        if isinstance(value, dict):
            fields(value, where, ("value",), ("color",))
            color = choice(value.get("color", COLOR), f"{where}.color", OPEN_COLOR)
            value = value["value"]
        out.append((str(name), number(value, where, low=0), color))
    return out


def parsed_reference(reference, values):
    if reference is None:
        return None
    fields(reference, "reference", ("label", "value"))
    value = reference["value"]
    if value == "mean":
        value = sum(values) / len(values)
        value = round(value) if all(float(v).is_integer() for v in values) else round(value, 2)
    return str(reference["label"]), number(value, "reference.value", low=0)


def build(data):
    fields(data, "top level", ("bars",), ("sort", "reference", "thousands"))
    thousands = choice(data.get("thousands", "."), "thousands", (".", ","))
    bars = parsed_bars(data["bars"])
    if data.get("sort", True):
        bars.sort(key=lambda bar: -bar[1])
    values = [value for _, value, _ in bars]
    reference = parsed_reference(data.get("reference"), values)
    integers = all(float(v).is_integer() for v in values + ([reference[1]] if reference else []))
    top, step = axis_top(max(values + ([reference[1]] if reference else [])) or 1, integers)
    scale = HEIGHT / top

    bar = max(MIN_BAR, max(fonts.width(shown(v, thousands), FONT, VALUE_SIZE) for v in values) + 2 * BAR_PAD)
    pitch = max(bar, max(fonts.width(name, FONT, CATEGORY_SIZE) for name, _, _ in bars)) + PITCH_PAD
    width, base = len(bars) * pitch, HEIGHT
    out = []
    for i in range(round(top / step) + 1):
        y = base - i * step * scale
        if i:
            out.append({"type": "line", "x": 0, "y": y, "points": [[0, 0], [width, 0]], "strokeColor": GRID,
                        "strokeWidth": 1, "strokeStyle": "dashed", "roughness": 0})
        out.append(text(-10, y - TICK_SIZE * LINE / 2, shown(i * step, thousands), TICK_SIZE, MUTED, align="right"))
    if reference:  # under the bars, which hide it where it crosses them
        label, value = reference
        y, red = base - value * scale, shade("red", 7)
        out.append({"type": "line", "x": 0, "y": y, "points": [[0, 0], [width, 0]], "strokeColor": red,
                    "strokeStyle": "dashed", **LINE_STYLE})
        out.append(text(width + 10, y - TICK_SIZE * LINE / 2, f"{label} {shown(value, thousands)}", TICK_SIZE, red))
    for i, (name, value, color) in enumerate(bars):
        middle, h = i * pitch + pitch / 2, value * scale
        if h:
            out.append({"type": "rectangle", "x": middle - bar / 2, "y": base - h, "width": bar, "height": h,
                        "strokeColor": shade(color, 7), "backgroundColor": shade(color, 6), "fillStyle": "solid",
                        **LINE_STYLE})
        inside = h >= VALUE_SIZE * LINE + 16
        y = base - h + 8 if inside else base - h - 8 - VALUE_SIZE * LINE
        out.append(text(middle, y, shown(value, thousands), VALUE_SIZE, "#ffffff" if inside else shade(color, 9),
                        align="center"))
        out.append(text(middle, base + 10, name, CATEGORY_SIZE, INK, align="center"))
    out.append({"type": "line", "x": 0, "y": base, "points": [[0, 0], [width, 0]], "strokeColor": AXIS, **LINE_STYLE})
    return out
