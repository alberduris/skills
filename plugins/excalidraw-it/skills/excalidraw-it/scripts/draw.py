#!/usr/bin/env python3
"""Print the edit_scene_content `add` payload of a whole diagram, drawn from its data in YAML.

Each module in ../generators/ draws one diagram type of ledger/types.yaml. Its
file name is the type with underscores, its docstring says the YAML it takes,
and build(data) returns the elements. Only the module of the type asked for runs,
so a broken generator stops no other. Each group id gets a suffix of its own
drawing, so two drawings in one scene never share a group. Needs PyYAML.

    draw.py bar-chart data.yaml | write.py <sceneId>
"""
import argparse
import ast
import hashlib
import json
import math
import sys

import yaml

import fonts
from canvas import header, height
from modules import SKILL_DIR, load
from schema import DataError

QUOTING = "Quote a value YAML would read as something else: 'no', 'on', 'null', or one with : # [ ] { } , ? in it."
EVERY_TYPE = f"Every type also takes `title` and `note`, drawn above the diagram. {QUOTING}"


def docstring(path):
    """The docstring of a generator, read without running it."""
    try:
        return ast.get_docstring(ast.parse(path.read_text())) or "(no docstring)"
    except SyntaxError as error:
        return f"(does not parse: {error})"


def left_edge(element):
    """Where an element starts on the left. add reads the x of a centred text as its centre and the x of a
    right-aligned one as its right edge; a text turned a quarter spans its height across."""
    if element["type"] != "text":
        return element["x"] + min(x for x, _ in element.get("points") or [[0, 0]])
    family, size = element.get("fontFamily", 5), element.get("fontSize", 20)
    width = fonts.width(element["text"], family, size) if fonts.known(family) else 0
    centre = element["x"] + {"left": 0.5, "center": 0, "right": -0.5}[element.get("textAlign", "left")] * width
    if abs(math.sin(element.get("angle", 0))) > 0.9:
        width = height(element["text"], size)
    return centre - width / 2


def top_left(elements):
    """The left edge of the drawing, which the title lines up with, and its top edge."""
    return (min(left_edge(e) for e in elements),
            min(e["y"] + min(y for _, y in e.get("points") or [[0, 0]]) for e in elements))


def own_groups(elements):
    """Suffix each group id with a token of this drawing, drawn from its content so the output stays the same."""
    token = hashlib.sha1(json.dumps(elements, sort_keys=True).encode()).hexdigest()[:6]
    for element in elements:
        if element.get("groupIds"):
            element["groupIds"] = [f"{group}-{token}" for group in element["groupIds"]]
    return elements


def drawn(build, data, x, y):
    if not isinstance(data, dict):
        raise DataError(f"expected a mapping at the top of the YAML, got {data!r}")
    title, note = data.pop("title", None), data.pop("note", None)
    elements = build(data)
    elements = header(title, note, *top_left(elements)) + elements
    left, top = top_left(elements)
    for element in elements:
        element["x"] += x - left
        element["y"] += y - top
    return own_groups(elements)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="type", required=True, metavar="<type>")
    for path in sorted((SKILL_DIR / "generators").glob("*.py")):
        doc = docstring(path)
        command = commands.add_parser(path.stem.replace("_", "-"), help=doc.splitlines()[0], description=doc,
                                      epilog=EVERY_TYPE, formatter_class=argparse.RawDescriptionHelpFormatter)
        command.add_argument("data", nargs="?", type=argparse.FileType(encoding="utf-8"), default=sys.stdin,
                             help="the YAML file; stdin when left out")
        command.add_argument("--x", type=float, default=0, help="left edge of the diagram, title included")
        command.add_argument("--y", type=float, default=0, help="top edge of the diagram, title included")
        command.set_defaults(path=path)
    args = parser.parse_args()
    try:
        data = yaml.safe_load(args.data)
    except yaml.YAMLError as error:
        sys.exit(f"{args.type}: the YAML does not parse: {error}\n{QUOTING}")
    try:
        elements = drawn(load(args.path).build, data, args.x, args.y)
    except DataError as error:
        sys.exit(f"{args.type}: {error}")
    print(json.dumps(elements, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
