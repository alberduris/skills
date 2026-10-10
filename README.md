# Claude Code Marketplace

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Plugins](https://img.shields.io/badge/plugins-8-blue.svg)](https://github.com/alberduris/claude-code-marketplace)
[![Claude Code](https://img.shields.io/badge/Claude-Code-orange.svg)](https://www.claude.com/product/claude-code)
<img src="assets/claude-icon.png" alt="Claude" height="18" style="margin-left: 6px; vertical-align: middle;">

Claude Code Plugins Marketplace by [@alberduris](https://x.com/alberduris).

This git repository is a Claude Code Marketplace; in other words, a way to **distribute** a **collection** of Plugins that augment Claude Code's capabilities via **Commands**, **Skills**, **Agents**, or **Hooks**.

## Quick Understanding

Zero-bullshit definitions without AI slop so we all know what we're talking about.

**Marketplace**: A git repository with a [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) file listing available Plugins.

**Plugin**: A packaged directory containing one or more of the following, plus [`.claude-plugin/plugin.json`](plugins/second-opinion/.claude-plugin/plugin.json) with metadata (name, version, author):
- **Skill**: Directory with `SKILL.md` + supporting files (scripts, templates, docs).
- **Command**: Single `.md` file.
- **Agent**: Isolated autonomous agent launched via Task tool; runs multi-turn conversation with tools (agent ↔ tools), returns final result. ([Learn more](https://alberduris.beehiiv.com/p/claude-code-sub-agents-what-they-are-and-what-they-are-not))
- **Hook**: Script triggered by events (file edits, tool calls, user prompt submission).

> **Invocation**: Both Skills and Commands can be invoked 3 ways: manually (`/name`), by Claude via `Skill` tool, or auto-discovered by context. The only difference is structure. Use `disable-model-invocation: true` in frontmatter if you want manual-only.

## Quick Start

### Standard Installation

Add the Marketplace and install Plugins through Claude Code:

```bash
# Add this Marketplace
/plugin marketplace add alberduris/claude-code-marketplace

# Install a Plugin
/plugin install second-opinion
```

### One-Command Installation

Use the Claude Plugins CLI to add the Marketplace and install Plugins in one step:

```bash
claude plugins install alberduris/claude-code-marketplace second-opinion
```

## Available Plugins

| Plugin | Description |
|--------|-------------|
| [second-opinion](plugins/second-opinion/) | Consult GPT-5 Pro for alternative perspectives; supports context injection, web search, and configurable models |
| [langfuse-traces](plugins/langfuse-traces/) | Query Langfuse traces for debugging LLM calls, analyzing token usage, and investigating workflow executions |
| [slack-reminders](plugins/slack-reminders/) | Schedule future reminders via Slack notifications at a specific date/time |
| [x-twitter](plugins/x-twitter/) | 36-command skill for X/Twitter — post, search, engage, moderate, discover communities, all from your terminal |
| [beehiiv](plugins/beehiiv/) | Manage your Beehiiv newsletter — list and read posts, create drafts from Markdown/HTML files |
| [newspaper-explainer](plugins/newspaper-explainer/) | Generate self-contained HTML broadsheet newspapers to explain any subject worth reporting |
| [self-message](plugins/self-message/) | Give Claude Code agents the ability to send themselves continuation messages mid-session — metacognition, not repetition |
| [telegram-notify](plugins/telegram-notify/) | Send and schedule Telegram messages from Claude Code via Bot API — instant or delayed delivery via Cloudflare Worker |

See each plugin's README for setup and usage instructions.

## License

MIT
