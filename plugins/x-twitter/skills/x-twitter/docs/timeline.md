Retrieves the authenticated user's home timeline (reverse chronological, not the algorithmic "For you" feed). Maps to GET /2/users/:id/timelines/reverse_chronological. Invoke via `node <base_directory>/x.ts timeline [flags]`. Output is JSON to stdout.

[!NOTE] Results skew heavily toward the authenticated account's own posts and do not reproduce the "Following" tab of the web client. Use `--exclude replies,retweets` to improve signal.

[!FLAGS] a) no flags — returns recent timeline posts. b) `--max-results <1-100>` — set number of results per page. c) `--next-token <token>` — pagination token from a previous response. d) `--start-time <ISO8601>` — oldest timestamp (inclusive). e) `--end-time <ISO8601>` — newest timestamp (exclusive). f) `--exclude <types>` — comma-separated list of tweet types to exclude: `replies`, `retweets`, or `replies,retweets`.

[!OUTPUT-SHAPE] `data` is an array of posts.
