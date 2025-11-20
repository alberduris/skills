# Claude Code Marketplace

Claude Code plugins marketplace by [@alberduris](https://github.com/alberduris).

This marketplace serves as a repository for plugins that extend Claude Code's capabilities with specialized skills.

## Quick Understanding

Zero-bullshit definitions without AI slop so we all know what we're talking about.

**Marketplace**: A git repository with a `.claude-plugin/marketplace.json` file listing available plugins.

**Plugin**: A packaged directory containing one or more of the following, plus `.claude-plugin/plugin.json` with metadata (name, version, author):
- **Skill**: A `SKILL.md` file with instructions Claude reads when contextually relevant. Can include supporting files (scripts, templates). Claude invokes based on description matching user's request.
- **Command**: Custom slash command (e.g., `/commit`) that expands to a prompt when invoked.
- **Agent**: Isolated autonomous agent launched via Task tool; runs multi-turn conversation with tools (agent ↔ tools), returns final result. ([Learn more](https://alberduris.beehiiv.com/p/claude-code-sub-agents-what-they-are-and-what-they-are-not))
- **Hook**: Script triggered by events (file edits, tool calls, user prompt submission).

## Quick Start

### Standard Installation

Add the marketplace and install plugins through Claude Code:

```bash
# Add this marketplace
/plugin marketplace add alberduris/claude-code-marketplace

# Install the second-opinion plugin
/plugin install second-opinion
```

### One-Command Installation

Use the Claude Plugins CLI to add the marketplace and install plugins in one step:

```bash
claude plugins install alberduris/claude-code-marketplace second-opinion
```

## Available Plugins

### Second Opinion (Skill) - `second-opinion`

Consult GPT-5 Pro for alternative perspectives when you need second opinion, peer review, or fresh take on technical decisions.

**Usage:** Automatically triggered when requesting "second opinion", "peer review", or "alternative perspective".

| Features |
|----------|
| Context injection from multiple files |
| Web search capability (OpenAI responses API) |
| Configurable model selection (gpt-5-pro default, gpt-5-nano tested) |
| Reasoning summary extraction |
| 30-minute timeout for complex queries |
| Calling agent retains final judgment authority |

| Requirements |
|--------------|
| `OPENAI_API_KEY` environment variable |
| Node.js/pnpm for TypeScript execution |

#### Configuration

After installation, configure your environment with the required API key:

```bash
# Add to your .env.local
OPENAI_API_KEY=your-api-key-here
```

Optional configuration:
```bash
SECOND_OPINION_MODEL=gpt-5-pro-2025-10-06  # default model
SECOND_OPINION_TIMEOUT=1800000              # 30min timeout in ms
```

## License

MIT
