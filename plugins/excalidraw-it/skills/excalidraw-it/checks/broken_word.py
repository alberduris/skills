"""A word the server broke across two lines of a label.

The server wraps a label bound to a shape by its own measure of the text, which
differs from the width of the real font by -11% to +19%. A shape sized to the
real width of its label can come back with a word split in two, "wardl" over
"ey", and the browser draws the line breaks the server stored. There is no fix:
widen the shape, then send its label again so the server wraps it anew.
"""


def word_at(text, index):
    start = max(text.rfind(" ", 0, index), text.rfind("\n", 0, index)) + 1
    ends = [end for end in (text.find(" ", index), text.find("\n", index)) if end >= 0]
    return text[start:min(ends, default=len(text))]


def broken_words(text, original):
    """Words of `original` that `text` splits with a line break the original lacks."""
    broken, j = [], 0
    for char in text:
        if j < len(original) and char == original[j]:
            j += 1
        elif char == "\n":
            if j < len(original) and original[j].isspace():
                j += 1  # the break took the place of a space
            elif 0 < j < len(original) and not original[j - 1].isspace() and original[j - 1] != "-":
                broken.append(word_at(original, j))
    return broken


def run(elements):
    for text in elements.values():
        if text["type"] != "text" or not text.get("containerId"):
            continue
        words = broken_words(text["text"], text.get("originalText") or text["text"])
        if words:
            yield {"id": text["containerId"],
                   "problem": f'label "{text["originalText"][:30]}" has {", ".join(words)} split across two lines'}
