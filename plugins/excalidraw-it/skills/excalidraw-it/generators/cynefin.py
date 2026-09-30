"""A Cynefin diagram: the four domains in their fixed corners around confusion, with what falls in each.

    domains:                   # the items of each domain, top to bottom; a domain may be left out
      complex: [qué hace que un diagrama no sea slop, qué tipos merecen generador]
      complicated: [colocar etiquetas sin choques]
      chaotic: [la API key, pegada en el chat]
      clear: [pasar lint --fix]
    confusion: ["state: ¿Mermaid o a mano?"]    # what fits no domain yet, in the middle
    transitions:               # [from, to, words], between two domains that share a boundary
      - [complex, complicated, el patrón se repite]
      - [clear, chaotic, complacencia]         # red: it falls off the cliff
    words:                     # each domain's name and how to act in it, and the name of confusion
      clear: [Obvio, "percibir, categorizar, responder"]

The corners are fixed as in Mermaid: complex top left, complicated top right,
chaotic bottom left, clear bottom right. You say what falls in each domain and
where things move; the generator sizes the diagram so each domain holds its
items, wrapping a long one onto more lines, and draws each transition across
its boundary, a second one across the same boundary further out. Quote an item
with ": " in it.
"""
import math

import fonts
from canvas import FONT, INK, LINE, TITLE_FONT, height, path, text, wrapped
from palette import shade
from schema import DataError, choice, entries, fields, listed

SIZE, NAME_SIZE, HOW_SIZE, CONFUSION_SIZE = 15, 24, 14, 20
MIN_W, MIN_H = 1000, 680
EDGE, NAME_GAP, BADGE_GAP, PAD_X, PAD_Y = 24, 16, 8, 16, 6
# an item, the words of a transition and an item of confusion wrap past these widths
WIDEST, WORDS_WIDEST, CONFUSION_WIDEST = 320, 220, 240
WAVE, PERIOD, STEP = 8, 240, 8    # a boundary: a sine this high and this long, sampled every STEP px
SPAN, BULGE, CLEAR = 120, 60, 24  # a transition reaches SPAN each side of its boundary and bulges BULGE out of it
BOUNDARY, LINK, CLIFF, RED = "#868e96", "#495057", "#343a40", shade("red", 7)
# each domain: its corner, as (-1 left or 1 right, -1 top or 1 bottom), and its color
DOMAINS = {"complex": ((-1, -1), "grape"), "complicated": ((1, -1), "blue"),
           "chaotic": ((-1, 1), "red"), "clear": ((1, 1), "teal")}
WORDS = {"complex": ["Complejo", "sondear, percibir, responder"],
         "complicated": ["Complicado", "percibir, analizar, responder"],
         "chaotic": ["Caótico", "actuar, percibir, responder"],
         "clear": ["Claro", "percibir, categorizar, responder"], "confusion": "Confusión"}


def parsed(data):
    fields(data, "top level", ("domains",), ("confusion", "transitions", "words"))
    domains = {d: [] for d in DOMAINS}
    for d, items in entries(data["domains"], "domains").items():
        choice(d, "domains", DOMAINS)
        domains[d] = [wrapped(str(item), SIZE, WIDEST) for item in listed(items, f"domains.{d}")]
    confusion = [wrapped(str(item), SIZE, CONFUSION_WIDEST) for item in listed(data.get("confusion"), "confusion")]
    transitions = []
    for i, transition in enumerate(listed(data.get("transitions"), "transitions")):
        where = f"transitions[{i}]"
        if not isinstance(transition, list) or len(transition) != 3:
            raise DataError(f"{where}: expected [from, to, words], got {transition!r}")
        a, b = (choice(end, where, DOMAINS) for end in transition[:2])
        (ax, ay), (bx, by) = DOMAINS[a][0], DOMAINS[b][0]
        if (ax != bx) == (ay != by):
            raise DataError(f"{where}: {a} and {b} share no boundary; a transition runs between two domains "
                            "side by side or one above the other")
        if any((a, b) == t[:2] for t in transitions):
            raise DataError(f"{where}: {a} to {b} comes twice")
        transitions.append((a, b, wrapped(str(transition[2]), SIZE, WORDS_WIDEST)))
    words = {**WORDS, **fields(data.get("words") or {}, "words", (), tuple(WORDS))}
    for d in DOMAINS:
        if not isinstance(words[d], list) or len(words[d]) != 2:
            raise DataError(f"words.{d}: expected [name, how to act], got {words[d]!r}")
    return domains, confusion, transitions, words


