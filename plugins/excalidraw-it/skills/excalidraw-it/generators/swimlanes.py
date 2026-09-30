"""Swimlanes: a flowchart with each step in the lane of who does it, one lane per actor, left to right.

    lanes:                     # name: color, left to right
      Operador: orange
      Claude: violet
      Scripts: blue
    steps:                     # id: {label, lane, row, kind}; kind: step (default), decision or terminal
      pide: {label: Pide un tipo, lane: Operador, row: 0, kind: terminal}
      genera: {label: "Escribe el\\ngenerador", lane: Claude, row: 0}
      lint: {label: lint.py revisa, lane: Scripts, row: 1}
      findings: {label: '¿Findings?', lane: Scripts, row: 2, kind: decision}
    edges:                     # [from, to] or [from, to, label]
      - [pide, genera]
      - [genera, lint]
      - [lint, findings]
      - [findings, genera, sí]

You put each step in its lane and row; the generator sizes the lanes, a
diamond twice as wide as its label, and routes each arrow as a line of its own
corners: level between steps on one row, straight down a lane, down then
across, across then up into the foot of a step above, or across the gap between
two rows, each on a track of its own there. When those would run over a step,
a label or another arrow, it runs up a corridor between a border of a lane and
its steps, so each lane is 80 px wider than its widest step. Into or out of a
head or a foot it keeps off the middle, and one that enters a side where another
leaves moves a little up or down; a diamond has only its corners. A label sits
beside where its arrow leaves. Give a handoff the row of the step it hands to
when the lane between them is empty on that row, so it runs level.
"""
import fonts
from canvas import FONT, INK, LINE, path, piece
from flow import DOWN, LEVEL, corridors, edges as parsed_edges, exit_label, node, size
from palette import OPEN_COLOR, shade
from schema import DataError, choice, entries, fields, number

SIZE, EXIT_SIZE = 18, 16
LANE_GAP, HEADER_H = 16, 60
FIRST_ROW, PITCH, ROW_CLEAR = 130, 130, 50  # FIRST_ROW: middle of row 0, from the top of the headers
CORRIDOR, CORRIDOR_STEP = 24, 10            # a loop back up runs this far inside the left border of its lane
TRACK = 10                                  # between two arrows that cross one gap between rows
LINE_COLOR, DARK = shade("gray", 7), "#343a40"
KINDS = ("step", "decision", "terminal")


def parsed(data):
    fields(data, "top level", ("lanes", "steps"), ("edges",))
    lanes = {}
    for name, color in entries(data["lanes"], "lanes").items():
        if "," in str(name):
            raise DataError(f"lanes.{name}: a lane name cannot hold a comma")
        lanes[str(name)] = choice(color, f"lanes.{name}", OPEN_COLOR)
    steps, cells = {}, {}
    for n, value in entries(data["steps"], "steps").items():
        where = f"steps.{n}"
        fields(value, where, ("label", "lane", "row"), ("kind",))
        step = node(value, where, KINDS, ("lane", "row"))
        spot = list(lanes).index(choice(str(value["lane"]), f"{where}.lane", lanes)), \
            number(value["row"], f"{where}.row", low=0, whole=True)
        if spot in cells:
            raise DataError(f"{where}: lane {value['lane']}, row {spot[1]} is taken by {cells[spot]}")
        cells[spot] = n
        steps[n] = {**step, "lane": spot[0], "row": spot[1]}
    return lanes, steps, parsed_edges(data.get("edges"), "edges", steps)


def layout(steps):
    """The width of each lane and the box of each step, centred in its lane and row."""
    sizes = {n: size(step["label"], "step" if step["kind"] == "terminal" else step["kind"], SIZE, least=160)
             for n, step in steps.items()}
    step_w = max([w for n, (w, _) in sizes.items() if steps[n]["kind"] != "decision"], default=160)
    sizes = {n: (w if steps[n]["kind"] == "decision" else step_w, h) for n, (w, h) in sizes.items()}
    lane_w = max(w for w, _ in sizes.values()) + 80
    rows = max(step["row"] for step in steps.values()) + 1
    tallest = [max([h for n, (_, h) in sizes.items() if steps[n]["row"] == r], default=0) for r in range(rows)]
    middles = [FIRST_ROW]
    for r in range(1, rows):
        middles.append(middles[-1] + max(PITCH, (tallest[r - 1] + tallest[r]) / 2 + ROW_CLEAR))
    box = {}
    for n, step in steps.items():
        w, h = sizes[n]
        box[n] = (step["lane"] * (lane_w + LANE_GAP) + lane_w / 2 - w / 2, middles[step["row"]] - h / 2, w, h)
    return lane_w, box, middles[-1] + tallest[-1] / 2 + 40 - HEADER_H


