"""An event model: the frames of a flow in time order, each in the lane of its kind and the column of its moment.

    frames:                    # in time order: [kind, text], with Mermaid's kinds
      - [ui, Chat del operador]                  # a screen: a sharp white box
      - [cmd, Escribir la escena]                # a command, blue
      - [evt, Escena.Elementos añadidos]         # an event, orange, in the lane of its stream: Escena
      - [rmo, Hallazgos del lint]                # a read model, green
      - [pcr, lint --fix]                        # an automation: a rounded white box, dashed
    words:                     # the lane titles, the legend and the time mark, in Spanish by default
      events: Eventos          # an event lane is titled this and its stream

words also takes ui_lane, cmd_lane and time, and ui, pcr, cmd, rmo and evt for the
legend. You give the frames in order; the generator puts screens and automations
in the top lane, commands and read models in the next, and the events of each
stream in a lane of their own, in the order the streams first appear; it wraps
each text to fit its box, makes each lane as tall as its tallest box, numbers the columns, binds each frame to the next and
adds a legend of the kinds the model uses. A \\n in a text breaks it where you
choose.
"""
import fonts
from canvas import FONT, INK, LINE, MUTED, arrow, height, piece, text, wrapped
from palette import shade
from schema import DataError, choice, fields, listed

SIZE, SMALL = 14, 12
BOX_W, BOX_H, PAD, COLUMN_GAP = 124, 60, 10, 26  # each frame's box at least this big, PAD inside it
LANE_PAD, LANE_GAP, HEADER_W, HEADER_SIZE = 18, 10, 170, 20  # the lanes: HEADER_SIZE is the piece's title size
BORDER = "#495057"
# kind: the lane it goes in (screens and automations, commands and read models, events) and its color
KINDS = {"ui": ("ui_lane", None), "pcr": ("ui_lane", None), "cmd": ("cmd_lane", "blue"),
         "rmo": ("cmd_lane", "green"), "evt": ("events", "orange")}
WORDS = {"ui_lane": "UI y\nautomatización", "cmd_lane": "Comandos y\nlecturas", "events": "Eventos",
         "time": "tiempo ->", "ui": "pantalla", "pcr": "automatización", "cmd": "comando",
         "rmo": "modelo de lectura", "evt": "evento"}


def parsed(data):
    fields(data, "top level", ("frames",), ("words",))
    frames = []
    for i, frame in enumerate(listed(data["frames"], "frames")):
        where = f"frames[{i}]"
        if not isinstance(frame, list) or len(frame) != 2:
            raise DataError(f"{where}: expected [kind, text], got {frame!r}")
        kind, content = choice(frame[0], where, KINDS), str(frame[1])
        stream = None
        if kind == "evt":
            if "." not in content:
                raise DataError(f"{where}: an event names its stream before a dot, as Pedido.Pagado; got {content!r}")
            stream, content = (part.strip() for part in content.split(".", 1))
        frames.append((kind, stream, wrapped(content, SIZE, BOX_W - 2 * PAD)))
    if not frames:
        raise DataError("frames: expected a list of [kind, text], got none")
    words = {**WORDS, **fields(data.get("words") or {}, "words", (), tuple(WORDS))}
    return frames, {key: str(value) for key, value in words.items()}


def lanes_of(frames, words):
    """The lanes the frames use, top to bottom, as (key, title, color): screens, commands, then each stream."""
    used = {KINDS[kind][0] for kind, _, _ in frames}
    out = [(key, words[key], color) for key, color in (("ui_lane", "gray"), ("cmd_lane", "blue")) if key in used]
    streams = dict.fromkeys(stream for _, stream, _ in frames if stream)
    out += [(stream, f"{words['events']}\n{stream}", "orange") for stream in streams]
    for _, title, _ in out:
        if "," in title:  # the piece takes its titles comma-separated
            raise DataError(f"lane {title!r}: a lane title cannot hold a comma")
    return out


def look(kind):
    """How a frame of this kind is drawn, in its box and in the legend."""
    color = KINDS[kind][1]
    out = {"strokeColor": shade(color, 7) if color else BORDER, "strokeWidth": 2, "roughness": 0,
           "backgroundColor": shade(color, 1) if color else "#ffffff", "fillStyle": "solid"}
    if kind != "ui":
        out["roundness"] = {"type": 3}
    if kind == "pcr":
        out["strokeStyle"] = "dashed"
    return out


def legend(kinds, words, x, y):
    out = []
    for kind in (k for k in KINDS if k in kinds):
        out += [{"type": "rectangle", "x": x, "y": y, "width": 48, "height": 24, **look(kind)},
                text(x + 58, y + 12 - SIZE * LINE / 2, words[kind], SIZE, MUTED)]
        x += 58 + fonts.width(words[kind], FONT, SIZE) + 36
    return out


def build(data):
    frames, words = parsed(data)
    lanes = lanes_of(frames, words)
    lane_index = {key: i for i, (key, _, _) in enumerate(lanes)}
    lane_of = [lane_index[stream or KINDS[kind][0]] for kind, stream, _ in frames]
    box_w = max([BOX_W] + [fonts.width(content, FONT, SIZE) + 2 * PAD for _, _, content in frames])
    # the boxes of a lane are as tall as its tallest, so a long text raises only its own lane
    box_h = [max([BOX_H] + [height(content, SIZE) + 2 * PAD for (_, _, content), at in zip(frames, lane_of)
                            if at == lane]) for lane in range(len(lanes))]
    header_w = max([HEADER_W] + [fonts.width(title, 7, HEADER_SIZE) + 2 * PAD for _, title, _ in lanes])
    column = box_w + COLUMN_GAP
    lanes_top = SMALL * LINE + 8
    out, tops, bottom = [], [], lanes_top
    for (_, title, color), h in zip(lanes, box_h):
        tops.append(bottom)
        out += piece("lane-with-header", titles=title, colors=color, x=0, y=bottom, width=len(frames) * column + 20,
                     height=h + 2 * LANE_PAD, header_height=0, across=True, header_width=header_w)
        bottom += h + 2 * LANE_PAD + LANE_GAP
    out.append(text(header_w - 10, 0, words["time"], SMALL, MUTED, align="right"))
    boxes = []
    for i, ((kind, _, content), lane) in enumerate(zip(frames, lane_of)):
        x, y = header_w + 10 + i * column + COLUMN_GAP / 2, tops[lane] + LANE_PAD
        color = KINDS[kind][1]
        boxes.append((f"frame-{i}", lane, (x, y, box_w, box_h[lane])))
        out += [text(x + box_w / 2, 0, f"{i + 1:02d}", SMALL, MUTED, align="center"),
                {"type": "rectangle", "tempId": f"frame-{i}", "x": x, "y": y, "width": box_w, "height": box_h[lane],
                 **look(kind), "label": {"text": content, "fontSize": SIZE, "fontFamily": FONT,
                                         "strokeColor": shade(color, 9) if color else INK}}]
    # each frame leads to the next: level along a lane, else from the edge that faces the next frame's lane
    for (a, a_lane, a_box), (b, b_lane, b_box) in zip(boxes, boxes[1:]):
        if a_lane == b_lane:
            start, end = [1, 0.5], [0, 0.5]
        else:
            down = b_lane > a_lane
            start, end = [0.5, int(down)], [0.5, int(not down)]
        out.append(arrow(a, a_box, start, b, b_box, end, strokeColor=BORDER, endArrowhead="triangle"))
    return out + legend({kind for kind, _, _ in frames}, words, header_w, bottom + 20)
