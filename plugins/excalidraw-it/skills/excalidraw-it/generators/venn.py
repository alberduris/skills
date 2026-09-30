"""A venn diagram: two or three sets as see-through circles of one size, and the items of each region inside it.

    sets:                    # name: color; left and right, or top left, top right and bottom
      legible: blue
      editable: teal
      barato: orange
    items:                   # [sets, item]: the item sits in the region of exactly those sets
      - [[legible, editable], a mano]
      - [[legible, editable, barato], generadores]    # in every set: larger, in Lilita One

The items of one region stack in one block. Each block sits at the spot of its
region where the corners of its box keep the most room from every circle, and the
circles grow until every block has room. Each set is named in its color outside
its circle, on the line from the middle.
"""
import math

import fonts
from canvas import FONT, INK, LINE, TITLE_FONT, height, text
from palette import OPEN_COLOR, shade
from schema import DataError, choice, entries, fields, listed

SET_SIZE, ITEM_SIZE, GOAL_SIZE = 22, 16, 20
MIN_R, MAX_R, R_STEP = 210, 420, 15
SPREAD, OPACITY = 116 / 210, 22  # how far each centre sits from the middle, in radii; the fill's opacity
ANGLES = {2: [180, 0], 3: [-150, -30, 90]}  # where each circle sits around the middle, in degrees
ROOM, STEP, NAME_GAP = 8, 4, 10  # the least room a block keeps from every circle; the search grid; a name's gap


def parsed(data):
    fields(data, "top level", ("sets", "items"))
    sets = [(str(name), choice(color, f"sets.{name}", OPEN_COLOR))
            for name, color in entries(data["sets"], "sets").items()]
    if len(sets) not in ANGLES:
        raise DataError(f"sets: a venn takes 2 or 3 sets, got {len(sets)}")
    index = {name: i for i, (name, _) in enumerate(sets)}
    regions = {}
    for i, item in enumerate(listed(data["items"], "items")):
        if not isinstance(item, list) or len(item) != 2 or not isinstance(item[0], list) or not item[0]:
            raise DataError(f"items[{i}]: expected [[set, …], item], got {item!r}")
        region = frozenset(index[choice(str(s), f"items[{i}]", index)] for s in item[0])
        regions.setdefault(region, []).append(str(item[1]))
    return sets, [(region, "\n".join(lines)) for region, lines in regions.items()]


def along(angle, distance):
    return distance * math.cos(math.radians(angle)), distance * math.sin(math.radians(angle))


def style(region, count):
    """An item in every set is the point of the diagram: larger, in Lilita One."""
    return (GOAL_SIZE, TITLE_FONT) if len(region) == count else (ITEM_SIZE, FONT)


def spot(region, w, h, centres, r):
    """The centre of a w x h box inside the region of exactly these sets, where the corners of the box keep
    the most room from every circle: inside the circles of the sets, outside the others. Also that room."""
    def room(x, y):
        corners = [(x + dx * w / 2, y + dy * h / 2) for dx in (-1, 0, 1) for dy in (-1, 1)]
        return min((r - math.dist(c, o)) if i in region else (math.dist(c, o) - r)
                   for c in corners for i, o in enumerate(centres))
    xs, ys = [o[0] for o in centres], [o[1] for o in centres]
    grid = [(x, y) for x in range(int(min(xs) - r), int(max(xs) + r), STEP)
            for y in range(int(min(ys) - r), int(max(ys) + r), STEP)]
    best = max(grid, key=lambda p: room(*p))
    return best, room(*best)


def layout(blocks, count):
    """The radius, the centres and the spot of each block: the smallest circles where every block has room."""
    boxes = []
    for region, content in blocks:
        size, font = style(region, count)
        boxes.append((fonts.width(content, font, size) * 1.1, height(content, size)))
    for r in range(MIN_R, MAX_R + 1, R_STEP):
        centres = [along(angle, SPREAD * r) for angle in ANGLES[count]]
        spots = [spot(region, w, h, centres, r) for (region, _), (w, h) in zip(blocks, boxes)]
        if all(room >= ROOM for _, room in spots):
            break
    return r, centres, [p for p, _ in spots]


def build(data):
    sets, blocks = parsed(data)
    r, centres, spots = layout(blocks, len(sets))
    fills, outlines, names = [], [], []
    for (name, color), (x, y), angle in zip(sets, centres, ANGLES[len(sets)]):
        circle = {"type": "ellipse", "x": x - r, "y": y - r, "width": 2 * r, "height": 2 * r, "roughness": 0}
        # the fill and the outline apart, so the fill can be see-through and the outline not
        fills.append({**circle, "strokeColor": "transparent", "backgroundColor": shade(color, 6),
                      "fillStyle": "solid", "opacity": OPACITY})
        outlines.append({**circle, "strokeColor": shade(color, 7), "strokeWidth": 2, "backgroundColor": "transparent"})
        # the name's box just outside the circle, on the line from the middle
        w, h = fonts.width(name, TITLE_FONT, SET_SIZE), SET_SIZE * LINE
        reach = abs(math.cos(math.radians(angle))) * w / 2 + abs(math.sin(math.radians(angle))) * h / 2
        lx, ly = along(angle, SPREAD * r + r + NAME_GAP + reach)
        names.append(text(lx, ly - h / 2, name, SET_SIZE, shade(color, 7), font=TITLE_FONT, align="center"))
    items = []
    for (region, content), (x, y) in zip(blocks, spots):
        size, font = style(region, len(sets))
        lines = content.count("\n") + 1
        items.append(text(x, y - lines * size * LINE / 2, content, size, INK, font=font, align="center"))
    return names + fills + outlines + items
