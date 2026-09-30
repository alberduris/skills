"""A Wardley map: components placed by how visible and how evolved they are, linked down the value chain.

    anchors:                   # name: [visibility, evolution], each from 0 to 1; the users, at the top
      Operador: [0.97, 0.52]
    components:                # name: [visibility, evolution], or name: {at, inertia}
      Diagrama legible: [0.86, 0.40]
      mermaid-to-excalidraw: {at: [0.30, 0.52], inertia: true}   # a thick bar: it resists change
    links:                     # [from, to], down the value chain
      - [Operador, Diagrama legible]
    evolve:                    # component: {to: evolution, name}; a red arrow to where it is going
      Receta por tipo: {to: 0.56, name: Generador por tipo}
    words:                     # the words of the axes and the legend, in Spanish by default
      stages: [Génesis, A medida, Producto (+alquiler), Commodity (+utility)]

words also takes evolution, visible, invisible, value_chain, evolves and inertia.
You place each component; the generator puts each name beside its dot, at the
first spot right, left, above or below that stays clear of the lines, the dots
and the names placed before it. Place the components so that no two links run
close together, since a web of near-parallel lines cannot be traced, and say in
the note that the positions are estimates.
"""
import math

import fonts
from canvas import FONT, INK, LINE, MUTED, TITLE_FONT, path, text
from palette import shade
from schema import DataError, choice, entries, fields, listed, number, pair

SIZE, ANCHOR_SIZE, AXIS_SIZE = 15, 20, 14
W, H, DOT = 1040, 620, 14
LINK, DIVIDER, RED = "#495057", "#ced4da", shade("red", 7)
WORDS = {"stages": ["Génesis", "A medida", "Producto (+alquiler)", "Commodity (+utility)"],
         "evolution": "evolución ->", "visible": "visible", "invisible": "invisible",
         "value_chain": "cadena de valor", "evolves": "hacia dónde evoluciona",
         "inertia": "inercia: se resiste a cambiar"}
STROKE = {"strokeWidth": 2, "roughness": 0}


def parsed(data):
    fields(data, "top level", ("anchors", "components"), ("links", "evolve", "words"))
    spot = {"low": 0, "high": 1}
    anchors = {str(n): pair(at, f"anchors.{n}", **spot) for n, at in entries(data["anchors"], "anchors").items()}
    components, inertia = {}, set()
    for n, value in entries(data["components"], "components").items():
        where = f"components.{n}"
        if n in anchors:
            raise DataError(f"{where}: {n} is also an anchor")
        if isinstance(value, dict):
            fields(value, where, ("at",), ("inertia",))
            if value.get("inertia"):
                inertia.add(str(n))
            value = value["at"]
        components[str(n)] = pair(value, where, **spot)
    names = {**anchors, **components}
    links = []
    for i, link in enumerate(listed(data.get("links"), "links")):
        if not isinstance(link, list) or len(link) != 2:
            raise DataError(f"links[{i}]: expected [from, to], got {link!r}")
        links.append(tuple(choice(str(end), f"links[{i}]", names) for end in link))
    evolve = {}
    for n, value in entries(data.get("evolve"), "evolve", optional=True).items():
        n, where = str(n), f"evolve.{n}"
        choice(n, where, components)
        fields(value, where, ("to", "name"))
        evolve[n] = number(value["to"], f"{where}.to", **spot), str(value["name"])
    words = {**WORDS, **fields(data.get("words") or {}, "words", (), tuple(WORDS))}
    if len(words["stages"]) != 4:
        raise DataError(f"words.stages: expected the names of the four stages, got {words['stages']!r}")
    return anchors, components, inertia, links, evolve, words


def at(visibility, evolution):
    return evolution * W, (1 - visibility) * H


def samples(a, b, step=6):
    n = max(1, int(math.dist(a, b) / step))
    return [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n + 1)]


def trimmed(a, b, start, end):
    """The segment a-b without its first `start` and its last `end` pixels."""
    d = math.dist(a, b)
    ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
    return (a[0] + ux * start, a[1] + uy * start), (b[0] - ux * end, b[1] - uy * end)


def segment(kind, start, end, color, **style):
    return path(kind, [start, end], strokeColor=color, roughness=0, **style)


def past_bar(here, there):
    """How far from a dot with inertia its link towards `there` starts: past the bar right of the dot, with 3 px
    to spare, when the link would cross it."""
    d = math.dist(here, there)
    ux, uy = (there[0] - here[0]) / d, (there[1] - here[1]) / d
    start = DOT / 2 + 2
    if ux <= 0:
        return start
    # the link crosses the box 3 px around the bar between t_in and t_out
    t_in, t_out = (DOT - 3) / ux, (DOT + 9) / ux
    if uy:
        t_in, t_out = max(t_in, min(-16 / uy, 16 / uy)), min(t_out, max(-16 / uy, 16 / uy))
    return max(start, t_out + 1) if t_in <= t_out else start


def around(x, y, reach=7):
    return [(x + dx, y + dy) for dx in (-reach, 0, reach) for dy in (-reach, 0, reach)]


def box_points(x, y, w, h):
    return [(x + i * w / 8, y + j * h / 2) for i in range(9) for j in range(3)]


def label_spot(x, y, w, h, taken, bar=0):
    """The first spot beside a point that stays clear of what is taken: right, left, above, below."""
    spots = [(x + DOT + bar, y - h / 2), (x - DOT - w, y - h / 2), (x - w / 2, y - DOT - h), (x - w / 2, y + DOT)]

    def hits(spot):
        sx, sy = spot
        return sum(sx - 4 < px < sx + w + 4 and sy - 4 < py < sy + h + 4 for px, py in taken)
    return min(spots, key=hits)


