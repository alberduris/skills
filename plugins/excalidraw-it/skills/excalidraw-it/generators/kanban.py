"""A kanban board: one lane per column, its cards stacked in it, all at one width.

    columns:                 # name: cards, or name: {color, limit, cards}
      Por hacer:
        - {ticket: EXC-21, title: Barras con xychart, tag: alta, person: Claude}
        - Limpiar el sandbox           # a card with only its title
      En curso:
        color: blue
        limit: 2                       # its limit of cards in progress: En curso  1/2
        cards:
          - {ticket: EXC-20, title: Kanban, tag: alta, person: Claude}
    tags: {alta: red, media: yellow, baja: gray}   # tag: color of its pill; these by default
    people: {Claude: orange, Operador: blue}       # person: color of the avatar

Each card is the piece card; \\n in a title breaks a line. The first column is
gray and the last green by default, and those between blue, violet, teal and
orange in turn. A tag with no color is gray; a person with no color takes the
next of blue, orange, teal, grape and pink. A column name cannot hold a comma.
"""
import re

from canvas import piece
from palette import OPEN_COLOR
from schema import DataError, choice, entries, fields, listed, number

GAP, HEADER, CARD_GAP = 16, 52, 12
MIDDLE = ["blue", "violet", "teal", "orange"]
TAGS = {"alta": "red", "media": "yellow", "baja": "gray"}
PEOPLE = ["blue", "orange", "teal", "grape", "pink"]


def colors(where, mapping):
    return {str(k): choice(v, f"{where}.{k}", OPEN_COLOR) for k, v in mapping.items()}


def parsed_card(card, where):
    if not isinstance(card, dict):
        card = {"title": card}
    fields(card, where, ("title",), ("ticket", "tag", "person"))
    return {key: str(value) for key, value in card.items() if value is not None}


def parsed(data):
    fields(data, "top level", ("columns",), ("tags", "people"))
    tags = {**TAGS, **colors("tags", entries(data.get("tags"), "tags", optional=True))}
    people = colors("people", entries(data.get("people"), "people", optional=True))
    columns = []
    names = list(entries(data["columns"], "columns"))
    for i, name in enumerate(names):
        where, value = f"columns.{name}", data["columns"][name]
        if "," in str(name):
            raise DataError(f"{where}: a column name cannot hold a comma, the lane piece splits its titles at them")
        color = "gray" if i == 0 else "green" if i == len(names) - 1 else MIDDLE[(i - 1) % len(MIDDLE)]
        limit = None
        if isinstance(value, dict):
            fields(value, where, ("cards",), ("color", "limit"))
            color = choice(value.get("color", color), f"{where}.color", OPEN_COLOR)
            limit = number(value["limit"], f"{where}.limit", low=1, whole=True) if "limit" in value else None
            value = value["cards"]
        cards = [parsed_card(card, f"{where}[{j}]") for j, card in enumerate(listed(value, where))]
        columns.append((str(name), color, limit, cards))
    for _, _, _, cards in columns:  # the people with no color, in the order they first appear
        for card in cards:
            if "person" in card and card["person"] not in people:
                people[card["person"]] = PEOPLE[len(people) % len(PEOPLE)]
    return columns, tags, people


def options(card, tags, people):
    """The flags of the piece card for one card of the YAML."""
    out = dict(card)
    if "tag" in card:
        out["tag_color"] = tags.get(card["tag"], "gray")
    if "person" in card:
        out["person_color"] = people[card["person"]]
    return out


def build(data):
    columns, tags, people = parsed(data)
    specs = [[options(card, tags, people) for card in cards] for *_, cards in columns]
    sizes = [piece("card", **spec)[0] for column in specs for spec in column]  # the first element is the box
    card_w = max((box["width"] for box in sizes), default=200)  # 200: a board with no card at all
    card_h = max((box["height"] for box in sizes), default=0)
    lane_w = card_w + 2 * GAP
    height = GAP + max([len(column) for column in specs] + [1]) * (card_h + CARD_GAP) - CARD_GAP + GAP
    lanes, cards = [], []
    for i, ((name, color, limit, items), column) in enumerate(zip(columns, specs)):
        x = i * (lane_w + GAP)
        title = f"{name}  {len(items)}/{limit}" if limit else f"{name}  {len(items)}"
        lanes += piece("lane-with-header", titles=title, colors=color, x=x, y=0, width=lane_w, gap=0, height=height,
                       header_height=HEADER)
        for j, spec in enumerate(column):
            slug = re.sub(r"[^a-z0-9]+", "-", spec.get("ticket", spec["title"]).lower()).strip("-")
            cards += piece("card", **spec, x=x + GAP, y=HEADER + GAP + j * (card_h + CARD_GAP), width=card_w,
                           group_id=f"card-{slug}")
    return lanes + cards
