"""An arrow hidden under its own label.

Excalidraw centres a bound label on its arrow, over a background that hides the
line: on the midpoint of the middle segment when the arrow has an even number
of points, on the middle point when it has an odd number. The stored position of
the label cannot be trusted, because the server routes an elbow arrow again
after it places the label.

On a sharp or elbow arrow, the segment under the label has to reach 20 px past
it on each side, or the arrow reads as two stubs: a short labelled arrow between
rows, or a self-loop whose turn the label covers. A curved arrow has no visible
segments, so 40 px of its line outside the label is enough. There is no fix:
space the shapes further apart, or draw a self-loop with a longer middle segment.
"""
import math

MARGIN = 40


def centre(points):
    if len(points) % 2:
        return points[len(points) // 2]
    a, b = points[len(points) // 2 - 1], points[len(points) // 2]
    return (a[0] + b[0]) / 2, (a[1] + b[1]) / 2


def across(label, a, b):
    """How much of the segment a-b the label covers."""
    length = math.dist(a, b) or 1
    return label["width"] * abs(b[0] - a[0]) / length + label["height"] * abs(b[1] - a[1]) / length


def segment_short(points, label):
    """Pixels the segments under the label fall short of reaching MARGIN / 2 past it on each side."""
    middle = len(points) // 2
    if len(points) % 2 == 0:
        a, b = points[middle - 1], points[middle]
        return across(label, a, b) + MARGIN - math.dist(a, b)
    # The label sits on a corner: each segment from it has to leave the label on its own.
    vertex = points[middle]
    return max(across(label, vertex, other) / 2 + MARGIN / 2 - math.dist(vertex, other)
               for other in (points[middle - 1], points[middle + 1]))


def outside(points, box):
    """Length of the line outside the box, sampled every pixel."""
    x0, y0, x1, y1 = box
    length = 0
    for a, b in zip(points, points[1:]):
        steps = max(1, int(math.dist(a, b)))
        for i in range(steps):
            t = (i + 0.5) / steps
            x, y = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
            length += 0 if x0 <= x <= x1 and y0 <= y <= y1 else math.dist(a, b) / steps
    return length


def run(elements):
    for text in elements.values():
        arrow = elements.get(text.get("containerId"))
        if text["type"] != "text" or not arrow or arrow["type"] != "arrow":
            continue
        points = [(arrow["x"] + x, arrow["y"] + y) for x, y in arrow["points"]]
        curved = not arrow.get("elbowed") and arrow.get("roundness") and len(points) > 2
        if curved:
            cx, cy = centre(points)
            w, h = text["width"] / 2, text["height"] / 2
            shown = outside(points, (cx - w, cy - h, cx + w, cy + h))
            problem = shown < MARGIN and f"only {shown:.0f} px of the curve show outside it"
        else:
            short = segment_short(points, text)
            problem = short > 0 and f"the segment under it is {short:.0f} px too short"
        if problem:
            yield {"id": arrow["id"], "problem": f'label "{text["text"][:30]}" hides its arrow: {problem}'}
