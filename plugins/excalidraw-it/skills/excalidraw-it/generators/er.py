"""An entity-relationship diagram: one table per entity, placed on a grid, joined by crow's-foot relations.

    entities:                  # name: {at: [column, row], columns, attributes, color}
      Workspace: {at: [0, 0], attributes: {id: PK, name}}           # name: key, or a name with no key
      Collection: {at: [1, 0], attributes: {id: PK, workspaceId: FK, name}}
    relations:                 # [from, to, cardinality at from, cardinality at to, verb]
      - [Workspace, Collection, exactly_one, zero_or_many, contiene]
      - [Element, Element, zero_or_one, zero_or_many, ata]            # to itself: a U under the table

The cardinalities: exactly_one, zero_or_one, one_or_many and zero_or_many,
drawn as crow's-foot heads on both ends. You place each entity on the grid;
the generator makes every table as wide as the widest, with the keys
right-aligned in gray, sizes the gaps for the verbs, runs a relation level at
the headers' height between tables on one row and straight otherwise, and
leaves room under a table for its self-relation, which takes the middle of
the table's foot, so keep the table's other relations off it. A table is blue
unless it names another color. Keep the path of a relation that skips a column
or a row empty.
"""
import fonts
from canvas import FONT, INK, height
from compartments import EDGE_COLOR, EDGE_SIZE, boxes, drawn, head_height, joined, level_or_straight, size
from grid import LABEL_CLEAR, cell
from palette import OPEN_COLOR
from schema import DataError, choice, entries, fields, listed

CARDINALITIES = ("exactly_one", "zero_or_one", "one_or_many", "zero_or_many")
DROP = 60  # how far a self-relation's U runs under its table


def parsed(data):
    fields(data, "top level", ("entities",), ("relations",))
    entities, cells = {}, {}
    for n, value in entries(data["entities"], "entities").items():
        where, n = f"entities.{n}", str(n)
        fields(value, where, ("at", "attributes"), ("columns", "color"))
        cells[n] = cell(value, where, spans=("columns",))
        attributes = [[str(name), str(key or "")]
                      for name, key in entries(value["attributes"], f"{where}.attributes").items()]
        entities[n] = attributes, choice(value.get("color", "blue"), f"{where}.color", OPEN_COLOR)
    relations = []
    for i, relation in enumerate(listed(data.get("relations"), "relations")):
        if not isinstance(relation, list) or len(relation) != 5:
            raise DataError(f"relations[{i}]: expected [from, to, cardinality at from, cardinality at to, verb], "
                            f"got {relation!r}")
        a, b = (choice(str(end), f"relations[{i}]", entities) for end in relation[:2])
        ca, cb = (choice(c, f"relations[{i}]", CARDINALITIES) for c in relation[2:4])
        relations.append((a, b, ca, cb, str(relation[4])))
    return entities, cells, relations


def self_relation(n, box, ca, cb, verb):
    """A U under the table, from its foot back to its foot, wide enough for the verb on its bottom."""
    x, y, w, h = box
    half = min(0.45, max(0.25, (fonts.width(verb, FONT, EDGE_SIZE) / 2 + LABEL_CLEAR) / w))
    return {"type": "arrow", "x": x + (0.5 - half) * w, "y": y + h,
            "points": [[0, 0], [0, DROP], [2 * half * w, DROP], [2 * half * w, 0]],
            "strokeColor": EDGE_COLOR, "strokeWidth": 2, "roughness": 0, "roundness": None,
            "startArrowhead": f"cardinality_{ca}", "endArrowhead": f"cardinality_{cb}",
            "startBinding": {"elementId": n, "fixedPoint": [0.5 - half, 1], "mode": "inside"},
            "endBinding": {"elementId": n, "fixedPoint": [0.5 + half, 1], "mode": "inside"},
            "label": {"text": verb, "fontSize": EDGE_SIZE, "fontFamily": FONT, "strokeColor": INK}}


def under(upper, lower):
    """Whether the lower cell sits in the next row, in a column of the upper one."""
    return lower.row == upper.last_row + 1 and lower.column <= upper.last_column and upper.column <= lower.last_column


def build(data):
    entities, cells, relations = parsed(data)
    sizes = {n: size(n, [attributes]) for n, (attributes, _) in entities.items()}
    # a table with a self-relation takes the room of its U and verb in its row, when a table sits under it
    room = {a: DROP + height(verb, EDGE_SIZE) / 2 + LABEL_CLEAR for a, b, _, _, verb in relations
            if a == b and any(under(cells[a], c) for c in cells.values())}
    padded = {n: (w, h + room.get(n, 0)) for n, (w, h) in sizes.items()}
    box = boxes(cells, padded, [(a, b, verb) for a, b, _, _, verb in relations if a != b], where="entities")
    box = {n: (x, y, w, sizes[n][1]) for n, (x, y, w, _) in box.items()}
    out = []
    for n, (attributes, color) in entities.items():
        out += drawn(n, box[n], n, [attributes], color, f"er-{n}")
    for a, b, ca, cb, verb in relations:
        if a == b:
            out.append(self_relation(a, box[a], ca, cb, verb))
            continue
        start, end = level_or_straight(box[a], head_height(a), box[b], head_height(b))
        out.append(joined(a, box[a], start, b, box[b], end, verb, startArrowhead=f"cardinality_{ca}",
                          endArrowhead=f"cardinality_{cb}"))
    return out
