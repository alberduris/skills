"""A stick figure for a person, over a see-through box that lines bind to: the use-case actors and the sequence
actors draw it."""
from canvas import LINE, TITLE_FONT, text

HEAD, ARMS, HIPS, FEET = 26, 38, 62, 92  # from the top of the head: its size, the arms, the hips, the feet
HALF, HAND_GAP = 22, 12                  # half the arm span, and how far the box reaches past each hand
NAME_GAP = 8


def height(size):
    """How tall the figure stands with its name under it."""
    return FEET + NAME_GAP + size * LINE


def hand(right):
    """The fixed point on the box level with the hands, on its right side or its left."""
    return [int(right), ARMS / FEET]


def stick_figure(box_id, name, cx, top, color, size=18, font=TITLE_FONT):
    """The figure centred on cx from `top` down and its name under it, all in one group. Its box, with tempId
    box_id, reaches HAND_GAP past each hand, so a line bound to it does not look like part of an arm."""
    group = [f"actor-{box_id}"]
    stroke = {"strokeColor": color, "strokeWidth": 2, "roughness": 0, "groupIds": group}

    def line(*points):
        return {"type": "line", "x": cx, "y": top, "points": [list(p) for p in points], **stroke}
    return [
        {"type": "rectangle", "tempId": box_id, "x": cx - HALF - HAND_GAP, "y": top, "width": 2 * (HALF + HAND_GAP),
         "height": FEET, "strokeColor": "transparent", "backgroundColor": "transparent", "groupIds": group},
        {"type": "ellipse", "x": cx - HEAD / 2, "y": top, "width": HEAD, "height": HEAD, **stroke},
        line((0, HEAD), (0, HIPS)), line((-HALF, ARMS), (HALF, ARMS)), line((-18, FEET), (0, HIPS), (18, FEET)),
        text(cx, top + FEET + NAME_GAP, name, size, color, font=font, align="center", groupIds=group),
    ]
