"""A timeline: periods at equal steps on an axis, each with a column of event cards under it.

    periods:                 # period: events, or period: {color, events}; an event is name: what
      "1991":
        Graphviz: grafos desde texto, con el lenguaje dot
      "2021":
        color: orange
        events:
          Excalidraw+: Excalidraw en equipo, de pago
          tldraw: otra pizarra en el navegador
          Figma: null        # an event with no description

The periods sit at equal steps whatever the time between them. Their colors
default to blue, cyan, teal, green, orange, red, grape, violet and pink in turn.
A description breaks into lines at most 200 px wide, at the \\n you write and
between words; every card takes the width of the widest, and is one group.
"""
import fonts
from canvas import FONT, INK, LINE, TITLE_FONT, height, text
from palette import OPEN_COLOR, shade
from schema import choice, entries, fields

YEAR_SIZE, NAME_SIZE, WHAT_SIZE = 24, 16, 14
DOT, STEM, CARD_GAP, COLUMN_GAP, PAD, WRAP = 20, 40, 16, 32, 12, 200
AXIS = "#495057"
COLORS = ["blue", "cyan", "teal", "green", "orange", "red", "grape", "violet", "pink"]


def wrapped(what):
    """The description in lines of at most WRAP px, broken at its own line breaks and between words."""
    lines = []
    for paragraph in what.split("\n"):
        line = ""
        for word in paragraph.split(" "):
            candidate = f"{line} {word}" if line else word
            if line and fonts.width(candidate, FONT, WHAT_SIZE) > WRAP:
                lines.append(line)
                candidate = word
            line = candidate
        lines.append(line)
    return "\n".join(lines)


def parsed(data):
    fields(data, "top level", ("periods",))
    periods = []
    for i, (period, value) in enumerate(entries(data["periods"], "periods").items()):
        where, color = f"periods.{period}", COLORS[i % len(COLORS)]
        if isinstance(value, dict) and "events" in value:
            fields(value, where, ("events",), ("color",))
            color = choice(value.get("color", color), f"{where}.color", OPEN_COLOR)
            value = value["events"]
        events = entries(value, f"{where}.events")
        periods.append((str(period), color, [(str(n), wrapped(str(w)) if w else "") for n, w in events.items()]))
    return periods


def card_height(what):
    return PAD + NAME_SIZE * LINE + (4 + height(what, WHAT_SIZE) if what else 0) + PAD


def build(data):
    periods = parsed(data)
    card_w = max(max(fonts.width(n, TITLE_FONT, NAME_SIZE), fonts.width(w, FONT, WHAT_SIZE) if w else 0)
                 for _, _, events in periods for n, w in events) * 1.2 + 2 * PAD
    out = []
    for i, (period, color, events) in enumerate(periods):
        stroke = shade(color, 7)
        left = i * (card_w + COLUMN_GAP)
        middle = left + card_w / 2
        out.append(text(middle, -DOT / 2 - 12 - YEAR_SIZE * LINE, period, YEAR_SIZE, stroke, TITLE_FONT,
                        align="center"))
        out.append({"type": "ellipse", "x": middle - DOT / 2, "y": -DOT / 2, "width": DOT, "height": DOT,
                    "strokeColor": stroke, "backgroundColor": stroke, "fillStyle": "solid", "roughness": 0})
        out.append({"type": "line", "x": middle, "y": DOT / 2, "points": [[0, 0], [0, STEM - DOT / 2]],
                    "strokeColor": stroke, "strokeWidth": 2, "roughness": 0})
        top = STEM
        for j, (name, what) in enumerate(events):
            group = [f"event-{i}-{j}"]
            card_h = card_height(what)
            out.append({"type": "rectangle", "x": left, "y": top, "width": card_w, "height": card_h,
                        "strokeColor": stroke, "backgroundColor": "#ffffff", "fillStyle": "solid",
                        "roundness": {"type": 3}, "strokeWidth": 2, "roughness": 0, "groupIds": group})
            out.append(text(left + PAD, top + PAD, name, NAME_SIZE, stroke, TITLE_FONT, groupIds=group))
            if what:
                out.append(text(left + PAD, top + PAD + NAME_SIZE * LINE + 4, what, WHAT_SIZE, INK, groupIds=group))
            top += card_h + CARD_GAP
    end = len(periods) * (card_w + COLUMN_GAP)
    # the axis goes first, under the dots
    return [{"type": "arrow", "x": -COLUMN_GAP, "y": 0, "points": [[0, 0], [end + COLUMN_GAP, 0]],
             "strokeColor": AXIS, "strokeWidth": 2, "roughness": 0, "roundness": None,
             "startArrowhead": None, "endArrowhead": "arrow"}] + out
