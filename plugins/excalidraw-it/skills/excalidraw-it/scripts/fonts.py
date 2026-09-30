#!/usr/bin/env python3
"""The characters each Excalidraw font has, and how wide they are.

fonts.json holds the advance of every character, in em, for each fontFamily id
Excalidraw ships a font file for. Helvetica (2) is a system font and is not in it.
Run this file to build fonts.json again from the fonts of the npm package; that
needs npm and fontTools with brotli.
"""
import functools
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

METRICS = Path(__file__).with_name("fonts.json")
PACKAGE = "@excalidraw/excalidraw"
# fontFamily id -> folder of the font files in the npm package.
FOLDERS = {1: "Virgil", 3: "Cascadia", 5: "Excalifont", 6: "Nunito", 7: "Lilita",
           8: "ComicShanns", 9: "Liberation"}


@functools.cache
def advances():
    return {int(family): table for family, table in json.loads(METRICS.read_text())["advances"].items()}


def known(font_family):
    return font_family in advances()


def covers(font_family, char):
    return char in advances()[font_family]


def width(text, font_family, font_size):
    """Width of the longest line, as the browser draws it."""
    table = advances()[font_family]
    return max(sum(table.get(char, 0) for char in line) for line in text.split("\n")) * font_size


def build():
    from fontTools.ttLib import TTFont

    with tempfile.TemporaryDirectory() as folder:
        tarball = subprocess.run(["npm", "pack", "--silent", PACKAGE], cwd=folder, check=True,
                                 capture_output=True, text=True).stdout.strip()
        with tarfile.open(Path(folder) / tarball) as archive:
            version = json.load(archive.extractfile("package/package.json"))["version"]
            archive.extractall(folder, filter="data")
        fonts = Path(folder) / "package" / "dist" / "prod" / "fonts"
        tables = {}
        for family, name in FOLDERS.items():
            table = tables[family] = {}
            # Each family is split into files by unicode range.
            for path in sorted((fonts / name).glob("*.woff2")):
                font = TTFont(path)
                em = font["head"].unitsPerEm
                for codepoint, glyph in font.getBestCmap().items():
                    table[chr(codepoint)] = round(font["hmtx"][glyph][0] / em, 4)
    return {"source": f"{PACKAGE}@{version}", "advances": tables}


if __name__ == "__main__":
    if len(sys.argv) != 1:
        sys.exit("usage: fonts.py  (builds fonts.json from the npm package)")
    metrics = build()
    METRICS.write_text(json.dumps(metrics, ensure_ascii=False, separators=(",", ":")))
    print(f"{METRICS}  {metrics['source']}  " + ", ".join(
        f"{FOLDERS[family]} {len(table)}" for family, table in metrics["advances"].items()))
