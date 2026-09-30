"""A gantt chart: tasks in sections as bars on a time axis of weeks, milestones as diamonds, and today.

    today: 2026-09-29        # a red dashed line; a task that ends by then is done
    sections:                # name: {color, tasks}; a task is name: [first day, last day]
      Tipos:
        color: violet
        tasks:
          Flowchart a organigrama: [2026-09-21, 2026-09-29]
          Gráficas: [2026-10-12, 2026-10-16]
    milestones:              # name: day
      Skill 1.0: 2026-11-20
    start: 2026-09-14        # the first day of the axis; the Monday before the earliest day by default
    weeks: 10                # by default, up to the week of the latest day
    words: {today: hoy, milestones: Hitos}

words also takes months, the twelve names the axis writes. The section colors
default to violet, blue, teal, orange, grape and green in turn. A task is filled
with its color when done and with a light tint of it when pending; without today
every task is pending.
"""
import math
from datetime import date, timedelta

import fonts
from canvas import FONT, INK, LINE, MUTED, TITLE_FONT, text
from palette import OPEN_COLOR, shade
from schema import DataError, choice, entries, fields, number

NAME_SIZE, SECTION_SIZE, AXIS_SIZE = 16, 18, 14
DAY, SECTION_H, ROW_H, BAR_H, TOP, DIAMOND = 12, 40, 36, 22, 36, 20
GRID, TODAY_RED = "#dee2e6", shade("red", 7)
COLORS = ["violet", "blue", "teal", "orange", "grape", "green"]
WORDS = {"today": "hoy", "milestones": "Hitos",
         "months": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]}


def day(value, where):
    if isinstance(value, date):  # YAML reads an unquoted 2026-09-14 as a date
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        raise DataError(f"{where}: expected a day as YYYY-MM-DD, got {value!r}") from None


def parsed(data):
    fields(data, "top level", ("sections",), ("milestones", "today", "start", "weeks", "words"))
    sections = []
    for i, (name, section) in enumerate(entries(data["sections"], "sections").items()):
        where = f"sections.{name}"
        fields(section, where, ("tasks",), ("color",))
        color = choice(section.get("color", COLORS[i % len(COLORS)]), f"{where}.color", OPEN_COLOR)
        tasks = []
        for task, span in entries(section["tasks"], f"{where}.tasks").items():
            at = f"{where}.tasks.{task}"
            if not isinstance(span, list) or len(span) != 2:
                raise DataError(f"{at}: expected [first day, last day], got {span!r}")
            first, last = day(span[0], at), day(span[1], at)
            if last < first:
                raise DataError(f"{at}: it ends before it starts")
            tasks.append((str(task), first, last))
        sections.append((str(name), color, tasks))
    milestones = [(str(n), day(d, f"milestones.{n}"))
                  for n, d in entries(data.get("milestones"), "milestones", optional=True).items()]
    today = day(data["today"], "today") if "today" in data else None
    words = {**WORDS, **fields(data.get("words") or {}, "words", (), tuple(WORDS))}
    if len(words["months"]) != 12:
        raise DataError(f"words.months: expected twelve names, got {words['months']!r}")
    days = [d for _, _, tasks in sections for _, a, b in tasks for d in (a, b)] + [d for _, d in milestones]
    days += [today] if today else []
    start = day(data["start"], "start") if "start" in data else min(days) - timedelta(days=min(days).weekday())
    need = math.ceil(((max(days) - start).days + 1) / 7)
    weeks = number(data.get("weeks", need), "weeks", low=1, whole=True)
    return sections, milestones, today, start, weeks, words


def vertical(x, top, bottom, color, dashed=False, width=1):
    return {"type": "line", "x": x, "y": top, "points": [[0, 0], [0, bottom - top]], "strokeColor": color,
            "strokeWidth": width, "roughness": 0, "strokeStyle": "dashed" if dashed else "solid"}


def build(data):
    sections, milestones, today, start, weeks, words = parsed(data)
    names = [n for _, _, tasks in sections for n, _, _ in tasks] + [n for n, _ in milestones]
    chart = max(fonts.width(n, FONT, NAME_SIZE) for n in names) * 1.2 + 32  # the left edge of the time axis

    def x_of(d):
        return chart + (d - start).days * DAY

    def shown(d):
        return f"{d.day} {words['months'][d.month - 1]}"

    out, y = [], TOP
    rows = sections + ([(words["milestones"], "gray", [(n, d, None) for n, d in milestones])] if milestones else [])
    for section, color, tasks in rows:
        stroke = shade(color, 7)
        out.append(text(0, y + 10, section, SECTION_SIZE, stroke, TITLE_FONT))
        y += SECTION_H
        for name, first, last in tasks:
            out.append(text(0, y + (ROW_H - NAME_SIZE * LINE) / 2, name, NAME_SIZE, INK))
            middle = y + ROW_H / 2
            if last is None:  # a milestone: a diamond on its day, its date beside it
                out.append({"type": "diamond", "x": x_of(first) + DAY / 2 - DIAMOND / 2, "y": middle - DIAMOND / 2,
                            "width": DIAMOND, "height": DIAMOND, "strokeColor": stroke, "backgroundColor": stroke,
                            "fillStyle": "solid", "roughness": 0})
                out.append(text(x_of(first) + DAY / 2 + 16, middle - AXIS_SIZE * LINE / 2, shown(first), AXIS_SIZE,
                                stroke))
            else:
                done = today is not None and last <= today
                out.append({"type": "rectangle", "x": x_of(first), "y": middle - BAR_H / 2,
                            "width": x_of(last + timedelta(days=1)) - x_of(first), "height": BAR_H,
                            "strokeColor": stroke, "backgroundColor": stroke if done else shade(color, 1),
                            "fillStyle": "solid", "roundness": {"type": 3}, "strokeWidth": 2, "roughness": 0})
            y += ROW_H
    bottom = y + 8
    grid = []
    for week in range(weeks + 1):
        d = start + timedelta(weeks=week)
        grid.append(vertical(x_of(d), TOP - 8, bottom, GRID))
        if week < weeks:
            out.append(text(x_of(d) + 6, 0, shown(d), AXIS_SIZE, MUTED))
    if today:
        x = x_of(today) + DAY / 2
        out.append(vertical(x, TOP - 8, bottom, TODAY_RED, dashed=True, width=2))
        out.append(text(x + 6, bottom - AXIS_SIZE * LINE, words["today"], AXIS_SIZE, TODAY_RED))
    return grid + out
