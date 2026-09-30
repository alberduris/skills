"""A character the font of its text lacks, drawn in a fallback font.

The browser draws each character a font lacks with the next font of its
fallback chain, which clashes with the rest of the text: → in Excalifont comes
out as a heavy geometric arrow. The fix writes the ASCII arrow instead; any
other missing character has no fix and is reworded by hand. An update keeps the
stored width, so the fix also sets the width of the new text, measured from the
font, and moves x to keep the text aligned as before.
"""
import fonts

ASCII = {"→": "->", "←": "<-", "↔": "<->", "⇒": "=>", "⇐": "<=", "⇔": "<=>"}


def ascii_text(text):
    return "".join(ASCII.get(char, char) for char in text)


def fixed(text):
    new_text = ascii_text(text["text"])
    width = fonts.width(new_text, text["fontFamily"], text["fontSize"])
    shift = {"center": (text["width"] - width) / 2, "right": text["width"] - width}.get(text["textAlign"], 0)
    return {"id": text["id"], "text": new_text, "originalText": ascii_text(text.get("originalText") or text["text"]),
            "width": width, "x": text["x"] + shift}


def run(elements):
    for text in elements.values():
        if text["type"] != "text" or not fonts.known(text["fontFamily"]):
            continue
        missing = "".join(sorted({char for char in text["text"]
                                  if not char.isspace() and not fonts.covers(text["fontFamily"], char)}))
        if not missing:
            continue
        finding = {
            "id": text["id"],
            "problem": f'"{text["text"][:40]}" has {missing}, which fontFamily {text["fontFamily"]} lacks',
        }
        if all(char in ASCII for char in missing):
            finding["fix"] = {"update": [fixed(text)]}
        yield finding
