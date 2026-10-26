Searches posts matching a query. By default searches the last 7 days (GET /2/tweets/search/recent). With `--all`, searches the full archive back to 2006 (GET /2/tweets/search/all), also under OAuth 1.0a user context. Invoke via `node <base_directory>/x.ts search "<query>" [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — returns up to 10 results. b) `--all` — search the full archive instead of just the last 7 days. c) `--max-results <10-100>` — set number of results per page (up to 500 with --all). d) `--sort <recency|relevancy>` — order results. e) `--start-time <ISO8601>` — oldest timestamp (inclusive). f) `--end-time <ISO8601>` — newest timestamp (exclusive). g) `--since-id <id>` — results newer than this post ID. h) `--until-id <id>` — results older than this post ID. i) `--next-token <token>` — the next page, from the previous output's `meta.next_token`.

[!IMPORTANT] Without `--all`, search only covers the **last 7 days**. Queries for older content will return zero results. Use `--all` for the full archive. To read a thread, use `thread`; for the replies to a post, `replies`; not `search` with `conversation_id:`.

[!RATE-LIMITS] `--all` is rate limited far more aggressively than recent search and returns `429 Too Many Requests` after only a few calls in quick succession. Space out full-archive queries and keep `--max-results` low. Each returned post is also a billed read, so `--max-results 100` costs ten times `--max-results 10` for the same query.

[!QUERY-SYNTAX] The query uses X search operators. Examples: `from:username`, `has:media`, `-is:retweet`, `#hashtag`, `"exact phrase"`, `lang:en`. Engagement thresholds: `min_likes:<n>`, `min_replies:<n>`, `min_reposts:<n>` — available on both recent and `--all`. Their web-search spellings `min_faves:` and `min_retweets:` are invalid here and error out. Combine with AND (space), OR, NOT (-). Max 4096 chars. Unknown operators are rejected by name, so an invalid query fails loudly rather than returning wrong results.

[!OUTPUT-SHAPE] `data` is an array of posts; `meta` carries `result_count`, `newest_id`, `oldest_id` and `next_token`.
