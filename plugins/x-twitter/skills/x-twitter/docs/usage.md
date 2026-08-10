Retrieves the project's post-read consumption against its monthly cap. Maps to GET /2/usage/tweets. Requires `X_API_BEARER_TOKEN` (app-only auth). Invoke via `node <base_directory>/x.js usage [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — returns consumption for the current billing cycle. b) `--days <1-90>` — number of days of usage history to include. c) `--raw` — output the full API response envelope.

[!NOT-CREDITS] `projectUsage` and `projectCap` count **posts read**, NOT credits and NOT money. The counter rises only on reads; creating and deleting posts leaves it unchanged. This command therefore CANNOT answer "do I have credits left?" — the X API exposes no dollar balance on any endpoint. When credits run out, calls fail with `402 Payment Required – credits depleted` while this command keeps working normally. For balance, spend, and auto-recharge, use the Developer Console at https://console.x.com.

[!OUTPUT-SHAPE] Default produces the usage object with `capResetDay` (day of month the cap resets), `projectCap` (posts readable per cycle), `projectId`, and `projectUsage` (posts read so far this cycle). With `--raw`, wraps into the API envelope with `data`.
