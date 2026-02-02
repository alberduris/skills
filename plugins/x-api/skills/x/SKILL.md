---
name: x
description: Interact with X (Twitter) API v2. Post tweets, read timeline, search, manage your account.
allowed-tools: Bash(node *), Bash(npm *), Bash(npx *), Bash(ls *)
---

X (Twitter) API v2 skill using the authenticated user's own developer credentials (OAuth 1.0a, pay-per-use). All commands go through a single entry point: `node <base_directory>/x.js <command> [flags]`. Each command has its own doc file with the full reference for flags and behavior.

[!SETUP] Before first use, check whether `<base_directory>/dist/x.js` exists. If it does NOT exist, run `npm install --prefix <base_directory>/../..` and then `npm run build --prefix <base_directory>/../..` to compile the TypeScript source. NEVER cd into the plugin directory; use --prefix to target it without changing your working directory.

[!COMMANDS] a) `me` — authenticated user's own account data (profile, metrics, verification). Full reference at @docs/me.md. b) `search` — search posts by query (last 7 days by default, full archive with --all). Full reference at @docs/search.md. c) `get` — retrieve one or more posts by ID (single ID or comma-separated). Full reference at @docs/get.md. d) `post` — create a tweet, reply, or quote tweet. Full reference at @docs/post.md. e) `delete` — delete a post owned by the authenticated user. Full reference at @docs/delete.md.

[!CREDENTIALS] Four OAuth 1.0a variables are REQUIRED: `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`. They resolve from the first source that provides them: a) `.env.local` in cwd, b) `.env` in cwd, c) `.env.local` in the plugin directory, d) `.env` in the plugin directory, e) environment variables. Obtain them from the X Developer Console (Apps > Keys and tokens).
