"""A rounded box with a small title, both in one group.

The title is standalone text 20 px from the left edge and 14 px from the top,
never a label bound to the box: Excalidraw puts a bound label back at 5 px from
the border each time the box moves, on top of the rounded corner.
Prints the free area inside the box to stderr, to place its members.
"""
import re
import sys
import unicodedata

from palette import OPEN_COLOR, shade

TITLE_LEFT, TITLE_TOP, TITLE_SIZE, PADDING = 20, 14, 20, 20


def add_arguments(parser):
    parser.add_argument("--title", required=True)
    parser.add_argument("--x", type=float, default=0, help="left edge of the box")
    parser.add_argument("--y", type=float, default=0, help="top edge of the box")
    parser.add_argument("--width", type=float, required=True)
    parser.add_argument("--height", type=float, required=True)
    parser.add_argument("--border", choices=["dashed", "solid"], default="dashed")
    parser.add_argument("--color", default="gray", help=f"border and title color: {', '.join(OPEN_COLOR)}")
    parser.add_argument("--group-id", help="shared groupIds value; defaults to box- plus the title in lowercase")


def group_id(title):
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    return "box-" + re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")


def title_element(title, box_x, box_y, color, group_ids):
    """The standalone title of a box at (box_x, box_y). Also used by checks/title_on_rounded_border.py."""
    return {"type": "text", "x": box_x + TITLE_LEFT, "y": box_y + TITLE_TOP,
            "width": len(title) * TITLE_SIZE, "height": TITLE_SIZE * 1.4, "text": title,
            "fontSize": TITLE_SIZE, "fontFamily": 7, "strokeColor": color, "groupIds": group_ids}


def build(args):
    if args.color not in OPEN_COLOR:
        sys.exit(f"unknown color: {args.color}")
    color = shade(args.color, 6)
    group = args.group_id or group_id(args.title)

    box = {"type": "rectangle", "x": args.x, "y": args.y, "width": args.width, "height": args.height,
           "strokeColor": color, "backgroundColor": "transparent", "strokeWidth": 2,
           "strokeStyle": args.border, "roundness": {"type": 3}, "roughness": 0, "groupIds": [group]}
    title = title_element(args.title, args.x, args.y, color, [group])

    top = args.y + TITLE_TOP + TITLE_SIZE * 1.4 + PADDING
    print(f"free area: x {args.x + PADDING:g}..{args.x + args.width - PADDING:g}, "
          f"y {top:g}..{args.y + args.height - PADDING:g}", file=sys.stderr)
    return [box, title]