def at(b, fx, fy):
    x, y, w, h = b
    return x + fx * w, y + fy * h


def routes(a, b, others, gaps, pointed=(False, False)):
    """The ways an arrow can run from box a to box b, best first: (start, end, corners between). One into or out
    of the head or foot of a step keeps clear of the arrow down it by leaving or entering off its middle, on the
    side that faces the other end, but for a diamond, `pointed`, whose only point there is its middle. `gaps`
    holds the y of the middle of each gap between two rows, where an arrow can cross the lanes clear of every step."""
    towards = 1 if b[0] > a[0] else 0
    leave = 0.5 if pointed[0] else 0.7 if towards else 0.3
    enter = 0.5 if pointed[1] else 0.3 if towards else 0.7
    level, down = a[1] + a[3] / 2 == b[1] + b[3] / 2, b[1] > a[1]
    out = []
    if level:  # straight across, or under what sits on the row between them
        out.append((*(LEVEL if towards else (LEVEL[1], LEVEL[0])), []))
        middle = a[1] + a[3] / 2
        bottom = max(y + h for x, y, w, h in [a, b, *others] if y < middle < y + h)
        under = next((y for y in gaps if bottom < y < bottom + 80), bottom + 24)  # the gap right below the row
        start, end = [leave, 1], [enter, 1]
        out.append((start, end, [(at(a, *start)[0], under), (at(b, *end)[0], under)]))
    elif a[0] + a[2] / 2 == b[0] + b[2] / 2:
        out.append((*(DOWN if down else (DOWN[1], DOWN[0])), []))
    elif down:
        start, end = [leave, 1], [1 - towards, 0.5]
        out.append((start, end, [(at(a, *start)[0], at(b, *end)[1])]))
        start, end = [towards, 0.5], [enter, 0]
        out.append((start, end, [(at(b, *end)[0], at(a, *start)[1])]))
    else:
        start, end = [towards, 0.5], [enter, 1]
        out.append((start, end, [(at(b, *end)[0], at(a, *start)[1])]))
    if not level:  # across a gap between rows: the one next to a, or the one next to b
        start, end = [leave, int(down)], [enter, int(not down)]
        top, bottom = (a[1] + a[3], b[1]) if down else (b[1] + b[3], a[1])
        between = [y for y in gaps if top < y < bottom]
        for y in dict.fromkeys(between[:1] + between[-1:]):
            out.append((start, end, [(at(a, *start)[0], y), (at(b, *end)[0], y)]))
    return out


def hits(points, boxes, margin=6):
    """How many times the line runs over a box."""
    return sum(min(x1, x2) < x + w + margin and max(x1, x2) > x - margin and
               min(y1, y2) < y + h + margin and max(y1, y2) > y - margin
               for (x1, y1), (x2, y2) in zip(points, points[1:]) for x, y, w, h in boxes)


def along(points, placed):
    """How many segments of the line run along a segment already placed, on the same line for more than 8 px."""
    count = 0
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        for (u1, v1), (u2, v2) in placed:
            if abs(x1 - x2) < 1 and abs(u1 - u2) < 1 and abs(x1 - u1) < 4:
                count += min(max(y1, y2), max(v1, v2)) - max(min(y1, y2), min(v1, v2)) > 8
            elif abs(y1 - y2) < 1 and abs(v1 - v2) < 1 and abs(y1 - v1) < 4:
                count += min(max(x1, x2), max(u1, u2)) - max(min(x1, x2), min(u1, u2)) > 8
    return count


def corridor(a, b, x):
    """Along a corridor at x, from the side of box a that faces it to the side of box b that faces it."""
    start, end = [int(x > a[0]), 0.5], [int(x > b[0]), 0.5]
    return start, end, [(x, at(a, *start)[1]), (x, at(b, *end)[1])]


def line(box, a, b, way):
    start, end, via = way
    return [at(box[a], *start), *via, at(box[b], *end)]


