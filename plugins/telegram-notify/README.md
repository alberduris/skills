# Telegram Notify

Telegram notifications for AI agents. Send messages instantly or schedule them for later delivery.

Only requires curl (+ a Cloudflare Worker for scheduled messages).

## Commands

| Command | Description |
|---------|-------------|
| `telegram send <text>` | Send a message now |
| `telegram schedule <datetime> <text>` | Schedule a message for later |
| `telegram scheduled` | List pending scheduled messages |
| `telegram cancel <id>` | Cancel a scheduled message |
| `telegram me` | Get bot info (useful for debugging credentials) |

### Datetime formats

The `schedule` command accepts flexible datetime inputs:

| Format | Example | Description |
|--------|---------|-------------|
| `+Nm`, `+Nh`, `+Nd` | `+30m`, `+2h`, `+1d2h30m` | Relative from now |
| `HH:MM` | `15:00` | Today at time (tomorrow if already passed) |
| `today HH:MM` | `today 15:00` | Today at time (local tz) |
| `tomorrow HH:MM` | `tomorrow 09:00` | Tomorrow at time (local tz) |
| `YYYY-MM-DD HH:MM` | `2026-04-07 09:00` | Date + time (local tz) |
| `ISO 8601` | `2026-04-07T09:00:00Z` | UTC |

Also accepts `hoy` and `mañana`.

## Setup

### 1. Telegram Bot (required for all commands)

1. Talk to [@BotFather](https://t.me/BotFather) on Telegram and run `/newbot` to create a bot. It'll give you a token.
2. Send any message to your new bot (so there's a chat to read from).
3. Grab your `chat_id`:

```bash
curl -s "https://api.telegram.org/bot<TOKEN>/getUpdates" | python3 -c "import sys,json; print(json.load(sys.stdin)['result'][0]['message']['chat']['id'])"
```

4. Set both values in `.env.local`, `.env`, or as environment variables:

```
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

Credential resolution checks `.env.local` and `.env` in the current working directory first, then in the plugin directory, and finally falls back to environment variables.

### 2. Cloudflare Worker (optional — only for scheduled messages)

> **This step is optional.** `send`, `me`, and all instant messaging works without it. You only need this if you want to schedule messages for later delivery (`schedule`, `scheduled`, `cancel`).

Scheduled messages use a Cloudflare Worker with KV storage as a message queue. The worker checks for due messages every 5 minutes. Entirely within Cloudflare's free tier — no credit card required.

#### Deploy the worker

1. Install the Wrangler CLI and log in:

```bash
npm install -g wrangler
wrangler login
```

2. Create the KV namespace:

```bash
cd plugins/telegram-notify/worker
wrangler kv namespace create "telegram-scheduler-queue"
```

3. Copy the `id` from the output into `worker/wrangler.toml`, replacing the existing KV namespace id. If you have multiple Cloudflare accounts, also set `account_id` in the toml.

4. Set the worker secrets:

```bash
wrangler secret put TELEGRAM_BOT_TOKEN
wrangler secret put TELEGRAM_CHAT_ID
wrangler secret put API_TOKEN          # generate one: openssl rand -hex 32
```

5. Deploy:

```bash
wrangler deploy
```

6. Add the worker URL and API token to your `.env.local` / `.env`:

```
TELEGRAM_WORKER_URL=https://telegram-scheduler.yourname.workers.dev
TELEGRAM_API_TOKEN=the-api-token-you-generated
```

## License

MIT
