"""A requirement diagram: requirements and the elements that satisfy or verify them, as boxes on a grid.

    nodes:                     # id: {kind, name, at: [column, row], columns, fields}
      r1: {kind: requirement, name: Diagramas sin slop, at: [1, 0], columns: 2,
           fields: {id: 1, texto: el operador no tiene que retocar nada, riesgo: alto, verificación: demostración}}
      r11: {kind: functionalRequirement, name: Lint limpio, at: [1, 1], fields: {id: 1.1, riesgo: medio}}
      qa: {kind: element, name: QA del operador, at: [0, 0], fields: {tipo: revisión, doc: la captura}}
    edges:                     # [from, to, relation], as Mermaid writes them
      - [r1, r11, contains]              # from the parent to the child
      - [qa, r1, verifies]               # from the element to the requirement

The kinds are Mermaid's: requirement, functionalRequirement,
interfaceRequirement, performanceRequirement, physicalRequirement,
designConstraint, and element. The relations: contains, copies, derives,
satisfies, verifies, refines and traces. The fields are key: value lines, in
the order and the words you write them: a requirement's id, text, risk and
verification method, an element's type and doc ref. You place each node on
the grid, an element under or beside what it satisfies or verifies and a
parent above its children, spanning their columns so it sits centred over
them. The generator draws a requirement violet and an element teal, each with
«its kind» above its name, wraps a long value with its next lines indented,
makes every box as wide as the widest, and runs each relation as a dashed
arrow labelled «its verb», level at the headers' height between boxes on one
row; contains runs elbowed from the child up to the parent's foot, with a
circle there. Keep the path of an arrow that skips a column or a row empty.
"""
from canvas import wrapped
from compartments import SIZE, boxes, drawn, head_height, joined, level_or_straight, size, up_to_feet
from grid import cell
from schema import DataError, choice, entries, fields, listed

KINDS = ("requirement", "functionalRequirement", "interfaceRequirement", "performanceRequirement",
         "physicalRequirement", "designConstraint", "element")
RELATIONS = ("contains", "copies", "derives", "satisfies", "verifies", "refines", "traces")
FIELD_W = 230  # a key: value line wider than this wraps
INDENT = "    "


def field_lines(values, where):
    """The key: value lines of a box, a long one wrapped with its next lines indented."""
    lines = []
    for key, value in entries(values, where).items():
        lines.append(wrapped(f"{key}: {value}", SIZE, FIELD_W).replace("\n", "\n" + INDENT))
    return lines


def parsed(data):
    fields(data, "top level", ("nodes",), ("edges",))
    nodes, cells = {}, {}
    for n, value in entries(data["nodes"], "nodes").items():
        where, n = f"nodes.{n}", str(n)
        fields(value, where, ("kind", "name", "at", "fields"), ("columns",))
        cells[n] = cell(value, where, spans=("columns",))
        kind = choice(value["kind"], f"{where}.kind", KINDS)
        nodes[n] = f"«{kind}»\n{value['name']}", field_lines(value["fields"], f"{where}.fields"), \
            "teal" if kind == "element" else "violet"
    edges = []
    for i, edge in enumerate(listed(data.get("edges"), "edges")):
        if not isinstance(edge, list) or len(edge) != 3:
            raise DataError(f"edges[{i}]: expected [from, to, relation], got {edge!r}")
        a, b = (choice(str(end), f"edges[{i}]", nodes) for end in edge[:2])
        edges.append((a, b, choice(edge[2], f"edges[{i}]", RELATIONS)))
    return nodes, cells, edges


def build(data):
    nodes, cells, edges = parsed(data)
    sizes = {n: size(title, [lines]) for n, (title, lines, _) in nodes.items()}
    box = boxes(cells, sizes, [(a, b, f"«{relation}»") for a, b, relation in edges])
    heads = {n: head_height(title) for n, (title, _, _) in nodes.items()}
    # contains: from the child, below, up to the parent
    upward = [(b, a) for a, b, relation in edges if relation == "contains" and cells[a].last_row < cells[b].row]
    feet = up_to_feet(upward, box)
    out = []
    for n, (title, lines, color) in nodes.items():
        out += drawn(n, box[n], title, [lines], color, f"requirement-{n}")
    for a, b, relation in edges:
        label = f"«{relation}»"
        if relation != "contains":
            start, end = level_or_straight(box[a], heads[a], box[b], heads[b])
            out.append(joined(a, box[a], start, b, box[b], end, label, strokeStyle="dashed"))
        elif (b, a) in feet:
            out.append(joined(b, box[b], [0.5, 0], a, box[a], [feet[b, a], 1], label, elbowed=True,
                              endArrowhead="circle_outline"))
        else:  # a child beside its parent: straight, the circle at the parent
            start, end = level_or_straight(box[b], heads[b], box[a], heads[a])
            out.append(joined(b, box[b], start, a, box[a], end, label, endArrowhead="circle_outline"))
    return out
