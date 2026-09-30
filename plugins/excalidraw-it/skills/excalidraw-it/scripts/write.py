#!/usr/bin/env python3
"""Send an edit to a scene through the MCP, reading the payload from stdin.

The payload is an `add` array, as pieces.py prints it, or an object with any of
delete, update and add, as lint.py prints a fix. Prints one summary line; the
full answer, with the id and position of each added element, goes to a file.
The add stores a standalone Cascadia text narrower than it renders, so the
texts it just added get the width fix of lint's clipped-text-end right after.

    pieces.py box-with-title --title Cloud --width 400 --height 200 | write.py <sceneId>
"""
import json
import sys
import time

from fetch import CACHE_DIR, fetch, live_elements
from mcp import call
from modules import SKILL_DIR, load

CASCADIA = 3


def edit(scene_id, change):
    """Apply one change ({delete, update, add}) and return the MCP answer."""
    arguments = {"sceneId": scene_id}
    if change.get("delete"):
        arguments["delete"] = change["delete"]
    for field in ("update", "add"):
        if change.get(field):
            arguments[field] = json.dumps(change[field], ensure_ascii=False)
    return call("edit_scene_content", arguments)


def cascadia_widths(scene_id, change, answer):
    """The width update clipped-text-end sends for the standalone Cascadia texts just added, or None."""
    if not any(e.get("type") == "text" and e.get("fontFamily") == CASCADIA and not e.get("containerId")
               for e in change.get("add") or []):
        return None
    elements = live_elements(fetch(scene_id))
    added = {i: elements[i] for i in answer.get("addedElementIds", []) if i in elements}
    check = load(SKILL_DIR / "checks" / "clipped_text_end.py")
    updates = [update for finding in check.run(added) for update in finding["fix"]["update"]]
    return {"update": updates} if updates else None


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: write.py <sceneId> < payload.json")
    payload = json.load(sys.stdin)
    change = {"add": payload} if isinstance(payload, list) else payload
    answer = edit(sys.argv[1], change)
    widths = cascadia_widths(sys.argv[1], change, answer)
    if widths:
        edit(sys.argv[1], widths)
    CACHE_DIR.mkdir(exist_ok=True)
    path = CACHE_DIR / f"{sys.argv[1]}-write-{time.strftime('%H%M%S')}.json"
    path.write_text(json.dumps(answer, ensure_ascii=False))
    widened = f", widened {len(widths['update'])} Cascadia texts" if widths else ""
    print(f"added {answer['added']}, updated {answer['updated']}, deleted {answer['deleted']}{widened}; answer in {path}")


if __name__ == "__main__":
    main()
