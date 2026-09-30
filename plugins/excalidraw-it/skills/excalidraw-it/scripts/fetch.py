#!/usr/bin/env python3
"""Download the content of an Excalidraw+ scene into a local file, out of the context.

Prints the file path and the number of live elements. Reads the API key from
EXCALIDRAW_API_KEY.
"""
import json
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

from key import api_key

API = "https://api.excalidraw.com/api/v1/scenes/{}/content"
CACHE_DIR = Path(tempfile.gettempdir()) / "excalidraw-it"


def fetch(scene_id):
    request = urllib.request.Request(API.format(scene_id), headers={"Authorization": f"Bearer {api_key()}"})
    try:
        with urllib.request.urlopen(request) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        sys.exit(f"GET {API.format(scene_id)} -> {error.code} {error.read().decode()}")


def live_elements(scene):
    return {element["id"]: element for element in scene["elements"] if not element.get("isDeleted")}


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: fetch.py <sceneId>")
    scene = fetch(sys.argv[1])
    CACHE_DIR.mkdir(exist_ok=True)
    path = CACHE_DIR / f"{sys.argv[1]}.json"
    path.write_text(json.dumps(scene, ensure_ascii=False))
    print(f"{path}  {len(live_elements(scene))} live elements")


if __name__ == "__main__":
    main()
