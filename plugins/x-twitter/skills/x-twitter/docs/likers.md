Lists users who liked a specific post. Maps to GET /2/tweets/:id/liking_users. Invoke via `node <base_directory>/x.ts likers <tweet_id> [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — returns users who liked the post with default profile fields. b) `--max-results <1-100>` — set number of results per page. c) `--next-token <token>` — pagination token from a previous response.

[!OUTPUT-SHAPE] `data` is an array of user objects.
