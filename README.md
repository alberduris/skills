# Claude Code Marketplace

<img src="assets/claude-icon.png" alt="Claude" height="18" align="left">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Plugins](https://img.shields.io/badge/plugins-1-blue.svg)](https://github.com/alberduris/claude-code-marketplace)
[![Claude Code](https://img.shields.io/badge/Claude-Code-orange.svg)](https://www.claude.com/product/claude-code)

Claude Code Plugins Marketplace by [@alberduris](https://x.com/alberduris).

This git repository is a Claude Code Marketplace; in other words, a way to **distribute** a **collection** of Plugins that augment Claude Code's capabilities via **Commands**, **Skills**, **Agents**, or **Hooks**.

## Quick Understanding

Zero-bullshit definitions without AI slop so we all know what we're talking about.

**Marketplace**: A git repository with a [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) file listing available Plugins.

**Plugin**: A packaged directory containing one or more of the following, plus [`.claude-plugin/plugin.json`](plugins/second-opinion/.claude-plugin/plugin.json) with metadata (name, version, author):
- **Skill**: A `SKILL.md` file with instructions Claude reads when contextually relevant. Can include supporting files (scripts, templates). Claude invokes based on description matching user's request.
- **Command**: Custom slash command (e.g., `/commit`) that expands to a prompt when invoked.
- **Agent**: Isolated autonomous agent launched via Task tool; runs multi-turn conversation with tools (agent ↔ tools), returns final result. ([Learn more](https://alberduris.beehiiv.com/p/claude-code-sub-agents-what-they-are-and-what-they-are-not))
- **Hook**: Script triggered by events (file edits, tool calls, user prompt submission).

## Quick Start

### Standard Installation

Add the Marketplace and install Plugins through Claude Code:

```bash
# Add this Marketplace
/plugin marketplace add alberduris/claude-code-marketplace

# Install the second-opinion Plugin
/plugin install second-opinion
```

### One-Command Installation

Use the Claude Plugins CLI to add the Marketplace and install Plugins in one step:

```bash
claude plugins install alberduris/claude-code-marketplace second-opinion
```

## Available Plugins

- [`second-opinion`](#second-opinion-skill---second-opinion) - Consult GPT-5 Pro for alternative perspectives

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
SECOND_OPINION_TIMEOUT=1800000             # 30min timeout in ms
```

## License

MIT
