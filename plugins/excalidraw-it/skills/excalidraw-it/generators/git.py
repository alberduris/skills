"""A git graph: one row per branch and one column per commit, replayed from commands as in Mermaid's gitGraph.

    main: main                 # the branch the history starts on; main by default
    colors: {fix: red}         # branch: color; the others take blue, violet, teal, red… in order of creation
    history:                   # one command per item
      - commit: init           # a commit on the current branch, with its message
      - branch: types          # a branch from the current commit, which becomes the current branch
      - commit: types.yaml
      - checkout: main         # the current branch
      - commit: fonts.py
        tag: v0.1              # a tag above a commit or a merge
      - merge: types           # merges types into the current branch
        tag: v0.2

Rows run top to bottom in order of creation, and each column is as wide as the
longest message or tag needs; a long message breaks into two lines. A new branch drops right after the commit it
starts from, and a merge rises just before its merge commit, so no line runs
over the row of another branch.
"""

import fonts
from canvas import FONT, TITLE_FONT, height, path, text, wrapped
from palette import OPEN_COLOR, shade
from schema import DataError, choice, entries, fields, listed

BRANCH_SIZE, LABEL_SIZE, TAG_SIZE = 18, 14, 14
MIN_STEP, LANE, DOT, TAG_H = 110, 100, 24, 28
WRAP = 140                   # a message wider than this breaks into balanced lines
GUIDE, LABEL, TAG_FILL = "#dee2e6", "#495057", "#fff3bf"
COLORS = ["blue", "violet", "teal", "red", "orange", "grape", "cyan", "green", "pink", "yellow"]
COMMANDS = ("commit", "branch", "checkout", "merge")


def replayed(history, main):
    """Every commit and merge in order, each on its branch, and the lines that join branches: (from, to, kind)."""
    rows, current, heads, starts = [main], main, {}, {}
    commits, links = [], []
    for i, item in enumerate(listed(history, "history")):
        where = f"history[{i}]"
        given = [command for command in COMMANDS if isinstance(item, dict) and command in item]
        if len(given) != 1:
            raise DataError(f"{where}: expected one of {', '.join(COMMANDS)}, got {item!r}")
        command = given[0]
        fields(item, where, (command,), ("tag",) if command in ("commit", "merge") else ())
        value = item[command]
        if command == "branch":
            name = str(value)
            if name in rows:
                raise DataError(f"{where}: branch {name} exists already")
            if current not in heads:
                raise DataError(f"{where}: {current} has no commit yet to branch from")
            rows.append(name)
            starts[name], current = heads[current], name
            continue
        if command == "checkout":
            current = choice(str(value), where, rows)
            continue
        node = {"id": f"c{len(commits)}", "branch": current, "merge": command == "merge",
                "label": None if command == "merge" or value is None else wrapped(str(value), LABEL_SIZE, WRAP),
                "tag": str(item["tag"]) if item.get("tag") is not None else None}
        if current in starts:
            links.append((starts.pop(current), node["id"], "off"))
        if command == "merge":
            source = choice(str(value), where, rows)
            if source == current:
                raise DataError(f"{where}: cannot merge {current} into itself")
            if source not in heads:
                raise DataError(f"{where}: {source} has no commit to merge")
            links.append((heads[source], node["id"], "merge"))
        commits.append(node)
        heads[current] = node["id"]
    if not commits:
        raise DataError("history: expected at least one commit")
    return rows, commits, links


def curve(ax, ay, bx, by, kind, step):
    """A branch or a merge line: level along the row of its own branch, and an S between the rows. A branch
    drops right after the commit it starts from, a merge rises just before its merge commit. Returns the
    width of the S and the height of the line at any x between the two commits."""
    wide = step if bx - ax <= step else step / 2  # the whole step when no commit sits between them
    x0 = ax if kind == "off" else bx - wide

    def y_at(x):
        t = min(max((x - x0) / wide, 0), 1)
        return ay + (by - ay) * (3 * t * t - 2 * t ** 3)
    return wide, y_at


def between(ax, ay, bx, by, kind, step):
    """The points of the line, sampled at even steps along the smoothstep: a curve through a corner
    overshoots it, and a curve through uneven steps loops."""
    wide, y_at = curve(ax, ay, bx, by, kind, step)
    n = round((bx - ax) / (wide / 6))
    return [(x, y_at(x)) for x in (ax + (bx - ax) * i / n for i in range(n + 1))]


def label_spans(commits, links, row_of, step):
    """Where each message sits beside its dot, (left, right) from the dot: centred, else left or right of it,
    whichever no line crosses. A line that leaves a commit for a lower row crosses a centred message."""
    at = {c["id"]: (i * step, row_of[c["branch"]] * LANE) for i, c in enumerate(commits)}
    lines = [(at[a][0], at[b][0], curve(*at[a], *at[b], kind, step)[1]) for a, b, kind in links]
    spans = {}
    for c in commits:
        if not c["label"]:
            continue
        x, y = at[c["id"]]
        w, h = fonts.width(c["label"], FONT, LABEL_SIZE), height(c["label"], LABEL_SIZE)
        top, bottom = y + DOT / 2 + 3, y + DOT / 2 + 9 + h

        def crossings(span):
            return sum(top <= y_at(px) <= bottom for x0, x1, y_at in lines
                       for px in range(int(max(x + span[0], x0)), int(min(x + span[1], x1)) + 1, 2))
        spans[c["id"]] = min([(-w / 2, w / 2), (4 - w, 4), (-4, w - 4)], key=crossings)
    return spans


