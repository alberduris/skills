"""An arrow end bound to a shape that stops short of it.

Moving a shape through update leaves its bound arrows where they were, and
create_diagram binds ellipses at points off the curve. The fix deletes the
arrow and adds it again between the bound points, snapped to the four cardinal
points on an ellipse or a diamond; the server routes an elbow arrow again from
its two ends. Rotated shapes are skipped.
"""
import math

# A sound end sits on the outline, or 5.5 px off it when the binding mode is orbit.
MAX_GAP = 10
CARDINAL = [(0.5, 0), (1, 0.5), (0.5, 1), (0, 0.5)]
STYLE = ("strokeColor", "strokeWidth", "strokeStyle", "roughness", "opacity",
         "startArrowhead", "endArrowhead", "elbowed", "groupIds", "frameId")


def outline(shape):
    x, y, w, h = shape["x"], shape["y"], shape["width"], shape["height"]
    if shape["type"] == "ellipse":
        return [(x + w / 2 * (1 + math.cos(i * math.pi / 36)), y + h / 2 * (1 + math.sin(i * math.pi / 36)))
                for i in range(72)]
    if shape["type"] == "diamond":
        return [(x + w / 2, y), (x + w, y + h / 2), (x + w / 2, y + h), (x, y + h / 2)]
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def gap(point, polygon):
    """Distance from a point outside the polygon to its outline; 0 inside."""
    px, py = point
    edges = list(zip(polygon, polygon[1:] + polygon[:1]))
    crossings = sum((ay > py) != (by > py) and px < ax + (py - ay) * (bx - ax) / (by - ay)
                    for (ax, ay), (bx, by) in edges)
    if crossings % 2:
        return 0
    def to_edge(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        t = max(0, min(1, ((px - a[0]) * dx + (py - a[1]) * dy) / (dx * dx + dy * dy)))
        return math.hypot(px - a[0] - t * dx, py - a[1] - t * dy)
    return min(to_edge(a, b) for a, b in edges)


def bound_point(shape, fixed_point):
    fx, fy = (min(max(value, 0), 1) for value in fixed_point)
    if shape["type"] in ("ellipse", "diamond"):
        fx, fy = min(CARDINAL, key=lambda c: math.hypot(c[0] - fx, c[1] - fy))
    return [fx, fy], (shape["x"] + fx * shape["width"], shape["y"] + fy * shape["height"])


def rebuilt(arrow, elements):
    """The add payload of the arrow drawn again between its bound points."""
    new = {"type": "arrow", **{key: arrow[key] for key in STYLE if arrow.get(key) is not None}}
    ends = []
    for field, index in (("startBinding", 0), ("endBinding", -1)):
        binding = arrow.get(field)
        shape = binding and elements.get(binding["elementId"])
        if shape:
            fixed_point, point = bound_point(shape, binding.get("fixedPoint") or [0.5, 0.5])
            new[field] = {"elementId": shape["id"], "fixedPoint": fixed_point, "mode": "inside"}
        else:
            point = (arrow["x"] + arrow["points"][index][0], arrow["y"] + arrow["points"][index][1])
        ends.append(point)
    (sx, sy), (ex, ey) = ends
    new.update(x=sx, y=sy, width=abs(ex - sx), height=abs(ey - sy), points=[[0, 0], [ex - sx, ey - sy]])
    for bound in arrow.get("boundElements") or []:
        text = elements.get(bound["id"])
        if text and text["type"] == "text":
            new["label"] = {"text": text.get("originalText") or text["text"], "fontSize": text["fontSize"],
                            "fontFamily": text["fontFamily"], "strokeColor": text["strokeColor"]}
    return new


def run(elements):
    for arrow in elements.values():
        if arrow["type"] != "arrow":
            continue
        short = []
        for field, index in (("startBinding", 0), ("endBinding", -1)):
            shape = elements.get((arrow.get(field) or {}).get("elementId"))
            if not shape or shape.get("angle"):
                continue
            end = (arrow["x"] + arrow["points"][index][0], arrow["y"] + arrow["points"][index][1])
            distance = gap(end, outline(shape))
            if distance > MAX_GAP:
                short.append(f"{field[:-7]} {distance:.0f} px from {shape['type']} {shape['id']}")
        if short:
            yield {"id": arrow["id"],
                   "problem": f"arrow ends short of its shapes: {'; '.join(short)}",
                   "fix": {"delete": [arrow["id"]], "add": [rebuilt(arrow, elements)]}}
