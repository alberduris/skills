"""A title bound as a top-aligned label to a rounded box.

Excalidraw keeps a bound label 5 px from the border, on top of the rounded
corner. The fix swaps the label for the standalone title of the box-with-title
piece, in a group with the box.
"""
from modules import SKILL_DIR, load

box_with_title = load(SKILL_DIR / "pieces" / "box_with_title.py")


def run(elements):
    for text in elements.values():
        box = elements.get(text.get("containerId"))
        if text["type"] != "text" or not box or box["type"] != "rectangle":
            continue
        if not box.get("roundness") or text.get("verticalAlign") != "top":
            continue
        title = text.get("originalText") or text["text"]
        # The new group goes first: Excalidraw orders groupIds from the innermost group out.
        group_ids = [box_with_title.group_id(title)] + box.get("groupIds", [])
        yield {
            "id": text["id"],
            "problem": f'"{title}" is bound to the top of rounded box {box["id"]}, 5 px from its border',
            "fix": {
                "delete": [text["id"]],
                "update": [{"id": box["id"], "groupIds": group_ids}],
                "add": [box_with_title.title_element(title, box["x"], box["y"], text["strokeColor"], group_ids)],
            },
        }
