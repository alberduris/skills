"""An org chart: the root on top, departments side by side under a bus, and their teams stacked under each.

    root: Dirección general
    staff: [Asesoría jurídica]     # at most two roles on dashed lines: the first right of the trunk, the second left
    departments:                   # name: [teams], or name: {head, color, teams}; left to right
      Tecnología: {head: CTO, color: blue, teams: [Plataforma, Datos, Seguridad]}
      Finanzas: [Contabilidad, Control de gestión]

A department with a head shows it on a second line. A department with no color
takes the next of blue, violet, teal, orange, grape, cyan, green and pink that no
department chose. Every
column is as wide as the widest department or team, so the teams line up.
"""

import fonts
from canvas import FONT, INK, LINE, path, spare_colors
from palette import OPEN_COLOR, shade
from schema import DataError, choice, entries, fields, listed

ROOT_SIZE, DEPT_SIZE, TEAM_SIZE = 22, 20, 18
ROOT_H, STAFF_H, TEAM_H = 64, 48, 46
COLUMN_GAP, INDENT, TEAM_GAP, TEAMS_TOP = 40, 40, 18, 32
STAFF_Y, BUS_Y, DEPT_Y = 120, 184, 224  # the middle of the staff boxes, the bus, the top of the departments
STAFF_OUT = 60                           # from the trunk to a staff box
ROOT_FILL, EDGE = "#343a40", "#495057"
COLORS = ["blue", "violet", "teal", "orange", "grape", "cyan", "green", "pink"]


def lines(content):
    return content.count("\n") + 1


def fit(content, size):
    """Width of a box for the label: the server measures up to 19% wider than the font."""
    return fonts.width(content, FONT, size) * 1.2 + 32


def team_height(team):
    return max(TEAM_H, lines(team) * TEAM_SIZE * LINE + 20)


def parsed(data):
    fields(data, "top level", ("root", "departments"), ("staff",))
    staff = [str(role) for role in listed(data.get("staff"), "staff")]
    if len(staff) > 2:
        raise DataError(f"staff: at most two roles, one on each side of the trunk; got {len(staff)}")
    departments, spare = [], spare_colors(entries(data["departments"], "departments"), COLORS)
    for name, value in data["departments"].items():
        where, head, color = f"departments.{name}", None, None
        if isinstance(value, dict):
            fields(value, where, (), ("head", "color", "teams"))
            head = value.get("head")
            color = choice(value["color"], f"{where}.color", OPEN_COLOR) if "color" in value else None
            value = value.get("teams")
        teams = [str(team) for team in listed(value, where)]
        departments.append((str(name), None if head is None else str(head), color or next(spare), teams))
    return str(data["root"]), staff, departments


def box(tempid, x, y, width, height, label, size, stroke, fill, text_color=INK, dashed=False):
    return {"type": "rectangle", "tempId": tempid, "x": x, "y": y, "width": width, "height": height,
            "strokeColor": stroke, "backgroundColor": fill, "fillStyle": "solid", "roundness": {"type": 3},
            "strokeWidth": 2, "roughness": 0, "strokeStyle": "dashed" if dashed else "solid",
            "label": {"text": label, "fontSize": size, "fontFamily": FONT, "strokeColor": text_color}}


def polyline(points, start, end, color, dashed=False):
    """A headless arrow with square corners through `points`, bound at both ends: (element id, fixedPoint)."""
    return path("arrow", points, roundness=None, startArrowhead=None, endArrowhead=None, strokeColor=color,
                strokeWidth=2, roughness=0, strokeStyle="dashed" if dashed else "solid",
                startBinding={"elementId": start[0], "fixedPoint": start[1], "mode": "inside"},
                endBinding={"elementId": end[0], "fixedPoint": end[1], "mode": "inside"})


def build(data):
    root, staff, departments = parsed(data)
    labels = {name: name if head is None else f"{name}\n{head}" for name, head, _, _ in departments}
    dept_h = max(72 if lines(label) > 1 else 56 for label in labels.values())
    team_width = max([fit(t, TEAM_SIZE) for *_, teams in departments for t in teams], default=0)
    column = max(team_width + INDENT, max(fit(label, DEPT_SIZE) for label in labels.values()))
    trunk = (len(departments) * column + (len(departments) - 1) * COLUMN_GAP) / 2
    root_width = fit(root, ROOT_SIZE)
    out = [box("root", trunk - root_width / 2, 0, root_width, ROOT_H, root, ROOT_SIZE, ROOT_FILL, ROOT_FILL, "#ffffff")]
    for i, role in enumerate(staff):
        right, width = i == 0, fit(role, TEAM_SIZE)
        x = trunk + STAFF_OUT if right else trunk - STAFF_OUT - width
        role_id = f"staff:{i}"
        out.append(box(role_id, x, STAFF_Y - STAFF_H / 2, width, STAFF_H, role, TEAM_SIZE, EDGE, "#ffffff", dashed=True))
        out.append(polyline([(trunk, ROOT_H), (trunk, STAFF_Y), (x if right else x + width, STAFF_Y)],
                            ("root", [0.5, 1]), (role_id, [0 if right else 1, 0.5]), EDGE, dashed=True))
    for i, (name, _, color, teams) in enumerate(departments):
        stroke, left = shade(color, 7), i * (column + COLUMN_GAP)
        middle, dept_id = left + column / 2, f"dept:{name}"
        out.append(box(dept_id, left, DEPT_Y, column, dept_h, labels[name], DEPT_SIZE, stroke, shade(color, 1),
                       shade(color, 9)))
        out.append(polyline([(trunk, ROOT_H), (trunk, BUS_Y), (middle, BUS_Y), (middle, DEPT_Y)],
                            ("root", [0.5, 1]), (dept_id, [0.5, 0]), EDGE))
        spine, top = left + INDENT / 2, DEPT_Y + dept_h + TEAMS_TOP
        for j, team in enumerate(teams):
            h, team_id = team_height(team), f"team:{name}/{j}"
            out.append(box(team_id, left + INDENT, top, column - INDENT, h, team, TEAM_SIZE, stroke, "#ffffff"))
            out.append(polyline([(spine, DEPT_Y + dept_h), (spine, top + h / 2), (left + INDENT, top + h / 2)],
                                (dept_id, [INDENT / 2 / column, 1]), (team_id, [0, 0.5]), stroke))
            top += h + TEAM_GAP
    return out
