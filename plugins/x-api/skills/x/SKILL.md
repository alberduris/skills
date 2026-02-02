---
name: x
description: Interact with X (Twitter) API v2. Post tweets, read timeline, search, manage your account.
allowed-tools: Bash(node *), Bash(npm *), Bash(npx *), Bash(cd *), Bash(ls *)
---

# X API Skill

X (Twitter) API v2 via your own developer credentials (OAuth 1.0a, pay-per-use).

## Setup

Before first use, the plugin needs to be built. Check if `dist/cli.js` exists in the plugin directory (`<base_directory>/../..`). If not:

```bash
cd <base_directory>/../.. && npm install && npm run build
```

## Commands

| Command | Description | Docs |
|---------|-------------|------|
| `me` | Your account profile, metrics, verification status | [docs/me.md](docs/me.md) |

## Invocation

```
<base_directory>/x <command> [flags]
```

Read the command docs for available flags and examples.

## Credentials

Credentials are loaded from the first source that has them:

1. `.env.local` in the current working directory
2. `.env` in the current working directory
3. `.env.local` in the plugin directory
4. `.env` in the plugin directory
5. Environment variables

Required: `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`

Get these from [console.x.com](https://console.x.com) > Apps > Keys and tokens.