def fitted_step(commits, links, row_of):
    """The step between columns, and the spans of the messages: wide enough for every tag and message to
    clear the one beside it."""
    step = max([MIN_STEP] + [tag_width(c["tag"]) + 16 for c in commits if c["tag"]])
    for _ in range(4):  # a wider step reshapes the lines, which may move a message
        spans = label_spans(commits, links, row_of, step)
        need = max([step] + [spans[a["id"]][1] - spans[b["id"]][0] + 20
                             for a, b in zip(commits, commits[1:]) if a["id"] in spans and b["id"] in spans])
        if need <= step:
            break
        step = need
    return step, spans


def headless(points, start, end, color, curved=False):
    return path("arrow", points, roundness={"type": 2} if curved else None, startArrowhead=None, endArrowhead=None,
                strokeColor=color, strokeWidth=3, roughness=0,
                startBinding={"elementId": start, "fixedPoint": [0.5, 0.5], "mode": "inside"},
                endBinding={"elementId": end, "fixedPoint": [0.5, 0.5], "mode": "inside"})


def tag_width(tag):
    return fonts.width(tag, FONT, TAG_SIZE) * 1.2 + 20


def build(data):
    fields(data, "top level", ("history",), ("main", "colors"))
    rows, commits, links = replayed(data["history"], str(data.get("main", "main")))
    given = {str(b): choice(c, f"colors.{b}", OPEN_COLOR)
             for b, c in entries(data.get("colors"), "colors", optional=True).items()}
    for branch in given:
        choice(branch, "colors", rows)
    free = iter(c for c in COLORS * len(rows) if c not in given.values())
    color_of = {name: shade(given[name] if name in given else next(free), 7) for name in rows}
    row_of = {name: i for i, name in enumerate(rows)}

    step, spans = fitted_step(commits, links, row_of)
    at = {c["id"]: (i * step, row_of[c["branch"]] * LANE) for i, c in enumerate(commits)}
    branch_of = {c["id"]: c["branch"] for c in commits}
    end = (len(commits) - 1) * step + step / 2
    name_w = max(fonts.width(name, TITLE_FONT, BRANCH_SIZE) for name in rows) * 1.2
    out = []
    for name in rows:
        y = row_of[name] * LANE
        out.append(text(-step / 2 - name_w - 16, y - BRANCH_SIZE * 0.65, name, BRANCH_SIZE, color_of[name],
                        font=TITLE_FONT))
        out.append({"type": "line", "x": -step / 2, "y": y, "points": [[0, 0], [end + step / 2, 0]],
                    "strokeColor": GUIDE, "strokeWidth": 1, "strokeStyle": "dashed", "roughness": 0})
        on_row = [c["id"] for c in commits if c["branch"] == name]
        if len(on_row) > 1:
            out.append(headless([at[on_row[0]], at[on_row[-1]]], on_row[0], on_row[-1], color_of[name]))
    for a, b, kind in links:
        (ax, ay), (bx, by) = at[a], at[b]
        out.append(headless(between(ax, ay, bx, by, kind, step), a, b,
                            color_of[branch_of[b] if kind == "off" else branch_of[a]], curved=True))
    for c in commits:
        x, y = at[c["id"]]
        color = color_of[c["branch"]]
        out.append({"type": "ellipse", "tempId": c["id"], "x": x - DOT / 2, "y": y - DOT / 2, "width": DOT,
                    "height": DOT, "strokeColor": color, "backgroundColor": "#ffffff" if c["merge"] else color,
                    "fillStyle": "solid", "strokeWidth": 4 if c["merge"] else 2, "roughness": 0})
        if c["label"]:  # add reads the x of a centred text as its centre, of a right-aligned one as its right
            left, right = spans[c["id"]]
            align = "center" if left == -right else "right" if right == 4 else "left"
            anchor = {"center": x, "right": x + right, "left": x + left}[align]
            out.append(text(anchor, y + DOT / 2 + 6, c["label"], LABEL_SIZE, LABEL, align=align))
        if c["tag"]:
            w = tag_width(c["tag"])
            out.append({"type": "rectangle", "x": x - w / 2, "y": y - DOT / 2 - 40, "width": w, "height": TAG_H,
                        "strokeColor": LABEL, "backgroundColor": TAG_FILL, "fillStyle": "solid",
                        "roundness": {"type": 3}, "roughness": 0,
                        "label": {"text": c["tag"], "fontSize": TAG_SIZE, "fontFamily": FONT}})
    return out
