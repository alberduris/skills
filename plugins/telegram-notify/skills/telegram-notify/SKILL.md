---
name: telegram-notify
description: Send notifications via Telegram. Use when the user asks to notify, alert, message, or ping — or when a long-running task completes and the user previously asked to be notified.
version: "0.1.0"
allowed-tools: Bash(bash *)
---

Telegram Bot API skill. All commands go through `bash <base_directory>/bin/telegram <command>`.

[!COMMANDS]

a) `bash <base_directory>/bin/telegram send <text>` — send a message to the configured chat.
b) `bash <base_directory>/bin/telegram me` — get bot info; useful for debugging credential issues.

[!CREDENTIALS] Requires `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` as environment variables (or in `.env` / `.env.local`). If missing, tell the user to check the README for setup instructions.

[!GUIDELINES]
- This is instant messaging, not a report. Write the way you'd write a quick Telegram message to a coworker: one or two short sentences, no more. No markdown, no formatting, no bullet points, no tables, no code blocks, no headers, no bold, no italic. Just plain text. If you're tempted to send more than 2-3 lines, you're sending too much. The user will read this on their phone and a wall of text is a terrible experience. Summarize aggressively. The point is to get the user back to the session, not to deliver a full report over Telegram.
- Never send credentials, secrets, or sensitive data through Telegram unless the user explicitly asks for it.
