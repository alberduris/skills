Retrieves the authenticated user's home timeline (reverse chronological, not the algorithmic "For you" feed). Maps to GET /2/users/:id/timelines/reverse_chronological. Invoke via `node <base_directory>/x.js timeline [flags]`. Output is JSON to stdout.

[!NOTE] (2026-02-14) The X API returns heavily skewed results — mostly own tweets — and does not faithfully reproduce the "Following" tab on x.com. Use `--exclude replies,retweets` to improve signal.

[!FLAGS] a) no flags — returns recent timeline posts with default tweet fields and expanded authors. b) `--max-results <1-100>` — set number of results per page. c) `--next-token <token>` — pagination token from a previous response. d) `--start-time <ISO8601>` — oldest timestamp (inclusive). e) `--end-time <ISO8601>` — newest timestamp (exclusive). f) `--exclude <types>` — comma-separated list of tweet types to exclude: `replies`, `retweets`, or `replies,retweets`. g) `--raw` — output the full API response envelope.

[!OUTPUT-SHAPE] Default produces an array of tweet objects. Each tweet includes `referenced_tweets` (array indicating if the tweet is a reply, retweet, or quote) and `in_reply_to_user_id` when applicable. With `--raw`, wraps into the API envelope with `data`, `includes`, and `meta` (next_token for pagination).
