"""A user journey: stages side by side, their tasks in one row of cards, and a curve through the score of each.

    actors:                    # name: color; a dot per actor under each task, and a legend at the foot
      Operador: blue
      Claude: orange
    stages:                    # stage: {color, tasks}; color is optional
      Pedir:
        color: blue
        tasks:                 # task: [score from 1 to 5, actor, ...], as in Mermaid's journey
          Describir el diagrama: [4, Operador]
          Elegir el tipo: [3, Operador, Claude]

Each stage is a lane as wide as its tasks. A task name longer than a couple of
words breaks into balanced lines; a given \\n stays. Under the cards, a band of
five guide lines numbered 1 to 5 holds the curve, which never runs past a score, with a dot per task from red
at 1 to green at 5.
"""

import math

import fonts
from canvas import FONT, INK, MUTED, height, path, piece, text, wrapped
from palette import OPEN_COLOR, shade
from schema import DataError, choice, entries, fields, listed, number

TASK_SIZE, AXIS_SIZE, LEGEND_SIZE = 16, 14, 16
SCORE_COLORS = {1: "#e03131", 2: "#f76707", 3: "#f59f00", 4: "#74b816", 5: "#2f9e44"}
HEADER, PAD, CARD_GAP, LANE_GAP, MIN_CARD_H = 48, 20, 16, 16, 64
MARK, MARK_GAP, BAND_GAP, SCORE_STEP, DOT = 12, 10, 40, 36, 16
BREAK, WRAP = 100, 150      # a task name wider than BREAK breaks into balanced lines, each within WRAP
GUIDE, CURVE = "#ced4da", "#495057"
NUMBER_X, STEPS = 8, 12    # the scores 1 to 5 sit inside the first lane; the curve takes STEPS points per task
COLORS = ["blue", "violet", "teal", "orange", "grape", "cyan", "green", "pink"]


def parsed(data):
    fields(data, "top level", ("actors", "stages"))
    actors = {str(a): shade(choice(c, f"actors.{a}", OPEN_COLOR), 7)
              for a, c in entries(data["actors"], "actors").items()}
    stages = []
    for i, (stage, value) in enumerate(entries(data["stages"], "stages").items()):
        where = f"stages.{stage}"
        if "," in str(stage):
            raise DataError(f"{where}: a stage name cannot hold a comma")
        fields(value, where, ("tasks",), ("color",))
        color = choice(value.get("color", COLORS[i % len(COLORS)]), f"{where}.color", OPEN_COLOR)
        tasks = []
        for task, spec in entries(value["tasks"], f"{where}.tasks").items():
            spec = listed(spec, f"{where}.tasks.{task}")
            if not spec:
                raise DataError(f"{where}.tasks.{task}: expected [score, actor, ...]")
            score = number(spec[0], f"{where}.tasks.{task}[0]", low=1, high=5, whole=True)
            who = [choice(str(a), f"{where}.tasks.{task}", actors) for a in spec[1:]]
            tasks.append((wrapped(str(task), TASK_SIZE, WRAP, keep=BREAK), score, who))
        stages.append((str(stage), color, tasks))
    return actors, stages


def monotone(points):
    """Points along a smooth curve through `points` that never rises above or dips below the two it runs between,
    so it stays within the band: a monotone cubic (Fritsch and Carlson), flat at each peak and each dip."""
    slopes = [(y1 - y0) / (x1 - x0) for (x0, y0), (x1, y1) in zip(points, points[1:])]
    tangents = [slopes[0]] + [0 if a * b <= 0 else (a + b) / 2 for a, b in zip(slopes, slopes[1:])] + [slopes[-1]]
    for i, slope in enumerate(slopes):
        if slope == 0:
            tangents[i] = tangents[i + 1] = 0
            continue
        a, b = tangents[i] / slope, tangents[i + 1] / slope
        if math.hypot(a, b) > 3:
            tangents[i], tangents[i + 1] = 3 * a * slope / math.hypot(a, b), 3 * b * slope / math.hypot(a, b)
    out = []
    for (x0, y0), (x1, y1), m0, m1 in zip(points, points[1:], tangents, tangents[1:]):
        w = x1 - x0
        for step in range(STEPS):
            t = step / STEPS
            out.append((x0 + t * w, (2 * t ** 3 - 3 * t ** 2 + 1) * y0 + (t ** 3 - 2 * t ** 2 + t) * w * m0
                        + (3 * t ** 2 - 2 * t ** 3) * y1 + (t ** 3 - t ** 2) * w * m1))
    return out + [points[-1]]