def badge_size(content):
    return fonts.width(content, FONT, SIZE) + 2 * PAD_X, height(content, SIZE) + 2 * PAD_Y


def badge(x, y, content, color):
    """A white rounded label, from its top left corner."""
    w, h = badge_size(content)
    return {"type": "rectangle", "x": x, "y": y, "width": w, "height": h, "strokeColor": color,
            "backgroundColor": "#ffffff", "fillStyle": "solid", "roughness": 0, "roundness": {"type": 3},
            "label": {"text": content, "fontSize": SIZE, "fontFamily": FONT, "strokeColor": INK}}


def stack_height(items):
    return sum(badge_size(item)[1] + BADGE_GAP for item in items) - BADGE_GAP if items else 0


def arcs(transitions, half_w, half_h):
    """Each transition as (a, b, words, start, apex, end), from the centre: across its boundary, clear of the
    ellipse of confusion, which reaches half_w and half_h from it, and of the one before it across the same
    boundary. Also how far each arm reaches out, (-1 or 1, level) for the arms above, below, left and right."""
    reach, out = {}, []
    for a, b, words in transitions:
        (ax, ay), (bx, by) = DOMAINS[a][0], DOMAINS[b][0]
        w, h = badge_size(words)
        level = ay == by  # side by side: the arc runs level across the boundary above or below the middle
        side, inner, outward = (ay, half_h, h / 2) if level else (ax, half_w, w / 2)
        d = reach.get((side, level), max(inner + max(0, outward - BULGE), SPAN) + CLEAR)
        if level:
            start, apex, end = (ax * SPAN, side * d), (0, side * (d + BULGE)), (bx * SPAN, side * d)
        else:
            start, apex, end = (side * d, ay * SPAN), (side * (d + BULGE), 0), (side * d, by * SPAN)
        reach[side, level] = d + BULGE + outward + CLEAR
        out.append((a, b, words, start, apex, end))
    return out, reach


def closed(points, color):
    return path("line", points + [points[0]], strokeColor="transparent", backgroundColor=shade(color, 1),
                fillStyle="solid", roughness=0)


