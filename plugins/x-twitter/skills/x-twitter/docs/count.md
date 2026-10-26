Counts posts matching a query over time. By default counts from the last 7 days (GET /2/tweets/counts/recent). With `--all`, counts from the full archive (GET /2/tweets/counts/all). Requires `X_API_BEARER_TOKEN` (app-only auth) in both modes. Invoke via `node <base_directory>/x.ts count "<query>" [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — returns time-series counts for the last 7 days. b) `--all` — count from the full archive instead of just the last 7 days. c) `--start-time <ISO8601>` — oldest timestamp (inclusive). d) `--end-time <ISO8601>` — newest timestamp (exclusive). e) `--granularity <minute|hour|day>` — time bucket size (default: hour). f) `--next-token <token>` — pagination token.

[!OUTPUT-SHAPE] `data` is an array of count objects with `start`, `end`, and `tweet_count`; `meta.total_tweet_count` is the sum.
