"""A card: a white rounded box with a title and, if given, a ticket, a tag and a person, all in one group.

The ticket sits top left in gray, the tag top right in a pill, the title under
them, and the person at the foot as an avatar with their initial, beside their
name. Without --width the card is as wide as its content; size(args) gives its
width and height, to line up a column of cards at one width.
Prints the bounds of the card to stderr, to place the next one.
"""
import re
import sys

import fonts
from palette import OPEN_COLOR, shade

FONT, TITLE_SIZE, SMALL = 5, 16, 13
PAD, TOP_GAP, FOOT_GAP, AVATAR, TAG_PAD = 14, 8, 12, 22, 8
BORDER, MUTED = "#adb5bd", "#868e96"
LINE = 1.25


def add_arguments(parser):
    parser.add_argument("--title", required=True, help="the card text; \\n breaks a line")
    parser.add_argument("--ticket", help="an id in gray, top left")
    parser.add_argument("--tag", help="a word in a pill, top right: a priority, a status")
    parser.add_argument("--tag-color", default="gray", help=f"shade 1 fills the pill, shade 9 writes it: {', '.join(OPEN_COLOR)}")
    parser.add_argument("--person", help="who owns the card, at the foot")
    parser.add_argument("--person-color", default="blue", help="the avatar, in shade 7")
    parser.add_argument("--x", type=float, default=0, help="left edge of the card")
    parser.add_argument("--y", type=float, default=0, help="top edge of the card")
    parser.add_argument("--width", type=float, help="defaults to the width of the content")
    parser.add_argument("--group-id", help="shared groupIds value; defaults to card- plus the ticket or the title")


def tag_width(tag):
    return fonts.width(tag, FONT, SMALL) * 1.2 + 2 * TAG_PAD


def size(args):
    title = args.title.replace("\\n", "\n")
    top = args.ticket or args.tag
    rows = [fonts.width(title, FONT, TITLE_SIZE),
            (fonts.width(args.ticket, FONT, SMALL) if args.ticket else 0) + (12 + tag_width(args.tag) if args.tag else 0),
            AVATAR + 8 + fonts.width(args.person, FONT, SMALL) if args.person else 0]
    height = (PAD + (SMALL * LINE + TOP_GAP if top else 0) + (title.count("\n") + 1) * TITLE_SIZE * LINE
              + (FOOT_GAP + AVATAR if args.person else 0) + PAD)
    return max(rows) * 1.2 + 2 * PAD, height


def build(args):
    for color in (args.tag_color, args.person_color):
        if color not in OPEN_COLOR:
            sys.exit(f"unknown color: {color}")
    width, height = size(args)
    width = args.width or width
    x, y = args.x, args.y
    slug = re.sub(r"[^a-z0-9]+", "-", (args.ticket or args.title).lower()).strip("-")
    common = {"groupIds": [args.group_id or f"card-{slug}"]}
    small = {"fontSize": SMALL, "fontFamily": FONT}
    out = [{"type": "rectangle", "x": x, "y": y, "width": width, "height": height, "strokeColor": BORDER,
            "backgroundColor": "#ffffff", "fillStyle": "solid", "roundness": {"type": 3}, "roughness": 0, **common}]
    line_y = y + PAD
    if args.ticket:
        out.append({"type": "text", "x": x + PAD, "y": line_y, "text": args.ticket, "strokeColor": MUTED, **small, **common})
    if args.tag:
        fill = shade(args.tag_color, 1)
        out.append({"type": "rectangle", "x": x + width - PAD - tag_width(args.tag), "y": line_y - 3,
                    "width": tag_width(args.tag), "height": SMALL * LINE + 6, "strokeColor": fill,
                    "backgroundColor": fill, "fillStyle": "solid", "roundness": {"type": 3}, "roughness": 0,
                    "label": {"text": args.tag, "strokeColor": shade(args.tag_color, 9), **small}, **common})
    if args.ticket or args.tag:
        line_y += SMALL * LINE + TOP_GAP
    out.append({"type": "text", "x": x + PAD, "y": line_y, "text": args.title.replace("\\n", "\n"),
                "fontSize": TITLE_SIZE, "fontFamily": FONT, "strokeColor": "#1e1e1e", **common})
    if args.person:
        avatar_y = y + height - PAD - AVATAR
        text_y = avatar_y + (AVATAR - SMALL * LINE) / 2
        ink = shade(args.person_color, 7)
        out += [
            {"type": "ellipse", "x": x + PAD, "y": avatar_y, "width": AVATAR, "height": AVATAR, "strokeColor": ink,
             "backgroundColor": ink, "fillStyle": "solid", "roughness": 0, **common},
            # add reads the x of a centred text as its centre
            {"type": "text", "x": x + PAD + AVATAR / 2, "y": text_y, "text": args.person[0].upper(),
             "strokeColor": "#ffffff", "textAlign": "center", **small, **common},
            {"type": "text", "x": x + PAD + AVATAR + 8, "y": text_y, "text": args.person, "strokeColor": MUTED,
             **small, **common},
        ]
    print(f"card: x {x:g}..{x + width:g}, y {y:g}..{y + height:g}", file=sys.stderr)
    return out