def exit_text(label, way, box, a):
    """The label of an arrow that runs `way` out of box a, beside where it leaves; under the line out of a corridor."""
    start, _, via = way
    return exit_label(label, at(box[a], *start), start, LINE_COLOR, EXIT_SIZE, below=len(via) == 2)


def label_box(label, way, box, a):
    element = exit_text(label, way, box, a)
    return element["x"], element["y"], fonts.width(label, FONT, EXIT_SIZE), EXIT_SIZE * LINE


def cost(edge, label, way, chosen, labels, box):
    """What an arrow that runs `way` gets in the way of: the steps it runs over, then the labels it crosses or
    lays its own over and the segments it shares with other arrows, but for those that end where it ends, then
    the steps it passes within 20 px of."""
    a, b = edge
    points = line(box, a, b, way)
    rest = {e: w for e, w in chosen.items() if e != edge}
    segments = [s for (c, d), w in rest.items() if (d, w[1]) != (b, way[1])
                for s in zip(line(box, c, d, w), line(box, c, d, w)[1:])]
    clashes = hits(points, [label_box(labels[e], w, box, e[0]) for e, w in rest.items() if labels[e]])
    if label:
        own = label_box(label, way, box, a)
        clashes += sum(hits(list(s), [own]) for (c, d), w in rest.items()
                       for s in zip(line(box, c, d, w), line(box, c, d, w)[1:]))
    steps = [box[n] for n in box if n not in edge]
    near = hits(points, steps, margin=20) - hits(points, steps)
    return hits(points, steps), clashes + along(points, segments), near


def paths(edges, steps, box, lane_w):
    """The fixed points and corners of each arrow: of its routes, then of the corridors down the left and then
    the right margin of each lane from a's to b's, the first that costs least. A second pass chooses again knowing every other arrow.
    Each corridor runs further in than one it would run on."""
    labels = {(a, b): label for a, b, label in edges}
    rows = max(step["row"] for step in steps.values()) + 1
    spans = [[box[n] for n, step in steps.items() if step["row"] == r] for r in range(rows)]
    gaps = [(max(y + h for _, y, _, h in spans[r]) + min(y for _, y, _, _ in spans[r + 1])) / 2
            for r in range(rows - 1) if spans[r] and spans[r + 1]]
    ways, corridor_ways, chosen = {}, {}, {}
    for a, b, _ in edges:
        lanes = range(min(steps[a]["lane"], steps[b]["lane"]), max(steps[a]["lane"], steps[b]["lane"]) + 1)
        margins = [lane * (lane_w + LANE_GAP) + CORRIDOR for lane in lanes] + \
            [lane * (lane_w + LANE_GAP) + lane_w - CORRIDOR for lane in lanes]
        corridor_ways[a, b] = [corridor(box[a], box[b], x) for x in margins]
        pointed = tuple(steps[n]["kind"] == "decision" for n in (a, b))
        ways[a, b] = routes(box[a], box[b], [box[n] for n in box if n not in (a, b)], gaps, pointed) + \
            corridor_ways[a, b]
    for _ in range(2):
        for edge, label in labels.items():
            chosen[edge] = min(ways[edge], key=lambda way: cost(edge, label, way, chosen, labels, box))
    loops = {}
    for (a, b), way in chosen.items():
        if way in corridor_ways[a, b]:
            low, high = sorted((steps[a]["row"], steps[b]["row"]))
            x = way[2][0][0]
            lane, inside = divmod(x, lane_w + LANE_GAP)
            loops.setdefault(lane, []).append(((a, b), -1 if inside < lane_w / 2 else 1, low, high, x, steps[a]["row"]))
    for lane_loops in loops.values():  # the corridors of one lane share its room
        for (a, b), x in corridors(lane_loops, clear=0, step=CORRIDOR_STEP).items():
            chosen[a, b] = corridor(box[a], box[b], x)
    return spread(tracked(chosen, gaps), box, {n for n, step in steps.items() if step["kind"] == "decision"})


