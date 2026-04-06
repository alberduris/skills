---
name: telegram-notify
description: Send notifications via Telegram. Use when the user asks to notify, alert, message, or ping — or when a long-running task completes and the user previously asked to be notified. Can also schedule messages for later delivery.
version: "0.2.0"
allowed-tools: Bash(bash *)
---

Telegram Bot API skill. All commands go through `bash <base_directory>/telegram.sh <command>`.

[!COMMANDS]

a) `bash <base_directory>/telegram.sh send <text>` — send a message to the configured chat immediately.
b) `bash <base_directory>/telegram.sh schedule <datetime> <text>` — schedule a message for later delivery via Cloudflare Worker.
c) `bash <base_directory>/telegram.sh scheduled` — list all pending scheduled messages.
d) `bash <base_directory>/telegram.sh cancel <id>` — cancel a scheduled message by ID.
e) `bash <base_directory>/telegram.sh me` — get bot info; useful for debugging credential issues.

[!DATETIME FORMATS for schedule]

The `<datetime>` argument accepts multiple formats. Always quote it if it contains spaces.

- `+30m`, `+2h`, `+1d`, `+2h30m` — relative from now
- `15:00` — today at that time (local tz); if already passed, assumes tomorrow
- `"tomorrow 09:00"` or `"mañana 09:00"` — tomorrow at that time (local tz)
- `"today 15:00"` or `"hoy 15:00"` — today at that time (local tz)
- `"2026-04-07 09:00"` — date + time (local tz)
- `2026-04-07T09:00:00Z` — ISO 8601 (UTC)

[!CREDENTIALS]

- **send, me**: Require `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` as environment variables (or in `.env` / `.env.local`).
- **schedule, scheduled, cancel**: Additionally require `TELEGRAM_WORKER_URL` and `TELEGRAM_API_TOKEN` (the Cloudflare Worker endpoint and its auth token).

If missing, tell the user to check the README for setup instructions.

[!GUIDELINES]
- This is instant messaging, not a report. Write the way you'd write a quick Telegram message to a coworker: one or two short sentences, no more. No markdown, no formatting, no bullet points, no tables, no code blocks, no headers, no bold, no italic. Just plain text. If you're tempted to send more than 2-3 lines, you're sending too much. The user will read this on their phone and a wall of text is a terrible experience. Summarize aggressively. The point is to get the user back to the session, not to deliver a full report over Telegram.
- Never send credentials, secrets, or sensitive data through Telegram unless the user explicitly asks for it.
- Scheduled messages have ~5 min granularity (the worker checks the queue every 5 minutes). Don't promise exact-to-the-second delivery.
