"""Lanes, each one a light gray body with a colored header on top, or on its left with --across.

One lane per actor, system or phase; draw the steps inside the bodies. Lanes
stand side by side, or with --across lie one under the other, for a flow that
runs left to right.
Prints the bounds of each body to stderr, to place the steps.
"""
import sys

from palette import OPEN_COLOR, shade

BODY_STYLE = {"backgroundColor": "#f8f9fa", "strokeColor": "#dee2e6", "strokeWidth": 1}


def add_arguments(parser):
    parser.add_argument("--titles", required=True, help="lane titles, comma-separated, left to right or top to bottom")
    parser.add_argument("--colors", default="blue,violet,teal",
                        help=f"header colors, comma-separated, repeated when there are more lanes: {', '.join(OPEN_COLOR)}")
    parser.add_argument("--x", type=float, default=0, help="left edge of the first lane")
    parser.add_argument("--y", type=float, default=0, help="top edge of the headers")
    parser.add_argument("--width", type=float, default=300, help="width of each lane; with --across, of each body")
    parser.add_argument("--gap", type=float, default=20, help="space between two lanes")
    parser.add_argument("--height", type=float, default=960, help="height of each body, below its header; with --across, of each lane")
    parser.add_argument("--header-height", type=float, default=60)
    parser.add_argument("--across", action="store_true", help="lanes one under the other, each header on the left of its body")
    parser.add_argument("--header-width", type=float, default=180, help="with --across, width of each header")


def build(args):
    titles = [title.strip() for title in args.titles.split(",")]
    colors = [color.strip() for color in args.colors.split(",")]
    unknown = [color for color in colors if color not in OPEN_COLOR]
    if unknown:
        sys.exit(f"unknown colors: {', '.join(unknown)}")

    bodies, headers = [], []
    across = getattr(args, "across", False)  # callers that build the args themselves may leave it out
    for i, title in enumerate(titles):
        if across:
            x, y = args.x, args.y + i * (args.height + args.gap)
            header = (x, y, args.header_width, args.height)
            body = (x + args.header_width, y, args.width, args.height)
        else:
            x = args.x + i * (args.width + args.gap)
            header = (x, args.y, args.width, args.header_height)
            body = (x, args.y + args.header_height, args.width, args.height)
        color = colors[i % len(colors)]
        fill, border = shade(color, 1), shade(color, 7)  # the header: shade 1 fills it, shade 7 draws its border
        bx, by, bw, bh = body
        bodies.append({"type": "rectangle", "x": bx, "y": by, "width": bw, "height": bh,
                       "fillStyle": "solid", "roughness": 0, **BODY_STYLE})
        hx, hy, hw, hh = header
        headers.append({"type": "rectangle", "x": hx, "y": hy, "width": hw, "height": hh,
                        "backgroundColor": fill, "strokeColor": border, "fillStyle": "solid", "roughness": 0,
                        "label": {"text": title, "fontSize": 20, "fontFamily": 7}})
        print(f"lane {i + 1} {title!r}: body x {bx:g}..{bx + bw:g}, y {by:g}..{by + bh:g}", file=sys.stderr)
    return bodies + headers
