# Excalidraw It

Draw diagrams with your agent on a live Excalidraw+ scene. You watch each write land in your browser, fix what you want by hand, and tell the agent what you changed.

The agent does not place shapes one by one. For each diagram type there is a generator that draws the whole diagram, title and note included, from a few lines of YAML. After every write, a lint checks the scene for the mistakes agents make on the canvas again and again (text clipped at the end of its box, a word broken across two lines, an arrow end floating off its shape, a label hiding its arrow…) and fixes what it finds.

## Diagram types

32 generators, one per type:

| Family | Types |
|--------|-------|
| Charts | bar-chart, pie, radar, sankey, treemap, venn |
| Time | gantt, timeline, kanban, user-journey, git |
| Trees | mindmap, org-chart, tree-view, ishikawa |
| Flows | flowchart, swimlanes, agentflow, sequence, use-case, railroad |
| Architecture | architecture, c4, block, wardley |
| Data | class, er, requirement, packet |
| Frameworks | quadrant, cynefin, event-modeling |

State diagrams go through Mermaid. For a type with no generator, `ledger/types.yaml` says which route draws it: the MCP's `create_diagram`, Mermaid, or by hand.

## Requirements

- An [Excalidraw+](https://plus.excalidraw.com) workspace and an API key for it.
- Python 3 with PyYAML: `pip install pyyaml`.
- Only for the Mermaid route: Node.js and Google Chrome. The first run installs `playwright-core` next to the script.

## Setup

1. Export your API key, e.g. in `~/.zshrc`:

   ```bash
   export EXCALIDRAW_API_KEY=...
   ```

2. Add the Excalidraw+ MCP to Claude Code. The single quotes keep the key out of the config file: Claude Code reads it from the environment.

   ```bash
   claude mcp add --transport http --scope user excalidraw-plus https://api.excalidraw.com/api/v1/mcp \
     --header 'Authorization: Bearer ${EXCALIDRAW_API_KEY}'
   ```

## Install

```bash
npx skills add alberduris/skills --skill excalidraw-it
```

## Usage

The skill runs only when you call it:

```
/excalidraw-it draw the architecture of this repo
/excalidraw-it a gantt of the Q4 roadmap in docs/roadmap.md
```

The agent creates a scene (or uses the one you give it), sends you the link, and draws. To change a diagram, ask: it edits the YAML and draws it again.

## How it works

Inside [`skills/excalidraw-it/`](skills/excalidraw-it/):

| Part | What it holds |
|------|---------------|
| `generators/` | One generator per type, and an example of each in `generators/examples/` |
| `scripts/` | `draw.py` (YAML → elements), `write.py` (elements → scene), `lint.py`, `fetch.py`, `pieces.py`, `mermaid.py` |
| `ledger/sins.yaml` | The mistakes agents make on the canvas, each with the rule that prevents it |
| `checks/` | The lint check of each sin |
| `ledger/pieces.yaml` + `pieces/` | Prefab pieces for what is drawn by hand: a box with a title, a card, a lane with a header |
| `ledger/types.yaml` | For each type, the route that draws it and why the others are vetoed |

The scripts call the Excalidraw+ MCP over HTTP themselves, so the payloads and the answers stay out of the agent's context.