def build(data):
    actors, stages = parsed(data)
    names = [name for _, _, tasks in stages for name, _, _ in tasks]
    card_w = max(fonts.width(line, FONT, TASK_SIZE) for name in names for line in name.split("\n")) * 1.2 + 2 * PAD
    card_h = max([MIN_CARD_H] + [height(name, TASK_SIZE) + 24 for name in names])
    band_top = HEADER + PAD + card_h + MARK_GAP + MARK + BAND_GAP
    band_bottom = band_top + 4 * SCORE_STEP
    lane_h = band_bottom + BAND_GAP - HEADER
    out, cards, marks, points, x = [], [], [], [], 0
    for stage, color, tasks in stages:
        width = len(tasks) * card_w + (len(tasks) - 1) * CARD_GAP + 2 * PAD
        out += piece("lane-with-header", titles=stage, colors=color, x=x, y=0, width=width, gap=0, height=lane_h,
                     header_height=HEADER)
        for i, (name, score, who) in enumerate(tasks):
            left = x + PAD + i * (card_w + CARD_GAP)
            middle = left + card_w / 2
            cards.append({"type": "rectangle", "x": left, "y": HEADER + PAD, "width": card_w, "height": card_h,
                          "strokeColor": shade(color, 7), "backgroundColor": "#ffffff", "fillStyle": "solid",
                          "roundness": {"type": 3}, "roughness": 0,
                          "label": {"text": name, "fontSize": TASK_SIZE, "fontFamily": FONT, "strokeColor": INK}})
            row = len(who) * MARK + (len(who) - 1) * 6  # one dot per actor under the card, centred
            for j, actor in enumerate(who):
                marks.append({"type": "ellipse", "x": middle - row / 2 + j * (MARK + 6),
                              "y": HEADER + PAD + card_h + MARK_GAP, "width": MARK, "height": MARK,
                              "strokeColor": actors[actor], "backgroundColor": actors[actor], "fillStyle": "solid",
                              "roughness": 0})
            points.append((middle, band_top + (5 - score) * SCORE_STEP, score))
        x += width + LANE_GAP
    right = x - LANE_GAP
    guide_x = NUMBER_X + fonts.width("5", FONT, AXIS_SIZE) + 8
    for score in range(1, 6):
        y = band_top + (5 - score) * SCORE_STEP
        out.append({"type": "line", "x": guide_x, "y": y, "points": [[0, 0], [right - guide_x, 0]],
                    "strokeColor": GUIDE, "strokeWidth": 1, "strokeStyle": "dashed", "roughness": 0})
        out.append(text(NUMBER_X, y - AXIS_SIZE * 0.65, str(score), AXIS_SIZE, MUTED))
    if len(points) > 1:
        out.append(path("line", monotone([(px, py) for px, py, _ in points]), roundness=None, strokeColor=CURVE,
                        strokeWidth=2, roughness=0))
    out += [{"type": "ellipse", "x": px - DOT / 2, "y": py - DOT / 2, "width": DOT, "height": DOT,
             "strokeColor": SCORE_COLORS[s], "backgroundColor": SCORE_COLORS[s], "fillStyle": "solid",
             "roughness": 0} for px, py, s in points]
    out += cards + marks
    legend_y, lx = HEADER + lane_h + 20, 0
    for actor, color in actors.items():
        out.append({"type": "ellipse", "x": lx, "y": legend_y + 4, "width": MARK, "height": MARK,
                    "strokeColor": color, "backgroundColor": color, "fillStyle": "solid", "roughness": 0})
        out.append(text(lx + MARK + 8, legend_y, actor, LEGEND_SIZE))
        lx += MARK + 8 + fonts.width(actor, FONT, LEGEND_SIZE) + 28
    return out
