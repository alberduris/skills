# Telegram Notify

Telegram notifications for AI agents. Packages the Telegram Bot API behind a simple `telegram` CLI along with a SKILL.md that gives the agent the context it needs to use it.

Only requires curl.

## Commands

| Command | Description |
|---------|-------------|
| `telegram send <text>` | Send a message to the configured chat |
| `telegram me` | Get bot info (useful for debugging credentials) |

## Setup

You'll need a Telegram bot token and your chat ID. Here's how to get them:

1. Talk to [@BotFather](https://t.me/BotFather) on Telegram and run `/newbot` to create a bot. It'll give you a token.
2. Send any message to your new bot (so there's a chat to read from).
3. Grab your `chat_id` by hitting the bot's `getUpdates` endpoint:

```bash
curl -s "https://api.telegram.org/bot<TOKEN>/getUpdates" | python3 -c "import sys,json; print(json.load(sys.stdin)['result'][0]['message']['chat']['id'])"
```

4. Set both values as environment variables, or put them in a `.env.local` / `.env` file:

```
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

Credential resolution follows the same pattern as x-twitter: it checks `.env.local` and `.env` in the current working directory first, then in the plugin directory, and finally falls back to environment variables.

## License

MIT