def spread(chosen, box, pointed):
    """Where one arrow enters the side of a step at the point another leaves from, one of them moves a fifth of
    the step's height up or down, towards where its line turns: the one that enters, or else the one that leaves.
    A diamond has no point there but its corner."""
    def moved(n, fixed, near, far):
        """The fixed point on a side and the corner next to it, moved towards `far`, the point after that corner;
        None on a diamond, off a side, or where the line does not turn at that corner."""
        if n in pointed or fixed[1] != 0.5 or near[1] == far[1]:
            return None
        fy = 0.3 if far[1] < near[1] else 0.7
        return [fixed[0], fy], (near[0], box[n][1] + fy * box[n][3])

    for (a, b), (start, end, via) in list(chosen.items()):
        leaving = {(c, tuple(w[0])) for (c, _), w in chosen.items()}
        entering = {(d, tuple(w[1])) for (_, d), w in chosen.items()}
        points = [at(box[a], *start), *via, at(box[b], *end)]
        if (b, tuple(end)) in leaving and len(via) and (new := moved(b, end, via[-1], points[-3])):
            chosen[a, b] = start, new[0], [*via[:-1], new[1]]
        elif (a, tuple(start)) in entering and len(via) and (new := moved(a, start, via[0], points[2])):
            chosen[a, b] = new[0], end, [new[1], *via[1:]]
    return chosen


def tracked(chosen, gaps):
    """The arrows that cross one gap between rows, each on a track of its own where they would run along each
    other: the middle of the gap first, then TRACK above it, below it, and further out. Where two turn at one x,
    the one that turns up runs above the one that turns down, so their turns do not overlap."""
    offsets = [0] + [side * TRACK * (i // 2 + 1) for i, side in enumerate([-1, 1] * 2)]
    for gap in gaps:
        crossing = sorted((min(via[0][0], via[1][0]), max(via[0][0], via[1][0]), edge)
                          for edge, (_, _, via) in chosen.items() if len(via) == 2 and via[0][1] == via[1][1] == gap)
        placed = []  # (left, right, y, turns): turns maps the x of each turn to -1 up or 1 down
        for left, right, edge in crossing:
            start, end, via = chosen[edge]
            turns = {via[0][0]: 1 - 2 * start[1], via[1][0]: 1 - 2 * end[1]}  # to a head below 1, to a foot above -1

            def fits(y, turning=True):
                for other_left, other_right, other_y, other_turns in placed:
                    if other_y == y and left - 8 < other_right and other_left < right + 8:
                        return False
                    for x, turn in turns.items() if turning else ():
                        other = next((t for ox, t in other_turns.items() if abs(ox - x) < 4), None)
                        if other is not None and other != turn and (y - other_y) * turn < 0:
                            return False
                return True
            # two that cross like an X turn both ways at the same x's: then a track of its own, at least
            y = next((gap + dy for dy in offsets if fits(gap + dy)), None) or \
                next((gap + dy for dy in offsets if fits(gap + dy, turning=False)), gap)
            placed.append((left, right, y, turns))
            chosen[edge] = start, end, [(via[0][0], y), (via[1][0], y)]
    return chosen


def build(data):
    lanes, steps, edges = parsed(data)
    lane_w, box, body = layout(steps)
    out = piece("lane-with-header", titles=",".join(lanes), colors=",".join(lanes.values()), x=0, y=0,
                width=lane_w, gap=LANE_GAP, height=body, header_height=HEADER_H)
    for n, step in steps.items():
        x, y, w, h = box[n]
        border, fill, ink = {"terminal": (DARK, DARK, "#ffffff"),
                             "decision": (shade("yellow", 7), shade("yellow", 1), INK),
                             "step": (shade(list(lanes.values())[step["lane"]], 7), "#ffffff", INK)}[step["kind"]]
        out.append({"type": "diamond" if step["kind"] == "decision" else "rectangle", "tempId": n,
                    "x": x, "y": y, "width": w, "height": h, "strokeColor": border, "backgroundColor": fill,
                    "fillStyle": "solid", "strokeWidth": 2, "roughness": 0,
                    "roundness": None if step["kind"] == "decision" else {"type": 3},
                    "label": {"text": step["label"], "fontSize": SIZE, "fontFamily": FONT, "strokeColor": ink}})
    route = paths(edges, steps, box, lane_w)
    for a, b, label in edges:
        start, end, via = route[a, b]
        points = [at(box[a], *start), *via, at(box[b], *end)]
        out.append(path("arrow", points, roundness=None, endArrowhead="arrow", strokeColor=LINE_COLOR, strokeWidth=2,
                        roughness=0, startBinding={"elementId": a, "fixedPoint": start, "mode": "inside"},
                        endBinding={"elementId": b, "fixedPoint": end, "mode": "inside"}))
        if label:
            out.append(exit_text(label, route[a, b], box, a))
    return out
