"""A class diagram: one box per class in three compartments, placed on a grid, joined by UML relations.

    classes:                   # name: {at: [column, row], columns, stereotype, attributes, methods, color}
      Plugin: {at: [1, 0], columns: 2, stereotype: abstract, attributes: [+id], methods: [+load(path)]}
      Check: {at: [1, 1], methods: [+run(elements) Finding[]]}
      Linter: {at: [0, 1], attributes: [+checks], methods: [+run_checks(sceneId)]}
    relations:                 # [from, to, kind] or [from, to, kind, label]
      - [Check, Plugin, inherits]          # from the child up to the parent
      - [Linter, Check, aggregates, 1..*]  # from the whole to the part

The kinds: inherits and realizes run from the child up to the parent's foot,
elbowed, with a hollow triangle there, realizes dashed; aggregates and composes
run from the whole, with a hollow or a solid diamond there; associates is a
solid arrow and depends a dashed one. You place each class on the grid, a
parent above its children and spanning their columns so it sits centred over
them; the generator makes every box as wide as the widest, sizes the gaps for
the labels, and runs an arrow level at the headers' height between classes on
one row. A class is violet unless it names another color. Keep the path of an
arrow that skips a column or a row empty.
"""
from compartments import boxes, drawn, head_height, joined, level_or_straight, size, up_to_feet
from grid import cell
from palette import OPEN_COLOR
from schema import DataError, choice, entries, fields, listed

# kind: start head, end head, dashed, elbowed up to the parent
KINDS = {"inherits": (None, "triangle_outline", False, True), "realizes": (None, "triangle_outline", True, True),
         "aggregates": ("diamond_outline", None, False, False), "composes": ("diamond", None, False, False),
         "associates": (None, "arrow", False, False), "depends": (None, "arrow", True, False)}


def parsed(data):
    fields(data, "top level", ("classes",), ("relations",))
    classes, cells = {}, {}
    for n, value in entries(data["classes"], "classes").items():
        where = f"classes.{n}"
        fields(value, where, ("at",), ("columns", "stereotype", "attributes", "methods", "color"))
        n = str(n)
        cells[n] = cell(value, where, spans=("columns",))
        title = (f"«{value['stereotype']}»\n" if value.get("stereotype") else "") + n
        sections = [[str(line) for line in listed(value.get(part), f"{where}.{part}")]
                    for part in ("attributes", "methods")]
        classes[n] = title, sections, choice(value.get("color", "violet"), f"{where}.color", OPEN_COLOR)
    relations = []
    for i, relation in enumerate(listed(data.get("relations"), "relations")):
        if not isinstance(relation, list) or len(relation) not in (3, 4):
            raise DataError(f"relations[{i}]: expected [from, to, kind] or [from, to, kind, label], got {relation!r}")
        a, b = (choice(str(end), f"relations[{i}]", classes) for end in relation[:2])
        kind = choice(relation[2], f"relations[{i}]", KINDS)
        relations.append((a, b, kind, str(relation[3]) if len(relation) == 4 else None))
    return classes, cells, relations


def build(data):
    classes, cells, relations = parsed(data)
    sizes = {n: size(title, sections) for n, (title, sections, _) in classes.items()}
    box = boxes(cells, sizes, [(a, b, label) for a, b, _, label in relations if label], where="classes")
    heads = {n: head_height(title) for n, (title, _, _) in classes.items()}
    upward = [(a, b) for a, b, kind, _ in relations if KINDS[kind][3] and cells[b].last_row < cells[a].row]
    feet = up_to_feet(upward, box)
    out = []
    for n, (title, sections, color) in classes.items():
        out += drawn(n, box[n], title, sections, color, f"class-{n}")
    for a, b, kind, label in relations:
        start_head, end_head, dashed, _ = KINDS[kind]
        style = {"startArrowhead": start_head, "endArrowhead": end_head}
        if dashed:
            style["strokeStyle"] = "dashed"
        if (a, b) in feet:  # up from the child's top to its spot on the parent's foot
            start, end = [0.5, 0], [feet[a, b], 1]
            style["elbowed"] = True
        else:
            start, end = level_or_straight(box[a], heads[a], box[b], heads[b])
        out.append(joined(a, box[a], start, b, box[b], end, label, **style))
    return out
