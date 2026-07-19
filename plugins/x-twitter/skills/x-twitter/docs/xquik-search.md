# Xquik Search

Search public X posts through the Xquik API without loading account credentials.

```bash
node <base_directory>/x.js xquik-search "AI agents"
```

## Setup

Set an Xquik API key in `.env.local`, `.env`, or the process environment:

```bash
XQUIK_API_KEY=your-api-key
```

`XQUIK_BASE_URL` is optional and defaults to `https://xquik.com`.

Requests time out after 15 seconds. Failures report only the HTTP status and do
not print API response details.

## Options

| Option | Description |
|--------|-------------|
| `--max-results <1-200>` | Maximum posts to return (default: 20) |
| `--sort latest\|top` | Chronological or engagement-ranked results |
| `--start-time <ISO 8601>` | Return posts after this timestamp |
| `--end-time <ISO 8601>` | Return posts before this timestamp |
| `--next-token <cursor>` | Continue from a previous raw response |
| `--raw` | Return pagination metadata with the posts |

This command is read-only. It does not use the OAuth credentials required by
write commands.

Xquik is an independent third-party service. Not affiliated with X Corp.
"Twitter" and "X" are trademarks of X Corp.
