"""A treemap: each item a tile whose area is its size, the items of a folder inside it, laid out squarified.

    items:                   # name: size for a tile; name: {size, color}; or name: {items, color} for a folder
      scripts:
        color: blue
        items: {write.py: 1450, lint.py: 1700}
      SKILL.md: {size: 4300, color: violet}
    unit: bytes              # sizes as B, KB and MB; another word goes after the number; plain numbers by default
    width: 960               # of the whole map; 960 by 560 by default
    height: 560
    thousands: ","           # the thousands separator, "." by default; the decimal one is the other

An item takes the next color of blue, yellow, red, teal, violet, orange, grape,
cyan, lime, pink, indigo and green unless it has its own, and the files of a
folder take its color. A tile shows its name, broken after _ - / or a space, and
its size when they fit, its name alone when only that fits, and nothing when not
even that does. Say the total and what the area measures in the note.
"""
import re

import fonts
from canvas import FONT, LINE, TITLE_FONT, shown, text
from palette import OPEN_COLOR, shade
from schema import DataError, choice, entries, fields, number

FOLDER_SIZE, FILE_SIZE = 16, 13
HEADER, PAD, INSET = 30, 4, 6  # a folder's title strip, the room around its files, a tile's text inset
COLORS = ["blue", "yellow", "red", "teal", "violet", "orange", "grape", "cyan", "lime", "pink", "indigo", "green"]
BREAKS = re.compile(r"[^_\-/ ]+[_\-/ ]?|[_\-/ ]")  # the pieces of a name, each with the break after it


def parsed(data):
    fields(data, "top level", ("items",), ("unit", "width", "height", "thousands"))
    items = []
    for i, (name, value) in enumerate(entries(data["items"], "items").items()):
        where, color = f"items.{name}", COLORS[i % len(COLORS)]
        if isinstance(value, dict):
            fields(value, where, (), ("size", "items", "color"))
            if ("size" in value) == ("items" in value):
                raise DataError(f"{where}: give it a size, for a tile, or items, for a folder")
            color = choice(value.get("color", color), f"{where}.color", OPEN_COLOR)
            value = value.get("size", value.get("items"))
        if isinstance(value, dict):
            files = [(str(f), number(v, f"{where}.items.{f}", low=0))
                     for f, v in entries(value, f"{where}.items").items()]
            items.append((str(name), sorted(files, key=lambda f: -f[1]), color))
        else:
            items.append((str(name), number(value, where, low=0), color))
    if not sum(total(node) for _, node, _ in items):
        raise DataError("items: every size is 0")
    size = (number(data.get("width", 960), "width", low=200), number(data.get("height", 560), "height", low=200))
    return items, data.get("unit"), size, choice(data.get("thousands", "."), "thousands", (".", ","))


def total(node):
    return node if not isinstance(node, list) else sum(v for _, v in node)


def size_text(n, unit, thousands):
    """A size: bytes as B, KB with one decimal or MB with one decimal; any other unit after the number."""
    if unit == "bytes":
        limit, unit = next(((limit, name) for limit, name in ((1e6, "MB"), (1e3, "KB")) if n >= limit), (1, "B"))
        out = shown(n / limit, thousands, 1, trim=False) if limit > 1 else shown(n, thousands, 0)
    else:
        out = shown(n, thousands)
    return f"{out} {unit}" if unit else out


def squarify(values, x, y, w, h):
    """One rectangle per value, largest first, laid in rows along the shorter side of what is left,
    each row grown while that keeps its worst aspect ratio from getting worse."""
    scale = w * h / (sum(values) or 1)
    areas, rects = [max(v * scale, 1e-6) for v in values], []
    while areas:
        side = min(w, h)
        worst = lambda row: max(max(side * side * a / sum(row) ** 2, sum(row) ** 2 / (side * side * a)) for a in row)
        n = 1
        while n < len(areas) and worst(areas[:n + 1]) <= worst(areas[:n]):
            n += 1
        thick, along = sum(areas[:n]) / side, 0
        for a in areas[:n]:
            rects.append((x, y + along, thick, a / thick) if w >= h else (x + along, y, a / thick, thick))
            along += a / thick
        x, w, y, h = (x + thick, w - thick, y, h) if w >= h else (x, w, y + thick, h - thick)
        areas = areas[n:]
    return rects


def wrapped(name, room):
    """The name in lines that fit the room, broken after _ - / or a space; None when a piece alone is too wide."""
    lines = []
    for piece in BREAKS.findall(name):
        if lines and fonts.width(lines[-1] + piece, FONT, FILE_SIZE) * 1.2 <= room:
            lines[-1] += piece
        elif fonts.width(piece, FONT, FILE_SIZE) * 1.2 <= room:
            lines.append(piece)
        else:
            return None
    return [line.rstrip() for line in lines]


def tile(name, size, x, y, w, h, color, group):
    """A file: a tile with its name and size inside when they fit, its name alone when only that does."""
    out = [{"type": "rectangle", "x": x, "y": y, "width": w, "height": h, "roughness": 0, "roundness": None,
            "strokeColor": shade(color, 6), "strokeWidth": 1, "backgroundColor": shade(color, 1),
            "fillStyle": "solid", "groupIds": [group]}]
    lines = wrapped(name, w - 2 * INSET)
    room = int((h - 2 * INSET) // (FILE_SIZE * LINE))
    if lines and len(lines) <= room:
        content = "\n".join(lines + [size] if len(lines) < room else lines)
        out.append(text(x + INSET, y + INSET, content, FILE_SIZE, shade(color, 9), groupIds=[group]))
    return out


def folder_title(name, size, w):
    """The name and total of a folder, its name alone when both do not fit, nothing when not even that does."""
    for title in (f"{name}  {size}", name):
        if fonts.width(title, TITLE_FONT, FOLDER_SIZE) * 1.1 <= w - 2 * INSET - 4:
            return title
    return None


def build(data):
    items, unit, (width, height), thousands = parsed(data)
    items.sort(key=lambda item: -total(item[1]))
    folders, tiles = [], []
    for i, ((name, node, color), (x, y, w, h)) in enumerate(
            zip(items, squarify([total(node) for _, node, _ in items], 0, 0, width, height))):
        if not isinstance(node, list) or h < HEADER + 2 * PAD + FILE_SIZE:
            tiles += tile(name, size_text(total(node), unit, thousands), x, y, w, h, color, f"tile-{i}")
            continue
        folders.append({"type": "rectangle", "x": x, "y": y, "width": w, "height": h, "roughness": 0,
                        "roundness": None, "strokeColor": shade(color, 7), "strokeWidth": 2,
                        "backgroundColor": "#ffffff", "fillStyle": "solid"})
        title = folder_title(name, size_text(total(node), unit, thousands), w)
        if title:
            folders.append(text(x + INSET + 2, y + INSET, title, FOLDER_SIZE, shade(color, 7), font=TITLE_FONT))
        rects = squarify([v for _, v in node], x + PAD, y + HEADER, w - 2 * PAD, h - HEADER - PAD)
        for j, ((file, n), rect) in enumerate(zip(node, rects)):
            tiles += tile(file, size_text(n, unit, thousands), *rect, color, f"tile-{i}-{j}")
    return folders + tiles
