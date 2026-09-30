"""A tree view: one row per file or folder, indented one step per level, with a column of descriptions.

    tree:                          # name: what is under it
      excalidraw-it/:              # a folder: the mapping of its children
        ledger/:                   # {note, highlight, children} to describe a folder
          note: lo que la skill sabe
          children:
            sins.yaml: {note: 7 errores, cada uno con su regla, highlight: true}
            types.yaml: 22 tipos, con su ruta y su receta     # a file: its description, or nothing
        SKILL.md:

A folder is a name ending with /, or one with children; its name is blue after a
filled icon, a file's is dark after an outlined one. The names are in Cascadia,
the descriptions in gray in one column right of the longest name. A highlighted
row has a yellow strip behind its name and its description; say in the note what
the yellow means. A folder's mapping is read as {note, highlight, children} only
when it has the key children. Quote a note with a comma inside {…}.
"""
import fonts
from canvas import FONT, INK, LINE, MUTED, text
from palette import shade
from schema import DataError, entries, fields

CODE, SIZE = 3, 15
ROW, INDENT, ICON, GAP, DESC_GAP = 30, 28, 16, 8, 56
EDGE = "#adb5bd"


def described(name, value):
    """Whether a mapping describes its row as {note, highlight, children}, rather than list a folder's children."""
    return "children" in value or (not name.endswith("/") and set(value) <= {"note", "highlight"})


def rows(tree, where, depth=0, parent=None, out=None):
    """(depth, name, note, highlight, folder, parent row) per row, top to bottom."""
    out = [] if out is None else out
    for name, value in entries(tree, where).items():
        name, here = str(name), f"{where}.{name}"
        note, highlight, children = None, False, None
        if isinstance(value, dict) and described(name, value):
            fields(value, here, (), ("note", "highlight", "children"))
            note, highlight, children = value.get("note"), bool(value.get("highlight")), value.get("children")
        elif isinstance(value, dict):
            if set(value) & {"note", "highlight"}:
                raise DataError(f"{here}: note or highlight among other keys; quote a note that has a comma in "
                                "a {…} mapping, and put a folder's children under children")
            children = value
        elif value is not None:
            note = value
        if isinstance(note, (dict, list)):
            raise DataError(f"{here}: a description is a text, got {note!r}")
        folder = name.endswith("/") or bool(children)
        out.append((depth, name, None if note is None else str(note), highlight, folder, parent))
        if children:
            rows(children, here, depth + 1, len(out) - 1, out)
    return out


def last_child(table, i):
    """Whether no sibling follows row i."""
    return all(row[5] != table[i][5] for row in table[i + 1:])


def build(data):
    fields(data, "top level", ("tree",))
    table = rows(data["tree"], "tree")
    names_end = max(depth * INDENT + ICON + GAP + fonts.width(name, CODE, SIZE) for depth, name, *_ in table)
    edges, out = [], []
    for i, (depth, name, note, highlight, folder, parent) in enumerate(table):
        cy, x = i * ROW + ROW / 2, depth * INDENT
        # the parent's line runs down to its last child, and a tick reaches each child
        if parent is not None:
            edges.append({"type": "line", "x": x - INDENT + ICON / 2, "y": cy,
                          "points": [[0, 0], [INDENT - ICON / 2 - 4, 0]]})
            if last_child(table, i):
                first = parent * ROW + ROW / 2 + 9
                edges.append({"type": "line", "x": x - INDENT + ICON / 2, "y": first, "points": [[0, 0], [0, cy - first]]})
        if folder:
            out.append({"type": "rectangle", "x": x, "y": cy - 6, "width": ICON, "height": 12, "roughness": 0,
                        "strokeColor": shade("blue", 6), "backgroundColor": shade("blue", 6), "fillStyle": "solid",
                        "roundness": {"type": 3}})
        else:
            out.append({"type": "rectangle", "x": x + 2, "y": cy - 7.5, "width": ICON - 4, "height": 15,
                        "roughness": 0, "strokeColor": MUTED, "backgroundColor": "#ffffff", "fillStyle": "solid"})
        text_x, text_y = x + ICON + GAP, cy - SIZE * LINE / 2
        if highlight:
            yellow = shade("yellow", 1)
            end = names_end + DESC_GAP + fonts.width(note, FONT, SIZE) if note else text_x + fonts.width(name, CODE, SIZE)
            out.append({"type": "rectangle", "x": text_x - 6, "y": text_y - 3, "width": end - text_x + 12,
                        "height": SIZE * LINE + 6, "strokeColor": yellow, "backgroundColor": yellow,
                        "fillStyle": "solid", "roughness": 0, "roundness": {"type": 3}})
        out.append(text(text_x, text_y, name, SIZE, shade("blue", 7) if folder else INK, font=CODE))
        if note:
            out.append(text(names_end + DESC_GAP, text_y, note, SIZE, MUTED))
    return [{**edge, "strokeColor": EDGE, "strokeWidth": 1, "roughness": 0} for edge in edges] + out
