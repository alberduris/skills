Retrieves the direct replies to a post, newest first, one page at a time. Searches `in_reply_to_tweet_id:<id>`. Invoke via `node <base_directory>/x.ts replies <tweet_id> [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — returns up to 10 replies from the last 7 days. b) `--all` — searches the full archive instead. c) `--max-results <10-100>` — replies per page (up to 500 with `--all`). d) `--next-token <token>` — the next page, from the previous output's `meta.next_token`.

[!OUTPUT-SHAPE] `data` is an array of posts. Each keeps the post it answers as `{ type: "replied_to", id }` in `referenced_tweets`.

[!COST] Every reply returned is a billed read, and a popular post has thousands. Page deliberately rather than walking every `next_token`.
