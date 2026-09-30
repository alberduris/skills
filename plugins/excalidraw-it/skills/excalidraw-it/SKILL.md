---
name: excalidraw-it
description: Draw diagrams with the operator on a live Excalidraw+ scene, through the Excalidraw+ MCP. Draws each diagram type from a few lines of YAML with a generator of its own, and carries the known sins agents commit on the canvas, each with the rule that prevents it and the lint check that catches it, plus a ledger of prefab pieces that come out right the first time.
version: "0.1.1"
disable-model-invocation: true
---

A diagram here is a scene in the operator's Excalidraw+ workspace. You write it through the MCP, and the operator's browser shows each write as soon as the server saves it. The operator edits the scene by hand only to correct something, and tells you when they do: read back only the elements they name, never the whole scene.

[!SETUP]:

1. Before the first JSON you write by hand, or the first `create_diagram`, call the format guide that matches the task, once per session: `read_diagram_format`, `read_freeform_format` or `read_presentation_format`. It costs about 10k tokens. Skip it while `draw.py`, `pieces.py` or `mermaid.py` write every element: their payloads already follow the format.
2. Use an existing scene id, or `create_scene` in the collection the operator names; with none named, in the one `list_collections` marks `isDefault: true` (`private` works only with a personal API key). Give the operator the link `https://app.excalidraw.com/s/<workspace>/<sceneId>`, with `metadata.workspace` and `metadata.id` of the `create_scene` response.

[!TYPES]:

`python3 <base_directory>/scripts/draw.py --help` lists the diagram types that have a generator: a script that draws the whole diagram, title and note included, from its data in YAML. For one of them, `draw.py <type> --help` shows the YAML it takes, and it is all you need to read: write the data and run `python3 <base_directory>/scripts/draw.py <type> data.yaml | python3 <base_directory>/scripts/write.py <sceneId>`.
To change a generated diagram, change its data and draw it again: first send `{"delete": [...]}` with the `addedElementIds` of its write answer, and their labels go with them. Edit elements by hand only for what the data cannot say.
For a type with no generator, read its entry in `ledger/types.yaml`: which route draws it (`create_diagram`, Mermaid through mermaid-to-excalidraw, or by hand with `edit_scene_content`) and why the others are vetoed. A type with no entry: draw it by hand from the entry of the closest type, and propose an entry for it to the operator.

[!EVERY-WRITE]:

1. Before you write JSON by hand, check the plan against the sins and use every piece from the ledger that fits; a generator already does both.
2. Write through `python3 <base_directory>/scripts/write.py <sceneId>`, with the payload on stdin: an `add` array, or an object with `delete`, `update` and `add`. It calls `edit_scene_content` over HTTP and prints one line; the full answer goes to `$TMPDIR/excalidraw-it/`.
3. After the write, run `python3 <base_directory>/scripts/lint.py <sceneId> --fix`. It applies the fix of every finding and lints the scene again.
4. Once the lint is clean, call `take_screenshot` before you show the result. Render per frame when the scene is larger than one screen, because a full-scene render is scaled down to 1920x1080 and small defects stop being visible.

[!READING]:

Each way of reading the scene costs a different amount of context. Measured on a scene of 107 elements:

- `search_scene_content` with a `query` returns only the matching elements, about 200 tokens each. It matches shape labels and standalone text, and never returns the text of a label bound to a shape (`containerId` set), so it cannot tell you where a label sits.
- `get_scene_content` returns every element: 73 KB, about 20k tokens. Never call it.
- `python3 <base_directory>/scripts/fetch.py <sceneId>` downloads the same content through the REST API into a local file, with the key in `EXCALIDRAW_API_KEY`. Query that file with Python and print only the fields you need. Use it for every question about geometry: label padding, arrow endpoints, overlaps.
- `take_screenshot` costs between a few hundred tokens and about 3k, depending on the render size. To check a layout, it is cheaper than reading the JSON.

`edit_scene_content` answers with the id and position of each element it added: about 4k tokens for 83 elements.

[!SINS]:

`ledger/sins.yaml` lists the mistakes agents make on the canvas again and again i.e., what happens, and the rule that prevents it. Read it before the first write by hand. Each sin has a lint check with the same id, except the ones marked `lint: none`.

[!PIECES]:

`ledger/pieces.yaml` lists prefab pieces i.e., what each one is, when to use it, and the variants it takes. Each piece id is also a command of `scripts/pieces.py`, which prints the `add` payload with every coordinate computed. Pipe it into `write.py`: `pieces.py <id> … | write.py <sceneId>`. Run `python3 <base_directory>/scripts/pieces.py <id> --help` for its parameters, and never draw a piece by hand.