def axes(words):
    out = [{"type": "arrow", "x": 0, "y": H, "points": [[0, 0], [0, -H]], "strokeColor": INK,
            "endArrowhead": "triangle", **STROKE},
           {"type": "arrow", "x": 0, "y": H, "points": [[0, 0], [W, 0]], "strokeColor": INK,
            "endArrowhead": "triangle", **STROKE}]
    for i, stage in enumerate(words["stages"]):
        if i:
            out.append(segment("line", (i * W / 4, 0), (i * W / 4, H), DIVIDER, strokeStyle="dashed", strokeWidth=1))
        out.append(text((i + 0.5) * W / 4, H + 12, stage, AXIS_SIZE, MUTED, align="center"))
    return out + [text(W, H + 16 + AXIS_SIZE * LINE, words["evolution"], AXIS_SIZE, MUTED, align="right"),
                  text(-12, 0, words["visible"], AXIS_SIZE, MUTED, align="right"),
                  text(-12, H - AXIS_SIZE * LINE, words["invisible"], AXIS_SIZE, MUTED, align="right"),
                  text(-40, H / 2 - AXIS_SIZE * LINE / 2, words["value_chain"], AXIS_SIZE, MUTED, align="center",
                       angle=3 * math.pi / 2)]


def legend(words, evolves, inertia):
    """What the red arrow and the bar mean, under the axis, only for what the map uses."""
    out, x, y = [], 0, H + 60
    if evolves:
        out += [segment("arrow", (x, y), (x + 40, y), RED, strokeStyle="dashed", endArrowhead="triangle", strokeWidth=2),
                text(x + 52, y - SIZE * LINE / 2, words["evolves"], SIZE, MUTED)]
        x += 52 + fonts.width(words["evolves"], FONT, SIZE) + 48
    if inertia:
        out += [{"type": "rectangle", "x": x, "y": y - 11, "width": 6, "height": 22, "strokeColor": INK,
                 "backgroundColor": INK, "fillStyle": "solid", "roughness": 0},
                text(x + 18, y - SIZE * LINE / 2, words["inertia"], SIZE, MUTED)]
    return out


def build(data):
    anchors, components, inertia, links, evolve, words = parsed(data)
    points = {n: at(*spot) for n, spot in {**anchors, **components}.items()}
    ghosts = {c: (at(components[c][0], to), name) for c, (to, name) in evolve.items()}
    anchor_h = ANCHOR_SIZE * LINE
    out, taken = axes(words), []
    def clear(n, there):
        """How far from n its link towards `there` starts: under an anchor's name, past a bar, or off the dot."""
        if n in anchors:
            return anchor_h / 2 + 4
        return past_bar(points[n], there) if n in inertia else DOT / 2 + 2

    # links from the edge of one dot to the edge of the other; from an anchor, from under its name
    for a, b in links:
        start, end = trimmed(points[a], points[b], clear(a, points[b]), clear(b, points[a]))
        out.append(segment("line", start, end, LINK, strokeWidth=1))
        taken += samples(start, end)
    for c, (ghost, _) in ghosts.items():
        start, end = trimmed(points[c], ghost, past_bar(points[c], ghost) + 2 if c in inertia else DOT / 2 + 4,
                             DOT / 2 + 4)
        out.append(segment("arrow", start, end, RED, strokeStyle="dashed", endArrowhead="triangle", strokeWidth=2))
        taken += samples(start, end)
    dot = {"type": "ellipse", "width": DOT, "height": DOT, "backgroundColor": "#ffffff", "fillStyle": "solid", **STROKE}
    for c in components:
        x, y = points[c]
        out.append({**dot, "x": x - DOT / 2, "y": y - DOT / 2, "strokeColor": INK})
        taken += around(x, y)
        if c in inertia:
            out.append({"type": "rectangle", "x": x + DOT, "y": y - 13, "width": 6, "height": 26, "strokeColor": INK,
                        "backgroundColor": INK, "fillStyle": "solid", "roughness": 0})
            taken += [(x + DOT + 3, y + dy) for dy in range(-13, 14, 4)]
    for (x, y), _ in ghosts.values():
        out.append({**dot, "x": x - DOT / 2, "y": y - DOT / 2, "strokeColor": RED})
        taken += around(x, y)
    for n in anchors:
        x, y = points[n]
        w = fonts.width(n, TITLE_FONT, ANCHOR_SIZE)
        out.append(text(x, y - anchor_h / 2, n, ANCHOR_SIZE, font=TITLE_FONT, align="center"))
        taken += box_points(x - w / 2, y - anchor_h / 2, w, anchor_h)
    # names beside their dots, highest first, each clear of the lines, the dots and the names before it
    labels = [(c, *points[c], INK) for c in sorted(components, key=lambda c: -components[c][0])]
    labels += [(name, x, y, RED) for (x, y), name in ghosts.values()]
    for name, x, y, color in labels:
        w, h = fonts.width(name, FONT, SIZE), SIZE * LINE
        lx, ly = label_spot(x, y, w, h, taken, bar=12 if name in inertia else 0)
        out.append(text(lx, ly, name, SIZE, color))
        taken += box_points(lx, ly, w, h)
    return out + legend(words, bool(evolve), bool(inertia))
