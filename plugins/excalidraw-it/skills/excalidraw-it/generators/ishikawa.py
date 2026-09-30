"""An ishikawa diagram: the effect on the right, the spine into it, and the categories of causes as slanted bones.

    effect: "El diagrama\\nsale slop"
    categories:                # category: [causes], or category: {color, causes}; in pairs from the head
      Texto: [recortado al final, una palabra partida]      # the first of each pair above the spine
      Flechas: {color: teal, causes: [un extremo suelto, tapada por su etiqueta]}

The categories go in pairs, nearest the head first: the first of each pair above
the spine and the second below, meeting it at one point. A category with no color
takes the next of blue, teal, violet, orange, grape, cyan, green and pink that no
category chose. Every
bone is as tall as the longest list of causes needs, and each pair sits left of
the one nearer the head by the widest cause of that pair.
"""
import math

import fonts
from canvas import FONT, INK, LINE, MUTED, TITLE_FONT, height, spare_colors, text
from palette import OPEN_COLOR, shade
from schema import choice, entries, fields, listed

BONE_SIZE, CAUSE_SIZE, HEAD_SIZE = 18, 16, 22
STEP, SLANT, UNDER, GAP, PAD = 40, math.radians(62), 26, 40, 14
BONE, SPINE = "#495057", "#343a40"
HEAD_GAP = 90  # from the meeting point of the nearest pair to the effect
COLORS = ["blue", "teal", "violet", "orange", "grape", "cyan", "green", "pink"]
STROKE = {"strokeWidth": 2, "roughness": 0}


def parsed(data):
    fields(data, "top level", ("effect", "categories"))
    categories, spare = [], spare_colors(entries(data["categories"], "categories"), COLORS)
    for name, value in data["categories"].items():
        where, color = f"categories.{name}", None
        if isinstance(value, dict):
            fields(value, where, (), ("color", "causes"))
            color = choice(value["color"], f"{where}.color", OPEN_COLOR) if "color" in value else None
            value = value.get("causes")
        categories.append((str(name), color or next(spare), [str(cause) for cause in listed(value, where)]))
    return str(data["effect"]), categories


def box(content, font, size):
    return fonts.width(content, font, size) * 1.2 + 2 * PAD, height(content, size) + 2 * PAD


def build(data):
    effect, categories = parsed(data)
    rise = (max(len(causes) for _, _, causes in categories) + 1) * STEP  # how far a bone reaches from the spine
    run = rise / math.tan(SLANT)
    label_h = max(box(name, TITLE_FONT, BONE_SIZE)[1] for name, _, _ in categories)
    spine_y = label_h + rise
    head_w, head_h = box(effect, TITLE_FONT, HEAD_SIZE)
    # each pair of bones meets the spine left of the pair nearer the head, clear of that pair's causes
    pairs = [categories[i:i + 2] for i in range(0, len(categories), 2)]
    reach = [max([fonts.width(c, FONT, CAUSE_SIZE) + UNDER for _, _, causes in pair for c in causes], default=0)
             for pair in pairs]
    labels = [max(box(name, TITLE_FONT, BONE_SIZE)[0] for name, _, _ in pair) for pair in pairs]
    attach, x = [], 0
    for j, pair in enumerate(pairs):
        x -= max(reach[j - 1], (labels[j - 1] + labels[j]) / 2) + GAP if j else 0
        attach += [x] * len(pair)
    shift = run + max(reach[-1], labels[-1] / 2) + 20 - attach[-1]
    attach = [a + shift for a in attach]
    head_x = attach[0] + HEAD_GAP
    out = [{"type": "arrow", "x": 0, "y": spine_y, "points": [[0, 0], [head_x - 4, 0]], "strokeColor": SPINE,
            "strokeWidth": 4, "roughness": 0, "endArrowhead": "triangle"},
           {"type": "rectangle", "x": head_x, "y": spine_y - head_h / 2, "width": head_w, "height": head_h,
            "strokeColor": shade("red", 7), "backgroundColor": shade("red", 1), "fillStyle": "solid", **STROKE,
            "roundness": {"type": 3},
            "label": {"text": effect, "fontSize": HEAD_SIZE, "fontFamily": TITLE_FONT, "strokeColor": shade("red", 9)}}]
    for i, ((name, color, causes), sx) in enumerate(zip(categories, attach)):
        up = -1 if i % 2 == 0 else 1  # the first bone of each pair above the spine
        end_y = spine_y + up * rise
        w, h = box(name, TITLE_FONT, BONE_SIZE)
        out += [{"type": "line", "x": sx, "y": spine_y, "points": [[0, 0], [-run, up * rise]], "strokeColor": BONE,
                 **STROKE},
                {"type": "rectangle", "x": sx - run - w / 2, "y": end_y - h if up < 0 else end_y, "width": w,
                 "height": h, "strokeColor": shade(color, 7), "backgroundColor": shade(color, 1), "fillStyle": "solid",
                 **STROKE, "roundness": {"type": 3},
                 "label": {"text": name, "fontSize": BONE_SIZE, "fontFamily": TITLE_FONT,
                           "strokeColor": shade(color, 9)}}]
        # causes from the label down to the spine, each underlined up to the bone, its text on the line
        for k, cause in enumerate(causes):
            y = end_y - up * (k + 1) * STEP
            on_bone = sx - run * abs(y - spine_y) / rise
            width = fonts.width(cause, FONT, CAUSE_SIZE)
            out += [{"type": "line", "x": on_bone - width - UNDER, "y": y, "points": [[0, 0], [width + UNDER, 0]],
                     "strokeColor": MUTED, "strokeWidth": 1, "roughness": 0},
                    text(on_bone - width - UNDER + 2, y - CAUSE_SIZE * LINE - 2, cause, CAUSE_SIZE, INK)]
    return out