def build(data):
    domains, confusion, transitions, words = parsed(data)
    block = NAME_SIZE * LINE + 4 + HOW_SIZE * LINE
    # confusion: its name and items centred in an ellipse that holds their block
    lines_w = max([fonts.width(words["confusion"], TITLE_FONT, CONFUSION_SIZE)] +
                  [fonts.width(item, FONT, SIZE) for item in confusion])
    lines_h = CONFUSION_SIZE * LINE + (8 + sum(height(item, SIZE) for item in confusion) if confusion else 0)
    ew, eh = lines_w * math.sqrt(2) + 30, lines_h * math.sqrt(2) + 16
    placed, reach = arcs(transitions, ew / 2, eh / 2)
    # the cross between the corners holds confusion and the transitions, level above and below it, upright beside it
    badges = [(badge_size(w), DOMAINS[a][0][1] == DOMAINS[b][0][1]) for a, b, w, *_ in placed]
    corridor = max([SPAN] + [bw / 2 for (bw, _), level in badges if level])
    band = max([SPAN, eh / 2] + [bh / 2 for (_, bh), level in badges if not level])
    widest = max(max([fonts.width(words[d][0], TITLE_FONT, NAME_SIZE), fonts.width(words[d][1], FONT, HOW_SIZE)] +
                     [badge_size(item)[0] for item in items]) for d, items in domains.items())
    tallest = max(block + (NAME_GAP + stack_height(items) if items else 0) for items in domains.values())
    half_w = max(MIN_W / 2, EDGE + widest + corridor + CLEAR, reach.get((-1, False), 0), reach.get((1, False), 0))
    half_h = max(MIN_H / 2, EDGE + tallest + band + CLEAR, reach.get((-1, True), 0), reach.get((1, True), 0))
    half_w, half_h = (math.ceil(half / STEP) * STEP for half in (half_w, half_h))
    cx, cy, w, h = half_w, half_h, 2 * half_w, 2 * half_h
    # the boundaries: one wave across the middle, one down the top half, both through the centre
    across = [(x, cy + WAVE * math.sin(2 * math.pi * (x - cx) / PERIOD)) for x in range(0, w + 1, STEP)]
    down = [(cx + WAVE * math.sin(2 * math.pi * (y - cy) / PERIOD), y) for y in range(0, cy + 1, STEP)]
    left, right = [p for p in across if p[0] <= cx], [p for p in across if p[0] >= cx]
    shapes = {"complex": [(0, 0), *down, *left[::-1]], "complicated": [down[0], (w, 0), *right[::-1], *down[::-1]],
              "chaotic": [*left, (cx, h), (0, h)], "clear": [*right, (w, h), (cx, h)]}
    out = [closed(points, DOMAINS[d][1]) for d, points in shapes.items()]
    # the cliff: clear sits on top of it and falls into chaos
    boundary = {"strokeColor": BOUNDARY, "strokeWidth": 2, "roughness": 0}
    out += [path("line", across, **boundary), path("line", down, **boundary),
            path("line", [(cx, cy), (cx, h)], strokeColor=CLIFF, strokeWidth=5, roughness=0)]
    for d, items in domains.items():
        (sx, sy), color = DOMAINS[d]
        name, how = words[d]
        x, align = (w - EDGE, "right") if sx > 0 else (EDGE, "left")
        y = EDGE if sy < 0 else h - EDGE - block
        out += [text(x, y, name, NAME_SIZE, shade(color, 7), TITLE_FONT, align),
                text(x, y + NAME_SIZE * LINE + 4, how, HOW_SIZE, shade(color, 9), align=align)]
        # from the name towards the middle, in their order top to bottom
        item_y = y + block + NAME_GAP if sy < 0 else y - NAME_GAP - stack_height(items)
        for item in items:
            bw, bh = badge_size(item)
            out.append(badge(x - bw if sx > 0 else x, item_y, item, shade(color, 6)))
            item_y += bh + BADGE_GAP
    # each transition a curve across its boundary, its words on its apex hiding the line and the boundary
    for a, b, content, start, apex, end in placed:
        color = RED if (a, b) == ("clear", "chaotic") else LINK
        (x0, y0), (x1, y1), (x2, y2) = [(cx + px, cy + py) for px, py in (start, apex, end)]
        out.append({"type": "arrow", "x": x0, "y": y0, "points": [[0, 0], [x1 - x0, y1 - y0], [x2 - x0, y2 - y0]],
                    "strokeColor": color, "strokeWidth": 2, "roughness": 0, "roundness": {"type": 2},
                    "endArrowhead": "triangle"})
        bw, bh = badge_size(content)
        out.append(badge(x1 - bw / 2, y1 - bh / 2, content, color))
    out.append({"type": "ellipse", "x": cx - ew / 2, "y": cy - eh / 2, "width": ew, "height": eh,
                "strokeColor": BOUNDARY, "backgroundColor": "#ffffff", "fillStyle": "solid", "strokeWidth": 2,
                "roughness": 0})
    y = cy - lines_h / 2
    out.append(text(cx, y, words["confusion"], CONFUSION_SIZE, LINK, TITLE_FONT, "center"))
    y += CONFUSION_SIZE * LINE + 8
    for item in confusion:
        out.append(text(cx, y, item, SIZE, align="center"))
        y += height(item, SIZE)
    return out
